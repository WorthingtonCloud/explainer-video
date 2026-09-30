#!/usr/bin/env python3
"""Sound-effect palette for the explainer, from ElevenLabs text-to-sound (eleven_text_to_sound_v2).
Duration set = 11 credits a second (min 0.5 s). Resumable: a file already in sfx/ is never re-bought.
Hard cap CAP credits for the project (ledger.csv, rows starting "sfx"). Needs --yes (the human's go, with the number said first).

    python3 sfx.py --yes"""
import csv, datetime, json, math, os, sys, urllib.request
from keys import key as get_key

CAP = 1000
URL = "https://api.elevenlabs.io/v1/sound-generation?output_format=mp3_44100_192"
PALETTE = {  # name: (seconds, prompt)
    "whoosh1":  (1.2, "soft airy cinematic whoosh transition, smooth air movement, clean, no impact, no music"),
    "whoosh2":  (1.2, "gentle smooth whoosh pass by, soft air, subtle cinematic transition, clean, no music"),
    "swish1":   (0.6, "fast soft swish, quick whip pan air swipe, clean, subtle"),
    "swish2":   (0.6, "quick soft air swipe swoosh, short, clean, subtle"),
    "land1":    (0.8, "soft deep muted thud, gentle low UI impact as a number appears on screen, clean, minimal, no reverb tail"),
    "land2":    (0.8, "soft low felt thump, subtle interface hit, warm, short, clean"),
    "tick1":    (0.5, "single soft UI click tick, subtle clean digital interface sound"),
    "tick2":    (0.5, "tiny soft wooden click, subtle, clean, single"),
    "pop":      (0.5, "soft gentle bubble pop, UI notification, subtle, single"),
    "counter":  (1.5, "rapid soft digital counter ticking, fast tiny ticks speeding up, subtle, clean"),
    "click":    (0.5, "single computer mouse click, crisp, close, clean"),
    "powerup":  (1.2, "soft electric power up shimmer, gentle rising hum of lights turning on, subtle, clean"),
    "shimmer":  (1.6, "delicate digital shimmer swell, many tiny sparkling ticks, airy, soft, subtle"),
    "paper":    (0.6, "paper card sliding onto a table, soft swoosh, close, clean"),
    "error":    (0.6, "soft muted low error buzz, gentle negative UI tone, short, subtle"),
    "chime":    (0.8, "soft positive UI chime, two gentle bright notes, clean, subtle"),
    "lock":     (0.5, "soft digital lock click, clean, subtle, single"),
    "pulse":    (1.0, "soft low sonar pulse, one gentle deep ping, subtle, clean"),
    "riser":    (1.5, "soft short airy riser, gentle tension build, clean, no impact at the end"),
    "sting":    (2.5, "subtle modern logo reveal, one soft low boom with a short airy shimmer tail, clean, minimal, elegant"),
}


def key():
    return get_key("ELEVENLABS_API_KEY")


def spent():
    if not os.path.exists("ledger.csv"): return 0
    return sum(int(r["credits"]) for r in csv.DictReader(open("ledger.csv")) if r["what"].startswith("sfx"))


if "--yes" not in sys.argv:
    todo = [n for n in PALETTE if not os.path.exists(f"sfx/{n}.mp3")]
    sys.exit(f"Would spend about {sum(math.ceil(11 * PALETTE[n][0]) for n in todo)} credits on {len(todo)} sounds. Add --yes.")
os.makedirs("sfx", exist_ok=True)
for name, (secs, prompt) in PALETTE.items():
    out, cost = f"sfx/{name}.mp3", math.ceil(11 * secs)
    if os.path.exists(out): continue
    if spent() + cost > CAP: sys.exit(f"⛔ {name} would pass the {CAP}-credit cap ({spent()} spent)")
    req = urllib.request.Request(URL, method="POST", headers={"xi-api-key": key(), "Content-Type": "application/json"},
        data=json.dumps({"text": prompt, "duration_seconds": secs, "prompt_influence": 0.6, "model_id": "eleven_text_to_sound_v2"}).encode())
    try:
        audio = urllib.request.urlopen(req, timeout=120).read()
    except urllib.error.HTTPError as e:
        sys.exit(f"{name}: HTTP {e.code} {e.read()[:300]}")
    open(out, "wb").write(audio)
    with open("ledger.csv", "a", newline="") as f:
        csv.DictWriter(f, ["date", "what", "credits", "note"]).writerow(
            {"date": datetime.date.today().isoformat(), "what": f"sfx {name}", "credits": cost, "note": prompt[:80]})
    print(f"{out}  {secs}s  ~{cost} credits (total {spent()})", flush=True)
