"""
Achievements engine unit tests.

Run with: ``python -m pytest tests/``.

Exercises the end-of-run evaluator: correct unlocks fire from a finished run's
stats, lifetime counters accumulate across runs, derived stats (distinct
power-ups, lottery jackpot from the proof ledger) resolve, and a repeat of an
identical run yields no *new* unlocks. Persistence I/O is stubbed so the tests
never touch disk or a browser bridge.
"""
import unittest

from game import achievements as ach
from game.config import RAIN_START_PILLAR


class _FakeProof:
    def __init__(self, events):
        self._events = list(events)

    def events_tuple(self):
        return list(self._events)


class _FakeWorld:
    """Minimal stand-in exposing the attributes evaluate_run reads."""

    def __init__(self, **kw):
        self.score = kw.get("score", 0)
        self.coin_count = kw.get("coin_count", 0)
        self.pillars_passed = kw.get("pillars_passed", 0)
        self.time_alive = kw.get("time_alive", 0.0)
        self.near_misses = kw.get("near_misses", 0)
        self.flap_count = kw.get("flap_count", 0)
        self.cycles_completed = kw.get("cycles_completed", 0)
        self.ceiling_hits = kw.get("ceiling_hits", 0)
        self.tricks_landed = kw.get("tricks_landed", 0)
        self.tricks_landed_types = set(kw.get("tricks_landed_types", ()))
        self.powerups_picked = dict(ach._blank()["life"]["powerups_seen"])  # empty-ish
        self.powerups_picked = kw.get("powerups_picked", {})
        self._proof = _FakeProof(kw.get("events", []))
        # Wall-of-Shame signals (death-moment snapshot + per-run extras).
        self.coins_spawned = kw.get("coins_spawned", 0)
        self.death_ghost = kw.get("death_ghost", False)
        self.death_kfc = kw.get("death_kfc", False)
        self.max_flaps_per_sec = kw.get("max_flaps_per_sec", 0)
        self._lottery_pulled = kw.get("_lottery_pulled", False)
        self.died_early_phase = kw.get("died_early_phase", False)
        # Hall-of-Shame expansion signals (death-moment snapshot + tallies).
        self.death_slowmo = kw.get("death_slowmo", False)
        self.death_poison = kw.get("death_poison", False)
        self.death_skateboard = kw.get("death_skateboard", False)
        self.death_lightning = kw.get("death_lightning", False)
        self.death_celebration = kw.get("death_celebration", False)
        self.death_magnet_zero = kw.get("death_magnet_zero", False)
        self.death_wish_pending = kw.get("death_wish_pending", False)
        self.coin_blind = kw.get("coin_blind", False)
        self._lightning_strikes_run = kw.get("_lightning_strikes_run", 0)


