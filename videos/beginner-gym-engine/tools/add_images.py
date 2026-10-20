"""Record which generated images exist so the renderer can fall back for missing ones.

Usage: python3 add_images.py <timeline.json> <img_dir>
"""
import json
import pathlib
import sys

tl_path, img_dir = sys.argv[1:3]
tl = json.load(open(tl_path))
tl["images"] = sorted(p.stem for p in pathlib.Path(img_dir).glob("*.jpg") if p.stat().st_size > 20000)
json.dump(tl, open(tl_path, "w"), indent=1)
print("images:", tl["images"])
