# Skybit sound effect credits

All in-game audio in this directory is sourced from **Kenney.nl** game-audio
packs (Concept C "Pop Mobile Hyper-Casual" round) plus light post-processing
through ffmpeg, with the exceptions noted below. All Kenney content is
released under the **Creative Commons Zero (CC0 1.0 Universal)** license —
public domain dedication, no attribution required. Sources listed here as a
courtesy and to make audit / replacement easy.

License: <https://creativecommons.org/publicdomain/zero/1.0/>

## Per-event mapping

| Event       | Source pack                | Source file(s) and processing                                          |
|-------------|----------------------------|------------------------------------------------------------------------|
| flap        | Kenney Interface Sounds    | `pluck_002.wav`                                                        |
| coin        | Kenney Interface Sounds    | `confirmation_001.wav`                                                 |
| coin_combo  | Kenney Interface Sounds    | `confirmation_001.wav` (same source as `coin`; runtime pitch-shifts per combo step) |
| coin_triple | Kenney Interface Sounds    | `confirmation_001.wav` pitched **+1 semitone** via ffmpeg `asetrate` (same as `triple_coin`) |
| triple_coin | Kenney Interface Sounds    | `confirmation_001.wav` pitched **+1 semitone** — fires once on TRIPLE power-up pickup |
| grow        | Kenney Digital + Impact    | `phaser_up_3.ogg` body + `impact_wood_medium_000.ogg` pop tail (amix, gain 0.5) |
| poof        | Kenney Impact Sounds       | `impact_generic_light_001.ogg`                                         |
| ghost       | Kenney Digital Audio       | `phase_jump_2.ogg` pitched **−1 semitone** + 4-tap `aecho` cave tail   |
| slowmo      | Kenney Digital Audio       | `phaser_down_2.ogg` + long-tap `aecho` reverb (200 / 400 / 600 ms)     |
| magnet      | Kenney Sci-fi Sounds       | `laser_retro_001.ogg` + reverb tail                                    |
| death      | Kenney Music Jingles 8-Bit | `jingles_nes_15.ogg`                                                   |
| thunder     | _(procedural)_             | Stdlib chiptune render — see `tools/synth_sounds.py`. Pending replacement in a follow-up audition. |
| gameover    | _(unused)_                 | File present but not played — `audio.play_gameover()` was removed from `scenes._on_death`; `death.ogg` carries the moment alone. |

## Pack URLs

- Kenney Interface Sounds: <https://kenney.nl/assets/interface-sounds>
- Kenney Music Jingles:    <https://kenney.nl/assets/music-jingles>
- Kenney Digital Audio:    <https://kenney.nl/assets/digital-audio>
- Kenney Impact Sounds:    <https://kenney.nl/assets/impact-sounds>
- Kenney Sci-fi Sounds:    <https://kenney.nl/assets/sci-fi-sounds>

## Processing applied to every file

Each candidate is auditioned and chosen via `tools/build_sound_candidates.py`
(see the `_spec()` dict for the per-event recipe). The build pipeline is:

```
[optional layering via ffmpeg amix with per-input volume]
[optional pitch/effect: asetrate, lowpass, vibrato, tremolo]
[optional aecho reverb tail (subtle / heavy)]
silenceremove=start_periods=1:start_silence=0.005:start_threshold=-60dB
loudnorm=I=-16:LRA=11:TP=-1.5
libvorbis -q:a 4 -ac 1 -ar 44100
```

Loudness normalised to -16 LUFS so events don't clip when they overlap, then
encoded to OGG Vorbis quality 4 mono 44.1 kHz to match what `pygame.mixer`
opens at runtime.
