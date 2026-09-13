"""
Scene state machine (Menu / Play / Run-summary / …) plus the top-level App class.
"""
import math
import random
import pygame

from game.config import W, H, FPS, TITLE, GROUND_Y
from game.draw import (
    get_sky_surface_biome, draw_mountains, draw_cloud,
    UI_RED,
)
from game import biome as _biome
from game import cloud_variants
from game import foreground
from game import sky_designs
from game.world import World
from game.hud import HUD, _font
from game import audio
from game import play_log
from game.config import BIRD_X, SCROLL_BASE, SPAWN_GRACE

# One persistent full-screen overlay reused for every play-scene tint
# (slow-mo / KFC / ghost / hit-flash) so an active effect costs a fill+blit
# instead of allocating a fresh W x H SRCALPHA surface each frame.
_SCENE_TINT = pygame.Surface((W, H), pygame.SRCALPHA)
from game import intro as _intro
from game.lottery_slot import draw_reveal as _draw_lottery_reveal

# Pixels of `bg_scroll` covered while the gameplay opener is active. After
# the post-ready grace window, the cottage is fully off-screen-left and the
# overlay shuts itself off. SPAWN_GRACE was moved to config but this
# reference still pointed at the long-deleted World class attribute.
_OPENER_SCROLL_END = int(SPAWN_GRACE * SCROLL_BASE)

# Reused scratch surface for the lightning bolt so the strike doesn't allocate
# (and full-screen-blit) one surface per glow-layer per bolt every frame.
_bolt_scratch_cache: dict = {}


