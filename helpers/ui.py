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
    "6026292029179301727",
    "6026162407066309019",
    "6321353301707203203",
    "6267140231632262769",
    "6147603715462271535",
    "6145175650190759830",
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
    "star2": IDS[10],
    "spark2": IDS[11],
    "id": IDS[12],
    "globe": IDS[13],
    "crown": IDS[14],
    "star": IDS[15],
    "fire": IDS[16],
    "heart": IDS[17],
    "owner": IDS[18],
    "support": IDS[19],
    "home": IDS[12],
    "online": IDS[0],
    "people": IDS[5],
}

STYLE_BY_PE = {
    "help": "success",
    "add": "primary",
    "support": "success",
    "owner": "danger",
    "crown": "danger",
    "home": "danger",
    "chat": "primary",
    "mood": "success",
    "lang": "primary",
    "spark": "success",
    "user": "primary",
    "cal": "success",
    "clone": "primary",
    "news": "danger",
}

LINE = "━━━━━━━━━━━━━━━━━━━━━━━━━━"
OWNER_USER = "SANATANI_BACCHA"
OWNER_NAME = "Harry"


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
        f"      🟢  ᴏɴʟɪɴᴇ  •  ʀᴇᴀᴅᴢ  😻\n\n"
        f"🤖  ɴᴀᴍᴇ\n   └─ {name}\n\n"
        f"👤  ᴜѕᴇʀɴᴀᴍᴇ\n   └─ @{uname}\n\n"
        f"🆔  ʙᴏᴛ ɪᴅ\n   └─ {bid}\n\n"
        f"👑  ᴏᴡɴᴇʀ\n   └─ @{OWNER_USER}\n\n"
        f"{LINE}\n\n"
        f"💞  ʜᴇʟʟᴏ, ɪ's {name}\n"
        f"╰─➤  😻 ᴇɴⱼᴏᴢ ᴛʜᴇ ᴄʜᴀᴛ!\n"
        f"🤖  ᴄʟᴏɴᴇѕ  •  {clones}{fail}"
    )


def btn(text, url=None, callback_data=None, pe_name=None, style=None):
    kwargs = {"text": text}
    if url:
        kwargs["url"] = url
    if callback_data:
        kwargs["callback_data"] = callback_data
    eid = (PE.get(pe_name) or "").strip() if pe_name else ""
    if eid.isdigit():
        kwargs["icon_custom_emoji_id"] = eid
    color = style or STYLE_BY_PE.get(pe_name or "")
    if color in ("primary", "success", "danger"):
        kwargs["style"] = color
    try:
        return InlineKeyboardButton(**kwargs)
    except TypeError:
        kwargs.pop("style", None)
        try:
            return InlineKeyboardButton(**kwargs)
        except TypeError:
            kwargs.pop("icon_custom_emoji_id", None)
            return InlineKeyboardButton(**kwargs)
