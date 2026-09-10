"""
Achievements — meta-progression for Skybit.

A run never *earns* an achievement mid-flight; the whole roster is evaluated
once at end-of-run against the finished ``World`` (zero per-frame cost). Unlock
state + lifetime counters persist locally on both build targets:

  * native  — read-modify-written under the ``"achievements"`` key of
              ``skybit_save.json`` (siblings such as a future high-score blob
              are preserved).
  * browser — a single JSON string in ``localStorage["skybit_ach"]`` via two
              actions on the closure-private ``window.__sk`` dispatcher
              (``ach_load`` / ``ach_save``), probed exactly like the
              leaderboard bridge so a missing dispatcher degrades to "nothing
              unlocked" instead of crashing.

Every ``save()`` also mirrors the blob to a Supabase ``profiles`` row keyed by
the device's anonymous UUID (web only); ``sync_cloud()`` pulls + merges that
backup once at startup, so a lost/cleared ``localStorage`` blob is restored as
long as the device UUID survived. Storage stays behind ``load()`` / ``save()``.

The blob also carries forward-looking sections so a future store and a
player-statistics screen are purely additive:

  * ``wallet`` — the spendable coin balance is *derived*, never stored
    (``life["total_coins"]`` collected − ``wallet["spent"]``), so it can't
    desync or be double-spent across a cloud restore.
  * ``inventory`` — owned + equipped store items.

Cloud-merge reconciles each section by its kind — grow-only maps union (earliest
timestamp wins), monotonic counters take the element-wise max, mutable selections
resolve last-write-wins by ``mtime``. See ``_merge``.

Design rules:
  * Achievement ``id`` strings are PERMANENT. Renaming or reusing one orphans
    a player's saved unlock — only ever ADD new ids.
  * Adding achievements needs no migration (an id absent from ``unlocked`` is
    simply locked). ``store["v"]`` guards structural changes to the lifetime
    block; ``_migrate`` back-fills missing keys.
  * Every read/write is wrapped so a corrupt save degrades gracefully.
"""
from __future__ import annotations

import sys
import json
import time
from collections import OrderedDict
from dataclasses import dataclass

from game.config import (
    SAVE_FILE, LOTTERY_TIERS,
    RAIN_START_PILLAR, SNOW_START_PILLAR,
)

_IS_BROWSER = sys.platform == "emscripten"

# Nested under this key in skybit_save.json so unrelated save data can coexist.
_ACH_KEY = "achievements"
# localStorage key for the browser path.
_WEB_KEY = "skybit_ach"
# Schema version of the persisted blob. v2 added mtime + wallet + inventory.
_SCHEMA_V = 2

# Jackpot coin delta, pulled from the live lottery table so a re-tune of the
# top tier keeps the "hit the jackpot" achievement honest.
_JACKPOT_DELTA = next((d for (label, _w, d) in LOTTERY_TIERS
                       if label == "JACKPOT"), 100)


# ── Categories ────────────────────────────────────────────────────────────────

CAT_PROGRESS   = "Flight Log"      # pillars / score / day-cycle milestones
CAT_RICHES     = "Riches"          # coin totals (run + lifetime)
CAT_POWERUPS   = "Power Player"    # power-up usage + collection
CAT_STORM      = "Stormchaser"     # nerve, endurance, weather biomes
CAT_SKATER     = "Skater"          # skateboard buff
CAT_ODDITIES   = "Oddities"        # off-beat clock / UI / whimsy unlocks
CAT_DEDICATION = "Dedication"      # long-haul loyalty + grind milestones
CAT_SECRET     = "Mysteries"       # hidden late-game / secret unlocks

CATEGORY_ORDER = (
    CAT_PROGRESS, CAT_RICHES, CAT_POWERUPS, CAT_STORM, CAT_SKATER,
    CAT_ODDITIES, CAT_DEDICATION, CAT_SECRET,
)

# Wall of Shame — anti-achievements for blooper-reel play. Disjoint ids + their
# own categories so they live on a separate tab; they share the flat unlocked{}
# map and the one evaluate_run loop. Every roast punches at the play, not the
# player, and is out-grindable.
CAT_SHAME_BLOOPER = "Blooper Reel"        # per-run pratfalls
CAT_SHAME_WASTED  = "Wasted Opportunity"  # squandered a gift
CAT_SHAME_COSMIC  = "Cosmic Joke"         # eerily specific / uncanny detections
CAT_SHAME_LOWS    = "Lifetime Lows"       # cumulative low-lights

SHAME_CATEGORY_ORDER = (CAT_SHAME_BLOOPER, CAT_SHAME_WASTED,
                        CAT_SHAME_COSMIC, CAT_SHAME_LOWS)


@dataclass(frozen=True)
class Achievement:
    """One unlockable. ``stat`` + ``scope`` describe what is measured;
    ``target`` is the threshold (``1`` for a boolean flag)."""
    id: str            # PERMANENT — never rename or reuse
    title: str
    desc: str          # requirement / flavour; hidden+locked renders "???"
    category: str
    icon_key: str      # routes to a procedural badge drawer
    stat: str          # see _run_value / _life_value resolvers
    target: int = 1
    scope: str = "run"     # "run" (per-run World stat) | "life" (cumulative)
    hidden: bool = False   # locked row shows "???" until unlocked


# ── Roster (source of truth, ordered by category) ─────────────────────────────
#
# Every entry is derivable from signals the World already tracks — no new
# per-frame instrumentation. "Derived" stats (distinct_powerups, lottery_jackpot,
# magnet_life) are computed by the resolvers below.

