#!/usr/bin/env python3
"""Render a multi-ratio (16:9, 9:16, 4:5, 1:1) Product / App / Brand Commercial Promo from promo.json.
Implements ScreenStudio-style zoom-to-detail, high-taste typography overlays (Be Vietnam Pro),
subtle sound design, and a clean 0.8-1.4s brand end card.

Usage:
  PY render_promo.py <promo.json> -o <output.mp4>
"""
import json
import os
import shutil
import subprocess
import sys
from PIL import Image, ImageDraw, ImageFilter

SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(SKILL_ROOT, 'youtube-edit', 'scripts'))
from build_graphics import load_font, strip_emoji  # noqa: E402


def find_bin(name):
    p = shutil.which(name)
    if p:
        return p
    for sk in ('video-edit', 'youtube-edit'):
        pf = os.path.join(SKILL_ROOT, sk, '.platform.json')
        if os.path.isfile(pf):
            try:
                with open(pf, encoding='utf-8') as fh:
                    val = json.load(fh).get(name)
                    if val and os.path.isfile(val):
                        return val
            except Exception:
                pass
    return f'/opt/homebrew/bin/{name}' if sys.platform == 'darwin' else name


FF = find_bin('ffmpeg')
FP = find_bin('ffprobe')
VCODEC = ['-c:v', 'h264_videotoolbox', '-b:v', '18M'] if sys.platform == 'darwin' else ['-c:v', 'libx264', '-preset', 'fast', '-crf', '17']
SFX_DIR = os.path.join(SKILL_ROOT, 'youtube-edit', 'assets', 'sfx')

RATIOS = {
    '16:9': (1920, 1080),
    '9:16': (1080, 1920),
    '4:5': (1080, 1350),
    '1:1': (1080, 1080),
}


def hex_to_rgba(h, alpha=255):
    h = h.lstrip('#')
    if len(h) == 6:
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), alpha)
    return (255, 184, 0, alpha)


def probe_size(path):
    out = subprocess.run([
        FP, '-v', 'error', '-select_streams', 'v:0',
        '-show_entries', 'stream=width,height', '-of', 'csv=p=0', path
    ], capture_output=True, encoding='utf-8', errors='replace').stdout.strip().split(',')[:2]
    return int(out[0]), int(out[1])


