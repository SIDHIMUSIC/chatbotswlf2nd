from telegram.ext import CommandHandler

from helpers.database import chat_logs
from helpers.persona import get_prefs
from helpers.style import sc
from modules.start import lang_kb, mood_kb
from helpers.ui import LINE


async def newchat_cmd(update, context):
    if not update.message:
        return
    uid = update.effective_user.id
    cid = update.effective_chat.id
    chat_logs.delete_many({"user_id": uid, "chat_id": cid})
    await update.message.reply_text(f"✨ {sc('new chat unlocked')}\n{sc('purani baat reset ho gayi')}")


async def profile_cmd(update, context):
    if not update.message:
        return
    from modules.start import _screen
    packed = _screen("ui_profile", update.effective_user, context.bot)
    if not packed:
        return
    text, kb, ents = packed
    try:
        await update.message.reply_text(text, entities=ents, reply_markup=kb)
    except Exception:
        await update.message.reply_text(text, reply_markup=kb)


async def mode_cmd(update, context):
    if not update.message:
        return
    prefs = get_prefs(update.effective_user.id)
    await update.message.reply_text(
        f"🆭 {sc('choose mood')}\n{LINE}\n\n{sc('now')} · {prefs['mode']}",
        reply_markup=mood_kb(prefs["mode"]),
    )


async def lang_cmd(update, context):
    if not update.message:
        return
    prefs = get_prefs(update.effective_user.id)
    await update.message.reply_text(
        f"🌐 {sc('choose language')}\n{LINE}\n\n{sc('now')} · {prefs['lang']}",
        reply_markup=lang_kb(prefs["lang"]),
    )


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
