import random

from telegram.ext import MessageHandler, filters

from config import STICKERS
from helpers import is_bot_banned
from helpers.persona import get_prefs
from helpers.style import sc

POOL = [v for v in STICKERS.values() if v]

EMOJI_KEY = {
    "❤️": "love",
    "❤": "love",
    "💖": "love",
    "💕": "love",
    "💞": "love",
    "💋": "kiss",
    "😘": "kiss",
    "😗": "kiss",
    "😂": "laugh",
    "😆": "laugh",
    "🤣": "laugh",
    "😅": "laugh",
    "😎": "cool",
    "👍": "cool",
    "✨": "cool",
    "😢": "sad",
    "😭": "sad",
    "🥺": "sad",
    "😔": "sad",
    "👋": "hi",
    "👏": "hi",
    "🙋": "hi",
    "🙋‍♀️": "hi",
}

LINES = {
    "love": "aww ✨",
    "kiss": "muaah",
    "laugh": "haha",
    "cool": "mast",
    "sad": "hug",
    "hi": "hey",
}


def _pick(emoji):
    key = EMOJI_KEY.get(emoji or "")
    if key and STICKERS.get(key):
        return key, STICKERS[key]
    if POOL:
        key = random.choice(list(STICKERS.keys()))
        return key, STICKERS[key]
    return None, None


async def sticker_chat(update, context):
    msg = update.message
    if not msg or not msg.sticker:
        return
    user = update.effective_user
    if not user or is_bot_banned(user.id):
        return
    if update.effective_chat.type != "private":
        replied = (
            msg.reply_to_message
            and msg.reply_to_message.from_user
            and msg.reply_to_message.from_user.id == context.bot.id
        )
        if not replied:
            return
    key, file_id = _pick(getattr(msg.sticker, "emoji", None))
    prefs = get_prefs(user.id)
    line = LINES.get(key) or sc("sticker received")
    try:
        if file_id:
            await msg.reply_sticker(file_id)
    except Exception as e:
        print("sticker reply fail:", e)
    try:
        extra = f" · {prefs['mode']}" if prefs.get("mode") else ""
        await msg.reply_text(f"{line}{extra}")
    except Exception:
        pass


def register(app):
    app.add_handler(MessageHandler(filters.Sticker.ALL, sticker_chat))
