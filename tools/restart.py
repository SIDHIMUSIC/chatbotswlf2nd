"""Owner /restart /heal — soft fix ya hard reboot."""
from telegram.ext import CommandHandler

from helpers.decorators import is_owner
from helpers.heal import can_restart, schedule_restart, soft_heal


async def restart(update, context):
    if not is_owner(update.effective_user.id):
        return await update.message.reply_text("Sirf owner.")
    if not can_restart():
        return await update.message.reply_text("Abhi abhi restart hua. 3 min baad try karo.")
    soft_heal()
    await update.message.reply_text("Restart ho raha hai. 10-20 sec me wapas aaunga.")
    schedule_restart(1.2)


async def heal_cmd(update, context):
    if not is_owner(update.effective_user.id):
        return await update.message.reply_text("Sirf owner.")
    cleared = soft_heal()
    bits = ", ".join(cleared) or "nothing"
    await update.message.reply_text(f"Heal ho gaya: {bits}\nRestart nahi kiya.")


def register(app):
    app.add_handler(CommandHandler("restart", restart))
    app.add_handler(CommandHandler("reboot", restart))
    app.add_handler(CommandHandler("heal", heal_cmd))
    app.add_handler(CommandHandler("fix", heal_cmd))
