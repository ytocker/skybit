"""Render 5 candidate GROW icons inspired by online grow/buff motifs.

Run from repo root:  python tools/render_grow_candidates.py
Outputs in screenshots/:
  grow_icon_versions.png   — 3x2 comparison sheet
  grow_v1.png .. grow_v5.png — individual 256x256 close-ups
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


# Palette — matches the in-game parrot
RED_BODY  = (240,  55,  55)
RED_BELLY = (255, 130,  90)
RED_DARK  = ( 80,  10,  18)
WING_BLUE = ( 40, 100, 255)
BEAK_GOLD = (255, 195,  60)
EYE_W     = (252, 252, 255)
EYE_BLK   = ( 12,  12,  20)
GREEN_HI  = ( 50, 220, 100)
GREEN_OUT = ( 28, 160,  70)
STAR_GOLD = (255, 220,  80)
STAR_DARK = (180, 130,  20)
WHITE     = (250, 250, 252)
MUSH_RED  = (220,  35,  35)
MUSH_DARK = (130,  10,  20)
MUSH_HI   = (255,  90,  90)
STEM_HI   = (252, 232, 200)
STEM_DARK = (185, 155, 110)
BG_DARK   = ( 12,   8,  38)


def parrot_sprite(size: int, outline_only: bool = False) -> pygame.Surface:
    """Right-facing macaw silhouette. If outline_only, draw only the dark body
    outline as a faint ghost shape (used by V1 nesting silhouettes)."""
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    cx, cy = size // 2, size // 2

    bw = int(size * 0.78)
    bh = int(size * 0.62)
    body = pygame.Rect(cx - bw // 2, cy - bh // 2 + 1, bw, bh)
    if outline_only:
        pygame.draw.ellipse(s, RED_DARK, body, max(2, size // 18))
        # Tail
        tail_pts = [
            (body.x + 1, body.centery),
            (body.x - int(size * 0.18), body.centery - int(size * 0.10)),
            (body.x - int(size * 0.22), body.centery + int(size * 0.10)),
            (body.x + 1, body.centery + int(size * 0.10)),
        ]
        pygame.draw.lines(s, RED_DARK, True, tail_pts, max(2, size // 18))
        # Beak
        bx0 = body.right - int(size * 0.04)
        by0 = body.y + int(size * 0.30)
        beak = [
            (bx0,                            by0),
            (bx0 + int(size * 0.18),         by0 + int(size * 0.06)),
            (bx0 + int(size * 0.06),         by0 + int(size * 0.18)),
            (bx0 - int(size * 0.04),         by0 + int(size * 0.10)),
        ]
        pygame.draw.lines(s, RED_DARK, True, beak, max(2, size // 18))
        return s

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
    if size >= 22:
        pygame.draw.circle(s, EYE_W, (bar_x + bar_w // 4, bar_y + bar_h // 2), 1)
        pygame.draw.circle(s, EYE_W, (bar_x + 3 * bar_w // 4, bar_y + bar_h // 2), 1)
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


def draw_chunky_chevron(surf, cx, cy, w, h, fill, outline):
    """Upward-pointing block chevron centered at (cx, cy)."""
    pts_out = [
        (cx,         cy - h),
        (cx + w,     cy - h // 4),
        (cx + w // 2, cy - h // 4),
        (cx + w // 2, cy + h // 2),
        (cx - w // 2, cy + h // 2),
        (cx - w // 2, cy - h // 4),
        (cx - w,     cy - h // 4),
    ]
    pygame.draw.polygon(surf, outline, pts_out)
    pts_in = [
        (cx,             cy - h + 2),
        (cx + w - 2,     cy - h // 4 + 1),
        (cx + w // 2 - 1, cy - h // 4 + 1),
        (cx + w // 2 - 1, cy + h // 2 - 1),
        (cx - w // 2 + 1, cy + h // 2 - 1),
        (cx - w // 2 + 1, cy - h // 4 + 1),
        (cx - w + 2,     cy - h // 4 + 1),
    ]
    pygame.draw.polygon(surf, fill, pts_in)


def draw_5_point_star(surf, cx, cy, r_outer, r_inner, fill, outline):
    """5-pointed star centered at (cx, cy)."""
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        r = r_outer if i % 2 == 0 else r_inner
        pts.append((cx + math.cos(ang) * r, cy + math.sin(ang) * r))
    pygame.draw.polygon(surf, outline, pts)
    inner_pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        r = (r_outer - 2) if i % 2 == 0 else (r_inner - 1)
        inner_pts.append((cx + math.cos(ang) * r, cy + math.sin(ang) * r))
    pygame.draw.polygon(surf, fill, inner_pts)


# ── V1 — Two-frame evolution ────────────────────────────────────────────────
def candidate_v1(size=32):
    """Small parrot on the left → big parrot on the right, with a green
    up-chevron between them ('it grows')."""
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    small = parrot_sprite(int(size * 0.34))
    big   = parrot_sprite(int(size * 0.62))
    base = size - 3
    # Position them at the far edges so the chevron has room in the middle.
    s.blit(small, (0, base - small.get_height()))
    s.blit(big,   (size - big.get_width(), base - big.get_height()))
    # Green up-chevron in the gap, sitting above the small bird's head height.
    mid_x = small.get_width() + (size - small.get_width() - big.get_width()) // 2
    mid_y = base - small.get_height() // 2 - 1
    draw_chunky_chevron(s, mid_x, mid_y,
                        w=max(2, int(size * 0.09)),
                        h=max(4, int(size * 0.20)),
                        fill=GREEN_HI, outline=GREEN_OUT)
    return s


# ── V2 — Parrot perched on a Mario-style mushroom ───────────────────────────
def candidate_v2(size=32):
    """Mario super-mushroom in the lower half, parrot perched on top of the
    cap. Riffs on the canonical 'grow' icon while staying skybit-themed."""
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    cx = size // 2

    # Stem occupies the bottom band
    stem = pygame.Rect(cx - int(size * 0.20), int(size * 0.74),
                       int(size * 0.40), int(size * 0.22))
    pygame.draw.rect(s, MUSH_DARK, stem.inflate(2, 2), border_radius=2)
    pygame.draw.rect(s, STEM_HI, stem, border_radius=2)

    # Cap — wider, shorter, sits in the lower-middle band
    cap_rect = pygame.Rect(cx - int(size * 0.46), int(size * 0.42),
                           int(size * 0.92), int(size * 0.36))
    pygame.draw.ellipse(s, MUSH_DARK, cap_rect.inflate(2, 2))
    pygame.draw.ellipse(s, MUSH_RED, cap_rect)
    # Hot upper rim
    hi = pygame.Rect(cap_rect.x + 2, cap_rect.y + 2, cap_rect.width - 4, int(size * 0.10))
    pygame.draw.ellipse(s, MUSH_HI, hi)
    # White spots
    for sx, sy, sr in (
        (cx - int(size * 0.22), int(size * 0.52), max(2, int(size * 0.07))),
        (cx + int(size * 0.18), int(size * 0.50), max(2, int(size * 0.08))),
        (cx + int(size * 0.02), int(size * 0.60), max(1, int(size * 0.05))),
    ):
        pygame.draw.circle(s, WHITE, (sx, sy), sr)

    # Parrot perched ON TOP of the cap, fully visible.
    bird = parrot_sprite(int(size * 0.52))
    s.blit(bird, (cx - bird.get_width() // 2, int(size * 0.06)))
    return s


# ── V3 — Super-Star halo ────────────────────────────────────────────────────
def candidate_v3(size=32):
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    cx = cy = size // 2
    # Star behind
    draw_5_point_star(s, cx, cy,
                      r_outer=int(size * 0.50),
                      r_inner=int(size * 0.22),
                      fill=GREEN_HI, outline=GREEN_OUT)
    # Bird centred
    bird = parrot_sprite(int(size * 0.66))
    s.blit(bird, ((size - bird.get_width()) // 2, (size - bird.get_height()) // 2))
    return s


# ── V4 — Expand corners (fullscreen-style) ──────────────────────────────────
def candidate_v4(size=32):
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    bird = parrot_sprite(int(size * 0.72))
    s.blit(bird, ((size - bird.get_width()) // 2, (size - bird.get_height()) // 2))

    # Four corner L-bracket arrows pointing OUTWARD.
    pad = max(1, size // 16)
    arm = max(3, int(size * 0.16))
    thk = max(2, int(size * 0.06))

    def corner(x0, y0, dx, dy):
        # Two perpendicular bars meeting at (x0, y0), each `arm` long, `thk` thick.
        # Bar 1: along x
        if dx > 0:
            r1 = pygame.Rect(x0, y0, arm, thk)
        else:
            r1 = pygame.Rect(x0 - arm, y0, arm, thk)
        # Bar 2: along y
        if dy > 0:
            r2 = pygame.Rect(x0, y0, thk, arm)
        else:
            r2 = pygame.Rect(x0, y0 - arm, thk, arm)
        for r in (r1, r2):
            pygame.draw.rect(s, GREEN_OUT, r.inflate(2, 2))
            pygame.draw.rect(s, GREEN_HI, r)
        # Arrow tip — small triangle at the far end of each bar
        if dx > 0:
            tip = [(r1.right + 4, r1.centery),
                   (r1.right, r1.top - 2), (r1.right, r1.bottom + 2)]
        else:
            tip = [(r1.left - 4, r1.centery),
                   (r1.left, r1.top - 2), (r1.left, r1.bottom + 2)]
        pygame.draw.polygon(s, GREEN_OUT, tip)
        if dx > 0:
            tip_in = [(r1.right + 2, r1.centery),
                      (r1.right, r1.top - 0), (r1.right, r1.bottom + 0)]
        else:
            tip_in = [(r1.left - 2, r1.centery),
                      (r1.left, r1.top - 0), (r1.left, r1.bottom + 0)]
        pygame.draw.polygon(s, GREEN_HI, tip_in)
        if dy > 0:
            tip2 = [(r2.centerx, r2.bottom + 4),
                    (r2.left - 2, r2.bottom), (r2.right + 2, r2.bottom)]
        else:
            tip2 = [(r2.centerx, r2.top - 4),
                    (r2.left - 2, r2.top), (r2.right + 2, r2.top)]
        pygame.draw.polygon(s, GREEN_OUT, tip2)

    corner(pad,             pad,             +1, +1)
    corner(size - pad - 1,  pad,             -1, +1)
    corner(pad,             size - pad - 1, +1, -1)
    corner(size - pad - 1,  size - pad - 1, -1, -1)
    return s


# ── V5 — Boost-arrow podium ─────────────────────────────────────────────────
def candidate_v5(size=32):
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    cx = size // 2

    # Big chunky up-arrow occupying lower 70%
    aw_head = int(size * 0.78)
    aw_shaft = int(size * 0.36)
    head_top_y = int(size * 0.30)
    head_bot_y = int(size * 0.55)
    shaft_bot_y = size - 2

    pts_out = [
        (cx,                       head_top_y),
        (cx + aw_head // 2,        head_bot_y),
        (cx + aw_shaft // 2,       head_bot_y),
        (cx + aw_shaft // 2,       shaft_bot_y),
        (cx - aw_shaft // 2,       shaft_bot_y),
        (cx - aw_shaft // 2,       head_bot_y),
        (cx - aw_head // 2,        head_bot_y),
    ]
    pygame.draw.polygon(s, GREEN_OUT, pts_out)
    pts_in = [
        (cx,                          head_top_y + 2),
        (cx + aw_head // 2 - 2,       head_bot_y - 1),
        (cx + aw_shaft // 2 - 1,      head_bot_y - 1),
        (cx + aw_shaft // 2 - 1,      shaft_bot_y - 1),
        (cx - aw_shaft // 2 + 1,      shaft_bot_y - 1),
        (cx - aw_shaft // 2 + 1,      head_bot_y - 1),
        (cx - aw_head // 2 + 2,       head_bot_y - 1),
    ]
    pygame.draw.polygon(s, GREEN_HI, pts_in)

    # Bird perched on top of the arrow tip — slightly oversized so it
    # visually "rides" the boost.
    bird = parrot_sprite(int(size * 0.60))
    bx = cx - bird.get_width() // 2
    by = max(0, head_top_y - bird.get_height() // 2 - 2)
    s.blit(bird, (bx, by))
    return s


# ── Compose comparison sheet + close-ups ─────────────────────────────────────

CANDIDATES = [
    ("V1: nest",     candidate_v1),
    ("V2: mushroom", candidate_v2),
    ("V3: star",     candidate_v3),
    ("V4: expand",   candidate_v4),
    ("V5: boost",    candidate_v5),
]

CLOSEUP = 256
SRC = 32

# Individual close-ups
for i, (name, fn) in enumerate(CANDIDATES, start=1):
    canvas = pygame.Surface((CLOSEUP, CLOSEUP), pygame.SRCALPHA)
    pygame.draw.rect(canvas, (12, 8, 38, 235), canvas.get_rect(), border_radius=24)
    src = fn(SRC)
    upscaled = pygame.transform.scale(src, (CLOSEUP - 16, CLOSEUP - 16))
    canvas.blit(upscaled, (8, 8))
    out = os.path.join(OUT_DIR, f"grow_v{i}.png")
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
    "GROW icon — 5 candidates", True, (220, 200, 140))
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

out = os.path.join(OUT_DIR, "grow_icon_versions.png")
pygame.image.save(sheet, out)
print("  saved", os.path.basename(out))
