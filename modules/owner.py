import random
import time

from telegram import InlineKeyboardMarkup
from telegram.ext import CommandHandler

from config import START_IMAGES, SUPPORT_CHANNEL
from helpers.decorators import is_owner
from helpers.database import users, bot_bans, chat_logs
from helpers.rich import Rich
from helpers.style import sc
from helpers.ui import LINE, OWNER_USER, btn


def owner_card():
    r = Rich()
    r.e("crown").t(f"  {sc('bot owner profile')}  ").e("star").t(f"\n{LINE}\n\n")
    r.e("star").t(f"  {sc('this intelligent ai bot is proudly crafted')}\n")
    r.t(f"{sc('owned and managed by')}\n\n")
    r.e("user").t("  Harry\n")
    r.e("heart").t(f"  @{OWNER_USER}\n\n")
    r.e("fire").t(f"  {sc('a passionate developer')}\n")
    r.t(f"•  {sc('smart automation')}\n")
    r.t(f"•  {sc('secure systems')}\n")
    r.t(f"•  {sc('smooth user experience')}\n\n")
    r.e("spark").t(f"  {sc('vision')}\n")
    r.t(f"{sc('creating powerful reliable ai bots')}\n\n")
    r.e("crown").t(f"  {sc('owner tools')}\n")
    r.t("/broadcast   /bcstats\n/stats   /heal   /restart\n/id")
    kb = InlineKeyboardMarkup([
        [btn("◍ ᴏᴡɴᴇʀ ◍", url=f"https://t.me/{OWNER_USER}", pe_name="owner")],
        [btn("◍ ѕᴜᴘᴘᴏʀᴛ ◍", url=SUPPORT_CHANNEL, pe_name="support")],
        [
            btn("ᴄᴏɴѕᴏʟᴇ", callback_data="ui_owner", pe_name="crown"),
            btn("🏠 ʜᴏᴍᴇ", callback_data="home", pe_name="home"),
        ],
    ])
    text, ents = r.build()
    return text, ents, kb


async def _send_owner(message):
    text, ents, kb = owner_card()
    photo = random.choice(START_IMAGES) if START_IMAGES else None
    if photo:
        try:
            return await message.reply_photo(
                photo=photo, caption=text, caption_entities=ents, reply_markup=kb
            )
        except Exception:
            try:
                return await message.reply_photo(photo=photo, caption=text, reply_markup=kb)
            except Exception:
                pass
    try:
        return await message.reply_text(text, entities=ents, reply_markup=kb, disable_web_page_preview=True)
    except Exception:
        return await message.reply_text(text, reply_markup=kb, disable_web_page_preview=True)


async def owner_info(update, context):
    if not update.message:
        return
    await _send_owner(update.message)


async def stats(update, context):
    if not update.message:
        return
    if not is_owner(update.effective_user.id):
        return await update.message.reply_text("Owner only")
    total_users = users.count_documents({})
    total_banned = bot_bans.count_documents({})
    total_groups = len(
        chat_logs.distinct("chat_id", {"chat_type": {"$in": ["group", "supergroup"]}})
    )
    since = time.time() - 86400
    daily_active = len(chat_logs.distinct("user_id", {"time": {"$gte": since}}))
    await update.message.reply_text(
        f"📊  {sc('bot dashboard')}\n{LINE}\n\n"
        f"👤  {sc('users')}  ·  {total_users}\n"
        f"🔥  {sc('daily')}  ·  {daily_active}\n"
        f"👥  {sc('groups')}  ·  {total_groups}\n"
        f"🚫  {sc('banned')}  ·  {total_banned}\n\n"
        f"/broadcast   /bcstats"
    )


async def id_cmd(update, context):
    if not update.message:
        return
    user = update.effective_user
    chat = update.effective_chat
    await update.message.reply_text(
        f"👤  {sc('id')}  ·  {user.id}\n"
        f"💬  {sc('chat')}  ·  {chat.id}\n"
        f"📍  {chat.type}"
    )


def register(app):
    app.add_handler(CommandHandler("owner", owner_info))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("id", id_cmd))
