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

# Version with voiceover (voice generated with ElevenLabs, saved in assets/voiceover.mp3)
ffmpeg -y -i assets/voiceover.mp3 -ar 44100 -ac 1 "$TMP/voice.wav"
python3 mix_voice.py "$TMP/music.wav" "$TMP/voice.wav" "$TMP/mix.wav"
ffmpeg -y -i okplus-showreel.mp4 -i "$TMP/mix.wav" -map 0:v -map 1:a -c:v copy -af "volume=-3.1dB" \
  -c:a aac -b:a 192k -movflags +faststart okplus-showreel-voix.mp4
echo "-> okplus-showreel-voix.mp4"

# 9:16 version for social media (same timing, vertical layouts in vertical.html, with voiceover)
PAGE=vertical.html SIZE=1080x1920 node render.js frames "$TMP/vframes" 60 4
ffmpeg -y -framerate 60 -i "$TMP/vframes/f%05d.jpg" -i "$TMP/mix.wav" \
  -vf "tmix=frames=2,fps=30,format=yuv420p" -af "volume=-3.1dB" \
  -c:v libx264 -preset slow -crf 18 -profile:v high -movflags +faststart \
  -c:a aac -b:a 192k -shortest okplus-showreel-9x16.mp4
echo "-> okplus-showreel-9x16.mp4"
