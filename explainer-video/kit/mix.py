#!/usr/bin/env python3
"""The sound pass: the voice, a faint music bed, and sound effects pinned to the picture. No re-render: the new audio is
muxed onto the finished video. Effect times come from reel.json (the same word-pinned cues the scenes animate on) via
this project's cues.py, so a re-recorded voice re-times the effects too.

    $PY mix.py --video out/<name>-vN.mp4 --tag vN [--takes 1 2 3 4] [--music_db -16] [--duck_db 6] [--sfx_db 0] [--no_sfx]
      → out/<name>-vN-sfx.mp4 (voice + effects), out/<name>-vN-take<N>.mp4 (voice + music + effects),
        stems in mix/, and the mixer page's tracks + settings (mixer/media, mixer/config.json)
    $PY = a Python with numpy

Levels are relative to the voice, which is mastered to -16 LUFS (ElevenLabs delivered -24.6: quiet on a phone).
Defaults = the demo's approved mix (Sep 30, 2026): music ~20 dB under the voice, effects as mixed."""
import argparse, importlib.util, json, os, re, subprocess
import numpy as np

SR = 48000
ap = argparse.ArgumentParser()
ap.add_argument("--video", required=True); ap.add_argument("--tag", required=True)
ap.add_argument("--takes", nargs="*", type=int, default=None, help="music takes to mix (default: every music/take*.mp3)")
ap.add_argument("--music_db", type=float, default=-16, help="music bed vs the voice, in pauses (LU)")
ap.add_argument("--duck_db", type=float, default=6, help="extra dip under speech")
ap.add_argument("--sfx_db", type=float, default=0, help="shift every effect up or down")
ap.add_argument("--no_sfx", action="store_true")
a = ap.parse_args()

R = json.load(open("reel.json"))
END = round(sum(s["secs"] for s in R["segments"]), 3)
T, t = {}, 0.0
for s in R["segments"]:
    T[s["name"]] = t
    t += s["secs"]
TT = {tid: T[s["name"]] + a0 for s in R["segments"] for tid, a0, _ in s.get("titles", [])}
C = {k: v.get("cues", {}) for k, v in R["scenes"].items()}
END_T = T[R["segments"][-1]["name"]]  # the end card is always the last segment


def load(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()


def write(path, x):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", path],
                   input=np.ascontiguousarray(x, np.float32).tobytes(), check=True)


def lufs(x):
    write("/tmp/_lufs.wav", x)
    out = subprocess.run(["ffmpeg", "-hide_banner", "-i", "/tmp/_lufs.wav", "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    return float([l for l in out.splitlines() if l.strip().startswith("I:")][-1].split()[1])


db = lambda d: 10 ** (d / 20)
N = int(round(END * SR))
fit = lambda x: np.pad(x, ((0, max(0, N - len(x))), (0, 0)))[:N]
dbf = lambda x: 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-12)

# ── the voice, at -16 LUFS ──
voice = fit(load(R["music"]["file"]))
v_lufs = lufs(voice)
voice *= db(-16 - v_lufs)
print(f"voice {v_lufs:.1f} → -16 LUFS")

# ── the effects: cues.py → cues(T, TT, C, END_T) returns (time, sound, align, level vs the voice in dB). align "peak" puts
#    the sound's loudest moment on the time (a whoosh into a cut); "on" puts its attack there (hits, clicks, ticks). ──
spec = importlib.util.spec_from_file_location("cues", "cues.py"); cm = importlib.util.module_from_spec(spec); spec.loader.exec_module(cm)
CUES = cm.cues(T, TT, C, END_T)
TRIM = getattr(cm, "TRIM", {"click": (0.0, 0.12)})  # ElevenLabs' "single click" came back as three clicks; keep the first

ref = 20 * np.log10(np.sqrt(np.mean(voice[np.abs(voice).max(1) > 0.02] ** 2)) + 1e-9)  # the voice's active loudness
sfx = np.zeros((N, 2), np.float32)
cache = {}
for when, name, align, lvl in CUES:
    if name not in cache:
        x = load(f"sfx/{name}.mp3")
        if name in TRIM:
            a0, a1 = TRIM[name]
            x = x[int(a0 * SR):int(a1 * SR)] * np.linspace(1, 0, int((a1 - a0) * SR))[:, None] ** 0.3
        env = np.sqrt(np.convolve((x ** 2).mean(1), np.ones(240) / 240, "same"))
        act = env > env.max() * 0.1
        rms = 20 * np.log10(np.sqrt(np.mean(x[act] ** 2)) + 1e-9)
        # the peak, and the attack (where it first reaches half its peak): files start with silence of varying length
        cache[name] = (x * db(-rms), int(np.argmax(env)), int(np.argmax(env > env.max() * 0.5)))
    x, pk, att = cache[name]
    x = x * db(ref + lvl + a.sfx_db)
    if np.abs(x).max() > db(-8): x *= db(-8) / np.abs(x).max()  # no single click jumps out of the mix
    s = int(round(when * SR)) - (pk if align == "peak" else att)
    s0, x = max(0, s), x[max(0, -s):]
    x = x[:N - s0]
    sfx[s0:s0 + len(x)] += x
print(f"{len(CUES)} effects placed")
if a.no_sfx: sfx[:] = 0
os.makedirs("mix", exist_ok=True)
write("mix/stem-voice.wav", voice); write("mix/stem-fx.wav", sfx)


def mux(mix, out):
    write("mix/_master.wav", mix * db(-16 - lufs(mix)))
    # a limiter at -2 dB (AAC overshoots a -1.5 limit to -0.6), AAC 192k onto the untouched picture
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.video, "-i", "mix/_master.wav", "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                    "-af", "alimiter=limit=0.8:attack=3:release=60:level=false", "-c:a", "aac", "-b:a", "192k",
                    "-movflags", "+faststart", "-shortest", out], check=True)
    print(out)


