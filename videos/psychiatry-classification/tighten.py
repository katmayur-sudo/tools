"""Remove breaths and long pauses from a cleaned voice track (level-based, no transcriber).

Usage: python3 tighten.py <in.wav> <out.wav>
Sound is split into segments at dips below FLOOR lasting over 50 ms (shorter dips are consonant
closures). A segment that never reaches LOUD is a breath or noise and is dropped. A segment's
quiet lead-in / tail is cut to 0.15 / 0.2 s (keeps soft onsets like "Ph-", drops an attached
breath). Gaps become 0.3 s where the original paused over 0.45 s (sentence), else at most 0.15 s.
"""
import subprocess
import sys
import wave

import numpy as np

SR, HOP = 48000, 480                        # 10 ms frames
FLOOR, LOUD = -38, -26                      # dB (20 ms RMS)
DIP = 5                                     # frames below FLOOR still counted as inside a word
LEAD, TAIL = 15, 20                         # max quiet frames kept before / after a segment's loud part
FADE = int(.012 * SR)


def main():
    src, out = sys.argv[1:3]
    x = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                                     capture_output=True, check=True).stdout, np.float32)
    db = 20 * np.log10(np.sqrt(np.convolve(x ** 2, np.ones(2 * HOP) / (2 * HOP), "same")[::HOP]) + 1e-9)
    on = db > FLOOR
    segs, i = [], 0                          # [start, end) frames above FLOOR, bridging short dips
    while i < len(on):
        if not on[i]:
            i += 1
            continue
        j = i
        while j < len(on) and (on[j] or on[j:j + DIP + 1].any()):
            j += 1
        segs.append((i, j))
        i = j
    kept = []
    for a, b in segs:
        loud = np.flatnonzero(db[a:b] > LOUD)
        if len(loud):                        # else: breath / noise only
            kept.append((max(a, a + loud[0] - LEAD), min(b, a + loud[-1] + 1 + TAIL)))
    fade = np.linspace(0, 1, FADE)
    parts, prev = [np.zeros(int(.25 * SR), np.float32)], None
    for a, b in kept:
        if prev is not None:
            g = (a - prev) / 100
            parts.append(np.zeros(int((.3 if g > .45 else min(g, .15)) * SR), np.float32))
        seg = x[a * HOP:b * HOP].copy()
        seg[:FADE] *= fade
        seg[-FADE:] *= fade[::-1]
        parts.append(seg)
        prev = b
    parts.append(np.zeros(int(.3 * SR), np.float32))
    y = np.concatenate(parts)
    assert kept and len(y) <= len(x) + SR, "nothing kept or track grew"
    with wave.open(out, "wb") as f:
        f.setnchannels(1), f.setsampwidth(2), f.setframerate(SR)
        f.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())
    print(f"{len(segs)} segments, {len(segs) - len(kept)} breaths dropped, {len(x) / SR:.1f} s -> {len(y) / SR:.1f} s")


if __name__ == "__main__":
    main()
