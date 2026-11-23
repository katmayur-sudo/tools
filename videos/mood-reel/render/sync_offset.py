# Audio offset from several visual speech cues when the mouth is hidden (handheld mic).
import sys, subprocess, numpy as np, mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions
vid, wav, model = sys.argv[1:4]
W, H = 540, 960
raw = subprocess.run(["ffmpeg","-v","error","-i",vid,"-vf",f"fps=30,scale={W}:{H}","-f","rawvideo","-pix_fmt","rgb24","-"],capture_output=True).stdout
fr = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)
lm = vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(base_options=BaseOptions(model_asset_path=model)))
jaw, mo, mot = [], [], []
prev = None
for f in fr:
    g = f.mean(2)
    mot.append(0 if prev is None else np.abs(g - prev).mean()); prev = g
    r = lm.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(f)))
    if not r.face_landmarks: jaw.append(np.nan); mo.append(np.nan); continue
    p = r.face_landmarks[0]
    jaw.append((p[152].y - p[1].y) / (p[1].y - p[10].y)); mo.append(abs(p[14].y - p[13].y) / abs(p[291].x - p[61].x))
a = np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i",wav,"-ac","1","-ar","16000","-f","s16le","-"],capture_output=True).stdout, np.int16).astype(float)
hop = 16000 // 30
e = np.log(np.array([np.sqrt(np.mean(a[i*hop:(i+1)*hop]**2)+1) for i in range(len(a)//hop)]))
sp = (e > np.percentile(e, 40)).astype(float)
k = np.ones(9) / 9
def curve(x, ref, diff):
    x = np.nan_to_num(np.array(x) - np.nanmean(x))
    if diff: x = np.convolve(np.abs(np.diff(x, prepend=x[0])), k, "same")
    r = np.convolve(ref, k, "same") if diff else ref - ref.mean()
    out = []
    for lag in range(-30, 46):
        idx = np.arange(len(x)) - lag; ok = (idx >= 0) & (idx < len(r))
        out.append((round(np.corrcoef(x[ok], r[idx[ok]])[0, 1], 3), lag))
    return out
for name, x, ref, diff in [("jaw-open vs level", jaw, e, False), ("jaw-motion vs speech", jaw, sp, True),
                           ("mouth-motion vs speech", mo, sp, True), ("frame-motion vs speech", mot, sp, True)]:
    c = curve(x, ref, diff); b = max(c)
    print(f"{name:24s} best lag {b[1]:+d} frames (corr {b[0]})  " + " ".join(f"{l}:{v}" for v, l in c if l % 3 == 0))
