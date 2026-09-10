"""Render 5 size variants of the chosen 'beefy' coil megamagnet
design (thick coil body + thick cyan zigzag arc + spherical
discharge balls at each pole tip). Sizes range from 'matches the
original silhouette' up to '+2 px wider, thicker arms', all smaller
than the previous draft (outer_r=16) which read as too large.

Run from repo root:

    python tools/snapshot_megamagnet_beefy_sizes.py

Outputs under docs/screenshots/powerups/megamagnet/:
    beefy_NN_<name>.png       (5 per-variant cells)
    beefy_size_variants.png   (combined 3x2 sheet with reference + 5)
"""
import os
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "dummy"

import math
import sys
import pygame
pygame.init()

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.entities import PowerUp


OUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "docs", "screenshots", "powerups", "megamagnet",
)
os.makedirs(OUT_DIR, exist_ok=True)


CELL_RAW = 90
ZOOM = 3
CELL_W = CELL_RAW * ZOOM
CELL_H = CELL_RAW * ZOOM
PULSE = 1.6

BALL_R = 3      # main yellow-white core (was 4 in too-big draft)
BALL_HALO_R = 7 # outer cyan glow


def _draw_body(surf, cx, cy, outer_r, inner_r):
    arch_cy = cy - 3
    leg_bot = cy + 13

    sz = 52
    scx = sz // 2
    scy = outer_r + 4

    scratch = pygame.Surface((sz, sz), pygame.SRCALPHA)
    pygame.draw.circle(scratch, (80, 5, 8), (scx, scy), outer_r + 2)
    pygame.draw.rect(scratch, (80, 5, 8),
                     (scx - outer_r - 2, scy,
                      (outer_r + 2) * 2, leg_bot - arch_cy + 4))
    RED_HI = (235, 35, 45)
    pygame.draw.circle(scratch, RED_HI, (scx, scy), outer_r + 1)
    pygame.draw.rect(scratch, RED_HI,
                     (scx - outer_r - 1, scy,
                      (outer_r + 1) * 2, leg_bot - arch_cy + 3))
    pygame.draw.circle(scratch, (255, 95, 95), (scx, scy), inner_r + 1, 2)
    pygame.draw.circle(scratch, (255, 85, 85), (scx, scy), outer_r, 2)
    pygame.draw.circle(scratch, (0, 0, 0, 0), (scx, scy), inner_r)
    pygame.draw.rect(scratch, (0, 0, 0, 0),
                     (scx - inner_r, scy, inner_r * 2, sz - scy))
    surf.blit(scratch, (cx - scx, arch_cy - scy))

    left_cx = cx - inner_r - (outer_r - inner_r) // 2
    right_cx = cx + inner_r + (outer_r - inner_r) // 2
    arm_w = outer_r - inner_r
    for tip_cx in (left_cx, right_cx):
        pygame.draw.rect(surf, (40, 42, 60),
                         (tip_cx - arm_w // 2 - 1, leg_bot - 4, arm_w + 2, 9),
                         border_radius=4)
        pygame.draw.rect(surf, (195, 210, 232),
                         (tip_cx - arm_w // 2, leg_bot - 3, arm_w, 7),
                         border_radius=3)
        pygame.draw.rect(surf, (238, 246, 255),
                         (tip_cx - arm_w // 2 + 1, leg_bot - 3, arm_w - 2, 3),
                         border_radius=2)
    return leg_bot, left_cx, right_cx


def _draw_copper_coil(surf, cy, lcx, rcx, arm_w):
    COPPER_LO = (110, 55, 14)
    COPPER_HI = (220, 130, 55)
    HIGHLIGHT = (255, 225, 160)
    for tip_cx in (lcx, rcx):
        for i in range(4):
            wy = cy + 2 + i * 3
            left_x = tip_cx - arm_w // 2 - 1
            right_x = tip_cx + arm_w // 2 + 1
            mid_x = tip_cx
            dip = 1 if (i % 2 == 0) else -1
            pygame.draw.lines(surf, COPPER_LO, False,
                              [(left_x, wy + 1),
                               (mid_x, wy + 1 + dip),
                               (right_x, wy + 1)], 2)
            pygame.draw.lines(surf, COPPER_HI, False,
                              [(left_x, wy),
                               (mid_x, wy + dip),
                               (right_x, wy)], 1)
            pygame.draw.line(surf, HIGHLIGHT,
                             (left_x + 1, wy), (mid_x - 1, wy))


def _draw_beefy_arc_and_balls(surf, leg_bot, lcx, rcx):
    """Beefy zigzag arc between the pole tips + big spherical
    yellow-white discharge balls at each pole."""
    y0 = leg_bot + 7
    # Zigzag — 6 segments, ±5 amplitude.
    pts = [(lcx, y0)]
    for i in range(1, 6):
        t = i / 6
        x = int(lcx + (rcx - lcx) * t)
        y = int(y0 + math.sin(PULSE * 11 + i * 1.7) * 5)
        pts.append((x, y))
    pts.append((rcx, y0))

    arc_surf = pygame.Surface((rcx - lcx + 16, 20), pygame.SRCALPHA)
    shifted = [(p[0] - lcx + 8, p[1] - y0 + 8) for p in pts]
    pygame.draw.lines(arc_surf, (110, 195, 255, 230), False, shifted, 4)
    pygame.draw.lines(arc_surf, (220, 240, 255, 255), False, shifted, 2)
    surf.blit(arc_surf, (lcx - 8, y0 - 8))

    # Discharge balls at each pole tip — cyan halo + yellow mid + white core.
    for tip_cx in (lcx, rcx):
        ball_cy = leg_bot + 2
        glow = pygame.Surface((BALL_HALO_R * 2 + 2, BALL_HALO_R * 2 + 2),
                              pygame.SRCALPHA)
        gcx = BALL_HALO_R + 1
        for r in range(BALL_HALO_R, 0, -1):
            t = r / BALL_HALO_R
            a = int(180 * (1 - t * 0.85))
            pygame.draw.circle(glow, (130, 210, 255, a), (gcx, gcx), r)
        surf.blit(glow, (tip_cx - gcx, ball_cy - gcx))
        pygame.draw.circle(surf, (255, 230, 100), (tip_cx, ball_cy), BALL_R)
        pygame.draw.circle(surf, (255, 255, 240), (tip_cx, ball_cy),
                           max(1, BALL_R - 2))


def render_size(outer_r, inner_r):
    """Return a render fn for the given body dimensions."""
    def _r(cell):
        cx, cy = CELL_RAW // 2, CELL_RAW // 2 - 3
        leg_bot, lcx, rcx = _draw_body(cell, cx, cy, outer_r, inner_r)
        _draw_copper_coil(cell, cy, lcx, rcx, outer_r - inner_r)
        _draw_beefy_arc_and_balls(cell, leg_bot, lcx, rcx)
    return _r


def render_reference(cell):
    """Production magnet for size comparison."""
    cx, cy = CELL_RAW // 2, CELL_RAW // 2 - 3
    p = PowerUp(cx, cy, "magnet")
    p.pulse = PULSE
    p.draw(cell)


# (file-name suffix, outer_r, inner_r, label)
SIZES = (
    ("01_A_same_size",  13, 6, "A  same size as original"),
    ("02_B_plus1",      14, 6, "B  +1 px wider"),
    ("03_C_plus1_thick", 14, 5, "C  +1 px wider, thicker arms"),
    ("04_D_plus2",      15, 6, "D  +2 px wider"),
    ("05_E_plus2_thick", 15, 5, "E  +2 px wider, thicker arms"),
)


def _make_cell_backdrop():
    surf = pygame.Surface((CELL_RAW, CELL_RAW))
    for y in range(CELL_RAW):
        t = y / (CELL_RAW - 1)
        c = int(28 + t * 18)
        pygame.draw.line(surf, (c, c, c + 6), (0, y), (CELL_RAW - 1, y))
    return surf


def _render_cell(fn):
    backdrop = _make_cell_backdrop()
    fn(backdrop)
    return pygame.transform.scale(backdrop, (CELL_W, CELL_H))


def main():
    rendered = []
    # Reference cell #0
    rendered.append(("00_reference", "Original (reference)",
                     _render_cell(render_reference)))

    for name, outer_r, inner_r, label in SIZES:
        z = _render_cell(render_size(outer_r, inner_r))
        rendered.append((name, label, z))
        out_path = os.path.join(OUT_DIR, f"beefy_{name}.png")
        pygame.image.save(z, out_path)
        print(f"saved {out_path}")

    _write_combined_sheet(rendered)


def _write_combined_sheet(rendered):
    cell_label_h = 36
    pad = 16
    margin = 24
    header_h = 56

    cell_full_h = CELL_H + cell_label_h
    cols, rows = 3, 2
    sheet_w = cols * CELL_W + (cols - 1) * pad + 2 * margin
    sheet_h = header_h + rows * cell_full_h + (rows - 1) * pad + 2 * margin

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((22, 22, 28))

    title_font = pygame.font.SysFont(None, 32, bold=True)
    label_font = pygame.font.SysFont(None, 24, bold=True)

    title = title_font.render(
        "Megamagnet beefy — 5 size variants vs original",
        True, (240, 240, 245))
    sheet.blit(title, (margin, margin + 6))

    for i, (name, label, surf) in enumerate(rendered):
        col = i % cols
        row = i // cols
        x = margin + col * (CELL_W + pad)
        y = margin + header_h + row * (cell_full_h + pad)

        pygame.draw.rect(sheet, (40, 40, 50),
                         (x, y, CELL_W, cell_label_h))
        idx = name.split("_", 1)[0]
        if idx == "00":
            badge_col = (180, 200, 230)
            text = f"#0  {label}"
        else:
            badge_col = (250, 220, 130)
            text = f"#{int(idx)}  {label}"
        lbl = label_font.render(text, True, badge_col)
        sheet.blit(lbl, (x + 12, y + 8))
        sheet.blit(surf, (x, y + cell_label_h))

    out_path = os.path.join(OUT_DIR, "beefy_size_variants.png")
    pygame.image.save(sheet, out_path)
    print(f"saved {out_path}")


if __name__ == "__main__":
    main()
