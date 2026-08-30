from datetime import datetime

import pytz
from telegram.ext import CommandHandler

from helpers.database import users
from helpers.style import sc

IST = pytz.timezone("Asia/Kolkata")


def _today():
    return datetime.now(IST).strftime("%Y-%m-%d")


async def do_checkin(message, user):
    today = _today()
    doc = users.find_one({"user_id": user.id}) or {}
    last = doc.get("checkin_day")
    streak = int(doc.get("checkin_streak") or 0)
    total = int(doc.get("checkin_total") or 0)
    if last == today:
        return await message.reply_text(
            f"✦ {sc('already checked in')}\n"
            f"{sc('streak')}: <b>{streak}</b>  {sc('total')}: <b>{total}</b>",
            parse_mode="HTML",
        )
    from datetime import timedelta
    yday = (datetime.now(IST) - timedelta(days=1)).strftime("%Y-%m-%d")
    streak = streak + 1 if last == yday else 1
    total += 1
    users.update_one(
        {"user_id": user.id},
        {"$set": {
            "checkin_day": today,
            "checkin_streak": streak,
            "checkin_total": total,
            "first_name": user.first_name,
        }},
        upsert=True,
    )
    bonus = "  fire streak" if streak >= 7 else ""
    await message.reply_text(
        f"✦ <b>{sc('daily check in')}</b>\n\n"
        f"{sc('hey')} {user.first_name}\n"
        f"{sc('streak')}: <b>{streak}</b> din{bonus}\n"
        f"{sc('total')}: <b>{total}</b>\n\n"
        f"{sc('kal phir milte hain')}",
        parse_mode="HTML",
    )


async def checkin_cmd(update, context):
    await do_checkin(update.message, update.effective_user)


def register(app):
    app.add_handler(CommandHandler("checkin", checkin_cmd))
    app.add_handler(CommandHandler("daily", checkin_cmd))
