# Psychiatric Disorders: How They Are Classified

A 9:16 short (1080×1920, 30 fps, ~85 s) for medical students and junior doctors: the ten ICD-10
blocks (F00–F98) of Davidson's Box 31.1, Medical Psychiatry, plus delirium on medical wards (Box 31.2).
Code-drawn motion graphics (no stock or generated images yet), one accent colour per group,
word-synced captions. Narration is the owner's own recording (`VO_SCRIPT.md`).

Rendered video and audio are not stored in this repo.

```bash
# silent first cut (timing estimated from script.json's wpm)
python3 timeline.py script.json timeline.json
node render/render.mjs timeline.json out.mp4

# with the owner's voice-over: re-time to the recording, then mux it
pip install faster-whisper
python3 timeline.py script.json timeline.json voiceover.wav
node render/render.mjs timeline.json out.mp4 voiceover.wav

# review stills
node render/render.mjs timeline.json stills/ --stills 2,16,75
```

`timeline.py` reuses `../beginner-gym-engine/tools/transcribe.py` for the Whisper alignment, so
captions always show the script's spelling.
