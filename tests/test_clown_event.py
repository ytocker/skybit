"""
Clown event — locked behaviour.

Pins:
  - The event fires once per biome day, when the phase crosses the clown
    anchor (CLOWN_EVENT_PHASE = the phase of CLOWN_START_PILLAR), and re-arms
    on the cycle wrap so it recurs every day.
  - The reserved slot is always CLOWN_SLOT_PILLARS wide regardless of the
    rolled gauntlet length N: the first N pillars are warren towers
    (is_staff, at the fused CLOWN_WARREN_SPACING), the remaining N..slot are
    regular gameplay, and coin rush is suppressed across the whole slot — so
    downstream pillar numbering stays deterministic.
"""
import os
import random
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402
pygame.init()
pygame.display.set_mode((360, 640))

from game.world import World, CLOWN_EVENT_PHASE, CLOWN_PRECLEAR_PHASE  # noqa: E402
from game.clown_routes import build_clown_route  # noqa: E402
from game.config import (  # noqa: E402
    CLOWN_SLOT_PILLARS, CLOWN_WARREN_SPACING, CLOWN_ROLL_MIN, CLOWN_ROLL_MAX,
    CLOWN_PRECLEAR_PILLARS, CLOWN_LEADIN_PILLARS, CLOWN_OUTRO_PILLARS)
from game.biome import CYCLE_SECONDS  # noqa: E402


