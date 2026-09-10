"""CLOSED-stall front for the lagoon hub — a rolled bamboo blind pulled down over
a shut stall (no awning, no preview dome, no label). Split into its own module
only to keep the change surgical; it is logically part of store_hub and reuses
store_hub's vendored lagoon primitives so a closed hut matches an open hut to the
pixel (same seat/body/roof/footprint — only the front is covered).

Which category groups are shut is store_hub.CLOSED_GROUPS; emptying that set
restores the all-open 7-stall hub, so the full open design is kept for the future.

Pure pygame, both build targets safe (no numpy, no mixer, no docs import). The
import from store_hub below runs lazily (store_hub imports this module inside
_render_static_device, after it is fully loaded), so there is no import cycle.
"""
from __future__ import annotations

import math
import pygame

from game.store_hub import (
    m, vgrad, lerp_color, WHITE, soft_glow,
    STALL_DARK, WOOD_MID, WOOD_LO, WOOD_HI,
    THATCH_LO, THATCH_HI, THATCH_EDGE, DW, DH,
)

# Cool "dormant" veil (the store's locked-chip cool-slate), laid low-alpha over a
# shut FRONT only so closed stalls sit back asleep while the open three pop warm —
# never over the roof/stilts, so the warm village silhouette stays coherent.
DORMANT_TINT = (70, 84, 118)


def _dormant_veil(surf, rect, amount=0.15):
    """A soft cool veil over a closed front so it reads dormant. Kept in the
    12-18% band (cool the plane, not go muddy blue-grey), with a gentle top-down
    deepening so the covered plane also sits a touch darker than the thatch roof
    above it (a closed front must be a DISTINCT covered plane, not merge in)."""
    v = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    a = int(255 * amount)
    for y in range(rect.h):
        t = y / max(1, rect.h - 1)
        aa = int(a * (1.0 + 0.35 * (1.0 - t)))
        v.fill((*DORMANT_TINT, min(255, aa)), (0, y, rect.w, 1))
    surf.blit(v, rect.topleft)


def _contact_shadow(surf, rect, scale, strength=150):
    """A soft dark contact line where the drawn-DOWN blind meets the opening lip,
    so it reads as hung over the opening (not painted flat on the wall): a short
    upward-fading band on the bottom edge + a crisp hairline at the lip."""
    h = max(m(3), int(m(6) * scale))
    band = pygame.Surface((rect.w, h), pygame.SRCALPHA)
    for y in range(h):
        t = y / max(1, h - 1)
        a = int(strength * t ** 1.4)
        band.fill((6, 6, 12, a), (0, y, rect.w, 1))
    surf.blit(band, (rect.left, rect.bottom - h))
    pygame.draw.line(surf, (0, 0, 0, 175), (rect.left, rect.bottom - max(1, m(1))),
                     (rect.right, rect.bottom - max(1, m(1))), max(1, m(1)))


def _shut_interior(surf, cx, body_top, half_w, body_h):
    """Deepen the stall opening to a black shadow box so any gaps in the blind read
    as an unlit, empty interior (nobody home) rather than warm timber."""
    op = pygame.Rect(cx - half_w + m(6), body_top + m(2),
                     half_w * 2 - m(12), body_h - m(4))
    fill = (10, 9, 14)
    surf.blit(vgrad(op.w, op.h, 0, lerp_color(fill, (26, 24, 36), 0.5), fill),
              op.topleft)
    return op


