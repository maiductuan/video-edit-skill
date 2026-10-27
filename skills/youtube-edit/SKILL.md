---
name: youtube-edit
description: >-
  Turns raw 16:9 camera or phone clips (talking-head + B-roll) into a finished, polished YouTube video (1080p60 or 4K)
  for vlogs, food/travel reviews, and studio talking-head episodes. Automatically classifies A-roll (speech) vs B-roll
  (scenery/food/action), transcribes Vietnamese or English speech with word-level timing, trims dead air and bad takes,
  weaves B-roll over A-roll commentary (J/L cuts), generates animated 16:9 YouTube graphics (Intro Banner, Chapter
  Dividers, Location/Food/Price/Rating Lower-Thirds, Info Callouts, Subscribe & Bell CTA), adds styled Vietnamese
  subtitles, mixes BGM with automatic voice ducking + sound effects, and checks every overlay on a QA contact sheet.
  Trigger with /youtube-edit or phrases like 'edit this YouTube video', 'dựng vlog YouTube', 'edit vlog review',
  'làm video YouTube từ các clip này'.
---

# /youtube-edit

End-to-end 16:9 YouTube video editor for **Vlogs, Food/Travel Reviews, and Talking-Head** episodes. Raw clips (both talking on-camera A-roll and scenic/food B-roll) go in; a finished 1920×1080 (30fps or 60fps) YouTube master comes out with animated 16:9 graphics, clean cuts, color grading, SFX, and optional BGM auto-ducking.

Read before building:
- [`references/graphics.md`](./references/graphics.md) — Exact specs and JSON schemas for the 16:9 YouTube Graphics Pack (Intro Title, Chapter Cards, Review/Location Lower-Thirds with Price & Rating, Callout Badges, Subscribe CTA, and Subtitles).
- [`references/looks.md`](./references/looks.md) — The 3 YouTube 16:9 color grades & visual themes (`vibrant_vlog`, `cinema_travel`, `clean_studio`).

---

## Step 0: Environment & Channel Config

`SK` is this skill's directory (`~/.gemini/config/skills/youtube-edit` or `.agents/skills/youtube-edit`).

