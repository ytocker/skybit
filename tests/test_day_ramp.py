"""
Per-day difficulty ramp unit tests.

Skybit's biome cycle is a "day". Each completed day applies a one-shot
step on `SCROLL_BASE` (+8 px/s, cap 220) and `GAP_START` (-5 px,
floor 135). These tests pin the curve so a future refactor can't
silently drift the step / cap / floor.
"""
import os
import unittest

# The dummy SDL driver lets us instantiate World headlessly.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402
pygame.init()
pygame.display.set_mode((360, 640))

from game.world import World  # noqa: E402
from game.config import (   # noqa: E402
    SCROLL_BASE, GAP_START,
    DAY_SCROLL_STEP, DAY_SCROLL_CAP,
    DAY_GAP_STEP, DAY_GAP_FLOOR,
    RAMP_PIPES,
)


# (cycles_completed, expected_scroll_base, expected_gap)
DAY_RAMP_CURVE = (
    (0,  160.0, 170),
    (1,  168.0, 165),
    (2,  176.0, 160),
    (3,  184.0, 155),
    (5,  200.0, 145),
    (7,  216.0, 135),
    (8,  220.0, 135),
    (10, 220.0, 135),
    (20, 220.0, 135),
)


class DayRampTests(unittest.TestCase):
    def setUp(self):
        # Fresh World — neutralise the RAIL/SKATEBOARD/WEATHER multipliers
        # and the newbie-onboarding ramp so _current_scroll() / _current_gap()
        # return the unmodified post-day-ramp BASE (= regular endpoints
        # + day delta, no newbie lerp).
        self.world = World()
        self.world.bird.cart_locked = False
        self.world.slide_boost = 0.0
        self.world.biome_time = 80.0  # mid-day phase, no storm
        # _ramp_t = 1.0 once pillars_passed >= RAMP_PIPES.
        self.world.pillars_passed = RAMP_PIPES

    def test_curve_matches(self):
        for cycles, expect_scroll, expect_gap in DAY_RAMP_CURVE:
            with self.subTest(cycles=cycles):
                self.world.cycles_completed = cycles
                self.assertAlmostEqual(
                    self.world._current_scroll(), expect_scroll, places=2,
                    msg=f"scroll at day {cycles}")
                self.assertEqual(
                    self.world._current_gap(), expect_gap,
                    msg=f"gap at day {cycles}")

    def test_day_zero_is_baseline(self):
        self.world.cycles_completed = 0
        self.assertEqual(self.world._current_scroll(), SCROLL_BASE)
        self.assertEqual(self.world._current_gap(), GAP_START)

    def test_caps_lock_after_ceiling(self):
        # Each dial caps independently. Past day 8 nothing changes.
        self.world.cycles_completed = 100
        self.assertEqual(self.world._current_scroll(), DAY_SCROLL_CAP)
        self.assertEqual(self.world._current_gap(), DAY_GAP_FLOOR)

    def test_step_sizes(self):
        # Step values match the locked plan — drift here means the per-day
        # delta has been retuned without explicit intent.
        self.assertEqual(DAY_SCROLL_STEP, 8.0)
        self.assertEqual(DAY_GAP_STEP, 5)
        self.assertEqual(DAY_SCROLL_CAP, 220.0)
        self.assertEqual(DAY_GAP_FLOOR, 135)


if __name__ == "__main__":
    unittest.main()
