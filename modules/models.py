from telegram.ext import CommandHandler
from helpers.catalog import refresh, snapshot
from helpers.decorators import is_owner


async def models_cmd(update, context):
    if not is_owner(update.effective_user.id):
        return await update.message.reply_text("Owner only.")
    try:
        refresh()
    except Exception:
        pass
    snap = snapshot()
    chat = snap.get("chat") or []
    img = snap.get("image") or []
    dead = snap.get("dead") or []
    best = snap.get("best") or {}
    text = (
        "⚡ <b>MODEL POOL</b>\n"
        f"Quality: <code>{snap.get('quality')}</code>\n"
        f"Sticky: <code>{best.get('nara') or '—'}</code>\n\n"
        f"Chat ({len(chat)}):\n<code>{', '.join(chat[:25])}</code>\n\n"
        f"Image ({len(img)}):\n<code>{', '.join(img[:12])}</code>\n\n"
        f"Cooldown: <code>{', '.join(dead) if dead else 'none'}</code>"
    )
    await update.message.reply_text(text[:3900], parse_mode="HTML")


async def refresh_cmd(update, context):
    if not is_owner(update.effective_user.id):
        return
    refresh(force=True)
    await update.message.reply_text("Pool refresh ho gayi.")


def register(app):
    app.add_handler(CommandHandler("models", models_cmd))
    app.add_handler(CommandHandler("refreshmodels", refresh_cmd))
