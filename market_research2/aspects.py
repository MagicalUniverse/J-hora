import swisseph as swe

# 1. SETUP
B_JD = 2461203.0 
FLAGS = swe.FLG_SIDEREAL | swe.FLG_TOPOCTR | swe.FLG_TRUEPOS

PLANETS = {
    'Sun': swe.SUN, 'Moon': swe.MOON, 'Mars': swe.MARS, 
    'Jupiter': swe.JUPITER, 'Saturn': swe.SATURN,
    'Mercury': swe.MERCURY, 'Venus': swe.VENUS,
    'Rahu': swe.MEAN_NODE, 'Ketu': swe.MEAN_NODE
}

# 2. CORRECTED ASPECT MAP
# Ketu is now an empty list [], meaning it projects no aspects.
ASPECT_MAP = {
    'Sun': [7], 'Moon': [7], 'Mercury': [7], 'Venus': [7],
    'Mars': [4, 7, 8], 
    'Jupiter': [5, 7, 9], 
    'Saturn': [3, 7, 10],
    'Rahu': [5, 9], 
    'Ketu': [] 
}

# 3. SCANNING ENGINE
print(f"--- Universal Matrix Scan (Ketu silent) ---")

for day in range(7):
    T_JD = B_JD + day
    pos = {}
    for name, pid in PLANETS.items():
        if name == 'Ketu':
            pos['Ketu'] = (pos['Rahu'] + 180) % 360
        else:
            pos[name] = swe.calc_ut(T_JD, pid, FLAGS)[0][0]
    
    for p1 in PLANETS:
        for p2 in PLANETS:
            if p1 == p2: continue
            
            dist = int(((pos[p2] - pos[p1]) % 360) // 30) + 1
            
            # Check if this distance exists in the map for planet p1
            if dist in ASPECT_MAP.get(p1, []):
                print(f"Day {day}: {p1} aspects {p2} ({dist}th)")
