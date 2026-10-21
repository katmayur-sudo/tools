"""Time map between two cuts of the same picks (after tail/head tweaks).
usage: warp.py old_segments.json new_segments.json warp.json   -> rows [old_a, old_b, new_a, new_b]"""
import json, sys

o, n = json.load(open(sys.argv[1])), json.load(open(sys.argv[2]))
assert len(o) == len(n), "segment lists differ in length; re-pick instead of warping"
W, oo, no = [], 0.0, 0.0
for a, b in zip(o, n):
    W.append([round(oo, 3), round(oo + a[1] - a[0], 3), round(no, 3), round(no + b[1] - b[0], 3)])
    oo += a[1] - a[0]; no += b[1] - b[0]
json.dump(W, open(sys.argv[3], "w"))
print(f"old {oo:.2f}s -> new {no:.2f}s")


def M(t, W=W):
    """old-cut time -> new-cut time (times inside a removed tail clamp to the segment end)"""
    for oa, ob, na, nb in W:
        if t < ob: return min(nb, na + max(0, t - oa))
    return W[-1][3]