ACHIEVEMENTS: tuple[Achievement, ...] = (
    # ── Flight Log ────────────────────────────────────────────────────────
    Achievement("first_flight", "First Delivery",
                "Clear your very first pillar.",
                CAT_PROGRESS, "pillar", "pillars_passed", 1),
    Achievement("pillar_25", "Courier in Training",
                "Pass 25 pillars in one run.",
                CAT_PROGRESS, "pillar", "pillars_passed", 25),
    Achievement("pillar_50", "Route Veteran",
                "Pass 50 pillars in one run.",
                CAT_PROGRESS, "pillar", "pillars_passed", 50),
    Achievement("pillar_100", "Centurion of the Sky",
                "Pass 100 pillars in one run.",
                CAT_PROGRESS, "pillar", "pillars_passed", 100),
    Achievement("score_100", "Triple Digits",
                "Reach a score of 100.",
                CAT_PROGRESS, "score", "score", 100),
    Achievement("score_500", "High Flyer",
                "Reach a score of 500.",
                CAT_PROGRESS, "score", "score", 500),
    Achievement("day_complete", "Round the Clock",
                "Survive a full day-into-night cycle.",
                CAT_PROGRESS, "day", "cycles_completed", 1),
    Achievement("day_three", "Three-Day Weekend",
                "Survive three full day cycles in one run.",
                CAT_PROGRESS, "day", "cycles_completed", 3),
    Achievement("frequent_flyer", "Frequent Flyer",
                "Pass 1,000 pillars all-time.",
                CAT_PROGRESS, "pillar", "total_pillars", 1000, scope="life"),
    Achievement("globetrotter", "Globetrotter",
                "Pass 10,000 pillars all-time.",
                CAT_PROGRESS, "pillar", "total_pillars", 10000, scope="life"),
    Achievement("sky_legend", "Sky Legend",
                "Pass 250 pillars in a single run.",
                CAT_PROGRESS, "sky_legend", "pillars_passed", 250),
    Achievement("quad_digits", "Quadruple Digits",
                "Reach a score of 1,000.",
                CAT_PROGRESS, "quad_digits", "score", 1000),
    Achievement("weeklong_bender", "Weeklong Bender",
                "Survive seven full day cycles in one run.",
                CAT_PROGRESS, "weeklong_bender", "cycles_completed", 7),
    Achievement("purist", "Purist",
                "Reach 100 pillars in one run without touching a power-up.",
                CAT_PROGRESS, "purist", "purist", 1),

    # ── Riches ────────────────────────────────────────────────────────────
    Achievement("coin_25_run", "Pocket Change",
                "Collect 25 coins in one run.",
                CAT_RICHES, "coin", "coin_count", 25),
    Achievement("coin_100_run", "Coin Run",
                "Collect 100 coins in one run.",
                CAT_RICHES, "coin", "coin_count", 100),
    Achievement("coins_500_life", "Coin Collector",
                "Collect 500 coins all-time.",
                CAT_RICHES, "coin", "total_coins", 500, scope="life"),
    Achievement("coins_5000_life", "Coin Vault",
                "Collect 5,000 coins all-time.",
                CAT_RICHES, "coin", "total_coins", 5000, scope="life"),
    Achievement("coin_tycoon", "Coin Tycoon",
                "Collect 25,000 coins all-time.",
                CAT_RICHES, "coin", "total_coins", 25000, scope="life"),
    Achievement("midas", "Midas Touch",
                "Collect 100,000 coins all-time.",
                CAT_RICHES, "coin", "total_coins", 100000, scope="life"),
    Achievement("millionaire", "Millionaire",
                "Collect 1,000,000 coins all-time.",
                CAT_RICHES, "millionaire", "total_coins", 1000000, scope="life"),

    # ── Power Player ──────────────────────────────────────────────────────
    Achievement("first_powerup", "Power Up!",
                "Grab your first power-up.",
                CAT_POWERUPS, "powerup", "distinct_powerups", 1),
    Achievement("powerup_sampler", "Buffet",
                "Use 4 different power-ups in a single run.",
                CAT_POWERUPS, "powerup", "distinct_powerups", 4),
    Achievement("magnet_life", "Animal Magnetism",
                "Trigger the magnet 15 times all-time.",
                CAT_POWERUPS, "magnet", "magnet_life", 15, scope="life"),
    Achievement("powerup_collector", "Gotta Grab 'Em All",
                "Discover 10 different power-ups all-time.",
                CAT_POWERUPS, "powerup", "distinct_powerups", 10, scope="life"),
    Achievement("greasy_fingers", "Finger Lickin'",
                "Go into KFC mode.",
                CAT_POWERUPS, "kfc", "pu:kfc", 1),
    Achievement("power_hungry", "Power Hungry",
                "Collect 100 power-ups all-time.",
                CAT_POWERUPS, "powerup", "total_powerups", 100, scope="life"),
    Achievement("power_addict", "Power Addict",
                "Collect 500 power-ups all-time.",
                CAT_POWERUPS, "powerup", "total_powerups", 500, scope="life"),
    Achievement("power_overwhelming", "Power Overwhelming",
                "Collect 2,500 power-ups all-time.",
                CAT_POWERUPS, "power_overwhelming", "total_powerups", 2500, scope="life"),
    Achievement("overachiever", "Overachiever",
                "Collect 20 power-ups in a single run.",
                CAT_POWERUPS, "overachiever", "run_powerups", 20),
    Achievement("kitchen_sink", "Kitchen Sink",
                "Use all six power-ups in a single run.",
                CAT_POWERUPS, "kitchen_sink", "distinct_powerups", 6),
    Achievement("overloaded", "Overloaded",
                "Have three power-ups active at the same time.",
                CAT_POWERUPS, "overloaded", "max_active_powerups", 3),
    Achievement("bullet_time", "Bullet Time",
                "Pass 10 pillars during a single Slow-Mo.",
                CAT_POWERUPS, "bullet_time", "max_pillars_in_slowmo", 10),
    Achievement("ghost_rider", "Ghost Rider",
                "Phase through 8 pillars during a single Ghost.",
                CAT_POWERUPS, "ghost_rider", "max_pillars_in_ghost", 8),
    Achievement("regifted", "Regifted",
                "Have a Surprise Box roll you the same power-up twice in a run.",
                CAT_POWERUPS, "regifted", "surprise_repeat", 1),

    # ── Stormchaser ───────────────────────────────────────────────────────
    Achievement("near_miss_5", "Close Shave",
                "Squeak past 5 pillars in one run.",
                CAT_STORM, "nerve", "near_misses", 5),
    Achievement("near_miss_15", "Threadneedle",
                "Squeak past 15 pillars in one run.",
                CAT_STORM, "nerve", "near_misses", 15),
    Achievement("marathon", "Long Haul",
                "Stay airborne for two minutes straight.",
                CAT_STORM, "clock", "time_alive", 120),
    Achievement("storm_rider", "Storm Rider",
                "Fly into the rain.",
                CAT_STORM, "storm", "pillars_passed", RAIN_START_PILLAR),
    Achievement("snowbird", "Snowbird",
                "Reach the snow squall.",
                CAT_STORM, "storm", "pillars_passed", SNOW_START_PILLAR),
    Achievement("flap_life", "Tireless Wings",
                "Flap 5,000 times all-time.",
                CAT_STORM, "wing", "total_flaps", 5000, scope="life"),
    Achievement("headbanger", "Headbanger",
                "Bonk the ceiling 10 times in one run.",
                CAT_STORM, "ceiling", "ceiling_hits", 10),
    Achievement("hard_head", "Hard Head",
                "Bonk the ceiling 200 times all-time.",
                CAT_STORM, "ceiling", "total_ceiling", 200, scope="life"),
    Achievement("iron_wings", "Iron Wings",
                "Flap 50,000 times all-time.",
                CAT_STORM, "wing", "total_flaps", 50000, scope="life"),
    Achievement("endless", "Endless",
                "Stay airborne for ten minutes straight.",
                CAT_STORM, "endless", "time_alive", 600),

    # ── Skater ────────────────────────────────────────────────────────────
    Achievement("board_meeting", "Board Meeting",
                "Catch a skateboard.",
                CAT_SKATER, "skate", "pu:skateboard", 1),
    Achievement("sponsored", "Sponsored",
                "Catch 10 skateboards all-time.",
                CAT_SKATER, "skate", "puseen:skateboard", 10, scope="life"),
    Achievement("going_pro", "Going Pro",
                "Catch 50 skateboards all-time.",
                CAT_SKATER, "skate", "puseen:skateboard", 50, scope="life"),
    Achievement("full_combo", "Full Combo",
                "Land all four trick types in one run.",
                CAT_SKATER, "skate", "trick_types", 4),
    Achievement("trickster", "Trickster",
                "Land 50 skateboard tricks all-time.",
                CAT_SKATER, "skate", "total_tricks", 50, scope="life"),
    Achievement("trick_legend", "Trick Legend",
                "Land 500 skateboard tricks all-time.",
                CAT_SKATER, "skate", "total_tricks", 500, scope="life"),
    Achievement("grinder", "Grinder",
                "Ride the rail cart 10 times all-time.",
                CAT_SKATER, "rail", "puseen:rail", 10, scope="life"),
    Achievement("rail_baron", "Rail Baron",
                "Ride the rail cart 50 times all-time.",
                CAT_SKATER, "rail", "puseen:rail", 50, scope="life"),

    # ── Oddities (hidden whimsy) ──────────────────────────────────────────
    Achievement("read_fine_print", "Read the Fine Print",
                "Scroll all the way to the bottom of the Hall of Fame.",
                CAT_ODDITIES, "read_fine_print", "manual", 1, hidden=True),
    Achievement("morbid_curiosity", "Morbid Curiosity",
                "Pay a visit to the Hall of Shame.",
                CAT_ODDITIES, "morbid_curiosity", "manual", 1, hidden=True),
    Achievement("are_you_still_there", "Are You Still There?",
                "Leave the bird idling on the menu for five minutes.",
                CAT_ODDITIES, "are_you_still_there", "manual", 1, hidden=True),
    Achievement("after_hours", "Night Owl",
                "Take flight after midnight.",
                CAT_ODDITIES, "after_hours", "clock_night", 1, hidden=True),
    Achievement("early_bird", "Early Bird",
                "Take flight before 6 a.m.",
                CAT_ODDITIES, "early_bird", "clock_dawn", 1, hidden=True),
    Achievement("leap_of_faith", "Leap of Faith",
                "Fly on February 29th.",
                CAT_ODDITIES, "leap_of_faith", "clock_leapday", 1, hidden=True),
    Achievement("auld_lang_syne", "Auld Lang Syne",
                "Fly on New Year's Day.",
                CAT_ODDITIES, "auld_lang_syne", "clock_newyear", 1, hidden=True),
    Achievement("lucky_sevens", "Lucky Sevens",
                "End a run on a score of exactly 777.",
                CAT_ODDITIES, "lucky_sevens", "lucky_777", 1, hidden=True),
    Achievement("palindrome", "Palindrome",
                "End a run on a palindromic score.",
                CAT_ODDITIES, "palindrome", "palindrome_score", 1, hidden=True),

    # ── Dedication (loyalty + grind) ──────────────────────────────────────
    Achievement("the_completionist", "The Completionist",
                "Earn every other Hall of Fame badge.",
                CAT_DEDICATION, "the_completionist", "manual", 1),
    Achievement("many_happy_returns", "Many Happy Returns",
                "Come back and fly a year after your very first flight.",
                CAT_DEDICATION, "many_happy_returns", "returned_after_year", 1,
                scope="life"),
    Achievement("creature_of_habit", "Creature of Habit",
                "Play on seven different days.",
                CAT_DEDICATION, "creature_of_habit", "distinct_days", 7,
                scope="life"),
    Achievement("the_grind", "The Grind",
                "Play 100 runs all-time.",
                CAT_DEDICATION, "the_grind", "total_runs", 100, scope="life"),
    Achievement("never_say_die", "Never Say Die",
                "Rack up 1,000 crashes all-time (you never gave up).",
                CAT_DEDICATION, "never_say_die", "total_runs", 1000, scope="life"),

    # ── Mysteries (hidden) ────────────────────────────────────────────────
    Achievement("made_a_wish", "Three Wishes",
                "Summon the genie and make a wish.",
                CAT_SECRET, "genie", "pu:genie", 1, hidden=True),
    Achievement("knighted", "Knighted",
                "Survive a fatal hit under a knight's guard.",
                CAT_SECRET, "knight", "pu:knight", 1, hidden=True),
    Achievement("treasure_hunter", "X Marks the Spot",
                "Crack open a cycle-finale treasure chest.",
                CAT_SECRET, "treasure", "pu:treasure", 1, hidden=True),
    Achievement("jackpot", "Jackpot!",
                "Hit the lottery's top tier.",
                CAT_SECRET, "lottery", "lottery_jackpot", 1, hidden=True),
    Achievement("rail_rider", "Off the Rails",
                "Ride the rail cart.",
                CAT_SECRET, "rail", "pu:rail", 1, hidden=True),
    Achievement("poisoned", "Be Careful What You Wish For",
                "Discover the genie's nastier surprise.",
                CAT_SECRET, "poison", "pu:poison", 1, hidden=True),
)

