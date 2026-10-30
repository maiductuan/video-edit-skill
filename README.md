# Multi-Platform AI Video Edit Skill Suite
### By [@maiductuan](https://github.com/maiductuan) — Human-Grade Video Editing for Claude Code & Antigravity

A complete **5-skill video production suite** that turns raw camera or phone footage into finished, broadcast-grade edits across **YouTube (16:9)**, **Instagram Reels / TikTok / Shorts (9:16)**, **Meta & TikTok Commercial Ads (9:16 / 4:5 / 1:1 / 16:9)**, and **Video Podcasts (16:9 / 9:16)** — engineered with **proactive AI Visual Storytelling, Multi-Frame Motion Graphics, and strict Anti-AI-Slop editorial standards** so videos never feel static ("đơ") or dry ("khô").

---

## The 5-Skill Suite Architecture

| Skill | Trigger | Aspect Ratios | Genre & Core Capabilities |
|---|---|---|---|
| **`video-edit`** *(Root)* | `/video-edit` | `9:16` | **Reels / TikTok / Shorts Talking-Head:** Picks cleanest take across repeats, removes dead air, 4K punch-in + **2.5D optical parallax camera pushes**, CoreML/CPU background cutout for words & wall visuals behind your head, **proactive AI editorial visual cards (`AI_CARDS`), behind-speaker wall canvases (`WALL_VISUALS`), full-bleed Ken Burns B-roll cutaways (`BROLL_CUTAWAYS`)**, parallel HyperFrames motion graphics (counters, flowcharts, Before/After, UI inserts), and 3 signature looks (`bold`, `cool_girl`, `cool_dude`). |
| **`youtube-edit`** | `/youtube-edit` | `16:9` + `9:16` Shorts | **YouTube Vlog, Food/Travel Review & Studio Talking-Head:** Auto-classifies `A-ROLL`, `B-ROLL`, and `IMAGE-BROLL`, weaves B-roll over voice with J/L cuts, **renders AI-generated B-roll images with 4K-supersampled 60fps Ken Burns motion + dynamic video camera pushes/pans**, 6 cinema color looks, **11 animated 16:9 graphics & multi-frame RGBA motion cards** (`intro`, `chapter`, `lower_third`, `callout`, `subscribe`, plus live-zooming `visual_card`, counting `stat_card`, staggered `checklist`, 2-stage `comparison`, `kinetic_quote`, and `custom_motion`), `Be Vietnam Pro` subtitles, speech-aware BGM ducking, and `-14 LUFS` mastering. |
| **`commercial-promo`** | `/commercial-promo` | `9:16`, `4:5`, `1:1`, `16:9` | **Product Commercials & UGC Ads:** 4 conversion frameworks (`PAS`, `AIDA`, `Before-After-Bridge`, `Flash Showcase`), 0–2s Hook Lock, feature pills, price/discount tags, end-card CTA, and EBU R128 loudness normalization. |
| **`podcast-interview`** | `/podcast-interview` | `16:9`, `9:16` | **Dual-Speaker Podcast & Interview Clips:** Side-by-side (`16:9`) or top-bottom (`9:16`) split-screen composer with rounded studio frames, active-speaker highlight border, speaker name/role badges, quote banners, and audiogram waveform bar. |
| **`video-director`** | `/video-director` | All (`16:9`, `9:16`, `4:5`, `1:1`) | **Master Router & QA Director:** Routes any video brief to the right skill, runs **6-Gate QA (`G0–G4`)** (`audit_video.py`), cuts montages locked to music RMS beats (`beat_sync.py`), and reframes exports across platforms (`reframe.py`). |

---

## Anti-Static Visual Rhythm & Anti-AI-Slop Philosophy (`references/ai-motion-and-visuals.md` & `references/anti-ai-slop.md`)

A great edit avoids two opposite failure modes: **boring static talking-head ("đơ & khô")** and **chaotic AI slop**. Every skill in this suite balances dynamic visual storytelling with **10 non-negotiable human-editor rules**:

