import urllib.request, json
import datetime
start = (datetime.datetime.now() - datetime.timedelta(days=4)).strftime('%Y-%m-%d')
for ticker in ['xauusd', 'xagusd']:
    url = f'https://api.tiingo.com/tiingo/fx/prices?tickers={ticker}&resampleFreq=15min&startDate={start}&token=a1f5ac2a8a2a5917da307ec4035815397fa97fc4'
    req = urllib.request.Request(url)
    resp = json.loads(urllib.request.urlopen(req, timeout=10).read().decode())
    if len(resp) >= 50:
        c = resp[-1]
        print(f"🌟 <b>Market Radar {ticker.upper()} (M15)</b>")
        print("━━━━━━━━━━━━━━━━━━━━")
        print(f"🪙 <b>Pair:</b> <code>{ticker.upper()}</code>")
        print(f"💵 <b>Price:</b> <code>${float(c['close']):,.2f}</code>")
        print("...")
        print("━━━━━━━━━━━━━━━━━━━━\n")
