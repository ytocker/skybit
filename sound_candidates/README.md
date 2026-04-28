# Skybit sound candidates — ARCADE FUN palette

5 candidates per game event, all CC0 from [Kenney.nl](https://kenney.nl).
Direction: **wacky, punchy, dopaminergic**. Mario coin chimes, Sonic ring zings,
NES "got item!" fanfares, cartoon boings, comic fail stings. Sounds that make a
player smile.

All trimmed of leading silence and normalized to ~-16 LUFS so volumes are
comparable across candidates.

**How to review:** play each `<event>/N_*.ogg` (1–5), reply with picks
("flap=2, coin=4, …"). I swap chosen files into `game/assets/sounds/`,
delete this folder, ship.

---

## Per-event design briefs (FUN axis)

### `flap` — wing flap on every input
**Demonstrate:** A bouncy, goofy little blip — *"boop!"*. Should feel like a
Mario jump tone, not a UI click. Quick, playful, organic-feeling pitch.

| # | File | Vibe |
|---|---|---|
| 1 | `pep_1` | Cute synth boop |
| 2 | `pep_3` | Lower boop variant |
| 3 | `zap_1` | Quick zap-zing |
| 4 | `high_up` | Bright rising chirp |
| 5 | `pluck_001` | Synth pluck |

### `coin` — coin pickup (most-played reward)
**Demonstrate:** The classic two-note Mario-coin chime. *"ding-DING!"*. Bouncy,
bright, instantly satisfying.

| # | File | Vibe |
|---|---|---|
| 1 | `two_tone_1` | Two-note arcade chime |
| 2 | `two_tone_2` | Different intervals |
| 3 | `zap_two_tone` | Punchier two-note zap |
| 4 | `zap_two_tone_2` | Brighter zap variant |
| 5 | `nes_0` | NES short jingle |

### `coin_combo` — combo pickup
**Demonstrate:** Sibling of coin, more excited / brighter / a third note.
*"ding-ding-DING!"*

| # | File | Vibe |
|---|---|---|
| 1 | `pep_5` | Cute pep boop |
| 2 | `nes_1` | NES bright phrase |
| 3 | `nes_2` | NES alt phrase |
| 4 | `three_tone_1` | Three-note arcade run |
| 5 | `zap_three_tone_up` | Three-note zap up |

### `coin_triple` — triple-multiplier coin (rare jackpot)
**Demonstrate:** *"YOU ROCK!"* triumphant cluster. NES-style fanfare burst.

| # | File | Vibe |
|---|---|---|
| 1 | `nes_3` | NES triumphant phrase |
| 2 | `nes_4` | Alt NES triumphant |
| 3 | `nes_5` | Longer NES win |
| 4 | `nes_8` | NES quick arpeggio |
| 5 | `three_tone_2` | Three-tone arcade variant |

### `mushroom` — TRIPLE 3X power-up
**Demonstrate:** NES "got item!" fanfare. Mario power-up energy. Joyful.

| # | File | Vibe |
|---|---|---|
| 1 | `nes_10` | Quick NES fanfare |
| 2 | `nes_11` | Longer "got item" |
| 3 | `nes_12` | Triumphant NES |
| 4 | `nes_13` | Multi-note fanfare |
| 5 | `nes_16` | Short NES sting |

### `magnet` — MAGNET power-up (pulls coins)
**Demonstrate:** Wacky charging-up — like a vacuum cleaner switching on.
Rising goofy sweep.

| # | File | Vibe |
|---|---|---|
| 1 | `phaser_up_2` | Smooth rising phaser |
| 2 | `phaser_up_4` | Faster phaser zip |
| 3 | `phaser_up_7` | Different phaser flavor |
| 4 | `power_up_5` | Quick power-up pep |
| 5 | `power_up_11` | Cheerful charge-up |

### `slowmo` — SLOWMO power-up
**Demonstrate:** Cartoon "wahhhhh" descent — like a tape player slowing down.
Goofy, NOT scary.

| # | File | Vibe |
|---|---|---|
| 1 | `phaser_down_2` | Smooth descending |
| 2 | `phaser_down_3` | Slower descending |
| 3 | `low_down` | Low descending tone |
| 4 | `phase_jump_4` | Wobbly jump-down |
| 5 | `zap_three_tone_down` | Three-tone zap down |

### `poof` — KFC power-up start/expiry
**Demonstrate:** Silly cartoon puff — *"poof!"* / *"boing!"*. Light, comical.

| # | File | Vibe |
|---|---|---|
| 1 | `pep_2` | Goofy pep boop |
| 2 | `pep_4` | Higher pep boop |
| 3 | `zap_1` | Quick zap |
| 4 | `low_random` | Wacky low burble |
| 5 | `phase_jump_2` | Cartoon phase jump |

### `ghost` — GHOST power-up (phase through pipes)
**Demonstrate:** Wobbly cartoon "wooo" with personality. Slightly spooky-cute.

| # | File | Vibe |
|---|---|---|
| 1 | `phase_jump_1` | Sci-fi phase warble |
| 2 | `phase_jump_3` | Different phase shift |
| 3 | `phase_jump_5` | Faster phase jump |
| 4 | `space_trash_1` | Wobbly atmospheric |
| 5 | `low_three_tone` | Three-tone mystic |

### `grow` — GROW power-up (bird becomes 2× size)
**Demonstrate:** Comic balloon-inflating rise. *"poof! BIGGER!"*. Triumphant
ascending sweep.

| # | File | Vibe |
|---|---|---|
| 1 | `power_up_3` | Multi-stage rise |
| 2 | `power_up_8` | Quick punchy power |
| 3 | `power_up_9` | Rising arcade power |
| 4 | `power_up_12` | Longer power-up phrase |
| 5 | `phaser_up_3` | Rising phaser sweep |

### `thunder` — storm biome ambient cue
**Demonstrate:** Synth low rumble — atmospheric, not scary. Background flavor.

*Best of available; Kenney doesn't have great real thunder.*

| # | File | Vibe |
|---|---|---|
| 1 | `low_random` | Random low burble |
| 2 | `low_down` | Low descending tone |
| 3 | `low_three_tone` | Three-tone deep |
| 4 | `space_trash_2` | Atmospheric clatter |
| 5 | `zap_2` | Long zap |

### `death` — bird hits a pillar
**Demonstrate:** Comic sad-trombone fail blip. You'll die a LOT — must be
playful, NOT punishing. Cartoon "wah-wah-WAHH".

| # | File | Vibe |
|---|---|---|
| 1 | `hit_0` | Sad cartoon fail sting |
| 2 | `hit_4` | Longer comic fail |
| 3 | `hit_8` | Quick fail blip |
| 4 | `hit_11` | Longer descending fail |
| 5 | `hit_16` | Short comic fail |

### `gameover` — game-over screen
**Demonstrate:** NES sad-but-cute outro. *"Aww, run over."* Charming, short.

| # | File | Vibe |
|---|---|---|
| 1 | `nes_5` | Longer NES sad melody |
| 2 | `nes_7` | NES outro phrase |
| 3 | `nes_14` | Quick NES sad |
| 4 | `nes_15` | Classic descending fail |
| 5 | `nes_16` | Short NES outro |

---

## After you pick

Reply with picks ("flap=2, coin=1, …") and I will:
1. Move chosen files into `game/assets/sounds/<event>.ogg`
2. Update `game/assets/sounds/CREDITS.md`
3. Delete this `sound_candidates/` directory
4. Commit & push
