import asyncio
import random
from datetime import datetime

import pytz
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler, filters

from config import START_IMAGES, SUPPORT_CHANNEL, BOT_USERNAME
from helpers.decorators import is_owner
from helpers.style import sc
from helpers.database import users

IST = pytz.timezone("Asia/Kolkata")
MENU_BTN = "Menu"

BOOT = [
    f"booting core\n<code>ooooo</code>".replace("o", "○"),
    "linking memory",
    "ai online",
]


def reply_menu():
    return ReplyKeyboardMarkup(
        [[KeyboardButton("Menu")], [KeyboardButton("Imagine"), KeyboardButton("Help")]],
        resize_keyboard=True,
        is_persistent=True,
    )


def panel_kb(user_id=None):
    rows = [
        [
            InlineKeyboardButton("New Chat", callback_data="menu_chat"),
            InlineKeyboardButton("Imagine", callback_data="menu_image"),
        ],
        [
            InlineKeyboardButton("Roleplay", callback_data="menu_role"),
            InlineKeyboardButton("Memory", callback_data="menu_memory"),
        ],
        [InlineKeyboardButton("Add to Group", url=f"https://t.me/{BOT_USERNAME}?startgroup=true")],
        [
            InlineKeyboardButton("Updates", url=SUPPORT_CHANNEL),
            InlineKeyboardButton("Support", url="https://t.me/SANATANI_BACHA"),
        ],
        [
            InlineKeyboardButton("Owner", callback_data="menu_owner"),
            InlineKeyboardButton("About", callback_data="menu_features"),
        ],
    ]
    if user_id and is_owner(user_id):
        rows.append([InlineKeyboardButton("Console", callback_data="menu_owner")])
    return InlineKeyboardMarkup(rows)


def caption(user, bot_name, extra_users=None):
    name = user.first_name or "baby"
    clock = datetime.now(IST).strftime("%I:%M %p")
    count = extra_users or "-"
    return (
        f"✦ <b>{sc('hey')} {name}</b>\n"
        f"✦ {sc('i am')} <b>{bot_name}</b> {sc('your personal ai')}\n\n"
        f"{sc('always online for late night talks')}\n"
        f"{sc('image art  memory  roleplay  groups')}\n\n"
        f"🟢 {sc('status')}  {sc('online')}\n"
        f"🕒 {clock}   👤 {count}\n\n"
        f"<i>{sc('powered by harry')}</i>"
    )


async def _user_count():
    try:
        return users.estimated_document_count()
    except Exception:
        try:
            return users.count_documents({})
        except Exception:
            return None


async def send_home(message, user, bot_name, loading=True):
    loader = None
    if loading:
        loader = await message.reply_text(f"✦ {sc('booting core')}", parse_mode="HTML")
        await asyncio.sleep(0.25)
        try:
            await loader.edit_text(f"✦ {sc('ai online')}", parse_mode="HTML")
        except Exception:
            pass
    text = caption(user, bot_name, await _user_count())
    kb = panel_kb(user.id)
    photo = random.choice(START_IMAGES) if START_IMAGES else None
    sent = None
    if photo:
        try:
            sent = await message.reply_photo(photo=photo, caption=text, parse_mode="HTML", reply_markup=kb)
        except Exception:
            sent = None
    if sent is None:
        sent = await message.reply_text(text, parse_mode="HTML", reply_markup=kb, disable_web_page_preview=True)
    try:
        await message.reply_text(sc("quick bar ready"), reply_markup=reply_menu())
    except Exception:
        pass
    if loader:
        try:
            await loader.delete()
        except Exception:
            pass
    return sent


async def start(update, context):
    if not update.message:
        return
    await send_home(update.message, update.effective_user, context.bot.first_name or "Harry")


async def start_from_callback(update, context):
    query = update.callback_query
    await query.answer()
    text = caption(query.from_user, context.bot.first_name or "Harry", await _user_count())
    kb = panel_kb(query.from_user.id)
    try:
        await query.edit_message_caption(caption=text, parse_mode="HTML", reply_markup=kb)
    except Exception:
        try:
            await query.edit_message_text(text, parse_mode="HTML", reply_markup=kb, disable_web_page_preview=True)
        except Exception:
            await query.message.reply_text(text, parse_mode="HTML", reply_markup=kb)


async def menu_callback(update, context):
    query = update.callback_query
    await query.answer()
    data = query.data
    back = InlineKeyboardMarkup([[InlineKeyboardButton("Home", callback_data="home")]])
    pages = {
        "menu_chat": (
            f"💬 <b>{sc('live chat')}</b>\n\n"
            f"{sc('type anything like a friend')}\n"
            f"{sc('in groups tag me or reply')}\n\n"
            "<code>yaad rakh naam: Ashu</code>"
        ),
        "menu_image": (
            f"🖼 <b>{sc('imagine studio')}</b>\n\n"
            "<code>/image cyberpunk indian boy 4k</code>\n"
            "<code>/image lord krishna digital art</code>"
        ),
        "menu_role": (
            f"🎭 <b>{sc('roleplay')}</b>\n\n"
            f"{sc('just start the scene in chat')}\n"
            f"{sc('example')}: <i>tum meri bestie ho campus pe</i>"
        ),
        "menu_memory": (
            f"🧠 <b>{sc('memory')}</b>\n\n"
            "<code>yaad rakh city: Patna</code>"
        ),
        "menu_features": (
            f"ℹ️ <b>{sc('about')}</b>\n\n"
            f"• {sc('nara router + openrouter backup')}\n"
            f"• {sc('fast hinglish personality')}\n"
            f"• {sc('made by')} @SANATANI_BACHA"
        ),
    }
    if data == "menu_owner":
        from modules.owner import owner_info
        return await owner_info(update, context)
    text = pages.get(data)
    if text:
        await query.message.reply_text(text, parse_mode="HTML", reply_markup=back)


async def reply_bar(update, context):
    if not update.message:
        return
    text = (update.message.text or "").strip()
    if text == "Menu":
        return await send_home(update.message, update.effective_user, context.bot.first_name or "Harry", loading=False)
    if text == "Imagine":
        return await update.message.reply_text(
            f"🖼 <b>{sc('imagine')}</b>\n<code>/image your prompt</code>", parse_mode="HTML"
        )
    if text == "Help":
        from modules.help import help_cmd
        return await help_cmd(update, context)


def register(app):
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(menu_callback, pattern="^menu_"))
    app.add_handler(CallbackQueryHandler(start_from_callback, pattern="^home$"))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^(Menu|Imagine|Help)$"), reply_bar))
