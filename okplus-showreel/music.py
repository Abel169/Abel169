"""Original 30 s soundtrack synthesized from scratch (120 BPM, A minor), synced to the edit."""
import numpy as np
from scipy.signal import butter, sosfilt
from scipy.io import wavfile
import sys

SR = 44100
DUR = 30.0
N = int(SR * DUR)
BEAT = 0.5
rng = np.random.default_rng(3)
L = np.zeros(N); R = np.zeros(N)


def lp(x, f, o=2): return sosfilt(butter(o, f, 'low', fs=SR, output='sos'), x)
def hp(x, f, o=2): return sosfilt(butter(o, f, 'high', fs=SR, output='sos'), x)
def bp(x, a, b, o=2): return sosfilt(butter(o, [a, b], 'band', fs=SR, output='sos'), x)


def add(sig, t, gain=1.0, pan=0.0):
    i = int(t * SR)
    if i >= N: return
    sig = sig[:N - i]
    L[i:i + len(sig)] += sig * gain * np.sqrt(0.5 * (1 - pan))
    R[i:i + len(sig)] += sig * gain * np.sqrt(0.5 * (1 + pan))


def tt(d): return np.arange(int(d * SR)) / SR
def note(n): return 440 * 2 ** ((n - 69) / 12)


# ---------- drum voices ----------
def kick():
    t = tt(0.45)
    f = 45 + 110 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) * np.exp(-t * 7.5)
    click = hp(rng.standard_normal(len(t)), 2000) * np.exp(-t * 300) * 0.25
    return np.tanh((s + click) * 1.6)


def hat(d=0.06):
    t = tt(d)
    return hp(rng.standard_normal(len(t)), 7500) * np.exp(-t * 70)


def clap():
    t = tt(0.3)
    n = bp(rng.standard_normal(len(t)), 900, 4000)
    env = np.exp(-t * 18)
    for k in (0.0, 0.012, 0.024):
        env += np.where(t >= k, np.exp(-(t - k) * 160), 0) * 0.7
    body = np.sin(2 * np.pi * 190 * t) * np.exp(-t * 30) * 0.4
    return n * env * 0.5 + body


def impact():
    t = tt(2.2)
    f = 30 + 70 * np.exp(-t * 6)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.2)
    noise = lp(rng.standard_normal(len(t)), 3000) * np.exp(-t * 5) * 0.5
    return np.tanh((boom * 1.3 + noise) * 1.2)


def whoosh(d, rev=False):
    t = tt(d)
    n = rng.standard_normal(len(t))
    out = np.zeros_like(n)
    # sweep band by chunks
    ch = 1024
    for i in range(0, len(t), ch):
        p = i / len(t)
        fc = 300 + 7000 * (p ** 2)
        seg = n[max(0, i - 2048):i + ch]
        f = bp(seg, fc * 0.6, min(fc * 1.6, 20000))
        out[i:i + ch] = f[-len(n[i:i + ch]):]
    env = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 2 * (t / d) ** 1.5
    s = out * env
    return s[::-1] if rev else s


def riser(d):
    t = tt(d)
    f = 200 * 2 ** (t / d * 3)
    s = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.25
    s = lp(s, 2500)
    return s * (t / d) ** 2 + whoosh(d) * 0.6


def click():
    t = tt(0.05)
    return np.sin(2 * np.pi * 2400 * t) * np.exp(-t * 120) * 0.6 + hp(rng.standard_normal(len(t)), 5000) * np.exp(-t * 200) * 0.3


def ding():
    t = tt(1.4)
    s = sum(np.sin(2 * np.pi * note(n) * t) * a for n, a in [(88, 1), (95, .5), (100, .3)])
    return s * np.exp(-t * 3.5) * 0.35


# ---------- tonal voices ----------
CHORDS = [(57, [57, 60, 64]), (53, [53, 57, 60]), (48, [55, 60, 64]), (55, [55, 59, 62])]  # Am F C G


def saw(f, t, det=0.0):
    s = 0
    for d in (-det, 0, det):
        s = s + 2 * ((t * f * (1 + d)) % 1) - 1
    return s / 3


def pad_bar(chord, d):
    t = tt(d)
    s = sum(saw(note(n + 12), t, 0.006) for n in chord)
    s = lp(s, 1400)
    env = np.minimum(1, t / 0.25) * np.minimum(1, (d - t) / 0.3)
    return s * env * 0.18


