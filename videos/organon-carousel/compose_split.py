"""Split-screen case-taking reel: speaker (brand background) on top, self-writing case sheet below,
full-screen aphorism cards with voice only, Roman Hinglish captions on the seam.

Usage: python3 compose_split.py <cut_dir> <work_dir> <cards_9x16_dir> <title_card.png> <brand_bg.png>
cut_dir: aligned_cut.json (words on the cut), voice_cut.wav, gaze_aroll.json.
work_dir: top_raw.mp4 + top_alpha.mp4 (from matte_mediapipe.py), and receives everything else.
Then run the mood-reel audio.py on work_dir (cues.json) and the final ffmpeg step this script prints.
"""
import json, os, subprocess, sys, wave
import numpy as np

CUT, WK, CARDS, TITLE, BG = sys.argv[1:6]
HERE = os.path.dirname(os.path.abspath(__file__))
FPS = 30
W = json.load(open(f"{CUT}/aligned_cut.json"))
with wave.open(f"{CUT}/voice_cut.wav") as w: DUR = w.getnframes() / w.getframerate()
NF = round(DUR * FPS)
ts = lambda i: W[i]["s"]

# ---- steps (first word) and their aphorism; board items (word that triggers the write-on)
STEPS = [(0, None), (16, "83–90"), (36, "83"), (78, "84"), (97, "85"), (135, "86"), (157, "87"), (185, "88"), (195, "89"), (205, "90"), (247, None)]
BOARD = {"q1": 40, "q2": 50, "q3": 59, "q4": 69, "p1": 80, "chup": 85, "words": 93, "line2": 97, "gap": 103,
         "c1": 148, "c2": 150, "c3": 151, "c4": 152, "c5": 154, "x1": 172, "v1": 178, "ticks": 188, "gq": 192, "sq": 199,
         "d1": 228, "d2": 229, "d3": 230, "d4": 231, "d5": 239, "end": 252}
WRITE = 0.5  # seconds a line takes to "write"
step_t = [ts(i) - 0.15 if i else 0.0 for i, _ in STEPS] + [DUR]

# ---- glances still in the cut (head pitch > median + 6 deg)
G = json.load(open(f"{CUT}/gaze_aroll.json"))
p = np.array([x.get("pitch", 99) for x in G]); med = np.median(p[p < 99])
look = np.zeros(NF, bool)
for x in G:
    if x.get("pitch", 99) > med + 6:
        f = round(x["t"] * FPS)
        if f < NF: look[f] = True

# ---- card windows: one per aphorism step, placed to hide as much glancing as possible
cards = []
for k, (i, tag) in enumerate(STEPS):
    if tag is None or "–" in tag: continue
    a, b = step_t[k] + 1.0, step_t[k + 1]
    L = min(3.5, max(b - a - 0.3, 2.0))
    best = max(((look[round(t * FPS):round((t + L) * FPS)].sum(), t) for t in np.arange(a, max(a, b - L) + 1e-6, 1 / FPS)), default=(0, a))
    cards.append((f"{CARDS}/slide_{int(tag) - 82:02d}.png", round(best[1], 3), round(best[1] + L, 3), tag))
# intro: "Organon §83–90" title card over the longest intro glance, if any
a, b = step_t[1], step_t[2]
seg = look[round(a * FPS):round(b * FPS)]
if seg.any():
    idx = np.flatnonzero(seg); t0 = a + idx[0] / FPS; t1 = a + (idx[-1] + 1) / FPS
    cards.append((TITLE, round(max(t0 - 0.3, a), 3), round(min(t1 + 0.3, b), 3), "title"))
cards.sort(key=lambda c: c[1])
covered = sum(look[round(c[1] * FPS):round(c[2] * FPS)].sum() for c in cards) / FPS

# ---- board frames: render only states that change
def state(t):
    tag = next((STEPS[k][1] for k in range(len(STEPS) - 1, -1, -1) if t >= step_t[k] and STEPS[k][1]), None)
    items = {}
    for k, wi in BOARD.items():
        t0 = ts(wi) - 0.05
        if t >= t0: items[k] = round(min((t - t0) / WRITE, 1.0), 2)
    return {"tag": tag, "items": items}
os.makedirs(f"{WK}/board", exist_ok=True)
uniq, seq = [], []
for f in range(NF):
    st = state(f / FPS)
    if not uniq or st != uniq[-1]: uniq.append(st)
    seq.append(len(uniq) - 1)
