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
from helpers.rich import Rich
from helpers.persona import LANGS, MODES, get_prefs, set_pref

IST = pytz.timezone("Asia/Kolkata")

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
    "ur": "🇵🇦 ᴜʀᴅᴜ",
    "pa": "🇮🇳 ᴘᴜɴⱼᴀʙɪ",
    "bn": "🇧🇩 ʙᴇɴɢᴀʟɪ",
}


def _uname(bot):
    return (getattr(bot, "username", None) or BOT_USERNAME or "HARRY_HERUKOBOT").lstrip("@")


def nav_kb(back_to=None):
    row = []
    if back_to:
        row.append(btn("◀️ ʙᴀᴄᴋ", callback_data=back_to, pe_name="home"))
    row.append(btn("🏠 ʜᴏᴍᴇ", callback_data="home", pe_name="crown"))
    return InlineKeyboardMarkup([row])


def home_kb(user_id=None, bot_username=None):
    uname = (bot_username or BOT_USERNAME or "HARRY_HERUKOBOT").lstrip("@")
    rows = [
        [btn("ᴄʜᴀᴛ", callback_data="ui_chat", pe_name="chat"), btn("ʜᴇʟᴘ", callback_data="ui_help", pe_name="help")],
        [btn("ᴍᴏᴏᴅ", callback_data="ui_mood", pe_name="mood"), btn("ʟᴀɴɢ", callback_data="ui_lang", pe_name="lang")],
        [btn("ɴᴇᴡ ᴄʜᴀᴛ", callback_data="ui_newchat", pe_name="spark"), btn("ᴘʀᴏғɪʟᴇ", callback_data="ui_profile", pe_name="user")],
        [btn("ᴄʜᴇᴄᴋɪɴ", callback_data="ui_checkin", pe_name="cal"), btn("ᴄʟᴏɴᴇ", callback_data="ui_clone", pe_name="clone")],
        [btn("ᴀᴅᴅ ᴛᴏ ɢʀᴏᴜᴘ", url=f"https://t.me/{uname}?startgroup=true", pe_name="add")],
        [btn("ᴜᴘᴅᴀᴛᴇѕ", url=SUPPORT_CHANNEL, pe_name="news"), btn("ᴏᴡɴᴇʀ", url=f"https://t.me/{OWNER_USER}", pe_name="owner")],
    ]
    if user_id and is_owner(user_id):
        rows.append([btn("ᴄᴏɴѕᴏʟᴇ", callback_data="ui_owner", pe_name="crown")])
    return InlineKeyboardMarkup(rows)


def back_kb():
    return nav_kb()


def mood_kb(cur="bestie"):
    rows, row = [], []
    for key, label in MOOD_LABEL.items():
        mark = "• " if key == cur else ""
        row.append(btn(f"{mark}{label}", callback_data=f"mood_{key}", pe_name="mood"))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([btn("◀️ ʙᴀᴄᴋ", callback_data="home", pe_name="home"), btn("🏠 ʜᴏᴍᴇ", callback_data="home", pe_name="crown")])
    return InlineKeyboardMarkup(rows)


def lang_kb(cur="hinglish"):
    rows, row = [], []
    for key, label in LANG_LABEL.items():
        mark = "• " if key == cur else ""
        row.append(btn(f"{mark}{label}", callback_data=f"langset_{key}", pe_name="lang"))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([btn("◀️ ʙᴀᴄᴋ", callback_data="home", pe_name="home"), btn("🏠 ʜᴏᴍᴇ", callback_data="home", pe_name="crown")])
    return InlineKeyboardMarkup(rows)


def help_kb():
    return InlineKeyboardMarkup([
        [btn("ᴄʜᴀᴛ", callback_data="help_chat", pe_name="chat"), btn("ᴛᴏᴏʟѕ", callback_data="help_tools", pe_name="spark")],
        [btn("ᴏᴡɴᴇʀ", callback_data="help_owner", pe_name="crown"), btn("ᴄʟᴏɴᴇ", callback_data="ui_clone", pe_name="clone")],
        [btn("◀️ ʙᴀᴄᴋ", callback_data="ui_help", pe_name="home"), btn("🏠 ʜᴏᴍᴇ", callback_data="home", pe_name="star")],
    ])


