"""Original 30 s cinematic score for the Zéro VBG showreel (120 BPM, D minor), synced to the edit.
Usage: python3 music.py out.wav"""
import sys
import numpy as np
from scipy.signal import butter, sosfilt
from scipy.io import wavfile

SR = 44100; DUR = 30.0; N = int(SR * DUR); BEAT = 0.5
rng = np.random.default_rng(5)
L = np.zeros(N); R = np.zeros(N)
lp = lambda x, f, o=2: sosfilt(butter(o, f, 'low', fs=SR, output='sos'), x)
hp = lambda x, f, o=2: sosfilt(butter(o, f, 'high', fs=SR, output='sos'), x)
bp = lambda x, a, b, o=2: sosfilt(butter(o, [a, b], 'band', fs=SR, output='sos'), x)
tt = lambda d: np.arange(int(d * SR)) / SR
note = lambda n: 440 * 2 ** ((n - 69) / 12)


def add(sig, t, g=1.0, pan=0.0):
    i = int(t * SR)
    if i >= N or i < 0: return
    sig = sig[:N - i]
    L[i:i + len(sig)] += sig * g * np.sqrt(.5 * (1 - pan)); R[i:i + len(sig)] += sig * g * np.sqrt(.5 * (1 + pan))


def thump(f0=55, d=0.5, dec=9):
    t = tt(d); f = f0 + 60 * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * dec)


def kick(): return np.tanh(thump(48, .45, 7.5) * 1.5 + hp(rng.standard_normal(int(.45 * SR)), 2500) * np.exp(-tt(.45) * 300) * .2)


def hat(d=.05): t = tt(d); return hp(rng.standard_normal(len(t)), 8000) * np.exp(-t * 80)


def snap():
    t = tt(.35); n = bp(rng.standard_normal(len(t)), 1200, 6000) * np.exp(-t * 16)
    return n * .55 + np.sin(2 * np.pi * 180 * t) * np.exp(-t * 25) * .3


def impact(d=2.6):
    t = tt(d); f = 28 + 60 * np.exp(-t * 5)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 1.8)
    return np.tanh((boom * 1.3 + lp(rng.standard_normal(len(t)), 2500) * np.exp(-t * 4) * .45) * 1.2)


def swell(d, rev=False):
    t = tt(d); n = rng.standard_normal(len(t)); out = np.zeros_like(n)
    for i in range(0, len(t), 1024):
        fc = 250 + 6000 * (i / len(t)) ** 2
        seg = bp(n[max(0, i - 2048):i + 1024], fc * .6, min(fc * 1.6, 20000)); out[i:i + 1024] = seg[-len(n[i:i + 1024]):]
    s = out * (t / d) ** 2.2 * np.minimum(1, (d - t) / .03)
    return s[::-1] if rev else s


def piano(n, d=2.0, vel=1.0):
    t = tt(d); f = note(n); s = 0
    for k, a in [(1, 1), (2, .45), (3, .22), (4, .12), (5, .06)]:
        s = s + a * np.sin(2 * np.pi * f * k * (1 + .0004 * k * k) * t) * np.exp(-t * (1.6 + k * .9))
    return s * np.minimum(1, t / .004) * .22 * vel


def pad(chord, d):
    t = tt(d); s = 0
    for n in chord:
        for det in (-.004, 0, .004):
            s = s + (2 * ((t * note(n) * (1 + det)) % 1) - 1)
    s = lp(s / 9, 900)
    return s * np.minimum(1, t / .6) * np.minimum(1, (d - t) / .4) * .5


def bass(n, d):
    t = tt(d); f = note(n)
    return (np.sin(2 * np.pi * f * t) + .25 * np.tanh(3 * np.sin(2 * np.pi * 2 * f * t))) * np.exp(-t * 3.5) * np.minimum(1, t / .005) * .5


def chime(n):
    t = tt(1.8)
    return sum(np.sin(2 * np.pi * note(n + o) * t) * a for o, a in [(0, 1), (12, .4), (19, .2)]) * np.exp(-t * 3) * .3


