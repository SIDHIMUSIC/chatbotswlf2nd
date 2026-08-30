"""HARRY CHATBOT — modular Telegram AI + live clones."""
import traceback
from telegram import BotCommand
from telegram.ext import ApplicationBuilder, ContextTypes

from config import TOKEN, OWNER_ID, LOG_GROUP_ID
from utils.auto_loader import load_modules, load_tools
from helpers.clone_runtime import start_saved_clones, UPDATES


async def error_handler(update, context: ContextTypes.DEFAULT_TYPE):
    error_text = "".join(
        traceback.format_exception(None, context.error, context.error.__traceback__)
    )
    try:
        if update and getattr(update, "effective_message", None):
            await update.effective_message.reply_text("Thodi dikkat aa gayi.")
    except Exception:
        pass
    try:
        await context.bot.send_message(OWNER_ID, f"ERROR\n{error_text[:3500]}")
    except Exception as e:
        print("OWNER DM FAILED:", e)
    print(error_text)


async def _post_init(application):
    try:
        await application.bot.set_my_commands([
            BotCommand("start", "Open home panel"),
            BotCommand("help", "Command guide"),
            BotCommand("image", "Generate AI image"),
            BotCommand("clone", "Clone a bot token"),
            BotCommand("checkin", "Daily check-in"),
            BotCommand("ping", "Speed check"),
        ])
    except Exception as e:
        print("set commands skip:", e)
    try:
        from helpers.catalog import refresh
        refresh()
    except Exception as e:
        print("catalog warmup skip:", e)
    started, failed = [], []
    try:
        started, failed = await start_saved_clones()
    except Exception as e:
        print("clone boot fail:", e)
    try:
        me = await application.bot.get_me()
        text = (
            f"Online: {me.first_name} (@{me.username})\n"
            f"Clones live: {len(started)}\n"
            + ("Failed: " + "; ".join(failed[:5]) if failed else "Nara + OpenRouter ready.")
        )
        await application.bot.send_message(OWNER_ID, text)
    except Exception as e:
        print("Startup notify skip:", e)


def main():
    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .concurrent_updates(True)
        .post_init(_post_init)
        .build()
    )
    load_modules(app)
    load_tools(app)
    app.add_error_handler(error_handler)
    print("HARRY online")
    app.run_polling(
        drop_pending_updates=True,
        allowed_updates=UPDATES,
        close_loop=False,
    )


if __name__ == "__main__":
    main()
