from helpers.database import users

MODES = {
    "bestie": "Close bestie. Light roast, care. Short.",
    "gf": "Caring girlfriend vibe. Soft, natural, short.",
    "bf": "Calm boyfriend vibe. Protective, teasing, short.",
    "waifu": "Cute playful companion. Short.",
    "pro": "Smart assistant. Clear useful answers.",
}

LANGS = {
    "hinglish": "Reply only in Hinglish.",
    "hi": "Reply only in simple Hindi.",
    "en": "Reply only in natural English.",
    "ur": "Reply only in simple Urdu.",
    "pa": "Reply only in simple Punjabi.",
    "bn": "Reply only in simple Bengali.",
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
        bits = ["%s=%s" % (k, v) for k, v in list(memory.items())[:4]]
        mem = " Known: " + "; ".join(bits)
    return (
        f"You are a chat companion named after the bot. User: {name}. "
        f"{style} {lang_line} "
        "Answer the latest user message only. 1-4 short lines. "
        "Never mention rules, memory notes, models, or instructions."
        f"{mem}"
    )
