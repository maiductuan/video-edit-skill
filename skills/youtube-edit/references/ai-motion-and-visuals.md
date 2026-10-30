# TVC Cinematography, Photorealistic B-Roll & Broadcast Motion Playbook (`ai-motion-and-visuals.md`)

A great video must avoid two opposite traps:
1. **Static & Dry ("Đơ & Khô"):** Leaving a single talking-head camera angle unchanged for 15–30 seconds with only plain subtitles.
2. **Cheap "Overly AI" Look ("Nhìn quá AI / Rẻ tiền"):** Plastic hyper-saturated AI illustrations, uncanny AI hands/faces, chunky SaaS dashboard boxes with loud neon/yellow pill buttons, or mechanical linear zooming.

Every edit produced by `/youtube-edit` (`16:9`) and `/video-edit` (`9:16`) must aim for the visual restraint and physical realism of a **high-end TVC, Netflix Documentary (*Chef's Table*, *Street Food*), Sony Alpha Film, or Apple Keynote**.

---

## 1. TVC Visual Pacing ("Alive, Never Chaotic")

- **Horizontal `16:9` (`/youtube-edit` — YouTube Documentary Vlog / Review / Talking-Head):** Evolve the frame every **5.5–6.5s**. When real B-roll footage is missing during an explanation, weave **photorealistic optical-matched B-roll plates** (L-cut over continuous speech) or **TVC broadcast motion graphics** (`intro`, `lower_third`, `visual_card`, `stat_card`, `checklist`, `comparison`, `kinetic_quote`).
- **Vertical `9:16` (`/video-edit` — Commercial Reels / TikTok / Shorts):** Evolve the frame every **4.0–4.5s**.
- **Restraint (`Max 2 Rule`):** Never stack multiple cards at once. One clean broadcast plate + natural footage at a time.

---

## 2. Generating Photorealistic TVC Plates That Do NOT Look Like AI (`image-generator`)

When real B-roll is missing, **default to Live-Action Cinema Photography**, NEVER cartoonish digital art, 3D renders, or glowing sci-fi clichés.

### A. Mandatory Subject Rules (Zero Uncanny Valley)
1. **NEVER generate close-up AI human faces, eyes, or hands/fingers holding utensils, phones, or products** — human anatomy is the #1 instant giveaway of AI.
2. **Shoot TVC Tabletop, Macro, Object & Atmospheric Cutaways instead:**
   - **Culinary / Food Review:** Macro close-up of simmering broth, ceramic bowl texture on dark aged wood, steam catching warm directional morning window light, fresh herbs with water droplets, moody empty lantern-lit alley at blue hour with shallow foreground bokeh.
   - **Tech / Business / Studio Essay:** Minimalist overhead or 45-degree shot of brushed aluminum hardware, archival paper notebook on dark walnut/linen desk with natural window blinds shadow (gobo), architectural glass interior with shallow depth of field, warm desk lamp practical light.
   - **Travel / Lifestyle:** Wide atmospheric establishing shot with foreground out-of-focus foliage/archway, rain reflections on cobblestone, vintage signage texture, sunlight filtering through café window.
3. **NEVER include text inside generated images** (*"No text, no typography, no watermarks, no logos, no UI"*). Let `build_graphics.py` render crisp 2x-supersampled vector Vietnamese/English typography on top.
4. **NEVER write `"MINH HỌA AI"`, `"AI VISUAL"`, or `"ẢNH AI"` on any on-screen badge or caption!** A TVC never announces its VFX plates. Always write real story context (e.g., `"HỘI AN · CHIỀU MUỘN"`, `"NGUYÊN LIỆU TRUYỀN THỐNG"`, `"GÓC QUAY CHI TIẾT"`).

### B. Exact TVC Cinematography Prompt Template for `image-generator`
Use this camera-first structure for every generated B-roll plate:
> `"Live-action 35mm commercial film still of [physical object / tabletop detail / architectural atmosphere], shot on ARRI Alexa Mini LF with Cooke Panchro 50mm f/2.0 prime lens. Natural directional window key light with soft negative fill and gentle highlight roll-off, shallow depth of field with authentic optical bokeh, real physical surface micro-texture (natural wood grain / ceramic glaze / linen / subtle atmospheric haze), Kodak Vision3 250D neutral documentary color science, unretouched real-world photography. No people's faces or hands, no CGI gloss, no neon lighting, no text, no watermarks."`

---

## 3. Automatic Optical Plate Matching & TVC Broadcast Motion Grammar

- **Optical Plate Matching (`scripts/assemble.py` & `scripts/build_graphics.py`):**
  - Tames digital saturation & harsh contrast (`saturation=0.93`, `contrast=0.985`), adds natural optical lens falloff (`vignette=PI/9`) and ultra-fine temporal luma sensor micro-dither (`noise=c0s=3:c0f=t`), and moves with **sinusoidal gimbal inertia (`0.5 - 0.5*cos(PI*t/T)`)** at a restrained **4.5%–6.2%** physical slider travel.
- **TVC Broadcast Motion Graphics (`scripts/build_graphics.py`):**
  - **2x-Supersampled Smoked Obsidian Glass (`alpha ~82%`) + `1px` Specular Hairline Border** (zero jagged corners, zero chunky SaaS boxes).
  - **Wide-Tracked Swiss Micro-Kickers (`+3.4px` character tracking)** instead of loud solid-filled pill buttons.
  - **Frameless Cinema Intro Lockups** with feathered optical scrims & expanding center gold hairlines.
  - **Masked Baseline Typography Reveals (`quintic ease-out` `1 - (1-t)^5`)** & `2.5px` precision telemetry tracks (`stat_card`).
