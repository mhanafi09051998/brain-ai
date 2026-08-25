import re

file_path = '/home/ubuntu/Agent_Claudia_Autonomus/scripts/claudia_live_watchdog.py'

with open(file_path, 'r') as f:
    c = f.read()

# 1. Update calc_indicators to return fvg_top and fvg_bottom
old_calc_fvg = '''    bull_fvg = bear_fvg = False
    fvg_zone = ""
    for i in range(len(candles)-10, len(candles)-1):
        if candles[i]["low"] > candles[i-2]["high"] and (candles[i]["low"] - candles[i-2]["high"] > 0.2 * atr):
            fvg_zone = f"${candles[i-2]['high']:.2f} - ${candles[i]['low']:.2f}"
            if curr <= candles[i]["low"] + (0.2 * atr):
                bull_fvg = True
        if candles[i]["high"] < candles[i-2]["low"] and (candles[i-2]["low"] - candles[i]["high"] > 0.2 * atr):
            fvg_zone = f"${candles[i]['high']:.2f} - ${candles[i-2]['low']:.2f}"
            if curr >= candles[i]["high"] - (0.2 * atr):
                bear_fvg = True
            
    return {
        "price": curr,
        "ema20": ema20,
        "ema50": ema50,
        "rsi": rsi,
        "atr": atr,
        "bullish_fvg": bull_fvg,
        "bearish_fvg": bear_fvg,
        "fvg_zone": fvg_zone
    }'''

new_calc_fvg = '''    bull_fvg = bear_fvg = False
    fvg_zone = ""
    fvg_top = fvg_bottom = None
    for i in range(len(candles)-10, len(candles)-1):
        if candles[i]["low"] > candles[i-2]["high"] and (candles[i]["low"] - candles[i-2]["high"] > 0.2 * atr):
            fvg_top = candles[i]["low"]
            fvg_bottom = candles[i-2]["high"]
            fvg_zone = f"${fvg_bottom:.2f} - ${fvg_top:.2f}"
            if curr <= fvg_top + (0.2 * atr):
                bull_fvg = True
        if candles[i]["high"] < candles[i-2]["low"] and (candles[i-2]["low"] - candles[i]["high"] > 0.2 * atr):
            fvg_top = candles[i-2]["low"]
            fvg_bottom = candles[i]["high"]
            fvg_zone = f"${fvg_bottom:.2f} - ${fvg_top:.2f}"
            if curr >= fvg_bottom - (0.2 * atr):
                bear_fvg = True
            
    return {
        "price": curr,
        "ema20": ema20,
        "ema50": ema50,
        "rsi": rsi,
        "atr": atr,
        "bullish_fvg": bull_fvg,
        "bearish_fvg": bear_fvg,
        "fvg_zone": fvg_zone,
        "fvg_top": fvg_top,
        "fvg_bottom": fvg_bottom
    }'''

c = c.replace(old_calc_fvg, new_calc_fvg)

# 2. Update scan_asset to construct limit_plan
old_msg_template = '''    msg_template = f"""🌟 <b>Market Radar {asset['id']} (M15)</b>
━━━━━━━━━━━━━━━━━━━━
🪙 <b>Pair:</b> <code>{asset['pair']}</code>
⏱️ <code>{now_str}</code>
💵 <b>Price:</b> <code>${price:,.2f}</code>

{status_header}
🧭 <b>Bias:</b> <b>{direction}</b>

<b>[ Parameter Checklist ]</b>
{check_txt}

<b>[ Action Plan ]</b>
🎯 <b>Entry:</b> <code>{price:.2f}</code>
🛑 <b>SL:</b> <code>{sl:.2f}</code>
🏆 <b>TP1 (1:3):</b> <code>{tp1:.2f}</code>
🚀 <b>TP2 (1:4.5):</b> <code>{tp2:.2f}</code>
━━━━━━━━━━━━━━━━━━━━"""'''

new_msg_template = '''    limit_plan = ""
    if ind.get("fvg_top") and ind.get("fvg_bottom"):
        if is_bull:
            l_entry = ind["fvg_top"]
            l_sl = ind["fvg_bottom"] - (0.5 * atr)
            l_tp = l_entry + (3.0 * atr)
            limit_plan = f"\\n\\n<b>[ Limit Order Plan ]</b>\\n🛒 <b>Buy Limit:</b> <code>{l_entry:.2f}</code>\\n🛑 <b>SL (Luar Zona):</b> <code>{l_sl:.2f}</code>\\n🏆 <b>TP (1:3):</b> <code>{l_tp:.2f}</code>"
        else:
            l_entry = ind["fvg_bottom"]
            l_sl = ind["fvg_top"] + (0.5 * atr)
            l_tp = l_entry - (3.0 * atr)
            limit_plan = f"\\n\\n<b>[ Limit Order Plan ]</b>\\n🛒 <b>Sell Limit:</b> <code>{l_entry:.2f}</code>\\n🛑 <b>SL (Luar Zona):</b> <code>{l_sl:.2f}</code>\\n🏆 <b>TP (1:3):</b> <code>{l_tp:.2f}</code>"

    msg_template = f"""🌟 <b>Market Radar {asset['id']} (M15)</b>
━━━━━━━━━━━━━━━━━━━━
🪙 <b>Pair:</b> <code>{asset['pair']}</code>
⏱️ <code>{now_str}</code>
💵 <b>Price:</b> <code>${price:,.2f}</code>

{status_header}
🧭 <b>Bias:</b> <b>{direction}</b>

<b>[ Parameter Checklist ]</b>
{check_txt}

<b>[ Market Execution Plan ]</b>
🎯 <b>Entry Sekarang:</b> <code>{price:.2f}</code>
🛑 <b>SL:</b> <code>{sl:.2f}</code>
🏆 <b>TP1:</b> <code>{tp1:.2f}</code>{limit_plan}
━━━━━━━━━━━━━━━━━━━━"""'''

c = c.replace(old_msg_template, new_msg_template)

with open(file_path, 'w') as f:
    f.write(c)
