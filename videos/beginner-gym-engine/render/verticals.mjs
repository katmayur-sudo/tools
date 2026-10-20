// Render native 9:16 shorts built by shorts/build.py.
//
// Usage: node verticals.mjs <site_dir> <data_dir> <ig|yt> <out_dir> [--stills id:t1,t2;id:t3]
import { chromium } from "/opt/node22/lib/node_modules/playwright/index.mjs";
import { spawn } from "node:child_process";
import fs from "node:fs";
import path from "node:path";

const [siteDir, dataDir, platform, outDir, flag, stillsArg] = process.argv.slice(2);
const handles = { ig: "@drmak_fitness", yt: "@drmakfitness" };
const ids = ["v1_three_gears", "v2_goblet_squat", "v3_first_plan", "v4_three_mistakes", "v5_six_zones_home"]
  .filter(id => fs.existsSync(path.join(dataDir, `${id}.json`)));
fs.mkdirSync(outDir, { recursive: true });
const browser = await chromium.launch({ executablePath: "/opt/pw-browsers/chromium-1194/chrome-linux/chrome" });
const url = "file://" + path.resolve(siteDir, "render/index.html");

async function open(id) {
  const data = JSON.parse(fs.readFileSync(path.join(dataDir, `${id}.json`), "utf8"));
  const cfg = { ...data, platform, handle: handles[platform] };
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  await page.goto(url);
  await page.evaluate(c => window.setVertical(c), cfg);
  await page.evaluate(() => document.fonts.ready);
  return { page, cfg };
}
async function shot(page, t) {
  await page.evaluate(x => window.renderVertical(x), t);
  await page.evaluate(() => Promise.all([...document.images].map(i => i.complete ? 0 : new Promise(r => { i.onload = i.onerror = r; }))));
  return page.screenshot({ type: "jpeg", quality: 92 });
}

if (flag === "--stills") {
  for (const part of stillsArg.split(";")) {
    const [id, ts] = part.split(":");
    const { page } = await open(id);
    for (const t of ts.split(",").map(Number)) fs.writeFileSync(path.join(outDir, `${id}_${t.toFixed(2)}.jpg`), await shot(page, t));
    await page.close();
  }
} else {
  await Promise.all(ids.map(async id => {
    const { page, cfg } = await open(id);
    const out = path.join(outDir, `${id}_${platform}_video.mp4`);
    const ff = spawn("ffmpeg", ["-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", "30", "-c:v", "mjpeg", "-i", "-",
      "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", out], { stdio: ["pipe", "inherit", "inherit"] });
    const frames = Math.round(cfg.end * 30);
    for (let f = 0; f < frames; f++) {
      const buf = await shot(page, f / 30);
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once("drain", r));
    }
    ff.stdin.end();
    await new Promise(r => ff.on("close", r));
    console.log(id, platform, frames, "frames");
  }));
}
await browser.close();
