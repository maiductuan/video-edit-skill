#!/usr/bin/env python3
"""
install_all.py — One-command installer for the Multi-Platform Video Edit Skill Suite.
Installs all 5 skills:
  1. video-edit         (9:16 Reels / TikTok / Shorts talking-head)
  2. youtube-edit       (16:9 YouTube Vlog / Food & Travel Review / Studio Talking-Head)
  3. commercial-promo   (9:16 / 4:5 / 1:1 / 16:9 Product Ad & Promo)
  4. podcast-interview  (16:9 / 9:16 Dual-Speaker Split-Screen Podcast)
  5. video-director     (Master Router, Anti-AI-Slop QA Gate G0-G4, Beat-Sync, Reframe)

Usage:
  python3 install_all.py [--target ~/.claude/skills] [--symlink]
"""
import argparse, os, shutil, subprocess, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
SUB_SKILLS = ['youtube-edit', 'commercial-promo', 'podcast-interview', 'video-director']


def detect_default_targets():
    home = Path.home()
    targets = []
    # Check Antigravity / Gemini config skills dir
    gemini_dir = home / '.gemini' / 'config' / 'skills'
    claude_dir = home / '.claude' / 'skills'
    if gemini_dir.parent.exists():
        targets.append(gemini_dir)
    if claude_dir.parent.exists() or not targets:
        targets.append(claude_dir)
    return targets


def sync_skill(src: Path, dst: Path, use_symlink: bool = False):
    if src.resolve() == dst.resolve():
        print(f"SKIP (already in place): {dst}")
        return
    if use_symlink:
        if dst.is_symlink() or dst.exists():
            if dst.is_dir() and not dst.is_symlink():
                shutil.rmtree(dst)
            else:
                dst.unlink()
        dst.symlink_to(src)
        print(f"SYMLINKED: {dst} -> {src}")
    else:
        if dst.is_symlink():
            dst.unlink()
        shutil.copytree(
            src,
            dst,
            ignore=shutil.ignore_patterns(
                '.git', '.venv', '__pycache__', '*.pyc', '.DS_Store', '.platform.json', 'config.json', 'skills'
            ),
            dirs_exist_ok=True,
        )
        print(f"INSTALLED: {dst}")


def main():
    ap = argparse.ArgumentParser(description='Install the full 5-skill Video Editing Suite.')
    ap.add_argument('--target', help='Target skills directory (default: auto-detect ~/.claude/skills and ~/.gemini/config/skills)')
    ap.add_argument('--symlink', action='store_true', help='Symlink instead of copying files')
    ap.add_argument('--skip-setup', action='store_true', help='Skip running setup.py after copying')
    args = ap.parse_args()

    targets = [Path(args.target).expanduser().resolve()] if args.target else detect_default_targets()

    for target_dir in targets:
        target_dir.mkdir(parents=True, exist_ok=True)
        print(f"\n=== Installing suite into: {target_dir} ===")

        # 1. Install video-edit (root skill)
        video_edit_dst = target_dir / 'video-edit'
        sync_skill(REPO_ROOT, video_edit_dst, use_symlink=args.symlink)

        # 2. Install sub-skills from skills/<name>
        for name in SUB_SKILLS:
            src = REPO_ROOT / 'skills' / name
            if not src.exists():
                print(f"WARNING: {src} not found, skipping.")
                continue
            dst = target_dir / name
            sync_skill(src, dst, use_symlink=args.symlink)

        if not args.skip_setup:
            for setup_skill in ['video-edit', 'youtube-edit']:
                setup_script = target_dir / setup_skill / 'scripts' / 'setup.py'
                if setup_script.exists():
                    print(f"\n--- Running setup.py for {setup_skill} ---")
                    subprocess.run([sys.executable, str(setup_script)], check=False)

    print("\nSUITE_READY: Installed 5 skills (video-edit, youtube-edit, commercial-promo, podcast-interview, video-director)")


if __name__ == '__main__':
    main()
