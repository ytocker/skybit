# Skybit — Review Pass

*Played through 20 scripted scenes covering menu flow, core gameplay, tension moments, max/min difficulty, and every biome band in the 5-minute cycle. Screenshots numbered `01_…png` through `20_…png` in this folder.*

---

## First Impressions

Skybit is a one-input arcade game with unusual ambition in its art department. The genre target is obvious (Flappy Bird, tap-to-flap, pass pipes, die, restart), but the presentation refuses the minimal-geometry route and instead commits to a painterly, biome-aware world built entirely from procedural gradients and glows. The first time the sky bleeds from cyan into rose into moonlit navy while you're mid-flight, Skybit looks like it was made by someone who cares. That's rare in this genre.

The hook is intact. The ride is smoother than most clones. And there's a handful of polish items that, addressed, would push it from "impressively crafted" to "please put this on my phone."

---

## Visuals & Art Direction

### What lands

- **Biome rotation is the signature feature.** `18_biome_golden_hour.png` and `19_biome_dusk.png` do what this genre almost never does: make you want to keep playing past a plateau just to see the sky change. Stars fading in at `19_biome_dusk.png` is a lovely moment. Anchoring the cycle to real time (5 min) rather than score is the right call — it rewards presence, not skill.
- **Pillars as Zhangjiajie sandstone.** The silhouette is distinctive enough that nobody will mistake this for Flappy's green cylinders. Vegetation scattered along the column body (`06_gap_traversal.png`, `16_max_difficulty.png`) gives vertical reading: tall pillars tell you the difficulty rose. Mist at the base is a small touch that makes the world feel atmospheric rather than flat.
- **Bird sprite is legible in every biome.** The aviator sunglasses sell personality without needing animation frames. Red body reads against every sky band except — see below — sunset. Orange belly highlights catch the warm biomes.

### What falters

- **Cloud shapes are the weakest visual element.** Compare `06_gap_traversal.png` to `18_biome_golden_hour.png`: the same blob cluster. Four or five deformed ellipses stacked. Against painterly skies, the clouds read as Microsoft Paint. This is the single biggest "why does this look cheap?" offender.
- **Bird-vs-stone contrast drops at sunset.** In `14_death_hitflash.png` the bird's red body sits inches from the rose-tinted pillar; in a real-time crash moment a new player may lose track of where the bird ended up. A thin dark outline on the bird would solve it without retint work.
- **Pillar body still has visible horizontal seams.** Erosion cracks are painted at a fixed `crack_step = 80` offset into each pillar, and since they're not pillar-seeded, pillars near each other share the same horizontal crack heights. Not ruinous — but very tall pillars (`08_combo_x5.png`, `15_death_particles.png`) read as stacked sections rather than continuous stone.

---

## Moment-to-Moment Feel

### What lands

- **Coin juice is exactly right.** `07_coin_grab.png` — localized gold/white sparkles, a "+1" float, and nothing else. No full-screen flash, no camera punch. It's the difference between feeling like the game is celebrating with you and feeling like it's yelling. Rare restraint in a casual game.
- **Mushroom pickup staging is excellent.** `10_mushroom_pickup.png` is a genuine crescendo: the "3X POWER!" text, the orange aura cocooning the bird, the timer bar blooming at the top, the world subtly slowed by `time_scale = 0.35`. For the eight seconds after, the whole game feels *different*. This is juice done properly — reserved for the rare event and given space to land.
- **Combo is communicated once, at the bottom.** The persistent bouncing `X5 COMBO!` badge (`08_combo_x5.png`) in red-on-white replaces the older stacking float-texts; much cleaner now.

### What falters

- **The game has no sound.** Not a note. In a genre defined by micro-feedback, the absence of a flap whoosh, a coin tink, a mushroom fanfare, and a death thud is the #1 thing standing between this and "shippable." No screenshot can show what a game *feels* like without audio — but I can tell you exactly what's missing because every other casual game has these four cues and they carry 30% of the moment-to-moment satisfaction.
- **Mushroom in-gap reads as a speech bubble.** `09_mushroom_in_gap.png` — the pulsing white halo is a perfect circle, and at a glance the mushroom looks *contained* in it rather than *emanating* it. It reads as a call-out, not a powerup. Making the halo softer-edged, elliptical, or layered (instead of one opaque disc) would fix it.
- **The `+3` floatt text during 3X is hard to spot.** `11_triple_active_+3.png` — the aura around the bird swallows small UI text. "+3" should be bigger and/or thrown further outside the aura radius when the buff is active.

---

## UI & Readability

### What lands

