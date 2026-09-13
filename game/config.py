W, H   = 360, 640
FPS    = 60
TITLE  = "Skybit"
VERSION = "1.1.0"          # shown on Settings → Credits; keep in sync with pyproject

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

# Pip carries the parcel for the entire run. The parcel's collision
# footprint is a second circle below the bird; pillars touching that
# circle are also lethal.
PARCEL_R          = 9    # forgiving (parcel sprite is 22 px so r=11 would catch its corners)
PARCEL_Y_OFFSET   = 12   # px below bird-centre to parcel-centre (matches intro composition)

COIN_R             = 13

# Coin-rush: every Nth pipe gets a wider gap filled with a dense coin arc.
COIN_RUSH_INTERVAL = 15
COIN_RUSH_GAP_BOOST = 1.30
COIN_RUSH_COINS    = 14

POWERUP_R          = 14    # collision + footprint radius for every power-up
POWERUP_CHANCE     = 0.24  # chance to spawn a power-up after a pipe gate
POWERUP_CHANCE_NEWBIE = 0.10  # warmup starting chance; ramps to POWERUP_CHANCE
                              # on the same _ramp_t() curve as gap/scroll/spacing
                              # so the opening doesn't feel like a powerup parade
POWERUP_COOLDOWN   = 5.5   # min seconds between power-up spawns
# Dead-Pip cross-fade: alpha-blend from alive sprite to dead palette
# over this many seconds starting at the collision moment.
DEATH_FADE_DURATION = 0.4
TRIPLE_DURATION    = 8.0
MAGNET_DURATION    = 8.0
MAGNET_RADIUS      = 82.0
# Megamagnet — the late-game upgrade form of `magnet`. Same duration,
# 2x pull radius. Magnet is REPLACED by megamagnet at the score
# threshold below — both never spawn simultaneously (see
# POWERUP_REPLACED_AT + the spawn filter in World._maybe_spawn_powerup).
MEGAMAGNET_DURATION = 8.0
MEGAMAGNET_RADIUS   = MAGNET_RADIUS * 2.0   # = 164
SLOWMO_DURATION    = 8.0
SLOWMO_SCALE       = 0.7
KFC_DURATION       = 8.0
KFC_GAP_BOOST      = 1.30    # gap_h multiplier on KFC-flagged pipes - makes
                             # the powerup feel as generous as the bucket
                             # variant already looks. Stacks with COIN_RUSH.
GHOST_DURATION     = 8.0
GROW_DURATION      = 8.0
GROW_SCALE         = 1.4
REVERSE_DURATION   = 8.0
SHRINK_DURATION    = 8.0
SHRINK_SCALE       = 0.6
SHRINK_TRANSITION  = 0.45
RAIL_PILLAR_COUNT  = 7       # cart rides over exactly N pillars then releases
RAIL_LEAD_PILLARS  = 1       # pillars to skip before the cart so players have
                            # time to reach it (cart parks on the 2nd ahead)
RAIL_SCROLL_MULT   = 2.5     # world scrolls 2.5x faster during the ride
RAIL_ABOVE_FINIAL  = 6       # rail track sits this many px above the (lethal)
                            # finial tips — on top of the kill zone, just above
                            # the antennas, with short posts connecting down
# Lottery tiers: (label, weight, coin_delta). Weights need not sum to anything
# — normalized at pick time. Loss tiers clamp at score 0 (see
# World._apply_lottery_result), so total coins never go negative.
LOTTERY_TIERS = (
    ("JACKPOT",  5,  100),
    ("BIG WIN", 12,   40),
    ("WIN",     20,   15),
    ("NOTHING", 35,    0),
    ("LOSS",    20,  -10),
    ("BUST",     8,  -50),
)
LOTTERY_REVEAL_TIME = 1.0

