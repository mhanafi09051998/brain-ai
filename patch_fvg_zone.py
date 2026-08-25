import re

file_path = 'scripts/claudia_live_watchdog.py'
with open(file_path, 'r') as f:
    c = f.read()

# Replace the FVG logic in calc_indicators
old_fvg_logic = '''    bull_fvg = bear_fvg = False
    for i in range(len(candles)-10, len(candles)-1):
        if candles[i]["low"] > candles[i-2]["high"] and (candles[i]["low"] - candles[i-2]["high"] > 0.2 * atr):
            if curr <= candles[i]["low"] + (0.2 * atr): bull_fvg = True
        if candles[i]["high"] < candles[i-2]["low"] and (candles[i-2]["low"] - candles[i]["high"] > 0.2 * atr):
            if curr >= candles[i]["high"] - (0.2 * atr): bear_fvg = True
            
    return {
        "price": curr,
        "ema20": ema20,
        "ema50": ema50,
        "rsi": rsi,
        "atr": atr,
        "bullish_fvg": bull_fvg,
        "bearish_fvg": bear_fvg
    }'''

new_fvg_logic = '''    bull_fvg = bear_fvg = False
    fvg_zone = ""
    for i in range(len(candles)-10, len(candles)-1):
        if candles[i]["low"] > candles[i-2]["high"] and (candles[i]["low"] - candles[i-2]["high"] > 0.2 * atr):
            if curr <= candles[i]["low"] + (0.2 * atr):
                bull_fvg = True
                fvg_zone = f"${candles[i-2]['high']:.2f} - ${candles[i]['low']:.2f}"
        if candles[i]["high"] < candles[i-2]["low"] and (candles[i-2]["low"] - candles[i]["high"] > 0.2 * atr):
            if curr >= candles[i]["high"] - (0.2 * atr):
                bear_fvg = True
                fvg_zone = f"${candles[i]['high']:.2f} - ${candles[i-2]['low']:.2f}"
            
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

c = c.replace(old_fvg_logic, new_fvg_logic)

# Replace the Telegram template checklist formatting
old_bull_check = '''        check_txt = f"""{"✅" if trend_bull else "❌"} Trend Bullish
{"✅" if price_above_ema else "❌"} Price vs EMA20
{"✅" if rsi_bull_ok else "❌"} RSI: {rsi:.1f}
{"✅" if fvg_bull else "❌"} FVG Retest
{"✅" if atr_ok else "❌"} Volatilitas"""'''

new_bull_check = '''        fvg_str = f"({ind['fvg_zone']})" if ind.get("fvg_zone") else ""
        check_txt = f"""{"✅" if trend_bull else "❌"} Trend Bullish
{"✅" if price_above_ema else "❌"} Price vs EMA20
{"✅" if rsi_bull_ok else "❌"} RSI: {rsi:.1f}
{"✅" if fvg_bull else "❌"} FVG Retest {fvg_str}
{"✅" if atr_ok else "❌"} Volatilitas"""'''

old_bear_check = '''        check_txt = f"""{"✅" if trend_bear else "❌"} Trend Bearish
{"✅" if price_below_ema else "❌"} Price vs EMA20
{"✅" if rsi_bear_ok else "❌"} RSI: {rsi:.1f}
{"✅" if fvg_bear else "❌"} FVG Retest
{"✅" if atr_ok else "❌"} Volatilitas"""'''

new_bear_check = '''        fvg_str = f"({ind['fvg_zone']})" if ind.get("fvg_zone") else ""
        check_txt = f"""{"✅" if trend_bear else "❌"} Trend Bearish
{"✅" if price_below_ema else "❌"} Price vs EMA20
{"✅" if rsi_bear_ok else "❌"} RSI: {rsi:.1f}
{"✅" if fvg_bear else "❌"} FVG Retest {fvg_str}
{"✅" if atr_ok else "❌"} Volatilitas"""'''

c = c.replace(old_bull_check, new_bull_check)
c = c.replace(old_bear_check, new_bear_check)

with open(file_path, 'w') as f:
    f.write(c)
