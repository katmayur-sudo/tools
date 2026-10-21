"""Music helpers.
  beat.py energy <file> [...]   one char per second (space = near-silence); reject tracks with gaps/dips
  beat.py phase <file> <bpm>    where the beat grid falls (low-band onset folding)"""
import sys, subprocess, numpy as np
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))  # -I mode skips the script dir
from common import FF


def pcm(f, sr, af=None):
    cmd = [FF, "-v", "error", "-i", f, "-ac", "1", "-ar", str(sr)] + (["-af", af] if af else []) + ["-f", "s16le", "-"]
    return np.frombuffer(subprocess.run(cmd, capture_output=True).stdout, np.int16).astype(np.float32) / 32768


if sys.argv[1] == "energy":
    for f in sys.argv[2:]:
        a = pcm(f, 8000); w = 4000
        db = 20 * np.log10(np.array([np.sqrt(np.mean(a[i:i + w] ** 2) + 1e-9) for i in range(0, len(a) - w, w)]))
        print(f"{f}: {len(a) / 8000:.0f}s\n  " + "".join(" .:-=+*#%@"[min(9, max(0, int((d + 40) / 4)))] for d in db[::2]))
else:
    f, bpm = sys.argv[2], float(sys.argv[3]); SR = 4000; a = pcm(f, SR, "lowpass=150"); hop = 40
    env = np.array([np.sqrt(np.mean(a[i:i + hop] ** 2)) for i in range(0, len(a) - hop, hop)])
    on = np.maximum(0, np.diff(env)); P = int(round(60 / bpm * 100))
    for lo in range(8, int(len(on) / 100) - 40, 40):
        seg = on[lo * 100:(lo + 40) * 100]
        best = max(range(P), key=lambda ph: seg[ph::P].sum())
        print(f"{lo}-{lo + 40}s: beats at {lo + best / 100:.2f}s + k*{60 / bpm:.3f}s")
