"""Original 30 s Afro-house score for the OK+ SuguPro showreel (120 BPM, A minor), synced to the edit.
Usage: python3 music.py out.wav"""
import sys
import numpy as np
from scipy.signal import butter, sosfilt
from scipy.io import wavfile

SR = 44100; DUR = 30.0; N = int(SR * DUR); BEAT = .5; STEP = .125
rng = np.random.default_rng(9)
lp = lambda x, f, o=2: sosfilt(butter(o, f, 'low', fs=SR, output='sos'), x)
hp = lambda x, f, o=2: sosfilt(butter(o, f, 'high', fs=SR, output='sos'), x)
bp = lambda x, a, b, o=2: sosfilt(butter(o, [a, b], 'band', fs=SR, output='sos'), x)
tt = lambda d: np.arange(int(d * SR)) / SR
note = lambda n: 440 * 2 ** ((n - 69) / 12)
MUS = np.zeros((N, 2)); FX = np.zeros((N, 2))


def add(buf, sig, t, g=1.0, pan=0.0):
    i = int(t * SR)
    if i >= N or i < 0: return
    sig = sig[:N - i]
    buf[i:i + len(sig), 0] += sig * g * np.sqrt(.5 * (1 - pan)); buf[i:i + len(sig), 1] += sig * g * np.sqrt(.5 * (1 + pan))


def kick():
    t = tt(.4); f = 50 + 120 * np.exp(-t * 32)
    return np.tanh(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 8) * 1.6 + hp(rng.standard_normal(len(t)), 3000) * np.exp(-t * 300) * .2)


def logdrum(n):
    t = tt(.42); f = note(n) * (1 + 1.2 * np.exp(-t * 45))
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 6.5)
    return lp(np.tanh(s * 2.2), 1800) * .8


def shaker(acc=1.0):
    t = tt(.07); return bp(rng.standard_normal(len(t)), 5000, 12000) * np.exp(-t * 60) * acc


def clap():
    t = tt(.3); n = bp(rng.standard_normal(len(t)), 900, 5000); env = np.exp(-t * 18)
    for k in (0, .011, .022): env = env + np.where(t >= k, np.exp(-(t - k) * 170), 0) * .6
    return n * env * .5


def conga(f=330):
    t = tt(.25); fr = f * (1 + .25 * np.exp(-t * 60))
    return np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * 18) * .6


def marimba(n, d=.6):
    t = tt(d); f = note(n)
    return (np.sin(2 * np.pi * f * t) + .35 * np.sin(2 * np.pi * f * 4 * t) * np.exp(-t * 30)) * np.exp(-t * 7) * np.minimum(1, t / .002) * .3


def rhodes(chord, d):
    t = tt(d); s = 0
    for n in chord:
        f = note(n); m = np.sin(2 * np.pi * f * t) * 1.4 * np.exp(-t * 3)
        s = s + np.sin(2 * np.pi * f * t + m) * np.exp(-t * 1.3) * (1 + .15 * np.sin(2 * np.pi * 5 * t))
    return s * np.minimum(1, t / .005) * np.minimum(1, (d - t) / .1) * .09


def pad(chord, d):
    t = tt(d); s = 0
    for n in chord:
        for de in (-.005, 0, .005): s = s + (2 * ((t * note(n) * (1 + de)) % 1) - 1)
    return lp(s / 9, 1200) * np.minimum(1, t / .4) * np.minimum(1, (d - t) / .3) * .35


def impact(d=2.2):
    t = tt(d); f = 30 + 70 * np.exp(-t * 6)
    return np.tanh((np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.2) * 1.3 + lp(rng.standard_normal(len(t)), 3000) * np.exp(-t * 5) * .45) * 1.2)


def sweep(d, rev=False):
    t = tt(d); n = rng.standard_normal(len(t)); out = np.zeros_like(n)
    for i in range(0, len(t), 1024):
        fc = 300 + 7000 * (i / len(t)) ** 2
        seg = bp(n[max(0, i - 2048):i + 1024], fc * .6, min(fc * 1.6, 20000)); out[i:i + 1024] = seg[-len(n[i:i + 1024]):]
    s = out * (t / d) ** 2 * np.minimum(1, (d - t) / .03)
    return s[::-1] if rev else s


def bell(n, d=1.2):
    t = tt(d); return sum(np.sin(2 * np.pi * note(n + o) * t) * a for o, a in [(0, 1), (12, .5), (19, .25), (24, .15)]) * np.exp(-t * 4) * .3


def tick():
    t = tt(.03); return np.sin(2 * np.pi * 3200 * t) * np.exp(-t * 200) * .5


def printer(d):
    t = tt(d); n = bp(rng.standard_normal(len(t)), 1500, 5000)
    return n * (.5 + .5 * np.sign(np.sin(2 * np.pi * 38 * t))) * .25 * np.minimum(1, t / .02) * np.minimum(1, (d - t) / .02)


def thump():
    t = tt(.5); f = 60 + 80 * np.exp(-t * 40)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 10) + hp(rng.standard_normal(len(t)), 1500) * np.exp(-t * 60) * .3


# progression (A minor): Fmaj7 – G6 – Em7 – Am9, one per bar (2 s), bars aligned on 3.0
PROG = [(41, [57, 60, 64, 65]), (43, [55, 59, 62, 64]), (40, [55, 59, 62, 64]), (45, [57, 60, 64, 71])]
LOG = {3: 0, 6: 0, 10: 7, 11: 5, 14: 3}            # 16th steps -> semitone offset from root
MAR = [0, None, 7, None, 12, 10, None, 7, None, 5, 7, None, 3, None, 0, None]
PENTA = [57, 60, 62, 64, 67, 69, 72]

