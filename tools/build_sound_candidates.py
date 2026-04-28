#!/usr/bin/env python3
"""Build the sound_candidates/ tree.

For each game event, copy 5 Kenney candidate sounds into
sound_candidates/<event>/, normalized to -16 LUFS and encoded as OGG.
Filenames are prefixed 1_..5_ so the user can quickly say "I want #3
for coin" and we know which file to use.
"""
import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DST_ROOT = ROOT / "sound_candidates"
DST_ROOT.mkdir(parents=True, exist_ok=True)

# Source pack roots
INT  = Path("/tmp/kenney-interface-sounds/addons/kenney_interface_sounds")
UI   = Path("/tmp/kenney-ui-audio/addons/kenney_ui_audio")
JING = Path("/tmp/kenney-music-jingles-for-godot/addons/kenney music jingles")
DIG  = Path("/tmp/kenney-digital-audio-for-godot/addons/kenney digital audio")
IMP  = Path("/tmp/kenney-impact-sounds-for-godot/addons/kenney impact sounds")
RPG  = Path("/tmp/kenney-rpg-audio-for-godot/addons/kenney rpg audio")

# Top-5 candidates per event. Each tuple = (rank, source_path, short_label).
CANDIDATES = {
    "flap": [
        (1, INT  / "click_001.wav",                                       "click_001"),
        (2, INT  / "click_005.wav",                                       "click_005"),
        (3, INT  / "tick_001.wav",                                        "tick_001"),
        (4, INT  / "pluck_001.wav",                                       "pluck_001"),
        (5, RPG  / "cloth_2.ogg",                                         "cloth_2"),
    ],
    "coin": [
        (1, JING / "Pizzicato jingles/jingles_pizzi_0.ogg",               "pizzi_0"),
        (2, JING / "Pizzicato jingles/jingles_pizzi_3.ogg",               "pizzi_3"),
        (3, JING / "Pizzicato jingles/jingles_pizzi_5.ogg",               "pizzi_5"),
        (4, JING / "Pizzicato jingles/jingles_pizzi_8.ogg",               "pizzi_8"),
        (5, JING / "Steel jingles/jingles_steel_0.ogg",                   "steel_0"),
    ],
    "coin_combo": [
        (1, JING / "Pizzicato jingles/jingles_pizzi_2.ogg",               "pizzi_2"),
        (2, JING / "Pizzicato jingles/jingles_pizzi_4.ogg",               "pizzi_4"),
        (3, JING / "Pizzicato jingles/jingles_pizzi_7.ogg",               "pizzi_7"),
        (4, JING / "Pizzicato jingles/jingles_pizzi_11.ogg",              "pizzi_11"),
        (5, JING / "Steel jingles/jingles_steel_5.ogg",                   "steel_5"),
    ],
    "coin_triple": [
        (1, JING / "Pizzicato jingles/jingles_pizzi_6.ogg",               "pizzi_6"),
        (2, JING / "Pizzicato jingles/jingles_pizzi_10.ogg",              "pizzi_10"),
        (3, JING / "Pizzicato jingles/jingles_pizzi_15.ogg",              "pizzi_15"),
        (4, JING / "Steel jingles/jingles_steel_3.ogg",                   "steel_3"),
        (5, JING / "Steel jingles/jingles_steel_15.ogg",                  "steel_15"),
    ],
    "mushroom": [
        (1, JING / "Pizzicato jingles/jingles_pizzi_12.ogg",              "pizzi_12"),
        (2, JING / "Pizzicato jingles/jingles_pizzi_15.ogg",              "pizzi_15"),
        (3, JING / "Steel jingles/jingles_steel_5.ogg",                   "steel_5"),
        (4, JING / "Steel jingles/jingles_steel_8.ogg",                   "steel_8"),
        (5, JING / "8-Bit jingles/jingles_nes_3.ogg",                     "nes_3"),
    ],
    "magnet": [
        (1, DIG  / "phaser_up_2.ogg",                                     "phaser_up_2"),
        (2, DIG  / "phaser_up_5.ogg",                                     "phaser_up_5"),
        (3, DIG  / "power_up_3.ogg",                                      "power_up_3"),
        (4, DIG  / "power_up_5.ogg",                                      "power_up_5"),
        (5, DIG  / "power_up_11.ogg",                                     "power_up_11"),
    ],
    "slowmo": [
        (1, DIG  / "phaser_down_2.ogg",                                   "phaser_down_2"),
        (2, DIG  / "phaser_down_3.ogg",                                   "phaser_down_3"),
        (3, DIG  / "low_down.ogg",                                        "low_down"),
        (4, DIG  / "phase_jump_4.ogg",                                    "phase_jump_4"),
        (5, JING / "Pizzicato jingles/jingles_pizzi_16.ogg",              "pizzi_16"),
    ],
    "poof": [
        (1, IMP  / "impact_wood_medium_000.ogg",                          "wood_medium_000"),
        (2, IMP  / "impact_wood_light_000.ogg",                           "wood_light_000"),
        (3, IMP  / "impact_soft_medium_001.ogg",                          "soft_medium_001"),
        (4, IMP  / "impact_plank_medium_002.ogg",                         "plank_medium_002"),
        (5, INT  / "pluck_002.wav",                                       "pluck_002"),
    ],
    "ghost": [
        (1, DIG  / "phase_jump_1.ogg",                                    "phase_jump_1"),
        (2, DIG  / "phase_jump_2.ogg",                                    "phase_jump_2"),
        (3, DIG  / "phaser_up_1.ogg",                                     "phaser_up_1"),
        (4, DIG  / "low_three_tone.ogg",                                  "low_three_tone"),
        (5, DIG  / "space_trash_1.ogg",                                   "space_trash_1"),
    ],
    "grow": [
        (1, DIG  / "power_up_3.ogg",                                      "power_up_3"),
        (2, DIG  / "power_up_4.ogg",                                      "power_up_4"),
        (3, DIG  / "power_up_8.ogg",                                      "power_up_8"),
        (4, DIG  / "power_up_11.ogg",                                     "power_up_11"),
        (5, DIG  / "phaser_up_3.ogg",                                     "phaser_up_3"),
    ],
    "thunder": [
        (1, DIG  / "low_random.ogg",                                      "low_random"),
        (2, DIG  / "low_three_tone.ogg",                                  "low_three_tone"),
        (3, DIG  / "low_down.ogg",                                        "low_down"),
        (4, DIG  / "space_trash_2.ogg",                                   "space_trash_2"),
        (5, DIG  / "space_trash_3.ogg",                                   "space_trash_3"),
    ],
    "death": [
        (1, IMP  / "impact_soft_heavy_002.ogg",                           "soft_heavy_002"),
        (2, IMP  / "impact_soft_medium_001.ogg",                          "soft_medium_001"),
        (3, IMP  / "impact_wood_heavy_003.ogg",                           "wood_heavy_003"),
        (4, JING / "Hit jingles/jingles_hit_0.ogg",                       "hit_0"),
        (5, JING / "Hit jingles/jingles_hit_8.ogg",                       "hit_8"),
    ],
    "gameover": [
        (1, JING / "8-Bit jingles/jingles_nes_15.ogg",                    "nes_15"),
        (2, JING / "8-Bit jingles/jingles_nes_5.ogg",                     "nes_5"),
        (3, JING / "8-Bit jingles/jingles_nes_10.ogg",                    "nes_10"),
        (4, JING / "Pizzicato jingles/jingles_pizzi_16.ogg",              "pizzi_16"),
        (5, JING / "Sax jingles/jingles_sax_15.ogg",                      "sax_15"),
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


total = 0
missing = []
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
        sz = dst.stat().st_size
        print(f"  {rank}. {label:20s} {sz:6d} B")

print(f"\nTotal: {total} candidates staged.")
if missing:
    print("\nMissing sources:")
    for m in missing:
        print(f"  {m}")
