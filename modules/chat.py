import time
import asyncio
import random
from datetime import datetime

import pytz
from telegram.ext import MessageHandler, filters

from config import BOT_USERNAME, BOT_NICKNAMES, STICKERS
from helpers import (
    safe_ai_async,
    get_fallback_reply,
    get_memory,
    set_memory,
    is_bot_banned,
    users,
    chat_logs,
)
from helpers.persona import get_prefs, persona_prompt

try:
    from helpers.learning import save_learned_reply, get_learned_reply
except ImportError:
    def save_learned_reply(*args, **kwargs):
        pass

    def get_learned_reply(*args, **kwargs):
        return None

SKIP = {"Menu", "Imagine", "Help"}


def build_history(user_id, chat_id):
    rows = list(
        chat_logs.find({"user_id": user_id, "chat_id": chat_id}).sort("time", -1).limit(10)
    )
    rows.reverse()
    out = []
    for row in rows:
        role = row.get("role") if row.get("role") in ("user", "assistant") else "user"
        msg = (row.get("text") or "").strip()[:240]
        if msg:
            out.append({"role": role, "content": msg})
    return out


def _maybe_remember(user_id, text):
    lower = text.lower()
    if lower.startswith("/remember ") or lower.startswith("yaad rakh "):
        body = text.split(" ", 1)[-1]
        if ":" in body:
            key, val = body.split(":", 1)
        elif "=" in body:
            key, val = body.split("=", 1)
        else:
            key, val = "note", body
        set_memory(user_id, key, val)
        return True
    return False


async def chat(update, context):
    if not update.message or not update.message.text:
        return
    text = update.message.text.strip()
    if text in SKIP:
        return
    user = update.effective_user
    lower_text = text.lower()
    chat_id = update.effective_chat.id
    name = user.first_name or "Friend"
    if is_bot_banned(user.id):
        return
    if update.effective_chat.type != "private":
        mentioned = "@%s" % BOT_USERNAME.lower() in lower_text
        nickname_called = any(nick in lower_text for nick in BOT_NICKNAMES)
        replied_to_bot = (
            update.message.reply_to_message
            and update.message.reply_to_message.from_user
            and update.message.reply_to_message.from_user.is_bot
        )
        if not mentioned and not nickname_called and not replied_to_bot:
            return
    users.update_one(
        {"user_id": user.id},
        {"$set": {"first_name": user.first_name, "username": user.username, "last_seen": time.time()},
         "$inc": {"xp": 1}},
        upsert=True,
    )
    if _maybe_remember(user.id, text):
        await update.message.reply_text("Theek, yaad rakh liya.")
        return
    try:
        if (
            update.message.reply_to_message
            and update.message.reply_to_message.from_user
            and update.message.reply_to_message.from_user.is_bot
        ):
            original = update.message.reply_to_message.text or ""
            if original and text:
                save_learned_reply(original, text, user.id)
    except Exception as e:
        print("Learning save error:", e)
    chat_logs.insert_one({
        "user_id": user.id,
        "chat_id": chat_id,
        "chat_type": update.effective_chat.type,
        "role": "user",
        "text": text[:500],
        "time": time.time(),
    })
    if "joke" in lower_text or "funny" in lower_text:
        style = "Short Hinglish joke."
    elif "shayari" in lower_text:
        style = "Chhoti Hindi shayari, 4 line."
    elif any(w in lower_text for w in ("roleplay", "rp ", "scene")):
        style = "Stay in the scene the user started."
    else:
        style = "Normal baat."
    prefs = get_prefs(user.id)
    messages = [{"role": "system", "content": persona_prompt(name, get_memory(user.id), prefs)}]
    messages.extend(build_history(user.id, chat_id))
    messages.append({"role": "user", "content": "%s\n\n%s" % (style, text)})
    reply = None
    try:
        learned = get_learned_reply(text)
        if learned and random.random() < 0.08:
            reply = learned
    except Exception:
        pass
    if not reply:
        reply = await safe_ai_async(messages)
    if not reply:
        reply = get_fallback_reply(user.id, text, name)
    reply = reply.strip()[:3500]
    await context.bot.send_chat_action(chat_id, "typing")
    await asyncio.sleep(0.2)
    await update.message.reply_text(reply, reply_to_message_id=update.message.message_id)
    try:
        sticker = None
        if any(w in lower_text for w in ["love", "pyar", "miss"]):
            sticker = STICKERS.get("love")
        elif any(w in lower_text for w in ["haha", "lol", "joke"]):
            sticker = STICKERS.get("laugh")
        elif any(w in lower_text for w in ["hi", "hello", "hey"]):
            sticker = STICKERS.get("hi")
        if sticker:
            await context.bot.send_sticker(chat_id=chat_id, sticker=sticker)
    except Exception as e:
        print("Sticker error:", e)
    chat_logs.insert_one({
        "user_id": user.id,
        "chat_id": chat_id,
        "chat_type": update.effective_chat.type,
        "role": "assistant",
        "text": reply[:500],
        "time": time.time(),
    })


def register(app):
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