- **Name Entry is surprisingly solid.** `05_nameentry.png` — three slots, a yellow cursor indicator, full alphabet grid with `_` for space, DEL/OK buttons big enough for fingers. The "Rank #1 · Score 8" header tells you what you're playing for. This could ship on mobile tomorrow.
- **Leaderboard is legible.** `03_gameover_leaderboard.png` — gold first, orange second, cream third, white rest. Highlight row visually distinct with a blue band. Unfilled rows now dim gracefully (`02_gameover_tryagain.png`). "TAP TO RETRY" pulses correctly.
- **`TRY AGAIN!`** in place of `SCORE 0` on first-pillar deaths is a small empathy fix that reframes failure as invitation.

### What falters

- **HUD overlaps the bird at the ceiling.** `12_ceiling_close.png` — when the bird clips near `y < 40` it goes *behind* (or awkwardly beside) the BEST pill in the top-left. If someone's panic-flapping they can visually lose the bird for a frame, which in a twitch game is fatal. BEST should shrink or translucent-fade when the bird enters the upper 60 px.
- **"NEW BEST!" state is partially correct.** `04_gameover_new_best.png` shows `NEW BEST!` pulsing under the score but the leaderboard below still shows the *previous* top entry in rank 1 (KAT 22) — because the shot bypasses NameEntry. In real play the name-entry flow would insert the player's entry before the leaderboard renders, so this is a test-rig artifact. Still worth flagging: if the leaderboard ever renders *before* insert_score runs, the mismatch will feel broken.
- **Score display has no background plate.** The big centered `11`, `42`, `22` digits across the shots sit directly on whatever sky/pillar is behind them. In `08_combo_x5.png` the `11` is fine against plain sky, but on a frame where it overlaps a pillar (has happened in prior passes) it vanishes. A subtle dark gradient behind the score digit would bulletproof this.

---

## Progression & Difficulty

### What lands

- **Difficulty ramp is perceptible, not punishing.** Compare `17_low_difficulty.png` (score 2, gap 170 px) to `16_max_difficulty.png` (score 42, gap 115 px) — the gap genuinely tightens and the pillars feel more imposing, but `16` is still playable if the player has learned to feather flaps. The ramp hits max at score 35+ and holds there, which is the right choice (no death spiral).
- **Coin arcs teach without tutorialising.** The 5-coin arc patterns (`07_coin_grab.png`) guide the bird through the gap on an ideal trajectory. You learn the correct *path* by chasing coins, which is better than any onboarding text.

### What falters

- **First pillar onset is aggressive.** From `x = 90` the first pillar spawns at `x = 420` and reaches the bird in about 2 seconds. On mobile with no audio cue to start, some new players will drop before they realize the game has started. A 1-second "get ready" indicator or a pulse on the bird before the first pillar locks in would help.
- **No session-length goal.** Top-10 is the only metric. A skilled player has nothing to chase beyond their own score. Even a *per-biome* badge ("First to score during Dusk") or a mushroom-count mini-goal would give returning players a second axis to pursue. Biomes are a beautiful progression mechanic and right now they're passive scenery.

---

## What's Missing

1. **Audio.** Flap whoosh, coin tink, combo chime, mushroom fanfare (plus a lowered-tempo ambient loop for night biomes), impact thud, game-over sting. Non-negotiable for shipping.
2. **Haptics on mobile.** `pygame.haptic` would layer with the lack of audio — a short rumble on death and on mushroom pickup.
3. **A daily seed.** One fixed-seed run per day, shared leaderboard. Turns a casual game into a shareable one.
4. **Parallax mountains moving.** They're drawn each frame from the same noise function — they scroll at a slower rate than pillars, but that motion could be pushed more for depth.
5. **Bird tilt floor.** At high downward velocity the bird reaches `tilt_deg = -60°` (per `Bird.tilt_deg`). Fine. But at positive velocity the bird can read as "crashing" before it's actually crashed, muddying the feedback.

---

## Verdict

Skybit is the rare clone that's actually about something. The Zhangjiajie palette, the real-time biome cycle, the restrained coin feedback, and the mushroom moment-of-glory all suggest a designer with taste. The flaws are uniformly *fixable*: add sound, darken a bird outline, shrink the BEST pill at the ceiling, swap the mushroom halo for something less speech-bubble-like, and offer a second axis of progression.

**Signature moment to keep:** the first time the horizon bleeds into sunset mid-run and the stone pillars shift from warm tan to rose. That's a feature no other tap-to-flap game has. Do not break it.

**Ship-blocker:** silence.

**Quick wins from this review:** cloud shapes (2 hrs), bird outline (15 min), HUD-fade at the ceiling (30 min), mushroom halo shape (30 min), score backdrop (30 min).

---

*Specific frame references throughout this review live under `docs/review/` — 20 PNGs, all reproducible via `python tools/playtest_shots.py`.*
