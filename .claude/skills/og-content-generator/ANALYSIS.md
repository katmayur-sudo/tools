# Porcelain keynote launch film: style analysis

Independent style study of the "Manus 2.0 style" keynote launch film, built only from the three
**public preview films** on the Skillry listing (`skillry.dev/skills/bs-manus2-0-style-launch-video`)
and its public description. The paid Skill files were not used. Nothing here reproduces Manus's
film, characters or logo; the products in the previews are themselves demo products (Muse, Grok Bot,
Skillry).

## The three reference films

| Film | Product | Length | Detected cuts | Median shot | Tempo | Loudness |
|---|---|---|---|---|---|---|
| p1 | "Muse", personal AI agent (blue accent) | 94.2 s | 18 hard cuts | 3.9 s | ~123 BPM | -15.4 LUFS |
| p2 | "Grok Bot", AI teammates (blue accent) | 103.9 s | 20 | 3.8 s | ~129 BPM | -15.0 LUFS |
| p3 | "Skillry", skills library (coral accent, warm canvas) | 110.5 s | 32 | 2.0 s | ~123 BPM | -16.7 LUFS |

Hard cuts sit within ~0.1 s of the beat grid (beat = 0.47-0.49 s); many other transitions are
dissolves or in-shot text changes that also land on beats. No voice-over, no subtitles: **the type
is the narrator** and the music is the pace.

## The formula (same order in all three)

| # | Beat | Time (p1) | What it looks like |
|---|---|---|---|
| 1 | **Cold open** | 0:00-0:02 | Near-black `#08090C`, small dim logomark + wordmark fading up in the centre. Quiet music intro. |
| 2 | **Introducing** | 0:02 | Cut to porcelain. Logomark + "Introducing <Name>", medium weight, centred, small. |
| 3 | **Meet line** | 0:04 | "Meet your personal **AI agent**": one accent-coloured phrase. |
| 4 | **Slot divider** | 0:06 and every chapter | Dark screen. Left: accent lead word ("Your" / "New"). Right: a vertical word wheel (`Time / Agent / Browser / Rules / Mac`) where the current item is white and the others fade to grey; each divider rolls the wheel one step. These are the chapter markers (4-5 per film). |
| 5 | **Hero statement** | 0:08 | Short 2-3 line sentence, sometimes with an inline mascot/emoji. |
| 6 | **Real UI** | 0:10-0:16 | The product's real interface on a white rounded card with a soft shadow; slow camera push-in (~1.00→1.08), live cursor, typing, a click. |
| 7 | **Kinetic list** | 0:16-0:23 | Row of app/feature icons with the active one raised; words build one at a time ("Email. Calendar. Money. Health.") then a payoff line ("Muse handles **it all.**"). |
| 8 | **B-roll + rotating phrase** | 0:26-0:32 | Lifestyle footage, white text lower-left: fixed line + a phrase that swaps in accent colour ("Muse cooks up / family calendars / gift ideas"). |
| 9 | **Soft 3D clouds** | 0:36-0:40 | Statement on porcelain with soft white clouds drifting under it ("A secure computer with a browser"). |
| 10 | **Desktop push-in** | 0:44-0:50 | OS desktop + app window, permission dialog, cursor clicks "Allow". |
| 11 | **Plate + glass card** | 0:52-0:57 | Full-bleed landscape photo (glacier, salt flat, sea stacks), white title top-centre, frosted glass card listing 3-5 icon rows. |
| 12 | **One More Thing** | 0:58 | Porcelain, "One More Thing", words fading in grey→black one at a time. |
| 13 | **Reveal** | 1:02-1:05 | White pill ("Muse for Mac") with a loading dot, then 3D objects/mascots burst around it. |
| 14 | **Second UI / phone** | 1:06-1:20 | Phone mock on a plate, b-roll "from anywhere", floating label chips on a street plate ("Flowers ordered", "Table for two, 7 PM"). |
| 15 | **Closing line** | 1:20-1:27 | Built word by word, one word annotated: small handwritten word above with a squiggle ("your *time* back"), or a hand-drawn ellipse circling a word ("**You** decide what matters"). Mascot peeks in from the bottom edge. |
| 16 | **End card** | 1:28-1:33 | Logomark slides into wordmark, objects at the edges. Cut to black. |

## Visual system

- **Canvas:** porcelain `#F4F4F4` (cool) or `#F4F0E8` (warm, p3). Dividers `#08090C`.
- **Accent:** one brand colour only, used for the lead word of dividers and 1-2 words per line
  (blue `#2F6BFF`-ish for p1/p2, coral `#E8775A`-ish for p3).
- **Type:** neutral grotesk (Inter / SF-like), regular-medium weight, **small** (about 40-56 px at
  1080p) with huge whitespace. Never bold slabs, never all caps.
- **Text motion:** word-by-word fade with a slight blur and upward drift; trailing words start grey
  and settle to ink; phrases swap with a vertical slide.
- **Cards:** white, radius 16-24 px, soft long shadow; glass cards `rgba(255,255,255,.72)` with
  backdrop blur on photographic plates.
- **Camera:** slow push-ins on UI (≈8 % over a shot), subtle Ken Burns on plates and b-roll.
- **3D props / mascots:** soft clay-like objects for the reveal and the end card.

## Sound

Upbeat minimal instrumental (house/pop, ~123-129 BPM), quiet intro under the cold open, groove from
"Introducing", a lift into "One More Thing", outro under the end card. Everything is cut to the
beat grid; mix around -15 LUFS.

## Copy rules (from the description and the films)

- Use only claims the product itself makes (research the site first).
- 3-5 pillars, each introduced by a slot-divider word; one surprise saved for "One More Thing".
- Lines are short: 2-7 words; one accent phrase per line.
- Close with a human line ("You decide what matters") and the logo.

## Workflow (as published)

1. **Research** the site in a browser: desktop + mobile screenshots, logo, colours, copy; pick
   3-5 pillars and one surprise.
2. **Storyboard** in the style's patterns using only the site's claims.
3. **Media** (optional, paid): landscape plates, 5 s b-roll and an instrumental soundtrack, listed
   with costs and approved before submitting.
4. **Render** the HTML film frame by frame with headless Chrome + FFmpeg at 1080p / 2K / 4K, QA'd
   frame by frame.
