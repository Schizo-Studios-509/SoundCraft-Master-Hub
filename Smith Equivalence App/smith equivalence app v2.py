#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Smith Equivalence Law — Cosmic → Audible (OWM)
Sidereal + Galactic Integration • Pyto iOS Edition • v2 (auto UTC offset + progress)

Prompts: Local date/time, City/State, cycle, harmonic n.
Auto-detects: UTC offset from location via Open-Meteo (no API key).
Outputs: WAV tone + Markdown (.md) log in Pyto's working directory.

Requires: numpy, requests   (install in Pyto with: pip install numpy requests)
"""

import sys, os, math, wave, datetime as dt
from typing import Tuple

def say(msg): print(msg, flush=True)

# ---- deps ----
try:
    import numpy as np
except Exception:
    say("Install numpy first: pip install numpy")
    sys.exit(1)
try:
    import requests
except Exception:
    say("Install requests first: pip install requests")
    sys.exit(1)

# ---- config ----
DURATION = 2.0            # seconds (short to avoid any stalls)
SAMPLE_RATE = 22050       # Hz
F_MIN, F_MAX = 55.0, 1760.0

# Galactic Center (Sgr A*), J2000
RA_GC_DEG  = 266.404988
DEC_GC_DEG = -29.007807
RA_GC_H    = RA_GC_DEG / 15.0

# Base cycles (name, period seconds, f0 in nHz)
CYCLES = {
    "1": ("Sidereal Day",            86164.091,       11605.8),
    "2": ("Synodic Month",           2551443,          391.935),
    "3": ("Tropical Year",           31556925.2,        31.689),
    "4": ("Nodal Cycle (18.6 y)",    586953600,          1.704),
    "5": ("Precession (25,772 y)",   813532800000,       0.001229),
}

# ---- astro helpers ----
def jd_from_datetime(t_utc: dt.datetime) -> float:
    y, m = t_utc.year, t_utc.month
    d = t_utc.day + (t_utc.hour + t_utc.minute/60 + t_utc.second/3600)/24
    if m <= 2:
        y -= 1
        m += 12
    A = y // 100
    B = 2 - A + A // 4
    return int(365.25*(y+4716)) + int(30.6001*(m+1)) + d + B - 1524.5

def gmst_deg(jd: float) -> float:
    T = (jd - 2451545.0)/36525.0
    G = 280.46061837 + 360.98564736629*(jd - 2451545.0) + 0.000387933*T*T - (T*T*T)/38710000.0
    return G % 360.0

def lst_hours(jd: float, lon_deg: float) -> float:
    return (gmst_deg(jd) + lon_deg) % 360.0 / 15.0

def hour_angle(lst_h: float, ra_h: float) -> float:
    return (lst_h - ra_h) % 24.0

def altitude_deg(lat_deg: float, dec_deg: float, H_hours: float) -> float:
    phi = math.radians(lat_deg)
    dec = math.radians(dec_deg)
    H  = math.radians(H_hours * 15.0)
    s = math.sin(phi)*math.sin(dec) + math.cos(phi)*math.cos(dec)*math.cos(H)
    s = max(-1.0, min(1.0, s))
    return math.degrees(math.asin(s))

def owm_to_audible(cosmic_hz: float, f0_hz: float, fmin=F_MIN, fmax=F_MAX) -> float:
    if f0_hz <= 0.0:
        return 0.0
    # Scale to A3=220 reference by base
    f = cosmic_hz * (220.0 / f0_hz)
    while f < fmin: f *= 2.0
    while f > fmax: f /= 2.0
    return f

# ---- IO helpers ----
def ask(q, cast=str):
    v = input(q + ": ").strip()
    if cast is str:
        return v
    try:
        return cast(v)
    except Exception:
        sys.exit(f"Bad input for {q}")

def geocode_city(city_state: str) -> Tuple[float, float]:
    # OpenStreetMap Nominatim (no key)
    url = "https://nominatim.openstreetmap.org/search"
    r = requests.get(url, params={"q": city_state, "format":"json", "limit":1},
                     headers={"User-Agent":"SmithEquivalencePyto/1.0"}, timeout=20)
    r.raise_for_status()
    data = r.json()
    if not data:
        sys.exit("Could not geocode location.")
    return float(data[0]["lat"]), float(data[0]["lon"])

def detect_utc_offset_hours(lat: float, lon: float) -> float:
    # Open-Meteo free API returns utc_offset_seconds and timezone name (no key)
    url = "https://api.open-meteo.com/v1/forecast"
    r = requests.get(url, params={"latitude":lat, "longitude":lon, "timezone":"auto", "current":"temperature"},
                     headers={"User-Agent":"SmithEquivalencePyto/1.0"}, timeout=20)
    r.raise_for_status()
    j = r.json()
    # utc_offset_seconds may not always be present; compute from "utc_offset_seconds" if available,
    # else fallback using "timezone_abbreviation" heuristic (rare).
    if "utc_offset_seconds" in j:
        return float(j["utc_offset_seconds"]) / 3600.0
    # Fallback: assume zero (UTC) if not provided (very rare)
    return 0.0

def write_wave(path: str, freq: float, duration: float = DURATION, samplerate: int = SAMPLE_RATE):
    t = np.linspace(0.0, duration, int(samplerate*duration), endpoint=False)
    sig = np.sin(2.0 * math.pi * freq * t)
    pcm = (sig * 32767.0).astype(np.int16)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(samplerate)
        wf.writeframes(pcm.tobytes())

def fmt(x: float, n=6) -> str:
    return f"{x:.{n}f}"

# ---- main ----
def main():
    say("🔮 Smith Equivalence — Pyto App (auto UTC offset + progress)\n")

    # [1/6] Inputs
    say("[1/6] Gathering inputs…")
    date_s = ask("Date (YYYY-MM-DD)")
    time_s = ask("Time (HH:MM 24h)")
    city   = ask("City, State (e.g., Spokane, WA)")

    # Parse local date/time
    try:
        local_dt = dt.datetime.strptime(f"{date_s} {time_s}", "%Y-%m-%d %H:%M")
    except ValueError:
        sys.exit("Bad date/time format. Use YYYY-MM-DD and HH:MM (24h).")

    # [2/6] Geocode + UTC offset
    say("[2/6] Geocoding location…")
    lat, lon = geocode_city(city)
    say(f"    Location: {city}  lat={fmt(lat,4)}  lon={fmt(lon,4)}")
    say("    Detecting UTC offset from location…")
    utc_off = detect_utc_offset_hours(lat, lon)
    say(f"    UTC offset detected: {fmt(utc_off,2)} hours")

    # Convert to UTC
    utc_dt = local_dt - dt.timedelta(hours=utc_off)

    # [3/6] Sidereal/Galactic parameters
    say("[3/6] Computing sidereal + galactic parameters…")
    jd = jd_from_datetime(utc_dt)
    lst = lst_hours(jd, lon)
    H   = hour_angle(lst, RA_GC_H)
    alt_gc = altitude_deg(lat, DEC_GC_DEG, H)
    say(f"    JD(UTC)={fmt(jd,5)}  LST={fmt(lst,3)}h  GC H={fmt(H,3)}h  GC Alt={fmt(alt_gc,2)}°")

    # [4/6] Cycle + harmonic selection
    say("[4/6] Choose cycle:")
    for k, v in CYCLES.items():
        say(f"    {k}. {v[0]}")
    ckey = ask("Cycle", str)
    if ckey not in CYCLES:
        sys.exit("Bad cycle choice.")
    name, T, f0_nhz = CYCLES[ckey]
    n = ask("Harmonic n", int)

    # [5/6] Smith Equivalence math
    say("[5/6] Applying Smith Equivalence math…")
    f0_hz   = f0_nhz * 1e-9
    fn_nhz  = n * f0_nhz
    if name == "Sidereal Day":
        phase = (H % 24.0) / 24.0
        visibility = max(0.0, math.sin(math.radians(alt_gc)))
        fn_nhz *= phase * visibility
    fn_hz = fn_nhz * 1e-9
    audible = owm_to_audible(fn_hz, f0_hz, F_MIN, F_MAX)
    say(f"    Cosmic f_n={fmt(fn_nhz,6)} nHz  ({fmt(fn_hz,12)} Hz)  →  Audible={fmt(audible,3)} Hz")

    # [6/6] File outputs
    say("[6/6] Writing files…")
    base = f"{name.replace(' ','_')}_n{n}_{local_dt.strftime('%Y%m%d_%H%M')}"
    wav_path = os.path.abspath(base + ".wav")
    md_path  = os.path.abspath(base + ".md")

    write_wave(wav_path, audible, DURATION, SAMPLE_RATE)

    md = f"""# Cosmic → Audible Frequency Log

