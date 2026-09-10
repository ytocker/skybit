"""Render 5 megamagnet icon variants + the current production magnet
as a reference. The variants are intentionally close in size to the
original (+1 px arm radius only) — the "stronger" feel comes from
added ornament, not larger silhouettes.

Run from repo root:

    python tools/snapshot_megamagnet_icon_variants.py

Outputs under docs/screenshots/powerups/megamagnet/:
    icon_NN_<name>.png       (5 per-variant cells)
    icon_variants.png        (combined 3x2 sheet with original + 5)
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


CELL_RAW = 80
ZOOM = 3
CELL_W = CELL_RAW * ZOOM
CELL_H = CELL_RAW * ZOOM

# Static pulse phase — mid-discharge for the cyan arc + tip bolts.
PULSE = 1.6

# Body dimensions for variants — only +1 px vs the original
# (outer_r=13). Arm thickness grows from 7 px to 8 px — visible
# without enlarging the silhouette.
VAR_OUTER_R = 14
VAR_INNER_R = 6


def _draw_body(surf, cx, cy, *, outer_r=VAR_OUTER_R, inner_r=VAR_INNER_R,
               body_alpha=255, red_hi=(235, 35, 45),
               highlight_inner=(255, 95, 95),
               highlight_outer=(255, 85, 85)):
    """Crimson horseshoe at (cx, cy). Mirrors _draw_magnet in
    game/entities.py but takes outer_r / inner_r as parameters.
    Returns (leg_bot, left_cx, right_cx)."""
    arch_cy = cy - 3
    leg_bot = cy + 13

    sz = 46
    scx = sz // 2
    scy = outer_r + 4

    scratch = pygame.Surface((sz, sz), pygame.SRCALPHA)
    pygame.draw.circle(scratch, (80, 5, 8), (scx, scy), outer_r + 2)
    pygame.draw.rect(scratch, (80, 5, 8),
                     (scx - outer_r - 2, scy,
                      (outer_r + 2) * 2, leg_bot - arch_cy + 4))
    pygame.draw.circle(scratch, red_hi, (scx, scy), outer_r + 1)
    pygame.draw.rect(scratch, red_hi,
                     (scx - outer_r - 1, scy,
                      (outer_r + 1) * 2, leg_bot - arch_cy + 3))
    pygame.draw.circle(scratch, highlight_inner, (scx, scy), inner_r + 1, 2)
    pygame.draw.circle(scratch, highlight_outer, (scx, scy), outer_r, 2)
    pygame.draw.circle(scratch, (0, 0, 0, 0), (scx, scy), inner_r)
    pygame.draw.rect(scratch, (0, 0, 0, 0),
                     (scx - inner_r, scy, inner_r * 2, sz - scy))

    if body_alpha < 255:
        scratch.set_alpha(body_alpha)
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


def _draw_arc_and_bolts(surf, leg_bot, left_cx, right_cx, pulse,
                        bolt_count=2, arc_thick=2, arc_col=(100, 195, 255, 200)):
    """Cyan arc + per-tip yellow bolts. bolt_count = number of bolts
    per pole tip (default 2 matches the live magnet)."""
    arc_y0 = leg_bot + 6
    arc_pts = [(left_cx, arc_y0)]
    for i in range(1, 6):
        t = i / 6
        x = int(left_cx + (right_cx - left_cx) * t)
        y = int(arc_y0 + math.sin(pulse * 11 + i * 1.7) * 4)
        arc_pts.append((x, y))
    arc_pts.append((right_cx, arc_y0))
    arc_surf = pygame.Surface(
        (right_cx - left_cx + 8, 16), pygame.SRCALPHA)
    shifted = [(p[0] - left_cx + 4, p[1] - arc_y0 + 4) for p in arc_pts]
    if len(shifted) >= 2:
        pygame.draw.lines(arc_surf, arc_col, False, shifted, arc_thick)
    surf.blit(arc_surf, (left_cx - 4, arc_y0 - 4))

    YELLOW = (255, 220, 60)
    WHITE = (255, 250, 220)
    BOLT_TEMPLATES = (
        # (sign-multiplier x ofs list, y ofs list)
        ([0, 4, 1, 5], [0, 2, 4, 6]),     # down-and-outward
        ([1, 4, 2, 6], [-1, 0, 2, 1]),    # sideways
        ([0, 2, -1, 3], [0, -2, -4, -3]), # upward-outward
        ([2, 5, 3, 6], [1, 3, 5, 7]),     # secondary down
    )
    for sign, tip_cx in ((-1, left_cx), (+1, right_cx)):
        tip_y = leg_bot + 1
        for k in range(bolt_count):
            xs, ys = BOLT_TEMPLATES[k % len(BOLT_TEMPLATES)]
            jitter = int(math.sin(pulse * 9 + k * 1.3) * 1)
            pts = [(tip_cx + sign * x, tip_y + y + (jitter if i == 2 else 0))
                   for i, (x, y) in enumerate(zip(xs, ys))]
            pygame.draw.lines(surf, YELLOW, False, pts, 2)
            pygame.draw.lines(surf, WHITE, False, pts, 1)
        pygame.draw.circle(surf, WHITE, (tip_cx, tip_y), 2)
        pygame.draw.circle(surf, YELLOW, (tip_cx, tip_y), 1)


# ── reference: live production magnet sprite ────────────────────────────────
def render_reference(cell):
    cx, cy = CELL_RAW // 2, CELL_RAW // 2 - 2
    p = PowerUp(cx, cy, "magnet")
    p.pulse = PULSE
    p.draw(cell)


# ── #1 Coil — copper wire wrapping the arms ─────────────────────────────────
def render_coil(cell):
    cx, cy = CELL_RAW // 2, CELL_RAW // 2 - 2
    leg_bot, lcx, rcx = _draw_body(cell, cx, cy)

    # Copper coil drawn as a sequence of slightly slanted thin strokes
    # ACROSS the arm width (not wider than the arm) — each stroke is
    # one wrap of wire seen on the front face, alternating in slope
    # to suggest the wire winding from front to back. A darker rim
    # pixel underneath each stroke gives volume.
    COPPER_LO = (110, 55, 14)
    COPPER_HI = (220, 130, 55)
    HIGHLIGHT = (255, 225, 160)

    arm_w = VAR_OUTER_R - VAR_INNER_R
    for tip_cx in (lcx, rcx):
        # 4 wraps spaced 3px apart so the red shows between bands.
        # Each wrap is a 2-segment polyline that dips at the centre,
        # alternating direction to suggest the wire winding from
        # front to back.
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
            pygame.draw.lines(cell, COPPER_LO, False, pts_shadow, 2)
            pygame.draw.lines(cell, COPPER_HI, False, pts_main, 1)
            # Topmost-pixel specular for each wrap.
            pygame.draw.line(cell, HIGHLIGHT,
                             (left_x + 1, wy),
                             (mid_x - 1, wy))

    _draw_arc_and_bolts(cell, leg_bot, lcx, rcx, PULSE)


# ── #2 Crackle — more lightning, brighter arc, arch sparks ──────────────────
def render_crackle(cell):
    cx, cy = CELL_RAW // 2, CELL_RAW // 2 - 2
    leg_bot, lcx, rcx = _draw_body(cell, cx, cy)
    # Thicker, brighter arc + extra bolts per tip.
    _draw_arc_and_bolts(cell, leg_bot, lcx, rcx, PULSE,
                        bolt_count=4, arc_thick=4,
                        arc_col=(170, 235, 255, 240))

    # Two short lightning bolts radiating UP-OUT from the arch
    # shoulders (where the curve meets the legs), not the dead-centre
    # top. Drawn as proper zig-zag polylines, not X marks.
    YELLOW = (255, 220, 60)
    WHITE = (255, 250, 220)
    shoulder_offsets = (
        # (sign-x, anchor-x rel-to-arch-shoulder)
        (-1, -VAR_OUTER_R),
        (+1, +VAR_OUTER_R),
    )
    for sign, ax in shoulder_offsets:
        ay = -VAR_OUTER_R + 5
        bolt = [
            (cx + ax,                cy + ay),
            (cx + ax + sign * 3,     cy + ay - 3),
            (cx + ax + sign * 1,     cy + ay - 5),
            (cx + ax + sign * 4,     cy + ay - 8),
        ]
        pygame.draw.lines(cell, YELLOW, False, bolt, 2)
        pygame.draw.lines(cell, WHITE, False, bolt, 1)
        # Anchor dot on the body's shoulder edge.
        pygame.draw.circle(cell, WHITE, (cx + ax, cy + ay), 1)


# ── #3 Polished — premium chrome polish, gold pole-tip accents ──────────────
def render_polished(cell):
    cx, cy = CELL_RAW // 2, CELL_RAW // 2 - 2
    leg_bot, lcx, rcx = _draw_body(
        cell, cx, cy,
        red_hi=(220, 28, 38),
        highlight_inner=(255, 150, 150),
        highlight_outer=(255, 120, 120))

    # Specular sheen across the arch top — bright but not opaque, so
    # the red identity stays underneath.
    arch_top_y = cy - VAR_OUTER_R
    sheen = pygame.Surface((VAR_OUTER_R * 2 + 4, 4), pygame.SRCALPHA)
    pygame.draw.ellipse(sheen, (255, 220, 220, 140),
                        (0, 0, VAR_OUTER_R * 2 + 4, 4))
    pygame.draw.ellipse(sheen, (255, 245, 245, 170),
                        (2, 0, VAR_OUTER_R * 2, 2))
    cell.blit(sheen, (cx - VAR_OUTER_R - 2, arch_top_y))

    # Gold rim around the bottom of each arm — a thick gold band
    # right above the chrome tip, plus a gold dot accent on the
    # inner pole-tip face.
    GOLD_LO = (160, 110, 25)
    GOLD_HI = (255, 215, 80)
    GOLD_BRIGHT = (255, 240, 160)
    arm_w = VAR_OUTER_R - VAR_INNER_R + 2
    for tip_cx in (lcx, rcx):
        gold_x = tip_cx - arm_w // 2
        pygame.draw.rect(cell, GOLD_LO,
                         (gold_x, leg_bot - 1, arm_w, 4),
                         border_radius=2)
        pygame.draw.rect(cell, GOLD_HI,
                         (gold_x + 1, leg_bot - 1, arm_w - 2, 3),
                         border_radius=1)
        pygame.draw.line(cell, GOLD_BRIGHT,
                         (gold_x + 1, leg_bot - 1),
                         (gold_x + arm_w - 2, leg_bot - 1))

    _draw_arc_and_bolts(cell, leg_bot, lcx, rcx, PULSE)


# ── #4 Field lines — magnetic field arcing OVER the magnet ──────────────────
def render_field_lines(cell):
    cx, cy = CELL_RAW // 2, CELL_RAW // 2 - 2
    leg_bot, lcx, rcx = _draw_body(cell, cx, cy)

    # 2 dashed white-blue field-line arcs going OVER the arch, from
    # near the left pole tip up over the top of the magnet down to
    # the right pole tip. Drawn BEFORE the body so they sit behind
    # the red — but we already drew body, so blit them in front but
    # at low alpha. (Field lines in physics textbooks sit in front
    # too — they're conceptual.)
    FIELD = (220, 240, 255, 145)
    DARK = (100, 140, 200, 130)

    # The arc centre sits at (cx, leg_bot + 1). Ellipse spans from
    # left-tip x to right-tip x, height tall enough to clear the
    # arch top.
    arch_top_y = cy - VAR_OUTER_R - 2
    for i, (xpad, ypad, thick) in enumerate((
            (6, 14, 2),   # outer arc
            (12, 22, 2))):  # bigger outer arc
        w = (rcx - lcx) + xpad * 2
        h = ((leg_bot + 1) - arch_top_y) * 2 + ypad
        ex = cx - w // 2
        ey = (leg_bot + 1) - h // 2
        arc_surf = pygame.Surface((w + 4, h + 4), pygame.SRCALPHA)
        # Dashed arc — draw N short segments around the top half.
        DASHES = 11
        span_start = math.pi  # 180°
        span_end = math.tau   # 360° i.e. 0° — top half going right
        # We want the TOP half of the ellipse only. In pygame.draw.arc
        # angle 0 is right (3 o'clock), pi/2 is up. So the top half
        # is from pi/2 to 3*pi/2... but pygame draws CCW.
        # Use angles from 0.05*pi (right end) to 0.95*pi (left end)
        # — pygame draws CCW from start, so that gives the top half.
        for d in range(DASHES):
            t0 = d / DASHES
            t1 = (d + 0.55) / DASHES
            a0 = math.pi * (0.05 + 0.90 * t0)
            a1 = math.pi * (0.05 + 0.90 * t1)
            pygame.draw.arc(arc_surf, DARK, (2, 2, w, h), a0, a1, thick + 1)
            pygame.draw.arc(arc_surf, FIELD, (2, 2, w, h), a0, a1, thick)
        cell.blit(arc_surf, (ex - 2, ey - 2))

    _draw_arc_and_bolts(cell, leg_bot, lcx, rcx, PULSE)


# ── #5 Chevrons — yellow hazard chevrons painted on the arms ────────────────
def render_chevrons(cell):
    cx, cy = CELL_RAW // 2, CELL_RAW // 2 - 2
    leg_bot, lcx, rcx = _draw_body(cell, cx, cy)

    # 2 chevrons per arm — fewer than v1 so the red still reads
    # between markings.
    HAZARD = (255, 215, 60)
    SHADOW = (90, 50, 0)
    arm_w = VAR_OUTER_R - VAR_INNER_R
    for tip_cx in (lcx, rcx):
        for i in range(2):
            cy_chev = cy + 2 + i * 5
            half = arm_w // 2
            left = (tip_cx - half, cy_chev)
            mid = (tip_cx, cy_chev + 2)
            right = (tip_cx + half, cy_chev)
            pygame.draw.lines(cell, SHADOW, False, [left, mid, right], 3)
            pygame.draw.lines(cell, HAZARD, False, [left, mid, right], 2)

    _draw_arc_and_bolts(cell, leg_bot, lcx, rcx, PULSE)


VARIANTS = (
    ("00_reference",   render_reference,   "Original"),
    ("01_coil",        render_coil,        "Copper coil"),
    ("02_crackle",     render_crackle,     "Heavy crackle"),
    ("03_polished",    render_polished,    "Polished + gold"),
    ("04_field_lines", render_field_lines, "Field lines"),
    ("05_chevrons",    render_chevrons,    "Hazard chevrons"),
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
            out_path = os.path.join(OUT_DIR, f"icon_{name}.png")
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
        "Megamagnet icon — original + 5 design variants",
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

    out_path = os.path.join(OUT_DIR, "icon_variants.png")
    pygame.image.save(sheet, out_path)
    print(f"saved {out_path}")


if __name__ == "__main__":
    main()
