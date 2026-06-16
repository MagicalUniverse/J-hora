import swisseph as swe

# 1. SETUP
LAGNA_INDEX = 5  # Virgo
B_JD = 2461203.0 
FLAGS = swe.FLG_SIDEREAL | swe.FLG_TOPOCTR | swe.FLG_TRUEPOS

# Map: Sign Index -> Lord Planet
LORDS = {0: 'Mars', 1: 'Venus', 2: 'Mercury', 3: 'Moon', 4: 'Sun', 5: 'Mercury', 
         6: 'Venus', 7: 'Mars', 8: 'Jupiter', 9: 'Saturn', 10: 'Saturn', 11: 'Jupiter'}

PLANETS = {'Sun': swe.SUN, 'Moon': swe.MOON, 'Mars': swe.MARS, 
           'Jupiter': swe.JUPITER, 'Saturn': swe.SATURN,
           'Mercury': swe.MERCURY, 'Venus': swe.VENUS}

# 2. SCANNING ENGINE
print(f"--- 7-Day Transit Scan (Lagna: {LAGNA_INDEX}) ---")

for day in range(7):
    T_JD = B_JD + day
    print(f"\n--- Day {day} ---")
    
    for name, pid in PLANETS.items():
        # Get sign planet is currently in
        lon = swe.calc_ut(T_JD, pid, FLAGS)[0][0]
        sign_idx = int(lon // 30)
        
        # Calculate house relative to Lagna
        house = ((sign_idx - LAGNA_INDEX) % 12) + 1
        lord = LORDS[sign_idx]
        
        # Apply BULL/BEAR status
        status = None
        if house in [6, 8, 12]: status = "BULL"
        elif house in [5, 9, 11]: status = "BEAR"
        
        if status:
            print(f"{status} {name} (Lord: {lord}) in {house}th")
