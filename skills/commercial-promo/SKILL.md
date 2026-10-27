---
name: commercial-promo
description: >-
  Creates high-taste, non-AI-slop product launch videos, SaaS/app screen demos, and commercial showcases across
  16:9, 9:16, 4:5, and 1:1 aspect ratios. Features beat-synced cutting, ScreenStudio-style zoom-to-action on UI or
  product details, clean neo-grotesk motion typography (Be Vietnam Pro / Avenir Next), consequence-over-claim visual
  storytelling, and a crisp 0.8-1.4s brand end lockup. Trigger with /commercial-promo or requests like 'make a product
  promo video', 'edit an app demo reel', 'dựng video quảng cáo sản phẩm', 'làm video giới thiệu app'.
---

# /commercial-promo

High-taste Product Launch, App/SaaS Demo & Commercial Promo editor for **16:9 (YouTube/Web), 9:16 (Reels/TikTok/Shorts), 4:5 (Instagram/Facebook Feed Ads), and 1:1 (Square)**.

Built on the **Anti-AI-Slop & Motion Designer Taste Codex** ([`anti-ai-slop.md`](../video-edit/references/anti-ai-slop.md)):
- **Consequence over Claim:** Show the product performing the action (zoomed 1.4x–2.2x into the real UI/product detail) rather than floating a small card on an empty background or inventing fake stats.
- **No Page Chrome / No Deck Slides:** Zero fake `REC`, `01 / FEATURE`, progress bars, or PowerPoint bullet slides.
- **Tm1 Pacing Rhythm:** Beats shorten toward the climax (`2.4s -> 1.9s -> 1.5s -> 1.1s`), then the final brand lockup lands cleanly and holds `0.8–1.4s`.

---

## Workflow & `promo.json` Specification

1. Create `<project_dir>/promo.json`:
```json
{
  "ratio": "16:9",
  "brand": {
    "name": "CALM BELL STUDIO",
    "tagline": "Thiết kế âm thanh & hình ảnh tự nhiên",
    "accent": "#FFB800",
    "surface": "dark"
  },
  "music": "/optional/path/to/bgm.mp3",
  "beats": [
    {
      "clip": "/path/to/clip1.mp4",
      "in": 1.0,
      "out": 3.6,
      "zoom": 1.0,
      "cx": 0.5,
      "cy": 0.5,
      "kicker": "BƯỚC ĐỘT PHÁ",
      "headline": "Tự Động Hóa Quy Trình Dựng",
      "subline": "Từ clip thô đến bản master trong 2 phút"
    },
    {
      "clip": "/path/to/clip2.mp4",
      "in": 4.2,
      "out": 6.4,
      "zoom": 1.35,
      "cx": 0.5,
      "cy": 0.45,
      "headline": "Chuẩn Màu Điện Ảnh & Âm Thanh -14 LUFS"
    }
  ],
  "end_card": {
    "duration": 1.2,
    "title": "CALM BELL STUDIO",
    "cta": "Trải nghiệm ngay hôm nay"
  }
}
```

2. Run `render_promo.py` with the suite's Python (`.venv/bin/python`):
```bash
"/Users/laptoptt/.gemini/config/skills/video-edit/.venv/bin/python" "SK/scripts/render_promo.py" "<project_dir>/promo.json" -o "<project_dir>/promo_master.mp4"
```

3. Run `/video-director`'s `audit_video.py` on `<project_dir>/promo_master.mp4` and inspect the `_audit_sheet.jpg` with `read_file` before delivering!