1. Check `SK/.platform.json`. If missing or `ready` is not `true`, run:
   ```bash
   python3 "SK/scripts/setup.py"
   ```
   Wait until it prints `READY`. Read `PY` (the skill's `.venv/bin/python`) from `SK/.platform.json`. Always use `PY` to run scripts in `SK/scripts/`.

2. Check `SK/config.json`. If it does not exist, ask the user (or use sensible defaults if they ask to start immediately):
   - **Channel Name** (e.g., `"Tuấn Đi Review"`)
   - **Channel Handle / Tagline** (e.g., `"@tuandireview • Ẩm thực & Khám phá"`)
   - **Default Look**:
     - `vibrant_vlog` (default: warm, appetizing colors for food, street life & travel vlogs)
     - `cinema_travel` (golden highlights, teal shadows, subtle letterbox/vignette feel)
     - `clean_studio` (natural skin tones, high clarity for talking-head & tech reviews)
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
   - Keep all titles, lower-thirds, and subtitles inside `x: 80..1840`, `y: 70..980` (respecting the YouTube player scrubber bar at the bottom and top-right info cards).
   - Never place a lower-third or chapter banner over a speaker's face or over the main close-up subject of a food/product B-roll shot.
2. **Vietnamese Typography Integrity:**
   - Never use Latin-only stripped fonts for Vietnamese text. All graphics and subtitles use full Vietnamese Unicode glyphs (`ă, â, đ, ê, ô, ơ, ư` and all 5 tone marks).
3. **A-Roll + B-Roll Storytelling:**
   - **A-Roll (Talking-head / Host speaking on camera):** Keep the cleanest take when lines are repeated; trim dead air (>0.4s silence) between sentences. Use a `1.25x–1.45x` punch-in crop when two A-roll cuts from the same camera angle appear back-to-back.
   - **B-Roll (Food close-up, street atmosphere, walking shot, drone/pan):** Use in two ways:
     - **B-Roll Overlay (J/L Cut / Voice-over):** Keep the A-roll audio playing continuously while cutting the video track to B-roll (`"broll_clip"` in `edl.json`) when the host describes food, scenery, or a location.
     - **Standalone B-Roll Montage:** Insert 2.5s–5.0s scenic shots between chapters with music/ambient sound lifted.
4. **Audio Balance:**
   - Normalize speech to `-14 LUFS` (peak `-2 dB` to `-4 dB`).
   - Graphic SFX (`whoosh-short`, `pop`, `sparkle`, `click`) must stay subtle (`volume 0.25–0.35`) so they never overpower speech.
   - When BGM is included, duck BGM to `12%–15%` volume during speech and swell to `40%–50%` during B-roll-only transitions.
5. **Never modify or delete the user's original source video files.**

---

## End-to-End Workflow

### 1. Intake & Ingest (`ingest.py`)
Create `<projectsDir>/<project-slug>/` and run:
```bash
"PY" "SK/scripts/ingest.py" "<project_dir>" <clips_or_folder> [--lang vi] [--newest N]
```
What `ingest.py` produces:
- `sources.json`: Maps `c1`, `c2`, ... to absolute file paths with resolution, FPS, duration, and automatic classification (`"A-ROLL"` if speech covers >25% of the clip, else `"B-ROLL"`).
- `work/sheets.jpg`: Stacked 16:9 contact sheets (8 frames per clip) so you can inspect every camera angle, dish, and location.
- `transcript.txt` & `words_cN.json`: Word-level and segment-level timestamps + `silencedetect` speech map.

**Always inspect `work/sheets.jpg` (using `read_file`) and read `transcript.txt` before planning the edit.**

---

### 2. Build the Edit Decision List (`<project_dir>/edl.json`)
Design the narrative structure (Hook -> Intro -> Chapter 1 -> Chapter 2 -> ... -> Outro/CTA) and write `<project_dir>/edl.json`:

```json
[
  {
    "id": "hook",
    "type": "aroll",
    "clip": "c1",
    "in": 2.40,
    "out": 8.80,
    "zoom": 1.0,
    "cx": 0.5,
    "cy": 0.5,
    "line": "Hôm nay mình dẫn mọi người đi khám phá phố cổ Hội An..."
  },
  {
    "id": "intro_broll",
    "type": "broll",
    "clip": "c2",
    "in": 1.00,
    "out": 5.50,
    "ambient_vol": 0.35,
    "note": "Toàn cảnh phố cổ đèn lồng lung linh"
  },
  {
    "id": "review_caolau",
    "type": "aroll_with_broll",
    "clip": "c3",
    "in": 10.20,
    "out": 22.50,
    "broll_inserts": [
      {"clip": "c4", "src_in": 3.0, "start_offset": 4.0, "duration": 4.5}
    ],
    "line": "Tô cao lầu ở đây sợi mì rất dai, thịt xá xíu đậm đà..."
  }
]
```

Supported segment types in `edl.json`:
- `"aroll"`: Standard talking-head/on-camera clip with its own speech audio (`zoom`, `cx`, `cy` optional for 4K punch-in).
- `"broll"`: Scenic/action shot (uses softened ambient audio `ambient_vol`, default `0.25`).
- `"aroll_with_broll"`: Plays the A-roll audio continuously from `clip` (`in`..`out`), while cutting the video picture to one or more `broll_inserts` at `start_offset` seconds into the segment!

Run `assemble.py` to build `<project_dir>/assets/base_16x9.mp4` and `<project_dir>/segments.json`:
```bash
"PY" "SK/scripts/assemble.py" "<project_dir>" [--fps 60]
```

---

### 3. Configure 16:9 YouTube Graphics & Subtitles (`<project_dir>/graphics.json`)
Create `<project_dir>/graphics.json` to define the animated 16:9 YouTube overlays and optional subtitles. All times can be given either as absolute seconds (`"start"`, `"end"`) or relative to a segment ID (`"segment": "review_caolau", "offset": 0.5, "duration": 4.5`):

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
      "type": "chapter",
      "segment": "review_caolau",
      "offset": 0.0,
      "duration": 3.0,
      "number": "01",
      "title": "Cao Lầu Gia Truyền Phố Cổ",
      "subtitle": "Điểm dừng chân đầu tiên"
    },
    {
      "type": "lower_third",
      "segment": "review_caolau",
      "offset": 3.5,
      "duration": 5.0,
      "category": "ẨM THỰC HỘI AN",
      "title": "Cao Lầu Đặc Biệt",
      "location": "📍 26 Thái Phiên, Minh An, Hội An",
      "price": "💰 40.000đ / tô",
      "rating": "⭐ 9.2/10"
    },
    {
      "type": "callout",
      "segment": "review_caolau",
      "offset": 9.0,
      "duration": 3.5,
      "position": "top_right",
      "icon": "💡",
      "title": "Mẹo nhỏ",
      "text": "Nên đi trước 17h30 để không phải xếp hàng chờ bàn!"
    },
    {
      "type": "subscribe",
      "segment": "review_caolau",
      "offset": 13.0,
      "duration": 4.0,
      "channel": "Tuấn Đi Review",
      "handle": "@tuandireview • Nhấn Đăng Ký để xem vlog mới mỗi tuần!"
    }
  ]
}
```

Generate the animated RGBA overlay assets, sound cues, and `.ass` subtitles:
```bash
"PY" "SK/scripts/build_graphics.py" "<project_dir>"
```

---

### 4. Final Render, Color Grade, Audio Mix & QA (`render.py`)
Composite the base 16:9 timeline, color grade look, animated 16:9 graphics, `.ass` subtitles, SFX triggers, and optional BGM (with auto-ducking during speech):
```bash
"PY" "SK/scripts/render.py" "<project_dir>" -o "<project_dir>/renders/<slug>-v1.mp4" [--bgm "/path/to/music.mp3"] [--quality high]
```
What `render.py` produces:
- `<project_dir>/renders/<slug>-v1.mp4`: The finished 1920×1080 YouTube video (H.264 + AAC 192kbps).
- `<project_dir>/work/qa_sheet.jpg`: A visual QA contact sheet sampling every graphic overlay and cut point in the final rendered video.

**Always inspect `<project_dir>/work/qa_sheet.jpg` with `read_file` to verify that every title, lower-third, chapter card, and subtitle is legible, properly aligned inside the 16:9 safe zone, and free of typos before delivering to the user.**

---

### 5. Optional: Extract a 9:16 YouTube Short (`extract_shorts.py`)
When the user also wants a vertical 9:16 teaser/Short from their finished 16:9 YouTube episode:
```bash
"PY" "SK/scripts/extract_shorts.py" "<project_dir>/renders/<slug>-v1.mp4" --start 0.0 --duration 35.0 -o "<project_dir>/renders/<slug>-short.mp4" --title "Khám Phá Hội An"
```
