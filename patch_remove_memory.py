import re

file_path = 'scripts/claudia_live_watchdog.py'

with open(file_path, 'r') as f:
    c = f.read()

# Remove check_memory_and_restart from the code
c = re.sub(r'def check_memory_and_restart\(\):.*?except: pass', '', c, flags=re.DOTALL)
c = re.sub(r'MEMORY_LIMIT_MB = 450\.0\n', '', c)
c = re.sub(r'check_memory_and_restart\(\)\n', '', c)

with open(file_path, 'w') as f:
    f.write(c)
