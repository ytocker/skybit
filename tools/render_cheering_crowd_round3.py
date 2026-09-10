"""Cycle-finale cheering crowd — Round 3 FINAL polish on R2-1.

Single 360×200 cell rendered on the real grass+soil ground band with the
live ``CelebrationGroundMarker`` (``1 Day``) so the polish reads against
the production scene. Three surgical fixes vs round 2:

  1. LEFT flag pole nudged -2 px so the silhouette no longer kisses the
     leftmost parrot's head crown.
  2. RIGHT megaphone bell gets a 1-px CREAM rim highlight on the OUTER
     cone edge — the cone now reads as a cone at 1×, not a blob.
  3. RIGHT-side jump rhythm broken — the megaphone parrot's static lift
     moves 0 → 3 px so the four right-side bob phases no longer split
     into a 0/0 doublet (now 0 / 5 / 3 / 4).

Output: docs/treasure_box/cheering_crowd_round3_final.png
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

from game.config import GROUND_Y, H
from game.draw import draw_ground, GROUND_TOP, GROUND_MID, GROUND_BOT
from game.entities import CelebrationBunting, CelebrationGroundMarker

# Bunting family — match CelebrationBunting.COLOURS verbatim so the crowd
# stays inside the cycle-finale colour story.
GOLD  = CelebrationBunting.COLOURS[0]
RED   = CelebrationBunting.COLOURS[1]
BLUE  = CelebrationBunting.COLOURS[2]
CREAM = CelebrationBunting.COLOURS[3]
INK   = CelebrationBunting.INK

CELL_W = 360
CELL_H = 200

SKY_TOP = (90, 170, 230)
SKY_MID = (140, 200, 240)
SKY_BOT = (190, 230, 250)

CELL_GROUND_Y = GROUND_Y - (H - CELL_H)


def _shade(col, d):
    return (
        max(0, min(255, col[0] + d)),
        max(0, min(255, col[1] + d)),
        max(0, min(255, col[2] + d)),
    )


def _draw_sky(surf: pygame.Surface, cell_h: int) -> None:
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
    draw_ground(surf, CELL_GROUND_Y, surf.get_width(), CELL_H, 0.0,
                GROUND_TOP, GROUND_MID, GROUND_BOT)


def _draw_finish_marker(surf: pygame.Surface, stripe_x: int) -> None:
    marker = CelebrationGroundMarker(world_x=stripe_x, day=1)
    spr = marker._sprite
    target_top = CELL_GROUND_Y + CelebrationGroundMarker.TOP_PAD
    target_left = stripe_x - CelebrationGroundMarker.LINE_W // 2
    surf.blit(spr, (target_left, target_top))


# ── instrument primitives ──────────────────────────────────────────────────
# All verbatim from round 2 except _draw_megaphone, which now carries the
# round-3 cream rim highlight so the cone silhouette reads at 1×.

def _draw_pompom(surf, cx, cy, fluff=GOLD, accent=RED):
    spikes = (
        (-3, 0), (3, 0), (0, -3), (0, 3),
        (-2, -2), (2, -2), (-2, 2), (2, 2),
    )
    for dx, dy in spikes:
        pygame.draw.circle(surf, fluff, (cx + dx, cy + dy), 1)
    pygame.draw.circle(surf, fluff, (cx, cy), 3)
    pygame.draw.circle(surf, accent, (cx - 1, cy - 1), 1)
    pygame.draw.circle(surf, _shade(fluff, -50), (cx, cy), 3, 1)


def _draw_trumpet(surf, x, y, body=GOLD):
    pygame.draw.line(surf, body, (x, y), (x + 5, y - 5), 2)
    bell = [
        (x + 5, y - 5),
        (x + 10, y - 9),
        (x + 9, y - 11),
        (x + 4, y - 7),
    ]
    pygame.draw.polygon(surf, body, bell)
    pygame.draw.polygon(surf, _shade(body, -70), bell, 1)
    pygame.draw.circle(surf, CREAM, (x + 5, y - 5), 1)


def _draw_drum(surf, cx, cy, shell=RED, rim=CREAM, stick=INK):
    w, h = 16, 10
    rect = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
    pygame.draw.rect(surf, shell, rect, border_radius=2)
    pygame.draw.rect(surf, rim, (rect.x, rect.y, rect.w, 2))
    pygame.draw.rect(surf, rim, (rect.x, rect.y + rect.h - 2, rect.w, 2))
    for k in range(4):
        kx = rect.x + 2 + k * 4
        pygame.draw.line(surf, _shade(shell, -50),
                         (kx, rect.y + 2), (kx + 1, rect.y + rect.h - 2), 1)
    pygame.draw.circle(surf, _shade(shell, -25), (cx, cy), 3)
    pygame.draw.circle(surf, INK, (cx, cy), 3, 1)
    pygame.draw.rect(surf, INK, rect, 1, border_radius=2)
    pygame.draw.line(surf, stick, (cx - 5, cy - 8), (cx - 1, cy - 2), 1)
    pygame.draw.line(surf, stick, (cx + 5, cy - 8), (cx + 1, cy - 2), 1)


def _draw_megaphone(surf, x, y, body=RED, mouth=CREAM):
    """Megaphone pointed up-and-right. The round-3 fix is a 1-px CREAM
    highlight along the upper outer cone edge plus a CREAM pixel on the
    bell rim corner, so the funnel reads as a cone at 1×."""
    pts = [
        (x, y),
        (x + 11, y - 8),
        (x + 13, y - 4),
        (x + 3, y + 3),
    ]
    pygame.draw.polygon(surf, body, pts)
    pygame.draw.polygon(surf, INK, pts, 1)
    # Round-3 fix: cream rim highlight on the OUTER cone edge — runs from
    # throat to bell so the cone slope is visible against the red body.
    pygame.draw.line(surf, mouth, (x + 1, y - 1), (x + 11, y - 8), 1)
    # Mouthpiece (CREAM) — the inner colour ring at the open end (existing).
    pygame.draw.line(surf, mouth, (x + 11, y - 8), (x + 13, y - 4), 2)
    # Single-pixel CREAM dot on the outer bell corner — the bell-edge
    # specular that makes the cone shape pop at 1× zoom.
    if 0 <= x + 12 < surf.get_width() and 0 <= y - 7 < surf.get_height():
        surf.set_at((x + 12, y - 7), mouth)
    # Grip stripe across the throat — hand-anchor cue (existing).
    pygame.draw.line(surf, _shade(body, -55), (x + 2, y), (x + 7, y - 4), 1)


def _draw_flag(surf, x_base, y_base, pole_h=20, banner=GOLD, pole=CREAM):
    pygame.draw.line(surf, pole, (x_base, y_base),
                     (x_base, y_base - pole_h), 2)
    pygame.draw.line(surf, _shade(pole, -60), (x_base, y_base),
                     (x_base, y_base - pole_h), 1)
    banner_pts = [
        (x_base, y_base - pole_h),
        (x_base + 11, y_base - pole_h + 2),
        (x_base + 10, y_base - pole_h + 4),
        (x_base + 11, y_base - pole_h + 7),
        (x_base, y_base - pole_h + 6),
    ]
    pygame.draw.polygon(surf, banner, banner_pts)
    pygame.draw.polygon(surf, _shade(banner, -60), banner_pts, 1)


def _draw_tambourine(surf, cx, cy, rim=CREAM, jingle=GOLD):
    pygame.draw.circle(surf, rim, (cx, cy), 6)
    pygame.draw.circle(surf, _shade(rim, -60), (cx, cy), 6, 1)
    pygame.draw.circle(surf, CREAM, (cx, cy), 3)
    pygame.draw.circle(surf, _shade(rim, -40), (cx, cy), 3, 1)
    for k in range(4):
        ang = k * (math.pi / 2) + 0.4
        jx = cx + int(math.cos(ang) * 6)
        jy = cy + int(math.sin(ang) * 6)
        pygame.draw.circle(surf, jingle, (jx, jy), 2)
        pygame.draw.circle(surf, _shade(jingle, -70), (jx, jy), 2, 1)


def _draw_party_horn(surf, x, y, body=GOLD, tip=RED, streamer=CREAM):
    pygame.draw.line(surf, body, (x, y), (x + 8, y - 3), 3)
    pygame.draw.line(surf, _shade(body, -60), (x, y), (x + 8, y - 3), 1)
    pygame.draw.line(surf, tip, (x + 8, y - 3), (x + 12, y - 6), 2)
    pygame.draw.line(surf, streamer, (x + 12, y - 6), (x + 14, y - 4), 2)
    pygame.draw.line(surf, streamer, (x + 14, y - 4), (x + 16, y - 7), 1)
    pygame.draw.circle(surf, streamer, (x + 16, y - 7), 1)


# ── parrot figure (verbatim R2) ─────────────────────────────────────────────

PLUMAGE = (
    (RED,   CREAM, GOLD,  GOLD),
    (BLUE,  CREAM, GOLD,  GOLD),
    (GOLD,  RED,   BLUE,  RED),
    (CREAM, RED,   BLUE,  RED),
    (RED,   GOLD,  CREAM, GOLD),
    (BLUE,  GOLD,  CREAM, GOLD),
    (GOLD,  CREAM, RED,   RED),
    (CREAM, BLUE,  RED,   GOLD),
)


def _parrot(surf, x, ground_y, plumage_idx=0, jump=0, pose="raise",
            instrument=None, mirror=False):
    body, belly, wing_accent, beak = PLUMAGE[plumage_idx % len(PLUMAGE)]
    feet_y = ground_y - 1 - jump

    shadow_alpha = 90 if jump == 0 else 55
    shadow = pygame.Surface((24, 5), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow, (0, 0, 0, shadow_alpha), (0, 0, 24, 5))
    surf.blit(shadow, (x - 12, ground_y))

    body_h = 18
    body_top = feet_y - body_h

    foot_col = _shade(beak, -20) if beak != INK else INK
    pygame.draw.line(surf, foot_col, (x - 3, feet_y - 1),
                     (x - 4, feet_y + 1), 2)
    pygame.draw.line(surf, foot_col, (x + 3, feet_y - 1),
                     (x + 4, feet_y + 1), 2)

    pygame.draw.ellipse(surf, body, (x - 8, body_top, 16, body_h))
    pygame.draw.ellipse(surf, _shade(body, -55),
                        (x - 8, body_top, 16, body_h), 1)

    pygame.draw.ellipse(surf, belly, (x - 5, body_top + 7, 10, 10))
    pygame.draw.ellipse(surf, _shade(belly, -40),
                        (x - 5, body_top + 7, 10, 10), 1)

    head_cy = body_top + 3
    pygame.draw.ellipse(surf, body, (x - 7, head_cy - 7, 14, 12))
    pygame.draw.ellipse(surf, _shade(body, -65),
                        (x - 7, head_cy - 7, 14, 12), 1)

    if mirror:
        beak_pts = [
            (x - 6, head_cy),
            (x - 11, head_cy + 1),
            (x - 6, head_cy + 3),
        ]
    else:
        beak_pts = [
            (x + 6, head_cy),
            (x + 11, head_cy + 1),
            (x + 6, head_cy + 3),
        ]
    pygame.draw.polygon(surf, beak, beak_pts)
    pygame.draw.polygon(surf, _shade(beak, -70), beak_pts, 1)

    eye_x = x - 3 if mirror else x + 3
    pygame.draw.circle(surf, CREAM, (eye_x, head_cy - 1), 2)
    pygame.draw.circle(surf, INK, (eye_x + (-1 if mirror else 1),
                                   head_cy - 1), 1)

    mouth_x = x - 5 if mirror else x + 5
    pygame.draw.line(surf, INK, (mouth_x, head_cy + 2),
                     (mouth_x + (-1 if mirror else 1), head_cy + 3), 1)

    near_x = x - 6 if mirror else x + 6
    near_dir = -1 if mirror else 1
    far_x = -near_x + 2 * x

    if pose == "raise":
        pygame.draw.polygon(surf, _shade(body, -25), [
            (far_x, body_top + 4),
            (far_x + (-near_dir) * 4, body_top - 5),
            (far_x + (-near_dir), body_top - 4),
            (far_x + near_dir * 2, body_top + 5),
        ])
        pygame.draw.line(surf, wing_accent,
                         (far_x + (-near_dir) * 4, body_top - 5),
                         (far_x + (-near_dir), body_top - 4), 2)
        pygame.draw.polygon(surf, _shade(body, -25), [
            (near_x, body_top + 4),
            (near_x + near_dir * 4, body_top - 5),
            (near_x + near_dir, body_top - 4),
            (near_x + (-near_dir) * 2, body_top + 5),
        ])
        pygame.draw.line(surf, wing_accent,
                         (near_x + near_dir * 4, body_top - 5),
                         (near_x + near_dir, body_top - 4), 2)
        if instrument:
            instrument(surf, near_x + near_dir * 4, body_top - 5)
    else:
        pygame.draw.polygon(surf, _shade(body, -25), [
            (far_x, body_top + 4),
            (far_x + (-near_dir) * 5, body_top + 2),
            (far_x + (-near_dir) * 3, body_top + 5),
            (far_x + near_dir, body_top + 8),
        ])
        pygame.draw.polygon(surf, _shade(body, -25), [
            (near_x, body_top + 4),
            (near_x + near_dir * 4, body_top - 6),
            (near_x + near_dir, body_top - 5),
            (near_x + (-near_dir) * 2, body_top + 5),
        ])
        pygame.draw.line(surf, wing_accent,
                         (near_x + near_dir * 4, body_top - 6),
                         (near_x + near_dir, body_top - 5), 2)
        if instrument:
            instrument(surf, near_x + near_dir * 4, body_top - 6)


# ── R2-1 composition with the three round-3 surgical fixes ─────────────────

def draw_r3_final(surf, stripe_x):
    """R2-1 layout — mixed band, 7 parrots, 3 LEFT / 4 RIGHT — with the
    three round-3 surgical fixes:

      FIX 1 (leftmost flag): pass ``hx - 2`` to ``_draw_flag`` so the
        pole moves 2 px LEFT off the parrot head silhouette.
      FIX 2 (right megaphone): handled inside ``_draw_megaphone`` —
        cream rim highlight on the outer cone edge plus 1-px bell-corner
        dot so the cone reads as a cone at 1×.
      FIX 3 (right-side jump rhythm): megaphone-parrot jump 0 → 3 so the
        right-side stack reads as 0 / 5 / 3 / 4 instead of clustering two
        figures at jump=0.
    """
    gy = CELL_GROUND_Y + 4

    # LEFT side (3) — flag · pom · drum.
    _parrot(surf, stripe_x - 130, gy, 0, jump=4, pose="raise", mirror=True,
            instrument=lambda s, hx, hy: _draw_flag(s, hx - 2, hy + 6,
                                                    pole_h=20, banner=GOLD))
    _parrot(surf, stripe_x - 95, gy, 5, jump=0, pose="wave", mirror=True,
            instrument=lambda s, hx, hy: _draw_pompom(s, hx - 1, hy - 1,
                                                       GOLD, RED))
    _parrot(surf, stripe_x - 60, gy, 2, jump=3, pose="raise", mirror=True,
            instrument=lambda s, hx, hy: _draw_drum(s, hx + 4, hy + 12,
                                                    RED, CREAM))

    # RIGHT side (4) — tambourine · trumpet · megaphone · party-horn.
    _parrot(surf, stripe_x + 24, gy, 1, jump=0, pose="raise",
            instrument=lambda s, hx, hy: _draw_tambourine(s, hx + 2, hy - 1,
                                                          CREAM, GOLD))
    _parrot(surf, stripe_x + 60, gy, 6, jump=5, pose="raise",
            instrument=lambda s, hx, hy: _draw_trumpet(s, hx, hy, GOLD))
    _parrot(surf, stripe_x + 100, gy, 3, jump=3, pose="wave",
            instrument=lambda s, hx, hy: _draw_megaphone(s, hx, hy + 2,
                                                         RED, CREAM))
    _parrot(surf, stripe_x + 140, gy, 7, jump=4, pose="raise",
            instrument=lambda s, hx, hy: _draw_party_horn(s, hx, hy, GOLD,
                                                          RED, CREAM))


def main():
    cell = pygame.Surface((CELL_W, CELL_H))
    _draw_sky(cell, CELL_H)
    _draw_cell_ground(cell)
    draw_r3_final(cell, stripe_x=200)
    _draw_finish_marker(cell, 200)
    pygame.draw.rect(cell, (40, 30, 20), cell.get_rect(), 1)

    out_path = os.path.join(
        REPO_ROOT, "docs", "treasure_box", "cheering_crowd_round3_final.png")
    pygame.image.save(cell, out_path)
    print(out_path)


if __name__ == "__main__":
    main()
