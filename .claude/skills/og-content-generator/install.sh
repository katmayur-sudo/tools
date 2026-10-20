#!/usr/bin/env bash
# Install the og-content-generator skill for Claude Code on this computer.
#
#   ./install.sh            personal install  -> ~/.claude/skills/og-content-generator (every project)
#   ./install.sh --project  project install   -> ./.claude/skills/og-content-generator (current repo)
#   ./install.sh --zip      build og-content-generator.zip for uploading to Claude chats
#
# Re-run after `git pull` to update. Checks the render dependencies and says what is missing.
set -euo pipefail
src="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
name="og-content-generator"

case "${1:-}" in
  --zip)
    out="$(pwd)/$name.zip"
    rm -f "$out"
    (cd "$src/.." && zip -qr "$out" "$name" -x "$name/install.sh")
    echo "built $out (upload in Claude: Settings > Capabilities > Skills > Upload skill)"
    exit 0 ;;
  --project) dest="$(pwd)/.claude/skills/$name" ;;
  *) dest="$HOME/.claude/skills/$name" ;;
esac

if [ "$(cd "$src" && pwd)" != "$(mkdir -p "$dest" && cd "$dest" && pwd)" ]; then
  rm -rf "$dest"
  mkdir -p "$(dirname "$dest")"
  cp -R "$src" "$dest"
fi
echo "installed -> $dest"

missing=0
check() { if command -v "$1" >/dev/null 2>&1; then echo "  ok   $1"; else echo "  MISSING $1  ($2)"; missing=1; fi; }
echo "dependencies:"
check node "Node.js 20+ from nodejs.org"
check ffmpeg "brew install ffmpeg / apt install ffmpeg / winget install ffmpeg"
check python3 "python.org"
python3 -c "import numpy" 2>/dev/null && echo "  ok   numpy" || { echo "  MISSING numpy  (pip install numpy)"; missing=1; }
node -e "import('playwright').then(()=>process.exit(0)).catch(()=>process.exit(1))" 2>/dev/null \
  && echo "  ok   playwright" || echo "  note playwright not found locally: npm i -g playwright && npx playwright install chromium (or set PLAYWRIGHT_MODULE)"
[ "$missing" = 0 ] && echo "ready: ask Claude Code for a launch film, trailer or reel - it storyboards first." || echo "install the missing tools, then re-run."
