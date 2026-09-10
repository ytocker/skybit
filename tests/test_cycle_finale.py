"""
Cycle-finale polish — locked behaviour.

Pins:
  - Treasure chest never lands in `world.powerups_picked` so the
    run-summary chip strip can never show a chest icon.
  - The chest's pickup hitbox tracks the FULL drawn sprite (~100 x 82
    px), not the small 34 px circle a regular power-up uses. Brushing
    the chest's outer corner picks it up.
  - Bunting / balloons / crowd spawn at the BIOME WRAP moment (not at
    chest-drop) but anchor their LEFT edge to the FIRST phantom rush
    pillar (one effective-spacing past the on-screen left flanker), so
    the whole celebration is off-screen at the wrap and SCROLLS IN from
    the right instead of popping onto the playfield. Predicted right
    endpoint still coincides with the future RIGHT real pillar within a
    frame's scroll tolerance.
"""
import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402
pygame.init()
pygame.display.set_mode((360, 640))

from game.world import World  # noqa: E402
from game.entities import PowerUp  # noqa: E402
from game.config import PIPE_W  # noqa: E402
from game.treasure_box import PICKUP_W, PICKUP_H  # noqa: E402


def _drop_chest(world, bx=180.0, by=320.0):
    chest = PowerUp(bx, by, kind="treasure")
    world.powerups.append(chest)
    return chest


class TreasureNotInSummary(unittest.TestCase):
    def test_powerups_picked_skips_treasure(self):
        w = World()
        chest = _drop_chest(w)
        # Drive the bird onto the chest centre — guaranteed pickup
        # whatever the collision model is.
        w.bird.x, w.bird.y = chest.x, chest.y
        w._check_pickups()
        self.assertTrue(chest.collected, "chest should be picked up")
        self.assertEqual(w.powerups_picked.get("treasure", 0), 0,
                         "treasure must not increment powerups_picked")


class ChestSpriteRectCollision(unittest.TestCase):
    """The chest is 100x82; circle test was ~34 px from centre.
    A horizontal offset of 48 px from centre is past the old circle
    but well inside the new sprite-rect."""

    def test_corner_brush_picks_up(self):
        w = World()
        chest = _drop_chest(w, bx=200.0, by=320.0)
        # 48 px right of chest centre — inside the 50 px half-width,
        # outside the 34 px collision circle.
        w.bird.x = chest.x + 48
        w.bird.y = chest.y
        w._check_pickups()
        self.assertTrue(chest.collected,
                        "corner-brush should pick up the chest under "
                        "the new sprite-rect hitbox")

    def test_far_miss_still_misses(self):
        w = World()
        chest = _drop_chest(w, bx=200.0, by=320.0)
        # Well outside the sprite rect — must not pick up.
        w.bird.x = chest.x + PICKUP_W
        w.bird.y = chest.y + PICKUP_H
        w._check_pickups()
        self.assertFalse(chest.collected,
                         "far miss must not pick up the chest")


