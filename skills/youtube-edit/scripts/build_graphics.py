#!/usr/bin/env python3
"""Generate 1920x1080 RGBA YouTube graphics (Intro, Chapters, Lower-Thirds, Callouts, Subscribe CTA)
and .ass Vietnamese subtitles from <project_dir>/graphics.json and <project_dir>/segments.json.

Usage:
  PY build_graphics.py <project_dir>
"""
import json
import os
import sys
import textwrap
import unicodedata
from PIL import Image, ImageDraw, ImageFilter, ImageFont

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_FILE = os.path.join(SKILL_DIR, 'config.json')
FONTS_DIR = os.path.join(SKILL_DIR, 'assets', 'fonts')

THEMES = {
    'vibrant_vlog': {
        'accent': (255, 184, 0, 255),        # Warm Amber Gold #FFB800
        'accent_text': (18, 20, 26, 255),
        'badge_red': (239, 68, 68, 255),     # YouTube Red #EF4444
        'surface': (18, 20, 28, 232),        # Deep Charcoal Glass
        'surface_alt': (30, 34, 46, 240),
        'border': (255, 255, 255, 55),
        'text': (255, 255, 255, 255),
        'subtext': (235, 230, 220, 255),
    },
    'cinema_travel': {
        'accent': (243, 201, 105, 255),      # Champagne Gold #F3C969
        'accent_text': (15, 18, 24, 255),
        'badge_red': (220, 53, 69, 255),
        'surface': (12, 16, 22, 236),
        'surface_alt': (24, 32, 42, 240),
        'border': (243, 201, 105, 70),
        'text': (250, 247, 242, 255),
        'subtext': (216, 207, 194, 255),
    },
    'clean_studio': {
        'accent': (56, 189, 248, 255),       # Electric Cyan #38BDF8
        'accent_text': (12, 18, 30, 255),
        'badge_red': (239, 68, 68, 255),
        'surface': (15, 23, 42, 235),
        'surface_alt': (30, 41, 59, 240),
        'border': (148, 163, 184, 65),
        'text': (255, 255, 255, 255),
        'subtext': (203, 213, 225, 255),
    },
    'film_kodak': {
        'accent': (224, 122, 95, 255),       # Terracotta #E07A5F
        'accent_text': (255, 253, 249, 255),
        'badge_red': (214, 69, 65, 255),
        'surface': (24, 20, 18, 234),
        'surface_alt': (38, 32, 28, 240),
        'border': (224, 122, 95, 75),
        'text': (253, 251, 247, 255),
        'subtext': (222, 214, 202, 255),
    },
    'minimal_editorial': {
        'accent': (217, 78, 52, 255),        # Editorial Vermilion #D94E34
        'accent_text': (255, 255, 255, 255),
        'badge_red': (217, 78, 52, 255),
        'surface': (246, 243, 236, 244),     # Warm Ivory Paper Surface
        'surface_alt': (234, 229, 218, 248),
        'border': (24, 24, 27, 45),
        'text': (24, 24, 27, 255),           # Deep Ink Text
        'subtext': (82, 82, 91, 255),
    },
    'warm_food': {
        'accent': (245, 158, 11, 255),       # Saffron Gold #F59E0B
        'accent_text': (20, 16, 14, 255),
        'badge_red': (239, 68, 68, 255),
        'surface': (22, 18, 16, 235),
        'surface_alt': (36, 28, 24, 240),
        'border': (245, 158, 11, 70),
        'text': (255, 253, 249, 255),
        'subtext': (235, 225, 212, 255),
    },
}


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
        # Never use index 8 (Heavy) as it lacks stacked Vietnamese glyphs; 0=Bold, 2=Demi Bold, 5=Medium, 7=Regular
        idx = {'heavy': 0, 'bold': 0, 'demi': 2, 'medium': 5, 'regular': 7}.get(weight, 0)
        try:
            return ImageFont.truetype(avenir, size, index=idx)
        except Exception:
            pass
    for fallback in (
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


def render_intro(ov, theme):
    img = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))
    # Subtle center-bottom gradient scrim for legibility
    scrim = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))
    sd = ImageDraw.Draw(scrim)
    sd.rounded_rectangle((180, 310, 1740, 770), radius=36, fill=(10, 12, 18, 195))
    scrim = scrim.filter(ImageFilter.GaussianBlur(8))
    img = Image.alpha_composite(img, scrim)

    img = add_shadow(img, (210, 330, 1710, 750), radius=32, blur=28, alpha=140)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((210, 330, 1710, 750), radius=32, fill=theme['surface'], outline=theme['border'], width=2)

    # Top accent pill badge
    badge = strip_emoji(ov.get('badge', 'VLOG REVIEW')).upper()
    f_badge = load_font(26, 'bold')
    f_title = load_font(68, 'heavy')
    f_sub = load_font(34, 'medium')

    bb = d.textbbox((0, 0), badge, font=f_badge)
    bw = (bb[2] - bb[0]) + 56
    bx0 = 960 - bw // 2
    d.rounded_rectangle((bx0, 372, bx0 + bw, 428), radius=28, fill=theme['accent'])
    d.text((960, 400), badge, font=f_badge, fill=theme['accent_text'], anchor='mm')

    # Main Title
    title = strip_emoji(ov.get('title', '')).upper()
    if len(title) > 36:
        f_title = load_font(56, 'heavy')
    d.text((960, 525), title, font=f_title, fill=theme['text'], anchor='mm')

    # Decorative divider bar
    d.rounded_rectangle((860, 595, 1060, 603), radius=4, fill=theme['accent'])

    # Subtitle
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
    # Left accent vertical stripe
    d.rounded_rectangle((x0, y0, x0 + 14, y1), radius=7, fill=theme['accent'])

    # Number pill
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

    # Category pill
    cb = d.textbbox((0, 0), cat, font=f_cat)
    cw = (cb[2] - cb[0]) + 32
    d.rounded_rectangle((x0 + 36, y0 + 22, x0 + 36 + cw, y0 + 60), radius=10, fill=theme['surface_alt'], outline=theme['accent'], width=2)
    d.text((x0 + 36 + cw // 2, y0 + 41), cat, font=f_cat, fill=theme['accent'], anchor='mm')

    # Main place/dish title
    d.text((x0 + 36, y0 + 74), title, font=f_title, fill=theme['text'])

    # Location & Price line
    if meta_str:
        d.text((x0 + 36, y0 + 138), meta_str, font=f_meta, fill=theme['subtext'])

    # Rating badge on the right
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

    # Circular avatar badge on left
    cx, cy, r = x0 + 70, (y0 + y1) // 2, 44
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=theme['accent'])
    initials = ''.join(w[0].upper() for w in channel.split()[:2]) or 'YT'
    d.text((cx, cy), initials, font=load_font(30, 'heavy'), fill=theme['accent_text'], anchor='mm')

    # Channel name & handle
    d.text((x0 + 136, y0 + 28), channel, font=f_ch, fill=theme['text'])
    d.text((x0 + 136, y0 + 76), handle, font=f_hd, fill=theme['subtext'])

    # Red Subscribe button on right
    bx0, by0 = x1 - btn_w - 26, y0 + 28
    bx1, by1 = x1 - 26, y1 - 28
    d.rounded_rectangle((bx0, by0, bx1, by1), radius=40, fill=theme['badge_red'])
    d.text(((bx0 + bx1) // 2, (by0 + by1) // 2), btn_txt, font=f_btn, fill=(255, 255, 255, 255), anchor='mm')
    return img


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

        if otype == 'intro':
            img = render_intro(ov, theme)
            sfx = [('whoosh-short', start, 0.32), ('impact-bass-1', start + 0.15, 0.25)]
        elif otype == 'chapter':
            img = render_chapter(ov, theme)
            sfx = [('whoosh-short', start, 0.30)]
        elif otype == 'callout':
            img = render_callout(ov, theme)
            sfx = [('click-soft', start, 0.30)]
        elif otype == 'subscribe':
            img = render_subscribe(ov, theme, cfg)
            sfx = [('pop', start, 0.30), ('click', start + 0.75, 0.32)]
        else:
            img = render_lower_third(ov, theme)
            sfx = [('pop', start, 0.28)]
            if ov.get('rating'):
                sfx.append(('sparkle', start + 0.35, 0.22))

        png_path = os.path.join(gfx_dir, f'ov_{idx:02d}_{otype}.png')
        img.save(png_path, 'PNG')
        manifest['overlays'].append({
            'id': f'ov_{idx:02d}',
            'type': otype,
            'png': png_path,
            'start': start,
            'end': end,
            'duration': round(end - start, 3),
        })
        for s_name, s_time, s_vol in sfx:
            manifest['sfx_events'].append({'name': s_name, 'time': round(s_time, 3), 'volume': s_vol})
        print(f'[{start:6.2f}s - {end:6.2f}s] {otype:12s} -> {os.path.basename(png_path)}')

    manifest_path = os.path.join(work, 'graphics_manifest.json')
    with open(manifest_path, 'w', encoding='utf-8') as fh:
        json.dump(manifest, fh, indent=2, ensure_ascii=False)


if __name__ == '__main__':
    main()
