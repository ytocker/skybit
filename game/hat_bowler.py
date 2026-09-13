import math

import pygame


# Bowler reads as itself through pure geometry: a hard semicircular dome over a
# short brim that kettle-curls up at both ends. Everything is derived from head_w
# so the silhouette holds whether the head is 80px or 18px wide.
def draw_hat(surf, cx, base_y, head_w, facing=1):
    """Draw a side-profile BOWLER hat sized for a head of width head_w, centered at cx, brim line at base_y."""
    cx = int(cx)
    base_y = int(base_y)

    # Warm chestnut felt: lifted one step brighter than chocolate so the rounded
    # dome separates cleanly from the dark-navy store card instead of dissolving
    # into it at small sizes.
    felt = (96, 62, 44)
    felt_dark = (60, 38, 26)
    band = (34, 21, 15)
    sheen = (176, 138, 110)
    rim = (188, 150, 122)

    # A bowler crown is SHORT — a true half-circle rather than a tall cylinder.
    # Dome width tracks the head; height is kept under half the width so it never
    # creeps toward top-hat proportions.
    dome_w = head_w * 0.78
    dome_h = dome_w * 0.46
    dome_left = cx - dome_w / 2.0
    dome_top = base_y - dome_h

    # Brim is narrow and overhangs the dome only slightly; its tips kettle-curl
    # UP hard — that curl is the bowler's signature, so it is deliberately
    # exaggerated to survive down to an 18px head.
    brim_half = dome_w / 2.0 + max(2.0, head_w * 0.13)
    brim_thick = max(2.0, head_w * 0.07)
    curl = max(3.0, head_w * 0.20)

    # ---- Brim: a flattened ellipse whose ends lift, drawn as a filled poly so
    # the upward kettle-curl is explicit instead of a straight slab. A high power
    # on the edge term keeps the middle flat and snaps the very tips upward.
    steps = 28
    top_pts = []
    bot_pts = []
    for i in range(steps + 1):
        t = i / steps
        x = cx - brim_half + t * (2 * brim_half)
        # Quartic edge term: middle stays near base_y, only the outer tips lift.
        edge = (2 * t - 1) ** 4
        lift = curl * edge
        top_pts.append((x, base_y - lift))
        # Underside thins toward the tips so the curl reads as a rolled rim.
        bot_pts.append((x, base_y + brim_thick - lift * 0.85))
    brim_poly = top_pts + bot_pts[::-1]
    pygame.draw.polygon(surf, felt_dark, brim_poly)

    # Thin top sliver of the brim catches a touch of light so it doesn't read as
    # a single dark mass against the dome.
    pygame.draw.lines(surf, felt, False, top_pts, max(1, int(head_w * 0.025)))

    # ---- Crown: a half-disc. The full ellipse is twice as tall as the dome, and
    # a clip rect restricts it to the upper half so the result is a hard rounded
    # dome seated exactly on the brim line — no flat cap, no lower bulge.
    dome_rect = pygame.Rect(int(dome_left), int(dome_top), int(dome_w), int(round(dome_h * 2)))
    prev_clip = surf.get_clip()
    surf.set_clip(pygame.Rect(int(dome_left) - 1, int(dome_top) - 1, int(dome_w) + 2, int(dome_h) + 2))
    pygame.draw.ellipse(surf, felt, dome_rect)

    # ---- Rim-light: a thin bright arc tracing the upper-left of the dome,
    # drawn slightly inset from the silhouette. This crisp light edge is what
    # gives the round crown card-separation against the dark navy background.
    rim_w = max(1, int(round(head_w * 0.045)))
    rim_inset = max(0.5, head_w * 0.015)
    rim_rect = pygame.Rect(
        int(dome_left + rim_inset),
        int(dome_top + rim_inset),
        int(dome_w - 2 * rim_inset),
        int(round((dome_h - rim_inset) * 2)),
    )
    if rim_rect.width >= 3 and rim_rect.height >= 3:
        # Upper-left quadrant of the dome arc (pygame angles run CCW from +x).
        pygame.draw.arc(surf, rim, rim_rect, math.pi / 2, math.pi, rim_w)
    surf.set_clip(prev_clip)

    # ---- Band: a darker ribbon hugging the base of the dome, clipped to the
    # dome's footprint so it follows the curved sides rather than overhanging.
    band_h = max(1.5, dome_h * 0.18)
    band_w = dome_w * 0.96
    band_rect = pygame.Rect(int(cx - band_w / 2), int(base_y - band_h), int(band_w), int(round(band_h)))
    pygame.draw.rect(surf, band, band_rect)

    # ---- Sheen: an off-centre soft highlight arc on the upper dome, the classic
    # polished-felt glint. Mirrors with facing.
    sheen_cx = cx + facing * dome_w * 0.16
    sheen_w = dome_w * 0.28
    sheen_h = dome_h * 0.5
    sheen_rect = pygame.Rect(
        int(sheen_cx - sheen_w / 2),
        int(dome_top + dome_h * 0.12),
        int(sheen_w),
        int(sheen_h * 2),
    )
    if sheen_rect.width >= 2 and sheen_rect.height >= 2:
        sheen_surf = pygame.Surface((sheen_rect.width, sheen_rect.height), pygame.SRCALPHA)
        pygame.draw.ellipse(sheen_surf, (*sheen, 95), sheen_surf.get_rect())
        surf.blit(sheen_surf, sheen_rect.topleft)

    # Subtle inner edge along the dome's lower band gives a felt thickness cue.
    pygame.draw.line(
        surf, felt_dark,
        (int(dome_left + dome_w * 0.06), base_y - band_h),
        (int(dome_left + dome_w * 0.94), base_y - band_h),
        max(1, int(head_w * 0.02)),
    )
