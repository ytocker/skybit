"""
Procedural audio for Skybit.

Two backends:
  * Native (desktop): synthesize WAV bytes with stdlib (`math`, `struct`) and
    play through `pygame.mixer`. No external asset files, no numpy.
  * Browser (pygbag / Pyodide / emscripten): route every play_* call through
    JavaScript's Web Audio API via `platform.window.skyPlay(name, volume)`.
    pygame.mixer in pygbag is unreliable (pygbag issue #19, discussion #88);
    the JS helper is defined in web.tmpl and synthesizes the same sounds in
    the browser on the first user gesture.

Both backends degrade gracefully when the audio device can't be opened
(headless snapshots, missing JS helper, etc.) — every play_* call is a
silent no-op in that case.
"""
import math
import os
import struct
import sys

import pygame


SAMPLE_RATE = 22050
_CHANNELS = 1
_SAMPLE_WIDTH = 2            # 16-bit PCM
_BITS_PER_SAMPLE = 8 * _SAMPLE_WIDTH
_BYTE_RATE = SAMPLE_RATE * _CHANNELS * _SAMPLE_WIDTH
_BLOCK_ALIGN = _CHANNELS * _SAMPLE_WIDTH

_IS_BROWSER = sys.platform == "emscripten"


# ── Browser backend (Web Audio via platform.window.skyPlay) ──────────────────

if _IS_BROWSER:
    # pygbag exposes the JS window as `platform.window`; Pyodide also exposes
    # it as the `js` module. We prefer `js` because that's the standard Pyodide
    # pattern and works regardless of pygbag internal wrapping.
    _skyPlay = None      # cached reference to the JS function
    _logged_once = False

    def _resolve() -> None:
        """Locate window.skyPlay via js.* first, then platform.window.*."""
        global _skyPlay
        if _skyPlay is not None:
            return
        try:
            import js  # type: ignore
            if hasattr(js, "skyPlay"):
                _skyPlay = js.skyPlay
                _jlog("audio.py: _skyPlay resolved via js.skyPlay")
                return
        except Exception as e:
            _jlog("audio.py: js import failed: " + repr(e))
        try:
            import platform as _pgb  # pygbag platform module
            if hasattr(_pgb, "window") and hasattr(_pgb.window, "skyPlay"):
                _skyPlay = _pgb.window.skyPlay
                _jlog("audio.py: _skyPlay resolved via platform.window.skyPlay")
                return
        except Exception as e:
            _jlog("audio.py: platform import failed: " + repr(e))
        _jlog("audio.py: skyPlay NOT found — sounds will be silent")

    def _jlog(msg: str) -> None:
        """Log to browser console so we can see what's happening."""
        try:
            import js  # type: ignore
            js.console.log(msg)
        except Exception:
            try:
                import platform as _p
                _p.window.console.log(msg)
            except Exception:
                print(msg)

    def init() -> None:
        """No-op — JS (web.tmpl) sets up the AudioContext on first user gesture."""
        _resolve()

    def _play(name: str, volume: float) -> None:
        global _logged_once
        if _skyPlay is None:
            _resolve()
        if _skyPlay is None:
            return
        try:
            _skyPlay(name, volume)
        except Exception as e:
            if not _logged_once:
                _logged_once = True
                _jlog("audio.py: skyPlay(" + name + ") raised: " + repr(e))

    def play_flap() -> None:          _play("flap", 0.55)
    def play_coin() -> None:          _play("coin", 0.75)
    def play_coin_combo() -> None:    _play("coin_combo", 0.80)
    def play_coin_triple() -> None:   _play("coin_triple", 0.85)
    def play_mushroom() -> None:      _play("mushroom", 0.85)
    def play_magnet() -> None:        _play("magnet", 0.75)
    def play_slowmo() -> None:        _play("slowmo", 0.75)
    def play_thunder() -> None:       _play("thunder", 0.85)
    def play_death() -> None:         _play("death", 0.75)
    def play_gameover() -> None:      _play("gameover", 0.70)
    def play_poof() -> None:          _play("poof", 0.88)
    def play_ghost() -> None:         _play("ghost", 0.70)
    def play_grow() -> None:          _play("grow", 0.80)


