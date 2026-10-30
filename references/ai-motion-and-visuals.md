# AI Visual Storytelling & Motion Graphics Playbook (`ai-motion-and-visuals.md`)

Raw talking-head or single-angle vlog footage quickly feels **static ("đơ") and dry ("khô")** if the edit only trims pauses and slaps plain text subtitles on top. Great human editors (Vox, Johnny Harris, Ali Abdaal, MKBHD, high-retention Reels/Shorts creators) continuously evolve the frame using **purposeful visual metaphors, AI-generated editorial visuals, animated data/concept cards, and subtle optical camera motion** — while strictly obeying `anti-ai-slop.md`.

---

## 1. The Anti-Static Visual Rhythm Rule ("No Bare Talking-Head")

Never leave an unchanged static talking-head shot on screen for long stretches:
- **Vertical `9:16` (`/video-edit` — Reels / TikTok / Shorts):** Maximum **4.0–4.5s** without a visual or camera evolution. Every 5–7s should introduce a fresh visual anchor (AI visual card, behind-speaker wall graphic, B-roll cutaway, animated UI/infographic insert, or 4K punch-in / 2.5D parallax push).
- **Horizontal `16:9` (`/youtube-edit` — YouTube Vlog / Review / Talking-Head):** Maximum **5.5–6.5s** of bare talking-head. Whenever the speaker explains a concept, story, number, comparison, location, or step without matching real B-roll footage, proactively generate **AI B-roll visuals (with Ken Burns motion)** or **animated motion cards (`visual_card`, `stat_card`, `checklist`, `comparison`, `kinetic_quote`)**.

> **Anti-Slop Guardrail (`Max 2 Rule`):** Keep the frame alive through *sequential rhythm*, not clutter. Never stack 4 widgets at once. At any timestamp, pair the speaker/footage with **at most 1 hero graphic or visual card** (+ clean subtitle if enabled), using smooth cubic deceleration (`power3.out`, zero cartoon triple-bounce).

---

## 2. Generating High-Taste AI Images (`image-generator` / Gemini Image)

When real B-roll is missing or the speaker mentions an abstract concept, metaphor, historical/story scene, comparison, or product detail, **proactively generate visuals** into `<project>/assets/ai_visuals/` (run `image-generator` subagents in parallel so image generation adds almost zero wall-clock wait!).

### What to Generate vs. What is Banned

| DO Generate (Human Art-Director Taste) | NEVER Generate (Cheap AI Slop) |
|---|---|
| **Editorial Collage & Warm Illustrations:** Clean Vox/Kinfolk-style editorial illustrations on textured paper, warm charcoal, or muted brand tones | **Fake AI Studio Rooms:** Never permanently replace the speaker's real room background behind their cutout with a fake AI bedroom/office |
| **Cinematic B-Roll Cutaway Photography:** Realistic 35mm-style close-ups (e.g. steaming bowl texture, street lanterns at dusk, hands sketching on desk, minimalist workspace, architecture) with natural lighting and shallow depth of field | **Neon Sci-Fi Cyborg / Glowing Brain Clichés:** Ban purple/cyan matrix grids, glowing holographic brains, floating 3D robots with 7 fingers, or baked-in garbled AI gibberish text |
| **Clean Isometric / Concept Visuals:** Minimalist object renders, clean maps, or visual metaphors **without tiny baked-in text** (let Python / HyperFrames render crisp Vietnamese or English typography on top!) | **Text-Heavy AI Images:** Never ask an image model to render Vietnamese sentences or paragraphs inside the image — generate clean visual art and add typography via `build_graphics.py` or `build.py` |

### Prompting Formula for `image-generator`
Always specify:
1. **Aspect Ratio & Framing:** `16:9 widescreen (1920x1080)` for YouTube B-roll cutaways, `4:3` or `1:1` for floating PiP `visual_card` inserts, `9:16 vertical (1080x1920)` for full-screen Reel B-roll cutaways.
2. **No Text Rule:** Explicitly append *"No text, no watermarks, no UI chrome, no logos"* so typography added by our graphics engine stays 100% sharp and typo-free.
3. **Color Harmony:** Match the video's active look (`warm golden-hour editorial`, `clean minimalist studio slate`, `Kodak Portra 400 natural film tones`, or `cream & butter-yellow editorial`).

---

## 3. How to Composite AI Visuals & Motion in `/video-edit` (`9:16`)

`assets/template/build.py` ships 4 built-in anti-static mechanisms (in addition to behind-head kinetic words and parallel HyperFrames `.webm` sub-agent inserts):

