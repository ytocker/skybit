# Skybit — Playtest Critique (autoplay pass)

Ran a headless AI player (`tools/autoplay.py`) through several rounds plus
a scripted max-difficulty scene. Frames live in `docs/critique/` alongside
the reference set in `docs/screenshots/`.

## What works

- **Pillars read as Zhangjiajie.** The Slender Spire silhouette with
  vegetation scattered up the body is dramatic; mist at the base sells it
  further. Biome retinting works cleanly (day/sunset/night shots).
- **Coins are legible.** Slow flip + embossed star + metallic rim is clear
  against every biome. Coin arc patterns are readable in motion.
- **HUD corners are tidy.** BEST pill top-left, coin counter top-right,
  pause button top-right, score centered up top. Not crowded.
- **Bird trail + coin sparkles** feel juicy — no big flash, just localized
  gold particles as specified.

## Issues spotted

### 1. Combo float-texts pile up during fast streaks

On a 5-coin arc, world.py spawns a `"X{n} COMBO!"` FloatText on *every*
pickup at or past combo 3. They stack diagonally in the air mid-flight
(see `docs/critique/03_play_early.png` — three overlapping `Xn COMBO!`
labels plus the persistent bouncing badge at the bottom). Overkill.

**Fix:** drop the per-pickup FloatText. The persistent bouncing badge
drawn by `HUD.draw_play` already communicates the multiplier and
gracefully updates in-place as combo grows.

### 2. Game-Over card says "SCORE 0" after a crash-on-spawn

When the AI (or a player) dies before passing the first pillar, the
overlay still renders "SCORE" / "0" in big gold. That's accurate but
dispiriting — feels like a grade, not a call to try again.

**Fix:** below a threshold (score == 0), swap the label for "TRY AGAIN!"
and skip the giant 0.

### 3. Empty leaderboard rows render as "--- 0"

Ranks 8–10 when unfilled show as `8. ---   0`. The repeated zeros draw
the eye and make a fresh install feel sparse (see `05_game_over.png`).

**Fix:** dim the name+score for empty rows (cream → muted blue-grey) and
drop the literal "0" — keep just the "---" placeholder.

### 4. Vegetation repeats too visibly on very tall pillars

On score-25+ pillars the repeating `pine_med / moss / pine_small / shrub`
pattern walks straight down the column, and because the pine height
wobble is tiny (`rng.randint(-2, 2)`) you can see the pattern (compare
upper vs lower half of the bottom pillar in `03_play_early.png`).

**Fix:** widen the height wobble and vary the lean angle so adjacent
instances look different. Already have the per-pillar seed — just use
it more.

### 5. Pillar body has visible horizontal "seams"

`_make_stone_pillar_body` paints horizontal erosion cracks at a fixed
`crack_step = 80`. Across several pillars those crack bands line up at
similar heights, reading as "construction seams" on very tall pipes
(see `04_play_high_diff.png`). A random offset per pillar would hide
the regularity.

**Fix:** jitter the crack start row per-pillar — not worth doing here,
cache keyed by palette colors only. Tracked for a future pass.

### 6. First-pipe onset is fine; difficulty ramp itself is OK

Gap ramps from 170 px (score 0) to 115 px (score 35+) cleanly; scroll
from 160 → 290 px/s. Max-difficulty scene still looks playable (see
`04_play_high_diff.png`). No change needed.

### 7. Silence

No sound design at all. Dropped out of scope with the deployment code,
but a flap whoosh + coin "tink" would lift it a lot. Future pass.

## Changes landed this pass

The three quick wins — combo stacking, game-over zero-state copy, empty
leaderboard rows — plus wider vegetation wobble for variety. The rest are
tracked here for later.
