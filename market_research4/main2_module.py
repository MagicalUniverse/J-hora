"""
SCRIPT NAME: main2_module.py
PURPOSE: Astrology Calculation Engine
VERSION: 2.2.0
"""

# SECTION 1: IMPORTS
import sys
import swisseph as swe
from datetime import datetime, timezone

# SECTION 2: CONFIGURATION AND CONSTANTS
# Fixed: 'sa' removed from RASI to prevent conflict with Saturn
RASI = ["ar", "ta", "ge", "cn", "le", "vi", "li", "sc", "sg", "cp", "aq", "pi"]
PLANETS = {"Su": swe.SUN, "Mo": swe.MOON, "Ma": swe.MARS, "Me": swe.MERCURY, 
           "Ju": swe.JUPITER, "Ve": swe.VENUS, "Sa": swe.SATURN, "Ra": swe.MEAN_NODE}

# SECTION 3: MATH UTILITIES
def get_dms(lon):
    d = int(lon % 30); m = int((lon * 60) % 60); s = int((lon * 3600) % 60)
    return f"{d:02}°{m:02}'{s:02}''"

def get_nav(lon):
    d = lon % 30; sign_idx = int(lon // 30); n = int(d // (30 / 9))
    modality = (sign_idx % 3)
    start_sign = (sign_idx // 3) * 3 if modality == 0 else (((sign_idx // 3) * 3 + 8) % 12 if modality == 1 else ((sign_idx // 3) * 3 + 4) % 12)
    nav_sign = (start_sign + n) % 12; nav_deg = (d % (30 / 9)) * 9
    return RASI[nav_sign], nav_deg

# SECTION 4: CORE CALCULATION LOGIC
def get_chart_data(lat, lon, dt):
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    # Using float for precise time calculation
    jd = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute/60 + dt.second/3600)
    _, ascmc = swe.houses_ex(jd, lat, lon, b'P', flags=swe.FLG_SIDEREAL)
    results = [("Asc", ascmc[0])]
    for k, v in PLANETS.items():
        xx, _ = swe.calc_ut(jd, v, swe.FLG_SIDEREAL)
        results.append((k, xx[0]))
    results.append(("Ke", (results[-1][1] + 180) % 360))
    formatted = []
    for name, lon_val in results:
        d1_str = f"{int(lon_val%30)} {RASI[int(lon_val//30)]} {get_dms(lon_val).split('°')[1]}"
        nav_s, nav_d = get_nav(lon_val)
        d9_str = f"{int(nav_d)} {nav_s} {get_dms(nav_d).split('°')[1]}"
        formatted.append((name, d1_str, d9_str))
    return formatted

# SECTION 5: EXECUTION AND DISPLAY
def run_system(year, month, day, hour, minute, second, lat, lon):
    print(f"{'Planet':<6} | {'D1 Position':<15} | {'D9 Position':<15}")
    print("-" * 42)
    dt = datetime(year, month, day, hour, minute, second, tzinfo=timezone.utc)
    data = get_chart_data(lat, lon, dt)
    for row in data:
        print(f"{row[0]:<6} | {row[1]:<15} | {row[2]:<15}")

# SECTION 6: USER INPUT (EDIT HERE)
if __name__ == "__main__":
    MY_LAT, MY_LON = 59.908611, 10.747778
    # Format: Year, Month, Day, Hour, Minute, Second
    run_system(1995, 12, 28, 8, 0, 0, MY_LAT, MY_LON)
