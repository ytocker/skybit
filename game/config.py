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
SCORES_FILE = "skybit_scores.json"   # local fallback only — see LEADERBOARD_* below

# ── Global leaderboard (shared across all players) ──────────────────────────
# Paste your JSONBin.io credentials here. Until both URLs and the key are
# filled in, storage.load_scores() falls back silently to an empty list and
# storage.save_scores() is a no-op — gameplay is unaffected.
#   1. Sign up free at https://jsonbin.io
#   2. Create a bin seeded with: { "scores": [] }
#   3. Paste the bin id below (URL form is shown).
#   4. Paste the X-Master-Key.
LEADERBOARD_BIN_ID = ""                                   # e.g. "65f0a1b9c0e..."
LEADERBOARD_KEY    = ""                                   # X-Master-Key header value
LEADERBOARD_GET_URL = (
    f"https://api.jsonbin.io/v3/b/{LEADERBOARD_BIN_ID}/latest"
    if LEADERBOARD_BIN_ID else ""
)
LEADERBOARD_PUT_URL = (
    f"https://api.jsonbin.io/v3/b/{LEADERBOARD_BIN_ID}"
    if LEADERBOARD_BIN_ID else ""
)
LEADERBOARD_TIMEOUT_S = 2.0   # don't freeze the title screen on a dead network
