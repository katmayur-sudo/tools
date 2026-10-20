# Start Your Engine: the best gym exercises for beginners

A 7:41 YouTube explainer for [Dr Mak Fitness](https://www.youtube.com/@drmakfitness) (1920×1080, 30 fps), made entirely by Claude Code:
script, the owner's cloned voice-over ("dr mak"), word-synced motion graphics, animated exercise
figures, sound design and the thumbnail. Its editing style is the `red-ink-explainer` signature
(`/styles/red-ink-explainer.yaml`), learned from two reference videos.

The rendered video, the generated images and the owner's photos are **not** stored in this repo.

## What the references taught

| | Reference A — [WK2Aam_rC5c](https://youtu.be/WK2Aam_rC5c) | Reference B — [aWPUyUM-2Ig](https://youtu.be/aWPUyUM-2Ig) |
|---|---|---|
| Subject | Turning raw footage into a pro edit with Claude Code skills (cutaway + finish), DaVinci Resolve MCP, Remotion | Making motion graphics with Claude Code + a motion MCP, layered on real footage |
| Look | Light, clean, centered text screens; word captions with a red keyword box; counters, progress bars, text bubbles | Dark background, red light leaks, rounded dark cards, glowing keyword pills, red ribbons |
| Rhythm | No dead air, punchy cuts, "style library" reused per video | Hook of one idea every 2-3 s, "the old way" crossed out with red ✕, word slams |
| Voice | Casual, confident walkthrough | Fast, energetic, question-led hook ("What if I told you…") |

Both lean on the same idea as the Pocket Creative Director video in `workflows/`: a written style
system that the agent reuses, rather than one-off prompting.

## Structure (7:41)

| Time | Section | Visual idea |
|---|---|---|
| 0:00 | Hook | Owner's back photo full-bleed, "ENGINE." slam, old way crossed out, 3-step roadmap |
| 0:19 | Part 1 · The Engine | Metabolism, where daily calories go (60-70% / ~10% / rest), muscle vs fat at rest (owner photo) |
| 1:05 | The three gears | ATP-PC ~10 s, glycolysis ≤2 min, aerobic for hours; glucose uptake; afterburn; mitochondria |
| 1:51 | Part 2 · Ignition sequence | 5-min warm-up timer and checklist |
| 2:18 | 8 exercises | Goblet squat, dumbbell RDL, incline push-up, one-arm row, seated press, step-up, farmer's carry, dead bug — each with an animated figure, cues, the common mistake and the dose |
| 5:46 | Finisher | 10 min zone-2 cardio |
| 5:59 | Part 3 · The Plan | 3 full-body days, 2-3 × 8-12, 60-90 s rest, 2-3 reps in reserve, double progression |
| 6:37 | Fuel & maintenance | 1.6 g/kg protein, 7-9 h sleep, 7-8k steps |
| 6:54 | Mistakes, outro | Owner photo, recap, doctor disclaimer, save CTA |
| 7:29 | End screen (12 s) | @drmakfitness identity, voiced subscribe CTA with animated click + bell, two empty frames for YouTube end-screen videos |

## Visual and sound design

- **No stock images.** Every illustration is code-drawn motion graphics: a spinning engine turning
  food into energy, a sleeping moon with a still-burning flame, a glowing mitochondrion emitting ATP,
  a warming thermometer, a beating heart with an ECG trace, a protein calculator (70 kg → 112 g),
  a sleep clock and a step odometer. The only photos are the owner's.
- **Engagement devices:** camera punch-ins with a red flash on key lines, word-synced captions,
  exercise progress dots, a rep counter synced to each animated figure, red stingers per exercise.
- **Sound design (16 synthesized effects):** riser into chapters, whoosh + hit on stingers, boom on
  big claims, error buzz on mistakes and crossed-out items, tick on checklists, ding on doses and
  wins, gear clunks for the three gears, counter rattles on numbers, a soft thud on every rep,
  heartbeat under the cardio finisher, click + bell on the subscribe button. Effects sit ~8 dB under
  the voice; music is side-chain ducked; master at -14 LUFS.

## Rebuild it

```bash
# 1. voice-over: one ElevenLabs generation per section of script.json with the dr mak voice → vo/<id>.mp3
# 2. word timings (script words, Whisper timings)
python3 tools/transcribe.py script.json vo words.json
# 3. timeline: scenes, word cues, captions, sfx
python3 tools/build_timeline.py script.json words.json vo timeline.json
# 4. (optional) B-roll stills; the current cut uses motion graphics instead of stock images
python3 tools/fetch_images.py img
python3 tools/add_images.py timeline.json img
# 5. soundtrack (synth music + sfx + voice, -14 LUFS)
python3 tools/make_audio.py timeline.json vo audio
# 6. frames → video (site/render/index.html + site/assets/{img,user})
node render/render.mjs site timeline.json chunks 4
tools/finish.sh chunks audio/mix.wav beginner-gym-engine.mp4
```

`render/thumbnail.html` renders the 1280×720 thumbnail from the same assets.

## Fact basis for the script

Resting metabolic rate ≈ 60-70% of daily energy use; thermic effect of food ≈ 10%; skeletal muscle
≈ 13 kcal/kg/day vs fat ≈ 4.5 kcal/kg/day at rest; phosphagen system ≈ 10 s, glycolysis up to ~2 min;
contraction-driven GLUT4 glucose uptake; EPOC after resistance training is real but modest;
endurance training increases mitochondrial content; protein ≈ 1.6 g/kg/day for muscle gain.