# ── Wall of Shame roster (anti-achievements) ──────────────────────────────────
# Most read free per-run signals; a few read a small death-moment snapshot the
# World captures in _die() (death_ghost / death_kfc / died_early_phase /
# _lottery_pulled / max_flaps_per_sec). All thresholds tunable; all escapable.

SHAME_ACHIEVEMENTS: tuple[Achievement, ...] = (
    # ── Blooper Reel (per-run) ────────────────────────────────────────────
    Achievement("goose_egg", "The Goose Egg",
                "End a run with zero points and zero coins — nothing at all.",
                CAT_SHAME_BLOOPER, "goose_egg", "goose_egg", 1),
    Achievement("icarus", "The Icarus Award",
                "Die on or before the very first pillar.",
                CAT_SHAME_BLOOPER, "icarus", "pillar1_death", 1),
    Achievement("hummingbird", "The Hummingbird",
                "Panic-flap 10+ times in a single second.",
                CAT_SHAME_BLOOPER, "hummingbird", "max_flaps_per_sec", 10),
    Achievement("denial", "Denial",
                "Die with Ghost active — you phased around the gap into a wall.",
                CAT_SHAME_BLOOPER, "denial", "died_ghost", 1),
    Achievement("kfc_incident", "The KFC Incident",
                "Die in KFC fry-skin mode. Finger lickin' fatal.",
                CAT_SHAME_BLOOPER, "kfc_incident", "died_kfc", 1),
    Achievement("so_close", "So Close, So Far",
                "Graze 8 pillars by a hair in one run, then die anyway.",
                CAT_SHAME_BLOOPER, "so_close", "near_misses", 8),
    Achievement("lottery_loser", "The Lottery Loser",
                "Pull the lottery slot, then die before it ever mattered.",
                CAT_SHAME_BLOOPER, "lottery_loser", "lottery_pulled", 1),
    Achievement("the_49er", "The 49er",
                "Die on pillar 49 — one short of the genie at 50.",
                CAT_SHAME_BLOOPER, "the_49er", "pillar_49", 1),
    Achievement("night_owl", "Night Owl's Revenge",
                "Die in the first 5 seconds of a new biome phase.",
                CAT_SHAME_BLOOPER, "night_owl", "early_phase_death", 1),
    Achievement("bullet_bystander", "Bullet Time Bystander",
                "Die with Slow-Mo active. The world slowed down and you still "
                "couldn't dodge.",
                CAT_SHAME_BLOOPER, "bullet_bystander", "died_slowmo", 1),
    Achievement("cursed", "Cursed",
                "Die to the genie's poison wish, with no knight to save you.",
                CAT_SHAME_BLOOPER, "cursed", "died_poison", 1),
    Achievement("board_to_death", "Board to Death",
                "Die mid skateboard grind or trick.",
                CAT_SHAME_BLOOPER, "board_to_death", "died_skateboard", 1),
    Achievement("lightning_rod", "The Lightning Rod",
                "Get struck by lightning, then die before the scorch clears.",
                CAT_SHAME_BLOOPER, "lightning_rod", "died_lightning", 1),
    Achievement("party_foul", "Party Foul",
                "Die during the Day-Complete celebration — mid-party.",
                CAT_SHAME_BLOOPER, "party_foul", "died_celebration", 1),

    # ── Wasted Opportunity (squandered a gift) ────────────────────────────
    Achievement("rich_reckless", "Rich and Reckless",
                "Die with a Magnet active having collected zero coins during it.",
                CAT_SHAME_WASTED, "rich_reckless", "magnet_zero_coins", 1),
    Achievement("coin_blind", "Coin Blind",
                "Fly through a whole Coin Rush and grab fewer than 3 coins.",
                CAT_SHAME_WASTED, "coin_blind", "coin_blind", 1),
    Achievement("wish_unspent", "Wish Unspent",
                "Grab the genie lamp but die before collecting a single wish.",
                CAT_SHAME_WASTED, "wish_unspent", "wish_unspent", 1),

    # ── Cosmic Joke (eerily specific detections) ──────────────────────────
    Achievement("ninety_nine", "Ninety-Nine Problems",
                "Die on a score of exactly 99 — one shy of triple digits.",
                CAT_SHAME_COSMIC, "ninety_nine", "score_99", 1),
    Achievement("groundhog_day", "Groundhog Day",
                "Die on the exact same pillar two runs in a row. The sky remembers.",
                CAT_SHAME_COSMIC, "groundhog_day", "repeat_pillar_streak", 2,
                scope="life"),
    Achievement("stat_impossible", "Statistically Impossible",
                "End a run where score, pillars, and coins are all prime numbers.",
                CAT_SHAME_COSMIC, "stat_impossible", "all_prime", 1),
    Achievement("three_am", "The 3 AM Shift",
                "Play a run between 3 and 4 a.m. local time. Go to bed.",
                CAT_SHAME_COSMIC, "three_am", "clock_3am", 1),
    Achievement("same_time_tomorrow", "Same Time Tomorrow",
                "Start a run at the same clock-minute on two different days.",
                CAT_SHAME_COSMIC, "same_time_tomorrow", "same_minute_two_days", 1,
                scope="life"),

    # ── Lifetime Lows (cumulative) ────────────────────────────────────────
    Achievement("the_scrooge", "The Scrooge",
                "Fly past 5,000 coins all-time. They're still out there.",
                CAT_SHAME_LOWS, "the_scrooge", "coins_missed_life", 5000, scope="life"),
    Achievement("early_checkout", "Early Checkout",
                "End 25 runs all-time in under 3 seconds.",
                CAT_SHAME_LOWS, "early_checkout", "sub3_deaths", 25, scope="life"),
    Achievement("snake_bit", "Snake Bit",
                "Die to poison 5 times all-time. The genie really doesn't like you.",
                CAT_SHAME_LOWS, "snake_bit", "poison_deaths", 5, scope="life"),
    Achievement("lightning_magnet", "Lightning Magnet",
                "Take 25 lightning strikes all-time.",
                CAT_SHAME_LOWS, "lightning_magnet", "lightning_hits", 25,
                scope="life"),
)

