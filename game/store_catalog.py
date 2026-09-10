"""Store item catalog — pure data, no pygame.

Kept import-light (no pygame, no surface building) so the persistence
layer (game/store_data.py) and the headless unit tests can read prices
and validate inventory without pulling in the rendering stack.

Every entry is ``id -> {name, cost, kind, group}``:

  - ``kind`` is one of CATALOG_KINDS. New categories (pillar/ground/trail/
    boost) slot in without a schema change.
  - ``group`` is one of GROUPS — the store's browsing tab (costume / parrot /
    animal). Purely a UI grouping; the renderer and gacha ignore it.
  - skin ids must each resolve in ``parrot.get_skin_frame``'s dispatch map;
    tests assert that the two stay in sync so a catalog entry can never
    point at a look the renderer can't draw.

``BASE_SKIN`` is the default parrot. It is implicitly owned and never
sold, so it is deliberately absent from CATALOG (the store surfaces it as a
free DEFAULT card in the PARROTS tab).
"""
from __future__ import annotations

BASE_SKIN = "skin_base"

# Default parcel (the kraft-box Pip always carried). Like BASE_SKIN it is
# implicitly owned and never sold — the PARCELS tab surfaces it as a free
# DEFAULT card so the player can always revert.
PARCEL_BASE = "parcel_base"

CATALOG_KINDS = ("skin", "pillar", "ground", "trail", "boost", "parcel")

# Store browsing tabs, in display order.
GROUPS = ("costume", "parrot", "animal", "shoes", "hats", "shades", "parcels")

