"""From the cleaned, cut voice note: shot/card timings, captions, one card clip per shot, a preview.

Usage: python3 voice_kit.py <voice_dir> <cards_dir> <out_dir>
voice_dir: voice_cut.wav + aligned_cut.json (words aligned on the cut). cards_dir: c03_0.png ... (2x renders).
"""
import json, os, subprocess, sys, wave

V, C, O = sys.argv[1:4]
os.makedirs(f"{O}/clips", exist_ok=True)
FPS = 30
W = json.load(open(f"{V}/aligned_cut.json"))
with wave.open(f"{V}/voice_cut.wav") as w: DUR = w.getnframes() / w.getframerate()
NF = round(DUR * FPS)

# shot: (first word, card id or None for the avatar, {state: word})
SHOTS = [(0, None, {}), (16, None, {}),
         (28, "c03", {1: 35, 2: 36, 3: 41, 4: 43, 5: 46}),
         (55, "c04", {1: 59, 2: 60, 3: 62}),
         (63, "c05", {1: 64, 2: 77, 3: 80, 4: 88}),
         (96, "c06", {1: 103, 2: 106, 3: 107, 4: 114, 5: 118}),
         (126, "c07", {1: 137}),
         (144, "c08", {1: 148, 2: 153, 3: 157}),
         (164, "c09", {1: 170, 2: 171, 3: 176, 4: 178, 5: 180}),
         (183, "c10", {1: 187, 2: 192, 3: 195, 4: 200, 5: 206}),
         (218, None, {})]
NAMES = {"c03": ["start", "ghabrahat", "chinta", "bachna", "sharir", "isiliye"], "c04": ["teen-type", "phobic", "panic", "generalised"],
         "c05": ["phobia", "khaas-cheez", "flight", "bheed", "injection"], "c06": ["panic-disorder", "seene", "dhadkan", "jhunjhuni", "heart-attack", "wajah"],
         "c07": ["exam-tip", "wahi-symptoms"], "c08": ["generalised", "har-baat", "control", "muscle"],
         "c09": ["medical-cause", "thyroid", "arrhythmia", "sugar", "phaeo", "withdrawal"], "c10": ["ilaaj", "samjhao", "cbt", "exposure", "antidepressant", "benzo"]}
fr = lambda t: round(t * FPS)
def cut_before(i):  # shot change in the pause before word i
    return fr((W[i - 1]["e"] + W[i]["s"]) / 2) if i else 0
starts = [cut_before(s[0]) for s in SHOTS] + [NF]
assert all(a < b for a, b in zip(starts, starts[1:])), starts

def tc(f): s = f // FPS; return f"{s // 60:02d}:{s % 60:02d}.{round(f % FPS / FPS * 100):02d}"
def tcf(f): s = f // FPS; return f"00:{s // 60:02d}:{s % 60:02d}:{f % FPS:02d}"

timeline, clip_cmds = [], []
for n, (w0, card, states) in enumerate(SHOTS):
    a, b = starts[n], starts[n + 1]
    if card is None:
        timeline.append({"shot": n + 1, "what": "AVATAR (HeyGen)", "in": a, "out": b}); continue
    st = [(0, a)] + [(k, max(fr(W[i]["s"]) - 2, a)) for k, i in sorted(states.items())]
    for j, (k, f) in enumerate(st):
        end = st[j + 1][1] if j + 1 < len(st) else b
        timeline.append({"shot": n + 1, "what": f"S{card[1:]}_{k}_{NAMES[card][k]}.png", "in": f, "out": end})
    # one clip per card shot: states fade in at their word, slow push 1.00 -> 1.03
    d = (b - a) / FPS
    ins, fc, last = [], "", "[0:v]"
    for j, (k, f) in enumerate(st):
        ins += ["-loop", "1", "-framerate", str(FPS), "-t", f"{d:.4f}", "-i", f"{C}/{card}_{k}.png"]
        if j:
            t = (f - a) / FPS
            fc += f"[{j}:v]format=rgba,fade=in:st={t:.3f}:d=0.18:alpha=1[s{j}];{last}[s{j}]overlay=0:0[b{j}];"; last = f"[b{j}]"
    fc += (f"{last}scale=w='trunc(1080*(1+0.03*t/{d:.3f})/2)*2':h='trunc(1920*(1+0.03*t/{d:.3f})/2)*2':eval=frame,"
           f"crop=1080:1920,setsar=1,format=yuv420p[v]")
    clip = f"{O}/clips/S{card[1:]}_{NAMES[card][0]}_{tc(a).replace(':', 'm').replace('.', 's')}.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", fc, "-map", "[v]", "-frames:v", str(b - a),
                    "-r", str(FPS), "-c:v", "libx264", "-preset", "medium", "-crf", "16", clip], check=True)
    clip_cmds.append((n + 1, os.path.basename(clip), a, b))

