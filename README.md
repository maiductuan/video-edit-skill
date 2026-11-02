# Multi-Platform AI Video Edit Skill Suite
### By [@maiductuan](https://github.com/maiductuan) — Human-Grade Video Editing for Claude Code & Antigravity

A complete **5-skill video production suite** that turns raw camera or phone footage into finished, broadcast-grade edits across **YouTube (16:9)**, **Instagram Reels / TikTok / Shorts (9:16)**, **Meta & TikTok Commercial Ads (9:16 / 4:5 / 1:1 / 16:9)**, and **Video Podcasts (16:9 / 9:16)** — engineered with **Modern Creator / Storyboard Motion Graphics (`modern_mint` & `anthropic_coral`), Dot-Grid Surfaces, Zero-Emoji Policy, Proactive AI Visual Storytelling, and strict Anti-AI-Slop editorial standards** so videos never feel static ("đơ") or dry ("khô").

---

## The 5-Skill Suite Architecture

All 5 skills are available inside `skills/` (and `video-edit` is also mirrored at the repository root for direct single-skill clones):

| Skill | Folder | Trigger | Aspect Ratios | Genre & Core Capabilities |
|---|---|---|---|---|
| **`video-edit`** | `skills/video-edit` *(+ Root)* | `/video-edit` | `9:16` | **Reels / TikTok / Shorts (TVC & Editorial Grade):** Picks cleanest take across repeats, removes dead air, 4K punch-in + **2.5D optical slider parallax**, CoreML/CPU cutout for words & wall plates behind your head, **photorealistic 35mm optical-matched B-roll cutaways (`BROLL_CUTAWAYS`), smoked-glass cinema PiP plates (`AI_CARDS`), behind-speaker wall canvases (`WALL_VISUALS`)**, parallel HyperFrames motion graphics, and 3 signature looks (`bold`, `cool_girl`, `cool_dude`). |
| **`youtube-edit`** | `skills/youtube-edit` | `/youtube-edit` | `16:9` + `9:16` Shorts | **YouTube Vlog, Documentary Review & Studio Talking-Head:** Auto-classifies `A-ROLL`, `B-ROLL`, and `IMAGE-BROLL`, weaves J/L cuts, **Modern Creator / Storyboard Graphics (`modern_mint` `#4ADE80` & `anthropic_coral` `#E87B55`) with Dot-Grid backgrounds, Bold Condensed Display typography + glowing underline bars, circular number badges `(1)(2)(3)`, neon-glow callout frames, mini 2-bar charts, and automatic 11-Frame Static Storyboard (`work/storyboard_11frames.jpg`)**, `Be Vietnam Pro` subtitles, and `-14 LUFS` mastering. |
| **`commercial-promo`** | `skills/commercial-promo` | `/commercial-promo` | `9:16`, `4:5`, `1:1`, `16:9` | **Product Commercials & UGC Ads:** 4 conversion frameworks (`PAS`, `AIDA`, `Before-After-Bridge`, `Flash Showcase`), 0–2s Hook Lock, dot-grid glowing feature pills, price/discount tags, end-card CTA, and EBU R128 loudness normalization. |
| **`podcast-interview`** | `skills/podcast-interview` | `/podcast-interview` | `16:9`, `9:16` | **Dual-Speaker Podcast & Interview Clips:** Side-by-side (`16:9`) or top-bottom (`9:16`) split-screen composer with rounded studio frames, active-speaker highlight border, dot-grid speaker name/role badges, quote banners, and audiogram waveform bar. |
| **`video-director`** | `skills/video-director` | `/video-director` | All (`16:9`, `9:16`, `4:5`, `1:1`) | **Master Router & QA Director:** Routes any video brief to the right skill, runs **6-Gate QA (`G0–G4`)** (`audit_video.py`), cuts montages locked to music RMS beats (`beat_sync.py`), and reframes exports across platforms (`reframe.py`). |

---

## Modern Creator Graphics & Anti-AI-Slop Philosophy (`references/ai-motion-and-visuals.md` & `references/anti-ai-slop.md`)

Every skill in this suite enforces **human-grade editorial standards**:

1. **Zero-Emoji Policy:** Strictly zero Unicode emojis across all video overlays, subtitles, badges, and templates. Visual hierarchy uses vector geometry (circular number badges `(1)(2)(3)`, geometric brand spark icons, glowing underline bars, and dot-grid textures).
2. **Modern Creator / Storyboard Aesthetic (`modern_mint` & `anthropic_coral`):**
   - **Dot-Grid Background (`dot background`):** Subtle matrix of glowing dots inside graphic cards and storyboard plates so dark surfaces never feel empty.
   - **Two-Tier Display Lockup:** Conversational lead-in kicker above a **Bold Condensed Uppercase Display Headline** paired with a **thick `5px` glowing underline bar**.
   - **Circular Numbered Step Pills (`(1)`, `(2)`, `(3)`):** Stacked rounded cards with `2px` glowing borders for step-by-step lists.
   - **Glowing Neon-Border Callout Frame & Mini 2-Bar Chart:** Crisp `2px` solid accent stroke + outer Gaussian neon glow with clean `•` bullet points and 2-bar vertical comparison charts.
   - **11-Frame Static Storyboard (`work/storyboard_11frames.jpg`):** Automatically generated before rendering so you can review all 11 static graphic frames at a glance.
