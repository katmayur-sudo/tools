"""Word-timestamped transcription that keeps repeated takes.
usage: transcribe.py <16k mono wav> <out words.json> [model=medium.en]"""
import sys, json, wave, numpy as np
from faster_whisper import WhisperModel

wf = wave.open(sys.argv[1])
a = np.frombuffer(wf.readframes(wf.getnframes()), np.int16).astype(np.float32) / 32768
m = WhisperModel(sys.argv[3] if len(sys.argv) > 3 else "medium.en", device="cpu", compute_type="int8")
# condition_on_previous_text=False stops whisper from merging repeated takes into one
segs, _ = m.transcribe(a, beam_size=5, word_timestamps=True, condition_on_previous_text=False, vad_filter=True,
                       vad_parameters={"min_silence_duration_ms": 300})
words = []
for s in segs:
    print(f"[{s.start:7.2f}-{s.end:7.2f}] {s.text}", flush=True)
    for w in s.words:
        words.append({"w": w.word.strip(), "s": round(w.start, 2), "e": round(w.end, 2)})
json.dump(words, open(sys.argv[2], "w"), indent=0)
print(len(words), "words")
