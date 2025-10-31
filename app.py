from fastapi import FastAPI
from SmartApi import SmartConnect
from SmartApi.smartWebSocketV2 import SmartWebSocketV2
import os, pyotp, random, pandas as pd
import ta
from ta.momentum import RSIIndicator
from ta.trend import MACD
from ta.volatility import BollingerBands

app = FastAPI()

# --- Load environment variables ---
api_key = os.getenv("API_KEY") or os.getenv("ANGLE_API_KEY")
client_id = os.getenv("CLIENT_ID")
password = os.getenv("PASSWORD") or os.getenv("ANGLE_PASSWORD")
totp_secret = os.getenv("TOTP_SECRET")

# --- Initialize SmartApi session ---
obj = None
FEED_TOKEN = None
try:
    otp = pyotp.TOTP(totp_secret).now()
    obj = SmartConnect(api_key)
    session_data = obj.generateSession(client_id, password, otp)
    print("✅ Logged in successfully with Angel One!")
    print("Session Data:", session_data)

    # Safe way to get feedToken
    FEED_TOKEN = session_data.get("feedToken") or session_data.get("data", {}).get("feedToken")
    if not FEED_TOKEN:
        print("❌ feedToken is missing — WebSocket won't work")
    else:
        print("✅ feedToken is ready:", FEED_TOKEN)

except Exception as e:
    print(f"❌ Error logging in: {e}")

# --- WebSocket Setup ---
latest_ticks = {}

if FEED_TOKEN:jwt_token = session_data.get("jwtToken") or session_data.get("data", {}).get("jwtToken")
sws = SmartWebSocketV2(FEED_TOKEN, client_id, api_key, jwt_token)

    def on_data(wsapp, message):
        token = message.get("token")
        price = message.get("ltp")
        latest_ticks[token] = price
        print(f"📡 Tick for {token}: {price}")

    def on_open(wsapp):
        print("✅ WebSocket Connected")
        sws.subscribe([
            {"exchangeType": 1, "token": "99926000"},  # NIFTY
            {"exchangeType": 1, "token": "99926001"}   # SENSEX
        ])

    sws.on_open = on_open
    sws.on_data = on_data
    sws.connect()

# --- Routes ---
@app.get("/")
def home():
    return {
        "message": "Welcome to AI Bot Pro Backend!",
        "routes": [
            "/health", "/check_balance", "/signals/deep", "/signals/multi/latest",
            "/analysis", "/option_chain", "/ai_signal", "/price_action",
            "/live_feed", "/strategy_signal", "/coach_advice"
        ]
    }

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
        "macd": {"value": 1.12, "signal": 0.98, "histogram": 0.14},
        "bollinger_bands": {"upper": 19850, "middle": 19500, "lower": 19150},
        "volume_analysis": {
            "current_volume": 1200000,
            "average_volume": 950000,
            "volume_spike": True
        },
        "sentiment": {"news_sentiment": "Positive", "social_sentiment": "Neutral"},
        "risk_management": {
            "stop_loss": "19350", "take_profit": "19850", "risk_reward_ratio": 2.5
        },
        "notes": [
            "MACD crossover confirms bullish bias",
            "Volume spike supports breakout",
            "Positive news sentiment from major financial outlets"
        ]
    }

def fetch_candle_data(symbol: str) -> pd.DataFrame:
    data = {"close": [19500, 19520, 19510, 19530, 19550, 19540, 19560, 19570, 19580, 19590]}
    return pd.DataFrame(data)

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
        "bollinger": {"upper": round(upper, 2), "lower": round(lower, 2)}
    }

@app.get("/signals/multi/latest")
def multi_signal():
    symbols = ["NIFTY 50", "SENSEX", "RELIANCE", "BANKNIFTY"]
    return [get_signal(symbol) for symbol in symbols]

@app.get("/analysis")
def analysis():
    return {
        "mistakes": ["Overtrading", "No stop loss", "Ignoring trend"],
        "suggestions": [
            "Use stop loss", "Trade less frequently",
            "Follow the dominant trend", "Avoid revenge trading"
        ]
    }

@app.get("/option_chain")
def option_chain(symbol: str = "NIFTY"):
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
    signal_strength = 8.7
    bias = "BUY" if signal_strength > 6 else "SELL"
    return {
        "symbol": symbol,
        "ai_signal": bias,
        "confidence": f"{signal_strength}/10",
        "indicators": {
            "rsi": 62.3, "macd": 1.14,
            "volume_spike": True, "trend": "UP", "sentiment": "Positive"
        },
        "note": "AI model suggests bullish momentum with strong volume and positive sentiment"
    }

@app.get("/price_action")
def price_action(symbol: str = "NIFTY"):
    data = {
        "open": [100, 102, 101, 105, 107],
        "high": [103, 104, 103, 108, 109],
        "low": [99, 100, 100, 104, 106],
        "close": [102, 101, 105, 107, 108]
    }
    df = pd.DataFrame(data)
    patterns = []

    for i in range(len(df)):
        o, h, l, c = df["open"][i], df["high"][i], df["low"][i], df["close"][i]
        body = abs(c - o)
        range_ = h - l

        if body < 0.2 and range_ > 1.5:
            patterns.append("Doji")
        elif c > o and (o - l) > body * 2:
            patterns.append("Hammer")
        elif i > 0:
            prev_o, prev_c = df["open"][i - 1], df["close"][i - 1]
            if c > o and o < prev_c and c > prev_o:
                patterns.append("Bullish Engulfing")
            elif c < o and o > prev_c and c < prev_o:
                patterns.append("Bearish Engulfing")
            else:
                patterns.append("None")
        else:
            patterns.append("None")

    df["pattern"] = patterns

    return {
        "symbol": symbol,
        "candlestick_patterns": df["pattern"].tolist(),
        "note": "Basic price action analysis using simulated OHLC data"
    }
