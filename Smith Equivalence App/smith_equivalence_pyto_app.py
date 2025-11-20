#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pyto App: Smith Equivalence Law — Cosmic → Audible (OWM) with Sidereal + Galactic Integration
Runs entirely in Pyto on iOS/iPadOS.
Prompts for: local date/time, UTC offset, City, State, cycle, harmonic n.
Outputs: a WAV tone file and a Markdown (.md) Grimoire log in the current Pyto working directory.
Requires: numpy, requests  (install in Pyto via pip if you don't have them)
"""

import os
import sys
import math
import wave
import datetime as dt
from typing import Tuple

def say(msg: str):
    print(msg, flush=True)

try:
    import numpy as np
except Exception:
    say("This app needs numpy. In Pyto, run:  pip install numpy")
    sys.exit(1)

try:
    import requests
except Exception:
    say("This app needs requests. In Pyto, run:  pip install requests")
    sys.exit(1)

DURATION_SEC = 2.0
SAMPLE_RATE  = 22050
F_MIN, F_MAX = 55.0, 1760.0

RA_GC_DEG   = 266.404988
DEC_GC_DEG  = -29.007807
RA_GC_HOURS = RA_GC_DEG / 15.0

CYCLES = {
    "1": {"name": "Sidereal Day",          "T": 86164.091,     "f0_nhz": 11605.8},
    "2": {"name": "Synodic Month",         "T": 2551443,       "f0_nhz": 391.935},
    "3": {"name": "Tropical Year",         "T": 31556925.2,    "f0_nhz": 31.689},
    "4": {"name": "Nodal Cycle (18.6 y)",  "T": 586953600,     "f0_nhz": 1.704},
    "5": {"name": "Precession (25,772 y)", "T": 813532800000,  "f0_nhz": 0.001229},
}

def jd_from_datetime(dt_utc: dt.datetime) -> float:
    year = dt_utc.year
    month = dt_utc.month
    day = dt_utc.day + (dt_utc.hour + dt_utc.minute/60 + dt_utc.second/3600)/24
    if month <= 2:
        year -= 1
        month += 12
    A = year // 100
    B = 2 - A + (A // 4)
    jd = int(365.25*(year + 4716)) + int(30.6001*(month + 1)) + day + B - 1524.5
    return float(jd)

def gmst_in_degrees(jd: float) -> float:
    T = (jd - 2451545.0)/36525.0
    GMST = 280.46061837 + 360.98564736629*(jd - 2451545.0) + 0.000387933*T*T - (T*T*T)/38710000.0
    return GMST % 360.0

def lst_in_hours(jd: float, longitude_deg: float) -> float:
    gmst_deg = gmst_in_degrees(jd)
    lst_deg = (gmst_deg + longitude_deg) % 360.0
    return lst_deg / 15.0

def hour_angle_hours(lst_hours: float, ra_hours: float) -> float:
    return (lst_hours - ra_hours) % 24.0

def altitude_of_object(lat_deg: float, dec_deg: float, H_hours: float) -> float:
    phi = math.radians(lat_deg)
    dec = math.radians(dec_deg)
    H_rad = math.radians(H_hours * 15.0)
    sin_h = math.sin(phi)*math.sin(dec) + math.cos(phi)*math.cos(dec)*math.cos(H_rad)
    sin_h = max(-1.0, min(1.0, sin_h))
    return math.degrees(math.asin(sin_h))

def owm_scale(cosmic_freq_hz: float, f0_hz: float, fmin: float = F_MIN, fmax: float = F_MAX) -> float:
    if f0_hz <= 0.0:
        raise ValueError("f0_hz must be positive.")
    S = 220.0 / f0_hz
    fprime = cosmic_freq_hz * S
    while fprime < fmin:
        fprime *= 2.0
    while fprime > fmax:
        fprime /= 2.0
    return fprime

def ask(prompt: str, caster=str):
    try:
        val = input(f"{prompt}: ").strip()
    except EOFError:
        say("\nInput aborted."); sys.exit(1)
    if caster is str:
        return val
    try:
        return caster(val)
    except Exception:
        say(f"Could not parse that as {caster.__name__}. You entered: {val}")
        sys.exit(1)

def geocode_city(city_state: str) -> Tuple[float, float]:
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": city_state, "format": "json", "limit": 1}
    headers = {"User-Agent": "Pyto-SmithEquivalence/1.0"}
    r = requests.get(url, params=params, headers=headers, timeout=20)
    r.raise_for_status()
    data = r.json()
    if not data:
        say(f"Could not geocode location: {city_state}")
        sys.exit(1)
    return float(data[0]["lat"]), float(data[0]["lon"])

def write_wave(filename: str, freq: float, duration: float = DURATION_SEC, samplerate: int = SAMPLE_RATE):
    t = np.linspace(0.0, duration, int(samplerate*duration), endpoint=False)
    wave_data = np.sin(2.0 * math.pi * freq * t)
    wave_data = (wave_data * 32767.0).astype(np.int16)
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(samplerate)
        wf.writeframes(wave_data.tobytes())

def fmt(x: float, digits: int = 6) -> str:
    return f"{x:.{digits}f}"

def main():
    say("🔮 Smith Equivalence — Pyto App (OWM + Sidereal + Galactic)\n")

    date_str = ask("Enter LOCAL date (YYYY-MM-DD or YYYY/MM/DD)")
    time_str = ask("Enter LOCAL time HH:MM (24h or add AM/PM, e.g., 06:30 PM)")
    tz_offset = ask("Enter your LOCAL UTC offset in hours (e.g., -7 for PDT, +1 for CET)", float)
    city_state = ask("Enter City, State (e.g., Spokane, WA)")

    # Parse date/time allowing AM/PM or 24h, and - or /
    dt_formats = ["%Y-%m-%d %I:%M %p", "%Y/%m/%d %I:%M %p", "%Y-%m-%d %H:%M", "%Y/%m/%d %H:%M"]
    local_dt = None
    for fmt_ in dt_formats:
        try:
            local_dt = dt.datetime.strptime(f"{date_str} {time_str}", fmt_)
            break
        except ValueError:
            continue
    if local_dt is None:
        say("Could not parse your date/time. Try '2025-10-04 06:00' or '2025/10/04 06:00 PM'."); sys.exit(1)

    utc_dt = local_dt - dt.timedelta(hours=tz_offset)

    say("📡 Geocoding location...")
    lat, lon = geocode_city(city_state)
    say(f"📍 {city_state}: lat={fmt(lat,4)}°, lon={fmt(lon,4)}°")

    say("🧮 Computing Julian Date + Sidereal parameters...")
    jd = jd_from_datetime(utc_dt)
    lst_hours = lst_in_hours(jd, lon)
    H_gc_hours = hour_angle_hours(lst_hours, RA_GC_HOURS)
    alt_gc_deg = altitude_of_object(lat, DEC_GC_DEG, H_gc_hours)
    say(f"🕰 JD(UTC)={fmt(jd,5)}  |  LST={fmt(lst_hours,3)} h  |  GC H={fmt(H_gc_hours,3)} h  |  GC Alt={fmt(alt_gc_deg,2)}°")

    say("\nChoose cycle:")
    for k in sorted(CYCLES.keys()):
        say(f"  {k}. {CYCLES[k]['name']}")
    cycle_key = ask("Enter choice number", str)
    if cycle_key not in CYCLES:
        say("Invalid cycle choice."); sys.exit(1)
    cycle = CYCLES[cycle_key]

    n = ask("Enter harmonic n (e.g., 4, 5, 7, 8, 12)", int)

    f0_nhz = cycle["f0_nhz"]
    f0_hz  = f0_nhz * 1e-9

    cosmic_nhz = n * f0_nhz
    if cycle["name"] == "Sidereal Day":
        phase_fraction = (H_gc_hours % 24.0) / 24.0
        visibility = max(0.0, math.sin(math.radians(alt_gc_deg)))
        cosmic_nhz *= phase_fraction * visibility

    cosmic_hz = cosmic_nhz * 1e-9

    say("🎚 Mapping to audible band (OWM)...")
    audible_hz = owm_scale(cosmic_hz, f0_hz, F_MIN, F_MAX)

    base = f"{cycle['name'].replace(' ', '_')}_n{n}_{local_dt.strftime('%Y%m%d_%H%M')}"
    wav_path = os.path.abspath(base + ".wav")
    md_path  = os.path.abspath(base + ".md")

    say(f"🎧 Generating {DURATION_SEC:.1f}s tone at {audible_hz:.3f} Hz → {os.path.basename(wav_path)}")
    write_wave(wav_path, audible_hz, DURATION_SEC, SAMPLE_RATE)
    say("✅ Tone generated.")

    md = []
    md.append("# Cosmic → Audible Frequency Log")
    md.append("")
    md.append(f"**Cycle**: {cycle['name']}")
    md.append(f"**Harmonic**: n={n}")
    md.append(f"**Local Date/Time**: {local_dt.strftime('%Y-%m-%d %H:%M')} (UTC offset {tz_offset:+.1f} h)")
    md.append(f"**UTC Date/Time**: {utc_dt.strftime('%Y-%m-%d %H:%M')}")
    md.append(f"**Julian Date (UTC)**: {fmt(jd,5)}")
    md.append(f"**Location**: {city_state}")
    md.append(f"**Latitude**: {fmt(lat,6)}°   **Longitude**: {fmt(lon,6)}°")
    md.append(f"**Local Sidereal Time**: {fmt(lst_hours,4)} h")
    md.append(f"**Galactic Center RA/Dec (J2000)**: {fmt(RA_GC_DEG,6)}° / {fmt(DEC_GC_DEG,6)}°")
    md.append(f"**GC Hour Angle**: {fmt(H_gc_hours,4)} h   **GC Altitude**: {fmt(alt_gc_deg,4)}°")
    md.append(f"**Base f₀**: {fmt(f0_nhz,6)} nHz  (**{fmt(f0_hz,12)} Hz**)")
    md.append(f"**Cosmic harmonic f_n**: {fmt(cosmic_nhz,6)} nHz  (**{fmt(cosmic_hz,12)} Hz**)")
    md.append(f"**Audible (OWM)**: {fmt(audible_hz,6)} Hz  (band {F_MIN:.0f}–{F_MAX:.0f} Hz)")
    md.append("")
    md.append(f"**Declaration**: This tone of {fmt(audible_hz,3)} Hz is the {n}th harmonic of the {cycle['name']}.")
    md.append(f"Because it is represented under the Smith Equivalence Formula, it is the cosmic frequency {fmt(cosmic_nhz,6)} nHz.")
    md.append("")
    md.append(f"**WAV file**: `{os.path.basename(wav_path)}`")

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("
".join(md))

    say("
✨ Results")
    say(f"Audible Frequency (OWM): {fmt(audible_hz,3)} Hz")
    say(f"Cosmic Frequency: {fmt(cosmic_nhz,6)} nHz  ({fmt(cosmic_hz,12)} Hz)")
    say(f"Log: {md_path}")
    say(f"WAV: {wav_path}")
    say("
Done.")

if __name__ == "__main__":
    main()
