#!/usr/bin/env python3
"""
Clean & Professional Telegram DM Alert Templates & Tester
- OPEN Position Notification
- CLOSED Position Notification
- Slash Commands (/start, /status, /vault, /pnl)
Author: Gahar Inovasi Teknologi (Claudia Ultra)
"""
import os
import sys
import json
import urllib.request
from datetime import datetime, timezone, timedelta

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

TARGET_CHAT_ID = int(os.environ.get("TELEGRAM_CHAT_ID", "***CHAT_ID_REMOVED***"))
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN") or os.environ.get("TELEGRAM_GOLD_BOT_TOKEN") or os.environ.get("TELEGRAM_SERVER_BOT_TOKEN", "")

def get_open_position_msg(pair="SOL/USDC", direction="LONG", entry_price=149.80, size_sol=10.0, sl=148.90, tp=151.60):
    now_str = datetime.now(timezone(timedelta(hours=7))).strftime("%d %b, %H:%M WIB")
    notional = size_sol * entry_price
    sl_pct = ((sl - entry_price) / entry_price) * 100
    tp_pct = ((tp - entry_price) / entry_price) * 100
    
    return f"""<b>ORDER — POSITION OPEN</b>
<code>{now_str} • FVG Scalp</code>
─────────────────────

<b>POSITION DETAILS</b>
• Pair     : <code>{pair}</code>
• Direction: <code>{direction}</code>
• Entry    : <code>${entry_price:,.2f}</code>
• Size     : <code>{size_sol:.2f} SOL (${notional:,.1f})</code>
• Exposure : <code>14.8% Vault</code>

<b>RISK & TARGETS</b>
• Stop Loss  : <code>${sl:,.2f} ({sl_pct:+.1f}%)</code>
• Take Profit: <code>${tp:,.2f} ({tp_pct:+.1f}%)</code>
• RRR        : <code>1 : 2.0</code>

<b>CONFIRMATION</b>
[x] 15m Trend: Bullish
[x] FVG Zone : $149.60-$149.90
[x] Volatility: ATR 1.82

─────────────────────
<b>Tx:</b> <a href="https://solscan.io">solscan.io/open_tx</a>
<i>Claudia Ultra Engine</i>"""

def get_closed_position_msg(pair="SOL/USDC", direction="LONG", entry_price=149.80, exit_price=151.60, size_sol=10.0, net_pnl=17.88):
    now_str = datetime.now(timezone(timedelta(hours=7))).strftime("%d %b, %H:%M WIB")
    pnl_sol = net_pnl / exit_price
    pnl_pct = ((exit_price - entry_price) / entry_price) * 100
    
    return f"""<b>SETTLEMENT — CLOSED</b>
<code>{now_str} • TP Hit (18m)</code>
─────────────────────

<b>PERFORMANCE</b>
• Pair     : <code>{pair} ({direction})</code>
• Entry    : <code>${entry_price:,.2f}</code>
• Exit     : <code>${exit_price:,.2f}</code>
• Size     : <code>{size_sol:.2f} SOL</code>

<b>FINANCIAL RESULT</b>
• Net PnL  : <code>+${net_pnl:,.2f} ({pnl_pct:+.2f}%)</code>
• Yield SOL: <code>+{pnl_sol:.4f} SOL</code>
• Gas/Tip  : <code>-$0.12 (Jito)</code>

<b>VAULT STATUS</b>
• Total AUM: <code>$10,160.68</code>
• Exposure : <code>0.00% (In Vault)</code>
• 24h PnL  : <code>+$160.68 (+1.6%)</code>

─────────────────────
<b>Tx:</b> <a href="https://solscan.io">solscan.io/close_tx</a>
<i>Claudia Ultra Engine</i>"""

def get_help_slash_msg():
    return """<b>ZOLU ASSET VAULT</b>
<code>Claudia Ultra Terminal</code>
─────────────────────

<b>DAFTAR PERINTAH</b>
• <code>/saldo</code> : Saldo & total profit
• <code>/status</code>: Status & harga aktif
• <code>/user</code>  : Porsi modal investor
• <code>/report</code>: Laporan per jam
• <code>/help</code>  : Panduan terminal

─────────────────────
<i>Gahar Inovasi Teknologi</i>"""

