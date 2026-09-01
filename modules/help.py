from telegram.ext import CommandHandler

from modules.start import _screen


async def help_cmd(update, context):
    if not update.message:
        return
    packed = _screen("ui_help", update.effective_user, context.bot)
    if not packed:
        return
    text, kb, ents = packed
    try:
        await update.message.reply_text(
            text, entities=ents, reply_markup=kb, disable_web_page_preview=True
        )
    except Exception:
        await update.message.reply_text(text, reply_markup=kb, disable_web_page_preview=True)


def register(app):
    app.add_handler(CommandHandler("help", help_cmd))
