"""Sound design: voice chain + ducked, pocketed music bed + SFX cues, mastered to -14 LUFS.
usage: mix.py mix.json [visual.mp4]   -> out/mix.wav, out/mix.m4a, out/mix_with_cut.mp4 (+ out/final.mp4 with a visual)
mix.json: {"voice": "cut/cut.mp4", "music": "music.wav", "sfx_dir": "sfx", "out": "audio",
  "bpm": 120, "beat_phase": 0.0,            # track time of any beat (beat.py phase)
  "beat_word": 61.70,                       # reel time that must land on a beat (or give "music_offset")
  "music_start_min": 8.0, "music_gain": 0.32,
  "dips": [[15.9, 16.95]],                  # extra 0.4-deep music dips under masked words (reel time)
  "cues": [[5.02, "whoosh", -10], [6.28, "click", -6], [9.27, "pop", -9, 0.22]],   # [t, file, dB, trim?]
  "vocal": "default" | "lav_preset" | "<custom ffmpeg chain applied before the de-esser>",
  "warp": "warp.json" (optional: cue/dip/beat times authored on an older cut)}"""
import json, os, subprocess, sys
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))  # -I mode skips the script dir
from common import FF, duration

C = json.load(open(sys.argv[1])); VIS = sys.argv[2] if len(sys.argv) > 2 else None
WARP = json.load(open(C["warp"])) if C.get("warp") else None


def M(t):
    if not WARP: return t
    for oa, ob, na, nb in WARP:
        if t < ob: return min(nb, na + max(0, t - oa))
    return WARP[-1][3]


VOICE, OUT = C["voice"], C.get("out", "audio"); os.makedirs(f"{OUT}/bus", exist_ok=True)
END = round(duration(VOICE), 3)
P = 60 / C.get("bpm", 120)
if "music_offset" in C:
    OFF = C["music_offset"]
else:
    lo, ph, T = C.get("music_start_min", 8.0), C.get("beat_phase", 0.0), M(C.get("beat_word", 0.0))
    OFF = lo + ((ph - T - lo) % P)          # (t + OFF) hits a beat at t = beat_word
PEAK = {"whoosh": .62, "whoosh2": .80, "thud": .17, "impact": .17, "riser": 2.51}
cues = [(max(0.0, M(c[0]) - PEAK.get(c[1], 0)), c[1], c[2], c[3] if len(c) > 3 else None) for c in C.get("cues", [])]
DIP = [(M(a), M(b)) for a, b in C.get("dips", [])]
DIP_EXPR = "1" if not DIP else "if(isnan(t),1,1-0.4*(" + "+".join(
    f"clip((t-{x})/0.12,0,1)*clip(({y}-t)/0.12,0,1)" for x, y in DIP) + "))"
fmt = "aformat=sample_rates=48000:channel_layouts=stereo"

LAV = ("highpass=f=80:p=2,highpass=f=80:p=2,bass=f=118:g=6,equalizer=f=316:width_type=h:width=210:g=-3,"
       "equalizer=f=2796:width_type=h:width=1398:g=2.2,treble=f=18662:g=5.1,afftdn=nr=8:nf=-45:tn=1")
MB = ("[vd]acrossover=split=80 250 10000:order=8th[b1][b2][b3][b4];"
      "[b1]acompressor=threshold=0.0631:ratio=2.5:attack=1:release=200:makeup=2.239[c1];"
      "[b2]acompressor=threshold=0.1259:ratio=2:attack=1:release=200:makeup=1.995[c2];"
      "[c1][c2][b3][b4]amix=inputs=4:normalize=0,alimiter=limit=1:attack=4:release=500:level=disabled[mb]")
TAIL = f"deesser=i=0.5:m=0.5:f=0.5:s=o,acompressor=threshold=0.09:ratio=3:attack=8:release=120:makeup=1.6,apad=whole_dur={END},atrim=0:{END}[o]"
vocal = C.get("vocal", "default")
if vocal == "lav_preset":
    VOX = f"[0:a]{fmt},{LAV}[vd];{MB};[mb]{TAIL}"
