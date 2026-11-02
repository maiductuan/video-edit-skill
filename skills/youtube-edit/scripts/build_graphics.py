#!/usr/bin/env python3
"""Modern Creator & Storyboard Motion Graphics Engine for /youtube-edit (1920x1080 RGBA).
Designed around the Modern Dot-Grid + Condensed Display + Glowing Neon Border + Numbered Step Pills aesthetic:
  - Regular Dot-Matrix (`dot background`) inside graphic plates & storyboard boards so backgrounds never feel empty
  - Two-tier Display Typography Lockup: clean conversational sans-serif lead-in + Bold Condensed Uppercase Display
    headline in vibrant Mint Green (#4ADE80), Anthropic Coral Orange (#EB7A58), Electric Cyan (#38BDF8), or Amber (#F59E0B)
    paired with a thick 5px glowing underline bar positioned dynamically below the glyph descenders
  - Circular Outlined Number Badges (1, 2, 3) inside rounded glowing-border pill cards
  - Glowing Neon-Border Callout frames (2.5px crisp stroke + Gaussian outer bloom) with clean bullet points
  - Mini Vertical Bar-Chart comparison plates (muted grey bar vs. glowing neon bar with outer bloom) & Blur-vs-Sharp plates
  - Automatic 11-Frame Static Storyboard Sheet (`work/storyboard_11frames.jpg`) for instant visual review
  - Strict Zero-Emoji & Zero-AI-Tag enforcement (all supplementary emojis and self-referential AI labels stripped)

Usage:
  PY build_graphics.py <project_dir>
"""
import json
import math
import os
import re
import shutil
import subprocess
import sys
import textwrap
import unicodedata
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_FILE = os.path.join(SKILL_DIR, 'config.json')
PLATFORM_FILE = os.path.join(SKILL_DIR, '.platform.json')
FONTS_DIR = os.path.join(SKILL_DIR, 'assets', 'fonts')
MOTION_FPS = 30

# Modern Creator & Storyboard Palettes (Mint Green, Anthropic Coral Orange, Electric Cyan, Saffron Amber)
THEMES = {
    'modern_mint': {
        'accent': (74, 222, 128, 255),        # Vibrant Mint Green #4ADE80 (from reference storyboard)
        'accent_glow': (52, 211, 153, 135),   # Emerald Neon Bloom #34D399
        'accent_text': (9, 20, 14, 255),
        'badge_red': (239, 68, 68, 255),
        'surface': (11, 21, 16, 238),         # Deep Forest Obsidian #0B1510
        'card_bg': (16, 33, 24, 242),         # Translucent Dark Mint Card #102118
        'dot_color': (74, 222, 128, 46),      # Dot-matrix background pattern
        'track': (255, 255, 255, 42),
        'muted_bar': (92, 102, 96, 225),
        'border': (74, 222, 128, 210),        # Crisp glowing mint border
        'border_soft': (74, 222, 128, 115),   # Subtle pill border
        'hairline': (74, 222, 128, 52),
        'kicker_text': (216, 232, 223, 255),  # Soft Mint-White lead-in ("Claude cắt thử")
        'text': (248, 252, 249, 255),
        'subtext': (178, 202, 188, 255),
    },
    'cinema_travel': {
        'accent': (74, 222, 128, 255),        # Modern Mint Green #4ADE80
        'accent_glow': (52, 211, 153, 135),
        'accent_text': (9, 20, 14, 255),
        'badge_red': (239, 68, 68, 255),
        'surface': (11, 21, 16, 238),
        'card_bg': (16, 33, 24, 242),
        'dot_color': (74, 222, 128, 46),
        'track': (255, 255, 255, 42),
        'muted_bar': (92, 102, 96, 225),
        'border': (74, 222, 128, 210),
        'border_soft': (74, 222, 128, 115),
        'hairline': (74, 222, 128, 52),
        'kicker_text': (216, 232, 223, 255),
        'text': (248, 252, 249, 255),
        'subtext': (178, 202, 188, 255),
    },
    'anthropic_coral': {
        'accent': (232, 123, 85, 255),        # Official Anthropic Coral Orange #E87B55 / #D97757
        'accent_glow': (232, 123, 85, 135),
        'accent_text': (20, 12, 10, 255),
        'badge_red': (229, 72, 61, 255),
        'surface': (18, 14, 12, 238),         # Warm Carbon Obsidian
        'card_bg': (28, 21, 18, 242),
        'dot_color': (232, 123, 85, 46),
        'track': (255, 245, 238, 42),
        'muted_bar': (108, 98, 94, 225),
        'border': (232, 123, 85, 210),
        'border_soft': (232, 123, 85, 115),
        'hairline': (232, 123, 85, 52),
        'kicker_text': (238, 226, 218, 255),
        'text': (252, 249, 246, 255),
        'subtext': (202, 186, 178, 255),
    },
    'vibrant_vlog': {
        'accent': (232, 123, 85, 255),        # Anthropic Coral Orange #E87B55
        'accent_glow': (232, 123, 85, 135),
        'accent_text': (20, 12, 10, 255),
        'badge_red': (229, 72, 61, 255),
        'surface': (18, 14, 12, 238),
        'card_bg': (28, 21, 18, 242),
        'dot_color': (232, 123, 85, 46),
        'track': (255, 245, 238, 42),
        'muted_bar': (108, 98, 94, 225),
        'border': (232, 123, 85, 210),
        'border_soft': (232, 123, 85, 115),
        'hairline': (232, 123, 85, 52),
        'kicker_text': (238, 226, 218, 255),
        'text': (252, 249, 246, 255),
        'subtext': (202, 186, 178, 255),
    },
    'clean_studio': {
        'accent': (56, 189, 248, 255),        # Electric Studio Cyan #38BDF8
        'accent_glow': (56, 189, 248, 135),
        'accent_text': (10, 16, 28, 255),
        'badge_red': (239, 68, 68, 255),
        'surface': (11, 17, 28, 238),
        'card_bg': (17, 26, 42, 242),
        'dot_color': (56, 189, 248, 46),
        'track': (255, 255, 255, 42),
        'muted_bar': (90, 102, 118, 225),
        'border': (56, 189, 248, 210),
        'border_soft': (56, 189, 248, 115),
        'hairline': (56, 189, 248, 52),
        'kicker_text': (218, 232, 246, 255),
        'text': (248, 250, 252, 255),
        'subtext': (178, 194, 214, 255),
    },
    'film_kodak': {
        'accent': (232, 123, 85, 255),        # Anthropic Coral Sienna #E87B55
        'accent_glow': (232, 123, 85, 135),
        'accent_text': (20, 12, 10, 255),
        'badge_red': (229, 72, 61, 255),
        'surface': (18, 14, 12, 238),
        'card_bg': (28, 21, 18, 242),
        'dot_color': (232, 123, 85, 46),
        'track': (255, 245, 238, 42),
        'muted_bar': (108, 98, 94, 225),
        'border': (232, 123, 85, 210),
        'border_soft': (232, 123, 85, 115),
        'hairline': (232, 123, 85, 52),
        'kicker_text': (238, 226, 218, 255),
        'text': (252, 249, 246, 255),
        'subtext': (202, 186, 178, 255),
    },
    'minimal_editorial': {
        'accent': (74, 222, 128, 255),
        'accent_glow': (52, 211, 153, 135),
        'accent_text': (9, 20, 14, 255),
        'badge_red': (239, 68, 68, 255),
        'surface': (12, 18, 15, 238),
        'card_bg': (18, 28, 23, 242),
        'dot_color': (74, 222, 128, 46),
        'track': (255, 255, 255, 42),
        'muted_bar': (92, 102, 96, 225),
        'border': (74, 222, 128, 210),
        'border_soft': (74, 222, 128, 115),
        'hairline': (74, 222, 128, 52),
        'kicker_text': (216, 232, 223, 255),
        'text': (248, 252, 249, 255),
        'subtext': (178, 202, 188, 255),
    },
    'warm_food': {
        'accent': (245, 158, 11, 255),        # Vibrant Amber Gold #F59E0B
        'accent_glow': (245, 158, 11, 135),
        'accent_text': (20, 14, 8, 255),
        'badge_red': (239, 68, 68, 255),
        'surface': (18, 14, 10, 238),
        'card_bg': (28, 22, 15, 242),
        'dot_color': (245, 158, 11, 46),
        'track': (255, 245, 230, 42),
        'muted_bar': (110, 100, 88, 225),
        'border': (245, 158, 11, 210),
        'border_soft': (245, 158, 11, 115),
        'hairline': (245, 158, 11, 52),
        'kicker_text': (242, 232, 216, 255),
        'text': (253, 250, 245, 255),
        'subtext': (206, 192, 174, 255),
    },
}

BANNED_AI_TAG_PATTERNS = re.compile(
    r'\b(minh\s*h[oọ]a\s*ai|ai\s*visuals?|ai\s*generated|[aả]nh\s*ai|t[aạ]o\s*b[oở]i\s*ai)\b',
    re.IGNORECASE,
)


def get_ffmpeg():
    for pf in (
        PLATFORM_FILE,
        os.path.join(os.path.dirname(SKILL_DIR), 'video-edit', '.platform.json'),
    ):
        if os.path.isfile(pf):
            try:
                with open(pf, encoding='utf-8') as fh:
                    ff = json.load(fh).get('ffmpeg')
                    if ff and os.path.isfile(ff):
                        return ff
            except Exception:
                pass
    return shutil.which('ffmpeg') or 'ffmpeg'


FF = get_ffmpeg()


def ease_out_cubic(p):
    p = max(0.0, min(1.0, float(p)))
    return 1.0 - (1.0 - p) ** 3


def ease_out_quint(p):
    p = max(0.0, min(1.0, float(p)))
    return 1.0 - (1.0 - p) ** 5


def ease_in_out_sine(p):
    p = max(0.0, min(1.0, float(p)))
    return 0.5 - 0.5 * math.cos(math.pi * p)


def scale_alpha(img, alpha_factor):
    if alpha_factor >= 0.999:
        return img
    if alpha_factor <= 0.001:
        return Image.new('RGBA', img.size, (0, 0, 0, 0))
    r, g, b, a = img.split()
    a = a.point(lambda v: int(v * alpha_factor))
    return Image.merge('RGBA', (r, g, b, a))


