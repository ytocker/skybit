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

COIN_R             = 11

# Coin-rush: every Nth pipe gets a wider gap filled with a dense coin arc.
COIN_RUSH_INTERVAL = 15
COIN_RUSH_GAP_BOOST = 1.30
COIN_RUSH_COINS    = 14

POWERUP_R          = 14    # collision + footprint radius for every power-up
POWERUP_CHANCE     = 0.14  # chance to spawn a power-up after a pipe gate
POWERUP_COOLDOWN   = 5.5   # min seconds between power-up spawns
TRIPLE_DURATION    = 10.0
MAGNET_DURATION    = 10.0
MAGNET_RADIUS      = 82.0
SLOWMO_DURATION    = 10.0
SLOWMO_SCALE       = 0.7
KFC_DURATION       = 10.0
GHOST_DURATION     = 10.0
GROW_DURATION      = 10.0
GROW_SCALE         = 1.5

# Spawn weights for power-up kinds. Must sum to anything — they're
# normalized at pick time.
POWERUP_WEIGHTS    = (
    ("triple", 1),
    ("slowmo", 1),
    ("magnet", 1),
    ("kfc",    1),
    ("ghost",  1),
    ("grow",   1),
)

SAVE_FILE = "skybit_save.json"
SCORES_FILE = "skybit_scores.json"
