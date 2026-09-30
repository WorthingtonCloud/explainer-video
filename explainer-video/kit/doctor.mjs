// Preflight for an explainer: run this before anything else, so a missing tool fails here with a plain message instead
// of deep inside a build with a confusing one.   node doctor.mjs
// (The explainer kit's own copy: it replaces the renderer's doctor when the kits are copied into a project.)
import { execFileSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { findPuppeteer, findChrome } from "./lib/browser.mjs";

const rows = [];
const add = (need, name, ok, detail, fix) => rows.push({ need, name, ok, detail, fix });
const sh = (cmd, args) => { try { return execFileSync(cmd, args, { encoding: "utf8", stdio: ["ignore", "pipe", "pipe"] }); } catch { return null; } };

add("required", "node 22+", Number(process.versions.node.split(".")[0]) >= 22, process.versions.node, "install Node 22 or newer (HyperFrames needs it)");

const ffv = sh("ffmpeg", ["-hide_banner", "-version"]);
const filters = sh("ffmpeg", ["-hide_banner", "-filters"]) || "";
// A stripped ffmpeg reports a missing filter as a syntax error in your command. Check the ones the kit uses.
const needF = ["scale", "crop", "fps", "format", "overlay", "fade", "tpad", "tile", "drawbox", "signalstats", "metadata",
  "ebur128", "ametadata", "setparams", "afade", "atrim", "aformat", "alimiter", "apad", "aresample", "acrossfade", "volume", "hstack", "vstack"];
const encoders = sh("ffmpeg", ["-hide_banner", "-encoders"]) || "";
const missing = [...needF.filter((f) => !new RegExp(`\\s${f}\\s`).test(filters)),
  ...["libx264", "aac", "pcm_s16le"].filter((e) => !new RegExp(`\\s${e}\\s`).test(encoders)).map((e) => `${e} encoder`)];
add("required", "ffmpeg (full build)", !!ffv && missing.length === 0, ffv ? (missing.length ? `missing: ${missing.join(", ")}` : ffv.split("\n")[0].slice(0, 40)) : "not found",
  "install a full ffmpeg (macOS: brew install ffmpeg · Linux: your package manager, or a static build)");
add("required", "ffprobe", !!sh("ffprobe", ["-version"]), "", "comes with ffmpeg");
add("required", "curl", !!sh("curl", ["--version"]), "", "install curl (the take check uploads with it)");

const hfv = sh(process.platform === "win32" ? "npx.cmd" : "npx", ["--no-install", "hyperframes", "--version"]);
add("required", "hyperframes", !!hfv, (hfv || "not found").trim().split("\n").pop(), "in this folder: npm install   (renders the video)");
add("required", "gsap", fs.existsSync("node_modules/gsap/dist/gsap.min.js"), "node_modules/gsap", "in this folder: npm install");
const pp = findPuppeteer();
add("required", "puppeteer", !!pp, pp ? `${pp.name}` : "not found", "in this folder: npm i puppeteer   (audit, stills)");
if (pp?.name === "puppeteer-core") add("required", "Chrome", !!findChrome(), findChrome() || "not found", "set CHROME=/path/to/chrome");

const PY = process.env.PYTHON || "python3";
const py = sh(PY, ["-c", "import sys; print(sys.version.split()[0])"]);
add("required", PY, !!py, (py || "").trim(), "install Python 3.9+ (Windows: run the kit under WSL)");
const np = sh(PY, ["-c", "import numpy; print(numpy.__version__)"]);
add("required", "numpy", !!np, (np || "").trim() || "not found", "pip install numpy   (mix.py, pitch.py, voicebed.py; or set PYTHON to one that has it)");

const plan = fs.existsSync("plan.json") ? JSON.parse(fs.readFileSync("plan.json", "utf8")) : null;
add("required", "plan.json", !!plan, plan ? `${plan.name} v${plan.version}` : "none yet", "cp plan.example.json plan.json, then make it yours");
const fcss = plan?.font?.css;
add("required", "font", !!fcss && fs.existsSync(fcss), fcss && fs.existsSync(fcss) ? fcss : "not downloaded", 'node fonts.mjs Archivo && node fonts.mjs "JetBrains Mono" 500,700   (or your brand\'s Google Fonts)');
add("optional", "narrator", !!plan?.narrator?.voice, plan?.narrator?.voice || "not chosen yet", 'python3 voices.py (free previews), then plan.json → "narrator": {"voice": "<ID>"}');

// keys: the environment, else the nearest .env in this folder or any folder above it (the same lookup as keys.py)
const envKey = (k) => {
  if (process.env[k]) return true;
  for (let d = process.cwd(); ; d = path.dirname(d)) {
    const f = path.join(d, ".env");
    if (fs.existsSync(f) && new RegExp(`^${k}=.+`, "m").test(fs.readFileSync(f, "utf8"))) return true;
    if (path.dirname(d) === d) return false;
  }
};
add("paid", "ELEVENLABS_API_KEY", envKey("ELEVENLABS_API_KEY"), "the narration (and the sound effects)", "ElevenLabs → API key → .env   (library voices need a paid plan over the API)");
add("paid, optional", "OPENAI_API_KEY", envKey("OPENAI_API_KEY"), "the take check: transcribe the take back (about a cent)", "OpenAI → API key → .env");
add("paid, optional", "KIE_AI_API_KEY", envKey("KIE_AI_API_KEY"), "the music bed (Suno on kie.ai, about $0.12)", "kie.ai → API key → .env   (or bring your own track)");

let bad = 0;
for (const r of rows) {
  const mark = r.ok ? "✓" : r.need === "required" ? "✗" : "·";
  if (!r.ok && r.need === "required") bad++;
  console.log(`${mark} ${r.name.padEnd(20)} ${r.need.padEnd(15)} ${r.ok ? r.detail : `${r.detail} → ${r.fix}`}`);
}
console.log(bad ? `\n${bad} required item(s) missing.` : "\nReady. The picture, the audit and the mix cost nothing; the voice, the music and the effects are paid, and each asks first.");
console.log("HyperFrames telemetry: build.mjs turns it off (HYPERFRAMES_NO_TELEMETRY=1). Run hyperframes by hand? Set it yourself.");
process.exit(bad ? 1 : 0);
