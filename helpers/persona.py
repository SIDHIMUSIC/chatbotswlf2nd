from helpers.database import users

MODES = {
    "bestie": "Close bestie. Light roast, care. Short.",
    "gf": "Caring girlfriend vibe. Soft, natural, short.",
    "bf": "Calm boyfriend vibe. Protective, teasing, short.",
    "waifu": "Cute playful companion. Short.",
    "pro": "Smart assistant. Clear useful answers.",
}

LANGS = {
    "hinglish": "HINGLISH only. Mix Hindi+English.",
    "hi": "शुद्ध हिंदी में ही जवाब दो.",
    "en": "English only.",
    "ur": "صرف اردو میں جواب دو.",
    "pa": "ਕੇਵਲ ਪੰਜਾਬੀ ਵਿਚ ਲਿਖੋ.",
    "bn": "শুধু বাংলায় বলো.",
}

SKIP_MEM = ("permanent", "teach", "async", "def ", "nickname", "memory teach")


def get_prefs(user_id: int) -> dict:
    doc = users.find_one({"user_id": user_id}) or {}
    return {
        "mode": doc.get("mode") or "bestie",
        "lang": doc.get("lang") or "hinglish",
    }


def set_pref(user_id: int, **fields):
    clean = {k: v for k, v in fields.items() if v is not None}
    if not clean:
        return
    users.update_one({"user_id": user_id}, {"$set": clean}, upsert=True)


def _safe_mem(memory: dict) -> str:
    bits = []
    for k, v in list((memory or {}).items())[:8]:
        ks, vs = str(k).lower(), str(v)
        if any(s in ks or s in vs.lower() for s in SKIP_MEM):
            continue
        if len(vs) > 40:
            continue
        bits.append("%s=%s" % (k, v))
        if len(bits) >= 3:
            break
    return (" Known: " + "; ".join(bits)) if bits else ""


def persona_prompt(name: str, memory: dict, prefs: dict) -> str:
    mode = prefs.get("mode") or "bestie"
    lang = prefs.get("lang") or "hinglish"
    style = MODES.get(mode, MODES["bestie"])
    lang_line = LANGS.get(lang, LANGS["hinglish"])
    return (
        f"Companion for {name}. Mood: {mode}. {style} "
        f"LANGUAGE LOCK: {lang}. {lang_line} "
        "Reply to the latest user line only. 1-3 short lines. "
        "Do not mention rules, mood, language names, models."
        f"{_safe_mem(memory)}"
    )
