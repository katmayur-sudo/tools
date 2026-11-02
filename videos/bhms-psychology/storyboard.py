"""Storyboard PDF: one still per scene with its voice-over line underneath, 8 scenes per page.

Usage: python3 storyboard.py <reel.json> <timeline.json> <work_dir> <out.pdf>
Renders the stills with render/render.mjs into work_dir/stills first.
"""
import json
import os
import subprocess
import sys
import textwrap

from PIL import Image, ImageDraw, ImageFont

reel, tl_path, work, out = sys.argv[1:5]
r, t = json.load(open(reel)), json.load(open(tl_path))
at = [f"{b['end'] - .4:.2f}" for b in t["beats"]]  # late in each scene, once everything is on screen
stills = os.path.join(work, "stills")
subprocess.run(["node", os.path.join(os.path.dirname(os.path.abspath(__file__)), "render/render.mjs"), tl_path, stills, "--stills", ",".join(at)], check=True)
F = lambda s: ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Bold.otf", s)
W, H, cols = 2400, 3300, 4
cw, ch, pages = W // cols, H // 2, []
for p0 in range(0, len(r["beats"]), 8):
    pg = Image.new("RGB", (W, H), "#0B0D12")
    d = ImageDraw.Draw(pg)
    for k, i in enumerate(range(p0, min(len(r["beats"]), p0 + 8))):
        b, s = r["beats"][i], t["beats"][i]
        x, y = (k % cols) * cw, (k // cols) * ch
        pg.paste(Image.open(os.path.join(stills, f"{at[i]}.jpg")).resize((540, 960)), (x + 30, y + 30))
        d.text((x + 30, y + 1005), f"{i + 1}. {b['type'].upper()}  {s['start']:.0f}-{s['end']:.0f}s", font=F(30), fill="#FFB547")
        d.multiline_text((x + 30, y + 1050), "\n".join(textwrap.wrap(b["vo"], 38)[:10]), font=F(24), fill="#EEEEEE", spacing=6)
    pages.append(pg)
pages[0].save(out, save_all=True, append_images=pages[1:], resolution=150)
print(out, len(pages), "pages")
