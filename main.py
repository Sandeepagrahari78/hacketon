from fastapi import FastAPI, Request
from datetime import datetime
import re

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

# -----------------------------
# HEALTH CHECK (GET + HEAD)
# -----------------------------
@app.api_route("/", methods=["GET", "HEAD"])
async def health_check(request: Request):
    return {"status": "active", "system": "Agentic Honey-Pot", "version": "final"}

# -----------------------------
# ANALYZE (GET + HEAD for testers)
# -----------------------------
@app.api_route("/analyze", methods=["GET", "HEAD"])
async def analyze_get(request: Request):
    # tester ke liye default response
    return build_response("System validation ping", request)

# -----------------------------
# ANALYZE (POST real)
# -----------------------------
@app.post("/analyze")
async def analyze_post(request: Request):
    message = "System validation ping"

    # body safe parse (empty/invalid -> no crash)
    try:
        body = await request.json()
        if isinstance(body, dict):
            message = body.get("message") or body.get("text") or body.get("input") or message
        elif isinstance(body, str) and body.strip():
            message = body.strip()
    except Exception:
        pass

    return build_response(message, request)
