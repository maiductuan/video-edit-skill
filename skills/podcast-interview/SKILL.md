---
name: podcast-interview
description: >-
  Edits multi-speaker podcasts, interviews, and vodcasts into 16:9 full episodes or 9:16 vertical clips (including
  top/bottom split-screen dual-speaker layout or active-speaker crop). Preserves natural conversational pauses
  (250-450ms), bridges cuts with continuous room tone so background ambience never drops to digital zero, generates
  speaker name/role lower-thirds and quote highlight cards, and masters audio to -16 LUFS (podcast standard) or
  -14 LUFS (YouTube/Reels standard). Trigger with /podcast-interview or phrases like 'edit this podcast', 'cut interview
  clips', 'dựng video podcast / phỏng vấn', 'cắt clip podcast dọc 9:16'.
---

# /podcast-interview

Professional Podcast, Interview & Vodcast editor supporting both **16:9 Full Episodes (`1920×1080`)** and **9:16 Vertical Clips (`1080×1920` Split-Screen or Active-Speaker Focus)**.

---

## Core Editorial Rules for Podcasts & Interviews

1. **Preserve Conversational Rhythm (`250–450 ms`):**
   - Unlike solo talking-head reels where pauses are cut tight (`150–250 ms`), interviews rely on natural human timing, reactions, and laughs. Cut only dead air (`>0.65s`), false starts, and filler ("ờm", "à").
2. **J-Cuts & Reaction L-Cuts:**
   - Start the next speaker's audio `4–8 frames` (`0.15–0.25s`) before cutting the camera to them (J-cut), and occasionally hold on the listener's nod/reaction for `1.0–1.5s` while the speaker talks (L-cut).
3. **Continuous Room Tone (Zero Digital Dropouts):**
   - Never let a trim between sentences drop to `-inf dB` digital silence. `render_podcast.py` mixes a subtle `-52 dB` warm room-tone floor under speech edits so every cut sounds invisible on headphones.
4. **Dual-Mode Framing (`16:9` vs `9:16` Split-Screen):**
   - **`16:9` Mode:** Full landscape framing with speaker name/role lower-thirds (`speaker_card`) and topic chapter banners.
   - **`9:16_split` Mode:** Stacks Camera A (or Left Speaker crop) in the top half (`1080×960`) and Camera B (or Right Speaker crop) in the bottom half (`1080×960`) with a thin accent divider and centered captions at `y=960`!

---

## Usage (`render_podcast.py`)

Create `<project_dir>/podcast.json`:
```json
{
  "mode": "9:16_split",
  "target_lufs": -14.0,
  "title_badge": "PODCAST HIGHLIGHT",
  "segments": [
    {
      "clip": "/path/to/interview_16x9.mp4",
      "in": 12.5,
      "out": 28.0,
      "left_speaker_cx": 0.28,
      "right_speaker_cx": 0.72,
      "speaker_name": "Minh Tuấn",
      "speaker_role": "Host • Tuấn Đi Review",
      "quote": "Bí quyết để video không bị cảm giác AI là giữ lại nhịp thở tự nhiên."
    }
  ]
}
```
Run `render_podcast.py`:
```bash
"/Users/laptoptt/.gemini/config/skills/video-edit/.venv/bin/python" "SK/scripts/render_podcast.py" "<project_dir>/podcast.json" -o "<project_dir>/podcast_clip.mp4"
```
