# J-hora
Beräkna resultat från en lista med olika tidpunkt 


# High-Precision Sidereal Transit Engine

A lightweight, high-precision Python transit calculation engine utilizing the Swiss Ephemeris (`pyswisseph`). This engine is fully calibrated to align with traditional Chitra-Paksha Lahiri configurations down to sub-arcsecond tolerances, featuring automated multi-tier divisional chart (Varga) mapping and boundary collision detection.

## Features

* **Astronomical Precision:** Sub-arcsecond parity with desktop calculation suites (Jagannatha Hora).
* **Zodiac Calibration:** Hardlocked to Traditional Chitra-Paksha Lahiri Sidereal parameters.
* **Divisional Analysis:** Real-time extraction of D1 (Rashi), D9 (Navamsa/Pada), and D2 (Parasara Hora) matrices.
* **Boundary Safeguards:** Integrated runtime tracking that flags positions within 1 arcminute of any sign, Nakshatra, or divisional boundary to prevent amplification errors.

## Installation

Ensure you have the Swiss Ephemeris C-library dependencies compiled for your environment before executing the script.

                  ┌─────────────────────────────────┐
                  │      LIVE MARKET TIMESTAMP      │
                  └────────────────┬────────────────┘
                                   │
         ┌─────────────────────────┼─────────────────────────┐
         ▼                         ▼                         ▼
 ┌───────────────┐         ┌───────────────┐         ┌───────────────┐
 │ Alignment     │         │ Aspect Logic  │         │ Sentiment     │
 │ Layer         │         │ (Drishti)     │         │ Layer         │
 └───────┬───────┘         └───────┬───────┘         └───────┬───────┘
         │                         │                         │
         ▼                         ▼                         ▼
 - Match Market to Birth   - Compute geometric arcs  - Find house lords
 - Flag/Color Ascendant    - Match special aspects   - Apply Bull/Bear 
   crossings Red             (e.g., Saturn 3/7/10)     scoring parameters

   
