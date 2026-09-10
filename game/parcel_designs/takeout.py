"""TAKEOUT PAIL parcel cosmetic (LOW tier).

The classic Chinese-takeout oyster pail, drawn as the FOLDED CARD-STOCK BOX it
actually is — not a turned vessel. The silhouette is a squat, near-square
trapezoid: a slightly flared top over a WIDE FLAT bottom (base ~70% of the top
width), so it reads as a flat-bottomed box rather than a tapered bucket. One
bold ASYMMETRIC diagonal flap folds the top closed (the single overlapping
closure of real oyster pails), a 1px vertical FRONT SEAM creases the body so the
paper reads folded, and a tall thin near-semicircular WIRE bail arches above.

Everything is drawn at 2× then smoothscaled to 22px, so the cues are pushed
hard: the diagonal closure is several px of run, the seam is a clean value step,
and the bail is a thin bright 1px@22 (2px@2×) wire over a dark keyline so it
stays a crisp arc through the tilt-row banking instead of blobbing into a mass.
"""
import pygame

from game.parrot import _lerp_color


# Day palette per brief; night relies on the white body self-lighting, with
# only a faint cool keyline so the box doesn't smear into the dark sky.
BODY_HI = (244, 241, 234)        # #F4F1EA white paper, lit edge
BODY_LO = (208, 202, 188)        # shaded fold side for a touch of form
SEAM_LO = (190, 184, 170)        # one value step darker — the front crease
FLAP = (211, 58, 44)             # #D33A2C red fold-tab accent
FLAP_HI = (236, 110, 96)
FLAP_LO = (158, 38, 30)          # shadowed underlap so the diagonal fold reads
WIRE = (176, 176, 186)           # brighter grey wire — stays a thin arc tilted
WIRE_HI = (214, 214, 224)
OUTLINE = (40, 28, 24)           # dark high-value keyline for the bright sky


