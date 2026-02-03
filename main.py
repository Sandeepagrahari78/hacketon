from fastapi import FastAPI, Request
from datetime import datetime
import re

app = FastAPI(title="Agentic Honey-Pot API", version="final")

# -----------------------------
# HEALTH CHECK
# -----------------------------
@app.get("/")
async def health_check():
    return {"status": "active", "system": "Agentic Honey-Pot", "version": "final"}


# -----------------------------
# MAIN API (NO 422 GUARANTEE)
# -----------------------------
@app.post("/analyze")
async def analyze_message(request: Request):

    # Default message (works even if GUVI sends empty body)
    message = "System validation ping. Please share details."

    # Try to read JSON body safely
    try:
        body = await request.json()

        if isinstance(body, dict):
            message = body.get("message") or body.get("text") or body.get("input") or message
        elif isinstance(body, str) and body.strip():
            message = body.strip()

    except Exception:
        # Body missing / invalid JSON -> keep default message
        pass

    msg_lower = message.lower()

    # Scam detection
    scam_keywords = ["account", "blocked", "verify", "upi", "link", "bank", "urgent"]
    is_scam = any(word in msg_lower for word in scam_keywords)

    # Extraction
    url_pattern = r"https?://[a-zA-Z0-9./_-]+"
    upi_pattern = r"\b[\w.-]+@[\w.-]+\b"
    bank_pattern = r"\b\d{9,18}\b"

    links = re.findall(url_pattern, message)
    upi_ids = re.findall(upi_pattern, message)
    bank_accounts = re.findall(bank_pattern, message)

    timestamp = datetime.utcnow().isoformat()
    request_ip = request.client.host if request.client else None

    return {
        "is_scam": is_scam,
        "reply": "Main thoda confuse hoon, ek baar phir se samjha sakte ho?",
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
