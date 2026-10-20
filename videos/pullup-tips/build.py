"""Timeline + soundtrack for the "5 Pull-Up Tips" short.

Usage: python3 build.py <vo_dir> <out_dir>
<vo_dir> holds the dr mak voice lines 0_hook.mp3 ... 6_end.mp3 (ElevenLabs, eleven_multilingual_v2).
Writes <out_dir>/timeline.json (scenes, karaoke words) and <out_dir>/mix.wav (voice + soft lo-fi
bed + SFX, -14 LUFS). The bed and SFX are synthesized here, so they are free to publish.
"""
import json
import pathlib
import re
import subprocess
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "videos/beginner-gym-engine/tools"), str(ROOT / ".claude/skills/og-content-generator/engine")]
import make_audio as fx  # noqa: E402
import music as mu  # noqa: E402

SR = 48000
# (file, scene kind, tip number, title, Roman Hinglish caption with *keywords*)
LINES = [
    ("0_hook", "hook", 0, "", "Pull-ups se *back* grow karni hai? Ye *5 tips* follow karo."),
    ("1_deadhang", "deadhang", 1, "DEAD HANG", "Number one... Dead hang. Har rep full *dead hang* se start karo, aur shoulders ko *neeche lock* karo."),
    ("2_grip", "grip", 2, "FULL GRIP", "Two... Grip. Bar ko *poori grip* se pakdo, *thumbs* bar ke around."),
    ("3_core", "core", 3, "CORE TIGHT", "Three... Core. Core *tight*, body bilkul still. *No swing.*"),
    ("4_range", "range", 4, "FULL RANGE", "Four... Range. Neeche full *dead hang*, aur upar *chin* bar ke upar."),
    ("5_tempo", "tempo", 5, "3 SEC DOWN", "Five... Tempo. *Teen second* mein, *control* se neeche aao."),
    ("6_end", "end", 0, "", "Follow karo *Dr Mak Fitness*... save karo, aur agle pull day pe try karna."),
]
LEAD, GAP, TAIL = .15, .35, 1.2


def load(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).astype(np.float64)


def speech_spans(x):
    """Voiced spans (pauses > 0.18 s split them), from a smoothed energy envelope."""
    k = int(.02 * SR)
    e = np.sqrt(np.convolve(x * x, np.ones(k) / k, mode="same"))
    on = e > max(1e-4, e.max() * .06)
    spans, i, n = [], 0, len(x)
    while i < n:
        if on[i]:
            j = i
            while j < n and (on[j] or (j + int(.18 * SR) < n and on[j:j + int(.18 * SR)].any())):
                j += 1
            spans.append((i / SR, j / SR)); i = j
        else:
            i += 1
    return spans or [(0, n / SR)]


def place_words(text, spans, t0, line):
    """Spread caption words over the voiced spans by character weight; '...' marks a span break."""
    chunks = [c.strip() for c in text.split("...") if c.strip()]
    if len(chunks) != len(spans):  # fall back to one stream over all speech
        chunks, spans = [" ".join(chunks)], [(spans[0][0], spans[-1][1])]
    out = []
    for chunk, (a, b) in zip(chunks, spans):
        toks = chunk.split()
        wts = [len(w.strip("*")) + 2 for w in toks]
        acc = 0
        for w, wt in zip(toks, wts):
            d = (b - a) * wt / sum(wts)
            out.append({"w": w.replace("*", ""), "hl": w.startswith("*") or w.endswith("*"), "s": round(t0 + a + acc, 3), "e": round(t0 + a + acc + d, 3), "line": line})
            acc += d
    return out


def merge_spans(spans, n):
    """Reduce voiced spans to n groups by merging across the shortest pauses."""
    spans = list(spans)
    while len(spans) > n:
        gaps = [spans[i + 1][0] - spans[i][1] for i in range(len(spans) - 1)]
        i = int(np.argmin(gaps)); spans[i:i + 2] = [(spans[i][0], spans[i + 1][1])]
    return spans


