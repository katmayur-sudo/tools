"""Soundtrack for Delirium vs Dementia: synth music bed + sfx on the cuts, plus the voice if given.

Usage: python3 mix.py <timeline.json> <out.wav> [vo.wav]
Without a voice the music is not ducked (silent preview). Master at -14 LUFS.
Music and sfx come from ../beginner-gym-engine/tools/make_audio.py (synthesized, free to publish).
"""
import json
import subprocess
import sys

import numpy as np

sys.path.insert(0, "../beginner-gym-engine/tools")
import make_audio as ma  # noqa: E402

SFX = {"hook": {"galat": "error", "delirium": "boom"}, "block": {"organic": "ding"},
       "diff": {"left": "pop", "right": "pop", "both": "chime"}, "defs": {"right": "pop"},
       "myth": {"fact": "error"}, "mgmt": {}, "exam": {"left": "hit", "right": "hit"}, "close": {"save": "chime"}}


def main():
    tl_path, out = sys.argv[1:3]
    vo = sys.argv[3] if len(sys.argv) > 3 else None
    tl = json.load(open(tl_path))
    sr, total = ma.SR, tl["end"]
    bank = {k: getattr(ma, k)() for k in ("whoosh", "pop", "error", "boom", "ding", "chime", "hit", "tick")}
    hits = [(b["start"], "whoosh") for b in tl["beats"][1:]] + [(0.0, "whoosh")]
    for b in tl["beats"]:
        for k, t in b["cues"].items():
            kind = SFX[b["type"]].get(k, "tick" if b["type"] == "mgmt" else None)
            if kind:
                hits.append((t, kind))
        if b["type"] == "myth":
            hits.append((b["cues"]["fact"] + .3, "ding"))
    fx = np.zeros(int((total + 2) * sr))
    for t, kind in hits:
        snd = bank[kind]
        i = max(0, int(t * sr) - (int(.45 * sr) if kind == "whoosh" else 0))  # whoosh peaks ~0.45 s in
        fx[i:i + len(snd)] += snd[:len(fx) - i]
    n = int(total * sr)
    ma.write_wav(out + ".sfx.wav", fx[:n] * .7)
    ma.write_wav(out + ".music.wav", ma.music(total)[:n] * .8)
    if vo:
        graph = (f"[2:a]aresample={sr},pan=stereo|c0=c0|c1=c0,apad=whole_dur={total},asplit=2[vo][key];"
                 "[0:a]volume=0.5[mus];[mus][key]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=400[duck];"
                 "[1:a]volume=0.55[fx];[vo][duck][fx]amix=inputs=3:normalize=0[m];[m]loudnorm=I=-14:TP=-1.5:LRA=9[out]")
    else:
        graph = "[0:a]volume=0.5[mus];[1:a]volume=0.55[fx];[mus][fx]amix=inputs=2:normalize=0[m];[m]loudnorm=I=-14:TP=-1.5:LRA=9[out]"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", out + ".music.wav", "-i", out + ".sfx.wav", *(["-i", vo] if vo else []),
                    "-filter_complex", graph, "-map", "[out]", "-ar", str(sr), "-t", str(total), out], check=True)
    print(out, f"{total:.1f} s, {len(hits)} sfx, voice: {bool(vo)}")


if __name__ == "__main__":
    main()