json.dump(uniq, open(f"{WK}/board_states.json", "w"))
subprocess.run(["node", "-e", f"""
const {{chromium}} = require("playwright"); const fs = require("fs");
const S = JSON.parse(fs.readFileSync("{WK}/board_states.json"));
(async () => {{ const b = await chromium.launch(); const p = await b.newPage({{viewport: {{width: 1080, height: 960}}}});
  await p.goto("file://{WK}/board.html"); await p.evaluate(() => document.fonts.ready);
  for (let i = 0; i < S.length; i++) {{ await p.evaluate(s => window.show(s), S[i]); await p.screenshot({{path: `{WK}/board/b_${{String(i).padStart(4, "0")}}.png`}}); }}
  await b.close(); }})();"""], check=True, cwd=WK)
with open(f"{WK}/board.ffconcat", "w") as fh:
    fh.write("ffconcat version 1.0\n")
    f = 0
    while f < NF:
        g = f
        while g < NF and seq[g] == seq[f]: g += 1
        fh.write(f"file 'board/b_{seq[f]:04d}.png'\nduration {(g - f) / FPS:.6f}\n"); f = g
    fh.write(f"file 'board/b_{seq[-1]:04d}.png'\n")

# ---- captions (Roman Hinglish as spoken; "" merges into the previous word), hidden while a card is up
ROMAN = ("Homoeopath||sirf|kaisa|lag|raha|hai|yeh|nahi|poochta.|Dekho|case|taking|ka|asli|sach.|"
 "Aphorism|83|se 90|tak|Dr.|Hahnemann|ne|apni|Organon|of Medicine|mein|bata|rakha|hai|ki|aap|case|taking|kaise|lenge?|"
 "Doctor|mein|chaar|cheezein:|No|prejudice:|pehle|se|apni|koi|alag|dhaarna|nahi|banani.|Sharp|senses:|ek|ek|baareek|detail|pakadna|aana|chahiye.|"
 "Attention:|saara|dhyaan|patient|aur|patient|ki|baaton|pe.|Aur|sach|likhna:|jo|patient|bole,|actual|mein|wahi|likhna.|"
 "Patient|bole|\"sar|dard|rehta|hai\".|Main|chup.|Physician|ko|chup|rehna|hai,|roko|mat.|Uske|words|mein|likho.|"
 "Har|naya|symptom,|nayi|line|se.|Beech|mein|gap|chhodo,|taaki|jab|aap|wapas|saare|symptoms|patient|ke|saath|go|through|karo,|"
 "to|details|mention|karne|ki|jagah|ho.|Aur|har|symptom|aapko|paper|pe|alag,|individual|dikhe.|"
 "Ab|complete|karo.|Ek|baar|uski|saari|baatein|sunne|ke|baad|complete|karo:|kab|se?|Kaisa?|Kahan?|Kitni|der?|Kab|badhta|hai?|"
 "Leading|questions|aapko|nahi|poochne.|Woh|jaise|bata|raha|hai,|aapko|uski|baatein|sunni|hai.|Jaise|\"dhoop|mein|badhta|hai?\"|Galat.|"
 "\"Kis|cheez|se|badhta|hai?\"|Yeh|sahi.|Jo|nahi|bataya,|general|sawaal|se|poochho:|\"Neend|kaisi|hai?\"|"
 "Picture|poori|ho,|tab|special|sawaal:|\"Neend|mein|bolte|ho?\"|"
 "Aakhir|mein|doctor|khud|dekhega,|khud|observe|karega.|Aphorism|90|mein|Dr.|Hahnemann||ne|bataya|hai:|physician|khud|se|jo|observe|karega:|"
 "chehra,|mood,|zubaan,|pulse,|aur|case|taking|ke|time|patient|ke|behaviour|aur|activities|mein|jo|bhi|notice|karein.|"
 "To|patient|ki|poori|story|plus|doctor|ka|observation:|yahi|hai|asli|case|taking.|Save|karo.").split("|")
assert len(ROMAN) == len(W), (len(ROMAN), len(W))
in_card = lambda t: any(c[1] - 0.05 <= t <= c[2] + 0.05 for c in cards)
words = []
for i, tok in enumerate(ROMAN):
    if not tok: words[-1]["e"] = W[i]["e"]; continue
    words.append({"t": tok, "s": W[i]["s"], "e": W[i]["e"]})
chunks, cur = [], []
for k, w in enumerate(words):
    cur.append(w)
    gap = words[k + 1]["s"] - w["e"] if k + 1 < len(words) else 9
    ends_next = k + 1 < len(words) and words[k + 1]["t"][-1] in ".,?:\""
    if (len(cur) >= 4 and not (len(cur) == 4 and ends_next)) or w["t"][-1] in ".,?:\"" or gap > 0.35: chunks.append(cur); cur = []