def caption_home(user, bot, extra_users=None):
    name = user.first_name or "✦"
    uname = _uname(bot)
    clock = datetime.now(IST).strftime("%I:%M %p")
    count = extra_users if extra_users not in (None, "-") else "—"
    prefs = get_prefs(user.id)
    r = Rich()
    r.e("star", "✦").t(f"  {sc('hey')}  {name}  ").e("spark", "✨").t("\n")
    r.e("heart", "💞").t(f"  {sc('welcome to')}  @{uname}  ").e("fire", "🔥").t("\n\n")
    r.e("user", "🧠").t(f"  {sc('your personal ai companion')}\n\n")
    r.t(f"{LINE}\n")
    r.e("chat", "💬").t(f"  {sc('features')} : {sc('chat')} • {sc('voice')} • {sc('clone')} • {sc('groups')}\n")
    r.e("mood", "🆭").t(f"  {sc('mood')} · {prefs['mode']}     ")
    r.e("lang", "🌐").t(f"  {sc('lang')} · {prefs['lang']}\n")
    r.t(f"{LINE}\n")
    r.e("help", "📖").t(f"  {sc('tap help to see all commands')}\n\n")
    r.e("online", "🟢").t(f"  {sc('online')}    ")
    r.e("cal", "🕒").t(f"  {clock}    ")
    r.e("people", "👤").t(f"  {count}\n")
    r.e("crown", "✦").t(f"  {sc('powered by harry')}")
    return r.build()


async def _user_count():
    try:
        return users.estimated_document_count()
    except Exception:
        try:
            return users.count_documents({})
        except Exception:
            return None


def _chat_count(user_id):
    try:
        return chat_logs.count_documents({"user_id": user_id})
    except Exception:
        return 0


async def send_home(message, user, bot):
    text, ents = caption_home(user, bot, await _user_count())
    kb = home_kb(user.id, bot.username)
    photo = random.choice(START_IMAGES) if START_IMAGES else None
    if photo:
        try:
            return await message.reply_photo(photo=photo, caption=text, caption_entities=ents, reply_markup=kb)
        except Exception:
            try:
                return await message.reply_photo(photo=photo, caption=text, reply_markup=kb)
            except Exception:
                pass
    try:
        return await message.reply_text(text, entities=ents, reply_markup=kb, disable_web_page_preview=True)
    except Exception:
        return await message.reply_text(text, reply_markup=kb, disable_web_page_preview=True)


async def start(update, context):
    if not update.message:
        return
    await send_home(update.message, update.effective_user, context.bot)


async def start_from_callback(update, context):
    query = update.callback_query
    await query.answer("Home")
    text, ents = caption_home(query.from_user, context.bot, await _user_count())
    ok = await paint(query, text, home_kb(query.from_user.id, context.bot.username), ents)
    if not ok and query.message:
        await send_home(query.message, query.from_user, context.bot)


def owner_card():
    r = Rich()
    r.e("crown", "👑").t(f"  {sc('bot owner')}\n{LINE}\n\n")
    r.e("spark", "✨").t(f"  {sc('crafted and managed by')}\n")
    r.e("user", "👤").t("  Harry\n")
    r.e("star", "🔗").t(f"  @{OWNER_USER}\n\n")
    r.e("fire", "🚀").t(f"  {sc('developer')} • {sc('automation')} • {sc('ai bots')}\n")
    r.e("heart", "💡").t(f"  {sc('tap below to connect')}")
    kb = InlineKeyboardMarkup([
        [btn("◍ ᴏᴡɴᴇʀ ◍", url=f"https://t.me/{OWNER_USER}", pe_name="owner")],
        [btn("◍ ѕᴜᴘᴘᴏʀᴛ ◍", url=SUPPORT_CHANNEL, pe_name="news")],
        [btn("◀️ ʙᴀᴄᴋ", callback_data="home", pe_name="home"), btn("🏠 ʜᴏᴍᴇ", callback_data="home", pe_name="crown")],
    ])
    return r.build() + (kb,)


def pack(r, kb):
    text, ents = r.build()
    return text, kb, ents


