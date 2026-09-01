from telegram import InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler

from helpers.decorators import is_owner
from helpers.style import sc
from helpers.ui import LINE, OWNER_USER, btn, pe
from config import BOT_USERNAME


def _bot(context):
    return (getattr(context.bot, "username", None) or BOT_USERNAME or "HARRY_HERUKOBOT").lstrip("@")


def pages(uname: str):
    star = pe("star", "✦")
    fire = pe("fire", "🔥")
    heart = pe("heart", "💖")
    crown = pe("crown", "👑")
    return {
        "help_home": (
            f"{star} <b>{sc('help menu')}</b>\n"
            f"{LINE}\n\n"
            f"{sc('i am')} <b>@{uname}</b>\n"
            f"{sc('your personal ai companion')}\n\n"
            f"{fire} {sc('pick a section below')}\n"
            f"{sc('groups me reply ya')} @{uname} {sc('se call karo')}"
        ),
        "help_chat": (
            f"{heart} <b>{sc('chat commands')}</b>\n"
            f"{LINE}\n\n"
            "/start — {home}\n".format(home=sc("home panel"))
            + "/help — {g}\n".format(g=sc("this menu"))
            + "/ping — {s}\n".format(s=sc("speed check"))
            + "/id — {i}\n\n".format(i=sc("user and chat id"))
            + f"<code>yaad rakh name: {sc('value')}</code>\n"
            f"{sc('joke  shayari  roleplay mood')}"
        ),
        "help_tools": (
            f"{fire} <b>{sc('tools')}</b>\n"
            f"{LINE}\n\n"
            "/checkin — {d}\n".format(d=sc("daily streak"))
            + "/clone — {c}\n".format(c=sc("make your twin bot"))
            + "/myclones — {l}\n".format(l=sc("your clones"))
            + "/mode — {m}\n".format(m=sc("chat vibe"))
            + "/owner — {o}".format(o=sc("creator card"))
        ),
        "help_owner": (
            f"{crown} <b>{sc('owner panel')}</b>\n"
            f"{LINE}\n\n"
            "/stats  /broadcast\n"
            "/heal  /fix\n"
            "/restart  /reboot\n"
            "/models  /pestatus\n\n"
            f"{sc('chat me')} <code>sudhar</code> {sc('or')} <code>restart</code>"
        ),
    }


def nav():
    return InlineKeyboardMarkup([
        [
            btn("◍ ᴄʜᴀᴛ", callback_data="help_chat", pe_name="chat"),
            btn("◍ ᴛᴏᴏʟѕ", callback_data="help_tools", pe_name="fire"),
        ],
        [
            btn("◍ ᴏᴡɴᴇʀ", callback_data="help_owner", pe_name="crown"),
            btn("◍ ʜᴏᴍᴇ", callback_data="home", pe_name="home"),
        ],
        [btn("◍ ᴄʟᴏѕᴇ", callback_data="help_close", pe_name="star")],
    ])


async def _show(target, key, context, is_query=False):
    uname = _bot(context)
    text = pages(uname).get(key, pages(uname)["help_home"])
    kb = nav()
    if is_query:
        try:
            await target.edit_message_text(text, parse_mode="HTML", reply_markup=kb, disable_web_page_preview=True)
            return
        except Exception:
            try:
                await target.edit_message_caption(caption=text, parse_mode="HTML", reply_markup=kb)
                return
            except Exception:
                target = target.message
    await target.reply_text(text, parse_mode="HTML", reply_markup=kb, disable_web_page_preview=True)


async def help_cmd(update, context):
    await _show(update.message, "help_home", context)


async def help_callback(update, context):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data == "help_close":
        try:
            await query.message.delete()
        except Exception:
            pass
        return
    if data == "help_owner" and not is_owner(query.from_user.id):
        return await query.answer("Owner only.", show_alert=True)
    await _show(query, data if data in pages("x") else "help_home", context, is_query=True)


def register(app):
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CallbackQueryHandler(help_callback, pattern="^help_"))
