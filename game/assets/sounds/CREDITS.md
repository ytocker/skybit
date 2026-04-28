# Skybit sound effect credits

All audio in this directory is sourced from **Kenney.nl** game audio packs,
which are released under the **Creative Commons Zero (CC0 1.0 Universal)**
license — public domain dedication, no attribution required. We're listing
the sources here as a courtesy and to make audit / replacement easy.

License: <https://creativecommons.org/publicdomain/zero/1.0/>

## Per-event mapping

| Event       | Source pack             | Source file / processing                                      |
|-------------|-------------------------|---------------------------------------------------------------|
| flap        | Kenney RPG Audio        | `cloth_4.ogg` trimmed to 200ms, fade-out                      |
| coin        | Kenney Digital Audio    | `pep_sound_5.ogg` trimmed to 200ms, fade-out                  |
| coin_combo  | Kenney Digital Audio    | `pep_sound_5.ogg` (full ~570ms)                               |
| coin_triple | Kenney Digital Audio    | `pep_sound_5.ogg` + same one octave up (sparkly chime, 200ms) |
| mushroom    | Kenney Music Jingles    | `Steel/jingles_steel_5.ogg`                                   |
| magnet      | Kenney Digital Audio    | `phaser_up_2.ogg`                    |
| slowmo      | Kenney Digital Audio    | `phaser_down_2.ogg`                  |
| thunder     | Kenney Digital Audio    | `low_three_tone.ogg`                 |
| death       | Kenney Impact Sounds    | `impact_soft_heavy_002.ogg`          |
| gameover    | Kenney Music Jingles    | `8-Bit/jingles_nes_15.ogg`           |
| poof        | Kenney Impact Sounds    | `impact_wood_medium_000.ogg`         |
| ghost       | Kenney Digital Audio    | `phase_jump_2.ogg`                   |
| grow        | Kenney Digital Audio    | `power_up_8.ogg`                     |

## Pack URLs

- Kenney Interface Sounds: <https://kenney.nl/assets/interface-sounds>
- Kenney Music Jingles:    <https://kenney.nl/assets/music-jingles>
- Kenney Digital Audio:    <https://kenney.nl/assets/digital-audio>
- Kenney Impact Sounds:    <https://kenney.nl/assets/impact-sounds>

## Processing applied to every file

Each source file was passed through ffmpeg with:

```
silenceremove=start_periods=1:start_silence=0.05:start_threshold=-45dB
loudnorm=I=-16:LRA=11:TP=-1.5
libvorbis -q:a 4 -ac 1 -ar 44100
```

→ leading silence trimmed, loudness normalized to ~-16 LUFS (no event
clips when they overlap), encoded to OGG Vorbis quality 4 mono 44.1 kHz.