# Spawn weights for power-up kinds. Must sum to anything — they're
# normalized at pick time. `surprise` resolves at pickup-time to one of
# the six "real" early-game kinds (triple/magnet/slowmo/kfc/ghost/shrink)
# chosen at random — see World._on_powerup.
# `reverse` is intentionally excluded — the implementation is kept in
# place but the power-up doesn't spawn or resolve from a surprise box.
# To re-enable: add ("reverse", 1) below AND restore "reverse" in the
# random.choice() inside World._on_powerup.
# `grow`, `rail`, and `lottery` are late-game late-game-gated (see
# POWERUP_SCORE_GATES below) and intentionally NOT in the surprise
# re-roll pool — letting surprise bypass the gate would defeat the
# purpose of the gate.
POWERUP_WEIGHTS    = (
    ("triple",     1),
    ("slowmo",     1),
    ("magnet",     1),
    ("kfc",        1),
    ("ghost",      1),
    ("shrink",     1),
    ("surprise",   1),
    ("grow",       1),
    ("rail",       1),
    ("lottery",    1),
    ("megamagnet", 1),
)

# Per-kind minimum score before a power-up enters the spawn roll.
# Filter applied in World._maybe_spawn_powerup. Omitted kinds are
# unrestricted (gate of 0). Lets late-game pickups stay rare for new
# players while showing up reliably once the run has built momentum.
POWERUP_SCORE_GATES = {
    "rail":       100,
    "grow":       200,
    "lottery":    250,
    "megamagnet": 250,
}

# Per-kind score at which the kind is REMOVED from the spawn pool.
# Used to implement upgrade-style swaps: when the run hits this
# score, the listed kind stops spawning (presumably replaced by an
# upgraded variant that gates IN at the same score). Filter applied
# in World._maybe_spawn_powerup alongside POWERUP_SCORE_GATES.
POWERUP_REPLACED_AT = {
    "magnet": 250,   # at 250+, megamagnet (radius 2x) takes over
}

# ── Secret late-game power-ups ───────────────────────────────────────────────
# A separate, undeclared tier that only enters the spawn roll once the run
# crosses LATE_GAME_PILLAR pillars. Kept out of POWERUP_WEIGHTS (and the
# Surprise re-roll) so the gate can't be bypassed, and out of the help screen
# so the roster stays a surprise. Weights are normalized at pick time alongside
# the normal pool.
#
# The milestone is keyed to PILLARS PASSED (not score) so it lands at the
# same gameplay moment every run regardless of coin pickups, lottery wins,
# or storm-jolt deductions. A genie lamp is placed in the spacing between
# pillar LATE_GAME_PILLAR and the next pillar (so the player encounters it
# right after scoring that pillar). From that moment, the genie is also added
# to the regular spawn pool and the Surprise Box re-roll pool.
LATE_GAME_PILLAR       = 50
# The genie lamp's pillar number is resolved in weather.GENIE_PILLAR as
# pillar_for_phase(THERMAL_PEAK_PHASE) + GENIE_PILLARS_AFTER_GEYSER_PEAK,
# anchoring it to the geyser event so both stay in sync when thermal tuning changes.
GENIE_PILLARS_AFTER_GEYSER_PEAK = 3
# DEBUG: extra genie spawn early in the run so the pickup + chamber + wishes
# can be exercised without playing through the full milestone. Same one-shot rules
# as the production milestone (also flips on the genie pool + surprise-box
# choices). Set to None to disable.
DEBUG_GENIE_PILLAR     = None
# Only the genie spawns directly from the secret tier. Knight, skateboard,
# and poison are reachable EXCLUSIVELY via the genie's fixed offer — they
# are not in any weight table and cannot be Surprise-re-rolled.
SECRET_POWERUP_WEIGHTS = (
    ("genie", 0.125),
)

# POISON — the genie's trap pick. Picking it sets Bird.poison_active and
# ramps Bird.poison_t over POISON_DURATION seconds; at t = 1.0 World._die
# fires. No recovery (knight save still applies — it's the only escape).
POISON_DURATION = 8.0

