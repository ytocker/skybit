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

    # ── Music bridge (calls skyMusic* defined in web.tmpl) ────────────────
    def _call_sky(name: str, *args) -> bool:
        """Call a window.skyMusic* helper. Returns True if dispatched."""
        try:
            import js  # type: ignore
            fn = getattr(js, name, None)
            if fn is not None:
                fn(*args)
                return True
        except Exception:
            pass
        try:
            import platform as _p
            fn = getattr(_p.window, name, None)
            if fn is not None:
                fn(*args)
                return True
        except Exception:
            pass
        return False

    def start_music() -> None:        _call_sky("skyMusicStart", 0.22)
    def pause_music() -> None:        _call_sky("skyMusicPause")
    def resume_music() -> None:       _call_sky("skyMusicResume")
    def stop_music(fadeout_ms: int = 800) -> None:
        _call_sky("skyMusicStop", fadeout_ms)


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

    # ── Background-music synthesis (Instant-Crush-inspired, original notes) ──

    def _midi_hz(m: int) -> float:
        return 440.0 * (2.0 ** ((m - 69) / 12.0))

    def _render_voice(dur_s: float, freq: float, shape: str, volume: float,
                      detune_cents: float = 0.0, attack_s: float = 0.02,
                      release_s: float = 0.10) -> list[int]:
        """Render one mono voice as a list[int16] (no wrapping/clipping here)."""
        n = int(dur_s * SAMPLE_RATE)
        f = freq * (2.0 ** (detune_cents / 1200.0))
        phase = 0.0
        buf = [0] * n
        for i in range(n):
            phase += f / SAMPLE_RATE
            env = _envelope(i, n, attack_s, release_s)
            buf[i] = int(_shape(shape, phase) * env * volume * 32767)
        return buf

    def _render_kick(dur_s: float, volume: float = 0.7) -> list[int]:
        """Fast 60→40 Hz sine sweep with snappy exponential amp decay."""
        n = int(dur_s * SAMPLE_RATE)
        phase = 0.0
        buf = [0] * n
        for i in range(n):
            t = i / max(1, n)
            f = 60.0 * math.exp(-3.0 * t) + 40.0
            phase += f / SAMPLE_RATE
            amp = math.exp(-6.0 * t) * volume
            buf[i] = int(math.sin(2 * math.pi * phase) * amp * 32767)
        return buf

    def _accumulate(target: list[int], source: list[int], start: int) -> None:
        """Add source into target starting at sample index `start` (safe, clamped)."""
        m = min(len(source), len(target) - start)
        if m <= 0:
            return
        for i in range(m):
            target[start + i] += source[i]

    # Warm lo-fi / ambient progression — extended jazz chords (7ths / 9ths).
    # Cmaj7 → Am9 → Fmaj7 → G7sus4. Each chord = 1 bar; progression cycles
    # 4× across the 16-bar loop, giving the 4 evolving sections room to grow.
    # (Reference: lo-fi chord research — Cmaj7 is "warm, slightly wistful,
    # unresolved"; Am9 sets a lush emotional tone; G7sus4 hangs on a
    # suspended fourth for a welcoming pull back to C.)
    _MUSIC_CHORDS = (
        (60, (0, 4, 7, 11),     "Cmaj7"),    # C E G B
        (57, (0, 3, 7, 10, 14), "Am9"),      # A C E G B
        (53, (0, 4, 7, 11),     "Fmaj7"),    # F A C E
        (55, (0, 5, 7, 10),     "G7sus4"),   # G C D F
    )
    # 4 sections of 4 bars each. Each boolean flags which layers are on.
    # A: pad only (gentle intro) → B: +arp (warming up) →
    # C: +soft kick + lead (full) → D: strip back to pad+arp (breath).
    _MUSIC_SECTIONS = (
        dict(sub=True, pad=True, arp=False, kick=False, lead=False),
        dict(sub=True, pad=True, arp=True,  kick=False, lead=False),
        dict(sub=True, pad=True, arp=True,  kick=True,  lead=True ),
        dict(sub=True, pad=True, arp=True,  kick=False, lead=False),
    )
    # Arpeggio index-into-chord-offsets pattern, 8 notes per bar (8th notes).
    # Pattern varies per section so ears get subtle evolution.
    _MUSIC_ARP_PATTERNS = (
        (0, 1, 2, 3, 2, 1, 0, 1),   # asc-desc
        (0, 2, 1, 3, 2, 0, 3, 1),   # zig-zag
        (0, 2, 3, 2, 1, 3, 2, 0),   # syncopated
        (0, 2, 1, 3, 0, 2, 1, 3),   # stepwise
    )
    _BPM = 78
    _BEAT_SEC = 60.0 / _BPM          # 0.769 s
    _BAR_SEC = _BEAT_SEC * 4         # 3.077 s
    _BARS_TOTAL = 16
    _BARS_PER_SECTION = 4

    _music_sound: "pygame.mixer.Sound | None" = None

    def _gen_music_loop() -> "pygame.mixer.Sound":
        total_sec = _BARS_TOTAL * _BAR_SEC
        n = int(total_sec * SAMPLE_RATE)
        mix = [0] * n
        for bar in range(_BARS_TOTAL):
            section = _MUSIC_SECTIONS[(bar // _BARS_PER_SECTION) % len(_MUSIC_SECTIONS)]
            root, offsets, _name = _MUSIC_CHORDS[bar % len(_MUSIC_CHORDS)]
            bar_start = bar * _BAR_SEC
            bar_i0 = int(bar_start * SAMPLE_RATE)
            # Sub-bass: deep sine root, slow attack, held whole bar.
            if section['sub']:
                v = _render_voice(_BAR_SEC * 0.95, _midi_hz(root - 12), "sine",
                                  0.19, attack_s=0.35, release_s=0.35)
                _accumulate(mix, v, bar_i0)
            # Pad: full extended chord (7ths/9ths), 2 detuned triangle voices each,
            # slow swell. Spans full bar.
            if section['pad']:
                for off in offsets:
                    for det in (-5, +5):
                        v = _render_voice(_BAR_SEC * 0.98, _midi_hz(root + off),
                                          "triangle", 0.045, detune_cents=det,
                                          attack_s=0.45, release_s=0.55)
                        _accumulate(mix, v, bar_i0)
            # Arpeggio: 8 eighth-notes per bar, patterns rotate per section.
            if section['arp']:
                pattern = _MUSIC_ARP_PATTERNS[(bar // _BARS_PER_SECTION) % len(_MUSIC_ARP_PATTERNS)]
                note_dur = _BEAT_SEC * 0.45
                for i in range(8):
                    idx = pattern[i] % len(offsets)
                    note = root + offsets[idx] + 12
                    t = bar_start + i * (_BEAT_SEC / 2)
                    v = _render_voice(note_dur, _midi_hz(note), "sine", 0.075,
                                      attack_s=0.006, release_s=0.12)
                    _accumulate(mix, v, int(t * SAMPLE_RATE))
            # Soft kick on beats 1 & 3 only in full section (not dance-y).
            if section['kick']:
                soft_kick = _render_kick(0.12, volume=0.45)
                for beat in (0, 2):
                    _accumulate(mix, soft_kick,
                                int((bar_start + beat * _BEAT_SEC) * SAMPLE_RATE))
            # Lead: 2 long pentatonic-ish notes per bar, detuned pair.
            if section['lead']:
                lead_degs = (0, 7, 11, 14, 7, 11, 0, 7)  # up + over the chord
                base = (bar % 4) * 2
                for i in range(2):
                    deg = lead_degs[(base + i) % len(lead_degs)]
                    t = bar_start + i * (_BAR_SEC / 2)
                    for det in (-4, +4):
                        v = _render_voice(_BAR_SEC * 0.48, _midi_hz(root + deg + 12),
                                          "sine", 0.085, detune_cents=det,
                                          attack_s=0.06, release_s=0.45)
                        _accumulate(mix, v, int(t * SAMPLE_RATE))
        # Clip to int16 and build WAV.
        for i in range(n):
            s = mix[i]
            if s > 32767: s = 32767
            elif s < -32768: s = -32768
            mix[i] = s
        return pygame.mixer.Sound(buffer=_wav_bytes(mix))


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

    _MUSIC_VOLUME = 0.22
    _MUSIC_CHANNEL_ID = 0
    _music_requested = False      # user wants music playing?
    _music_thread_started = False

    def _music_channel() -> "pygame.mixer.Channel | None":
        if not _mixer_ok:
            return None
        return pygame.mixer.Channel(_MUSIC_CHANNEL_ID)

    def _build_music_in_background() -> None:
        """Generate the loop in a daemon thread so the game boots instantly.
        When the Sound is ready, auto-start it if the user requested music."""
        global _music_sound, _music_thread_started
        if _music_thread_started:
            return
        _music_thread_started = True
        import threading
        def _worker():
            global _music_sound
            try:
                snd = _gen_music_loop()
            except Exception:
                return
            _music_sound = snd
            if _music_requested:
                _play_music_sound()
        threading.Thread(target=_worker, daemon=True).start()

    def _play_music_sound() -> None:
        if not _mixer_ok or _music_sound is None:
            return
        try:
            ch = _music_channel()
            if ch is None:
                return
            ch.stop()
            ch.play(_music_sound, loops=-1)
            ch.set_volume(_MUSIC_VOLUME)
        except pygame.error:
            pass

    def start_music() -> None:
        """(Re)start the background loop on the reserved channel. Non-blocking:
        the first call kicks off a background generator and this returns
        immediately; music fades in as soon as the loop is ready."""
        global _music_requested
        if not _mixer_ok:
            return
        _music_requested = True
        if _music_sound is None:
            _build_music_in_background()
        else:
            _play_music_sound()

    def pause_music() -> None:
        ch = _music_channel()
        if ch is not None:
            ch.pause()

    def resume_music() -> None:
        ch = _music_channel()
        if ch is not None:
            ch.unpause()

    def stop_music(fadeout_ms: int = 800) -> None:
        global _music_requested
        _music_requested = False
        ch = _music_channel()
        if ch is None:
            return
        if fadeout_ms > 0:
            ch.fadeout(fadeout_ms)
        else:
            ch.stop()
