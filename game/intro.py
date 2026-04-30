"""
Skybit intro cinematic — a calm 12-second journey that introduces Pip, his
employer Mr. Garrick, and the day-cycle world before the menu fades in.

Played once on first launch (gated by the `intro_seen` flag in
`skybit_save.json`), and skippable on any tap/click/key.

Everything is drawn procedurally with the same primitives the game uses, so
the cut into the menu is seamless. No new asset files. No new dependencies.

Composition is structured as five gentle beats dispatched by elapsed-time:
  0.0–1.0   "Dawn"       – clear-day post-house with parcel waiting
  1.0–4.0   "Hand-off"   – Pip glides in, takes parcel from doorstep
  4.0–9.0   "Journey"    – flight through golden hour → sunset → night
  9.0–11.0  "Arrival"    – Pip glides in to a starlit home, delivers
  11.0–12.0 "Title"      – Skybit logotype + "TAP TO FLY"

The brief asks for an MP4 deliverable; this codebase has no video pipeline,
so we ship the in-engine cinematic and let downstream marketing record it
externally if a literal MP4 is needed.
"""
from __future__ import annotations

import math
import random
import pygame

from game.config import W, H, GROUND_Y
from game.draw import (
    get_sky_surface_biome, draw_mountains, draw_cloud, draw_ground,
    blit_glow, lerp_color, rounded_rect_grad,
    UI_GOLD, UI_CREAM, WHITE, NEAR_BLACK,
)
from game import biome as _biome
from game import parrot as _parrot
from game.pillar_variants import draw_pillar_pair
from game.hud import _font


DURATION = 12.0


# ── small easing helpers ─────────────────────────────────────────────────────

def _clamp01(x: float) -> float:
    return 0.0 if x < 0.0 else (1.0 if x > 1.0 else x)


def _smoothstep(t: float) -> float:
    t = _clamp01(t)
    return t * t * (3.0 - 2.0 * t)


def _ease_out_cubic(t: float) -> float:
    t = _clamp01(t)
    inv = 1.0 - t
    return 1.0 - inv * inv * inv


# ── procedural sprites (built lazily, then cached) ───────────────────────────

_SPRITES: dict = {}


