#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Smith Equivalence Law -- Cosmic → Audible (OWM)
Sidereal + Galactic Integration • Pyto iOS Edition • v7.1

Changes in v7.1
- Reordered Event Mode menu: 1, 4, 3, 2
- New event logic:
    1. Single ALL-DAY date → 00:00 → 23:59 (same day) → averaged
    4. Single DATE + TIME RANGE → start → end (same day) → averaged
    3. DATE RANGE ONLY → each day 00:00 → 23:59 → averaged per day
    2. DATE RANGE + TIME RANGE → 
         - start date: 00:00 → 23:59
         - intermediate dates: 00:00 → 23:59
         - end date: 00:00 → specified end time
         → averaged per day
- Each expanded day yields exactly ONE tone + ONE Grimoire log
- Astronomy math for full-day blocks is done by sampling 2 endpoints and averaging
"""

import sys, os, math, datetime as dt, wave, struct

def say(msg): 
    print(msg, flush=True)

try:
    import numpy as np, requests
except Exception:
    sys.exit("Install deps: pip install numpy requests")

# --- constants ----------------------------------------------------
F_MIN, F_MAX = 55.0, 1760.0
RA_GC_DEG, DEC_GC_DEG = 266.404988, -29.007807
RA_GC_H = RA_GC_DEG / 15.0
SAMPLE_RATE = 44100
DURATION = 60.0  # seconds

CYCLES = {
    "1": ("Sidereal Day", 86164.091, 11605.8),
    "2": ("Synodic Month", 2551443, 391.935),
    "3": ("Tropical Year", 31556925.2, 31.689),
    "4": ("Nodal Cycle (18.6 y)", 586953600, 1.704),
    "5": ("Precession (25,772 y)", 813532800000, 0.001229),
    "6": ("Galactic Year (~225M y)", 7.1e15, 1.41e-13),
}

# --- astronomy ----------------------------------------------------
def jd_from_datetime(t_utc):
    y, m = t_utc.year, t_utc.month
    d = t_utc.day + (t_utc.hour + t_utc.minute/60 + t_utc.second/3600)/24
    if m <= 2:
        y -= 1
        m += 12
    A = y // 100
    B = 2 - A + A // 4
    return int(365.25*(y+4716)) + int(30.6001*(m+1)) + d + B - 1524.5

def gmst_deg(jd):
    return (280.46061837 + 360.98564736629*(jd - 2451545.0)) % 360

def lst_hours(jd, lon):
    return (gmst_deg(jd) + lon) % 360 / 15

def hour_angle(lst, ra):
    return (lst - ra) % 24

def altitude_deg(lat, dec, H):
    φ, δ, H = map(math.radians, [lat, dec, H*15])
    s = math.sin(φ)*math.sin(δ) + math.cos(φ)*math.cos(δ)*math.cos(H)
    return math.degrees(math.asin(max(-1, min(1, s))))

def owm_to_audible(cosmic_hz, f0_hz, fmin=F_MIN, fmax=F_MAX):
    if f0_hz <= 0 or cosmic_hz <= 0:
        return 0.0
    f = cosmic_hz * (220.0 / f0_hz)
    if f < fmin:
        k = max(0, int(math.ceil(math.log(fmin/f, 2))))
        f *= (2.0 ** k)
    elif f > fmax:
        k = max(0, int(math.ceil(math.log(f/fmax, 2))))
        f /= (2.0 ** k)
    return f

# --- helpers -------------------------------------------------------
def ask(q, caster=str):
    v = input(q + ": ").strip()
    if caster is str:
        return v
    try:
        return caster(v)
    except:
        sys.exit(f"Invalid input for {q}")

def geocode_city(q):
    r = requests.get(
        "https://nominatim.openstreetmap.org/search",
        params={"q": q, "format": "json", "limit": 1},
        headers={"User-Agent": "SmithEquivalencePyto/1.0"},
        timeout=20,
    )
    j = r.json()
    if not j:
        sys.exit("Location not found.")
    return float(j[0]["lat"]), float(j[0]["lon"])

def detect_utc_offset_hours(lat, lon):
    r = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={"latitude": lat, "longitude": lon, "timezone": "auto"},
        headers={"User-Agent": "SmithEquivalencePyto/1.0"},
        timeout=20,
    )
    j = r.json()
    return j.get("utc_offset_seconds", 0) / 3600.0

def generate_sine_wave(filename, freq_hz):
    samples = (np.sin(2*np.pi*np.arange(int(SAMPLE_RATE*DURATION))*freq_hz/SAMPLE_RATE))
    with wave.open(filename, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        for s in samples:
            wf.writeframes(
                struct.pack('<h', int(max(-1, min(1, s)) * 32767))
            )

# --- date/time utils -----------------------------------------------
def parse_date(s):
    try:
        return dt.datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        sys.exit("Invalid date, use YYYY-MM-DD")

def parse_time(s):
    try:
        return dt.datetime.strptime(s, "%H:%M").time()
    except ValueError:
        sys.exit("Invalid time, use HH:MM 24h")

def daterange(start_date, end_date):
    # inclusive
    for n in range((end_date - start_date).days + 1):
        yield start_date + dt.timedelta(days=n)

# --- astronomy sampling/averaging ----------------------------------
def compute_slot_average(
    local_start_dt: dt.datetime,
    local_end_dt: dt.datetime,
    lat: float,
    lon: float,
    utc_off: float,
    f0_nhz: float,
    n: int
):
    """
    Sample at start and end of the slot, average the weights and resulting cosmic
    frequency. This keeps output = 1 tone/log per slot but respects 00:00–23:59.
    """
    # convert to UTC
    utc_start = local_start_dt - dt.timedelta(hours=utc_off)
    utc_end   = local_end_dt   - dt.timedelta(hours=utc_off)

    # helper to compute one instant
    def instant_calc(utc_dt):
        jd = jd_from_datetime(utc_dt)
        lst = lst_hours(jd, lon)
        H = hour_angle(lst, RA_GC_H)
        alt_gc = altitude_deg(lat, DEC_GC_DEG, H)

        fn_nhz_raw = n * f0_nhz
        fn_hz_raw = fn_nhz_raw * 1e-9

        W_phase = 0.5 * (1.0 + math.cos(2.0*math.pi*(H/24.0)))
        W_alt = max(0.0, (math.sin(math.radians(alt_gc)) + 1.0) * 0.5)
        W = max(1e-12, W_phase * W_alt)

        fn_nhz_repr = fn_nhz_raw * W
        fn_hz_repr = fn_nhz_repr * 1e-9

        return {
            "utc_dt": utc_dt,
            "jd": jd,
            "lst": lst,
            "H": H,
            "alt_gc": alt_gc,
            "W_phase": W_phase,
            "W_alt": W_alt,
            "W": W,
            "fn_nhz_raw": fn_nhz_raw,
            "fn_hz_raw": fn_hz_raw,
            "fn_nhz_repr": fn_nhz_repr,
            "fn_hz_repr": fn_hz_repr,
        }

    start_res = instant_calc(utc_start)
    end_res   = instant_calc(utc_end)

    # average what matters
    avg = {}
    for key in [
        "jd", "lst", "H", "alt_gc",
        "W_phase", "W_alt", "W",
        "fn_nhz_raw", "fn_hz_raw",
        "fn_nhz_repr", "fn_hz_repr"
    ]:
        avg[key] = (start_res[key] + end_res[key]) / 2.0

    # pick a representative UTC for logging (midpoint)
    avg_utc = utc_start + (utc_end - utc_start) / 2
    avg["utc_dt"] = avg_utc

    return avg

# --- event expansion -----------------------------------------------
def expand_event_mode(mode: str):
    """
    Returns list of slots.
    Each slot = dict with:
        {
            "local_start": datetime,
            "local_end": datetime,
            "label": str,  # for filenames
        }
    """
    slots = []

    if mode == "1":
        # Single ALL-DAY date → 00:00 to 23:59 same day
        d = parse_date(ask("Date (YYYY-MM-DD)"))
        local_start = dt.datetime.combine(d, dt.time(0, 0))
        local_end   = dt.datetime.combine(d, dt.time(23, 59))
        slots.append({
            "local_start": local_start,
            "local_end": local_end,
            "label": d.strftime("%Y%m%d"),
        })

    elif mode == "4":
        # Single date + time range → start → end on same day
        d = parse_date(ask("Date (YYYY-MM-DD)"))
        t_start = parse_time(ask("Start time (HH:MM 24h)"))
        t_end   = parse_time(ask("End time (HH:MM 24h)"))
        if t_end < t_start:
            sys.exit("End time must be >= start time for single date.")
        local_start = dt.datetime.combine(d, t_start)
        local_end   = dt.datetime.combine(d, t_end)
        slots.append({
            "local_start": local_start,
            "local_end": local_end,
            "label": d.strftime("%Y%m%d"),
        })

    elif mode == "3":
        # Date RANGE only → each day 00:00 → 23:59
        d1 = parse_date(ask("Start date (YYYY-MM-DD)"))
        d2 = parse_date(ask("End date (YYYY-MM-DD)"))
        if d2 < d1:
            sys.exit("End date must be >= start date")
        for d in daterange(d1, d2):
            local_start = dt.datetime.combine(d, dt.time(0, 0))
            local_end   = dt.datetime.combine(d, dt.time(23, 59))
            slots.append({
                "local_start": local_start,
                "local_end": local_end,
                "label": d.strftime("%Y%m%d"),
            })

    elif mode == "2":
        # Date RANGE + Time RANGE
        # Start date: 00:00 - 23:59
        # Intermediate dates: 00:00 - 23:59
        # End date: 00:00 - specified end time
        d1 = parse_date(ask("Start date (YYYY-MM-DD)"))
        d2 = parse_date(ask("End date (YYYY-MM-DD)"))
        if d2 < d1:
            sys.exit("End date must be >= start date")
        end_time = parse_time(ask("End time on end date (HH:MM 24h)"))

        current = d1
        while current <= d2:
            if current == d1 and current == d2:
                # same day range: 00:00 → end_time
                local_start = dt.datetime.combine(current, dt.time(0, 0))
                local_end   = dt.datetime.combine(current, end_time)
            elif current == d1:
                # first day: 00:00 → 23:59
                local_start = dt.datetime.combine(current, dt.time(0, 0))
                local_end   = dt.datetime.combine(current, dt.time(23, 59))
            elif current == d2:
                # last day: 00:00 → specified end_time
                local_start = dt.datetime.combine(current, dt.time(0, 0))
                local_end   = dt.datetime.combine(current, end_time)
            else:
                # intermediate
                local_start = dt.datetime.combine(current, dt.time(0, 0))
                local_end   = dt.datetime.combine(current, dt.time(23, 59))

            slots.append({
                "local_start": local_start,
                "local_end": local_end,
                "label": current.strftime("%Y%m%d"),
            })
            current += dt.timedelta(days=1)

    else:
        sys.exit("Invalid event mode")

    return slots

# --- main ----------------------------------------------------------
def main():
    say("🔮 Smith Equivalence -- v7.1 (Event-Accurate)\n")
    say("Event modes:")
    say("  1. Single ALL-DAY date (00:00 → 23:59)")
    say("  4. Single date + TIME RANGE (same date)")
    say("  3. DATE RANGE only (each day 00:00 → 23:59)")
    say("  2. DATE RANGE + TIME RANGE (start 00:00 → end-date time)")
    event_mode = ask("Select event mode (1/4/3/2)")

    slots = expand_event_mode(event_mode)
    say(f"📅 Expanded into {len(slots)} slot(s).")

    city = ask("City, State (or type ENTER EXACT)")

    if city.strip().upper() == "ENTER EXACT":
        lat = ask("Latitude (decimal degrees)", float)
        lon = ask("Longitude (decimal degrees)", float)
    else:
        say("📡 Locating + timezone detection…")
        lat, lon = geocode_city(city)

    utc_off = detect_utc_offset_hours(lat, lon)

    # cycle selection
    say("\nSelect cycle:")
    for k, v in CYCLES.items():
        say(f"  {k}. {v[0]}")
    ckey = ask("Cycle", str)
    if ckey not in CYCLES:
        sys.exit("Invalid cycle")
    name, _, f0_nhz = CYCLES[ckey]
    n = ask("Harmonic n", int)

    f0_hz = f0_nhz * 1e-9

    for slot in slots:
        local_start = slot["local_start"]
        local_end   = slot["local_end"]
        label       = slot["label"]

        say(f"\n🪐 Slot: {local_start} → {local_end}")

        avg = compute_slot_average(
            local_start,
            local_end,
            lat,
            lon,
            utc_off,
            f0_nhz,
            n
        )

        # map averaged cosmic to audible
        audible_repr = owm_to_audible(avg["fn_hz_repr"], f0_hz)
        audible_repr_out = f"{audible_repr:.6f}"

        say(f"    JD≈{avg['jd']:.5f}  LST≈{avg['lst']:.5f}h  GC Alt≈{avg['alt_gc']:.3f}°")
        say(f"    Weights: phase={avg['W_phase']:.5f} altitude={avg['W_alt']:.5f} composite={avg['W']:.5f}")
        say(f"    🎚 Represented Audible Frequency: {audible_repr_out} Hz")

        # filenames
        base = f"{name.replace(' ','_')}_n{n}_{label}"
        md_path = os.path.abspath(base + "_GrimoireLog.md")
        wav_path = os.path.abspath(base + "_Tone.wav")

        say("    🎧 Generating 60-second tone…")
        generate_sine_wave(wav_path, audible_repr)
        say(f"        Saved tone → {wav_path}")

        # log
        local_mid = local_start + (local_end - local_start) / 2
        md = f"""# Cosmic → Audible Frequency Log (v7.1)

