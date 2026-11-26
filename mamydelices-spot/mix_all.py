"""Final mix for the Mamy Délices spot: music (ducked) + voiceover lines + sound effects.
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
    ((0.00, 1.19), 0.25),    # « Une envie de douceur ? »
    ((1.61, 2.28), 1.55),    # (chuchoté) « Ne mens pas… »         -> vanilla starts dripping
    ((2.61, 3.22), 2.35),    # « je t'ai vu. »                      -> drop falls
    ((3.63, 6.22), 3.4),     # « Mamy Délices ! Le goût de la différence ! »
    ((6.36, 8.23), 7.4),     # « Gâteaux, glaces, viennoiseries… »  -> tiles fly out
    ((8.39, 9.52), 9.45),    # « tout est dans ton téléphone ! »
    ((9.78, 10.50), 14.0),   # « Tu choisis… »                       -> tap on cakes
    ((10.66, 12.10), 15.45), # « tu personnalises… (rire) »          -> 8 parts, +
    ((12.17, 13.35), 17.25), # « et hop, dans le panier ! »          -> cake flies to cart
    ((13.46, 15.74), 19.55), # « Cent pour cent fait maison, depuis 2012. »
    ((15.94, 17.61), 23.6),  # « Et on te livre partout à Bamako ! »
    ((17.76, 19.45), 26.3),  # « Télécharge l'appli Mamy Délices… »
    ((19.65, 21.60), 28.0),  # « (rire) ton ventre te dira merci ! »
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
