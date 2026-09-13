"""Death-Trap pickup — Round 2 exploration sheet.

Acts on the art-director's per-panel critique of round 1: every concept
is re-drawn with stronger 48-px silhouette + a brighter warning halo so
the rim reads peripherally on dawn-teal. Tombstone is REPLACED by a
rusty buzzsaw — the most mechanically explicit hazard in the set.

WHY this lives in tools/ — design sheet only, no production code is
touched until the loop converges on a winner.

Concepts:
  1. BEAR TRAP   — closed serrated jaw-ring (top-down), armed dot.
  2. BOMB        — round bomb, lit-fuse sparks, soft red rim-glow
                   instead of red bar, sparks flying off the tip.
  3. CURSED GEM  — angular near-black shard, two perpendicular
                   violet cracks at high alpha.
  4. POISON VIAL — green glass, red X painted DIRECTLY on the glass,
                   2-3 vapour puffs above the cork.
  5. BUZZSAW     — rusty serrated blade, red hazard halo, motion arcs.
"""
from __future__ import annotations

import math
import os
import sys

# WHY headless: tool must render in CI / sandbox with no display server.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame


# ── Layout constants ─────────────────────────────────────────────────
PANEL_W, PANEL_H = 360, 240
COLS, ROWS       = 1, 5
TITLE_H          = 56
GUTTER           = 12
SHEET_W          = PANEL_W * COLS + GUTTER * (COLS + 1)
SHEET_H          = TITLE_H + (PANEL_H + GUTTER) * ROWS + GUTTER

DAWN_TEAL        = (38, 44, 66)
INK              = (235, 240, 250)
DIM              = (150, 158, 178)
PANEL_BG         = (24, 28, 42)
GRID             = (54, 62, 86)

NATIVE_PX        = 48
SS               = 5
ZOOM_FACTOR      = 4


# ── Shared palette (kit-matched) ─────────────────────────────────────
BLACK_DOME = (10, 10, 18)
SHADOW     = (4,  4,  10)
RED_HI     = (235, 35, 45)
RED_LO     = (130, 18, 24)
EMBER      = (255, 170, 60)
SPARK      = (255, 240, 200)
PURPLE     = (195, 135, 255)
BRUISE     = (140, 60, 180)        # crack glow — violet not magenta
IRON_DARK  = (52,  56,  72)
IRON_MID   = (90,  96, 112)
IRON_HI    = (175, 184, 200)
RUST       = (180, 90, 40)
RUST_DEEP  = (130, 60, 28)
COPPER     = (200, 110,  55)
SAW_GREY   = (110, 100, 95)
SAW_GREY_HI = (160, 150, 140)
WOOD_DARK  = (60,  38,  22)
WOOD_MID   = (95,  62,  34)
WOOD_HI    = (140,  92,  52)
GREEN_TOX  = (120, 200,  90)
GREEN_LO   = (40,  100,  50)
GREEN_GLASS = (35, 90, 50)
DIRT_LO    = (50,  32,  20)
DIRT_HI    = (110,  78,  46)


# ── Helpers ──────────────────────────────────────────────────────────
def _ss_canvas(w: int, h: int) -> pygame.Surface:
    return pygame.Surface((w * SS, h * SS), pygame.SRCALPHA)


def _resolve(big: pygame.Surface, w: int, h: int) -> pygame.Surface:
    return pygame.transform.smoothscale(big, (w, h))


def _radial_glow(radius: int, color, max_alpha: int = 160) -> pygame.Surface:
    """Soft circular glow — fades from max_alpha at the centre to 0 at
    the rim. Bumped baseline from R1 (~90) to ~160-180 so the warning
    halo survives the dawn-teal background at 48 px."""
    d = radius * 2 + 2
    g = pygame.Surface((d, d), pygame.SRCALPHA)
    cx = d // 2
    for r in range(radius, 0, -1):
        t = r / radius
        a = int(max_alpha * (1 - t) ** 1.6)
        pygame.draw.circle(g, (*color, a), (cx, cx), r)
    return g


