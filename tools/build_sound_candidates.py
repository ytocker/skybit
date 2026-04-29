"""Stage candidate sound files for the v3 'Real Sounds, Smartly Sourced' plan.

Reads from the staged Kenney CC0 packs in /tmp/, lays out 5 candidates per
event in `sound_candidates_v3/<event>/`, and writes them through the same
ffmpeg normalisation pipeline used elsewhere in the project (silenceremove
+ loudnorm I=-16 + libvorbis q4 mono 44100).

Some candidates are *variant packs* (flap, coin): the file
becomes three nearby variants `1_label_a.ogg`, `1_label_b.ogg`, `1_label_c.ogg`
that the audio runtime later picks between at random. Other candidates can
be *layered* — multiple Kenney sources mixed together with per-source
gain (and a tiny stdlib-synthesised sweetener like a sub-bump or pad in
some places). All layering is done once at build time by ffmpeg's amix
filter; runtime cost stays zero.

Sonniss/Juhani slots from the original plan are not present (those
libraries aren't reachable from this build host); the spec falls back to
Kenney-only per the plan's own footnote — still a real upgrade over the
previous all-Kenney v2 because of multi-pack diversity, layering, and
variation.

Run:
    python tools/build_sound_candidates.py             # all events
    python tools/build_sound_candidates.py --only flap # one event
"""
import argparse
import array
import math
import pathlib
import random
import struct
import subprocess
import tempfile
import wave


# ── Paths ────────────────────────────────────────────────────────────────────

REPO    = pathlib.Path(__file__).parent.parent
OUT_DIR = REPO / "sound_candidates_v3"

DIG   = pathlib.Path("/tmp/kenney-digital-audio-for-godot/addons/kenney digital audio")
JING  = pathlib.Path("/tmp/kenney-music-jingles-for-godot/addons/kenney music jingles")
IMP   = pathlib.Path("/tmp/kenney-impact-sounds-for-godot/addons/kenney impact sounds")
IFACE = pathlib.Path("/tmp/kenney-interface-sounds")
UI    = pathlib.Path("/tmp/kenney-ui-audio")


# Hardcoded library roots — `find_file` rglob's from each one so subfolders
# (like "Music Jingles/8-Bit jingles/") are reached transparently.
DIG_ROOT   = pathlib.Path("/tmp/kenney-digital-audio-for-godot")
JING_ROOT  = pathlib.Path("/tmp/kenney-music-jingles-for-godot")
IMP_ROOT   = pathlib.Path("/tmp/kenney-impact-sounds-for-godot")
IFACE_ROOT = pathlib.Path("/tmp/kenney-interface-sounds")
UI_ROOT    = pathlib.Path("/tmp/kenney-ui-audio")
SCIFI_ROOT = pathlib.Path("/tmp/kenney-sci-fi-sounds-for-godot")


def find_file(root: pathlib.Path, name: str) -> pathlib.Path:
    """Find `name` (with or without extension) anywhere under `root`."""
    candidates = list(root.rglob(name)) + list(root.rglob(name + ".ogg")) + list(root.rglob(name + ".wav"))
    if not candidates:
        raise FileNotFoundError(f"no match for {name!r} under {root}")
    return candidates[0]


def D(name):  return find_file(DIG_ROOT,   name)   # Digital Audio
def J(name):  return find_file(JING_ROOT,  name)   # Music Jingles (NES + Hit etc.)
def Im(name): return find_file(IMP_ROOT,   name)   # Impact Sounds
def If(name): return find_file(IFACE_ROOT, name)   # Interface Sounds
def U(name):  return find_file(UI_ROOT,    name)   # UI Audio
def S(name):  return find_file(SCIFI_ROOT, name)   # Sci-fi Sounds (force_field, low_freq_explosion, etc.)


# ── Synth sweeteners (stdlib only; only ever mixed UNDER a real sample) ─────

SR     = 44100
TWO_PI = 2.0 * math.pi


def _synth_to_wav(samples, path):
    pcm = bytearray()
    for s in samples:
        v = max(-1.0, min(1.0, s))
        pcm.extend(struct.pack("<h", int(v * 32767)))
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(bytes(pcm))


