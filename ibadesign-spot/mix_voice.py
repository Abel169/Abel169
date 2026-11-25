"""IBA Design spot: place the voiceover on the scenes, duck the music, master.
Usage: python3 mix_voice.py music.wav voice.mp3 out.wav"""
import sys, subprocess, tempfile, os
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR = 44100
mp, vp, out = sys.argv[1:4]
m = wavfile.read(mp)[1].astype(np.float64) / 32768
N = len(m)


def clip(a, b, tempo=1.0):
    """Extract voice[a:b] (s), optionally time-stretched without pitch change (ffmpeg atempo)."""
    with tempfile.TemporaryDirectory() as d:
        f = os.path.join(d, 'c.wav')
        af = f"atrim={a}:{b},asetpts=N/SR/TB" + (f",atempo={tempo}" if tempo != 1 else "")
        subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', vp, '-af', af, '-ar', str(SR), '-ac', '1', f], check=True)
        return wavfile.read(f)[1].astype(np.float64) / 32768


# (segments in the voice file, tempo, position in the video)
LINES = [
    ([(0.00, 0.89)], 1.0, 1.6),               # « IBA Design. »                       -> logo reveal
    ([(1.50, 3.60)], 1.0, 4.0),               # « Quand l'élégance devient une signature. »
    ([(3.98, 7.81)], 1.0, 6.6),               # « Des abayas raffinées, brodées avec soin, pensées pour chaque femme. »
    ([(8.06, 10.83)], 1.0, 11.0),             # « Des pièces d'exception, pour sublimer chaque instant. »
    ([(11.10, 14.18)], 1.08, 14.9),           # « Découvrez notre boutique, à Hamdallaye ACI 2000. »
    ([(14.39, 15.22)], 1.0, 17.75),           # « Abaya Bijoux. »
    ([(15.44, 16.25)], 1.0, 18.6),            # « Abaya Bibi. »
    ([(16.43, 18.91)], 1.0, 19.6),            # « Recommandée par 90 % de nos clientes. »
    ([(19.28, 20.00), (20.60, 22.58)], 1.0, 22.05),  # « IBA Design. Prêt-à-porter féminin, à Bamako. »
]

vt = np.zeros(N)
for segs, tempo, at in LINES:
    parts = []
    for a, b in segs:
        c = clip(a, b, tempo); f = int(.012 * SR); c[:f] *= np.linspace(0, 1, f); c[-f:] *= np.linspace(1, 0, f)
        parts += [c, np.zeros(int(.15 * SR))]
    seg = np.concatenate(parts[:-1])
    i = int(at * SR); seg = seg[:N - i]; vt[i:i + len(seg)] += seg
    print(f'{at:5.2f}s -> {at + len(seg) / SR:5.2f}s')

vt = sosfilt(butter(2, 90, 'high', fs=SR, output='sos'), vt)
vt = vt + sosfilt(butter(1, [2500, 6000], 'band', fs=SR, output='sos'), vt) * .2
vt = np.tanh(vt / np.max(np.abs(vt)) * 1.5) / np.tanh(1.5)

env = np.convolve(np.abs(vt), np.ones(int(.03 * SR)) / int(.03 * SR), 'same')
act = (env > .02).astype(float); duck = np.zeros(N); g = 0.0
for i in range(0, N, 64):
    tgt = act[i]; g = min(tgt, g + 64 / (.06 * SR)) if tgt > g else max(tgt, g - 64 / (.35 * SR)); duck[i:i + 64] = g
mix = m * (1 - .6 * duck)[:, None] * .85 + vt[:, None] * .82
mix = np.tanh(mix * 1.05); mix /= np.max(np.abs(mix)) * 1.06
wavfile.write(out, SR, (mix * 32767).astype(np.int16)); print('ok')
