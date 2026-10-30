---
name: youtube-edit
description: >-
  Turns raw 16:9 camera or phone clips (talking-head + B-roll) into a finished, dynamic YouTube video (1080p60 or 4K)
  for vlogs, food/travel reviews, and studio talking-head episodes. Automatically classifies A-roll (speech) vs B-roll
  (scenery/food/action), transcribes Vietnamese or English speech with word-level timing, trims dead air and bad takes,
  proactively generates AI editorial visuals & B-roll imagery (with 4K-supersampled 60fps Ken Burns camera motion) when
  real B-roll is missing so talking-head sections never feel static or dry, weaves B-roll over A-roll commentary (J/L cuts),
  renders 11 animated 16:9 YouTube graphics & multi-frame RGBA motion cards (Intro, Chapters, Review Lower-Thirds,
  PiP AI Visual Cards, Counting Stat Cards, Staggered Checklists, Before/After Comparisons, Kinetic Quotes, Callouts,
  Subscribe CTA), adds styled Vietnamese subtitles, mixes BGM with automatic voice ducking + SFX, and checks every
  overlay on a QA contact sheet. Trigger with /youtube-edit or phrases like 'edit this YouTube video', 'dựng vlog YouTube',
  'edit vlog review', 'làm video YouTube từ các clip này'.
---

# /youtube-edit

End-to-end 16:9 YouTube video editor for **Vlogs, Food/Travel Reviews, and Talking-Head** episodes. Raw clips (talking on-camera A-roll and optional scenic/food B-roll) go in; a finished 1920×1080 (30fps or 60fps) YouTube master comes out with dynamic camera motion, AI-generated editorial B-roll & visual cards, multi-frame animated RGBA motion graphics, clean J/L cuts, color grading, SFX, and BGM auto-ducking.

Read before building:
- [`references/ai-motion-and-visuals.md`](./references/ai-motion-and-visuals.md) — **Mandatory Anti-Static Playbook:** How and when to generate AI B-roll visuals (`image-generator`), dynamic camera motion (`push_in`, `pull_out`, `pan_right`, `pan_left`), and animated motion cards so videos never feel stiff ("đơ") or dry ("khô").
- [`references/graphics.md`](./references/graphics.md) — Exact specs and JSON schemas for all **11 YouTube 16:9 Graphics & Multi-Frame RGBA Motion Cards** (`intro`, `chapter`, `lower_third`, `callout`, `subscribe`, `visual_card`, `stat_card`, `checklist`, `comparison`, `kinetic_quote`, `custom_motion`).
- [`references/looks.md`](./references/looks.md) — The 6 YouTube 16:9 color grades & visual themes (`vibrant_vlog`, `cinema_travel`, `clean_studio`, `film_kodak`, `minimal_editorial`, `warm_food`).

---

## Step 0: Environment & Channel Config

`SK` is this skill's directory (`~/.gemini/config/skills/youtube-edit` or `~/.claude/skills/youtube-edit`).

