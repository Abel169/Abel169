"""Final mix for the Orange Mastercard tutorial: music (ducked) + voiceover lines + sound effects.
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
    ((0.00, 2.68), 0.2),     # « Tu veux acheter en ligne, mais tu n'as pas de carte bancaire ? »
    ((3.04, 5.25), 3.6),     # « Étape un : ouvre l'appli Max it. »
    ((5.61, 8.70), 7.1),     # « Étape deux : touche la loupe, et tape Mastercard. »
    ((9.08, 10.88), 11.1),   # « Étape trois : touche Acheter. »
    ((11.19, 15.53), 14.1),  # « Étape quatre : choisis la carte virtuelle, à mille francs, et remplis tes informations. »
    ((15.88, 17.90), 19.6),  # « Étape cinq : accepte les conditions. »
    ((18.26, 21.57), 23.1),  # « Étape six : tape ton code secret Orange Money, et confirme. »
    ((21.83, 23.79), 30.6),  # « Félicitations, ta carte est prête ! »  -> card reveal
    ((24.13, 27.94), 34.4),  # « Étape sept : active-la avec ta première recharge, dès 500 francs. »
    ((28.29, 30.97), 40.1),  # « Étape huit : paie en ligne, en toute simplicité ! »
    ((31.19, 34.25), 48.6),  # « Et surtout, ne partage jamais ton code ni ton CVV. »
    ((34.55, 35.47), 51.9),  # « À toi de jouer ! »
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
mg = (1 - .66 * duck)[:, None] * .72
fg = (1 - .7 * duck)[:, None] * .24
mix = m * mg + fx * fg + vt[:, None] * 1.0
# report voice vs music level while the voice is speaking
on = duck > .9
rv = np.sqrt(np.mean(vt[on] ** 2)); rm = np.sqrt(np.mean((m * mg)[on] ** 2)); rf = np.sqrt(np.mean((fx * fg)[on] ** 2))
rfa = np.sqrt(np.mean((fx * fg) ** 2)); rma = np.sqrt(np.mean((m * mg) ** 2))
print(f'effets vs musique (global): {20*np.log10(rfa/rma):+.1f} dB')
print(f'voix vs musique: +{20*np.log10(rv/rm):.1f} dB | voix vs effets: +{20*np.log10(rv/rf):.1f} dB')
mix = np.tanh(mix * 1.05); mix /= np.max(np.abs(mix)) * 1.06
wavfile.write(out, SR, (mix * 32767).astype(np.int16)); print('ok')
