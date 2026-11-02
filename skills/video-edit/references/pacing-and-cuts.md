# Multi-Genre Pacing, Cuts & Audio Reference (`pacing-and-cuts.md`)

Sourced editorial benchmarks for every major video genre and platform.

---

## 1. Pacing & Cut Frequency by Video Genre

| Genre | Visual Change / Cut Rhythm | Natural Breath Gap | Primary Cut Types | Audio Mix Target |
|---|---|---|---|---|
| **Vertical Talking-Head (`9:16` Reels/TikTok/Shorts)** | Every **2.0–3.5s**; pattern interrupt every **5–7s** | `150–280 ms` | Hard cuts, 4K punch-ins (`1.3x–1.8x`), behind-head kinetic words, UI inserts | Voice `-14 LUFS`, SFX `-16 dB` under voice, BGM optional (`-22 dB`) |
| **YouTube Vlog / Food & Travel Review (`16:9`)** | Event-driven; **3.5–5.5s** average per shot; 3–5 shot sequences (Wide → Medium → Close-up detail) | `220–380 ms` (preserve ambient room/street tone) | J/L cuts (`aroll_with_broll` voice continuing over food/scenery), action cuts | Voice `-14 LUFS`, ambient B-roll `-18 dB`, BGM `-18 dB` (speech) / `-9 dB` (montage) |
| **YouTube Talking-Head / Essay / Tech Review (`16:9`)** | Every **3.0–6.0s** in hook (first 2 min), **4.0–8.0s** in body | `200–350 ms` | Alternating wide / `1.2x` crop, B-roll screen/product overlays, chapter cards | Voice `-14 LUFS`, clean high-pass (`80Hz`), minimal melody-free BGM (`-22 dB`) |
| **Product Promo / Brand Commercial (`16:9`, `9:16`, `4:5`)** | Beat-synced (`1.2–2.8s` per shot); beats shorten toward climax, final shot lingers `0.8–1.4s` | Beat-locked | Cut on musical downbeats or peak motion velocity; zoom-to-click for UI | Master `-14 LUFS`, BGM leads at `-12 LUFS` (or ducks `-14 dB` under voiceover), 1–3 hero SFX hits |
| **Podcast / Multi-Cam Interview (`16:9` & `9:16` Clips)** | Cut on speaker changes and authentic reactions (`4.0–10.0s`) | `250–450 ms` (keep conversational pauses & laughs) | J-cuts (hear speaker 4–8 frames before cutting to them), L-cuts on reactions | `-16 LUFS` (podcast feed) or `-14 LUFS` (YouTube), room tone under all cuts |
| **Screen Tutorial / Walkthrough (`16:9`)** | Driven by UI actions; shots **≥ 4.5s** so viewer can locate cursor & read UI | `350–500 ms` after each action step | Hard cuts between steps, smooth `1.4x–2.0x` zoom to active region, step badges | Voice `-14 LUFS`, subtle click/keystroke SFX (`-20 dB`), no distracting BGM |

---

## 2. The 3 Valid Reasons to Make a Cut

Every cut in an `edl.json` must satisfy at least one of these three editorial criteria:
1. **Removes dead time or a weaker take:** Eliminates a false start, hesitation, or silence while preserving natural breathing (`200–350 ms`).
2. **Advances visual information:** Switches from the speaker to the dish/product/screen they just named, or shifts to a closer detail shot (Wide → Medium → Close-up).
3. **Follows physical or musical motion:** Cuts on an action (putting down a bowl, walking into a shop, clicking a button) or lands on a musical beat in a B-roll montage.

---

## 3. J-Cuts, L-Cuts & B-Roll Weaving

- **L-Cut (Voice continues over B-Roll):** The gold standard for YouTube reviews and vlogs. The host introduces a dish or place on camera (`0.0s–3.0s`), then the video cuts to close-up B-roll of the food/street (`3.0s–8.5s`) while the host's voice continues describing the taste and price, returning to the host on camera for the final verdict.
- **J-Cut (Audio leads Picture by `0.15s–0.40s`):** Start the next scene's audio slightly before its video cut so transitions between chapters or speakers feel fluid rather than abrupt.
- **3-Shot B-Roll Sequence Rule:** When showing a location or dish, prefer a mini-sequence over one long shaky clip:
  1. **Establishing Wide (`2.0–3.0s`):** Exterior sign, street atmosphere, or table spread.
  2. **Medium Action (`2.0–3.5s`):** Pouring broth, picking up chopsticks, walking inside.
  3. **Hero Close-Up (`2.5–4.0s`):** Crisp macro detail of the food/product paired with the `lower_third` price/rating card.
