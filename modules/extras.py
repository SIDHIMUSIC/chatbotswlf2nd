from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler

from helpers.database import chat_logs, users
from helpers.memory import get_memory
from helpers.persona import MODES, get_prefs, set_pref
from helpers.style import sc


def mode_kb():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Bestie", callback_data="mode_bestie"),
            InlineKeyboardButton("GF vibe", callback_data="mode_gf"),
        ],
        [
            InlineKeyboardButton("BF vibe", callback_data="mode_bf"),
            InlineKeyboardButton("Waifu", callback_data="mode_waifu"),
        ],
        [
            InlineKeyboardButton("Pro AI", callback_data="mode_pro"),
        ],
        [
            InlineKeyboardButton("Hinglish", callback_data="lang_hinglish"),
            InlineKeyboardButton("Hindi", callback_data="lang_hi"),
            InlineKeyboardButton("English", callback_data="lang_en"),
        ],
        [InlineKeyboardButton("Home", callback_data="home")],
    ])


async def newchat_cmd(update, context):
    uid = update.effective_user.id
    cid = update.effective_chat.id
    chat_logs.delete_many({"user_id": uid, "chat_id": cid})
    await update.message.reply_text(
        f"✦ {sc('new chat unlocked')}\n{sc('purani baat reset ho gayi')}"
    )


async def profile_cmd(update, context):
    user = update.effective_user
    prefs = get_prefs(user.id)
    mem = get_memory(user.id)
    doc = users.find_one({"user_id": user.id}) or {}
    mem_lines = "\n".join(f"• {k}: {v}" for k, v in list(mem.items())[:8]) or sc("abhi khaali")
    text = (
        f"👤 <b>{sc('profile')}</b>\n\n"
        f"{sc('name')}: {user.first_name}\n"
        f"{sc('mode')}: <code>{prefs['mode']}</code>\n"
        f"{sc('lang')}: <code>{prefs['lang']}</code>\n"
        f"{sc('seen')}: <code>{int(doc.get('last_seen') or 0)}</code>\n\n"
        f"{sc('memory')}\n{mem_lines}"
    )
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=mode_kb())


async def mode_cmd(update, context):
    prefs = get_prefs(update.effective_user.id)
    await update.message.reply_text(
        f"✦ {sc('choose vibe')}\nnow: <code>{prefs['mode']}</code> / <code>{prefs['lang']}</code>",
        parse_mode="HTML",
        reply_markup=mode_kb(),
    )


async def mode_callback(update, context):
    query = update.callback_query
    await query.answer()
    data = query.data
    uid = query.from_user.id
    if data.startswith("mode_"):
        mode = data.split("_", 1)[1]
        if mode in MODES:
            set_pref(uid, mode=mode)
            await query.answer(f"Mode: {mode}", show_alert=True)
    elif data.startswith("lang_"):
        lang = data.split("_", 1)[1]
        set_pref(uid, lang=lang)
        await query.answer(f"Lang: {lang}", show_alert=True)
    prefs = get_prefs(uid)
    try:
        await query.edit_message_text(
            f"✦ {sc('choose vibe')}\nnow: <code>{prefs['mode']}</code> / <code>{prefs['lang']}</code>",
            parse_mode="HTML",
            reply_markup=mode_kb(),
        )
    except Exception:
        pass


async def imagine_cmd(update, context):
    from modules.image import image_cmd
    return await image_cmd(update, context)


def register(app):
    app.add_handler(CommandHandler("newchat", newchat_cmd))
    app.add_handler(CommandHandler("reset", newchat_cmd))
    app.add_handler(CommandHandler("profile", profile_cmd))
    app.add_handler(CommandHandler("mode", mode_cmd))
    app.add_handler(CommandHandler("imagine", imagine_cmd))
    app.add_handler(CallbackQueryHandler(mode_callback, pattern="^(mode_|lang_)"))
