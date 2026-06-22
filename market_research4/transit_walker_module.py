# input_module.py
from datetime import datetime, time

class InputModule:
    def __init__(self, lat, lon, dt_birth, dt_transit_start=None):
        self.lat = lat
        self.lon = lon
        self.dt_birth = dt_birth # Your birth chart reference
        
        # Default transit start: 09:00 on the day of entry
        if dt_transit_start is None:
            today = datetime.now().date()
            self.dt_transit_start = datetime.combine(today, time(9, 0))
        else:
            self.dt_transit_start = dt_transit_start
