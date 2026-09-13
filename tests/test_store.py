"""
Coin Store unit tests — wallet, inventory, catalog.

Run with: ``python -m pytest tests/`` (gates the deploy alongside the
plausibility suite).

The catalog (game.store_catalog) and the persistence layer
(game.store_data) are pygame-free, so these run headless. Only the native
JSON branch is exercised — the emscripten localStorage bridge is a thin
getItem/setItem pass-through validated in-browser.
"""
import os
import json
import tempfile
import unittest

from game import store_catalog
from game import store_data


class _StoreTestBase(unittest.TestCase):
    """Point STORE_FILE at a throwaway path and reset the module cache so
    each test loads a fresh wallet from disk."""

    def setUp(self):
        self._tmp = tempfile.NamedTemporaryFile(
            suffix=".json", delete=False, mode="w")
        self._tmp.close()
        os.unlink(self._tmp.name)  # start with no file → default state
        self._orig_file = store_data.STORE_FILE
        store_data.STORE_FILE = self._tmp.name
        store_data._reset_for_test()

    def tearDown(self):
        store_data.STORE_FILE = self._orig_file
        store_data._reset_for_test()
        try:
            os.unlink(self._tmp.name)
        except OSError:
            pass

    def _reload(self):
        """Force a save-then-reload cycle to prove persistence round-trips."""
        store_data.save()
        store_data._reset_for_test()
        store_data.load()


class TestWallet(_StoreTestBase):

    def test_fresh_state_is_empty(self):
        self.assertEqual(store_data.balance(), 0)
        self.assertEqual(store_data.owned_ids(), set())
        self.assertEqual(store_data.equipped("skin"), store_catalog.BASE_SKIN)

    def test_add_coins_and_round_trip(self):
        store_data.add_coins(120)
        store_data.add_coins(30)
        self.assertEqual(store_data.balance(), 150)
        self._reload()
        self.assertEqual(store_data.balance(), 150)

    def test_add_coins_ignores_nonpositive(self):
        store_data.add_coins(100)
        store_data.add_coins(0)
        store_data.add_coins(-50)
        self.assertEqual(store_data.balance(), 100)


class TestPurchase(_StoreTestBase):

    def _an_item(self):
        # Cheapest catalog item so we can fund it deterministically.
        return min(store_catalog.CATALOG, key=store_catalog.cost)

    def test_purchase_deducts_and_unlocks(self):
        item = self._an_item()
        store_data.add_coins(store_catalog.cost(item) + 25)
        ok, reason = store_data.try_purchase(item)
        self.assertTrue(ok)
        self.assertEqual(reason, "")
        self.assertTrue(store_data.is_owned(item))
        self.assertEqual(store_data.balance(), 25)
        self._reload()
        self.assertTrue(store_data.is_owned(item))

    def test_repurchase_rejected(self):
        item = self._an_item()
        store_data.add_coins(store_catalog.cost(item) * 3)
        store_data.try_purchase(item)
        bal = store_data.balance()
        ok, reason = store_data.try_purchase(item)
        self.assertFalse(ok)
        self.assertEqual(reason, "owned")
        self.assertEqual(store_data.balance(), bal)

    def test_insufficient_funds(self):
        item = self._an_item()
        store_data.add_coins(store_catalog.cost(item) - 1)
        ok, reason = store_data.try_purchase(item)
        self.assertFalse(ok)
        self.assertEqual(reason, "insufficient")
        self.assertFalse(store_data.is_owned(item))
        self.assertEqual(store_data.balance(), store_catalog.cost(item) - 1)

    def test_unknown_item(self):
        store_data.add_coins(9999)
        ok, reason = store_data.try_purchase("skin_does_not_exist")
        self.assertFalse(ok)
        self.assertEqual(reason, "badid")

    def test_try_spend(self):
        store_data.add_coins(100)
        self.assertTrue(store_data.try_spend(60))
        self.assertEqual(store_data.balance(), 40)
        self.assertFalse(store_data.try_spend(50))  # not enough
        self.assertEqual(store_data.balance(), 40)
        self.assertFalse(store_data.try_spend(0))   # no free spends


