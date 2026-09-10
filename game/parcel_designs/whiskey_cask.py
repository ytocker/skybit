"""CASKED DRAM — a cask-aged whiskey bottle in a wooden barrel-stave cradle.

The IDENTITY is two value-separated masses: a warm AMBER glass bottle with a
pale CORK stopper, seated in a curved BROWN wood cradle wrapped by a grey IRON
hoop. The cradle is the tell that lifts this above a plain bottle — a fine
single-cask dram still riding its barrel. The amber bottle reads as the drink;
the wood cradle below reads as the cask.

22px read tradeoffs (WHY): at true size the two materials must NOT fuse, so they
are pushed apart on VALUE as well as hue — the bottle is a bright amber that
desaturates to a light grey, the wood cradle is a deliberately DARKER brown that
desaturates to a clearly lower grey, with a hard iron-hoop band between them as a
third value to fence the join. Micro wood grain turns to mud at this size, so the
cradle is sold by ONE bold curved mass + a single stave-seam down its middle and
the bright hoop band, not by plank lines. The cork is kept a FAT pale block (the
loudest top beat) so the bottle reads as sealed even after the smoothscale. Built
on a 44px work surface then smoothscaled to 22 so the curved cradle and amber
edges antialias cleanly. A baked dark OUTLINE (inflated, drawn first) carries the
silhouette on bright DAY sky; a warm amber KEYLINE rim inside is the NIGHT
lifeline; bottle + cradle are held off the surface edges so the gameplay rotozoom
never clips the cork or the cradle horns under Pip's bank arc.
"""
import pygame

# Tight palette from the concept. Identity rides on VALUE: amber glass is the
# bright mass, wood is pushed darker, the iron hoop is a cool mid-grey band that
# fences the two so they read apart even in grayscale. Cork is a pale beat on top.
AMBER = (198, 122,  40)        # cask-aged whiskey glass (body mid)
AMBER_HI = (244, 186,  96)     # lit amber highlight / left glass sheen
# Belly is deliberately kept MID amber (not driven down to wood value) so the
# glass never sinks to the cradle's grey in grayscale — the amber/wood split is
# the load-bearing read, so the bottle holds a high mid value all the way down.
AMBER_DEEP = (176, 104,  40)   # lower-body amber — stays well above wood luma
CORK = (201, 160, 106)         # pale cork stopper — the loudest top beat
CORK_HI = (230, 200, 156)      # cork top edge highlight
# Wood pushed meaningfully darker (and its lit stave lifted) so the cradle owns a
# full light->dark sweep that sits CLEARLY below the amber belly's value. The gap
# between AMBER_DEEP luma and WOOD core luma is the ≥60-luma fence.
WOOD = ( 96,  60,  34)         # barrel-stave cradle (darker than amber on value)
WOOD_HI = (172, 124,  80)      # lit upper stave face (lifted for its own sweep)
WOOD_SHADE = ( 62,  38,  20)   # stave seam + inner cradle shadow (deep)
IRON = (104, 110, 120)         # iron hoop band (cool grey — third value)
IRON_HI = (170, 176, 184)      # hoop top highlight so it reads as a metal band
OUTLINE = ( 36,  26,  16)      # dark, high-value: reads on bright day sky
KEYLINE = (240, 196, 120)      # warm amber rim — the NIGHT lifeline (BOTTLE only)
# Cradle gets its own cooler/darker keyline so the night rim never makes the wood
# glow amber and erase the wood/glass split.
KEYLINE_WOOD = (132,  98,  64) # desaturated tan rim for the cradle at night


