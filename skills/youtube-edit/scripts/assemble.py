#!/usr/bin/env python3
"""Assemble 16:9 YouTube timeline (<project>/assets/base_16x9.mp4) from sources.json and edl.json.
Supports:
  - "aroll": talking-head / narration segment (optional zoom, cx, cy for 4K punch-in)
  - "broll": scenic/food segment with softened ambient audio ("ambient_vol", default 0.30)
  - "aroll_with_broll": continuous A-roll speech audio while cutting the video picture to one or more
                        broll_inserts: [{"clip": "c2", "src_in": 1.0, "start_offset": 3.0, "duration": 4.0}]

Usage:
  PY assemble.py <project_dir> [--fps 60]
"""
import json
import os
import subprocess
import sys

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLATFORM_FILE = os.path.join(SKILL_DIR, '.platform.json')


def load_platform():
    if os.path.isfile(PLATFORM_FILE):
        with open(PLATFORM_FILE, encoding='utf-8') as fh:
            return json.load(fh)
    return {}


PLAT = load_platform()
FF = PLAT.get('ffmpeg') or 'ffmpeg'
FP = PLAT.get('ffprobe') or 'ffprobe'


def get_clip_path(src_entry):
    return src_entry['path'] if isinstance(src_entry, dict) else src_entry


def size(path):
    out = subprocess.run([
        FP, '-v', 'error', '-select_streams', 'v:0',
        '-show_entries', 'stream=width,height', '-of', 'csv=p=0', path
    ], capture_output=True, encoding='utf-8', errors='replace').stdout.strip().split(',')[:2]
    return int(out[0]), int(out[1])


def crop_filter(zoom, cx, cy, sw, sh):
    if not zoom or zoom <= 1.0:
        return ''
    w = max(2, round(sw / zoom / 2) * 2)
    h = max(2, round(sh / zoom / 2) * 2)
    x = min(max(round(cx * sw - w / 2), 0), sw - w)
    y = min(max(round(cy * sh - h / 2), 0), sh - h)
    return f'crop={w}:{h}:{x}:{y},'


def scale_16x9(zoom=1.0, cx=0.5, cy=0.5, sw=1920, sh=1080, fps=60):
    c = crop_filter(zoom, cx, cy, sw, sh)
    return (
        f'{c}scale=1920:1080:force_original_aspect_ratio=increase:flags=lanczos,'
        f'crop=1920:1080,fps={fps},format=yuv420p'
    )


def duration_of(path):
    out = subprocess.run([
        FP, '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path
    ], capture_output=True, encoding='utf-8', errors='replace').stdout.strip()
    return float(out) if out else 0.0


