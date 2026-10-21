"""Forced-align whisper words over a long recording in pause-bounded chunks (torchaudio MMS_FA).
usage: align.py <16k mono wav> <words.json> <out aligned.json>
Output keeps whisper's tokens; s/e become aligned times, ws = whisper start, sc = alignment score."""
import json, re, sys, wave
import numpy as np, torch, torchaudio

NUM = {"0": "zero", "1": "one", "2": "two", "3": "three", "4": "four", "5": "five", "6": "six", "7": "seven", "8": "eight", "9": "nine"}


def spoken(tok):
    t = tok.lower().strip()
    if re.fullmatch(r"\.\d+[.,]?", t):            # ".5" -> "point five"
        return ["point"] + [NUM[c] for c in re.sub(r"\D", "", t)]
    out = []
    for part in re.split(r"[\s\-]+", t):
        part = re.sub(r"[^a-z0-9']", "", part)
        if not part:
            continue
        out += [NUM[c] for c in part] if part.isdigit() else [part.replace("'", "")]
    return out


WAV, WORDS, OUT = sys.argv[1:4]
words = json.load(open(WORDS))
wf = wave.open(WAV); SR = 16000
audio = np.frombuffer(wf.readframes(wf.getnframes()), np.int16).astype(np.float32) / 32768
bundle = torchaudio.pipelines.MMS_FA
model = bundle.get_model(with_star=False); tok, aligner = bundle.get_tokenizer(), bundle.get_aligner()

# chunk at gaps > 1.0s once a chunk is > 20s long
groups, cur = [], [0]
for i in range(1, len(words)):
    if words[i]["s"] - words[i - 1]["e"] > 1.0 and words[i - 1]["e"] - words[cur[0]]["s"] > 20:
        groups.append(cur); cur = []
    cur.append(i)
groups.append(cur)
res = [dict(w) for w in words]
for gi, g in enumerate(groups):
    lo = words[g[0]]["s"] - 0.6 if gi == 0 else (words[groups[gi - 1][-1]]["e"] + words[g[0]]["s"]) / 2
    hi = words[g[-1]]["e"] + 0.8 if gi == len(groups) - 1 else (words[g[-1]]["e"] + words[groups[gi + 1][0]]["s"]) / 2
    lo = max(lo, 0); hi = min(hi, len(audio) / SR)
    seg = torch.from_numpy(audio[int(lo * SR):int(hi * SR)]).unsqueeze(0)
    flat, owner = [], []
    for i in g:
        for sw in spoken(words[i]["w"]):
            flat.append(sw); owner.append(i)
    if not flat:
        continue
    with torch.inference_mode():
        em, _ = model(seg)
    spans = aligner(em[0], tok(flat))
    ratio = seg.size(1) / em.size(1) / SR
    st, en, sc = {}, {}, {}
    for k, sp in enumerate(spans):
        i = owner[k]
        st.setdefault(i, lo + sp[0].start * ratio); en[i] = lo + sp[-1].end * ratio
        sc.setdefault(i, []).append(float(np.mean([s.score for s in sp])))
    for i in g:
        res[i].update(ws=words[i]["s"], s=round(st.get(i, words[i]["s"]), 3), e=round(en.get(i, words[i]["e"]), 3),
                      sc=round(float(np.mean(sc.get(i, [0]))), 2))
    print(f"chunk {gi}: {lo:7.2f}-{hi:7.2f}  {len(g)} words")
json.dump(res, open(OUT, "w"), indent=0)
for i, w in enumerate(res):
    print(f"{i:4d} {w['s']:8.2f} {w['w']}")
