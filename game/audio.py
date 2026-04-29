"""
Skybit audio: plays procedurally-synthesised SFX on both backends.

* Native (desktop / pygbag main thread):
    pygame.mixer.Sound(file=...) loads the OGGs once at init() time and
    plays them via mixer channels. The native backend additionally adds
    three runtime polish features on top of the rendered files:

      1. Pitch-shift on combo — `play_coin_combo` and `play_coin_triple`
         take a `chain_step` argument and pick a pre-computed +N-semitone
         variant of the source so consecutive coins climb in pitch.
      2. Pitch-jitter on flap — flap.ogg plays back as one of five small
         pitch variants picked at random per call, so 100+ flaps per run
         don't fatigue the ear.
      3. Voice limiting — each high-frequency SFX (coin / coin_combo /
         coin_triple / flap) caps concurrent playing channels so a coin
         rush of 14 simultaneous coins doesn't muddy.

* Browser (pygbag / Pyodide / emscripten):
    Each play_X() call routes to JS window.skyPlay(name, volume), which
    is defined in inject_theme.py. The JS side fetches the same OGG
    files that inject_theme.py copies to build/web/sounds/ at build
    time, then plays them through Web Audio. The runtime polish above
    is native-only for now — the browser plays the rendered (neutral-
    pitch) files.

Both backends degrade gracefully when the audio device can't be opened
(headless snapshots, missing JS helper, etc.) — every play_X call is a
silent no-op in that case.
"""
import os
import random
import struct
import sys
import wave

import pygame


_IS_BROWSER = sys.platform == "emscripten"

_SOUND_DIR = os.path.join(os.path.dirname(__file__), "assets", "sounds")

_SOUND_FILES = (
    "flap", "coin", "coin_combo", "coin_triple", "triple_coin",
    "magnet", "slowmo", "thunder", "death", "gameover",
    "poof", "ghost", "grow",
)


# ── Browser backend (Web Audio via platform.window.skyPlay) ──────────────────

if _IS_BROWSER:
    _skyPlay = None
    _logged_once = False

    def _resolve() -> None:
        global _skyPlay
        if _skyPlay is not None:
            return
        try:
            import js  # type: ignore
            if hasattr(js, "skyPlay"):
                _skyPlay = js.skyPlay
                return
        except Exception:
            pass
        try:
            import platform as _pgb  # pygbag platform module
            if hasattr(_pgb, "window") and hasattr(_pgb.window, "skyPlay"):
                _skyPlay = _pgb.window.skyPlay
                return
        except Exception:
            pass

    def init() -> None:
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
                try:
                    import js  # type: ignore
                    js.console.log("audio.py: skyPlay(" + name + ") raised: " + repr(e))
                except Exception:
                    print("audio.py: skyPlay(" + name + ") raised:", e)


# ── Native backend (pygame.mixer + procedural OGG files) ────────────────────

