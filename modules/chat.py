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

try:
    from function import get_bot_extras
except ImportError:
    def get_bot_extras(name):
        return ""

try:
    from helpers.learning import save_learned_reply, get_learned_reply
except ImportError:
    def save_learned_reply(*args, **kwargs):
        pass

    def get_learned_reply(*args, **kwargs):
        return None


def _system_prompt(name, memory):
    mem = ""
    if memory:
        bits = ["- %s: %s" % (k, v) for k, v in list(memory.items())[:6]]
        mem = "\nYaadein:\n" + "\n".join(bits)
    extra = get_bot_extras(name) or ""
    return (
        "Tu Harry hai, Telegram pe close Hinglish dost.\n"
        "User ka naam: %s.\n"
        "1 se 4 line me natural reply de. Robotic mat ban.\n"
        "Har line pe emoji mat pel. AI/model/API ka naam mat le.\n"
        "Shayari/joke tabhi jab user maange.\n"
        "%s%s" % (name, extra, mem)
    )


def build_history(user_id, chat_id):
    rows = list(
        chat_logs.find({"user_id": user_id, "chat_id": chat_id}).sort("time", -1).limit(12)
    )
    rows.reverse()
    out = []
    for row in rows:
        role = row.get("role") if row.get("role") in ("user", "assistant") else "user"
        msg = (row.get("text") or "").strip()[:280]
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


async def chatgpt_typing(update, context, text):
    await context.bot.send_chat_action(update.effective_chat.id, "typing")
    await asyncio.sleep(0.25)
    await update.message.reply_text(text, reply_to_message_id=update.message.message_id)


async def chat(update, context):
    if not update.message or not update.message.text:
        return
    user = update.effective_user
    text = update.message.text.strip()
    lower_text = text.lower()
    chat_id = update.effective_chat.id
    name = user.first_name or "Friend"
    tz = pytz.timezone("Asia/Kolkata")
    now = datetime.now(tz)
    if "date" in lower_text and len(lower_text) < 20:
        await update.message.reply_text(
            "Aaj %s, %s hai." % (now.strftime("%d %B %Y"), now.strftime("%A"))
        )
        return
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
        {"$set": {"first_name": user.first_name, "username": user.username, "last_seen": time.time()}},
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
        style = "Ek short Hinglish joke sunao."
    elif "shayari" in lower_text:
        style = "Chhoti si Hindi shayari likho, 4-6 line."
    else:
        style = "Normal dosti wali baat kar."
    messages = [{"role": "system", "content": _system_prompt(name, get_memory(user.id))}]
    messages.extend(build_history(user.id, chat_id))
    messages.append({"role": "user", "content": "%s\n\n%s" % (style, text)})
    reply = None
    try:
        learned = get_learned_reply(text)
        if learned and random.random() < 0.12:
            reply = learned
    except Exception:
        pass
    if not reply:
        reply = await safe_ai_async(messages)
    if not reply or any(x in reply.lower() for x in ["dikkat aa", "ai busy", "try karo"]):
        reply = get_fallback_reply(user.id, text, name)
    reply = reply.strip()[:3500]
    await chatgpt_typing(update, context, reply)
    try:
        sticker_to_send = None
        if any(w in lower_text for w in ["love", "pyar", "miss", "dil"]):
            sticker_to_send = STICKERS.get("love")
        elif any(w in lower_text for w in ["haha", "lol", "haso", "funny", "joke"]):
            sticker_to_send = STICKERS.get("laugh")
        elif any(w in lower_text for w in ["cool", "mast", "fire", "op"]):
            sticker_to_send = STICKERS.get("cool")
        elif any(w in lower_text for w in ["sad", "dukhi", "rona", "cry"]):
            sticker_to_send = STICKERS.get("sad")
        elif any(w in lower_text for w in ["hi", "hello", "hey", "namaste"]):
            sticker_to_send = STICKERS.get("hi")
        elif any(w in lower_text for w in ["kiss", "chumma", "muah"]):
            sticker_to_send = STICKERS.get("kiss")
        if sticker_to_send:
            await context.bot.send_sticker(chat_id=chat_id, sticker=sticker_to_send)
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
