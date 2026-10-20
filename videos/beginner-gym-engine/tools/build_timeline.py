"""Turn the script, voice-over durations and word timings into timeline.json for the renderer.

Usage: python3 build_timeline.py <script.json> <words.json> <vo_dir> <out_timeline.json>

Every animation beat is keyed to the moment a word is spoken ("cues"), so visuals land on the
voice instead of on guessed timestamps.
"""
import json
import re
import subprocess
import sys

GAP = 0.45          # silence between voice-over sections
CHAPTER = 1.9       # chapter title cards (no voice)
STINGER = 1.5       # exercise number stingers (no voice)
END_CARD = 12.0       # YouTube end-screen elements need 5-20 s
LEAD_IN = 0.35

CHAPTERS = {
    "s01_engine": ("PART 1", "The Engine"),
    "s03_warmup": ("PART 2", "The Ignition Sequence"),
    "s13_plan": ("PART 3", "The Plan"),
}

# phrase -> cue name, searched in order through each section's words
CUES = {
    "s00_hook": ["engine", "first day", "wrong exercises", "too much", "no plan", "in the next",
                 "engine starts", "eight exercises", "weekly plan"],
    "s01_engine": ["metabolism", "sixty", "sleep", "resting metabolic", "ten percent", "the rest is",
                   "muscle", "kilogram of muscle", "three times", "small", "does all the work",
                   "every single day"],
    "s02_ignition": ["three gears", "gear one", "ten seconds", "gear two", "two minutes", "the burn",
                     "gear three", "hours", "all three gears", "bonus", "pulls sugar", "afterburn",
                     "mitochondria. more", "bigger"],
    "s03_warmup": ["five minutes", "lightly sweating", "ten bodyweight squats", "ten arm circles",
                   "ten hip hinges", "practice set", "warm muscles", "joints", "first working set"],
    "s12_finisher": ["ten minutes", "zone two", "talk", "sing", "gear three", "mitochondria"],
    "s13_plan": ["three days", "monday", "wednesday", "friday", "two to three sets", "eight to twelve",
                 "sixty to ninety", "fifty minutes", "how heavy", "in the tank", "same on the last",
                 "first two weeks", "double progression", "add a little weight", "steady increase"],
    "s14_fuel": ["fuel", "protein", "sleep", "steps", "everyday movement"],
    "s15_mistakes": ["one:", "two:", "three:", "results"],
    "s17_subscribe": ["subscribe", "dr mak"],
    "s16_outro": ["ignition sequence", "warm up", "eight exercises", "cardio", "three days",
                  "start light", "consistent", "engine build", "medical", "save this", "next one"],
}
EXERCISE_CUES = ["exercise", "the common mistake", "three"]

EXERCISES = {
    "s04_goblet_squat": dict(pose="squat", img="goblet", muscles=["thigh", "glute"],
                             mistake="Heels lifting", fix="Sit back, weight in mid-foot"),
    "s05_rdl": dict(pose="rdl", img="rdl", muscles=["hamstring", "glute"],
                    mistake="Rounding your back", fix="Stop where your hips stop"),
    "s06_pushup": dict(pose="pushup", img="bench", muscles=["chest", "upperarm"],
                       mistake="Sagging hips", fix="Squeeze glutes and abs"),
    "s07_row": dict(pose="row", img="row", muscles=["back", "upperarm"],
                    mistake="Twisting to swing it up", fix="Too heavy? Go lighter"),
    "s08_press": dict(pose="press", img="press", muscles=["shoulder", "upperarm"],
                      mistake="Arching your lower back", fix="Ribs down, back on the pad"),
    "s09_stepup": dict(pose="stepup", img="stepup", muscles=["thigh", "glute"],
                       mistake="Pushing off the back foot", fix="Front leg does the work"),
    "s10_carry": dict(pose="carry", img="carry", muscles=["forearm", "core", "back"],
                      mistake="Leaning or rounding", fix="Balance a book on your head"),
    "s11_deadbug": dict(pose="deadbug", img="deadbug", muscles=["core"],
                        mistake="Lower back lifting", fix="Only reach while it stays flat"),
}