if cur: chunks.append(cur)
A = lambda t: f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{max(t, 0) % 60:05.2f}"
ass = ["[Script Info]", "ScriptType: v4.00+", "PlayResX: 1080", "PlayResY: 1920", "WrapStyle: 2", "", "[V4+ Styles]",
       "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
       "Style: C,Inter Display,54,&H00FFFFFF,&H00FFFFFF,&H00110C0A,&H00110C0A,-1,0,0,0,100,100,0,0,3,16,0,5,40,40,0,1", "", "[Events]",
       "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
srt = []
for ci, c in enumerate(chunks):
    end = min(c[-1]["e"] + 0.25, chunks[ci + 1][0]["s"] - 0.04) if ci + 1 < len(chunks) else c[-1]["e"] + 0.25
    srt.append((c[0]["s"], end, " ".join(x["t"] for x in c)))
    for j, w in enumerate(c):
        s0 = w["s"] - (0.05 if j == 0 else 0); e0 = c[j + 1]["s"] if j + 1 < len(c) else end
        if in_card((s0 + e0) / 2): continue
        txt = " ".join(("{\\c&H3FD2FF&}" + x["t"] + "{\\c&HFFFFFF&}") if x is w else x["t"] for x in c)
        ass.append(f"Dialogue: 0,{A(s0)},{A(e0)},C,,0,0,0,,{{\\pos(540,960)}}{txt}")
open(f"{WK}/captions.ass", "w").write("\n".join(ass) + "\n")
S2 = lambda t: f"{int(t // 3600):02d}:{int(t % 3600 // 60):02d}:{int(t % 60):02d},{int(round(t % 1 * 1000)) % 1000:03d}"
open(f"{WK}/captions.srt", "w").write("".join(f"{k + 1}\n{S2(a)} --> {S2(b)}\n{t}\n\n" for k, (a, b, t) in enumerate(srt)))

# ---- sound cues for audio.py: whoosh as each card comes in, soft pop as each board line starts
json.dump({"whoosh": [c[1] for c in cards], "pop": [ts(i) for i in BOARD.values()], "shots": [0, DUR]}, open(f"{WK}/cues.json", "w"))

# ---- final render command (top: speaker over brand background; bottom: board; cards full screen)
ins = ["-i", f"{WK}/top_raw.mp4", "-i", f"{WK}/top_alpha.mp4", "-loop", "1", "-framerate", str(FPS), "-i", BG,
       "-f", "concat", "-safe", "0", "-i", f"{WK}/board.ffconcat"]
fc = ("[2:v]scale=-2:960,crop=1080:960,setsar=1,format=yuv420p[bg];[1:v]format=gray[a];[0:v]format=yuv420p[fg0];"
      "[fg0][a]alphamerge[fg];[bg][fg]overlay=0:0:shortest=1[top];[3:v]fps=30,scale=1080:960,setsar=1,format=yuv420p[bd];"
      "[top][bd]vstack=inputs=2[v0];")
last = "[v0]"
for k, (img, a, b, _) in enumerate(cards):
    n = 4 + k
    ins += ["-loop", "1", "-framerate", str(FPS), "-t", f"{DUR:.3f}", "-i", img]
    fc += (f"[{n}:v]scale=1080:1920,format=rgba,fade=in:st={a:.3f}:d=0.15:alpha=1,fade=out:st={b - 0.15:.3f}:d=0.15:alpha=1[c{k}];"
           f"{last}[c{k}]overlay=0:0:enable='between(t,{a:.3f},{b:.3f})'[v{k + 1}];")
    last = f"[v{k + 1}]"
fc += f"{last}ass={WK}/captions.ass,format=yuv420p[v]"
cmd = ["ffmpeg", "-v", "error", "-y", *ins, "-i", f"{WK}/mix.wav", "-filter_complex", fc, "-map", "[v]", "-map", f"{4 + len(cards)}:a",
       "-frames:v", str(NF), "-r", str(FPS), "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-c:a", "aac", "-b:a", "256k",
       "-movflags", "+faststart", f"{WK}/Case_taking_reel.mp4"]
json.dump(cmd, open(f"{WK}/final_cmd.json", "w"))
json.dump({"cards": cards, "frames": NF, "glance_s": round(look.sum() / FPS, 2), "glance_covered_s": round(covered, 2)}, open(f"{WK}/plan.json", "w"), indent=1)
print("frames", NF, "board states", len(uniq), "cards", [(c[3], c[1], c[2]) for c in cards])
print("glance seconds", round(look.sum() / FPS, 2), "covered by cards", round(covered, 2))
