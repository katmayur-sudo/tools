"""Render the two talking-head layers from the approved cut with ONE fixed crop (camera is static).
usage: crop.py cut.mp4 --center-x 515 [--out assets] [--face-y 520]
  talk_c.mp4: full-face 1080x1920 (crop 720x1280)   talk_a.mp4: speaker card 980x720 (crop 760x558)
Measure center-x as the middle of the chair/seat on a few frames from different takes."""
import argparse, os, subprocess
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))  # -I mode skips the script dir
from common import FF

ap = argparse.ArgumentParser()
ap.add_argument("cut"); ap.add_argument("--center-x", type=int, required=True)
ap.add_argument("--out", default="assets"); ap.add_argument("--face-y", type=int, default=520)
ap.add_argument("--card-y", type=int, default=760)
a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
jobs = [(f"crop=720:1280:{a.center_x - 360}:{a.face_y},scale=1080:1920:flags=lanczos", "talk_c.mp4", "16"),
        (f"crop=760:558:{a.center_x - 380}:{a.card_y},scale=980:720:flags=lanczos", "talk_a.mp4", "17")]
procs = [subprocess.Popen([FF, "-v", "error", "-y", "-i", a.cut, "-an", "-vf", f"{vf},fps=30", "-c:v", "libx264",
                           "-crf", crf, "-preset", "fast", "-pix_fmt", "yuv420p", "-g", "15", f"{a.out}/{name}"])
         for vf, name, crf in jobs]
for p in procs: p.wait()
print("wrote", ", ".join(f"{a.out}/{n}" for _, n, _ in jobs))
