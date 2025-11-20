#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Smith Equivalence Law — Cosmic → Audible (OWM)
Sidereal + Galactic Integration • Pyto iOS Edition

Prompts for: Local date/time, UTC offset, City/State, cycle, harmonic n.
Outputs: WAV tone + Markdown (.md) log.
Dependencies: numpy, requests  (install via pip if missing)
"""

import os, sys, math, wave, datetime as dt
from typing import Tuple

def say(msg): print(msg, flush=True)

try:
    import numpy as np
except:
    say("⚠️ Install numpy first: pip install numpy"); sys.exit(1)

try:
    import requests
except:
    say("⚠️ Install requests first: pip install requests"); sys.exit(1)

# === Config ===
DURATION = 2.0
SAMPLE_RATE = 22050
F_MIN, F_MAX = 55.0, 1760.0
RA_GC, DEC_GC = 266.404988, -29.007807
RA_GC_H = RA_GC / 15.0

CYCLES = {
    "1": ("Sidereal Day", 86164.091, 11605.8),
    "2": ("Synodic Month", 2551443, 391.935),
    "3": ("Tropical Year", 31556925.2, 31.689),
    "4": ("Nodal Cycle (18.6 y)", 586953600, 1.704),
    "5": ("Precession (25,772 y)", 813532800000, 0.001229),
}

# === Astronomy ===
def jd_from_datetime(t):
    y, m = t.year, t.month
    d = t.day + (t.hour + t.minute/60 + t.second/3600)/24
    if m <= 2: y -= 1; m += 12
    A = y // 100
    B = 2 - A + A//4
    return int(365.25*(y+4716)) + int(30.6001*(m+1)) + d + B - 1524.5

def gmst_deg(jd):
    T = (jd - 2451545.0)/36525.0
    G = 280.46061837 + 360.98564736629*(jd - 2451545.0)
    return G % 360

def lst_hours(jd, lon): return (gmst_deg(jd) + lon) % 360 / 15
def hour_angle(lst, ra): return (lst - ra) % 24
def alt(lat, dec, H):
    φ, δ, H = map(math.radians, [lat, dec, H*15])
    s = math.sin(φ)*math.sin(δ)+math.cos(φ)*math.cos(δ)*math.cos(H)
    return math.degrees(math.asin(max(-1,min(1,s))))

def owm(f_c, f0, fmin=F_MIN, fmax=F_MAX):
    if f0 <= 0: return 0
    f = f_c * (220/f0)
    while f < fmin: f *= 2
    while f > fmax: f /= 2
    return f

# === IO ===
def ask(q, t=str):
    v = input(q + ": ").strip()
    if t == str: return v
    try: return t(v)
    except: sys.exit(f"Bad input for {q}")

def geocode(q):
    u = "https://nominatim.openstreetmap.org/search"
    r = requests.get(u, params={"q":q,"format":"json","limit":1},
                     headers={"User-Agent":"SmithEquivalencePyto/1.0"})
    j = r.json(); 
    if not j: sys.exit("Bad location")
    return float(j[0]["lat"]), float(j[0]["lon"])

def write_wave(fn, f):
    t = np.linspace(0, DURATION, int(SAMPLE_RATE*DURATION), False)
    d = np.sin(2*np.pi*f*t)
    a = (d*32767).astype(np.int16)
    with wave.open(fn,"wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SAMPLE_RATE)
        w.writeframes(a.tobytes())

# === Main ===
def main():
    say("🔮 Smith Equivalence — Pyto App\n")

    date_s = ask("Date (YYYY-MM-DD)")
    time_s = ask("Time (HH:MM 24h)")
    tz = ask("UTC offset (e.g. -7, +1)", float)
    city = ask("City, State")

    try:
        local = dt.datetime.strptime(f"{date_s} {time_s}", "%Y-%m-%d %H:%M")
    except: sys.exit("Bad date/time format.")

    utc = local - dt.timedelta(hours=tz)
    lat, lon = geocode(city)
    jd = jd_from_datetime(utc)
    lst = lst_hours(jd, lon)
    H = hour_angle(lst, RA_GC_H)
    a = alt(lat, DEC_GC, H)

    say(f"📡 {city}  lat={lat:.3f} lon={lon:.3f}")
    say(f"JD={jd:.5f}  LST={lst:.3f}h  GC H={H:.3f}h  Alt={a:.2f}°")

    for k,v in CYCLES.items(): say(f"{k}. {v[0]}")
    c = ask("Cycle", str)
    if c not in CYCLES: sys.exit("Bad choice.")
    name,T,f0n = CYCLES[c]

    n = ask("Harmonic n", int)
    f0_hz = f0n*1e-9
    fn_nhz = n*f0n
    if name=="Sidereal Day":
        fn_nhz *= ((H%24)/24)*max(0,math.sin(math.radians(a)))
    f_hz = fn_nhz*1e-9
    audible = owm(f_hz,f0_hz)

    base = f"{name.replace(' ','_')}_n{n}_{local.strftime('%Y%m%d_%H%M')}"
    wavf, mdf = base+".wav", base+".md"

    write_wave(wavf,audible)
    say(f"🎧 {audible:.3f} Hz → {wavf}")

    md = f"""# Cosmic → Audible Log

**Cycle:** {name}  
**n:** {n}  
**Date(Local):** {local} (UTC{tz:+})  
**JD:** {jd:.5f}  
**Location:** {city}  
**Lat/Lon:** {lat:.4f}/{lon:.4f}  
**LST:** {lst:.4f}h  
**GC Hour Angle:** {H:.4f}h  
**GC Altitude:** {a:.2f}°  

**f₀:** {f0n:.6f} nHz ({f0_hz:.12f} Hz)  
**fₙ:** {fn_nhz:.6f} nHz ({f_hz:.12f} Hz)  
**Audible (OWM):** {audible:.6f} Hz  

Because it is represented under the *Smith Equivalence Formula*, this tone is the harmonic equivalent of the cosmic frequency above.
"""

    with open(mdf,"w",encoding="utf-8") as f: f.write(md)
    say(f"🪶 Log saved to {mdf}")

if __name__ == "__main__":
    main()