"""Procedural NES-style chiptune synthesis for Skybit's 13 SFX events.

Stdlib + ffmpeg only — no numpy, no pygame, no external assets.

Each sound is rendered from waveform primitives (sine, square, triangle,
sawtooth, low-passed noise) into a 16-bit mono 44.1 kHz WAV, then piped
through ffmpeg for the project's standard processing chain — silenceremove
+ loudnorm to -16 LUFS + libvorbis q4 mono 44100 — so loudness is
consistent across the catalogue and stays well under the clip ceiling
even when several events overlap.

Run:
    python tools/synth_sounds.py

Output goes straight to game/assets/sounds/ — idempotent (re-running just
overwrites). No state is kept between runs.
"""
import argparse
import array
import math
import os
import pathlib
import random
import struct
import subprocess
import tempfile
import wave


SR        = 44100
OUT_DIR   = pathlib.Path(__file__).parent.parent / "game" / "assets" / "sounds"
TWO_PI    = 2.0 * math.pi


# ── waveform primitives ──────────────────────────────────────────────────────

def _sine(phase):
    return math.sin(phase)

def _square(phase):
    return 1.0 if math.sin(phase) >= 0 else -1.0

def _triangle(phase):
    p = (phase / TWO_PI) % 1.0
    return 4.0 * abs(p - 0.5) - 1.0

def _saw(phase):
    p = (phase / TWO_PI) % 1.0
    return 2.0 * p - 1.0

_WAVE = {
    "sine":     _sine,
    "square":   _square,
    "triangle": _triangle,
    "saw":      _saw,
}


# ── envelope ─────────────────────────────────────────────────────────────────

def _envelope(i, n, atk_n, rel_n):
    """Linear AR envelope: ramp up over atk_n samples, ramp down over rel_n
    samples at the tail. Sustain is the middle plateau at 1.0."""
    a = 1.0
    if atk_n and i < atk_n:
        a = i / atk_n
    tail = n - i
    if rel_n and tail <= rel_n:
        a *= max(0.0, tail / rel_n)
    return a


def lowpass_1pole(samples, cutoff_hz, sample_rate=SR):
    """One-pole IIR low-pass.  α = dt/(RC+dt) with RC = 1/(2π·fc).
    Applied (1) at 3 kHz inside `tone(shape="soft_square")` to tame square-wave
    harmonics, and (2) at 5 kHz inside `render()` as a final post-processing
    pass on every sound for warmer overall timbre."""
    n = len(samples)
    if n == 0:
        return array.array('f')
    rc = 1.0 / (TWO_PI * cutoff_hz)
    dt = 1.0 / sample_rate
    alpha = dt / (rc + dt)
    out = array.array('f', [0.0] * n)
    y = samples[0]
    out[0] = y
    for i in range(1, n):
        y = y + alpha * (samples[i] - y)
        out[i] = y
    return out


# ── tone synthesizer ─────────────────────────────────────────────────────────

