"""Cycle-finale cheering crowd — Round 1 exploration sheet.

The cycle-finale already plants a vertical white finish-line stripe + "{N} Day"
white label on the ground band, directly beneath the chest's world-x (see
``CelebrationGroundMarker`` in ``game/entities.py``). User wants a small,
festive crowd of cheering figures painted next to the stripe — the moment
the player crosses the finish line should feel celebrated, not lonely.

Five distinct directions, one per cell:

  V1 — Chibi humans · RIGHT-side only · 5 figures · pom-poms / megaphone /
       drum / trumpet / flag · arms-raised + jumping.
  V2 — Parrot-people mix · BOTH sides · 7 figures · pom-poms x2 / tambourine /
       party-horn / drum / flag x2 · waving + jumping.
  V3 — Silhouette stadium row · RIGHT-side only · 7 figures · trumpet /
       megaphone / drum / cymbals / flag / pom-poms / horn · arms-raised.
  V4 — Classic stadium-fan jerseys · BOTH sides · 5 figures · trumpet x2 /
       big drum / flag / pom-poms · holding-up-instrument.
  V5 — Pixel-mascot animals · LEFT-side only · 3 figures · drum / megaphone /
       flag · jumping + waving.

Each cell renders on a real slice of the game's ground band so the figure
heights, finish-line stripe, and "1 Day" label can be judged against the
actual environment (no separate "preview canvas" lying about scale). Top
title strip names + describes each variant.

Output: docs/treasure_box/cheering_crowd_round1.png  (doc-only; not shipped)
"""
from __future__ import annotations

import math
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(THIS_DIR)
sys.path.insert(0, REPO_ROOT)

pygame.init()
pygame.display.set_mode((1, 1))

from game.config import GROUND_Y, H, W
from game.draw import draw_ground, GROUND_TOP, GROUND_MID, GROUND_BOT
from game.entities import CelebrationGroundMarker

# ── sheet layout constants ─────────────────────────────────────────────────
# 5 cells in a 2×3 grid; the 6th tile is a legend / spec block. Each cell is
# 360 px wide × 200 px tall so the crowd can be judged at gameplay scale
# (Pip is 28 px, COIN_R is 13 — figures stay 22-32 px wide).
CELL_W = 360
CELL_H = 200
COLS   = 3
ROWS   = 2
TITLE_BAND_H = 78
PAD = 12
SHEET_W = COLS * CELL_W + (COLS + 1) * PAD
SHEET_H = TITLE_BAND_H + ROWS * CELL_H + (ROWS + 1) * PAD

# Cycle-finale moment lands on the DAY palette wrap (see biome.py), so the
# sky behind the chest in the reference screenshot is bright cyan. We mirror
# those tones so the cells match the in-game environment.
SKY_TOP   = (90, 170, 230)
SKY_MID   = (140, 200, 240)
SKY_BOT   = (190, 230, 250)

# Cell-local ground band: keep the same 45-px band as the game.
CELL_GROUND_Y = GROUND_Y - (H - CELL_H)   # cell-local y for the grass line

# Festive palette family — matches CelebrationBunting.COLOURS so the crowd
# sits inside the cycle-finale colour story instead of clashing.
GOLD   = (255, 220, 110)
RED    = (220,  64,  32)
BLUE   = ( 96, 176, 232)
CREAM  = (252, 244, 218)
GREEN  = (108, 192, 96)
PURPLE = (170, 110, 200)
INK    = ( 30,  20,   8)
SKIN_LIGHT = (235, 195, 150)
SKIN_DARK  = (185, 130, 95)
SKIN_DEEP  = (135,  85, 60)
PARROT_BODY = (110, 200, 100)
PARROT_DARK = ( 55, 140,  70)
PARROT_BEAK = (255, 195,  60)


# ── helpers: ground slice + finish-line stripe + label ─────────────────────

def _draw_sky(surf: pygame.Surface, cell_h: int) -> None:
    """Vertical sky gradient confined to the cell so the crowd is read
    against a believable horizon, not a flat box."""
    for y in range(cell_h):
        t = y / max(1, cell_h - 1)
        if t < 0.5:
            seg = t / 0.5
            c = (
                int(SKY_TOP[0] + (SKY_MID[0] - SKY_TOP[0]) * seg),
                int(SKY_TOP[1] + (SKY_MID[1] - SKY_TOP[1]) * seg),
                int(SKY_TOP[2] + (SKY_MID[2] - SKY_TOP[2]) * seg),
            )
        else:
            seg = (t - 0.5) / 0.5
            c = (
                int(SKY_MID[0] + (SKY_BOT[0] - SKY_MID[0]) * seg),
                int(SKY_MID[1] + (SKY_BOT[1] - SKY_MID[1]) * seg),
                int(SKY_MID[2] + (SKY_BOT[2] - SKY_MID[2]) * seg),
            )
        pygame.draw.line(surf, c, (0, y), (surf.get_width(), y))


def _draw_cell_ground(surf: pygame.Surface) -> None:
    """Real grass + soil band, using the live game draw routine so flower
    density, blade tufts, and soil shading match what the player sees."""
    draw_ground(surf, CELL_GROUND_Y, surf.get_width(), CELL_H, 0.0,
                GROUND_TOP, GROUND_MID, GROUND_BOT)


def _draw_finish_marker(surf: pygame.Surface, stripe_x: int) -> None:
    """Drop the real ``CelebrationGroundMarker`` sprite into the cell.
    Built with day=1 so the label reads "1 Day" as in the reference."""
    marker = CelebrationGroundMarker(world_x=stripe_x, day=1)
    spr = marker._sprite  # WHY: re-using the cached label keeps stroke/colour identical
    # The marker's draw() expects screen GROUND_Y; we override the y so the
    # composite lands inside the cell's local ground band.
    target_top = CELL_GROUND_Y + CelebrationGroundMarker.TOP_PAD
    target_left = stripe_x - CelebrationGroundMarker.LINE_W // 2
    surf.blit(spr, (target_left, target_top))


