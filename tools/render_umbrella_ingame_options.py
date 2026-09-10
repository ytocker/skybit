"""Umbrella power-up — in-gameplay overlay exploration (round 2).

The umbrella cancels the thunderstorm flap-dampening; while it is active a
small umbrella floats above Pip's head. The chosen pickup ICON is C4 (cream
badge ring) from `render_umbrella_icon_options.py` — the umbrella INSIDE that
ring is a teal/white scalloped canopy + J-hook handle. The in-gameplay
umbrella must read as the SAME umbrella so the player connects pickup ->
buff: same teal/white canopy, ink outline, ferrule, handle. The cream/gold
ring was pickup FRAMING only, so it is deliberately absent here.

Two behaviours this sheet must prove:
  - The umbrella sits ON TOP of Pip's head and stays UPRIGHT (or at a fixed
    per-variant lean) while Pip's body tilts as he flaps/dives — exactly the
    helmet-overlay precedent (`Bird._draw_helmet`): the rotating bird is
    drawn first, the overlay is composed upright on top afterwards.
  - It is a night thunderstorm event, so every cell sits on a dark storm sky
    with faint rain streaks.

We reuse the icon's `_canopy`, `_j_handle`, and the teal/white/ink/ferrule
palette so the in-game umbrella is pixel-consistent with the chosen icon —
no second source of truth for the umbrella look.

Each of the 5 variants is shown across 3 representative Pip poses
(+25deg rising, 0deg level, -25deg diving) so the reviewer can see the
umbrella holding its angle while Pip rotates underneath it.

Round 2 (art-director: V5 lead, V1 fallback): canopy teal lightened ~12%
off the navy sky, ink outline thickened + right rim explicitly closed,
ferrule on V5/V1, fewer/bolder scallops, V2 upright (no lean), V3 droplets
cut + shrunk to V1 size, V4 canopy +20% lifted, V5 J-hook offset outboard
so it clears the wing. The umbrella angle is fixed per-variant and NEVER
follows Pip's tilt.

Output: docs/umbrella_powerup/ingame_round_2.png   (doc-only; not shipped)
"""
from __future__ import annotations

import math
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(THIS_DIR))

pygame.init()
pygame.display.set_mode((1, 1))

from game import parrot
# Reuse the chosen icon's exact umbrella geometry + palette so the
# in-gameplay umbrella matches pickup C4 pixel-for-pixel.
from tools.render_umbrella_icon_options import (
    _canopy, _j_handle,
    CANOPY_TEAL as _ICON_TEAL, CANOPY_TEAL_HI as _ICON_TEAL_HI, CANOPY_CREAM,
    INK, FERRULE, DROP_BLUE, DROP_BLUE_HI,
    _lerp,
)

# Against the deep night-storm indigo (top ~ (26,28,50)) the icon's dusk-tuned
# teal drifts navy and the canopy fuses with the sky. Lift the SAME hue ~12%
# in value/chroma so the dome separates at gameplay scale; the icon stays the
# source of truth for the shape, this is a night-legibility nudge only.
def _brighten(c, f):
    return tuple(min(255, int(round(v + (255 - v) * f))) for v in c)


CANOPY_TEAL = _brighten(_ICON_TEAL, 0.12)        # ~ (84,185,196)
CANOPY_TEAL_HI = _brighten(_ICON_TEAL_HI, 0.12)  # ~ (136,219,226)

# Supersample the umbrella overlay then smoothscale down so the ink outline
# and scallops stay crisp at the small on-head footprint (same idiom the icon
# tool uses for the pickup glyph).
SS = 6

# Pip sprite metrics (parrot.SPRITE_W/H = 64x60). The head crown sits high in
# the sprite — the head ellipse is centred ~21px from the sprite top, i.e.
# ~9px above the sprite centre; its top edge is ~25px above centre. The
# umbrella hem is anchored just above that crown.
HEAD_CROWN_DX = 15                      # px right of parrot centre (head is
                                        # offset toward Pip's face — sprite
                                        # head ellipse centred at (47, 21),
                                        # sprite centre (32, 30) → +15, −9 →
                                        # crown ~−18 above centre)
HEAD_CROWN_DY = -18                     # px above parrot centre


