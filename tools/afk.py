import time
from telegram.ext import CommandHandler, MessageHandler, filters

from helpers.database import users
from helpers.botme import nicknames


def _set_afk(uid, reason):
    users.update_one(
        {"user_id": uid},
        {"$set": {"afk": True, "afk_reason": reason[:80], "afk_since": time.time()}},
        upsert=True,
    )


def _clear_afk(uid):
    users.update_one({"user_id": uid}, {"$set": {"afk": False, "afk_reason": ""}})


async def afk_cmd(update, context):
    if not update.message:
        return
    reason = " ".join(context.args).strip() or "AFK"
    _set_afk(update.effective_user.id, reason)
    await update.message.reply_text(f"AFK on · {reason}")


async def afk_watch(update, context):
    msg = update.message
    if not msg or not msg.text:
        return
    user = update.effective_user
    if not user:
        return
    text = msg.text.strip()
    low = text.lower()
    nicks = nicknames(context.bot)
    if low in {"afk", "/afk"} or any(low.startswith(n + " afk") for n in nicks) or low.endswith(" afk"):
        reason = text.split("afk", 1)[-1].strip() or "AFK"
        _set_afk(user.id, reason)
        try:
            await msg.reply_text(f"AFK on · {reason}")
        except Exception:
            pass
        return
    doc = users.find_one({"user_id": user.id}) or {}
    if doc.get("afk"):
        _clear_afk(user.id)
        try:
            await msg.reply_text("AFK off. Welcome back.")
        except Exception:
            pass
    if msg.reply_to_message and msg.reply_to_message.from_user:
        other = users.find_one({"user_id": msg.reply_to_message.from_user.id}) or {}
        if other.get("afk"):
            try:
                await msg.reply_text(
                    f"{msg.reply_to_message.from_user.first_name} AFK · {other.get('afk_reason') or 'AFK'}"
                )
            except Exception:
                pass


def register(app):
    app.add_handler(CommandHandler("afk", afk_cmd))
    app.add_handler(CommandHandler("back", lambda u, c: _back(u)))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, afk_watch), group=-1)


async def _back(update):
    if not update.message:
        return
    _clear_afk(update.effective_user.id)
    await update.message.reply_text("AFK off")
