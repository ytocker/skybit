W, H   = 360, 640
FPS    = 60
TITLE  = "Skybit"

GROUND_Y   = 595
CEILING_Y  = 0

GRAVITY   = 1600.0
FLAP_V    = -520.0
MAX_FALL  = 700.0

SCROLL_BASE = 160.0
SCROLL_MAX  = 290.0

PIPE_W        = 58
PIPE_SPACING  = 280
GAP_START     = 170
GAP_MIN       = 115

BIRD_X = 90
BIRD_R = 14

# Pip carries the parcel for the entire run. The parcel's collision
# footprint is a second circle below the bird; pillars touching that
# circle are also lethal.
PARCEL_R          = 9    # forgiving (parcel sprite is 22 px so r=11 would catch its corners)
PARCEL_Y_OFFSET   = 12   # px below bird-centre to parcel-centre (matches intro composition)

COIN_R             = 13

# Coin-rush: every Nth pipe gets a wider gap filled with a dense coin arc.
COIN_RUSH_INTERVAL = 15
COIN_RUSH_GAP_BOOST = 1.30
COIN_RUSH_COINS    = 14

POWERUP_R          = 14    # collision + footprint radius for every power-up
POWERUP_CHANCE     = 0.30  # chance to spawn a power-up after a pipe gate
POWERUP_COOLDOWN   = 5.5   # min seconds between power-up spawns
TRIPLE_DURATION    = 8.0
MAGNET_DURATION    = 8.0
MAGNET_RADIUS      = 82.0
SLOWMO_DURATION    = 8.0
SLOWMO_SCALE       = 0.7
KFC_DURATION       = 8.0
GHOST_DURATION     = 8.0
GROW_DURATION      = 8.0
GROW_SCALE         = 1.5
REVERSE_DURATION   = 8.0

# Spawn weights for power-up kinds. Must sum to anything — they're
# normalized at pick time. `surprise` resolves at pickup-time to one of
# the six "real" kinds chosen at random (see World._on_powerup).
# `reverse` is intentionally excluded — the implementation is kept in
# place but the power-up doesn't spawn or resolve from a surprise box.
# To re-enable: add ("reverse", 1) below AND restore "reverse" in the
# random.choice() inside World._on_powerup.
POWERUP_WEIGHTS    = (
    ("triple",   1),
    ("slowmo",   1),
    ("magnet",   1),
    ("kfc",      1),
    ("ghost",    1),
    ("grow",     1),
    ("surprise", 1),
)

SAVE_FILE = "skybit_save.json"
SCORES_FILE = "skybit_scores.json"
