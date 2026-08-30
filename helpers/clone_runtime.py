"""Start cloned bot tokens as live polling apps in this process."""
import os
import traceback
from telegram.ext import ApplicationBuilder

from helpers.clones import get_all_clones
from utils.auto_loader import load_modules, load_tools

MAX_CLONES = int(os.getenv("MAX_CLONES", "8"))
MAX_PER_USER = int(os.getenv("MAX_CLONES_PER_USER", "2"))
RUNNING = {}
UPDATES = [
    "message", "edited_message", "callback_query", "inline_query",
    "business_connection", "business_message", "edited_business_message",
    "deleted_business_messages",
]


def _wire(app):
    load_modules(app)
    load_tools(app)
    try:
        from HARRYCHATBOT import error_handler
        app.add_error_handler(error_handler)
    except Exception:
        pass


async def start_clone(token: str, bot_id=None):
    token = (token or "").strip()
    if not token:
        return False, "empty token"
    if bot_id and bot_id in RUNNING:
        return True, "already running"
    if len(RUNNING) >= MAX_CLONES:
        return False, f"limit {MAX_CLONES} live clones"
    try:
        app = ApplicationBuilder().token(token).concurrent_updates(True).build()
        _wire(app)
        await app.initialize()
        await app.start()
        await app.updater.start_polling(drop_pending_updates=True, allowed_updates=UPDATES)
        me = await app.bot.get_me()
        RUNNING[me.id] = app
        print(f"CLONE LIVE @{me.username} ({me.id})")
        return True, f"@{me.username}"
    except Exception as e:
        traceback.print_exc()
        return False, str(e)[:180]


async def stop_clone(bot_id: int):
    app = RUNNING.pop(int(bot_id), None)
    if not app:
        return False
    try:
        await app.updater.stop()
        await app.stop()
        await app.shutdown()
    except Exception as e:
        print("stop clone:", e)
    return True


async def start_saved_clones():
    started = []
    failed = []
    items = get_all_clones()[:MAX_CLONES]
    for item in items:
        ok, info = await start_clone(item.get("bot_token"), item.get("bot_id"))
        name = item.get("bot_username") or info
        if ok:
            started.append(str(name))
        else:
            failed.append(f"{name}: {info}")
    print("Clones started:", started, "failed:", failed)
    return started, failed


def running_usernames():
    out = []
    for bot_id, app in RUNNING.items():
        try:
            out.append(f"{bot_id}")
        except Exception:
            out.append(str(bot_id))
    return list(RUNNING.keys())
