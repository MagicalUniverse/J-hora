import swisseph as swe
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

# -----------------------------
# CONFIG
# -----------------------------
swe.set_sid_mode(swe.SIDM_LAHIRI)
swe.set_ephe_path('.')

RASI = ["Ar", "Ta", "Ge", "Cn", "Le", "Vi", "Li", "Sc", "Sg", "Cp", "Aq", "Pi"]

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


FLAGS = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED

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
    
    # Correct D9 logic: 
    # Navamsa is the 9th harmonic.
    # We must map the 0-360 position into the 9th division.
    d9_sign = nav(lon)
    
    # Calculate degree within the navamsa sign
    # Each navamsa is 3°20' (3.333 degrees)
    d9_deg_in_sign = (lon % 3.3333333333333335) * 9 
    
    return {
        "lon": lon,
        "d9_sign": d9_sign,
        "d9_deg": d9_deg_in_sign
    }

def compute(dt, lat, lon):
    # Pass the timezone-aware datetime directly to julday
    # Do not apply manual LMT correction; let swe.houses_ex handle the coordinate shift
    utc_dt = dt.astimezone(timezone.utc)
    jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, 
                    utc_dt.hour + utc_dt.minute/60 + utc_dt.second/3600)
    
    # Use 'S' (Sripathi) and strictly Topocentric calculation
    # This aligns the Ascendant cusp with the geographic observation point
    houses, ascmc = swe.houses_ex(jd, lat, lon, b'S', FLAGS)
    
    planets = {k: planet(jd, v) for k, v in PLANETS.items()}
    
    # Node logic
    planets["Ke"]["lon"] = (planets["Ra"]["lon"] + 180) % 360
    planets["Ke"]["d9_lon"] = (planets["Ke"]["lon"] * 9) % 360
    
    return {"utc": utc_dt, "asc": ascmc[0], "planets": planets}

def print_chart(c):
    print("\nUTC:", c["utc"])
    asc_s, asc_d, asc_m, asc_sec = dms(c["asc"])
    asc_d9_lon = (c['asc'] * 9) % 360
    asc_d9_s, asc_d9_d, asc_d9_m, asc_d9_sec = dms(asc_d9_lon)
    
    print(f"Lagna: {asc_s} {asc_d:02d}°{asc_m:02d}'{asc_sec:02d}\" | D9: {asc_d9_s} {asc_d9_d:02d}°{asc_d9_m:02d}'{asc_d9_sec:02d}\"")

    print("\n--- NATAL PLANETS ---")
    for k, p in c["planets"].items():
        s, d, m, sec = dms(p["lon"])
        d9_s, d9_d, d9_m, d9_sec = dms(p["d9_lon"])
        
        print(f"{k:>2}  {s:>2}  {d:02d}°{m:02d}'{sec:02d}\" | D9: {d9_s} {d9_d:02d}°{d9_m:02d}'{d9_sec:02d}\"")

# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    # Standard Oslo time
    test_dt = datetime(1995, 12, 28, 9, 0, 0, tzinfo=ZoneInfo("Europe/Oslo"))
    natal = compute(test_dt, 59.90870, 10.74779)
    print_chart(natal)
