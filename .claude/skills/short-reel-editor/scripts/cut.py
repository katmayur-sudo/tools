"""Cut raw footage to the script from aligned word picks; tighten pauses; trim take edges by gaze.
usage: cut.py cut.json
cut.json: {"source": "raw.MOV", "words": "aligned.json", "gaze": "gaze15.json" (optional), "out": "cut/",
           "picks": [[first_word, last_word], [first, last, forced_start_sec], ...],   # script order
           "tail": {"<last_word_index>": 0.05},   # per-take tail overrides (user-flagged slow cuts)
           "pre": 0.07, "post": 0.10, "maxgap": 0.26, "keep": 0.08, "fps": 30, "down_pitch": 11}
writes out/cut.mp4, segments.json [[src_a, src_b, first, last]], words_cut.json, lookdown.json"""
import json, os, subprocess, sys
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))  # -I mode skips the script dir
from common import FF

C = json.load(open(sys.argv[1]))
w = json.load(open(C["words"]))
g = json.load(open(C["gaze"])) if C.get("gaze") else []
OUT = C.get("out", "cut"); os.makedirs(OUT, exist_ok=True)
PRE, POST, MAXGAP, KEEP = C.get("pre", .07), C.get("post", .10), C.get("maxgap", .26), C.get("keep", .08)
FPS, PITCH = C.get("fps", 30), C.get("down_pitch", 11)
TAIL = {int(k): v for k, v in C.get("tail", {}).items()}

segs = []  # (lo, hi, run_first, run_last, take_first, take_last)
for a, b, *force in C["picks"]:
    lo = w[a]["s"] - PRE
    if a > 0: lo = max(lo, w[a - 1]["e"] + 0.03)
    if force: lo = force[0]
    run = a
    for i in range(a, b):
        if w[i + 1]["s"] - w[i]["e"] > MAXGAP:      # split long internal pauses
            segs.append((lo, w[i]["e"] + KEEP, run, i, a, b)); lo = w[i + 1]["s"] - KEEP; run = i + 1
    hi = w[b]["e"] + POST
    if b + 1 < len(w): hi = min(hi, w[b + 1]["s"] - 0.03)
    segs.append((lo, hi, run, b, a, b))


def down(x): return (not x["face"]) or x["pitch"] > PITCH
def mostly_down(a, b):
    xs = [x for x in g if w[a]["s"] <= x["t"] <= w[b]["e"]]
    return sum(map(down, xs)) > 0.3 * max(len(xs), 1)

# take edges only: end before the head drops, start once it is up; never inside a take, never on look-down takes
trimmed = []
for lo, hi, p, q, a, b in segs:
    if g and not mostly_down(a, b):
        if q == b:
            drop = [x["t"] for x in g if w[q]["s"] <= x["t"] <= hi and down(x)]
            if drop: hi = max(w[q]["e"] + 0.02, drop[0] - 0.07)
        if p == a:
            up = [x["t"] for x in g if lo <= x["t"] <= w[p]["e"] and down(x)]
            if up: lo = min(w[p]["s"] - 0.02, up[-1] + 0.07)
    if q == b and q in TAIL: hi = w[q]["e"] + TAIL[q]
    trimmed.append((lo, hi, p, q))
# whole frames, so concat never pads audio and the word map never drifts
segs = [(round(x, 3), round(x + round((y - x) * FPS) / FPS, 3), p, q) for x, y, p, q in trimmed]

ins, fc = [], []
for i, (a, b, _, _) in enumerate(segs):
    d = b - a
    ins += ["-ss", f"{a:.3f}", "-t", f"{d + 0.1:.3f}", "-i", C["source"]]   # per-segment seek: ~5x faster than trim
    fc.append(f"[{i}:v]trim=0:{d:.3f},setpts=PTS-STARTPTS,fps={FPS}[v{i}];")
    fc.append(f"[{i}:a]atrim=0:{d:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.012,afade=t=out:st={d - 0.012:.3f}:d=0.012[a{i}];")
n = len(segs)
fc.append("".join(f"[v{i}][a{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=1[vo][ao]")
subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-y", *ins, "-filter_complex", "".join(fc),
                "-map", "[vo]", "-map", "[ao]", "-c:v", "libx264", "-crf", "17", "-preset", "fast", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", f"{OUT}/cut.mp4"], check=True)

cw, off, look = [], 0.0, []
for a, b, p, q in segs:
    for i in range(p, q + 1):
        cw.append({"w": w[i]["w"], "s": round(off + w[i]["s"] - a, 3), "e": round(off + w[i]["e"] - a, 3), "src": w[i]["s"]})
    for x in g:
        if a <= x["t"] < b:
            look.append((round(off + x["t"] - a, 2), (not x["face"]) or x["pitch"] > 15))
    off += b - a
json.dump(segs, open(f"{OUT}/segments.json", "w"))
json.dump(cw, open(f"{OUT}/words_cut.json", "w"), indent=0)
rng = []
for t, d in look:                 # merge, bridge gaps < 0.6s, drop blips < 0.4s
    if d:
        if rng and t - rng[-1][1] < 0.6: rng[-1][1] = t + 0.2
        else: rng.append([t, t + 0.2])
rng = [r for r in rng if r[1] - r[0] >= 0.4]
json.dump(rng, open(f"{OUT}/lookdown.json", "w"))
print(n, "segments; cut", round(off, 2), "s")
for a, b in rng:
    print(f"  look-down {a:6.2f}-{b:6.2f}  " + " ".join(x["w"] for x in cw if x["e"] > a and x["s"] < b))
