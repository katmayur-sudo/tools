// Screenshot thumb.html to PNG. Usage: node shot.mjs <v> <out.png>
import { chromium } from "/opt/node22/lib/node_modules/playwright/index.mjs";
import path from "node:path";
const [v, out] = process.argv.slice(2);
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 1280, height: 720 } });
await p.goto("file://" + path.resolve("thumb.html") + "?v=" + v);
await p.evaluate(() => document.fonts.ready);
await p.screenshot({ path: out });
await b.close();
