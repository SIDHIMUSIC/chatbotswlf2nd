import time

GAP = 3.0
_LAST = {}


def too_fast(user_id: int) -> bool:
    now = time.time()
    prev = _LAST.get(user_id, 0)
    if now - prev < GAP:
        return True
    _LAST[user_id] = now
    if len(_LAST) > 4000:
        old = now - 60
        dead = [k for k, t in _LAST.items() if t < old]
        for k in dead[:1500]:
            _LAST.pop(k, None)
    return False