# ── shared figure-building helpers ─────────────────────────────────────────

def _draw_pompom(surf, cx, cy, col, r=4):
    """Fluffy pom-pom — soft cluster of 5 tiny circles for a furry edge."""
    for dx, dy in ((-2, -1), (2, -1), (0, -2), (-1, 1), (2, 1)):
        pygame.draw.circle(surf, col, (cx + dx, cy + dy), 2)
    pygame.draw.circle(surf, _shade(col, -30), (cx, cy), 1)


def _shade(col, d):
    return (max(0, min(255, col[0] + d)),
            max(0, min(255, col[1] + d)),
            max(0, min(255, col[2] + d)))


def _draw_trumpet(surf, x, y, col=(220, 180, 50)):
    """Tiny upraised trumpet — stem + flared bell, gold."""
    pygame.draw.line(surf, col, (x, y), (x + 4, y - 4), 2)
    pygame.draw.polygon(surf, col, [
        (x + 4, y - 4), (x + 8, y - 8), (x + 6, y - 9), (x + 3, y - 5)
    ])
    pygame.draw.polygon(surf, _shade(col, -50), [
        (x + 4, y - 4), (x + 8, y - 8), (x + 6, y - 9), (x + 3, y - 5)
    ], 1)


def _draw_drum(surf, cx, cy, body_col=RED, rim_col=GOLD):
    """Snare-style drum slung at the waist — small barrel + rims + tension
    lines. Drawn front-on so it reads at 22 px wide."""
    w, h = 14, 9
    rect = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
    pygame.draw.rect(surf, body_col, rect, border_radius=2)
    pygame.draw.rect(surf, rim_col, (rect.x, rect.y, rect.w, 2))
    pygame.draw.rect(surf, rim_col, (rect.x, rect.y + rect.h - 2, rect.w, 2))
    # Zigzag tension lines
    for k in range(4):
        kx = rect.x + 2 + k * 3
        pygame.draw.line(surf, _shade(body_col, -40),
                         (kx, rect.y + 2), (kx + 1, rect.y + rect.h - 2), 1)
    pygame.draw.rect(surf, INK, rect, 1, border_radius=2)


def _draw_megaphone(surf, x, y, col=RED):
    """Megaphone cone pointing up-and-right, gripped at the wrist."""
    pts = [(x, y), (x + 9, y - 8), (x + 11, y - 5), (x + 3, y + 2)]
    pygame.draw.polygon(surf, col, pts)
    pygame.draw.polygon(surf, INK, pts, 1)
    pygame.draw.line(surf, CREAM, (x + 2, y - 1), (x + 8, y - 6), 1)


def _draw_flag(surf, x_base, y_base, pole_h=18, flag_col=GOLD, pole_col=INK):
    """Flag on a thin pole — rectangular flag with a wavy free edge."""
    pygame.draw.line(surf, pole_col, (x_base, y_base),
                     (x_base, y_base - pole_h), 1)
    pygame.draw.polygon(surf, flag_col, [
        (x_base, y_base - pole_h),
        (x_base + 10, y_base - pole_h + 2),
        (x_base + 9, y_base - pole_h + 5),
        (x_base + 10, y_base - pole_h + 8),
        (x_base, y_base - pole_h + 7),
    ])
    pygame.draw.polygon(surf, _shade(flag_col, -50), [
        (x_base, y_base - pole_h),
        (x_base + 10, y_base - pole_h + 2),
        (x_base + 9, y_base - pole_h + 5),
        (x_base + 10, y_base - pole_h + 8),
        (x_base, y_base - pole_h + 7),
    ], 1)


def _draw_tambourine(surf, cx, cy, body_col=GOLD):
    """Tambourine — disc + 4 jingle slots."""
    pygame.draw.circle(surf, body_col, (cx, cy), 5)
    pygame.draw.circle(surf, _shade(body_col, -60), (cx, cy), 5, 1)
    pygame.draw.circle(surf, CREAM, (cx, cy), 3)
    pygame.draw.circle(surf, _shade(body_col, -40), (cx, cy), 3, 1)
    for k in range(4):
        ang = k * (math.pi / 2) + 0.4
        jx = cx + int(math.cos(ang) * 5)
        jy = cy + int(math.sin(ang) * 5)
        pygame.draw.circle(surf, CREAM, (jx, jy), 1)


def _draw_party_horn(surf, x, y, col=GOLD):
    """Party horn — short blowpipe + curled streamer tip."""
    pygame.draw.line(surf, col, (x, y), (x + 7, y - 2), 2)
    pygame.draw.line(surf, RED, (x + 7, y - 2), (x + 11, y - 5), 2)
    pygame.draw.line(surf, BLUE, (x + 11, y - 5), (x + 13, y - 3), 1)
    pygame.draw.circle(surf, CREAM, (x + 13, y - 3), 1)


def _draw_cymbals(surf, cx, cy, col=GOLD):
    """Pair of clashed cymbals — two filled ellipses, slightly offset."""
    pygame.draw.ellipse(surf, col, (cx - 6, cy - 2, 6, 4))
    pygame.draw.ellipse(surf, _shade(col, -60), (cx - 6, cy - 2, 6, 4), 1)
    pygame.draw.ellipse(surf, col, (cx, cy - 2, 6, 4))
    pygame.draw.ellipse(surf, _shade(col, -60), (cx, cy - 2, 6, 4), 1)
    pygame.draw.ellipse(surf, CREAM, (cx - 5, cy - 1, 4, 2))


# ── V1 — Chibi humans, right-side only ─────────────────────────────────────

