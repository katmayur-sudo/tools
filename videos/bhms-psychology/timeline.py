"""Timeline for a BHMS psychology reel: beat starts, cue times and captions.

Usage: python3 timeline.py reels/01-….json timeline.json [words.json]
Without words.json (from vo.py) timing is estimated from the words (silent first cut).
Each beat's "cues" are words of its "vo", in order; each one times the next item on screen.
"""
import json
import re
import sys

WPM = 175      # Roman Hinglish (many short words) at a teaching pace
LEAD = 0.4     # silence before the first word
PAUSE = 0.5    # gap between beats
TAIL = 1.5     # hold after the last word
END = ".?!:।"


def estimated(beats):
    words, t = [], LEAD
    for b in beats:
        for w in b["vo"].split():
            d = 60 / WPM * (1.5 if w[-1] in END else 1.25 if w[-1] == "," else 1)
            words.append({"w": w, "s": round(t, 3), "e": round(t + d, 3)})
            t += d
        t += PAUSE
    return words


def bare(w):
    return re.sub(r"[.,:;?!।\"']", "", w).lower()


def cue_times(cues, bw):
    out, i = [], 0
    for c in cues:
        j = next((k for k in range(i, len(bw)) if bw[k]["w"] == c or bare(bw[k]["w"]) == bare(c)), None)
        assert j is not None, f"cue {c!r} not found after word {i} in: {' '.join(w['w'] for w in bw)}"
        out.append(bw[j]["s"])
        i = j + 1
    return out


def captions(words):
    out, cur = [], []
    for w in words:
        cur.append(w)
        if len(cur) >= 4 or w["w"][-1] in END or (w["w"][-1] == "," and len(cur) >= 2):
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    out = [{"s": c[0]["s"], "e": c[-1]["e"], "words": [[x["w"], x["s"]] for x in c]} for c in out]
    for a, b in zip(out, out[1:]):  # hold each chunk until the next starts (max +0.5 s)
        a["e"] = round(min(b["s"], a["e"] + 0.5), 3)
    return out


def main():
    sc = json.load(open(sys.argv[1]))
    beats = sc["beats"]
    words = json.load(open(sys.argv[3])) if len(sys.argv) > 3 else estimated(beats)  # words.json from vo.py
    assert len(words) == sum(len(b["vo"].split()) for b in beats), "words.json is for another script"
    i, tl = 0, []
    for b in beats:
        bw = words[i:i + len(b["vo"].split())]
        i += len(bw)
        fields = {k: v for k, v in b.items() if k not in ("vo", "tts", "cues")}
        tl.append({**fields, "start": bw[0]["s"], "cues": cue_times(b.get("cues", []), bw)})
    for a, b in zip(tl, tl[1:]):  # cut a little before the next beat's first word
        b["start"] = round(b["start"] - 0.15, 3)
        a["end"] = b["start"]
    tl[0]["start"] = 0.0
    tl[-1]["end"] = round(words[-1]["e"] + TAIL, 3)
    meta = {k: sc[k] for k in ("n", "title", "topic", "tag")}
    json.dump({**meta, "end": tl[-1]["end"], "beats": tl, "captions": captions(words)},
              open(sys.argv[2], "w"), ensure_ascii=False, indent=1)
    print(f"{sys.argv[1]}: {len(words)} words, {tl[-1]['end']:.1f} s")


if __name__ == "__main__":
    main()
