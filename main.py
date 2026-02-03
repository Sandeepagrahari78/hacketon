from fastapi import FastAPI, Request
from agent import generate_response
from datetime import datetime
import re

app = FastAPI(title="Agentic Honey-Pot API")

@app.post("/analyze")
async def analyze_message(request: Request):
    try:
        body = await request.json()
        message = body.get("message", "Your account is blocked. Verify immediately.")
    except:
        message = "Your account is blocked. Verify immediately."

    msg_lower = message.lower()

    scam_keywords = ["account", "blocked", "verify", "upi", "link", "bank"]
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
            "timestamp": datetime.now().isoformat(),
            "request_origin_ip": request.client.host if request.client else None,
            "geo_location": None
        },
        "confidence_score": 0.9 if is_scam else 0.3
    }
