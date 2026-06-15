import swisseph as swe
import pandas as pd
from datetime import datetime

# 1. Vedic Sidereal Setup
swe.set_sid_mode(swe.SIDM_LAHIRI)

def generate_transit_summary(start_dt, end_dt, buffer_deg=1.0):
    planets = {
        'Sun': swe.SUN, 'Moo': swe.MOON, 'Mar': swe.MARS, 'Mer': swe.MERCURY, 
        'Ven': swe.VENUS, 'Jup': swe.JUPITER, 'Sat': swe.SATURN
    }
    rashi_map = {0: 'Ar', 1: 'Ta', 2: 'Ge', 3: 'Cn', 4: 'Le', 5: 'Vi', 
                 6: 'Li', 7: 'Sc', 8: 'Sg', 9: 'Cp', 10: 'Aq', 11: 'Pi'}
    
    summary_ledger = []
    
    for name, pid in planets.items():
        in_zone = False
        zone_start = None
        start_pos = None
        
        curr = start_dt
        while curr <= end_dt:
            jd = swe.julday(curr.year, curr.month, curr.day, curr.hour + curr.minute/60.0)
            pos = swe.calc_ut(jd, pid, swe.FLG_SIDEREAL)[0][0]
            
            boundary_dist = pos % 30
            dist_to_edge = min(boundary_dist, 30 - boundary_dist)
            
            if dist_to_edge <= buffer_deg:
                if not in_zone:
                    in_zone = True
                    zone_start = curr
                    start_pos = pos % 30
                last_in_zone_time = curr
            else:
                if in_zone:
                    duration = last_in_zone_time - zone_start
                    total_hours = int(duration.total_seconds() // 3600)
                    total_mins = int((duration.total_seconds() % 3600) // 60)
                    
                    summary_ledger.append({
                        'Planet': name,
                        'Space': rashi_map.get(int(pos // 30), '??'),
                        'Entrance': zone_start.strftime('%Y-%m-%d %H:%M'),
                        'Degree': f"{start_pos:.2f}°",
                        'Duration': f"{total_hours}h {total_mins}m"
                    })
                    in_zone = False
            curr += pd.Timedelta(minutes=30) # Increased resolution for duration accuracy
            
    return pd.DataFrame(summary_ledger)
