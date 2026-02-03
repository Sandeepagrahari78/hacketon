from fastapi import FastAPI, Request
from datetime import datetime
import re
import json

app = FastAPI(title="Agentic Honey-Pot API", version="final")

def make_reply(upi_id, bank_account, phishing_link, is_scam):
    # If not scam, keep neutral
    if not is_scam:
        return "Theek hai, aap thoda detail me bata sakte ho kya? Main samajh nahi pa raha."

    # If scam but nothing extracted -> ask for details (honeypot behaviour)
    if not upi_id and not bank_account and not phishing_link:
        return "Main confused hoon. Payment kaise karna hai? UPI ID ya account number aur link bhej do please."

    # If link present but no payment handle
    if phishing_link and not upi_id and not bank_account:
        return "Link mil gaya. Par payment kispe karna hai—UPI ID ya account number? Please share."

    # If UPI present but no link
    if upi_id and not phishing_link:
        return f"UPI ID ({upi_id}) mil gaya. Link bhi bhej do aur kitna amount send karna hai?"

    # If bank present but no IFSC (we won't ask IFSC if you want to avoid, but it's realistic)
    if bank_account and not phishing_link:
        return f"Account number ({bank_account}) mil gaya. Link bhi bhej do aur amount kitna hai?"

    # If everything present
    return "Theek hai, ek baar confirm kar do—main link par fill karu ya direct payment karu? Amount bhi bata do."

def build_response(message: str, request: Request):
    msg_lower = (message or "").lower()
    scam_keywords = ["account", "blocked", "verify", "upi", "link", "bank", "urgent", "kyc", "suspend"]
    is_scam = any(word in msg_lower for word in scam_keywords)

    url_pattern = r"https?://[a-zA-Z0-9./?=_-]+"
    upi_pattern = r"\b[\w.-]+@[\w.-]+\b"
    bank_pattern = r"\b\d{9,18}\b"

    links = re.findall(url_pattern, message or "")
    upi_ids = re.findall(upi_pattern, message or "")
    bank_accounts = re.findall(bank_pattern, message or "")

    upi_id = upi_ids[0] if upi_ids else None
    bank_account = bank_accounts[0] if bank_accounts else None
    phishing_link = links[0] if links else None

    reply_text = make_reply(upi_id, bank_account, phishing_link, is_scam)

    return {
        "is_scam": is_scam,
        "reply": reply_text,
        "extracted_intelligence": {
            "upi_id": upi_id,
            "bank_account": bank_account,
            "phishing_link": phishing_link
        },
        "metadata": {
            "timestamp": datetime.utcnow().isoformat(),
            "request_origin_ip": request.client.host if request.client else None,
            "geo_location": None,
            "server_version": "final-v999"
        },
        "confidence_score": 0.9 if is_scam else 0.3
    }

def safe_extract_message(raw_bytes: bytes) -> str:
    message = "System validation ping"
    if not raw_bytes:
        return message

    try:
        text = raw_bytes.decode("utf-8", errors="ignore").strip()
        if not text:
            return message

        data = json.loads(text)

        if isinstance(data, dict):
            return data.get("message") or data.get("text") or data.get("input") or message
        if isinstance(data, str) and data.strip():
            return data.strip()

        return message
    except Exception:
        text = raw_bytes.decode("utf-8", errors="ignore").strip()
        return text if text else message

@app.api_route("/", methods=["GET", "HEAD"])
async def health_check(request: Request):
    return {"status": "active", "system": "Agentic Honey-Pot", "version": "final-v999"}

@app.api_route("/analyze", methods=["GET", "HEAD"])
async def analyze_get(request: Request):
    return build_response("System validation ping", request)

@app.post("/analyze")
async def analyze_post(request: Request):
    raw = await request.body()
    message = safe_extract_message(raw)
    return build_response(message, request)
