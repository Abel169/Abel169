"""Synthesized sound effects for the WhatsApp Business tutorial, synced to index.html timings.
Usage: python3 sfx.py out.wav  (26 s, 44.1 kHz stereo)"""
import sys
import numpy as np
from scipy.signal import butter, sosfilt
from scipy.io import wavfile

SR = 44100; DUR = 21.5; N = int(SR * DUR)
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


# ---------------- typo statut timings
add(whoosh(.25,True),0.00,.25)
add(impact(1.2),0.00,.4); add(stamp(),0.00,.25)
add(impact(1.2),0.22,.4); add(stamp(),0.22,.25)
add(impact(1.2),0.44,.4); add(stamp(),0.44,.25)
add(whoosh(.25,True),1.17,.25)
add(tick(1900),1.35,.25)
add(impact(1.2),1.55,.4); add(stamp(),1.55,.25)
add(whoosh(.25,True),2.27,.25)
add(impact(1.2),2.45,.4); add(stamp(),2.45,.25)
add(tick(1900),2.70,.25)
add(whoosh(.25,True),3.37,.25)
add(tick(2600),3.55,.12)
add(tick(2600),3.60,.12)
add(tick(2600),3.65,.12)
add(tick(2600),3.70,.12)
add(tick(2600),3.75,.12)
add(tick(2600),3.80,.12)
add(tick(1900),3.67,.25)
add(tick(1900),3.87,.25)
add(impact(1.2),4.05,.4); add(stamp(),4.05,.25)
add(whoosh(.3),4.70,.3); add(sad(),4.80,.15)
add(whoosh(.25,True),5.17,.25)
add(tick(1900),5.35,.25)
add(tick(1900),5.53,.25)
add(impact(1.2),5.75,.4); add(stamp(),5.75,.25)
add(tick(2600),6.10,.12)
add(tick(2600),6.15,.12)
add(tick(2600),6.20,.12)
add(tick(2600),6.25,.12)
add(tick(2600),6.30,.12)
add(tick(2600),6.35,.12)
add(whoosh(.25,True),6.72,.25)
add(tick(2600),6.90,.12)
add(tick(2600),6.95,.12)
add(tick(2600),7.00,.12)
add(tick(2600),7.05,.12)
add(tick(2600),7.10,.12)
add(tick(2600),7.15,.12)
add(tick(1900),7.02,.25)
add(impact(1.2),7.20,.4); add(stamp(),7.20,.25)
add(pop(900),7.50,.45)
add(whoosh(.25,True),8.42,.25)
add(tick(2600),8.60,.12)
add(tick(2600),8.65,.12)
add(tick(2600),8.70,.12)
add(tick(2600),8.75,.12)
add(tick(2600),8.80,.12)
add(tick(2600),8.85,.12)
add(tick(1900),8.72,.25)
add(shimmer(.8),8.92,.25)
add(whoosh(.25,True),9.92,.25)
add(tick(2600),10.10,.12)
add(tick(2600),10.15,.12)
add(tick(2600),10.20,.12)
add(tick(2600),10.25,.12)
add(tick(2600),10.30,.12)
add(tick(2600),10.35,.12)
add(tick(1900),10.22,.25)
add(tick(1900),10.40,.25)
add(tick(1900),10.60,.25)
add(impact(1.2),10.78,.4); add(stamp(),10.78,.25)
add(whoosh(.25,True),11.82,.25)
add(tick(2600),12.00,.12)
add(tick(2600),12.05,.12)
add(tick(2600),12.10,.12)
add(tick(2600),12.15,.12)
add(tick(2600),12.20,.12)
add(tick(2600),12.25,.12)
add(tick(1900),12.12,.25)
add(tick(1900),12.30,.25)
add(impact(1.2),12.50,.4); add(stamp(),12.50,.25)
add(whoosh(.25,True),13.62,.25)
add(tick(2600),13.80,.12)
add(tick(2600),13.85,.12)
add(tick(2600),13.90,.12)
add(tick(2600),13.95,.12)
add(tick(2600),14.00,.12)
add(tick(2600),14.05,.12)
add(tick(1900),13.92,.25)
add(tick(1900),14.15,.25)
add(impact(1.2),14.35,.4); add(stamp(),14.35,.25)
add(whoosh(.25,True),15.72,.25)
add(tick(1900),15.90,.25)
add(tick(1900),16.08,.25)
add(impact(1.2),16.30,.4); add(stamp(),16.30,.25)
add(whoosh(.25,True),17.22,.25)
add(tick(1900),17.40,.25)
add(tick(1900),17.58,.25)
add(impact(1.2),17.76,.4); add(stamp(),17.76,.25)
add(tick(2600),18.20,.12)
add(tick(2600),18.25,.12)
add(tick(2600),18.30,.12)
add(tick(2600),18.35,.12)
add(tick(2600),18.40,.12)
add(tick(2600),18.45,.12)
add(whoosh(.25,True),19.02,.25)
add(impact(1.2),19.20,.4); add(stamp(),19.20,.25)
add(tick(1900),19.40,.25)
add(impact(1.2),19.60,.4); add(stamp(),19.60,.25)
add(pop(900),20.00,.45)

mix = np.tanh(FX * 1.0)
mix /= max(1e-9, np.max(np.abs(mix))) * 1.05
wavfile.write(sys.argv[1], SR, (mix * 32767).astype(np.int16)); print('ok')
