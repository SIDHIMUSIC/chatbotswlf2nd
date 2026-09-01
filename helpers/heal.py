"""Soft heal + hard restart. Heroku worker exit=1 pe khud uthata hai."""
import os
import threading
import time

_LAST_RESTART = 0
_RESTART_GAP = 180
_ERR_HITS = []
_ERR_WINDOW = 90
_ERR_LIMIT = 6


def soft_heal():
    cleared = []
    try:
        from helpers import ai as ai_mod
        ai_mod._CACHE.clear()
        cleared.append("ai_cache")
    except Exception as e:
        print("heal ai cache:", e)
    try:
        from helpers import catalog as cat
        cat._DEAD.clear()
        cat._BEST["groq"] = None
        cleared.append("model_cooldown")
    except Exception as e:
        print("heal catalog:", e)
    return cleared


def can_restart():
    return time.time() - _LAST_RESTART >= _RESTART_GAP


def schedule_restart(delay=1.5):
    global _LAST_RESTART
    if not can_restart():
        print("Restart skipped: cooldown")
        return False
    _LAST_RESTART = time.time()
    print(f"HEAL restart in {delay}s")

    def _die():
        time.sleep(delay)
        os._exit(1)

    threading.Thread(target=_die, daemon=True).start()
    return True


def note_error(err):
    """Fatal errors count karke auto restart."""
    now = time.time()
    text = str(err or "").lower()
    name = type(err).__name__.lower() if err else ""
    _ERR_HITS.append(now)
    while _ERR_HITS and now - _ERR_HITS[0] > _ERR_WINDOW:
        _ERR_HITS.pop(0)

    fatal_bits = (
        "conflict", "terminated by other getupdates",
        "event loop is closed", "cannot close a running event loop",
        "application is not running", "httpx.connecterror",
        "remoteprotocolerror", "serverdisconnected",
    )
    is_fatal = any(b in text or b in name for b in fatal_bits)
    noisy = len(_ERR_HITS) >= _ERR_LIMIT
    if is_fatal or noisy:
        soft_heal()
        return schedule_restart(2)
    return False


def owner_intent(text: str):
    t = (text or "").strip().lower()
    if not t:
        return None
    hard = (
        "restart", "reboot", "reboot kar", "restart kar",
        "band karke chalu", "dobara start", "bot restart",
    )
    soft = (
        "sudhar", "sudhaar", "theek kar", "theek kr",
        "heal", "fix", "gadbad", "gdbd", "sahi kar",
        "cache clear", "model fix",
    )
    if any(k in t for k in hard):
        return "restart"
    if any(k in t for k in soft):
        return "heal"
    return None
