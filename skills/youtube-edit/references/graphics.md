# YouTube 16:9 Graphics Pack Specification (`graphics.md`)

All graphics are rendered at **1920×1080 RGBA** with full Vietnamese Unicode support (`Avenir Next` / `Be Vietnam Pro` / `Helvetica Neue`), smooth slide/fade entrance & exit transitions (`0.35s` in, `0.30s` out), and paired sound effects (`whoosh-short`, `pop`, `sparkle`, `click`).

---

## Safe Zone Layout (1920×1080)

- **Horizontal Margins:** `80px` left and right (`x: 80..1840`).
- **Vertical Margins:** `70px` top (`y: 70`), `100px` bottom (`y: 980`) so nothing collides with the YouTube player progress bar or control icons.
- **Subtitles Band:** Centered horizontally at `y: 945..1015`. When a `lower_third` or `subscribe` card is active at the bottom-left, subtitles stay centered or shift cleanly without overlap.

---

## Graphic Component Types (`graphics.json -> overlays[]`)

### 1. `intro` — Full-Screen Title Banner
Displayed over an opening B-roll or hook shot (typically `3.5s–4.5s`).
- **Fields:**
  - `badge` (string): Top pill label (e.g., `"TUẤN ĐI REVIEW • HỘI AN VLOG"`)
  - `title` (string): Main bold headline (e.g., `"MỘT BUỔI KHÁM PHÁ PHỐ CỔ HỘI AN"`)
  - `subtitle` (string): Supporting tagline (e.g., `"Ăn Uống • Check-in • Dạo Phố Đèn Lồng"`)
- **SFX:** `whoosh-short` at entrance + `impact-bass-1` (subtle) at title lock.

### 2. `chapter` — Section / Chapter Transition Card
Marks a new topic, stop, or chapter in the video (typically `2.5s–3.5s`).
- **Fields:**
  - `number` (string): Chapter number badge (e.g., `"01"`, `"02"`, `"CHƯƠNG 1"`)
  - `title` (string): Chapter title (e.g., `"Thưởng Thức Cao Lầu & Mì Quảng"`)
  - `subtitle` (string, optional): Context note (e.g., `"Điểm dừng chân đầu tiên tại phố cổ"`)
- **Placement:** Bottom-left or Top-left modern editorial bar with accent number block.
- **SFX:** `whoosh-short` on entrance.

### 3. `lower_third` — Location / Food / Product Review Card
The signature vlog review card for introducing a dish, restaurant, landmark, or product (typically `4.0s–6.0s`).
- **Fields:**
  - `category` (string, optional): Small uppercase tag (e.g., `"ĐỊA ĐIỂM ĂN UỐNG"`, `"CHECK-IN HỘI AN"`)
  - `title` (string): Name of dish, restaurant, or place (e.g., `"Bánh Mì Phượng Hội An"`)
  - `location` (string, optional): Address or area (e.g., `"📍 2B Phan Chu Trinh, Hội An"`)
  - `price` (string, optional): Price pill (e.g., `"💰 25.000đ - 35.000đ"`)
  - `rating` (string, optional): Score badge on the right (e.g., `"⭐ 9.5/10"`)
- **Placement:** Bottom-left (`x: 88, y: 740`), leaving the center and right of the 16:9 frame completely clear for the subject/food.
- **SFX:** `pop` on entrance + `sparkle` if `rating` is present.

### 4. `callout` — Info / Tip / Note Pill
Compact floating card at the top-right (`x: 1220, y: 86`) or top-left (`x: 88, y: 86`) for tips, warnings, or quick facts (typically `3.0s–4.5s`).
- **Fields:**
  - `position` (string): `"top_right"` (default) or `"top_left"`
  - `icon` (string): Short label or symbol (e.g., `"MẸO NHỎ"`, `"LƯU Ý"`)
  - `title` (string): Short header (e.g., `"Thời điểm đẹp nhất"`)
  - `text` (string): 1–2 line tip (e.g., `"Từ 17h00 - 18h30 khi phố cổ bắt đầu lên đèn"`)
- **SFX:** `click-soft` on entrance.

### 5. `subscribe` — YouTube Subscribe & Notification Bell CTA
Animated bottom-center or bottom-right YouTube channel card prompting viewers to Like & Subscribe (typically `3.5s–4.5s`).
- **Fields:**
  - `channel` (string): Channel name (defaults to `config.json -> channelName`)
  - `handle` (string): Subtitle/CTA text (e.g., `"@tuandireview • Đăng ký kênh để đón xem vlog mới!"`)
  - `button_text` (string, optional): Defaults to `"ĐĂNG KÝ  🔔"`
- **SFX:** `pop` on card entrance + `click` at `+0.8s` when the Subscribe button highlights.
