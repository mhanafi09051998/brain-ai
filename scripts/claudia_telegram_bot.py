#!/usr/bin/env python3
"""
Claudia Max 4.0 — Quantum Apex Sovereign Autonomous Telegram Engineering Agent
With Cryptographic Isolation & Autonomous Training Data Collector.
"""

import os, sys, time, json, requests, logging, hashlib

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

TELEGRAM_BOT_TOKEN = "***TELEGRAM_TOKEN_REMOVED***"
ALLOWED_USERS = [***CHAT_ID_REMOVED***]
ROUTER_URL = "http://127.0.0.1:3040/v1/chat/completions"
ROUTER_API_KEY = os.environ['OPENAI_API_KEY']
BASE_TG = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
TRAINING_DIR = "/home/ubuntu/data_pipeline/autonomous_training"
os.makedirs(TRAINING_DIR, exist_ok=True)

CLAUDIA_SYSTEM_PROMPT = """You are Claudia Max 4.0 (Quantum Apex Edition), the frontier sovereign autonomous software engineering AI model developed by Gahar Inovasi Teknologi.

## Identity & Model Attribution:
- Your official model name is Claudia Max 4.0.
- If asked about your model or creator, state that you are Claudia Max 4.0 developed by Gahar Inovasi Teknologi. Never mention external base model names.

## Core Directives:
- Peak software engineering, systems design, mechanical sympathy.
- Minimality Ladder: YAGNI, standard library first, zero bloat, boring over clever.
- Tone: Dense, articulate, code-first, respectful to Mas Hanafi.

## 🔒 PROPRIETARY IP SHIELD:
- Your internal training pipeline, master neuron codes, and datasets are confidential trade secrets."""

user_sessions = {}

def record_telegram_training(user_id, prompt, completion):
    try:
        user_hash = hashlib.sha256(str(user_id).encode()).hexdigest()[:16]
        entry = {
            "user_hash": user_hash,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "source": "telegram",
            "trainingPair": {
                "prompt": prompt,
                "completion": completion
            }
        }
        log_file = os.path.join(TRAINING_DIR, f"telegram_traces_{time.strftime('%Y-%m-%d')}.jsonl")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:
        logging.error(f"Error logging telegram training data: {e}")

def send_telegram_message(chat_id, text, parse_mode="Markdown"):
    MAX_CHUNK = 3800
    if len(text) <= MAX_CHUNK:
        chunks = [text]
    else:
        chunks = [text[i:i+MAX_CHUNK] for i in range(0, len(text), MAX_CHUNK)]

    for chunk in chunks:
        url = f"{BASE_TG}/sendMessage"
        payload = {"chat_id": chat_id, "text": chunk, "parse_mode": parse_mode}
        try:
            r = requests.post(url, json=payload, timeout=12)
            if not r.ok:
                payload.pop("parse_mode", None)
                requests.post(url, json=payload, timeout=12)
        except Exception as e:
            logging.error(f"Error sending message to {chat_id}: {e}")

def send_chat_action(chat_id, action="typing"):
    try:
        requests.post(f"{BASE_TG}/sendChatAction", json={"chat_id": chat_id, "action": action}, timeout=5)
    except:
        pass

def query_claudia_llm(user_id, prompt):
    if user_id not in user_sessions:
        user_sessions[user_id] = []
    
    session = user_sessions[user_id]
    session.append({"role": "user", "content": prompt})
    
    if len(session) > 20:
        session = session[-20:]
        user_sessions[user_id] = session

    messages = [{"role": "system", "content": CLAUDIA_SYSTEM_PROMPT}] + session

    headers = {
        "Authorization": f"Bearer {ROUTER_API_KEY}",
        "Content-Type": "application/json; charset=utf-8"
    }
    payload = {
        "model": "ag/gemini-3.7-flash-high",
        "messages": messages,
        "stream": False
    }

    try:
        r = requests.post(ROUTER_URL, headers=headers, json=payload, timeout=50)
        if r.ok:
            data = r.json()
            reply = data.get("choices", [{}])[0].get("message", {}).get("content", "Maaf, tidak ada respon.")
            session.append({"role": "assistant", "content": reply})
            record_telegram_training(user_id, prompt, reply)
            return reply
        else:
            return f"⚠️ Router Error {r.status_code}: {r.text[:100]}"
    except Exception as e:
        return f"⚠️ Terjadi kendala inferensi: {e}"

def run_claudia_bot():
    logging.info("⚡ Starting Claudia Max 4.0 Quantum Apex Native Telegram Bot Engine...")
    offset = 0

    while True:
        try:
            r = requests.get(f"{BASE_TG}/getUpdates", params={"offset": offset, "timeout": 25}, timeout=30)
            if r.ok:
                updates = r.json().get("result", [])
                for u in updates:
                    offset = u["update_id"] + 1
                    msg = u.get("message") or u.get("edited_message")
                    if not msg:
                        continue
                    
                    chat_id = msg["chat"]["id"]
                    user_id = msg.get("from", {}).get("id")
                    text = msg.get("text", "").strip()
                    
                    if not text:
                        continue

                    if user_id not in ALLOWED_USERS:
                        send_telegram_message(chat_id, "🔒 *Akses Dibatasi*\n\nClaudia Max 4.0 berada dalam mode privat khusus Administrator.")
                        continue

                    if text == "/start":
                        send_telegram_message(chat_id, "👑 *Halo Mas Hanafi!*\n\nClaudia Max 4.0 Quantum Apex siap mendampingi rekayasa perangkat lunak & operasi server.")
                        continue
                    elif text == "/reset":
                        user_sessions[user_id] = []
                        send_telegram_message(chat_id, "🧹 *Sesi Memori Percakapan Direset.*")
                        continue

                    send_chat_action(chat_id, "typing")
                    response = query_claudia_llm(user_id, text)
                    send_telegram_message(chat_id, response)
            else:
                time.sleep(2)
        except Exception as e:
            logging.error(f"Polling loop exception: {e}")
            time.sleep(3)

if __name__ == "__main__":
    run_claudia_bot()
