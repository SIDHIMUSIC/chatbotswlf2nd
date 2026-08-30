import random
from telegram.ext import CommandHandler

FLIRT = [
    "Aankh mili nahi thi properly, phir bhi dimaag mein reh gaye tum.",
    "Tumhara text aaya na, din set ho gaya.",
    "Itna cute mat bano, focus toot jata hai.",
    "Coffee nahi, tumhari baatein chahiye late night.",
]
ROAST = [
    "Wifi se zyada hang tum karte ho.",
    "Confidence full, homework jaise empty.",
    "Mirror se ladai mat karna, haar jaoge.",
    "Brain buffering pe hai kya aaj?",
]
HUG = [
    "Aao, ek tight hug. Bahar ki duniya baad mein.",
    "Head on shoulder. Quiet. Safe.",
    "Hug pack delivered. Expiry: never.",
]


async def _pick(update, lines, title):
    await update.message.reply_text(f"{title}\n{random.choice(lines)}")


async def flirt(update, context):
    await _pick(update, FLIRT, "✦ flirt")


async def roast(update, context):
    await _pick(update, ROAST, "✦ roast")


async def hug(update, context):
    await _pick(update, HUG, "✦ hug")


def register(app):
    app.add_handler(CommandHandler("flirt", flirt))
    app.add_handler(CommandHandler("roast", roast))
    app.add_handler(CommandHandler("hug", hug))
