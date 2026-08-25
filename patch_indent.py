import re

file_path = 'scripts/claudia_live_watchdog.py'

with open(file_path, 'r') as f:
    c = f.read()

# Fix indentation of time.sleep
c = re.sub(r'[ \t]*time\.sleep\(POLL_INTERVAL_SEC\)', '        time.sleep(POLL_INTERVAL_SEC)', c)

with open(file_path, 'w') as f:
    f.write(c)
