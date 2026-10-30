---
name: video-edit
description: "Turns raw 9:16 talking-head clips into a finished, dynamic Instagram reel / TikTok / Short end to end: picks the cleanest take of every line, cuts dead air, punches in from 4K with 2.5D parallax camera motion, cuts you out of the background for words & visuals behind your head, proactively generates AI editorial visuals & B-roll cutaways + parallel animated motion graphics (UI inserts, counters, flowcharts, comparisons) so talking-head videos never feel static or dry, applies 3 designed looks (bold, cool girl, cool dude), adds subtle sound design, and checks every cut inside the Reels safe zone. Trigger with /video-edit or phrases like 'edit these clips', 'I dropped clips in my downloads', 'cut this into a reel', 'dựng video dọc 9:16', 'make this reel look fire'."
---

# /video-edit

Raw clips in, finished reel out. The user never opens an editor: they review a phone copy and give notes; every
round is a ~2 minute re-render.

Read before building: `references/looks.md` (the three looks, exact values), `references/layout.md` (safe zone,
placement, behind-head formula), `references/ai-motion-and-visuals.md` (**mandatory anti-static playbook: AI-generated visuals, B-roll cutaways, 2.5D parallax & motion graphics**), `references/gotchas.md` (every trap already hit once), `references/anti-ai-slop.md`
(mandatory human-grade editorial rules — zero AI slop), and `references/pacing-and-cuts.md` (shot durations & J/L cut
rules). Read `references/overlays.md` for parallel animated UI & motion-graphic sub-agents.

> **Multi-Platform Suite Router:** This repository ships a 5-skill suite (`python3 "SK/install_all.py"` installs all 5):
> - `/video-edit` (this skill): 9:16 Talking-Head Reels / TikTok / Shorts with subject cutout, kinetic typography behind head, AI visual cards & motion inserts
> - `/youtube-edit` (`skills/youtube-edit`): 16:9 YouTube Vlog, Food & Travel Review, and Studio Talking-Head with A/B-roll J/L cuts, AI B-roll Ken Burns & animated RGBA motion graphics
> - `/commercial-promo` (`skills/commercial-promo`): Multi-ratio (`9:16`, `4:5`, `1:1`, `16:9`) Product Ad & Promo with beat-sync & price badge
> - `/podcast-interview` (`skills/podcast-interview`): `16:9` / `9:16` Dual-Speaker Split-Screen Podcast & Audiograms
> - `/video-director` (`skills/video-director`): Master Router, 6-Gate QA Audit (`G0–G4` + EBU R128 `-14 LUFS`), Beat-Sync, and Smart Reframe

Works on macOS, Linux and Windows. setup.py detects the machine at the start of every run and every command below
comes from that record, so never guess paths or shells: see "This machine" right after Step 0.

## Step 0: First-time setup (runs once)

`SK` is this skill's folder (the one holding this SKILL.md), as a full path. Usually `~/.claude/skills/video-edit` or `~/.gemini/config/skills/video-edit`;
on Windows that is `C:/Users/<name>/.claude/skills/video-edit` or `C:/Users/<name>/.gemini/config/skills/video-edit`.

Look for `SK/config.json`.

**If it exists:** load it (name, instagram handle, default look, folders), run the setup script exactly as in
step 3 below (a few seconds: it only checks, and repairs the environment after an update), read "This machine",
and go to Step 1 once it prints READY.

**If it does not exist:**
1. Say: "Welcome to /video-edit! Let's get you set up. This takes about 2 minutes and only happens once."
2. Ask, in one message:
   - Your name (used on your Instagram profile insert)
   - Your Instagram handle (for your profile insert and to pull your reels for the orbit effect)
   - Default look: **bold** (kinetic words behind your head), **cool girl** (warm, yellow serif italic, your reels
     orbiting you) or **cool dude** (dark editorial, tracked caps + serif). Offer bold if they are unsure.
   - Where your raw clips usually land (default `~/Downloads`) and where projects should live (default `~/reel-edits`)
