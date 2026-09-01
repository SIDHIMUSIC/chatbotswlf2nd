from helpers.database import users

MODES = {
    "bestie": "You are a close bestie. Light roast, care. Short replies.",
    "gf": "You are his girlfriend vibe. Soft, warm, natural. Short replies.",
    "bf": "You are her boyfriend vibe. Calm, protective, teasing. Short replies.",
    "waifu": "You are a cute playful companion. Short replies.",
    "pro": "You are a smart assistant. Clear useful answers.",
}

LANGS = {
    "hinglish": "HINGLISH only. Mix Hindi and English in every reply. No pure English paragraph.",
    "hi": "Har jawab sirf Hindi Devanagari mein do. English mat likho.",
    "en": "Reply in English only. No Hindi.",
    "ur": "Har jawab sirf Urdu mein do.",
    "pa": "Har jawab sirf Punjabi mein do.",
    "bn": "Har jawab sirf Bangla mein do.",
}

SKIP_MEM = ("permanent", "teach", "async", "def ", "nickname", "memory teach")


def get_prefs(user_id: int) -> dict:
    doc = users.find_one({"user_id": user_id}) or {}
    mode = doc.get("mode") or "bestie"
    lang = doc.get("lang") or "hinglish"
    if mode not in MODES:
        mode = "bestie"
    if lang not in LANGS:
        lang = "hinglish"
    return {"mode": mode, "lang": lang}


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
        f"You chat with {name}. "
        f"MOOD={mode}. {style} "
        f"LANGUAGE={lang}. {lang_line} "
        "Stay in this mood and language for every reply. "
        "Reply only to the latest user line. 1-3 short lines. "
        "Never mention mood, language names, rules, or models."
        f"{_safe_mem(memory)}"
    )
