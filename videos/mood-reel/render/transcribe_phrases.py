# Phrase-by-phrase transcription: split at pauses (>=0.3 s below -40 dB), transcribe every phrase on its own.
import sys, json, subprocess, numpy as np
from faster_whisper import WhisperModel
wav, out = sys.argv[1:3]
a = np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i",wav,"-f","f32le","-ac","1","-ar","16000","-"],capture_output=True).stdout, np.float32)
fr = 160  # 10 ms
db = np.array([20*np.log10(np.sqrt(np.mean(a[i:i+fr]**2))+1e-9) for i in range(0, len(a)-fr, fr)])
loud = db > db.max() - 40
runs, st = [], None
for i, l in enumerate(loud):
    if l and st is None: st = i
    if not l and st is not None:
        if not loud[i:i+30].any(): runs.append((st, i)); st = None
if st is not None: runs.append((st, len(loud)))
runs = [(max(s-15,0), e+15) for s, e in runs if e - s > 12]
m = WhisperModel("large-v3", device="cpu", compute_type="int8")
phr = []
for s, e in runs:
    seg, _ = m.transcribe(a[s*fr:e*fr], language="hi", vad_filter=False, word_timestamps=True, condition_on_previous_text=False)
    ws = [{"w": w.word.strip(), "s": round(w.start + s/100, 3), "e": round(w.end + s/100, 3), "p": round(w.probability, 2)} for x in seg for w in x.words]
    phr.append({"s": s/100, "e": e/100, "words": ws})
    print(f"{s/100:6.2f}-{e/100:6.2f} " + " ".join(w["w"] for w in ws), flush=True)
json.dump(phr, open(out, "w"), ensure_ascii=False)
