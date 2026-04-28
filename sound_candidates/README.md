# Skybit sound candidates — review & pick

This directory holds **5 candidate sounds per game event** so you can listen to
each one in your audio player and tell me which to ship. All files are CC0 from
[Kenney.nl](https://kenney.nl) (Music Jingles, Digital Audio, Impact Sounds,
Interface Sounds, RPG Audio packs), trimmed of leading silence and normalized
to ~-16 LUFS so volume is consistent across candidates.

**How to review:**
1. Open each `<event>/` folder
2. Listen to `1_*.ogg` through `5_*.ogg`
3. Tell me your pick per event (e.g. "flap=2, coin=4, ...")
4. I swap the chosen files into `game/assets/sounds/` and ship

**Aesthetic target across all 13 sounds:** *cute, pleasant, casual-mobile*. Like
Crossy Road / Stack / Mini Metro feels — warm, friendly, fatigue-free even
after hundreds of plays. Never harsh, never piercing, never aggressive.

---

## Per-event design briefs

### `flap` — wing flap (every input — most-played sound!)
**Should evoke:** A soft little "pf" or "tap". Tiny, organic, imperceptibly
short. The kind of sound you don't consciously notice but feels right with
each tap.
**Should NOT be:** A button click, a sharp tick, anything with treble bite, or
anything over ~120 ms. Every harsh tone here multiplies into fatigue across
hundreds of taps per session.

| # | File | What it is |
|---|---|---|
| 1 | `click_001` | Soft tactile UI click |
| 2 | `click_005` | Slightly muted variant of the above |
| 3 | `tick_001` | Quick "tk" tick |
| 4 | `pluck_001` | Short string pluck (could read as a wing twitch) |
| 5 | `cloth_2` | Fabric whoosh from RPG audio (most "wing-like") |

### `coin` — coin pickup (frequent reward)
**Should evoke:** Sweet, satisfying micro-reward — *"yes, got one!"* — single
warm chime in the mid-high range. Pizzicato pluck or soft mallet bell. Like
Mario coin's *intent* without copying its execution.
**Should NOT be:** Mechanical / clinking metal-coin sounds (those feel cheap
and tinny), anything in the piercing 3-4 kHz range, anything over ~250 ms.

| # | File | What it is |
|---|---|---|
| 1 | `pizzi_0` | Warm pizzicato pluck, mid pitch |
| 2 | `pizzi_3` | Pizzicato, slightly different pitch |
| 3 | `pizzi_5` | Pizzicato, brighter |
| 4 | `pizzi_8` | Pizzicato, longer ring |
| 5 | `steel_0` | Steel chime — different timbre family |

### `coin_combo` — combo pickup (rarer, slightly bigger reward)
**Should evoke:** Sibling of `coin` but brighter / higher / fuller — like *"got
another one, even better!"*. Should still be a single-note feel.
**Should NOT be:** Different family from `coin` — it should feel like the same
instrument, just pitched up.

| # | File | What it is |
|---|---|---|
| 1 | `pizzi_2` | Higher pizzicato |
| 2 | `pizzi_4` | Bright pizzicato run |
| 3 | `pizzi_7` | Longer ringing pizzicato |
| 4 | `pizzi_11` | Pizzicato with a grace note |
| 5 | `steel_5` | Bright steel chime |

### `coin_triple` — triple-multiplier coin (rare, biggest single reward)
**Should evoke:** *"WOW!"* moment — short cheerful chime cluster, a small
twinkly arpeggio that signals something special.
**Should NOT be:** Generic — this is the rarest coin event so it should be
clearly *different* from `coin` / `coin_combo`.

| # | File | What it is |
|---|---|---|
| 1 | `pizzi_6` | Pizzicato cluster / grace notes |
| 2 | `pizzi_10` | Multi-note pizzicato run |
| 3 | `pizzi_15` | Twinkly pizzicato phrase |
| 4 | `steel_3` | Steel chime arpeggio |
| 5 | `steel_15` | Long ringing steel phrase |

### `mushroom` — TRIPLE 3X power-up
**Should evoke:** *"Power up acquired!"* — short joyful jingle, ascending
flutter or chord. Victory-feel without being over-the-top.
**Should NOT be:** Anything aggressive or dramatic — this is a hyper-casual
power-up, not a boss-defeat fanfare.

| # | File | What it is |
|---|---|---|
| 1 | `pizzi_12` | Cheerful pizzicato phrase |
| 2 | `pizzi_15` | Twinkly pizzicato |
| 3 | `steel_5` | Bright steel fanfare |
| 4 | `steel_8` | Warm steel ascending |
| 5 | `nes_3` | NES-style "got item" jingle |

### `magnet` — MAGNET power-up (pulls coins toward bird)
**Should evoke:** Magical/charging-up rising sweep — *"power flowing in"*.
Slight magnetic-buzz quality is good. Should suggest energy gathering.
**Should NOT be:** Aggressive sci-fi laser. Wants to feel friendly-magical.