def synth_sub_bump_60_80():
    """60 Hz sine, 80 ms, with a 30 ms fade-in for a soft 'thump' under
    a power-up jingle."""
    n = int(SR * 0.080)
    out = array.array("f", [0.0] * n)
    fade = int(SR * 0.030)
    for i in range(n):
        a = min(1.0, i / fade) if fade else 1.0
        out[i] = math.sin(TWO_PI * 60.0 * i / SR) * a
    return out


def synth_whistle_down_80():
    """Triangle 1200 → 400 Hz over 80 ms, AR envelope. Cartoon ricochet tail."""
    n = int(SR * 0.080)
    out = array.array("f", [0.0] * n)
    phase = 0.0
    for i in range(n):
        t = i / n
        f = 1200.0 + (400.0 - 1200.0) * t
        phase += TWO_PI * f / SR
        # triangle
        p = (phase / TWO_PI) % 1.0
        v = 4.0 * abs(p - 0.5) - 1.0
        env = min(1.0, i / 4) * max(0.0, (n - i) / max(1, n // 3))
        out[i] = v * env
    return out


def synth_noise_burst_1500():
    """Low-passed white noise (1.5 kHz cutoff), 80 ms, fast decay."""
    n = int(SR * 0.080)
    rc = 1.0 / (TWO_PI * 1500.0)
    dt = 1.0 / SR
    alpha = dt / (rc + dt)
    rng = random.Random(11)
    out = array.array("f", [0.0] * n)
    y = 0.0
    for i in range(n):
        x = rng.uniform(-1.0, 1.0)
        y = y + alpha * (x - y)
        env = min(1.0, i / 2) * max(0.0, (n - i) / n)
        out[i] = y * env
    return out


def synth_soft_pad_200():
    """Quiet triangle stack (3 voices: G3+B3+D4), 200 ms with a slow fade-in
    over the first half. Adds 'emotional weight' under a game-over jingle."""
    n = int(SR * 0.200)
    out = array.array("f", [0.0] * n)
    voices = [(196.0, 0.4), (247.0, 0.3), (294.0, 0.3)]
    for f, gain in voices:
        phase = 0.0
        for i in range(n):
            phase += TWO_PI * f / SR
            p = (phase / TWO_PI) % 1.0
            v = (4.0 * abs(p - 0.5) - 1.0) * gain
            t = i / n
            env = (t * 2.0) if t < 0.5 else 1.0   # half fade-in, then plateau
            out[i] += v * env
    return out


SYNTH_RECIPES = {
    "synth:sub_bump_60_80":     synth_sub_bump_60_80,
    "synth:whistle_down_80":    synth_whistle_down_80,
    "synth:noise_burst_1500hz": synth_noise_burst_1500,
    "synth:soft_pad_200":       synth_soft_pad_200,
}


# ── Candidate spec ───────────────────────────────────────────────────────────

# Each event maps to a list of `(slot, label, layers)` where:
#   - For variant_pack events (flap, coin) `layers` is a list of
#     three single-source paths — they render as `_a/_b/_c`.
#   - For all other events `layers` is a list of `(source, gain)` tuples.
#     One tuple = single-file copy+normalize. Multiple tuples = ffmpeg amix.
#
# `source` is either a Path (real file), or a "synth:<name>" sentinel that
# triggers the small stdlib generator above.

VARIANT_PACK_EVENTS = {"flap", "coin"}


def _spec():
    """Concept C 'Pop Mobile Hyper-Casual' candidate set — closest-fit
    substitution given the libraries actually reachable from the build host
    (Casino + Sonniss are unreachable). Each candidate is either a 3-tuple
    (slot, label, layers) or a 4-tuple (..., reverb) where reverb is
    'subtle' / 'heavy' / None — see REVERB_AF for the ffmpeg specs."""
    return {
        # Variant packs — 3 single-source files per slot, rendered as _a/_b/_c
        "flap": [
            (1, "iface_select_123", [If("select_001"), If("select_002"), If("select_003")]),
            (2, "iface_tick_124",   [If("tick_001"),   If("tick_002"),   If("tick_004")]),
            (3, "iface_drop_123",   [If("drop_001"),   If("drop_002"),   If("drop_003")]),
            (4, "ui_click_123",     [U("click1"),      U("click2"),      U("click3")]),
            (5, "iface_pluck_drop", [If("pluck_001"),  If("pluck_002"),  If("drop_004")]),
        ],
        "coin": [
            (1, "iface_confirm_123",  [If("confirmation_001"), If("confirmation_002"), If("confirmation_003")]),
            (2, "iface_glass_low",    [If("glass_001"), If("glass_002"), If("glass_003")]),
            (3, "iface_select_456",   [If("select_004"), If("select_005"), If("select_006")]),
            (4, "dig_two_three_tone", [D("two_tone_1"), D("two_tone_2"), D("three_tone_1")]),
            (5, "dig_zap_two_three",  [D("zap_two_tone"), D("zap_two_tone_2"), D("zap_three_tone_up")]),
        ],
        # Single-output events — Concept C spec adds reverb tails on the
        # high-stakes / "premium" candidates.
        "coin_triple": [
            (1, "iface_confirm4+ff0",   [(If("confirmation_004"), 1.0), (S("force_field_000"), 0.3)],   "subtle"),
            (2, "nes_3_accent",         [(J("jingles_nes_3"), 1.0)]),
            (3, "iface_glass4+up3",     [(If("glass_004"), 1.0), (D("phaser_up_3"), 0.4)],              "subtle"),
            (4, "scifi_force_field_1",  [(S("force_field_001"), 1.0)],                                  "subtle"),
            (5, "iface_confirm2+cn0",   [(If("confirmation_002"), 1.0), (S("computer_noise_000"), 0.3)],"subtle"),
        ],

        "triple_coin": [
            (1, "up3+confirm4+sub",     [(D("phaser_up_3"), 1.0), (If("confirmation_004"), 1.0), ("synth:sub_bump_60_80", 0.5)], "subtle"),
            (2, "pwr8+ff2",             [(D("power_up_8"), 1.0), (S("force_field_002"), 0.3)],          "subtle"),
            (3, "nes_11_accent",        [(J("jingles_nes_11"), 1.0)]),
            (4, "up5+confirm2+sub",     [(D("phaser_up_5"), 1.0), (If("confirmation_002"), 1.0), ("synth:sub_bump_60_80", 0.4)], "subtle"),
            (5, "power_up_3_solo",      [(D("power_up_3"), 1.0)],                                       "subtle"),
        ],

        "magnet": [
            (1, "phaser_up_2_solo",     [(D("phaser_up_2"), 1.0)]),
            (2, "phaser_up_4_solo",     [(D("phaser_up_4"), 1.0)]),
            (3, "up3+confirm4_lock",    [(D("phaser_up_3"), 1.0), (If("confirmation_004"), 0.4)]),
            (4, "power_up_5_solo",      [(D("power_up_5"), 1.0)]),
            (5, "up7+computer_noise1",  [(D("phaser_up_7"), 1.0), (S("computer_noise_001"), 0.3)]),
        ],

        "slowmo": [
            (1, "phaser_down_2_solo",   [(D("phaser_down_2"), 1.0)]),
            (2, "phaser_down_3_solo",   [(D("phaser_down_3"), 1.0)]),
            (3, "down3+computer_noise2",[(D("phaser_down_3"), 1.0), (S("computer_noise_002"), 0.3)]),
            (4, "low_down_solo",        [(D("low_down"), 1.0)]),
            (5, "down1+zap_down",       [(D("phaser_down_1"), 1.0), (D("zap_three_tone_down"), 0.4)]),
        ],

        "grow": [
            (1, "up3+wood_med0",        [(D("phaser_up_3"), 1.0), (Im("impact_wood_medium_000"), 0.5)]),
            (2, "power_up_8_solo",      [(D("power_up_8"), 1.0)]),
            (3, "ff3+wood_lt2",         [(S("force_field_003"), 1.0), (Im("impact_wood_light_002"), 0.4)]),
            (4, "pwr11+wood_med2",      [(D("power_up_11"), 1.0), (Im("impact_wood_medium_002"), 0.5)]),
            (5, "power_up_3_solo",      [(D("power_up_3"), 1.0)]),
        ],

        "ghost": [
            (1, "pj3+ff1_airy",         [(D("phase_jump_3"), 1.0), (S("force_field_001"), 0.3)],        "subtle"),
            (2, "phase_jump_5_solo",    [(D("phase_jump_5"), 1.0)],                                     "subtle"),
            (3, "phase_jump_1_solo",    [(D("phase_jump_1"), 1.0)],                                     "subtle"),
            (4, "scifi_force_field_4",  [(S("force_field_004"), 1.0)],                                  "subtle"),
            (5, "pj2+computer_noise0",  [(D("phase_jump_2"), 1.0), (S("computer_noise_000"), 0.3)],     "subtle"),
        ],

        "poof": [
            (1, "iface_select_001_solo",[(If("select_001"), 1.0)]),
            (2, "ui_click1_solo",       [(U("click1"), 1.0)]),
            (3, "impact_generic_lt_1",  [(Im("impact_generic_light_001"), 1.0)]),
            (4, "iface_drop_001_solo",  [(If("drop_001"), 1.0)]),
            (5, "select2+noise_burst",  [(If("select_002"), 1.0), ("synth:noise_burst_1500hz", 0.3)]),
        ],

        "thunder": [
            (1, "scifi_low_freq_exp_0", [(S("low_frequency_explosion_000"), 1.0)]),
            (2, "scifi_low_freq_exp_1", [(S("low_frequency_explosion_001"), 1.0)]),
            (3, "low_three_tone_solo",  [(D("low_three_tone"), 1.0)]),
            (4, "lfe0+low_random",      [(S("low_frequency_explosion_000"), 1.0), (D("low_random"), 0.4)]),
            (5, "low_random_solo",      [(D("low_random"), 1.0)]),
        ],

        "death": [
            (1, "wood_med2+whistle",    [(Im("impact_wood_medium_002"), 1.0), ("synth:whistle_down_80", 0.4)]),
            (2, "hit_4_accent",         [(J("jingles_hit_4"), 1.0)]),
            (3, "impact_generic_lt_3",  [(Im("impact_generic_light_003"), 1.0)]),
            (4, "error1+low_down",      [(If("error_001"), 1.0), (D("low_down"), 0.3)]),
            (5, "drop2+whistle_down",   [(If("drop_002"), 1.0), ("synth:whistle_down_80", 0.4)]),
        ],

        "gameover": [
            (1, "low3tone+pad_heavy",   [(D("low_three_tone"), 1.0), ("synth:soft_pad_200", 0.3)],      "heavy"),
            (2, "nes_15_accent",        [(J("jingles_nes_15"), 1.0)]),
            (3, "down3+pad",            [(D("phaser_down_3"), 1.0), ("synth:soft_pad_200", 0.3)],       "subtle"),
            (4, "ff2+pad",              [(S("force_field_002"), 1.0), ("synth:soft_pad_200", 0.3)],     "subtle"),
            (5, "nes5+pad",             [(J("jingles_nes_5"), 1.0), ("synth:soft_pad_200", 0.2)],       "subtle"),
        ],
    }


# ── Render pipeline ──────────────────────────────────────────────────────────

NORM_AF = ("silenceremove=start_periods=1:start_silence=0.005:start_threshold=-60dB,"
           "loudnorm=I=-16:LRA=11:tp=-1.5")

# Concept C reverb tails — applied (when the candidate spec asks) BEFORE the
# normalise chain so the reverb energy gets factored into loudnorm.
#   subtle  — single short tap, ~60 ms delay, light feedback
#   heavy   — two taps (60 + 150 ms), used only on the gameover pad layer
REVERB_AF = {
    "subtle": "aecho=0.7:0.7:60:0.3",
    "heavy":  "aecho=0.8:0.88:60|150:0.4|0.3",
}


def _af_chain(reverb):
    """Build the audio-filter chain string. `reverb` is None / 'subtle' / 'heavy'."""
    if reverb and reverb in REVERB_AF:
        return f"{REVERB_AF[reverb]},{NORM_AF}"
    return NORM_AF


def _materialise_synth(spec, tmpdir):
    """Resolve any 'synth:...' sentinels into real WAV files in tmpdir."""
    if isinstance(spec, pathlib.Path):
        return spec
    if isinstance(spec, tuple):
        path_or_sentinel, gain = spec
        return (_materialise_synth(path_or_sentinel, tmpdir), gain)
    if isinstance(spec, str) and spec.startswith("synth:"):
        recipe = SYNTH_RECIPES[spec]
        path = pathlib.Path(tmpdir) / f"{spec.split(':',1)[1]}.wav"
        if not path.exists():
            _synth_to_wav(recipe(), path)
        return path
    return spec


def render_single(src: pathlib.Path, gain: float, out: pathlib.Path, reverb=None):
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
           "-i", str(src),
           "-af", f"volume={gain},{_af_chain(reverb)}",
           "-ac", "1", "-ar", str(SR),
           "-c:a", "libvorbis", "-q:a", "4",
           str(out)]
    subprocess.run(cmd, check=True)


def render_layered(layers, out: pathlib.Path, reverb=None):
    """ffmpeg amix of N inputs with per-input volume + the standard normalise tail.
    Optional `reverb` adds an aecho stage before the normalise chain."""
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"]
    for src, _gain in layers:
        cmd += ["-i", str(src)]
    parts = []
    labels = []
    for i, (_src, gain) in enumerate(layers):
        parts.append(f"[{i}:a]volume={gain}[v{i}]")
        labels.append(f"[v{i}]")
    parts.append("".join(labels) + f"amix=inputs={len(layers)}:duration=first:dropout_transition=0[mix]")
    parts.append(f"[mix]{_af_chain(reverb)}[out]")
    cmd += ["-filter_complex", ";".join(parts),
            "-map", "[out]",
            "-ac", "1", "-ar", str(SR),
            "-c:a", "libvorbis", "-q:a", "4",
            str(out)]
    subprocess.run(cmd, check=True)


def render_event(name: str, candidates, tmpdir: pathlib.Path) -> int:
    """Each candidate is (slot, label, layers) or (slot, label, layers, reverb)."""
    out_dir = OUT_DIR / name
    out_dir.mkdir(parents=True, exist_ok=True)
    is_pack = name in VARIANT_PACK_EVENTS
    written = 0
    for cand in candidates:
        if len(cand) == 4:
            slot, label, layers, reverb = cand
        else:
            slot, label, layers = cand
            reverb = None
        if is_pack:
            for sub, src in zip("abc", layers):
                src = _materialise_synth(src, tmpdir)
                out = out_dir / f"{slot}_{label}_{sub}.ogg"
                render_single(src, 1.0, out, reverb=reverb)
                written += 1
        else:
            resolved = [_materialise_synth(L, tmpdir) for L in layers]
            out = out_dir / f"{slot}_{label}.ogg"
            if len(resolved) == 1:
                src, gain = resolved[0]
                render_single(src, gain, out, reverb=reverb)
            else:
                render_layered(resolved, out, reverb=reverb)
            written += 1
    return written


# ── Driver ───────────────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--only", nargs="*", metavar="EVENT")
    args = p.parse_args()

    spec = _spec()
    targets = args.only if args.only else list(spec)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="synth-sweet-") as tmpdir:
        for name in targets:
            if name not in spec:
                raise SystemExit(f"unknown event: {name!r}; choices: {sorted(spec)}")
            print(f"=== {name} ===")
            n = render_event(name, spec[name], pathlib.Path(tmpdir))
            print(f"  {n} candidate file(s) written to {OUT_DIR / name}/")

    # Drop a small README so the audition step is clear.
    readme = OUT_DIR / "README.md"
    readme.write_text(
        "# v3 sound candidates — audition pool\n\n"
        "Each subdirectory holds 5 candidates per event. For `flap` and `coin`\n"
        "each candidate is a 3-variant pack (`_a/_b/_c`) — pick the *family\n"
        "number* and you get the whole pack.\n\n"
        "Listen with `ffplay`, VLC, or any player. Reply with picks like\n"
        "`flap=2, coin=3, mushroom=1, ...`.\n",
        encoding="utf-8",
    )
    print("\nDone.")


if __name__ == "__main__":
    main()
