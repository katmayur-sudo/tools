# Storyboard · "No gym? 6 moves. Whole body." (v5_six_zones_home)

9:16 short, ~35 s, Dr Mak Fitness style (`render/verticals.js`): owner photo + slam hook as the intro,
follow card as the outro, red accent #E0262B, word-synced captions, code-drawn exercise figures.
Voice: the cloned **dr mak** ElevenLabs voice (`s0DMVIZPbbCMs31sURvA`, eleven_multilingual_v2).

**Idea source:** [this Short](https://www.youtube.com/shorts/xLpbXcIwQpk), a static chart of 6 body zones with
3 moves each and reps per set. We keep the idea (one move per zone, rep targets) and redraw
everything ourselves: none of its footage, artwork or music is reused. The rep targets are adjusted
for a no-equipment routine.

**Structure: looped arc.** Hook → rising action → conflict → comeback → payoff.

| # | Time | Arc beat | Voice-over | Screen |
|---|---|---|---|---|
| 1 | 0.0–3.5 | **Hook** (intro) | No gym? No problem. Six moves. Your whole body. Twelve minutes. | Owner B&W photo full-bleed, "No gym?" → slam "6 MOVES. WHOLE BODY." with boom; a 12:00 timer pill |
| 2 | 3.5–5.0 | Rising | Legs: squats, fifteen reps. | Body-zone map lights LEGS; animated squat figure; "15" rep counter |
| 3 | 5.0–6.5 | Rising | Chest: push-ups, twenty. | CHEST zone; push-up figure; "20" |
| 4 | 6.5–8.0 | Rising | Arms: chair dips, fifteen. | ARMS zone; chair-dip figure; "15" |
| 5 | 8.0–9.5 | Rising | Shoulders: pike push-ups, ten. | SHOULDERS zone; pike push-up figure; "10" |
| 6 | 9.5–11.0 | Rising | Abs: dead bugs, ten each side. | ABS zone; dead-bug figure; "10 / side" |
| 7 | 11.0–12.3 | Rising | Fat burn: jumping jacks, thirty seconds. | FAT BURN zone; jumping-jack figure; 0:30 countdown. All 6 zones now lit = the full chart |
| 8 | 12.3–17.1 | **Conflict** | Round two. Your arms start shaking. Your form breaks. This is where most people quit. | "ROUND 2" stinger; figure wobbles (camera shake), form line turns red with ✕; "most people quit" with error buzz, screen dims |
| 9 | 17.1–23.2 | **Comeback** | Don't quit. Drop to your knees for push-ups. Slow every rep down. Rest thirty seconds, then finish the round. | Hard cut back to light; "DON'T QUIT" punch-in; knee push-up figure; slow-rep metronome; 0:30 rest ring; round bar fills |
| 10 | 23.2–31.6 | **Payoff** | Three rounds, three days a week. Add two reps every week. That's how a home workout builds muscle. Save this and follow for the full plan. | 3 × 3 grid (rounds × Mon/Wed/Fri); reps staircase +2/week; "BUILDS MUSCLE" red pill; small doctor-disclaimer line |
| 11 | 31.6–34.9 | Outro | (none) | Follow card: @drmakfitness / @drmak_fitness, animated click |

The rising action stacks the six zones into one chart, as the Short does. The conflict breaks it at
round two, and the comeback loops back into the same chart, so the payoff lands on a finished plan.

## Build (as made, 2026-10-20)
English, voice take 1 of 4 (31.4 s). From `videos/beginner-gym-engine/tools`, with the owner's photos in
`<site>/assets/user/{back,side}.jpg` (never committed) and `<site>/render` a copy of `../render`:

```bash
PYTHONPATH=. python3 ../shorts/build.py ../../home-six-zones/script.json <vo_dir> <data_dir>   # vo_dir/v5_six_zones_home.mp3
node <site>/render/verticals.mjs <site> <data_dir> yt <out_dir>
ffmpeg -i <out_dir>/v5_six_zones_home_yt_video.mp4 -i <data_dir>/v5_six_zones_home_audio.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest final.mp4
```

**Hinglish version** (`v5_six_zones_home_hi`, voice take 4 of 4, 40.3 s): ElevenLabs gets `tts` (Hindi words in
Devanagari for natural pronunciation), captions use `text` (Roman Hinglish). `style` reuses the English
short's scenes and sound design; `cue_phrases` maps each scene cue to the Hinglish words that trigger it.
Build only it with `build.py … <data_dir> v5_six_zones_home_hi`, render with `yt` and `ig`.
