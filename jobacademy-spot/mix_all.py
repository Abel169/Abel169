"""Final mix for the Job Academy spot: music (ducked) + voiceover lines + sound effects.
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
    ((0.00, 2.82), 0.1),     # « Diplôme en poche… mais toujours pas de job ? »
    ((3.06, 3.99), 3.6),     # « Job Academy ! »                    -> logo
    ((4.18, 6.75), 4.75),    # « L'école qui t'enseigne à décrocher le job de tes rêves. »
    ((7.00, 10.39), 7.6),    # « Orientation, compétences, CV, préparation à l'emploi : »
    ((10.58, 12.32), 11.1),  # « on t'accompagne étape par étape. »
    ((12.57, 15.29), 13.4),  # « Des guides et des mini-cours concrets, et certains sont gratuits ! »
    ((15.59, 18.70), 20.2),  # « Simple, pratique, accessible, même avec un smartphone. »
    ((18.99, 21.17), 23.65), # « Avec Job Academy, tu ne restes pas seul. »
    ((21.41, 24.12), 27.0),  # « Rendez-vous sur job-academy point online ! »
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