def _screen(key, user, bot):
    uname = _uname(bot)
    prefs = get_prefs(user.id)
    if key == "ui_chat":
        r = Rich()
        r.e("chat", "💬").t(f"  {sc('live chat')}\n{LINE}\n\n")
        r.e("spark", "✨").t(f"  {sc('neeche type karo')}\n")
        r.e("mood", "🆭").t(f"  {sc('mood')} · {prefs['mode']}\n")
        r.e("lang", "🌐").t(f"  {sc('lang')} · {prefs['lang']}")
        return pack(r, nav_kb("home"))
    if key in ("ui_help", "help_home"):
        r = Rich()
        r.e("help", "📖").t(f"  {sc('help menu')}\n{LINE}\n\n")
        r.e("heart", "🧠").t(f"  {sc('welcome to')}  @{uname}\n\n")
        r.e("chat", "💬").t(f"  {sc('chat')} — {sc('type anything')}\n")
        r.e("mood", "🆭").t(f"  {sc('mood')} — gf / bf / bestie / waifu / pro\n")
        r.e("lang", "🌐").t(f"  {sc('lang')} — hindi • english • hinglish\n")
        r.e("cal", "📅").t(f"  {sc('checkin')} — {sc('daily streak')}\n")
        r.e("clone", "🤖").t(f"  {sc('clone')} — /clone TOKEN")
        return pack(r, help_kb())
    if key == "help_chat":
        r = Rich().e("chat", "💬").t(f"  {sc('chat guide')}\n{LINE}\n\n✨  {sc('just type')}\n🎙️  {sc('voice note bhejo')}")
        return pack(r, help_kb())
    if key == "help_tools":
        r = Rich().e("spark", "✨").t(f"  {sc('tools')}\n{LINE}\n\n/start   /help   /newchat\n/checkin   /clone   /ping   /profile")
        return pack(r, help_kb())
    if key == "help_owner":
        r = Rich().e("crown", "👑").t(f"  {sc('owner')}\n{LINE}\n\n🔗  @{OWNER_USER}\n/stats   /heal   /restart")
        return pack(r, help_kb())
    if key == "ui_mood":
        r = Rich().e("mood", "🆭").t(f"  {sc('choose mood')}\n{LINE}\n\n✨  {sc('now')} · {prefs['mode']}")
        return pack(r, mood_kb(prefs["mode"]))
    if key == "ui_lang":
        r = Rich().e("lang", "🌐").t(f"  {sc('choose language')}\n{LINE}\n\n✨  {sc('now')} · {prefs['lang']}")
        return pack(r, lang_kb(prefs["lang"]))
    if key == "ui_profile":
        doc = users.find_one({"user_id": user.id}) or {}
        chats = _chat_count(user.id)
        handle = f"@{user.username}" if user.username else "—"
        r = Rich()
        r.e("user", "👤").t(f"  {sc('profile')}\n{LINE}\n\n")
        r.e("star", "✦").t(f"  {user.first_name or '—'}\n")
        r.e("spark", "🔗").t(f"  {handle}\n")
        r.e("crown", "🆔").t(f"  {sc('id')}  ·  {user.id}\n")
        r.e("chat", "💬").t(f"  {sc('chats')}  ·  {chats}\n")
        r.e("mood", "🆭").t(f"  {sc('mood')}  ·  {prefs['mode']}\n")
        r.e("lang", "🌐").t(f"  {sc('lang')}  ·  {prefs['lang']}\n")
        r.e("cal", "🔥").t(f"  {sc('streak')}  ·  {doc.get('checkin_streak') or 0}")
        return pack(r, nav_kb("home"))
    if key == "ui_clone":
        r = Rich()
        r.e("clone", "🤖").t(f"  {sc('clone')}\n{LINE}\n\n")
        r.e("spark", "✨").t(f"  {sc('botfather se naya bot banao')}\n\n")
        r.t("➤  /clone TOKEN\n➤  /myclones")
        return pack(r, nav_kb("home"))
    if key == "ui_owner":
        text, ents, kb = owner_card()
        return text, kb, ents
    return None


async def ui_callback(update, context):
    query = update.callback_query
    user = query.from_user
    data = query.data

    if data.startswith("mood_"):
        mode = data.split("_", 1)[1]
        if mode in MODES:
            set_pref(user.id, mode=mode)
            await query.answer(f"Mood · {mode}")
        else:
            await query.answer()
        text, kb, ents = _screen("ui_mood", user, context.bot)
        await paint(query, text, kb, ents)
        return
    if data.startswith("langset_"):
        lang = data.split("_", 1)[1]
        if lang in LANGS:
            set_pref(user.id, lang=lang)
            chat_logs.delete_many({"user_id": user.id, "chat_id": query.message.chat_id, "role": "assistant"})
            await query.answer(f"Lang · {lang}")
        else:
            await query.answer()
        text, kb, ents = _screen("ui_lang", user, context.bot)
        await paint(query, text, kb, ents)
        return

    await query.answer()
    if data == "ui_newchat":
        chat_logs.delete_many({"user_id": user.id, "chat_id": query.message.chat_id})
        r = Rich().e("spark", "✨").t(f"  {sc('new chat')}\n{LINE}\n\n{sc('purani baat reset ho gayi')}")
        text, ents = r.build()
        await paint(query, text, nav_kb("home"), ents)
        return
    if data == "ui_checkin":
        from modules.checkin import do_checkin_text
        try:
            body = await do_checkin_text(user)
        except Exception:
            body = sc("checkin done")
        r = Rich().e("cal", "📅").t(f"  {sc('check in')}\n{LINE}\n\n{body}")
        text, ents = r.build()
        await paint(query, text, nav_kb("home"), ents)
        return
    packed = _screen(data, user, context.bot)
    if packed:
        text, kb, ents = packed
        await paint(query, text, kb, ents)


def register(app):
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(start_from_callback, pattern="^home$"))
    app.add_handler(CallbackQueryHandler(ui_callback, pattern="^(ui_|mood_|langset_|help_)"))
