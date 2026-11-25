"""Final mix for the launch-offer video: music (ducked) + voiceover lines + sound effects.
Usage: python3 mix_all.py music.wav voice.wav sfx.wav out.wav   (all 44.1 kHz)"""
import sys
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR = 44100
mp, vp, sp, out = sys.argv[1:5]
load = lambda p: wavfile.read(p)[1].astype(np.float64) / 32768
m = load(mp); v = load(vp); fx = load(sp)
if v.ndim == 2: v = v.mean(1)
N = len(m); fx = fx[:N]

# (start, end) in the voice file -> position in the video (s)
LINES = [
    ((0.00, 0.88), 0.1),     # « Tu as un commerce ? »
    ((1.21, 2.10), 0.85),    # « Tes photos ne vendent pas ? »
    ((2.41, 5.02), 3.65),    # « Je les transforme en pubs vidéo qui donnent envie d'acheter ! »
    ((5.32, 6.16), 8.15),    # « Offre de lancement ! »        -> impact + confetti
    ((6.26, 7.34), 9.4),     # « Seulement cinq places. »      -> tickets
    ((7.48, 9.11), 11.15),   # « Des prix de lancement sur tous les packs ! »
    ((9.32, 11.72), 18.3),   # « Livraison en 48 h, paiement Orange Money. »
    ((11.96, 14.14), 21.8),  # « Réserve ta place maintenant : écris-moi en DM ! »
    ((14.40, 15.60), 24.2),  # « Sogoba Créative. »
]

v = sosfilt(butter(2, 90, 'high', fs=SR, output='sos'), v)
v = v + sosfilt(butter(1, [2500, 6000], 'band', fs=SR, output='sos'), v) * .25
v = np.tanh(v / np.max(np.abs(v)) * 1.6) / np.tanh(1.6)
vt = np.zeros(N)
for (a, b), at in LINES:
    seg = v[int(a * SR):int(b * SR)].copy(); f = int(.012 * SR)
    seg[:f] *= np.linspace(0, 1, f); seg[-f:] *= np.linspace(1, 0, f)
    i = int(at * SR); seg = seg[:N - i]; vt[i:i + len(seg)] += seg

env = np.convolve(np.abs(vt), np.ones(int(.03 * SR)) / int(.03 * SR), 'same')
act = (env > .02).astype(float); duck = np.zeros(N); g = 0.0
att, rel = 64 / (.04 * SR), 64 / (.25 * SR)
for i in range(0, N, 64):
    tgt = act[i]; g = min(tgt, g + att) if tgt > g else max(tgt, g - rel); duck[i:i + 64] = g

mix = m * (1 - .62 * duck)[:, None] * .8 + fx * (1 - .35 * duck)[:, None] * .75 + vt[:, None] * .8
mix = np.tanh(mix * 1.05); mix /= np.max(np.abs(mix)) * 1.06
wavfile.write(out, SR, (mix * 32767).astype(np.int16)); print('ok')
