"""Copy the 13 bundled game sounds to /tmp/skybit_sounds/ for audible review.

Run from repo root:  python tools/render_sound_demo.py

The actual sound files live under game/assets/sounds/ as CC0 OGGs sourced
from Kenney.nl. This script just mirrors them to /tmp for quick auditing.
"""
import os
import shutil

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "game", "assets", "sounds")
DST = "/tmp/skybit_sounds"

os.makedirs(DST, exist_ok=True)
n = 0
for fn in sorted(os.listdir(SRC)):
    if fn.endswith(".ogg"):
        shutil.copy(os.path.join(SRC, fn), os.path.join(DST, fn))
        sz = os.path.getsize(os.path.join(SRC, fn))
        print(f"  {fn:18s} {sz:6d} B")
        n += 1
print(f"\n{n} sounds copied to {DST}")
