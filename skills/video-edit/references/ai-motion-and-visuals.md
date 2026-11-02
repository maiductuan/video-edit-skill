# TVC Cinematography, Photorealistic B-Roll & Broadcast Motion Playbook (`ai-motion-and-visuals.md`)

A great video must avoid two opposite traps:
1. **Static & Dry ("Đơ & Khô"):** Leaving a single talking-head camera angle unchanged for 15–30 seconds with only plain subtitles.
2. **Cheap "Overly AI" Look ("Nhìn quá AI / Rẻ tiền"):** Plastic hyper-saturated AI illustrations, uncanny AI hands/faces, chunky SaaS dashboard boxes with loud neon/yellow pill buttons, or mechanical linear zooming.

Every edit produced by `/video-edit` (`9:16`) and `/youtube-edit` (`16:9`) must aim for the visual restraint and physical realism of a **high-end TVC, Netflix Documentary (*Chef's Table*, *Street Food*), Sony Alpha Film, or Apple Keynote**.

---

## 1. TVC Visual Pacing ("Alive, Never Chaotic")

- **Vertical `9:16` (`/video-edit` — Commercial Reels / TikTok / Shorts):** Evolve the frame every **4.0–4.5s** using subtle 4K punch-ins, 2.5D optical slider parallax, optical-matched B-roll cutaways (`1.8s–3.0s`), sleek smoked-glass cinema plates, or clean HyperFrames motion typography.
- **Horizontal `16:9` (`/youtube-edit` — YouTube Documentary Vlog / Review / Talking-Head):** Evolve the frame every **5.5–6.5s**. When real B-roll footage is missing during an explanation, weave **photorealistic optical-matched B-roll plates** (L-cut over continuous speech) or **TVC broadcast motion graphics** (`intro`, `lower_third`, `visual_card`, `stat_card`, `checklist`, `comparison`, `kinetic_quote`).
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
3. **NEVER include text inside generated images** (*"No text, no typography, no watermarks, no logos, no UI"*). Let our 2x-supersampled vector broadcast engine render crisp Vietnamese/English typography on top.
4. **NEVER write `"MINH HỌA AI"`, `"AI VISUAL"`, or `"ẢNH AI"` on any on-screen badge or caption!** A TVC never announces its VFX plates. Always write real story context (e.g., `"HỘI AN · CHIỀU MUỘN"`, `"NGUYÊN LIỆU TRUYỀN THỐNG"`, `"GÓC QUAY CHI TIẾT"`).

### B. Exact TVC Cinematography Prompt Template for `image-generator`
Use this camera-first structure for every generated B-roll plate:
> `"Live-action 35mm commercial film still of [physical object / tabletop detail / architectural atmosphere], shot on ARRI Alexa Mini LF with Cooke Panchro 50mm f/2.0 prime lens. Natural directional window key light with soft negative fill and gentle highlight roll-off, shallow depth of field with authentic optical bokeh, real physical surface micro-texture (natural wood grain / ceramic glaze / linen / subtle atmospheric haze), Kodak Vision3 250D neutral documentary color science, unretouched real-world photography. No people's faces or hands, no CGI gloss, no neon lighting, no text, no watermarks."`

---

## 3. Automatic Optical Plate Matching (Built Into Our Pipeline)

Raw still images look fake in video if they slide linearly with hyper-digital contrast. Our pipeline automatically applies **VFX Optical Plate Matching**:
- **In `/youtube-edit` (`scripts/assemble.py` & `scripts/build_graphics.py`):**
  - **De-Plasticize Color & Contrast:** Automatically tames digital saturation (`saturation=0.93`, `contrast=0.985`) before the master film grade so AI plates match real phone/mirrorless camera dynamic range.
  - **Optical Lens Falloff & 35mm Sensor Micro-Dither:** Adds subtle corner lens falloff (`vignette=PI/9`) and ultra-fine temporal luma sensor micro-dither (`noise=c0s=3:c0f=t`) on full-screen image B-roll so moving frames feel captured by a physical CMOS cinema sensor rather than a sliding PNG.
  - **Sinusoidal Gimbal Inertia (`0.5 - 0.5*cos(PI*t/T)`):** Replaces stiff linear `zoompan` with dampened slider/gimbal acceleration & deceleration at a restrained **4.5%–6.2%** travel.
- **In `/video-edit` (`assets/template/build.py`):**
  - `.optplate`, `.aiframe img`, and `.wallvis img` automatically pass through `contrast(.98) saturate(.91) brightness(.97)` and inherit the reel's active `.g` camera grade + optical vignette on `BROLL_CUTAWAYS`, moving with `ease: 'sine.inOut'` (`1.0 -> 1.062`).

---

## 4. TVC Broadcast Motion Design Grammar

All 10 built-in graphics in `/youtube-edit` (`scripts/build_graphics.py`) render as **30fps lossless RGBA motion clips (`.mov` `qtrle`)** using high-end broadcast craft:
- **Translucent Smoked Obsidian Glass (`alpha ~82%`) + `1px` Specular Hairline Border** (2x supersampled with Lanczos anti-aliasing — zero jagged pixel corners, zero chunky SaaS boxes).
- **Wide-Tracked Swiss Micro-Kickers (`+3.4px` character tracking)** paired with a `5px` precision accent square instead of loud solid-colored pill buttons.
- **Masked Baseline Typography Reveals (`overflow: hidden`, `quintic ease-out` `1 - (1-t)^5`)** where headlines rise cleanly out of an invisible baseline while `1.5px–2.5px` architectural hairline rules draw across.
- **Precision `2.5px` Telemetry Lines (`stat_card`)** with a leading accent dot instead of fat cartoon progress bars.