class TestAchievements(unittest.TestCase):

    def setUp(self):
        # Stub persistence so nothing hits disk / the browser bridge.
        self._orig_save = ach.save
        ach.save = lambda store=None: None
        ach.reset_cache()

    def tearDown(self):
        ach.save = self._orig_save
        ach.reset_cache()

    def test_first_flight_and_basic_thresholds(self):
        store = ach._blank()
        w = _FakeWorld(pillars_passed=30, score=120, coin_count=26)
        newly = ach.evaluate_run(w, store)
        self.assertIn("first_flight", newly)
        self.assertIn("pillar_25", newly)
        self.assertIn("score_100", newly)
        self.assertIn("coin_25_run", newly)
        # Not reached this run.
        self.assertNotIn("pillar_50", newly)
        self.assertNotIn("score_500", newly)

    def test_no_rerun_duplicates(self):
        store = ach._blank()
        w = _FakeWorld(pillars_passed=30)
        first = ach.evaluate_run(w, store)
        self.assertIn("first_flight", first)
        # A second run past the same thresholds must not re-fire already-unlocked
        # ids. Dies on a DIFFERENT pillar (31) so the repeat-pillar streak stays
        # at 1 and groundhog_day (a legitimate cross-run unlock) doesn't fire.
        second = ach.evaluate_run(_FakeWorld(pillars_passed=31), store)
        self.assertEqual(second, [])

    def test_lifetime_accumulation_unlocks(self):
        store = ach._blank()
        # 500 lifetime coins via ten 50-coin runs; coins_500_life unlocks on
        # the run that crosses the threshold, not before.
        unlocked_on = None
        for i in range(10):
            newly = ach.evaluate_run(_FakeWorld(coin_count=50), store)
            if "coins_500_life" in newly:
                unlocked_on = i
        self.assertEqual(store["life"]["total_coins"], 500)
        self.assertEqual(store["life"]["total_runs"], 10)
        self.assertEqual(unlocked_on, 9)

    def test_distinct_powerups_run_and_life(self):
        store = ach._blank()
        w = _FakeWorld(powerups_picked={"triple": 1, "magnet": 2,
                                        "slowmo": 1, "ghost": 1})
        newly = ach.evaluate_run(w, store)
        self.assertIn("first_powerup", newly)
        self.assertIn("powerup_sampler", newly)   # 4 distinct in the run
        # magnet_life counts magnet + megamagnet; only 2 so far.
        self.assertNotIn("magnet_life", newly)

    def test_hidden_secret_from_pickup(self):
        store = ach._blank()
        w = _FakeWorld(powerups_picked={"genie": 1, "poison": 1})
        newly = ach.evaluate_run(w, store)
        self.assertIn("made_a_wish", newly)
        self.assertIn("poisoned", newly)
        self.assertTrue(ach.BY_ID["made_a_wish"].hidden)

    def test_lottery_jackpot_from_events(self):
        store = ach._blank()
        jackpot = ach._JACKPOT_DELTA
        w = _FakeWorld(events=[(1.0, jackpot, "lottery")])
        newly = ach.evaluate_run(w, store)
        self.assertIn("jackpot", newly)
        # A losing lottery roll must not count.
        store2 = ach._blank()
        w2 = _FakeWorld(events=[(1.0, -10, "lottery")])
        self.assertNotIn("jackpot", ach.evaluate_run(w2, store2))

    def test_weather_biome_threshold(self):
        store = ach._blank()
        w = _FakeWorld(pillars_passed=RAIN_START_PILLAR)
        self.assertIn("storm_rider", ach.evaluate_run(w, store))

    def test_headbanger_run(self):
        store = ach._blank()
        self.assertNotIn("headbanger", ach.evaluate_run(_FakeWorld(ceiling_hits=9), store))
        self.assertIn("headbanger", ach.evaluate_run(_FakeWorld(ceiling_hits=10), ach._blank()))

    def test_full_combo_trick_types(self):
        store = ach._blank()
        three = _FakeWorld(tricks_landed=8,
                           tricks_landed_types=("backflip", "kickflip", "heelflip"))
        self.assertNotIn("full_combo", ach.evaluate_run(three, store))
        four = _FakeWorld(tricks_landed=4,
                          tricks_landed_types=("backflip", "kickflip", "heelflip", "popshuvit"))
        self.assertIn("full_combo", ach.evaluate_run(four, ach._blank()))

    def test_lifetime_tricks_and_ceiling_accumulate(self):
        store = ach._blank()
        got_trickster = False
        for _ in range(5):
            newly = ach.evaluate_run(_FakeWorld(tricks_landed=10, ceiling_hits=40), store)
            got_trickster = got_trickster or ("trickster" in newly)
        self.assertEqual(store["life"]["total_tricks"], 50)
        self.assertEqual(store["life"]["total_ceiling"], 200)
        self.assertTrue(got_trickster)               # 50 tricks all-time
        self.assertIn("hard_head", store["unlocked"])  # 200 ceiling bonks all-time

    def test_lifetime_skateboards_and_rails(self):
        store = ach._blank()
        for _ in range(10):
            ach.evaluate_run(_FakeWorld(powerups_picked={"skateboard": 1, "rail": 1}), store)
        self.assertEqual(store["life"]["powerups_seen"]["skateboard"], 10)
        self.assertIn("sponsored", store["unlocked"])  # 10 skateboards
        self.assertIn("grinder", store["unlocked"])    # 10 rails

    def test_total_powerups_lifetime(self):
        store = ach._blank()
        # 25 power-ups per run across 4 runs = 100 → Power Hungry.
        for _ in range(4):
            ach.evaluate_run(_FakeWorld(powerups_picked={"triple": 13, "magnet": 12}), store)
        self.assertIn("power_hungry", store["unlocked"])
        self.assertNotIn("power_addict", store["unlocked"])

    def test_registry_ids_unique(self):
        ids = [a.id for a in ach.ACHIEVEMENTS]
        self.assertEqual(len(ids), len(set(ids)))
        # Every achievement belongs to a known category bucket.
        for a in ach.ACHIEVEMENTS:
            self.assertIn(a, ach.BY_CAT[a.category])


