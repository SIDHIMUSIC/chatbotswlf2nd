import os

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))
LOG_GROUP_ID = int(os.getenv("LOG_GROUP_ID", "0"))
SUPPORT_CHANNEL = os.getenv("SUPPORT_CHANNEL", "https://t.me/TG_BIO_STYLE")
MONGO_URI = os.getenv("MONGODB_URI")

GROQ_API_KEY = (
    os.getenv("GROQ_API_KEY")
    or os.getenv("GROK_API_KEY")
    or ""
)
GROQ_BASE_URL = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1").rstrip("/")
GROQ_MODELS = [
    m.strip()
    for m in os.getenv(
        "GROQ_MODELS",
        "llama-3.1-8b-instant,llama-3.3-70b-versatile,openai/gpt-oss-20b",
    ).split(",")
    if m.strip()
]

AI_QUALITY = os.getenv("AI_QUALITY", "balanced").strip().lower()
AI_MAX_TOKENS = int(os.getenv("AI_MAX_TOKENS", "180"))
AI_TEMPERATURE = float(os.getenv("AI_TEMPERATURE", "0.85"))
MODEL = os.getenv("AI_MODEL", GROQ_MODELS[0] if GROQ_MODELS else "llama-3.1-8b-instant")

STICKERS = {
    "love": "CAACAgUAAxkBAAICkGpqypsya2BXKP0sNhsEtd-cAsDhAAIxGwACdAwJVM63pdgEFTPJPQQ",
    "laugh": "CAACAgUAAxkBAAICkmpqyui1e-zbO-nol7-e01vrC2MfAAL1GAAChw3oV8iooC6NIUCIPQQ",
    "cool": "CAACAgUAAxkBAAICjGpqyoW1gnhwTDJIFzz95oJG6z7wAAKFBgACXlLhVLPoEBmR249cPQQ",
    "sad": "CAACAgUAAxkBAAIClGpqywxGs1BzSBd9g4Q6Ny6tuyPJAAL7GQACxC_4VC60bVf1GL78PQQ",
    "hi": "CAACAgUAAxkBAAIClmpqyyoFUf8V0ANvl4PlcemyJwXxAALvEQACfBtYVl9LYa8NbqObPQQ",
    "kiss": "CAACAgUAAxkBAAICimpqynJAvtWx6NL6eEav0krtBWyOAAKICgAC2Z5YVzc4yHqRO_tUPQQ",
}

START_IMAGES = [
    "https://graph.org/file/705cda02e63f4cb0bdb90-ce4d0ddd3a8cf38b5a.jpg",
    "https://graph.org/file/8c5e8ea95b69e682aed19-22090eb6bb17ce7a54.jpg",
    "https://graph.org/file/556615482003de63f32be-58c192c7e65004f9d4.jpg",
    "https://graph.org/file/bb129887cac5752f0f0f5-70aec0f85376516f16.jpg",
]

BOT_USERNAME = os.getenv("BOT_USERNAME", "HARRY_HERUKOBOT")
BOT_NICKNAMES = ["harry"]

if not TOKEN or not MONGO_URI or not OWNER_ID:
    raise RuntimeError("Missing TELEGRAM_BOT_TOKEN / MONGODB_URI / OWNER_ID")

if not GROQ_API_KEY:
    raise RuntimeError("Missing GROQ_API_KEY")
