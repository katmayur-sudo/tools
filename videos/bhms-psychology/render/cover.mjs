// Reel cover (1080x1920) + YouTube thumbnail (1280x720) from cover.html. Usage: node cover.mjs <out_dir>
import { createRequire } from "node:module";
import path from "node:path";
import { fileURLToPath } from "node:url";

const { chromium } = createRequire(import.meta.url)("playwright");
const dir = path.dirname(fileURLToPath(import.meta.url)), out = process.argv[2];
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1280, height: 1920 } });
await page.goto("file://" + path.join(dir, "cover.html"));
await page.evaluate(() => document.fonts.ready);
for (const id of ["reel", "yt"]) await page.locator("#" + id).screenshot({ path: path.join(out, `cover-${id}.png`) });
await browser.close();
