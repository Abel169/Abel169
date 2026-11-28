#!/usr/bin/env bash
# Regenerates typo-statut-whatsapp-9x16-voix.mp4 (26.5 s): kinetic typography + voice "David" (ElevenLabs) + SFX.
set -euo pipefail
cd "$(dirname "$0")"
TMP=${TMP_DIR:-$(mktemp -d)}
DUR=26.5 SIZE=1080x1920 node render.js frames "$TMP/frames" 60 4
python3 sfx.py "$TMP/sfx.wav"
ffmpeg -y -i assets/voiceover.mp3 -ar 44100 -ac 1 "$TMP/voice.wav"
ffmpeg -y -i "$TMP/voice.wav" -i "$TMP/sfx.wav" -filter_complex "[0]adelay=200|200,highpass=f=80,acompressor=threshold=-20dB:ratio=3:attack=5:release=80[v];[1]volume=0.35[s];[v][s]amix=inputs=2:normalize=0:duration=longest[m]" -map "[m]" -t 26.5 "$TMP/mix.wav"
ffmpeg -y -framerate 60 -i "$TMP/frames/f%05d.jpg" -i "$TMP/mix.wav" -vf "tmix=frames=2,fps=30,format=yuv420p" \
  -af "loudnorm=I=-15:TP=-1.5:LRA=11" -ar 44100 -c:v libx264 -preset slow -crf 18 -profile:v high -movflags +faststart -c:a aac -b:a 192k -shortest typo-statut-whatsapp-9x16-voix.mp4
