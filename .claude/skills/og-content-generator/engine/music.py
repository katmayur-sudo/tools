"""Synthesize an upbeat minimal instrumental cut to the film's beat grid.

Usage: python3 music.py <storyboard.json> <out.wav>
Structure follows the storyboard: soft pad under the cold open, groove from the first porcelain
scene, a drop-out + riser into "One More Thing", the full groove after the reveal, and a pad-only
outro under the end card. Mastered to about -15 LUFS like the reference films.
"""
import json
import subprocess
import sys
import wave

import numpy as np

SR = 48000
rng = np.random.default_rng(3)
hz = lambda m: 440 * 2 ** ((m - 69) / 12)


def lowpass(x, cutoff):
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc = (1 - a) * x[i] + a * acc
        y[i] = acc
    return y


def kick():
    t = np.arange(int(.35 * SR)) / SR
    return np.sin(2 * np.pi * np.cumsum(50 + 110 * np.exp(-t * 30)) / SR) * np.exp(-t * 9) * .9


def clap():
    n = int(.2 * SR)
    t = np.arange(n) / SR
    return lowpass(rng.standard_normal(n), 3500) * (np.exp(-t * 30) + .5 * np.exp(-np.maximum(0, t - .012) * 30)) * .35


def hat():
    n = int(.06 * SR)
    noise = rng.standard_normal(n)
    return (noise - lowpass(noise, 7000)) * np.exp(-np.arange(n) / SR * 70) * .18


def chord(notes, dur, amp=.06, bright=1.0):
    t = np.arange(int(dur * SR)) / SR
    out = sum((np.sin(2 * np.pi * hz(m) * t) + .25 * bright * np.sin(4 * np.pi * hz(m) * t)) for m in notes)
    env = np.minimum(1, t / .01) * np.exp(-t * 3.5)
    return out * env * amp


def pad(notes, dur, amp=.05):
    t = np.arange(int(dur * SR)) / SR
    out = sum(np.sin(2 * np.pi * hz(m) * t + np.sin(t * .7 + m)) for m in notes)
    env = np.minimum(1, t / .6) * np.minimum(1, (dur - t) / .6)
    return out * np.clip(env, 0, 1) * amp


def main():
    sb = json.load(open(sys.argv[1]))
    out_path = sys.argv[2]
    bpm = sb["bpm"]
    beat = 60 / bpm
    starts, b = [], 0
    for sc in sb["scenes"]:
        starts.append((b, b + sc["beats"], sc["type"]))
        b += sc["beats"]
    total_beats = b
    n = int((total_beats * beat + 1.5) * SR)
    mix = np.zeros(n)

    def put(x, t):
        i = int(t * SR)
        if i < n:
            mix[i:i + len(x)] += x[:n - i]

    cold_end = next(e for s, e, k in starts if k == "cold")
    om = [(s, e) for s, e, k in starts if k == "onemore"]
    end_start = next(s for s, e, k in starts if k == "end")
    quiet = set()
    for s, e in om:
        quiet.update(range(s, e))
    # chords: Fmaj7 - Am7 - Dm7 - Cmaj7, one bar each
    prog = [[53, 57, 60, 64], [57, 60, 64, 67], [50, 53, 57, 60], [48, 52, 55, 59]]
    bass = [41, 45, 38, 36]
    k, h, c = kick(), hat(), clap()
    for bt in range(total_beats):
        t = bt * beat
        bar, pos = bt // 4, bt % 4
        ch = prog[bar % 4]
        if pos == 0:
            put(pad([m + 12 for m in ch], 4 * beat + .6, .035), t)
        groove = cold_end <= bt < end_start and bt not in quiet
        if groove:
            put(k, t)
            put(h, t + beat / 2)
            if pos in (1, 3):
                put(c, t)
            if pos in (0, 2):
                put(chord([m + 12 for m in ch], beat * .9, .05), t + beat / 2)
            tb = np.arange(int(beat * .45 * SR)) / SR
            put(np.sin(2 * np.pi * hz(bass[bar % 4]) * tb) * np.exp(-tb * 4) * .22, t)
    # riser into each One More Thing beat and an impact after it
    for s, e in om:
        d = (e - s) * beat
        tt = np.arange(int(d * SR)) / SR
        rise = (np.sin(2 * np.pi * np.cumsum(220 * 6 ** (tt / d)) / SR) * .05 + lowpass(rng.standard_normal(len(tt)), 3000) * .12) * (tt / d) ** 2
        put(rise, s * beat)
        tb = np.arange(int(1.2 * SR)) / SR
        put(np.sin(2 * np.pi * np.cumsum(40 + 80 * np.exp(-tb * 12)) / SR) * np.exp(-tb * 3) * .8, e * beat)
    mix /= max(1e-6, np.abs(mix).max()) * 1.1
    fade = int(1.2 * SR)
    mix[-fade:] *= np.linspace(1, 0, fade)
    raw = out_path + ".raw.wav"
    with wave.open(raw, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((mix * 32767).astype("<i2").tobytes())
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-af", "loudnorm=I=-15:TP=-1.5:LRA=8",
                    "-ar", str(SR), "-ac", "2", out_path], check=True)
    print("music", round(total_beats * beat, 2), "s at", bpm, "bpm")


if __name__ == "__main__":
    main()