3. Run the setup script with whichever Python the machine has. Try these in order until one prints STATUS lines:
   `python3 "SK/scripts/setup.py"`, then `python "SK/scripts/setup.py"`, then `py -3 "SK/scripts/setup.py"`.
   (On Windows `python3` is often a Microsoft Store stub that prints "Python was not found": just try the next one.)
   None of them runs: Python is missing. Give the fix for their system and stop (Windows:
   `winget install --id Python.Python.3.12 -e`, Mac: `brew install python`, Linux: `sudo apt install python3 python3-venv`).
   Then read the STATUS lines:
   - ffmpeg / node / python venv MISSING: the line ends with the exact fix for THIS machine (winget on Windows,
     brew on Mac, apt on Linux). Give it to the user and stop until the script prints READY.
   - Windows: the user pastes the winget lines into their own PowerShell window (winget asks them to agree to its
     terms the first time), then quits Claude Code / Antigravity completely and reopens it, or the new programs are not found.
   - The script downloads the 6 sound effects itself. If it still reports them MISSING (offline), that is optional:
     the reel just has no SFX until they are added.
4. Optional, Apify (pulls reels and profile stats automatically): try a simple Apify MCP call. If it is not
   connected, say it is optional and how to add it:
   1. Create a free account at https://apify.com and copy the API token from Settings > API & Integrations.
   2. In a terminal, paste this one line with the token in place of YOUR_TOKEN:
      `claude mcp add apify -e APIFY_TOKEN=YOUR_TOKEN -- npx -y @apify/actors-mcp-server`
      (heads up: Claude Code stores the token in plain text in `~/.claude.json`; keep that file private).
   3. Reopen Claude and run /video-edit again.
   Without Apify, the skill asks them to drop their reel files into the project instead.
5. Save `SK/config.json` (no secrets, ever):
   ```json
   {"name": "...", "instagram": "handle-without-@", "defaultLook": "bold", "clipsDir": "~/Downloads",
    "projectsDir": "~/reel-edits", "setupComplete": true, "setupDate": "YYYY-MM-DD"}
   ```
6. Say: "Setup complete! Running /video-edit now..." and continue.

## This machine (read on every run)

Read `SK/.platform.json`, written by setup.py. It records the OS (`os`: macos, linux or windows), the CPU and the
exact commands for this computer:
- `PY` = its `python` value: the skill's own Python (`.venv/bin/python` on Mac and Linux,
  `.venv/Scripts/python.exe` on Windows). Run EVERY Python script of this skill with it, never a bare `python3`.
- `HF` = `PY "SK/scripts/hf.py"`: starts the pinned HyperFrames (`npx --yes hyperframes@0.8.34 ...`) with the
  right Node on any OS. No `nvm use`, no `npx.cmd` trouble.
- `cutout`: `CoreML` (Apple Silicon) or `CPU` (Windows, Linux, Intel Macs: no GPU help, so the cutout step is the
  slow one; say so, run it in the background and keep building).

setup.py rewrites this file on every run (Step 0), so it is always current. File missing, or `PY` no longer
exists: setup did not run or did not reach READY; run it as in Step 0.3 and follow its fix.

One command style that works in zsh, bash, Git Bash and PowerShell:
- Full paths in double quotes with forward slashes (fine on Windows too): `"PY" "SK/scripts/ingest.py" "<project>"`.
- In PowerShell (Windows without Git for Windows, or whenever the PowerShell tool is the one you have) put `&` in
  front: `& "PY" "SK/scripts/ingest.py" "<project>"`.
- One command per call. No `&&`, no `VAR=1 command`, no `~` inside arguments, no `source`, no `zsh`.
- `ffmpeg` and `ffprobe` are on PATH on every OS (setup checks it), so one-off ffmpeg commands are the same everywhere.

## Hard rules
1. Everything inside the Reels safe zone: top 220, bottom 450 (nothing below y 1470), sides 35, right 100 from y 1155.
2. Never cover the face with text or cards. Behind-head words show at least ~70% of each letter.
3. Captions say what was actually said: fix Whisper's mishearings of names and keywords ("Claude" often comes out
   as "cloud"/"claws", "skill" as "scale"). No em dashes in on-screen text.
4. **Anti-Static / Anti-Dry Visual Rhythm:** Never leave an unchanged talking-head frame with only plain text for more than `4.0–4.5s`. Evolve the frame every 4–6s using 4K punch-ins, 2.5D parallax camera pushes, AI-generated editorial visual cards (`AI_CARDS` / `WALL_VISUALS`), short B-roll cutaways (`BROLL_CUTAWAYS`), or parallel HyperFrames motion graphics (`agents/`).
5. Sound effects subtle (template `SFX_GAIN = 0.75` of the base volumes), never louder than the voice.
6. Credit other creators on screen (@handle) whenever their reels appear. Real numbers on the user's own profile;
   anything else (commenters, chat history) is a generic placeholder, never a real person, never fabricated proof.
