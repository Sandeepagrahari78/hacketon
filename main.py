print("🔥🔥 AGENTIC HONEY-POT API RUNNING 🔥🔥")

from fastapi import FastAPI, Request
from pydantic import BaseModel
from agent import generate_response
from datetime import datetime
import re
from typing import Optional

app = FastAPI(
    title="Agentic Honey-Pot API",
    version="final"
)

# -----------------------------
# HEALTH CHECK
# -----------------------------
@app.get("/")
async def health_check():
    return {
        "status": "active",
        "system": "Agentic Honey-Pot",
        "version": "final"
    }

# -----------------------------
# Input Model (POST support)
# -----------------------------
class MessageInput(BaseModel):
    message: Optional[str] = None


# -----------------------------
# CORE LOGIC (REUSED)
# -----------------------------
def process_message(message: str, request: Request):
    msg_lower = message.lower()

    scam_keywords = ["account", "blocked", "verify", "upi", "link", "bank", "urgent"]
    is_scam = any(word in msg_lower for word in scam_keywords)

    url_pattern = r"https?://[a-zA-Z0-9./_-]+"
    upi_pattern = r"\b[\w.-]+@[\w.-]+\b"
    bank_pattern = r"\b\d{9,18}\b"

    links = re.findall(url_pattern, message)
    upi_ids = re.findall(upi_pattern, message)
    bank_accounts = re.findall(bank_pattern, message)

    reply = generate_response(message)

    return {
        "is_scam": is_scam,
        "reply": reply,
        "extracted_intelligence": {
            "upi_id": upi_ids[0] if upi_ids else None,
            "bank_account": bank_accounts[0] if bank_accounts else None,
            "phishing_link": links[0] if links else None
        },
        "metadata": {
            "timestamp": datetime.utcnow().isoformat(),
            "request_origin_ip": request.client.host if request.client else None,
            "geo_location": None
        },
        "confidence_score": 0.9 if is_scam else 0.3
    }


# -----------------------------
# GET ANALYZE (GUVI TESTER)
# -----------------------------
@app.get("/analyze")
async def analyze_get(request: Request):
    return process_message(
        "System test request for honeypot validation.",
        request
    )


# -----------------------------
# POST ANALYZE (REAL USE)
# -----------------------------
@app.post("/analyze")
async def analyze_post(
    request: Request,
    input_data: Optional[MessageInput] = None
):
    message = (
        input_data.message
        if input_data and input_data.message
        else "System test request for honeypot validation."
    )

    return process_message(message, request)
