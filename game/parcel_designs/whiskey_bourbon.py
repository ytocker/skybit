"""SQUARE BOURBON — a square black-and-gold Tennessee-whiskey bottle parcel.

The IDENTITY is the SQUARE boxy bottle + the BLACK-and-GOLD centre label. Three
beats carry it: SQUARE shoulders (a straight-walled glass box, not a round
bottle), a crisp BLACK rectangular LABEL trimmed in GOLD across the middle, and
a short BLACK screw CAP. Amber whiskey peeks above and below the label so the
vessel reads as a drink before the label even registers.

22px read tradeoffs (WHY): the black label is the loudest premium cue, so it is a
FAT crisp rectangular MASS (~0.30–0.74 of the body) filled solid near-black with
its centre rows kept PURE BLACK and crossed by NO gold at all — at the 22px
downscale, any gold drawn INSIDE the black averages the whole band into muddy
gold-brown, so ALL gold is pushed OUT of the label interior onto the amber. The
gold trim is the SECOND cue and lives ONLY as two thin gold FENCE lines — one on
the amber just above the label's top edge, one on the amber just below the bottom
edge (gold-on-amber survives the downscale where gold-on-black dissolved). The
read top-to-bottom is amber / gold edge / SOLID BLACK BAR / gold edge / amber.
The body walls are kept dead STRAIGHT with only the
base corners tucked so the silhouette stays boxy and squared off — the square
shape is what separates it from a round whiskey bottle across the tilt arc. Amber
is split into a BRIGHT band above (so it never fuses with the cap/shoulder) and a
deeper pool below the label so a hint of liquid reads on both sides without
competing with the black mass. A single 2px gold-hi glint sits at the label's
top-LEFT corner — never inside the black core. Drawn on a 44px
work surface then smoothscaled to 22 so the label/gold edges antialias cleanly. A
baked dark OUTLINE (inflated, drawn first) carries the silhouette on bright DAY
sky; a warm gold-tinted KEYLINE rim inside is the NIGHT lifeline; the bottle is
held off the surface edges so the gameplay rotozoom never clips the cap or base.
"""
import pygame

# Tight palette from the concept: pale green glass, amber bourbon, a black centre
# label, gold trim (the premium tell), a dark outline for day and a warm keyline
# for night.
GLASS = (168, 182, 160)        # pale green Tennessee glass (shoulders / edges)
AMBER = (168,  94,  22)        # bourbon liquid
AMBER_HI = (214, 138,  56)     # lit amber / meniscus glint
LABEL = ( 30,  30,  34)        # near-black label body (the loudest premium mass)
LABEL_CORE = (  6,   6,  10)   # PURE-black centre rows — kept clear of all gold
GOLD = (227, 178,  60)         # gold trim ring + band (the second cue)
GOLD_HI = (248, 224, 138)      # gold highlight glint
CAP = ( 26,  26,  30)          # short black screw cap
CAP_HI = ( 96,  96, 104)       # cap top edge highlight
OUTLINE = ( 22,  22,  14)      # dark, high-contrast: reads on bright day sky
KEYLINE = (228, 196, 120)      # warm gold rim — the NIGHT lifeline


