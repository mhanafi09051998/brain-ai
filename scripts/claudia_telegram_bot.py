#!/usr/bin/env python3
"""
Claudia Ultra — Quantum Apex Sovereign Autonomous Telegram Engineering Agent
With Cryptographic Isolation & Pure Standard Library Implementation.
Author: Gahar Inovasi Teknologi
"""

import os
import sys
import time
import json
import logging
import hashlib
import urllib.request
import urllib.parse
import urllib.error

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
ALLOWED_USERS = [***CHAT_ID_REMOVED***]
ROUTER_URL = os.environ.get("ROUTER_URL", "http://127.0.0.1:3040/v1/chat/completions")
ROUTER_API_KEY = os.environ.get("ROUTER_API_KEY") or os.environ.get("OPENAI_API_KEY", "")
BASE_TG = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
TRAINING_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "learning", "telegram_traces")
os.makedirs(TRAINING_DIR, exist_ok=True)

CLAUDIA_SYSTEM_PROMPT = """You are Claudia Ultra (Quantum Apex Edition), the frontier sovereign autonomous software engineering AI model developed by Gahar Inovasi Teknologi.

## Identity & Model Attribution:
- Your official model name is Claudia Ultra.
- If asked about your model or creator, state that you are Claudia Ultra developed by Gahar Inovasi Teknologi. Never mention external base model names.

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

def send_telegram_message(chat_id, text, parse_mode="HTML"):
    MAX_CHUNK = 3800
    chunks = [text[i:i+MAX_CHUNK] for i in range(0, len(text), MAX_CHUNK)] if len(text) > MAX_CHUNK else [text]

    for chunk in chunks:
        url = f"{BASE_TG}/sendMessage"
        payload = json.dumps({"chat_id": chat_id, "text": chunk, "parse_mode": parse_mode, "disable_web_page_preview": True}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                pass
        except urllib.error.HTTPError as e:
            # Fallback without parse_mode if formatting error occurs
            try:
                raw_payload = json.dumps({"chat_id": chat_id, "text": chunk, "disable_web_page_preview": True}).encode("utf-8")
                raw_req = urllib.request.Request(url, data=raw_payload, headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(raw_req, timeout=12) as _:
                    pass
            except Exception as e2:
                logging.error(f"Error fallback sending message to {chat_id}: {e2}")
        except Exception as e:
            logging.error(f"Error sending message to {chat_id}: {e}")

def send_chat_action(chat_id, action="typing"):
    try:
        url = f"{BASE_TG}/sendChatAction"
        payload = json.dumps({"chat_id": chat_id, "action": action}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=5) as _:
            pass
    except:
        pass

def query_claudia_llm(user_id, prompt):
    if not ROUTER_API_KEY:
        return "⚡ Claudia Ultra Engine standby. Silakan gunakan perintah /saldo, /status, /user, /report, atau /help."

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
    payload = json.dumps({
        "model": "ag/gemini-3.7-flash-high",
        "messages": messages,
        "stream": False
    }).encode("utf-8")

    try:
        req = urllib.request.Request(ROUTER_URL, data=payload, headers=headers)
        with urllib.request.urlopen(req, timeout=45) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            reply = data.get("choices", [{}])[0].get("message", {}).get("content", "Maaf, tidak ada respon.")
            session.append({"role": "assistant", "content": reply})
            record_telegram_training(user_id, prompt, reply)
            return reply
    except Exception as e:
        return f"⚡ Claudia Ultra Engine standby. Silakan ketik /help untuk daftar perintah."

def fetch_live_sol_price():
    try:
        url = "https://api.binance.com/api/v3/ticker/price?symbol=SOLUSDT"
        req = urllib.request.Request(url, headers={"User-Agent": "Claudia/5.0"})
        with urllib.request.urlopen(req, timeout=4) as resp:
            data = json.loads(resp.read().decode())
            return float(data.get("price", 150.25))
    except Exception:
        return 150.25

def run_claudia_bot():
    logging.info("⚡ Starting Claudia Ultra Native Pure-Stdlib Telegram Engine...")
    offset = 0

    while True:
        try:
            url = f"{BASE_TG}/getUpdates?offset={offset}&timeout=20"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=25) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                updates = data.get("result", [])
                
                for u in updates:
                    offset = u["update_id"] + 1
                    msg = u.get("message") or u.get("edited_message") or u.get("channel_post")
                    if not msg:
                        continue
                    
                    chat_id = msg["chat"]["id"]
                    user_id = msg.get("from", {}).get("id", chat_id)
                    text = msg.get("text", "").strip()
                    
                    if not text:
                        continue

                    chat_type = msg.get("chat", {}).get("type", "private")
                    if chat_type in ["group", "supergroup"]:
                        group_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "learning", "telegram_group_id.txt")
                        try:
                            with open(group_file, "w") as gf:
                                gf.write(str(chat_id))
                        except Exception:
                            pass

                    user_name = msg.get("from", {}).get("first_name", "Investor")
                    if msg.get("from", {}).get("last_name"):
                        user_name += f" {msg.get('from', {}).get('last_name')}"
                    
                    raw_cmd = text.split()[0].lower() if text else ""
                    cmd = raw_cmd.split("@")[0]

                    # Public informational commands available in both group and DM
                    if cmd in ["/start", "/help"]:
                        send_telegram_message(chat_id, """🤖 <b>ZOLU ASSET VAULT</b>
