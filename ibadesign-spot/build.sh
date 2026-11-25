#!/usr/bin/env bash
# Regenerates ibadesign-fil-dor-9x16.mp4 (1080x1920, 25 s). Needs the source photos in photos/ (kept local, see .gitignore).
set -euo pipefail
cd "$(dirname "$0")"
TMP=${TMP_DIR:-$(mktemp -d)}
DUR=25 SIZE=1080x1920 node render.js frames "$TMP/frames" 60 4
python3 music.py "$TMP/music.wav"
ffmpeg -y -framerate 60 -i "$TMP/frames/f%05d.jpg" -i "$TMP/music.wav" \
  -vf "tmix=frames=2,fps=30,format=yuv420p" -af "loudnorm=I=-14:TP=-1:LRA=11" -ar 44100 \
  -c:v libx264 -preset slow -crf 17 -profile:v high -movflags +faststart \
  -c:a aac -b:a 192k -shortest ibadesign-fil-dor-9x16.mp4

# Version with voiceover (Dahlia, assets/voiceover.mp3) + client music "Victoire" (first 25 s)
ffmpeg -y -t 25 -i assets/music-victoire.mp3 -af "afade=t=out:st=23.6:d=1.4" -ar 44100 -ac 2 "$TMP/victoire.wav"
python3 mix_voice.py "$TMP/victoire.wav" assets/voiceover.mp3 "$TMP/mix.wav"
ffmpeg -y -i ibadesign-fil-dor-9x16.mp4 -i "$TMP/mix.wav" -map 0:v -map 1:a -c:v copy \
  -af "loudnorm=I=-14:TP=-1:LRA=11" -ar 44100 -c:a aac -b:a 192k -movflags +faststart -shortest ibadesign-fil-dor-9x16-voix.mp4
