# BHMS Psychology reels

9:16 reels (1080×1920, 30 fps) for BHMS students, one per syllabus topic in
`../../notes/bhms-psychology/topics.md`. Hinglish narration, code-drawn motion graphics, word-highlighted captions,
synth music and sfx. Facts come from the owner's textbook (see `CLAUDE.md`); the reels never name the book.

- `reels/NN-*.json`: one script per reel: scenes (`hook`, `title`, `define`, `points`, `compare`, `card`, `iceberg`,
  `triangle`, `exam`, `close`), each with its on-screen fields, the spoken `vo` (also the captions), an optional `tts`
  (how to say it, e.g. "two eleven" for §211) and `cues` (words in `vo` that bring each item on screen).
- `SCRIPTS.md`: the readable scripts, generated: `python3 scripts_md.py > SCRIPTS.md`.

Rendered video and audio are not stored in this repo.

```bash
# once per session: Hindi font for Chromium (Mukta, OFL, from npm)
npm pack @fontsource/mukta@5.3.0 && tar xzf fontsource-mukta-5.3.0.tgz && pip install fonttools brotli
for w in 500 600 700 800; do for s in devanagari latin; do python3 -c "import sys; from fontTools.ttLib import TTFont; f = TTFont(sys.argv[1]); f.flavor = None; f.save(sys.argv[2])" package/files/mukta-$s-$w-normal.woff2 ~/.fonts/Mukta-$s-$w.ttf; done; done; fc-cache -f

# silent first cut (timing estimated from the words)
python3 timeline.py reels/01-what-is-psychology.json tl.json
python3 mix.py tl.json mix.wav            # add a voice-over wav as 3rd arg to duck the music under it
node render/render.mjs tl.json out.mp4 mix.wav
node render/render.mjs tl.json stills/ --stills 3,20,40   # review stills
```

Voice-over: not done yet. The owner's ElevenLabs clone ("Dr mak") is an instant clone, which the current plan can't
use. Once there's a voice-over, `timeline.py` needs real timings (per-scene clips, or Whisper alignment as in
`../psychiatry-classification/timeline.py`) instead of the estimate.
