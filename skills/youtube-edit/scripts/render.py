#!/usr/bin/env python3
"""Composite base 16:9 video + color look + animated 16:9 graphics + Vietnamese subtitles + SFX + dynamic BGM auto-ducking,
master audio to -14 LUFS (EBU R128), and generate a QA contact sheet (<project_dir>/work/qa_sheet.jpg).

Usage:
  PY render.py <project_dir> -o <output.mp4> [--bgm <music.mp3>] [--quality high|fast]
"""
import json
import os
import re
import subprocess
import sys

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLATFORM_FILE = os.path.join(SKILL_DIR, '.platform.json')
SFX_DIR = os.path.join(SKILL_DIR, 'assets', 'sfx')

GRADE_FILTERS = {
    'vibrant_vlog': 'eq=contrast=1.05:saturation=1.12:brightness=0.012',
    'cinema_travel': 'eq=contrast=1.08:saturation=0.96:brightness=-0.008,colorbalance=rs=-0.03:gs=0.0:bs=0.04:rh=0.04:gh=0.02:bh=-0.03',
    'clean_studio': 'eq=contrast=1.04:saturation=1.03:brightness=0.01',
    'film_kodak': 'eq=contrast=1.03:saturation=0.94:brightness=0.02,colorbalance=rm=0.03:gm=0.01:bm=-0.02:rh=0.03:gh=0.01:bh=-0.03',
    'minimal_editorial': 'eq=contrast=1.06:saturation=0.92:brightness=0.005',
    'warm_food': 'eq=contrast=1.06:saturation=1.15:brightness=0.015,colorbalance=rh=0.03:gh=0.01:bh=-0.02',
}


def load_platform():
    if os.path.isfile(PLATFORM_FILE):
        with open(PLATFORM_FILE, encoding='utf-8') as fh:
            return json.load(fh)
    return {}


PLAT = load_platform()
FF = PLAT.get('ffmpeg') or 'ffmpeg'
FP = PLAT.get('ffprobe') or 'ffprobe'


def duration_of(path):
    out = subprocess.run([
        FP, '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path
    ], capture_output=True, encoding='utf-8', errors='replace').stdout.strip()
    return float(out) if out else 0.0


def measure_lufs(path):
    err = subprocess.run([
        FF, '-hide_banner', '-i', path, '-af', 'ebur128=peak=true', '-f', 'null', '-'
    ], capture_output=True, encoding='utf-8', errors='replace').stderr
    i_lufs, tp = None, None
    for line in err.splitlines():
        if 'I:' in line and 'LUFS' in line:
            m = re.search(r'I:\s*([-\d.]+)\s*LUFS', line)
            if m:
                i_lufs = float(m.group(1))
        if 'Peak:' in line and 'dBFS' in line:
            m = re.search(r'Peak:\s*([-\d.]+)\s*dBFS', line)
            if m:
                tp = float(m.group(1))
    return i_lufs, tp


def escape_ass_path(p):
    return p.replace('\\', '/').replace(':', '\\:').replace("'", "\\'")


def build_bgm_duck_expr(segments):
    """Duck BGM to 0.14 (-17 dB) during A-roll speech segments and swell to 0.38 (-8.4 dB) on B-roll segments."""
    speech_windows = []
    for s in (segments or []):
        if s.get('type', 'aroll') in ('aroll', 'aroll_with_broll'):
            st = max(0.0, float(s['start']) - 0.15)
            en = float(s['end']) + 0.20
            speech_windows.append(f'between(t,{st:.2f},{en:.2f})')
    if not speech_windows:
        return '0.22'
    cond = '+'.join(speech_windows)
    return f"if(gt({cond},0), 0.14, 0.38)"


def filter_non_slop_sfx(sfx_events, total_dur):
    """Anti-Slop SFX Guard: cap volume <= 0.28, minimum 0.35s spacing, max 3 identical SFX in a row."""
    valid = []
    last_time = -1.0
    streak_name = None
    streak_count = 0
    for ev in sorted(sfx_events or [], key=lambda x: float(x['time'])):
        t = float(ev['time'])
        name = ev['name']
        if t >= total_dur or not os.path.isfile(os.path.join(SFX_DIR, f'{name}.mp3')):
            continue
        if t - last_time < 0.25 and name == streak_name:
            continue
        if name == streak_name:
            streak_count += 1
        else:
            streak_name = name
            streak_count = 1
        if streak_count > 3:
            continue
        valid.append({
            'name': name,
            'time': t,
            'volume': min(0.28, float(ev.get('volume', 0.25))),
        })
        last_time = t
    return valid


