#!/usr/bin/env bash
# Regenerates sugupro-showreel-9x16.mp4 (1080x1920, 9:16, 30 fps, H.264 + AAC).
# Needs: node + playwright (Chromium), python3 + numpy + scipy, ffmpeg.
set -euo pipefail
cd "$(dirname "$0")"
TMP=${TMP_DIR:-$(mktemp -d)}
SIZE=1080x1920 node render.js frames "$TMP/frames" 60 4
python3 music.py "$TMP/music.wav"
ffmpeg -y -framerate 60 -i "$TMP/frames/f%05d.jpg" -i "$TMP/music.wav" \
  -vf "tmix=frames=2,fps=30,format=yuv420p" -af "loudnorm=I=-14:TP=-1:LRA=11" -ar 44100 \
  -c:v libx264 -preset slow -crf 18 -profile:v high -movflags +faststart \
  -c:a aac -b:a 192k -shortest sugupro-showreel-9x16.mp4
echo "-> sugupro-showreel-9x16.mp4"

# Version with voiceover + the client's music ("Victoire", first 30 s, provided in assets/)
ffmpeg -y -t 30 -i assets/music-victoire.mp3 -af "afade=t=out:st=28.8:d=1.2" -ar 44100 -ac 2 "$TMP/victoire30.wav"
ffmpeg -y -i assets/voiceover.mp3 -ar 44100 -ac 1 "$TMP/voice.wav"
python3 mix_voice.py "$TMP/victoire30.wav" "$TMP/voice.wav" "$TMP/mix.wav"
ffmpeg -y -i sugupro-showreel-9x16.mp4 -i "$TMP/mix.wav" -map 0:v -map 1:a -c:v copy \
  -af "loudnorm=I=-14:TP=-1:LRA=11" -ar 44100 -c:a aac -b:a 192k -movflags +faststart -shortest sugupro-showreel-9x16-voix.mp4
echo "-> sugupro-showreel-9x16-voix.mp4"
