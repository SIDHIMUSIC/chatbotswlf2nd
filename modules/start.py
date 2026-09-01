import random
from datetime import datetime

import pytz
from telegram import InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler

from config import START_IMAGES, SUPPORT_CHANNEL, BOT_USERNAME
from helpers.decorators import is_owner
from helpers.style import sc
from helpers.database import users
from helpers.ui import LINE, OWNER_USER, btn, pe

IST = pytz.timezone("Asia/Kolkata")


def _uname(bot):
    raw = (getattr(bot, "username", None) or BOT_USERNAME or "HARRY_HERUKOBOT").lstrip("@")
    return raw


def panel_kb(user_id=None, bot_username=None):
    uname = (bot_username or BOT_USERNAME or "HARRY_HERUKOBOT").lstrip("@")
    rows = [
        [
            btn("◍ ᴄʜᴀᴛ", callback_data="menu_chat", pe_name="chat"),
            btn("◍ ʜᴇʟᴘ", callback_data="help_home", pe_name="star"),
        ],
        [
            btn("◍ ʀᴏʟᴇᴘʟᴀʏ", callback_data="menu_role", pe_name="heart"),
            btn("◍ ᴄʜᴇᴄᴋ-ɪɴ", callback_data="menu_checkin", pe_name="fire"),
        ],
        [
            btn("◍ ᴄʟᴏɴᴇ", callback_data="menu_clone", pe_name="spark"),
            btn("◍ ᴍᴏᴅᴇ", callback_data="menu_mode", pe_name="star"),
        ],
        [btn("◍ ᴀᴅᴅ ᴛᴏ ɢᴛᴏᴜᴘ", url=f"https://t.me/{uname}?startgroup=true", pe_name="fire")],
        [
            btn("◍ ᴜᴘᴅᴀᴛᴇѕ", url=SUPPORT_CHANNEL, pe_name="support"),
            btn("◍ ᴏᴡɴᴇʀ", url=f"https://t.me/{OWNER_USER}", pe_name="owner"),
        ],
    ]
    if user_id and is_owner(user_id):
        rows.append([btn("◍ ᴄᴏɴѕᴏʟᴇ", callback_data="menu_owner", pe_name="crown")])
    return InlineKeyboardMarkup(rows)


def caption(user, bot, extra_users=None):
    name = user.first_name or "✦"
    uname = _uname(bot)
    clock = datetime.now(IST).strftime("%I:%M %p")
    count = extra_users if extra_users not in (None, "-") else "—"
    star = pe("star", "✦")
    return (
        f"{star} <b>{sc('hey')} {name}</b>\n"
        f"{star} {sc('i am')} <b>@{uname}</b>\n"
        f"{sc('your personal ai companion')}\n\n"
        f"{LINE}\n"
        f"{sc('always online for late night talks')}\n"
        f"{sc('chat  voice  checkin  clone  groups')}\n"
        f"{LINE}\n\n"
        f"🟢 {sc('status')}  {sc('online')}\n"
        f"🕒 {clock}    👤 {count}\n\n"
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


async def send_home(message, user, bot):
    text = caption(user, bot, await _user_count())
    kb = panel_kb(user.id, bot.username)
    photo = random.choice(START_IMAGES) if START_IMAGES else None
    if photo:
        try:
            return await message.reply_photo(photo=photo, caption=text, parse_mode="HTML", reply_markup=kb)
        except Exception:
            pass
    return await message.reply_text(text, parse_mode="HTML", reply_markup=kb, disable_web_page_preview=True)


async def start(update, context):
    if not update.message:
        return
    await send_home(update.message, update.effective_user, context.bot)


async def start_from_callback(update, context):
    query = update.callback_query
    await query.answer()
    text = caption(query.from_user, context.bot, await _user_count())
    kb = panel_kb(query.from_user.id, context.bot.username)
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
    back = InlineKeyboardMarkup([[btn("◍ ʜᴏᴍᴇ", callback_data="home", pe_name="home")]])
    if data == "menu_owner":
        from modules.owner import owner_info
        return await owner_info(update, context)
    if data == "menu_checkin":
        from modules.checkin import do_checkin
        return await do_checkin(query.message, query.from_user)
    if data == "menu_mode":
        from modules.extras import mode_cmd_send
        return await mode_cmd_send(query.message, query.from_user.id)
    uname = _uname(context.bot)
    pages = {
        "menu_chat": (
            f"{pe('chat', '💬')} <b>{sc('live chat')}</b>\n{LINE}\n\n"
            f"{sc('just type anything')}\n"
            f"{sc('or send a voice note')}\n\n"
            "<code>yaad rakh city: Patna</code>"
        ),
        "menu_role": (
            f"{pe('heart', '🆭')} <b>{sc('roleplay')}</b>\n{LINE}\n\n"
            f"{sc('start a scene in chat')}\n"
            f"{sc('or pick vibe from')} /mode"
        ),
        "menu_clone": (
            f"{pe('spark', '🤖')} <b>{sc('clone bot')}</b>\n{LINE}\n\n"
            f"{sc('botfather se naya bot banao')}\n"
            "<code>/clone TOKEN</code>\n"
            "<code>/myclones</code>"
        ),
        "menu_features": (
            f"{pe('star', 'ℹ️')} <b>{sc('about')} @{uname}</b>\n{LINE}\n\n"
            f"• {sc('late night talks')}\n"
            f"• {sc('voice  checkin  clone')}\n"
            f"• {sc('made by')} @{OWNER_USER}"
        ),
    }
    text = pages.get(data)
    if text:
        await query.message.reply_text(text, parse_mode="HTML", reply_markup=back)


def register(app):
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(menu_callback, pattern="^menu_"))
    app.add_handler(CallbackQueryHandler(start_from_callback, pattern="^home$"))
