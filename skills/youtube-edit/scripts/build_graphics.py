#!/usr/bin/env python3
"""Generate 1920x1080 RGBA YouTube graphics & animated motion cards:
  Static-shell + slide cards: intro, chapter, lower_third, callout, subscribe
  Multi-frame RGBA motion cards (.mov qtrle argb + peak .png):
    - visual_card   (Framed AI illustration / photo PiP card with live inner Ken Burns zoom)
    - stat_card     (Animated counting hero metric + filling progress bar)
    - checklist     (Staggered step-by-step / key takeaways reveal; alias: steps_card)
    - comparison    (Two-stage Before vs. After / Pros vs. Cons split card)
    - kinetic_quote (Editorial thesis / pull-quote card with sweeping accent bar)
    - custom_motion (Pass-through transparent .webm / .mov motion graphic)
Plus .ass Vietnamese subtitles from <project_dir>/graphics.json and <project_dir>/segments.json.

Usage:
  PY build_graphics.py <project_dir>
"""
import json
import os
import re
import shutil
import subprocess
import sys
import textwrap
import unicodedata
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_FILE = os.path.join(SKILL_DIR, 'config.json')
PLATFORM_FILE = os.path.join(SKILL_DIR, '.platform.json')
FONTS_DIR = os.path.join(SKILL_DIR, 'assets', 'fonts')
MOTION_FPS = 30

THEMES = {
    'vibrant_vlog': {
        'accent': (255, 184, 0, 255),        # Warm Amber Gold #FFB800
        'accent_text': (18, 20, 26, 255),
        'badge_red': (239, 68, 68, 255),     # YouTube Red #EF4444
        'surface': (18, 20, 28, 234),        # Deep Charcoal Glass
        'surface_alt': (30, 34, 46, 242),
        'border': (255, 255, 255, 58),
        'text': (255, 255, 255, 255),
        'subtext': (235, 230, 220, 255),
    },
    'cinema_travel': {
        'accent': (243, 201, 105, 255),      # Champagne Gold #F3C969
        'accent_text': (15, 18, 24, 255),
        'badge_red': (220, 53, 69, 255),
        'surface': (12, 16, 22, 236),
        'surface_alt': (24, 32, 42, 242),
        'border': (243, 201, 105, 72),
        'text': (250, 247, 242, 255),
        'subtext': (216, 207, 194, 255),
    },
    'clean_studio': {
        'accent': (56, 189, 248, 255),       # Electric Cyan #38BDF8
        'accent_text': (12, 18, 30, 255),
        'badge_red': (239, 68, 68, 255),
        'surface': (15, 23, 42, 236),
        'surface_alt': (30, 41, 59, 242),
        'border': (148, 163, 184, 68),
        'text': (255, 255, 255, 255),
        'subtext': (203, 213, 225, 255),
    },
    'film_kodak': {
        'accent': (224, 122, 95, 255),       # Terracotta #E07A5F
        'accent_text': (255, 253, 249, 255),
        'badge_red': (214, 69, 65, 255),
        'surface': (24, 20, 18, 236),
        'surface_alt': (38, 32, 28, 242),
        'border': (224, 122, 95, 75),
        'text': (253, 251, 247, 255),
        'subtext': (222, 214, 202, 255),
    },
    'minimal_editorial': {
        'accent': (217, 78, 52, 255),        # Editorial Vermilion #D94E34
        'accent_text': (255, 255, 255, 255),
        'badge_red': (217, 78, 52, 255),
        'surface': (246, 243, 236, 245),     # Warm Ivory Paper Surface
        'surface_alt': (234, 229, 218, 248),
        'border': (24, 24, 27, 45),
        'text': (24, 24, 27, 255),           # Deep Ink Text
        'subtext': (82, 82, 91, 255),
    },
    'warm_food': {
        'accent': (245, 158, 11, 255),       # Saffron Gold #F59E0B
        'accent_text': (20, 16, 14, 255),
        'badge_red': (239, 68, 68, 255),
        'surface': (22, 18, 16, 236),
        'surface_alt': (36, 28, 24, 242),
        'border': (245, 158, 11, 72),
        'text': (255, 253, 249, 255),
        'subtext': (235, 225, 212, 255),
    },
}


def get_ffmpeg():
    if os.path.isfile(PLATFORM_FILE):
        try:
            with open(PLATFORM_FILE, encoding='utf-8') as fh:
                ff = json.load(fh).get('ffmpeg')
                if ff and os.path.isfile(ff):
                    return ff
        except Exception:
            pass
    sib = os.path.join(os.path.dirname(SKILL_DIR), 'video-edit', '.platform.json')
    if os.path.isfile(sib):
        try:
            with open(sib, encoding='utf-8') as fh:
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


def scale_alpha(img, alpha_factor):
    """Multiply the alpha channel of an RGBA image by alpha_factor (0.0..1.0)."""
    if alpha_factor >= 0.999:
        return img
    if alpha_factor <= 0.001:
        return Image.new('RGBA', img.size, (0, 0, 0, 0))
    r, g, b, a = img.split()
    a = a.point(lambda v: int(v * alpha_factor))
    return Image.merge('RGBA', (r, g, b, a))


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
                frame_fn(total_dur * 0.6, total_dur - 0.15).save(png_path, 'PNG')
            return mov_path
    except Exception:
        pass

    # Fallback: save peak static PNG if ffmpeg pipe unavailable
    peak_frame = frame_fn((total_dur - 0.15) * peak_ratio, total_dur - 0.15)
    peak_frame.save(png_path, 'PNG')
    return None


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


