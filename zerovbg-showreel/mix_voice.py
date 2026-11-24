"""Zéro VBG: place voiceover lines on their scenes, duck the music under the voice, master the mix.
Usage: python3 mix_voice.py music.wav voice.wav out.wav  (all 44.1 kHz)"""
import sys
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR = 44100
music_path, voice_path, out_path = sys.argv[1:4]
_, m = wavfile.read(music_path); m = m.astype(np.float64) / 32768
_, v = wavfile.read(voice_path); v = v.astype(np.float64) / 32768
if v.ndim == 2: v = v.mean(1)
N = len(m)

# (start, end) in the voice file  ->  position in the film (s)
LINES = [
    ((0.00, 2.10), 0.15),    # « Le silence protège les agresseurs. »
    ((2.38, 3.11), 2.45),    # « Brisons-le. »
    ((3.48, 4.47), 3.65),    # « Zéro VBG. »                -> logo reveal
    ((4.83, 7.30), 4.6),     # « Ensemble contre les violences basées sur le genre. »
    ((7.76, 9.78), 7.3),     # « S'informer, et comprendre ses droits. »
    ((10.03, 10.69), 12.55), # « Dénoncer : »
    ((10.96, 13.46), 13.6),  # « par la voix, par téléphone, ou par formulaire. »
    ((13.71, 17.31), 18.4),  # « Victime, témoin ou agent : chaque signalement est sécurisé. »
    ((17.70, 20.00), 22.9),  # « Personne ne doit rester seul face à la violence. »
    ((20.35, 21.29), 26.6),  # « Zéro VBG. »                -> outro icon
    ((21.59, 22.21), 27.45), # « Ensemble, »
    ((22.40, 23.64), 27.95), # « brisons le silence. »
]

# voice clean-up: high-pass, light compression, normalise
v = sosfilt(butter(2, 90, 'high', fs=SR, output='sos'), v)
v = sosfilt(butter(1, [2500, 6000], 'band', fs=SR, output='sos'), v) * 0.25 + v   # presence lift
v = np.tanh(v / np.max(np.abs(v)) * 1.6) / np.tanh(1.6)

vt = np.zeros(N)
for (a, b), at in LINES:
    seg = v[int(a * SR):int(b * SR)].copy()
    f = int(0.012 * SR); seg[:f] *= np.linspace(0, 1, f); seg[-f:] *= np.linspace(1, 0, f)
    i = int(at * SR); seg = seg[:N - i]
    vt[i:i + len(seg)] += seg

# ducking envelope (attack 40 ms, release 250 ms) -> music down ~9 dB under voice
env = np.abs(vt)
win = int(0.03 * SR); env = np.convolve(env, np.ones(win) / win, 'same')
act = (env > 0.02).astype(float)
duck = np.zeros(N); g = 0.0
att, rel = 1 / (0.04 * SR), 1 / (0.25 * SR)
for i in range(0, N, 64):
    target = act[i]
    g = min(target, g + att * 64) if target > g else max(target, g - rel * 64)
    duck[i:i + 64] = g
mg = 1 - 0.65 * duck

mix = m * mg[:, None] * 0.85 + vt[:, None] * 0.78
mix = np.tanh(mix * 1.05)
mix /= np.max(np.abs(mix)) * 1.06
wavfile.write(out_path, SR, (mix * 32767).astype(np.int16))
print('ok')
