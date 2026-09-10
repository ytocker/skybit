"""LOVE LETTER — ENVELOPE parcel cosmetic.

A sweet sealed billet-doux. A ~22px flat slab that must survive Pip's bank
without collapsing into "a card". Three things carry the read at true size: the
rose flap V (the envelope cue), one unbroken CREAM band across the lower third
(the letter inside), and the glossy red HEART seated on that band like a wax
seal. The heart is value-separated by a cream halo ring so it survives even in
grayscale — the identity can't ride on hue alone. Built on a 44px work surface
then smoothscaled to 22 with a baked dark outline for DAY sky and a warm keyline
for NIGHT.
"""
import pygame

from game.draw import lerp_color as _lerp_color

# DAY blush body / rose flap / red heart, plus a warm keyline so the slab still
# reads against a dark sky without changing the sprite per mode.
PINK_HI = (247, 197, 207)      # top of body gradient
PINK_BASE = (244, 184, 196)    # body
PINK_SHADE = (224, 156, 170)   # lower body, gives the slab volume
ROSE_FLAP = (217, 126, 146)    # closing flap V
# Deepened so the right-half crease reads as a clearly darker wedge at 22px —
# the fold is what sells "envelope" on the gameplay sprite, not just up close.
ROSE_FLAP_SHADE = (168, 88, 108)
CREAM = (246, 233, 221)        # the letter band + heart halo
CREAM_HI = (252, 244, 236)     # halo lift, lighter than the band so it pops
HEART = (216, 58, 74)          # wax-seal red
HEART_HI = (240, 120, 132)     # glossy lift
HEART_SHADE = (162, 38, 52)
OUTLINE = (90, 42, 51)         # dark, reads on bright day sky
KEYLINE = (250, 214, 222)      # warm blush rim — the NIGHT lifeline