def bass_note(n, d):
    t = tt(d)
    f = note(n - 12)
    s = np.sin(2 * np.pi * f * t) + 0.35 * np.tanh(3 * np.sin(2 * np.pi * f * 2 * t))
    return s * np.minimum(1, t / 0.005) * np.exp(-t * 3) * 0.55


def pluck(n, d=0.25):
    t = tt(d)
    s = saw(note(n), t, 0.004)
    s = lp(s, 3200)
    return s * np.exp(-t * 14) * 0.22


# ---------- arrangement ----------
# Intro (0-3): riser into logo hit at 1.22, ambient pad, drop at 3.0
add(riser(1.2), 0.02, 0.8)
add(impact(), 1.2, 1.0)
add(whoosh(0.55), 2.5, 0.7, -0.3)
for b in range(15):
    t0 = b * 2.0
    root, ch = CHORDS[b % 4]
    add(pad_bar(ch, 2.0), t0, 1.0 if t0 >= 3 else 0.7)

kick_times = []
for i in range(int(DUR / BEAT)):
    t = i * BEAT
    if t < 3.0 or t >= 29.0: continue
    if 26.5 <= t < 27.0: continue        # tiny break before the outro
    kick_times.append(t)
    add(kick(), t, 0.95)
    add(hat(), t + BEAT / 2, 0.22, 0.25)
    if i % 2 == 1: add(clap(), t, 0.42, -0.1)
    if t >= 12 and t < 23: add(hat(0.03), t + BEAT * 0.75, 0.12, -0.3)

# bass: 8ths on root, following chord
for b in range(15):
    root, ch = CHORDS[b % 4]
    for k in range(8):
        t = b * 2 + k * 0.25
        if t < 3.0 or t >= 29.0: continue
        n = root + (12 if k in (3, 7) else 0)
        add(bass_note(n, 0.24), t, 0.9 if k % 2 else 0.6)

# arpeggio pluck from S3 onward
for b in range(15):
    root, ch = CHORDS[b % 4]
    arp = [ch[0] + 12, ch[1] + 12, ch[2] + 12, ch[1] + 12, ch[0] + 24, ch[2] + 12, ch[1] + 12, ch[2] + 12]
    for k in range(8):
        t = b * 2 + k * 0.25
        if 7.0 <= t < 26.5:
            add(pluck(arp[k]), t, 1.0, 0.4 if k % 2 else -0.4)

# transitions & accents
for t in (3.0, 7.0, 12.0, 18.0, 23.0, 27.0):
    add(impact(), t, 0.55)
for t in (6.45, 11.45, 17.45, 22.5, 26.45):
    add(whoosh(0.55), t, 0.75, 0.2)
add(click(), 6.24, 0.9)
for i in range(5): add(click(), 7.5 + i * 0.25, 0.5, -0.6 + i * 0.3)
for i in range(5): add(click(), 13.0 + i * 0.45, 0.45, 0.5)
for t in (19.15, 20.15, 21.15): add(whoosh(0.35, rev=True), t - 0.1, 0.5, -0.4)
add(click(), 23.75, 0.6); add(click(), 24.12, 0.8)
add(ding(), 24.85, 1.0)
add(riser(1.0), 27.3, 0.6)
add(impact(), 28.28, 1.1)
add(ding(), 28.3, 0.7)
# final sustained chord
t = tt(1.7)
fin = sum(saw(note(n), t, 0.008) for n in (57, 64, 69, 72, 76))
add(lp(fin, 1800) * np.exp(-t * 1.2) * 0.25, 28.3, 1.0)

# sidechain ducking from kicks on the music bus
duck = np.ones(N)
tk = tt(0.35)
curve = 1 - 0.55 * np.exp(-tk * 14)
for k in kick_times:
    i = int(k * SR); duck[i:i + len(curve)] = np.minimum(duck[i:i + len(curve)], curve[:N - i])
L *= duck; R *= duck

mix = np.stack([L, R], 1)
mix = hp(mix.T, 28).T
mix = np.tanh(mix * 1.1) * 0.9
# fade out last 0.6s
fo = np.ones(N); n0 = int((DUR - 0.6) * SR); fo[n0:] = np.linspace(1, 0, N - n0) ** 2
mix *= fo[:, None]
mix /= np.max(np.abs(mix)) * 1.08
wavfile.write(sys.argv[1], SR, (mix * 32767).astype(np.int16))
print('ok', mix.shape)
