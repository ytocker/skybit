"""Integration confirmation — renders the LIVE `ALPINE_HAZE` biome (carrying the
signed-off evening of the day) over the real in-game mountains/pagodas/parrot,
straight from `game.biome_sky_keyframes`, NOT the study module. Confirms the port
into the live render path reads as the approved study row.

Output: docs/biome_redesign/alpine_haze_live_evening_ingame.png
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tools.preview_sky_alpine_ingame as P  # noqa: E402
from game.biome_sky_keyframes import ALPINE_HAZE  # noqa: E402

# Single live row instead of the 11 study concepts, and a dedicated output name.
P.CONCEPTS = [("alpine_haze (LIVE)", ALPINE_HAZE)]
_orig_join = os.path.join


def _patched_save(sheet, _out):
    out = _orig_join(P._ROOT, "docs", "biome_redesign",
                     "alpine_haze_live_evening_ingame.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    _real_save(sheet, out)
    print(f"wrote {out}  ({sheet.get_width()}x{sheet.get_height()})")


import pygame  # noqa: E402

_real_save = pygame.image.save
pygame.image.save = _patched_save

if __name__ == "__main__":
    P.main()
