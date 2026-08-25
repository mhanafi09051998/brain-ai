import re

file_path = '/home/ubuntu/Agent_Claudia_Autonomus/scripts/claudia_live_watchdog.py'

with open(file_path, 'r') as f:
    c = f.read()

old_logic = '''    for i in range(len(candles)-10, len(candles)-1):
        if candles[i]["low"] > candles[i-2]["high"] and (candles[i]["low"] - candles[i-2]["high"] > 0.2 * atr):
            if curr <= candles[i]["low"] + (0.2 * atr):
                bull_fvg = True
                fvg_zone = f"${candles[i-2]['high']:.2f} - ${candles[i]['low']:.2f}"
        if candles[i]["high"] < candles[i-2]["low"] and (candles[i-2]["low"] - candles[i]["high"] > 0.2 * atr):
            if curr >= candles[i]["high"] - (0.2 * atr):
                bear_fvg = True
                fvg_zone = f"${candles[i]['high']:.2f} - ${candles[i-2]['low']:.2f}"'''

new_logic = '''    for i in range(len(candles)-10, len(candles)-1):
        if candles[i]["low"] > candles[i-2]["high"] and (candles[i]["low"] - candles[i-2]["high"] > 0.2 * atr):
            fvg_zone = f"${candles[i-2]['high']:.2f} - ${candles[i]['low']:.2f}"
            if curr <= candles[i]["low"] + (0.2 * atr):
                bull_fvg = True
        if candles[i]["high"] < candles[i-2]["low"] and (candles[i-2]["low"] - candles[i]["high"] > 0.2 * atr):
            fvg_zone = f"${candles[i]['high']:.2f} - ${candles[i-2]['low']:.2f}"
            if curr >= candles[i]["high"] - (0.2 * atr):
                bear_fvg = True'''

c = c.replace(old_logic, new_logic)

with open(file_path, 'w') as f:
    f.write(c)
