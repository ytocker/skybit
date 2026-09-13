"""
World simulation: physics, spawner, collision, difficulty ramp.
Handles coin/mushroom pickup FX. IMPORTANT: coin pickup must NOT do a
full-screen flash (that was the 'glitch' the user saw) — only localized
sparkle particles around the coin.
"""
import math
import random
import pygame

from game.config import (
    W, H, GROUND_Y, PIPE_W, PIPE_SPACING,
    GAP_START, SCROLL_BASE,
    DAY_SCROLL_STEP, DAY_SCROLL_CAP, DAY_GAP_STEP, DAY_GAP_FLOOR,
    GAP_NEWBIE_START, SCROLL_NEWBIE_BASE, PIPE_SPACING_NEWBIE, RAMP_PIPES,
    PLATEAU_PIPES, SPAWN_GRACE,
    PIPE_HITBOX_SHRINK,
    BIRD_X, BIRD_R, COIN_R, POWERUP_R, PARCEL_R, PARCEL_Y_OFFSET,
    POWERUP_CHANCE, POWERUP_CHANCE_NEWBIE, POWERUP_COOLDOWN,
    TRIPLE_DURATION, MAGNET_DURATION, MAGNET_RADIUS,
    MEGAMAGNET_DURATION, MEGAMAGNET_RADIUS,
    SLOWMO_DURATION, SLOWMO_SCALE, KFC_DURATION, KFC_GAP_BOOST, GHOST_DURATION,
    GROW_DURATION, GROW_SCALE, REVERSE_DURATION,
    POWERUP_WEIGHTS, POWERUP_SCORE_GATES, POWERUP_REPLACED_AT,
    SHRINK_DURATION, SHRINK_SCALE,
    RAIL_PILLAR_COUNT, RAIL_LEAD_PILLARS, RAIL_SCROLL_MULT,
    LOTTERY_TIERS, LOTTERY_REVEAL_TIME,
    FLAP_V,
    COIN_RUSH_INTERVAL, COIN_RUSH_GAP_BOOST, COIN_RUSH_COINS,
    SECRET_POWERUP_WEIGHTS, LATE_GAME_PILLAR, DEBUG_GENIE_PILLAR,
    CLOWN_START_PILLAR, CLOWN_SLOT_PILLARS, CLOWN_WARREN_SPACING,
    CLOWN_PRECLEAR_PILLARS, CLOWN_LEADIN_PILLARS, CLOWN_OUTRO_PILLARS,
    STORM_JOLT_RAIN_MIN,
    GENIE_OFFER_COUNT, GENIE_OFFER_Y_SLOTS,
    GENIE_CHAMBER_GAP_BOOST, GENIE_CHAMBER_SPACING,
    GENIE_CHAMBER_REVEAL_DIST,
    SKATEBOARD_DURATION, SKATE_SLIDE_MULT, SKATE_SLIDE_ATTACK,
    SKATE_SLIDE_RELEASE, BACKFLIP_DURATION, BACKFLIP_TAP_WINDOW,
    KICKFLIP_DURATION, KICKFLIP_TAP_GAP_MIN, KICKFLIP_TAP_GAP_MAX,
    HEELFLIP_DURATION, HEELFLIP_TAP_GAP_MIN, HEELFLIP_TAP_GAP_MAX,
    POPSHUVIT_DURATION, POPSHUVIT_TAP_GAP_MIN, POPSHUVIT_TAP_GAP_MAX,
    KNIGHT_DURATION, KNIGHT_INVULN,
    LIVES_PER_RUN, LIVES_INVULN_DUR, LIVES_FLICKER_HZ,
    UMBRELLA_DURATION, UMBRELLA_SPAWN_PILLARS,
    DEATH_FADE_DURATION,
    TREASURE_BOX_GRANT, TREASURE_BOX_ANIM_T,
    CYCLE_FINALE_RUSH_PILLARS, CYCLE_FINALE_BOX_INDEX,
    CYCLE_FINALE_PHASE_HI, CYCLE_FINALE_PHASE_LO,
    WEATHER_HEAVY_THRESHOLD, WEATHER_COIN_SHAKE_AMP, WEATHER_PIP_SHIVER_AMP,
    WEATHER_FLAP_DAMPEN_MAX, WEATHER_WIND_LEAN_AMP, WEATHER_WIND_SCROLL_FACTOR,
    THERMAL_SPAWN_THRESHOLD, THERMAL_SPAWN_CHANCE_MAX,
    GEYSER_MAX_CONCURRENT,
    ROCK_SPAWN_THRESHOLD, ROCK_PER_PILLAR_MAX, ROCK_RING_COUNT,
    GEYSER_RAMP_PILLARS,
    GEYSER_W, GEYSER_H, GEYSER_LIFT_VY_CAP,
    GEYSER_GY_DELTA_MAX, GEYSER_GX_SHIFT_MAX, GEYSER_DUD_CHANCE,
)
from game.entities import (
    Bird, Pipe, Coin, PowerUp, Particle, CloudPuff, PoofGrain, FloatText,
    GenieCharacter, TrickBubble, Ramp,
    FlyingCoinParticle, Geyser, Rock, RockPatch,
)
from game._proof import ProofState
from game.draw import (
    COIN_GOLD, COIN_LIGHT,
    PARTICLE_GOLD, PARTICLE_ORNG, PARTICLE_WHT, PARTICLE_CRIM,
    UI_GOLD, UI_ORANGE, UI_CREAM, WHITE, BIRD_RED, UI_RED,
)
from game import biome
from game import audio
from game import geyser_fx
from game.weather import (
    Weather,
    rain_intensity as _rain_intensity,
    storm_intensity as _storm_intensity,
    thermal_intensity as _thermal_intensity,
    GENIE_PILLAR,
    _phase_for_pillar,
)
from game.clown_event import ClownEvent
from game.ambient import AmbientScenes

CLOWN_EVENT_PHASE = _phase_for_pillar(CLOWN_START_PILLAR)
CLOWN_PRECLEAR_PHASE = _phase_for_pillar(CLOWN_START_PILLAR - CLOWN_PRECLEAR_PILLARS)


def _lerp(a, b, t):
    return a + (b - a) * max(0.0, min(1.0, t))


