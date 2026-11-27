"""Final mix for the Sogoba presentation: music (ducked) + voiceover lines + sound effects.
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
    ((0.00, 3.55), 0.2),     # « En 1989, il vendait de l'engrais avec son père. »
    ((3.70, 6.40), 3.9),     # « Quelques années plus tard… il le fabriquait. »
    ((6.60, 9.90), 6.9),     # « Seydou Nantoumé, né au pays dogon, commence petit : »
    ((10.00, 12.95), 10.3),  # « il achète… pour le revendre. »
    ((13.05, 18.70), 13.5),  # « Petit à petit… de Côte d'Ivoire et du Sénégal. »
    ((18.80, 28.10), 19.3),  # « En 1994… Les débuts ne sont pas faciles. »
    ((28.15, 33.55), 28.9),  # « En 2006… Il le fait quand même. »
    ((33.65, 39.40), 36.2),  # « En 2009… sa matière première. »
    ((39.45, 45.60), 42.1),  # « En 2016… neuf pays. »
    ((45.70, 53.35), 48.5),  # « La leçon… fabricant. »
    ((53.40, 56.80), 56.5),  # « Quelle marque malienne… commentaire ! »
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

# voice-forward balance: music ~-9 dB and SFX ~-6 dB under the voice
mg = (1 - .66 * duck)[:, None] * 1.25
fg = (1 - .7 * duck)[:, None] * .16
mix = m * mg + fx * fg + vt[:, None] * 1.0
# report voice vs music level while the voice is speaking
on = duck > .9
rv = np.sqrt(np.mean(vt[on] ** 2)); rm = np.sqrt(np.mean((m * mg)[on] ** 2)); rf = np.sqrt(np.mean((fx * fg)[on] ** 2))
rfa = np.sqrt(np.mean((fx * fg) ** 2)); rma = np.sqrt(np.mean((m * mg) ** 2))
print(f'effets vs musique (global): {20*np.log10(rfa/rma):+.1f} dB')
print(f'voix vs musique: +{20*np.log10(rv/rm):.1f} dB | voix vs effets: +{20*np.log10(rv/rf):.1f} dB')
mix = np.tanh(mix * 1.05); mix /= np.max(np.abs(mix)) * 1.06
wavfile.write(out, SR, (mix * 32767).astype(np.int16)); print('ok')
