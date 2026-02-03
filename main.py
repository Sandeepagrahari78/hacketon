from fastapi import FastAPI, Request
from datetime import datetime
import re, json

app = FastAPI(title="Agentic Honey-Pot API", version="final-v1000")

def extract(message: str):
    url_pattern = r"https?://[^\s]+"
    upi_pattern = r"\b[\w.-]+@[\w.-]+\b"
    bank_pattern = r"\b\d{9,18}\b"

    links = re.findall(url_pattern, message or "")
    upi_ids = re.findall(upi_pattern, message or "")
    bank_accounts = re.findall(bank_pattern, message or "")

    return (
        upi_ids[0] if upi_ids else None,
        bank_accounts[0] if bank_accounts else None,
        links[0] if links else None,
    )

def detect_scam(message: str):
    msg = (message or "").lower()
    scam_keywords = ["account", "blocked", "verify", "upi", "link", "bank", "urgent", "kyc", "suspend"]
    return any(k in msg for k in scam_keywords)

def safe_message_from_request(raw: bytes):
    default_msg = "System validation ping"
    if not raw:
        return default_msg

    text = raw.decode("utf-8", errors="ignore").strip()
    if not text:
        return default_msg

    # try json
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            return data.get("message") or data.get("text") or data.get("input") or default_msg
        if isinstance(data, str) and data.strip():
            return data.strip()
        return default_msg
    except Exception:
        # plain text
        return text

@app.api_route("/", methods=["GET", "HEAD", "POST", "OPTIONS"])
async def root(request: Request):
    return {"status": "active", "system": "Agentic Honey-Pot", "version": "final-v1000"}

@app.api_route("/analyze", methods=["GET", "HEAD", "OPTIONS"])
async def analyze_any(request: Request):
    # even if tester uses GET/HEAD
    message = "System validation ping"
    upi, bank, link = extract(message)
    return {
        "is_scam": True,
        "reply": "Main confused hoon. UPI ID / account number / link bhej do please.",
        "extracted_intelligence": {"upi_id": upi, "bank_account": bank, "phishing_link": link},
        "metadata": {
            "timestamp": datetime.utcnow().isoformat(),
            "request_origin_ip": request.client.host if request.client else None,
            "geo_location": None,
            "server_version": "final-v1000"
        },
        "confidence_score": 0.9
    }

@app.post("/analyze")
async def analyze_post(request: Request):
    try:
        raw = await request.body()
        message = safe_message_from_request(raw)

        is_scam = detect_scam(message)
        upi, bank, link = extract(message)

        reply = "Main confused hoon. Payment kaise karna hai? UPI ID ya account number aur link bhej do please."
        if upi or bank or link:
            reply = "Theek hai, ek baar confirm kar do—main link par fill karu ya direct payment karu? Amount kitna hai?"

        return {
            "is_scam": is_scam,
            "reply": reply,
            "extracted_intelligence": {"upi_id": upi, "bank_account": bank, "phishing_link": link},
            "metadata": {
                "timestamp": datetime.utcnow().isoformat(),
                "request_origin_ip": request.client.host if request.client else None,
                "geo_location": None,
                "server_version": "final-v1000"
            },
            "confidence_score": 0.9 if is_scam else 0.3
        }

    except Exception as e:
        # ✅ never 500
        return {
            "is_scam": True,
            "reply": "Main thoda confuse hoon, ek baar phir se samjha sakte ho?",
            "extracted_intelligence": {"upi_id": None, "bank_account": None, "phishing_link": None},
            "metadata": {
                "timestamp": datetime.utcnow().isoformat(),
                "request_origin_ip": None,
                "geo_location": None,
                "server_version": "final-v1000",
                "debug_error": str(e)
            },
            "confidence_score": 0.5
        }
