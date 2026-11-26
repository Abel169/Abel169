#!/usr/bin/env bash
# Regenerates orange-mastercard-tuto-9x16.mp4 (1080x1920, 53 s). Fictional data, "SIMULATION" mockup.
set -euo pipefail
cd "$(dirname "$0")"
TMP=${TMP_DIR:-$(mktemp -d)}
DUR=53 SIZE=1080x1920 node render.js frames "$TMP/frames" 60 4
python3 sfx.py "$TMP/sfx.wav"
ffmpeg -y -t 53 -i assets/music-victoire.mp3 -af "afade=t=out:st=51:d=2" -ar 44100 -ac 2 "$TMP/music.wav"
ffmpeg -y -i "$TMP/music.wav" -i "$TMP/sfx.wav" -filter_complex "[0:a]volume=1.0[m];[1:a]volume=0.32[s];[m][s]amix=inputs=2:normalize=0[a]" -map "[a]" "$TMP/mix.wav"
ffmpeg -y -framerate 60 -i "$TMP/frames/f%05d.jpg" -i "$TMP/mix.wav" \
  -vf "tmix=frames=2,fps=30,format=yuv420p" -af "loudnorm=I=-14:TP=-1:LRA=11" -ar 44100 \
  -c:v libx264 -preset slow -crf 18 -profile:v high -movflags +faststart -c:a aac -b:a 192k -shortest orange-mastercard-tuto-9x16.mp4
