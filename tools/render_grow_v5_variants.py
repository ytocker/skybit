"""Render 5 refined V5 variations: parrot centered with up-arrow BEHIND.

Run from repo root:  python tools/render_grow_v5_variants.py
Outputs in screenshots/:
  grow_v5_variants.png         — 3x2 comparison sheet
  grow_v5_a.png .. grow_v5_e.png — individual close-ups (256×256)

Source resolution bumped from 32px → 64px so the icons render cleaner
when upscaled.
"""
import os
import sys
import math

os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame
pygame.init()

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "screenshots")
os.makedirs(OUT_DIR, exist_ok=True)


# Palette
RED_BODY  = (240,  55,  55)
RED_BELLY = (255, 130,  90)
RED_DARK  = ( 80,  10,  18)
WING_BLUE = ( 40, 100, 255)
BEAK_GOLD = (255, 195,  60)
EYE_W     = (252, 252, 255)
EYE_BLK   = ( 12,  12,  20)
GREEN_HI  = ( 50, 220, 100)
GREEN_MID = ( 38, 190,  85)
GREEN_OUT = ( 28, 160,  70)
GREEN_DRK = ( 18, 110,  50)
WHITE     = (250, 250, 252)
BG_DARK   = ( 12,   8,  38)


def parrot_sprite(size: int) -> pygame.Surface:
    """Right-facing macaw silhouette. Tuned for size>=40 with slimmer outlines."""
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    cx, cy = size // 2, size // 2

    bw = int(size * 0.78)
    bh = int(size * 0.62)
    body = pygame.Rect(cx - bw // 2, cy - bh // 2 + 1, bw, bh)
    pygame.draw.ellipse(s, RED_DARK, body.inflate(2, 2))
    pygame.draw.ellipse(s, RED_BODY, body)
    belly = pygame.Rect(body.x + body.width // 4, body.centery,
                        body.width // 2 + 1, body.height // 2)
    pygame.draw.ellipse(s, RED_BELLY, belly)
    tail_pts = [
        (body.x + 1, body.centery),
        (body.x - int(size * 0.18), body.centery - int(size * 0.10)),
        (body.x - int(size * 0.22), body.centery + int(size * 0.10)),
        (body.x + 1, body.centery + int(size * 0.10)),
    ]
    pygame.draw.polygon(s, RED_DARK, tail_pts)
    pygame.draw.polygon(s, RED_BODY, [
        (body.x + 1, body.centery),
        (body.x - int(size * 0.14), body.centery - int(size * 0.06)),
        (body.x - int(size * 0.18), body.centery + int(size * 0.07)),
        (body.x + 1, body.centery + int(size * 0.07)),
    ])
    wing_pts = [
        (body.centerx - int(size * 0.05), body.centery - int(size * 0.04)),
        (body.centerx + int(size * 0.20), body.centery + int(size * 0.04)),
        (body.centerx - int(size * 0.02), body.centery + int(size * 0.18)),
    ]
    pygame.draw.polygon(s, RED_DARK, wing_pts)
    inner_wing = [
        (body.centerx - int(size * 0.02), body.centery - int(size * 0.01)),
        (body.centerx + int(size * 0.16), body.centery + int(size * 0.04)),
        (body.centerx - int(size * 0.01), body.centery + int(size * 0.14)),
    ]
    pygame.draw.polygon(s, WING_BLUE, inner_wing)
    bar_x = body.right - int(size * 0.42)
    bar_y = body.y + int(size * 0.10)
    bar_w = int(size * 0.36)
    bar_h = max(2, int(size * 0.14))
    pygame.draw.rect(s, EYE_BLK, (bar_x, bar_y, bar_w, bar_h), border_radius=1)
    # Pupil dots — scale with size
    pr = max(1, size // 32)
    pygame.draw.circle(s, EYE_W, (bar_x + bar_w // 4, bar_y + bar_h // 2), pr)
    pygame.draw.circle(s, EYE_W, (bar_x + 3 * bar_w // 4, bar_y + bar_h // 2), pr)
    bx0 = body.right - int(size * 0.04)
    by0 = body.y + int(size * 0.30)
    beak = [
        (bx0,                            by0),
        (bx0 + int(size * 0.18),         by0 + int(size * 0.06)),
        (bx0 + int(size * 0.06),         by0 + int(size * 0.18)),
        (bx0 - int(size * 0.04),         by0 + int(size * 0.10)),
    ]
    pygame.draw.polygon(s, RED_DARK, beak)
    inner_beak = [
        (bx0 + 1,                        by0 + 1),
        (bx0 + int(size * 0.14),         by0 + int(size * 0.07)),
        (bx0 + int(size * 0.05),         by0 + int(size * 0.14)),
        (bx0 - int(size * 0.02),         by0 + int(size * 0.09)),
    ]
    pygame.draw.polygon(s, BEAK_GOLD, inner_beak)
    return s


def draw_block_arrow(surf, cx, cy, head_w, shaft_w, total_h, fill, outline,
                     hi_band=None):
    """Vertical block-arrow centered at (cx, cy). The arrow head is at TOP.

      head_w = full width across the arrow head
      shaft_w = shaft width
      total_h = total height (head + shaft)
      hi_band = optional (hi_color) for a 2-px highlight band on the left edge
    """
    head_h = int(total_h * 0.42)
    top_y    = cy - total_h // 2
    head_bot = top_y + head_h
    bot_y    = cy + total_h // 2

    pts_out = [
        (cx,                  top_y),
        (cx + head_w // 2,    head_bot),
        (cx + shaft_w // 2,   head_bot),
        (cx + shaft_w // 2,   bot_y),
        (cx - shaft_w // 2,   bot_y),
        (cx - shaft_w // 2,   head_bot),
        (cx - head_w // 2,    head_bot),
    ]
    pygame.draw.polygon(surf, outline, pts_out)
    pts_in = [
        (cx,                      top_y + 2),
        (cx + head_w // 2 - 2,    head_bot - 1),
        (cx + shaft_w // 2 - 1,   head_bot - 1),
        (cx + shaft_w // 2 - 1,   bot_y - 1),
        (cx - shaft_w // 2 + 1,   bot_y - 1),
        (cx - shaft_w // 2 + 1,   head_bot - 1),
        (cx - head_w // 2 + 2,    head_bot - 1),
    ]
    pygame.draw.polygon(surf, fill, pts_in)
    if hi_band:
        # 2-px highlight band running down the left edge of the shaft
        pygame.draw.line(surf, hi_band,
                         (cx - shaft_w // 2 + 2, head_bot + 1),
                         (cx - shaft_w // 2 + 2, bot_y - 2), 2)
        pygame.draw.line(surf, hi_band,
                         (cx - 2, top_y + 4),
                         (cx - head_w // 4, head_bot - 2), 2)


def draw_chevron_only(surf, cx, cy, w, h, fill, outline):
    """Just the chevron HEAD shape (no shaft) — like a > rotated up."""
    pts_out = [
        (cx,             cy - h // 2),
        (cx + w // 2,    cy + h // 2),
        (cx + w // 4,    cy + h // 2),
        (cx,             cy),
        (cx - w // 4,    cy + h // 2),
        (cx - w // 2,    cy + h // 2),
    ]
    pygame.draw.polygon(surf, outline, pts_out)
    pts_in = [
        (cx,                 cy - h // 2 + 2),
        (cx + w // 2 - 2,    cy + h // 2 - 1),
        (cx + w // 4 - 1,    cy + h // 2 - 1),
        (cx,                 cy + 2),
        (cx - w // 4 + 1,    cy + h // 2 - 1),
        (cx - w // 2 + 2,    cy + h // 2 - 1),
    ]
    pygame.draw.polygon(surf, fill, pts_in)


# ── Variant A — single tall arrow extending above & below the parrot ────────
def candidate_a(size=64):
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    cx = cy = size // 2
    draw_block_arrow(s, cx, cy,
                     head_w=int(size * 0.62),
                     shaft_w=int(size * 0.26),
                     total_h=int(size * 0.92),
                     fill=GREEN_HI, outline=GREEN_OUT, hi_band=GREEN_MID)
    bird = parrot_sprite(int(size * 0.62))
    s.blit(bird, (cx - bird.get_width() // 2, cy - bird.get_height() // 2))
    return s


# ── Variant B — wide stubby arrow (head dominates) ──────────────────────────
def candidate_b(size=64):
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    cx = cy = size // 2
    draw_block_arrow(s, cx, cy,
                     head_w=int(size * 0.92),
                     shaft_w=int(size * 0.38),
                     total_h=int(size * 0.78),
                     fill=GREEN_HI, outline=GREEN_OUT, hi_band=GREEN_MID)
    bird = parrot_sprite(int(size * 0.66))
    s.blit(bird, (cx - bird.get_width() // 2, cy - bird.get_height() // 2 + 2))
    return s


# ── Variant C — outline-only arrow (frame), parrot fully visible inside ─────
def candidate_c(size=64):
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    cx = cy = size // 2
    head_w  = int(size * 0.86)
    shaft_w = int(size * 0.36)
    total_h = int(size * 0.92)
    head_h  = int(total_h * 0.42)
    top_y    = cy - total_h // 2
    head_bot = top_y + head_h
    bot_y    = cy + total_h // 2
    pts = [
        (cx,                  top_y),
        (cx + head_w // 2,    head_bot),
        (cx + shaft_w // 2,   head_bot),
        (cx + shaft_w // 2,   bot_y),
        (cx - shaft_w // 2,   bot_y),
        (cx - shaft_w // 2,   head_bot),
        (cx - head_w // 2,    head_bot),
    ]
    # Two-pass outline for that "thick frame" look
    pygame.draw.polygon(s, GREEN_OUT, pts, max(3, size // 18))
    pygame.draw.polygon(s, GREEN_HI,  pts, max(2, size // 32))
    bird = parrot_sprite(int(size * 0.62))
    s.blit(bird, (cx - bird.get_width() // 2, cy - bird.get_height() // 2))
    return s


# ── Variant D — stacked double chevron behind ──────────────────────────────
def candidate_d(size=64):
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    cx = size // 2
    # Two stacked chevrons pointing UP, one above the other
    draw_chevron_only(s, cx, int(size * 0.30),
                      w=int(size * 0.74), h=int(size * 0.30),
                      fill=GREEN_HI, outline=GREEN_OUT)
    draw_chevron_only(s, cx, int(size * 0.66),
                      w=int(size * 0.74), h=int(size * 0.30),
                      fill=GREEN_HI, outline=GREEN_OUT)
    bird = parrot_sprite(int(size * 0.60))
    s.blit(bird, (cx - bird.get_width() // 2,
                  size // 2 - bird.get_height() // 2))
    return s


# ── Variant E — solid arrow + side speed-line marks (energy) ────────────────
def candidate_e(size=64):
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    cx = cy = size // 2
    draw_block_arrow(s, cx, cy,
                     head_w=int(size * 0.58),
                     shaft_w=int(size * 0.24),
                     total_h=int(size * 0.86),
                     fill=GREEN_HI, outline=GREEN_OUT, hi_band=GREEN_MID)
    # Side speed lines — three short horizontal dashes on each flank,
    # inset from the canvas edges, suggesting upward motion.
    line_thk = max(2, size // 24)
    for i, frac in enumerate((0.30, 0.50, 0.70)):
        ly = int(size * frac)
        # Left side
        x1 = int(size * 0.04 + i * size * 0.025)
        x2 = x1 + max(4, size // 8)
        pygame.draw.line(s, GREEN_OUT, (x1, ly), (x2, ly), line_thk + 1)
        pygame.draw.line(s, GREEN_HI,  (x1, ly), (x2, ly), line_thk - 1)
        # Right side (mirror)
        x1r = size - x1
        x2r = size - x2
        pygame.draw.line(s, GREEN_OUT, (x1r, ly), (x2r, ly), line_thk + 1)
        pygame.draw.line(s, GREEN_HI,  (x1r, ly), (x2r, ly), line_thk - 1)
    bird = parrot_sprite(int(size * 0.60))
    s.blit(bird, (cx - bird.get_width() // 2, cy - bird.get_height() // 2))
    return s


# ── Compose ──────────────────────────────────────────────────────────────────

CANDIDATES = [
    ("A: tall arrow",     candidate_a),
    ("B: wide arrow",     candidate_b),
    ("C: frame outline",  candidate_c),
    ("D: double chevron", candidate_d),
    ("E: speed lines",    candidate_e),
]

CLOSEUP = 256
SRC = 64

# Individual close-ups
ascii_letters = ("a", "b", "c", "d", "e")
for letter, (name, fn) in zip(ascii_letters, CANDIDATES):
    canvas = pygame.Surface((CLOSEUP, CLOSEUP), pygame.SRCALPHA)
    pygame.draw.rect(canvas, (12, 8, 38, 235), canvas.get_rect(), border_radius=24)
    src = fn(SRC)
    upscaled = pygame.transform.scale(src, (CLOSEUP - 16, CLOSEUP - 16))
    canvas.blit(upscaled, (8, 8))
    out = os.path.join(OUT_DIR, f"grow_v5_{letter}.png")
    pygame.image.save(canvas, out)
    print("  saved", os.path.basename(out))


# 3×2 comparison sheet
CELL = 192
GAP  = 16
COLS = 3
ROWS = 2
PAD_TOP = 16
LABEL_H = 22
W = COLS * CELL + (COLS + 1) * GAP
H = ROWS * (CELL + LABEL_H) + (ROWS + 1) * GAP + PAD_TOP

sheet = pygame.Surface((W, H))
sheet.fill(BG_DARK)
title = pygame.font.Font(None, 24).render(
    "GROW icon V5 — 5 refined variations", True, (220, 200, 140))
sheet.blit(title, (GAP, 6))

label_font = pygame.font.Font(None, 18)
for i, (name, fn) in enumerate(CANDIDATES):
    col = i % COLS
    row = i // COLS
    x = GAP + col * (CELL + GAP)
    y = PAD_TOP + GAP + row * (CELL + LABEL_H + GAP)
    pygame.draw.rect(sheet, (22, 16, 52), (x, y, CELL, CELL), border_radius=6)
    pygame.draw.rect(sheet, (40, 30, 80), (x, y, CELL, CELL), 2, border_radius=6)
    src = fn(SRC)
    upscaled = pygame.transform.scale(src, (CELL - 12, CELL - 12))
    sheet.blit(upscaled, (x + 6, y + 6))
    label = label_font.render(name, True, (220, 210, 170))
    sheet.blit(label, (x + (CELL - label.get_width()) // 2, y + CELL + 2))

out = os.path.join(OUT_DIR, "grow_v5_variants.png")
pygame.image.save(sheet, out)
print("  saved", os.path.basename(out))