def add_shadow(canvas, box, radius=24, blur=24, offset=(0, 12), alpha=120):
    shadow = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    x0, y0, x1, y1 = box
    ox, oy = offset
    sd.rounded_rectangle((x0 + ox, y0 + oy, x1 + ox, y1 + oy), radius=radius, fill=(0, 0, 0, alpha))
    shadow = shadow.filter(ImageFilter.GaussianBlur(blur))
    return Image.alpha_composite(canvas, shadow)


def strip_emoji(text):
    """Normalize Vietnamese NFC and strip supplementary plane emojis so vector fonts never render tofu boxes."""
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


# ---------------------------------------------------------------------------
# Classic 16:9 YouTube Cards (1920x1080 RGBA)
# ---------------------------------------------------------------------------

def render_intro(ov, theme):
    img = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))
    scrim = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))
    sd = ImageDraw.Draw(scrim)
    sd.rounded_rectangle((180, 310, 1740, 770), radius=36, fill=(10, 12, 18, 195))
    scrim = scrim.filter(ImageFilter.GaussianBlur(8))
    img = Image.alpha_composite(img, scrim)

    img = add_shadow(img, (210, 330, 1710, 750), radius=32, blur=28, alpha=140)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((210, 330, 1710, 750), radius=32, fill=theme['surface'], outline=theme['border'], width=2)

    badge = strip_emoji(ov.get('badge', 'VLOG REVIEW')).upper()
    f_badge = load_font(26, 'bold')
    f_title = load_font(68, 'heavy')
    f_sub = load_font(34, 'medium')

    bb = d.textbbox((0, 0), badge, font=f_badge)
    bw = (bb[2] - bb[0]) + 56
    bx0 = 960 - bw // 2
    d.rounded_rectangle((bx0, 372, bx0 + bw, 428), radius=28, fill=theme['accent'])
    d.text((960, 400), badge, font=f_badge, fill=theme['accent_text'], anchor='mm')

    title = strip_emoji(ov.get('title', '')).upper()
    if len(title) > 36:
        f_title = load_font(56, 'heavy')
    d.text((960, 525), title, font=f_title, fill=theme['text'], anchor='mm')

    d.rounded_rectangle((860, 595, 1060, 603), radius=4, fill=theme['accent'])

    sub = strip_emoji(ov.get('subtitle', ''))
    if sub:
        d.text((960, 665), sub, font=f_sub, fill=theme['subtext'], anchor='mm')
    return img