# sound for each cue (default "pop"); "+0.25" style offsets let a sound land on the animation
CUE_SFX = {
    "s00_hook": {"engine": "boom", "wrong exercises": "error+0.25", "too much": "error+0.25",
                 "no plan": "error+0.25", "in the next": "swish", "engine starts": "pop",
                 "eight exercises": "pop", "weekly plan": "pop"},
    "s01_engine": {"sixty": "counter", "ten percent": "tick", "the rest is": "tick", "sleep": "chime",
                   "kilogram of muscle": "counter", "three times": "boom", "does all the work": "ding"},
    "s02_ignition": {"gear one": "gear", "gear two": "gear", "gear three": "gear", "bonus": "ding",
                     "afterburn": "riser", "mitochondria. more": "chime", "bigger": "ding"},
    "s03_warmup": {"five minutes": "tick", "ten bodyweight squats": "tick", "ten arm circles": "tick",
                   "ten hip hinges": "tick", "practice set": "tick", "warm muscles": "pop",
                   "joints": "pop", "first working set": "pop"},
    "s12_finisher": {"zone two": "ding", "sing": "error"},
    "s13_plan": {"monday": "tick", "wednesday": "tick", "friday": "tick", "two to three sets": "pop",
                 "eight to twelve": "pop", "sixty to ninety": "pop", "fifty minutes": "ding",
                 "in the tank": "counter", "double progression": "riser", "steady increase": "ding"},
    "s14_fuel": {"protein": "ding", "sleep": "chime", "steps": "counter", "everyday movement": "pop"},
    "s15_mistakes": {"one:": "error", "two:": "error", "three:": "error", "results": "ding"},
    "s16_outro": {"warm up": "tick", "eight exercises": "tick", "cardio": "tick", "three days": "tick",
                  "consistent": "boom", "save this": "ding"},
    "s17_subscribe": {"subscribe": "click+0.55", "dr mak": "bell+0.15"},
}
# cues that also get a camera punch-in (zoom kick)
PUNCH = {"s00_hook": ["engine"], "s01_engine": ["three times", "does all the work"],
         "s02_ignition": ["three gears", "afterburn", "bigger"], "s13_plan": ["how heavy", "steady increase"],
         "s15_mistakes": ["one:", "two:", "three:"], "s16_outro": ["consistent"]}

HIGHLIGHT = {"engine", "metabolism", "muscle", "gears", "mitochondria", "afterburn", "sugar",
             "warm", "squat", "deadlift", "push-up", "row", "press", "step-up", "carry", "bug",
             "mistake", "protein", "sleep", "steps", "plan", "consistent", "light", "heavy",
             "progression", "zone", "three", "eight", "ten", "fifty", "insulin", "oxygen"}


def norm(w):
    return re.sub(r"[^a-z0-9]", "", w.lower())


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
                          "csv=p=0", path], capture_output=True, text=True, check=True).stdout
    return float(out)


def find_cues(words, phrases):
    cues, start = {}, 0
    toks = [norm(w["w"]) for w in words]
    for ph in phrases:
        target = [norm(p) for p in ph.split()]
        hit = None
        for i in range(start, len(toks) - len(target) + 1):
            if toks[i:i + len(target)] == target:
                hit = i
                break
        if hit is None:  # fall back to a search from the beginning
            for i in range(0, len(toks) - len(target) + 1):
                if toks[i:i + len(target)] == target:
                    hit = i
                    break
        if hit is None:
            raise SystemExit(f"cue not found: {ph!r}")
        cues[ph] = round(words[hit]["s"], 3)
        start = hit + 1
    return cues


def caption_chunks(words, offset):
    chunks, cur = [], []
    for w in words:
        cur.append(w)
        end_punct = w["w"][-1] in ".,:?!;"
        if len(cur) >= 4 or (end_punct and len(cur) >= 2) or w["w"][-1] in ".?!":
            chunks.append(cur)
            cur = []
    if cur:
        chunks.append(cur)
    out = []
    for c in chunks:
        hl = -1
        for i, w in enumerate(c):
            if norm(w["w"]).rstrip("s") in HIGHLIGHT or norm(w["w"]) in HIGHLIGHT:
                hl = i
                break
        out.append({"s": round(c[0]["s"] + offset, 3), "e": round(c[-1]["e"] + offset, 3),
                    "words": [w["w"] for w in c], "hl": hl})
    for a, b in zip(out, out[1:]):  # hold each chunk until the next one starts (max +0.6s)
        a["e"] = round(min(b["s"], a["e"] + 0.6), 3)
    return out