class TestWallOfShame(unittest.TestCase):
    """Anti-achievements: triggers fire at threshold, lifetime tallies fold in,
    and shame ids stay disjoint from the Fame roster."""

    def setUp(self):
        self._orig_save = ach.save
        ach.save = lambda store=None: None
        ach.reset_cache()

    def tearDown(self):
        ach.save = self._orig_save
        ach.reset_cache()

    def test_ids_disjoint_and_registered(self):
        fame = {a.id for a in ach.ACHIEVEMENTS}
        self.assertTrue(ach.SHAME_IDS.isdisjoint(fame))
        for sid in ach.SHAME_IDS:
            self.assertIn(sid, ach.BY_ID)          # unified lookup covers shame
            self.assertTrue(ach.is_shame(sid))
        for a in ach.SHAME_ACHIEVEMENTS:
            self.assertIn(a, ach.BY_CAT_SHAME[a.category])

    def test_goose_egg_and_icarus(self):
        store = ach._blank()
        newly = ach.evaluate_run(
            _FakeWorld(score=0, coin_count=0, pillars_passed=0), store)
        self.assertIn("goose_egg", newly)
        self.assertIn("icarus", newly)            # pillars_passed <= 1
        self.assertEqual(store["life"]["scoreless_deaths"], 1)
        self.assertEqual(store["life"]["pillar1_deaths"], 1)

    def test_goose_egg_needs_zero_coins(self):
        store = ach._blank()
        # A coin disqualifies the Goose Egg (stricter than a pillar-1 death).
        newly = ach.evaluate_run(
            _FakeWorld(score=0, coin_count=3, pillars_passed=0), store)
        self.assertNotIn("goose_egg", newly)
        self.assertIn("icarus", newly)

    def test_ghost_and_kfc_death(self):
        store = ach._blank()
        newly = ach.evaluate_run(
            _FakeWorld(pillars_passed=20, death_ghost=True, death_kfc=True), store)
        self.assertIn("denial", newly)
        self.assertIn("kfc_incident", newly)

    def test_hummingbird_threshold(self):
        store = ach._blank()
        self.assertNotIn(
            "hummingbird",
            ach.evaluate_run(_FakeWorld(pillars_passed=5, max_flaps_per_sec=9), store))
        self.assertIn(
            "hummingbird",
            ach.evaluate_run(_FakeWorld(pillars_passed=5, max_flaps_per_sec=10),
                             ach._blank()))

    def test_49er_and_night_owl_and_lottery(self):
        self.assertIn("the_49er",
                      ach.evaluate_run(_FakeWorld(pillars_passed=49), ach._blank()))
        self.assertNotIn("the_49er",
                         ach.evaluate_run(_FakeWorld(pillars_passed=50), ach._blank()))
        self.assertIn("night_owl",
                      ach.evaluate_run(_FakeWorld(died_early_phase=True), ach._blank()))
        self.assertIn("lottery_loser",
                      ach.evaluate_run(_FakeWorld(_lottery_pulled=True), ach._blank()))

    def test_shame_death_context_flags(self):
        # Each death-moment snapshot flag fires its own Blooper Reel roast.
        cases = {
            "bullet_bystander": dict(death_slowmo=True),
            "cursed": dict(death_poison=True),
            "board_to_death": dict(death_skateboard=True),
            "lightning_rod": dict(death_lightning=True),
            "party_foul": dict(death_celebration=True),
        }
        for ach_id, kw in cases.items():
            newly = ach.evaluate_run(_FakeWorld(pillars_passed=20, **kw),
                                     ach._blank())
            self.assertIn(ach_id, newly)

    def test_wasted_opportunity(self):
        self.assertIn("rich_reckless", ach.evaluate_run(
            _FakeWorld(pillars_passed=15, death_magnet_zero=True), ach._blank()))
        self.assertIn("coin_blind", ach.evaluate_run(
            _FakeWorld(pillars_passed=15, coin_blind=True), ach._blank()))
        self.assertIn("wish_unspent", ach.evaluate_run(
            _FakeWorld(pillars_passed=55, death_wish_pending=True), ach._blank()))

    def test_cosmic_joke_run_scope(self):
        # Ninety-Nine Problems: exactly 99, not 98/100.
        self.assertIn("ninety_nine",
                      ach.evaluate_run(_FakeWorld(score=99), ach._blank()))
        self.assertNotIn("ninety_nine",
                         ach.evaluate_run(_FakeWorld(score=100), ach._blank()))
        # Statistically Impossible: score/pillars/coins all prime (7, 5, 3).
        self.assertIn("stat_impossible", ach.evaluate_run(
            _FakeWorld(score=7, pillars_passed=5, coin_count=3), ach._blank()))
        # A single composite disqualifies it (4 is not prime).
        self.assertNotIn("stat_impossible", ach.evaluate_run(
            _FakeWorld(score=7, pillars_passed=4, coin_count=3), ach._blank()))

    def test_groundhog_day_repeat_pillar(self):
        store = ach._blank()
        self.assertNotIn("groundhog_day",
                         ach.evaluate_run(_FakeWorld(pillars_passed=12), store))
        # Dying on the same pillar again flips the streak to 2 → unlock.
        self.assertIn("groundhog_day",
                      ach.evaluate_run(_FakeWorld(pillars_passed=12), store))

    def test_same_time_tomorrow(self):
        import time as _t
        store = ach._blank()
        hm = _t.strftime("%H:%M", _t.localtime())
        # Pre-seed this minute as first played on a different calendar day.
        store["life"]["play_minutes"][hm] = "1999-01-01"
        self.assertIn("same_time_tomorrow",
                      ach.evaluate_run(_FakeWorld(pillars_passed=3), store))

    def test_lifetime_snake_bit_and_lightning_magnet(self):
        store = ach._blank()
        for _ in range(5):
            ach.evaluate_run(_FakeWorld(pillars_passed=8, death_poison=True,
                                        _lightning_strikes_run=5), store)
        self.assertEqual(store["life"]["poison_deaths"], 5)
        self.assertEqual(store["life"]["lightning_hits"], 25)
        self.assertIn("snake_bit", store["unlocked"])
        self.assertIn("lightning_magnet", store["unlocked"])

    def test_lifetime_scrooge_and_early_checkout(self):
        store = ach._blank()
        # 25 sub-3s runs unlock Early Checkout; coins-flown-past accrue toward Scrooge.
        for _ in range(24):
            ach.evaluate_run(_FakeWorld(time_alive=1.0, coin_count=0, coins_spawned=10), store)
        self.assertNotIn("early_checkout", store["unlocked"])
        ach.evaluate_run(_FakeWorld(time_alive=1.0, coin_count=0, coins_spawned=10), store)
        self.assertIn("early_checkout", store["unlocked"])
        self.assertEqual(store["life"]["coins_missed_life"], 25 * 10)


