import time
from datetime import datetime, timezone

from telegram.ext import CommandHandler

from helpers.database import users
from helpers.style import sc


def _today():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


async def do_checkin_text(user):
    today = _today()
    doc = users.find_one({"user_id": user.id}) or {}
    last = doc.get("checkin_day")
    streak = int(doc.get("checkin_streak") or 0)
    if last == today:
        return (
            f"✨  {sc('already checked in')}\n"
            f"🔥  {sc('streak')}  ·  {streak}"
        )
    streak = streak + 1 if last else 1
    users.update_one(
        {"user_id": user.id},
        {"$set": {"checkin_day": today, "checkin_streak": streak, "last_seen": time.time()}},
        upsert=True,
    )
    return (
        f"✅  {sc('checked in')}\n"
        f"🔥  {sc('streak')}  ·  {streak}"
    )


async def do_checkin(message, user):
    body = await do_checkin_text(user)
    await message.reply_text(f"📅  {sc('check in')}\n\n{body}")


async def checkin_cmd(update, context):
    if not update.message:
        return
    await do_checkin(update.message, update.effective_user)


def register(app):
    app.add_handler(CommandHandler("checkin", checkin_cmd))
