"""Original 25 s score for the IBA Design spot "Le Fil d'Or" (D major, 120 BPM half-time feel).
Piano + string pad + kora-like harp (Karplus-Strong) + soft percussion, with SFX synced to the edit.
Usage: python3 music.py out.wav"""
import sys
import numpy as np
from scipy.signal import butter, sosfilt
from scipy.io import wavfile

SR = 44100; DUR = 25.0; N = int(SR * DUR)
rng = np.random.default_rng(12)
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


def kora(n, d=1.6, bright=.5):
    """Karplus-Strong plucked string."""
    f = note(n); p = max(2, int(SR / f)); m = int(d * SR)
    buf = lp(rng.standard_normal(p), 2000 + 6000 * bright)
    out = np.zeros(m); b = buf.copy(); k = 0
    for i in range(m):
        out[i] = b[k]; nk = (k + 1) % p
        b[k] = .4985 * (b[k] + b[nk]); k = nk
    return out * np.minimum(1, (m - np.arange(m)) / (.05 * SR)) * .5


def piano(n, d=2.0, vel=1.0):
    t = tt(d); f = note(n); s = 0
    for k, a in [(1, 1), (2, .4), (3, .18), (4, .09), (5, .04)]:
        s = s + a * np.sin(2 * np.pi * f * k * (1 + .0004 * k * k) * t) * np.exp(-t * (1.3 + k * .8))
    return s * np.minimum(1, t / .004) * .2 * vel


def pad(chord, d):
    t = tt(d); s = 0
    for n in chord:
        for de in (-.004, 0, .004): s = s + (2 * ((t * note(n) * (1 + de)) % 1) - 1)
    s = lp(s / 12, 1100)
    vib = 1 + .002 * np.sin(2 * np.pi * 5 * t)
    return s * vib * np.minimum(1, t / .7) * np.minimum(1, (d - t) / .5) * .4


def bell(n, d=1.6):
    t = tt(d); return sum(np.sin(2 * np.pi * note(n + o) * t) * a for o, a in [(0, 1), (12, .45), (19, .2), (24, .1)]) * np.exp(-t * 3) * .28


def silk(d=.7):
    t = tt(d); n = rng.standard_normal(len(t)); out = np.zeros_like(n)
    for i in range(0, len(t), 1024):
        fc = 1500 + 5000 * np.sin(np.pi * i / len(t))
        seg = bp(n[max(0, i - 2048):i + 1024], fc * .7, min(fc * 1.4, 20000)); out[i:i + 1024] = seg[-len(n[i:i + 1024]):]
    return out * np.sin(np.pi * t / d) ** 2 * .5


def kick():
    t = tt(.4); f = 48 + 70 * np.exp(-t * 30)
    return np.tanh(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9) * 1.3)


def snap():
    t = tt(.15); return bp(rng.standard_normal(len(t)), 1500, 7000) * np.exp(-t * 45) * .6


def shaker(a=1.):
    t = tt(.06); return bp(rng.standard_normal(len(t)), 5000, 12000) * np.exp(-t * 70) * a


def boom(d=2.0):
    t = tt(d); f = 34 + 40 * np.exp(-t * 5)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.2) * .9


def shimmer(d=1.2, base=86):
    s = np.zeros(int(d * SR))
    for i in range(12):
        b = bell(base + [0, 4, 7, 11, 12, 16][i % 6], .8) * .4; k = int(i * d / 14 * SR); s[k:k + len(b)] += b[:len(s) - k]
    return s


D = 62  # D4
CH = [(38, [62, 66, 69, 73, 76]), (35, [59, 62, 66, 69, 76]), (43, [59, 62, 66, 69, 74]), (45, [57, 61, 64, 66, 71])]  # Dmaj9 Bm11 Gmaj9 A6/9
SCALE = [62, 64, 66, 69, 71, 74, 76, 78, 81]

