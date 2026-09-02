import random
from telegram.ext import CommandHandler

from helpers.database import db
from helpers.decorators import is_owner
from helpers.ui import LINE

quotes_col = db.daily_quote_chats

QUOTES = [
    "Chhoti si baat, badi si smile.",
    "Aaj slow, par aage.",
    "Dil halka rakh, baaki ho jayega.",
    "Ek pyara message kaafi hai.",
    "Raat late ho, dil soft ho.",
    "Jo feel ho, wohi sach.",
    "Thoda rest, phir glow.",
    "Tum kaafi ho.",
]


async def dailyquote(update, context):
    if not update.message:
        return
    q = random.choice(QUOTES)
    await update.message.reply_text(f"✨  {q}\n{LINE}")


async def autquote(update, context):
    if not update.message:
        return
    chat = update.effective_chat
    if chat.type == "private":
        return await update.message.reply_text("Group mein /autquote on")
    if not is_owner(update.effective_user.id):
        try:
            member = await context.bot.get_chat_member(chat.id, update.effective_user.id)
            if member.status not in ("creator", "administrator"):
                return await update.message.reply_text("Admin only")
        except Exception:
            return
    arg = (context.args[0].lower() if context.args else "on")
    if arg in ("off", "stop"):
        quotes_col.delete_one({"chat_id": chat.id})
        return await update.message.reply_text("Daily quote off")
    quotes_col.update_one({"chat_id": chat.id}, {"$set": {"chat_id": chat.id, "on": True}}, upsert=True)
    await update.message.reply_text("Daily quote on. /dailyquote abhi bhej sakte ho.")


def register(app):
    app.add_handler(CommandHandler("dailyquote", dailyquote))
    app.add_handler(CommandHandler("autquote", autquote))