def main():
    if len(sys.argv) < 2:
        print('Usage: PY assemble.py <project_dir> [--fps 60]')
        sys.exit(1)

    proj = os.path.abspath(os.path.expanduser(sys.argv[1]))
    args = sys.argv[2:]
    fps = 60
    if '--fps' in args:
        i = args.index('--fps')
        fps = int(args[i + 1])

    with open(os.path.join(proj, 'sources.json'), encoding='utf-8') as fh:
        sources = json.load(fh)
    with open(os.path.join(proj, 'edl.json'), encoding='utf-8') as fh:
        edl = json.load(fh)

    work = os.path.join(proj, 'work')
    assets = os.path.join(proj, 'assets')
    os.makedirs(work, exist_ok=True)
    os.makedirs(assets, exist_ok=True)

    parts = []
    segments_meta = []
    cur_t = 0.0

    for k, seg in enumerate(edl):
        seg_id = seg.get('id', f's{k+1}')
        seg_type = seg.get('type', 'aroll')
        clip_path = get_clip_path(sources[seg['clip']])
        sw, sh = size(clip_path)
        t_in = float(seg['in'])
        t_out = float(seg['out'])
        dur = round(t_out - t_in, 3)
        out_seg = os.path.join(work, f'seg_{k:03d}.mp4')

        vf_main = scale_16x9(seg.get('zoom', 1.0), seg.get('cx', 0.5), seg.get('cy', 0.5), sw, sh, fps)
        vol = float(seg.get('ambient_vol', 0.30)) if seg_type == 'broll' else float(seg.get('volume', 1.0))
        af_main = f'volume={vol:.2f},afade=t=in:d=0.02,afade=t=out:st={max(0.0, dur - 0.03):.3f}:d=0.03'

        broll_inserts = seg.get('broll_inserts') or []
        if seg_type == 'aroll_with_broll' and broll_inserts:
            # First extract base A-roll video+audio segment
            base_tmp = os.path.join(work, f'seg_{k:03d}_base.mp4')
            subprocess.run([
                FF, '-loglevel', 'error', '-y',
                '-ss', f'{t_in:.3f}', '-t', f'{dur:.3f}', '-i', clip_path,
                '-vf', vf_main, '-af', af_main,
                '-c:v', 'h264_videotoolbox', '-b:v', '16M',
                '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', base_tmp
            ], check=True)

            # Overlay each B-roll video insert onto base_tmp while keeping base_tmp's audio
            inputs = ['-i', base_tmp]
            fc_parts = []
            last_v = '[0:v]'
            for bi, ins in enumerate(broll_inserts):
                b_path = get_clip_path(sources[ins['clip']])
                b_in = float(ins.get('src_in', 0.0))
                b_off = float(ins.get('start_offset', 0.0))
                b_dur = float(ins.get('duration', 3.0))
                inputs += ['-ss', f'{b_in:.3f}', '-t', f'{b_dur:.3f}', '-i', b_path]
                inp_idx = bi + 1
                v_tag = f'[bv{bi}]'
                out_tag = f'[vov{bi}]'
                fc_parts.append(
                    f'[{inp_idx}:v]scale=1920:1080:force_original_aspect_ratio=increase:flags=lanczos,'
                    f'crop=1920:1080,fps={fps},setpts=PTS-STARTPTS+{b_off:.3f}/TB{v_tag}'
                )
                fc_parts.append(
                    f"{last_v}{v_tag}overlay=0:0:enable='between(t,{b_off:.3f},{b_off + b_dur:.3f})'{out_tag}"
                )
                last_v = out_tag

            subprocess.run([
                FF, '-loglevel', 'error', '-y', *inputs,
                '-filter_complex', ';'.join(fc_parts),
                '-map', last_v, '-map', '0:a',
                '-c:v', 'h264_videotoolbox', '-b:v', '16M',
                '-c:a', 'copy', out_seg
            ], check=True)
        else:
            subprocess.run([
                FF, '-loglevel', 'error', '-y',
                '-ss', f'{t_in:.3f}', '-t', f'{dur:.3f}', '-i', clip_path,
                '-vf', vf_main, '-af', af_main,
                '-c:v', 'h264_videotoolbox', '-b:v', '16M',
                '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', out_seg
            ], check=True)

        actual_dur = duration_of(out_seg) or dur
        parts.append(out_seg)
        segments_meta.append({
            **seg,
            'id': seg_id,
            'type': seg_type,
            'start': round(cur_t, 3),
            'end': round(cur_t + actual_dur, 3),
            'duration': round(actual_dur, 3),
        })
        print(f'[{cur_t:6.2f}s -> {cur_t + actual_dur:6.2f}s] ({actual_dur:5.2f}s) {seg_id:16s} [{seg_type}] {seg["clip"]} ({t_in:.2f}-{t_out:.2f})', flush=True)
        cur_t += actual_dur

    concat_txt = os.path.join(work, 'concat.txt')
    with open(concat_txt, 'w', encoding='utf-8') as fh:
        for p in parts:
            fh.write(f"file '{os.path.basename(p)}'\n")

    base_out = os.path.join(assets, 'base_16x9.mp4')
    subprocess.run([
        FF, '-loglevel', 'error', '-y',
        '-f', 'concat', '-safe', '0', '-i', concat_txt,
        '-c:v', 'h264_videotoolbox', '-b:v', '18M', '-r', str(fps),
        '-c:a', 'aac', '-b:a', '192k', base_out
    ], check=True)

    with open(os.path.join(proj, 'segments.json'), 'w', encoding='utf-8') as fh:
        json.dump(segments_meta, fh, indent=2, ensure_ascii=False)

    print(f'Assembled {base_out} ({cur_t:.2f}s total @ {fps}fps)')


if __name__ == '__main__':
    main()