class TestEquip(_StoreTestBase):

    def test_equip_requires_ownership(self):
        skin = store_catalog.skin_ids()[0]
        self.assertFalse(store_data.equip(skin))  # not owned yet
        store_data.grant(skin)
        self.assertTrue(store_data.equip(skin))
        self.assertEqual(store_data.equipped("skin"), skin)
        self._reload()
        self.assertEqual(store_data.equipped("skin"), skin)

    def test_base_skin_always_equippable(self):
        self.assertTrue(store_data.is_owned(store_catalog.BASE_SKIN))
        self.assertTrue(store_data.equip(store_catalog.BASE_SKIN))

    def test_equip_then_revert_to_default(self):
        skin = store_catalog.skin_ids()[0]
        store_data.grant(skin)
        store_data.equip(skin)
        self.assertEqual(store_data.equipped("skin"), skin)
        # The DEFAULT card path: re-equip the base look.
        self.assertTrue(store_data.equip(store_catalog.BASE_SKIN))
        self.assertEqual(store_data.equipped("skin"), store_catalog.BASE_SKIN)


class TestDaily(_StoreTestBase):

    def test_daily_claims_once_per_day(self):
        from game.config import DAILY_REWARD
        self.assertTrue(store_data.daily_available())
        granted = store_data.claim_daily()
        self.assertEqual(granted, DAILY_REWARD)
        self.assertEqual(store_data.balance(), DAILY_REWARD)
        self.assertFalse(store_data.daily_available())
        self.assertEqual(store_data.claim_daily(), 0)  # second same-day no-op
        self.assertEqual(store_data.balance(), DAILY_REWARD)


class TestResilience(_StoreTestBase):

    def test_corrupt_file_yields_defaults(self):
        with open(store_data.STORE_FILE, "w", encoding="utf-8") as f:
            f.write("{not valid json at all")
        store_data._reset_for_test()
        store_data.load()
        self.assertEqual(store_data.balance(), 0)
        self.assertEqual(store_data.owned_ids(), set())

    def test_forward_compat_missing_keys(self):
        # A state written by an older build: only wallet present.
        with open(store_data.STORE_FILE, "w", encoding="utf-8") as f:
            json.dump({"wallet": 77}, f)
        store_data._reset_for_test()
        store_data.load()
        self.assertEqual(store_data.balance(), 77)
        self.assertEqual(store_data.equipped("skin"), store_catalog.BASE_SKIN)
        self.assertIsNone(store_data.equipped("trail"))

    def test_unknown_owned_ids_dropped(self):
        with open(store_data.STORE_FILE, "w", encoding="utf-8") as f:
            json.dump({"owned": ["skin_tophat", "skin_phantom_xyz"]}, f)
        store_data._reset_for_test()
        store_data.load()
        owned = store_data.owned_ids()
        self.assertIn("skin_tophat", owned)
        self.assertNotIn("skin_phantom_xyz", owned)

    def test_stale_equipped_skin_resets_to_base(self):
        # A skin removed/renamed in a later build must not leave the UI showing
        # a stale "equipped" while the renderer falls back to the base look.
        with open(store_data.STORE_FILE, "w", encoding="utf-8") as f:
            json.dump({"equipped_skin": "skin_removed_xyz"}, f)
        store_data._reset_for_test()
        store_data.load()
        self.assertEqual(store_data.equipped("skin"), store_catalog.BASE_SKIN)

    def test_valid_equipped_skin_preserved(self):
        sid = store_catalog.skin_ids()[0]
        with open(store_data.STORE_FILE, "w", encoding="utf-8") as f:
            json.dump({"equipped_skin": sid}, f)
        store_data._reset_for_test()
        store_data.load()
        self.assertEqual(store_data.equipped("skin"), sid)


