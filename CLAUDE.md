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
Keynote-style launch films: use the `og-content-generator` skill in `.claude/skills/` (storyboard first, always).
Never commit the owner's photos or rendered media to this repo.

## Installed skills (`.claude/skills/`)

Use these whenever the request matches. They load automatically from this repo.

- `og-content-generator`: keynote-style launch films, trailers, brand films; storyboard first.
- `short-reel-editor`: raw talking-head footage + script → finished 9:16 Reel/Short, with an
  approval gate at every stage. Supports English, Hindi and Hinglish: ask the language and, for
  Hindi/Hinglish, whether captions are Roman Hinglish or Devanagari, then use `--lang hi`.
  Always pass "Dr. Mak" and the script's English terms via `--prompt` and `fix`.
- `prompt-master`: writes or fixes a prompt for a specific AI tool (Claude Code, ChatGPT,
  Midjourney, Sora, ElevenLabs…). Confirm the target tool first.
- `graphify` (v0.9.93, Apache-2.0): `/graphify <path>` turns a folder of code, docs, PDFs,
  images or video into a queryable knowledge graph (`graphify-out/`: graph.html,
  GRAPH_REPORT.md, graph.json); then `/graphify query "…"`, `path`, `explain`. It installs the
  `graphifyy` CLI from PyPI on first run (cloud sessions lose it, so each session reinstalls).
  Code needs no API key; never ask for one. Keep `graphify-out/` out of commits (it's gitignored).
- `ponytail` (v5.3.2, MIT, from github.com/DietrichGebert/ponytail): lazy senior dev mode for
  coding tasks, the smallest complete change; `/ponytail lite|full|ultra`, "stop ponytail" ends it.
  Siblings: `/ponytail-review` (review a diff), `/ponytail-audit` (whole repo, ranked),
  `/ponytail-debt` (list `shortcut:` comments), `/ponytail-gain`, `/ponytail-help`. Only the skills
  are installed, not the plugin's hooks, so it is not auto-on and the band/board/config in
  `/ponytail-help` don't apply here. Not for video or script work.

When the owner uploads a new skill (zip or folder), read every file before installing, then put
it in `.claude/skills/<name>/` in this repo (not `~/.claude/skills`, which cloud sessions lose),
add it to this list, and merge it to `main` so every new session has it.