# intro 0–3
for b in range(2):
    add(MUS, pad(PROG[b][1], 1.6), b * 1.5, .7)
for i, n in enumerate([69, 72, 76, 74, 72, 69]): add(MUS, marimba(n, .8), .2 + i * .17, .8, -.3 + i * .12)
add(FX, sweep(1.2), .05, .5); add(FX, impact(), 1.25, 1.0); add(MUS, bell(81, 1.5), 1.25, .5)
add(FX, sweep(.45), 2.55, .7)

kicks = []
for b in range(14):
    t0 = 3.0 + b * 2.0
    if t0 >= 30: break
    root, ch = PROG[b % 4]
    if t0 < 28.5:
        add(MUS, rhodes(ch, 2.0), t0, 1.0)
        add(MUS, pad(ch, 2.0), t0, .5)
    for s in range(16):
        ts = t0 + s * STEP
        if ts >= 28.4: break
        if s % 4 == 0: kicks.append(ts); add(MUS, kick(), ts, .95)
        add(MUS, shaker(1.0 if s % 2 else .45), ts, .2, .35)
        if s in (4, 12): add(MUS, clap(), ts, .45, -.1)
        if s in LOG and ts >= 7.0: add(MUS, logdrum(root + LOG[s]), ts, .75)
        if s in (2, 7, 9, 13): add(MUS, conga(330 if s != 7 else 240), ts, .35, .5)
        if MAR[s] is not None and 7.0 <= ts < 27: add(MUS, marimba(57 + 12 + MAR[s] % 12 + (12 if MAR[s] >= 12 else 0), .5), ts, .55, -.4)

# sync FX
add(FX, sweep(.6), 6.4, .6, .2); add(FX, impact(1.5), 7.0, .35)
for t in (8.0, 8.5, 9.0): add(FX, tick(), t, .9); add(FX, bell(88, .4), t, .25)
add(FX, bell(84, 1.4), 9.55, .9); add(FX, bell(91, 1.4), 9.62, .6)                       # ka-ching
add(FX, hp(rng.standard_normal(int(.2 * SR)), 4000) * np.exp(-tt(.2) * 30) * .4, 9.55, 1)
add(FX, printer(.7), 9.75, .9)
for i in range(12): add(FX, tick(), 10.3 + i * .05, .35, .6)
add(FX, thump(), 10.95, 1.0)
add(FX, sweep(.5), 11.55, .6); add(FX, impact(), 12.0, .55)
add(FX, sweep(1.0, True), 12.6, .3)
add(FX, bell(76, .8), 14.6, .5); add(FX, bell(76, .8), 14.85, .4)                          # alert
for i in range(14): add(FX, tick(), 14.8 + i * .07, .2)
add(FX, sweep(.8), 15.3, .4)
add(FX, sweep(.5), 16.5, .7); add(FX, impact(), 17.0, .6)
add(FX, sweep(.8), 18.3, .5); add(FX, impact(1.2), 19.0, .4)
for i in range(3): add(FX, bell(81 + i * 3, .6), 19.25 + i * .18, .35, -.3 + i * .3)
add(FX, bell(88, 1.4), 19.9, .7)
for i in range(3): add(FX, tick(), 20.15 + i * .12, .6)
add(FX, sweep(.6), 20.6, .6); add(FX, impact(1.5), 21.0, .35)
for i in range(9): add(FX, tick(), 22.15 + i * .1, .5)
add(FX, sweep(.5), 23.1, .5)
for i in range(3): add(FX, tick(), 23.95 + i * .25, .5)
add(FX, thump(), 24.9, 1.0); add(FX, bell(93, .9), 24.95, .4)
add(FX, sweep(.5), 26.55, .6); add(FX, impact(), 27.0, .5)
add(FX, impact(), 28.2, .9); add(MUS, bell(81, 2.0), 28.2, .6)
fin = sum(marimba(n, 1.8) for n in (57, 64, 69, 72, 76)) + rhodes([57, 60, 64, 71], 1.8) * 2
add(MUS, fin, 28.2, 1.0)

# side-chain on the music bus
duck = np.ones(N); cv = 1 - .5 * np.exp(-tt(.3) * 16)
for k in kicks:
    i = int(k * SR); duck[i:i + len(cv)] = np.minimum(duck[i:i + len(cv)], cv[:N - i])
MUS *= duck[:, None]
# "network cut": music muffled 17.3–19.0
w = np.zeros(N); a, b_, c = int(17.25 * SR), int(17.55 * SR), int(19.0 * SR)
w[a:b_] = np.linspace(0, 1, b_ - a); w[b_:c] = 1; w[c:c + int(.08 * SR)] = np.linspace(1, 0, int(.08 * SR))
muff = np.stack([lp(MUS[:, 0], 500, 4), lp(MUS[:, 1], 500, 4)], 1) * .8
MUS = MUS * (1 - w[:, None]) + muff * w[:, None]

mix = MUS + FX
mix = np.stack([hp(mix[:, 0], 28), hp(mix[:, 1], 28)], 1)
mix = np.tanh(mix * 1.15)
fo = np.ones(N); n0 = int((DUR - .7) * SR); fo[n0:] = np.linspace(1, 0, N - n0) ** 2
mix *= fo[:, None]; mix /= np.max(np.abs(mix)) * 1.08
wavfile.write(sys.argv[1], SR, (mix * 32767).astype(np.int16)); print('ok')
