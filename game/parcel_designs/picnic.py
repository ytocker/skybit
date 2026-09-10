"""PICNIC BASKET parcel cosmetic (MID tier).

A wicker picnic basket: a wide rounded BASKET body, a single tall HANDLE
arch springing from the rim with an open SKY-HOLE under it, and a red-check
CLOTH bulge spilling over the rim. At 22px the read is the combined glyph —
one clean handle arch over a fat rounded body with a bright check lump
breaking the rim line. Weave is suggested with ≤3 horizontal hatch lines
(fine wicker dies at this size); the silhouette + one warm body colour +
the bold red/cream check carry it.

The handle is the rotation-survival anchor: ONE bold dark-keylined arch with
a clear hole beneath it, so the basket still reads as a basket banked from
−25° to 90°. The check is the picnic tell — deliberately blocky, SATURATED,
dark-enough red squares so it survives both the smoothscale AND grayscale,
where a fine grid or a pastel red would collapse to a smudge.
"""
import pygame

from game.parrot import _lerp_color


# Day palette per brief.
WICKER_HI = (197, 150, 88)        # lit wicker, lighter than #B98A4A base
WICKER_BASE = (185, 138, 74)      # #B98A4A wicker body
WICKER_LO = (146, 104, 54)        # shaded lower belly
WEAVE = (126, 90, 42)             # #7E5A2A darker weave hatch
# A DARK, saturated red so it separates from cream by VALUE (survives
# grayscale) — a brighter pastel red collapses to the same gray as cream.
CLOTH_RED = (190, 38, 36)         # deep checker red
CLOTH_CREAM = (246, 238, 224)     # bright cream check ground
OUTLINE = (52, 32, 16)            # dark high-value keyline for the bright sky
HANDLE_HI = (210, 166, 104)       # lit cane on the handle's inner edge


