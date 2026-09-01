import asyncio
import re
import time

import requests

from config import (
    AI_MAX_TOKENS,
    AI_TEMPERATURE,
    GEMINI_API_KEY,
    GEMINI_BASE_URL,
    NARA_API_KEY,
    NARA_BASE_URL,
    OPENROUTER_BASE_URL,
    OPENROUTER_KEY,
)
from helpers.catalog import (
    gemini_chat_models,
    gemini_image_models,
    mark_fail,
    mark_ok,
    nara_image_models,
    next_nara_chat,
    or_chat_models,
    or_image_models,
)

_CACHE = {}
_CACHE_TTL = 45
CHAT_TIMEOUT = 20
MAX_TRIES = 2


def _openai_providers():
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


def _messages_to_gemini(messages):
    system_parts = []
    contents = []
    for msg in messages or []:
        role = msg.get("role") or "user"
        text = (msg.get("content") or "").strip()
        if not text:
            continue
        if role == "system":
            system_parts.append(text)
        elif role == "assistant":
            contents.append({"role": "model", "parts": [{"text": text}]})
        else:
            contents.append({"role": "user", "parts": [{"text": text}]})
    # Gemini 3.x rejects requests whose last content role is model.
    if contents and contents[-1].get("role") == "model":
        contents.append({"role": "user", "parts": [{"text": "continue"}]})
    return "\n".join(system_parts).strip(), contents


def _extract_gemini_text(data):
    bits = []
    for cand in data.get("candidates") or []:
        content = cand.get("content") or {}
        for part in content.get("parts") or []:
            text = part.get("text")
            if text and not part.get("thought"):
                bits.append(text)
    if bits:
        return "\n".join(bits).strip()
    for cand in data.get("candidates") or []:
        content = cand.get("content") or {}
        for part in content.get("parts") or []:
            if part.get("text"):
                bits.append(part["text"])
    return "\n".join(bits).strip()


def _post_gemini(model, messages):
    system, contents = _messages_to_gemini(messages)
    if not contents:
        contents = [{"role": "user", "parts": [{"text": "hi"}]}]
    url = f"{GEMINI_BASE_URL}/models/{model}:generateContent"
    payload = {
        "contents": contents,
        "generationConfig": {
            "maxOutputTokens": max(AI_MAX_TOKENS, 256),
            "temperature": AI_TEMPERATURE,
            "thinkingConfig": {"thinkingLevel": "LOW"},
        },
    }
    if system:
        payload["systemInstruction"] = {"parts": [{"text": system}]}
    r = requests.post(
        url,
        params={"key": GEMINI_API_KEY},
        headers={"Content-Type": "application/json"},
        json=payload,
        timeout=CHAT_TIMEOUT,
    )
    data = r.json() if r.content else {}
    if r.status_code >= 400:
        err = data.get("error") or data
        raise RuntimeError(f"gemini/{model}: {err}")
    text = _extract_gemini_text(data)
    if not text:
        raise RuntimeError(f"gemini/{model}: empty reply")
    return text


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

    if GEMINI_API_KEY:
        for model in gemini_chat_models()[:MAX_TRIES]:
            try:
                text = _post_gemini(model, messages)
                mark_ok(model, "gemini")
                _CACHE[key] = (time.time(), text)
                print(f"AI OK: gemini / {model}")
                return text
            except Exception as e:
                last_err = e
                mark_fail(model)
                print("AI FAIL:", e)

    for provider in _openai_providers():
        for model in provider["chat_models"]()[:MAX_TRIES]:
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

    print("AI ALL FAILED:", last_err)
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
        inline = obj.get("inlineData") or obj.get("inline_data")
        if isinstance(inline, dict) and inline.get("data"):
            mime = inline.get("mimeType") or inline.get("mime_type") or "image/png"
            return f"data:{mime};base64,{inline['data']}"
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


def _generate_gemini_image(prompt: str):
    last_err = None
    for model in gemini_image_models()[:2]:
        try:
            url = f"{GEMINI_BASE_URL}/models/{model}:generateContent"
            payload = {
                "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                "generationConfig": {
                    "responseModalities": ["TEXT", "IMAGE"],
                },
            }
            r = requests.post(
                url,
                params={"key": GEMINI_API_KEY},
                json=payload,
                timeout=25,
            )
            data = r.json() if r.content else {}
            if r.status_code >= 400:
                raise RuntimeError(data.get("error", data))
            found = _find_image_url(data)
            if not found:
                raise RuntimeError("no image")
            mark_ok(model, "gemini")
            return found
        except Exception as e:
            last_err = e
            mark_fail(model)
    raise RuntimeError(last_err)


def generate_image(prompt: str) -> str:
    last_err = None
    if GEMINI_API_KEY:
        try:
            return _generate_gemini_image(prompt)
        except Exception as e:
            last_err = e
            print("GEMINI IMAGE FAIL:", e)
    for provider in _openai_providers():
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