def strip_emoji(text):
    """Normalize Vietnamese NFC and strip all emojis, dingbats, and enclosed symbols so zero emojis ever appear."""
    if not text:
        return ''
    text = unicodedata.normalize('NFC', str(text))
    out = []
    for ch in text:
        cp = ord(ch)
        if (
            cp > 0xFFFF
            or (0x2460 <= cp <= 0x27BF)
            or cp in (0xFE0F, 0xFE0E, 0x200D)
        ):
            continue
        out.append(ch)
    return ' '.join(''.join(out).split())


def clean_kicker(text, fallback='Story Beat'):
    """Format a clean conversational lead-in kicker (never all-caps TV news banner or self-referential AI label)."""
    s = strip_emoji(text)
    if not s:
        return fallback
    s = BANNED_AI_TAG_PATTERNS.sub('', s).strip(' •·-|/')
    if not s:
        return fallback
    s = re.sub(r'\s*[•|]\s*', ' · ', s)
    return s


def load_font(size, weight='bold'):
    bvp_map = {
        'heavy': 'BeVietnamPro-ExtraBold.ttf',
        'bold': 'BeVietnamPro-Bold.ttf',
        'demi': 'BeVietnamPro-SemiBold.ttf',
        'medium': 'BeVietnamPro-Medium.ttf',
        'regular': 'BeVietnamPro-Medium.ttf',
    }
    bvp_path = os.path.join(FONTS_DIR, bvp_map.get(weight, 'BeVietnamPro-Bold.ttf'))
    if os.path.isfile(bvp_path):
        try:
            return ImageFont.truetype(bvp_path, size)
        except Exception:
            pass
    for fallback in (
        'C:/Windows/Fonts/segoeuib.ttf',
        'C:/Windows/Fonts/segoeui.ttf',
        'C:/Windows/Fonts/arialbd.ttf',
        '/System/Library/Fonts/Avenir Next.ttc',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
    ):
        if os.path.isfile(fallback):
            try:
                return ImageFont.truetype(fallback, size)
            except Exception:
                pass
    return ImageFont.load_default()


# ---------------------------------------------------------------------------
# Modern Dot-Grid + Glowing Border + Condensed Display Primitives
# ---------------------------------------------------------------------------

def draw_dot_grid_region(canvas, box, dot_color, spacing=22, dot_r=1.5, radius=16):
    """Render a regular dot-matrix (`dot background`) inside a rounded rectangle so cards never feel flat or empty."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    if w <= 8 or h <= 8:
        return
    grid_im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grid_im)
    r = max(1, int(round(dot_r)))
    for gy in range(spacing // 2, h - 4, spacing):
        for gx in range(spacing // 2, w - 4, spacing):
            gd.ellipse((gx - r, gy - r, gx + r, gy + r), fill=dot_color)
    mask = Image.new('L', (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, w - 1, h - 1), radius=radius, fill=255)
    clipped = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    clipped.paste(grid_im, (0, 0), mask)
    canvas.alpha_composite(clipped, dest=(x0, y0))


def make_modern_glow_plate(cw, ch, box, theme, radius=16, glow_alpha=125, border_w=2, use_dots=True, soft=False):
    """Dark obsidian/forest plate with dot-grid texture, outer neon border bloom, and crisp 2px glowing stroke."""
    x0, y0, x1, y1 = box
    canvas = Image.new('RGBA', (cw, ch), (0, 0, 0, 0))

    # 1. Deep optical drop shadow
    sh = Image.new('RGBA', (cw, ch), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((x0, y0 + 8, x1, y1 + 10), radius=radius, fill=(0, 0, 0, 145))
    canvas = Image.alpha_composite(canvas, sh.filter(ImageFilter.GaussianBlur(14)))

    # 2. Outer neon border glow (matching the glowing green/coral border in reference image)
    if glow_alpha > 0:
        ac = theme['accent']
        glow_layer = Image.new('RGBA', (cw, ch), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow_layer)
        gd.rounded_rectangle(
            (x0 - 1, y0 - 1, x1 + 1, y1 + 1),
            radius=radius + 1,
            outline=(ac[0], ac[1], ac[2], glow_alpha),
            width=border_w + 3,
        )
        canvas = Image.alpha_composite(canvas, glow_layer.filter(ImageFilter.GaussianBlur(8)))

    # 3. 2x-supersampled dark fill + crisp border
    ss = 2
    hi = Image.new('RGBA', (cw * ss, ch * ss), (0, 0, 0, 0))
    hd = ImageDraw.Draw(hi)
    bx0, by0, bx1, by1 = x0 * ss, y0 * ss, x1 * ss, y1 * ss
    fill_c = theme['card_bg'] if soft else theme['surface']
    hd.rounded_rectangle((bx0, by0, bx1, by1), radius=radius * ss, fill=fill_c)
    plate = hi.resize((cw, ch), Image.LANCZOS)
    canvas = Image.alpha_composite(canvas, plate)

    # 4. Dot-grid texture inside the card
    if use_dots:
        draw_dot_grid_region(canvas, (x0, y0, x1, y1), theme['dot_color'], spacing=22, dot_r=1.5, radius=radius)

    # 5. Crisp 2x-supersampled border stroke on top
    hi_b = Image.new('RGBA', (cw * ss, ch * ss), (0, 0, 0, 0))
    stroke_c = theme['border_soft'] if soft else theme['border']
    ImageDraw.Draw(hi_b).rounded_rectangle(
        (bx0, by0, bx1, by1), radius=radius * ss, outline=stroke_c, width=border_w * ss
    )
    canvas = Image.alpha_composite(canvas, hi_b.resize((cw, ch), Image.LANCZOS))
    return canvas


def draw_brand_spark_badge(canvas, x, y, theme, size=24):
    """Draw the sleek Anthropic/Claude-style vector spark badge (rounded accent square + 10-ray geometric spark)."""
    ss = 2
    s2 = size * ss
    hi = Image.new('RGBA', (s2, s2), (0, 0, 0, 0))
    hd = ImageDraw.Draw(hi)
    ac = theme['accent']
    hd.rounded_rectangle((0, 0, s2 - 1, s2 - 1), radius=int(size * 0.26 * ss), fill=ac)
    cx, cy = s2 / 2.0, s2 / 2.0
    rays = [
        (-0.08, -0.76), (0.38, -0.52), (0.76, -0.16), (0.68, 0.18), (0.48, 0.68),
        (-0.06, 0.62), (-0.44, 0.68), (-0.66, 0.22), (-0.74, -0.32), (-0.42, -0.50),
    ]
    r_len = s2 * 0.34
    for rx, ry in rays:
        hd.line((cx, cy, cx + rx * r_len, cy + ry * r_len), fill=(255, 255, 255, 245), width=max(2, int(ss * 1.9)))
    badge = hi.resize((size, size), Image.LANCZOS)
    canvas.alpha_composite(badge, dest=(x, y))


def draw_circle_number_badge(canvas, cx, cy, num_text, theme, radius=21):
    """Draw the circular outlined number badge (1, 2, 3) from the reference image's right-side pill stack."""
    ss = 2
    d_px = (radius * 2 + 8) * ss
    hi = Image.new('RGBA', (d_px, d_px), (0, 0, 0, 0))
    hd = ImageDraw.Draw(hi)
    c_mid = d_px // 2
    r_ss = radius * ss
    ac = theme['accent']
    hd.ellipse(
        (c_mid - r_ss, c_mid - r_ss, c_mid + r_ss, c_mid + r_ss),
        fill=(ac[0], ac[1], ac[2], 24),
        outline=ac,
        width=int(2.4 * ss),
    )
    f_num = load_font(int(radius * 1.02 * ss), 'heavy')
    hd.text((c_mid, c_mid), str(num_text), font=f_num, fill=ac, anchor='mm')
    badge = hi.resize((radius * 2 + 8, radius * 2 + 8), Image.LANCZOS)
    canvas.alpha_composite(badge, dest=(cx - radius - 4, cy - radius - 4))


def make_condensed_display_strip(text, font_size, theme, condense_x=0.83, with_glow=True):
    """Render bold condensed uppercase display typography ('& DỰNG STORYBOARD') with tight ink bounds."""
    txt = strip_emoji(text).upper()
    if not txt:
        return Image.new('RGBA', (8, 8), (0, 0, 0, 0))
    render_size = int(round(font_size * 1.15))
    f = load_font(render_size, 'heavy')
    dummy = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    bb = ImageDraw.Draw(dummy).textbbox((0, 0), txt, font=f)
    ink_w = max(8, bb[2] - bb[0])
    ink_h = max(8, bb[3] - bb[1])

    raw_w = ink_w + 12
    raw_h = ink_h + 10
    raw = Image.new('RGBA', (raw_w, raw_h), (0, 0, 0, 0))
    rd = ImageDraw.Draw(raw)
    rd.text((6 - bb[0], 5 - bb[1]), txt, font=f, fill=theme['accent'])

    cond_w = max(8, int(round(raw_w * condense_x)))
    condensed = raw.resize((cond_w, raw_h), Image.LANCZOS)

    if not with_glow:
        return condensed

    out = Image.new('RGBA', (cond_w + 12, raw_h + 10), (0, 0, 0, 0))
    ac = theme['accent']
    glow_im = Image.new('RGBA', condensed.size, (ac[0], ac[1], ac[2], 0))
    _, _, _, a = condensed.split()
    glow_a = a.point(lambda v: int(v * 0.34))
    glow_im.putalpha(glow_a)
    out.alpha_composite(glow_im, dest=(6, 5))
    out = out.filter(ImageFilter.GaussianBlur(5))
    out.alpha_composite(condensed, dest=(6, 5))
    return out


