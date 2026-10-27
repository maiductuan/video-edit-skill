---
name: video-director
description: >-
  Universal video editing director, anti-AI-slop critic, beat-synced montage builder, and multi-platform aspect-ratio
  reframer (16:9 YouTube, 9:16 Reels/TikTok/Shorts, 4:5 Feed, 1:1 Square). Use this skill to plan edits across any
  genre, run the 6 automated quality & EBU R128 loudness gates (audit_video.py), cut B-roll montages to musical beats
  (beat_sync.py), or reframe finished videos across platforms (reframe.py) while enforcing human editorial taste and
  banning AI slop patterns. Trigger with /video-director or requests like 'check this video quality', 'cut these clips
  to the beat of this song', 'convert this video to 9:16 / 4:5 / 16:9', 'audit video loudness and cuts'.
---

# /video-director

The **Editorial Brain & Multi-Platform QA/Repurposing Toolkit** for the video editing suite. While `/video-edit` (9:16 talking-head reels), `/youtube-edit` (16:9 vlogs, reviews & studio episodes), `/commercial-promo` (product/brand promos), and `/podcast-interview` (interviews & vodcasts) handle genre-specific pipelines, **`/video-director`** provides:

1. **Automated 6-Gate Quality & Anti-Slop Audit (`scripts/audit_video.py`)**
2. **Musical Beat-Sync EDL Generator (`scripts/beat_sync.py`)**
3. **Multi-Platform Aspect Ratio Reframer (`scripts/reframe.py` — `16:9`, `9:16`, `4:5`, `1:1`)**
4. **Human Editorial Taste & Anti-AI-Slop Enforcement**

---

## 1. Choosing the Right Skill for the Job

| User Goal / Footage | Primary Skill | Aspect Ratio | Signature Capabilities |
|---|---|---|---|
| **Talking-head vertical clip** (Reels, TikTok, Shorts) | [`/video-edit`](../video-edit/SKILL.md) | `9:16` (`1080×1920`) | CoreML background cutout, words behind head, 3 looks (`bold`, `cool girl`, `cool dude`), animated UI inserts |
| **Vlog, Food/Travel Review, or Sit-down YouTube Episode** | [`/youtube-edit`](../youtube-edit/SKILL.md) | `16:9` (`1920×1080` / `4K`) | A-roll vs B-roll classification, J/L cut B-roll over voice, 6 color looks, 16:9 graphics pack (Intro, Chapters, Lower-Third with Price/Rating, Subscribe), BGM auto-ducking |
| **Product Launch, SaaS/App Demo, or Beat-Synced Commercial** | [`/commercial-promo`](../commercial-promo/SKILL.md) | `16:9`, `9:16`, `4:5`, `1:1` | Beat-synced cuts (`beat_sync.py`), zoom-to-action UI/product focus, high-taste typography, 0.8–1.4s brand end lockup |
| **Podcast, Interview, Two-Person Talk, or Vodcast Clips** | [`/podcast-interview`](../podcast-interview/SKILL.md) | `16:9` & `9:16` Split-Screen | Conversational pause preservation (`250–450ms`), room-tone gap smoothing, speaker lower-thirds, 9:16 dual-speaker vertical layout |
| **Beat-sync montage, Cross-platform reframing, or Final QA Audit** | **`/video-director`** *(this skill)* | All (`16:9`, `9:16`, `4:5`, `1:1`) | `audit_video.py` (6 Gates + LUFS), `beat_sync.py` (music onset cutter), `reframe.py` (smart crop & optical backdrop) |

---

## 2. Core Tools in `scripts/`

Always run scripts with the suite's Python environment (`~/.gemini/config/skills/video-edit/.venv/bin/python` or `python3` when only standard library + `ffmpeg` is used).

