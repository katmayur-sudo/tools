"""DaVinci Resolve kit for the split-screen case-taking reel (no music; the owner finishes the edit in Resolve).

Usage: python3 kit_split.py <cut_dir> <work_dir> <kit_dir> <cards_9x16_dir> <title_card.png>
cut_dir: aroll_fixed.mp4, voice_cut.wav, aligned_cut.json, offcam_kit.json.
work_dir: plan.json, captions.srt, Board_animation_1080x960.mp4, board_states.json (from compose_split.py),
          plus A-roll_logo_background_1080x960.mp4 and top_alpha.mp4 in its parent.
"""
import json, os, shutil, sys

CUT, WK, K, CARDS, TITLE = sys.argv[1:6]
HERE = os.path.dirname(os.path.abspath(__file__))
FPS = 30
for d in ["1_A-roll", "2_Board", "3_Cards", "4_Audio", "5_Captions"]: os.makedirs(f"{K}/{d}", exist_ok=True)
fr = lambda t: round(t * FPS)
def tc(f): s = f // FPS; return f"00:{s // 60:02d}:{s % 60:02d}:{f % FPS:02d}"

top = f"{os.path.dirname(WK)}/A-roll_logo_background_1080x960.mp4"
shutil.copy(top, f"{K}/1_A-roll/A-roll_logo_background_1080x960.mp4")
shutil.copy(f"{CUT}/aroll_fixed.mp4", f"{K}/1_A-roll/A-roll_full_frame_original_background.mp4")
shutil.copy(f"{os.path.dirname(WK)}/top_alpha.mp4", f"{K}/1_A-roll/A-roll_person_matte_1080x960.mp4")
shutil.copy(f"{WK}/Board_animation_1080x960.mp4", f"{K}/2_Board/Board_animation_1080x960.mp4")
shutil.copy(f"{CUT}/voice_cut.wav", f"{K}/4_Audio/Voice_clean.wav")
shutil.copy(f"{WK}/captions.srt", f"{K}/5_Captions/Captions_Hinglish.srt")
titles = {"83": "Physician ki 4 qualities", "84": "Suno, roko mat", "85": "Har symptom, nayi line", "86": "Har symptom complete karo",
          "87": "Leading questions nahi", "88": "Jo chhoota, general sawaal", "89": "Phir special sawaal", "90": "Doctor ka apna observation"}
for n in range(83, 91):
    shutil.copy(f"{CARDS}/slide_{n - 82:02d}.png", f"{K}/3_Cards/Card_{n}.png")
shutil.copy(TITLE, f"{K}/3_Cards/Title_card_83-90.png")

plan = json.load(open(f"{WK}/plan.json")); NF = plan["frames"]
W = json.load(open(f"{CUT}/aligned_cut.json"))
cards = [(f"3_Cards/Card_{c[3]}.png", fr(c[1]), fr(c[2]), c[3]) for c in plan["cards"] if c[3] != "title"]

# board items: when each line starts writing (same table compose_split.py used)
BOARD = {"q1": (40, "No prejudice"), "q2": (50, "Senses"), "q3": (59, "Attention"), "q4": (69, "Fidelity"), "p1": (80, '1. "Sar dard rehta hai"'),
         "chup": (85, "Chup · roko mat"), "words": (93, "(uske words mein likho)"), "line2": (97, "2. ........"), "gap": (103, "gap chhodo"),
         "c1": (148, "Kab se?"), "c2": (150, "Kaisa?"), "c3": (151, "Kahan?"), "c4": (152, "Kitni der?"), "c5": (154, "Kab badhta?"),
         "x1": (172, '✗ "Dhoop mein badhta?"'), "v1": (178, '✓ "Kis cheez se badhta?"'), "ticks": (188, "Gaps ticked"),
         "gq": (192, 'General: "Neend kaisi hai?"'), "sq": (199, 'Special: "Neend mein bolte ho?"'),
         "d1": (228, "Chehra"), "d2": (229, "Mood"), "d3": (230, "Zubaan"), "d4": (231, "Pulse"), "d5": (239, "Behaviour"), "end": (252, "Story + observation = case-taking")}
