"""Render every game sound to a WAV under /tmp/skybit_sounds/ for audible review.

Run from repo root:  python tools/render_sound_demo.py
"""
import os
import sys

os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame
pygame.init()

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

OUT_DIR = "/tmp/skybit_sounds"
os.makedirs(OUT_DIR, exist_ok=True)

import game.audio as audio

bank = audio._build_bank()
for name, payload in bank.items():
    items = payload if isinstance(payload, list) else [payload]
    for i, wav in enumerate(items):
        suffix = "" if len(items) == 1 else f"_v{i+1}"
        path = os.path.join(OUT_DIR, f"{name}{suffix}.wav")
        with open(path, "wb") as f:
            f.write(wav)
        n_samples = (len(wav) - 44) // 2
        print(f"  {name+suffix:14s}  {n_samples/22050*1000:>4.0f} ms  ->  {path}")

print(f"\nAll sounds written to {OUT_DIR}")
