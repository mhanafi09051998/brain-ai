import re

file_path = 'scripts/claudia_live_watchdog.py'
with open(file_path, 'r') as f: c = f.read()

replacement = '''import datetime
    start = (datetime.datetime.now() - datetime.timedelta(days=4)).strftime('%Y-%m-%d')
    url = f"https://api.tiingo.com/tiingo/fx/prices?tickers={ticker}&resampleFreq=15min&startDate={start}&token={TIINGO_TOKEN}"'''

c = c.replace('url = f"https://api.tiingo.com/tiingo/fx/prices?tickers={ticker}&resampleFreq=15min&token={TIINGO_TOKEN}"', replacement)

with open(file_path, 'w') as f: f.write(c)
