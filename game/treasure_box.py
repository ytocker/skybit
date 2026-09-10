"""W4 treasure-box pickup sprite + open-lid variant for the cycle-
finale reward animation.

Extracted from `tools/render_treasure_box_grandiose_options.py` (round
3, cell W4 — walnut + brass + 5-pointed brass star). The runtime module
needs to live under `game/` because the WASM bundle only stages
`main.py`, `inject_theme.py`, `pyproject.toml`, and `game/` per the
deploy-hygiene rule in CLAUDE.md.

Two sprites, cached at module scope:

  closed  — the normal in-air pickup icon (walnut chest with the brass
            star lock plate centred on the seam).
  open    — drawn for ~0.6 s after pickup: lid lifted off the body,
            warm gold-glow interior visible in the gap, brass lock
            plate stays bolted to the body so the brass star reads
            above the spilled light.
"""
from __future__ import annotations

import math

import pygame


# ── Footprint + supersample ─────────────────────────────────────────────────
PICKUP_W = 100
PICKUP_H = 82
SS = 7

# ── Palette (verbatim copies of the design-tool constants) ──────────────────
INK   = (22, 18, 34)
CREAM = (250, 244, 222)

WALNUT_HI    = (154, 98, 56)
WALNUT_MID   = (124, 74, 40)
WALNUT_LO    = (78, 42, 20)
WALNUT_GRAIN = (52, 26, 10)

BRASS_HI  = (236, 204, 132)
BRASS_MID = (202, 164, 84)
BRASS_LO  = (140, 108, 44)
BRASS_INK = (90, 62, 18)

GOLD_INK = (110, 72, 10)

# Gold-coin palette (for the spilling coin pile in the open variant).
GOLD_HI  = (255, 232, 124)
GOLD_MID = (240, 196,  72)
GOLD_LO  = (188, 138,  28)

# Starburst rays — alternating cream / saturated gold / cream so the
# fan radiating behind the open chest carries a clear three-tone
# "jackpot" pop instead of a flat yellow halo.
STAR_CREAM = (252, 244, 218)
STAR_GOLD  = (252, 200,  88)
STAR_SUN_HI = (255, 250, 220)         # core glow centre
STAR_SUN_LO = (252, 196,  88)         # core glow rim

# Lid grain ticks reuse the design tool's neutral wood-grain ink so the
# walnut top has the same dark ladder of cross-strokes the docs sheet
# shows.
LID_GRAIN = (72, 40, 18)


def _lerp(a, b, t):
    return (int(a[0] + (b[0] - a[0]) * t),
            int(a[1] + (b[1] - a[1]) * t),
            int(a[2] + (b[2] - a[2]) * t))


def _vgrad_rect(surf, rect, top_col, bot_col, radius=0):
    tmp = pygame.Surface(rect.size, pygame.SRCALPHA)
    h_ = rect.height
    for y in range(h_):
        t = y / max(1, h_ - 1)
        pygame.draw.line(tmp, _lerp(top_col, bot_col, t),
                         (0, y), (rect.width, y))
    if radius:
        mask = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255),
                         mask.get_rect(), border_radius=radius)
        tmp.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(tmp, rect.topleft)


def _chest_body(big, rect, ink_w, top_col, mid_col, lo_col, radius=None):
    if radius is None:
        radius = max(2, int(rect.width * 0.06))
    _vgrad_rect(big, rect, top_col, mid_col, radius=radius)
    foot = pygame.Rect(rect.left, rect.top + int(rect.height * 0.62),
                       rect.width, int(rect.height * 0.40))
    _vgrad_rect(big, foot, mid_col, lo_col, radius=radius)
    pygame.draw.rect(big, INK, rect, ink_w, border_radius=radius)