def _chibi_human(surf, x, ground_y, shirt, pants=(60, 60, 100), hair=(80, 50, 30),
                 jump=0, arms="up", instrument=None):
    """Small chibi figure ~22 px wide × 30 px tall. Big head, simple body.

    ``jump`` shifts the whole sprite up (0-5 px). ``arms`` chooses arm pose.
    ``instrument`` is an optional callable taking (surf) — drawn after arms
    so it sits on top of the wrist."""
    feet_y = ground_y - 1 - jump
    head_r = 7
    body_top_y = feet_y - 14
    head_cy = body_top_y - head_r + 1
    # Shadow
    shadow = pygame.Surface((18, 4), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow, (0, 0, 0, 70), (0, 0, 18, 4))
    surf.blit(shadow, (x - 9, ground_y))
    # Legs (slight stride in jump)
    leg_w = 3
    if jump > 0:
        pygame.draw.line(surf, pants, (x - 2, body_top_y + 12),
                         (x - 4, feet_y), leg_w)
        pygame.draw.line(surf, pants, (x + 2, body_top_y + 12),
                         (x + 4, feet_y), leg_w)
    else:
        pygame.draw.rect(surf, pants, (x - 4, body_top_y + 12, 3, feet_y - body_top_y - 12))
        pygame.draw.rect(surf, pants, (x + 1, body_top_y + 12, 3, feet_y - body_top_y - 12))
    # Body / shirt
    pygame.draw.rect(surf, shirt, (x - 5, body_top_y, 10, 14), border_radius=2)
    pygame.draw.rect(surf, _shade(shirt, -40), (x - 5, body_top_y, 10, 14), 1, border_radius=2)
    # Head
    pygame.draw.circle(surf, SKIN_LIGHT, (x, head_cy), head_r)
    pygame.draw.circle(surf, _shade(SKIN_LIGHT, -50), (x, head_cy), head_r, 1)
    # Hair cap
    pygame.draw.ellipse(surf, hair, (x - head_r, head_cy - head_r,
                                     head_r * 2, head_r))
    pygame.draw.ellipse(surf, _shade(hair, -40),
                        (x - head_r, head_cy - head_r, head_r * 2, head_r), 1)
    # Eyes
    pygame.draw.circle(surf, INK, (x - 2, head_cy + 1), 1)
    pygame.draw.circle(surf, INK, (x + 2, head_cy + 1), 1)
    # Mouth — open cheering shout
    pygame.draw.ellipse(surf, INK, (x - 1, head_cy + 3, 3, 2))
    pygame.draw.ellipse(surf, (200, 80, 90), (x - 1, head_cy + 3, 3, 2), 0)
    # Arms — both up
    arm_col = SKIN_LIGHT
    arm_dark = _shade(SKIN_LIGHT, -40)
    if arms == "up":
        # Both arms reach above the head
        pygame.draw.line(surf, shirt, (x - 4, body_top_y + 3),
                         (x - 8, body_top_y - 4), 3)
        pygame.draw.line(surf, shirt, (x + 4, body_top_y + 3),
                         (x + 8, body_top_y - 4), 3)
        pygame.draw.circle(surf, arm_col, (x - 8, body_top_y - 5), 2)
        pygame.draw.circle(surf, arm_col, (x + 8, body_top_y - 5), 2)
        pygame.draw.circle(surf, arm_dark, (x - 8, body_top_y - 5), 2, 1)
        pygame.draw.circle(surf, arm_dark, (x + 8, body_top_y - 5), 2, 1)
        if instrument:
            instrument(surf, x + 8, body_top_y - 5)
    elif arms == "wave":
        # One arm up, one out
        pygame.draw.line(surf, shirt, (x - 4, body_top_y + 3),
                         (x - 9, body_top_y + 1), 3)
        pygame.draw.line(surf, shirt, (x + 4, body_top_y + 3),
                         (x + 7, body_top_y - 6), 3)
        pygame.draw.circle(surf, arm_col, (x - 9, body_top_y + 1), 2)
        pygame.draw.circle(surf, arm_col, (x + 7, body_top_y - 6), 2)
        if instrument:
            instrument(surf, x + 7, body_top_y - 6)


def draw_variant_1(surf: pygame.Surface, stripe_x: int) -> None:
    """V1 — Chibi humans, right-side only, 5 figures, mixed instruments,
    arms-raised + jumping."""
    gy = CELL_GROUND_Y + 4
    # 5 figures lined up to the right of the stripe; alternating jump phase
    specs = [
        (stripe_x + 20, GOLD,  (60,  60, 110), (90,  50, 30), 4, "up",
         lambda s, hx, hy: _draw_pompom(s, hx, hy - 3, GOLD)),
        (stripe_x + 50, RED,   (40,  40,  90), (60, 30, 20), 0, "up",
         lambda s, hx, hy: _draw_megaphone(s, hx - 2, hy - 1, RED)),
        (stripe_x + 80, BLUE,  (80,  60,  40), (220, 200, 160), 3, "up",
         lambda s, hx, hy: _draw_drum(s, hx - 4, hy + 10, RED, GOLD)),
        (stripe_x + 110, CREAM, (90, 60, 30), (50, 30, 15), 0, "up",
         lambda s, hx, hy: _draw_trumpet(s, hx - 1, hy)),
        (stripe_x + 142, GREEN, (50,  40,  90), (200, 140, 90), 5, "up",
         lambda s, hx, hy: _draw_flag(s, hx, hy + 6, 16, GOLD)),
    ]
    for fx, shirt, pants, hair, jump, arms, instr in specs:
        _chibi_human(surf, fx, gy, shirt, pants, hair, jump, arms, instr)


# ── V2 — Parrot-people mix, both sides ─────────────────────────────────────