def bed(dur):
    """Soft lo-fi bed: electric-piano 7th chords, brushed groove, round bass - 88 BPM, minor and warm."""
    n = int(dur * SR); out = np.zeros(n)
    bpm = 88; beat = 60 / bpm
    prog = [[57, 60, 64, 67], [53, 57, 60, 64], [48, 52, 55, 59], [55, 59, 62, 65]]  # Am7 Fmaj7 Cmaj7 G7
    roots = [45, 41, 36, 43]

    def put(x, t, g=1.):
        i = int(t * SR)
        if i < n: out[i:i + len(x)] += x[:n - i] * g

    def epiano(notes, d):
        t = np.arange(int(d * SR)) / SR
        x = sum(np.sin(2 * np.pi * mu.hz(m) * t + .6 * np.sin(2 * np.pi * mu.hz(m) * 2 * t) * np.exp(-t * 3)) for m in notes)
        return x * np.exp(-t * 1.1) * np.minimum(1, t / .01) * (1 + .15 * np.sin(2 * np.pi * 4.5 * t)) * .045

    k = 0
    while k * beat < dur:
        t, bar, pos = k * beat, (k // 4) % 4, k % 4
        if pos == 0:
            put(epiano(prog[bar], 4 * beat + .8), t)
            put(mu.pad([m + 12 for m in prog[bar]], 4 * beat + .6, .012), t)
        if pos == 2:
            put(epiano([prog[bar][1] + 12, prog[bar][3] + 12], 1.6 * beat), t + beat * .5, .6)
        if pos in (0, 2) and t > 1.5:
            put(mu.kick(), t, .35)
        if pos in (1, 3) and t > 1.5:
            put(mu.clap(), t, .22)
        put(mu.hat(), t + beat * .5, .28)
        tb = np.arange(int(beat * .9 * SR)) / SR
        put(np.sin(2 * np.pi * mu.hz(roots[bar]) * tb) * np.exp(-tb * 2.5) * .16, t)
        k += 1
    fade = np.ones(n); fade[:int(1.2 * SR)] = np.linspace(0, 1, int(1.2 * SR)); fade[-int(1.5 * SR):] = np.linspace(1, 0, int(1.5 * SR))
    return out * fade


def main():
    vo_dir, out = sys.argv[1:3]
    t, scenes, words, clips = LEAD, [], [], []
    for li, (f, kind, n, title, cap) in enumerate(LINES):
        x = load(f"{vo_dir}/{f}.mp3")
        d = len(x) / SR
        start = 0.0 if li == 0 else t - LEAD
        spans = merge_spans(speech_spans(x), max(1, len([c for c in cap.split("...") if c.strip()])))
        words += place_words(cap, spans, t, li)
        clips.append((x, t))
        end = t + d + (TAIL if kind == "end" else GAP)
        scenes.append({"kind": kind, "n": n, "title": title, "start": round(start, 3), "end": round(end - LEAD, 3) if kind != "end" else round(end, 3)})
        t = end
    for a, b in zip(scenes, scenes[1:]):
        a["end"] = b["start"]
    for s in scenes:
        s["dur"] = round(s["end"] - s["start"], 3)
    dur = scenes[-1]["end"]
    json.dump({"dur": dur, "scenes": scenes, "words": words}, open(f"{out}/timeline.json", "w"), indent=1)

    N = int(dur * SR)
    vo = np.zeros(N)
    for x, t0 in clips:
        i = int(t0 * SR); vo[i:i + len(x)] += x[:N - i]
    music = bed(dur)
    e = np.convolve(np.abs(vo), np.ones(int(.1 * SR)) / int(.1 * SR), mode="same")
    music *= (1 - .6 * np.clip(e / (e.max() * .2), 0, 1)) * .75
    sfx = np.zeros(N)

    def put(c, at, g):
        i = int(at * SR)
        if 0 <= i < N: sfx[i:i + len(c)] += c[:N - i] * g
    put(fx.boom(), 0, .55); put(fx.whoosh(.5), 0, .45)
    for s in scenes[1:]:
        put(fx.whoosh(.4), s["start"] - .12, .5)
        if s["n"]:
            put(fx.hit(.6), s["start"], .35)
    tempo = next(s for s in scenes if s["kind"] == "tempo")
    for k in range(3):
        put(fx.tick(), tempo["start"] + .6 + k * .72, .9)
    endc = scenes[-1]
    put(fx.click(), endc["start"] + 2.4, .6); put(fx.bell(), endc["start"] + 2.5, .45)
    mix = vo + music + sfx * .5
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ac", "1", "-ar", str(SR), "-i", "-",
                    "-af", "loudnorm=I=-14:TP=-1.5:LRA=9", "-ac", "2", "-ar", str(SR), f"{out}/mix.wav"],
                   input=np.clip(mix, -1, 1).astype(np.float32).tobytes(), check=True)
    print(f"{dur:.2f} s, {len(scenes)} scenes, {len(words)} words")
    for s in scenes:
        print(f"  {s['kind']:9s} {s['start']:6.2f}-{s['end']:6.2f}")


if __name__ == "__main__":
    main()
