from telegram.ext import CommandHandler, CallbackQueryHandler

from helpers.database import chat_logs
from helpers.persona import get_prefs
from helpers.style import sc
from modules.start import lang_kb, mood_kb
from helpers.panel import paint
from helpers.ui import LINE


async def mode_cmd_send(message, user_id):
    prefs = get_prefs(user_id)
    await message.reply_text(
        f"🆭 <b>{sc('choose mood')}</b>\n{LINE}\n\n"
        f"{sc('now')} · <code>{prefs['mode']}</code>",
        parse_mode="HTML",
        reply_markup=mood_kb(prefs["mode"]),
    )


async def newchat_cmd(update, context):
    uid = update.effective_user.id
    cid = update.effective_chat.id
    chat_logs.delete_many({"user_id": uid, "chat_id": cid})
    await update.message.reply_text(f"✨ {sc('new chat unlocked')}\n{sc('purani baat reset ho gayi')}")


async def profile_cmd(update, context):
    from modules.start import _screen
    text, kb = _screen("ui_profile", update.effective_user, context.bot)
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=kb)


async def mode_cmd(update, context):
    await mode_cmd_send(update.message, update.effective_user.id)


async def lang_cmd(update, context):
    prefs = get_prefs(update.effective_user.id)
    await update.message.reply_text(
        f"🌐 <b>{sc('choose language')}</b>\n{LINE}\n\n"
        f"{sc('now')} · <code>{prefs['lang']}</code>",
        parse_mode="HTML",
        reply_markup=lang_kb(prefs["lang"]),
    )


async def mode_callback(update, context):
    query = update.callback_query
    await query.answer()
    from modules.start import ui_callback
    return await ui_callback(update, context)


async def imagine_cmd(update, context):
    from modules.image import image_cmd
    return await image_cmd(update, context)


def register(app):
    app.add_handler(CommandHandler("newchat", newchat_cmd))
    app.add_handler(CommandHandler("reset", newchat_cmd))
    app.add_handler(CommandHandler("profile", profile_cmd))
    app.add_handler(CommandHandler("mode", mode_cmd))
    app.add_handler(CommandHandler("mood", mode_cmd))
    app.add_handler(CommandHandler("lang", lang_cmd))
    app.add_handler(CommandHandler("language", lang_cmd))
    app.add_handler(CommandHandler("imagine", imagine_cmd))
