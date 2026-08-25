import re
with open('/home/ubuntu/Agent_Claudia_Autonomus/scripts/claudia_live_watchdog.py', 'r') as f:
    c = f.read()
pattern = re.compile(r'(now_str = datetime.now.*?WIB\").*?(# Determine Dominant Direction)', re.DOTALL)
replacement = r'''\1

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

    \2'''
c = re.sub(pattern, replacement, c)
c = c.replace('Price < EMA20', 'Price vs EMA20')
c = c.replace('Price > EMA20', 'Price vs EMA20')
with open('/home/ubuntu/Agent_Claudia_Autonomus/scripts/claudia_live_watchdog.py', 'w') as f:
    f.write(c)
print("Done regex patch")