1. **Anti-Static Visual Beat Rhythm:** Never leave an unchanged bare talking-head frame for more than `4.0–4.5s` (`9:16`) or `5.5–6.5s` (`16:9`). Proactively enrich missing B-roll with high-taste text-free AI visuals (`image-generator`), 60fps Ken Burns / 2.5D parallax camera drift, and animated data/concept motion cards.
2. **No Canned Transitions:** Zero `xfade` dissolves, wipes, pixelates, or zoom-spins between normal cuts. 95%+ of cuts are clean hard cuts or J/L cuts (`0.2s–0.5s` audio lead).
3. **Importance Budget (`Max 2 Rule`):** At any timestamp, a frame contains at most **2 simultaneous visual elements** (e.g., speaker + 1 animated motion card, OR B-roll + subtitle — never 4 stacked widgets).
4. **Organic Motion Curves:** Zero linear (`t`) movement on UI entrances and zero cartoon triple-bounce springs. All overlays enter with cubic ease-out (`1 - (1-t)^3` over `0.28–0.34s`).
5. **Restrained Palette & High-Contrast Typography:** Max 3 colors per look (`Primary Text`, `Surface Card`, `1 Brand Accent`). Full Vietnamese diacritic support via **Be Vietnam Pro**.
6. **Reading Speed Guard:** Every graphic enforces `min_duration = max(1.8s, word_count * 0.33s + 0.6s)`.
7. **Subtle Sound Design:** SFX (`whoosh-short`, `pop`, `sparkle`, `click`) sit `12–24 dB` underneath speech with automatic spam suppression.
8. **Natural Color Grading & Real Rooms:** Protect skin tones and keep the speaker's real environment (never permanently swap in a fake AI bedroom/studio background; use framed editorial cards, behind-speaker wall canvases, and clean B-roll cutaways instead).
9. **Broadcast Loudness (`-14 LUFS`):** Two-channel EBU R128 loudness normalization (`I=-14 LUFS`, `TP <= -1.0 dBTP`) with dynamic speech-aware BGM ducking.
10. **Mandatory Visual QA Contact Sheet (`G0–G4`):** Every render generates a contact sheet (`work/qa_sheet.jpg` / `work/cut_check.jpg`) and passes `audit_video.py`.

---

## Quick Install (All 5 Skills)

### Option A: One-Line Terminal Install (Claude Code & Antigravity)

```bash
git clone https://github.com/maiductuan/video-edit-skill "$HOME/.claude/skills/video-edit" && python3 "$HOME/.claude/skills/video-edit/install_all.py"
```

*(Note: `install_all.py` automatically detects `~/.claude/skills` and `~/.gemini/config/skills`, installs all 5 skills, downloads Google Fonts `Be Vietnam Pro` + SFX, and sets up the shared Python `.venv` with `faster-whisper`.)*

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

## Usage Examples

### 1. `/video-edit` — 9:16 Instagram Reels / TikTok / Shorts
```text
/video-edit I dropped 5 vertical talking-head clips in ~/Downloads, use the cool_dude look and add AI visual cards + motion graphics so there are no static talking stretches
```

### 2. `/youtube-edit` — 16:9 YouTube Vlog, Food/Travel Review & Talking-Head
```text
/youtube-edit Dựng video YouTube review ẩm thực từ các clip trong ~/Downloads/da-lat-trip, dùng look warm_food, tự tạo ảnh minh họa AI và các thẻ motion (stat_card, checklist, visual_card) cho các đoạn nói dài
```

### 3. `/commercial-promo` — Multi-Ratio Product Ad (`9:16`, `4:5`, `1:1`, `16:9`)
```text
/commercial-promo Tạo video quảng cáo 4:5 và 9:16 cho sản phẩm cà phê cold brew từ thư mục clips, theo cấu trúc PAS, thêm nhãn giá 69.000đ (-30%)
```

### 4. `/podcast-interview` — Dual-Speaker Split-Screen Podcast (`16:9` & 9:16`)
```text
/podcast-interview Ghép 2 góc máy host.mp4 và guest.mp4 thành video podcast 9:16 split-screen kèm sóng nhạc audiogram và tên khách mời
```

### 5. `/video-director` — Beat-Sync Montage, Multi-Ratio Reframe & 6-Gate QA Audit
```text
/video-director Dựng montage B-roll cắt đúng nhịp trống file bgm.mp3 và kiểm tra chất lượng QA G0-G4 cho file final.mp4
```

---

## Repository Structure

```text
video-edit-skill/
├── SKILL.md                        # Root skill (/video-edit 9:16 talking-head reels)
├── README.md                       # Suite documentation
├── install_all.py                  # One-command installer for all 5 skills
├── scripts/                        # /video-edit pipeline (setup, ingest, cut, cutout, render)
├── assets/template/build.py        # 9:16 HyperFrames template (with AI_CARDS, WALL_VISUALS, BROLL_CUTAWAYS, PARALLAX_SHOTS)
├── references/
│   ├── ai-motion-and-visuals.md    # Proactive AI visuals, Ken Burns, 2.5D parallax & motion cards playbook
│   ├── anti-ai-slop.md             # 10 non-negotiable human editorial rules
│   ├── pacing-and-cuts.md          # Genre pacing benchmarks & J/L cut grammar
│   ├── looks.md                    # 9:16 Reel looks (bold, cool_girl, cool_dude)
│   ├── layout.md                   # Safe zones & behind-head typography math
│   ├── overlays.md                 # Parallel HyperFrames motion & UI sub-agent briefs
│   └── gotchas.md                  # Known platform edge cases
└── skills/
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