def tone(dur_ms, f_start, f_end=None, shape="sine", vol=0.4,
         atk_ms=4, rel_ms=20, sweep="linear", lfo=None,
         vol_ramp_to=None):
    """Single tone with optional pitch sweep, AR envelope, and frequency LFO.

    dur_ms       — total duration in milliseconds.
    f_start      — base frequency at t=0.
    f_end        — frequency at t=dur (defaults to f_start, no sweep).
    shape        — one of "sine", "square", "triangle", "saw".
    vol          — peak volume in [0, 1] (post-envelope, pre-mix).
    atk_ms/rel_ms— linear attack/release in milliseconds.
    sweep        — "linear" (constant df/dt) or "exp" (f0*(f1/f0)^t).
    lfo          — optional callable(t_seconds) -> frequency multiplier.
    vol_ramp_to  — if set, volume linearly ramps from `vol` to `vol_ramp_to`
                   over the full duration (used for "inflating" sounds).
    """
    if shape == "soft_square":
        # Render hard square then post-filter at 3 kHz — same call shape, so
        # call sites can drop in "soft_square" wherever they used "square".
        raw = tone(dur_ms, f_start, f_end, shape="square", vol=vol,
                   atk_ms=atk_ms, rel_ms=rel_ms, sweep=sweep, lfo=lfo,
                   vol_ramp_to=vol_ramp_to)
        return lowpass_1pole(raw, cutoff_hz=3000)
    if f_end is None:
        f_end = f_start
    n = max(1, int(SR * dur_ms / 1000))
    atk_n = int(SR * atk_ms / 1000)
    rel_n = int(SR * rel_ms / 1000)
    fn = _WAVE[shape]
    out = array.array('f', [0.0] * n)

    phase = 0.0
    log_ratio = math.log(f_end / f_start) if (sweep == "exp" and f_start > 0) else 0.0

    for i in range(n):
        t = i / n
        if sweep == "exp" and f_start > 0:
            f = f_start * math.exp(log_ratio * t)
        else:
            f = f_start + (f_end - f_start) * t
        if lfo is not None:
            f *= lfo(i / SR)
        phase += TWO_PI * f / SR
        v = fn(phase)
        amp = vol if vol_ramp_to is None else (vol + (vol_ramp_to - vol) * t)
        out[i] = v * amp * _envelope(i, n, atk_n, rel_n)
    return out


# ── noise synthesizer ────────────────────────────────────────────────────────

def noise(dur_ms, cutoff_hz=4000, vol=0.4, atk_ms=2, rel_ms=80, seed=None):
    """White noise → one-pole low-pass at cutoff_hz, with AR envelope."""
    n = max(1, int(SR * dur_ms / 1000))
    atk_n = int(SR * atk_ms / 1000)
    rel_n = int(SR * rel_ms / 1000)
    rng = random.Random(seed) if seed is not None else random
    rc = 1.0 / (TWO_PI * cutoff_hz)
    dt = 1.0 / SR
    alpha = dt / (rc + dt)
    out = array.array('f', [0.0] * n)
    y = 0.0
    for i in range(n):
        x = rng.uniform(-1.0, 1.0)
        y = y + alpha * (x - y)
        out[i] = y * vol * _envelope(i, n, atk_n, rel_n)
    return out


# ── helpers ──────────────────────────────────────────────────────────────────

def concat(*layers):
    """Concatenate layers head-to-tail (sequence)."""
    out = array.array('f')
    for l in layers:
        out.extend(l)
    return out


def mix(*layers, gains=None):
    """Mix layers in parallel, padding shorter ones with silence at the end."""
    if not layers:
        return array.array('f')
    if gains is None:
        gains = [1.0] * len(layers)
    n = max(len(l) for l in layers)
    out = array.array('f', [0.0] * n)
    for layer, g in zip(layers, gains):
        for i, s in enumerate(layer):
            out[i] += s * g
    return out


def ring_mod(samples, lfo_hz, depth):
    """Multiply each sample by `1 + depth*sin(2*pi*lfo_hz*t)` (depth modulation)."""
    out = array.array('f', [0.0] * len(samples))
    for i, s in enumerate(samples):
        t = i / SR
        out[i] = s * (1.0 + depth * math.sin(TWO_PI * lfo_hz * t))
    return out


def fade_out(samples, ms):
    """Linear fade-out over the last `ms` milliseconds."""
    n = len(samples)
    fn = min(n, int(SR * ms / 1000))
    if fn <= 0:
        return samples
    for i in range(n - fn, n):
        samples[i] *= (n - i) / fn
    return samples


def silence(ms):
    return array.array('f', [0.0] * max(0, int(SR * ms / 1000)))


# ── WAV writer + ffmpeg post-process ─────────────────────────────────────────

