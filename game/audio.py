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
    _sounds: "dict[str, pygame.mixer.Sound | list[pygame.mixer.Sound]]" = {}

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

    def _noise_iter(seed=None):
        """Generator yielding white noise samples in [-1, 1] from a 32-bit LCG.
        `seed` lets per-play variants pull different noise sequences."""
        state = _LCG_SEED if seed is None else (seed & 0xFFFFFFFF)
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

    def _punch_env(t: float, dur: float, dec_tau: float, punch: float = 0.35) -> float:
        """Instant onset (no attack ramp) with a brief overshoot, then exp decay.
        Mirrors sfxr's env_punch parameter — gives the snap that pickup sounds
        need. `punch` = 0.0..1.0 amount of initial overshoot above unity, decayed
        away over the first ~12 ms."""
        x = t / max(1e-6, dec_tau)
        body = math.exp(-x) if x < 20.0 else 0.0
        if punch > 0 and t < 0.012:
            # Linear taper from (1+punch) at t=0 to 1.0 at t=12ms
            body *= 1.0 + punch * max(0.0, 1.0 - t / 0.012)
        return body

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
                    atk=0.005, dec=None, env="exp",
                    vibrato_hz=0.0, vibrato_depth=0.0,
                    detune_cents=0.0,
                    jump_at=None, jump_to_f=None,
                    punch=0.35, tremolo_hz=0.0, tremolo_depth=0.0):
        """Render a band-limited oscillator voice into `buf` (in-place, mixing).

        env="exp"   → linear attack + exp decay (good for sustained / pad)
        env="punch" → instant onset + exp decay (good for percussive pickups)
        env="hann"  → raised-cosine attack + exp decay (slow pad attack)

        `jump_at` (seconds, optional) instantly jumps the carrier frequency
        from f0 to `jump_to_f` at that point — mirrors sfxr's arpeggio mod and
        the canonical Mario coin's two-note pitch jump.

        `tremolo_*` is amplitude modulation; `vibrato_*` is frequency modulation.
        """
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
            if jump_at is not None and jump_to_f is not None and t >= jump_at:
                # Fixed pitch on the jumped-to note (no further sweep)
                f_base = jump_to_f
            else:
                # Linear pitch sweep f0 → f1 across the full dur (or until jump)
                f_base = f0 + (f1 - f0) * (t / max(1e-6, dur))
            f = f_base * detune_mul
            if vibrato_hz > 0 and vibrato_depth > 0:
                f *= 1.0 + vibrato_depth * math.sin(2 * math.pi * vibrato_hz * t)
            phase += f / sr
            if env == "punch":
                e = _punch_env(t, dur, dec, punch)
            elif env == "hann":
                e = _hann_in(t, atk) * (math.exp(-(t - atk) / max(1e-6, dec))
                                        if t >= atk else 1.0)
            else:
                e = _exp_env(t, dur, atk, dec)
            amp = e * vol
            if tremolo_hz > 0 and tremolo_depth > 0:
                amp *= 1.0 + tremolo_depth * math.sin(2 * math.pi * tremolo_hz * t)
            buf[start_i + j] += _osc(shape, phase, f) * amp

    def _voice_noise(buf, sr, total_n, start_s, dur,
                     vol, lp_hz=None, hp_hz=None,
                     atk=0.001, dec=None, env="exp",
                     am_hz=0.0, am_depth=0.0,
                     seed=None, punch=0.0):
        """Render filtered white noise into `buf`. `lp_hz`/`hp_hz` are one-pole
        cutoffs (None = bypass). `am_*` adds slow amplitude modulation. `env`
        accepts "exp" (linear attack + exp decay), "punch" (sfxr-style instant
        onset), or "hann" (raised-cosine attack). `seed` (optional) selects a
        different noise sequence — used to make per-play variants of repeated
        sounds (flap, etc.) feel organic instead of mechanical."""
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
        ng = _noise_iter(seed)
        for j in range(end_i - start_i):
            t = j / sr
            x = next(ng)
            if lp_a is not None:
                lp_state += lp_a * (x - lp_state)
                x = lp_state
            if hp_a is not None:
                hp_state += hp_a * (x - hp_state)
                x = x - hp_state  # subtract LP → HP
            if env == "punch":
                e = _punch_env(t, dur, dec, punch)
            elif env == "hann":
                e = _hann_in(t, atk) * (math.exp(-(t - atk) / max(1e-6, dec))
                                        if t >= atk else 1.0)
            else:
                e = _exp_env(t, dur, atk, dec)
            amp = vol * e
            if am_hz > 0 and am_depth > 0:
                amp *= 1.0 + am_depth * math.sin(2 * math.pi * am_hz * t)
            buf[start_i + j] += x * amp

    def _render(voices, total_dur_s: float, soft_clip: bool = False) -> bytes:
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
              env="exp", vibrato_hz=0.0, vibrato_depth=0.0,
              tremolo_hz=0.0, tremolo_depth=0.0,
              detune_cents=0.0, jump_at=None, jump_to_f=None, punch=0.35):
        return lambda buf, sr, n: _voice_tone(
            buf, sr, n, start, dur, f0, f1, shape, vol,
            atk=atk, dec=dec, env=env,
            vibrato_hz=vibrato_hz, vibrato_depth=vibrato_depth,
            tremolo_hz=tremolo_hz, tremolo_depth=tremolo_depth,
            detune_cents=detune_cents,
            jump_at=jump_at, jump_to_f=jump_to_f, punch=punch)

    def _noise(start, dur, vol, lp_hz=None, hp_hz=None,
               atk=0.001, dec=None, env="exp", am_hz=0.0, am_depth=0.0,
               seed=None, punch=0.0):
        return lambda buf, sr, n: _voice_noise(
            buf, sr, n, start, dur, vol, lp_hz=lp_hz, hp_hz=hp_hz,
            atk=atk, dec=dec, env=env, am_hz=am_hz, am_depth=am_depth,
            seed=seed, punch=punch)

    def _arp(start, dur1, dur2, f1, f2, shape, vol, env="punch", punch=0.40):
        """Mario-style two-note arpeggio: a short low note that instantly jumps
        to a higher held note. The single oscillator uses pitch-jump rather
        than two separate voices, so phase is continuous (no click)."""
        total = dur1 + dur2
        return _tone(start, total, f1, f1, shape, vol,
                     atk=0.0, dec=total * 0.55, env=env, punch=punch,
                     jump_at=dur1, jump_to_f=f2)

    def _chord(start, dur, freqs, shape, vol, atk=0.006, dec=None,
               detune_cents=0.0):
        """Stack of voices at given frequencies, each at vol/N."""
        per = vol / max(1, len(freqs))
        return [_tone(start, dur, f, f, shape, per,
                      atk=atk, dec=dec, env="exp",
                      detune_cents=detune_cents) for f in freqs]

    def _build_bank() -> "dict[str, list[bytes] | bytes]":
        """Render every sound to WAV bytes. Pure synth — no pygame.mixer dep.
        Returns a dict of name → bytes (single sound) or list[bytes] (variants
        picked at random per play). Repeat-heavy sounds (flap, coin) ship as
        variant lists for organic feel."""

        # Musical anchors. The Mario coin perfect-4th interval (B5 → E6) is
        # the canonical reward gesture; other intervals consonate with this
        # and with C major (Skybit's tonal home).
        _A4   = 440.0
        _C5   = 523.25
        _D5   = 587.33
        _E5   = 659.25
        _G5   = 783.99
        _A5   = 880.00
        _B5   = 987.77
        _C6   = 1046.50
        _E6   = 1318.51
        _G6   = 1567.98
        _A6   = 1760.00
        _C7   = 2093.00

        def _semi(f, n):
            return f * (2 ** (n / 12.0))

        def _flap_variant(seed: int, pitch_mul: float):
            """LP-filtered noise burst + sub pop. Seed picks a different noise
            slice; pitch shift makes consecutive flaps feel organic."""
            return _render([
                _noise(0.000, 0.055, vol=0.40, lp_hz=1100,
                       env="punch", dec=0.025, punch=0.55, seed=seed),
                _tone (0.000, 0.090, 170 * pitch_mul, 85 * pitch_mul,
                       "sine", vol=0.32, env="punch", dec=0.045, punch=0.55),
            ], total_dur_s=0.100)

        def _coin_variant(semitones: float):
            """Mario-style perfect-4th arpeggio (B5 → E6). Single sine voice
            with an instant pitch jump. `semitones` varies pitch per variant."""
            f1 = _semi(_B5, semitones)
            f2 = _semi(_E6, semitones)
            return _render([
                _tone(0.000, 0.130, f1, f1, "sine", 0.62,
                      env="punch", dec=0.080, punch=0.55,
                      jump_at=0.030, jump_to_f=f2),
                _tone(0.030, 0.040, _semi(_E6 * 4, semitones),
                      _semi(_E6 * 4, semitones), "sine", 0.16,
                      env="punch", dec=0.012, punch=0.45),
            ], total_dur_s=0.150)

        def _arp(start, f1, f2, vol, dur=0.110):
            return [_tone(start, dur, f1, f1, "sine", vol,
                          env="punch", dec=dur * 0.55, punch=0.55,
                          jump_at=0.024, jump_to_f=f2)]

        flap_variants = [
            _flap_variant(0xA1B2C3D4, 1.00),
            _flap_variant(0x33445566, 1.06),
            _flap_variant(0x77889900, 0.94),
            _flap_variant(0x12FE34DC, 1.03),
        ]
        coin_variants = [
            _coin_variant( 0.0),
            _coin_variant(+0.5),
            _coin_variant(-0.5),
            _coin_variant(+1.0),
        ]

        # coin_combo: Mario arp one 4th up (E6 → A6)
        coin_combo = _render([
            _tone(0.000, 0.150, _E6, _E6, "sine", 0.62,
                  env="punch", dec=0.090, punch=0.55,
                  jump_at=0.034, jump_to_f=_A6),
            _tone(0.034, 0.045, _A6 * 2, _A6 * 2, "sine", 0.16,
                  env="punch", dec=0.014, punch=0.40),
        ], total_dur_s=0.170)

        # coin_triple: three Mario arps C-E-G ascending
        coin_triple = _render(
            _arp(0.000, _C5, _G5,     0.55, dur=0.090) +
            _arp(0.090, _E5, _B5,     0.58, dur=0.090) +
            _arp(0.180, _G5, _D5 * 2, 0.62, dur=0.130) +
            [_tone(0.205, 0.045, _C7 * 2, _C7 * 2, "sine", 0.18,
                   env="punch", dec=0.014, punch=0.45)],
            total_dur_s=0.330)

        # mushroom: fanfare arp + sustained C-major chord
        def _mush_step(s, f):
            return _tone(s, 0.075, f, f, "triangle", 0.50,
                         env="punch", dec=0.045, punch=0.40)
        mushroom = _render([
            _mush_step(0.000, _C5),
            _mush_step(0.070, _E5),
            _mush_step(0.140, _G5),
            _mush_step(0.210, _C6),
            *_chord(0.290, 0.260, [_C5, _E5, _G5], "triangle",
                    vol=0.55, atk=0.006, dec=0.20, detune_cents=+2),
            *_chord(0.290, 0.260, [_C5, _E5, _G5], "triangle",
                    vol=0.55, atk=0.006, dec=0.20, detune_cents=-2),
            _tone(0.300, 0.060, _C7 * 2, _C7 * 2, "sine", 0.16,
                  env="punch", dec=0.020, punch=0.40),
        ], total_dur_s=0.580)

        # magnet: ascending chime + tremolo + high tinkle
        magnet = _render([
            _tone(0.000, 0.220, _A4, _A5, "triangle", 0.45,
                  env="punch", dec=0.150, punch=0.40,
                  tremolo_hz=10, tremolo_depth=0.18),
            _tone(0.110, 0.060, _A6, _A6, "sine", 0.18,
                  env="punch", dec=0.025, punch=0.30),
        ], total_dur_s=0.260)

        # slowmo: descending sweep + sub octave pad
        slowmo = _render([
            _tone(0.000, 0.300, _A5, _A4, "triangle", 0.50,
                  env="exp", atk=0.005, dec=0.22),
            _tone(0.000, 0.380, _A4 * 0.5, _A4 * 0.5, "sine", 0.22,
                  env="hann", atk=0.040, dec=0.30),
        ], total_dur_s=0.420)

        # thunder: LP-filtered noise rumble with AM wobble + sub
        thunder = _render([
            _noise(0.000, 0.700, vol=0.55, lp_hz=110,
                   env="exp", atk=0.040, dec=0.55,
                   am_hz=3.2, am_depth=0.40, seed=0xBEEF1234),
            _tone (0.000, 0.700, 48, 36, "sine", 0.32,
                   env="exp", atk=0.040, dec=0.55),
        ], total_dur_s=0.760)

        # death: low whomp
        death = _render([
            _noise(0.000, 0.070, vol=0.40, lp_hz=1200,
                   env="punch", dec=0.040, punch=0.50),
            _tone (0.000, 0.260, 220, 60, "sine", 0.50,
                   env="punch", dec=0.18, punch=0.30),
            _tone (0.080, 0.220, 80, 40, "sine", 0.40,
                   env="exp", atk=0.005, dec=0.16),
        ], total_dur_s=0.350)

        # gameover: descending steps + sustained D-minor chord
        def _go(s, f):
            return _tone(s, 0.130, f, f, "triangle", 0.45,
                         env="punch", dec=0.080, punch=0.30)
        gameover = _render([
            _go(0.000, _C5),
            _go(0.140, _A4),
            _go(0.280, _semi(_A4, -3)),  # F4
            *_chord(0.420, 0.320,
                    [_semi(_A4, -7), _semi(_A4, -3), _A4],
                    "triangle", vol=0.50, atk=0.006, dec=0.24, detune_cents=+2),
            *_chord(0.420, 0.320,
                    [_semi(_A4, -7), _semi(_A4, -3), _A4],
                    "triangle", vol=0.50, atk=0.006, dec=0.24, detune_cents=-2),
        ], total_dur_s=0.760)

        # poof: cartoon puff
        poof = _render([
            _noise(0.000, 0.055, vol=0.50, lp_hz=900,
                   env="punch", dec=0.030, punch=0.55),
            _tone (0.010, 0.140, 480, 180, "triangle", 0.46,
                   env="punch", dec=0.090, punch=0.35),
            _tone (0.020, 0.120, 110, 60, "sine", 0.30,
                   env="exp", atk=0.003, dec=0.080),
        ], total_dur_s=0.180)

        # ghost: ethereal swish
        ghost = _render([
            _tone(0.000, 0.380, 700, 900, "sine", 0.34,
                  env="hann", atk=0.050, dec=0.30,
                  vibrato_hz=4.5, vibrato_depth=0.045),
            _noise(0.000, 0.380, vol=0.10, hp_hz=2500,
                   env="hann", atk=0.060, dec=0.30),
        ], total_dur_s=0.420)

        # grow: Mario arp ladder + sustained C-major chord + sparkle
        grow = _render(
            _arp(0.000, _C5, _G5,     0.55, dur=0.080) +
            _arp(0.080, _E5, _B5,     0.58, dur=0.080) +
            _arp(0.160, _G5, _D5 * 2, 0.60, dur=0.090) +
            [
                *_chord(0.260, 0.260, [_C6, _E6, _G6], "triangle",
                        vol=0.50, atk=0.006, dec=0.20, detune_cents=+2),
                *_chord(0.260, 0.260, [_C6, _E6, _G6], "triangle",
                        vol=0.50, atk=0.006, dec=0.20, detune_cents=-2),
                _tone(0.275, 0.055, _C7 * 2, _C7 * 2, "sine", 0.18,
                      env="punch", dec=0.020, punch=0.40),
            ], total_dur_s=0.560)

        return {
            "flap":        flap_variants,
            "coin":        coin_variants,
            "coin_combo":  coin_combo,
            "coin_triple": coin_triple,
            "mushroom":    mushroom,
            "magnet":      magnet,
            "slowmo":      slowmo,
            "thunder":     thunder,
            "death":       death,
            "gameover":    gameover,
            "poof":        poof,
            "ghost":       ghost,
            "grow":        grow,
        }

    def _load_sounds() -> None:
        global _mixer_ok
        try:
            for name, payload in _build_bank().items():
                if isinstance(payload, list):
                    _sounds[name] = [pygame.mixer.Sound(buffer=w) for w in payload]
                else:
                    _sounds[name] = pygame.mixer.Sound(buffer=payload)
        except pygame.error:
            _sounds.clear()
            _mixer_ok = False

    def init() -> None:
        global _mixer_ok
        _mixer_ok = _open_mixer()
        if _mixer_ok:
            _load_sounds()

    import random as _random
    def _play(name: str, volume: float = 1.0) -> None:
        if not _mixer_ok:
            return
        s = _sounds.get(name)
        if s is None:
            return
        if isinstance(s, list):
            s = _random.choice(s)
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
