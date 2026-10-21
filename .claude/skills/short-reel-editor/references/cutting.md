# Cutting raw footage to the script

## 1. Transcribe every take
```
ffmpeg -i raw.MOV -ac 1 -ar 16000 raw16.wav
python -I scripts/transcribe.py raw16.wav words.json            # medium.en, word timestamps
python -I scripts/align.py raw16.wav words.json aligned.json     # MMS_FA forced alignment, 20–35s chunks
```
- Use `medium.en` with `condition_on_previous_text=False` and VAD (min silence 300 ms). `small.en` silently merges repeated takes ("headless browser" → "headless same").
- medium.en sometimes drops "Number" before a digit ("Number two" → "2."). Give that pick a forced start time.
- Whisper word times run early. Always use the forced-alignment `s`/`e` for cuts and captions.

## 2. Pick takes
- Print the aligned transcript with word indices. For each script line, find every attempt and choose the **last complete, clean** one (fluent, mic close, looking at camera).
- Write the picks as `[first_word_index, last_word_index]` (plus an optional forced start) in `cut.json`, in script order. See `scripts/README.md`.
- Phrases the speaker says differently from the script are fine. Keep what they said and fix it only in captions if it was mis-transcribed.

## 3. Gaze: find look-downs
```
python -I scripts/gaze.py raw.MOV gaze15.json 15 --crop 0.6,0.2,0.36    # head crop: width frac, x frac, y frac
```
- It runs the mediapipe face landmarker on a head crop. A wide shot's face is too small on the full frame.
- Pitch comes from the transformation matrix, `atan2(-m[1,2], m[2,2])`. Looking at camera is about 0–7°. Looking down is pitch > 11–15°, or no face found.
- `cut.py` writes `lookdown.json`: the merged look-down ranges in cut time. These ranges **must** get full-screen B-roll.

## 4. Cut
```
python -I scripts/cut.py cut.json          # -> cut/cut.mp4, segments.json, words_cut.json, lookdown.json
```
- Internal pauses over 0.26s are split, keeping 0.08s either side.
- Take boundaries only: end before the head drops (gaze) and start after the head is up. Skip this for takes that are mostly look-down.
- Default tail (`post`) is 0.10s. For any take the user flags ("make this jump cut faster", "I start looking down"), set `tail[last_word_index] = 0.05`.
- Segments snap to whole frames, so concat never pads audio and the word map never drifts.
- Render with per-segment input seeking (`-ss a -t d -i SRC` per segment plus a concat filter). It's about 5× faster than `trim` on one input.

## 5. Review copy
Make `cut_vN_REVIEW.mp4` with a red border, the label "LOOKING DOWN - B-ROLL HERE" and a timecode over each look-down range. Put the drawtext filters in a `-filter_script:v` file, because inline quoting breaks. The macOS Helvetica.ttc has no → glyph.

## 6. Framing (after the cut is approved)
- Measure the chair or seat edges on a few frames from different takes. On a tripod they don't move.
- Choose one crop centred on the chair:
  - full-face C: `crop=720:1280:X:520` → 1080x1920
  - speaker card A: `crop=760:558:X:760` → 980x720
```
python -I scripts/crop.py cut/cut.mp4 --center-x 515 --out assets/
```
- **Never** re-centre per take on the face. Hide jump cuts in the composition with alternating punch-ins instead.

## 7. Re-cutting after feedback
Feedback like "0:35 make this jump cut faster" changes segment lengths. Keep authoring times on the old cut and map them:
```
python -I scripts/warp.py old_segments.json new_segments.json warp.json
```
`warp.json` rows are `[old_a, old_b, new_a, new_b]`. All three consumers read it, so nothing has to be re-timed by hand:
- `captions.py --warp`
- `mix.py` (the `warp` key)
- the template's `tl` wrapper, through `window.WARP`

Re-check the music beat alignment after a warp, because the `beat_word` time moves.
