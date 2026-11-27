#!/usr/bin/env bash
# Regenerates tuto-whatsapp-business-9x16.mp4 (41 s) and, if assets/voiceover.mp3 exists, the -voix version.
set -euo pipefail
cd "$(dirname "$0")"
TMP=${TMP_DIR:-$(mktemp -d)}
DUR=41 SIZE=1080x1920 node render.js frames "$TMP/frames" 60 4
python3 sfx.py "$TMP/sfx.wav"
ffmpeg -y -t 41 -i assets/music-victoire.mp3 -af "afade=t=out:st=39:d=2" -ar 44100 -ac 2 "$TMP/music.wav"
ffmpeg -y -i "$TMP/music.wav" -i "$TMP/sfx.wav" -filter_complex "[0:a]volume=1.0[m];[1:a]volume=0.32[s];[m][s]amix=inputs=2:normalize=0[a]" -map "[a]" "$TMP/mix.wav"
ffmpeg -y -framerate 60 -i "$TMP/frames/f%05d.jpg" -i "$TMP/mix.wav" \
  -vf "tmix=frames=2,fps=30,format=yuv420p" -af "loudnorm=I=-14:TP=-1:LRA=11" -ar 44100 \
  -c:v libx264 -preset slow -crf 18 -profile:v high -movflags +faststart -c:a aac -b:a 192k -shortest tuto-whatsapp-business-9x16.mp4
if [ -f assets/voiceover.mp3 ]; then
  ffmpeg -y -i assets/voiceover.mp3 -ar 44100 -ac 1 "$TMP/voice.wav"
  python3 mix_all.py "$TMP/music.wav" "$TMP/voice.wav" "$TMP/sfx.wav" "$TMP/final.wav"
  ffmpeg -y -i tuto-whatsapp-business-9x16.mp4 -i "$TMP/final.wav" -map 0:v -map 1:a -c:v copy \
    -af "loudnorm=I=-14:TP=-1:LRA=11" -ar 44100 -c:a aac -b:a 192k -movflags +faststart -shortest tuto-whatsapp-business-9x16-voix.mp4
fi