def render_chapter(ov, theme):
    img = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))
    num = strip_emoji(ov.get('number', '01')).upper()
    if not num.startswith('CHƯƠNG') and len(num) <= 3:
        num_label = f'CHƯƠNG {num}'
    else:
        num_label = num
    title = strip_emoji(ov.get('title', ''))
    sub = strip_emoji(ov.get('subtitle', ''))

    f_num = load_font(26, 'heavy')
    f_title = load_font(44, 'bold')
    f_sub = load_font(28, 'medium')

    tmp_d = ImageDraw.Draw(img)
    tb = tmp_d.textbbox((0, 0), title, font=f_title)
    sb = tmp_d.textbbox((0, 0), sub, font=f_sub) if sub else (0, 0, 0, 0)
    card_w = max(560, max(tb[2] - tb[0], sb[2] - sb[0]) + 120)
    card_w = min(card_w, 1200)

    x0, y0 = 88, 760
    x1, y1 = x0 + card_w, 945
    img = add_shadow(img, (x0, y0, x1, y1), radius=24, blur=22, alpha=130)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((x0, y0, x1, y1), radius=24, fill=theme['surface'], outline=theme['border'], width=2)
    d.rounded_rectangle((x0, y0, x0 + 14, y1), radius=7, fill=theme['accent'])

    nb = d.textbbox((0, 0), num_label, font=f_num)
    nw = (nb[2] - nb[0]) + 36
    d.rounded_rectangle((x0 + 38, y0 + 22, x0 + 38 + nw, y0 + 64), radius=12, fill=theme['accent'])
    d.text((x0 + 38 + nw // 2, y0 + 43), num_label, font=f_num, fill=theme['accent_text'], anchor='mm')

    if sub:
        d.text((x0 + 38, y0 + 82), title, font=f_title, fill=theme['text'])
        d.text((x0 + 38, y0 + 138), sub, font=f_sub, fill=theme['subtext'])
    else:
        d.text((x0 + 38, y0 + 96), title, font=f_title, fill=theme['text'])
    return img


def render_lower_third(ov, theme):
    img = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))
    cat = strip_emoji(ov.get('category', 'ĐỊA ĐIỂM & ẨM THỰC')).upper()
    title = strip_emoji(ov.get('title', ''))
    loc = strip_emoji(ov.get('location', ''))
    price = strip_emoji(ov.get('price', ''))
    rating = strip_emoji(ov.get('rating', ''))

    f_cat = load_font(22, 'bold')
    f_title = load_font(44, 'heavy')
    f_meta = load_font(27, 'demi')
    f_rate = load_font(34, 'heavy')

    tmp_d = ImageDraw.Draw(img)
    tb = tmp_d.textbbox((0, 0), title, font=f_title)
    meta_parts = [p for p in (loc, price) if p]
    meta_str = '   •   '.join(meta_parts)
    mb = tmp_d.textbbox((0, 0), meta_str, font=f_meta) if meta_str else (0, 0, 0, 0)

    extra_right = 190 if rating else 56
    card_w = max(620, max(tb[2] - tb[0], mb[2] - mb[0]) + 64 + extra_right)
    card_w = min(card_w, 1340)

    x0, y0 = 88, 745
    x1, y1 = x0 + card_w, 950
    img = add_shadow(img, (x0, y0, x1, y1), radius=26, blur=24, alpha=135)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((x0, y0, x1, y1), radius=26, fill=theme['surface'], outline=theme['border'], width=2)
    d.rounded_rectangle((x0, y0, x0 + 14, y1), radius=7, fill=theme['accent'])

    cb = d.textbbox((0, 0), cat, font=f_cat)
    cw = (cb[2] - cb[0]) + 32
    d.rounded_rectangle((x0 + 36, y0 + 22, x0 + 36 + cw, y0 + 60), radius=10, fill=theme['surface_alt'], outline=theme['accent'], width=2)
    d.text((x0 + 36 + cw // 2, y0 + 41), cat, font=f_cat, fill=theme['accent'], anchor='mm')

    d.text((x0 + 36, y0 + 74), title, font=f_title, fill=theme['text'])

    if meta_str:
        d.text((x0 + 36, y0 + 138), meta_str, font=f_meta, fill=theme['subtext'])

    if rating:
        rx0, ry0 = x1 - 165, y0 + 42
        rx1, ry1 = x1 - 28, y1 - 42
        d.rounded_rectangle((rx0, ry0, rx1, ry1), radius=20, fill=theme['accent'])
        d.text(((rx0 + rx1) // 2, (ry0 + ry1) // 2 - 14), 'ĐÁNH GIÁ', font=load_font(18, 'bold'), fill=theme['accent_text'], anchor='mm')
        d.text(((rx0 + rx1) // 2, (ry0 + ry1) // 2 + 18), rating, font=f_rate, fill=theme['accent_text'], anchor='mm')

    return img


def render_callout(ov, theme):
    img = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))
    pos = ov.get('position', 'top_right')
    tag = strip_emoji(ov.get('icon', 'GHI CHÚ')).upper() or 'MẸO NHỎ'
    title = strip_emoji(ov.get('title', 'Lưu ý'))
    text = strip_emoji(ov.get('text', ''))

    f_tag = load_font(20, 'bold')
    f_title = load_font(32, 'bold')
    f_text = load_font(25, 'medium')

    tmp_d = ImageDraw.Draw(img)
    tb = tmp_d.textbbox((0, 0), tag, font=f_tag)
    tw = (tb[2] - tb[0]) + 26
    ttb = tmp_d.textbbox((0, 0), title, font=f_title)
    header_w = 26 + tw + 14 + (ttb[2] - ttb[0]) + 36

    wrapped = textwrap.wrap(text, width=40)[:2]
    card_w = min(760, max(560, header_w))
    card_h = 175 if len(wrapped) <= 1 else 205
    x0 = 1920 - 88 - card_w if pos == 'top_right' else 88
    y0 = 78
    x1, y1 = x0 + card_w, y0 + card_h

    img = add_shadow(img, (x0, y0, x1, y1), radius=22, blur=20, alpha=125)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((x0, y0, x1, y1), radius=22, fill=theme['surface'], outline=theme['border'], width=2)
    d.rounded_rectangle((x0, y0, x1, y0 + 8), radius=4, fill=theme['accent'])

    d.rounded_rectangle((x0 + 26, y0 + 24, x0 + 26 + tw, y0 + 56), radius=8, fill=theme['accent'])
    d.text((x0 + 26 + tw // 2, y0 + 40), tag, font=f_tag, fill=theme['accent_text'], anchor='mm')

    d.text((x0 + 26 + tw + 14, y0 + 40), title, font=f_title, fill=theme['text'], anchor='lm')

    for idx, line in enumerate(wrapped):
        d.text((x0 + 26, y0 + 76 + idx * 34), line, font=f_text, fill=theme['subtext'])
    return img


def render_subscribe(ov, theme, cfg):
    img = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))
    channel = strip_emoji(ov.get('channel') or cfg.get('channelName') or 'Tuấn Đi Review')
    handle = strip_emoji(ov.get('handle') or cfg.get('channelHandle') or '@tuandireview • Nhấn Đăng Ký kênh nhé!')
    btn_txt = strip_emoji(ov.get('button_text') or 'ĐĂNG KÝ KÊNH').upper()

    f_ch = load_font(34, 'heavy')
    f_hd = load_font(23, 'medium')
    f_btn = load_font(24, 'heavy')

    tmp_d = ImageDraw.Draw(img)
    cb = tmp_d.textbbox((0, 0), channel, font=f_ch)
    hb = tmp_d.textbbox((0, 0), handle, font=f_hd)
    bb = tmp_d.textbbox((0, 0), btn_txt, font=f_btn)
    btn_w = max(230, (bb[2] - bb[0]) + 56)
    text_w = max(cb[2] - cb[0], hb[2] - hb[0])

    card_w = max(860, 144 + text_w + 48 + btn_w + 32)
    card_w = min(card_w, 1360)
    card_h = 136
    x0 = (1920 - card_w) // 2
    y0 = 815
    x1, y1 = x0 + card_w, y0 + card_h

    img = add_shadow(img, (x0, y0, x1, y1), radius=68, blur=24, alpha=140)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((x0, y0, x1, y1), radius=68, fill=theme['surface'], outline=theme['border'], width=2)

    cx, cy, r = x0 + 70, (y0 + y1) // 2, 44
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=theme['accent'])
    initials = ''.join(w[0].upper() for w in channel.split()[:2]) or 'YT'
    d.text((cx, cy), initials, font=load_font(30, 'heavy'), fill=theme['accent_text'], anchor='mm')

    d.text((x0 + 136, y0 + 28), channel, font=f_ch, fill=theme['text'])
    d.text((x0 + 136, y0 + 76), handle, font=f_hd, fill=theme['subtext'])

    bx0, by0 = x1 - btn_w - 26, y0 + 28
    bx1, by1 = x1 - 26, y1 - 28
    d.rounded_rectangle((bx0, by0, bx1, by1), radius=40, fill=theme['badge_red'])
    d.text(((bx0 + bx1) // 2, (by0 + by1) // 2), btn_txt, font=f_btn, fill=(255, 255, 255, 255), anchor='mm')
    return img


# ---------------------------------------------------------------------------
# Multi-Frame Animated RGBA Motion & AI Visual Cards
# ---------------------------------------------------------------------------

def make_editorial_placeholder(vw, vh, theme, title_hint=''):
    """Generate a tasteful geometric editorial visual if an AI image file is missing."""
    im = Image.new('RGBA', (vw, vh), theme['surface_alt'])
    d = ImageDraw.Draw(im)
    ac = theme['accent']
    # Subtle architectural grid lines
    for x in range(40, vw, 64):
        d.line((x, 0, x, vh), fill=(ac[0], ac[1], ac[2], 24), width=1)
    for y in range(40, vh, 64):
        d.line((0, y, vw, y), fill=(ac[0], ac[1], ac[2], 24), width=1)
    # Soft concentric editorial rings
    cx, cy = int(vw * 0.62), int(vh * 0.46)
    for r, a in ((190, 36), (135, 58), (80, 95)):
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(ac[0], ac[1], ac[2], a), width=3)
    d.ellipse((cx - 28, cy - 28, cx + 28, cy + 28), fill=ac)
    if title_hint:
        d.text((36, vh - 56), title_hint[:28].upper(), font=load_font(22, 'bold'), fill=theme['subtext'])
    return im


def build_motion_visual_card(ov, theme, proj, dur, mov_path, png_path):
    """Framed AI illustration / photo PiP card with live inner Ken Burns zoom + sweeping accent trim."""
    pos = (ov.get('position') or 'right').lower()
    tag = strip_emoji(ov.get('tag') or ov.get('category') or 'GÓC NHÌN MINH HỌA').upper()
    title = strip_emoji(ov.get('title') or '')
    caption = strip_emoji(ov.get('caption') or ov.get('text') or '')

    pad = 28  # outer margin for drop shadow inside tight canvas
    card_w = 820 if pos == 'center' else 680
    wrapped_cap = textwrap.wrap(caption, width=46 if pos == 'center' else 38)[:2]
    text_block_h = (56 if title else 0) + len(wrapped_cap) * 34 + 34
    vp_w = card_w - 48
    vp_h = 420 if pos == 'center' else 380
    card_h = 24 + vp_h + 20 + max(78, text_block_h)

    cw, ch = card_w + pad * 2, card_h + pad * 2
    if pos == 'left':
        ox = 88 - pad
    elif pos == 'center':
        ox = (1920 - cw) // 2
    else:
        ox = 1920 - 88 - card_w - pad
    oy = 118 - pad

    # Load AI image or generate clean editorial artwork
    img_rel = ov.get('image') or ov.get('src') or ''
    img_abs = os.path.join(proj, img_rel) if (img_rel and not os.path.isabs(img_rel)) else img_rel
    if img_abs and os.path.isfile(img_abs):
        try:
            src_im = Image.open(img_abs).convert('RGBA')
        except Exception:
            src_im = make_editorial_placeholder(vp_w + 120, vp_h + 120, theme, title)
    else:
        src_im = make_editorial_placeholder(vp_w + 120, vp_h + 120, theme, title)

    # Pre-scale source image to cover 1.16x viewport for crisp bicubic Ken Burns
    target_w, target_h = int(vp_w * 1.18), int(vp_h * 1.18)
    scale_k = max(target_w / max(1, src_im.width), target_h / max(1, src_im.height))
    pre_w, pre_h = max(target_w, int(src_im.width * scale_k)), max(target_h, int(src_im.height * scale_k))
    src_im = src_im.resize((pre_w, pre_h), Image.LANCZOS)

    # Rounded mask for image viewport
    vp_mask = Image.new('L', (vp_w, vp_h), 0)
    ImageDraw.Draw(vp_mask).rounded_rectangle((0, 0, vp_w, vp_h), radius=20, fill=255)

    # Pre-render static card shell + typography once
    shell = Image.new('RGBA', (cw, ch), (0, 0, 0, 0))
    shell = add_shadow(shell, (pad, pad, pad + card_w, pad + card_h), radius=28, blur=20, offset=(0, 10), alpha=135)
    sd = ImageDraw.Draw(shell)
    sd.rounded_rectangle((pad, pad, pad + card_w, pad + card_h), radius=28, fill=theme['surface'], outline=theme['border'], width=2)

    f_tag = load_font(20, 'bold')
    f_title = load_font(34, 'heavy')
    f_cap = load_font(24, 'medium')

    ty = pad + 24 + vp_h + 18
    if title:
        sd.text((pad + 26, ty), title, font=f_title, fill=theme['text'])
        ty += 48
    for line in wrapped_cap:
        sd.text((pad + 26, ty), line, font=f_cap, fill=theme['subtext'])
        ty += 32

    # Tag pill overlay drawn on top-left corner of viewport
    tag_layer = Image.new('RGBA', (vp_w, vp_h), (0, 0, 0, 0))
    if tag:
        td = ImageDraw.Draw(tag_layer)
        tb = td.textbbox((0, 0), tag, font=f_tag)
        tw = (tb[2] - tb[0]) + 28
        td.rounded_rectangle((16, 16, 16 + tw, 52), radius=10, fill=theme['accent'])
        td.text((16 + tw // 2, 34), tag, font=f_tag, fill=theme['accent_text'], anchor='mm')

    def frame_fn(t, total_d):
        p = min(1.0, max(0.0, t / max(0.5, total_d)))
        # Zoom 1.0 -> 1.11 smoothly across card duration + gentle horizontal drift
        cur_zoom = 1.0 + 0.11 * p
        crop_w = max(16, int(round(vp_w / cur_zoom * 1.14)))
        crop_h = max(16, int(round(vp_h / cur_zoom * 1.14)))
        crop_w = min(pre_w, crop_w)
        crop_h = min(pre_h, crop_h)
        max_dx = max(0, pre_w - crop_w)
        max_dy = max(0, pre_h - crop_h)
        cx0 = int(max_dx * (0.35 + 0.30 * p))
        cy0 = int(max_dy * (0.50 - 0.15 * p))
        cropped = src_im.crop((cx0, cy0, cx0 + crop_w, cy0 + crop_h)).resize((vp_w, vp_h), Image.BICUBIC)
        cropped = Image.alpha_composite(cropped, tag_layer)

        frame = shell.copy()
        frame.paste(cropped, (pad + 24, pad + 24), vp_mask)

        # Animated accent progress bar at bottom of card
        bar_e = ease_out_cubic(min(1.0, t / 0.85))
        bar_w = int((card_w - 52) * bar_e)
        if bar_w > 6:
            fd = ImageDraw.Draw(frame)
            fd.rounded_rectangle(
                (pad + 26, pad + card_h - 14, pad + 26 + bar_w, pad + card_h - 8),
                radius=3, fill=theme['accent']
            )
        return frame

    vid = encode_rgba_motion(cw, ch, dur, frame_fn, mov_path, png_path)
    return {'video': vid, 'png': png_path, 'x': ox, 'y': oy}


def parse_stat_value(val_str):
    """Parse '+85%', '40.000đ', '9.4/10', '3.5x' into (prefix, target_float, decimals, use_dot_thousands, suffix)."""
    s = strip_emoji(val_str or '100%')
    m = re.match(r'^([^\d-]*)(-?\d[\d.,]*)(.*)$', s)
    if not m:
        return '', None, 0, False, s
    prefix, num_part, suffix = m.group(1), m.group(2), m.group(3)
    # Detect Vietnamese thousands separator like '40.000' or '1.250.000'
    if re.match(r'^-?\d{1,3}(\.\d{3})+$', num_part):
        val = float(num_part.replace('.', ''))
        return prefix, val, 0, True, suffix
    clean = num_part.replace(',', '.')
    try:
        val = float(clean)
    except ValueError:
        return '', None, 0, False, s
    decimals = len(clean.split('.')[1]) if '.' in clean else 0
    return prefix, val, min(2, decimals), False, suffix


def format_stat_number(prefix, val, decimals, use_dot_thousands, suffix):
    if use_dot_thousands:
        n = int(round(val))
        formatted = f'{n:,}'.replace(',', '.')
    elif decimals > 0:
        formatted = f'{val:.{decimals}f}'
    else:
        formatted = str(int(round(val)))
    return f'{prefix}{formatted}{suffix}'


def build_motion_stat_card(ov, theme, dur, mov_path, png_path):
    """Hero metric counter card where numbers count up from 0 and progress bar fills smoothly."""
    pos = (ov.get('position') or 'right').lower()
    tag = strip_emoji(ov.get('tag') or ov.get('category') or 'CHỈ SỐ NỔI BẬT').upper()
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
    card_w = 640
    wrapped_lbl = textwrap.wrap(label, width=30)[:2]
    wrapped_sub = textwrap.wrap(subtext, width=38)[:2]
    card_h = 265 + len(wrapped_lbl) * 40 + (len(wrapped_sub) * 30 + 10 if wrapped_sub else 0)
    cw, ch = card_w + pad * 2, card_h + pad * 2

    if pos == 'left':
        ox = 88 - pad
    elif pos == 'center':
        ox = (1920 - cw) // 2
    else:
        ox = 1920 - 88 - card_w - pad
    oy = 215 - pad

    shell = Image.new('RGBA', (cw, ch), (0, 0, 0, 0))
    shell = add_shadow(shell, (pad, pad, pad + card_w, pad + card_h), radius=28, blur=20, offset=(0, 10), alpha=135)
    sd = ImageDraw.Draw(shell)
    sd.rounded_rectangle((pad, pad, pad + card_w, pad + card_h), radius=28, fill=theme['surface'], outline=theme['border'], width=2)
    sd.rounded_rectangle((pad, pad, pad + 12, pad + card_h), radius=6, fill=theme['accent'])

    f_tag = load_font(20, 'bold')
    f_val = load_font(86 if len(raw_val) <= 7 else 68, 'heavy')
    f_lbl = load_font(32, 'bold')
    f_sub = load_font(23, 'medium')

    tb = sd.textbbox((0, 0), tag, font=f_tag)
    tw = (tb[2] - tb[0]) + 30
    sd.rounded_rectangle((pad + 34, pad + 26, pad + 34 + tw, pad + 62), radius=10, fill=theme['accent'])
    sd.text((pad + 34 + tw // 2, pad + 44), tag, font=f_tag, fill=theme['accent_text'], anchor='mm')

    # Progress bar track
    bar_x0, bar_y0 = pad + 34, pad + 196
    bar_max_w = card_w - 68
    sd.rounded_rectangle((bar_x0, bar_y0, bar_x0 + bar_max_w, bar_y0 + 16), radius=8, fill=theme['surface_alt'])

    ty = bar_y0 + 34
    for line in wrapped_lbl:
        sd.text((pad + 34, ty), line, font=f_lbl, fill=theme['text'])
        ty += 40
    ty += 6
    for line in wrapped_sub:
        sd.text((pad + 34, ty), line, font=f_sub, fill=theme['subtext'])
        ty += 30

    count_dur = min(1.15, max(0.65, dur * 0.42))

    def frame_fn(t, _total_d):
        e = ease_out_cubic(t / count_dur)
        frame = shell.copy()
        fd = ImageDraw.Draw(frame)
        if target_num is not None:
            disp = format_stat_number(prefix, target_num * e, decimals, use_dots, suffix)
        else:
            disp = strip_emoji(raw_val)
        fd.text((pad + 34, pad + 78), disp, font=f_val, fill=theme['accent'])

        fill_w = int(bar_max_w * prog_target * e)
        if fill_w > 10:
            fd.rounded_rectangle((bar_x0, bar_y0, bar_x0 + fill_w, bar_y0 + 16), radius=8, fill=theme['accent'])
        return frame

    vid = encode_rgba_motion(cw, ch, dur, frame_fn, mov_path, png_path)
    return {'video': vid, 'png': png_path, 'x': ox, 'y': oy}


def build_motion_checklist(ov, theme, dur, mov_path, png_path):
    """Staggered step-by-step / key takeaways card where items reveal one by one."""
    pos = (ov.get('position') or 'right').lower()
    tag = strip_emoji(ov.get('tag') or ov.get('category') or 'ĐIỂM CHÍNH').upper()
    title = strip_emoji(ov.get('title') or 'Tóm tắt nhanh')
    raw_items = [strip_emoji(x) for x in (ov.get('items') or []) if strip_emoji(x)][:4]
    if not raw_items:
        raw_items = [strip_emoji(ov.get('text') or 'Điểm nổi bật cần lưu ý')]
    stagger = float(ov.get('stagger', min(0.62, max(0.30, (dur - 0.9) / max(1, len(raw_items))))))

    pad = 26
    card_w = 700
    row_h = 82
    card_h = 148 + len(raw_items) * (row_h + 12) + 16
    cw, ch = card_w + pad * 2, card_h + pad * 2
    ox = (88 - pad) if pos == 'left' else (1920 - 88 - card_w - pad)
    oy = max(84 - pad, (1040 - ch) // 2)

    shell = Image.new('RGBA', (cw, ch), (0, 0, 0, 0))
    shell = add_shadow(shell, (pad, pad, pad + card_w, pad + card_h), radius=28, blur=20, offset=(0, 10), alpha=135)
    sd = ImageDraw.Draw(shell)
    sd.rounded_rectangle((pad, pad, pad + card_w, pad + card_h), radius=28, fill=theme['surface'], outline=theme['border'], width=2)

    f_tag = load_font(19, 'bold')
    f_title = load_font(34, 'heavy')
    f_num = load_font(22, 'heavy')
    f_item = load_font(25, 'demi')

    tb = sd.textbbox((0, 0), tag, font=f_tag)
    tw = (tb[2] - tb[0]) + 28
    sd.rounded_rectangle((pad + 30, pad + 24, pad + 30 + tw, pad + 58), radius=9, fill=theme['accent'])
    sd.text((pad + 30 + tw // 2, pad + 41), tag, font=f_tag, fill=theme['accent_text'], anchor='mm')
    sd.text((pad + 30, pad + 72), title, font=f_title, fill=theme['text'])

    # Pre-render each row sprite once for super-fast compositing
    row_sprites = []
    rw = card_w - 60
    for idx, item_txt in enumerate(raw_items):
        sp = Image.new('RGBA', (rw, row_h), (0, 0, 0, 0))
        rd = ImageDraw.Draw(sp)
        rd.rounded_rectangle((0, 0, rw, row_h), radius=16, fill=theme['surface_alt'], outline=theme['border'], width=1)
        rd.rounded_rectangle((14, 17, 62, 65), radius=12, fill=theme['accent'])
        rd.text((38, 41), f'{idx + 1:02d}', font=f_num, fill=theme['accent_text'], anchor='mm')
        lines = textwrap.wrap(item_txt, width=36)[:2]
        if len(lines) == 1:
            rd.text((80, 41), lines[0], font=f_item, fill=theme['text'], anchor='lm')
        else:
            rd.text((80, 26), lines[0], font=f_item, fill=theme['text'], anchor='lm')
            rd.text((80, 56), lines[1], font=f_item, fill=theme['subtext'], anchor='lm')
        row_sprites.append(sp)

    def frame_fn(t, _total_d):
        frame = shell.copy()
        for idx, sp in enumerate(row_sprites):
            t_start = 0.14 + idx * stagger
            if t < t_start:
                continue
            e = ease_out_cubic((t - t_start) / 0.34)
            dx = int(round((1.0 - e) * 26))
            faded = scale_alpha(sp, e)
            ry = pad + 136 + idx * (row_h + 12)
            frame.alpha_composite(faded, dest=(pad + 30 + dx, ry))
        return frame

    vid = encode_rgba_motion(cw, ch, dur, frame_fn, mov_path, png_path, peak_ratio=0.82)
    return {'video': vid, 'png': png_path, 'x': ox, 'y': oy}


def build_motion_comparison(ov, theme, dur, mov_path, png_path):
    """Two-stage Before vs. After / Pros vs. Cons split motion card."""
    pos = (ov.get('position') or 'center').lower()
    left_tag = strip_emoji(ov.get('left_tag') or 'TRƯỚC ĐÂY').upper()
    right_tag = strip_emoji(ov.get('right_tag') or 'HIỆN TẠI').upper()
    left_title = strip_emoji(ov.get('left_title') or 'Cách thông thường')
    right_title = strip_emoji(ov.get('right_title') or 'Điểm nâng cấp')
    left_items = [strip_emoji(x) for x in (ov.get('left_items') or []) if strip_emoji(x)][:3]
    right_items = [strip_emoji(x) for x in (ov.get('right_items') or []) if strip_emoji(x)][:3]
    split_delay = float(ov.get('split_delay', 0.65))

    pad = 26
    col_w = 460 if pos != 'center' else 540
    gap = 24
    total_w = col_w * 2 + gap
    max_rows = max(1, len(left_items), len(right_items))
    col_h = 165 + max_rows * 66 + 22
    cw, ch = total_w + pad * 2, col_h + pad * 2

    if pos == 'right':
        ox = 1920 - 88 - total_w - pad
    elif pos == 'left':
        ox = 88 - pad
    else:
        ox = (1920 - cw) // 2
    oy = (1000 - ch) // 2

    f_tag = load_font(19, 'bold')
    f_title = load_font(31, 'heavy')
    f_item = load_font(23, 'medium')

    def make_col(tag_txt, head_txt, items, is_right):
        sp = Image.new('RGBA', (col_w + pad * 2, col_h + pad * 2), (0, 0, 0, 0))
        sp = add_shadow(sp, (pad, pad, pad + col_w, pad + col_h), radius=26, blur=18, offset=(0, 10), alpha=130)
        d = ImageDraw.Draw(sp)
        border_c = theme['accent'] if is_right else theme['border']
        bw = 3 if is_right else 2
        d.rounded_rectangle((pad, pad, pad + col_w, pad + col_h), radius=26, fill=theme['surface'], outline=border_c, width=bw)

        tb = d.textbbox((0, 0), tag_txt, font=f_tag)
        tw = (tb[2] - tb[0]) + 28
        pill_fill = theme['accent'] if is_right else theme['surface_alt']
        pill_txt = theme['accent_text'] if is_right else theme['subtext']
        d.rounded_rectangle((pad + 28, pad + 24, pad + 28 + tw, pad + 58), radius=9, fill=pill_fill)
        d.text((pad + 28 + tw // 2, pad + 41), tag_txt, font=f_tag, fill=pill_txt, anchor='mm')

        d.text((pad + 28, pad + 74), head_txt, font=f_title, fill=theme['text'])
        d.line((pad + 28, pad + 126, pad + col_w - 28, pad + 126), fill=theme['border'], width=1)

        iy = pad + 148
        bullet_c = theme['accent'] if is_right else theme['subtext']
        for it in items:
            wrapped = textwrap.wrap(it, width=32 if pos != 'center' else 38)[:2]
            d.ellipse((pad + 28, iy + 10, pad + 40, iy + 22), fill=bullet_c)
            for li, ln in enumerate(wrapped):
                d.text((pad + 54, iy + li * 28), ln, font=f_item, fill=theme['text'] if is_right else theme['subtext'])
            iy += 66
        return sp

    left_sp = make_col(left_tag, left_title, left_items, is_right=False)
    right_sp = make_col(right_tag, right_title, right_items, is_right=True)

    def frame_fn(t, _total_d):
        frame = Image.new('RGBA', (cw, ch), (0, 0, 0, 0))
        frame.alpha_composite(left_sp, dest=(0, 0))
        if t >= split_delay:
            e = ease_out_cubic((t - split_delay) / 0.36)
            dy = int(round((1.0 - e) * 24))
            faded_r = scale_alpha(right_sp, e)
            frame.alpha_composite(faded_r, dest=(col_w + gap, dy))
        return frame

    vid = encode_rgba_motion(cw, ch, dur, frame_fn, mov_path, png_path, peak_ratio=0.78)
    return {'video': vid, 'png': png_path, 'x': ox, 'y': oy, 'split_delay': split_delay}


def build_motion_kinetic_quote(ov, theme, dur, mov_path, png_path):
    """Editorial pull-quote / key-thesis highlight banner with sweeping accent bars."""
    tag = strip_emoji(ov.get('tag') or ov.get('category') or 'ĐIỂM CỐT LÕI').upper()
    quote = strip_emoji(ov.get('quote') or ov.get('text') or ov.get('title') or '')
    author = strip_emoji(ov.get('author') or ov.get('subtitle') or '')

    pad = 26
    card_w = 1140
    lines = textwrap.wrap(quote, width=46)[:2]
    card_h = 160 + len(lines) * 52 + (40 if author else 0)
    cw, ch = card_w + pad * 2, card_h + pad * 2
    ox = (1920 - cw) // 2
    oy = (680 if ov.get('position') != 'top' else 110) - pad

    shell = Image.new('RGBA', (cw, ch), (0, 0, 0, 0))
    shell = add_shadow(shell, (pad, pad, pad + card_w, pad + card_h), radius=26, blur=22, offset=(0, 10), alpha=140)
    sd = ImageDraw.Draw(shell)
    sd.rounded_rectangle((pad, pad, pad + card_w, pad + card_h), radius=26, fill=theme['surface'], outline=theme['border'], width=2)

    f_tag = load_font(19, 'bold')
    f_q = load_font(38, 'heavy')
    f_au = load_font(24, 'medium')

    tb = sd.textbbox((0, 0), tag, font=f_tag)
    tw = (tb[2] - tb[0]) + 28
    sd.rounded_rectangle((pad + 40, pad + 24, pad + 40 + tw, pad + 58), radius=9, fill=theme['accent'])
    sd.text((pad + 40 + tw // 2, pad + 41), tag, font=f_tag, fill=theme['accent_text'], anchor='mm')

    qy = pad + 78
    max_line_w = 240
    for ln in lines:
        lb = sd.textbbox((0, 0), ln, font=f_q)
        max_line_w = max(max_line_w, lb[2] - lb[0])
        sd.text((pad + 40, qy), ln, font=f_q, fill=theme['text'])
        qy += 52

    if author:
        sd.text((pad + 40, qy + 14), f'— {author}', font=f_au, fill=theme['subtext'])

    def frame_fn(t, _total_d):
        e = ease_out_cubic(t / 0.65)
        frame = shell.copy()
        fd = ImageDraw.Draw(frame)
        # Growing vertical left accent stripe
        vh = max(16, int((card_h - 40) * e))
        fd.rounded_rectangle((pad + 12, pad + 20, pad + 22, pad + 20 + vh), radius=5, fill=theme['accent'])
        # Sweeping underline accent bar beneath quote
        uw = max(12, int(min(card_w - 80, max_line_w) * e))
        fd.rounded_rectangle((pad + 40, qy + 2, pad + 40 + uw, qy + 8), radius=3, fill=theme['accent'])
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
    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Avenir Next,44,&H00FFFFFF,&H0000B8FF,&H0014100E,&H9614100E,-1,0,0,0,100,100,0,0,3,14,0,2,90,90,48,1

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

        if otype == 'visual_card':
            res = build_motion_visual_card(ov, theme, proj, dur, mov_path, png_path)
            entry.update(res)
            sfx = [('whoosh-short', start, 0.28)]
        elif otype == 'stat_card':
            res = build_motion_stat_card(ov, theme, dur, mov_path, png_path)
            entry.update(res)
            sfx = [('pop', start, 0.28), ('sparkle', start + 0.55, 0.20)]
        elif otype in ('checklist', 'steps_card'):
            res = build_motion_checklist(ov, theme, dur, mov_path, png_path)
            entry.update(res)
            sfx = [('pop', start, 0.28), ('click-soft', start + 0.65, 0.24)]
        elif otype == 'comparison':
            res = build_motion_comparison(ov, theme, dur, mov_path, png_path)
            entry.update(res)
            sfx = [('whoosh-short', start, 0.26), ('pop', start + res.get('split_delay', 0.65), 0.26)]
        elif otype == 'kinetic_quote':
            res = build_motion_kinetic_quote(ov, theme, dur, mov_path, png_path)
            entry.update(res)
            sfx = [('whoosh-short', start, 0.28)]
        elif otype == 'custom_motion':
            src_rel = ov.get('src') or ov.get('video') or ''
            src_abs = os.path.join(proj, src_rel) if (src_rel and not os.path.isabs(src_rel)) else src_rel
            entry['video'] = src_abs if os.path.isfile(src_abs) else None
            entry['x'] = int(ov.get('x', 0))
            entry['y'] = int(ov.get('y', 0))
            sfx_name = ov.get('sfx', 'whoosh-short')
            sfx = [(sfx_name, start, 0.26)] if sfx_name else []
        elif otype == 'intro':
            img = render_intro(ov, theme)
            img.save(png_path, 'PNG')
            sfx = [('whoosh-short', start, 0.32), ('impact-bass-1', start + 0.15, 0.25)]
        elif otype == 'chapter':
            img = render_chapter(ov, theme)
            img.save(png_path, 'PNG')
            sfx = [('whoosh-short', start, 0.30)]
        elif otype == 'callout':
            img = render_callout(ov, theme)
            img.save(png_path, 'PNG')
            sfx = [('click-soft', start, 0.30)]
        elif otype == 'subscribe':
            img = render_subscribe(ov, theme, cfg)
            img.save(png_path, 'PNG')
            sfx = [('pop', start, 0.30), ('click', start + 0.75, 0.32)]
        else:
            img = render_lower_third(ov, theme)
            img.save(png_path, 'PNG')
            sfx = [('pop', start, 0.28)]
            if ov.get('rating'):
                sfx.append(('sparkle', start + 0.35, 0.22))

        manifest['overlays'].append(entry)
        for s_name, s_time, s_vol in sfx:
            manifest['sfx_events'].append({'name': s_name, 'time': round(s_time, 3), 'volume': s_vol})
        out_asset = os.path.basename(entry['video'] or entry['png'])
        kind_tag = 'MOTION' if entry.get('video') else 'CARD  '
        print(f'[{start:6.2f}s - {end:6.2f}s] [{kind_tag}] {otype:14s} -> {out_asset}', flush=True)

    manifest_path = os.path.join(work, 'graphics_manifest.json')
    with open(manifest_path, 'w', encoding='utf-8') as fh:
        json.dump(manifest, fh, indent=2, ensure_ascii=False)


if __name__ == '__main__':
    main()
