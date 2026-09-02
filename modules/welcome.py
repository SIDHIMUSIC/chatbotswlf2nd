from telegram.ext import CommandHandler, MessageHandler, filters

from config import STICKERS
from helpers.database import db
from helpers.decorators import is_owner
from helpers.rich import Rich
from helpers.style import sc
from helpers.ui import LINE
from helpers.botme import uname

wel_col = db.welcome_cfg


def welcome_on(chat_id: int) -> bool:
    doc = wel_col.find_one({"chat_id": chat_id}) or {}
    return bool(doc.get("on", True))


def set_welcome(chat_id: int, on: bool):
    wel_col.update_one({"chat_id": chat_id}, {"$set": {"on": on}}, upsert=True)


async def _admin(update, context):
    user = update.effective_user
    if is_owner(user.id):
        return True
    try:
        m = await context.bot.get_chat_member(update.effective_chat.id, user.id)
        return m.status in ("creator", "administrator")
    except Exception:
        return False


def _card(member, chat):
    name = member.first_name or "friend"
    handle = f"@{member.username}" if member.username else "—"
    title = chat.title or sc("group")
    r = Rich()
    r.e("star").t(f"  {sc('welcome')}  {name}\n\n")
    r.e("chat").t(f"  {sc('group')}:  {title}\n")
    r.e("id").t(f"  {sc('your id')}:  {member.id}\n")
    r.e("user").t(f"  {sc('username')}:  {handle}\n\n")
    r.t(f"{LINE}\n")
    r.e("heart").t(f"  {sc('hope you find good vibes')}\n")
    r.e("spark").t(f"  {sc('new friends and lots of fun')}  ").e("fire")
    return r.build()


async def welcome(update, context):
    msg = update.message
    if not msg or not msg.new_chat_members:
        return
    chat = update.effective_chat
    if not welcome_on(chat.id):
        return
    bot_id = context.bot.id
    for member in msg.new_chat_members:
        if member.id == bot_id:
            try:
                await msg.reply_text(f"Bot add. Mention @{uname(context.bot)}")
            except Exception:
                pass
            continue
        if member.is_bot:
            continue
        text, ents = _card(member, chat)
        try:
            await msg.reply_text(text, entities=ents)
        except Exception:
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


async def welcome_cmd(update, context):
    if not update.message:
        return
    if update.effective_chat.type == "private":
        return await update.message.reply_text("Group mein /welcome on ya off")
    if not await _admin(update, context):
        return await update.message.reply_text("Admin only")
    arg = (context.args[0].lower() if context.args else "")
    if arg in ("off", "disable", "0"):
        set_welcome(update.effective_chat.id, False)
        return await update.message.reply_text("Welcome off")
    if arg in ("on", "enable", "1"):
        set_welcome(update.effective_chat.id, True)
        return await update.message.reply_text("Welcome on")
    state = "on" if welcome_on(update.effective_chat.id) else "off"
    await update.message.reply_text(f"Welcome {state}\n/welcome on\n/welcome off")


def register(app):
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
    app.add_handler(CommandHandler("welcome", welcome_cmd))
