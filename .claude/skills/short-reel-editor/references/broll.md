# B-roll and graphics

## Plan from the script
For every script line, decide:
- the mode (A/B/C)
- the graphic
- the exact word each element lands on, from `words_cut.json`

Honour the user's bracketed B-roll notes literally. Map every look-down range to B. Read the plan back as a short table in the storyboard message.

## Real assets over mocks
| Script mentions | Use |
|---|---|
| "my last post", "my channel" | An Instagram profile clone with the **real** avatar and stats. The page's `og:image` and `og:description` work without a login when fetched with the user-agent `facebookexternalhit/1.1`. The last post is the actual previous reel, playing. The grid needs a login, so ask for a screenshot rather than inventing tiles. |
| A LinkedIn, X or YouTube post or link | Resolve the short link (`curl -L`) and read the JSON-LD and `og:` tags for the author, avatar, text, counts and the media URL (LinkedIn: `dms.licdn.com/.../mp4-640p...`). Rebuild the card with the real content and play the real video muted. |
| A software tool (Premiere Pro, After Effects…) | A real screen recording from a free-licence stock site. Mixkit works without a login, e.g. `https://mixkit.co/free-stock-video/video-editing/`, with assets at `assets.mixkit.co/videos/<id>/<id>-1080.mp4`. Pexels and Pixabay block scripted fetches. Verify that the UI is really that tool before using it. |
| Brands and frameworks | Real logos: Simple Icons via `cdn.jsdelivr.net/npm/simple-icons@13.21.0/icons/<slug>.svg`, the project's own site (e.g. `hyperframes.heygen.com/hyperframes/logo-light.svg`), or official press or square logos. |
| A demo clip of "raw footage" | Cut it from the user's raw footage, but **only from a gaze-checked camera-facing span**. Otherwise use a person-free graphic clip. |

**Never fabricate** names, follower counts, posts or quotes. When a real asset can't be fetched, say so and ask.

## Scene recipes (all in `assets/template/index.html` style)
- **Profile click-through (A):**
  1. A profile card pops in.
  2. A cursor glides to the first tile and clicks.
  3. The tile grows into a reel player playing the real reel.
  4. On "no X", strike-through tiles appear (e.g. the Premiere logo with a red slash).
- **N-ways diagram (B, then A):**
  1. Brief → Claude → N route rows → output.
  2. Per item, the "focus pattern": the chosen row rises to the heading slot and the others fade.
  3. An explanation animation plays below.
- **Raw → edited (B):**
  1. A phone frame plays a raw clip tagged RAW.
  2. A punch-in shows the cut.
  3. The clip shrinks into the bottom card while the graphic card and caption appear: the reel's own layout in miniature.
  4. Text slides in, a counter counts up, and coloured wipes land exactly on the music beats.
- **Typeset line (B):** italic serif words appear in sync, with the keyword big and blue and a slow "rendering…" bar. Use it to replace a face shot with a quick head drop.
- **Tool connect (A):** two logo cards, a cable that draws in, an "MCP" chip, and the plugs snapping together with a flash. A results panel then shows what was picked.
- **Skill / summary (A):** icons from the whole video in a ring fly into one file card ("SKILL.md").

## Asset hygiene
- Re-encode every clip to 30fps H.264 with `-g 15` so seeking is cheap.
- Every `<video>` needs an `id`, `class="clip"`, `data-start`, `data-duration`, `data-media-start` and `muted`.
- JS-created media must still exist statically in the HTML.
- Keep stock sources and their licences in `stock/` next to the project.
