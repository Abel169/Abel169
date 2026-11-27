#!/usr/bin/env bash
# Regenerates histoire-toguna-9x16.mp4 (62 s): frames + original kora music + SFX + Tony voiceover.
set -euo pipefail
cd "$(dirname "$0")"
TMP=${TMP_DIR:-$(mktemp -d)}
DUR=62 SIZE=1080x1920 node render.js frames "$TMP/frames" 60 4
python3 sfx.py "$TMP/sfx.wav"
python3 music_kora.py "$TMP/music.wav" 62 28.8 42.0
ffmpeg -y -i assets/voiceover.mp3 -ar 44100 -ac 1 "$TMP/voice.wav"
python3 mix_all.py "$TMP/music.wav" "$TMP/voice.wav" "$TMP/sfx.wav" "$TMP/final.wav"
ffmpeg -y -framerate 60 -i "$TMP/frames/f%05d.jpg" -i "$TMP/final.wav" \
  -vf "tmix=frames=2,fps=30,format=yuv420p" -af "loudnorm=I=-14:TP=-1:LRA=11" -ar 44100 \
  -c:v libx264 -preset slow -crf 18 -profile:v high -movflags +faststart -c:a aac -b:a 192k -shortest histoire-toguna-9x16.mp4
