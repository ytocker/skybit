"""Tiny painter's-algorithm draw buffer for the sidewalk foreground.

The promenade + near lane used to paint in a fixed pass order, so occlusion was
decided by call order rather than depth — a plant drawn early could be overpainted
by a structure drawn later on the SAME ground line. Both lanes now ENQUEUE their
draws here instead of painting immediately; each lane flushes its queue sorted by
base/feet Y so an object whose feet sit lower on screen (nearer the camera) paints
last and overlays one whose feet are higher.

Selection (the `_world_xs`/`_slot_latch`/`_latch_prune` loops) is unchanged and
still runs every frame; only the paint is deferred into a captured closure.

Cross-lane depth is handled by WHERE each lane flushes relative to the gameplay
pillars (see foreground.py / scenes.py): the far lane flushes behind the pillars,
the near lane flushes in front of them — pillar bases sit between the two lanes'
ground lines, so this places everything at the right depth without sorting the
full-height pillar geometry into the queue.
"""
from __future__ import annotations

# Tie-break tiers for objects sharing a ground line: lower value = further back
# (painted earlier). Free-standing props/cast sit IN FRONT of large fixed
# back-structures at the same feet line, matching the "lower-on-screen overlays"
# read where the literal base-y can't break the tie.
TB_STRUCTURE = 0    # kiosk / pagoda stall, lamp post, banner pole, wish-tree, crates
TB_FIXTURE   = 10   # planters, cairns, barrels, bamboo, vine tubs, benches, braziers, campfire
TB_CAST      = 20   # people, animals, performers

_QUEUE: list = []   # (base_y:int, tiebreak:int, seq:int, fn)
_SEQ = 0


def reset():
    """Drop any queued draws — called once at the head of the frame's foreground
    so a flush aborted mid-frame can never leak into the next."""
    global _SEQ
    _QUEUE.clear()
    _SEQ = 0


def enqueue(base_y, tiebreak, fn):
    """Defer a draw: `fn(surf)` runs at flush time, ordered by (base_y, tiebreak,
    submission). `base_y` should be the STATIC feet line (not the per-frame bob)
    so near-tied objects keep a stable order and never z-fight."""
    global _SEQ
    _QUEUE.append((int(base_y), int(tiebreak), _SEQ, fn))
    _SEQ += 1


def flush(surf):
    """Paint everything queued so far, back-to-front, then clear the queue. The
    `seq` term makes the sort total + deterministic and preserves submission order
    within a (base_y, tiebreak) group (e.g. a performer enqueued after its crowd
    still draws over it)."""
    if not _QUEUE:
        return
    _QUEUE.sort(key=lambda c: (c[0], c[1], c[2]))
    for _by, _tb, _seq, fn in _QUEUE:
        fn(surf)
    _QUEUE.clear()
