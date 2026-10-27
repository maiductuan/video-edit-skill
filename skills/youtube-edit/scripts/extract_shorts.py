#!/usr/bin/env python3
"""Extract a 9:16 vertical YouTube Short / Reel (1080x1920) from a 16:9 YouTube video,
with a blurred 9:16 background canvas, centered foreground frame, and top Vietnamese title banner.

Usage:
  PY extract_shorts.py <input_16x9.mp4> --start 0.0 --duration 30.0 -o <output_short.mp4> [--title "Khám Phá Hội An"]
"""
import os
import subprocess
import sys
from PIL import Image, ImageDraw, ImageFont

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(SKILL_DIR, 'scripts'))
from build_graphics import load_font, strip_emoji  # noqa: E402


def make_banner(title, sub, out_png):
    img = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if title:
        f_title = load_font(56, 'heavy')
        d.rounded_rectangle((90, 250, 990, 410), radius=28, fill=(18, 20, 28, 225), outline=(255, 184, 0, 180), width=3)
        d.text((540, 312), strip_emoji(title).upper(), font=f_title, fill=(255, 184, 0, 255), anchor='mm')
        if sub:
            d.text((540, 368), strip_emoji(sub), font=load_font(30, 'demi'), fill=(255, 255, 255, 255), anchor='mm')
    img.save(out_png, 'PNG')


def main():
    if len(sys.argv) < 2:
        print('Usage: PY extract_shorts.py <input_16x9.mp4> --start 0 --duration 30 -o <out.mp4> [--title "..."]')
        sys.exit(1)

    inp = os.path.abspath(os.path.expanduser(sys.argv[1]))
    args = sys.argv[2:]

    start = 0.0
    if '--start' in args:
        i = args.index('--start'); start = float(args[i + 1]); args = args[:i] + args[i + 2:]

    dur = 30.0
    if '--duration' in args:
        i = args.index('--duration'); dur = float(args[i + 1]); args = args[:i] + args[i + 2:]

    out = os.path.join(os.path.dirname(inp), 'short_9x16.mp4')
    if '-o' in args:
        i = args.index('-o'); out = os.path.abspath(os.path.expanduser(args[i + 1])); args = args[:i] + args[i + 2:]

    title = ''
    if '--title' in args:
        i = args.index('--title'); title = args[i + 1]; args = args[:i] + args[i + 2:]

    sub = 'Tuấn Đi Review • YouTube Shorts'
    if '--subtitle' in args:
        i = args.index('--subtitle'); sub = args[i + 1]; args = args[:i] + args[i + 2:]

    banner_png = out + '.banner.png'
    make_banner(title, sub, banner_png)

    fc = (
        '[0:v]split=2[bg][fg];'
        '[bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=28:4,eq=brightness=-0.18[bg_b];'
        '[fg]scale=1080:-2[fg_s];'
        '[bg_b][fg_s]overlay=0:(H-h)/2[v_comp];'
        '[v_comp][1:v]overlay=0:0,format=yuv420p[vout]'
    )
    subprocess.run([
        'ffmpeg', '-loglevel', 'error', '-y',
        '-ss', f'{start:.3f}', '-t', f'{dur:.3f}', '-i', inp,
        '-loop', '1', '-t', f'{dur:.3f}', '-i', banner_png,
        '-filter_complex', fc,
        '-map', '[vout]', '-map', '0:a',
        '-c:v', 'h264_videotoolbox', '-b:v', '14M',
        '-c:a', 'aac', '-b:a', '192k', out
    ], check=True)
    if os.path.isfile(banner_png):
        os.remove(banner_png)
    print(f'Extracted 9:16 YouTube Short -> {out}')


if __name__ == '__main__':
    main()
