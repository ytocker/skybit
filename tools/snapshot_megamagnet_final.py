"""Final megamagnet icon snapshot. Locks in:

  - body  : beefy C  (outer_r=14, inner_r=5, arm_w=9)
  - coils : legacy width (half_span=5, 11 px total)
            left arm shifted -2 px, right arm shifted +1 px (the user
            requested 1 px more outward on the left to compensate for
            the half-pixel rounding asymmetry in left_cx)
  - arc   : beefy 4 px-thick cyan zigzag
  - poles : yellow-white discharge balls with cyan halos

Side-by-side with the production magnet at the same zoom for size
reference.

Run from repo root:

    python tools/snapshot_megamagnet_final.py

Output: docs/screenshots/powerups/megamagnet/icon_final.png
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
ZOOM = 4
CELL_W = CELL_RAW * ZOOM
CELL_H = CELL_RAW * ZOOM
PULSE = 1.6

OUTER_R = 14
INNER_R = 5
ARM_W = OUTER_R - INNER_R
HALF_SPAN = 5
LEFT_SHIFT = 2     # px to move left-arm coils LEFTward
RIGHT_SHIFT = 1    # px to move right-arm coils RIGHTward
BALL_R = 3
BALL_HALO_R = 7


def _draw_body(surf, cx, cy):
    arch_cy = cy - 3
    leg_bot = cy + 13

    sz = 52
    scx = sz // 2
    scy = OUTER_R + 4

    scratch = pygame.Surface((sz, sz), pygame.SRCALPHA)
    pygame.draw.circle(scratch, (80, 5, 8), (scx, scy), OUTER_R + 2)
    pygame.draw.rect(scratch, (80, 5, 8),
                     (scx - OUTER_R - 2, scy,
                      (OUTER_R + 2) * 2, leg_bot - arch_cy + 4))
    RED_HI = (235, 35, 45)
    pygame.draw.circle(scratch, RED_HI, (scx, scy), OUTER_R + 1)
    pygame.draw.rect(scratch, RED_HI,
                     (scx - OUTER_R - 1, scy,
                      (OUTER_R + 1) * 2, leg_bot - arch_cy + 3))
    pygame.draw.circle(scratch, (255, 95, 95), (scx, scy), INNER_R + 1, 2)
    pygame.draw.circle(scratch, (255, 85, 85), (scx, scy), OUTER_R, 2)
    pygame.draw.circle(scratch, (0, 0, 0, 0), (scx, scy), INNER_R)
    pygame.draw.rect(scratch, (0, 0, 0, 0),
                     (scx - INNER_R, scy, INNER_R * 2, sz - scy))
    surf.blit(scratch, (cx - scx, arch_cy - scy))

    left_cx = cx - INNER_R - ARM_W // 2
    right_cx = cx + INNER_R + ARM_W // 2
    for tip_cx in (left_cx, right_cx):
        pygame.draw.rect(surf, (40, 42, 60),
                         (tip_cx - ARM_W // 2 - 1, leg_bot - 4,
                          ARM_W + 2, 9), border_radius=4)
        pygame.draw.rect(surf, (195, 210, 232),
                         (tip_cx - ARM_W // 2, leg_bot - 3,
                          ARM_W, 7), border_radius=3)
        pygame.draw.rect(surf, (238, 246, 255),
                         (tip_cx - ARM_W // 2 + 1, leg_bot - 3,
                          ARM_W - 2, 3), border_radius=2)
    return leg_bot, left_cx, right_cx


def _draw_coil(surf, cy, left_anchor, right_anchor):
    COPPER_LO = (110, 55, 14)
    COPPER_HI = (220, 130, 55)
    HIGHLIGHT = (255, 225, 160)
    for tip_cx in (left_anchor, right_anchor):
        for i in range(4):
            wy = cy + 2 + i * 3
            left_x = tip_cx - HALF_SPAN
            right_x = tip_cx + HALF_SPAN
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
    y0 = leg_bot + 7
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


def render_final(cell):
    cx, cy = CELL_RAW // 2, CELL_RAW // 2 - 3
    leg_bot, lcx, rcx = _draw_body(cell, cx, cy)
    _draw_coil(cell, cy,
               left_anchor=lcx - LEFT_SHIFT,
               right_anchor=rcx + RIGHT_SHIFT)
    _draw_beefy_arc_and_balls(cell, leg_bot, lcx, rcx)


def render_reference(cell):
    cx, cy = CELL_RAW // 2, CELL_RAW // 2 - 3
    p = PowerUp(cx, cy, "magnet")
    p.pulse = PULSE
    p.draw(cell)


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
    ref = _render_cell(render_reference)
    final = _render_cell(render_final)

    cell_label_h = 44
    pad = 24
    margin = 30
    header_h = 60

    sheet_w = 2 * CELL_W + pad + 2 * margin
    sheet_h = header_h + cell_label_h + CELL_H + 2 * margin

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((22, 22, 28))

    title_font = pygame.font.SysFont(None, 36, bold=True)
    label_font = pygame.font.SysFont(None, 28, bold=True)

    title = title_font.render(
        "Megamagnet — final calibration", True, (240, 240, 245))
    sheet.blit(title, (margin, margin + 6))
    sub_font = pygame.font.SysFont(None, 22, bold=False)
    sub = sub_font.render(
        f"beefy C body  ·  coil shift: left −{LEFT_SHIFT} px, "
        f"right +{RIGHT_SHIFT} px",
        True, (190, 195, 210))
    sheet.blit(sub, (margin, margin + 36))

    for col, (label, surf) in enumerate((
            ("Original (reference)", ref),
            ("Megamagnet (final)",   final))):
        x = margin + col * (CELL_W + pad)
        y = margin + header_h
        pygame.draw.rect(sheet, (40, 40, 50), (x, y, CELL_W, cell_label_h))
        col_text = (180, 200, 230) if col == 0 else (250, 220, 130)
        lbl = label_font.render(label, True, col_text)
        sheet.blit(lbl, (x + 16, y + 10))
        sheet.blit(surf, (x, y + cell_label_h))

    out_path = os.path.join(OUT_DIR, "icon_final.png")
    pygame.image.save(sheet, out_path)
    print(f"saved {out_path}")


if __name__ == "__main__":
    main()
