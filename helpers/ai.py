import asyncio
import time

import requests

from config import AI_MAX_TOKENS, AI_TEMPERATURE, GROQ_API_KEY, GROQ_BASE_URL
from helpers.catalog import groq_chat_models, mark_fail, mark_ok

_CACHE = {}
_CACHE_TTL = 45
CHAT_TIMEOUT = 20
MAX_TRIES = 3


def _extract_text(data):
    try:
        msg = data["choices"][0]["message"]
        text = (msg.get("content") or "").strip()
        if not text:
            text = str(msg.get("reasoning") or msg.get("reasoning_content") or "").strip()
        return text
    except Exception:
        return ""


def _post_groq(model, messages):
    r = requests.post(
        f"{GROQ_BASE_URL}/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": messages,
            "max_tokens": min(AI_MAX_TOKENS, 512),
            "temperature": AI_TEMPERATURE,
        },
        timeout=CHAT_TIMEOUT,
    )
    data = r.json() if r.content else {}
    if r.status_code == 429:
        mark_fail(model)
        raise RuntimeError(f"groq/{model}: rate limited")
    if r.status_code >= 400 or "choices" not in data:
        raise RuntimeError(f"groq/{model}: {data.get('error', data)}")
    text = _extract_text(data)
    if not text:
        raise RuntimeError(f"groq/{model}: empty reply")
    return text


def safe_ai(messages: list) -> str:
    key = str(messages[-2:] if messages else [])
    hit = _CACHE.get(key)
    if hit and time.time() - hit[0] < _CACHE_TTL:
        return hit[1]

    last_err = None
    for model in groq_chat_models()[:MAX_TRIES]:
        try:
            text = _post_groq(model, messages)
            mark_ok(model, "groq")
            _CACHE[key] = (time.time(), text)
            print(f"AI OK: groq / {model}")
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


def generate_image(prompt: str) -> str:
    raise RuntimeError("Groq image nahi deta. /image ab band hai.")


async def generate_image_async(prompt: str) -> str:
    return await asyncio.to_thread(generate_image, prompt)
