# Delirium vs Dementia

Animated explainer (Hinglish) for medical students: what the two are, 8 differences, 4 myths, simple
management, and an exam one-liner. Facts from Davidson's Principles & Practice of Medicine, 24th ed
(see `notes/davidson/delirium-dementia.md` and the sources in `script.json`). Two formats from one renderer:
1080×1920 for Reels / Shorts and 1920×1080 for YouTube. Rendered media and the owner's audio are not stored here.

```bash
# silent cut timed from script.json's wpm (music + sfx only)
python3 ../psychiatry-classification/timeline.py script.json timeline.json
python3 mix.py timeline.json mix.wav
node render/render.mjs timeline.json 1080x1920 reels.mp4 mix.wav
node render/render.mjs timeline.json 1920x1080 youtube.mp4 mix.wav

# with the owner's voice-over: clean + tighten it (see ../psychiatry-classification/README.md), then
python3 ../psychiatry-classification/timeline.py script.json timeline.json vo.wav
python3 mix.py timeline.json mix.wav vo.wav
# ...and render both sizes as above
```
