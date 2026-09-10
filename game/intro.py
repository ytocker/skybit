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
    get_sky_surface_biome, draw_mountains, draw_cloud,
    blit_glow, lerp_color, rounded_rect_grad,
    UI_GOLD, UI_CREAM, WHITE, NEAR_BLACK,
)
from game import biome as _biome
from game import cloud_variants
from game import foreground
from game import sky_designs
from game import parrot as _parrot
from game.pillar_pagodas import draw_pillar_pair
from game.hud import _font, _GOLD_BRIGHT, _RED_OUTLINE
from game.entities import Coin, PowerUp


DURATION = 15.0


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
        # One random cloud design for the whole cinematic, matching the
        # one-design-per-run rule used in gameplay.
        self.cloud_variant = random.randrange(cloud_variants.VARIANT_COUNT)

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
    # An active sky design paints its own per-phase sky (same two-bucket fade);
    # only when none is active do we bake the live biome sky below.
    if sky_designs.render_active(surf, W, H, GROUND_Y,
                                 _biome.palette_for_phase(phase), phase):
        return
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
                cloud_phase: float, ground: bool = True,
                cloud_variant: int = 0) -> None:
    """Sky + mountains + (optional) floor for the given phase. Intro beats
    pass ``ground=True`` so the buff sandstone sidewalk matches gameplay."""
    palette = _biome.palette_for_phase(phase)
    _draw_sky(surf, phase)
    # Three drifting clouds for ambient depth — retint to the active sky design
    # so they match the sky, else the live palette.
    cloud_pal = sky_designs.active_cloud_palette(phase, palette) or palette
    for i, (bx, by, sc) in enumerate(
            ((40, 110, 0.85), (220, 70, 0.7), (120, 200, 1.0))):
        ox = ((bx - scroll * (0.04 + 0.02 * i)) % (W + 160)) - 80
        draw_cloud(surf, ox, by + math.sin(cloud_phase * 0.3 + i) * 3,
                   sc, variant=cloud_variant, palette=cloud_pal)
    draw_mountains(surf, scroll, GROUND_Y, W, phase=phase)
    if ground:
        # The buff sandstone sidewalk is the gameplay floor; the intro shares it
        # so the cinematic ground matches the game (was the retired grass band).
        foreground.draw_foreground_floor(surf, scroll, palette, phase)


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
                ground=True, cloud_variant=scene.cloud_variant)

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
                cloud_phase=scene.t, ground=True,
                cloud_variant=scene.cloud_variant)

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


# Tutorial sub-beats run inside the same time window the journey used to
# occupy. Each one is 3.5 s wide so labels can breathe and entities
# linger on screen.
_TUTORIAL_START = 4.0
_TUTORIAL_END   = 12.0
_TUTORIAL_LEN   = _TUTORIAL_END - _TUTORIAL_START   # 8 s

# Sub-beat lengths. All four tutorial beats run at the same tight 2.0 s
# pace — paired with the faster world scroll below, the bird now flies
# with real speed and the cinematic stops dragging. Sub-beat internals
# scale off `sub_t = sub_u * _SUB_LEN`, so the per-beat animations
# (pillar slide-in, coin trail, power-up trail) compress proportionally.
_JUMP_SUB_LEN = 2.0
_SUB_LEN = 2.0


def _label_alpha(sub_u: float) -> int:
    """Fade-in 0–0.15, hold to 0.85, fade-out to 1.0 (per-sub-beat local-u)."""
    if sub_u < 0.15:
        return int(255 * (sub_u / 0.15))
    if sub_u > 0.85:
        return int(255 * max(0.0, 1.0 - (sub_u - 0.85) / 0.15))
    return 255