def build(mode: str = "normal", icon_size: int = 0) -> pygame.Surface:
    # mode is ignored — the basket keeps its cosy look across every power-up.
    SIZE = 44
    surf = pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)
    cx = SIZE // 2

    # Basket body geometry — WIDE and rounded, the cosy-domestic tell.
    rim_y = 24                     # top rim line
    bot_y = 38                     # rounded bottom
    top_hw = 15                    # half-width at the rim
    bot_hw = 12                    # slightly tapered base

    # Drop shadow grounds the basket under Pip.
    sh = pygame.Surface((34, 8), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (8, 4, 14, 120), sh.get_rect())
    surf.blit(sh, (cx - 17, bot_y - 2))

    # ONE clean HANDLE arch, drawn first so the rim + cloth cover its feet and
    # the arch reads as rising out of the basket. The arch is a thick dark
    # keyline with a thinner cane laid inside it, leaving an OPEN sky-hole under
    # the crown — that hole is the "carry handle" tell and must stay clear, so
    # nothing (no twin band, no mid-gray pool) is drawn across it.
    foot_y = rim_y + 1
    arc_top = 5
    h_rect = pygame.Rect(cx - 11, arc_top, 22, 26)
    # Dark keyline arch (outer) — sharp edges that survive the smoothscale.
    pygame.draw.arc(surf, OUTLINE, h_rect, 0.30, 2.84, 5)
    pygame.draw.line(surf, OUTLINE, (cx - 10, arc_top + 11), (cx - 10, foot_y), 5)
    pygame.draw.line(surf, OUTLINE, (cx + 10, arc_top + 11), (cx + 10, foot_y), 5)
    # Cane fill sits inside the keyline; a single inner highlight gives it round
    # cane volume without a second arc (the muddy twin band read as noise).
    pygame.draw.arc(surf, WICKER_BASE, h_rect, 0.30, 2.84, 2)
    pygame.draw.line(surf, WICKER_BASE, (cx - 10, arc_top + 11), (cx - 10, foot_y), 2)
    pygame.draw.line(surf, WICKER_BASE, (cx + 10, arc_top + 11), (cx + 10, foot_y), 2)
    pygame.draw.arc(surf, HANDLE_HI, h_rect.inflate(-3, -3), 0.5, 2.6, 1)

    # Body OUTLINE frame — an inflated rounded body behind the gradient fill.
    out_rect = pygame.Rect(cx - top_hw - 2, rim_y - 2,
                           (top_hw + 2) * 2, bot_y - rim_y + 4)
    pygame.draw.rect(surf, OUTLINE, out_rect, border_radius=7)

    # Gradient body fill clipped to a rounded basket shape.
    body_rect = pygame.Rect(cx - top_hw, rim_y, top_hw * 2, bot_y - rim_y + 1)
    fill = pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)
    for y in range(body_rect.top, body_rect.bottom):
        t = (y - body_rect.top) / max(1, body_rect.height - 1)
        col = _lerp_color(WICKER_HI, WICKER_LO, t) + (255,)
        fill.fill(col, pygame.Rect(0, y, SIZE, 1))
    mask = pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), body_rect, border_radius=6)
    fill.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(fill, (0, 0))

    # Weave suggestion — ≤3 horizontal hatch lines. A thicker rim band reads as
    # the bound top edge; two thin courses below hint at the wicker rows.
    pygame.draw.line(surf, WEAVE, (cx - top_hw + 1, rim_y + 3),
                     (cx + top_hw - 1, rim_y + 3), 2)
    pygame.draw.line(surf, WEAVE, (cx - top_hw + 2, rim_y + 7),
                     (cx + top_hw - 2, rim_y + 7), 1)
    pygame.draw.line(surf, WEAVE, (cx - bot_hw + 1, rim_y + 11),
                     (cx + bot_hw - 1, rim_y + 11), 1)
    # Vertical weave ticks on the rim band give a wicker over-under read.
    for vx in range(cx - top_hw + 3, cx + top_hw - 1, 5):
        pygame.draw.line(surf, WEAVE, (vx, rim_y + 1), (vx, rim_y + 5), 1)

    # Bound RIM line sits over the body top, a high-value lid edge the cloth
    # bulges over.
    pygame.draw.line(surf, OUTLINE, (cx - top_hw, rim_y),
                     (cx + top_hw, rim_y), 2)
    pygame.draw.line(surf, WICKER_HI, (cx - top_hw + 2, rim_y - 1),
                     (cx + top_hw - 4, rim_y - 1), 1)

    # CLOTH bulge — the "full" personality and the picnic tell. A cream lobe
    # spilling over the rim, CONTAINED within the rim half-width so it can't
    # spill past the keyline and split the silhouette, outlined dark so it pops
    # on the bright sky. Its crown meets the handle cleanly (the handle cane is
    # narrow here, so no third mid-gray material pools between them).
    lobe_hw = 10                    # < top_hw so the lobe stays inside the rim
    cloth_pts = [
        (cx - lobe_hw, rim_y + 1), (cx - lobe_hw + 2, rim_y - 4),
        (cx - 4, rim_y - 6), (cx + 2, rim_y - 6),
        (cx + lobe_hw - 2, rim_y - 4), (cx + lobe_hw, rim_y + 1),
    ]
    pygame.draw.polygon(surf, OUTLINE, _expand(cloth_pts, cx, rim_y, 1))
    pygame.draw.polygon(surf, CLOTH_CREAM, cloth_pts)

    # BOLD blocky CHECKER — a deliberate 2-row checker of big SATURATED red
    # squares on cream, sized to survive the smoothscale to 22px AND grayscale.
    # Squares are ~3px (≈1.5px at 22) and packed edge-to-edge so the red
    # coverage stays high enough to read as a checked tablecloth, not a smudge.
    sq = 3
    top_row = rim_y - 5
    bot_row = rim_y - 2
    # Top row: red squares at the left and right of the crown.
    pygame.draw.rect(surf, CLOTH_RED, pygame.Rect(cx - 7, top_row, sq, sq))
    pygame.draw.rect(surf, CLOTH_RED, pygame.Rect(cx - 1, top_row, sq, sq))
    pygame.draw.rect(surf, CLOTH_RED, pygame.Rect(cx + 5, top_row, sq, sq))
    # Bottom row: offset by one square so the checker alternates over/under.
    pygame.draw.rect(surf, CLOTH_RED, pygame.Rect(cx - 4, bot_row, sq, sq))
    pygame.draw.rect(surf, CLOTH_RED, pygame.Rect(cx + 2, bot_row, sq, sq))
    pygame.draw.rect(surf, CLOTH_RED, pygame.Rect(cx - 10, bot_row, sq, sq))
    pygame.draw.rect(surf, CLOTH_RED, pygame.Rect(cx + 8, bot_row, sq, sq))
    # Cream highlight catch on the crest of the bulge.
    pygame.draw.line(surf, (255, 252, 246), (cx - 4, rim_y - 6),
                     (cx + 1, rim_y - 6), 1)

    if icon_size:
        return pygame.transform.smoothscale(surf, (icon_size, icon_size))
    return pygame.transform.smoothscale(surf, (22, 22))


def _expand(pts, cx, baseline, grow):
    """Push the cloth lobe points outward from its centre to bake a 1px dark
    keyline behind the bulge so it reads against a bright sky."""
    out = []
    for x, y in pts:
        dx = 1 if x > cx else (-1 if x < cx else 0)
        dy = -1 if y < baseline else 1
        out.append((x + dx * grow, y + dy * grow))
    return out