def _write_wav(samples, path):
    pcm = bytearray()
    for s in samples:
        v = max(-1.0, min(1.0, s))
        pcm.extend(struct.pack('<h', int(v * 32767)))
    with wave.open(str(path), 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(bytes(pcm))


def _ffmpeg_post(wav_path, ogg_path):
    """silenceremove (head trim) + loudnorm to -16 LUFS + libvorbis q4 mono."""
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-i", str(wav_path),
        "-af", ("silenceremove=start_periods=1:start_silence=0.005:"
                "start_threshold=-60dB,"
                "loudnorm=I=-16:LRA=7:tp=-2"),
        "-ac", "1", "-ar", str(SR),
        "-c:a", "libvorbis", "-q:a", "4",
        str(ogg_path),
    ]
    subprocess.run(cmd, check=True)


def render(name, samples):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    # Global one-pole LP at 5 kHz — single biggest perceived-warmth win.
    # Tames square-harmonic sting while keeping chip character intact.
    samples = lowpass_1pole(samples, cutoff_hz=5000)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp_path = pathlib.Path(tmp.name)
    try:
        _write_wav(samples, tmp_path)
        out = OUT_DIR / f"{name}.ogg"
        _ffmpeg_post(tmp_path, out)
        ms = int(1000 * len(samples) / SR)
        print(f"  wrote {out.name}  ({ms} ms before loudnorm)")
    finally:
        try:
            tmp_path.unlink()
        except OSError:
            pass


# ── 13 sound recipes (Warm Chiptune revision) ───────────────────────────────
#
# Three rules driving every recipe:
#   * fundamentals dropped one octave from the prior version
#   * triangle by default; square only where bite is the character;
#     "soft_square" (square + 3 kHz LP) where we still need chip tone
#   * peak volumes 0.22..0.32 to give loudnorm headroom — warmer body, less sting
# render() applies a global 5 kHz one-pole LP to every output. noise() keeps
# its own internal LP for poof / thunder / grow's pop burst.

def make_flap():
    # Soft-square sweep 160 → 280 Hz — full octave below the prior square.
    return tone(60, 160, 280, shape="soft_square", vol=0.18, atk_ms=4, rel_ms=50)


def make_coin():
    # Two-note triangle chime, B4 → E5 (was B5/E6).
    n1 = tone(65, 494, shape="triangle", vol=0.26, atk_ms=3, rel_ms=30)
    n2 = tone(85, 659, shape="triangle", vol=0.28, atk_ms=3, rel_ms=60)
    return concat(n1, n2)


def make_coin_combo():
    # Same shape, perfect-fifth higher: F#5 → B5.
    n1 = tone(65, 740, shape="triangle", vol=0.27, atk_ms=3, rel_ms=30)
    n2 = tone(85, 988, shape="triangle", vol=0.29, atk_ms=3, rel_ms=60)
    return concat(n1, n2)


def make_coin_triple():
    # Sine arpeggio A4 → C#5 → E5, then 30 ms E5→G5 sparkle on the tail.
    n1  = tone(70, 440, shape="sine", vol=0.28, atk_ms=3, rel_ms=20)
    n2  = tone(70, 554, shape="sine", vol=0.28, atk_ms=3, rel_ms=20)
    n3a = tone(40, 659, shape="sine", vol=0.28, atk_ms=2, rel_ms=2)
    n3b = tone(30, 659, 784, shape="sine", vol=0.28, atk_ms=1, rel_ms=20)
    return concat(n1, n2, n3a, n3b)


