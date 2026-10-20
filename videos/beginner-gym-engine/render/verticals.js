// Native 9:16 shorts. Loaded after index.html's main script and reuses its helpers
// (appear, spring, leaks, ribbon, figureSVG, mg* illustrations, img, ...).
// Each short is a list of beats; a beat starts on a spoken cue and runs until the next one.
(() => {
  let V = null;                       // current short: {id, cues, dur, end, captions, hook, photo, handle, platform}
  const at = k => V.cues[k];
  const W = 1080;

  const css = `
    .vbg{position:absolute;inset:0;background:#0E0E10}
    .vt{font-family:"Inter Display","Inter";font-weight:900;letter-spacing:-0.035em;color:#fff;line-height:1}
    .vred{color:#E0262B}
    .vbox{display:inline-block;background:#E0262B;color:#fff;border-radius:22px;padding:4px 28px;box-shadow:0 0 60px rgba(224,38,43,.55)}
    .vcard{position:absolute;background:#fff;border-radius:40px;box-shadow:0 40px 80px -30px rgba(0,0,0,.6)}
    .vdark{position:absolute;background:#18181B;border-radius:40px;box-shadow:0 0 0 2px rgba(255,255,255,.07) inset,0 40px 80px -30px rgba(0,0,0,.6)}`;

  // big centred text that slams in (scale 1.5 -> 1 with a shake)
  function slam(text, t0, top, size, opts = {}) {
    const dt = T - t0;
    if (dt < 0) return "";
    const s = 1 + 0.5 * Math.exp(-dt * 9) * (dt < 0.6 ? 1 : 0);
    const sh = dt < 0.35 ? Math.sin(dt * 120) * 10 * (1 - dt / 0.35) : 0;
    const o = clamp(dt / 0.08);
    return `<div class="abs vt" style="left:40px;right:40px;top:${top}px;text-align:center;font-size:${size}px;opacity:${o};transform:translateX(${sh}px) scale(${s});${opts.style ?? ""}">${text}</div>`;
  }
  const pop = (t0, o = {}) => appear(t0, { dy: o.dy ?? 60, scale: o.scale ?? .8, dur: .45, until: o.until });
  const iconCircle = (e, bg = "#E0262B", size = 180) => `<div style="width:${size}px;height:${size}px;border-radius:50%;background:${bg};display:flex;align-items:center;justify-content:center;font-size:${size * .5}px;box-shadow:0 0 50px rgba(224,38,43,.45)">${e}</div>`;
  function bar(x, y, w, p, label, col = "#E0262B") {
    return `<div class="abs" style="left:${x}px;top:${y}px;width:${w}px;height:34px;border-radius:17px;background:rgba(255,255,255,.12)"><div style="height:100%;width:${100 * clamp(p)}%;border-radius:17px;background:${col}"></div></div>
      <div class="abs vt" style="left:${x}px;top:${y + 52}px;font-size:46px">${label}</div>`;
  }
  function gearsRow(top, lit) {
    return `<svg class="abs" style="left:90px;top:${top}px" width="900" height="300">${[0, 1, 2].map(i => {
      const on = lit[i], r = 110;
      return `<g transform="translate(${150 + i * 300},150) rotate(${(i % 2 ? -1 : 1) * T * (on ? 60 : 8)})"><path d="${gearPath(r, 12, 24)}" fill="${on ? "#E0262B" : "none"}" stroke="${on ? "#E0262B" : "rgba(255,255,255,.35)"}" stroke-width="8"/><circle r="38" fill="#0E0E10"/></g>
        <text x="${150 + i * 300}" y="${168}" text-anchor="middle" font-size="54" font-weight="900" fill="#fff">${i + 1}</text>`;
    }).join("")}</svg>`;
  }
  function figureCard(kind, top, h = 760, label = "") {
    return `<div class="vcard" style="left:60px;top:${top}px;width:960px;height:${h}px;overflow:hidden">
      <div class="grid" style="opacity:.7"></div>
      <div class="abs" style="left:40px;top:${(h - 690) / 2}px">${figureSVG(kind, T, 880, 690)}</div>
      ${label ? `<div class="abs pill" style="right:30px;top:30px;background:#FBE3E2;color:#E0262B;font-size:28px">${label}</div>` : ""}</div>`;
  }
  const stamp = (t0, top) => T < t0 ? "" : `<div class="abs" style="left:0;right:0;top:${top}px;text-align:center;transform:scale(${1 + 1.2 * Math.exp(-(T - t0) * 12)}) rotate(-8deg);opacity:${clamp((T - t0) * 8)}">
      <span style="display:inline-block;border:14px solid #E0262B;color:#E0262B;border-radius:30px;padding:0 40px;font-family:'Inter Display';font-weight:900;font-size:150px;background:rgba(14,14,16,.6)">✕</span></div>`;

  // ---------- beats per short ----------
  const BEATS = {
    v1_three_gears: [
      ["missing one", () => gearsRow(380, [1, 1, 0]) + `<div class="abs" style="left:770px;top:420px;font-size:140px;transform:rotate(${8 * Math.sin(T * 6)}deg)">❓</div>`
        + slam(`If you only <span class="vred">lift</span>…`, at("missing one") - .4, 780, 96) + slam(`you're missing one`, at("missing one") + .3, 900, 84, { style: "color:#bbb" })],
      ["gear one", () => `<div class="abs vt vred" style="left:80px;top:300px;font-size:330px;${pop(at("gear one"))}">1</div>`
        + `<div class="abs" style="left:640px;top:340px;${pop(at("gear one") + .15)}">${iconCircle("⚡")}</div>`
        + slam("Stored energy", at("gear one") + .4, 680, 100)
        + bar(140, 860, 800, prog(at("ten seconds"), at("ten seconds") + 1.2), `~${Math.round(10 * prog(at("ten seconds"), at("ten seconds") + 1.2))} seconds · all-out`)],
      ["gear two", () => `<div class="abs vt vred" style="left:80px;top:300px;font-size:330px;${pop(at("gear two"))}">2</div>`
        + `<div class="abs" style="left:640px;top:340px;${pop(at("gear two") + .15)}">${iconCircle("🔥")}</div>`
        + slam("Fast sugar burn", at("gear two") + .4, 680, 100)
        + bar(140, 860, 800, prog(at("two minutes"), at("two minutes") + 1.2), `up to ${Math.max(0, Math.round(120 * prog(at("two minutes"), at("two minutes") + 1.2)))} sec`)
        + (on(at("burning feeling")) ? [0, 1, 2, 3, 4, 5, 6].map(k => { const q = ((T * .7 + k / 7) % 1); return `<div class="abs" style="left:${100 + k * 130}px;top:${1150 - q * 260}px;font-size:${70 + 30 * Math.sin(k)}px;opacity:${Math.sin(q * Math.PI)}">🔥</div>`; }).join("")
          + slam(`= <span class="vbox">THE BURN</span>`, at("burning feeling") + .6, 1020, 80) : "")],
      ["gear three", () => `<div class="abs vt vred" style="left:80px;top:300px;font-size:330px;${pop(at("gear three"))}">3</div>`
        + `<div class="abs" style="left:640px;top:340px;${pop(at("gear three") + .15)}">${iconCircle("❤️")}</div>`
        + slam("Aerobic engine", at("gear three") + .4, 680, 100)
        + (on(at("hours")) ? slam(`runs for <span class="vbox">HOURS</span>`, at("hours"), 860, 90) : slam("slower…", at("gear three") + 1.2, 860, 70, { style: "color:#999" }))],
      ["lifting trains", () => `<div class="vdark" style="left:60px;top:330px;width:960px;height:300px;${pop(at("lifting trains"))}"><div class="abs" style="left:40px;top:60px;font-size:150px">🏋️</div>
          <div class="abs vt" style="left:240px;top:80px;font-size:70px">Lifting</div><div class="abs vt vred" style="left:240px;top:170px;font-size:60px">→ gears 1 + 2</div></div>`
        + `<div class="vdark" style="left:60px;top:680px;width:960px;height:300px;${pop(at("easy cardio"))}"><div class="abs" style="left:40px;top:60px;font-size:150px">🚶</div>
          <div class="abs vt" style="left:240px;top:80px;font-size:70px">10 min easy cardio</div><div class="abs vt vred" style="left:240px;top:170px;font-size:60px">→ gear 3</div></div>`],
      ["all three", () => gearsRow(330, [1, 1, 1]) + slam(`Train <span class="vbox">all 3</span>`, at("all three"), 720, 120)
        + slam("= a bigger engine 🔥", at("all three") + 1.2, 880, 84)],
      ["follow", () => slam(`Follow for the<br><span class="vred">full workout</span>`, at("follow"), 560, 110)],
    ],
    v2_goblet_squat: [
      ["barbell squat", () => figureCard("squat", 300, 700) + `<div class="abs" style="left:240px;top:470px;width:600px;height:26px;border-radius:13px;background:#333"></div>` + stamp(at("barbell squat") + .5, 540)
        + slam(`Not the <span class="vred">barbell</span> squat`, at("barbell squat"), 1060, 84)],
      ["start with this", () => slam(`Start with<br><span class="vbox">THIS</span> 👇`, at("start with this"), 520, 140)],
      ["goblet squat", () => slam(`GOBLET SQUAT`, at("goblet squat"), 230, 110) + figureCard("squat", 380, 720, "Quads · Glutes · Core")
        + stepPill([["dumbbell at your chest", "Dumbbell at your chest"], ["back safe", "Chest up · back safe"], ["feet shoulder", "Feet shoulder-width"], ["sit down", "Sit between your hips"], ["knees follow", "Knees follow your toes"], ["drive the floor", "Drive the floor away"]], 1130)],
      ["heels lift", () => figureCard("squat", 300, 620) + `<div class="vcard" style="left:60px;top:960px;width:960px;height:220px;border:6px solid #E0262B;${pop(at("heels lift"))}">
          <div class="abs" style="left:40px;top:34px;font-size:34px;font-weight:900;letter-spacing:.14em;color:#E0262B">✕ HEELS LIFTING?</div>
          <div class="abs vt" style="left:40px;top:96px;font-size:62px;color:#111">Weight in your mid-foot</div></div>`],
      ["three sets", () => slam(`<span class="vbox" style="font-size:220px">3 × 10</span>`, at("three sets"), 520, 200) + slam("sets × reps", at("three sets") + .5, 830, 60, { style: "color:#999" })],
      ["biggest muscles", () => `<div class="abs" style="${pop(at("biggest muscles"))}">${mgEngine(90, 300, 900, 640)}</div>` + slam(`Legs = your <span class="vred">biggest</span> engine`, at("biggest muscles") + .4, 1010, 76)],
      ["save this", () => slam(`📌 SAVE THIS<br><span class="vred">for leg day</span>`, at("save this"), 560, 120)],
    ],
    v3_first_plan: [
      ["all you need", () => slam(`Here's <span class="vbox">ALL</span><br>you need`, at("all you need"), 500, 130) + `<div class="abs" style="left:0;right:0;top:${880 + 20 * Math.sin(T * 8)}px;text-align:center;font-size:120px;opacity:${clamp((T - at("all you need") - .4) * 3)}">👇</div>`],
      ["three full-body", () => slam(`<span class="vred">3</span> full-body days`, at("three full-body"), 260, 96) + calendar(430)],
      ["two to three sets", () => statRows([["2–3", "sets", at("two to three sets")], ["8–12", "reps", at("eight to twelve")], ["60–90 s", "rest", at("sixty to ninety")]], 320)],
      ["the secret", () => slam(`THE <span class="vbox">SECRET</span> 🤫`, at("the secret"), 560, 130)],
      ["in the tank", () => slam(`Stop with <span class="vred">2–3 reps</span><br>in the tank`, at("in the tank"), 280, 84) + repTank(620)],
      ["twelve reps", () => slam(`Hit <span class="vbox">12</span> on every set`, at("twelve reps"), 280, 90) + stairs(520, at("add a little")) + slam("→ add a little weight", at("add a little") + .2, 1060, 72, { style: "color:#E0262B" })],
      ["that's it", () => slam(`That's it.`, at("that's it"), 620, 170)],
      ["twelve weeks", () => slam(`Run it for`, at("twelve weeks") - .3, 380, 90) + slam(`<span class="vbox" style="font-size:200px">12 WEEKS</span>`, at("twelve weeks"), 500, 200) + weeksBar(820, at("twelve weeks"))],
      ["save this", () => slam(`📌 SAVE THIS`, at("save this"), 520, 140) + slam(`follow for the <span class="vred">exercises</span>`, at("save this") + .8, 720, 76)],
    ],
    v4_three_mistakes: [
      ["mistake one", () => mistakeHead(1, "Too heavy, too soon", at("mistake one"))
        + bar(140, 760, 800, prog(at("ego grows"), at("ego grows") + .8), on(at("ego grows")) ? "EGO 📈" : "", "#E0262B")
        + bar(140, 960, 800, on(at("muscles don't")) ? .12 : 0, on(at("muscles don't")) ? "MUSCLE 📉" : "", "#888")],
      ["mistake two", () => mistakeHead(2, "Skipping the warm-up", at("mistake two")) + `<div class="abs" style="${pop(at("five minutes"))}">${mgThermo(300, 720, 480, 380, prog(at("five minutes"), at("five minutes") + 1.5))}</div>`
        + slam(`just <span class="vbox">5 min</span>`, at("five minutes") + .3, 1130, 70)],
      ["mistake three", () => mistakeHead(3, "New program every week", at("mistake three")) + programShuffle(760, at("mistake three") + .5, at("time to adapt"))
        + slam(`Give it time ⏳`, at("time to adapt"), 1150, 76)],
      ["fix your fuel", () => slam(`FIX YOUR <span class="vbox">FUEL</span> ⛽`, at("fix your fuel"), 250, 100)
        + `<div class="vcard" style="left:60px;top:420px;width:460px;height:640px;overflow:hidden;${pop(at("protein"))}">${mgProtein(460, 400, at("protein"))}<div class="abs vt" style="left:30px;top:440px;font-size:80px;color:#E0262B">1.6 g/kg</div><div class="abs" style="left:34px;top:540px;font-size:34px;font-weight:800">protein a day</div></div>`
        + `<div class="vcard" style="left:560px;top:420px;width:460px;height:640px;overflow:hidden;${pop(at("sleep"))}">${mgSleepClock(460, 400, at("sleep"))}<div class="abs vt" style="left:30px;top:440px;font-size:80px;color:#E0262B">7–9 h</div><div class="abs" style="left:34px;top:540px;font-size:34px;font-weight:800">sleep</div></div>`],
      ["guilty", () => slam(`Which one<br>are <span class="vbox">YOU?</span>`, at("guilty"), 360, 130)
        + `<div class="abs" style="left:0;right:0;top:760px;text-align:center">${[1, 2, 3].map((n, i) => `<span class="vt" style="display:inline-block;margin:0 22px;width:180px;height:180px;line-height:180px;border-radius:50%;background:#18181B;font-size:100px;border:6px solid #E0262B;${pop(at("guilty") + .4 + i * .15)}">${n}</span>`).join("")}</div>`
        + `<div class="abs" style="left:0;right:0;top:1020px;text-align:center;font-size:${110 + 10 * Math.sin(T * 6)}px;opacity:${clamp((T - at("comment")) * 4)}">💬👇</div>`],
    ],
  };
  function stepPill(items, top) {
    let cur = -1; items.forEach((it, i) => { if (on(at(it[0]))) cur = i; });
    if (cur < 0) return "";
    const t0 = at(items[cur][0]);
    return `<div class="abs" style="left:0;right:0;top:${top}px;text-align:center;${appear(t0, { dy: 30, scale: .85, dur: .35 })}">
      <span class="vt" style="display:inline-flex;align-items:center;gap:20px;background:#fff;color:#111;border-radius:999px;padding:18px 40px;font-size:56px">
      <span style="display:inline-flex;width:72px;height:72px;border-radius:50%;background:#E0262B;color:#fff;align-items:center;justify-content:center;font-size:40px">${cur + 1}</span>${items[cur][1]}</span></div>`;
  }
  function calendar(top) {
    const days = ["M", "T", "W", "T", "F", "S", "S"], hit = { 0: at("monday"), 2: at("wednesday"), 4: at("friday") };
    return `<div class="abs" style="left:60px;top:${top}px;width:960px">${days.map((d, i) => { const lit = hit[i] !== undefined && on(hit[i]);
      return `<div class="abs vt" style="left:${i % 4 * 245}px;top:${Math.floor(i / 4) * 300}px;width:220px;height:270px;border-radius:30px;background:${lit ? "#E0262B" : "#18181B"};text-align:center;padding-top:40px;font-size:90px;${pop(at("three full-body") + .1 + i * .06)};${lit ? "box-shadow:0 0 60px rgba(224,38,43,.6)" : ""}">${d}<div style="font-size:80px;margin-top:20px">${lit ? "🏋️" : "·"}</div></div>`; }).join("")}</div>`;
  }
  function statRows(rows, top) {
    return rows.map((r, i) => `<div class="${i === 1 ? "vcard" : "vdark"}" style="left:60px;top:${top + i * 290}px;width:960px;height:250px;${pop(r[2])}">
      <div class="abs vt" style="left:50px;top:55px;font-size:150px;color:${i === 1 ? "#E0262B" : "#fff"}">${r[0]}</div>
      <div class="abs vt" style="right:50px;top:95px;font-size:70px;color:${i === 1 ? "#111" : "#999"}">${r[1]}</div></div>`).join("");
  }
  function repTank(top) {
    const t0 = at("in the tank");
    return `<div class="abs" style="left:60px;top:${top}px;width:960px">${[...Array(12)].map((_, i) => { const left = i >= 9;
      return `<div class="abs vt" style="left:${(i % 4) * 245}px;top:${Math.floor(i / 4) * 170}px;width:220px;height:150px;border-radius:24px;text-align:center;line-height:150px;font-size:70px;
        ${left ? "border:7px dashed #E0262B;color:#E0262B" : "background:#fff;color:#111"};${pop(t0 + .2 + i * .08, { dy: 30 })}">${i + 1}</div>`; }).join("")}</div>`;
  }
  function stairs(top, t1) {
    return `<svg class="abs" style="left:90px;top:${top}px" width="900" height="500">${[1, 2, 3, 4, 5, 6].map((s, i) => { const t0 = t1 - .6 + i * .25, hgt = 80 + i * 65, p = easeOut(prog(t0, t0 + .4));
      return `<rect x="${i * 150}" y="${480 - hgt * p}" width="130" height="${hgt * p}" rx="18" fill="${i < 1 ? "#fff" : "#E0262B"}"/>`; }).join("")}</svg>`;
  }
  function weeksBar(top, t0) {
    return `<div class="abs" style="left:60px;top:${top}px;width:960px">${[...Array(12)].map((_, i) => `<div class="abs" style="left:${i * 80}px;top:0;width:66px;height:${120 + i * 14}px;border-radius:14px;background:${on(t0 + .3 + i * .12) ? "#E0262B" : "rgba(255,255,255,.12)"}"></div>`).join("")}</div>`;
  }
  function mistakeHead(n, text, t0) {
    return `<div class="abs vt" style="left:70px;top:260px;font-size:300px;color:#E0262B;${pop(t0)}">#${n}</div>
      <div class="abs" style="left:760px;top:330px;${pop(t0 + .2)}">${iconCircle("✕", "#E0262B", 200)}</div>
      ${slam(text, t0 + .35, 600, text.length > 18 ? 80 : 100)}`;
  }
  function programShuffle(top, t0, t1) {
    const names = ["Bro split", "PPL", "5×5", "HIIT", "Arnold split", "Upper/Lower"];
    const k = Math.floor(Math.max(0, Math.min(T, t1) - t0) * 5) % names.length;
    return `<div class="vcard" style="left:240px;top:${top}px;width:600px;height:300px;transform:rotate(${(k % 2 ? 4 : -4) * (T < t1 ? 1 : 0)}deg);${pop(t0)}">
      <div class="abs" style="left:40px;top:40px;font-size:30px;font-weight:800;letter-spacing:.14em;color:#999">THIS WEEK'S PLAN</div>
      <div class="abs vt" style="left:40px;top:110px;font-size:100px;color:#111">${T < t1 ? names[k] : "Same plan ✓"}</div></div>`;
  }

  function hook() {
    const h = V.hook, ph = V.photo, dt = T;
    const kb = 1.08 + 0.06 * clamp(T / 2.5);
    const shake = dt < .4 ? Math.sin(dt * 110) * 14 * (1 - dt / .4) : 0;
    return `<div class="abs" style="inset:0;overflow:hidden"><img src="${img(ph, false)}" style="position:absolute;width:100%;height:100%;object-fit:cover;object-position:${V.photoPos || "50% 50%"};transform:scale(${kb}) translateX(${shake}px);filter:grayscale(1) contrast(1.15) brightness(.7)"></div>
      <div class="abs" style="inset:0;background:linear-gradient(180deg,rgba(14,14,16,.2) 0%,rgba(14,14,16,.15) 40%,rgba(14,14,16,.92) 75%)"></div>${leaks(.8)}
      <div class="abs vt" style="left:60px;right:60px;top:1060px;font-size:96px;${appear(.05, { dy: 40, dur: .35 })}">${h[0]}</div>
      ${slam(`<span class="vbox" style="font-size:${h[1].length > 14 ? 110 : 140}px">${h[1]}</span>`, .35, 1190, 140, { style: "text-align:left" })}`;
  }
  function tail() {
    const c = V, tt = T - c.dur, click = c.dur + 1.0, clicked = T >= click, press = clicked && T < click + .15 ? .85 : 1;
    const cp = easeInOut(prog(c.dur + .4, click - .05)), ig = c.platform === "ig";
    return `${ribbon("r", .7)}
      <div class="abs" style="left:390px;top:430px;width:300px;height:300px;border-radius:50%;overflow:hidden;box-shadow:0 0 0 8px #E0262B,0 0 80px rgba(224,38,43,.6);${appear(c.dur + .05, { scale: .6 })}">
        <img src="${img("side", false)}" style="position:absolute;width:330%;height:330%;left:-118%;top:-38%;object-fit:cover;filter:grayscale(1) contrast(1.1)"></div>
      <div class="abs vt" style="left:0;right:0;top:790px;text-align:center;font-size:96px;${appear(c.dur + .15)}">Dr Mak Fitness</div>
      <div class="abs" style="left:0;right:0;top:910px;text-align:center;color:#E0262B;font-size:50px;font-weight:800;${appear(c.dur + .25)}">${c.handle}</div>
      <div class="abs" style="left:0;right:0;top:1130px;text-align:center;${appear(c.dur + .35)}"><span style="display:inline-block;transform:scale(${press});padding:26px 70px;border-radius:999px;font-weight:900;font-size:56px;color:#fff;
        background:${clicked ? "#2A2A2E" : "#E0262B"};box-shadow:${clicked ? "none" : "0 0 60px rgba(224,38,43,.75)"}">${clicked ? (ig ? "✓ Following" : "✓ Subscribed") : (ig ? "Follow" : "▶ Subscribe")}</span></div>
      <svg class="abs" style="left:${lerp(760, 600, cp)}px;top:${lerp(1500, 1190, cp)}px;${tt < .4 ? "opacity:0" : ""}" width="70" height="80"><path d="M5 5 L5 60 L20 47 L31 70 L41 66 L30 43 L50 43 Z" fill="#fff" stroke="#111" stroke-width="3" transform="scale(${press})"/></svg>
      <div class="abs" style="inset:0;background:#000;opacity:${prog(c.end - .35, c.end)}"></div>`;
  }
  function captions() {
    const cap = V.captions.find(c => T >= c.s && T < c.e);
    if (!cap || T < V.hookEnd) return "";
    return `<div class="abs" style="left:50px;right:50px;top:1280px;display:flex;flex-wrap:wrap;justify-content:center;gap:12px">${cap.words.map((w, i) =>
      `<span class="vt" style="display:inline-block;font-size:72px;padding:6px 20px;border-radius:16px;background:${i === cap.hl ? "#E0262B" : "#fff"};color:${i === cap.hl ? "#fff" : "#111"};${appear(cap.s + i * .05, { dy: 24, scale: .85, dur: .3 })}">${w.replace(/[,.:;?]$/, "")}</span>`).join("")}</div>`;
  }

  window.setVertical = cfg => {
    V = cfg;
    document.documentElement.style.cssText = "width:1080px;height:1920px";
    document.body.style.cssText = "width:1080px;height:1920px;background:#0E0E10;overflow:hidden";
    document.body.innerHTML = `<style>${css}</style><div id="v" class="abs" style="inset:0"></div>`;
  };
  window.renderVertical = t => {
    T = t;
    let h = `<div class="vbg"></div>`;
    if (t >= V.dur) {
      h += leaks(.9) + tail();
    } else if (t < V.hookEnd) {
      h += hook();
    } else {
      h += leaks(.7);
      const beats = BEATS[V.id];
      let cur = null, start = 0;
      for (const b of beats) if (t >= at(b[0]) - .05) { cur = b; start = at(b[0]); }
      if (cur) {
        h += cur[1]();
        const since = t - start + .05;
        if (since < .28) { const y = 1920 - 2300 * easeInOut(since / .28);
          h += `<div class="abs" style="left:-100px;right:-100px;top:${y}px;height:260px;background:#E0262B;z-index:40;transform:skewY(-8deg);box-shadow:0 0 80px rgba(224,38,43,.8)"></div>`; }
      }
      h += captions();
    }
    // top chrome: handle + progress
    if (t < V.dur) {
      h += `<div class="abs" style="left:60px;top:150px;font-size:30px;font-weight:800;color:rgba(255,255,255,.85);z-index:45"><span style="color:#E0262B">▶</span> ${V.handle}</div>`;
      h += `<div class="abs" style="left:0;top:0;height:10px;background:#E0262B;z-index:45;width:${W * t / V.dur}px"></div>`;
    }
    // punch-ins on the beats listed for this short
    let kick = 0;
    for (const p of V.punches || []) if (t >= p && t < p + .7) kick = Math.max(kick, Math.exp(-(t - p) * 7));
    if (kick > .001) h = `<div class="abs" style="inset:0;transform:scale(${1 + .05 * kick}) translate(${Math.sin(t * 95) * 8 * kick}px,${Math.cos(t * 83) * 6 * kick}px)">${h}</div><div class="abs" style="inset:0;background:rgba(224,38,43,${.18 * kick * kick});z-index:80"></div>`;
    document.getElementById("v").innerHTML = h;
  };
})();
