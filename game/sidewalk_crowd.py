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
_FAMILY = {"stroller": "pedestrian", "kids": "kid", "dog": "dog",
           "elder": "elder"}
_SALT = {"stroller": 31, "kids": 41, "dog": 51, "elder": 61}
_GAIT_RATE = {"stroller": 1.0, "kids": 1.2, "dog": 1.9, "elder": 0.7}

_NEAR_CAP = 34             # hard ceiling regardless of density (perf)
# Targets are IN-BAND counts: the walk band spans W + 2*_SPAWN_MARGIN world-px
# (~1.9x the screen), so an on-screen crowd of N needs ~1.9N in the band. Sized
# for ~7 on-screen figures on a calm day and ~15 at the night-market peak.
_BASE_N = 20              # target near-lane living count at full density
_MARKET_N = 30            # fuller front lane through the night-market window
_SPAWN_MARGIN = 120       # spawn/cull this far off the screen edges (world px)
_SPAWN_COOLDOWN = 0.14    # min seconds between spawns (so they don't enter as a wall)
                          # — the real population gate: at 160 px/s over the
                          # ~690 px band, steady state ~= band_time/cooldown.
_LEAVE_STAGGER = 0.8      # seconds between departures when the street empties

# Walk speeds, world px/s. Sign convention: <0 walks WITH the flow (nets faster
# leftward on screen), >0 walks AGAINST it (upstream — still nets leftward, just
# slower), 0 = standing (rides exactly world speed, i.e. planted).
_PED_SPEED = (34.0, 66.0)
# A stray ambles: the old (72, 140) dart made every dog re-cross the screen
# several times, multiplying its perceived frequency well past its spawn share.
_DOG_SPEED = (55.0, 100.0)


class _Ent:
    __slots__ = ("kind", "variant", "world_x", "walk_vel", "facing", "gait",
                 "state", "timer", "target_vel", "accel", "wave", "depth")


def _pick_kind():
    # People dominate; the dog is a STRAY — an occasional sighting, not a
    # fifth of the street (at 20% the fast re-crossing dogs read as a pack).
    r = random.random()
    if r < 0.46:
        return "stroller"
    if r < 0.71:
        return "kids"
    if r < 0.93:
        return "elder"
    return "dog"


def _market_now(phase):
    """The night-market window (remapped keyframes): the front lane strolls."""
    p = phase % 1.0
    return 0.680 <= p < 0.820


def _roll_ped_vel(phase=0.0):
    """Two-way distribution: ~10% standing, ~30% upstream, ~60% with the flow.
    Through the night market more people stand and everyone ambles (an eating,
    browsing crowd, not a commuting one); in real rain the walkers hurry."""
    market = _market_now(phase)
    r = random.random()
    if r < (0.22 if market else 0.10):
        return 0.0
    mag = random.uniform(*_PED_SPEED)
    if market:
        mag *= 0.72
    elif getattr(pr, "_CUR_RAIN", 0.0) > 0.35:
        mag *= 1.25
    return mag if r < 0.40 else -mag


