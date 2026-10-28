// Reel cover 1080x1920 (key text inside the 3:4 profile-grid crop). Usage: node cover.mjs <out.png>
import { createRequire } from "node:module";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const { chromium } = createRequire(import.meta.url)("playwright");
const dir = path.dirname(fileURLToPath(import.meta.url));
const groups = JSON.parse(fs.readFileSync(path.join(dir, "../script.json"), "utf8")).beats.filter(b => b.type === "group");
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
await page.goto("file://" + path.join(dir, "cover.html"));
await page.evaluate(g => window.setGroups(g), groups);
await page.evaluate(() => document.fonts.ready);
await page.screenshot({ path: process.argv[2] });
await browser.close();