| # | File | What it is |
|---|---|---|
| 1 | `phaser_up_2` | Smooth rising sweep |
| 2 | `phaser_up_5` | Faster rising sweep |
| 3 | `power_up_3` | Multi-stage power-up rise |
| 4 | `power_up_5` | Quick power-up zip |
| 5 | `power_up_11` | Cheerful power-up phrase |

### `slowmo` — SLOWMO power-up (slows time)
**Should evoke:** Time-warp, dreamy descending — like the world is slowing
down. A gentle drop in pitch / energy.
**Should NOT be:** Death-march doom. Should feel cool, not alarming.

| # | File | What it is |
|---|---|---|
| 1 | `phaser_down_2` | Smooth descending sweep |
| 2 | `phaser_down_3` | Slower descending sweep |
| 3 | `low_down` | Low descending tone |
| 4 | `phase_jump_4` | Wobbly phase shift |
| 5 | `pizzi_16` | Descending pizzicato |

### `poof` — KFC power-up start (and its expiry)
**Should evoke:** Cartoonish "POOF!" — a quick puff of smoke, *appearing /
disappearing*. Light, comical wood-block tap or short impact.
**Should NOT be:** Heavy thud — this is a transformation puff, not an explosion.

| # | File | What it is |
|---|---|---|
| 1 | `wood_medium_000` | Hollow wood tap |
| 2 | `wood_light_000` | Lighter wood tap |
| 3 | `soft_medium_001` | Soft padded thud |
| 4 | `plank_medium_002` | Thicker plank knock |
| 5 | `pluck_002` | UI pluck (more cartoonish) |

### `ghost` — GHOST power-up (phase through pipes)
**Should evoke:** Ethereal *"woooo"* — otherworldly, slightly spooky but cute.
Suggests becoming intangible / phasing out of physical reality.
**Should NOT be:** Scary horror — Skybit ghost is friendly-cute.

| # | File | What it is |
|---|---|---|
| 1 | `phase_jump_1` | Sci-fi phase warble |
| 2 | `phase_jump_2` | Ethereal phase shift |
| 3 | `phaser_up_1` | Long airy rise |
| 4 | `low_three_tone` | Three-tone descending mystic |
| 5 | `space_trash_1` | Wobbly atmospheric |

### `grow` — GROW power-up (bird becomes 2× size)
**Should evoke:** *"Puffing up / inflating"* — ascending tone ladder or rising
sweep that feels like getting bigger.
**Should NOT be:** Same as `magnet` — should feel more triumphant / final.

| # | File | What it is |
|---|---|---|
| 1 | `power_up_3` | Multi-stage rise |
| 2 | `power_up_4` | Bright ascending phrase |
| 3 | `power_up_8` | Quick punchy power-up |
| 4 | `power_up_11` | Cheerful ascending |
| 5 | `phaser_up_3` | Smooth rise with slide |

### `thunder` — storm biome ambient cue
**Should evoke:** Distant rumble — atmospheric, low-frequency, NOT
attention-stealing. Just a weather flavor accent.
**Should NOT be:** Loud or scary — it's background atmosphere.

*Caveat: Kenney doesn't have great real-thunder samples. These are all
synthesized low rumbles from the Digital Audio pack. Best of bad options.
We could also keep this one procedural if none feel right.*

| # | File | What it is |
|---|---|---|
| 1 | `low_random` | Random low burble |
| 2 | `low_three_tone` | Three-tone deep descent |
| 3 | `low_down` | Low descending tone |
| 4 | `space_trash_2` | Atmospheric clattering |
| 5 | `space_trash_3` | Different atmospheric texture |

### `death` — bird hits a pillar
**Should evoke:** Soft *"oof"* / fail moment. You'll die a LOT in this game so
this MUST be playful, not punishing. Cartoon thud or sad blip.
**Should NOT be:** Aggressive crash, dramatic gong, anything frightening. Cute
fail energy.

| # | File | What it is |
|---|---|---|
| 1 | `soft_heavy_002` | Padded heavy thud |
| 2 | `soft_medium_001` | Lighter padded thud |
| 3 | `wood_heavy_003` | Heavy hollow wood thud |
| 4 | `hit_0` | Sad "ohh" hit jingle |
| 5 | `hit_8` | Comedic fail hit jingle |

### `gameover` — game-over screen reveals
**Should evoke:** Short charming sad outro — *"aww, run over"*. A descending
3-note phrase or sad short tune. Charming, NOT depressing.
**Should NOT be:** Long or dramatic. Quick and cute.

| # | File | What it is |
|---|---|---|
| 1 | `nes_15` | Classic 8-bit descending fail |
| 2 | `nes_5` | NES sad melody |
| 3 | `nes_10` | NES short outro |
| 4 | `pizzi_16` | Pizzicato descending |
| 5 | `sax_15` | Sax-like comedic fail |

---

## After you pick

Reply with the picks (e.g. "flap=2, coin=1, coin_combo=3, ..."), and I will:
1. Swap the chosen files into `game/assets/sounds/<event>.ogg`
2. Update `game/assets/sounds/CREDITS.md` with the new mapping
3. Delete this `sound_candidates/` directory
4. Commit & push

If a particular event has nothing that fits — say "none of the flap candidates
work" — I'll pull more options from a different Kenney pack.
