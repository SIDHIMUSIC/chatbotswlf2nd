import asyncio
import random
from datetime import datetime

import pytz
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler

from config import START_IMAGES, SUPPORT_CHANNEL, BOT_USERNAME
from helpers.decorators import is_owner

IST = pytz.timezone("Asia/Kolkata")

BOOT = [
    (
        "✨ <b>HARRY SYSTEM</b>\n"
        "<code>━━━━━━━━━━━━━━━━━━━━━</code>\n\n"
        "○ Connecting engines\n"
        "○ Warming AI core\n"
        "○ Loading memory\n\n"
        "<code>[███░░░░░░░]</code>  28%"
    ),
    (
        "✨ <b>HARRY SYSTEM</b>\n"
        "<code>━━━━━━━━━━━━━━━━━━━━━</code>\n\n"
        "● Connecting engines\n"
        "○ Warming AI core\n"
        "○ Loading memory\n\n"
        "<code>[█████░░░░░]</code>  54%"
    ),
    (
        "✨ <b>HARRY SYSTEM</b>\n"
        "<code>━━━━━━━━━━━━━━━━━━━━━</code>\n\n"
        "● Connecting engines\n"
        "● Warming AI core\n"
        "○ Loading memory\n\n"
        "<code>[████████░░]</code>  81%"
    ),
    (
        "✨ <b>HARRY SYSTEM</b>\n"
        "<code>━━━━━━━━━━━━━━━━━━━━━</code>\n\n"
        "● Connecting engines\n"
        "● Warming AI core\n"
        "● Loading memory\n\n"
        "<code>[██████████]</code>  100%\n\n"
        "<i>Ready.</i>"
    ),
]


def _now():
    return datetime.now(IST).strftime("%I:%M %p • %d %b")


def welcome_caption(user, bot_name):
    name = user.first_name or "Friend"
    uname = f"@{user.username}" if user.username else "Private"
    return (
        f"👑 <b>{bot_name.upper()}</b>\n"
        f"<code>━━━━━━━━━━━━━━━━━━━━━━━━</code>\n\n"
        f"Hey <a href='tg://user?id={user.id}'>{name}</a>\n"
        f"<i>Your personal AI companion is online.</i>\n\n"
        f"👤 {uname}\n"
        f"🕒 {_now()}\n\n"
        "✦ Natural Hinglish chat\n"
        "✦ /image — AI art\n"
        "✦ Memory — <code>yaad rakh naam: Ashu</code>\n"
        "✦ Group ready — mention se call\n\n"
        f"<code>━━━━━━━━━━━━━━━━━━━━━━━━</code>\n"
        "<b>Select a panel below</b>"
    )


def home_keyboard(user_id=None):
    rows = [
        [
            InlineKeyboardButton("💬 Start Chat", callback_data="menu_chat"),
            InlineKeyboardButton("🖼 Generate", callback_data="menu_image"),
        ],
        [
            InlineKeyboardButton("📚 Command Guide", callback_data="help_home"),
            InlineKeyboardButton("⚡ Features", callback_data="menu_features"),
        ],
        [
            InlineKeyboardButton("💙 Support", url=SUPPORT_CHANNEL),
            InlineKeyboardButton("👤 Owner", url="https://t.me/SANATANI_BACHA"),
        ],
    ]
    if user_id and is_owner(user_id):
        rows.append([InlineKeyboardButton("🔐 Owner Console", callback_data="menu_owner")])
    rows.append([InlineKeyboardButton("✨ Add me to Group", url=f"https://t.me/{BOT_USERNAME}?startgroup=true")])
    return InlineKeyboardMarkup(rows)


async def _play_loading(message):
    msg = await message.reply_text(BOOT[0], parse_mode="HTML")
    for frame in BOOT[1:]:
        await asyncio.sleep(0.28)
        try:
            await msg.edit_text(frame, parse_mode="HTML")
        except Exception:
            break
    await asyncio.sleep(0.18)
    return msg


async def _send_home(target_message, user, bot_name, loader=None):
    caption = welcome_caption(user, bot_name)
    kb = home_keyboard(user.id)
    photo = random.choice(START_IMAGES) if START_IMAGES else None
    sent = None
    if photo:
        try:
            sent = await target_message.reply_photo(
                photo=photo,
                caption=caption,
                parse_mode="HTML",
                reply_markup=kb,
            )
        except Exception:
            sent = None
    if sent is None:
        sent = await target_message.reply_text(
            caption,
            parse_mode="HTML",
            reply_markup=kb,
            disable_web_page_preview=True,
        )
    if loader:
        try:
            await loader.delete()
        except Exception:
            pass
    return sent


async def start(update, context):
    if not update.message:
        return
    bot_name = context.bot.first_name or "Harry"
    loader = await _play_loading(update.message)
    await _send_home(update.message, update.effective_user, bot_name, loader)


async def start_from_callback(update, context):
    query = update.callback_query
    await query.answer()
    bot_name = context.bot.first_name or "Harry"
    caption = welcome_caption(query.from_user, bot_name)
    kb = home_keyboard(query.from_user.id)
    try:
        await query.edit_message_caption(caption=caption, parse_mode="HTML", reply_markup=kb)
    except Exception:
        try:
            await query.edit_message_text(
                caption, parse_mode="HTML", reply_markup=kb, disable_web_page_preview=True
            )
        except Exception:
            await query.message.reply_text(
                caption, parse_mode="HTML", reply_markup=kb, disable_web_page_preview=True
            )


async def menu_callback(update, context):
    query = update.callback_query
    await query.answer()
    data = query.data
    back = InlineKeyboardMarkup([[InlineKeyboardButton("➡ Home", callback_data="home")]])

    if data == "menu_chat":
        text = (
            "💬 <b>LIVE CHAT</b>\n"
            "<code>━━━━━━━━━━━━━━━━━━</code>\n\n"
            "Yahan seedha message likho.\n"
            "Group me <b>Harry</b> bolo ya bot ko reply karo.\n\n"
            "Memory: <code>yaad rakh city: Patna</code>"
        )
    elif data == "menu_image":
        text = (
            "🖼 <b>AI STUDIO</b>\n"
            "<code>━━━━━━━━━━━━━━━━━━</code>\n\n"
            "<code>/image cyberpunk indian boy 4k</code>\n"
            "<code>/image lord krishna digital art</code>"
        )
    elif data == "menu_features":
        text = (
            "⚡ <b>WHAT’S INSIDE</b>\n"
            "<code>━━━━━━━━━━━━━━━━━━</code>\n\n"
            "• Multi-model AI router\n"
            "• NaraRouter + OpenRouter backup\n"
            "• Short, real Hinglish replies\n"
            "• Image generation\n"
            "• Personal memory + chat history\n"
            "• Owner tools + broadcast"
        )
    elif data == "menu_owner":
        if not is_owner(query.from_user.id):
            return await query.answer("Owner only.", show_alert=True)
        from modules.owner import owner_info
        return await owner_info(update, context)
    else:
        return

    try:
        await query.message.reply_text(text, parse_mode="HTML", reply_markup=back)
    except Exception:
        pass


def register(app):
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(menu_callback, pattern="^menu_"))
    app.add_handler(CallbackQueryHandler(start_from_callback, pattern="^home$"))
