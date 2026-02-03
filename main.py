print("🔥🔥 AGENTIC HONEY-POT API RUNNING 🔥🔥")

from fastapi import FastAPI, Request
from pydantic import BaseModel
from agent import generate_response
from datetime import datetime
import re

app = FastAPI(
    title="Agentic Honey-Pot API",
    version="final"
)

# -----------------------------
# HEALTH CHECK (VERY IMPORTANT)
# -----------------------------
@app.get("/")
async def health_check():
    return {
        "status": "active",
        "system": "Agentic Honey-Pot",
        "version": "final"
    }

# -----------------------------
# Input Model
# -----------------------------
class MessageInput(BaseModel):
    message: str

# -----------------------------
# MAIN API ENDPOINT
# -----------------------------
@app.post("/analyze")
async def analyze_message(input_data: MessageInput, request: Request):

    message = input_data.message
    msg_lower = message.lower()

    # 1️⃣ Scam Detection (simple & safe)
    scam_keywords = ["account", "blocked", "verify", "upi", "link", "bank", "urgent"]
    is_scam = any(word in msg_lower for word in scam_keywords)

    # 2️⃣ Extract Intelligence
    url_pattern = r"https?://[a-zA-Z0-9./_-]+"
    upi_pattern = r"\b[\w.-]+@[\w.-]+\b"
    bank_pattern = r"\b\d{9,18}\b"

    links = re.findall(url_pattern, message)
    upi_ids = re.findall(upi_pattern, message)
    bank_accounts = re.findall(bank_pattern, message)

    # 3️⃣ AI Human-like Reply
    reply = generate_response(message)

    # 4️⃣ Metadata
    timestamp = datetime.utcnow().isoformat()
    request_ip = request.client.host if request.client else None

    # 5️⃣ FINAL RESPONSE (HACKATHON FORMAT)
    return {
        "is_scam": is_scam,
        "reply": reply,
        "extracted_intelligence": {
            "upi_id": upi_ids[0] if upi_ids else None,
            "bank_account": bank_accounts[0] if bank_accounts else None,
            "phishing_link": links[0] if links else None
        },
        "metadata": {
            "timestamp": timestamp,
            "request_origin_ip": request_ip,
            "geo_location": None
        },
        "confidence_score": 0.9 if is_scam else 0.3
    }
