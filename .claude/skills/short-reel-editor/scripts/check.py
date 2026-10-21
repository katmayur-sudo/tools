"""Critique loop: loudness, true peak, frozen/black frames, and voice intelligibility vs the cut's words.
usage: check.py final.mp4 words_cut.json [--model small.en]"""
import difflib, json, re, subprocess, sys, wave, os, tempfile
import numpy as np
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))  # -I mode skips the script dir
from common import FF, duration

F, WORDS = sys.argv[1], sys.argv[2]
model = sys.argv[sys.argv.index("--model") + 1] if "--model" in sys.argv else "small.en"
print(f"duration {duration(F):.2f}s")
log = subprocess.run([FF, "-hide_banner", "-nostats", "-i", F, "-vf", "freezedetect=n=0.001:d=0.6,blackdetect=d=0.2",
                      "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
fr = re.findall(r"freeze_start: ([\d.]+)", log); bl = re.findall(r"black_start:([\d.]+)", log)
I = re.findall(r"^\s+I:\s+(-?[\d.]+) LUFS", log, re.M); pk = re.findall(r"^\s+Peak:\s+(-?[\d.]+) dBFS", log, re.M)
print("frozen stretches:", fr or "none"); print("black frames:", bl or "none")
print(f"loudness {I[-1] if I else '?'} LUFS, true peak {pk[-1] if pk else '?'} dBFS (target -14 / <= -1.5)")
wav = os.path.join(tempfile.mkdtemp(), "a.wav")
subprocess.run([FF, "-v", "error", "-y", "-i", F, "-ac", "1", "-ar", "16000", wav], check=True)
a = np.frombuffer(wave.open(wav).readframes(10 ** 9), np.int16).astype(np.float32) / 32768
from faster_whisper import WhisperModel
segs, _ = WhisperModel(model, compute_type="int8").transcribe(a, language="en")
norm = lambda t: [x for x in re.sub(r"[^a-z0-9' ]", " ", t.lower()).split() if x]
ref = norm(" ".join(x["w"] for x in json.load(open(WORDS)))); hyp = norm(" ".join(s.text for s in segs))
sm = difflib.SequenceMatcher(None, ref, hyp)
print(f"voice match {sm.ratio() * 100:.1f}%  (compare with the voice-only bus; digits/spelling diffs are harmless)")
for op, i1, i2, j1, j2 in sm.get_opcodes():
    if op != "equal": print("  ", op, ref[i1:i2], "->", hyp[j1:j2])
