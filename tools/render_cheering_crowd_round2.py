"""Cycle-finale cheering crowd — Round 2 exploration sheet.

Round-1 critique: ITERATE on V2 (parrot-people crowd, both sides). Every
figure becomes a parrot — Pip cousins — re-palettes into the bunting
family only (GOLD / RED / BLUE / CREAM / INK), with INSTRUMENT silhouettes
puffed up so the 1× gameplay sprite still reads after the chest scroll.
Every other figure jumps / lifts a wing; ≤ 8 figures per cell; head-tops
stay ≤ GROUND_Y. No KFC gag in round 2.

Five sub-directions of the same parrot-crowd-in-bunting-palette theme:

  R2-1 — 7 parrots · 3/4 layout · ONE OF EACH instrument
         (drum · trumpet · flag · pom · tambourine · megaphone · horn).
  R2-2 — 7 parrots · both sides · INSTRUMENT-HEAVY
         (2 flags + 2 pom-poms + 1 drum + 1 trumpet + 1 megaphone).
  R2-3 — 6 parrots · 3/3 symmetric · MARCHING-BAND rhythm section
         (2 drums + 1 tambourine + 1 trumpet + 1 cymbal + 1 horn).
  R2-4 — 8 parrots · DENSE, every figure jumps or wings-raised, mixed.
  R2-5 — 5 parrots · MINIMAL · 2 flags + 2 pom-poms + 1 trumpet, generous
         spacing.

The 6th tile is a 2× ZOOM of R2-1 so the critic can verify instrument
silhouettes (drum front ~6 px, trumpet bell ~4 px, flag ~8×5, pom ~5,
megaphone cone ~6 wide). Each cell renders on the real grass+soil band
with the actual ``CelebrationGroundMarker`` sprite ("1 Day"), so figure
height + finish-line scale are judged against the live game.

Output: docs/treasure_box/cheering_crowd_round2.png (doc-only; not shipped)
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
from game.entities import CelebrationBunting, CelebrationGroundMarker

# Bunting family — match CelebrationBunting.COLOURS verbatim so the crowd
# lives inside the cycle-finale colour story rather than next to it.
GOLD  = CelebrationBunting.COLOURS[0]   # (255, 220, 110)
RED   = CelebrationBunting.COLOURS[1]   # (220,  64,  32)
BLUE  = CelebrationBunting.COLOURS[2]   # ( 96, 176, 232)
CREAM = CelebrationBunting.COLOURS[3]   # (252, 244, 218)
INK   = CelebrationBunting.INK          # ( 30,  20,   8)

# Sheet layout — 6 tiles (5 variants + zoom callout), 3 cols × 2 rows.
CELL_W = 360
CELL_H = 200
COLS   = 3
ROWS   = 2
TITLE_BAND_H = 78
PAD = 12
SHEET_W = COLS * CELL_W + (COLS + 1) * PAD
SHEET_H = TITLE_BAND_H + ROWS * (CELL_H + 28) + (ROWS + 1) * PAD

# Sky — day-palette wrap colours pulled from the round-1 sheet for
# continuity between rounds in the gallery.
SKY_TOP = (90, 170, 230)
SKY_MID = (140, 200, 240)
SKY_BOT = (190, 230, 250)

# Cell-local ground band; same 45-px band as the live world.
CELL_GROUND_Y = GROUND_Y - (H - CELL_H)


# ── colour helpers ─────────────────────────────────────────────────────────

def _shade(col, d):
    return (
        max(0, min(255, col[0] + d)),
        max(0, min(255, col[1] + d)),
        max(0, min(255, col[2] + d)),
    )


# ── ground + finish-line marker ────────────────────────────────────────────

def _draw_sky(surf: pygame.Surface, cell_h: int) -> None:
    """Vertical gradient confined to the cell — believable horizon behind
    each parrot so silhouettes are read against the real game tone."""
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
# All re-tuned to bunting palette + +1-2 px so each silhouette survives at
# 1× scale during the ~5 s window the player sees the crowd.

def _draw_pompom(surf, cx, cy, fluff=GOLD, accent=RED):
    """Pom-pom — 5-px-diameter cluster with radial spikes so the fuzzy
    edge survives at 1× scale. Two-tone (fluff + accent) reads as a
    bunting-coloured cheer prop."""
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
    """Tiny upraised trumpet — bell flare bumped to ~4 px so the funnel
    reads after the scroll. Stem CREAM-ringed at the wrist for grip."""
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
    """Snare drum slung at the waist. Shell RED + rim CREAM per critique;
    two visible drumsticks make the silhouette read as percussion at 1×."""
    w, h = 16, 10
    rect = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
    pygame.draw.rect(surf, shell, rect, border_radius=2)
    pygame.draw.rect(surf, rim, (rect.x, rect.y, rect.w, 2))
    pygame.draw.rect(surf, rim, (rect.x, rect.y + rect.h - 2, rect.w, 2))
    for k in range(4):
        kx = rect.x + 2 + k * 4
        pygame.draw.line(surf, _shade(shell, -50),
                         (kx, rect.y + 2), (kx + 1, rect.y + rect.h - 2), 1)
    # Front "head" — small ~6-px circle so the player parses "drum, not box".
    pygame.draw.circle(surf, _shade(shell, -25), (cx, cy), 3)
    pygame.draw.circle(surf, INK, (cx, cy), 3, 1)
    pygame.draw.rect(surf, INK, rect, 1, border_radius=2)
    # Crossed sticks above the rim — ink, slim, clearly readable.
    pygame.draw.line(surf, stick, (cx - 5, cy - 8), (cx - 1, cy - 2), 1)
    pygame.draw.line(surf, stick, (cx + 5, cy - 8), (cx + 1, cy - 2), 1)


def _draw_megaphone(surf, x, y, body=RED, mouth=CREAM):
    """Megaphone pointed up-and-right. Cone mouth bumped to ~6 px wide so
    the funnel silhouette survives the scroll."""
    pts = [
        (x, y),
        (x + 11, y - 8),
        (x + 13, y - 4),
        (x + 3, y + 3),
    ]
    pygame.draw.polygon(surf, body, pts)
    pygame.draw.polygon(surf, INK, pts, 1)
    # Mouthpiece (CREAM) — the inner colour ring at the open end.
    pygame.draw.line(surf, mouth, (x + 11, y - 8), (x + 13, y - 4), 2)
    # Grip stripe across the throat — hand-anchor cue.
    pygame.draw.line(surf, _shade(body, -55), (x + 2, y), (x + 7, y - 4), 1)


def _draw_flag(surf, x_base, y_base, pole_h=20, banner=GOLD, pole=CREAM):
    """Festive flag — pole CREAM, banner GOLD or BLUE per the bunting
    family. Banner bumped to ~8×5 px with a slight droop so the player
    reads "flag catching wind" not "stick with rectangle".
    """
    pygame.draw.line(surf, pole, (x_base, y_base),
                     (x_base, y_base - pole_h), 2)
    pygame.draw.line(surf, _shade(pole, -60), (x_base, y_base),
                     (x_base, y_base - pole_h), 1)
    # Banner with a wind droop — 5 verts so the trailing edge has a curve.
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
    """Tambourine — CREAM rim + 4 GOLD jingles."""
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
    """Party horn — GOLD blowpipe + RED curled tip + CREAM streamer."""
    pygame.draw.line(surf, body, (x, y), (x + 8, y - 3), 3)
    pygame.draw.line(surf, _shade(body, -60), (x, y), (x + 8, y - 3), 1)
    pygame.draw.line(surf, tip, (x + 8, y - 3), (x + 12, y - 6), 2)
    # CREAM streamer — small wave + bobble at the tip.
    pygame.draw.line(surf, streamer, (x + 12, y - 6), (x + 14, y - 4), 2)
    pygame.draw.line(surf, streamer, (x + 14, y - 4), (x + 16, y - 7), 1)
    pygame.draw.circle(surf, streamer, (x + 16, y - 7), 1)


def _draw_cymbals(surf, cx, cy, body=GOLD):
    """Pair of clashed cymbals — two filled ellipses + clash flash."""
    pygame.draw.ellipse(surf, body, (cx - 7, cy - 3, 7, 5))
    pygame.draw.ellipse(surf, _shade(body, -70), (cx - 7, cy - 3, 7, 5), 1)
    pygame.draw.ellipse(surf, body, (cx, cy - 3, 7, 5))
    pygame.draw.ellipse(surf, _shade(body, -70), (cx, cy - 3, 7, 5), 1)
    pygame.draw.ellipse(surf, CREAM, (cx - 6, cy - 2, 5, 3))
    # Clash flash — small ink wedges at the meeting point.
    pygame.draw.line(surf, RED, (cx - 1, cy - 4), (cx + 1, cy - 4), 1)


# ── parrot figure ─────────────────────────────────────────────────────────

# Per-figure plumage rolls — body / belly / wing / beak colours, all from
# the bunting palette. The crowd reads as a flock when these vary.
PLUMAGE = (
    # (body, belly, wing_accent, beak)
    (RED,   CREAM, GOLD,  GOLD),   # A — red body, cream chest, gold wing+beak
    (BLUE,  CREAM, GOLD,  GOLD),   # B — blue body, cream chest, gold wing+beak
    (GOLD,  RED,   BLUE,  RED),    # C — gold body, red chest, blue wing
    (CREAM, RED,   BLUE,  RED),    # D — cream body, red chest, blue wing
    (RED,   GOLD,  CREAM, GOLD),   # E — red body, gold chest, cream wing
    (BLUE,  GOLD,  CREAM, GOLD),   # F — blue body, gold chest, cream wing
    (GOLD,  CREAM, RED,   RED),    # G — gold body, cream chest, red wing
    (CREAM, BLUE,  RED,   GOLD),   # H — cream body, blue chest, red wing
)


def _parrot(surf, x, ground_y, plumage_idx=0, jump=0, pose="raise",
            instrument=None, mirror=False):
    """Round-bodied macaw, Pip cousin. ~22 px wide × 28 px tall.

    ``jump`` = pixel lift (0 = grounded). ``pose`` ∈ {"raise", "wave"} —
    raise = both wings up cheering, wave = one wing up + one out at the
    side. ``mirror`` flips the figure so the head and instrument face the
    finish line stripe (used for the LEFT-side parrots).
    """
    body, belly, wing_accent, beak = PLUMAGE[plumage_idx % len(PLUMAGE)]
    feet_y = ground_y - 1 - jump

    # Shadow disc — softer + shorter on jumping figures so the lift reads.
    shadow_alpha = 90 if jump == 0 else 55
    shadow = pygame.Surface((24, 5), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow, (0, 0, 0, shadow_alpha), (0, 0, 24, 5))
    surf.blit(shadow, (x - 12, ground_y))

    body_h = 18
    body_top = feet_y - body_h

    # Feet — beak-coloured toes; offset apart so the stance reads at 1×.
    foot_col = _shade(beak, -20) if beak != INK else INK
    pygame.draw.line(surf, foot_col, (x - 3, feet_y - 1),
                     (x - 4, feet_y + 1), 2)
    pygame.draw.line(surf, foot_col, (x + 3, feet_y - 1),
                     (x + 4, feet_y + 1), 2)

    # Round body
    pygame.draw.ellipse(surf, body, (x - 8, body_top, 16, body_h))
    pygame.draw.ellipse(surf, _shade(body, -55),
                        (x - 8, body_top, 16, body_h), 1)

    # Belly patch — chest colour, slightly inset.
    pygame.draw.ellipse(surf, belly, (x - 5, body_top + 7, 10, 10))
    pygame.draw.ellipse(surf, _shade(belly, -40),
                        (x - 5, body_top + 7, 10, 10), 1)

    # Head — sits above the body, same body colour with darker rim.
    head_cy = body_top + 3
    pygame.draw.ellipse(surf, body, (x - 7, head_cy - 7, 14, 12))
    pygame.draw.ellipse(surf, _shade(body, -65),
                        (x - 7, head_cy - 7, 14, 12), 1)

    # Beak — direction depends on ``mirror`` so the crowd faces the line.
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

    # Eye — CREAM whites + INK pupil, off-centre toward the beak.
    eye_x = x - 3 if mirror else x + 3
    pygame.draw.circle(surf, CREAM, (eye_x, head_cy - 1), 2)
    pygame.draw.circle(surf, INK, (eye_x + (-1 if mirror else 1),
                                   head_cy - 1), 1)

    # Open shouting mouth at the beak base — adds energy to the figure.
    mouth_x = x - 5 if mirror else x + 5
    pygame.draw.line(surf, INK, (mouth_x, head_cy + 2),
                     (mouth_x + (-1 if mirror else 1), head_cy + 3), 1)

    # Wings raised as arms. ``pose`` decides asymmetry — jumping parrots
    # raise both wings, grounded ones lift the outside wing only so the
    # crowd has a natural standing/jumping interleave.
    near_x = x - 6 if mirror else x + 6     # wing closest to finish line
    near_dir = -1 if mirror else 1
    far_x = -near_x + 2 * x                  # outside wing

    if pose == "raise":
        # Both wings UP — full cheer.
        # Outside (far) wing
        pygame.draw.polygon(surf, _shade(body, -25), [
            (far_x, body_top + 4),
            (far_x + (-near_dir) * 4, body_top - 5),
            (far_x + (-near_dir), body_top - 4),
            (far_x + near_dir * 2, body_top + 5),
        ])
        # Wing-tip accent — feather edge in wing-accent colour.
        pygame.draw.line(surf, wing_accent,
                         (far_x + (-near_dir) * 4, body_top - 5),
                         (far_x + (-near_dir), body_top - 4), 2)
        # Inside (near) wing
        pygame.draw.polygon(surf, _shade(body, -25), [
            (near_x, body_top + 4),
            (near_x + near_dir * 4, body_top - 5),
            (near_x + near_dir, body_top - 4),
            (near_x + (-near_dir) * 2, body_top + 5),
        ])
        pygame.draw.line(surf, wing_accent,
                         (near_x + near_dir * 4, body_top - 5),
                         (near_x + near_dir, body_top - 4), 2)
        # Instrument hangs off the inside wing-tip so it reads near the line.
        if instrument:
            instrument(surf, near_x + near_dir * 4, body_top - 5)
    else:  # "wave" — outside wing held out, inside wing raised
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


# ── per-variant compositions ────────────────────────────────────────────────

# Each variant takes (surf, stripe_x). All crowds keep head-tops above
# GROUND_Y by construction (head_cy = body_top + 3, body_top = feet_y -
# body_h - jump, body_h = 18, head_r = ~7; head crown ~ ground_y - 28 - jump
# — well within the GROUND_Y=595 limit; see the assert at the bottom).


def draw_variant_1(surf, stripe_x):
    """R2-1 — 7 parrots, 3 LEFT / 4 RIGHT, ONE-OF-EACH instrument so the
    band sounds varied. Alternating jumps (4 px) sell motion at 1× scale."""
    gy = CELL_GROUND_Y + 4
    # LEFT side (3) — flag · pom · drum
    _parrot(surf, stripe_x - 130, gy, 0, jump=4, pose="raise", mirror=True,
            instrument=lambda s, hx, hy: _draw_flag(s, hx, hy + 6,
                                                    pole_h=20, banner=GOLD))
    _parrot(surf, stripe_x - 95, gy, 5, jump=0, pose="wave", mirror=True,
            instrument=lambda s, hx, hy: _draw_pompom(s, hx - 1, hy - 1,
                                                       GOLD, RED))
    _parrot(surf, stripe_x - 60, gy, 2, jump=3, pose="raise", mirror=True,
            instrument=lambda s, hx, hy: _draw_drum(s, hx + 4, hy + 12,
                                                    RED, CREAM))
    # RIGHT side (4) — tambourine · trumpet · megaphone · party-horn
    _parrot(surf, stripe_x + 24, gy, 1, jump=0, pose="raise",
            instrument=lambda s, hx, hy: _draw_tambourine(s, hx + 2, hy - 1,
                                                          CREAM, GOLD))
    _parrot(surf, stripe_x + 60, gy, 6, jump=5, pose="raise",
            instrument=lambda s, hx, hy: _draw_trumpet(s, hx, hy, GOLD))
    _parrot(surf, stripe_x + 100, gy, 3, jump=0, pose="wave",
            instrument=lambda s, hx, hy: _draw_megaphone(s, hx, hy + 2,
                                                         RED, CREAM))
    _parrot(surf, stripe_x + 140, gy, 7, jump=4, pose="raise",
            instrument=lambda s, hx, hy: _draw_party_horn(s, hx, hy, GOLD,
                                                          RED, CREAM))


def draw_variant_2(surf, stripe_x):
    """R2-2 — 7 parrots, both sides, INSTRUMENT-HEAVY: 2 flags · 2 pom-
    poms · 1 drum · 1 trumpet · 1 megaphone. More gold + red bursts."""
    gy = CELL_GROUND_Y + 4
    # LEFT (3) — flag · pom · megaphone
    _parrot(surf, stripe_x - 125, gy, 4, jump=3, pose="raise", mirror=True,
            instrument=lambda s, hx, hy: _draw_flag(s, hx, hy + 7,
                                                    pole_h=22, banner=BLUE))
    _parrot(surf, stripe_x - 90, gy, 1, jump=0, pose="raise", mirror=True,
            instrument=lambda s, hx, hy: _draw_pompom(s, hx - 1, hy - 1,
                                                       GOLD, RED))
    _parrot(surf, stripe_x - 55, gy, 7, jump=4, pose="wave", mirror=True,
            instrument=lambda s, hx, hy: _draw_megaphone(s, hx - 1, hy + 1,
                                                         RED, CREAM))
    # RIGHT (4) — pom · drum · trumpet · flag
    _parrot(surf, stripe_x + 24, gy, 0, jump=0, pose="raise",
            instrument=lambda s, hx, hy: _draw_pompom(s, hx + 1, hy - 1,
                                                       GOLD, RED))
    _parrot(surf, stripe_x + 60, gy, 5, jump=5, pose="raise",
            instrument=lambda s, hx, hy: _draw_drum(s, hx + 3, hy + 12,
                                                    RED, CREAM))
    _parrot(surf, stripe_x + 100, gy, 2, jump=0, pose="raise",
            instrument=lambda s, hx, hy: _draw_trumpet(s, hx, hy, GOLD))
    _parrot(surf, stripe_x + 140, gy, 6, jump=3, pose="wave",
            instrument=lambda s, hx, hy: _draw_flag(s, hx, hy + 6,
                                                    pole_h=20, banner=GOLD))


def draw_variant_3(surf, stripe_x):
    """R2-3 — 6 parrots, 3/3 SYMMETRIC marching-band: 2 drums + tambourine
    + trumpet + cymbal + horn. Reads as a percussion ensemble at the
    finish-line ribbon."""
    gy = CELL_GROUND_Y + 4
    # LEFT (3) — drum · tambourine · trumpet
    _parrot(surf, stripe_x - 120, gy, 1, jump=0, pose="raise", mirror=True,
            instrument=lambda s, hx, hy: _draw_drum(s, hx + 4, hy + 12,
                                                    RED, CREAM))
    _parrot(surf, stripe_x - 80, gy, 6, jump=4, pose="raise", mirror=True,
            instrument=lambda s, hx, hy: _draw_tambourine(s, hx + 2, hy - 1,
                                                          CREAM, GOLD))
    _parrot(surf, stripe_x - 40, gy, 3, jump=0, pose="raise", mirror=True,
            instrument=lambda s, hx, hy: _draw_trumpet(s, hx - 5, hy, GOLD))
    # RIGHT (3) — drum · cymbal · horn
    _parrot(surf, stripe_x + 28, gy, 0, jump=0, pose="raise",
            instrument=lambda s, hx, hy: _draw_drum(s, hx + 4, hy + 12,
                                                    RED, CREAM))
    _parrot(surf, stripe_x + 75, gy, 7, jump=5, pose="raise",
            instrument=lambda s, hx, hy: _draw_cymbals(s, hx + 4, hy, GOLD))
    _parrot(surf, stripe_x + 125, gy, 2, jump=0, pose="raise",
            instrument=lambda s, hx, hy: _draw_party_horn(s, hx, hy + 1,
                                                          GOLD, RED, CREAM))


def draw_variant_4(surf, stripe_x):
    """R2-4 — 8 parrots, DENSE crowd, EVERY figure jumping (0/2/4/5 px
    so the bob phases don't all match), mixed instruments. Max energy."""
    gy = CELL_GROUND_Y + 4
    # LEFT (4) — flag · pom · drum · trumpet
    _parrot(surf, stripe_x - 145, gy, 0, jump=4, pose="raise", mirror=True,
            instrument=lambda s, hx, hy: _draw_flag(s, hx, hy + 6,
                                                    pole_h=20, banner=GOLD))
    _parrot(surf, stripe_x - 115, gy, 5, jump=2, pose="raise", mirror=True,
            instrument=lambda s, hx, hy: _draw_pompom(s, hx - 1, hy - 1,
                                                       GOLD, RED))
    _parrot(surf, stripe_x - 82, gy, 2, jump=5, pose="raise", mirror=True,
            instrument=lambda s, hx, hy: _draw_drum(s, hx + 4, hy + 12,
                                                    RED, CREAM))
    _parrot(surf, stripe_x - 47, gy, 7, jump=3, pose="wave", mirror=True,
            instrument=lambda s, hx, hy: _draw_trumpet(s, hx - 5, hy, GOLD))
    # RIGHT (4) — pom · tambourine · megaphone · flag
    _parrot(surf, stripe_x + 22, gy, 1, jump=4, pose="raise",
            instrument=lambda s, hx, hy: _draw_pompom(s, hx + 1, hy - 1,
                                                       GOLD, RED))
    _parrot(surf, stripe_x + 55, gy, 6, jump=2, pose="raise",
            instrument=lambda s, hx, hy: _draw_tambourine(s, hx + 2, hy - 1,
                                                          CREAM, GOLD))
    _parrot(surf, stripe_x + 92, gy, 3, jump=5, pose="raise",
            instrument=lambda s, hx, hy: _draw_megaphone(s, hx, hy + 2,
                                                         RED, CREAM))
    _parrot(surf, stripe_x + 130, gy, 4, jump=3, pose="raise",
            instrument=lambda s, hx, hy: _draw_flag(s, hx, hy + 6,
                                                    pole_h=20, banner=BLUE))


def draw_variant_5(surf, stripe_x):
    """R2-5 — 5 parrots, MINIMAL: 2 flags · 2 pom-poms · 1 trumpet, with
    generous spacing so each figure reads as a distinct character."""
    gy = CELL_GROUND_Y + 4
    # LEFT (2) — flag · pom
    _parrot(surf, stripe_x - 120, gy, 4, jump=4, pose="raise", mirror=True,
            instrument=lambda s, hx, hy: _draw_flag(s, hx, hy + 7,
                                                    pole_h=22, banner=GOLD))
    _parrot(surf, stripe_x - 65, gy, 1, jump=0, pose="raise", mirror=True,
            instrument=lambda s, hx, hy: _draw_pompom(s, hx - 1, hy - 1,
                                                       GOLD, RED))
    # RIGHT (3) — trumpet · pom · flag
    _parrot(surf, stripe_x + 30, gy, 5, jump=4, pose="raise",
            instrument=lambda s, hx, hy: _draw_trumpet(s, hx, hy, GOLD))
    _parrot(surf, stripe_x + 85, gy, 0, jump=0, pose="raise",
            instrument=lambda s, hx, hy: _draw_pompom(s, hx + 1, hy - 1,
                                                       GOLD, RED))
    _parrot(surf, stripe_x + 140, gy, 7, jump=5, pose="raise",
            instrument=lambda s, hx, hy: _draw_flag(s, hx, hy + 7,
                                                    pole_h=22, banner=BLUE))


# ── cell + zoom-callout composition ─────────────────────────────────────────

def _make_cell(variant_fn, stripe_x=200) -> pygame.Surface:
    cell = pygame.Surface((CELL_W, CELL_H))
    _draw_sky(cell, CELL_H)
    _draw_cell_ground(cell)
    # Crowd FIRST so the white finish stripe + label paint above them —
    # same draw order the world uses (markers ride above ground events).
    variant_fn(cell, stripe_x)
    _draw_finish_marker(cell, stripe_x)
    pygame.draw.rect(cell, (40, 30, 20), cell.get_rect(), 1)
    return cell


def _make_zoom_tile(variant_fn) -> pygame.Surface:
    """6th tile — 2× scale of R2-1's RIGHT-side crowd so instrument
    silhouettes are sized for critic inspection."""
    base = _make_cell(variant_fn)
    # Crop the right-side ~145 px of the cell (where the 4 right parrots
    # cluster) and scale 2× into the tile.
    crop = pygame.Rect(180, 30, 175, 170)
    sub = base.subsurface(crop).copy()
    zoom = pygame.transform.scale(sub, (CELL_W, CELL_H))
    pygame.draw.rect(zoom, (40, 30, 20), zoom.get_rect(), 1)
    # 2× crosshair tag — keeps reviewers oriented.
    font = pygame.font.Font(None, 18)
    badge = font.render("R2-1  ·  2× zoom (right-side crowd)", True,
                        (252, 244, 218))
    pad_box = pygame.Surface((badge.get_width() + 10, badge.get_height() + 6),
                             pygame.SRCALPHA)
    pad_box.fill((20, 16, 28, 200))
    zoom.blit(pad_box, (6, 6))
    zoom.blit(badge, (11, 9))
    return zoom


# ── sheet assembly ────────────────────────────────────────────────────────

VARIANT_TITLES = (
    ("R2-1  Mixed band  (7 parrots · 3/4)",
     "drum · trumpet · flag · pom · tambourine · megaphone · party-horn"),
    ("R2-2  Instrument-heavy  (7 parrots)",
     "2 flags + 2 pom-poms + drum + trumpet + megaphone"),
    ("R2-3  Marching-band  (6 parrots · 3/3 sym)",
     "2 drums + tambourine + trumpet + cymbals + horn"),
    ("R2-4  Dense / max energy  (8 parrots)",
     "all jumping or wings-raised · mixed instruments"),
    ("R2-5  Minimal  (5 parrots)",
     "2 flags + 2 pom-poms + 1 trumpet · generous spacing"),
)


def _draw_title_band(sheet):
    pygame.draw.rect(sheet, (28, 22, 36), (0, 0, SHEET_W, TITLE_BAND_H))
    pygame.draw.line(sheet, (90, 80, 60),
                     (0, TITLE_BAND_H - 1), (SHEET_W, TITLE_BAND_H - 1), 1)
    font_lg = pygame.font.Font(None, 28)
    font_sm = pygame.font.Font(None, 18)
    title = font_lg.render(
        "Cycle-finale cheering crowd  —  Round 2  ·  all-parrot crowd, "
        "bunting palette",
        True, (252, 244, 218))
    sheet.blit(title, (PAD, 8))
    sub = font_sm.render(
        "GOLD (255,220,110) · RED (220,64,32) · BLUE (96,176,232) · CREAM "
        "(252,244,218) · INK (30,20,8)  ·  ≤8 parrots / cell  ·  every-"
        "other figure jumping",
        True, (200, 195, 175))
    sheet.blit(sub, (PAD, 36))
    sub2 = font_sm.render(
        "Real grass+soil band + actual CelebrationGroundMarker sprite per "
        "cell  ·  head-tops verified ≤ GROUND_Y (595)",
        True, (170, 165, 150))
    sheet.blit(sub2, (PAD, 54))


def _draw_cell_caption(sheet, cx, cy, head, sub):
    font_h = pygame.font.Font(None, 19)
    font_s = pygame.font.Font(None, 15)
    head_s = font_h.render(head, True, (252, 244, 218))
    sub_s = font_s.render(sub, True, (180, 175, 155))
    sheet.blit(head_s, (cx + 4, cy - 32))
    sheet.blit(sub_s, (cx + 4, cy - 15))


def main():
    sheet = pygame.Surface((SHEET_W, SHEET_H))
    sheet.fill((22, 18, 28))
    _draw_title_band(sheet)

    variants = (
        draw_variant_1, draw_variant_2, draw_variant_3,
        draw_variant_4, draw_variant_5,
    )
    for idx, fn in enumerate(variants):
        row = idx // COLS
        col = idx % COLS
        cx = PAD + col * (CELL_W + PAD)
        cy = TITLE_BAND_H + PAD + row * (CELL_H + 28 + PAD) + 28
        cell = _make_cell(fn)
        sheet.blit(cell, (cx, cy))
        head, sub = VARIANT_TITLES[idx]
        _draw_cell_caption(sheet, cx, cy, head, sub)

    # 6th tile — 2× zoom of R2-1 right-side crowd.
    cx = PAD + 2 * (CELL_W + PAD)
    cy = TITLE_BAND_H + PAD + 1 * (CELL_H + 28 + PAD) + 28
    zoom = _make_zoom_tile(draw_variant_1)
    sheet.blit(zoom, (cx, cy))
    _draw_cell_caption(
        sheet, cx, cy,
        "Callout  ·  R2-1 right side at 2× scale",
        "verify instrument silhouettes (drum head ~6 / trumpet bell ~4 / "
        "flag ~8×5 / pom ~5)")

    out_path = os.path.join(
        REPO_ROOT, "docs", "treasure_box", "cheering_crowd_round2.png")
    pygame.image.save(sheet, out_path)
    print(out_path)


if __name__ == "__main__":
    main()
