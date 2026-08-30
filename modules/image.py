from telegram.ext import CommandHandler

from helpers.ai import generate_image_async


async def image_cmd(update, context):
    prompt = " ".join(context.args).strip() if context.args else ""
    if not prompt:
        return await update.message.reply_text(
            "Usage:\n/image cyberpunk indian boy 4k\n/image lord krishna digital art"
        )

    wait = await update.message.reply_text("Image bana raha hoon...")
    try:
        await context.bot.send_chat_action(update.effective_chat.id, "upload_photo")
        url = await generate_image_async(prompt)
        if url.startswith("http"):
            await update.message.reply_photo(photo=url, caption=prompt[:200])
        else:
            import base64
            from io import BytesIO
            raw = url
            if "," in raw:
                raw = raw.split(",", 1)[1]
            bio = BytesIO(base64.b64decode(raw))
            bio.name = "image.png"
            await update.message.reply_photo(photo=bio, caption=prompt[:200])
    except Exception as e:
        await update.message.reply_text(
            "Image nahi bani. Nara/OpenRouter image model check karo.\n"
            f"Error: {str(e)[:200]}"
        )
    try:
        await wait.delete()
    except Exception:
        pass


def register(app):
    app.add_handler(CommandHandler("image", image_cmd))
