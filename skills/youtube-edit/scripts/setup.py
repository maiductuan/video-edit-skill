#!/usr/bin/env python3
"""First-run environment setup for /youtube-edit.
Checks ffmpeg/ffprobe, sets up or links the Python .venv (faster-whisper + Pillow),
copies/fetches the 6 sound effects into assets/sfx, verifies Vietnamese font support,
and writes .platform.json + default config.json.
"""
import datetime
import json
import os
import platform
import shutil
import subprocess
import sys
import urllib.request

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLATFORM_FILE = os.path.join(SKILL_DIR, '.platform.json')
CONFIG_FILE = os.path.join(SKILL_DIR, 'config.json')
SFX_NAMES = ['whoosh-short', 'pop', 'sparkle', 'click', 'click-soft', 'impact-bass-1']
SFX_URL = 'https://raw.githubusercontent.com/heygen-com/hyperframes/main/skills/media-use/audio/assets/sfx'
FONT_URL = 'https://raw.githubusercontent.com/google/fonts/main/ofl/bevietnampro'
FONT_FILES = [
    'BeVietnamPro-ExtraBold.ttf',
    'BeVietnamPro-Bold.ttf',
    'BeVietnamPro-SemiBold.ttf',
    'BeVietnamPro-Medium.ttf',
]

VI_FONT_CANDIDATES = [
    os.path.join(SKILL_DIR, 'assets', 'fonts', 'BeVietnamPro-Bold.ttf'),
    '/System/Library/Fonts/Avenir Next.ttc',
    '/System/Library/Fonts/Helvetica.ttc',
    '/System/Library/Fonts/Supplemental/Arial Bold.ttf',
    '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
    'C:/Windows/Fonts/arialbd.ttf',
]


def say(msg):
    print(msg, flush=True)


def find_venv_py(venv_dir):
    for rel in (('Scripts', 'python.exe'), ('bin', 'python'), ('bin', 'python3')):
        cand = os.path.join(venv_dir, *rel)
        if os.path.isfile(cand):
            return cand
    return None


def load_sibling_platform():
    sib = os.path.join(os.path.dirname(SKILL_DIR), 'video-edit', '.platform.json')
    if os.path.isfile(sib):
        try:
            with open(sib, encoding='utf-8') as fh:
                return json.load(fh)
        except Exception:
            pass
    return {}


def find_tool(name):
    p = shutil.which(name)
    if p:
        return os.path.abspath(p)
    sib = load_sibling_platform()
    if sib.get(name) and os.path.isfile(sib[name]):
        return os.path.abspath(sib[name])
    for d in ('/opt/homebrew/bin', '/usr/local/bin', '/usr/bin'):
        cand = os.path.join(d, name)
        if os.path.isfile(cand):
            return cand
    return None


def ensure_venv():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    venv_dir = os.path.join(SKILL_DIR, '.venv')
    venv_py = find_venv_py(venv_dir)
    if venv_py:
        say(f'STATUS python venv OK ({venv_py})')
        return True, venv_py

    # Check if sibling skill video-edit already has a ready .venv we can link or share
    sibling_venv = os.path.join(os.path.dirname(SKILL_DIR), 'video-edit', '.venv')
    sibling_py = find_venv_py(sibling_venv)
    if sibling_py:
        try:
            if os.path.islink(venv_dir) or os.path.exists(venv_dir):
                shutil.rmtree(venv_dir, ignore_errors=True)
            os.symlink(sibling_venv, venv_dir, target_is_directory=True)
            linked_py = find_venv_py(venv_dir) or sibling_py
            say(f'STATUS python venv OK (linked to {sibling_venv})')
            return True, linked_py
        except OSError:
            say(f'STATUS python venv OK (shared from {sibling_venv})')
            return True, sibling_py

    say(f'STATUS python venv: creating {venv_dir} (faster-whisper + Pillow)...')
    subprocess.run([sys.executable, '-m', 'venv', venv_dir], check=True)
    venv_py = find_venv_py(venv_dir)
    subprocess.run([venv_py, '-m', 'pip', 'install', '-q', '--upgrade', 'pip'], check=True)
    subprocess.run([venv_py, '-m', 'pip', 'install', '-q', 'faster-whisper==1.2.1', 'av>=11,<19', 'pillow'], check=True)
    say('STATUS python venv OK')
    return True, venv_py