else:
    _mixer_ok = False
    _sounds: "dict[str, pygame.mixer.Sound]" = {}

    # Pre-computed pitch-shifted variants for the events that benefit. Each
    # value is a list of mixer.Sound objects keyed by semitone offset.
    _flap_variants: "list[pygame.mixer.Sound]" = []          # -2..+2 semitones
    _combo_variants: "list[pygame.mixer.Sound]" = []         # +0..+12 semitones
    _triple_variants: "list[pygame.mixer.Sound]" = []        # +0..+12 semitones

    # Voice-limiting: per-event lists of currently-playing channels. Capped at
    # _VOICE_CAPS[name] concurrent channels; oldest is stopped to free a slot.
    _channels: "dict[str, list[pygame.mixer.Channel]]" = {}
    _VOICE_CAPS = {
        "flap":        2,
        "coin":        2,
        "coin_combo":  2,
        "coin_triple": 2,
    }

    # ── pure-Python pitch shifter ──────────────────────────────────────────

    def _read_wav_bytes_from_ogg(ogg_path: str) -> "tuple[list[int], int]":
        """Decode an OGG via pygame and return (samples, sample_rate). The
        samples list is mono int16 in native byte order. We use this only at
        init() time for the small set of variant sources, so the conversion
        cost is paid once per process."""
        snd = pygame.mixer.Sound(file=ogg_path)
        raw = snd.get_raw()
        # pygame.mixer was opened with size=-16, channels=1, freq=44100 below,
        # so raw is little-endian int16 mono — but be defensive about channels.
        try:
            mixer_freq, mixer_size, mixer_channels = pygame.mixer.get_init()
        except Exception:
            mixer_freq, mixer_size, mixer_channels = 44100, -16, 1
        n_bytes = len(raw)
        n_samples = n_bytes // 2  # int16 = 2 bytes
        samples = list(struct.unpack(f"<{n_samples}h", raw))
        if mixer_channels and mixer_channels > 1:
            # Downmix to mono by averaging channels. (Mixer should be mono per
            # _open_mixer below, but this keeps us robust.)
            stride = mixer_channels
            samples = [sum(samples[i:i+stride]) // stride
                       for i in range(0, len(samples), stride)]
        return samples, mixer_freq

    def _resample(samples: "list[int]", rate: float) -> "list[int]":
        """Linear-interpolated resample. `rate` is the playback-speed ratio:
        rate > 1 reads faster (higher pitch, shorter), rate < 1 reads slower.

        For semitone shifts of +N, rate = 2 ** (N/12).
        """
        if abs(rate - 1.0) < 1e-9:
            return list(samples)
        n_in = len(samples)
        n_out = max(1, int(n_in / rate))
        out = [0] * n_out
        for i in range(n_out):
            src = i * rate
            j = int(src)
            frac = src - j
            if j + 1 < n_in:
                v = samples[j] + (samples[j + 1] - samples[j]) * frac
            else:
                v = samples[j] if j < n_in else 0
            # Clip to int16 range
            iv = int(v)
            if iv > 32767:
                iv = 32767
            elif iv < -32768:
                iv = -32768
            out[i] = iv
        return out

    def _make_pitch_variant(samples: "list[int]", semitones: float) -> pygame.mixer.Sound:
        rate = 2.0 ** (semitones / 12.0)
        shifted = _resample(samples, rate)
        # Pack back into int16 LE bytes and hand it to pygame.mixer.Sound.
        buf = struct.pack(f"<{len(shifted)}h", *shifted)
        return pygame.mixer.Sound(buffer=buf)

    # ── init / load ────────────────────────────────────────────────────────

    def _open_mixer() -> bool:
        if os.environ.get("SDL_AUDIODRIVER") == "dummy":
            return False
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)
            return True
        except Exception:
            return False

    def _load_sounds() -> None:
        global _mixer_ok
        try:
            for name in _SOUND_FILES:
                path = os.path.join(_SOUND_DIR, f"{name}.ogg")
                if os.path.exists(path):
                    _sounds[name] = pygame.mixer.Sound(file=path)
        except pygame.error:
            _sounds.clear()
            _mixer_ok = False

    def _build_pitch_variants() -> None:
        # flap: +/- 2 semitones in 1-semitone steps -> 5 variants.
        global _flap_variants, _combo_variants, _triple_variants
        flap_path = os.path.join(_SOUND_DIR, "flap.ogg")
        if os.path.exists(flap_path):
            samples, _ = _read_wav_bytes_from_ogg(flap_path)
            _flap_variants = [_make_pitch_variant(samples, n) for n in (-2, -1, 0, 1, 2)]

        for name, target_list in (("coin_combo", "_combo_variants"),
                                  ("coin_triple", "_triple_variants")):
            p = os.path.join(_SOUND_DIR, f"{name}.ogg")
            if not os.path.exists(p):
                continue
            samples, _ = _read_wav_bytes_from_ogg(p)
            # 0..12 semitones (one octave) — covers chain steps 1..13.
            variants = [_make_pitch_variant(samples, n) for n in range(0, 13)]
            globals()[target_list] = variants

    def init() -> None:
        global _mixer_ok
        _mixer_ok = _open_mixer()
        if _mixer_ok:
            _load_sounds()
            try:
                _build_pitch_variants()
            except Exception:
                # If the variant build fails (e.g. format mismatch on some
                # platform), fall back silently to the un-shifted base sounds.
                _flap_variants.clear()
                _combo_variants.clear()
                _triple_variants.clear()

    # ── voice limiter ──────────────────────────────────────────────────────

    def _can_play(name: str) -> "pygame.mixer.Channel | None":
        """Reserve a channel for `name`, capping concurrent playback. Returns
        a channel to play on (or None if no cap applies / no channel free)."""
        cap = _VOICE_CAPS.get(name)
        if cap is None:
            return None  # no cap for this event — caller plays normally
        live = [c for c in _channels.get(name, []) if c.get_busy()]
        if len(live) >= cap:
            # Stop the oldest so the newest play stays responsive.
            try:
                live[0].stop()
            except Exception:
                pass
            live = live[1:]
        _channels[name] = live
        ch = pygame.mixer.find_channel(True)  # forces a free channel
        return ch

    def _play_sound(name: str, sound: pygame.mixer.Sound, volume: float) -> None:
        if not _mixer_ok or sound is None:
            return
        ch = _can_play(name)
        if ch is None:
            ch = sound.play()
        else:
            ch.play(sound)
            _channels.setdefault(name, []).append(ch)
        if ch is not None:
            ch.set_volume(volume)

    # ── core dispatch ──────────────────────────────────────────────────────

    def _play(name: str, volume: float = 1.0) -> None:
        if not _mixer_ok:
            return
        s = _sounds.get(name)
        if s is None:
            return
        _play_sound(name, s, volume)


