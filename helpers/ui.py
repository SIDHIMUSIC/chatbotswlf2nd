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
    "hey": IDS[10],
    "bot": IDS[11],
    "mood": IDS[12],
    "lang": IDS[13],
    "online": IDS[0],
    "clock": IDS[1],
    "people": IDS[2],
    "chat": IDS[3],
    "help": IDS[4],
    "spark": IDS[5],
    "user": IDS[6],
    "cal": IDS[7],
    "clone": IDS[8],
    "add": IDS[9],
    "news": IDS[10],
    "owner": IDS[11],
    "crown": IDS[12],
    "home": IDS[13],
    "heart": IDS[0],
    "fire": IDS[1],
    "star": IDS[2],
    "support": IDS[3],
}

LINE = "━━━━━━━━━━━━━━━━━━━━━━━━━━"
OWNER_USER = "SANATANI_BACHA"
OWNER_NAME = "🉩◕🇧𝐀𝐑𝐑𝐘◕🉪 =‌𐌓 Ἑc⃘🇮🇳™"


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
        f"      🟢  ᴏɴʟɪɴᴇ  •  ʀᴇᴀᴅʏ\n\n"
        f"🤖  {name}\n"
        f"👤  @{uname}\n"
        f"🆔  {bid}\n"
        f"👑  {OWNER_ID}\n"
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
