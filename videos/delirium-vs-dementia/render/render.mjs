// Render Delirium vs Dementia at any size (9:16 Reels/Shorts or 16:9 YouTube), 30 fps.
//
// Usage: node render.mjs <timeline.json> <WxH> <out.mp4> [audio]        full video (silent if no audio)
//        node render.mjs <timeline.json> <WxH> <out_dir> --stills t1,t2  JPEG stills for review
import { spawn } from "node:child_process";
import { createRequire } from "node:module";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const { chromium } = createRequire(import.meta.url)("playwright");  // globally installed; ESM import can't see it
const [tlPath, size, out, arg, stills] = process.argv.slice(2);
const [width, height] = size.split("x").map(Number);
const tl = JSON.parse(fs.readFileSync(tlPath, "utf8"));
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width, height } });
await page.goto("file://" + path.join(path.dirname(fileURLToPath(import.meta.url)), "index.html"));
await page.evaluate(d => window.setData(d), tl);
await page.evaluate(() => document.fonts.ready);
const shot = async t => { await page.evaluate(x => window.renderAt(x), t); return page.screenshot({ type: "jpeg", quality: 95 }); };

if (arg === "--stills") {
  fs.mkdirSync(out, { recursive: true });
  for (const t of stills.split(",").map(Number)) fs.writeFileSync(path.join(out, `${t.toFixed(2)}.jpg`), await shot(t));
} else {
  const audio = arg ? ["-i", arg] : [];
  const ff = spawn("ffmpeg", ["-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", "30", "-c:v", "mjpeg", "-i", "-", ...audio,
    "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
    ...(arg ? ["-c:a", "aac", "-b:a", "256k", "-shortest"] : []), out], { stdio: ["pipe", "inherit", "inherit"] });
  const frames = Math.round(tl.end * 30);
  for (let f = 0; f < frames; f++) {
    const buf = await shot(f / 30);
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once("drain", r));
  }
  ff.stdin.end();
  await new Promise(r => ff.on("close", r));
  console.log(out, frames, "frames");
}
await browser.close();
