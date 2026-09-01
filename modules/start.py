import random
from datetime import datetime

import pytz
from telegram import InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler

from config import START_IMAGES, SUPPORT_CHANNEL, BOT_USERNAME
from helpers.decorators import is_owner
from helpers.style import sc
from helpers.database import users, chat_logs
from helpers.ui import LINE, OWNER_USER, btn
from helpers.panel import paint
from helpers.persona import MODES, get_prefs, set_pref
from helpers.memory import get_memory

IST = pytz.timezone("Asia/Kolkata")


def _uname(bot):
    return (getattr(bot, "username", None) or BOT_USERNAME or "JULIET_MUSUCBOT").lstrip("@")


def home_kb(user_id=None, bot_username=None):
    uname = (bot_username or BOT_USERNAME or "JULIET_MUSUCBOT").lstrip("@")
    rows = [
        [
            btn("💬  ᴄʜᴀᴛ", callback_data="ui_chat"),
            btn("📖  ʜᴇʟᴘ", callback_data="ui_help"),
        ],
        [
            btn("🆭  ᴍᴏᴏᴅ", callback_data="ui_mood"),
            btn("🌐  ʟᴀɴɢ", callback_data="ui_lang"),
        ],
        [
            btn("✨  ɴᴇᴡ ᴄʜᴀᴛ", callback_data="ui_newchat"),
            btn("👤  ᴘʀᴏғɪʟᴇ", callback_data="ui_profile"),
        ],
        [
            btn("📅  ᴄʜᴇᴄᴋɪɴ", callback_data="ui_checkin"),
            btn("🤖  ᴄʟᴏɴᴇ", callback_data="ui_clone"),
        ],
        [btn("➕  ᴀᴅᴅ ᴛᴏ ɢʀᴏᴜᴘ", url=f"https://t.me/{uname}?startgroup=true")],
        [
            btn("📣  ᴜᴘᴅᴀᴛᴇѕ", url=SUPPORT_CHANNEL),
            btn("👑  ᴏᴡɴᴇʀ", url=f"https://t.me/{OWNER_USER}"),
        ],
    ]
    if user_id and is_owner(user_id):
        rows.append([btn("⚙️  ᴄᴏɴѕᴏʟᴇ", callback_data="ui_owner")])
    return InlineKeyboardMarkup(rows)


def back_kb():
    return InlineKeyboardMarkup([[btn("◀️  ʜᴏᴍᴇ", callback_data="home")]])


def mood_kb(cur="bestie"):
    labels = [
        ("bestie", "💞 ʙᴇѕᴛɪᴇ"),
        ("gf", "💗 ɢғ ᴠɪʙᴇ"),
        ("bf", "💙 ʙғ ᴠɪʙᴇ"),
        ("waifu", "✨ ᴡᴀɪғᴜ"),
        ("pro", "💪 ᴘʀᴏ ᴀɪ"),
    ]
    rows = []
    row = []
    for key, label in labels:
        mark = "• " if key == cur else ""
        row.append(btn(f"{mark}{label}", callback_data=f"mood_{key}"))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([btn("◀️  ʜᴏᴍᴇ", callback_data="home")])
    return InlineKeyboardMarkup(rows)


def lang_kb(cur="hinglish"):
    items = [
        ("hinglish", "🇮🇳 ʜɪɴɢʟɪѕʜ"),
        ("hi", "🇮🇳 ʜɪɴᴅɪ"),
        ("en", "🇬🇧 ᴇɴɢʟɪѕʜ"),
    ]
    row = []
    for key, label in items:
        mark = "• " if key == cur else ""
        row.append(btn(f"{mark}{label}", callback_data=f"langset_{key}"))
    return InlineKeyboardMarkup([row, [btn("◀️  ʜᴏᴍᴇ", callback_data="home")]])


