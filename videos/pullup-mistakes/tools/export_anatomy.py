"""Export the Z-Anatomy figure (CC BY-SA 4.0) as a skinned, render-ready binary for render/short.html.

Usage (Blender as a Python module, `pip install bpy`):
  python3 -I export_anatomy.py <Z-Anatomy FBX dir> <classification.json> <out_dir> [--budget 600000]

Inputs: MuscularSystem100.fbx, SkeletalSystem100.fbx and "Regions of human body100.fbx" from
https://github.com/LluisV/Z-Anatomy (Resources/Models/FBX). classification.json maps each muscle
name (side-agnostic) to {material, superficial, group, segments} (built once with an anatomy review).

Writes <out_dir>/anatomy.bin + anatomy.json: one entry per (group, material) chunk with positions,
normals, indices and 4 skin weights per vertex, plus the joint landmarks of the rest skeleton.
Coordinates are converted to the renderer's world: metres, +y up, +z = the figure's front, +x = its left.
Skin weights: distance to the bone segments a structure is attached to (from the classification),
1/d^4 falloff, then Laplacian-smoothed over the mesh so joints bend smoothly.
"""
import json
import math
import re
import sys
from collections import defaultdict

import bpy
import numpy as np

FBX_DIR, CLS, OUT = sys.argv[1:4]
BUDGET = int(sys.argv[sys.argv.index("--budget") + 1]) if "--budget" in sys.argv else 600000

BONES = ["root", "spine", "chest", "neck", "head",
         "clav_l", "upperarm_l", "forearm_l", "hand_l", "clav_r", "upperarm_r", "forearm_r", "hand_r",
         "fing_l", "tip_l", "fing_r", "tip_r",
         "thigh_l", "shin_l", "foot_l", "thigh_r", "shin_r", "foot_r"]
PARENT = {"root": None, "spine": "root", "chest": "spine", "neck": "chest", "head": "neck",
          "clav_l": "chest", "upperarm_l": "clav_l", "forearm_l": "upperarm_l", "hand_l": "forearm_l",
          "clav_r": "chest", "upperarm_r": "clav_r", "forearm_r": "upperarm_r", "hand_r": "forearm_r",
          "fing_l": "hand_l", "tip_l": "fing_l", "fing_r": "hand_r", "tip_r": "fing_r",
          "thigh_l": "root", "shin_l": "thigh_l", "foot_l": "shin_l", "thigh_r": "root", "shin_r": "thigh_r", "foot_r": "shin_r"}
SEG2BONE = {"head": "head", "neck": "neck", "chest": "chest", "abdomen": "spine", "pelvis": "root", "scapula": "clav",
            "upperarm": "upperarm", "forearm": "forearm", "hand": "hand", "finger": "fing", "tip": "tip", "thigh": "thigh", "shin": "shin", "foot": "foot"}


def to_world(v):  # Z-Anatomy (x left, y back, z up) -> (x left, y up, z front)
    return np.stack([v[:, 0], v[:, 2], -v[:, 1]], axis=1)


def load_all():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for f in ["MuscularSystem100.fbx", "SkeletalSystem100.fbx", "Regions of human body100.fbx"]:
        before = set(bpy.data.objects)
        bpy.ops.import_scene.fbx(filepath=f"{FBX_DIR}/{f}")
        for o in set(bpy.data.objects) - before:
            o["src"] = f.split(".")[0]


