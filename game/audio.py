"""
Procedural audio for Skybit.

Every sound effect is synthesized on import using Python's stdlib (`wave`,
`struct`, `io`, `math`) — no external asset files, no numpy. Falls back to
no-op when `pygame.mixer.init()` can't open an audio device (e.g. headless
snapshot runs with SDL_AUDIODRIVER=dummy).

Call the module-level `play_*` helpers; they guard against a missing mixer.
"""
import io
import math
import os
import struct
import wave

import pygame


SAMPLE_RATE = 22050

_mixer_ok = False


def _safe_init_mixer() -> bool:
    """Open the audio device. Swallow failures so headless tests keep running."""
    if os.environ.get("SDL_AUDIODRIVER") == "dummy":
        return False
    try:
        pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=1, buffer=512)
        return True
    except pygame.error:
        return False


def _wav_bytes(samples: list[int]) -> bytes:
    """Pack 16-bit mono PCM samples into an in-memory WAV blob."""
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SAMPLE_RATE)
        w.writeframes(b"".join(struct.pack("<h", s) for s in samples))
    return buf.getvalue()


def _shape(shape: str, phase: float) -> float:
    """Return a waveform sample in [-1, 1] for a unit-phase cycle."""
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
    """Linear attack/hold/release envelope."""
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


def _synth_sequence(steps: list[tuple[float, float, float, str, float]]) -> bytes:
    """Concatenate several tone segments.
    Each step: (duration_s, f_start, f_end, shape, volume)."""
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


# ── Public API ───────────────────────────────────────────────────────────────

_sounds: dict[str, pygame.mixer.Sound] = {}


def init() -> None:
    """Open the mixer and generate every sound. Safe to call once at startup."""
    global _mixer_ok
    _mixer_ok = _safe_init_mixer()
    if not _mixer_ok:
        return
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
        _sounds["death"] = pygame.mixer.Sound(
            buffer=_synth(0.32, 330, 90, "square", 0.45, 0.005, 0.18))
        _sounds["gameover"] = pygame.mixer.Sound(
            buffer=_synth_sequence([
                (0.12, 523, 523, "triangle", 0.35),
                (0.12, 440, 440, "triangle", 0.35),
                (0.14, 349, 349, "triangle", 0.38),
                (0.18, 262, 262, "triangle", 0.42),
            ]))
    except pygame.error:
        # Mixer opened but sound loading failed — disable.
        _sounds.clear()
        _mixer_ok = False


def _play(name: str, volume: float = 1.0) -> None:
    if not _mixer_ok:
        return
    s = _sounds.get(name)
    if s is None:
        return
    ch = s.play()
    if ch is not None:
        ch.set_volume(volume)


def play_flap() -> None:         _play("flap", 0.55)
def play_coin() -> None:         _play("coin", 0.75)
def play_coin_combo() -> None:   _play("coin_combo", 0.80)
def play_coin_triple() -> None:  _play("coin_triple", 0.85)
def play_mushroom() -> None:     _play("mushroom", 0.85)
def play_death() -> None:        _play("death", 0.75)
def play_gameover() -> None:     _play("gameover", 0.70)