7. Prove cuts from the final render, not from snapshots.
8. Never delete the user's files. Originals are read, never modified.

## Workflow

### 1. Intake
- Clips: the files the user names, else the newest video files in `clipsDir`. Create `<projectsDir>/<short-slug>/`.
  (`~` in config.json is the user's home folder, `C:/Users/<name>` on Windows. The skill's scripts expand it.)
- Reference links (IG reels, Pinterest pins) for a style: download them and look at frames before designing anything
  (see overlays.md for how to fetch them).

### 2. Ingest
```bash
PY SK/scripts/ingest.py <project> <clips or folder> [--newest 5]
```
Look at `work/sheets.jpg` (setups and angles) and read `transcript.txt` (per-clip lines, words with times, speech map).

### 3. Pick takes -> `<project>/edl.json`
- Rebuild the script from the takes: people repeat a line until it lands. Use the LAST complete clean take unless
  the user says otherwise ("the better section starts at 0:47" means one continuous take from there).
- In/out points from the speech map: start ~0.05-0.07s before the first word, end at the silence start after the
  last word. Kill dead air between sections; confirm short pauses with silencedetect before trimming (Whisper can
  invent a leading word at a cut).
- Two segments in a row from the same angle: punch one in (zoom 1.3-1.9 from the 4K original, cx/cy on the chest).
- Unsure words (keyword, CTA trigger): re-transcribe that snippet with medium.en and a prompt containing the names.
- Format: `[{"id": "hook", "clip": "c1", "in": 12.66, "out": 15.72, "zoom": 1.0, "cx": 0.5, "cy": 0.5, "line": "..."}]`
- Post the EDL + planned **Visual Beat Map** (which beats get AI visual cards, wall visuals, B-roll cutaways, or motion inserts) to the user as a short table and keep going; do not wait.

### 4. Assemble, transcribe, cut out
```bash
PY SK/scripts/assemble.py <project>                 # aroll.mp4 clean 30fps CFR + segments.json with exact frames
PY SK/scripts/transcribe_cut.py <project> "<names and keywords in the script>"
PY SK/scripts/cutout.py <project>                   # run in background; asserts cutout frames == aroll frames
PY SK/scripts/headpos.py <project>                  # after the cutout: head/body position per segment
```
One cutout at a time (about 1.5 GB of RAM). It prints a progress line every 30 seconds.

### 5. AI Visuals & Motion Graphics in Parallel (Anti-Static Rule — as soon as the EDL is locked)
**Never let a talking-head shot sit bare for more than `4.0–4.5s` with only subtitles** — that makes the reel feel stiff ("đơ") and dry ("khô"). Right after locking `edl.json`, follow `references/ai-motion-and-visuals.md` (and `references/anti-ai-slop.md` Max-2 rule) and launch visual/motion tasks in parallel while `cutout.py` runs:

1. **Proactive Photorealistic TVC Plates (`image-generator` subagent -> `<project>/assets/ai_visuals/`):**
   - Scan the script for concrete nouns, objects, atmospheres, products, locations, or outcomes that lack real B-roll footage.
   - Spawn `image-generator` subagents in parallel using **live-action 35mm TVC cinematography prompts** (*ARRI Alexa / Sony FX3, 50mm f/2.0 prime lens, directional window key light + negative fill, natural surface micro-texture, Kodak Vision3 neutral color science*). **Default to photorealistic tabletop/macro/architectural cutaways** — NEVER close-up AI faces/hands, NEVER cartoon/neon AI art, NEVER text inside images, and NEVER label cards `"AI VISUAL"` or `"MINH HỌA AI"`.
   - Composite them in `build.py` using the template's optical-matched TVC helpers (`0°` clean architectural alignment by default, `1.5px` specular glass bezel, `sine.inOut` restrained slider drift):
     - `AI_CARDS` (`ai_cards()`): Smoked-glass cinema PiP plate (`z-index: 8`, `rot=0` default) beside/below the speaker (`y <= 1470`) with restrained `1.0 -> 1.065` gimbal drift + tracked uppercase kicker.
     - `WALL_VISUALS` (`wall_visuals()`): Wide cinema plate placed on the wall **behind the speaker cutout** (`z-index: 2`) for 3-layer studio depth.
     - `BROLL_CUTAWAYS` (`broll_cutaways()`): Full-bleed `1.8s–3.2s` 9:16 B-roll cutaway (`z-index: 5`, automatically inherits the reel's `.g` camera color grade!) with eased slider drift over continuous speech.
2. **Parallel HyperFrames Motion Sub-Agents (`references/overlays.md` -> `<project>/agents/<name>/`):**
   - Do not wait for the script to literally name a software UI! Spawn parallel sub-agents to render transparent VP9 `.webm` motion inserts whenever the speaker mentions:
     - **Metrics / Numbers / Growth:** Animated counter card (`0 -> 10x`, `+85%`), filling bar/line chart.
     - **Steps / Lists / Frameworks:** 3-step animated flowchart or staggered checklist with drawn SVG connectors (`strokeDashoffset`).
     - **Comparisons:** Before vs. After / Old Way vs. New Way split motion card.
     - **App UI / Social CTA / Mixed-Media Collage:** Realistic app window, IG profile follow CTA, or GSAP parallax collage combining AI-generated PNGs from `assets/ai_visuals/`.
3. **2.5D Optical Parallax & Camera Motion (`PARALLAX_SHOTS` in `build.py`):**
   - On talking-head segments longer than `3.0s`, apply differential 2.5D parallax (`#bgv` `1.0 -> 1.025` vs `#cutwrap` `1.0 -> 1.065`) or 4K punch-ins so the camera never feels frozen on a dead tripod.

### 6. Build
Copy `SK/assets/template/` into the project (build.py, hyperframes.json, package.json, assets/fonts, assets/sfx),
then adapt build.py. It is the finished build of a real reel: keep the machinery (`dude_words`, `cards`, `ai_cards`, `wall_visuals`, `broll_cutaways`, `parallax_pushes`, `girl`, `orbit`, `core`, `grades`, `audio`), rewrite the content (its
docstring lists which is which).
- Which look where: `defaultLook` for the whole reel; a line that names a look switches its section.
- Orbit and profile grid use the user's own reels (overlays.md: Apify post scraper with their handle, or files they
  drop into `assets/reels/`).
- Iterate from the project folder: `HF lint` (0 errors), then `PY build.py --safe`, then
  `HF snapshot --at <10-20 moments> --no-end --describe false`. Read the contact sheets, fix layout, readability
  and safe zone. (`HF` picks the right Node by itself, so there is no `nvm use`.)
  A build.py copied from an older version of this skill ignores `--safe`: if the red guide is missing from the
  snapshots, build that project the old way, `SAFE=1 "PY" build.py` (such projects only exist on Mac and Linux).

### 7. Render and QA
```bash
PY build.py           # without --safe
HF render -o renders/<slug>-vN.mp4 --quality high      # ~1.5-2 min for a 25s reel on Apple Silicon
PY SK/scripts/check_cuts.py <project> renders/<slug>-vN.mp4 --phone
```
Look at `work/cut_check.jpg`: every after-cut frame shows the new shot cleanly. Check audio peaks (`volumedetect`,
max around -2 to -5 dB) and the silence at section joins.

### 8. Deliver
Send or point to the phone copy (720p) and the full-quality render. Report in plain terms what changed and anything
that needs the user's call. Keep every version in `renders/`; back up `assets/` + `segments.json` to `work/vN/` before
re-assembling.

## Defaults that came out of real feedback (do not re-litigate)
- Change the grade and captions to create a look; never permanently replace the speaker's real room background with a fake AI-generated room. Instead, keep the real room and layer **framed AI visual cards (`AI_CARDS`), behind-speaker wall visuals (`WALL_VISUALS`), short 1.8–3.2s B-roll cutaways (`BROLL_CUTAWAYS`), and animated motion inserts** so the video stays dynamic and visually rich.
- No film grain. Dark is fine, but keep the subject lit and skin from going red.
- Lead-in captions centred in front of the speaker read better than lines pinned to the left edge.
- Words behind the head are the signature move, but only when readable.
- Never deliver a "talking-head + plain subtitles only" edit: every 4–5 seconds needs an intentional visual or camera beat.

---
Built by [@maiductuan](https://instagram.com/maiductuan). Follow for daily AI automation builds, real systems, not theory.