class SidewalkCrowd:
    """One instance per World; updated where `bg_scroll` advances, drawn by the
    near-lane painter which reads `.near`."""

    def __init__(self):
        self.near: list[_Ent] = []
        self._spawn_cd = 0.0
        self._leave_cd = 0.0
        self._id = 0
        self._seen_score = 0
        self._seen_misses = 0

    def _density(self, phase, t):
        return pr.street_density(phase, t)

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
            e.walk_vel = _roll_ped_vel(phase)
            e.target_vel = 0.0
            e.accel = 0.0
            e.timer = random.uniform(2.0, 5.0)
        e.facing = 1 if e.walk_vel > 0 else -1
        e.wave = 0.0
        # Depth across the front walk, dealt for the entity's whole life: 0 =
        # the walk's mid-line, 1 = the kerb nearest the camera. Mildly
        # bottom-weighted — the front edge stays the busiest, but every tier
        # gets real traffic (a steeper curve starved the back tiers so the
        # depth ladder had nothing to show) — and nearer figures drift a touch
        # faster for a cheap parallax read.
        e.depth = random.random() ** 0.85
        e.walk_vel *= 0.90 + 0.10 * e.depth
        self.near.append(e)

    def _transition(self, e, phase=0.0):
        if e.state == "leaving":
            return                       # a departure is one-way — no re-decisions
        if e.kind == "dog":
            # Re-pick a dart target — occasionally upstream → weaving/darting.
            mag = random.uniform(*_DOG_SPEED)
            e.target_vel = mag if random.random() < 0.25 else -mag
            e.timer = random.uniform(0.35, 1.0)
            e.state = "dart"
        elif e.state == "walk":
            e.state = "pause"
            e.walk_vel = 0.0
            # Night-market pauses are BROWSE pauses — longer, at a stall's pace.
            e.timer = (random.uniform(1.5, 3.0) if _market_now(phase)
                       else random.uniform(0.8, 2.5))
        else:
            e.state = "walk"
            e.walk_vel = _roll_ped_vel(phase)
            e.timer = random.uniform(2.0, 5.0)

    def update(self, scroll, speed, sdt, phase, t):
        """Advance the sim. `scroll` is the post-increment `world.bg_scroll`;
        `speed` the px/s the world moved this frame; `sdt` the scaled dt (carries
        slow-mo). Called at every bg_scroll advance (play + menu idle)."""
        maxv = 0.9 * speed   # nothing outruns the world → always exits left (0 → frozen)
        keep = []
        for e in self.near:
            if not hasattr(e, "wave"):      # tolerate externally-built entities
                e.wave = 0.0
            if not hasattr(e, "depth"):
                e.depth = 1.0
            e.timer -= sdt
            if e.timer <= 0.0:
                self._transition(e, phase)
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
            # Depth parallax: nearer WALKERS drift faster across the screen —
            # the motion cue the size ladder needs — quantised to the same four
            # tiers the renderer maps depth onto. Only while moving: a standing
            # figure must stay pixel-locked to the paving (the planted
            # invariant), so the drift gates on the walk itself.
            if abs(e.walk_vel) > 1.0:
                e.world_x -= speed * sdt * (0.0614, 0.092, 0.1227, 0.15)[
                    min(3, int(e.depth * 4.0))]
            e.gait += _GAIT_RATE[e.kind] * sdt
            if e.walk_vel < -1.0:
                e.facing = -1
            elif e.walk_vel > 1.0:
                e.facing = 1
            if e.world_x - scroll > -_SPAWN_MARGIN:   # still on/near screen → keep
                keep.append(e)
        self.near = keep

        self._spawn_cd -= sdt
        base_n = _MARKET_N if _market_now(phase) else _BASE_N
        target = min(_NEAR_CAP, int(round(base_n * self._density(phase, t))))
        if len(self.near) < target and self._spawn_cd <= 0.0:
            self._spawn(scroll, phase)
            self._spawn_cd = _SPAWN_COOLDOWN
        # Tournament awareness — the town is cheerful and notices the flyer,
        # without ever becoming HUD: a couple of figures wave for a beat at a
        # score milestone or a near-miss, and through the finale's coin rush the
        # whole front lane stops and waves Pip through. Muted during the calm
        # mandates; waves decay on their own.
        for e in self.near:
            if e.wave > 0.0:
                e.wave -= sdt
        if not pr.calm_now():
            from game import foreground_weekend as _wkd
            # FIRE-TREE NIGHT: while the dragon parades, the whole front lane
            # stops where it stands and turns to face it — the market pausing
            # for its own crown is the festival's strongest beat.
            if _wkd.happening_active('festival_dragon'):
                for e in self.near:
                    # A departure stays one-way even for the dragon — someone
                    # already walking off doesn't spin back around.
                    if e.kind != "dog" and e.state not in ("watch_parade", "leaving"):
                        e.state = "watch_parade"
                        e.walk_vel = 0.0
                        e.facing = 1          # the dragon enters from the right
                        e.timer = 12.0
                        e.wave = max(e.wave, 0.6 + random.random() * 0.8)
            # Once-per-day: the first drops — the frame rain arrives, everyone
            # on the front lane stops, looks up, then moves on.
            if (getattr(pr, "_CUR_RAIN", 0.0) >= 0.12
                    and _wkd.happening('first_umbrella', (0.48, 0.545),
                                       phase, t, 2.0) is not None
                    and not getattr(self, "_first_drops_done", False)):
                self._first_drops_done = True
                for i, e in enumerate(self.near):
                    if e.kind != "dog":
                        e.state = "pause"
                        e.walk_vel = 0.0
                        e.timer = 1.0 + 0.25 * i
                        e.wave = max(e.wave, 0.9 + 0.2 * i)
            score = int(pr.signal('score', 0) or 0)
            if score // 25 > self._seen_score // 25:
                for e in random.sample(self.near, min(3, len(self.near))):
                    if e.kind != "dog":
                        e.wave = max(e.wave, 1.5)
            self._seen_score = score
            misses = int(pr.signal('near_misses', 0) or 0)
            if misses > self._seen_misses and self.near:
                e = random.choice(self.near)
                if e.kind != "dog":
                    e.wave = max(e.wave, 0.8)
            self._seen_misses = misses
            if pr.signal('finale_active'):
                for e in self.near:
                    if e.kind != "dog":
                        e.wave = max(e.wave, 0.5)
                        if e.state == "walk" and abs(e.walk_vel) > 20.0:
                            e.walk_vel *= 0.5   # slow to see the flyer through
        # Departure choreography: when the street empties (a storm building, the
        # market closing), the surplus figures don't fade — one at a time, on a
        # stagger, someone visibly hurries off with the flow and exits.
        self._leave_cd -= sdt
        if len(self.near) > target + 1 and self._leave_cd <= 0.0:
            for e in self.near:
                if e.state not in ("leaving", "dart", "watch_parade"):
                    e.state = "leaving"
                    e.walk_vel = -random.uniform(66.0, 92.0)
                    e.facing = -1
                    e.timer = 1e9
                    self._leave_cd = _LEAVE_STAGGER
                    break
