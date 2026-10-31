#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Smith Equivalence Law — Cosmic → Audible (OWM)
Sidereal + Galactic Integration • Pyto iOS Edition • v4 (auto UTC offset, precision 6-decimal, no freeze)
"""

import sys, os, math, datetime as dt
from typing import Tuple

def say(msg): print(msg, flush=True)

try:
    import numpy as np, requests
except Exception:
    sys.exit("Install dependencies: pip install numpy requests")

# Constants
F_MIN, F_MAX = 55.0, 1760.0
RA_GC_DEG, DEC_GC_DEG = 266.404988, -29.007807
RA_GC_H = RA_GC_DEG / 15.0

CYCLES = {
    "1": ("Sidereal Day", 86164.091, 11605.8),
    "2": ("Synodic Month", 2551443, 391.935),
    "3": ("Tropical Year", 31556925.2, 31.689),
    "4": ("Nodal Cycle (18.6 y)", 586953600, 1.704),
    "5": ("Precession (25,772 y)", 813532800000, 0.001229),
}

# Astronomy functions
def jd_from_datetime(t_utc):
    y, m = t_utc.year, t_utc.month
    d = t_utc.day + (t_utc.hour + t_utc.minute/60 + t_utc.second/3600)/24
    if m <= 2: y -= 1; m += 12
    A = y // 100; B = 2 - A + A // 4
    return int(365.25*(y+4716)) + int(30.6001*(m+1)) + d + B - 1524.5

def gmst_deg(jd):
    return (280.46061837 + 360.98564736629*(jd - 2451545.0)) % 360

def lst_hours(jd, lon): return (gmst_deg(jd) + lon) % 360 / 15
def hour_angle(lst, ra): return (lst - ra) % 24

def altitude_deg(lat, dec, H):
    φ, δ, H = map(math.radians, [lat, dec, H*15])
    s = math.sin(φ)*math.sin(δ)+math.cos(φ)*math.cos(δ)*math.cos(H)
    return math.degrees(math.asin(max(-1,min(1,s))))

def owm_to_audible(cosmic_hz, f0_hz, fmin=F_MIN, fmax=F_MAX):
    if f0_hz <= 0: return 0
    f = cosmic_hz * (220/f0_hz)
    while f < fmin: f *= 2
    while f > fmax: f /= 2
    return f

# Utilities
def ask(q, t=str):
    v = input(q + ": ").strip()
    if t == str: return v
    try: return t(v)
    except: sys.exit(f"Invalid input for {q}")

def geocode_city(q):
    r = requests.get("https://nominatim.openstreetmap.org/search",
        params={"q":q,"format":"json","limit":1},
        headers={"User-Agent":"SmithEquivalencePyto/1.0"}, timeout=20)
    j = r.json()
    if not j: sys.exit("Location not found.")
    return float(j[0]["lat"]), float(j[0]["lon"])

def detect_utc_offset_hours(lat, lon):
    r = requests.get("https://api.open-meteo.com/v1/forecast",
        params={"latitude":lat,"longitude":lon,"timezone":"auto"},
        headers={"User-Agent":"SmithEquivalencePyto/1.0"}, timeout=20)
    j = r.json()
    return j.get("utc_offset_seconds", 0)/3600.0

def fmt6(x): return f"{x:.6f}"

# Main
def main():
    say("🔮 Smith Equivalence — Precision Frequency Mode (v4)\n")

    date_s = ask("Date (YYYY-MM-DD)")
    time_s = ask("Time (HH:MM 24h)")
    city   = ask("City, State (e.g., Spokane, WA)")

    try:
        local_dt = dt.datetime.strptime(f"{date_s} {time_s}", "%Y-%m-%d %H:%M")
    except:
        sys.exit("Bad date/time format. Use YYYY-MM-DD and HH:MM (24h).")

    say("📡 Locating + timezone detection…")
    lat, lon = geocode_city(city)
    utc_off = detect_utc_offset_hours(lat, lon)
    utc_dt = local_dt - dt.timedelta(hours=utc_off)
    say(f"    {city}  lat={fmt6(lat)} lon={fmt6(lon)} UTC offset={fmt6(utc_off)}h")

    jd = jd_from_datetime(utc_dt)
    lst = lst_hours(jd, lon)
    H = hour_angle(lst, RA_GC_H)
    alt_gc = altitude_deg(lat, DEC_GC_DEG, H)
    say(f"🪐 JD={fmt6(jd)}  LST={fmt6(lst)}h  GC H={fmt6(H)}h  Alt={fmt6(alt_gc)}°")

    say("\nSelect cycle:")
    for k,v in CYCLES.items(): say(f"  {k}. {v[0]}")
    ckey = ask("Cycle", str)
    if ckey not in CYCLES: sys.exit("Invalid cycle")
    name, _, f0_nhz = CYCLES[ckey]
    n = ask("Harmonic n", int)

    say("\n[5/6] Applying Smith Equivalence math…")

    f0_hz = f0_nhz * 1e-9
    fn_nhz = n * f0_nhz

    if name == "Sidereal Day":
        phase = (H % 24) / 24
        visibility = max(0.0, math.sin(math.radians(alt_gc)))
        fn_nhz *= phase * visibility

    fn_hz = fn_nhz * 1e-9

    if f0_hz <= 0 or fn_hz <= 0:
        say("⚠️ Frequencies below threshold. Substituting nominal audible base.")
        audible = 440.000000
    else:
        audible = owm_to_audible(fn_hz, f0_hz)

    say(f"🎚 Cosmic {fn_nhz:.6f} nHz ({fn_hz:.12f} Hz) → Audible {audible:.6f} Hz")

    base = f"{name.replace(' ','_')}_n{n}_{local_dt.strftime('%Y%m%d_%H%M')}"
    md_path = os.path.abspath(base + ".md")
    md = f"""# Cosmic → Audible Frequency Log

**Cycle:** {name}  
**Harmonic (n):** {n}  

**Local Date/Time:** {local_dt} (UTC{utc_off:+.2f})  
**UTC Date/Time:** {utc_dt}  
**Julian Date (UTC):** {fmt6(jd)}  

**Location:** {city}  
**Latitude:** {fmt6(lat)}°  
**Longitude:** {fmt6(lon)}°  
**Local Sidereal Time:** {fmt6(lst)} h  
**Galactic Center Hour Angle:** {fmt6(H)} h  
**Galactic Center Altitude:** {fmt6(alt_gc)}°  

**Base f₀:** {fmt6(f0_nhz)} nHz ({fmt6(f0_hz)} Hz)  
**Cosmic fₙ:** {fmt6(fn_nhz)} nHz ({fmt6(fn_hz)} Hz)  
**Audible (OWM):** {fmt6(audible)} Hz  

Because it is represented under the *Smith Equivalence Formula*, 
this frequency carries the cosmic harmonic equivalence of the {name}.
"""

    with open(md_path,"w",encoding="utf-8") as f: f.write(md)
    say(f"🪶 Log saved to {md_path}")
    say("✅ Complete.")

if __name__ == "__main__":
    main()
