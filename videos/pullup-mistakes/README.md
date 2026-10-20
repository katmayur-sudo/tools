# 5 Pull-Up Mistakes: refined short

A refined version of the owner's YouTube Short "5 Pull-Up Mistakes Killing Your Back Gains". It reuses
the original "dr mak" voice-over, re-cut from 45.7 s down to 36.2 s, and renders in two grades:

| Grade | Look |
|---|---|
| `porcelain` | The keynote launch-film look: warm porcelain canvas, Inter Display, one red accent, a soft push on every cut and a bright 124 BPM groove. |
| `redblack` | The channel's dark look: black with deep-red glow and neon tubes, Anton captions with yellow keywords, a red slash on each cut, grain and a dark 120 BPM bed. |

**The owner's back photo is the athlete in every scene.** The photo is cut out with rembg
(`u2net_human_seg`) and the hanging arms are masked off. The torso then rides a back-view pull-up rig:

- Drawn arms reach the bar with 2-bone inverse kinematics (IK).
- The head is a separate piece, so it can sink into the shoulders during the shrug.
- 3D tilt and ghost copies show the leg swing.
- Muscle overlays sit on the real back: traps, lats, scapula and elbow arrows, and the core lock.

## Pipeline

```bash
F=<film_dir>                       # scratch dir; never commit the photo or renders
python3 tools/build_timeline.py source.mp4 $F            # vo.wav (re-cut voice) + timeline.json
python3 -c "from rembg import remove,new_session;from PIL import Image;\
im=remove(Image.open('back.jpg'),session=new_session('u2net_human_seg'));im.crop((470,580,1030,1536)).save('$F/assets/back.png')"
# + $F/assets/anton.woff2 (Google Fonts, latin subset)
python3 tools/mix.py $F redblack $F/mix_redblack.wav     # bed + SFX on cues, -14 LUFS
node render/render.mjs $F redblack $F/stills --stills 5,10,20    # style frames
node render/render.mjs $F redblack $F/video.mp4                  # 4 workers, about 4 min
ffmpeg -i $F/video.mp4 -i $F/mix_redblack.wav -map 0:v -map 1:a -c:v copy -c:a aac -shortest out.mp4
```

- `build_timeline.py` holds the kept voice lines, the Hinglish caption text, and the scene and animation
  cues as source times.
- The `BODY_CLIP`, `LAT_*` and `TRAPS` shapes in `render/short.html` are drawn for that specific photo
  crop. Redraw them if the photo changes.