def make_mushroom():
    # 6-note "got item!" fanfare, all an octave warmer (C4..C5 instead of C5..C6).
    # Triangle (gain 1.0) stacked with soft_square (gain 0.3) for chip bite
    # without the previous square sting.
    notes = [
        ( 80, 262),   # C4
        ( 80, 330),   # E4
        ( 80, 392),   # G4
        (100, 523),   # C5
        ( 80, 494),   # B4
    ]
    parts = []
    for ms, f in notes:
        tr = tone(ms, f, shape="triangle",    vol=0.24, atk_ms=4, rel_ms=25)
        sq = tone(ms, f, shape="soft_square", vol=0.24, atk_ms=4, rel_ms=25)
        parts.append(mix(tr, sq, gains=[0.7, 0.3]))
    # Final 180 ms C5 with 8 Hz vibrato over the last 100 ms (±0.5%).
    def lfo(t):
        if t < 0.080:
            return 1.0
        return 1.0 + 0.005 * math.sin(TWO_PI * 8.0 * t)
    tr = tone(180, 523, shape="triangle",    vol=0.24, atk_ms=4, rel_ms=40, lfo=lfo)
    sq = tone(180, 523, shape="soft_square", vol=0.24, atk_ms=4, rel_ms=40, lfo=lfo)
    parts.append(mix(tr, sq, gains=[0.7, 0.3]))
    return concat(*parts)


def make_magnet():
    # 3-stage rising sweep, all an octave lower than before.
    s1 = tone(200, 110, 440, shape="triangle",    vol=0.26, atk_ms=4, rel_ms=10,
              sweep="exp")
    s2 = tone(100, 440, 660, shape="soft_square", vol=0.28, atk_ms=2, rel_ms=10)
    s3 = tone( 50, 880,      shape="triangle",    vol=0.30, atk_ms=2, rel_ms=40)
    return concat(s1, s2, s3)


def make_slowmo():
    # Descending triangle 440 → 110 (was 880 → 220). Last 80 ms get 6 Hz vibrato.
    s1 = tone(130, 440, 330, shape="triangle", vol=0.24, atk_ms=4, rel_ms=10)
    s2 = tone(130, 330, 220, shape="triangle", vol=0.26, atk_ms=2, rel_ms=10)
    def lfo(t):
        if t < 0.110:
            return 1.0
        return 1.0 + 0.015 * math.sin(TWO_PI * 6.0 * t)
    s3 = tone(190, 220, 110, shape="triangle", vol=0.28, atk_ms=2, rel_ms=80, lfo=lfo)
    return concat(s1, s2, s3)


def make_grow():
    # Stage 1: soft_square exp-sweep 55 → 330 over 350 ms (octave down), vol
    # ramps 0.20 → 0.30. Stage 3 pop ends at 440 instead of 880 — warmer pop.
    s1 = tone(350, 55, 330, shape="soft_square", vol=0.20, atk_ms=10, rel_ms=10,
              sweep="exp", vol_ramp_to=0.30)
    s2 = silence(30)
    pop = tone(80, 660, 440, shape="triangle", vol=0.32, atk_ms=1, rel_ms=60)
    # Noise burst stays at 2 kHz LP — internal cutoff, untouched by the global LP.
    burst = noise(40, cutoff_hz=2000, vol=0.18, atk_ms=1, rel_ms=20, seed=1)
    return concat(s1, s2, mix(pop, burst))


def make_ghost():
    # Triangle (changed from square) sweeping 220 → 330 → 220 with deep
    # frequency vibrato — produces wobble without the metallic ring-mod tones.
    def lfo(t):
        return 1.0 + 0.4 * math.sin(TWO_PI * 5.5 * t)
    half = tone(200, 220, 330, shape="triangle", vol=0.22, atk_ms=4, rel_ms=10, lfo=lfo)
    back = tone(200, 330, 220, shape="triangle", vol=0.22, atk_ms=2, rel_ms=40, lfo=lfo)
    return concat(half, back)


def make_poof():
    # Tighter noise LP (1.8 kHz, was 2.5 kHz) — under 2 kHz reads as "puff",
    # above as "hiss". Tonal nucleus also dropped an octave (1760 → 880).
    n = noise(120, cutoff_hz=1800, vol=0.32, atk_ms=2, rel_ms=110, seed=2)
    t = tone(80, 880, 440, shape="triangle", vol=0.16, atk_ms=2, rel_ms=60)
    return mix(n, t)


