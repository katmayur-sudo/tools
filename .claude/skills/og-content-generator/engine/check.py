"""Validate a storyboard before anything is rendered.

Usage: python3 check.py <storyboard.json> [--assets <film_dir>]
Exits non-zero with a list of problems; prints a timing table when the storyboard is valid.
"""
import json
import pathlib
import sys

TYPES = {
    "cold": [], "intro": [], "line": ["text"], "slot": ["index"], "ui": ["image"],
    "iconRow": ["icons", "words", "payoff"], "broll": ["image", "line", "phrases"],
    "plate": ["plate", "title"], "chips": ["plate", "title", "chips"], "onemore": [],
    "reveal": ["text"], "closer": ["pre", "word"], "end": [],
}
PLATES = {"sea", "salt", "glacier", "dusk"}
TOP = ["name", "accent", "bpm", "chapters", "scenes"]


def main():
    path = sys.argv[1]
    film_dir = pathlib.Path(sys.argv[sys.argv.index("--assets") + 1]) if "--assets" in sys.argv else None
    sb = json.load(open(path))
    errs, warn = [], []
    for k in TOP:
        if k not in sb:
            errs.append(f"missing top-level '{k}'")
    if errs:
        sys.exit("\n".join(errs))
    beat = 60 / sb["bpm"]
    t, rows, used_slots = 0.0, [], []
    for i, sc in enumerate(sb["scenes"]):
        kind = sc.get("type")
        if kind not in TYPES:
            errs.append(f"scene {i}: unknown type '{kind}'")
            continue
        for f in ["beats"] + TYPES[kind]:
            if f not in sc:
                errs.append(f"scene {i} ({kind}): missing '{f}'")
        if not isinstance(sc.get("beats"), int) or sc.get("beats", 0) < 2:
            errs.append(f"scene {i} ({kind}): 'beats' must be an integer >= 2")
        if kind == "slot":
            if not 0 <= sc.get("index", -1) < len(sb["chapters"]):
                errs.append(f"scene {i}: slot index {sc.get('index')} outside chapters")
            used_slots.append(sc.get("index"))
        texts = sc.get("text", [])
        for line in texts if isinstance(texts, list) else [texts]:
            n = len(str(line).split())
            if n > 9:
                warn.append(f"scene {i} ({kind}): line has {n} words, keep lines to 2-7 words")
        for key in ("image", "plate", "peek"):
            v = sc.get(key)
            if v and not (key == "plate" and v in PLATES) and film_dir and not (film_dir / v).exists():
                errs.append(f"scene {i} ({kind}): asset not found: {v}")
        d = sc.get("beats", 0) * beat
        rows.append((i, kind, t, d, sc.get("text") or sc.get("title") or sc.get("payoff") or ""))
        t += d
    kinds = [r[1] for r in rows]
    if kinds and kinds[0] != "cold":
        warn.append("formula: films open on a 'cold' scene")
    if "onemore" not in kinds:
        warn.append("formula: no 'onemore' reveal")
    if kinds and kinds[-1] != "end":
        warn.append("formula: films close on an 'end' card")
    if used_slots != sorted(used_slots):
        warn.append("slot indexes should step forward through 'chapters'")
    if not 30 <= t <= 130:
        warn.append(f"length {t:.1f}s is outside the usual 45-120 s")
    for r in rows:
        txt = r[4] if isinstance(r[4], str) else " / ".join(r[4])
        print(f"{r[0]:>2}  {r[2]:6.2f}s  {r[3]:5.2f}s  {r[1]:<8} {txt[:60]}")
    print(f"total {t:.1f}s, {len(rows)} scenes, {sb['bpm']} BPM")
    for w in warn:
        print("warning:", w)
    if errs:
        sys.exit("\n".join("error: " + e for e in errs))


if __name__ == "__main__":
    main()
