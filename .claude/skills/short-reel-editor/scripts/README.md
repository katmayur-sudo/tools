# Pipeline scripts

Run every script with `python -I` from your project folder. They find ffmpeg on PATH, or through the `FFMPEG` / `FFPROBE` environment variables.

| Step | Command | Output |
|---|---|---|
| Audio for ASR | `ffmpeg -i raw.MOV -ac 1 -ar 16000 raw16.wav` | `raw16.wav` |
| Transcribe | `transcribe.py raw16.wav words.json` | Whisper words, with repeated takes kept |
| Align | `align.py raw16.wav words.json aligned.json` | Forced-aligned words, printed with their indices for picking takes |
| Gaze | `gaze.py raw.MOV gaze15.json 15 --crop 0.6,0.2,0.36` | Per-sample head pitch |
| Cut | `cut.py cut.json` | `cut/cut.mp4`, `segments.json`, `words_cut.json`, `lookdown.json` |
| Re-cut map | `warp.py old_segments.json new_segments.json warp.json` | Old→new time map |
| Framing | `crop.py cut/cut.mp4 --center-x 515 --out project/assets` | `talk_c.mp4`, `talk_a.mp4` (one fixed crop) |
| Captions | `captions.py captions.json` | `project/assets/captions.js` |
| Music | `beat.py energy *.mp3`, `beat.py phase track.wav 120`, `epidemic.py search "…" 100 128` | Track choice and beat grid |
| Mix | `mix.py mix.json [visual.mp4]` | `audio/mix.wav`, `.m4a`, `mix_with_cut.mp4`, `final.mp4` |
| Safe zones | `safezone.py snaps/ ../assets/safezone_mask.png sheet.jpg` | Overlay sheet |
| Critique | `check.py final.mp4 cut/words_cut.json` | Freeze, black, loudness and intelligibility report |

Example `cut.json`:
```json
{"source": "raw.MOV", "words": "aligned.json", "gaze": "gaze15.json", "out": "cut",
 "picks": [[0, 14], [118, 140], [240, 258, 227.84]],
 "tail": {"14": 0.05}, "post": 0.10}
```

SFX library: put `click pop tick whoosh whoosh2 thud impact error success shutter typing notif riser` `.wav` files in `sfx/`. Epidemic's `epidemic.py sfx`/`sfxget` can fill it.
