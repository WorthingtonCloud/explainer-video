<p align="center"><a href="media/explainer-widescreen.mp4">Watch the widescreen cut</a></p>

<p align="center">
  2 minutes 56 seconds, sound on. On a phone? Watch the <a href="media/explainer-vertical.mp4">vertical cut</a>.
</p>

# explainer-video

**A skill that lets your AI agent make a narrated explainer video by itself**: the arc, the words, the voice, the
scenes, the sound, and the checks. You bring the source and your notes. You never open a video editor.

The video above was made this way, for [The Lab](https://lab.worthington.cloud), from one of its notes. An agent pulled
the ideas and the evidence out of the note, wrote the narration, recorded the narrator, drew every scene in code, and
started each move on the word it illustrates. It checked every frame for words and pictures fighting, then mixed a faint
music bed and small sound effects under the voice. It took three versions and about $1 in voice, music and effects. The
widescreen cut is the same plan with one flag. This skill is what those versions taught, packaged so your agent starts
where that one finished.

## Install it

Paste this to your agent (Claude Code, or any agent that can run shell commands and has a skills folder):

```text
Install the explainer-video skill from https://github.com/WorthingtonCloud/explainer-video. Clone the repo and
copy its explainer-video/ folder into my skills folder (for Claude Code: ~/.claude/skills/explainer-video).
Then read its SKILL.md, set up a video folder from its kit, run node doctor.mjs, and tell me what's
missing. When everything passes, interview me for my first explainer.
```

Or by hand:

```bash
git clone https://github.com/WorthingtonCloud/explainer-video
cp -R explainer-video/explainer-video ~/.claude/skills/
```

**You need:** Node 22+, Python 3 with numpy, a full build of ffmpeg, and curl. `npm install` in a video folder brings
HyperFrames, GSAP and puppeteer. `doctor.mjs` checks all of it. macOS and Linux run it as is; on Windows, run it under
WSL.
**The paid parts:** an [ElevenLabs](https://elevenlabs.io) key for the voice and the sound effects (library voices need
a paid plan over the API; pay-as-you-go works). Optional: an [OpenAI](https://platform.openai.com) key to transcribe each
take back and catch a changed word (about a cent), and a [kie.ai](https://kie.ai) key for the music (about 12 cents), or
bring your own track. Every paid script prints its cost and waits for a yes. The picture, the audit and the mix are free.

## How it works

1. **The agent interviews you first.** One question at a time, each with its suggested answer, every answer saved to a
   file before the next: the source, who watches, what they should get by the end, the acts, the register, the
   narrator, the look, the budget.
2. **It pitches the arc as acts** before writing a word of narration: one idea per act, the evidence and its source, and
   the picture. It explains the ideas, not the article: the narrator never says "the author".
3. **It writes the narration and records it.** Stage directions steer the read. It transcribes every take back to catch
   a word the voice model changed (the demo's first take said "fell to 12" for "fell twelve percent"), measures whether
   the read is flat, and gives you a listening page. Your ear decides.
4. **The voice keeps the time.** Every word gets a timestamp, and every animation and title is pinned to a word, not to
   a second. Change a line, record just that act again, and the whole video re-times itself.
5. **Every scene is drawn in code**: literal diagrams of the real thing, one accent color, one soft spotlight. Numbers sit
   on screen as stats with their source beside them.
6. **It checks its own frames before you see them.** An audit scrubs the whole timeline for words and pictures
   fighting: a shape over words, a line through a number, words on a see-through card, a label hanging off its box. The
   demo's first cut had 29 of these, and still frames showed none. Then stills, a contact sheet, every transition, the
   black levels.
7. **The sound comes last, without re-rendering.** Two music directions, a small palette of effects pinned to the same
   words, and a mixer page where you switch takes and set the levels live.
8. **The other shape is one flag.** `plan.py --wide` makes the widescreen cut of the same plan. The words move to the
   left, each scene slides aside only while words are up, and the approved sound drops straight on.

## What's in the box

| File | What it does |
|---|---|
| `explainer-video/SKILL.md` | The method: the interview, the steps, the cost gates, and the house rules |
| `kit/narrate.py` | Records the narration on ElevenLabs with a timestamp for every word; `--acts` re-records only what changed |
| `kit/check_take.py` · `pitch.py` · `listen.py` | Transcribes a take back and lists changed words · measures a flat read · a listening page |
| `kit/voices.py` | A free audition page of narrator voices |
| `kit/voicebed.py` | The voice track and its word timings; splices a re-recorded act onto the approved take |
| `kit/plan.py` | `plan.json` → `reel.json`: every word spec becomes a time; `--wide` for the widescreen cut |
| `kit/scenes.js` | The scene helpers, icons, overlap rules and the demo's ten scenes, as a worked example |
| `kit/audit.mjs` | Scrubs the timeline for words and pictures fighting; `crops.py` and `snap.mjs` to look closer |
| `kit/music.py` · `sfx.py` · `cues.py` | The music bed (Suno on kie.ai) · the effects palette (ElevenLabs) · where each effect lands |
| `kit/mix.py` · `mixer/` | Voice + music + effects onto the finished video, and the mixer page for picking the take and levels |
| `kit/build.mjs` · `reel.js` · `qa.py` | The renderer from [sizzle-reel](https://github.com/WorthingtonCloud/sizzle-reel): one HyperFrames composition, rendered and checked |
| `kit/doctor.mjs` | Preflight: says plainly what's missing |

## The rules that cost a round of notes each

The video explains ideas, never the article. One spoken number per act; the rest sit on screen with a source. Every
take is transcribed back before it's trusted. Times come from the words, never typed in. No render until the audit says
"no overlaps": every tag is solid, bars stop beside their numbers, and nothing crosses a label. A dimmed scene gets one
scrim, not faded cards. The music sits about 20 dB under the voice and never competes. The picture is never re-rendered
for sound. In widescreen, anything that leaves a vertical frame has to leave the wide one too. The full list, with the
fix for each, is in [SKILL.md](explainer-video/SKILL.md).

## Credits

The renderer, the interview method and the render-then-inspect loop come from the
[sizzle-reel](https://github.com/WorthingtonCloud/sizzle-reel) skill, which credits Nate Herk and Jay E (RoboNuggets)
for the ideas it builds on. The video renders on [HyperFrames](https://github.com/heygen-com/hyperframes) by HeyGen
(Apache-2.0) and [GSAP](https://gsap.com). The voice and the effects are ElevenLabs; the music is Suno, through kie.ai.

## License

MIT. Use it, change it, ship explainers with it.
