// Render the vertical 1080x1920 shorts defined in shorts.json, one Chromium page per short.
//
// Usage: node shorts.mjs <site_dir> <timeline.json> <shorts.json> <platform: ig|yt> <out_dir>
// Each short plays the main timeline from `a` to `b` in the vertical layout, then a follow card.
import { chromium } from "/opt/node22/lib/node_modules/playwright/index.mjs";
import { spawn } from "node:child_process";
import fs from "node:fs";
import path from "node:path";

const [siteDir, tlPath, shortsPath, platform, outDir] = process.argv.slice(2);
const tl = JSON.parse(fs.readFileSync(tlPath, "utf8"));
const conf = JSON.parse(fs.readFileSync(shortsPath, "utf8"));
fs.mkdirSync(outDir, { recursive: true });
const url = "file://" + path.resolve(siteDir, "render/index.html");
const browser = await chromium.launch({ executablePath: "/opt/pw-browsers/chromium-1194/chrome-linux/chrome" });
const fps = tl.fps, started = Date.now();

await Promise.all(conf.shorts.map(async sh => {
  const cfg = { ...sh, platform, handle: conf.handles[platform], end: sh.b + conf.tail_seconds };
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  await page.goto(url);
  await page.evaluate(t => window.setTimeline(t), tl);
  await page.evaluate(c => window.setShort(c), cfg);
  await page.evaluate(() => document.fonts.ready);
  const out = path.join(outDir, `${sh.id}_${platform}_video.mp4`);
  const ff = spawn("ffmpeg", ["-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", String(fps), "-c:v", "mjpeg",
    "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", out], { stdio: ["pipe", "inherit", "inherit"] });
  const frames = Math.round((cfg.end - cfg.a) * fps);
  for (let f = 0; f < frames; f++) {
    await page.evaluate(t => window.renderShort(t), cfg.a + f / fps);
    await page.evaluate(() => Promise.all([...document.images].map(i => i.complete ? 0 : new Promise(r => { i.onload = i.onerror = r; }))));
    const buf = await page.screenshot({ type: "jpeg", quality: 92 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once("drain", r));
  }
  ff.stdin.end();
  await new Promise(r => ff.on("close", r));
  console.log(`${sh.id} ${platform}: ${frames} frames`);
}));
await browser.close();
console.log(`done in ${((Date.now() - started) / 1000).toFixed(0)}s`);
