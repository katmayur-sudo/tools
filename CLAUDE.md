# Notes for Claude

## Video voice-over

- Always narrate videos with the owner's cloned ElevenLabs voice **"dr mak"** (Dr. Mac),
  `voice_id: s0DMVIZPbbCMs31sURvA`. Never pick a stock or library voice unless the owner asks.
- It is cloned from a Hindi speaker with a Haryanvi accent: use a multilingual model and write
  the script in the language the owner wants (Hindi, English or Hinglish).
- If the voice can't be found, stop and ask instead of substituting another voice.

## Video workflow

See `workflows/pocket-creative-director/` for the edit workflow, prompts and style DNA template.
Saved style signatures live in `styles/` (e.g. `styles/red-ink-explainer.yaml`); reuse them by name.
`videos/beginner-gym-engine/` is a full worked example (script, timeline, HTML renderer, audio mix).
Keynote-style launch films: use the `porcelain-keynote-film` skill in `.claude/skills/`.
Never commit the owner's photos or rendered media to this repo.
