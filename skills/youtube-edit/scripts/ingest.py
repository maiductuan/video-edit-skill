#!/usr/bin/env python3
"""Ingest raw 16:9 clips (and optional B-roll images) for a /youtube-edit project.
Scans clips, classifies each as A-ROLL (talking-head / narration), B-ROLL (scenery / food / ambient),
or IMAGE-BROLL (still photos / AI-generated visuals), creates 16:9 contact sheets (work/sheets.jpg),
and transcribes Vietnamese or English speech with faster-whisper.

Usage:
  PY ingest.py <project_dir> <clip_files_or_folder...> [--lang vi] [--newest N] [--no-transcribe]
"""
import json
import os
import shutil
import subprocess
import sys

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLATFORM_FILE = os.path.join(SKILL_DIR, '.platform.json')
VIDEO_EXT = ('.mp4', '.mov', '.m4v', '.mkv')
IMAGE_EXT = ('.png', '.jpg', '.jpeg', '.webp')
MEDIA_EXT = VIDEO_EXT + IMAGE_EXT


def load_platform():
    if os.path.isfile(PLATFORM_FILE):
        with open(PLATFORM_FILE, encoding='utf-8') as fh:
            return json.load(fh)
    return {}


PLAT = load_platform()
FF = PLAT.get('ffmpeg') or shutil.which('ffmpeg') or 'ffmpeg'
FP = PLAT.get('ffprobe') or shutil.which('ffprobe') or 'ffprobe'


def probe(path):
    is_img = path.lower().endswith(IMAGE_EXT)
    cmd = [
        FP, '-v', 'error', '-select_streams', 'v:0',
        '-show_entries', 'stream=width,height,r_frame_rate',
        '-show_entries', 'format=duration',
        '-of', 'json', path
    ]
    out = subprocess.run(cmd, capture_output=True, encoding='utf-8', errors='replace').stdout
    j = json.loads(out or '{}')
    s = (j.get('streams') or [{}])[0]
    w = int(s.get('width') or 1920)
    h = int(s.get('height') or 1080)
    if is_img:
        return w, h, 'image', 0.0
    dur = float((j.get('format') or {}).get('duration') or s.get('duration') or 0.0)
    return w, h, s.get('r_frame_rate', '30/1'), dur


