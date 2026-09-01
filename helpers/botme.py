USERNAME = "HARRY_HERUKOBOT"
FIRST = "Chatbot"
NICKS = ["harry"]


def apply_me(me):
    global USERNAME, FIRST, NICKS
    USERNAME = (getattr(me, "username", None) or USERNAME or "").lstrip("@")
    FIRST = (getattr(me, "first_name", None) or FIRST or "Chatbot").strip()
    nicks = set()
    if USERNAME and len(USERNAME) > 2:
        nicks.add(USERNAME.lower())
    low = FIRST.lower()
    if low and len(low) > 2 and low not in {"bot", "chatbot", "ai"}:
        nicks.add(low)
    nicks.add("harry")
    NICKS = [n for n in nicks if n and n not in {"ai", "bot"}]
    return USERNAME


def uname(bot=None) -> str:
    if bot is not None:
        live = (getattr(bot, "username", None) or "").lstrip("@")
        if live:
            return live
    return USERNAME.lstrip("@")


def nicknames(bot=None):
    extra = []
    if bot is not None:
        u = (getattr(bot, "username", None) or "").lstrip("@").lower()
        if u:
            extra.append(u)
    seen = set()
    out = []
    for n in extra + NICKS:
        if n and n not in seen and n not in {"ai", "bot"}:
            seen.add(n)
            out.append(n)
    return out
