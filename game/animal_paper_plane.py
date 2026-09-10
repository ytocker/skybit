"""Secret PAPER PLANE skin — a RANDOM one of four folded-paper designs.

When the player flies the secret paper plane, the look is rolled at random from
four hand-designed folds, so it feels like a little surprise rather than a fixed
skin:

  * DART      — crisp white printer-paper razor dart (deep charcoal keel fold)
  * GLIDER    — broad manila wide-wing keel glider
  * NOTEBOOK  — folded blue-ruled loose-leaf (two blue rules + a red margin)
  * NEWSPRINT — sunday-comic fold with a red "POW!" halftone burst

Each design is its own self-contained module (game/animal_pp_*.py) so their
private helpers and palettes never collide; this module just imports their
getters and dispatches `skin_paper_plane` to one of them. The pick is made once
per launch (re-roll via ``reroll()``), so the look stays stable across frames in
a session — no per-frame flicker — and varies between sessions.

Contract: `BUILDERS = {"skin_paper_plane": get_paper_plane}` where the getter is
the cached `(frame_idx, tilt_deg) -> Surface` of the chosen design (64×84, mass
centred at (32,44), nose-forward), merged into the animal registry by
game/animal_skins.py. The 4 sub-modules are imported here directly, so their own
`skin_*` ids never register as separate store items.
"""
import random

from game.animal_pp_dart import get_dart_classic
from game.animal_pp_glider import get_glider_wide
from game.animal_pp_notebook import get_notebook
from game.animal_pp_news import get_newsprint


# The four designs the player can roll (uniform). Stunt Fold and the old
# dollar-bill dart were dropped from the pool per design review.
_POOL = (get_dart_classic, get_glider_wide, get_notebook, get_newsprint)
_chosen = random.choice(_POOL)


def reroll() -> None:
    """Pick a fresh random design. Per-launch by default; call this to re-roll
    (e.g. to vary the look between runs) without touching the store wiring."""
    global _chosen
    _chosen = random.choice(_POOL)


def get_paper_plane(frame_idx, tilt_deg):
    return _chosen(frame_idx, tilt_deg)


BUILDERS = {"skin_paper_plane": get_paper_plane}