# GENIE — picking up the lamp summons a conjurer who lays out GENIE_OFFER_COUNT
# alternate power-ups ahead of Pip; flying into one claims it and poofs the rest.
GENIE_OFFER_COUNT   = 3
GENIE_OFFER_X_START = 200
GENIE_OFFER_X_STEP  = 60
GENIE_OFFER_Y_SLOTS = (220, 320, 420)
# GENIE CHAMBER — the next pillar after a genie cast becomes a 2.0x-wider
# gap with the 3 offers stacked vertically inside it (random order), so
# Pip must fly through the gap and pick one wish by altitude.
GENIE_CHAMBER_GAP_BOOST = 2.0
GENIE_CHAMBER_SPACING   = 105
# Wishes pop in with a reveal poof once the chamber pillar is within
# this many px of Pip — gives ~1.5 s of read time at SCROLL_BASE.
GENIE_CHAMBER_REVEAL_DIST = 250

# SKATEBOARD — timed grind/slide buff. The world scrolls faster while Pip is
# actually grinding a surface; the boost eases in over SKATE_SLIDE_ATTACK and
# fades over SKATE_SLIDE_RELEASE so it reads as "skate rush, gentle coast".
# Flapping while skating spins a backflip trick.
SKATEBOARD_DURATION = 20.0
SKATE_SLIDE_MULT    = 1.5
SKATE_SLIDE_ATTACK  = 0.18
SKATE_SLIDE_RELEASE = 0.55
# Trick tap-detection windows. A flap while SKATEBOARD is active is
# routed through World._track_skateboard_tricks which inspects the
# gap to the previous tap and decides which trick to fire. Windows
# are disjoint so a single tap advances at most one pattern.
BACKFLIP_TAP_WINDOW   = 0.45    # 3 FAST taps within this gap → backflip
BACKFLIP_DURATION     = 0.85
KICKFLIP_TAP_GAP_MIN  = 0.55    # 2 SLOW taps in this gap → kickflip
KICKFLIP_TAP_GAP_MAX  = 0.75
KICKFLIP_DURATION     = 0.55
POPSHUVIT_TAP_GAP_MIN = 0.46    # 2 MEDIUM taps in this gap → pop shuvit
POPSHUVIT_TAP_GAP_MAX = 0.54
POPSHUVIT_DURATION    = 0.45
HEELFLIP_TAP_GAP_MIN  = 0.85    # 2 VERY-SLOW taps in this gap → heelflip
HEELFLIP_TAP_GAP_MAX  = 1.05
HEELFLIP_DURATION     = 0.55

# KNIGHT — survive-one-hit buff. While active, the next lethal hit is consumed
# and Pip is revived with KNIGHT_INVULN seconds of collision grace.
KNIGHT_DURATION     = 30.0
KNIGHT_INVULN       = 1.5

# LIVES — every run starts with LIVES_PER_RUN hearts. A pipe collision that
# would otherwise end the run instead spends one heart and grants
# LIVES_INVULN_DUR seconds of full collision immunity so Pip can clear the
# obstacle that hit him. LIVES_FLICKER_HZ is the opacity-toggle rate of the
# bird sprite during that grace window (classic i-frame signal).
LIVES_PER_RUN    = 2
LIVES_INVULN_DUR = 1.5
LIVES_FLICKER_HZ = 10

# ── CLOWN EVENT ──────────────────────────────────────────────────────────────
# A scripted set-piece: a tight "warren" gauntlet of fused staff-pillars.
# CLOWN_SLOT_PILLARS is the max gauntlet length (== CLOWN_ROLL_MAX) reserved in
# the timeline so all downstream pillar numbers stay deterministic regardless of
# the actual rolled length. CLOWN_LEADIN_PILLARS is the clear-sky gap between
# the die-reveal and the first warren tower.
CLOWN_START_PILLAR    = 65
CLOWN_SLOT_PILLARS    = 25           # held max slot width (== CLOWN_ROLL_MAX)
CLOWN_ROLL_MIN        = 10
CLOWN_ROLL_MAX        = 25
CLOWN_WARREN_SPACING  = 72           # fused centre-to-centre spacing (vs PIPE_SPACING)
CLOWN_WARREN_GAP      = 172          # per-pillar gap height inside the gauntlet
CLOWN_PRECLEAR_PILLARS = 2           # phantom empties BEFORE the clown+die appear
CLOWN_LEADIN_PILLARS  = 1            # empties after the die reveal, before the gauntlet
CLOWN_OUTRO_PILLARS   = 1            # empties right after the gauntlet

