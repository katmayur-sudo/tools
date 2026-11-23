"""Calm pad + soft piano bed and light SFX for the mood reel, then the final mix.

Usage: python3 audio.py <scratch> [voice.wav] [outdir]  (defaults raw1/voice_cut.wav, out; needs <outdir>/cues.json)
Writes out/music.wav, out/sfx.wav, out/mix.wav (-14 LUFS, TP <= -1.5).
"""
import json, subprocess, sys, wave
import numpy as np

S = sys.argv[1]
VOICE = f"{S}/{sys.argv[2] if len(sys.argv) > 2 else 'raw1/voice_cut.wav'}"
OUT = f"{S}/{sys.argv[3] if len(sys.argv) > 3 else 'out'}"
SR = 48000
with wave.open(VOICE) as _w: DUR = _w.getnframes() / SR
rng = np.random.default_rng(7)
t = np.arange(int(SR * DUR)) / SR

def write(path, x):
    x = np.clip(x, -1, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2 if x.ndim == 2 else 1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((x * 32767).astype("<i2").tobytes())

def lp(x, fc):  # one-pole low-pass
    a = np.exp(-2 * np.pi * fc / SR); y = np.empty_like(x); acc = 0.0
    for i, v in enumerate(x): acc = (1 - a) * v + a * acc; y[i] = acc
    return y

hz = lambda m: 440 * 2 ** ((m - 69) / 12)
# Cmaj7 - Am7 - Fmaj7 - G6, 4 s each (60 bpm feel), calm and warm
CHORDS = [[48, 55, 59, 64], [45, 52, 55, 60], [41, 48, 52, 57], [43, 50, 55, 59]]
BAR = 4.0
pad = np.zeros_like(t)
for k in range(int(DUR / BAR) + 1):
    ch = CHORDS[k % 4]; st = k * BAR
    seg = (t >= st - 0.8) & (t < st + BAR + 0.8)
    tt = t[seg] - st
    env = np.clip((tt + 0.8) / 1.2, 0, 1) * np.clip((BAR + 0.8 - tt) / 1.2, 0, 1)
    for m in ch:
        for det in (-0.06, 0.06):
            f = hz(m) * 2 ** (det / 12)
            pad[seg] += env * (np.sin(2 * np.pi * f * t[seg]) + 0.25 * np.sin(4 * np.pi * f * t[seg])) / 8
# soft piano arpeggio, one note per beat, an octave up
pno = np.zeros_like(t)
for b in range(int(DUR)):
    ch = CHORDS[int(b / BAR) % 4]; m = ch[[0, 2, 1, 3][b % 4]] + 12
    s0 = int(b * SR); n = min(int(2.5 * SR), len(t) - s0)
    tt = np.arange(n) / SR; f = hz(m)
    pno[s0:s0 + n] += np.exp(-tt * 2.2) * (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(4 * np.pi * f * tt) + 0.1 * np.sin(6 * np.pi * f * tt)) * 0.18
music = lp(pad, 1800) + lp(pno, 3000)
music *= np.clip(t / 1.5, 0, 1) * np.clip((DUR - t) / 2.5, 0, 1)
music /= np.abs(music).max() * 1.25
# light stereo width: short delay on the right
music = np.stack([music, np.roll(music, int(0.012 * SR))], 1)
write(f"{OUT}/music.wav", music)

# ---- SFX
cues = json.load(open(f"{OUT}/cues.json"))
sfx = np.zeros_like(t)
def whoosh():
    n = int(0.45 * SR); tt = np.arange(n) / SR
    noise = rng.standard_normal(n)
    env = np.sin(np.pi * tt / tt[-1]) ** 2
    y = np.zeros(n); acc = 0.0
    for i in range(n):  # sweeping low-pass 400 Hz -> 3 kHz -> 600 Hz
        fc = 400 + 2600 * np.sin(np.pi * tt[i] / tt[-1])
        a = np.exp(-2 * np.pi * fc / SR); acc = (1 - a) * noise[i] + a * acc; y[i] = acc
    return y * env / np.abs(y).max() * 0.35
def pop():
    n = int(0.09 * SR); tt = np.arange(n) / SR
    f = 950 - 450 * tt / tt[-1]
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 45) * 0.28
W, P = whoosh(), pop()
for c in cues["whoosh"]:
    s0 = max(int((c - 0.3) * SR), 0); sfx[s0:s0 + len(W)] += W[: len(sfx) - s0]
for c in cues["pop"]:
    s0 = int(c * SR); sfx[s0:s0 + len(P)] += P[: len(sfx) - s0]
write(f"{OUT}/sfx.wav", sfx)

# ---- mix: voice clean (already EQ'd/de-essed), music ducked + 1-5 kHz pocket, SFX with pocket
fc = ("[0:a]aresample=48000,pan=stereo|c0=c0|c1=c0,asplit=2[v][sc];"
      "[1:a]volume=-18dB,equalizer=f=2500:t=o:w=1.6:g=-6[m];"
      "[m][sc]sidechaincompress=threshold=0.03:ratio=4:attack=40:release=450:makeup=1,asplit[md][mds];"
      "[2:a]volume=-9dB,equalizer=f=2500:t=o:w=1.4:g=-4,pan=stereo|c0=c0|c1=c0,asplit[s][ss];"
      "[v][md][s]amix=inputs=3:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=9,aresample=48000[a]")
# also the music and SFX stems exactly as they sit in the mix (ducked, EQ'd, levelled), for an NLE at 0 dB
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", VOICE, "-i", f"{OUT}/music.wav",
                "-i", f"{OUT}/sfx.wav", "-filter_complex", fc, "-map", "[a]", "-t", str(DUR),
                "-c:a", "pcm_s16le", f"{OUT}/mix.wav", "-map", "[mds]", "-t", str(DUR), "-c:a", "pcm_s24le",
                f"{OUT}/music_ready.wav", "-map", "[ss]", "-t", str(DUR), "-c:a", "pcm_s24le", f"{OUT}/sfx_ready.wav"], check=True)
print("ok")