def _warning_glow_blit(surf: pygame.Surface, cx: int, cy: int,
                       pulse_phase: float, color=(235, 35, 45),
                       core_alpha: int = 170,
                       core_r: int = 12,
                       halo_r: int = 16) -> None:
    """Two-stop warning halo: a bright core that breathes, plus a
    wider faint outer halo so the rim catches peripheral vision."""
    breath = 0.7 + 0.3 * (0.5 + 0.5 * math.sin(pulse_phase))
    # Outer halo — lower alpha but wider radius (~2-3 px outside the icon)
    outer = _radial_glow(halo_r, color, max_alpha=int(80 * breath))
    surf.blit(outer, (cx - outer.get_width() // 2,
                      cy - outer.get_height() // 2))
    # Inner pulse — brighter
    inner = _radial_glow(core_r, color, max_alpha=int(core_alpha * breath))
    surf.blit(inner, (cx - inner.get_width() // 2,
                      cy - inner.get_height() // 2))


# ── Concept 1 — BEAR TRAP (closed serrated jaw-ring, top-down) ───────
def draw_bear_trap(out_size: int, pulse: float) -> pygame.Surface:
    """Top-down view of a sprung jaw-ring: circular iron disc with a
    visible tooth crown around the rim, central spring/lock plate, dirt
    mound for grounding. Reads as a solid dark disc with a jagged edge
    at 48 px — closed silhouette is far stronger than the open-V."""
    surf = pygame.Surface((out_size, out_size), pygame.SRCALPHA)
    _warning_glow_blit(surf, out_size // 2, out_size // 2 + 2,
                       pulse, color=(220, 70, 40),
                       core_alpha=170, core_r=13, halo_r=18)

    big = _ss_canvas(out_size, out_size)
    cx = out_size * SS // 2
    cy = out_size * SS // 2 + 1 * SS

    # Dirt mound base — wide flat ellipse so the trap reads as sitting
    mound_rect = pygame.Rect(0, 0, 38 * SS, 9 * SS)
    mound_rect.center = (cx, cy + 14 * SS)
    pygame.draw.ellipse(big, (28, 18, 10), mound_rect.inflate(2 * SS, 2 * SS))
    pygame.draw.ellipse(big, DIRT_LO, mound_rect)
    pygame.draw.ellipse(big, DIRT_HI,
                        pygame.Rect(mound_rect.left + 4 * SS,
                                    mound_rect.top + SS,
                                    mound_rect.width - 8 * SS,
                                    2 * SS))

    # Outer jaw-ring — oval so it reads 3/4 top-down (taller flat than tall)
    ring_w = 38 * SS
    ring_h = 30 * SS
    ring_rect = pygame.Rect(0, 0, ring_w, ring_h)
    ring_rect.center = (cx, cy)

    # Shadow under the ring
    pygame.draw.ellipse(big, SHADOW,
                        ring_rect.move(2 * SS, 3 * SS).inflate(2 * SS, 2 * SS))

    # Tooth crown — draw triangular bite teeth around the rim FIRST so
    # the ring's outline overdraws their bases cleanly. 12 teeth.
    n_teeth = 12
    rx = ring_w / 2
    ry = ring_h / 2
    tooth_outer = 1.20    # how far out from the rim the tip pokes
    tooth_inner = 0.92    # where the tooth base sits
    for i in range(n_teeth):
        a0 = (i / n_teeth) * math.tau - math.pi / 2
        a1 = ((i + 0.5) / n_teeth) * math.tau - math.pi / 2
        a2 = ((i + 1) / n_teeth) * math.tau - math.pi / 2
        p0 = (cx + math.cos(a0) * rx * tooth_inner,
              cy + math.sin(a0) * ry * tooth_inner)
        p1 = (cx + math.cos(a1) * rx * tooth_outer,
              cy + math.sin(a1) * ry * tooth_outer)
        p2 = (cx + math.cos(a2) * rx * tooth_inner,
              cy + math.sin(a2) * ry * tooth_inner)
        pygame.draw.polygon(big, IRON_DARK,
                            [(int(p[0]), int(p[1])) for p in (p0, p1, p2)])
        # Highlight the outward edge of upper teeth (catches dawn light)
        if math.sin(a1) < -0.1:
            pygame.draw.line(big, IRON_HI,
                             (int(p0[0]), int(p0[1])),
                             (int(p1[0]), int(p1[1])),
                             max(1, SS // 2 + 1))

    # Iron disc body — dark outer ring, lighter inner face
    pygame.draw.ellipse(big, IRON_DARK, ring_rect)
    pygame.draw.ellipse(big, IRON_MID,
                        ring_rect.inflate(-4 * SS, -4 * SS))
    pygame.draw.ellipse(big, (70, 76, 92),
                        ring_rect.inflate(-8 * SS, -8 * SS))

    # Inner pressure plate — circular dark pan
    pan_rx = 9 * SS
    pan_ry = 7 * SS
    pan_rect = pygame.Rect(0, 0, pan_rx * 2, pan_ry * 2)
    pan_rect.center = (cx, cy + SS)
    pygame.draw.ellipse(big, BLACK_DOME, pan_rect)
    pygame.draw.ellipse(big, IRON_DARK,
                        pan_rect.inflate(-2 * SS, -2 * SS))
    # Spring/lock cross — two crossed bars on the pan
    bar_w = 7 * SS
    bar_h = max(2, SS + 1)
    pygame.draw.rect(big, COPPER,
                     pygame.Rect(cx - bar_w, cy + SS - bar_h // 2,
                                 bar_w * 2, bar_h))
    pygame.draw.rect(big, RUST,
                     pygame.Rect(cx - bar_h // 2, cy + SS - bar_w,
                                 bar_h, bar_w * 2))
    pygame.draw.circle(big, IRON_DARK, (cx, cy + SS), max(2, SS))

    # Top rim catches light — bright arc on top of the ring
    rim_rect = ring_rect.inflate(-SS, -SS)
    pygame.draw.arc(big, IRON_HI, rim_rect,
                    math.radians(200), math.radians(340), max(1, SS))

    # Pulsing red "armed" dot — dead centre, easy to find
    armed_phase = 0.55 + 0.45 * (0.5 + 0.5 * math.sin(pulse * 3.0))
    arm_col = (int(200 + 55 * armed_phase), 30, 30)
    pygame.draw.circle(big, BLACK_DOME, (cx, cy + SS), int(2.4 * SS))
    pygame.draw.circle(big, arm_col, (cx, cy + SS), int(1.6 * SS))
    # Spec highlight on the dot
    pygame.draw.circle(big, (255, 220, 220),
                       (cx - SS // 2, cy + SS // 2),
                       max(1, SS // 2))

    surf.blit(_resolve(big, out_size, out_size), (0, 0))
    return surf


# ── Concept 2 — BOMB (refined) ───────────────────────────────────────
def draw_bomb(out_size: int, pulse: float) -> pygame.Surface:
    """Round cast-iron bomb with a lit fuse: white-hot spark core +
    orange halo, 2-3 spark dots flying off, soft red rim-glow under the
    sphere (replaces the R1 red equator band), dark shadow on the dirt
    below. Keeps the round black silhouette and the curling fuse."""
    surf = pygame.Surface((out_size, out_size), pygame.SRCALPHA)
    _warning_glow_blit(surf, out_size // 2, out_size // 2 + 6, pulse,
                       color=(245, 110, 40),
                       core_alpha=175, core_r=14, halo_r=19)

    big = _ss_canvas(out_size, out_size)
    cx = out_size * SS // 2
    cy = out_size * SS // 2 + 4 * SS

    body_r = 14 * SS

    # Soft red rim-glow disc BENEATH the bomb (replaces the equator bar).
    # Painted before the body so it bleeds out around the silhouette.
    rim_glow = _radial_glow(int(body_r * 1.45),
                            (230, 50, 50), max_alpha=110)
    big.blit(rim_glow,
             (cx - rim_glow.get_width() // 2,
              cy + 4 * SS - rim_glow.get_height() // 2))

    # Dark contact shadow on the dirt under the bomb
    shadow_rect = pygame.Rect(0, 0, int(body_r * 1.9), int(body_r * 0.55))
    shadow_rect.center = (cx, cy + body_r + 2 * SS)
    sh = pygame.Surface(shadow_rect.size, pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (0, 0, 0, 140),
                        pygame.Rect(0, 0, *shadow_rect.size))
    big.blit(sh, shadow_rect.topleft)

    # Cast-iron body — outer rim shadow, dome black, soft top-left sheen
    pygame.draw.circle(big, SHADOW,     (cx, cy + 2 * SS), body_r + 2 * SS)
    pygame.draw.circle(big, BLACK_DOME, (cx, cy), body_r + SS)
    pygame.draw.circle(big, (32, 32, 44), (cx, cy), body_r)
    # Sheen — broad soft arc, not a buff-y shine
    sheen_rect = pygame.Rect(cx - body_r + 3 * SS, cy - body_r + 2 * SS,
                             int(body_r * 1.0), int(body_r * 0.65))
    pygame.draw.ellipse(big, (75, 78, 95), sheen_rect)
    pygame.draw.ellipse(big, (110, 112, 130),
                        sheen_rect.inflate(-3 * SS, -3 * SS))

    # Fuse cap — short cylinder
    cap_w, cap_h = 8 * SS, 5 * SS
    cap_rect = pygame.Rect(cx - cap_w // 2, cy - body_r - cap_h + 1 * SS,
                           cap_w, cap_h)
    pygame.draw.rect(big, (40, 28, 16), cap_rect, border_radius=SS)
    pygame.draw.rect(big, (90, 60, 28),
                     cap_rect.inflate(-2 * SS, -2 * SS), border_radius=SS)

    # Fuse — curving cord, jute-coloured
    fuse_base = (cx, cap_rect.top + SS)
    fuse_pts = [
        fuse_base,
        (cx - 2 * SS, cy - body_r - 4 * SS),
        (cx + 3 * SS, cy - body_r - 9 * SS),
        (cx - 1 * SS, cy - body_r - 13 * SS),
        (cx + 4 * SS, cy - body_r - 16 * SS),
    ]
    pygame.draw.lines(big, (40, 28, 14), False, fuse_pts, 3 * SS)
    pygame.draw.lines(big, (180, 130, 60), False, fuse_pts, max(1, SS + 1))
    pygame.draw.lines(big, (240, 200, 110), False, fuse_pts[:3],
                      max(1, SS // 2))

    tip = fuse_pts[-1]
    flick = 0.7 + 0.3 * (0.5 + 0.5 * math.sin(pulse * 6.5))

    # Burning tip — layered orange halo with a tight 1-px-equivalent
    # white-hot core so it reads as LIT, not just a stem end.
    for r, col in (
        (int(6 * SS * flick), (255, 130, 30, 130)),
        (int(4 * SS * flick), (255, 180, 70, 200)),
        (int(2 * SS * flick), (255, 230, 160, 240)),
    ):
        eg = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(eg, col, (r + 2, r + 2), max(1, r))
        big.blit(eg, (tip[0] - r - 2, tip[1] - r - 2))
    # White-hot core — 1 px at native, so SS at supersample
    pygame.draw.circle(big, (255, 255, 240), tip, max(1, SS))

    # 2-3 spark dots flying off the tip — short bright stars
    spark_angles = (30, 110, 200, 290)
    for i, ang_deg in enumerate(spark_angles):
        ang = math.radians(ang_deg + pulse * 25)
        dist = (6 + (i % 2) * 3) * SS * flick
        sx = tip[0] + int(math.cos(ang) * dist)
        sy = tip[1] + int(math.sin(ang) * dist)
        # Trailing line + bright pip at the end
        pygame.draw.line(big, (255, 200, 110),
                         (tip[0] + int(math.cos(ang) * 2 * SS),
                          tip[1] + int(math.sin(ang) * 2 * SS)),
                         (sx, sy), max(1, SS // 2))
        pygame.draw.circle(big, (255, 240, 200), (sx, sy), max(1, SS - 1))

    # Smoke curl — three offset translucent puffs above the spark
    smoke_offset = math.sin(pulse * 1.3) * 1.5 * SS
    for i, (dx, dy, r, a) in enumerate((
        (3, -4, 4, 70),
        (-2, -8, 5, 55),
        (4, -13, 6, 35),
    )):
        puff = pygame.Surface((r * 2 * SS + 2, r * 2 * SS + 2),
                              pygame.SRCALPHA)
        pygame.draw.circle(puff, (190, 195, 205, a),
                           (r * SS + 1, r * SS + 1), r * SS)
        big.blit(puff,
                 (tip[0] + (dx * SS + int(smoke_offset)) - r * SS - 1,
                  tip[1] + dy * SS - r * SS - 1))

    surf.blit(_resolve(big, out_size, out_size), (0, 0))
    return surf


# ── Concept 3 — CURSED GEM (angular shard + two violet cracks) ───────
def draw_cursed_gem(out_size: int, pulse: float) -> pygame.Surface:
    """Near-black hexagonal shard with TWO perpendicular fractures
    glowing bruise-violet. Asymmetric chipped corners + sharp angles so
    it cannot be confused with the poison vial silhouette or read as a
    soft jewel. Sparse 1-px corner glints keep it from going "shiny
    collectible.\""""
    surf = pygame.Surface((out_size, out_size), pygame.SRCALPHA)
    _warning_glow_blit(surf, out_size // 2, out_size // 2 + 2, pulse,
                       color=(150, 50, 200),
                       core_alpha=165, core_r=13, halo_r=17)

    big = _ss_canvas(out_size, out_size)
    cx = out_size * SS // 2
    cy = out_size * SS // 2 + 1 * SS

    s = SS

    # Asymmetric chipped rhombus / sharp hexagonal shard. Top is a
    # tilted apex; bottom is a chipped corner. NOT a teardrop.
    base_pts = [
        (cx - 3 * s,    cy - 18 * s),    # tilted top apex
        (cx + 5 * s,    cy - 14 * s),    # top-right shoulder
        (cx + 14 * s,   cy - 4 * s),     # right outer
        (cx + 9 * s,    cy + 10 * s),    # lower-right
        (cx + 2 * s,    cy + 17 * s),    # bottom chipped point
        (cx - 8 * s,    cy + 12 * s),    # lower-left
        (cx - 14 * s,   cy + 1 * s),     # left outer
        (cx - 10 * s,   cy - 11 * s),    # upper-left
    ]

    # Drop shadow — deeper for the darker body
    shadow = [(p[0] + 2 * s, p[1] + 3 * s) for p in base_pts]
    pygame.draw.polygon(big, (2, 0, 8), shadow)

    # Near-black body — push to (15,12,30) per critique
    pygame.draw.polygon(big, (15, 12, 30), base_pts)

    # Subtle inner facet split — slightly lighter on the left face so
    # the shape doesn't go totally flat.
    apex = base_pts[0]
    bottom = base_pts[4]
    facet_left = [apex, base_pts[7], base_pts[6], base_pts[5], bottom]
    pygame.draw.polygon(big, (22, 16, 40), facet_left)

    # Faint violet rim line — single hairline, NOT a glow rim
    pygame.draw.polygon(big, (60, 30, 90), base_pts, max(1, SS // 2 + 1))

    # === Two perpendicular cracks (the danger language) ============
    # Crack A — main diagonal, top-left to bottom-right, jagged.
    crack_a = [
        (cx - 9 * s,  cy - 13 * s),
        (cx - 4 * s,  cy - 7 * s),
        (cx + 1 * s,  cy - 2 * s),
        (cx + 5 * s,  cy + 5 * s),
        (cx + 8 * s,  cy + 11 * s),
    ]
    # Crack B — perpendicular crossbar, top-right to bottom-left.
    crack_b = [
        (cx + 8 * s,  cy - 10 * s),
        (cx + 3 * s,  cy - 5 * s),
        (cx - 1 * s,  cy + 1 * s),
        (cx - 6 * s,  cy + 7 * s),
        (cx - 10 * s, cy + 11 * s),
    ]

    def _paint_crack(pts):
        """Wide bruise-violet glow underlay → narrow bright violet core
        → 1-px white-hot centreline so the crack reads at 48 px."""
        layers = (
            (int(SS * 3.5),       (140, 60, 180, 100)),
            (int(SS * 2.2),       (170, 80, 210, 160)),
            (int(SS * 1.3),       (210, 130, 240, 200)),
            (max(1, SS // 2 + 1), (255, 230, 255, 255)),
        )
        for gw, col in layers:
            tmp = pygame.Surface((big.get_width(), big.get_height()),
                                 pygame.SRCALPHA)
            pygame.draw.lines(tmp, col, False, pts, gw)
            big.blit(tmp, (0, 0))

    _paint_crack(crack_a)
    _paint_crack(crack_b)

    # Pulsing violet ember at the crack intersection — the wound's heart
    pulse_amt = 0.7 + 0.3 * (0.5 + 0.5 * math.sin(pulse * 4.5))
    ember_r = int(max(1, SS * 1.8 * pulse_amt))
    ember_surf = pygame.Surface((ember_r * 4, ember_r * 4), pygame.SRCALPHA)
    pygame.draw.circle(ember_surf, (180, 80, 220, 180),
                       (ember_r * 2, ember_r * 2), ember_r * 2)
    pygame.draw.circle(ember_surf, (255, 240, 255, 255),
                       (ember_r * 2, ember_r * 2), max(1, ember_r))
    big.blit(ember_surf, (cx - ember_r * 2,
                          cy - 1 * s - ember_r * 2))

    # Few sparse 1-px corner glints (just 2 — not "shiny loot")
    pygame.draw.circle(big, (235, 220, 255),
                       (cx - 9 * s, cy - 11 * s), max(1, SS))
    pygame.draw.circle(big, (220, 200, 240),
                       (cx + 12 * s, cy - 1 * s), max(1, SS - 1))

    # Faint violet wisp escaping the top crack
    for i, (dy, r, a) in enumerate(((-9, 2, 110), (-13, 3, 70), (-17, 4, 40))):
        sw = pygame.Surface((r * 2 * s + 2, r * 2 * s + 2), pygame.SRCALPHA)
        pygame.draw.circle(sw, (170, 100, 220, a),
                           (r * s + 1, r * s + 1), r * s)
        big.blit(sw, (crack_a[0][0] - r * s + i * s,
                      crack_a[0][1] + dy * s))

    surf.blit(_resolve(big, out_size, out_size), (0, 0))
    return surf


# ── Concept 4 — POISON VIAL (label dropped, fat red X on glass) ──────
def draw_poison_vial(out_size: int, pulse: float) -> pygame.Surface:
    """Green-glass apothecary flask. The white label is gone — a thick
    red X is painted DIRECTLY on the glass (3-px arms at native size).
    Vapour is three distinct sickly-green puffs above the cork."""
    surf = pygame.Surface((out_size, out_size), pygame.SRCALPHA)
    _warning_glow_blit(surf, out_size // 2, out_size // 2 + 3, pulse,
                       color=(120, 220, 90),
                       core_alpha=170, core_r=13, halo_r=18)

    big = _ss_canvas(out_size, out_size)
    cx = out_size * SS // 2
    cy = out_size * SS // 2 + 3 * SS

    # Flask body — rounded shoulder + slight conical taper
    body_top    = cy - 8 * SS
    body_bottom = cy + 15 * SS
    body_pts = [
        (cx - 4 * SS, body_top),                         # neck shoulder L
        (cx - 11 * SS, body_top + 5 * SS),               # flare L
        (cx - 12 * SS, body_bottom - 4 * SS),            # belly L
        (cx - 9 * SS,  body_bottom),                     # foot L
        (cx + 9 * SS,  body_bottom),                     # foot R
        (cx + 12 * SS, body_bottom - 4 * SS),
        (cx + 11 * SS, body_top + 5 * SS),
        (cx + 4 * SS,  body_top),                        # neck shoulder R
    ]
    # Dark glass outline
    pygame.draw.polygon(big, BLACK_DOME, body_pts)
    # Slightly green-tinted dark glass fill (so the empty top still
    # reads as glass, not as void)
    inner_glass = [(int(p[0] * 0.94 + cx * 0.06),
                    int(p[1] * 0.97 + cy * 0.03)) for p in body_pts]
    pygame.draw.polygon(big, GREEN_GLASS, inner_glass)

    # Liquid fill — green up to ~50% of body, wavy meniscus
    fill_top_y = body_top + 9 * SS
    meniscus = []
    seg_x_left = cx - 11 * SS
    seg_x_right = cx + 11 * SS
    for i in range(13):
        t = i / 12
        mx = int(seg_x_left + (seg_x_right - seg_x_left) * t)
        wave = math.sin(pulse * 2.2 + i * 0.9) * SS
        meniscus.append((mx, fill_top_y + int(wave)))
    below = [p for p in body_pts if p[1] > fill_top_y]
    right_below = sorted([p for p in below if p[0] >= cx],
                         key=lambda q: q[1])
    left_below = sorted([p for p in below if p[0] < cx],
                        key=lambda q: -q[1])
    liquid_outline = meniscus + right_below + left_below
    pygame.draw.polygon(big, GREEN_LO, liquid_outline)
    pygame.draw.lines(big, GREEN_TOX, False, meniscus, max(1, SS // 2 + 1))
    band_pts = [(p[0], p[1] + 4 * SS) for p in meniscus]
    pygame.draw.lines(big, (90, 160, 70), False, band_pts, max(1, SS // 2))

    # Bubbles inside the liquid
    for i, (bx_off, by_off, br) in enumerate(((-4, 6, 2),
                                              (3, 9, 1),
                                              (-1, 3, 1))):
        drift = math.sin(pulse * 1.6 + i * 1.7) * SS
        pygame.draw.circle(big, (180, 240, 180, 220),
                           (cx + bx_off * SS, fill_top_y + by_off * SS
                            + int(drift)), br * SS)

    # Glass rim highlight on the left side
    pygame.draw.line(big, (90, 160, 110),
                     (cx - 11 * SS, body_top + 6 * SS),
                     (cx - 11 * SS, body_bottom - 5 * SS),
                     max(1, SS // 2 + 1))

    # Neck — narrow cylinder
    neck_rect = pygame.Rect(cx - 4 * SS, body_top - 5 * SS,
                            8 * SS, 6 * SS)
    pygame.draw.rect(big, BLACK_DOME, neck_rect)
    pygame.draw.rect(big, (30, 60, 40),
                     neck_rect.inflate(-2 * SS, -1 * SS))
    pygame.draw.line(big, (90, 160, 110),
                     (neck_rect.left + SS, neck_rect.top + SS),
                     (neck_rect.left + SS, neck_rect.bottom - SS),
                     max(1, SS // 2))

    # Cork stopper
    cork_rect = pygame.Rect(cx - 5 * SS, body_top - 10 * SS, 10 * SS, 5 * SS)
    pygame.draw.rect(big, WOOD_DARK, cork_rect, border_radius=SS)
    pygame.draw.rect(big, (170, 110, 60),
                     cork_rect.inflate(-2 * SS, -1 * SS), border_radius=SS)
    pygame.draw.line(big, (220, 170, 110),
                     (cork_rect.left + 2 * SS, cork_rect.top + SS),
                     (cork_rect.right - 2 * SS, cork_rect.top + SS),
                     max(1, SS // 2))

    # === RED X painted directly on the glass (no label) =============
    # Critique calls for 3-px arms at native 48 px → 3 * SS on supersample.
    # Place the X across the dark upper-body glass for maximum contrast.
    x_arm_w = 3 * SS
    x_cx = cx
    x_cy = cy + 1 * SS
    x_reach = 7 * SS
    # Dark backing strokes — gives the red an outline against the glass
    pygame.draw.line(big, (40, 5, 8),
                     (x_cx - x_reach - SS // 2, x_cy - x_reach - SS // 2),
                     (x_cx + x_reach + SS // 2, x_cy + x_reach + SS // 2),
                     x_arm_w + 2 * SS // 2 + 2)
    pygame.draw.line(big, (40, 5, 8),
                     (x_cx + x_reach + SS // 2, x_cy - x_reach - SS // 2),
                     (x_cx - x_reach - SS // 2, x_cy + x_reach + SS // 2),
                     x_arm_w + 2 * SS // 2 + 2)
    # Red foreground X — thick, vivid
    pygame.draw.line(big, (220, 35, 45),
                     (x_cx - x_reach, x_cy - x_reach),
                     (x_cx + x_reach, x_cy + x_reach),
                     x_arm_w)
    pygame.draw.line(big, (220, 35, 45),
                     (x_cx + x_reach, x_cy - x_reach),
                     (x_cx - x_reach, x_cy + x_reach),
                     x_arm_w)
    # Tiny bright spec along the upper-left arm — selling "painted on"
    pygame.draw.line(big, (255, 130, 130),
                     (x_cx - x_reach + SS, x_cy - x_reach + SS // 2),
                     (x_cx - x_reach + 3 * SS, x_cy - x_reach + 2 * SS),
                     max(1, SS // 2))

    # Vapour wisps above cork — 3 distinct puff blobs, not a wisp
    puffs = (
        (-1, -12, 4, 150),
        (2,  -17, 5, 110),
        (-2, -23, 6, 70),
    )
    for i, (dx, dy, r, a) in enumerate(puffs):
        drift = math.sin(pulse * 1.0 + i * 0.7) * SS
        pw = pygame.Surface((r * 2 * SS + 2, r * 2 * SS + 2),
                            pygame.SRCALPHA)
        pygame.draw.circle(pw, (170, 220, 160, a),
                           (r * SS + 1, r * SS + 1), r * SS)
        # Inner highlight on the lowest two puffs
        if i < 2:
            pygame.draw.circle(pw, (210, 240, 190, min(255, a + 50)),
                               (r * SS + 1 - SS, r * SS + 1 - SS),
                               max(1, r * SS - 2 * SS))
        big.blit(pw, (cx + dx * SS + int(drift) - r * SS - 1,
                      cy + dy * SS - r * SS - 1))

    surf.blit(_resolve(big, out_size, out_size), (0, 0))
    return surf


# ── Concept 5 — RUSTY BUZZSAW (replaces tombstone) ───────────────────
def draw_buzzsaw(out_size: int, pulse: float) -> pygame.Surface:
    """Rusty circular sawblade hanging in air: 10 triangular teeth
    around the rim, iron-grey body with patches of rust-brown, dark hub
    with a centre hole, motion-blur arcs hinting at spin. Sits over a
    strong red warning halo — the most explicit hazard in the lineup."""
    surf = pygame.Surface((out_size, out_size), pygame.SRCALPHA)
    _warning_glow_blit(surf, out_size // 2, out_size // 2, pulse,
                       color=(235, 40, 50),
                       core_alpha=175, core_r=14, halo_r=19)

    big = _ss_canvas(out_size, out_size)
    cx = out_size * SS // 2
    cy = out_size * SS // 2

    # Blade rotation phase — slow visible spin in the at-size preview
    spin = pulse * 0.6

    blade_r_outer = 16 * SS    # tooth tip
    blade_r_inner = 13 * SS    # tooth base / blade body rim
    n_teeth = 10

    # Drop shadow under the blade
    sh_rect = pygame.Rect(0, 0, int(blade_r_outer * 2 * 0.9),
                          int(blade_r_outer * 0.5))
    sh_rect.center = (cx + 2 * SS, cy + 3 * SS)
    sh = pygame.Surface(sh_rect.size, pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (0, 0, 0, 130),
                        pygame.Rect(0, 0, *sh_rect.size))
    big.blit(sh, sh_rect.topleft)

    # === Teeth drawn first so blade body overdraws their bases =====
    for i in range(n_teeth):
        a0 = (i / n_teeth) * math.tau + spin
        a1 = ((i + 0.45) / n_teeth) * math.tau + spin
        a2 = ((i + 0.9) / n_teeth) * math.tau + spin
        # Teeth are asymmetric — leading edge sharper than trailing, so
        # they read as cutters not stars
        p0 = (cx + math.cos(a0) * blade_r_inner,
              cy + math.sin(a0) * blade_r_inner)
        p1 = (cx + math.cos(a1) * blade_r_outer,
              cy + math.sin(a1) * blade_r_outer)
        p2 = (cx + math.cos(a2) * blade_r_inner,
              cy + math.sin(a2) * blade_r_inner)
        tri = [(int(p[0]), int(p[1])) for p in (p0, p1, p2)]
        pygame.draw.polygon(big, SAW_GREY, tri)
        # Bright leading edge on each tooth
        pygame.draw.line(big, SAW_GREY_HI,
                         (int(p0[0]), int(p0[1])),
                         (int(p1[0]), int(p1[1])),
                         max(1, SS // 2 + 1))
        # Dark trailing edge for tooth depth
        pygame.draw.line(big, IRON_DARK,
                         (int(p1[0]), int(p1[1])),
                         (int(p2[0]), int(p2[1])),
                         max(1, SS // 2))

    # === Blade body — iron disc with mottled rust patches ============
    body_rect = pygame.Rect(0, 0, blade_r_inner * 2, blade_r_inner * 2)
    body_rect.center = (cx, cy)
    pygame.draw.ellipse(big, IRON_DARK,
                        body_rect.inflate(2 * SS, 2 * SS))
    pygame.draw.ellipse(big, SAW_GREY, body_rect)
    pygame.draw.ellipse(big, SAW_GREY_HI,
                        body_rect.inflate(-3 * SS, -3 * SS))

    # Rust patches — irregular blotches, rotated with the spin
    rust_patches = (
        (0.0,  0.55, 5, 4),
        (1.7,  0.62, 4, 3),
        (3.2,  0.48, 6, 4),
        (4.7,  0.58, 3, 3),
        (5.7,  0.52, 4, 3),
    )
    for ang_off, dist_f, rw, rh in rust_patches:
        ang = ang_off + spin * 0.8
        dx = math.cos(ang) * blade_r_inner * dist_f
        dy = math.sin(ang) * blade_r_inner * dist_f
        patch_rect = pygame.Rect(0, 0, rw * SS, rh * SS)
        patch_rect.center = (cx + int(dx), cy + int(dy))
        pygame.draw.ellipse(big, RUST, patch_rect)
        pygame.draw.ellipse(big, RUST_DEEP,
                            patch_rect.inflate(-SS, -SS))

    # Concentric scoring rings on the blade — turning marks
    for r_fac in (0.85, 0.65, 0.4):
        ring_rect = body_rect.inflate(
            -int(blade_r_inner * 2 * (1 - r_fac)),
            -int(blade_r_inner * 2 * (1 - r_fac)),
        )
        pygame.draw.ellipse(big, (140, 130, 120), ring_rect,
                            max(1, SS // 2))

    # Hub — darker disc with a hex/round mounting hole
    hub_r = 4 * SS
    pygame.draw.circle(big, IRON_DARK, (cx, cy), hub_r + SS)
    pygame.draw.circle(big, IRON_MID, (cx, cy), hub_r)
    pygame.draw.circle(big, IRON_HI, (cx - SS, cy - SS), max(1, SS))
    # Centre mounting hole
    pygame.draw.circle(big, BLACK_DOME, (cx, cy), int(1.6 * SS))
    # Hex bolt suggestion — three short tick marks around the hole
    for tick_a in (0, math.tau / 3, 2 * math.tau / 3):
        a = tick_a + spin
        tx0 = cx + int(math.cos(a) * SS * 1.6)
        ty0 = cy + int(math.sin(a) * SS * 1.6)
        tx1 = cx + int(math.cos(a) * SS * 2.6)
        ty1 = cy + int(math.sin(a) * SS * 2.6)
        pygame.draw.line(big, (40, 42, 54), (tx0, ty0), (tx1, ty1),
                         max(1, SS // 2))

    # Motion-blur arcs — 2-3 faint white arcs OUTSIDE the teeth to
    # suggest spin. Painted on a separate surface for alpha control.
    motion_surf = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    for arc_off, arc_len, alpha in (
        (0.2,  1.4, 90),
        (2.6,  1.2, 70),
        (4.4,  1.5, 55),
    ):
        start_a = arc_off + spin
        end_a = start_a + arc_len
        arc_rect = pygame.Rect(0, 0, int(blade_r_outer * 2.35),
                                int(blade_r_outer * 2.35))
        arc_rect.center = (cx, cy)
        pygame.draw.arc(motion_surf, (255, 255, 255, alpha), arc_rect,
                        start_a, end_a, max(1, SS // 2 + 1))
    big.blit(motion_surf, (0, 0))

    surf.blit(_resolve(big, out_size, out_size), (0, 0))
    return surf


# ── Panel composition ───────────────────────────────────────────────
CONCEPTS = [
    ("BEAR TRAP",   draw_bear_trap,
     "closed jaw-ring (top-down), serrated teeth, armed dot"),
    ("BOMB",        draw_bomb,
     "soft red rim-glow, white-hot fuse core, spark dots flying"),
    ("CURSED GEM",  draw_cursed_gem,
     "near-black shard, two perpendicular violet cracks"),
    ("POISON VIAL", draw_poison_vial,
     "thick red X painted on glass, 3 distinct vapour puffs"),
    ("BUZZSAW",     draw_buzzsaw,
     "rusty toothed sawblade, motion arcs, red hazard halo"),
]


def _panel_bg(surf: pygame.Surface, rect: pygame.Rect) -> None:
    pygame.draw.rect(surf, PANEL_BG, rect, border_radius=10)
    pygame.draw.rect(surf, GRID, rect, width=1, border_radius=10)


def _draw_label(surf: pygame.Surface, text: str, x: int, y: int,
                font: pygame.font.Font, color=INK) -> None:
    s = font.render(text, True, color)
    surf.blit(s, (x, y))


def _draw_grid_dot(surf: pygame.Surface, rect: pygame.Rect) -> None:
    """Faint vertical hairline divider between the two icon stages."""
    mid = rect.left + rect.width // 2 + 30
    pygame.draw.line(surf, (44, 50, 70), (mid, rect.top + 18),
                     (mid, rect.bottom - 18), 1)


def build_sheet() -> pygame.Surface:
    sheet = pygame.Surface((SHEET_W, SHEET_H))
    sheet.fill(DAWN_TEAL)

    font_title = pygame.font.SysFont("dejavusansmono", 24, bold=True)
    font_h     = pygame.font.SysFont("dejavusans", 16, bold=True)
    font_s     = pygame.font.SysFont("dejavusans", 12)
    font_xs    = pygame.font.SysFont("dejavusans", 10)

    _draw_label(sheet, "DEATH TRAP  —  Round 2", 16, 12, font_title)
    _draw_label(sheet,
                "rev: stronger 48-px silhouettes + bumped warning halo "
                "(~170 a, +2-3 px outer) | tombstone replaced by buzzsaw",
                16, 38, font_s, color=DIM)

    # Pulse picked per concept so spark/glow phases feel alive.
    base_pulse = {
        "BEAR TRAP":   1.7,
        "BOMB":        2.4,
        "CURSED GEM":  1.1,
        "POISON VIAL": 0.5,
        "BUZZSAW":     2.0,
    }

    for i, (name, fn, blurb) in enumerate(CONCEPTS):
        row = i
        panel_x = GUTTER
        panel_y = TITLE_H + row * (PANEL_H + GUTTER) + GUTTER
        rect = pygame.Rect(panel_x, panel_y, PANEL_W, PANEL_H)
        _panel_bg(sheet, rect)
        _draw_grid_dot(sheet, rect)

        _draw_label(sheet, f"{i + 1}.  {name}",
                    rect.left + 14, rect.top + 10, font_h)
        _draw_label(sheet, blurb,
                    rect.left + 14, rect.top + 30, font_s, color=DIM)

        # Left: at-size render with bob baked in
        icon = fn(NATIVE_PX, base_pulse[name])
        bob = int(math.sin(base_pulse[name] * 1.0) * 2)
        left_cx = rect.left + 70
        left_cy = rect.top + rect.height // 2 + 8 + bob
        swatch = pygame.Surface((84, 84), pygame.SRCALPHA)
        pygame.draw.circle(swatch, DAWN_TEAL, (42, 42), 42)
        pygame.draw.circle(swatch, (28, 32, 50), (42, 42), 42, 2)
        sheet.blit(swatch, (left_cx - 42, left_cy - 42))
        sheet.blit(icon, (left_cx - icon.get_width() // 2,
                          left_cy - icon.get_height() // 2))
        _draw_label(sheet, "in-world  48 px", left_cx - 38,
                    rect.bottom - 22, font_xs, color=DIM)

        # Right: 4x zoom
        zoomed = pygame.transform.scale(
            icon,
            (NATIVE_PX * ZOOM_FACTOR, NATIVE_PX * ZOOM_FACTOR),
        )
        right_cx = rect.right - 120
        right_cy = rect.top + rect.height // 2 + 6
        z_rect = pygame.Rect(0, 0, NATIVE_PX * ZOOM_FACTOR + 16,
                             NATIVE_PX * ZOOM_FACTOR + 16)
        z_rect.center = (right_cx, right_cy)
        pygame.draw.rect(sheet, (18, 22, 34), z_rect, border_radius=6)
        pygame.draw.rect(sheet, GRID, z_rect, width=1, border_radius=6)
        sheet.blit(zoomed, (right_cx - zoomed.get_width() // 2,
                            right_cy - zoomed.get_height() // 2))
        _draw_label(sheet, "4x zoom",
                    z_rect.left + 6, z_rect.bottom + 4, font_xs, color=DIM)

    footer = ("judged at 48 px first | halo ~170 alpha core + outer 2-3 px "
              "ring | no PNGs | procedural only")
    foot_s = font_xs.render(footer, True, DIM)
    sheet.blit(foot_s, (GUTTER + 4, SHEET_H - 16))

    return sheet


def main() -> None:
    pygame.init()
    out_dir = os.path.join(os.path.dirname(__file__), "..", "docs",
                           "death_pickup")
    out_dir = os.path.abspath(out_dir)
    os.makedirs(out_dir, exist_ok=True)
    sheet = build_sheet()
    out_path = os.path.join(out_dir, "round_2.png")
    pygame.image.save(sheet, out_path)
    print(out_path)


if __name__ == "__main__":
    main()
    sys.exit(0)
