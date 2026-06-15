import pandas as pd

def filter_cusp_transitions(df, threshold=1.0/60.0):
    cusp_events = []
    planets = ['Sun', 'Moo', 'Mar', 'Mer', 'Ven', 'Jup', 'Sat', 'Rah', 'Ket']
    
    for _, row in df.iterrows():
        for p in planets:
            val = row[p]
            
            # 1. Rashi Cusp Check (Multiples of 30)
            dist_to_rashi = min(val % 30, 30 - (val % 30))
            if dist_to_rashi <= threshold:
                cusp_events.append({"Time": row["Time"], "Body": p, "Type": "Rashi", "Deg": round(val, 4)})
                
            # 2. Nakshatra Cusp Check (Multiples of 13.3333)
            dist_to_nak = min(val % 13.3333, 13.3333 - (val % 13.3333))
            if dist_to_nak <= threshold:
                cusp_events.append({"Time": row["Time"], "Body": p, "Type": "Nak", "Deg": round(val, 4)})
                
    return pd.DataFrame(cusp_events)