# Rain intensity above which the storm-jolt lightning strike can fire.
STORM_JOLT_RAIN_MIN   = 0.85

# RAIN + THUNDERSTORM anchor. The dusk storm block (drizzle build →
# storm peak → fade, plus the in-game lightning gate) is shifted along
# the biome phase axis so its drizzle's lower edge lands at this
# pillar number. The block's SHAPE/WIDTH/PEAK HEIGHT is unchanged —
# only the start anchor moves. Tune this to move the whole storm
# earlier (smaller pillar) or later (larger pillar); weather.py
# derives the phase shift from the same onboarding-ramp dwell math
# the world uses, so the storm always lands at the chosen pillar.
#
# The clown event occupies CLOWN_START_PILLAR … CLOWN_START_PILLAR +
# CLOWN_SLOT_PILLARS − 1 (pillars 65–89). CLOWN_TO_RAIN_BUFFER gives
# a gap of clean gameplay between the clown outro and the first drizzle
# so the two events never overlap.
CLOWN_TO_RAIN_BUFFER      = 10          # gap between clown end and rain drizzle
_RAIN_START_PILLAR_PRE_CLOWN = 70       # original pre-clown anchor (reference only)
_SNOW_START_PILLAR_PRE_CLOWN = 139      # original pre-clown anchor (reference only)
RAIN_START_PILLAR   = (                 # pillar 100
    CLOWN_START_PILLAR + CLOWN_SLOT_PILLARS + CLOWN_TO_RAIN_BUFFER
)
_POST_CLOWN_SHIFT   = RAIN_START_PILLAR - _RAIN_START_PILLAR_PRE_CLOWN  # +30
_FINALE_SNOW_BUFFER_PILLARS = 12        # snow-to-finale clearance

# Extra scroll time (seconds) the biome day must cover to accommodate
# the clown block. Keeps every post-clown phase-anchor in sync because
# weather.py and World._seed_first_pipes both read this.
DAY_EXTRA_SECONDS   = (_POST_CLOWN_SHIFT + _FINALE_SNOW_BUFFER_PILLARS) * (PIPE_SPACING / SCROLL_BASE)

# SNOW SQUALL anchor. Same idea as RAIN_START_PILLAR but for the
# predawn snow-squall block in `weather.storm_intensity`. The bump's
# lower edge lands at this pillar; the SHAPE/WIDTH (half-width 0.10,
# scale 1.045) stay unchanged, so only the start anchor moves.
SNOW_START_PILLAR   = _SNOW_START_PILLAR_PRE_CLOWN + _POST_CLOWN_SHIFT  # 169

# Seconds of scroll buffer added to the first seeded pipe's spawn x so
# the cottage opener has clean air to scroll behind Pip before pillars
# take over. Single source of truth so the chart's `_phase_for_pillar`
# and the World's `_seed_first_pipes` agree on the first-pillar offset.
SPAWN_GRACE         = 1.5

# UMBRELLA — independent power-up that cancels the rain flap-dampen during
# thunderstorms. Spawns exactly at the pillar numbers in
# UMBRELLA_SPAWN_PILLARS (NOT in POWERUP_WEIGHTS or the surprise re-roll),
# both of which fall inside the dusk rain block, so the pickup naturally
# only appears while it's raining (a cull step also drops any uncollected
# umbrella once rain returns to 0).
UMBRELLA_DURATION       = 8.0
UMBRELLA_SPAWN_PILLARS  = (RAIN_START_PILLAR + 12, RAIN_START_PILLAR + 24)  # (112, 124)

