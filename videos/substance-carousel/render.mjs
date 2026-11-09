// Render the F10–F19 carousel: slides.json -> 1080x1350 PNGs. Photos come from <out_dir>/../assets (outside git).
//
// Usage: node render.mjs <out_dir> [assets_dir]
import { createRequire } from "node:module";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const { chromium } = createRequire(import.meta.url)("playwright");
const here = path.dirname(fileURLToPath(import.meta.url));
const [out, assets = path.join(out, "..", "assets")] = process.argv.slice(2);
const data = JSON.parse(fs.readFileSync(path.join(here, "slides.json"), "utf8"));
if (data.slides.length > 20) throw new Error("Instagram allows 20 slides");
fs.mkdirSync(out, { recursive: true });
// the page loads photos from ./assets next to it, so render a copy beside the assets
const page_ = path.join(path.dirname(path.resolve(assets)), "carousel.html");
fs.copyFileSync(path.join(here, "carousel.html"), page_);
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1080, height: 1350 } });
await page.goto("file://" + page_);
await page.evaluate(() => document.fonts.ready);
for (let i = 0; i < data.slides.length; i++) {
  await page.evaluate(([d, i]) => window.show(d, i), [data, i]);
  await page.waitForTimeout(150);
  await page.screenshot({ path: path.join(out, `slide_${String(i + 1).padStart(2, "0")}.png`) });
}
await browser.close();
console.log(data.slides.length, "slides ->", out);
