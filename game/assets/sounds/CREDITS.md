# Skybit sound effect credits

All 13 SFX events in this directory are **procedurally synthesised** from
waveform primitives — sine, square, triangle, sawtooth, and a one-pole
low-passed white-noise generator — using only Python's `wave`, `struct`,
`array`, `math`, and `random` modules. There are no external assets and
no licensed third-party audio.

The synthesis recipes live in [`tools/synth_sounds.py`](../../../tools/synth_sounds.py)
in the repository root. Run

```
python tools/synth_sounds.py
```

to regenerate every OGG in this directory. The script is idempotent —
re-running just overwrites cleanly.

## Per-event mapping

| Event       | Waveform(s)        | Description                                                    |
|-------------|--------------------|----------------------------------------------------------------|
| flap        | square             | 60 ms sweep 320 → 560 Hz, low volume (plays constantly)        |
| coin        | triangle           | Two-note ascending chime — B5 (60 ms) → E6 (80 ms)             |
| coin_combo  | triangle           | Same shape as coin, perfect-fifth higher (F#6 → B6)            |
| coin_triple | sine               | Major arpeggio A5/C#6/E6 + 30 ms sparkle E6 → G6 tail          |
| mushroom    | square + triangle  | 6-note "got item!" fanfare, last note has +12 cent vibrato     |
| magnet      | triangle + square  | 3-stage rising sweep 220 → 880 → 1320 Hz + 1760 Hz ping        |
| slowmo      | triangle           | Descending phrase 880 → 220 Hz, tape-stretch vibrato on tail   |
| grow        | square + tri+noise | 350 ms inflate sweep → 30 ms gap → pop (tri + noise burst)     |
| ghost       | square (ring-mod)  | 5.5 Hz ring modulation depth 0.4 over 440 → 660 → 440 Hz curve |
| poof        | noise + triangle   | LP-noise burst at 2.5 kHz + 1760 → 880 Hz tonal nucleus        |
| thunder     | triangle + noise   | 60 Hz LFO triangle + 200 Hz low-passed noise tail              |
| death       | square             | 4-note descent A4 → G4 → E4 → B3 with B3 → F#3 bend            |
| gameover    | triangle + square  | 5-note descent C5 → C4, C-minor resolution with 100 ms fade    |

## Processing applied to every file

After synthesis, each WAV is piped through ffmpeg with:

```
silenceremove=start_periods=1:start_silence=0.005:start_threshold=-60dB
loudnorm=I=-16:LRA=7:tp=-2
libvorbis -q:a 4 -ac 1 -ar 44100
```

→ leading silence trimmed, loudness normalised to -16 LUFS so events
don't clip when they overlap, then encoded to OGG Vorbis quality 4 mono
44.1 kHz to match what `pygame.mixer` opens at runtime.