class World:
    # Seconds AFTER the ready_t (1.0 s) freeze before the first pipe should
    # enter the visible frame. The intro hands gameplay the cottage + parcel
    # composition; this grace period gives the opener overlay time to scroll
    # the cottage off-screen before pillars take over. Lives in `game.config`
    # as `SPAWN_GRACE` (single source of truth so the progression chart's
    # `_phase_for_pillar` and `_seed_first_pipes` agree on the first-pillar
    # offset).

    def __init__(self, demo=None):
        # `demo`, when set, is a branch-only scripted prototype controller
        # (see game/warren_demo.py) that owns spawning + the clown/dice/route
        # beat. Every demo branch below is gated on `demo is not None`, so the
        # normal run path is untouched.
        self.demo = demo

        # Reshuffle the meadow at the start of every new World — picks a
        # fresh ground theme + sparsity baseline + decoration positions
        # so no two plays look the same.
        from game import ground_variants
        ground_variants.set_run_seed(None)

        self.bird = Bird()
        self.pipes: list[Pipe] = []
        self.coins: list[Coin] = []
        self.powerups: list[PowerUp] = []
        # SKATEBOARD ramps perched on lower-pillar crowns; spawned by
        # _maybe_spawn_ramp during the buff. Scrolls + culls with the
        # pipes; world collision checks them when bird.skateboard_active.
        self.ramps: list[Ramp] = []
        self.geysers: list[Geyser] = []
        self.rocks: list[Rock] = []
        geyser_fx.prewarm()   # bake cone/steam/rock caches → no first-eruption hitch
        self.particles: list[Particle] = []
        self.float_texts: list[FloatText] = []
        # Cycle-finale celebration entities. Banner is screen-space;
        # garland tracks 2 pillar refs in world-space and scrolls with
        # them. Both are spawned together in _activate_treasure_box and
        # share a 1.4 s fade envelope so they leave the scene as one.
        self.treasure_banners: list = []
        self.celebration_garlands: list = []
        # Persistent sky + ground decor over the 5-pillar phantom gap.
        # Spawned from World._activate_treasure_box (bunting + balloons)
        # and World._spawn_pipe at chest drop (ground marker), so they
        # signal "completed-the-day zone" for the whole time the gap is
        # on screen, not just the 3.5 s celebration window.
        self.celebration_buntings: list = []
        self.celebration_balloon_clusters: list = []
        self.celebration_ground_markers: list = []
        # Cheering crowd of 7 parrots flanking the finish-line stripe —
        # spawned in the same chest-drop branch as the marker.
        self.celebration_crowds: list = []
        # Cycle counter — increments on every biome-phase wrap, so the
        # banner reads "DAY 1 COMPLETE!" on the first rollover, "DAY 2"
        # on the second, etc. Resets each fresh run (no save-file
        # persistence — every run starts at day 0 pre-rollover).
        self.cycles_completed: int = 0
        # Second-wave coin storm: 0.30 s after the chest pickup, a tail
        # of 40 more flying coins spawns from the chest's last known
        # position. Stays > 0 between activation and fire; reset to 0
        # afterward so a second pickup in the same run schedules cleanly.
        self._treasure_second_wave_t: float = 0.0
        self._treasure_second_wave_pos: tuple = (0.0, 0.0)

        self.scroll_speed = SCROLL_BASE
        self.bg_scroll = 0.0

        self.score = 0
        self.coin_count = 0

        self.triple_timer = 0.0
        self.magnet_timer = 0.0
        self.megamagnet_timer = 0.0
        self.slowmo_timer = 0.0
        self.kfc_timer    = 0.0
        # Random index into KFC_MOUNTAIN_DRAWERS, refreshed on each
        # _activate_kfc call so the background fries-pile style varies
        # between powerup activations. `kfc_mountain_layers` holds the
        # three pre-rendered per-parallax-layer Surfaces;
        # `kfc_activation_scroll` snapshots bg_scroll at pickup time so
        # PlayScene can compute the parallax offset for each layer and
        # make the fries pile drift at the same speed as the normal
        # mountains do.
        self.kfc_mountain_variant = 0
        self.kfc_mountain_layers: "list[pygame.Surface] | None" = None
        self.kfc_activation_scroll = 0.0
        self.ghost_timer  = 0.0
        self.ghost_timer_total = GHOST_DURATION  # full window the HUD bar drains over
        self.grow_timer   = 0.0
        self.reverse_timer = 0.0
        self.shrink_timer = 0.0
        # RAIL TRACK: pillar-limited buff. Tagging is fixed at activation
        # — exactly RAIL_PILLAR_COUNT pillars get rail_active set in
        # _activate_rail and nothing else picks up the tag afterward.
        # rail_pipes is rebuilt from self.pipes' rail_active flags every
        # frame so the renderer still sees the on-screen tail of tagged
        # pipes after expiry. rail_pending is the count of force-spawned
        # pipes the next _spawn_pipe call should tag.
        self.rail_pillars_left = 0
        self.rail_pipes: list = []
        self.rail_cart_pipe = None
        self.rail_pending = 0
        # Lottery reveal animation. None when not rolling; a dict
        # {t, tier, delta, x, y, applied} while the scratch-card reels
        # are ticking. Result lands at LOTTERY_REVEAL_TIME.
        self.lottery_anim: "dict | None" = None
        self.powerup_cooldown = 0.0

        # ── Secret late-game power-ups ──────────────────────────────────────
        # GENIE: companion conjurer actors. Each is ticked + culled in update.
        self.genie_actors: list = []
        # GENIE CHAMBER: True between _activate_genie and the next pipe
        # spawn; the spawning pillar consumes the flag, applies the
        # chamber gap boost, and nests the 3 wish offers vertically
        # inside its (now over-wide) gap.
        self.genie_chamber_pending = False
        # SKATEBOARD: timed grind buff. slide_boost is an attack/release
        # envelope (0..1) that ramps up while Pip grinds a surface and decays
        # otherwise; _current_scroll reads it to speed the world up.
        self.skateboard_timer = 0.0
        self.slide_boost = 0.0
        self._sliding_this_frame = False
        self._sliding_prev_frame = False
        # SKATEBOARD comic trick bubbles + tap-streak state. Each flap
        # during the skateboard buff feeds _track_skateboard_tricks
        # which resolves the trick palette and pops a coloured bubble
        # near the score HUD.
        self.trick_bubbles: list = []
        self._last_tap_t = -999.0
        self._tap_streak = 0
        # Activation overlays (drawn in scenes): caption banner + starburst.
        self.skateboard_caption_t = 0.0
        self.skateboard_caption_dur = 0.0
        self.skateboard_caption_overlay = None
        self.skateboard_burst_t = 0.0
        self.skateboard_burst_dur = 0.0
        self.skateboard_burst_surface = None
        self.skateboard_burst_cx = 0
        self.skateboard_burst_cy = 0
        self._skateboard_lift_y = 26
        # KNIGHT: survive-one-hit. While knight_timer > 0 the next lethal hit
        # is consumed in _die() and Pip revives with knight_invuln seconds of
        # collision grace.
        self.knight_timer = 0.0
        self.knight_invuln = 0.0
        # LIVES: three hearts per run. Each pipe collision that would otherwise
        # end the run spends one heart and calls _revive_life() instead of
        # game_over. lives_invuln is the post-revive immunity countdown.
        self.lives_remaining = LIVES_PER_RUN
        self.lives_invuln    = 0.0
        self.lives_used      = 0
        # UMBRELLA: independent power-up that cancels rain flap-dampening.
        # Spawned once per storm during the rain window; never in the regular
        # weighted pool or the surprise re-roll.
        self.umbrella_timer = 0.0

        # Coin-rush counter: increments each spawn; every Nth pipe is a rush.
        self.pipes_spawned = 0

        # Consecutive non-rush pillars while the morning-thermal event is
        # active. Drives the rock-density ramp and gates the first geyser so
        # the rocks build up over GEYSER_RAMP_PILLARS pillars as a telegraph.
        # Resets to 0 whenever the event is off.
        self._thermal_pillars = 0

        # When the previous pillar planted a geyser, the next pillar's gap_y
        # is pre-rolled at plant time (so the geyser's horizontal position
        # can be biased toward the side that needs more pre-descent space).
        # _spawn_pipe consumes this instead of rolling its own gy.
        self._pending_gap_y = None

        # Per-run stats surfaced on the post-game summary.
        self.pillars_passed = 0
        self.time_alive = 0.0
        self.near_misses = 0
        self.flap_count = 0
        # Every Coin construction increments this; the stats screen uses
        # coin_count / max(1, coins_spawned - len(coins)) as the "% of
        # encountered coins grabbed" figure (coins still on screen don't
        # count as missed yet).
        self.coins_spawned = 0
        # Ceiling bonks this run (Pip clamped against the top edge). Edge-detected
        # via _was_ceiling_clamped so a held bonk counts once, not every frame.
        self.ceiling_hits = 0
        self._was_ceiling_clamped = False
        # Skateboard tricks landed this run + the distinct trick types performed
        # (for a "land all four in one run" goal). Both reset with the fresh World.
        self.tricks_landed = 0
        self.tricks_landed_types: set = set()
        # Wall of Shame: a small death-moment snapshot (filled in _die) + two
        # live trackers. max_flaps_per_sec is the worst 1-second flap burst this
        # run (panic-spike roast); _lottery_pulled marks a lottery slot pull.
        self.death_pillar = 0
        self.death_ghost = False
        self.death_kfc = False
        self.died_early_phase = False
        # Hall-of-Shame expansion: more death-moment snapshots, all filled in
        # _die while the effect state is still live (read post-death by
        # achievements.evaluate_run on the same frame).
        self.death_slowmo = False
        self.death_poison = False
        self.death_skateboard = False
        self.death_lightning = False
        self.death_celebration = False
        self.death_magnet_zero = False
        self.death_wish_pending = False
        self._lottery_pulled = False
        self.max_flaps_per_sec = 0
        self._flap_window_t = 0.0
        self._flap_window_n = 0
        # Hall-of-Fame per-run trackers (cheap, event-driven — no per-frame scan).
        # max_active_powerups: peak count of simultaneously-active timed buffs,
        # sampled at each activation. max_pillars_in_slowmo / _in_ghost: most
        # pillars cleared within ONE continuous Slow-Mo / Ghost window (the
        # per-activation counter resets when that buff (re)starts). surprise_repeat
        # flags a Surprise Box that re-rolled a kind it already rolled this run.
        self.max_active_powerups = 0
        self.max_pillars_in_slowmo = 0
        self.max_pillars_in_ghost = 0
        self._slowmo_run_pillars = 0
        self._ghost_run_pillars = 0
        self.surprise_repeat = 0
        self._surprise_rolls: set = set()
        # Hall-of-Shame live trackers: coins grabbed inside the current magnet
        # window (Rich and Reckless), whether a genie-chamber wish was ever
        # collected (Wish Unspent), the Coin Rush grab tally (Coin Blind), and
        # the count of storm jolts survived this run (Lightning Magnet).
        self._coins_in_magnet = 0
        self._genie_wish_taken = False
        self.coin_blind = False
        self._rush_cur_total = 0
        self._rush_cur_got = 0
        self._lightning_strikes_run = 0
        self.powerups_picked = {
            "triple": 0, "magnet": 0, "megamagnet": 0, "slowmo": 0, "kfc": 0,
            "ghost": 0, "grow": 0, "reverse": 0, "surprise": 0,
            "shrink": 0, "rail": 0, "lottery": 0,
            "skateboard": 0, "knight": 0, "genie": 0,
            "poison": 0, "treasure": 0,
        }
        # Cycle-finale "treasure box" state. _last_biome_phase samples the
        # phase every frame so a wrap from ~1.0 back to ~0.0 can be detected
        # one frame after biome_time crosses CYCLE_SECONDS. When that fires
        # the next CYCLE_FINALE_RUSH_PILLARS pillars are forced into a coin
        # rush; the middle pillar carries the chest. _finale_box_dropped is
        # a one-shot guard inside a single finale.
        self._last_biome_phase = 0.0
        self._finale_rush_remaining = 0
        self._finale_box_dropped = False
        # Clown event: a held CLOWN_SLOT_PILLARS-wide slot, re-armed each day.
        self._clown_slot_remaining = 0
        self._clown_route = []
        self._clown_fired_this_cycle = False
        self._clown_preclear_remaining = 0
        self._clown_entrance_pending = False
        self._clown_leadin_remaining = 0
        self._clown_outro_remaining = 0
        self.clown_event = None
        # Transient flag so near-miss detection fires once per pillar.
        self._near_miss_flags: dict[int, bool] = {}

        self.hit_flash = 0.0    # death-only red tint, NOT coin
        self.shake_mag = 0.0
        self.shake_t = 0.0

        # ── Thunderstorm storm-jolt state ──────────────────────────────────
        # lightning_strike: dict {path, life, life_max} for the bolt being
        # drawn (None when idle). _storm_jolt_lockout: cooldown after a
        # strike. _lightning_scorch_t: smoke-wisp aftermath timer.
        # _storm_buildup_seq/_t: scheduled telegraph bolts → climax strike.
        self.lightning_strike = None
        self._storm_jolt_lockout = 0.0
        self._lightning_scorch_t = 0.0
        self._scorch_smoke_accum = 0.0
        self._storm_buildup_seq = []
        self._storm_buildup_t = 0.0

        # Real elapsed gameplay seconds — drives the day/night biome cycle.
        # Held at this value while ready_t > 0 so the sky doesn't tick over
        # while the player is still on the start-of-run prompt. Open at
        # fresh-dawn (phase 0.0); the first cycle-finale chest fires
        # organically ~CYCLE_SECONDS later, with the newbie ramp
        # (~80 s at newbie scroll/spacing) safely finished by then.
        # Manual chest-event playtest uses the debug F9 hotkey rather
        # than a baked-in time shift.
        self.biome_time = 0.0

        # Always-ticking clock used for purely-cosmetic idle animations
        # (bird bob during the ready wait) so they keep moving even while
        # biome_time is frozen.
        self._idle_t = 0.0

        # Tamper-evident parallel ledger of every scoring event in the
        # run. The leaderboard submission carries the proof state, not
        # ``self.score``, so a JS-side ``world.score = 99999`` does not
        # change what gets submitted.
        self._proof = ProofState()

        self.weather = Weather()
        self.ambient = AmbientScenes()

        # Bake the parallax mountain strips for the opening bucket so the first
        # rendered frame is a cache hit (mirrors geyser_fx.prewarm above).
        from game import mountains_v14 as _mtn
        _mtn.prewarm(W, GROUND_Y, self.biome_phase)

        # Stateful near-lane sidewalk crowd (independent walking). Registered with
        # the foreground facade so draw_near_lane picks it up; re-registered here so
        # each new World (each run) owns a fresh, empty crowd.
        from game.sidewalk_crowd import SidewalkCrowd
        from game import foreground as _foreground
        self.crowd = SidewalkCrowd()
        _foreground.set_crowd(self.crowd)

        # "Get ready" freeze at the start of a round: physics paused until
        # the player flaps or the timer expires. Gives new players a moment
        # to orient before the first pillar scrolls in (REVIEW.md finding).
        self.ready_t = 1.0

        self.game_over = False

        # One-shot: when pillars_passed crosses LATE_GAME_PILLAR, a genie
        # lamp is placed in the gap between that pillar and the next one,
        # and from that point on the genie joins the regular spawn pool
        # and the Surprise Box re-roll pool.
        self._genie_milestone_fired = False
        # DEBUG aid: separate one-shot trigger at DEBUG_GENIE_PILLAR so the
        # pickup + chamber + wishes can be tested early without grinding
        # to pillar 65. Also enables the late-game pool/surprise rules.
        self._debug_genie_milestone_fired = False

        self._seed_first_pipes()

    # Back-compat: older snapshot/playtest scripts poke `world.mushrooms`.
    @property
    def mushrooms(self):
        return self.powerups

    @mushrooms.setter
    def mushrooms(self, value):
        self.powerups = value

    # ── difficulty ───────────────────────────────────────────────────────────

    def _ramp_t(self):
        # Newbie onboarding ramp: the first PLATEAU_PIPES pillars hold
        # the four _current_*() helpers at the easier newbie endpoints
        # (GAP_NEWBIE_START / SCROLL_NEWBIE_BASE / PIPE_SPACING_NEWBIE /
        # POWERUP_CHANCE_NEWBIE), then an ease-out quadratic eases them
        # toward the regular endpoints by pillar RAMP_PIPES. Keyed off
        # self.pillars_passed (per-run, NOT per-day) so the easier
        # intro never re-triggers after the first cycle wraps.
        pp = self.pillars_passed
        if pp < PLATEAU_PIPES:
            return 0.0
        x = (pp - PLATEAU_PIPES) / max(1, RAMP_PIPES - PLATEAU_PIPES)
        x = min(1.0, x)
        return 1.0 - (1.0 - x) ** 2

    # ── biome ────────────────────────────────────────────────────────────────

    @property
    def biome_phase(self):
        return biome.phase_for_time(self.biome_time)

    @property
    def biome_palette(self):
        return biome.palette_for_phase(self.biome_phase)

    def _day_delta_scroll(self) -> float:
        # Each completed biome cycle (day) adds DAY_SCROLL_STEP to the
        # scroll base, capped at DAY_SCROLL_CAP. Applied on top of the
        # post-newbie-ramp base, BEFORE the RAIL/SKATEBOARD/WEATHER
        # multipliers stack — so relative boosts (RAIL ×2.5, etc.) feel
        # the same shape, just at a higher base.
        return min(self.cycles_completed * DAY_SCROLL_STEP,
                   DAY_SCROLL_CAP - SCROLL_BASE)

    def _day_delta_gap(self) -> int:
        # Each completed day removes DAY_GAP_STEP px from the gap, with
        # a floor at DAY_GAP_FLOOR — kept well above the inert GAP_MIN
        # so casual players don't hit "feels random" territory.
        return -min(self.cycles_completed * DAY_GAP_STEP,
                    GAP_START - DAY_GAP_FLOOR)

    def _current_gap(self):
        base = _lerp(GAP_NEWBIE_START, GAP_START, self._ramp_t())
        return int(base + self._day_delta_gap())

    def _current_scroll(self):
        base = _lerp(SCROLL_NEWBIE_BASE, SCROLL_BASE, self._ramp_t())
        base += self._day_delta_scroll()
        # RAIL: world rushes by RAIL_SCROLL_MULT× while Pip is locked on
        # the cart. Pre-lock, normal speed so the player can take their
        # time deciding whether to land on the parked cart.
        if self.bird.cart_locked:
            base *= RAIL_SCROLL_MULT
        # SKATEBOARD grind: lerp from 1.0 to SKATE_SLIDE_MULT on the
        # slide-boost envelope so the speed-up eases in/out instead of
        # snapping when Pip lands on / lifts off a surface.
        if self.slide_boost > 0:
            base *= 1.0 + self.slide_boost * (SKATE_SLIDE_MULT - 1.0)
        # Snow-squall TAILWIND (predawn ~0.85): speeds the world up so
        # pipes/coins approach faster — composed multiplicatively with
        # the skateboard slide boost so both layer cleanly.
        wi = _storm_intensity(self.biome_phase)
        if wi > 0:
            base *= 1.0 + WEATHER_WIND_SCROLL_FACTOR * wi
        return base

    def _current_spacing(self):
        return int(_lerp(PIPE_SPACING_NEWBIE, PIPE_SPACING, self._ramp_t()))

    def _next_spacing(self):
        """Spacing for the NEXT pillar to spawn. During the clown slot the
        warren towers sit at the tight fused spacing; everything else uses
        the normal ramped spacing."""
        if self._clown_leadin_remaining > 0 or self._clown_outro_remaining > 0:
            return self._current_spacing()
        if self._clown_slot_remaining > 0:
            idx = CLOWN_SLOT_PILLARS - self._clown_slot_remaining
            if idx < len(self._clown_route):
                return CLOWN_WARREN_SPACING
        return self._current_spacing()

    def _current_powerup_chance(self):
        return _lerp(POWERUP_CHANCE_NEWBIE, POWERUP_CHANCE, self._ramp_t())

    # ── weather → gameplay (rain hooks + thunderstorm storm-jolt) ──────────────
    def _apply_weather_effects(self, dt):
        """Route current rain intensity to coins (shake) and Pip (shiver +
        flap dampen), drive the snow-squall tailwind + back-snow, and
        schedule the storm-jolt lightning strike at peak rain. Coin shake +
        Pip shiver are visual-only; flap dampen is a real (small) lift cut."""
        ri = _rain_intensity(self.weather.phase)
        if ri <= 0:
            for c in self.coins:
                c.weather_dx = 0.0
            self.bird.shiver_x = 0.0
            self.bird.shiver_y = 0.0
            self.bird.flap_dampen = 0.0
            # Storm has ended (or hasn't started this cycle). Cull any
            # uncollected umbrella still floating on-world — the pickup
            # can ONLY exist while it's raining.
            self.powerups = [m for m in self.powerups
                             if m.kind != "umbrella"]
        else:
            amp_x = WEATHER_COIN_SHAKE_AMP * ri
            freq = 4.5 * (1.0 + ri)
            for c in self.coins:
                c._weather_phase += dt * freq
                c.weather_dx = math.sin(c._weather_phase) * amp_x
            heavy = ri > WEATHER_HEAVY_THRESHOLD
            if heavy:
                heavy_t = (ri - WEATHER_HEAVY_THRESHOLD) / (1.0 - WEATHER_HEAVY_THRESHOLD)
                flash_kick = 1.5 if self.weather.flash_remaining > 0 else 1.0
                self.bird.shiver_x = random.uniform(-1, 1) * WEATHER_PIP_SHIVER_AMP * heavy_t * flash_kick
                self.bird.shiver_y = random.uniform(-1, 1) * WEATHER_PIP_SHIVER_AMP * heavy_t * flash_kick
                self.bird.flap_dampen = WEATHER_FLAP_DAMPEN_MAX * heavy_t
            else:
                self.bird.shiver_x = 0.0
                self.bird.shiver_y = 0.0
                self.bird.flap_dampen = 0.0
            # Umbrella overrides the rain flap-dampen — jumps return to
            # normal while it's active. Shiver stays (purely visual flavour).
            if self.umbrella_timer > 0:
                self.bird.flap_dampen = 0.0

        # Snow-squall tailwind (predawn ~0.85): forward push (scroll boost
        # lives in _current_scroll); driven by the storm envelope.
        wi = _storm_intensity(self.weather.phase)
        if wi > 0.05:
            self.bird.wind_lean = +WEATHER_WIND_LEAN_AMP * wi
        else:
            self.bird.wind_lean = 0.0

        # Windblown snow on Pip mirrors the squall's accumulated cover —
        # weather.snow_cover is the single source that also drives the screen
        # whiteout, so Pip buries and the scene whitens in lockstep (build ∝
        # intensity, full cover held through the climax, shed as it passes).
        self.bird.snow_load = self.weather.snow_cover

        # Storm jolt: near-peak rain, after lockout, only if Pip has score
        # to lose. Kicks off a ~4.4 s buildup of telegraph bolts → the strike.
        if self._storm_jolt_lockout > 0:
            self._storm_jolt_lockout = max(0.0, self._storm_jolt_lockout - dt)
        elif (ri > 0.85
              and self.score > 0
              and not self.game_over
              and self.ready_t <= 0
              and not self._storm_buildup_seq
              and random.random() < 0.06 * dt * 60):
            self._start_storm_buildup()

        if self._storm_buildup_seq:
            self._storm_buildup_t += dt
            while (self._storm_buildup_seq
                   and self._storm_buildup_t >= self._storm_buildup_seq[0][0]):
                _, kind = self._storm_buildup_seq.pop(0)
                if kind == "strike":
                    self._fire_storm_jolt()
                else:
                    side = -1 if kind.endswith("left") else 1
                    self._fire_background_lightning(side=side)

    def _apply_thermal_lift(self, dt):
        """Morning-thermal updraft — a CONSTANT rise. While Pip is inside any
        geyser column his upward speed is set to exactly GEYSER_LIFT_VY_CAP:
        one constant for every geyser, no stacking, and independent of how
        deep or how long he's been inside. A flap (faster than the cap) still
        overrides it, and being in two overlapping columns changes nothing."""
        if self.bird.vy <= -GEYSER_LIFT_VY_CAP:
            return
        bx, by = self.bird.x, self.bird.y
        for gy in self.geysers:
            if gy.contains(bx, by):
                self.bird.vy = -GEYSER_LIFT_VY_CAP
                break

    def _start_storm_buildup(self):
        """Telegraph the strike: 9 escalating-tempo background bolts, the
        real strike at t=4.40 s, then 2 fade-away bolts as it settles."""
        self._storm_buildup_seq = [
            (0.00, "bg_left"),
            (0.80, "bg_right"),
            (1.50, "bg_left"),
            (2.10, "bg_right"),
            (2.60, "bg_left"),
            (3.05, "bg_right"),
            (3.45, "bg_left"),
            (3.80, "bg_right"),
            (4.10, "bg_left"),
            (4.40, "strike"),
            (5.40, "bg_right"),
            (6.90, "bg_left"),
        ]
        self._storm_buildup_t = 0.0
        self._storm_jolt_lockout = 25.0

    def _fire_background_lightning(self, side: int = -1):
        """Non-damaging telegraph bolt landing off to Pip's side, with
        reduced flash/shake — "the storm is cracking around him"."""
        bx, by = self.bird.x, self.bird.y
        origin_x = bx + side * random.uniform(110, 170)
        impact_x = bx + side * random.uniform(80, 150)
        impact_y = random.uniform(by - 80, by + 80)
        path = [(origin_x, 0.0)]
        segs = 18
        for i in range(1, segs):
            t = i / segs
            jx = random.uniform(-42, 42) * (1.0 - t * 0.55)
            cx = origin_x * (1 - t) + impact_x * t + jx
            cy = impact_y * t
            path.append((cx, cy))
        path.append((impact_x, impact_y))
        self.lightning_strike = {"path": path, "life": 0.32, "life_max": 0.32}
        self.weather.flash_remaining = max(self.weather.flash_remaining, 0.14)
        self.shake_mag = max(self.shake_mag, 3.5)
        self.shake_t = max(self.shake_t, 0.20)
        try:
            audio.play_thunder(volume=random.uniform(0.35, 0.55))
        except Exception:
            pass

    def _bolt_path(self, ox, oy, ix, iy, segs=20, jit=40):
        """Jagged lightning polyline from origin (ox, oy) → impact (ix, iy)."""
        path = [(ox, oy)]
        for i in range(1, segs):
            t = i / segs
            jx = random.uniform(-jit, jit) * (1.0 - t * 0.7)
            path.append((ox * (1 - t) + ix * t + jx, oy + (iy - oy) * t))
        path.append((ix, iy))
        return path

    def _side_bolt(self, base_x):
        """A flanking bolt — same layered look as the main strike, but a
        randomised length + jaggedness so it's never the same shape."""
        oy = random.uniform(0.0, GROUND_Y * 0.22)            # some start lower → shorter
        iy = random.uniform(GROUND_Y * 0.45, GROUND_Y - 18)  # end mid-air or near ground
        return self._bolt_path(base_x + random.uniform(-40, 40), oy,
                               base_x + random.uniform(-30, 30), iy,
                               segs=random.randint(13, 21),
                               jit=random.uniform(26.0, 44.0))

    def _fire_storm_jolt(self):
        """LIGHTNING STRIKES PIP — bolt + flash + hard shake + 100 points
        knocked off the SCORE (all of it if under 100) + cyan sparks + X-Ray
        Sparks skeleton flash + scorch smoke. Loss logged as a negative
        weather_jolt ledger event."""
        lost = min(100, self.score)
        if lost <= 0:
            return
        self._lightning_strikes_run += 1      # Lightning Magnet lifetime tally
        self.score = max(0, self.score - lost)
        self._proof.record(self.time_alive, -lost, "weather_jolt")

        bx, by = self.bird.x, self.bird.y
        # THREE simultaneous bolts at the climax: the main strike on Pip plus
        # two flanking bolts at absolute screen positions (Pip flies on the
        # left), each a different length + jaggedness so the sky forks.
        main = self._bolt_path(bx + random.uniform(-70, 70), 0.0, bx, by - 2,
                               segs=22, jit=42)
        side_l = self._side_bolt(random.uniform(18.0, 70.0))
        side_r = self._side_bolt(random.uniform(W * 0.62, W - 24.0))
        self.lightning_strike = {"paths": [main, side_l, side_r], "path": main,
                                 "life": 0.50, "life_max": 0.50}
        self.weather.flash_remaining = max(self.weather.flash_remaining, 0.22)
        self.shake_mag = max(self.shake_mag, 9.0)
        self.shake_t = max(self.shake_t, 0.55)
        self._storm_jolt_lockout = 25.0
        self._lightning_scorch_t = 3.7
        self._scorch_smoke_accum = 0.0
        self.bird.skeleton_flash_t = 3.50

        scatter_bx, scatter_by = self.bird.x, self.bird.y + 4
        n = min(lost, 20)
        for i in range(n):
            ang = (i / n) * math.tau + random.uniform(-0.15, 0.15)
            speed = random.uniform(200.0, 320.0)
            vx = math.cos(ang) * speed
            vy = math.sin(ang) * speed - 80.0
            self.particles.append(FlyingCoinParticle(
                scatter_bx, scatter_by, vx, vy, life=0.95,
            ))

        for _ in range(40):
            ang = random.uniform(0, math.tau)
            sp = random.uniform(140, 280)
            spark_col = random.choice((
                (220, 240, 255), (180, 220, 255),
                (255, 255, 255), (140, 200, 255),
                (255, 240, 180),
            ))
            self.particles.append(Particle(
                scatter_bx, scatter_by - 12,
                math.cos(ang) * sp, math.sin(ang) * sp,
                life=random.uniform(0.35, 0.60),
                r=random.choice((3, 3, 4)),
                color=spark_col,
                gravity=180,
            ))

        # Damage label sits to the right of Pip (sprite is 64 px wide) so the
        # "-100!" glyph and its sparkle ring don't cover him while the X-Ray
        # skeleton flash is the visual hook of the strike.
        self.float_texts.append(FloatText(
            f"-{lost}!", self.bird.x + 80, self.bird.y - 14, UI_RED,
            size=30, life=1.6, vy=-26, style="powerup",
        ))

        try:
            audio.play_thunder(volume=0.98)
            audio.play_poof()
            audio.play_magnet(volume=0.55)
        except Exception:
            pass

    def _spawn_scorch_wisp(self):
        """Light smoke puff trailing BEHIND Pip (to his left) so it streams
        away rather than covering the skeleton view during the flash."""
        bx, by = self.bird.x, self.bird.y
        ox = random.uniform(-32, -14)
        oy = random.uniform(-18, 12)
        vx = random.uniform(-40, -10)
        vy = random.uniform(-55, -25)
        col = random.choice((
            (170, 165, 175), (200, 195, 200),
            (150, 145, 155), (220, 215, 220),
            (185, 180, 190),
        ))
        self.particles.append(Particle(
            bx + ox, by + oy, vx, vy,
            life=random.uniform(0.70, 1.05),
            r=random.randint(5, 8),
            color=col,
            gravity=-30,
        ))

    # ── spawning ─────────────────────────────────────────────────────────────

    def _seed_first_pipes(self):
        # Push the seed pipes further off-screen by SPAWN_GRACE seconds of
        # scroll so the gameplay opener (cottage + parcel) has clean air
        # behind Pip before the first pillar arrives.
        offset = int(SPAWN_GRACE * SCROLL_BASE)
        x = W + 60 + offset
        spacing = self._current_spacing()
        for _ in range(3):
            self._spawn_pipe(x)
            x += spacing

    def _spawn_phantom_relief(self, x):
        """Invisible, non-colliding, non-scoring phantom pillar that takes a
        spawn slot without shifting downstream pillar numbers."""
        p = Pipe(x, GROUND_Y * 0.5, int(self._current_gap()))
        p.is_phantom = True
        p.spawn_index = self.pipes_spawned - 1
        self.pipes.append(p)

    def _spawn_pipe(self, x):
        gap_h = self._current_gap()
        # Every Nth pipe is a "coin rush": wider gap + dense coin arc, no
        # power-up. The visual announcement fires below.
        self.pipes_spawned += 1
        is_rush = (self.pipes_spawned % COIN_RUSH_INTERVAL == 0)
        # ── Clown relief empties ────────────────────────────────────────────
        if self._clown_preclear_remaining > 0:
            self._clown_preclear_remaining -= 1
            self._spawn_phantom_relief(x)
            if self._clown_preclear_remaining == 0 and self._clown_entrance_pending:
                self._clown_entrance_pending = False
                self.clown_event = ClownEvent()
            return
        if (self.clown_event is not None
                and self.clown_event.phase in ("enter", "rolling")):
            self._spawn_phantom_relief(x)
            return
        if self._clown_leadin_remaining > 0:
            self._clown_leadin_remaining -= 1
            self._spawn_phantom_relief(x)
            return
        if self._clown_outro_remaining > 0:
            self._clown_outro_remaining -= 1
            self._spawn_phantom_relief(x)
            return
        # ── Clown event slot ───────────────────────────────────────────────
        if self._clown_slot_remaining > 0:
            idx = CLOWN_SLOT_PILLARS - self._clown_slot_remaining
            self._clown_slot_remaining -= 1
            is_rush = False
            is_route_tower = idx < len(self._clown_route)
            if is_route_tower:
                route_cy, route_gap = self._clown_route[idx]
                p = Pipe(x, float(route_cy), int(route_gap))
                p.is_rush = False
                p.spawn_index = self.pipes_spawned - 1
                p.is_staff = True
                self.pipes.append(p)
                if idx == len(self._clown_route) - 1:
                    self._clown_outro_remaining = CLOWN_OUTRO_PILLARS
            if self._clown_slot_remaining == 0:
                self._clown_route = []
            if is_route_tower:
                return
        # Cycle-finale: while a finale is queued (5 pillars after the
        # day/night rollover), every pillar is forced into a coin rush.
        # The chamber path still wins if both coincide — the finale just
        # yields that one pillar; the rush counter still ticks down.
        is_finale_pillar = False
        if (self._finale_rush_remaining > 0
                and not self.genie_chamber_pending):
            is_rush = True
            is_finale_pillar = True
            self._finale_rush_remaining -= 1
        # GENIE CHAMBER takes priority over coin-rush: if a chamber is
        # pending and we'd have rolled a rush, the chamber wins and the
        # rush is skipped (no double-boost; the rush counter still ticks).
        is_chamber = self.genie_chamber_pending
        if is_chamber:
            is_rush = False
            gap_h = int(gap_h * GENIE_CHAMBER_GAP_BOOST)
        elif is_rush:
            gap_h = int(gap_h * COIN_RUSH_GAP_BOOST)
        # Pipes spawned during KFC mode get a wider collision gap so the
        # powerup is an actual gameplay reward, not just visual flair.
        # Stacks with the rush boost if both happen on the same pipe.
        kfc_spawn = self.kfc_timer > 0
        if kfc_spawn:
            gap_h = int(gap_h * KFC_GAP_BOOST)
        margin = 70
        lo = margin + gap_h // 2
        hi = GROUND_Y - margin - gap_h // 2
        # A geyser planted by the previous pillar pre-rolled this pillar's
        # gy (already inside GEYSER_GY_DELTA_MAX of the previous gap). Just
        # re-clamp to this pillar's actual gap_h margins — rush/KFC widen
        # gap_h vs. what was assumed at pre-roll time.
        if self._pending_gap_y is not None:
            gy = max(lo, min(hi, self._pending_gap_y))
            self._pending_gap_y = None
        else:
            gy = random.randint(lo, hi)
        p = Pipe(x, gy, gap_h)
        p.is_rush = is_rush
        p.is_genie_chamber = is_chamber
        # is_kfc is sticky for the pipe's lifetime - it gates the gap
        # widening (see _activate_kfc) so the wider gap outlives the
        # powerup timer. The visual reverts at timer=0 via the
        # kfc_visual gate in Pipe.draw.
        p.is_kfc = kfc_spawn
        # Rail tag: claimed at spawn if _activate_rail is force-spawning
        # pillars to fill out the 5-pillar track and this pipe isn't a
        # rush pillar.
        p.rail_active = False
        self.pipes.append(p)

        # ── Cycle-finale phantom branch ────────────────────────────────────
        # Mark the 5 finale slots as invisible / non-colliding / non-
        # scoring placeholders. The sky stays fully open across the span;
        # the FIRST phantom seeds one continuous long-rush coin formation
        # spanning all 5 slots, and the MIDDLE phantom drops the treasure
        # box at the geometric centre of the span. The early-return skips
        # the rail / chamber / per-pillar rush / coin / ramp / rock /
        # geyser branches below.
        if is_finale_pillar:
            p.is_phantom = True
            spacing = self._current_spacing()
            if self._finale_rush_remaining == CYCLE_FINALE_RUSH_PILLARS - 1:
                self._spawn_finale_long_rush_coins(p.x, p.gap_y, p.gap_h, spacing)
            mid_remaining = CYCLE_FINALE_RUSH_PILLARS - CYCLE_FINALE_BOX_INDEX - 1
            if (not self._finale_box_dropped
                    and self._finale_rush_remaining == mid_remaining):
                bx = p.x + PIPE_W * 0.5
                by = p.gap_y
                self.powerups.append(PowerUp(bx, by, kind="treasure"))
                self._finale_box_dropped = True
            return

        if getattr(self, "rail_pending", 0) > 0 and not is_rush and not is_chamber:
            p.rail_active = True
            self.rail_pipes.append(p)
            self.rail_pending -= 1
        if is_chamber:
            # Wishes don't materialise yet — only the wide-gap pillar
            # spawns. The wishes pop in with a poof when Pip approaches
            # so the player sees them appear instead of finding them
            # already floating in mid-air. See _tick_genie_chambers.
            p.wishes_spawned = False
            self.genie_chamber_pending = False
        elif is_rush:
            self._spawn_rush_coins(p)
            self._announce_rush(p)
        else:
            # Advance (or reset) the thermal-event pillar counter — the
            # telegraph clock the rock ramp + geyser gate read.
            if _thermal_intensity(self.biome_phase) > ROCK_SPAWN_THRESHOLD:
                self._thermal_pillars += 1
            else:
                self._thermal_pillars = 0
            self._spawn_coins_in_gap(p)
            self._maybe_spawn_powerup(p)
            self._maybe_spawn_ramp(p)
            self._maybe_spawn_rocks(p)
            self._maybe_spawn_geyser(p)

    def _spawn_genie_chamber_offers(self, pipe: Pipe):
        """Place KNIGHT / POISON / SKATEBOARD wishes vertically inside
        the chamber pillar's gap, in random order, centred on gap_y
        with +/-GENIE_CHAMBER_SPACING separation. Called by
        _tick_genie_chambers once Pip is within GENIE_CHAMBER_REVEAL_DIST
        of the chamber pillar so the player sees the wishes poof into
        existence rather than scroll in pre-placed."""
        kinds = ["knight", "poison", "skateboard"]
        random.shuffle(kinds)
        slot_dy = (-GENIE_CHAMBER_SPACING, 0, GENIE_CHAMBER_SPACING)
        ox = pipe.x + PIPE_W // 2
        for kind, dy in zip(kinds, slot_dy):
            oy = pipe.gap_y + dy
            offer = PowerUp(ox, oy, kind=kind)
            offer.is_genie_offer = True
            self.powerups.append(offer)
            self._spawn_genie_reveal_poof(ox, oy)
        try:
            audio._play("coin_triple", 0.95)
        except Exception:
            pass
        pipe.wishes_spawned = True

    def _tick_genie_chambers(self):
        """Materialise the 3 wishes inside any chamber pillar Pip is
        approaching. Trigger fires once per chamber, when the pillar's
        x is within GENIE_CHAMBER_REVEAL_DIST of Pip — gives the
        player ~1.5 s at SCROLL_BASE to read the wishes before they
        arrive."""
        bx = self.bird.x
        for p in self.pipes:
            if not getattr(p, "is_genie_chamber", False):
                continue
            if getattr(p, "wishes_spawned", False):
                continue
            if (p.x - bx) <= GENIE_CHAMBER_REVEAL_DIST:
                self._spawn_genie_chamber_offers(p)

    def _maybe_spawn_ramp(self, pipe: Pipe):
        """During the SKATEBOARD window, sometimes drop a wooden wedge
        on top of this pipe's LOWER pillar. 38x22 gentle incline with
        a small +/-2 px jitter so wedges look hand-placed. Right-
        aligned on the pillar so the kicker sits flush with the
        pillar's right edge."""
        if self.skateboard_timer <= 0:
            return
        if random.random() >= 0.55:
            return
        ramp_w = 38 + random.randint(-2, 2)
        ramp_h = 22 + random.randint(-2, 2)
        ramp_w = min(ramp_w, PIPE_W - 2)
        base_y = pipe.gap_y + pipe.gap_h / 2
        rx = pipe.x + PIPE_W - ramp_w
        self.ramps.append(Ramp(rx, ramp_w, ramp_h, base_y=base_y))
        pipe.has_ramp = True

    def _maybe_spawn_geyser(self, pipe: Pipe):
        # Geysers are held back until the rock field has ramped across
        # GEYSER_RAMP_PILLARS pillars — so a player always gets the ~8-pillar
        # rocks-only telegraph first. The first geyser is FORCED exactly when
        # the ramp completes (the payoff of the clue); after that they spawn
        # probabilistically, with concurrency scaling 0→GEYSER_MAX_CONCURRENT by
        # intensity so they fade out naturally on the event's falling edge.
        if self._thermal_pillars < GEYSER_RAMP_PILLARS:
            return
        intensity = _thermal_intensity(self.biome_phase)
        allowed = round(intensity * GEYSER_MAX_CONCURRENT)
        if len(self.geysers) >= max(1, allowed):
            return
        first = self._thermal_pillars == GEYSER_RAMP_PILLARS and not self.geysers
        if first or (allowed >= 1
                     and random.random() < THERMAL_SPAWN_CHANCE_MAX * intensity):
            spacing = self._current_spacing()
            # Pre-roll the NEXT pillar's gap_y now — clamped within
            # GEYSER_GY_DELTA_MAX of this pillar's gap so the column-pinned
            # bird can always make the next gap. Knowing the next gy here
            # lets us bias the column's x: when the next gap is lower the
            # column shifts right, giving the player more pre-column space
            # to dive freely (the in-column lift then drops them onto the
            # lower target with minimal post-column recovery).
            gap_h_next = self._current_gap()
            margin = 70
            lo_n = max(margin + gap_h_next // 2,
                       pipe.gap_y - GEYSER_GY_DELTA_MAX)
            hi_n = min(GROUND_Y - margin - gap_h_next // 2,
                       pipe.gap_y + GEYSER_GY_DELTA_MAX)
            if self.grow_timer > 0:
                shrink = int((GROW_SCALE - 1.0) * 30)
                lo_n = min(lo_n + shrink, hi_n)
                hi_n = max(hi_n - shrink, lo_n)
            next_gy = random.randint(lo_n, hi_n)
            self._pending_gap_y = next_gy
            shift_frac = max(0.0, min(1.0,
                             (next_gy - pipe.gap_y) / GEYSER_GY_DELTA_MAX))
            gx = (pipe.x + (PIPE_W + spacing) * 0.5
                  + shift_frac * GEYSER_GX_SHIFT_MAX)
            g = Geyser(gx, intensity)
            # ~1 in 4 vents is a dud: ground formation visible (cone + ring
            # spawned below), but no eruption + no lift. contains() already
            # gates on .active, so the lift path goes quiet for free.
            if random.random() < GEYSER_DUD_CHANCE:
                g.active = False
            self.geysers.append(g)
            # Frame the base with a little ring of rocks on both flanks so the
            # geyser reads as "surrounded", not perched on bare ground.
            for _ in range(ROCK_RING_COUNT):
                side = -1 if random.random() < 0.5 else 1
                rx = gx + side * random.uniform(24.0, 52.0)
                ry = GROUND_Y + random.uniform(0.0, 6.0)
                big = random.random() < 0.4
                v = (random.randint(3, geyser_fx.ROCK_N - 1) if big
                     else random.randint(0, 2))
                self.rocks.append(Rock(rx, ry, v))

    def _scatter_rocks(self, x_lo, x_hi, count):
        """Lay `count` rocks across [x_lo, x_hi] as natural little clusters —
        a larger anchor rock with 1-3 smaller companions huddled around it —
        rather than an even sprinkle, so the field reads as real scree."""
        # Bake the whole cluster into ONE patch surface (blitted as a single
        # sprite each frame) instead of 100s of per-rock blits.
        variants = geyser_fx.get_rock_variants()
        pad = geyser_fx.ROCK_MAX_W + 16        # cover companion offset + sprite half
        patch_x = x_lo - pad
        patch_top = GROUND_Y - 24
        patch = pygame.Surface((max(1, int(x_hi - x_lo) + 2 * pad), 44),
                               pygame.SRCALPHA)

        def _stamp(rx, ry, v):
            s, ox, oy = variants[v]
            patch.blit(s, (int(rx - patch_x - ox), int(ry - patch_top - oy)))

        placed = 0
        while placed < count:
            cx = random.uniform(x_lo, x_hi)
            for _ in range(random.randint(1, 3)):       # smaller companions (behind)
                if placed >= count:
                    break
                _stamp(cx + random.uniform(-15.0, 15.0),
                       GROUND_Y + random.uniform(0.0, 6.0),
                       random.randint(0, 3))
                placed += 1
            if placed >= count:
                break
            _stamp(cx, GROUND_Y + random.uniform(1.0, 5.0),
                   random.randint(3, geyser_fx.ROCK_N - 1))   # larger anchor (front)
            placed += 1
        self.rocks.append(RockPatch(patch_x, patch_top, patch))

    def _maybe_spawn_rocks(self, pipe: Pipe):
        # The rock field is the event's telegraph: density ramps by PILLAR
        # COUNT (not the smooth time curve) so it's countable and readable —
        # ~1-2 rocks on the first pillar, growing larger each pillar, hitting
        # the maximum right as the first geyser erupts (pillar GEYSER_RAMP_
        # PILLARS), then holding at max while the event stays active.
        if self._thermal_pillars <= 0:
            return
        frac = min(1.0, self._thermal_pillars / GEYSER_RAMP_PILLARS)
        density = frac * frac                       # quadratic ease-in: slow start, grows faster
        count = max(1, round(ROCK_PER_PILLAR_MAX * density))
        x0 = pipe.x + PIPE_W
        self._scatter_rocks(x0, x0 + self._current_spacing(), count)

    def _spawn_coins_in_gap(self, pipe: Pipe):
        prev_count = len(self.coins)
        pattern = random.choice(("arc", "line", "cluster"))
        cx = pipe.x + PIPE_W + self._current_spacing() * 0.5
        gy = pipe.gap_y
        if pattern == "arc":
            n = 5
            radius = min(70, pipe.gap_h * 0.35)
            for i in range(n):
                t = i / (n - 1)
                ang = -math.pi * 0.35 + math.pi * 0.7 * t
                x = cx + math.sin(ang) * 50
                y = gy + math.cos(ang) * radius - radius * 0.2
                self.coins.append(Coin(x, y))
        elif pattern == "line":
            n = 4
            for i in range(n):
                x = cx - 40 + i * 22
                self.coins.append(Coin(x, gy))
        else:  # cluster
            for dx, dy in ((0, 0), (-20, -14), (20, -14), (-20, 14), (20, 14)):
                self.coins.append(Coin(cx + dx, gy + dy))
        self.coins_spawned += len(self.coins) - prev_count

    def _spawn_rush_coins(self, pipe: Pipe):
        """Dense coin formation across the gap — random variant each rush."""
        prev_count = len(self.coins)
        spacing = self._current_spacing()
        cx = pipe.x + PIPE_W + spacing * 0.45
        gy = pipe.gap_y
        span = spacing * 0.85
        amp = min(pipe.gap_h * 0.32, 65)
        n = COIN_RUSH_COINS

        variant = random.choice(("wave", "s_curve", "chevron", "oval", "double_arc"))

        if variant == "wave":
            phase = random.uniform(0, math.tau)
            waves = random.uniform(1.0, 1.6)
            for i in range(n):
                t = i / (n - 1)
                x = cx - span / 2 + span * t
                y = gy + math.sin(phase + waves * math.tau * t) * amp
                self.coins.append(Coin(x, y))

        elif variant == "s_curve":
            phase = random.choice((0.0, math.pi))
            for i in range(n):
                t = i / (n - 1)
                x = cx - span / 2 + span * t
                y = gy + math.sin(phase + 3 * math.pi * t) * amp * 0.75
                self.coins.append(Coin(x, y))

        elif variant == "chevron":
            flip = random.choice((1, -1))
            for i in range(n):
                t = i / (n - 1)
                tri = 2.0 * abs(2.0 * t - 1.0) - 1.0
                x = cx - span / 2 + span * t
                y = gy + flip * amp * tri
                self.coins.append(Coin(x, y))

        elif variant == "oval":
            for i in range(n):
                theta = i / n * math.tau
                x = cx + math.cos(theta) * span * 0.32
                y = gy + math.sin(theta) * amp * 0.65
                self.coins.append(Coin(x, y))

        elif variant == "double_arc":
            half = n // 2
            rest = n - half
            for i in range(half):
                t = i / max(half - 1, 1)
                x = cx - span / 2 + span * t
                y = gy - amp * 0.4 + math.sin(math.pi * t) * amp * 0.3
                self.coins.append(Coin(x, y))
            for i in range(rest):
                t = i / max(rest - 1, 1)
                x = cx - span / 2 + span * t
                y = gy + amp * 0.4 - math.sin(math.pi * t) * amp * 0.3
                self.coins.append(Coin(x, y))

        self.coins_spawned += len(self.coins) - prev_count
        # Open a fresh Coin Blind window: tag this rush's coins and reset the
        # grab tally. Force-close any prior window — rushes are 15 pillars apart
        # so the previous one is always fully behind Pip by now.
        self._finalize_rush(force=True)
        for c in self.coins[prev_count:]:
            c.is_rush = True
        self._rush_cur_total = len(self.coins) - prev_count
        self._rush_cur_got = 0

    def _spawn_finale_long_rush_coins(self, first_phantom_x: float,
                                      center_y: float, gap_h: int,
                                      spacing: int):
        """Cycle-finale long coin rush — one continuous formation across
        the full phantom span (CYCLE_FINALE_RUSH_PILLARS pillars wide),
        replacing the per-pillar rush formations the finale used to lay
        down. Variant pool excludes 'oval' (doesn't stretch wide).
        Pattern repeats / scales internally so the long span reads as
        one shape, not N chunks."""
        prev_count = len(self.coins)
        total_span = CYCLE_FINALE_RUSH_PILLARS * spacing
        # Bracket the formation half a spacing in from each end of the
        # phantom span so the entry + exit feel like the same beat the
        # regular per-pillar rush has (formation centred between pillars,
        # not flush with them).
        cx = first_phantom_x + total_span * 0.5
        span = total_span - spacing
        n = CYCLE_FINALE_RUSH_PILLARS * COIN_RUSH_COINS
        amp = min(gap_h * 0.32, 65)
        gy = center_y

        # 'oval' from _spawn_rush_coins doesn't scale across the long
        # span (the oval collapses to a horizontal line of coins) so
        # it's excluded. The remaining four stretch cleanly.
        variant = random.choice(("wave", "s_curve", "chevron", "double_arc"))

        if variant == "wave":
            phase = random.uniform(0, math.tau)
            # 5x more wavelengths than the per-pillar wave (1.0-1.6) so
            # the long span has 5+ visible peaks instead of one.
            waves = random.uniform(5.0, 8.0)
            for i in range(n):
                t = i / (n - 1)
                x = cx - span / 2 + span * t
                y = gy + math.sin(phase + waves * math.tau * t) * amp
                self.coins.append(Coin(x, y))

        elif variant == "s_curve":
            phase = random.choice((0.0, math.pi))
            # Triple the per-pillar variant's 3π / span so the same
            # twist density carries across the 5x longer span.
            for i in range(n):
                t = i / (n - 1)
                x = cx - span / 2 + span * t
                y = gy + math.sin(phase + 9 * math.pi * t) * amp * 0.75
                self.coins.append(Coin(x, y))

        elif variant == "chevron":
            flip = random.choice((1, -1))
            # 5 chevron repeats so the zig-zag reads as motif, not a
            # single triangle stretched across two screen widths.
            repeats = CYCLE_FINALE_RUSH_PILLARS
            for i in range(n):
                t = i / (n - 1)
                tri_t = (t * repeats) % 1.0
                tri = 2.0 * abs(2.0 * tri_t - 1.0) - 1.0
                x = cx - span / 2 + span * t
                y = gy + flip * amp * tri
                self.coins.append(Coin(x, y))

        elif variant == "double_arc":
            # Two parallel arcs running the full span — upper + lower.
            # Each arc carries half the total coin count.
            half = n // 2
            rest = n - half
            for i in range(half):
                t = i / max(half - 1, 1)
                x = cx - span / 2 + span * t
                y = gy - amp * 0.4 + math.sin(math.pi * t) * amp * 0.3
                self.coins.append(Coin(x, y))
            for i in range(rest):
                t = i / max(rest - 1, 1)
                x = cx - span / 2 + span * t
                y = gy + amp * 0.4 - math.sin(math.pi * t) * amp * 0.3
                self.coins.append(Coin(x, y))

        self.coins_spawned += len(self.coins) - prev_count
        # Open a fresh Coin Blind window: tag this rush's coins and reset the
        # grab tally (force-close any prior window — rushes are 15 pillars apart,
        # so the previous one is always fully behind Pip by now).
        self._finalize_rush(force=True)
        for c in self.coins[prev_count:]:
            c.is_rush = True
        self._rush_cur_total = len(self.coins) - prev_count
        self._rush_cur_got = 0

    def _finalize_rush(self, force: bool = False):
        """Close the current Coin Rush window for the Coin Blind roast. Only
        fires once the rush is fully behind Pip (no uncollected rush coin still
        ahead), unless force-closed by the next rush spawning."""
        if self._rush_cur_total <= 0:
            return
        if not force and any(
                getattr(c, "is_rush", False) and not c.collected
                and c.x > self.bird.x for c in self.coins):
            return
        if self._rush_cur_got < 3:
            self.coin_blind = True
        self._rush_cur_total = 0
        self._rush_cur_got = 0

    def _announce_rush(self, pipe: Pipe):
        """Gold sparkle burst when a rush pipe enters from the right edge."""
        x = pipe.x - 20
        y = pipe.gap_y
        for _ in range(22):
            ang = random.uniform(0, math.tau)
            spd = random.uniform(60, 220)
            col = random.choice((PARTICLE_GOLD, COIN_LIGHT, UI_ORANGE))
            self.particles.append(Particle(
                x, y,
                math.cos(ang) * spd, math.sin(ang) * spd,
                random.uniform(0.5, 1.0),
                random.randint(2, 4),
                col, gravity=120,
            ))

    def _check_genie_milestone(self, last_scored_pipe):
        """Fires once per run when pillars_passed crosses LATE_GAME_PILLAR
        (and a separate debug one-shot at DEBUG_GENIE_PILLAR). Called from
        the pipe-pass loop with the pipe just scored, so the genie lamp
        lands in the spacing immediately after it — the player encounters
        the lamp while flying from that pillar toward the next.

        Pillar-based (not score-based) so coin pickups, lottery wins, and
        storm-jolt deductions can't shift the moment. Doesn't override
        any pre-existing powerup; the lamp just appears at the normal
        in-gap placement."""
        if (DEBUG_GENIE_PILLAR is not None
                and not self._debug_genie_milestone_fired
                and self.pillars_passed >= DEBUG_GENIE_PILLAR):
            self._debug_genie_milestone_fired = True
            self._spawn_milestone_genie(last_scored_pipe)
            return
        if self._genie_milestone_fired:
            return
        if self.pillars_passed < LATE_GAME_PILLAR:
            return
        self._genie_milestone_fired = True
        self._spawn_milestone_genie(last_scored_pipe)

    def _spawn_milestone_genie(self, last_scored_pipe):
        """Drop a genie lamp at an offscreen-right position so it scrolls
        into view like a normally-spawned powerup — no mid-screen pop-in.

        Anchors to the rightmost pipe (the same anchor a freshly-spawned
        pipe's powerup would use), but clamps to at least `W + spacing/2`
        so even when the pipe list is sparse (degenerate state) the lamp
        still starts off-screen.

        Used by both the production milestone (pillar 65) and the debug
        one-shot (pillar 5)."""
        spacing = self._current_spacing()
        anchor_pipe = self.pipes[-1] if self.pipes else last_scored_pipe
        gx = max(anchor_pipe.x + PIPE_W + spacing * 0.5,
                 W + spacing * 0.5)
        gy = anchor_pipe.gap_y
        self.powerups.append(PowerUp(gx, gy, kind="genie"))
        # Set the standard cooldown so the next regular spawn doesn't
        # immediately stack a second powerup right behind the lamp.
        self.powerup_cooldown = POWERUP_COOLDOWN

    def _maybe_spawn_powerup(self, pipe: Pipe):
        if self.powerup_cooldown > 0:
            return
        if random.random() >= self._current_powerup_chance():
            return
        # Score-gated kinds drop out of the pool until the run's score
        # crosses each kind's threshold. Lets late-game pickups stay
        # rare for new players while showing up reliably once the run
        # has built momentum. POWERUP_REPLACED_AT is the inverse:
        # kinds drop OUT once the score crosses their replacement
        # threshold (used to swap magnet -> megamagnet at 250).
        kinds, weights = [], []
        for k, w in POWERUP_WEIGHTS:
            if POWERUP_SCORE_GATES.get(k, 0) > self.score:
                continue
            replaced_at = POWERUP_REPLACED_AT.get(k)
            if replaced_at is not None and self.score >= replaced_at:
                continue
            kinds.append(k)
            weights.append(w)
        # Secret late-game tier: only enters the roll once a genie
        # milestone has fired (production at pillar LATE_GAME_PILLAR or
        # the debug one-shot at DEBUG_GENIE_PILLAR). Kept out of
        # POWERUP_WEIGHTS so the gate can't be bypassed.
        if self._genie_milestone_fired or self._debug_genie_milestone_fired:
            for k, w in SECRET_POWERUP_WEIGHTS:
                kinds.append(k)
                weights.append(w)
        if not kinds:
            return
        kind = random.choices(kinds, weights=weights, k=1)[0]
        x = pipe.x + PIPE_W + self._current_spacing() * 0.5 + random.uniform(-20, 20)
        y = pipe.gap_y + random.uniform(-10, 10)
        self.powerups.append(PowerUp(x, y, kind=kind))
        self.powerup_cooldown = POWERUP_COOLDOWN

    # ── public control ──────────────────────────────────────────────────────

    def flap(self):
        if not self.game_over:
            # A tap during the "get ready" freeze both lifts the bird and
            # kicks the world into motion immediately.
            if self.ready_t > 0:
                self.ready_t = 0.0
            sign = -1 if self.reverse_timer > 0 else 1
            self.bird.flap(gravity_sign=sign)
            self.flap_count += 1
            self._flap_window_n += 1
            if self._flap_window_n > self.max_flaps_per_sec:
                self.max_flaps_per_sec = self._flap_window_n
            audio.play_flap()
            # SKATEBOARD tricks. The detector handles 4 tap patterns:
            #   1) 3 FAST taps   (gap ≤ BACKFLIP_TAP_WINDOW)   → backflip
            #   2) 2 MEDIUM taps (POPSHUVIT_TAP_GAP_MIN-MAX)  → pop shuvit
            #   3) 2 SLOW taps   (KICKFLIP_TAP_GAP_MIN-MAX)   → kickflip
            #   4) 2 VERY-SLOW   (HEELFLIP_TAP_GAP_MIN-MAX)   → heelflip
            # Only tracked while the buff is active and no flip is
            # already in progress.
            if (self.skateboard_timer > 0
                    and self.bird.backflip_t <= 0
                    and self.bird.kickflip_t <= 0
                    and self.bird.heelflip_t <= 0
                    and self.bird.popshuvit_t <= 0):
                self._track_skateboard_tricks()

    def _track_skateboard_tricks(self):
        now = self._idle_t
        gap = now - self._last_tap_t
        if gap <= BACKFLIP_TAP_WINDOW:
            self._tap_streak += 1
        else:
            self._tap_streak = 1
        self._last_tap_t = now
        if self._tap_streak >= 3:
            self._trigger_backflip()
            self._tap_streak = 0
            return
        if POPSHUVIT_TAP_GAP_MIN <= gap <= POPSHUVIT_TAP_GAP_MAX:
            self._trigger_popshuvit()
            return
        if KICKFLIP_TAP_GAP_MIN <= gap <= KICKFLIP_TAP_GAP_MAX:
            self._trigger_kickflip()
            return
        if HEELFLIP_TAP_GAP_MIN <= gap <= HEELFLIP_TAP_GAP_MAX:
            self._trigger_heelflip()

    def _trigger_backflip(self):
        self.bird.backflip_t = BACKFLIP_DURATION
        self.bird.backflip_dur = BACKFLIP_DURATION
        audio.play_backflip()
        self._record_trick("backflip")
        self._spawn_trick_bubble("BACKFLIP!")

    def _trigger_kickflip(self):
        self.bird.kickflip_t = KICKFLIP_DURATION
        self.bird.kickflip_dur = KICKFLIP_DURATION
        audio.play_backflip()
        self._record_trick("kickflip")
        self._spawn_trick_bubble("KICKFLIP!")

    def _trigger_heelflip(self):
        self.bird.heelflip_t = HEELFLIP_DURATION
        self.bird.heelflip_dur = HEELFLIP_DURATION
        audio.play_backflip()
        self._record_trick("heelflip")
        self._spawn_trick_bubble("HEELFLIP!")

    def _trigger_popshuvit(self):
        self.bird.popshuvit_t = POPSHUVIT_DURATION
        self.bird.popshuvit_dur = POPSHUVIT_DURATION
        audio.play_backflip()
        self._record_trick("popshuvit")
        self._spawn_trick_bubble("POP SHUVIT!")

    def _record_trick(self, kind: str):
        # One landed trick: bump the run total and note the distinct type so a
        # "land all four types in one run" goal can read len(tricks_landed_types).
        self.tricks_landed += 1
        self.tricks_landed_types.add(kind)

    # Trick bubble anchor zones — RIGHT of the score (original POW!
    # badge home) or a mirror LEFT anchor below the coins pill. Each
    # bubble picks a side so multi-trick stacks spread across both
    # corners instead of piling onto one.
    _TRICK_ANCHOR_X_RIGHT = W - 70
    _TRICK_ANCHOR_X_LEFT = 70
    _TRICK_ANCHOR_Y = 165

    def _spawn_trick_bubble(self, label: str):
        anchor_x = (self._TRICK_ANCHOR_X_LEFT
                    if random.random() < 0.5
                    else self._TRICK_ANCHOR_X_RIGHT)
        ox = random.randint(-10, 10)
        oy = random.randint(-10, 10)
        tilt = random.uniform(-18, 18)
        self.trick_bubbles.append(TrickBubble(
            label,
            anchor_x + ox,
            self._TRICK_ANCHOR_Y - self._skateboard_lift_y + oy,
            tilt_deg=tilt,
        ))

    # ── update ──────────────────────────────────────────────────────────────

    def update(self, dt):
        self._idle_t += dt
        # Dead-Pip cross-fade ticks every frame regardless of game state —
        # bird physics is frozen after death so this is the only thing
        # advancing the alpha blend in Bird.draw.
        if 0 < self.bird.death_fade_t < DEATH_FADE_DURATION:
            self.bird.death_fade_t = min(
                DEATH_FADE_DURATION, self.bird.death_fade_t + dt)
        # Slowmo scales the *world* (scroll, entity velocity, entity spin,
        # pickup physics, AND the biome day/night cycle) — not the bird's
        # input physics. Lets players still flap responsively while
        # everything else crawls.
        world_scale = SLOWMO_SCALE if self.slowmo_timer > 0 else 1.0
        sdt = dt * world_scale
        # The biome cycle only advances once the run has actually started.
        # While ready_t > 0 the sky stays frozen at the dawn palette — the
        # day/night arc was rolling forward earlier even when Pip was
        # still on the post-house porch waiting for input. Advanced by sdt
        # (not raw dt) so the day cycle slows alongside everything else
        # the slowmo buff scales — otherwise rain / lightning / snow land
        # at earlier pillars during slowmo than the progression chart
        # predicts.
        if self.ready_t <= 0:
            self.biome_time += sdt
        # Cycle-finale rollover detect: when the day/night phase wraps
        # from the late-night band (> HI) back into early dawn (< LO),
        # queue a CYCLE_FINALE_RUSH_PILLARS-pillar coin rush; the
        # middle pillar drops the treasure box (see _spawn_pipe).
        # Sampled every frame so the detect lands within one frame of
        # the actual rollover.
        _new_phase = self.biome_phase
        if (self._last_biome_phase > CYCLE_FINALE_PHASE_HI
                and _new_phase < CYCLE_FINALE_PHASE_LO):
            self._finale_rush_remaining = CYCLE_FINALE_RUSH_PILLARS
            self._finale_box_dropped = False
            # Day counter ticks once per cycle wrap. The banner that
            # rides the chest pickup later in this same finale rush
            # reads max(1, cycles_completed) so the first cycle the
            # player survives reads "DAY 1 COMPLETE!".
            self.cycles_completed += 1
            # Spawn celebration items NOW (not later when the chest
            # actually drops) so the LEFT real flanking pillar — which
            # is still on-screen at this wrap moment — visibly carries
            # the bunting's left rope-end as it scrolls past. By the
            # time the chest spawns the LEFT pillar has scrolled
            # ~2*spacing left and is leaving the screen; spawning the
            # bunting then makes it pop into existence mid-air.
            # Predicted positions are deterministic because pillars
            # scroll at one rate and stay at one spacing apart in
            # world-x: from LEFT.x, the chest lands at LEFT.x +
            # BOX_INDEX*spacing + 1 and the RIGHT real flanker at
            # LEFT.x + (RUSH_PILLARS+1)*spacing.
            if self.pipes:
                left_pillar = self.pipes[-1]
                spacing = self._current_spacing()
                # Pipes effectively land at world-x = W + 60 (the clamp
                # at the spawn site below — see line ~1528:
                # `max(prev.x + spacing, W + 60)`). The clamp ALWAYS
                # fires because the spawn trigger fires when
                # prev.x < W - spacing, so prev.x + spacing < W < W + 60.
                # The resulting world-x gap between two consecutive
                # pillars is therefore (W + 60) - (W - spacing) =
                # spacing + 60, not the nominal spacing.
                effective_spacing = spacing + 60
                left_x = left_pillar.x + PIPE_W * 0.5
                left_y = left_pillar.gap_y - left_pillar.gap_h * 0.5
                # finish_x = future chest centre. With
                # CYCLE_FINALE_BOX_INDEX phantoms before the chest,
                # that's (BOX_INDEX + 1) effective-spacings past LEFT.
                finish_x = left_x + (CYCLE_FINALE_BOX_INDEX + 1) * effective_spacing
                # right_x = predicted RIGHT real pillar centre =
                # (RUSH_PILLARS + 1) effective-spacings past LEFT.
                # Symmetric y at both ends — pillar gaps vary < 30 px,
                # well within the rope sag's visual tolerance.
                right_x = left_x + (CYCLE_FINALE_RUSH_PILLARS + 1) * effective_spacing
                right_y = left_y
                from game.entities import (
                    CelebrationGroundMarker, CelebrationBunting,
                    CelebrationBalloonCluster, CelebrationCrowd)
                day = max(1, self.cycles_completed)
                # Band-spanning decor (bunting rope, balloons, crowd) anchors
                # its LEFT edge to the FIRST phantom rush pillar — one
                # effective-spacing past the on-screen left flanker — rather
                # than the flanker itself. That pillar is always off the right
                # screen edge at the wrap moment, so the whole celebration
                # SCROLLS IN from the right like real scenery instead of
                # popping onto the playfield. Both band ends are predicted
                # rush-pillar positions, so the rope still hangs between pillar
                # tips as they arrive; the ground marker already lives at
                # finish_x (off-screen).
                decor_left_x = left_x + effective_spacing
                self.celebration_ground_markers.append(
                    CelebrationGroundMarker(finish_x, day))
                self.celebration_buntings.append(
                    CelebrationBunting(decor_left_x, left_y, right_x, right_y))
                self.celebration_balloon_clusters.append(
                    CelebrationBalloonCluster(decor_left_x, right_x))
                self.celebration_crowds.append(
                    CelebrationCrowd(decor_left_x, right_x, finish_x=finish_x))
            # Re-arm the clown event for the new day.
            self._clown_fired_this_cycle = False
        # Clown event trigger: fires once per day when the phase crosses the
        # pre-clear anchor so the jester enters a clean field.
        if (not self._clown_fired_this_cycle
                and self._last_biome_phase < CLOWN_PRECLEAR_PHASE <= _new_phase):
            self._clown_fired_this_cycle = True
            self._clown_preclear_remaining = CLOWN_PRECLEAR_PILLARS
            self._clown_entrance_pending = True
        if self.clown_event is not None:
            self.clown_event.update(self, sdt)
            if self.clown_event.done:
                self.clown_event = None
        self._last_biome_phase = _new_phase
        # Weather tracks biome phase, scales with sdt so slowmo softens rain too.
        self.weather.update(sdt, self.biome_phase)
        # Ambient scenes (V-flocks, fireworks, balloon, parrots, blossoms,
        # campfire) — sparse, phase-gated. Campfire uses bg_scroll to ride
        # the foreground parallax layer so it reads as world scenery.
        self.ambient.update(sdt, self.biome_phase, self.biome_palette,
                            self.bg_scroll)

        # While the "get ready" prompt is up, hold everything still except
        # a tiny idle animation on the bird. The freeze waits indefinitely
        # for the player's first flap (no auto-expiring countdown).
        if self.ready_t > 0 and not self.game_over:
            # Gentle bob without physics integration. Driven by idle_t so it
            # keeps moving even though biome_time is frozen.
            self.bird.vy = 0
            self.bird.y = H * 0.42 + math.sin(self._idle_t * 4.0) * 6
            self.bird.frame_t += dt * 6.0
            # Keep particles / float-texts ticking so nothing freezes visually.
            for p in self.particles:
                p.update(dt)
            self.particles = [p for p in self.particles if p.alive()]
            for t in self.float_texts:
                t.update(dt)
            self.float_texts = [t for t in self.float_texts if t.alive()]
            for b in self.trick_bubbles:
                b.update(dt)
            self.trick_bubbles = [b for b in self.trick_bubbles if b.alive()]
            return

        if not self.game_over:
            sign = -1 if self.reverse_timer > 0 else 1
            self.bird.update(dt, gravity_sign=sign)  # bird physics at real time
            # Terminal poison: Bird.update ramps poison_t toward 1.0; the HUD
            # poison bar reads the same ramp and disappears at t=1.0. From
            # that point Bird.flap is guarded — Pip can no longer rise, so
            # gravity carries him into a pillar / the ground and the normal
            # collision pipeline triggers _die.

            # Weather → gameplay: rain coin-shake / Pip shiver / flap dampen,
            # snow tailwind + back-snow, and the storm-jolt scheduling.
            self._apply_weather_effects(sdt)

            # Scripted demo beat (clown → dice → route → fall); spawns its own
            # pillars, so the auto-spawn block below is gated off for it.
            if self.demo is not None:
                self.demo.update(self, sdt)

            speed = self._current_scroll() if not self.game_over else 0
            self.bg_scroll += speed * sdt
            # Advance the sidewalk crowd in lockstep with the ground (sdt carries
            # slow-mo; speed carries rail/skate/weather), so planted entities stay
            # pixel-locked and walkers move relative to the ground.
            self.crowd.update(self.bg_scroll, speed, sdt,
                              self.biome_phase, self.biome_time)
            for p in self.pipes:
                p.x -= speed * sdt
            for r in self.ramps:
                r.x -= speed * sdt
            for c in self.coins:
                c.x -= speed * sdt
                c.update(sdt)
            for m in self.powerups:
                m.x -= speed * sdt
                m.update(sdt)
            # Cycle-finale party decor — ground marker, bunting, balloon
            # cluster — all ride world scroll so they stay parked over
            # the phantom gap as it crosses the playfield. The bunting
            # and balloon cluster ALSO advance their internal time
            # (balloon bob + upward drift) on each update.
            scroll_dx = speed * sdt
            for gm in self.celebration_ground_markers:
                gm.update(sdt, scroll_dx)
            self.celebration_ground_markers = [
                gm for gm in self.celebration_ground_markers if gm.alive()
            ]
            for cb in self.celebration_buntings:
                cb.update(sdt, scroll_dx)
            self.celebration_buntings = [
                cb for cb in self.celebration_buntings if cb.alive()
            ]
            for bc in self.celebration_balloon_clusters:
                bc.update(sdt, scroll_dx)
            self.celebration_balloon_clusters = [
                bc for bc in self.celebration_balloon_clusters if bc.alive()
            ]
            for cc in self.celebration_crowds:
                cc.update(sdt, scroll_dx)
            self.celebration_crowds = [
                cc for cc in self.celebration_crowds if cc.alive()
            ]
            # Genie chamber wishes pop in when Pip gets close enough so
            # the player sees them materialise instead of finding them
            # pre-placed in the gap.
            self._tick_genie_chambers()
            for gy in self.geysers:
                gy.x -= speed * sdt
                gy.update(sdt)
            for r in self.rocks:
                r.x -= speed * sdt
            # Morning-thermal updraft: continuous lift while Pip is inside an
            # active geyser column (capped, zone ends mid-screen — see method).
            self._apply_thermal_lift(dt)

            # Magnet pull — tug uncollected coins toward the bird.
            # Either timer triggers; the bigger radius wins if both
            # are somehow active simultaneously (shouldn't happen
            # under the swap-at-250 rule but defensive anyway).
            if self.magnet_timer > 0 or self.megamagnet_timer > 0:
                self._apply_magnet(dt)

            # cull off-screen — but keep rail-active pipes alive past
            # the normal off-screen threshold so the polyline's left
            # bridge segment is fully off-screen before its anchor
            # pipe culls. Without this, when the player flies above
            # the cart without locking, each rail pipe culls the
            # instant its right edge crosses the left screen edge,
            # and the still-on-screen ~100-150 px bridge from that
            # pipe to the next pipe "pops" off, making chunks of
            # the track disappear behind the parrot.
            # While Pip is locked on the cart, keep rail pipes
            # indefinitely past off-screen so the polyline extends
            # far behind during the ride for visual flair.
            self.pipes = [
                p for p in self.pipes
                if not p.off_screen()
                or (getattr(p, "rail_active", False)
                    and (self.bird.cart_locked or p.x + PIPE_W > -300))
            ]
            # Refresh rail_pipes every frame so the renderer still sees
            # the on-screen tail of tagged pipes after expiry.
            self.rail_pipes = [
                p for p in self.pipes if getattr(p, "rail_active", False)
            ]
            # Drop the parked-cart reference once its host pillar has
            # finally been culled off-screen, so we don't keep drawing
            # the cart at a frozen position after the pipe is gone.
            if (self.rail_cart_pipe is not None
                    and self.rail_cart_pipe not in self.pipes):
                self.rail_cart_pipe = None
            self.coins = [c for c in self.coins if c.x + 20 > 0 and not c.collected]
            self.powerups = [
                m for m in self.powerups
                if m.x + 20 > 0
                and (not m.collected or m.claimed_anim_t > 0.0)
            ]
            self.geysers = [gy for gy in self.geysers if not gy.off_screen()]
            self.rocks = [r for r in self.rocks if not r.off_screen()]

            # spawn more pipes. Suppressed while the rail powerup is
            # active so no untagged pipe slips between the pre-spawned
            # track and the right edge. After the ride ends the pipe
            # list may be empty (all rail pipes culled); re-seed one
            # fresh pipe so the player has something to navigate.
            spacing = self._next_spacing()
            if self.demo is None and not self.bird.cart_active:
                # Warren towers must bypass the W+60 spawn clamp so the
                # tight fused spacing isn't silently inflated.
                warren_next = (self._clown_leadin_remaining == 0
                               and self._clown_outro_remaining == 0
                               and self._clown_slot_remaining > 0
                               and (CLOWN_SLOT_PILLARS - self._clown_slot_remaining)
                               < len(self._clown_route))
                if not self.pipes:
                    self._spawn_pipe(W + 60)
                elif warren_next:
                    if self.pipes[-1].x + spacing <= W + 60:
                        self._spawn_pipe(max(self.pipes[-1].x + spacing, W + 60))
                elif self.pipes[-1].x < W - spacing:
                    # Spawn off-screen on the right: after a rail ride the
                    # last tagged pipe sits near Pip (x≈80) so the natural
                    # `prev.x + spacing` lands inside the screen, popping the
                    # next pillar in mid-air. Clamp to at least W+60 so the
                    # new pillar always enters the playfield by scrolling.
                    next_x = max(self.pipes[-1].x + spacing, W + 60)
                    self._spawn_pipe(next_x)

            # scoring: pass a pipe
            bx = self.bird.x
            by = self.bird.y
            for p in self.pipes:
                # Cycle-finale phantom slots don't score — they're "not
                # there" from the player's POV; the chest's +100 is the
                # span's reward, not 5 pillar passes.
                if p.is_phantom:
                    continue
                if not p.scored and p.x + PIPE_W < bx:
                    p.scored = True
                    self.score += 1
                    self.pillars_passed += 1
                    # Per-activation buff-clearing tallies (Bullet Time / Ghost
                    # Rider). Timers are decremented later this frame, so a
                    # still-positive value means the buff was active at pass time.
                    if self.slowmo_timer > 0:
                        self._slowmo_run_pillars += 1
                        self.max_pillars_in_slowmo = max(
                            self.max_pillars_in_slowmo, self._slowmo_run_pillars)
                    if self.ghost_timer > 0:
                        self._ghost_run_pillars += 1
                        self.max_pillars_in_ghost = max(
                            self.max_pillars_in_ghost, self._ghost_run_pillars)
                    self._check_genie_milestone(p)
                    # UMBRELLA: fixed-pillar spawn (both pillars inside the
                    # rain block, so the "only while raining" rule is
                    # honoured by construction). Membership-test fires
                    # exactly once per listed pillar.
                    if self.pillars_passed in UMBRELLA_SPAWN_PILLARS:
                        self._spawn_storm_umbrella()
                    self._proof.record(self.time_alive, 1, "pipe")
                    # RAIL: count down the per-ride pillar budget. Fires
                    # whether or not Pip locked — if all 5 tagged pipes
                    # pass without a lock the powerup expires silently.
                    if (self.bird.cart_active
                            and getattr(p, "rail_active", False)
                            and self.rail_pillars_left > 0):
                        self.rail_pillars_left -= 1
                        if self.rail_pillars_left == 0:
                            self._end_rail_ride()

            # Near-miss detection: once per pipe, flag if the bird was within
            # a narrow band of either edge without hitting. Fires as the pipe
            # passes behind the bird so it doesn't double-count mid-flight.
            for p in self.pipes:
                # Phantoms have no visible edges to graze.
                if p.is_phantom:
                    continue
                pid = id(p)
                if self._near_miss_flags.get(pid):
                    continue
                # Only check pipes currently overlapping the bird's x-range
                if p.x < bx + BIRD_R and p.x + PIPE_W > bx - BIRD_R:
                    gap_top = p.gap_y - p.gap_h / 2
                    gap_bot = p.gap_y + p.gap_h / 2
                    # Distance from bird to nearest pipe edge vertically
                    d_top = by - gap_top  # positive if below the top edge
                    d_bot = gap_bot - by  # positive if above the bot edge
                    margin = 10
                    if 0 < d_top < margin or 0 < d_bot < margin:
                        self.near_misses += 1
                        self._near_miss_flags[pid] = True

            # Time alive
            self.time_alive += dt

            # Wall of Shame: tumbling 1-second window for the worst flap burst.
            self._flap_window_t += dt
            if self._flap_window_t >= 1.0:
                self._flap_window_t -= 1.0
                self._flap_window_n = 0

            # collisions
            self._check_collisions()

            # pickups
            self._check_pickups()

            # timers (real time, not scaled — the buffs shouldn't self-extend).
            if self.triple_timer > 0:
                self.triple_timer = max(0.0, self.triple_timer - dt)
            self.bird.triple_active = self.triple_timer > 0
            if self.magnet_timer > 0:
                self.magnet_timer = max(0.0, self.magnet_timer - dt)
            if self.megamagnet_timer > 0:
                self.megamagnet_timer = max(0.0, self.megamagnet_timer - dt)
            if self.slowmo_timer > 0:
                self.slowmo_timer = max(0.0, self.slowmo_timer - dt)
            if self.kfc_timer > 0:
                self.kfc_timer = max(0.0, self.kfc_timer - dt)
                if self.kfc_timer == 0:
                    self._spawn_poof(self.bird.x, self.bird.y)
            self.bird.kfc_active = self.kfc_timer > 0
            if self.ghost_timer > 0:
                self.ghost_timer = max(0.0, self.ghost_timer - dt)
            self.bird.ghost_active = self.ghost_timer > 0
            if self.grow_timer > 0:
                self.grow_timer = max(0.0, self.grow_timer - dt)
            self.bird.grow_active = self.grow_timer > 0
            if self.reverse_timer > 0:
                self.reverse_timer = max(0.0, self.reverse_timer - dt)
            if self.shrink_timer > 0:
                self.shrink_timer = max(0.0, self.shrink_timer - dt)
            self.bird.shrink_active = self.shrink_timer > 0
            # SKATEBOARD: timer + slide-boost envelope (attack while grinding,
            # release otherwise) + activation overlay timers.
            if self.skateboard_timer > 0:
                self.skateboard_timer = max(0.0, self.skateboard_timer - dt)
            self.bird.skateboard_active = self.skateboard_timer > 0
            if self.bird.skateboard_active and self._sliding_this_frame:
                self.slide_boost = min(
                    1.0, self.slide_boost + dt / SKATE_SLIDE_ATTACK)
            else:
                self.slide_boost = max(
                    0.0, self.slide_boost - dt / SKATE_SLIDE_RELEASE)
            # Grind landings — first frame Pip starts sliding while the
            # skateboard buff is active. Roll once on landing for a
            # NOSE / TAIL grind callout; both share the gold palette in
            # TRICK_BUBBLE_PALETTE. grind_type latches so the bubble
            # only fires once per slide; cleared on slide-end below.
            if (self._sliding_this_frame
                    and not self._sliding_prev_frame
                    and self.skateboard_timer > 0
                    and self.bird.grind_type is None):
                if random.random() < 0.40:
                    gtype = random.choice(("nose", "tail"))
                    self.bird.grind_type = gtype
                    self._spawn_trick_bubble(f"{gtype.upper()} GRIND!")
            if (not self._sliding_this_frame
                    and self._sliding_prev_frame
                    and self.bird.grind_type is not None):
                self.bird.grind_type = None
            self._sliding_prev_frame = self._sliding_this_frame
            if self.skateboard_caption_t > 0:
                self.skateboard_caption_t = max(
                    0.0, self.skateboard_caption_t - dt)
                if self.skateboard_caption_t <= 0:
                    self.skateboard_caption_overlay = None
            if self.skateboard_burst_t > 0:
                self.skateboard_burst_t = max(
                    0.0, self.skateboard_burst_t - dt)
                if self.skateboard_burst_t <= 0:
                    self.skateboard_burst_surface = None
            # KNIGHT: buff timer + post-revive collision grace.
            if self.knight_timer > 0:
                self.knight_timer = max(0.0, self.knight_timer - dt)
            self.bird.knight_active = self.knight_timer > 0
            if self.knight_invuln > 0:
                self.knight_invuln = max(0.0, self.knight_invuln - dt)
            if self.lives_invuln > 0:
                self.lives_invuln = max(0.0, self.lives_invuln - dt)
            # Sync flicker: bird is hidden on the second half of each
            # LIVES_FLICKER_HZ period while the i-frame window is active.
            _lperiod = 1.0 / LIVES_FLICKER_HZ
            self.bird.lives_flicker_visible = (
                self.lives_invuln <= 0
                or (self.lives_invuln % _lperiod) < _lperiod * 0.5
            )
            if self.umbrella_timer > 0:
                self.umbrella_timer = max(0.0, self.umbrella_timer - dt)
            self.bird.umbrella_active = self.umbrella_timer > 0
            # GENIE: tick + cull companion conjurer actors.
            for g in self.genie_actors:
                g.update(dt)
            self.genie_actors = [g for g in self.genie_actors if g.alive()]
            # Lottery reveal ticks every frame regardless of any other
            # timer. _apply_lottery_result fires once at the reveal
            # mark; the dict lingers a moment after so the confetti /
            # tier label still renders, then clears.
            if self.lottery_anim is not None:
                self.lottery_anim["t"] += dt
                if (not self.lottery_anim["applied"]
                        and self.lottery_anim["t"] >= LOTTERY_REVEAL_TIME):
                    self._apply_lottery_result()
                    self.lottery_anim["applied"] = True
                if self.lottery_anim["t"] >= LOTTERY_REVEAL_TIME + 1.4:
                    self.lottery_anim = None
            if self.powerup_cooldown > 0:
                self.powerup_cooldown -= dt
            if self.hit_flash > 0:
                self.hit_flash = max(0.0, self.hit_flash - dt)
            # Lightning bolt: decay its visual life; expire at 0.
            if self.lightning_strike is not None:
                self.lightning_strike["life"] -= dt
                if self.lightning_strike["life"] <= 0:
                    self.lightning_strike = None
            # Scorch aftermath: emit ~40 smoke wisps/s off Pip while active.
            if self._lightning_scorch_t > 0:
                self._lightning_scorch_t = max(0.0, self._lightning_scorch_t - dt)
                self._scorch_smoke_accum += dt
                while self._scorch_smoke_accum >= 0.025:
                    self._scorch_smoke_accum -= 0.025
                    self._spawn_scorch_wisp()
        else:
            # freeze world but let particles + float texts drift
            pass

        # shake decay
        if self.shake_t > 0:
            self.shake_t -= dt
            if self.shake_t <= 0:
                self.shake_mag = 0.0

        # particles and float texts
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.alive()]
        for t in self.float_texts:
            t.update(dt)
        self.float_texts = [t for t in self.float_texts if t.alive()]
        for b in self.trick_bubbles:
            b.update(dt)
        self.trick_bubbles = [b for b in self.trick_bubbles if b.alive()]
        # Cycle-finale celebration entities — banner + garland share a
        # 1.4 s envelope. Second-wave coin storm fires 0.30 s after the
        # chest pickup (drains here so it tracks gameplay dt, not real
        # time — slow-mo stretches the wait too).
        for tb in self.treasure_banners:
            tb.update(dt)
        self.treasure_banners = [
            tb for tb in self.treasure_banners if tb.alive()]
        for g in self.celebration_garlands:
            g.update(dt)
        # Drop the garland if either pillar ref has been culled off-screen
        # — anchors would dangle on a freed Pipe otherwise. The bunting,
        # balloon cluster, and ground marker use world-x coords (not pipe
        # refs) so they are scrolled + culled in the scroll loop above
        # alongside coins / powerups.
        live_pipes = set(id(p) for p in self.pipes)
        self.celebration_garlands = [
            g for g in self.celebration_garlands
            if g.alive()
            and id(g.left) in live_pipes
            and id(g.right) in live_pipes
        ]
        if self._treasure_second_wave_t > 0:
            self._treasure_second_wave_t -= dt
            if self._treasure_second_wave_t <= 0:
                self._treasure_second_wave_t = 0.0
                self._fire_treasure_second_wave()

    def world_idle_tick(self, dt):
        """Run the background without handling bird death/pipe spawning
        logic — used by the Menu scene to keep visuals alive."""
        self.biome_time += dt
        self.weather.update(dt, self.biome_phase)
        self.bg_scroll += SCROLL_BASE * 0.5 * dt
        # Keep the crowd alive on the menu too (no slow-mo here → sdt == dt).
        self.crowd.update(self.bg_scroll, SCROLL_BASE * 0.5, dt,
                          self.biome_phase, self.biome_time)
        self.ambient.update(dt, self.biome_phase, self.biome_palette,
                            self.bg_scroll)
        for p in self.pipes:
            p.x -= SCROLL_BASE * 0.25 * dt
        for c in self.coins:
            c.x -= SCROLL_BASE * 0.25 * dt
            c.update(dt)
        for m in self.powerups:
            m.x -= SCROLL_BASE * 0.25 * dt
            m.update(dt)
        self.pipes = [p for p in self.pipes if not p.off_screen()]
        self.ramps = [r for r in self.ramps if not r.off_screen()]
        self.coins = [c for c in self.coins if c.x + 20 > 0]
        self.powerups = [m for m in self.powerups if m.x + 20 > 0]
        if self.pipes and self.pipes[-1].x < W - PIPE_SPACING:
            self._spawn_pipe(self.pipes[-1].x + PIPE_SPACING)
        # Geysers + rocks are gameplay-window elements only; the cosmetic menu
        # background doesn't scroll/cull them, so don't let _spawn_pipe
        # accumulate any (and keep the telegraph counter from pre-advancing).
        self.geysers.clear()
        self.rocks.clear()
        self._thermal_pillars = 0
        self._pending_gap_y = None

        # animate bird gently (bobbing)
        self.bird.frame_t += dt * 8.0
        self.bird.y = H * 0.42 + math.sin(self.bg_scroll * 0.05) * 12
        self.bird.vy = -math.cos(self.bg_scroll * 0.05) * 40

        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.alive()]

    # ── collisions ───────────────────────────────────────────────────────────

    def bird_radius(self) -> float:
        if self.grow_timer > 0:
            return BIRD_R * GROW_SCALE
        if self.shrink_timer > 0:
            return BIRD_R * SHRINK_SCALE
        return BIRD_R

    def _check_collisions(self):
        bx, by = self.bird.x, self.bird.y
        br = self.bird_radius()
        # SKATEBOARD: while skating Pip grinds surfaces instead of dying on
        # them. `_sliding_this_frame` is reset each frame and flipped True by
        # the ground / pillar-top snaps below so update() can ramp the
        # slide-boost up while he's actually grinding and fade it otherwise.
        skating = self.skateboard_timer > 0
        self._sliding_this_frame = False
        # Ceiling: clamp Pip and zero upward velocity instead of killing.
        # Bonking the top edge feels accidental and was a recurring "unfair
        # death" complaint; the ground still kills.
        if by - br < 0:
            self.bird.y = br
            if self.bird.vy < 0:
                self.bird.vy = 0.0
            by = self.bird.y
            # Count one bonk per contact (rising edge), not every clamped frame.
            if not self._was_ceiling_clamped:
                self.ceiling_hits += 1
            self._was_ceiling_clamped = True
        else:
            self._was_ceiling_clamped = False
        # KNIGHT grace: brief window after a revive where Pip is immune to
        # ground + pipe collisions so he can clear the obstacle that hit him.
        if self.knight_invuln > 0:
            return
        # LIVES grace: same immunity window granted after spending a heart,
        # so Pip has time to fly clear of the pipe that hit him.
        if self.lives_invuln > 0:
            return
        # SKATEBOARD ramp surface: while skating, snap Pip to any wedge
        # he's currently over so he rolls UP the slope, before the
        # generic ground / pillar checks run.
        if skating and self.ramps:
            for r in self.ramps:
                if r.x <= bx <= r.x + r.w:
                    surf_y = r.surface_y_at(bx)
                    if by + br > surf_y - 1 and self.bird.vy >= -50:
                        self.bird.y = surf_y - br
                        self.bird.vy = 0.0
                        by = self.bird.y
                        self._sliding_this_frame = True
                    break
        if by + br > GROUND_Y:
            if skating:
                # Slide along the ground instead of dying.
                self.bird.y = GROUND_Y - br
                self.bird.vy = 0.0
                by = self.bird.y
                self._sliding_this_frame = True
                self._maybe_skateboard_dust(self.bird.x, GROUND_Y)
                self._maybe_grind_sparks(GROUND_Y)
            else:
                self._die()
                return
        if self.ghost_timer > 0:
            return  # phase through pipes while ghost is active
        if self.bird.cart_locked:
            # Rail has taken over — re-snap Pip onto the rail every
            # frame (interpolated y between consecutive rail pipes,
            # slope written to bird.cart_tilt_deg). Phase through
            # tagged pillars; the rail bridges them.
            self._snap_cart_to_rail(self.bird.x)
            return
        # SKATEBOARD: full pipe-collision intercept. Bottom-pillar top
        # hits become rolls, upper-pillar underside hits become helmet
        # "CLONK!" deflects (the cyan-lamp / skull-bunny helmet design's
        # whole point — the punk helmet ABSORBS the bonk so Pip doesn't
        # die). Side hits are still lethal.
        if skating:
            for p in self.pipes:
                # Phantoms have no rim / crown to skate or bonk against.
                if p.is_phantom:
                    continue
                if self._skateboard_handle_pipe(p, bx, by, br):
                    by = self.bird.y
                    break
        # Pip's hitboxes: body (existing) + parcel below him. The parcel
        # offset rotates with his tilt so when he dives the parcel swings
        # forward/down with him.
        if self.grow_timer > 0:
            scale = GROW_SCALE
        elif self.shrink_timer > 0:
            scale = SHRINK_SCALE
        else:
            scale = 1.0
        parcel_offset = pygame.math.Vector2(
            0, PARCEL_Y_OFFSET * scale).rotate(-self.bird.tilt_deg)
        px = bx + parcel_offset.x
        py = by + parcel_offset.y
        pr = PARCEL_R * scale
        # While skating the parcel IS the board under Pip's feet, so its
        # collision footprint is gone — only Pip's body hitbox applies.
        if skating:
            pr = 0
        # RAIL: parked-cart hitbox. Only touching the cart itself (a
        # small rect sitting in the gap of rail_cart_pipe) locks Pip
        # onto the rail. Hitting the pillar BODY of that same pipe —
        # or any other tagged pillar — is fatal like any other pillar.
        cart_pipe = getattr(self, "rail_cart_pipe", None)
        if (self.bird.cart_active
                and not self.bird.cart_locked
                and cart_pipe is not None):
            if (self._circle_hits_cart(cart_pipe, bx, by, br)
                    or self._circle_hits_cart(cart_pipe, px, py, pr)):
                self._lock_pip_on_cart()
                return
        # Parcel shouldn't graze the ground unless the bird already would
        # have died (the bird circle's r > parcel offset+r in normal flight).
        # Skip ground/ceiling re-check; only pipes are added.
        for p in self.pipes:
            if p.collides_circle(bx, by, br - PIPE_HITBOX_SHRINK):
                self._die()
                return
            if pr > 0 and p.collides_circle(px, py, pr - 1):
                self._die()
                return

    def _skateboard_handle_pipe(self, p, bx, by, br) -> bool:
        """When SKATEBOARD is active, intercept lethal pipe collisions.

        Returns True if the collision was absorbed (no death):
          - Bottom-pillar TOP hit: land and roll along the rim.
          - Upper-pillar UNDERSIDE hit: helmet CLONK! deflect with
            stars + audio + shake. The cyan-lamp / skull-bunny helmet
            absorbs the bonk so Pip bounces gently instead of dying.
        Returns False for side hits, which are still lethal.
        """
        gap_top = p.gap_y - p.gap_h / 2
        gap_bot = p.gap_y + p.gap_h / 2
        in_column = (p.x - br < bx < p.x + PIPE_W + br)
        if (in_column and by < gap_bot and self.bird.vy >= -50
                and (by + br) >= gap_bot):
            self.bird.y = gap_bot - br
            self.bird.vy = 0.0
            self._maybe_skateboard_dust(bx, gap_bot)
            self._maybe_grind_sparks(gap_bot)
            self._sliding_this_frame = True
            return True
        if (in_column and by > gap_top and self.bird.vy <= 50
                and (by - br) <= gap_top):
            self.bird.y = gap_top + br
            self.bird.vy = max(self.bird.vy, 0.0) + 25
            self.shake_mag = max(self.shake_mag, 5.0)
            self.shake_t = max(self.shake_t, 0.18)
            audio.play_helmet_bonk()
            for _ in range(10):
                ang = random.uniform(-math.pi, 0)
                spd = random.uniform(120, 220)
                self.particles.append(Particle(
                    bx, gap_top,
                    math.cos(ang) * spd, math.sin(ang) * spd,
                    random.uniform(0.3, 0.6),
                    random.randint(2, 4),
                    random.choice((UI_GOLD, UI_CREAM, WHITE)),
                    gravity=400,
                ))
            return True
        return False

    def _maybe_skateboard_dust(self, x, y_ground):
        """Occasional dust puff while sliding — throttled, not every frame."""
        if random.random() < 0.35:
            for _ in range(2):
                ang = random.uniform(math.pi * 0.9, math.pi * 1.1)
                spd = random.uniform(40, 110)
                self.particles.append(Particle(
                    x - random.uniform(0, 10),
                    y_ground - 2,
                    math.cos(ang) * spd,
                    -abs(math.sin(ang) * spd * 0.4),
                    random.uniform(0.25, 0.45),
                    random.randint(2, 3),
                    random.choice(((220, 215, 200), (200, 195, 180), WHITE)),
                    gravity=200,
                ))

    def _maybe_grind_sparks(self, y_ground):
        """Bright spark spray at the grinding wheel — front wheel for
        a nose grind, back wheel for a tail grind. Sprays backward
        with an upward kick, fast settle. Brighter + denser than the
        slide-dust so grinds read as metal-on-concrete."""
        if self.bird.grind_type is None:
            return
        if self.bird.grind_type == "nose":
            wheel_dx = +14
        else:
            wheel_dx = -14
        wx = self.bird.x + wheel_dx
        if random.random() < 0.85:
            for _ in range(random.randint(3, 5)):
                ang = random.uniform(math.pi * 0.7, math.pi * 1.3)
                spd = random.uniform(100, 230)
                colour = random.choice((PARTICLE_ORNG,
                                        PARTICLE_GOLD,
                                        PARTICLE_WHT,
                                        (255, 220, 130)))
                self.particles.append(Particle(
                    wx + random.uniform(-2, 2),
                    y_ground - 2,
                    math.cos(ang) * spd,
                    math.sin(ang) * spd - random.uniform(20, 60),
                    random.uniform(0.18, 0.38),
                    random.randint(1, 3),
                    colour,
                    gravity=500,
                ))

    def _die(self):
        if self.game_over:
            return
        # KNIGHT revive: if the survive-one-hit buff is active, consume it
        # instead of dying and revive Pip with a grace window. Knight is
        # the only escape from poison — clear that state too.
        if self.bird.knight_active:
            self.knight_timer = 0.0
            self.bird.knight_active = False
            self.bird.poison_active = False
            self.bird.poison_t = 0.0
            self._revive_knight()
            return
        # LIVES revive: spend a heart instead of ending the run.
        if self.lives_remaining > 0:
            self._revive_life()
            return
        # Wall of Shame: snapshot the death-moment context while effect state is
        # still live (read post-death by achievements.evaluate_run). Only a real
        # death reaches here — a knight revive returned above.
        self.death_pillar = self.pillars_passed
        self.death_ghost = bool(self.bird.ghost_active)
        self.death_kfc = bool(self.bird.kfc_active)
        self.died_early_phase = (self.cycles_completed >= 1
                                 and (self.biome_time % biome.CYCLE_SECONDS) < 5.0)
        self.death_slowmo = self.slowmo_timer > 0
        self.death_poison = bool(self.bird.poison_active)
        self.death_skateboard = bool(self.bird.skateboard_active)
        self.death_lightning = self._lightning_scorch_t > 0
        self.death_celebration = bool(self.treasure_banners
                                      or self.celebration_garlands)
        self.death_magnet_zero = ((self.magnet_timer > 0 or self.megamagnet_timer > 0)
                                  and self._coins_in_magnet == 0)
        self.death_wish_pending = (self.powerups_picked.get("genie", 0) > 0
                                   and not self._genie_wish_taken)
        self._finalize_rush()      # close an in-progress rush for Coin Blind
        self.game_over = True
        self.bird.alive = False
        # Start the dead-Pip cross-fade. Tiny non-zero value gates the
        # overlay in Bird.draw; world.update advances it each frame.
        self.bird.death_fade_t = 1e-6
        self.hit_flash = 0.35
        self.shake_mag = 8
        self.shake_t = 0.45
        audio.play_death()
        for _ in range(26):
            self.particles.append(Particle(
                self.bird.x, self.bird.y,
                random.uniform(-260, 260), random.uniform(-360, -40),
                random.uniform(0.5, 1.2), random.randint(3, 6),
                random.choice((PARTICLE_CRIM, PARTICLE_ORNG, PARTICLE_WHT)),
                gravity=900,
            ))

    def _revive_life(self):
        """Spend one heart: grant collision immunity, kick upward, fire a
        modest burst so the player reads it as a recoverable hit, not death."""
        self.lives_remaining -= 1
        self.lives_used      += 1
        self.lives_invuln     = LIVES_INVULN_DUR
        if self.lives_remaining == 0:
            self.bird.on_last_life = True
            self.bird.on_first_hit = False
        elif self.lives_remaining == 1:
            self.bird.on_first_hit = True
        self.bird.vy          = FLAP_V * 0.7
        self.hit_flash        = 0.20
        self.shake_mag        = max(self.shake_mag, 4.0)
        self.shake_t          = max(self.shake_t,   0.25)
        audio.play_life_lost()
        for _ in range(12):
            ang = random.uniform(0, math.tau)
            spd = random.uniform(80, 200)
            self.particles.append(Particle(
                self.bird.x, self.bird.y,
                math.cos(ang) * spd, math.sin(ang) * spd,
                random.uniform(0.35, 0.8), random.randint(2, 4),
                random.choice(((255, 160, 30), (255, 220, 60), (255, 255, 200))),
                gravity=500,
            ))
        self.float_texts.append(FloatText(
            "♥ -1 LIFE", self.bird.x, self.bird.y - 40, (220, 60, 80),
            size=26, life=1.2, vy=-60, style="powerup",
        ))

    # ── pickups ──────────────────────────────────────────────────────────────

    def _check_pickups(self):
        bx, by = self.bird.x, self.bird.y
        br = BIRD_R + 4
        for c in self.coins:
            if c.collected:
                continue
            dx = c.x - bx
            dy = c.y - by
            if dx * dx + dy * dy < (br + COIN_R) ** 2:
                c.collected = True
                self._on_coin(c)
        for m in self.powerups:
            if m.collected:
                continue
            if m.kind == "treasure":
                # The chest sprite is drawn at full PICKUP_W × PICKUP_H
                # (~100 × 82 px) — much larger than a regular power-up
                # circle. Use a circle-vs-rect test so any visible
                # touch on the chest triggers pickup, instead of only
                # the small ~34 px centre.
                from game.treasure_box import PICKUP_W, PICKUP_H
                half_w = PICKUP_W * 0.5
                half_h = PICKUP_H * 0.5
                closest_x = max(m.x - half_w, min(bx, m.x + half_w))
                closest_y = max(m.y - half_h, min(by, m.y + half_h))
                ddx = bx - closest_x
                ddy = by - closest_y
                if ddx * ddx + ddy * ddy < br * br:
                    m.collected = True
                    self._on_powerup(m)
                continue
            dx = m.x - bx
            dy = m.y - by
            if dx * dx + dy * dy < (br + POWERUP_R) ** 2:
                m.collected = True
                self._on_powerup(m)

    def _apply_magnet(self, dt):
        """Tug uncollected coins toward the bird. Pull radius is
        MEGAMAGNET_RADIUS when the megamagnet timer is active,
        otherwise MAGNET_RADIUS. Pull strength is the same."""
        radius = MEGAMAGNET_RADIUS if self.megamagnet_timer > 0 else MAGNET_RADIUS
        r2 = radius * radius
        bx, by = self.bird.x, self.bird.y
        for c in self.coins:
            if c.collected:
                continue
            dx = bx - c.x
            dy = by - c.y
            d2 = dx * dx + dy * dy
            if d2 > r2 or d2 < 1.0:
                continue
            d = math.sqrt(d2)
            pull = 520 * (1.0 - d / radius)
            c.x += (dx / d) * pull * dt
            c.y += (dy / d) * pull * dt

    def _on_coin(self, coin: Coin):
        value = 3 if self.triple_timer > 0 else 1
        self.score += value
        self.coin_count += 1
        self._proof.record(self.time_alive, value, "coin")
        if self.magnet_timer > 0 or self.megamagnet_timer > 0:
            self._coins_in_magnet += 1
        if getattr(coin, "is_rush", False):
            self._rush_cur_got += 1

        # *** GLITCH FIX ***
        # NO screen-wide flash. Only localized sparkle particles.
        for _ in range(10):
            ang = random.uniform(0, math.tau)
            spd = random.uniform(80, 220)
            col = random.choice((PARTICLE_GOLD, COIN_LIGHT, PARTICLE_WHT))
            self.particles.append(Particle(
                coin.x, coin.y,
                math.cos(ang) * spd, math.sin(ang) * spd,
                random.uniform(0.4, 0.8),
                random.randint(2, 4),
                col, gravity=300,
            ))
        if value == 3:
            label = "+3"
            color = UI_ORANGE
            size = 32
            text_y_offset = 18
        else:
            label = "+1"
            color = UI_GOLD
            size = 24
            text_y_offset = 8
        # style="powerup" gives the +N a bold dark outline + vertical
        # gradient + sparkle dots, matching the look of the power-up
        # activation float-texts. Gradient/outline are auto-derived from
        # `color`, so +1 reads gold and +3 reads orange.
        self.float_texts.append(
            FloatText(label, coin.x, coin.y - text_y_offset, color,
                      size=size, life=0.9, style="powerup"))

        if value == 3:
            audio.play_coin_triple()
        else:
            audio.play_coin()

    def _on_powerup(self, m: PowerUp):
        # Genie offer: collecting any one of the spawned offers cancels the
        # others (with a poof). Done before activation so the chosen kind's
        # activator still runs normally below.
        if getattr(m, "is_genie_offer", False):
            self._cull_genie_offers_except(m)
            self._genie_wish_taken = True
        # POISON HEAL: grabbing ANY power-up other than another poison
        # cures Pip mid-dive. Clear the poison state before the kind's
        # activator runs so a knight pickup doesn't trigger its
        # poison-revive path (no revive needed — Pip's already healed).
        if self.bird.poison_active and m.kind != "poison":
            self.bird.poison_active = False
            self.bird.poison_t = 0.0
            self.float_texts.append(FloatText(
                "CURED!", m.x, m.y - 26, (160, 230, 200),
                size=24, life=1.1, vy=-30, style="powerup",
            ))
        # Surprise box: roll a random "real" kind at pickup time, then route
        # through that kind's activator. The resolved activator plays the
        # matching sound — there's no dedicated surprise SFX.
        kind = m.kind
        if kind == "surprise":
            self.powerups_picked["surprise"] = self.powerups_picked.get("surprise", 0) + 1
            # "reverse" is intentionally excluded — feels too disorienting
            # in stacks. The activation code is still wired up; add it back
            # to this tuple (and to POWERUP_WEIGHTS in config.py) to enable.
            # `grow` is excluded too — it's a late-game-gated pickup
            # (POWERUP_SCORE_GATES["grow"] == 250). Letting a Surprise
            # Box resolve to grow would bypass the gate.
            # Surprise honours the magnet -> megamagnet swap rule: once
            # the run hits POWERUP_REPLACED_AT["magnet"], surprise rolls
            # megamagnet instead of magnet so the box doesn't sneak the
            # downgrade past the threshold.
            magnet_kind = ("megamagnet"
                           if self.score >= POWERUP_REPLACED_AT.get("magnet", 1 << 30)
                           else "magnet")
            choices = ["triple", magnet_kind, "slowmo", "kfc", "ghost", "shrink"]
            # Once a genie milestone has fired (production or debug), the
            # Surprise Box also rolls the genie — the trap-bearing tier no
            # longer needs its own standalone pickup to surface. (Knight /
            # poison / skateboard stay genie-only.)
            if self._genie_milestone_fired or self._debug_genie_milestone_fired:
                choices.append("genie")
            kind = random.choice(choices)
            if kind in self._surprise_rolls:
                self.surprise_repeat = 1
            self._surprise_rolls.add(kind)
            self._spawn_surprise_reveal(m)
        # Treasure isn't a power-up, it's a once-per-day reward. Skip the
        # pickup-counter increment so it doesn't surface in the run-summary
        # power-ups strip alongside Magnet / Triple / etc. The dict key is
        # kept at 0 in __init__ so existing analytics queries still find
        # the column.
        if kind != "treasure":
            self.powerups_picked[kind] = self.powerups_picked.get(kind, 0) + 1
        if kind == "triple":
            self._activate_triple(m)
        elif kind == "magnet":
            self._activate_magnet(m)
        elif kind == "megamagnet":
            self._activate_megamagnet(m)
        elif kind == "slowmo":
            self._activate_slowmo(m)
        elif kind == "kfc":
            self._activate_kfc(m)
        elif kind == "ghost":
            self._activate_ghost(m)
        elif kind == "grow":
            self._activate_grow(m)
        elif kind == "reverse":
            self._activate_reverse(m)
        elif kind == "shrink":
            self._activate_shrink(m)
        elif kind == "rail":
            self._activate_rail(m)
        elif kind == "lottery":
            self._activate_lottery(m)
        elif kind == "skateboard":
            self._activate_skateboard(m)
        elif kind == "knight":
            self._activate_knight(m)
        elif kind == "genie":
            self._activate_genie(m)
        elif kind == "poison":
            self._activate_poison(m)
        elif kind == "umbrella":
            self._activate_umbrella(m)
        elif kind == "treasure":
            self._activate_treasure_box(m)

        # Sample the peak stack of simultaneously-active timed buffs (Overloaded)
        # right after this pickup's activator sets its timer.
        self.max_active_powerups = max(self.max_active_powerups,
                                       self._count_active_powerups())

    def _count_active_powerups(self) -> int:
        """Number of timed power-up buffs currently running (for the Overloaded
        stack tally). Counts the standard effect timers only."""
        timers = (self.triple_timer, self.magnet_timer, self.megamagnet_timer,
                  self.slowmo_timer, self.kfc_timer, self.ghost_timer,
                  self.grow_timer, self.reverse_timer, self.shrink_timer,
                  self.skateboard_timer, self.knight_timer, self.umbrella_timer)
        return sum(1 for t in timers if t > 0)

    def _spawn_surprise_reveal(self, m):
        """Brief gold-burst + cloud puff so the player sees the box "open"
        before the resolved power-up's own activator fires."""
        for _ in range(18):
            ang = random.uniform(0, math.tau)
            spd = random.uniform(140, 280)
            col = random.choice((UI_GOLD, UI_ORANGE, UI_CREAM, WHITE))
            self.particles.append(Particle(
                m.x, m.y,
                math.cos(ang) * spd, math.sin(ang) * spd,
                random.uniform(0.4, 0.8),
                random.randint(2, 4),
                col, gravity=160,
            ))

    def _pickup_burst(self, m, colors, n=30, speed_hi=320, grav=150):
        for _ in range(n):
            ang = random.uniform(0, math.tau)
            spd = random.uniform(100, speed_hi)
            col = random.choice(colors)
            self.particles.append(Particle(
                m.x, m.y,
                math.cos(ang) * spd, math.sin(ang) * spd,
                random.uniform(0.5, 1.0),
                random.randint(3, 6),
                col, gravity=grav,
            ))

    def _activate_triple(self, m):
        self.triple_timer = TRIPLE_DURATION
        self.shake_mag = max(self.shake_mag, 3.0)
        self.shake_t = max(self.shake_t, 0.25)
        audio.play_triple_coin()
        audio.play_poof()
        self._spawn_poof(self.bird.x, self.bird.y)
        self._pickup_burst(m, (UI_ORANGE, UI_GOLD, BIRD_RED, UI_CREAM))
        self.float_texts.append(FloatText(
            "3X POWER!", m.x, m.y - 26, UI_ORANGE,
            size=30, life=1.4, vy=-30, style="powerup",
        ))

    def _activate_magnet(self, m):
        self.magnet_timer = MAGNET_DURATION
        self.shake_mag = max(self.shake_mag, 2.5)
        self.shake_t = max(self.shake_t, 0.25)
        audio.play_magnet()
        self._pickup_burst(m, (BIRD_RED, (220, 30, 40), UI_CREAM, WHITE))
        self.float_texts.append(FloatText(
            "MAGNET!", m.x, m.y - 26, BIRD_RED,
            size=28, life=1.3, vy=-30, style="powerup",
        ))

    def _activate_megamagnet(self, m):
        self.megamagnet_timer = MEGAMAGNET_DURATION
        self.shake_mag = max(self.shake_mag, 3.5)
        self.shake_t = max(self.shake_t, 0.3)
        audio.play_megamagnet()
        self._pickup_burst(m, (BIRD_RED, (220, 30, 40), UI_CREAM, WHITE),
                           n=42, speed_hi=380)
        self.float_texts.append(FloatText(
            "MEGAMAGNET!", m.x, m.y - 26, BIRD_RED,
            size=32, life=1.4, vy=-32, style="powerup",
        ))

    def _activate_slowmo(self, m):
        self._slowmo_run_pillars = 0     # fresh window for the Bullet Time tally
        self.slowmo_timer = SLOWMO_DURATION
        self.shake_mag = max(self.shake_mag, 2.5)
        self.shake_t = max(self.shake_t, 0.25)
        audio.play_slowmo()
        self._pickup_burst(m, ((180, 100, 255), (120, 60, 200), WHITE, UI_CREAM))
        self.float_texts.append(FloatText(
            "SLOW-MO!", m.x, m.y - 26, (200, 140, 255),
            size=28, life=1.3, vy=-30, style="powerup",
        ))

    def _activate_kfc(self, m):
        self.kfc_timer = KFC_DURATION
        self.bird.kfc_active = True
        # Pick a fries-mountain variant at random for this activation
        # and pre-render it to a Surface. game.fries_mountains has 3
        # variants (classic / boxes / curly); the chosen index +
        # cached Surface are read by PlayScene._draw_background for as
        # long as kfc_timer > 0.
        from game.fries_mountains import (
            KFC_MOUNTAIN_DRAWERS, get_cached_mountain,
        )
        self.kfc_mountain_variant = random.randint(
            0, len(KFC_MOUNTAIN_DRAWERS) - 1)
        # Module-level cache built once per variant — App.__init__ prewarms
        # all variants under the splash, so this is a guaranteed cache hit
        # at pickup time (no frame spike).
        self.kfc_mountain_layers = get_cached_mountain(
            self.kfc_mountain_variant, GROUND_Y, W)
        # Snapshot scroll at pickup so PlayScene can derive the parallax
        # offset (bg_scroll - kfc_activation_scroll) for each layer.
        self.kfc_activation_scroll = self.bg_scroll
        # Retroactively flip every pipe currently on screen so the entire
        # visible scene becomes fast-food at the moment of pickup, AND
        # widen its collision gap. The KFC *visual* is gated on
        # kfc_timer > 0 (see Pipe.draw), so when the timer expires every
        # pillar snaps back to stone alongside the fries mountain + Pip.
        # The wider gap is sticky on the pipe instance, though: it stays
        # for the rest of that pipe's life so the player isn't punished
        # by a mid-flight gap shrink.
        #
        # `is_kfc` is the sticky gap-widened flag and gates the
        # double-boost guard below — a second KFC pickup (or a pipe born
        # during the active window) must not compound 1.30 again.
        for p in self.pipes:
            if not p.is_kfc:
                p.gap_h = int(p.gap_h * KFC_GAP_BOOST)
                p.is_kfc = True
        self.shake_mag = max(self.shake_mag, 5.0)
        self.shake_t   = max(self.shake_t,   0.4)
        audio.play_poof()
        self._spawn_poof(self.bird.x, self.bird.y)
        self._pickup_burst(m, ((210, 138, 42), (238, 178, 72), (148, 82, 18), WHITE), n=28)
        self.float_texts.append(FloatText(
            "DEEP FRIED!", m.x, m.y - 26, (230, 160, 40),
            size=28, life=1.6, vy=-28, style="powerup",
        ))

    def _activate_ghost(self, m):
        GHOST_BLUE  = (140, 180, 255)
        GHOST_WHITE = (210, 225, 255)
        self._ghost_run_pillars = 0      # fresh window for the Ghost Rider tally
        self.ghost_timer = GHOST_DURATION
        self.ghost_timer_total = GHOST_DURATION
        self.bird.ghost_active = True
        self.shake_mag = max(self.shake_mag, 2.0)
        self.shake_t   = max(self.shake_t,   0.2)
        audio.play_ghost()
        audio.play_poof()
        self._spawn_poof(self.bird.x, self.bird.y)
        self._pickup_burst(m, (GHOST_BLUE, GHOST_WHITE, (180, 200, 255)),
                           n=28, speed_hi=260, grav=120)
        # Wisp orbit particles at bird position
        for i in range(10):
            ang = i / 10 * math.tau
            spd = random.uniform(40, 90)
            self.particles.append(Particle(
                self.bird.x + math.cos(ang) * 20,
                self.bird.y + math.sin(ang) * 20,
                math.cos(ang) * spd, math.sin(ang) * spd - 30,
                random.uniform(0.4, 0.8),
                random.randint(2, 4),
                random.choice((GHOST_BLUE, GHOST_WHITE)),
                gravity=60,
            ))
        self.float_texts.append(FloatText(
            "GHOST!", m.x, m.y - 26, (180, 210, 255),
            size=28, life=1.3, vy=-30, style="powerup",
        ))

    def _activate_grow(self, m):
        GROW_HI  = (50, 220, 100)
        GROW_OUT = (28, 160,  70)
        self.grow_timer = GROW_DURATION
        self.bird.grow_active = True
        self.shake_mag = max(self.shake_mag, 4.0)
        self.shake_t   = max(self.shake_t,   0.3)
        audio.play_grow()
        audio.play_poof()
        self._spawn_poof(self.bird.x, self.bird.y)
        self._pickup_burst(m, (GROW_HI, GROW_OUT, WHITE, UI_CREAM), n=30, speed_hi=300)
        self.float_texts.append(FloatText(
            "GROW!", m.x, m.y - 26, GROW_HI,
            size=30, life=1.3, vy=-30, style="powerup",
        ))

    def _activate_treasure_box(self, m):
        """Cycle-finale reward — the rarest moment in the game, calibrated
        over-the-top: +TREASURE_BOX_GRANT * day score, 90 first-wave
        flying coins in 3 velocity buckets, 40 more 0.30 s later as a
        settling tail, a "DAY N COMPLETE!" banner that drops above the
        chest, a world-space festoon garland strung between the two
        flanking pillars, 16 confetti flakes, the biggest sparkle aura in
        the game, +grant float, screen shake, three-layer audio fanfare.

        Grant scales linearly with the day count: day 1 -> 100, day 2 ->
        200, day N -> 100 * N. Survives-through-the-day reward, scoped
        to in-run progression — cycles_completed resets to 0 on a fresh
        run so each playthrough starts the scaling chain over."""
        day = max(1, self.cycles_completed)
        grant = TREASURE_BOX_GRANT * day
        self.score += grant
        # 'treasure' is its own proof-ledger kind — plausibility only
        # special-cases 'coin' and 'pipe' for dscore bounds, so the
        # variable scaling jump is accepted without changing any
        # per-event bound. The MAX_PLAUSIBLE_SCORE = 100_000 ceiling
        # still bounds the total run score.
        self._proof.record(self.time_alive, grant, "treasure")
        self._finale_box_dropped = True

        # Open-lid sprite + halo fade-out timer; ALSO gates the powerup
        # cull so the chest stays drawn past the moment of collection.
        m.claimed_anim_t = TREASURE_BOX_ANIM_T

        # Screen shake — ~1.5× the megamagnet pickup, the loudest existing
        # power-up pickup.
        self.shake_mag = max(self.shake_mag, 7.0)
        self.shake_t   = max(self.shake_t,   0.55)

        # ── Coin storm — first wave, 3 velocity buckets ─────────────────
        # 40 "rocket" coins: high arc, longest life. 30 "medium" mid arc.
        # 20 "soft" low arc. The staggered peaks mean the screen doesn't
        # see ALL coins crest at the same frame — the spectacle sustains.
        # Cone widened almost to a full upward 180° so the fan reads as
        # an eruption, not a tight jet.
        for _ in range(40):                       # rocket
            ang = random.uniform(-math.pi + 0.05, -0.05)
            spd = random.uniform(380, 560)
            self.particles.append(FlyingCoinParticle(
                m.x, m.y,
                math.cos(ang) * spd, math.sin(ang) * spd,
                life=random.uniform(4.5, 6.0),
            ))
        for _ in range(30):                       # medium
            ang = random.uniform(-math.pi + 0.05, -0.05)
            spd = random.uniform(240, 360)
            self.particles.append(FlyingCoinParticle(
                m.x, m.y,
                math.cos(ang) * spd, math.sin(ang) * spd,
                life=random.uniform(3.5, 4.75),
            ))
        for _ in range(20):                       # soft
            ang = random.uniform(-math.pi + 0.05, -0.05)
            spd = random.uniform(120, 220)
            self.particles.append(FlyingCoinParticle(
                m.x, m.y,
                math.cos(ang) * spd, math.sin(ang) * spd,
                life=random.uniform(2.5, 3.5),
            ))

        # Sparkle aura — 60 additive particles, the biggest burst in the
        # game (vs. megamagnet's 42).
        for _ in range(60):
            ang = random.uniform(0, math.tau)
            spd = random.uniform(100, 420)
            col = random.choice((
                UI_GOLD, UI_ORANGE, UI_CREAM, WHITE, PARTICLE_GOLD,
            ))
            self.particles.append(Particle(
                m.x, m.y,
                math.cos(ang) * spd, math.sin(ang) * spd,
                random.uniform(0.6, 1.2),
                random.randint(3, 6),
                col, gravity=100,
            ))

        # ── Firework bursts — 7 staggered explosions across 1.4 s ──────
        # Sit in the air above + around the banner so the celebration
        # has visible aerial fireworks (V3 motif). Drawn additively so
        # the flash punches through the twilight sky. Each burst rides
        # the world scroll via x decrement applied at draw time — they
        # spawn as world-space FX particles + tick with self.particles.
        from game.entities import CelebrationFireworkBurst
        # Burst positions: 3 around the top-centre banner area + 2 at
        # mid-height bracketing the chest + 2 finale bursts behind the
        # chest. Stagger ignite delays so the bursts pop in sequence,
        # not all at once.
        # Restaggered across the new ~2.5 s "active hold" window so
        # bursts keep popping during the banner hold instead of all
        # clumping at the start.
        burst_specs = [
            (W * 0.30,  80.0,  0.05),    # upper-left, snap-ignite
            (W * 0.70,  90.0,  0.35),    # upper-right
            (W * 0.50,  60.0,  0.70),    # top-centre behind banner
            (W * 0.20, 180.0,  1.15),    # mid-left
            (W * 0.80, 170.0,  1.55),    # mid-right
            (W * 0.40, 220.0,  2.00),    # finale-1, around the chest
            (W * 0.60, 200.0,  2.50),    # finale-2
        ]
        palette = CelebrationFireworkBurst.PALETTE
        for i, (fx, fy, delay) in enumerate(burst_specs):
            colour = palette[i % len(palette)]
            radius_mul = 1.2 if i == 2 else 1.0
            self.particles.append(CelebrationFireworkBurst(
                fx, fy, ignite_delay=delay,
                color=colour, radius_mul=radius_mul,
            ))

        # ── Confetti dusting — 16 rotating flakes ───────────────────────
        # World-space (rides scroll via vx). Spread across the upper
        # half of the scene around / above / beside the banner; an
        # exclusion ellipse keeps them off the chest pile.
        from game.entities import CelebrationConfetti
        scroll_vx = -self._current_scroll()
        for _ in range(16):
            # Spawn around the chest with a sky-biased offset so flakes
            # arc through the banner reveal area instead of dropping
            # into the chest interior.
            ox = random.uniform(-140, 140)
            oy = random.uniform(-80, -30)
            ang = random.uniform(-math.pi * 0.85, -math.pi * 0.15)
            spd = random.uniform(140, 280)
            vx = math.cos(ang) * spd + scroll_vx
            vy = math.sin(ang) * spd
            self.particles.append(CelebrationConfetti(
                m.x + ox, m.y + oy, vx, vy,
                random.choice(CelebrationConfetti.COLOURS),
                life=random.uniform(3.5, 5.0),
                spin=random.uniform(-6.0, 6.0),
            ))

        # ── DAY N COMPLETE! banner ──────────────────────────────────────
        # Drops in screen-space above the chest. cycles_completed was
        # incremented at the cycle rollover earlier in this finale.
        from game.entities import TreasureBanner, CelebrationGarland
        self.treasure_banners.append(TreasureBanner(
            day_num=max(1, self.cycles_completed),
            x=m.x,
            y_chest=m.y,
        ))

        # ── Festoon garland across flanking pillars ─────────────────────
        # World-space: tracks the two pipes flanking the chest's x by
        # ref so the catenary follows them as they scroll. If somehow
        # one side is missing (e.g. an edge case at the very first
        # cycle), the garland silently skips — the banner + coins
        # carry the moment alone.
        left, right = self._flanking_pillars(m.x)
        if left is not None and right is not None:
            self.celebration_garlands.append(
                CelebrationGarland(left, right))
            # Bunting + balloons have already been appended at the first
            # post-finale real-pillar spawn in _spawn_pipe — no double-
            # spawn here.

        self.float_texts.append(FloatText(
            f"+{grant}!", m.x, m.y - 30, UI_GOLD,
            size=44, life=5.0, vy=-30, style="powerup",
        ))

        # Schedule the second wave: 40 more coins fired from the chest
        # position 0.30 s later, downward-biased (the "settling debris"
        # tail). Snapshot position now so the wave fires from where the
        # chest WAS even if its sprite has scrolled left a touch by
        # then. Wave coins ride the world scroll the same way.
        self._treasure_second_wave_t = 0.80
        self._treasure_second_wave_pos = (m.x, m.y)

        audio.play_treasure_pickup()

    def _flanking_pillars(self, x: float):
        """Return (left, right) pipes — the closest pipe whose centre is
        left of x and the closest whose centre is right of x. Either
        may be None if x sits beyond the spawned-pipe range. Phantoms
        skipped so the cycle-finale festoon hangs from the REAL pillars
        bordering the open 5-pillar gap, not from two invisible phantoms
        mid-span."""
        left = None
        right = None
        for p in self.pipes:
            if p.is_phantom:
                continue
            cx = p.x + PIPE_W * 0.5
            if cx < x:
                if left is None or cx > left.x + PIPE_W * 0.5:
                    left = p
            elif cx > x:
                if right is None or cx < right.x + PIPE_W * 0.5:
                    right = p
        return left, right

    def _fire_treasure_second_wave(self):
        """Tail of 40 more flying coins from the chest's pickup position.
        Downward-biased so it reads as "settling coin debris" after the
        rocket peak — keeps the eye occupied through the chest's
        claimed_anim_t fade-out."""
        sx, sy = self._treasure_second_wave_pos
        scroll_vx = -self._current_scroll()
        for _ in range(40):
            # Wide downward fan — angles in -0.3..pi+0.3 cover sideways
            # + down. Gravity (baked into FlyingCoinParticle physics)
            # carries them naturally to the ground.
            ang = random.uniform(-0.3, math.pi + 0.3)
            spd = random.uniform(120, 280)
            self.particles.append(FlyingCoinParticle(
                sx, sy,
                math.cos(ang) * spd + scroll_vx, math.sin(ang) * spd,
                life=random.uniform(3.0, 4.5),
            ))

    def _spawn_poof(self, x, y):
        """Burst of expanding cloud puffs — used on KFC transformation start and end."""
        puff_colors = [
            (255, 255, 255), (240, 240, 240),
            (225, 225, 225), (210, 215, 220),
        ]
        for _ in range(14):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(50, 130)
            vx    = math.cos(angle) * speed
            vy    = math.sin(angle) * speed - random.uniform(10, 40)
            life  = random.uniform(0.32, 0.52)
            r0    = random.randint(4, 9)
            r1    = random.randint(13, 22)
            color = random.choice(puff_colors)
            self.particles.append(CloudPuff(x, y, vx, vy, life, r0, r1, color))

    # ── Secret late-game power-ups ───────────────────────────────────────────

    def _spawn_grainy_poof(self, x, y, palette=None, n=None, rx=34, ry=34,
                           scroll_vx=0.0):
        """Magic-dust poof — a puffy CLOUD that covers its source, built from
        a few overlapping soft lobes densely packed with motes so it reads as
        a cohesive, lumpy cloud. (rx, ry) set the area covered. Used for every
        genie beat: the genie / offers appearing and vanishing.

        scroll_vx is added to every grain's vx so the cloud drifts along with
        the world. Callers anchored to a scrolling pipe (the chamber reveal)
        pass -current_scroll so the poof stays attached to the pillar; the
        default 0 keeps bird-anchored poofs in screen space as before."""
        if palette is None:
            palette = [(255, 180, 190), (255, 225, 170), (255, 250, 180),
                       (190, 240, 200), (180, 225, 255), (215, 190, 255),
                       (255, 255, 255)]
        if n is None:
            n = max(140, int(rx * ry * 0.28))
        base = min(rx, ry)
        lobes = [(0.0, 0.0, 0.90 * base)]
        for _ in range(random.randint(5, 7)):
            la = random.uniform(0, math.tau)
            lr = random.uniform(0.0, 0.60)
            lobes.append((math.cos(la) * rx * lr,
                          math.sin(la) * ry * lr,
                          random.uniform(0.50, 0.80) * base))
        for _ in range(n):
            lox, loy, lrad = random.choice(lobes)
            a  = random.uniform(0, math.tau)
            rr = math.sqrt(random.random())          # fill the lobe disc
            px = x + lox + math.cos(a) * lrad * rr
            py = y + loy + math.sin(a) * lrad * rr
            vx = random.uniform(-14, 14) + scroll_vx
            vy = random.uniform(-20, 6)
            life = random.uniform(0.50, 1.00)
            size = random.choice((3, 3, 4, 4))
            self.particles.append(
                PoofGrain(px, py, vx, vy, life, size, random.choice(palette)))

    def _spawn_genie_reveal_poof(self, x, y):
        """Poof when a Genie offer materialises — the same magic dust as
        every other genie beat so appear and vanish read as one effect.
        The chamber pillar is scrolling leftward while the post-poof spawn
        delay plays out, so we ride the world scroll on the poof's grains
        — keeps the cloud parked on the pillar all the way to where the
        wish actually materialises (no spatial gap between poof and
        pickup)."""
        self._spawn_grainy_poof(x, y, scroll_vx=-self._current_scroll())

    def _activate_skateboard(self, m):
        from game.skateboard_fx import (
            render_caption_overlay, render_starburst_surface,
        )
        self.skateboard_timer = SKATEBOARD_DURATION
        self.bird.skateboard_active = True
        self.shake_mag = max(self.shake_mag, 4.0)
        self.shake_t = max(self.shake_t, 0.3)
        audio.play_skateboard()
        self._spawn_poof(self.bird.x, self.bird.y)
        self._pickup_burst(
            m, ((60, 60, 70), (180, 180, 190), UI_ORANGE, UI_GOLD), n=28)
        seed = int(self._idle_t * 1000) & 0xFFFF
        self.skateboard_caption_dur = SKATEBOARD_DURATION
        self.skateboard_caption_t = self.skateboard_caption_dur
        self.skateboard_caption_overlay = render_caption_overlay(
            int(self.bird.x), int(self.bird.y), rng_seed=seed,
        )
        # Activation starburst (the big pop-art star around Pip) was
        # removed by user request — only the caption banner + score
        # halftone swap remain as activation FX. Leave the burst state
        # fields in place but null the surface so the scenes.py guard
        # short-circuits.
        self.skateboard_burst_dur = 0.0
        self.skateboard_burst_t = 0.0
        self.skateboard_burst_surface = None
        self.skateboard_burst_cx = 0
        self.skateboard_burst_cy = 0

    def _activate_knight(self, m):
        KNIGHT_STEEL = (190, 200, 220)
        KNIGHT_GOLD  = (226, 182,  72)
        self.knight_timer = KNIGHT_DURATION
        self.bird.knight_active = True
        self.shake_mag = max(self.shake_mag, 3.5)
        self.shake_t   = max(self.shake_t,   0.3)
        audio.play_knight()
        self._spawn_poof(self.bird.x, self.bird.y)
        self._pickup_burst(m, (KNIGHT_STEEL, KNIGHT_GOLD, WHITE, UI_CREAM),
                           n=32, speed_hi=320)
        self.float_texts.append(FloatText(
            "+1 LIFE", m.x, m.y - 26, KNIGHT_GOLD,
            size=30, life=1.4, vy=-32, style="powerup",
        ))

    def _revive_knight(self):
        """Survive-one-hit revive: re-flap up, grant a grace window, and fire
        a steel-and-brass spark burst + GUARD! text."""
        self.knight_invuln = KNIGHT_INVULN
        self.bird.vy = FLAP_V * 0.9
        self.shake_mag = max(self.shake_mag, 6.0)
        self.shake_t   = max(self.shake_t,   0.3)
        audio.play_ghost()
        audio.play_thunder()
        for _ in range(36):
            ang = random.uniform(0, math.tau)
            spd = random.uniform(160, 420)
            col = random.choice((
                (210, 218, 236), (146, 156, 178),
                (226, 182,  72), WHITE,
            ))
            self.particles.append(Particle(
                self.bird.x, self.bird.y,
                math.cos(ang) * spd, math.sin(ang) * spd,
                random.uniform(0.5, 1.2),
                random.randint(3, 6),
                col, gravity=180,
            ))
        self.float_texts.append(FloatText(
            "GUARD!", self.bird.x, self.bird.y - 32, (226, 182, 72),
            size=30, life=1.4, vy=-36, style="powerup",
        ))

    def _activate_genie(self, m):
        """Genie Lamp — summons the conjurer for the wish-cast ceremony
        and arranges a GENIE CHAMBER pillar: a 2.0x-wider gap with
        KNIGHT / POISON / SKATEBOARD stacked vertically inside it in
        random order. To make the wishes arrive faster, we first try
        to convert the CURRENT rightmost pipe into the chamber (one
        pillar earlier than waiting for the next spawn). If no suitable
        existing pipe is far enough ahead of Pip, we fall back to
        flagging the next-spawned pipe."""
        gy = 175
        gx = 180
        # No floating offers — the GenieCharacter still spawns for the
        # visual cast beat but with an empty `offers` list, so
        # _fire_all becomes a poof + chime only. The actual offer
        # placement happens when the chamber pillar's reveal triggers.
        # gy lifted from 225 to 175 (50 px up) so the conjurer rises
        # into the cleared upper band — the SKATEBOARD deck banner
        # ends at y≈116 and the genie's head (gy - 96) lands at y≈79,
        # so it sits just below the HUD chrome instead of mid-screen.
        self.genie_actors.append(GenieCharacter(
            gx, gy, vx=0.0, offers=[], world=self,
        ))
        # Pick the chamber pillar — prefer "one pillar before" (the
        # current rightmost pipe), fall back to next-spawn.
        if not self._convert_rightmost_pipe_to_chamber():
            self.genie_chamber_pending = True
        self.shake_mag = max(self.shake_mag, 2.0)
        self.shake_t   = max(self.shake_t, 0.2)
        try:
            audio.play_genie()
        except Exception:
            pass
        self._pickup_burst(
            m, ((185, 130, 45), (250, 215, 130),
                (170, 130, 195), (220, 200, 240)),
            n=24, speed_hi=260,
        )
        self.float_texts.append(FloatText(
            "GENIE!", m.x, m.y - 26, (250, 215, 130),
            size=28, life=1.3, vy=-28, style="powerup",
        ))

    def _convert_rightmost_pipe_to_chamber(self) -> bool:
        """Retroactively turn the most recently spawned pipe into a
        genie chamber: widen gap to 2.0x, recentre to keep margins,
        clear in-gap content, mark for wish reveal on approach.

        Returns False if no eligible pipe exists (too close to Pip, or
        already tagged for a competing role) — caller falls back to
        the pending-next-spawn path."""
        if not self.pipes:
            return False
        target = self.pipes[-1]
        # Need enough lead distance so the player can read the chamber
        # and adjust altitude — must be at least one pipe-spacing ahead
        # of the pipe Pip is currently passing.
        if (target.x - self.bird.x) < 350:
            return False
        # Don't steal pipes already committed to another role.
        if (getattr(target, "is_rush", False)
                or getattr(target, "is_kfc", False)
                or getattr(target, "rail_active", False)
                or getattr(target, "is_genie_chamber", False)):
            return False
        margin = 70
        new_gap_h = int(GAP_START * GENIE_CHAMBER_GAP_BOOST)
        # Clamp the existing gap centre so the over-wide gap stays
        # inside the playfield (margin top + GROUND_Y - margin bottom).
        min_y = margin + new_gap_h // 2
        max_y = GROUND_Y - margin - new_gap_h // 2
        target.gap_y = max(min_y, min(max_y, target.gap_y))
        target.gap_h = new_gap_h
        target.is_genie_chamber = True
        target.wishes_spawned = False
        # Clear in-gap clutter so the chamber reads as a wish moment,
        # not a regular pillar with extra coins.
        band_xmin = target.x - 40
        band_xmax = target.x + PIPE_W + 40
        self.coins = [c for c in self.coins
                      if not (band_xmin <= c.x <= band_xmax)]
        self.powerups = [
            p for p in self.powerups
            if not (band_xmin <= p.x <= band_xmax)
            or getattr(p, "is_genie_offer", False)
        ]
        return True

    def _spawn_storm_umbrella(self):
        """Drop an umbrella offscreen-right at a comfortable mid-screen y
        so the player can navigate to it. Fired from the scoring path
        when `pillars_passed` enters UMBRELLA_SPAWN_PILLARS (currently
        p85 + p97 — both inside the dusk rain block). Anchored to the
        rightmost existing pipe like the milestone genie, but never
        closer than W+spacing/2 from the right edge so it always
        arrives by scrolling in. Independent of the regular powerup
        roll — does NOT consume POWERUP_COOLDOWN or get filtered by
        the weighted pool."""
        if not self.pipes:
            return
        spacing = self._current_spacing()
        anchor = self.pipes[-1]
        gx = max(anchor.x + PIPE_W + spacing * 0.5, W + spacing * 0.5)
        gy = max(140, min(H - 200, anchor.gap_y))
        self.powerups.append(PowerUp(gx, gy, kind="umbrella"))

    def _activate_umbrella(self, m):
        """Umbrella pickup. Cancels rain flap-dampening for the next
        UMBRELLA_DURATION seconds (see _apply_weather_effects) and lights
        Bird.umbrella_active so entities.py paints the upright canopy over
        the head. Spawn flow is independent of the regular pool — see
        _maybe_spawn_storm_umbrella below."""
        from game.config import UMBRELLA_DURATION
        self.umbrella_timer = UMBRELLA_DURATION
        self.bird.umbrella_active = True
        try:
            audio.play_slowmo()  # gentle pickup blip; shares the cool palette
        except Exception:
            pass
        self._pickup_burst(m, ((84, 185, 196), (136, 219, 226),
                               (250, 244, 222), WHITE))
        self.float_texts.append(FloatText(
            "UMBRELLA!", m.x, m.y - 26, (84, 185, 196),
            size=28, life=1.3, vy=-30, style="powerup",
        ))

    def _activate_poison(self, m):
        """Poison trap (genie-only). Starts Bird.poison_t at 0; Bird.update
        ramps it toward 1.0 over POISON_DURATION seconds; World.update
        watches for the terminal 1.0 and fires _die(). Knight saves the
        bird AND clears the poison state — only escape path."""
        self.bird.poison_active = True
        self.bird.poison_t = 0.0
        self.shake_mag = max(self.shake_mag, 2.5)
        self.shake_t   = max(self.shake_t, 0.25)
        try:
            audio.play_death()
        except Exception:
            pass
        self._pickup_burst(
            m, ((120, 200, 90), (200, 224, 96), (60, 100, 50), WHITE),
            n=20, speed_hi=240,
        )
        self.float_texts.append(FloatText(
            "POISON!", m.x, m.y - 26, (200, 224, 96),
            size=28, life=1.4, vy=-30, style="powerup",
        ))

    def _cull_genie_offers_except(self, chosen: "PowerUp"):
        """Mark every other genie offer collected (so the normal sweep removes
        it next frame) and poof a cloud where each unchosen wish stood, then
        kill any active GenieCharacter so it stops casting."""
        for p in self.powerups:
            if p is chosen or not getattr(p, "is_genie_offer", False):
                continue
            p.collected = True
            self._spawn_grainy_poof(p.x, p.y)
        for g in self.genie_actors:
            g.kill()

    def _activate_reverse(self, m):
        self.reverse_timer = REVERSE_DURATION
        # Zero vy so the flip feels snappy instead of inheriting downward speed.
        self.bird.vy = 0.0
        self.shake_mag = max(self.shake_mag, 2.5)
        self.shake_t = max(self.shake_t, 0.25)
        audio.play_slowmo()
        self._pickup_burst(m, ((170, 90, 230), (110, 50, 180), (215, 165, 250), WHITE))
        self.float_texts.append(FloatText(
            "FLIP!", m.x, m.y - 26, (190, 130, 245),
            size=30, life=1.3, vy=-30, style="powerup",
        ))

    def _activate_shrink(self, m):
        SHRINK_HI  = (80, 180, 240)
        SHRINK_OUT = (30, 90, 160)
        self.shrink_timer = SHRINK_DURATION
        self.bird.shrink_active = True
        self.shake_mag = max(self.shake_mag, 3.0)
        self.shake_t = max(self.shake_t, 0.25)
        audio.play_shrink()
        audio.play_poof()
        self._spawn_poof(self.bird.x, self.bird.y)
        self._pickup_burst(m, (SHRINK_HI, SHRINK_OUT, WHITE, UI_CREAM),
                           n=30, speed_hi=280)
        self.float_texts.append(FloatText(
            "SHRINK!", m.x, m.y - 26, SHRINK_HI,
            size=30, life=1.3, vy=-30, style="powerup",
        ))

    def _activate_rail(self, m):
        """RAIL TRACK — pillar-limited buff. Skips the next pillar (a
        RAIL_LEAD_PILLARS lead-in so players aren't ambushed and have
        time to glide over) then tags the following RAIL_PILLAR_COUNT
        pillars with rail track, parking a stationary cart on the FIRST
        tagged one. Pip is
        NOT auto-locked: he keeps flying with normal flap. If he touches
        the cart pillar the cart locks him in and rides through the
        remaining tagged pillars. The other tagged pillars still have
        track but no cart — touching them kills Pip like any obstacle.
        If picked up WHILE Pip is already locked on the rail (he can't
        dodge), extend the current ride by RAIL_PILLAR_COUNT more
        pillars."""
        if self.bird.cart_locked:
            self._extend_rail_ride(m)
            return
        self.rail_pillars_left = RAIL_PILLAR_COUNT
        self.bird.cart_active = True
        self.bird.cart_locked = False
        self.rail_pending = 0
        for p in self.pipes:
            p.rail_active = False
        ahead = sorted(
            (p for p in self.pipes
             if p.x > self.bird.x and not getattr(p, "is_rush", False)),
            key=lambda p: p.x)[RAIL_LEAD_PILLARS:]
        for p in ahead[:RAIL_PILLAR_COUNT]:
            p.rail_active = True
        tagged_ahead = min(len(ahead), RAIL_PILLAR_COUNT)
        need = RAIL_PILLAR_COUNT - tagged_ahead
        if need > 0:
            self.rail_pending = need
            spacing = self._current_spacing()
            next_x = (max((p.x for p in self.pipes), default=self.bird.x)
                      + spacing)
            guard = need * 3
            while self.rail_pending > 0 and guard > 0:
                self._spawn_pipe(next_x)
                next_x += spacing
                guard -= 1
            self.rail_pending = 0
        self.rail_pipes = [p for p in self.pipes if p.rail_active]
        self.rail_cart_pipe = (sorted(self.rail_pipes, key=lambda p: p.x)[0]
                               if self.rail_pipes else None)
        audio.play_rail()
        self._pickup_burst(m, (UI_GOLD, UI_ORANGE, (255, 220, 100), WHITE), n=28)
        self.float_texts.append(FloatText(
            "RAILS UP!", m.x, m.y - 26, UI_GOLD,
            size=28, life=1.3, vy=-30, style="powerup",
        ))

    def _extend_rail_ride(self, m):
        """Mid-ride pickup: extend the current locked ride by tagging
        more pillars ahead so there are RAIL_PILLAR_COUNT tagged in
        front of Pip, then reset the per-ride budget."""
        ahead = sorted(
            (p for p in self.pipes
             if p.x > self.bird.x and not getattr(p, "is_rush", False)),
            key=lambda p: p.x)
        tagged_ahead = sum(1 for p in ahead
                           if getattr(p, "rail_active", False))
        for p in ahead:
            if tagged_ahead >= RAIL_PILLAR_COUNT:
                break
            if not getattr(p, "rail_active", False):
                p.rail_active = True
                tagged_ahead += 1
        need = RAIL_PILLAR_COUNT - tagged_ahead
        if need > 0:
            self.rail_pending = need
            spacing = self._current_spacing()
            next_x = (max((p.x for p in self.pipes), default=self.bird.x)
                      + spacing)
            guard = need * 3
            while self.rail_pending > 0 and guard > 0:
                self._spawn_pipe(next_x)
                next_x += spacing
                guard -= 1
            self.rail_pending = 0
        self.rail_pipes = [p for p in self.pipes if p.rail_active]
        self.rail_pillars_left = RAIL_PILLAR_COUNT
        audio.play_rail()
        self._pickup_burst(m, (UI_GOLD, UI_ORANGE, (255, 220, 100), WHITE), n=18)
        self.float_texts.append(FloatText(
            "+5 RAILS", m.x, m.y - 26, UI_GOLD,
            size=26, life=1.2, vy=-30, style="powerup",
        ))

    # Pip's centre-y when the cart is locked on the rail — chosen so
    # the cart body sits with its wheels exactly on the rail line.
    _CART_LOCKED_OFFSET = 32

    # Parked-cart hitbox — bounds match the visual painted by
    # scenes._draw_parked_cart so what the player sees as "the cart"
    # is exactly what triggers the lock. Half-width tracks the mine
    # cart's 72-px top (36 each side).
    _CART_HALF_W = 36
    _CART_TOP_OFF = 28
    _CART_BOT_OFF = 5

    def _circle_hits_cart(self, pipe, cx, cy, r):
        """True if the circle at (cx, cy) with radius r overlaps the
        parked-cart rect sitting on `pipe`. The cart lives inside the
        pillar's gap, so touching the pillar BODY of the same pipe
        returns False and falls through to normal pipe collision."""
        cart_cx = pipe.x + PIPE_W // 2
        rail_y = pipe.gap_y + pipe.gap_h / 2
        left = cart_cx - self._CART_HALF_W
        right = cart_cx + self._CART_HALF_W
        top = rail_y - self._CART_TOP_OFF
        bot = rail_y - self._CART_BOT_OFF
        nx = max(left, min(cx, right))
        ny = max(top, min(cy, bot))
        return (cx - nx) ** 2 + (cy - ny) ** 2 <= r * r

    def _lock_pip_on_cart(self):
        """Touched the parked cart — flip into locked-ride mode. Snaps
        Pip onto the rail at the cart pillar's gap-center."""
        self.bird.cart_locked = True
        self._snap_cart_to_rail(self.bird.x)
        self.shake_mag = max(self.shake_mag, 3.0)
        self.shake_t = max(self.shake_t, 0.2)
        audio.play_rail()

    def _snap_cart_to_rail(self, bx):
        """Snap bird.y so the wagon wheels ride the current rail
        segment, interpolating across the bridge between two
        consecutive rail pipes. Also writes the local rail slope to
        bird.cart_tilt_deg so the cart sprite rotates with the curve."""
        sorted_pipes = sorted(self.rail_pipes, key=lambda p: p.x)
        offset = self._CART_LOCKED_OFFSET

        for i, p in enumerate(sorted_pipes):
            if p.x - 6 <= bx <= p.x + PIPE_W + 6:
                rail_y = p.gap_y + p.gap_h / 2
                self.bird.y = rail_y - offset
                self.bird.vy = 0.0
                if i + 1 < len(sorted_pipes):
                    nxt = sorted_pipes[i + 1]
                    self.bird.cart_tilt_deg = self._rail_slope_deg(
                        p.x + PIPE_W, rail_y,
                        nxt.x, nxt.gap_y + nxt.gap_h / 2)
                else:
                    self.bird.cart_tilt_deg = 0.0
                return

        for i in range(len(sorted_pipes) - 1):
            p1, p2 = sorted_pipes[i], sorted_pipes[i + 1]
            if p1.x + PIPE_W <= bx <= p2.x:
                span = max(1, p2.x - (p1.x + PIPE_W))
                t = (bx - (p1.x + PIPE_W)) / span
                y1 = p1.gap_y + p1.gap_h / 2
                y2 = p2.gap_y + p2.gap_h / 2
                self.bird.y = (y1 + (y2 - y1) * t) - offset
                self.bird.vy = 0.0
                self.bird.cart_tilt_deg = self._rail_slope_deg(
                    p1.x + PIPE_W, y1, p2.x, y2)
                return

    @staticmethod
    def _rail_slope_deg(x1: float, y1: float,
                        x2: float, y2: float) -> float:
        """Tilt (degrees, pygame convention) for a rail segment.
        NEGATIVE = downhill-right → nose down; POSITIVE = uphill-right
        → nose up. Capped at ±45° so a wildly steep bridge doesn't
        flip the cart upside-down."""
        dx = x2 - x1
        if dx <= 0.5:
            return 0.0
        dy = y2 - y1
        deg = -math.degrees(math.atan2(dy, dx))
        return max(-45.0, min(45.0, deg))

    def _end_rail_ride(self):
        """End the rail powerup. If Pip rode the cart, release with an
        upward "jump" so the player gets air control on the same
        frame. If he never landed on the cart, clean up silently.
        Existing rail_active flags on already-tagged pipes are NOT
        cleared — the on-screen tail of track scrolls off naturally."""
        was_locked = self.bird.cart_locked
        self.bird.cart_active = False
        self.bird.cart_locked = False
        self.bird.cart_tilt_deg = 0.0
        self.rail_cart_pipe = None
        if was_locked:
            sign = -1 if self.reverse_timer > 0 else 1
            self.bird.vy = FLAP_V * sign
            self.bird.flap_boost = 0.45
            audio.play_flap()

    def _apply_lottery_result(self):
        anim = self.lottery_anim
        if anim is None:
            return
        delta = anim["delta"]
        tier = anim["tier"]
        # Score delta clamps at 0 — total coins never go negative.
        # coin_count is NOT touched (plausibility requires coin_count
        # == len(coin events)); deltas record as a "lottery" event.
        if delta > 0:
            self.score += delta
            self._proof.record(self.time_alive, delta, "lottery")
            color = UI_GOLD if delta >= 40 else UI_ORANGE
            audio.play_lottery_win()
        elif delta < 0:
            actual = -min(self.score, -delta)
            self.score += actual
            if actual != 0:
                self._proof.record(self.time_alive, actual, "lottery")
            color = (220, 70, 60)
            audio.play_lottery_bust()
        else:
            color = (200, 200, 200)
        sign = "+" if delta > 0 else ""
        label = f"{tier}! {sign}{delta}" if delta != 0 else f"{tier}!"
        self.float_texts.append(FloatText(
            label, self.bird.x, self.bird.y - 40, color,
            size=28, life=1.4, vy=-30, style="powerup",
        ))
        if delta >= 100:
            self._pickup_burst(self.bird,
                               (UI_GOLD, UI_ORANGE, UI_CREAM, WHITE),
                               n=40, speed_hi=380)
        elif delta >= 15:
            self._pickup_burst(self.bird, (UI_GOLD, UI_CREAM, WHITE), n=20)
        elif delta < 0:
            self._pickup_burst(self.bird,
                               ((220, 70, 60), (140, 30, 30), (80, 80, 80)),
                               n=18)

    def _activate_lottery(self, m):
        # Roll the tier immediately; the reveal animation delays the
        # score change for showmanship.
        labels = [t[0] for t in LOTTERY_TIERS]
        weights = [t[1] for t in LOTTERY_TIERS]
        deltas = {t[0]: t[2] for t in LOTTERY_TIERS}
        tier = random.choices(labels, weights=weights, k=1)[0]
        delta = deltas[tier]
        self.lottery_anim = {
            "t": 0.0,
            "tier": tier,
            "delta": delta,
            "x": m.x,
            "y": m.y,
            "applied": False,
        }
        self.shake_mag = max(self.shake_mag, 2.5)
        self.shake_t = max(self.shake_t, 0.2)
        audio.play_lottery_roll()
        self._pickup_burst(m, (UI_GOLD, UI_ORANGE, UI_CREAM, WHITE), n=22)
        self.float_texts.append(FloatText(
            "LOTTERY!", m.x, m.y - 26, UI_GOLD,
            size=26, life=1.0, vy=-30, style="powerup",
        ))

    # ── utility ──────────────────────────────────────────────────────────────

    def shake_offset(self):
        if self.shake_t <= 0 or self.shake_mag <= 0:
            return 0, 0
        amp = self.shake_mag * (self.shake_t / 0.45)
        return (random.uniform(-amp, amp), random.uniform(-amp, amp))