def speech_analysis(path, dur):
    if dur <= 0.0 or path.lower().endswith(IMAGE_EXT):
        return 0.0, ''
    cmd = [FF, '-hide_banner', '-i', path, '-af', 'silencedetect=n=-36dB:d=0.40', '-f', 'null', '-']
    err = subprocess.run(cmd, capture_output=True, encoding='utf-8', errors='replace').stderr
    marks = []
    silence_total = 0.0
    last_s = None
    for line in err.splitlines():
        if 'silence_start:' in line:
            try:
                t = float(line.split('silence_start:')[1].strip().split()[0])
                marks.append(('S', t))
                last_s = t
            except ValueError:
                pass
        elif 'silence_end:' in line:
            try:
                t = float(line.split('silence_end:')[1].strip().split()[0])
                marks.append(('E', t))
                if last_s is not None:
                    silence_total += max(0.0, t - last_s)
                    last_s = None
            except ValueError:
                pass
    if last_s is not None and dur > last_s:
        silence_total += dur - last_s
    speech_ratio = max(0.0, min(1.0, (dur - silence_total) / dur)) if dur > 0 else 0.0
    map_str = ' '.join(f'{k}{v:.2f}' for k, v in marks)
    return speech_ratio, map_str


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if len(sys.argv) < 3:
        print('Usage: PY ingest.py <project_dir> <clips_or_folder> [--lang vi] [--newest N] [--no-transcribe]')
        sys.exit(1)

    proj = os.path.abspath(os.path.expanduser(sys.argv[1]))
    args = sys.argv[2:]

    lang = 'vi'
    if '--lang' in args:
        i = args.index('--lang')
        lang = args[i + 1]
        args = args[:i] + args[i + 2:]

    newest = None
    if '--newest' in args:
        i = args.index('--newest')
        newest = int(args[i + 1])
        args = args[:i] + args[i + 2:]

    no_transcribe = False
    if '--no-transcribe' in args:
        args.remove('--no-transcribe')
        no_transcribe = True

    files = []
    for a in args:
        p = os.path.abspath(os.path.expanduser(a))
        if os.path.isdir(p):
            # Prefer video files when scanning a directory unless explicitly passed image files
            vids = [os.path.join(p, fn) for fn in os.listdir(p) if fn.lower().endswith(VIDEO_EXT)]
            imgs = [os.path.join(p, fn) for fn in os.listdir(p) if fn.lower().endswith(IMAGE_EXT)]
            files.extend(vids if vids else imgs)
        elif os.path.isfile(p) and p.lower().endswith(MEDIA_EXT):
            files.append(p)

    files = sorted(set(files), key=os.path.getmtime)
    if newest:
        files = files[-newest:]

    if not files:
        print('No media files found.')
        sys.exit(1)

    work = os.path.join(proj, 'work')
    os.makedirs(work, exist_ok=True)
    os.makedirs(os.path.join(proj, 'assets', 'ai_visuals'), exist_ok=True)

    sources = {}
    sheets = []
    summary_lines = []

    for idx, f in enumerate(files):
        cid = f'c{idx + 1}'
        is_img = f.lower().endswith(IMAGE_EXT)
        w, h, fr, dur = probe(f)
        if is_img:
            speech_ratio, smap = 0.0, ''
            role = 'IMAGE-BROLL'
        else:
            speech_ratio, smap = speech_analysis(f, dur)
            role = 'A-ROLL' if speech_ratio >= 0.25 else 'B-ROLL'
        sources[cid] = {
            'path': f,
            'name': os.path.basename(f),
            'kind': 'image' if is_img else 'video',
            'width': w,
            'height': h,
            'fps': fr,
            'duration': round(dur, 3),
            'speech_ratio': round(speech_ratio, 2),
            'role': role,
        }
        print(f'{cid:4s} [{role:11s}] {w}x{h} {fr:6s} {dur:6.1f}s (speech {int(speech_ratio*100):2d}%)  {os.path.basename(f)}', flush=True)

        sh = os.path.join(work, f'sheet_{cid}.jpg')
        if is_img:
            subprocess.run([
                FF, '-loglevel', 'error', '-y', '-loop', '1', '-t', '1', '-i', f,
                '-vf', 'fps=8,scale=320:180:force_original_aspect_ratio=decrease,pad=320:180:(ow-iw)/2:(oh-ih)/2,tile=8x1',
                '-frames:v', '1', sh
            ], check=True)
        else:
            fps_expr = f'8/{max(dur, 0.5):.3f}'
            subprocess.run([
                FF, '-loglevel', 'error', '-y', '-i', f,
                '-vf', f'fps={fps_expr},scale=320:180:force_original_aspect_ratio=decrease,pad=320:180:(ow-iw)/2:(oh-ih)/2,tile=8x1',
                '-frames:v', '1', sh
            ], check=True)
        sheets.append(sh)

    with open(os.path.join(proj, 'sources.json'), 'w', encoding='utf-8') as fh:
        json.dump(sources, fh, indent=2, ensure_ascii=False)

    if len(sheets) == 1:
        shutil.copyfile(sheets[0], os.path.join(work, 'sheets.jpg'))
    else:
        ins = sum((['-i', s] for s in sheets), [])
        subprocess.run([
            FF, '-loglevel', 'error', '-y', *ins,
            '-filter_complex', f'vstack=inputs={len(sheets)}',
            os.path.join(work, 'sheets.jpg')
        ], check=True)

    if no_transcribe:
        print('Skipped transcription (--no-transcribe).')
        return

    from faster_whisper import WhisperModel
    model_name = 'small.en' if lang == 'en' else 'base'
    print(f'Transcribing with faster-whisper ({model_name}, lang={lang})...', flush=True)
    model = WhisperModel(model_name, device='cpu', compute_type='int8')

    for cid, meta in sources.items():
        f = meta['path']
        summary_lines.append(f"===== {cid} [{meta['role']}] {meta['name']} ({meta['duration']:.1f}s)")
        if meta.get('kind') == 'image' or meta['speech_ratio'] < 0.05:
            summary_lines.append('  (Visual / B-Roll only — no speech detected)')
            with open(os.path.join(proj, f'words_{cid}.json'), 'w', encoding='utf-8') as fh:
                json.dump([], fh)
            continue

        wav = os.path.join(work, f'{cid}.wav')
        subprocess.run([FF, '-loglevel', 'error', '-y', '-i', f, '-vn', '-ac', '1', '-ar', '16000', wav], check=True)
        segs, _ = model.transcribe(wav, language=None if lang == 'auto' else lang, word_timestamps=True, vad_filter=True)
        words = []
        for s in segs:
            summary_lines.append(f'  [{s.start:6.2f} - {s.end:6.2f}] {s.text.strip()}')
            for w in (s.words or []):
                words.append({'text': w.word.strip(), 'start': round(w.start, 3), 'end': round(w.end, 3)})
        with open(os.path.join(proj, f'words_{cid}.json'), 'w', encoding='utf-8') as fh:
            json.dump(words, fh, indent=2, ensure_ascii=False)

    transcript_path = os.path.join(proj, 'transcript.txt')
    with open(transcript_path, 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(summary_lines) + '\n')
    print('\n'.join(summary_lines))


if __name__ == '__main__':
    main()
