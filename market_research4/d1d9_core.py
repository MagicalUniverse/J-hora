import swisseph as swe
from datetime import timezone

# -----------------------------
# CONFIG
# -----------------------------
swe.set_sid_mode(swe.SIDM_LAHIRI)
swe.set_ephe_path('.')

RASI = ["Ar","Ta","Ge","Cn","Le","Vi","Li","Sc","Sg","Cp","Aq","Pi"]

PLANETS = {
    "Su": swe.SUN,
    "Mo": swe.MOON,
    "Ma": swe.MARS,
    "Me": swe.MERCURY,
    "Ju": swe.JUPITER,
    "Ve": swe.VENUS,
    "Sa": swe.SATURN,
    "Ra": swe.MEAN_NODE,
    "Ke": swe.MEAN_NODE
}

FLAGS = swe.FLG_SWIEPH | swe.FLG_SIDEREAL

# -----------------------------
# HELPERS
# -----------------------------

def dms(lon):
    sign_idx = int(lon // 30) % 12
    deg_float = lon % 30
    deg = int(deg_float)
    min_full = (deg_float - deg) * 60
    minutes = int(min_full)
    seconds = int((min_full - minutes) * 60)
    return RASI[sign_idx], deg, minutes, seconds

def nav(lon):
    sign_index = int(lon // 30)
    d = lon % 30
    n = int(d // (30 / 9))
    if sign_index in [0,3,6,9]: start = sign_index
    elif sign_index in [1,4,7,10]: start = (sign_index + 8) % 12
    else: start = (sign_index + 4) % 12
    return RASI[(start + n) % 12]

# -----------------------------
# PLANET CALC
# -----------------------------

def planet(jd, pid):
    xx, _ = swe.calc_ut(jd, pid, FLAGS)
    lon = xx[0]
    
    # CALCULATE D9 LON FOR DEGREES
    d9_lon = (lon * 9) % 360
    
    return {
        "lon": lon,
        "d9_lon": d9_lon,
        "d9_sign": nav(lon)
    }

def compute(dt, lat, lon):
    utc = dt.astimezone(timezone.utc)
    jd = swe.julday(utc.year, utc.month, utc.day, utc.hour + utc.minute/60 + utc.second/3600)
    
    houses, ascmc = swe.houses_ex(jd, lat, lon, b'P', flags=FLAGS)
    
    return {
        "utc": utc,
        "asc": ascmc[0],
        "planets": {k: planet(jd, v) for k, v in PLANETS.items()}
    }

def print_chart(c):
    print("\nUTC:", c["utc"])
    print("Lagna:", dms(c["asc"]))
    print("\n--- NATAL PLANETS ---")
    for k, p in c["planets"].items():
        s, d, m, sec = dms(p["lon"])
        d9_s, d9_d, d9_m, _ = dms(p["d9_lon"])
        print(f"{k:>2}  {s:>2}  {d:02d}°{m:02d}'{sec:02d}\" | D9: {d9_s} {d9_d:02d}°{d9_m:02d}'")

# Add this to the bottom of d1d9_core.py
if __name__ == "__main__":
    from datetime import datetime
    from zoneinfo import ZoneInfo
    
    # Test coordinates
    test_dt = datetime(1995, 1, 28, 9, 0, 0, tzinfo=ZoneInfo("Europe/Oslo"))
    natal = compute(test_dt, 59.90870, 10.74779)
    print_chart(natal)
