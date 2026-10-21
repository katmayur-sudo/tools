"""Word-synced captions for the A/B layout modes -> captions.js (CAPS, MODES, END, WARP).
usage: captions.py captions.json
captions.json: {"words": "cut/words_cut.json", "out": "project/assets/captions.js",
  "modes": [[0,"C"],[5.02,"A"],[12.8,"B"], ...],        # A talk+graphic, B graphic only, C full face (cover text in HTML)
  "fix": {"techs": "text", "claw": "Claude"},            # transcription slips -> script words
  "merge": [["hyper","frames","HyperFrames"]],           # two tokens -> one
  "phrases": {"code": 2, "real": 2},                     # keep N words together starting at this word
  "need": {"video": "models"},                           # phrase only when followed by this word
  "blue": ["frame","SVG","beat"],                        # B-mode keywords in blue
  "nocap": [[10.9, 12.6]],                               # typeset B-roll beats with no caption
  "warp": "warp.json" (optional: modes/nocap authored on an older cut)}"""
import json, re, sys

C = json.load(open(sys.argv[1]))
w = json.load(open(C["words"]))
WARP = json.load(open(C["warp"])) if C.get("warp") else None


def M(t):
    if not WARP: return t
    for oa, ob, na, nb in WARP:
        if t < ob: return round(min(nb, na + max(0, t - oa)), 3)
    return WARP[-1][3]


END = round(w[-1]["e"] + 0.2, 3) if "end" not in C else C["end"]
MODES = [(M(t), m) for t, m in C["modes"]]
NOCAP = [(M(a), M(b)) for a, b in C.get("nocap", [])]
FIX, PHRASE, NEED, BLUE = C.get("fix", {}), C.get("phrases", {}), C.get("need", {}), set(C.get("blue", []))
MERGE = {(a.lower(), b.lower()): out for a, b, out in C.get("merge", [])}
SMALL = {"a", "the", "i", "to", "of", "it", "my", "is", "and", "by", "for", "on", "so", "can", "that", "this", "into",
         "with", "just", "its", "you", "your", "an", "are", "as", "in", "which", "it's", "no", "see", "plus", "but"}

toks, i = [], 0
while i < len(w):
    t, s, e = w[i]["w"], w[i]["s"], w[i]["e"]
    if i + 1 < len(w):
        key = (re.sub(r"[.,!?]+$", "", t).lower(), re.sub(r"[.,!?]+$", "", w[i + 1]["w"]).lower())
        if key in MERGE:
            t, e = MERGE[key], w[i + 1]["e"]; i += 1
    i += 1
    t = re.sub(r"[.,!?]+$", "", t)
    toks.append({"w": FIX.get(t, t), "s": s, "e": e})


def mode_at(t):
    m = "A"
    for a, x in MODES:
        if t >= a - 1e-6: m = x
    return m


def phrase(k):
    t = toks[k]["w"]; n = PHRASE.get(t, 0)
    if n and t in NEED and (k + 1 >= len(toks) or toks[k + 1]["w"] != NEED[t]): n = 0
    return n


caps, i = [], 0
while i < len(toks):
    m = mode_at(toks[i]["s"]); n = phrase(i)
    if not n:
        n = 1
        if toks[i]["w"].lower() in SMALL and i + 1 < len(toks) and toks[i + 1]["s"] - toks[i]["e"] < 0.35 and not phrase(i + 1):
            n = 2
    grp = toks[i:i + n]
    if any(mode_at(g["s"]) != m for g in grp): grp = grp[:1]; n = 1
    caps.append({"t": grp[0]["s"], "le": grp[-1]["e"], "words": [[g["w"], g["s"]] for g in grp], "m": m,
                 "blue": m == "B" and any(g["w"] in BLUE for g in grp)})
    i += n
for k, c in enumerate(caps):
    nxt = caps[k + 1]["t"] if k + 1 < len(caps) else END
    sw = [a for a, _ in MODES if c["t"] < a <= nxt]
    c["e"] = round(min([nxt, c["le"] + 0.8] + sw), 2); del c["le"]
caps = [c for c in caps if c["m"] != "C" and not any(a <= c["t"] < b for a, b in NOCAP)]
open(C["out"], "w").write("window.CAPS=" + json.dumps(caps) + ";\nwindow.MODES=" + json.dumps(MODES) +
                          ";\nwindow.END=" + str(END) + ";\nwindow.WARP=" + json.dumps(WARP or [[0, END, 0, END]]) + ";\n")
for c in caps:
    print(c["m"], f'{c["t"]:6.2f}-{c["e"]:6.2f}', "*" if c["blue"] else " ", " ".join(x[0] for x in c["words"]))