# Cost ladder is tuned so the first unlock is a goal (a few good runs) rather
# than a side effect of session one: entry ~260, mid ~450-550, premium ~650-800,
# fantasy showpieces ~1200-1500. Coin *earn* is left untouched (gameplay feel);
# the daily reward gives a steady drip toward the higher tiers.
CATALOG: dict[str, dict] = {
    # ── COSTUMES (accessories/restyles on the macaw) ──────────────────────────
    "skin_pirate":      {"name": "PIRATE",      "cost":  280, "kind": "skin", "group": "costume"},
    "skin_cowboy":      {"name": "COWBOY",      "cost":  320, "kind": "skin", "group": "costume"},
    "skin_pharaoh":     {"name": "PHARAOH",     "cost":  380, "kind": "skin", "group": "costume"},
    "skin_crown":       {"name": "CROWN",       "cost":  450, "kind": "skin", "group": "costume"},
    "skin_tophat":      {"name": "GENTLEMAN",   "cost":  520, "kind": "skin", "group": "costume"},
    "skin_ninja":       {"name": "NINJA",       "cost":  560, "kind": "skin", "group": "costume"},
    "skin_viking":      {"name": "VIKING",      "cost":  600, "kind": "skin", "group": "costume"},
    "skin_baseball":    {"name": "BASEBALL",    "cost":  950, "kind": "skin", "group": "costume"},
    "skin_tennis":      {"name": "TENNIS",      "cost": 1000, "kind": "skin", "group": "costume"},
    "skin_wizard":      {"name": "WIZARD",      "cost":  720, "kind": "skin", "group": "costume"},
    "skin_basketball":  {"name": "BASKETBALL",  "cost":  950, "kind": "skin", "group": "costume"},
    "skin_mummy":       {"name": "MUMMY",       "cost": 1100, "kind": "skin", "group": "costume"},
    "skin_astronaut":   {"name": "ASTRONAUT",   "cost": 2600, "kind": "skin", "group": "costume"},
    "skin_pilot":       {"name": "CAPTAIN",     "cost": 2200, "kind": "skin", "group": "costume"},
    "skin_skeleton":    {"name": "SKELETON",    "cost":  300, "kind": "skin", "group": "parrot"},
    "skin_zombie":      {"name": "ZOMBIE",      "cost":  480, "kind": "skin", "group": "parrot"},
    "skin_disco":    {"name": "DISCO",     "cost": 800, "kind": "skin", "group": "parrot"},

    # ── PARROTS (full-body species recolours) ─────────────────────────────────
    "skin_bluegold":  {"name": "BLUE MACAW",  "cost": 280, "kind": "skin", "group": "parrot"},
    "skin_amazon":    {"name": "AMAZON",      "cost": 300, "kind": "skin", "group": "parrot"},
    "skin_sunconure": {"name": "SUN CONURE",  "cost": 360, "kind": "skin", "group": "parrot"},
    "skin_hyacinth":  {"name": "HYACINTH",    "cost": 450, "kind": "skin", "group": "parrot"},
    "skin_cockatoo":  {"name": "COCKATOO",    "cost": 520, "kind": "skin", "group": "parrot"},
    "skin_lorikeet":  {"name": "LORIKEET",    "cost": 600, "kind": "skin", "group": "parrot"},
    "skin_prism":     {"name": "PRISM",        "cost": 1400, "kind": "skin", "group": "parrot"},
    "skin_thorncrest": {"name": "THORNCREST",   "cost": 1700, "kind": "skin", "group": "parrot"},
    "skin_embermoth": {"name": "EMBERMOTH",    "cost": 1900, "kind": "skin", "group": "parrot"},
    "skin_aurora":    {"name": "AURORA MACAW", "cost": 2800, "kind": "skin", "group": "parrot"},
    "skin_moonbloom": {"name": "MOONBLOOM",    "cost": 3200, "kind": "skin", "group": "parrot"},
    "skin_tempest":   {"name": "TEMPEST CONDOR", "cost": 3600, "kind": "skin", "group": "parrot"},
    # SECRET tier — masked as ??? in the store until bought (price still shown).
    "skin_binky":     {"name": "BINKY",       "cost": 6000, "kind": "skin", "group": "parrot", "secret": True},
    "skin_chrome":    {"name": "CHROME MACAW", "cost": 9500, "kind": "skin", "group": "parrot", "secret": True},

    # ── ANIMALS (from-scratch creatures) ──────────────────────────────────────
    # Common — entry-level, accessible within a couple of runs.
    "skin_bee":      {"name": "BEE",       "cost": 200,  "kind": "skin", "group": "animal"},
    "skin_owl":      {"name": "OWL",       "cost": 280,  "kind": "skin", "group": "animal"},
    "skin_toucan":   {"name": "TOUCAN",    "cost": 340,  "kind": "skin", "group": "animal"},
    # Rare — comfortable multi-session grind, evenly spaced.
    "skin_penguin":  {"name": "PENGUIN",   "cost": 420,  "kind": "skin", "group": "animal"},
    "skin_bat":      {"name": "BAT",       "cost": 490,  "kind": "skin", "group": "animal"},
    "skin_flamingo": {"name": "FLAMINGO",  "cost": 560,  "kind": "skin", "group": "animal"},
    "skin_pufferfish":   {"name": "PUFFERFISH",   "cost": 640,  "kind": "skin", "group": "animal"},
    "skin_chameleon":    {"name": "CHAMELEON",    "cost": 720,  "kind": "skin", "group": "animal"},
    # Epic — aspirational ladder; each unlock feels like an event.
    "skin_eagle":    {"name": "EAGLE",     "cost": 900,  "kind": "skin", "group": "animal"},
    "skin_red_panda":    {"name": "RED PANDA",    "cost": 1100, "kind": "skin", "group": "animal"},
    "skin_sugar_glider": {"name": "SUGAR GLIDER", "cost": 1400, "kind": "skin", "group": "animal"},
    "skin_mantis_shrimp": {"name": "MANTIS SHRIMP", "cost": 1800, "kind": "skin", "group": "animal"},
    "skin_dragon":   {"name": "DRAGON",    "cost": 2300, "kind": "skin", "group": "animal"},
    # Legendary — prestige tier; kitsune anchors the visible legendary goal.
    "skin_kitsune":      {"name": "KITSUNE",      "cost": 3500, "kind": "skin", "group": "animal"},
    # Secret legendary — masked ??? until purchased, price still shown.
    "skin_paper_plane":  {"name": "PAPER PLANE",   "cost": 5000,  "kind": "skin", "group": "animal", "secret": True},
    # Mystery SUN — rolls a random one of two sun designs at unlock, then locks to it.
    "skin_sun":          {"name": "SUN",           "cost": 6000,  "kind": "skin", "group": "animal", "secret": True},
    "skin_pinata_burro":  {"name": "BURRO PIÑATA",  "cost": 7000,  "kind": "skin", "group": "animal", "secret": True},
    "skin_pinata_cactus": {"name": "CACTUS PIÑATA", "cost": 8000,  "kind": "skin", "group": "animal", "secret": True},
    "skin_toaster":      {"name": "FLYING TOASTER", "cost": 9000,  "kind": "skin", "group": "animal", "secret": True},
    "skin_pinata_parrot": {"name": "PARROT PIÑATA", "cost": 10500, "kind": "skin", "group": "animal", "secret": True},
    "skin_jet_fighter":  {"name": "JET FIGHTER",   "cost": 12000, "kind": "skin", "group": "animal", "secret": True},

    # ── SHOES (stylized procedural sneaker/sandal homages Pip wears) ───────────
    # Priced on desirability: sandals/slides cheap, classics mid, hype premium —
    # then a fantastical epic→legendary tier (gel, light-up, winged, rocket) that
    # gets wilder the higher it climbs, so the tab spans the whole rarity ladder.
    "skin_shoe_flipflops":  {"name": "FLIP-FLOPS",  "cost": 240, "kind": "skin", "group": "shoes"},
    "skin_shoe_poolslides": {"name": "POOL SLIDES", "cost": 300, "kind": "skin", "group": "shoes"},
    "skin_shoe_courtgreen": {"name": "COURT GREEN", "cost": 420, "kind": "skin", "group": "shoes"},
    "skin_shoe_canvashigh": {"name": "CANVAS HIGH", "cost": 460, "kind": "skin", "group": "shoes"},
    "skin_shoe_checkerslip": {"name": "CHECKER SLIP", "cost": 480, "kind": "skin", "group": "shoes"},
    "skin_shoe_shelltoe":   {"name": "SHELL TOE",   "cost": 540, "kind": "skin", "group": "shoes"},
    "skin_shoe_airflyer":   {"name": "AIR FLYER",   "cost": 620, "kind": "skin", "group": "shoes"},
    "skin_shoe_airbubble":  {"name": "AIR BUBBLE",  "cost": 680, "kind": "skin", "group": "shoes"},
    "skin_shoe_boostknit":  {"name": "BOOST KNIT",  "cost": 760, "kind": "skin", "group": "shoes"},
    "skin_shoe_megadad":    {"name": "MEGA DAD",    "cost": 780, "kind": "skin", "group": "shoes"},
    "skin_shoe_retro1":     {"name": "RETRO 1",     "cost": 850, "kind": "skin", "group": "shoes"},
    "skin_shoe_jellycore":  {"name": "JELLYCORE",   "cost": 1200, "kind": "skin", "group": "shoes"},
    "skin_shoe_neoncircuit": {"name": "NEON CIRCUIT", "cost": 1800, "kind": "skin", "group": "shoes"},
    "skin_shoe_wingboots":  {"name": "WING BOOTS",  "cost": 3200, "kind": "skin", "group": "shoes"},
    "skin_shoe_afterburner": {"name": "AFTERBURNER", "cost": 4800, "kind": "skin", "group": "shoes"},

    # ── HATS (stylized procedural headwear Pip wears, NY cap as the hero) ──────
    # Priced on desirability: novelty/casual cheap, classics mid-high, the
    # seasonal Santa and the signature NY cap premium.
    "skin_hat_partyhat":  {"name": "PARTY HAT",     "cost": 220, "kind": "skin", "group": "hats"},
    "skin_hat_strawhat":  {"name": "STRAW HAT",     "cost": 260, "kind": "skin", "group": "hats"},
    "skin_hat_beanie":    {"name": "BEANIE",        "cost": 300, "kind": "skin", "group": "hats"},
    "skin_hat_beret":     {"name": "BERET",         "cost": 320, "kind": "skin", "group": "hats"},
    "skin_hat_buckethat": {"name": "BUCKET HAT",    "cost": 360, "kind": "skin", "group": "hats"},
    "skin_hat_flatcap":   {"name": "FLAT CAP",      "cost": 380, "kind": "skin", "group": "hats"},
    "skin_hat_propeller": {"name": "PROPELLER CAP", "cost": 420, "kind": "skin", "group": "hats"},
    "skin_hat_trucker":   {"name": "TRUCKER CAP",   "cost": 440, "kind": "skin", "group": "hats"},
    "skin_hat_snapback":  {"name": "SNAPBACK",      "cost": 460, "kind": "skin", "group": "hats"},
    "skin_hat_gradcap":   {"name": "GRAD CAP",      "cost": 500, "kind": "skin", "group": "hats"},
    "skin_hat_chef":      {"name": "CHEF TOQUE",    "cost": 520, "kind": "skin", "group": "hats"},
    "skin_hat_bowler":    {"name": "BOWLER",        "cost": 560, "kind": "skin", "group": "hats"},
    "skin_hat_fedora":    {"name": "FEDORA",        "cost": 600, "kind": "skin", "group": "hats"},
    "skin_hat_sombrero":  {"name": "SOMBRERO",      "cost": 640, "kind": "skin", "group": "hats"},
    "skin_hat_santa":     {"name": "SANTA HAT",     "cost": 700, "kind": "skin", "group": "hats"},
    "skin_hat_nycap":     {"name": "NY CAP",        "cost": 850, "kind": "skin", "group": "hats"},

    # ── SHADES (eyewear Pip wears over his eyes; NO SHADES removes them) ───────
    # A mix of classic/fun/techy/quirky lenses. NO SHADES is the cheapest — the
    # bare-eyed look — then a value ladder up to the premium cyber visor.
    "skin_shades_none":    {"name": "NO SHADES",    "cost": 120, "kind": "skin", "group": "shades"},
    "skin_shades_nerd":    {"name": "NERD SPECS",   "cost": 180, "kind": "skin", "group": "shades"},
    "skin_shades_round":   {"name": "ROUND SHADES", "cost": 220, "kind": "skin", "group": "shades"},
    "skin_shades_heart":   {"name": "HEART SHADES", "cost": 240, "kind": "skin", "group": "shades"},
    "skin_shades_star":    {"name": "STAR SHADES",  "cost": 260, "kind": "skin", "group": "shades"},
    "skin_shades_black":   {"name": "BLACK SHADES", "cost": 300, "kind": "skin", "group": "shades"},
    "skin_shades_white":   {"name": "WHITE RETRO",  "cost": 320, "kind": "skin", "group": "shades"},
    "skin_shades_3d":      {"name": "3D GLASSES",   "cost": 360, "kind": "skin", "group": "shades"},
    "skin_shades_pixel":   {"name": "PIXEL SHADES", "cost": 400, "kind": "skin", "group": "shades"},
    "skin_shades_ski":     {"name": "SKI GOGGLES",  "cost": 440, "kind": "skin", "group": "shades"},
    "skin_shades_monocle": {"name": "MONOCLE",      "cost": 480, "kind": "skin", "group": "shades"},
    "skin_shades_cyber":   {"name": "CYBER VISOR",  "cost": 560, "kind": "skin", "group": "shades"},

    # ── PARCELS (the gift Pip carries below him; PARCEL_BASE is the free default) ─
    # Priced across the rarity bands so the tab is a proper pyramid, not a wall of
    # commons: everyday mail/containers are COMMON (<400), the drinks + sports
    # collectibles are RARE (400-799), the treasures are EPIC (800-2499), and the
    # showpieces are LEGENDARY (>=2500). NO PARCEL is the cheapest — the empty-
    # handed look (mirrors NO SHADES); it only hides the sprite, Pip's parcel
    # hitbox is unchanged so difficulty holds.
    # COMMON — everyday mail + basic containers
    "parcel_none":      {"name": "NO PARCEL",      "cost": 120,  "kind": "parcel", "group": "parcels"},
    "parcel_airmail":   {"name": "AIRMAIL",        "cost": 200,  "kind": "parcel", "group": "parcels"},
    "parcel_love":      {"name": "LOVE LETTER",    "cost": 240,  "kind": "parcel", "group": "parcels"},
    "parcel_postmark":  {"name": "POSTMARK",       "cost": 260,  "kind": "parcel", "group": "parcels"},
    "parcel_takeout":   {"name": "TAKEOUT PAIL",   "cost": 290,  "kind": "parcel", "group": "parcels"},
    "parcel_plastic":   {"name": "WATER BOTTLE",   "cost": 320,  "kind": "parcel", "group": "parcels"},
    "parcel_picnic":    {"name": "PICNIC BASKET",  "cost": 370,  "kind": "parcel", "group": "parcels"},
    # RARE — drinks + sports collectibles
    "parcel_tumbler":   {"name": "TUMBLER",        "cost": 440,  "kind": "parcel", "group": "parcels"},
    "parcel_coconut":   {"name": "COCONUT",        "cost": 500,  "kind": "parcel", "group": "parcels"},
    "parcel_soccer":    {"name": "SOCCER BALL",    "cost": 560,  "kind": "parcel", "group": "parcels"},
    "parcel_basketball": {"name": "BASKETBALL",    "cost": 600,  "kind": "parcel", "group": "parcels"},
    "parcel_tennis":    {"name": "TENNIS BALL",    "cost": 640,  "kind": "parcel", "group": "parcels"},
    "parcel_baseball":  {"name": "BASEBALL",       "cost": 690,  "kind": "parcel", "group": "parcels"},
    "parcel_football":  {"name": "FOOTBALL",       "cost": 740,  "kind": "parcel", "group": "parcels"},
    # EPIC — premium treasures
    "parcel_coin":      {"name": "GOLD COIN",      "cost": 900,  "kind": "parcel", "group": "parcels"},
    "parcel_diamond":   {"name": "DIAMOND",        "cost": 1500, "kind": "parcel", "group": "parcels"},
    "parcel_chest":     {"name": "TREASURE CHEST", "cost": 2200, "kind": "parcel", "group": "parcels"},
    # LEGENDARY — showpieces (the two secret premiums are masked ??? until bought)
    "parcel_minipip":   {"name": "MINI PIP",       "cost": 3500, "kind": "parcel", "group": "parcels"},
    # FINEST WHISKEY is a single mystery parcel: buying it rolls one of four
    # drams (decanter / scotch / bourbon / cask) at unlock, locked for good.
    "parcel_whiskey":   {"name": "FINEST WHISKEY", "cost": 9000, "kind": "parcel", "group": "parcels", "secret": True},
    "parcel_snowglobe": {"name": "SNOWGLOBE",      "cost": 9500, "kind": "parcel", "group": "parcels", "secret": True},
}


