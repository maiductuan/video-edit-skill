# YouTube 16:9 Looks & Color Grading (`looks.md`)

All 6 looks operate on a **1920×1080 (16:9)** or **3840×2160 (4K)** canvas and pair an organic `ffmpeg` color filter chain (designed to preserve natural skin tones and avoid "AI slop" oversaturation or crushed blacks) with a matched typography & card palette.

---

## 1. `vibrant_vlog` (Default — Food, Street & Travel Vlog)
Warm, lively colors for daytime/evening exploration and street food vlogs.
- **FFmpeg Grade:** `eq=contrast=1.05:saturation=1.12:brightness=0.012`
- **Graphics Palette:** Amber Gold `#FFB800`, Deep Charcoal Glass `rgba(18, 20, 28, 0.90)`, Crisp White `#FFFFFF`

## 2. `cinema_travel` (Cinematic Travel & Golden Hour)
Cool teal shadows paired with warm golden highlights for scenic travel storytelling and heritage towns.
- **FFmpeg Grade:** `eq=contrast=1.08:saturation=0.96:brightness=-0.008,colorbalance=rs=-0.03:gs=0.0:bs=0.04:rh=0.04:gh=0.02:bh=-0.03`
- **Graphics Palette:** Champagne Gold `#F3C969`, Obsidian Glass `rgba(12, 16, 22, 0.92)`, Ivory `#FAF7F2`

## 3. `clean_studio` (Talking-Head, Tech & Desk Review)
Neutral white balance and crisp micro-contrast for indoor setups, tutorials, and tech reviews.
- **FFmpeg Grade:** `eq=contrast=1.04:saturation=1.03:brightness=0.01`
- **Graphics Palette:** Electric Cyan `#38BDF8`, Slate Glass `rgba(15, 23, 42, 0.92)`, Pure White `#FFFFFF`

## 4. `film_kodak` (Analog Documentary & Cafe Aesthetic)
Soft lifted blacks, warm nostalgic midtones, and muted highlights inspired by 35mm Kodak Portra film (no artificial digital noise).
- **FFmpeg Grade:** `eq=contrast=1.03:saturation=0.94:brightness=0.02,colorbalance=rm=0.03:gm=0.01:bm=-0.02:rh=0.03:gh=0.01:bh=-0.03`
- **Graphics Palette:** Terracotta `#E07A5F`, Warm Espresso Glass `rgba(24, 20, 18, 0.90)`, Cream `#FDFBF7`

## 5. `minimal_editorial` (Vox / Kinfolk / Design Essay)
Refined, understated contrast with warm off-white paper-inspired cards and dark charcoal typography.
- **FFmpeg Grade:** `eq=contrast=1.06:saturation=0.92:brightness=0.005`
- **Graphics Palette:** Warm Ivory Surface `rgba(246, 243, 236, 0.95)`, Deep Ink Text `#18181B`, Vermilion Accent `#D94E34`

## 6. `warm_food` (Culinary Close-Up & Restaurant Review)
Appetizing warmth that brings out rich broth, grilled meats, and fresh herbs while keeping skin natural.
- **FFmpeg Grade:** `eq=contrast=1.06:saturation=1.15:brightness=0.015,colorbalance=rh=0.03:gh=0.01:bh=-0.02`
- **Graphics Palette:** Saffron Gold `#F59E0B`, Rich Umber Glass `rgba(22, 18, 16, 0.90)`, Warm White `#FFFDF9`
