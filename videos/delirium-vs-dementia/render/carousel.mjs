// Instagram carousel (1080x1350 PNG slides) from the same renderer: a cover, then each scene in its final state.
//
// Usage: node carousel.mjs <timeline.json> <out_dir>
import { createRequire } from "node:module";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const { chromium } = createRequire(import.meta.url)("playwright");
const [tlPath, out] = process.argv.slice(2);
const tl = JSON.parse(fs.readFileSync(tlPath, "utf8"));
tl.assets ??= "file://" + path.resolve(path.dirname(tlPath), "assets");
const hook = tl.beats[0];
const slides = [[0, true], [hook.cues.delirium - .15, false],  // Dadaji slide: after the ✕, before the title
  ...tl.beats.slice(1).map(b => [b.end - .05, false])];
if (slides.length > 20) throw new Error(`${slides.length} slides; Instagram allows 20`);
fs.mkdirSync(out, { recursive: true });
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1080, height: 1350 } });
await page.goto("file://" + path.join(path.dirname(fileURLToPath(import.meta.url)), "index.html"));
await page.evaluate(d => window.setData(d), tl);
await page.evaluate(() => document.fonts.ready);
for (const [i, [t, cover]] of slides.entries()) {
  await page.evaluate(([t, n, total, c]) => window.renderSlide(t, n, total, c), [t, i + 1, slides.length, cover]);
  await page.evaluate(() => Promise.all([...document.querySelectorAll("*")].map(() => 0)));
  await page.waitForTimeout(150);  // let background images decode
  await page.screenshot({ path: path.join(out, `slide_${String(i + 1).padStart(2, "0")}.png`) });
}
await browser.close();
console.log(slides.length, "slides ->", out);