class SlotReservation(unittest.TestCase):
    def _lay_slot(self, n):
        """Lay the reserved slot by hand: drive _spawn_pipe directly with the
        slot pre-armed (no lead-in here — that's armed at the live trigger).
        Loops past the slot width by CLOWN_OUTRO_PILLARS, since the outro
        empties (armed on the last warren tower) take spawn slots WITHOUT
        draining the reserved count."""
        w = World()
        w._clown_route = build_clown_route(n, random.Random(0))
        w._clown_slot_remaining = CLOWN_SLOT_PILLARS
        rows = []  # (is_staff, is_phantom, is_rush, spacing-for-this-pillar)
        x = 500.0
        for _ in range(CLOWN_SLOT_PILLARS + CLOWN_OUTRO_PILLARS):
            sp = w._next_spacing()
            w._spawn_pipe(x)
            p = w.pipes[-1]
            rows.append((getattr(p, "is_staff", False), p.is_phantom,
                         getattr(p, "is_rush", False), sp))
            x += sp
        return w, rows

    def test_short_roll_fills_to_slot_width(self):
        n = 14
        w, rows = self._lay_slot(n)
        staff = [s for s, _ph, _r, _sp in rows]
        phantom = [ph for _s, ph, _r, _sp in rows]
        # n warren towers, then the outro empties, then the regular-fill tail
        # padding the warren run to the fixed slot width.
        self.assertEqual(sum(staff), n)
        self.assertEqual(staff[:n], [True] * n, "first N pillars are warren")
        self.assertEqual(phantom[n:n + CLOWN_OUTRO_PILLARS],
                         [True] * CLOWN_OUTRO_PILLARS,
                         "outro empties immediately follow the gauntlet")
        fill = rows[n + CLOWN_OUTRO_PILLARS:]
        self.assertEqual(len(fill), CLOWN_SLOT_PILLARS - n,
                         "fill pads the warren run to the fixed slot width")
        self.assertTrue(all(not s and not ph for s, ph, _r, _sp in fill),
                        "fill pillars are normal (not warren, not phantom)")
        self.assertEqual(w._clown_slot_remaining, 0, "slot fully consumed")

    def test_warren_uses_fused_spacing(self):
        n = 12
        _w, rows = self._lay_slot(n)
        self.assertTrue(all(sp == CLOWN_WARREN_SPACING
                            for _s, _ph, _r, sp in rows[:n]),
                        "warren pillars sit at the fused spacing")
        self.assertTrue(all(sp != CLOWN_WARREN_SPACING
                            for _s, _ph, _r, sp in rows[n:]),
                        "outro empties + regular fill use the normal spacing")

    def test_warren_on_screen_spacing_is_not_inflated(self):
        """Drive the real update() spawn loop (not the manual _lay_slot lay-out)
        and assert adjacent warren towers actually land ~CLOWN_WARREN_SPACING
        apart on screen. The normal-pillar spawn path clamps the entry x to
        W+60, which silently added ~60px to every gap (72 -> ~133px); warren
        towers must bypass that clamp."""
        from game.entities import Pipe
        orig = Pipe.collides_circle
        Pipe.collides_circle = lambda *a, **k: False  # never die → spawns flow
        try:
            w = World()
            w.ready_t = 0.0
            w.flap()
            w._clown_route = build_clown_route(CLOWN_ROLL_MAX, random.Random(0))
            w._clown_slot_remaining = CLOWN_SLOT_PILLARS
            gaps = set()
            for _ in range(60 * 20):
                w.bird.y = 300.0       # pin so no ground/ceiling death
                w.bird.vy = 0.0
                w.update(1 / 60.0)
                xs = sorted(p.x for p in w.pipes
                            if getattr(p, "is_staff", False))
                for a, b in zip(xs, xs[1:]):
                    gaps.add(round(b - a))
        finally:
            Pipe.collides_circle = orig
        self.assertTrue(gaps, "warren towers should have spawned")
        self.assertTrue(
            all(abs(g - CLOWN_WARREN_SPACING) <= 3 for g in gaps),
            f"warren on-screen spacing must be ~{CLOWN_WARREN_SPACING}px "
            f"(not the +60 clamped gap), got {sorted(gaps)}")

    def test_coin_rush_suppressed_in_slot(self):
        _w, rows = self._lay_slot(CLOWN_ROLL_MAX)
        self.assertFalse(any(r for _s, _ph, r, _sp in rows),
                         "no coin rush anywhere inside the clown slot")

    def test_full_roll_is_all_warren(self):
        n = CLOWN_ROLL_MAX
        _w, rows = self._lay_slot(n)
        staff = [s for s, _ph, _r, _sp in rows]
        self.assertEqual(sum(staff), n,
                         "a max roll fills the slot entirely with warren towers")
        self.assertTrue(all(staff[:n]), "first N (= slot width) are all warren")
        # The only trailing pillars are the outro empties.
        self.assertTrue(all(ph for _s, ph, _r, _sp in rows[n:]),
                        "the only pillars after the gauntlet are outro empties")

    def test_relief_empties_bracket_the_gauntlet(self):
        """Drive the live event end-to-end and assert the gauntlet is bracketed
        by exactly CLOWN_LEADIN_PILLARS empty (phantom) pillars before the first
        staff tower and CLOWN_OUTRO_PILLARS after the last — HIDING existing
        pillars (the gauntlet keeps its full length), not adding any. Phantoms
        never score."""
        from game.entities import Pipe
        from game.clown_event import ClownEvent
        orig_collide = Pipe.collides_circle
        orig_spawn = World._spawn_pipe
        Pipe.collides_circle = lambda *a, **k: False  # never die → spawns flow
        # Record the spawn-ORDERED type from inside _spawn_pipe — tracking pipes
        # by id() in self.pipes undercounts, since CPython reuses an id once a
        # culled pipe is freed.
        seq = []  # "staff" / "phantom" / "normal"

        def _hook(self, x):
            n0 = len(self.pipes)
            orig_spawn(self, x)
            if len(self.pipes) > n0:
                p = self.pipes[-1]
                seq.append("staff" if getattr(p, "is_staff", False)
                           else ("phantom" if p.is_phantom else "normal"))
        World._spawn_pipe = _hook
        try:
            w = World()
            w.ready_t = 0.0
            w.bird.alive = True
            w.game_over = False
            w.pillars_passed = 40          # past the newbie ramp → full scroll
            w.flap()
            # Reserve a full gauntlet via the real reveal path + arm the lead-in
            # exactly as the live trigger does.
            ev = ClownEvent()
            w.clown_event = ev
            ev.collected = True
            ev.ghost_run = False
            ev.roll = CLOWN_ROLL_MAX
            ev.spin_t = 0.0
            ev.phase = "rolling"
            ev._reveal(w)
            w._clown_leadin_remaining = CLOWN_LEADIN_PILLARS
            for _ in range(60 * 40):
                w.bird.y = 300.0
                w.bird.vy = 0.0
                w.update(1 / 60.0)
                # Phantoms must never score (the relief slots are "not there").
                self.assertFalse(any(p.is_phantom and p.scored for p in w.pipes),
                                 "a relief empty must never award a point")
        finally:
            Pipe.collides_circle = orig_collide
            World._spawn_pipe = orig_spawn
        staff = [i for i, t in enumerate(seq) if t == "staff"]
        self.assertEqual(len(staff), CLOWN_ROLL_MAX,
                         "the full gauntlet still spawns (length not capped)")
        first, last = staff[0], staff[-1]
        lead = 0
        for t in reversed(seq[:first]):
            if t == "phantom":
                lead += 1
            else:
                break
        out = 0
        for t in seq[last + 1:]:
            if t == "phantom":
                out += 1
            else:
                break
        self.assertEqual(lead, CLOWN_LEADIN_PILLARS,
                         "lead-in empties immediately precede the gauntlet")
        self.assertEqual(out, CLOWN_OUTRO_PILLARS,
                         "outro empties immediately follow the gauntlet")


