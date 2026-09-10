"""Render 5 megamagnet icon variants building on the copper-coil
design. Body is thicker than the earlier coil draft (outer_r 14→16,
arm thickness 8→10), and each variant explores a different way to
make the lightning between the pole tips read as massive / really
strong.

Run from repo root:

    python tools/snapshot_megamagnet_coil_strong.py

Outputs under docs/screenshots/powerups/megamagnet/:
    coil_NN_<name>.png       (5 per-variant cells)
    coil_strong_variants.png (combined 3x2 sheet with reference + 5)
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

# Body dimensions — thicker than the earlier coil variant.
VAR_OUTER_R = 16    # was 14 in the previous coil draft (+2)
VAR_INNER_R = 6     # same -> arm thickness grows from 8 to 10


# ── shared body + copper coil primitives ────────────────────────────────────
def _draw_body(surf, cx, cy, *, outer_r=VAR_OUTER_R, inner_r=VAR_INNER_R):
    """Crimson horseshoe at (cx, cy). Returns (leg_bot, lcx, rcx)."""
    arch_cy = cy - 3
    leg_bot = cy + 15

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
        # Beefier chrome pole tips to match the thicker body.
        pygame.draw.rect(surf, (40, 42, 60),
                         (tip_cx - arm_w // 2 - 1, leg_bot - 4, arm_w + 2, 10),
                         border_radius=4)
        pygame.draw.rect(surf, (195, 210, 232),
                         (tip_cx - arm_w // 2, leg_bot - 3, arm_w, 8),
                         border_radius=3)
        pygame.draw.rect(surf, (238, 246, 255),
                         (tip_cx - arm_w // 2 + 1, leg_bot - 3, arm_w - 2, 3),
                         border_radius=2)
    return leg_bot, left_cx, right_cx


def _draw_copper_coil(surf, cy, lcx, rcx):
    """Copper coil wraps on each arm — same pattern as the previous
    coil variant, sized for the thicker arm width (10px)."""
    COPPER_LO = (110, 55, 14)
    COPPER_HI = (220, 130, 55)
    HIGHLIGHT = (255, 225, 160)

    arm_w = VAR_OUTER_R - VAR_INNER_R    # = 10
    for tip_cx in (lcx, rcx):
        for i in range(4):
            wy = cy + 2 + i * 3
            left_x = tip_cx - arm_w // 2 - 1
            right_x = tip_cx + arm_w // 2 + 1
            mid_x = tip_cx
            dip = 1 if (i % 2 == 0) else -1
            pts_shadow = [
                (left_x,  wy + 1),
                (mid_x,   wy + 1 + dip),
                (right_x, wy + 1),
            ]
            pts_main = [
                (left_x,  wy),
                (mid_x,   wy + dip),
                (right_x, wy),
            ]
            pygame.draw.lines(surf, COPPER_LO, False, pts_shadow, 2)
            pygame.draw.lines(surf, COPPER_HI, False, pts_main, 1)
            pygame.draw.line(surf, HIGHLIGHT,
                             (left_x + 1, wy),
                             (mid_x - 1, wy))


def _zigzag_pts(left_cx, right_cx, y0, amp, segments=6, phase=0.0):
    """Build a zig-zag polyline from left tip to right tip."""
    pts = [(left_cx, y0)]
    for i in range(1, segments):
        t = i / segments
        x = int(left_cx + (right_cx - left_cx) * t)
        y = int(y0 + math.sin(phase + i * 1.7) * amp)
        pts.append((x, y))
    pts.append((right_cx, y0))
    return pts


# ── variant draw helpers ────────────────────────────────────────────────────

# #1 BEEFY — thick zigzag arc + big spherical discharge balls at poles.
def _arc_beefy(surf, leg_bot, lcx, rcx):
    y0 = leg_bot + 8
    pts = _zigzag_pts(lcx, rcx, y0, amp=6, segments=6, phase=PULSE * 11)
    # Thick light-blue zigzag with cyan core.
    arc_surf = pygame.Surface((rcx - lcx + 16, 24), pygame.SRCALPHA)
    shifted = [(p[0] - lcx + 8, p[1] - y0 + 8) for p in pts]
    pygame.draw.lines(arc_surf, (110, 195, 255, 230), False, shifted, 5)
    pygame.draw.lines(arc_surf, (220, 240, 255, 255), False, shifted, 2)
    surf.blit(arc_surf, (lcx - 8, y0 - 8))

    # Massive spherical discharge balls at each pole tip.
    for tip_cx in (lcx, rcx):
        ball_cy = leg_bot + 2
        # Outer cyan halo
        glow = pygame.Surface((20, 20), pygame.SRCALPHA)
        for r in (8, 6, 4):
            a = {8: 70, 6: 130, 4: 200}[r]
            pygame.draw.circle(glow, (130, 210, 255, a), (10, 10), r)
        surf.blit(glow, (tip_cx - 10, ball_cy - 10))
        # Yellow + white core
        pygame.draw.circle(surf, (255, 230, 100), (tip_cx, ball_cy), 4)
        pygame.draw.circle(surf, (255, 255, 240), (tip_cx, ball_cy), 2)


# #2 PLASMA — double-layer arc (white core + cyan halo) + glowing orb nodes.
def _arc_plasma(surf, leg_bot, lcx, rcx):
    y0 = leg_bot + 9
    pts = _zigzag_pts(lcx, rcx, y0, amp=5, segments=8, phase=PULSE * 11)
    arc_surf = pygame.Surface((rcx - lcx + 20, 28), pygame.SRCALPHA)
    shifted = [(p[0] - lcx + 10, p[1] - y0 + 10) for p in pts]
    # Plasma layers: outer faint glow, mid cyan, white-hot core.
    pygame.draw.lines(arc_surf, (90, 180, 255, 80), False, shifted, 9)
    pygame.draw.lines(arc_surf, (130, 210, 255, 180), False, shifted, 6)
    pygame.draw.lines(arc_surf, (200, 235, 255, 230), False, shifted, 3)
    pygame.draw.lines(arc_surf, (255, 255, 255, 255), False, shifted, 1)
    surf.blit(arc_surf, (lcx - 10, y0 - 10))

    # Glowing plasma orbs at each pole tip — soft outer halo + bright core.
    for tip_cx in (lcx, rcx):
        ball_cy = leg_bot + 2
        glow = pygame.Surface((22, 22), pygame.SRCALPHA)
        for r in (10, 8, 6, 4):
            a = {10: 50, 8: 90, 6: 150, 4: 220}[r]
            pygame.draw.circle(glow, (140, 220, 255, a), (11, 11), r)
        surf.blit(glow, (tip_cx - 11, ball_cy - 11))
        pygame.draw.circle(surf, (255, 255, 255), (tip_cx, ball_cy), 3)


# #3 BRANCHED — main arc + jagged side-branches + star-sparks at the ends.
def _arc_branched(surf, leg_bot, lcx, rcx):
    y0 = leg_bot + 8
    pts = _zigzag_pts(lcx, rcx, y0, amp=5, segments=7, phase=PULSE * 11)
    arc_surf = pygame.Surface((rcx - lcx + 16, 30), pygame.SRCALPHA)
    shifted = [(p[0] - lcx + 8, p[1] - y0 + 8) for p in pts]
    pygame.draw.lines(arc_surf, (110, 195, 255, 220), False, shifted, 4)
    pygame.draw.lines(arc_surf, (220, 240, 255, 255), False, shifted, 2)

    # 2 jagged side-branches splitting from the main arc at the
    # 1/3 and 2/3 stations, each going up-out into a small spike tree.
    branch_seeds = (
        (shifted[2], (-4, -6), (-7, -10), (-4, -12)),
        (shifted[5], (+4, -6), (+7, -10), (+4, -12)),
    )
    for anchor, *legs in branch_seeds:
        pts_b = [anchor]
        for dx, dy in legs:
            pts_b.append((anchor[0] + dx, anchor[1] + dy))
        pygame.draw.lines(arc_surf, (110, 195, 255, 220), False, pts_b, 3)
        pygame.draw.lines(arc_surf, (220, 240, 255, 255), False, pts_b, 1)
    surf.blit(arc_surf, (lcx - 8, y0 - 8))

    # Star-burst sparks at each pole tip.
    for tip_cx in (lcx, rcx):
        ball_cy = leg_bot + 2
        # Soft halo
        glow = pygame.Surface((18, 18), pygame.SRCALPHA)
        for r in (7, 5):
            a = {7: 70, 5: 140}[r]
            pygame.draw.circle(glow, (140, 220, 255, a), (9, 9), r)
        surf.blit(glow, (tip_cx - 9, ball_cy - 9))
        # 6-arm star
        for k in range(6):
            ang = k * (math.tau / 6)
            ex = int(tip_cx + math.cos(ang) * 5)
            ey = int(ball_cy + math.sin(ang) * 5)
            pygame.draw.line(surf, (255, 245, 200),
                             (tip_cx, ball_cy), (ex, ey), 2)
        pygame.draw.circle(surf, (255, 255, 240), (tip_cx, ball_cy), 2)


# #4 BEAM — solid energy band running directly between two heavy
# anvil-shaped electrodes mounted just below each pole tip.
def _arc_beam(surf, leg_bot, lcx, rcx):
    plate_cy = leg_bot + 6   # electrode centre, below the chrome tip
    plate_half_w = 7

    # Draw the anvil electrodes FIRST so the beam connects across them.
    for tip_cx in (lcx, rcx):
        # Dark frame
        pygame.draw.rect(surf, (40, 42, 60),
                         (tip_cx - plate_half_w - 1, plate_cy - 4,
                          plate_half_w * 2 + 2, 9),
                         border_radius=2)
        # Chrome body
        pygame.draw.rect(surf, (190, 215, 240),
                         (tip_cx - plate_half_w, plate_cy - 3,
                          plate_half_w * 2, 7),
                         border_radius=2)
        # Bright top edge
        pygame.draw.line(surf, (245, 252, 255),
                         (tip_cx - plate_half_w + 1, plate_cy - 3),
                         (tip_cx + plate_half_w - 1, plate_cy - 3))

    # Solid energy beam at electrode centre Y, spanning from the
    # inner edge of the left plate to the inner edge of the right.
    beam_x0 = lcx + plate_half_w
    beam_x1 = rcx - plate_half_w
    beam_w = beam_x1 - beam_x0
    if beam_w > 4:
        band = pygame.Surface((beam_w, 11), pygame.SRCALPHA)
        for dy in range(-4, 5):
            t = abs(dy) / 4.0
            a = int(230 * (1 - t * 0.85))
            col = (140 + int((255 - 140) * (1 - t)),
                   210 + int((255 - 210) * (1 - t)),
                   255,
                   a)
            pygame.draw.line(band, col, (0, 5 + dy), (beam_w - 1, 5 + dy))
        # White-hot core
        pygame.draw.line(band, (255, 255, 255, 255),
                         (0, 5), (beam_w - 1, 5), 1)
        surf.blit(band, (beam_x0, plate_cy - 5))

    # Glow puff at each electrode where the beam fires from.
    for tip_cx in (lcx, rcx):
        glow = pygame.Surface((14, 12), pygame.SRCALPHA)
        for r in (6, 4, 2):
            a = {6: 100, 4: 180, 2: 240}[r]
            pygame.draw.circle(glow, (180, 235, 255, a), (7, 6), r)
        surf.blit(glow, (tip_cx - 7, plate_cy - 6))


# #5 MULTI-ARC — 3 well-separated parallel zigzag arcs + wide
# stepped electrodes.
def _arc_multi(surf, leg_bot, lcx, rcx):
    # Arc-cluster surface tall enough to hold three well-separated arcs.
    arc_h = 26
    arc_surf = pygame.Surface((rcx - lcx + 20, arc_h), pygame.SRCALPHA)
    base_y = 6   # the centre of the cluster within arc_surf
    layers = (
        (-7, 5, PULSE * 11 + 0.0, (180, 230, 255, 240), 2),
        (+0, 6, PULSE * 11 + 1.3, (140, 210, 255, 250), 3),
        (+7, 5, PULSE * 11 + 2.6, (110, 195, 255, 240), 2),
    )
    for y_off, amp, phase, col, thick in layers:
        pts = _zigzag_pts(lcx, rcx, 0, amp=amp, segments=7, phase=phase)
        shifted = [(p[0] - lcx + 10, base_y + y_off + p[1]) for p in pts]
        pygame.draw.lines(arc_surf, col, False, shifted, thick + 1)
        pygame.draw.lines(arc_surf, (240, 250, 255, 255), False, shifted, 1)
    surf.blit(arc_surf, (lcx - 10, leg_bot + 4 - base_y))

    # Big stepped discharge platforms at each pole tip.
    for tip_cx in (lcx, rcx):
        base_cy = leg_bot + 3
        # Outer dark frame — wide
        pygame.draw.rect(surf, (40, 42, 60),
                         (tip_cx - 9, base_cy - 1, 18, 6),
                         border_radius=2)
        # Chrome platform
        pygame.draw.rect(surf, (200, 220, 240),
                         (tip_cx - 8, base_cy - 1, 16, 4),
                         border_radius=2)
        # Bright top edge
        pygame.draw.line(surf, (255, 255, 255),
                         (tip_cx - 7, base_cy - 1),
                         (tip_cx + 7, base_cy - 1))
        # 3 small discharge studs along the platform top
        for sx in (-5, 0, 5):
            pygame.draw.circle(surf, (255, 250, 220),
                               (tip_cx + sx, base_cy + 1), 2)
            pygame.draw.circle(surf, (255, 220, 100),
                               (tip_cx + sx, base_cy + 1), 1)


# ── per-variant cell renderers ──────────────────────────────────────────────

def _render_coil_variant(cell, arc_fn):
    cx, cy = CELL_RAW // 2, CELL_RAW // 2 - 3
    leg_bot, lcx, rcx = _draw_body(cell, cx, cy)
    _draw_copper_coil(cell, cy, lcx, rcx)
    arc_fn(cell, leg_bot, lcx, rcx)


def render_beefy(cell):    _render_coil_variant(cell, _arc_beefy)
def render_plasma(cell):   _render_coil_variant(cell, _arc_plasma)
def render_branched(cell): _render_coil_variant(cell, _arc_branched)
def render_beam(cell):     _render_coil_variant(cell, _arc_beam)
def render_multi(cell):    _render_coil_variant(cell, _arc_multi)


def render_reference(cell):
    """Production magnet for size comparison."""
    cx, cy = CELL_RAW // 2, CELL_RAW // 2 - 3
    p = PowerUp(cx, cy, "magnet")
    p.pulse = PULSE
    p.draw(cell)


VARIANTS = (
    ("00_reference",  render_reference,  "Original"),
    ("01_beefy",      render_beefy,      "Beefy"),
    ("02_plasma",     render_plasma,     "Plasma"),
    ("03_branched",   render_branched,   "Branched"),
    ("04_beam",       render_beam,       "Beam"),
    ("05_multi_arc",  render_multi,      "Multi-arc"),
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
    for name, fn, label in VARIANTS:
        zoomed = _render_cell(fn)
        rendered.append((name, label, zoomed))
        if name != "00_reference":
            out_path = os.path.join(OUT_DIR, f"coil_{name}.png")
            pygame.image.save(zoomed, out_path)
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
    label_font = pygame.font.SysFont(None, 26, bold=True)

    title = title_font.render(
        "Megamagnet — thicker coil body + 5 massive-lightning variants",
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
            text = f"#0  {label}  (reference)"
        else:
            badge_col = (250, 220, 130)
            text = f"#{int(idx)}  {label}"
        lbl = label_font.render(text, True, badge_col)
        sheet.blit(lbl, (x + 12, y + 6))
        sheet.blit(surf, (x, y + cell_label_h))

    out_path = os.path.join(OUT_DIR, "coil_strong_variants.png")
    pygame.image.save(sheet, out_path)
    print(f"saved {out_path}")


if __name__ == "__main__":
    main()
