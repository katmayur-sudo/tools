"""Build data + soundtrack for the native 9:16 shorts.

Usage (from videos/beginner-gym-engine/tools): python3 ../shorts/build.py <shorts/script.json> <vo_dir> <out_dir> [short_id ...]
Writes <out_dir>/<id>.json (cues, captions, timing) and <out_dir>/<id>_audio.wav (-14 LUFS).
"""
import json
import subprocess
import sys

import numpy as np
from faster_whisper import WhisperModel

import make_audio as ma
from build_timeline import caption_chunks, find_cues
from transcribe import align, load

LEAD = 0.25          # silence before the voice starts
TAIL = 3.0           # follow / subscribe card
PHOTO = {"v1_three_gears": ("back", "50% 40%"), "v2_goblet_squat": ("side", "55% 40%"),
         "v3_first_plan": ("front", "30% 35%"), "v4_three_mistakes": ("back", "50% 40%"),
         "v5_six_zones_home": ("back", "50% 45%")}
SFX = {   # cue -> sound ("+x" delays it); every other cue gets a swish
    "v1_three_gears": {"three gears": "boom", "gear one": "gear", "ten seconds": "counter", "gear two": "gear",
                       "two minutes": "counter", "burning feeling": "riser", "gear three": "gear", "hours": "ding",
                       "lifting trains": "pop", "easy cardio": "pop", "all three": "boom", "follow": "ding"},
    "v2_goblet_squat": {"new to the gym": "boom", "barbell squat": "error+0.5", "start with this": "boom",
                        "goblet squat": "hit", "dumbbell at your chest": "tick", "back safe": "tick",
                        "feet shoulder": "tick", "sit down": "tick", "knees follow": "tick", "drive the floor": "tick",
                        "heels lift": "error", "three sets": "boom", "biggest muscles": "riser", "save this": "ding"},
    "v3_first_plan": {"stop overthinking": "boom", "all you need": "swish", "monday": "tick", "wednesday": "tick",
                      "friday": "tick", "two to three sets": "pop", "eight to twelve": "pop", "sixty to ninety": "pop",
                      "the secret": "boom", "in the tank": "counter", "add a little": "ding", "that's it": "hit",
                      "twelve weeks": "boom", "save this": "ding"},
    "v4_three_mistakes": {"three mistakes": "boom", "mistake one": "error", "ego grows": "riser",
                          "muscles don't": "thud", "mistake two": "error", "five minutes": "tick",
                          "mistake three": "error", "time to adapt": "ding", "fix your fuel": "hit",
                          "protein": "ding", "sleep": "chime", "guilty": "boom", "comment": "pop"},
    "v5_six_zones_home": {"no gym": "boom", "legs": "hit", "chest": "hit", "arms": "hit", "shoulders": "hit",
                          "abs": "hit", "fat burn": "counter", "round two": "riser", "most people quit": "error",
                          "don't quit": "boom", "your knees": "pop", "slow every rep": "tick",
                          "thirty seconds": "counter", "three rounds": "ding", "two reps": "riser",
                          "that's how": "boom", "save this": "ding"},
}
AVATAR = {"v5_six_zones_home": "left:-184%;top:-14%"}   # follow-card crop of the side photo, when it differs
PUNCH = {"v1_three_gears": ["all three"], "v2_goblet_squat": ["start with this", "three sets"],
         "v3_first_plan": ["the secret", "that's it", "twelve weeks"],
         "v4_three_mistakes": ["mistake one", "mistake two", "mistake three", "guilty"],
         "v5_six_zones_home": ["most people quit", "don't quit", "that's how"]}


