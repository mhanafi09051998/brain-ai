import sys; sys.path.append('scripts')
import claudia_live_watchdog as wd

candles = wd.fetch_klines_twelve('XAU/USD')
ind = wd.calc_indicators(candles)
fvg_str = f"({ind['fvg_zone']})" if ind.get('fvg_zone') else ''
print(f"✅ FVG Retest {fvg_str}")