# Both walls share one flat unlocked{} map + one evaluate loop; the two BY_CAT
# maps keep them on separate tabs.
ALL_ACHIEVEMENTS: tuple[Achievement, ...] = ACHIEVEMENTS + SHAME_ACHIEVEMENTS
SHAME_IDS: frozenset = frozenset(a.id for a in SHAME_ACHIEVEMENTS)

# Derived lookups, built once.
BY_ID: dict[str, Achievement] = {a.id: a for a in ALL_ACHIEVEMENTS}

BY_CAT: "OrderedDict[str, list[Achievement]]" = OrderedDict(
    (cat, [a for a in ACHIEVEMENTS if a.category == cat])
    for cat in CATEGORY_ORDER
)
BY_CAT_SHAME: "OrderedDict[str, list[Achievement]]" = OrderedDict(
    (cat, [a for a in SHAME_ACHIEVEMENTS if a.category == cat])
    for cat in SHAME_CATEGORY_ORDER
)
# Combined view so category_progress resolves a category on either wall.
BY_CAT_ALL: "OrderedDict[str, list[Achievement]]" = OrderedDict(
    list(BY_CAT.items()) + list(BY_CAT_SHAME.items())
)


def is_shame(ach_id: str) -> bool:
    """True for Wall-of-Shame ids (drives the tarnished badge tone)."""
    return ach_id in SHAME_IDS


