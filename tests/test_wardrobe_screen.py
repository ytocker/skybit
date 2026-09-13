"""WardrobeScene + ProfileScene + the store_data.slot_of() refactor.

Run with: ``python -m pytest tests/``.
"""
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import os as _os_mod
import tempfile
import unittest

import pygame

pygame.init()
pygame.font.init()

from game import store_catalog, store_data
from game.config import W, H


class _StoreTestBase(unittest.TestCase):
    """Same tempfile-backed STORE_FILE pattern as tests/test_store.py, so
    each test starts from a fresh, isolated save."""

    def setUp(self):
        self._tmp = tempfile.NamedTemporaryFile(
            suffix=".json", delete=False, mode="w")
        self._tmp.close()
        _os_mod.unlink(self._tmp.name)
        self._orig_file = store_data.STORE_FILE
        store_data.STORE_FILE = self._tmp.name
        store_data._reset_for_test()

    def tearDown(self):
        store_data.STORE_FILE = self._orig_file
        store_data._reset_for_test()
        try:
            _os_mod.unlink(self._tmp.name)
        except OSError:
            pass


class TestSlotOf(unittest.TestCase):
    def test_matches_store_private_helper_for_a_skin(self):
        from game import store as _store
        sid = store_catalog.ids_of_group("costume")[0]
        self.assertEqual(store_data.slot_of(sid), _store._slot_of(sid))
        self.assertEqual(store_data.slot_of(sid), "skin")

    def test_matches_store_private_helper_for_a_parcel(self):
        from game import store as _store
        ids = store_catalog.ids_of_group("parcels")
        if ids:
            sid = ids[0]
            self.assertEqual(store_data.slot_of(sid), _store._slot_of(sid))
            self.assertEqual(store_data.slot_of(sid), "parcel")

    def test_base_defaults(self):
        self.assertEqual(store_data.slot_of(store_catalog.BASE_SKIN), "skin")
        self.assertEqual(store_data.slot_of(store_catalog.PARCEL_BASE), "parcel")


