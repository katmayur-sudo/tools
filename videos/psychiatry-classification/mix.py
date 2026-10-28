"""Soundtrack for the psychiatry short: cleaned voice + synth music bed (ducked) + sfx, -14 LUFS.

Usage: python3 mix.py <timeline.json> <vo_clean.wav> <out.wav>
Music and sfx come from ../beginner-gym-engine/tools/make_audio.py (synthesized, free to publish).
"""
import json
import subprocess
import sys

import numpy as np

sys.path.insert(0, "../beginner-gym-engine/tools")
import make_audio as ma  # noqa: E402


def main():
    tl_path, vo, out = sys.argv[1:4]
    tl = json.load(open(tl_path))
    sr, total = ma.SR, tl["end"]
    hits = []  # (time, sound)
    for b in tl["beats"]:
        c = b["cues"]
        if b["type"] == "hook":
            hits += [(0.0, ma.whoosh()), (c["ten"], ma.boom())]
        else:
            hits.append((b["start"], ma.whoosh() if b["type"] == "group" else ma.swish()))
        if b["type"] == "group":
            hits.append((c["examples"], ma.pop()))
        if b["type"] == "recap":
            hits += [(t, ma.tick()) for k, t in c.items()]
        if b["type"] == "close":
            hits += [(c["delirium"], ma.hit()), (c["think"], ma.ding()), (c["save"], ma.chime())]
    fx = np.zeros(int((total + 2) * sr))
    for t, snd in hits:
        i = max(0, int(t * sr) - (int(.45 * sr) if len(snd) == len(ma.whoosh()) else 0))  # whoosh peaks ~0.45 s in
        fx[i:i + len(snd)] += snd[:len(fx) - i]
    n = int(total * sr)
    ma.write_wav(out + ".sfx.wav", fx[:n] * .7)
    ma.write_wav(out + ".music.wav", ma.music(total)[:n] * .8)
    graph = (f"[0:a]aresample={sr},pan=stereo|c0=c0|c1=c0,apad=whole_dur={total},asplit=2[vo][key];"
             "[1:a]volume=0.5[mus];[mus][key]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=400[duck];"
             "[2:a]volume=0.55[fx];[vo][duck][fx]amix=inputs=3:normalize=0[m];[m]loudnorm=I=-14:TP=-1.5:LRA=9[out]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", vo, "-i", out + ".music.wav", "-i", out + ".sfx.wav",
                    "-filter_complex", graph, "-map", "[out]", "-ar", str(sr), "-t", str(total), out], check=True)
    print(out, f"{total:.1f} s, {len(hits)} sfx")


if __name__ == "__main__":
    main()
