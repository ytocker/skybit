"""
Bespoke engraved center glyphs for the SHAME — Lifetime Lows (Wall of Shame)
medallions, rendered TARNISHED (cracked-pewter anti-trophy).

These follow the single-colour engrave idiom of ``game.achievement_icons``:
each ``_glyph_<id>(surf, cx, cy, r, col)`` lays BOLD filled shapes in the passed
``col`` only — the builder strokes a down-right inset shadow + up-left sheen for
the struck-relief look, so the glyph hard-codes no fills of its own. Authored in
the ~22px legibility floor: nothing thinner than ~3px or smaller than ~5px.

The joke lives in the silhouette (per the v2 LOCKED spec):
  * the_scrooge   — a ``$`` coin draped with cobweb-strands from one corner and
                    a hanging dust-drip: money that gathered dust, never spent.
  * early_checkout — a counter bell rung once + ONE bold down-arrow: "rang and
                    left" — bailed in under 3 seconds.

WRITE-ONLY module: imports ``game`` read-only and never mutates it; the render
harness merges ``GLYPHS`` into a private copy of the badge glyph table.
"""
from __future__ import annotations

import math
import pygame


def _ring_dollar(surf, cx, cy, r, col, rr):
    # The in-game `$` coin read, matching `_glyph_coin`: a bold ring with a
    # struck `$` centred in it. Kept as a helper so the Scrooge coin reuses the
    # exact Riches silhouette — the neglect cue (web/dust), not the coin, is the
    # only thing that distinguishes this from a wealth emblem.
    pygame.draw.circle(surf, col, (cx, cy), rr, max(3, r // 8))
    f = _glyph_font(int(rr * 1.7))
    g = f.render("$", True, col)
    surf.blit(g, g.get_rect(center=(cx, cy)))


def _glyph_the_scrooge(surf, cx, cy, r, col):
    # A `$` coin neglected into dust: the coin sits low-right while a corner
    # spiderweb hangs off its upper-left rim, and a single bead drips off the
    # coin's underside. The web over money is the whole read — "never spent,
    # never taken".
    rr = int(r * 0.50)
    coin_cx = cx + int(r * 0.14)
    coin_cy = cy + int(r * 0.12)
    _ring_dollar(surf, coin_cx, coin_cy, r, col, rr)

    # A TRUE corner cobweb: radial spoke strands fanning out from an anchor on
    # the coin's upper-left rim, crossed by nested concentric arcs. Drawn as open
    # arcs (never a closed polygon) so the rings stay see-through and read as a
    # spiderweb at 44px instead of collapsing into a filled wedge.
    web_w = max(3, r // 10)
    ang0 = math.radians(218)       # anchor toward upper-left, on the coin rim
    ax = coin_cx + math.cos(ang0) * rr
    ay = coin_cy + math.sin(ang0) * rr
    # Three radial spokes fanning into the upper-left quadrant (up, up-left, left)
    # measured from screen +x with y pointing down.
    spoke_angles = (math.radians(248), math.radians(212), math.radians(176))
    spoke_len = r * 0.94
    for a in spoke_angles:
        ex = ax + math.cos(a) * spoke_len
        ey = ay + math.sin(a) * spoke_len
        pygame.draw.line(surf, col, (int(ax), int(ay)), (int(ex), int(ey)), web_w)

    # Three nested concentric arcs spanning the spoke fan — the web's rings. Each
    # is centred on the anchor at a growing radius, so the gaps between rings stay
    # open and the spiderweb reads.
    a_lo = min(spoke_angles)
    a_hi = max(spoke_angles)
    arc_w = max(2, r // 12)
    for frac in (0.40, 0.66, 0.92):
        rad = spoke_len * frac
        rect = pygame.Rect(int(ax - rad), int(ay - rad), int(rad * 2), int(rad * 2))
        # pygame arc angles are CCW from +x; screen y is flipped, so negate the
        # spoke span to make the arc connect the radial strands.
        pygame.draw.arc(surf, col, rect, -a_hi, -a_lo, arc_w)

    # A single dust-drip hanging off the coin's lower edge — the "gathered dust"
    # tick. A short stem + a teardrop bead, bold enough to survive at 44px.
    dx = coin_cx - int(r * 0.10)
    dsy = coin_cy + rr + max(2, r // 12)
    dby = dsy + int(r * 0.30)
    pygame.draw.line(surf, col, (dx, dsy), (dx, dby), max(3, r // 11))
    pygame.draw.circle(surf, col, (dx, dby), max(4, int(r * 0.16)))


def _glyph_early_checkout(surf, cx, cy, r, col):
    # A counter bell rung once, with ONE bold down-arrow beside it: "checked out
    # immediately". The bell is the dome + base plate + a button-cap on top; the
    # down-arrow says "left". Shifted left so the arrow has its own column.
    bx = cx - int(r * 0.22)        # bell centre column

    # Base plate — a flat rounded slab the dome sits on.
    base_w = int(r * 1.04)
    base_h = max(4, int(r * 0.20))
    base_y = cy + int(r * 0.40)
    pygame.draw.rect(surf, col, (bx - base_w // 2, base_y, base_w, base_h),
                     border_radius=max(2, r // 9))

    # Dome — a half-disc seated on the plate. Drawn as a filled circle whose
    # lower half is clipped by the plate, giving a clean bell hump.
    dome_r = int(r * 0.50)
    dome_cy = base_y - int(dome_r * 0.10)
    pygame.draw.circle(surf, col, (bx, dome_cy), dome_r)
    pygame.draw.rect(surf, col, (bx - dome_r, dome_cy, dome_r * 2,
                                 dome_r + base_h), 0)  # square off below centre

    # Button-cap — the strike knob on top of the dome.
    cap_r = max(4, int(r * 0.15))
    pygame.draw.circle(surf, col, (bx, dome_cy - dome_r - cap_r // 2 + 1), cap_r)

    # ONE bold down-arrow to the right — "leaving". A thick shaft + a wide
    # arrowhead, sized to read as a decisive exit, not a tick.
    ax = cx + int(r * 0.62)
    a_top = cy - int(r * 0.46)
    a_tip = cy + int(r * 0.56)
    shaft_w = max(4, int(r * 0.18))
    pygame.draw.line(surf, col, (ax, a_top), (ax, a_tip - int(r * 0.18)), shaft_w)
    head = int(r * 0.30)
    pygame.draw.polygon(surf, col, [
        (ax, a_tip),
        (ax - head, a_tip - head),
        (ax + head, a_tip - head),
    ])


# Font cache for the `$` glyph — mirrors `achievement_icons._glyph_font` so the
# coin face matches the Riches family exactly.
_glyph_fonts: dict = {}


def _glyph_font(px: int):
    f = _glyph_fonts.get(px)
    if f is None:
        f = pygame.font.SysFont(None, px, bold=True)
        _glyph_fonts[px] = f
    return f


GLYPHS = {
    "the_scrooge": _glyph_the_scrooge,
    "early_checkout": _glyph_early_checkout,
}
