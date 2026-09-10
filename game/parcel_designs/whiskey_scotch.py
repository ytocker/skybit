"""SCOTCH FIFTH — a labeled single-malt whiskey bottle parcel cosmetic.

The IDENTITY is the classic scotch read: a tall ROUND-SHOULDERED glass bottle
holding AMBER whiskey, fenced across the middle by a fat cream+gold rectangular
LABEL (the brand tell), with a FOIL-wrapped neck and a short cap on top. Two
beats carry the premium read before any detail: the warm amber liquid that fills
the body, and the bright label mass that brands it.

22px read tradeoffs (WHY): at true size the label is the loudest premium cue, so
it is a FAT cream block spanning the body's waist, capped with a gold band and
FENCED top + bottom with the dark OUTLINE colour — that hard fence keeps it one
discrete bright mass after the smoothscale instead of bleeding into the amber.
The label is held full-width so it survives the downscale + the bank rotation as
a band, not a sliver. The amber is a single warm gradient (deeper at the base)
rather than micro-glints, because bold masses beat fine detail at 22px. The neck
foil is a small darker-gold sleeve that separates the cap beat from the round
shoulder so the top never fuses at the downscale. A baked dark OUTLINE (inflated,
drawn first) carries the silhouette on bright DAY sky; a cool KEYLINE rim inside
is the NIGHT lifeline; the bottle is held off the surface edges so the gameplay
rotozoom never clips the cap or base.
"""
import pygame

# Tight palette from the concept: cool-green glass, warm amber whiskey, a cream
# label with a gold band (the brand read + grayscale anchor), gold neck foil, a
# dark outline for day and a cool keyline for night.
GLASS = (159, 194, 194)         # cool-green glass shoulder rim / glints
SHOULDER = (190, 122, 44)       # amber-through-glass at the shoulder (whiskey read)
AMBER = (196, 118, 26)          # whiskey body — warm glowing amber (#C4761A)
AMBER_DK = (154, 86, 14)        # deeper amber low in the body (#9A560E, volume)
AMBER_HI = (236, 168, 86)       # bright meniscus / upper liquid
AMBER_GLINT = (244, 190, 116)   # lit band low in the body (glowing spirit beat)
LABEL = (242, 232, 204)         # cream label mass (the brand read, #F2E8CC-ish)
GOLD = (231, 184, 66)           # gold label pinstripe + foil collar (premium tell)
GOLD_HI = (250, 228, 146)       # gold highlight edge
FOIL = (214, 168, 52)           # gold-foil neck collar (its own deeper-gold beat)
CAP = (46, 35, 22)              # dark cork-cap top beat (own darker value)
OUTLINE = (32, 24, 15)          # dark, high-value: reads on bright day sky
KEYLINE = (208, 224, 220)       # cool rim — the NIGHT lifeline


