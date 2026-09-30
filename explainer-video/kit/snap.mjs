// Stills of the composition at given times, straight from the timeline (no render):  node snap.mjs 44 59.8 … → qa/snap/
import fs from "node:fs"; import path from "node:path"; import { pathToFileURL } from "node:url";
import { launch, loadReel } from "./lib/browser.mjs";
const R = loadReel(), [W, H] = R.size, times = process.argv.slice(2).map(Number);
const b = await launch(), p = await b.newPage();
await p.setViewport({ width: W, height: H, deviceScaleFactor: 1 });
await p.goto(pathToFileURL(path.resolve("comp/index.html")).href, { waitUntil: "load" });
await p.evaluate(async () => { await document.fonts.ready; return true; });
fs.rmSync("qa/snap", { recursive: true, force: true }); fs.mkdirSync("qa/snap", { recursive: true });
for (const t of times) {
  await p.evaluate((t) => { window.__timelines.main.seek(t, false); }, t);
  await p.screenshot({ path: `qa/snap/${t.toFixed(2).padStart(7, "0")}.png` });
}
await b.close(); console.log(`qa/snap/ (${times.length})`);