def build(mode="normal", icon_size: int = 0) -> pygame.Surface:
    # Mode-agnostic: one static bottle sprite for every Pip skin.
    S = 44
    surf = pygame.Surface((S, S), pygame.SRCALPHA)
    cx = S // 2

    # Geometry: a SQUARE-shouldered glass body, a short neck, and a short black
    # cap. Held off the surface edges so the gameplay rotozoom never clips it.
    BW = 18
    body_top = 14
    body_bot = 39
    body_rect = pygame.Rect(cx - BW // 2, body_top, BW, body_bot - body_top)
    body_rad = 2                  # only a faint base tuck so the box stays square

    # Neck: a short narrow step from the square shoulder up to the cap.
    NW = 8
    neck_rect = pygame.Rect(cx - NW // 2, 9, NW, 6)

    # Cap: a short black screw cap — the boxy bourbon top beat. Kept squat + wide
    # so it stays a distinct black block over the body on night / grayscale.
    CW, CH = 11, 7
    cap_rect = pygame.Rect(cx - CW // 2, 3, CW, CH)

    # --- Baked dark outline (drawn first, slightly inflated) for the DAY read.
    pygame.draw.rect(surf, OUTLINE, cap_rect.inflate(4, 4), border_radius=2)
    pygame.draw.rect(surf, OUTLINE, neck_rect.inflate(4, 3))
    pygame.draw.rect(surf, OUTLINE, body_rect.inflate(4, 4), border_radius=body_rad + 2)

    # --- Square shoulder: hard, near-flat tucks from the body wall corners into
    # the neck so the cap/neck and body never fuse, while keeping the shoulder
    # squared rather than rounded (the boxy bourbon read).
    sh_y = neck_rect.bottom
    sh_dark = (44, 50, 40)
    pygame.draw.polygon(surf, sh_dark, [
        (body_rect.x, body_top + 1),
        (neck_rect.x, sh_y - 1),
        (neck_rect.x, sh_y + 1),
        (body_rect.x, body_top + 3),
    ])
    pygame.draw.polygon(surf, sh_dark, [
        (body_rect.right, body_top + 1),
        (neck_rect.right, sh_y - 1),
        (neck_rect.right, sh_y + 1),
        (body_rect.right, body_top + 3),
    ])
    # Fill the shoulder interior so the body wall meets the neck cleanly.
    pygame.draw.polygon(surf, GLASS, [
        (body_rect.x + 1, body_top + 2),
        (neck_rect.x, sh_y),
        (neck_rect.right, sh_y),
        (body_rect.right - 1, body_top + 2),
    ])

    # --- BODY built on its own alpha surface: a thin amber band, the BLACK label
    # with gold trim across the middle, then a deeper amber band below, masked to
    # the straight-walled square shape and composited in one piece.
    bw, bh = body_rect.w, body_rect.h
    body = pygame.Surface((bw, bh), pygame.SRCALPHA)

    # Amber whiskey fills the whole body first; the black label sits on top of it
    # so amber peeks above AND below as a hint of liquid. The TOP half is pushed
    # toward AMBER_HI so the upper band stays bright and never fuses with the
    # cap/shoulder; the lower half settles into a deeper amber pool.
    for y in range(bh):
        t = y / max(1, bh - 1)
        # Bias the gradient so the top band reads brighter than a linear ramp.
        tt = t * t
        c = (
            int(AMBER_HI[0] + (AMBER[0] - AMBER_HI[0]) * tt),
            int(AMBER_HI[1] + (AMBER[1] - AMBER_HI[1]) * tt),
            int(AMBER_HI[2] + (AMBER[2] - AMBER_HI[2]) * tt),
        )
        body.fill(c + (255,), pygame.Rect(0, y, bw, 1))

    # Label band geometry: a FAT crisp black mass across the MIDDLE, near full
    # body width, widened to ~0.30–0.74 so the black survives as the dominant
    # mass with a bright amber band above and a deeper amber pool below.
    label_top = int(bh * 0.30)
    label_bot = int(bh * 0.74)

    # BLACK centre label — the loudest premium mass, and the WHOLE design. Filled
    # solid near-black; its centre source rows are forced PURE BLACK with NO gold
    # crossing them so the band reads as a hard black BAR at 22px (gold drawn
    # inside would average the whole label into muddy gold-brown at the downscale).
    body.fill(LABEL + (255,), pygame.Rect(0, label_top, bw, label_bot - label_top))
    core_top = label_top + 2
    core_bot = label_bot - 2
    body.fill(LABEL_CORE + (255,), pygame.Rect(0, core_top, bw, core_bot - core_top))
    # FENCE the label top + bottom with the dark OUTLINE value so the edges stay
    # crisp against the amber after the smoothscale.
    pygame.draw.line(body, OUTLINE, (0, label_top), (bw, label_top), 1)
    pygame.draw.line(body, OUTLINE, (0, label_bot - 1), (bw, label_bot - 1), 1)

    # GOLD trim — the second cue — lives ONLY on the amber OUTSIDE the black: one
    # fence line just above the label and one just below. Gold-on-amber survives
    # the downscale where gold-on-black dissolved into mud. Nothing gold ever
    # crosses the black core.
    pygame.draw.line(body, GOLD, (1, label_top - 1), (bw - 2, label_top - 1), 1)
    pygame.draw.line(body, GOLD, (1, label_bot), (bw - 2, label_bot), 1)
    # ONE restrained gold-hi glint at the label's top-LEFT corner — on the amber
    # fence, never inside the black core.
    pygame.draw.line(body, GOLD_HI, (1, label_top - 1), (4, label_top - 1), 1)

    # Mask to a STRAIGHT-WALLED square shape: only the bottom corners tuck.
    mask = pygame.Surface((bw, bh), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(),
                     border_radius=body_rad, border_top_left_radius=0,
                     border_top_right_radius=0)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(body, body_rect.topleft)

    # --- Glass glint on the amber above the label so the body reads as liquid.
    pygame.draw.line(surf, AMBER_HI,
                     (body_rect.x + 2, body_rect.y + 2),
                     (body_rect.x + 2, body_rect.y + label_top - 1), 2)
    # Meniscus glint on the deeper amber below the label.
    pygame.draw.line(surf, AMBER_HI,
                     (body_rect.x + 2, body_rect.y + label_bot + 1),
                     (body_rect.right - 3, body_rect.y + label_bot + 1), 1)

    # --- NECK fill (between the square shoulder and the cap).
    pygame.draw.rect(surf, GLASS, neck_rect)

    # --- CAP: short black screw cap with a flat top highlight + a hard groove at
    # the cap/neck join (OUTLINE colour) so it reads as a screw-on lid.
    pygame.draw.rect(surf, CAP, cap_rect, border_radius=2)
    pygame.draw.line(surf, CAP_HI,
                     (cap_rect.x + 1, cap_rect.y + 1),
                     (cap_rect.right - 2, cap_rect.y + 1), 1)
    pygame.draw.line(surf, OUTLINE,
                     (cap_rect.x, cap_rect.bottom - 1),
                     (cap_rect.right - 1, cap_rect.bottom - 1), 2)

    # --- Warm gold keyline rim INSIDE the outline — the NIGHT lifeline that glows
    # on dark sky while staying subtle on day. Traces the square body wall + cap.
    pygame.draw.rect(surf, KEYLINE, body_rect, width=1, border_radius=body_rad,
                     border_top_left_radius=0, border_top_right_radius=0)
    pygame.draw.rect(surf, KEYLINE, cap_rect, width=1, border_radius=2)

    if icon_size:
        return pygame.transform.smoothscale(surf, (icon_size, icon_size))
    return pygame.transform.smoothscale(surf, (22, 22))
