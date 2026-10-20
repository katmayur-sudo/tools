// Render the HTML motion graphics to video, frame by frame, in parallel chunks.
//
// Usage: node render.mjs <site_dir> <timeline.json> <out_dir> [workers=4] [--stills t1,t2,...]
// <site_dir> must contain render/index.html and assets/{img,user}/.
// Each worker drives its own Chromium page and pipes JPEG frames into its own ffmpeg process;
// the chunks are concatenated afterwards (see tools/finish.sh).
import { chromium } from "/opt/node22/lib/node_modules/playwright/index.mjs";
import { spawn } from "node:child_process";
import fs from "node:fs";
import path from "node:path";

const [siteDir, tlPath, outDir, workersArg, flag, stillsArg] = process.argv.slice(2);
const tl = JSON.parse(fs.readFileSync(tlPath, "utf8"));
const workers = Number(workersArg || 4);
fs.mkdirSync(outDir, { recursive: true });
const url = "file://" + path.resolve(siteDir, "render/index.html");

async function openPage(browser) {
  const page = await browser.newPage({ viewport: { width: tl.width, height: tl.height } });
  await page.goto(url);
  await page.evaluate(t => window.setTimeline(t), tl);
  await page.evaluate(() => document.fonts.ready);
  return page;
}

async function frame(page, t) {
  await page.evaluate(x => window.renderAt(x), t);
  // wait for any images in this frame to decode before capturing
  await page.evaluate(() => Promise.all([...document.images].map(i => i.complete ? 0 : new Promise(r => { i.onload = i.onerror = r; }))));
  return page.screenshot({ type: "jpeg", quality: 92 });
}

const browser = await chromium.launch({ executablePath: "/opt/pw-browsers/chromium-1194/chrome-linux/chrome" });

if (flag === "--stills") {
  const page = await openPage(browser);
  for (const t of stillsArg.split(",").map(Number)) {
    fs.writeFileSync(path.join(outDir, `still_${t.toFixed(2)}.jpg`), await frame(page, t));
  }
  await browser.close();
  process.exit(0);
}

const total = Math.ceil(tl.duration * tl.fps);
const per = Math.ceil(total / workers);
const started = Date.now();
await Promise.all([...Array(workers)].map(async (_, w) => {
  const a = w * per, b = Math.min(total, a + per);
  const page = await openPage(browser);
  const ff = spawn("ffmpeg", ["-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", String(tl.fps),
    "-c:v", "mjpeg", "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
    "-r", String(tl.fps), path.join(outDir, `chunk_${String(w).padStart(2, "0")}.mp4`)], { stdio: ["pipe", "inherit", "inherit"] });
  for (let f = a; f < b; f++) {
    const buf = await frame(page, f / tl.fps);
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once("drain", r));
    if (w === 0 && (f - a) % 300 === 0) {
      const done = (f - a) / (b - a), el = (Date.now() - started) / 1000;
      console.log(`worker0 ${(done * 100).toFixed(1)}%  elapsed ${el.toFixed(0)}s  eta ${done > 0 ? (el / done - el).toFixed(0) : "?"}s`);
    }
  }
  ff.stdin.end();
  await new Promise(r => ff.on("close", r));
}));
await browser.close();
console.log(`rendered ${total} frames in ${((Date.now() - started) / 1000).toFixed(0)}s`);
