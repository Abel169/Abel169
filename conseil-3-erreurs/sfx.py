"""Synthesized sound effects for the 3 erreurs TikTok, synced to index.html timings.
Usage: python3 sfx.py out.wav  (26 s, 44.1 kHz stereo)"""
import sys
import numpy as np
from scipy.signal import butter, sosfilt
from scipy.io import wavfile

SR = 44100; DUR = 36.5; N = int(SR * DUR)
rng = np.random.default_rng(4)
FX = np.zeros((N, 2))
lp = lambda x, f, o=2: sosfilt(butter(o, f, 'low', fs=SR, output='sos'), x)
hp = lambda x, f, o=2: sosfilt(butter(o, f, 'high', fs=SR, output='sos'), x)
bp = lambda x, a, b, o=2: sosfilt(butter(o, [a, b], 'band', fs=SR, output='sos'), x)
tt = lambda d: np.arange(int(d * SR)) / SR
note = lambda n: 440 * 2 ** ((n - 69) / 12)


def add(sig, t, g=1.0, pan=0.0):
    i = int(t * SR)
    if i >= N or i < 0: return
    sig = sig[:N - i]
    FX[i:i + len(sig), 0] += sig * g * np.sqrt(.5 * (1 - pan)); FX[i:i + len(sig), 1] += sig * g * np.sqrt(.5 * (1 + pan))


def whoosh(d, rev=False, lo=300, hi=7000):
    t = tt(d); n = rng.standard_normal(len(t)); out = np.zeros_like(n)
    for i in range(0, len(t), 1024):
        fc = lo + (hi - lo) * (i / len(t)) ** 2
        seg = bp(n[max(0, i - 2048):i + 1024], fc * .6, min(fc * 1.6, 20000)); out[i:i + 1024] = seg[-len(n[i:i + 1024]):]
    s = out * np.sin(np.pi * np.clip(t / d, 0, 1)) ** 1.5
    return s[::-1] if rev else s


def riser(d):
    t = tt(d); f = 180 * 2 ** (t / d * 3.5)
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * .3 * (t / d) ** 2
    return tone + whoosh(d) * .8 * (t / d)


def impact(d=1.8):
    t = tt(d); f = 32 + 80 * np.exp(-t * 7)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.6)
    return np.tanh((boom * 1.4 + lp(rng.standard_normal(len(t)), 3500) * np.exp(-t * 7) * .5) * 1.3)


def pop(f=600):
    t = tt(.12); fr = f * (1 + 1.5 * np.exp(-t * 60))
    return np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * 35) * .8


def tick(f=3000):
    t = tt(.03); return np.sin(2 * np.pi * f * t) * np.exp(-t * 220) * .6


def bell(n, d=1.0):
    t = tt(d); return sum(np.sin(2 * np.pi * note(n + o) * t) * a for o, a in [(0, 1), (12, .5), (19, .25), (24, .12)]) * np.exp(-t * 4.5) * .35


def kaching():
    s = np.zeros(int(1.3 * SR)); b1 = bell(88, 1.2); b2 = bell(95, 1.1)
    s[:len(b1)] += b1; s[int(.06 * SR):int(.06 * SR) + len(b2)] += b2 * .8
    n = hp(rng.standard_normal(int(.25 * SR)), 5000) * np.exp(-tt(.25) * 25) * .35; s[:len(n)] += n
    return s


def stamp():
    t = tt(.5); f = 70 + 90 * np.exp(-t * 45)
    return np.tanh((np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 11) + hp(rng.standard_normal(len(t)), 1500) * np.exp(-t * 70) * .5) * 1.6)


def scratch(d=.3):
    t = tt(d); n = rng.standard_normal(len(t))
    return bp(n, 1800, 6000) * np.exp(-((t - d / 2) / (d / 3)) ** 2) * .9


def sad():
    t = tt(.7); f = 520 * np.exp(-t * 1.6)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3) * .45


def shimmer(d=1.0):
    s = np.zeros(int(d * SR))
    for i in range(14):
        b = bell(84 + (i * 5) % 17, .5) * .5; k = int(i * d / 14 * SR); s[k:k + len(b)] += b[:len(s) - k]
    return s


def scan(d):
    t = tt(d); n = rng.standard_normal(len(t)); out = np.zeros_like(n)
    for i in range(0, len(t), 1024):
        fc = 600 + 5000 * (i / len(t))
        seg = bp(n[max(0, i - 2048):i + 1024], fc * .85, fc * 1.15, 4); out[i:i + 1024] = seg[-len(n[i:i + 1024]):]
    hum = np.sin(2 * np.pi * (220 + 300 * t / d) * t) * .15
    return (out * 1.6 + hum) * np.sin(np.pi * t / d)


def confetti():
    s = np.zeros(int(1.2 * SR))
    for i in range(30):
        k = int(rng.random() * .9 * SR); p = pop(900 + rng.random() * 1500) * .25; s[k:k + len(p)] += p[:len(s) - k]
    return s + hp(rng.standard_normal(len(s)), 3000) * np.exp(-tt(1.2) * 6) * .25


# ---------------- 3 erreurs timings
add(pop(800),1.0,.4); add(pop(600),1.3,.4)
for i in range(10): add(tick(2400),1.0+i*.18,.15)
add(whoosh(.5),3.0,.5); add(impact(1.4),3.75,.55)
for k,(e,f) in enumerate([(6.4,11.4),(13.9,19.2),(22.0,27.6)]):
    add(whoosh(.35,True),e-.3,.4); add(stamp(),e+.05,.35); add(sad(),f-.9,.25); add(stamp(),f-.85,.4)
    add(whoosh(.35),f-.1,.3); add(bell(84,.8),f+.05,.35); add(shimmer(.8),f+.15,.25)
add(whoosh(.6,True),9.3,.45)
for i in range(4): add(tick(2200),15.7+i*.1,.2)
for i in range(4): add(tick(2200),16.4+i*.1,.2)
add(kaching(),19.4,.45)
add(pop(900),22.6,.4)
for i in range(8): add(tick(2600),24.6+i*.15,.25)
add(pop(700),26.0,.4); add(pop(900),27.9,.4); add(kaching(),28.7,.4)
add(whoosh(.6),29.6,.5); add(impact(1.4),29.9,.45)
for i in range(3): add(pop(600+i*120),30.7+i*.25,.35)
add(pop(1000),31.5,.45); add(shimmer(1.0),33.3,.35); add(stamp(),33.4,.35)

mix = np.tanh(FX * 1.0)
mix /= max(1e-9, np.max(np.abs(mix))) * 1.05
wavfile.write(sys.argv[1], SR, (mix * 32767).astype(np.int16)); print('ok')
