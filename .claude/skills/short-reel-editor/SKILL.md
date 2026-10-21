---
name: short-reel-editor
description: Edit raw talking-head footage into a finished 9:16 Instagram Reel / YouTube Short, driven by the user's script — cut to the script, pick clean takes, hide look-downs with B-roll, add motion graphics (HyperFrames + GSAP), word-synced captions, music + SFX sound design and a cover, with an approval gate at every stage. Use when the user hands over raw footage (one long take with retakes) plus a script and wants an edited reel, or asks to "edit this footage into a reel/short".
---

# Short Reel Editor

Turns one raw recording (multiple takes, pauses, glances at notes) plus the script it was read from into a polished, captioned, sound-designed vertical reel. The style is a clean "AI edit" look: off-white canvas, graphic on top, caption in the middle, speaker card at the bottom, with full-face punch-in beats and graphic-only B-roll beats.

Every stage is gated on the user's approval. Never skip a gate, even if the user says "just make the video" mid-way; show them what the next gate needs and continue only on approval.

## Before you start: ask two things

1. **The raw footage and the script.** Also ask if any lines have B-roll notes (e.g. "show my Instagram page here", "recreate this diagram") and whether there are reference images or links for them.
2. **How the sound should be made.**
   - **Epidemic Sound** (needs the user's Epidemic MCP key in `EPIDEMIC_SOUND_API_KEY` or a `.env` file; never print it)
   - **Their own music/SFX files**
   - **Free** (any royalty-free track they point to, or ACE-Step 1.5 if installed)

Also offer to apply their own vocal preset. If they have one in Premiere/Audition, ask for screenshots of the EQ, DeNoise and compressor and copy the numbers (see `references/sound.md`).

## Requirements

- `ffmpeg` and `ffprobe` on PATH (or set `FFMPEG` / `FFPROBE`).
- Python 3.10+ with `faster-whisper`, `torch`, `torchaudio`, `mediapipe`, `numpy` (`pip install -r scripts/requirements.txt`).
- Node.js 18+ for HyperFrames (`npx hyperframes@0.8.164 ...`). Load the `/hyperframes` skill if it is installed.
- mediapipe face model: `scripts/gaze.py` downloads `face_landmarker.task` on first run.

Check these first and tell the user exactly what to install if anything is missing.

## The workflow (8 gated steps)

| # | Step | What you deliver | Gate |
|---|---|---|---|
| 1 | **Cut to script** | Transcribe, align, pick the best take of every line, tighten pauses (`references/cutting.md`) | — |
| 2 | **Show the cut** | `cut_vN.mp4` plus a `_REVIEW.mp4` with a red border and label on every look-down range | User approves the cut |
| 3 | **B-roll, graphics, music, SFX** | HyperFrames composition built on `assets/template/` (`references/style.md`, `references/broll.md`); pick the music | — |
| 4 | **Storyboard** | Snapshot frames of every beat and safe-zone sheets (`scripts/safezone.py`) | User approves the frames |
| 5 | **Sound design** | Mix with voice chain, ducked music, mid pocket and SFX (`references/sound.md`) | — |
| 6 | **Audio first** | `audio_vN.m4a`/`.wav` plus the audio laid over the approved cut | User approves the audio |
| 7 | **Render** | Final render, then the critique loop (`references/review.md`) | — |
| 8 | **Deliver** | Video, cover and caption; once approved, copy them into `approved/<reel-name>/` | User approves the final |

On every revision round, change only what was asked, then show the changed frames (or a review render when the change is about timing or motion) before replacing the final.

## Non-negotiable rules (learned from real review rounds)

**Cutting**
- Use the last clean take of each line. If a line was spoken whole in one take, prefer it to a stitched pickup.
- End each take right on its last word, about 0.05–0.1s after. Default tails show the head dropping to read the next line, and users notice even a few frames of it.
- Never use freeze frames to hide a head drop. They read as glitches.
- Never gaze-trim inside a take or inside sections that will get full-screen B-roll. It makes cuts choppy.
- Snap every segment to whole frames, or caption and SFX timing drifts about 0.5s by the end.

**Framing**
- The camera is static. Use **one fixed crop** centred on the subject's chair or seat, with equal padding left and right, for the whole video.
- **Never** re-centre per take on the face: it makes the frame jump at every cut.
- Hide jump cuts with alternating fixed-centre punch-ins (1.0 ↔ 1.08 per segment).
- Add "interactive" ease zooms on talking-head sections. Each full-face section opens with a quick scale-in (1.07→1, power3.out) and then a slow easy-ease push (→1.05, sine.inOut). Card sections get a slow push.

**Look-downs**
- Wherever the speaker looks down (reading notes, laptop), show **only B-roll or graphics**, never their face. Detect it with `scripts/gaze.py`.
- B-roll inserts must not show the speaker looking down either. This includes demo clips cut from the same raw footage: gaze-check them, or use a person-free clip.
- If a full-face line has a too-quick head drop, replace it with a typeset B-roll (italic serif on the beige canvas).

**Captions**
- Word-synced from forced alignment, not raw Whisper times (Whisper runs early).
- Middle captions are regular weight, ink colour. Graphic-only beats use big italic serif caps, and keywords may be blue.
- Fix transcription slips against the script ("AI techs" → "AI text").

**B-roll content**
- Use real things over generic mocks: the user's real profile (real avatar and stats), the real post they reference (resolve the link, use its real author, text and video), and real software screen recordings when the script names the tool (e.g. an actual Premiere Pro timeline from a free-licence stock site).
- Never fabricate posts, names or numbers. If something can't be fetched (an Instagram grid needs a login), say so and ask for a screenshot.
- Logos over text labels.

**Safe zones and layout**
- Keep text, faces and key graphics inside the Instagram safe area (`assets/safezone_mask.png`, `references/style.md`).
- Graphics sit high, the caption sits in the middle, and the speaker card sits at the bottom with the face inside the safe zone.

**Audio**
- Music never drops out under speech.
- Duck the music under the voice and cut a mid pocket (about 1–5 kHz) into the music and SFX so the voice pops.
- De-ess the voice.
- Master to about −14 LUFS with true peak at or below −1.5 dB.
- Verify intelligibility by re-transcribing the mix and comparing it to the voice alone.

**Delivery**
- Always show frames before rendering.
- Run the critique loop after rendering.
- Deliver the video, a cover (the user's studio headshot if they have one, not a frame grab) and a caption.

## File map

- `references/cutting.md`: transcription, alignment, take picking, gaze, tails, framing, re-timing after recuts
- `references/style.md`: layout modes A/B/C, typography, colours, captions, safe zones, motion vocabulary
- `references/broll.md`: B-roll planning, real-asset sourcing, stock sources, scene recipes
- `references/sound.md`: music choice, beat grid, ducking, mid pocket, vocal chain, SFX placement, checks
- `references/review.md`: approval gates, storyboard sheets, critique loop, deliverables, revision etiquette
- `scripts/`: the pipeline (see `scripts/README.md`)
- `assets/template/`: HyperFrames starter composition with the A/B/C mode system, captions, cover text, zooms and time-warp
- `assets/cover/`: cover template
- `assets/safezone_mask.png`: Instagram Reels safe-zone guide (1080x1920)
