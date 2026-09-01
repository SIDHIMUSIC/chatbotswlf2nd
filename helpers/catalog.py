"""Groq model pool."""
import time

from config import AI_QUALITY, GROQ_MODELS

_DEAD = {}
_BEST = {"groq": None}


def is_dead(model: str) -> bool:
    return _DEAD.get(model, 0) > time.time()


def mark_fail(model: str):
    _DEAD[model] = time.time() + 180
    if _BEST.get("groq") == model:
        _BEST["groq"] = None


def mark_ok(model: str, provider="groq"):
    _DEAD.pop(model, None)
    _BEST[provider] = model


def refresh(force=False):
    return snapshot()


def groq_chat_models():
    models = [m for m in GROQ_MODELS if not is_dead(m)] or list(GROQ_MODELS)
    best = _BEST.get("groq")
    if best and best in models:
        models = [best] + [m for m in models if m != best]
    return models


def snapshot():
    return {
        "chat": list(GROQ_MODELS),
        "image": [],
        "dead": [m for m, t in _DEAD.items() if t > time.time()],
        "best": dict(_BEST),
        "quality": AI_QUALITY,
        "provider": "groq",
    }
