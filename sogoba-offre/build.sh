#!/usr/bin/env bash
# Regenerates sogoba-offre-lancement-9x16.mp4 (1080x1920, 26 s). Prices: edit PACKS in index.html.
# Needs ../sogoba-promo/clips (run ../sogoba-promo/build.sh once first).
set -euo pipefail
cd "$(dirname "$0")"
TMP=${TMP_DIR:-$(mktemp -d)}
DUR=26 SIZE=1080x1920 node render.js frames "$TMP/frames" 60 4
ffmpeg -y -ss 60 -t 26 -i assets/music-victoire.mp3 -af "afade=t=in:d=0.1,afade=t=out:st=24.8:d=1.2" -ar 44100 -ac 2 "$TMP/music.wav"
ffmpeg -y -framerate 60 -i "$TMP/frames/f%05d.jpg" -i "$TMP/music.wav" \
  -vf "tmix=frames=2,fps=30,format=yuv420p" -af "loudnorm=I=-14:TP=-1:LRA=11" -ar 44100 \
  -c:v libx264 -preset slow -crf 18 -profile:v high -movflags +faststart \
  -c:a aac -b:a 192k -shortest sogoba-offre-lancement-9x16.mp4
