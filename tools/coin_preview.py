"""Render 5 distinct coin design candidates side-by-side for review.

Each design is drawn on a 220×260 panel (200×200 visual + label band) and
tiled horizontally into a single PNG: docs/screenshots/coin_options.png.

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

PANEL_W = 220
PANEL_H = 260
CELL_CENTER = (PANEL_W // 2, 100)
COIN_DISPLAY_R = 44  # larger than in-game so details read in a static image
BG_TOP = (34, 46, 78)
BG_BOT = (18, 26, 52)
LABEL_BG = (10, 14, 32)
LABEL_FG = (240, 230, 200)
ACCENT = (255, 205, 70)


def _panel_bg() -> pygame.Surface:
    surf = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    for y in range(PANEL_H):
        t = y / PANEL_H
        col = (
            int(BG_TOP[0] + (BG_BOT[0] - BG_TOP[0]) * t),
            int(BG_TOP[1] + (BG_BOT[1] - BG_TOP[1]) * t),
            int(BG_TOP[2] + (BG_BOT[2] - BG_TOP[2]) * t),
        )
        pygame.draw.line(surf, col, (0, y), (PANEL_W, y))
    pygame.draw.rect(surf, (255, 255, 255, 18),
                     pygame.Rect(0, 0, PANEL_W, PANEL_H), width=1)
    return surf


def _glow(surf, cx, cy, r, color, alpha):
    g = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
    for i in range(r, 0, -2):
        a = int(alpha * (i / r) ** 2)
        pygame.draw.circle(g, (*color, a), (r, r), i)
    surf.blit(g, (cx - r, cy - r), special_flags=pygame.BLEND_ADD)


def _label(surf: pygame.Surface, letter: str, name: str, subtitle: str):
    font_l = pygame.font.SysFont("arial", 30, bold=True)
    font_n = pygame.font.SysFont("arial", 17, bold=True)
    font_s = pygame.font.SysFont("arial", 12, bold=False)

    band = pygame.Rect(0, PANEL_H - 66, PANEL_W, 66)
    pygame.draw.rect(surf, LABEL_BG, band)
    pygame.draw.rect(surf, ACCENT, pygame.Rect(0, band.y, PANEL_W, 2))

    l_img = font_l.render(letter, True, ACCENT)
    surf.blit(l_img, (12, band.y + 18))

    n_img = font_n.render(name, True, LABEL_FG)
    surf.blit(n_img, (50, band.y + 12))

    s_img = font_s.render(subtitle, True, (170, 180, 210))
    surf.blit(s_img, (50, band.y + 34))


# ─── A. Classic Gold Disc (Mario SMB) ────────────────────────────────────────

def _draw_classic(surf: pygame.Surface):
    cx, cy = CELL_CENTER
    r = COIN_DISPLAY_R
    _glow(surf, cx, cy, r + 22, (255, 210, 80), 110)

    pygame.draw.circle(surf, (120, 80, 10), (cx + 2, cy + 3), r)         # drop shadow
    pygame.draw.circle(surf, (200, 140, 30), (cx, cy), r)                 # dark rim
    pygame.draw.circle(surf, (255, 200, 50), (cx, cy), r - 3)             # mid gold
    pygame.draw.circle(surf, (255, 230, 110), (cx, cy), r - 8)            # bright disc

    # Bead-rim dots
    for i in range(20):
        ang = i * math.tau / 20
        bx = cx + math.cos(ang) * (r - 3)
        by = cy + math.sin(ang) * (r - 3)
        pygame.draw.circle(surf, (180, 120, 20), (int(bx), int(by)), 2)

    # Embossed star
    def _star(color, ox=0, oy=0):
        pts = []
        for i in range(10):
            ang = -math.pi / 2 + i * math.tau / 10
            rr = (r - 14) if i % 2 == 0 else (r - 24)
            pts.append((cx + math.cos(ang) * rr + ox,
                        cy + math.sin(ang) * rr + oy))
        pygame.draw.polygon(surf, color, pts)
    _star((180, 110, 10), 0, 2)     # emboss shadow
    _star((255, 240, 150))            # star face

    # Specular highlight
    hl = pygame.Surface((r, r), pygame.SRCALPHA)
    pygame.draw.ellipse(hl, (255, 255, 255, 130),
                        pygame.Rect(4, 3, int(r * 0.55), int(r * 0.3)))
    surf.blit(hl, (cx - r // 2 - 4, cy - r + 4))


# ─── B. Sonic Ring ──────────────────────────────────────────────────────────

def _draw_ring(surf: pygame.Surface):
    cx, cy = CELL_CENTER
    r_out = COIN_DISPLAY_R
    r_in = int(r_out * 0.52)
    _glow(surf, cx, cy, r_out + 20, (255, 240, 120), 150)

    # Outer soft shadow
    shadow = pygame.Surface((r_out * 2 + 10, r_out * 2 + 10), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow, (0, 0, 0, 110),
                        pygame.Rect(0, 0, r_out * 2 + 10, r_out * 2 + 10))
    surf.blit(shadow, (cx - r_out - 5 + 3, cy - r_out - 5 + 5))

    # Build the ring by drawing outer disc then cutting the hole with SRCALPHA
    ring = pygame.Surface((r_out * 2 + 8, r_out * 2 + 8), pygame.SRCALPHA)
    rx, ry = r_out + 4, r_out + 4

    # Chrome gradient (top → bottom: pale yellow → deep gold)
    for i in range(r_out, r_out - 12, -1):
        t = (r_out - i) / 12
        col = (
            int(255 * (1 - t) + 220 * t),
            int(230 * (1 - t) + 160 * t),
            int(80 * (1 - t) + 20 * t),
        )
        pygame.draw.circle(ring, col, (rx, ry), i)
    pygame.draw.circle(ring, (255, 250, 200), (rx, ry), r_out - 12)

    # Punch the hole (transparent center)
    pygame.draw.circle(ring, (0, 0, 0, 0), (rx, ry), r_in)

    # Thin dark rim around outer + inner edges for separation
    pygame.draw.circle(ring, (150, 90, 10), (rx, ry), r_out, width=2)
    pygame.draw.circle(ring, (150, 90, 10), (rx, ry), r_in, width=2)

    # Top-left highlight arc
    pygame.draw.arc(ring, (255, 255, 240),
                    pygame.Rect(rx - r_out + 2, ry - r_out + 2,
                                (r_out - 2) * 2, (r_out - 2) * 2),
                    math.radians(120), math.radians(200), 3)

    surf.blit(ring, (cx - rx, cy - ry))


# ─── C. Faceted Gem (Zelda rupee) ────────────────────────────────────────────

def _draw_gem(surf: pygame.Surface):
    cx, cy = CELL_CENTER
    r = COIN_DISPLAY_R
    _glow(surf, cx, cy, r + 20, (120, 255, 180), 120)

    # Hex-ish rupee silhouette: tall diamond with flat top/bottom
    top = (cx, cy - r - 2)
    bot = (cx, cy + r + 2)
    ul = (cx - r + 8, cy - r // 2)
    ur = (cx + r - 8, cy - r // 2)
    ll = (cx - r + 8, cy + r // 2)
    lr = (cx + r - 8, cy + r // 2)
    outline = [top, ur, lr, bot, ll, ul]

    # Drop shadow
    shadow = [(p[0] + 3, p[1] + 4) for p in outline]
    pygame.draw.polygon(surf, (10, 40, 30), shadow)

    # Main emerald body
    pygame.draw.polygon(surf, (30, 170, 110), outline)

    # Darker right facet
    right_facet = [top, ur, lr, bot]
    pygame.draw.polygon(surf, (20, 120, 80), right_facet)

    # Bright left facet
    left_facet = [top, ul, ll, bot]
    pygame.draw.polygon(surf, (90, 230, 160), left_facet)

    # Central vertical seam
    pygame.draw.line(surf, (15, 80, 55), top, bot, 2)

    # Horizontal seam
    pygame.draw.line(surf, (15, 80, 55), ul, ur, 2)
    pygame.draw.line(surf, (15, 80, 55), ll, lr, 2)

    # Top specular triangle
    hl_pts = [top, (cx - 6, cy - r // 2 + 4), (cx + 6, cy - r // 2 + 4)]
    pygame.draw.polygon(surf, (220, 255, 230), hl_pts)

    # Outer hard outline
    pygame.draw.polygon(surf, (12, 60, 40), outline, width=2)


# ─── D. Plasma Orb (modern mobile) ───────────────────────────────────────────

def _draw_plasma(surf: pygame.Surface):
    cx, cy = CELL_CENTER
    r = COIN_DISPLAY_R

    # Big soft halo
    for i in range(r + 32, 4, -2):
        t = 1 - i / (r + 32)
        a = int(190 * t ** 2)
        col_r = int(120 + 135 * t)
        col_g = int(80 + 150 * t)
        col_b = int(200 + 40 * t)
        g = pygame.Surface((i * 2, i * 2), pygame.SRCALPHA)
        pygame.draw.circle(g, (col_r, col_g, col_b, a), (i, i), i)
        surf.blit(g, (cx - i, cy - i), special_flags=pygame.BLEND_ADD)

    # Inner condensed core — no hard rim
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

    # Pin-bright inner highlight, offset up-left
    hl = pygame.Surface((r, r), pygame.SRCALPHA)
    pygame.draw.ellipse(hl, (255, 255, 255, 220),
                        pygame.Rect(0, 0, int(r * 0.45), int(r * 0.3)))
    surf.blit(hl, (cx - r // 2, cy - r // 2 - 4))

    # Faint sparkle cross
    spark = pygame.Surface((r * 3, r * 3), pygame.SRCALPHA)
    pygame.draw.line(spark, (255, 255, 255, 150),
                     (r * 3 // 2, r + 4), (r * 3 // 2, r * 2 - 4), 2)
    pygame.draw.line(spark, (255, 255, 255, 150),
                     (r + 4, r * 3 // 2), (r * 2 - 4, r * 3 // 2), 2)
    surf.blit(spark, (cx - r * 3 // 2, cy - r * 3 // 2),
              special_flags=pygame.BLEND_ADD)


# ─── E. Ornate Medallion (parrot motif, bronze) ─────────────────────────────

def _draw_medallion(surf: pygame.Surface):
    cx, cy = CELL_CENTER
    r = COIN_DISPLAY_R
    _glow(surf, cx, cy, r + 18, (220, 150, 70), 100)

    # Scalloped outer edge — 16 tiny bumps around the rim
    scallops = 16
    bump_r = 4
    for i in range(scallops):
        ang = i * math.tau / scallops
        bx = cx + math.cos(ang) * (r + 1)
        by = cy + math.sin(ang) * (r + 1)
        pygame.draw.circle(surf, (100, 60, 20), (int(bx), int(by)), bump_r + 1)
        pygame.draw.circle(surf, (200, 140, 70), (int(bx), int(by)), bump_r)

    # Main medallion disc — antique bronze
    pygame.draw.circle(surf, (90, 55, 20), (cx, cy), r)                   # deep rim
    pygame.draw.circle(surf, (180, 125, 65), (cx, cy), r - 4)             # mid bronze
    pygame.draw.circle(surf, (145, 95, 45), (cx, cy), r - 10)             # inner field

    # Laurel wreath — tiny leaves around the inner disc
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

    # Embossed parrot silhouette (beak + head + body) — simplified profile
    # Body
    pygame.draw.ellipse(surf, (55, 30, 10),
                        pygame.Rect(cx - 13, cy - 6, 22, 20))
    pygame.draw.ellipse(surf, (230, 175, 95),
                        pygame.Rect(cx - 13, cy - 8, 22, 20))
    # Head
    pygame.draw.circle(surf, (55, 30, 10), (cx - 6, cy - 10), 8)
    pygame.draw.circle(surf, (240, 190, 100), (cx - 6, cy - 12), 8)
    # Beak (hook)
    beak_pts = [(cx - 13, cy - 12), (cx - 20, cy - 8), (cx - 14, cy - 6)]
    pygame.draw.polygon(surf, (55, 30, 10), beak_pts)
    # Eye
    pygame.draw.circle(surf, (40, 20, 8), (cx - 4, cy - 12), 2)
    # Tail feather streak
    pygame.draw.polygon(surf, (55, 30, 10),
                        [(cx + 9, cy + 2), (cx + 18, cy + 8), (cx + 9, cy + 10)])
    pygame.draw.polygon(surf, (230, 175, 95),
                        [(cx + 9, cy), (cx + 17, cy + 6), (cx + 9, cy + 8)])

    # Top-left specular arc
    pygame.draw.arc(surf, (255, 230, 170),
                    pygame.Rect(cx - r + 4, cy - r + 4, (r - 4) * 2, (r - 4) * 2),
                    math.radians(130), math.radians(210), 3)


# ─── compose ────────────────────────────────────────────────────────────────

def build_canvas() -> pygame.Surface:
    designs = [
        ("A", "Classic Gold Disc", "Mario-style disc + star",
         _draw_classic),
        ("B", "Sonic Ring", "Hollow chrome torus",
         _draw_ring),
        ("C", "Faceted Gem", "Zelda-rupee emerald",
         _draw_gem),
        ("D", "Plasma Orb", "Soft glowing light",
         _draw_plasma),
        ("E", "Parrot Medallion", "Ornate bronze, parrot motif",
         _draw_medallion),
    ]

    header_h = 70
    total_w = PANEL_W * len(designs) + 10 * (len(designs) + 1)
    total_h = header_h + PANEL_H + 20

    canvas = pygame.Surface((total_w, total_h), pygame.SRCALPHA)
    # Dark page background
    for y in range(total_h):
        t = y / total_h
        col = (int(10 + 8 * t), int(12 + 6 * t), int(24 + 12 * t))
        pygame.draw.line(canvas, col, (0, y), (total_w, y))

    title_f = pygame.font.SysFont("arial", 28, bold=True)
    sub_f = pygame.font.SysFont("arial", 15, bold=False)
    title = title_f.render("Skybit — Coin Redesign Candidates",
                           True, (255, 220, 130))
    canvas.blit(title, (18, 14))
    sub = sub_f.render("Reply with a letter (A–E) to pick the look.",
                       True, (180, 190, 220))
    canvas.blit(sub, (18, 44))

    x = 10
    y = header_h
    for letter, name, subtitle, fn in designs:
        panel = _panel_bg()
        fn(panel)
        _label(panel, letter, name, subtitle)
        canvas.blit(panel, (x, y))
        x += PANEL_W + 10

    return canvas


if __name__ == "__main__":
    out_dir = os.path.join(ROOT, "docs", "screenshots")
    os.makedirs(out_dir, exist_ok=True)
    canvas = build_canvas()
    path = os.path.join(out_dir, "coin_options.png")
    pygame.image.save(canvas, path)
    print("wrote", path, canvas.get_size())
