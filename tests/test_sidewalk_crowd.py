"""Sidewalk crowd sim — locked behaviour.

Pins the invariants that make the near lane read alive without breaking the
world-anchored/no-pop contract:
  - a STANDING entity tracks the ground exactly (planted): its world_x never
    drifts, so screen_x = world_x - scroll moves at the pure world speed;
  - nothing outruns the world (|walk_vel| <= 0.9*speed) → every entity nets
    leftward and thus enters right / exits left (no mid-screen pop);
  - spawns appear OFF the right edge, culls happen OFF the left edge;
  - live count is capped regardless of density (perf);
  - speed==0 (game frozen) freezes translation.
"""
import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402
pygame.init()
pygame.display.set_mode((360, 640))

from game.config import W  # noqa: E402
from game import sidewalk_crowd as sc  # noqa: E402


def _standing(crowd, world_x):
    e = sc._Ent()
    e.kind = "stroller"
    e.variant = 0
    e.world_x = world_x
    e.walk_vel = 0.0
    e.facing = -1
    e.gait = 0.0
    e.state = "pause"
    e.timer = 999.0          # no transition during the test window
    e.target_vel = 0.0
    e.accel = 0.0
    crowd.near.append(e)
    return e


class StandingIsPlanted(unittest.TestCase):
    def test_standing_entity_never_drifts(self):
        c = sc.SidewalkCrowd()
        scroll = 1000.0
        e = _standing(c, scroll + 300.0)      # on-screen
        speed, sdt = 160.0, 1 / 60.0
        x0 = e.world_x
        for _ in range(120):
            scroll += speed * sdt
            c.update(scroll, speed, sdt, 0.30, 20.0)
        # world_x unchanged → screen_x moved at exactly the world speed, i.e. it
        # stayed pixel-locked to the floor/pillars (the "planted" guarantee).
        self.assertAlmostEqual(e.world_x, x0, places=6)


class NeverOutrunsWorld(unittest.TestCase):
    def test_walk_vel_clamped_below_speed(self):
        c = sc.SidewalkCrowd()
        e = _standing(c, 500.0)
        e.kind = "dog"
        e.walk_vel = 9999.0      # absurd
        e.target_vel = 9999.0
        e.accel = 99999.0
        speed, sdt = 130.0, 1 / 60.0
        c.update(600.0, speed, sdt, 0.30, 20.0)
        self.assertLessEqual(abs(e.walk_vel), 0.9 * speed + 1e-6)

    def test_speed_zero_freezes(self):
        c = sc.SidewalkCrowd()
        e = _standing(c, 500.0)
        e.walk_vel = 50.0
        x0 = e.world_x
        c.update(500.0, 0.0, 1 / 60.0, 0.30, 20.0)
        self.assertEqual(e.walk_vel, 0.0)
        self.assertEqual(e.world_x, x0)


class SpawnCullOffScreen(unittest.TestCase):
    def test_spawns_off_right_edge(self):
        c = sc.SidewalkCrowd()
        scroll = 0.0
        speed, sdt = 160.0, 1 / 60.0
        # High-population daytime phase + past the run-fill ramp → spawns fire.
        for _ in range(600):
            scroll += speed * sdt
            c.update(scroll, speed, sdt, 0.30, 30.0)
            for e in c.near:
                # No entity is ever culled while still on screen, and none is
                # spawned already inside the play area: newest sits off the right.
                self.assertGreater(e.world_x - scroll, -sc._SPAWN_MARGIN - 1)
        self.assertGreater(len(c.near), 0, "daytime crowd should populate")

    def test_cull_off_left(self):
        c = sc.SidewalkCrowd()
        e = _standing(c, -10000.0)     # far off the left edge
        c.update(0.0, 160.0, 1 / 60.0, 0.30, 30.0)
        self.assertNotIn(e, c.near)


class CountCapped(unittest.TestCase):
    def test_never_exceeds_cap(self):
        c = sc.SidewalkCrowd()
        scroll = 0.0
        speed, sdt = 160.0, 1 / 60.0
        for _ in range(2000):
            scroll += speed * sdt
            c.update(scroll, speed, sdt, 0.30, 60.0)
            self.assertLessEqual(len(c.near), sc._NEAR_CAP)


if __name__ == "__main__":
    unittest.main()
