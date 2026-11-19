"""Compose the mood-disorders reel from the graded cut, card PNGs and word timings.

Usage: python3 compose.py <scratch>   (expects raw1/graded.mp4, raw1/words_cut_v2.json,
raw1/segments_v2.json, reel/cards/*.png, reel/assets/shot4_anhedonia.png, reel/circle_mask.png,
reel/ring.png). Writes <scratch>/out/: shots/*.mp4, silent.mp4, captions.ass, cues.json.
"""
import json, os, subprocess, sys

S = sys.argv[1]
OUT = f"{S}/out"; os.makedirs(f"{OUT}/shots", exist_ok=True)
W = json.load(open(f"{S}/raw1/words_cut_v2.json"))
SEG = json.load(open(f"{S}/raw1/segments_v2.json"))
FPS, DUR = 30, 69.9
CARDS, ASSETS = f"{S}/reel/cards", f"{S}/reel/assets"

# word 108 has no aligned time: interpolate between its neighbours
for i, w in enumerate(W):
    if w["cs"] is None:
        W[i]["cs"] = (W[i - 1]["ce"] + W[i + 1]["cs"]) / 2 - 0.1
        W[i]["ce"] = W[i]["cs"] + 0.2
cs = lambda i: W[i]["cs"]
snap = lambda t: round(t * FPS) / FPS

def boundary(i):  # shot cut sits in the pause before word i
    return snap((W[i - 1]["ce"] + W[i]["cs"]) / 2)

# (type, first word, card id, {state: word}, overlay, overlay-from-word)
SHOTS = [
    ("full", 0, None, {}, "o1", 0),
    ("full", 15, None, {}, "o2", 15),
    ("pip", 26, "s3", {1: 45}, None, None),
    ("card", 57, None, {}, None, None),
    ("pip", 79, "s5", {1: 85, 2: 87, 3: 89, 4: 91}, None, None),
    ("pip", 94, "s6", {1: 98, 2: 99, 3: 101}, None, None),
    ("full", 108, None, {}, "o7", 120),
    ("pip", 125, "s8", {1: 129, 2: 134, 3: 138, 4: 141, 5: 143}, None, None),
    ("pip", 154, "s9", {1: 159, 2: 161, 3: 166, 4: 177}, None, None),
    ("full", 182, None, {}, "o10", 190),
]
starts = [0.0] + [boundary(s[1]) for s in SHOTS[1:]] + [DUR]

# cut-segment boundaries (cumulative durations) for alternating punch-ins
seg_t, t = [], 0.0
for a, b in SEG:
    seg_t.append(t); t += b - a

def zoom_expr(t0, d):
    """1.0/1.07 alternating per cut segment, plus a slow push of +0.04 across the shot."""
    parts = []
    for k, st in enumerate(seg_t):
        en = seg_t[k + 1] if k + 1 < len(seg_t) else DUR + 1
        if en <= t0 or st >= t0 + d: continue
        z = 1.07 if k % 2 else 1.0
        parts.append((max(st - t0, 0), z))
    e = "1.0"
    for st, z in reversed(parts):
        e = f"if(gte(t,{st:.3f}),{z},{e})"
    return f"({e}+0.04*t/{d:.3f})"

def run(args):
    subprocess.run(["ffmpeg", "-v", "error", "-y", *args], check=True)

ENC = ["-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", "-r", str(FPS), "-an"]
cues = {"whoosh": [], "pop": []}
files = []
for n, (kind, w0, card, states, ov, ovw) in enumerate(SHOTS):
    t0, t1 = starts[n], starts[n + 1]; d = t1 - t0
    f = f"{OUT}/shots/{n + 1:02d}.mp4"; files.append(f)
    src = ["-ss", f"{t0:.4f}", "-t", f"{d:.4f}", "-i", f"{S}/raw1/graded.mp4"]
    if n: cues["whoosh"].append(t0)
    if kind == "full":
        z = zoom_expr(t0, d)
        fc = (f"[0:v]scale=w='trunc(1080*{z}/2)*2':h='trunc(1920*{z}/2)*2':eval=frame,"
              f"crop=1080:1920,setsar=1[v]")
        ins = src
        if ov:
            ot = max(cs(ovw) - t0, 0.25)
            ins = src + ["-loop", "1", "-t", f"{d:.4f}", "-i", f"{CARDS}/{ov}_0.png"]
            fc += (f";[1:v]format=rgba,fade=in:st={ot:.3f}:d=0.3:alpha=1[o];"
                   f"[v][o]overlay=0:0[v]")
            cues["pop"].append(t0 + ot)
    elif kind == "card":
        ins = ["-loop", "1", "-t", f"{d:.4f}", "-i", f"{ASSETS}/shot4_anhedonia.png"]
        fc = (f"[0:v]scale=w='trunc(1080*(1+0.04*t/{d:.3f})/2)*2':h='trunc(1920*(1+0.04*t/{d:.3f})/2)*2':eval=frame,"
              f"crop=1080:1920,setsar=1,fade=in:st=0:d=0.6:color=0xF6F3EC[v]")
    else:  # pip: card states stacked, then the face circle
        ins = ["-loop", "1", "-t", f"{d:.4f}", "-i", f"{CARDS}/{card}_0.png"]
        fc, last = "", "[0:v]"
        for k, (st, wi) in enumerate(sorted(states.items())):
            ins += ["-loop", "1", "-t", f"{d:.4f}", "-i", f"{CARDS}/{card}_{st}.png"]
            at = max(cs(wi) - t0 - 0.05, 0)
            cues["pop" if card != "s8" or st < 5 else "whoosh"].append(t0 + at)
            fc += f"[{k + 1}:v]format=rgba,fade=in:st={at:.3f}:d=0.18:alpha=1[s{k}];{last}[s{k}]overlay=0:0[b{k}];"
            last = f"[b{k}]"
        m = len(states) + 1
        ins += src + ["-i", f"{S}/reel/circle_mask.png", "-i", f"{S}/reel/ring.png"]
        fc += (f"{last}scale=w='trunc(1080*(1+0.03*t/{d:.3f})/2)*2':h='trunc(1920*(1+0.03*t/{d:.3f})/2)*2':eval=frame,"
               f"crop=1080:1920,setsar=1[bg];"
               f"[{m}:v]crop=760:760:130:170,scale=320:320,format=rgba[f];[{m + 1}:v]format=gray[mk];"
               f"[f][mk]alphamerge[fc];[bg][fc]overlay=730:100[v1];[v1][{m + 2}:v]overlay=720:90[v]")
    run([*ins, "-filter_complex", fc, "-map", "[v]", "-t", f"{d:.4f}", *ENC, f])
    print(f"shot {n + 1} {kind} {t0:.2f}-{t1:.2f}")

