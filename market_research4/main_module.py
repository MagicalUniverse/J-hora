from datetime import datetime
from input_module import InputModule
from transit_walker_module import TransitWalker
from d1d9_core_module import get_chart_data, get_dms
from scanner_module import TransitScanner

# 1. Setup
birth_dt = datetime(1990, 5, 15, 12, 0)
hub = InputModule(lat=57.1, lon=12.2, dt_birth=birth_dt)
birth_chart = get_chart_data(birth_dt, hub) # The reference point

# 2. Initialize Engine & Scanner
walker = TransitWalker(hub)
scanner = TransitScanner(birth_chart, orb=0.5)

# 3. Process
print(f"{'Time':<20} {'Event'}")
for timestamp, transit_chart in walker.walk(duration_days=7, interval_minutes=5):
    alerts = scanner.scan(transit_chart)
    for t_body, b_body, b_lon, t_lon in alerts:
        print(f"{str(timestamp):<20} {t_body} conjunct {b_body} at {get_dms(t_lon)}")
