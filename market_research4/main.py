from datetime import datetime
from zoneinfo import ZoneInfo
import swisseph as swe
from d1d9_core import compute, print_chart
from transit_engine import TransitEngine

# Configuration
RASI = ["Ar", "Ta", "Ge", "Cn", "Le", "Vi", "Li", "Sc", "Sg", "Cp", "Aq", "Pi"]
LOCATION = (59.90870, 10.74779)
NATAL_TIME = datetime(1995, 1, 28, 9, 0, 0, tzinfo=ZoneInfo("Europe/Oslo"))

def dms(lon):
    lon = lon % 360
    sign = int(lon // 30)
    d = lon % 30
    deg = int(d)
    m = int((d - deg) * 60)
    s = int((((d - deg) * 60) - m) * 60)
    return RASI[sign], deg, m, s

def show_chart(chart, title="CHART"):
    print(f"\n=== {title} ===\nUTC: {chart['utc']}\nLagna: {dms(chart['asc'])}")
    for k, v in chart["planets"].items():
        s, d, m, sec = dms(v["lon"])
        print(f"{k:>2}  {s:>2}  {d:02d}°{m:02d}'{sec:02d}\" | D9: {RASI[v['d9']]}")

def run_analysis(transit_dt):
    natal = compute(NATAL_TIME, *LOCATION)
    engine = TransitEngine(natal)
    engine.load(transit_dt, *LOCATION)
    
    show_chart(natal, "NATAL CHART")
    # Assuming your TransitEngine has a .report() or similar method
    engine.report() 

if __name__ == "__main__":
    print(f"Swiss Ephemeris Version: {swe.version}")
    target_date = datetime(2026, 6, 20, 9, 0, 0, tzinfo=ZoneInfo("Europe/Oslo"))
    run_analysis(target_date)