class TestCatalogIntegrity(unittest.TestCase):

    def test_entries_well_formed(self):
        for item_id, meta in store_catalog.CATALOG.items():
            self.assertIn("name", meta)
            self.assertIn("cost", meta)
            self.assertIn("kind", meta)
            self.assertIsInstance(meta["cost"], int)
            self.assertGreater(meta["cost"], 0)
            self.assertIn(meta["kind"], store_catalog.CATALOG_KINDS)

    def test_base_skin_not_sold(self):
        self.assertNotIn(store_catalog.BASE_SKIN, store_catalog.CATALOG)

    def test_every_entry_has_valid_group(self):
        for item_id, meta in store_catalog.CATALOG.items():
            self.assertIn(meta.get("group"), store_catalog.GROUPS,
                          f"{item_id} has an invalid/missing group")

    def test_costume_and_parrot_tabs_populated(self):
        # These two tabs ship with content; animals arrive via the design loop.
        self.assertTrue(store_catalog.ids_of_group("costume"))
        self.assertTrue(store_catalog.ids_of_group("parrot"))

    def test_ids_of_group_partition(self):
        # Every catalog item belongs to exactly one group tab; the union is the
        # full roster (skins across costume/parrot/animal/shoes/hats/shades plus
        # the parcels tab).
        by_group = []
        for g in store_catalog.GROUPS:
            by_group += store_catalog.ids_of_group(g)
        self.assertEqual(sorted(by_group), sorted(store_catalog.CATALOG.keys()))

    def test_cosmetic_pool_excludes_boosts(self):
        for item_id in store_catalog.cosmetic_ids():
            self.assertNotEqual(store_catalog.kind(item_id), "boost")

    def test_rarity_tiers(self):
        # Every catalog item maps to one of the four price-tier rarities, and
        # the free defaults read as common.
        for sid in store_catalog.CATALOG:
            self.assertIn(store_catalog.rarity(sid), store_catalog.RARITIES)
        self.assertEqual(store_catalog.rarity(store_catalog.BASE_SKIN), "common")
        self.assertEqual(store_catalog.rarity(store_catalog.PARCEL_BASE), "common")
        # Band boundaries spot-checked on representative items.
        self.assertEqual(store_catalog.rarity("skin_shades_none"), "common")   # 120
        self.assertEqual(store_catalog.rarity("skin_pirate"), "common")        # 280
        self.assertEqual(store_catalog.rarity("skin_ninja"), "rare")           # 560
        self.assertEqual(store_catalog.rarity("skin_eagle"), "epic")           # 900
        self.assertEqual(store_catalog.rarity("skin_dragon"), "legendary")     # 2300
        self.assertEqual(store_catalog.rarity("skin_kitsune"), "legendary")    # 3500

    def test_every_skin_resolves_in_renderer(self):
        # The catalog must never offer a skin the bird renderer can't draw.
        # Imported here (not module-top) so the pure-data tests above don't
        # pull in pygame.
        from game import parrot
        ids = parrot.skin_builder_ids()
        for sid in store_catalog.skin_ids():
            self.assertIn(sid, ids,
                          f"{sid} has no builder reachable from get_skin_frame")
        # Base skin is the implicit default and must also be drawable.
        self.assertIn(store_catalog.BASE_SKIN, ids)

    def test_shoes_tab_populated(self):
        # The SHOES tab ships with its full roster.
        shoes = store_catalog.ids_of_group("shoes")
        self.assertTrue(shoes)
        self.assertTrue(all(store_catalog.kind(s) == "skin" for s in shoes))

    def test_every_shoe_has_a_product_shot_icon(self):
        # Shoes are presented by their own product-shot icon (the sneaker
        # itself) rather than Pip wearing them, so every shoe id must resolve
        # to a non-None get_skin_icon. Non-shoe skins return None (in-game look).
        from game import parrot
        for sid in store_catalog.ids_of_group("shoes"):
            self.assertIsNotNone(parrot.get_skin_icon(sid),
                                 f"{sid} is missing a product-shot icon")
        # A representative non-shoe skin has no icon and falls back to the frame.
        self.assertIsNone(parrot.get_skin_icon(store_catalog.BASE_SKIN))

    def test_hats_tab_populated(self):
        # The HATS tab ships with its full roster, all skins with positive costs.
        hats = store_catalog.ids_of_group("hats")
        self.assertTrue(hats)
        self.assertTrue(all(store_catalog.kind(h) == "skin" for h in hats))
        self.assertTrue(all(isinstance(store_catalog.cost(h), int)
                            and store_catalog.cost(h) > 0 for h in hats))

    def test_every_hat_has_a_product_shot_icon(self):
        # Hats, like shoes, are presented by a product-shot icon, so every hat
        # id must resolve to a non-None get_skin_icon (the hat itself).
        from game import parrot
        for sid in store_catalog.ids_of_group("hats"):
            self.assertIsNotNone(parrot.get_skin_icon(sid),
                                 f"{sid} is missing a product-shot icon")

    def test_shades_tab_populated(self):
        # The SHADES tab ships with its full roster, all skins with positive
        # costs, and includes the NO SHADES remove option.
        shades = store_catalog.ids_of_group("shades")
        self.assertTrue(shades)
        self.assertIn("skin_shades_none", shades)
        self.assertTrue(all(store_catalog.kind(s) == "skin" for s in shades))
        self.assertTrue(all(isinstance(store_catalog.cost(s), int)
                            and store_catalog.cost(s) > 0 for s in shades))

    def test_styled_shades_have_icons_but_no_shades_does_not(self):
        # Every styled lens is shown by its product-shot icon (the glasses
        # themselves). NO SHADES has no lenses, so it has no icon and is
        # presented by the bare-eyed bird frame instead.
        from game import parrot
        for sid in store_catalog.ids_of_group("shades"):
            if sid == "skin_shades_none":
                self.assertIsNone(parrot.get_skin_icon(sid))
                self.assertIsNotNone(parrot.get_skin_frame(sid, 1, 0.0))
            else:
                self.assertIsNotNone(parrot.get_skin_icon(sid),
                                     f"{sid} is missing a product-shot icon")