# ── Persistence ───────────────────────────────────────────────────────────────

def _as_int(v) -> int:
    """Coerce a possibly-missing / possibly-string JSON value to int (default 0)."""
    try:
        return int(v or 0)
    except (TypeError, ValueError):
        return 0


def _blank() -> dict:
    """A fresh, fully-formed save blob."""
    return {
        "v": _SCHEMA_V,
        "mtime": 0,                     # last local-write unix ts (LWW clock)
        "unlocked": {},                 # id -> unlock unix timestamp
        "life": {
            "total_runs": 0,
            "total_coins": 0,
            "total_pillars": 0,
            "total_flaps": 0,
            "total_time": 0,
            "best_cycles": 0,
            "total_tricks": 0,          # skateboard tricks landed, all-time
            "total_ceiling": 0,         # ceiling bonks, all-time
            "powerups_seen": {},        # kind -> lifetime pickup count
            # Wall-of-Shame lifetime tallies (also feed future saddled titles).
            "scoreless_deaths": 0,      # runs ending 0 score & 0 coins
            "pillar1_deaths": 0,        # runs dying on/before pillar 1
            "sub3_deaths": 0,           # runs ending in under 3 seconds
            "coins_missed_life": 0,     # coins flown past, all-time
            "last_death_pillar": -1,    # pillar # of the previous death
            "repeat_pillar_streak": 0,  # consecutive deaths on the same pillar
            "poison_deaths": 0,         # runs ended by the genie's poison wish
            "lightning_hits": 0,        # storm-jolt strikes taken, all-time
            # Same-minute-two-days roast: HH:MM -> earliest YYYY-MM-DD it was
            # played, plus a sticky flag once the same minute recurs on a new day.
            "play_minutes": {},
            "same_minute_two_days": 0,
            # Dedication (loyalty) tallies.
            "first_launch": 0,          # unix ts of the very first run
            "distinct_days": 0,         # count of distinct local calendar days played
            "last_play_date": "",       # most recent YYYY-MM-DD played (distinct-day guard)
        },
        # Spendable balance is DERIVED (see coin_balance), never stored, so a
        # cloud restore can't resurrect spent coins. Only the monotonic spent
        # total lives here.
        "wallet": {"spent": 0},         # lifetime coins spent in the store
        "inventory": {
            "owned": {},                # store item id -> first-owned unix ts
            "equipped": {},             # slot -> equipped item id (LWW)
        },
    }


def _migrate(store: dict) -> dict:
    """Back-fill any keys a newer build expects onto an older save. Additive
    only — never drops a player's unlocked ids, owned items, or counters."""
    if not isinstance(store, dict):
        return _blank()
    base = _blank()
    inv = store.get("inventory") or {}
    out = {
        "v": _SCHEMA_V,
        "mtime": _as_int(store.get("mtime")),
        "unlocked": dict(store.get("unlocked") or {}),
        "life": {**base["life"], **(store.get("life") or {})},
        "wallet": {**base["wallet"], **(store.get("wallet") or {})},
        "inventory": {
            "owned": dict(inv.get("owned") or {}),
            "equipped": dict(inv.get("equipped") or {}),
        },
    }
    seen = out["life"].get("powerups_seen")
    if not isinstance(seen, dict):
        out["life"]["powerups_seen"] = {}
    pm = out["life"].get("play_minutes")
    if not isinstance(pm, dict):
        out["life"]["play_minutes"] = {}
    return out


# Native local-JSON (mirrors leaderboard._load_local / _save_local).

def _load_native() -> dict:
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            doc = json.load(f)
        return _migrate(doc.get(_ACH_KEY))
    except Exception:
        return _blank()


def _save_native(store: dict) -> None:
    try:
        doc = {}
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                doc = json.load(f) or {}
        except Exception:
            doc = {}
        if not isinstance(doc, dict):
            doc = {}
        doc[_ACH_KEY] = store
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(doc, f)
    except Exception:
        pass


# Browser localStorage via window.__sk (probed like leaderboard._resolve).

def _web_dispatcher():
    try:
        import platform as _p  # type: ignore
        win = getattr(_p, "window", None)
        return getattr(win, "__sk", None) if win is not None else None
    except Exception:
        return None


def _load_web() -> dict:
    try:
        sk = _web_dispatcher()
        if sk is None:
            return _blank()
        raw = sk("ach_load", _WEB_KEY)
        if not raw:
            return _blank()
        return _migrate(json.loads(str(raw)))
    except Exception:
        return _blank()


def _save_web(store: dict) -> None:
    try:
        sk = _web_dispatcher()
        if sk is None:
            return
        sk("ach_save", json.dumps(store, separators=(",", ":")), _WEB_KEY)
    except Exception:
        pass


# Module-level cached store so the screen + engine share one in-memory copy.
_store: "dict | None" = None


def load() -> dict:
    """Return the (cached) save blob, loading from disk/localStorage once."""
    global _store
    if _store is None:
        _store = _load_web() if _IS_BROWSER else _load_native()
    return _store


def save(store: "dict | None" = None) -> None:
    """Persist the store (defaults to the cached one). Stamps the local-write
    clock and, on the web build, mirrors the blob to the Supabase backup."""
    global _store
    if store is not None:
        _store = store
    if _store is None:
        return
    _store["mtime"] = int(time.time())
    if _IS_BROWSER:
        _save_web(_store)
        _cloud_push(_store)
    else:
        _save_native(_store)


