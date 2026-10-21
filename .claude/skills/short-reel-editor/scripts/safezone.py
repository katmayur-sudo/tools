"""Tint the Instagram safe-zone guide over storyboard frames and tile them into one sheet.
usage: safezone.py <frames_dir> <safezone_mask.png> <out.jpg> [cols=8]"""
import glob, os, subprocess, sys, tempfile
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))  # -I mode skips the script dir
from common import FF

frames = sorted(glob.glob(os.path.join(sys.argv[1], "frame-*.png")))
mask, out = sys.argv[2], sys.argv[3]; cols = int(sys.argv[4]) if len(sys.argv) > 4 else 8
tmp = tempfile.mkdtemp()
for i, f in enumerate(frames):
    subprocess.run([FF, "-v", "error", "-y", "-i", f, "-i", mask, "-filter_complex",
                    "[1:v]scale=1080:1920,colorkey=white:0.25:0.1,format=rgba,colorchannelmixer=aa=0.45[m];[0:v][m]overlay,scale=270:480",
                    f"{tmp}/{i:03d}.png"], check=True)
rows = (len(frames) + cols - 1) // cols
subprocess.run([FF, "-v", "error", "-y", "-framerate", "1", "-i", f"{tmp}/%03d.png", "-vf",
                f"tile={cols}x{rows}:padding=4:color=black", "-frames:v", "1", "-update", "1", out], check=True)
print(len(frames), "frames ->", out)
