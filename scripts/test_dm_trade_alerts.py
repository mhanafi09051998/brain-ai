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
    now_str = datetime.now(timezone(timedelta(hours=7))).strftime("%d %b %Y, %H:%M:%S WIB")
    notional = size_sol * entry_price
    sl_pct = ((sl - entry_price) / entry_price) * 100
    tp_pct = ((tp - entry_price) / entry_price) * 100
    
    return f"""<b>EXECUTION ORDER — POSITION OPENED</b>
<code>Timestamp : {now_str}</code>
<code>Strategy  : Scalp FVG Liquidity Retest</code>
──────────────────────────

<b>POSITION DETAILS</b>
• Pair        : <code>{pair}</code>
• Direction   : <code>{direction} (Buy)</code>
• Entry Price : <code>${entry_price:,.2f}</code>
• Position    : <code>{size_sol:.2f} SOL (${notional:,.2f})</code>
• Exposure    : <code>14.77% of Vault AUM</code>

<b>RISK & TARGET LEVELS</b>
• Stop Loss   : <code>${sl:,.2f} ({sl_pct:+.2f}%)</code>
• Take Profit : <code>${tp:,.2f} ({tp_pct:+.2f}%)</code>
• Risk/Reward : <code>1 : 2.0</code>

<b>TECHNICAL CONFIRMATIONS</b>
[x] 15m Trend: Bullish (EMA20 > EMA50)
[x] Liquidity: FVG Retest ($149.60 - $149.90)
[x] Volatility: ATR 1.82 (Nominal)

──────────────────────────
<b>Transaction:</b> <a href="https://solscan.io">solscan.io/tx/sample_open_sig</a>
<i>Claudia Ultra Engine • Automated Trade Dispatch</i>"""

def get_closed_position_msg(pair="SOL/USDC", direction="LONG", entry_price=149.80, exit_price=151.60, size_sol=10.0, net_pnl=17.88):
    now_str = datetime.now(timezone(timedelta(hours=7))).strftime("%d %b %Y, %H:%M:%S WIB")
    pnl_sol = net_pnl / exit_price
    pnl_pct = ((exit_price - entry_price) / entry_price) * 100
    
    return f"""<b>TRADE SETTLEMENT — POSITION CLOSED</b>
<code>Timestamp : {now_str}</code>
<code>Duration  : 18m 23s</code>
<code>Exit Type : TAKE PROFIT (Limit Filled)</code>
──────────────────────────

<b>TRADE PERFORMANCE</b>
• Pair         : <code>{pair} ({direction})</code>
• Entry Price  : <code>${entry_price:,.2f}</code>
• Exit Price   : <code>${exit_price:,.2f}</code>
• Position Size: <code>{size_sol:.2f} SOL</code>

<b>FINANCIAL RESULT</b>
• Gross Profit : <code>+${(exit_price - entry_price) * size_sol:,.2f}</code>
• Gas & Fees   : <code>-$0.12 (Jito Priority Tip)</code>
• Net Realized : <code>+${net_pnl:,.2f} ({pnl_pct:+.2f}%)</code> | <code>+{pnl_sol:.4f} SOL</code>

<b>VAULT STATUS POST-SETTLEMENT</b>
• Current AUM  : <code>$10,160.68</code>
• Open Exposure: <code>0.00% (100% In Vault)</code>
• 24h Realized : <code>+$160.68 (+1.58%)</code>

──────────────────────────
<b>Transaction:</b> <a href="https://solscan.io">solscan.io/tx/sample_close_sig</a>
<i>Claudia Ultra Engine • Automated Trade Dispatch</i>"""