class TestParcels(_StoreTestBase):
    """The PARCELS tab: a new independent equip slot whose free DEFAULT is the
    classic kraft box, fronted like PARROTS/SHADES. Every parcel must resolve in
    the parcel renderer and carry a store-card icon."""

    def test_parcels_group_registered(self):
        self.assertIn("parcels", store_catalog.GROUPS)
        self.assertIn("parcel", store_catalog.CATALOG_KINDS)

    def test_parcel_base_owned_and_equips(self):
        # The default parcel is implicitly owned (never sold) and equips into
        # its own slot, independent of the bird skin.
        self.assertTrue(store_data.is_owned(store_catalog.PARCEL_BASE))
        self.assertEqual(store_data.equipped("parcel"), store_catalog.PARCEL_BASE)
        self.assertTrue(store_data.equip(store_catalog.PARCEL_BASE))
        self.assertEqual(store_data.equipped("parcel"), store_catalog.PARCEL_BASE)
        # Equipping a parcel must not disturb the skin slot.
        self.assertEqual(store_data.equipped("skin"), store_catalog.BASE_SKIN)

    def test_parcel_catalog_entries_well_formed(self):
        for pid in store_catalog.ids_of_group("parcels"):
            self.assertEqual(store_catalog.kind(pid), "parcel")
            self.assertGreater(store_catalog.cost(pid), 0)

    def test_every_parcel_resolves_in_renderer(self):
        # Base + every catalog parcel must produce a square sprite via the
        # parcel dispatch, and register in the parcel builders. Most are exactly
        # PARCEL_SIZE; a few run larger to carry a glow skirt (e.g. the lantern),
        # so the contract is "square, at least PARCEL_SIZE" — the draw code
        # anchors on centre so an oversize sprite still hangs correctly.
        from game import parrot
        builders = parrot._store_parcel_builders()
        for pid in [store_catalog.PARCEL_BASE] + store_catalog.ids_of_group("parcels"):
            surf = parrot.get_parcel("normal", pid)
            w, h = surf.get_size()
            self.assertEqual(w, h, f"{pid} sprite must be square")
            self.assertGreaterEqual(w, parrot.PARCEL_SIZE,
                                    f"{pid} sprite smaller than PARCEL_SIZE")
            self.assertIn(pid, builders, f"{pid} missing a parcel builder")

    def test_every_parcel_has_a_product_shot_icon(self):
        from game import parrot
        for pid in [store_catalog.PARCEL_BASE] + store_catalog.ids_of_group("parcels"):
            self.assertIsNotNone(parrot.get_skin_icon(pid),
                                 f"{pid} is missing a product-shot icon")


