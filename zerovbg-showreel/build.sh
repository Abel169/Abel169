#!/usr/bin/env bash
# Regenerates zerovbg-showreel-9x16.mp4 (1080x1920, 9:16, 30 fps, H.264 + AAC, -14 LUFS).
# Needs: node + playwright (Chromium), python3 + numpy + scipy, ffmpeg.
set -euo pipefail
cd "$(dirname "$0")"
TMP=${TMP_DIR:-$(mktemp -d)}
SIZE=1080x1920 node render.js frames "$TMP/frames" 60 4
python3 music.py "$TMP/music.wav"
ffmpeg -y -framerate 60 -i "$TMP/frames/f%05d.jpg" -i "$TMP/music.wav" \
  -vf "tmix=frames=2,fps=30,format=yuv420p" -af "loudnorm=I=-14:TP=-1:LRA=11" -ar 44100 \
  -c:v libx264 -preset slow -crf 18 -profile:v high -movflags +faststart \
  -c:a aac -b:a 192k -shortest zerovbg-showreel-9x16.mp4
echo "-> zerovbg-showreel-9x16.mp4"
