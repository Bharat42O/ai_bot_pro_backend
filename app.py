from fastapi import FastAPI
from SmartApi import SmartConnect
import os, pyotp
import pandas as pd
import pandas_ta as ta

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

# --- Health Routes ---
@app.get("/")
def read_root():
    return {"status": "ok"}

@app.head("/")
def head_root():
    return {"status": "ok"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# --- Balance Route (optional) ---
@app.get("/check_balance")
def check_balance():
    if not obj:
        return {"status": "error", "message": "SmartApi not initialized"}
    try:
        balance = obj.rmsLimit()
        return {"status": "success", "balance": balance}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# --- Deep Signal Route ---
@app.get("/signals/deep")
def signals_deep(symbol: str):
    return {
        "symbol": symbol,
        "bias": "BUY",
        "confluence_score": 8.2,
        "rsi": 67.4,
        "atr": 1.35,
        "trend": "UP",
        "option_suggestion": {
            "strike": "19600",
            "type": "CALL",
            "note": "Strong bullish momentum with volume confirmation"
        },
        "macd": {
            "value": 1.12,
            "signal": 0.98,
            "histogram": 0.14
        },
        "bollinger_bands": {
            "upper": 19850,
            "middle": 19500,
            "lower": 19150
        },
        "volume_analysis": {
            "current_volume": 1200000,
            "average_volume": 950000,
            "volume_spike": True
        },
        "sentiment": {
            "news_sentiment": "Positive",
            "social_sentiment": "Neutral"
        },
        "risk_management": {
            "stop_loss": "19350",
            "take_profit": "19850",
            "risk_reward_ratio": 2.5
        },
        "notes": [
            "MACD crossover confirms bullish bias",
            "Volume spike supports breakout",
            "Positive news sentiment from major financial outlets"
        ]
    }

# --- Multi-Symbol Signal Route ---
def fetch_candle_data(symbol: str) -> pd.DataFrame:
    data = {
        "close": [19500, 19520, 19510, 19530, 19550, 19540, 19560, 19570, 19580, 19590]
    }
    df = pd.DataFrame(data)
    return df

def get_signal(symbol: str):
    df = fetch_candle_data(symbol)
    rsi = ta.rsi(df['close'], length=14).iloc[-1]
    macd = ta.macd(df['close'])
    macd_val = macd['MACD_12_26_9'].iloc[-1]
    macd_signal = macd['MACDs_12_26_9'].iloc[-1]
    bb = ta.bbands(df['close'])
    upper = bb['BBU_20_2.0'].iloc[-1]
    lower = bb['BBL_20_2.0'].iloc[-1]

    signal = "HOLD"
    if rsi < 30 and macd_val > macd_signal:
        signal = "BUY"
    elif rsi > 70 and macd_val < macd_signal:
        signal = "SELL"

    return {
        "symbol": symbol,
        "signal": signal,
        "rsi": round(rsi, 2),
        "macd": round(macd_val, 2),
        "bollinger": {
            "upper": round(upper, 2),
            "lower": round(lower, 2)
        }
    }

@app.get("/signals/multi/latest")
def multi_signal():
    symbols = ["NIFTY 50", "SENSEX", "RELIANCE", "BANKNIFTY"]
    results = [get_signal(symbol) for symbol in symbols]
    return results

# --- Analysis Route ---
@app.get("/analysis")
def analysis():
    return {
        "mistakes": ["Overtrading", "No stop loss", "Ignoring trend"],
        "suggestions": [
            "Use stop loss",
            "Trade less frequently",
            "Follow the dominant trend",
            "Avoid revenge trading"
        ]
    }
@app.get("/option_chain")
def option_chain(symbol: str = "NIFTY"):
    # Dummy data — replace with SmartAPI option chain fetch
    option_data = {
        "19600": {"call_oi": 120000, "put_oi": 80000},
        "19700": {"call_oi": 95000, "put_oi": 110000},
        "19800": {"call_oi": 70000, "put_oi": 130000},
        "19900": {"call_oi": 50000, "put_oi": 90000},
    }

    max_call = max(option_data.items(), key=lambda x: x[1]["call_oi"])
    max_put = max(option_data.items(), key=lambda x: x[1]["put_oi"])

    return {
        "symbol": symbol,
        "max_call_strike": max_call[0],
        "max_call_oi": max_call[1]["call_oi"],
        "max_put_strike": max_put[0],
        "max_put_oi": max_put[1]["put_oi"],
        "note": f"Strong resistance at {max_call[0]}, support at {max_put[0]}"
    }
@app.get("/ai_signal")
def ai_signal(symbol: str = "NIFTY"):
    # Simulated AI logic — replace with real model later
    signal_strength = 8.7  # out of 10
    bias = "BUY" if signal_strength > 6 else "SELL"

    return {
        "symbol": symbol,
        "ai_signal": bias,
        "confidence": f"{signal_strength}/10",
        "indicators": {
            "rsi": 62.3,
            "macd": 1.14,
            "volume_spike": True,
            "trend": "UP",
            "sentiment": "Positive"
        },
        "note": "AI model suggests bullish momentum with strong volume and positive sentiment"
    }
