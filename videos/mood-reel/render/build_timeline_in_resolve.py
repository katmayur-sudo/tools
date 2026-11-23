"""Build the reel's timeline in DaVinci Resolve from timeline_resolve.json (this kit's folder).

Run inside Resolve (works in the free version): Workspace > Console > Py3, then
    exec(open(r"<kit folder>/build_timeline_in_resolve.py").read())
or copy this file into Resolve's Scripts/Utility folder and run it from Workspace > Scripts.
Resolve Studio can also run it from a terminal while Resolve is open (Preferences > System > General >
External scripting using: Local).

It creates project "<name>" (or reuses it), sets 1080x1920 @ 30 fps, imports the kit's media, places every clip
frame-exactly, sets the punch-in zoom and the face-circle position, adds a marker per shot, then checks every
placed clip's length and prints a report. Subtitles, overlay fade-ins and the -1 dB master are left to do by hand
(Resolve's API cannot set them); the report says how.
"""
import json, os, sys

try:
    KIT = os.path.dirname(os.path.abspath(__file__))
except NameError:  # exec() from the console has no __file__
    KIT = os.path.dirname(os.path.abspath(sys.argv[0])) if sys.argv and sys.argv[0] else os.getcwd()
if not os.path.exists(os.path.join(KIT, "timeline_resolve.json")):
    KIT = input("Path of the kit folder: ").strip().strip('"')
SPEC = json.load(open(os.path.join(KIT, "timeline_resolve.json")))
NAME = "Mood Reel"

def get_resolve():
    try:
        return resolve  # noqa: F821  (defined inside Resolve's console)
    except NameError:
        pass
    mods = {"darwin": "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules",
            "win32": os.path.join(os.environ.get("PROGRAMDATA", r"C:\ProgramData"),
                                  r"Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules"),
            "linux": "/opt/resolve/Developer/Scripting/Modules"}
    sys.path.append(mods.get(sys.platform, mods["linux"]))
    import DaVinciResolveScript as dvr
    return dvr.scriptapp("Resolve")

R = get_resolve()
assert R, "Resolve is not reachable: open DaVinci Resolve first (and enable external scripting for terminal use)."
pm = R.GetProjectManager()
proj = pm.CreateProject(NAME) or pm.LoadProject(NAME)
assert proj, f"Could not create or open project {NAME!r}"
T = SPEC["timeline"]
for k, v in [("timelineFrameRate", str(T["fps"])), ("timelineResolutionWidth", str(T["width"])),
             ("timelineResolutionHeight", str(T["height"]))]:
    if not proj.SetSetting(k, v):
        print(f"! could not set {k}={v} (set it in Project Settings if the project already had timelines)")

mp = proj.GetMediaPool()
files = sorted({SPEC["aroll"]["file"]} | {c["file"] for c in SPEC["clips"]} | {a["file"] for a in SPEC["audio"]})
items = mp.ImportMedia([os.path.join(KIT, f) for f in files]) or []
by_name = {it.GetClipProperty("File Name"): it for it in items}
missing = [f for f in files if os.path.basename(f) not in by_name]
assert not missing, f"Not imported: {missing}"
item = lambda f: by_name[os.path.basename(f)]

tl = mp.CreateEmptyTimeline(f"{NAME} {T['width']}x{T['height']}")
proj.SetCurrentTimeline(tl)
while tl.GetTrackCount("video") < 4: tl.AddTrack("video")
while tl.GetTrackCount("audio") < 3: tl.AddTrack("audio", "stereo")
T0 = tl.GetStartFrame()
report = []
EXCLUSIVE = None  # whether this Resolve treats endFrame as exclusive; measured on the first clip

def place(f, src_in, src_out, rec_in, track, media_type):
    global EXCLUSIVE
    n = src_out - src_in
    def add(end):
        return mp.AppendToTimeline([{"mediaPoolItem": item(f), "startFrame": src_in, "endFrame": end,
                                     "recordFrame": T0 + rec_in, "trackIndex": track, "mediaType": media_type}])
    if EXCLUSIVE is None:  # calibrate once
        got = add(src_out - 1)
        if got and got[0].GetDuration() == n - 1:
            tl.DeleteClips(got); EXCLUSIVE = True; got = add(src_out)
        else:
            EXCLUSIVE = False
    else:
        got = add(src_out if EXCLUSIVE else src_out - 1)
    if not got:
        report.append(f"FAILED to place {f} at frame {rec_in} on track {track}"); return None
    if got[0].GetDuration() != n:
        report.append(f"length {got[0].GetDuration()} != {n}: {f} at frame {rec_in}")
    return got[0]

# V1 + A1: A-roll pieces (video and its audio placed separately, same frames)
for p in SPEC["aroll"]["pieces"]:
    v = place(SPEC["aroll"]["file"], p["src_in"], p["src_out"], p["rec_in"], 1, 1)
    place(SPEC["aroll"]["file"], p["src_in"], p["src_out"], p["rec_in"], 1, 2)
    if v and p["zoom"] != 1.0:
        v.SetProperty("ZoomX", p["zoom"]); v.SetProperty("ZoomY", p["zoom"])

# V2-V4: card clips, face circles, overlays
for c in SPEC["clips"]:
    it = place(c["file"], c["src_in"], c["src_out"], c["rec_in"], int(c["track"][1:]), 1)
    if it and "Pan" in c:
        it.SetProperty("Pan", c["Pan"]); it.SetProperty("Tilt", c["Tilt"])

# A2, A3: music and SFX stems
for a in SPEC["audio"]:
    place(a["file"], 0, a["rec_out"] - a["rec_in"], a["rec_in"], int(a["track"][1:]), 2)

for m in SPEC["markers"]:
    tl.AddMarker(m["frame"], "Blue", m["name"], "", 1)

ok = tl.GetEndFrame() - T0
print(f"Timeline built: {ok} frames (expected {T['frames']}). endFrame exclusive: {EXCLUSIVE}")
print("\n".join(report) if report else "All clips placed at their exact lengths.")
print("By hand: 1) File > Import > Subtitle > 6_Captions/Captions_Hinglish.srt, drag to the timeline start.\n"
      "2) Optional: 9-frame fade-in on the V4 overlays.  3) Fairlight: master bus -1 dB (-14 LUFS).")