class PreClear(unittest.TestCase):
    """The clown enters a CLEAN sky: CLOWN_PRECLEAR_PILLARS phantom empties are
    laid BEFORE the ClownEvent controller exists, and the beat then stays clear
    (phantom) through the die roll until the reveal."""

    def test_preclear_precedes_the_clown_creation(self):
        from game.clown_event import ClownEvent
        w = World()
        w.pillars_passed = 40  # past the ramp → full scroll
        w._clown_preclear_remaining = CLOWN_PRECLEAR_PILLARS
        w._clown_entrance_pending = True
        x = 500.0
        for _ in range(CLOWN_PRECLEAR_PILLARS):
            # The clown must not exist until the last pre-clear empty is laid, so
            # it never shares the sky with the real pillars still in flight.
            self.assertIsNone(w.clown_event,
                              "clown appears only after the pre-clear empties")
            sp = w._next_spacing()
            w._spawn_pipe(x)
            x += sp
            p = w.pipes[-1]
            self.assertTrue(p.is_phantom, "pre-clear pillars are phantom empties")
            self.assertFalse(getattr(p, "is_staff", False))
        self.assertEqual(w._clown_preclear_remaining, 0)
        self.assertIsInstance(w.clown_event, ClownEvent,
                              "clown enters right after the last pre-clear empty")

    def test_beat_stays_clear_until_reveal(self):
        from game.clown_event import ClownEvent
        w = World()
        w.pillars_passed = 40
        ev = ClownEvent()
        w.clown_event = ev
        x = 500.0
        for phase in ("enter", "rolling"):
            ev.phase = phase
            w._spawn_pipe(x)
            x += w._next_spacing()
            self.assertTrue(w.pipes[-1].is_phantom,
                            f"sky stays clear during the '{phase}' phase")