def get_saldo_slash_msg(vault_aum_usd=10160.68, initial_deposit=10000.00, realized_pnl=160.68, sol_price=150.25):
    now_str = datetime.now(timezone(timedelta(hours=7))).strftime("%d %b, %H:%M WIB")
    vault_sol = vault_aum_usd / sol_price
    pnl_pct = (realized_pnl / initial_deposit) * 100
    
    return f"""<b>VAULT — SALDO & PROFIT</b>
<code>Updated : {now_str}</code>
─────────────────────

<b>RINGKASAN MODAL</b>
• Modal Awal : <code>${initial_deposit:,.2f}</code>
• Nilai Vault: <code>${vault_aum_usd:,.2f}</code>
  (~{vault_sol:.2f} SOL)
• Total PnL  : <code>+${realized_pnl:,.2f} (+{pnl_pct:.2f}%)</code>

<b>DISTRIBUSI ASET</b>
• USDC (Cash): <code>$8,500.00 (83.7%)</code>
• SOL (Asset): <code>11.05 SOL ($1,660)</code>
• Exposure   : <code>0.00% (Settled)</code>

─────────────────────
<i>Claudia Ultra Engine</i>"""

def get_user_slash_msg(user_id=***CHAT_ID_REMOVED***, deposit_usd=10000.00, net_yield_usd=160.68):
    now_str = datetime.now(timezone(timedelta(hours=7))).strftime("%d %b, %H:%M WIB")
    return f"""<b>VAULT — INVESTOR INFO</b>
<code>Updated : {now_str}</code>
─────────────────────

<b>PROFIL INVESTOR</b>
• ID   : <code>{user_id}</code>
• Nama : <code>Muhammad Hanafi</code>
• Akun : <code>Tier-1 Investor</code>

<b>PORSI & ALOKASI</b>
• Porsi Modal : <code>100.00%</code>
• Deposit     : <code>${deposit_usd:,.2f}</code>
• Skema       : <code>Pro-Rata Modal</code>
• Total Yield : <code>+${net_yield_usd:,.2f}</code>
• Penarikan   : <code>Instant On-Chain</code>

─────────────────────
<i>Claudia Ultra Governance</i>"""

def get_status_slash_msg(sol_price=150.25):
    now_str = datetime.now(timezone(timedelta(hours=7))).strftime("%d %b, %H:%M WIB")
    return f"""<b>VAULT — STATUS ENGINE</b>
<code>Updated : {now_str}</code>
─────────────────────

<b>STATUS OPERASIONAL</b>
• Engine: <code>ONLINE (Radar)</code>
• Pair  : <code>SOL/USDC (15m)</code>
• Index : <code>SOL ${sol_price:,.2f}</code>

<b>RENTANG HARGA AKTIF</b>
• Support   : <code>$149.20-$149.80</code>
• Resistance: <code>$151.80-$152.40</code>
• Trend     : <code>Bullish (EMA20>50)</code>
• Risk Lock : <code>Max 1.5%/Trade</code>

─────────────────────
<i>Claudia Ultra Telemetry</i>"""

def send_msg(text):
    if not BOT_TOKEN:
        print("[!] BOT_TOKEN missing.")
        return False
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = json.dumps({
        "chat_id": TARGET_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }).encode("utf-8")
    try:
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            print(f"[✓] Sent successfully (Status {resp.status})")
            return True
    except Exception as e:
        print(f"[!] Send error: {e}")
        return False

if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "all"
    if action in ["open", "all"]:
        print("--- SENDING OPEN POSITION NOTIFICATION ---")
        send_msg(get_open_position_msg())
    if action in ["close", "all"]:
        print("--- SENDING CLOSED POSITION NOTIFICATION ---")
        send_msg(get_closed_position_msg())
    if action in ["help", "all"]:
        print("--- SENDING SLASH COMMAND HELP ---")
        send_msg(get_help_slash_msg())
    if action in ["saldo", "all"]:
        print("--- SENDING SLASH COMMAND SALDO ---")
        send_msg(get_saldo_slash_msg())
    if action in ["status", "all"]:
        print("--- SENDING SLASH COMMAND STATUS ---")
        send_msg(get_status_slash_msg())
    if action in ["user", "all"]:
        print("--- SENDING SLASH COMMAND USER ---")
        send_msg(get_user_slash_msg())
