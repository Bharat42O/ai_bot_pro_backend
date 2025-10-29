from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
import uvicorn
import sqlite3
import os
import pyotp
from typing import List
from SmartApi import SmartConnect

# ===================================================
# 🌐 Angel One SmartAPI Setup
# ===================================================
api_key = os.getenv("ANGEL_API_KEY")
client_id = os.getenv("ANGEL_CLIENT_ID")
password = os.getenv("ANGEL_PASSWORD")
totp_secret = os.getenv("ANGEL_TOTP")

smartApi = None
feedToken = None

def connect_angel():
    global smartApi, feedToken
    try:
        totp = pyotp.TOTP(totp_secret).now()
        smartApi = SmartConnect(api_key=api_key)
        data = smartApi.generateSession(client_id, password, totp)
        feedToken = smartApi.getfeedToken()
        print("✅ Connected to Angel One successfully!")
        print("Feed Token:", feedToken)
        return True
    except Exception as e:
        print("❌ Error connecting to Angel One:", e)
        return False

# ===================================================
# 🧠 SQLite Knowledge DB Setup
# ===================================================
DB_FILE = 'knowledge.db'

def init_db():
    con = sqlite3.connect(DB_FILE)
    con.execute('''CREATE TABLE IF NOT EXISTS docs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source TEXT,
        text TEXT
    )''')
    con.commit()
    con.close()

init_db()

# ===================================================
# 🚀 FastAPI App
# ===================================================
app = FastAPI(title="AI Bot Pro Backend")

@app.on_event("startup")
async def startup_event():
    connect_angel()

@app.get("/")
def root():
    return {"status": "backend running ✅"}

# ===================================================
# 📥 Ingest CSV Endpoint
# ===================================================
@app.post("/ingest/csv")
async def ingest_csv(file: UploadFile = File(...)):
    content = (await file.read()).decode("utf-8", errors="ignore")
    lines = [l.strip() for l in content.splitlines() if l.strip()]
    con = sqlite3.connect(DB_FILE)
    for line in lines:
        con.execute("INSERT INTO docs (source,text) VALUES (?,?)", ("trades", line))
    con.commit()
    con.close()
    return {"status": "ok", "lines": len(lines)}

# ===================================================
# 💬 Query Endpoint
# ===================================================
class QueryReq(BaseModel):
    q: str

def last_docs(n=6):
    con = sqlite3.connect(DB_FILE)
    cur = con.execute("SELECT text FROM docs ORDER BY id DESC LIMIT ?", (n,))
    rows = [r[0] for r in cur.fetchall()]
    con.close()
    return rows

@app.post("/query")
async def query(req: QueryReq):
    q = req.q
    ctx = last_docs(6)
    answer = (
        "I checked your recent trades and market facts:\n"
        + "\n".join(ctx[:4])
        + f"\n\nYou asked: {q}\n\n(Reply: This is the MVP assistant — connect an LLM for richer answers.)"
    )
    return {"answer": answer, "sources": ctx}

# ===================================================
# ⚡ Angel Connection Check Endpoint
# ===================================================
@app.get("/connect")
def connect_check():
    ok = connect_angel()
    if ok:
        return {"message": "Connected successfully 🎉", "feedToken": feedToken}
    else:
        return {"error": "Failed to connect to Angel One"}

# ===================================================
# 🏁 Run Locally
# ===================================================
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
