import os

# ================= ENV =================
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))
LOG_GROUP_ID = int(os.getenv("LOG_GROUP_ID", "0"))
SUPPORT_CHANNEL = os.getenv("SUPPORT_CHANNEL", "https://t.me/TG_BIO_STYLE")
MONGO_URI = os.getenv("MONGODB_URI")

# NaraRouter (primary) — https://router.bynara.id
NARA_API_KEY = os.getenv("NARA_API_KEY") or os.getenv("NARAROUTER_API_KEY", "")
NARA_BASE_URL = os.getenv("NARA_BASE_URL", "https://router.bynara.id/v1").rstrip("/")

# OpenRouter (backup)
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = os.getenv(
    "OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"
).rstrip("/")

NARA_MODELS = [
    m.strip()
    for m in os.getenv(
        "NARA_MODELS",
        "agnes-2.5-flash,agnes-2.0-flash,glm-5.3-flash-free,"
        "minimax-m3-free,laguna-s-2.1,auto/bynara,gpt-5.5",
    ).split(",")
    if m.strip()
]
OPENROUTER_MODELS = [
    m.strip()
    for m in os.getenv(
        "OPENROUTER_MODELS",
        "openrouter/free,meta-llama/llama-3.3-70b-instruct:free,"
        "minimax/minimax-m3:free",
    ).split(",")
    if m.strip()
]

NARA_IMAGE_MODELS = [
    m.strip()
    for m in os.getenv(
        "NARA_IMAGE_MODELS",
        "agnes-image-2.1-flash,agnes-image-2.0-flash",
    ).split(",")
    if m.strip()
]
OPENROUTER_IMAGE_MODELS = [
    m.strip()
    for m in os.getenv(
        "OPENROUTER_IMAGE_MODELS",
        "black-forest-labs/flux.2-schnell,"
        "google/gemini-2.5-flash-image,"
        "sourceful/riverflow-v2-quick-preview",
    ).split(",")
    if m.strip()
]

AI_QUALITY = os.getenv("AI_QUALITY", "balanced").strip().lower()
AI_MAX_TOKENS = int(os.getenv("AI_MAX_TOKENS", "180"))
AI_TEMPERATURE = float(os.getenv("AI_TEMPERATURE", "0.85"))
MODEL = os.getenv("AI_MODEL", NARA_MODELS[0] if NARA_MODELS else "auto/bynara")

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

BOT_USERNAME = os.getenv("BOT_USERNAME", "JULIET_MUSUCBOT")
BOT_NICKNAMES = ["harry", "juliet", "ai", "baby"]

if not TOKEN or not MONGO_URI or not OWNER_ID:
    raise RuntimeError("Missing TELEGRAM_BOT_TOKEN / MONGODB_URI / OWNER_ID")

if not NARA_API_KEY and not OPENROUTER_KEY:
    raise RuntimeError("Missing NARA_API_KEY or OPENROUTER_API_KEY")
