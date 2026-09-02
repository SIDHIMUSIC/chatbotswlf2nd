import time
from datetime import datetime, timedelta, timezone

from telegram import ChatPermissions
from telegram.ext import CommandHandler

from helpers.database import users
from helpers.decorators import is_owner


async def _is_admin(update, context):
    user = update.effective_user
    if is_owner(user.id):
        return True
    try:
        member = await context.bot.get_chat_member(update.effective_chat.id, user.id)
        return member.status in ("creator", "administrator")
    except Exception:
        return False


async def warn_cmd(update, context):
    if not update.message or update.effective_chat.type == "private":
        return
    if not await _is_admin(update, context):
        return await update.message.reply_text("Admin only")
    target = update.message.reply_to_message.from_user if update.message.reply_to_message else None
    if not target:
        return await update.message.reply_text("Reply karke /warn")
    if is_owner(target.id):
        return await update.message.reply_text("Owner ko warn nahi")
    doc = users.find_one({"user_id": target.id}) or {}
    warns = int(doc.get("warns") or 0) + 1
    users.update_one({"user_id": target.id}, {"$set": {"warns": warns}}, upsert=True)
    await update.message.reply_text(f"Warn {warns}/3 · {target.first_name}")
    if warns >= 3:
        try:
            until = datetime.now(timezone.utc) + timedelta(minutes=10)
            await context.bot.restrict_chat_member(
                update.effective_chat.id,
                target.id,
                ChatPermissions(can_send_messages=False),
                until_date=until,
            )
            users.update_one({"user_id": target.id}, {"$set": {"warns": 0}})
            await update.message.reply_text(f"3 warn · 10 min mute · {target.first_name}")
        except Exception:
            await update.message.reply_text("Mute fail. Bot ko admin + restrict right do.")


async def mute_cmd(update, context):
    if not update.message or update.effective_chat.type == "private":
        return
    if not await _is_admin(update, context):
        return await update.message.reply_text("Admin only")
    target = update.message.reply_to_message.from_user if update.message.reply_to_message else None
    if not target:
        return await update.message.reply_text("Reply karke /mute")
    mins = 10
    if context.args:
        try:
            mins = max(1, min(int(context.args[0]), 1440))
        except Exception:
            mins = 10
    try:
        until = datetime.now(timezone.utc) + timedelta(minutes=mins)
        await context.bot.restrict_chat_member(
            update.effective_chat.id,
            target.id,
            ChatPermissions(can_send_messages=False),
            until_date=until,
        )
        await update.message.reply_text(f"Muted {mins} min · {target.first_name}")
    except Exception:
        await update.message.reply_text("Mute fail. Bot ko admin + restrict right do.")


async def unmute_cmd(update, context):
    if not update.message or update.effective_chat.type == "private":
        return
    if not await _is_admin(update, context):
        return await update.message.reply_text("Admin only")
    target = update.message.reply_to_message.from_user if update.message.reply_to_message else None
    if not target:
        return await update.message.reply_text("Reply karke /unmute")
    try:
        await context.bot.restrict_chat_member(
            update.effective_chat.id,
            target.id,
            ChatPermissions(
                can_send_messages=True,
                can_send_audios=True,
                can_send_documents=True,
                can_send_photos=True,
                can_send_videos=True,
                can_send_voice_notes=True,
                can_send_other_messages=True,
            ),
        )
        await update.message.reply_text(f"Unmuted · {target.first_name}")
    except Exception:
        await update.message.reply_text("Unmute fail")


def register(app):
    app.add_handler(CommandHandler("warn", warn_cmd))
    app.add_handler(CommandHandler("mute", mute_cmd))
    app.add_handler(CommandHandler("unmute", unmute_cmd))
