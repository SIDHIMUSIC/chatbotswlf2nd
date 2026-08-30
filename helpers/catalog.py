"""Live NaraRouter + OpenRouter model catalog."""
import time
import requests

from config import (
    NARA_API_KEY,
    NARA_BASE_URL,
    NARA_IMAGE_MODELS,
    NARA_MODELS,
    OPENROUTER_BASE_URL,
    OPENROUTER_IMAGE_MODELS,
    OPENROUTER_KEY,
    OPENROUTER_MODELS,
    AI_QUALITY,
)

PLANS_URL = "https://router.bynara.id/api/plans"
IMAGE_HINTS = (
    "image", "imagine", "flux", "video", "lyria", "tts", "whisper",
    "embed", "diffusion",
)

_CACHE = {"t": 0, "chat": [], "image": [], "all": []}
_TTL = 600
_DEAD = {}
_RR = {"nara": 0, "openrouter": 0}


def _is_image(mid: str) -> bool:
    m = (mid or "").lower()
    return any(h in m for h in IMAGE_HINTS)


def _mark_dead(model: str, seconds=600):
    _DEAD[model] = time.time() + seconds


def is_dead(model: str) -> bool:
    until = _DEAD.get(model, 0)
    return until > time.time()


def mark_fail(model: str):
    _mark_dead(model, 8 * 60)


def mark_ok(model: str):
    _DEAD.pop(model, None)


def _fetch_nara_from_plans():
    r = requests.get(PLANS_URL, timeout=15)
    r.raise_for_status()
    data = r.json()
    plans = data.get("data") or []
    free = []
    paid = []
    seen = set()
    for plan in plans:
        if not plan.get("is_active"):
            continue
        names = plan.get("models") or []
        bucket = free if (plan.get("code") == "free" or plan.get("price_daily_idr") == 0) else paid
        for mid in names:
            if not mid or mid in seen:
                continue
            seen.add(mid)
            bucket.append(mid)
    return free, paid


def _fetch_nara_entitled():
    if not NARA_API_KEY:
        return []
    r = requests.get(
        f"{NARA_BASE_URL}/models",
        headers={"Authorization": f"Bearer {NARA_API_KEY}"},
        timeout=15,
    )
    if r.status_code >= 400:
        return []
    data = r.json()
    items = data.get("data") or data.get("models") or []
    out = []
    for item in items:
        mid = item.get("id") if isinstance(item, dict) else str(item)
        if mid:
            out.append(mid)
    return out


def refresh(force=False):
    now = time.time()
    if not force and _CACHE["chat"] and now - _CACHE["t"] < _TTL:
        return _CACHE
    chat, image = [], []
    try:
        free, paid = _fetch_nara_from_plans()
    except Exception as e:
        print("Nara plans fetch fail:", e)
        free, paid = list(NARA_MODELS), []
    entitled = []
    try:
        entitled = _fetch_nara_entitled()
    except Exception as e:
        print("Nara /v1/models fail:", e)

    nara_all = []
    for group in (free, entitled, paid, NARA_MODELS, ["auto/bynara", "gpt-5.5"]):
        for mid in group:
            if mid and mid not in nara_all:
                nara_all.append(mid)

    quality = AI_QUALITY
    if quality == "free":
        pool = [m for m in (free + entitled) if m]
        if not pool:
            pool = nara_all
    elif quality == "high":
        high = [m for m in nara_all if any(x in m.lower() for x in ("gpt-5", "claude", "opus", "sonnet"))]
        pool = high + [m for m in nara_all if m not in high]
    else:
        pool = []
        for mid in free + ["auto/bynara"] + [m for m in nara_all if m not in free]:
            if mid not in pool:
                pool.append(mid)

    for mid in pool + list(NARA_IMAGE_MODELS):
        if _is_image(mid):
            if mid not in image:
                image.append(mid)
        else:
            if mid not in chat:
                chat.append(mid)

    _CACHE.update({"t": now, "chat": chat, "image": image or list(NARA_IMAGE_MODELS), "all": nara_all})
    print("Nara catalog chat models:", len(chat), chat[:20])
    return _CACHE


def nara_chat_models():
    refresh()
    return [m for m in _CACHE["chat"] if not is_dead(m)] or list(_CACHE["chat"])


def nara_image_models():
    refresh()
    imgs = [m for m in _CACHE["image"] if not is_dead(m)]
    return imgs or list(NARA_IMAGE_MODELS)


def next_nara_chat():
    models = nara_chat_models()
    if not models:
        return []
    i = _RR["nara"] % len(models)
    _RR["nara"] += 1
    return models[i:] + models[:i]


def or_chat_models():
    return [m for m in OPENROUTER_MODELS if not is_dead(m)] or list(OPENROUTER_MODELS)


def or_image_models():
    return [m for m in OPENROUTER_IMAGE_MODELS if not is_dead(m)] or list(OPENROUTER_IMAGE_MODELS)


def snapshot():
    refresh()
    return {
        "chat": _CACHE["chat"],
        "image": _CACHE["image"],
        "dead": [m for m, t in _DEAD.items() if t > time.time()],
        "quality": AI_QUALITY,
    }
