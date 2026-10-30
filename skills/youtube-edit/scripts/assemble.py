#!/usr/bin/env python3
"""Assemble 16:9 YouTube timeline (<project>/assets/base_16x9.mp4) from sources.json and edl.json.
Engineered for TVC / Documentary realism:
  - "aroll": talking-head / narration segment (optional 4K punch-in + eased gimbal camera drift)
  - "broll": real scenic/food video OR photorealistic AI plate ("image": "assets/ai_visuals/scene.png")
             processed with 4K-supersampled sinusoidal gimbal inertia (4-7% subtle dolly/pan) AND
             TVC Optical Plate Matching (highlight/chroma taming, subtle lens falloff, fine luma sensor
             micro-dither) so still plates blend seamlessly with real camera footage without looking "AI".
  - "aroll_with_broll": continuous A-roll speech audio with J/L-cut video & optical-matched image inserts.

Usage:
  PY assemble.py <project_dir> [--fps 60]
"""
import json
import os
import shutil
import subprocess
import sys

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLATFORM_FILE = os.path.join(SKILL_DIR, '.platform.json')
IMAGE_EXT = ('.png', '.jpg', '.jpeg', '.webp')


def load_platform():
    if os.path.isfile(PLATFORM_FILE):
        with open(PLATFORM_FILE, encoding='utf-8') as fh:
            return json.load(fh)
    return {}


PLAT = load_platform()
FF = PLAT.get('ffmpeg') or shutil.which('ffmpeg') or 'ffmpeg'
FP = PLAT.get('ffprobe') or shutil.which('ffprobe') or 'ffprobe'
VCODEC = ['-c:v', 'h264_videotoolbox', '-b:v', '16M'] if sys.platform == 'darwin' else ['-c:v', 'libx264', '-preset', 'fast', '-crf', '16']
VCODEC_MASTER = ['-c:v', 'h264_videotoolbox', '-b:v', '18M'] if sys.platform == 'darwin' else ['-c:v', 'libx264', '-preset', 'fast', '-crf', '16']


def get_clip_path(src_entry):
    return src_entry['path'] if isinstance(src_entry, dict) else src_entry


def resolve_media_path(item, sources, proj):
    """Resolve either an 'image' path (relative to project or absolute) or a 'clip' key from sources.json."""
    if item.get('image'):
        p = os.path.expanduser(str(item['image']))
        if not os.path.isabs(p):
            p = os.path.join(proj, p)
        return os.path.abspath(p)
    clip_key = item.get('clip', '')
    if clip_key in sources:
        return get_clip_path(sources[clip_key])
    p = os.path.expanduser(str(clip_key))
    if not os.path.isabs(p):
        p = os.path.join(proj, p)
    return os.path.abspath(p)


def is_image_file(path):
    return path.lower().endswith(IMAGE_EXT)


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