def draw_glowing_underline(canvas, x0, y0, width, theme, thickness=5):
    """Draw the thick glowing underline bar directly beneath a condensed display headline."""
    if width <= 4:
        return
    ac = theme['accent']
    glow = Image.new('RGBA', (width + 24, thickness + 24), (0, 0, 0, 0))
    ImageDraw.Draw(glow).rounded_rectangle(
        (12, 12, 12 + width, 12 + thickness),
        radius=max(2, thickness // 2),
        fill=(ac[0], ac[1], ac[2], 140),
    )
    glow = glow.filter(ImageFilter.GaussianBlur(5))
    ImageDraw.Draw(glow).rounded_rectangle(
        (12, 12, 12 + width, 12 + thickness),
        radius=max(2, thickness // 2),
        fill=ac,
    )
    canvas.alpha_composite(glow, dest=(x0 - 12, y0 - 12))


def make_text_strip(text, font, fill, pad_y=6):
    """Pre-render a single line of typography onto a tight RGBA strip for masked baseline reveals."""
    dummy = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    bb = ImageDraw.Draw(dummy).textbbox((0, 0), text, font=font)
    w = max(4, (bb[2] - bb[0]) + 10)
    h = max(4, (bb[3] - bb[1]) + pad_y * 2)
    strip = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(strip).text((2 - bb[0], pad_y - bb[1]), text, font=font, fill=fill)
    return strip


def paste_masked_reveal(canvas, strip, dest_xy, progress, align='left'):
    """Overflow:hidden baseline mask reveal with quintic deceleration."""
    if progress <= 0.01 or strip is None:
        return
    e = ease_out_quint(progress)
    sw, sh = strip.size
    x, y = dest_xy
    if align == 'center':
        x = int(round(x - sw / 2.0))
    elif align == 'right':
        x = int(round(x - sw))
    dy = int(round((1.0 - e) * sh * 0.88))
    if dy <= 0 and e >= 0.995:
        canvas.alpha_composite(strip, dest=(x, y))
        return
    window = Image.new('RGBA', (sw, sh), (0, 0, 0, 0))
    faded = scale_alpha(strip, min(1.0, progress * 1.45))
    window.alpha_composite(faded, dest=(0, dy))
    canvas.alpha_composite(window, dest=(x, y))


def encode_rgba_motion(w, h, dur, frame_fn, mov_path, png_path, peak_ratio=0.72):
    """Pipe RGBA frames from frame_fn(t, dur) into lossless QuickTime Animation (qtrle argb) .mov + peak .png."""
    total_dur = max(1.5, float(dur)) + 0.15
    n_frames = max(2, int(round(total_dur * MOTION_FPS)))
    peak_idx = min(n_frames - 1, max(0, int(round((total_dur - 0.15) * peak_ratio * MOTION_FPS))))

    try:
        proc = subprocess.Popen([
            FF, '-loglevel', 'error', '-y',
            '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{w}x{h}', '-r', str(MOTION_FPS), '-i', '-',
            '-c:v', 'qtrle', '-pix_fmt', 'argb', mov_path
        ], stdin=subprocess.PIPE)
        for i in range(n_frames):
            t = i / float(MOTION_FPS)
            frame = frame_fn(t, total_dur - 0.15)
            if i == peak_idx:
                frame.save(png_path, 'PNG')
            proc.stdin.write(frame.tobytes())
        proc.stdin.close()
        rc = proc.wait()
        if rc == 0 and os.path.isfile(mov_path):
            if not os.path.isfile(png_path):
                frame_fn((total_dur - 0.15) * peak_ratio, total_dur - 0.15).save(png_path, 'PNG')
            return mov_path
    except Exception:
        pass

    peak_frame = frame_fn((total_dur - 0.15) * peak_ratio, total_dur - 0.15)
    peak_frame.save(png_path, 'PNG')
    return None


def prepare_optical_image(src_im, target_w, target_h):
    im = src_im.convert('RGB')
    im = ImageEnhance.Color(im).enhance(0.92)
    im = ImageEnhance.Contrast(im).enhance(0.98)
    im = im.convert('RGBA')
    scale_k = max(target_w / max(1, im.width), target_h / max(1, im.height))
    pw, ph = max(target_w, int(im.width * scale_k)), max(target_h, int(im.height * scale_k))
    return im.resize((pw, ph), Image.LANCZOS)


def make_editorial_placeholder(vw, vh, theme, title_hint=''):
    im = Image.new('RGBA', (vw, vh), theme['surface'])
    draw_dot_grid_region(im, (0, 0, vw, vh), theme['dot_color'], spacing=22, dot_r=1.5, radius=12)
    if title_hint:
        f = load_font(20, 'demi')
        ImageDraw.Draw(im).text((32, vh - 44), strip_emoji(title_hint)[:32], font=f, fill=theme['subtext'])
    return im


# ---------------------------------------------------------------------------
# 1. Modern Two-Tier Display Lockup Intro (`intro`)
#    Matches "Claude cắt thử / & DỰNG STORYBOARD" + glowing underline + dot-grid plate
# ---------------------------------------------------------------------------

def build_modern_intro(ov, theme, dur, mov_path, png_path):
    kicker = clean_kicker(ov.get('badge', 'Daily Vlog'), 'Daily Vlog')
    raw_title = strip_emoji(ov.get('title', '')).upper()
    title = f'& {raw_title}' if (raw_title and not raw_title.startswith('&')) else raw_title
    subtitle = strip_emoji(ov.get('subtitle', ''))

    f_kicker = load_font(26, 'demi')
    f_sub = load_font(22, 'bold')
    kicker_strip = make_text_strip(kicker, f_kicker, theme['kicker_text'], pad_y=4)
    head_strip = make_condensed_display_strip(title, 58 if len(title) <= 28 else 48, theme, condense_x=0.83)
    sub_strip = make_text_strip(subtitle, f_sub, theme['text'], pad_y=4) if subtitle else None

    pad = 24
    head_w = head_strip.width - 12
    head_y = 58
    line_y = head_y + head_strip.height + 2
    sub_y = line_y + 16
    card_w = min(1340, max(640, head_w + 76, (sub_strip.width if sub_strip else 0) + 120))
    card_h = (sub_y + 52) if sub_strip else (line_y + 24)
    cw, ch = card_w + pad * 2, card_h + pad * 2

    ox, oy = 88 - pad, (1010 - card_h) - pad
    shell = make_modern_glow_plate(cw, ch, (pad, pad, pad + card_w, pad + card_h), theme, radius=18, border_w=2)

    def frame_fn(t, _total_d):
        frame = shell.copy()
        if t > 0.04:
            kp = ease_out_cubic((t - 0.04) / 0.36)
            kl = Image.new('RGBA', (card_w - 40, 40), (0, 0, 0, 0))
            draw_brand_spark_badge(kl, 0, 6, theme, size=24)
            kl.alpha_composite(kicker_strip, dest=(36, 2))
            frame.alpha_composite(scale_alpha(kl, kp), dest=(pad + 28, pad + 18))

        if t > 0.10:
            paste_masked_reveal(frame, head_strip, (pad + 22, pad + head_y), (t - 0.10) / 0.48)

        bar_e = ease_out_quint(max(0.0, (t - 0.20) / 0.52))
        bar_w = int(head_w * bar_e)
        if bar_w > 8:
            draw_glowing_underline(frame, pad + 28, pad + line_y, bar_w, theme, thickness=5)

        if sub_strip and t > 0.28:
            sp = ease_out_cubic((t - 0.28) / 0.42)
            sl = Image.new('RGBA', (card_w - 48, 48), (0, 0, 0, 0))
            draw_circle_number_badge(sl, 18, 22, '1', theme, radius=16)
            sl.alpha_composite(sub_strip, dest=(46, 6))
            frame.alpha_composite(scale_alpha(sl, sp), dest=(pad + 28, pad + sub_y))
        return frame

    vid = encode_rgba_motion(cw, ch, dur, frame_fn, mov_path, png_path, peak_ratio=0.68)
    return {'video': vid, 'png': png_path, 'x': ox, 'y': oy}


# ---------------------------------------------------------------------------
# 2. Modern Chapter Lockup (`chapter`)
#    Circular number badge ①/② + Condensed Display Headline + Glowing Underline
# ---------------------------------------------------------------------------

def build_modern_chapter(ov, theme, dur, mov_path, png_path):
    raw_num = strip_emoji(ov.get('number', '1')).lstrip('0') or '1'
    title = strip_emoji(ov.get('title', '')).upper()
    disp_title = f'& {title}' if (title and not title.startswith('&')) else title
    sub = strip_emoji(ov.get('subtitle', ''))
    kicker = clean_kicker(ov.get('badge') or f'Phần {raw_num} · Hành trình thực tế')

    f_kicker = load_font(23, 'demi')
    f_sub = load_font(20, 'medium')
    kicker_strip = make_text_strip(kicker, f_kicker, theme['kicker_text'], pad_y=4)
    head_strip = make_condensed_display_strip(disp_title, 48 if len(disp_title) <= 30 else 42, theme, condense_x=0.83)
    sub_strip = make_text_strip(f'•  {sub}', f_sub, theme['text'], pad_y=4) if sub else None

    pad = 24
    head_w = head_strip.width - 12
    head_y = 54
    line_y = head_y + head_strip.height + 2
    sub_y = line_y + 14
    card_w = min(1220, max(540, head_w + 72, (sub_strip.width if sub_strip else 0) + 72))
    card_h = (sub_y + 42) if sub_strip else (line_y + 22)
    cw, ch = card_w + pad * 2, card_h + pad * 2
    ox, oy = 88 - pad, (940 - card_h) - pad

    shell = make_modern_glow_plate(cw, ch, (pad, pad, pad + card_w, pad + card_h), theme, radius=16, border_w=2)

    def frame_fn(t, _total_d):
        frame = shell.copy()
        if t > 0.04:
            kp = ease_out_cubic((t - 0.04) / 0.36)
            kl = Image.new('RGBA', (card_w - 48, 42), (0, 0, 0, 0))
            draw_circle_number_badge(kl, 18, 20, raw_num[:2], theme, radius=16)
            kl.alpha_composite(kicker_strip, dest=(46, 4))
            frame.alpha_composite(scale_alpha(kl, kp), dest=(pad + 26, pad + 14))

        if t > 0.10:
            paste_masked_reveal(frame, head_strip, (pad + 20, pad + head_y), (t - 0.10) / 0.46)

        bar_e = ease_out_quint(max(0.0, (t - 0.18) / 0.50))
        bar_w = int(head_w * bar_e)
        if bar_w > 6:
            draw_glowing_underline(frame, pad + 26, pad + line_y, bar_w, theme, thickness=4)

        if sub_strip and t > 0.25:
            paste_masked_reveal(frame, sub_strip, (pad + 26, pad + sub_y), (t - 0.25) / 0.44)
        return frame

    vid = encode_rgba_motion(cw, ch, dur, frame_fn, mov_path, png_path)
    return {'video': vid, 'png': png_path, 'x': ox, 'y': oy}


# ---------------------------------------------------------------------------
# 3. Modern Lower-Third + Mini Glowing Bar Chart (`lower_third`)
# ---------------------------------------------------------------------------

def build_modern_lower_third(ov, theme, dur, mov_path, png_path):
    cat = clean_kicker(ov.get('category', 'Ghi chú thực tế'), 'Trải nghiệm')
    title = strip_emoji(ov.get('title', '')).upper()
    loc = strip_emoji(ov.get('location', ''))
    price = strip_emoji(ov.get('price', ''))
    rating = strip_emoji(ov.get('rating', ''))

    f_kicker = load_font(22, 'demi')
    f_meta = load_font(20, 'medium')
    kicker_strip = make_text_strip(cat, f_kicker, theme['kicker_text'], pad_y=4)
    head_strip = make_condensed_display_strip(title, 46 if len(title) <= 28 else 38, theme, condense_x=0.84)

    bullets = [b for b in (loc, price) if b]
    bullet_str = '   ·   '.join(bullets)
    meta_strip = make_text_strip(f'•  {bullet_str}', f_meta, theme['text'], pad_y=4) if bullet_str else None

    has_chart = bool(rating)
    score_ratio = 0.88
    if '/' in rating:
        try:
            num_s, den_s = rating.split('/', 1)
            score_ratio = max(0.18, min(1.0, float(num_s.strip()) / max(1.0, float(den_s.strip()))))
        except Exception:
            score_ratio = 0.85

    pad = 24
    chart_w = 190 if has_chart else 0
    head_w = head_strip.width - 12
    head_y = 50
    line_y = head_y + head_strip.height + 2
    meta_y = line_y + 14
    text_w = max(460, head_w, (meta_strip.width if meta_strip else 0))
    card_w = min(1320, text_w + 68 + chart_w)
    card_h = max(176 if has_chart else 148, (meta_y + 42) if meta_strip else (line_y + 22))
    cw, ch = card_w + pad * 2, card_h + pad * 2
    ox, oy = 88 - pad, (940 - card_h) - pad

    shell = make_modern_glow_plate(cw, ch, (pad, pad, pad + card_w, pad + card_h), theme, radius=16, border_w=2)

    def frame_fn(t, _total_d):
        frame = shell.copy()
        fd = ImageDraw.Draw(frame)

        if t > 0.04:
            kp = ease_out_cubic((t - 0.04) / 0.36)
            kl = Image.new('RGBA', (card_w - chart_w - 40, 36), (0, 0, 0, 0))
            draw_brand_spark_badge(kl, 0, 5, theme, size=22)
            kl.alpha_composite(kicker_strip, dest=(32, 2))
            frame.alpha_composite(scale_alpha(kl, kp), dest=(pad + 26, pad + 14))

        if t > 0.10:
            paste_masked_reveal(frame, head_strip, (pad + 20, pad + head_y), (t - 0.10) / 0.46)

        bar_e = ease_out_quint(max(0.0, (t - 0.18) / 0.50))
        bar_w = int(min(head_w, card_w - chart_w - 52) * bar_e)
        if bar_w > 6:
            draw_glowing_underline(frame, pad + 26, pad + line_y, bar_w, theme, thickness=4)

        if meta_strip and t > 0.24:
            paste_masked_reveal(frame, meta_strip, (pad + 26, pad + meta_y), (t - 0.24) / 0.44)

        if has_chart and t > 0.22:
            ce = ease_out_quint((t - 0.22) / 0.52)
            cx0 = pad + card_w - chart_w + 10
            cy0, cy1 = pad + 16, pad + card_h - 16
            sub_box = (cx0, cy0, pad + card_w - 16, cy1)
            fd.rounded_rectangle(sub_box, radius=12, fill=(9, 14, 11, 220), outline=theme['border_soft'], width=1)

            base_y = cy1 - 26
            max_bh = max(36, (cy1 - cy0) - 62)
            b1_h = max(10, int(max_bh * (0.72 if score_ratio < 0.35 else 0.32) * ce))
            bx1 = cx0 + 32
            fd.rounded_rectangle((bx1, base_y - b1_h, bx1 + 38, base_y), radius=4, fill=theme['muted_bar'])

            b2_h = max(12, int(max_bh * max(0.24, score_ratio) * ce))
            bx2 = cx0 + 84
            ac = theme['accent']
            glow_b = Image.new('RGBA', (66, b2_h + 24), (0, 0, 0, 0))
            ImageDraw.Draw(glow_b).rounded_rectangle((12, 12, 54, 12 + b2_h), radius=5, fill=(ac[0], ac[1], ac[2], 150))
            glow_b = glow_b.filter(ImageFilter.GaussianBlur(6))
            ImageDraw.Draw(glow_b).rounded_rectangle((12, 12, 54, 12 + b2_h), radius=5, fill=ac)
            frame.alpha_composite(glow_b, dest=(bx2 - 12, base_y - b2_h - 12))

            fd = ImageDraw.Draw(frame)
            fd.line((cx0 + 16, base_y, sub_box[2] - 16, base_y), fill=theme['hairline'], width=1)
            fd.text(((cx0 + sub_box[2]) // 2, cy0 + 16), rating, font=load_font(19, 'heavy'), fill=ac, anchor='mm')
            fd.text(((cx0 + sub_box[2]) // 2, cy1 - 13), 'THỰC TẾ', font=load_font(11, 'bold'), fill=theme['subtext'], anchor='mm')
        return frame

    vid = encode_rgba_motion(cw, ch, dur, frame_fn, mov_path, png_path)
    return {'video': vid, 'png': png_path, 'x': ox, 'y': oy}


# ---------------------------------------------------------------------------
# 4. Glowing Neon-Border Callout Box (`callout`)
# ---------------------------------------------------------------------------

def build_modern_callout(ov, theme, dur, mov_path, png_path):
    pos = (ov.get('position') or 'top_right').lower()
    kicker = clean_kicker(ov.get('icon', 'Ghi chú'), 'Ghi chú')
    title = strip_emoji(ov.get('title', 'Điểm chú ý')).upper()
    text = strip_emoji(ov.get('text', ''))
    bullets = [strip_emoji(x) for x in (ov.get('items') or []) if strip_emoji(x)]
    if not bullets and text:
        bullets = [p.strip() for p in re.split(r'[•·\n]+', text) if p.strip()]

    f_kicker = load_font(20, 'demi')
    f_bullet = load_font(21, 'medium')
    head_strip = make_condensed_display_strip(title, 38, theme, condense_x=0.84)

    wrapped_bullets = [textwrap.wrap(b, width=42)[:2] for b in bullets[:3]]

    pad = 24
    head_y = 44
    line_y = head_y + head_strip.height + 2
    bullets_y0 = line_y + 14
    card_w = max(580, min(740, head_strip.width + 64))
    total_lines = sum(len(wb) for wb in wrapped_bullets)
    card_h = bullets_y0 + total_lines * 29 + max(0, len(wrapped_bullets) - 1) * 8 + 18
    cw, ch = card_w + pad * 2, card_h + pad * 2
    ox = (1920 - 88 - card_w - pad) if pos == 'top_right' else (88 - pad)
    oy = 78 - pad

    shell = make_modern_glow_plate(cw, ch, (pad, pad, pad + card_w, pad + card_h), theme, radius=14, glow_alpha=155, border_w=2)

    def frame_fn(t, _total_d):
        frame = shell.copy()
        fd = ImageDraw.Draw(frame)
        if t > 0.04:
            draw_brand_spark_badge(frame, pad + 24, pad + 16, theme, size=20)
            fd.text((pad + 52, pad + 14), kicker, font=f_kicker, fill=theme['kicker_text'])
        if t > 0.08:
            paste_masked_reveal(frame, head_strip, (pad + 18, pad + head_y), (t - 0.08) / 0.42)
            bw = int((head_strip.width - 12) * ease_out_quint((t - 0.14) / 0.45))
            if bw > 6:
                draw_glowing_underline(frame, pad + 24, pad + line_y, bw, theme, thickness=3)

        by = pad + bullets_y0
        for b_idx, wb in enumerate(wrapped_bullets):
            t0 = 0.18 + b_idx * 0.12
            if t > t0:
                alpha_k = ease_out_cubic((t - t0) / 0.35)
                bl = Image.new('RGBA', (card_w - 48, len(wb) * 29 + 4), (0, 0, 0, 0))
                bd = ImageDraw.Draw(bl)
                bd.text((0, 0), '•', font=load_font(23, 'heavy'), fill=theme['accent'])
                for li, ln in enumerate(wb):
                    bd.text((22, li * 28), ln, font=f_bullet, fill=theme['text'])
                frame.alpha_composite(scale_alpha(bl, alpha_k), dest=(pad + 24, by))
            by += len(wb) * 29 + 8
        return frame

    vid = encode_rgba_motion(cw, ch, dur, frame_fn, mov_path, png_path)
    return {'video': vid, 'png': png_path, 'x': ox, 'y': oy}


# ---------------------------------------------------------------------------
# 5. Modern Subscribe CTA Pill (`subscribe`)
# ---------------------------------------------------------------------------

def build_modern_subscribe(ov, theme, cfg, dur, mov_path, png_path):
    channel = strip_emoji(ov.get('channel') or cfg.get('channelName') or 'Tuấn Đi Review')
    handle = strip_emoji(ov.get('handle') or cfg.get('channelHandle') or '@tuandireview · Đăng ký kênh')
    btn_txt = strip_emoji(ov.get('button_text') or 'ĐĂNG KÝ').upper()

    f_ch = load_font(30, 'heavy')
    f_hd = load_font(20, 'medium')
    f_btn = load_font(20, 'heavy')

    pad = 24
    card_w = 880
    card_h = 116
    cw, ch = card_w + pad * 2, card_h + pad * 2
    ox, oy = (1920 - cw) // 2, 820 - pad

    shell = make_modern_glow_plate(cw, ch, (pad, pad, pad + card_w, pad + card_h), theme, radius=18, border_w=2)

    def frame_fn(t, _total_d):
        frame = shell.copy()
        fd = ImageDraw.Draw(frame)
        draw_circle_number_badge(frame, pad + 52, pad + card_h // 2, 'YT', theme, radius=26)
        fd.text((pad + 98, pad + 24), channel, font=f_ch, fill=theme['text'])
        fd.text((pad + 98, pad + 64), handle, font=f_hd, fill=theme['subtext'])

        btn_w = 184
        bx0, by0 = pad + card_w - btn_w - 24, pad + 26
        bx1, by1 = pad + card_w - 24, pad + card_h - 26
        ac = theme['accent']
        fd.rounded_rectangle((bx0, by0, bx1, by1), radius=12, fill=ac)
        fd.text(((bx0 + bx1) // 2, (by0 + by1) // 2), btn_txt, font=f_btn, fill=theme['accent_text'], anchor='mm')
        return frame

    vid = encode_rgba_motion(cw, ch, dur, frame_fn, mov_path, png_path)
    return {'video': vid, 'png': png_path, 'x': ox, 'y': oy}


# ---------------------------------------------------------------------------
# 6. Modern Picture-in-Picture Window Frame (`visual_card`)
# ---------------------------------------------------------------------------

def build_motion_visual_card(ov, theme, proj, dur, mov_path, png_path):
    pos = (ov.get('position') or 'right').lower()
    tag = clean_kicker(ov.get('tag') or ov.get('category') or 'Visual Preview', fallback='Góc quay chi tiết')
    title = strip_emoji(ov.get('title') or '').upper()
    caption = strip_emoji(ov.get('caption') or ov.get('text') or '')

    head_strip = make_condensed_display_strip(title, 36, theme, condense_x=0.84) if title else None
    pad = 24
    bezel = 16
    header_h = 44
    card_w = max(760 if pos == 'center' else 640, (head_strip.width + 56) if head_strip else 640)
    wrapped_cap = textwrap.wrap(caption, width=46 if pos == 'center' else 38)[:2]
    vp_w = card_w - bezel * 2
    vp_h = 390 if pos == 'center' else 348
    footer_h = ((head_strip.height + 16) if head_strip else 0) + len(wrapped_cap) * 28 + 26
    card_h = header_h + vp_h + max(64, footer_h)

    cw, ch = card_w + pad * 2, card_h + pad * 2
    if pos == 'left':
        ox = 88 - pad
    elif pos == 'center':
        ox = (1920 - cw) // 2
    else:
        ox = 1920 - 88 - card_w - pad
    oy = 118 - pad

    img_rel = ov.get('image') or ov.get('src') or ''
    img_abs = os.path.join(proj, img_rel) if (img_rel and not os.path.isabs(img_rel)) else img_rel
    if img_abs and os.path.isfile(img_abs):
        try:
            src_im = prepare_optical_image(Image.open(img_abs), int(vp_w * 1.14), int(vp_h * 1.14))
        except Exception:
            src_im = make_editorial_placeholder(int(vp_w * 1.14), int(vp_h * 1.14), theme, title)
    else:
        src_im = make_editorial_placeholder(int(vp_w * 1.14), int(vp_h * 1.14), theme, title)

    pre_w, pre_h = src_im.size
    vp_mask = Image.new('L', (vp_w, vp_h), 0)
    ImageDraw.Draw(vp_mask).rounded_rectangle((0, 0, vp_w - 1, vp_h - 1), radius=10, fill=255)

    shell = make_modern_glow_plate(cw, ch, (pad, pad, pad + card_w, pad + card_h), theme, radius=16, border_w=2)
    sd = ImageDraw.Draw(shell)
    for idx_dot, dot_c in enumerate(((255, 95, 87, 180), (254, 188, 46, 180), (40, 200, 64, 180))):
        dx = pad + 20 + idx_dot * 18
        dy = pad + 17
        sd.ellipse((dx, dy, dx + 10, dy + 10), fill=dot_c)
    draw_brand_spark_badge(shell, pad + 82, pad + 12, theme, size=20)
    sd.text((pad + 110, pad + 11), tag, font=load_font(18, 'bold'), fill=theme['kicker_text'])

    f_cap = load_font(20, 'medium')

    def frame_fn(t, total_d):
        p = ease_in_out_sine(t / max(0.5, total_d))
        cur_zoom = 1.0 + 0.065 * p
        crop_w = min(pre_w, max(16, int(round(vp_w / cur_zoom * 1.10))))
        crop_h = min(pre_h, max(16, int(round(vp_h / cur_zoom * 1.10))))
        cx0 = int(max(0, pre_w - crop_w) * (0.40 + 0.22 * p))
        cy0 = int(max(0, pre_h - crop_h) * (0.50 - 0.10 * p))
        cropped = src_im.crop((cx0, cy0, cx0 + crop_w, cy0 + crop_h)).resize((vp_w, vp_h), Image.BICUBIC)

        frame = shell.copy()
        frame.paste(cropped, (pad + bezel, pad + header_h), vp_mask)
        fd = ImageDraw.Draw(frame)
        fd.rounded_rectangle(
            (pad + bezel, pad + header_h, pad + bezel + vp_w, pad + header_h + vp_h),
            radius=10, outline=theme['border_soft'], width=1
        )

        fy = pad + header_h + vp_h + 12
        if head_strip and t > 0.10:
            paste_masked_reveal(frame, head_strip, (pad + 16, fy), (t - 0.10) / 0.45)
            fy += head_strip.height + 10
        if wrapped_cap and t > 0.20:
            for idx_l, ln in enumerate(wrapped_cap):
                fd.text((pad + 22, fy + idx_l * 26), f'•  {ln}' if idx_l == 0 else f'   {ln}', font=f_cap, fill=theme['text'])
        return frame

    vid = encode_rgba_motion(cw, ch, dur, frame_fn, mov_path, png_path)
    return {'video': vid, 'png': png_path, 'x': ox, 'y': oy}


# ---------------------------------------------------------------------------
# 7. Modern Bar-Chart & Telemetry Card (`stat_card`)
#    Matches the "TỰ EDIT TRÊN CAPCUT" glowing vertical bar-chart card in the reference image
# ---------------------------------------------------------------------------

def parse_stat_value(val_str):
    s = strip_emoji(val_str or '100%')
    m = re.match(r'^([^\d-]*)(-?\d[\d.,]*)(.*)$', s)
    if not m:
        return '', None, 0, False, s
    prefix, num_part, suffix = m.group(1), m.group(2), m.group(3)
    if re.match(r'^-?\d{1,3}(\.\d{3})+$', num_part):
        return prefix, float(num_part.replace('.', '')), 0, True, suffix
    clean = num_part.replace(',', '.')
    try:
        val = float(clean)
    except ValueError:
        return '', None, 0, False, s
    decimals = len(clean.split('.')[1]) if '.' in clean else 0
    return prefix, val, min(2, decimals), False, suffix


def format_stat_number(prefix, val, decimals, use_dot_thousands, suffix):
    if use_dot_thousands:
        formatted = f'{int(round(val)):,}'.replace(',', '.')
    elif decimals > 0:
        formatted = f'{val:.{decimals}f}'
    else:
        formatted = str(int(round(val)))
    return f'{prefix}{formatted}{suffix}'


def build_motion_stat_card(ov, theme, dur, mov_path, png_path):
    """Modern dot-grid stat card with condensed display header + glowing 2-bar vertical comparison chart."""
    pos = (ov.get('position') or 'right').lower()
    tag = clean_kicker(ov.get('tag') or ov.get('category') or 'So sánh thực tế', 'Chỉ số')
    raw_val = str(ov.get('value') or ov.get('metric') or '92%')
    label = strip_emoji(ov.get('label') or ov.get('title') or '').upper()
    subtext = strip_emoji(ov.get('subtext') or ov.get('text') or '')

    prefix, target_num, decimals, use_dots, suffix = parse_stat_value(raw_val)
    if 'progress' in ov and ov['progress'] is not None:
        prog_target = max(0.12, min(1.0, float(ov['progress'])))
    elif target_num is not None and '%' in suffix and 0 < target_num <= 100:
        prog_target = max(0.15, target_num / 100.0)
    elif target_num is not None and '/10' in suffix and 0 < target_num <= 10:
        prog_target = max(0.15, target_num / 10.0)
    else:
        prog_target = 0.85

    head_strip = make_condensed_display_strip(label or 'CHỈ SỐ THỰC TẾ', 38 if len(label) <= 28 else 32, theme, condense_x=0.84)
    f_val = load_font(72 if len(raw_val) <= 7 else 56, 'heavy')
    f_sub = load_font(19, 'medium')
    wrapped_sub = textwrap.wrap(subtext, width=28)[:3]

    pad = 24
    head_y = 44
    line_y = head_y + head_strip.height + 2
    body_y = line_y + 18
    card_w = max(640, min(780, head_strip.width + 56))
    card_h = body_y + 218
    cw, ch = card_w + pad * 2, card_h + pad * 2

    if pos == 'left':
        ox = 88 - pad
    elif pos == 'center':
        ox = (1920 - cw) // 2
    else:
        ox = 1920 - 88 - card_w - pad
    oy = 190 - pad

    shell = make_modern_glow_plate(cw, ch, (pad, pad, pad + card_w, pad + card_h), theme, radius=16, border_w=2)
    sd = ImageDraw.Draw(shell)
    draw_brand_spark_badge(shell, pad + 26, pad + 16, theme, size=20)
    sd.text((pad + 54, pad + 14), tag, font=load_font(19, 'demi'), fill=theme['kicker_text'])

    count_dur = min(1.20, max(0.65, dur * 0.45))

    def frame_fn(t, _total_d):
        e = ease_out_quint(t / count_dur)
        frame = shell.copy()
        paste_masked_reveal(frame, head_strip, (pad + 20, pad + head_y), t / 0.42)
        draw_glowing_underline(frame, pad + 26, pad + line_y, int((head_strip.width - 12) * e), theme, thickness=4)

        fd = ImageDraw.Draw(frame)
        disp = format_stat_number(prefix, target_num * e, decimals, use_dots, suffix) if target_num is not None else strip_emoji(raw_val)
        fd.text((pad + 26, pad + body_y), disp, font=f_val, fill=theme['text'])

        sy = pad + body_y + 98
        for idx_s, ln in enumerate(wrapped_sub):
            fd.text((pad + 26, sy + idx_s * 26), f'•  {ln}' if idx_s == 0 else f'   {ln}', font=f_sub, fill=theme['subtext'])

        # Right side: Mini vertical 2-bar chart positioned cleanly below the headline underline
        chart_x0 = pad + card_w - 234
        chart_y0 = pad + body_y
        chart_y1 = pad + card_h - 20
        fd.rounded_rectangle(
            (chart_x0, chart_y0, pad + card_w - 24, chart_y1),
            radius=12, fill=(9, 14, 11, 220), outline=theme['border_soft'], width=1
        )
        base_y = chart_y1 - 32
        max_h = max(36, (chart_y1 - chart_y0) - 56)

        b1_ratio = 0.78 if prog_target < 0.35 else 0.32
        b1_h = max(10, int(max_h * b1_ratio * e))
        bx1 = chart_x0 + 36
        fd.rounded_rectangle((bx1, base_y - b1_h, bx1 + 48, base_y), radius=5, fill=theme['muted_bar'])

        b2_ratio = max(0.22, prog_target)
        b2_h = max(12, int(max_h * b2_ratio * e))
        bx2 = chart_x0 + 110
        ac = theme['accent']
        glow_bar = Image.new('RGBA', (76, b2_h + 28), (0, 0, 0, 0))
        ImageDraw.Draw(glow_bar).rounded_rectangle((14, 14, 62, 14 + b2_h), radius=6, fill=(ac[0], ac[1], ac[2], 160))
        glow_bar = glow_bar.filter(ImageFilter.GaussianBlur(7))
        ImageDraw.Draw(glow_bar).rounded_rectangle((14, 14, 62, 14 + b2_h), radius=6, fill=ac)
        frame.alpha_composite(glow_bar, dest=(bx2 - 14, base_y - b2_h - 14))

        fd = ImageDraw.Draw(frame)
        fd.line((chart_x0 + 20, base_y, pad + card_w - 44, base_y), fill=theme['hairline'], width=1)
        fd.text((bx1 + 24, base_y + 14), 'Kỳ vọng', font=load_font(13, 'medium'), fill=theme['subtext'], anchor='mm')
        fd.text((bx2 + 24, base_y + 14), 'Thực tế', font=load_font(13, 'bold'), fill=ac, anchor='mm')
        return frame

    vid = encode_rgba_motion(cw, ch, dur, frame_fn, mov_path, png_path)
    return {'video': vid, 'png': png_path, 'x': ox, 'y': oy}


# ---------------------------------------------------------------------------
# 8. Vertical Stack of Numbered Step Pills (`checklist` / `steps_card`)
#    Exact match for the right-side ① ② ③ rounded pill cards in the reference image
# ---------------------------------------------------------------------------

def build_motion_checklist(ov, theme, dur, mov_path, png_path):
    """Header plate + vertical stack of dark dot-grid rounded pill cards with circular (1) (2) (3) badges."""
    pos = (ov.get('position') or 'right').lower()
    tag = clean_kicker(ov.get('tag') or ov.get('category') or 'Quy trình thực hiện', 'Tóm tắt')
    title = strip_emoji(ov.get('title') or 'Các bước chính').upper()
    raw_items = [strip_emoji(x) for x in (ov.get('items') or []) if strip_emoji(x)][:4]
    if not raw_items:
        raw_items = [strip_emoji(ov.get('text') or 'Chi tiết trải nghiệm thực tế')]
    stagger = float(ov.get('stagger', min(0.48, max(0.24, (dur - 0.9) / max(1, len(raw_items))))))

    head_strip = make_condensed_display_strip(title, 38, theme, condense_x=0.84)
    f_kicker = load_font(19, 'demi')
    f_item = load_font(22, 'bold')

    pad = 24
    card_w = max(580, min(700, head_strip.width + 56))
    pill_h = 100
    pill_gap = 14
    header_card_h = 42 + head_strip.height + 24
    card_h = header_card_h + 16 + len(raw_items) * pill_h + max(0, len(raw_items) - 1) * pill_gap
    cw, ch = card_w + pad * 2, card_h + pad * 2
    ox = (88 - pad) if pos == 'left' else (1920 - 88 - card_w - pad)
    oy = max(80 - pad, (1020 - ch) // 2)

    # Pre-render top header card so it has high contrast over bright outdoor skies/roads
    header_plate = make_modern_glow_plate(
        card_w + 24, header_card_h + 24, (12, 12, 12 + card_w, 12 + header_card_h),
        theme, radius=16, glow_alpha=120, border_w=2
    )
    hd = ImageDraw.Draw(header_plate)
    draw_brand_spark_badge(header_plate, 12 + 22, 12 + 14, theme, size=20)
    hd.text((12 + 50, 12 + 12), tag, font=f_kicker, fill=theme['kicker_text'])
    header_plate.alpha_composite(head_strip, dest=(12 + 16, 12 + 38))
    draw_glowing_underline(
        header_plate, 12 + 22, 12 + 38 + head_strip.height + 2,
        min(card_w - 44, head_strip.width - 12), theme, thickness=4
    )

    # Pre-render each individual rounded pill card (1, 2, 3)
    pill_sprites = []
    for idx, item_txt in enumerate(raw_items):
        pw, ph = card_w, pill_h
        p_im = make_modern_glow_plate(
            pw + 24, ph + 24, (12, 12, 12 + pw, 12 + ph),
            theme, radius=16, glow_alpha=95, border_w=2, soft=True
        )
        draw_circle_number_badge(p_im, 12 + 44, 12 + ph // 2, str(idx + 1), theme, radius=21)
        pd = ImageDraw.Draw(p_im)
        lines = textwrap.wrap(item_txt, width=32)[:2]
        if len(lines) == 1:
            pd.text((12 + 84, 12 + ph // 2 - 14), lines[0], font=f_item, fill=theme['text'])
        else:
            pd.text((12 + 84, 12 + 18), lines[0], font=f_item, fill=theme['text'])
            pd.text((12 + 84, 12 + 50), lines[1], font=f_item, fill=theme['text'])
        pill_sprites.append(p_im)

    def frame_fn(t, _total_d):
        frame = Image.new('RGBA', (cw, ch), (0, 0, 0, 0))
        if t > 0.02:
            hp = ease_out_cubic(t / 0.34)
            frame.alpha_composite(scale_alpha(header_plate, hp), dest=(pad - 12, pad - 12))

        for idx, sp in enumerate(pill_sprites):
            t0 = 0.14 + idx * stagger
            if t < t0:
                continue
            re_p = ease_out_quint((t - t0) / 0.44)
            dx = int(round((1.0 - re_p) * 28))
            py = pad + header_card_h + 16 + idx * (pill_h + pill_gap) - 12
            frame.alpha_composite(scale_alpha(sp, min(1.0, (t - t0) / 0.26)), dest=(pad - 12 + dx, py))
        return frame

    vid = encode_rgba_motion(cw, ch, dur, frame_fn, mov_path, png_path, peak_ratio=0.82)
    return {'video': vid, 'png': png_path, 'x': ox, 'y': oy}


# ---------------------------------------------------------------------------
# 9. Modern Blur-vs-Sharp / Muted-vs-Glowing Split Comparison (`comparison`)
# ---------------------------------------------------------------------------

def build_motion_comparison(ov, theme, dur, mov_path, png_path):
    pos = (ov.get('position') or 'center').lower()
    left_tag = clean_kicker(ov.get('left_tag') or 'Cách cũ (Mờ / Thủ công)', 'Trước đây')
    right_tag = clean_kicker(ov.get('right_tag') or 'Hiện đại (Sắc nét / Chuẩn)', 'Nổi bật')
    left_title = strip_emoji(ov.get('left_title') or 'Bản nháp cũ').upper()
    right_title = strip_emoji(ov.get('right_title') or 'Bản chuẩn hiện đại').upper()
    left_items = [strip_emoji(x) for x in (ov.get('left_items') or []) if strip_emoji(x)][:3]
    right_items = [strip_emoji(x) for x in (ov.get('right_items') or []) if strip_emoji(x)][:3]
    split_delay = float(ov.get('split_delay', 0.55))

    r_head = make_condensed_display_strip(right_title, 34, theme, condense_x=0.84)
    pad = 24
    col_w = max(490 if pos == 'center' else 420, r_head.width + 48)
    gap = 28
    card_w = col_w * 2 + gap
    max_rows = max(1, len(left_items), len(right_items))
    body_y = 54 + r_head.height + 22
    card_h = body_y + max_rows * 62 + 20
    cw, ch = card_w + pad * 2, card_h + pad * 2

    if pos == 'right':
        ox = 1920 - 88 - card_w - pad
    elif pos == 'left':
        ox = 88 - pad
    else:
        ox = (1920 - cw) // 2
    oy = (1000 - ch) // 2

    f_kicker = load_font(19, 'demi')
    f_item = load_font(21, 'medium')

    left_plate = make_modern_glow_plate(
        col_w + 24, card_h + 24, (12, 12, 12 + col_w, 12 + card_h),
        theme, radius=16, glow_alpha=0, border_w=1, use_dots=False, soft=True
    )
    ld = ImageDraw.Draw(left_plate)
    draw_circle_number_badge(left_plate, 12 + 36, 12 + 32, '1', theme, radius=16)
    ld.text((12 + 64, 12 + 20), left_tag, font=f_kicker, fill=theme['subtext'])
    ld.text((12 + 28, 12 + 58), left_title, font=load_font(28, 'bold'), fill=theme['subtext'])
    ld.line((12 + 28, 12 + body_y - 12, 12 + col_w - 28, 12 + body_y - 12), fill=theme['hairline'], width=1)
    iy = 12 + body_y
    for it in left_items:
        for li, ln in enumerate(textwrap.wrap(it, width=34)[:2]):
            ld.text((12 + 28, iy + li * 26), f'•  {ln}' if li == 0 else f'   {ln}', font=f_item, fill=theme['subtext'])
        iy += 62
    left_plate = left_plate.filter(ImageFilter.GaussianBlur(0.8))

    right_plate = make_modern_glow_plate(
        col_w + 24, card_h + 24, (12, 12, 12 + col_w, 12 + card_h),
        theme, radius=16, glow_alpha=155, border_w=2, use_dots=True, soft=False
    )
    rd = ImageDraw.Draw(right_plate)
    draw_circle_number_badge(right_plate, 12 + 36, 12 + 32, '2', theme, radius=16)
    rd.text((12 + 64, 12 + 20), right_tag, font=f_kicker, fill=theme['kicker_text'])
    right_plate.alpha_composite(r_head, dest=(12 + 20, 12 + 52))
    draw_glowing_underline(right_plate, 12 + 26, 12 + 52 + r_head.height + 2, min(col_w - 52, r_head.width - 12), theme, thickness=4)
    iy = 12 + body_y
    for it in right_items:
        for li, ln in enumerate(textwrap.wrap(it, width=34)[:2]):
            rd.text((12 + 28, iy + li * 26), f'•  {ln}' if li == 0 else f'   {ln}', font=load_font(21, 'bold'), fill=theme['text'])
        iy += 62

    def frame_fn(t, _total_d):
        frame = Image.new('RGBA', (cw, ch), (0, 0, 0, 0))
        le = ease_out_quint(t / 0.45)
        frame.alpha_composite(
            scale_alpha(left_plate, min(0.88, t / 0.28)),
            dest=(pad - 12, pad - 12 + int((1.0 - le) * 18)),
        )
        if t >= split_delay:
            re_p = ease_out_quint((t - split_delay) / 0.48)
            dy = int(round((1.0 - re_p) * 20))
            frame.alpha_composite(
                scale_alpha(right_plate, min(1.0, (t - split_delay) / 0.28)),
                dest=(pad + col_w + gap - 12, pad - 12 + dy),
            )
        return frame

    vid = encode_rgba_motion(cw, ch, dur, frame_fn, mov_path, png_path, peak_ratio=0.80)
    return {'video': vid, 'png': png_path, 'x': ox, 'y': oy, 'split_delay': split_delay}


# ---------------------------------------------------------------------------
# 10. Glowing Neon-Border Pull-Quote / Highlight Box (`kinetic_quote`)
# ---------------------------------------------------------------------------

def build_motion_kinetic_quote(ov, theme, dur, mov_path, png_path):
    tag = clean_kicker(ov.get('tag') or ov.get('category') or 'Tổng kết thực tế', 'Điểm cốt lõi')
    quote = strip_emoji(ov.get('quote') or ov.get('text') or ov.get('title') or '')
    author = strip_emoji(ov.get('author') or ov.get('subtitle') or '')

    head_strip = make_condensed_display_strip(tag.upper(), 36, theme, condense_x=0.84)
    f_q = load_font(28, 'bold')
    f_au = load_font(20, 'demi')
    lines = textwrap.wrap(quote, width=54)[:2]
    line_strips = [make_text_strip(f'•  {ln}' if i == 0 else f'   {ln}', f_q, theme['text'], pad_y=4) for i, ln in enumerate(lines)]
    au_strip = make_text_strip(f'—  {author}', f_au, theme['accent'], pad_y=4) if author else None

    pad = 24
    head_y = 16
    line_y = head_y + head_strip.height + 2
    quote_y0 = line_y + 16
    max_lw = max([head_strip.width + 64] + [s.width + 64 for s in line_strips])
    card_w = min(1320, max(920, max_lw))
    card_h = quote_y0 + len(line_strips) * 42 + (40 if au_strip else 16)
    cw, ch = card_w + pad * 2, card_h + pad * 2
    ox = (1920 - cw) // 2
    oy = (940 - card_h if ov.get('position') != 'top' else 104) - pad

    shell = make_modern_glow_plate(cw, ch, (pad, pad, pad + card_w, pad + card_h), theme, radius=16, glow_alpha=155, border_w=2)

    def frame_fn(t, _total_d):
        frame = shell.copy()
        if t > 0.04:
            draw_brand_spark_badge(frame, pad + 26, pad + head_y + 8, theme, size=22)
            paste_masked_reveal(frame, head_strip, (pad + 54, pad + head_y), (t - 0.04) / 0.40)
            bw = int((head_strip.width - 12) * ease_out_quint((t - 0.10) / 0.45))
            if bw > 6:
                draw_glowing_underline(frame, pad + 60, pad + line_y, bw, theme, thickness=4)

        qy = pad + quote_y0
        for idx, st_im in enumerate(line_strips):
            t0 = 0.14 + idx * 0.10
            if t > t0:
                paste_masked_reveal(frame, st_im, (pad + 26, qy), (t - t0) / 0.48)
            qy += 42

        if au_strip and t > 0.30:
            paste_masked_reveal(frame, au_strip, (pad + 50, qy + 4), (t - 0.30) / 0.42)
        return frame

    vid = encode_rgba_motion(cw, ch, dur, frame_fn, mov_path, png_path)
    return {'video': vid, 'png': png_path, 'x': ox, 'y': oy}


# ---------------------------------------------------------------------------
# 11-Frame Static Storyboard Sheet Generator (`work/storyboard_11frames.jpg`)
#     Matches the reference image workflow:
#     (1) Cắt video, làm graphic thử -> (2) 11 khung hình tĩnh để duyệt -> (3) Mình góp ý vài chỗ
# ---------------------------------------------------------------------------

def build_storyboard_sheet(proj, work, manifest, theme):
    """Render a 1920x1240 modern Dot-Grid Storyboard Review Board with 11 static frames."""
    base_vid = None
    for cand in (
        os.path.join(work, 'base_ambient_only.mp4'),
        os.path.join(proj, 'assets', 'base_16x9.mp4'),
        os.path.join(work, '4k_segs', 'base_4k_ambient.mp4'),
    ):
        if os.path.isfile(cand):
            base_vid = cand
            break
    if not base_vid:
        return None

    dur = 60.0
    try:
        fp = shutil.which('ffprobe') or FF.replace('ffmpeg', 'ffprobe')
        out = subprocess.run(
            [fp, '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', base_vid],
            capture_output=True, encoding='utf-8', errors='replace'
        ).stdout.strip()
        if out:
            dur = float(out.split(',')[0])
    except Exception:
        pass

    overlays = manifest.get('overlays') or []
    sample_items = []
    for ov in overlays:
        st, en = float(ov['start']), float(ov['end'])
        t_mid = round(st + (en - st) * 0.68, 2)
        sample_items.append((t_mid, ov))
    while len(sample_items) < 11:
        idx = len(sample_items) + 1
        t_fill = round(min(dur - 0.5, max(0.5, (dur / 12.0) * idx)), 2)
        sample_items.append((t_fill, None))
    sample_items = sorted(sample_items[:11], key=lambda x: x[0])

    W, H = 1920, 1240
    board = Image.new('RGBA', (W, H), theme['surface'])
    draw_dot_grid_region(board, (0, 0, W, H), theme['dot_color'], spacing=26, dot_r=1.6, radius=0)
    bd = ImageDraw.Draw(board)

    # Top-left Header Lockup ("Claude cắt thử / & DỰNG STORYBOARD")
    draw_brand_spark_badge(board, 64, 38, theme, size=26)
    bd.text((100, 34), 'Claude cắt thử · Bản dựng tĩnh', font=load_font(26, 'demi'), fill=theme['kicker_text'])
    h_strip = make_condensed_display_strip('& DỰNG STORYBOARD', 56, theme, condense_x=0.83)
    board.alpha_composite(h_strip, dest=(58, 70))
    draw_glowing_underline(board, 64, 70 + h_strip.height + 2, h_strip.width - 12, theme, thickness=5)

    # Top-right 3 workflow pills (1 Cắt video, làm graphic thử / 2 11 khung hình tĩnh để duyệt / 3 Mình góp ý vài chỗ)
    steps = [
        ('1', 'Cắt video, làm graphic thử'),
        ('2', '11 khung hình tĩnh để duyệt'),
        ('3', 'Duyệt nhanh trước khi xuất 4K'),
    ]
    for s_idx, (s_num, s_txt) in enumerate(steps):
        pw, ph = 344, 62
        px = W - 64 - (3 - s_idx) * (pw + 14) + 14
        py = 58
        pill = make_modern_glow_plate(pw + 16, ph + 16, (8, 8, 8 + pw, 8 + ph), theme, radius=14, glow_alpha=80, border_w=2, soft=True)
        draw_circle_number_badge(pill, 8 + 30, 8 + ph // 2, s_num, theme, radius=15)
        ImageDraw.Draw(pill).text((8 + 56, 8 + ph // 2 - 11), s_txt, font=load_font(17, 'bold'), fill=theme['text'])
        board.alpha_composite(pill, dest=(px - 8, py - 8))

    tw, th = 428, 240
    cols = 4
    gx0, gy0 = 64, 196
    gx_gap, gy_gap = 26, 28

    for f_idx, (t_sec, ov) in enumerate(sample_items):
        row = f_idx // cols
        col = f_idx % cols
        fx = gx0 + col * (tw + gx_gap)
        fy = gy0 + row * (th + 58 + gy_gap)

        tmp_jpg = os.path.join(work, f'_sb_tmp_{f_idx:02d}.jpg')
        try:
            subprocess.run(
                [FF, '-loglevel', 'error', '-y', '-ss', f'{t_sec:.2f}', '-i', base_vid, '-vf', 'scale=1920:1080', '-frames:v', '1', tmp_jpg],
                check=False
            )
            if os.path.isfile(tmp_jpg):
                f_im = Image.open(tmp_jpg).convert('RGBA')
                os.remove(tmp_jpg)
            else:
                f_im = Image.new('RGBA', (1920, 1080), (20, 26, 22, 255))
        except Exception:
            f_im = Image.new('RGBA', (1920, 1080), (20, 26, 22, 255))

        if ov and ov.get('png') and os.path.isfile(ov['png']):
            try:
                ov_im = Image.open(ov['png']).convert('RGBA')
                f_im.alpha_composite(ov_im, dest=(int(ov.get('x', 0)), int(ov.get('y', 0))))
            except Exception:
                pass

        thumb = f_im.resize((tw, th), Image.LANCZOS)
        card = make_modern_glow_plate(
            tw + 20, th + 64, (10, 10, 10 + tw, 10 + th + 48),
            theme, radius=12, glow_alpha=110 if ov else 45, border_w=2 if ov else 1, use_dots=False
        )
        card.paste(thumb, (10, 10))
        draw_circle_number_badge(card, 10 + 24, 10 + th + 24, str(f_idx + 1), theme, radius=14)
        cd = ImageDraw.Draw(card)
        lbl = f"{t_sec:5.1f}s  ·  {ov['type'].upper() if ov else 'B-ROLL / SCENE'}"
        cd.text((10 + 48, 10 + th + 13), lbl, font=load_font(16, 'bold'), fill=theme['text'])
        board.alpha_composite(card, dest=(fx - 10, fy - 10))

    # 12th slot: Summary / Feedback callout box
    fx = gx0 + 3 * (tw + gx_gap)
    fy = gy0 + 2 * (th + 58 + gy_gap)
    note_card = make_modern_glow_plate(tw + 20, th + 64, (10, 10, 10 + tw, 10 + th + 48), theme, radius=12, glow_alpha=160, border_w=2)
    nd = ImageDraw.Draw(note_card)
    notes = [
        '• Dot-grid background chống trống trải',
        '• Tiêu đề Condensed + gạch chân phát sáng',
        '• Pill đánh số (1) (2) (3) & cột so sánh',
        '• Màu Mint (#4ADE80) & Cam Anthropic',
        '• 100% không dùng emoji hay khung TV cũ',
    ]
    for n_i, n_txt in enumerate(notes):
        nd.text((24, 28 + n_i * 48), n_txt, font=load_font(16, 'bold'), fill=theme['accent'] if n_i == 4 else theme['text'])
    board.alpha_composite(note_card, dest=(fx - 10, fy - 10))

    sb_path = os.path.join(work, 'storyboard_11frames.jpg')
    board.convert('RGB').save(sb_path, 'JPEG', quality=93)
    return sb_path


# ---------------------------------------------------------------------------
# Subtitles (.ass) & Main Orchestrator
# ---------------------------------------------------------------------------

def ass_timestamp(sec):
    sec = max(0.0, float(sec))
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = sec % 60
    return f'{h}:{m:02d}:{s:05.2f}'


def write_ass_subtitles(items, seg_map, out_path):
    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Be Vietnam Pro,42,&H00F8FAFC,&H0080DE4A,&H000D1510,&H880A120E,-1,0,0,0,100,100,0.4,0,1,2.5,1.2,2,110,110,50,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = [header.strip()]
    for it in items:
        if 'segment' in it and it['segment'] in seg_map:
            base = seg_map[it['segment']]['start']
            st = base + float(it.get('offset', 0.0))
            en = st + float(it.get('duration', 2.5))
        else:
            st = float(it['start'])
            en = float(it['end'])
        txt = strip_emoji(it['text']).replace('\n', '\\N')
        lines.append(f'Dialogue: 0,{ass_timestamp(st)},{ass_timestamp(en)},Default,,0,0,0,,{txt}')
    with open(out_path, 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(lines) + '\n')


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if len(sys.argv) < 2:
        print('Usage: PY build_graphics.py <project_dir>')
        sys.exit(1)

    proj = os.path.abspath(os.path.expanduser(sys.argv[1]))
    work = os.path.join(proj, 'work')
    gfx_dir = os.path.join(work, 'overlays')
    os.makedirs(gfx_dir, exist_ok=True)

    cfg = {}
    if os.path.isfile(CONFIG_FILE):
        with open(CONFIG_FILE, encoding='utf-8') as fh:
            cfg = json.load(fh)

    seg_map = {}
    seg_file = os.path.join(proj, 'segments.json')
    if os.path.isfile(seg_file):
        with open(seg_file, encoding='utf-8') as fh:
            for s in json.load(fh):
                seg_map[s['id']] = s

    with open(os.path.join(proj, 'graphics.json'), encoding='utf-8') as fh:
        gcfg = json.load(fh)

    look_name = gcfg.get('look') or cfg.get('defaultLook') or 'modern_mint'
    theme = THEMES.get(look_name, THEMES['modern_mint'])

    manifest = {
        'look': look_name,
        'subtitles_ass': None,
        'overlays': [],
        'sfx_events': [],
    }

    subs = gcfg.get('subtitles') or {}
    if subs.get('enabled') and subs.get('items'):
        ass_path = os.path.join(work, 'subtitles.ass')
        write_ass_subtitles(subs['items'], seg_map, ass_path)
        manifest['subtitles_ass'] = ass_path
        print(f'Wrote {len(subs["items"])} subtitles -> {ass_path}')

    for idx, ov in enumerate(gcfg.get('overlays') or []):
        otype = ov.get('type', 'lower_third')
        if 'segment' in ov and ov['segment'] in seg_map:
            base = seg_map[ov['segment']]['start']
            start = round(base + float(ov.get('offset', 0.0)), 3)
            dur = float(ov.get('duration', 4.0))
            end = round(start + dur, 3)
        else:
            start = round(float(ov.get('start', 0.0)), 3)
            end = round(float(ov.get('end', start + float(ov.get('duration', 4.0)))), 3)
        dur = max(1.5, round(end - start, 3))

        ov_theme_name = ov.get('theme')
        ov_theme = THEMES.get(ov_theme_name, theme) if ov_theme_name else theme

        png_path = os.path.join(gfx_dir, f'ov_{idx:02d}_{otype}.png')
        mov_path = os.path.join(gfx_dir, f'ov_{idx:02d}_{otype}.mov')
        entry = {
            'id': f'ov_{idx:02d}',
            'type': otype,
            'png': png_path,
            'video': None,
            'x': 0,
            'y': 0,
            'start': start,
            'end': end,
            'duration': dur,
        }

        if otype == 'intro':
            res = build_modern_intro(ov, ov_theme, dur, mov_path, png_path)
            entry.update(res)
            sfx = [('whoosh-short', start, 0.22)]
        elif otype == 'chapter':
            res = build_modern_chapter(ov, ov_theme, dur, mov_path, png_path)
            entry.update(res)
            sfx = [('whoosh-short', start, 0.20)]
        elif otype == 'lower_third':
            res = build_modern_lower_third(ov, ov_theme, dur, mov_path, png_path)
            entry.update(res)
            sfx = [('click-soft', start, 0.20)]
        elif otype == 'visual_card':
            res = build_motion_visual_card(ov, ov_theme, proj, dur, mov_path, png_path)
            entry.update(res)
            sfx = [('whoosh-short', start, 0.18)]
        elif otype == 'stat_card':
            res = build_motion_stat_card(ov, ov_theme, dur, mov_path, png_path)
            entry.update(res)
            sfx = [('click-soft', start, 0.20)]
        elif otype in ('checklist', 'steps_card'):
            res = build_motion_checklist(ov, ov_theme, dur, mov_path, png_path)
            entry.update(res)
            sfx = [('click-soft', start, 0.20)]
        elif otype == 'comparison':
            res = build_motion_comparison(ov, ov_theme, dur, mov_path, png_path)
            entry.update(res)
            sfx = [('whoosh-short', start, 0.18), ('click-soft', start + res.get('split_delay', 0.55), 0.18)]
        elif otype == 'kinetic_quote':
            res = build_motion_kinetic_quote(ov, ov_theme, dur, mov_path, png_path)
            entry.update(res)
            sfx = [('whoosh-short', start, 0.18)]
        elif otype == 'custom_motion':
            src_rel = ov.get('src') or ov.get('video') or ''
            src_abs = os.path.join(proj, src_rel) if (src_rel and not os.path.isabs(src_rel)) else src_rel
            entry['video'] = src_abs if os.path.isfile(src_abs) else None
            entry['x'] = int(ov.get('x', 0))
            entry['y'] = int(ov.get('y', 0))
            sfx_name = ov.get('sfx', 'whoosh-short')
            sfx = [(sfx_name, start, 0.20)] if sfx_name else []
        elif otype == 'callout':
            res = build_modern_callout(ov, ov_theme, dur, mov_path, png_path)
            entry.update(res)
            sfx = [('click-soft', start, 0.20)]
        elif otype == 'subscribe':
            res = build_modern_subscribe(ov, ov_theme, cfg, dur, mov_path, png_path)
            entry.update(res)
            sfx = [('click-soft', start, 0.20), ('click', start + 0.75, 0.22)]
        else:
            res = build_modern_lower_third(ov, ov_theme, dur, mov_path, png_path)
            entry.update(res)
            sfx = [('click-soft', start, 0.20)]

        manifest['overlays'].append(entry)
        for s_name, s_time, s_vol in sfx:
            manifest['sfx_events'].append({'name': s_name, 'time': round(s_time, 3), 'volume': s_vol})
        out_asset = os.path.basename(entry['video'] or entry['png'])
        print(f'[{start:6.2f}s - {end:6.2f}s] [MODERN-GFX] {otype:14s} -> {out_asset} (@{entry["x"]},{entry["y"]})', flush=True)

    manifest_path = os.path.join(work, 'graphics_manifest.json')
    with open(manifest_path, 'w', encoding='utf-8') as fh:
        json.dump(manifest, fh, indent=2, ensure_ascii=False)

    sb_path = build_storyboard_sheet(proj, work, manifest, theme)
    if sb_path:
        print(f'Built 11-Frame Static Storyboard Sheet -> {sb_path}', flush=True)


if __name__ == '__main__':
    main()