class TestWardrobeScene(_StoreTestBase):
    def _scene(self):
        from game.wardrobe_screen import WardrobeScene
        return WardrobeScene()

    def _render(self, sc):
        surf = pygame.Surface((W, H), pygame.SRCALPHA)
        sc.render(surf)
        return surf

    def test_category_switch_updates_rows_and_rail_selection(self):
        sc = self._scene()
        self._render(sc)
        self.assertEqual(sc.sel_group, "costume")
        parrot_rect = next(r for r, g in sc.rail_rects if g == "parrot")
        sc.handle_tap(parrot_rect.center)
        self.assertEqual(sc.sel_group, "parrot")
        self._render(sc)  # must not raise after switching

    def test_tapping_owned_tile_equips_and_persists(self):
        ids = store_catalog.ids_of_group("costume")
        a, b = ids[0], ids[1]
        store_data._ensure()["owned"] = [a, b]
        store_data.equip(a)

        sc = self._scene()
        self._render(sc)
        rect, tile = next((r, t) for r, t in sc._tile_layout
                          if t["kind"] == "own" and t["sid"] == b)
        self.assertFalse(tile["equipped"])

        screen_pos = (rect.x + sc.view.x + 1,
                     rect.y + sc.view.y - int(sc.scroll_offset) + 1)
        sc.handle_tap(screen_pos)
        self.assertEqual(store_data.equipped("skin"), b)

        # Re-render must reflect the new equip state (cache invalidated).
        self._render(sc)
        _, tile2 = next((r, t) for r, t in sc._tile_layout if t["sid"] == b)
        self.assertTrue(tile2["equipped"])
        _, tile_a = next((r, t) for r, t in sc._tile_layout if t["sid"] == a)
        self.assertFalse(tile_a["equipped"])

    def test_tapping_already_equipped_tile_is_a_noop(self):
        ids = store_catalog.ids_of_group("costume")
        a = ids[0]
        store_data._ensure()["owned"] = [a]
        store_data.equip(a)
        before = dict(store_data._ensure())

        sc = self._scene()
        self._render(sc)
        rect, _tile = next((r, t) for r, t in sc._tile_layout if t["sid"] == a)
        screen_pos = (rect.x + sc.view.x + 1,
                     rect.y + sc.view.y - int(sc.scroll_offset) + 1)
        sc.handle_tap(screen_pos)
        self.assertEqual(store_data._ensure(), before)

    def test_tapping_void_tile_does_nothing(self):
        sc = self._scene()
        self._render(sc)
        rect, tile = next((r, t) for r, t in sc._tile_layout if t["kind"] == "void")
        screen_pos = (rect.x + sc.view.x + 1,
                     rect.y + sc.view.y - int(sc.scroll_offset) + 1)
        before_owned = store_data.owned_ids()
        sc.handle_tap(screen_pos)
        self.assertEqual(store_data.owned_ids(), before_owned)

    def test_equip_is_mutually_exclusive_across_groups_sharing_the_skin_slot(self):
        costume_id = store_catalog.ids_of_group("costume")[0]
        parrot_ids = store_catalog.ids_of_group("parrot")
        if not parrot_ids:
            self.skipTest("no parrot catalog entries")
        parrot_id = parrot_ids[0]
        store_data._ensure()["owned"] = [costume_id, parrot_id]
        store_data.equip(costume_id)
        self.assertEqual(store_data.equipped("skin"), costume_id)
        store_data.equip(parrot_id)
        self.assertEqual(store_data.equipped("skin"), parrot_id)
        # The costume group's own view must now show nothing equipped —
        # cross-checked directly via store_data, the real source of truth.
        self.assertNotEqual(store_data.equipped("skin"), costume_id)

    def test_grand_total_matches_real_owned_counts_across_groups(self):
        from game import wardrobe_screen as ws
        costume_ids = store_catalog.ids_of_group("costume")
        store_data._ensure()["owned"] = costume_ids[:2]
        expected = sum(ws._owned_count(g) for _, g in ws.CATS)
        self.assertEqual(expected, 2)


class TestAchievementsEmbedded(unittest.TestCase):
    def test_embedded_mode_renders_without_own_header_or_footer(self):
        from game import achievements as ach
        from game.achievements_screen import AchievementsScene

        store = ach._blank()
        surf = pygame.Surface((W, H), pygame.SRCALPHA)

        sc = AchievementsScene()
        sc.embedded_top = 72
        sc.render(surf, 1 / 60, store)

        self.assertIsNotNone(sc.tab_fame_rect)
        self.assertIsNotNone(sc.tab_shame_rect)
        self.assertEqual(sc.tab_fame_rect.y, 76)  # embedded_top(72) + 4
        # Standalone mode draws its own footer/MENU button; embedded mode
        # leaves that to the host and never sets this rect.
        self.assertIsNone(sc.menu_btn_rect)

    def test_standalone_mode_unchanged(self):
        from game import achievements as ach
        from game.achievements_screen import AchievementsScene

        store = ach._blank()
        surf = pygame.Surface((W, H), pygame.SRCALPHA)

        sc = AchievementsScene()
        sc.render(surf, 1 / 60, store)

        self.assertIsNotNone(sc.menu_btn_rect)
        self.assertEqual(sc.tab_fame_rect.y, 60)  # HEADER_H(56) + 4


class TestProfileScene(unittest.TestCase):
    def test_tab_switch_and_close(self):
        from game.profile_screen import ProfileScene

        surf = pygame.Surface((W, H), pygame.SRCALPHA)
        ps = ProfileScene()
        ps.render(surf)
        self.assertEqual(ps.tab, "wardrobe")

        result = ps.tap_or_close(ps.tab_achievements_rect.center)
        self.assertIsNone(result)
        self.assertEqual(ps.tab, "achievements")
        ps.render(surf)

        result = ps.tap_or_close(ps.menu_btn_rect.center)
        self.assertEqual(result, "close")


if __name__ == "__main__":
    unittest.main()
