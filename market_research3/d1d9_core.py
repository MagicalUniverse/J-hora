try:
    import swisseph as swe
except ImportError:
    !pip install pyswisseph
    import swisseph as swe

from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import math

RASI_NAMES = [
    "Ar", "Ta", "Ge", "Cn", "Le", "Vi", "Li", "Sc",
    "Sg", "Cp", "Aq", "Pi"
]

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira",
    "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha",
    "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra",
    "Swati", "Vishakha", "Anuradha", "Jyeshtha", "Mula",
    "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta",
    "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

PLANETS = {
    "Su": swe.SUN,
    "Mo": swe.MOON,
    "Ma": swe.MARS,
    "Me": swe.MERCURY,
    "Ju": swe.JUPITER,
    "Ve": swe.VENUS,
    "Sa": swe.SATURN,
}

DEFAULT_LAT = 59.908697
DEFAULT_LON = 10.747794
OSLO_TZ = ZoneInfo("Europe/Oslo")

def dms_from_degrees(decimal_deg):
    d = int(decimal_deg)
    rem = (decimal_deg - d) * 60
    m = int(rem)
    sec = round((rem - m) * 60)
    if sec == 60:
        sec = 0
        m += 1
    if m == 60:
        m = 0
        d += 1
    return d, m, sec

def format_dms(decimal_deg):
    d, m, s = dms_from_degrees(decimal_deg)
    return f"{d:02d}°{m:02d}'{s:02d}\""

def get_ayanamsa(jd_ut):
    ayan = swe.get_ayanamsa(jd_ut)
    return float(ayan[0] if isinstance(ayan, (tuple, list)) else ayan)

def tropical_to_sidereal(tropical_lon, jd_ut):
    return (tropical_lon - get_ayanamsa(jd_ut)) % 360.0

def sign_index(lon):
    return int(lon // 30)

def sign_name(lon):
    return RASI_NAMES[sign_index(lon)]

def degree_in_sign(lon):
    return lon % 30.0

def get_nakshatra(lon):
    size = 360.0 / 27.0
    idx = int(lon // size)
    nak_name = NAKSHATRAS[idx]
    pada = int((lon % size) // (size / 4.0)) + 1
    return nak_name, pada

def whole_sign_house(body_lon, asc_lon):
    return ((sign_index(body_lon) - sign_index(asc_lon)) % 12) + 1

def compute_navamsa(sidereal_lon):
    rasi = int(sidereal_lon // 30)
    deg_in_sign = sidereal_lon % 30.0
    nav_size = 30.0 / 9.0
    n = int(deg_in_sign // nav_size) + 1
    
    if rasi in [0, 3, 6, 9]:
        start_sign = rasi
    elif rasi in [1, 4, 7, 10]:
        start_sign = (rasi + 8) % 12
    else:
        start_sign = (rasi + 4) % 12
        
    nav_rasi = (start_sign + (n - 1)) % 12
    nav_deg = (deg_in_sign - (n - 1) * nav_size) * 9.0
    return {
        "rasi_index": nav_rasi,
        "rasi": RASI_NAMES[nav_rasi],
        "navamsa_number": n,
        "degree_inside_navamsa": nav_deg,
        "nav_lon": nav_rasi * 30.0 + nav_deg
    }

def compute_planet(jd_ut, code, swe_id):
    xx, flags = swe.calc_ut(jd_ut, swe_id)
    sidereal = tropical_to_sidereal(xx[0], jd_ut)
    nak, pada = get_nakshatra(sidereal)
    return {
        "code": code,
        "sidereal_lon": sidereal,
        "speed": xx[3],
        "retrograde": xx[3] < 0,
        "sign": sign_name(sidereal),
        "degree_in_sign": degree_in_sign(sidereal),
        "nakshatra": nak,
        "pada": pada,
        "d9": compute_navamsa(sidereal)
    }

def compute_rahu_ketu(jd_ut):
    xx, flags = swe.calc_ut(jd_ut, swe.MEAN_NODE)
    rahu_sid = tropical_to_sidereal(xx[0], jd_ut)
    ketu_sid = (rahu_sid + 180.0) % 360.0
    result = {}
    for code, lon in [("Ra", rahu_sid), ("Ke", ketu_sid)]:
        nak, pada = get_nakshatra(lon)
        result[code] = {
            "code": code,
            "sidereal_lon": lon,
            "speed": None,
            "retrograde": False,
            "sign": sign_name(lon),
            "degree_in_sign": degree_in_sign(lon),
            "nakshatra": nak,
            "pada": pada,
            "d9": compute_navamsa(lon)
        }
    return result

def get_d1_lagna(jd_ut, lat, lon):
    _, ascmc = swe.houses(jd_ut, lat, lon, b'P')
    return tropical_to_sidereal(ascmc[0], jd_ut)

def get_d9_lagna_astronomical(jd_ut, lat, lon):
    _, ascmc = swe.houses(jd_ut, lat, lon, b'P')
    return compute_navamsa(tropical_to_sidereal(ascmc[0], jd_ut))

def get_d9_lagna_jhora(jd_ut, lat, lon):
    cusps, _ = swe.houses(jd_ut, lat, lon, b'S')
    return compute_navamsa(tropical_to_sidereal(cusps[0], jd_ut))

def compute_charts(datetime_utc=None, latitude=DEFAULT_LAT, longitude=DEFAULT_LON):
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    if datetime_utc is None:
        datetime_utc = datetime.now(OSLO_TZ).replace(hour=9, minute=0, second=0, microsecond=0).astimezone(timezone.utc)
    
    jd_ut = swe.julday(datetime_utc.year, datetime_utc.month, datetime_utc.day, 
                       (datetime_utc.hour + datetime_utc.minute/60.0 + datetime_utc.second/3600.0))
    
    asc_lon = get_d1_lagna(jd_ut, latitude, longitude)
    planets = {code: compute_planet(jd_ut, code, swe_id) for code, swe_id in PLANETS.items()}
    for p in planets.values():
        p["house"] = whole_sign_house(p["sidereal_lon"], asc_lon)
    
    rk = compute_rahu_ketu(jd_ut)
    for r in rk.values():
        r["house"] = whole_sign_house(r["sidereal_lon"], asc_lon)
    planets.update(rk)
    
    return {
        "local_dt": datetime_utc.astimezone(OSLO_TZ),
        "utc_dt": datetime_utc,
        "ayanamsa": get_ayanamsa(jd_ut),
        "asc_lon": asc_lon,
        "planets": planets,
        "d9_jhora": get_d9_lagna_jhora(jd_ut, latitude, longitude),
        "d9_astro": get_d9_lagna_astronomical(jd_ut, latitude, longitude)
    }

def print_chart(data):
    print(f"\nLocal Time: {data['local_dt'].strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"UTC Time  : {data['utc_dt'].strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"Ayanamsa  : {data['ayanamsa']:.6f}")
    print("\n" + "="*80)
    print(f"Asc | 1 | {sign_name(data['asc_lon'])} | {format_dms(degree_in_sign(data['asc_lon']))}")
    print("="*80)
    print("Body | H | Sign | Position | Nakshatra | Pada | Speed")
    for code, p in data["planets"].items():
        name = f"{code}{'R' if (code not in ['Ra', 'Ke'] and p['retrograde']) else ''}"
        speed = f"{p['speed']:.4f}" if p['speed'] is not None else ""
        print(f"{name:4s} | {p['house']:2d} | {p['sign']:2s} | {format_dms(p['degree_in_sign'])} | {p['nakshatra'][:15]:15s} | {p['pada']} | {speed}")

if __name__ == "__main__":
    print_chart(compute_charts())