def _make_umbrella(head_span, *, rise_scale=0.62, panels=5,
                   handle_len=0.0, handle_dx=0.0, lean_deg=0.0, ferrule=True,
                   deflect_drops=False):
    """Build one upright (or fixed-lean) umbrella overlay surface sized to
    `head_span` px of half-width, reusing the icon's canopy/handle so it
    matches the chosen pickup. Returns the smoothscaled SRCALPHA surface and
    the (x, y) of the canopy hem-centre within that surface, so the caller can
    seat the hem precisely on Pip's crown regardless of handle length.

    `handle_len` is the J-hook shaft length as a fraction of span (0 = none).
    `handle_dx` shifts the handle OUTBOARD (fraction of span) from the canopy
    apex so the J-hook clears Pip's wing — the canopy stays centred on the
    crown. `lean_deg` is a FIXED tilt applied to the whole umbrella — it never
    tracks Pip's pose. `deflect_drops` adds a couple of raindrops splitting off
    the rim (the rain-protection tell). Default `panels=5`: fewer, bolder
    scallops read better than 6 at the on-head footprint."""
    span = int(head_span * SS)
    rise = int(span * rise_scale)
    # Thicker outline than round 1 (was ~1.05*SS) so the ink survives the
    # downscale and the rim stays continuous at gameplay scale.
    ink = max(3, int(SS * 1.5))

    # Generous canvas: room above for the ferrule, below for any handle, and
    # margin on the sides for the lean rotation + deflection drops.
    handle_px = int(span * handle_len)
    margin = int(span * 0.6)
    w = span * 2 + margin * 2
    h = rise + int(span * 0.5) + handle_px + margin * 2
    big = pygame.Surface((w, h), pygame.SRCALPHA)

    # Hem centre placed so the dome + ferrule fit above and the handle hangs
    # below within the canvas.
    cx = w // 2
    hem_y = margin + rise + int(span * 0.30)

    if handle_len > 0:
        # The shaft anchors at the apex but is shifted OUTBOARD by handle_dx so
        # the J-hook hangs beside Pip's body, never crossing the wing. It is
        # drawn straight down (tilt=0): the handle is vertical and does NOT
        # rotate with any per-variant lean below.
        _j_handle(big, cx + int(span * handle_dx), hem_y, handle_px, span, ink)
    _canopy(big, cx, hem_y, span, rise, panels,
            (CANOPY_TEAL, CANOPY_CREAM), ink,
            ferrule=ferrule, hi_col=CANOPY_TEAL_HI)

    # Re-ink the dome arc + hem on top of the panels so the outline reads as
    # one continuous bold rim — at gameplay scale the per-panel ink was
    # breaking up, especially on the RIGHT rim. Trace the same circular arc the
    # canopy uses (cos falloff across the span) and close both end ribs.
    rim_pts = []
    steps = 48
    for k in range(steps + 1):
        t = (k / steps) * 2 - 1                       # -1..1 across the dome
        ax = cx - span + (2 * span) * (k / steps)
        ay = hem_y - rise * max(0.0, math.cos(t * math.pi / 2))
        rim_pts.append((ax, ay))
    pygame.draw.lines(big, INK, False, rim_pts, ink)
    pygame.draw.line(big, INK, (cx - span, hem_y), (cx + span, hem_y), ink)
    pygame.draw.line(big, INK, (cx - span, hem_y),
                     (cx - span, hem_y - rise * 0.04), ink)
    pygame.draw.line(big, INK, (cx + span, hem_y),
                     (cx + span, hem_y - rise * 0.04), ink)

    if deflect_drops:
        # A few drops peeling off both hem corners + sliding down the dome,
        # so the bigger shelter reads as actively shedding rain.
        for dirx in (-1, 1):
            hx = cx + dirx * span
            for k, (ox, oy, dr) in enumerate(
                    ((0.10, 0.16, 0.10), (0.30, 0.42, 0.08))):
                dx = int(hx + dirx * span * ox)
                dy = int(hem_y + span * oy)
                rr = int(span * dr)
                pygame.draw.circle(big, DROP_BLUE, (dx, dy + rr), rr)
                pygame.draw.polygon(big, DROP_BLUE,
                                    [(dx - rr, dy + rr), (dx, dy - rr),
                                     (dx + rr, dy + rr)])
                pygame.draw.circle(big, DROP_BLUE_HI,
                                   (dx - rr // 3, dy + rr - rr // 3),
                                   max(1, rr // 3))
                pygame.draw.circle(big, INK, (dx, dy + rr), rr, ink)

    # Downscale to on-screen size first, then apply the FIXED lean. The hem
    # anchor is tracked through both transforms so the caller seats it right.
    sw, sh = w // SS, h // SS
    small = pygame.transform.smoothscale(big, (sw, sh))
    hem = (cx / SS, hem_y / SS)

    if lean_deg:
        rotated = pygame.transform.rotate(small, lean_deg)
        # rotate pivots about the surface centre; recompute where the hem
        # landed so the umbrella still seats correctly after the lean.
        scx, scy = sw / 2, sh / 2
        rel_x, rel_y = hem[0] - scx, hem[1] - scy
        a = math.radians(-lean_deg)               # pygame rotates CCW for +deg
        rx = rel_x * math.cos(a) - rel_y * math.sin(a)
        ry = rel_x * math.sin(a) + rel_y * math.cos(a)
        rw, rh = rotated.get_size()
        hem = (rw / 2 + rx, rh / 2 + ry)
        small = rotated

    return small, hem


# ---------------------------------------------------------------------------
# Five variants. Each is a builder returning (surface, hem_anchor) plus the
# vertical gap (in px) to float the hem above Pip's head crown.
# ---------------------------------------------------------------------------
def w1_v4_baseline(head_span):
    """W1 — V4 baseline (+20% width): reference for the wider set so the
    chosen direction is visible alongside the new widenings."""
    surf, hem = _make_umbrella(int(head_span * 1.20), rise_scale=0.62,
                               panels=5, handle_len=0.0, lean_deg=0.0,
                               ferrule=True)
    return surf, hem, 7


def w2_wider(head_span):
    """W2 — +40% width. Mild widening over V4; reads as a roomier hat."""
    surf, hem = _make_umbrella(int(head_span * 1.40), rise_scale=0.62,
                               panels=5, handle_len=0.0, lean_deg=0.0,
                               ferrule=True)
    return surf, hem, 7


def w2b_fifty(head_span):
    """W2b — +50% width. The midpoint the user asked to see between W2
    (+40%) and W3 (+60%)."""
    surf, hem = _make_umbrella(int(head_span * 1.50), rise_scale=0.62,
                               panels=5, handle_len=0.0, lean_deg=0.0,
                               ferrule=True)
    return surf, hem, 7


def w3_shelter(head_span):
    """W3 — +60% width. Starts to read as a clear shelter covering Pip's
    head & shoulders, but still leaves silhouette legible."""
    surf, hem = _make_umbrella(int(head_span * 1.60), rise_scale=0.62,
                               panels=5, handle_len=0.0, lean_deg=0.0,
                               ferrule=True)
    return surf, hem, 8


def w4_wide_shelter(head_span):
    """W4 — +80% width. Strong shelter read; canopy now visibly extends
    past Pip's wings on either side."""
    surf, hem = _make_umbrella(int(head_span * 1.80), rise_scale=0.62,
                               panels=6, handle_len=0.0, lean_deg=0.0,
                               ferrule=True)
    return surf, hem, 8


def w5_max_wide(head_span):
    """W5 — +100% width (double V4 baseline width-factor). Maximum
    shelter read — beyond this it crowds the playfield."""
    surf, hem = _make_umbrella(int(head_span * 2.00), rise_scale=0.60,
                               panels=6, handle_len=0.0, lean_deg=0.0,
                               ferrule=True)
    return surf, hem, 9


def v1_canopy_straight(head_span):
    """V1 — Canopy only, upright (legible fallback): clean teal canopy ~1.0x
    head-span, no handle, 0deg, ferrule on, bolder 5-scallop hem, floating a
    touch above the crown."""
    surf, hem = _make_umbrella(head_span, panels=5, handle_len=0.0,
                               lean_deg=0.0, ferrule=True)
    return surf, hem, 6


def v2_short_handle(head_span):
    """V2 — Short-handle upright: V5's shape with a stub J-hook. Upright (the
    old 10deg lean is gone — upright is a hard requirement). Handle offset
    outboard so it clears the wing."""
    surf, hem = _make_umbrella(head_span, panels=5, handle_len=0.30,
                               handle_dx=0.32, lean_deg=0.0, ferrule=True)
    return surf, hem, 6


def v3_canopy_clean(head_span):
    """V3 — V1-sized canopy, no droplets (deflection drops cut per AD). Reads
    as a clean shelter sitting clear above the crown."""
    surf, hem = _make_umbrella(head_span, panels=5, handle_len=0.0,
                               lean_deg=0.0, ferrule=True, deflect_drops=False)
    return surf, hem, 7


def v4_lifted_canopy(head_span):
    """V4 — Canopy +20% lifted: a larger dome floated ~7px above the crown so
    it reads as a shelter, not a cap. No handle."""
    surf, hem = _make_umbrella(int(head_span * 1.20), rise_scale=0.62,
                               panels=5, handle_len=0.0, lean_deg=0.0,
                               ferrule=True)
    return surf, hem, 7


def v5_full_handle(head_span):
    """V5 — Full handle (lead, literal icon match): canopy + full visible
    J-hook running down beside the body, upright, ferrule on. The handle is
    offset outboard so it never overlaps the wing at any tilt, and stays
    vertical (it does not rotate)."""
    surf, hem = _make_umbrella(head_span, panels=5, handle_len=0.62,
                               handle_dx=0.40, lean_deg=0.0, ferrule=True)
    return surf, hem, 6


VARIANTS = [
    ("W2",  "Wider (+40%)",        w2_wider),
    ("W2b", "Fifty (+50%)",        w2b_fifty),
    ("W3",  "Shelter (+60%)",      w3_shelter),
]

POSES = [(+25.0, "rising"), (0.0, "level"), (-25.0, "diving")]


# ---------------------------------------------------------------------------
# Night thunderstorm-sky swatch with faint rain streaks (per-cell backdrop).
# Darker than the icon tool's dusk swatch since the umbrella event is night.
# ---------------------------------------------------------------------------
def _night_storm(w, h, seed):
    surf = pygame.Surface((w, h))
    top = (26, 28, 50)                  # deep night indigo
    bot = (12, 14, 28)
    for y in range(h):
        surf.fill(_lerp(top, bot, y / max(1, h - 1)), (0, y, w, 1))
    rng = (seed * 2654435761) & 0xFFFFFFFF

    def rnd():
        nonlocal rng
        rng = (1103515245 * rng + 12345) & 0x7FFFFFFF
        return rng / 0x7FFFFFFF

    streaks = pygame.Surface((w, h), pygame.SRCALPHA)
    for _ in range(int(w * h / 520)):
        x = rnd() * w
        y = rnd() * h
        ln = 8 + rnd() * 14
        pygame.draw.line(streaks, (180, 198, 235, 50),
                         (x, y), (x - 3, y + ln), 1)
    surf.blit(streaks, (0, 0))
    return surf


def _draw_cell(sheet, x, y, cw, ch, build_fn, tilt_deg, seed):
    """Pip at `tilt_deg` with the variant umbrella seated upright on his
    crown, over a night-storm swatch."""
    swatch = _night_storm(cw, ch, seed)
    sheet.blit(swatch, (x, y))
    pygame.draw.rect(sheet, (54, 60, 84), (x, y, cw, ch), 1)

    cx = x + cw // 2
    cy = y + ch // 2 + 6                 # bias down so umbrella has headroom

    # Gentle idle bob baked in so Pip + umbrella read as a live, hovering
    # pickup state rather than pinned dead-centre.
    bob = int(round(math.sin(seed * 0.9) * 3))
    cy += bob

    # Pip first — rotated by his pose tilt (the umbrella must NOT inherit this).
    pip = parrot.get_parrot(0, tilt_deg)
    pr = pip.get_rect(center=(cx, cy))
    sheet.blit(pip, pr.topleft)

    # The head crown rides with Pip's rotation. The head sprite sits OFFSET
    # from the body centre (Pip's face is to the right at +15 px, crown at
    # −18 px), so the crown's world position must rotate that full 2D offset
    # by the tilt — not just (0, dy). Without the x term the umbrella drifts
    # off Pip's head whenever he tilts (he dives forward, his head moves
    # right and down, but the umbrella stayed at the body's centre+dy).
    # pygame rotozoom rotates CCW for +deg; screen y-down convention.
    a = math.radians(tilt_deg)
    cosA, sinA = math.cos(a), math.sin(a)
    hx, hy = HEAD_CROWN_DX, HEAD_CROWN_DY
    crown_dx = hx * cosA + hy * sinA
    crown_dy = -hx * sinA + hy * cosA
    crown_x = cx + crown_dx
    crown_y = cy + crown_dy

    # Build the umbrella sized to Pip's head half-span (~head ellipse rx 12).
    surf, hem, gap = build_fn(20)
    hem_x, hem_y = hem
    # Seat the hem `gap` px above the crown; blit so the hem anchor lands there.
    target_x = crown_x
    target_y = crown_y - gap
    blit_x = int(target_x - hem_x)
    blit_y = int(target_y - hem_y)
    sheet.blit(surf, (blit_x, blit_y))


def main():
    out_dir = os.path.join(os.path.dirname(THIS_DIR),
                           "docs", "umbrella_powerup")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "ingame_round_3b_fifty.png")

    def font(sz, bold=False):
        return pygame.font.SysFont("Arial", sz, bold=bold)

    cell_w, cell_h = 200, 200
    pad = 14
    header_h = 78
    row_label_w = 150            # left gutter for V-labels
    col_label_h = 26             # pose labels above the grid

    n_rows = len(VARIANTS)
    n_cols = len(POSES)

    grid_x0 = pad + row_label_w
    grid_y0 = header_h + col_label_h

    sheet_w = grid_x0 + n_cols * cell_w + (n_cols - 1) * pad + pad
    sheet_h = grid_y0 + n_rows * cell_h + (n_rows - 1) * pad + pad
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((18, 18, 28))

    title = font(24, bold=True).render(
        "UMBRELLA in-gameplay — +50% (W2b) between W2 (+40%) and W3 (+60%)",
        True, (240, 240, 248))
    sheet.blit(title, (pad, pad))
    sub = font(14).render(
        "+40% / +50% / +60% widths side-by-side over the V4 canopy. "
        "Umbrella tracks Pip's head crown — stays above the head as he tilts.",
        True, (172, 182, 200))
    sheet.blit(sub, (pad, pad + 30))
    sub2 = font(13).render(
        "All upright, no handle (V4 style). Cols = pose "
        "(rising +25 / level 0 / diving -25).",
        True, (150, 175, 205))
    sheet.blit(sub2, (pad, pad + 50))

    # Column (pose) labels above the grid.
    for col, (_tilt, pose_name) in enumerate(POSES):
        cx = grid_x0 + col * (cell_w + pad)
        lbl = font(15, bold=True).render(pose_name, True, (210, 220, 236))
        sheet.blit(lbl, (cx + cell_w // 2 - lbl.get_width() // 2,
                         grid_y0 - col_label_h + 4))

    seed = 3
    for row, (tag, name, build_fn) in enumerate(VARIANTS):
        gy = grid_y0 + row * (cell_h + pad)
        # Row (variant) label in the left gutter.
        tag_lbl = font(18, bold=True).render(tag, True, (250, 244, 230))
        sheet.blit(tag_lbl, (pad, gy + cell_h // 2 - 24))
        # Wrap the name across up to two lines in the gutter.
        words = name.split(" ")
        line, lines = "", []
        for wd in words:
            trial = (line + " " + wd).strip()
            if font(13).size(trial)[0] > row_label_w - 8 and line:
                lines.append(line)
                line = wd
            else:
                line = trial
        if line:
            lines.append(line)
        for i, ln in enumerate(lines):
            nlbl = font(13).render(ln, True, (200, 208, 224))
            sheet.blit(nlbl, (pad, gy + cell_h // 2 + i * 16))

        for col, (tilt, _pose) in enumerate(POSES):
            gx = grid_x0 + col * (cell_w + pad)
            _draw_cell(sheet, gx, gy, cell_w, cell_h, build_fn, tilt,
                       seed)
            seed += 1

    pygame.image.save(sheet, out_path)
    print(f"saved {out_path}  ({sheet_w}x{sheet_h})")


if __name__ == "__main__":
    main()
