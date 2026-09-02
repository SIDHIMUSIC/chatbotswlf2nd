import random

from telegram.ext import MessageHandler, filters

from config import STICKERS
from helpers import is_bot_banned
from helpers.persona import get_prefs
from helpers.style import sc

POOL = [v for v in STICKERS.values() if v]

EMOJI_KEY = {
    "❤️": "love", "❤": "love", "💖": "love", "💕": "love", "💞": "love",
    "💋": "kiss", "😘": "kiss", "😗": "kiss",
    "😂": "laugh", "😆": "laugh", "🤣": "laugh", "😅": "laugh",
    "😎": "cool", "👍": "cool", "✨": "cool",
    "😢": "sad", "😭": "sad", "🥺": "sad", "😔": "sad",
    "👋": "hi", "👏": "hi",
}

LINES = {
    "love": "aww ✨", "kiss": "muaah", "laugh": "haha",
    "cool": "mast", "sad": "hug", "hi": "hey",
}


def pick_sticker(emoji=None):
    key = EMOJI_KEY.get(emoji or "")
    if key and STICKERS.get(key):
        return key, STICKERS[key]
    if POOL:
        key = random.choice(list(STICKERS.keys()))
        return key, STICKERS[key]
    return None, None


def _group_ok(msg, bot):
    if msg.chat.type == "private":
        return True
    replied = (
        msg.reply_to_message
        and msg.reply_to_message.from_user
        and msg.reply_to_message.from_user.id == bot.id
    )
    return bool(replied)


async def sticker_chat(update, context):
    msg = update.message
    if not msg or not msg.sticker:
        return
    user = update.effective_user
    if not user or is_bot_banned(user.id):
        return
    if not _group_ok(msg, context.bot):
        return
    key, file_id = pick_sticker(getattr(msg.sticker, "emoji", None))
    try:
        if file_id:
            await msg.reply_sticker(file_id)
    except Exception as e:
        print("sticker reply fail:", e)
    try:
        await msg.reply_text(LINES.get(key) or sc("sticker received"))
    except Exception:
        pass


async def photo_react(update, context):
    msg = update.message
    if not msg or not msg.photo:
        return
    user = update.effective_user
    if not user or is_bot_banned(user.id):
        return
    if not _group_ok(msg, context.bot):
        return
    key, file_id = pick_sticker()
    prefs = get_prefs(user.id)
    try:
        if file_id:
            await msg.reply_sticker(file_id)
    except Exception as e:
        print("photo sticker fail:", e)
    cap = random.choice([
        sc("nice pic"),
        sc("mast photo"),
        sc("cuteeee"),
        sc("looks good"),
    ])
    try:
        await msg.reply_text(f"{cap}  ·  {prefs.get('mode') or 'bestie'}")
    except Exception:
        pass


def register(app):
    app.add_handler(MessageHandler(filters.Sticker.ALL, sticker_chat))
    app.add_handler(MessageHandler(filters.PHOTO, photo_react))
