from datetime import datetime, timezone

class InputModule:
    def __init__(self, dt_local, lat, lon):
        self.dt_local = dt_local
        self.lat = lat
        self.lon = lon
        
    def get_context(self):
        # Centralized settings
        return {
            "dt_local": self.dt_local,
            "lat": self.lat,
            "lon": self.lon
        }
