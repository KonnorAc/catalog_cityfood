from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
import os, requests
app = FastAPI()

WHATSAPP_TOKEN = os.getenv("EAAPKqRtzHkkBPEhmivNVqbSWqVZCGsuswlTtTcYLZAYGQc9WdiWbJhCZAgJUe7DZA8ehCAQYNLQGnlpPz3txgR8ZBuWghgaBSZBzUMQPeryh1QiOazY1uORUq576XXcpOR398sn8QrEKQo7w8KZCSj16fpmQTZAXVD21ls8PbOZCQMGQ0Vqu0OZBAjrqIYsgIJvB4JoYKBPTjdTeM1snWjQKmK54pZCv0yMWTSFuF7v0JLb25msZAQZDZD")        # токен из Meta
PHONE_NUMBER_ID = os.getenv("812730505246582")      # id номера в WhatsApp Cloud API
GRAPH_URL = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"

class Lead(BaseModel):
    name: str
    company: str
    volume: str | None = None
    message: str | None = None
    to_phone: str 

@app.post("/send-whatsapp")
def send_whatsapp(lead: Lead):
    text = (
        f"Новая заявка с сайта:\n"
        f"Имя: {lead.name}\n"
        f"Компания: {lead.company}\n"
        f"Email: {lead.email}\n"
        f"Объём: {lead.volume or ''}\n"
        f"Сообщение: {lead.message or ''}"
    )
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": lead.to_phone,          
        "type": "text",
        "text": {"body": text}
    }
    r = requests.post(GRAPH_URL, headers=headers, json=payload, timeout=15)
    if r.status_code >= 300:
        raise HTTPException(status_code=500, detail=r.text)
    return {"ok": True}