# TREASURE BOX — once-per-biome-cycle finale reward. When the day/night
# cycle wraps from late-night back to dawn, the next CYCLE_FINALE_RUSH_PILLARS
# pillars are forced into a continuous coin rush; the middle pillar (index
# CYCLE_FINALE_BOX_INDEX, 0-based) additionally drops a treasure_box
# PowerUp at the gap centre. Picking it up grants +TREASURE_BOX_GRANT to
# the score with a grandiose fanfare animation. Not in POWERUP_WEIGHTS
# (weight 0) — only the cycle-finale path spawns it, never a random roll.
TREASURE_BOX_GRANT          = 100
CYCLE_FINALE_RUSH_PILLARS   = 3
CYCLE_FINALE_BOX_INDEX      = 1     # 0-based; pillar 2 of 3 carries the chest
CYCLE_FINALE_PHASE_HI       = 0.95  # rollover detected when last phase > HI
CYCLE_FINALE_PHASE_LO       = 0.05  # AND new phase < LO (wrap from ~1 to ~0)
# Seconds the chest stays drawn after pickup, rendering the lid-popped
# sprite + halo bloom + fade so the loot beat reads as a moment, not a
# blink. Coincides with the audio fanfare tail.
TREASURE_BOX_ANIM_T         = 1.5

# ── Per-day difficulty ramp ──────────────────────────────────────────────────
# Skybit's biome cycle (~5.3 min) is a "day". Each cycle a player completes
# nudges the world a touch harder so a skilled run doesn't plateau on
# muscle memory. Step-then-plateau curve — applied at the cycle-finale
# wrap, holds for the new day, no gradual creep within a day. Silent (no
# HUD telegraph) — the chest-finale banner is the only signal players need.
DAY_SCROLL_STEP   = 8.0   # px/s added to SCROLL_BASE per completed day
DAY_SCROLL_CAP    = 220.0 # ceiling on the post-ramp scroll base (RAIL ×2.5
                          # and the snow-squall tailwind ×1.42 still stack on
                          # top — a day-8 RAIL ride cresting the squall peak ≈
                          # 781 px/s, absorbed by the +2-pillar slack in
                          # _plausibility.pillars_ceiling)
DAY_GAP_STEP      = 5     # px removed from GAP_START per completed day
DAY_GAP_FLOOR     = 135   # gap floor — sits well above the inert GAP_MIN
                          # (115); below ~130 the play-area for Pip + parcel
                          # starts to feel random rather than challenging.

# ── Pipe collision (hitbox forgiveness) ──────────────────────────────────────
# Effective bird radius for pipe collisions = BIRD_R - PIPE_HITBOX_SHRINK.
# Was 12 px (BIRD_R - 2); 10 px makes pillars feel less magnetic without
# letting the bird visibly clip through.
PIPE_HITBOX_SHRINK = 4

# ── Weather → gameplay ──────────────────────────────────────────────────────
# Layer 1 of weather-as-input: light rain wobbles coins, heavy rain slides
# them and shivers Pip + dampens his flap. All values derived from
# weather.rain_intensity(phase) which already exists.
WEATHER_HEAVY_THRESHOLD  = 0.5
# Peak left-right shake amplitude at rain_intensity = 1.0. Scales
# linearly with rain intensity so the tremor grows smoothly from
# barely-there at first drizzle (≈ 0.4 px at ri=0.1) to clearly
# violent at peak storm (4.0 px). No vertical drift, no sliding —
# the wobble is the ONLY weather effect on coins.
WEATHER_COIN_SHAKE_AMP   = 4.0
WEATHER_PIP_SHIVER_AMP   = 1.5
WEATHER_FLAP_DAMPEN_MAX  = 0.18

