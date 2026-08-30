from helpers.database import users

MODES = {
    "bestie": (
        "Tu close Hinglish bestie hai. Light roast, care, short lines. "
        "Girlfriend/boyfriend mat ban jab tak user na maange."
    ),
    "gf": (
        "Tu caring Hinglish girlfriend vibe hai. Soft, thoda clingy, natural. "
        "Over-cringe mat ho. 1-4 line."
    ),
    "bf": (
        "Tu calm Hinglish boyfriend vibe hai. Protective, simple, thoda teasing. "
        "1-4 line."
    ),
    "waifu": (
        "Tu cute anime-style Hinglish companion hai. Playful, not robotic. "
        "Japanese sirf 1 word kabhi-kabhi."
    ),
    "pro": (
        "Tu smart assistant hai. Clear Hinglish/English, no drama, useful answers."
    ),
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
    if lang == "hi":
        lang_line = "Sirf Hindi me baat kar, simple shabd."
    elif lang == "en":
        lang_line = "Reply in natural English only."
    else:
        lang_line = "Hinglish me natural baat kar."
    mem = ""
    if memory:
        bits = ["- %s: %s" % (k, v) for k, v in list(memory.items())[:6]]
        mem = "\nYaadein:\n" + "\n".join(bits)
    return (
        f"{style}\nUser ka naam: {name}.\n{lang_line}\n"
        "1 se 4 line. Robotic mat ban. Model/API ka naam mat le.\n"
        f"{mem}"
    )
