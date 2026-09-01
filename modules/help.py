from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler
from helpers.decorators import is_owner

LINE = "<code>━━━━━━━━━━━━━━━━━━━━━━</code>"

PAGES = {
    "help_home": (
        "📚 <b>COMMAND GUIDE</b>\n"
        f"{LINE}\n\n"
        "Pick a section. Everything below works in private.\n"
        "Groups me bot ko reply ya naam se call karo."
    ),
    "help_basic": (
        "📌 <b>BASIC</b>\n"
        f"{LINE}\n\n"
        "/start — home panel\n"
        "/help — this guide\n"
        "/ping — speed check\n"
        "/id — user & chat id\n"
        "/owner — creator card"
    ),
    "help_chat": (
        "💬 <b>CHAT</b>\n"
        f"{LINE}\n\n"
        "Seedha message bhejo.\n"
        "<code>yaad rakh city: Patna</code>\n"
        "joke / shayari likho to mood change.\n\n"
        "AI Groq Llama pe chalti hai."
    ),
    "help_image": (
        "🖼 <b>IMAGE</b>\n"
        f"{LINE}\n\n"
        "Groq image nahi deta. Chat text only."
    ),
    "help_owner": (
        "👑 <b>OWNER</b>\n"
        f"{LINE}\n\n"
        "/stats /broadcast /models\n"
        "/heal /fix — cache + model cooldown clear\n"
        "/restart /reboot — process reboot\n"
        "Chat me: <code>sudhar</code> / <code>gadbad</code> / <code>restart</code>"
    ),
}


def nav(extra=None):
    rows = [
        [
            InlineKeyboardButton("Basic", callback_data="help_basic"),
            InlineKeyboardButton("Chat", callback_data="help_chat"),
        ],
        [
            InlineKeyboardButton("Image", callback_data="help_image"),
            InlineKeyboardButton("Owner", callback_data="help_owner"),
        ],
        [
            InlineKeyboardButton("➡ Home", callback_data="home"),
            InlineKeyboardButton("Close", callback_data="help_close"),
        ],
    ]
    if extra:
        rows.insert(0, extra)
    return InlineKeyboardMarkup(rows)


async def _show(query_or_msg, key, is_query=False):
    text = PAGES.get(key, PAGES["help_home"])
    kb = nav()
    if is_query:
        try:
            await query_or_msg.edit_message_text(text, parse_mode="HTML", reply_markup=kb, disable_web_page_preview=True)
            return
        except Exception:
            try:
                await query_or_msg.edit_message_caption(caption=text, parse_mode="HTML", reply_markup=kb)
                return
            except Exception:
                target = query_or_msg.message
    else:
        target = query_or_msg
    await target.reply_text(text, parse_mode="HTML", reply_markup=kb, disable_web_page_preview=True)


async def help_cmd(update, context):
    await _show(update.message, "help_home")


async def help_callback(update, context):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data == "help_close":
        try:
            await query.message.delete()
        except Exception:
            pass
        return
    if data == "help_owner" and not is_owner(query.from_user.id):
        return await query.answer("Owner only.", show_alert=True)
    await _show(query, data if data in PAGES else "help_home", is_query=True)


def register(app):
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CallbackQueryHandler(help_callback, pattern="^help_"))