# ---- intro 0–3 : thread glissando, logo shimmer
add(pad(CH[0][1], 3.2), 0, .6)
for i, n in enumerate(SCALE): add(kora(n, 1.4, .6), .05 + i * .1, .55, -.6 + i * .15)
add(boom(), .55, .35)
add(shimmer(1.2, 86), 1.5, .8, .2)
add(silk(.7), 1.9, .5, .4)
add(piano(50, 2.5, 1.2), 2.6, 1); add(piano(57, 2.5, .9), 2.6, 1)

# ---- body from 3.0 : 2 s bars
for b in range(11):
    t0 = 3.0 + b * 2.0
    if t0 >= 24.5: break
    root, ch = CH[b % 4]
    breakdown = 15.0 <= t0 < 17.0
    add(pad(ch, 2.0), t0, .75)
    for j, n in enumerate(ch[:4]): add(piano(n, 2.0, .7), t0 + j * .02, 1, (n - 66) / 14)
    add(piano(root, 2.0, .9), t0)
    # kora arpeggio 8ths
    arp = [ch[0], ch[2], ch[4], ch[2] + 12, ch[1] + 12, ch[3], ch[2], ch[4]]
    for k in range(8):
        tk = t0 + k * .25
        if tk < 6.0 and k % 2: continue
        add(kora(arp[k] + 12 if tk > 6 else arp[k], .9, .45), tk, .38 if not breakdown else .28, .45 if k % 2 else -.45)
    # percussion from 6.0
    for k in range(8):
        tk = t0 + k * .25
        if tk < 6.0 or breakdown or tk >= 22.0: continue
        if k in (0, 4): add(kick(), tk, .55)
        if k == 4: add(snap(), tk, .35, .2)
        add(shaker(.9 if k % 2 else .5), tk, .14, -.3)
    # bass pulse
    if t0 >= 6.0 and not breakdown and t0 < 22:
        for k in (0, 3, 4, 6):
            tb = tt(.4); bs = np.sin(2 * np.pi * note(root - 12 + 12) * tb) * np.exp(-tb * 5) * .4
            add(bs, t0 + k * .25, .8)

# ---- sync SFX
add(silk(.8), 3.25, .6, -.2)                                  # veil S2
for i in range(6):                                            # 6 arches
    t = 6.0 + i * 1.5
    add(silk(.7), t + .2, .55, (-1) ** i * .3)
    add(bell(SCALE[i % len(SCALE)] + 12, 1.0), t + .45, .35, (-1) ** i * .4)
add(boom(2.2), 15.0, .4)
add(bell(78, 2.0), 15.25, .7, -.3); add(bell(85, 2.0), 15.6, .6, .3)   # lamps
add(silk(.8), 17.0, .5, -.3); add(silk(.8), 17.25, .5, .3)
add(silk(.8), 19.0, .5, -.3); add(silk(.8), 19.25, .5, .3)
for i in range(5): add(bell(74 + [0, 2, 4, 7, 9][i] + 12, 1.0), 20.1 + i * .12, .45, -.4 + i * .2)   # stars
add(boom(2.5), 22.0, .45)
add(shimmer(1.4, 86), 22.7, .7, -.2)
fin = sum(piano(n, 3.0, 1.0) for n in (38, 50, 57, 62, 66, 69, 73)) + pad([62, 66, 69, 73, 76], 3.0)
add(fin, 22.0, 1.0)
for i, n in enumerate(reversed(SCALE)): add(kora(n + 12, 1.2, .5), 23.4 + i * .07, .35, .6 - i * .15)

mix = np.stack([L, R], 1)
mix = np.stack([hp(mix[:, 0], 30), hp(mix[:, 1], 30)], 1)
# light room reverb (feedback delays)
for dly, g in ((.031, .25), (.047, .2), (.073, .16), (.113, .12)):
    k = int(dly * SR); mix[k:, 0] += mix[:-k, 1] * g; mix[k:, 1] += mix[:-k, 0] * g
mix = np.tanh(mix * 1.1)
fo = np.ones(N); n0 = int((DUR - .9) * SR); fo[n0:] = np.linspace(1, 0, N - n0) ** 2
mix *= fo[:, None]; mix /= np.max(np.abs(mix)) * 1.08
wavfile.write(sys.argv[1], SR, (mix * 32767).astype(np.int16)); print('ok')
