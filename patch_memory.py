import re

file_path = '/home/ubuntu/Agent_Claudia_Autonomus/scripts/claudia_live_watchdog.py'

with open(file_path, 'r') as f:
    c = f.read()

# Change MEMORY_LIMIT_MB from 450.0 to 16000.0 (16GB) to prevent spam loop
c = re.sub(r'MEMORY_LIMIT_MB\s*=\s*450\.0', 'MEMORY_LIMIT_MB = 16000.0', c)

with open(file_path, 'w') as f:
    f.write(c)
