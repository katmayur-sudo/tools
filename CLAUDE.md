# Notes for Claude

## Video voice-over

- Always narrate videos with the owner's cloned ElevenLabs voice **"dr mak"** (Dr. Mac),
  `voice_id: s0DMVIZPbbCMs31sURvA`. Never pick a stock or library voice unless the owner asks.
- It is cloned from a Hindi speaker with a Haryanvi accent: use a multilingual model and write
  the script in the language the owner wants (Hindi, English or Hinglish).
- If the voice can't be found, stop and ask instead of substituting another voice.
- 2026-11-01: the ElevenLabs connector's workspace lists it as "Dr mak", `voice_id: i8eMY5Sai8UQByZW6Pv3`
  (cloned, hi, Haryanvi), and refuses to speak with it: "Instantly cloned voices are not available on your current
  plan." Until the owner upgrades or says otherwise, don't generate; ask.

## Psychiatry content source

- For anything psychiatry-related, take facts **only** from Davidson's Principles & Practice of Medicine,
  **24th edition (2022)**, and cite printed page numbers. Mark anything from outside the book as such.
- The owner shares the book as a Google Drive PDF. The link is deliberately not stored here because this repo
  is public; ask the owner for it, then `curl -L "https://drive.google.com/uc?export=download&id=<ID>"` into the
  scratchpad and search it with `pdftotext`. Never commit the PDF.
- Notes already extracted from the book live in `notes/davidson/` (start there).

## Psychology reel series (BHMS exam content)

- Topic list, exam pattern and reel order: `notes/bhms-psychology/topics.md`, mapped from the NCH First BHMS
  syllabus (owner shares it as a Drive PDF; don't commit it). The syllabus says what to teach, not the facts.
- Owner's rule: this series follows the BHMS (homoeopathy degree) syllabus, i.e. what BHMS students are taught.
  The Davidson-only rule above is for psychiatry content, not for this series. Each reel covers its topic's
  learning objectives.
- **Facts for every reel come only from the owner's psychology textbook** (owner's rule, 2026-11-01):
  *Introduction to Psychology*, Saylor Foundation edition (783 pages, CC BY-NC-SA 3.0; not Morgan's, never cite
  it as Morgan). Shared as a Drive PDF: ask for the link, download it to the scratchpad, search with `pdftotext`, and
  never commit it. `topics.md` gives the book pages for each topic and flags what the book lacks; mark anything
  from outside the book as such. Don't name the book in the reels (owner's rule).
- Reels are built in `videos/bhms-psychology/` (scripts in `reels/*.json`, readable `SCRIPTS.md`). The owner picks
  which topics become reels; reels 1–7 have scripts and silent first cuts (voice-over pending).

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
- `watch` (v0.2.0, MIT, from github.com/taoufik123-collab/claude-watch): `/watch <url-or-path> [why]`
  lets Claude watch a video: scene-change frames, pacing (cuts/min), a 0-10s hook microscope, and a
  transcript, written to `report.md`. Needs ffmpeg (installed) and yt-dlp for URLs: `pip install
  yt-dlp` each cloud session. It only pulls English captions; Hindi/Hinglish or local files need a
  Groq/OpenAI Whisper key in `~/.config/watch/.env`, else frames only. Only the skill is installed,
  not the plugin's hook; the Obsidian steps skip when no vault exists.

When the owner uploads a new skill (zip or folder), read every file before installing, then put
it in `.claude/skills/<name>/` in this repo (not `~/.claude/skills`, which cloud sessions lose),
add it to this list, and merge it to `main` so every new session has it.
