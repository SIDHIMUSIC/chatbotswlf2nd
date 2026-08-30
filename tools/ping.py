import time
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler
from config import SUPPORT_CHANNEL


async def ping(update, context):
    t0 = time.perf_counter()
    msg = await update.message.reply_text("🏓 checking...")
    ms = round((time.perf_counter() - t0) * 1000, 1)
    if ms < 120:
        status = "Ultra Fast"
    elif ms < 280:
        status = "Fast"
    else:
        status = "Warming up"
    await msg.edit_text(
        f"🏓 <b>PONG</b>\n"
        f"<code>{ms} ms</code> • {status}\n"
        f"AI router ready.",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Support", url=SUPPORT_CHANNEL)]]
        ),
    )


def register(app):
    app.add_handler(CommandHandler("ping", ping))
