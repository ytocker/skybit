"""Startup budget guard — the load path must stay lazy.

Eagerly building the store-skin hurt/hat frames once cost roughly 1000 seconds
of hang under pygbag before it was made lazy; the browser pays orders of
magnitude more for pure-Python frame construction than a desktop does, so a
build that is merely slow natively can look like a game that never finishes
loading. These tests pin the two properties that keep that from coming back:
nothing builds skin frames while the game is starting, and the per-frame HUD
art the player sees on every frame is cached rather than redrawn.

Run with: ``python -m pytest tests/``.
"""
import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

pygame.init()
pygame.display.set_mode((360, 640))


class TestSkinFramesStayLazy(unittest.TestCase):
    """Importing the game and constructing App() must not build any store-skin
    frame. The frames the game genuinely needs are queued on App's prewarm
    queue and drained one per frame AFTER the first paint, so the splash lifts
    without waiting for them."""

    def test_no_skin_frames_built_during_startup(self):
        from game import store_skin_hurt, store_skin_hat

        calls = []
        originals = []
        targets = ((store_skin_hurt, "_prebuild_pair"),
                   (store_skin_hat, "_prebuild_triple"))
        for mod, name in targets:
            fn = getattr(mod, name, None)
            # A renamed builder would silently gut this test, so require it.
            self.assertTrue(callable(fn), f"{mod.__name__}.{name} is missing — "
                                          "update this guard to the new name")

            def make(fn=fn, tag=f"{mod.__name__}.{name}"):
                def wrapped(*a, **k):
                    calls.append(tag)
                    return fn(*a, **k)
                return wrapped

            originals.append((mod, name, fn))
            setattr(mod, name, make())

        try:
            from game.scenes import App
            app = App()
            # The queue is what defers the real work; it must still be pending.
            self.assertTrue(getattr(app, "_prewarm_queue", None),
                            "startup prewarm queue is empty — frame builds "
                            "may have moved back onto the load path")
        finally:
            for mod, name, fn in originals:
                setattr(mod, name, fn)

        self.assertEqual(calls, [],
                         f"store-skin frames built during startup: {calls}")


class TestNestArtIsCached(unittest.TestCase):
    """Both nest slots are static art drawn on every frame of a run, so both
    are cached. Drawing them live costs hundreds of per-pixel writes a frame."""

    def test_both_slots_cache_after_first_draw(self):
        from game import hud
        hud._NEST_SLOT_SPRITES = {}
        surf = pygame.Surface((360, 640), pygame.SRCALPHA)
        hud._nest_draw_slot(surf, hud._NEST_CY, True)
        hud._nest_draw_slot(surf, hud._NEST_CY, False)
        self.assertIsNotNone(hud._NEST_SLOT_SPRITES.get((hud._NEST_CY, True)),
                             "alive slot is not cached")
        self.assertIsNotNone(hud._NEST_SLOT_SPRITES.get((hud._NEST_CY, False)),
                             "empty slot is not cached")

    def test_cached_slot_is_reused_not_rebuilt(self):
        from game import hud
        hud._NEST_SLOT_SPRITES = {}
        surf = pygame.Surface((360, 640), pygame.SRCALPHA)
        hud._nest_draw_slot(surf, hud._NEST_CY, True)
        first = hud._NEST_SLOT_SPRITES[(hud._NEST_CY, True)]
        hud._nest_draw_slot(surf, hud._NEST_CY, True)
        self.assertIs(hud._NEST_SLOT_SPRITES[(hud._NEST_CY, True)], first,
                      "alive nest sprite was rebuilt on the second frame")


if __name__ == "__main__":
    unittest.main()
