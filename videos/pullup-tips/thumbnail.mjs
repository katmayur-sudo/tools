import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
import fs from 'node:fs';
const here = process.cwd(), shared = '/home/user/tools/videos/pullup-mistakes/render/';
fs.writeFileSync(here + '/.t.html', fs.readFileSync('/home/user/tools/videos/pullup-tips/tips.html', 'utf8').replaceAll('__ASSETS__', 'file://' + here + '/assets/').replaceAll('__RENDER__', 'file://' + shared));
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--allow-file-access-from-files'] });
const tl = JSON.parse(fs.readFileSync('timeline.json', 'utf8'));
async function shot(w, h, cam, gfx, out) {
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto('file://' + here + '/.t.html'); await p.evaluate(t => window.setShort(t), tl); await p.evaluate(() => document.fonts.ready);
  await p.evaluate(([cam, gfx, w, h]) => {
    T = 3; R3.renderer.setSize(w, h, false); R3.cam.aspect = w / h;
    for (const id of ['gl', 'bloom']) { const e = document.getElementById(id); e.style.width = w + 'px'; e.style.height = h + 'px'; }
    document.documentElement.style.width = document.body.style.width = w + 'px'; document.documentElement.style.height = document.body.style.height = h + 'px';
    pose({ p: .82, depress: 1, glow: { lats: [0, 1], back: [0, .9], delts: [0, .5] }, cam: { ...cam, look: V3(...cam.look) } });
    R3.cam.aspect = w / h; R3.cam.updateProjectionMatrix(); R3.renderer.render(R3.scene, R3.cam);
    const bl = document.getElementById('bloom'); bl.width = w / 2; bl.height = h / 2; const x = bl.getContext('2d'); x.filter = 'brightness(.85) contrast(2.4) saturate(1.4) blur(16px)'; x.drawImage(document.getElementById('gl'), 0, 0, w / 2, h / 2); bl.style.cssText = `position:absolute;left:0;top:0;width:${w}px;height:${h}px;mix-blend-mode:screen;opacity:.6`;
    document.getElementById('gl').style.filter = 'contrast(1.15) saturate(1.2)';
    document.getElementById('bg').innerHTML = `<div class="abs" style="inset:0;background:radial-gradient(80% 60% at 50% 45%,#5a050c 0%,#1a0204 55%,#050506 85%)"></div>`;
    document.getElementById('fg').innerHTML = gfx + `<div class="abs" style="inset:0;background:radial-gradient(80% 70% at 50% 45%,transparent 55%,rgba(0,0,0,.7) 100%)"></div>`;
  }, [cam, gfx, w, h]);
  await p.setViewportSize({ width: w, height: h });
  await p.screenshot({ path: out, type: 'jpeg', quality: 95, clip: { x: 0, y: 0, width: w, height: h } });
  await p.close();
}
const Y = '#FFD21E', R = '#FF1F2D';
const arrow = (x1, y1, x2, y2, s = 1) => `<svg class="abs" style="inset:0;overflow:visible;z-index:40" width="2000" height="2000"><defs><marker id="m" markerWidth="6" markerHeight="6" refX="3" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6 Z" fill="${Y}"/></marker></defs>
  <path d="M${x1} ${y1} Q${(x1 + x2) / 2 + 80 * s} ${(y1 + y2) / 2 - 60} ${x2} ${y2}" fill="none" stroke="${Y}" stroke-width="${16 * Math.abs(s)}" stroke-linecap="round" marker-end="url(#m)"/></svg>`;
// 9:16 Shorts cover
await shot(1080, 1920, { az: .18, el: -.1, dist: 4.3, look: [0, 1.98, 0], fov: 30 },
  `<div class="abs a" style="left:0;right:0;top:120px;text-align:center;font-size:230px;z-index:40;text-shadow:0 10px 50px #000"><span style="color:${Y}">5</span> PULL-UP</div>
   <div class="abs a" style="left:0;right:0;top:340px;text-align:center;z-index:40"><span style="display:inline-block;padding:0 40px;background:${R};font-size:220px;transform:rotate(-3deg);box-shadow:0 0 80px ${R}">TIPS</span></div>
   <div class="abs a" style="left:0;right:0;top:1470px;text-align:center;font-size:130px;z-index:40;text-shadow:0 8px 40px #000">FOR A <span style="color:${Y}">WIDER BACK</span></div>
   <div class="abs" style="left:0;right:0;top:1640px;text-align:center;z-index:40"><span style="display:inline-block;padding:14px 34px;border-radius:999px;background:#fff;color:#111;font:900 50px Inter">DR MAK FITNESS</span></div>
   ${arrow(170, 1380, 330, 1130)}${arrow(910, 1380, 750, 1130, -1)}`, 'thumb_shorts.jpg');
await b.close();