**Event Mode:** {event_mode}  
**Cycle:** {name}  
**Harmonic (n):** {n}  

**Local Window:** {local_start} → {local_end}  
**Representative Local Time:** {local_mid} (UTC{utc_off:+.2f})  
**Representative UTC:** {avg['utc_dt']}  
**Julian Date (avg):** {avg['jd']}  

**Location:** {city}  
**Latitude:** {lat}°  
**Longitude:** {lon}°  
**Local Sidereal Time (avg):** {avg['lst']} h  
**Galactic Center Hour Angle (avg):** {avg['H']} h  
**Galactic Center Altitude (avg):** {avg['alt_gc']}°  

**Weights (averaged over slot)**  
- Phase = {avg['W_phase']}  
- Altitude = {avg['W_alt']}  
- Composite = {avg['W']}  

**Base f₀:** {f0_nhz} nHz ({f0_hz} Hz)  
**Cosmic fₙ (raw):** {avg['fn_nhz_raw']} nHz ({avg['fn_hz_raw']} Hz)  
**Cosmic fₙ (Represented):** {avg['fn_nhz_repr']} nHz ({avg['fn_hz_repr']} Hz)  
**Audible (OWM):** {audible_repr_out} Hz  

**Tone File:** {wav_path}  
"""
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md)
        say(f"    🪶 Log saved → {md_path}")

    say("\n✅ Complete. All slots processed.")

if __name__ == "__main__":
    main()