class TestBuyConfirmFlow(_StoreTestBase):
    """The store gates every coin-spending purchase behind a confirm modal: a
    tap on an unowned card only opens the modal; coins move on CONFIRM, never
    on the first tap. Needs a headless pygame surface, so it builds a StoreScene.
    """

    def setUp(self):
        super().setUp()
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
        os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
        import pygame
        pygame.init()
        pygame.display.set_mode((360, 640))
        from game.store import StoreScene
        self.surf = pygame.Surface((360, 640))
        self.scene = StoreScene()
        # The buy-confirm flow lives in the category grid; a purchase is only
        # reachable after drilling into a stall from the lagoon hub, so drive the
        # scene there before exercising it (the hub itself sells nothing).
        self.scene.view = "category"
        store_data.add_coins(99999)
        # A known unowned, non-secret catalog item.
        self.item = "skin_pirate"

    def _render(self):
        self.scene.render(self.surf)

    def test_tap_unowned_opens_modal_without_buying(self):
        self.scene._tap_item(self.item)
        self.assertEqual(self.scene._confirm, self.item)
        self.assertFalse(store_data.is_owned(self.item))
        self.assertEqual(store_data.balance(), 99999)

    def test_confirm_buys_and_equips(self):
        self.scene._tap_item(self.item)
        self._render()  # lays out confirm_yes_rect
        self.scene.handle_tap(self.scene.confirm_yes_rect.center)
        self.assertTrue(store_data.is_owned(self.item))
        self.assertEqual(store_data.equipped("skin"), self.item)
        self.assertEqual(store_data.balance(), 99999 - store_catalog.cost(self.item))
        self.assertIsNone(self.scene._confirm)

    def test_cancel_dismisses_without_buying(self):
        self.scene._tap_item(self.item)
        self._render()
        self.scene.handle_tap(self.scene.confirm_no_rect.center)
        self.assertFalse(store_data.is_owned(self.item))
        self.assertEqual(store_data.balance(), 99999)
        self.assertIsNone(self.scene._confirm)

    def test_tap_scrim_outside_panel_dismisses(self):
        self.scene._tap_item(self.item)
        self._render()
        self.scene.handle_tap((4, 4))  # corner of the scrim, off the panel
        self.assertFalse(store_data.is_owned(self.item))
        self.assertIsNone(self.scene._confirm)

    def test_modal_is_exclusive(self):
        # With the modal up, a tap that isn't a modal control can't switch tabs
        # or buy; it just (when on the scrim) dismisses.
        self.scene._tap_item(self.item)
        self._render()
        before = self.scene.tab
        self.scene.handle_tap((4, 4))
        self.assertEqual(self.scene.tab, before)


if __name__ == "__main__":
    unittest.main()
