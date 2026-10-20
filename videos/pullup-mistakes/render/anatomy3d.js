// Real-anatomy 3D athlete shared by short.html and the launch film (videos/pullup-launch).
// Expects these globals from the page: T (time), G (theme with name/acc), ASSET (asset base URL),
// lerp(), easeOut(). Exposes loadAnatomy(), build3D(), pose(st), proj(v), R3.
// ================= 3D athlete: real human anatomy (Z-Anatomy, CC BY-SA 4.0) =================
// anatomy.bin/.json come from tools/export_anatomy.py: every superficial muscle, tendon and bone of the
// Z-Anatomy figure plus skin for the head, hands and feet, skinned to a 19-bone skeleton. World units
// are metres; the athlete faces +z (the wall) and the camera sits behind, so we see the back.
const V3 = (x, y, z) => new THREE.Vector3(x, y, z), UP = V3(0, 1, 0);
const BAR_Y = 2.3, GRIP = .44;
const HOT_GROUPS = ["traps", "lats", "back", "delts", "arms", "forearms", "core", "chest", "neck", "glutes", "legs"];
let R3 = null, ANAT = null;
function loadBin(url) {
  return new Promise((res, rej) => { const x = new XMLHttpRequest(); x.open("GET", url); x.responseType = "arraybuffer";
    x.onload = () => res(x.response); x.onerror = rej; x.send(); });
}
async function loadAnatomy() {
  const [meta, bin] = await Promise.all([loadBin(ASSET + "anatomy.json").then(b => JSON.parse(new TextDecoder().decode(b))), loadBin(ASSET + "anatomy.bin")]);
  ANAT = { meta, bin };
}
// muscle shader: bulge along the normal when active, plus light pulsing along the body ("fibres firing")
function muscleMat(base, opts) {
  const m = new THREE.MeshPhysicalMaterial(opts);
  m.userData.u = { uAct: { value: 0 }, uTime: { value: 0 }, uHot: { value: new THREE.Color(0xff5a1f) } };
  m.onBeforeCompile = sh => {
    Object.assign(sh.uniforms, m.userData.u);
    sh.vertexShader = "uniform float uAct;\nvarying vec3 vRest;\n" + sh.vertexShader
      .replace("#include <begin_vertex>", "#include <begin_vertex>\n vRest = position;\n transformed += objectNormal * uAct * 0.0025;");
    sh.fragmentShader = "uniform float uAct; uniform float uTime; uniform vec3 uHot;\nvarying vec3 vRest;\n" + sh.fragmentShader
      .replace("#include <emissivemap_fragment>", `#include <emissivemap_fragment>
 float wave = 0.55 + 0.45 * sin(vRest.y * 70.0 - uTime * 7.0 + vRest.x * 20.0);
 float rim = pow(1.0 - abs(dot(normalize(vViewPosition), normal)), 1.5);
 totalEmissiveRadiance += uHot * uAct * (0.28 + 0.16 * wave + 0.55 * rim);
 diffuseColor.rgb = mix(diffuseColor.rgb, diffuseColor.rgb * 1.25 + uHot * 0.15, uAct * 0.6);`);
  };
  m.customProgramCacheKey = () => "muscle";
  return m;
}
function build3D() {
  const R = G.name === "redblack", M = ANAT.meta, buf = ANAT.bin;
  const renderer = new THREE.WebGLRenderer({ canvas: document.getElementById("gl"), alpha: true, antialias: true, preserveDrawingBuffer: true });
  renderer.setPixelRatio(1); renderer.setSize(1080, 1920, false);
  renderer.outputColorSpace = THREE.SRGBColorSpace; renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = R ? 1.2 : 1.05;
  renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap; renderer.setClearColor(0x000000, 0);
  const scene = new THREE.Scene(), cam = new THREE.PerspectiveCamera(28, 1080 / 1920, .1, 60);
  // lights: a soft key from behind-left (camera side), cool fill, and rims from the wall side
  if (R) {
    scene.add(new THREE.HemisphereLight(0x4a1a1e, 0x050505, 1.0));
    const key = new THREE.DirectionalLight(0xfff0ea, 3.0); key.position.set(-2.5, 4, -5); key.castShadow = true; scene.add(key, key.target); shadowSetup(key);
    const fill = new THREE.DirectionalLight(0x9fb0ff, .55); fill.position.set(3, 1.5, -4); scene.add(fill);
    for (const [x, i] of [[-2.2, 70], [2.2, 70], [0, 30]]) { const l = new THREE.SpotLight(0xff2030, i, 12, .7, .6, 1.6); l.position.set(x, 3.3, 1.8); l.target.position.set(0, 1.7, 0); scene.add(l, l.target); }
  } else {
    scene.add(new THREE.HemisphereLight(0xffffff, 0xd8cdbd, 1.15));
    const key = new THREE.DirectionalLight(0xfff3e6, 2.6); key.position.set(-3, 5, -5); key.castShadow = true; scene.add(key, key.target); shadowSetup(key);
    const rim = new THREE.DirectionalLight(0xffffff, 1.6); rim.position.set(3, 3, 3); scene.add(rim);
    const side = new THREE.DirectionalLight(0xfff0e0, .8); side.position.set(4, 1, -2); scene.add(side);
  }
  function shadowSetup(l) { l.target.position.set(0, 1.6, 0); l.shadow.mapSize.set(2048, 2048); const c = l.shadow.camera; c.left = -1.6; c.right = 1.6; c.top = 1.8; c.bottom = -1.8; c.near = .5; c.far = 15; l.shadow.radius = 5; l.shadow.bias = -.0005; l.shadow.normalBias = .01; }
  const wall = new THREE.Mesh(new THREE.PlaneGeometry(12, 12), new THREE.ShadowMaterial({ opacity: R ? .55 : .16 }));
  wall.position.set(0, 2, .6); wall.rotation.y = Math.PI; wall.receiveShadow = true; scene.add(wall);
  const metal = new THREE.MeshStandardMaterial({ color: R ? 0xbdbdbd : 0xcfcfcf, metalness: .9, roughness: .22 });
  const frameM = new THREE.MeshStandardMaterial({ color: R ? 0x151012 : 0xd9d2c5, roughness: .6, metalness: .2 });
  const bar = new THREE.Mesh(new THREE.CylinderGeometry(.017, .017, 1.7, 40), metal); bar.rotation.z = Math.PI / 2; bar.position.set(0, BAR_Y, 0); bar.castShadow = true; scene.add(bar);
  for (const x of [-.85, .85]) { const p = new THREE.Mesh(new THREE.BoxGeometry(.06, 3.2, .06), frameM); p.position.set(x, BAR_Y - 1.4, .12); p.castShadow = true; scene.add(p);
    const a = new THREE.Mesh(new THREE.BoxGeometry(.05, .05, .2), frameM); a.position.set(x, BAR_Y, .06); scene.add(a); }
  // skeleton (rest = anatomical position, identity rotations)
  const bones = {};
  for (const n of M.bones) { const b = new THREE.Bone(); b.name = n; bones[n] = b; }
  for (const n of M.bones) {
    const p = M.parent[n], r = V3(...M.rest[n]);
    if (p) { bones[p].add(bones[n]); bones[n].position.copy(r.sub(V3(...M.rest[p]))); } else { bones[n].position.copy(r); scene.add(bones[n]); }
  }
  bones.root.updateMatrixWorld(true);
  const skel = new THREE.Skeleton(M.bones.map(n => bones[n]));
  // materials
  const muscleBase = R ? 0x8a2326 : 0xa8322f;
  const mats = {};
  for (const g of HOT_GROUPS) mats[g] = muscleMat(muscleBase, { color: muscleBase, roughness: .42, metalness: 0, sheen: .8, sheenColor: new THREE.Color(R ? 0xff7070 : 0xffa0a0), sheenRoughness: .4, clearcoat: .3, clearcoatRoughness: .35 });
  const tendon = new THREE.MeshPhysicalMaterial({ color: R ? 0xcfc6ba : 0xece6dc, roughness: .28, clearcoat: .5, sheen: .4, sheenColor: new THREE.Color(0xffffff) });
  const boneM = new THREE.MeshStandardMaterial({ color: R ? 0xcdbfa6 : 0xe6dac2, roughness: .6 });
  const skinM = new THREE.MeshPhysicalMaterial({ color: R ? 0xa86d52 : 0xc68b66, roughness: .55, sheen: .5, sheenColor: new THREE.Color(0xffc8b0) });
  const hairM = new THREE.MeshStandardMaterial({ color: 0x120d0a, roughness: .85, side: THREE.DoubleSide });
  for (const c of M.chunks) {
    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.BufferAttribute(new Float32Array(buf, c.position, c.verts * 3), 3));
    g.setAttribute("normal", new THREE.BufferAttribute(new Float32Array(buf, c.normal, c.verts * 3), 3));
    g.setAttribute("skinIndex", new THREE.BufferAttribute(new Uint16Array(buf, c.skinIndex, c.verts * 4), 4));
    g.setAttribute("skinWeight", new THREE.BufferAttribute(new Float32Array(buf, c.skinWeight, c.verts * 4), 4));
    g.setIndex(new THREE.BufferAttribute(new Uint32Array(buf, c.index, c.tris * 3), 1));
    const mat = c.material === "muscle" ? (mats[c.group] ?? mats.core) : c.material === "tendon" ? tendon : c.material === "bone" ? boneM : c.material === "hair" ? hairM : skinM;
    const m = new THREE.SkinnedMesh(g, mat); m.bind(skel, new THREE.Matrix4()); m.castShadow = true; m.frustumCulled = false; scene.add(m);
  }
  const rest = n => V3(...M.rest[n]);
  const len = (a, b) => rest(a).distanceTo(rest(b));
  const L = { ua: len("upperarm_l", "forearm_l"), fa: len("forearm_l", "hand_l") };
  R3 = { renderer, scene, cam, mats, bones, rest, L, joints: {} };
  pose({});
}
// 2-bone IK in 3D: elbow bends toward `pole`
function ik(S, H, a, b, pole) {
  const d = H.clone().sub(S), Ln = Math.min(d.length(), a + b - 1e-4), dir = d.clone().normalize();
  const x = (a * a - b * b + Ln * Ln) / (2 * Ln), h = Math.sqrt(Math.max(0, a * a - x * x));
  const n = pole.clone().sub(dir.clone().multiplyScalar(pole.dot(dir))).normalize();
  return S.clone().addScaledVector(dir, x).addScaledVector(n, h);
}
const _q = new THREE.Quaternion(), _q2 = new THREE.Quaternion();
const worldQ = b => b.getWorldQuaternion(new THREE.Quaternion());
const worldP = b => b.getWorldPosition(V3());
function setWorldQ(b, q) { b.quaternion.copy(worldQ(b.parent).invert().multiply(q)); b.updateMatrixWorld(true); }
// st: p (0 dead hang .. 1 chin over bar), shrug, lean (rad, + = legs forward), legSwing, knee,
//     glow: {group: [colour, amount]} (amount drives contraction + glow), cam: {az, el, dist, look, fov, shake}
function pose(st) {
  const P = R3, B = P.bones, p = st.p ?? 0, shrug = st.shrug ?? 0, lean = st.lean ?? -.1 * p;
  for (const b of Object.values(B)) b.quaternion.identity();
  B.root.position.copy(P.rest("root")); B.root.rotation.set(lean, 0, 0);
  B.chest.rotation.set(-.12 * p - .04, 0, 0); B.spine.rotation.set(-.05 * p, 0, 0);
  B.head.rotation.set(-.15 + .1 * p, 0, 0);
  // shoulder girdle: arms overhead rotate the scapulae upward; shrugging elevates them, "blades down" depresses them
  const up = .55 + .3 * shrug - .12 * (st.depress ?? 0);
  B.clav_l.rotation.set(0, 0, up); B.clav_r.rotation.set(0, 0, -up);
  B.root.updateMatrixWorld(true);
  // place the body so the shoulders sit at the height of this rep phase
  const HL = P.rest("fing_l").distanceTo(P.rest("hand_l")), SL = worldP(B.upperarm_l), Hy = BAR_Y - HL * .97, reach = (P.L.ua + P.L.fa) * .985, dx = GRIP - Math.abs(SL.x);
  const yHang = Hy - Math.sqrt(Math.max(.01, reach * reach - dx * dx - .0016)), yTop = BAR_Y - .17;
  const ys = lerp(yHang, yTop, p);
  B.root.position.y += ys - SL.y; B.root.position.z += (-.03 - .07 * p) - SL.z;
  B.root.updateMatrixWorld(true);
  const J = {};
  for (const [s, sx] of [["l", 1], ["r", -1]]) {
    const ua = B["upperarm_" + s], fa = B["forearm_" + s], hd = B["hand_" + s];
    // overhand grip: the knuckle line sits on the bar, the palm presses its back, the wrist stays straight
    const S = worldP(ua), K = V3(sx * GRIP, BAR_Y + .004, -.03), pole = V3(sx, -.35, -.55);
    let u = K.clone().sub(S).normalize(), H = K.clone().addScaledVector(u, -HL), E = ik(S, H, P.L.ua, P.L.fa, pole);
    for (let it = 0; it < 3; it++) { u = H.clone().sub(E).normalize(); H = K.clone().addScaledVector(u, -HL); E = ik(S, H, P.L.ua, P.L.fa, pole); }
    const dU0 = P.rest("forearm_" + s).sub(P.rest("upperarm_" + s)).normalize(), dF0 = P.rest("hand_" + s).sub(P.rest("forearm_" + s)).normalize();
    const qU = _q.setFromUnitVectors(dU0, E.clone().sub(S).normalize()).clone();
    setWorldQ(ua, qU);
    const dF = dF0.clone().applyQuaternion(qU), qF = _q2.setFromUnitVectors(dF, H.clone().sub(E).normalize()).clone().multiply(qU);
    setWorldQ(fa, qF);
    // hand in line with the forearm; fingers wrap over the top of the bar toward the wall (MCP ~80 deg, PIP ~85 deg)
    const dH = P.rest("fing_" + s).sub(P.rest("hand_" + s)).normalize().applyQuaternion(qF);
    const qH = new THREE.Quaternion().setFromUnitVectors(dH, K.clone().sub(H).normalize()).multiply(qF);
    setWorldQ(hd, qH);
    const ax = K.clone().sub(H).normalize().cross(V3(0, 0, 1)).normalize();
    setWorldQ(B["fing_" + s], new THREE.Quaternion().setFromAxisAngle(ax, 1.4).multiply(qH));
    setWorldQ(B["tip_" + s], new THREE.Quaternion().setFromAxisAngle(ax, 2.85).multiply(qH));
    J["sh" + s.toUpperCase()] = S; J["el" + s.toUpperCase()] = worldP(fa);
  }
  // legs: hip flexion swings them, knees bend so the feet trail behind
  const sw = st.legSwing ?? 0, kb = st.knee ?? .55;
  for (const s of ["l", "r"]) { B["thigh_" + s].rotation.set(-(sw + .12), 0, 0); B["shin_" + s].rotation.set(kb, 0, 0); B["foot_" + s].rotation.set(.45, 0, 0); }
  B.root.updateMatrixWorld(true);
  // activation per muscle group (0..1): synergists follow the prime mover; the grip always works a little
  const act = {}; for (const g of HOT_GROUPS) act[g] = st.glow?.[g]?.[1] ?? 0;
  act.back = Math.max(act.back, act.lats * .75); act.delts = Math.max(act.delts, .5 * Math.max(act.lats, act.arms, act.traps));
  act.forearms = Math.max(act.forearms, .25 + .35 * act.arms); act.core = Math.max(act.core, .2 * act.lats);
  for (const g of HOT_GROUPS) {
    const u = P.mats[g].userData.u, bad = st.glow?.[g]?.[0] === G.acc || (g === "delts" && (st.glow?.traps || st.glow?.arms)) || (g === "forearms" && st.glow?.arms);
    u.uAct.value = act[g] * (.88 + .12 * Math.sin(T * 9)); u.uTime.value = T; u.uHot.value.setHex(bad ? 0xff1a14 : (G.name === "redblack" ? 0xff7a1a : 0xff5512));
  }
  // screen anchors for the motion graphics
  const C = B.chest, Sp = B.spine, rel = (b, n, off) => b.localToWorld(off.clone().sub(P.rest(n)));
  P.joints = { ...J, head: rel(B.head, "head", P.rest("head").add(V3(0, .1, 0))), waist: rel(Sp, "spine", V3(0, 1.02, -.1)),
    latL: rel(C, "chest", V3(.12, 1.17, -.11)), latR: rel(C, "chest", V3(-.12, 1.17, -.11)),
    latLb: rel(Sp, "spine", V3(.09, 1.04, -.1)), latRb: rel(Sp, "spine", V3(-.09, 1.04, -.1)),
    trap: rel(C, "chest", V3(0, 1.42, -.1)), foot: worldP(B.foot_l) };
  // camera: orbit around the athlete from behind
  const c = st.cam ?? {}, az = c.az ?? .32, el = c.el ?? .06, dist = c.dist ?? 6.6, look = c.look ?? V3(0, 1.63, 0);
  P.cam.fov = c.fov ?? 28; P.cam.updateProjectionMatrix();
  const shk = c.shake ?? 0;
  P.cam.position.set(look.x + Math.sin(az) * dist * Math.cos(el) + Math.sin(T * 91) * shk, look.y + Math.sin(el) * dist + Math.cos(T * 77) * shk, look.z - Math.cos(az) * dist * Math.cos(el));
  P.cam.lookAt(look);
  P.cam.updateMatrixWorld(true);
}
// world -> screen px
function proj(v) { if (!v) return [-999, -999]; const q = v.clone().project(R3.cam); return [(q.x + 1) / 2 * 1080, (1 - q.y) / 2 * 1920]; }
