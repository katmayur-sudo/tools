# Second pass on the cut itself: trim every off-camera frame (head pitch > median + 6 deg) that is not inside a word.
import json, numpy as np
FPS = 30
S = json.load(open("segments.json")); G = json.load(open("gaze_aroll.json")); W = json.load(open("aligned_cut.json"))
p = np.array([x.get("pitch", 99) for x in G]); med = np.median(p[p < 99])
d = [x["t"] for x in G if x.get("pitch", 99) > med + 6 or not x["face"]]
runs = []
for t in d:
    if runs and t - runs[-1][1] <= 0.1: runs[-1][1] = t
    else: runs.append([t, t])
words = [(w["s"] - 0.04, w["e"] + 0.03) for w in W]
def minus(iv, holes):
    out = [iv]
    for x, y in holes:
        nxt = []
        for p0, p1 in out:
            if y <= p0 or x >= p1: nxt.append((p0, p1)); continue
            if x > p0: nxt.append((p0, x))
            if y < p1: nxt.append((y, p1))
        out = nxt
    return out
cut_c = [iv for a, b in runs for iv in minus((a, b + 1 / FPS), words) if iv[1] - iv[0] >= 1 / FPS - 1e-6]
# cut time -> sound-file time, per segment
segc, c = [], 0.0
for a, b in S: segc.append((a, b, c)); c += b - a
cut_r = []
for x, y in cut_c:
    for a, b, c0 in segc:
        lo, hi = max(x, c0), min(y, c0 + b - a)
        if hi > lo: cut_r.append((a + lo - c0, a + hi - c0))
new = []
for a, b in S:
    new += [(round(round(p0 * FPS) / FPS, 4), round(round(p1 * FPS) / FPS, 4)) for p0, p1 in minus((a, b), cut_r) if p1 - p0 >= 3 / FPS]
json.dump(new, open("segments_v4.json", "w"))
left = [(round(max(a, x), 2), round(min(b + 1 / FPS, y), 2), w["w"]) for a, b in runs for (x, y), w in zip(words, W)
        if x < b + 1 / FPS and a < y]
print("trimmed", len(cut_c), "bits,", round(sum(y - x for x, y in cut_c), 2), "s; new length", round(sum(b - a for a, b in new), 2))
print("off-camera frames left inside words (cut time):", left)