def reset_cache() -> None:
    """Drop the in-memory copy (tests / forced reload)."""
    global _store
    _store = None


# ── Cloud backup (web only) ────────────────────────────────────────────────────
#
# A Supabase ``profiles`` row per device (keyed by the anon skybit_device_id
# UUID, attached JS-side) holds a mirror of the blob. Push is fire-and-forget on
# every save; pull + merge runs once at startup via sync_cloud(). This is a
# backup + foundation for later account sync, NOT a cure for a full storage wipe
# (which erases the device UUID too, orphaning the row).

def _cloud_push(store: dict) -> None:
    """Upsert the blob to the Supabase backup. Never throws into the caller."""
    if not _IS_BROWSER:
        return
    try:
        sk = _web_dispatcher()
        if sk is None:
            return
        sk("profile_push", json.dumps(store, separators=(",", ":")))
    except Exception:
        pass


async def _cloud_pull() -> "dict | None":
    """Fetch this device's cloud blob (migrated) or None. Polls the bridge the
    same way leaderboard.fetch_top10 does."""
    if not _IS_BROWSER:
        return None
    try:
        import asyncio
        sk = _web_dispatcher()
        if sk is None:
            return None
        sk("profile_pull")
        tries = 0
        while tries < 120:                  # 120 * 0.05s = 6s deadline
            v = sk("profile_pull_done")
            if v is not None:
                raw = str(v)
                return _migrate(json.loads(raw)) if raw else None
            tries += 1
            await asyncio.sleep(0.05)
    except Exception:
        return None
    return None


def _union_earliest(a: dict, b: dict) -> dict:
    """Merge two grow-only ``id -> timestamp`` maps, keeping the earliest ts."""
    out = dict(a)
    for k, ts in b.items():
        if k not in out or _as_int(ts) < _as_int(out[k]):
            out[k] = ts
    return out


def _max_counters(a: dict, b: dict) -> dict:
    """Element-wise max over two monotonic-counter maps."""
    return {k: max(_as_int(a.get(k)), _as_int(b.get(k)))
            for k in set(a) | set(b)}


def _merge(a: dict, b: dict) -> dict:
    """Reconcile two profile blobs by section kind (see the module docstring and
    ADDENDUM 6 policy table): grow-only maps union on earliest ts, monotonic
    counters take element-wise max, mutable selections (equipped) resolve
    last-write-wins by ``mtime``. Order-independent for everything but the LWW
    fields, which favour the more recently written blob."""
    a = _migrate(a)
    b = _migrate(b)
    a_newer = _as_int(a.get("mtime")) >= _as_int(b.get("mtime"))

    _skip = ("powerups_seen", "play_minutes")
    a_life = {k: v for k, v in a["life"].items() if k not in _skip}
    b_life = {k: v for k, v in b["life"].items() if k not in _skip}
    life = _max_counters(a_life, b_life)
    life["powerups_seen"] = _max_counters(a["life"]["powerups_seen"],
                                          b["life"]["powerups_seen"])
    # play_minutes is a HH:MM -> earliest-date map, not a counter: union the two
    # keeping the earliest date string per minute so cross-device history survives.
    pm: dict = dict(a["life"].get("play_minutes") or {})
    for hm, date in (b["life"].get("play_minutes") or {}).items():
        if hm not in pm or str(date) < str(pm[hm]):
            pm[hm] = date
    life["play_minutes"] = pm

    return {
        "v": _SCHEMA_V,
        "mtime": max(_as_int(a.get("mtime")), _as_int(b.get("mtime"))),
        "unlocked": _union_earliest(a["unlocked"], b["unlocked"]),
        "life": life,
        "wallet": _max_counters(a["wallet"], b["wallet"]),
        "inventory": {
            "owned": _union_earliest(a["inventory"]["owned"],
                                     b["inventory"]["owned"]),
            "equipped": dict((a if a_newer else b)["inventory"]["equipped"]),
        },
    }


async def sync_cloud() -> None:
    """Web-only: reconcile the local profile with its Supabase backup once at
    startup. Pulls the cloud copy, merges it into the cached store, and persists
    the merged result (which re-pushes it). No-op when the bridge is absent or no
    cloud copy exists — the local profile is authoritative on its own."""
    global _store
    if not _IS_BROWSER:
        return
    cloud = await _cloud_pull()
    if cloud is None:
        return
    _store = _merge(load(), cloud)
    save(_store)


# ── Store / wallet / inventory API (data + merge here; catalog lives in config) ─
#
# The store's item catalog (ids, prices, art) is intentionally NOT stored in the
# profile — it belongs in config.py + a procedural icon module like power-ups, so
# re-pricing or re-skinning is a code change, not a save migration. The profile
# holds only the per-player state: spent total + owned/equipped item ids.

def coin_balance(store: "dict | None" = None) -> int:
    """Spendable coins = lifetime coins collected − lifetime coins spent. Derived
    (never stored) so it can't desync or be double-spent across a cloud restore."""
    if store is None:
        store = load()
    earned = _as_int((store.get("life") or {}).get("total_coins"))
    spent = _as_int((store.get("wallet") or {}).get("spent"))
    return max(0, earned - spent)


def spend_coins(n: int, store: "dict | None" = None) -> bool:
    """Spend ``n`` coins if affordable: bump the lifetime spent counter and
    persist. Returns False and writes nothing on an overdraw or non-positive n."""
    if store is None:
        store = load()
    n = int(n)
    if n <= 0 or coin_balance(store) < n:
        return False
    wallet = store.setdefault("wallet", {"spent": 0})
    wallet["spent"] = _as_int(wallet.get("spent")) + n
    save(store)
    return True


def owns(store: dict, item_id: str) -> bool:
    return item_id in ((store.get("inventory") or {}).get("owned") or {})


def grant_item(item_id: str, store: "dict | None" = None) -> None:
    """Mark a store item owned (idempotent) and persist."""
    if store is None:
        store = load()
    inv = store.setdefault("inventory", {"owned": {}, "equipped": {}})
    owned = inv.setdefault("owned", {})
    if item_id not in owned:
        owned[item_id] = int(time.time())
        save(store)


