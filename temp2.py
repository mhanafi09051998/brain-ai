import sys; sys.path.append('/home/ubuntu/Agent_Claudia_Autonomus/scripts')
import claudia_live_watchdog as wd

candles = wd.fetch_klines_twelve('XAU/USD')
ind = wd.calc_indicators(candles)
price = ind['price']
atr = ind['atr']
rsi = ind['rsi']
ema20 = ind['ema20']
ema50 = ind['ema50']

trend_bear = ema20 < ema50
price_below_ema = price < ema20
rsi_bear_ok = 32 <= rsi <= 60
fvg_bear = ind['bearish_fvg']
atr_ok = atr >= 1.5

score = sum([trend_bear, price_below_ema, rsi_bear_ok, fvg_bear, atr_ok])
print(f"Price: ${price:,.2f}")
print(f"RSI: {rsi:.1f}")
print(f"Score: {score}/5")
print(f"FVG Zone: {ind['fvg_zone']}")
