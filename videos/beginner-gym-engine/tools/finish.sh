#!/usr/bin/env bash
# Join the rendered video chunks and mux the final soundtrack.
# Usage: finish.sh <chunks_dir> <mix.wav> <out.mp4>
set -euo pipefail
chunks=${1:?chunks dir}
mix=${2:?mix.wav}
out=${3:?out.mp4}

ls "$chunks"/chunk_*.mp4 | sort | sed "s/^/file '/;s/$/'/" > "$chunks/list.txt"
ffmpeg -hide_banner -loglevel error -y -f concat -safe 0 -i "$chunks/list.txt" -i "$mix" \
  -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -movflags +faststart -shortest "$out"
ffprobe -v error -show_entries format=duration,size -of default=nw=1 "$out"