def make_beat_overlay(W, H, beat, accent_rgba, out_png):
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    headline = strip_emoji(beat.get('headline', ''))
    subline = strip_emoji(beat.get('subline', ''))
    kicker = strip_emoji(beat.get('kicker', '')).upper()
    if not (headline or subline or kicker):
        img.save(out_png, 'PNG')
        return False

    f_kick = load_font(22, 'bold')
    f_head = load_font(46 if W >= 1400 else 40, 'heavy')
    f_sub = load_font(28 if W >= 1400 else 25, 'medium')

    tmp = ImageDraw.Draw(img)
    hb = tmp.textbbox((0, 0), headline, font=f_head) if headline else (0, 0, 0, 0)
    sb = tmp.textbbox((0, 0), subline, font=f_sub) if subline else (0, 0, 0, 0)
    card_w = min(W - 120, max(520, max(hb[2] - hb[0], sb[2] - sb[0]) + 96))
    card_h = 128 + (42 if kicker else 0) + (44 if subline else 0)

    x0 = (W - card_w) // 2
    y0 = H - card_h - (110 if H <= 1350 else 280)
    x1, y1 = x0 + card_w, y0 + card_h

    shadow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle((x0, y0 + 10, x1, y1 + 10), radius=26, fill=(0, 0, 0, 135))
    img = Image.alpha_composite(img, shadow.filter(ImageFilter.GaussianBlur(22)))

    d = ImageDraw.Draw(img)
    d.rounded_rectangle((x0, y0, x1, y1), radius=26, fill=(14, 17, 24, 232), outline=(255, 255, 255, 55), width=2)
    d.rounded_rectangle((x0 + card_w // 2 - 48, y0, x0 + card_w // 2 + 48, y0 + 6), radius=3, fill=accent_rgba)

    cy = y0 + 30
    if kicker:
        d.text((W // 2, cy + 12), kicker, font=f_kick, fill=accent_rgba, anchor='mm')
        cy += 42
    if headline:
        d.text((W // 2, cy + 24), headline, font=f_head, fill=(255, 255, 255, 255), anchor='mm')
        cy += 56
    if subline:
        d.text((W // 2, cy + 16), subline, font=f_sub, fill=(215, 220, 230, 255), anchor='mm')

    img.save(out_png, 'PNG')
    return True


def make_end_card(W, H, end_cfg, brand_cfg, accent_rgba, out_mp4, fps=60):
    dur = min(1.4, max(0.8, float(end_cfg.get('duration', 1.2))))
    img = Image.new('RGBA', (W, H), (12, 14, 20, 255))
    d = ImageDraw.Draw(img)
    title = strip_emoji(end_cfg.get('title') or brand_cfg.get('name') or 'BRAND').upper()
    cta = strip_emoji(end_cfg.get('cta') or brand_cfg.get('tagline') or '')

    f_title = load_font(64 if W >= 1400 else 52, 'heavy')
    f_cta = load_font(30 if W >= 1400 else 26, 'demi')

    d.text((W // 2, H // 2 - 24), title, font=f_title, fill=(255, 255, 255, 255), anchor='mm')
    d.rounded_rectangle((W // 2 - 70, H // 2 + 26, W // 2 + 70, H // 2 + 32), radius=3, fill=accent_rgba)
    if cta:
        d.text((W // 2, H // 2 + 72), cta, font=f_cta, fill=accent_rgba, anchor='mm')

    png = out_mp4 + '.png'
    img.convert('RGB').save(png, 'PNG')
    subprocess.run([
        FF, '-loglevel', 'error', '-y',
        '-loop', '1', '-t', f'{dur:.3f}', '-i', png,
        '-f', 'lavfi', '-t', f'{dur:.3f}', '-i', 'anullsrc=channel_layout=stereo:sample_rate=48000',
        '-vf', f'fps={fps},format=yuv420p',
        *VCODEC,
        '-c:a', 'aac', '-b:a', '192k', '-shortest', out_mp4
    ], check=True)
    os.remove(png)
    return dur


def main():
    if len(sys.argv) < 2:
        print('Usage: PY render_promo.py <promo.json> -o <output.mp4>')
        sys.exit(1)

    cfg_path = os.path.abspath(os.path.expanduser(sys.argv[1]))
    with open(cfg_path, encoding='utf-8') as fh:
        cfg = json.load(fh)

    out_path = os.path.join(os.path.dirname(cfg_path), 'promo_master.mp4')
    if '-o' in sys.argv:
        i = sys.argv.index('-o')
        out_path = os.path.abspath(os.path.expanduser(sys.argv[i + 1]))

    ratio = cfg.get('ratio', '16:9')
    W, H = RATIOS.get(ratio, (1920, 1080))
    brand = cfg.get('brand') or {}
    accent = hex_to_rgba(brand.get('accent', '#FFB800'))

    work = os.path.join(os.path.dirname(out_path), '_promo_work')
    os.makedirs(work, exist_ok=True)

    seg_files = []
    total_dur = 0.0
    for idx, b in enumerate(cfg.get('beats') or []):
        clip = os.path.abspath(os.path.expanduser(b['clip']))
        sw, sh = probe_size(clip)
        t_in, t_out = float(b['in']), float(b['out'])
        dur = round(t_out - t_in, 3)
        zoom = float(b.get('zoom', 1.0))
        cx, cy = float(b.get('cx', 0.5)), float(b.get('cy', 0.5))

        crop_str = ''
        if zoom > 1.0:
            cw, ch = max(2, round(sw / zoom / 2) * 2), max(2, round(sh / zoom / 2) * 2)
            x = min(max(round(cx * sw - cw / 2), 0), sw - cw)
            y = min(max(round(cy * sh - ch / 2), 0), sh - ch)
            crop_str = f'crop={cw}:{ch}:{x}:{y},'

        ov_png = os.path.join(work, f'ov_{idx:02d}.png')
        has_ov = make_beat_overlay(W, H, b, accent, ov_png)
        seg_out = os.path.join(work, f'seg_{idx:02d}.mp4')

        base_vf = (
            f'{crop_str}scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,'
            f'crop={W}:{H},fps=60,eq=contrast=1.05:saturation=1.08'
        )
        if has_ov:
            fade_out_st = max(0.25, dur - 0.25)
            fc = (
                f'[0:v]{base_vf}[bv];'
                f'[1:v]format=rgba,fade=t=in:st=0.08:d=0.24:alpha=1,fade=t=out:st={fade_out_st:.3f}:d=0.22:alpha=1[ov];'
                f"[bv][ov]overlay=0:'if(lt(t,0.28),pow(1-t/0.28,3)*22,0)',format=yuv420p[vout]"
            )
            subprocess.run([
                FF, '-loglevel', 'error', '-y',
                '-ss', f'{t_in:.3f}', '-t', f'{dur:.3f}', '-i', clip,
                '-loop', '1', '-t', f'{dur:.3f}', '-i', ov_png,
                '-filter_complex', fc, '-map', '[vout]', '-map', '0:a?',
                *VCODEC,
                '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', seg_out
            ], check=True)
        else:
            subprocess.run([
                FF, '-loglevel', 'error', '-y',
                '-ss', f'{t_in:.3f}', '-t', f'{dur:.3f}', '-i', clip,
                '-vf', f'{base_vf},format=yuv420p',
                *VCODEC,
                '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', seg_out
            ], check=True)

        seg_files.append(seg_out)
        total_dur += dur

    if cfg.get('end_card'):
        end_mp4 = os.path.join(work, 'seg_end.mp4')
        total_dur += make_end_card(W, H, cfg['end_card'], brand, accent, end_mp4)
        seg_files.append(end_mp4)

    concat_txt = os.path.join(work, 'concat.txt')
    with open(concat_txt, 'w', encoding='utf-8') as fh:
        for sf in seg_files:
            fh.write(f"file '{os.path.basename(sf)}'\n")

    subprocess.run([
        FF, '-loglevel', 'error', '-y',
        '-f', 'concat', '-safe', '0', '-i', concat_txt,
        '-af', 'loudnorm=I=-14:TP=-1.0:LRA=11',
        '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', out_path
    ], check=True)
    shutil.rmtree(work, ignore_errors=True)
    print(f'Rendered Commercial Promo ({ratio}, {W}x{H}, {total_dur:.2f}s) -> {out_path}')


if __name__ == '__main__':
    main()
