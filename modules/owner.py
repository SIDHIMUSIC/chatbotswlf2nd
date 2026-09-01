import random
import time

from telegram.ext import CommandHandler

from config import START_IMAGES
from helpers.decorators import is_owner
from helpers.database import users, bot_bans, chat_logs


async def owner_info(update, context):
    from modules.start import owner_card
    if not update.message:
        return
    text, ents, kb = owner_card()
    photo = random.choice(START_IMAGES) if START_IMAGES else None
    if photo:
        try:
            await update.message.reply_photo(
                photo=photo, caption=text, caption_entities=ents, reply_markup=kb
            )
            return
        except Exception:
            try:
                await update.message.reply_photo(photo=photo, caption=text, reply_markup=kb)
                return
            except Exception:
                pass
    try:
        await update.message.reply_text(text, entities=ents, reply_markup=kb, disable_web_page_preview=True)
    except Exception:
        await update.message.reply_text(text, reply_markup=kb, disable_web_page_preview=True)


async def stats(update, context):
    if not update.message or not is_owner(update.effective_user.id):
        return
    total_users = users.count_documents({})
    total_banned = bot_bans.count_documents({})
    total_groups = len(
        chat_logs.distinct("chat_id", {"chat_type": {"$in": ["group", "supergroup"]}})
    )
    since = time.time() - 86400
    daily_active = len(chat_logs.distinct("user_id", {"time": {"$gte": since}}))
    await update.message.reply_text(
        f"📊  ʙᴏᴛ ᴅᴀѕʜʙᴏᴀʀᴅ\n\n"
        f"👤  ᴜѕᴇʀѕ  ·  {total_users}\n"
        f"🔥  ᴅᴀɪʟʏ  ·  {daily_active}\n"
        f"👥  ɢʀᴏᴜᴘѕ  ·  {total_groups}\n"
        f"🚫  ʙᴀɴ  ·  {total_banned}"
    )


async def id_cmd(update, context):
    if not update.message:
        return
    user = update.effective_user
    chat = update.effective_chat
    await update.message.reply_text(
        f"👤  ɪᴅ  ·  {user.id}\n"
        f"💬  ᴄʜᴀᴛ  ·  {chat.id}\n"
        f"📍  {chat.type}"
    )


def register(app):
    app.add_handler(CommandHandler("owner", owner_info))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("id", id_cmd))
