from datetime import datetime

# ============================================================
# SCRIPT NAME: input_module.py
# VERSION: 1.1.0
#
# PURPOSE:
# - Configuration management
# - Centralized JHora reference storage for validation
# ============================================================



class InputModule:
    # JHORA Reference table now lives here
    JHORA_REFERENCE = {
        "Lagna": {"d1": "04°58'21''", "d9": "Ta 14°45'17''"},
        "Su":    {"d1": "12°18'21''", "d9": "Cn 20°45'09''"},
        "Mo":    {"d1": "06°41'41''", "d9": "Vi 00°15'12''"},
        "Ma":    {"d1": "27°31'20''", "d9": "Sg 07°42'04''"},
        "Me":    {"d1": "00°40'09''", "d9": "Cp 06°01'28''"},
        "Ju":    {"d1": "04°51'02''", "d9": "Ta 13°39'23''"},
        "Ve":    {"d1": "14°18'44''", "d9": "Ta 08°48'43''"},
        "Sa":    {"d1": "25°21'31''", "d9": "Ta 18°13'39''"},
        "Ra":    {"d1": "28°49'46''", "d9": "Vi 19°27'58''"},
        "Ke":    {"d1": "Pi 28°49'46''", "d9": "Pi 19°27'58''"}
    }

    def __init__(self, lat=None, lon=None, dms_lat=(59, 54, 31), dms_lon=(10, 44, 52), 
                 dt_birth="1995-12-28 08:00", dt_transit_start="2026-06-24 09:00", 
                 duration=7, interval=5):
        
        self.lat = lat if lat is not None else dms_lat[0] + dms_lat[1]/60 + dms_lat[2]/3600
        self.lon = lon if lon is not None else dms_lon[0] + dms_lon[1]/60 + dms_lon[2]/3600
        
        self.dt_birth = datetime.strptime(dt_birth, "%Y-%m-%d %H:%M")
        self.dt_transit_start = datetime.strptime(dt_transit_start, "%Y-%m-%d %H:%M")
        self.duration = duration
        self.interval = interval
        
        print(f"\n--- CONFIGURATION VERIFIED ---")
        print(f"Location: {self.lat:.4f}°N, {self.lon:.4f}°E")
        print("------------------------------\n")
