import swisseph as swe
from datetime import timezone

# Assuming these are defined as you had them
RASI = ["Ar","Ta","Ge","Cn","Le","Vi","Li","Sc","Sg","Cp","Aq","Pi"]
PLANETS = {"Su": swe.SUN, "Mo": swe.MOON, "Ma": swe.MARS, "Me": swe.MERCURY, 
           "Ju": swe.JUPITER, "Ve": swe.VENUS, "Sa": swe.SATURN, "Ra": swe.MEAN_NODE}

def get_chart_data(dt_local, input_hub):
    """Calculates chart data using the Centralized Input Hub."""
    # Extract settings from the hub
    lat = input_hub.lat
    lon = input_hub.lon
    
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    
    # Standardize time
    utc_dt = dt_local.astimezone(timezone.utc)
    jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, 
                    utc_dt.hour + utc_dt.minute/60 + utc_dt.second/3600)
    
    # Calculate houses and planets
    cusps, ascmc = swe.houses_ex(jd, lat, lon, b'P', flags=swe.FLG_SIDEREAL)
    results = [("Lagna", ascmc[0])]
    
    planet_longs = {}
    for k, v in PLANETS.items():
        xx, _ = swe.calc_ut(jd, v, swe.FLG_SIDEREAL)
        planet_longs[k] = xx[0]
        results.append((k, xx[0]))
    
    results.append(("Ke", (planet_longs["Ra"] + 180) % 360))
    return results