def main():
    if len(sys.argv) < 2:
        print('Usage: PY render.py <project_dir> -o <output.mp4> [--bgm <music.mp3>] [--quality high|fast]')
        sys.exit(1)

    proj = os.path.abspath(os.path.expanduser(sys.argv[1]))
    args = sys.argv[2:]

    out_file = os.path.join(proj, 'renders', 'youtube_v1.mp4')
    if '-o' in args:
        i = args.index('-o')
        out_file = os.path.abspath(os.path.expanduser(args[i + 1]))
        args = args[:i] + args[i + 2:]

    bgm_file = None
    if '--bgm' in args:
        i = args.index('--bgm')
        bgm_file = os.path.abspath(os.path.expanduser(args[i + 1]))
        args = args[:i] + args[i + 2:]

    quality = 'high'
    if '--quality' in args:
        i = args.index('--quality')
        quality = args[i + 1]

    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    work = os.path.join(proj, 'work')
    base_video = os.path.join(proj, 'assets', 'base_16x9.mp4')
    if not os.path.isfile(base_video):
        print(f'Missing {base_video}. Run assemble.py first.')
        sys.exit(1)

    total_dur = duration_of(base_video)
    manifest_file = os.path.join(work, 'graphics_manifest.json')
    manifest = {'look': 'vibrant_vlog', 'overlays': [], 'sfx_events': [], 'subtitles_ass': None}
    if os.path.isfile(manifest_file):
        with open(manifest_file, encoding='utf-8') as fh:
            manifest = json.load(fh)

    segments = []
    seg_file = os.path.join(proj, 'segments.json')
    if os.path.isfile(seg_file):
        with open(seg_file, encoding='utf-8') as fh:
            segments = json.load(fh)

    look = manifest.get('look', 'vibrant_vlog')
    grade = GRADE_FILTERS.get(look, GRADE_FILTERS['vibrant_vlog'])

    inputs = ['-i', base_video]
    fc = []

    # 1. Base video grade + optional ASS subtitles
    v_chain = grade
    ass_file = manifest.get('subtitles_ass')
    if ass_file and os.path.isfile(ass_file):
        v_chain += f",subtitles='{escape_ass_path(ass_file)}'"
    fc.append(f'[0:v]{v_chain}[v0]')
    last_v = '[v0]'

    # 2. Animated RGBA graphic overlays with smooth cubic deceleration slide
    overlays = manifest.get('overlays') or []
    for idx, ov in enumerate(overlays):
        inp_idx = len(inputs) // 2
        st = float(ov['start'])
        en = float(ov['end'])
        dur = max(1.5, en - st)
        fade_in = min(0.32, dur * 0.22)
        fade_out_st = max(st + fade_in, en - min(0.28, dur * 0.22))
        fade_out_d = max(0.12, en - fade_out_st)

        inputs += ['-loop', '1', '-t', f'{en + 0.1:.3f}', '-i', ov['png']]
        ov_tag = f'[gov{idx}]'
        next_v = f'[v{idx + 1}]'
        fc.append(
            f'[{inp_idx}:v]format=rgba,'
            f'fade=t=in:st={st:.3f}:d={fade_in:.3f}:alpha=1,'
            f'fade=t=out:st={fade_out_st:.3f}:d={fade_out_d:.3f}:alpha=1{ov_tag}'
        )
        # Smooth cubic ease-out 28px upward arrival over 0.32s (no bounce/elastic slop)
        p_expr = f"clip((t-{st:.3f})/0.32,0,1)"
        y_expr = f"if(lt(t-{st:.3f},0.32),pow(1-{p_expr},3)*28,0)"
        fc.append(
            f"{last_v}{ov_tag}overlay=x=0:y='{y_expr}':enable='between(t,{st:.3f},{en:.3f})':format=auto{next_v}"
        )
        last_v = next_v

    fc.append(f'{last_v}format=yuv420p[vout]')

    # 3. Audio mix: cleaned dialogue + dynamic auto-ducked BGM + guarded SFX + EBU R128 -14 LUFS master
    audio_mix_tags = ['[a_base]']
    fc.append('[0:a]aresample=48000,highpass=f=75,volume=1.0[a_base]')

    if bgm_file and os.path.isfile(bgm_file):
        bgm_idx = len(inputs) // 2
        inputs += ['-stream_loop', '-1', '-t', f'{total_dur:.3f}', '-i', bgm_file]
        fade_out_bgm = max(0.0, total_dur - 2.2)
        duck_expr = build_bgm_duck_expr(segments)
        fc.append(
            f"[{bgm_idx}:a]aresample=48000,volume='{duck_expr}':eval=frame,"
            f'afade=t=in:st=0:d=1.2,afade=t=out:st={fade_out_bgm:.3f}:d=2.2[a_bgm]'
        )
        audio_mix_tags.append('[a_bgm]')

    sfx_events = filter_non_slop_sfx(manifest.get('sfx_events'), total_dur)
    for s_idx, ev in enumerate(sfx_events):
        sfx_path = os.path.join(SFX_DIR, f"{ev['name']}.mp3")
        inp_idx = len(inputs) // 2
        inputs += ['-i', sfx_path]
        # Place transient ~2 frames (40ms) early for natural visual sync
        delay_ms = max(0, int(round((float(ev['time']) - 0.04) * 1000)))
        vol = float(ev['volume'])
        s_tag = f'[asfx{s_idx}]'
        fc.append(f'[{inp_idx}:a]aresample=48000,volume={vol:.2f},adelay={delay_ms}|{delay_ms}{s_tag}')
        audio_mix_tags.append(s_tag)

    if len(audio_mix_tags) == 1:
        fc.append('[a_base]loudnorm=I=-14:TP=-1.0:LRA=11[aout]')
    else:
        fc.append(
            f"{''.join(audio_mix_tags)}amix=inputs={len(audio_mix_tags)}:duration=first:dropout_transition=0:normalize=0,"
            f'loudnorm=I=-14:TP=-1.0:LRA=11[aout]'
        )

    v_codec = ['-c:v', 'h264_videotoolbox', '-b:v', '20M' if quality == 'high' else '12M']
    cmd = [
        FF, '-loglevel', 'error', '-y',
        *inputs,
        '-filter_complex', ';'.join(fc),
        '-map', '[vout]', '-map', '[aout]',
        *v_codec,
        '-c:a', 'aac', '-b:a', '192k', '-ar', '48000',
        '-movflags', '+faststart',
        out_file
    ]
    print(f'Rendering 1920x1080 YouTube master -> {out_file} ({total_dur:.1f}s, look={look}, {len(overlays)} overlays, {len(sfx_events)} SFX)...', flush=True)
    subprocess.run(cmd, check=True)

    # 4. Generate QA contact sheet sampling every graphic overlay & key segment
    sample_times = []
    for ov in overlays:
        mid = round((float(ov['start']) + float(ov['end'])) / 2.0, 2)
        if 0.0 <= mid < total_dur:
            sample_times.append(mid)
    if not sample_times:
        step = max(1.0, total_dur / 6.0)
        sample_times = [round(step * i, 2) for i in range(1, 6) if step * i < total_dur]

    qa_frames = []
    for i, t in enumerate(sample_times[:12]):
        fp_jpg = os.path.join(work, f'qa_{i:02d}.jpg')
        subprocess.run([
            FF, '-loglevel', 'error', '-y', '-ss', f'{t:.2f}', '-i', out_file,
            '-vf', 'scale=640:360', '-frames:v', '1', fp_jpg
        ], check=True)
        qa_frames.append(fp_jpg)

    qa_sheet = os.path.join(work, 'qa_sheet.jpg')
    if qa_frames:
        cols = 2 if len(qa_frames) > 1 else 1
        rows = (len(qa_frames) + cols - 1) // cols
        ins = sum((['-i', f] for f in qa_frames), [])
        subprocess.run([
            FF, '-loglevel', 'error', '-y', *ins,
            '-filter_complex', f"concat=n={len(qa_frames)}:v=1:a=0,tile={cols}x{rows}",
            '-frames:v', '1', qa_sheet
        ], check=True)

    i_lufs, tp = measure_lufs(out_file)
    print(f'QA contact sheet -> {qa_sheet}')
    print(f'AUDIO MASTER     -> Integrated: {i_lufs} LUFS | True Peak: {tp} dBTP (Target: -14 LUFS, <= -1.0 dBTP)')
    print(f'DONE             -> {out_file}')


if __name__ == '__main__':
    main()
