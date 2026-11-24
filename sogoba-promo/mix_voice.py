"""Sogoba Creative promo: place voiceover lines on their scenes, duck the music under the voice, master the mix.
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
    ((0.00, 1.61), 0.1),     # « Ta marque mérite de bouger. »
    ((1.94, 3.29), 3.4),     # « Sogoba Créative ! »                   -> name reveal
    ((3.49, 5.35), 4.95),    # « Spots publicitaires avec l'IA. »       -> bio pills
    ((5.64, 8.52), 7.0),     # « Des vidéos qui captent l'attention… »  -> showreel
    ((8.89, 12.21), 11.8),   # « Applications, marques, campagnes : je donne vie à vos idées. »
    ((12.52, 13.74), 17.6),  # « Des projets qui parlent. »             -> portfolio title
    ((13.96, 14.55), 21.1),  # « Design. »
    ((14.64, 15.17), 21.6),  # « Vidéo. »
    ((15.27, 16.13), 22.1),  # « Motion design. »
    ((16.29, 18.61), 22.9),  # « Des idées, des images, de l'impact ! »
    ((18.75, 19.49), 25.55), # « Abonne-toi ! »                          -> tap on the button
    ((19.65, 21.35), 26.6),  # « Et pour tes projets, écris-moi en DM. »
    ((21.53, 22.90), 28.4),  # « Sogoba Créative. »
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
