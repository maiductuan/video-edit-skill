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
VCODEC = ['-c:v', 'h264_videotoolbox', '-b:v', '16M'] if sys.platform == 'darwin' else ['-c:v', 'libx264', '-preset', 'fast', '-crf', '18']


def probe_size(path):
    out = subprocess.run([
        FP, '-v', 'error', '-select_streams', 'v:0',
        '-show_entries', 'stream=width,height', '-of', 'csv=p=0', path
    ], capture_output=True, encoding='utf-8', errors='replace').stdout.strip().split(',')[:2]
    return int(out[0]), int(out[1])


def make_split_overlay(seg, title_badge, out_png):
    img = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # Center divider bar between top and bottom speaker frames
    d.rectangle((0, 956, 1080, 964), fill=(255, 184, 0, 255))

    if title_badge:
        f_b = load_font(24, 'heavy')
        txt = strip_emoji(title_badge).upper()
        bb = d.textbbox((0, 0), txt, font=f_b)
        bw = (bb[2] - bb[0]) + 48
        d.rounded_rectangle((540 - bw // 2, 932, 540 + bw // 2, 988), radius=28, fill=(18, 20, 28, 245), outline=(255, 184, 0, 255), width=3)
        d.text((540, 960), txt, font=f_b, fill=(255, 184, 0, 255), anchor='mm')

    quote = strip_emoji(seg.get('quote', ''))
    speaker = strip_emoji(seg.get('speaker_name', ''))
    if quote or speaker:
        box = (64, 1240, 1016, 1440)
        sh = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle((64, 1250, 1016, 1450), radius=24, fill=(0, 0, 0, 140))
        img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(20)))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle(box, radius=24, fill=(16, 18, 26, 232), outline=(255, 255, 255, 55), width=2)
        if speaker:
            role = strip_emoji(seg.get('speaker_role', ''))
            label = f'{speaker}  •  {role}' if role else speaker
            d.text((540, 1282), label, font=load_font(24, 'bold'), fill=(255, 184, 0, 255), anchor='mm')
        if quote:
            d.text((540, 1356), quote[:54] + ('...' if len(quote) > 54 else ''), font=load_font(30, 'heavy'), fill=(255, 255, 255, 255), anchor='mm')

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
