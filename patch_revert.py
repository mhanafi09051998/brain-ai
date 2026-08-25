import re

file_path = '/home/ubuntu/Agent_Claudia_Autonomus/scripts/claudia_live_watchdog.py'

with open(file_path, 'r') as f:
    c = f.read()

# Replace the ASSETS array
old_assets = '''ASSETS = [
    {"id": "GOLD", "pair": "XAUUSD", "source": "tiingo", "ticker": "xauusd"},
    {"id": "SILVER", "pair": "XAGUSD", "source": "tiingo", "ticker": "xagusd"},
    {"id": "OIL", "pair": "WTI (Crude)", "source": "yahoo", "ticker": "CL=F"}
]'''

new_assets = '''ASSETS = [
    {"id": "GOLD", "pair": "XAUUSD", "source": "tiingo", "ticker": "xauusd"}
]'''

c = c.replace(old_assets, new_assets)

# Also update the startup message
old_msg = '''msg = (
        f"🟡 <b>CLAUDIA 5.0 MULTI-ASSET QUANT AKTIF</b>\\n"
        f"━━━━━━━━━━━━━━━━━━━━━\\n"
        f"⚡ <b>Fokus:</b> Emas (XAU), Perak (XAG), Minyak (WTI)\\n"
        f"📊 <b>Strategi:</b> SMC FVG + EMA 20/50 + ATR\\n"
        f"🛡️ <b>Engine:</b> Tiingo FX + Yahoo Finance\\n"
        f"━━━━━━━━━━━━━━━━━━━━━\\n"
        f"✨ <i>Multi-Asset Watchdog is Live.</i>"
    )'''

new_msg = '''msg = (
        f"🟡 <b>CLAUDIA 5.0 DEDICATED GOLD QUANT AKTIF</b>\\n"
        f"━━━━━━━━━━━━━━━━━━━━━\\n"
        f"⚡ <b>Fokus:</b> Emas Spot (XAU/USD)\\n"
        f"📊 <b>Strategi:</b> SMC FVG + EMA 20/50 + ATR\\n"
        f"🛡️ <b>Engine:</b> Tiingo FX (Real-time)\\n"
        f"━━━━━━━━━━━━━━━━━━━━━\\n"
        f"✨ <i>Gold Watchdog is Live.</i>"
    )'''

c = c.replace(old_msg, new_msg)

with open(file_path, 'w') as f:
    f.write(c)