def _parrot_person(surf, x, ground_y, body=PARROT_BODY, belly=GOLD,
                   jump=0, arms="up", instrument=None, headband=None):
    """Anthropomorphic macaw — round green body, yellow belly, beak, tiny
    feet. Reads as a Pip cousin so the crowd feels native to Skybit."""
    feet_y = ground_y - 1 - jump
    body_h = 18
    body_top = feet_y - body_h
    # Shadow
    shadow = pygame.Surface((22, 4), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow, (0, 0, 0, 70), (0, 0, 22, 4))
    surf.blit(shadow, (x - 11, ground_y))
    # Tiny orange feet
    pygame.draw.line(surf, PARROT_BEAK, (x - 3, feet_y), (x - 3, feet_y + 1), 2)
    pygame.draw.line(surf, PARROT_BEAK, (x + 3, feet_y), (x + 3, feet_y + 1), 2)
    # Round body
    pygame.draw.ellipse(surf, body, (x - 8, body_top, 16, body_h))
    pygame.draw.ellipse(surf, _shade(body, -50), (x - 8, body_top, 16, body_h), 1)
    # Belly patch
    pygame.draw.ellipse(surf, belly, (x - 5, body_top + 7, 10, 10))
    # Head (sits a bit above body)
    head_cy = body_top + 4
    pygame.draw.ellipse(surf, body, (x - 7, head_cy - 7, 14, 12))
    pygame.draw.ellipse(surf, _shade(body, -60), (x - 7, head_cy - 7, 14, 12), 1)
    # Beak
    pygame.draw.polygon(surf, PARROT_BEAK,
                        [(x + 6, head_cy), (x + 11, head_cy + 1),
                         (x + 6, head_cy + 3)])
    pygame.draw.polygon(surf, _shade(PARROT_BEAK, -60),
                        [(x + 6, head_cy), (x + 11, head_cy + 1),
                         (x + 6, head_cy + 3)], 1)
    # Eye
    pygame.draw.circle(surf, CREAM, (x + 3, head_cy - 1), 2)
    pygame.draw.circle(surf, INK,   (x + 4, head_cy - 1), 1)
    # Headband (optional fan-spirit accent)
    if headband is not None:
        pygame.draw.rect(surf, headband, (x - 7, head_cy - 7, 14, 2))
        pygame.draw.line(surf, _shade(headband, -50),
                         (x - 7, head_cy - 5), (x + 6, head_cy - 5), 1)
    # Wings raised as arms
    if arms == "up":
        pygame.draw.polygon(surf, _shade(body, -30),
                            [(x - 7, body_top + 4), (x - 11, body_top - 4),
                             (x - 8, body_top - 3), (x - 5, body_top + 5)])
        pygame.draw.polygon(surf, _shade(body, -30),
                            [(x + 7, body_top + 4), (x + 11, body_top - 4),
                             (x + 8, body_top - 3), (x + 5, body_top + 5)])
        if instrument:
            instrument(surf, x + 10, body_top - 4)
    elif arms == "wave":
        pygame.draw.polygon(surf, _shade(body, -30),
                            [(x - 7, body_top + 4), (x - 12, body_top + 1),
                             (x - 9, body_top + 4), (x - 6, body_top + 8)])
        pygame.draw.polygon(surf, _shade(body, -30),
                            [(x + 7, body_top + 4), (x + 11, body_top - 5),
                             (x + 8, body_top - 4), (x + 5, body_top + 5)])
        if instrument:
            instrument(surf, x + 10, body_top - 5)


def draw_variant_2(surf: pygame.Surface, stripe_x: int) -> None:
    """V2 — Parrot-people mix, both sides, 7 figures, waving + jumping,
    pom-poms + tambourine + party-horn + drum + flag x2."""
    gy = CELL_GROUND_Y + 4
    # LEFT side — 3 figures (mix of parrots + chibi)
    _parrot_person(surf, stripe_x - 130, gy, PARROT_BODY, GOLD, 4, "up",
                   lambda s, hx, hy: _draw_flag(s, hx, hy + 5, 16, RED), GOLD)
    _chibi_human(surf, stripe_x - 100, gy, BLUE, (30, 30, 80), (60, 30, 15),
                 0, "up", lambda s, hx, hy: _draw_tambourine(s, hx, hy - 2, GOLD))
    _parrot_person(surf, stripe_x - 70, gy, PARROT_BODY, CREAM, 3, "wave",
                   lambda s, hx, hy: _draw_pompom(s, hx, hy, RED), RED)
    # RIGHT side — 4 figures
    _chibi_human(surf, stripe_x + 22, gy, RED, (60, 40, 20), (40, 25, 15),
                 5, "up", lambda s, hx, hy: _draw_pompom(s, hx, hy - 2, GOLD))
    _parrot_person(surf, stripe_x + 55, gy, PARROT_BODY, GOLD, 0, "up",
                   lambda s, hx, hy: _draw_party_horn(s, hx - 2, hy + 2, GOLD), BLUE)
    _chibi_human(surf, stripe_x + 90, gy, GOLD, (80, 60, 30), (90, 50, 20),
                 2, "up", lambda s, hx, hy: _draw_drum(s, hx - 4, hy + 10, RED, GOLD))
    _parrot_person(surf, stripe_x + 125, gy, PARROT_BODY, GOLD, 4, "wave",
                   lambda s, hx, hy: _draw_flag(s, hx, hy + 5, 16, BLUE), CREAM)


# ── V3 — Silhouette stadium row, right-side only ───────────────────────────

