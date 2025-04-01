from fastapi import FastAPI, Request
import httpx
import os
import asyncio
import openai
import pprint

app = FastAPI()

# === Настройки ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
YOUTUBE_LINK = "https://youtube.com/@GoraGMX"
FACEIT_NICKNAME = "GoraGMX"

# === Webhook от Telegram ===
@app.post("/telegram")
async def telegram_webhook(request: Request):
    body = await request.json()
    print("=== RAW TELEGRAM UPDATE ===")
    pprint.pprint(body)

    message = body.get("message")
    if not message:
        return {"ok": True}

    chat_id = message["chat"]["id"]
    text = message.get("text", "")

    if text.startswith("!гориксскажи"):
        user_input = text.replace("!гориксскажи", "").strip()
        if not user_input:
            reply = "[GORIX]: Скажи что-нибудь после команды!"
        else:
            response = await ask_gpt(user_input)
            reply = f"[GORIX]: {response}"

    elif text.startswith("!гориксфакт"):
        topic = text.replace("!гориксфакт", "").strip()
        prompt = f"Расскажи интересный факт по теме '{topic}'" if topic else "Расскажи интересный факт"
        response = await ask_gpt(prompt)
        reply = f"[GORIX FACT]: {response}"

    elif text.startswith("!стата"):
        reply = f"[GORIX]: FACEIT-стата игрока {FACEIT_NICKNAME} скоро будет доступна."

    elif text.startswith("!ютуб"):
        reply = f"[GORIX]: Вот мой YouTube канал — {YOUTUBE_LINK}"

    else:
        return {"ok": True}  # Не реагируем на другие команды

    await send_message(chat_id, reply)
    return {"ok": True}


# === Запрос к OpenAI ===
async def ask_gpt(prompt: str) -> str:
    openai.api_key = os.getenv("OPENAI_API_KEY")
    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Ошибка: {str(e)}"


# === Ответ в Telegram ===
async def send_message(chat_id: int, text: str):
    async with httpx.AsyncClient() as client:
        await client.post(f"{TELEGRAM_API_URL}/sendMessage", json={
            "chat_id": chat_id,
            "text": text
        })
