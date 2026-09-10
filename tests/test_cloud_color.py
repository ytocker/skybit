"""Cloud-color continuity tests.

The cloud body recipe used to switch between a warm and a cool mix at a hard
`sky_top` luminance threshold, which made cloud color SNAP at one point in the
day/night cycle. These tests pin the recipe as continuous across a dense phase
sweep — for both the live biome palette and the active Karst sky design — and
guard that the color helpers stay valid on a sky-only palette (no `mtn_far`).

Run with: ``python -m pytest tests/``.
"""
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import unittest

from game import biome as _biome
from game.biome_sky_keyframes import BIOMES
from game.cloud_variants import (
    _cloud_body_color, _ink_shadow_color, _lit_edge_color,
)

# Max allowed per-step channel jump over a fine phase sweep. A genuine
# discontinuity (the old hard threshold jumped ~60) stays ~60 at ANY step size,
# whereas a smooth crossfade shrinks with the step — so a fine step + tight
# bound discriminates a snap from a merely-steep transition.
_MAX_STEP_DELTA = 12
_STEP = 0.0005


def _max_adjacent_delta(palette_for_phase):
    prev = None
    worst = 0
    p = 0.0
    while p <= 1.0 + 1e-9:
        col = _cloud_body_color(palette_for_phase(p % 1.0))
        if prev is not None:
            worst = max(worst, max(abs(a - b) for a, b in zip(col, prev)))
        prev = col
        p += _STEP
    return worst


class CloudColorContinuityTest(unittest.TestCase):
    def test_body_continuous_live_biome(self):
        worst = _max_adjacent_delta(_biome.palette_for_phase)
        self.assertLessEqual(
            worst, _MAX_STEP_DELTA,
            f"cloud body color snaps on the live biome cycle (Δ={worst})")

    def test_body_continuous_karst(self):
        spec = BIOMES["karst_watertown"]
        worst = _max_adjacent_delta(spec.palette_for_phase)
        self.assertLessEqual(
            worst, _MAX_STEP_DELTA,
            f"cloud body color snaps on the Karst cycle (Δ={worst})")

    def test_helpers_accept_sky_only_palette(self):
        # The active design palette is sky-only (no mtn_far / mountain keys).
        sky_only = BIOMES["karst_watertown"].palette_for_phase(0.5)
        self.assertNotIn("mtn_far", sky_only)
        for fn in (_cloud_body_color, _ink_shadow_color, _lit_edge_color):
            col = fn(sky_only)
            self.assertEqual(len(col), 3)
            self.assertTrue(all(0 <= c <= 255 for c in col))


if __name__ == "__main__":
    unittest.main()
