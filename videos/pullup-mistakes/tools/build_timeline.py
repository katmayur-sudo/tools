"""Re-cut the original voice-over and build the timeline (cues + word captions) for the refined short.

Usage: python3 build_timeline.py <source.mp4> <out_dir>
Writes <out_dir>/vo.wav (tightened voice) and <out_dir>/timeline.json. The voice is the owner's
original "dr mak" take: lines are reordered/trimmed and pauses over 0.26 s shrink to 0.14 s.
"""
import json
import re
import subprocess
import sys

import numpy as np

SR = 48000
# (src_start, src_end, hinglish caption) - the source take, in the order it is kept
LINES = [
    (0.00, 1.12, "Pull-ups kar rahe?"),
    (4.28, 5.76, "Back mein kuch feel nahi hota?"),
    (6.16, 7.80, "Toh ye 5 galtiyan check karo."),
    (8.18, 11.18, "Pehli galti: shoulders ko kaanon tak *shrug* karna."),
    (11.18, 14.70, "Pull se pehle, shoulder blades ko *neeche* aur *peeche* kheencho."),
    (14.70, 17.52, "Doosri: sirf *arms* se kheenchna."),
    (17.52, 20.48, "Elbows ko neeche, *ribs* ki taraf drive karo."),
    (20.48, 23.20, "Teesri: pair *jhulakar* momentum lena."),
    (23.20, 25.60, "Core *tight*, body bilkul still."),
    (25.60, 27.44, "Chauthi: *half* reps."),
    (27.44, 30.88, "Neeche poora *dead hang*, aur upar *chin* bar ke upar."),
    (30.88, 33.62, "Aur paanchvi: neeche *dhadaam* se gir jaana."),
    (33.62, 36.64, "Teen se paanch second mein, *control* se neeche aao."),
    (36.64, 40.18, "Ise *save* kar lo, aur agle pull day pe ye paanchon check karna."),
    (42.80, 45.38, "Dr Mak Fitness ko *follow* aur subscribe karo."),
]
# scene starts, as source times (first spoken word of each beat)
SCENES = [("hook", 0.0), ("promise", 4.28), ("m1", 8.18), ("f1", 11.18), ("m2", 14.70), ("f2", 17.52),
          ("m3", 20.48), ("f3", 23.20), ("m4", 25.60), ("f4", 27.44), ("m5", 30.88), ("f5", 33.62),
          ("recap", 36.64), ("cta", 42.80)]


def pauses(src):
    log = subprocess.run(["ffmpeg", "-nostdin", "-i", src, "-af", "silencedetect=n=-35dB:d=0.22", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    v = [float(x) for x in re.findall(r"silence_(?:start|end): ([0-9.]+)", log)]
    return list(zip(v[::2], v[1::2]))


def main():
    src, out = sys.argv[1:3]
    sil = pauses(src)
    blocks = []  # contiguous lines form one block so pauses at line boundaries also shrink
    for a, b, _ in LINES:
        if blocks and abs(blocks[-1][1] - a) < 1e-6:
            blocks[-1][1] = b
        else:
            blocks.append([a, b])
    segs = []
    for a, b in blocks:
        cur = a
        for s, e in sil:
            if s > a and e < b and e - s > 0.26:
                segs.append((cur, s + 0.07))
                cur = e - 0.07
        segs.append((cur, b))

    def m(t):
        acc = 0.0
        for a, b in segs:
            if t <= a:
                return round(acc, 3)
            if t <= b:
                return round(acc + t - a, 3)
            acc += b - a
        return round(acc, 3)

    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32).reshape(-1, 2)
    fade = int(0.008 * SR)
    ramp = np.linspace(0, 1, fade)[:, None]
    parts = []
    for a, b in segs:
        c = x[int(a * SR):int(b * SR)].copy()
        c[:fade] *= ramp
        c[-fade:] *= ramp[::-1]
        parts.append(c)
    vo = np.concatenate(parts)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ac", "2", "-ar", str(SR), "-i", "-", f"{out}/vo.wav"],
                   input=vo.tobytes(), check=True)

    # word captions: spread each line's words over its kept speech by character weight
    words = []
    for a, b, text in LINES:
        spans = [(m(max(s, a)), m(min(e, b))) for s, e in segs if e > a and s < b]
        speech = sum(e - s for s, e in spans)
        toks = text.split()
        weights = [len(w.strip("*")) + 2 for w in toks]
        acc = 0.0
        for w, wt in zip(toks, weights):
            d = speech * wt / sum(weights)
            t0 = spans[0][0] + acc
            words.append({"w": w.strip("*"), "hl": w.startswith("*"), "s": round(t0, 3), "e": round(t0 + d, 3)})
            acc += d
    cues = {name: m(t) for name, t in SCENES}
    # extra animation cues (source word times from the transcript)
    for name, t in [("lats0", 4.92), ("five", 6.50), ("neeche", 13.42), ("peeche", 14.18), ("arms", 16.50),
                    ("drive", 19.82), ("swing", 21.88), ("still", 25.26), ("deadhang", 28.58), ("chin", 29.88),
                    ("dhadaam", 32.66), ("teen", 33.62), ("paanch", 34.30), ("control", 35.32), ("save", 36.98),
                    ("check", 39.52), ("follow", 43.96)]:
        cues[name] = m(t)
    dur = round(len(vo) / SR, 3)
    json.dump({"dur": dur, "cues": cues, "words": words, "lines": [m(a) for a, _, _ in LINES]},
              open(f"{out}/timeline.json", "w"), indent=1)
    print(f"vo {dur} s, {len(words)} caption words, {len(segs)} segments")


if __name__ == "__main__":
    main()