def front_bamboo(surf, cx, body_top, half_w, body_h, deck_y, scale):
    """ROLLED BAMBOO BLIND — a woven reed shade pulled DOWN over the front: stacked
    thin horizontal reed slats (each a lit-top rounded dowel), a heavier bottom
    weight bar, and two side cords. Warm cane, pulled a touch deeper than the
    thatch so the reed plane separates from the straw above it at hub size."""
    _shut_interior(surf, cx, body_top, half_w, body_h)
    bl = pygame.Rect(cx - half_w + m(4), body_top + m(3),
                     half_w * 2 - m(8), body_h - m(8))
    CANE_HI = (200, 158, 96)
    CANE = (156, 116, 64)
    CANE_LO = (104, 72, 36)
    CANE_EDGE = (64, 42, 20)
    # faint back panel so slat gaps read against wood, not pure black
    surf.blit(vgrad(bl.w, bl.h, 0, (52, 38, 24), (28, 20, 12)), bl.topleft)
    slat_h = max(m(4), int(m(6) * scale))
    y = bl.top
    row = 0
    while y < bl.bottom - slat_h:
        r = pygame.Rect(bl.left, y, bl.w, slat_h - max(1, m(1)))
        j = 0.06 * math.sin(row * 1.7)
        top = lerp_color(CANE_HI, CANE, min(1.0, 0.15 + abs(j)))
        surf.blit(vgrad(r.w, r.h, 0, top, CANE_LO), r.topleft)
        pygame.draw.line(surf, lerp_color(CANE_HI, WHITE, 0.30),
                         (r.left, r.top), (r.right, r.top), max(1, m(0.8)))
        # deeper groove between reeds so each reads as a rounded rod, not a stripe
        pygame.draw.line(surf, CANE_EDGE, (r.left, r.bottom),
                         (r.right, r.bottom), max(1, m(1.1)))
        groove = pygame.Surface((r.w, max(1, m(1.6))), pygame.SRCALPHA)
        groove.fill((10, 7, 4, 105))
        surf.blit(groove, (r.left, r.bottom))
        y += slat_h
        row += 1
    # vertical binding cords woven through the reeds (three tracks)
    for fx in (0.22, 0.5, 0.78):
        vx = bl.left + int(bl.w * fx)
        pygame.draw.line(surf, CANE_EDGE, (vx, bl.top), (vx, bl.bottom),
                         max(1, m(1.2)))
        pygame.draw.line(surf, lerp_color(CANE_HI, WHITE, 0.2),
                         (vx - m(1), bl.top), (vx - m(1), bl.bottom), max(1, m(0.6)))
    # heavier bottom weight bar (the "pulled all the way down" tell)
    wb = pygame.Rect(bl.left - m(1), bl.bottom - int(slat_h * 1.4),
                     bl.w + m(2), int(slat_h * 1.4) + m(1))
    wbsh = pygame.Surface((wb.w, m(4)), pygame.SRCALPHA)
    for yy in range(m(4)):
        wbsh.fill((8, 6, 4, int(90 * (1 - yy / m(4)))), (0, yy, wb.w, 1))
    surf.blit(wbsh, (wb.left, wb.top - m(4)))
    surf.blit(vgrad(wb.w, wb.h, m(2), CANE, CANE_EDGE), wb.topleft)
    pygame.draw.line(surf, lerp_color(CANE, WHITE, 0.35),
                     (wb.left, wb.top + m(1)), (wb.right, wb.top + m(1)), max(1, m(1.2)))
    pygame.draw.rect(surf, CANE_EDGE, wb, width=max(1, m(1)), border_radius=m(2))
    # side pull-cords looping down from the eave, with a small toggle knot
    for sx in (bl.left + m(3), bl.right - m(3)):
        pygame.draw.line(surf, (54, 40, 24), (sx, bl.top - m(2)),
                         (sx, bl.bottom + m(4)), max(1, m(1)))
        pygame.draw.circle(surf, CANE_LO, (sx, bl.bottom + m(4)), max(1, m(2)))
    _dormant_veil(surf, bl, 0.15)
    # eave shadow so the blind hangs UNDER the roof
    pygame.draw.line(surf, (0, 0, 0, 150), (bl.left, bl.top),
                     (bl.right, bl.top), max(1, m(1.4)))
    _contact_shadow(surf, bl, scale)


