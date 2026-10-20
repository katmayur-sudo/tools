# Prompt pack

Copy-paste prompts for each step of the workflow in `../README.md`. Replace `<…>`.

## Prompt 0: Preflight

```text
Check this machine is ready to edit video: ffmpeg/ffprobe versions, my editor (<After Effects aerender | DaVinci Resolve | Remotion via npx>),
and whether ELEVENLABS_API_KEY is set. Create refs/ footage/ audio/ frames/ styles/library/ out/ if missing.
Read footage/INDEX.md and CLAUDE.md. Tell me what's missing; don't install anything without asking.
```

## Prompt 1: Script (storyteller)

```text
Write a <30–45>s voice-over script about <topic> for <Instagram Reels>, tone: <satire, over-the-top | calm, premium>.
Structure it like the reference in refs/: hook (first 2s), 3 beats, payoff line.
Return a table: line | target seconds | on-screen text | visual idea. Keep on-screen text to ≤5 words per card.
```

## Prompt 2: ElevenLabs voice-over (my cloned voice)

```text
Voice it with my cloned ElevenLabs voice "dr mak" (voice_id s0DMVIZPbbCMs31sURvA), never a stock voice.
Turn this script into a delivery for that voice: add delivery/emotion tags, pauses and emphasis
per line, and give me the final text to paste. Then <generate it via the API into audio/vo.mp3 | stop so I generate it by hand>.
After I confirm the audio, get word-level timestamps into audio/vo_words.json.
```

## Prompt 3: Extract the DNA

```text
Analyse refs/<reference>.mp4 and write its style DNA to styles/<name>.yaml using templates/style-dna.yaml.
1. ffprobe it; 2. detect cuts (scene threshold 0.3) and list them with durations;
3. run scripts/contact_sheet.sh on it and LOOK at the sheets;
4. fill in pacing, typography (font, size, position, animation timing), colour grade, camera moves, transitions,
   effects (match cuts, glow, blur, motion blur) and a sound-design hit list with timestamps.
Be specific with numbers (frames, px, %, easing). Take your time; this is the slow first pass.
```

## Prompt 4: Build ("do your thing")

```text
Recreate the edit described in styles/<name>.yaml using my script and audio/vo.mp3 (timestamps in audio/vo_words.json).
Use whatever tool you think is best (After Effects, Blender, Remotion, Resolve). I don't care which.
Pick talking-head and match-cut shots from footage/ (see footage/INDEX.md); vary the clips.
Cut on word boundaries. Do the sound design too (hit list in the DNA) and a music bed ducked under the VO, about −14 LUFS.
Before showing me anything: render out/draft.mp4, run scripts/contact_sheet.sh on it, compare against the
reference sheets, fix every difference you find, and repeat until it matches. Then summarise what you changed.
```

## Prompt 5: Notes pass (one batched prompt)

```text
Notes on out/draft.mp4, apply all, then re-run the self-check:
1. Overall: colours too punchy → match the reference grade (less saturation/contrast).
2. <00:04> name card: spelling should be "<Name>".
3. <00:07–00:09> title: remove motion blur on text.
4. <00:12> title: add a soft white bloom/glow (blurred duplicate, Add, ~50%).
5. Match cut at <00:15>: pick different, better-matching clips from footage/; no repeated clips.
```

## Prompt 6: Sound design pass

```text
Build the SFX layer from the DNA hit list: whoosh on each transition, riser into <reveal>, impact on title slams,
soft UI clicks on screen-recording moments, room tone under the VO. Generate each with ElevenLabs sound effects
(or use sfx/ library files if present), place them frame-accurately, keep them under the VO, and export audio/sfx_mix.wav.
If Reaper is installed, build it as a Reaper project so I can tweak it.
```

## Prompt 7: Save as signature + library

```text
The edit is approved. Save the final, corrected DNA as styles/<signature>.yaml (fold my notes in as rules).
Extract each reusable technique (match cut, text bloom, kinetic title, etc.) into styles/library/<technique>.md
with parameters and a short how-to for <tool>. Add a line to CLAUDE.md: "Signatures live in styles/; reuse them".
```

## Reuse (fast path)

```text
Make a new edit from <script/audio> in the <signature> signature. Swap the match-cut technique for library/<x>.md.
Same self-check loop as before.
```
