"""
Skybit audio: plays the curated CC0 OGG samples on both backends.

* Native (desktop / pygbag main thread):
    pygame.mixer.Sound(file=...) loads each OGG once at init() time and
    plays it via mixer channels. A small voice-limiter caps concurrent
    plays for the high-frequency events (coin / coin_triple / flap) at 2
    channels — keeps a 14-coin rush from muddying.

* Browser (pygbag / Pyodide / emscripten):
    Each play_X() call routes to JS window.skyPlay(name, volume), which
    is defined in inject_theme.py. The JS side fetches the same OGG
    files that inject_theme.py copies to build/web/sounds/ at build
    time, then plays them through Web Audio.

Both backends play the picked OGG at neutral pitch. The runtime
pitch-shift on triple chain length and the ±2-semitone flap jitter that
previously lived here were removed at the user's request — the climbing
pitch was uncomfortable.

Both backends degrade gracefully when the audio device can't be opened
(headless snapshots, missing JS helper, etc.) — every play_X call is a
silent no-op in that case.
"""
import os
import sys

import pygame


_IS_BROWSER = sys.platform == "emscripten"

_SOUND_DIR = os.path.join(os.path.dirname(__file__), "assets", "sounds")

_SOUND_FILES = (
    "flap", "coin", "coin_triple", "triple_coin",
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

    # Voice-limiting: per-event lists of currently-playing channels. Capped at
    # _VOICE_CAPS[name] concurrent channels; oldest is stopped to free a slot.
    _channels: "dict[str, list[pygame.mixer.Channel]]" = {}
    _VOICE_CAPS = {
        "flap":        2,
        "coin":        2,
        "coin_triple": 2,
    }

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

    def init() -> None:
        global _mixer_ok
        _mixer_ok = _open_mixer()
        if _mixer_ok:
            _load_sounds()

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
    _play("flap", 0.55)

def play_coin() -> None:
    _play("coin", 0.75)

def play_coin_triple() -> None:
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