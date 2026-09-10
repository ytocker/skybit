"""Lagoon-hub stall-front unit tests — registry wiring + every design renders.

Run with: ``python -m pytest tests/`` (gates the deploy alongside the
plausibility suite).

Two of the five item designs (`hook_rail`, `counter`) are held in reserve for
categories that are still shuttered, so nothing on screen exercises them. They
are rendered here anyway: an unused design that no longer builds is the whole
risk of parking it in the tree, and a silent break would only surface when a
new stall opens months later.

Needs a headless pygame surface, same as the other render-backed suites.
"""
import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

pygame.init()
pygame.display.set_mode((360, 640))

from game import stall_fronts
from game.store_hub import DW, DH, m


def _ctx(group, scale=0.96, fy=0.862):
    """The context dict store_hub.draw_hut hands the stall-front hooks, built
    with the same geometry for a hut at the supersampled device resolution."""
    cx = int(DW * 0.5)
    deck_y = int(DH * fy)
    body_h = int(m(64) * scale)
    body_top = deck_y - body_h
    return dict(cx=cx, deck_y=deck_y, body_top=body_top, body_h=body_h,
                half_w=int(m(58) * scale), eave=int(m(10) * scale),
                roof_apex_y=body_top - int(m(40) * scale),
                scale=scale, group=group, label=stall_fronts.__name__.upper()[:8])


class TestRegistry(unittest.TestCase):
    def test_every_open_group_maps_to_a_real_design(self):
        for group, design in stall_fronts.ITEM.items():
            self.assertIn(design, stall_fronts.DESIGNS,
                          f"{group} points at unknown design {design!r}")

    def test_reserve_designs_are_still_present(self):
        # Kept for the shuttered categories; deleting one is a decision, not a
        # tidy-up, so the loss should fail here rather than pass silently.
        for design in ("hook_rail", "counter"):
            self.assertIn(design, stall_fronts.DESIGNS)


class TestDesignsRender(unittest.TestCase):
    """Every design — including the two no stall wears yet — must draw, and
    must stay inside the stall opening (the m(8) side posts and the deck lip
    are hard walls of the hut architecture)."""

    def _render(self, fn, group, scale, fy):
        ctx = _ctx(group, scale, fy)
        surf = pygame.Surface((DW, DH), pygame.SRCALPHA)
        fn(surf, ctx)
        return surf, ctx

    def test_each_design_draws_something(self):
        for name, fn in stall_fronts.DESIGNS.items():
            with self.subTest(design=name):
                surf, _ = self._render(fn, "parcels", 0.96, 0.862)
                self.assertIsNotNone(surf.get_bounding_rect(),
                                     f"{name} drew nothing")
                self.assertGreater(surf.get_bounding_rect().width, 0,
                                   f"{name} drew nothing")

    def test_each_design_stays_inside_the_opening(self):
        for name, fn in stall_fronts.DESIGNS.items():
            with self.subTest(design=name):
                surf, ctx = self._render(fn, "parcels", 0.96, 0.862)
                bb = surf.get_bounding_rect()
                self.assertGreaterEqual(bb.left, ctx["cx"] - ctx["half_w"],
                                        f"{name} crossed the left post")
                self.assertLessEqual(bb.right, ctx["cx"] + ctx["half_w"],
                                     f"{name} crossed the right post")
                self.assertLessEqual(bb.bottom, ctx["deck_y"] + m(4),
                                     f"{name} spilled past the deck lip")
                # Reaching up into the awning's scallop voids is by design —
                # climbing past the seam onto the thatch is not.
                self.assertGreaterEqual(bb.top, ctx["body_top"],
                                        f"{name} painted onto the roof")

    def test_each_design_renders_at_both_live_stall_scales(self):
        # The open stalls run at 0.92 and 0.96; a design that only survives one
        # of them breaks the moment it is assigned to a different tier.
        for name, fn in stall_fronts.DESIGNS.items():
            for group, scale, fy in (("parrot", 0.92, 0.788),
                                     ("costume", 0.92, 0.788),
                                     ("parcels", 0.96, 0.862)):
                with self.subTest(design=name, group=group):
                    self._render(fn, group, scale, fy)


class TestSignRenders(unittest.TestCase):
    def test_sign_draws_above_the_awning_seam(self):
        # The seam at body_top is the ceiling of the opening below; the sign
        # rides the roof and must never dip onto the stripes.
        ctx = _ctx("parcels")
        surf = pygame.Surface((DW, DH), pygame.SRCALPHA)
        stall_fronts.draw_sign(surf, ctx)
        bb = surf.get_bounding_rect()
        self.assertGreater(bb.width, 0, "sign drew nothing")
        self.assertLessEqual(bb.bottom, ctx["body_top"] + m(2))


if __name__ == "__main__":
    unittest.main()
