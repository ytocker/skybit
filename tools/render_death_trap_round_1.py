"""Death-Trap pickup — Round 1 exploration sheet.

Renders five distinct hazard-pickup concepts side-by-side as a single
review PNG under docs/death_pickup/round_1.png. Each concept appears
twice: once at its real ~48 px in-game footprint on the dawn-sky teal
background (38,44,66), and once at 4× zoom so the art-director can
judge silhouette + detail.

WHY this lives in tools/ and not game/ — Round 1 only ships a design
sheet; no production code is touched until a winner is chosen.

Concepts (telegraphed danger, NOT deceptive mimics):
  1. BEAR TRAP   — sprung iron jaws on a wood plate, red "armed" dot.
  2. BOMB        — cast-iron sphere with lit fuse + spark + smoke curl.
  3. CURSED GEM  — jagged obsidian shard, hairline crack leaking red.
  4. POISON VIAL — black flask of sickly-green liquid, hazard label.
  5. TOMBSTONE   — cracked slab, soil mound, withered grass.

All draws supersample at SS=5 then smoothscale to the native size so
edges match the rest of the pickup kit (magnet / slowmo / shrink).
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

NATIVE_PX        = 48          # display footprint target
SS               = 5           # supersample factor
ZOOM_FACTOR      = 4           # right-side zoom


# ── Shared palette (kit-matched) ─────────────────────────────────────
BLACK_DOME = (10, 10, 18)
SHADOW     = (4,  4,  10)
RED_HI     = (235, 35, 45)
RED_LO     = (130, 18, 24)
EMBER      = (255, 170, 60)
SPARK      = (255, 240, 200)
PURPLE     = (195, 135, 255)
IRON_DARK  = (52,  56,  72)
IRON_MID   = (90,  96, 112)
IRON_HI    = (175, 184, 200)
RUST       = (160,  80,  40)
COPPER     = (200, 110,  55)
WOOD_DARK  = (60,  38,  22)
WOOD_MID   = (95,  62,  34)
WOOD_HI    = (140,  92,  52)
GREEN_TOX  = (120, 200,  90)
GREEN_LO   = (40,  100,  50)
SULFUR     = (220, 220,  80)
BONE       = (200, 200, 190)   # NOT cream — skateboard owns that
DIRT_LO    = (50,  32,  20)
DIRT_HI    = (110,  78,  46)
GRASS_DRY  = (130, 120,  72)


# ── Helpers ──────────────────────────────────────────────────────────
def _ss_canvas(w: int, h: int) -> pygame.Surface:
    return pygame.Surface((w * SS, h * SS), pygame.SRCALPHA)


def _resolve(big: pygame.Surface, w: int, h: int) -> pygame.Surface:
    return pygame.transform.smoothscale(big, (w, h))


def _radial_glow(radius: int, color, max_alpha: int = 120) -> pygame.Surface:
    """Soft circular glow — fades from max_alpha at the centre to 0 at
    the rim. Used for the "warning glow" pulse beneath every icon."""
    d = radius * 2 + 2
    g = pygame.Surface((d, d), pygame.SRCALPHA)
    cx = d // 2
    for r in range(radius, 0, -1):
        t = r / radius
        a = int(max_alpha * (1 - t) ** 1.8)
        pygame.draw.circle(g, (*color, a), (cx, cx), r)
    return g


def _warning_glow_blit(surf: pygame.Surface, cx: int, cy: int,
                       pulse_phase: float, color=(235, 35, 45)) -> None:
    """Subtle breathing red/amber halo — readable as DANGER, not BUFF.
    Low alpha and small radius keep it clear of "buff aura" reads."""
    breath = 0.65 + 0.35 * (0.5 + 0.5 * math.sin(pulse_phase))
    r = int(6 + breath * 2)
    glow = _radial_glow(r, color, max_alpha=int(90 * breath))
    surf.blit(glow, (cx - glow.get_width() // 2,
                     cy - glow.get_height() // 2))


# ── Concept 1 — BEAR TRAP ────────────────────────────────────────────
def draw_bear_trap(out_size: int, pulse: float) -> pygame.Surface:
    """Iron jaws sprung at an angle on a circular wood plate. Hairline
    serrations down the inner bite. A short broken-chain stub trails
    off the lower-left. Tiny red "armed" dot sits on the plate as a
    micro-cue. Glow tinted amber-red so it reads HAZARD not BUFF."""
    surf = pygame.Surface((out_size, out_size), pygame.SRCALPHA)
    _warning_glow_blit(surf, out_size // 2, out_size // 2 + 2,
                       pulse, color=(220, 70, 40))

    big = _ss_canvas(out_size, out_size)
    cx = out_size * SS // 2
    cy = out_size * SS // 2 + 2 * SS

    # Wood mounting plate — slightly oval so it reads 3/4 view
    plate_w = int(38 * SS)
    plate_h = int(12 * SS)
    plate_rect = pygame.Rect(0, 0, plate_w, plate_h)
    plate_rect.center = (cx, cy + 6 * SS)
    pygame.draw.ellipse(big, WOOD_DARK, plate_rect.inflate(2 * SS, 2 * SS))
    pygame.draw.ellipse(big, WOOD_MID,  plate_rect)
    # Wood grain
    for gy in range(plate_rect.top + 2 * SS, plate_rect.bottom, 3 * SS):
        pygame.draw.line(big, WOOD_DARK,
                         (plate_rect.left + 3 * SS, gy),
                         (plate_rect.right - 3 * SS, gy), max(1, SS // 2))
    pygame.draw.ellipse(big, WOOD_HI,
                        pygame.Rect(plate_rect.left + 4 * SS,
                                    plate_rect.top + 1 * SS,
                                    plate_rect.width - 8 * SS,
                                    2 * SS))

    # Central pressure pan — dark iron disc
    pan_r = 7 * SS
    pygame.draw.circle(big, IRON_DARK, (cx, cy + 4 * SS), pan_r + SS)
    pygame.draw.circle(big, IRON_MID,  (cx, cy + 4 * SS), pan_r)
    pygame.draw.circle(big, IRON_HI,   (cx - 2 * SS, cy + 2 * SS), SS)

    # Jaws — two crescents opening upward. Drawn as polygons so the
    # serrated bite reads at 48 px (a straight curve smoothes away).
    def _jaw(side: int) -> None:
        """side = +1 right jaw, -1 left jaw."""
        # Outer arc points — bottom anchor near pan, tip up and outward,
        # then back inward to the bite line. Bite line is jagged.
        ax = cx + side * 1 * SS
        ay = cy + 3 * SS                          # base near pan
        tip_x = cx + side * 18 * SS
        tip_y = cy - 14 * SS
        outer = [
            (ax, ay),
            (cx + side * 6 * SS,  cy - 3 * SS),
            (cx + side * 13 * SS, cy - 11 * SS),
            (tip_x, tip_y),
            (cx + side * 16 * SS, cy - 16 * SS),
            (cx + side * 12 * SS, cy - 18 * SS),
            (cx + side * 6 * SS,  cy - 16 * SS),
        ]
        # Bite line (inner edge) — zig-zag for serrated teeth feel
        bite_pts = []
        steps = 7
        for i in range(steps + 1):
            t = i / steps
            bx = int(cx + side * (2 + (12 * t)) * SS)
            by = int(cy - 16 * t * SS - 1 * SS)
            jag = (-1 if i % 2 == 0 else +1) * SS
            bite_pts.append((bx, by + jag))
        poly = outer + list(reversed(bite_pts))
        pygame.draw.polygon(big, IRON_DARK, poly)
        # Inner lighter face
        inner_poly = [(int(p[0] - side * 1 * SS), int(p[1] + 1 * SS))
                      for p in poly]
        pygame.draw.polygon(big, IRON_MID, inner_poly)
        # Edge highlight on the outer rim
        pygame.draw.lines(big, IRON_HI, False, outer[:4], max(1, SS // 2 + 1))
        # Teeth — short dark lines on the bite line
        for i in range(0, len(bite_pts) - 1, 2):
            bx, by = bite_pts[i]
            pygame.draw.line(big, BLACK_DOME, (bx, by),
                             (bx - side * SS, by + 2 * SS), max(1, SS // 2))

    _jaw(+1)
    _jaw(-1)

    # Spring coils — two small circles at the jaw hinges
    for s in (-1, +1):
        hx = cx + s * 12 * SS
        hy = cy + 1 * SS
        pygame.draw.circle(big, IRON_DARK, (hx, hy), 3 * SS)
        pygame.draw.circle(big, COPPER,    (hx, hy), 2 * SS)
        pygame.draw.circle(big, RUST,      (hx, hy), 2 * SS, max(1, SS // 2))

    # Broken chain stub trailing off lower-left
    chain_y = cy + 9 * SS
    for i, dx in enumerate((-14, -17, -20)):
        link = pygame.Rect(0, 0, 3 * SS, 4 * SS)
        link.center = (cx + dx * SS, chain_y + (i % 2) * SS)
        pygame.draw.ellipse(big, IRON_MID, link)
        pygame.draw.ellipse(big, IRON_DARK, link, max(1, SS // 2))

    # Tiny RED "armed" dot on the plate
    armed_phase = 0.6 + 0.4 * (0.5 + 0.5 * math.sin(pulse * 3.0))
    arm_col = (int(180 + 70 * armed_phase), 30, 30)
    pygame.draw.circle(big, BLACK_DOME, (cx + 12 * SS, cy + 7 * SS), 2 * SS)
    pygame.draw.circle(big, arm_col,    (cx + 12 * SS, cy + 7 * SS), max(1, SS))

    surf.blit(_resolve(big, out_size, out_size), (0, 0))
    return surf


# ── Concept 2 — BOMB ─────────────────────────────────────────────────
def draw_bomb(out_size: int, pulse: float) -> pygame.Surface:
    """Classic round cast-iron bomb with lit fuse. Spark sits at the
    fuse tip and pops brighter on every pulse beat. Faint smoke curl
    above. NO skull face — the bone-cream skull is owned by skate."""
    surf = pygame.Surface((out_size, out_size), pygame.SRCALPHA)
    _warning_glow_blit(surf, out_size // 2, out_size // 2 + 4, pulse,
                       color=(245, 110, 40))

    big = _ss_canvas(out_size, out_size)
    cx = out_size * SS // 2
    cy = out_size * SS // 2 + 4 * SS

    body_r = 14 * SS

    # Cast-iron body — outer shadow, dome black, top-left specular
    pygame.draw.circle(big, SHADOW,     (cx, cy + 2 * SS), body_r + 2 * SS)
    pygame.draw.circle(big, BLACK_DOME, (cx, cy), body_r + SS)
    pygame.draw.circle(big, (32, 32, 44), (cx, cy), body_r)
    # Soft sheen — broad arc, not a buff-y shine
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
    # Fuse highlight — single bright filament on top
    pygame.draw.lines(big, (240, 200, 110), False, fuse_pts[:3],
                      max(1, SS // 2))

    # Spark cluster at the burning tip — pulses
    tip = fuse_pts[-1]
    flick = 0.6 + 0.4 * (0.5 + 0.5 * math.sin(pulse * 6.5))
    for r, col in (
        (int(5 * SS * flick), (255, 140, 30, 140)),
        (int(3 * SS * flick), (255, 200, 80, 220)),
        (int(2 * SS * flick), (255, 240, 200, 255)),
    ):
        ember_surf = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(ember_surf, col, (r + 1, r + 1), max(1, r))
        big.blit(ember_surf, (tip[0] - r - 1, tip[1] - r - 1))
    # Spark shards radiating
    for ang_deg in (15, 90, 165, 230, 305):
        ang = math.radians(ang_deg + pulse * 30)
        sx = tip[0] + int(math.cos(ang) * 7 * SS * flick)
        sy = tip[1] + int(math.sin(ang) * 7 * SS * flick)
        pygame.draw.line(big, (255, 220, 140),
                         tip, (sx, sy), max(1, SS // 2))

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

    # Red hazard band on the bomb body — a tiny ribbon for extra danger cue
    band_h = 3 * SS
    band_y = cy + 3 * SS
    band_pts = [
        (cx - body_r + 2 * SS, band_y),
        (cx + body_r - 2 * SS, band_y - 1 * SS),
        (cx + body_r - 2 * SS, band_y + band_h),
        (cx - body_r + 2 * SS, band_y + band_h + 1 * SS),
    ]
    pygame.draw.polygon(big, (180, 25, 30), band_pts)
    pygame.draw.polygon(big, (235, 60, 60), [
        (cx - body_r + 3 * SS, band_y + 1 * SS),
        (cx + body_r - 3 * SS, band_y),
        (cx + body_r - 3 * SS, band_y + band_h - 1 * SS),
        (cx - body_r + 3 * SS, band_y + band_h),
    ])

    surf.blit(_resolve(big, out_size, out_size), (0, 0))
    return surf


# ── Concept 3 — CURSED GEM ───────────────────────────────────────────
def draw_cursed_gem(out_size: int, pulse: float) -> pygame.Surface:
    """Angular obsidian shard with a violet rim-light and a hairline
    crack leaking red glow from within. The silhouette is intentionally
    spiky so it does NOT collide with the round magnet / shield / coin
    or the lamp's softer cut-glass arches."""
    surf = pygame.Surface((out_size, out_size), pygame.SRCALPHA)
    _warning_glow_blit(surf, out_size // 2, out_size // 2 + 2, pulse,
                       color=(220, 40, 60))

    big = _ss_canvas(out_size, out_size)
    cx = out_size * SS // 2
    cy = out_size * SS // 2 + 1 * SS

    # Crystal silhouette — irregular octagon, taller than wide
    s = SS
    base_pts = [
        (cx,            cy - 18 * s),    # top spike
        (cx + 9 * s,    cy - 11 * s),
        (cx + 13 * s,   cy - 1 * s),
        (cx + 8 * s,    cy + 12 * s),
        (cx + 2 * s,    cy + 17 * s),    # bottom point
        (cx - 6 * s,    cy + 13 * s),
        (cx - 13 * s,   cy + 2 * s),
        (cx - 10 * s,   cy - 9 * s),
    ]

    # Drop shadow
    shadow = [(p[0] + 2 * s, p[1] + 3 * s) for p in base_pts]
    pygame.draw.polygon(big, (4, 0, 14), shadow)

    # Outer black silhouette + faint violet rim
    pygame.draw.polygon(big, (15, 8, 24), base_pts)
    pygame.draw.polygon(big, (90, 50, 140), base_pts, max(1, SS // 2 + 1))

    # Internal facets — split the crystal into 3 sub-polys for shading
    apex = base_pts[0]
    bottom = base_pts[4]
    left_mid = base_pts[6]
    right_mid = base_pts[2]
    facet_left = [apex, left_mid, bottom]
    facet_right = [apex, right_mid, bottom]
    pygame.draw.polygon(big, (30, 18, 48), facet_left)
    pygame.draw.polygon(big, (22, 12, 38), facet_right)

    # Bright violet edge along the left facet — rim-light
    pygame.draw.line(big, (160, 110, 220), apex, left_mid, max(1, SS // 2 + 1))
    pygame.draw.line(big, PURPLE, apex,
                     (apex[0] - 4 * s, apex[1] + 6 * s), max(1, SS // 2 + 1))

    # Hairline RED crack — jagged line + glow halo behind it
    crack_pts = [
        (cx - 1 * s, cy - 14 * s),
        (cx + 2 * s, cy - 7 * s),
        (cx - 2 * s, cy - 1 * s),
        (cx + 3 * s, cy + 6 * s),
        (cx - 1 * s, cy + 12 * s),
    ]
    # Wide glow underlay
    glow_w = max(2, SS + 2)
    pygame.draw.lines(big, (235, 30, 40, 0), False, crack_pts, glow_w + 4 * s)
    # Layered glow (the actual visible warmth)
    for gw, col in (
        (glow_w + 3 * s, (235, 40, 50, 80)),
        (glow_w + 2 * s, (245, 70, 70, 140)),
        (glow_w + 1 * s, (255, 120, 110, 200)),
        (glow_w,         (255, 220, 200, 255)),
    ):
        tmp = pygame.Surface((big.get_width(), big.get_height()),
                             pygame.SRCALPHA)
        pygame.draw.lines(tmp, col, False, crack_pts, gw)
        big.blit(tmp, (0, 0))

    # Bright violet specular dot near the top — readable highlight
    pygame.draw.circle(big, (220, 200, 255),
                       (cx + 4 * s, cy - 11 * s), max(1, SS))

    # Pulsing red ember nub at the crack's brightest junction
    pulse_amt = 0.7 + 0.3 * (0.5 + 0.5 * math.sin(pulse * 4.5))
    ember_r = int(max(1, SS * 1.5 * pulse_amt))
    ember_surf = pygame.Surface((ember_r * 4, ember_r * 4), pygame.SRCALPHA)
    pygame.draw.circle(ember_surf, (255, 80, 70, 160),
                       (ember_r * 2, ember_r * 2), ember_r * 2)
    pygame.draw.circle(ember_surf, (255, 240, 220, 255),
                       (ember_r * 2, ember_r * 2), max(1, ember_r))
    big.blit(ember_surf, (crack_pts[2][0] - ember_r * 2,
                          crack_pts[2][1] - ember_r * 2))

    # Wisp of red smoke escaping the top of the crack
    for i, (dy, r, a) in enumerate(((-8, 2, 90), (-12, 3, 60), (-16, 4, 30))):
        sw = pygame.Surface((r * 2 * SS + 2, r * 2 * SS + 2), pygame.SRCALPHA)
        pygame.draw.circle(sw, (230, 80, 80, a),
                           (r * SS + 1, r * SS + 1), r * SS)
        big.blit(sw, (crack_pts[0][0] - r * SS + i * SS,
                      crack_pts[0][1] + dy * SS))

    surf.blit(_resolve(big, out_size, out_size), (0, 0))
    return surf


# ── Concept 4 — POISON VIAL ──────────────────────────────────────────
def draw_poison_vial(out_size: int, pulse: float) -> pygame.Surface:
    """Black-glass apothecary flask with sickly-green liquid bubbling
    inside, cork stopper, a square hazard label with an "X" (NOT a
    skull). Pale vapour wisps from the neck."""
    surf = pygame.Surface((out_size, out_size), pygame.SRCALPHA)
    _warning_glow_blit(surf, out_size // 2, out_size // 2 + 3, pulse,
                       color=(120, 220, 90))

    big = _ss_canvas(out_size, out_size)
    cx = out_size * SS // 2
    cy = out_size * SS // 2 + 3 * SS

    # Flask body — rounded shoulder + slight conical taper for hazard
    # silhouette. Built as a polygon with rounded corner emulation.
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
    # Glass outline (dark)
    pygame.draw.polygon(big, BLACK_DOME, body_pts)
    inner = [(int(p[0] * 0.92 + cx * 0.08),
              int(p[1] * 0.96 + cy * 0.04)) for p in body_pts]
    # Liquid fill — green up to ~70% of body
    fill_top_y = body_top + 9 * SS
    liquid_pts = [
        p for p in body_pts if p[1] >= fill_top_y
    ]
    # Insert top edge with a wavy meniscus
    meniscus = []
    seg_x_left = cx - 11 * SS
    seg_x_right = cx + 11 * SS
    for i in range(13):
        t = i / 12
        mx = int(seg_x_left + (seg_x_right - seg_x_left) * t)
        wave = math.sin(pulse * 2.2 + i * 0.9) * SS
        meniscus.append((mx, fill_top_y + int(wave)))
    liquid_poly = [meniscus[0]] + meniscus + [meniscus[-1]] + sorted(
        [p for p in body_pts if p[1] > fill_top_y],
        key=lambda q: (q[1], -q[0]))
    # Simpler — just clip body_pts to below fill_top_y then prepend meniscus
    below = [p for p in body_pts if p[1] > fill_top_y]
    # Reorder below clockwise from rightmost top to leftmost top
    right_below = sorted([p for p in below if p[0] >= cx],
                         key=lambda q: q[1])
    left_below = sorted([p for p in below if p[0] < cx],
                        key=lambda q: -q[1])
    liquid_outline = meniscus + right_below + left_below
    pygame.draw.polygon(big, GREEN_LO, liquid_outline)
    # Highlight ribbon along top of the meniscus
    pygame.draw.lines(big, GREEN_TOX, False, meniscus, max(1, SS // 2 + 1))
    # Lighter band partway down
    band_pts = [(p[0], p[1] + 4 * SS) for p in meniscus]
    pygame.draw.lines(big, (90, 160, 70), False, band_pts, max(1, SS // 2))

    # Bubbles inside the liquid — three small pale circles drifting up
    for i, (bx_off, by_off, br) in enumerate(((-4, 6, 2),
                                              (3, 9, 1),
                                              (-1, 3, 1))):
        drift = math.sin(pulse * 1.6 + i * 1.7) * SS
        pygame.draw.circle(big, (180, 240, 180, 220),
                           (cx + bx_off * SS, fill_top_y + by_off * SS
                            + int(drift)), br * SS)

    # Glass rim highlight on the left side
    pygame.draw.line(big, (90, 100, 120),
                     (cx - 11 * SS, body_top + 6 * SS),
                     (cx - 11 * SS, body_bottom - 5 * SS),
                     max(1, SS // 2 + 1))

    # Neck — narrow cylinder
    neck_rect = pygame.Rect(cx - 4 * SS, body_top - 5 * SS,
                            8 * SS, 6 * SS)
    pygame.draw.rect(big, BLACK_DOME, neck_rect)
    pygame.draw.rect(big, (40, 44, 56),
                     neck_rect.inflate(-2 * SS, -1 * SS))
    pygame.draw.line(big, (90, 100, 120),
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

    # Hazard label — small bone-coloured square with red "X"
    lbl_w, lbl_h = 12 * SS, 9 * SS
    lbl_rect = pygame.Rect(0, 0, lbl_w, lbl_h)
    lbl_rect.center = (cx, cy + 4 * SS)
    pygame.draw.rect(big, BLACK_DOME,
                     lbl_rect.inflate(2 * SS, 2 * SS),
                     border_radius=SS)
    pygame.draw.rect(big, (200, 200, 190), lbl_rect,
                     border_radius=SS)
    # Red X
    pygame.draw.line(big, (180, 25, 30),
                     (lbl_rect.left + 2 * SS, lbl_rect.top + 2 * SS),
                     (lbl_rect.right - 2 * SS, lbl_rect.bottom - 2 * SS),
                     max(2, SS))
    pygame.draw.line(big, (180, 25, 30),
                     (lbl_rect.right - 2 * SS, lbl_rect.top + 2 * SS),
                     (lbl_rect.left + 2 * SS, lbl_rect.bottom - 2 * SS),
                     max(2, SS))

    # Vapour wisps above cork
    for i, (dx, dy, r, a) in enumerate(((0, -14, 3, 90),
                                         (3, -19, 4, 60),
                                         (-2, -23, 5, 35))):
        drift = math.sin(pulse * 1.0 + i * 0.7) * SS
        pw = pygame.Surface((r * 2 * SS + 2, r * 2 * SS + 2),
                            pygame.SRCALPHA)
        pygame.draw.circle(pw, (170, 220, 160, a),
                           (r * SS + 1, r * SS + 1), r * SS)
        big.blit(pw, (cx + dx * SS + int(drift) - r * SS - 1,
                      cy + dy * SS - r * SS - 1))

    surf.blit(_resolve(big, out_size, out_size), (0, 0))
    return surf


# ── Concept 5 — TOMBSTONE ────────────────────────────────────────────
def draw_tombstone(out_size: int, pulse: float) -> pygame.Surface:
    """Squat RIP slab with a vertical crack, withered grass tuft, dark
    soil mound at the base. Tilt is baked into the silhouette so it
    reads even at the smallest size."""
    surf = pygame.Surface((out_size, out_size), pygame.SRCALPHA)
    _warning_glow_blit(surf, out_size // 2, out_size // 2 + 4, pulse,
                       color=(200, 70, 90))

    big = _ss_canvas(out_size, out_size)
    cx = out_size * SS // 2
    cy = out_size * SS // 2 + 2 * SS

    s = SS

    # Soil mound — wide dark ellipse with lighter top
    mound_rect = pygame.Rect(0, 0, 40 * s, 14 * s)
    mound_rect.center = (cx, cy + 14 * s)
    pygame.draw.ellipse(big, (28, 18, 10), mound_rect.inflate(2 * s, 2 * s))
    pygame.draw.ellipse(big, DIRT_LO, mound_rect)
    pygame.draw.ellipse(big, DIRT_HI,
                        pygame.Rect(mound_rect.left + 3 * s,
                                    mound_rect.top + 1 * s,
                                    mound_rect.width - 6 * s,
                                    4 * s))
    # Dirt clods — small dark dots
    for off_x in (-12, -5, 4, 10):
        pygame.draw.circle(big, (30, 18, 8),
                           (cx + off_x * s, cy + 14 * s), int(1.2 * s))

    # Slab — slightly tilted rounded-top rectangle.
    tilt_x = 2 * s   # whole slab leans right slightly
    slab_w, slab_h = 24 * s, 26 * s
    slab_left  = cx - slab_w // 2 + tilt_x
    slab_top   = cy - 16 * s
    slab_right = slab_left + slab_w
    slab_bot   = slab_top + slab_h

    # Rounded-top arch as polygon (semicircle + rect)
    arch_pts = []
    for ang_deg in range(180, 360 + 1, 10):
        ang = math.radians(ang_deg)
        ax = slab_left + slab_w // 2 + int(math.cos(ang) * slab_w / 2)
        ay = slab_top + slab_h // 4 + int(math.sin(ang) * slab_h / 4)
        arch_pts.append((ax, ay))
    body_pts = arch_pts + [
        (slab_right, slab_bot),
        (slab_left,  slab_bot),
    ]

    # Drop shadow
    shadow_pts = [(p[0] + 2 * s, p[1] + 3 * s) for p in body_pts]
    pygame.draw.polygon(big, (8, 8, 14), shadow_pts)

    # Stone fill — cool grey with a warm-top gradient feel
    pygame.draw.polygon(big, (62, 66, 82), body_pts)
    # Inner face (slightly lighter)
    inner_pts = [(p[0] + s, p[1] + s) for p in body_pts]
    pygame.draw.polygon(big, (90, 94, 108), inner_pts)
    # Top warmth band — a flatter ellipse at the dome
    warm = pygame.Rect(slab_left + 3 * s, slab_top + 2 * s,
                       slab_w - 6 * s, 4 * s)
    pygame.draw.ellipse(big, (130, 122, 130), warm)

    # Outline — purple-tinged so it reads ominous, not neutral
    pygame.draw.polygon(big, (40, 30, 60), body_pts, max(1, s + 1))

    # Vertical crack — zig-zag dark line
    crack_x = slab_left + slab_w // 2 - 3 * s
    crack_pts = [
        (crack_x,            slab_top + 4 * s),
        (crack_x + 2 * s,    slab_top + 9 * s),
        (crack_x - 1 * s,    slab_top + 14 * s),
        (crack_x + 2 * s,    slab_top + 19 * s),
        (crack_x - 1 * s,    slab_bot - 2 * s),
    ]
    pygame.draw.lines(big, (30, 24, 40), False, crack_pts, max(2, s + 1))
    pygame.draw.lines(big, (50, 44, 60), False,
                      [(p[0] + s, p[1] + 1) for p in crack_pts],
                      max(1, s // 2 + 1))

    # "RIP" carving — slim chiselled glyphs with a dark inset
    rip_y = slab_top + 8 * s
    rip_chars = [
        ('R', slab_left + 5 * s),
        ('I', slab_left + 11 * s),
        ('P', slab_left + 15 * s),
    ]
    for ch, x in rip_chars:
        # Background carved well
        if ch == 'I':
            rect = pygame.Rect(x, rip_y, 2 * s, 8 * s)
            pygame.draw.rect(big, (30, 24, 40), rect)
            pygame.draw.rect(big, (50, 44, 60),
                             rect.move(s // 2 + 1, 1), max(1, s // 2))
        elif ch == 'R':
            pts = [(x, rip_y), (x + 4 * s, rip_y),
                   (x + 5 * s, rip_y + 2 * s), (x + 4 * s, rip_y + 4 * s),
                   (x, rip_y + 4 * s), (x + 5 * s, rip_y + 8 * s),
                   (x + 3 * s, rip_y + 8 * s), (x + s, rip_y + 4 * s),
                   (x, rip_y + 4 * s)]
            pygame.draw.lines(big, (30, 24, 40), False, pts, max(2, s + 1))
        else:  # P
            pts = [(x, rip_y + 8 * s), (x, rip_y),
                   (x + 4 * s, rip_y), (x + 5 * s, rip_y + 2 * s),
                   (x + 4 * s, rip_y + 4 * s), (x, rip_y + 4 * s)]
            pygame.draw.lines(big, (30, 24, 40), False, pts, max(2, s + 1))

    # Withered grass tuft — sparse dry strands at the base
    for i, (gx, gh) in enumerate(((-15, 5), (-10, 7), (-6, 4),
                                   (8, 6), (12, 5), (16, 7))):
        sway = math.sin(pulse * 1.1 + i * 0.8) * s
        tip_x = cx + gx * s + int(sway)
        tip_y = cy + 12 * s - gh * s
        base_x = cx + gx * s
        base_y = cy + 12 * s
        pygame.draw.line(big, GRASS_DRY,
                         (base_x, base_y), (tip_x, tip_y), max(1, s // 2 + 1))
        pygame.draw.line(big, (160, 150, 90),
                         (base_x, base_y), (tip_x, tip_y), max(1, s // 2))

    # A tiny purple-ish wisp floating up — supernatural cue
    wisp_dy = -22 * s + int(math.sin(pulse * 0.9) * 2 * s)
    for i, (dx, r, a) in enumerate(((-2, 3, 90), (1, 4, 60), (-1, 5, 30))):
        pw = pygame.Surface((r * 2 * s + 2, r * 2 * s + 2),
                            pygame.SRCALPHA)
        pygame.draw.circle(pw, (170, 130, 200, a),
                           (r * s + 1, r * s + 1), r * s)
        big.blit(pw, (cx + dx * s - r * s - 1,
                      cy + wisp_dy + i * 3 * s - r * s - 1))

    surf.blit(_resolve(big, out_size, out_size), (0, 0))
    return surf


# ── Panel composition ───────────────────────────────────────────────
CONCEPTS = [
    ("BEAR TRAP",   draw_bear_trap,
     "iron jaws sprung — red 'armed' dot"),
    ("BOMB",        draw_bomb,
     "lit fuse + sparks + smoke curl"),
    ("CURSED GEM",  draw_cursed_gem,
     "obsidian shard, crack leaking red glow"),
    ("POISON VIAL", draw_poison_vial,
     "sickly green liquid, hazard 'X' label"),
    ("TOMBSTONE",   draw_tombstone,
     "RIP slab + soil mound + ghost wisp"),
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

    # Title bar
    _draw_label(sheet, "DEATH TRAP  —  Round 1", 16, 12, font_title)
    _draw_label(sheet,
                "five telegraphed-danger pickup concepts | "
                "native ~48 px | dawn-sky teal | 4x zoom for detail",
                16, 38, font_s, color=DIM)

    # Render each concept once at NATIVE size with a representative
    # pulse value; pulse picked per concept so spark/glow phases feel
    # alive, not frozen at zero.
    base_pulse = {
        "BEAR TRAP":   1.7,
        "BOMB":        2.4,
        "CURSED GEM":  1.1,
        "POISON VIAL": 0.5,
        "TOMBSTONE":   3.2,
    }

    for i, (name, fn, blurb) in enumerate(CONCEPTS):
        row = i
        panel_x = GUTTER
        panel_y = TITLE_H + row * (PANEL_H + GUTTER) + GUTTER
        rect = pygame.Rect(panel_x, panel_y, PANEL_W, PANEL_H)
        _panel_bg(sheet, rect)
        _draw_grid_dot(sheet, rect)

        # Concept heading
        _draw_label(sheet, f"{i + 1}.  {name}",
                    rect.left + 14, rect.top + 10, font_h)
        _draw_label(sheet, blurb,
                    rect.left + 14, rect.top + 30, font_s, color=DIM)

        # Left: at-size render (with bob applied — pickup is ~48 px footprint)
        icon = fn(NATIVE_PX, base_pulse[name])
        bob = int(math.sin(base_pulse[name] * 1.0) * 2)
        left_cx = rect.left + 70
        left_cy = rect.top + rect.height // 2 + 8 + bob
        # Add a small "in-world swatch" — dawn-sky disc behind the icon
        # so the wider panel BG doesn't bias legibility.
        swatch = pygame.Surface((84, 84), pygame.SRCALPHA)
        pygame.draw.circle(swatch, DAWN_TEAL, (42, 42), 42)
        pygame.draw.circle(swatch, (28, 32, 50), (42, 42), 42, 2)
        sheet.blit(swatch, (left_cx - 42, left_cy - 42))
        sheet.blit(icon, (left_cx - icon.get_width() // 2,
                          left_cy - icon.get_height() // 2))
        _draw_label(sheet, "in-world  48 px", left_cx - 38,
                    rect.bottom - 22, font_xs, color=DIM)

        # Right: 4× zoom
        zoomed = pygame.transform.scale(
            icon,
            (NATIVE_PX * ZOOM_FACTOR, NATIVE_PX * ZOOM_FACTOR),
        )
        right_cx = rect.right - 120
        right_cy = rect.top + rect.height // 2 + 6
        # Mounting tile background for the zoom
        z_rect = pygame.Rect(0, 0, NATIVE_PX * ZOOM_FACTOR + 16,
                             NATIVE_PX * ZOOM_FACTOR + 16)
        z_rect.center = (right_cx, right_cy)
        pygame.draw.rect(sheet, (18, 22, 34), z_rect, border_radius=6)
        pygame.draw.rect(sheet, GRID, z_rect, width=1, border_radius=6)
        sheet.blit(zoomed, (right_cx - zoomed.get_width() // 2,
                            right_cy - zoomed.get_height() // 2))
        _draw_label(sheet, "4x zoom",
                    z_rect.left + 6, z_rect.bottom + 4, font_xs, color=DIM)

    # Footer line
    footer = ("idle bob sin(pulse * ~1.0) * 2-3 px  "
              "|  no buff-y halo  |  warning glow only  "
              "|  procedural draw, no PNGs")
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
    out_path = os.path.join(out_dir, "round_1.png")
    pygame.image.save(sheet, out_path)
    print(out_path)


if __name__ == "__main__":
    main()
    sys.exit(0)
