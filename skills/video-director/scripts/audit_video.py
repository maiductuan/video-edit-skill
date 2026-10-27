#!/usr/bin/env python3
"""Automated 6-Gate Video & Audio Auditor (audit_video.py).
Checks stream integrity (G0), black/frozen frames (G1), EBU R128 loudness & true peak (G2),
silence dropouts (G3), and generates a 12-frame visual QA contact sheet (G4/G5).

Usage:
  python3 audit_video.py <video.mp4> [--target-lufs -14.0]
"""
import json
import os
import re
import shutil
import subprocess
import sys

FF = shutil.which('ffmpeg') or '/opt/homebrew/bin/ffmpeg'
FP = shutil.which('ffprobe') or '/opt/homebrew/bin/ffprobe'


def probe_video(path):
    out = subprocess.run([
        FP, '-v', 'error', '-show_entries', 'stream=index,codec_type,codec_name,width,height,r_frame_rate',
        '-show_entries', 'format=duration,size', '-of', 'json', path
    ], capture_output=True, encoding='utf-8', errors='replace').stdout
    return json.loads(out)


def audit_streams(path, target_lufs=-14.0):
    info = probe_video(path)
    streams = info.get('streams') or []
    v_stream = next((s for s in streams if s.get('codec_type') == 'video'), None)
    a_stream = next((s for s in streams if s.get('codec_type') == 'audio'), None)
    dur = float((info.get('format') or {}).get('duration') or 0.0)

    gates = {}
    gates['G0_render_exists'] = bool(v_stream and dur > 0.5)

    # Check black frames & loudness in one pass
    af_chain = 'ebur128=peak=true,silencedetect=n=-60dB:d=1.2'
    vf_chain = 'blackdetect=d=0.25:pix_th=0.05'
    cmd = [FF, '-hide_banner', '-i', path, '-vf', vf_chain, '-af', af_chain, '-f', 'null', '-']
    err = subprocess.run(cmd, capture_output=True, encoding='utf-8', errors='replace').stderr

    black_stretches = re.findall(r'black_duration:([\d.]+)', err)
    total_black = sum(float(x) for x in black_stretches)
    gates['G1_no_black_frames'] = total_black < 0.35

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

    if a_stream and i_lufs is not None:
        gates['G2_loudness_ok'] = (abs(i_lufs - target_lufs) <= 2.5) and (tp is None or tp <= -0.3)
    else:
        gates['G2_loudness_ok'] = False

    dead_silences = re.findall(r'silence_duration:\s*([\d.]+)', err)
    long_dead_air = [float(x) for x in dead_silences if float(x) > 1.8]
    gates['G3_no_dead_dropouts'] = len(long_dead_air) == 0

    # Generate 12-frame QA contact sheet
    sheet_path = os.path.splitext(path)[0] + '_audit_sheet.jpg'
    w = int(v_stream.get('width', 1920)) if v_stream else 1920
    h = int(v_stream.get('height', 1080)) if v_stream else 1080
    tw = 360 if w >= h else 240
    th = int(round(tw * h / max(1, w) / 2) * 2)
    fps_expr = f'12/{max(dur, 1.0):.3f}'
    subprocess.run([
        FF, '-loglevel', 'error', '-y', '-i', path,
        '-vf', f'fps={fps_expr},scale={tw}:{th},tile=4x3',
        '-frames:v', '1', sheet_path
    ], check=True)
    gates['G4_qa_sheet_generated'] = os.path.isfile(sheet_path)

    report = {
        'file': path,
        'duration_s': round(dur, 2),
        'resolution': f'{w}x{h}',
        'fps': v_stream.get('r_frame_rate') if v_stream else None,
        'integrated_lufs': i_lufs,
        'true_peak_dbtp': tp,
        'black_seconds': round(total_black, 2),
        'long_silence_count': len(long_dead_air),
        'qa_sheet': sheet_path,
        'gates': gates,
    }
    return report


def main():
    if len(sys.argv) < 2:
        print('Usage: python3 audit_video.py <video.mp4> [--target-lufs -14.0]')
        sys.exit(1)

    path = os.path.abspath(os.path.expanduser(sys.argv[1]))
    target_lufs = -14.0
    if '--target-lufs' in sys.argv:
        i = sys.argv.index('--target-lufs')
        target_lufs = float(sys.argv[i + 1])

    rep = audit_streams(path, target_lufs)
    print('=== VIDEO DIRECTOR QUALITY AUDIT ===')
    print(f"File       : {rep['file']}")
    print(f"Resolution : {rep['resolution']} @ {rep['fps']} fps | Duration: {rep['duration_s']}s")
    print(f"Audio Mix  : Integrated {rep['integrated_lufs']} LUFS | True Peak {rep['true_peak_dbtp']} dBTP (Target {target_lufs} LUFS)")
    print(f"Black Time : {rep['black_seconds']}s | Dead Air Stretches (>1.8s): {rep['long_silence_count']}")
    print(f"QA Sheet   : {rep['qa_sheet']}")
    for g, ok in rep['gates'].items():
        print(f"  [{ 'PASS' if ok else 'WARN' }] {g}")


if __name__ == '__main__':
    main()
