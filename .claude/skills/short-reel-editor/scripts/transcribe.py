"""Word-timestamped transcription that keeps repeated takes.
usage: transcribe.py <16k mono wav> <out words.json> [--lang en|hi|auto] [--model NAME] [--prompt "script words"]
  --lang en    English (default model medium.en)
  --lang hi    Hindi or Hinglish (default model large-v3; words come out mostly in Devanagari, English words often in Latin)
  --lang auto  detect per file (multilingual model)
  --prompt     a line or two of the script in the spelling you want: biases names and English words in Hinglish"""
import sys, json, wave, numpy as np
from faster_whisper import WhisperModel

args = [a for a in sys.argv[1:]]
opt = lambda k, d=None: args[args.index(k) + 1] if k in args else d
pos = [a for i, a in enumerate(args) if not a.startswith("--") and (i == 0 or not args[i - 1].startswith("--"))]
LANG = opt("--lang", "en")
MODEL = opt("--model") or (pos[2] if len(pos) > 2 else ("medium.en" if LANG == "en" else "large-v3"))
if LANG != "en" and MODEL.endswith(".en"):
    sys.exit(f"{MODEL} is English-only; use a multilingual model (large-v3, medium) for --lang {LANG}")

wf = wave.open(pos[0])
a = np.frombuffer(wf.readframes(wf.getnframes()), np.int16).astype(np.float32) / 32768
m = WhisperModel(MODEL, device="cpu", compute_type="int8")
# condition_on_previous_text=False stops whisper from merging repeated takes into one
segs, info = m.transcribe(a, language=None if LANG == "auto" else LANG, beam_size=5, word_timestamps=True,
                          condition_on_previous_text=False, vad_filter=True, initial_prompt=opt("--prompt"),
                          vad_parameters={"min_silence_duration_ms": 300})
print(f"model {MODEL}, language {info.language} ({info.language_probability:.2f})", flush=True)
words = []
for s in segs:
    print(f"[{s.start:7.2f}-{s.end:7.2f}] {s.text}", flush=True)
    for w in s.words:
        words.append({"w": w.word.strip(), "s": round(w.start, 2), "e": round(w.end, 2)})
json.dump(words, open(pos[1], "w"), indent=0, ensure_ascii=False)
print(len(words), "words")
