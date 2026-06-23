# d1d9_core_module.py

import swisseph as swe
from datetime import timezone

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

def get_chart_data(dt_local, input_hub):
    """Calculates chart data using parameters from the Input Hub."""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    
    # Standardize time to UTC
    dt_utc = dt_local.astimezone(timezone.utc)
    jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, 
                    dt_utc.hour + dt_utc.minute/60 + dt_utc.second/3600)
    
    # Calculate houses and planets
    cusps, ascmc = swe.houses_ex(jd, input_hub.lat, input_hub.lon, b'P', flags=swe.FLG_SIDEREAL)
    results = [("Lagna", ascmc[0])]
    
    planet_longs = {}
    for k, v in PLANETS.items():
        xx, _ = swe.calc_ut(jd, v, swe.FLG_SIDEREAL)
        planet_longs[k] = xx[0]
        results.append((k, xx[0]))
    
    results.append(("Ke", (planet_longs["Ra"] + 180) % 360))
    return results
