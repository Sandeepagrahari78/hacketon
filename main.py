from fastapi import FastAPI, Request
from datetime import datetime
import re
import json

app = FastAPI(title="Agentic Honey-Pot API", version="final")

# -----------------------------
# HELPERS
# -----------------------------
def build_response(message: str, request: Request):
    msg_lower = (message or "").lower()
    scam_keywords = ["account", "blocked", "verify", "upi", "link", "bank", "urgent"]
    is_scam = any(word in msg_lower for word in scam_keywords)

    url_pattern = r"https?://[a-zA-Z0-9./_-]+"
    upi_pattern = r"\b[\w.-]+@[\w.-]+\b"
    bank_pattern = r"\b\d{9,18}\b"

    links = re.findall(url_pattern, message or "")
    upi_ids = re.findall(upi_pattern, message or "")
    bank_accounts = re.findall(bank_pattern, message or "")

    return {
        "is_scam": is_scam,
        "reply": "Main thoda confuse hoon, ek baar phir se samjha sakte ho?",
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

def safe_extract_message(raw_bytes: bytes) -> str:
    # default message if body empty / invalid
    message = "System validation ping"

    if not raw_bytes:
        return message

    try:
        text = raw_bytes.decode("utf-8", errors="ignore").strip()
        if not text:
            return message

        # try JSON parse
        data = json.loads(text)

        if isinstance(data, dict):
            return data.get("message") or data.get("text") or data.get("input") or message
        if isinstance(data, str) and data.strip():
            return data.strip()

        return message
    except Exception:
        # not JSON -> treat as plain text
        try:
            text = raw_bytes.decode("utf-8", errors="ignore").strip()
            return text if text else message
        except Exception:
            return message

# -----------------------------
# HEALTH CHECK (GET + HEAD)
# -----------------------------
@app.api_route("/", methods=["GET", "HEAD"])
async def health_check(request: Request):
    return {"status": "active", "system": "Agentic Honey-Pot", "version": "final"}

# -----------------------------
# ANALYZE (GET + HEAD)
# -----------------------------
@app.api_route("/analyze", methods=["GET", "HEAD"])
async def analyze_get(request: Request):
    return build_response("System validation ping", request)

# -----------------------------
# ANALYZE (POST)
# -----------------------------
@app.post("/analyze")
async def analyze_post(request: Request):
    raw = await request.body()          # ✅ never fails
    message = safe_extract_message(raw)  # ✅ never fails
    return build_response(message, request)
