"""Umbrella power-up — icon exploration round 2 (converged on bold canopy).

The Umbrella cancels the thunderstorm flap-dampening, so the icon must
read "umbrella / rain protection / keeps me dry" the instant the pickup
flies into view. Each candidate is a self-contained procedural draw:
supersampled at SS then smoothscaled down, matching the lottery/knight
icon family in game/entities.py (3-5 colour palette, thick ink outline,
gentle float-bob baked in).

Round 1's art-director read: the only axis that matters is the LEFT ~48px
real pickup; the enclosing bubble shrinks the umbrella too much at that
size. Round 2 converges every cell onto ONE strong icon — a bold scalloped
TEAL/WHITE open canopy with a J-hook handle, gentle ~15deg tilt, and
rain-deflection droplets peeling off the canopy tips — and demotes the
bubble to a faint accent behind the canopy rather than an enclosing sphere.
Teal (not red) keeps the canopy off the skateboard deck's red.

Five converged cells:
  C1  Teal lead              — THE icon: bold canopy, 15deg, deflect droplets.
  C2  Teal + accent bubble   — faint highlight-arc + thin rim behind canopy.
  C3  Deflected rain (U3)    — teal canopy, droplets pulled tight to the rim.
  C4  Cream badge ring (U5)  — enlarged canopy so it reads as an umbrella.
  C5  Teal colorway alt      — deeper teal + thin gold panel rim.

Each cell shows the icon at the true pickup footprint (POWERUP_R = 14 ->
~48 px) AND a 3x zoom for detail, on a dusk thunderstorm-sky swatch with
faint rain streaks so legibility is judged in context.

Output: docs/umbrella_powerup/round_2.png   (doc-only; not shipped)
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

# ---------------------------------------------------------------------------
# Footprint + palette
# ---------------------------------------------------------------------------
# POWERUP_R = 14 in game/config.py; the visible pickup glyph reads a touch
# wider than the collision radius, so 48 px is the honest on-screen target.
PICKUP_PX = 48
SS = 7                                   # supersample factor (lottery uses 6)

# Canonical float-bob phase so every candidate sits like a real pickup
# rather than dead-centred (matches the sin(pulse*0.8)*2 idiom in-game).
BOB_PULSE = 1.15

INK        = (22, 18, 34)                # thick outer ink, shared family
INK_SOFT   = (46, 40, 64)
CANOPY_RED = (224,  68,  74)
CANOPY_RED_HI = (244, 120, 122)
CANOPY_RED_LO = (176,  40,  48)
CANOPY_CREAM = (250, 244, 222)
CANOPY_TEAL = ( 60, 176, 188)
CANOPY_TEAL_HI = (120, 214, 222)
CANOPY_TEAL_LO = ( 36, 128, 142)
# Deeper teal colorway for the C5 alt; darkest panel sits well below the
# dusk-sky value (top swatch ~ (52,50,78)) so the silhouette holds at night.
CANOPY_TEAL2 = ( 40, 148, 162)
CANOPY_TEAL2_HI = ( 96, 198, 208)
GOLD_RIM   = (240, 206, 110)
HANDLE     = (118,  80,  46)
HANDLE_HI  = (164, 122,  78)
FERRULE    = (246, 222, 120)
DROP_BLUE  = (140, 196, 240)
DROP_BLUE_HI = (208, 236, 252)
BUBBLE_RIM = (210, 236, 250)
BUBBLE_FILL = (180, 214, 240)
SHIELD_AQUA = (150, 222, 232)
PIP_TEAL   = ( 70, 178, 110)
PIP_BELLY  = (236, 226, 140)
PIP_BEAK   = (244, 168,  60)
DRY_SHADOW = (30, 24, 48)


def _lerp(a, b, t):
    return (int(a[0] + (b[0] - a[0]) * t),
            int(a[1] + (b[1] - a[1]) * t),
            int(a[2] + (b[2] - a[2]) * t))


# ---------------------------------------------------------------------------
# Shared canopy builder — a scalloped open umbrella on a supersampled surf.
# Returns nothing; draws into `big` centred on (cx, cy) in SS-space.
# ---------------------------------------------------------------------------
def _canopy(big, cx, cy, span, rise, panels, cols, ink_w,
            ferrule=True, hi_col=None):
    """Open canopy: an arched dome split into `panels` scalloped segments
    that alternate through `cols`. `span` = half-width, `rise` = dome height.
    Scallops drop below the rib line so the hem reads as fabric, not a bowl."""
    n = panels
    hem_y = cy
    # Rib tips along the hem, plus the scalloped dips between them.
    rib_x = [cx - span + (2 * span) * (i / n) for i in range(n + 1)]
    scallop_drop = span * 0.16

    for i in range(n):
        x0, x1 = rib_x[i], rib_x[i + 1]
        xm = (x0 + x1) / 2
        col = cols[i % len(cols)]
        # Dome top follows a circular arc; sample apex of this panel.
        def arc_y(x):
            t = (x - cx) / span                      # -1..1 across the dome
            return cy - rise * max(0.0, math.cos(t * math.pi / 2))
        poly = [
            (x0, hem_y),
            (xm, hem_y + scallop_drop),               # scalloped dip
            (x1, hem_y),
            (x1, arc_y(x1)),
            (xm, arc_y(xm) - rise * 0.05),
            (x0, arc_y(x0)),
        ]
        pygame.draw.polygon(big, col, poly)
        # Per-panel sheen near the apex.
        if hi_col:
            sh = [(x0, arc_y(x0)),
                  (xm, arc_y(xm) - rise * 0.05),
                  (xm, arc_y(xm) + rise * 0.22),
                  (x0, arc_y(x0) + rise * 0.22)]
            pygame.draw.polygon(big, hi_col, sh)
        pygame.draw.polygon(big, INK, poly, ink_w)

    # Apex highlight cap to seat the dome roundness.
    pygame.draw.line(big, INK, (cx - span, hem_y), (cx + span, hem_y), ink_w)

    if ferrule:
        tip_top = cy - rise - span * 0.30
        pygame.draw.line(big, INK, (cx, cy - rise + 2), (cx, tip_top),
                         max(ink_w, int(span * 0.07)))
        pygame.draw.circle(big, FERRULE, (int(cx), int(tip_top)),
                           int(span * 0.085))
        pygame.draw.circle(big, INK, (int(cx), int(tip_top)),
                           int(span * 0.085), ink_w)


def _j_handle(big, cx, top_y, length, span, ink_w, tilt=0.0):
    """Vertical shaft from the canopy apex down to a J-hook crook."""
    shaft_w = max(ink_w, int(span * 0.09))
    bx = cx + math.sin(tilt) * length * 0.4
    by = top_y + length
    pygame.draw.line(big, HANDLE_HI, (cx, top_y), (bx, by), shaft_w + ink_w)
    pygame.draw.line(big, HANDLE, (cx, top_y), (bx, by), shaft_w)
    # J-hook: a small arc curling back up.
    hook_r = span * 0.20
    rect = pygame.Rect(0, 0, int(hook_r * 2), int(hook_r * 2))
    rect.center = (int(bx - hook_r), int(by))
    pygame.draw.arc(big, HANDLE, rect, math.radians(-95), math.radians(180),
                    shaft_w)
    pygame.draw.arc(big, INK, rect, math.radians(-95), math.radians(180),
                    ink_w)
    pygame.draw.line(big, INK, (cx, top_y), (bx, by), ink_w)


def _bubble(big, cx, cy, r, ink_w, drops=True):
    """Translucent soap-bubble sphere with a rim + arc highlight and a
    couple of beading raindrops sliding off it."""
    # Soft fill via a stack of fading rings (cheap radial wash).
    for k in range(6):
        t = k / 5
        rr = int(r * (1 - t * 0.16))
        a = int(60 * (1 - t))
        s = pygame.Surface((rr * 2, rr * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*BUBBLE_FILL, a), (rr, rr), rr)
        big.blit(s, (cx - rr, cy - rr))
    # Rim.
    pygame.draw.circle(big, BUBBLE_RIM, (cx, cy), r, max(ink_w, int(r * 0.05)))
    pygame.draw.circle(big, INK, (cx, cy), r, ink_w)
    # Curved specular highlight, upper-left.
    hr = int(r * 0.74)
    hrect = pygame.Rect(0, 0, hr * 2, hr * 2)
    hrect.center = (cx, cy)
    pygame.draw.arc(big, (255, 255, 255), hrect,
                    math.radians(115), math.radians(168),
                    max(ink_w, int(r * 0.06)))
    # Small round glint.
    pygame.draw.circle(big, (255, 255, 255),
                       (int(cx - r * 0.42), int(cy - r * 0.46)),
                       int(r * 0.10))
    if drops:
        for (ox, oy, dr) in ((0.92, -0.30, 0.14), (0.80, 0.55, 0.10)):
            dx, dy = int(cx + r * ox), int(cy + r * oy)
            ddr = int(r * dr)
            pygame.draw.circle(big, DROP_BLUE, (dx, dy + ddr), ddr)
            pygame.draw.polygon(big, DROP_BLUE,
                                [(dx - ddr, dy + ddr), (dx, dy - ddr),
                                 (dx + ddr, dy + ddr)])
            pygame.draw.circle(big, DROP_BLUE_HI,
                               (dx - ddr // 3, dy + ddr - ddr // 3),
                               max(1, ddr // 3))
            pygame.draw.circle(big, INK, (dx, dy + ddr), ddr, ink_w)


def _accent_bubble(big, cx, cy, r, ink_w):
    """A FAINT bubble *accent* drawn BEHIND the canopy — a thin rim + a
    single specular highlight-arc, no enclosing sphere. Reads as a nod to
    the rain-shield idea without shrinking the umbrella at pickup size."""
    s = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
    sc = r + 2
    # Thin translucent rim only (no solid fill that would dim the canopy).
    pygame.draw.circle(s, (*BUBBLE_RIM, 90), (sc, sc), r, max(ink_w, int(r * 0.04)))
    # Single upper-left highlight-arc — the bubble's tell at a glance.
    hr = int(r * 0.80)
    hrect = pygame.Rect(0, 0, hr * 2, hr * 2)
    hrect.center = (sc, sc)
    pygame.draw.arc(s, (255, 255, 255, 120), hrect,
                    math.radians(112), math.radians(166),
                    max(ink_w, int(r * 0.05)))
    big.blit(s, (cx - sc, cy - sc))


def _tip_droplets(big, cx, cy, span, rise, ink_w, scale):
    """Two short droplet streaks peeling off the LEFT and RIGHT canopy tips,
    anchored TOUCHING the hem corners (not floating away) so the icon reads
    'rain protection', not just 'umbrella'. `scale` = px (SS-space size)."""
    for dirx in (-1, 1):
        hx = cx + dirx * span
        hy = cy
        # Short streak hugging the tip, angled outward + down.
        x0, y0 = hx + dirx * span * 0.04, hy - rise * 0.02
        x1, y1 = hx + dirx * span * 0.34, hy + scale * 0.13
        pygame.draw.line(big, DROP_BLUE_HI, (x0, y0), (x1, y1),
                         max(2, int(SS * 0.6)))
        pygame.draw.line(big, INK, (x0, y0), (x1, y1), ink_w)
        # Bead at the streak's end so it terminates as a drop, not a dash.
        dr = int(scale * 0.05)
        pygame.draw.circle(big, DROP_BLUE, (int(x1), int(y1 + dr)), dr)
        pygame.draw.circle(big, DROP_BLUE_HI,
                           (int(x1 - dr // 3), int(y1 + dr - dr // 3)),
                           max(1, dr // 3))
        pygame.draw.circle(big, INK, (int(x1), int(y1 + dr)), dr, ink_w)


def _raindrop(big, x, y, r, ink_w, col=DROP_BLUE):
    pygame.draw.circle(big, col, (int(x), int(y + r)), int(r))
    pygame.draw.polygon(big, col,
                        [(x - r, y + r), (x, y - r * 1.1), (x + r, y + r)])
    pygame.draw.circle(big, DROP_BLUE_HI,
                       (int(x - r / 3), int(y + r - r / 3)), max(1, int(r / 3)))
    pygame.draw.circle(big, INK, (int(x), int(y + r)), int(r), ink_w)
    pygame.draw.line(big, INK, (x - r, y + r), (x, y - r * 1.1), ink_w)
    pygame.draw.line(big, INK, (x + r, y + r), (x, y - r * 1.1), ink_w)


# ---------------------------------------------------------------------------
# The five candidate icon draws. Each returns a PICKUP_PX-square SRCALPHA
# surface (the icon already smoothscaled to footprint).
# ---------------------------------------------------------------------------
def _finish(big):
    w = big.get_width() // SS
    return pygame.transform.smoothscale(big, (w, w))


def _bold_canopy_icon(teal, teal_hi, panel_rim=None, accent_bubble=False):
    """Shared body for the converged lead — a bold scalloped open canopy
    (~70% icon width) in teal/white with a J-hook handle, deflection
    droplets peeling off both tips, and a gentle ~15deg tilt. Handle +
    canopy + droplets are composed together then rotated as one so the
    J-hook stays inside the 48px bounds.

    `panel_rim` optionally inks each panel edge in a thin gold rim (C5).
    `accent_bubble` draws a faint highlight-arc + thin rim BEHIND the
    canopy (C2) — never an enclosing sphere."""
    px = PICKUP_PX * SS
    big = pygame.Surface((px, px), pygame.SRCALPHA)
    c = px // 2
    ink = max(3, int(SS * 1.05))
    # ~70% icon width => half-width span ~0.35; tame rise keeps the dome bold
    # without crowding the tips after a 15deg tilt.
    span = int(px * 0.35)
    rise = int(px * 0.30)
    uy = c + int(px * 0.06)               # hem a touch low so handle has room

    big2 = pygame.Surface((px, px), pygame.SRCALPHA)
    cc = c
    if accent_bubble:
        # Behind everything, centred near the dome so the arc reads up-left.
        _accent_bubble(big2, cc, uy - int(rise * 0.45),
                       int(px * 0.40), max(2, int(SS * 0.6)))
    _j_handle(big2, cc, uy, int(px * 0.34), span, ink)
    _canopy(big2, cc, uy, span, rise, 6,
            (teal, CANOPY_CREAM), ink, hi_col=teal_hi)
    if panel_rim is not None:
        # Thin gold rim tracing the dome arc, panel by panel.
        n = 6
        for i in range(n + 1):
            t = (i / n) * 2 - 1
            ax = cc - span + (2 * span) * (i / n)
            ay = uy - rise * max(0.0, math.cos(t * math.pi / 2))
            pygame.draw.circle(big2, panel_rim, (int(ax), int(ay)),
                               max(1, int(SS * 0.5)))
    _tip_droplets(big2, cc, uy, span, rise, max(2, int(SS * 0.8)), px)

    rot = pygame.transform.rotate(big2, 15)
    big.blit(rot, rot.get_rect(center=(c, c)))
    return _finish(big)


def icon_c1():
    """C1 — Teal lead: bold canopy, 15deg tilt, deflection droplets. THE icon."""
    return _bold_canopy_icon(CANOPY_TEAL, CANOPY_TEAL_HI)


def icon_c2():
    """C2 — Teal lead + faint accent bubble behind the canopy (not enclosing)."""
    return _bold_canopy_icon(CANOPY_TEAL, CANOPY_TEAL_HI, accent_bubble=True)


def icon_c3():
    """C3 — Umbrella + deflected rain, droplets pulled tight to the rim."""
    px = PICKUP_PX * SS
    big = pygame.Surface((px, px), pygame.SRCALPHA)
    c = px // 2
    ink = max(2, int(SS * 0.85))
    span = int(px * 0.34)
    rise = int(px * 0.28)
    uy = c + int(px * 0.02)
    # Incoming streaks above the dome.
    for fx in (-0.22, 0.06, 0.30):
        x = c + px * fx
        pygame.draw.line(big, DROP_BLUE,
                         (x, c - px * 0.46), (x - px * 0.05, c - px * 0.30),
                         max(2, int(SS * 0.5)))
    _j_handle(big, c, uy, int(px * 0.30), span, ink)
    _canopy(big, c, uy, span, rise, 5,
            (CANOPY_TEAL, CANOPY_CREAM), ink, hi_col=CANOPY_TEAL_HI)
    # Two drops peeling off each hem corner, kept WITHIN ~3px of the rim
    # (~0.06*px at SS) so at 1x they read as deflection, not detached dots.
    near = px * 0.04
    for (hx, hy, dirx) in ((c - span, uy, -1), (c + span, uy, 1)):
        _raindrop(big, hx + dirx * near, hy + px * 0.02,
                  int(px * 0.05), ink)
        _raindrop(big, hx + dirx * (near + px * 0.05), hy + px * 0.07,
                  int(px * 0.04), ink)
        # motion tick hugging the tip
        pygame.draw.line(big, DROP_BLUE_HI,
                         (hx + dirx * px * 0.02, hy - px * 0.02),
                         (hx + dirx * px * 0.06, hy + px * 0.03),
                         max(1, int(SS * 0.35)))
    return _finish(big)


def icon_c4():
    """C4 — Cream badge ring (from U5) but with the umbrella ENLARGED so it
    reads as an umbrella, not 'a thing in a ring'. The teal canopy now fills
    most of the ring; the J-hook handle drops just inside the rim."""
    px = PICKUP_PX * SS
    big = pygame.Surface((px, px), pygame.SRCALPHA)
    c = px // 2
    ink = max(2, int(SS * 0.9))
    # Cream badge ring with a gold edge — a framed-charm read.
    ring_r = int(px * 0.46)
    pygame.draw.circle(big, (250, 238, 206), (c, c), ring_r)
    pygame.draw.circle(big, FERRULE, (c, c), ring_r, max(2, int(SS * 0.7)))
    pygame.draw.circle(big, INK, (c, c), ring_r, ink)
    pygame.draw.circle(big, INK, (c, c), int(ring_r * 0.86),
                       max(1, int(SS * 0.4)))
    # Enlarged canopy filling the upper ring — near the bold-lead proportions
    # so the umbrella is the subject, the ring just a frame.
    span = int(px * 0.34)
    rise = int(px * 0.26)
    uy = c - int(px * 0.02)
    # Handle first so the canopy ink overlaps its top cleanly.
    _j_handle(big, c, uy, int(px * 0.30), span, ink)
    _canopy(big, c, uy, span, rise, 6,
            (CANOPY_TEAL, CANOPY_CREAM), ink, hi_col=CANOPY_TEAL_HI,
            ferrule=True)
    return _finish(big)


def icon_c5():
    """C5 — Teal colorway / contrast alt: the bold lead silhouette in a
    deeper teal with a thin gold rim tracing the panel edges, for users who
    want a touch more pop against bright daytime sky."""
    return _bold_canopy_icon(CANOPY_TEAL2, CANOPY_TEAL2_HI, panel_rim=GOLD_RIM)


CANDIDATES = [
    ("C1", "Teal lead", icon_c1),
    ("C2", "Teal + accent bubble", icon_c2),
    ("C3", "Deflected rain", icon_c3),
    ("C4", "Cream badge ring", icon_c4),
    ("C5", "Deeper teal + gold rim", icon_c5),
]


# ---------------------------------------------------------------------------
# Dusk thunderstorm-sky swatch with faint rain streaks (context backdrop).
# ---------------------------------------------------------------------------
def _storm_swatch(w, h, seed):
    surf = pygame.Surface((w, h))
    top = (52, 50, 78)                  # bruised dusk indigo
    bot = (30, 30, 50)
    for y in range(h):
        surf.fill(_lerp(top, bot, y / max(1, h - 1)), (0, y, w, 1))
    # A muted ground band at the foot so it reads as a sky, not a void.
    pygame.draw.rect(surf, (38, 44, 46), (0, int(h * 0.88), w, h))
    rng = (seed * 2654435761) & 0xFFFFFFFF
    def rnd():
        nonlocal rng
        rng = (1103515245 * rng + 12345) & 0x7FFFFFFF
        return rng / 0x7FFFFFFF
    streaks = pygame.Surface((w, h), pygame.SRCALPHA)
    for _ in range(int(w * h / 900)):
        x = rnd() * w
        y = rnd() * h * 0.9
        ln = 6 + rnd() * 10
        pygame.draw.line(streaks, (190, 205, 235, 42),
                         (x, y), (x - 2, y + ln), 1)
    surf.blit(streaks, (0, 0))
    return surf


def main():
    out_dir = os.path.join(os.path.dirname(THIS_DIR),
                           "docs", "umbrella_powerup")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_2.png")

    # Bake float-bob: shift each finished icon a couple px on its swatch.
    bob = int(round(math.sin(BOB_PULSE * 0.8) * 2))

    cell_w, cell_h = 300, 320
    cols = 5
    pad = 16
    header_h = 84
    footer_h = 34

    sheet_w = pad * 2 + cols * cell_w + (cols - 1) * pad
    sheet_h = header_h + cell_h + footer_h + pad * 2
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((20, 20, 30))

    def font(sz, bold=False):
        return pygame.font.SysFont("Arial", sz, bold=bold)

    title = font(26, bold=True).render(
        "UMBRELLA power-up — icon exploration  (round 2)", True,
        (240, 240, 246))
    sheet.blit(title, (pad, pad))
    sub = font(14).render(
        "Cancels thunderstorm flap-dampening. Each cell: dusk storm sky + "
        "rain streaks. Left = true pickup size (~48 px, POWERUP_R 14, "
        "float-bobbed); right = 3x zoom.",
        True, (170, 178, 192))
    sheet.blit(sub, (pad, pad + 32))
    sub2 = font(13).render(
        "Round 2 — converged on the bold canopy; bubble demoted to accent.",
        True, (150, 175, 205))
    sheet.blit(sub2, (pad, pad + 52))

    for col, (tag, name, fn) in enumerate(CANDIDATES):
        x = pad + col * (cell_w + pad)
        y = header_h + pad
        swatch = _storm_swatch(cell_w, cell_h, seed=col + 3)
        sheet.blit(swatch, (x, y))
        pygame.draw.rect(sheet, (60, 66, 84), (x, y, cell_w, cell_h), 1)

        icon = fn()

        # True pickup size on the upper-left of the cell.
        true_cx = x + cell_w // 2 - PICKUP_PX // 2 - 8
        true_cy = y + cell_h // 2 - PICKUP_PX // 2 + bob
        sheet.blit(icon, (true_cx, true_cy))
        # ring + caption marking the honest footprint
        pygame.draw.circle(sheet, (255, 255, 255),
                           (true_cx + PICKUP_PX // 2,
                            true_cy + PICKUP_PX // 2 - bob),
                           PICKUP_PX // 2 + 4, 1)
        lbl = font(12).render("real pickup ~48px", True, (210, 220, 235))
        sheet.blit(lbl, (x + 10, y + cell_h - 24))

        # 3x zoom lower-right for detail.
        zoom = pygame.transform.smoothscale(icon, (PICKUP_PX * 3,
                                                    PICKUP_PX * 3))
        zx = x + cell_w - PICKUP_PX * 3 - 14
        zy = y + cell_h - PICKUP_PX * 3 - 30
        sheet.blit(zoom, (zx, zy))
        zl = font(12).render("3x zoom", True, (210, 220, 235))
        sheet.blit(zl, (zx + PICKUP_PX * 3 - 48, zy - 2))

        # Caption strip.
        cap = font(16, bold=True).render(f"{tag}  {name}", True,
                                         (245, 240, 230))
        sheet.blit(cap, (x + 8, header_h + pad + cell_h + 6))

    pygame.image.save(sheet, out_path)
    print(f"saved {out_path}  ({sheet_w}x{sheet_h})")


if __name__ == "__main__":
    main()
