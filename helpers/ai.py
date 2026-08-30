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
_CACHE_TTL = 80


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


def _cache_key(messages):
    return str(messages[-4:] if messages else [])


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
    extra = {}
    low = model.lower()
    max_tokens = AI_MAX_TOKENS
    if any(x in low for x in ("gpt-5", "claude", "kimi", "gemini-3", "opus", "reason")):
        max_tokens = max(AI_MAX_TOKENS, 400)
        extra["reasoning_effort"] = "low"
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": AI_TEMPERATURE,
        **extra,
    }
    r = requests.post(
        provider["url"],
        headers=_headers(provider),
        json=payload,
        timeout=45,
    )
    data = r.json() if r.content else {}
    if r.status_code >= 400 or "choices" not in data:
        raise RuntimeError(f"{provider['name']}/{model}: {data.get('error', data)}")
    text = _extract_text(data)
    if not text:
        raise RuntimeError("empty reply")
    return text


def safe_ai(messages: list) -> str:
    refresh()
    key = _cache_key(messages)
    hit = _CACHE.get(key)
    if hit and time.time() - hit[0] < _CACHE_TTL:
        return hit[1]
    last_err = None
    tried = 0
    for provider in _providers():
        models = provider["chat_models"]()
        for model in models[:12]:
            tried += 1
            try:
                text = _post_chat(provider, model, messages)
                mark_ok(model)
                _CACHE[key] = (time.time(), text)
                print(f"AI OK: {provider['name']} / {model}")
                return text
            except Exception as e:
                last_err = e
                mark_fail(model)
                print("AI FAIL:", e)
                continue
    print("AI ALL FAILED after", tried, "tries:", last_err)
    return ""


async def safe_ai_async(messages: list) -> str:
    return await asyncio.to_thread(safe_ai, messages)


def get_fallback_reply(user_id: int, text: str, name: str) -> str:
    lower = text.lower()
    memory = get_memory(user_id)
    if memory:
        for key, value in memory.items():
            if key in lower or str(value).lower() in lower:
                return f"{name}, haan yaad hai — {key}: {value}"
    if any(w in lower for w in ["hi", "hello", "hey", "namaste", "hola"]):
        return f"Hey {name}! Kaise ho?"
    if any(w in lower for w in ["kaise ho", "how are you", "kya haal"]):
        return f"Main theek hoon {name}, tum sunao."
    if any(w in lower for w in ["bye", "alvida", "good night", "gn"]):
        return f"Bye {name}, take care."
    if any(w in lower for w in ["thank", "shukriya", "thanks"]):
        return f"Welcome {name}"
    try:
        last_chats = list(
            chat_logs.find({"user_id": user_id, "role": "user"}).sort("time", -1).limit(5)
        )
        if last_chats:
            last = (last_chats[0].get("text") or "")[:80]
            return f"{name}, AI thodi busy hai. Last baat thi: {last}"
    except Exception as e:
        print("Fallback chat error:", e)
    return f"{name}, abhi reply late ho raha hai, thodi der baad try karo."


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


def _images_generations(provider, model, prompt):
    r = requests.post(
        provider["images_url"],
        headers=_headers(provider),
        json={"model": model, "prompt": prompt, "n": 1, "size": "1024x1024"},
        timeout=90,
    )
    data = r.json() if r.content else {}
    if r.status_code >= 400:
        raise RuntimeError(data.get("error", data))
    url = _find_image_url(data)
    if not url:
        raise RuntimeError("no image in generations response")
    return url


def _image_via_chat(provider, model, prompt):
    r = requests.post(
        provider["url"],
        headers=_headers(provider),
        json={
            "model": model,
            "messages": [{"role": "user", "content": f"Generate an image: {prompt}"}],
            "max_tokens": 200,
        },
        timeout=90,
    )
    data = r.json() if r.content else {}
    if r.status_code >= 400:
        raise RuntimeError(data.get("error", data))
    url = _find_image_url(data)
    if not url:
        raise RuntimeError("no image url in chat response")
    return url


def generate_image(prompt: str) -> str:
    last_err = None
    for provider in _providers():
        for model in provider["image_models"]()[:8]:
            try:
                url = _images_generations(provider, model, prompt)
                mark_ok(model)
                print(f"IMG OK generations: {provider['name']} / {model}")
                return url
            except Exception as e:
                last_err = e
                print("IMG generations FAIL:", e)
            try:
                url = _image_via_chat(provider, model, prompt)
                mark_ok(model)
                print(f"IMG OK chat: {provider['name']} / {model}")
                return url
            except Exception as e:
                last_err = e
                mark_fail(model)
                print("IMG chat FAIL:", e)
    raise RuntimeError(f"Image failed: {last_err}")


async def generate_image_async(prompt: str) -> str:
    return await asyncio.to_thread(generate_image, prompt)
