# Visual style

## Canvas and tokens
1080x1920 at 30fps. Off-white canvas with flat, clean UI cards.
```
--bg:#F4F3EF  --ink:#161616  --blue:#2E5BFF  --orange:#D97757  --yellow:#FFE14D
--line:#E3E1DB --green:#1FB45A --red:#E5484D  --grey:#8a877f
```

**Fonts** (bundled in `assets/template/assets/fonts`, all under the OFL):
- Inter 500–900
- Instrument Serif italic, used as the family `ISerif`
- JetBrains Mono, used as the family `Mono`

**Never name a @font-face family after a generic keyword** (Serif, Monospace, and so on). CSS treats it as the generic family and the bundled font silently doesn't load.

## Three layout modes (`MODES` in captions.js)
| Mode | Screen | Caption |
|---|---|---|
| **A**: talk + graphic | Graphic on top. The scene is authored in 1080x1920 coordinates (y 100–1020) and squeezed with `transform: translateY(115px) scale(.74)` from origin `540px 100px`, so it lands in y 215–896. Speaker card at left 50, top 1082, 980x720, radius 44. The face must sit inside the safe zone. | Middle, top 945, Inter 500 at 74px, ink. Regular weight, never bold. |
| **B**: graphic only | Graphic fills the frame. Use it for every look-down and for big explainer beats. | Italic serif caps at 124px, top about 1190 (below the graphic). Keywords in blue. |
| **C**: full face | Sharp full-bleed video, never blurred bands. | White cover text over the hands: small italic serif (64px) plus big Inter 900 caps keyword (112px). Two-line big text sits at top 1325 with the small line at 1250. A dark gradient shade sits behind it. |

**Rhythm:**
- Open the hook on C, with captions only.
- Alternate A for explaining, B for look-downs and big diagrams, and C for punchlines ("TOOK A WHILE", "THE THING", "TASTE").
- Close on C with the CTA: **COMMENT “KEYWORD”** in white, word-synced. Don't add "I'll send it" text or link cards.

## Captions
- Built from forced-aligned words (`scripts/captions.py`).
- Join a small word ("the", "a", "so", "on"…) to the next word when the gap is under 0.35s. Never join into a phrase start.
- Keep these phrases together: "code drawn", "real footage", "count up", "Epidemic Sound", "Number 2".
- Each caption stays until the next one starts, or until its last word ends plus 0.8s, or until the next mode switch, whichever comes first.
- No middle captions in C (it uses cover text), and none in typeset B-roll beats (`nocap`).

## Motion vocabulary
- `pop()`: back.out scale-in from 0.6.
- Panels enter with power3.out, y +40–60.
- Cursor click: scale 0.8 for 0.08s.
- Typed text: char-by-char spans.
- Counters: stepped `textContent` sets.
- Line drawing: stroke-dashoffset.
- Explainer focus pattern: list → chosen item rises to the heading slot (x −40, y to 290, scale 1.08, blue border) → others fade → explanation animates below.
- Beat transitions: coloured wipes (scaleX in 0.12s, out 0.14s) on music beats.
- Talking-head zooms: see the jump-cut punch-ins and ease zooms in SKILL.md, implemented in the template as `#zC`/`#zA` wrappers with punch-ins on the video element.

## Safe zones (Instagram Reels, 1080x1920)
- **Safe area:** x 62–1015 for y 266–1151. Below that, the right edge narrows to x 852 down to y 1536.
- **Unsafe:**
  - the top 0–266
  - the bottom 1536–1920
  - the right strip, x > 1015
  - the bottom-right notch: x > 852 for y 1151–1536
- Check every storyboard frame with `scripts/safezone.py`. Slightly overlapping the top line with a graphic is OK. Text and faces must not.

## Cover
- Use `assets/cover/index.html`, 1080x1920. Keep the key content inside y 300–1650, since the grid crops the centre 3:4.
- Put the user's studio headshot at the top, feathered with `mix-blend-mode:multiply` so its white background melts into the beige.
- Below it: a small italic line, a big two-line hook (second line blue), and a small visual of the payoff.