def _build_parcel() -> pygame.Surface:
    """A wrapped-present courier package: kraft-tan box with a red ribbon
    cross and a red bow. Ported from v2_skybit's surprise-box drawing
    geometry but with the question-mark glyph stripped out and a courier
    colour palette."""
    BOX_BASE   = (180, 130,  80)   # warm kraft tan
    BOX_SHADE  = (110,  75,  40)
    BOX_HI     = (220, 175, 120)
    RIBBON     = (200,  50,  60)
    RIBBON_HI  = (255, 110, 100)
    BOW_FILL   = (200,  50,  60)
    BOW_HI     = (255, 130, 120)
    DK_OUTLINE = ( 26,  10,  12)

    SIZE = 56
    surf = pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)

    BOX_W, BOX_H = 40, 34
    cx, cy = SIZE // 2, SIZE // 2 + 2
    rect = pygame.Rect(cx - BOX_W // 2, cy - BOX_H // 2 + 2, BOX_W, BOX_H)

    # Drop shadow
    sh = pygame.Surface((BOX_W + 8, 10), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (8, 4, 22, 130), sh.get_rect())
    surf.blit(sh, (cx - (BOX_W + 8) // 2, rect.bottom - 4))

    # Box body: dark frame, vertical-gradient fill, top sheen — same trick
    # as the surprise-box reference.
    pygame.draw.rect(surf, DK_OUTLINE, rect.inflate(4, 4), border_radius=8)
    body = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    for y in range(rect.h):
        t = y / max(1, rect.h - 1)
        col = lerp_color(BOX_BASE, BOX_SHADE, t) + (255,)
        body.fill(col, pygame.Rect(0, y, rect.w, 1))
    mask = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(),
                     border_radius=6)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(body, rect.topleft)
    pygame.draw.line(surf, BOX_HI,
                     (rect.x + 4, rect.y + 3),
                     (rect.right - 5, rect.y + 3), 2)

    # Ribbon: vertical stripe down the middle
    rv_w = 6
    rvx = rect.centerx - rv_w // 2
    pygame.draw.rect(surf, RIBBON, (rvx, rect.y, rv_w, rect.h))
    pygame.draw.line(surf, RIBBON_HI,
                     (rvx + 1, rect.y), (rvx + 1, rect.bottom - 1), 1)

    # Ribbon: horizontal stripe across the middle
    rh_w = 6
    rhy = rect.y + rect.h // 2 - rh_w // 2
    pygame.draw.rect(surf, RIBBON, (rect.x, rhy, rect.w, rh_w))
    pygame.draw.line(surf, RIBBON_HI, (rect.x, rhy + 1),
                     (rect.right - 1, rhy + 1), 1)

    # Bow on top — puffy two-loop with a knot and trailing tails
    bx, by = cx, rect.y - 6
    pygame.draw.ellipse(surf, DK_OUTLINE,
                        pygame.Rect(bx - 13, by - 6, 13, 12))
    pygame.draw.ellipse(surf, BOW_FILL,
                        pygame.Rect(bx - 12, by - 5, 11, 10))
    pygame.draw.ellipse(surf, DK_OUTLINE,
                        pygame.Rect(bx,       by - 6, 13, 12))
    pygame.draw.ellipse(surf, BOW_FILL,
                        pygame.Rect(bx + 1,   by - 5, 11, 10))
    pygame.draw.ellipse(surf, BOW_HI, pygame.Rect(bx - 10, by - 4, 4, 3))
    pygame.draw.ellipse(surf, BOW_HI, pygame.Rect(bx + 6,  by - 4, 4, 3))
    pygame.draw.rect(surf, DK_OUTLINE, pygame.Rect(bx - 4, by - 6, 9, 12),
                     border_radius=2)
    pygame.draw.rect(surf, BOW_FILL,  pygame.Rect(bx - 3, by - 5, 7, 10),
                     border_radius=2)
    pygame.draw.line(surf, BOW_HI, (bx - 1, by - 4), (bx - 1, by + 3), 1)
    # Trailing tails into the box
    pygame.draw.line(surf, DK_OUTLINE, (bx - 2, by + 4), (bx - 7, by + 11), 4)
    pygame.draw.line(surf, DK_OUTLINE, (bx + 2, by + 4), (bx + 7, by + 11), 4)
    pygame.draw.line(surf, BOW_FILL,   (bx - 2, by + 4), (bx - 6, by + 10), 2)
    pygame.draw.line(surf, BOW_FILL,   (bx + 2, by + 4), (bx + 6, by + 10), 2)

    # Render at full detail above, then downscale once so the parcel reads
    # tiny enough to fit under Pip while keeping a single shared size at every
    # use site (ledge / hand-off / journey carry / mailbox).
    return pygame.transform.smoothscale(surf, (22, 22))


def _build_mailbag() -> pygame.Surface:
    """A canvas satchel with a leather strap and a small brass buckle."""
    surf = pygame.Surface((48, 38), pygame.SRCALPHA)
    # Drop shadow
    pygame.draw.ellipse(surf, (0, 0, 0, 90), (4, 30, 40, 6))
    # Body — soft canvas
    pygame.draw.ellipse(surf, (170, 145, 100), (4, 12, 40, 22))
    pygame.draw.rect(surf, (170, 145, 100), (4, 16, 40, 14))
    # Flap
    pygame.draw.polygon(surf, (140, 115, 75),
                        [(6, 12), (42, 12), (40, 22), (8, 22)])
    # Strap
    pygame.draw.line(surf, (90, 55, 35), (10, 16), (4, 6), 2)
    pygame.draw.line(surf, (90, 55, 35), (38, 16), (44, 6), 2)
    # Buckle
    pygame.draw.circle(surf, (220, 180, 70), (24, 22), 3)
    pygame.draw.circle(surf, (140, 100, 30), (24, 22), 3, 1)
    return surf


def _build_mailbox() -> pygame.Surface:
    """A small wooden mailbox on a short post, with a red flag raised."""
    surf = pygame.Surface((40, 44), pygame.SRCALPHA)
    # Post
    pygame.draw.rect(surf, (95, 70, 45), (18, 24, 4, 20))
    # Box body
    pygame.draw.rect(surf, (170, 130, 90), (8, 14, 24, 14), border_radius=3)
    # Door panel
    pygame.draw.rect(surf, (130, 95, 60), (12, 17, 16, 8), border_radius=2)
    pygame.draw.circle(surf, (220, 180, 70), (26, 21), 1)  # latch
    # Flag pole + flag (raised)
    pygame.draw.line(surf, (60, 40, 25), (32, 6), (32, 18), 2)
    pygame.draw.polygon(surf, (220, 60, 60),
                        [(32, 6), (32, 13), (24, 9)])
    return surf


def _build_skyhouse(kind: str = "home"):
    """A detailed cottage on a fluffy cloud with a porch deck. Two variants:
      * "post" — pickup house: teal roof, yellow pennant flag, hanging
        paper lantern over the porch, painted POST plaque above the door.
      * "home" — delivery destination: red roof, no flag, no plaque.
    Shared elements: multi-layer cloud, stone foundation, gradient plank
    walls, dithered shingle roof, brick chimney with smoke puffs, shuttered
    window + flowerbox, plank door with doormat, porch deck + railing,
    moss strands. Returns (surface, anchors_dict) so beat callers can place
    the parcel + Garrick at meaningful positions."""
    SIZE_W, SIZE_H = 160, 120
    surf = pygame.Surface((SIZE_W, SIZE_H), pygame.SRCALPHA)
    rng = random.Random(hash(kind) & 0xFFFF)

    OUTLINE   = ( 50,  32,  20)
    OUTLINE_S = ( 80,  56,  36)
    WALL_TOP  = (242, 220, 178)
    WALL_BOT  = (210, 180, 140)
    WALL_HI   = (255, 240, 210)
    WALL_TRIM = (130,  85,  50)
    PLANK_LN  = (180, 145, 100)
    if kind == "post":
        ROOF      = ( 60, 130, 175)
        ROOF_DK   = ( 28,  78, 120)
        ROOF_HI   = (110, 180, 220)
    else:  # "home"
        ROOF      = (180,  62,  52)
        ROOF_DK   = (120,  32,  28)
        ROOF_HI   = (220, 100,  88)
    DOOR      = ( 92,  56,  30)
    DOOR_DK   = ( 60,  34,  18)
    DOOR_HI   = (135,  85,  52)
    WIN_FRAME = ( 72,  44,  24)
    WIN_GLASS = (170, 215, 240)
    WIN_HI    = (220, 235, 250)
    SHUTTER   = (160, 105,  60)
    SHUTTER_D = (110,  68,  38)
    CLOUD     = (252, 252, 255)
    CLOUD_HI  = (255, 255, 255)
    CLOUD_SHA = (210, 215, 235)
    CLOUD_DK  = (180, 188, 215)
    BRICK     = (160,  78,  60)
    BRICK_DK  = (110,  46,  34)
    MORTAR    = ( 80,  50,  36)
    STONE_LT  = (200, 188, 168)
    STONE_DK  = (130, 118, 100)
    PORCH     = (170, 130,  82)
    PORCH_DK  = (115,  82,  48)
    PORCH_HI  = (210, 170, 118)
    BRASS     = (240, 200, 100)
    BRASS_DK  = (170, 130,  60)
    LEAF      = ( 95, 145,  72)
    LEAF_DK   = ( 55,  95,  44)

    # ── Cloud base — multi-layer fluffy silhouette with wisp tendrils ────
    cl_y = 88
    pygame.draw.ellipse(surf, CLOUD_DK,  (4,   cl_y + 8, 152, 18))
    pygame.draw.ellipse(surf, CLOUD_SHA, (8,   cl_y + 4, 144, 20))
    pygame.draw.ellipse(surf, CLOUD,     (12,  cl_y,     136, 20))
    pygame.draw.ellipse(surf, CLOUD,     (0,   cl_y + 6,  44, 16))
    pygame.draw.ellipse(surf, CLOUD,     (114, cl_y + 6,  46, 16))
    # Wisp tendrils trailing left + right
    pygame.draw.ellipse(surf, CLOUD_SHA, (-8,  cl_y + 12, 28, 8))
    pygame.draw.ellipse(surf, CLOUD_SHA, (140, cl_y + 12, 24, 8))
    # Top sheen highlights
    pygame.draw.ellipse(surf, CLOUD_HI,  (24,  cl_y + 1,  60,  8))
    pygame.draw.ellipse(surf, CLOUD_HI,  (96,  cl_y + 2,  50,  6))

    # House body
    # ── House geometry: body sits on the LEFT half; porch extends RIGHT.
    body_x, body_y = 14, 50
    body_w, body_h = 60, 36

    # ── Stone foundation band beneath the house body ────────────────────
    found_y = body_y + body_h
    pygame.draw.rect(surf, OUTLINE,
                     (body_x - 2, found_y, body_w + 4, 5))
    for sy in range(found_y + 1, found_y + 4):
        col = lerp_color(STONE_LT, STONE_DK, (sy - found_y - 1) / 2)
        pygame.draw.line(surf, col,
                         (body_x - 1, sy), (body_x + body_w, sy), 1)
    # Mortar nicks every ~7 px
    for nx in range(body_x + 3, body_x + body_w, 7):
        pygame.draw.line(surf, STONE_DK,
                         (nx, found_y + 1), (nx, found_y + 3), 1)

    # ── Walls — vertical gradient + plank siding + corner trim ──────────
    rounded_rect_grad(surf, (body_x, body_y, body_w, body_h),
                      radius=2, top_color=WALL_TOP, bot_color=WALL_BOT)
    pygame.draw.rect(surf, OUTLINE,
                     (body_x - 1, body_y - 1, body_w + 2, body_h + 2), 1)
    # Vertical plank siding lines every 6 px
    for px in range(body_x + 6, body_x + body_w, 6):
        pygame.draw.line(surf, PLANK_LN,
                         (px, body_y + 2), (px, body_y + body_h - 2), 1)
    # Sun-side eave highlight band
    pygame.draw.line(surf, WALL_HI,
                     (body_x + 1, body_y + 1),
                     (body_x + body_w - 2, body_y + 1), 1)
    # Darker corner trim columns
    pygame.draw.rect(surf, WALL_TRIM, (body_x - 1, body_y, 2, body_h))
    pygame.draw.rect(surf, WALL_TRIM,
                     (body_x + body_w - 1, body_y, 2, body_h))

    # ── Roof — main pitched gable with dithered alternating shingle rows
    eave_l = (body_x - 6, body_y + 2)
    eave_r = (body_x + body_w + 6, body_y + 2)
    peak_x = body_x + body_w // 2 - 2
    peak_y = body_y - 22
    roof_outline = [
        (eave_l[0] - 1, eave_l[1] + 1),
        (peak_x,        peak_y - 1),
        (eave_r[0] + 1, eave_r[1] + 1),
    ]
    pygame.draw.polygon(surf, OUTLINE, roof_outline)
    pygame.draw.polygon(surf, ROOF, [eave_l, (peak_x, peak_y), eave_r])
    # Shingle rows: alternating colour, slightly offset short segments.
    # slope = how far up the roof this row is (0 at eaves, 1 at peak); rows
    # narrow as they climb toward the peak.
    roof_height = max(1, eave_l[1] - peak_y)
    for i in range(8):
        sy = body_y + 1 - i * 3
        if sy < peak_y + 2:
            break
        slope = (eave_l[1] - sy) / roof_height
        x_lo = int(eave_l[0] + (peak_x - eave_l[0]) * slope) + 1
        x_hi = int(eave_r[0] + (peak_x - eave_r[0]) * slope) - 1
        if x_hi - x_lo < 4:
            continue
        col = ROOF_DK if (i % 2 == 0) else ROOF_HI
        x = x_lo + (i % 2) * 3
        seg = 5
        while x + seg < x_hi:
            pygame.draw.line(surf, col, (x, sy), (x + seg - 1, sy), 1)
            x += seg + 2
    # Sun-side leading-slope highlight + dark eave shadow
    pygame.draw.line(surf, ROOF_HI,
                     (eave_l[0] + 2, eave_l[1]),
                     (peak_x - 1,    peak_y + 2), 1)
    pygame.draw.line(surf, ROOF_DK,
                     (eave_l[0], eave_l[1] + 2),
                     (eave_r[0], eave_r[1] + 2), 1)

    # ── Brick chimney with stone cap + 3 smoke puffs ────────────────────
    chim_x, chim_y_top, chim_w, chim_h = body_x + body_w - 14, peak_y + 2, 8, 18
    pygame.draw.rect(surf, OUTLINE,
                     (chim_x - 1, chim_y_top - 1, chim_w + 2, chim_h + 2))
    pygame.draw.rect(surf, BRICK,
                     (chim_x, chim_y_top, chim_w, chim_h))
    # Brick courses (alternating dark/mortar lines)
    for i, by in enumerate(range(chim_y_top + 2, chim_y_top + chim_h, 3)):
        pygame.draw.line(surf, MORTAR,
                         (chim_x, by), (chim_x + chim_w - 1, by), 1)
        # Vertical offsets for the brick stagger
        off = 3 if (i % 2 == 0) else 0
        if chim_x + off < chim_x + chim_w - 1:
            pygame.draw.line(surf, BRICK_DK,
                             (chim_x + off, by + 1),
                             (chim_x + off, by + 1), 1)
    # Stone cap
    pygame.draw.rect(surf, OUTLINE,
                     (chim_x - 2, chim_y_top - 3, chim_w + 4, 3))
    pygame.draw.rect(surf, STONE_LT,
                     (chim_x - 1, chim_y_top - 2, chim_w + 2, 1))
    # (Smoke puffs intentionally omitted — at sprite-pixel scale they
    # rendered as semi-transparent rectangular blobs instead of soft puffs.)

    # ── Window with shutters + flowerbox ─────────────────────────────────
    win_w, win_h = 14, 12
    win_x = body_x + 8
    win_y = body_y + 8
    # Shutters on either side
    for side, sx in (("L", win_x - 5), ("R", win_x + win_w + 1)):
        pygame.draw.rect(surf, OUTLINE,
                         (sx - 1, win_y - 1, 5, win_h + 2))
        pygame.draw.rect(surf, SHUTTER, (sx, win_y, 4, win_h))
        # Diagonal slats
        for sl in range(0, win_h - 1, 2):
            pygame.draw.line(surf, SHUTTER_D,
                             (sx, win_y + sl + 1),
                             (sx + 3, win_y + sl), 1)
    # Window frame + glass
    pygame.draw.rect(surf, OUTLINE,
                     (win_x - 1, win_y - 1, win_w + 2, win_h + 2))
    pygame.draw.rect(surf, WIN_GLASS, (win_x, win_y, win_w, win_h))
    # Reflection sheen
    pygame.draw.line(surf, WIN_HI,
                     (win_x + 1, win_y + 1),
                     (win_x + win_w // 2 - 1, win_y + 1), 1)
    pygame.draw.line(surf, WIN_HI,
                     (win_x + 1, win_y + 1),
                     (win_x + 1, win_y + win_h // 2 - 1), 1)
    # Cross frame (mullions)
    pygame.draw.line(surf, WIN_FRAME,
                     (win_x + win_w // 2, win_y),
                     (win_x + win_w // 2, win_y + win_h - 1), 1)
    pygame.draw.line(surf, WIN_FRAME,
                     (win_x, win_y + win_h // 2),
                     (win_x + win_w - 1, win_y + win_h // 2), 1)
    # Sill
    pygame.draw.rect(surf, WALL_TRIM,
                     (win_x - 2, win_y + win_h, win_w + 4, 2))
    # Flower box below the sill — wood box + foliage clumps + flower dots
    fb_x, fb_y, fb_w, fb_h = win_x - 2, win_y + win_h + 2, win_w + 4, 5
    pygame.draw.rect(surf, OUTLINE, (fb_x - 1, fb_y - 1, fb_w + 2, fb_h + 1))
    pygame.draw.rect(surf, DOOR_DK, (fb_x, fb_y, fb_w, fb_h))
    pygame.draw.line(surf, DOOR_HI,
                     (fb_x, fb_y), (fb_x + fb_w - 1, fb_y), 1)
    # Foliage clumps spilling over
    for cx_clump in (fb_x + 2, fb_x + fb_w // 2, fb_x + fb_w - 3):
        pygame.draw.circle(surf, LEAF_DK, (cx_clump, fb_y - 1), 2)
        pygame.draw.circle(surf, LEAF, (cx_clump - 1, fb_y - 2), 2)
    # Flower dots — bougainvillea two-layer technique
    flower_a = (255, 220,  90) if kind == "post" else (235, 130, 165)
    flower_b = (180, 220, 255) if kind == "post" else (250, 235, 220)
    for _ in range(7):
        fx = rng.randint(fb_x + 1, fb_x + fb_w - 2)
        fy = rng.randint(fb_y - 3, fb_y - 1)
        pygame.draw.circle(surf, flower_a, (fx, fy), 1)
        if rng.random() < 0.5:
            pygame.draw.circle(surf, flower_b, (fx + 1, fy), 1)

    # ── Door — taller plank door with threshold + brass knob + doormat ──
    door_w, door_h = 14, 22
    door_x = body_x + body_w - door_w - 6
    door_y = body_y + body_h - door_h
    # Frame
    pygame.draw.rect(surf, OUTLINE,
                     (door_x - 2, door_y - 1, door_w + 4, door_h + 1))
    pygame.draw.rect(surf, WALL_TRIM,
                     (door_x - 1, door_y, door_w + 2, door_h))
    pygame.draw.rect(surf, DOOR, (door_x, door_y + 1, door_w, door_h - 1))
    # Vertical plank lines on the door
    for dx in (door_x + 4, door_x + 9):
        pygame.draw.line(surf, DOOR_DK,
                         (dx, door_y + 2), (dx, door_y + door_h - 2), 1)
    # Top arched highlight band
    pygame.draw.line(surf, DOOR_HI,
                     (door_x + 1, door_y + 2),
                     (door_x + door_w - 2, door_y + 2), 1)
    # Brass knob + small kickplate
    pygame.draw.circle(surf, BRASS,
                       (door_x + door_w - 3, door_y + door_h // 2), 1)
    pygame.draw.rect(surf, BRASS_DK,
                     (door_x + 1, door_y + door_h - 4, door_w - 2, 2))
    # Doormat — straw-coloured band on the foundation
    mat_x, mat_y, mat_w, mat_h = door_x - 2, found_y + 1, door_w + 4, 3
    pygame.draw.rect(surf, OUTLINE_S, (mat_x, mat_y, mat_w, mat_h))
    for i in range(0, mat_w, 2):
        pygame.draw.line(surf, BRASS_DK,
                         (mat_x + i, mat_y + 1),
                         (mat_x + i, mat_y + 1), 1)

    # ── POST nameplate above the door (post variant only) ───────────────
    if kind == "post":
        sign_x, sign_y, sign_w, sign_h = door_x - 1, door_y - 8, door_w + 2, 6
        pygame.draw.rect(surf, OUTLINE,
                         (sign_x - 1, sign_y - 1, sign_w + 2, sign_h + 2))
        pygame.draw.rect(surf, BRASS, (sign_x, sign_y, sign_w, sign_h))
        pygame.draw.line(surf, BRASS_DK,
                         (sign_x, sign_y + sign_h - 1),
                         (sign_x + sign_w - 1, sign_y + sign_h - 1), 1)
        # Pixel-painted POST glyphs (each letter is 3 px wide × 4 tall)
        gy = sign_y + 1
        gx = sign_x + 1
        # P
        for px, py in ((0,0),(1,0),(0,1),(2,1),(0,2),(1,2),(0,3)):
            surf.set_at((gx + px, gy + py), OUTLINE)
        # O
        gx += 4
        for px, py in ((0,0),(1,0),(2,0),(0,1),(2,1),(0,2),(2,2),(0,3),(1,3),(2,3)):
            surf.set_at((gx + px, gy + py), OUTLINE)
        # S
        gx += 4
        for px, py in ((1,0),(2,0),(0,1),(1,2),(2,2),(0,3),(1,3)):
            surf.set_at((gx + px, gy + py), OUTLINE)
        # T
        gx += 4
        for px, py in ((0,0),(1,0),(2,0),(1,1),(1,2),(1,3)):
            surf.set_at((gx + px, gy + py), OUTLINE)

    # ── Porch deck on the right of the house — planks + railing ─────────
    porch_x_left  = body_x + body_w
    porch_x_right = porch_x_left + 64
    porch_top_y   = found_y + 1
    porch_bot_y   = porch_top_y + 6
    # Plank floor (4 horizontal planks with gaps)
    pygame.draw.rect(surf, OUTLINE,
                     (porch_x_left, porch_top_y - 1,
                      porch_x_right - porch_x_left + 1,
                      porch_bot_y - porch_top_y + 2))
    pygame.draw.rect(surf, PORCH,
                     (porch_x_left, porch_top_y,
                      porch_x_right - porch_x_left, 6))
    for i, py in enumerate((porch_top_y, porch_top_y + 2,
                             porch_top_y + 4)):
        col = PORCH_HI if (i % 2 == 0) else PORCH_DK
        pygame.draw.line(surf, col,
                         (porch_x_left, py), (porch_x_right - 1, py), 1)
    # Top edge highlight (sunlit deck top)
    pygame.draw.line(surf, PORCH_HI,
                     (porch_x_left, porch_top_y),
                     (porch_x_right - 1, porch_top_y), 1)
    # Front rail running along the deck above the floor
    rail_y = porch_top_y - 6
    pygame.draw.line(surf, OUTLINE,
                     (porch_x_left, rail_y),
                     (porch_x_right - 1, rail_y), 1)
    pygame.draw.line(surf, PORCH,
                     (porch_x_left, rail_y - 1),
                     (porch_x_right - 1, rail_y - 1), 1)
    # Vertical balusters (slim wood posts)
    for bx in range(porch_x_left + 4, porch_x_right - 2, 10):
        pygame.draw.line(surf, OUTLINE,
                         (bx, rail_y), (bx, porch_top_y - 1), 1)
        pygame.draw.line(surf, PORCH_DK,
                         (bx + 1, rail_y), (bx + 1, porch_top_y - 1), 1)
    # End post (taller, supports the rail's right end)
    end_post_x = porch_x_right - 2
    pygame.draw.rect(surf, OUTLINE,
                     (end_post_x - 1, rail_y - 6, 4, porch_top_y - rail_y + 6))
    pygame.draw.rect(surf, PORCH,
                     (end_post_x, rail_y - 5, 2, porch_top_y - rail_y + 5))

    # ── Hanging lantern at the porch end (post variant only) ────────────
    if kind == "post":
        # Bracket arm reaching out from end post
        bracket_x = end_post_x + 2
        bracket_y = rail_y - 4
        pygame.draw.line(surf, OUTLINE,
                         (end_post_x + 1, bracket_y),
                         (bracket_x + 4, bracket_y), 2)
        # Lantern body
        lan_cx, lan_cy = bracket_x + 5, bracket_y + 8
        pygame.draw.line(surf, OUTLINE,
                         (lan_cx, bracket_y), (lan_cx, lan_cy - 4), 1)
        # Soft warm glow behind the lantern
        blit_glow(surf, lan_cx, lan_cy, 8, (255, 220, 140), 100)
        # Paper-lantern body (rounded teardrop)
        pygame.draw.ellipse(surf, OUTLINE,
                            (lan_cx - 4, lan_cy - 4, 9, 9))
        pygame.draw.ellipse(surf, (255, 200, 110),
                            (lan_cx - 3, lan_cy - 3, 7, 7))
        pygame.draw.ellipse(surf, (255, 240, 180),
                            (lan_cx - 2, lan_cy - 2, 4, 4))
        # Top + bottom caps
        pygame.draw.line(surf, OUTLINE,
                         (lan_cx - 2, lan_cy - 4), (lan_cx + 2, lan_cy - 4), 1)
        pygame.draw.line(surf, OUTLINE,
                         (lan_cx - 1, lan_cy + 5), (lan_cx + 1, lan_cy + 5), 1)

    # ── Pennant flag (post variant only) ─────────────────────────────────
    chimney_top = (chim_x + chim_w // 2, chim_y_top - 3)
    if kind == "post":
        pole_top_y = chimney_top[1] - 14
        pygame.draw.line(surf, OUTLINE,
                         (chimney_top[0], pole_top_y),
                         (chimney_top[0], chimney_top[1]), 2)
        flag_pts = [(chimney_top[0],     pole_top_y + 1),
                    (chimney_top[0] + 12, pole_top_y + 5),
                    (chimney_top[0],     pole_top_y + 9)]
        pygame.draw.polygon(surf, (235, 205,  90), flag_pts)
        pygame.draw.polygon(surf, OUTLINE, flag_pts, 1)
        # Flutter line
        pygame.draw.line(surf, OUTLINE_S,
                         (chimney_top[0] + 2, pole_top_y + 4),
                         (chimney_top[0] + 9, pole_top_y + 5), 1)

    # ── Foliage accents — moss strands + ivy spray ──────────────────────
    # Moss strands hanging from the cloud lip
    for mx in (24, 50, 102, 132):
        h = 6 + (mx % 4)
        pygame.draw.line(surf, LEAF_DK, (mx, cl_y + 5), (mx, cl_y + 5 + h), 1)
        pygame.draw.circle(surf, LEAF,    (mx, cl_y + 5 + h), 2)
        pygame.draw.circle(surf, LEAF_DK, (mx, cl_y + 5 + h), 2, 1)
    # Ivy spray creeping up the right corner of the house body
    ivy_x = body_x + body_w - 1
    for dy in range(0, 18, 3):
        pygame.draw.circle(surf, LEAF_DK,
                           (ivy_x - (dy % 5 == 0), body_y + body_h - dy), 2)
        pygame.draw.circle(surf, LEAF,
                           (ivy_x - 1 - (dy % 5 == 0), body_y + body_h - dy - 1), 1)

    # ── Anchors for callers (sprite-local coordinates) ──────────────────
    anchors = {
        "doorstep":     (door_x + door_w // 2, mat_y),
        "porch_top":    (porch_x_left, porch_x_right, porch_top_y),
        "garrick_stand": (porch_x_left + 20, porch_top_y),
        "chimney_top":  chimney_top,
    }
    return surf, anchors


def _build_garrick() -> pygame.Surface:
    """Mr. Garrick: a calm pelican silhouette in pale-pink with a white shirt
    collar and a perpetual frown beak. Simple — he's a quiet supporting role
    in the cinematic."""
    surf = pygame.Surface((64, 72), pygame.SRCALPHA)
    # Drop shadow
    pygame.draw.ellipse(surf, (0, 0, 0, 90), (10, 60, 44, 8))
    # Tail — small
    pygame.draw.polygon(surf, (210, 175, 175),
                        [(8, 50), (20, 46), (18, 56)])
    # Body — pale pink ovate
    pygame.draw.ellipse(surf, (240, 200, 200), (10, 30, 44, 32))
    # Belly highlight
    pygame.draw.ellipse(surf, (255, 220, 220), (16, 40, 30, 20))
    # White shirt collar — two wedges meeting at a V under the head
    pygame.draw.polygon(surf, (255, 255, 255),
                        [(28, 38), (36, 38), (32, 50)])
    pygame.draw.polygon(surf, (220, 220, 220),
                        [(28, 38), (32, 50), (24, 44)])
    pygame.draw.polygon(surf, (220, 220, 220),
                        [(36, 38), (32, 50), (40, 44)])
    # Head — round dome
    pygame.draw.ellipse(surf, (240, 200, 200), (20, 12, 26, 24))
    # Eye — beady black with a tiny eye-bag arc to read "tired manager"
    pygame.draw.circle(surf, (20, 20, 30), (38, 22), 2)
    pygame.draw.arc(surf, (160, 110, 110),
                    pygame.Rect(34, 23, 10, 6), 0.0, math.pi, 1)
    # Beak — long, hooked, frown set
    pygame.draw.polygon(surf, (255, 200, 90),
                        [(40, 22), (60, 26), (58, 31), (40, 28)])
    # Lower beak (slightly drooped)
    pygame.draw.polygon(surf, (220, 160, 60),
                        [(40, 28), (58, 31), (54, 33), (40, 31)])
    # Microphone — small dark stem + bulb on the breast, suggesting the
    # "endless orders into Pip's earpiece" without dialogue.
    pygame.draw.line(surf, (40, 40, 50), (28, 50), (22, 56), 2)
    pygame.draw.circle(surf, (60, 60, 70), (22, 56), 3)
    return surf


def _get_sprite(name: str) -> pygame.Surface:
    s = _SPRITES.get(name)
    if s is None:
        if name == "parcel":   s = _build_parcel()
        elif name == "mailbag": s = _build_mailbag()
        elif name == "mailbox": s = _build_mailbox()
        elif name == "skyhouse_post":
            s, _ = _build_skyhouse(kind="post")
        elif name == "skyhouse_home":
            s, _ = _build_skyhouse(kind="home")
        elif name == "garrick": s = _build_garrick()
        else: raise KeyError(name)
        _SPRITES[name] = s
    return s


_HOUSE_ANCHORS: dict = {}


def _get_house_anchors(kind: str) -> dict:
    """Sprite-local anchor positions for the sky-house variants. Computed
    by rebuilding the sprite once (cached in _HOUSE_ANCHORS), so callers
    don't have to hard-code internal pixel offsets."""
    a = _HOUSE_ANCHORS.get(kind)
    if a is None:
        _, a = _build_skyhouse(kind=kind)
        _HOUSE_ANCHORS[kind] = a
    return a


# Public re-exports — `scenes.py` reuses these for the gameplay opener
# (cottage + parcel rendered for the first ~2.5 s of STATE_PLAY).
get_sprite = _get_sprite
get_house_anchors = _get_house_anchors


class IntroScene:
    """Owns the entire frame for the intro state.

    The scene must never compose with `World` — the App's `_render` skips its
    background/entity passes whenever `state == STATE_INTRO`.
    """

    DURATION = DURATION

    def __init__(self):
        self.t = 0.0
        self.done = False
        self._title_t = 0.0

    def update(self, dt: float) -> None:
        self.t += dt
        self._title_t += dt
        if self.t >= self.DURATION:
            self.done = True

    def skip(self) -> None:
        self.done = True

    def render(self, surf: pygame.Surface) -> None:
        # Fallback fill in case a beat draws nothing (defensive).
        surf.fill((10, 12, 30))
        # Beats are dispatched in render() — see slices D + E.
        _dispatch_beat(self, surf)
        # SKIP affordance fades in at t=1.5 s, top-right.
        _draw_skip_pill(surf, self.t)


# ── world-paint helpers used by every beat ───────────────────────────────────

def _draw_sky(surf: pygame.Surface, phase: float) -> None:
    """Paint the biome-aware sky for `phase`, blending two adjacent buckets so
    a slowly-changing phase reads as a continuous fade. Mirrors the trick in
    `scenes.py:_draw_background`."""
    buckets = _biome.PHASE_BUCKETS
    pf = phase % 1.0
    bucket_f = pf * buckets
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


def _draw_world(surf: pygame.Surface, phase: float, scroll: float,
                cloud_phase: float, ground: bool = True) -> None:
    """Sky + mountains + (optional) ground for the given phase. Intro beats
    pass ``ground=True`` so the green grass band matches gameplay."""
    palette = _biome.palette_for_phase(phase)
    _draw_sky(surf, phase)
    # Three drifting clouds for ambient depth
    for i, (bx, by, sc, variant) in enumerate((
            (40, 110, 0.85, 0), (220, 70, 0.7, 2), (120, 200, 1.0, 4))):
        ox = ((bx - scroll * (0.04 + 0.02 * i)) % (W + 160)) - 80
        draw_cloud(surf, ox, by + math.sin(cloud_phase * 0.3 + i) * 3,
                   sc, variant=variant)
    draw_mountains(surf, scroll, GROUND_Y, W,
                   palette['mtn_far'], palette['mtn_near'])
    if ground:
        draw_ground(surf, GROUND_Y, W, H, scroll,
                    palette['ground_top'], palette['ground_mid'], (60, 40, 25))


def _draw_distant_pillar(surf: pygame.Surface, x_center: int,
                         palette: dict, h_top: int, h_bot: int) -> None:
    """A single pillar pair drawn as a soft silhouette in the distance."""
    w = 36
    top_rect = pygame.Rect(x_center - w // 2, 0, w, h_top)
    bot_rect = pygame.Rect(x_center - w // 2, GROUND_Y - h_bot, w, h_bot)
    draw_pillar_pair(surf, top_rect, bot_rect, palette, seed=x_center * 31)


def _draw_pip(surf: pygame.Surface, x: float, y: float, frame_t: float,
              tilt_deg: float, scale: float = 1.0, alpha: int = 255) -> None:
    """Draw the macaw at (x, y) using the cached parrot rotation."""
    frame_idx = int(frame_t) % len(_parrot.FRAMES)
    img = _parrot.get_parrot(frame_idx, tilt_deg)
    if scale != 1.0:
        sw = max(2, int(img.get_width() * scale))
        sh = max(2, int(img.get_height() * scale))
        img = pygame.transform.smoothscale(img, (sw, sh))
    if alpha < 255:
        img = img.copy()
        img.set_alpha(alpha)
    r = img.get_rect(center=(int(x), int(y)))
    surf.blit(img, r.topleft)


def _draw_glow_motes(surf: pygame.Surface, t: float,
                     count: int = 10, color=(255, 230, 180)) -> None:
    """Drifting motes — like dust in a beam of sun. Quiet depth that never
    reads as gameplay coins. Kept small and dim by design."""
    for i in range(count):
        seed = i * 137
        speed = 18.0 + (seed % 13) * 1.5
        x = ((seed * 7 % W) + t * speed) % (W + 40) - 20
        y = (seed * 53 % (H - 200)) + math.sin(t * 0.8 + i) * 10
        r = 4 + (seed % 3) * 2
        a = 30 + int(18 * math.sin(t * 1.3 + i * 0.8))
        a = max(15, min(60, a))
        blit_glow(surf, int(x), int(y), r, color, a)


def _draw_distant_flock(surf: pygame.Surface, t: float, x_off: float) -> None:
    """A small V-formation of birds, drifting once across the journey beat."""
    # Anchor x slides from off-screen-right to off-screen-left across ~5 s.
    cx = int(x_off)
    if cx < -40 or cx > W + 40:
        return
    cy = 130
    color = (40, 50, 75)
    for i, (dx, dy) in enumerate(((0, 0), (-8, 4), (8, 4), (-16, 8), (16, 8))):
        bob = math.sin(t * 4.5 + i) * 1.0
        bx = cx + dx
        by = cy + dy + bob
        pygame.draw.polygon(surf, color, [
            (bx - 4, by), (bx, by - 2), (bx + 4, by),
            (bx + 1, by + 1), (bx - 1, by + 1),
        ])


# ── beat 1: Dawn at the perch (0.0 – 2.5) ────────────────────────────────────

def _beat_dawn(scene: "IntroScene", surf: pygame.Surface, u: float) -> None:
    """Predawn → first light. A tiny post-house floats in the sky with the
    parcel waiting on its doorstep; Mr. Garrick hovers nearby. The world
    wakes up; Pip hasn't arrived yet."""
    # Pickup happens in clear daylight. The biome stays locked here — only
    # the journey beat cycles through the day/night arc.
    phase = 0.0
    _draw_world(surf, phase, scroll=u * 4.0, cloud_phase=scene.t,
                ground=True)

    # Pickup post-house — anchored on the LEFT, slightly above centre,
    # with a slow weightless bob.
    house = _get_sprite("skyhouse_post")
    anc = _get_house_anchors("post")
    house_cx = int(W * 0.30)
    house_cy = int(H * 0.42) + int(math.sin(scene.t * 0.7) * 2)
    house_x = house_cx - house.get_width() // 2
    house_y = house_cy - house.get_height() // 2
    surf.blit(house, (house_x, house_y))

    doorstep_x = house_x + anc["doorstep"][0]
    doorstep_y = house_y + anc["doorstep"][1]

    # Parcel waits on the doormat at the doorstep.
    par = _get_sprite("parcel")
    surf.blit(par, (doorstep_x - par.get_width() // 2,
                    doorstep_y - par.get_height() + 1))

    # Mr. Garrick — STANDING on the porch deck (no bob, no hover).
    # Scaled down so he fits the cottage at proper proportion.
    g = pygame.transform.smoothscale(_get_sprite("garrick"), (38, 42))
    stand_x_local, stand_y_local = anc["garrick_stand"]
    g_x = house_x + stand_x_local - g.get_width() // 2
    g_y = house_y + stand_y_local - g.get_height() + 4  # feet on the deck
    surf.blit(g, (g_x, g_y))


# ── beat 2: The hand-off (2.5 – 4.5) ─────────────────────────────────────────

def _beat_handoff(scene: "IntroScene", surf: pygame.Surface, u: float) -> None:
    """Same pickup post-house as beat 1. Mr. Garrick stands on the porch.
    Pip swoops in from off-screen, lifts the parcel off the doorstep, and
    drifts to the right of the porch — composed as the launch pose for
    the journey."""
    # Same locked clear-day biome as beat 1 — pickup never shifts colours.
    sky_phase = 0.0
    _draw_world(surf, sky_phase, scroll=10.0 + u * 6.0,
                cloud_phase=scene.t, ground=True)

    # Reuse the EXACT post-house from beat 1.
    house = _get_sprite("skyhouse_post")
    anc = _get_house_anchors("post")
    house_cx = int(W * 0.30)
    house_cy = int(H * 0.42) + int(math.sin(scene.t * 0.7) * 2)
    house_x = house_cx - house.get_width() // 2
    house_y = house_cy - house.get_height() // 2
    surf.blit(house, (house_x, house_y))

    doorstep_x = house_x + anc["doorstep"][0]
    doorstep_y = house_y + anc["doorstep"][1]
    porch_left, porch_right, porch_top = anc["porch_top"]
    porch_top_x_right = house_x + porch_right
    porch_top_y_world = house_y + porch_top

    # Mr. Garrick STANDING on the porch — no bob, no wing flap, just a
    # patient postmaster. Scaled to cottage proportion.
    g = pygame.transform.smoothscale(_get_sprite("garrick"), (38, 42))
    stand_x_local, stand_y_local = anc["garrick_stand"]
    g_x = house_x + stand_x_local - g.get_width() // 2
    g_y = house_y + stand_y_local - g.get_height() + 4
    surf.blit(g, (g_x, g_y))

    # Pip swoops in from off-screen-LEFT, arcs up and over the cottage roof,
    # then descends to land on the porch beside the doorstep where the parcel
    # is waiting. Final exit drifts him to the journey's bob position.
    par = _get_sprite("parcel")
    pip_start = (-50, 90)
    pip_dock  = (doorstep_x + 22, doorstep_y - 16)   # porch-level hover beside doorstep
    # Exit endpoint tracks the journey's live sin-bob position so the cut
    # into beat 3 is positionally seamless even mid-bob.
    journey_x = W * 0.48 + math.sin(scene.t * 0.8) * 18
    journey_y = H * 0.42 + math.sin(scene.t * 1.5) * 14
    pip_exit  = (journey_x, journey_y)
    # Approach occupies most of the beat (u 0.0–0.75) so the swoop never
    # feels rushed; departure is the last quarter. Add a vertical arc — Pip
    # dips UP over the cottage roof in the middle of the path before
    # descending to the porch — so the landing reads as a natural glide
    # rather than a straight line.
    APPROACH_ARC = 30  # px of upward dip at midpoint of the approach
    if u < 0.78:
        ease = _smoothstep(_clamp01(u / 0.75))
        pip_x = pip_start[0] + (pip_dock[0] - pip_start[0]) * ease
        pip_y_lerp = pip_start[1] + (pip_dock[1] - pip_start[1]) * ease
        # Negative offset = arc UP through the middle of the flight
        pip_y = pip_y_lerp - math.sin(ease * math.pi) * APPROACH_ARC
        # Tilt: head slightly down during the long descent, leveling to
        # zero as Pip touches down on the porch.
        tilt = -8.0 * (1.0 - ease)
        # Parcel still on the doormat until Pip reaches it.
        surf.blit(par, (doorstep_x - par.get_width() // 2,
                        doorstep_y - par.get_height() + 1))
    else:
        ease = _smoothstep(_clamp01((u - 0.78) / 0.22))
        pip_x = pip_dock[0] + (pip_exit[0] - pip_dock[0]) * ease
        pip_y = pip_dock[1] + (pip_exit[1] - pip_dock[1]) * ease
        # Banks slightly up as he lifts off carrying the parcel.
        tilt = 4.0 * ease
        # Parcel now travels with Pip — tucked beneath him.
        surf.blit(par, (int(pip_x) - par.get_width() // 2,
                        int(pip_y) + 10))
    _draw_pip(surf, pip_x, pip_y, frame_t=scene.t * 4.0, tilt_deg=tilt)


# ── beat 3: The journey (4.5 – 10.0) ─────────────────────────────────────────

# Phase waypoints across the beat: clear day → golden hour → sunset → night.
# The journey ends at night so beat 4 can deliver the parcel under starlight
# without a biome jump. Pickup (beats 1-2) is locked at clear day.
_JOURNEY_WAYPOINTS = (
    (0.00, 0.00),  # u=0.00, clear day (matches the locked pickup biome)
    (0.30, 0.18),  # golden hour
    (0.60, 0.32),  # sunset
    (1.00, 0.62),  # night
)


def _journey_phase(u: float) -> float:
    u = _clamp01(u)
    for i in range(len(_JOURNEY_WAYPOINTS) - 1):
        u0, p0 = _JOURNEY_WAYPOINTS[i]
        u1, p1 = _JOURNEY_WAYPOINTS[i + 1]
        if u <= u1:
            seg = 0.0 if u1 <= u0 else (u - u0) / (u1 - u0)
            seg = _smoothstep(seg)
            return p0 + (p1 - p0) * seg
    return _JOURNEY_WAYPOINTS[-1][1]


def _beat_journey(scene: "IntroScene", surf: pygame.Surface, u: float) -> None:
    """The heart of the cinematic. Pip glides serenely while the world cycles
    around him. Camera floats high — no ground in frame."""
    phase = _journey_phase(u)
    # Scroll continues from beat 2's end value (16) so the cloud parallax
    # doesn't pop at the cut — it then accelerates across the beat.
    scroll = 16.0 + u * 280.0
    _draw_world(surf, phase, scroll=scroll, cloud_phase=scene.t, ground=True)

    # First slice of the beat: the pickup post-house is still drifting off
    # the left edge as Pip "flies past" it, bridging the cut from beat 2.
    if u < 0.18:
        bridge_t = u / 0.18  # 0 at the cut, 1 when fully scrolled away
        house = _get_sprite("skyhouse_post")
        # Match beat 2's last anchor (W*0.30, H*0.42), then translate left.
        anchor_cx = int(W * 0.30) - int(bridge_t * (W * 0.55))
        anchor_cy = int(H * 0.42)
        hx = anchor_cx - house.get_width() // 2
        hy = anchor_cy - house.get_height() // 2
        # Fade out the cottage as it slides away.
        if bridge_t < 1.0:
            faded = house.copy()
            faded.set_alpha(int(255 * (1.0 - bridge_t)))
            surf.blit(faded, (hx, hy))

    # Distant V-formation flock — drifts across once during the beat
    if 0.55 < u < 0.85:
        flock_u = (u - 0.55) / 0.30
        fx = W + 40 - flock_u * (W + 80)
        _draw_distant_flock(surf, scene.t, fx)

    # Last half of the journey: the destination home cottage appears as a
    # small hazy silhouette on the horizon and grows as Pip "flies toward"
    # it, so by the cut into beat 4 the cottage is already in place at full
    # size. Replaces the previous rise-from-below pop in beat 4.
    if u >= 0.50:
        approach = _smoothstep((u - 0.50) / 0.50)
        home = _get_sprite("skyhouse_home")
        scale = 0.28 + 0.72 * approach          # 0.28 distant → 1.0 near
        sw = int(home.get_width() * scale)
        sh = int(home.get_height() * scale)
        home_scaled = pygame.transform.smoothscale(home, (sw, sh))
        # Hazy alpha while distant; full opacity when near.
        home_scaled.set_alpha(int(170 + 85 * approach))
        # Cottage anchored to its beat-4 settled position so the cut is
        # positionally seamless. A subtle bob like beat 4's.
        home_cx = W // 2
        home_cy = int(H * 0.55) + int(math.sin(scene.t * 0.9) * 3)
        surf.blit(home_scaled, (home_cx - sw // 2, home_cy - sh // 2))

    # Pip — gentle sin-bob path centred at H*0.42 (matches beat 2's exit
    # altitude exactly so the cut is invisible). Slow flap, almost-level
    # tilt; he carries the parcel tucked beneath him.
    pip_x = W * 0.48 + math.sin(scene.t * 0.8) * 18
    pip_y = H * 0.42 + math.sin(scene.t * 1.5) * 14
    tilt = math.sin(scene.t * 1.5) * -6.0
    par = _get_sprite("parcel")
    surf.blit(par, (int(pip_x) - par.get_width() // 2,
                    int(pip_y) + 10))
    _draw_pip(surf, pip_x, pip_y, frame_t=scene.t * 5.0, tilt_deg=tilt,
              scale=1.0)


# ── beat 4: Arrival (10.0 – 11.0) ────────────────────────────────────────────

def _beat_arrival(scene: "IntroScene", surf: pygame.Surface, u: float) -> None:
    """Pip glides up to a tiny cottage floating on a cloud and leaves the
    parcel on its doorstep. No pillar, no mailbox — the destination is a
    house in the sky."""
    # Delivery happens at night — the journey ended there, so beat 4 holds
    # the same starlit phase Pip arrived under. Scroll continues from
    # beat 3's end value (296) so the cloud parallax doesn't pop.
    phase = 0.62
    _draw_world(surf, phase, scroll=296.0 + u * 30.0,
                cloud_phase=scene.t, ground=True)

    # Floating sky-house, centred. The cottage was approached gradually
    # during the last half of the journey beat (it grew from a distant
    # silhouette to full size), so the cut here is positionally seamless
    # — it just keeps bobbing.
    house = _get_sprite("skyhouse_home")
    anc = _get_house_anchors("home")
    house_cx = W // 2
    house_cy_settled = int(H * 0.55)
    house_cy_now = house_cy_settled + int(math.sin(scene.t * 0.9) * 3)
    house_x = house_cx - house.get_width() // 2
    house_y_now = house_cy_now - house.get_height() // 2
    surf.blit(house, (house_x, house_y_now))

    # Doorstep follows the live cottage bob so Pip's drop target stays
    # anchored to the visible doormat.
    doorstep_x = house_x + anc["doorstep"][0]
    doorstep_y = house_y_now + anc["doorstep"][1]

    # Pip's start pose tracks the journey's live sin-bob so the cut from
    # beat 3 is seamless even mid-bob. Pip glides from there down to the
    # doorstep, drops the parcel, and continues onward.
    par = _get_sprite("parcel")
    start_x = W * 0.48 + math.sin(scene.t * 0.8) * 18
    start_y = H * 0.42 + math.sin(scene.t * 1.5) * 14
    drop_x, drop_y = doorstep_x + 38, doorstep_y - 30
    exit_x, exit_y = doorstep_x + 80, doorstep_y - 70
    # Same pacing as beat 2: arrival uses most of the beat, drop + exit
    # is the final stretch.
    if u < 0.75:
        ease = _smoothstep(u / 0.72)
        pip_x = start_x + (drop_x - start_x) * ease
        pip_y = start_y + (drop_y - start_y) * ease
        tilt = -10.0 * (1.0 - ease)
        carry_x = int(pip_x) - par.get_width() // 2
        carry_y = int(pip_y) + 10
        surf.blit(par, (carry_x, carry_y))
        _draw_pip(surf, pip_x, pip_y, frame_t=scene.t * 4.0, tilt_deg=tilt)
    else:
        rest_x = doorstep_x - par.get_width() // 2
        rest_y = doorstep_y - par.get_height()
        surf.blit(par, (rest_x, rest_y))
        ease = _smoothstep((u - 0.75) / 0.25)
        pip_x = drop_x + (exit_x - drop_x) * ease
        pip_y = drop_y + (exit_y - drop_y) * ease
        tilt = 6.0 * ease  # banks up as he flies off
        _draw_pip(surf, pip_x, pip_y, frame_t=scene.t * 4.0, tilt_deg=tilt)


# ── beat 5: Title (11.0 – 12.0) ──────────────────────────────────────────────

def _beat_title(scene: "IntroScene", surf: pygame.Surface, u: float) -> None:
    """Cinematic close-out: hold on the same starlit night the parcel was
    delivered under for ~1 s, dim the scene gently, then auto-finish so the
    App can hand off to the menu (which is the actual click-to-start
    title screen showing SKYBIT + the subtitle + the tap prompt)."""
    phase = 0.62
    _draw_world(surf, phase, scroll=440.0 + scene.t * 12.0,
                cloud_phase=scene.t, ground=True)

    # Gentle dim toward the menu's tint so the cut into STATE_MENU isn't
    # a jarring brightness pop.
    dim_a = int(110 * _smoothstep(_clamp01(u)))
    dim = pygame.Surface((W, H), pygame.SRCALPHA)
    dim.fill((6, 1, 21, dim_a))
    surf.blit(dim, (0, 0))


# ── final beat dispatcher ────────────────────────────────────────────────────

def _dispatch_beat(scene: "IntroScene", surf: pygame.Surface) -> None:
    t = scene.t
    # Beat windows (rebalanced so dawn doesn't stall and Pip's arrivals
    # in the hand-off + delivery have time to glide in gracefully):
    #   dawn      0.0–1.0 (1.0s)
    #   handoff   1.0–4.0 (3.0s) — Pip's pickup arrival uses most of this
    #   journey   4.0–9.0 (5.0s)
    #   arrival   9.0–11.0 (2.0s) — Pip's delivery arrival is unhurried
    #   title    11.0–12.0 (1.0s)
    if t < 1.0:
        _beat_dawn(scene, surf, t / 1.0)
    elif t < 4.0:
        _beat_handoff(scene, surf, (t - 1.0) / 3.0)
    elif t < 9.0:
        _beat_journey(scene, surf, (t - 4.0) / 5.0)
    elif t < 11.0:
        _beat_arrival(scene, surf, (t - 9.0) / 2.0)
    elif t < DURATION:
        _beat_title(scene, surf, (t - 11.0) / 1.0)
    else:
        _beat_title(scene, surf, 1.0)


def _draw_skip_pill(surf: pygame.Surface, t: float) -> None:
    """Short SKIP pill at the bottom of the intro screen. Fades in at
    t=1.0 s (so the user has a moment to see the cinematic before the
    button suggests bailing). The pill is purely a visual affordance —
    the App's input handler treats any tap during STATE_INTRO as a skip,
    not just clicks on this rect."""
    if t < 1.0:
        return
    fade = _clamp01((t - 1.0) / 0.4)
    alpha_text = int(220 * fade)
    alpha_pill = int(170 * fade)
    if alpha_text <= 0:
        return
    f = _font(13, True)
    label = f.render("SKIP", True, WHITE)
    label.set_alpha(alpha_text)
    pad_w = label.get_width() + 26
    pad_h = label.get_height() + 10
    pill = pygame.Surface((pad_w, pad_h), pygame.SRCALPHA)
    pygame.draw.ellipse(pill, (0, 0, 20, alpha_pill), pill.get_rect())
    pygame.draw.ellipse(pill, (255, 255, 255, alpha_pill // 3),
                        pill.get_rect(), 1)
    px = (W - pad_w) // 2
    py = H - pad_h - 18
    surf.blit(pill, (px, py))
    surf.blit(label, (px + (pad_w - label.get_width()) // 2,
                      py + (pad_h - label.get_height()) // 2))
