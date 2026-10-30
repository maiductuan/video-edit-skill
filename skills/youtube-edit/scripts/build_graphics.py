#!/usr/bin/env python3
"""TVC & Documentary Broadcast Motion Graphics Engine for /youtube-edit (1920x1080 RGBA).
Crafted to look like Netflix Documentary / Apple Keynote / Sony Alpha TVC — NEVER cheap SaaS/AI templates:
  - 2x Supersampled Lanczos anti-aliased smoked-glass plates with 1px specular hairline borders
  - Wide-tracked Swiss/TVC micro-kickers (+3.5px optical character tracking, zero loud toy pill buttons)
  - True After-Effects-style masked baseline typography reveals (overflow-hidden yPercent 100->0 expo.out)
  - Live-drawing 1.5px-2.5px architectural hairline rules & precision telemetry lines
  - Automatic AI-Image Optical Film Matching inside visual_card (chroma taming + soft optical vignette)
  - Automatic sanitization of self-referential "AI" labels so "MINH HỌA AI" / "AI VISUAL" never appear on screen

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

# Calibrated TVC & Documentary Cinema Palettes (restrained, non-radioactive broadcast tones)
THEMES = {
    'vibrant_vlog': {
        'accent': (238, 182, 78, 255),        # Brushed Champagne Amber #EEB64E
        'accent_text': (16, 18, 22, 255),
        'badge_red': (214, 48, 49, 255),      # Broadcast Cinema Red
        'surface': (14, 16, 22, 210),         # Translucent Smoked Obsidian Glass
        'surface_top': (24, 27, 36, 216),
        'track': (255, 255, 255, 34),
        'border': (255, 255, 255, 42),
        'hairline': (255, 255, 255, 28),
        'text': (250, 248, 245, 255),         # Warm Optical White
        'subtext': (196, 192, 184, 255),
    },
    'cinema_travel': {
        'accent': (222, 190, 122, 255),       # Anamorphic Brushed Gold #DEBE7A
        'accent_text': (12, 15, 20, 255),
        'badge_red': (198, 46, 54, 255),
        'surface': (10, 14, 19, 214),
        'surface_top': (18, 24, 32, 220),
        'track': (222, 190, 122, 34),
        'border': (222, 190, 122, 48),
        'hairline': (255, 255, 255, 26),
        'text': (247, 244, 237, 255),
        'subtext': (190, 184, 173, 255),
    },
    'clean_studio': {
        'accent': (125, 211, 252, 255),       # Studio Ice Silver-Cyan #7DD3FC
        'accent_text': (11, 16, 26, 255),
        'badge_red': (214, 48, 49, 255),
        'surface': (13, 18, 28, 212),
        'surface_top': (22, 30, 44, 218),
        'track': (255, 255, 255, 34),
        'border': (186, 204, 226, 44),
        'hairline': (255, 255, 255, 26),
        'text': (248, 250, 252, 255),
        'subtext': (182, 194, 209, 255),
    },
    'film_kodak': {
        'accent': (217, 134, 102, 255),       # Kodak Portra Warm Sienna #D98666
        'accent_text': (252, 249, 245, 255),
        'badge_red': (196, 56, 52, 255),
        'surface': (19, 16, 14, 214),
        'surface_top': (29, 24, 21, 220),
        'track': (255, 245, 235, 32),
        'border': (217, 134, 102, 50),
        'hairline': (255, 245, 235, 26),
        'text': (250, 246, 240, 255),
        'subtext': (198, 189, 178, 255),
    },
    'minimal_editorial': {
        'accent': (198, 72, 48, 255),         # Kinfolk / Swiss Vermilion #C64830
        'accent_text': (255, 255, 255, 255),
        'badge_red': (198, 72, 48, 255),
        'surface': (245, 242, 235, 236),      # Museum Archival Paper
        'surface_top': (251, 249, 244, 242),
        'track': (24, 24, 27, 26),
        'border': (24, 24, 27, 36),
        'hairline': (24, 24, 27, 24),
        'text': (22, 22, 25, 255),
        'subtext': (92, 92, 100, 255),
    },
    'warm_food': {
        'accent': (232, 168, 56, 255),        # Michelin Culinary Saffron #E8A838
        'accent_text': (18, 14, 12, 255),
        'badge_red': (214, 48, 49, 255),
        'surface': (18, 14, 12, 214),
        'surface_top': (28, 22, 18, 220),
        'track': (255, 245, 230, 32),
        'border': (232, 168, 56, 48),
        'hairline': (255, 245, 230, 26),
        'text': (252, 249, 244, 255),
        'subtext': (204, 194, 182, 255),
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
    """Signature TVC / Apple Keynote curve: crisp initial impulse, long silky deceleration."""
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
    """Normalize Vietnamese NFC and strip supplementary emojis so vector fonts never render tofu boxes."""
    if not text:
        return ''
    text = unicodedata.normalize('NFC', str(text))
    out = []
    for ch in text:
        cp = ord(ch)
        if cp > 0xFFFF or (0x2600 <= cp <= 0x27BF) or cp == 0xFE0F:
            continue
        out.append(ch)
    return ' '.join(''.join(out).split())


def clean_tvc_kicker(text, fallback='CHI TIẾT'):
    """Never allow self-referential 'MINH HỌA AI' / 'AI VISUAL' tags on broadcast frames."""
    s = strip_emoji(text)
    if not s:
        return fallback
    s = BANNED_AI_TAG_PATTERNS.sub('', s).strip(' •·-|/')
    return s.upper() if s else fallback


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
    avenir = '/System/Library/Fonts/Avenir Next.ttc'
    if os.path.isfile(avenir):
        idx = {'heavy': 0, 'bold': 0, 'demi': 2, 'medium': 5, 'regular': 7}.get(weight, 0)
        try:
            return ImageFont.truetype(avenir, size, index=idx)
        except Exception:
            pass
    for fallback in (
        'C:/Windows/Fonts/segoeuib.ttf',
        'C:/Windows/Fonts/segoeui.ttf',
        'C:/Windows/Fonts/arialbd.ttf',
        '/System/Library/Fonts/Supplemental/Arial Bold.ttf',
        '/System/Library/Fonts/Helvetica.ttc',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
    ):
        if os.path.isfile(fallback):
            try:
                return ImageFont.truetype(fallback, size)
            except Exception:
                pass
    return ImageFont.load_default()


def tracked_width(draw, text, font, tracking=3.2):
    if not text:
        return 0
    total = 0.0
    for i, ch in enumerate(text):
        bb = draw.textbbox((0, 0), ch, font=font)
        total += (bb[2] - bb[0])
        if i < len(text) - 1:
            total += tracking
    return int(round(total))


def draw_tracked_text(draw, xy, text, font, fill, tracking=3.2, align='left'):
    """Render wide-tracked uppercase TVC micro-typography with exact sub-pixel spacing."""
    if not text:
        return 0
    x, y = xy
    w = tracked_width(draw, text, font, tracking=tracking)
    if align == 'center':
        cur_x = x - w / 2.0
    elif align == 'right':
        cur_x = x - w
    else:
        cur_x = float(x)
    for ch in text:
        draw.text((int(round(cur_x)), y), ch, font=font, fill=fill)
        bb = draw.textbbox((0, 0), ch, font=font)
        cur_x += (bb[2] - bb[0]) + tracking
    return w


def draw_tvc_kicker(draw, x, y, text, theme, font_size=16, align='left'):
    """Draw a luxury TVC kicker: tiny 5px precision accent square + wide-tracked uppercase label."""
    f = load_font(font_size, 'demi')
    txt = text.upper()
    if align == 'center':
        tw = tracked_width(draw, txt, f, tracking=3.4)
        total_w = 16 + tw
        sx = int(round(x - total_w / 2.0))
        draw.rectangle((sx, y + 6, sx + 5, y + 11), fill=theme['accent'])
        draw_tracked_text(draw, (sx + 16, y), txt, f, theme['accent'], tracking=3.4, align='left')
        return total_w
    draw.rectangle((x, y + 6, x + 5, y + 11), fill=theme['accent'])
    tw = draw_tracked_text(draw, (x + 15, y), txt, f, theme['accent'], tracking=3.4, align='left')
    return 15 + tw


def make_tvc_glass_plate(cw, ch, box, theme, radius=16, shadow_alpha=105):
    """2x-supersampled smoked-glass architectural plate with vertical sheen & 1px specular hairline border."""
    x0, y0, x1, y1 = box
    canvas = Image.new('RGBA', (cw, ch), (0, 0, 0, 0))

    # Feathered optical drop shadow
    if shadow_alpha > 0:
        sh = Image.new('RGBA', (cw, ch), (0, 0, 0, 0))
        sd = ImageDraw.Draw(sh)
        sd.rounded_rectangle((x0, y0 + 10, x1, y1 + 12), radius=radius, fill=(0, 0, 0, shadow_alpha))
        sh = sh.filter(ImageFilter.GaussianBlur(18))
        canvas = Image.alpha_composite(canvas, sh)

    # 2x supersampled vector plate for razor-smooth corners & 1px hairline border
    ss = 2
    hi = Image.new('RGBA', (cw * ss, ch * ss), (0, 0, 0, 0))
    hd = ImageDraw.Draw(hi)
    bx0, by0, bx1, by1 = x0 * ss, y0 * ss, x1 * ss, y1 * ss
    hd.rounded_rectangle((bx0, by0, bx1, by1), radius=radius * ss, fill=theme['surface'])
    # Subtle top specular sheen band
    sheen_h = max(8, int((by1 - by0) * 0.42))
    sheen = Image.new('RGBA', (cw * ss, ch * ss), (0, 0, 0, 0))
    shd = ImageDraw.Draw(sheen)
    shd.rounded_rectangle((bx0, by0, bx1, by0 + sheen_h), radius=radius * ss, fill=(255, 255, 255, 9))
    mask = Image.new('L', (cw * ss, ch * ss), 0)
    ImageDraw.Draw(mask).rounded_rectangle((bx0, by0, bx1, by1), radius=radius * ss, fill=255)
    hi.paste(Image.alpha_composite(hi, sheen), (0, 0), mask)

    # 1px crisp hairline border (2px at 2x SS)
    hd = ImageDraw.Draw(hi)
    hd.rounded_rectangle((bx0, by0, bx1, by1), radius=radius * ss, outline=theme['border'], width=2)

    plate = hi.resize((cw, ch), Image.LANCZOS)
    return Image.alpha_composite(canvas, plate)


def make_text_strip(text, font, fill, pad_y=10):
    """Pre-render a single line of typography onto a tight RGBA strip for masked baseline reveals."""
    dummy = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    dd = ImageDraw.Draw(dummy)
    bb = dd.textbbox((0, 0), text, font=font)
    w = max(4, (bb[2] - bb[0]) + 12)
    h = max(4, (bb[3] - bb[1]) + pad_y * 2)
    strip = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    sd = ImageDraw.Draw(strip)
    sd.text((2 - bb[0], pad_y - bb[1]), text, font=font, fill=fill)
    return strip


def paste_masked_reveal(canvas, strip, dest_xy, progress, align='left'):
    """After-Effects-style overflow:hidden baseline mask reveal (y rises from +100% -> 0% with quintic ease)."""
    if progress <= 0.01:
        return
    e = ease_out_quint(progress)
    sw, sh = strip.size
    x, y = dest_xy
    if align == 'center':
        x = int(round(x - sw / 2.0))
    elif align == 'right':
        x = int(round(x - sw))
    dy = int(round((1.0 - e) * sh * 0.92))
    if dy <= 0 and e >= 0.995:
        canvas.alpha_composite(strip, dest=(x, y))
        return
    # Clip strictly to [y, y + sh] invisible mask window
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
    """Match an AI/still image to real TVC camera footage: tame digital chroma, soften contrast, add subtle vignette."""
    im = src_im.convert('RGB')
    im = ImageEnhance.Color(im).enhance(0.91)
    im = ImageEnhance.Contrast(im).enhance(0.975)
    im = im.convert('RGBA')

    scale_k = max(target_w / max(1, im.width), target_h / max(1, im.height))
    pw, ph = max(target_w, int(im.width * scale_k)), max(target_h, int(im.height * scale_k))
    im = im.resize((pw, ph), Image.LANCZOS)

    # Subtle optical corner vignette so edges never look clinically flat
    vig = Image.new('RGBA', (pw, ph), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vig)
    vd.rectangle((0, 0, pw, ph), outline=(0, 0, 0, 58), width=max(12, pw // 28))
    vig = vig.filter(ImageFilter.GaussianBlur(max(18, pw // 20)))
    return Image.alpha_composite(im, vig)


def make_editorial_placeholder(vw, vh, theme, title_hint=''):
    """Minimalist dark architectural studio plate if an external image path is missing."""
    im = Image.new('RGBA', (vw, vh), (16, 19, 25, 255))
    d = ImageDraw.Draw(im)
    ac = theme['accent']
    for x in range(48, vw, 80):
        d.line((x, 0, x, vh), fill=(255, 255, 255, 11), width=1)
    for y in range(48, vh, 80):
        d.line((0, y, vw, y), fill=(255, 255, 255, 11), width=1)
    d.line((48, vh // 2, vw - 48, vh // 2), fill=(ac[0], ac[1], ac[2], 70), width=1)
    if title_hint:
        draw_tracked_text(d, (48, vh - 46), title_hint[:28].upper(), load_font(16, 'demi'), theme['subtext'], tracking=3.0)
    return im


# ---------------------------------------------------------------------------
# 1. TVC Frameless Cinema Intro Lockup (Netflix Documentary / Sony Alpha Style)
# ---------------------------------------------------------------------------

def build_tvc_intro(ov, theme, dur, mov_path, png_path):
    kicker = clean_tvc_kicker(ov.get('badge', 'PHÓNG SỰ TRẢI NGHIỆM'), 'PHÓNG SỰ')
    title = strip_emoji(ov.get('title', '')).upper()
    subtitle = strip_emoji(ov.get('subtitle', ''))

    cw, ch = 1520, 440
    ox, oy = (1920 - cw) // 2, (1080 - ch) // 2

    # Soft feathered optical scrim (NO boxy rectangle — lets cinema footage breathe full-bleed!)
    scrim = Image.new('RGBA', (cw, ch), (0, 0, 0, 0))
    sd = ImageDraw.Draw(scrim)
    sd.ellipse((120, 40, cw - 120, ch - 40), fill=(8, 10, 14, 158))
    scrim = scrim.filter(ImageFilter.GaussianBlur(64))

    f_title = load_font(66 if len(title) <= 30 else 52, 'heavy')
    f_sub = load_font(26, 'medium')
    title_strip = make_text_strip(title, f_title, theme['text'], pad_y=12) if title else None
    sub_strip = make_text_strip(subtitle, f_sub, theme['subtext'], pad_y=8) if subtitle else None

    def frame_fn(t, _total_d):
        frame = scale_alpha(scrim, ease_out_cubic(t / 0.45))
        fd = ImageDraw.Draw(frame)

        # 1. Tracked uppercase kicker fades in gently at top
        if t > 0.06:
            kp = ease_out_cubic((t - 0.06) / 0.45)
            klayer = Image.new('RGBA', (cw, 40), (0, 0, 0, 0))
            kd = ImageDraw.Draw(klayer)
            draw_tvc_kicker(kd, cw // 2, 8, kicker, theme, font_size=17, align='center')
            frame.alpha_composite(scale_alpha(klayer, kp), dest=(0, 96))

        # 2. Hero title rises cleanly out of invisible baseline mask
        if title_strip and t > 0.12:
            paste_masked_reveal(frame, title_strip, (cw // 2, 148), (t - 0.12) / 0.58, align='center')

        # 3. Precision 2px center gold hairline expands outward
        rule_e = ease_out_quint(max(0.0, (t - 0.22) / 0.62))
        half_w = int(110 * rule_e)
        if half_w > 2:
            fd.rectangle((cw // 2 - half_w, 258, cw // 2 + half_w, 260), fill=theme['accent'])

        # 4. Subtitle reveals below hairline
        if sub_strip and t > 0.30:
            paste_masked_reveal(frame, sub_strip, (cw // 2, 282), (t - 0.30) / 0.55, align='center')
        return frame

    vid = encode_rgba_motion(cw, ch, dur, frame_fn, mov_path, png_path, peak_ratio=0.65)
    return {'video': vid, 'png': png_path, 'x': ox, 'y': oy}


# ---------------------------------------------------------------------------
# 2. TVC Chapter & Lower-Third Architectural Ribbons
# ---------------------------------------------------------------------------

def build_tvc_chapter(ov, theme, dur, mov_path, png_path):
    num = strip_emoji(ov.get('number', '01')).upper()
    kicker = f'PHẦN {num}' if (not num.startswith(('CHƯƠNG', 'PHẦN')) and len(num) <= 3) else num
    title = strip_emoji(ov.get('title', ''))
    sub = strip_emoji(ov.get('subtitle', ''))

    f_title = load_font(40, 'heavy')
    f_sub = load_font(23, 'medium')
    title_strip = make_text_strip(title, f_title, theme['text'], pad_y=8) if title else None
    sub_strip = make_text_strip(sub, f_sub, theme['subtext'], pad_y=6) if sub else None

    pad = 26
    content_w = max(
        480,
        (title_strip.width if title_strip else 0) + 84,
        (sub_strip.width if sub_strip else 0) + 84,
    )
    card_w = min(1080, content_w)
    card_h = 158 if sub_strip else 124
    cw, ch = card_w + pad * 2, card_h + pad * 2
    ox, oy = 88 - pad, 780 - pad

    shell = make_tvc_glass_plate(cw, ch, (pad, pad, pad + card_w, pad + card_h), theme, radius=14)

    def frame_fn(t, _total_d):
        frame = shell.copy()
        fd = ImageDraw.Draw(frame)

        # Growing left vertical 3px accent laser line (bottom -> top)
        le = ease_out_quint(t / 0.52)
        lh = int((card_h - 36) * le)
        if lh > 4:
            y_bot = pad + card_h - 18
            fd.rectangle((pad + 20, y_bot - lh, pad + 23, y_bot), fill=theme['accent'])

        if t > 0.05:
            kl = Image.new('RGBA', (card_w, 32), (0, 0, 0, 0))
            draw_tvc_kicker(ImageDraw.Draw(kl), 0, 4, kicker, theme, font_size=15)
            frame.alpha_composite(scale_alpha(kl, ease_out_cubic((t - 0.05) / 0.38)), dest=(pad + 38, pad + 20))

        if title_strip and t > 0.12:
            paste_masked_reveal(frame, title_strip, (pad + 38, pad + 48), (t - 0.12) / 0.50)

        if sub_strip and t > 0.22:
            paste_masked_reveal(frame, sub_strip, (pad + 38, pad + 104), (t - 0.22) / 0.48)
        return frame

    vid = encode_rgba_motion(cw, ch, dur, frame_fn, mov_path, png_path)
    return {'video': vid, 'png': png_path, 'x': ox, 'y': oy}


def build_tvc_lower_third(ov, theme, dur, mov_path, png_path):
    cat = clean_tvc_kicker(ov.get('category', 'ĐỊA ĐIỂM & TRẢI NGHIỆM'), 'TRẢI NGHIỆM')
    title = strip_emoji(ov.get('title', ''))
    loc = strip_emoji(ov.get('location', ''))
    price = strip_emoji(ov.get('price', ''))
    rating = strip_emoji(ov.get('rating', ''))

    f_title = load_font(40, 'heavy')
    f_meta = load_font(23, 'medium')
    meta_str = '   ·   '.join([p for p in (loc, price) if p])

    title_strip = make_text_strip(title, f_title, theme['text'], pad_y=8) if title else None
    meta_strip = make_text_strip(meta_str, f_meta, theme['subtext'], pad_y=6) if meta_str else None

    pad = 26
    score_w = 158 if rating else 0
    text_w = max(
        460,
        (title_strip.width if title_strip else 0),
        (meta_strip.width if meta_strip else 0),
    )
    card_w = min(1260, text_w + 84 + score_w)
    card_h = 166 if meta_strip else 132
    cw, ch = card_w + pad * 2, card_h + pad * 2
    ox, oy = 88 - pad, 765 - pad

    shell = make_tvc_glass_plate(cw, ch, (pad, pad, pad + card_w, pad + card_h), theme, radius=14)

    # Parse rating into main number + '/10' denominator for Michelin-style minimalist typography
    rate_main, rate_sub = rating, ''
    if '/' in rating:
        parts = rating.split('/', 1)
        rate_main, rate_sub = parts[0].strip(), '/' + parts[1].strip()
    rate_strip = make_text_strip(rate_main, load_font(44, 'heavy'), theme['accent'], pad_y=6) if rating else None

    def frame_fn(t, _total_d):
        frame = shell.copy()
        fd = ImageDraw.Draw(frame)

        # Left 3px accent laser line
        le = ease_out_quint(t / 0.50)
        lh = int((card_h - 36) * le)
        if lh > 4:
            yb = pad + card_h - 18
            fd.rectangle((pad + 20, yb - lh, pad + 23, yb), fill=theme['accent'])

        if t > 0.05:
            kl = Image.new('RGBA', (card_w, 32), (0, 0, 0, 0))
            draw_tvc_kicker(ImageDraw.Draw(kl), 0, 4, cat, theme, font_size=15)
            frame.alpha_composite(scale_alpha(kl, ease_out_cubic((t - 0.05) / 0.36)), dest=(pad + 38, pad + 20))

        if title_strip and t > 0.11:
            paste_masked_reveal(frame, title_strip, (pad + 38, pad + 48), (t - 0.11) / 0.50)

        # Hairline divider + metadata
        if meta_strip and t > 0.20:
            re_w = int((card_w - score_w - 76) * ease_out_quint((t - 0.20) / 0.52))
            if re_w > 6:
                fd.line((pad + 38, pad + 106, pad + 38 + re_w, pad + 106), fill=theme['hairline'], width=1)
            paste_masked_reveal(frame, meta_strip, (pad + 38, pad + 114), (t - 0.24) / 0.46)

        # Minimalist Michelin-style score column on the right (hairline vertical divider, zero chunky yellow box!)
        if rate_strip and t > 0.26:
            div_x = pad + card_w - score_w
            vh = int((card_h - 44) * ease_out_quint((t - 0.26) / 0.45))
            if vh > 4:
                fd.line((div_x, pad + 22, div_x, pad + 22 + vh), fill=theme['hairline'], width=1)
            rx_center = div_x + score_w // 2 - (12 if rate_sub else 0)
            paste_masked_reveal(frame, rate_strip, (rx_center, pad + card_h // 2 - 18), (t - 0.28) / 0.48, align='center')
            if rate_sub and t > 0.36:
                fd.text((rx_center + rate_strip.width // 2 + 2, pad + card_h // 2 + 4), rate_sub,
                        font=load_font(20, 'medium'), fill=theme['subtext'])
            kl2 = Image.new('RGBA', (score_w, 24), (0, 0, 0, 0))
            draw_tracked_text(ImageDraw.Draw(kl2), (score_w // 2, 2), 'ĐÁNH GIÁ', load_font(13, 'demi'),
                              theme['subtext'], tracking=2.6, align='center')
            frame.alpha_composite(scale_alpha(kl2, ease_out_cubic((t - 0.30) / 0.4)), dest=(div_x, pad + 22))
        return frame

    vid = encode_rgba_motion(cw, ch, dur, frame_fn, mov_path, png_path)
    return {'video': vid, 'png': png_path, 'x': ox, 'y': oy}


# ---------------------------------------------------------------------------
# 3. Callout & Subscribe TVC Minimalist Plates
# ---------------------------------------------------------------------------

def render_callout(ov, theme):
    img = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))
    pos = ov.get('position', 'top_right')
    tag = clean_tvc_kicker(ov.get('icon', 'GHI CHÚ'), 'GHI CHÚ')
    title = strip_emoji(ov.get('title', 'Lưu ý'))
    text = strip_emoji(ov.get('text', ''))

    f_title = load_font(28, 'bold')
    f_text = load_font(22, 'medium')
    wrapped = textwrap.wrap(text, width=42)[:2]

    card_w = 580
    card_h = 148 if len(wrapped) <= 1 else 178
    x0 = (1920 - 88 - card_w) if pos == 'top_right' else 88
    y0 = 78

    plate = make_tvc_glass_plate(1920, 1080, (x0, y0, x0 + card_w, y0 + card_h), theme, radius=14)
    img = Image.alpha_composite(img, plate)
    d = ImageDraw.Draw(img)
    d.rectangle((x0, y0 + 18, x0 + 3, y0 + card_h - 18), fill=theme['accent'])
    draw_tvc_kicker(d, x0 + 24, y0 + 18, tag, theme, font_size=14)
    d.text((x0 + 24, y0 + 44), title, font=f_title, fill=theme['text'])
    for idx, line in enumerate(wrapped):
        d.text((x0 + 24, y0 + 86 + idx * 30), line, font=f_text, fill=theme['subtext'])
    return img


def render_subscribe(ov, theme, cfg):
    img = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))
    channel = strip_emoji(ov.get('channel') or cfg.get('channelName') or 'Tuấn Đi Review')
    handle = strip_emoji(ov.get('handle') or cfg.get('channelHandle') or '@tuandireview  ·  Theo dõi hành trình mới mỗi tuần')
    btn_txt = strip_emoji(ov.get('button_text') or 'ĐĂNG KÝ').upper()

    f_ch = load_font(30, 'heavy')
    f_hd = load_font(21, 'medium')
    f_btn = load_font(19, 'bold')

    tmp_d = ImageDraw.Draw(img)
    cb = tmp_d.textbbox((0, 0), channel, font=f_ch)
    hb = tmp_d.textbbox((0, 0), handle, font=f_hd)
    btn_w = max(168, tracked_width(tmp_d, btn_txt, f_btn, tracking=2.2) + 52)
    text_w = max(cb[2] - cb[0], hb[2] - hb[0])

    card_w = min(1240, max(760, 118 + text_w + 56 + btn_w + 32))
    card_h = 114
    x0 = (1920 - card_w) // 2
    y0 = 828

    plate = make_tvc_glass_plate(1920, 1080, (x0, y0, x0 + card_w, y0 + card_h), theme, radius=16)
    img = Image.alpha_composite(img, plate)
    d = ImageDraw.Draw(img)

    # Minimalist monogram ring
    cx, cy, r = x0 + 58, y0 + card_h // 2, 34
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=theme['accent'], width=2)
    initials = ''.join(w[0].upper() for w in channel.split()[:2]) or 'YT'
    d.text((cx, cy), initials, font=load_font(23, 'heavy'), fill=theme['text'], anchor='mm')

    d.text((x0 + 112, y0 + 24), channel, font=f_ch, fill=theme['text'])
    d.text((x0 + 112, y0 + 64), handle, font=f_hd, fill=theme['subtext'])

    bx0, by0 = x0 + card_w - btn_w - 24, y0 + 26
    bx1, by1 = x0 + card_w - 24, y0 + card_h - 26
    d.rounded_rectangle((bx0, by0, bx1, by1), radius=10, fill=theme['badge_red'])
    draw_tracked_text(d, ((bx0 + bx1) // 2, by0 + 18), btn_txt, f_btn, (255, 255, 255, 255), tracking=2.2, align='center')
    return img


# ---------------------------------------------------------------------------
# 4. TVC Picture-in-Picture Cinema Plate (`visual_card` — Optical Matched)
# ---------------------------------------------------------------------------

def build_motion_visual_card(ov, theme, proj, dur, mov_path, png_path):
    """TVC cinema PiP frame: thin 14px smoked-glass bezel, optical-matched plate, sinusoidal gimbal drift."""
    pos = (ov.get('position') or 'right').lower()
    tag = clean_tvc_kicker(ov.get('tag') or ov.get('category') or '', fallback='GÓC QUAY CHI TIẾT')
    title = strip_emoji(ov.get('title') or '')
    caption = strip_emoji(ov.get('caption') or ov.get('text') or '')

    pad = 26
    bezel = 14
    card_w = 780 if pos == 'center' else 650
    wrapped_cap = textwrap.wrap(caption, width=48 if pos == 'center' else 40)[:2]
    vp_w = card_w - bezel * 2
    vp_h = 410 if pos == 'center' else 366
    footer_h = (28 if tag else 0) + (42 if title else 0) + len(wrapped_cap) * 28 + 26
    card_h = bezel + vp_h + max(64, footer_h)

    cw, ch = card_w + pad * 2, card_h + pad * 2
    if pos == 'left':
        ox = 88 - pad
    elif pos == 'center':
        ox = (1920 - cw) // 2
    else:
        ox = 1920 - 88 - card_w - pad
    oy = 124 - pad

    img_rel = ov.get('image') or ov.get('src') or ''
    img_abs = os.path.join(proj, img_rel) if (img_rel and not os.path.isabs(img_rel)) else img_rel
    if img_abs and os.path.isfile(img_abs):
        try:
            raw_im = Image.open(img_abs)
            src_im = prepare_optical_image(raw_im, int(vp_w * 1.14), int(vp_h * 1.14))
        except Exception:
            src_im = make_editorial_placeholder(int(vp_w * 1.14), int(vp_h * 1.14), theme, title)
    else:
        src_im = make_editorial_placeholder(int(vp_w * 1.14), int(vp_h * 1.14), theme, title)

    pre_w, pre_h = src_im.size
    # 2x supersampled rounded viewport mask for razor-clean corners
    vp_mask_hi = Image.new('L', (vp_w * 2, vp_h * 2), 0)
    ImageDraw.Draw(vp_mask_hi).rounded_rectangle((0, 0, vp_w * 2, vp_h * 2), radius=20, fill=255)
    vp_mask = vp_mask_hi.resize((vp_w, vp_h), Image.LANCZOS)

    shell = make_tvc_glass_plate(cw, ch, (pad, pad, pad + card_w, pad + card_h), theme, radius=16)
    f_title = load_font(29, 'bold')
    f_cap = load_font(21, 'medium')
    title_strip = make_text_strip(title, f_title, theme['text'], pad_y=6) if title else None

    def frame_fn(t, total_d):
        # Smooth sinusoidal gimbal drift (restrained 6.5% dolly, never fast/artificial)
        p = ease_in_out_sine(t / max(0.5, total_d))
        cur_zoom = 1.0 + 0.065 * p
        crop_w = min(pre_w, max(16, int(round(vp_w / cur_zoom * 1.10))))
        crop_h = min(pre_h, max(16, int(round(vp_h / cur_zoom * 1.10))))
        cx0 = int(max(0, pre_w - crop_w) * (0.40 + 0.22 * p))
        cy0 = int(max(0, pre_h - crop_h) * (0.50 - 0.10 * p))
        cropped = src_im.crop((cx0, cy0, cx0 + crop_w, cy0 + crop_h)).resize((vp_w, vp_h), Image.BICUBIC)

        frame = shell.copy()
        frame.paste(cropped, (pad + bezel, pad + bezel), vp_mask)
        fd = ImageDraw.Draw(frame)
        # Subtle 1px inner frame hairline around image
        fd.rounded_rectangle(
            (pad + bezel, pad + bezel, pad + bezel + vp_w, pad + bezel + vp_h),
            radius=10, outline=(255, 255, 255, 30), width=1
        )

        fy = pad + bezel + vp_h + 14
        if tag:
            draw_tvc_kicker(fd, pad + 22, fy, tag, theme, font_size=13)
            fy += 24
        if title_strip and t > 0.10:
            paste_masked_reveal(frame, title_strip, (pad + 22, fy - 4), (t - 0.10) / 0.48)
            fy += 38
        if wrapped_cap and t > 0.20:
            ca = ease_out_cubic((t - 0.20) / 0.45)
            clayer = Image.new('RGBA', (card_w - 44, len(wrapped_cap) * 28 + 6), (0, 0, 0, 0))
            cd = ImageDraw.Draw(clayer)
            for idx, ln in enumerate(wrapped_cap):
                cd.text((0, idx * 27), ln, font=f_cap, fill=theme['subtext'])
            frame.alpha_composite(scale_alpha(clayer, ca), dest=(pad + 22, fy))

        # Hairline 1.5px bottom accent rule
        rw = int((card_w - 44) * ease_out_quint(t / 0.70))
        if rw > 4:
            fd.line((pad + 22, pad + card_h - 10, pad + 22 + rw, pad + card_h - 10), fill=theme['accent'], width=2)
        return frame

    vid = encode_rgba_motion(cw, ch, dur, frame_fn, mov_path, png_path)
    return {'video': vid, 'png': png_path, 'x': ox, 'y': oy}


# ---------------------------------------------------------------------------
# 5. TVC / Apple Keynote Precision Telemetry Card (`stat_card`)
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
    """Apple Keynote / Bloomberg style telemetry plate: large tabular figure + 2px hairline gauge."""
    pos = (ov.get('position') or 'right').lower()
    tag = clean_tvc_kicker(ov.get('tag') or ov.get('category') or 'THÔNG SỐ THỰC TẾ', 'THÔNG SỐ')
    raw_val = str(ov.get('value') or ov.get('metric') or '92%')
    label = strip_emoji(ov.get('label') or ov.get('title') or '')
    subtext = strip_emoji(ov.get('subtext') or ov.get('text') or '')

    prefix, target_num, decimals, use_dots, suffix = parse_stat_value(raw_val)
    if 'progress' in ov and ov['progress'] is not None:
        prog_target = max(0.05, min(1.0, float(ov['progress'])))
    elif target_num is not None and '%' in suffix and 0 < target_num <= 100:
        prog_target = target_num / 100.0
    elif target_num is not None and '/10' in suffix and 0 < target_num <= 10:
        prog_target = target_num / 10.0
    else:
        prog_target = 0.82

    pad = 26
    card_w = 590
    wrapped_lbl = textwrap.wrap(label, width=32)[:2]
    wrapped_sub = textwrap.wrap(subtext, width=40)[:2]
    card_h = 228 + len(wrapped_lbl) * 36 + (len(wrapped_sub) * 26 + 8 if wrapped_sub else 0)
    cw, ch = card_w + pad * 2, card_h + pad * 2

    if pos == 'left':
        ox = 88 - pad
    elif pos == 'center':
        ox = (1920 - cw) // 2
    else:
        ox = 1920 - 88 - card_w - pad
    oy = 230 - pad

    shell = make_tvc_glass_plate(cw, ch, (pad, pad, pad + card_w, pad + card_h), theme, radius=16)
    sd = ImageDraw.Draw(shell)
    draw_tvc_kicker(sd, pad + 32, pad + 26, tag, theme, font_size=14)

    f_val = load_font(82 if len(raw_val) <= 7 else 64, 'heavy')
    f_lbl = load_font(28, 'bold')
    f_sub = load_font(21, 'medium')

    # Razor-thin 2px precision telemetry track
    bar_x0, bar_y = pad + 32, pad + 178
    bar_max_w = card_w - 64
    sd.line((bar_x0, bar_y, bar_x0 + bar_max_w, bar_y), fill=theme['track'], width=2)

    ty = bar_y + 22
    for ln in wrapped_lbl:
        sd.text((pad + 32, ty), ln, font=f_lbl, fill=theme['text'])
        ty += 36
    ty += 4
    for ln in wrapped_sub:
        sd.text((pad + 32, ty), ln, font=f_sub, fill=theme['subtext'])
        ty += 26

    count_dur = min(1.25, max(0.70, dur * 0.45))

    def frame_fn(t, _total_d):
        e = ease_out_quint(t / count_dur)
        frame = shell.copy()
        fd = ImageDraw.Draw(frame)
        disp = format_stat_number(prefix, target_num * e, decimals, use_dots, suffix) if target_num is not None else strip_emoji(raw_val)
        fd.text((pad + 32, pad + 56), disp, font=f_val, fill=theme['text'])

        fill_w = int(bar_max_w * prog_target * e)
        if fill_w > 2:
            fd.line((bar_x0, bar_y, bar_x0 + fill_w, bar_y), fill=theme['accent'], width=3)
            # Precision leading telemetry dot
            cx = bar_x0 + fill_w
            fd.ellipse((cx - 4, bar_y - 4, cx + 4, bar_y + 4), fill=theme['accent'])
        return frame

    vid = encode_rgba_motion(cw, ch, dur, frame_fn, mov_path, png_path)
    return {'video': vid, 'png': png_path, 'x': ox, 'y': oy}


# ---------------------------------------------------------------------------
# 6. Swiss Editorial Staggered Brief (`checklist` / `steps_card`)
# ---------------------------------------------------------------------------

def build_motion_checklist(ov, theme, dur, mov_path, png_path):
    """Single clean smoked-glass architectural brief with drawing hairline dividers (no nested boxy clutter!)."""
    pos = (ov.get('position') or 'right').lower()
    tag = clean_tvc_kicker(ov.get('tag') or ov.get('category') or 'ĐIỂM CẦN LƯU Ý', ' TÓM TẮT')
    title = strip_emoji(ov.get('title') or 'Điểm chính')
    raw_items = [strip_emoji(x) for x in (ov.get('items') or []) if strip_emoji(x)][:4]
    if not raw_items:
        raw_items = [strip_emoji(ov.get('text') or 'Chi tiết trải nghiệm thực tế')]
    stagger = float(ov.get('stagger', min(0.58, max(0.28, (dur - 0.9) / max(1, len(raw_items))))))

    pad = 26
    card_w = 660
    row_h = 74
    card_h = 128 + len(raw_items) * row_h + 18
    cw, ch = card_w + pad * 2, card_h + pad * 2
    ox = (88 - pad) if pos == 'left' else (1920 - 88 - card_w - pad)
    oy = max(86 - pad, (1040 - ch) // 2)

    shell = make_tvc_glass_plate(cw, ch, (pad, pad, pad + card_w, pad + card_h), theme, radius=16)
    sd = ImageDraw.Draw(shell)
    draw_tvc_kicker(sd, pad + 32, pad + 24, tag, theme, font_size=14)
    title_strip = make_text_strip(title, load_font(31, 'heavy'), theme['text'], pad_y=6)

    f_idx = load_font(19, 'bold')
    f_item = load_font(23, 'medium')
    rw = card_w - 64

    row_sprites = []
    for idx, item_txt in enumerate(raw_items):
        sp = Image.new('RGBA', (rw, row_h), (0, 0, 0, 0))
        rd = ImageDraw.Draw(sp)
        draw_tracked_text(rd, (0, 24), f'{idx + 1:02d}', f_idx, theme['accent'], tracking=2.0)
        lines = textwrap.wrap(item_txt, width=38)[:2]
        if len(lines) == 1:
            rd.text((48, 22), lines[0], font=f_item, fill=theme['text'])
        else:
            rd.text((48, 10), lines[0], font=f_item, fill=theme['text'])
            rd.text((48, 38), lines[1], font=f_item, fill=theme['subtext'])
        row_sprites.append(sp)

    def frame_fn(t, _total_d):
        frame = shell.copy()
        fd = ImageDraw.Draw(frame)
        paste_masked_reveal(frame, title_strip, (pad + 32, pad + 50), t / 0.45)

        for idx, sp in enumerate(row_sprites):
            t0 = 0.16 + idx * stagger
            if t < t0:
                continue
            ry = pad + 118 + idx * row_h
            # Hairline top rule draws across horizontally
            he = ease_out_quint((t - t0) / 0.42)
            hw = int(rw * he)
            if hw > 4:
                fd.line((pad + 32, ry, pad + 32 + hw, ry), fill=theme['hairline'], width=1)
            # Row text rises softly
            re_p = ease_out_quint((t - t0) / 0.46)
            dy = int(round((1.0 - re_p) * 16))
            frame.alpha_composite(scale_alpha(sp, min(1.0, (t - t0) / 0.28)), dest=(pad + 32, ry + dy))
        return frame

    vid = encode_rgba_motion(cw, ch, dur, frame_fn, mov_path, png_path, peak_ratio=0.82)
    return {'video': vid, 'png': png_path, 'x': ox, 'y': oy}


# ---------------------------------------------------------------------------
# 7. Architectural Split Comparison Sheet (`comparison`)
# ---------------------------------------------------------------------------

def build_motion_comparison(ov, theme, dur, mov_path, png_path):
    """Unified smoked-glass architectural panel divided by a 1px vertical rule — sleek documentary look."""
    pos = (ov.get('position') or 'center').lower()
    left_tag = clean_tvc_kicker(ov.get('left_tag') or 'THÔNG THƯỜNG', 'SO SÁNH')
    right_tag = clean_tvc_kicker(ov.get('right_tag') or 'ĐIỂM NỔI BẬT', 'ĐÁNH GIÁ')
    left_title = strip_emoji(ov.get('left_title') or 'Trước đây')
    right_title = strip_emoji(ov.get('right_title') or 'Trải nghiệm thực tế')
    left_items = [strip_emoji(x) for x in (ov.get('left_items') or []) if strip_emoji(x)][:3]
    right_items = [strip_emoji(x) for x in (ov.get('right_items') or []) if strip_emoji(x)][:3]
    split_delay = float(ov.get('split_delay', 0.60))

    pad = 26
    card_w = 1060 if pos == 'center' else 880
    col_w = card_w // 2
    max_rows = max(1, len(left_items), len(right_items))
    card_h = 148 + max_rows * 62 + 24
    cw, ch = card_w + pad * 2, card_h + pad * 2

    if pos == 'right':
        ox = 1920 - 88 - card_w - pad
    elif pos == 'left':
        ox = 88 - pad
    else:
        ox = (1920 - cw) // 2
    oy = (1000 - ch) // 2

    shell = make_tvc_glass_plate(cw, ch, (pad, pad, pad + card_w, pad + card_h), theme, radius=16)

    f_title = load_font(28, 'bold')
    f_item = load_font(22, 'medium')

    def render_col_content(kicker_txt, head_txt, items, is_accent):
        sp = Image.new('RGBA', (col_w - 48, card_h - 40), (0, 0, 0, 0))
        d = ImageDraw.Draw(sp)
        if is_accent:
            draw_tvc_kicker(d, 0, 4, kicker_txt, theme, font_size=14)
        else:
            draw_tracked_text(d, (0, 4), kicker_txt, load_font(14, 'demi'), theme['subtext'], tracking=3.0)
        d.text((0, 34), head_txt, font=f_title, fill=theme['text'] if is_accent else theme['subtext'])
        d.line((0, 82, col_w - 64, 82), fill=theme['accent'] if is_accent else theme['hairline'], width=2 if is_accent else 1)

        iy = 104
        for it in items:
            wrapped = textwrap.wrap(it, width=32 if pos != 'center' else 38)[:2]
            dash_c = theme['accent'] if is_accent else theme['subtext']
            d.line((0, iy + 14, 12, iy + 14), fill=dash_c, width=2)
            for li, ln in enumerate(wrapped):
                d.text((24, iy + li * 26), ln, font=f_item, fill=theme['text'] if is_accent else theme['subtext'])
            iy += 60
        return sp

    left_sp = render_col_content(left_tag, left_title, left_items, is_accent=False)
    right_sp = render_col_content(right_tag, right_title, right_items, is_accent=True)

    def frame_fn(t, _total_d):
        frame = shell.copy()
        fd = ImageDraw.Draw(frame)

        # Left column reveals immediately
        le = ease_out_quint(t / 0.48)
        frame.alpha_composite(scale_alpha(left_sp, min(1.0, t / 0.30)), dest=(pad + 32, pad + 24 + int((1 - le) * 14)))

        # Center vertical hairline divider grows downward
        vh = int((card_h - 48) * ease_out_quint(t / 0.55))
        if vh > 4:
            fd.line((pad + col_w, pad + 24, pad + col_w, pad + 24 + vh), fill=theme['hairline'], width=1)

        # Right column illuminates on second beat
        if t >= split_delay:
            re_p = ease_out_quint((t - split_delay) / 0.50)
            dy = int(round((1.0 - re_p) * 16))
            frame.alpha_composite(
                scale_alpha(right_sp, min(1.0, (t - split_delay) / 0.30)),
                dest=(pad + col_w + 32, pad + 24 + dy)
            )
        return frame

    vid = encode_rgba_motion(cw, ch, dur, frame_fn, mov_path, png_path, peak_ratio=0.80)
    return {'video': vid, 'png': png_path, 'x': ox, 'y': oy, 'split_delay': split_delay}


# ---------------------------------------------------------------------------
# 8. Documentary Editorial Pull-Quote (`kinetic_quote`)
# ---------------------------------------------------------------------------

def build_motion_kinetic_quote(ov, theme, dur, mov_path, png_path):
    tag = clean_tvc_kicker(ov.get('tag') or ov.get('category') or ' GÓC NHÌN', 'GÓC NHÌN')
    quote = strip_emoji(ov.get('quote') or ov.get('text') or ov.get('title') or '')
    author = strip_emoji(ov.get('author') or ov.get('subtitle') or '')

    pad = 26
    card_w = 1120
    lines = textwrap.wrap(quote, width=48)[:2]
    card_h = 136 + len(lines) * 48 + (36 if author else 0)
    cw, ch = card_w + pad * 2, card_h + pad * 2
    ox = (1920 - cw) // 2
    oy = (690 if ov.get('position') != 'top' else 108) - pad

    shell = make_tvc_glass_plate(cw, ch, (pad, pad, pad + card_w, pad + card_h), theme, radius=14)
    f_q = load_font(34, 'bold')
    f_au = load_font(21, 'medium')
    line_strips = [make_text_strip(ln, f_q, theme['text'], pad_y=6) for ln in lines]
    au_strip = make_text_strip(f'—  {author}', f_au, theme['subtext'], pad_y=4) if author else None

    def frame_fn(t, _total_d):
        frame = shell.copy()
        fd = ImageDraw.Draw(frame)

        # Growing 3px vertical left gold bar
        vh = int((card_h - 40) * ease_out_quint(t / 0.55))
        if vh > 4:
            fd.rectangle((pad + 22, pad + 20, pad + 25, pad + 20 + vh), fill=theme['accent'])

        if t > 0.05:
            kl = Image.new('RGBA', (card_w, 28), (0, 0, 0, 0))
            draw_tvc_kicker(ImageDraw.Draw(kl), 0, 4, tag, theme, font_size=14)
            frame.alpha_composite(scale_alpha(kl, ease_out_cubic((t - 0.05) / 0.36)), dest=(pad + 44, pad + 22))

        qy = pad + 56
        for idx, st_im in enumerate(line_strips):
            t0 = 0.12 + idx * 0.11
            if t > t0:
                paste_masked_reveal(frame, st_im, (pad + 44, qy), (t - t0) / 0.52)
            qy += 48

        if au_strip and t > 0.32:
            paste_masked_reveal(frame, au_strip, (pad + 44, qy + 8), (t - 0.32) / 0.45)
        return frame

    vid = encode_rgba_motion(cw, ch, dur, frame_fn, mov_path, png_path)
    return {'video': vid, 'png': png_path, 'x': ox, 'y': oy}


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
    # Cinema documentary subtitle styling: subtle translucent smoked pill or crisp 2.2px optical outline, never chunky blocks
    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Be Vietnam Pro,42,&H00F8FAFC,&H004EB6EE,&H00101216,&H800A0C10,-1,0,0,0,100,100,0.4,0,1,2.4,1.2,2,110,110,52,1

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
        txt = it['text'].replace('\n', '\\N')
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

    look_name = gcfg.get('look') or cfg.get('defaultLook') or 'vibrant_vlog'
    theme = THEMES.get(look_name, THEMES['vibrant_vlog'])

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

        # Restrained TVC sound design (lower, airier volumes <= 0.22 so SFX feel cinematic, never loud)
        if otype == 'intro':
            res = build_tvc_intro(ov, theme, dur, mov_path, png_path)
            entry.update(res)
            sfx = [('whoosh-short', start, 0.22)]
        elif otype == 'chapter':
            res = build_tvc_chapter(ov, theme, dur, mov_path, png_path)
            entry.update(res)
            sfx = [('whoosh-short', start, 0.20)]
        elif otype == 'lower_third':
            res = build_tvc_lower_third(ov, theme, dur, mov_path, png_path)
            entry.update(res)
            sfx = [('click-soft', start, 0.20)]
        elif otype == 'visual_card':
            res = build_motion_visual_card(ov, theme, proj, dur, mov_path, png_path)
            entry.update(res)
            sfx = [('whoosh-short', start, 0.18)]
        elif otype == 'stat_card':
            res = build_motion_stat_card(ov, theme, dur, mov_path, png_path)
            entry.update(res)
            sfx = [('click-soft', start, 0.20)]
        elif otype in ('checklist', 'steps_card'):
            res = build_motion_checklist(ov, theme, dur, mov_path, png_path)
            entry.update(res)
            sfx = [('click-soft', start, 0.20)]
        elif otype == 'comparison':
            res = build_motion_comparison(ov, theme, dur, mov_path, png_path)
            entry.update(res)
            sfx = [('whoosh-short', start, 0.18), ('click-soft', start + res.get('split_delay', 0.60), 0.18)]
        elif otype == 'kinetic_quote':
            res = build_motion_kinetic_quote(ov, theme, dur, mov_path, png_path)
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
            img = render_callout(ov, theme)
            img.save(png_path, 'PNG')
            sfx = [('click-soft', start, 0.20)]
        elif otype == 'subscribe':
            img = render_subscribe(ov, theme, cfg)
            img.save(png_path, 'PNG')
            sfx = [('click-soft', start, 0.20), ('click', start + 0.75, 0.22)]
        else:
            res = build_tvc_lower_third(ov, theme, dur, mov_path, png_path)
            entry.update(res)
            sfx = [('click-soft', start, 0.20)]

        manifest['overlays'].append(entry)
        for s_name, s_time, s_vol in sfx:
            manifest['sfx_events'].append({'name': s_name, 'time': round(s_time, 3), 'volume': s_vol})
        out_asset = os.path.basename(entry['video'] or entry['png'])
        kind_tag = 'TVC-MOTION' if entry.get('video') else 'TVC-PLATE '
        print(f'[{start:6.2f}s - {end:6.2f}s] [{kind_tag}] {otype:14s} -> {out_asset}', flush=True)

    manifest_path = os.path.join(work, 'graphics_manifest.json')
    with open(manifest_path, 'w', encoding='utf-8') as fh:
        json.dump(manifest, fh, indent=2, ensure_ascii=False)


if __name__ == '__main__':
    main()
