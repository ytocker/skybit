"""Death-Trap pickup — Round 3 (final) exploration sheet.

Per the art-director's round-2 critique: BOMB and BUZZSAW are the ship
finalists; BEAR TRAP gets a paired-pressure-plate inner mechanism +
1-px tooth notches; CURSED GEM commits hard to a diamond/kite silhouette
with explicit facet edges; POISON VIAL is re-silhouetted as a chemistry
erlenmeyer flask (conical body, narrow neck) to break the GENIE-lamp
resemblance and avoid SKATEBOARD's Jolly Roger skull motif.

Calibration follows the per-panel halo overrides — CURSED GEM drops to
~140 alpha to stop the violet halo bleeding into the dark body; POISON
warms to ~190 so the red halo survives against the green flask.

WHY this lives in tools/ — final design sheet only, no production code
touched until the loop converges on a winner.
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
IRON_DARK  = (52,  56,  72)
IRON_MID   = (90,  96, 112)
IRON_HI    = (175, 184, 200)
RUST       = (180, 90, 40)
RUST_DEEP  = (130, 60, 28)
COPPER     = (200, 110,  55)
SAW_GREY   = (110, 100, 95)
SAW_GREY_HI = (160, 150, 140)
WOOD_DARK  = (60,  38,  22)
GREEN_TOX  = (120, 200,  90)
GREEN_LO   = (40,  100,  50)
GREEN_GLASS = (35, 90, 50)
VAPOR_HI   = (200, 224,  96)        # sickly yellow-green vapour
DIRT_LO    = (50,  32,  20)
DIRT_HI    = (110,  78,  46)
# Gem palette — commits hard to violet/magenta wound
GEM_BODY   = (20,  15,  30)
GEM_FACET  = (220, 190, 240)
FISSURE_HOT = (224,  48,  96)
# Bomb fuse — cooled away from amber to bone-gray + brass collar
FUSE_BONE   = (180, 175, 160)
FUSE_BONE_HI = (210, 205, 190)
BRASS_COLLAR = (180, 140,  60)


# ── Helpers ──────────────────────────────────────────────────────────
def _ss_canvas(w: int, h: int) -> pygame.Surface:
    return pygame.Surface((w * SS, h * SS), pygame.SRCALPHA)


def _resolve(big: pygame.Surface, w: int, h: int) -> pygame.Surface:
    return pygame.transform.smoothscale(big, (w, h))


def _radial_glow(radius: int, color, max_alpha: int = 160) -> pygame.Surface:
    """Soft circular glow — fades from max_alpha at the centre to 0 at
    the rim. Used as the warning halo around every pickup."""
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
                       halo_r: int = 16,
                       outer_alpha: int = 80) -> None:
    """Two-stop warning halo: a bright core that breathes, plus a wider
    faint outer halo. Per-panel calibration — CURSED GEM uses a lower
    alpha so the violet doesn't bleed into the near-black silhouette."""
    breath = 0.7 + 0.3 * (0.5 + 0.5 * math.sin(pulse_phase))
    outer = _radial_glow(halo_r, color, max_alpha=int(outer_alpha * breath))
    surf.blit(outer, (cx - outer.get_width() // 2,
                      cy - outer.get_height() // 2))
    inner = _radial_glow(core_r, color, max_alpha=int(core_alpha * breath))
    surf.blit(inner, (cx - inner.get_width() // 2,
                      cy - inner.get_height() // 2))


# ── Concept 1 — BEAR TRAP (paired pressure plates + notched teeth) ───
def draw_bear_trap(out_size: int, pulse: float) -> pygame.Surface:
    """Top-down sprung jaw-ring. Inner mechanism is now ASYMMETRIC paired
    pressure-plate halves split by a thin black gap (mechanical, not
    symmetric reticle). Rim teeth get 1-px black notches between them so
    the toothiness survives downscaling to 48 px on dawn-teal."""
    surf = pygame.Surface((out_size, out_size), pygame.SRCALPHA)
    _warning_glow_blit(surf, out_size // 2, out_size // 2 + 2,
                       pulse, color=(220, 70, 40),
                       core_alpha=170, core_r=13, halo_r=18)

    big = _ss_canvas(out_size, out_size)
    cx = out_size * SS // 2
    cy = out_size * SS // 2 + 1 * SS

    # Dirt mound base
    mound_rect = pygame.Rect(0, 0, 38 * SS, 9 * SS)
    mound_rect.center = (cx, cy + 14 * SS)
    pygame.draw.ellipse(big, (28, 18, 10), mound_rect.inflate(2 * SS, 2 * SS))
    pygame.draw.ellipse(big, DIRT_LO, mound_rect)
    pygame.draw.ellipse(big, DIRT_HI,
                        pygame.Rect(mound_rect.left + 4 * SS,
                                    mound_rect.top + SS,
                                    mound_rect.width - 8 * SS,
                                    2 * SS))

    # Outer jaw-ring oval (3/4 top-down)
    ring_w = 38 * SS
    ring_h = 30 * SS
    ring_rect = pygame.Rect(0, 0, ring_w, ring_h)
    ring_rect.center = (cx, cy)

    pygame.draw.ellipse(big, SHADOW,
                        ring_rect.move(2 * SS, 3 * SS).inflate(2 * SS, 2 * SS))

    # Tooth crown — 12 teeth with 1-px black notches between adjacent
    # teeth so the silhouette stays jagged at 48 px instead of mushing
    # into a smooth ring.
    n_teeth = 12
    rx = ring_w / 2
    ry = ring_h / 2
    tooth_outer = 1.20
    tooth_inner = 0.92
    notch_outer = 1.05
    notch_inner = 0.95
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
        # Light catch on tooth's outward facet (upper half)
        if math.sin(a1) < -0.1:
            pygame.draw.line(big, IRON_HI,
                             (int(p0[0]), int(p0[1])),
                             (int(p1[0]), int(p1[1])),
                             max(1, SS // 2 + 1))

    # 1-px black notch lines radiating between teeth — each notch goes
    # from a base point on the rim outward to a point just past the
    # tooth gap. Survives downscaling because it's a hard black line.
    for i in range(n_teeth):
        a_notch = (i / n_teeth) * math.tau - math.pi / 2
        base = (cx + math.cos(a_notch) * rx * notch_inner,
                cy + math.sin(a_notch) * ry * notch_inner)
        tip  = (cx + math.cos(a_notch) * rx * notch_outer,
                cy + math.sin(a_notch) * ry * notch_outer)
        pygame.draw.line(big, (2, 2, 6),
                         (int(base[0]), int(base[1])),
                         (int(tip[0]), int(tip[1])),
                         max(1, SS // 2 + 1))

    # Iron disc body — dark outer ring, lighter inner face
    pygame.draw.ellipse(big, IRON_DARK, ring_rect)
    pygame.draw.ellipse(big, IRON_MID,
                        ring_rect.inflate(-4 * SS, -4 * SS))
    pygame.draw.ellipse(big, (70, 76, 92),
                        ring_rect.inflate(-8 * SS, -8 * SS))

    # === Paired pressure-plate halves =================================
    # Asymmetric — right half slightly larger than left, split by a
    # thin (1 px native = SS supersample) black gap. Sells as a sprung
    # mechanism that snaps shut, not a reticle.
    plate_rect = pygame.Rect(0, 0, 22 * SS, 13 * SS)
    plate_rect.center = (cx, cy + SS)
    # Subtle shadow under the plate so it sits in the iron disc
    pygame.draw.ellipse(big, SHADOW,
                        plate_rect.move(0, SS).inflate(2 * SS, SS))

    # Left half — slightly smaller. Clip with a vertical line at the
    # split (offset right of centre by 1 px to make it asymmetric).
    split_x = cx + SS  # asymmetric split — right plate is bigger
    left_half = pygame.Surface(plate_rect.size, pygame.SRCALPHA)
    pygame.draw.ellipse(left_half, IRON_DARK,
                        pygame.Rect(0, 0, *plate_rect.size))
    pygame.draw.ellipse(left_half, (62, 66, 84),
                        pygame.Rect(SS, SS,
                                    plate_rect.width - 2 * SS,
                                    plate_rect.height - 2 * SS))
    # Mask the right half off this surface so we get the left lobe only
    mask_right = pygame.Surface(plate_rect.size, pygame.SRCALPHA)
    mask_right.fill((0, 0, 0, 0))
    pygame.draw.rect(mask_right, (0, 0, 0, 255),
                     pygame.Rect(split_x - plate_rect.left, 0,
                                 plate_rect.width, plate_rect.height))
    left_half.blit(mask_right, (0, 0),
                   special_flags=pygame.BLEND_RGBA_SUB)
    big.blit(left_half, plate_rect.topleft)

    # Right half — slightly larger (extends a hair past mirror centre)
    right_rect = plate_rect.copy()
    right_rect.width = plate_rect.right - split_x + SS  # bigger
    right_rect.left = split_x
    pygame.draw.ellipse(big, IRON_DARK, right_rect)
    pygame.draw.ellipse(big, (78, 82, 100),
                        right_rect.inflate(-2 * SS, -2 * SS))

    # The split gap — thin black line down the middle (1 px native)
    pygame.draw.line(big, (0, 0, 4),
                     (split_x, plate_rect.top + 1 * SS),
                     (split_x, plate_rect.bottom - 1 * SS),
                     max(1, SS // 2 + 1))

    # Hinge dot at the bottom of the split — sells the mechanism
    pygame.draw.circle(big, BLACK_DOME,
                       (split_x, plate_rect.bottom - 1 * SS),
                       max(2, SS))
    pygame.draw.circle(big, COPPER,
                       (split_x, plate_rect.bottom - 1 * SS),
                       max(1, SS - 1))

    # Top rim catches light — bright arc on top of the ring
    rim_rect = ring_rect.inflate(-SS, -SS)
    pygame.draw.arc(big, IRON_HI, rim_rect,
                    math.radians(200), math.radians(340), max(1, SS))

    # Tiny pulsing red "armed" pip on the right (bigger) plate to keep
    # the visual heat in the mechanism without going central
    armed_phase = 0.55 + 0.45 * (0.5 + 0.5 * math.sin(pulse * 3.0))
    arm_col = (int(210 + 45 * armed_phase), 35, 35)
    pip_pos = (split_x + 6 * SS, cy + SS)
    pygame.draw.circle(big, BLACK_DOME, pip_pos, int(1.8 * SS))
    pygame.draw.circle(big, arm_col, pip_pos, int(1.1 * SS))

    surf.blit(_resolve(big, out_size, out_size), (0, 0))
    return surf


# ── Concept 2 — BOMB (finishing polish: bone fuse + brass collar) ────
def draw_bomb(out_size: int, pulse: float) -> pygame.Surface:
    """Round cast-iron bomb. Final polish on the lead:
    - 2-px white-hot spark core with a 1-px orange offset pixel so the
      tip survives downscaling on dawn-teal.
    - Bone-gray fuse stem with a brass collar at the base where the
      fuse meets the sphere — cools the palette away from GENIE amber.
    - Single 1-px upper-left highlight dot on the sphere (NOT a sheen
      arc) to sell roundness without going glossy."""
    surf = pygame.Surface((out_size, out_size), pygame.SRCALPHA)
    _warning_glow_blit(surf, out_size // 2, out_size // 2 + 6, pulse,
                       color=(245, 110, 40),
                       core_alpha=175, core_r=14, halo_r=19)

    big = _ss_canvas(out_size, out_size)
    cx = out_size * SS // 2
    cy = out_size * SS // 2 + 4 * SS

    body_r = 14 * SS

    # Soft red rim-glow disc beneath the bomb
    rim_glow = _radial_glow(int(body_r * 1.45),
                            (230, 50, 50), max_alpha=110)
    big.blit(rim_glow,
             (cx - rim_glow.get_width() // 2,
              cy + 4 * SS - rim_glow.get_height() // 2))

    # Contact shadow on the dirt
    shadow_rect = pygame.Rect(0, 0, int(body_r * 1.9), int(body_r * 0.55))
    shadow_rect.center = (cx, cy + body_r + 2 * SS)
    sh = pygame.Surface(shadow_rect.size, pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (0, 0, 0, 140),
                        pygame.Rect(0, 0, *shadow_rect.size))
    big.blit(sh, shadow_rect.topleft)

    # Cast-iron body — outer rim shadow, dome black
    pygame.draw.circle(big, SHADOW,     (cx, cy + 2 * SS), body_r + 2 * SS)
    pygame.draw.circle(big, BLACK_DOME, (cx, cy), body_r + SS)
    pygame.draw.circle(big, (32, 32, 44), (cx, cy), body_r)

    # === Single 1-px upper-left highlight DOT (not a sheen arc) =======
    # Lives at ~45 deg above-left of centre, low alpha to read as
    # rounding cue, not as a glossy plastic bauble.
    hl = pygame.Surface((4 * SS, 4 * SS), pygame.SRCALPHA)
    pygame.draw.circle(hl, (220, 220, 235, 120),
                       (2 * SS, 2 * SS), max(1, SS))
    big.blit(hl, (cx - int(body_r * 0.55) - SS,
                  cy - int(body_r * 0.55) - SS))

    # === Brass collar where fuse meets sphere =========================
    # Short thick ring just above the dome top — explicitly metallic.
    collar_w, collar_h = 10 * SS, 3 * SS
    collar_rect = pygame.Rect(cx - collar_w // 2,
                              cy - body_r - 1 * SS,
                              collar_w, collar_h)
    pygame.draw.rect(big, (90, 60, 24), collar_rect, border_radius=SS)
    pygame.draw.rect(big, BRASS_COLLAR,
                     collar_rect.inflate(-SS, -SS), border_radius=SS // 2 + 1)
    # Brass highlight band
    pygame.draw.line(big, (240, 200, 110),
                     (collar_rect.left + 2 * SS,
                      collar_rect.top + SS),
                     (collar_rect.right - 2 * SS,
                      collar_rect.top + SS),
                     max(1, SS // 2))

    # === Bone-gray fuse stem (NO amber) ===============================
    fuse_base = (cx, collar_rect.top + SS)
    fuse_pts = [
        fuse_base,
        (cx - 2 * SS, cy - body_r - 4 * SS),
        (cx + 3 * SS, cy - body_r - 9 * SS),
        (cx - 1 * SS, cy - body_r - 13 * SS),
        (cx + 4 * SS, cy - body_r - 16 * SS),
    ]
    pygame.draw.lines(big, (60, 58, 50), False, fuse_pts, 3 * SS)
    pygame.draw.lines(big, FUSE_BONE, False, fuse_pts, max(1, SS + 1))
    pygame.draw.lines(big, FUSE_BONE_HI, False, fuse_pts[:3],
                      max(1, SS // 2))

    tip = fuse_pts[-1]
    flick = 0.7 + 0.3 * (0.5 + 0.5 * math.sin(pulse * 6.5))

    # === Spark — 2-px white-hot core + 1-px orange offset =============
    # Orange halo BEHIND the white-hot core so the tip reads "LIT" but
    # the bright pixel survives the smoothscale.
    for r, col in (
        (int(7 * SS * flick), (255, 130, 30, 130)),
        (int(5 * SS * flick), (255, 180, 70, 200)),
        (int(3 * SS * flick), (255, 230, 160, 240)),
    ):
        eg = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(eg, col, (r + 2, r + 2), max(1, r))
        big.blit(eg, (tip[0] - r - 2, tip[1] - r - 2))
    # Orange pixel offset (1 px native = SS supersample) — placed just
    # below-right of the white core so downscale leaves a 2-tone tip
    pygame.draw.circle(big, (255, 165, 60),
                       (tip[0] + SS, tip[1] + SS), max(2, int(SS * 1.2)))
    # White-hot core (2 px native ≈ 2*SS supersample)
    pygame.draw.circle(big, (255, 255, 245), tip, max(2, int(SS * 1.6)))

    # Spark dots flying off the tip
    spark_angles = (30, 110, 200, 290)
    for i, ang_deg in enumerate(spark_angles):
        ang = math.radians(ang_deg + pulse * 25)
        dist = (6 + (i % 2) * 3) * SS * flick
        sx = tip[0] + int(math.cos(ang) * dist)
        sy = tip[1] + int(math.sin(ang) * dist)
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


# ── Concept 3 — CURSED GEM (committed kite + facet edges) ────────────
def draw_cursed_gem(out_size: int, pulse: float) -> pygame.Surface:
    """Tilted asymmetric kite/diamond — 4 hard corners, taller than
    wide, rotated ~15 deg so it does not read as a UI close-button.
    Two of the four facet edges get 1-px pale-violet highlights so the
    crystal geometry survives at 48 px. Single hot-magenta fissure down
    the long axis; the perpendicular crack is demoted to a hint. Outer
    halo is dropped to ~140 alpha so the violet doesn't bleed into and
    mush the near-black silhouette."""
    surf = pygame.Surface((out_size, out_size), pygame.SRCALPHA)
    # NB: lower outer-halo alpha per critique — halo was bleeding
    _warning_glow_blit(surf, out_size // 2, out_size // 2 + 2, pulse,
                       color=(180, 60, 120),
                       core_alpha=140, core_r=12, halo_r=16,
                       outer_alpha=55)

    big = _ss_canvas(out_size, out_size)
    cx = out_size * SS // 2
    cy = out_size * SS // 2 + 1 * SS

    s = SS

    # === Tilted kite — taller than wide, rotated ~15 degrees =========
    # Define the 4 corners as offsets from centre, then rotate.
    raw = [
        (0,        -19),   # top apex
        (12,        -2),   # right corner (slightly above middle)
        (3,         18),   # bottom apex (slightly off-axis = asymmetry)
        (-13,       -4),   # left corner
    ]
    theta = math.radians(15.0)
    ct, st_ = math.cos(theta), math.sin(theta)
    pts = []
    for dx, dy in raw:
        rx = dx * ct - dy * st_
        ry = dx * st_ + dy * ct
        pts.append((cx + int(rx * s), cy + int(ry * s)))
    top_p, right_p, bot_p, left_p = pts

    # Drop shadow
    shadow = [(p[0] + 2 * s, p[1] + 3 * s) for p in pts]
    pygame.draw.polygon(big, (2, 0, 8), shadow)

    # Near-black gem body
    pygame.draw.polygon(big, GEM_BODY, pts)

    # Subtle inner facet split — line from top apex to bottom apex
    # creates 2 visible halves; we tint the left face slightly lighter
    left_face = [top_p, left_p, bot_p]
    pygame.draw.polygon(big, (32, 22, 50), left_face)

    # === 1-px bright facet edges on the two light-catching edges =====
    # The "light" comes from the upper-left, so the top-left edge and
    # the top-right edge catch — those are top->left and top->right.
    pygame.draw.line(big, GEM_FACET, top_p, left_p, max(1, s // 2 + 1))
    pygame.draw.line(big, GEM_FACET, top_p, right_p, max(1, s // 2 + 1))
    # Dim violet rim on the lower edges so the silhouette reads sharp
    pygame.draw.line(big, (70, 35, 95), bot_p, left_p, max(1, s // 2 + 1))
    pygame.draw.line(big, (70, 35, 95), bot_p, right_p, max(1, s // 2 + 1))

    # === Main fissure: hot magenta down the long axis ================
    # Long axis runs from top_p to bot_p; add a jagged kink mid-way.
    midx = (top_p[0] + bot_p[0]) / 2
    midy = (top_p[1] + bot_p[1]) / 2
    kink = (int(midx - 2 * s), int(midy + 1 * s))
    fissure_pts = [
        (top_p[0] + int(2 * s * ct),
         top_p[1] + int(2 * s * st_)),                # just inside apex
        (int(midx + 1 * s), int(midy - 2 * s)),
        kink,
        (int(midx + 2 * s), int(midy + 4 * s)),
        (bot_p[0] - int(1 * s * ct),
         bot_p[1] - int(1 * s * st_)),
    ]

    def _paint_fissure(pts_, layers):
        for gw, col in layers:
            tmp = pygame.Surface((big.get_width(), big.get_height()),
                                 pygame.SRCALPHA)
            pygame.draw.lines(tmp, col, False, pts_, gw)
            big.blit(tmp, (0, 0))

    _paint_fissure(fissure_pts, (
        (int(s * 3.4), (*FISSURE_HOT, 110)),
        (int(s * 2.2), (240, 90, 140, 170)),
        (int(s * 1.3), (255, 160, 200, 210)),
        (max(1, s // 2 + 1), (255, 235, 245, 255)),
    ))

    # Demoted perpendicular crack — short hairline cut off the kink,
    # MUCH lower alpha so it reads as a hint not a co-equal stroke.
    perp_pts = [
        kink,
        (kink[0] + 5 * s, kink[1] - 3 * s),
        (kink[0] + 8 * s, kink[1] - 5 * s),
    ]
    _paint_fissure(perp_pts, (
        (int(s * 1.8), (180, 60, 120, 80)),
        (max(1, s // 2 + 1), (240, 180, 210, 130)),
    ))

    # Pulsing ember at the kink — wound's heart
    pulse_amt = 0.7 + 0.3 * (0.5 + 0.5 * math.sin(pulse * 4.5))
    ember_r = int(max(1, s * 1.6 * pulse_amt))
    ember_surf = pygame.Surface((ember_r * 4, ember_r * 4), pygame.SRCALPHA)
    pygame.draw.circle(ember_surf, (240, 80, 140, 180),
                       (ember_r * 2, ember_r * 2), ember_r * 2)
    pygame.draw.circle(ember_surf, (255, 240, 245, 255),
                       (ember_r * 2, ember_r * 2), max(1, ember_r))
    big.blit(ember_surf, (kink[0] - ember_r * 2,
                          kink[1] - ember_r * 2))

    # Two sparse 1-px corner glints on light-catching corners
    pygame.draw.circle(big, (240, 220, 250),
                       (top_p[0] + s, top_p[1] + s), max(1, s))
    pygame.draw.circle(big, (220, 200, 240),
                       (left_p[0] + s, left_p[1]), max(1, s - 1))

    surf.blit(_resolve(big, out_size, out_size), (0, 0))
    return surf


# ── Concept 4 — ERLENMEYER FLASK (re-silhouetted from vial) ──────────
def draw_poison_flask(out_size: int, pulse: float) -> pygame.Surface:
    """Chemistry erlenmeyer flask: wide conical base narrowing to a
    short vertical neck with a small cork. The conical body is the
    key — it exists nowhere else in the pickup set and breaks the
    GENIE-lamp resemblance. Red X painted directly on the conical
    glass; vapour is pushed to sickly yellow-green so it pops off the
    liquid body. Halo at ~190 alpha because the green body absorbs the
    red warning halo more than the other panels."""
    surf = pygame.Surface((out_size, out_size), pygame.SRCALPHA)
    _warning_glow_blit(surf, out_size // 2, out_size // 2 + 4, pulse,
                       color=(235, 50, 50),
                       core_alpha=190, core_r=14, halo_r=19,
                       outer_alpha=95)

    big = _ss_canvas(out_size, out_size)
    cx = out_size * SS // 2
    cy = out_size * SS // 2 + 4 * SS

    # === Conical body — wide flat bottom, narrow neck =================
    base_y     = cy + 16 * SS
    shoulder_y = cy - 2 * SS    # where cone meets neck
    neck_top_y = shoulder_y - 6 * SS
    base_half  = 14 * SS        # half-width at bottom
    shoulder_half = 4 * SS      # half-width at neck base
    # Conical trapezoid — true cone profile, NO rounded shoulders.
    body_pts = [
        (cx - shoulder_half, shoulder_y),
        (cx - base_half,     base_y - 2 * SS),
        (cx - base_half + 2 * SS, base_y),     # foot bevel L
        (cx + base_half - 2 * SS, base_y),     # foot bevel R
        (cx + base_half,     base_y - 2 * SS),
        (cx + shoulder_half, shoulder_y),
    ]
    # Glass outline
    pygame.draw.polygon(big, BLACK_DOME, body_pts)
    # Dark-green tinted glass interior
    inner_pts = [
        (cx - shoulder_half + SS, shoulder_y + SS),
        (cx - base_half + SS,     base_y - 3 * SS),
        (cx - base_half + 3 * SS, base_y - SS),
        (cx + base_half - 3 * SS, base_y - SS),
        (cx + base_half - SS,     base_y - 3 * SS),
        (cx + shoulder_half - SS, shoulder_y + SS),
    ]
    pygame.draw.polygon(big, GREEN_GLASS, inner_pts)

    # === Liquid fill — green up to ~65% of cone height ===============
    # Liquid level higher than the neck base so the conical "load" reads.
    fill_top_y = shoulder_y + 7 * SS
    # Wavy meniscus across the cone's interior width at that height
    t_fill = (fill_top_y - shoulder_y) / (base_y - shoulder_y)
    fill_left_x  = cx - int(shoulder_half + (base_half - shoulder_half) * t_fill) + SS
    fill_right_x = cx + int(shoulder_half + (base_half - shoulder_half) * t_fill) - SS
    meniscus = []
    for i in range(15):
        t = i / 14
        mx = int(fill_left_x + (fill_right_x - fill_left_x) * t)
        wave = math.sin(pulse * 2.2 + i * 0.9) * (SS // 2 + 1)
        meniscus.append((mx, fill_top_y + int(wave)))
    # Liquid polygon — meniscus across the top, cone walls down to base
    liquid_pts = (
        meniscus
        + [(cx + base_half - SS,     base_y - 3 * SS),
           (cx + base_half - 3 * SS, base_y - SS),
           (cx - base_half + 3 * SS, base_y - SS),
           (cx - base_half + SS,     base_y - 3 * SS)]
    )
    pygame.draw.polygon(big, GREEN_LO, liquid_pts)
    # Bright meniscus line
    pygame.draw.lines(big, GREEN_TOX, False, meniscus, max(1, SS // 2 + 1))
    # Darker band below meniscus
    band_pts = [(p[0], p[1] + 3 * SS) for p in meniscus]
    pygame.draw.lines(big, (90, 160, 70), False, band_pts, max(1, SS // 2))

    # Bubbles inside the liquid
    for i, (bx_off, by_off, br) in enumerate(((-4, 5, 2),
                                              (3, 8, 1),
                                              (-1, 11, 1))):
        drift = math.sin(pulse * 1.6 + i * 1.7) * SS
        pygame.draw.circle(big, (180, 240, 180, 220),
                           (cx + bx_off * SS,
                            fill_top_y + by_off * SS + int(drift)),
                           br * SS)

    # Glass rim highlight — straight line down the left cone wall
    pygame.draw.line(big, (90, 170, 110),
                     (cx - shoulder_half + SS, shoulder_y + 2 * SS),
                     (cx - base_half + 2 * SS, base_y - 3 * SS),
                     max(1, SS // 2 + 1))

    # === Narrow vertical neck =========================================
    neck_rect = pygame.Rect(cx - 4 * SS, neck_top_y + SS,
                            8 * SS, shoulder_y - neck_top_y)
    pygame.draw.rect(big, BLACK_DOME, neck_rect)
    pygame.draw.rect(big, (30, 60, 40),
                     neck_rect.inflate(-2 * SS, 0))
    pygame.draw.line(big, (90, 170, 110),
                     (neck_rect.left + SS, neck_rect.top + SS),
                     (neck_rect.left + SS, neck_rect.bottom - SS),
                     max(1, SS // 2))

    # Small cork at the top
    cork_rect = pygame.Rect(cx - 5 * SS, neck_top_y - 4 * SS,
                            10 * SS, 5 * SS)
    pygame.draw.rect(big, WOOD_DARK, cork_rect, border_radius=SS)
    pygame.draw.rect(big, (170, 110, 60),
                     cork_rect.inflate(-2 * SS, -SS), border_radius=SS)
    pygame.draw.line(big, (220, 170, 110),
                     (cork_rect.left + 2 * SS, cork_rect.top + SS),
                     (cork_rect.right - 2 * SS, cork_rect.top + SS),
                     max(1, SS // 2))

    # === RED X painted directly on the conical glass =================
    # Place on the cone (between meniscus and base — the wide part).
    x_arm_w = 3 * SS
    x_cx = cx
    x_cy = (fill_top_y + base_y) // 2 - SS
    x_reach = 6 * SS
    # Dark backing
    pygame.draw.line(big, (40, 5, 8),
                     (x_cx - x_reach - SS, x_cy - x_reach - SS),
                     (x_cx + x_reach + SS, x_cy + x_reach + SS),
                     x_arm_w + 2)
    pygame.draw.line(big, (40, 5, 8),
                     (x_cx + x_reach + SS, x_cy - x_reach - SS),
                     (x_cx - x_reach - SS, x_cy + x_reach + SS),
                     x_arm_w + 2)
    pygame.draw.line(big, (220, 35, 45),
                     (x_cx - x_reach, x_cy - x_reach),
                     (x_cx + x_reach, x_cy + x_reach),
                     x_arm_w)
    pygame.draw.line(big, (220, 35, 45),
                     (x_cx + x_reach, x_cy - x_reach),
                     (x_cx - x_reach, x_cy + x_reach),
                     x_arm_w)
    # Tiny spec sells "painted"
    pygame.draw.line(big, (255, 130, 130),
                     (x_cx - x_reach + SS, x_cy - x_reach + SS // 2),
                     (x_cx - x_reach + 3 * SS, x_cy - x_reach + 2 * SS),
                     max(1, SS // 2))

    # === Vapour puffs — sickly yellow-green (NOT same as liquid) =====
    puffs = (
        (-1, -10, 4, 170),
        (2,  -16, 5, 130),
        (-2, -22, 6, 85),
    )
    for i, (dx, dy, r, a) in enumerate(puffs):
        drift = math.sin(pulse * 1.0 + i * 0.7) * SS
        pw = pygame.Surface((r * 2 * SS + 2, r * 2 * SS + 2),
                            pygame.SRCALPHA)
        pygame.draw.circle(pw, (*VAPOR_HI, a),
                           (r * SS + 1, r * SS + 1), r * SS)
        if i < 2:
            pygame.draw.circle(pw, (230, 240, 150,
                                    min(255, a + 50)),
                               (r * SS + 1 - SS, r * SS + 1 - SS),
                               max(1, r * SS - 2 * SS))
        big.blit(pw, (cx + dx * SS + int(drift) - r * SS - 1,
                      cork_rect.top + dy * SS - r * SS - 1))

    surf.blit(_resolve(big, out_size, out_size), (0, 0))
    return surf


# ── Concept 5 — BUZZSAW (finishing polish: less rust, sharper teeth) ─
def draw_buzzsaw(out_size: int, pulse: float) -> pygame.Surface:
    """Rusty circular sawblade. Final polish:
    - Rust patches reduced to ~25% disc area (2-3 patches only) so the
      cool iron-gray dominates.
    - 1-px black notches between teeth so the jagged silhouette stays
      sharp at 48 px on dawn-teal.
    - Two short bright 1-px tangent streaks at disc edge (motion arcs
      baked stronger — kept because they paint cleanly).
    - Hub bolt darker than the disc body so it doesn't compete with
      the teeth as a focal point."""
    surf = pygame.Surface((out_size, out_size), pygame.SRCALPHA)
    _warning_glow_blit(surf, out_size // 2, out_size // 2, pulse,
                       color=(235, 40, 50),
                       core_alpha=170, core_r=14, halo_r=19)

    big = _ss_canvas(out_size, out_size)
    cx = out_size * SS // 2
    cy = out_size * SS // 2

    spin = pulse * 0.6

    blade_r_outer = 16 * SS
    blade_r_inner = 13 * SS
    n_teeth = 10

    # Drop shadow under the blade
    sh_rect = pygame.Rect(0, 0, int(blade_r_outer * 2 * 0.9),
                          int(blade_r_outer * 0.5))
    sh_rect.center = (cx + 2 * SS, cy + 3 * SS)
    sh = pygame.Surface(sh_rect.size, pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (0, 0, 0, 130),
                        pygame.Rect(0, 0, *sh_rect.size))
    big.blit(sh, sh_rect.topleft)

    # === Teeth drawn first ===========================================
    tooth_records = []   # remember tooth base points for notch lines
    for i in range(n_teeth):
        a0 = (i / n_teeth) * math.tau + spin
        a1 = ((i + 0.45) / n_teeth) * math.tau + spin
        a2 = ((i + 0.9) / n_teeth) * math.tau + spin
        p0 = (cx + math.cos(a0) * blade_r_inner,
              cy + math.sin(a0) * blade_r_inner)
        p1 = (cx + math.cos(a1) * blade_r_outer,
              cy + math.sin(a1) * blade_r_outer)
        p2 = (cx + math.cos(a2) * blade_r_inner,
              cy + math.sin(a2) * blade_r_inner)
        tri = [(int(p[0]), int(p[1])) for p in (p0, p1, p2)]
        pygame.draw.polygon(big, SAW_GREY, tri)
        pygame.draw.line(big, SAW_GREY_HI,
                         (int(p0[0]), int(p0[1])),
                         (int(p1[0]), int(p1[1])),
                         max(1, SS // 2 + 1))
        pygame.draw.line(big, IRON_DARK,
                         (int(p1[0]), int(p1[1])),
                         (int(p2[0]), int(p2[1])),
                         max(1, SS // 2))
        tooth_records.append((p0, p2))

    # === 1-px black notches between adjacent teeth ====================
    # Each gap sits between this tooth's p2 (trailing) and the next
    # tooth's p0 (leading). Draw a short radial black line down into
    # the disc to keep the silhouette jagged after downscaling.
    for i in range(n_teeth):
        _, p2 = tooth_records[i]
        p0_next, _ = tooth_records[(i + 1) % n_teeth]
        # Midpoint of the gap, pulled slightly inward
        gap_mid_x = (p2[0] + p0_next[0]) / 2
        gap_mid_y = (p2[1] + p0_next[1]) / 2
        # Inward target (toward disc centre, slightly inside rim)
        vx = cx - gap_mid_x
        vy = cy - gap_mid_y
        vlen = math.hypot(vx, vy) or 1.0
        inset = 2.5 * SS
        ix = gap_mid_x + vx / vlen * inset
        iy = gap_mid_y + vy / vlen * inset
        pygame.draw.line(big, (2, 2, 6),
                         (int(gap_mid_x), int(gap_mid_y)),
                         (int(ix), int(iy)),
                         max(1, SS // 2 + 1))

    # === Blade body — iron disc =====================================
    body_rect = pygame.Rect(0, 0, blade_r_inner * 2, blade_r_inner * 2)
    body_rect.center = (cx, cy)
    pygame.draw.ellipse(big, IRON_DARK,
                        body_rect.inflate(2 * SS, 2 * SS))
    pygame.draw.ellipse(big, SAW_GREY, body_rect)
    pygame.draw.ellipse(big, SAW_GREY_HI,
                        body_rect.inflate(-3 * SS, -3 * SS))

    # === Rust patches — only 3 patches now ============================
    rust_patches = (
        (0.5,  0.55, 5, 4),
        (2.9,  0.50, 4, 3),
        (4.8,  0.58, 4, 3),
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

    # Concentric scoring rings — turning marks
    for r_fac in (0.85, 0.65, 0.4):
        ring_rect = body_rect.inflate(
            -int(blade_r_inner * 2 * (1 - r_fac)),
            -int(blade_r_inner * 2 * (1 - r_fac)),
        )
        pygame.draw.ellipse(big, (140, 130, 120), ring_rect,
                            max(1, SS // 2))

    # === Hub — DARKER than disc so teeth stay the focal point ========
    hub_r = 4 * SS
    pygame.draw.circle(big, (28, 30, 40), (cx, cy), hub_r + SS)
    pygame.draw.circle(big, (50, 54, 70), (cx, cy), hub_r)
    pygame.draw.circle(big, (90, 96, 112),
                       (cx - SS, cy - SS), max(1, SS))
    # Centre mounting hole
    pygame.draw.circle(big, BLACK_DOME, (cx, cy), int(1.6 * SS))
    # Hex bolt suggestion — tick marks
    for tick_a in (0, math.tau / 3, 2 * math.tau / 3):
        a = tick_a + spin
        tx0 = cx + int(math.cos(a) * SS * 1.6)
        ty0 = cy + int(math.sin(a) * SS * 1.6)
        tx1 = cx + int(math.cos(a) * SS * 2.6)
        ty1 = cy + int(math.sin(a) * SS * 2.6)
        pygame.draw.line(big, (20, 22, 30), (tx0, ty0), (tx1, ty1),
                         max(1, SS // 2))

    # === Motion arcs — two short 1-px tangent streaks at the disc edge
    # Painted brighter / shorter so the streak survives downscaling.
    motion_surf = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    for arc_off, arc_len, alpha in (
        (0.5, 0.55, 150),
        (3.6, 0.45, 130),
    ):
        start_a = arc_off + spin
        end_a = start_a + arc_len
        arc_rect = pygame.Rect(0, 0, int(blade_r_outer * 2.30),
                                int(blade_r_outer * 2.30))
        arc_rect.center = (cx, cy)
        pygame.draw.arc(motion_surf, (255, 255, 255, alpha), arc_rect,
                        start_a, end_a, max(1, SS // 2 + 1))
    big.blit(motion_surf, (0, 0))

    surf.blit(_resolve(big, out_size, out_size), (0, 0))
    return surf


# ── Panel composition ───────────────────────────────────────────────
CONCEPTS = [
    ("BEAR TRAP",   draw_bear_trap,
     "asymmetric paired pressure-plates + 1-px tooth notches"),
    ("BOMB",        draw_bomb,
     "bone-gray fuse + brass collar | 2-px white-hot core + orange offset"),
    ("CURSED GEM",  draw_cursed_gem,
     "tilted kite (~15deg), facet edges, hot-magenta fissure, dimmer halo"),
    ("ERLENMEYER",  draw_poison_flask,
     "conical chemistry flask, red X on glass, yellow-green vapour"),
    ("BUZZSAW",     draw_buzzsaw,
     "iron-dominant disc, 3 rust patches, 1-px tooth notches, sharp arcs"),
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

    _draw_label(sheet, "DEATH TRAP  —  Round 3 (final)",
                16, 12, font_title)
    _draw_label(sheet,
                "per-panel halo calibration | GEM committed to kite | "
                "VIAL re-silhouetted as erlenmeyer | BOMB fuse cooled",
                16, 38, font_s, color=DIM)

    base_pulse = {
        "BEAR TRAP":  1.7,
        "BOMB":       2.4,
        "CURSED GEM": 1.1,
        "ERLENMEYER": 0.5,
        "BUZZSAW":    2.0,
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

    footer = ("final round | halo per-panel: BOMB/BUZZSAW/TRAP ~170, "
              "GEM ~140 (dimmer), FLASK ~190 | judged at 48 px first")
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
    out_path = os.path.join(out_dir, "round_3.png")
    pygame.image.save(sheet, out_path)
    print(out_path)


if __name__ == "__main__":
    main()
    sys.exit(0)