def exists(item_id: str) -> bool:
    return item_id in CATALOG


def name(item_id: str) -> str:
    return CATALOG[item_id]["name"]


def cost(item_id: str) -> int:
    return CATALOG[item_id]["cost"]


def kind(item_id: str) -> str:
    return CATALOG[item_id]["kind"]


def ids_of_kind(k: str) -> list[str]:
    return [i for i, v in CATALOG.items() if v["kind"] == k]


def group(item_id: str) -> str:
    return CATALOG[item_id].get("group", "costume")


def is_secret(item_id: str) -> bool:
    """Secret items render masked (??? + a "?" icon, price still shown) in the
    store until bought, then reveal. Opt-in per entry; absent means visible."""
    return CATALOG.get(item_id, {}).get("secret", False)


# Rarity tiers by price — the ladder the store draws as each card's outline
# colour (common→gray, rare→blue, epic→purple, legendary→orange). Intrinsic to
# the item (unlike the transient equipped highlight). The bands are chosen so
# every tab spans several tiers and the legendary band is reserved for the
# genuine showpieces (the dearest animals, parcels, and the secret flyers).
RARITIES = ("common", "rare", "epic", "legendary")
_RARITY_BANDS = ((500, "common"), (900, "rare"), (2000, "epic"))


def rarity(item_id: str) -> str:
    """The price-tier rarity of an item. Free defaults (BASE_SKIN / PARCEL_BASE,
    absent from CATALOG) read as common."""
    c = CATALOG.get(item_id, {}).get("cost", 0)
    for ceiling, tier in _RARITY_BANDS:
        if c < ceiling:
            return tier
    return "legendary"


def ids_of_group(g: str) -> list[str]:
    """Catalog ids in a store tab (costume / parrot / animal), in catalog order."""
    return [i for i, v in CATALOG.items() if v.get("group", "costume") == g]


def skin_ids() -> list[str]:
    return ids_of_kind("skin")


def cosmetic_ids() -> list[str]:
    """Everything the Prize Machine can hand out — every kind except the
    consumable boost lane (boosts are bought deliberately, never rolled)."""
    return [i for i, v in CATALOG.items() if v["kind"] != "boost"]
