import swisseph as swe
from datetime import datetime, timezone
import swisseph as swe

def get_chart_data(dt, lat, lon):
    # 1. Convert local time to UTC explicitly
    # Assuming dt is already a timezone-aware datetime object
    utc_dt = dt.astimezone(timezone.utc)
    
    # 2. Calculate Julian Day
    jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, 
                    utc_dt.hour + utc_dt.minute/60 + utc_dt.second/3600)
    
    # 3. Explicitly set Ayanamsa mode and force calculation
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    
    # ... your planet loop ...
    # Inside your loop, you can now verify the shift:
    # ayanamsa = swe.get_ayanamsa(jd)
    return data

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
    if modality == 0: start_sign = (sign_idx // 3) * 3
    elif modality == 1: start_sign = ((sign_idx // 3) * 3 + 8) % 12
    else: start_sign = ((sign_idx // 3) * 3 + 4) % 12
    
    nav_sign = (start_sign + n) % 12
    nav_deg = (d % (30 / 9)) * 9
    return RASI[nav_sign], nav_deg

def get_chart_data(dt_local, lat, lon):
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    dt_utc = dt_local.astimezone(timezone.utc)
    jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, dt_utc.hour + dt_utc.minute/60)
    
    cusps, ascmc = swe.houses_ex(jd, lat, lon, b'P', flags=swe.FLG_SIDEREAL)
    results = [("Lagna", ascmc[0])]
    
    planet_longs = {}
    for k, v in PLANETS.items():
        xx, _ = swe.calc_ut(jd, v, swe.FLG_SIDEREAL)
        planet_longs[k] = xx[0]
        results.append((k, xx[0]))
    
    ke_lon = (planet_longs["Ra"] + 180) % 360
    results.append(("Ke", ke_lon))
    return results