1. Check `SK/.platform.json`. If missing or `ready` is not `true`, run:
   ```bash
   python3 "SK/scripts/setup.py"
   ```
   *(On Windows if `python3` is a Store stub, use `python "SK/scripts/setup.py"` or `py -3 "SK/scripts/setup.py"`.)*
   Wait until it prints `READY`. Read `PY` (the skill's `.venv` Python) from `SK/.platform.json`. Always use `PY` to run scripts in `SK/scripts/` (in PowerShell prefix with `&`: `& "PY" "SK/scripts/..."`).

2. Check `SK/config.json`. If it does not exist, ask the user (or use sensible defaults if they ask to start immediately):
   - **Channel Name** (e.g., `"Tuấn Đi Review"`)
   - **Channel Handle / Tagline** (e.g., `"@tuandireview • Ẩm thực & Khám phá"`)
   - **Default Look**: `vibrant_vlog` (default), `warm_food`, `cinema_travel`, `clean_studio`, `film_kodak`, or `minimal_editorial`
   - **Default FPS**: `60` (smooth 1080p60 vlog motion) or `30` (cinematic 30fps)
   - **Language**: `"vi"` (Vietnamese default) or `"en"`

   Save `SK/config.json`:
   ```json
   {
     "channelName": "Tuấn Đi Review",
     "channelHandle": "@tuandireview",
     "defaultLook": "vibrant_vlog",
     "fps": 60,
     "lang": "vi",
     "clipsDir": "~/Downloads",
     "projectsDir": "~/youtube-edits"
   }
   ```

---

## Hard Rules for YouTube 16:9 Editing

1. **YouTube 16:9 Safe Zone (1920×1080):**
   - Keep all titles, lower-thirds, motion cards, and subtitles inside `x: 80..1840`, `y: 70..980` (respecting the YouTube player scrubber bar at the bottom and top-right info cards).
   - Never place a card over a speaker's face: when the host sits center-left, place PiP motion cards (`visual_card`, `stat_card`, `checklist`) on `"position": "right"`; when the host sits right, use `"position": "left"`.
2. **Vietnamese Typography Integrity:**
   - Never use Latin-only stripped fonts for Vietnamese text. All graphics and subtitles use full Vietnamese Unicode glyphs (`ă, â, đ, ê, ô, ơ, ư` and all 5 tone marks). Never ask an AI image model to render Vietnamese paragraphs inside an image — generate text-free visuals and let `build_graphics.py` render crisp vector Vietnamese typography.
3. **Anti-Static / Anti-Dry Storytelling ("No Bare Talking-Head > 6s"):**
   - **A-Roll (Talking-head / Host speaking on camera):** Keep the cleanest take when lines are repeated; trim dead air (>0.4s silence) while keeping natural breaths (`220–350 ms`). Use a `1.25x–1.45x` punch-in crop when two A-roll cuts from the same angle appear back-to-back, and add subtle `"motion": "push_in"` on longer explanations.
   - **Never leave a bare talking-head shot unchanged for more than `5.5–6.5s`:**
     - If real B-roll footage exists, weave it via `"aroll_with_broll"` (J/L cut voiceover) or standalone `"broll"` montages (`2.5s–5.0s`).
     - **If real B-roll is missing or the host discusses abstract concepts, numbers, comparisons, tips, or stories:** proactively spawn `image-generator` subagents in parallel to create clean editorial visuals in `<project_dir>/assets/ai_visuals/*.png` (woven as Ken Burns B-roll in `edl.json` or framed PiP `visual_card` overlays in `graphics.json`) AND pair spoken beats with animated motion cards (`stat_card`, `checklist`, `comparison`, `kinetic_quote`).
   - **Importance Budget (`Max 2 Rule`):** At any timestamp, show at most **1 hero graphic/motion card** (+ clean bottom subtitle if enabled). Never stack multiple cards at the same second.
4. **Audio Balance:**
   - Normalize integrated loudness to `-14 LUFS` (`<= -1.0 dBTP` true peak).
   - Graphic SFX (`whoosh-short`, `pop`, `sparkle`, `click`, `click-soft`) stay subtle (`volume <= 0.28`) so they never overpower speech.
   - When BGM is included, duck BGM to `~14%` volume during speech and swell smoothly to `~38%` during B-roll-only transitions.
5. **Never modify or delete the user's original source video files.**

---

## End-to-End Workflow

### 1. Intake & Ingest (`ingest.py`)
Create `<projectsDir>/<project-slug>/` and run:
```bash
"PY" "SK/scripts/ingest.py" "<project_dir>" <clips_or_folder> [--lang vi] [--newest N]
```
*(In PowerShell prefix with `&`: `& "PY" "SK/scripts/ingest.py" ...`)*

What `ingest.py` produces:
- `sources.json`: Maps `c1`, `c2`, ... to absolute file paths with resolution, FPS, duration, and automatic classification (`"A-ROLL"`, `"B-ROLL"`, or `"IMAGE-BROLL"`).
- `work/sheets.jpg`: Stacked 16:9 contact sheets (8 frames per clip) so you can inspect every camera angle, speaker framing (left/center/right), dish, and location.
- `transcript.txt` & `words_cN.json`: Word-level and segment-level timestamps + `silencedetect` speech map.

**Always inspect `work/sheets.jpg` (using `read_file`) and read `transcript.txt` before planning the edit.**

---

### 2. Generate AI Visuals in Parallel (`image-generator` -> `<project_dir>/assets/ai_visuals/`)
Audit the transcript for stretches > `6.0s` where no matching real B-roll exists (or where an editorial diagram/illustration elevates the story):
- Spawn `image-generator` subagents in parallel to save `16:9` (for full-screen B-roll cutaways) or `4:3` (for floating PiP `visual_card` inserts) images into `<project_dir>/assets/ai_visuals/`.
- Prompt for human art-director styles matching the active look (e.g., *warm 35mm documentary photography*, *clean editorial collage illustration on warm paper/charcoal*, *minimalist studio product macro*) and always include *"No text, no watermarks, no UI chrome, no neon sci-fi clichés"*.

---

### 3. Build the Edit Decision List (`<project_dir>/edl.json`)
Design the narrative structure (Hook -> Intro -> Chapters -> Outro/CTA) with dynamic camera `"motion"` and real or AI B-roll inserts:

```json
[
  {
    "id": "hook",
    "type": "aroll",
    "clip": "c1",
    "in": 2.40,
    "out": 8.80,
    "zoom": 1.0,
    "motion": "push_in",
    "motion_amt": 0.06,
    "line": "Hôm nay mình dẫn mọi người đi khám phá phố cổ Hội An..."
  },
  {
    "id": "intro_broll",
    "type": "broll",
    "clip": "c2",
    "in": 1.00,
    "out": 5.50,
    "motion": "pan_right",
    "ambient_vol": 0.35,
    "note": "Toàn cảnh phố cổ đèn lồng lung linh"
  },
  {
    "id": "review_caolau",
    "type": "aroll_with_broll",
    "clip": "c3",
    "in": 10.20,
    "out": 26.50,
    "motion": "push_in",
    "broll_inserts": [
      {"clip": "c4", "src_in": 3.0, "start_offset": 3.5, "duration": 4.5, "motion": "push_in"},
      {"image": "assets/ai_visuals/caolau_origin.png", "start_offset": 10.5, "duration": 4.0, "motion": "pan_right"}
    ],
    "line": "Tô cao lầu ở đây sợi mì rất dai, gắn liền với lịch sử thương cảng Hội An..."
  }
]
```

Supported segment & motion options in `edl.json`:
- `"aroll"`: Talking-head clip with speech audio (`zoom`, `cx`, `cy` for 4K crop + `"motion": "push_in" | "pull_out" | "pan_right" | "pan_left" | "none"`).
- `"broll"`: Scenic/action video (`"clip"`) **OR** AI-generated 16:9 image (`"image": "assets/ai_visuals/..."`, `"duration": 4.0`, `"motion": "push_in" | "pull_out" | "pan_right" | "pan_left" | "drift_up"`). Still images are 4K-supersampled (`3840×2160`) for zero-jitter 60fps Ken Burns motion!
- `"aroll_with_broll"`: Continuous A-roll speech audio from `clip`, cutting the video track to one or more `broll_inserts` (each insert can be either a `"clip"` video or an `"image"` AI visual with Ken Burns `"motion"`!).

Run `assemble.py` to build `<project_dir>/assets/base_16x9.mp4` and `<project_dir>/segments.json`:
```bash
"PY" "SK/scripts/assemble.py" "<project_dir>" [--fps 60]
```

---

### 4. Configure Animated 16:9 Graphics, Motion Cards & Subtitles (`<project_dir>/graphics.json`)
Create `<project_dir>/graphics.json` combining classic YouTube cards (`intro`, `chapter`, `lower_third`, `callout`, `subscribe`) with **multi-frame animated RGBA motion cards** (`visual_card`, `stat_card`, `checklist`, `comparison`, `kinetic_quote`, `custom_motion`):

```json
{
  "look": "vibrant_vlog",
  "subtitles": {
    "enabled": true,
    "style": "pill_bottom",
    "items": [
      {"segment": "hook", "offset": 0.1, "duration": 3.1, "text": "Hôm nay cùng mình khám phá Phố Cổ Hội An nhé!"}
    ]
  },
  "overlays": [
    {
      "type": "intro",
      "segment": "intro_broll",
      "offset": 0.3,
      "duration": 4.0,
      "badge": "TUẤN ĐI REVIEW • VLOG #12",
      "title": "KHÁM PHÁ PHỐ CỔ HỘI AN",
      "subtitle": "Ăn Sập Phố Cổ • Check-in Góc Đẹp • Trải Nghiệm Thực Tế"
    },
    {
      "type": "lower_third",
      "segment": "review_caolau",
      "offset": 3.5,
      "duration": 4.5,
      "category": "ẨM THỰC HỘI AN",
      "title": "Cao Lầu Đặc Biệt",
      "location": "26 Thái Phiên, Minh An, Hội An",
      "price": "40.000đ / tô",
      "rating": "9.2/10"
    },
    {
      "type": "visual_card",
      "segment": "review_caolau",
      "offset": 8.5,
      "duration": 4.5,
      "position": "right",
      "image": "assets/ai_visuals/gieng_ba_le.png",
      "tag": "BÍ QUYẾT GIA TRUYỀN",
      "title": "Nước Giếng Bá Lễ Cổ",
      "caption": "Sợi mì cao lầu chuẩn vị phải được nhào từ tro củi tràm và nước giếng cổ."
    },
    {
      "type": "stat_card",
      "segment": "review_caolau",
      "offset": 13.5,
      "duration": 3.8,
      "position": "right",
      "tag": "ĐÁNH GIÁ THỰC TẾ",
      "value": "9.2/10",
      "label": "Độ đáng thử khi ghé Hội An",
      "subtext": "Mức giá bình dân, phục vụ nhanh dưới 5 phút"
    },
    {
      "type": "checklist",
      "segment": "review_caolau",
      "offset": 18.0,
      "duration": 4.8,
      "position": "right",
      "tag": "3 LƯU Ý KHI ĐI",
      "title": "Kinh nghiệm ăn ngon",
      "items": [
        "Đi trước 17h30 để tránh xếp hàng",
        "Gọi thêm tóp mỡ giòn ăn kèm",
        "Thanh toán tiền mặt hoặc chuyển khoản"
      ]
    },
    {
      "type": "subscribe",
      "segment": "review_caolau",
      "offset": 23.0,
      "duration": 3.4,
      "channel": "Tuấn Đi Review",
      "handle": "@tuandireview • Nhấn Đăng Ký để xem vlog mới mỗi tuần!"
    }
  ]
}
```

Generate the animated RGBA `.mov`/`.png` overlay assets, sound cues, and `.ass` subtitles:
```bash
"PY" "SK/scripts/build_graphics.py" "<project_dir>"
```

---

### 5. Final Render, Color Grade, Audio Mix & QA (`render.py`)
Composite the base 16:9 timeline, color grade look, animated RGBA motion cards, `.ass` subtitles, SFX triggers, and optional BGM (with auto-ducking during speech + `-14 LUFS` EBU R128 mastering):
```bash
"PY" "SK/scripts/render.py" "<project_dir>" -o "<project_dir>/renders/<slug>-v1.mp4" [--bgm "/path/to/music.mp3"] [--quality high]
```
What `render.py` produces:
- `<project_dir>/renders/<slug>-v1.mp4`: The finished 1920×1080 YouTube video (H.264 + AAC 192kbps, `-14 LUFS`).
- `<project_dir>/work/qa_sheet.jpg`: A visual QA contact sheet sampling every graphic & motion overlay (at 70% peak reveal so counters, checklists, and comparisons are fully visible) in the final rendered video.

**Always inspect `<project_dir>/work/qa_sheet.jpg` with `read_file` to verify that every title, motion card, AI visual, lower-third, and subtitle is legible, properly aligned inside the 16:9 safe zone, never covering the host's face, and free of typos before delivering to the user.**

---

### 6. Optional: Extract a 9:16 YouTube Short (`extract_shorts.py`)
When the user also wants a vertical 9:16 teaser/Short from their finished 16:9 YouTube episode:
```bash
"PY" "SK/scripts/extract_shorts.py" "<project_dir>/renders/<slug>-v1.mp4" --start 0.0 --duration 35.0 -o "<project_dir>/renders/<slug>-short.mp4" --title "Khám Phá Hội An"
```
