from telegram.ext import MessageHandler, filters

from config import STICKERS
from helpers.style import sc
from helpers.ui import LINE
from helpers.botme import uname


async def welcome(update, context):
    msg = update.message
    if not msg or not msg.new_chat_members:
        return
    bot_id = context.bot.id
    handle = uname(context.bot)
    for member in msg.new_chat_members:
        if member.is_bot:
            continue
        name = member.first_name or "friend"
        text = (
            f"✨  {sc('welcome')}  {name}\n"
            f"{LINE}\n\n"
            f"{sc('type')} @{handle} {sc('ya reply')}"
        )
        try:
            await msg.reply_text(text)
        except Exception:
            pass
        sid = STICKERS.get("hi") or STICKERS.get("s1")
        if sid:
            try:
                await msg.reply_sticker(sid)
            except Exception:
                pass
        if member.id == bot_id:
            try:
                await msg.reply_text(f"Bot add ho gaya. Mention @{handle}")
            except Exception:
                pass


def register(app):
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
