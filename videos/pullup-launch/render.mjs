// Render "The Perfect Pull-Up" launch film (9:16).
//
// Usage: node render.mjs <film_dir> <storyboard.json> <out> [--board] [--workers 4]
//   --board : <out> is a directory; writes one still per scene (mid-scene) + board.png + storyboard.md
//   else    : <out> is the silent MP4 (mux music.wav afterwards, see README.md)
// <film_dir>/assets holds three.min.js (r158) and anatomy.bin/.json from
// ../pullup-mistakes/tools/export_anatomy.py. WebGL runs on SwiftShader, so no GPU is needed.
import { spawn } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const PW = process.env.PLAYWRIGHT_MODULE ?? "/opt/node22/lib/node_modules/playwright/index.mjs";
const { chromium } = await import(fs.existsSync(PW) ? PW : "playwright");
const [filmDir, sbPath, out, ...rest] = process.argv.slice(2);
const opt = k => (rest.includes(k) ? rest[rest.indexOf(k) + 1] : undefined);
const here = path.dirname(fileURLToPath(import.meta.url));
const assets = path.resolve(filmDir, "assets") + "/";
const shared = path.resolve(here, "../pullup-mistakes/render") + "/";
const pagePath = path.resolve(filmDir, ".launch.html");
fs.writeFileSync(pagePath, fs.readFileSync(path.join(here, "launch.html"), "utf8")
  .replaceAll("__ASSETS__", "file://" + assets).replaceAll("__RENDER__", "file://" + shared));
const sb = JSON.parse(fs.readFileSync(sbPath, "utf8"));
const browser = await chromium.launch({ executablePath: process.env.CHROME_PATH ?? "/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
  args: ["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist", "--allow-file-access-from-files"] });

async function open() {
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  await page.goto("file://" + pagePath);
  const dur = await page.evaluate(s => window.setFilm(s), sb);
  await page.evaluate(() => document.fonts.ready);
  return { page, dur };
}
const shot = async (page, t) => { await page.evaluate(x => window.renderAt(x), t); return page.screenshot({ type: "jpeg", quality: 92 }); };

if (rest.includes("--board")) {
  fs.mkdirSync(out, { recursive: true });
  const { page } = await open();
  const beat = 60 / sb.bpm; let b = 0;
  const rows = [];
  for (const [i, sc] of sb.scenes.entries()) {
    const s = b * beat, e = (b + sc.beats) * beat; b += sc.beats;
    const t = s + Math.min(e - s - .05, (e - s) * .7);
    const f = `scene${String(i + 1).padStart(2, "0")}.jpg`;
    fs.writeFileSync(path.join(out, f), await shot(page, t));
    rows.push({ i: i + 1, f, type: sc.type, s, e, copy: sc.caption ?? (Array.isArray(sc.text) ? sc.text.join(" / ") : sc.text) ?? (sc.type === "slot" ? `${sb.slotLead} ${sb.chapters[sc.index]}` : sc.word ? `${sc.pre} ${sc.word}` : sc.sub ?? sc.shot ?? "") });
  }
  const cards = rows.map(r => `<div class="c"><img src="${r.f}"><b>${r.i}. ${r.type}</b> <span>${r.s.toFixed(1)}–${r.e.toFixed(1)} s</span><p>${(r.copy ?? "").replace(/\*/g, "")}</p></div>`).join("");
  fs.writeFileSync(path.join(out, "board.html"), `<!doctype html><meta charset=utf-8><style>body{margin:0;padding:28px;background:#111;color:#eee;font:15px Inter;width:2364px}
    h1{margin:0 0 6px;font-size:30px}.g{display:grid;grid-template-columns:repeat(9,1fr);gap:14px}.c img{width:100%;border-radius:10px;display:block}.c span{float:right;color:#E0262B}.c p{margin:4px 0;color:#bbb;font-size:13px}</style>
    <h1>${sb.name} · storyboard</h1><div style="color:#aaa;margin-bottom:14px">${sb.format} · ${sb.bpm} BPM · ${(b * beat).toFixed(1)} s · ${sb.scenes.length} scenes</div><div class="g">${cards}</div>`);
  const bp = await browser.newPage({ viewport: { width: 2420, height: 1000 } });
  await bp.goto("file://" + path.resolve(out, "board.html")); await bp.waitForTimeout(400);
  await bp.screenshot({ path: path.join(out, "board.png"), fullPage: true });
  fs.writeFileSync(path.join(out, "storyboard.md"), `| # | type | time | copy |\n|---|---|---|---|\n` + rows.map(r => `| ${r.i} | ${r.type} | ${r.s.toFixed(1)}–${r.e.toFixed(1)} s | ${(r.copy ?? "").replace(/\*/g, "")} |`).join("\n") + "\n");
  console.log("board ->", path.join(out, "board.png"));
} else {
  const workers = Number(opt("--workers") ?? 4);
  const { page: p0, dur } = await open(); await p0.close();
  const frames = Math.round(dur * 30), per = Math.ceil(frames / workers);
  const parts = await Promise.all([...Array(workers)].map(async (_, w) => {
    const { page } = await open(), part = `${out}.part${w}.mp4`;
    const ff = spawn("ffmpeg", ["-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", "30", "-c:v", "mjpeg", "-i", "-",
      "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", part], { stdio: ["pipe", "inherit", "inherit"] });
    for (let f = w * per; f < Math.min(frames, (w + 1) * per); f++) {
      const buf = await shot(page, f / 30);
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once("drain", r));
    }
    ff.stdin.end(); await new Promise(r => ff.on("close", r));
    return part;
  }));
  fs.writeFileSync(`${out}.txt`, parts.map(p => `file '${path.resolve(p)}'`).join("\n"));
  await new Promise(r => spawn("ffmpeg", ["-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", `${out}.txt`, "-c", "copy", out], { stdio: "inherit" }).on("close", r));
  for (const p of parts) fs.unlinkSync(p);
  fs.unlinkSync(`${out}.txt`);
  console.log(frames, "frames ->", out);
}
await browser.close();
fs.unlinkSync(pagePath);