def build(mode="normal", icon_size: int = 0) -> pygame.Surface:
    # Mode-agnostic: one static slab sprite for every Pip skin.
    S = 44
    surf = pygame.Surface((S, S), pygame.SRCALPHA)

    # Slab body, kept well off the surface edges so the gameplay rotozoom never
    # clips the corners at any bank angle.
    BW, BH = 34, 26
    cx, cy = S // 2, S // 2
    rect = pygame.Rect(cx - BW // 2, cy - BH // 2, BW, BH)
    rad = 4

    # Rounded-rect mask reused for body + cream band so every fill stays inside
    # the same silhouette and the corners never sprout detached blobs.
    mask = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(),
                     border_radius=rad)

    # Baked outline frame (drawn first, slightly inflated) — the dark silhouette
    # that survives on the bright day sky.
    pygame.draw.rect(surf, OUTLINE, rect.inflate(6, 6), border_radius=rad + 2)

    # Blush body: gentle vertical gradient masked to the rounded rect, giving the
    # flat card a touch of volume so it never reads as a paper cut-out.
    body = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    for y in range(rect.h):
        t = y / max(1, rect.h - 1)
        row = _lerp_color(PINK_HI, PINK_SHADE, t)
        body.fill(row + (255,), pygame.Rect(0, y, rect.w, 1))
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(body, rect.topleft)

    # CREAM letter band — one unbroken horizontal stripe across the lower third
    # of the body, masked to the rounded rect. A single band (not a pentagon)
    # survives rotation as one shape instead of breaking into corner blobs, and
    # gives the heart a light seat to sit on.
    band = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    band_top = int(rect.h * 0.60)
    pygame.draw.rect(band, CREAM + (255,),
                     pygame.Rect(0, band_top, rect.w, rect.h - band_top))
    band.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(band, rect.topleft)
    # Thin dark seam along the band's top edge so flap and letter separate
    # crisply even when colour washes out.
    pygame.draw.line(surf, OUTLINE,
                     (rect.x + 1, rect.y + band_top),
                     (rect.right - 2, rect.y + band_top), 1)

    # Closing flap — a downward V from the two top corners to the flap point at
    # centre, filling the body ABOVE the cream band. Dark under-edge first (its
    # own outline over the body), then the rose fill, then a deeper shade wedge
    # on the right half so the fold catches less light. This V is the envelope.
    top_l = (rect.x + 1, rect.y + 1)
    top_r = (rect.right - 1, rect.y + 1)
    flap_pt = (cx, rect.y + band_top - 1)

    pygame.draw.polygon(surf, OUTLINE,
                        [(top_l[0] - 1, top_l[1] - 1),
                         (top_r[0] + 1, top_r[1] - 1),
                         (flap_pt[0], flap_pt[1] + 1)])
    pygame.draw.polygon(surf, ROSE_FLAP, [top_l, top_r, flap_pt])
    # Right-half shade wedge = the fold crease catching less light.
    pygame.draw.polygon(surf, ROSE_FLAP_SHADE,
                        [(cx, top_l[1]), top_r, flap_pt])

    # The two diagonal seams of the V at full 1px outline weight so the crease
    # edge is crisp at 22px — the fold must read on the gameplay sprite.
    pygame.draw.line(surf, OUTLINE, (top_l[0] + 1, top_l[1]), flap_pt, 1)
    pygame.draw.line(surf, OUTLINE, (top_r[0] - 1, top_r[1]), flap_pt, 1)

    # Warm keyline rim INSIDE the outline — a glowing blush edge on night sky,
    # subtle on day. Drawn after the flap so the whole closed shape is ringed.
    pygame.draw.rect(surf, KEYLINE, rect, width=1, border_radius=rad)

    # HEART wax seal — the identity. Built BOLD from two lobe circles + a lower
    # point triangle so it reads as a HEART, not a dot, after the smoothscale to
    # 22px. Seated ~1px below the flap seam so it sits ON the cream band like a
    # wax seal closing the envelope. A CREAM halo ring outside the dark outline
    # value-separates it: heart-red and rose collapse to the same gray, so
    # without the light ring the heart vanishes in grayscale.
    hcx, hcy = cx, flap_pt[1] + 3     # dropped onto the cream band
    lobe_r = 4                        # bold enough to read as a heart at 22px
    lobe_dx = 3
    bottom = (hcx, hcy + 8)

    def _heart(color, cxx, cyy, lr, dx, bot):
        pygame.draw.circle(surf, color, (cxx - dx, cyy), lr)
        pygame.draw.circle(surf, color, (cxx + dx, cyy), lr)
        pygame.draw.polygon(surf, color,
                            [(cxx - dx - lr + 1, cyy + 1),
                             (cxx + dx + lr - 1, cyy + 1),
                             bot])

    # Light halo ring (largest) so the heart pops by VALUE on every background,
    # then the dark outline, then the red fill.
    _heart(CREAM_HI, hcx, hcy, lobe_r + 2, lobe_dx, (bottom[0], bottom[1] + 2))
    _heart(OUTLINE, hcx, hcy, lobe_r + 1, lobe_dx, (bottom[0], bottom[1] + 1))
    _heart(HEART, hcx, hcy, lobe_r, lobe_dx, bottom)
    # Lower-right shade lobe for a waxy 3D bead read.
    pygame.draw.circle(surf, HEART_SHADE, (hcx + lobe_dx, hcy + 1), lobe_r - 1)
    pygame.draw.polygon(surf, HEART_SHADE,
                        [(hcx, hcy + 1), (hcx + lobe_dx + lobe_r - 1, hcy + 1),
                         bottom])
    # Re-lay the red core so the shade only darkens the rim, keeping it red.
    pygame.draw.circle(surf, HEART, (hcx - lobe_dx, hcy), lobe_r - 1)
    pygame.draw.circle(surf, HEART, (hcx + lobe_dx, hcy), lobe_r - 2)
    pygame.draw.polygon(surf, HEART,
                        [(hcx - lobe_dx - lobe_r + 2, hcy + 1),
                         (hcx + lobe_dx + lobe_r - 3, hcy + 1),
                         (bottom[0], bottom[1] - 1)])
    # Glossy sheen on the upper-left lobe = wax catching light.
    pygame.draw.circle(surf, HEART_HI, (hcx - lobe_dx - 1, hcy - 1), 1)

    if icon_size:
        return pygame.transform.smoothscale(surf, (icon_size, icon_size))
    return pygame.transform.smoothscale(surf, (22, 22))
