from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler
from config import SUPPORT_CHANNEL


def _caption(user, bot_name):
    return (
        f"✨ <b>HEY {user.first_name}</b>\n\n"
        f"❖ <b>WELCOME TO {bot_name}</b>\n\n"
        "➤ Fast AI Chat\n"
        "➤ AI Image — /image\n"
        "➤ Memory System\n\n"
        "<b>Choose an option below 👇</b>"
    )


def _kb():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🤖 Chat", callback_data="menu_chat"),
            InlineKeyboardButton("🖼 AI Image", callback_data="menu_image"),
        ],
        [
            InlineKeyboardButton("📚 Help", callback_data="help_home"),
            InlineKeyboardButton("👑 Owner", callback_data="menu_owner"),
        ],
        [InlineKeyboardButton("❤️ Support", url=SUPPORT_CHANNEL)],
    ])


async def start(update, context):
    bot_name = context.bot.first_name or "Harry"
    await update.message.reply_text(
        _caption(update.effective_user, bot_name),
        parse_mode="HTML",
        reply_markup=_kb(),
        disable_web_page_preview=True,
    )


async def start_from_callback(update, context):
    query = update.callback_query
    await query.answer()
    bot_name = context.bot.first_name or "Harry"
    try:
        await query.edit_message_text(
            _caption(query.from_user, bot_name),
            parse_mode="HTML",
            reply_markup=_kb(),
            disable_web_page_preview=True,
        )
    except Exception:
        await query.message.reply_text(
            _caption(query.from_user, bot_name),
            parse_mode="HTML",
            reply_markup=_kb(),
            disable_web_page_preview=True,
        )


async def menu_callback(update, context):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data == "menu_chat":
        await query.message.reply_text("Bas message bhejo, main reply karunga.")
    elif data == "menu_image":
        await query.message.reply_text("Use: /image lord krishna digital art")
    elif data == "menu_owner":
        from modules.owner import owner_info
        await owner_info(update, context)


def register(app):
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(menu_callback, pattern="^menu_"))
    app.add_handler(CallbackQueryHandler(start_from_callback, pattern="^home$"))
