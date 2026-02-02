import requests
import json

# FastAPI endpoint
URL = "http://127.0.0.1:8000/analyze"

# Test scam message (judge-friendly)
payload = {
    "message": "Your bank account is blocked. Please click this link to verify: http://fakebank-verify.com"
}

headers = {
    "Content-Type": "application/json"
}

print("📤 Sending request to API...\n")

try:
    response = requests.post(URL, headers=headers, data=json.dumps(payload))
    
    print("Status Code:", response.status_code)
    print("\n📥 Response JSON:\n")
    
    print(json.dumps(response.json(), indent=2))

except Exception as e:
    print("❌ Error while calling API:", str(e))
