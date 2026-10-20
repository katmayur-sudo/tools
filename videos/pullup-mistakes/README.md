# 5 Pull-Up Mistakes: refined short

A refined version of the owner's YouTube Short "5 Pull-Up Mistakes Killing Your Back Gains". It reuses
the original "dr mak" voice-over, re-cut from 45.7 s down to 36.2 s, and renders in two grades:

| Grade | Look |
|---|---|
| `porcelain` | The keynote launch-film look: warm porcelain canvas, Inter Display, one red accent, a soft push on every cut and a bright 124 BPM groove. |
| `redblack` | The channel's dark look: black with deep-red glow and neon tubes, Anton captions with yellow keywords, a red slash on each cut, grain and a dark 120 BPM bed. |

**A 3D athlete does the reps, and the owner's photos appear only in the intro and outro.**

- **3D athlete** (three.js r158, procedural, no model files): clay-style in `porcelain`, glossy black with
  red rim lights in `redblack`.
- **Pull-up rig:** a 2-bone inverse kinematics (IK) solver puts the arms on the bar. The athlete can shrug,
  lean, swing its legs and drop.
- **Muscles:** lats, traps, arms and core are separate meshes that glow green (fix) or red (mistake).
- **Shadow:** the athlete's shadow falls on a shadow-catcher wall.
- **Camera:** it orbits and pushes in on each scene.
- **Motion graphics:** arrows, callout pins, rings and range lines are pinned to projected 3D joints, so
  they stick to the body.
- **Intro and outro:** the back photo (hook) and the side mirror photo (follow card) are rembg cut-outs
  graded to match.

## Pipeline

```bash
F=<film_dir>                       # scratch dir; never commit the photo or renders
python3 tools/build_timeline.py source.mp4 $F            # vo.wav (re-cut voice) + timeline.json
python3 -c "from rembg import remove,new_session;from PIL import Image;s=new_session('u2net_human_seg');\
[ (lambda o:o.crop(o.getbbox()).save(f'$F/assets/{n}.png'))(remove(Image.open(f'{n}.jpg'),session=s)) for n in ('back','side')]"
# + $F/assets/anton.woff2 (Google Fonts, latin subset) and three.min.js (npm pack three@0.158.0 -> build/)
python3 tools/mix.py $F redblack $F/mix_redblack.wav     # bed + SFX on cues, -14 LUFS
node render/render.mjs $F redblack $F/stills --stills 5,10,20    # style frames
node render/render.mjs $F redblack $F/video.mp4                  # WebGL via SwiftShader, 4 workers, ~5 min
ffmpeg -i $F/video.mp4 -i $F/mix_redblack.wav -map 0:v -map 1:a -c:v copy -c:a aac -shortest out.mp4
```

- `build_timeline.py` holds the kept voice lines, the Hinglish caption text, and the scene and animation
  cues as source times.
- Athlete proportions (`BAR_Y`, `GRIP`, `UA`, `FA`), default camera framing and muscle meshes are in
  `build3D()` and `pose()` in `render/short.html`.
