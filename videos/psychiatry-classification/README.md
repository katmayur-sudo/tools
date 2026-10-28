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

# with the owner's voice-over: clean it (RNNoise model: github.com/richardpl/arnndn-models std.rnnn),
# cut breaths and long pauses, re-time to it, mix music + sfx at -14 LUFS, then render
ffmpeg -i raw.mp3 -ac 1 -af "adeclip,highpass=f=80,aresample=48000,arnndn=m=std.rnnn:mix=0.95,afftdn=nf=-45:tn=1,equalizer=f=250:t=q:w=1.2:g=-2.5,equalizer=f=3500:t=q:w=1.5:g=2.5,equalizer=f=10000:t=h:w=0.7:g=1.5,deesser=i=0.35,acompressor=threshold=-22dB:ratio=3:attack=8:release=120:makeup=2,loudnorm=I=-16:TP=-1.5:LRA=7" -ar 48000 vo_clean.wav
python3 tighten.py vo_clean.wav vo.wav
pip install faster-whisper
python3 timeline.py script.json timeline.json vo.wav
python3 mix.py timeline.json vo.wav mix.wav
node render/render.mjs timeline.json out.mp4 mix.wav

# review stills
node render/render.mjs timeline.json stills/ --stills 2,16,75
```

`timeline.py` reuses `../beginner-gym-engine/tools/transcribe.py` for the Whisper alignment, so
captions always show the script's spelling.