# ---- captions (Roman Hinglish, as spoken; "" merges into the previous word)
ROMAN = ("Dil|tez|dhadak|raha|hai,|seene|mein|dard,|haath|kaanp|raha|hai,|heart attack?|Ya|panic|attack?|"
 "Main||Dr.|Mayurakshi.|Chaliye,|90|second|mein|anxiety|disorders|samajhte|hain.|"
 "Anxiety|disorder|mein|chaar|cheezein|hoti|hain:|ghabrahat,|chinta|wale|vichaar,|cheezon|se|bachna,|aur|sharir|ke|symptoms.|"
 "Isiliye|mareez|aksar|pehle|physician|ke|paas|aata|hai.|"
 "Teen|type|yaad|rakho:|phobic,|panic|aur|generalised.|"
 "Phobia:|kisi|khaas|cheez|ya|jagah|ka|bahut|zyada|darr,|aur|usse|bachna.|Jaise|flight|ka|darr.|"
 "Bheed|mein|akele|bahar|jaane|ka|darr:|agoraphobia.|Injection|ka|darr|bhi|phobia|ho|sakta|hai.|"
 "Panic|disorder:|achanak,|baar|baar|tez|ghabrahat.|Seene|mein|dard,|dhadkan,|hothon|aur|ungliyon|mein|jhunjhuni.|"
 "Mareez|ko|lagta|heart|attack|hai.|Wajah:|zyada|tez|saans|lena,|yaani|hyperventilation.||"
 "Exam|tip:|mareez|ek|se|do|minute|tez|saans|le,|aur|wahi|symptoms|aa|jaayein,|to|panic|confirm.|"
 "Generalised|anxiety:|har|waqt,|har|baat|ki|chinta,|jo|control|mein|nahi|aati.|Muscle|tension|se|alag|alag|body|complaints.|"
 "Par|pehle|medical|cause|check|karo:|thyroid,|dil|ki|dhadkan|ki|gadbad,|sugar|low,|phaeochromocytoma,|aur|alcohol ya|benzodiazepine|withdrawal.|"
 "Ilaaj|mein|sabse|pehle|samjhao|aur|bharosa|do.|Phir|CBT,|relaxation,|aur|phobia|mein|dheere|dheere|exposure.|"
 "Dawa|mein|antidepressant||first|choice.|Benzodiazepine||sirf|thode|time|ke|liye,|kyunki|aadat|lag|jaati|hai.|"
 "OCD|aur|PTSD|agle|reel|mein.|Save|karo|aur|apne|batchmate|ko|share|karo.").split("|")
assert len(ROMAN) == len(W), (len(ROMAN), len(W))
NOCAP = range(55, 63)  # shot 4, the word-only "3 TYPES" card
words = []
for i, tok in enumerate(ROMAN):
    if not tok: words[-1]["e"] = W[i]["e"]; continue
    if i in NOCAP: continue
    words.append({"t": tok, "s": W[i]["s"], "e": W[i]["e"]})
