"""Timeline for the psychiatry short: beat starts, cue times and captions.

Usage: python3 timeline.py script.json timeline.json [voiceover.(wav|mp3|m4a)]
Without audio the words are spaced at the script's wpm (silent first cut).
With audio, Whisper word timings are aligned back to the script's own words, so
captions always show the script spelling (needs: pip install faster-whisper).
"""
import json
import sys

LEAD = 0.4     # silence before the first word
PAUSE = 0.45   # gap between beats when estimating
TAIL = 2.5     # end card after the last word


def estimated(beats, wpm):
    words, t = [], LEAD
    for b in beats:
        for w in b["vo"].split():
            d = 60 / wpm * (1.4 if w[-1] in ".,:?!" else 1)
            words.append({"w": w, "s": round(t, 3), "e": round(t + d, 3)})
            t += d
        t += PAUSE
    return words


def from_audio(beats, path):
    sys.path.insert(0, "../beginner-gym-engine/tools")
    from faster_whisper import WhisperModel
    from transcribe import align, load
    segs, _ = WhisperModel("base.en", device="cpu", compute_type="int8").transcribe(load(path), word_timestamps=True)
    heard = [{"w": w.word.strip(), "s": w.start, "e": w.end} for s in segs for w in s.words]
    return align([w for b in beats for w in b["vo"].split()], heard)


def captions(words):
    out, cur = [], []
    for w in words:
        cur.append(w)
        if len(cur) >= 4 or w["w"][-1] in ".?!:" or (w["w"][-1] == "," and len(cur) >= 2):
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    out = [{"s": c[0]["s"], "e": c[-1]["e"], "words": [[x["w"], x["s"]] for x in c]} for c in out]
    for a, b in zip(out, out[1:]):  # hold each chunk until the next starts (max +0.5 s)
        a["e"] = round(min(b["s"], a["e"] + 0.5), 3)
    return out


def main():
    script_path, out_path = sys.argv[1:3]
    sc = json.load(open(script_path))
    beats = sc["beats"]
    words = from_audio(beats, sys.argv[3]) if len(sys.argv) > 3 else estimated(beats, sc["wpm"])
    i, tl = 0, []
    for b in beats:
        bw = words[i:i + len(b["vo"].split())]
        i += len(bw)
        cues = {}
        for k, word in b.get("cues", {}).items():
            hit = next(w for w in bw if w["w"] == word)  # every cue word must be in its beat's vo
            cues[k] = hit["s"]
        tl.append({**{k: v for k, v in b.items() if k not in ("vo", "cues")}, "start": bw[0]["s"], "cues": cues})
    for a, b in zip(tl, tl[1:]):  # cut a little before the next beat's first word
        b["start"] = round(b["start"] - 0.15, 3)
        a["end"] = b["start"]
    tl[0]["start"] = 0.0
    tl[-1]["end"] = round(words[-1]["e"] + TAIL, 3)
    json.dump({"title": sc["title"], "end": tl[-1]["end"], "beats": tl, "captions": captions(words)},
              open(out_path, "w"), indent=1)
    print(f"{len(words)} words, {tl[-1]['end']:.1f} s, {'audio' if len(sys.argv) > 3 else 'estimated'} timing")


if __name__ == "__main__":
    main()
