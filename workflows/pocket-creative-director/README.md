# Workflow: recreate a pro edit from one prompt with Claude Code

Built from **"How Claude Code made this edit from one prompt"** by simply forseth (Johannes Forseth)
<https://youtu.be/LoapCWKjsQ4> · 10:52 · unlisted breakdown of one of his Instagram edits.

- [1. What the video is actually about](#1-what-the-video-is-actually-about)
- [2. Timeline of the video](#2-timeline-of-the-video)
- [3. The tool stack he used](#3-the-tool-stack-he-used)
- [4. Key concepts: DNA, signatures, library](#4-key-concepts-dna-signatures-library)
- [5. The workflow, step by step](#5-the-workflow-step-by-step)
- [6. Effects and cuts catalog](#6-effects-and-cuts-catalog)
- [7. Where image generation fits](#7-where-image-generation-fits)
- [8. Lessons and pitfalls from the video](#8-lessons-and-pitfalls-from-the-video)
- [Files in this folder](#files-in-this-folder)

---

## 1. What the video is actually about

The video is **not** a tutorial on AI image generators. It's a screen-recorded walkthrough (the
creator sits in a webcam bubble, bottom right) of how one of his Instagram edits was produced
almost entirely by **Claude Code** running his product, the **Pocket Creative Director**: a set of
Claude Code guidelines and skills that turn an agent into a creative director and editor.

The core claims:

1. **He recorded nothing.** The narration was written by Claude, using a "storyteller" skill, and
   voiced with **ElevenLabs v4**. He then picked existing clips of himself from a footage library
   on the cloud.
2. **The edit is a 1:1 recreation of another creator's edit.** He gave Claude a reference video
   (an interview clip of a man in a suit, plus a music-app segment) and said, roughly: *"Recreate this.
   I don't care what you use: After Effects, Blender, whatever. Do the sound design too."* Then he
   went to the store.
3. **Claude built the edit natively in After Effects** (multiple compositions, layers, keyframes),
   checked itself by **extracting frames** and looking at them, and did the sound design.
4. **The first recreation is slow; later ones are fast.** The first pass took a long time
   (30 min to 2 h depending on the edit). The analysis is then saved as a reusable style
   **"DNA" / "signature"**, so the same style can be regenerated quickly.
5. **It was a "two-shot", not a one-shot.** He only gave small notes. The colours were too punchy,
   the name text was wrong, he wanted less motion blur and some bloom/glow on the text, and he
   asked it to swap in better match-cut footage from his library.
6. **His thesis:** current models (Opus 5.5, Fable…) are already good at motion design. What they
   lack is a **system**: structure, guidelines, memory of *you*. Give them that and the output
   stops being "AI slop". He frames it as "steal like an artist": recreate to learn a style, then
   remix pieces into your own, rather than shipping 1:1 copies. He credits the original creator.

## 2. Timeline of the video

| Time | What happens |
|---|---|
| 0:00–0:25 | Intro over the After Effects project. This breakdown was also edited by Pocket Creative Director. |
| 0:25–0:55 | Disclaimer: it's a 1:1 recreation of another creator's edit. "Steal like an artist", don't copy. |
| 0:55–1:33 | The Claude Code chat. It started as a test of **ElevenLabs v4** that turned into "make a satire edit". |
| 1:33–1:58 | Claude wrote the script and the ElevenLabs audio is the exact file heard in the Instagram video. |
| 1:58–2:25 | Shows the reference video. The prompt: "recreate this, use After Effects / Blender / anything, and sound-design it". |
| 2:25–3:05 | He left while it worked. Explains **DNA**: the first recreation is slow; after that the style is reusable and fast. |
| 3:05–3:31 | First result: colours too punchy. Shows Claude **extracting frames** (a grid of frames) to check its own work. |
| 3:31–3:44 | The full After Effects project with compositions. DaVinci Resolve would work too, and you don't need to know either app. |
| 3:44–4:11 | Human in the loop: explaining while it works makes it faster, but **vague directions can steer it wrong**. |
| 4:11–5:15 | Small notes only: show the original video, fix the on-screen name, remove motion blur on text. |
| 5:15–5:54 | Once the DNA exists, add your own ideas. Asked for **bloom/glow** on text. Warns that speech-to-text rambling is bad direction. |
| 5:54–6:34 | Style saved as a **signature**. Individual effects (e.g. the **match cut**) saved to a **library**. "Boards" is in beta. |
| 6:34–7:39 | **Sound design**: v1 used ElevenLabs SFX. Now teaching it native sound design in **Reaper**. Music was composed from a purchased film-score pack. |
| 7:39–8:44 | Recap: storyteller skill → ElevenLabs v4 prompting guide → generated MP3 manually (free credits) → "go" → near-perfect result. Only change: better match-cut footage from his cloud library. |
| 8:44–9:51 | "Two-shot, not one-shot." Models are good at motion graphics but lack a system and guidelines. |
| 9:51–10:52 | North Star: a creative director behind your back for one-person teams. "Use AI the right way, not AI slop." Credits the original creator. |

## 3. The tool stack he used

| Job | Tool in the video | Open or alternative option |
|---|---|---|
| Agent / orchestrator | **Claude Code** + Pocket Creative Director guidelines | Claude Code + the templates in this folder |
| Script | Claude ("storyteller" skill) | Claude with `templates/prompts.md` → Prompt 1 |
| Voice-over | **ElevenLabs v4** (generated by hand in the web app for free credits) | ElevenLabs API / ElevenLabs MCP `creative_generate_speech` |
| Edit / motion design | **Adobe After Effects** (driven by scripts) | DaVinci Resolve (Python API), Blender, **Remotion**, HyperFrames, ffmpeg |
| Self-check | Frame extraction → Claude looks at the stills | `scripts/contact_sheet.sh` (ffmpeg) |
| Sound effects | ElevenLabs SFX (v1), then **Reaper** (native, more reliable) | ElevenLabs sound effects, a licensed SFX library, Reaper / ReaScript |
| Music | Composed from a bought pack ("Film Score Collection 3"-style) | Any licensed stem pack, or generated music |
| Footage | His own cloud clip library | Your own B-roll bank, plus generated images and video (section 7) |
| Style memory | DNA → Signatures → Library → Boards (beta) | `templates/style-dna.yaml` + `CLAUDE.md` memory |

## 4. Key concepts: DNA, signatures, library

- **DNA:** a written breakdown of an edit's style. That covers pacing (cut lengths), typography, colour
  grade, camera moves, transitions, effects and sound-design rules. Making it is the expensive
  first pass.
- **Signature:** a saved DNA that you can call by name to restyle a new script ("make this in the
  *Satire-Interview* signature").
- **Library:** single techniques pulled out of a DNA (e.g. *match cut*, *text bloom*) so you can
  mix them into other edits.
- **Boards:** moodboards (beta in the app, unused in the video).

Reproduce this with `templates/style-dna.yaml`. Fill it once per reference, save it under
`styles/<name>.yaml`, and point Claude at it in every later prompt.

## 5. The workflow, step by step

### Step 0: Set up (once)
1. Make a project folder: `refs/`, `footage/`, `audio/`, `frames/`, `styles/`, `out/`.
2. Check the tools: `ffmpeg`, `ffprobe`, and your editor of choice (AE with `aerender`, Resolve, or
   `npx create-video@latest` for Remotion). Add an ElevenLabs API key, or plan to generate audio by hand.
3. Put your **footage bank** in `footage/` with a short `footage/INDEX.md` (one line per clip:
   file, what's in it, framing, energy). Claude picks better clips when it can read descriptions.
4. Add your personal rules to `CLAUDE.md` (fonts, colours, "no heavy motion blur on text", etc.).
   This is the "it knows you" part of his system.

### Step 1: Script (storyteller)
Use **Prompt 1** in `templates/prompts.md`. Give the topic, the tone (he went "satire, overdo it"),
the target length, and the reference's structure (hook → body → payoff). Ask for a timed script.

### Step 2: Voice-over
- Ask Claude for an **ElevenLabs v4 prompting guide** tailored to the script: voice choice, delivery
  tags, pauses, emphasis (**Prompt 2**).
- Generate the MP3 (by hand in the web app like he did, or through the API/MCP), then **listen all the
  way through** before moving on. He approved it before saying "go".
- Get word-level timestamps (ElevenLabs alignment, Whisper, or `creative_transcribe_audio`) so
  cuts and captions land on words.

### Step 3: Extract the reference's DNA (the slow first pass)
**Prompt 3.** Claude should:
1. `ffprobe` the reference for fps, resolution and duration.
2. Detect cuts: `ffmpeg -i ref.mp4 -vf "select='gt(scene,0.3)',showinfo" -f null -` → cut list.
3. Build contact sheets (`scripts/contact_sheet.sh ref.mp4 frames/ref`) and **look at them**.
4. Write the DNA (`templates/style-dna.yaml`): shot list with timings, typography, grade, motion,
   transitions, effects and SFX hits.

### Step 4: Build the edit (one prompt, then go away)
**Prompt 4**, the "do your thing" prompt. Key parts from the video:
- "Recreate the edit in `refs/` with my script and VO. **Use whatever tool you want**
  (After Effects / Blender / Remotion)."
- "Use clips from `footage/` for the talking-head and match-cut shots."
- "**Do the sound design too.**"
- "Check your own work by extracting frames at every cut and comparing them with the reference."

### Step 5: Self-check loop (the frame grid in the video)
After each render, Claude runs `scripts/contact_sheet.sh out/draft.mp4 frames/draft`. Then it
compares the sheet with the reference sheet and fixes differences **before** showing you. Things to
check: text clipping or safe margins, grade against the reference, cut timing against VO words,
black or duplicate frames, and audio peaks (`ffmpeg -af ebur128`).

### Step 6: Notes pass (the "second shot")
Watch it **once**, write **all** notes in **one** clear prompt (**Prompt 5**). His real notes were:
- "Colours are way too punchy." → pull saturation and contrast back toward the reference.
- Fix the on-screen **name** text.
- "No motion blur on this text."
- "Add a bloom/glow on this text."
- "Go through my library and pick **better, more varied footage for the match cut**."

Be specific: give a timestamp, the element, and the change. He warns that rambling speech-to-text
notes **steer it the wrong way**.

### Step 7: Sound design
- Hit list from the DNA: whooshes on transitions, risers into reveals, impacts on title slams,
  UI clicks on screen-recording moments, room tone under VO.
- v1: ElevenLabs sound effects per hit (**Prompt 6**). Better: a curated, licensed SFX library mixed
  in **Reaper** (he's moving there for consistent quality).
- Music: cut a licensed score pack to the edit's beats, and duck it under the VO (sidechain or
  ffmpeg `sidechaincompress`).
- Target about −14 LUFS integrated for social video.

### Step 8: Save the style (signature + library)
**Prompt 7.** Save the final DNA as `styles/<signature>.yaml`. Pull reusable techniques
(match cut, text bloom, Apple-style title) into `styles/library/*.md`, each with its own
parameters. Next time: "Make a new edit from this script in the `<signature>` signature." That's
the fast path.

### Step 9: Make it yours
Mix techniques from several signatures rather than shipping a 1:1 copy, and credit any creator you
studied.

## 6. Effects and cuts catalog

What shows up in the video and its edit, with how to build each one:

| Effect | What it is | How to build it |
|---|---|---|
| **Apple-style kinetic title** | Small lead-in line ("It's called the") over a large bold title ("Pocket Creative Director."), clean sans (SF Pro / Inter), white, lower-left, with a full stop | AE text layers with a soft opacity + Y-offset ease-in (~8–12 frames, ease-out-cubic) and a slight stagger per line. Remotion: `spring()` on `translateY` + opacity |
| **Blurred talking-head background** | Speaker defocused behind the title for legibility | Gaussian blur 20–40px on the footage layer while the title is up, animated in and out. ffmpeg: `gblur=sigma=20` |
| **Text bloom / glow** | Soft halo on white text | Duplicate the text, blur it 10–30px, blend Add/Screen at 40–70%, or use AE Glow. CSS: `filter: drop-shadow(0 0 12px #fff8)` |
| **Motion blur on text** (removed in the notes) | Smears fast text moves | AE motion blur toggle / shutter angle. **Turn it off on typography** if it looks smeary |
| **Match cut** | Cut between two shots that share a shape, position or motion | Line up the subject's position and scale across the cut. Use varied source clips (his note) |
| **Interview / reference cutaways** | Showing the original video inside the edit | Picture-in-picture or full-frame cutaway with a lower-third name card |
| **Name card** | Large white name on a light grey field ("Johannes Forseth") | Solid background + bold title. Check spelling (one of his notes) |
| **Screen-recording + webcam bubble** | The breakdown video's own format | Screen capture full-frame, with the webcam scaled ~25% in the bottom-right corner with rounded corners |
| **Colour grade** | Match the reference, not over-punchy | Lumetri / Resolve: lower saturation and contrast, neutral whites. ffmpeg: `eq=saturation=0.9:contrast=1.0` |
| **Hard cuts on VO words** | Pacing from narration | Cut on word boundaries from the timestamps. Trim breaths |
| **Sound design hits** | Whoosh / riser / impact / UI click | One hit per visual event from the DNA hit list |

## 7. Where image generation fits

The video itself doesn't generate images. His visuals are recreated motion graphics plus his own
footage. If you have **no footage bank**, generated stills and clips can fill the same slots in the
DNA:

1. **Match-cut pairs:** generate two images with the same composition and different subjects
   (same camera angle, subject centred, same scale). Keep everything except the subject fixed in
   the prompt so the cut lines up.
2. **B-roll stills → motion:** generate a still, then image-to-video (or a Ken Burns
   `zoompan` in ffmpeg) for 2–3 s cutaways.
3. **Backgrounds for kinetic type:** soft abstract gradients or out-of-focus room shots that keep
   the title readable.
4. **Thumbnail:** blurred speaker + large Apple-style title, just like the video's thumbnail.

Prompt pattern for consistency (put it in the DNA so every image matches):

```
[subject], [action], [shot type + lens, e.g. "medium close-up, 50mm"],
[lighting from DNA, e.g. "soft window light, warm neutral"], [grade from DNA, e.g. "muted, low contrast"],
[aspect ratio of the edit], no text, no watermark
```

Tools that can do this from Claude Code include the Higgsfield, ManyMotions, ElevenLabs (full
connector) and JsonCut MCP servers, or any image API. Upscale before compositing, and keep a
fixed seed or reference image for character consistency.

## 8. Lessons and pitfalls from the video

- **A system beats a smarter model.** Write guidelines, DNA files and memory, and reuse them.
- **The first recreation is expensive; reuse is cheap.** Always save the signature.
- **Give clear, batched notes.** Vague or rambling direction sends the agent the wrong way.
- **Let it check itself visually.** Frame extraction catches problems before you watch the render.
- **Listen to the VO before building.** Everything is timed to it.
- **Watch the colours.** The first pass came out too saturated.
- **Use native audio tools (Reaper) and a curated SFX library** for consistent sound.
- **Respect the source.** Recreating a style to learn it is fine. Publish your own remix and credit the original.

## Files in this folder

| File | Purpose |
|---|---|
| `templates/prompts.md` | Copy-paste prompts 0–7 for every step above |
| `templates/style-dna.yaml` | The DNA / signature template |
| `scripts/contact_sheet.sh` | Scene-cut detection + frame grids for the self-check loop |