class CelebrationSpawnAtWrap(unittest.TestCase):
    """Bunting + crowd + balloons spawn at biome WRAP, anchored to the
    FIRST phantom rush pillar (one effective-spacing past the left
    flanker) so they start off-screen and scroll in. Predicted right
    endpoint lands on the future RIGHT real pillar."""

    def _force_wrap(self, world):
        # Reproduce world.update's wrap-detect: previous phase past HI
        # then current phase past LO. The class's _last_biome_phase
        # snapshots last frame; pushing the biome_time forward so the
        # NEXT computed phase < LO triggers the rollover branch.
        from game.config import (
            CYCLE_FINALE_PHASE_HI, CYCLE_FINALE_PHASE_LO, RAMP_PIPES)
        # Bypass the newbie ramp so _current_spacing() returns
        # PIPE_SPACING (not PIPE_SPACING_NEWBIE) — keeps the bunting
        # geometry expectations pinned to the regular endpoints.
        world.pillars_passed = RAMP_PIPES
        world._last_biome_phase = CYCLE_FINALE_PHASE_HI + 0.01
        from game.biome import CYCLE_SECONDS
        # Phase = (biome_time / CYCLE_SECONDS) mod 1.0 -- nudge time
        # to a point where phase wraps to ~0.01 < LO.
        world.biome_time = CYCLE_SECONDS * 1.0 + 0.5
        # Sanity-check: the computed phase IS below LO.
        self.assertLess(world.biome_phase, CYCLE_FINALE_PHASE_LO,
                        "test fixture: phase didn't wrap below LO")
        # One update tick — wrap-detect fires inside world.update.
        world.ready_t = 0.0   # let biome_time tick
        world.bird.alive = True
        world.game_over = False
        world.update(1 / 60.0)

    def test_wrap_spawns_celebration_offscreen(self):
        from game.config import (
            CYCLE_FINALE_RUSH_PILLARS, CYCLE_FINALE_BOX_INDEX, PIPE_SPACING)
        # effective_spacing accounts for the W+60 spawn clamp (the spawn
        # site clamps each new pillar to world-x = W+60 the moment its
        # trigger fires, so the world-x gap between consecutive pillars
        # is spacing + 60, not the nominal spacing).
        effective_spacing = PIPE_SPACING + 60
        w = World()
        x = 800.0
        for _ in range(3):
            w._spawn_pipe(x)
            x += 280.0
        last_real = w.pipes[-1]
        flanker_x = last_real.x + PIPE_W * 0.5
        flanker_y = last_real.gap_y - last_real.gap_h * 0.5
        self._force_wrap(w)
        self.assertEqual(len(w.celebration_buntings), 1)
        self.assertEqual(len(w.celebration_balloon_clusters), 1)
        self.assertEqual(len(w.celebration_crowds), 1)
        bunting = w.celebration_buntings[-1]
        # Left endpoint sits on the FIRST phantom rush pillar — one
        # effective-spacing past the left flanker — so the decor starts
        # off the right screen edge and scrolls in (within one frame of
        # scroll, since wrap-detect runs INSIDE update after a tick of
        # scroll).
        self.assertAlmostEqual(bunting.x_left,
                               flanker_x + effective_spacing,
                               delta=20.0,
                               msg="bunting.x_left should sit on the first rush pillar")
        # y is unchanged (still the flanker's gap-top height; only x shifts).
        self.assertAlmostEqual(bunting.y_left, flanker_y, places=2)
        # Right endpoint = flanker + (RUSH_PILLARS + 1) * effective_spacing
        # (the future RIGHT real pillar); from the first rush pillar the
        # span is therefore RUSH_PILLARS * effective_spacing.
        expected_span = CYCLE_FINALE_RUSH_PILLARS * effective_spacing
        self.assertAlmostEqual(bunting.x_right - bunting.x_left,
                               expected_span, delta=1.0)
        # finish_x = flanker + (BOX_INDEX + 1) * effective_spacing
        #          = bunting.x_left + BOX_INDEX * effective_spacing.
        crowd = w.celebration_crowds[-1]
        expected_finish = bunting.x_left + CYCLE_FINALE_BOX_INDEX * effective_spacing
        # finish_x is appended verbatim to cluster_xs by the world, but this
        # expected value is recomputed via a differently-grouped (mathematically
        # equal) expression, so the two can differ by a few ULPs — match the
        # stripe within float tolerance rather than bit-exact.
        self.assertTrue(
            any(abs(cx - expected_finish) < 1e-6 for cx in crowd.cluster_xs),
            "one crowd cluster must sit on the predicted finish stripe")
        # All clusters fall within the [left, right] span.
        for cx in crowd.cluster_xs:
            self.assertGreaterEqual(cx, bunting.x_left - 0.001)
            self.assertLessEqual(cx, bunting.x_right + 0.001)

    def test_chest_lands_on_predicted_finish_x(self):
        """The chest spawn x at phantom #2 must match the finish_x the
        bunting predicted at wrap moment, within one frame of scroll.
        Prevents a future spacing-ramp tweak from silently desyncing
        the prediction."""
        w = World()
        x = 800.0
        for _ in range(3):
            w._spawn_pipe(x)
            x += 280.0
        self._force_wrap(w)
        from game.config import (
            CYCLE_FINALE_BOX_INDEX, PIPE_SPACING)
        effective_spacing = PIPE_SPACING + 60
        bunting = w.celebration_buntings[-1]
        # Step until the chest is spawned. Keep the bird alive +
        # away from pillars every frame so the update doesn't game-
        # over and stop spawning pillars.
        chest = None
        for _ in range(2000):
            w.bird.alive = True
            w.game_over = False
            w.bird.y = 320.0
            w.bird.vy = 0.0
            w.update(1 / 60.0)
            chest = next((m for m in w.powerups if m.kind == "treasure"),
                         None)
            if chest is not None:
                break
        self.assertIsNotNone(chest, "chest must spawn within 2000 frames")
        # Both bunting and chest scroll at the same world rate. The
        # bunting's left endpoint now sits on the FIRST rush pillar, so
        # the chest (BOX_INDEX phantoms further on) lands at
        # bunting.x_left + BOX_INDEX * effective_spacing at every frame
        # after chest spawn (one frame of scroll tolerance).
        predicted_finish_now = bunting.x_left + CYCLE_FINALE_BOX_INDEX * effective_spacing
        self.assertAlmostEqual(chest.x, predicted_finish_now, delta=20.0,
                               msg=(f"chest x {chest.x:.1f} should match "
                                    f"predicted finish {predicted_finish_now:.1f} "
                                    f"within one frame of scroll"))


if __name__ == "__main__":
    unittest.main()
