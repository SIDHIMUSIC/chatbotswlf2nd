from telegram.ext import CommandHandler

from modules.start import _screen, send_home


async def help_cmd(update, context):
    if not update.message:
        return
    text, kb = _screen("ui_help", update.effective_user, context.bot)
    try:
        await update.message.reply_photo(
            photo=update.message.reply_to_message.photo[-1].file_id
            if update.message.reply_to_message and update.message.reply_to_message.photo
            else None,
            caption=text,
            parse_mode="HTML",
            reply_markup=kb,
        )
        return
    except Exception:
        pass
    await update.message.reply_text(
        text, parse_mode="HTML", reply_markup=kb, disable_web_page_preview=True
    )


def register(app):
    app.add_handler(CommandHandler("help", help_cmd))
