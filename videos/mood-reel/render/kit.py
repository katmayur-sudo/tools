"""Package a reel as a DaVinci Resolve kit, precise enough for another Claude (or a person) to rebuild the edit.

Usage: python3 kit.py <scratch> <reel.json> <kit_dir> [preview.mp4]
Needs, for the reel's out dir: compose.py --plan (timeline.json, cues.json, captions), compose.py --layers <out>/layers,
and audio.py (music_ready.wav, sfx_ready.wav, mix.wav).
"""
import json, os, shutil, sys

S, RJ, K = sys.argv[1:4]
PREVIEW = sys.argv[4] if len(sys.argv) > 4 else None
HERE = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(RJ)); OUT = f"{S}/{R['out']}"
FPS, W, H = 30, 1080, 1920
CARDS = f"{S}/reel/cards"
NAME = {"s3": "Udaasi-vs-Depression", "s5": "Body-symptoms", "s6": "Organic-causes", "s8": "Mania-Bipolar", "s9": "Treatment",
        "o1": "Title_Udaas-ya-Depressed", "o2": "LowerThird_Name", "o7": "Text_Poochne-se-risk", "o10": "Logo_Save-Share",
        "n2": "Name-card", "e10": "End-card_Save-Share", "shot4_anhedonia": "ANHEDONIA"}
STEP = {"s3": ["base", "+Depression"], "s5": ["base", "+Bhook-kam", "+Neend", "+Thakaan", "+Slow"],
        "s6": ["base", "+Thyroid", "+Steroids", "+Stroke"], "s8": ["base", "+Khushi", "+Neend", "+Bolna", "+Paise", "Bipolar-card"],
        "s9": ["base", "+Dawa", "+Therapy", "+Saath", "+Mood-stabiliser"]}
D = {k: f"{K}/{v}" for k, v in dict(aroll="1_A-roll", clips="2_Card_Clips", face="3_Face_Circle", ov="4_Text_Overlays",
     audio="5_Audio", cap="6_Captions", png="7_Card_PNGs_editable", ref="8_Reference", photos="9_Photos_Credits").items()}
for d in D.values(): os.makedirs(d, exist_ok=True)

fr = lambda t: round(t * FPS)
def tc(f):
    s = f // FPS; return f"00:{s // 60:02d}:{s % 60:02d}:{f % FPS:02d}"

cues = json.load(open(f"{OUT}/cues.json")); TL = json.load(open(f"{OUT}/timeline.json"))
starts = [fr(t) for t in cues["shots"]]; total = starts[-1]
seg = json.load(open(f"{S}/{R['segments']}"))
seg_fr = [fr(b) - fr(a) for a, b in seg]
assert sum(seg_fr) == total, (sum(seg_fr), total)

# ---- media
shutil.copy(f"{S}/{R['video']}", f"{D['aroll']}/A-roll_ORIGINAL_cut_synced.mp4")
voice = R["video"].rsplit("/", 1)[0] + "/voice_cut.wav"
for src, dst in [(f"{S}/{voice}", "1_Voice_clean_(same as A-roll audio).wav"), (f"{OUT}/music_ready.wav", "2_Music_ready.wav"),
                 (f"{OUT}/sfx_ready.wav", "3_SFX_ready.wav"), (f"{OUT}/mix.wav", "4_Final_mix_reference.wav")]:
    shutil.copy(src, f"{D['audio']}/{dst}")
shutil.copy(f"{OUT}/captions.srt", f"{D['cap']}/Captions_Hinglish.srt")
shutil.copy(f"{OUT}/captions.ass", f"{D['cap']}/Captions_word-highlight.ass")
if PREVIEW: shutil.copy(PREVIEW, f"{D['ref']}/Preview_how-it-should-look.mp4")
for r in ["R-01.jpg", "R-02.jpg", "R-04.jpg", "R-05.jpg", "R-06.png", "R-08.jpg"]:
    shutil.copy(f"{S}/reel/assets/{r}", f"{D['photos']}/{r}")
shutil.copy(f"{HERE}/../CREDITS.md", f"{D['photos']}/CREDITS.md")

