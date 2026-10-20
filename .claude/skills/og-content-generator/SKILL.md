---
name: og-content-generator
description: Original-content generator for videos. Turns an idea from the chat into a storyboard first, gets it approved, then renders - keynote launch films (porcelain canvas, "New ___" word-wheel chapters, real screens with push-ins, glass cards, One More Thing, beat-synced music), and routes voiced explainers and 9:16 shorts to the matching pipelines. Use whenever the user wants a launch video, channel trailer, product/feature announcement, brand film, reel/short or any new video content, or mentions a content idea worth saving.
---

# OG content generator

Makes original video content from ideas in the conversation. Paths like `engine/…` are relative to
this skill's folder. **Rule zero: storyboard first, always.**
No paid generation and no final render happens before the user has seen and approved a storyboard.

## 0 · Ideas from the chat (every time)
1. Read `ideas.md` (next to this file). Read `brand/*.json` for the brand you are working on
   (e.g. `brand/drmak-fitness.json`: handles, accent, the owner's cloned voice, style rules).
2. Scan the conversation for ideas: topics, hooks, formats, references, "I want…", "make one about…".
   Add every new one to `ideas.md` under *Backlog* with format + date, even ones not made today.
3. If the user hasn't named a topic, propose 3 ideas from the backlog (one line each: hook, format,
   length) and let them pick.

## 1 · Brief (ask only what's missing)
Topic/product · audience · format · length · language · brand/accent · assets (screens, photos,
footage, music) · platform. Defaults: keynote film 60 s 16:9, brand from `brand/`.

| Format | Use for | Engine |
|---|---|---|
| **Keynote film** (default here) | launch, trailer, announcement, recap. Music only, no voice | `engine/` in this skill |
| **Voiced explainer** 16:9 | teaching, how-to, science | `videos/beginner-gym-engine/` pipeline + `styles/red-ink-explainer.yaml` (in the `katmayur-sudo/tools` repo) |
| **Native short / reel** 9:16 | hooks, single tips, series | `videos/beginner-gym-engine/render/verticals.js` + `shorts/build.py` (same repo) |
| **Refine an existing short** 9:16 | the user uploads their own video | `videos/pullup-mistakes/` (same repo): re-cut their voice, rig their photo, two grades |

For voiced formats use the brand's voice from `brand/*.json` / `CLAUDE.md` (Dr Mak: the cloned
"dr mak" ElevenLabs voice, never a stock voice).

## 2 · Storyboard (mandatory gate)
1. Write `storyboard.json` (schema below). Copy rules: 2-7 words per line, one `*accent*` phrase,
   only true/sourced claims, hook in the first scene that has words.
2. Validate: `python3 engine/check.py storyboard.json --assets <film_dir>` (fix every error).
3. Show it:
   - **Board**: `node engine/render.mjs <film_dir> storyboard.json none <out> --board <board_dir>`
     → `board.png` (one still per scene with time, type and copy) + `storyboard.md`.
   - **Live preview**: `python3 engine/preview.py storyboard.json <film_dir> preview.html --inline [--music music.wav]`
     → one HTML file with play/scrub (works in a browser or as a Claude chat artifact).
4. Send the board and the scene table, and **stop until the user approves or edits it**. Apply their
   notes to the JSON and re-show if anything structural changed.

## 3 · Assets
Screens: Playwright screenshots of the real product (1920×1080 and phone) or frames from the
creator's own videos (`ffmpeg -ss <t> -i video -frames:v 1`). Plates: photos or the built-in CSS
plates `sea`, `salt`, `glacier`, `dusk`. Paid generation (images, b-roll, music, voice): list every
job with its cost and wait for approval. Owner photos and renders never go into git.

## 4 · Music, render, QA
- Music: `python3 engine/music.py storyboard.json music.wav` (soft open, groove, drop + riser into
  One More Thing, pad outro, ≈-15 LUFS), or a licensed track with `bpm` set to its tempo.
