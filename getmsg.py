import os
import re
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, Field
from dotenv import load_dotenv  # опционально (см. ниже)

load_dotenv()  # если используешь .env

app = FastAPI(title="Lead -> Telegram", version="1.0.0")

# <-- ИМЕНА переменных окружения!
TELEGRAM_BOT_TOKEN = os.getenv("8178976162:AAFR-9Lw4L2a7ti4N4a4lqBLkRSINfKyuMk")
TELEGRAM_CHAT_ID = os.getenv("6631927894")

if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    raise RuntimeError("TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID не заданы")

TG_API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

E164_RE = re.compile(r"^[1-9]\d{7,14}$")

class Lead(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    company: str | None = Field(None, max_length=120)
    email: EmailStr | None = None
    client_phone: str | None = Field(None, description="В международном формате без +, напр. 905551112233")
    volume: str | None = Field(None, max_length=50)
    message: str | None = Field(None, max_length=1000)

    def phone_ok(self) -> bool:
        return self.client_phone is None or bool(E164_RE.match(self.client_phone))

TG_MD_ESC = r"_*[]()~`>#+-=|{}.!"
def esc_md(text: str) -> str:
    if text is None:
        return "-"
    return "".join("\\" + ch if ch in TG_MD_ESC else ch for ch in str(text))

def send_telegram_message(text: str) -> dict:
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text[:4096],
        "parse_mode": "MarkdownV2",
        "disable_web_page_preview": True
    }
    r = requests.post(f"{TG_API}/sendMessage", json=payload, timeout=15)
    if r.status_code >= 300:
        raise HTTPException(status_code=500, detail=r.text)
    return r.json()

@app.post("/lead")
def handle_lead(lead: Lead):
    if not lead.phone_ok():
        raise HTTPException(status_code=422, detail="client_phone должен быть в E.164 без '+', напр. 905551112233")

    text = (
        f"*📥 Новая заявка с сайта*\n"
        f"*Имя:* {esc_md(lead.name)}\n"
        f"*Компания:* {esc_md(lead.company or '-')}\n"
        f"*Email:* {esc_md(lead.email or '-')}\n"
        f"*Телефон (WhatsApp/Telegram):* {esc_md(lead.client_phone or '-')}\n"
        f"*Объём:* {esc_md(lead.volume or '-')}\n"
        f"*Комментарий:* {esc_md(lead.message or '-')}"
    )
    resp = send_telegram_message(text)
    return {"ok": True, "telegram_response": resp}
