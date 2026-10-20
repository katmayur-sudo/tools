---
name: porcelain-keynote-film
description: Make a keynote-style launch film (60-120 s, 16:9) for a product, app, channel or brand in the "porcelain keynote" style - small kinetic type on a porcelain canvas, dark "New ___" word-wheel chapter dividers, the product's real screens with camera push-ins and a live cursor, glass cards on landscape plates, a "One More Thing" reveal and a logo end card, all cut to a beat-synced instrumental. Use for launch videos, product announcements, feature recaps and channel trailers. No voice-over or subtitles.
---

# Porcelain keynote launch film

An original implementation of the keynote launch-film style analysed in `ANALYSIS.md` (an
independent style study; never use another company's name, logo, characters or footage).

## When to use
- Launch / announcement / feature-recap / channel-trailer videos where **type + real screens + music**
  carry the story.
- Not for talking heads, tutorials, voice-over or subtitled content (use the explainer workflow in
  `videos/beginner-gym-engine/` for those).

## Inputs to collect
- Product or brand name, URL or source material (screens, app, videos), accent colour, logo/mark.
- Length (default ~60 s; the references run 94-110 s), resolution (1080p default, 1440, 2160).
- 3-5 pillars (become the "New ___" chapter words) and one surprise for "One More Thing".
- Optional: a licensed music track (otherwise `music.py` synthesizes one at the storyboard BPM).

## Workflow
1. **Research.** Open the site/app (Playwright screenshots of the real UI at 1920×1080 and phone
   size), collect logo, colours and the product's own claims. For a channel or creator, grab frames
   from their own videos. Use only true, sourced claims.
2. **Storyboard** (`examples/*.storyboard.json`). Follow the formula from `ANALYSIS.md`:
   `cold → intro → meet line → slot(0) → hero line → ui → iconRow → slot(1) → ui/plate → slot(2) →
   line(clouds)/ui → broll → onemore → slot(last) → reveal → ui(phone) → closer(squiggle) →
   closer(circle) → end`. Durations are in **beats**, so every cut lands on the music. Lines are
   2-7 words with one `*accent*` phrase.
3. **Assets.** Put screenshots/photos in `<film_dir>/assets/`. Plates can be photos or the built-in
   CSS plates `sea`, `salt`, `glacier`, `dusk` (no image generation needed). Paid generation
   (plates, b-roll, music) only after listing every job and its cost and getting approval.
4. **QA stills.** One still per scene:
   `node engine/render.mjs <film_dir> sb.json none <stills_dir> --stills t1,t2,...` and check
   text fit, crops, overlaps and that nothing important sits under the cursor.
5. **Music.** `python3 engine/music.py sb.json music.wav` (soft cold open, groove, drop + riser into
   One More Thing, pad outro, -15 LUFS). Or supply a track and set `bpm` to its tempo.
6. **Render.** `node engine/render.mjs <film_dir> sb.json music.wav film.mp4 [--res 2160]`
   (4 parallel Chromium pages → FFmpeg; ~1.5 min for a 60 s 1080p film).

`<film_dir>` = a folder containing `engine/film.html` (copied) and the `assets/` the storyboard
references. Keep owner photos and rendered media out of git.

## Scene types (storyboard `type`)
| type | fields |
|---|---|
| `cold` | dark open, dim mark + name |
| `intro` | `text` (default "Introducing <name>") |
| `line` | `text` (string or array of lines), `clouds`, `size`, `grey` (word index after which words start grey) |
| `slot` | `index` into top-level `chapters`; lead word = `slotLead` ("New"/"Your") |
| `ui` | `image`, `w`,`h`, `zoomFrom`/`zoomTo`, `origin`, `pos`, `desktop`, `cursor{from,to,delay,move,click}`; or `phone:true` + `plate` + `title` + `x` |
| `iconRow` | `icons` (emoji), `active`, `words` (built one per `wordBeats`), `payoff` |
| `broll` | `image`, `pos`, `filter`, `line`, `phrases` (rotate in accent) |
| `plate` | `plate` (CSS preset or image), `title`, `items` [[icon, text], ...] in a glass card |
| `chips` | `plate`, `title`, `chips` [[icon, label, x, y], ...] popping on beats |
| `onemore` | "One More Thing", words grey → ink on the beat |
| `reveal` | `text` pill, `objects` (emoji) burst after 2 beats, `tilt` |
| `closer` | `pre`, `word`, `post`; `mode:"circle"` circles the word, default squiggle annotation; `peek` image |
| `end` | logomark slides into name, `sub`, `objects` at the edges, fade to black |

Top level: `name`, `accent`, `canvas` (`#F4F4F4` cool or `#F4F0E8` warm), `bpm`, `logo`,
`logoFilter`, `slotLead`, `chapters`, `scenes`.

## Style rules (do not break)
- Small type (≈56 px at 1080p), regular/medium weight, lots of empty canvas; never bold slabs.
- One accent colour; 1-2 accent words per line; dividers are the only dark scenes.
- Cuts on the beat; median shot 2-4 s; the type is the narrator: no voice-over, no captions.
- Real product screens over illustrations; slow push-ins, never fast zooms.

See `examples/drmak-fitness.storyboard.json` for a complete 61 s film (126 beats at 124 BPM).
