"""Synthesized sound effects for the Orange Mastercard tutorial, synced to index.html timings.
Usage: python3 sfx.py out.wav  (26 s, 44.1 kHz stereo)"""
import sys
import numpy as np
from scipy.signal import butter, sosfilt
from scipy.io import wavfile

SR = 44100; DUR = 53.0; N = int(SR * DUR)
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


# ---------------- Orange Mastercard tutorial timings
add(pop(500),1.0,.5); add(stamp(),1.8,.5)
add(whoosh(.6),3.0,.6); add(impact(1.4),3.3,.6)
add(tick(2600),5.4,.8); add(pop(900),5.42,.25)
add(tick(2600),7.4,.8); add(pop(900),7.42,.25)
add(tick(2600),10.2,.8); add(pop(900),10.219999999999999,.25)
add(tick(2600),12.9,.8); add(pop(900),12.92,.25)
add(tick(2600),14.5,.8); add(pop(900),14.52,.25)
add(tick(2600),18.7,.8); add(pop(900),18.72,.25)
add(tick(2600),21.0,.8); add(pop(900),21.02,.25)
add(tick(2600),22.2,.8); add(pop(900),22.22,.25)
add(tick(2600),23.9,.8); add(pop(900),23.919999999999998,.25)
add(tick(2600),24.3,.8); add(pop(900),24.32,.25)
add(tick(2600),24.7,.8); add(pop(900),24.72,.25)
add(tick(2600),25.1,.8); add(pop(900),25.12,.25)
add(tick(2600),25.6,.8); add(pop(900),25.62,.25)
add(tick(2600),29.4,.8); add(pop(900),29.419999999999998,.25)
add(tick(2600),31.3,.8); add(pop(900),31.32,.25)
add(tick(2600),35.6,.8); add(pop(900),35.620000000000005,.25)
add(tick(2600),37.3,.8); add(pop(900),37.32,.25)
add(tick(2600),44.0,.8); add(pop(900),44.02,.25)
for i in range(10): add(tick(2000+i*60),8.0+i*.11,.25)
for t in (3.5,7,11,14,19.5,23,30.5,40): add(bell(84,.6),t,.3); add(whoosh(.35,True),t-.3,.35)
for i in range(6): add(tick(2200),15.0+i*.55,.2)
add(impact(1.6),31.6,.6); add(shimmer(1.4),31.8,.6); add(whoosh(.8),31.5,.5)
add(kaching(),37.6,.6)
for i in range(12): add(tick(2300),41.0+i*.13,.2)
add(kaching(),44.5,.8); add(confetti(),44.6,.4)
add(whoosh(.6),46.3,.5)
for i in range(4): add(pop(600+i*120),47.0+i*.35,.4)
add(stamp(),48.7,.5); add(impact(1.4),49.6,.6); add(shimmer(1.2),49.7,.4)

mix = np.tanh(FX * 1.0)
mix /= max(1e-9, np.max(np.abs(mix))) * 1.05
wavfile.write(sys.argv[1], SR, (mix * 32767).astype(np.int16)); print('ok')