# Tailwind event (predawn, phase ~0.85). Two effects scaled by
# weather.wind_intensity(phase):
#   - WEATHER_WIND_LEAN_AMP: max RIGHTWARD visual x-offset on
#     the bird (in screen pixels) when wind = 1.0. Pure visual
#     — does not affect collision (Bird.x stays at BIRD_X).
#     Positive direction is rightward (ahead of normal), applied
#     via Bird.draw shake_x. At 11.0 px Pip's push is ~17% of his
#     64-px sprite width, clearly visible as "tailwind boost".
#   - WEATHER_WIND_SCROLL_FACTOR: max fraction the world scroll
#     is INCREASED at peak wind. At wind 1.0 the scroll runs at
#     (1 + factor) × normal so pipes/coins approach faster and
#     the player covers more distance per second. 0.40 means
#     40% more progress at peak — the sweet spot between the calmer
#     0.37 and the 0.42 that played too hard.
WEATHER_WIND_LEAN_AMP     = 11.0
WEATHER_WIND_SCROLL_FACTOR = 0.40

# Windblown snow accumulating on Pip during the snow squall. bird.snow_load
# (0..1) builds at a CONSTANT (uniform) rate only while it's snowing HARD
# (storm_intensity >= WEATHER_SNOW_ON_WI), so it starts a bit INTO the storm
# (~phase 0.84, not the first faint flakes), holds full through the heavy part,
# then defrosts as the snowfall lightens — clearing as the storm ends (~1.03).
# See the threshold model in weather.Weather.update.
WEATHER_SNOW_ON_WI      = 0.45    # storm intensity at/above which snow builds — gates the
                                  # START (~phase 0.84, a bit into the storm)
WEATHER_SNOW_MELT_AT    = 0.04    # phase PAST the peak at which defrost begins (independent
                                  # of the start): ~phase 0.95 → snow sheds and is gone ~1.0
WEATHER_SNOW_ACCUM_RATE = 0.037   # constant build pace while it's snowing hard (~full by ~0.92)
WEATHER_SNOW_MELT_RATE  = 0.06    # defrost pace past the peak (gone ~the day boundary)

WEATHER_WET_ON_RI      = 0.18   # rain intensity at/above which paving wets up
WEATHER_WET_RISE_RATE  = 0.45   # per-second wetness build while raining hard
WEATHER_WET_DRY_RATE   = 0.18   # per-second dry-out once the rain eases

WEATHER_CROWD_RAIN_MIN   = 0.22  # crowd-density multiplier at heaviest rain
WEATHER_CROWD_SNOW_MIN   = 0.06  # crowd-density multiplier at snow-squall peak
WEATHER_UMBRELLA_RAIN_AT = 0.12  # rain intensity at which umbrellas appear in the crowd

