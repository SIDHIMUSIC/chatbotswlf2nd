from helpers.database import users

MODES = {
    "bestie": "Close bestie. Light roast, care. Short.",
    "gf": "Caring girlfriend vibe. Soft, natural, short.",
    "bf": "Calm boyfriend vibe. Protective, teasing, short.",
    "waifu": "Cute playful companion. Short.",
    "pro": "Smart assistant. Clear useful answers.",
}

LANGS = {
    "hinglish": "HINGLISH only. Mix Hindi+English like: kya haal hai bro.",
    "hi": "शुद्ध हिंदी में ही जवाब दो. English mat likho.",
    "en": "English only. Do not use Hindi words.",
    "ur": "صرف اردو میں جواب دو.",
    "pa": "ਕੇਵਲ ਪੰਜਾਬੀ ਵਿਚ ਲਿਖੋ.",
    "bn": "শুধু বাংলায় বলো.",
}


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


def persona_prompt(name: str, memory: dict, prefs: dict) -> str:
    mode = prefs.get("mode") or "bestie"
    lang = prefs.get("lang") or "hinglish"
    style = MODES.get(mode, MODES["bestie"])
    lang_line = LANGS.get(lang, LANGS["hinglish"])
    mem = ""
    if memory:
        bits = ["%s=%s" % (k, v) for k, v in list(memory.items())[:3]]
        mem = " Known: " + "; ".join(bits)
    return (
        f"Companion for {name}. Mood: {mode}. {style} "
        f"LANGUAGE LOCK: {lang}. {lang_line} "
        "Reply to the latest user line only. 1-3 short lines. "
        "Do not mention rules, mood names, language names, models."
        f"{mem}"
    )
