"""Live NaraRouter catalog — never block the first chat."""
import time
import requests

from config import (
    NARA_API_KEY,
    NARA_BASE_URL,
    NARA_IMAGE_MODELS,
    NARA_MODELS,
    OPENROUTER_IMAGE_MODELS,
    OPENROUTER_MODELS,
    AI_QUALITY,
)

PLANS_URL = "https://router.bynara.id/api/plans"
IMAGE_HINTS = ("image", "imagine", "flux", "video", "lyria", "tts", "whisper", "embed", "diffusion")

FAST_FREE = [
    "agnes-2.5-flash",
    "agnes-2.0-flash",
    "glm-5.3-flash-free",
    "minimax-m3-free",
    "auto/bynara",
]

_CACHE = {"t": 0, "chat": list(NARA_MODELS) or list(FAST_FREE), "image": list(NARA_IMAGE_MODELS), "all": []}
_TTL = 1800
_DEAD = {}
_BEST = {"nara": None, "openrouter": None}


def _is_image(mid: str) -> bool:
    m = (mid or "").lower()
    return any(h in m for h in IMAGE_HINTS)


def is_dead(model: str) -> bool:
    return _DEAD.get(model, 0) > time.time()


def mark_fail(model: str):
    _DEAD[model] = time.time() + 180
    if _BEST.get("nara") == model:
        _BEST["nara"] = None


def mark_ok(model: str, provider="nara"):
    _DEAD.pop(model, None)
    _BEST[provider] = model


def refresh(force=False):
    now = time.time()
    if not force and _CACHE["t"] and now - _CACHE["t"] < _TTL:
        return _CACHE
    try:
        r = requests.get(PLANS_URL, timeout=4)
        r.raise_for_status()
        plans = (r.json().get("data") or [])
        free = []
        for plan in plans:
            if plan.get("code") == "free" or plan.get("price_daily_idr") == 0:
                for mid in plan.get("models") or []:
                    if mid and mid not in free and not _is_image(mid):
                        free.append(mid)
        if free:
            _CACHE["chat"] = free + [m for m in FAST_FREE if m not in free]
            _CACHE["t"] = now
            print("Nara catalog:", _CACHE["chat"][:8])
    except Exception as e:
        print("Nara plans skip:", e)
        if not _CACHE["t"]:
            _CACHE["chat"] = list(NARA_MODELS) or list(FAST_FREE)
            _CACHE["t"] = now
    return _CACHE


def nara_chat_models():
    models = [m for m in (_CACHE.get("chat") or FAST_FREE) if not is_dead(m) and not _is_image(m)]
    best = _BEST.get("nara")
    if best and best in models:
        models = [best] + [m for m in models if m != best]
    return models or list(FAST_FREE)


def nara_image_models():
    return [m for m in (_CACHE.get("image") or NARA_IMAGE_MODELS) if not is_dead(m)] or list(NARA_IMAGE_MODELS)


def next_nara_chat():
    return nara_chat_models()


def or_chat_models():
    models = [m for m in OPENROUTER_MODELS if not is_dead(m)] or list(OPENROUTER_MODELS)
    best = _BEST.get("openrouter")
    if best and best in models:
        models = [best] + [m for m in models if m != best]
    return models


def or_image_models():
    return [m for m in OPENROUTER_IMAGE_MODELS if not is_dead(m)] or list(OPENROUTER_IMAGE_MODELS)


def snapshot():
    return {
        "chat": _CACHE.get("chat") or FAST_FREE,
        "image": _CACHE.get("image") or list(NARA_IMAGE_MODELS),
        "dead": [m for m, t in _DEAD.items() if t > time.time()],
        "best": dict(_BEST),
        "quality": AI_QUALITY,
    }
