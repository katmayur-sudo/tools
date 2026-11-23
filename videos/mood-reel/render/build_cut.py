# segments -> voice_cut.wav, words aligned on the cut audio, A-roll (picture 4 frames ahead of sound in the raw file)
import json, wave, subprocess, sys, numpy as np
SEGF = sys.argv[1]; FPS, SR, VOFF = 30, 48000, 4
seg = [(round(a * FPS), round(b * FPS)) for a, b in json.load(open(SEGF))]
with wave.open("voice_clean.wav") as w: v = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32)
spf, fade = SR // FPS, int(0.01 * SR); parts = []
for A, B in seg:
    p = v[A * spf:B * spf].copy(); p[:fade] *= np.linspace(0, 1, fade); p[-fade:] *= np.linspace(1, 0, fade); parts.append(p)
with wave.open("voice_cut.wav", "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(np.clip(np.concatenate(parts), -32768, 32767).astype("<i2").tobytes())
S = [(A / FPS, B / FPS) for A, B in seg]
def m(t, start):
    c = 0
    for a, b in S:
        if a - 0.03 <= t <= b + 0.03: return round(c + min(max(t - a, 0), b - a), 3)
        if start and a > t and a - t < 0.6: return round(c, 3)
        c += b - a
W = json.load(open("words_kept.json"))
for x in W: x["s"], x["e"] = m(x["s"], 1), m(x["e"], 0)
for i, x in enumerate(W):
    if x["e"] is None: x["e"] = W[i + 1]["s"] if i + 1 < len(W) and W[i + 1]["s"] else x["s"] + 0.3
    if x["s"] is None: x["s"] = W[i - 1]["e"]
json.dump(W, open("words_cutrough.json", "w"), ensure_ascii=False)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "voice_cut.wav", "-ar", "16000", "cut16.wav"], check=True)
subprocess.run(["python3", "/home/user/tools/.claude/skills/short-reel-editor/scripts/align.py", "cut16.wav",
                "words_cutrough.json", "aligned_cut.json", "--lang", "hi"], check=True, capture_output=True)
A = json.load(open("aligned_cut.json"))
assert all(A[i]["s"] <= A[i + 1]["s"] for i in range(len(A) - 1)), "aligned words out of order"
for x in A: x["cs"], x["ce"] = x["s"], x["e"]
json.dump(A, open("words_cut2.json", "w"), ensure_ascii=False)
sel = "+".join(f"between(n,{a + VOFF},{b + VOFF - 1})" for a, b in seg)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "raw.mp4", "-i", "voice_cut.wav", "-filter_complex",
                f"[0:v]fps={FPS},select='{sel}',setpts=N/{FPS}/TB,format=yuv420p[v]", "-map", "[v]", "-map", "1:a", "-r", str(FPS),
                "-c:v", "libx264", "-preset", "slow", "-crf", "14", "-c:a", "aac", "-b:a", "320k", "-shortest",
                "-movflags", "+faststart", "aroll.mp4"], check=True)
print("frames", sum(b - a for a, b in seg), "low-score words", [(i, x["w"]) for i, x in enumerate(A) if x["sc"] < 0.2])
