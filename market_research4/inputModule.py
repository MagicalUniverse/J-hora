# main_module.py
from input_module import InputModule
from transit_walker import TransitWalker

# Everything is initialized here
hub = InputModule(lat=57.1, lon=12.2, dt_birth=my_birth_dt)

# Walker automatically picks up the hub's defaults
walker = TransitWalker(hub)

for timestamp, transit_chart in walker.walk():
    # Compare transit_chart vs. birth_chart (from hub.dt_birth)
    pass
