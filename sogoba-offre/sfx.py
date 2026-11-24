"""Synthesized sound effects for the launch-offer video, synced to index.html timings.
Usage: python3 sfx.py out.wav  (26 s, 44.1 kHz stereo)"""
import sys
import numpy as np
from scipy.signal import butter, sosfilt
from scipy.io import wavfile

SR = 44100; DUR = 26.0; N = int(SR * DUR)
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


# ---------------- S1 hook 0–3.5
for i in range(4): add(tick(2600), .1 + i * .08, .5)
for i in range(6): add(tick(2200), .75 + i * .08, .4)
add(whoosh(.5, lo=200, hi=3000), 1.1, .6, -.3)
for i in range(12): add(tick(1800 + i * 60), 1.9 + i * .05, .35, .3)
add(sad(), 2.15, .8)
add(riser(.5), 3.0, .7)
# ---------------- S2 before/after 3.5–8
add(impact(), 3.5, .8)
add(whoosh(.5, True), 3.55, .6)
add(pop(500), 4.15, .7)
add(scan(.65), 4.68, .9)
add(impact(1.2), 5.0, .5); add(shimmer(1.0), 5.0, .5, .3)
add(pop(800), 5.12, .7); add(bell(84, .8), 5.15, .5)
add(riser(.45), 7.6, .7)
# ---------------- S3 offer 8–11
add(impact(2.2), 8.0, 1.0); add(confetti(), 8.02, .9); add(bell(81, 1.5), 8.0, .4)
for i in range(9): add(tick(2400 + i * 120), 8.15 + i * .035, .35)
for i in range(5): add(pop(500 + i * 140), 9.0 + i * .25, .85, -.6 + i * .3)
add(stamp(), 10.22, .9)
add(whoosh(.4, lo=400, hi=9000), 10.68, .7)
# ---------------- S4 prices 11–18
add(impact(1.4), 11.0, .6)
for i in range(3):
    t0 = 11.6 + i * 1.5
    add(whoosh(.45), t0 - .05, .55, .5 if i % 2 == 0 else -.5)
    add(scratch(), t0 + .45, .7)
    add(kaching(), t0 + .78, .85)
    add(stamp(), t0 + 1.02, .55)
add(whoosh(.45, lo=300, hi=8000), 17.55, .7, -.4)
# ---------------- S5 included 18–21.5
for i in range(4): add(pop(700), 18.15 + i * .5, .5, .4); add(bell(79 + i * 3, .6), 18.2 + i * .5, .45, .4)
add(whoosh(.45, True), 21.1, .55)
# ---------------- S6 CTA 21.5–26
add(impact(2.0), 21.5, .8); add(shimmer(1.2), 21.55, .45, -.2)
for i in range(7): add(tick(2000 + i * 150), 21.8 + i * .06, .3)
add(pop(650), 22.62, .8); add(bell(88, .8), 22.65, .4)
add(shimmer(.8), 23.2, .4, .3)
add(bell(91, .9), 23.85, .45)

mix = np.tanh(FX * 1.0)
mix /= max(1e-9, np.max(np.abs(mix))) * 1.05
wavfile.write(sys.argv[1], SR, (mix * 32767).astype(np.int16)); print('ok')
