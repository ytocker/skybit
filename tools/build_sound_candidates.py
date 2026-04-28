#!/usr/bin/env python3
"""Build sound_candidates/ — ARCADE FUN palette.

Direction: wacky, punchy, dopaminergic. Mario/Sonic/NES energy. Sounds that
make a player smile. Bouncy synth blips, Mario-coin two-tones, triumphant
NES fanfares, goofy cartoon descents, comedic hit stings.
"""
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DST_ROOT = ROOT / "sound_candidates"

# Wipe existing event subfolders (keep README; we rewrite it after)
for child in DST_ROOT.iterdir():
    if child.is_dir():
        shutil.rmtree(child)

INT  = Path("/tmp/kenney-interface-sounds/addons/kenney_interface_sounds")
UI   = Path("/tmp/kenney-ui-audio/addons/kenney_ui_audio")
JING = Path("/tmp/kenney-music-jingles-for-godot/addons/kenney music jingles")
DIG  = Path("/tmp/kenney-digital-audio-for-godot/addons/kenney digital audio")
IMP  = Path("/tmp/kenney-impact-sounds-for-godot/addons/kenney impact sounds")

CANDIDATES = {
    "flap": [  # punchy goofy blip
        (1, DIG  / "pep_sound_1.ogg",                          "pep_1"),
        (2, DIG  / "pep_sound_3.ogg",                          "pep_3"),
        (3, DIG  / "zap_1.ogg",                                "zap_1"),
        (4, DIG  / "high_up.ogg",                              "high_up"),
        (5, INT  / "pluck_001.wav",                            "pluck_001"),
    ],
    "coin": [  # bouncy two-note Mario-coin chime
        (1, DIG  / "two_tone_1.ogg",                           "two_tone_1"),
        (2, DIG  / "two_tone_2.ogg",                           "two_tone_2"),
        (3, DIG  / "zap_two_tone.ogg",                         "zap_two_tone"),
        (4, DIG  / "zap_two_tone_2.ogg",                       "zap_two_tone_2"),
        (5, JING / "8-Bit jingles/jingles_nes_0.ogg",          "nes_0"),
    ],
    "coin_combo": [  # brighter, more excited
        (1, DIG  / "pep_sound_5.ogg",                          "pep_5"),
        (2, JING / "8-Bit jingles/jingles_nes_1.ogg",          "nes_1"),
        (3, JING / "8-Bit jingles/jingles_nes_2.ogg",          "nes_2"),
        (4, DIG  / "three_tone_1.ogg",                         "three_tone_1"),
        (5, DIG  / "zap_three_tone_up.ogg",                    "zap_three_tone_up"),
    ],
    "coin_triple": [  # triumphant cluster
        (1, JING / "8-Bit jingles/jingles_nes_3.ogg",          "nes_3"),
        (2, JING / "8-Bit jingles/jingles_nes_4.ogg",          "nes_4"),
        (3, JING / "8-Bit jingles/jingles_nes_5.ogg",          "nes_5"),
        (4, JING / "8-Bit jingles/jingles_nes_8.ogg",          "nes_8"),
        (5, DIG  / "three_tone_2.ogg",                         "three_tone_2"),
    ],
    "mushroom": [  # NES "got item!" fanfare
        (1, JING / "8-Bit jingles/jingles_nes_10.ogg",         "nes_10"),
        (2, JING / "8-Bit jingles/jingles_nes_11.ogg",         "nes_11"),
        (3, JING / "8-Bit jingles/jingles_nes_12.ogg",         "nes_12"),
        (4, JING / "8-Bit jingles/jingles_nes_13.ogg",         "nes_13"),
        (5, JING / "8-Bit jingles/jingles_nes_16.ogg",         "nes_16"),
    ],
    "magnet": [  # wacky vacuum-on charge
        (1, DIG  / "phaser_up_2.ogg",                          "phaser_up_2"),
        (2, DIG  / "phaser_up_4.ogg",                          "phaser_up_4"),
        (3, DIG  / "phaser_up_7.ogg",                          "phaser_up_7"),
        (4, DIG  / "power_up_5.ogg",                           "power_up_5"),
        (5, DIG  / "power_up_11.ogg",                          "power_up_11"),
    ],
    "slowmo": [  # cartoon "wahhh" descent
        (1, DIG  / "phaser_down_2.ogg",                        "phaser_down_2"),
        (2, DIG  / "phaser_down_3.ogg",                        "phaser_down_3"),
        (3, DIG  / "low_down.ogg",                             "low_down"),
        (4, DIG  / "phase_jump_4.ogg",                         "phase_jump_4"),
        (5, DIG  / "zap_three_tone_down.ogg",                  "zap_three_tone_down"),
    ],
    "poof": [  # silly cartoon puff/boing
        (1, DIG  / "pep_sound_2.ogg",                          "pep_2"),
        (2, DIG  / "pep_sound_4.ogg",                          "pep_4"),
        (3, DIG  / "zap_1.ogg",                                "zap_1"),
        (4, DIG  / "low_random.ogg",                           "low_random"),
        (5, DIG  / "phase_jump_2.ogg",                         "phase_jump_2"),
    ],
    "ghost": [  # wobbly "wooo" with personality
        (1, DIG  / "phase_jump_1.ogg",                         "phase_jump_1"),
        (2, DIG  / "phase_jump_3.ogg",                         "phase_jump_3"),
        (3, DIG  / "phase_jump_5.ogg",                         "phase_jump_5"),
        (4, DIG  / "space_trash_1.ogg",                        "space_trash_1"),
        (5, DIG  / "low_three_tone.ogg",                       "low_three_tone"),
    ],
    "grow": [  # comic balloon-inflating rise
        (1, DIG  / "power_up_3.ogg",                           "power_up_3"),
        (2, DIG  / "power_up_8.ogg",                           "power_up_8"),
        (3, DIG  / "power_up_9.ogg",                           "power_up_9"),
        (4, DIG  / "power_up_12.ogg",                          "power_up_12"),
        (5, DIG  / "phaser_up_3.ogg",                          "phaser_up_3"),
    ],
    "thunder": [  # synth low rumble
        (1, DIG  / "low_random.ogg",                           "low_random"),
        (2, DIG  / "low_down.ogg",                             "low_down"),
        (3, DIG  / "low_three_tone.ogg",                       "low_three_tone"),
        (4, DIG  / "space_trash_2.ogg",                        "space_trash_2"),
        (5, DIG  / "zap_2.ogg",                                "zap_2"),
    ],
    "death": [  # comic sad-trombone fail blip
        (1, JING / "Hit jingles/jingles_hit_0.ogg",            "hit_0"),
        (2, JING / "Hit jingles/jingles_hit_4.ogg",            "hit_4"),
        (3, JING / "Hit jingles/jingles_hit_8.ogg",            "hit_8"),
        (4, JING / "Hit jingles/jingles_hit_11.ogg",           "hit_11"),
        (5, JING / "Hit jingles/jingles_hit_16.ogg",           "hit_16"),
    ],
    "gameover": [  # NES sad-but-cute outro
        (1, JING / "8-Bit jingles/jingles_nes_5.ogg",          "nes_5"),
        (2, JING / "8-Bit jingles/jingles_nes_7.ogg",          "nes_7"),
        (3, JING / "8-Bit jingles/jingles_nes_14.ogg",         "nes_14"),
        (4, JING / "8-Bit jingles/jingles_nes_15.ogg",         "nes_15"),
        (5, JING / "8-Bit jingles/jingles_nes_16.ogg",         "nes_16"),
    ],
}


def normalize(src: Path, dst: Path) -> None:
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error", "-i", str(src),
        "-af", "silenceremove=start_periods=1:start_silence=0.05:start_threshold=-45dB,"
               "loudnorm=I=-16:LRA=11:TP=-1.5",
        "-c:a", "libvorbis", "-q:a", "4", "-ac", "1", "-ar", "44100",
        str(dst),
    ]
    subprocess.run(cmd, check=True)


total, missing = 0, []
for event, picks in CANDIDATES.items():
    out_dir = DST_ROOT / event
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n=== {event} ===")
    for rank, src, label in picks:
        if not src.exists():
            missing.append(str(src))
            print(f"  {rank}. MISSING: {src}")
            continue
        dst = out_dir / f"{rank}_{label}.ogg"
        normalize(src, dst)
        total += 1
        d = subprocess.check_output([
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", str(dst),
        ]).decode().strip()
        sz = dst.stat().st_size
        print(f"  {rank}. {label:22s} dur={float(d):4.2f}s  {sz} B")

print(f"\nTotal: {total} candidates staged.")
if missing:
    print("\nMissing sources:")
    for m in missing:
        print(f"  {m}")