def draw_hut_closed(surf, cx, deck_y, scale):
    """A SHUT hut: identical seat/body/roof/footprint to store_hub.draw_hut, but the
    awning + preview dome + label are replaced by the rolled bamboo blind. No text,
    no preview — the silhouette matches an open hut to the pixel."""
    half_w = int(m(58) * scale)
    body_h = int(m(64) * scale)
    roof_h = int(m(40) * scale)
    eave = int(m(10) * scale)
    body_top = deck_y - body_h
    roof_apex_y = body_top - roof_h

    soft_glow(surf, cx, deck_y, half_w + eave, (0, 0, 0), 110, layers=6)

    body_rect = pygame.Rect(cx - half_w, body_top, half_w * 2, body_h)
    surf.blit(vgrad(body_rect.w, body_rect.h, 0,
                    lerp_color(STALL_DARK, WOOD_MID, 0.25), STALL_DARK),
              body_rect.topleft)
    for px in (body_rect.left, body_rect.right - m(8)):
        pygame.draw.rect(surf, WOOD_LO, (px, body_top, m(8), body_h))
        pygame.draw.line(surf, WOOD_HI, (px + m(1), body_top),
                         (px + m(1), deck_y), max(1, m(1)))

    rl = (cx - half_w - eave, body_top)
    rr = (cx + half_w + eave, body_top)
    apex = (cx, roof_apex_y)
    shs = pygame.Surface((DW, DH), pygame.SRCALPHA)
    pygame.draw.polygon(shs, (0, 0, 0, 80),
                        [(rl[0], rl[1] + m(6)), (rr[0], rr[1] + m(6)),
                         (apex[0], apex[1] + m(6))])
    surf.blit(shs, (0, 0))
    courses = 9
    for i in range(courses):
        t0 = i / courses
        t1 = (i + 1) / courses
        y_lo = body_top - (body_top - roof_apex_y) * t0
        y_hi = body_top - (body_top - roof_apex_y) * t1
        xl0 = rl[0] + (apex[0] - rl[0]) * t0
        xr0 = rr[0] + (apex[0] - rr[0]) * t0
        xl1 = rl[0] + (apex[0] - rl[0]) * t1
        xr1 = rr[0] + (apex[0] - rr[0]) * t1
        col = lerp_color(THATCH_LO, THATCH_HI, 1.0 - t0)
        pygame.draw.polygon(surf, col, [(xl0, y_lo), (xr0, y_lo),
                                        (xr1, y_hi), (xl1, y_hi)])
        fringe_n = 18
        for fdx in range(fringe_n):
            ft = fdx / fringe_n
            fx = xl0 + (xr0 - xl0) * ft
            drop = m(3) * scale * (0.5 + 0.5 * math.sin(fdx * 2.3 + i))
            pygame.draw.line(surf, lerp_color(col, THATCH_EDGE, 0.5),
                             (fx, y_lo), (fx, y_lo + drop), max(1, m(0.8)))
    lit = pygame.Surface((DW, DH), pygame.SRCALPHA)
    pygame.draw.polygon(lit, (*lerp_color(THATCH_HI, WHITE, 0.25), 90),
                        [rl, apex, (cx, body_top)])
    surf.blit(lit, (0, 0))
    pygame.draw.line(surf, THATCH_EDGE, rl, apex, max(1, m(1.6)))
    pygame.draw.line(surf, THATCH_EDGE, rr, apex, max(1, m(1.6)))
    pygame.draw.line(surf, lerp_color(THATCH_HI, WHITE, 0.4),
                     rl, apex, max(1, m(1.0)))
    pygame.draw.circle(surf, THATCH_EDGE, apex, m(4))
    pygame.draw.circle(surf, THATCH_HI, (apex[0] - m(1), apex[1] - m(1)), m(2))

    front_bamboo(surf, cx, body_top, half_w, body_h, deck_y, scale)
