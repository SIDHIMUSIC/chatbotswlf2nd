from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationHandlerStop, MessageHandler, filters

from config import MUST_JOIN, MUST_JOIN_PHOTO
from helpers.decorators import is_owner


def _channel():
    raw = (MUST_JOIN or "").strip()
    if not raw:
        return ""
    raw = raw.replace("https://t.me/", "").replace("http://t.me/", "").lstrip("@")
    return raw


def _link(handle):
    return f"https://t.me/{handle}"


async def must_join_channel(update, context):
    handle = _channel()
    if not handle:
        return
    msg = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    if not msg or not user or not chat:
        return
    if chat.type != "private":
        return
    if is_owner(user.id):
        return
    chat_id = handle if handle.startswith("-") else f"@{handle}"
    try:
        member = await context.bot.get_chat_member(chat_id, user.id)
        if member.status in ("member", "administrator", "creator", "restricted"):
            return
    except Exception as e:
        err = str(e).lower()
        print("must_join check:", e)
        if "admin" in err or "chat not found" in err or "peer" in err:
            return
    link = _link(handle)
    kb = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Join Channel", url=link)]]
    )
    cap = (
        f"Hello {user.first_name}\n\n"
        f"Channel join karo tab bot chalega.\n"
        f"{link}"
    )
    try:
        if MUST_JOIN_PHOTO:
            await msg.reply_photo(photo=MUST_JOIN_PHOTO, caption=cap, reply_markup=kb)
        else:
            await msg.reply_text(cap, reply_markup=kb)
    except Exception as e:
        print("must_join send:", e)
        try:
            await msg.reply_text(cap, reply_markup=kb)
        except Exception:
            pass
    raise ApplicationHandlerStop()


def register(app):
    app.add_handler(
        MessageHandler(filters.ChatType.PRIVATE, must_join_channel),
        group=-2,
    )
