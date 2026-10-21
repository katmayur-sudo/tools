"""Per-sample head pitch on a head crop (mediapipe FaceLandmarker) -> look-down detection.
usage: gaze.py VIDEO OUT.json [fps=15] [--crop W,X,Y]   crop = square of width W*iw at (X*iw, Y*ih)
pitch > ~11-15 deg or no face = looking down. Downloads the face model on first run."""
import sys, json, subprocess, math, os, urllib.request, numpy as np, mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))  # -I mode skips the script dir
from common import FF

MODEL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "face_landmarker.task")
URL = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"
if not os.path.exists(MODEL):
    urllib.request.urlretrieve(URL, MODEL)
args = [a for a in sys.argv[1:] if not a.startswith("--")]
src, out = args[0], args[1]
fps = float(args[2]) if len(args) > 2 else 15
cw, cx, cy = 0.6, 0.2, 0.36
if "--crop" in sys.argv:
    cw, cx, cy = map(float, sys.argv[sys.argv.index("--crop") + 1].split(","))
W = 640
lm = vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=MODEL), output_facial_transformation_matrixes=True, num_faces=1))
p = subprocess.Popen([FF, "-v", "error", "-i", src, "-vf", f"fps={fps},crop=iw*{cw}:iw*{cw}:iw*{cx}:ih*{cy},scale={W}:{W}",
                      "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
res, i = [], 0
while True:
    buf = p.stdout.read(W * W * 3)
    if len(buf) < W * W * 3:
        break
    r = lm.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.frombuffer(buf, np.uint8).reshape(W, W, 3)))
    t = round(i / fps, 2); i += 1
    if not r.face_landmarks:
        res.append({"t": t, "face": 0}); continue
    m = np.array(r.facial_transformation_matrixes[0])
    res.append({"t": t, "face": 1, "pitch": round(math.degrees(math.atan2(-m[1, 2], m[2, 2])), 1)})
json.dump(res, open(out, "w"))
print(len(res), "samples;", sum(1 for x in res if not x["face"]), "without a face")
