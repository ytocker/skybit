"""Stage candidate sound files for the v3 'Real Sounds, Smartly Sourced' plan.

Reads from the staged Kenney CC0 packs in /tmp/, lays out 5 candidates per
event in `sound_candidates_v3/<event>/`, and writes them through the same
ffmpeg normalisation pipeline used elsewhere in the project (silenceremove
+ loudnorm I=-16 + libvorbis q4 mono 44100).

Some candidates are *variant packs* (flap, coin, coin_combo): the file
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
#   - For variant_pack events (flap, coin, coin_combo) `layers` is a list of
#     three single-source paths — they render as `_a/_b/_c`.
#   - For all other events `layers` is a list of `(source, gain)` tuples.
#     One tuple = single-file copy+normalize. Multiple tuples = ffmpeg amix.
#
# `source` is either a Path (real file), or a "synth:<name>" sentinel that
# triggers the small stdlib generator above.

VARIANT_PACK_EVENTS = {"flap", "coin", "coin_combo"}


def _spec():
    return {
        "flap": [
            (1, "pep_low_123",        [D("pep_sound_1"), D("pep_sound_2"), D("pep_sound_3")]),
            (2, "pep_mid_345",        [D("pep_sound_3"), D("pep_sound_4"), D("pep_sound_5")]),
            (3, "iface_pluck_drop",   [If("pluck_001"),  If("pluck_002"),  If("drop_004")]),
            (4, "iface_drop",         [If("drop_001"),   If("drop_002"),   If("drop_003")]),
            (5, "iface_click",        [If("click_001"),  If("click_002"),  If("click_003")]),
        ],
        "coin": [
            (1, "two_three_tone",     [D("two_tone_1"),  D("two_tone_2"),  D("three_tone_1")]),
            (2, "zap_two_three",      [D("zap_two_tone"), D("zap_two_tone_2"), D("zap_three_tone_up")]),
            (3, "nes_short_012",      [J("jingles_nes_0"), J("jingles_nes_1"), J("jingles_nes_2")]),
            (4, "iface_confirm",      [If("confirmation_001"), If("confirmation_002"), If("confirmation_003")]),
            (5, "iface_glass",        [If("glass_001"), If("glass_002"), If("glass_003")]),
        ],
        "coin_combo": [
            (1, "three_tone_pack",    [D("three_tone_1"), D("three_tone_2"), D("zap_three_tone_up")]),
            (2, "nes_phrases_123",    [J("jingles_nes_1"), J("jingles_nes_2"), J("jingles_nes_3")]),
            (3, "zap_ascending",      [D("zap_three_tone_up"), D("zap_two_tone"), D("zap_two_tone_2")]),
            (4, "switch_clean",       [U("switch1"), U("switch2"), U("switch3")]),
            (5, "phaser_brief",       [D("phaser_up_1"), D("phaser_up_2"), D("phaser_up_3")]),
        ],

        "coin_triple": [
            (1, "layered_nes3+pwr5",  [(J("jingles_nes_3"), 1.0), (D("power_up_5"), 0.4)]),
            (2, "nes_4_solo",         [(J("jingles_nes_4"), 1.0)]),
            (3, "nes_8_arpeggio",     [(J("jingles_nes_8"), 1.0)]),
            (4, "layered_nes5+up3",   [(J("jingles_nes_5"), 1.0), (D("phaser_up_3"), 0.3)]),
            (5, "nes_6_solo",         [(J("jingles_nes_6"), 1.0)]),
        ],

        "mushroom": [
            (1, "layered_nes10+up3+sub", [(J("jingles_nes_10"), 1.0),
                                           (D("phaser_up_3"),    0.3),
                                           ("synth:sub_bump_60_80", 0.5)]),
            (2, "nes_11_solo",         [(J("jingles_nes_11"), 1.0)]),
            (3, "layered_nes12+up5",   [(J("jingles_nes_12"), 1.0), (D("phaser_up_5"), 0.4)]),
            (4, "nes_13_solo",         [(J("jingles_nes_13"), 1.0)]),
            (5, "layered_nes14+pwr8",  [(J("jingles_nes_14"), 1.0), (D("power_up_8"), 0.3)]),
        ],

        "magnet": [
            (1, "phaser_up_2_solo",    [(D("phaser_up_2"), 1.0)]),
            (2, "power_up_5_solo",     [(D("power_up_5"), 1.0)]),
            (3, "layered_up4+pwr11",   [(D("phaser_up_4"), 1.0), (D("power_up_11"), 0.4)]),
            (4, "phaser_up_7_solo",    [(D("phaser_up_7"), 1.0)]),
            (5, "layered_up3+zap",     [(D("phaser_up_3"), 1.0), (D("zap_three_tone_up"), 0.5)]),
        ],

        "slowmo": [
            (1, "phaser_down_2_solo",  [(D("phaser_down_2"), 1.0)]),
            (2, "layered_down3+low",   [(D("phaser_down_3"), 1.0), (D("low_down"), 0.4)]),
            (3, "low_down_solo",       [(D("low_down"), 1.0)]),
            (4, "layered_down1+zap",   [(D("phaser_down_1"), 1.0), (D("zap_three_tone_down"), 0.4)]),
            (5, "zap_down_solo",       [(D("zap_three_tone_down"), 1.0)]),
        ],

        "grow": [
            (1, "layered_up3+wood_med",[(D("phaser_up_3"), 1.0), (Im("impact_wood_medium_000"), 0.5)]),
            (2, "power_up_8_solo",     [(D("power_up_8"), 1.0)]),
            (3, "power_up_3_solo",     [(D("power_up_3"), 1.0)]),
            (4, "layered_up5+wood_lt", [(D("phaser_up_5"), 1.0), (Im("impact_wood_light_002"), 0.4)]),
            (5, "layered_pwr11+wood",  [(D("power_up_11"), 1.0), (Im("impact_wood_medium_002"), 0.5)]),
        ],

        "ghost": [
            (1, "phase_jump_1_solo",   [(D("phase_jump_1"), 1.0)]),
            (2, "phase_jump_3_solo",   [(D("phase_jump_3"), 1.0)]),
            (3, "phase_jump_5_solo",   [(D("phase_jump_5"), 1.0)]),
            (4, "layered_pj5+space",   [(D("phase_jump_5"), 1.0), (D("space_trash_1"), 0.3)]),
            (5, "layered_pj2+lowtone", [(D("phase_jump_2"), 1.0), (D("low_three_tone"), 0.3)]),
        ],

        "poof": [
            (1, "wood_light_002_solo", [(Im("impact_wood_light_002"), 1.0)]),
            (2, "generic_lt_001_solo", [(Im("impact_generic_light_001"), 1.0)]),
            (3, "layered_pep2+noise",  [(D("pep_sound_2"), 1.0), ("synth:noise_burst_1500hz", 0.3)]),
            (4, "low_random_solo",     [(D("low_random"), 1.0)]),
            (5, "layered_pj2+wood",    [(D("phase_jump_2"), 1.0), (Im("impact_generic_light_002"), 0.4)]),
        ],

        "thunder": [
            (1, "low_three_tone_solo", [(D("low_three_tone"), 1.0)]),
            (2, "layered_low_random",  [(D("low_random"), 1.0), (D("low_down"), 0.5)]),
            (3, "low_down_solo",       [(D("low_down"), 1.0)]),
            (4, "layered_low3+space",  [(D("low_three_tone"), 1.0), (D("space_trash_2"), 0.4)]),
            (5, "space_trash_3_solo",  [(D("space_trash_3"), 1.0)]),
        ],

        "death": [
            (1, "layered_hit0+whistle",[(J("jingles_hit_0"), 1.0), ("synth:whistle_down_80", 0.3)]),
            (2, "hit_4_solo",          [(J("jingles_hit_4"), 1.0)]),
            (3, "hit_8_solo",          [(J("jingles_hit_8"), 1.0)]),
            (4, "layered_hit11+low",   [(J("jingles_hit_11"), 1.0), (D("low_down"), 0.3)]),
            (5, "hit_13_solo",         [(J("jingles_hit_13"), 1.0)]),
        ],

        "gameover": [
            (1, "layered_nes15+pad",   [(J("jingles_nes_15"), 1.0), ("synth:soft_pad_200", 0.2)]),
            (2, "nes_5_solo",          [(J("jingles_nes_5"), 1.0)]),
            (3, "nes_7_solo",          [(J("jingles_nes_7"), 1.0)]),
            (4, "layered_nes14+pwr7",  [(J("jingles_nes_14"), 1.0), (D("power_up_7"), 0.3)]),
            (5, "nes_9_solo",          [(J("jingles_nes_9"), 1.0)]),
        ],
    }


# ── Render pipeline ──────────────────────────────────────────────────────────

NORM_AF = ("silenceremove=start_periods=1:start_silence=0.005:start_threshold=-60dB,"
           "loudnorm=I=-16:LRA=11:tp=-1.5")


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


def render_single(src: pathlib.Path, gain: float, out: pathlib.Path):
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
           "-i", str(src),
           "-af", f"volume={gain},{NORM_AF}",
           "-ac", "1", "-ar", str(SR),
           "-c:a", "libvorbis", "-q:a", "4",
           str(out)]
    subprocess.run(cmd, check=True)


def render_layered(layers, out: pathlib.Path):
    """ffmpeg amix of N inputs with per-input volume + the standard normalise tail."""
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"]
    for src, _gain in layers:
        cmd += ["-i", str(src)]
    parts = []
    labels = []
    for i, (_src, gain) in enumerate(layers):
        parts.append(f"[{i}:a]volume={gain}[v{i}]")
        labels.append(f"[v{i}]")
    parts.append("".join(labels) + f"amix=inputs={len(layers)}:duration=longest:dropout_transition=0[mix]")
    parts.append(f"[mix]{NORM_AF}[out]")
    cmd += ["-filter_complex", ";".join(parts),
            "-map", "[out]",
            "-ac", "1", "-ar", str(SR),
            "-c:a", "libvorbis", "-q:a", "4",
            str(out)]
    subprocess.run(cmd, check=True)


def render_event(name: str, candidates, tmpdir: pathlib.Path) -> int:
    out_dir = OUT_DIR / name
    out_dir.mkdir(parents=True, exist_ok=True)
    is_pack = name in VARIANT_PACK_EVENTS
    written = 0
    for slot, label, layers in candidates:
        if is_pack:
            for sub, src in zip("abc", layers):
                src = _materialise_synth(src, tmpdir)
                out = out_dir / f"{slot}_{label}_{sub}.ogg"
                render_single(src, 1.0, out)
                written += 1
        else:
            resolved = [_materialise_synth(L, tmpdir) for L in layers]
            out = out_dir / f"{slot}_{label}.ogg"
            if len(resolved) == 1:
                src, gain = resolved[0]
                render_single(src, gain, out)
            else:
                render_layered(resolved, out)
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
        "Each subdirectory holds 5 candidates per event. For `flap`, `coin`,\n"
        "and `coin_combo` each candidate is a 3-variant pack (`_a/_b/_c`) — pick\n"
        "the *family number* and you get the whole pack.\n\n"
        "Listen with `ffplay`, VLC, or any player. Reply with picks like\n"
        "`flap=2, coin=3, mushroom=1, ...`.\n",
        encoding="utf-8",
    )
    print("\nDone.")


if __name__ == "__main__":
    main()