def _curved_lid(big, lid_rect, ink_w, top_col, mid_col, lo_col,
                grain=True, sheen=True):
    arc_h = int(lid_rect.height * 0.65)
    cx = lid_rect.centerx
    pts = []
    n = 18
    top_y = lid_rect.top - arc_h
    half_w = lid_rect.width // 2
    for i in range(n + 1):
        t = i / n
        ang = math.pi * (1 - t)
        ax = cx + math.cos(ang) * half_w
        ay = lid_rect.top - math.sin(ang) * arc_h
        pts.append((ax, ay))
    pts.append((lid_rect.right, lid_rect.bottom))
    pts.append((lid_rect.left, lid_rect.bottom))
    pygame.draw.polygon(big, mid_col, pts)
    grad_rect = pygame.Rect(lid_rect.left, top_y,
                            lid_rect.width, lid_rect.bottom - top_y)
    grad = pygame.Surface(grad_rect.size, pygame.SRCALPHA)
    for y in range(grad_rect.height):
        t = y / max(1, grad_rect.height - 1)
        pygame.draw.line(grad, _lerp(top_col, lo_col, t),
                         (0, y), (grad_rect.width, y))
    mask = pygame.Surface(grad_rect.size, pygame.SRCALPHA)
    local_pts = [(p[0] - grad_rect.left, p[1] - grad_rect.top) for p in pts]
    pygame.draw.polygon(mask, (255, 255, 255, 255), local_pts)
    grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(grad, grad_rect.topleft)
    if sheen:
        sh = pygame.Surface((lid_rect.width, arc_h * 2), pygame.SRCALPHA)
        pygame.draw.ellipse(sh, (255, 248, 222, 90),
                            (int(lid_rect.width * 0.18),
                             int(arc_h * 0.20),
                             int(lid_rect.width * 0.42),
                             int(arc_h * 0.45)))
        big.blit(sh, (lid_rect.left, top_y))
    if grain:
        for frac in (0.30, 0.55, 0.78):
            y = top_y + int(arc_h * 2 * frac)
            dy = (lid_rect.top - y) / max(1, arc_h)
            dy = max(-1.0, min(1.0, dy))
            hx = int(half_w * math.sqrt(max(0.0, 1.0 - dy * dy)))
            pygame.draw.line(big, LID_GRAIN,
                             (cx - hx + ink_w * 2, y),
                             (cx + hx - ink_w * 2, y),
                             max(1, ink_w // 2))
    pygame.draw.polygon(big, INK, pts, ink_w)
    return pts, top_y


def _new_big():
    return pygame.Surface((PICKUP_W * SS, PICKUP_H * SS), pygame.SRCALPHA)


def _common_layout():
    px_w = PICKUP_W * SS
    px_h = PICKUP_H * SS
    margin_x = int(px_w * 0.08)
    body_top = int(px_h * 0.38)
    body_bot = int(px_h * 0.92)
    lid_top  = int(px_h * 0.20)
    body = pygame.Rect(margin_x, body_top,
                       px_w - 2 * margin_x, body_bot - body_top)
    lid  = pygame.Rect(margin_x, lid_top,
                       px_w - 2 * margin_x, body_top - lid_top)
    return body, lid


def _brass_bands_and_grain(big, body, ink):
    bw = int(body.width * 0.10)
    band_h = body.height - int(body.height * 0.20)
    left_band = pygame.Rect(body.left + int(body.width * 0.08),
                            body.top + int(body.height * 0.10),
                            bw, band_h)
    right_band = pygame.Rect(body.right - int(body.width * 0.08) - bw,
                             body.top + int(body.height * 0.10),
                             bw, band_h)
    for r in (left_band, right_band):
        _vgrad_rect(big, r, BRASS_HI, BRASS_LO, radius=max(1, ink))
        pygame.draw.rect(big, BRASS_INK, r, ink, border_radius=max(1, ink))
        rivet_r = max(2, int(r.height * 0.06))
        for ry in (r.top + r.height // 12, r.bottom - r.height // 12):
            cx = r.centerx
            pygame.draw.circle(big, BRASS_HI, (cx, ry), rivet_r)
            pygame.draw.circle(big, BRASS_INK, (cx, ry), rivet_r,
                               max(1, ink // 2))
    for i in range(1, 4):
        gy = body.top + int(body.height * (i / 4))
        x0 = body.left + int(body.width * 0.10)
        x1 = body.right - int(body.width * 0.10)
        pygame.draw.line(big, WALNUT_GRAIN, (x0, gy), (x1, gy),
                         max(1, ink // 2))


def _lid_strap(big, lid, ink):
    strap_y = lid.top + int(lid.height * 0.10)
    pygame.draw.line(big, BRASS_MID,
                     (lid.left + int(lid.width * 0.04), strap_y),
                     (lid.right - int(lid.width * 0.04), strap_y),
                     max(3, ink))
    pygame.draw.line(big, BRASS_INK,
                     (lid.left + int(lid.width * 0.04), strap_y),
                     (lid.right - int(lid.width * 0.04), strap_y),
                     max(1, ink // 2))


def _brass_star(b, cx, cy, ink_w):
    r_out = max(4, int(SS * 2.6))
    r_in  = max(2, int(r_out * 0.42))
    pts = []
    for k in range(10):
        ang = -math.pi / 2 + k * (math.pi / 5)
        rr = r_out if k % 2 == 0 else r_in
        pts.append((cx + math.cos(ang) * rr,
                    cy + math.sin(ang) * rr))
    pygame.draw.polygon(b, BRASS_HI, pts)
    pygame.draw.polygon(b, BRASS_INK, pts, max(1, ink_w // 2))


def _brass_lock_plate(big, body, ink, with_clasp=True):
    lock_w = int(body.width * 0.30)
    lock_h = int(body.height * 0.55)
    lock_cx = body.centerx
    lock_cy = body.top + lock_h // 2 - int(body.height * 0.08)
    lock = pygame.Rect(0, 0, lock_w, lock_h)
    lock.center = (lock_cx, lock_cy)
    _vgrad_rect(big, lock, BRASS_HI, BRASS_LO, radius=max(2, lock_w // 8))
    pygame.draw.rect(big, BRASS_INK, lock, ink,
                     border_radius=max(2, lock_w // 8))
    _brass_star(big, lock_cx, lock_cy, ink)
    if with_clasp:
        clasp = pygame.Rect(0, 0, int(lock_w * 0.35), int(lock_h * 0.45))
        clasp.midbottom = (lock_cx, body.top + int(lock_h * 0.18))
        _vgrad_rect(big, clasp, BRASS_HI, BRASS_LO,
                    radius=max(2, clasp.width // 6))
        pygame.draw.rect(big, BRASS_INK, clasp, max(1, ink // 2),
                         border_radius=max(2, clasp.width // 6))


def _apply_unifiers(big, body, lid):
    arc_h = int(lid.height * 0.65)
    cx = lid.centerx
    half_w = lid.width // 2
    pts = []
    n = 24
    for i in range(n + 1):
        t = i / n
        ang = math.pi * (1 - t)
        ax = cx + math.cos(ang) * (half_w - max(1, SS // 3))
        ay = lid.top - math.sin(ang) * (arc_h - max(1, SS // 3))
        pts.append((ax, ay))
    if len(pts) >= 2:
        pygame.draw.lines(big, (255, 226, 158), False, pts,
                          max(1, SS // 3))
    L = max(2, int(SS * 0.9))
    for (px, py) in (
        (body.left  + int(body.width * 0.10), body.top  + int(body.height * 0.10)),
        (body.right - int(body.width * 0.10), body.top  + int(body.height * 0.10)),
        (body.left  + int(body.width * 0.10), body.bottom - int(body.height * 0.18)),
        (body.right - int(body.width * 0.10), body.bottom - int(body.height * 0.18)),
    ):
        pygame.draw.circle(big, CREAM, (px, py), max(1, L // 2))
        pygame.draw.line(big, CREAM, (px - L, py), (px + L, py),
                         max(1, SS // 3))
        pygame.draw.line(big, CREAM, (px, py - L), (px, py + L),
                         max(1, SS // 3))


def _smoothscale(big):
    return pygame.transform.smoothscale(big, (PICKUP_W, PICKUP_H))


# ── Builders ────────────────────────────────────────────────────────────────


def _build_closed() -> pygame.Surface:
    big = _new_big()
    ink = max(3, int(SS * 1.05))
    body, lid = _common_layout()

    _chest_body(big, body, ink, WALNUT_HI, WALNUT_MID, WALNUT_LO)
    _brass_bands_and_grain(big, body, ink)
    _curved_lid(big, lid, ink, WALNUT_HI, WALNUT_MID, WALNUT_LO,
                grain=True, sheen=True)
    _lid_strap(big, lid, ink)
    _brass_lock_plate(big, body, ink)
    _apply_unifiers(big, body, lid)
    return _smoothscale(big)


def _build_open() -> pygame.Surface:
    """Open chest, B2 'overflowing gold' recipe in W4 walnut + brass.

    Half-open lid rotated 28 deg back on a rear hinge; dark interior
    void inside the body so the gold pile reads against a shadow; 3
    coins behind the front lip, 5 coins spilling over the lip (breaking
    the silhouette so the spill reads as motion), 1 larger coin
    floating above the open lid. Drawn at SS, smoothscaled to footprint.

    The starburst halo sits BEHIND this sprite at draw time — it lives
    on its own cached surface so it can rotate independently with the
    animation timer (see draw_open_sprite)."""
    big = _new_big()
    ink = max(3, int(SS * 1.05))
    body, lid = _common_layout()

    # Body — same walnut as the closed sprite so it still reads as W4.
    _chest_body(big, body, ink, WALNUT_HI, WALNUT_MID, WALNUT_LO)
    _brass_bands_and_grain(big, body, ink)

    # Inside-of-box dark void so the spilled coins read against shadow.
    inner = pygame.Rect(body.left + int(body.width * 0.10),
                        body.top + int(body.height * 0.04),
                        body.width - int(body.width * 0.20),
                        int(body.height * 0.40))
    _vgrad_rect(big, inner, (32, 22, 14), (12, 8, 4),
                radius=max(2, inner.width // 16))
    pygame.draw.rect(big, INK, inner,
                     max(1, ink // 2),
                     border_radius=max(2, inner.width // 16))

    # Half-open curved lid rotated ~28 deg back. Hinged at the back-top
    # of the body (mirrors icon_b2's pattern from the design tool).
    lid_w = lid.width
    lid_h = int(lid.height * 1.6)
    lid_surf = pygame.Surface((lid_w + 8, lid_h + 8), pygame.SRCALPHA)
    local_lid = pygame.Rect(4, lid_h - lid.height, lid_w, lid.height)
    _curved_lid(lid_surf, local_lid, ink,
                WALNUT_HI, WALNUT_MID, WALNUT_LO,
                grain=True, sheen=True)
    _lid_strap(lid_surf, local_lid, ink)
    rot = pygame.transform.rotate(lid_surf, 28)
    hinge = (body.left + int(lid.width * 0.18),
             body.top - int(lid.height * 0.10))
    big.blit(rot, rot.get_rect(midbottom=hinge))

    # Coin pile — pile_cy / coin_r0 match the B2 design recipe so the
    # spacing and overlap stay battle-tested. Round 4 promoted the pile
    # from 9 to 22 coins so the cycle-finale chest reads as a HOARD,
    # not a handful: back-row + lateral-spill + deep-pile + 3 sky-drifters.
    pile_cy = body.top + int(body.height * 0.55)
    coin_r0 = int(body.height * 0.18)

    # Back-row coins inside the box (3, partially behind the front lip).
    for (ox, oy, rs) in ((-0.28, -0.20, 1.0),
                         ( 0.08, -0.26, 1.0),
                         ( 0.32, -0.10, 0.9)):
        _gold_coin(big,
                   body.centerx + int(body.width * ox),
                   pile_cy + int(body.height * oy),
                   max(3, int(coin_r0 * rs)),
                   ink)

    # Deep-pile coins — 4 stacked higher behind the front lip so the
    # pile reads with depth, not as one flat row.
    for (ox, oy, rs) in ((-0.18, -0.42, 0.95),
                         ( 0.18, -0.40, 1.00),
                         (-0.04, -0.34, 0.90),
                         ( 0.24, -0.28, 0.85)):
        _gold_coin(big,
                   body.centerx + int(body.width * ox),
                   pile_cy + int(body.height * oy),
                   max(3, int(coin_r0 * rs)),
                   ink)

    # Front-spill coins (5) breaking the body's front edge silhouette.
    for (ox, oy, rs) in ((-0.36,  0.18, 1.05),
                         (-0.10,  0.30, 1.10),
                         ( 0.18,  0.32, 1.00),
                         ( 0.40,  0.20, 0.95),
                         (-0.22,  0.40, 0.90)):
        _gold_coin(big,
                   body.centerx + int(body.width * ox),
                   pile_cy + int(body.height * oy),
                   max(3, int(coin_r0 * rs)),
                   ink)

    # Lateral-spill coins — 4 cascading off the left and right edges
    # so the pour reads as omnidirectional, not just forward.
    for (ox, oy, rs) in ((-0.58,  0.04, 0.90),
                         (-0.50, -0.10, 0.80),
                         ( 0.56,  0.06, 0.85),
                         ( 0.48, -0.12, 0.80)):
        _gold_coin(big,
                   body.centerx + int(body.width * ox),
                   pile_cy + int(body.height * oy),
                   max(3, int(coin_r0 * rs)),
                   ink)

    # One bigger coin leaping out above the open lid — captures the
    # "GOLD IS ERUPTING" beat at a focal point above the body.
    _gold_coin(big,
               body.centerx + int(body.width * 0.12),
               pile_cy + int(body.height * -0.92),
               max(4, int(coin_r0 * 1.10)),
               ink)

    # 3 small "drifter" coins floating in the air above the open lid —
    # a tiny constellation sized down so they read as airborne, not
    # crowding the larger leaping coin.
    for (ox, oy, rs) in ((-0.32, -0.72, 0.55),
                         ( 0.40, -0.78, 0.55),
                         ( 0.02, -1.18, 0.55)):
        _gold_coin(big,
                   body.centerx + int(body.width * ox),
                   pile_cy + int(body.height * oy),
                   max(3, int(coin_r0 * rs)),
                   ink)

    return _smoothscale(big)


def _gold_coin(big, cx, cy, r, ink_w, glyph=True):
    """Stylised gold coin — concentric gradient + rim + $-glyph chord.
    Verbatim copy of the design tool helper (tools/render_treasure_box_
    options.py:268). Used by the open variant's spilling-coin pile."""
    pygame.draw.circle(big, GOLD_LO, (cx, cy + max(1, r // 6)), r)
    pygame.draw.circle(big, GOLD_HI, (cx, cy), r)
    pygame.draw.circle(big, GOLD_MID, (cx, cy), max(1, int(r * 0.78)))
    pygame.draw.circle(big, GOLD_INK, (cx, cy), r, max(1, ink_w // 2))
    if glyph and r >= 4:
        pygame.draw.line(big, GOLD_INK,
                         (cx - r // 3, cy - r // 3),
                         (cx + r // 3, cy - r // 3),
                         max(1, ink_w // 2))
        pygame.draw.line(big, GOLD_INK,
                         (cx - r // 3, cy + r // 3),
                         (cx + r // 3, cy + r // 3),
                         max(1, ink_w // 2))
        pygame.draw.line(big, GOLD_INK,
                         (cx, cy - r // 2),
                         (cx, cy + r // 2),
                         max(1, ink_w // 2))


# ── Starburst halo ──────────────────────────────────────────────────────────
# Lives on its own cached surface so the draw path can rotate it
# independently of the chest. Sized 1.6x the chest footprint so the
# rays extend ~30% past the chest silhouette on every side at peak.

# Big, grandiose halo — the chest is the reward for completing a full
# biome cycle so the burst is intentionally larger than the chest by
# ~60% on every side. Rays extend ~1.6x the chest's max footprint.
_STARBURST_RADIUS = int(max(PICKUP_W, PICKUP_H) * 1.40)
_STARBURST_SIZE   = _STARBURST_RADIUS * 2


def _build_starburst() -> pygame.Surface:
    """16-ray cream/gold fan + warm sun-disc + 8 tip sparkles. Built at
    SS supersample then smoothscaled. Designed for the cycle-finale
    pickup — once-per-cycle milestone, so the visual is sized + layered
    deliberately to feel like a real celebration:

      * 16 rays alternating LONG cream / SHORT gold so the silhouette
        carries a clear 8-pointed dominant shape with secondary fill.
      * Warm gold sun-disc at the centre (radial gradient via stacked
        concentric circles) so the burst origin reads as a brilliant
        light source, not an empty hub.
      * 8 cream sparkle pearls past the long ray tips so the corona
        keeps reading at the smallest scale + adds a "pixie dust" beat.
    """
    big = pygame.Surface((_STARBURST_SIZE * SS, _STARBURST_SIZE * SS),
                         pygame.SRCALPHA)
    cx = _STARBURST_SIZE * SS // 2
    cy = _STARBURST_SIZE * SS // 2
    r_long  = int(_STARBURST_RADIUS * SS * 0.88)
    r_short = int(r_long * 0.52)
    rays = 16
    long_half_w  = int(r_long * 0.090)
    short_half_w = int(r_long * 0.075)
    for k in range(rays):
        ang = -math.pi / 2 + k * (math.tau / rays)
        long_ray = (k % 2 == 0)
        col = STAR_CREAM if long_ray else STAR_GOLD
        r_tip = r_long if long_ray else r_short
        half_w = long_half_w if long_ray else short_half_w
        tip = (cx + math.cos(ang) * r_tip,
               cy + math.sin(ang) * r_tip)
        base_a = (cx + math.cos(ang + math.pi / 2) * half_w,
                  cy + math.sin(ang + math.pi / 2) * half_w)
        base_b = (cx + math.cos(ang - math.pi / 2) * half_w,
                  cy + math.sin(ang - math.pi / 2) * half_w)
        pygame.draw.polygon(big, col, [tip, base_a, base_b])

    # Center sun-disc — three concentric circles for a radial-glow
    # falloff. Outer mid-gold ring grounds the burst; middle warm
    # gold inner fill carries the body brightness; small cream-white
    # specular pip at the apex sells "this is the LIGHT SOURCE".
    sun_outer = int(r_long * 0.30)
    sun_mid   = int(r_long * 0.20)
    sun_core  = int(r_long * 0.10)
    pygame.draw.circle(big, STAR_GOLD,   (cx, cy), sun_outer)
    pygame.draw.circle(big, STAR_SUN_LO, (cx, cy), sun_mid)
    pygame.draw.circle(big, STAR_SUN_HI, (cx, cy), sun_core)

    # 8 tip sparkles past the long-ray ends — cream pearls + tiny
    # specular highlight. Keeps the corona reading at thumbnail.
    sparkle_r = max(2, int(SS * 1.1))
    sparkle_dist = int(r_long * 1.10)
    for k in range(0, rays, 2):                     # long-ray indices
        ang = -math.pi / 2 + k * (math.tau / rays)
        sx = cx + math.cos(ang) * sparkle_dist
        sy = cy + math.sin(ang) * sparkle_dist
        pygame.draw.circle(big, STAR_CREAM, (sx, sy), sparkle_r)
        pygame.draw.circle(big, (255, 255, 255),
                           (sx - sparkle_r // 3, sy - sparkle_r // 3),
                           max(1, sparkle_r // 2))

    return pygame.transform.smoothscale(
        big, (_STARBURST_SIZE, _STARBURST_SIZE))


# ── Public API ──────────────────────────────────────────────────────────────


_CLOSED_CACHE: "pygame.Surface | None" = None
_OPEN_CACHE: "pygame.Surface | None" = None
_STARBURST_CACHE: "pygame.Surface | None" = None


def _closed_sprite() -> pygame.Surface:
    global _CLOSED_CACHE
    if _CLOSED_CACHE is None:
        _CLOSED_CACHE = _build_closed()
    return _CLOSED_CACHE


def _open_sprite() -> pygame.Surface:
    global _OPEN_CACHE
    if _OPEN_CACHE is None:
        _OPEN_CACHE = _build_open()
    return _OPEN_CACHE


def _starburst_sprite() -> pygame.Surface:
    global _STARBURST_CACHE
    if _STARBURST_CACHE is None:
        _STARBURST_CACHE = _build_starburst()
    return _STARBURST_CACHE


def draw_pickup_icon(surf, cx, cy, pulse):
    """Closed-lid in-air sprite. Gentle sine bob on `pulse`, same idiom
    as the rest of the procedural icon family."""
    icon = _closed_sprite()
    bob = int(round(math.sin(pulse * 1.0) * 2))
    r = icon.get_rect(center=(int(cx), int(cy) + bob))
    surf.blit(icon, r.topleft)


def draw_open_sprite(surf, cx, cy, anim_t, anim_t_max):
    """Open-chest sprite (O3+O4 combined): a slowly-rotating cream/gold
    starburst halo behind the chest, then the half-open lid + spilling
    coin pile on top. Fades 255 → 0 over the post-pickup window.

    anim_t  — seconds remaining on the lid-pop timer (drains to 0).
    anim_t_max — initial timer value (== TREASURE_BOX_ANIM_T)."""
    t = max(0.0, min(1.0, anim_t / anim_t_max)) if anim_t_max > 0 else 0.0
    cx, cy = int(cx), int(cy)
    elapsed = anim_t_max - anim_t

    # Starburst halo — punches in over the first 0.15 s, then fades out
    # over the FIRST half of the window (faster than the chest) so it
    # reads as the "flash of the jackpot" rather than a permanent
    # backdrop. Normal alpha (no BLEND_ADD) keeps the rays from
    # blowing out against bright dawn-sky backdrops. Max alpha capped
    # at 180 so the cream rays never wash out the chest underneath.
    burst = _starburst_sprite()
    burst_window = anim_t_max * 0.70
    if elapsed < burst_window:
        # Slower fade-out tail than v3 so the celebration LINGERS — the
        # cycle-finale chest is the rarest pickup in the game and the
        # corona earns the extra dwell time.
        burst_t = 1.0 - (elapsed / burst_window) ** 1.8
    else:
        burst_t = 0.0
    burst_alpha = max(0, min(225, int(225 * burst_t)))
    if burst_alpha > 0:
        # Punch-in scale envelope: overshoot to 1.15 at ~0.10 s, then
        # settle back to 1.0. Reads as a real "POP!" entrance rather
        # than a static halo.
        if elapsed < 0.10:
            scale = 0.75 + (elapsed / 0.10) * 0.40        # 0.75 -> 1.15
        elif elapsed < 0.22:
            scale = 1.15 - ((elapsed - 0.10) / 0.12) * 0.15  # 1.15 -> 1.00
        else:
            scale = 1.0
        deg = (elapsed * 95.0) % 360.0
        burst_rot = pygame.transform.rotozoom(burst, deg, scale)
        burst_rot.set_alpha(burst_alpha)
        surf.blit(burst_rot, burst_rot.get_rect(center=(cx, cy)))

    # Chest — half-open lid + spilling coin pile, fades over the full
    # window so the loot read survives past the starburst flash.
    chest_alpha = max(0, min(255, int(255 * t)))
    sprite = _open_sprite().copy()
    sprite.set_alpha(chest_alpha)
    surf.blit(sprite, sprite.get_rect(center=(cx, cy)))
