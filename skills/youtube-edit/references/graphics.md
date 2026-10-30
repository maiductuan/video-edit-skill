# YouTube 16:9 TVC & Documentary Broadcast Motion Pack (`graphics.md`)

All graphics are rendered for a **1920×1080 RGBA** canvas using **2x-supersampled Lanczos anti-aliasing**, **translucent smoked-obsidian glass plates (`alpha ~82%`) with `1px` specular hairline borders**, **wide-tracked Swiss/TVC micro-kickers (`+3.4px` character tracking)**, and **After-Effects-style `overflow: hidden` masked baseline typography reveals (`quintic ease-out` `1 - (1-t)^5`)** — designed to look like a Netflix Documentary, Sony Alpha Film, or Apple Keynote rather than boxy SaaS/AI templates.

> **Strict Anti-AI-Tag Rule:** Never write `"MINH HỌA AI"`, `"AI VISUAL"`, or `"ẢNH AI"` in any `tag` or `category` field (`build_graphics.py` also strips self-referential AI labels automatically). Always write real story context (`"GÓC QUAY CHI TIẾT"`, `"PHỐ CỔ · 17:30"`, `"NGUYÊN LIỆU GỐC"`).

---

## Safe Zone Layout (1920×1080)

- **Horizontal Margins:** `88px` left and right (`x: 88..1832`).
- **Vertical Margins:** `72px` top (`y: 72`), `100px` bottom (`y: 980`) so nothing collides with the YouTube player progress bar or control icons.
- **Face Protection Rule:** Inspect `work/sheets.jpg` first! When the speaker sits center-left, place PiP motion cards (`visual_card`, `stat_card`, `checklist`) on `"position": "right"`; when the speaker sits center-right, place them on `"position": "left"`. Use `"position": "center"` over blurred/scenic B-roll or when emphasizing a full topic transition.
- **Subtitles Band:** Centered horizontally at `y: 945..1015`.

---

## Part A: Classic YouTube Editorial Cards (`1920×1080` RGBA)

### 1. `intro` — Full-Screen Title Banner
Displayed over an opening B-roll or hook shot (`3.5s–4.5s`).
- **Fields:** `badge` (top pill), `title` (main bold headline), `subtitle` (supporting tagline).
- **SFX:** `whoosh-short` at entrance + `impact-bass-1` (subtle) at title lock.

### 2. `chapter` — Section / Chapter Transition Card
Marks a new topic, stop, or chapter (`2.5s–3.5s`).
- **Fields:** `number` (`"01"`, `"02"` -> renders `"CHƯƠNG 01"`), `title`, `subtitle` (optional).
- **Placement:** Bottom-left (`x: 88, y: 760`) with vertical accent stripe.
- **SFX:** `whoosh-short` on entrance.

### 3. `lower_third` — Location / Food / Product Review Card
Signature vlog review card for introducing a dish, restaurant, landmark, or product (`4.0s–6.0s`).
- **Fields:** `category` (optional tag), `title` (dish/place name), `location` (optional), `price` (optional), `rating` (optional right badge, e.g. `"9.2/10"`).
- **Placement:** Bottom-left (`x: 88, y: 745`).
- **SFX:** `pop` on entrance + `sparkle` if `rating` is present.

### 4. `callout` — Compact Info / Tip / Note Pill
Floating card at `"top_right"` (default) or `"top_left"` (`y: 78`, `3.0s–4.5s`).
- **Fields:** `position` (`"top_right"` | `"top_left"`), `icon` (short text tag, e.g. `"MẸO NHỎ"`, `"LƯU Ý"`), `title`, `text` (1–2 concise lines).
- **SFX:** `click-soft` on entrance.

### 5. `subscribe` — YouTube Subscribe & Bell CTA
Bottom-center pill card prompting viewers to Like & Subscribe (`3.5s–4.5s`).
- **Fields:** `channel`, `handle`, `button_text` (defaults to `"ĐĂNG KÝ KÊNH"`).
- **SFX:** `pop` on entrance + `click` at `+0.75s`.

---

## Part B: Multi-Frame Animated RGBA Motion & AI Visual Cards (`30fps` Lossless `qtrle` RGBA `.mov`)

Use these **6 animated motion overlay types** throughout talking-head explanations, reviews, and essays so the screen stays dynamic and visually illustrative rather than static ("đơ") or dry ("khô"):

