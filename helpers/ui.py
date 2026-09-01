from telegram import InlineKeyboardButton

from config import SUPPORT_CHANNEL

PE = {
    "crown": "6026292029179301727",
    "star": "6026162407066309019",
    "fire": "6321353301707203203",
    "heart": "6267140231632262769",
    "owner": "6147603715462271535",
    "support": "6145175650190759830",
    "chat": "6026162407066309019",
    "spark": "6026292029179301727",
    "home": "6267140231632262769",
}

LINE = "<code>━━━━━━━━━━━━━━━━━━━━</code>"
OWNER_USER = "SANATANI_BACHA"
OWNER_NAME = "🉩◕𝐇𝐀𝐑𝐑𝐘◕🉪 =‌𐌓 ⨮⃘🇮🇳™"


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
