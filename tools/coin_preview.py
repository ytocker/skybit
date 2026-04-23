"""Render 5 distinct coin design candidates side-by-side for review.

Each coin is drawn directly onto a single shared canvas so its silhouette
defines its shape — no circular halos, no per-coin backdrop panels. Writes
docs/screenshots/coin_options.png.

Usage:  python tools/coin_preview.py
"""
import math
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((1, 1))

SLOT_W = 220
COIN_Y = 180            # y-center of every coin
LABEL_Y = 280           # y-top of label block
COIN_DISPLAY_R = 44
HEADER_H = 70
CANVAS_H = 400

BG_TOP = (18, 22, 44)
BG_BOT = (8, 10, 22)
LABEL_FG = (240, 230, 200)
SUB_FG = (170, 180, 210)
ACCENT = (255, 205, 70)


# ─── A. Classic Gold Disc ────────────────────────────────────────────────────

def _draw_classic(surf: pygame.Surface, cx: int, cy: int):
    r = COIN_DISPLAY_R
    pygame.draw.circle(surf, (200, 140, 30), (cx, cy), r)
    pygame.draw.circle(surf, (255, 200, 50), (cx, cy), r - 3)
    pygame.draw.circle(surf, (255, 230, 110), (cx, cy), r - 8)

    for i in range(20):
        ang = i * math.tau / 20
        bx = cx + math.cos(ang) * (r - 3)
        by = cy + math.sin(ang) * (r - 3)
        pygame.draw.circle(surf, (180, 120, 20), (int(bx), int(by)), 2)

    def _star(color, ox=0, oy=0):
        pts = []
        for i in range(10):
            ang = -math.pi / 2 + i * math.tau / 10
            rr = (r - 14) if i % 2 == 0 else (r - 24)
            pts.append((cx + math.cos(ang) * rr + ox,
                        cy + math.sin(ang) * rr + oy))
        pygame.draw.polygon(surf, color, pts)
    _star((180, 110, 10), 0, 2)
    _star((255, 240, 150))

    hl = pygame.Surface((r, r), pygame.SRCALPHA)
    pygame.draw.ellipse(hl, (255, 255, 255, 130),
                        pygame.Rect(4, 3, int(r * 0.55), int(r * 0.3)))
    surf.blit(hl, (cx - r // 2 - 4, cy - r + 4))


# ─── B. Sonic Ring ──────────────────────────────────────────────────────────

def _draw_ring(surf: pygame.Surface, cx: int, cy: int):
    r_out = COIN_DISPLAY_R
    r_in = int(r_out * 0.52)

    ring = pygame.Surface((r_out * 2 + 8, r_out * 2 + 8), pygame.SRCALPHA)
    rx, ry = r_out + 4, r_out + 4

    for i in range(r_out, r_out - 12, -1):
        t = (r_out - i) / 12
        col = (
            int(255 * (1 - t) + 220 * t),
            int(230 * (1 - t) + 160 * t),
            int(80 * (1 - t) + 20 * t),
        )
        pygame.draw.circle(ring, col, (rx, ry), i)
    pygame.draw.circle(ring, (255, 250, 200), (rx, ry), r_out - 12)

    # Cut the hole — everything inside r_in becomes transparent
    pygame.draw.circle(ring, (0, 0, 0, 0), (rx, ry), r_in)

    pygame.draw.circle(ring, (150, 90, 10), (rx, ry), r_out, width=2)
    pygame.draw.circle(ring, (150, 90, 10), (rx, ry), r_in, width=2)

    pygame.draw.arc(ring, (255, 255, 240),
                    pygame.Rect(rx - r_out + 2, ry - r_out + 2,
                                (r_out - 2) * 2, (r_out - 2) * 2),
                    math.radians(120), math.radians(200), 3)

    surf.blit(ring, (cx - rx, cy - ry))


# ─── C. Faceted Gem (diamond / rupee) ────────────────────────────────────────

def _draw_gem(surf: pygame.Surface, cx: int, cy: int):
    r = COIN_DISPLAY_R

    top = (cx, cy - r - 2)
    bot = (cx, cy + r + 2)
    ul = (cx - r + 8, cy - r // 2)
    ur = (cx + r - 8, cy - r // 2)
    ll = (cx - r + 8, cy + r // 2)
    lr = (cx + r - 8, cy + r // 2)
    outline = [top, ur, lr, bot, ll, ul]

    pygame.draw.polygon(surf, (30, 170, 110), outline)

    right_facet = [top, ur, lr, bot]
    pygame.draw.polygon(surf, (20, 120, 80), right_facet)

    left_facet = [top, ul, ll, bot]
    pygame.draw.polygon(surf, (90, 230, 160), left_facet)

    pygame.draw.line(surf, (15, 80, 55), top, bot, 2)
    pygame.draw.line(surf, (15, 80, 55), ul, ur, 2)
    pygame.draw.line(surf, (15, 80, 55), ll, lr, 2)

    hl_pts = [top, (cx - 6, cy - r // 2 + 4), (cx + 6, cy - r // 2 + 4)]
    pygame.draw.polygon(surf, (220, 255, 230), hl_pts)

    pygame.draw.polygon(surf, (12, 60, 40), outline, width=2)


# ─── D. Plasma Orb ──────────────────────────────────────────────────────────

def _draw_plasma(surf: pygame.Surface, cx: int, cy: int):
    r = COIN_DISPLAY_R

    core_steps = 18
    for i in range(core_steps):
        t = i / (core_steps - 1)
        radius = int(r * (1 - t * 0.6))
        col = (
            int(255 * (1 - t * 0.1)),
            int(220 - 140 * t),
            int(255 - 120 * t),
        )
        a = int(255 * (1 - t * 0.8))
        circ = pygame.Surface((radius * 2 + 2, radius * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(circ, (*col, a), (radius + 1, radius + 1), radius)
        surf.blit(circ, (cx - radius - 1, cy - radius - 1))

    hl = pygame.Surface((r, r), pygame.SRCALPHA)
    pygame.draw.ellipse(hl, (255, 255, 255, 220),
                        pygame.Rect(0, 0, int(r * 0.45), int(r * 0.3)))
    surf.blit(hl, (cx - r // 2, cy - r // 2 - 4))


# ─── E. Parrot Medallion ────────────────────────────────────────────────────

def _draw_medallion(surf: pygame.Surface, cx: int, cy: int):
    r = COIN_DISPLAY_R

    # Scalloped outer edge — bumps are part of the silhouette, not a halo
    scallops = 16
    bump_r = 4
    for i in range(scallops):
        ang = i * math.tau / scallops
        bx = cx + math.cos(ang) * (r + 1)
        by = cy + math.sin(ang) * (r + 1)
        pygame.draw.circle(surf, (100, 60, 20), (int(bx), int(by)), bump_r + 1)
        pygame.draw.circle(surf, (200, 140, 70), (int(bx), int(by)), bump_r)

    pygame.draw.circle(surf, (90, 55, 20), (cx, cy), r)
    pygame.draw.circle(surf, (180, 125, 65), (cx, cy), r - 4)
    pygame.draw.circle(surf, (145, 95, 45), (cx, cy), r - 10)

    leaves = 14
    for i in range(leaves):
        ang = -math.pi / 2 + i * math.tau / leaves
        lx = cx + math.cos(ang) * (r - 7)
        ly = cy + math.sin(ang) * (r - 7)
        leaf = pygame.Surface((10, 6), pygame.SRCALPHA)
        pygame.draw.ellipse(leaf, (90, 140, 60), leaf.get_rect())
        pygame.draw.ellipse(leaf, (60, 110, 40), leaf.get_rect(), width=1)
        rot = math.degrees(ang) + 90
        leaf = pygame.transform.rotate(leaf, rot)
        lr = leaf.get_rect(center=(int(lx), int(ly)))
        surf.blit(leaf, lr.topleft)

    pygame.draw.ellipse(surf, (55, 30, 10),
                        pygame.Rect(cx - 13, cy - 6, 22, 20))
    pygame.draw.ellipse(surf, (230, 175, 95),
                        pygame.Rect(cx - 13, cy - 8, 22, 20))
    pygame.draw.circle(surf, (55, 30, 10), (cx - 6, cy - 10), 8)
    pygame.draw.circle(surf, (240, 190, 100), (cx - 6, cy - 12), 8)
    beak_pts = [(cx - 13, cy - 12), (cx - 20, cy - 8), (cx - 14, cy - 6)]
    pygame.draw.polygon(surf, (55, 30, 10), beak_pts)
    pygame.draw.circle(surf, (40, 20, 8), (cx - 4, cy - 12), 2)
    pygame.draw.polygon(surf, (55, 30, 10),
                        [(cx + 9, cy + 2), (cx + 18, cy + 8), (cx + 9, cy + 10)])
    pygame.draw.polygon(surf, (230, 175, 95),
                        [(cx + 9, cy), (cx + 17, cy + 6), (cx + 9, cy + 8)])

    pygame.draw.arc(surf, (255, 230, 170),
                    pygame.Rect(cx - r + 4, cy - r + 4, (r - 4) * 2, (r - 4) * 2),
                    math.radians(130), math.radians(210), 3)


# ─── compose ────────────────────────────────────────────────────────────────

def _draw_label(canvas, slot_x, letter, name, subtitle):
    font_l = pygame.font.SysFont("arial", 32, bold=True)
    font_n = pygame.font.SysFont("arial", 17, bold=True)
    font_s = pygame.font.SysFont("arial", 12, bold=False)

    cx = slot_x + SLOT_W // 2
    letter_img = font_l.render(letter, True, ACCENT)
    canvas.blit(letter_img, letter_img.get_rect(midtop=(cx, LABEL_Y)))

    name_img = font_n.render(name, True, LABEL_FG)
    canvas.blit(name_img, name_img.get_rect(midtop=(cx, LABEL_Y + 40)))

    sub_img = font_s.render(subtitle, True, SUB_FG)
    canvas.blit(sub_img, sub_img.get_rect(midtop=(cx, LABEL_Y + 62)))


def build_canvas() -> pygame.Surface:
    designs = [
        ("A", "Classic Gold Disc", "Mario-style disc + star", _draw_classic),
        ("B", "Sonic Ring",        "Hollow chrome torus",     _draw_ring),
        ("C", "Faceted Gem",       "Zelda-rupee diamond",     _draw_gem),
        ("D", "Plasma Orb",        "Soft glowing light",      _draw_plasma),
        ("E", "Parrot Medallion",  "Ornate bronze, parrot",   _draw_medallion),
    ]

    total_w = SLOT_W * len(designs)
    canvas = pygame.Surface((total_w, CANVAS_H), pygame.SRCALPHA)

    for y in range(CANVAS_H):
        t = y / CANVAS_H
        col = (
            int(BG_TOP[0] + (BG_BOT[0] - BG_TOP[0]) * t),
            int(BG_TOP[1] + (BG_BOT[1] - BG_TOP[1]) * t),
            int(BG_TOP[2] + (BG_BOT[2] - BG_TOP[2]) * t),
        )
        pygame.draw.line(canvas, col, (0, y), (total_w, y))

    title_f = pygame.font.SysFont("arial", 26, bold=True)
    sub_f = pygame.font.SysFont("arial", 15, bold=False)
    canvas.blit(title_f.render("Skybit — Coin Redesign Candidates",
                               True, (255, 220, 130)), (18, 14))
    canvas.blit(sub_f.render("Reply with a letter (A–E) to pick the look.",
                             True, SUB_FG), (18, 44))

    for i, (letter, name, subtitle, fn) in enumerate(designs):
        slot_x = i * SLOT_W
        cx = slot_x + SLOT_W // 2
        fn(canvas, cx, COIN_Y)
        _draw_label(canvas, slot_x, letter, name, subtitle)

    return canvas


if __name__ == "__main__":
    out_dir = os.path.join(ROOT, "docs", "screenshots")
    os.makedirs(out_dir, exist_ok=True)
    canvas = build_canvas()
    path = os.path.join(out_dir, "coin_options.png")
    pygame.image.save(canvas, path)
    print("wrote", path, canvas.get_size())
