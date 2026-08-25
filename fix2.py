with open('/home/ubuntu/Agent_Claudia_Autonomus/scripts/claudia_live_watchdog.py', 'r') as f:
    c = f.read()
c = c.replace('WIB"', 'WIB")')
# Just to be safe if it was replaced multiple times:
c = c.replace('WIB"))', 'WIB")')
with open('/home/ubuntu/Agent_Claudia_Autonomus/scripts/claudia_live_watchdog.py', 'w') as f:
    f.write(c)