# ── Native backend (pygame.mixer + synthesized WAV) ──────────────────────────

else:
    _mixer_ok = False
    _sounds: "dict[str, pygame.mixer.Sound]" = {}

    def _open_mixer() -> bool:
        if os.environ.get("SDL_AUDIODRIVER") == "dummy":
            return False
        try:
            pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=1, buffer=512)
            return True
        except Exception:
            return False

    def _wav_bytes(samples: list[int]) -> bytes:
        data = b"".join(struct.pack("<h", s) for s in samples)
        data_size = len(data)
        riff_size = 4 + 24 + 8 + data_size
        return b"".join((
            b"RIFF",
            struct.pack("<I", riff_size),
            b"WAVE",
            b"fmt ",
            struct.pack("<I", 16),
            struct.pack("<H", 1),
            struct.pack("<H", _CHANNELS),
            struct.pack("<I", SAMPLE_RATE),
            struct.pack("<I", _BYTE_RATE),
            struct.pack("<H", _BLOCK_ALIGN),
            struct.pack("<H", _BITS_PER_SAMPLE),
            b"data",
            struct.pack("<I", data_size),
            data,
        ))

    _NYQUIST = SAMPLE_RATE / 2
    _TWO_PI = 2 * math.pi

    def _osc(shape: str, phase: float, f: float) -> float:
        """Band-limited oscillator — mirrors Web Audio OscillatorNode.

        `phase` is in cycles (already integrated f/sr per sample).
        `f` is the instantaneous frequency in Hz, used to clip harmonics that
        would otherwise alias above Nyquist.
        """
        if shape == "sine" or f <= 0:
            return math.sin(_TWO_PI * phase)
        if shape == "square":
            # square = (4/π) Σ_{k=1,3,5,...<Nyquist/f} sin(2π·k·phase)/k
            s = 0.0
            k = 1
            while k * f < _NYQUIST:
                s += math.sin(_TWO_PI * k * phase) / k
                k += 2
            return (4.0 / math.pi) * s
        if shape == "triangle":
            # triangle = (8/π²) Σ_{k=1,3,5,...} (-1)^((k-1)/2) sin(2π·k·phase)/k²
            s = 0.0
            k = 1
            sign = 1.0
            while k * f < _NYQUIST:
                s += sign * math.sin(_TWO_PI * k * phase) / (k * k)
                sign = -sign
                k += 2
            return (8.0 / (math.pi ** 2)) * s
        return math.sin(_TWO_PI * phase)

    def _envelope(i: int, n: int, attack_s: float = 0.008, release_s: float = 0.12) -> float:
        """Linear attack → hold → linear release, matching Web Audio gain ramp:
            setValueAtTime(0, 0); linearRampToValueAtTime(vol, atk);
            setValueAtTime(vol, dur-rel); linearRampToValueAtTime(0, dur).
        """
        a = max(1, int(attack_s * SAMPLE_RATE))
        r = max(1, int(release_s * SAMPLE_RATE))
        if i < a:
            return i / a
        if i > n - r:
            return max(0.0, (n - i) / r)
        return 1.0

    def _synth(duration_s: float, f_start: float, f_end: float,
               shape: str = "sine", volume: float = 0.35,
               attack_s: float = 0.008, release_s: float = 0.12) -> bytes:
        n = int(duration_s * SAMPLE_RATE)
        samples: list[int] = []
        phase = 0.0
        df = (f_end - f_start) / max(1, n)  # linearRampToValueAtTime ≡ linear in i
        for i in range(n):
            f = f_start + df * i
            phase += f / SAMPLE_RATE
            env = _envelope(i, n, attack_s, release_s)
            s = _osc(shape, phase, f) * env * volume
            samples.append(max(-32768, min(32767, int(s * 32767))))
        return _wav_bytes(samples)

    def _synth_sequence(steps) -> bytes:
        samples: list[int] = []
        for dur, f0, f1, shape, vol in steps:
            n = int(dur * SAMPLE_RATE)
            phase = 0.0
            df = (f1 - f0) / max(1, n)
            for i in range(n):
                f = f0 + df * i
                phase += f / SAMPLE_RATE
                env = _envelope(i, n, 0.01, 0.08)
                s = _osc(shape, phase, f) * env * vol
                samples.append(max(-32768, min(32767, int(s * 32767))))
        return _wav_bytes(samples)

    # ── Procedural++ toolkit ─────────────────────────────────────────────────
    # Multi-voice mixer with band-limited oscillators, deterministic noise,
    # one-pole filters, exponential envelopes, vibrato/FM, and detune.
    # Both Python (here) and JS (inject_theme.py) implement the same primitives
    # so the local and deployed sounds are perceptually identical.

    _LCG_SEED = 0x12345678  # deterministic noise across renders

    def _noise_iter():
        """Generator yielding white noise samples in [-1, 1] from a 32-bit LCG."""
        state = _LCG_SEED
        while True:
            state = (state * 1664525 + 1013904223) & 0xFFFFFFFF
            yield (state / 0x80000000) - 1.0

    def _exp_env(t: float, dur: float, atk: float, dec_tau: float) -> float:
        """Linear attack to 1.0 over `atk`, then exponential decay with time
        constant `dec_tau`. Reaches ~0 at t=dur. Matches the perceptual feel
        Web Audio's setTargetAtTime produces."""
        if t < atk:
            return t / max(1e-6, atk)
        # Exponential decay; clamp to avoid arithmetic noise past audible range
        x = (t - atk) / max(1e-6, dec_tau)
        return math.exp(-x) if x < 20.0 else 0.0

    def _hann_in(t: float, atk: float) -> float:
        """Smooth raised-cosine attack from 0 → 1 over `atk` (matches the
        S-curve Web Audio's setTargetAtTime sweeps in with). Used for slow
        pad-style attacks like ghost."""
        if atk <= 0:
            return 1.0
        if t >= atk:
            return 1.0
        return 0.5 - 0.5 * math.cos(math.pi * t / atk)

    def _voice_tone(buf, sr, total_n, start_s, dur,
                    f0, f1, shape, vol,
                    atk=0.005, dec=None, attack_curve="linear",
                    vibrato_hz=0.0, vibrato_depth=0.0,
                    detune_cents=0.0):
        """Render a band-limited oscillator voice into `buf` (in-place, mixing).
        `dec` defaults to `dur * 0.5` for percussive natural decay.
        `detune_cents` shifts pitch by ±cents (1 cent = 1.0006×). Render twice
        with ±d cents for chorus."""
        if dec is None:
            dec = dur * 0.5
        start_i = int(start_s * sr)
        n = int(dur * sr)
        end_i = min(start_i + n, total_n)
        if start_i >= total_n:
            return
        detune_mul = 2 ** (detune_cents / 1200.0)
        phase = 0.0
        for j in range(end_i - start_i):
            t = j / sr
            # Linear pitch sweep f0 → f1 over `dur`
            f = (f0 + (f1 - f0) * (t / max(1e-6, dur))) * detune_mul
            if vibrato_hz > 0 and vibrato_depth > 0:
                f *= 1.0 + vibrato_depth * math.sin(2 * math.pi * vibrato_hz * t)
            phase += f / sr
            env = (_hann_in(t, atk) * math.exp(-(t - atk) / max(1e-6, dec))
                   if attack_curve == "hann" and t >= atk
                   else _exp_env(t, dur, atk, dec))
            buf[start_i + j] += _osc(shape, phase, f) * env * vol

    def _voice_noise(buf, sr, total_n, start_s, dur,
                     vol, lp_hz=None, hp_hz=None,
                     atk=0.001, dec=None, attack_curve="linear",
                     am_hz=0.0, am_depth=0.0):
        """Render filtered white noise into `buf`. `lp_hz`/`hp_hz` are one-pole
        cutoffs (None = bypass). `am_*` adds slow amplitude modulation (used for
        thunder rumble)."""
        if dec is None:
            dec = dur * 0.5
        start_i = int(start_s * sr)
        n = int(dur * sr)
        end_i = min(start_i + n, total_n)
        if start_i >= total_n:
            return
        # One-pole IIR: a = 1 - exp(-2π·fc/sr)  ≈  2π·fc/sr  for fc << sr/2
        lp_a = 1.0 - math.exp(-2 * math.pi * lp_hz / sr) if lp_hz else None
        hp_a = 1.0 - math.exp(-2 * math.pi * hp_hz / sr) if hp_hz else None
        lp_state = 0.0
        hp_state = 0.0
        ng = _noise_iter()
        for j in range(end_i - start_i):
            t = j / sr
            x = next(ng)
            if lp_a is not None:
                lp_state += lp_a * (x - lp_state)
                x = lp_state
            if hp_a is not None:
                hp_state += hp_a * (x - hp_state)
                x = x - hp_state  # subtract LP → HP
            env = (_hann_in(t, atk) * math.exp(-(t - atk) / max(1e-6, dec))
                   if attack_curve == "hann" and t >= atk
                   else _exp_env(t, dur, atk, dec))
            amp = vol * env
            if am_hz > 0 and am_depth > 0:
                amp *= 1.0 + am_depth * math.sin(2 * math.pi * am_hz * t)
            buf[start_i + j] += x * amp

    def _render(voices, total_dur_s: float, soft_clip: bool = True) -> bytes:
        """Mix a list of voice callables into one mono 16-bit PCM buffer.
        Each voice is `lambda buf, sr, n: ...` rendering itself into `buf`."""
        sr = SAMPLE_RATE
        n = int(total_dur_s * sr)
        buf = [0.0] * n
        for v in voices:
            v(buf, sr, n)
        # Gentle saturation to fatten chord stacks; tanh soft-clip
        # at ~0.95 keeps headroom while pulling overdrive harmonics in.
        if soft_clip:
            for i in range(n):
                buf[i] = math.tanh(0.9 * buf[i])
        # Quantize to 16-bit
        out: list[int] = [0] * n
        for i in range(n):
            v = buf[i]
            if v > 1.0: v = 1.0
            elif v < -1.0: v = -1.0
            out[i] = int(v * 32767)
        return _wav_bytes(out)

    # ── Voice factory shortcuts (close over the helpers above) ───────────────

    def _tone(start, dur, f0, f1, shape, vol, atk=0.005, dec=None,
              vibrato_hz=0.0, vibrato_depth=0.0, detune_cents=0.0,
              attack_curve="linear"):
        return lambda buf, sr, n: _voice_tone(
            buf, sr, n, start, dur, f0, f1, shape, vol, atk, dec,
            attack_curve, vibrato_hz, vibrato_depth, detune_cents)

    def _noise(start, dur, vol, lp_hz=None, hp_hz=None,
               atk=0.001, dec=None, am_hz=0.0, am_depth=0.0,
               attack_curve="linear"):
        return lambda buf, sr, n: _voice_noise(
            buf, sr, n, start, dur, vol, lp_hz, hp_hz,
            atk, dec, attack_curve, am_hz, am_depth)

    def _twin(start, dur, f, shape, vol, **kw):
        """Two detuned copies of the same tone, each at half volume."""
        return [
            _tone(start, dur, f, f, shape, vol * 0.5, detune_cents=+5, **kw),
            _tone(start, dur, f, f, shape, vol * 0.5, detune_cents=-5, **kw),
        ]

    def _chord(start, dur, freqs, shape, vol, **kw):
        """Stack of sines/triangles at given frequencies, each at vol/N."""
        per = vol / max(1, len(freqs))
        return [_tone(start, dur, f, f, shape, per, **kw) for f in freqs]

    def _build_bank() -> "dict[str, bytes]":
        """Render every sound to WAV bytes. Pure synth — no pygame.mixer dep."""
        # ── flap (wing whoosh: filtered noise burst + low pop) ───────────
        flap = _render([
            _noise(0.0, 0.060, vol=0.45, lp_hz=1500, atk=0.002, dec=0.025),
            _tone (0.0, 0.080, 180, 90, "sine",   vol=0.30, atk=0.002, dec=0.04),
        ], total_dur_s=0.090)

        # ── coin (bright shimmer: detuned twin + 5th + sparkle ping) ─────
        coin = _render(
            _twin(0.0, 0.120, 1320, "sine", 0.55, atk=0.003, dec=0.060) + [
                _tone(0.0,   0.120, 1980, 1980, "sine", 0.22, atk=0.003, dec=0.060),
                _tone(0.080, 0.040, 4400, 4400, "sine", 0.18, atk=0.001, dec=0.012),
            ], total_dur_s=0.140)

        # ── coin_combo (coin + ascending sweep) ──────────────────────────
        coin_combo = _render(
            _twin(0.0, 0.140, 1480, "sine", 0.58, atk=0.003, dec=0.075) + [
                _tone(0.0,   0.140, 2220, 2220, "sine", 0.24, atk=0.003, dec=0.075),
                _tone(0.0,   0.060,  880, 2200, "sine", 0.22, atk=0.001, dec=0.030),
                _tone(0.090, 0.040, 4900, 4900, "sine", 0.20, atk=0.001, dec=0.012),
            ], total_dur_s=0.160)

        # ── coin_triple (major arpeggio, each step a chord stack) ────────
        # C5(523) E5(659) G5(784); each note = root + 5th, layered
        def _chord_step(start, dur, root, vol):
            return [
                _tone(start, dur, root,        root,        "sine", vol * 0.55,
                      atk=0.003, dec=dur * 0.6, detune_cents=+4),
                _tone(start, dur, root,        root,        "sine", vol * 0.55,
                      atk=0.003, dec=dur * 0.6, detune_cents=-4),
                _tone(start, dur, root * 1.5,  root * 1.5,  "sine", vol * 0.30,
                      atk=0.003, dec=dur * 0.55),
            ]
        coin_triple = _render(
            _chord_step(0.000, 0.060, 523, 0.55) +
            _chord_step(0.060, 0.060, 659, 0.55) +
            _chord_step(0.120, 0.120, 784, 0.65) +
            [_tone(0.130, 0.050, 5200, 5200, "sine", 0.18, atk=0.001, dec=0.020)],
            total_dur_s=0.260)

        # ── mushroom (fanfare arpeggio + final triad chord) ──────────────
        mush_step = lambda s, d, f: _tone(s, d, f, f, "triangle", 0.52,
                                          atk=0.004, dec=d * 0.55)
        mushroom = _render([
            mush_step(0.000, 0.060, 523),
            mush_step(0.060, 0.060, 659),
            mush_step(0.120, 0.060, 784),
            # Final sustained C-major triad (C5 + E5 + G5)
            _tone(0.180, 0.220, 523, 523, "triangle", 0.30,
                  atk=0.005, dec=0.18, detune_cents=+3),
            _tone(0.180, 0.220, 523, 523, "triangle", 0.30,
                  atk=0.005, dec=0.18, detune_cents=-3),
            _tone(0.180, 0.220, 659, 659, "triangle", 0.26, atk=0.005, dec=0.18),
            _tone(0.180, 0.220, 784, 784, "triangle", 0.26, atk=0.005, dec=0.18),
            # Sparkle on the chord
            _tone(0.190, 0.060, 4700, 4700, "sine", 0.16, atk=0.001, dec=0.025),
        ], total_dur_s=0.430)

        # ── magnet (vibrato pulse + ascending sweep) ─────────────────────
        magnet = _render([
            _tone(0.000, 0.110, 220, 660, "triangle", 0.45,
                  atk=0.005, dec=0.080, vibrato_hz=5, vibrato_depth=0.030),
            _tone(0.080, 0.140, 660, 990, "sine",     0.42,
                  atk=0.005, dec=0.090, vibrato_hz=7, vibrato_depth=0.020),
            _tone(0.120, 0.080, 1320, 1320, "sine",   0.18, atk=0.002, dec=0.05),
        ], total_dur_s=0.250)

        # ── slowmo (descending dive + delay echoes + low pad) ────────────
        slowmo = _render([
            _tone(0.000, 0.220, 880, 440, "triangle", 0.50, atk=0.005, dec=0.16),
            _tone(0.090, 0.220, 660, 330, "triangle", 0.30, atk=0.005, dec=0.16),
            _tone(0.180, 0.220, 440, 220, "sine",     0.20, atk=0.005, dec=0.16),
            _tone(0.000, 0.380, 220, 220, "sine",     0.18,
                  atk=0.020, dec=0.30, attack_curve="hann"),
        ], total_dur_s=0.420)

        # ── thunder (low rumble + sub-sine + AM wobble) ──────────────────
        thunder = _render([
            _noise(0.000, 0.700, vol=0.55, lp_hz=120,
                   atk=0.030, dec=0.55, am_hz=4.5, am_depth=0.35),
            _tone (0.000, 0.700, 50, 38, "sine", 0.35, atk=0.030, dec=0.55),
            _noise(0.000, 0.080, vol=0.30, lp_hz=2000, atk=0.001, dec=0.05),  # crack onset
        ], total_dur_s=0.760)

        # ── death (descending sweep + crash noise + low thud) ────────────
        death = _render([
            _noise(0.000, 0.080, vol=0.45, lp_hz=2000, atk=0.001, dec=0.045),
            _tone (0.000, 0.220, 330,  90, "square", 0.40, atk=0.004, dec=0.16),
            _tone (0.150, 0.180,  80,  40, "sine",   0.45, atk=0.005, dec=0.13),
        ], total_dur_s=0.380)

        # ── gameover (sad descending arpeggio + final minor chord) ──────
        go_step = lambda s, d, f: _tone(s, d, f, f, "triangle", 0.45,
                                        atk=0.004, dec=d * 0.55)
        gameover = _render([
            go_step(0.000, 0.120, 523),
            go_step(0.120, 0.120, 440),
            go_step(0.240, 0.140, 349),
            # D-minor-ish landing triad: D4(294) F4(349) A4(440)
            _tone(0.380, 0.300, 294, 294, "triangle", 0.30,
                  atk=0.006, dec=0.24, detune_cents=+3),
            _tone(0.380, 0.300, 294, 294, "triangle", 0.30,
                  atk=0.006, dec=0.24, detune_cents=-3),
            _tone(0.380, 0.300, 349, 349, "triangle", 0.24, atk=0.006, dec=0.24),
            _tone(0.380, 0.300, 440, 440, "triangle", 0.20, atk=0.006, dec=0.24),
        ], total_dur_s=0.700)

        # ── poof (KFC: noise impact + cartoon boing) ─────────────────────
        poof = _render([
            _noise(0.000, 0.060, vol=0.55, lp_hz=900, atk=0.001, dec=0.035),
            _tone (0.010, 0.140, 420, 180, "triangle", 0.48,
                   atk=0.002, dec=0.090, vibrato_hz=8, vibrato_depth=0.040),
            _tone (0.020, 0.120, 130, 70,  "sine",     0.34, atk=0.003, dec=0.090),
        ], total_dur_s=0.180)

        # ── ghost (ethereal vibrato sine + breathy HP-noise wash) ───────
        ghost = _render([
            _tone(0.000, 0.520, 800, 800, "sine", 0.36,
                  atk=0.060, dec=0.42, attack_curve="hann",
                  vibrato_hz=3.0, vibrato_depth=0.040),
            _tone(0.020, 0.480, 1200, 1200, "sine", 0.22,
                  atk=0.060, dec=0.38, attack_curve="hann",
                  vibrato_hz=2.5, vibrato_depth=0.025),
            _noise(0.000, 0.520, vol=0.10, hp_hz=2500,
                   atk=0.080, dec=0.40, attack_curve="hann"),
        ], total_dur_s=0.560)

        # ── grow (rising chord ladder + final C-major chord + sparkle) ──
        grow_step = lambda s, d, f: _tone(s, d, f, f, "triangle", 0.50,
                                          atk=0.003, dec=d * 0.55)
        grow = _render([
            grow_step(0.000, 0.060, 523),  # C5
            grow_step(0.060, 0.060, 659),  # E5
            grow_step(0.120, 0.060, 784),  # G5
            # Sustained final C-major triad with sparkle
            _tone(0.180, 0.240, 1046, 1046, "triangle", 0.32,
                  atk=0.004, dec=0.18, detune_cents=+4),
            _tone(0.180, 0.240, 1046, 1046, "triangle", 0.32,
                  atk=0.004, dec=0.18, detune_cents=-4),
            _tone(0.180, 0.240,  784,  784, "triangle", 0.28, atk=0.004, dec=0.18),
            _tone(0.180, 0.240, 1318, 1318, "triangle", 0.24, atk=0.004, dec=0.18),
            _tone(0.190, 0.060, 5200, 5200, "sine",     0.18, atk=0.001, dec=0.025),
        ], total_dur_s=0.460)

        return {
            "flap": flap, "coin": coin, "coin_combo": coin_combo,
            "coin_triple": coin_triple, "mushroom": mushroom,
            "magnet": magnet, "slowmo": slowmo, "thunder": thunder,
            "death": death, "gameover": gameover, "poof": poof,
            "ghost": ghost, "grow": grow,
        }

    def _load_sounds() -> None:
        global _mixer_ok
        try:
            for name, wav in _build_bank().items():
                _sounds[name] = pygame.mixer.Sound(buffer=wav)
        except pygame.error:
            _sounds.clear()
            _mixer_ok = False

    def init() -> None:
        global _mixer_ok
        _mixer_ok = _open_mixer()
        if _mixer_ok:
            _load_sounds()

    def _play(name: str, volume: float = 1.0) -> None:
        if not _mixer_ok:
            return
        s = _sounds.get(name)
        if s is None:
            return
        ch = s.play()
        if ch is not None:
            ch.set_volume(volume)

    def play_flap() -> None:          _play("flap", 0.55)
    def play_coin() -> None:          _play("coin", 0.75)
    def play_coin_combo() -> None:    _play("coin_combo", 0.80)
    def play_coin_triple() -> None:   _play("coin_triple", 0.85)
    def play_mushroom() -> None:      _play("mushroom", 0.85)
    def play_magnet() -> None:        _play("magnet", 0.75)
    def play_slowmo() -> None:        _play("slowmo", 0.75)
    def play_thunder() -> None:       _play("thunder", 0.85)
    def play_death() -> None:         _play("death", 0.75)
    def play_gameover() -> None:      _play("gameover", 0.70)
    def play_poof() -> None:          _play("poof", 0.88)
    def play_ghost() -> None:         _play("ghost", 0.70)
    def play_grow() -> None:          _play("grow", 0.80)
