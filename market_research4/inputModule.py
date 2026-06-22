from datetime import datetime, time
class InputModule:
    def __init__(self, lat, lon, dt_birth, dt_transit_start=None):
        self.lat = lat
        self.lon = lon
        self.dt_birth = dt_birth
        self.dt_transit_start = dt_transit_start or datetime.combine(datetime.now().date(), time(9, 0))
