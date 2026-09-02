from telegram.ext import CommandHandler

from helpers.database import users, chat_logs
from helpers.ui import LINE
from helpers.style import sc
from config import STICKERS


def _level(xp):
    xp = int(xp or 0)
    lvl = xp // 50 + 1
    need = 50 - (xp % 50)
    return xp, lvl, need


async def rank_cmd(update, context):
    if not update.message:
        return
    user = update.effective_user
    target = user
    if update.message.reply_to_message and update.message.reply_to_message.from_user:
        target = update.message.reply_to_message.from_user
    doc = users.find_one({"user_id": target.id}) or {}
    xp, lvl, need = _level(doc.get("xp"))
    chats = 0
    try:
        chats = chat_logs.count_documents({"user_id": target.id, "role": "user"})
    except Exception:
        pass
    text = (
        f"🏆  {sc('rank card')}\n{LINE}\n\n"
        f"👤  {target.first_name}\n"
        f"⭐  {sc('level')}  ·  {lvl}\n"
        f"⚡  xp  ·  {xp}\n"
        f"💬  {sc('chats')}  ·  {chats}\n"
        f"🔥  next  ·  {need} xp"
    )
    await update.message.reply_text(text)
    sid = STICKERS.get("cool") or STICKERS.get("s1")
    if sid:
        try:
            await update.message.reply_sticker(sid)
        except Exception:
            pass


async def couple_cmd(update, context):
    if not update.message:
        return
    a = update.effective_user.first_name or "A"
    if update.message.reply_to_message and update.message.reply_to_message.from_user:
        b = update.message.reply_to_message.from_user.first_name or "B"
    elif context.args:
        b = " ".join(context.args)
    else:
        return await update.message.reply_text("Reply karke /couple ya /couple name")
    seed = (a.lower() + b.lower())
    pct = (sum(ord(c) for c in seed) % 71) + 25
    text = (
        f"💕  {sc('couple')}\n{LINE}\n\n"
        f"{a}  +  {b}\n"
        f"{pct}%"
    )
    await update.message.reply_text(text)
    sid = STICKERS.get("love") or STICKERS.get("kiss")
    if sid:
        try:
            await update.message.reply_sticker(sid)
        except Exception:
            pass


def register(app):
    app.add_handler(CommandHandler("rank", rank_cmd))
    app.add_handler(CommandHandler("xp", rank_cmd))
    app.add_handler(CommandHandler("couple", couple_cmd))
