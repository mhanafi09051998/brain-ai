import sys
sys.path.append('/home/ubuntu/Agent_Claudia_Autonomus/scripts')
import claudia_live_watchdog as wd

res = wd.scan_gold_market()
print("Result of scan:", res)
