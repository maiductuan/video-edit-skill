# Animated Motion Graphics, Data Visuals & UI Inserts (built by parallel sub-agents)

The main session owns the cut, grade, captions, AI visual generation (`image-generator`), and final integration; each rich animated motion insert (micro-infographics, metric counters, step-by-step flowcharts, Before/After comparison cards, mixed-media AI-image collages, app UI recreations, social CTA cards) is delegated to its own sub-agent working in its own folder, in parallel.

## When to Spawn Motion Sub-Agents (Anti-Static Rule)
Do **not** wait for the speaker to mention an app screen! Spawn 2–5 parallel motion sub-agents across a 30–60s reel whenever the speaker discusses:
1. **Numbers, Metrics, ROI, or Growth (`metric-card`):** Animated counter (`0 -> 10x`, `+85%`, `$0 -> $12k`), smooth SVG trend line (`strokeDashoffset`) or filling progress bar.
2. **Processes, Lists, Tips, or Workflows (`flow-steps`):** 2–4 step vertical/horizontal pipeline or staggered checklist where each pill illuminates on its spoken timestamp with animated SVG arrows.
3. **Contrasts & Pain Points (`before-after`):** Two-column or sliding Before vs. After / Manual vs. Automated comparison card.
4. **Visual Metaphors & Collages (`mixed-media`):** Combines 1–3 clean AI-generated images from `<project>/assets/ai_visuals/` with GSAP 2.5D parallax float, drawn SVG circles/underlines (`strokeDashoffset`), and crisp typography pills.
5. **App / Browser / Code / Social CTA (`app-ui`, `ig-follow`):** Realistic software interaction, file scroll, or profile follow & comment CTA.

## Pattern
1. Lock the insert's timing to the speaker's words first (word timings from `transcribe_cut.py` / the clip's words json).
   Convert to the insert's own clock: insert `t=0` at a known source moment, every beat = word time - that moment.
2. Spawn one sub-agent per insert (`invoke_subagent` / Agent tool in background), all in parallel while `cutout.py` runs.
3. Each agent builds a standalone HyperFrames project in `<project>/agents/<name>/` and renders a TRANSPARENT VP9 WebM
   at a fixed size and duration. The main build places it with a wrapper div (position/scale/tilt, either `z-index: 2` behind the speaker cutout or `z-index: 9` under the chin / beside the torso inside `y <= 1470` safe zone) and a timed `<video>`.
4. When an agent reports back, read its notes (things it flags as "might look off" are usually real, e.g. a grid
   thumbnail with an off-brand title). Send fixes back with `send_message` instead of redoing the work.

## Brief template (fill every bracket; the specifics are what make the result good)
`[PY]` and `[skill]` are the `python` and `skill_dir` values from `.platform.json` (full paths, so the sub-agent
runs the same commands on Mac, Linux and Windows).
```
Build ONE short animated motion graphic / UI clip with HyperFrames: [what it shows — e.g. animated 3-step flowchart / metric counter card / Before-vs-After comparison / mixed-media AI visual card / app recreation]. It plays in a 9:16 vertical video while [speaker] says "[line]", so it must look human-crafted, editorial, and readable on a phone (zero AI-slop HUD brackets or cartoon bounce).

Where to work: [project]/agents/[name]/ (touch nothing else). Inputs: [files, including any AI visuals in ../../assets/ai_visuals/]. Copy setup (fonts.css + woff2, hyperframes.json, package.json) from [project]/ ; mirror [skill]/assets/overlay-examples/[closest]/ for structure.

Output: composition [W x H], transparent background outside a [window/card/floating-elements] with ~[R]px rounded corners (corners transparent, inside opaque). Duration [D]s, 30fps. Render renders/[name].webm with --format webm. Verify alpha (ffprobe alpha_mode=1; decode a frame with -c:v libvpx-vp9 and check a corner pixel is transparent).

Look: [palette matching bold/cool_girl/cool_dude, fonts (Be Vietnam Pro / Inter / Instrument Serif / DM Serif Display), concise structured facts <= 10-12 words total; no copied logos; full Vietnamese Unicode diacritics if Vietnamese].
Readable sizes: key text >= 26px at the size it will be shown. Smooth cubic/expo deceleration (power3.out / expo.out), no elastic triple-bounce.

Timeline (seconds, locked to the voice, keep within ±0.05s): [beat list].

HyperFrames rules: run it as `"[PY]" "[skill]/scripts/hf.py" <lint|snapshot|render ...>` from your folder (pinned hyperframes@0.8.34 with Node 22+, same command on Mac, Linux and Windows; in PowerShell put `&` in front), run build.py with "[PY]" and write index.html with encoding='utf-8', root div with data-composition-id/start/duration/width/height, paused GSAP timeline registered in window.__timelines["main"], gsap.set for initial states OUTSIDE the timeline, immediateRender:false on fromTo, no apostrophes in ids, no onUpdate text tricks (for counters or typed text, pre-generate discrete spans/keyframes revealed with tl.set), lint 0 errors, snapshot and LOOK at the PNGs, then render. Never delete files.

Report back: path, exact duration, alpha confirmed, actual beat times (for sound effects), anything that looks off.
```

## Example inserts (`assets/overlay-examples/` has reference `index.html` / `build.py`)
- **claude-desktop** (`1000x720`, `4.35s`): Claude desktop light theme, 5 clip thumbnails dragged into the input with a
  count badge, `/video-edit` typed with a slash-command menu, Claude reply with a "Using skill" pill and a checklist
  ending in a "reel.mp4 · ready" file card. Placed on the wall BEHIND the speaker (`z` between base video and cutout).
- **ig-follow** (`760x1000`, `2.9s`): the creator's IG profile in dark mode (profile pic, verified badge, posts /
  followers / following, bio, post grid from their reels), a touch dot taps Follow at `0.70s` (button -> Following),
  the comment sheet slides up, the CTA keyword is typed and posted at `1.75s`. Scaled `.7` under the chin in the CTA.
  Click sounds at the two taps. Fill it with the user's REAL numbers (handle from `config.json`; pull stats with an
  Instagram profile scraper on Apify if connected, otherwise ask). Example commenters must stay generic placeholders.
- **skill-md** (`860x1000`, `2.15s`): dark code editor showing a `SKILL.md` with markdown highlighting, a smooth eased
  scroll on a wrapper `y`, a line glow as a section passes. Scaled `.72` with a slight `rotateX` tilt under the face.
- **metric-counter / flowchart / before-after** (`880x560` or `920x680`, `2.2–4.0s`): dark charcoal or warm cream glass card (`border-radius: 32px`), accent pill header, discrete GSAP `tl.set` counter ticks (`0% -> 92%`) + SVG progress bar / `strokeDashoffset` connector arrows synced to spoken keywords.

## Creator reels as cards
Instagram: Apify's official Instagram scraper (pay-per-use; currently `apify/instagram-scraper` with `directUrls`
and `resultsType: posts`) returns a `videoUrl` you can curl. Pinterest pins: the pin page HTML contains
`v1.pinimg.com/videos/.../*_720w.mp4`. Transcribe to pick the 2-3s that match the line. Trim to `260x462` tiles,
muted, `-g 30`. Always show the `@handle`.

The creator's own reels (for the orbit, the profile grid): Apify's official Instagram post scraper with the handle
from `config.json`, 6 reels, trim each to `300x534` muted tiles. Without Apify, ask the user to drop 6 of their reels
into the project's `assets/reels/` folder.
