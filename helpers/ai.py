import asyncio
import re
import time

import requests

from config import (
    AI_MAX_TOKENS,
    AI_TEMPERATURE,
    NARA_API_KEY,
    NARA_BASE_URL,
    OPENROUTER_BASE_URL,
    OPENROUTER_KEY,
)
from helpers.catalog import (
    mark_fail,
    mark_ok,
    nara_image_models,
    next_nara_chat,
    or_chat_models,
    or_image_models,
    refresh,
)
from helpers.database import chat_logs
from helpers.memory import get_memory

_CACHE = {}
_CACHE_TTL = 45
CHAT_TIMEOUT = 8
MAX_TRIES = 2


def _providers():
    items = []
    if NARA_API_KEY:
        items.append({
            "name": "nara",
            "url": f"{NARA_BASE_URL}/chat/completions",
            "images_url": f"{NARA_BASE_URL}/images/generations",
            "key": NARA_API_KEY,
            "chat_models": next_nara_chat,
            "image_models": nara_image_models,
            "headers_extra": {},
        })
    if OPENROUTER_KEY:
        items.append({
            "name": "openrouter",
            "url": f"{OPENROUTER_BASE_URL}/chat/completions",
            "images_url": f"{OPENROUTER_BASE_URL}/images/generations",
            "key": OPENROUTER_KEY,
            "chat_models": or_chat_models,
            "image_models": or_image_models,
            "headers_extra": {
                "HTTP-Referer": "https://t.me/SANATANI_BACHA",
                "X-Title": "Harry ChatBot",
            },
        })
    return items


def _headers(provider):
    return {
        "Authorization": f"Bearer {provider['key']}",
        "Content-Type": "application/json",
        **provider["headers_extra"],
    }


def _extract_text(data):
    try:
        msg = data["choices"][0]["message"]
        text = (msg.get("content") or "").strip()
        if not text:
            text = str(msg.get("reasoning") or msg.get("reasoning_content") or "").strip()
        return text
    except Exception:
        return ""


def _post_chat(provider, model, messages):
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": min(AI_MAX_TOKENS, 140),
        "temperature": AI_TEMPERATURE,
    }
    r = requests.post(
        provider["url"],
        headers=_headers(provider),
        json=payload,
        timeout=CHAT_TIMEOUT,
    )
    data = r.json() if r.content else {}
    if r.status_code >= 400 or "choices" not in data:
        raise RuntimeError(f"{provider['name']}/{model}: {data.get('error', data)}")
    text = _extract_text(data)
    if not text:
        raise RuntimeError("empty reply")
    return text


def safe_ai(messages: list) -> str:
    key = str(messages[-2:] if messages else [])
    hit = _CACHE.get(key)
    if hit and time.time() - hit[0] < _CACHE_TTL:
        return hit[1]

    last_err = None
    tried = 0
    for provider in _providers():
        for model in provider["chat_models"]()[:MAX_TRIES]:
            tried += 1
            try:
                text = _post_chat(provider, model, messages)
                mark_ok(model, provider["name"])
                _CACHE[key] = (time.time(), text)
                print(f"AI OK: {provider['name']} / {model}")
                return text
            except Exception as e:
                last_err = e
                mark_fail(model)
                print("AI FAIL:", e)
                if tried >= MAX_TRIES:
                    break
        if tried >= MAX_TRIES:
            break
    print("AI ALL FAILED after", tried, "tries:", last_err)
    return ""


async def safe_ai_async(messages: list) -> str:
    return await asyncio.to_thread(safe_ai, messages)


def get_fallback_reply(user_id: int, text: str, name: str) -> str:
    lower = text.lower()
    if any(w in lower for w in ["hi", "hello", "hey", "namaste"]):
        return f"Hey {name}! Kaise ho?"
    if any(w in lower for w in ["kaise ho", "how are you", "kya haal"]):
        return f"Main theek hoon {name}, tum sunao."
    if any(w in lower for w in ["bye", "good night", "gn"]):
        return f"Bye {name}, take care."
    return f"{name}, ek second ruk, phir se bhej do."


def _find_image_url(obj):
    if isinstance(obj, str):
        match = re.search(r"https?://[^\s)\"']+\.(?:png|jpg|jpeg|webp)", obj, re.I)
        if match:
            return match.group(0)
        match = re.search(r"https?://[^\s)\"']+", obj)
        if match and any(x in match.group(0).lower() for x in ["image", "img", "cdn"]):
            return match.group(0)
        return None
    if isinstance(obj, dict):
        for k in ("url", "image_url", "b64_json"):
            if obj.get(k):
                val = obj[k]
                if k == "image_url" and isinstance(val, dict):
                    return val.get("url")
                return val
        for val in obj.values():
            found = _find_image_url(val)
            if found:
                return found
    if isinstance(obj, list):
        for item in obj:
            found = _find_image_url(item)
            if found:
                return found
    return None


def generate_image(prompt: str) -> str:
    last_err = None
    for provider in _providers():
        for model in provider["image_models"]()[:2]:
            try:
                r = requests.post(
                    provider["images_url"],
                    headers=_headers(provider),
                    json={"model": model, "prompt": prompt, "n": 1, "size": "1024x1024"},
                    timeout=25,
                )
                data = r.json() if r.content else {}
                if r.status_code >= 400:
                    raise RuntimeError(data.get("error", data))
                url = _find_image_url(data)
                if not url:
                    raise RuntimeError("no image")
                mark_ok(model, provider["name"])
                return url
            except Exception as e:
                last_err = e
                mark_fail(model)
    raise RuntimeError(f"Image failed: {last_err}")


async def generate_image_async(prompt: str) -> str:
    return await asyncio.to_thread(generate_image, prompt)