STEPS = [(0, "Hook"), (16, "Intro: Aphorism 83–90"), (36, "§83 Physician ki 4 qualities"), (78, "§84 Suno, roko mat"), (97, "§85 Nayi line"),
         (135, "§86 Complete karo"), (157, "§87 Leading questions nahi"), (185, "§88 General sawaal"), (195, "§89 Special sawaal"), (205, "§90 Doctor observes"), (247, "End")]
off = json.load(open(f"{CUT}/offcam_kit.json"))

spec = {
 "about": "Frame-exact split-screen reel, 30 fps, frames from the timeline start; *_out exclusive. Every media file is already the full "
          "reel length or its exact slot, so src_in is 0. Top half = speaker with logo background, bottom half = self-writing board, "
          "cards full screen (no face, no board) while the voice continues. No music.",
 "timeline": {"width": 1080, "height": 1920, "fps": FPS, "frames": NF, "duration": tc(NF)},
 "tracks": {"V1": "A-roll with logo background, 1080x960, Position Y +480 (top half)", "V2": "Board animation, 1080x960, Position Y -480 (bottom half)",
            "V3": "Aphorism cards 1080x1920, full screen, cover everything", "A1": "Voice_clean.wav (also inside the A-roll file)", "ST1": "Captions_Hinglish.srt"},
 "aroll": {"file": "1_A-roll/A-roll_logo_background_1080x960.mp4", "pieces": []},
 "clips": [{"track": "V1", "file": "1_A-roll/A-roll_logo_background_1080x960.mp4", "src_in": 0, "src_out": NF, "rec_in": 0, "rec_out": NF, "tc_in": tc(0), "tc_out": tc(NF), "Pan": 0, "Tilt": 480},
           {"track": "V2", "file": "2_Board/Board_animation_1080x960.mp4", "src_in": 0, "src_out": NF, "rec_in": 0, "rec_out": NF, "tc_in": tc(0), "tc_out": tc(NF), "Pan": 0, "Tilt": -480}]
          + [{"track": "V3", "file": f, "src_in": 0, "src_out": b - a, "rec_in": a, "rec_out": b, "tc_in": tc(a), "tc_out": tc(b), "aphorism": n} for f, a, b, n in cards],
 "audio": [{"track": "A1", "file": "4_Audio/Voice_clean.wav", "rec_in": 0, "rec_out": NF}],
 "subtitles": {"file": "5_Captions/Captions_Hinglish.srt", "rec_in": 0},
 "markers": [{"frame": fr(W[i]["s"] - 0.15) if i else 0, "tc": tc(fr(W[i]["s"] - 0.15) if i else 0), "name": name} for i, name in STEPS],
 "board_items": [{"text": t, "frame": fr(W[i]["s"] - 0.05), "tc": tc(fr(W[i]["s"] - 0.05))} for _, (i, t) in BOARD.items()],
 "off_camera": [{"tc_in": tc(fr(o["in"])), "tc_out": tc(fr(o["out"])), "frame_in": fr(o["in"]), "frame_out": fr(o["out"]), "during_words": o["during"]} for o in off],
}
json.dump(spec, open(f"{K}/timeline_resolve.json", "w"), indent=1, ensure_ascii=False)
shutil.copy(f"{HERE}/../mood-reel/render/build_timeline_in_resolve.py", f"{K}/build_timeline_in_resolve.py")