base = re.sub(r"-v\d+$", "", os.path.splitext(os.path.basename(a.video))[0])
mux(voice + sfx, f"out/{base}-{a.tag}-sfx.mp4")

# ── the music: faint, dipping a little more under speech (slow release, so it breathes, never pumps), up ~5 dB for the
#    end card, faded to the last frame ──
venv = np.sqrt(np.convolve((voice ** 2).mean(1), np.ones(2400) / 2400, "same"))
speaking = (venv > db(-45)).astype(np.float32)
held = np.convolve(speaking, np.ones(int(0.35 * SR)), "same") > 0
hann = np.hanning(int(0.5 * SR)); duck = np.convolve(held.astype(np.float32), hann / hann.sum(), "same")
tt = np.arange(N) / SR
gain = db(-a.duck_db * duck)
gain = np.where(tt >= END_T, np.minimum(1, gain + (tt - END_T) / 0.6) * db(np.clip((tt - END_T) / 0.6, 0, 1) * 5), gain)
gain *= np.clip(tt / 0.4, 0, 1) * np.clip((END - tt) / 1.4, 0, 1)
names = json.load(open("music/takes.json")) if os.path.exists("music/takes.json") else {}
takes = a.takes or sorted(int(f[4:-4]) for f in os.listdir("music") if re.fullmatch(r"take\d+\.mp3", f))
spk = venv > db(-45)
cfg = {"end": END, "takes": []}
for n in takes:
    m = load(f"music/take{n}.mp3")
    if len(m) < N: print(f"⚠️  take{n} is {len(m) / SR:.1f}s, shorter than the video ({END:.1f}s): Suno extend it, or pick a longer take")
    m = fit(m) * db(-16 + a.music_db - lufs(fit(m))) * gain[:, None]
    write(f"mix/stem-music{n}.wav", m)
    under = round(dbf(m[spk].mean(1)) - dbf(voice[spk].mean(1)), 1)  # what the mixer shows as "N dB under the voice"
    cfg["takes"].append({"n": n, "label": (names.get(f"take{n}") or {}).get("label", f"take {n}"), "under": under})
    print(f"take{n}: music {under:+.1f} dB vs the voice under speech")
    mux(voice + m + sfx, f"out/{base}-{a.tag}-take{n}.mp4")

# ── the mixer page (mixer/index.html): every stem, compressed, plus the picture and the settings ──
os.makedirs("mixer/media", exist_ok=True)
for s in ["voice", "fx"] + [f"music{n}" for n in takes]:
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"mix/stem-{s}.wav", "-ar", "44100", "-c:a", "aac", "-b:a", "160k", f"mixer/media/{s}.m4a"], check=True)
vid = "mixer/media/video.mp4"
if os.path.lexists(vid): os.remove(vid)
os.symlink(os.path.relpath(os.path.abspath(a.video), "mixer/media"), vid)
json.dump(cfg, open("mixer/config.json", "w"), indent=1)
print("mixer: mixer/index.html (serve the project folder: python3 -m http.server, open /mixer/)")
