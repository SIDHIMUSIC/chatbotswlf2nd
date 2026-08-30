# HARRY CHATBOT

Modular Telegram AI bot. NaraRouter primary + OpenRouter backup.

## Deploy
[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/SIDHIMUSIC/chatbotswlf2nd)

ENV required: `TELEGRAM_BOT_TOKEN`, `MONGODB_URI`, `OWNER_ID`  
Plus `NARA_API_KEY` and/or `OPENROUTER_API_KEY`.

```
NARA_BASE_URL=https://router.bynara.id/v1
AI_QUALITY=balanced
AI_MAX_TOKENS=140
```

## Commands
- `/start` cinematic boot + home
- chat in private / mention in group
- `/image prompt`
- `/ping` `/help` `/id` `/owner`
- owner: `/stats` `/models` `/refreshmodels` `/broadcast`

```bash
pip install -r requirements.txt
cp .env.example .env
python HARRYCHATBOT.py
```
