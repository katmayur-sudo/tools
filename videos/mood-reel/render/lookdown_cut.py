# Remove glance-down frames from the cut without clipping words: cut from the end of the word a glance starts in
# (or from the glance start, in a pause) to the glance end or the next word's start, whichever is first.
import json, numpy as np
FPS, OFF = 30, 4 / 30  # picture leads sound by 4 frames
S = json.load(open("segments.json")); G = json.load(open("gaze.json")); W = json.load(open("aligned_cut.json"))
segc, c = [], 0.0
for a, b in S: segc.append((a, b, c)); c += b - a
def toraw(t):
    for a, b, c0 in segc:
        if c0 <= t < c0 + (b - a) + 1e-6: return a + t - c0
for w in W: w["rs"], w["re"] = toraw(w["s"]), toraw(min(w["e"], c - 1e-3))
p = np.array([x.get("pitch", 99) for x in G]); med = np.median(p[p < 99])
down = [x["t"] - OFF for x in G if x.get("pitch", 99) > med + 11 or not x["face"]]
runs = []
for t in down:
    if runs and t - runs[-1][1] <= 0.2: runs[-1][1] = t
    else: runs.append([t, t])
def minus(iv, holes):  # interval minus a list of intervals
    out = [iv]
    for x, y in holes:
        nxt = []
        for p0, p1 in out:
            if y <= p0 or x >= p1: nxt.append((p0, p1)); continue
            if x > p0: nxt.append((p0, x))
            if y < p1: nxt.append((y, p1))
        out = nxt
    return out
words = [(w["rs"] - 0.04, w["re"] + 0.03) for w in W]
cuts, keep_inside = [], []
for a, b in runs:
    b += 1 / 15
    cuts += [(x, y) for x, y in minus((a, b), words) if y - x >= 2 / FPS]
    keep_inside += [(round(max(a, x), 2), round(min(b, y), 2), w["w"]) for (x, y), w in zip(words, W)
                    if x < b and a < y and min(b, y) - max(a, x) > 0.12]
new = []
for a, b in S:
    pieces = minus((a, b), cuts)
    new += [(round(round(p0 * FPS) / FPS, 4), round(round(p1 * FPS) / FPS, 4)) for p0, p1 in pieces if p1 - p0 >= 3 / FPS]
json.dump(new, open("segments_v3.json", "w"))
print("cuts", len(cuts), "pieces", len(new), "length", round(sum(b - a for a, b in new), 2))
json.dump(keep_inside, open("glance_in_words.json", "w"), ensure_ascii=False)
print("glances during words (sound time, >0.12 s):", keep_inside)
