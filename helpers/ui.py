from telegram import InlineKeyboardButton

from config import OWNER_ID, SUPPORT_CHANNEL

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
    "5440621591387980068",
    "5373012449597335010",
    "5208959082735616282",
    "5229086076873748176",
]

PE = {
    "chat": IDS[0],
    "help": IDS[1],
    "mood": IDS[2],
    "lang": IDS[3],
    "spark": IDS[4],
    "user": IDS[5],
    "cal": IDS[6],
    "clone": IDS[7],
    "add": IDS[8],
    "news": IDS[9],
    "owner": IDS[10],
    "crown": IDS[11],
    "home": IDS[12],
    "star": IDS[13],
    "heart": IDS[4],
    "fire": IDS[6],
    "support": IDS[9],
}

LINE = "━━━━━━━━━━━━━━━━━━━━━━━━━━"
OWNER_USER = "SANATANI_BACHA"
OWNER_NAME = "🉩◕🇧𝐀𝐑𝐑𝐘◕🉪 =‌𐌓 Ἑc⃘🇮🇳™"


def spaced(word: str) -> str:
    return "  ".join(list((word or "").upper()))


def boot_card(me, clones=0, failed=None):
    name = (getattr(me, "first_name", None) or "Chatbot").strip()
    uname = (getattr(me, "username", None) or "HARRY_HERUKOBOT").lstrip("@")
    bid = getattr(me, "id", "—")
    title = spaced(name[:12])
    fail = f"\n⚠️  {failed[0][:80]}" if failed else ""
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
    eid = (PE.get(pe_name) or "").strip() if pe_name else ""
    if eid.isdigit():
        kwargs["icon_custom_emoji_id"] = eid
    try:
        return InlineKeyboardButton(**kwargs)
    except TypeError:
        kwargs.pop("icon_custom_emoji_id", None)
        return InlineKeyboardButton(**kwargs)