clips = []  # (track, file, rec_in, rec_out, extra)
for n, sh in enumerate(R["shots"]):
    tag, a, b = f"S{n + 1:02d}", starts[n], starts[n + 1]
    if sh["kind"] == "pip":
        c = sh["card"]
        for i in range(len(sh["states"]) + 1):
            shutil.copy(f"{CARDS}/{c}_{i}.png", f"{D['png']}/{tag}_{NAME[c]}_{i}_{STEP[c][i]}.png")
        shutil.copy(f"{OUT}/layers/{tag}_{c}_card.mp4", f"{D['clips']}/{tag}_{NAME[c]}.mp4")
        shutil.copy(f"{OUT}/layers/{tag}_face_circle.mov", f"{D['face']}/{tag}_face_circle.mov")
        clips.append(("V2", f"2_Card_Clips/{tag}_{NAME[c]}.mp4", a, b, {}))
        clips.append(("V3", f"3_Face_Circle/{tag}_face_circle.mov", a, b, {"Pan": 350, "Tilt": 700}))
    elif sh["kind"] == "card":
        base = os.path.basename(sh["file"]); key = base.replace("_0.png", "").replace(".png", "")
        shutil.copy(f"{S}/{sh['file']}", f"{D['png']}/{tag}_{NAME[key]}.png")
        shutil.copy(f"{OUT}/layers/{tag}_{key}_card.mp4", f"{D['clips']}/{tag}_{NAME[key]}.mp4")
        clips.append(("V2", f"2_Card_Clips/{tag}_{NAME[key]}.mp4", a, b, {}))
for e in TL:  # overlays on full-face shots
    if e["track"].startswith("V3 overlay"):
        o = e["file"].replace("_0.png", ""); n = next(i for i in range(len(starts) - 1) if starts[i] <= fr(e["start"]) < starts[i + 1])
        name = f"S{n + 1:02d}_{NAME[o]}.png"
        shutil.copy(f"{CARDS}/{e['file']}", f"{D['ov']}/{name}")
        clips.append(("V4", f"4_Text_Overlays/{name}", fr(e["start"]), fr(e["end"]), {"fade_in_frames": 9}))

# A-roll on V1 as one piece per cut segment (each cut = a real edit point), alternating punch-in on full-face shots
full = [(starts[n], starts[n + 1]) for n, sh in enumerate(R["shots"]) if sh["kind"] == "full"]
aroll, f0 = [], 0
for k, n in enumerate(seg_fr):
    vis = any(a < f0 + n and f0 < b for a, b in full)
    aroll.append({"src_in": f0, "src_out": f0 + n, "rec_in": f0, "rec_out": f0 + n, "zoom": 1.07 if (k % 2 and vis) else 1.0})
    f0 += n

spec = {
 "about": "Frame-exact edit of the reel. Frames at 30 fps from the timeline start; *_out frames are exclusive "
          "(a clip with rec_in 0, rec_out 15 covers frames 0..14 = 15 frames). Every media file is already the "
          "exact length of its slot, so src_in is 0 for everything except the A-roll pieces.",
 "timeline": {"width": W, "height": H, "fps": FPS, "frames": total, "duration": tc(total)},
 "tracks": {
  "V1": "A-roll pieces (video + its linked clean-voice audio on A1)",
  "V2": "card clips (full screen, opaque): they hide the A-roll; the A-roll audio keeps playing underneath",
  "V3": "face circle clips (340x340 with alpha), Position X +350, Y +700 (pixels from centre, up = +), Zoom 1.0",
  "V4": "text overlay PNGs with alpha, full frame, Position 0,0",
  "A1": "A-roll audio (clean voice), 0 dB",
  "A2": "5_Audio/2_Music_ready.wav at 0 dB, from frame 0 (already ducked under the voice and EQ'd)",
  "A3": "5_Audio/3_SFX_ready.wav at 0 dB, from frame 0",
  "ST1": "6_Captions/Captions_Hinglish.srt from frame 0",
  "master": "-1 dB on the master bus gives -14 LUFS integrated, true peak about -2 dBTP (Instagram level)"},
 "aroll": {"file": "1_A-roll/A-roll_ORIGINAL_cut_synced.mp4", "pieces": aroll},
 "clips": [{"track": t, "file": f, "src_in": 0, "src_out": b - a, "rec_in": a, "rec_out": b, "tc_in": tc(a), "tc_out": tc(b), **x}
           for t, f, a, b, x in sorted(clips, key=lambda c: (c[2], c[0]))],
 "audio": [{"track": "A2", "file": "5_Audio/2_Music_ready.wav", "rec_in": 0, "rec_out": total},
           {"track": "A3", "file": "5_Audio/3_SFX_ready.wav", "rec_in": 0, "rec_out": total}],
 "subtitles": {"file": "6_Captions/Captions_Hinglish.srt", "rec_in": 0},
 "push_in": {"about": "Optional (the script can't keyframe): on each full-face shot, zoom rises linearly by +0.04 "
             "from the shot's first to last frame, on top of each piece's zoom. Keyframe Inspector > Zoom at both ends.",
             "shots": [{"rec_in": a, "rec_out": b, "tc_in": tc(a), "tc_out": tc(b)} for a, b in full]},
 "markers": [{"frame": starts[n], "tc": tc(starts[n]), "name": f"S{n + 1:02d} {sh['kind']}"} for n, sh in enumerate(R["shots"])],
}
json.dump(spec, open(f"{K}/timeline_resolve.json", "w"), indent=1, ensure_ascii=False)
shutil.copy(f"{HERE}/build_timeline_in_resolve.py", f"{K}/build_timeline_in_resolve.py")

