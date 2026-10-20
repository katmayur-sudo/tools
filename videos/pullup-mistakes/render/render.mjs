// Render the refined pull-up short in one grade.
//
// Usage: node render.mjs <film_dir> <porcelain|redblack> <out.mp4> [--stills t1,t2,...] [--workers 4]
// <film_dir> holds timeline.json and assets/ (three.min.js r158, anton.woff2, back.png + side.png cut-outs). Video only; mux the
// soundtrack afterwards (see ../README.md).
import { spawn } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const PW = process.env.PLAYWRIGHT_MODULE ?? "/opt/node22/lib/node_modules/playwright/index.mjs";
const { chromium } = await import(fs.existsSync(PW) ? PW : "playwright");
const [filmDir, grade, out, ...rest] = process.argv.slice(2);
const opt = k => (rest.includes(k) ? rest[rest.indexOf(k) + 1] : undefined);
const here = path.dirname(fileURLToPath(import.meta.url));
const assets = path.resolve(filmDir, "assets") + "/";
const html = fs.readFileSync(path.join(here, "short.html"), "utf8").replaceAll("__ASSETS__", "file://" + assets);
const page_path = path.resolve(filmDir, `.short_${grade}.html`);
fs.writeFileSync(page_path, html);
const tl = JSON.parse(fs.readFileSync(path.join(filmDir, "timeline.json"), "utf8"));
// WebGL for the 3D athlete: SwiftShader works headless without a GPU
const browser = await chromium.launch({ executablePath: process.env.CHROME_PATH ?? "/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
  args: ["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist", "--allow-file-access-from-files"] });

async function open() {
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  await page.goto("file://" + page_path);
  await page.evaluate(([t, g, a]) => window.setShort(t, g, a), [tl, grade, "file://" + assets]);
  await page.evaluate(() => document.fonts.ready);
  return page;
}
async function shot(page, t) {
  await page.evaluate(x => window.renderAt(x), t);
  await page.evaluate(() => Promise.all([...document.images].map(i => i.complete ? 0 : new Promise(r => { i.onload = i.onerror = r; }))));
  return page.screenshot({ type: "jpeg", quality: 92 });
}

if (opt("--stills")) {
  fs.mkdirSync(out, { recursive: true });
  const page = await open();
  for (const t of opt("--stills").split(",").map(Number)) fs.writeFileSync(path.join(out, `${grade}_${t.toFixed(2)}.jpg`), await shot(page, t));
} else {
  const workers = Number(opt("--workers") ?? 4), frames = Math.round(tl.dur * 30), per = Math.ceil(frames / workers);
  const parts = await Promise.all([...Array(workers)].map(async (_, w) => {
    const page = await open(), part = `${out}.part${w}.mp4`;
    const ff = spawn("ffmpeg", ["-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", "30", "-c:v", "mjpeg", "-i", "-",
      "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", part], { stdio: ["pipe", "inherit", "inherit"] });
    for (let f = w * per; f < Math.min(frames, (w + 1) * per); f++) {
      const buf = await shot(page, f / 30);
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once("drain", r));
    }
    ff.stdin.end();
    await new Promise(r => ff.on("close", r));
    return part;
  }));
  fs.writeFileSync(`${out}.txt`, parts.map(p => `file '${path.resolve(p)}'`).join("\n"));
  await new Promise(r => spawn("ffmpeg", ["-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", `${out}.txt`, "-c", "copy", out], { stdio: "inherit" }).on("close", r));
  for (const p of parts) fs.unlinkSync(p);
  fs.unlinkSync(`${out}.txt`);
  console.log(grade, frames, "frames ->", out);
}
await browser.close();
fs.unlinkSync(page_path);