def make_thunder():
    # Triangle dropped 60 → 45 Hz with a tighter wander; noise tail LP 200 → 150 Hz.
    rng = random.Random(7)
    chunk_ms = 50
    total_ms = 800
    n_chunks = total_ms // chunk_ms
    freqs = [45 + rng.uniform(-4, 4) for _ in range(n_chunks + 1)]
    body = array.array('f')
    phase = 0.0
    for ci in range(n_chunks):
        n_in_chunk = int(SR * chunk_ms / 1000)
        for i in range(n_in_chunk):
            t = i / n_in_chunk
            f = freqs[ci] + (freqs[ci + 1] - freqs[ci]) * t
            phase += TWO_PI * f / SR
            body.append(_triangle(phase) * 0.36)
    atk_n = int(SR * 50 / 1000)
    for i in range(atk_n):
        body[i] *= i / atk_n
    tail = noise(600, cutoff_hz=150, vol=0.22, atk_ms=10, rel_ms=400, seed=3)
    pad = silence(200)
    tail = concat(pad, tail)
    return mix(body, tail)


def make_death():
    # 4-note descending soft_square; whole phrase moves down a fourth from before.
    # Bottom note bends G3 → D3 over the last 80 ms.
    n1  = tone( 80, 330, shape="soft_square", vol=0.26, atk_ms=4, rel_ms=20)
    n2  = tone( 80, 294, shape="soft_square", vol=0.28, atk_ms=4, rel_ms=20)
    n3  = tone(100, 247, shape="soft_square", vol=0.30, atk_ms=4, rel_ms=20)
    n4a = tone( 60, 196, shape="soft_square", vol=0.32, atk_ms=4, rel_ms=10)
    n4b = tone( 80, 196, 147, shape="soft_square", vol=0.32, atk_ms=2, rel_ms=60)
    return concat(n1, n2, n3, n4a, n4b)


def make_gameover():
    # 5-note descending phrase G4..G3 (was C5..C4). Triangle + soft_square stack.
    notes = [
        (110, 392),  # G4
        (110, 330),  # E4
        (130, 294),  # D4
        (150, 247),  # B3
    ]
    parts = []
    vols = [0.24, 0.26, 0.28, 0.30]
    for (ms, f), vol in zip(notes, vols):
        tr = tone(ms, f, shape="triangle",    vol=vol, atk_ms=4, rel_ms=25)
        sq = tone(ms, f, shape="soft_square", vol=vol, atk_ms=4, rel_ms=25)
        parts.append(mix(tr, sq, gains=[0.7, 0.3]))
    # Final 200 ms G3, last 100 ms fades to silence.
    tr = tone(200, 196, shape="triangle",    vol=0.32, atk_ms=4, rel_ms=10)
    sq = tone(200, 196, shape="soft_square", vol=0.32, atk_ms=4, rel_ms=10)
    final = mix(tr, sq, gains=[0.7, 0.3])
    fade_out(final, 100)
    parts.append(final)
    return concat(*parts)


# ── recipe registry ──────────────────────────────────────────────────────────

RECIPES = {
    "flap":        make_flap,
    "coin":        make_coin,
    "coin_combo":  make_coin_combo,
    "coin_triple": make_coin_triple,
    "mushroom":    make_mushroom,
    "magnet":      make_magnet,
    "slowmo":      make_slowmo,
    "grow":        make_grow,
    "ghost":       make_ghost,
    "poof":        make_poof,
    "thunder":     make_thunder,
    "death":       make_death,
    "gameover":    make_gameover,
}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--only", nargs="*", metavar="NAME",
                   help="Render only the listed events (default: all 13).")
    args = p.parse_args()

    names = args.only if args.only else list(RECIPES)
    print(f"Rendering {len(names)} sound(s) to {OUT_DIR}/")
    for name in names:
        if name not in RECIPES:
            raise SystemExit(f"unknown event: {name!r}; "
                             f"choices: {sorted(RECIPES)}")
        samples = RECIPES[name]()
        render(name, samples)
    print("Done.")


if __name__ == "__main__":
    main()