# ---- self-checks: every slot filled exactly, no overlaps on a track
assert aroll[-1]["rec_out"] == total
v2 = sorted((c["rec_in"], c["rec_out"]) for c in spec["clips"] if c["track"] == "V2")
assert all(a[1] <= b[0] for a, b in zip(v2, v2[1:])), "V2 overlap"

# ---- human guide
shot_rows = "\n".join(f"| S{n + 1:02d} | {tc(starts[n])} | {tc(starts[n + 1])} | "
                      f"{ {'full': 'Full face (A-roll visible)', 'pip': 'Card clip + face circle', 'card': 'Card only, voice continues'}[sh['kind']]} |"
                      for n, sh in enumerate(R["shots"]))
clip_rows = "\n".join(f"| {c['tc_in']} | {c['tc_out']} | {c['track']} | {c['file']} |" for c in spec["clips"])
guide = f"""# DaVinci Resolve kit

**Timeline:** 1080 x 1920, 30 fps, {tc(total)} ({total} frames). Everything is placed from 00:00:00:00.
Frame-exact data for automation: `timeline_resolve.json`. Builder script for Resolve: `build_timeline_in_resolve.py`.
Instructions for the Claude on your computer: `INSTRUCTIONS_FOR_CLAUDE.md`.

## Folders
| Folder | What |
|---|---|
| 1_A-roll | Your video, original colour and quality, no grade. Pauses, breaths, retakes and false starts removed, every scripted word kept once, **sound synced to your lips**, clean voice inside. |
| 2_Card_Clips | Every card shot as one ready clip with its pop-ins and slow push baked in (exact length of its slot). |
| 3_Face_Circle | Your face in a circle with a white ring and a transparent background, one clip per card shot, already in sync. |
| 4_Text_Overlays | See-through PNGs for the full-face shots. |
| 5_Audio | Voice (same as the A-roll audio), music and SFX ready to sit at 0 dB (already ducked and EQ'd), and my final mix for reference. |
| 6_Captions | .srt for Resolve (File > Import > Subtitle). The .ass has word-by-word yellow highlight, for other tools. |
| 7_Card_PNGs_editable | The single card images and build-up states, if you want to restyle or re-time the cards yourself. |
| 8_Reference | My preview render: how the finished reel should look. |
| 9_Photos_Credits | Photos used in the cards. CC BY photos must be credited in the Instagram caption (CREDITS.md). |

## Tracks
| Track | Content |
|---|---|
| V1 | A-roll, cut into {len(aroll)} pieces (one per edit). On full-face shots alternate pieces are zoomed 107% to hide the jump cuts |
| V2 | Card clips. They cover the A-roll **picture only**: your voice continues underneath |
| V3 | Face circle on card shots: **Position X 350, Y 700**, Zoom 1.0 |
| V4 | Text overlays (fade in over 9 frames) |
| (optional) | Slow push-in on full-face shots: keyframe Zoom +0.04 from first to last frame of each full-face shot |
| A1 | A-roll audio = clean voice, 0 dB |
| A2 | 2_Music_ready.wav, 0 dB |
| A3 | 3_SFX_ready.wav, 0 dB |
| Subtitles | Captions_Hinglish.srt |
| Master | -1 dB, which gives -14 LUFS (Instagram level) |

## Shots
| Shot | In | Out | What shows |
|---|---|---|---|
{shot_rows}

## Every clip on V2 to V4 (timecode HH:MM:SS:FF; Out = first frame after the clip)
| In | Out | Track | File |
|---|---|---|---|
{clip_rows}
"""
open(f"{K}/EDIT_GUIDE.md", "w").write(guide + R.get("guide_notes", ""))
shutil.copy(f"{HERE}/INSTRUCTIONS_FOR_CLAUDE.md", f"{K}/INSTRUCTIONS_FOR_CLAUDE.md")
print("clips", len(spec["clips"]), "aroll pieces", len(aroll), "frames", total)