def build(mode="normal", icon_size: int = 0) -> pygame.Surface:
    # Mode-agnostic: one static bottle sprite for every Pip skin.
    S = 44
    surf = pygame.Surface((S, S), pygame.SRCALPHA)
    cx = S // 2

    # Geometry: a TALL body with a round shoulder, a foil neck, and a short cap.
    # Held off the surface edges so the gameplay rotozoom never clips it.
    BW = 17
    body_top = 17                 # straight body wall starts below the shoulder
    body_bot = 40
    body_rect = pygame.Rect(cx - BW // 2, body_top, BW, body_bot - body_top)
    body_rad = 4                  # base rounds in

    # Round shoulder: a wedge that tucks the body wall up into the neck.
    # The gold FOIL collar is a deliberately TALL/WIDE distinct gold beat so it
    # never fuses with the dark cap above it at small bank angles.
    shoulder_top = 13
    NW = 9
    foil_top = 7
    neck_rect = pygame.Rect(cx - NW // 2, foil_top, NW, shoulder_top - foil_top + 2)

    # Cap: a short dark cork beat ABOVE the foil, its own darker value, with a
    # 1px groove between cap and foil so the top reads dark / gold top-to-bottom.
    CW, CH = 7, 4
    cap_rect = pygame.Rect(cx - CW // 2, 2, CW, CH)

    # --- Baked dark outline (drawn first, slightly inflated) for the DAY read.
    pygame.draw.rect(surf, OUTLINE, cap_rect.inflate(4, 4), border_radius=2)
    pygame.draw.rect(surf, OUTLINE, neck_rect.inflate(4, 3))
    # Round shoulder outline: an ellipse spanning body width up to the neck.
    sh_out = pygame.Rect(body_rect.x - 2, shoulder_top - 2,
                         BW + 4, (body_top - shoulder_top) + 6)
    pygame.draw.ellipse(surf, OUTLINE, sh_out)
    pygame.draw.rect(surf, OUTLINE, body_rect.inflate(4, 4),
                     border_radius=body_rad + 2)

    # --- Round shoulder fill: amber-through-glass so the whiskey read carries
    # all the way up the bottle, with a thin cool glass rim at the very top edge.
    sh_fill = pygame.Rect(body_rect.x, shoulder_top, BW, (body_top - shoulder_top) + 4)
    pygame.draw.ellipse(surf, SHOULDER, sh_fill)
    pygame.draw.arc(surf, GLASS, sh_fill, 0.5, 2.64, 1)  # cool glint along the top curve

    # --- BODY built on its own alpha surface: amber whiskey with the cream LABEL
    # mass fenced across the waist, masked to the straight-walled shape and
    # composited in one piece so the label edges antialias cleanly.
    bw, bh = body_rect.w, body_rect.h
    body = pygame.Surface((bw, bh), pygame.SRCALPHA)

    # Amber whiskey gradient: a warm glowing spirit — lit amber near the top
    # (meniscus), warming through the body amber, deepening to a rich base —
    # one warm mass, not micro-glints, because masses beat detail at 22px.
    for y in range(bh):
        t = y / max(1, bh - 1)
        if t < 0.5:                 # upper liquid: highlight -> body amber
            u = t / 0.5
            a, b = AMBER_HI, AMBER
        else:                       # lower liquid: body amber -> deep base
            u = (t - 0.5) / 0.5
            a, b = AMBER, AMBER_DK
        c = (int(a[0] + (b[0] - a[0]) * u),
             int(a[1] + (b[1] - a[1]) * u),
             int(a[2] + (b[2] - a[2]) * u))
        body.fill(c + (255,), pygame.Rect(0, y, bw, 1))

    # Label band geometry: a FAT cream mass across the body waist. Spanning
    # ~0.30–0.62 of body height so the bright core survives the downscale +
    # rotation as a band, not a sliver — the loudest premium cue.
    label_top = int(bh * 0.30)
    label_bot = int(bh * 0.62)

    # ONE clear amber highlight beat LOW in the body (below the label) so the
    # lower glass reads as lit liquid, not flat brown — a soft glowing band.
    glint_y = label_bot + int((bh - label_bot) * 0.42)
    pygame.draw.line(body, AMBER_GLINT, (2, glint_y), (bw - 3, glint_y), 2)
    pygame.draw.line(body, AMBER_HI, (2, glint_y + 2), (bw - 3, glint_y + 2), 1)

    # Cream label: the single brightest, cleanest mass — no interior shade.
    body.fill(LABEL + (255,), pygame.Rect(0, label_top, bw, label_bot - label_top))
    # ONE crisp gold pinstripe at the label TOP (the only interior detail).
    body.fill(GOLD + (255,), pygame.Rect(0, label_top + 1, bw, 1))
    pygame.draw.line(body, GOLD_HI, (0, label_top + 2), (bw, label_top + 2), 1)
    # FENCE top + bottom with the dark OUTLINE colour so the label stays one
    # hard, discrete bright block after the smoothscale instead of bleeding.
    pygame.draw.line(body, OUTLINE, (0, label_top), (bw, label_top), 1)
    pygame.draw.line(body, OUTLINE, (0, label_bot - 1), (bw, label_bot - 1), 1)

    # Mask to a STRAIGHT-WALLED shape: only the bottom corners round.
    mask = pygame.Surface((bw, bh), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(),
                     border_radius=body_rad, border_top_left_radius=0,
                     border_top_right_radius=0)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(body, body_rect.topleft)

    # --- Meniscus glint just under the shoulder so the upper amber reads as
    # liquid surface (a bright lip above the label).
    my = body_rect.y + 2
    pygame.draw.line(surf, AMBER_HI,
                     (body_rect.x + 2, my), (body_rect.right - 3, my), 1)
    # Vertical glass glint streak on the amber (a single committed highlight).
    pygame.draw.line(surf, AMBER_HI,
                     (body_rect.x + 3, body_rect.y + 3),
                     (body_rect.x + 3, body_rect.y + label_top - 1), 2)

    # --- FOIL COLLAR: a tall/wide deeper-gold sleeve, its own distinct beat that
    # separates the dark cap from the round amber shoulder. Bright gold highlight
    # up one side, lit gold top edge so it never reads as the same value as the cap.
    pygame.draw.rect(surf, FOIL, neck_rect)
    pygame.draw.line(surf, GOLD_HI,
                     (neck_rect.x + 1, neck_rect.y + 1),
                     (neck_rect.x + 1, neck_rect.bottom - 1), 1)
    pygame.draw.line(surf, GOLD,
                     (neck_rect.x + 1, neck_rect.y),
                     (neck_rect.right - 2, neck_rect.y), 1)
    # Hard foil/shoulder groove so the collar stays a distinct beat at the downscale.
    pygame.draw.line(surf, OUTLINE,
                     (neck_rect.x, neck_rect.bottom - 1),
                     (neck_rect.right - 1, neck_rect.bottom - 1), 1)

    # --- CAP: short dark cork top, its OWN darker value. A 1px OUTLINE groove
    # between cap and foil keeps the two from fusing at small bank angles.
    pygame.draw.rect(surf, OUTLINE,
                     pygame.Rect(cap_rect.x - 1, cap_rect.bottom,
                                 cap_rect.w + 2, 1))
    pygame.draw.rect(surf, CAP, cap_rect, border_radius=2)
    pygame.draw.line(surf, GLASS,
                     (cap_rect.x + 1, cap_rect.y + 1),
                     (cap_rect.right - 2, cap_rect.y + 1), 1)

    # --- Cool keyline rim INSIDE the outline — the NIGHT lifeline that glows on
    # dark sky while staying subtle on day. Traces the body wall + shoulder + cap.
    pygame.draw.rect(surf, KEYLINE, body_rect, width=1, border_radius=body_rad,
                     border_top_left_radius=0, border_top_right_radius=0)
    pygame.draw.ellipse(surf, KEYLINE, sh_fill, width=1)
    pygame.draw.rect(surf, KEYLINE, cap_rect, width=1, border_radius=2)

    if icon_size:
        return pygame.transform.smoothscale(surf, (icon_size, icon_size))
    return pygame.transform.smoothscale(surf, (22, 22))