1. **Floating Editorial Visual Cards (`AI_CARDS` / `ai_cards()`, `z-index: 8`):**
   - Places an AI illustration or photo inside a rounded bordered card (`border-radius: 28px`, subtle `-5°..+6°` editorial tilt, deep drop shadow, optional caption pill) beside or below the speaker (`y <= 1470` safe zone).
   - Automatically animates an **inner Ken Burns zoom (`scale 1.0 -> 1.12`)** inside the card window so the image feels alive, never pasted on like a dead sticker.
2. **Behind-Speaker Wall Canvas (`WALL_VISUALS` / `wall_visuals()`, `z-index: 2`):**
   - Sits *between* `#bgv` (base video) and `#cutwrap` (speaker background cutout)!
   - Displays a wide `1000×680` visual card, diagram, or moodboard behind the speaker's shoulders/head (`top: 235px`, `left: 40px`) with subtle drift while `#cut` stays crisp in front — creating true 3-layer studio depth.
3. **Full-Bleed B-Roll Cutaways (`BROLL_CUTAWAYS` / `broll_cutaways()`, `z-index: 5`):**
   - Covers the frame for `1.8s–3.2s` (L-cut while the speaker's voice continues!) using either a real B-roll video or an AI-generated `9:16` visual with **Ken Burns scale + pan motion**, keeping kinetic captions legible on top.
4. **2.5D Optical Parallax Camera Push (`PARALLAX_SHOTS` / `parallax_pushes()`):**
   - On talking-head segments longer than `3.0s`, scales `#bgv` slowly (`1.0 -> 1.025`) while scaling the speaker cutout `#cutwrap` slightly faster (`1.0 -> 1.065`). The differential zoom creates authentic optical camera-slider parallax between the speaker and their room!

### Parallel HyperFrames Motion Sub-Agents (Beyond App UIs)
In Step 5 of `/video-edit`, spawn parallel sub-agents (`references/overlays.md`) not only when an app UI is mentioned, but whenever the script benefits from:
- **Animated Metric / Counter Cards** (`0 -> 10x`, `+85%`, animated bar/line chart)
- **Before vs. After Split Cards** (pain point -> transformation synced to spoken beats)
- **3-Step Animated Flowcharts / Checklists** (SVG connector lines drawing via `strokeDashoffset`)
- **Mixed-Media Collage Inserts** (animating 2–3 AI-generated PNG assets with GSAP parallax + drawn SVG arrows)

---

## 4. How to Composite AI Visuals & Motion in `/youtube-edit` (`16:9`)

`/youtube-edit` includes native motion rendering in `assemble.py`, `build_graphics.py`, and `render.py`:

### A. AI Image B-Roll + Dynamic Camera Motion in `edl.json` (`assemble.py`)
- **AI Images as Full 16:9 B-Roll (`type: "broll"` or inside `broll_inserts`):**
  Pass `"image": "assets/ai_visuals/scene_01.png"` (or an image clip ID from `sources.json`) with `"motion": "push_in" | "pull_out" | "pan_right" | "pan_left" | "drift_up"`. `assemble.py` supersamples the image to 4K (`3840×2160`) and renders silky-smooth 60fps Ken Burns camera motion with zero pixel jitter!
- **Dynamic Camera Motion on Real Video Clips:**
  Add `"motion": "push_in" | "pull_out" | "pan_right" | "pan_left"` (and optional `"motion_amt": 0.06`) to any A-roll or B-roll segment in `edl.json` so long explanations gently push in toward the speaker or pan across a dish/street scene.

### B. Animated RGBA Motion Graphics in `graphics.json` (`build_graphics.py`)
In addition to `intro`, `chapter`, `lower_third`, `callout`, and `subscribe`, use these **6 animated motion & visual overlay types** (rendered as lossless RGBA motion clips so elements truly animate frame-by-frame!):
1. **`visual_card`**: Floating Picture-in-Picture editorial card (`left`, `right`, or `center`) framing an AI-generated image/photo with **live inner Ken Burns zoom (`1.0 -> 1.09`)**, category pill, title, and caption beside the talking host.
2. **`stat_card`**: Hero number/metric card where **numbers smoothly count up from 0** (`0% -> 92%`, `0đ -> 45.000đ`, `0x -> 3.5x`) and an accent progress bar fills with cubic ease-out.
3. **`checklist`**: Step-by-step / key-takeaways card where **items 1, 2, 3, 4 stagger in sequentially** on screen synced to the explanation (never a static wall of text!).
4. **`comparison`**: Two-column **Before vs. After / Pros vs. Cons** split card where Column A lands first and Column B reveals after `split_delay` seconds with an accent highlight.
5. **`kinetic_quote`**: Editorial pull-quote / thesis highlight banner with a live sweeping accent underline bar.
6. **`custom_motion`**: Embeds any custom transparent `.webm` (VP9 alpha) or `.mov` (QuickTime `qtrle` RGBA) motion graphic built by a sub-agent or HyperFrames.
