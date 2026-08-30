import asyncio
from telegram.ext import CommandHandler
from helpers.ai import generate_image_async

FRAMES = [
    "🖼 <b>STUDIO</b>\n<code>[██░░░░]</code> sketching...",
    "🖼 <b>STUDIO</b>\n<code>[████░░]</code> painting...",
    "🖼 <b>STUDIO</b>\n<code>[██████]</code> rendering...",
]


async def image_cmd(update, context):
    prompt = " ".join(context.args).strip() if context.args else ""
    if not prompt:
        return await update.message.reply_text(
            "🖼 <b>AI STUDIO</b>\n\n"
            "<code>/image cyberpunk indian boy 4k</code>\n"
            "<code>/image lord krishna digital art</code>",
            parse_mode="HTML",
        )
    wait = await update.message.reply_text(FRAMES[0], parse_mode="HTML")
    task = asyncio.create_task(generate_image_async(prompt))
    for frame in FRAMES[1:]:
        if task.done():
            break
        await asyncio.sleep(0.35)
        try:
            await wait.edit_text(frame, parse_mode="HTML")
        except Exception:
            break
    try:
        await context.bot.send_chat_action(update.effective_chat.id, "upload_photo")
        url = await task
        if url.startswith("http"):
            await update.message.reply_photo(photo=url, caption=f"✨ {prompt[:180]}")
        else:
            import base64
            from io import BytesIO
            raw = url.split(",", 1)[-1] if "," in url else url
            bio = BytesIO(base64.b64decode(raw))
            bio.name = "image.png"
            await update.message.reply_photo(photo=bio, caption=f"✨ {prompt[:180]}")
    except Exception as e:
        await update.message.reply_text(f"Image fail.\n<code>{str(e)[:180]}</code>", parse_mode="HTML")
    try:
        await wait.delete()
    except Exception:
        pass


def register(app):
    app.add_handler(CommandHandler("image", image_cmd))