### A. Automated 6-Gate Video & Audio Auditor (`audit_video.py`)
Never declare a rendered video "finished" without running `audit_video.py` and inspecting the generated contact sheet:
```bash
python3 "SK/scripts/audit_video.py" "<rendered_video.mp4>" [--target-lufs -14.0]
```
What `audit_video.py` checks and outputs:
- **Gate G0 (Stream & Playability):** Confirms valid video + audio streams, exact resolution, FPS, and duration.
- **Gate G1 (No Black / Dead Frames):** Runs `blackdetect` and `freezedetect` to catch unintended blank or frozen stretches.
- **Gate G2 (Audio Loudness & Peak Master):** Measures EBU R128 Integrated Loudness (`-14.0 LUFS ± 1.5` for YouTube/Reels; `-16.0 LUFS` for Podcasts) and True Peak (`≤ -1.0 dBTP`).
- **Gate G3 (No Digital Silence Dropouts):** Checks that cuts do not drop into dead digital silence (`<-65 dB`) mid-episode.
- **Gate G4 & G5 (Visual & Safe-Zone Sheet):** Writes `<video>_audit_sheet.jpg` (12 evenly spaced frames with timestamps) so you can inspect every title, lower-third, and cut with `read_file`.

### B. Beat-Synced Montage & EDL Builder (`beat_sync.py`)
Given a music file (`.mp3`, `.wav`, `.m4a`) and a folder/list of video clips, `beat_sync.py` detects musical energy peaks (beats/downbeats) and outputs either a beat-locked `edl.json` or a finished beat-synced montage MP4:
```bash
python3 "SK/scripts/beat_sync.py" --music "<song.mp3>" --clips <clip_folder_or_files...> -o "<output_montage.mp4>" [--duration 20] [--pace medium]
```
- `--pace fast`: Cuts every `1.0–1.8s` on beat peaks (high-energy product reel / travel teaser).
- `--pace medium` (default): Cuts every `1.8–3.2s` on musical phrases, shortening beats toward the climax and lingering on the final shot (`Tm1` human pacing rule).
- `--pace slow`: Cuts every `3.2–5.0s` for cinematic travel / documentary sequences.

### C. Multi-Platform Aspect Ratio Reframer (`reframe.py`)
Converts any video cleanly across platforms while respecting each platform's UI safe zone:
```bash
python3 "SK/scripts/reframe.py" "<input.mp4>" --ratio 9:16 --mode crop -o "<out_9x16.mp4>" [--cx 0.5] [--cy 0.45]
python3 "SK/scripts/reframe.py" "<input.mp4>" --ratio 4:5 --mode backdrop -o "<out_4x5.mp4>" [--title "Khám Phá Hội An"]
```
- Supported `--ratio`: `16:9` (`1920×1080`), `9:16` (`1080×1920`), `4:5` (`1080×1350`), `1:1` (`1080×1080`).
- Supported `--mode`:
  - `crop`: Full-bleed optical Lanczos crop centered on `(--cx, --cy)`.
  - `backdrop`: Preserves the full source frame in the center over a soft-blurred, darkened ambient background canvas with optional Vietnamese/English title header.

---

## 3. The 8 Editorial Laws (Anti-AI-Slop Summary)

1. **Every cut has a reason:** Removes dead air, changes visual information, or lands on an action/beat. Never cut mid-word or mid-blink.
2. **Cut the dead air, keep the breath:** Leave `200–350 ms` between sentences so the speaker sounds human, not robotic.
3. **Deliver the promise in the first 3 seconds:** Cold open with the best moment or claim; never start with a slow logo intro or "Xin chào mọi người, lại là mình đây..." filler.
4. **Importance Budget (Max 25% Hero Beats):** If everything is giant, bouncing, and loud, nothing is special. Reserve big kinetic type or full-screen cards for the top 20–25% of moments.
5. **No Page Chrome or Fake HUD:** Never draw `REC`, `01 / SCENE`, `60FPS`, fake corner brackets, or progress bars on screen.
6. **Graphics are Anchored & Concise:** Enter `≤0.4s` before the spoken trigger word, never sit empty, and contain `≤12 words` of structured facts (Place, Price, Score, Key Term) rather than repeating the spoken transcript.
7. **The Voice Never Fights the Mix:** BGM sits `18–22 dB` below speech (auto-ducked), SFX sit `12–24 dB` below speech (max 3 in a row), and final output is mastered to `-14 LUFS` (`≤ -1.0 dBTP`).
8. **Honest Visual QA:** Always inspect the contact sheet (`_audit_sheet.jpg` / `qa_sheet.jpg`) with `read_file` before delivering.
