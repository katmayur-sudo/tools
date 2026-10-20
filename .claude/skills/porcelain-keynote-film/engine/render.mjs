// Render a porcelain keynote film from a storyboard.
//
// Usage: node render.mjs <film_dir> <storyboard.json> <music.wav> <out.mp4> [--res 1080|1440|2160] [--stills t1,t2,...]
// <film_dir> holds film.html plus the assets the storyboard references (relative paths).
// Rendering is split across 4 Chromium pages; frames are piped into FFmpeg and joined with the music.
import { spawn, spawnSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";

let chromium;
try { ({ chromium } = await import("playwright")); }
catch { ({ chromium } = await import(process.env.PLAYWRIGHT_MODULE || "/opt/node22/lib/node_modules/playwright/index.mjs")); }

const [filmDir, sbPath, music, out, ...rest] = process.argv.slice(2);
const opt = k => { const i = rest.indexOf(k); return i >= 0 ? rest[i + 1] : undefined; };
const res = Number(opt("--res") ?? 1080), scale = res / 1080, fps = 30, workers = 4;
const sb = JSON.parse(fs.readFileSync(sbPath, "utf8"));
const exe = process.env.CHROME_PATH || "/opt/pw-browsers/chromium-1194/chrome-linux/chrome";
const browser = await chromium.launch({ executablePath: fs.existsSync(exe) ? exe : undefined });

async function page() {
  const p = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: scale });
  await p.goto("file://" + path.resolve(filmDir, "film.html"));
  const dur = await p.evaluate(s => window.setFilm(s), sb);
  await p.evaluate(() => document.fonts.ready);
  return { p, dur };
}
async function frame(p, t) {
  await p.evaluate(x => window.renderAt(x), t);
  await p.evaluate(() => Promise.all([...document.images].map(i => i.complete ? 0 : new Promise(r => { i.onload = i.onerror = r; }))));
  return p.screenshot({ type: "jpeg", quality: 93 });
}

const stills = opt("--stills");
if (stills) {
  const { p } = await page();
  fs.mkdirSync(out, { recursive: true });
  for (const t of stills.split(",").map(Number)) fs.writeFileSync(path.join(out, `still_${t.toFixed(2)}.jpg`), await frame(p, t));
  await browser.close();
  process.exit(0);
}

const { dur } = await page();
const total = Math.round(dur * fps), per = Math.ceil(total / workers), tmp = out + ".parts";
fs.mkdirSync(tmp, { recursive: true });
await Promise.all([...Array(workers)].map(async (_, w) => {
  const { p } = await page();
  const ff = spawn("ffmpeg", ["-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", String(fps), "-c:v", "mjpeg", "-i", "-",
    "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", path.join(tmp, `p${w}.mp4`)], { stdio: ["pipe", "inherit", "inherit"] });
  for (let f = w * per; f < Math.min(total, (w + 1) * per); f++) {
    const buf = await frame(p, f / fps);
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once("drain", r));
  }
  ff.stdin.end();
  await new Promise(r => ff.on("close", r));
}));
await browser.close();
fs.writeFileSync(path.join(tmp, "list.txt"), [...Array(workers)].map((_, w) => `file 'p${w}.mp4'`).join("\n"));
spawnSync("ffmpeg", ["-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", path.join(tmp, "list.txt"), "-i", music,
  "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out], { stdio: "inherit" });
fs.rmSync(tmp, { recursive: true, force: true });
console.log(`rendered ${total} frames (${dur.toFixed(1)} s) at ${res}p -> ${out}`);