chunks, cur = [], []
for k, w in enumerate(words):
    cur.append(w)
    gap = words[k + 1]["s"] - w["e"] if k + 1 < len(words) else 9
    ends_next = k + 1 < len(words) and words[k + 1]["t"][-1] in ".,?:"  # don't strand a phrase's last word alone
    if (len(cur) >= 4 and not (len(cur) == 4 and ends_next)) or w["t"][-1] in ".,?:" or gap > 0.35: chunks.append(cur); cur = []
if cur: chunks.append(cur)
srt = lambda t: f"{int(t // 3600):02d}:{int(t % 3600 // 60):02d}:{int(t % 60):02d},{int(round(t % 1 * 1000)) % 1000:03d}"
with open(f"{O}/Captions_Hinglish.srt", "w") as fh:
    for k, c in enumerate(chunks):
        end = min(c[-1]["e"] + 0.25, chunks[k + 1][0]["s"] - 0.06) if k + 1 < len(chunks) else c[-1]["e"] + 0.25
        fh.write(f"{k + 1}\n{srt(max(c[0]['s'] - 0.05, 0))} --> {srt(end)}\n{' '.join(x['t'] for x in c)}\n\n")
# word-highlight .ass for the preview
ass = ["[Script Info]", "ScriptType: v4.00+", "PlayResX: 1080", "PlayResY: 1920", "WrapStyle: 2", "", "[V4+ Styles]",
       "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
       "Style: C,Inter Display,72,&H00FFFFFF,&H00FFFFFF,&H00110C0A,&H96000000,-1,0,0,0,100,100,0,0,1,6,3,5,60,60,0,1", "", "[Events]",
       "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
ts = lambda t: f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{max(t, 0) % 60:05.2f}"
for ci, c in enumerate(chunks):
    end = min(c[-1]["e"] + 0.25, chunks[ci + 1][0]["s"] - 0.06) if ci + 1 < len(chunks) else c[-1]["e"] + 0.25
    for j, w in enumerate(c):
        e = c[j + 1]["s"] if j + 1 < len(c) else end
        txt = " ".join(("{\\c&H3FD2FF&}" + x["t"] + "{\\c&HFFFFFF&}") if x is w else x["t"] for x in c)
        ass.append(f"Dialogue: 0,{ts(w['s'] - (0.05 if j == 0 else 0))},{ts(e)},C,,0,0,0,,{{\\pos(540,1385)}}{txt}")
open(f"{O}/captions_preview.ass", "w").write("\n".join(ass) + "\n")

json.dump({"fps": FPS, "frames": NF, "shots": starts, "timeline": timeline, "clips": clip_cmds}, open(f"{O}/timeline.json", "w"), indent=1)

# ---- cue sheet
rows = "\n".join(f"| {e['shot']} | {tc(e['in'])} | {tc(e['out'])} | {tcf(e['in'])} | {e['what']} |" for e in timeline)
crow = "\n".join(f"| {s} | {tc(a)} | {tc(b)} | {(b - a) / FPS:.2f} s | clips/{f} |" for s, f, a, b in clip_cmds)
open(f"{O}/CUE_SHEET_exact_times.md", "w").write(f"""# Cue sheet: exact times (for the clean audio `Voice_clean_final.wav`, {tc(NF)} long)

Times are from the start of the video (minutes:seconds.hundredths). The timecode column is HH:MM:SS:FF at 30 fps.
"Out" is where the next item starts. Every card stays until its Out time.

## Easiest: one clip per card shot (pop-ins already animated)
Put each clip in at its In time, full screen; it ends exactly at its Out time.

| Shot | In | Out | Length | File |
|---|---|---|---|---|
{crow}

## Or: image by image
| Shot | In | Out | Timecode in | Show |
|---|---|---|---|---|
{rows}

No captions during shot 4 ({tc(starts[3])}–{tc(starts[4])}).
""")
print("frames", NF, "shots", [tc(s) for s in starts], "clips", len(clip_cmds), "caption lines", len(chunks))
