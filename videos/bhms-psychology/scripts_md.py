"""Write SCRIPTS.md (the readable voice-over scripts) from reels/*.json, so the two never drift apart.

Usage: python3 scripts_md.py > SCRIPTS.md
"""
import glob
import json
import re

print("# BHMS Psychology reels: voice-over scripts\n")
print("Generated from `reels/*.json` by `scripts_md.py`; edit the JSON, not this file.")
print("Read each scene as one paragraph with a short pause between scenes. Bold = what appears on screen.\n")
for path in sorted(glob.glob("reels/*.json")):
    r = json.load(open(path))
    print(f"## Reel {r['n']}: {r['title']}\n\n{r['topic']} · {r['tag']}\n")
    for i, b in enumerate(r["beats"], 1):
        screen = b.get("big") or b.get("term") or b.get("name") or b.get("title") or b.get("note") or ""
        screen = re.sub(r"<[^>]+>", "", screen).replace("&nbsp;", " ")
        print(f"{i}. ({b['type']}{': **' + screen + '**' if screen else ''}) {b['vo']}\n")
    if r.get("outside_book"):
        print("Not from the textbook (check before posting): " + "; ".join(r["outside_book"]) + ".\n")
