# d1d9_core_module.py
# VERSION: 3.1.4

import swisseph as swe

# 1. Requirements:
# - Calculate D1 Rashi and D9 Navamsha positions.
# - Use Lahiri Ayanamsa.
# - Apply JHora-style Navamsha calculation logic.
# - Output consistent formatting.
# ============================================================
# NOTE (IMPORTANT FOR ALL AI ASSISTANTS / FUTURE CHATS)
#
# - D1 calculation is based on Swiss Ephemeris (sidereal Lahiri)
# - Minor arc-minute deviations (3–6 min) vs JHora are acceptable
#   and likely due to ephemeris + time precision differences
#
# - D9 (Navamsha) MUST remain fixed using the current mapping
#   system verified against JHora output pattern.
#
# - DO NOT REPLACE NAVAMSHA LOGIC WITHOUT JHORA CROSS CHECK
# ============================================================


RASI = ["Ar", "Ta", "Ge", "Cn", "Le", "Vi", "Li", "Sc", "Sg", "Cp", "Aq", "Pi"]

PLANETS = {
    "Su": swe.SUN,
    "Mo": swe.MOON,
    "Ma": swe.MARS,
    "Me": swe.MERCURY,
    "Ju": swe.JUPITER,
    "Ve": swe.VENUS,
    "Sa": swe.SATURN,
    "Ra": swe.MEAN_NODE
}

def get_dms(lon):
    """Formats longitude to: DD Sign MM' SS''"""
    d = int(lon % 30)
    m = int((lon * 60) % 60)
    s = int((lon * 3600) % 60)
    return f"{d:02} {m:02}'{s:02}''"

def get_nav(lon):
    """Calculates JHora-style Navamsha sign and degree."""
    sign = int(lon // 30)
    deg = lon % 30
    nav_index = int(deg // (30 / 9))

    # JHora-style fixed Navamsa start mapping
    start_map = [0, 9, 6, 3, 0, 9, 6, 3, 0, 9, 6, 3]
    start = start_map[sign]
    nav_sign = (start + nav_index) % 12
    nav_deg = (deg % (30 / 9)) * 9

    return RASI[nav_sign], nav_deg

def get_chart_data(lat, lon, dt):
    """Generates D1/D9 chart data list."""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    jd = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute/60 + dt.second/3600)
    cusps, ascmc = swe.houses_ex(jd, lat, lon, b'P', flags=swe.FLG_SIDEREAL)
    
    results = [("Lagna", ascmc[0])]
    planet_longs = {}
    
    for name, planet in PLANETS.items():
        xx, _ = swe.calc_ut(jd, planet, swe.FLG_SIDEREAL)
        planet_longs[name] = xx[0]
        results.append((name, xx[0]))
        
    ketu_lon = (planet_longs["Ra"] + 180) % 360
    results.append(("Ke", ketu_lon))
    
    chart = []
    for body, lon_val in results:
        d1_sign_idx = int(lon_val // 30)
        d1_sign = RASI[d1_sign_idx]
        d1_deg = get_dms(lon_val)
        
        d9_sign, d9_deg_raw = get_nav(lon_val)
        d9_deg = get_dms(d9_deg_raw)
        
        chart.append({
            "body": body,
            "d1_sign": d1_sign,
            "d1_deg": d1_deg,
            "d9_sign": d9_sign,
            "d9_deg": d9_deg
        })
    return chart
