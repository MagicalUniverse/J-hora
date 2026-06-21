%%writefile d1d9_core.py
import swisseph as swe
from datetime import timezone

# -----------------------------
# CONFIG (LOCKED)
# -----------------------------

swe.set_sid_mode(swe.SIDM_LAHIRI)
swe.set_ephe_path('.')  # IMPORTANT for Colab stability

RASI = ["Ar","Ta","Ge","Cn","Le","Vi","Li","Sc","Sg","Cp","Aq","Pi"]

NAKSHATRAS = [
    "Ashwini","Bharani","Krittika","Rohini","Mrigashira",
    "Ardra","Punarvasu","Pushya","Ashlesha","Magha",
    "Purva Phalguni","Uttara Phalguni","Hasta","Chitra",
    "Swati","Vishakha","Anuradha","Jyeshtha","Mula",
    "Purva Ashadha","Uttara Ashadha","Shravana","Dhanishta",
    "Shatabhisha","Purva Bhadrapada","Uttara Bhadrapada","Revati"
]

PLANETS = {
    "Su": swe.SUN,
    "Mo": swe.MOON,
    "Ma": swe.MARS,
    "Me": swe.MERCURY,
    "Ju": swe.JUPITER,
    "Ve": swe.VENUS,
    "Sa": swe.SATURN,
    "Ra": swe.MEAN_NODE
    "Ke": swe.MEAN_NODE
}
}

FLAGS = swe.FLG_SWIEPH | swe.FLG_SIDEREAL


# -----------------------------
# BASIC HELPERS
# -----------------------------

def sign(lon):
    return RASI[int(lon // 30) % 12]

def deg(lon):
    return lon % 30


def nak(lon):
    size = 360 / 27
    i = int(lon // size) % 27
    pada = int((lon % size) // (size / 4)) + 1
    return NAKSHATRAS[i], pada


# -----------------------------
# NAVAMSA (STANDARD JHORA METHOD)
# -----------------------------

def nav(lon):
    sign_index = int(lon // 30)
    d = lon % 30
    n = int(d // (30 / 9))

    # standard movable/fixed/dual mapping
    if sign_index in [0,3,6,9]:
        start = sign_index
    elif sign_index in [1,4,7,10]:
        start = (sign_index + 8) % 12
    else:
        start = (sign_index + 4) % 12

    return RASI[(start + n) % 12]


# -----------------------------
# PLANET CALC
# -----------------------------

def planet(jd, pid):
    xx, _ = swe.calc_ut(jd, pid, FLAGS)
    lon = xx[0]

    return {
        "lon": lon,
        "sign": sign(lon),
        "deg": deg(lon),
        "nak": nak(lon),
        "d9": nav(lon),
        "retro": xx[3] < 0
    }


# -----------------------------
# LAGNA (STABLE VERSION)
# -----------------------------

def lagna(jd, lat, lon):
    houses, ascmc = swe.houses_ex(
        jd, lat, lon,
        b'P',
        flags=FLAGS
    )
    return ascmc[0]


# -----------------------------
# MAIN ENGINE
# -----------------------------

def compute(dt, lat, lon):
    utc = dt.astimezone(timezone.utc)

    jd = swe.julday(
        utc.year, utc.month, utc.day,
        utc.hour + utc.minute/60 + utc.second/3600
    )

    asc = lagna(jd, lat, lon)

    planets = {k: planet(jd, v) for k, v in PLANETS.items()}

    return {
        "utc": utc,
        "jd": jd,
        "asc": asc,
        "planets": planets
    }

def dms(lon):
    sign = int(lon // 30)
    deg_float = lon % 30

    deg = int(deg_float)
    minutes_full = (deg_float - deg) * 60
    minutes = int(minutes_full)
    seconds = int((minutes_full - minutes) * 60)

    return RASI[sign], deg, minutes, seconds
# -----------------------------
# OUTPUT
# -----------------------------

def print_chart(c):
    print("\nUTC:", c["utc"])
    print("Lagna:", dms(c["asc"]))

    print("\n--- NATAL PLANETS ---")

    for k, p in c["planets"].items():
        sign, deg, min_, sec = dms(p["lon"])

        print(
            f"{k:>2}  {sign:>2}  "
            f"{deg:02d}°{min_:02d}'{sec:02d}\"  "
            f"| D9: {RASI[p['d9']]}"
        )
