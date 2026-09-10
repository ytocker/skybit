"""Tune the copper-coil position on the locked-in 'beefy C' body
(outer_r=14, inner_r=5). Current rendering spans coils as `arm_w + 2`
which makes them protrude past the arm's inner edge into the hollow.
This sheet renders 5 alignment variants for the user to pick from.

Run from repo root:

    python tools/snapshot_megamagnet_coil_align.py

Outputs under docs/screenshots/powerups/megamagnet/:
    align_NN_<name>.png       (5 per-variant cells)
    coil_align_variants.png   (combined 3x2 sheet with reference + 5)
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

# Beefy C body dimensions.
OUTER_R = 14
INNER_R = 5
ARM_W = OUTER_R - INNER_R   # = 9
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

    # The true GEOMETRIC centre of each arm (where the red sits).
    # Note: this is (OUTER_R + INNER_R) / 2 from cx, which for our
    # numbers (14 + 5 = 19) is 9.5 — half-pixel. Round outward so the
    # tip_cx sits within the arm's visible pixel range.
    left_arm_cx = cx - (OUTER_R + INNER_R + 1) // 2     # = cx - 10
    right_arm_cx = cx + (OUTER_R + INNER_R + 1) // 2    # = cx + 10
    # But the existing magnet code uses cx +/- INNER_R +/- ARM_W//2
    # which gives cx +/- 9, NOT 10. Keep that for the chrome tip so
    # the silhouette stays identical to the previous beefy C — only
    # the COIL position varies between alignment variants.
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
    return leg_bot, left_cx, right_cx, left_arm_cx, right_arm_cx


def _draw_coil(surf, cy, left_anchor, right_anchor, half_span):
    """Coil wraps. left_anchor / right_anchor = the x-coord each arm's
    coil cluster is centred on. half_span = how far the bands extend
    left and right of that anchor (so total span = 2*half_span + 1).
    Highlight pixel is centred across the band (symmetric) rather
    than only on the left half as in the legacy code."""
    COPPER_LO = (110, 55, 14)
    COPPER_HI = (220, 130, 55)
    HIGHLIGHT = (255, 225, 160)
    for tip_cx in (left_anchor, right_anchor):
        for i in range(4):
            wy = cy + 2 + i * 3
            left_x = tip_cx - half_span
            right_x = tip_cx + half_span
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
            # Symmetric specular: one bright pixel at the band centre,
            # not a left-biased run that pulls the eye sideways.
            pygame.draw.line(surf, HIGHLIGHT,
                             (mid_x - 1, wy), (mid_x + 1, wy))


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


# Each variant defines:
#   anchor_left  - which x-coord to centre the left arm's coil on
#   anchor_right - which x-coord to centre the right arm's coil on
#   half_span    - half-width of the coil bands (total = 2*half + 1)
def render_align(anchor_pick, half_span):
    """Return a render fn for the given coil alignment.

    anchor_pick = "tip"     -> centre coils on pole tip x (the legacy
                                /broken behaviour: 0.5 px inward of
                                arm centre on each arm).
                  "arm_out" -> centre coils on the true arm centre,
                                rounded OUTWARD (away from hollow).
                  "arm_in"  -> centre coils on the true arm centre,
                                rounded INWARD (toward hollow).
    """
    def _r(cell):
        cx, cy = CELL_RAW // 2, CELL_RAW // 2 - 3
        leg_bot, lcx, rcx, larm, rarm = _draw_body(cell, cx, cy)
        if anchor_pick == "tip":
            anchor_l, anchor_r = lcx, rcx
        elif anchor_pick == "arm_out":
            # outward round = farther from cx
            anchor_l = cx - ((OUTER_R + INNER_R + 1) // 2)
            anchor_r = cx + ((OUTER_R + INNER_R + 1) // 2)
        elif anchor_pick == "arm_in":
            # inward round = closer to cx
            anchor_l = cx - ((OUTER_R + INNER_R) // 2)
            anchor_r = cx + ((OUTER_R + INNER_R) // 2)
        else:
            raise ValueError(anchor_pick)
        _draw_coil(cell, cy, anchor_l, anchor_r, half_span)
        _draw_beefy_arc_and_balls(cell, leg_bot, lcx, rcx)
    return _r


def render_reference(cell):
    cx, cy = CELL_RAW // 2, CELL_RAW // 2 - 3
    p = PowerUp(cx, cy, "magnet")
    p.pulse = PULSE
    p.draw(cell)


# (suffix, anchor, half_span, label)
# arm_w = 9, so:
#   half_span=5  -> 11 px total (legacy: overflows arm by 1px each side)
#   half_span=4  -> 9 px total (matches arm width exactly)
#   half_span=3  -> 7 px total (smaller than arm — inset wraps)
# anchor "tip"     -> cx ± 9  (legacy tip_cx, 0.5px inside arm centre)
#        "arm_out" -> cx ± 10 (true arm centre rounded outward)
VARIANTS = (
    ("01_legacy",      "tip",     5,
     "Legacy (current)"),
    ("02_match_tip",   "tip",     4,
     "Match arm, on tip (-9 / +9)"),
    ("03_match_out",   "arm_out", 4,
     "Match arm, outward (-10 / +10)"),
    ("04_narrow_tip",  "tip",     3,
     "Narrow 7 px, on tip"),
    ("05_narrow_out",  "arm_out", 3,
     "Narrow 7 px, outward"),
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
    rendered = [("00_reference", "Original (reference)",
                 _render_cell(render_reference))]

    for name, anchor, half_span, label in VARIANTS:
        z = _render_cell(render_align(anchor, half_span))
        rendered.append((name, label, z))
        out_path = os.path.join(OUT_DIR, f"align_{name}.png")
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
    label_font = pygame.font.SysFont(None, 22, bold=True)

    title = title_font.render(
        "Megamagnet beefy C — coil alignment variants",
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

    out_path = os.path.join(OUT_DIR, "coil_align_variants.png")
    pygame.image.save(sheet, out_path)
    print(f"saved {out_path}")


if __name__ == "__main__":
    main()
