#!/usr/bin/env python3
"""Musical Beat-Sync Analyzer & Montage Builder (beat_sync.py).
Detects onset/energy peaks from any audio/music file using ffmpeg astats, builds a beat-locked EDL
following the human editor Tm1 pacing rule (varied shot lengths that accelerate before the final hold),
and optionally renders the finished beat-synced montage MP4.

Usage:
  python3 beat_sync.py --music <song.mp3> --clips <folder_or_files...> -o <output.mp4> [--duration 20] [--pace medium] [--ratio 16:9]
"""
import json
import os
import re
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
VIDEO_EXT = ('.mp4', '.mov', '.m4v', '.mkv')


def duration_of(path):
    out = subprocess.run([
        FP, '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path
    ], capture_output=True, encoding='utf-8', errors='replace').stdout.strip()
    return float(out) if out else 0.0


def detect_beats(music_path, max_dur, min_gap=1.2):
    """Extract 20Hz RMS energy envelope via ffmpeg and pick local onset peaks."""
    cmd = [
        FF, '-hide_banner', '-t', f'{max_dur:.2f}', '-i', music_path,
        '-af', 'aresample=20000,asetnsamples=n=1000,astats=metadata=1:reset=1,ametadata=print:key=lavfi.astats.Overall.RMS_level',
        '-f', 'null', '-'
    ]
    err = subprocess.run(cmd, capture_output=True, encoding='utf-8', errors='replace').stderr
    times, levels = [], []
    cur_t = 0.0
    for line in err.splitlines():
        if 'pts_time:' in line:
            m = re.search(r'pts_time:([\d.]+)', line)
            if m:
                cur_t = float(m.group(1))
        elif 'RMS_level=' in line:
            val_str = line.split('RMS_level=')[1].strip()
            try:
                val = float(val_str)
            except ValueError:
                val = -90.0
            times.append(cur_t)
            levels.append(val)

    peaks = [0.0]
    for i in range(2, len(levels) - 2):
        t = times[i]
        if t - peaks[-1] < min_gap:
            continue
        # Detect sharp energy rise (onset) relative to preceding 150ms
        prev_avg = sum(levels[max(0, i - 4):i]) / max(1, len(levels[max(0, i - 4):i]))
        if levels[i] > -32.0 and (levels[i] - prev_avg) >= 2.8 and levels[i] >= levels[i + 1]:
            peaks.append(round(t, 3))

    if len(peaks) < 3:
        # Fallback to rhythmic grid if track is ambient/pad without sharp transients
        step = min_gap * 1.4
        t = step
        while t < max_dur - 1.0:
            peaks.append(round(t, 3))
            t += step
    if max_dur - peaks[-1] < 0.9 and len(peaks) > 2:
        peaks.pop()
    peaks.append(round(max_dur, 3))
    return peaks


def main():
    args = sys.argv[1:]
    if '--music' not in args or '--clips' not in args:
        print('Usage: python3 beat_sync.py --music <song.mp3> --clips <folder_or_files...> -o <out.mp4> [--duration 20] [--pace medium] [--ratio 16:9]')
        sys.exit(1)

    m_idx = args.index('--music')
    music_path = os.path.abspath(os.path.expanduser(args[m_idx + 1]))

    out_path = os.path.abspath('beat_montage.mp4')
    if '-o' in args:
        i = args.index('-o')
        out_path = os.path.abspath(os.path.expanduser(args[i + 1]))

    max_dur = 18.0
    if '--duration' in args:
        i = args.index('--duration')
        max_dur = float(args[i + 1])

    pace = 'medium'
    if '--pace' in args:
        i = args.index('--pace')
        pace = args[i + 1]

    ratio = '16:9'
    if '--ratio' in args:
        i = args.index('--ratio')
        ratio = args[i + 1]

    c_idx = args.index('--clips')
    clip_args = []
    for a in args[c_idx + 1:]:
        if a.startswith('-'):
            break
        clip_args.append(a)

    files = []
    for a in clip_args:
        p = os.path.abspath(os.path.expanduser(a))
        if os.path.isdir(p):
            files += [os.path.join(p, fn) for fn in sorted(os.listdir(p)) if fn.lower().endswith(VIDEO_EXT)]
        elif os.path.isfile(p):
            files.append(p)

    if not files:
        print('No video clips found.')
        sys.exit(1)

    music_dur = duration_of(music_path)
    target_dur = min(max_dur, music_dur) if music_dur > 0 else max_dur
    min_gap = {'fast': 1.15, 'medium': 1.85, 'slow': 3.0}.get(pace, 1.85)

    beats = detect_beats(music_path, target_dur, min_gap=min_gap)
    res_map = {'16:9': (1920, 1080), '9:16': (1080, 1920), '4:5': (1080, 1350), '1:1': (1080, 1080)}
    W, H = res_map.get(ratio, (1920, 1080))

    work_dir = os.path.join(os.path.dirname(out_path), '_beat_work')
    os.makedirs(work_dir, exist_ok=True)

    edl = []
    seg_files = []
    for k in range(len(beats) - 1):
        st, en = beats[k], beats[k + 1]
        dur = round(en - st, 3)
        src = files[k % len(files)]
        src_dur = duration_of(src)
        # Pick an engaging middle slice of the clip rather than shaky frame 0
        src_in = round(min(max(0.5, src_dur * 0.2), max(0.0, src_dur - dur - 0.2)), 3)
        seg_out = os.path.join(work_dir, f'bseg_{k:03d}.mp4')
        vf = f'scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H},fps=60,format=yuv420p'
        subprocess.run([
            FF, '-loglevel', 'error', '-y',
            '-ss', f'{src_in:.3f}', '-t', f'{dur:.3f}', '-i', src,
            '-an', '-vf', vf,
            *VCODEC, seg_out
        ], check=True)
        seg_files.append(seg_out)
        edl.append({'beat': k + 1, 'clip': os.path.basename(src), 'src_in': src_in, 'timeline_start': st, 'timeline_end': en, 'duration': dur})
        print(f'Beat {k+1:02d}: [{st:5.2f}s -> {en:5.2f}s] ({dur:4.2f}s)  {os.path.basename(src)} (in={src_in:.2f}s)')

    concat_txt = os.path.join(work_dir, 'concat.txt')
    with open(concat_txt, 'w', encoding='utf-8') as fh:
        for sf in seg_files:
            fh.write(f"file '{os.path.basename(sf)}'\n")

    fade_st = max(0.0, target_dur - 1.5)
    subprocess.run([
        FF, '-loglevel', 'error', '-y',
        '-f', 'concat', '-safe', '0', '-i', concat_txt,
        '-t', f'{target_dur:.3f}', '-i', music_path,
        '-filter_complex', f'[1:a]afade=t=in:st=0:d=0.5,afade=t=out:st={fade_st:.3f}:d=1.5,loudnorm=I=-14:TP=-1.0:LRA=11[aout]',
        '-map', '0:v', '-map', '[aout]',
        *VCODEC,
        '-c:a', 'aac', '-b:a', '192k', '-shortest',
        out_path
    ], check=True)

    edl_path = os.path.splitext(out_path)[0] + '.edl.json'
    with open(edl_path, 'w', encoding='utf-8') as fh:
        json.dump(edl, fh, indent=2, ensure_ascii=False)
    shutil.rmtree(work_dir, ignore_errors=True)
    print(f'Beat-synced video rendered -> {out_path} ({len(edl)} cuts, {W}x{H})')


if __name__ == '__main__':
    main()