def equip(slot: str, item_id: "str | None", store: "dict | None" = None) -> None:
    """Set (or clear, with ``item_id=None``) the equipped item for a slot."""
    if store is None:
        store = load()
    inv = store.setdefault("inventory", {"owned": {}, "equipped": {}})
    equipped = inv.setdefault("equipped", {})
    if item_id is None:
        equipped.pop(slot, None)
    else:
        equipped[slot] = item_id
    save(store)


def lifetime_stats(store: "dict | None" = None) -> dict:
    """Read-only snapshot of the lifetime counters for the stats screen."""
    if store is None:
        store = load()
    return dict(store.get("life") or {})


# ── Stat resolvers ────────────────────────────────────────────────────────────

def _is_prime(n: int) -> bool:
    """Plain primality test for the Statistically Impossible roast (small n)."""
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0:
        return False
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    return True


def _has_jackpot(world) -> bool:
    """Scan the proof ledger for a lottery event that landed the top tier."""
    proof = getattr(world, "_proof", None)
    if proof is None:
        return False
    try:
        for (_t, dscore, kind) in proof.events_tuple():
            if kind == "lottery" and int(dscore) >= _JACKPOT_DELTA:
                return True
    except Exception:
        return False
    return False


def _run_value(world, ach: Achievement) -> int:
    """Current value of a run-scope achievement's stat for this finished run."""
    s = ach.stat
    pp = getattr(world, "powerups_picked", {}) or {}
    if s == "distinct_powerups":
        return sum(1 for v in pp.values() if v > 0)
    if s == "lottery_jackpot":
        return 1 if _has_jackpot(world) else 0
    if s == "trick_types":
        return len(getattr(world, "tricks_landed_types", ()) or ())
    if s.startswith("pu:"):
        return int(pp.get(s[3:], 0) or 0)
    # ── Wall of Shame run-scope triggers ──────────────────────────────────
    if s == "goose_egg":
        return 1 if (int(getattr(world, "score", 0) or 0) == 0
                     and int(getattr(world, "coin_count", 0) or 0) == 0) else 0
    if s == "pillar1_death":
        return 1 if int(getattr(world, "pillars_passed", 0) or 0) <= 1 else 0
    if s == "pillar_49":
        return 1 if int(getattr(world, "pillars_passed", 0) or 0) == 49 else 0
    if s == "died_ghost":
        return 1 if getattr(world, "death_ghost", False) else 0
    if s == "died_kfc":
        return 1 if getattr(world, "death_kfc", False) else 0
    if s == "lottery_pulled":
        return 1 if getattr(world, "_lottery_pulled", False) else 0
    if s == "early_phase_death":
        return 1 if getattr(world, "died_early_phase", False) else 0
    if s == "died_slowmo":
        return 1 if getattr(world, "death_slowmo", False) else 0
    if s == "died_poison":
        return 1 if getattr(world, "death_poison", False) else 0
    if s == "died_skateboard":
        return 1 if getattr(world, "death_skateboard", False) else 0
    if s == "died_lightning":
        return 1 if getattr(world, "death_lightning", False) else 0
    if s == "died_celebration":
        return 1 if getattr(world, "death_celebration", False) else 0
    if s == "magnet_zero_coins":
        return 1 if getattr(world, "death_magnet_zero", False) else 0
    if s == "coin_blind":
        return 1 if getattr(world, "coin_blind", False) else 0
    if s == "wish_unspent":
        return 1 if getattr(world, "death_wish_pending", False) else 0
    if s == "score_99":
        return 1 if int(getattr(world, "score", 0) or 0) == 99 else 0
    if s == "all_prime":
        sc = int(getattr(world, "score", 0) or 0)
        pl = int(getattr(world, "pillars_passed", 0) or 0)
        cn = int(getattr(world, "coin_count", 0) or 0)
        return 1 if (_is_prime(sc) and _is_prime(pl) and _is_prime(cn)) else 0
    # ── Hall-of-Fame run-scope derivations ────────────────────────────────
    if s == "run_powerups":
        return sum(int(v or 0) for v in pp.values())
    if s == "purist":
        return 1 if (int(getattr(world, "pillars_passed", 0) or 0) >= 100
                     and sum(int(v or 0) for v in pp.values()) == 0) else 0
    if s == "lucky_777":
        return 1 if int(getattr(world, "score", 0) or 0) == 777 else 0
    if s == "palindrome_score":
        sc = str(int(getattr(world, "score", 0) or 0))
        return 1 if (len(sc) >= 2 and sc == sc[::-1]) else 0
    if s.startswith("clock_"):
        lt = time.localtime()
        if s == "clock_night":
            return 1 if 0 <= lt.tm_hour < 4 else 0
        if s == "clock_dawn":
            return 1 if 4 <= lt.tm_hour < 6 else 0
        if s == "clock_3am":
            return 1 if lt.tm_hour == 3 else 0
        if s == "clock_leapday":
            return 1 if (lt.tm_mon == 2 and lt.tm_mday == 29) else 0
        if s == "clock_newyear":
            return 1 if (lt.tm_mon == 1 and lt.tm_mday == 1) else 0
    if s == "manual":
        return 0                      # unlocked only via unlock(); never auto
    # max_flaps_per_sec, near_misses, … fall through to the plain world attr.
    return int(getattr(world, s, 0) or 0)


def _life_value(store: dict, ach: Achievement) -> int:
    """Current value of a life-scope achievement's stat from the save blob."""
    life = store.get("life", {}) or {}
    seen = life.get("powerups_seen", {}) or {}
    s = ach.stat
    if s == "distinct_powerups":
        return sum(1 for v in seen.values() if v > 0)
    if s == "magnet_life":
        return int(seen.get("magnet", 0) or 0) + int(seen.get("megamagnet", 0) or 0)
    if s == "total_powerups":
        return sum(int(v or 0) for v in seen.values())
    if s.startswith("puseen:"):
        return int(seen.get(s[7:], 0) or 0)
    if s == "returned_after_year":
        fl = int(life.get("first_launch", 0) or 0)
        return 1 if (fl and (int(time.time()) - fl) >= 365 * 86400) else 0
    if s == "distinct_days":
        return int(life.get("distinct_days", 0) or 0)
    return int(life.get(s, 0) or 0)


def current_value(store: dict, ach: Achievement) -> "int | None":
    """Value to show on a locked progress bar. Only life-scope achievements
    expose live progress (per-run bests aren't persisted); run-scope returns
    ``None`` so the screen omits the bar."""
    if ach.scope == "life":
        return _life_value(store, ach)
    return None