def _draw_lightning_bolt(surf, strike):
    """Paint the storm-jolt lightning — the main bolt that strikes Pip plus
    (when present) two flanking bolts in `strike["paths"]`, so the sky forks
    with three simultaneous strikes at the climax. Four concentric layers per
    bolt — wide plasma bloom, outer purple glow, cyan halo, white core. Alpha
    holds full for the first 35% of life so the zig-zags read, then decays;
    flanking bolts a touch thinner. Round circles at every waypoint so each
    polyline reads as one crackle."""
    if strike is None or strike.get("life", 0) <= 0:
        return
    paths = strike.get("paths") or ([strike["path"]] if strike.get("path") else [])
    paths = [p for p in paths if len(p) >= 2]
    if not paths:
        return
    life = strike["life"]
    life_max = strike["life_max"]
    raw_t = max(0.0, min(1.0, life / life_max))
    HOLD = 0.35
    if raw_t >= 1.0 - HOLD:
        t = 1.0
    else:
        t = raw_t / (1.0 - HOLD)
    t_glow = t ** 0.7
    sw, sh = surf.get_size()
    # All layers/bolts paint onto one reused scratch surface (cleared per
    # frame) so the strike does a single blit instead of one full-screen
    # allocation + blit per layer per bolt.
    scratch = _bolt_scratch_cache.get((sw, sh))
    if scratch is None:
        scratch = pygame.Surface((sw, sh), pygame.SRCALPHA)
        _bolt_scratch_cache[(sw, sh)] = scratch
    scratch.fill((0, 0, 0, 0))
    for bi, path in enumerate(paths):
        ws = 1.0 if bi == 0 else 0.65            # flanking bolts thinner
        layers = (
            ((130,  80, 220), int(70 * t_glow),  max(1, int(18 * ws))),
            ((180, 100, 255), int(170 * t_glow), max(1, int(12 * ws))),
            ((140, 220, 255), int(235 * t_glow), max(1, int(7 * ws))),
            ((255, 255, 255), int(255 * t),      max(1, int(4 * ws))),
        )
        pts = [(int(x), int(y)) for (x, y) in path]
        # Widest/dimmest first so the bright core overwrites the centre and
        # the wide glow stays at the edges.
        for col, alpha, width in layers:
            if alpha <= 0 or width <= 0:
                continue
            pygame.draw.lines(scratch, (*col, alpha), False, pts, width)
            joint_r = max(1, width // 2)
            for px, py in pts:
                pygame.draw.circle(scratch, (*col, alpha), (px, py), joint_r)
    surf.blit(scratch, (0, 0))


def _draw_opener(surf: pygame.Surface, world) -> None:
    """Gameplay opener — cottage drifting off-screen-left + parcel tucked
    beneath Pip. Mirrors the intro's beat-2 ending so the cut from menu →
    play preserves the cinematic's final image. Runs for the first
    ``World.SPAWN_GRACE`` seconds after the ready_t freeze expires."""
    progress = world.bg_scroll / _OPENER_SCROLL_END
    if progress >= 1.0:
        return
    # Fade out over the last 30% so the cottage doesn't snap-disappear.
    fade = 1.0 if progress < 0.7 else max(0.0, 1.0 - (progress - 0.7) / 0.3)
    alpha = int(255 * fade)

    house = _intro.get_sprite("skyhouse_post")
    house_cx = int(W * 0.30) - int(world.bg_scroll)
    house_cy = int(H * 0.42)
    hx = house_cx - house.get_width() // 2
    hy = house_cy - house.get_height() // 2
    if hx + house.get_width() > 0 and alpha > 0:
        if alpha < 255:
            faded = house.copy()
            faded.set_alpha(alpha)
            surf.blit(faded, (hx, hy))
        else:
            surf.blit(house, (hx, hy))
    # The parcel itself is now drawn permanently by Bird.draw, so the
    # opener no longer needs its own parcel pass.


# ── Rail powerup render helpers (called from App._render) ──────────────────

_PINE_DK = ( 70,  45,  25)
_PINE    = (135,  90,  50)
_PINE_HI = (180, 130,  75)
_IRON_DK = ( 50,  45,  45)
_IRON    = (110, 100,  95)
_IRON_HI = (190, 180, 175)

# Mine-cart palette (railway-design `paint_mine_cart`).
_MINE_DK   = ( 40,  30,  28)
_MINE      = ( 95,  75,  65)
_MINE_HI   = (175, 155, 140)
_MINE_RIV  = (210, 190, 170)
_MINE_RUST = (140,  60,  20)

# The cart layers are laid out so the rail-contact line (wheel bottoms)
# sits this many px BELOW the sprite centre. Callers anchor the sprite
# centre at rail_y - _CART_RAIL_DY, which lands the wheels on the rail.
_CART_RAIL_DY = 16
_CART_WHEELS = None  # cached wheels-only layer, built once
_CART_BODY   = None  # cached bucket-only layer, built once


def _draw_spoked_wheel(surf, cx, cy, r):
    """Iron tire ring + hub disc + 8 radiating spokes + centre cap
    (railway-design `draw_spoked_wheel`, mine-cart palette)."""
    rim = max(2, r // 4)
    pygame.draw.circle(surf, _MINE_DK, (cx, cy), r)
    pygame.draw.circle(surf, _MINE,    (cx, cy), r - rim)
    for i in range(8):
        ang = (i / 8) * math.tau
        ex = cx + int(math.cos(ang) * (r - rim // 2))
        ey = cy + int(math.sin(ang) * (r - rim // 2))
        pygame.draw.line(surf, _MINE_HI, (cx, cy), (ex, ey), max(2, r // 6))
    pygame.draw.circle(surf, _MINE_HI, (cx, cy), max(2, r // 4))


def _build_cart_layers():
    """Build the two cached Mine-Cart layers — wheels and bucket — once,
    at 4x then smooth-scaled down so the spokes and rivets stay crisp.
    Geometry is the railway-design mine cart
    (`render_cart_designs.py:paint_mine_cart`), widened to a 72-px top.
    Both layers share one canvas + anchor so they register exactly: the
    rail-contact line (wheel bottoms) sits _CART_RAIL_DY px below the
    sprite centre. The caller draws Pip BETWEEN the two layers, so the
    bucket front overlaps his lower half and he reads as sitting inside."""
    SS = 4  # supersample factor (matches the design render's SCALE)
    SW, SH = 80, 60
    cx = (SW // 2) * SS
    rail_y = (SH // 2 + _CART_RAIL_DY) * SS

    WHEEL_R  = 5 * SS
    CART_W   = 58 * SS
    CART_H   = 18 * SS
    bot_w    = int(CART_W * 0.78)
    WHEEL_DX = bot_w // 2 - SS  # wheels tucked just inside the bottom corners

    # ── Wheels layer ──
    wheels = pygame.Surface((SW * SS, SH * SS), pygame.SRCALPHA)
    for dx in (-WHEEL_DX, WHEEL_DX):
        _draw_spoked_wheel(wheels, cx + dx, rail_y - WHEEL_R, WHEEL_R)

    # ── Bucket layer — trapezoid (wider at top) + rivets + rust line ──
    body = pygame.Surface((SW * SS, SH * SS), pygame.SRCALPHA)
    top_w = CART_W
    body_top = rail_y - 2 * WHEEL_R - CART_H
    body_bot = rail_y - 2 * WHEEL_R
    pts_outer = [(cx - top_w // 2, body_top), (cx + top_w // 2, body_top),
                 (cx + bot_w // 2, body_bot), (cx - bot_w // 2, body_bot)]
    pygame.draw.polygon(body, _MINE_DK, pts_outer)
    inset = 3 * SS
    pts_inner = [(cx - top_w // 2 + inset, body_top + inset),
                 (cx + top_w // 2 - inset, body_top + inset),
                 (cx + bot_w // 2 - inset, body_bot - inset),
                 (cx - bot_w // 2 + inset, body_bot - inset)]
    pygame.draw.polygon(body, _MINE, pts_inner)
    pygame.draw.rect(body, _MINE_HI,
                     pygame.Rect(cx - top_w // 2, body_top, top_w, 2 * SS))
    pygame.draw.rect(body, _MINE_DK,
                     pygame.Rect(cx - top_w // 2, body_top - SS, top_w, SS))
    rsize = 2 * SS
    for rx, ry in ((cx - top_w // 2 + 4 * SS, body_top + 4 * SS),
                   (cx + top_w // 2 - 4 * SS - rsize, body_top + 4 * SS),
                   (cx - top_w // 2 + 4 * SS, body_bot - 4 * SS - rsize),
                   (cx + top_w // 2 - 4 * SS - rsize, body_bot - 4 * SS - rsize)):
        pygame.draw.rect(body, _MINE_RIV, pygame.Rect(rx, ry, rsize, rsize))
    pygame.draw.line(body, _MINE_RUST,
                     (cx - bot_w // 2 + 6 * SS, body_bot - 2),
                     (cx + bot_w // 2 - 6 * SS, body_bot - 2), max(1, SS // 2))

    return (pygame.transform.smoothscale(wheels, (SW, SH)),
            pygame.transform.smoothscale(body, (SW, SH)))


def _draw_parked_cart_at(surf, cx, cy, tilt_deg=0.0, layer="all"):
    """Blit the Mine Cart centred at the given screen position. `layer`
    picks which part to draw: "wheels" and "body" are the two halves that
    sandwich Pip on the locked ride; "all" draws both (parked cart, no
    Pip). Tilt rotates each layer about the same centre. Layers are built
    once and cached; only the per-frame rotation is paid here."""
    global _CART_WHEELS, _CART_BODY
    if _CART_WHEELS is None:
        _CART_WHEELS, _CART_BODY = _build_cart_layers()
    if layer == "wheels":
        parts = (_CART_WHEELS,)
    elif layer == "body":
        parts = (_CART_BODY,)
    else:
        parts = (_CART_WHEELS, _CART_BODY)
    for sprite in parts:
        if abs(tilt_deg) > 0.5:
            sprite = pygame.transform.rotate(sprite, tilt_deg)
        rect = sprite.get_rect(center=(int(cx), int(cy)))
        surf.blit(sprite, rect.topleft)


def _draw_parked_cart(surf, pipe):
    """Pre-lock cart parked on the rail line of `pipe` (the first
    tagged pillar). Removed once Pip locks or the pillar scrolls past."""
    from game.config import PIPE_W
    cx = pipe.x + PIPE_W // 2
    rail_y = pipe.rail_y
    # 32-px lift matches World._CART_LOCKED_OFFSET so the parked cart
    # sits visually identical to the locked-ride cart.
    _draw_parked_cart_at(surf, cx, rail_y - 16)


def _draw_cart_on_bird(surf, world, sx, sy, layer="all"):
    """Locked-ride cart drawn at Pip's screen position with the local
    rail slope rotation. Drawn in two passes around Pip ("wheels" under,
    "body" over) so he sits inside the bucket."""
    bx = world.bird.x + sx
    by = world.bird.y + sy
    # Bird sits 32 px above the rail line; the cart wheels need to be
    # on the rail, so anchor the cart slightly below the bird centre.
    _draw_parked_cart_at(surf, bx, by + 16, tilt_deg=world.bird.cart_tilt_deg,
                         layer=layer)


def _draw_rails(surf, rail_pipes):
    """Continuous pine-tie + twin iron-rail polyline just above every rail-tagged
    pillar's finial tips, with a short post dropping the rail onto each antenna so
    the track reads as resting on top of the kill zone."""
    from game.config import PIPE_W
    if not rail_pipes:
        return
    pipes_sorted = sorted(rail_pipes, key=lambda p: p.x)
    pts = []
    for p in pipes_sorted:
        rail_y = int(p.rail_y)
        # Support post: connect the rail down onto this pillar's antenna tip.
        cx = int(p.x + PIPE_W // 2)
        tip = int(p.finial_tip_y) + 1
        pygame.draw.line(surf, _IRON_DK, (cx, rail_y), (cx, tip), 3)
        pygame.draw.line(surf, _IRON, (cx, rail_y), (cx, tip), 1)
        pts.append((int(p.x), rail_y))
        pts.append((int(p.x + PIPE_W), rail_y))
    _draw_trestle_rail(surf, pts)


def _draw_trestle_rail(surf, pts):
    """Pine ties + twin iron rails along a polyline. Bridges between
    consecutive pipes keep their ties so the result reads as one
    continuous railway."""
    if len(pts) < 2:
        return

    segs, total = [], 0.0
    for i in range(len(pts) - 1):
        x0, y0 = pts[i]
        x1, y1 = pts[i + 1]
        d = math.hypot(x1 - x0, y1 - y0)
        segs.append((d, (x0, y0), (x1, y1)))
        total += d
    spacing = 8
    length = 14
    half = length / 2
    n = max(1, int(total / spacing))
    for k in range(n + 1):
        target = (k / n) * total
        acc = 0.0
        for d, p0, p1 in segs:
            if acc + d >= target:
                f = (target - acc) / max(1.0, d)
                cx = int(p0[0] + (p1[0] - p0[0]) * f)
                cy = int(p0[1] + (p1[1] - p0[1]) * f)
                dx = p1[0] - p0[0]
                dy = p1[1] - p0[1]
                seg_len = max(1.0, math.hypot(dx, dy))
                nx = -dy / seg_len
                ny = dx / seg_len
                a = (int(cx + nx * half), int(cy + ny * half))
                b = (int(cx - nx * half), int(cy - ny * half))
                pygame.draw.line(surf, _PINE_DK, a, b, 5)
                pygame.draw.line(surf, _PINE, a, b, 3)
                hi_a = (int(cx + nx * half * 0.55),
                        int(cy + ny * half * 0.55))
                hi_b = (int(cx - nx * half * 0.55),
                        int(cy - ny * half * 0.55))
                pygame.draw.line(surf, _PINE_HI, hi_a, hi_b, 1)
                break
            acc += d

    for dy_off, col, w in (
        ( 3, _IRON_DK, 3), (-3, _IRON_DK, 3),
        ( 3, _IRON,    2), (-3, _IRON,    2),
        ( 2, _IRON_HI, 1), (-4, _IRON_HI, 1),
    ):
        shifted = [(x, y + dy_off) for x, y in pts]
        pygame.draw.lines(surf, col, False, shifted, w)


# Hex grid overlay for the magnet force-field. Built once per radius
# and re-blit each frame — the rings pulse but the hex pattern is
# static, so building it lazily here keeps the per-frame work in the
# magnet draw loop bounded (one blit instead of ~225 polygon draws
# at MAGNET_RADIUS). Cells fade from invisible at the centre to full
# alpha at the rim so the bird stays the focal point.
_MAGNET_HEX_GRID_CACHE: "dict[int, pygame.Surface]" = {}


def _magnet_hex_grid(radius: int) -> pygame.Surface:
    cached = _MAGNET_HEX_GRID_CACHE.get(radius)
    if cached is not None:
        return cached
    surf = pygame.Surface((radius * 2 + 8, radius * 2 + 8),
                          pygame.SRCALPHA)
    cx, cy = radius + 4, radius + 4
    hex_r = max(5, int(radius * 0.085))
    hex_w = hex_r * math.sqrt(3)
    hex_h = hex_r * 1.5
    rows = int(radius * 2 / hex_h) + 3
    cols = int(radius * 2 / hex_w) + 3
    for ri in range(-rows // 2, rows // 2 + 1):
        for ci in range(-cols // 2, cols // 2 + 1):
            hx = cx + ci * hex_w + (hex_w / 2 if ri % 2 else 0)
            hy = cy + ri * hex_h
            dx = hx - cx
            dy = hy - cy
            d = math.hypot(dx, dy)
            if d > radius * 0.92:
                continue
            falloff = d / radius
            a = int(160 * (falloff ** 1.5))
            if a < 12:
                continue
            verts = []
            for v in range(6):
                ang = math.tau * v / 6 + math.pi / 6
                verts.append((hx + math.cos(ang) * hex_r,
                              hy + math.sin(ang) * hex_r))
            pygame.draw.polygon(surf, (255, 215, 100, a), verts, 1)
    _MAGNET_HEX_GRID_CACHE[radius] = surf
    return surf


# Persistent magnet-field composite surface (one per field diameter) reused each
# frame, plus a cache of the breathing hex grid scaled to each target size — so
# the active magnet field costs no per-frame Surface alloc and no per-frame
# smoothscale (only the breathing rings/glow are redrawn).
_MAGNET_FIELD_SURF: "dict[int, pygame.Surface]" = {}
_MAGNET_HEX_SCALED: dict = {}


def _magnet_field_surf(d: int) -> pygame.Surface:
    s = _MAGNET_FIELD_SURF.get(d)
    if s is None:
        s = pygame.Surface((d, d), pygame.SRCALPHA)
        _MAGNET_FIELD_SURF[d] = s
    return s


def _magnet_hex_scaled(rad: int, scaled_d: int) -> pygame.Surface:
    key = (rad, scaled_d)
    s = _MAGNET_HEX_SCALED.get(key)
    if s is None:
        s = pygame.transform.smoothscale(_magnet_hex_grid(rad),
                                         (scaled_d, scaled_d))
        _MAGNET_HEX_SCALED[key] = s
    return s


STATE_MENU = 0
STATE_PLAY = 1
STATE_NAMEENTRY = 2
STATE_PAUSE = 4
STATE_STATS = 5
STATE_LEADERBOARD = 6
STATE_INTRO = 7
STATE_POWERUPS = 8
STATE_ACHIEVEMENTS = 9
STATE_ACHV_EARNED = 10
STATE_SETTINGS = 11
STATE_ABOUT = 12
STATE_STORE = 13
STATE_PROFILE = 14

# Background cloud depth slots: (base_x, base_y, scale). Geometry is fixed so the
# parallax-depth spread stays good; all slots share one cloud design per run,
# picked at random (see App._pick_cloud_variant), so each run has a consistent
# cloud style that varies between runs.
_CLOUD_SLOTS = (
    (20, 90, 0.9), (180, 140, 1.1), (60, 220, 0.8),
    (230, 60, 0.7), (320, 180, 0.9), (140, 40, 1.0),
)


class App:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(TITLE)
        self.screen = pygame.display.set_mode((W, H))
        self.clock = pygame.time.Clock()
        audio.init()
        # Apply the saved SFX-mute preference (device-local) before the first sound.
        from game import prefs
        audio.set_muted(prefs.get_muted())
        self.world = World()
        self.hud = HUD()
        self.session_best = 0
        self._new_best = False
        # Which action the player picked on the run-summary screen.
        # Persists across STATE_NAMEENTRY / STATE_LEADERBOARD so that
        # after a top-10 player dismisses the leaderboard they land
        # where they originally chose. Reset on death so each run
        # starts fresh.
        self._post_leaderboard: str = "menu"
        # Intro plays once per program launch — start every session in
        # STATE_INTRO. Within the session (consecutive games after death,
        # menu-tap → play → die → menu) the intro is never replayed since
        # the App stays alive and we already moved past STATE_INTRO.
        from game.intro import IntroScene
        self.intro: object | None = IntroScene()
        # Built lazily when the intro auto-completes (not when the user
        # skips it). Lives until the player taps once on the help screen.
        self.powerup_help: object | None = None
        # Achievements screen — built lazily when opened from the menu,
        # torn down on dismiss. Owns its own scroll/drag state. (Kept for
        # its render/tap-handling code, which ProfileScene reuses in
        # "embedded" mode; the menu's PROFILE tap no longer opens this
        # directly — see _open_profile.)
        self.achievements: object | None = None
        # PROFILE — the shared WARDROBE/ACHIEVEMENTS parent, built lazily on
        # the menu PROFILE tap and torn down on dismiss.
        self.profile: object | None = None
        # Coin store — the lagoon-hub landing + category grids, built lazily on
        # the menu STORE tap and torn down on BACK. Owns its own hub/category
        # navigation + buy-confirm state.
        self.store: object | None = None
        # The end-of-run "ACHIEVEMENT EARNED!" screen — built on death when a
        # run unlocks one or more achievements, shown before the run summary,
        # torn down on the continue tap. Owns its own scroll/drag state.
        self.achv_earned: object | None = None
        # Settings screen — built lazily when opened from the menu SETTINGS chip,
        # torn down on dismiss. Holds the How to Play / Power-Ups launchers.
        self.settings: object | None = None
        # About screen — built lazily when opened from Settings.
        self.about: object | None = None
        # Sub-screen return targets: How to Play (intro) and Power-Ups (explainer)
        # opened from Settings come back to STATE_SETTINGS instead of the menu.
        self._intro_return_state: "int | None" = None
        self._powerups_return_state = STATE_MENU
        # Menu idle clock (Oddities "Are You Still There?"): seconds since the
        # last input while sitting on the menu; unlocks once at 5 minutes idle.
        self._menu_idle_t = 0.0
        self._menu_idle_fired = False
        # True when the intro was launched from the menu's HOW TO PLAY
        # button. _finish_intro reads this to land back on MENU instead
        # of the POWERUPS explainer.
        self._intro_from_menu = False
        self.state = STATE_INTRO
        # The scripted Warren demo (clown → dice → route → fall) is a dev
        # harness kept opt-in behind `--warren` (native CLI only) so this
        # merged line boots the normal intro → power-ups → menu flow on
        # both native and the pygbag/web build. The clown event itself
        # lives in real gameplay; the standalone demo has its own
        # event-test deploy branch.
        import sys as _sys
        self._warren_demo = "--warren" in _sys.argv
        if self._warren_demo:
            self._start_warren_demo()
        self._cloud_phase = 0.0
        self._cloud_variant = 0
        self._pick_cloud_variant()
        self._running = True
        self._stats_t = 0.0
        # True while the HTML splash overlay is still painted on top of
        # the canvas; flips False on the first user-visible frame (in
        # async_run, when first_frame_done is set). The intro update
        # gates on this so the cinematic clock doesn't accumulate while
        # pygbag is still booting — without it, by the time the splash
        # dismisses the intro can be ~7 s in (opening on the "avoid
        # pillars" sub-beat instead of the dawn one).
        self._splash_covering = True
        # Touch dedup: SDL emits both FINGERDOWN and a synthetic MOUSEBUTTONDOWN
        # for one tap on mobile, so naive routing types every key twice. After
        # any FINGERDOWN, suppress mouse events for a 0.5 s window. On pure
        # desktop this never fires (no FINGERDOWN ever arrives).
        self._last_finger_t = -1e9
        self._finger_dedup_window = 0.5
        # Brief grace window after un-pausing during which an in-play tap
        # is ignored — keeps the resume tap (and its echo) from doubling as
        # a flap. Scoped to its own timer so the pause fix can't entangle
        # with the shared _cooldown_t used by menus/leaderboard.
        self._resume_grace_t = 0.0
        # Leaderboard state
        self._lb_scores: list = []
        self._lb_player_rank = -1
        # Last browser-side fetch error code (empty when the fetch
        # succeeded, even if it returned zero rows from a brand-new
        # database). Set by _on_name_submitted / _show_leaderboard_native
        # before flipping to STATE_LEADERBOARD; rendered by the scene
        # when scores is empty so a network/RLS failure doesn't look
        # like "no scores yet."
        self._lb_fetch_error: str = ""
        # Tabbed leaderboard: the CURRENT board (above) plus a read-only
        # LEGACY board (previous version's scores). The legacy board is
        # fetched lazily the first time the player switches to its tab, so
        # the common case (opening on CURRENT, never touching LEGACY) pays
        # no extra network round-trip. Reset on every open via _reset_lb_tabs.
        self._lb_legacy_scores: list = []
        self._lb_legacy_fetch_error: str = ""
        self._lb_selected_tab = 0  # 0 = CURRENT, 1 = LEGACY
        self._legacy_loaded = False
        self._legacy_loading = False  # browser legacy fetch in flight
        self._legacy_task = None  # strong ref for the lazy legacy fetch
        self._start_name_entry = False
        self._fetch_pending = False
        self._final_score = 0
        self._name_task = None  # strong ref prevents GC killing the task mid-flight
        self._play_log_task = None  # strong ref for the per-run telemetry POST
        self._lb_task = None  # strong ref for the menu-trophy leaderboard fetch
        self._name_input_buf = ""  # native name-entry text buffer

        # ── Deferred pre-warm queue ─────────────────────────────────────────
        # Two power-ups had per-pickup build cost (GROW: ~50 ms first
        # build; KFC: 7-37 ms per variant per pickup). Building both at
        # startup made initial load 150+ ms slower. Instead we queue the
        # builds and drain ONE per frame in ``_update`` after the first
        # paint — startup pays nothing, and the cache fills over the
        # next ~4 frames (during the intro animation where the small
        # per-frame cost is masked). ``get_cached_mountain`` builds on
        # demand if a pickup happens before its variant is warm.
        from game import parrot
        from game.fries_mountains import LAYER_DRAWERS, get_cached_mountain
        self._prewarm_queue = [
            ("grow",       lambda: parrot._get_grow_frames()),
            ("first_hit",  lambda: parrot._get_fh_frames()),
            ("hurt",       lambda: parrot._get_hurt_frames()),
            ("kfc0",       lambda: get_cached_mountain(0, GROUND_Y, W)),
            ("kfc1",       lambda: get_cached_mountain(1, GROUND_Y, W)),
            ("kfc2",       lambda: get_cached_mountain(2, GROUND_Y, W)),
        ]

    # ── helpers ─────────────────────────────────────────────────────────────

    @property
    def best(self):
        return self.session_best

    # ── input ────────────────────────────────────────────────────────────────

    def _flap_input(self, pos=None):
        # Any tap/key is activity — reset the menu idle clock.
        self._menu_idle_t = 0.0
        if self.state == STATE_INTRO:
            # Any tap during the cinematic skips it. Gate by `_cooldown_t`
            # so the same physical tap that opened the intro (FINGERDOWN
            # → MOUSEBUTTONDOWN echo, or a duplicate FINGERDOWN on flaky
            # devices) can't immediately skip it back out. The cooldown
            # ticks down inside _update so a deliberate skip works a
            # beat later.
            #
            # Also bail while `_splash_covering` is still True: the HTML
            # splash overlay is on top of the canvas, so the player can't
            # see the intro and isn't tapping it deliberately. The pygbag
            # boot kick (inject_theme.fireSyntheticGesture) dispatches a
            # full pointer/mouse/touch sequence to satisfy the UME gate,
            # and those events reach this handler — without the gate they
            # silently skip the intro before the first frame ever renders.
            if self._splash_covering:
                return
            if self._cooldown_t > 0:
                return
            self._finish_intro(skipped=True)
            return
        if self.state == STATE_POWERUPS:
            # Same shape: gate the dismiss-tap on the entry cooldown so
            # the explainer doesn't flicker straight back out. Returns to the
            # menu, or to Settings when it was opened from there.
            if self._cooldown_t > 0:
                return
            self.powerup_help = None
            self.state = self._powerups_return_state
            self._powerups_return_state = STATE_MENU
            self._cooldown_t = 0.25
            return
        if self.state == STATE_SETTINGS:
            # A tap hits a launcher row (open its scene) or the MENU pill (back).
            # Gated by the entry cooldown so the opening tap's echo can't bounce.
            if self._cooldown_t > 0:
                return
            sc = self.settings
            if pos is None or sc is None:
                return
            mb = getattr(sc, "menu_btn_rect", None)
            if mb and mb.collidepoint(pos):
                self._close_settings()
                return
            for rect, action in getattr(sc, "row_rects", ()):
                if rect.collidepoint(pos):
                    if action == "howto":
                        self._open_howto_from_settings()
                    elif action == "powerups":
                        self._open_powerups_from_settings()
                    elif action == "toggle_sound":
                        self._toggle_sound()
                    elif action == "about":
                        self._open_about()
                    return
            return
        if self.state == STATE_ABOUT:
            if self._cooldown_t > 0:
                return
            sc = self.about
            mb = getattr(sc, "menu_btn_rect", None) if sc is not None else None
            if pos is None or mb is None or mb.collidepoint(pos):
                self._close_about()   # MENU pill (or ESC/key) → back to Settings
            return
        if self.state == STATE_STORE:
            # The store owns its own hub/category/BACK navigation; delegate the
            # tap and only act on the "back" token (BACK on the hub → exit to
            # menu). Gated by the entry cooldown so the opening tap can't bounce.
            if self._cooldown_t > 0:
                return
            if self.store is None:
                self.state = STATE_MENU
                return
            if self.store.handle_tap(pos) == "back":
                self._close_store()  # already sets _cooldown_t = 0.25
            else:
                self._cooldown_t = 0.25  # block duplicate FINGERDOWN double-fire
            return
        if self.state == STATE_MENU:
            # Single shared cooldown gate for every menu action. This is
            # what stops a follow-up event from the same physical tap
            # (e.g. the second FINGERDOWN that dismissed INTRO → MENU)
            # from immediately dispatching a help-button hit at the same
            # screen position. Kept short (0.25 s, set on every menu
            # entry) so a deliberate first tap from a settled menu still
            # feels instant — typical reaction time is well above 0.25 s.
            if self._cooldown_t > 0:
                return
            if pos and self.hud.menu_settings_rect \
                    and self.hud.menu_settings_rect.collidepoint(pos):
                self._open_settings()
                return
            # The framed Pip diorama is the Profile entry — WARDROBE (what's
            # owned) and ACHIEVEMENTS (records), as two tabs of one screen.
            # Checked before START so a tap inside the frame can't fall
            # through to starting a run.
            if pos and self.hud.menu_profile_rect \
                    and self.hud.menu_profile_rect.collidepoint(pos):
                self._open_profile()
                return
            if pos and self.hud.menu_store_rect \
                    and self.hud.menu_store_rect.collidepoint(pos):
                self._open_store()
                return
            if pos and self.hud.menu_top10_rect \
                    and self.hud.menu_top10_rect.collidepoint(pos):
                self._open_leaderboard_from_menu()
                return
            # Start a run only when the player hits the START pill (or
            # presses a key — no pos for keyboard events). Taps that
            # land anywhere else on the menu are a no-op so an accidental
            # touch outside the pill can't fling the player into play.
            if pos is None or (self.hud.menu_start_rect
                               and self.hud.menu_start_rect.collidepoint(pos)):
                self._start_play()
        elif self.state == STATE_PLAY:
            if pos and self.hud.pause_btn.contains(pos):
                self.state = STATE_PAUSE
                return
            # Swallow the resume tap (and its echo) for a beat after leaving
            # PAUSE so the click that un-pauses can't double as a flap — the
            # player wants the game to continue exactly as it was frozen.
            if self._resume_grace_t > 0:
                return
            # Demo locks input for the final scripted fall.
            if getattr(self.world, "demo", None) is not None \
                    and self.world.demo.gates_flap():
                return
            self.world.flap()
        elif self.state == STATE_PAUSE:
            self.state = STATE_PLAY
            self._resume_grace_t = 0.25
        elif self.state == STATE_STATS:
            if self._stats_t < 0.6 or self._fetch_pending:
                return
            # Hit-test the run-summary buttons. The HUD populates these
            # rects each frame in draw_stats; before the 0.6s reveal
            # gate they are empty so taps in that window do nothing.
            play_rect = getattr(self.hud, "stats_play_again_rect", None)
            menu_rect = getattr(self.hud, "stats_main_menu_rect", None)
            if pos and play_rect and play_rect.collidepoint(pos):
                self._post_leaderboard = "play"
                self._advance_past_stats()
            elif pos and menu_rect and menu_rect.collidepoint(pos):
                self._post_leaderboard = "menu"
                self._advance_past_stats()
        elif self.state == STATE_NAMEENTRY:
            pass  # JS overlay handles input
        elif self.state == STATE_LEADERBOARD:
            # Tabs switch the active board without dismissing the screen.
            # Checked before the cooldown gate so a tab is tappable the
            # instant the board opens; taps anywhere else fall through to
            # the dismiss logic below. Keyboard (pos is None) dismisses.
            if pos is not None:
                tcur = getattr(self.hud, "_lb_tab_current_rect", None)
                tleg = getattr(self.hud, "_lb_tab_legacy_rect", None)
                if tcur is not None and tcur.collidepoint(pos):
                    self._lb_selected_tab = 0
                    return
                if tleg is not None and tleg.collidepoint(pos):
                    if self._lb_selected_tab != 1:
                        self._lb_selected_tab = 1
                        self._kick_legacy_fetch()
                    return
            if self._cooldown_t <= 0:
                # Branch on the run-summary intent so the player lands
                # where they chose on the stats screen after they've
                # dismissed the leaderboard celebration.
                if self._post_leaderboard == "play":
                    self._restart()
                else:
                    self.state = STATE_MENU
                # Keep the menu visible for a beat instead of letting the
                # next event in the same tap (FINGERDOWN / MOUSEBUTTONDOWN
                # echoes, or a fast double-click) skip straight into play.
                self._cooldown_t = 0.4

    def _toggle_pause(self):
        if self.state == STATE_PLAY:
            self.state = STATE_PAUSE
        elif self.state == STATE_PAUSE:
            self.state = STATE_PLAY

    # ── achievements screen ───────────────────────────────────────────────────
    def _open_achievements(self):
        from game.achievements_screen import AchievementsScene
        self.achievements = AchievementsScene()
        self.state = STATE_ACHIEVEMENTS
        self._cooldown_t = 0.25

    def _close_achievements(self):
        self.achievements = None
        self.state = STATE_MENU
        self._cooldown_t = 0.25

    # ── profile (wardrobe + achievements, shared chrome) ────────────────────
    def _open_profile(self):
        from game.profile_screen import ProfileScene
        self.profile = ProfileScene()
        self.state = STATE_PROFILE
        self._cooldown_t = 0.25

    def _close_profile(self):
        self.profile = None
        self.state = STATE_MENU
        self._cooldown_t = 0.25

    # ── coin store ────────────────────────────────────────────────────────────
    def _open_store(self):
        from game.store import StoreScene
        self.store = StoreScene()
        self.state = STATE_STORE
        self._cooldown_t = 0.25

    def _close_store(self):
        self.store = None
        self.state = STATE_MENU
        self._cooldown_t = 0.25

    # ── settings screen ───────────────────────────────────────────────────────
    def _open_settings(self):
        from game.settings_screen import SettingsScene
        self.settings = SettingsScene()
        self.state = STATE_SETTINGS
        self._cooldown_t = 0.25

    def _close_settings(self):
        self.settings = None
        self.state = STATE_MENU
        self._cooldown_t = 0.25

    def _toggle_sound(self):
        """Sound Effects row → flip the device-local SFX mute + apply it live."""
        from game import prefs
        new_muted = not prefs.get_muted()
        prefs.set_muted(new_muted)
        audio.set_muted(new_muted)
        self._cooldown_t = 0.25

    def _open_about(self):
        from game.about_screen import AboutScene
        self.about = AboutScene()
        self.state = STATE_ABOUT
        self._cooldown_t = 0.25

    def _close_about(self):
        self.about = None
        if self.settings is None:      # defensive: Settings is normally still alive
            from game.settings_screen import SettingsScene
            self.settings = SettingsScene()
        self.state = STATE_SETTINGS
        self._cooldown_t = 0.25

    def _open_howto_from_settings(self):
        """How to Play row → the intro cinematic, returning to Settings after."""
        from game.intro import IntroScene
        self.intro = IntroScene()
        self._intro_return_state = STATE_SETTINGS
        self.state = STATE_INTRO
        self._cooldown_t = 0.25

    def _open_powerups_from_settings(self):
        """Power-Ups row → the explainer, returning to Settings after."""
        from game.powerup_help import PowerUpHelpScene
        self.powerup_help = PowerUpHelpScene()
        self._powerups_return_state = STATE_SETTINGS
        self.state = STATE_POWERUPS
        self._cooldown_t = 0.25

    def _handle_store_event(self, e):
        """Pointer/key routing for the store. The scene owns horizontal swipe
        state so category pages can be swiped; a near-stationary release is a
        tap that is forwarded to handle_tap (gated by cooldown)."""
        sc = self.store
        if sc is None:
            self.state = STATE_MENU
            return
        if e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_ESCAPE, pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                if self._cooldown_t <= 0:
                    if sc.handle_tap(None) == "back":
                        self._close_store()
                    else:
                        self._cooldown_t = 0.25
            return
        if e.type == pygame.MOUSEBUTTONDOWN:
            sc.pointer_down(e.pos)
        elif e.type == pygame.MOUSEMOTION:
            if e.buttons[0]:
                sc.pointer_move(e.pos)
        elif e.type == pygame.MOUSEBUTTONUP:
            if sc.pointer_up() and self._cooldown_t <= 0:
                if sc.handle_tap(e.pos) == "back":
                    self._close_store()
                else:
                    self._cooldown_t = 0.25
        elif e.type == pygame.FINGERDOWN:
            sc.pointer_down((int(e.x * W), int(e.y * H)))
        elif e.type == pygame.FINGERMOTION:
            sc.pointer_move((int(e.x * W), int(e.y * H)))
        elif e.type == pygame.FINGERUP:
            if sc.pointer_up() and self._cooldown_t <= 0:
                if sc.handle_tap((int(e.x * W), int(e.y * H))) == "back":
                    self._close_store()
                else:
                    self._cooldown_t = 0.25

    def _handle_achievements_event(self, e):
        """Pointer/wheel/key routing for the scrollable achievements list. The
        scene owns scroll + drag state; a near-stationary release is a tap that
        dismisses back to the menu (gated by the entry cooldown so the opening
        tap's echo can't bounce straight back out)."""
        sc = self.achievements
        if sc is None:
            self.state = STATE_MENU
            return
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE or self._cooldown_t <= 0:
                self._close_achievements()
            return
        if e.type == pygame.MOUSEWHEEL:
            sc.scroll_by(-e.y * sc.WHEEL_STEP)
        elif e.type == pygame.MOUSEBUTTONDOWN:
            sc.pointer_down(e.pos[1])
        elif e.type == pygame.MOUSEMOTION:
            if e.buttons[0]:
                sc.pointer_move(e.pos[1])
        elif e.type == pygame.MOUSEBUTTONUP:
            if sc.pointer_up():
                self._achv_tap_or_close(sc, e.pos)
        elif e.type == pygame.FINGERDOWN:
            sc.pointer_down(int(e.y * H))
        elif e.type == pygame.FINGERMOTION:
            sc.pointer_move(int(e.y * H))
        elif e.type == pygame.FINGERUP:
            if sc.pointer_up():
                self._achv_tap_or_close(sc, (int(e.x * W), int(e.y * H)))

    def _achv_tap_or_close(self, sc, pos):
        """A stationary tap on the HALL OF FAME / HALL OF SHAME tabs switches the
        active wall; the MENU button dismisses. Taps elsewhere (e.g. on a row) do
        nothing, so the list feels solid — only the button or ESC exits."""
        tf = getattr(sc, "tab_fame_rect", None)
        ts = getattr(sc, "tab_shame_rect", None)
        mb = getattr(sc, "menu_btn_rect", None)
        if tf and tf.collidepoint(pos):
            sc.set_tab("fame")
            return
        if ts and ts.collidepoint(pos):
            sc.set_tab("shame")
            return
        if mb and mb.collidepoint(pos) and self._cooldown_t <= 0:
            self._close_achievements()

    def _handle_profile_event(self, e):
        """Pointer/wheel/key routing for the PROFILE screen (WARDROBE +
        ACHIEVEMENTS tabs). Full (x, y) is threaded through — unlike the
        achievements-only handler above, WARDROBE's item grid needs the x
        coordinate too, not just vertical scroll."""
        sc = self.profile
        if sc is None:
            self.state = STATE_MENU
            return
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE or self._cooldown_t <= 0:
                self._close_profile()
            return
        if e.type == pygame.MOUSEWHEEL:
            sc.scroll_by(-e.y * 56)
        elif e.type == pygame.MOUSEBUTTONDOWN:
            sc.pointer_down(e.pos)
        elif e.type == pygame.MOUSEMOTION:
            if e.buttons[0]:
                sc.pointer_move(e.pos)
        elif e.type == pygame.MOUSEBUTTONUP:
            if sc.pointer_up():
                self._profile_tap_or_close(sc, e.pos)
        elif e.type == pygame.FINGERDOWN:
            sc.pointer_down((int(e.x * W), int(e.y * H)))
        elif e.type == pygame.FINGERMOTION:
            sc.pointer_move((int(e.x * W), int(e.y * H)))
        elif e.type == pygame.FINGERUP:
            if sc.pointer_up():
                self._profile_tap_or_close(sc, (int(e.x * W), int(e.y * H)))

    def _profile_tap_or_close(self, sc, pos):
        """A stationary tap resolves through ProfileScene's own dispatch
        (view-pill, then the active tab's own controls); the MENU button
        dismisses (gated by the entry cooldown, same as every other
        owner-scene dismiss)."""
        result = sc.tap_or_close(pos)
        if result == "close" and self._cooldown_t <= 0:
            self._close_profile()

    # ── achievement-earned screen (end of run) ────────────────────────────────
    def _continue_from_achv_earned(self):
        """Tap on the ACHIEVEMENT EARNED! screen → hand off to the run summary,
        restarting its reveal timer so the summary animates in fresh."""
        self.achv_earned = None
        self.state = STATE_STATS
        self._stats_t = 0.0
        self._cooldown_t = 0.25

    def _handle_achv_earned_event(self, e):
        """Pointer/wheel/key routing for the scrollable earned screen. The scene
        owns scroll + drag; a near-stationary release is a tap that continues to
        the run summary (gated by the entry cooldown so the death tap's echo
        can't skip it instantly)."""
        sc = self.achv_earned
        if sc is None:
            self.state = STATE_STATS
            return
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE or self._cooldown_t <= 0:
                self._continue_from_achv_earned()
            return
        if e.type == pygame.MOUSEWHEEL:
            sc.scroll_by(-e.y * sc.WHEEL_STEP)
        elif e.type == pygame.MOUSEBUTTONDOWN:
            sc.pointer_down(e.pos[1])
        elif e.type == pygame.MOUSEMOTION:
            if e.buttons[0]:
                sc.pointer_move(e.pos[1])
        elif e.type == pygame.MOUSEBUTTONUP:
            if sc.pointer_up() and self._cooldown_t <= 0:
                self._continue_from_achv_earned()
        elif e.type == pygame.FINGERDOWN:
            sc.pointer_down(int(e.y * H))
        elif e.type == pygame.FINGERMOTION:
            sc.pointer_move(int(e.y * H))
        elif e.type == pygame.FINGERUP:
            if sc.pointer_up() and self._cooldown_t <= 0:
                self._continue_from_achv_earned()

    def _pick_cloud_variant(self):
        """Pick the single cloud design used by every cloud for the whole run,
        chosen at random. Called once per run so each run has one consistent
        cloud style that varies between runs (re-rolling per frame would
        flicker)."""
        self._cloud_variant = random.randrange(cloud_variants.VARIANT_COUNT)

    def _sync_bird_cosmetics(self):
        """Apply the coin-store loadout (equipped skin + parcel) to this run's
        bird so purchases/equips made in the store show up in gameplay."""
        from game import store_data
        b = self.world.bird
        b.equipped_skin = store_data.equipped("skin") or "skin_base"
        b.equipped_parcel = store_data.equipped("parcel") or "parcel_base"
        b.rebuild_skin_combos()

    def _start_play(self):
        # On the event-test branch the demo is the ONLY mode — every run
        # start (menu, restart) replays it, so route through it here.
        if self._warren_demo:
            self._start_warren_demo()
            return
        # The menu IS the start-of-game screen, so the click that brought
        # us here counts as the first flap — drop the ready_t freeze and
        # apply an initial flap so Pip launches immediately. The gameplay
        # opener (post-house drifting off-screen-left) still plays for
        # the first ~2.5 s of bg_scroll.
        self.world = World()
        self._sync_bird_cosmetics()
        self.world.ready_t = 0.0
        self.world.flap()
        self._pick_cloud_variant()
        self.state = STATE_PLAY

    def _start_warren_demo(self):
        """Launch the scripted Warren demo. If the controller can't be built
        (e.g. tools/ unavailable), disable the flag and fall back to a normal
        run permanently, so a run never gets bricked by the prototype (and the
        _start_play delegation above can't recurse)."""
        try:
            from game.warren_demo import WarrenDemo
            demo = WarrenDemo()
        except Exception:
            self._warren_demo = False
            self._start_play()
            return
        self.world = World(demo=demo)
        self.world.ready_t = 0.0
        self.world.flap()
        self.intro = None
        self._pick_cloud_variant()
        self.state = STATE_PLAY

    def _finish_intro(self, skipped: bool):
        """Hand off out of the intro. The next state depends on `skipped`:

          * `skipped=True`  — the player tapped during the cinematic. They
            wanted to bail past the intro flow, so we drop them straight
            on the menu, bypassing the power-ups explainer.
          * `skipped=False` — the cinematic ran to its natural end. Land
            on the power-ups explainer, which stays up until the player
            taps once more to reach the menu.

        Sets a brief cooldown so the same physical tap that triggered the
        skip can't echo into the now-MENU state and immediately call
        ``_start_play`` or open one of the secondary menu buttons. 0.25 s
        is enough to swallow:
          - SDL FINGERDOWN → MOUSEBUTTONDOWN echo (~tens of ms)
          - a duplicate FINGERDOWN that flaky touch firmware can emit
          - a fast follow-up tap that would otherwise cascade

        and short enough that a deliberate first tap from a settled
        menu (well past typical 200–300 ms reaction time) still feels
        instant.

        Mirror of the STATE_LEADERBOARD → MENU pattern in ``_flap_input``."""
        if self.intro is not None:
            self.intro.skip()
        self.intro = None
        if self._intro_return_state is not None:
            # Opened from a sub-screen (e.g. Settings' How to Play) — return
            # there whether the cinematic was skipped or watched through.
            self.state = self._intro_return_state
            self._intro_return_state = None
        elif self._intro_from_menu:
            # HOW TO PLAY replay always returns to MENU regardless of
            # whether the player tapped to skip or watched it through.
            self.state = STATE_MENU
            self._intro_from_menu = False
        elif skipped:
            self.state = STATE_MENU
        else:
            from game.powerup_help import PowerUpHelpScene
            self.powerup_help = PowerUpHelpScene()
            self.state = STATE_POWERUPS
        self._cooldown_t = 0.25

    def _restart(self):
        # Event-test branch: a restart replays the demo, not a normal run.
        if self._warren_demo:
            self._start_warren_demo()
            return
        # Same contract as `_start_play`: the tap that triggered the
        # restart counts as the first flap, no ready freeze.
        self.world = World()
        self._sync_bird_cosmetics()
        self.world.ready_t = 0.0
        self.world.flap()
        self._pick_cloud_variant()
        self.state = STATE_PLAY

    # ── run loop ────────────────────────────────────────────────────────────

    def run(self):
        # Sync entry point for native execution. Browser builds (pygbag) must
        # call async_run() directly so the page's event loop stays alive.
        import asyncio
        asyncio.run(self.async_run())

    async def async_run(self):
        import asyncio
        import sys as _sys
        self._cooldown_t = 0.0
        self._resume_grace_t = 0.0
        self._start_name_entry = False
        first_frame_done = False
        while self._running:
            dt = min(self.clock.tick(FPS) / 1000.0, 1 / 20.0)
            for e in pygame.event.get():
                self._handle_event(e)
            self._update(dt)
            self._render()
            pygame.display.flip()
            if not first_frame_done:
                first_frame_done = True
                # Splash overlay is about to start fading — let the
                # intro clock start ticking from here. See
                # `self._splash_covering` for the rationale.
                self._splash_covering = False
                # The boot kick (inject_theme.fireSyntheticGesture) retries
                # every 250 ms until it sees skybitGameReady. We just set
                # that flag, but events fired in the last retry interval
                # may still be sitting in the pygame queue. Set a short
                # cooldown so those trailing synthetic taps can't skip the
                # intro the instant the splash lifts.
                self._cooldown_t = max(self._cooldown_t, 0.4)
                # Signal to the JS overlay (inject_theme.py's dismiss()
                # waits on this) that the canvas now has a real Skybit
                # frame on it. Without this, the overlay would fade off
                # while pygbag's bare progress display was still visible
                # underneath -- the "separate screen" the user reported
                # between Skybit splash and the rendered intro.
                if _sys.platform == "emscripten":
                    try:
                        import js  # type: ignore
                        js.window.skybitGameReady = True
                    except Exception:
                        pass
            if self._start_name_entry:
                self._start_name_entry = False
                # create_task keeps the game loop running every frame while the
                # network coroutine makes progress between asyncio.sleep(0) yields.
                # Store strong ref so GC doesn't silently kill the task mid-flight.
                self._name_task = asyncio.create_task(self._on_name_submitted())
            # Yield to the browser's event loop each frame. On native runs
            # this is a zero-cost no-op between ticks.
            await asyncio.sleep(0)
        pygame.quit()

    def _handle_event(self, e):
        if e.type == pygame.QUIT:
            self._running = False
            return
        # Note when a real finger event arrives so we can suppress the
        # synthetic mouse follow-up that SDL fires for the same tap.
        now = pygame.time.get_ticks() / 1000.0
        if e.type == pygame.FINGERDOWN:
            self._last_finger_t = now
        elif e.type == pygame.MOUSEBUTTONDOWN:
            if now - self._last_finger_t < self._finger_dedup_window:
                return  # this MOUSEBUTTONDOWN is a touch echo — ignore
        # The store fully owns pointer + key input while open (swipe/tap/dismiss).
        if self.state == STATE_STORE:
            self._handle_store_event(e)
            return
        # The achievements list fully owns pointer + wheel + key input while
        # open (scroll/drag/dismiss), so route every event there and stop.
        if self.state == STATE_ACHIEVEMENTS:
            self._handle_achievements_event(e)
            return
        # PROFILE (wardrobe + achievements) likewise fully owns pointer +
        # wheel + key input while open.
        if self.state == STATE_PROFILE:
            self._handle_profile_event(e)
            return
        # The end-of-run earned screen likewise owns all pointer/wheel/key input
        # (scroll/drag/continue) while it's up.
        if self.state == STATE_ACHV_EARNED:
            self._handle_achv_earned_event(e)
            return
        import sys as _sys
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_p:
                self._toggle_pause()
                return
            # Debug hotkey: F9 force-triggers the cycle-finale rush so the
            # treasure-box animation can be iterated on without sitting
            # through a full 5-minute biome cycle. Also bumps
            # cycles_completed so the "DAY N COMPLETE!" banner reads
            # the next day each press AND so the scaling +100*day chest
            # reward can be playtested across multiple days from F9
            # alone. Mirrors the DEBUG_GENIE_PILLAR one-shot in config —
            # local-only.
            if e.key == pygame.K_F9 and self.state == STATE_PLAY:
                from game.config import CYCLE_FINALE_RUSH_PILLARS
                self.world._finale_rush_remaining = CYCLE_FINALE_RUSH_PILLARS
                self.world._finale_box_dropped = False
                self.world.cycles_completed += 1
                return
            if e.key == pygame.K_ESCAPE:
                if self.state in (STATE_PLAY, STATE_PAUSE):
                    self._toggle_pause()
                else:
                    self._running = False
                return
            # Native name-entry keyboard: intercept before flap routing.
            # ENTER submits; ESC no longer skips — there's a clickable
            # SKIP button now.
            if self.state == STATE_NAMEENTRY and _sys.platform != "emscripten":
                if e.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    self._submit_name_native(self._name_input_buf.strip())
                elif e.key == pygame.K_BACKSPACE:
                    self._name_input_buf = self._name_input_buf[:-1]
                elif e.unicode and e.unicode.isprintable() and len(self._name_input_buf) < 16:
                    self._name_input_buf += e.unicode
                return
            if e.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                self._flap_input()
        elif e.type == pygame.MOUSEBUTTONDOWN:
            if self._handle_name_entry_click(e.pos):
                return
            self._flap_input(e.pos)
        elif e.type == pygame.FINGERDOWN:
            pos = (int(e.x * W), int(e.y * H))
            if self._handle_name_entry_click(pos):
                return
            self._flap_input(pos)

    def _handle_name_entry_click(self, pos) -> bool:
        """If we're on the native name-entry screen and the click hit the
        SUBMIT or SKIP button, dispatch and return True. Returns False
        otherwise so normal flap routing can proceed."""
        import sys as _sys
        if self.state != STATE_NAMEENTRY or _sys.platform == "emscripten":
            return False
        if self.hud.name_submit_rect.collidepoint(pos):
            if self._name_input_buf.strip():
                self._submit_name_native(self._name_input_buf.strip())
            return True
        if self.hud.name_skip_rect.collidepoint(pos):
            self._submit_name_native("")
            return True
        return False

    # ── update ──────────────────────────────────────────────────────────────

    def _update(self, dt):
        self._cloud_phase += dt
        # Drain one prewarm task per frame after the splash has lifted, so
        # the GROW + KFC caches fill incrementally during the intro
        # rather than blocking startup. Each task takes 7-55 ms.
        if self._prewarm_queue and not self._splash_covering:
            _, task = self._prewarm_queue.pop(0)
            task()
        if self.state == STATE_INTRO:
            if self.intro is None:
                # Defensive: should never happen, but recover gracefully.
                self._finish_intro(skipped=True)
                return
            # Hold the intro at t=0 while the HTML splash is still
            # painting over the canvas — async_run flips this flag the
            # moment the first visible frame fires. Without the gate
            # the cinematic fast-forwards past the dawn beat during
            # pygbag's boot.
            if not self._splash_covering:
                self.intro.update(dt)
            # Tick the cooldown so a HOW-TO-PLAY-launched intro becomes
            # skippable a beat after it opens (see the gate in
            # _flap_input's STATE_INTRO branch).
            self._cooldown_t = max(0.0, self._cooldown_t - dt)
            if self.intro.done:
                # The cinematic ran out — show the power-ups explainer.
                # (User-initiated skips already routed through _flap_input.)
                self._finish_intro(skipped=False)
            return
        if self.state == STATE_POWERUPS:
            if self.powerup_help is not None:
                self.powerup_help.update(dt)
            self._cooldown_t = max(0.0, self._cooldown_t - dt)
            return
        if self.state == STATE_ACHIEVEMENTS:
            if self.achievements is not None:
                self.achievements.update(dt)
            self._cooldown_t = max(0.0, self._cooldown_t - dt)
            return
        if self.state == STATE_PROFILE:
            if self.profile is not None:
                self.profile.update(dt)
            self._cooldown_t = max(0.0, self._cooldown_t - dt)
            return
        if self.state == STATE_SETTINGS:
            if self.settings is not None:
                self.settings.update(dt)
            self._cooldown_t = max(0.0, self._cooldown_t - dt)
            return
        if self.state == STATE_ABOUT:
            if self.about is not None:
                self.about.update(dt)
            self._cooldown_t = max(0.0, self._cooldown_t - dt)
            return
        if self.state == STATE_STORE:
            if self.store is not None:
                self.store.update(dt)
            self._cooldown_t = max(0.0, self._cooldown_t - dt)
            return
        if self.state == STATE_ACHV_EARNED:
            if self.achv_earned is not None:
                self.achv_earned.update(dt)
            self._cooldown_t = max(0.0, self._cooldown_t - dt)
            return
        if self.state == STATE_MENU:
            self.world.world_idle_tick(dt)
            self._cooldown_t = max(0.0, self._cooldown_t - dt)
            # Are You Still There? — five minutes idling on the menu.
            self._menu_idle_t += dt
            if not self._menu_idle_fired and self._menu_idle_t >= 300.0:
                self._menu_idle_fired = True
                from game import achievements as _ach
                _ach.unlock("are_you_still_there")
        elif self.state == STATE_PLAY:
            self._resume_grace_t = max(0.0, self._resume_grace_t - dt)
            self.world.update(dt)
            if self.world.game_over:
                self._on_death()
        elif self.state == STATE_PAUSE:
            # World is frozen. Still tick the HUD pulse so the overlay animates.
            self.hud.title_t += dt
        elif self.state == STATE_STATS:
            self.world.update(dt)  # let particles/weather keep going behind
            self._stats_t += dt
            # No auto-advance — the screen stays until the player taps
            # (handled in _flap_input).
        elif self.state == STATE_NAMEENTRY:
            self.world.update(dt)  # keep world alive behind JS overlay
        elif self.state == STATE_LEADERBOARD:
            self._cooldown_t = max(0.0, self._cooldown_t - dt)

    def _on_death(self):
        score = self.world.score
        self._new_best = score > self.session_best
        if self._new_best:
            self.session_best = score
        # Fire-and-forget telemetry: send the run summary to Supabase
        # (browser-only; native is a silent no-op). Strong ref on
        # self prevents GC from killing the task mid-flight.
        import asyncio as _asyncio
        # The branch-only demo never writes telemetry / the DB.
        if getattr(self.world, "demo", None) is None:
            try:
                self._play_log_task = _asyncio.create_task(play_log.log_run(self.world))
            except RuntimeError:
                # No running loop (e.g. headless smoke tests) — skip silently.
                pass
        # Evaluate achievements once against the finished run (never for the
        # scripted demo). Any newly-unlocked ids get a full-screen
        # "ACHIEVEMENT EARNED!" card screen (scrollable) before the run summary.
        newly = []
        if getattr(self.world, "demo", None) is None:
            try:
                from game import achievements
                newly = achievements.evaluate_run(self.world)
            except Exception:
                newly = []
        self._stats_t = 0.0
        if newly:
            from game.achievement_earned import AchievementEarnedScene
            self.achv_earned = AchievementEarnedScene(newly)
            audio.play_achievement()
            self.state = STATE_ACHV_EARNED
            self._cooldown_t = 0.35       # so the death tap's echo can't skip it
        else:
            # Game-over screen no longer plays its own jingle — death.ogg
            # at the moment of impact carries the whole "run ended" cue.
            self.state = STATE_STATS
        # Reset the run-summary intent so a freshly opened stats
        # screen defaults to "main menu" until the player explicitly
        # taps PLAY AGAIN.
        self._post_leaderboard = "menu"

    def _advance_past_stats(self):
        """Tap on run-summary: if the score qualifies for top 10, the
        player flows into name entry and then the leaderboard view
        (so they see where their name landed). Otherwise we route
        straight back to the main menu — the leaderboard is still
        one tap away from there via the TOP 10 trophy."""
        import sys
        # Event-test branch: the demo is the only mode — any stats-screen tap
        # starts a fresh demo run, skipping the name-entry / leaderboard detour.
        if self._warren_demo:
            self.hud.title_t = 0.0
            self._start_warren_demo()
            self._cooldown_t = 0.25
            return
        self._final_score = self.world.score
        self._name_input_buf = ""
        if sys.platform == "emscripten":
            # Browser: kick off async fetch; _on_name_submitted decides
            # qualifies → NAMEENTRY → LEADERBOARD vs back to MENU.
            self._lb_scores = []
            self._lb_player_rank = -1
            self._fetch_pending = True
            self._start_name_entry = True
        else:
            # Native: top-10 lives in local JSON, fetch is sync.
            from game import leaderboard
            scores = leaderboard._native_fetch()
            if self._qualifies_for_top10(scores, self._final_score):
                self.state = STATE_NAMEENTRY
            else:
                # Non-qualifying: honour the player's stats-screen
                # choice. PLAY AGAIN starts a new run immediately;
                # MAIN MENU lands them on the menu (legacy default).
                self.hud.title_t = 0.0
                if self._post_leaderboard == "play":
                    self._restart()
                else:
                    self.state = STATE_MENU
                self._cooldown_t = 0.25

    @staticmethod
    def _qualifies_for_top10(scores, score) -> bool:
        if score <= 0:
            return False
        if len(scores) < 10:
            return True
        return score > scores[-1]["score"]

    def _reset_lb_tabs(self):
        """Clear tabbed-leaderboard state so each open lands on CURRENT and
        re-pulls the (still-live) legacy board on demand. Cancels any legacy
        fetch left in flight from a previous open so it can't write back to
        the next session's state."""
        if self._legacy_task is not None:
            try:
                self._legacy_task.cancel()
            except Exception:
                pass
            self._legacy_task = None
        self._lb_selected_tab = 0
        self._legacy_loaded = False
        self._legacy_loading = False
        self._lb_legacy_scores = []
        self._lb_legacy_fetch_error = ""

    def _kick_legacy_fetch(self):
        """Load the read-only LEGACY board the first time its tab is opened.
        Native has no previous-version source, so it resolves to an empty
        board; browser kicks an async read against the legacy table. Only one
        fetch runs at a time (the JS bridge has a single result slot), which
        the open sequence already guarantees — the current-board fetch is
        finished before the screen is interactive."""
        if self._legacy_loaded:
            return
        self._legacy_loaded = True
        import sys
        if sys.platform != "emscripten":
            self._lb_legacy_scores = []
            self._lb_legacy_fetch_error = ""
            return
        import asyncio
        try:
            self._legacy_task = asyncio.create_task(self._fetch_legacy())
            self._legacy_loading = True
        except RuntimeError:
            # No running event loop (smoke tests) — allow a later retry.
            self._legacy_loaded = False

    async def _fetch_legacy(self):
        try:
            from game import leaderboard
            scores = await leaderboard.fetch_top10(board="legacy")
            self._lb_legacy_scores = scores
            self._lb_legacy_fetch_error = leaderboard.last_fetch_error()
        except Exception:
            pass
        finally:
            self._legacy_loading = False

    def _open_leaderboard_from_menu(self):
        """Tap on the TOP 10 trophy panel in the main menu. Browser:
        kick off an async Supabase fetch but stay on the menu — the
        async task switches state to STATE_LEADERBOARD once the scores
        are in hand, so the player never sees a 'Loading top 10…'
        flash. Native: synchronous local fetch.

        No player highlight (``_lb_player_rank = -1``) because there's
        no just-finished run to rank. The same STATE_LEADERBOARD → MENU
        tap pattern that lives in ``_flap_input`` handles the way back."""
        import sys
        self._lb_player_rank = -1
        self._reset_lb_tabs()
        if sys.platform == "emscripten":
            if self._fetch_pending:
                # An earlier tap is still in flight — ignore re-taps
                # so we don't spawn parallel fetch tasks.
                return
            self._lb_scores = []
            self._lb_fetch_error = ""
            self._fetch_pending = True
            import asyncio
            try:
                self._lb_task = asyncio.create_task(
                    self._fetch_leaderboard_from_menu())
            except RuntimeError:
                # No running event loop (smoke tests). Skip the fetch;
                # the player stays on the menu.
                self._fetch_pending = False
        else:
            from game import leaderboard
            scores = leaderboard._native_fetch()
            self._show_leaderboard_native(scores, submitted=False)

    async def _fetch_leaderboard_from_menu(self):
        """Background task for the menu trophy button. Fetches Supabase
        top-10, stores it on the scene, then switches to
        STATE_LEADERBOARD — keeping the player on the menu until the
        scores are ready avoids the transient 'Loading…' screen."""
        try:
            from game import leaderboard
            scores = await leaderboard.fetch_top10()
            self._lb_scores = scores
            self._lb_fetch_error = leaderboard.last_fetch_error()
        except Exception:
            pass
        self._fetch_pending = False
        self.hud.title_t = 0.0
        self.state = STATE_LEADERBOARD
        self._cooldown_t = 0.25

    def _show_leaderboard_native(self, scores, submitted: bool):
        self._reset_lb_tabs()
        self._lb_scores = scores
        if scores and submitted:
            self._lb_player_rank = next(
                (i for i, e in enumerate(scores) if e["score"] == self._final_score),
                -1,
            )
        else:
            self._lb_player_rank = -1
        self.hud.title_t = 0.0
        self.state = STATE_LEADERBOARD
        self._cooldown_t = 0.25

    def _submit_name_native(self, name: str):
        """Finish native name-entry: save to local JSON, show leaderboard."""
        from game import leaderboard
        if name:
            leaderboard._native_submit(name, self._final_score)
        scores = leaderboard._native_fetch()
        self._show_leaderboard_native(scores, submitted=bool(name))

    async def _on_name_submitted(self):
        """Browser path triggered from _advance_past_stats. Fetches the
        current top 10, then branches on qualification: qualifiers go
        through name entry and land on the leaderboard so they can see
        where their name placed; non-qualifiers go straight back to
        the main menu instead of being parked on the leaderboard."""
        self._reset_lb_tabs()
        qualified = False
        try:
            from game import leaderboard
            scores = await leaderboard.fetch_top10()
            self._lb_fetch_error = leaderboard.last_fetch_error()
            if self._qualifies_for_top10(scores, self._final_score):
                qualified = True
                # Flip to NAMEENTRY so the Python-side render and the
                # JS overlay come up together — non-qualifiers must
                # never see a name-entry flash for the duration of
                # the fetch.
                self.state = STATE_NAMEENTRY
                name = await leaderboard.open_name_entry()
                if name:
                    await leaderboard.submit(name, self.world)
                    scores = await leaderboard.fetch_top10()
                    self._lb_fetch_error = leaderboard.last_fetch_error()
                    self._lb_player_rank = next(
                        (i for i, e in enumerate(scores) if e["score"] == self._final_score),
                        -1,
                    )
                else:
                    self._lb_player_rank = -1
            else:
                self._lb_player_rank = -1
            self._lb_scores = scores
        except Exception:
            pass
        self._fetch_pending = False
        self.hud.title_t = 0.0
        if qualified:
            self.state = STATE_LEADERBOARD
            self._cooldown_t = 0.25
        else:
            # Non-qualifying browser path: honour the player's stats
            # button choice. PLAY AGAIN bypasses the menu entirely.
            if self._post_leaderboard == "play":
                self._restart()
            else:
                self.state = STATE_MENU
            self._cooldown_t = 0.25

    # ── render ──────────────────────────────────────────────────────────────

    def _draw_background(self, surf):
        phase = self.world.biome_phase
        palette = self.world.biome_palette

        # An active sky design (game/sky_designs.py) paints its own per-phase sky
        # here, with the same two-bucket fade; only when none is active do we bake
        # the live shan-shui sky below. Either way flow continues to the mountains
        # and foreground, which stay on the live biome palette.
        if not sky_designs.render_active(surf, W, H, GROUND_Y, palette, phase):
            # The sky gradient is cached per phase bucket (see biome.PHASE_BUCKETS).
            # Blending the current bucket with the next one, weighted by how far
            # into the bucket we are, turns the otherwise ~10-second snap into a
            # continuous fade.
            buckets = _biome.PHASE_BUCKETS
            bucket_f = (phase % 1.0) * buckets
            a = int(bucket_f) % buckets
            b = (a + 1) % buckets
            t = bucket_f - int(bucket_f)

            pal_a = _biome.palette_for_phase(a / buckets)
            pal_b = _biome.palette_for_phase(b / buckets)
            sky_a = get_sky_surface_biome(W, H, GROUND_Y, pal_a, a)
            sky_b = get_sky_surface_biome(W, H, GROUND_Y, pal_b, b)

            sky_a.set_alpha(None)
            surf.blit(sky_a, (0, 0))
            if t > 0:
                sky_b.set_alpha(int(t * 255))
                surf.blit(sky_b, (0, 0))
                sky_b.set_alpha(None)

        # Clouds retint to the active sky design's palette so they match the sky;
        # falls back to the live palette when no design is active.
        cloud_pal = sky_designs.active_cloud_palette(phase, palette) or palette
        scroll = self.world.bg_scroll
        for i, (bx, by, sc) in enumerate(_CLOUD_SLOTS):
            ox = ((bx - scroll * (0.04 + 0.02 * i)) % (W + 160)) - 80
            draw_cloud(surf, ox,
                       by + math.sin(self._cloud_phase * 0.3 + i) * 3,
                       sc, variant=self._cloud_variant, palette=cloud_pal)
        if self.world.kfc_timer > 0 and self.world.kfc_mountain_layers:
            # Pre-rendered fries pile per parallax layer - blit cheaply
            # at the offset since activation so the pile drifts at the
            # same depth-cued speeds as the normal mountains.
            from game.fries_mountains import blit_fries_mountains
            scroll_offset = scroll - self.world.kfc_activation_scroll
            blit_fries_mountains(surf, self.world.kfc_mountain_layers,
                                  scroll_offset)
        else:
            draw_mountains(surf, scroll, GROUND_Y, W,
                           phase=self.world.biome_phase)
        # Ambient scenes (V-flocks, fireworks) sit between mountains and the
        # ground band so they read as "out there in the world" — behind
        # gameplay entities (pipes, coins, bird) but in front of terrain.
        self.world.ambient.draw(surf)
        # The buff sandstone sidewalk IS the play floor now (replaces the grass
        # meadow); promenade props + living cast ride on top of it.
        foreground.draw_foreground_floor(surf, scroll, palette, phase)
        # The sidewalk reacts to weather: rain glazes it + pools puddles, the snow
        # squall frosts it. Drawn on the paving UNDER the crowd's feet (the falling
        # rain + its splashes are an in-front layer in weather.draw later).
        foreground.draw_ground_weather(surf, scroll, palette,
                                       self.world.weather.wetness,
                                       self.world.weather.snow_cover)
        foreground.draw_promenade(surf, scroll, palette,
                                  self.world.biome_phase, self.world.biome_time)
        # NOTE: the NEAR/front lane is intentionally NOT drawn here. It is painted
        # later in _render, AFTER the gameplay pillars, so the front-lane plants +
        # people (feet lower on screen) occlude the pillar bases.

    def _render(self):
        # Intro renders its own self-contained scene (sky + pillars + cottage
        # + parrot etc.) and bypasses the in-game world draw entirely.
        if self.state == STATE_INTRO and self.intro is not None:
            self.intro.render(self.screen)
            return
        # Power-ups explainer also paints its own background — no world.
        if self.state == STATE_POWERUPS and self.powerup_help is not None:
            self.powerup_help.render(self.screen)
            return
        # Achievements list paints its own night background + scrolling list.
        if self.state == STATE_ACHIEVEMENTS and self.achievements is not None:
            from game import achievements as _ach
            self.achievements.render(self.screen, 1 / 60, _ach.load())
            return
        # PROFILE paints its own night background + WARDROBE/ACHIEVEMENTS content.
        if self.state == STATE_PROFILE and self.profile is not None:
            self.profile.render(self.screen)
            return
        # End-of-run earned screen paints its own full-screen night + card stack.
        if self.state == STATE_ACHV_EARNED and self.achv_earned is not None:
            self.achv_earned.render(self.screen, 1 / 60)
            return
        # Settings screen paints its own night background + launcher rows.
        if self.state == STATE_SETTINGS and self.settings is not None:
            self.settings.render(self.screen, 1 / 60)
            return
        # About screen paints its own night background.
        if self.state == STATE_ABOUT and self.about is not None:
            self.about.render(self.screen, 1 / 60)
            return
        # Coin store paints its own lagoon hub / category grids.
        if self.state == STATE_STORE and self.store is not None:
            self.store.render(self.screen)
            return
        sx, sy = self.world.shake_offset() if self.state == STATE_PLAY else (0, 0)
        sx, sy = int(sx), int(sy)
        self._draw_background(self.screen)

        # Menu scene = the gameplay opener as a static frame: pickup post-
        # house on the left with Pip standing in front of it holding the
        # parcel. No pillars or world entities until the user taps to start.
        if self.state == STATE_MENU:
            # No pillars in the menu, so the near lane just rides on the floor here
            # (depth-vs-pillar is moot); draw it so the street backdrop matches play.
            foreground.draw_near_lane(self.screen, self.world.bg_scroll,
                                      self.world.biome_palette,
                                      self.world.biome_phase, self.world.biome_time)
            house = _intro.get_sprite("skyhouse_post")
            hx = int(W * 0.30) - house.get_width() // 2
            hy = int(H * 0.42) - house.get_height() // 2
            self.screen.blit(house, (hx, hy))
            self.world.bird.draw(self.screen, sx, sy)
            self.hud.draw_menu(self.screen, 1 / 60, self.best)
            return

        # Cycle-finale ground marker ("{N} Day" gold bar) sits ON the
        # grass band, BEHIND pillars + bird so foreground elements
        # naturally overlap it. Drawn before pipes so the bird's
        # shadow + pillars layer on top.
        for gm in getattr(self.world, "celebration_ground_markers", ()):
            gm.draw(self.screen, sx, sy)
        # Cheering crowd flanks the marker on both sides; same layer
        # so the parrots stand on the grass behind Pip.
        for cc in getattr(self.world, "celebration_crowds", ()):
            cc.draw(self.screen, sx, sy)
        # Cycle-finale balloon cluster — sky-layer decor in the open gap.
        # Drawn before pipes so the (real) flanking pillars appear in
        # front of the balloons; in the phantom gap there are no pillars
        # so the balloons read as floating in open sky.
        for bc in getattr(self.world, "celebration_balloon_clusters", ()):
            bc.draw(self.screen, sx, sy)

        # Demo clown + floating die — behind the pillars (the route occludes
        # the strolling clown), mirroring the celebration-crowd layer above.
        if getattr(self.world, "demo", None) is not None:
            self.world.demo.draw_world(self.screen, self.world, sx, sy)
        # Inline clown event (live gameplay) uses the same behind-pillars layer.
        if getattr(self.world, "clown_event", None) is not None:
            self.world.clown_event.draw_world(self.screen, self.world, sx, sy)

        pipe_palette = self.world.biome_palette
        kfc_active = self.world.bird.kfc_active
        pipe_phase = self.world.biome_phase
        for p in self.world.pipes:
            p.draw(self.screen, pipe_palette, kfc_visual=kfc_active,
                   phase=pipe_phase)
        # (The demo roll-celebration popup is drawn LATER, after the HUD, so it
        # overlays the score counter — see the STATE_PLAY block below.)
        # SKATEBOARD ramps: wooden wedges perched on lower-pillar
        # crowns. Drawn AFTER pipes so the wedge overpaints the crown
        # vegetation; below the bird so Pip rides on top.
        for r in self.world.ramps:
            r.draw(self.screen)

        # Morning-thermal ground rocks sit on the terrain behind the vents —
        # the event's slow buildup/fade scatter. Drawn before geysers so a
        # vent cone overlaps any rock right at its base.
        for r in self.world.rocks:
            r.draw(self.screen)

        # Morning-thermal geysers: sinter-cone vents + flowing steam columns.
        # Drawn after pillars / before weather so the column reads as
        # foreground atmosphere sitting behind the coins + bird.
        for gy in self.world.geysers:
            gy.draw(self.screen)

        # NEAR/front sidewalk lane — drawn HERE (after the pillars + play-field
        # props) so the closest foreground plants/people occlude the pillar bases,
        # matching their depth (feet lower on screen = nearer the camera). Still
        # behind weather/coins/bird, so rain falls in front of them and Pip stays
        # on top.
        foreground.draw_near_lane(self.screen, self.world.bg_scroll,
                                  self.world.biome_palette,
                                  self.world.biome_phase, self.world.biome_time)

        # Weather sits between pillars and collectibles so rain/fog passes
        # behind the coins + bird — same layer a real foreground has.
        self.world.weather.draw(self.screen)

        # Lightning bolt — ABOVE weather (on top of rain streaks) but BELOW
        # coins/bird so Pip stays on top of the impact. Decays via
        # lightning_strike["life"] in World.update.
        _draw_lightning_bolt(self.screen, self.world.lightning_strike)

        triple_active = self.world.triple_timer > 0
        for c in self.world.coins:
            c.draw(self.screen, kfc_active=kfc_active,
                   triple_active=triple_active)
        for m in self.world.powerups:
            m.draw(self.screen)

        # Cycle-finale celebration festoon — world-space catenary +
        # bulbs hung between the two pillars flanking the open chest.
        # Drawn after the pillars / coins / powerups so it visibly
        # hangs IN FRONT of the pillar caps, and BEFORE the bird so
        # Pip flies past it as foreground.
        for cg in getattr(self.world, "celebration_garlands", ()):
            cg.draw(self.screen, sx, sy)
        # Bunting hangs above the garland — drawn after so it sits in
        # front of the festoon string in z-order; both ride world scroll.
        for cb in getattr(self.world, "celebration_buntings", ()):
            cb.draw(self.screen, sx, sy)

        # Gameplay opener: pickup post-house drifting off-screen-left + the
        # parcel tucked under Pip. Active only during STATE_PLAY's first
        # ~2.5 s, mirroring the intro's beat-2 closing image.
        if self.state == STATE_PLAY:
            _draw_opener(self.screen, self.world)

        # RAIL: track polyline + cart. The parked cart (no Pip) draws whole
        # under the bird. On the locked ride the cart is split around Pip —
        # wheels under him, bucket body over him — so he sits INSIDE it.
        if getattr(self.world, "rail_pipes", None):
            _draw_rails(self.screen, self.world.rail_pipes)
        cart_pipe = getattr(self.world, "rail_cart_pipe", None)
        locked = self.world.bird.cart_locked
        if cart_pipe is not None and not locked:
            _draw_parked_cart(self.screen, cart_pipe)
        if locked:
            _draw_cart_on_bird(self.screen, self.world, sx, sy, layer="wheels")

        self.world.bird.draw(self.screen, sx, sy,
                             flipped=self.world.reverse_timer > 0)

        if locked:
            _draw_cart_on_bird(self.screen, self.world, sx, sy, layer="body")

        for p in self.world.particles:
            p.draw(self.screen)
        # NOTE: genie_actors are NOT drawn here. The conjurer must read as the
        # front-most graphic, so it is re-blitted AFTER the HUD below (the
        # score panel + power-up bars would otherwise paint over it).

        # SKATEBOARD activation overlays: the deck-banner caption is
        # composited inside `hud.draw_play` (on top of coin/pause chrome,
        # under the live halftone score), so only the activation starburst
        # is handled here. The burst surface is currently set to None on
        # activation — the guard below short-circuits.
        if getattr(self.world, "skateboard_burst_t", 0) > 0 and \
                self.world.skateboard_burst_surface is not None:
            t = self.world.skateboard_burst_t
            FADE = 0.8
            if t > FADE:
                alpha = 255
            else:
                x = 1.0 - t / FADE
                alpha = int(255 * (1.0 - x) ** 2)
            burst = self.world.skateboard_burst_surface
            burst.set_alpha(alpha)
            bcx = self.world.skateboard_burst_cx + sx
            bcy = self.world.skateboard_burst_cy + sy
            self.screen.blit(
                burst, burst.get_rect(center=(bcx, bcy)))

        # Slow-mo: subtle violet tint overlay so the player feels the effect
        # even without looking at the HUD.
        if self.world.slowmo_timer > 0:
            _SCENE_TINT.fill((140, 70, 210, 28))
            self.screen.blit(_SCENE_TINT, (0, 0))

        # KFC mode: warm amber tint
        if self.world.kfc_timer > 0:
            _SCENE_TINT.fill((210, 120, 10, 20))
            self.screen.blit(_SCENE_TINT, (0, 0))

        # Ghost mode: cool blue-white screen tint. The ring around the bird
        # was removed — the SPECTRAL parrot palette + breathing-fade alpha
        # already carry the ghost read.
        if self.world.ghost_timer > 0:
            _SCENE_TINT.fill((140, 180, 255, 18))
            self.screen.blit(_SCENE_TINT, (0, 0))

        # LOTTERY reveal: top-left slot-machine cabinet shows the
        # roll for ~2.2 s. Drawn ON TOP of the world tints so the
        # tier label stays legible.
        if getattr(self.world, "lottery_anim", None) is not None:
            _draw_lottery_reveal(self.screen, self.world.lottery_anim)

        # Magnet force-field — Solar Gold palette: warm amber-gold rings
        # + golden glow + sci-fi hex-grid shield, with a coherent
        # dramatic breath. The rings + glow pulse; the hex grid is
        # static (cached at module load via `_magnet_hex_grid`) so we
        # blit the prebuilt overlay each frame instead of redrawing
        # ~225 polygons. Pulse rate 5.5 ⇒ ~1.14 s cycle.
        if self.world.magnet_timer > 0 or self.world.megamagnet_timer > 0:
            from game.config import MAGNET_RADIUS, MEGAMAGNET_RADIUS
            import math as _math
            t_pulse = self._cloud_phase * 5.5
            # Megamagnet renders the same field at 2x radius. The hex
            # grid cache builds a second entry for the larger size on
            # first activation; rings + glow scale by `rad` naturally.
            rad = (MEGAMAGNET_RADIUS if self.world.megamagnet_timer > 0
                   else MAGNET_RADIUS)
            field = _magnet_field_surf(rad * 2 + 8)
            field.fill((0, 0, 0, 0))
            lcx, lcy = rad + 4, rad + 4

            # Outer-ring pulse factor — drives BOTH the rings and the glow
            BREATH = 0.30
            s_outer = _math.sin(t_pulse + 0.0)
            u_outer = (s_outer + 1) / 2
            outer_factor = 1.0 - BREATH * (1.0 - u_outer)
            glow_rad = rad * outer_factor

            # Inner radial glow — bell-curve falloff peaking near the
            # outer edge, gold colour, scaled by the same pulse.
            GLOW_COL = (245, 175, 40)
            for i in range(18, 0, -1):
                r = int(glow_rad * i / 18)
                inner_t = i / 18
                bell = _math.exp(-((inner_t - 0.85) ** 2) / 0.15)
                a = int(72 * bell)
                if a > 0:
                    pygame.draw.circle(field, (*GLOW_COL, a),
                                       (lcx, lcy), r)

            # Hex-grid overlay — sits on top of the warm glow, under
            # the rings, so the rings remain the brightest read. The
            # cached grid is rendered at full radius once; each frame
            # we smoothscale it down to (rad * outer_factor) so the
            # hex breathes in lockstep with the outer ring instead of
            # sitting statically at full size while everything else
            # pulses. SRCALPHA is preserved through smoothscale.
            hex_full = _magnet_hex_grid(rad)
            scaled_d = int(rad * outer_factor) * 2 + 8
            full_d = int(rad) * 2 + 8
            if scaled_d != full_d:
                hex_layer = _magnet_hex_scaled(rad, scaled_d)
                offset = (full_d - scaled_d) // 2
                field.blit(hex_layer, (offset, offset))
            else:
                field.blit(hex_full, (0, 0))

            # 3 rings with per-ring gold tints, slightly out of phase.
            AA_COL = (255, 240, 180)
            for rfac, phase, alpha, width, breath_scale, ring_col in (
                    (1.00, 0.0,  180, 3, 1.00, (255, 220, 100)),
                    (0.78, 0.6,  140, 2, 0.85, (255, 195,  60)),
                    (0.55, 1.2,  100, 2, 0.70, (235, 165,  35))):
                amp = BREATH * breath_scale
                s = _math.sin(t_pulse + phase)
                u = (s + 1) / 2
                rr = int(rad * rfac * (1.0 - amp * (1.0 - u)))
                # Anti-alias ring with two ⅓-alpha satellites + main pass
                pygame.draw.circle(field, (*AA_COL, alpha // 3),
                                   (lcx, lcy), rr + 1, width)
                pygame.draw.circle(field, (*AA_COL, alpha // 3),
                                   (lcx, lcy), rr - 1, width)
                pygame.draw.circle(field, (*ring_col, alpha),
                                   (lcx, lcy), rr, width)

            self.screen.blit(field,
                             (int(self.world.bird.x) + sx - lcx,
                              int(self.world.bird.y) + sy - lcy))

        if self.world.hit_flash > 0:
            t = self.world.hit_flash / 0.35
            _SCENE_TINT.fill((*UI_RED, int(120 * t)))
            self.screen.blit(_SCENE_TINT, (0, 0))

        if self.state == STATE_MENU:
            self.hud.draw_menu(self.screen, 1 / 60, self.best)
        elif self.state == STATE_PLAY:
            self.hud.draw_play(self.screen, self.world, self.best)
            # The demo roll-celebration popup draws AFTER the HUD so it overlays
            # the score counter (the score no longer pokes through the banner).
            demo = getattr(self.world, "demo", None)
            if demo is not None:
                demo.draw_sign(self.screen, self.world, 0, 0)
                # While the banner is up, re-draw Pip ON TOP of it so the parrot
                # flies in front of the banner (which still overlays the score).
                if getattr(demo, "die_pop_t", 0) > 0:
                    self.world.bird.draw(self.screen, sx, sy,
                                         flipped=self.world.reverse_timer > 0)
            # Inline clown event reveal banner — same after-HUD overlay + Pip-
            # on-top redraw so the parrot flies in front of the banner.
            ce = getattr(self.world, "clown_event", None)
            if ce is not None:
                ce.draw_sign(self.screen, self.world, 0, 0)
                if getattr(ce, "die_pop_t", 0) > 0:
                    self.world.bird.draw(self.screen, sx, sy,
                                         flipped=self.world.reverse_timer > 0)
        elif self.state == STATE_PAUSE:
            self.hud.draw_play(self.screen, self.world, self.best, paused=True)
            self.hud.draw_pause_overlay(self.screen, score=self.world.score)
        elif self.state == STATE_STATS:
            self.hud.draw_stats(self.screen, self.world, 1 / 60, self._stats_t,
                                best=self.best, new_best=self._new_best,
                                show_prompt=not self._fetch_pending)
        elif self.state == STATE_NAMEENTRY:
            import sys as _sys
            if _sys.platform != "emscripten":
                self.hud.draw_name_entry(self.screen, 1 / 60, self._name_input_buf)
        elif self.state == STATE_LEADERBOARD:
            self.hud.draw_leaderboard(
                self.screen, 1 / 60,
                self._lb_scores, self._lb_player_rank,
                self._cooldown_t,
                fetch_error=self._lb_fetch_error,
                legacy_scores=self._lb_legacy_scores,
                legacy_fetch_error=self._lb_legacy_fetch_error,
                selected_tab=self._lb_selected_tab,
                legacy_loading=self._legacy_loading,
            )

        # SKATEBOARD: re-blit Pip + the board on top of HUD overlays so
        # the caption banner / pop-art score / trick bubbles can never
        # cover him. Only fires while the buff is active during play /
        # pause; other states skip.
        if (self.state in (STATE_PLAY, STATE_PAUSE)
                and self.world.bird.skateboard_active):
            self.world.bird.draw(self.screen, sx, sy,
                                 flipped=self.world.reverse_timer > 0)

        # GENIE: the conjurer is the front-most actor — re-blit it on top of
        # everything (HUD score panel + power-up progress bars, screen tints)
        # so nothing ever covers it. PLAY only; the pause / stats / leaderboard
        # screens keep their modal chrome on top.
        if self.state == STATE_PLAY:
            for g in self.world.genie_actors:
                g.draw(self.screen)
