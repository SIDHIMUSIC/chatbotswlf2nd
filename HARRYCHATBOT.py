"""HARRY CHATBOT — modular Telegram AI."""
import traceback
from telegram.ext import ApplicationBuilder, ContextTypes

from config import TOKEN, OWNER_ID, LOG_GROUP_ID
from utils.auto_loader import load_modules, load_tools


async def error_handler(update, context: ContextTypes.DEFAULT_TYPE):
    error_text = "".join(
        traceback.format_exception(None, context.error, context.error.__traceback__)
    )
    try:
        if update and getattr(update, "effective_message", None):
            await update.effective_message.reply_text("Thodi dikkat aa gayi. Owner ko report chali.")
    except Exception:
        pass
    try:
        await context.bot.send_message(OWNER_ID, f"ERROR\n{error_text[:3500]}")
    except Exception as e:
        print("OWNER DM FAILED:", e)
    if LOG_GROUP_ID:
        try:
            await context.bot.send_message(LOG_GROUP_ID, f"ERROR\n{error_text[:3500]}")
        except Exception as e:
            print("LOG GROUP FAILED:", e)
    print(error_text)


async def _post_init(application):
    try:
        from helpers.catalog import refresh
        refresh()
    except Exception as e:
        print("catalog warmup skip:", e)
    try:
        me = await application.bot.get_me()
        text = (
            f"Online: {me.first_name} (@{me.username})\n"
            f"ID: {me.id}\nOwner: {OWNER_ID}\n"
            "NaraRouter + OpenRouter ready."
        )
        await application.bot.send_message(OWNER_ID, text)
        if LOG_GROUP_ID:
            await application.bot.send_message(LOG_GROUP_ID, text)
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
    print("Loading modules...")
    load_modules(app)
    print("Loading tools...")
    load_tools(app)
    app.add_error_handler(error_handler)
    print("HARRY online")
    app.run_polling(
        drop_pending_updates=True,
        allowed_updates=[
            "message", "edited_message", "callback_query", "inline_query",
            "business_connection", "business_message", "edited_business_message",
            "deleted_business_messages",
        ],
        close_loop=False,
    )


if __name__ == "__main__":
    main()