def _silhouette_fan(surf, x, ground_y, jump=0, hat=None, instrument=None):
    """Backlit fan silhouette — no shading, pure dark form against the
    bright sky. ~22 px wide × 30 px tall."""
    feet_y = ground_y - 1 - jump
    head_r = 6
    body_top = feet_y - 14
    head_cy = body_top - head_r + 1
    sil = ( 35,  35,  55)
    # Shadow disc
    shadow = pygame.Surface((18, 4), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow, (0, 0, 0, 90), (0, 0, 18, 4))
    surf.blit(shadow, (x - 9, ground_y))
    # Legs
    if jump > 0:
        pygame.draw.line(surf, sil, (x - 2, body_top + 12), (x - 4, feet_y), 3)
        pygame.draw.line(surf, sil, (x + 2, body_top + 12), (x + 4, feet_y), 3)
    else:
        pygame.draw.rect(surf, sil, (x - 4, body_top + 12, 3, feet_y - body_top - 12))
        pygame.draw.rect(surf, sil, (x + 1, body_top + 12, 3, feet_y - body_top - 12))
    # Body
    pygame.draw.rect(surf, sil, (x - 5, body_top, 10, 14), border_radius=2)
    # Head
    pygame.draw.circle(surf, sil, (x, head_cy), head_r)
    # Hat tab (optional festive triangle)
    if hat is not None:
        pygame.draw.polygon(surf, hat,
                            [(x - head_r, head_cy - head_r + 1),
                             (x + head_r, head_cy - head_r + 1),
                             (x, head_cy - head_r - 6)])
        pygame.draw.circle(surf, CREAM, (x, head_cy - head_r - 6), 1)
    # Arms raised — single thick stroke each side
    pygame.draw.line(surf, sil, (x - 4, body_top + 3), (x - 8, body_top - 5), 3)
    pygame.draw.line(surf, sil, (x + 4, body_top + 3), (x + 8, body_top - 5), 3)
    if instrument:
        instrument(surf, x + 8, body_top - 5)


def draw_variant_3(surf: pygame.Surface, stripe_x: int) -> None:
    """V3 — Silhouette stadium row, right-side only, 7 figures all arms-up.
    Instruments are the only colour in the silhouette so the crowd reads as
    one rhythmic shape with bright accents."""
    gy = CELL_GROUND_Y + 4
    specs = [
        (stripe_x + 18,  3, GOLD,
         lambda s, hx, hy: _draw_trumpet(s, hx - 1, hy)),
        (stripe_x + 42,  0, RED,
         lambda s, hx, hy: _draw_megaphone(s, hx - 1, hy, RED)),
        (stripe_x + 66,  4, BLUE,
         lambda s, hx, hy: _draw_drum(s, hx - 3, hy + 10, RED, GOLD)),
        (stripe_x + 92,  0, GOLD,
         lambda s, hx, hy: _draw_cymbals(s, hx, hy)),
        (stripe_x + 116, 5, CREAM,
         lambda s, hx, hy: _draw_flag(s, hx, hy + 5, 16, RED)),
        (stripe_x + 140, 2, GREEN,
         lambda s, hx, hy: _draw_pompom(s, hx, hy - 2, GOLD)),
        (stripe_x + 162, 4, BLUE,
         lambda s, hx, hy: _draw_party_horn(s, hx - 2, hy + 1, GOLD)),
    ]
    for fx, jump, hat, instr in specs:
        _silhouette_fan(surf, fx, gy, jump, hat, instr)


# ── V4 — Classic stadium-fan jerseys, both sides ───────────────────────────