def mix(sid, vo, sfx, total, out):
    sr = ma.SR
    n = int(total * sr)
    bank = {"whoosh": ma.whoosh(), "hit": ma.hit(), "pop": ma.pop(), "swish": ma.swish(), "tick": ma.tick(),
            "ding": ma.ding(), "chime": ma.chime(), "error": ma.error(), "boom": ma.boom(), "riser": ma.riser(),
            "gear": ma.gear(), "counter": ma.counter(), "thud": ma.thud(), "click": ma.click(), "bell": ma.bell()}
    fx = np.zeros(n + sr)
    for s in sfx:
        snd = bank[s["type"]]
        i = max(0, int(s["t"] * sr) - (int(0.45 * sr) if s["type"] == "whoosh" else 0))
        fx[i:i + len(snd)] += snd[:len(fx) - i]
    ma.write_wav(f"{out}/{sid}_sfx.wav", fx[:n] * 0.8)
    ma.write_wav(f"{out}/{sid}_music.wav", ma.music(total)[:n])
    ms = int(LEAD * 1000)
    graph = (f"[0:a]aresample={sr},adelay={ms}|{ms},pan=stereo|c0=c0|c1=c0,apad=whole_dur={total},"
             f"loudnorm=I=-16:TP=-2:LRA=7,asplit=2[vo][key];"
             "[1:a]volume=0.6[mus];[mus][key]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=400[duck];"
             "[2:a]volume=0.6[fx];[vo][duck][fx]amix=inputs=3:normalize=0[m];[m]loudnorm=I=-14:TP=-1.5:LRA=9[out]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", vo, "-i", f"{out}/{sid}_music.wav",
                    "-i", f"{out}/{sid}_sfx.wav", "-filter_complex", graph, "-map", "[out]", "-ar", str(sr),
                    "-t", str(total), f"{out}/{sid}_audio.wav"], check=True)


def main():
    script_path, vo_dir, out = sys.argv[1:4]
    conf = json.load(open(script_path))
    model = WhisperModel("base.en", device="cpu", compute_type="int8")
    only = sys.argv[4:]   # optional short ids to build
    for sh in conf["shorts"]:
        if only and sh["id"] not in only:
            continue
        sid, style = sh["id"], sh.get("style", sh["id"])   # a language version reuses its original's style
        vo = f"{vo_dir}/{sid}.mp3"
        segs, _ = model.transcribe(load(vo), word_timestamps=True)
        heard = [{"w": w.word.strip(), "s": w.start, "e": w.end} for s in segs for w in s.words]
        words = align(sh["text"].split(), heard)
        dur = round(LEAD + words[-1]["e"] + 0.6, 3)
        phrase = {k: sh.get("cue_phrases", {}).get(k, k) for k in sh["cues"]}   # cue name -> words spoken
        found = find_cues(words, list(phrase.values()))
        cues = {k: round(found[p] + LEAD, 3) for k, p in phrase.items()}
        names = list(cues)
        hook_end = cues[names[1]] - 0.05
        sfx = [{"t": 0.0, "type": "whoosh"}, {"t": 0.35, "type": "boom"}]
        table = SFX[style]
        for k, t in cues.items():
            kind, _, off = table.get(k, "swish").partition("+")
            if t > 0.5:
                sfx.append({"t": round(t + float(off or 0), 3), "type": kind})
        sfx += [{"t": dur, "type": "whoosh"}, {"t": dur + 1.0, "type": "click"}, {"t": dur + 1.15, "type": "bell"}]
        photo, pos = PHOTO[style]
        data = {"id": sid, "hook": sh["hook"], "photo": photo, "photoPos": pos, "cues": cues, "dur": dur,
                "end": round(dur + TAIL, 3), "hookEnd": round(hook_end, 3),
                "captions": caption_chunks(words, LEAD), "beats": style, "punches": [cues[k] for k in PUNCH[style]], "sfx": sfx}
        if style in AVATAR:
            data["avatar"] = AVATAR[style]
        json.dump(data, open(f"{out}/{sid}.json", "w"), indent=1)
        mix(sid, vo, sfx, data["end"], out)
        print(sid, "voice", round(dur, 1), "s, total", data["end"], "s, hook ends", data["hookEnd"])


if __name__ == "__main__":
    main()