def video_motion_filter(zoom=1.0, cx=0.5, cy=0.5, sw=1920, sh=1080, fps=60, motion='none', dur=4.0, amt=None):
    """Build 16:9 scale+crop chain with subtle TVC gimbal-eased dolly/pan motion (4-6% restrained drift)."""
    c = crop_filter(zoom, cx, cy, sw, sh)
    motion = (motion or 'none').lower()
    d = max(0.2, float(dur))
    if motion in ('none', '', 'static'):
        return (
            f'{c}scale=1920:1080:force_original_aspect_ratio=increase:flags=lanczos,'
            f'crop=1920:1080,fps={fps},format=yuv420p'
        )

    # Restrained TVC dolly amplitude: 4.5% default so camera movement feels physical, never robotic
    m_amt = float(amt) if amt is not None else 0.045
    m_amt = max(0.02, min(0.14, m_amt))
    # Sinusoidal ease-in-out camera inertia: 0.5 - 0.5*cos(PI * t / d)
    prog = f'(0.5-0.5*cos(PI*clip(t/{d:.3f},0,1)))'

    if motion in ('pan_right', 'pan_left'):
        pw = round(1920 * (1.0 + m_amt) / 2) * 2
        ph = round(1080 * (1.0 + m_amt) / 2) * 2
        dx = max(2, pw - 1920)
        dy = max(0, (ph - 1080) // 2)
        x_expr = f'{dx}*{prog}' if motion == 'pan_right' else f'{dx}*(1-{prog})'
        return (
            f'{c}scale={pw}:{ph}:force_original_aspect_ratio=increase:flags=lanczos,'
            f'crop={pw}:{ph},fps={fps},'
            f"crop=1920:1080:x='{x_expr}':y='{dy}',format=yuv420p"
        )

    z_expr = f'(1.0+{m_amt:.4f}*{prog})' if motion != 'pull_out' else f'(1.0+{m_amt:.4f}*(1-{prog}))'
    return (
        f'{c}scale=1920:1080:force_original_aspect_ratio=increase:flags=lanczos,'
        f'crop=1920:1080,fps={fps},'
        f"scale=w='trunc(1920*{z_expr}/2)*2':h='trunc(1080*{z_expr}/2)*2':eval=frame:flags=bicubic,"
        f'crop=1920:1080,format=yuv420p'
    )


def image_ken_burns_filter(dur=4.0, fps=60, motion='push_in', amt=None, optical_match=True):
    """4K-supersampled TVC Dolly/Slider filter for still/AI plates with Optical Camera Sensor Matching:
       - Sinusoidal gimbal inertia (zero mechanical linear stiffness)
       - Restrained 6.0% physical slider travel
       - Highlight/chroma de-plasticizing + subtle lens falloff + fine temporal luma sensor micro-dither
         so AI plates blend seamlessly into real mirrorless/phone camera footage.
    """
    motion = (motion or 'push_in').lower()
    if motion in ('none', 'static'):
        motion = 'push_in'
    m_amt = float(amt) if amt is not None else 0.062
    m_amt = max(0.025, min(0.16, m_amt))
    n_frames = max(2, int(round(float(dur) * fps)))
    # Smooth sinusoidal slider curve instead of robotic linear on/N
    p = f'(0.5-0.5*cos(PI*on/{n_frames}))'

    if motion == 'pull_out':
        z = f'{1.0 + m_amt:.4f}-{m_amt:.4f}*{p}'
        x = 'iw/2-(iw/zoom/2)'
        y = 'ih/2-(ih/zoom/2)'
    elif motion == 'pan_right':
        z = f'{1.0 + m_amt:.4f}'
        x = f'(iw-iw/zoom)*{p}'
        y = 'ih/2-(ih/zoom/2)'
    elif motion == 'pan_left':
        z = f'{1.0 + m_amt:.4f}'
        x = f'(iw-iw/zoom)*(1-{p})'
        y = 'ih/2-(ih/zoom/2)'
    elif motion == 'drift_up':
        z = f'{1.0 + m_amt:.4f}'
        x = 'iw/2-(iw/zoom/2)'
        y = f'(ih-ih/zoom)*(1-{p})'
    elif motion == 'drift_down':
        z = f'{1.0 + m_amt:.4f}'
        x = 'iw/2-(iw/zoom/2)'
        y = f'(ih-ih/zoom)*{p}'
    else:  # push_in (default subtle TVC dolly-in)
        z = f'1.0+{m_amt:.4f}*{p}'
        x = 'iw/2-(iw/zoom/2)'
        y = 'ih/2-(ih/zoom/2)'

    optical_chain = ''
    if optical_match:
        # Tame AI hyper-saturation & harsh contrast, add natural lens corner falloff & subtle luma sensor dither
        optical_chain = (
            'eq=contrast=0.985:saturation=0.93:brightness=-0.005,'
            'vignette=PI/9,'
            'noise=c0s=3:c0f=t,'
        )

    return (
        'scale=3840:2160:force_original_aspect_ratio=increase:flags=lanczos,crop=3840:2160,'
        f"zoompan=z='{z}':x='{x}':y='{y}':d={n_frames}:s=1920x1080:fps={fps},"
        f'{optical_chain}format=yuv420p'
    )


def render_image_segment(img_path, dur, fps, motion, amt, out_mp4, optical_match=True):
    """Render a still/AI image into a TVC-matched 1920x1080 video plate with slider motion + silent stereo AAC."""
    vf = image_ken_burns_filter(dur=dur, fps=fps, motion=motion, amt=amt, optical_match=optical_match)
    subprocess.run([
        FF, '-loglevel', 'error', '-y',
        '-i', img_path,
        '-f', 'lavfi', '-t', f'{dur:.3f}', '-i', 'anullsrc=channel_layout=stereo:sample_rate=48000',
        '-vf', vf,
        '-map', '0:v:0', '-map', '1:a:0',
        '-t', f'{dur:.3f}',
        *VCODEC,
        '-c:a', 'aac', '-b:a', '192k', '-ar', '48000',
        out_mp4
    ], check=True)


def duration_of(path):
    out = subprocess.run([
        FP, '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path
    ], capture_output=True, encoding='utf-8', errors='replace').stdout.strip()
    return float(out) if out else 0.0


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if len(sys.argv) < 2:
        print('Usage: PY assemble.py <project_dir> [--fps 60]')
        sys.exit(1)

    proj = os.path.abspath(os.path.expanduser(sys.argv[1]))
    args = sys.argv[2:]
    fps = 60
    if '--fps' in args:
        i = args.index('--fps')
        fps = int(args[i + 1])

    sources = {}
    src_path = os.path.join(proj, 'sources.json')
    if os.path.isfile(src_path):
        with open(src_path, encoding='utf-8') as fh:
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
        media_path = resolve_media_path(seg, sources, proj)
        is_img = is_image_file(media_path)

        t_in = float(seg.get('in', 0.0))
        t_out = float(seg.get('out', t_in + float(seg.get('duration', 4.0))))
        dur = round(max(0.4, t_out - t_in), 3)
        out_seg = os.path.join(work, f'seg_{k:03d}.mp4')
        motion = seg.get('motion') or ('push_in' if is_img else 'none')
        m_amt = seg.get('motion_amt')
        opt_match = seg.get('optical_match', True)

        if is_img:
            render_image_segment(media_path, dur, fps, motion, m_amt, out_seg, optical_match=opt_match)
        else:
            sw, sh = size(media_path)
            vf_main = video_motion_filter(
                seg.get('zoom', 1.0), seg.get('cx', 0.5), seg.get('cy', 0.5),
                sw, sh, fps, motion=motion, dur=dur, amt=m_amt
            )
            vol = float(seg.get('ambient_vol', 0.30)) if seg_type == 'broll' else float(seg.get('volume', 1.0))
            af_main = f'volume={vol:.2f},afade=t=in:d=0.02,afade=t=out:st={max(0.0, dur - 0.03):.3f}:d=0.03'

            broll_inserts = seg.get('broll_inserts') or []
            if seg_type == 'aroll_with_broll' and broll_inserts:
                base_tmp = os.path.join(work, f'seg_{k:03d}_base.mp4')
                subprocess.run([
                    FF, '-loglevel', 'error', '-y',
                    '-ss', f'{t_in:.3f}', '-t', f'{dur:.3f}', '-i', media_path,
                    '-vf', vf_main, '-af', af_main,
                    *VCODEC,
                    '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', base_tmp
                ], check=True)

                inputs = ['-i', base_tmp]
                fc_parts = []
                last_v = '[0:v]'
                for bi, ins in enumerate(broll_inserts):
                    b_path = resolve_media_path(ins, sources, proj)
                    b_off = float(ins.get('start_offset', 0.0))
                    b_dur = float(ins.get('duration', 3.0))
                    b_motion = ins.get('motion') or ('push_in' if is_image_file(b_path) else 'none')
                    b_amt = ins.get('motion_amt')
                    inp_idx = bi + 1
                    v_tag = f'[bv{bi}]'
                    out_tag = f'[vov{bi}]'

                    if is_image_file(b_path):
                        kb_tmp = os.path.join(work, f'seg_{k:03d}_kb_{bi:02d}.mp4')
                        render_image_segment(
                            b_path, b_dur, fps, b_motion, b_amt, kb_tmp,
                            optical_match=ins.get('optical_match', True)
                        )
                        inputs += ['-i', kb_tmp]
                        fc_parts.append(f'[{inp_idx}:v]fps={fps},setpts=PTS-STARTPTS+{b_off:.3f}/TB{v_tag}')
                    else:
                        b_in = float(ins.get('src_in', 0.0))
                        bsw, bsh = size(b_path)
                        b_vf = video_motion_filter(
                            ins.get('zoom', 1.0), ins.get('cx', 0.5), ins.get('cy', 0.5),
                            bsw, bsh, fps, motion=b_motion, dur=b_dur, amt=b_amt
                        )
                        inputs += ['-ss', f'{b_in:.3f}', '-t', f'{b_dur:.3f}', '-i', b_path]
                        fc_parts.append(f'[{inp_idx}:v]{b_vf},setpts=PTS-STARTPTS+{b_off:.3f}/TB{v_tag}')

                    fc_parts.append(
                        f"{last_v}{v_tag}overlay=0:0:enable='between(t,{b_off:.3f},{b_off + b_dur:.3f})':eof_action=pass{out_tag}"
                    )
                    last_v = out_tag

                subprocess.run([
                    FF, '-loglevel', 'error', '-y', *inputs,
                    '-filter_complex', ';'.join(fc_parts),
                    '-map', last_v, '-map', '0:a',
                    *VCODEC,
                    '-c:a', 'copy', out_seg
                ], check=True)
            else:
                subprocess.run([
                    FF, '-loglevel', 'error', '-y',
                    '-ss', f'{t_in:.3f}', '-t', f'{dur:.3f}', '-i', media_path,
                    '-vf', vf_main, '-af', af_main,
                    *VCODEC,
                    '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', out_seg
                ], check=True)

        actual_dur = duration_of(out_seg) or dur
        parts.append(out_seg)
        src_label = seg.get('image') or seg.get('clip', 'media')
        segments_meta.append({
            **seg,
            'id': seg_id,
            'type': seg_type,
            'motion': motion,
            'start': round(cur_t, 3),
            'end': round(cur_t + actual_dur, 3),
            'duration': round(actual_dur, 3),
        })
        print(
            f'[{cur_t:6.2f}s -> {cur_t + actual_dur:6.2f}s] ({actual_dur:5.2f}s) '
            f'{seg_id:16s} [{seg_type}:{motion}] {src_label}',
            flush=True
        )
        cur_t += actual_dur

    concat_txt = os.path.join(work, 'concat.txt')
    with open(concat_txt, 'w', encoding='utf-8') as fh:
        for p in parts:
            fh.write(f"file '{os.path.basename(p)}'\n")

    base_out = os.path.join(assets, 'base_16x9.mp4')
    subprocess.run([
        FF, '-loglevel', 'error', '-y',
        '-f', 'concat', '-safe', '0', '-i', concat_txt,
        *VCODEC_MASTER, '-r', str(fps),
        '-c:a', 'aac', '-b:a', '192k', base_out
    ], check=True)

    with open(os.path.join(proj, 'segments.json'), 'w', encoding='utf-8') as fh:
        json.dump(segments_meta, fh, indent=2, ensure_ascii=False)

    print(f'Assembled {base_out} ({cur_t:.2f}s total @ {fps}fps)')


if __name__ == '__main__':
    main()
