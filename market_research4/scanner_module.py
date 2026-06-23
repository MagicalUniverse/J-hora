# scanner_module.py

class TransitScanner:
    def __init__(self, birth_chart, orb=1.0):
        self.birth_chart = birth_chart
        self.orb = orb

    def scan(self, transit_chart):
        """
        Calculates if a transit body is conjunct a birth body.
        The modulo logic handles the 360-degree boundary.
        """
        matches = []
        for b_name, b_lon in self.birth_chart:
            for t_name, t_lon in transit_chart:
                # Calculate shortest angular distance
                diff = abs(b_lon - t_lon) % 360
                distance = min(diff, 360 - diff)
                
                if distance < self.orb:
                    matches.append((t_name, b_name, b_lon, t_lon))
        return matches
