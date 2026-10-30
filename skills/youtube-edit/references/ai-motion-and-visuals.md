# AI Visual Storytelling & Motion Graphics Playbook (`ai-motion-and-visuals.md`)

Raw talking-head or single-angle vlog footage quickly feels **static ("đơ") and dry ("khô")** if the edit only trims pauses and slaps plain text subtitles on top. Great human editors (Vox, Johnny Harris, Ali Abdaal, MKBHD, high-retention Reels/Shorts creators) continuously evolve the frame using **purposeful visual metaphors, AI-generated editorial visuals, animated data/concept cards, and subtle optical camera motion** — while strictly obeying `anti-ai-slop.md`.

---

## 1. The Anti-Static Visual Rhythm Rule ("No Bare Talking-Head")

Never leave an unchanged static talking-head shot on screen for long stretches:
- **Horizontal `16:9` (`/youtube-edit` — YouTube Vlog / Review / Talking-Head):** Maximum **5.5–6.5s** of bare talking-head. Whenever the speaker explains a concept, story, number, comparison, location, or step without matching real B-roll footage, proactively generate **AI B-roll visuals (with Ken Burns motion)** or **animated motion cards (`visual_card`, `stat_card`, `checklist`, `comparison`, `kinetic_quote`)**.
- **Vertical `9:16` (`/video-edit` — Reels / TikTok / Shorts):** Maximum **4.0–4.5s** without a visual or camera evolution.

> **Anti-Slop Guardrail (`Max 2 Rule`):** Keep the frame alive through *sequential rhythm*, not clutter. Never stack 4 widgets at once. At any timestamp, pair the speaker/footage with **at most 1 hero graphic or visual card** (+ clean subtitle if enabled), using smooth cubic deceleration (`power3.out`, zero cartoon triple-bounce).

---

## 2. Generating High-Taste AI Images (`image-generator` / Gemini Image)

When real B-roll is missing or the speaker mentions an abstract concept, metaphor, historical/story scene, comparison, map, or product detail, **proactively generate visuals** into `<project_dir>/assets/ai_visuals/` (run `image-generator` subagents in parallel so image generation adds almost zero wall-clock wait!).

### What to Generate vs. What is Banned

| DO Generate (Human Art-Director Taste) | NEVER Generate (Cheap AI Slop) |
|---|---|
| **Editorial Collage & Warm Illustrations:** Clean Vox/Kinfolk-style editorial illustrations on textured paper, warm charcoal, or muted brand tones | **Fake AI Studio Rooms:** Never replace the speaker's real room background with a fake AI bedroom/office |
| **Cinematic B-Roll Cutaway Photography:** Realistic 35mm-style close-ups (e.g. steaming bowl texture, street lanterns at dusk, hands sketching on desk, minimalist workspace, architecture) with natural lighting and shallow depth of field | **Neon Sci-Fi Cyborg / Glowing Brain Clichés:** Ban purple/cyan matrix grids, glowing holographic brains, floating 3D robots, or garbled AI text |
| **Clean Isometric / Concept Visuals:** Minimalist object renders, clean maps, or visual metaphors **without tiny baked-in text** (let `build_graphics.py` render crisp Vietnamese or English typography on top!) | **Text-Heavy AI Images:** Never ask an image model to render Vietnamese sentences inside the image — generate clean visual art and add typography via `build_graphics.py` |

### Prompting Formula for `image-generator`
1. **Aspect Ratio & Framing:** `16:9 widescreen (1920x1080)` for full-bleed YouTube B-roll cutaways; `4:3` or `16:10` for floating PiP `visual_card` inserts.
2. **No Text Rule:** Explicitly append *"No text, no watermarks, no UI chrome, no logos"*.
3. **Color Harmony:** Match the video's active look (`vibrant_vlog`, `warm_food`, `cinema_travel`, `clean_studio`, `film_kodak`, or `minimal_editorial`).

---

## 3. Native Motion & AI Visual Tools in `/youtube-edit`

### A. AI Image B-Roll + Dynamic Camera Motion in `edl.json` (`assemble.py`)
- **AI Images as Full 16:9 B-Roll (`type: "broll"` or inside `broll_inserts`):**
  Pass `"image": "assets/ai_visuals/scene_01.png"` (or an image clip ID from `sources.json`) with `"motion": "push_in" | "pull_out" | "pan_right" | "pan_left" | "drift_up"`. `assemble.py` supersamples the image to 4K (`3840×2160`) and renders silky-smooth 60fps Ken Burns camera motion with zero pixel jitter!
- **Dynamic Camera Motion on Real Video Clips:**
  Add `"motion": "push_in" | "pull_out" | "pan_right" | "pan_left"` (and optional `"motion_amt": 0.06`) to any A-roll or B-roll segment in `edl.json` so long explanations gently push in toward the speaker or pan across a dish/street scene.

### B. Animated RGBA Motion Graphics in `graphics.json` (`build_graphics.py`)
In addition to `intro`, `chapter`, `lower_third`, `callout`, and `subscribe`, use these **6 animated motion & visual overlay types**:
1. **`visual_card`**: Floating Picture-in-Picture editorial card (`right`, `left`, or `center`) framing an AI-generated image/photo with **live inner Ken Burns zoom (`1.0 -> 1.09`)**, category pill, title, and caption beside the talking host.
2. **`stat_card`**: Hero number/metric card where **numbers smoothly count up from 0** (`0% -> 92%`, `0đ -> 45.000đ`, `0x -> 3.5x`) and an accent progress bar fills with cubic ease-out.
3. **`checklist`**: Step-by-step / key-takeaways card where **items 1, 2, 3, 4 stagger in sequentially** synced to the host's explanation.
4. **`comparison`**: Two-column **Before vs. After / Pros vs. Cons** split card where Column A lands first and Column B reveals after `split_delay` seconds with an accent highlight.
5. **`kinetic_quote`**: Editorial pull-quote / key-thesis banner with a live sweeping accent underline bar.
6. **`custom_motion`**: Embeds any custom transparent `.webm` (VP9 alpha) or `.mov` (QuickTime `qtrle` RGBA) motion graphic built by a sub-agent or HyperFrames.
