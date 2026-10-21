# short-reel-editor

A Claude skill that edits raw talking-head footage into a finished 9:16 reel: cut to your script, clean takes, B-roll over every look-down, motion graphics, word-synced captions, sound design and a cover. Every stage stops for your approval.

## Install
- **Claude Code:** copy this folder to `~/.claude/skills/short-reel-editor`, or ask Claude: "Install this skill for me: <repo url>".
- **Claude desktop or web:** Settings → Capabilities → upload `short-reel-editor.zip` as a skill.

## Requirements
- ffmpeg and ffprobe
- Python 3.10+, then `pip install -r scripts/requirements.txt`
- Node.js 18+ (for HyperFrames)

Optional:
- `EPIDEMIC_SOUND_API_KEY` (an Epidemic MCP key) to search and download music and SFX
- your own SFX `.wav` files in `sfx/`

## Licences of bundled files
- Inter, Instrument Serif and JetBrains Mono: SIL Open Font License
- GSAP: GreenSock standard licence (free)
- The safe-zone mask is a layout guide.

Music, SFX and stock footage you add keep their own licences.
