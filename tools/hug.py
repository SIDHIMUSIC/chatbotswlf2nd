from telegram.ext import CommandHandler

from config import STICKERS


async def hug_cmd(update, context):
    if not update.message:
        return
    who = update.effective_user.first_name
    if update.message.reply_to_message and update.message.reply_to_message.from_user:
        who = update.message.reply_to_message.from_user.first_name
    elif context.args:
        who = " ".join(context.args)
    await update.message.reply_text(f"hug  ·  {who}")
    sid = STICKERS.get("love") or STICKERS.get("s8") or STICKERS.get("kiss")
    if sid:
        try:
            await update.message.reply_sticker(sid)
        except Exception:
            pass


def register(app):
    app.add_handler(CommandHandler("hug", hug_cmd))