elif vocal == "default":
    VOX = f"[0:a]{fmt},highpass=f=80,equalizer=f=250:width_type=o:width=1.2:g=-1.5,equalizer=f=3000:width_type=o:width=1.4:g=2.5,{TAIL}"
else:
    VOX = f"[0:a]{fmt},{vocal},{TAIL}"


def run(ins, graph, out):
    subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-y", *ins, "-filter_complex", graph, "-map", "[o]",
                    "-c:a", "pcm_s24le", out], check=True)
    d = duration(out); assert abs(d - END) < 0.1, f"{out}: {d:.2f}s, expected {END:.2f}s"


B = f"{OUT}/bus"
run(["-i", VOICE], VOX, f"{B}/voice.wav")
if C.get("music"):
    run(["-i", C["music"], "-i", f"{B}/voice.wav"], ";".join([
        f"[0:a]{fmt},atrim={OFF}:{OFF + END},asetpts=PTS-STARTPTS,"
        "equalizer=f=1200:width_type=o:width=1.2:g=-3,equalizer=f=2600:width_type=o:width=1.2:g=-6,"
        f"equalizer=f=4800:width_type=o:width=1.2:g=-4,volume='{DIP_EXPR}':eval=frame,afade=t=in:d=0.08,"
        f"afade=t=out:st={END - 1.4}:d=1.4,volume={C.get('music_gain', 0.32)},apad=whole_dur={END}[mus]",
        f"[1:a]{fmt}[key]",
        f"[mus][key]sidechaincompress=threshold=0.03:ratio=8:attack=15:release=350:makeup=1,apad=whole_dur={END},atrim=0:{END}[o]"]),
        f"{B}/music.wav")
else:
    run(["-f", "lavfi", "-i", f"anullsrc=r=48000:cl=stereo:d={END}"], "[0:a]anull[o]", f"{B}/music.wav")
if cues:
    ins, parts = [], []
    for n, (t, f, db, trim) in enumerate(cues):
        ins += ["-i", f"{C.get('sfx_dir', 'sfx')}/{f}.wav"]
        tr = f"atrim=0:{trim},afade=t=out:st={trim - 0.04}:d=0.04," if trim else ""
        parts.append(f"[{n}:a]{fmt},{tr}volume={db}dB,adelay={int(t * 1000)}:all=1[s{n}]")
    parts.append("".join(f"[s{n}]" for n in range(len(cues))) + f"amix=inputs={len(cues)}:duration=longest:normalize=0,"
                 "equalizer=f=1500:width_type=o:width=1.4:g=-2.5,equalizer=f=3200:width_type=o:width=1.4:g=-4,"
                 f"apad=whole_dur={END},atrim=0:{END}[o]")
    run(ins, ";".join(parts), f"{B}/sfx.wav")
else:
    run(["-f", "lavfi", "-i", f"anullsrc=r=48000:cl=stereo:d={END}"], "[0:a]anull[o]", f"{B}/sfx.wav")

mix = f"[0:a][1:a][2:a]amix=inputs=3:duration=longest:normalize=0,atrim=0:{END},loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[o]"
subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-y", *sum([["-i", f"{B}/{b}.wav"] for b in ["voice", "music", "sfx"]], []),
                "-filter_complex", mix, "-map", "[o]", "-c:a", "pcm_s24le", f"{OUT}/mix.wav"], check=True)
subprocess.run([FF, "-v", "error", "-y", "-i", f"{OUT}/mix.wav", "-c:a", "aac", "-b:a", "256k", f"{OUT}/mix.m4a"], check=True)
for v, name in [(VOICE, "mix_with_cut.mp4")] + ([(VIS, "final.mp4")] if VIS else []):
    subprocess.run([FF, "-v", "error", "-y", "-i", v, "-i", f"{OUT}/mix.wav", "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-shortest", "-movflags", "+faststart", f"{OUT}/{name}"], check=True)
print(f"cues {len(cues)}, music offset {OFF:.2f}s ->", OUT)