def build(mode="normal", icon_size: int = 0) -> pygame.Surface:
    # Mode-agnostic: one static casked-dram sprite for every Pip skin.
    S = 44
    surf = pygame.Surface((S, S), pygame.SRCALPHA)
    cx = S // 2

    # Geometry: a rounded amber bottle standing in a shallow wooden cradle. The
    # bottle is biased UP so the cork has headroom; the cradle hugs the lower body
    # so the wood reads as a separate mass beneath the glass. Everything is held
    # off the surface edges for the rotozoom.
    BW = 15                       # bottle body width
    body_top = 16
    body_bot = 34
    body_rect = pygame.Rect(cx - BW // 2, body_top, BW, body_bot - body_top)
    body_rad = 6                  # rounded barrel-bellied bottle

    # Neck + cork above the shoulder.
    NW = 6
    neck_rect = pygame.Rect(cx - NW // 2, 9, NW, 8)
    CW, CH = 8, 6
    cork_rect = pygame.Rect(cx - CW // 2, 3, CW, CH)

    # Cradle: a flatter TRAPEZOIDAL barrel-stave profile (straight, slightly
    # tapering outer walls — staves, not a pillow) cupping the lower body. Its top
    # is pulled UP so the two "horns" rise PAST the bottle belly, making the glass
    # clearly sit INSIDE the cask. Widened past the bottle so the wood reads as its
    # own mass on every side. Built as an explicit polygon (with a small bottom
    # round) rather than a rounded rect so the silhouette stays barrel-staved.
    cradle_top = 25               # raised so horns clear the bottle belly
    cradle_bot = 41
    cradle_rect = pygame.Rect(cx - 15, cradle_top, 30, cradle_bot - cradle_top)
    # Outer wall taper: top edge a touch wider than the base (a cask belly).
    HORN = 2                      # how far each top horn flares past the base
    cr_l, cr_r = cradle_rect.left, cradle_rect.right
    cr_t, cr_b = cradle_rect.top, cradle_rect.bottom
    cradle_poly = [
        (cr_l - HORN, cr_t + 1),          # left horn (rises past belly)
        (cr_l - HORN + 1, cr_t - 2),      # horn tip
        (cr_l + 2, cr_t - 2),
        (cr_l + 1, cr_t + 4),
        (cr_l + 1, cr_b - 4),             # straight outer wall
        (cr_l + 4, cr_b),                 # bottom round-in
        (cr_r - 4, cr_b),
        (cr_r - 1, cr_b - 4),
        (cr_r - 1, cr_t + 4),
        (cr_r - 2, cr_t - 2),
        (cr_r + HORN - 1, cr_t - 2),      # right horn tip
        (cr_r + HORN, cr_t + 1),          # right horn
    ]

    # ---- Baked dark outline (drawn first, inflated) for the DAY silhouette. ----
    pygame.draw.rect(surf, OUTLINE, cork_rect.inflate(4, 4), border_radius=2)
    pygame.draw.rect(surf, OUTLINE, neck_rect.inflate(4, 2))
    pygame.draw.rect(surf, OUTLINE, body_rect.inflate(4, 4), border_radius=body_rad + 2)
    # Cradle outline: the stave polygon inflated outward by drawing it fat first.
    pygame.draw.polygon(surf, OUTLINE, [
        (px + (2 if px > cx else -2), py + (2 if py > (cr_t + cr_b) // 2 else -2))
        for (px, py) in cradle_poly])

    # ---- Shoulder tuck: dark diagonals so neck and body don't fuse. ----
    sh_y = neck_rect.bottom
    sh_dark = AMBER_DEEP
    pygame.draw.polygon(surf, sh_dark, [
        (body_rect.x, body_top + 3), (neck_rect.x, sh_y - 1),
        (neck_rect.x, sh_y + 1), (body_rect.x, body_top + 5)])
    pygame.draw.polygon(surf, sh_dark, [
        (body_rect.right, body_top + 3), (neck_rect.right, sh_y - 1),
        (neck_rect.right, sh_y + 1), (body_rect.right, body_top + 5)])

    # ---- AMBER BODY: a vertical light->deep gradient masked to the rounded
    # bottle, so the glass reads as a lit volume, not a flat amber slab. ----
    bw, bh = body_rect.w, body_rect.h
    body = pygame.Surface((bw, bh), pygame.SRCALPHA)
    for y in range(bh):
        t = y / max(1, bh - 1)
        # Lit at top, deepening toward the base where the cradle shadows it.
        c = (
            int(AMBER_HI[0] + (AMBER_DEEP[0] - AMBER_HI[0]) * t),
            int(AMBER_HI[1] + (AMBER_DEEP[1] - AMBER_HI[1]) * t),
            int(AMBER_HI[2] + (AMBER_DEEP[2] - AMBER_HI[2]) * t),
        )
        body.fill(c + (255,), pygame.Rect(0, y, bw, 1))
    # A broad mid-body amber band carried LOW so the belly (where it meets the
    # cradle) stays a bright mid amber and never sinks to wood value in grayscale.
    body.fill(AMBER + (255,), pygame.Rect(0, int(bh * 0.34), bw, int(bh * 0.46)))
    mask = pygame.Surface((bw, bh), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=body_rad)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(body, body_rect.topleft)

    # A bright vertical glass sheen down the lit (left) edge so the amber reads as
    # glossy glass — the brightest amber stroke, the value anchor on grayscale.
    pygame.draw.line(surf, AMBER_HI, (body_rect.x + 3, body_rect.y + 3),
                     (body_rect.x + 3, body_rect.bottom - 6), 2)

    # ---- NECK fill. ----
    pygame.draw.rect(surf, AMBER, neck_rect)
    pygame.draw.line(surf, AMBER_HI, (neck_rect.x + 1, neck_rect.y + 1),
                     (neck_rect.x + 1, neck_rect.bottom - 1), 1)

    # ---- CORK: a FAT pale block with a top highlight + a hard groove at the
    # cork/neck join so the bottle reads as sealed. ----
    pygame.draw.rect(surf, CORK, cork_rect, border_radius=2)
    pygame.draw.line(surf, CORK_HI, (cork_rect.x + 1, cork_rect.y + 1),
                     (cork_rect.right - 2, cork_rect.y + 1), 1)
    # A 1px dark groove between the cork base and the amber neck so the two pale/
    # warm masses never fuse at small bank angles after the smoothscale.
    pygame.draw.line(surf, OUTLINE, (cork_rect.x, cork_rect.bottom),
                     (cork_rect.right - 1, cork_rect.bottom), 1)
    pygame.draw.line(surf, OUTLINE, (cork_rect.x, cork_rect.bottom - 1),
                     (cork_rect.right - 1, cork_rect.bottom - 1), 1)

    # ---- WOODEN CRADLE: ONE bold curved brown mass cupping the lower body. The
    # bottle's amber base sits INTO it, so the wood is drawn over the lower body
    # to read as the bottle resting IN the cradle. Sold by a value step (darker
    # than amber) + a single stave seam, not plank lines that would alias to mud.
    # A full light->dark wood sweep painted over the surface, then masked to the
    # stave polygon. WOOD_HI lit at the top horns, dropping to WOOD_SHADE at the
    # trough — the cradle carries its OWN clear value sweep below the amber belly.
    cradle = pygame.Surface((S, S), pygame.SRCALPHA)
    g0, g1 = cr_t - 2, cr_b
    for y in range(g0, g1 + 1):
        t = (y - g0) / max(1, g1 - g0)
        c = (
            int(WOOD_HI[0] + (WOOD_SHADE[0] - WOOD_HI[0]) * t),
            int(WOOD_HI[1] + (WOOD_SHADE[1] - WOOD_HI[1]) * t),
            int(WOOD_HI[2] + (WOOD_SHADE[2] - WOOD_HI[2]) * t),
        )
        cradle.fill(c + (255,), pygame.Rect(0, y, S, 1))
    # Mid-band of the base wood tone so the cradle holds one readable brown core.
    cradle.fill(WOOD + (255,), pygame.Rect(0, int(g0 + (g1 - g0) * 0.32),
                                           S, int((g1 - g0) * 0.30)))
    cmask = pygame.Surface((S, S), pygame.SRCALPHA)
    pygame.draw.polygon(cmask, (255, 255, 255, 255), cradle_poly)
    cradle.blit(cmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(cradle, (0, 0))

    # ONE committed centre stave-seam (the ±side seams aliased to mud at 22px and
    # are dropped). Runs from the top horns down to just above the iron hoop so the
    # hoop stays one clean unbroken band.
    seam_bot = cradle_bot - 7
    pygame.draw.line(surf, WOOD_SHADE, (cx, cradle_top - 1), (cx, seam_bot), 1)

    # ---- IRON HOOP: a FAT cool-grey band crossing the visible FRONT belly of the
    # cradle — the beat that says "barrel hoop", not "dark base", so it is pushed
    # UP onto the belly (not the bottom lip) and made a thick ~4px band with a
    # bright 2px top edge so it survives the bank at every tilt as a metal hoop. ----
    hoop_y = cradle_bot - 7                  # pushed up onto the belly
    pygame.draw.line(surf, IRON, (cr_l + 2, hoop_y),
                     (cr_r - 2, hoop_y), 4)
    pygame.draw.line(surf, IRON_HI, (cr_l + 2, hoop_y - 2),
                     (cr_r - 2, hoop_y - 2), 2)

    # ---- NIGHT lifeline keylines INSIDE the outline. The warm amber rim traces
    # the BOTTLE ONLY (cork + body) — tracing it on the wood made the cradle glow
    # amber and erased the wood/glass split. The cradle gets its OWN cooler/darker
    # desaturated-tan rim so it stays read-apart wood on dark sky. ----
    pygame.draw.rect(surf, KEYLINE, body_rect, width=1, border_radius=body_rad)
    pygame.draw.rect(surf, KEYLINE, cork_rect, width=1, border_radius=2)
    pygame.draw.polygon(surf, KEYLINE_WOOD, cradle_poly, width=1)

    if icon_size:
        return pygame.transform.smoothscale(surf, (icon_size, icon_size))
    return pygame.transform.smoothscale(surf, (22, 22))