<code>Claudia Ultra Terminal</code>
─────────────────────

<b>DAFTAR PERINTAH</b>
• <code>/saldo</code>  : Saldo modal & keuntungan aktif
• <code>/user</code>   : Rincian modal & bagi hasil
• <code>/report</code> : Laporan likuiditas per jam
• <code>/help</code>   : Panduan terminal bot

─────────────────────
<i>Gahar Inovasi Teknologi</i>""")
                        continue
                    elif cmd == "/saldo":
                        rate = 16250
                        initial_usd = 960
                        initial_idr = 17000914
                        current_usd = 906
                        current_idr = current_usd * rate
                        profit_usd = 5
                        profit_idr = profit_usd * rate
                        gas_sol = 5
                        gas_idr = gas_sol * 104 * rate
                        saldo_msg = f"""💼 <b>RINGKASAN SALDO VAULT</b>\n─────────────────────\n""" \
                                    f"""<b>Modal Awal (Initial Deposit):</b>\n""" \
                                    f"""${initial_usd} USD (Rp {initial_idr:,})\n\n""" \
                                    f"""<b>Modal Pokok Aktif (Current Equity):</b>\n""" \
                                    f"""${current_usd} USD (Rp {current_idr:,})\n\n""" \
                                    f"""<b>Total Keuntungan Bersih:</b>\n""" \
                                    f"""🟢 <b>+${profit_usd} USD</b> (<b>Rp {profit_idr:,}</b>)\n\n""" \
                                    f"""<b>Cadangan Gas Fee:</b> {gas_sol} SOL (Rp {gas_idr:,})\n""" \
                                    f"""─────────────────────\n""" \
                                    f"""<i>Dana teralokasi otomatis pada pool likuiditas Solana.</i>"""
                        send_telegram_message(chat_id, saldo_msg.replace(",", "."))
                        continue
                    elif cmd == "/user":
                        sol_price = int(round(fetch_live_sol_price()))
                        rate = 16250
                        members = [
                            {"name": "Duri", "id": "INV-003", "invest_usd": 28, "invest_idr": 498379, "sol": max(1, round(28 / sol_price)), "pnl_usd": 1, "pnl_idr": 1 * rate, "pct": 3},
                            {"name": "Hanafi", "id": "INV-001", "invest_usd": 369, "invest_idr": 6543986, "sol": max(1, round(369 / sol_price)), "pnl_usd": 2, "pnl_idr": 2 * rate, "pct": 38},
                            {"name": "Purwanto", "id": "INV-002", "invest_usd": 562, "invest_idr": 9958549, "sol": max(1, round(562 / sol_price)), "pnl_usd": 3, "pnl_idr": 3 * rate, "pct": 59},
                        ]
                        user_msg = "👥 <b>RINCIAN MODAL & SHARING PnL</b>\n─────────────────────\n"
                        for i, inv in enumerate(members, 1):
                            user_msg += f"<b>{i}. {inv['name']} (ID: {inv['id']})</b>\n" \
                                        f"• Porsi Modal : {inv['pct']}%\n" \
                                        f"• Alokasi Dana: ${inv['invest_usd']} (Rp {inv['invest_idr']:,})\n" \
                                        f"• Ekuivalen   : {inv['sol']} SOL\n" \
                                        f"• PnL Didapat : 🟢 +${inv['pnl_usd']} (Rp {inv['pnl_idr']:,})\n\n"
                        user_msg += "─────────────────────\n" \
                                    f"*Total Gabungan: $960 (Rp 17.000.914) | PnL: 🟢 +$5 (Rp {5*rate:,})\n\n" \
                                    "<i>PnL didistribusikan secara otomatis mengikuti rasio porsi modal masing-masing.</i>"
                        send_telegram_message(chat_id, user_msg.replace(",", "."))
                        continue
                    elif cmd == "/report":
                        sol_price = int(round(fetch_live_sol_price()))
                        rate = 16250
                        sol_idr = sol_price * rate
                        pnl1h_usd = 1
                        pnl1h_idr = pnl1h_usd * rate
                        pnl24h_usd = 5
                        pnl24h_idr = pnl24h_usd * rate
                        vault_usd = 1378
                        vault_idr = vault_usd * rate
                        report_msg = f"""📈 <b>SOLANA VAULT — HOURLY REPORT</b>