def mesh_arrays(o, ratio):
    """Decimate a copy, triangulate, return world-space verts, normals, faces."""
    me = o.data
    if ratio < .98 and len(me.polygons) > 60:
        mod = o.modifiers.new("dec", "DECIMATE")
        mod.ratio = max(ratio, 60 / max(1, len(me.polygons)))
        mod.use_collapse_triangulate = True
    tri = o.modifiers.new("tri", "TRIANGULATE")
    dg = bpy.context.evaluated_depsgraph_get()
    ev = o.evaluated_get(dg)
    m = ev.to_mesh()
    m.transform(o.matrix_world)
    n = len(m.vertices)
    v = np.empty(n * 3, np.float32); m.vertices.foreach_get("co", v)
    m.calc_loop_triangles() if hasattr(m, "calc_loop_triangles") else None
    f = np.empty(len(m.loop_triangles) * 3, np.int32); m.loop_triangles.foreach_get("vertices", f)
    nr = np.empty(n * 3, np.float32)
    m.vertices.foreach_get("normal", nr)
    ev.to_mesh_clear()
    o.modifiers.clear()
    return to_world(v.reshape(-1, 3)), to_world(nr.reshape(-1, 3)), f.reshape(-1, 3)


def raw_verts(o):
    v = np.array([o.matrix_world @ p.co for p in o.data.vertices], np.float32)
    return to_world(v)


def side_of(name):
    s = name.rsplit(".", 1)[-1] if "." in name else ""
    return "l" if s.endswith("l") else "r" if s.endswith("r") else "m"


