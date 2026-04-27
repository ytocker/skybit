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

    def _shape(shape: str, phase: float) -> float:
        x = math.sin(2 * math.pi * phase)
        if shape == "sine":
            return x
        if shape == "square":
            return 1.0 if x > 0 else -1.0
        if shape == "triangle":
            p = phase - math.floor(phase)
            return 4 * abs(p - 0.5) - 1
        return x

    def _envelope(i: int, n: int, attack_s: float = 0.008, release_s: float = 0.12) -> float:
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
        for i in range(n):
            t = i / n
            f = f_start + (f_end - f_start) * t
            phase += f / SAMPLE_RATE
            env = _envelope(i, n, attack_s, release_s)
            s = _shape(shape, phase) * env * volume
            samples.append(max(-32768, min(32767, int(s * 32767))))
        return _wav_bytes(samples)

    def _synth_sequence(steps) -> bytes:
        samples: list[int] = []
        for dur, f0, f1, shape, vol in steps:
            n = int(dur * SAMPLE_RATE)
            phase = 0.0
            for i in range(n):
                t = i / max(1, n)
                f = f0 + (f1 - f0) * t
                phase += f / SAMPLE_RATE
                env = _envelope(i, n, 0.01, 0.08)
                s = _shape(shape, phase) * env * vol
                samples.append(max(-32768, min(32767, int(s * 32767))))
        return _wav_bytes(samples)

    def _load_sounds() -> None:
        global _mixer_ok
        try:
            _sounds["flap"] = pygame.mixer.Sound(
                buffer=_synth(0.07, 260, 520, "square", 0.25, 0.004, 0.05))
            _sounds["coin"] = pygame.mixer.Sound(
                buffer=_synth(0.10, 880, 1320, "sine", 0.40, 0.004, 0.08))
            _sounds["coin_combo"] = pygame.mixer.Sound(
                buffer=_synth(0.13, 1175, 1760, "sine", 0.45, 0.003, 0.09))
            _sounds["coin_triple"] = pygame.mixer.Sound(
                buffer=_synth_sequence([
                    (0.05, 880, 880, "sine", 0.35),
                    (0.06, 1175, 1175, "sine", 0.40),
                    (0.08, 1568, 1568, "sine", 0.45),
                ]))
            _sounds["mushroom"] = pygame.mixer.Sound(
                buffer=_synth_sequence([
                    (0.08, 523, 523, "triangle", 0.42),
                    (0.08, 659, 659, "triangle", 0.42),
                    (0.14, 784, 988, "triangle", 0.50),
                ]))
            _sounds["magnet"] = pygame.mixer.Sound(
                buffer=_synth_sequence([
                    (0.10, 220, 660, "triangle", 0.40),
                    (0.12, 660, 990, "sine", 0.42),
                ]))
            _sounds["slowmo"] = pygame.mixer.Sound(
                buffer=_synth_sequence([
                    (0.10, 880, 660, "triangle", 0.38),
                    (0.10, 660, 440, "triangle", 0.40),
                    (0.18, 440, 220, "sine", 0.45),
                ]))
            _sounds["thunder"] = pygame.mixer.Sound(
                buffer=_synth_sequence([
                    (0.20, 80,  60, "triangle", 0.38),
                    (0.20, 60,  50, "triangle", 0.35),
                    (0.40, 50,  40, "sine",     0.32),
                ]))
            _sounds["death"] = pygame.mixer.Sound(
                buffer=_synth(0.32, 330, 90, "square", 0.45, 0.005, 0.18))
            _sounds["gameover"] = pygame.mixer.Sound(
                buffer=_synth_sequence([
                    (0.12, 523, 523, "triangle", 0.35),
                    (0.12, 440, 440, "triangle", 0.35),
                    (0.14, 349, 349, "triangle", 0.38),
                    (0.18, 262, 262, "triangle", 0.42),
                ]))
            _sounds["poof"] = pygame.mixer.Sound(
                buffer=_synth_sequence([
                    (0.03, 420, 260, "triangle", 0.58),
                    (0.05, 260, 150, "square",   0.44),
                    (0.10, 150,  65, "sine",     0.28),
                ]))
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
