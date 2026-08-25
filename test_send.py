import sys, time; sys.path.append('/home/ubuntu/Agent_Claudia_Autonomus/scripts')
import claudia_live_watchdog as wd

candles = wd.fetch_klines_twelve('XAU/USD')
ind = wd.calc_indicators(candles)
price = ind['price']
atr = ind['atr']
rsi = ind['rsi']
ema20 = ind['ema20']
ema50 = ind['ema50']
now_str = wd.datetime.now(wd.timezone(wd.timedelta(hours=7))).strftime('%d %b %Y • %H:%M:%S WIB')

trend_bull = ema20 > ema50
trend_bear = ema20 < ema50
price_above_ema = price > ema20
price_below_ema = price < ema20
rsi_bull_ok = 40 <= rsi <= 68
rsi_bear_ok = 32 <= rsi <= 60
fvg_bull = ind['bullish_fvg']
fvg_bear = ind['bearish_fvg']
atr_ok = atr >= 1.5

bull_score = sum([trend_bull, price_above_ema, rsi_bull_ok, fvg_bull, atr_ok])
bear_score = sum([trend_bear, price_below_ema, rsi_bear_ok, fvg_bear, atr_ok])

if bull_score >= bear_score:
    direction = 'BUY (LONG)'
    score = bull_score
    is_bull = True
else:
    direction = 'SELL (SHORT)'
    score = bear_score
    is_bull = False

status_header = f'🛠️ <b>TEST NOTIFIKASI (Score: {score}/5)</b>'

fvg_str = f"({ind['fvg_zone']})" if ind.get('fvg_zone') else ''

if is_bull:
    check_txt = f"""{"✅" if trend_bull else "❌"} Trend Bullish
{"✅" if price_above_ema else "❌"} Price vs EMA20
{"✅" if rsi_bull_ok else "❌"} RSI: {rsi:.1f}
{"✅" if fvg_bull else "❌"} FVG Retest {fvg_str}
{"✅" if atr_ok else "❌"} Volatilitas"""
    sl = round(price - (1.5 * atr), 2)
    tp1 = round(price + (3.0 * atr), 2)
    tp2 = round(price + (4.5 * atr), 2)
else:
    check_txt = f"""{"✅" if trend_bear else "❌"} Trend Bearish
{"✅" if price_below_ema else "❌"} Price vs EMA20
{"✅" if rsi_bear_ok else "❌"} RSI: {rsi:.1f}
{"✅" if fvg_bear else "❌"} FVG Retest {fvg_str}
{"✅" if atr_ok else "❌"} Volatilitas"""
    sl = round(price + (1.5 * atr), 2)
    tp1 = round(price - (3.0 * atr), 2)
    tp2 = round(price - (4.5 * atr), 2)

msg = f"""🌟 <b>Market Radar GOLD (M15)</b>
━━━━━━━━━━━━━━━━━━━━
🪙 <b>Pair:</b> <code>XAUUSD</code>
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
━━━━━━━━━━━━━━━━━━━━"""
wd.send_telegram_msg(msg)
print('Test sent!')
