"""POSTMARK — franked ENVELOPE parcel cosmetic.

A vintage postal envelope: a manila slab struck by a bold round rubber-stamp
CANCELLATION mark across the top-right. The inked concentric rings are the
identity — the only "postmarked / in-transit" read in the envelope roster — so
they are drawn as the most legible mark on the sprite, sized so the manila gap
between the two rings survives the downscale. A small perforated red postage
stamp in the opposite corner is the colourblind-safe second anchor.

It is one of the flattest objects in the parcel roster — a slab, not a volume —
carried below Pip rotating with his bank, so the read must survive the rotozoom
at every flight angle on DAY *and* NIGHT sky. The cancellation rings are kept
bold and concentric (no micro-text) so the circle still reads as a postmark at
22px; the body shape stays off the surface edges so the rotozoom never clips its
corners.
"""
import math

import pygame

from game.draw import lerp_color as _lerp_color

# DAY manila / shade plus a NIGHT-friendly warm keyline so the slab still reads
# on a dark sky without changing the sprite per mode.
MANILA_BASE = (217, 185, 126)
MANILA_SHADE = (184, 150,  90)
MANILA_HI = (235, 208, 156)
STAMP_INK = ( 52,  48,  42)     # cancellation ring ink
POSTAGE_RED = (192,  57,  43)
POSTAGE_HI = (222, 120, 108)
OUTLINE = ( 44,  38,  32)       # dark, high-value: reads on day sky
KEYLINE = (236, 210, 158)       # warm rim — the NIGHT lifeline


def build(mode="normal", icon_size: int = 0) -> pygame.Surface:
    # Mode-agnostic: one static slab sprite for every Pip skin.
    S = 44
    surf = pygame.Surface((S, S), pygame.SRCALPHA)

    # Slab body, kept off the edges so the gameplay rotozoom never clips corners.
    BW, BH = 34, 26
    cx, cy = S // 2, S // 2
    rect = pygame.Rect(cx - BW // 2, cy - BH // 2, BW, BH)
    rad = 4

    # Baked outline frame (drawn first, slightly inflated) — the dark silhouette
    # that survives on the bright day sky.
    pygame.draw.rect(surf, OUTLINE, rect.inflate(6, 6), border_radius=rad + 2)

    # Manila body: gentle vertical gradient masked to the rounded rect.
    body = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    for y in range(rect.h):
        t = y / max(1, rect.h - 1)
        row = _lerp_color(MANILA_HI, MANILA_SHADE, t)
        body.fill(row + (255,), pygame.Rect(0, y, rect.w, 1))
    mask = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(),
                     border_radius=rad)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(body, rect.topleft)

    # Envelope flap: a shallow downward V from the top corners to a centred dip,
    # the cue that this slab is a closed envelope and not a plain card. Drawn in
    # OUTLINE (one value step darker than shade) with a deeper apex so the
    # closed-envelope read holds at hard bank instead of washing out.
    apex = (cx, rect.y + 10)
    pygame.draw.lines(surf, OUTLINE, False,
                      [(rect.x + 2, rect.y + 1), apex,
                       (rect.right - 3, rect.y + 1)], 1)

    # Perforated postage stamp — small red square in the BOTTOM-LEFT corner,
    # opposite the cancellation mark. A dark rim reads as the perforated edge and
    # a tiny highlight keeps it from going muddy at true size.
    st = 8
    sx, sy = rect.x + 3, rect.bottom - st - 3
    srect = pygame.Rect(sx, sy, st, st)
    pygame.draw.rect(surf, OUTLINE, srect.inflate(2, 2), border_radius=1)
    pygame.draw.rect(surf, POSTAGE_RED, srect, border_radius=1)
    pygame.draw.rect(surf, POSTAGE_HI, srect, width=1, border_radius=1)
    pygame.draw.circle(surf, POSTAGE_HI, (sx + 3, sy + 3), 1)

    # CANCELLATION STAMP — the identity. A bold round rubber-stamp mark struck
    # across the TOP-RIGHT: two concentric ink rings with a hub and short radial
    # bars, the universal "postmarked" read. Drawn LAST and biggest so it
    # dominates the sprite. No micro-text — bold legible geometry that holds at
    # 22px and under rotation. Inset ~2px off the right edge so a sliver of
    # manila always separates the outer ring from the dark body frame at every
    # bank angle (they fuse on the right when the mark hugs the edge).
    mx, my = rect.right - 11, rect.y + 10
    r_out, r_in = 7, 4
    # A brighter, wider lighter halo pad lifts the manila under the mark so the
    # dark ink rings always sit on a light pad and the concentric read survives
    # the 44->22 downscale rather than smearing into one blob.
    pygame.draw.circle(surf, MANILA_HI, (mx, my), r_out + 2)
    # Two concentric ink rings — the postmark. 1px rings keep the manila gap
    # between them alive; that gap IS the postmark signal.
    pygame.draw.circle(surf, STAMP_INK, (mx, my), r_out, 1)
    pygame.draw.circle(surf, STAMP_INK, (mx, my), r_in, 1)
    # Short radial cancellation bars between the rings, stopping short of the
    # inner ring so the manila gap survives and the mark reads as a strike rather
    # than a solid gear. 1px so they never plug the gap.
    for ang in (90, 270, 0, 180):
        a = math.radians(ang)
        x0 = mx + (r_in + 1.5) * math.cos(a)
        y0 = my - (r_in + 1.5) * math.sin(a)
        x1 = mx + (r_out - 0.5) * math.cos(a)
        y1 = my - (r_out - 0.5) * math.sin(a)
        pygame.draw.line(surf, STAMP_INK, (x0, y0), (x1, y1), 1)
    # Single inked hub pixel — a firm centre that reads at true size without
    # bulking up into a disc that swallows the inner ring's gap.
    pygame.draw.circle(surf, STAMP_INK, (mx, my), 1)

    # Warm keyline rim INSIDE the outline — a glowing edge on night sky that
    # stays subtle against day. Drawn last so it crowns the silhouette.
    pygame.draw.rect(surf, KEYLINE, rect, width=1, border_radius=rad)

    if icon_size:
        return pygame.transform.smoothscale(surf, (icon_size, icon_size))
    return pygame.transform.smoothscale(surf, (22, 22))
