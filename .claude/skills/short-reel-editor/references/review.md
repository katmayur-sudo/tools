# Approval gates, critique loop and delivery

## Presenting each gate
- **Cut:** link the clean cut and the `_REVIEW` copy. List the take choices, what was trimmed, and the look-down ranges that will get B-roll.
- **Storyboard:**
  - Snapshot 25–35 frames covering every beat: `npx hyperframes snapshot <dir> --at t1,t2,… --no-end --describe false -o out/`.
  - Add the contact sheets and one safe-zone sheet: `python -I scripts/safezone.py out/ assets/safezone_mask.png sheet.jpg`.
  - Give a shot-by-shot table (time, line, what's on screen) plus anything you couldn't source for real.
- **Audio:** see `sound.md`.
- **Revisions:**
  - Map each request to a concrete fix, and restate any ambiguous one along with your reading of it (e.g. "bike background" = beige background).
  - Fix only what was asked.
  - Show the changed frames, or a `_REVIEW` render when the change is about timing, jump cuts or motion.

## Rendering
```
npx hyperframes lint <dir>           # 0 errors before any snapshot or render
npx hyperframes render <dir> -q high -f 30 -o visual.mp4
python -I scripts/mix.py mix.json visual.mp4   # mux the approved mix
```
- HyperFrames needs ffmpeg/ffprobe on PATH.
- Renders take several minutes, so run them in the background.

## Critique loop (before delivering)
`python -I scripts/check.py final.mp4 words_cut.json` reports:
- duration and resolution
- `freezedetect` (n=0.001, d=0.6): **no frozen stretches**
- `blackdetect` (d=0.2): **no black frames**
- integrated loudness and true peak
- the transcription match and its diffs

Also pull 5–8 frames at changed or risky moments (mode switches, the new B-roll, the CTA) and look at them. For example, check that a recent asset swap made it into this render, and compare render timestamps against the asset timestamps.

## Deliverables
- `final/<reel>/<reel>.mp4`, `cover.png` and `caption.txt`. Keep earlier versions in `final/<reel>/previous/`.
- **Caption:** hook line, the list or payoff in a few short lines, the "edited by Claude" style line if true, `Comment "KEYWORD"…`, then 8–10 hashtags.
- Once the user approves the final, copy the video, cover and caption into `approved/<reel-name>/`. Nothing unapproved goes there.
- Flag licences: Epidemic tracks need the user's plan to cover publishing, and stock clips keep their licence notes.
