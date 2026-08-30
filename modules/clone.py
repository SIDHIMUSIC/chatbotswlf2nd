import requests
from telegram.ext import CommandHandler
from config import OWNER_ID
from helpers.clones import (
    save_clone, get_user_clones, get_all_clones,
    delete_clone, get_clone, get_clone_by_token,
)
from helpers.clone_runtime import (
    start_clone, stop_clone, MAX_CLONES, MAX_PER_USER, RUNNING,
)
from helpers.decorators import is_owner
from helpers.style import sc


async def clone_command(update, context):
    if not context.args:
        return await update.message.reply_text(
            f"🤖 <b>{sc('clone bot')}</b>\n\n"
            "1. @BotFather → /newbot\n"
            "2. token yahan bhejo\n\n"
            "<code>/clone 123456:AAHxxxx</code>\n\n"
            f"Limit: {MAX_PER_USER}/user, {MAX_CLONES} live", 
            parse_mode="HTML",
        )
    uid = update.effective_user.id
    if len(get_user_clones(uid)) >= MAX_PER_USER and not is_owner(uid):
        return await update.message.reply_text(f"Max {MAX_PER_USER} clones per user.")
    if len(RUNNING) >= MAX_CLONES:
        return await update.message.reply_text(f"Server limit {MAX_CLONES} live clones.")
    token = context.args[0].strip()
    try:
        data = requests.get(f"https://api.telegram.org/bot{token}/getMe", timeout=8).json()
    except Exception:
        return await update.message.reply_text("Token check fail.")
    if not data.get("ok"):
        return await update.message.reply_text("Invalid token.")
    info = data["result"]
    if get_clone_by_token(token):
        ok, msg = await start_clone(token, info["id"])
        return await update.message.reply_text(
            f"Already saved. Live: {ok} {msg}"
        )
    save_clone(uid, token, info.get("username"), info["id"], info.get("first_name"))
    ok, msg = await start_clone(token, info["id"])
    await update.message.reply_text(
        f"✦ saved @{info.get('username')}\n"
        f"{'LIVE now' if ok else 'saved but not live'}: {msg}\n\n"
        f"Open @{info.get('username')} and send /start",
        parse_mode="HTML",
    )
    try:
        await context.bot.send_message(OWNER_ID, f"Clone @{info.get('username')} live={ok}")
    except Exception:
        pass


async def my_clones(update, context):
    items = get_user_clones(update.effective_user.id)
    if not items:
        return await update.message.reply_text("Koi clone nahi. /clone TOKEN")
    lines = []
    for i, c in enumerate(items, 1):
        live = "ON" if c.get("bot_id") in RUNNING else "OFF"
        lines.append(f"{i}. @{c.get('bot_username')} [{live}]")
    await update.message.reply_text("Clones\n" + "\n".join(lines))


async def all_clones(update, context):
    if not is_owner(update.effective_user.id):
        return
    items = get_all_clones()
    await update.message.reply_text(f"Saved {len(items)} | Live {len(RUNNING)}")


async def del_clone(update, context):
    if not context.args:
        return await update.message.reply_text("/delclone bot_id")
    try:
        bot_id = int(context.args[0])
    except ValueError:
        return await update.message.reply_text("Invalid id")
    clone = get_clone(bot_id)
    if not clone:
        return await update.message.reply_text("Clone nahi mila.")
    uid = update.effective_user.id
    if uid != OWNER_ID and clone.get("owner_id") != uid:
        return await update.message.reply_text("Allowed nahi.")
    await stop_clone(bot_id)
    delete_clone(bot_id)
    await update.message.reply_text("Clone stopped + deleted.")


def register(app):
    app.add_handler(CommandHandler("clone", clone_command))
    app.add_handler(CommandHandler("myclones", my_clones))
    app.add_handler(CommandHandler("clones", all_clones))
    app.add_handler(CommandHandler("delclone", del_clone))