def build(mode: str = "normal", icon_size: int = 0) -> pygame.Surface:
    # mode is ignored — the pail keeps its own look across every power-up.
    SIZE = 44
    surf = pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)

    cx = SIZE // 2

    # Flat-bottomed BOX body — slightly flared top over a WIDE flat base. The
    # base half-width is ~70% of the top (11 vs 16 at 2×), and the body is squat
    # (top 18 → bottom 37, ~19px tall) so after smoothscale it reads square-ish
    # and flat-bottomed, NOT a tall tapered bucket.
    top_y, bot_y = 18, 37
    top_hw, bot_hw = 16, 11
    body = [
        (cx - top_hw, top_y),
        (cx + top_hw, top_y),
        (cx + bot_hw, bot_y),
        (cx - bot_hw, bot_y),
    ]

    # Drop shadow grounds the pail under Pip; widened to match the broader base.
    sh = pygame.Surface((30, 8), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (8, 4, 14, 120), sh.get_rect())
    surf.blit(sh, (cx - 15, bot_y - 1))

    # Tall thin near-semicircular WIRE bail FIRST so the body top edge overlaps
    # its feet — the arch then reads as a flimsy wire rising out of the box. Feet
    # land just inside the top corners; the arch rises well above the body to a
    # clear semicircle. A dark keyline backs the thin bright wire so it stays a
    # crisp arc — never a grey blob — through the tilt extremes.
    foot_y = top_y + 1
    fl_x, fr_x = cx - 9, cx + 9
    arc_top = 4
    arc_rect = pygame.Rect(fl_x, arc_top, (fr_x - fl_x), (foot_y - arc_top) * 2)
    # Keyline backing: stubby legs + the full half-circle arch (thin, +1 over wire).
    pygame.draw.line(surf, OUTLINE, (fl_x, foot_y), (fl_x, arc_top + 6), 3)
    pygame.draw.line(surf, OUTLINE, (fr_x, foot_y), (fr_x, arc_top + 6), 3)
    pygame.draw.arc(surf, OUTLINE, arc_rect, 0.0, 3.1416, 3)
    # Thin bright wire over the keyline — 2px@2× so it survives as a 1px arc@22.
    pygame.draw.line(surf, WIRE, (fl_x, foot_y), (fl_x, arc_top + 6), 2)
    pygame.draw.line(surf, WIRE, (fr_x, foot_y), (fr_x, arc_top + 6), 2)
    pygame.draw.arc(surf, WIRE, arc_rect, 0.0, 3.1416, 2)
    # Top highlight so the wire catches light and reads as round metal.
    pygame.draw.arc(surf, WIRE_HI, arc_rect.inflate(0, -3), 0.5, 2.6, 1)

    # Body outline frame, then a vertical gradient fill clipped to the shape.
    out_body = [
        (cx - top_hw - 2, top_y - 1),
        (cx + top_hw + 2, top_y - 1),
        (cx + bot_hw + 2, bot_y + 2),
        (cx - bot_hw - 2, bot_y + 2),
    ]
    pygame.draw.polygon(surf, OUTLINE, out_body)
    fill = pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)
    for y in range(top_y, bot_y + 1):
        t = (y - top_y) / max(1, bot_y - top_y)
        col = _lerp_color(BODY_HI, BODY_LO, t) + (255,)
        fill.fill(col, pygame.Rect(0, y, SIZE, 1))
    mask = pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), body)
    fill.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(fill, (0, 0))

    # Single vertical FRONT SEAM — one clean value step down the centre so the
    # body reads as a folded sheet of card stock with a front crease, not a
    # smooth turned vessel. Kept off-bright so it's a subtle crease, not a slot.
    pygame.draw.line(surf, SEAM_LO, (cx, top_y + 4), (cx, bot_y - 1), 1)

    # Lit left edge — gives the white paper a crisp self-lit keyline at night.
    pygame.draw.line(surf, (255, 253, 248),
                     (cx - top_hw + 2, top_y + 3),
                     (cx - bot_hw + 2, bot_y - 2), 1)

    # Folded RED TOP — the hero tell, now ONE bold ASYMMETRIC diagonal flap: a
    # single overlapping closure that crosses from the high left rim down to the
    # low right, the way real oyster pails fold shut. The asymmetry is what sells
    # "folded paper" at 22px versus a symmetric crimp.
    cap_lo = top_y + 6                           # how far the closure folds down
    # Shadowed UNDERLAP first — the flap the diagonal overlaps onto, on the right.
    pygame.draw.polygon(surf, FLAP_LO, [
        (cx - 2, top_y - 1),
        (cx + top_hw, top_y - 1),
        (cx + top_hw - 1, cap_lo),
        (cx - 2, cap_lo - 1),
    ])
    # Bold OVERLAP flap — a diagonal fold sweeping from the high left corner down
    # across to the low right, overlapping the underlap. This single skewed tab
    # is the unmistakable single-closure tell.
    pygame.draw.polygon(surf, FLAP, [
        (cx - top_hw, top_y),
        (cx + top_hw - 3, top_y - 3),        # high point lifts above the rim
        (cx + top_hw - 1, cap_lo - 2),
        (cx - top_hw + 1, cap_lo),
    ])
    # Keyline the leading diagonal edge of the overlap so the fold's slant is
    # crisp after downscale — this single bold diagonal is the read.
    pygame.draw.line(surf, OUTLINE,
                     (cx + top_hw - 3, top_y - 3), (cx - top_hw, top_y), 1)
    pygame.draw.line(surf, OUTLINE,
                     (cx - top_hw + 1, cap_lo), (cx + top_hw - 1, cap_lo - 2), 1)
    # Lit crease running along the diagonal so the fold catches light.
    pygame.draw.line(surf, FLAP_HI,
                     (cx - top_hw + 2, top_y), (cx + top_hw - 4, top_y - 2), 1)

    # Wire-attachment PINCH DIMPLES at the top rim corners — small dark notches
    # where the bail pinches the paper, an instantly-readable pail cue.
    pygame.draw.line(surf, OUTLINE, (fl_x - 1, top_y), (fl_x + 1, top_y + 2), 2)
    pygame.draw.line(surf, OUTLINE, (fr_x - 1, top_y + 2), (fr_x + 1, top_y), 2)

    if icon_size:
        return pygame.transform.smoothscale(surf, (icon_size, icon_size))
    return pygame.transform.smoothscale(surf, (22, 22))