def landmarks():
    ob = {o.name: o for o in bpy.data.objects if o.type == "MESH" and o.get("src") == "SkeletalSystem100"}
    V = lambda n: raw_verts(ob[n])
    J = {}
    for s, sx in (("l", 1), ("r", -1)):
        hum = V(f"Humerus.{s}")
        top = hum[hum[:, 1] > hum[:, 1].max() - .045]
        J[f"shoulder_{s}"] = top[np.argsort(np.abs(top[:, 0]))[:max(8, len(top) // 2)]].mean(0)  # medial half = humeral head
        J[f"elbow_{s}"] = hum[hum[:, 1] < hum[:, 1].min() + .025].mean(0)
        car = np.vstack([V(f"{b} bone.{s}") for b in ("Lunate", "Capitate", "Scaphoid")])
        J[f"wrist_{s}"] = car.mean(0)
        J[f"knuckle_{s}"] = V(f"Third metacarpal bone.{s}")[V(f"Third metacarpal bone.{s}")[:, 1].argmin()]
        pp = V(f"Proximal phalanx of third finger of hand.{s}"); dp = V(f"Distal phalanx of third finger of hand.{s}")
        J[f"pip_{s}"] = pp[pp[:, 1].argmin()]; J[f"fingertip_{s}"] = dp[dp[:, 1].argmin()]
        fem = V(f"Femur.{s}")
        top = fem[fem[:, 1] > fem[:, 1].max() - .05]
        J[f"hip_{s}"] = top[np.argsort(np.abs(top[:, 0]))[:max(8, len(top) // 3)]].mean(0)
        tib = V(f"Tibia.{s}")
        J[f"knee_{s}"] = (fem[fem[:, 1] < fem[:, 1].min() + .03].mean(0) + tib[tib[:, 1] > tib[:, 1].max() - .02].mean(0)) / 2
        J[f"ankle_{s}"] = V(f"Talus.{s}").mean(0)
        J[f"toe_{s}"] = V(f"Second metatarsal bone.{s}")[V(f"Second metatarsal bone.{s}")[:, 2].argmax()]
        cl = V(f"Clavicle.{s}")
        J[f"sternoclav_{s}"] = cl[np.argsort(np.abs(cl[:, 0]))[:20]].mean(0)
    body = lambda n: V(n).mean(0)
    J["L5"] = body("Vertebra L5"); J["L1"] = body("Vertebra L1"); J["T7"] = body("Vertebra T7")
    J["C7"] = body("Vertebra C7"); J["C1"] = body("Atlas (C1)")
    sk = np.vstack([V(n) for n in ("Occipital bone", "Frontal bone", "Parietal bone.l", "Parietal bone.r")])
    J["headtop"] = np.array([0, sk[:, 1].max(), sk[:, 2].mean()], np.float32)
    J["pelvis"] = (J["hip_l"] + J["hip_r"]) / 2
    return {k: np.asarray(v, np.float32) for k, v in J.items()}


def skeleton(J):
    """Bone head positions (rest) and the segment each bone covers for weighting."""
    H = {"root": J["pelvis"] * [0, 1, 1] + [0, 0, 0], "spine": J["L1"], "chest": J["T7"], "neck": J["C7"], "head": J["C1"]}
    seg = {"root": (J["pelvis"], J["L1"]), "spine": (J["L1"], J["T7"]), "chest": (J["T7"], J["C7"]),
           "neck": (J["C7"], J["C1"]), "head": (J["C1"], J["headtop"])}
    for s in "lr":
        H[f"clav_{s}"] = J[f"sternoclav_{s}"]; seg[f"clav_{s}"] = (J[f"sternoclav_{s}"], J[f"shoulder_{s}"])
        H[f"upperarm_{s}"] = J[f"shoulder_{s}"]; seg[f"upperarm_{s}"] = (J[f"shoulder_{s}"], J[f"elbow_{s}"])
        H[f"forearm_{s}"] = J[f"elbow_{s}"]; seg[f"forearm_{s}"] = (J[f"elbow_{s}"], J[f"wrist_{s}"])
        H[f"hand_{s}"] = J[f"wrist_{s}"]; seg[f"hand_{s}"] = (J[f"wrist_{s}"], J[f"knuckle_{s}"])
        H[f"fing_{s}"] = J[f"knuckle_{s}"]; seg[f"fing_{s}"] = (J[f"knuckle_{s}"], J[f"pip_{s}"])
        H[f"tip_{s}"] = J[f"pip_{s}"]; seg[f"tip_{s}"] = (J[f"pip_{s}"], J[f"fingertip_{s}"])
        H[f"thigh_{s}"] = J[f"hip_{s}"]; seg[f"thigh_{s}"] = (J[f"hip_{s}"], J[f"knee_{s}"])
        H[f"shin_{s}"] = J[f"knee_{s}"]; seg[f"shin_{s}"] = (J[f"knee_{s}"], J[f"ankle_{s}"])
        H[f"foot_{s}"] = J[f"ankle_{s}"]; seg[f"foot_{s}"] = (J[f"ankle_{s}"], J[f"toe_{s}"])
    return H, seg


def seg_dist(P, a, b):
    ab = b - a
    t = np.clip(((P - a) @ ab) / max(1e-9, ab @ ab), 0, 1)
    return np.linalg.norm(P - (a + t[:, None] * ab), axis=1)


def weights(P, F, cands, seg, smooth=12, power=4, sheet=False):
    """4 bone influences per vertex from distance to candidate segments, smoothed over the mesh.

    sheet=True is for torso muscles that insert on the humerus (lats, pecs, traps, scapular muscles): in
    the rest pose the arm hangs beside the torso, so plain distance would tie the whole sheet to the arm.
    Instead the arm only owns the vertices near the humeral insertion (proximal quarter of the humerus)."""
    names = sorted(set(cands))
    arm = [b for b in names if b.startswith("upperarm")] if sheet else []
    rest = [b for b in names if b not in arm] or ["chest"]
    D = np.stack([seg_dist(P, *seg[b]) for b in rest], 1)
    W = 1 / np.maximum(D, .008) ** power
    W /= W.sum(1, keepdims=True)
    if arm:
        A = np.stack([np.exp(-(seg_dist(P, seg[b][0], seg[b][0] + .25 * (seg[b][1] - seg[b][0])) / .045) ** 2) for b in arm], 1)
        a = np.clip(A.sum(1, keepdims=True), 0, 1)
        W = np.hstack([W * (1 - a), A / np.maximum(A.sum(1, keepdims=True), 1e-9) * a])
        names = rest + arm
    else:
        names = rest
    if len(names) > 1 and len(F):
        import scipy.sparse as sp
        n = len(P)
        e = np.concatenate([F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]])
        A = sp.coo_matrix((np.ones(len(e) * 2), (np.r_[e[:, 0], e[:, 1]], np.r_[e[:, 1], e[:, 0]])), shape=(n, n)).tocsr()
        A.data[:] = 1
        deg = np.asarray(A.sum(1)).ravel(); deg[deg == 0] = 1
        for _ in range(smooth):
            W = .5 * W + .5 * (A @ W) / deg[:, None]
    if W.shape[1] < 4:  # pad to 4 influences (zero weight on the root)
        W = np.hstack([W, np.zeros((len(W), 4 - W.shape[1]))])
        names = names + ["root"] * (4 - len(names))
    order = np.argsort(-W, 1)[:, :4]
    w4 = np.take_along_axis(W, order, 1)
    w4 /= np.maximum(w4.sum(1, keepdims=True), 1e-9)
    idx = np.array([BONES.index(b) for b in names])[order]
    return idx.astype(np.uint16), w4.astype(np.float32)


def bone_cands(segments, side, seg_keys):
    out = []
    for sg in segments:
        b = SEG2BONE[sg]
        if b in ("clav", "upperarm", "forearm", "hand", "fing", "tip", "thigh", "shin", "foot"):
            out += [f"{b}_{side}"] if side in "lr" else [f"{b}_l", f"{b}_r"]
        else:
            out.append(b)
    return [b for b in dict.fromkeys(out) if b in seg_keys] or ["chest"]


SKIN_HEAD_MIN_Z, FOOT_MAX_Z = 1.48, .13
HAND_WORDS = ("Palm", "Dorsum of hand", "digits of hand", "Perionyx.", "Nail plate.", "region of wrist", "Radial foveola")
FOOT_WORDS = ("foot", "Heel", "Sole", "malleol", "retromalleolar", "Hallucial", "Metatarsal region", "Anterior region of ankle")
BONE_KEEP = re.compile(r"^(Clavicle|Scapula|Humerus|Ulna|Radius|Hip bone|Femur|Patella|Tibia|Fibula|Sacrum|Coccyx|Vertebra [CTL]\d+|Atlas \(C1\)|Axis \(C2\)|"
                       r"(First|Second|Third|Fourth|Fifth|Sixth|Seventh|Eighth|Ninth|Tenth|Eleventh|Twelfth) rib|Costal cartilage of .* rib|Manubrium of sternum|Body of sternum|Xiphoid process)(\.[lr])?$")
BONE_SEG = [("Clavicle", ["scapula"]), ("Scapula", ["scapula"]), ("Humerus", ["upperarm"]), ("Ulna", ["forearm"]), ("Radius", ["forearm"]),
            ("Hip bone", ["pelvis"]), ("Sacrum", ["pelvis"]), ("Coccyx", ["pelvis"]), ("Femur", ["thigh"]), ("Patella", ["thigh", "shin"]),
            ("Tibia", ["shin"]), ("Fibula", ["shin"]), ("Vertebra C", ["neck"]), ("Atlas", ["neck", "head"]), ("Axis", ["neck"]),
            ("Vertebra T", ["chest", "abdomen"]), ("Vertebra L", ["abdomen", "pelvis"]), ("rib", ["chest", "abdomen"]), ("stern", ["chest"]), ("Xiphoid", ["chest"])]


def main():
    cls = {c["name"]: c for c in json.load(open(CLS))}
    load_all()
    J = landmarks()
    H, seg = skeleton(J)
    picks = []  # (object, chunk key, segments)
    for o in bpy.data.objects:
        if o.type != "MESH" or len(o.data.vertices) < 12:
            continue
        src, name = o.get("src"), o.name
        base = re.sub(r"\.(l|r|j|\d+)$", "", name)
        if src == "MuscularSystem100":
            c = cls.get(base)
            if not c or c["material"] == "exclude" or not c["superficial"]:
                continue
            picks.append((o, (c["group"], c["material"]), c["segments"]))
        elif src == "SkeletalSystem100" and BONE_KEEP.match(name):
            segs = next((s for k, s in BONE_SEG if k in name), ["chest"])
            picks.append((o, ("bone", "bone"), segs))
        elif src == "Regions of human body100":
            zs = raw_verts(o)[:, 1]
            zmin, zmax = min(zs), max(zs)
            if name.startswith(("Hairs of head", "Hairs of eyebrow", "Eyelashes")):
                picks.append((o, ("hair", "hair"), ["head"]))
            elif zmin >= SKIN_HEAD_MIN_Z and "Hairs" not in name:
                picks.append((o, ("skin", "skin"), ["head"]))
            elif any(w in name for w in HAND_WORDS):  # fingers get their own two joints so they can wrap the bar
                picks.append((o, ("skin", "skin"), ["forearm", "hand", "finger", "tip"]))
            elif zmax <= FOOT_MAX_Z and any(w in name for w in FOOT_WORDS):
                picks.append((o, ("skin", "skin"), ["shin", "foot"]))
    total = sum(len(o.data.polygons) for o, _, _ in picks)
    ratio = min(1, BUDGET / max(1, total))
    print(f"picked {len(picks)} objects, {total} polys -> ratio {ratio:.3f}", flush=True)
    chunks = defaultdict(lambda: {"P": [], "N": [], "F": [], "I": [], "W": [], "n": 0})
    for o, key, segs in picks:
        boost = 99 if key[0] == "skin" else 1.8 if key[0] in ("lats", "traps", "delts", "back") else 1.0
        P, N, F = mesh_arrays(o, min(1, ratio * boost))
        if key[0] == "forearms":  # tendons running on into the hand sit under the hand skin: trim them at the wrist
            wy = min(J["wrist_l"][1], J["wrist_r"][1]) - .004
            F = F[(P[F][:, :, 1] > wy).all(1)]
        if not len(F):
            continue
        side = side_of(o.name)
        if side == "m" and key[0] not in ("hair", "skin", "bone"):
            side = "m"
        if key[0] in ("lats", "back"):  # muscles over the shoulder blade also ride the scapula
            segs = list(dict.fromkeys(["scapula"] + list(segs)))[:4]
        cands = bone_cands(segs, side, seg)
        # sheet muscles that span the shoulder: sharp falloff, little diffusion, so they stretch instead of flaring
        sharp = key[0] in ("lats", "back", "chest", "traps")
        I, W = weights(P, F, cands, seg, smooth=3 if sharp else 10, power=4, sheet=sharp)
        c = chunks[key]
        c["P"].append(P); c["N"].append(N); c["F"].append(F + c["n"]); c["I"].append(I); c["W"].append(W); c["n"] += len(P)
    blob, meta = bytearray(), {"bones": BONES, "parent": PARENT, "rest": {b: H[b].round(5).tolist() for b in BONES},
                               "joints": {k: v.round(5).tolist() for k, v in J.items()}, "chunks": []}

    def put(arr):
        off = len(blob); blob.extend(np.ascontiguousarray(arr).tobytes())
        while len(blob) % 4: blob.append(0)
        return off
    for (group, mat), c in sorted(chunks.items()):
        P = np.vstack(c["P"]).astype(np.float32); N = np.vstack(c["N"]).astype(np.float32)
        F = np.vstack(c["F"]).astype(np.uint32); I = np.vstack(c["I"]).astype(np.uint16); W = np.vstack(c["W"]).astype(np.float32)
        meta["chunks"].append({"group": group, "material": mat, "verts": len(P), "tris": len(F),
                               "position": put(P), "normal": put(N), "index": put(F), "skinIndex": put(I), "skinWeight": put(W)})
        print(f"{group:10s} {mat:7s} v{len(P):7d} t{len(F):7d}", flush=True)
    open(f"{OUT}/anatomy.bin", "wb").write(blob)
    json.dump(meta, open(f"{OUT}/anatomy.json", "w"))
    print(f"wrote {len(blob) / 1e6:.1f} MB, {sum(c['tris'] for c in meta['chunks'])} tris")


if __name__ == "__main__":
    main()
