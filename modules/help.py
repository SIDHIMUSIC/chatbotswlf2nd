from telegram.ext import CommandHandler, CallbackQueryHandler

from modules.start import _screen, back_kb, send_home
from helpers.panel import paint


async def help_cmd(update, context):
    if not update.message:
        return
    text, kb = _screen("ui_help", update.effective_user, context.bot)
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=kb, disable_web_page_preview=True)


async def help_callback(update, context):
    query = update.callback_query
    await query.answer()
    if query.data == "help_close":
        text, kb = _screen("ui_help", query.from_user, context.bot)
        await paint(query, text, kb)
        return
    if query.data == "help_home":
        from modules.start import caption_home, home_kb, _user_count
        text = caption_home(query.from_user, context.bot, await _user_count())
        await paint(query, text, home_kb(query.from_user.id, context.bot.username))
        return
    text, kb = _screen("ui_help", query.from_user, context.bot)
    await paint(query, text, kb)


def register(app):
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CallbackQueryHandler(help_callback, pattern="^help_"))
