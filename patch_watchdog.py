import sys

file_path = '/home/ubuntu/Agent_Claudia_Autonomus/scripts/claudia_live_watchdog.py'

with open(file_path, 'r') as f:
    content = f.read()

target = '    now_str = datetime.now(timezone(timedelta(hours=7))).strftime("%d %b %Y • %H:%M:%S WIB")'
replacement = '''    now_str = datetime.now(timezone(timedelta(hours=7))).strftime("%d %b %Y • %H:%M:%S WIB")

    trend_bull = ema20 > ema50
    trend_bear = ema20 < ema50
    price_above_ema = price > ema20
    price_below_ema = price < ema20
    rsi_bull_ok = 40 <= rsi <= 68
    rsi_bear_ok = 32 <= rsi <= 60
    fvg_bull = ind["bullish_fvg"]
    fvg_bear = ind["bearish_fvg"]
    atr_ok = atr >= 1.5
    
    bull_score = sum([trend_bull, price_above_ema, rsi_bull_ok, fvg_bull, atr_ok])
    bear_score = sum([trend_bear, price_below_ema, rsi_bear_ok, fvg_bear, atr_ok])
'''

if target in content:
    content = content.replace(target, replacement)
    
    content = content.replace('Price < EMA20', 'Price vs EMA20')
    content = content.replace('Price > EMA20', 'Price vs EMA20')
    
    with open(file_path, 'w') as f:
        f.write(content)
    print("Patched successfully")
else:
    print("Target not found")
