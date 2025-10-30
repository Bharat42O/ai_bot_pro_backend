import os
import pyotp
from smartapi import SmartConnect
from fastapi import FastAPI

app = FastAPI()

# -----------------------------
# Load credentials from environment variables
# -----------------------------
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
CLIENT_ID = os.getenv("CLIENT_ID")
PASSWORD = os.getenv("PASSWORD")
TOTP_SECRET = os.getenv("TOTP_SECRET")

# -----------------------------
# Angel One login
# -----------------------------
try:
    if not all([API_KEY, API_SECRET, CLIENT_ID, PASSWORD, TOTP_SECRET]):
        raise ValueError("One or more environment variables are missing!")
from SmartApi import SmartConnect(api_key=API_KEY)
    totp = pyotp.TOTP(TOTP_SECRET).now()
    session_data = smart_api.generateSession(CLIENT_ID, PASSWORD, totp)
    print("✅ Logged in successfully with Angel One!")
except Exception as e:
    print("❌ Error connecting to Angel One:", e)

# -----------------------------
# FastAPI routes
# -----------------------------
@app.get("/")
def home():
    return {"message": "AI Bot Pro Backend is running successfully!"}

@app.get("/session")
def get_session():
    try:
        return {"status": "success", "data": session_data}
    except Exception as e:
        return {"status": "error", "message": str(e)}