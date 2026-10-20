"""Word-level timings for each voice-over section, aligned back to the script's own words.

Usage: python3 transcribe.py <script.json> <vo_dir> <out.json>
Whisper supplies the timings; the displayed words always come from the script, so captions
never show a mis-heard word. Script words Whisper missed get interpolated times.
"""
import difflib
import json
import re
import subprocess
import sys

import numpy as np
from faster_whisper import WhisperModel


def norm(w):
    return re.sub(r"[^a-z0-9]", "", w.lower())


def load(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "f32le", "-ac", "1",
                          "-ar", "16000", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32)


def align(script_words, heard):
    a = [norm(w) for w in script_words]
    b = [norm(h["w"]) for h in heard]
    times = [None] * len(a)
    for blk in difflib.SequenceMatcher(None, a, b, autojunk=False).get_matching_blocks():
        for k in range(blk.size):
            h = heard[blk.b + k]
            times[blk.a + k] = (h["s"], h["e"])
    # interpolate gaps between known neighbours
    known = [i for i, t in enumerate(times) if t]
    for i, t in enumerate(times):
        if t:
            continue
        prev = max([k for k in known if k < i], default=None)
        nxt = min([k for k in known if k > i], default=None)
        s0 = times[prev][1] if prev is not None else 0.0
        s1 = times[nxt][0] if nxt is not None else (heard[-1]["e"] if heard else s0 + 0.3)
        lo = prev if prev is not None else -1
        hi = nxt if nxt is not None else len(a)
        span = (s1 - s0) / (hi - lo)
        times[i] = (s0 + span * (i - lo - 1), s0 + span * (i - lo))
    return [{"w": w, "s": round(t[0], 3), "e": round(t[1], 3)} for w, t in zip(script_words, times)]


def main():
    script, vo_dir, out = sys.argv[1:4]
    model = WhisperModel("base.en", device="cpu", compute_type="int8")
    result = {}
    for sec in json.load(open(script))["sections"]:
        audio = load(f"{vo_dir}/{sec['id']}.mp3")
        segs, _ = model.transcribe(audio, word_timestamps=True)
        heard = [{"w": w.word.strip(), "s": w.start, "e": w.end} for s in segs for w in s.words]
        result[sec["id"]] = align(sec["text"].split(), heard)
        print(sec["id"], len(heard), "heard /", len(result[sec["id"]]), "script words", flush=True)
    json.dump(result, open(out, "w"), indent=1)


if __name__ == "__main__":
    main()
