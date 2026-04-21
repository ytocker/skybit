"""
Vivid scarlet-macaw parrot, pre-rendered to 4 animation frames.
Wing cycle:   0 up   1 mid-up   2 level   3 down
Drawn once at import with smooth alpha surfaces — no pixel art.
"""
import math
import pygame

from game.draw import (
    BIRD_RED, BIRD_RED_D, BIRD_WING, BIRD_WING_D, BIRD_TIP,
    BIRD_BELLY, BIRD_BEAK, BIRD_BEAK_D, WHITE, BLACK, NEAR_BLACK,
)

SPRITE_W, SPRITE_H = 60, 56


def _aaellipse(surf, color, center, rx, ry):
    """Filled antialiased ellipse."""
    cx, cy = center
    rect = pygame.Rect(int(cx - rx), int(cy - ry), int(rx * 2), int(ry * 2))
    pygame.draw.ellipse(surf, color, rect)


def _build_wing(angle_deg):
    """Wing polygon rotated around its shoulder anchor."""
    w = pygame.Surface((44, 44), pygame.SRCALPHA)
    # Main wing feather layer (blue)
    pts = [
        (22, 22),
        (40, 14),
        (42, 26),
        (30, 38),
        (18, 34),
    ]
    pygame.draw.polygon(w, BIRD_WING, pts)
    # Shadow underside
    spts = [
        (22, 22),
        (30, 38),
        (18, 34),
    ]
    pygame.draw.polygon(w, BIRD_WING_D, spts)
    # Primary feather tips (green)
    pygame.draw.polygon(w, BIRD_TIP, [
        (40, 14),
        (44, 18),
        (42, 26),
    ])
    # Feather divider lines
    pygame.draw.line(w, BIRD_WING_D, (24, 24), (38, 18), 2)
    pygame.draw.line(w, BIRD_WING_D, (26, 28), (40, 24), 2)
    pygame.draw.line(w, BIRD_WING_D, (28, 32), (40, 30), 2)
    return pygame.transform.rotate(w, angle_deg)


def _build_frame(wing_angle_deg):
    surf = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)

    # Tail feathers (behind everything)
    tail_colors = [
        (255, 180,  60),
        (255, 120,  60),
        (230,  60,  60),
    ]
    for i, c in enumerate(tail_colors):
        pts = [
            (4 + i * 2, 26 + i * 2),
            (14, 24 + i),
            (18, 30 + i * 2),
            (6 + i * 2, 34 + i * 2),
        ]
        pygame.draw.polygon(surf, c, pts)
    pygame.draw.line(surf, BIRD_RED_D, (6, 26), (16, 30), 1)

    # Body shadow
    _aaellipse(surf, BIRD_RED_D, (32, 32), 18, 14)
    # Body base
    _aaellipse(surf, BIRD_RED,   (30, 30), 18, 14)
    # Belly highlight
    _aaellipse(surf, BIRD_BELLY, (28, 36), 11, 6)

    # Wing (dynamic)
    wing = _build_wing(wing_angle_deg)
    wr = wing.get_rect(center=(34, 26))
    surf.blit(wing, wr.topleft)

    # Head
    _aaellipse(surf, BIRD_RED_D, (47, 22), 11, 10)
    _aaellipse(surf, BIRD_RED,   (46, 21), 11, 10)
    # Cheek highlight
    _aaellipse(surf, (255, 120, 120), (44, 24), 4, 3)

    # Eye ring
    pygame.draw.circle(surf, WHITE,      (50, 19), 4)
    pygame.draw.circle(surf, NEAR_BLACK, (50, 19), 4, 1)
    # Pupil
    pygame.draw.circle(surf, BLACK,      (51, 19), 2)
    # Eye highlight
    pygame.draw.circle(surf, WHITE,      (52, 18), 1)

    # Beak (hooked)
    beak_pts = [
        (54, 20),
        (59, 22),
        (57, 26),
        (52, 25),
    ]
    pygame.draw.polygon(surf, BIRD_BEAK, beak_pts)
    pygame.draw.polygon(surf, BIRD_BEAK_D, beak_pts, 1)
    # Beak lower line
    pygame.draw.line(surf, BIRD_BEAK_D, (52, 23), (57, 24), 1)

    # Small foot tuck
    pygame.draw.line(surf, BIRD_BEAK_D, (28, 43), (26, 47), 2)
    pygame.draw.line(surf, BIRD_BEAK_D, (34, 43), (36, 47), 2)

    return surf


# Four wing angles — up, mid-up, level, down
_WING_ANGLES = (50, 20, -10, -40)
FRAMES: list[pygame.Surface] = [_build_frame(a) for a in _WING_ANGLES]


_rot_cache: dict = {}


def get_parrot(frame_idx: int, tilt_deg: float) -> pygame.Surface:
    """Return rotated parrot surface, cached by (frame, rounded-angle)."""
    frame_idx = frame_idx % len(FRAMES)
    key = (frame_idx, int(round(tilt_deg / 3.0)) * 3)
    s = _rot_cache.get(key)
    if s is None:
        s = pygame.transform.rotozoom(FRAMES[frame_idx], key[1], 1.0)
        _rot_cache[key] = s
    return s
