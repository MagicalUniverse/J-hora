%%writefile transit_engine.py
from d1d9_core import compute

class TransitEngine:

    def __init__(self, natal):
        self.natal = natal

    def load(self, dt, lat, lon):
        self.transit = compute(dt, lat, lon)

    def report(self):
        print("\n=== TRANSIT COMPARISON ===")

        for k in self.natal["planets"]:
            n = self.natal["planets"][k]
            t = self.transit["planets"][k]

            print(
                k,
                "D1:",
                n["sign"], "→", t["sign"],
                "| D9:",
                n["d9"], "→", t["d9"]
            )
