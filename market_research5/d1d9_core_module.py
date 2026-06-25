"""
SCRIPT NAME: d1d9_core_module.py
PURPOSE: Single Source of Truth for D1/D9 Calculations
VERSION: 3.0.0

REQUIREMENTS:

* Swiss Ephemeris installed
* Lahiri Ayanamsha
* Returns D1 sign + degree separately
* Returns D9 sign + degree separately
* No printing
* No file writing
* No transit scanning
* Used by main2_module.py and transit_walker_module.py
  """

import swisseph as swe

RASI = ["Ar","Ta","Ge","Cn","Le","Vi","Li","Sc","Sg","Cp","Aq","Pi"]

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
d = int(lon % 30)
m = int((lon * 60) % 60)
s = int((lon * 3600) % 60)
return f"{d:02}°{m:02}'{s:02}''"

def get_nav(lon):
d = lon % 30
sign_idx = int(lon // 30)

```
n = int(d // (30 / 9))
modality = sign_idx % 3

if modality == 0:
    start_sign = (sign_idx // 3) * 3
elif modality == 1:
    start_sign = ((sign_idx // 3) * 3 + 8) % 12
else:
    start_sign = ((sign_idx // 3) * 3 + 4) % 12

nav_sign = (start_sign + n) % 12
nav_deg = (d % (30 / 9)) * 9

return RASI[nav_sign], nav_deg
```

def get_chart_data(lat, lon, dt):

```
swe.set_sid_mode(swe.SIDM_LAHIRI)

jd = swe.julday(
    dt.year,
    dt.month,
    dt.day,
    dt.hour + dt.minute/60 + dt.second/3600
)

cusps, ascmc = swe.houses_ex(
    jd,
    lat,
    lon,
    b'P',
    flags=swe.FLG_SIDEREAL
)

results = [("Lagna", ascmc[0])]

planet_longs = {}

for name, planet in PLANETS.items():
    xx, _ = swe.calc_ut(
        jd,
        planet,
        swe.FLG_SIDEREAL
    )

    planet_longs[name] = xx[0]
    results.append((name, xx[0]))

ketu_lon = (planet_longs["Ra"] + 180) % 360
results.append(("Ke", ketu_lon))

chart = []

for body, lon_val in results:

    d1_sign = RASI[int(lon_val // 30)]
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
```
