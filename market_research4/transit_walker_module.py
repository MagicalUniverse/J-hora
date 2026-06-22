from datetime import timedelta
from d1d9_core import get_chart_data  # Importing your existing core logic

class TransitWalker:
    def __init__(self, start_dt, lat, lon):
        self.current_dt = start_dt
        self.lat = lat
        self.lon = lon
        self.interval = timedelta(minutes=5)

    def walk(self, days=7):
        """Generates chart data every 5 minutes for a specified range."""
        end_dt = self.current_dt + timedelta(days=days)
        
        while self.current_dt < end_dt:
            # Generate the chart snapshot using your core module
            chart_snapshot = get_chart_data(self.current_dt, self.lat, self.lon)
            
            # Yield the data to the scanner (generator pattern is memory efficient)
            yield self.current_dt, chart_snapshot
            
            # Increment time
            self.current_dt += self.interval

# Example of how to connect it to your scanner:
# walker = TransitWalker(start_time, lat, lon)
# for timestamp, chart in walker.walk(days=7):
#     matches = transit_scanner.scan(chart) 
#     if matches:
#         print(f"Alert at {timestamp}: {matches}")
