"""
Values duplicated from game/ to keep the dashboard subtree decoupled.

Why not import: the dashboard runs in a different process, on a different
runtime (Streamlit Cloud), and may be deployed independently. A stray
import of game/ would drag pygame into the deploy and explode on import.
Cost of duplication is two integers and a list — refresh manually if the
game changes them.
"""

# game/_plausibility.py:42 — the game's own acceptance ceiling. Rows
# above this never make it into a legitimate run, so we drop them before
# any chart sees them. Matched to the game (was 10_000, which silently
# discarded legitimate 10k–100k telemetry that the game itself accepts;
# the in-game *leaderboard display* filter is a separate concern).
MAX_PLAUSIBLE_SCORE = 100_000

# game/world.py:101 — keys present in the powerups jsonb. Order matches
# the in-game pickup-rate weights for display consistency. "reverse" is
# implementation-intact-but-disabled per CLAUDE.md so will be ~always 0;
# we drop it from charts but keep it here for completeness in case the
# rule changes.
POWERUP_KEYS = (
    "triple",
    "magnet",
    "slowmo",
    "kfc",
    "ghost",
    "grow",
    "reverse",
    "surprise",
)

POWERUP_KEYS_ACTIVE = tuple(k for k in POWERUP_KEYS if k != "reverse")

# Friendlier labels for the dashboard. "slowmo" -> "Slow-Mo", etc.
POWERUP_LABELS = {
    "triple":   "Triple",
    "magnet":   "Magnet",
    "slowmo":   "Slow-Mo",
    "kfc":      "KFC",
    "ghost":    "Ghost",
    "grow":     "Grow",
    "reverse":  "Reverse",
    "surprise": "Surprise",
}
