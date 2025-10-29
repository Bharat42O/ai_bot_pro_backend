# backend/app.py
from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
import uvicorn
import sqlite3
import os
import json
from typing import List

from SmartApi import SmartConnect
import os

# Angel One credentials from environment variables
api_key = os.getenv("ANGEL_API_KEY")
client_id = os.getenv("CLIENT_ID")
api_secret = os.getenv("ANGEL_API_SECRET")

# Connect to Angel One SmartAPI
smartApi = SmartConnect(api_key)

try:
    data = smartApi.generateSession(client_id, api_secret)
    refreshToken = data['data']['refreshToken']
    feedToken = smartApi.getfeedToken()
    print("Feed token:", feedToken)

    # Example: Get NIFTY 50 live data
    nifty_data = smartApi.ltpData("NSE", "NIFTY 50", "26000")
    print("NIFTY:", nifty_data)

except Exception as e:
    print("Error connecting to Angel One:", e)


# Simple backend to store trade lines and respond to chat queries using stored docs
DB_FILE = 'knowledge.db'

app = FastAPI(title='AI Bot Pro Backend')

# init DB
def init_db():
    con = sqlite3.connect(DB_FILE)
    con.execute('''CREATE TABLE IF NOT EXISTS docs (id INTEGER PRIMARY KEY, source TEXT, text TEXT)''')
    con.commit(); con.close()

init_db()

@app.post('/ingest/csv')
async def ingest_csv(file: UploadFile = File(...)):
    content = (await file.read()).decode('utf-8', errors='ignore')
    lines = [l.strip() for l in content.splitlines() if l.strip()]
    con = sqlite3.connect(DB_FILE)
    for line in lines:
        con.execute('INSERT INTO docs (source,text) VALUES (?,?)', ('trades', line))
    con.commit(); con.close()
    return {'status':'ok', 'lines': len(lines)}

class QueryReq(BaseModel):
    q: str

# simple retrieval: return last N docs
def last_docs(n=6):
    con = sqlite3.connect(DB_FILE)
    cur = con.execute('SELECT text FROM docs ORDER BY id DESC LIMIT ?', (n,))
    rows = [r[0] for r in cur.fetchall()]
    con.close()
    return rows

@app.post('/query')
async def query(req: QueryReq):
    q = req.q
    ctx = last_docs(6)
    # Simple RAG-style reply (MVP). Later we can hook OpenAI or local LLM.
    answer = 'I checked your recent trades and market facts:\n' + '\n'.join(ctx[:4]) + f"\n\nYou asked: {q}\n\n(Reply: This is the MVP assistant — connect an LLM for richer answers.)"
    return {'answer': answer, 'sources': ctx}

@app.get('/')
def root():
    return {'status':'backend running'}

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
