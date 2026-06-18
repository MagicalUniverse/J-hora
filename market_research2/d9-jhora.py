import swisseph as swe

# -----------------------------
# 1. Tropisk longitud
# -----------------------------
def get_tropical_longitude(jd_ut, planet):
    lon = swe.calc_ut(jd_ut, planet)[0][0]
    return lon

# -----------------------------
# 2. Siderisk longitud (Lahiri)
# -----------------------------
def to_sidereal(jd_ut, lon_trop):
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    ayan = swe.get_ayanamsa(jd_ut)
    if isinstance(ayan, (tuple, list)):
        ayan = ayan[0]
    return (lon_trop - ayan) % 360

# -----------------------------
# 3. D9-beräkning (Navamsa)
#    - returnerar:
#      d9_rasi_index (0–11)
#      navamsa_number (1–9)
#      d9_degree_0_30 (grad inom navamsan, 0–30)
# -----------------------------
def calc_d9(lon_sid):
    rasi_index = int(lon_sid // 30)      # 0–11
    rasi_degree = lon_sid % 30           # 0–30
    navamsa_size = 30 / 9                # 3.333...°

    # Vilken navamsa (1–9) inom tecknet?
    n = int(rasi_degree // navamsa_size) + 1

    # Starttecken för navamsa beroende på rasi-typ
    movable = [0, 3, 6, 9]      # Ar, Cn, Li, Cp
    fixed   = [1, 4, 7, 10]     # Ta, Le, Sc, Aq
    dual    = [2, 5, 8, 11]     # Ge, Vi, Sg, Pi

    if rasi_index in movable:
        start = rasi_index
    elif rasi_index in fixed:
        start = (rasi_index + 8) % 12
    else:
        start = (rasi_index + 4) % 12

    d9_rasi = (start + (n - 1)) % 12

    # Rest inom navamsan (0–3.333...)
    offset = (n - 1) * navamsa_size
    rest = rasi_degree - offset

    # Skala upp till 0–30° inom navamsan
    d9_degree_0_30 = rest * 9

    return d9_rasi, n, d9_degree_0_30

# -----------------------------
# 4. Format för D9-grad (0–30°)
# -----------------------------
def format_d9_degree(d9_degree_0_30):
    deg = int(d9_degree_0_30)
    minute = int((d9_degree_0_30 - deg) * 60)
    return f"{deg}° {minute}'"

# -----------------------------
# 5. Rasi-namn
# -----------------------------
rasi_names = ["Ar","Ta","Ge","Cn","Le","Vi","Li","Sc","Sg","Cp","Aq","Pi"]

# -----------------------------
# 6. Ascendant (D1)
# -----------------------------
def get_ascendant(jd_ut, lat, lon):
    # lon: öst positiv, väst negativ
    ascmc = swe.houses(jd_ut, lat, lon)[0]
    asc = ascmc[0]
    return asc

# -----------------------------
# 7. Huvudfunktion: D1 + D9 + Ra/Ke + Asc
# -----------------------------
def compute_d1_d9(year, month, day, hour, minute, second, lat, lon):
    time_decimal = hour + minute/60 + second/3600
    jd_ut = swe.julday(year, month, day, time_decimal)

    # Rahu/Ketu: Rahu från ephemeris, Ketu = Rahu + 180°
    rahu_trop = get_tropical_longitude(jd_ut, swe.MEAN_NODE)
    ketu_trop = (rahu_trop + 180) % 360

    planets = {
        "Sun": swe.SUN,
        "Moon": swe.MOON,
        "Mars": swe.MARS,
        "Mercury": swe.MERCURY,
        "Jupiter": swe.JUPITER,
        "Venus": swe.VENUS,
        "Saturn": swe.SATURN,
        "Rahu": None,
        "Ketu": None
    }

    results = {}

    for name, code in planets.items():
        if name == "Rahu":
            lon_trop = rahu_trop
        elif name == "Ketu":
            lon_trop = ketu_trop
        else:
            lon_trop = get_tropical_longitude(jd_ut, code)

        lon_sid = to_sidereal(jd_ut, lon_trop)

        d9_rasi, navamsa_number, d9_degree_0_30 = calc_d9(lon_sid)
        d9_deg_str = format_d9_degree(d9_degree_0_30)

        results[name] = {
            "D1_sidereal": lon_sid,
            "D9_rasi_index": d9_rasi,
            "D9_rasi_name": rasi_names[d9_rasi],
            "D9_navamsa_number": navamsa_number,
            "D9_degree": d9_deg_str
        }

    # D9 Asc
    asc_trop = get_ascendant(jd_ut, lat, lon)
    asc_sid = to_sidereal(jd_ut, asc_trop)

    d9_rasi, navamsa_number, d9_degree_0_30 = calc_d9(asc_sid)
    d9_deg_str = format_d9_degree(d9_degree_0_30)

    results["Asc"] = {
        "D1_sidereal": asc_sid,
        "D9_rasi_index": d9_rasi,
        "D9_rasi_name": rasi_names[d9_rasi],
        "D9_navamsa_number": navamsa_number,
        "D9_degree": d9_deg_str
    }

    return results

# -----------------------------
# 8. Tabellutskrift för D9
# -----------------------------
def print_d9_table(results):
    print(f"{'Body':<10} {'Rasi':<5} {'Nav':<5} {'Deg':<8}")
    print("-" * 40)
    for body, data in results.items():
        print(f"{body:<10} {data['D9_rasi_name']:<5} {data['D9_navamsa_number']:<5} {data['D9_degree']:<8}")