# ── Morning-thermal geysers ─────────────────────────────────────────────────
# Ground geysers spawned during the thermal window. Spawn density + how many
# appear at once (1→GEYSER_MAX_CONCURRENT) scale with the live intensity, so
# they build sparse→busy toward the ~96s peak. Each geyser, once spawned, is
# ALWAYS erupting: a continuous wind column that reaches the top of the screen
# and a STRONG continuous updraft. Anywhere inside the column's width — at any
# height, all the way up — the air pushes Pip upward (he rides it to the top;
# the ceiling clamps him, it never kills). The push is capped only in SPEED so
# the ride stays readable, not in reach.
THERMAL_SPAWN_THRESHOLD  = 0.08   # legacy floor (kept; geyser gate uses the threshold below)
THERMAL_SPAWN_CHANCE_MAX = 0.85   # per-pillar geyser spawn chance at peak intensity
GEYSER_SPAWN_THRESHOLD   = 0.35   # intensity above which GEYSERS (not just rocks) spawn
GEYSER_MAX_CONCURRENT    = 3      # cap on simultaneous geysers (allowed scales 1→3 with intensity)
ROCK_SPAWN_THRESHOLD     = 0.02   # intensity above which scattered sinter rocks appear
ROCK_PER_PILLAR_MAX      = 32     # rocks scattered per pillar at full density (the maximum, reached right at the first geyser)
ROCK_RING_COUNT          = 6      # extra rocks framing each geyser's base so the ground reads as "surrounded", not bare
GEYSER_RAMP_PILLARS      = 8      # rocks-only pillars the field ramps across (1-2 → max) before the FIRST geyser — a readable "something's coming" telegraph
GEYSER_W            = 84.0        # column / lift width (px) — matches the visible air footprint
GEYSER_H            = float(GROUND_Y)  # column reaches the top of the screen; lift acts the full height
GEYSER_LIFT_VY_CAP  = 110.0       # CONSTANT rise speed inside any column — gentle/casual so the event helps rather than challenges; one constant for every geyser, no stacking, flaps (|FLAP_V|=520) still override. Lower than terminal so post-column bleed-off time shrinks and the next pillar stays reachable.
GEYSER_ACTIVE_HOT   = 3.0         # active-window length at peak intensity (s)
GEYSER_ACTIVE_COLD  = 1.0         # active-window length at the sparse edges (s)
GEYSER_DORMANT_HOT  = 1.2         # dormant gap between actives at peak (s)
GEYSER_DORMANT_COLD = 7.0         # dormant gap at the sparse edges (s)
GEYSER_TELEGRAPH    = 0.5         # bubbling lead-in before the column rises (s)
# Max gap-y delta allowed between two pillars with a geyser column planted
# between them. Without this clamp the column pins the bird near the top
# while pillar B's gap can be arbitrarily low, leaving a ~98 px drop window
# (spacing/2 - GEYSER_W/2) that gravity cannot cover for large Δgy. 140 px
# leaves headroom even under newbie scroll + Grow.
GEYSER_GY_DELTA_MAX = 140
# Max right-shift of the column from the inter-pillar gap midpoint when the
# next pillar's gap is lower than the current one's. Linear in Δgy: 0 at
# Δgy ≤ 0, GEYSER_GX_SHIFT_MAX at Δgy ≥ GEYSER_GY_DELTA_MAX. Bounded so
# post-column gap stays ≥ ~30 px at standard spacing (pre/post = 70 px each
# at center, becomes 110/30 at max shift) — leaves the bird real recovery
# room after the forced in-column rise.
GEYSER_GX_SHIFT_MAX = 40
# Probability a planted geyser is a "dud" — the sinter cone + rock ring still
# appear on the ground, but no hot-air column erupts and no updraft is applied
# (Geyser.active flag stays False). Adds visual variety + asks the player to
# read the field rather than assume every vent will lift them.
GEYSER_DUD_CHANCE = 0.25

# ── Onboarding warmup ramp ──────────────────────────────────────────────────
# Keyed on pillars_passed: every pipe scored nudges the gap, scroll, and
# spacing one notch closer to the regular endpoints (GAP_START / SCROLL_BASE
# / PIPE_SPACING). After RAMP_PIPES the ramp is complete and the game stays
# at today's regular tuning forever — no late-game tightening to GAP_MIN /
# SCROLL_MAX.
RAMP_PIPES           = 25
# Pillars at the very start of a run that hold the full newbie tuning
# (gap / scroll / spacing / powerup chance) flat before the ease-out ramp
# in World._ramp_t kicks in. Gives complete first-timers a short
# predictable runway to internalize flap timing without anything
# tightening underneath them. Five pillars is ~15 s at PIPE_SPACING_NEWBIE
# / SCROLL_NEWBIE_BASE — short enough that experienced players don't
# perceive a "tutorial mode."
PLATEAU_PIPES        = 5
GAP_NEWBIE_START     = 225
SCROLL_NEWBIE_BASE   = 125.0
PIPE_SPACING_NEWBIE  = 370

SAVE_FILE = "skybit_save.json"
SCORES_FILE = "skybit_scores.json"
STORE_FILE = "skybit_store.json"

DAILY_REWARD = 75


# Store visual design:
#   "classic" — the original store look (plus the banner draw-order fix)
#   "antique" — aged-gold metalwork: D1 double-bevel perimeter,
#               inner-keyline buttons, constellation-web ornament
#   "gilded"  — polished rim-shine gold perimeter at x1.4 weight,
#               swash-underlined BUY
STORE_DESIGN = "antique"
