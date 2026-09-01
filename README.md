# HARRY CHATBOT

Modular Telegram AI bot. Gemini primary + NaraRouter + OpenRouter backup.

## Deploy
[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/SIDHIMUSIC/chatbotswlf2nd)

ENV required: `TELEGRAM_BOT_TOKEN`, `MONGODB_URI`, `OWNER_ID`  
Plus at least one of `GEMINI_API_KEY`, `NARA_API_KEY`, `OPENROUTER_API_KEY`.

```
GEMINI_API_KEY=your_key
GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta
GEMINI_MODELS=gemini-flash-latest,gemini-2.5-flash,gemini-2.0-flash
NARA_BASE_URL=https://router.bynara.id/v1
AI_QUALITY=balanced
AI_MAX_TOKENS=180
```

Gemini endpoint used:
`POST /v1beta/models/gemini-flash-latest:generateContent`

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