# ── Public API (identical on both backends) ─────────────────────────────────

def play_flap() -> None:
    if _IS_BROWSER:
        _play("flap", 0.55)
        return
    # Pitch-jitter ±2 semitones across 5 pre-rendered variants.
    if _flap_variants:
        _play_sound("flap", random.choice(_flap_variants), 0.55)
    else:
        _play("flap", 0.55)

def play_coin() -> None:
    _play("coin", 0.75)

def play_coin_combo(chain_step: int = 1) -> None:
    """Play the combo coin sound, optionally pitch-shifted up by one semitone
    per chain step (capped at +12 = one octave). chain_step=1 plays the
    neutral rendered file."""
    if _IS_BROWSER:
        _play("coin_combo", 0.80)
        return
    if not _mixer_ok:
        return
    if _combo_variants:
        idx = max(0, min(12, chain_step - 1))
        _play_sound("coin_combo", _combo_variants[idx], 0.80)
    else:
        _play("coin_combo", 0.80)

def play_coin_triple(chain_step: int = 1) -> None:
    """Like play_coin_combo but for the 3X-active triple chime."""
    if _IS_BROWSER:
        _play("coin_triple", 0.85)
        return
    if not _mixer_ok:
        return
    if _triple_variants:
        idx = max(0, min(12, chain_step - 1))
        _play_sound("coin_triple", _triple_variants[idx], 0.85)
    else:
        _play("coin_triple", 0.85)

def play_triple_coin() -> None: _play("triple_coin", 0.85)
def play_magnet() -> None:      _play("magnet", 0.75)
def play_slowmo() -> None:      _play("slowmo", 0.75)
def play_thunder() -> None:     _play("thunder", 0.85)
def play_death() -> None:       _play("death", 0.75)
def play_gameover() -> None:    _play("gameover", 0.70)
def play_poof() -> None:        _play("poof", 0.88)
def play_ghost() -> None:       _play("ghost", 0.70)
def play_grow() -> None:        _play("grow", 0.80)
