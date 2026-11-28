#!/usr/bin/env bash
# Regenerates typo-statut-whatsapp-9x16.mp4 (21.5 s): kinetic typography, SFX only (music added on TikTok).
set -euo pipefail
cd "$(dirname "$0")"
TMP=${TMP_DIR:-$(mktemp -d)}
DUR=21.5 SIZE=1080x1920 node render.js frames "$TMP/frames" 60 4
python3 sfx.py "$TMP/sfx.wav"
ffmpeg -y -framerate 60 -i "$TMP/frames/f%05d.jpg" -i "$TMP/sfx.wav" -vf "tmix=frames=2,fps=30,format=yuv420p" \
  -af "loudnorm=I=-20:TP=-2:LRA=11" -ar 44100 -c:v libx264 -preset slow -crf 18 -profile:v high -movflags +faststart -c:a aac -b:a 192k -shortest typo-statut-whatsapp-9x16.mp4
