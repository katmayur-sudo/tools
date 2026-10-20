#!/usr/bin/env bash
# Self-check helper: detect scene cuts and build frame grids an agent can look at.
# Usage: contact_sheet.sh <video> <out_dir> [scene_threshold=0.3] [every_n_seconds=1]
# Outputs:
#   <out_dir>/cuts.txt        timestamps (s) where a cut was detected
#   <out_dir>/cut_NNN.jpg     one frame just after each cut
#   <out_dir>/sheet_NN.jpg    4x4 grids of frames sampled every N seconds
set -euo pipefail

video=${1:?usage: contact_sheet.sh <video> <out_dir> [scene_threshold] [every_n_seconds]}
out=${2:?usage: contact_sheet.sh <video> <out_dir> [scene_threshold] [every_n_seconds]}
threshold=${3:-0.3}
every=${4:-1}

mkdir -p "$out"

ffprobe -v error -select_streams v:0 \
  -show_entries stream=width,height,r_frame_rate:format=duration \
  -of default=noprint_wrappers=1 "$video" | tee "$out/info.txt"

# Scene cuts
ffmpeg -hide_banner -nostats -i "$video" \
  -vf "select='gt(scene,${threshold})',showinfo" -f null - 2>&1 \
  | grep -o 'pts_time:[0-9.]*' | cut -d: -f2 > "$out/cuts.txt" || true
echo "cuts: $(wc -l < "$out/cuts.txt")"

i=0
while read -r t; do
  i=$((i + 1))
  ffmpeg -nostdin -hide_banner -loglevel error -y -ss "$t" -i "$video" -frames:v 1 \
    -vf "scale=480:-2" "$out/$(printf 'cut_%03d.jpg' "$i")"
done < "$out/cuts.txt"

# Timestamped contact sheets
ffmpeg -hide_banner -loglevel error -y -i "$video" \
  -vf "fps=1/${every},scale=320:-2,drawtext=text='%{pts\:hms}':x=6:y=6:fontsize=18:fontcolor=white:box=1:boxcolor=black@0.6,tile=4x4" \
  "$out/sheet_%02d.jpg"

echo "sheets: $(ls "$out"/sheet_*.jpg | wc -l) in $out"
