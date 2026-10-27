# Anti-AI-Slop & Human Editorial Taste Codex (`anti-ai-slop.md`)

Distilled from analyzing 350+ video skills (`awesome-claude-video-skills`, `motionmaxxing`, `agent-video-editor`) and real-world creator feedback. Every skill in this repository MUST follow these rules so the final video looks crafted by an experienced human editor and motion designer — never like an automated "AI slop" template.

---

## 1. Never Ship These 10 "AI Slop" Tells

1. **Fake HUD / Corner Chrome / Storyboard Metadata:**
   - **Ban:** Tracked-caps labels in frame corners (`01 / INTRO`, `REC • 4K 60FPS`, `SCENE 02`, `BAR 1/8 - 120 BPM`), fake viewfinder brackets, decorative progress bars, or date/time stamps.
   - **Human Editor Choice:** Let the footage, composition, and a single clean graphic speak for themselves. Never decorate the frame with production metadata.

2. **Zero-Breath Robotic Speech Cuts:**
   - **Ban:** Slicing every pause down to `0.00s` so words collide without a breath, or cutting in the middle of a hand gesture or eye blink.
   - **Human Editor Choice:** Cut the dead air, **keep the breath (`200–350 ms` between sentences for talking-head/vlog; `250–450 ms` for interviews)**. Start cuts `50–70 ms` before the first consonant and end at the natural decay of the last vowel. Fill any background gap with room tone so the noise floor never drops to digital zero.

3. **Slide-Deck / Empty-Box Graphics:**
   - **Ban:** A graphic box or lower-third fading in empty and waiting 2 seconds for text, or turning a video into a PowerPoint slide with a left-aligned header + bullet list over a flat swatch background.
   - **Human Editor Choice:** A graphic is **never empty**. It enters at most `0.4–0.5s` before the spoken word that names it, with its content already locked in place, and leaves `0.8–1.2s` after the topic finishes.

4. **Uniform Metronome Animation & Elastic Bounce Spam:**
   - **Ban:** Putting the exact same `elastic.out` bounce or uniform `0.1s` stagger on every single word, card, and cut.
   - **Human Editor Choice:** Follow the **Importance Budget**:
     - **Level 1 (Connective — 50% of beats):** Hard cut or clean J/L cut, zero graphic, natural motion.
     - **Level 2 (Supporting — 25–30% of beats):** Subtle 4K punch-in (`1.15x–1.35x`), B-roll cutaway, or a quiet lower-third (`0.28s` smooth deceleration `power3.out`, no bounce).
     - **Level 3 (Hero Moment — at most 20–25% of beats):** Behind-head kinetic punch word, full chapter/location showcase card, or dramatic silence-then-hit payoff.

5. **Wall-to-Wall SFX Spam:**
   - **Ban:** Triggering a `whoosh`, `pop`, or `ding` on every cut, every subtitle line, or on top of an important spoken keyword.
   - **Human Editor Choice:** Place SFX only on intentional visual events (card entrance, chapter transition, CTA click). Keep SFX **`12–24 dB` below the voice** (`volume 0.22–0.32`), trigger the transient `2–4 frames` (`~0.08s`) before the visual peak, and **never repeat the same sound effect more than 3 times in a row**.

6. **Over-Processed Color, Crushed Darks & Fake Grain:**
   - **Ban:** Crushing shadow levels until faces turn muddy orange/red, slapping heavy artificial film grain over compressed H.264 footage (which turns skin into digital noise), or using neon purple/cyan AI gradients.
   - **Human Editor Choice:** Match exposure and white balance across clips first. Keep contrast adjustments gentle (`1.04–1.08`), protect skin tones in the midtones, and use soft optical vignettes only when isolating a studio subject.

7. **Redundant Text Walls Over Speech:**
   - **Ban:** Putting a 25-word paragraph inside an info card while the speaker is saying something else (violates Mayer's coherence and redundancy principles — viewers can either read a paragraph or listen, never both).
   - **Human Editor Choice:** On-screen cards show **structured facts that complement the voice** (Dish/Place Name, Address, Price, Rating `9.2/10`, Chapter Number, Key Metric), capped at **≤10–12 words per card**. Standard subtitles stay **≤42 characters per line, ≤2 lines**.

8. **Unmotivated Zooms & Resolution-Breaking Crops:**
   - **Ban:** Constant slow zooming back and forth on every sentence, zooming across a cut boundary, or zooming past the source resolution until the face is blurry.
   - **Human Editor Choice:** Punch in only to soften a same-angle jump cut or emphasize a key punchline. Never zoom across a cut. Cap 1080p sources at `1.20x` and 4K sources at `1.85x`.

9. **Wallpaper Music That Fights the Voice:**
   - **Ban:** Leaving background music at a flat `-10 dB` volume over dialogue, or cutting off music abruptly at the end without a phrase fade.
   - **Human Editor Choice:** Duck music **`18–22 dB` below the voice** during speech (`volume ~0.12–0.16`), swell smoothly (`0.5–0.8s` ramp) during B-roll-only montages (`volume ~0.38–0.48`), and master the final mix to **`-14 LUFS` integrated, `≤ -1.0 dBTP` true peak**.

10. **Self-Certified "Verified" Renders Without Looking:**
    - **Ban:** Declaring an edit "done and verified" without inspecting rendered frames and measuring audio levels.
    - **Human Editor Choice:** Always run `audit_video.py` / `check_cuts.py` and visually inspect the rendered contact sheet (`qa_sheet.jpg` / `cut_check.jpg`) at thumbnail size and full size to verify legibility, safe zones, Vietnamese diacritics, and cut cleanliness.

---

## 2. Typography & Safe-Zone Standards Across Platforms

| Platform / Format | Resolution | Safe Zone (Keep All Text & Cards Inside) | Subtitle / Caption Standard |
|---|---|---|---|
| **YouTube Landscape (16:9)** | `1920×1080` or `3840×2160` | `x: 88..1832`, `y: 72..960` (keep last 5–15s clear for End Screens) | Bottom-center (`y: 940..1010`), `42–48px`, ≤42 chars/line, ≤2 lines |
| **Reels / TikTok / Shorts (9:16)** | `1080×1920` | `x: 40..980` (`right: 100px` below `y: 1155`), `y: 220..1470` | Chest band (`y: 980..1320`), `56–84px` bold, 2–5 words per group |
| **Instagram / FB Feed (4:5)** | `1080×1350` | `x: 54..1026`, `y: 90..1210` | Lower-middle band (`y: 1020..1180`), `48–64px` |
| **Square Social / LinkedIn (1:1)** | `1080×1080` | `x: 54..1026`, `y: 72..970` | Bottom band (`y: 860..960`), `44–56px` |

### Reading Duration Formula
Every on-screen title, lower-third, or callout must stay visible for at least:
$$\text{Duration} = \max(1.8\text{ s},\ \text{word\_count} \times 0.33\text{ s} + 0.6\text{ s})$$
Never flash a graphic for less than `1.8s` or hold a static card past `6.0s`.
