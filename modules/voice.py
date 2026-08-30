import asyncio
import os
import tempfile

import requests
from telegram.ext import MessageHandler, filters

from config import NARA_API_KEY, NARA_BASE_URL, OPENROUTER_KEY, BOT_USERNAME, BOT_NICKNAMES
from helpers.ai import safe_ai_async
from helpers.persona import get_prefs, persona_prompt
from helpers.memory import get_memory
from helpers import is_bot_banned

WHISPER = ["whisper-1", "whisper-large-v3", "openai/whisper-large-v3"]


def _transcribe(path):
    headers = {}
    url = None
    if NARA_API_KEY:
        url = f"{NARA_BASE_URL}/audio/transcriptions"
        headers = {"Authorization": f"Bearer {NARA_API_KEY}"}
    elif OPENROUTER_KEY:
        url = "https://openrouter.ai/api/v1/audio/transcriptions"
        headers = {"Authorization": f"Bearer {OPENROUTER_KEY}"}
    else:
        return ""
    last = ""
    for model in WHISPER:
        try:
            with open(path, "rb") as fh:
                r = requests.post(
                    url,
                    headers=headers,
                    data={"model": model},
                    files={"file": ("voice.ogg", fh, "audio/ogg")},
                    timeout=20,
                )
            data = r.json() if r.content else {}
            text = (data.get("text") or "").strip()
            if text:
                return text
            last = str(data)[:120]
        except Exception as e:
            last = str(e)
            continue
    print("voice transcribe fail:", last)
    return ""


async def voice_chat(update, context):
    msg = update.message
    if not msg or not (msg.voice or msg.audio):
        return
    user = update.effective_user
    if is_bot_banned(user.id):
        return
    if update.effective_chat.type != "private":
        mentioned = False
        if msg.reply_to_message and msg.reply_to_message.from_user:
            mentioned = msg.reply_to_message.from_user.is_bot
        if not mentioned:
            return
    await context.bot.send_chat_action(update.effective_chat.id, "typing")
    media = msg.voice or msg.audio
    tg_file = await context.bot.get_file(media.file_id)
    path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp:
            path = tmp.name
        await tg_file.download_to_drive(path)
        spoken = await asyncio.to_thread(_transcribe, path)
    except Exception as e:
        print("voice download fail:", e)
        spoken = ""
    finally:
        if path:
            try:
                os.remove(path)
            except Exception:
                pass
    name = user.first_name or "Friend"
    prefs = get_prefs(user.id)
    if spoken:
        user_line = f"User ne voice note bheja. Transcript: {spoken}"
    else:
        user_line = "User ne voice note bheja, text nahi mila. Short warm reply do, text me bhi bolne ko bolo."
    messages = [
        {"role": "system", "content": persona_prompt(name, get_memory(user.id), prefs)},
        {"role": "user", "content": user_line},
    ]
    reply = await safe_ai_async(messages)
    if not reply:
        reply = f"{name}, voice aa gayi. Text me bhi likh do na."
    if spoken:
        reply = f"🎤 <i>{spoken[:180]}</i>\n\n{reply}"
    await msg.reply_text(reply, parse_mode="HTML")


def register(app):
    app.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, voice_chat))