3. **Anti-Static Visual Beat Rhythm:** Never leave an unchanged bare talking-head frame for more than `4.0–4.5s` (`9:16`) or `5.5–6.5s` (`16:9`). Proactively enrich missing B-roll with high-taste text-free AI visuals (`image-generator`), 60fps Ken Burns / 2.5D parallax camera drift, and animated data/concept motion cards.
4. **No Canned Transitions:** Zero `xfade` dissolves, wipes, pixelates, or zoom-spins between normal cuts. 95%+ of cuts are clean hard cuts or J/L cuts (`0.2s–0.5s` audio lead).
5. **Importance Budget (`Max 2 Rule`):** At any timestamp, a frame contains at most **2 simultaneous visual elements**.
6. **Broadcast Loudness (`-14 LUFS`):** Two-channel EBU R128 loudness normalization (`I=-14 LUFS`, `TP <= -1.0 dBTP`) with dynamic speech-aware BGM ducking.

---

## Quick Install (All 5 Skills)

### Option A: One-Line Terminal Install (Claude Code & Antigravity)

```bash
git clone https://github.com/maiductuan/video-edit-skill "$HOME/.claude/skills/video-edit" && python3 "$HOME/.claude/skills/video-edit/install_all.py"
```

*(Note: `install_all.py` automatically detects `~/.claude/skills` and `~/.gemini/config/skills`, installs all 5 skills from `skills/`, downloads Google Fonts `Be Vietnam Pro` + SFX, and sets up the shared Python `.venv` with `faster-whisper`.)*

### Option B: Chat Install inside Claude Code or Antigravity

Paste this into your agent chat:

```text
Install the full video-edit-skill suite from https://github.com/maiductuan/video-edit-skill and run python3 install_all.py
```

---

## Requirements

| Tool | macOS | Windows (PowerShell) | Linux |
|---|---|---|---|
| **FFmpeg** | `brew install ffmpeg` | `winget install --id Gyan.FFmpeg -e` | `sudo apt install ffmpeg` |
| **Node.js 22+** | `brew install node` | `winget install --id OpenJS.NodeJS.LTS -e` | [nodejs.org](https://nodejs.org) |
| **Python 3.10+** | `brew install python` | `winget install --id Python.Python.3.12 -e` | `sudo apt install python3 python3-venv` |

---

## Repository Structure

```text
video-edit-skill/
├── SKILL.md                        # Root skill mirror (/video-edit 9:16 talking-head reels)
├── README.md                       # Suite documentation
├── install_all.py                  # One-command installer for all 5 skills
├── scripts/                        # Root /video-edit pipeline
├── assets/template/build.py        # 9:16 HyperFrames template
├── references/                     # Core editorial & anti-AI-slop reference docs
└── skills/                         # Complete 5-skill directory
    ├── video-edit/                 # /video-edit (9:16 Talking-Head Reels / TikTok / Shorts)
    │   ├── SKILL.md
    │   ├── assets/
    │   ├── references/
    │   └── scripts/
    ├── youtube-edit/               # /youtube-edit (16:9 Vlog, Review, Talking-Head + Shorts)
    │   ├── SKILL.md
    │   ├── references/ (ai-motion-and-visuals.md, looks.md, graphics.md)
    │   └── scripts/ (setup.py, ingest.py, assemble.py, build_graphics.py, render.py, extract_shorts.py)
    ├── commercial-promo/           # /commercial-promo (9:16, 4:5, 1:1, 16:9 Product Ads)
    │   ├── SKILL.md
    │   └── scripts/ (render_promo.py)
    ├── podcast-interview/          # /podcast-interview (16:9 & 9:16 Split-Screen Podcast)
    │   ├── SKILL.md
    │   └── scripts/ (render_podcast.py)
    └── video-director/             # /video-director (Master Router, G0-G4 Audit, Beat-Sync, Reframe)
        ├── SKILL.md
        └── scripts/ (audit_video.py, beat_sync.py, reframe.py)
```

---

## Credits

Built on [FFmpeg](https://ffmpeg.org), [HyperFrames](https://github.com/heygen-com/hyperframes), [faster-whisper](https://github.com/SYSTRAN/faster-whisper), and [Pillow](https://python-pillow.org). Editorial QA and anti-slop principles inspired by best practices from the open-source Claude video skills ecosystem.
