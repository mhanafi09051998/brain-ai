import sys; sys.path.append('scripts')
import claudia_live_watchdog as wd

for asset in wd.ASSETS:
    if asset['source'] == 'tiingo':
        candles = wd.fetch_klines_tiingo(asset['ticker'])
    else:
        candles = wd.fetch_klines_yahoo(asset['ticker'])
    if not candles: continue
    ind = wd.calc_indicators(candles)
    if not ind: continue
    price = ind['price']
    print(f"Asset: {asset['pair']} | Price: ${price:,.2f}")
    
    # Render template logic for testing
    import time
    from datetime import datetime, timezone, timedelta
    atr = ind["atr"]
    rsi = ind["rsi"]
    ema20 = ind["ema20"]
    ema50 = ind["ema50"]
    now_str = datetime.now(timezone(timedelta(hours=7))).strftime("%d %b %Y • %H:%M:%S WIB")
    trend_bull = ema20 > ema50
    trend_bear = ema20 < ema50
    price_above_ema = price > ema20
    price_below_ema = price < ema20
    rsi_bull_ok = 40 <= rsi <= 68
    rsi_bear_ok = 32 <= rsi <= 60
    fvg_bull = ind["bullish_fvg"]
    fvg_bear = ind["bearish_fvg"]
    atr_ok = atr >= 1.5 if asset["id"] == "GOLD" else True

    bull_score = sum([trend_bull, price_above_ema, rsi_bull_ok, fvg_bull, atr_ok])
    bear_score = sum([trend_bear, price_below_ema, rsi_bear_ok, fvg_bear, atr_ok])
    score = max(bull_score, bear_score)
    is_bull = bull_score >= bear_score
    direction = "BUY (LONG)" if is_bull else "SELL (SHORT)"
    
    status_header = f"🔥 <b>EKSEKUSI ({score}/5)</b>" if score == 5 else f"⚠️ <b>SIAGA ({score}/5)</b>"
    
    msg_template = f"""🌟 <b>Market Radar {asset['id']} (M15)</b>
━━━━━━━━━━━━━━━━━━━━
🪙 <b>Pair:</b> <code>{asset['pair']}</code>
⏱️ <code>{now_str}</code>
💵 <b>Price:</b> <code>${price:,.2f}</code>

{status_header}
🧭 <b>Bias:</b> <b>{direction}</b>

<b>[ Parameter Checklist ]</b>
✅ Trend {"Bullish" if is_bull else "Bearish"}
✅ Price vs EMA20
✅ RSI: {rsi:.1f}
✅ FVG Retest
✅ Volatilitas

<b>[ Action Plan ]</b>
🎯 <b>Entry:</b> <code>{price:.2f}</code>
━━━━━━━━━━━━━━━━━━━━"""
    print(msg_template)
    print("-" * 40)
