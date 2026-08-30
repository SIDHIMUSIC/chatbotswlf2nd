"""
HARRY CHATBOT — Professional Modular Architecture
Made with ❤️ by Harry (@SANATANI_BACHA)
"""

import traceback
from telegram.ext import ApplicationBuilder, ContextTypes

from config import TOKEN, OWNER_ID, LOG_GROUP_ID
from utils.auto_loader import load_modules, load_tools


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    error_text = "".join(
        __import__("traceback").format_exception(None, context.error, context.error.__traceback__)
    )
    try:
        if update and getattr(update, "effective_message", None):
            await update.effective_message.reply_text(
                "❌ Bot me thodi dikkat aa gayi hai\nOwner ko report bhej di gayi hai 🙂"
            )
    except Exception:
        pass
    try:
        await context.bot.send_message(chat_id=OWNER_ID, text=f"🚨 BOT ERROR (PRIVATE)\n\n{error_text[:3500]}")
    except Exception as e:
        print("OWNER DM FAILED:", e)
    try:
        if LOG_GROUP_ID:
            await context.bot.send_message(chat_id=LOG_GROUP_ID, text=f"🚨 BOT ERROR\n\n{error_text[:3500]}")
    except Exception as e:
        print("LOG GROUP FAILED:", e)
    print("BOT ERROR:\n", error_text)


async def _post_init(application):
    try:
        me = await application.bot.get_me()
        text = (
            f"🟢 Bot Successfully Started!\n\n"
            f"🤖 Name: {me.first_name}\n"
            f"👤 Username: @{me.username}\n"
            f"🆔 Bot ID: {me.id}\n"
            f"👑 Owner: {OWNER_ID}\n\n"
            f"✅ NaraRouter + OpenRouter ready."
        )
        try:
            await application.bot.send_message(chat_id=OWNER_ID, text=text)
        except Exception as e:
            print("Owner DM failed:", e)
        if LOG_GROUP_ID:
            try:
                await application.bot.send_message(chat_id=LOG_GROUP_ID, text=text)
            except Exception as e:
                print("Log Group failed:", e)
    except Exception as e:
        print("Startup notification failed:", e)


def main():
    app = ApplicationBuilder().token(TOKEN).post_init(_post_init).build()
    print("\n🔄 Loading modules...")
    load_modules(app)
    print("\n🔄 Loading tools...")
    load_tools(app)
    app.add_error_handler(error_handler)
    print("HARRY AI CHATBOT (Modular) online")
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
