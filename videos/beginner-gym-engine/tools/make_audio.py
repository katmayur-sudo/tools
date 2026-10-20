"""Build the soundtrack: voice-over + synthesized music bed + sound effects, mixed to -14 LUFS.

Usage: python3 make_audio.py <timeline.json> <vo_dir> <out_dir>
Everything except the voice is generated here (no third-party audio), so it is free to publish.
"""
import json
import subprocess
import sys
import wave

import numpy as np

SR = 48000
rng = np.random.default_rng(7)


def write_wav(path, x):
    x = np.clip(x, -1, 1)
    st = np.stack([x, x], axis=1) if x.ndim == 1 else x
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((st * 32767).astype("<i2").tobytes())


def lowpass(x, cutoff):
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):  # one-pole filter; inputs here are short
        acc = (1 - a) * x[i] + a * acc
        y[i] = acc
    return y


def env(n, attack, release):
    e = np.ones(n)
    a, r = int(attack * SR), int(release * SR)
    e[:a] = np.linspace(0, 1, a)
    e[-r:] *= np.linspace(1, 0, r) ** 2
    return e


def whoosh(d=0.7):
    n = int(d * SR)
    noise = rng.standard_normal(n)
    sweep = np.linspace(400, 6000, n) ** 1.0
    out = np.zeros(n)
    # cheap time-varying band: blend two low-passes by the sweep
    lo, hi = lowpass(noise, 600), lowpass(noise, 5000)
    mix = np.sin(np.linspace(0, np.pi, n))
    out = (lo * (1 - mix) + (hi - lo) * mix)
    return out * env(n, d * 0.6, d * 0.4) * 0.5 * (sweep / sweep.max()) ** 0.3


def hit(d=1.0):
    n = int(d * SR)
    t = np.arange(n) / SR
    f = 55 + 70 * np.exp(-t * 18)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 4.5)
    click = lowpass(rng.standard_normal(n), 3000) * np.exp(-t * 60) * 0.6
    return (body + click) * 0.8


def pop(d=0.12):
    n = int(d * SR)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * (900 + 600 * np.exp(-t * 40)) * t) * np.exp(-t * 45) * 0.28


def swish(d=0.35):
    n = int(d * SR)
    return lowpass(rng.standard_normal(n), 2500) * env(n, 0.12, 0.2) * 0.3


def music(total):
    """Warm minor pad (Am-F-C-G) with a soft pulse at 96 bpm."""
    n = int(total * SR)
    t = np.arange(n) / SR
    bpm, bar = 96, 4 * 60 / 96
    chords = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]  # midi
    out = np.zeros(n)
    hz = lambda m: 440 * 2 ** ((m - 69) / 12)
    for b in range(int(total / bar) + 1):
        a0, a1 = int(b * bar * SR), min(n, int((b + 1) * bar * SR + 0.6 * SR))
        if a0 >= n:
            break
        seg_t = t[a0:a1] - b * bar
        e = np.minimum(1, seg_t / 0.8) * np.exp(-np.maximum(0, seg_t - bar) * 3)
        for m in chords[b % 4]:
            for det in (-0.08, 0.08):
                f = hz(m) * 2 ** (det / 12)
                out[a0:a1] += (np.sin(2 * np.pi * f * seg_t) + 0.3 * np.sin(4 * np.pi * f * seg_t)) * e * 0.05
        root = hz(chords[b % 4][0] - 12)
        out[a0:a1] += np.sin(2 * np.pi * root * seg_t) * e * 0.08
    beat = 60 / bpm
    kick = hit(0.4) * 0.35
    tick = lowpass(rng.standard_normal(int(0.05 * SR)), 9000) * np.exp(-np.arange(int(0.05 * SR)) / SR * 90) * 0.05
    k = 0
    while k * beat < total:
        i = int(k * beat * SR)
        out[i:i + len(kick)] += kick[:max(0, n - i)]
        j = int((k + 0.5) * beat * SR)
        out[j:j + len(tick)] += tick[:max(0, n - j)]
        k += 1
    fade = np.ones(n)
    fade[:int(2 * SR)] = np.linspace(0, 1, int(2 * SR))
    fade[-int(4 * SR):] = np.linspace(1, 0, int(4 * SR))
    return out * fade


def main():
    tl_path, vo_dir, out = sys.argv[1:4]
    tl = json.load(open(tl_path))
    total = tl["duration"]
    n = int(total * SR) + SR
    fx = np.zeros(n)
    bank = {"whoosh": whoosh(), "hit": hit(), "pop": pop(), "swish": swish()}
    for s in tl["sfx"]:
        snd = bank[s["type"]]
        i = int(s["t"] * SR) - (int(0.45 * SR) if s["type"] == "whoosh" else 0)
        i = max(0, i)
        fx[i:i + len(snd)] += snd[:n - i]
    write_wav(f"{out}/sfx.wav", fx * 0.8)
    write_wav(f"{out}/music.wav", music(total + 1))
    # voice track: each section placed at its timeline position
    inputs, filters = [], []
    for k, a in enumerate(tl["audio"]):
        inputs += ["-i", f"{vo_dir}/{a['file']}"]
        ms = int(a["t"] * 1000)
        filters.append(f"[{k}:a]aresample={SR},adelay={ms}|{ms},pan=stereo|c0=c0|c1=c0[v{k}]")
    mix = "".join(f"[v{k}]" for k in range(len(tl["audio"])))
    filters.append(f"{mix}amix=inputs={len(tl['audio'])}:normalize=0,apad=whole_dur={total}[vo]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(filters),
                    "-map", "[vo]", "-t", str(total), f"{out}/vo.wav"], check=True)
    # final mix: voice on top, music ducked under the voice, effects in between
    graph = ("[0:a]loudnorm=I=-16:TP=-2:LRA=7,asplit=2[vo][key];"
             "[1:a]volume=0.55[mus];[mus][key]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=400[duck];"
             "[2:a]volume=0.9[fx];[vo][duck][fx]amix=inputs=3:normalize=0[m];"
             "[m]loudnorm=I=-14:TP=-1.5:LRA=9[out]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{out}/vo.wav", "-i", f"{out}/music.wav",
                    "-i", f"{out}/sfx.wav", "-filter_complex", graph, "-map", "[out]", "-ar", str(SR),
                    "-t", str(total), f"{out}/mix.wav"], check=True)
    print("mix written", total)


if __name__ == "__main__":
    main()
