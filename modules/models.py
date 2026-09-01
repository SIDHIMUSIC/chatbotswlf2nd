from telegram.ext import CommandHandler
from helpers.catalog import snapshot
from helpers.decorators import is_owner


async def models_cmd(update, context):
    if not is_owner(update.effective_user.id):
        return await update.message.reply_text("Owner only.")
    snap = snapshot()
    chat = snap.get("chat") or []
    dead = snap.get("dead") or []
    best = snap.get("best") or {}
    text = (
        "⚡ <b>GROQ POOL</b>\n"
        f"Sticky: <code>{best.get('groq') or '—'}</code>\n\n"
        f"Chat: <code>{', '.join(chat)}</code>\n\n"
        f"Cooldown: <code>{', '.join(dead) if dead else 'none'}</code>"
    )
    await update.message.reply_text(text[:3900], parse_mode="HTML")


async def refresh_cmd(update, context):
    if not is_owner(update.effective_user.id):
        return
    await update.message.reply_text("Groq pool static hai — refresh ki zaroorat nahi.")


def register(app):
    app.add_handler(CommandHandler("models", models_cmd))
    app.add_handler(CommandHandler("refreshmodels", refresh_cmd))
