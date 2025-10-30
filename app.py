from fastapi import FastAPI
from SmartApi import SmartConnect
import os, pyotp

app = FastAPI()

# --- Load environment variables ---
api_key = os.getenv("API_KEY") or os.getenv("ANGLE_API_KEY")
client_id = os.getenv("CLIENT_ID")
password = os.getenv("PASSWORD") or os.getenv("ANGLE_PASSWORD")
totp_secret = os.getenv("TOTP_SECRET")

# --- Initialize SmartApi session ---
obj = None
try:
    otp = pyotp.TOTP(totp_secret).now()
    obj = SmartConnect(api_key)
    session_data = obj.generateSession(client_id, password, otp)
    print("✅ Logged in successfully with Angel One!")
except Exception as e:
    print(f"❌ Error logging in: {e}")

# --- Routes ---
@app.get("/")
def read_root():
    return {"status": "ok"}

@app.head("/")
def head_root():
    return {"status": "ok"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/check_balance")
def check_balance():
    if not obj:
        return {"status": "error", "message": "SmartApi not initialized"}
    try:
        balance = obj.rmsLimit()
        return {"status": "success", "balance": balance}
    except Exception as e:
        return {"status": "error", "message": str(e)}
