# main_module.py

from datetime import datetime
from input_module import InputModule
from transit_walker_module import TransitWalker
from d1d9_core_module import get_dms, get_nav

# 1. Initialization
# Define birth reference and transit start parameters here
birth_dt = datetime(1990, 5, 15, 12, 0) 
hub = InputModule(lat=57.1, lon=12.2, dt_birth=birth_dt)

# 2. Execution
walker = TransitWalker(hub)

# 3. Output
print(f"{'Body':<6} {'D1 (Rasi)':<15} {'D9 (Navamsa)':<15}")
print("-" * 38)

for timestamp, transit_chart in walker.walk(duration_days=7, interval_minutes=5):
    print(f"\n--- Transit Time: {timestamp} ---")
    for body_name, lon in transit_chart:
        print(f"{body_name:<6} {get_dms(lon):<15} {get_nav(lon)[0]} {get_nav(lon)[1]:.2f}°")
