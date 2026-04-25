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

MUSHROOM_R         = 14
MUSHROOM_CHANCE    = 0.14  # rebranded: chance to spawn *any* power-up
MUSHROOM_COOLDOWN  = 5.5
TRIPLE_DURATION    = 8.0
MAGNET_DURATION    = 5.0
MAGNET_RADIUS      = 82.0
SLOWMO_DURATION    = 3.0
SLOWMO_SCALE       = 0.5
COMBO_WINDOW       = 1.6

# Spawn weights for the three power-up kinds. Must sum to anything — they're
# normalized at pick time.
POWERUP_WEIGHTS    = (
    ("triple", 60),
    ("slowmo", 25),
    ("magnet", 15),
)

SAVE_FILE = "skybit_save.json"
SCORES_FILE = "skybit_scores.json"