# ── End-of-run engine ─────────────────────────────────────────────────────────

def _accumulate(store: dict, world) -> None:
    """Fold the just-finished run into the persistent lifetime counters."""
    life = store["life"]
    life["total_runs"] = int(life.get("total_runs", 0)) + 1
    # Dedication: stamp the first-ever launch + tally distinct calendar days.
    if not life.get("first_launch"):
        life["first_launch"] = int(time.time())
    today = time.strftime("%Y-%m-%d", time.localtime())
    if life.get("last_play_date") != today:
        life["distinct_days"] = int(life.get("distinct_days", 0) or 0) + 1
        life["last_play_date"] = today
    life["total_coins"] = int(life.get("total_coins", 0)) + int(getattr(world, "coin_count", 0) or 0)
    life["total_pillars"] = int(life.get("total_pillars", 0)) + int(getattr(world, "pillars_passed", 0) or 0)
    life["total_flaps"] = int(life.get("total_flaps", 0)) + int(getattr(world, "flap_count", 0) or 0)
    life["total_time"] = int(life.get("total_time", 0)) + int(getattr(world, "time_alive", 0) or 0)
    life["best_cycles"] = max(int(life.get("best_cycles", 0)),
                              int(getattr(world, "cycles_completed", 0) or 0))
    life["total_tricks"] = int(life.get("total_tricks", 0)) + int(getattr(world, "tricks_landed", 0) or 0)
    life["total_ceiling"] = int(life.get("total_ceiling", 0)) + int(getattr(world, "ceiling_hits", 0) or 0)
    seen = life.setdefault("powerups_seen", {})
    for kind, n in (getattr(world, "powerups_picked", {}) or {}).items():
        if n:
            seen[kind] = int(seen.get(kind, 0)) + int(n)

    # Wall-of-Shame lifetime tallies. _accumulate runs once per finished run
    # (a death), never on a quit, so these never punish disengagement.
    score = int(getattr(world, "score", 0) or 0)
    coin_count = int(getattr(world, "coin_count", 0) or 0)
    pillars = int(getattr(world, "pillars_passed", 0) or 0)
    if score == 0 and coin_count == 0:
        life["scoreless_deaths"] = int(life.get("scoreless_deaths", 0)) + 1
    if pillars <= 1:
        life["pillar1_deaths"] = int(life.get("pillar1_deaths", 0)) + 1
    if float(getattr(world, "time_alive", 0) or 0) < 3.0:
        life["sub3_deaths"] = int(life.get("sub3_deaths", 0)) + 1
    life["coins_missed_life"] = int(life.get("coins_missed_life", 0)) + max(
        0, int(getattr(world, "coins_spawned", 0) or 0) - coin_count)
    if pillars == int(life.get("last_death_pillar", -1)):
        life["repeat_pillar_streak"] = int(life.get("repeat_pillar_streak", 0)) + 1
    else:
        life["repeat_pillar_streak"] = 1
    life["last_death_pillar"] = pillars
    if getattr(world, "death_poison", False):
        life["poison_deaths"] = int(life.get("poison_deaths", 0)) + 1
    life["lightning_hits"] = int(life.get("lightning_hits", 0)) + int(
        getattr(world, "_lightning_strikes_run", 0) or 0)

    # Same-minute-two-days: remember the earliest calendar day each HH:MM was
    # played; the flag sticks once that minute recurs on a different day.
    hm = time.strftime("%H:%M", time.localtime())
    pm = life.get("play_minutes")
    if not isinstance(pm, dict):
        pm = life["play_minutes"] = {}
    prev = pm.get(hm)
    if prev is None:
        pm[hm] = today
    elif prev != today:
        life["same_minute_two_days"] = 1


def evaluate_run(world, store: "dict | None" = None) -> list[str]:
    """Evaluate the whole roster against a finished run. Accumulates lifetime
    counters, unlocks any newly-earned achievements, persists once, and returns
    the list of newly-unlocked ids (in roster order) for the unlock toast."""
    if store is None:
        store = load()
    _accumulate(store, world)

    unlocked = store["unlocked"]
    now = int(time.time())
    newly: list[str] = []
    for ach in ALL_ACHIEVEMENTS:
        if ach.id in unlocked:
            continue
        value = _run_value(world, ach) if ach.scope == "run" else _life_value(store, ach)
        if value >= ach.target:
            unlocked[ach.id] = now
            newly.append(ach.id)

    # The Completionist unlocks once every OTHER Fame badge is earned. Check
    # after the loop so a run that completes the set flips it in the same pass.
    if _check_completionist(store) and "the_completionist" not in newly:
        newly.append("the_completionist")

    save(store)
    return newly


def _check_completionist(store: dict) -> bool:
    """Unlock ``the_completionist`` when every OTHER Hall-of-Fame badge is held.
    Returns True if it was newly flipped by this call."""
    unlocked = store.get("unlocked") or {}
    if "the_completionist" in unlocked:
        return False
    fame_ids = [a.id for a in ACHIEVEMENTS if a.id != "the_completionist"]
    if fame_ids and all(fid in unlocked for fid in fame_ids):
        unlocked["the_completionist"] = int(time.time())
        return True
    return False


def unlock(ach_id: str, store: "dict | None" = None) -> bool:
    """Directly unlock an event/UI achievement (manual-stat ones). Returns True
    if newly unlocked."""
    if store is None:
        store = load()
    if ach_id in store["unlocked"]:
        return False
    store["unlocked"][ach_id] = int(time.time())
    _check_completionist(store)
    save(store)
    return True


# ── Read helpers for the screen ───────────────────────────────────────────────

def is_unlocked(store: dict, ach_id: str) -> bool:
    return ach_id in (store.get("unlocked") or {})


def unlocked_count() -> int:
    store = load()
    return len(store.get("unlocked") or {})


def category_progress(store: dict, category: str) -> "tuple[int, int]":
    """(unlocked, total) for a category's section header (either wall)."""
    items = BY_CAT_ALL.get(category, [])
    got = sum(1 for a in items if is_unlocked(store, a.id))
    return got, len(items)


def unlocked_signature(store: dict) -> tuple:
    """Stable key for the screen's render cache — changes only when the set of
    unlocked ids changes."""
    return tuple(sorted((store.get("unlocked") or {}).keys()))