class Trigger(unittest.TestCase):
    def _arm_just_before_anchor(self, w):
        w.ready_t = 0.0
        w.bird.alive = True
        w.game_over = False
        w._clown_fired_this_cycle = False
        w._clown_slot_remaining = 0
        # Park phase a hair before the PRE-CLEAR anchor (the clear-sky begins a
        # few pillars ahead of the clown); push biome_time a hair past it so the
        # crossing fires inside this update tick.
        w._last_biome_phase = CLOWN_PRECLEAR_PHASE - 0.005
        w.biome_time = (CLOWN_PRECLEAR_PHASE + 0.002) * CYCLE_SECONDS

    def test_fires_once_at_anchor(self):
        w = World()
        self._arm_just_before_anchor(w)
        w.update(1 / 60.0)
        # Crossing the pre-clear anchor arms the clear-sky runway + flags the
        # pending entrance. The clown controller is created later, once the
        # pre-clear empties are laid (see PreClear); the slot is reserved later
        # still, on the die roll (see Pickup tests).
        self.assertTrue(w._clown_fired_this_cycle)
        self.assertEqual(w._clown_preclear_remaining, CLOWN_PRECLEAR_PILLARS,
                         "crossing the anchor arms the pre-clear empties")
        self.assertTrue(w._clown_entrance_pending)
        self.assertIsNone(w.clown_event,
                          "clown is created after the pre-clear, not at the trigger")
        self.assertEqual(w._clown_slot_remaining, 0)

    def test_does_not_refire_same_day(self):
        w = World()
        self._arm_just_before_anchor(w)
        w.update(1 / 60.0)
        self.assertTrue(w._clown_fired_this_cycle)
        # Disarm the pending entrance and keep advancing within the same day: must
        # not re-arm until a cycle wrap re-sets the flag.
        w._clown_preclear_remaining = 0
        w._clown_entrance_pending = False
        w.clown_event = None
        w._last_biome_phase = CLOWN_PRECLEAR_PHASE - 0.005
        w.biome_time = (CLOWN_PRECLEAR_PHASE + 0.002) * CYCLE_SECONDS
        w.update(1 / 60.0)
        self.assertEqual(w._clown_preclear_remaining, 0,
                         "pre-clear must not re-arm twice in one day")
        self.assertFalse(w._clown_entrance_pending)
        self.assertIsNone(w.clown_event, "clown must not re-fire twice in one day")


class Pickup(unittest.TestCase):
    """The die roll reserves the gauntlet and feeds N to the slot."""

    def _roll(self, ghost=False):
        from game.clown_event import ClownEvent
        w = World()
        ev = ClownEvent()
        w.clown_event = ev
        # Force the outcome deterministically, then run the collect→reveal path.
        ev.collected = True
        ev.ghost_run = ghost
        ev.roll = 10 if ghost else 18
        ev.spin_t = 0.0
        ev.phase = "rolling"
        ev._reveal(w)
        return w, ev

    def test_roll_reserves_slot(self):
        w, ev = self._roll()
        self.assertEqual(w._clown_slot_remaining, CLOWN_SLOT_PILLARS)
        self.assertEqual(len(w._clown_route), 18, "route length == rolled N")
        self.assertGreater(ev.die_pop_t, 0.0, "reveal banner armed")

    def test_ghost_sets_bird_ghost(self):
        w, ev = self._roll(ghost=True)
        self.assertTrue(ev.ghost_run)
        self.assertGreater(w.ghost_timer, 0.0, "GHOST roll phases Pip through")
        self.assertEqual(w.ghost_timer_total, w.ghost_timer)
        self.assertEqual(len(w._clown_route), 10, "ghost rolls the minimum")

    def test_auto_grab_on_pass(self):
        from game.clown_event import ClownEvent
        w = World()
        ev = ClownEvent()
        # Park the die well left of Pip so the auto-grab fires this tick.
        ev.dice_x = w.bird.x - 100
        ev.update(w, 1 / 60.0)
        self.assertTrue(ev.collected, "a die that drifts past Pip auto-grabs")
        self.assertEqual(ev.phase, "rolling")


class WeatherWidthInvariance(unittest.TestCase):
    """Rain/snow event DURATIONS must stay fixed in wall-clock seconds (and so
    in pillars) regardless of how long the biome day is — extending the cycle to
    absorb the clown event must NOT stretch the storms. Their shape offsets are
    scaled by (original cycle / current cycle); these products must equal the
    original 320 s-cycle phase widths × 320."""

    def test_rain_durations_are_cycle_invariant(self):
        import game.weather as w
        from game.biome import CYCLE_SECONDS as cyc
        drizzle = (w.RAIN_DRIZZLE_END - w.RAIN_DRIZZLE_START) * cyc
        self.assertAlmostEqual(drizzle, 0.18 * 320.0, places=4)
        self.assertAlmostEqual(w.RAIN_STORM_WIDTH * cyc, 0.08 * 320.0, places=4)

    def test_snow_duration_is_cycle_invariant(self):
        import game.weather as w
        from game.biome import CYCLE_SECONDS as cyc
        self.assertAlmostEqual(w.SNOW_STORM_WIDTH * cyc, 0.13 * 320.0, places=4)


if __name__ == "__main__":
    unittest.main()
