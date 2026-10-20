"""Generate the B-roll stills with the free Pollinations image API (flux model).

Usage: python3 fetch_images.py <out_dir>
Images are objects/places only (no people), so nothing shows incorrect exercise form.
The provider's watermark sits in the bottom-right corner and is cropped off at render time.
"""
import pathlib
import sys
import time
import urllib.parse
import urllib.request

STYLE = ("cinematic editorial photograph, soft natural light, muted warm tones, "
         "shallow depth of field, clean minimal composition, high detail, no people, no text")

PROMPTS = {
    "hook": "empty modern gym at sunrise, barbell resting on the floor in the foreground",
    "engine": "close-up of a powerful car engine glowing orange as it starts, dramatic light",
    "sleep": "cozy bedroom at night, neatly made bed, soft lamp light",
    "mitochondria": "macro scientific 3d render of glowing mitochondria inside a cell, warm red tones",
    "warmup": "stationary exercise bike next to a window in a bright modern gym",
    "goblet": "single hexagonal dumbbell standing on a rubber gym floor",
    "rdl": "pair of dumbbells on a rack in a minimalist gym",
    "bench": "adjustable weight bench in a clean bright gym",
    "row": "row of dumbbells neatly arranged on a rack, side view",
    "press": "upright weight bench with two dumbbells on the floor beside it",
    "stepup": "wooden plyometric box on a gym floor, soft window light",
    "carry": "two heavy dumbbells with chalk dust on a gym floor",
    "deadbug": "rolled-out exercise mat on a wooden floor, top-down view",
    "cardio": "treadmill set to an incline in a bright gym, window view",
    "plan": "open notebook with a weekly workout plan on a desk beside a water bottle",
    "protein": "healthy high-protein meal on a table: eggs, grilled chicken, lentils, paneer, greek yogurt",
    "steps": "running shoes on a city sidewalk in morning light",
    "outro": "gym window with sunrise light streaming in over training equipment",
}


def fetch(name, prompt, out_dir, seed):
    dest = out_dir / f"{name}.jpg"
    if dest.exists() and dest.stat().st_size > 20000:
        return True
    q = urllib.parse.quote(f"{prompt}, {STYLE}")
    url = (f"https://image.pollinations.ai/prompt/{q}"
           f"?width=1280&height=720&model=turbo&nologo=true&seed={seed}")
    for attempt in range(5):
        try:
            with urllib.request.urlopen(url, timeout=120) as r:
                data = r.read()
            if len(data) > 20000:
                dest.write_bytes(data)
                print("ok", name, len(data), flush=True)
                return True
        except Exception as e:  # network hiccups and 5xx from the free tier
            print("retry", name, attempt, e, flush=True)
        time.sleep(4 * (attempt + 1))
    print("FAILED", name, flush=True)
    return False


def main():
    out_dir = pathlib.Path(sys.argv[1])
    out_dir.mkdir(parents=True, exist_ok=True)
    for i, (name, prompt) in enumerate(PROMPTS.items()):
        fetch(name, prompt, out_dir, seed=100 + i)


if __name__ == "__main__":
    main()