### 6. `visual_card` — Framed AI Illustration / Photo PiP Motion Card
Frames an AI-generated illustration, concept visual, map, or product photo (`assets/ai_visuals/*.png`) beside the talking speaker while animating a **live inner Ken Burns zoom (`1.00 -> 1.11`) + sweeping bottom accent bar** inside the rounded viewport (`3.5s–5.5s`).
```json
{
  "type": "visual_card",
  "segment": "explain_history",
  "offset": 1.0,
  "duration": 4.5,
  "position": "right",
  "image": "assets/ai_visuals/hoi_an_port.png",
  "tag": "BỐI CẢNH LỊCH SỬ",
  "title": "Thương Cảng Hội An Thế Kỷ 17",
  "caption": "Nơi giao thoa ẩm thực Việt - Nhật - Hoa tạo nên món Cao Lầu."
}
```

### 7. `stat_card` — Animated Counting Metric & Progress Bar Card
Parses numeric strings (`"+85%"`, `"40.000đ"`, `"9.4/10"`, `"3.5x"`, `"1.200+"`) and **animates the hero number counting up from `0` with cubic ease-out** while filling a rounded accent progress bar (`3.0s–4.5s`).
```json
{
  "type": "stat_card",
  "segment": "performance_test",
  "offset": 2.0,
  "duration": 3.8,
  "position": "right",
  "tag": "HIỆU NĂNG THỰC TẾ",
  "value": "+85%",
  "progress": 0.85,
  "label": "Nhanh hơn quy trình dựng thủ công",
  "subtext": "Đo trên video vlog 1080p60 dài 10 phút"
}
```

### 8. `checklist` (alias `steps_card`) — Staggered Step-by-Step Reveal Card
Reveals 2–4 concise points **one by one (`stagger` seconds apart, default `0.55s`)** with numbered accent pills sliding smoothly into place — obeying Mayer's multimedia principle instead of dumping a static text wall (`4.0s–6.0s`).
```json
{
  "type": "checklist",
  "segment": "tips_section",
  "offset": 0.5,
  "duration": 4.8,
  "position": "right",
  "tag": "3 BƯỚC QUAN TRỌNG",
  "title": "Checklist trước khi bấm máy",
  "stagger": 0.55,
  "items": [
    "Khóa WB & tốc độ màn trập 1/120s",
    "Thu âm mic rời cách miệng 15-20cm",
    "Quay thêm 3 góc B-roll cận cảnh"
  ]
}
```

### 9. `comparison` — Two-Stage Before vs. After / Pros vs. Cons Split Card
Column A (muted border) lands at `0.0s`, then Column B (accent-highlighted border & badge) reveals at `split_delay` (`default 0.65s`) with a paired `pop` SFX (`4.0s–6.0s`).
```json
{
  "type": "comparison",
  "segment": "verdict",
  "offset": 0.5,
  "duration": 5.0,
  "position": "center",
  "split_delay": 0.65,
  "left_tag": "ĐIỂM CẦN LƯU Ý",
  "left_title": "Giờ cao điểm tối",
  "left_items": ["Đông khách từ 18h-20h", "Không gian trong nhà hơi ấm"],
  "right_tag": "ĐIỂM CỘNG LỚN",
  "right_title": "Trải nghiệm ẩm thực",
  "right_items": ["Sợi cao lầu dai chuẩn vị gốc", "Giá chỉ 40.000đ, lên món cực nhanh"]
}
```

### 10. `kinetic_quote` — Editorial Thesis / Pull-Quote Highlight Banner
Highlights a key thesis statement or memorable quote with a growing vertical accent stripe and sweeping underline bar (`3.2s–4.8s`).
```json
{
  "type": "kinetic_quote",
  "segment": "conclusion",
  "offset": 0.4,
  "duration": 3.8,
  "tag": "ĐIỂM CỐT LÕI",
  "quote": "Một video cuốn hút không nằm ở hiệu ứng lòe loẹt, mà ở nhịp điệu hình ảnh luôn sống động theo từng câu kể.",
  "author": "Tổng kết trải nghiệm"
}
```

### 11. `custom_motion` — Custom Transparent `.webm` / `.mov` Motion Graphic Insert
Composites any custom RGBA motion graphic (e.g. built with HyperFrames VP9 `.webm` or Python `qtrle` `.mov`) at pixel coordinates `(x, y)`.
```json
{
  "type": "custom_motion",
  "segment": "deep_dive",
  "offset": 1.0,
  "duration": 4.0,
  "src": "work/motions/route_map.webm",
  "x": 0,
  "y": 0,
  "sfx": "whoosh-short"
}
```
