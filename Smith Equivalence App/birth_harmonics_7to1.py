# birth_harmonics_7to1_nogui.py
# Works in Pyto (no Tkinter). Just type your path when prompted.

import os, math, numpy as np, wave, aifc
from math import log2

def read_pcm(path):
    ext = os.path.splitext(path)[1].lower()
    opener = aifc.open if ext in [".aif", ".aiff"] else wave.open
    with opener(path, "rb") as f:
        n_channels = f.getnchannels()
        sampwidth  = f.getsampwidth()
        framerate  = f.getframerate()
        n_frames   = f.getnframes()
        raw = f.readframes(n_frames)
    if sampwidth == 2:
        data = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    elif sampwidth == 3:
        a = np.frombuffer(raw, dtype=np.uint8).reshape(-1,3)
        b = (a[:,2].astype(np.int32)<<24)|(a[:,1].astype(np.int32)<<16)|(a[:,0].astype(np.int32)<<8)
        data = (b.view(np.int32).astype(np.float32)/(2**31))
    elif sampwidth == 4:
        data = np.frombuffer(raw, dtype=np.int32).astype(np.float32)/(2**31)
    else:
        raise ValueError("Unsupported sample width")
    if n_channels > 1:
        data = data.reshape(-1,n_channels).mean(axis=1)
    return data, framerate

def hann(x): return x*np.hanning(len(x))

def rfft_mag(x,sr):
    N=min(len(x),int(sr*8))
    if N<sr: N=len(x)
    win=hann(x[:N])
    spec=np.fft.rfft(win)
    mag=np.abs(spec)
    freqs=np.fft.rfftfreq(N,1.0/sr)
    return freqs,mag

def peak_freq(freqs,mag,fmin=20,fmax=2000):
    mask=(freqs>=fmin)&(freqs<=fmax)
    if not np.any(mask): return None,None
    idx=np.argmax(mag[mask]); true_idx=np.where(mask)[0][0]+idx
    return freqs[true_idx],mag[true_idx]

def nearest_peak_around(freqs,mag,target_hz,window_cents=50):
    if target_hz<=0: return None,None,None
    r=2**(window_cents/1200.0)
    lo,hi=target_hz/r,target_hz*r
    mask=(freqs>=lo)&(freqs<=hi)
    if not np.any(mask): return None,None,None
    idx=np.argmax(mag[mask]); true_idx=np.where(mask)[0][0]+idx
    f=freqs[true_idx]; a=mag[true_idx]
    cents=1200*log2(f/target_hz)
    return f,a,cents

def sixdp(x): return f"{x:.6f}"

def main():
    path=input("Enter full path to your AIFF/WAV file:\n").strip()
    if not os.path.exists(path):
        print("File not found."); return
    x,sr=read_pcm(path)
    freqs,mag=rfft_mag(x,sr)
    f0,a0=peak_freq(freqs,mag,20,2000)
    if f0 is None: print("No fundamental found."); return

    rows=[]
    for n in range(1,8):
        target=n*f0
        f,a,c=nearest_peak_around(freqs,mag,target,60)
        rows.append((n,target,f,a,c))

    base=os.path.splitext(path)[0]
    csv_path=base+"_report.csv"
    txt_path=base+"_rep.txt"
    with open(csv_path,"w") as f:
        f.write("n,target_Hz,measured_Hz,amplitude,cents_deviation\n")
        for n,tgt,meas,amp,c in rows:
            f.write(f"{n},{sixdp(tgt)},{sixdp(meas) if meas else ''},{amp if amp else ''},{round(c,6) if c else ''}\n")

    rep=f"Representation: Self’s Birth Harmonic (n=1) ≡ {sixdp(f0)} Hz"
    with open(txt_path,"w") as f: f.write(rep+"\n")

    print(rep)
    print("CSV:",csv_path)
    print("Done.")

if __name__=="__main__":
    main()