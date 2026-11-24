#!/usr/bin/env bash
# Regenerates sogoba-creative-promo-9x16.mp4 (1080x1920, 9:16, 30 fps, H.264 + AAC).
# Needs the three showreel MP4s in ../okplus-showreel, ../zerovbg-showreel, ../sugupro-showreel.
set -euo pipefail
cd "$(dirname "$0")"
TMP=${TMP_DIR:-$(mktemp -d)}
mkdir -p clips
X(){ ffmpeg -loglevel error -y -ss "$2" -t "$3" -i "$1" -vf "fps=30,scale=$5" -q:v 3 "clips/$4_%03d.jpg"; }
X ../sugupro-showreel/sugupro-showreel-9x16.mp4 8.0 2.1 sg1 540:960
X ../zerovbg-showreel/zerovbg-showreel-9x16.mp4 13.4 1.6 zv1 540:960
X ../okplus-showreel/okplus-showreel-9x16.mp4 19.0 1.6 ok1 540:960
X ../sugupro-showreel/sugupro-showreel-9x16.mp4 18.9 1.6 sg2 540:960
X ../okplus-showreel/okplus-showreel.mp4 0.6 1.6 ok2 960:540
X ../zerovbg-showreel/zerovbg-showreel-9x16.mp4 1.9 1.6 zv2 540:960
X ../sugupro-showreel/sugupro-showreel-9x16.mp4 13.0 1.6 sg3 540:960
X ../sugupro-showreel/sugupro-showreel-9x16.mp4 26.6 3.0 sg4 360:640
X ../zerovbg-showreel/zerovbg-showreel-9x16.mp4 26.4 3.0 zv4 360:640
X ../okplus-showreel/okplus-showreel-9x16.mp4 27.0 3.0 ok4 360:640
SIZE=1080x1920 node render.js frames "$TMP/frames" 60 4
python3 music.py "$TMP/music.wav"
ffmpeg -y -framerate 60 -i "$TMP/frames/f%05d.jpg" -i "$TMP/music.wav" \
  -vf "tmix=frames=2,fps=30,format=yuv420p" -af "loudnorm=I=-14:TP=-1:LRA=11" -ar 44100 \
  -c:v libx264 -preset slow -crf 18 -profile:v high -movflags +faststart \
  -c:a aac -b:a 192k -shortest sogoba-creative-promo-9x16.mp4
echo "-> sogoba-creative-promo-9x16.mp4"
