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
    ((0.00, 3.10), 0.2),     # « Tu publies sur TikTok… mais personne n'achète ? »
    ((3.30, 5.62), 3.5),     # « Voici trois erreurs… »
    ((5.88, 7.00), 6.5),     # « Erreur numéro un : »
    ((7.18, 11.20), 7.4),    # « commencer ta vidéo par ton logo. En deux secondes… »
    ((11.36, 13.55), 11.4),  # « Commence plutôt par le problème de ton client. »
    ((13.76, 14.90), 14.0),  # « Erreur numéro deux : »
    ((15.00, 21.70), 15.1),  # « répondre prix en inbox… à partir de »
    ((21.90, 23.12), 22.1),  # « Erreur numéro trois : »
    ((23.22, 27.42), 23.4),  # « laisser les messages sans réponse… ailleurs »
    ((27.45, 29.62), 27.6),  # « Réponds vite, même pour dire merci. »
    ((29.70, 34.32), 29.9),  # « Et toi… abonne-toi pour d'autres conseils ! »
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
