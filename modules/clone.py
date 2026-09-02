import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler, CommandHandler

from config import LOG_GROUP_ID, OWNER_ID
from helpers.clones import (
    delete_clone,
    get_all_clones,
    get_clone,
    get_clone_by_token,
    get_user_clones,
    save_clone,
    set_approved,
)
from helpers.clone_runtime import (
    MAX_CLONES,
    MAX_PER_USER,
    RUNNING,
    start_clone,
    stop_clone,
)
from helpers.decorators import is_owner
from helpers.style import sc
from tools.broadcast import get_all_user_ids


async def _alert_owner(bot, user, info):
    mention = f'<a href="tg://user?id={user.id}">{user.first_name or user.id}</a>'
    uname = f"@{user.username}" if user.username else "—"
    text = (
        f"⚠️  <b>Clone request</b>\n\n"
        f"User {mention} ({uname})\n"
        f"ID <code>{user.id}</code>\n\n"
        f"Bot token de raha hai.\n"
        f"Clone @{info.get('username') or '—'}\n"
        f"bot id <code>{info.get('id')}</code>\n\n"
        f"Confirm ke baad hi live hoga."
    )
    kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Approve", callback_data=f"cloneok_{info['id']}"),
            InlineKeyboardButton("Deny", callback_data=f"clonedn_{info['id']}"),
        ]
    ])
    sent = False
    if LOG_GROUP_ID:
        try:
            await bot.send_message(
                LOG_GROUP_ID,
                text,
                parse_mode="HTML",
                reply_markup=kb,
            )
            sent = True
        except Exception as e:
            print("clone log group:", e)
    try:
        await bot.send_message(OWNER_ID, text, parse_mode="HTML", reply_markup=kb)
        sent = True
    except Exception as e:
        print("clone owner dm:", e)
    return sent


async def clone_command(update, context):
    if not update.message:
        return
    if not context.args:
        return await update.message.reply_text(
            f"{sc('clone bot')}\n\n"
            "@BotFather se token lo\n"
            "/clone TOKEN\n\n"
            "Owner confirm kare tab live.",
        )
    uid = update.effective_user.id
    if len(get_user_clones(uid)) >= MAX_PER_USER and not is_owner(uid):
        return await update.message.reply_text(f"Max {MAX_PER_USER} clones.")
    token = context.args[0].strip()
    try:
        data = requests.get(f"https://api.telegram.org/bot{token}/getMe", timeout=8).json()
    except Exception:
        return await update.message.reply_text("Token check fail.")
    if not data.get("ok"):
        return await update.message.reply_text("Invalid token.")
    info = data["result"]
    existing = get_clone_by_token(token) or get_clone(info["id"])
    if existing and existing.get("approved") and info["id"] in RUNNING:
        return await update.message.reply_text("Ye clone already live hai.")
    auto = is_owner(uid)
    save_clone(
        uid,
        token,
        info.get("username"),
        info["id"],
        info.get("first_name"),
        approved=auto,
    )
    if auto:
        ok, msg = await start_clone(token, info["id"])
        return await update.message.reply_text(
            f"Owner clone live: {ok} {msg}"
        )
    await _alert_owner(context.bot, update.effective_user, info)
    await update.message.reply_text(
        f"@{info.get('username')} save. Owner confirm karega tab open."
    )


async def clone_decide(update, context):
    q = update.callback_query
    if not is_owner(q.from_user.id):
        return await q.answer("Owner only", show_alert=True)
    data = q.data or ""
    try:
        bot_id = int(data.split("_", 1)[1])
    except Exception:
        return await q.answer()
    clone = get_clone(bot_id)
    if not clone:
        await q.answer("Clone nahi mila", show_alert=True)
        return
    if data.startswith("clonedn_"):
        await stop_clone(bot_id)
        delete_clone(bot_id)
        await q.answer("Denied")
        try:
            await q.edit_message_text(f"Denied @{clone.get('bot_username')}")
        except Exception:
            pass
        try:
            await context.bot.send_message(clone.get("owner_id"), "Clone request deny.")
        except Exception:
            pass
        return
    set_approved(bot_id, True)
    ok, msg = await start_clone(clone.get("bot_token"), bot_id)
    await q.answer("Approved")
    try:
        await q.edit_message_text(f"Approved @{clone.get('bot_username')} live={ok} {msg}")
    except Exception:
        pass
    try:
        await context.bot.send_message(
            clone.get("owner_id"),
            f"Clone approved. Open @{clone.get('bot_username')} /start",
        )
    except Exception:
        pass


async def my_clones(update, context):
    items = get_user_clones(update.effective_user.id)
    if not items:
        return await update.message.reply_text("Koi clone nahi. /clone TOKEN")
    lines = []
    for i, c in enumerate(items, 1):
        live = "ON" if c.get("bot_id") in RUNNING else "OFF"
        wait = "WAIT" if not c.get("approved") else live
        lines.append(f"{i}. @{c.get('bot_username')} [{wait}] id {c.get('bot_id')}")
    await update.message.reply_text("Clones\n" + "\n".join(lines))


async def all_clones(update, context):
    if not is_owner(update.effective_user.id):
        return
    items = get_all_clones()
    if not items:
        return await update.message.reply_text("No clones")
    lines = [f"Saved {len(items)} | Live {len(RUNNING)}\n"]
    for c in items:
        st = "LIVE" if c.get("bot_id") in RUNNING else ("WAIT" if not c.get("approved") else "OFF")
        lines.append(
            f"@{c.get('bot_username')} {st}\n"
            f"id {c.get('bot_id')} user {c.get('owner_id')}"
        )
    await update.message.reply_text("\n".join(lines)[:3900])


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


async def clone_bc(update, context):
    if not is_owner(update.effective_user.id):
        return
    if not context.args and not (update.message and update.message.reply_to_message):
        return await update.message.reply_text("/clonebc hello  ya reply + /clonebc")
    text = " ".join(context.args) if context.args else None
    apps = list(RUNNING.items())
    if not apps:
        return await update.message.reply_text("Koi live clone nahi")
    ids = get_all_user_ids()
    status = await update.message.reply_text(f"Clone broadcast {len(apps)} bots, {len(ids)} users...")
    sent = fail = 0
    for _bid, app in apps:
        bot = app.bot
        for uid in ids:
            try:
                if text:
                    await bot.send_message(uid, text)
                elif update.message.reply_to_message:
                    await update.message.reply_to_message.copy(uid)
                sent += 1
            except Exception:
                fail += 1
    await status.edit_text(f"Clone BC done. sent {sent} fail {fail}")


def register(app):
    app.add_handler(CommandHandler("clone", clone_command))
    app.add_handler(CommandHandler("myclones", my_clones))
    app.add_handler(CommandHandler("clones", all_clones))
    app.add_handler(CommandHandler("delclone", del_clone))
    app.add_handler(CommandHandler("clonebc", clone_bc))
    app.add_handler(CallbackQueryHandler(clone_decide, pattern="^(cloneok_|clonedn_)"))