with open(f"{OUT}/concat.txt", "w") as fh:
    fh.writelines(f"file '{f}'\n" for f in files)
run(["-f", "concat", "-safe", "0", "-i", f"{OUT}/concat.txt", "-c", "copy", f"{OUT}/silent.mp4"])

# ---- captions: Roman Hinglish, as spoken (one token per aligned word; "" = merged into previous)
ROMAN = ("Aap|udaas|ho ya|depressed?|Bas|ek|sawaal|poochho:|kya|ab|kuch|bhi|achha|lagta|hai?|"
 "Main|Dr.|Mayurakshi.|Chaliye,|90|second|mein|mood|disorders|samajhte|hain.|"
 "Udaasi|kisi|bure|waqt|ka|reaction|hai.|Samajh|mein|aati|hai,|aur|waqt|ke|saath|theek|ho|jaati|hai.|"
 "Depression|zyada|gehra|hota|hai,|lamba|chalta|hai,|aur|ilaaj|maangta|hai.|"
 "Aur|wo|ek|sawaal?|Anhedonia.|Jo|cheezein|pehle|khushi|deti|thi,|ab|kuch|bhi|achha|nahi|lagta.|Ye|sabse|bada|sign|hai.|"
 "Depression|sharir|mein|bhi|dikhta|hai:|bhook|kam,|neend|kharab,|thakaan|aur|sab|kuch|slow.|"
 "Par|pehle|check|karo:|thyroid,|steroids|ya|stroke|bhi|aisa|mood|bana|sakte|hain.|"
 "Agar|mood|bahut|low|hai,|to|suicide|ke|baare|mein|seedha|poochho.|Poochhne|se|risk|nahi|badhta.|"
 "Ab|iska|ulta:|mania.|Bahut|zyada|khushi|ya|irritability,|neend|ki|zaroorat|nahi,|bahut|bolna,|aur|paise|udaana.|"
 "Jab|depression|aur|mania|dono|aayein,|use|bipolar|disorder|kehte|hain.|"
 "Achhi|baat|ye|hai|ki|dawa|aur|therapy|dono|kaam|karti|hain,|aur|saath|mein|sabse|achha.|"
 "Bipolar|mein|sirf|antidepressant||nahi,|mood|stabiliser|bhi|zaroori|hai.|"
 "Poora|mood|disorders|carousel|mere|profile|pe|hai.|Save|karo,|aur|jise|zaroorat|ho,|usse|share|karo.").split("|")
assert len(ROMAN) == len(W), (len(ROMAN), len(W))

words = []
for i, tok in enumerate(ROMAN):
    if not tok: words[-1]["e"] = W[i]["ce"]; continue
    if 57 <= i <= 78: continue  # shot 4 is the word-only ANHEDONIA card: no captions
    words.append({"t": tok, "s": W[i]["cs"], "e": W[i]["ce"]})

chunks, cur = [], []
for k, w in enumerate(words):
    cur.append(w)
    gap = words[k + 1]["s"] - w["e"] if k + 1 < len(words) else 9
    if len(cur) == 4 or w["t"][-1] in ".,?:" or gap > 0.35:
        chunks.append(cur); cur = []
if cur: chunks.append(cur)

def ts(t):
    t = max(t, 0); return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"

ass = ["[Script Info]", "ScriptType: v4.00+", "PlayResX: 1080", "PlayResY: 1920", "WrapStyle: 2", "",
       "[V4+ Styles]",
       "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
       "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
       "Style: C,Inter Display,72,&H00FFFFFF,&H00FFFFFF,&H00110C0A,&H96000000,-1,0,0,0,100,100,0,0,1,6,3,5,60,60,0,1",
       "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
for ci, c in enumerate(chunks):
    end = c[-1]["e"] + 0.25
    if ci + 1 < len(chunks): end = min(end, chunks[ci + 1][0]["s"] - 0.06)
    for j, w in enumerate(c):
        s = w["s"] if j else w["s"] - 0.05
        e = c[j + 1]["s"] if j + 1 < len(c) else end
        txt = " ".join(("{\\c&H3FD2FF&}" + x["t"] + "{\\c&HFFFFFF&}") if x is w else x["t"] for x in c)
        pop = "{\\fscx92\\fscy92\\t(0,90,\\fscx100\\fscy100)}" if j == 0 else ""
        ass.append(f"Dialogue: 0,{ts(s)},{ts(e)},C,,0,0,0,,{{\\pos(540,1385)}}{pop}{txt}")
open(f"{OUT}/captions.ass", "w").write("\n".join(ass) + "\n")
json.dump({**cues, "shots": starts}, open(f"{OUT}/cues.json", "w"), indent=1)
print("chunks", len(chunks), "cues", {k: len(v) for k, v in cues.items()})
