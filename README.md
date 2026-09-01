# HARRY CHATBOT

Modular Telegram AI bot. Gemini 3.6 Flash primary + NaraRouter + OpenRouter backup.

ENV required: `TELEGRAM_BOT_TOKEN`, `MONGODB_URI`, `OWNER_ID`  
Plus at least one of `GEMINI_API_KEY`, `NARA_API_KEY`, `OPENROUTER_API_KEY`.

```
GEMINI_API_KEY=your_key
GEMINI_MODELS=gemini-3.6-flash,gemini-3.7-flash,gemini-flash-latest
```

New Gemini keys cannot call `gemini-2.5-flash` (404). Use `gemini-3.6-flash`.

```bash
pip install -r requirements.txt
cp .env.example .env
python HARRYCHATBOT.py
```
