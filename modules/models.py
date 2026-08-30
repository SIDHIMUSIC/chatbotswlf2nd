from telegram.ext import CommandHandler

from helpers.catalog import refresh, snapshot
from helpers.decorators import is_owner


async def models_cmd(update, context):
    if not is_owner(update.effective_user.id):
        return await update.message.reply_text("Owner only.")
    snap = snapshot()
    chat = snap["chat"]
    img = snap["image"]
    dead = snap["dead"]
    text = (
        f"Nara quality: {snap['quality']}\n"
        f"Chat models ({len(chat)}):\n" + ", ".join(chat[:40]) +
        (" ..." if len(chat) > 40 else "") +
        f"\n\nImage models ({len(img)}):\n" + ", ".join(img[:20]) +
        f"\n\nCooldown: {', '.join(dead) if dead else 'none'}"
    )
    await update.message.reply_text(text[:4000])


async def refresh_cmd(update, context):
    if not is_owner(update.effective_user.id):
        return
    refresh(force=True)
    await update.message.reply_text("Model list refresh ho gayi.")


def register(app):
    app.add_handler(CommandHandler("models", models_cmd))
    app.add_handler(CommandHandler("refreshmodels", refresh_cmd))