- Render: `node engine/render.mjs <film_dir> storyboard.json music.wav film.mp4 [--res 1080|1440|2160]`
  (4 Chromium workers → FFmpeg; ~1.5 min per 60 s at 1080p).
- QA: contact sheet of the MP4, check text fit, crops and that cuts land on beats; fix and re-render.

## 5 · Deliver and remember
Send the MP4 (+ preview HTML), suggested post copy (title, caption, hashtags) per platform, then mark
the idea `[x]` in `ideas.md` with the output path and note any new lesson under *Learnings* below.

## Running in each environment
- **Claude Code (cloud or this computer):** everything above. Needs Node 20+, FFmpeg, Python 3 with
  NumPy, and Playwright with Chromium (`npx playwright install chromium` if missing; set
  `CHROME_PATH` or `PLAYWRIGHT_MODULE` if they live elsewhere).
- **Claude chats (claude.ai / desktop, uploaded as a Skill):** do steps 0-2 fully. Deliver the
  storyboard table and `preview.html` (built with `--inline`) as the playable result; if the code
  sandbox has no browser/FFmpeg, hand over the storyboard JSON and tell the user to render it in
  Claude Code with the command in step 4.

## Storyboard schema (keynote film)
Top level: `name`, `accent`, `canvas` (`#F4F4F4` cool / `#F4F0E8` warm), `bpm`, `logo`,
`logoFilter`, `slotLead` ("New"/"Your"), `chapters` (3-5 pillar words), `scenes`.
Every scene has `type` and `beats` (integer; cuts land on the beat grid).

| type | fields |
|---|---|
| `cold` | dark open, dim mark + name |
| `intro` | `text` (default "Introducing <name>") |
| `line` | `text` (string or lines), `clouds`, `size`, `grey` |
| `slot` | `index` into `chapters` (step forward through them) |
| `ui` | `image`, `w`,`h`, `zoomFrom`/`zoomTo`, `origin`, `pos`, `desktop`, `cursor{from,to,delay,move,click}`; phone: `phone`, `plate`, `title`, `x` |
| `iconRow` | `icons`, `active`, `words`, `wordBeats`, `payoff` |
| `broll` | `image`, `pos`, `filter`, `line`, `phrases` |
| `plate` | `plate`, `title`, `items` [[icon, text]] (glass card) |
| `chips` | `plate`, `title`, `chips` [[icon, label, x, y]] |
| `onemore` | "One More Thing" |
| `reveal` | `text` pill, `objects` burst, `tilt` |
| `closer` | `pre`, `word`, `post`, `mode` ("circle" or squiggle), `gap`, `peek` |
| `end` | `sub`, `objects` |

Formula: `cold → intro → meet line → slot → hero line → ui → iconRow → slot → ui/plate → slot →
line(clouds)/ui → broll → onemore → slot → reveal → ui(phone) → closer → closer(circle) → end`.
Style rules and the reference breakdown: `ANALYSIS.md`. Full example:
`examples/drmak-fitness.storyboard.json` (61 s, 126 beats at 124 BPM).

## Learnings
- Small type (~56 px at 1080p), one accent colour, dividers are the only dark scenes.
- Cold-open stills look empty by design; judge the board from scene 1 onwards.
- The dr mak voice runs ~186 wpm: a 30 s short needs ~90 words, a 7 min explainer ~1,300.
- Free image APIs rate-limit fast; prefer real screens/frames and CSS plates over stock images.
- Refining an uploaded video: transcribe it (faster-whisper `small` handles Hindi), cut the dead air and
  storyboard the fixes over its own frames. The common fixes: a static stretch longer than 3 s, captions
  under the Shorts UI (bottom 20%), and a long end card that breaks the loop.
- "Use my photo in the animation" means the photo is the subject, not a backdrop. Cut it out with rembg
  `u2net_human_seg`, mask off the limbs, redraw them with IK, and draw the muscle overlays on the photo.
- Grades on request: `porcelain` (the launch film) and `redblack` (the channel's look). Render both
  from one timeline.