def get_help_slash_msg():
    return """<b>ZOLU ASSET VAULT — CONTROL TERMINAL</b>
<code>Engine : Claudia Ultra Quantitative Router</code>
──────────────────────────

<b>DAFTAR PERINTAH</b>
• <code>/saldo</code>  : Lihat ringkasan saldo modal dan keuntungan.
• <code>/status</code> : Lihat status engine dan rentang harga aktif.
• <code>/user</code>   : Lihat sharing porsi modal & profit investor.
• <code>/report</code> : Laporan berkala kinerja likuiditas per jam.
• <code>/help</code>   : Menampilkan daftar panduan perintah terminal.

──────────────────────────
<i>Gahar Inovasi Teknologi • Quantitative Asset Management</i>"""

def get_saldo_slash_msg(vault_aum_usd=10160.68, initial_deposit=10000.00, realized_pnl=160.68, sol_price=150.25):
    now_str = datetime.now(timezone(timedelta(hours=7))).strftime("%d %b %Y, %H:%M WIB")
    vault_sol = vault_aum_usd / sol_price
    pnl_pct = (realized_pnl / initial_deposit) * 100
    
    return f"""<b>ZOLU ASSET VAULT — SALDO & KEUNTUNGAN</b>
<code>Updated : {now_str}</code>
──────────────────────────

<b>RINGKASAN MODAL (AUM)</b>
• Modal Awal    : <code>${initial_deposit:,.2f}</code>
• Nilai Vault   : <code>${vault_aum_usd:,.2f}</code> (~{vault_sol:.2f} SOL)
• Total Profit  : <code>+${realized_pnl:,.2f} (+{pnl_pct:.2f}%)</code>

<b>DISTRIBUSI ASET</b>
• USDC (Cash)   : <code>$8,500.00 (83.66%)</code>
• SOL (Asset)   : <code>11.05 SOL (~$1,660.68)</code>
• Open Exposure : <code>0.00% (Cash Settled)</code>

──────────────────────────
<i>Claudia Ultra Engine • Transparency Verified</i>"""

def get_user_slash_msg(user_id=***CHAT_ID_REMOVED***, deposit_usd=10000.00, net_yield_usd=160.68):
    now_str = datetime.now(timezone(timedelta(hours=7))).strftime("%d %b %Y, %H:%M WIB")
    return f"""<b>ZOLU ASSET VAULT — INVESTOR SHARING</b>
<code>Updated : {now_str}</code>
──────────────────────────

<b>PROFIL INVESTOR</b>
• Telegram ID   : <code>{user_id}</code>
• Investor Name : <code>Muhammad Hanafi</code>
• Status Akun   : <code>Verified Tier-1 Investor</code>

<b>PORSI MODAL & PROFIT SHARING</b>
• Porsi Modal   : <code>100.00% (${deposit_usd:,.2f} Deposit)</code>
• Profit Sharing: <code>80% Investor / 20% Engine Performance</code>
• Akumulasi PnL : <code>+${net_yield_usd:,.2f} Net Yield</code>
• Hak Penarikan : <code>Instant Withdrawal On-Chain</code>

──────────────────────────
<i>Claudia Ultra Engine • Investor Governance</i>"""

def get_status_slash_msg(sol_price=150.25):
    now_str = datetime.now(timezone(timedelta(hours=7))).strftime("%d %b %Y, %H:%M WIB")
    return f"""<b>ZOLU ASSET VAULT — STATUS ENGINE & HARGA</b>
<code>Updated : {now_str}</code>
──────────────────────────

<b>STATUS OPERASIONAL</b>
• Engine State   : <code>ONLINE (Radar Active)</code>
• Target Pair    : <code>SOL/USDC (15m Timeframe)</code>
• Live Index     : <code>SOL/USD ${sol_price:,.2f}</code>

<b>RENTANG HARGA AKTIF</b>
• Support / FVG  : <code>$149.20 - $149.80</code>
• Resistance     : <code>$151.80 - $152.40</code>
• Trend Baseline : <code>Bullish (EMA20 > EMA50)</code>
• Risk Lock      : <code>Max 1.5% Risk per Entry</code>

──────────────────────────
<i>Claudia Ultra Engine • Live Telemetry</i>"""

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