rows = lambda xs: "\n".join(xs)
guide = f"""# DaVinci Resolve kit: Case-taking (Organon §83–90)

**Timeline:** 1080 x 1920, 30 fps, {tc(NF)} ({NF} frames). No music.
**Sync:** the A-roll uses your phone's own audio/picture timing (the version that looked right on your phone). The voice is cleaned; "compare karo" was replaced with your own "complete karo".

## Files
| Folder | File | Use |
|---|---|---|
| 1_A-roll | A-roll_logo_background_1080x960.mp4 | **Main.** You with the MK logo background, top half. Voice inside. |
| 1_A-roll | A-roll_full_frame_original_background.mp4 | Same cut, full 9:16 frame, original room background (backup). |
| 1_A-roll | A-roll_person_matte_1080x960.mp4 | Black/white cut-out mask, if you want to try another background in Resolve. |
| 2_Board | Board_animation_1080x960.mp4 | Bottom half. The case sheet writes itself, synced to your words. |
| 3_Cards | Card_83.png … Card_90.png, Title_card_83-90.png | Full-screen 9:16 cards. |
| 4_Audio | Voice_clean.wav | Clean voice, same as the A-roll audio. |
| 5_Captions | Captions_Hinglish.srt | File > Import > Subtitle. |

## Tracks
| Track | What | Position |
|---|---|---|
| V1 | A-roll_logo_background (whole length) | Y **+480** (top half) |
| V2 | Board_animation (whole length) | Y **−480** (bottom half) |
| V3 | Cards at the times below | full screen (covers face + board; voice continues) |
| A1 | Voice (from the A-roll or Voice_clean.wav, not both) | 0 dB; master −1 dB if needed for −14 LUFS |
| Subtitles | Captions_Hinglish.srt | hide them while a card is on screen |

## Steps (markers)
| In | Step |
|---|---|
{rows(f"| {m['tc']} | {m['name']} |" for m in spec['markers'])}

## Cards (V3)
| In | Out | Card |
|---|---|---|
{rows(f"| {c['tc_in']} | {c['tc_out']} | {c['file']} |" for c in spec['clips'] if c['track'] == 'V3')}

Each card is placed at the end of its step (after you explain it). Move a card freely within its step, e.g. over a moment where you look down (list below).

## Board lines (already animated in the board video; for reference)
| Starts writing | Line |
|---|---|
{rows(f"| {b['tc']} | {b['text']} |" for b in spec['board_items'])}

## Off-camera moments to cut (eye contact rule)
{len(off)} moments where you look down or away. In pauses you can cut them directly. Where words are spoken, cut picture **and** sound together only if you accept losing that syllable, or cover the moment with a card.
| In | Out | During words |
|---|---|---|
{rows(f"| {o['tc_in']} | {o['tc_out']} | {' '.join(o['during_words']) or '(pause, safe to cut)'} |" for o in spec['off_camera'])}

**Important:** cut **all tracks together** (A-roll, board, voice, captions) with ripple delete, so the board stays in sync with your words.
"""
open(f"{K}/EDIT_GUIDE.md", "w").write(guide)
open(f"{K}/INSTRUCTIONS_FOR_CLAUDE.md", "w").write(f"""# For the Claude editing this in DaVinci Resolve

1. Read `timeline_resolve.json`. It is frame-exact at 30 fps, and `*_out` is exclusive.
2. Build the timeline:
   - Run `build_timeline_in_resolve.py` in Resolve's console (Workspace > Console > Py3).
   - Or place by hand: V1 = A-roll (Position Y +480), V2 = Board (Position Y −480), V3 = cards at their frames, A1 = voice.
   - If Resolve's Pan/Tilt units differ, set Inspector Position Y to +480 / −480 instead.
3. Import `Captions_Hinglish.srt` as subtitles and hide them while a card is up.
4. Owner's rules:
   - The face must always look into the camera: cut the `off_camera` moments, all tracks together (ripple), keeping the board in sync.
   - Cards show full screen with only the voice behind them.
   - No music.
   - Don't add facts beyond Organon §83–90.
5. Export at 1080x1920, 30 fps, H.264, AAC.
""")
print("cards", len(cards), "board items", len(BOARD), "off-camera", len(off), "frames", NF)
