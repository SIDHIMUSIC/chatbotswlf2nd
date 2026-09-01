from telegram import InlineKeyboardButton

from config import OWNER_ID, SUPPORT_CHANNEL

# User-provided custom emoji ids (unique per button)
IDS = [
    "5280858699286471614",
    "6118209143972040877",
    "5431427591120628886",
    "5229102316145106683",
    "5301096984617166561",
    "6129584162992034014",
    "6336813264122419000",
    "6147896245684803245",
    "6082592230021795516",
    "6291916484918648855",
]

PE = {
    "hey": IDS[0],
    "bot": IDS[1],
    "chat": IDS[2],
    "help": IDS[3],
    "mood": IDS[4],
    "lang": IDS[5],
    "spark": IDS[6],
    "user": IDS[7],
    "cal": IDS[8],
    "clone": IDS[9],
    "add": IDS[0],
    "news": IDS[1],
    "owner": IDS[2],
    "crown": IDS[3],
    "home": IDS[4],
    "heart": IDS[5],
    "fire": IDS[6],
    "star": IDS[7],
    "support": IDS[8],
    "online": IDS[9],
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
        f"🤖  ɴᴀᴍᴇ\n   └─ {name}\n\n"
        f"👤  ᴜѕᴇʀɴᴀᴍᴇ\n   └─ @{uname}\n\n"
        f"🆔  ʙᴏᴛ ɪᴅ\n   └─ {bid}\n\n"
        f"👑  ᴏᴡɴᴇʀ\n   └─ {OWNER_ID}\n\n"
        f"{LINE}\n\n"
        f"💞  ʜᴇʟʟᴏ, ɪ'ᴍ {name}\n"
        f"╰─➤  😻 ᴇɴⱼᴏʏ ᴛʜᴇ ᴄʜᴀᴛ!\n"
        f"🤖  ᴄʟᴏɴᴇѕ  •  {clones}{fail}"
    )


def pe(name: str, fallback: str = "✦") -> str:
    eid = (PE.get(name) or "").strip()
    if not eid.isdigit():
        return fallback
    return f'<tg-emoji emoji-id="{eid}">{fallback}</tg-emoji>'


def btn(text, url=None, callback_data=None, pe_name=None):
    kwargs = {"text": text}
    if url:
        kwargs["url"] = url
    if callback_data:
        kwargs["callback_data"] = callback_data
    eid = (PE.get(pe_name) or "").strip() if pe_name else ""
    if eid.isdigit():
        kwargs["icon_custom_emoji_id"] = eid
    try:
        return InlineKeyboardButton(**kwargs)
    except TypeError:
        kwargs.pop("icon_custom_emoji_id", None)
        return InlineKeyboardButton(**kwargs)
