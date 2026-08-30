# 👑 HARRY CHATBOT

> Professional Modular Telegram AI Bot  
> Made with ❤️ by **Harry** ([@SANATANI_BACHA](https://t.me/SANATANI_BACHA))

NaraRouter primary + OpenRouter backup. Live model pool from `router.bynara.id/api/plans`.

## Deploy

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/SIDHIMUSIC/chatbotswlf2nd)

Required ENV: `TELEGRAM_BOT_TOKEN`, `MONGODB_URI`, `OWNER_ID`, plus `NARA_API_KEY` and/or `OPENROUTER_API_KEY`.

Optional: `NARA_BASE_URL=https://router.bynara.id/v1`, `AI_QUALITY=balanced`, `AI_MAX_TOKENS=180`

## Commands
- Chat: just message (group me mention/nickname)
- `/image prompt` — AI image
- `/models` `/refreshmodels` — owner model pool
- `yaad rakh naam: Ashu` — memory

## Run
```bash
pip install -r requirements.txt
cp .env.example .env
python HARRYCHATBOT.py
```
