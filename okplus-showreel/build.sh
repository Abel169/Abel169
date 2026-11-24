#!/usr/bin/env bash
# Regenerates okplus-showreel.mp4 (1920x1080, 16:9, 30 fps, H.264 + AAC).
# Needs: node + playwright (Chromium), python3 + numpy + scipy, ffmpeg.
set -euo pipefail
cd "$(dirname "$0")"
TMP=${TMP_DIR:-$(mktemp -d)}
node render.js frames "$TMP/frames" 60 4          # 1800 frames at 60 fps
python3 music.py "$TMP/music.wav"                 # original synthesized soundtrack
# Blend frame pairs (60 -> 30 fps) for natural motion blur, then encode.
ffmpeg -y -framerate 60 -i "$TMP/frames/f%05d.jpg" -i "$TMP/music.wav" \
  -vf "tmix=frames=2,fps=30,format=yuv420p" \
  -c:v libx264 -preset slow -crf 17 -profile:v high -movflags +faststart \
  -c:a aac -b:a 192k -shortest okplus-showreel.mp4
echo "-> okplus-showreel.mp4"
