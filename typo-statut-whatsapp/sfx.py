"""Synthesized sound effects for the WhatsApp Business tutorial, synced to index.html timings.
Usage: python3 sfx.py out.wav  (26 s, 44.1 kHz stereo)"""
import sys
import numpy as np
from scipy.signal import butter, sosfilt
from scipy.io import wavfile

SR = 44100; DUR = 26.5; N = int(SR * DUR)
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
add(whoosh(.25,True),0.02,.2)
add(impact(1.2),0.20,.3); add(stamp(),0.20,.18)
add(impact(1.2),0.35,.3); add(stamp(),0.35,.18)
add(impact(1.2),0.70,.3); add(stamp(),0.70,.18)
add(whoosh(.25,True),0.92,.2)
add(tick(1900),1.10,.18)
add(impact(1.2),1.40,.3); add(stamp(),1.40,.18)
add(whoosh(.25,True),1.77,.2)
add(impact(1.2),2.20,.3); add(stamp(),2.20,.18)
add(tick(1900),2.45,.18)
add(whoosh(.25,True),3.12,.2)
add(tick(2600),3.30,.08)
add(tick(2600),3.35,.08)
add(tick(2600),3.40,.08)
add(tick(2600),3.45,.08)
add(tick(2600),3.50,.08)
add(tick(2600),3.55,.08)
add(tick(1900),3.80,.18)
add(tick(1900),4.36,.18)
add(impact(1.2),4.60,.3); add(stamp(),4.60,.18)
add(whoosh(.3),5.05,.22)
add(whoosh(.25,True),5.07,.2)
add(tick(1900),5.25,.18)
add(tick(1900),5.65,.18)
add(impact(1.2),6.10,.3); add(stamp(),6.10,.18)
add(tick(2600),6.55,.08)
add(tick(2600),6.60,.08)
add(tick(2600),6.65,.08)
add(tick(2600),6.70,.08)
add(tick(2600),6.75,.08)
add(tick(2600),6.80,.08)
add(whoosh(.25,True),7.87,.2)
add(tick(2600),8.05,.08)
add(tick(2600),8.10,.08)
add(tick(2600),8.15,.08)
add(tick(2600),8.20,.08)
add(tick(2600),8.25,.08)
add(tick(2600),8.30,.08)
add(tick(1900),8.10,.18)
add(impact(1.2),8.25,.3); add(stamp(),8.25,.18)
add(pop(900),8.75,.35)
add(whoosh(.25,True),9.72,.2)
add(tick(2600),9.90,.08)
add(tick(2600),9.95,.08)
add(tick(2600),10.00,.08)
add(tick(2600),10.05,.08)
add(tick(2600),10.10,.08)
add(tick(2600),10.15,.08)
add(tick(1900),10.60,.18)
add(shimmer(.8),11.05,.2)
add(whoosh(.25,True),11.52,.2)
add(tick(2600),11.70,.08)
add(tick(2600),11.75,.08)
add(tick(2600),11.80,.08)
add(tick(2600),11.85,.08)
add(tick(2600),11.90,.08)
add(tick(2600),11.95,.08)
add(tick(1900),12.30,.18)
add(tick(1900),12.65,.18)
add(tick(1900),13.30,.18)
add(impact(1.2),13.80,.3); add(stamp(),13.80,.18)
add(whoosh(.25,True),14.37,.2)
add(tick(2600),14.55,.08)
add(tick(2600),14.60,.08)
add(tick(2600),14.65,.08)
add(tick(2600),14.70,.08)
add(tick(2600),14.75,.08)
add(tick(2600),14.80,.08)
add(tick(1900),15.20,.18)
add(tick(1900),15.60,.18)
add(impact(1.2),16.00,.3); add(stamp(),16.00,.18)
add(whoosh(.25,True),16.47,.2)
add(tick(2600),16.65,.08)
add(tick(2600),16.70,.08)
add(tick(2600),16.75,.08)
add(tick(2600),16.80,.08)
add(tick(2600),16.85,.08)
add(tick(2600),16.90,.08)
add(tick(1900),16.70,.18)
add(tick(1900),17.55,.18)
add(impact(1.2),18.25,.3); add(stamp(),18.25,.18)
add(whoosh(.25,True),18.82,.2)
add(tick(1900),19.00,.18)
add(tick(1900),19.30,.18)
add(impact(1.2),19.60,.3); add(stamp(),19.60,.18)
add(whoosh(.25,True),20.32,.2)
add(tick(1900),20.50,.18)
add(tick(1900),20.80,.18)
add(impact(1.2),21.10,.3); add(stamp(),21.10,.18)
add(tick(2600),21.80,.08)
add(tick(2600),21.85,.08)
add(tick(2600),21.90,.08)
add(tick(2600),21.95,.08)
add(tick(2600),22.00,.08)
add(tick(2600),22.05,.08)

add(whoosh(.25,True),22.72,.2)
add(impact(1.2),22.90,.3); add(stamp(),22.90,.18)
add(tick(1900),23.50,.18)
add(impact(1.2),23.80,.3); add(stamp(),23.80,.18)
add(pop(900),24.40,.35)

mix = np.tanh(FX * 1.0)
mix /= max(1e-9, np.max(np.abs(mix))) * 1.05
wavfile.write(sys.argv[1], SR, (mix * 32767).astype(np.int16)); print('ok')
