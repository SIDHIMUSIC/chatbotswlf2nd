"""HARRY CHATBOT — modular Telegram AI + live clones."""
import traceback
from telegram import BotCommand
from telegram.ext import ApplicationBuilder, ContextTypes
from telegram.error import Conflict, NetworkError, TimedOut, RetryAfter

from config import TOKEN, OWNER_ID, LOG_GROUP_ID
from utils.auto_loader import load_modules, load_tools
from helpers.clone_runtime import start_saved_clones, UPDATES
from helpers.heal import note_error, soft_heal


async def error_handler(update, context: ContextTypes.DEFAULT_TYPE):
    err = context.error
    quiet = isinstance(err, (TimedOut, RetryAfter, NetworkError)) and not isinstance(err, Conflict)
    error_text = "".join(
        traceback.format_exception(None, err, err.__traceback__ if err else None)
    )
    if not quiet:
        try:
            if update and getattr(update, "effective_message", None):
                await update.effective_message.reply_text("Gadbad hui, khud theek kar raha hoon.")
        except Exception:
            pass
        try:
            await context.bot.send_message(OWNER_ID, f"ERROR\n{str(err)[:800]}")
        except Exception as e:
            print("OWNER DM FAILED:", e)
        print(error_text[:2000])
    else:
        print("NET SKIP:", type(err).__name__, err)

    restarted = note_error(err)
    if restarted:
        try:
            await context.bot.send_message(OWNER_ID, "Auto-restart scheduled.")
        except Exception:
            pass


async def _post_init(application):
    soft_heal()
    try:
        await application.bot.set_my_commands([
            BotCommand("start", "Open home panel"),
            BotCommand("help", "Command guide"),
            BotCommand("image", "Generate AI image"),
            BotCommand("clone", "Clone a bot token"),
            BotCommand("checkin", "Daily check-in"),
            BotCommand("ping", "Speed check"),
            BotCommand("restart", "Owner reboot"),
            BotCommand("heal", "Owner self-fix"),
        ])
    except Exception as e:
        print("set commands skip:", e)
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
            + ("Failed: " + "; ".join(failed[:5]) if failed else "Groq + self-heal ready.")
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
    print("HARRY online — Groq + heal")
    app.run_polling(
        drop_pending_updates=True,
        allowed_updates=UPDATES,
        close_loop=False,
    )


if __name__ == "__main__":
    main()
