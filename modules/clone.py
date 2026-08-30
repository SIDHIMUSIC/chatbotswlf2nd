import requests
from telegram.ext import CommandHandler
from config import OWNER_ID
from helpers.clones import save_clone, get_user_clones, get_all_clones, delete_clone, get_clone, get_clone_by_token
from helpers.decorators import is_owner
from helpers.style import sc


async def clone_command(update, context):
    if not context.args:
        return await update.message.reply_text(
            f"🤖 <b>{sc('clone bot')}</b>\n\n"
            f"1. @BotFather pe /newbot\n"
            f"2. token yahan bhejo\n\n"
            "<code>/clone 123456:AAHxxxx</code>",
            parse_mode="HTML",
        )
    token = context.args[0].strip()
    try:
        data = requests.get(f"https://api.telegram.org/bot{token}/getMe", timeout=8).json()
    except Exception:
        return await update.message.reply_text("Token check fail. Phir try karo.")
    if not data.get("ok"):
        return await update.message.reply_text("Invalid token.")
    info = data["result"]
    if get_clone_by_token(token):
        return await update.message.reply_text("Yeh token pehle se cloned hai.")
    save_clone(update.effective_user.id, token, info.get("username"), info["id"], info.get("first_name"))
    await update.message.reply_text(
        f"✦ {sc('cloned')}\n@{info.get('username')}\n<code>{info['id']}</code>",
        parse_mode="HTML",
    )
    try:
        await context.bot.send_message(
            OWNER_ID,
            f"New clone by {update.effective_user.id}\n@{info.get('username')}",
        )
    except Exception:
        pass


async def my_clones(update, context):
    items = get_user_clones(update.effective_user.id)
    if not items:
        return await update.message.reply_text("Koi clone nahi. /clone TOKEN")
    lines = [f"{i}. @{c.get('bot_username')}" for i, c in enumerate(items, 1)]
    await update.message.reply_text("Clones\n" + "\n".join(lines))


async def all_clones(update, context):
    if not is_owner(update.effective_user.id):
        return
    items = get_all_clones()
    await update.message.reply_text("Total clones: %s" % len(items))


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
    delete_clone(bot_id)
    await update.message.reply_text("Clone delete.")


def register(app):
    app.add_handler(CommandHandler("clone", clone_command))
    app.add_handler(CommandHandler("myclones", my_clones))
    app.add_handler(CommandHandler("clones", all_clones))
    app.add_handler(CommandHandler("delclone", del_clone))
