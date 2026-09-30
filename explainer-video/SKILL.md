---
name: explainer-video
description: >
  Make a narrated motion-graphics explainer end to end, the way an agent should: interview the human, pull the ideas and
  the evidence out of the source, write the act-by-act arc and the narration, record the narrator with word timings,
  draw every scene in code and start each move on the word it illustrates, audit every frame for words and pictures
  fighting, render it, and mix a faint music bed and subtle sound effects under the voice. Vertical, widescreen, or
  both. Use for "make an explainer", "a narrated video about X", "turn this article / report / post into a video",
  "a TL;DR video", "explain X in a video", or to revise, re-voice, re-mix, re-cut an explainer or make its other shape.
  The picture costs nothing; the voice, the music and the effects are paid, gated on the human's yes and logged.
---

# explainer-video

A 2–3 minute narrated explainer your agent makes by itself. You bring the source, your taste and your notes. The agent
writes the arc and the words, records the narrator, draws the scenes, checks the frames, cuts it and mixes the sound.
You never open a video editor.

**The voice keeps the time.** Every animation starts on the word it illustrates, the way a promo cuts on the beat. Change
a line, record it again, and the whole video re-times itself. **It explains the ideas, not the article.** Each act is one
idea and the evidence behind it; the narrator never says "the author" or "in this piece".

**How it works:** `narration.txt` → `narrate.py` (the voice, with a timestamp for every word) → `voicebed.py` →
`plan.json` + `plan.py` (words become seconds) → `reel.json` → `scenes.js` + `build.mjs` → a
[HyperFrames](https://github.com/heygen-com/hyperframes) render → `audit.mjs` (words vs pictures) → `mix.py` (voice +
music + effects, no re-render) → the mixer page, where the human picks the music and the levels.

## Setup, once per video

```bash
mkdir -p videos/<name> && cp -R <this skill>/kit/ videos/<name>/ && cd videos/<name>
mv gitignore .gitignore && cp plan.example.json plan.json
npm install                      # HyperFrames (renders), GSAP (motion), puppeteer (audit, stills). Node 22+
pip install numpy                # mix.py, pitch.py, voicebed.py
node fonts.mjs Archivo && node fonts.mjs "JetBrains Mono" 500,700   # or the brand's Google Fonts
node doctor.mjs                  # says plainly what's missing
```

Keys come from the environment or a `.env` in the video folder (or any folder above it): `ELEVENLABS_API_KEY` for the
narration and the sound effects, `OPENAI_API_KEY` for the take check (optional), `KIE_AI_API_KEY` for the music
(optional: the human can bring a track). ⚠️ ElevenLabs' free plan can't use library voices over the API (HTTP 402
`paid_plan_required`); pay-as-you-go works. `$PY` below means a Python that has numpy (`PYTHON` in `doctor.mjs`).

