"""Knight + 3x — the royal METALLIC CROWN crest.

When the survive-one-hit KNIGHT skin overlaps the 3x-coins buff, Pip wears a
gold royal crown that reads as PART of the steel armour (not a civilian top
hat). Art-director-approved "CORONET x CIRCLET hybrid", variant A: a thick
rounded-bevel warm-gold band + three fat triangular points + one faceted ruby,
seated low/back so the armet's crimson plume rises cleanly behind it.

The crown is composited onto the FLAT knight frame at the helm anchor, so the
per-tilt rotozoom in `parrot.get_knight_hat_parrot` banks crown + bird together.
Procedural; native + WASM safe. Gold is a half-step warmer/brighter than the
helm BRASS so it reads as a richer royal gold yet the same gold-on-steel family.
"""
import pygame

# Band gold ramp (seat-shadow -> bevel-dark -> warm core -> lit -> specular).
G_SEAT = (88, 60, 22)
G_DK = (150, 110, 42)
G_MID = (222, 180, 92)
G_LT = (244, 212, 132)
G_HI = (255, 238, 174)
G_GLINT = (255, 252, 228)
# Single faceted ruby — warm, colourblind-safe (no red/green adjacency).
RUBY = (196, 38, 54)
RUBY_DK = (118, 16, 30)
RUBY_LT = (236, 92, 96)
RUBY_HI = (255, 168, 174)


def _ruby_gem(surf, cx, cy, r):
    """Faceted ruby set into the band face, lit from the upper-left to match
    the helm: dark bezel, a 2-value body (deeper lower-right, brighter
    upper-left), one white spark — what makes a 4-5px stone read as cut."""
    pygame.draw.circle(surf, RUBY_DK, (cx, cy), r + 1)
    pygame.draw.circle(surf, RUBY, (cx, cy), r)
    pygame.draw.circle(surf, RUBY_LT, (cx - 1, cy - 1), max(1, r - 1))
    pygame.draw.circle(surf, RUBY_HI, (cx - 1, cy - 1), max(1, r // 2))
    surf.set_at((cx - 1, cy - 1), (255, 255, 255))


def _band(surf, x0, x1, y, h):
    """Thick coronet band with a rounded bevel: a top->bottom value ramp (dark
    bottom edge, warm core, lit top row, upper-left specular) so it reads as a
    curved armour ring catching upper-left light, never a flat painted strip."""
    w = x1 - x0
    pygame.draw.rect(surf, G_SEAT, (x0, y + h, w, 1))
    pygame.draw.rect(surf, G_DK, (x0, y, w, h))
    pygame.draw.rect(surf, G_MID, (x0 + 1, y + 1, w - 2, h - 2))
    pygame.draw.rect(surf, G_LT, (x0 + 1, y + 1, w - 2, 2))
    pygame.draw.rect(surf, G_HI, (x0 + 2, y + 1, w - 4, 1))
    surf.set_at((x0 + 3, y + 1), G_GLINT)
    surf.set_at((x0 + 2, y + 2), G_GLINT)


def _fat_point(surf, cx, base_y, top_y, half):
    """A fat, clearly triangular gold point (base = 2*half): dark bevel
    triangle, warm core inset off the right/under edges, a lit upper-left face
    climbing to the tip, a glint pip. No thin spikes (they vanish on downscale).
    The right edge is kept on the dark bevel so all three points share one clean
    triangular silhouette."""
    pygame.draw.polygon(surf, G_DK, [(cx - half, base_y), (cx + half, base_y),
                                     (cx, top_y)])
    pygame.draw.polygon(surf, G_MID, [(cx - half + 1, base_y),
                                      (cx + half - 1, base_y), (cx, top_y + 2)])
    pygame.draw.polygon(surf, G_LT, [(cx - half + 1, base_y),
                                     (cx - half + 2, base_y), (cx, top_y + 2),
                                     (cx, top_y + 3)])
    pygame.draw.line(surf, G_HI, (cx - half + 2, base_y - 1), (cx, top_y + 1), 1)
    surf.set_at((cx, top_y + 1), G_GLINT)


def _crown(surf, cx, cy):
    """Variant A — the shipped royal crown: thick warm-gold band + three fat
    points (centre tallest) + one centred ruby. Points drawn UNDER the band so
    the band's lit top edge crosses cleanly in front of each base (the points
    read as rising FROM the ring)."""
    half = 11
    h = 7
    by = cy
    for dx, ph, hw in ((-8, 6, 3), (0, 9, 3), (8, 6, 3)):
        _fat_point(surf, cx + dx, by + 2, by - ph, hw)
    _band(surf, cx - half, cx + half, by, h)
    _ruby_gem(surf, cx, by + h // 2 + 1, 2)


def crown_frames(knight_frames):
    """Composite the royal crown onto each of the given knight frames at the
    helm dome anchor (helm at ~0.73 x / 0.17 y of the sprite; crown seated ~2px
    lower + 1px back so the plume clears behind it). Anchored RELATIVE TO EACH
    FRAME'S CENTRE so it lands correctly whether the frame is the standard knight
    or the larger, thick-battered fried knight (which sits on a bigger canvas).
    Reusable across the plain knight and the themed (fried/spectral) knights."""
    from game import parrot
    # Offset of the helm anchor from the frame centre, derived from the standard
    # layout (PAD=16): helm_cx = PAD + 0.73*W, helm_cy = PAD - 0.10*H + 7.
    dx = int(0.23 * parrot.SPRITE_W) - 1
    dy = int(-0.60 * parrot.SPRITE_H) + 7
    out = []
    for frame in knight_frames:
        f = frame.copy()
        _crown(f, f.get_width() // 2 + dx, f.get_height() // 2 + dy)
        out.append(f)
    return out


def build_knight_hat_frames():
    from game.knight_skin import build_knight_frames
    return crown_frames(build_knight_frames())


def build_knight_kfc_hat_frames():
    # Crown the NORMAL-size fried knight, then plump knight + crown together so
    # the crown seats correctly and scales with the bigger fried knight.
    from game.knight_skin import fried_knight_core_frames, plump_frames
    return plump_frames(crown_frames(fried_knight_core_frames()))


def build_knight_ghost_hat_frames():
    from game.knight_skin import build_knight_ghost_frames
    return crown_frames(build_knight_ghost_frames())


def build_knight_kfc_ghost_hat_frames():
    # Crown the NORMAL-size spectral fried knight, then plump together (matches
    # the kfc_hat ordering so the crown seats + scales on the bigger fried base).
    from game.knight_skin import fried_ghost_knight_core_frames, plump_frames
    return plump_frames(crown_frames(fried_ghost_knight_core_frames()))
