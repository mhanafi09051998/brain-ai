import re

file_path = '/home/ubuntu/Agent_Claudia_Autonomus/scripts/claudia_live_watchdog.py'

with open(file_path, 'r') as f:
    c = f.read()

c = c.replace(
    'url = f"https://api.twelvedata.com/time_series?symbol={target_symbol}&interval={twelve_interval}&outputsize={limit}&apikey={TWELVE_API_KEY}"',
    'url = f"https://api.twelvedata.com/time_series?symbol={target_symbol}&interval={twelve_interval}&outputsize={limit}&apikey={TWELVE_API_KEY}&timezone=Asia/Jakarta"'
)

with open(file_path, 'w') as f:
    f.write(c)
