import time
import asyncio
import random
import re

from telegram.ext import MessageHandler, filters

from config import STICKERS
from helpers import (
    safe_ai_async,
    get_fallback_reply,
    get_memory,
    set_memory,
    is_bot_banned,
    is_owner,
    users,
    chat_logs,
)
from helpers.persona import get_prefs, persona_prompt
from helpers.heal import can_restart, owner_intent, schedule_restart, soft_heal
from helpers.botme import nicknames, uname

try:
    from helpers.learning import save_learned_reply, get_learned_reply
except ImportError:
    def save_learned_reply(*args, **kwargs):
        pass

    def get_learned_reply(*args, **kwargs):
        return None

SKIP = {"Menu", "Imagine", "Help"}
LEAK = re.compile(
    r"(we have a conversation|we must respond|normal baat|system prompt|"
    r"instruction says|use nickname|no mention of model|yaadein:|"
    r"user ka naam|1 se 4 line|robotic mat|LANGUAGE=|MOOD=)",
    re.I,
)


def _clean(text: str) -> str:
    t = (text or "").strip()
    if not t or LEAK.search(t):
        return ""
    return t[:3500]


def build_history(user_id, chat_id):
    rows = list(
        chat_logs.find({"user_id": user_id, "chat_id": chat_id}).sort("time", -1).limit(6)
    )
    rows.reverse()
    out = []
    for row in rows:
        role = row.get("role") if row.get("role") in ("user", "assistant") else "user"
        msg = _clean((row.get("text") or "")[:180])
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
    bot_username = uname(context.bot).lower()
    if update.effective_chat.type != "private":
        mentioned = f"@{bot_username}" in lower_text if bot_username else False
        nickname_called = any(nick in lower_text for nick in nicknames(context.bot))
        replied_to_bot = (
            update.message.reply_to_message
            and update.message.reply_to_message.from_user
            and update.message.reply_to_message.from_user.id == context.bot.id
        )
        if not mentioned and not nickname_called and not replied_to_bot:
            return

    if is_owner(user.id):
        intent = owner_intent(text)
        if intent == "restart":
            if not can_restart():
                await update.message.reply_text("Abhi cooldown. 3 min baad restart.")
                return
            soft_heal()
            await update.message.reply_text("Theek. Restart le raha hoon.")
            schedule_restart(1.2)
            return
        if intent == "heal":
            cleared = soft_heal()
            await update.message.reply_text("Sudhar diya: " + (", ".join(cleared) or "ok"))
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
            and update.message.reply_to_message.from_user.id == context.bot.id
        ):
            original = update.message.reply_to_message.text or ""
            if original and text and not LEAK.search(original):
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
    prefs = get_prefs(user.id)
    messages = [{"role": "system", "content": persona_prompt(name, get_memory(user.id), prefs)}]
    messages.extend(build_history(user.id, chat_id))
    messages.append({"role": "user", "content": text[:500]})
    reply = None
    try:
        learned = get_learned_reply(text)
        if learned and random.random() < 0.05 and not LEAK.search(learned):
            reply = learned
    except Exception:
        pass
    if not reply:
        reply = _clean(await safe_ai_async(messages))
    if not reply:
        reply = get_fallback_reply(user.id, text, name)
    await context.bot.send_chat_action(chat_id, "typing")
    await asyncio.sleep(0.15)
    await update.message.reply_text(reply, reply_to_message_id=update.message.message_id)
    try:
        sticker = None
        if any(w in lower_text for w in ["love", "pyar", "miss"]):
            sticker = STICKERS.get("love")
        elif any(w in lower_text for w in ["haha", "lol", "joke"]):
            sticker = STICKERS.get("laugh")
        elif any(w in lower_text for w in ["hi", "hello", "hey", "hy"]):
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