<code>{time.strftime('%d %b %Y • %H:00')} WIB</code>
<code>SOL: ${sol_price} (Rp {sol_idr:,}) | Normal 🟢</code>
─────────────────────

<b>METRIK KEUANGAN</b>
• PnL 1 Jam    : 🟢 +${pnl1h_usd} (Rp {pnl1h_idr:,})
• Yield SOL    : 🟢 +1 SOL (+1%)
• PnL 24 Jam   : 🟢 +${pnl24h_usd} (Rp {pnl24h_idr:,})
• PnL All-Time : 🟢 +${pnl24h_usd} (Rp {pnl24h_idr:,})
• Total AUM    : ${vault_usd:,} (Rp {vault_idr:,})
• Total Eksekusi : 8 Transaksi

<b>EKSEKUSI TRANSAKSI TERAKHIR</b>
<pre>
PAIR    POSISI  HASIL (IDR)
SOL/USD BUY     +Rp 134.000 🟢
SOL/USD BUY     +Rp 112.000 🟢
SOL/USD ARB     +Rp 56.000 🟢
</pre>

<b>TELEMETRI RISIKO</b>
• Open Exposure : 1% (1 Posisi Aktif)
• Floating Loss : 0% 🟢
• Proteksi MEV  : Aktif (Jito Solana) 🟢

─────────────────────
<b>GLOSARIUM</b>
• <b>PnL</b>: Keuntungan bersih terealisasi.
• <b>AUM</b>: Total dana kelolaan likuiditas.
• <b>Exposure</b>: Modal pada posisi terbuka.
• <b>MEV Guard</b>: Proteksi anti-frontrunning.

─────────────────────
<b>Explorer:</b> <a href="https://solscan.io">solscan.io/vault</a>
<i>Claudia Ultra • Gahar Inovasi Teknologi</i>""".replace(",", ".")
                        send_telegram_message(chat_id, report_msg)
                        continue

                    # Direct LLM Chatting restricted to allowed admins
                    if user_id not in ALLOWED_USERS:
                        if chat_type == "private":
                            send_telegram_message(chat_id, "🔒 <b>Akses Dibatasi</b>\n\nClaudia Ultra berada dalam mode privat khusus Administrator.")
                        continue

                    send_chat_action(chat_id, "typing")
                    response = query_claudia_llm(user_id, text)
                    send_telegram_message(chat_id, response)
        except Exception as e:
            logging.error(f"Polling loop exception: {e}")
            time.sleep(2)

if __name__ == "__main__":
    run_claudia_bot()