# D minor: Dm  Bb  F  C
CH = [(50, [62, 65, 69]), (46, [62, 65, 70]), (53, [60, 65, 69]), (48, [60, 64, 67])]

# ---- intro 0–3.5 : heartbeat, drone, strike, riser
drone = lp(sum(np.sin(2 * np.pi * note(n) * tt(3.6) * (1 + d)) for n in (38, 50) for d in (-.002, .002)), 400) * .12
add(drone * np.minimum(1, tt(3.6) / 1.0), 0)
for b in (0.1, 1.1):
    add(thump(52, .5, 10), b, .8); add(thump(48, .5, 10), b + .24, .55)
add(swell(1.9), 0.1, .35)
add(impact(), 2.0, 1.0); add(piano(38, 2.4, 1.6), 2.0); add(piano(50, 2.4, 1.2), 2.0)
add(snap(), 2.45, .5); add(piano(62, 1.0, 1.2), 2.45, 1, .3)
add(swell(1.0), 2.5, .8)

# ---- body from 3.5
add(impact(), 3.5, .9)
for b in range(14):
    t0 = 3.5 + b * 2.0
    if t0 >= 30: break
    root, ch = CH[b % 4]
    add(pad(ch, 2.0), t0, .9)
    for n in ch: add(piano(n, 2.0, .9), t0, 1, (n - 65) / 12)
    add(piano(root - 12 + 24, 2.0, .7), t0)
    # arpeggio (from 7.0)
    arp = [ch[0] + 12, ch[1] + 12, ch[2] + 12, ch[1] + 12]
    for k in range(8):
        tk = t0 + k * .25
        if 7.0 <= tk < 26.5: add(piano(arp[k % 4] + (12 if k == 4 else 0), .6, .55), tk, 1, .5 if k % 2 else -.5)
    for k in range(8):
        tk = t0 + k * .25
        if 3.5 <= tk < 28.5: add(bass(root - 12 if k % 4 else root - 12, .24), tk, .8 if k % 2 else .55)

kicks = []
for i in range(60):
    t = i * BEAT
    if t < 3.5 or t >= 28.5: continue
    if t < 7.0 and i % 2: continue                 # half-time on the logo
    kicks.append(t); add(kick(), t, .9)
    if t >= 7.0:
        add(hat(), t + .25, .2, .3)
        if i % 2: add(snap(), t, .38, -.1)
    if 12.0 <= t < 22.5: add(hat(.03), t + .375, .1, -.3)

# transitions & accents
for t in (6.45, 11.45, 17.5, 22.0, 25.95): add(swell(.6), t, .6, .2)
for t in (7.0, 12.0, 18.0, 22.5): add(impact(1.6), t, .35)
add(swell(1.2), 12.1, .4)                      # into the mic moment
add(impact(), 13.25, .55)
for t in (15.85, 16.1, 15.95): add(chime(86), t, .25, .3)
for i in range(3): add(chime(81 + i * 2), 19.3 + i * .25, .2)
add(chime(86), 21.6, .9); add(chime(93), 21.7, .5)
for i in range(4): add(chime(79 + i * 3), 23.2 + i * .4, .18, .4)
add(impact(), 26.5, 1.0)
add(chime(86), 28.1, .6)
t = tt(3.5)
fin = sum(piano(n, 3.5, 1.1) for n in (38, 50, 57, 62, 65, 69))
add(fin, 26.5)

duck = np.ones(N); cv = 1 - .45 * np.exp(-tt(.35) * 14)
for k in kicks:
    i = int(k * SR); duck[i:i + len(cv)] = np.minimum(duck[i:i + len(cv)], cv[:N - i])
L *= duck; R *= duck
mix = np.stack([L, R], 1); mix = hp(mix.T, 28).T
mix = np.tanh(mix * 1.15)
fo = np.ones(N); n0 = int((DUR - .8) * SR); fo[n0:] = np.linspace(1, 0, N - n0) ** 2
mix *= fo[:, None]; mix /= np.max(np.abs(mix)) * 1.08
wavfile.write(sys.argv[1], SR, (mix * 32767).astype(np.int16)); print('ok')
