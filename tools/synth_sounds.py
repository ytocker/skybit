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


# ── 13 sound recipes ─────────────────────────────────────────────────────────

def make_flap():
    # Single square sweep 320 → 560 over 60 ms, vol 0.22.
    return tone(60, 320, 560, shape="square", vol=0.22, atk_ms=4, rel_ms=50)


def make_coin():
    # Two-note ascending triangle chime (Mario coin DNA).
    n1 = tone(60, 988, shape="triangle", vol=0.40, atk_ms=3, rel_ms=30)
    n2 = tone(80, 1318, shape="triangle", vol=0.45, atk_ms=3, rel_ms=60)
    return concat(n1, n2)


def make_coin_combo():
    # Same shape as coin, perfect-fifth higher.
    n1 = tone(60, 1480, shape="triangle", vol=0.40, atk_ms=3, rel_ms=30)
    n2 = tone(80, 1976, shape="triangle", vol=0.45, atk_ms=3, rel_ms=60)
    return concat(n1, n2)


def make_coin_triple():
    # Major arpeggio A5 → C#6 → E6 (sine for premium feel) + sparkle tail.
    n1 = tone(70, 880,  shape="sine", vol=0.42, atk_ms=3, rel_ms=20)
    n2 = tone(70, 1108, shape="sine", vol=0.42, atk_ms=3, rel_ms=20)
    # Final note: 70 ms steady E6 then 30 ms sweep E6 → G6 for sparkle.
    n3a = tone(40, 1318, shape="sine", vol=0.42, atk_ms=2, rel_ms=2)
    n3b = tone(30, 1318, 1568, shape="sine", vol=0.42, atk_ms=1, rel_ms=20)
    return concat(n1, n2, n3a, n3b)


def make_mushroom():
    # 6-note "got item!" fanfare — square + triangle stacked (gain 0.7 on tri).
    notes = [
        ( 80, 523),
        ( 80, 659),
        ( 80, 784),
        (100, 1047),
        ( 80, 988),
    ]
    parts = []
    for ms, f in notes:
        sq = tone(ms, f, shape="square",   vol=0.40, atk_ms=4, rel_ms=25)
        tr = tone(ms, f, shape="triangle", vol=0.40, atk_ms=4, rel_ms=25)
        parts.append(mix(sq, tr, gains=[1.0, 0.7]))
    # Final note 1047 Hz, 180 ms, with +12 cent vibrato over the last 100 ms.
    def lfo(t):
        # Vibrato only after t >= 0.080 s (last 100 ms of the 180 ms note).
        if t < 0.080:
            return 1.0
        return 1.0 + 0.005 * math.sin(TWO_PI * 8.0 * t)
    sq = tone(180, 1047, shape="square",   vol=0.40, atk_ms=4, rel_ms=40, lfo=lfo)
    tr = tone(180, 1047, shape="triangle", vol=0.40, atk_ms=4, rel_ms=40, lfo=lfo)
    parts.append(mix(sq, tr, gains=[1.0, 0.7]))
    return concat(*parts)


def make_magnet():
    # 3-stage rising sweep: triangle 220→880, square 880→1320, triangle ping 1760.
    s1 = tone(200, 220,  880,  shape="triangle", vol=0.40, atk_ms=4,  rel_ms=10, sweep="exp")
    s2 = tone(100, 880,  1320, shape="square",   vol=0.42, atk_ms=2,  rel_ms=10)
    s3 = tone( 50, 1760,        shape="triangle", vol=0.45, atk_ms=2,  rel_ms=40)
    return concat(s1, s2, s3)


def make_slowmo():
    # 3-stage descending phrase, all triangle (warm). Last 80 ms gets vibrato.
    s1 = tone(130, 880, 660, shape="triangle", vol=0.38, atk_ms=4, rel_ms=10)
    s2 = tone(130, 660, 440, shape="triangle", vol=0.40, atk_ms=2, rel_ms=10)
    # Stage 3: 190 ms; the last 80 ms get a 6 Hz vibrato.
    def lfo(t):
        if t < 0.110:
            return 1.0
        return 1.0 + 0.015 * math.sin(TWO_PI * 6.0 * t)
    s3 = tone(190, 440, 220, shape="triangle", vol=0.42, atk_ms=2, rel_ms=80, lfo=lfo)
    return concat(s1, s2, s3)