def _jersey_fan(surf, x, ground_y, jersey_col, num="1", jump=0, arms="hold",
                instrument=None, skin=SKIN_LIGHT, cap=GOLD):
    """Slightly chunkier than a chibi — striped athletic-fan silhouette
    with a numbered jersey + ball-cap. ~26 px wide × 34 px tall."""
    feet_y = ground_y - 1 - jump
    body_top = feet_y - 18
    head_r = 7
    head_cy = body_top - head_r + 2
    # Shadow
    shadow = pygame.Surface((20, 4), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow, (0, 0, 0, 70), (0, 0, 20, 4))
    surf.blit(shadow, (x - 10, ground_y))
    # Legs in shorts
    short_col = _shade(jersey_col, -55)
    pygame.draw.rect(surf, short_col, (x - 5, body_top + 12, 4, 5))
    pygame.draw.rect(surf, short_col, (x + 1, body_top + 12, 4, 5))
    # Socks + shoes
    pygame.draw.rect(surf, CREAM, (x - 5, body_top + 17, 4, 3))
    pygame.draw.rect(surf, CREAM, (x + 1, body_top + 17, 4, 3))
    pygame.draw.rect(surf, INK,   (x - 5, body_top + 20, 4, 2))
    pygame.draw.rect(surf, INK,   (x + 1, body_top + 20, 4, 2))
    # Jersey body + horizontal stripes
    pygame.draw.rect(surf, jersey_col, (x - 6, body_top, 12, 14), border_radius=2)
    stripe = _shade(jersey_col, -45)
    for sy in (body_top + 3, body_top + 7, body_top + 11):
        pygame.draw.line(surf, stripe, (x - 6, sy), (x + 5, sy), 1)
    pygame.draw.rect(surf, _shade(jersey_col, -60),
                     (x - 6, body_top, 12, 14), 1, border_radius=2)
    # Number on chest
    font = pygame.font.Font(None, 10)
    nt = font.render(num, True, CREAM)
    surf.blit(nt, (x - nt.get_width() // 2, body_top + 4))
    # Head
    pygame.draw.circle(surf, skin, (x, head_cy), head_r)
    pygame.draw.circle(surf, _shade(skin, -50), (x, head_cy), head_r, 1)
    # Ball cap
    pygame.draw.rect(surf, cap, (x - head_r, head_cy - head_r,
                                 head_r * 2, 4), border_radius=2)
    pygame.draw.polygon(surf, _shade(cap, -40),
                        [(x - head_r + 1, head_cy - head_r + 3),
                         (x + head_r + 3, head_cy - head_r + 4),
                         (x + head_r + 3, head_cy - head_r + 5),
                         (x - head_r + 1, head_cy - head_r + 5)])
    # Face — open shouting mouth
    pygame.draw.circle(surf, INK, (x - 2, head_cy + 1), 1)
    pygame.draw.circle(surf, INK, (x + 2, head_cy + 1), 1)
    pygame.draw.ellipse(surf, INK, (x - 1, head_cy + 3, 3, 2))
    # Arms — holding instrument up
    arm_col = skin
    if arms == "hold":
        pygame.draw.line(surf, jersey_col, (x - 5, body_top + 4),
                         (x - 9, body_top - 6), 3)
        pygame.draw.line(surf, jersey_col, (x + 5, body_top + 4),
                         (x + 9, body_top - 6), 3)
        pygame.draw.circle(surf, arm_col, (x - 9, body_top - 7), 2)
        pygame.draw.circle(surf, arm_col, (x + 9, body_top - 7), 2)
        if instrument:
            instrument(surf, x + 9, body_top - 7)


def draw_variant_4(surf: pygame.Surface, stripe_x: int) -> None:
    """V4 — Classic stadium-fan jerseys, both sides, 5 figures, holding-up
    trumpets / a big drum / flag / pom-poms."""
    gy = CELL_GROUND_Y + 4
    # LEFT side — 2 fans
    _jersey_fan(surf, stripe_x - 80, gy, RED, "7", 3, "hold",
                lambda s, hx, hy: _draw_trumpet(s, hx - 1, hy))
    _jersey_fan(surf, stripe_x - 45, gy, BLUE, "3", 0, "hold",
                lambda s, hx, hy: _draw_pompom(s, hx, hy - 2, GOLD),
                cap=RED)
    # RIGHT side — 3 fans, drum in the middle
    _jersey_fan(surf, stripe_x + 28, gy, GOLD, "9", 4, "hold",
                lambda s, hx, hy: _draw_trumpet(s, hx - 1, hy),
                skin=SKIN_DARK, cap=RED)
    _jersey_fan(surf, stripe_x + 70, gy, RED, "5", 0, "hold",
                lambda s, hx, hy: _draw_drum(s, hx - 4, hy + 14, BLUE, GOLD),
                skin=SKIN_LIGHT, cap=BLUE)
    _jersey_fan(surf, stripe_x + 112, gy, BLUE, "1", 3, "hold",
                lambda s, hx, hy: _draw_flag(s, hx, hy + 6, 18, GOLD),
                skin=SKIN_DEEP, cap=GOLD)


# ── V5 — Pixel-mascot animals, left-side only ──────────────────────────────

def _mascot_bear(surf, x, ground_y, fur=(170, 110, 70), jump=0, instrument=None):
    """Round-eared bear mascot, 28 px tall. Waves one paw."""
    feet_y = ground_y - 1 - jump
    body_top = feet_y - 18
    # Shadow
    shadow = pygame.Surface((22, 4), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow, (0, 0, 0, 70), (0, 0, 22, 4))
    surf.blit(shadow, (x - 11, ground_y))
    # Body
    pygame.draw.ellipse(surf, fur, (x - 8, body_top + 4, 16, 14))
    pygame.draw.ellipse(surf, _shade(fur, -50),
                        (x - 8, body_top + 4, 16, 14), 1)
    # Belly
    pygame.draw.ellipse(surf, CREAM, (x - 5, body_top + 9, 10, 8))
    # Head
    pygame.draw.circle(surf, fur, (x, body_top + 2), 7)
    pygame.draw.circle(surf, _shade(fur, -50), (x, body_top + 2), 7, 1)
    # Ears
    pygame.draw.circle(surf, fur, (x - 5, body_top - 3), 3)
    pygame.draw.circle(surf, fur, (x + 5, body_top - 3), 3)
    pygame.draw.circle(surf, _shade(fur, -50), (x - 5, body_top - 3), 3, 1)
    pygame.draw.circle(surf, _shade(fur, -50), (x + 5, body_top - 3), 3, 1)
    # Snout
    pygame.draw.ellipse(surf, CREAM, (x - 3, body_top + 2, 6, 4))
    pygame.draw.circle(surf, INK, (x, body_top + 3), 1)
    # Eyes
    pygame.draw.circle(surf, INK, (x - 3, body_top), 1)
    pygame.draw.circle(surf, INK, (x + 3, body_top), 1)
    # Open shouting mouth
    pygame.draw.ellipse(surf, INK, (x - 1, body_top + 4, 3, 2))
    # Feet
    pygame.draw.ellipse(surf, _shade(fur, -40), (x - 7, feet_y - 3, 6, 4))
    pygame.draw.ellipse(surf, _shade(fur, -40), (x + 1, feet_y - 3, 6, 4))
    # Arm raised with instrument
    pygame.draw.line(surf, fur, (x + 6, body_top + 8), (x + 11, body_top - 3), 3)
    pygame.draw.circle(surf, fur, (x + 11, body_top - 4), 2)
    if instrument:
        instrument(surf, x + 11, body_top - 4)


def _mascot_fox(surf, x, ground_y, jump=0, instrument=None):
    """Orange fox mascot with white belly + pointed ears. ~26 px tall."""
    feet_y = ground_y - 1 - jump
    body_top = feet_y - 17
    fur = (235, 130,  60)
    # Shadow
    shadow = pygame.Surface((20, 4), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow, (0, 0, 0, 70), (0, 0, 20, 4))
    surf.blit(shadow, (x - 10, ground_y))
    # Body
    pygame.draw.ellipse(surf, fur, (x - 7, body_top + 4, 14, 13))
    pygame.draw.ellipse(surf, _shade(fur, -60),
                        (x - 7, body_top + 4, 14, 13), 1)
    pygame.draw.ellipse(surf, CREAM, (x - 4, body_top + 9, 8, 7))
    # Head
    pygame.draw.ellipse(surf, fur, (x - 6, body_top - 3, 12, 9))
    pygame.draw.ellipse(surf, _shade(fur, -60),
                        (x - 6, body_top - 3, 12, 9), 1)
    # Ears (triangular)
    pygame.draw.polygon(surf, fur,
                        [(x - 6, body_top - 2), (x - 4, body_top - 7),
                         (x - 2, body_top - 1)])
    pygame.draw.polygon(surf, fur,
                        [(x + 6, body_top - 2), (x + 4, body_top - 7),
                         (x + 2, body_top - 1)])
    # Snout + nose
    pygame.draw.polygon(surf, CREAM,
                        [(x - 2, body_top + 3), (x + 2, body_top + 3),
                         (x, body_top + 6)])
    pygame.draw.circle(surf, INK, (x, body_top + 5), 1)
    # Eyes
    pygame.draw.circle(surf, INK, (x - 3, body_top + 1), 1)
    pygame.draw.circle(surf, INK, (x + 3, body_top + 1), 1)
    # Tail flicking up
    pygame.draw.polygon(surf, fur,
                        [(x - 6, body_top + 8), (x - 12, body_top + 2),
                         (x - 10, body_top + 9)])
    pygame.draw.polygon(surf, CREAM,
                        [(x - 9, body_top + 4), (x - 12, body_top + 2),
                         (x - 10, body_top + 6)])
    # Feet
    pygame.draw.ellipse(surf, INK, (x - 5, feet_y - 2, 4, 3))
    pygame.draw.ellipse(surf, INK, (x + 1, feet_y - 2, 4, 3))
    # Arm raised
    pygame.draw.line(surf, fur, (x + 5, body_top + 8), (x + 10, body_top - 3), 3)
    pygame.draw.circle(surf, fur, (x + 10, body_top - 4), 2)
    if instrument:
        instrument(surf, x + 10, body_top - 4)


def _mascot_bunny(surf, x, ground_y, jump=0, instrument=None):
    """Cream bunny mascot with tall ears. ~24 px tall (+ ear height)."""
    feet_y = ground_y - 1 - jump
    body_top = feet_y - 16
    fur = (245, 235, 215)
    # Shadow
    shadow = pygame.Surface((20, 4), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow, (0, 0, 0, 70), (0, 0, 20, 4))
    surf.blit(shadow, (x - 10, ground_y))
    # Body
    pygame.draw.ellipse(surf, fur, (x - 7, body_top + 4, 14, 13))
    pygame.draw.ellipse(surf, (180, 160, 140),
                        (x - 7, body_top + 4, 14, 13), 1)
    # Head
    pygame.draw.ellipse(surf, fur, (x - 6, body_top - 3, 12, 10))
    pygame.draw.ellipse(surf, (180, 160, 140),
                        (x - 6, body_top - 3, 12, 10), 1)
    # Ears
    pygame.draw.ellipse(surf, fur, (x - 5, body_top - 13, 4, 12))
    pygame.draw.ellipse(surf, fur, (x + 1, body_top - 13, 4, 12))
    pygame.draw.ellipse(surf, (230, 160, 180),
                        (x - 4, body_top - 11, 2, 8))
    pygame.draw.ellipse(surf, (230, 160, 180),
                        (x + 2, body_top - 11, 2, 8))
    pygame.draw.ellipse(surf, (180, 160, 140),
                        (x - 5, body_top - 13, 4, 12), 1)
    pygame.draw.ellipse(surf, (180, 160, 140),
                        (x + 1, body_top - 13, 4, 12), 1)
    # Face
    pygame.draw.circle(surf, INK, (x - 2, body_top + 1), 1)
    pygame.draw.circle(surf, INK, (x + 2, body_top + 1), 1)
    pygame.draw.circle(surf, (230, 100, 130), (x, body_top + 4), 1)
    pygame.draw.line(surf, INK, (x, body_top + 4), (x - 1, body_top + 6), 1)
    pygame.draw.line(surf, INK, (x, body_top + 4), (x + 1, body_top + 6), 1)
    # Feet
    pygame.draw.ellipse(surf, fur, (x - 6, feet_y - 3, 5, 4))
    pygame.draw.ellipse(surf, fur, (x + 1, feet_y - 3, 5, 4))
    # Arm raised with flag
    pygame.draw.line(surf, fur, (x + 5, body_top + 8), (x + 10, body_top - 4), 3)
    pygame.draw.circle(surf, fur, (x + 10, body_top - 5), 2)
    if instrument:
        instrument(surf, x + 10, body_top - 5)


def draw_variant_5(surf: pygame.Surface, stripe_x: int) -> None:
    """V5 — Pixel-mascot animals, left-side only, 3 figures (bear / fox /
    bunny), drum / megaphone / flag, jumping + waving."""
    gy = CELL_GROUND_Y + 4
    _mascot_bear(surf, stripe_x - 105, gy, fur=(170, 110, 70), jump=3,
                 instrument=lambda s, hx, hy: _draw_drum(s, hx - 4, hy + 12,
                                                        RED, GOLD))
    _mascot_fox(surf, stripe_x - 65, gy, jump=0,
                instrument=lambda s, hx, hy: _draw_megaphone(s, hx - 1, hy + 1,
                                                              RED))
    _mascot_bunny(surf, stripe_x - 28, gy, jump=5,
                  instrument=lambda s, hx, hy: _draw_flag(s, hx, hy + 5, 18,
                                                          BLUE))


# ── cell composition ───────────────────────────────────────────────────────

def _make_cell(variant_fn) -> pygame.Surface:
    """Build a single 360×200 cell: sky gradient + ground band + finish-line
    marker + crowd. Stripe is fixed at cell-x 200 so the crowd has the same
    spatial reference in every cell."""
    cell = pygame.Surface((CELL_W, CELL_H))
    _draw_sky(cell, CELL_H)
    _draw_cell_ground(cell)
    stripe_x = 200
    # Crowd FIRST so the white stripe + label sit on top — same draw order
    # the world uses (markers ride above ground events).
    variant_fn(cell, stripe_x)
    _draw_finish_marker(cell, stripe_x)
    # 1-px ink border so cells separate clearly on the sheet.
    pygame.draw.rect(cell, (40, 30, 20), cell.get_rect(), 1)
    return cell


# ── sheet assembly ─────────────────────────────────────────────────────────

VARIANT_TITLES = (
    ("V1  Chibi humans",
     "RIGHT only · 5 figures · pom / megaphone / drum / trumpet / flag"),
    ("V2  Parrot-people mix",
     "BOTH sides · 7 figures · flag x2 / tambourine / pom / horn / drum"),
    ("V3  Silhouette stadium",
     "RIGHT only · 7 figures · trumpet / megaphone / drum / cymbals / flag / pom / horn"),
    ("V4  Jersey fans",
     "BOTH sides · 5 figures · trumpet x2 / big drum / flag / pom"),
    ("V5  Pixel mascot animals",
     "LEFT only · 3 figures · drum / megaphone / flag · bear · fox · bunny"),
)


def _draw_title_band(sheet: pygame.Surface) -> None:
    """Top strip — sheet title + per-variant headers."""
    pygame.draw.rect(sheet, (28, 22, 36), (0, 0, SHEET_W, TITLE_BAND_H))
    pygame.draw.line(sheet, (90, 80, 60),
                     (0, TITLE_BAND_H - 1), (SHEET_W, TITLE_BAND_H - 1), 1)
    font_lg = pygame.font.Font(None, 28)
    font_sm = pygame.font.Font(None, 18)
    title = font_lg.render(
        "Cycle-finale cheering crowd  —  Round 1 exploration", True,
        (252, 244, 218))
    sheet.blit(title, (PAD, 8))
    subtitle = font_sm.render(
        "Real ground band + finish-line stripe + \"1 Day\" label per cell  ·"
        "  axes: figure style / sides / instruments / pose / density",
        True, (200, 195, 175))
    sheet.blit(subtitle, (PAD, 36))
    # Per-variant headers above each cell column happen during cell paste
    # below so the header is tied to each cell's actual screen rect.


def _draw_cell_caption(sheet, cx, cy, head, sub):
    font_h = pygame.font.Font(None, 19)
    font_s = pygame.font.Font(None, 15)
    head_s = font_h.render(head, True, (252, 244, 218))
    sub_s = font_s.render(sub, True, (180, 175, 155))
    sheet.blit(head_s, (cx + 4, cy - 32))
    sheet.blit(sub_s, (cx + 4, cy - 15))


def _draw_legend(sheet, cx, cy) -> None:
    """6th tile — spec block: cycle-finale palette swatches + figure-height
    scale ruler so the art-director can sanity-check sizes."""
    tile = pygame.Surface((CELL_W, CELL_H))
    tile.fill((36, 30, 44))
    pygame.draw.rect(tile, (60, 50, 70), tile.get_rect(), 1)
    title_f = pygame.font.Font(None, 22)
    body_f = pygame.font.Font(None, 16)
    tile.blit(title_f.render("Reference", True, (252, 244, 218)), (12, 10))
    # Palette swatches
    sw_y = 38
    for i, (name, col) in enumerate((
            ("GOLD",  GOLD), ("RED", RED), ("BLUE", BLUE),
            ("CREAM", CREAM), ("INK", INK))):
        pygame.draw.rect(tile, col, (12 + i * 64, sw_y, 28, 20),
                         border_radius=3)
        pygame.draw.rect(tile, (10, 10, 18), (12 + i * 64, sw_y, 28, 20),
                         1, border_radius=3)
        tile.blit(body_f.render(name, True, (220, 215, 200)),
                  (12 + i * 64 + 32, sw_y + 4))
    # Scale ruler — Pip (28), COIN_R (13), a figure (~30 px)
    ruler_y = 90
    tile.blit(body_f.render("Scale (px tall):", True, (220, 215, 200)),
              (12, ruler_y))
    # Pip silhouette stub
    pygame.draw.ellipse(tile, (140, 200, 90), (110, ruler_y + 4, 24, 18))
    pygame.draw.line(tile, INK, (110, ruler_y + 22), (134, ruler_y + 22), 1)
    tile.blit(body_f.render("Pip 28", True, (220, 215, 200)),
              (140, ruler_y + 5))
    # Crowd silhouette stub
    pygame.draw.rect(tile, (60, 60, 90), (200, ruler_y, 8, 22))
    pygame.draw.circle(tile, (60, 60, 90), (204, ruler_y - 4), 5)
    tile.blit(body_f.render("Crowd 30", True, (220, 215, 200)),
              (218, ruler_y + 5))
    # Footnote
    foot_y = 138
    foot = (
        "Each cell renders the real grass+soil band ",
        "(GROUND_Y=595, H=640) with the same finish-line ",
        "stripe + label sprite the game uses. Crowd ",
        "colours sit in the CelebrationBunting palette.",
    )
    for i, line in enumerate(foot):
        tile.blit(body_f.render(line, True, (200, 195, 175)),
                  (12, foot_y + i * 14))
    sheet.blit(tile, (cx, cy))


def main():
    sheet = pygame.Surface((SHEET_W, SHEET_H))
    sheet.fill((22, 18, 28))
    _draw_title_band(sheet)

    # Layout: row-major, 3 cols × 2 rows. 5 variant cells + 1 reference tile.
    variants = (
        draw_variant_1, draw_variant_2, draw_variant_3,
        draw_variant_4, draw_variant_5,
    )
    for idx, fn in enumerate(variants):
        row = idx // COLS
        col = idx % COLS
        cx = PAD + col * (CELL_W + PAD)
        cy = TITLE_BAND_H + PAD + row * (CELL_H + PAD) + 28  # +28 for caption
        cell = _make_cell(fn)
        sheet.blit(cell, (cx, cy))
        head, sub = VARIANT_TITLES[idx]
        _draw_cell_caption(sheet, cx, cy, head, sub)

    # Last tile (row 1, col 2) — reference / legend.
    cx = PAD + 2 * (CELL_W + PAD)
    cy = TITLE_BAND_H + PAD + 1 * (CELL_H + PAD) + 28
    _draw_legend(sheet, cx, cy)

    out_path = os.path.join(
        REPO_ROOT, "docs", "treasure_box", "cheering_crowd_round1.png")
    pygame.image.save(sheet, out_path)
    print(out_path)


if __name__ == "__main__":
    main()
