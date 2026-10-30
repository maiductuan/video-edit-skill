#!/usr/bin/env python3
"""Multi-Platform Aspect Ratio Reframer (reframe.py).
Converts any video cleanly to 16:9 (YouTube), 9:16 (Reels/TikTok/Shorts), 4:5 (IG/FB Feed), or 1:1 (Square)
using either smart focal crop (--mode crop) or optical blurred ambient backdrop (--mode backdrop).

Usage:
  python3 reframe.py <input.mp4> --ratio 9:16|4:5|1:1|16:9 [--mode crop|backdrop] [--cx 0.5] [--cy 0.5] [--title "..."] -o <output.mp4>
"""
import json
import os
import shutil
import subprocess
import sys

SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


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

RATIOS = {
    '16:9': (1920, 1080),
    '9:16': (1080, 1920),
    '4:5': (1080, 1350),
    '1:1': (1080, 1080),
}


def probe_size_dur(path):
    out = subprocess.run([
        FP, '-v', 'error', '-select_streams', 'v:0',
        '-show_entries', 'stream=width,height', '-show_entries', 'format=duration',
        '-of', 'csv=p=0', path
    ], capture_output=True, encoding='utf-8', errors='replace').stdout.strip().splitlines()
    w, h = [int(x) for x in out[0].split(',')[:2]]
    dur = float(out[-1].split(',')[0]) if len(out) > 1 else 30.0
    return w, h, dur


def main():
    if len(sys.argv) < 2:
        print('Usage: python3 reframe.py <input.mp4> --ratio 9:16 [--mode crop|backdrop] [--cx 0.5] [--cy 0.5] -o <out.mp4>')
        sys.exit(1)

    inp = os.path.abspath(os.path.expanduser(sys.argv[1]))
    args = sys.argv[2:]

    ratio = '9:16'
    if '--ratio' in args:
        i = args.index('--ratio'); ratio = args[i + 1]

    mode = 'crop'
    if '--mode' in args:
        i = args.index('--mode'); mode = args[i + 1]

    cx, cy = 0.5, 0.5
    if '--cx' in args:
        i = args.index('--cx'); cx = float(args[i + 1])
    if '--cy' in args:
        i = args.index('--cy'); cy = float(args[i + 1])

    start, dur = None, None
    if '--start' in args:
        i = args.index('--start'); start = float(args[i + 1])
    if '--duration' in args:
        i = args.index('--duration'); dur = float(args[i + 1])

    out = os.path.splitext(inp)[0] + f'_{ratio.replace(":", "x")}.mp4'
    if '-o' in args:
        i = args.index('-o'); out = os.path.abspath(os.path.expanduser(args[i + 1]))

    tw, th = RATIOS.get(ratio, (1080, 1920))
    sw, sh, src_dur = probe_size_dur(inp)

    ss_args = ['-ss', f'{start:.3f}'] if start is not None else []
    t_args = ['-t', f'{dur:.3f}'] if dur is not None else []

    if mode == 'backdrop':
        fc = (
            f'[0:v]split=2[bg][fg];'
            f'[bg]scale={tw}:{th}:force_original_aspect_ratio=increase:flags=lanczos,crop={tw}:{th},'
            f'boxblur=32:4,eq=brightness=-0.16:saturation=0.9[bg_b];'
            f'[fg]scale={tw}:{th}:force_original_aspect_ratio=decrease:flags=lanczos[fg_s];'
            f'[bg_b][fg_s]overlay=(W-w)/2:(H-h)/2,format=yuv420p[vout]'
        )
        subprocess.run([
            FF, '-loglevel', 'error', '-y', *ss_args, *t_args, '-i', inp,
            '-filter_complex', fc, '-map', '[vout]', '-map', '0:a?',
            *VCODEC, '-c:a', 'aac', '-b:a', '192k', out
        ], check=True)
    else:
        # Focal point crop
        target_aspect = tw / th
        src_aspect = sw / sh
        if src_aspect > target_aspect:
            ch = sh
            cw = int(round(sh * target_aspect / 2) * 2)
        else:
            cw = sw
            ch = int(round(sw / target_aspect / 2) * 2)
        x = min(max(int(round(cx * sw - cw / 2)), 0), sw - cw)
        y = min(max(int(round(cy * sh - ch / 2)), 0), sh - ch)
        vf = f'crop={cw}:{ch}:{x}:{y},scale={tw}:{th}:flags=lanczos,format=yuv420p'
        subprocess.run([
            FF, '-loglevel', 'error', '-y', *ss_args, *t_args, '-i', inp,
            '-vf', vf, '-map', '0:v:0', '-map', '0:a?',
            *VCODEC, '-c:a', 'aac', '-b:a', '192k', out
        ], check=True)

    print(f'Reframed ({ratio}, mode={mode}) -> {out} ({tw}x{th})')


if __name__ == '__main__':
    main()