**What's in the kit.** The renderer (`build.mjs`, `reel.js`, `qa.py`, `lib/`, `fonts.mjs`) comes from the
[sizzle-reel](https://github.com/WorthingtonCloud/sizzle-reel) skill; never edit it per video. The explainer's own
scripts sit beside it. `plan.example.json`, `narration.example.txt`, `scenes.js` and `cues.py` are the demo explainer's
(the video in the README), as a worked example: rewrite them for your video, and keep `scenes.js`'s helpers, icons and
overlap rules. The demo's last scene uses a photo (`stills/room.jpg`) that isn't in the kit: make your own or drop it.
Bump `version` in `plan.json` for every cut the human reviews; never overwrite one they've seen.

## Step 0: the interview, before anything is made

Ask **one question at a time**, each with **your recommended answer**, so the human can confirm or correct. Write every
answer to `brainstorm-<date>.md` before asking the next: the file, not your context, is the record. If the source can
answer a question, read it instead of asking.

1. **The source, the audience, the shape.** What piece is this (article, report, post, talk)? Who watches, and where
   does it post? Vertical 9:16 for phones and feeds, widescreen 16:9 for a site or a talk. Both are one flag apart.
2. **What should a cold viewer *get* by the end?** Not "what the article says": the ideas, and why they matter to them.
3. **The acts.** A rough list of ideas; for each, the evidence and where it comes from.
4. **Does the viewer have to do or provide something?** If so, that gets its own act. A hint at the end isn't enough.
5. **The register.** For example: an informed person being candid and a little funny, with energy; a calm documentary;
   a friendly teacher. Recommend one with energy: a flat read loses people.
6. **The narrator.** Auditions are free (`voices.py`). Does the human appear or get named? Default: no one appears.
7. **The look.** Brand colors, fonts, and the mark and address for the end card. Default: the demo's dark ground with
   one accent color, flat diagrams, one soft spotlight.
8. **Length and budget.** 2–3 minutes. The paid parts of the demo came to about $1.

Close with "anything never to show or say?", then write the brief at the top of the file.

## Step 1: read the source and pull the ideas

What does a cold viewer need to get? What is each idea's evidence, and where is it from? Which lines date themselves
("155 days ago") or say nothing? Check every number against its source now, and again on render day.

## Step 2: the arc, as acts, then wait

One line per act: the idea, the evidence with its source, and the picture. Show it, take notes, and write the locked arc
to `SCRIPT.md`. Expect two rounds. Watch for: any author or article framing; a missing "what you'd need" act; more than
one spoken number per act.

## Step 3: the narration

Write `narration.txt`: one paragraph per act, each under a `# N title` line. With ElevenLabs' `eleven_v4` model, stage
directions in brackets (`[wry]`, `[deadpan]`, `[leaning in]`) steer the read and aren't spoken; CAPS is emphasis; `...`
is a beat. The narrator says few numbers; every other number sits on screen as a stat with a small source tag (study,
year, sample).

```bash
python3 voices.py                                  # free previews → voice-previews/index.html; the human picks
python3 narrate.py v1                              # plan.json → "narrator"; prints the credits it used (ask first)
python3 check_take.py voice/narration-v1.mp3       # transcribes it back and lists every word that differs (~1¢)
$PY pitch.py voice/narration-v1.mp3                # speaking rate + pitch range: a narrow range is a flat read
python3 listen.py voice/narration-v1.mp3           # a listening page with the script beside it
```

Any word that changes the meaning gets reworded and recorded again. The human listens and decides; you can measure
loudness and pitch, but you can't hear taste, so say so.

## Step 4: the picture, voice only (v1)

```bash
python3 voicebed.py --take voice/narration-v1.mp3 --out v1    # the voice + 6 s under the end card, and its word timings
python3 plan.py                                               # plan.json → reel.json: every word spec becomes a time
```

In `plan.json`, each segment is one act (`"acts": [3]`) with a scene, word-pinned `cues` for the scene and `titles`
(`[id, from, to]`). A word spec is `"word"` (its first match in the segment's acts), `"word#2"` (the second),
`"act:word"` (from another act), plus `"+0.3"` / `"-0.2"` to shift, or `"end"`. Titles are `lower` (a line of words) or
`stat` (a big number that counts up, with a source line under it). Scenes go in `scenes.js`: every scene is a pure
function of time, drawn in a 1080×1400 design space, with its cues in `R.scenes.<scene>.cues`.

Then the loop, every time, before the human sees anything:

```bash
node build.mjs --no-render          # the composition, linted
node audit.mjs --shots              # must say "no overlaps"   (python3 crops.py 1,2,3 = close-ups of the hits)
node snap.mjs 12 34.5 61            # stills at those seconds: LOOK at every new scene's key moments
node build.mjs                      # the render, about 4 minutes on a laptop → out/<name>-v1.mp4
python3 qa.py out/<name>-v1.mp4     # contact sheet, first frame, phone safe zone, blacks, a strip per transition
```

**The audit is the check a still frame can't do.** It scrubs the whole timeline and lists every place words and
pictures fight: a shape painting over words, a line through words (thin dashed markers included), words on a
see-through or low-contrast shape, a title sitting on the scene, words running past the edge of their own card, and
two sets of words overlapping. The demo's first cut had 29 of these; still-frame checks showed none of them.
`--from` / `--to` audit one stretch after a fix.

Send v1 with one ask: notes as "time + what".

## Step 5: notes on the picture

Fix in code; run the loop again. A changed line of narration: record only the acts that changed
(`narrate.py v2 --acts 9-10`), check the take, splice it onto the approved one
(`voicebed.py --base voice/narration-v1.mp3 --take voice/narration-v2.mp3 --out v2`), point `plan.json` at the new
files, run `plan.py`, and everything re-times. When a line isn't landing, offer two wordings (tighter vs fuller) with
what each costs in length and money, and recommend one.

## Step 6: the sound pass (v2), once the picture is right

Say the cost and wait for the yes.

```bash
python3 music.py                    # prints the cost and stops; music.json sets the directions
python3 music.py --yes              # 2 directions × 2 takes of ~3 min on kie.ai (Suno): about $0.12, capped in code
python3 sfx.py                      # a 20-sound palette from ElevenLabs: about 220 credits, capped; --yes to buy
$PY mix.py --video out/<name>-v1.mp4 --tag v1     # every music take mixed + an effects-only cut + the mixer page
python3 -m http.server 8000         # then open http://localhost:8000/mixer/
```

Write `cues.py` for this video first: one sound per moment, pinned to the same word cues the scenes use, so a
re-recorded voice re-times the effects too. In the mixer page the human switches music takes live and sets the levels;
its "Tell Claude" line is the answer. Bake it: `mix.py --takes <N> --music_db … --sfx_db …`. The picture is never
re-rendered for sound. The demo's approved mix: music about 20 dB under the voice (`--music_db -16 --duck_db 6`), up
for the logo, faded to the last frame; effects as written in `cues.py` (`--sfx_db 0`).

## Step 7: the other shape

```bash
python3 plan.py --wide              # the same plan at 1920×1080, named <name>-16x9 (plain plan.py goes back to vertical)
node build.mjs --no-render && node audit.mjs && node snap.mjs …   # the loop again
node build.mjs
ffmpeg -i out/<name>-16x9-vN.mp4 -i out/<name>-vN-take<N>.mp4 -map 0:v -map 1:a -c copy out/<name>-16x9-vN-take<N>.mp4
```

Same voice, same times, so the approved sound drops straight on. In widescreen the words live on the left: each scene
sits in the middle of the frame and slides right only while a title is up (`scenes.js` does it). ⚠️ Look at every scene
again anyway: anything that "leaves" a vertical frame can stop in plain sight on a wide one, and no audit sees that.
Multiply every exit distance by `EXIT`. In the demo, a flying card stack and a person walking out both did it.

## Finish

The final file is `out/<name>-vN-take<N>.mp4`. Keep a `NEXT.md` with where it stands, so the next session starts from
the file. Posting it anywhere is the human's call, every time.

## House rules: each one is a round of notes someone already paid for

| Never | Instead |
|---|---|
| A video about the article ("the author argues", "in this piece", "I") | The ideas and their evidence; each act one idea |
| A calm, even read (the demo's first voice put its listener to sleep) | A register with energy; `pitch.py` measures the range; the human's ear decides |
| Several numbers spoken in one act | One spoken number per act; the rest on screen as stats with a source tag |
| Trusting a take because it sounds right | Transcribe it back: the demo's first take said "fell to 12" for "fell twelve percent" |
| A time typed into the plan | Words drive time; re-run `plan.py` after every take (takes of the same text vary ~10% in length) |
| A word spec that matches an earlier word | `"word#2"` or `"act:word"`: a title that "ends" before it starts never leaves the screen (`plan.py` refuses it) |
| Recording the whole take again for one line | Record the acts that changed; splice after the previous act's last word (`voicebed.py` checks the join) |
| A graphic moving over words, words on see-through shapes, a label hanging off its card | `audit.mjs` says "no overlaps" before any render; every tag and chip is solid |
| A bar growing under its number, a mover parking on a label, a stamp on the words | Bars stop beside their numbers; movers dock beside labels; stamps land beside the words |
| Dimming a scene by fading each card | One scrim on top (faded cards go see-through) |
| Two ideas on screen at once | One reading zone at a time: the picture and one line of words |
| A metaphor the viewer has to decode | A literal diagram of the real thing |
| Animating `left` / `top` | Transforms (`x`, `y`, `scale`): layout properties snap to whole pixels and stutter; the lint refuses them |
| `svgOrigin` with `x`/`y` and a scale change on an SVG group | Add `smoothOrigin: false`: GSAP otherwise "compensates" and the demo's 15 people never landed on their circle |
| A GSAP tween and a per-frame tick both writing one element's transform | Move a wrapper, animate the child |
| A dash-draw on a round-capped line; a dash-draw on a dashed shape | Make the gap longer than the line; fade dashed shapes in instead |
| Returning the timeline (or `document.fonts.ready`) from a puppeteer `evaluate` | Wrap it: `{ tl.seek(t); }` (serializing it hangs until the protocol times out) |
| Effects at their raw levels, aligned by the file's start | Normalize each (they vary ~20 dB); align by the attack; one sound per moment; a busy stretch gets fewer, not quieter |
| The voice as delivered (ElevenLabs: about -24.6 LUFS, quiet on a phone) | `mix.py` masters to -16 LUFS with a -2 dB limiter |
| Music that competes with the words: vocals, a lead melody, anything ominous | A steady bed ~20 dB under the voice, ducked under speech, up for the logo |
| A music take shorter than the video | Check the fit; Suno honors `duration: 180`. A take's `audio_url` once served a truncated file (`music.py` falls back to the stream URL) |
| Re-rendering the picture for a sound change | `mix.py` muxes new audio onto the finished video |
| Reading `qa.py`'s "audio drops 15 LU" as broken | Expected: it fires on narration pauses (it was built for music) |
| A number on screen not re-checked on render day | Re-check every number against its source, with the source tag beside it |
| Paid generation without a yes and a number | Every paid script prints the cost and needs `--yes`, stops at a cap, and logs to `ledger.csv` |
| Checking a playing `<video>` with a browser screenshot | It shows black; draw the video to a canvas |

## What the demo cost (all in, about $1)

| What | Where | Cost |
|---|---|---|
| Full narration (~2,800 characters) | ElevenLabs `eleven_v4` | ~170 credits |
| Re-recording two acts | ElevenLabs | 35 credits |
| Take check | OpenAI `gpt-4o-mini-transcribe` | ~1¢ |
| Music: 2 directions × 2 takes of 3 min | kie.ai, Suno V6 | 24 kie credits ($0.12) |
| Sound-effect palette, 20 sounds | ElevenLabs text-to-sound | ~220 credits |
| Render, audit, mix, mixer | your machine | free |

---

Credits: the renderer, the interview method and the render-then-inspect loop come from the
[sizzle-reel](https://github.com/WorthingtonCloud/sizzle-reel) skill (see its credits). Rendering is
[HyperFrames](https://github.com/heygen-com/hyperframes) by HeyGen (Apache-2.0) with [GSAP](https://gsap.com). The voice
and the effects are [ElevenLabs](https://elevenlabs.io); the music is Suno through [kie.ai](https://kie.ai). The rest was
learned over the first explainer's three versions.