def make_grow():
    # Stage 1: square exp-sweep 110→660 over 350 ms with vol ramping 0.32→0.45.
    s1 = tone(350, 110, 660, shape="square", vol=0.32, atk_ms=10, rel_ms=10,
              sweep="exp", vol_ramp_to=0.45)
    s2 = silence(30)
    # Stage 3: triangle 1320→880 over 80 ms + noise burst on top of first 40 ms.
    pop = tone(80, 1320, 880, shape="triangle", vol=0.50, atk_ms=1, rel_ms=60)
    burst = noise(40, cutoff_hz=4000, vol=0.25, atk_ms=1, rel_ms=20, seed=1)
    pop_with_burst = mix(pop, burst)
    return concat(s1, s2, pop_with_burst)


def make_ghost():
    # Square parabolic 440→660→440 with 5.5 Hz / 0.4-depth ring-mod.
    half = tone(200, 440, 660, shape="square", vol=0.36, atk_ms=4, rel_ms=10)
    back = tone(200, 660, 440, shape="square", vol=0.36, atk_ms=2, rel_ms=40)
    return ring_mod(concat(half, back), lfo_hz=5.5, depth=0.4)


def make_poof():
    # Noise burst (LP at 2.5 kHz) + tonal nucleus for shape.
    n = noise(120, cutoff_hz=2500, vol=0.45, atk_ms=2, rel_ms=110, seed=2)
    t = tone(80, 1760, 880, shape="triangle", vol=0.20, atk_ms=2, rel_ms=60)
    return mix(n, t)


def make_thunder():
    # Low triangle 60 Hz with a slow random walk + noise tail starting at 200 ms.
    rng = random.Random(7)
    chunks = []
    chunk_ms = 50
    total_ms = 800
    n_chunks = total_ms // chunk_ms
    # Pre-roll the chunk frequencies so we can interpolate cleanly.
    freqs = [60 + rng.uniform(-5, 5) for _ in range(n_chunks + 1)]
    body = array.array('f')
    phase = 0.0
    for ci in range(n_chunks):
        n_in_chunk = int(SR * chunk_ms / 1000)
        for i in range(n_in_chunk):
            t = i / n_in_chunk
            f = freqs[ci] + (freqs[ci + 1] - freqs[ci]) * t
            phase += TWO_PI * f / SR
            v = _triangle(phase) * 0.42
            body.append(v)
    # AR envelope over the body — slow attack, no release here (noise tail
    # carries the trailing energy).
    atk_n = int(SR * 50 / 1000)
    for i in range(atk_n):
        body[i] *= i / atk_n
    # Noise tail starts at 200 ms, lasts 600 ms, 400 ms decay.
    tail = noise(600, cutoff_hz=200, vol=0.20, atk_ms=10, rel_ms=400, seed=3)
    pad = silence(200)
    tail = concat(pad, tail)
    return mix(body, tail)


def make_death():
    # 4-note descending square with a B3→F#3 bend on the last note.
    n1 = tone( 80, 440, shape="square", vol=0.38, atk_ms=4, rel_ms=20)
    n2 = tone( 80, 392, shape="square", vol=0.40, atk_ms=4, rel_ms=20)
    n3 = tone(100, 330, shape="square", vol=0.42, atk_ms=4, rel_ms=20)
    n4a = tone( 60, 247, shape="square", vol=0.45, atk_ms=4, rel_ms=10)
    n4b = tone( 80, 247, 185, shape="square", vol=0.45, atk_ms=2, rel_ms=60)
    return concat(n1, n2, n3, n4a, n4b)


def make_gameover():
    # 5-note descending triangle + square stack. Final note fades out.
    notes = [(110, 523), (110, 440), (130, 392), (150, 330)]
    parts = []
    for ms, f in notes:
        tr = tone(ms, f, shape="triangle", vol=0.40, atk_ms=4, rel_ms=25)
        sq = tone(ms, f, shape="square",   vol=0.40, atk_ms=4, rel_ms=25)
        parts.append(mix(tr, sq, gains=[1.0, 0.6]))
    # Final 200 ms note at C4, fade-out the last 100 ms.
    tr = tone(200, 262, shape="triangle", vol=0.44, atk_ms=4, rel_ms=10)
    sq = tone(200, 262, shape="square",   vol=0.44, atk_ms=4, rel_ms=10)
    final = mix(tr, sq, gains=[1.0, 0.6])
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
