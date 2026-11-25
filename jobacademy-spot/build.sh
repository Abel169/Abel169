#!/usr/bin/env bash
# Regenerates jobacademy-spot-9x16.mp4 (1080x1920, 30 s) with "Victoire" (from 3:15) + synthesized SFX.
set -euo pipefail
cd "$(dirname "$0")"
TMP=${TMP_DIR:-$(mktemp -d)}
SIZE=1080x1920 node render.js frames "$TMP/frames" 60 4
python3 sfx.py "$TMP/sfx.wav"
ffmpeg -y -ss 195 -t 30 -i assets/music-victoire.mp3 -af "afade=t=in:d=0.1,afade=t=out:st=28.6:d=1.4" -ar 44100 -ac 2 "$TMP/music.wav"
ffmpeg -y -i "$TMP/music.wav" -i "$TMP/sfx.wav" -filter_complex "[0:a]volume=0.8[m];[1:a]volume=0.85[s];[m][s]amix=inputs=2:normalize=0[a]" -map "[a]" "$TMP/mix.wav"
ffmpeg -y -framerate 60 -i "$TMP/frames/f%05d.jpg" -i "$TMP/mix.wav" \
  -vf "tmix=frames=2,fps=30,format=yuv420p" -af "loudnorm=I=-14:TP=-1:LRA=11" -ar 44100 \
  -c:v libx264 -preset slow -crf 18 -profile:v high -movflags +faststart -c:a aac -b:a 192k -shortest jobacademy-spot-9x16.mp4

# Version with voiceover (Elisa): first 30 s of "Victoire", ducked under the voice, SFX kept
ffmpeg -y -t 30 -i assets/music-victoire.mp3 -af "afade=t=out:st=28.6:d=1.4" -ar 44100 -ac 2 "$TMP/music0.wav"
ffmpeg -y -i assets/voiceover.mp3 -ar 44100 -ac 1 "$TMP/voice.wav"
python3 mix_all.py "$TMP/music0.wav" "$TMP/voice.wav" "$TMP/sfx.wav" "$TMP/final.wav"
ffmpeg -y -i jobacademy-spot-9x16.mp4 -i "$TMP/final.wav" -map 0:v -map 1:a -c:v copy \
  -af "loudnorm=I=-14:TP=-1:LRA=11" -ar 44100 -c:a aac -b:a 192k -movflags +faststart -shortest jobacademy-spot-9x16-voix.mp4