def ensure_sfx():
    sfx_dir = os.path.join(SKILL_DIR, 'assets', 'sfx')
    os.makedirs(sfx_dir, exist_ok=True)
    sibling_sfx = os.path.join(os.path.dirname(SKILL_DIR), 'video-edit', 'assets', 'template', 'assets', 'sfx')

    for name in SFX_NAMES:
        dest = os.path.join(sfx_dir, f'{name}.mp3')
        if os.path.isfile(dest) and os.path.getsize(dest) > 0:
            continue
        src = os.path.join(sibling_sfx, f'{name}.mp3')
        if os.path.isfile(src) and os.path.getsize(src) > 0:
            shutil.copyfile(src, dest)
            continue
        url = f'{SFX_URL}/{name}.mp3'
        try:
            with urllib.request.urlopen(url, timeout=20) as r, open(dest, 'wb') as f:
                shutil.copyfileobj(r, f)
        except Exception:
            pass

    missing = [n for n in SFX_NAMES if not os.path.isfile(os.path.join(sfx_dir, f'{n}.mp3'))]
    if not missing:
        say('STATUS sound effects OK')
        return True
    say(f"STATUS sound effects MISSING: {' '.join(missing)} (optional)")
    return False


def find_vi_font():
    fonts_dir = os.path.join(SKILL_DIR, 'assets', 'fonts')
    os.makedirs(fonts_dir, exist_ok=True)
    for fn in FONT_FILES:
        dest = os.path.join(fonts_dir, fn)
        if not (os.path.isfile(dest) and os.path.getsize(dest) > 0):
            try:
                with urllib.request.urlopen(f'{FONT_URL}/{fn}', timeout=20) as r, open(dest, 'wb') as f:
                    shutil.copyfileobj(r, f)
            except Exception:
                pass
    for f in VI_FONT_CANDIDATES:
        if os.path.isfile(f):
            say(f'STATUS Vietnamese font OK ({f})')
            return f
    say('STATUS Vietnamese font fallback (default PIL font)')
    return None


def main():
    ff = find_tool('ffmpeg')
    fp = find_tool('ffprobe')
    if not ff or not fp:
        say('STATUS ffmpeg MISSING -> brew install ffmpeg')
        say('NOT READY')
        return 1
    say(f'STATUS ffmpeg OK ({ff})')

    py_ok, venv_py = ensure_venv()
    sfx_ok = ensure_sfx()
    vi_font = find_vi_font()

    if not os.path.isfile(CONFIG_FILE):
        default_cfg = {
            'channelName': 'Tuấn Đi Review',
            'channelHandle': '@tuandireview • Ẩm Thực & Khám Phá',
            'defaultLook': 'vibrant_vlog',
            'fps': 60,
            'lang': 'vi',
            'clipsDir': '~/Downloads',
            'projectsDir': '~/youtube-edits',
            'setupComplete': True,
            'setupDate': datetime.date.today().isoformat(),
        }
        with open(CONFIG_FILE, 'w', encoding='utf-8') as fh:
            json.dump(default_cfg, fh, indent=2, ensure_ascii=False)
            fh.write('\n')

    record = {
        'schema': 1,
        'ready': bool(ff and fp and py_ok),
        'checked': datetime.date.today().isoformat(),
        'os': platform.system().lower(),
        'arch': platform.machine().lower(),
        'skill_dir': SKILL_DIR,
        'python': venv_py,
        'ffmpeg': ff,
        'ffprobe': fp,
        'vi_font': vi_font,
        'sfx': sfx_ok,
    }
    with open(PLATFORM_FILE, 'w', encoding='utf-8') as fh:
        json.dump(record, fh, indent=2)
        fh.write('\n')

    say('READY' if record['ready'] else 'NOT READY')
    return 0 if record['ready'] else 1


if __name__ == '__main__':
    sys.exit(main())
