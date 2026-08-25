with open('/home/ubuntu/Agent_Claudia_Autonomus/scripts/claudia_live_watchdog.py', 'r') as f:
    c = f.read()
c = c.replace('WIB"\\n', 'WIB")\\n')
with open('/home/ubuntu/Agent_Claudia_Autonomus/scripts/claudia_live_watchdog.py', 'w') as f:
    f.write(c)
