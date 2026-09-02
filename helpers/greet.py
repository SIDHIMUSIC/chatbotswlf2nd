from datetime import datetime

import pytz

from helpers.database import users
from config import STICKERS

IST = pytz.timezone("Asia/Kolkata")

FEST = {
    "01-01": "Happy New Year",
    "01-14": "Makar Sankranti / Pongal",
    "01-26": "Happy Republic Day",
    "02-14": "Happy Valentine's Day",
    "03-04": "Happy Holi",
    "03-08": "Happy Women's Day",
    "08-15": "Happy Independence Day",
    "08-18": "Happy Raksha Bandhan",
    "09-05": "Happy Teachers Day",
    "10-02": "Happy Gandhi Jayanti",
    "12-25": "Merry Christmas",
    "12-31": "Happy New Year Eve",
    "2026-09-02": "Happy Onam",
    "2026-09-04": "Happy Janmashtami",
    "2026-09-14": "Ganpati Bappa Morya",
    "2026-09-25": "Ganesh Visarjan",
    "2026-10-20": "Happy Dussehra",
    "2026-10-29": "Happy Karwa Chauth",
    "2026-11-08": "Happy Diwali",
    "2026-11-09": "Happy Govardhan Puja",
    "2026-11-10": "Happy Bhai Dooj",
    "2026-11-15": "Happy Chhath Puja",
    "2026-11-24": "Happy Guru Nanak Jayanti",
    "2027-01-14": "Makar Sankranti / Pongal",
    "2027-01-26": "Happy Republic Day",
    "2027-03-10": "Eid Mubarak",
    "2027-03-22": "Happy Holi",
    "2027-08-15": "Happy Independence Day",
    "2027-08-16": "Happy Raksha Bandhan",
    "2027-08-25": "Happy Janmashtami",
    "2027-10-09": "Happy Dussehra",
    "2027-10-29": "Happy Diwali",
    "2027-12-25": "Merry Christmas",
}


def _today():
    return datetime.now(IST)


def festival_line(now=None):
    now = now or _today()
    key_full = now.strftime("%Y-%m-%d")
    key_md = now.strftime("%m-%d")
    return FEST.get(key_full) or FEST.get(key_md)


def _already(uid, cid, day):
    doc = users.find_one({"user_id": uid}) or {}
    marks = doc.get("greet_days") or {}
    return marks.get(str(cid)) == day


def _mark(uid, cid, day):
    users.update_one(
        {"user_id": uid},
        {"$set": {f"greet_days.{cid}": day}},
        upsert=True,
    )


def build_wish(name, now=None):
    now = now or _today()
    fest = festival_line(now)
    hour = now.hour
    bits = []
    if 5 <= hour < 12:
        bits.append(f"Good morning {name}")
    if fest:
        bits.append(fest)
    if not bits:
        return ""
    return " · ".join(bits)


async def maybe_greet(message, user, chat_id):
    now = _today()
    day = now.strftime("%Y-%m-%d")
    uid = user.id
    if _already(uid, chat_id, day):
        return False
    name = user.first_name or "friend"
    text = build_wish(name, now)
    if not text:
        return False
    _mark(uid, chat_id, day)
    try:
        await message.reply_text(text)
    except Exception:
        return False
    sid = STICKERS.get("hi") or STICKERS.get("s1")
    if sid and (festival_line(now) or now.hour < 12):
        try:
            await message.reply_sticker(sid)
        except Exception:
            pass
    return True
