import swisseph as swe
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

# Settings
RASI = ["Ar","Ta","Ge","Cn","Le","Vi","Li","Sc","Sg","Cp","Aq","Pi"]
PLANETS = {"Su": swe.SUN, "Mo": swe.MOON, "Ma": swe.MARS, "Me": swe.MERCURY, 
           "Ju": swe.JUPITER, "Ve": swe.VENUS, "Sa": swe.SATURN, "Ra": swe.MEAN_NODE}

def get_dms(lon):
    d = int(lon % 30)
    m = int((lon * 60) % 60)
    s = int((lon * 3600) % 60)
    return f"{d:02}°{m:02}'{s:02}''"

def get_nav(lon):
    d = lon % 30
    sign_idx = int(lon // 30)
    n = int(d // (30 / 9))
    modality = (sign_idx % 3)
    # Vedic Navamsha logic
    if modality == 0: start_sign = (sign_idx // 3) * 3
    elif modality == 1: start_sign = ((sign_idx // 3) * 3 + 8) % 12
    else: start_sign = ((sign_idx // 3) * 3 + 4) % 12
    
    nav_sign = (start_sign + n) % 12
    nav_deg = (d % (30 / 9)) * 9
    return RASI[nav_sign], nav_deg

def compute():
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    dt = datetime(1995, 12, 28, 9, 0, 0, tzinfo=ZoneInfo("Europe/Oslo"))
    dt_utc = dt.astimezone(timezone.utc)
    jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, dt_utc.hour + dt_utc.minute/60)
    
    # Lagna
    cusps, ascmc = swe.houses_ex(jd, 59.9139, 10.7522, b'P', flags=swe.FLG_SIDEREAL)
    results = [("Lagna", ascmc[0])]
    
    # Planets
    planet_longs = {}
    for k, v in PLANETS.items():
        xx, _ = swe.calc_ut(jd, v, swe.FLG_SIDEREAL)
        planet_longs[k] = xx[0]
        results.append((k, xx[0]))
    
    # Ketu (Calculated from Mean Rahu)
    ke_lon = (planet_longs["Ra"] + 180) % 360
    results.append(("Ke", ke_lon))
    
    # Print Table
    header = f"{'Body':<6} | {'D1 Sign':<8} | {'D1 Deg':<12} | {'D9 Sign':<8} | {'D9 Deg':<12}"
    print(header)
    print("-" * len(header))
    for name, lon in results:
        d9_s, d9_d = get_nav(lon)
        print(f"{name:<6} | {RASI[int(lon//30)]:<8} | {get_dms(lon):<12} | {d9_s:<8} | {get_dms(d9_d):<12}")

if __name__ == "__main__":
    compute()
