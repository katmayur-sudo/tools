# Instructions for the Claude editing this reel in DaVinci Resolve

You are rebuilding a finished 9:16 reel from this kit. The edit decisions are already made and frame-exact. Your job is to place the media exactly as specified, then hand over to the owner for creative changes.

## Source of truth
`timeline_resolve.json` holds the plan. `EDIT_GUIDE.md` is the same plan for people, and `8_Reference/Preview_how-it-should-look.mp4` shows the intended result.
- Frames are at 30 fps, counted from the timeline start.
- `*_out` is exclusive: `rec_in 0, rec_out 15` means 15 frames.
- Every card clip, face-circle clip and audio stem is already exactly as long as its slot. Use `src_in` 0 and do not trim them.
- Do not re-sync the A-roll to any other audio: its sound is already lip-synced (the phone's own offset was measured and corrected).

## Steps
1. Open DaVinci Resolve. Workspace > Console > Py3, then run:
   `exec(open(r"<this folder>/build_timeline_in_resolve.py").read())`
   (Resolve Studio with external scripting on can also run it from a terminal.)
2. Read the report it prints.
   - "All clips placed at their exact lengths" with the expected frame count means the build is done.
   - If it lists length or placement failures, fix those clips by hand using the frames in the JSON.
3. Check the face circle on a card shot against the preview render: top-right, ring touching about 90 px from the top edge.
   - The script sets Pan +350 and Tilt +700 (Inspector Position X/Y in timeline pixels, Y up).
   - If your Resolve version maps Pan/Tilt differently, set Position X 350, Y 700 in the Inspector.
4. By hand, since the API can't do these:
   - File > Import > Subtitle > `6_Captions/Captions_Hinglish.srt`, placed at the timeline start.
   - Optionally add a 9-frame fade-in on each V4 overlay.
   - In Fairlight, set the master bus to -1 dB, which gives -14 LUFS (the Instagram target).
5. Scrub the markers S01–S12 and compare each against the preview render.

## Rules the owner set (keep them if you change the edit)
- Never show the speaker's face while they look down. `EDIT_GUIDE.md` lists every glance-down time; on full-face shots those times are covered by cards.
- Keep every spoken word. Don't cut inside the A-roll pieces; they are the clean takes.
- Psychiatry facts on screen come only from Davidson's Principles & Practice of Medicine, 24th ed. Don't add new medical claims to the cards.
- Captions are Roman Hinglish, spelled as spoken. The ANHEDONIA card (S05) has no captions on purpose.
- Don't change the cards' text. Restyling colours, fonts or motion is fine; `7_Card_PNGs_editable` has the separate layers.
- Export 1080x1920, 30 fps, H.264, about 20 Mbps, with AAC 320 kbps audio.