def _draw_label_banner(surf: pygame.Surface, text: str, alpha: int) -> None:
    """Top-of-screen tutorial label — same gold-on-red-outline styling as
    the SKYBIT logotype and the POWER-UPS header on the help screen, so
    the tutorial reads as part of the game's visual family rather than a
    separate overlay. `alpha` drives fade-in / fade-out."""
    if alpha <= 0:
        return
    f = _font(34, True)
    fill = f.render(text, True, _GOLD_BRIGHT)
    out  = f.render(text, True, _RED_OUTLINE)
    sh   = f.render(text, True, NEAR_BLACK)
    fill.set_alpha(alpha)
    out.set_alpha(alpha)
    sh.set_alpha(int(alpha * 0.66))

    r = fill.get_rect(center=(W // 2, 110))
    PX = 3
    for ox, oy in ((-PX, 0), (PX, 0), (0, -PX), (0, PX),
                   (-PX, -PX), (PX, -PX), (-PX, PX), (PX, PX)):
        surf.blit(out, (r.x + ox, r.y + oy))
    surf.blit(sh, (r.x + 2, r.y + 3))
    surf.blit(fill, r.topleft)


def _tutorial_pip_carry_parcel(surf: pygame.Surface, pip_x: float,
                               pip_y: float) -> None:
    """Blit the parcel tucked beneath Pip — same offset the journey used."""
    par = _get_sprite("parcel")
    surf.blit(par, (int(pip_x) - par.get_width() // 2,
                    int(pip_y) + 10))


# ── Jump-demo physics ────────────────────────────────────────────────────────
# Mirrors the in-game gravity / flap / max-fall constants so the demo
# reads exactly like real gameplay — just dialled down by `_JUMP_SLOW`
# so the bird's apparent vertical speed is closer to the calm sin-bob
# of the other tutorial sub-beats. Both gravity and flap velocity scale
# by the same factor, so the trajectory shape and time-to-peak (~0.33 s)
# stay identical to gameplay; only the magnitudes shrink.
#
# 2.5 s sub-beat is divided into:
#   0.00–0.25  natural fall (no flap yet — establishes "this is what
#              happens if you don't tap")
#   0.25       flap #1
#   0.25–0.85  flap arc 1
#   0.85       flap #2
#   0.85–1.45  flap arc 2
#   1.45       flap #3
#   1.45–2.05  flap arc 3
#   2.05–2.50  quick ease-out back to baseline so the cut to AVOID
#              PILLARS feels tight rather than dwelling on a level-
#              flight tail.
_JUMP_SLOW     = 0.50     # scales velocities + gravity proportionally
_JUMP_GRAVITY  = 1600.0 * _JUMP_SLOW
_JUMP_FLAP_V   = -520.0 * _JUMP_SLOW
_JUMP_MAX_FALL =  700.0 * _JUMP_SLOW
_JUMP_FLAP_TIMES = (0.25, 0.85, 1.45)
_JUMP_SETTLE_T   = 2.05
_JUMP_SUBSTEP    = 1.0 / 120.0


def _jump_simulate(sub_t: float) -> tuple[float, float]:
    """Step-based simulation up to `sub_t` using the game's actual
    GRAVITY / FLAP_V / MAX_FALL constants. Returns (y_offset, vy)."""
    y = 0.0
    vy = 0.0
    flap_idx = 0
    flaps = _JUMP_FLAP_TIMES
    t = 0.0
    while t < sub_t:
        # Apply any flaps whose time has come.
        while flap_idx < len(flaps) and t >= flaps[flap_idx]:
            vy = _JUMP_FLAP_V
            flap_idx += 1
        step = min(_JUMP_SUBSTEP, sub_t - t)
        vy = min(vy + _JUMP_GRAVITY * step, _JUMP_MAX_FALL)
        y += vy * step
        t += step
    return y, vy


def _jump_demo_state(sub_t: float) -> tuple[float, float]:
    """Public state lookup for the jump sub-beat. Real physics through
    the third flap arc (sub_t ≤ _JUMP_SETTLE_T), then a quick ease-out
    back to (y, vy) = (0, 0) so the bird flies straight before the cut."""
    if sub_t <= _JUMP_SETTLE_T:
        return _jump_simulate(sub_t)
    # Snapshot at start of settle, then ease everything to 0.
    y0, vy0 = _jump_simulate(_JUMP_SETTLE_T)
    span = _JUMP_SUB_LEN - _JUMP_SETTLE_T
    p = max(0.0, min(1.0, (sub_t - _JUMP_SETTLE_T) / span))
    ease = 1.0 - (1.0 - p) * (1.0 - p)   # ease-out quadratic
    return y0 * (1.0 - ease), vy0 * (1.0 - p)


def _jump_tilt(vy: float) -> float:
    """Same tilt formula the in-game `Bird.tilt_deg` property uses."""
    t = max(-0.5, min(0.75, vy / 500.0))
    return -t * 55.0


def _tutorial_jump(scene: "IntroScene", surf: pygame.Surface,
                   sub_u: float) -> None:
    """Sub-beat 1 — TAP TO JUMP. Pip first falls naturally (gravity
    only, no flap), then performs two real-physics jumps using the
    game's actual GRAVITY / FLAP_V / MAX_FALL constants, then levels
    out so the cut to AVOID PILLARS is smooth."""
    # Bridge: the pickup post-house is still drifting off the left edge
    # at the start of the tutorial, mirroring the journey's old bridge.
    if sub_u < 0.22:
        bridge_t = sub_u / 0.22
        house = _get_sprite("skyhouse_post")
        anchor_cx = int(W * 0.30) - int(bridge_t * (W * 0.55))
        anchor_cy = int(H * 0.42)
        hx = anchor_cx - house.get_width() // 2
        hy = anchor_cy - house.get_height() // 2
        if bridge_t < 1.0:
            faded = house.copy()
            faded.set_alpha(int(255 * (1.0 - bridge_t)))
            surf.blit(faded, (hx, hy))

    sub_t = sub_u * _JUMP_SUB_LEN
    y_offset, vy = _jump_demo_state(sub_t)

    # Match the journey/arrival baseline x so cuts in/out are seamless.
    pip_x = W * 0.48 + math.sin(scene.t * 0.8) * 18
    pip_y = H * 0.42 + y_offset
    tilt = _jump_tilt(vy)

    _tutorial_pip_carry_parcel(surf, pip_x, pip_y)
    _draw_pip(surf, pip_x, pip_y, frame_t=scene.t * 5.5, tilt_deg=tilt)

    _draw_label_banner(surf, "TAP TO JUMP", _label_alpha(sub_u))


def _tutorial_pillars(scene: "IntroScene", surf: pygame.Surface,
                      sub_u: float) -> None:
    """Sub-beat 2 — AVOID PILLARS. A single pillar pair scrolls in from
    the right with a 170-px gap aligned to Pip's altitude; Pip dips
    slightly so he passes through it visibly."""
    # Pillar slides from off-right to off-left across the sub-beat.
    pipe_w = 58
    gap_h  = 170
    gap_y  = int(H * 0.42)
    pillar_x = int(W + 30 - sub_u * (W + 90))

    if pillar_x + pipe_w > 0 and pillar_x < W:
        top_h = max(1, gap_y - gap_h // 2)
        bot_y = gap_y + gap_h // 2
        bot_h = max(1, GROUND_Y - bot_y)
        top_rect = pygame.Rect(pillar_x, 0, pipe_w, top_h)
        bot_rect = pygame.Rect(pillar_x, bot_y, pipe_w, bot_h)
        # Resolve a palette from the current biome phase so the pillar
        # tints with the day→night cycle just like in gameplay.
        phase_now = _journey_phase(0.25)  # mid golden hour-ish
        palette = _biome.palette_for_phase(phase_now)
        draw_pillar_pair(surf, top_rect, bot_rect, palette, seed=4242,
                         phase=phase_now)

    # Pip — same calm bob the journey/arrival use so cuts are seamless.
    pip_x = W * 0.48 + math.sin(scene.t * 0.8) * 18
    pip_y = H * 0.42 + math.sin(scene.t * 1.5) * 14
    tilt = math.sin(scene.t * 1.5) * -6.0

    _tutorial_pip_carry_parcel(surf, pip_x, pip_y)
    _draw_pip(surf, pip_x, pip_y, frame_t=scene.t * 5.0, tilt_deg=tilt)

    _draw_label_banner(surf, "AVOID PILLARS", _label_alpha(sub_u))


# Coin trail config — five coins in a sine-wave pattern, scrolling in
# from off-right and crossing Pip one after the other.
_COIN_COUNT     = 5
_COIN_SPACING   = 60
_COIN_X0        = float(W) + 50.0   # initial x of the first coin
_COIN_SCROLL_PX = 260.0              # px/s the trail scrolls left
                                     # — bumped from 175 so the 5-coin
                                     # / 3-power-up trails still cross
                                     # Pip inside the 2.0 s sub-beat.
_COIN_AMP       = 28


def _coin_x_at(idx: int, sub_t: float) -> float:
    """Deterministic screen-x of coin `idx` at time `sub_t` into the
    coins sub-beat."""
    return _COIN_X0 + idx * _COIN_SPACING - sub_t * _COIN_SCROLL_PX


def _coin_collect_t(idx: int, pip_x: float) -> float:
    """Time (within the coins sub-beat) at which coin `idx` reaches Pip."""
    return (_COIN_X0 + idx * _COIN_SPACING - pip_x) / _COIN_SCROLL_PX


def _draw_pickup_sparkle(surf: pygame.Surface, cx: int, cy: int,
                         age: float) -> None:
    """6-particle gold/white sparkle burst, fades over 0.4 s."""
    if age < 0 or age > 0.4:
        return
    fade = max(0.0, 1.0 - age / 0.4)
    alpha = int(255 * fade)
    for i in range(6):
        ang = math.tau * i / 6
        r = 4 + age * 60
        px = int(cx + math.cos(ang) * r)
        py = int(cy + math.sin(ang) * r)
        col = (255, 230, 90) if i % 2 == 0 else (255, 250, 220)
        s = pygame.Surface((6, 6), pygame.SRCALPHA)
        pygame.draw.circle(s, (*col, alpha), (3, 3), 2)
        surf.blit(s, (px - 3, py - 3), special_flags=pygame.BLEND_ADD)


def _tutorial_coins(scene: "IntroScene", surf: pygame.Surface,
                    sub_u: float) -> None:
    """Sub-beat 3 — PICK UP COINS. A trail of five coins scrolls in from
    the right; each one pops with a sparkle as Pip passes through it."""
    sub_t = sub_u * _SUB_LEN
    # Same baseline bob as the journey/arrival so cuts are seamless.
    pip_x = W * 0.48 + math.sin(scene.t * 0.8) * 18
    pip_y = H * 0.42 + math.sin(scene.t * 1.5) * 14

    # Cache one Coin per index on the scene so the spin animation
    # advances smoothly across frames.
    coins = getattr(scene, "_tutorial_coins_cache", None)
    if coins is None:
        coins = [Coin(0, 0) for _ in range(_COIN_COUNT)]
        scene._tutorial_coins_cache = coins

    for idx, coin in enumerate(coins):
        # Update the spin/float animation every frame so coins look
        # alive even before they reach Pip.
        coin.update(1 / 60)
        # Sine-wave y so the trail reads as an arc, not a flat line.
        y_offset = math.sin(idx * 0.9) * _COIN_AMP
        coin.x = _coin_x_at(idx, sub_t)
        coin.y = H * 0.42 + y_offset

        # Collection trigger uses the bob-baseline x so it's deterministic
        # across frames — sin offset is small enough (±18 px) that visual
        # alignment with Pip's drawn position stays convincing.
        baseline_x = W * 0.48
        collect_t = _coin_collect_t(idx, baseline_x)
        if sub_t < collect_t:
            # Not yet collected — draw normally if on-screen.
            if -20 < coin.x < W + 20:
                coin.draw(surf)
        else:
            # Collected — draw the sparkle burst and skip the coin.
            age = sub_t - collect_t
            _draw_pickup_sparkle(surf, int(baseline_x), int(coin.y), age)

    _tutorial_pip_carry_parcel(surf, pip_x, pip_y)
    _draw_pip(surf, pip_x, pip_y, frame_t=scene.t * 5.5,
              tilt_deg=math.sin(scene.t * 1.5) * -6.0)

    _draw_label_banner(surf, "PICK UP COINS", _label_alpha(sub_u))


# Power-up trail config — three power-ups, more spaced than the coins
# so each one is clearly readable.
_POWERUP_KINDS    = ("triple", "magnet", "slowmo")
_POWERUP_SPACING  = 110
_POWERUP_X0       = float(W) + 50.0
_POWERUP_OFFSETS  = (-32, 22, -8)   # y-offsets per item, varied for shape


def _tutorial_powerups(scene: "IntroScene", surf: pygame.Surface,
                       sub_u: float) -> None:
    """Sub-beat 4 — TAKE POWER-UPS. Three power-ups scroll past in Pip's
    flight path. He doesn't collect them (per spec). The destination
    cottage starts sliding in from off-screen-right during the last 60 %
    of this sub-beat to bridge the cut into the arrival beat."""
    sub_t = sub_u * _SUB_LEN

    # Cache the PowerUp instances so .pulse advances smoothly.
    pus = getattr(scene, "_tutorial_pus_cache", None)
    if pus is None:
        pus = [PowerUp(0, 0, kind) for kind in _POWERUP_KINDS]
        scene._tutorial_pus_cache = pus

    for idx, pu in enumerate(pus):
        pu.update(1 / 60)
        x = _POWERUP_X0 + idx * _POWERUP_SPACING - sub_t * _COIN_SCROLL_PX
        pu.x = x
        pu.y = H * 0.42 + _POWERUP_OFFSETS[idx]
        if -30 < pu.x < W + 30:
            pu.draw(surf)

    # Destination cottage slide-in (last 60 % of this sub-beat). Endpoint
    # matches the arrival beat's expected position so the cut is seamless.
    if sub_u >= 0.40:
        approach = (sub_u - 0.40) / 0.60
        home = _get_sprite("skyhouse_home")
        home_cx_off = W + home.get_width() // 2 + 20
        home_cx_end = W // 2
        home_cx_now = int(home_cx_off + (home_cx_end - home_cx_off) * approach)
        home_cy_now = int(H * 0.55) + int(math.sin(scene.t * 0.9) * 3)
        surf.blit(home,
                  (home_cx_now - home.get_width() // 2,
                   home_cy_now - home.get_height() // 2))

    # Match the journey/arrival baseline bob exactly so the cut into
    # Beat 4 is pixel-perfect.
    pip_x = W * 0.48 + math.sin(scene.t * 0.8) * 18
    pip_y = H * 0.42 + math.sin(scene.t * 1.5) * 14
    tilt = math.sin(scene.t * 1.5) * -6.0

    _tutorial_pip_carry_parcel(surf, pip_x, pip_y)
    _draw_pip(surf, pip_x, pip_y, frame_t=scene.t * 5.0, tilt_deg=tilt)

    _draw_label_banner(surf, "TAKE POWER-UPS", _label_alpha(sub_u))


def _beat_tutorial(scene: "IntroScene", surf: pygame.Surface,
                   u: float) -> None:
    """Tutorial dispatcher — replaces the old `_beat_journey`. Splits the
    six-second window into four sub-beats and keeps the day→night biome
    cycle running across all of them, exactly like the journey did."""
    # Same biome phase + scroll progression the journey beat used, just
    # stretched across the new (slightly longer) tutorial window.
    phase = _journey_phase(u)
    # Faster scroll across the tutorial — was 280 px over 14 s (~20 px/s),
    # which made the bird feel becalmed compared to the in-game ~160 px/s
    # base speed. 400 px over 8 s = 50 px/s reads as a calm cruise: the
    # bird is clearly travelling, but the cinematic still feels measured.
    # Arrival beat's starting scroll below continues from here.
    scroll = 16.0 + u * 400.0
    _draw_world(surf, phase, scroll=scroll, cloud_phase=scene.t, ground=True,
                cloud_variant=scene.cloud_variant)

    # A distant V-flock keeps the world alive; same window the journey
    # had it on (now expressed in tutorial-local-u).
    if 0.55 < u < 0.85:
        flock_u = (u - 0.55) / 0.30
        fx = W + 40 - flock_u * (W + 80)
        _draw_distant_flock(surf, scene.t, fx)

    # Sub-beat dispatch. Slice lengths are no longer equal — TAP TO
    # JUMP is shorter to skip the redundant level-flight tail — so the
    # easiest path is to compute boundaries in tutorial-local seconds.
    tt = u * _TUTORIAL_LEN
    b1 = _JUMP_SUB_LEN
    b2 = b1 + _SUB_LEN
    b3 = b2 + _SUB_LEN
    if tt < b1:
        _tutorial_jump(scene, surf, tt / _JUMP_SUB_LEN)
    elif tt < b2:
        _tutorial_pillars(scene, surf, (tt - b1) / _SUB_LEN)
    elif tt < b3:
        _tutorial_coins(scene, surf, (tt - b2) / _SUB_LEN)
    else:
        _tutorial_powerups(scene, surf, (tt - b3) / _SUB_LEN)


# ── beat 4: Arrival (10.0 – 11.0) ────────────────────────────────────────────

def _beat_arrival(scene: "IntroScene", surf: pygame.Surface, u: float) -> None:
    """Pip glides up to a tiny cottage floating on a cloud and leaves the
    parcel on its doorstep. No pillar, no mailbox — the destination is a
    house in the sky."""
    # Delivery happens at night — the journey ended there, so beat 4 holds
    # the same starlit phase Pip arrived under. Scroll continues from
    # the tutorial beat's end value (16 + 400 = 416) so the cloud
    # parallax doesn't pop on the cut.
    phase = 0.62
    _draw_world(surf, phase, scroll=416.0 + u * 30.0,
                cloud_phase=scene.t, ground=True,
                cloud_variant=scene.cloud_variant)

    # Floating sky-house, centred. The cottage was approached during the
    # last 35% of the journey (scrolled in from off-screen-right), so the
    # cut here is positionally seamless — it just keeps bobbing.
    house = _get_sprite("skyhouse_home")
    anc = _get_house_anchors("home")
    house_cx = W // 2
    house_cy_settled = int(H * 0.55)
    house_cy_now = house_cy_settled + int(math.sin(scene.t * 0.9) * 3)
    house_x = house_cx - house.get_width() // 2
    house_y_now = house_cy_now - house.get_height() // 2
    surf.blit(house, (house_x, house_y_now))

    # Doorstep follows the live cottage bob.
    doorstep_x = house_x + anc["doorstep"][0]
    doorstep_y = house_y_now + anc["doorstep"][1]

    # Pip's start pose tracks the journey's live sin-bob so the cut from
    # beat 3 is seamless even mid-bob. Pip glides from there down to the
    # doorstep, drops the parcel, and continues onward.
    par = _get_sprite("parcel")
    start_x = W * 0.48 + math.sin(scene.t * 0.8) * 18
    start_y = H * 0.42 + math.sin(scene.t * 1.5) * 14
    drop_x, drop_y = doorstep_x + 38, doorstep_y - 30
    # Exit endpoint takes Pip clear off the upper-right edge of the
    # screen so the intro ends on his departure.
    exit_x, exit_y = W + 80, doorstep_y - 180
    # Three phases: approach (u 0–0.40), pause at doorstep delivering the
    # parcel (0.40–0.55), exit off-screen (0.55–1.00).
    if u < 0.40:
        ease = _smoothstep(u / 0.40)
        pip_x = start_x + (drop_x - start_x) * ease
        pip_y = start_y + (drop_y - start_y) * ease
        tilt = -10.0 * (1.0 - ease)
        carry_x = int(pip_x) - par.get_width() // 2
        carry_y = int(pip_y) + 10
        surf.blit(par, (carry_x, carry_y))
        _draw_pip(surf, pip_x, pip_y, frame_t=scene.t * 4.0, tilt_deg=tilt)
    elif u < 0.55:
        # Brief pause at the doorstep — parcel just delivered, Pip is
        # hovering for a beat before lifting off.
        rest_x = doorstep_x - par.get_width() // 2
        rest_y = doorstep_y - par.get_height()
        surf.blit(par, (rest_x, rest_y))
        _draw_pip(surf, drop_x, drop_y, frame_t=scene.t * 4.0, tilt_deg=0)
    else:
        rest_x = doorstep_x - par.get_width() // 2
        rest_y = doorstep_y - par.get_height()
        surf.blit(par, (rest_x, rest_y))
        ease = _smoothstep((u - 0.55) / 0.45)
        pip_x = drop_x + (exit_x - drop_x) * ease
        pip_y = drop_y + (exit_y - drop_y) * ease
        tilt = 14.0 * ease  # banks up as he soars off-screen
        _draw_pip(surf, pip_x, pip_y, frame_t=scene.t * 4.0, tilt_deg=tilt)


# ── final beat dispatcher ────────────────────────────────────────────────────

def _dispatch_beat(scene: "IntroScene", surf: pygame.Surface) -> None:
    t = scene.t
    # Beat windows. The old "journey" beat was repurposed as a four-step
    # gameplay tutorial (jump / pillars / coins / power-ups), still cycling
    # the day→night biome the journey did. Lengths are derived from the
    # constants above so trimming the tutorial doesn't strand the
    # arrival beat past the new DURATION.
    #   dawn      0.0 – 1.0
    #   handoff   1.0 – _TUTORIAL_START          (handoff_len = _T_START - 1)
    #   tutorial  _T_START – _T_END              (_TUTORIAL_LEN s)
    #   arrival   _T_END – DURATION              (arrival_len = DURATION - _T_END)
    handoff_len = _TUTORIAL_START - 1.0
    arrival_len = DURATION - _TUTORIAL_END
    if t < 1.0:
        _beat_dawn(scene, surf, t / 1.0)
    elif t < _TUTORIAL_START:
        _beat_handoff(scene, surf, (t - 1.0) / handoff_len)
    elif t < _TUTORIAL_END:
        _beat_tutorial(scene, surf, (t - _TUTORIAL_START) / _TUTORIAL_LEN)
    elif t < DURATION:
        _beat_arrival(scene, surf, (t - _TUTORIAL_END) / arrival_len)
    else:
        _beat_arrival(scene, surf, 1.0)


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
