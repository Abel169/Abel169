"""Original kora-style music (Karplus-Strong plucked strings + calabash percussion).
Usage: python3 music_kora.py out.wav DUR [build_times...]"""
import sys, numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt
SR = 44100
out = sys.argv[1]; DUR = float(sys.argv[2]); BUILD = [float(x) for x in sys.argv[3:]]
N = int(DUR * SR); L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(7)

def ks(freq, dur, bright=.5, decay=.996):
    n = int(dur * SR); p = int(SR / freq)
    buf = rng.uniform(-1, 1, p); buf = sosfilt(butter(1, 2000 + bright * 6000, fs=SR, output='sos'), buf)
    y = np.zeros(n)
    for i in range(n):
        y[i] = buf[i % p]
        buf[i % p] = decay * .5 * (buf[i % p] + buf[(i + 1) % p])
    y *= np.exp(-np.arange(n) / SR * 1.6)
    return y

cache = {}
def pluck(f, dur=1.6, bright=.5):
    k = (round(f, 2), dur, bright)
    if k not in cache: cache[k] = ks(f, dur, bright)
    return cache[k]

def add(sig, t, g=1., pan=0.):
    i = int(t * SR)
    if i >= N: return
    s = sig[:N - i] * g
    L[i:i + len(s)] += s * (1 - pan) * .5 * 2 ** .5 * .71
    R[i:i + len(s)] += s * (1 + pan) * .5 * 2 ** .5 * .71

def hz(m): return 440 * 2 ** ((m - 69) / 12)
BPM = 100; B = 60 / BPM; E8 = B / 2
# F major. chord cycle F  C  Bb  C  (2 beats each? -> 1 bar each)
CH = [(53, [65, 69, 72, 77]), (48, [64, 67, 72, 76]), (46, [62, 65, 70, 74]), (48, [64, 67, 72, 79])]
PAT = [0, 2, 1, 3, 2, 1, 3, 2]   # 8 eighths per bar, index into chord tones
def intensity(t):
    x = .55
    for b in BUILD: x += .15 * np.clip((t - b) / 2, 0, 1)
    return min(x, 1.0)

bar = 0; t = 0.0
while t < DUR:
    root, tones = CH[bar % 4]; I = intensity(t)
    add(pluck(hz(root - 12), 2.4, .2), t, .55, -.2)                 # thumb bass
    add(pluck(hz(root - 12 + 7), 1.6, .2), t + 2 * B, .35, -.2)
    for k, ix in enumerate(PAT):
        tt = t + k * E8 + (0.012 if k % 2 else 0)                     # slight swing
        add(pluck(hz(tones[ix]), 1.4, .55), tt, .32 * (1 if k % 2 == 0 else .8), .25 if k % 2 else -.05)
    # improvised run every 4 bars after the intro
    if bar % 4 == 3 and t > 6:
        sc = [72, 74, 76, 77, 79, 81, 84]
        for j in range(6): add(pluck(hz(sc[(j * 3 + bar) % 7]), 1.0, .7), t + 2 * B + j * B / 3, .22 * I, .35)
    # calabash percussion
    for bt in range(4):
        tb = t + bt * B
        if tb > 2.0:
            n = int(.25 * SR); env = np.exp(-np.arange(n) / SR * 22)
            thud = np.sin(2 * np.pi * 70 * np.arange(n) / SR) * env
            if bt in (0, 2): add(thud, tb, .55 * I)
            sh = rng.uniform(-1, 1, int(.06 * SR)) * np.exp(-np.arange(int(.06 * SR)) / SR * 70)
            sh = sosfilt(butter(2, 5000, 'high', fs=SR, output='sos'), sh)
            add(sh, tb + E8, .08 * I, .4); add(sh, tb, .05 * I, -.4)
    t += 4 * B; bar += 1

st = np.stack([L, R], 1)
# small room reverb
for d, g in ((.031, .25), (.053, .18), (.089, .12), (.13, .08)):
    k = int(d * SR); st[k:] += st[:-k] * g
fi = int(1.5 * SR); st[:fi] *= np.linspace(0, 1, fi)[:, None]
fo = int(2.5 * SR); st[-fo:] *= np.linspace(1, 0, fo)[:, None]
st = st / np.max(np.abs(st)) * .85
wavfile.write(out, SR, (st * 32767).astype(np.int16))
print('ok', DUR)
