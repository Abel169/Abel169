"""Synthesized sound effects for the Mamy Délices spot, synced to index.html timings.
Usage: python3 sfx.py out.wav  (26 s, 44.1 kHz stereo)"""
import sys
import numpy as np
from scipy.signal import butter, sosfilt
from scipy.io import wavfile

SR = 44100; DUR = 30.0; N = int(SR * DUR)
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


# ---------------- Mamy Délices timings
for i in range(3): add(tick(2400 + i * 100), .1 + i * .09, .4)
for i in range(2): add(pop(600 + i * 150), .5 + i * .09, .5)
add(whoosh(.5, True), .3, .4)
add(pop(500), .85, .6); add(pop(900), 1.25, .6); add(bell(88, .6), 1.3, .3)
add(whoosh(.6, lo=200, hi=2500), 2.55, .5)
add(impact(1.6), 3.2, .7); add(confetti(), 3.25, .6); add(bell(84, 1.4), 3.4, .5); add(bell(91, 1.2), 3.5, .35)
for i in range(16): add(tick(2200 + i * 40), 4.2 + i * .045, .2)
add(whoosh(.5, lo=400, hi=9000), 6.3, .55)
for i in range(6): add(pop(500 + i * 110), 7.7 + i * .42, .6, (-1) ** i * .5)
for t in (8.0, 9.4, 10.8): add(whoosh(.4, True), t, .35, .3)
add(whoosh(.5), 12.2, .5)
for i in range(3): add(pop(700), 12.8 + i * .12, .4)
add(tick(2600), 14.2, .9); add(whoosh(.4), 14.55, .4)
add(tick(2600), 15.55, .9); add(pop(800), 15.65, .5)
add(tick(2600), 16.5, .9); add(pop(1000), 16.55, .6)
add(whoosh(.7, True), 17.4, .5); add(kaching(), 18.15, .8); add(confetti(), 18.2, .4)
add(whoosh(.45), 19.0, .5); add(impact(1.6), 19.4, .6); add(stamp(), 19.55, .6)
for i in range(4): add(whoosh(.35), 20.4 + i * .42, .35, (-1) ** i * .5); add(pop(600 + i * 120), 20.6 + i * .42, .4)
add(whoosh(.5), 23.05, .5)
add(pop(500), 23.6, .5); add(pop(700), 23.8, .5)
add(scan(1.8), 24.1, .25)
add(bell(88, 1.0), 25.95, .5); add(confetti(), 26.0, .35)
add(whoosh(.45, lo=400, hi=9000), 26.25, .55)
add(impact(2.0), 26.6, .7); add(shimmer(1.2), 26.7, .4); add(bell(84, 1.4), 26.9, .4)
for i in range(2): add(pop(650 + i * 200), 27.8 + i * .15, .5)

mix = np.tanh(FX * 1.0)
mix /= max(1e-9, np.max(np.abs(mix))) * 1.05
wavfile.write(sys.argv[1], SR, (mix * 32767).astype(np.int16)); print('ok')
