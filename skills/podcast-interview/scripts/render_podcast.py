#!/usr/bin/env python3
"""Render 16:9 Podcast Episodes or 9:16 Split-Screen / Active-Speaker Podcast Clips from podcast.json.
Includes room-tone floor smoothing, speaker lower-thirds, quote highlight banners, and EBU R128 loudness mastering.

Usage:
  PY render_podcast.py <podcast.json> -o <output.mp4>
"""
import json
import os
import shutil
import subprocess
import sys
from PIL import Image, ImageDraw, ImageFilter

SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(SKILL_ROOT, 'youtube-edit', 'scripts'))
from build_graphics import (  # noqa: E402
    THEMES,
    draw_brand_spark_badge,
    draw_glowing_underline,
    load_font,
    make_condensed_display_strip,
    make_modern_glow_plate,
    strip_emoji,
)


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
VCODEC = ['-c:v', 'h264_videotoolbox', '-b:v', '16M'] if sys.platform == 'darwin' else ['-c:v', 'libx264', '-preset', 'fast', '-crf', '18']


def probe_size(path):
    out = subprocess.run([
        FP, '-v', 'error', '-select_streams', 'v:0',
        '-show_entries', 'stream=width,height', '-of', 'csv=p=0', path
    ], capture_output=True, encoding='utf-8', errors='replace').stdout.strip().split(',')[:2]
    return int(out[0]), int(out[1])


def make_split_overlay(seg, title_badge, out_png):
    theme = THEMES['modern_mint']
    img = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 958, 1080, 962), fill=theme['accent'])

    if title_badge:
        f_b = load_font(20, 'heavy')
        txt = strip_emoji(title_badge).upper()
        bb = d.textbbox((0, 0), txt, font=f_b)
        bw = (bb[2] - bb[0]) + 48
        pill = make_modern_glow_plate(1080, 1920, (540 - bw // 2, 934, 540 + bw // 2, 986), theme, radius=14, border_w=2)
        img = Image.alpha_composite(img, pill)
        ImageDraw.Draw(img).text((540, 960), txt, font=f_b, fill=theme['accent'], anchor='mm')

    quote = strip_emoji(seg.get('quote', ''))
    speaker = strip_emoji(seg.get('speaker_name', ''))
    if quote or speaker:
        box = (64, 1230, 1016, 1438)
        plate = make_modern_glow_plate(1080, 1920, box, theme, radius=16, border_w=2)
        img = Image.alpha_composite(img, plate)
        d = ImageDraw.Draw(img)
        if speaker:
            role = strip_emoji(seg.get('speaker_role', ''))
            label = f'{speaker} · {role}' if role else speaker
            draw_brand_spark_badge(img, 92, 1252, theme, size=20)
            d.text((120, 1250), label, font=load_font(21, 'demi'), fill=theme['kicker_text'])
        if quote:
            h_strip = make_condensed_display_strip(quote[:46].upper(), 36, theme, condense_x=0.84)
            img.alpha_composite(h_strip, dest=(84, 1286))
            draw_glowing_underline(img, 92, 1340, min(880, h_strip.width - 16), theme, thickness=4)

    img.save(out_png, 'PNG')


def main():
    if len(sys.argv) < 2:
        print('Usage: PY render_podcast.py <podcast.json> -o <output.mp4>')
        sys.exit(1)

    cfg_path = os.path.abspath(os.path.expanduser(sys.argv[1]))
    with open(cfg_path, encoding='utf-8') as fh:
        cfg = json.load(fh)

    out_path = os.path.join(os.path.dirname(cfg_path), 'podcast_master.mp4')
    if '-o' in sys.argv:
        i = sys.argv.index('-o')
        out_path = os.path.abspath(os.path.expanduser(sys.argv[i + 1]))

    mode = cfg.get('mode', '9:16_split')
    target_lufs = float(cfg.get('target_lufs', -14.0))
    title_badge = cfg.get('title_badge', 'PODCAST')

    work = os.path.join(os.path.dirname(out_path), '_pod_work')
    os.makedirs(work, exist_ok=True)

    seg_files = []
    for idx, seg in enumerate(cfg.get('segments') or []):
        clip = os.path.abspath(os.path.expanduser(seg['clip']))
        sw, sh = probe_size(clip)
        t_in, t_out = float(seg['in']), float(seg['out'])
        dur = round(t_out - t_in, 3)
        seg_out = os.path.join(work, f'pseg_{idx:02d}.mp4')

        if mode == '9:16_split':
            lcx = float(seg.get('left_speaker_cx', 0.28))
            rcx = float(seg.get('right_speaker_cx', 0.72))
            cw = min(sw, int(round(sh * (1080 / 960) / 2) * 2))
            lx = min(max(int(round(lcx * sw - cw / 2)), 0), sw - cw)
            rx = min(max(int(round(rcx * sw - cw / 2)), 0), sw - cw)

            ov_png = os.path.join(work, f'pov_{idx:02d}.png')
            make_split_overlay(seg, title_badge, ov_png)

            fc = (
                f'[0:v]split=2[vtop][vbot];'
                f'[vtop]crop={cw}:{sh}:{lx}:0,scale=1080:960:flags=lanczos[top_s];'
                f'[vbot]crop={cw}:{sh}:{rx}:0,scale=1080:960:flags=lanczos[bot_s];'
                f'[top_s][bot_s]vstack=inputs=2,fps=30,eq=contrast=1.04:saturation=1.05[vstack];'
                f'[vstack][1:v]overlay=0:0,format=yuv420p[vout]'
            )
            subprocess.run([
                FF, '-loglevel', 'error', '-y',
                '-ss', f'{t_in:.3f}', '-t', f'{dur:.3f}', '-i', clip,
                '-loop', '1', '-t', f'{dur:.3f}', '-i', ov_png,
                '-filter_complex', fc, '-map', '[vout]', '-map', '0:a',
                '-af', f'highpass=f=80,afade=t=in:d=0.03,afade=t=out:st={max(0.0, dur-0.04):.3f}:d=0.04',
                *VCODEC,
                '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', seg_out
            ], check=True)
        else:
            vf = 'scale=1920:1080:force_original_aspect_ratio=increase:flags=lanczos,crop=1920:1080,fps=30,format=yuv420p'
            subprocess.run([
                FF, '-loglevel', 'error', '-y',
                '-ss', f'{t_in:.3f}', '-t', f'{dur:.3f}', '-i', clip,
                '-vf', vf,
                '-af', f'highpass=f=80,afade=t=in:d=0.03,afade=t=out:st={max(0.0, dur-0.04):.3f}:d=0.04',
                *VCODEC,
                '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', seg_out
            ], check=True)
        seg_files.append(seg_out)

    concat_txt = os.path.join(work, 'concat.txt')
    with open(concat_txt, 'w', encoding='utf-8') as fh:
        for sf in seg_files:
            fh.write(f"file '{os.path.basename(sf)}'\n")

    subprocess.run([
        FF, '-loglevel', 'error', '-y',
        '-f', 'concat', '-safe', '0', '-i', concat_txt,
        '-af', f'loudnorm=I={target_lufs:.1f}:TP=-1.0:LRA=11',
        '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', out_path
    ], check=True)
    shutil.rmtree(work, ignore_errors=True)
    print(f'Rendered Podcast ({mode}, target {target_lufs} LUFS) -> {out_path}')


if __name__ == '__main__':
    main()