def caption_home(user, bot, extra_users=None):
    name = user.first_name or "✦"
    uname = _uname(bot)
    clock = datetime.now(IST).strftime("%I:%M %p")
    count = extra_users if extra_users not in (None, "-") else "—"
    prefs = get_prefs(user.id)
    return (
        f"✦ <b>{sc('hey')} {name}</b>\n"
        f"✦ {sc('i am')} <b>@{uname}</b>\n"
        f"{sc('your personal ai companion')}\n\n"
        f"{LINE}\n"
        f"{sc('mood')} · <code>{prefs['mode']}</code>   {sc('lang')} · <code>{prefs['lang']}</code>\n"
        f"{sc('always online for late night talks')}\n"
        f"{LINE}\n\n"
        f"🟢 {sc('online')}    🕒 {clock}    👤 {count}\n\n"
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
    text = caption_home(user, bot, await _user_count())
    kb = home_kb(user.id, bot.username)
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
    text = caption_home(query.from_user, context.bot, await _user_count())
    await paint(query, text, home_kb(query.from_user.id, context.bot.username))


def _screen(key, user, bot):
    uname = _uname(bot)
    prefs = get_prefs(user.id)
    if key == "ui_chat":
        return (
            f"💬 <b>{sc('live chat')}</b>\n{LINE}\n\n"
            f"{sc('just type anything below')}\n"
            f"{sc('or send a voice note')}\n\n"
            "<code>yaad rakh city: Patna</code>",
            back_kb(),
        )
    if key == "ui_help":
        return (
            f"📖 <b>{sc('help menu')}</b>\n{LINE}\n\n"
            f"{sc('i am')} <b>@{uname}</b>\n\n"
            f"/start — {sc('home')}\n"
            f"/help — {sc('this menu')}\n"
            f"/newchat — {sc('reset memory')}\n"
            f"/mode — {sc('mood')}\n"
            f"/checkin — {sc('daily streak')}\n"
            f"/clone — {sc('twin bot')}\n"
            f"/ping — {sc('speed')}\n\n"
            f"{sc('groups me reply ya')} @{uname}",
            back_kb(),
        )
    if key == "ui_mood":
        return (
            f"🆭 <b>{sc('choose mood')}</b>\n{LINE}\n\n"
            f"{sc('now')} · <code>{prefs['mode']}</code>\n"
            f"{sc('tap a vibe below')}",
            mood_kb(prefs["mode"]),
        )
    if key == "ui_lang":
        return (
            f"🌐 <b>{sc('choose language')}</b>\n{LINE}\n\n"
            f"{sc('now')} · <code>{prefs['lang']}</code>",
            lang_kb(prefs["lang"]),
        )
    if key == "ui_profile":
        mem = get_memory(user.id)
        doc = users.find_one({"user_id": user.id}) or {}
        mem_lines = "\n".join(f"• {k}: {v}" for k, v in list(mem.items())[:6]) or sc("empty")
        return (
            f"👤 <b>{sc('profile')}</b>\n{LINE}\n\n"
            f"{sc('mood')} · <code>{prefs['mode']}</code>\n"
            f"{sc('lang')} · <code>{prefs['lang']}</code>\n"
            f"{sc('streak')} · <code>{doc.get('checkin_streak') or 0}</code>\n\n"
            f"{sc('memory')}\n{mem_lines}",
            back_kb(),
        )
    if key == "ui_clone":
        return (
            f"🤖 <b>{sc('clone bot')}</b>\n{LINE}\n\n"
            f"{sc('botfather se naya bot banao')}\n"
            "<code>/clone TOKEN</code>\n"
            "<code>/myclones</code>",
            back_kb(),
        )
    if key == "ui_owner":
        return (
            f"👑 <b>{sc('owner')}</b>\n{LINE}\n\n"
            "/stats  /broadcast\n"
            "/heal  /restart\n"
            "/models",
            back_kb(),
        )
    return None


async def ui_callback(update, context):
    query = update.callback_query
    await query.answer()
    data = query.data
    user = query.from_user
    bot = context.bot

    if data == "ui_newchat":
        chat_logs.delete_many({"user_id": user.id, "chat_id": query.message.chat_id})
        text = f"✨ <b>{sc('new chat')}</b>\n{LINE}\n\n{sc('purani baat reset ho gayi')}"
        await paint(query, text, back_kb())
        return

    if data == "ui_checkin":
        from modules.checkin import do_checkin_text
        try:
            body = await do_checkin_text(user)
        except Exception:
            body = sc("checkin done")
        await paint(query, f"📅 <b>{sc('check in')}</b>\n{LINE}\n\n{body}", back_kb())
        return

    if data.startswith("mood_"):
        mode = data.split("_", 1)[1]
        if mode in MODES:
            set_pref(user.id, mode=mode)
        data = "ui_mood"
    elif data.startswith("langset_"):
        set_pref(user.id, lang=data.split("_", 1)[1])
        data = "ui_lang"

    packed = _screen(data, user, bot)
    if packed:
        text, kb = packed
        await paint(query, text, kb)


def register(app):
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(start_from_callback, pattern="^home$"))
    app.add_handler(CallbackQueryHandler(ui_callback, pattern="^(ui_|mood_|langset_)"))