class TestProfileSchemaAndMerge(unittest.TestCase):
    """v2 blob: migration, cloud-merge policy, derived coin balance, inventory."""

    def setUp(self):
        self._orig_save = ach.save
        ach.save = lambda store=None: None
        ach.reset_cache()

    def tearDown(self):
        ach.save = self._orig_save
        ach.reset_cache()

    def test_migrate_v1_to_v2_backfills_without_loss(self):
        v1 = {
            "v": 1,
            "unlocked": {"first_flight": 123},
            "life": {"total_coins": 400, "powerups_seen": {"magnet": 3}},
        }
        out = ach._migrate(v1)
        self.assertEqual(out["v"], ach._SCHEMA_V)
        self.assertEqual(out["unlocked"], {"first_flight": 123})
        self.assertEqual(out["life"]["total_coins"], 400)        # preserved
        self.assertEqual(out["life"]["total_pillars"], 0)        # back-filled
        self.assertEqual(out["wallet"], {"spent": 0})            # new section
        self.assertEqual(out["inventory"], {"owned": {}, "equipped": {}})
        self.assertEqual(out["mtime"], 0)

    def test_merge_restores_from_blank_local(self):
        # Local lost (blank), cloud holds progress → merge adopts the cloud copy.
        cloud = ach._blank()
        cloud["mtime"] = 500
        cloud["unlocked"] = {"first_flight": 100}
        cloud["life"]["total_coins"] = 900
        cloud["wallet"]["spent"] = 120
        cloud["inventory"]["owned"] = {"hat_gold": 50}
        cloud["inventory"]["equipped"] = {"skin": "macaw_blue"}
        merged = ach._merge(ach._blank(), cloud)
        self.assertEqual(merged["unlocked"], {"first_flight": 100})
        self.assertEqual(merged["life"]["total_coins"], 900)
        self.assertEqual(merged["wallet"]["spent"], 120)
        self.assertEqual(merged["inventory"]["owned"], {"hat_gold": 50})
        self.assertEqual(merged["inventory"]["equipped"], {"skin": "macaw_blue"})

    def test_merge_counters_take_max_no_regression(self):
        a = ach._blank(); a["mtime"] = 10
        a["life"]["total_coins"] = 1000
        a["life"]["powerups_seen"] = {"magnet": 9}
        a["wallet"]["spent"] = 300
        b = ach._blank(); b["mtime"] = 5
        b["life"]["total_coins"] = 200            # older, smaller
        b["life"]["powerups_seen"] = {"magnet": 4, "ghost": 2}
        b["wallet"]["spent"] = 100
        merged = ach._merge(a, b)
        self.assertEqual(merged["life"]["total_coins"], 1000)      # max
        self.assertEqual(merged["life"]["powerups_seen"], {"magnet": 9, "ghost": 2})
        self.assertEqual(merged["wallet"]["spent"], 300)           # max

    def test_merge_unlocked_keeps_earliest_ts_and_unions(self):
        a = {"unlocked": {"x": 100}}
        b = {"unlocked": {"x": 50, "y": 200}}
        merged = ach._merge(a, b)
        self.assertEqual(merged["unlocked"], {"x": 50, "y": 200})

    def test_merge_equipped_is_last_write_wins(self):
        a = ach._blank(); a["mtime"] = 10
        a["inventory"]["owned"] = {"hat_gold": 5}
        a["inventory"]["equipped"] = {"skin": "old"}
        b = ach._blank(); b["mtime"] = 20            # newer → its equipped wins
        b["inventory"]["owned"] = {"cape_red": 7}
        b["inventory"]["equipped"] = {"skin": "new"}
        merged = ach._merge(a, b)
        self.assertEqual(set(merged["inventory"]["owned"]), {"hat_gold", "cape_red"})
        self.assertEqual(merged["inventory"]["equipped"], {"skin": "new"})

    def test_coin_balance_derived_and_floored(self):
        store = ach._blank()
        store["life"]["total_coins"] = 100
        store["wallet"]["spent"] = 30
        self.assertEqual(ach.coin_balance(store), 70)
        # Defensive: spent somehow exceeding earned never goes negative.
        store["wallet"]["spent"] = 250
        self.assertEqual(ach.coin_balance(store), 0)

    def test_spend_coins_guards_and_records(self):
        store = ach._blank()
        store["life"]["total_coins"] = 100
        self.assertFalse(ach.spend_coins(0, store))      # non-positive
        self.assertFalse(ach.spend_coins(1000, store))   # overdraw → no write
        self.assertEqual(store["wallet"]["spent"], 0)
        self.assertTrue(ach.spend_coins(30, store))
        self.assertEqual(store["wallet"]["spent"], 30)
        self.assertEqual(ach.coin_balance(store), 70)
        # No double-spend: a re-pushed merge of the post-spend state is stable.
        merged = ach._merge(store, store)
        self.assertEqual(ach.coin_balance(merged), 70)

    def test_inventory_grant_and_equip(self):
        store = ach._blank()
        self.assertFalse(ach.owns(store, "hat_gold"))
        ach.grant_item("hat_gold", store)
        self.assertTrue(ach.owns(store, "hat_gold"))
        ach.equip("skin", "macaw_blue", store)
        self.assertEqual(store["inventory"]["equipped"]["skin"], "macaw_blue")
        ach.equip("skin", None, store)                   # clear the slot
        self.assertNotIn("skin", store["inventory"]["equipped"])


if __name__ == "__main__":
    unittest.main()
