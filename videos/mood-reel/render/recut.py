"""Frame-exact recut: voice, picture and word times all from the same 1/30 s segment boundaries.

Usage: python3 recut.py <scratch>
Reads raw1/raw.mp4, raw1/voice_clean.wav, raw1/segments_v2.json, raw1/words_cut_v2.json,
raw1/grade_v2.txt, raw1/look.png. Writes raw1/voice_cut.wav, raw1/words_cut_v3.json, raw1/graded4k.mp4.
"""
import json, subprocess, sys, wave
import numpy as np

S = sys.argv[1] + "/raw1"
FPS, SR = 30, 48000
# The phone file's picture runs 0.53 s ahead of its sound: measured by correlating mouth movement with
# speech over the whole take: 16 frames (0.53 s) by mouth opening vs voice level, ~0.6 s by speech activity,
# steady across 20 s windows; a test cut at 18 frames left a -2 frame residual. The file's own edit list
# claims 1.096 s, which the lips contradict.
OFF_FRAMES = 16
seg = [(round(a * FPS), round(b * FPS)) for a, b in json.load(open(f"{S}/segments_v2.json"))]

# ---- voice: exact sample slices, 10 ms fades at every join
with wave.open(f"{S}/voice_clean.wav") as w:
    assert w.getframerate() == SR and w.getnchannels() == 1
    v = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32)
spf, fade = SR // FPS, int(0.01 * SR)
parts = []
for A, B in seg:
    p = v[A * spf:B * spf].copy()
    p[:fade] *= np.linspace(0, 1, fade); p[-fade:] *= np.linspace(1, 0, fade)
    parts.append(p)
cut = np.concatenate(parts)
assert len(cut) == sum(B - A for A, B in seg) * spf
with wave.open(f"{S}/voice_cut.wav", "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(np.clip(cut, -32768, 32767).astype("<i2").tobytes())

# ---- word times in the new cut (s/e are raw sound-file times)
W = json.load(open(f"{S}/words_cut_v2.json"))
def to_cut(t):
    c = 0.0
    for A, B in seg:
        a, b = A / FPS, B / FPS
        if a - 0.03 <= t <= b + 0.03: return round(c + min(max(t - a, 0), b - a), 3)
        c += b - a
    return None
for w_ in W:
    w_["cs"], w_["ce"] = to_cut(w_["s"]), to_cut(w_["e"])
json.dump(W, open(f"{S}/words_cut_v3.json", "w"), ensure_ascii=False)
print("words without a time:", [i for i, w_ in enumerate(W) if w_["cs"] is None])

# ---- picture: same frames shifted by the measured offset, cinematic grade, 4K upscale
sel = "+".join(f"between(n,{A + OFF_FRAMES},{B + OFF_FRAMES - 1})" for A, B in seg)
grade = open(f"{S}/grade_v2.txt").read().strip()
fc = (f"[0:v]fps={FPS},select='{sel}',setpts=N/{FPS}/TB,{grade}[g];[g][1:v]overlay=0:0,"
      f"scale=2160:3840:flags=lanczos,cas=0.55,format=yuv420p[v]")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{S}/raw.mp4", "-i", f"{S}/look.png",
                "-filter_complex", fc, "-map", "[v]", "-r", str(FPS), "-c:v", "libx264", "-preset", "medium",
                "-crf", "15", f"{S}/graded4k.mp4"], check=True)
n = int(subprocess.run(["ffprobe", "-v", "error", "-count_packets", "-select_streams", "v", "-show_entries",
                        "stream=nb_read_packets", "-of", "csv=p=0", f"{S}/graded4k.mp4"],
                       capture_output=True, text=True).stdout)
assert n == sum(B - A for A, B in seg), (n, sum(B - A for A, B in seg))
print("frames", n, "seconds", n / FPS)
