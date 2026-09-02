from telegram.ext import CommandHandler

from helpers.ui import LINE
from helpers.style import sc


async def id_cmd(update, context):
    if not update.message:
        return
    chat = update.effective_chat
    user = update.effective_user
    target = user
    if update.message.reply_to_message and update.message.reply_to_message.from_user:
        target = update.message.reply_to_message.from_user
    uname = f"@{target.username}" if target.username else "—"
    text = (
        f"🆔  {sc('id card')}\n{LINE}\n\n"
        f"👤  {target.first_name}\n"
        f"{uname}\n"
        f"user  ·  <code>{target.id}</code>\n"
        f"chat  ·  <code>{chat.id}</code>"
    )
    await update.message.reply_text(text, parse_mode="HTML")


def register(app):
    app.add_handler(CommandHandler("id", id_cmd))
    app.add_handler(CommandHandler("info", id_cmd))
