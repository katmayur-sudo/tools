// Instagram carousel slides (1080x1350) from a carousels/*.json file. Usage: node carousel.mjs <slides.json> <out_dir>
import { createRequire } from "node:module";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const { chromium } = createRequire(import.meta.url)("playwright");
const [src, out] = process.argv.slice(2);
const { slides } = JSON.parse(fs.readFileSync(src, "utf8"));
if (slides.length > 20) throw new Error(`${slides.length} slides: Instagram allows 20`);
fs.mkdirSync(out, { recursive: true });
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1080, height: 1350 } });
await page.goto("file://" + path.join(path.dirname(fileURLToPath(import.meta.url)), "carousel.html"));
await page.evaluate(() => document.fonts.ready);
for (const [i, s] of slides.entries()) {
  await page.evaluate(([s, i, n]) => window.show(s, i, n), [s, i, slides.length]);
  await page.screenshot({ path: path.join(out, `slide-${String(i + 1).padStart(2, "0")}.jpg`), type: "jpeg", quality: 92 });
}
await browser.close();
console.log(out, slides.length, "slides");
