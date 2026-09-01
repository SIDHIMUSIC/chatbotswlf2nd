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
MOODS = ["bestie", "gf", "bf", "waifu", "pro"]
LANGS = ["hinglish", "hi", "en"]
MOOD_LABEL = {
    "bestie": "💞 ʙᴇѕᴛɪᴇ",
    "gf": "💗 ɢғ",
    "bf": "💙 ʙғ",
    "waifu": "✨ ᴡᴀɪғᴜ",
    "pro": "💪 ᴘʀᴏ",
}
LANG_LABEL = {
    "hinglish": "🇮🇳 ʜɪɴɢʟɪѕʜ",
    "hi": "🇮🇳 ʜɪɴᴅɪ",
    "en": "🇬🇧 ᴇɴɢʟɪѕʜ",
}


def _uname(bot):
    return (getattr(bot, "username", None) or BOT_USERNAME or "JULIET_MUSUCBOT").lstrip("@")


def _cycle(cur, items):
    try:
        return items[(items.index(cur) + 1) % len(items)]
    except ValueError:
        return items[0]


def home_kb(user_id=None, bot_username=None):
    uname = (bot_username or BOT_USERNAME or "JULIET_MUSUCBOT").lstrip("@")
    prefs = get_prefs(user_id) if user_id else {"mode": "bestie", "lang": "hinglish"}
    mood_txt = MOOD_LABEL.get(prefs["mode"], "💞 ᴍᴏᴏᴅ")
    lang_txt = LANG_LABEL.get(prefs["lang"], "🌐 ʟᴀɴɢ")
    rows = [
        [
            btn("✨ ᴄʜᴀᴛ", callback_data="ui_chat", pe_name="chat"),
            btn("✨ ʜᴇʟᴘ", callback_data="ui_help", pe_name="help"),
        ],
        [
            btn(mood_txt, callback_data="cycle_mood", pe_name="mood"),
            btn(lang_txt, callback_data="cycle_lang", pe_name="lang"),
        ],
        [
            btn("✨ ɴᴇᴡ ᴄʜᴀᴛ", callback_data="ui_newchat", pe_name="spark"),
            btn("✨ ᴘʀᴏғɪʟᴇ", callback_data="ui_profile", pe_name="user"),
        ],
        [
            btn("✨ ᴄʜᴇᴄᴋɪɴ", callback_data="ui_checkin", pe_name="cal"),
            btn("✨ ᴄʟᴏɴᴇ", callback_data="ui_clone", pe_name="bot"),
        ],
        [btn("✨ ᴀᴅᴅ ᴛᴏ ɢʀᴏᴜᴘ", url=f"https://t.me/{uname}?startgroup=true", pe_name="add")],
        [
            btn("✨ ᴜᴘᴅᴀᴛᴇѕ", url=SUPPORT_CHANNEL, pe_name="news"),
            btn("✨ ᴏᴡɴᴇʀ", url=f"https://t.me/{OWNER_USER}", pe_name="owner"),
        ],
    ]
    if user_id and is_owner(user_id):
        rows.append([btn("✨ ᴄᴏɴѕᴏʟᴇ", callback_data="ui_owner", pe_name="crown")])
    return InlineKeyboardMarkup(rows)


def back_kb():
    return InlineKeyboardMarkup([[btn("✨ ʜᴏᴍᴇ", callback_data="home", pe_name="home")]])


def mood_kb(cur="bestie"):
    return home_kb()


def lang_kb(cur="hinglish"):
    return home_kb()


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
        f"{sc('mood')} · <code>{prefs['mode']}</code>    {sc('lang')} · <code>{prefs['lang']}</code>\n"
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


async def _show_home(query, context):
    text = caption_home(query.from_user, context.bot, await _user_count())
    await paint(query, text, home_kb(query.from_user.id, context.bot.username))


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
    await _show_home(query, context)


def _screen(key, user, bot):
    uname = _uname(bot)
    prefs = get_prefs(user.id)
    if key == "ui_chat":
        return (
            f"💬 <b>{sc('live chat')}</b>\n{LINE}\n\n"
            f"{sc('neeche type karo')}\n"
            f"{sc('mood')} · <code>{prefs['mode']}</code>\n"
            f"{sc('lang')} · <code>{prefs['lang']}</code>",
            back_kb(),
        )
    if key == "ui_help":
        return (
            f"📖 <b>{sc('help')}</b>\n{LINE}\n\n"
            f"{sc('i am')} <b>@{uname}</b>\n\n"
            f"/start  /help  /newchat\n"
            f"/checkin  /clone  /ping\n\n"
            f"{sc('mood lang buttons chat pe lagte hain')}",
            back_kb(),
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
            f"{mem_lines}",
            back_kb(),
        )
    if key == "ui_clone":
        return (
            f"🤖 <b>{sc('clone')}</b>\n{LINE}\n\n"
            "<code>/clone TOKEN</code>\n"
            "<code>/myclones</code>",
            back_kb(),
        )
    if key == "ui_owner":
        return (
            f"⚙️ <b>{sc('console')}</b>\n{LINE}\n\n"
            "/stats  /broadcast\n"
            "/heal  /restart\n"
            "/models",
            back_kb(),
        )
    return None


async def ui_callback(update, context):
    query = update.callback_query
    user = query.from_user
    data = query.data

    if data == "cycle_mood":
        prefs = get_prefs(user.id)
        nxt = _cycle(prefs["mode"], MOODS)
        set_pref(user.id, mode=nxt)
        await query.answer(f"Mood · {nxt}")
        await _show_home(query, context)
        return
    if data == "cycle_lang":
        prefs = get_prefs(user.id)
        nxt = _cycle(prefs["lang"], LANGS)
        set_pref(user.id, lang=nxt)
        await query.answer(f"Lang · {nxt}")
        await _show_home(query, context)
        return

    await query.answer()

    if data == "ui_newchat":
        chat_logs.delete_many({"user_id": user.id, "chat_id": query.message.chat_id})
        await paint(
            query,
            f"✨ <b>{sc('new chat')}</b>\n{LINE}\n\n{sc('purani baat reset ho gayi')}",
            back_kb(),
        )
        return
    if data == "ui_checkin":
        from modules.checkin import do_checkin_text
        try:
            body = await do_checkin_text(user)
        except Exception:
            body = sc("checkin done")
        await paint(query, f"📅 <b>{sc('check in')}</b>\n{LINE}\n\n{body}", back_kb())
        return

    packed = _screen(data, user, context.bot)
    if packed:
        text, kb = packed
        await paint(query, text, kb)


def register(app):
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(start_from_callback, pattern="^home$"))
    app.add_handler(CallbackQueryHandler(ui_callback, pattern="^(ui_|cycle_)"))
