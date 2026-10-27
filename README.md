# Multi-Platform AI Video Edit Skill Suite
### By [@maiductuan](https://github.com/maiductuan) — Human-Grade Video Editing for Claude Code & Antigravity

A complete **5-skill video production suite** that turns raw camera or phone footage into finished, broadcast-grade edits across **YouTube (16:9)**, **Instagram Reels / TikTok / Shorts (9:16)**, **Meta & TikTok Commercial Ads (9:16 / 4:5 / 1:1 / 16:9)**, and **Video Podcasts (16:9 / 9:16)** — engineered from the ground up with strict **Anti-AI-Slop editorial standards**.

---

## The 5-Skill Suite Architecture

| Skill | Trigger | Aspect Ratios | Genre & Core Capabilities |
|---|---|---|---|
| **`video-edit`** *(Root)* | `/video-edit` | `9:16` | **Reels / TikTok / Shorts Talking-Head:** Picks cleanest take across repeats, removes dead air, 4K punch-in, CoreML background cutout for words behind your head, 3 signature looks (`bold`, `cool_girl`, `cool_dude`), animated HTML inserts via HyperFrames. |
| **`youtube-edit`** | `/youtube-edit` | `16:9` + `9:16` Shorts | **YouTube Vlog, Food/Travel Review & Studio Talking-Head:** Auto-classifies `A-ROLL` (speech) vs `B-ROLL` (scenery/food), weaves B-roll over voice with J/L cuts, 6 cinema color looks (`vibrant_vlog`, `warm_food`, `cinema_travel`, `clean_studio`, `film_kodak`, `minimal_editorial`), 5 animated 16:9 graphics (`intro`, `chapter`, `lower_third`, `callout`, `subscribe`), Vietnamese/English `Be Vietnam Pro` subtitles, speech-aware BGM ducking, and `-14 LUFS` mastering. |
| **`commercial-promo`** | `/commercial-promo` | `9:16`, `4:5`, `1:1`, `16:9` | **Product Commercials & UGC Ads:** 4 conversion frameworks (`PAS`, `AIDA`, `Before-After-Bridge`, `Flash Showcase`), 0–2s Hook Lock, feature pills, price/discount tags, end-card CTA, and EBU R128 loudness normalization. |
| **`podcast-interview`** | `/podcast-interview` | `16:9`, `9:16` | **Dual-Speaker Podcast & Interview Clips:** Side-by-side (`16:9`) or top-bottom (`9:16`) split-screen composer with rounded studio frames, active-speaker highlight border, speaker name/role badges, quote banners, and audiogram waveform bar. |
| **`video-director`** | `/video-director` | All (`16:9`, `9:16`, `4:5`, `1:1`) | **Master Router & QA Director:** Routes any video brief to the right skill, runs **6-Gate QA (`G0–G4`)** (`audit_video.py`), cuts montages locked to music RMS beats (`beat_sync.py`), and reframes exports across platforms (`reframe.py`). |

---

## Anti-AI-Slop Design Philosophy (`references/anti-ai-slop.md`)

Most automated video tools scream "made by AI" within 2 seconds. Every skill in this suite enforces **10 non-negotiable human-editor rules**:

1. **No Canned Transitions:** Zero `xfade` dissolves, wipes, pixelates, or zoom-spins between normal cuts. 95%+ of cuts are clean hard cuts or J/L cuts (`0.2s–0.5s` audio lead).
2. **Importance Budget (`Max 2 Rule`):** At any timestamp, a frame may contain at most **2 simultaneous visual elements** (e.g., footage + subtitle, OR footage + lower-third — never subtitle + lower-third + callout + floating emojis together).
3. **Organic Motion Curves:** Zero linear (`t`) movement and zero cartoon triple-bounce springs. All overlays enter with cubic ease-out (`1 - (1-t)^3` over `0.28s`) and exit over `0.22s`.
4. **Restrained Palette & High-Contrast Typography:** Max 3 colors per look (`Primary Text`, `Surface Card`, `1 Brand Accent`). No neon cyan/magenta gradients. Full Vietnamese diacritic support via **Be Vietnam Pro**.
5. **Reading Speed Guard:** Every graphic enforces `min_duration = max(2.0s, word_count / 3.0 + 0.8s)`.
6. **Subtle Sound Design:** SFX (`whoosh`, `pop`, `ding`, `shutter`) are mixed at `-16 dB to -20 dB` underneath speech and automatically suppressed if placed `< 4.0s` apart.
7. **Natural Color Grading:** Highlight roll-off and skin-tone protection (`5–10%` warm/cinema tint max) — never nuclear saturation (`sat > 1.25`).
8. **Breathing Room at Cut Boundaries:** Saves `120–180ms` of natural breath before and after sentences instead of robotic zero-millisecond word clipping.
9. **Broadcast Loudness (`-14 LUFS`):** Every render passes two-channel EBU R128 loudness normalization (`I=-14 LUFS`, `TP=-1.5 dBTP`) with dynamic speech-aware BGM ducking (`-4 dB` in B-roll, `-18 dB` under speech).
10. **Mandatory Visual QA Contact Sheet (`G0–G4`):** Never deliver an uninspected video. Every render generates a contact sheet (`work/qa_sheet.jpg`) and passes `audit_video.py`.

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
/video-edit I dropped 5 vertical talking-head clips in ~/Downloads, use the cool_dude look
```

### 2. `/youtube-edit` — 16:9 YouTube Vlog, Food/Travel Review & Talking-Head
```text
/youtube-edit Dựng video YouTube review ẩm thực từ các clip trong ~/Downloads/da-lat-trip, dùng look warm_food, thêm lower-third giá món ăn + địa chỉ và phụ đề tiếng Việt
```

### 3. `/commercial-promo` — Multi-Ratio Product Ad (`9:16`, `4:5`, `1:1`, `16:9`)
```text
/commercial-promo Tạo video quảng cáo 4:5 và 9:16 cho sản phẩm cà phê cold brew từ thư mục clips, theo cấu trúc PAS, thêm nhãn giá 69.000đ (-30%)
```

### 4. `/podcast-interview` — Dual-Speaker Split-Screen Podcast (`16:9` & `9:16`)
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
├── references/
│   ├── anti-ai-slop.md             # 10 non-negotiable human editorial rules
│   ├── pacing-and-cuts.md          # Genre pacing benchmarks & J/L cut grammar
│   ├── looks.md                    # 9:16 Reel looks (bold, cool_girl, cool_dude)
│   ├── layout.md                   # Safe zones & behind-head typography math
│   ├── overlays.md                 # Animated HTML UI inserts
│   └── gotchas.md                  # Known platform edge cases
└── skills/
    ├── youtube-edit/               # /youtube-edit (16:9 Vlog, Review, Talking-Head + Shorts)
    │   ├── SKILL.md
    │   ├── references/ (looks.md, graphics.md)
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
