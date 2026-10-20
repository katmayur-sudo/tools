"""Soundtrack for the refined short: re-cut voice + synthesized bed + SFX on the visual cues, -14 LUFS.

Usage: python3 mix.py <film_dir> <porcelain|redblack> <out.wav>
<film_dir> holds vo.wav and timeline.json from build_timeline.py. porcelain gets the bright 124 BPM
keynote groove of the launch film; redblack a darker 120 BPM minor trap bed. All audio except the
voice is generated here, so it is free to publish.
"""
import json
import pathlib
import subprocess
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / "videos/beginner-gym-engine/tools"), str(ROOT / ".claude/skills/og-content-generator/engine")]
import make_audio as fx  # noqa: E402
import music as mu  # noqa: E402

SR = 48000


def place(buf, clip, t, gain=1.0):
    i = int(t * SR)
    if i >= len(buf):
        return
    clip = clip[:len(buf) - i]
    buf[i:i + len(clip)] += clip * gain


def bed(dur, grade):
    n = int((dur + 1) * SR)
    out = np.zeros(n)
    if grade == "porcelain":
        bpm, prog_ = 124, [[57, 60, 64, 67], [53, 57, 60, 64], [48, 52, 55, 59], [55, 59, 62, 66]]
        beat = 60 / bpm
        for k in range(int(dur / beat) + 1):
            t = k * beat
            place(out, mu.kick(), t, .55)
            if k % 2:
                place(out, mu.clap(), t, .5)
            place(out, mu.hat(), t + beat / 2, .7)
            if k % 2 == 0:
                place(out, mu.chord([m + 12 for m in prog_[(k // 8) % 4]], beat * 1.6, .035), t + beat / 2)
            if k % 8 == 0:
                place(out, mu.pad(prog_[(k // 8) % 4], beat * 8.4, .03), t)
    else:
        bpm, roots = 120, [38, 38, 34, 36]  # D minor: D D Bb C
        beat = 60 / bpm
        for k in range(int(dur / beat) + 1):
            t, bar = k * beat, (k // 4) % 4
            if k % 8 in (0, 3, 6):
                sub = np.arange(int(.6 * SR)) / SR
                f = mu.hz(roots[bar]) * (1 + 1.5 * np.exp(-sub * 40))
                place(out, np.tanh(2 * np.sin(2 * np.pi * np.cumsum(f) / SR)) * np.exp(-sub * 3.2) * .45, t)
            if k % 4 == 2:
                place(out, mu.clap(), t, .6)
            for h in range(2):
                place(out, mu.hat(), t + h * beat / 2, .55 if h == 0 else .35)
            if k % 16 == 0:
                place(out, mu.pad([roots[bar] + 24, roots[bar] + 27, roots[bar] + 31], beat * 16.4, .028), t)
    fade = np.ones(n)
    fade[:int(.05 * SR)] = np.linspace(0, 1, int(.05 * SR))
    return out[:int(dur * SR)] * fade[:int(dur * SR)]


def main():
    film, grade, out = sys.argv[1:4]
    tl = json.load(open(f"{film}/timeline.json"))
    c, dur = tl["cues"], tl["dur"]
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", f"{film}/vo.wav", "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    vo = np.frombuffer(raw, np.float32).astype(np.float64)
    n = int(dur * SR)
    vo = np.pad(vo, (0, max(0, n - len(vo))))[:n]
    music = bed(dur, grade)
    # sidechain: duck the bed under the voice (smoothed envelope)
    e = np.abs(vo)
    k = int(.08 * SR)
    e = np.convolve(e, np.ones(k) / k, mode="same")
    duck = 1 - .55 * np.clip(e / (e.max() * .25), 0, 1)
    music *= duck * (.5 if grade == "porcelain" else .6)

    sfx = np.zeros(n)
    red = grade == "redblack"
    place(sfx, fx.hit(), 0.0, .9 if red else .5)
    place(sfx, fx.whoosh(.5), 0.0, .5)
    for sc in ["promise", "m1", "f1", "m2", "f2", "m3", "f3", "m4", "f4", "m5", "f5", "recap", "cta"]:
        place(sfx, fx.whoosh(.4) if red else fx.swish(.3), c[sc] - .12, .55 if red else .45)
    for i in range(5):
        place(sfx, fx.pop(), c["five"] + i * .1, .7)
    for sc, d in [("m1", .5), ("m2", .4), ("m3", .4), ("m4", .3)]:
        place(sfx, fx.error(), c[sc] + d, .55)
    for sc, d in [("f1", .3), ("f2", .3), ("f3", .3), ("f4", .3), ("f5", .2)]:
        place(sfx, fx.ding(), c[sc] + d, .4)
    place(sfx, fx.error(), c["dhadaam"], .5)
    place(sfx, fx.boom(), c["dhadaam"], .9 if red else .6)
    for kk in range(3):
        place(sfx, fx.tick(), c["f5"] + .7 + kk * .8, .9)
    step = (c["check"] - c["recap"] - .2) / 5
    for i in range(5):
        place(sfx, fx.pop(), c["recap"] + .2 + i * step, .7)
    place(sfx, fx.click(), c["follow"] + .25, .6)
    place(sfx, fx.bell(), c["follow"] + .35, .5)

    mix = vo * 1.0 + music + sfx * .55
    x = np.clip(mix, -1, 1).astype(np.float32)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ac", "1", "-ar", str(SR), "-i", "-",
                    "-af", "loudnorm=I=-14:TP=-1.5:LRA=9", "-ac", "2", "-ar", str(SR), out], input=x.tobytes(), check=True)
    print("mix", grade, round(dur, 2), "s ->", out)


if __name__ == "__main__":
    main()
