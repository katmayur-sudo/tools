"""Edit the owner's voice-over to fit the reel: drop retakes, breaths and long pauses, speed up, time every script word.

Usage: python3 vo.py <reel.json> <raw voice-over> <out_dir> [max_seconds=178] [heard.json]
Writes out_dir/vo.wav (denoised, cleaned, sped up, -16 LUFS) and out_dir/words.json (script words with times),
which timeline.py takes as its 3rd argument. Needs: pip install faster-whisper (model "small").
Whisper hears the Hinglish as Roman text; its word times are aligned back to the script's own words
(../beginner-gym-engine/tools/transcribe.py), so captions always show the script spelling.
"""
import difflib
import json
import os
import subprocess
import sys
import wave

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../beginner-gym-engine/tools"))
from transcribe import align, norm  # noqa: E402

SR = 48000
GAP_IN, GAP_BEAT = .14, .32   # pause kept inside a scene / between scenes (before speed-up)
PAD = .04                     # audio kept around each heard word


def pcm(path, sr, filters=""):
    cmd = ["ffmpeg", "-v", "error", "-i", path] + (["-af", filters] if filters else []) + ["-f", "f32le", "-ac", "1", "-ar", str(sr), "-"]
    return np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32)


def drop_retakes(heard, matched):
    """Unmatched heard runs that repeat the words right after them are false starts: drop them."""
    keep, i = [True] * len(heard), 0
    while i < len(heard):
        if i in matched:
            i += 1
            continue
        j = i
        while j < len(heard) and j not in matched:
            j += 1
        run = " ".join(norm(h["w"]) for h in heard[i:j])
        nxt = " ".join(norm(h["w"]) for h in heard[j:j + (j - i)])
        if difflib.SequenceMatcher(None, run, nxt).ratio() > .6:
            keep[i:j] = [False] * (j - i)
        i = j
    return keep


def main():
    reel, raw, out = sys.argv[1:4]
    limit = float(sys.argv[4]) if len(sys.argv) > 4 else 178
    os.makedirs(out, exist_ok=True)
    beats = json.load(open(reel))["beats"]
    x = pcm(raw, SR, "highpass=f=80,lowpass=f=12000,afftdn=nf=-30:nr=40:tn=1,afftdn=nf=-40:nr=12")  # two passes: room noise, then hiss
    if len(sys.argv) > 5:  # cached transcript: Whisper sometimes translates Hinglish runs instead of transcribing them
        heard = json.load(open(sys.argv[5]))
    else:
        from faster_whisper import WhisperModel
        prompt = "BHMS psychology Hinglish. Descartes, Wundt, Titchener, Freud, Watson, Skinner, Piaget, Hahnemann, Kent, Organon, aphorism."
        segs, _ = WhisperModel("small", device="cpu", compute_type="int8").transcribe(
            pcm(raw, 16000, "highpass=f=80,afftdn=nf=-35:nr=25:tn=1"), language="en", word_timestamps=True, initial_prompt=prompt)
        heard = [{"w": w.word.strip(), "s": w.start, "e": w.end} for s in segs for w in s.words]

    # which heard words the script matched, then drop false starts
    a, b = [norm(w) for b_ in beats for w in b_["vo"].split()], [norm(h["w"]) for h in heard]
    matched = {blk.b + k for blk in difflib.SequenceMatcher(None, a, b, autojunk=False).get_matching_blocks() for k in range(blk.size)}
    keep = drop_retakes(heard, matched)
    heard = [h for h, k in zip(heard, keep) if k]
    print(f"{len(keep)} heard words, {keep.count(False)} dropped as retakes")

    # beat of each heard word, from the aligned script words
    script = [(i, w) for i, bt in enumerate(beats) for w in bt["vo"].split()]
    words = align([w for _, w in script], heard)
    first = {}
    for (bi, _), w in zip(script, words):
        first.setdefault(bi, w["s"])
    beat_of = lambda t: max([bi for bi, s in first.items() if s <= t + .05], default=0)

    # splice: keep each heard word, shrink every gap; build a time map old -> new
    parts, tmap, t_new, prev = [np.zeros(int(.3 * SR), np.float32)], [], .3, None
    for h in heard:
        s, e = max(0, h["s"] - PAD), h["e"] + PAD
        if prev is not None:
            if s <= prev[1]:                       # overlapping pads: continue the same span
                s = prev[1]
            else:
                g = min(s - prev[1], GAP_BEAT if beat_of(h["s"]) != beat_of(prev[0]) else GAP_IN)
                parts.append(np.zeros(int(g * SR), np.float32))
                t_new += g
        seg = x[int(s * SR):int(e * SR)].copy()
        f = min(len(seg) // 2, int(.01 * SR))
        if f:
            seg[:f] *= np.linspace(0, 1, f)
            seg[-f:] *= np.linspace(1, 0, f)
        tmap.append((s, t_new))
        parts.append(seg)
        t_new += len(seg) / SR
        tmap.append((e, t_new))
        prev = (h["s"], e)
    y = np.concatenate(parts + [np.zeros(int(.3 * SR), np.float32)])
    src, dst = np.array([p[0] for p in tmap]), np.array([p[1] for p in tmap])

    speed = max(1.0, (len(y) / SR + 1.5) / limit)      # 1.5 s end card
    assert speed < 1.35, f"needs {speed:.2f}x to fit {limit}s: cut the script instead"
    tmp = os.path.join(out, "spliced.wav")
    with wave.open(tmp, "wb") as f:
        f.setnchannels(1), f.setsampwidth(2), f.setframerate(SR)
        f.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-af",
                    f"atempo={speed:.4f},equalizer=f=250:t=q:w=1.2:g=-2,equalizer=f=3500:t=q:w=1.5:g=2,"
                    "acompressor=threshold=-22dB:ratio=3:attack=8:release=120:makeup=2,loudnorm=I=-16:TP=-1.5:LRA=7",
                    "-ar", str(SR), os.path.join(out, "vo.wav")], check=True)
    os.remove(tmp)

    re_t = lambda t: round(float(np.interp(t, src, dst)) / speed, 3)
    json.dump([{"w": w["w"], "s": re_t(w["s"]), "e": re_t(w["e"])} for w in words],
              open(os.path.join(out, "words.json"), "w"), ensure_ascii=False, indent=0)
    print(f"{len(x) / SR:.1f} s raw -> {len(y) / SR:.1f} s spliced -> {len(y) / SR / speed:.1f} s at {speed:.2f}x")


if __name__ == "__main__":
    main()