def main():
    script_path, words_path, vo_dir, out_path = sys.argv[1:5]
    script = json.load(open(script_path))
    words = json.load(open(words_path))
    t = LEAD_IN
    scenes, captions, sfx, audio, punches = [], [], [], [], []
    n_ex = 0
    for sec in script["sections"]:
        sid = sec["id"]
        if sid in CHAPTERS:
            label, title = CHAPTERS[sid]
            scenes.append({"id": f"chapter_{sid}", "kind": "chapter", "start": round(t, 3),
                           "end": round(t + CHAPTER, 3), "label": label, "title": title})
            sfx.append({"t": round(t - 1.0, 3), "type": "riser"})
            sfx.append({"t": round(t, 3), "type": "whoosh"})
            sfx.append({"t": round(t + 0.35, 3), "type": "hit"})
            t += CHAPTER
        if sid in EXERCISES:
            n_ex += 1
            scenes.append({"id": f"stinger_{sid}", "kind": "stinger", "start": round(t, 3),
                           "end": round(t + STINGER, 3), "n": n_ex, "name": sec["name"]})
            sfx.append({"t": round(t, 3), "type": "whoosh"})
            sfx.append({"t": round(t + 0.3, 3), "type": "hit"})
            t += STINGER
        dur = duration(f"{vo_dir}/{sid}.mp3")
        w = words[sid]
        phrases = CUES.get(sid, EXERCISE_CUES if sid in EXERCISES else [])
        cues = {k: round(v + t, 3) for k, v in find_cues(w, phrases).items()}
        length = max(dur + GAP, END_CARD) if sec["kind"] == "endcard" else dur + GAP
        scene = {"id": sid, "kind": sec["kind"], "start": round(t, 3), "vo": round(t, 3),
                 "end": round(t + length, 3), "cues": cues}
        if sec["kind"] == "endcard":
            scene["channel"] = script.get("channel", {})
        if sid in EXERCISES:
            ex = EXERCISES[sid]
            scene.update(n=n_ex, name=sec["name"], target=sec["target"], dose=sec["dose"],
                         steps=sec["cues"], **ex)
            # spread the form cues across the "how to" part, before the mistake
            a = cues["exercise"] + 3.0
            b = cues["the common mistake"] - 0.3
            scene["stepTimes"] = [round(a + (b - a) * i / len(sec["cues"]), 3)
                                  for i in range(len(sec["cues"]))]
        if sid != "s00_hook":
            sfx.append({"t": round(t, 3), "type": "swish"})
        scenes.append(scene)
        audio.append({"file": f"{sid}.mp3", "t": round(t, 3)})
        if sec["kind"] != "endcard":
            captions += caption_chunks(w, t)
        table = CUE_SFX.get(sid, {})
        if sid in EXERCISES:
            table = {"the common mistake": "error+0.1", "three": "ding"}
            for st in scene["stepTimes"]:
                sfx.append({"t": st, "type": "tick"})
            # a soft thud on every rep of the animated figure (2.6 s period, bottom of the rep)
            r = t + 1.3
            while r < t + dur:
                sfx.append({"t": round(r, 3), "type": "thud"})
                r += 2.6
        for k, v in cues.items():
            kind, _, off = table.get(k, "pop").partition("+")
            sfx.append({"t": round(v + float(off or 0), 3), "type": kind})
        for k in PUNCH.get(sid, []):
            punches.append(cues[k])
        if sec["kind"] == "finisher":
            b = t
            while b < t + dur:
                sfx.append({"t": round(b, 3), "type": "heartbeat"})
                b += 0.85
        t += length
    # thin out light sounds so they never pile up closer than 0.3s apart
    sfx.sort(key=lambda s: s["t"])
    kept = []
    light = {"pop", "tick", "thud"}
    for s in sfx:
        if s["type"] in light and kept and s["t"] - kept[-1]["t"] < 0.3:
            continue
        kept.append(s)
    json.dump({"fps": 30, "width": 1920, "height": 1080, "duration": round(t, 3),
               "scenes": scenes, "captions": captions, "sfx": kept, "audio": audio,
               "punches": sorted(punches)},
              open(out_path, "w"), indent=1)
    print(f"duration {t:.1f}s ({t / 60:.2f} min), scenes {len(scenes)}, captions {len(captions)}")


if __name__ == "__main__":
    main()
