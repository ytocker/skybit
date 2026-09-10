"""Stateful NEAR-lane crowd: pedestrians and dogs that actually walk at their own
pace — two-way foot traffic, pauses/starts, dogs darting — instead of gliding at
one uniform looped speed like the old world-locked tiling did.

Cosmetic only (the sidewalk is never scored), so plain per-entity `random` is
fine; no cross-target determinism is needed.

Positions live in WORLD units (the same axis as `world.bg_scroll`); a lane
painter draws each entity at `screen_x = round(world_x - bg_scroll)`. So a
STANDING entity (`walk_vel == 0`) tracks the ground/floor pixel-for-pixel
(planted, exactly like a bench or a plant), and a walker adds only its own
integrated walk displacement — relative to the GROUND, never the camera.

Everything integrates with `sdt`, the same delta that advances `bg_scroll`, so
slow-mo / rail / skateboard / weather scroll changes all match for free. Entities
spawn and cull STRICTLY off-screen (right in, left out — the `|walk_vel| < speed`
clamp guarantees the net screen motion is always leftward), so the old no-pop /
no-flicker guarantee is preserved by geometry.
"""
from __future__ import annotations

import random

from game.config import W
from game import foreground_promenade as pr
from game import foreground_variants as _fv

# kind -> variant family for _fv.select_variant. Draw scale + drawer live in the
# lane module (foreground_near_lane._emit_near_crowd); the sim only carries state.
_FAMILY = {"stroller": "pedestrian", "kids": "kid", "dog": "dog"}
_SALT = {"stroller": 31, "kids": 41, "dog": 51}   # match the legacy per-row salts
_GAIT_RATE = {"stroller": 1.0, "kids": 1.2, "dog": 1.9}

_NEAR_CAP = 8              # hard ceiling regardless of density (perf)
_BASE_N = 6               # target near-lane living count at full density
_SPAWN_MARGIN = 120       # spawn/cull this far off the screen edges (world px)
_SPAWN_COOLDOWN = 0.35    # min seconds between spawns (so they don't enter as a wall)

# Walk speeds, world px/s. Sign convention: <0 walks WITH the flow (nets faster
# leftward on screen), >0 walks AGAINST it (upstream — still nets leftward, just
# slower), 0 = standing (rides exactly world speed, i.e. planted).
_PED_SPEED = (34.0, 66.0)
_DOG_SPEED = (72.0, 140.0)


class _Ent:
    __slots__ = ("kind", "variant", "world_x", "walk_vel", "facing", "gait",
                 "state", "timer", "target_vel", "accel")


def _pick_kind():
    r = random.random()
    if r < 0.50:
        return "stroller"
    if r < 0.75:
        return "kids"
    return "dog"


def _roll_ped_vel():
    """Two-way distribution: ~10% standing, ~30% upstream, ~60% with the flow."""
    r = random.random()
    if r < 0.10:
        return 0.0
    mag = random.uniform(*_PED_SPEED)
    return mag if r < 0.40 else -mag


class SidewalkCrowd:
    """One instance per World; updated where `bg_scroll` advances, drawn by the
    near-lane painter which reads `.near`."""

    def __init__(self):
        self.near: list[_Ent] = []
        self._spawn_cd = 0.0
        self._id = 0

    def _density(self, phase, t):
        return (pr._population(phase) * pr._run_fill(t)
                * pr._weather_crowd_factor(phase))

    def _spawn(self, scroll, phase):
        self._id += 1
        kind = _pick_kind()
        rain = getattr(pr, "_CUR_RAIN", 0.0)
        snow = getattr(pr, "_CUR_SNOW", 0.0)
        variant = _fv.select_variant(
            _FAMILY[kind], _fv.slot_seed(self._id, _SALT[kind]),
            _fv.beat_for_phase(phase), _fv.weather_bucket(rain, snow))
        e = _Ent()
        e.kind = kind
        e.variant = variant
        # Enter just off the RIGHT edge, scattered so a burst doesn't form a wall.
        e.world_x = scroll + W + _SPAWN_MARGIN + random.uniform(0.0, 90.0)
        e.gait = random.uniform(0.0, 10.0)      # own animation phase → not in lockstep
        if kind == "dog":
            e.state = "trot"
            e.walk_vel = -random.uniform(*_DOG_SPEED)
            e.target_vel = e.walk_vel
            e.accel = random.uniform(120.0, 260.0)
            e.timer = random.uniform(0.4, 1.1)
        else:
            e.state = "walk"
            e.walk_vel = _roll_ped_vel()
            e.target_vel = 0.0
            e.accel = 0.0
            e.timer = random.uniform(2.0, 5.0)
        e.facing = 1 if e.walk_vel > 0 else -1
        self.near.append(e)

    def _transition(self, e):
        if e.kind == "dog":
            # Re-pick a dart target — occasionally upstream → weaving/darting.
            mag = random.uniform(*_DOG_SPEED)
            e.target_vel = mag if random.random() < 0.25 else -mag
            e.timer = random.uniform(0.35, 1.0)
            e.state = "dart"
        elif e.state == "walk":
            e.state = "pause"
            e.walk_vel = 0.0
            e.timer = random.uniform(0.8, 2.5)
        else:
            e.state = "walk"
            e.walk_vel = _roll_ped_vel()
            e.timer = random.uniform(2.0, 5.0)

    def update(self, scroll, speed, sdt, phase, t):
        """Advance the sim. `scroll` is the post-increment `world.bg_scroll`;
        `speed` the px/s the world moved this frame; `sdt` the scaled dt (carries
        slow-mo). Called at every bg_scroll advance (play + menu idle)."""
        maxv = 0.9 * speed   # nothing outruns the world → always exits left (0 → frozen)
        keep = []
        for e in self.near:
            e.timer -= sdt
            if e.timer <= 0.0:
                self._transition(e)
            if e.kind == "dog":
                dv = e.target_vel - e.walk_vel
                step = e.accel * sdt
                dv = step if dv > step else (-step if dv < -step else dv)
                e.walk_vel += dv
            # Clamp BEFORE integrating so nothing outruns the world and speed==0
            # (game frozen) leaves world_x pinned to the ground.
            if e.walk_vel > maxv:
                e.walk_vel = maxv
            elif e.walk_vel < -maxv:
                e.walk_vel = -maxv
            e.world_x += e.walk_vel * sdt
            e.gait += _GAIT_RATE[e.kind] * sdt
            if e.walk_vel < -1.0:
                e.facing = -1
            elif e.walk_vel > 1.0:
                e.facing = 1
            if e.world_x - scroll > -_SPAWN_MARGIN:   # still on/near screen → keep
                keep.append(e)
        self.near = keep

        self._spawn_cd -= sdt
        target = min(_NEAR_CAP, int(round(_BASE_N * self._density(phase, t))))
        if len(self.near) < target and self._spawn_cd <= 0.0:
            self._spawn(scroll, phase)
            self._spawn_cd = _SPAWN_COOLDOWN
