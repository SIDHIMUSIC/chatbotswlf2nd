from telegram import InlineKeyboardButton

from config import OWNER_ID, SUPPORT_CHANNEL

PE = {
    "chat": "6026162407066309019",
    "help": "6026292029179301727",
    "mood": "6267140231632262769",
    "lang": "6321353301707203203",
    "spark": "6026292029179301727",
    "user": "6147603715462271535",
    "cal": "6026162407066309019",
    "bot": "6145175650190759830",
    "add": "6321353301707203203",
    "news": "6026292029179301727",
    "owner": "6147603715462271535",
    "crown": "6026292029179301727",
    "home": "6267140231632262769",
    "star": "6026162407066309019",
    "fire": "6321353301707203203",
    "heart": "6267140231632262769",
    "support": "6145175650190759830",
}

LINE = "━━━━━━━━━━━━━━━━━━━━━━━━━━"
OWNER_USER = "SANATANI_BACHA"
OWNER_NAME = "🉩◕𝐇𝐀𝐑𝐑𝐘◕🉪 =‌𐌓 ⨮⃘🇮🇳™"


def spaced(word: str) -> str:
    return "  ".join(list(word.upper()))


def boot_card(me, clones=0, failed=None):
    name = (getattr(me, "first_name", None) or "JULIET").strip()
    uname = (getattr(me, "username", None) or "JULIET_MUSUCBOT").lstrip("@")
    bid = getattr(me, "id", "—")
    title = spaced(name[:12]) if name else spaced("JULIET")
    fail = ""
    if failed:
        fail = f"\n⚠️  {failed[0][:80]}"
    return (
        f"╭{LINE}╮\n"
        f"       💗  {title}  💗\n"
        f"          A I   C H A T\n"
        f"╰{LINE}╯\n\n"
        f"      🟢  ᴏɴʟɪɴᴇ  •  ʀᴇᴀᴅʏ  😻\n\n"
        f"🤖  ɴᴀᴍᴇ\n"
        f"   └─ {name}\n\n"
        f"👤  ᴜѕᴇʀɴᴀᴍᴇ\n"
        f"   └─ @{uname}\n\n"
        f"🆔  ʙᴏᴛ ɪᴅ\n"
        f"   └─ {bid}\n\n"
        f"👑  ᴏᴡɴᴇʀ\n"
        f"   └─ {OWNER_ID}\n\n"
        f"{LINE}\n\n"
        f"💞  ʜᴇʟʟᴏ, ɪ'ᴍ {name}\n"
        f"🧠  ѕᴍᴀʀᴛ • ғᴀѕᴛ • ᴄᴜᴛᴇ\n"
        f"⚡  ʀᴇᴀᴅʏ ᴛᴏ ᴄʜᴀᴛ\n\n"
        f"╰─➤  😻 ᴇɴⱼᴏʏ ᴛʜᴇ ᴄʜᴀᴛ!\n"
        f"🤖  ᴄʟᴏɴᴇѕ  •  {clones}{fail}"
    )


def pe(name: str, fallback: str = "✦") -> str:
    return fallback


def btn(text, url=None, callback_data=None, pe_name=None):
    kwargs = {"text": text}
    if url:
        kwargs["url"] = url
    if callback_data:
        kwargs["callback_data"] = callback_data
    eid = (PE.get(pe_name) or PE.get("star") or "").strip() if pe_name else ""
    if eid.isdigit():
        kwargs["icon_custom_emoji_id"] = eid
    try:
        return InlineKeyboardButton(**kwargs)
    except TypeError:
        kwargs.pop("icon_custom_emoji_id", None)
        return InlineKeyboardButton(**kwargs)
