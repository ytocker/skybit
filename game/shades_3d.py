"""SHADES style `shades_3d` — retro anaglyph cinema glasses (PLASTIC).

The two-colour lens pair is the whole read: the EAR-side (far/back) lens is
RED, the BEAK-side (front/near) lens is CYAN, matching how anaglyph glasses
sit on a face. Pip faces RIGHT (facing=1) so cyan is to the right and the
plastic temple arm runs left toward the ear.

A thin DARK plastic frame rings every lens and runs as a divider down the
bridge: on a scarlet parrot head the RED lens would otherwise melt into the
head, so the black outline is what gives it an edge, and it lets the CYAN
read crisp beside it. The cyan film is pushed bright so the colour split is
unmistakable even at eye_w=22. Everything scales off `eye_w` so the look
holds from a 96px product shot down to a 22px in-game sprite.
"""
import pygame

# Anaglyph film — cyan pushed bright so the red/cyan split never collapses,
# and so the cyan lens visibly pops against the dark frame at 22px.
_RED      = (228, 36, 50)
_RED_H    = (255, 132, 138)
_CYAN     = (44, 226, 246)
_CYAN_H   = (190, 252, 255)
_GLINT    = (255, 255, 255)

# Thin black/charcoal plastic frame — the dark edge that keeps the red lens
# from camouflaging on the scarlet head and divides the two lenses.
_FRAME    = (26, 28, 34)
_FRAME_HI = (96, 100, 112)   # top-edge catch-light so the plastic reads round


def draw_shades(surf, cx, cy, eye_w, facing=1):
    f = facing
    # Narrowed from 0.44/0.50: the wide anaglyph pair pushed the cyan (near) lens
    # right over the beak. A tighter lens + tighter spacing keeps the two-colour
    # read while the front lens stays off the beak.
    lw = max(5, int(eye_w * 0.36))
    lh = max(5, int(eye_w * 0.38))
    sep = max(6, int(eye_w * 0.42))
    rad = max(1, int(eye_w * 0.09))
    # Frame ring thickness — kept >=2 so the divider survives at eye_w=22.
    fr = max(2, int(eye_w * 0.085))

    # Seat the pair on the eye but ride it slightly FORWARD so the near (cyan)
    # lens laps the beak base naturally; a modest lift keeps it off the beak tip.
    cy = cy - max(1, int(eye_w * 0.07))
    near = (cx + f * (sep // 2) + f * max(1, int(eye_w * 0.03)), cy)  # BEAK side -> cyan
    far = (cx - f * (sep // 2), cy)       # EAR side  -> red

    for (lx, ly), lens_c, lens_h in (
            (far, _RED, _RED_H), (near, _CYAN, _CYAN_H)):
        # Dark plastic frame drawn as a filled rounded rect under the film,
        # so every lens carries its own outline against head and sky.
        frame = pygame.Rect(0, 0, lw + fr * 2, lh + fr * 2)
        frame.center = (lx, ly)
        pygame.draw.rect(surf, _FRAME, frame, border_radius=rad + fr)
        # Coloured film sits inside the ring.
        inner = pygame.Rect(0, 0, lw, lh)
        inner.center = (lx, ly)
        pygame.draw.rect(surf, lens_c, inner, border_radius=rad)
        # Top-inner band lightens the film so it reads as lit glass, not paint.
        band = inner.inflate(-fr, -lh // 2)
        band.bottom = inner.centery
        pygame.draw.rect(surf, lens_h, band, border_radius=max(1, rad // 2))
        # '/' sheen + corner glint so the film looks lit on both lenses.
        pygame.draw.line(surf, _GLINT,
                         (lx - lw * 0.22, ly + lh * 0.18),
                         (lx + lw * 0.16, ly - lh * 0.24),
                         max(1, int(eye_w * 0.05)))
        pygame.draw.circle(surf, _GLINT,
                           (int(lx - lw * 0.24), int(ly - lh * 0.22)),
                           max(1, int(eye_w * 0.05)))
        # Thin top catch-light on the frame so the plastic looks rounded.
        pygame.draw.line(surf, _FRAME_HI,
                         (frame.left + rad, frame.top + max(1, fr // 2)),
                         (frame.right - rad, frame.top + max(1, fr // 2)),
                         max(1, fr // 2))

    # Dark plastic bridge — also the divider that separates the two lenses.
    pygame.draw.line(surf, _FRAME,
                     (far[0] + f * (lw // 2), cy - lh // 8),
                     (near[0] - f * (lw // 2), cy - lh // 8),
                     fr + 1)

    # Dark plastic temple arm hinging toward the ear.
    arm_root = (far[0] - f * (lw // 2 + fr), cy - lh // 5)
    arm_end = (far[0] - f * (lw // 2 + max(3, int(eye_w * 0.32))),
               cy - max(2, int(eye_w * 0.14)))
    pygame.draw.line(surf, _FRAME, arm_root, arm_end, max(2, fr))