**Cycle:** {name}  
**n:** {n}  

**Local Date/Time:** {local_dt} (UTC{utc_off:+.1f})  
**UTC Date/Time:** {utc_dt}  
**Julian Date (UTC):** {fmt(jd,5)}  

**Location:** {city}  
**Lat/Lon:** {fmt(lat,6)} / {fmt(lon,6)}  
**Local Sidereal Time:** {fmt(lst,4)} h  
**Galactic Center RA/Dec (J2000):** {fmt(RA_GC_DEG,6)}° / {fmt(DEC_GC_DEG,6)}°  
**GC Hour Angle:** {fmt(H,4)} h  
**GC Altitude:** {fmt(alt_gc,4)}°  

**f0 (base):** {fmt(f0_nhz,6)} nHz  ({fmt(f0_hz,12)} Hz)  
**f_n (cosmic):** {fmt(fn_nhz,6)} nHz  ({fmt(fn_hz,12)} Hz)  
**Audible (OWM):** {fmt(audible,6)} Hz  (band {int(F_MIN)}–{int(F_MAX)} Hz)

**Declaration:** This tone of {fmt(audible,3)} Hz is the {n}th harmonic of the {name}.  
Because it is represented under the Smith Equivalence Formula, it is the cosmic frequency {fmt(fn_nhz,6)} nHz.
"""

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md)

    say("✅ Done.")
    say(f"    WAV: {wav_path}")
    say(f"    Log: {md_path}")

if __name__ == "__main__":
    main()