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
from helpers.persona import LANGS, MODES, get_prefs, set_pref
from helpers.memory import get_memory

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
    return (getattr(bot, "username", None) or BOT_USERNAME or "JULIET_MUSUCBOT").lstrip("@")


def nav_kb(back_to=None):
    row = []
    if back_to:
        row.append(btn("◀️ ʙᴀᴄᴋ", callback_data=back_to, pe_name="home"))
    row.append(btn("🏠 ʜᴏᴍᴇ", callback_data="home", pe_name="crown"))
    return InlineKeyboardMarkup([row])


def home_kb(user_id=None, bot_username=None):
    uname = (bot_username or BOT_USERNAME or "JULIET_MUSUCBOT").lstrip("@")
    rows = [
        [
            btn("ᴄʜᴀᴛ", callback_data="ui_chat", pe_name="chat"),
            btn("ʜᴇʟᴘ", callback_data="ui_help", pe_name="help"),
        ],
        [
            btn("ᴍᴏᴏᴅ", callback_data="ui_mood", pe_name="mood"),
            btn("ʟᴀɴɢ", callback_data="ui_lang", pe_name="lang"),
        ],
        [
            btn("ɴᴇᴡ ᴄʜᴀᴛ", callback_data="ui_newchat", pe_name="spark"),
            btn("ᴘʀᴏғɪʟᴇ", callback_data="ui_profile", pe_name="user"),
        ],
        [
            btn("ᴄʜᴇᴄᴋɪɴ", callback_data="ui_checkin", pe_name="cal"),
            btn("ᴄʟᴏɴᴇ", callback_data="ui_clone", pe_name="clone"),
        ],
        [btn("ᴀᴅᴅ ᴛᴏ ɢʀᴏᴜᴘ", url=f"https://t.me/{uname}?startgroup=true", pe_name="add")],
        [
            btn("ᴜᴘᴅᴀᴛᴇѕ", url=SUPPORT_CHANNEL, pe_name="news"),
            btn("ᴏᴡɴᴇʀ", url=f"https://t.me/{OWNER_USER}", pe_name="owner"),
        ],
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
    rows.append([
        btn("◀️ ʙᴀᴄᴋ", callback_data="home", pe_name="home"),
        btn("🏠 ʜᴏᴍᴇ", callback_data="home", pe_name="crown"),
    ])
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
    rows.append([
        btn("◀️ ʙᴀᴄᴋ", callback_data="home", pe_name="home"),
        btn("🏠 ʜᴏᴍᴇ", callback_data="home", pe_name="crown"),
    ])
    return InlineKeyboardMarkup(rows)


def help_kb():
    return InlineKeyboardMarkup([
        [
            btn("ᴄʜᴀᴛ", callback_data="help_chat", pe_name="chat"),
            btn("ᴛᴏᴏʟѕ", callback_data="help_tools", pe_name="spark"),
        ],
        [
            btn("ᴏᴡɴᴇʀ", callback_data="help_owner", pe_name="crown"),
            btn("ᴄʟᴏɴᴇ", callback_data="ui_clone", pe_name="clone"),
        ],
        [
            btn("◀️ ʙᴀᴄᴋ", callback_data="ui_help", pe_name="home"),
            btn("🏠 ʜᴏᴍᴇ", callback_data="home", pe_name="crown"),
        ],
    ])


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
        f"🆭 {sc('mood')} · <code>{prefs['mode']}</code>\n"
        f"🌐 {sc('lang')} · <code>{prefs['lang']}</code>\n"
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
    await query.answer("Home")
    text = caption_home(query.from_user, context.bot, await _user_count())
    ok = await paint(query, text, home_kb(query.from_user.id, context.bot.username))
    if not ok and query.message:
        await send_home(query.message, query.from_user, context.bot)


def owner_card():
    from helpers.ui import OWNER_NAME
    text = (
        f"👑 <b>{sc('bot owner profile')}</b> ✨\n"
        f"{LINE}\n\n"
        f"✨ {sc('this intelligent ai bot is proudly crafted')}\n"
        f"{sc('owned and managed by')}\n\n"
        f"👤 <b><a href='https://t.me/{OWNER_USER}'>{OWNER_NAME}</a></b>\n"
        f"🔗 @{OWNER_USER}\n\n"
        f"🚀 {sc('a passionate developer')}\n"
        f"• {sc('smart automation')}\n"
        f"• {sc('secure systems')}\n"
        f"• {sc('smooth user experience')}\n\n"
        f"💡 {sc('vision')}\n"
        f"{sc('creating powerful reliable ai bots')}\n\n"
        f"👇 {sc('connect and stay updated')}"
    )
    kb = InlineKeyboardMarkup([
        [btn("◍ ᴏᴡɴᴇʀ ◍", url=f"https://t.me/{OWNER_USER}", pe_name="owner")],
        [btn("◍ ѕᴜᴘᴘᴏʀᴛ ᴄʜᴀɴɴᴇʟ ◍", url=SUPPORT_CHANNEL, pe_name="news")],
        [
            btn("◀️ ʙᴀᴄᴋ", callback_data="home", pe_name="home"),
            btn("🏠 ʜᴏᴍᴇ", callback_data="home", pe_name="crown"),
        ],
    ])
    return text, kb


def _screen(key, user, bot):
    uname = _uname(bot)
    prefs = get_prefs(user.id)
    if key == "ui_chat":
        return (
            f"💬 <b>{sc('live chat')}</b>\n{LINE}\n\n"
            f"{sc('neeche type karo')}\n"
            f"{sc('mood')} · <code>{prefs['mode']}</code>\n"
            f"{sc('lang')} · <code>{prefs['lang']}</code>",
            nav_kb("home"),
        )
    if key in ("ui_help", "help_home"):
        return (
            f"📖 <b>{sc('help menu')}</b>\n{LINE}\n\n"
            f"{sc('i am')} <b>@{uname}</b>\n"
            f"{sc('your personal ai companion')}\n\n"
            f"💬 {sc('chat')} — {sc('type anything')}\n"
            f"🆭 {sc('mood')} — gf / bf / bestie / waifu / pro\n"
            f"🌐 {sc('lang')} — hindi english hinglish +\n"
            f"📅 {sc('checkin')} — {sc('daily streak')}\n"
            f"🤖 {sc('clone')} — /clone TOKEN\n"
            f"✨ {sc('new chat')} — {sc('reset memory')}\n\n"
            f"{sc('groups me reply ya')} @{uname}",
            help_kb(),
        )
    if key == "help_chat":
        return (
            f"💬 <b>{sc('chat guide')}</b>\n{LINE}\n\n"
            f"• {sc('just type')}\n"
            f"• {sc('voice note bhejo')}\n"
            f"• <code>yaad rakh city: Patna</code>\n"
            f"• /newchat — {sc('fresh start')}",
            help_kb(),
        )
    if key == "help_tools":
        return (
            f"✨ <b>{sc('tools')}</b>\n{LINE}\n\n"
            f"/start — {sc('home')}\n"
            f"/help — {sc('this menu')}\n"
            f"/newchat — {sc('reset')}\n"
            f"/checkin — {sc('streak')}\n"
            f"/clone — {sc('twin bot')}\n"
            f"/ping — {sc('speed')}\n"
            f"/profile — {sc('your vibe')}",
            help_kb(),
        )
    if key == "help_owner":
        return (
            f"👑 <b>{sc('owner')}</b>\n{LINE}\n\n"
            f"@{OWNER_USER}\n"
            f"/stats  /broadcast\n"
            f"/heal  /restart",
            help_kb(),
        )
    if key == "ui_mood":
        return (
            f"🆭 <b>{sc('choose mood')}</b>\n{LINE}\n\n"
            f"{sc('now')} · <code>{prefs['mode']}</code>\n"
            f"{sc('tap one then chat')}",
            mood_kb(prefs["mode"]),
        )
    if key == "ui_lang":
        return (
            f"🌐 <b>{sc('choose language')}</b>\n{LINE}\n\n"
            f"{sc('now')} · <code>{prefs['lang']}</code>\n"
            f"{sc('tap one then chat')}",
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
            f"{mem_lines}",
            nav_kb("home"),
        )
    if key == "ui_clone":
        return (
            f"🤖 <b>{sc('clone')}</b>\n{LINE}\n\n"
            "<code>/clone TOKEN</code>\n"
            "<code>/myclones</code>",
            nav_kb("home"),
        )
    if key == "ui_owner":
        return owner_card()
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
        packed = _screen("ui_mood", user, context.bot)
        await paint(query, packed[0], packed[1])
        return
    if data.startswith("langset_"):
        lang = data.split("_", 1)[1]
        if lang in LANGS:
            set_pref(user.id, lang=lang)
            chat_logs.delete_many({"user_id": user.id, "chat_id": query.message.chat_id, "role": "assistant"})
            await query.answer(f"Lang · {lang}")
        else:
            await query.answer()
        packed = _screen("ui_lang", user, context.bot)
        await paint(query, packed[0], packed[1])
        return

    await query.answer()
    if data == "ui_newchat":
        chat_logs.delete_many({"user_id": user.id, "chat_id": query.message.chat_id})
        await paint(
            query,
            f"✨ <b>{sc('new chat')}</b>\n{LINE}\n\n{sc('purani baat reset ho gayi')}",
            nav_kb("home"),
        )
        return
    if data == "ui_checkin":
        from modules.checkin import do_checkin_text
        try:
            body = await do_checkin_text(user)
        except Exception:
            body = sc("checkin done")
        await paint(query, f"📅 <b>{sc('check in')}</b>\n{LINE}\n\n{body}", nav_kb("home"))
        return
    packed = _screen(data, user, context.bot)
    if packed:
        await paint(query, packed[0], packed[1])


def register(app):
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(start_from_callback, pattern="^home$"))
    app.add_handler(CallbackQueryHandler(ui_callback, pattern="^(ui_|mood_|langset_|help_)"))
