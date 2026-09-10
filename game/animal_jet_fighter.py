"""Secret JET FIGHTER skin — a RANDOM one of three fighter designs, LOCKED at
unlock.

When the player unlocks the secret jet, ONE of three hand-designed fighters is
rolled and that pick is persisted, so the same jet shows every run rather than
flickering to a new look each launch:

  * STEEL  — gunmetal Steel Raptor (twin delta + twin afterburner)
  * NAVAL  — F-14 "Jolly Rogers" (navy + gold leading-edge rail, twin tails)
  * CHROME — retro polished bare-metal with a single blue spine stripe

The roll happens at PURCHASE/grant time in ``store_data`` (uniform over the
pool) and is written into the saved inventory; this module just reads that
persisted index back and renders it. A surprise once, then yours for keeps.

All three are drawn NOSE-RIGHT, UPRIGHT, with NO baked rotation. The jet pitches
with the flappy arc on its own: the getter passes the bird's velocity tilt
(`Bird.tilt_deg`) straight through to each design's cached getter, which rotates
the sprite — so the nose pitches UP on a flap/jump and gradually noses DOWN as it
falls, exactly like a real fighter riding the arc.

Each design is its own self-contained module (game/animal_jet_*.py) so their
private helpers and palettes never collide; this module imports their getters and
dispatches `skin_jet_fighter` to the locked one. The sub-modules are imported here
directly, so their own `skin_*` ids never register as separate store items.
"""
import random

from game import store_data
from game.animal_jet_steel import get_steel
from game.animal_jet_naval import get_naval
from game.animal_jet_chrome import get_chrome


# The three designs the unlock can roll (uniform). POOL_SIZE is the single
# source of truth for the roll range — store_data reads it back when it locks
# the design at purchase.
_POOL = (get_steel, get_naval, get_chrome)
POOL_SIZE = len(_POOL)

# Bound lazily on first render (and refreshed right after an unlock) from the
# index persisted by store_data — never re-rolled per launch.
_chosen = None


def _apply(idx) -> None:
    global _chosen
    if idx is None or not (0 <= int(idx) < POOL_SIZE):
        # No persisted roll yet (legacy save, or a render before the unlock
        # landed): fall back to a uniform pick so a jet always shows.
        idx = random.randrange(POOL_SIZE)
    _chosen = _POOL[int(idx)]


def sync_from_store() -> None:
    """Lock the look to the index rolled at unlock (persisted in store_data).
    Call right after a fresh purchase so the store preview and the next run
    both show the same jet the player just unlocked."""
    try:
        _apply(store_data.skin_variant("skin_jet_fighter"))
    except Exception:
        _apply(None)


def get_jet_fighter(frame_idx, tilt_deg):
    if _chosen is None:
        sync_from_store()
    return _chosen(frame_idx, tilt_deg)


BUILDERS = {"skin_jet_fighter": get_jet_fighter}
