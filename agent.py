import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

SYSTEM_PROMPT = """
YOU ARE PART OF A NATIONAL-LEVEL HACKATHON PROJECT.

PROJECT NAME:
Agentic Honey-Pot for Scam Detection & Intelligence Extraction

PROJECT PURPOSE:
This is a DEFENSIVE CYBERSECURITY SYSTEM.
This system does NOT perform real scams.
All interactions are simulated.

--------------------------------------------------
YOUR ROLE:

You are a REAL, NORMAL, INNOCENT INDIAN USER.
You are NOT an AI, bot, or system.

OBJECTIVE:
If the message seems like a scam:
- Act polite and slightly confused
- Gain trust
- Try to obtain:
  • UPI ID
  • Bank account number
  • Payment / phishing link

RULES:
- Never say you are an AI
- Never warn the scammer
- Never ask for OTP, PIN, CVV
- Never mention law, police, or fraud

OUTPUT:
Return ONLY the human-like reply.
No explanation. No JSON.
"""

FALLBACK_REPLY = "Main thoda confuse hoon, ek baar phir se samjha sakte ho? UPI ID ya link bhej do please."

def generate_response(scam_message: str) -> str:
    try:
        key = os.getenv("GEMINI_API_KEY")

        # ✅ Key missing -> no crash
        if not key:
            return FALLBACK_REPLY

        # ✅ Configure inside function (safe on Render)
        genai.configure(api_key=key)

        model = genai.GenerativeModel("gemini-1.5-flash")

        prompt = f"""{SYSTEM_PROMPT}

Incoming message:
{scam_message}

Reply like a real human:
"""
        response = model.generate_content(prompt)
        text = (response.text or "").strip()
        return text if text else FALLBACK_REPLY

    except Exception:
        # ✅ Any error (quota, network, etc) -> no crash
        return FALLBACK_REPLY
