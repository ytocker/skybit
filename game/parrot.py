"""
Stylish scarlet-macaw with aviator sunglasses — 4 pre-rendered wing frames.
Everything is drawn procedurally once at import with smooth alpha surfaces
(no pixel art). `get_parrot(frame_idx, tilt_deg)` returns a rotated surface,
cached by (frame, rounded-angle).
"""
import math
import pygame

from game.draw import (
    BIRD_RED, BIRD_RED_D, BIRD_WING, BIRD_WING_D, BIRD_TIP,
    BIRD_BELLY, BIRD_BEAK, BIRD_BEAK_D, WHITE, BLACK, NEAR_BLACK,
)

SPRITE_W, SPRITE_H = 64, 60

# Shade palette
SHADE_BLACK   = (15, 15, 25)
SHADE_FRAME   = (255, 200, 50)     # gold aviator rim
SHADE_GLINT   = (255, 255, 255)
SHADE_TINT    = (35, 55, 90)       # reflected-sky blue on the lens


def _aaellipse(surf, color, center, rx, ry):
    cx, cy = center
    rect = pygame.Rect(int(cx - rx), int(cy - ry), int(rx * 2), int(ry * 2))
    pygame.draw.ellipse(surf, color, rect)


def _build_wing(angle_deg):
    """Wing polygon rotated around its shoulder anchor."""
    w = pygame.Surface((50, 50), pygame.SRCALPHA)
    # Drop shadow outline
    shadow_pts = [
        (24, 26), (46, 14), (50, 30), (34, 44), (18, 40),
    ]
    pygame.draw.polygon(w, (0, 0, 0, 110), shadow_pts)

    # Main wing feather layer (vivid blue)
    pts = [
        (24, 24), (44, 13), (48, 28), (32, 42), (18, 36),
    ]
    pygame.draw.polygon(w, BIRD_WING, pts)

    # Darker underside
    spts = [
        (24, 24), (32, 42), (18, 36),
    ]
    pygame.draw.polygon(w, BIRD_WING_D, spts)

    # Primary feather tips (green — macaw signature)
    pygame.draw.polygon(w, BIRD_TIP, [
        (44, 13), (50, 18), (48, 28),
    ])
    # A yellow secondary between blue & green for that scarlet-macaw stripe
    pygame.draw.polygon(w, (255, 200, 60), [
        (42, 18), (48, 22), (46, 28), (40, 24),
    ])

    # Feather divider lines
    pygame.draw.line(w, BIRD_WING_D, (26, 25), (42, 18), 2)
    pygame.draw.line(w, BIRD_WING_D, (28, 30), (44, 25), 2)
    pygame.draw.line(w, BIRD_WING_D, (30, 34), (46, 32), 2)
    # Crisp highlight edge
    pygame.draw.line(w, (170, 210, 255), (25, 25), (41, 15), 1)
    return pygame.transform.rotate(w, angle_deg)


def _draw_sunglasses(surf, cx, cy):
    """Aviator shades: two teardrop lenses joined by a gold bridge, with a
    tiny gold nose pad and a white sunlight glint on each lens."""
    # Lens geometry (relative to sprite)
    r_outer = 6
    # Left lens slightly back, right slightly forward because of the head tilt
    left  = (cx - 4, cy)
    right = (cx + 6, cy - 1)

    # Gold frame (outer)
    pygame.draw.circle(surf, SHADE_FRAME, left, r_outer + 1)
    pygame.draw.circle(surf, SHADE_FRAME, right, r_outer + 1)
    # Black lens body
    pygame.draw.circle(surf, SHADE_BLACK, left, r_outer)
    pygame.draw.circle(surf, SHADE_BLACK, right, r_outer)
    # Subtle sky-tint reflected on each lens (upper half)
    tint = pygame.Surface((r_outer * 2, r_outer), pygame.SRCALPHA)
    pygame.draw.ellipse(tint, (*SHADE_TINT, 130), tint.get_rect())
    surf.blit(tint, (left[0] - r_outer, left[1] - r_outer + 1))
    surf.blit(tint, (right[0] - r_outer, right[1] - r_outer + 1))
    # Bright white glint
    pygame.draw.circle(surf, SHADE_GLINT, (left[0] - 2, left[1] - 2), 2)
    pygame.draw.circle(surf, SHADE_GLINT, (right[0] - 2, right[1] - 3), 2)
    # Thin secondary glint
    pygame.draw.circle(surf, (255, 255, 255, 200), (left[0] + 2, left[1] + 2), 1)
    pygame.draw.circle(surf, (255, 255, 255, 200), (right[0] + 2, right[1] + 1), 1)

    # Gold bridge
    pygame.draw.line(surf, SHADE_FRAME, (left[0] + r_outer, left[1]), (right[0] - r_outer, right[1]), 2)
    # Top brow-bar (aviator double-bar)
    pygame.draw.line(surf, SHADE_FRAME,
                     (left[0] - r_outer + 1, left[1] - r_outer + 2),
                     (right[0] + r_outer - 1, right[1] - r_outer + 2), 1)


def _build_frame(wing_angle_deg):
    surf = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)

    # Tail: layered feather fan, vivid red→orange→yellow
    tail_colors = [
        (200,  30,  40),
        (240,  95,  40),
        (255, 160,  55),
        (255, 220,  80),
    ]
    for i, c in enumerate(tail_colors):
        pts = [
            (2 + i * 3, 26 + i * 2),
            (14 + i, 24 + i),
            (20 + i, 30 + i * 2),
            (6 + i * 3, 36 + i * 2),
        ]
        pygame.draw.polygon(surf, c, pts)
    # Tail divider lines
    pygame.draw.line(surf, BIRD_RED_D, (4, 27), (18, 31), 1)
    pygame.draw.line(surf, BIRD_RED_D, (6, 33), (20, 35), 1)

    # Body shadow (soft drop)
    _aaellipse(surf, (120, 20, 25), (34, 35), 19, 14)
    # Body base
    _aaellipse(surf, BIRD_RED, (32, 32), 19, 14)
    # Chest feather texture: a second ellipse blend
    _aaellipse(surf, (255, 100, 100), (30, 29), 13, 8)
    # Belly highlight
    _aaellipse(surf, BIRD_BELLY, (28, 38), 12, 6)
    # Glossy top sheen
    sheen = pygame.Surface((28, 6), pygame.SRCALPHA)
    pygame.draw.ellipse(sheen, (255, 230, 230, 160), sheen.get_rect())
    surf.blit(sheen, (22, 21))

    # Wing (dynamic, behind head but over body)
    wing = _build_wing(wing_angle_deg)
    wr = wing.get_rect(center=(34, 28))
    surf.blit(wing, wr.topleft)

    # Head shadow
    _aaellipse(surf, (150, 15, 20), (48, 23), 12, 11)
    # Head base
    _aaellipse(surf, BIRD_RED, (47, 21), 12, 11)
    # Cheek flush
    _aaellipse(surf, (255, 130, 130), (44, 24), 4, 3)
    # Crown highlight
    _aaellipse(surf, (255, 170, 170), (46, 16), 7, 3)

    # Aviator sunglasses (replaces the plain eye)
    _draw_sunglasses(surf, 50, 20)

    # Beak — hooked, with a glossy highlight
    beak_pts = [
        (55, 21), (61, 24), (58, 28), (52, 26),
    ]
    pygame.draw.polygon(surf, BIRD_BEAK, beak_pts)
    pygame.draw.polygon(surf, BIRD_BEAK_D, beak_pts, 1)
    # Beak gloss
    pygame.draw.line(surf, (255, 230, 150), (55, 22), (59, 24), 1)
    # Lower-beak split line
    pygame.draw.line(surf, BIRD_BEAK_D, (52, 24), (58, 25), 1)

    # Feet tucks
    pygame.draw.line(surf, BIRD_BEAK_D, (28, 45), (26, 49), 2)
    pygame.draw.line(surf, BIRD_BEAK_D, (34, 45), (36, 49), 2)

    return surf


def _add_outline(src: pygame.Surface, outline_color=(20, 12, 18, 220)) -> pygame.Surface:
    """Return a surface with a 1-px dark outline around the sprite silhouette.

    Makes the bird pop against warm sunset stone and dark night skies
    (REVIEW.md finding — bird was hard to track in `14_death_hitflash.png`)."""
    w, h = src.get_size()
    pad = 2
    out = pygame.Surface((w + pad * 2, h + pad * 2), pygame.SRCALPHA)
    # Build an opaque silhouette mask from the source's alpha channel.
    mask = pygame.mask.from_surface(src, threshold=8)
    silhouette = mask.to_surface(setcolor=outline_color, unsetcolor=(0, 0, 0, 0))
    # Blit the silhouette at the 8 neighbour offsets to grow it by 1 px.
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1),
                   (-1, -1), (1, -1), (-1, 1), (1, 1)):
        out.blit(silhouette, (pad + dx, pad + dy))
    # Stamp the real sprite on top.
    out.blit(src, (pad, pad))
    return out


# Four wing angles — up, mid-up, level, down
_WING_ANGLES = (50, 20, -10, -40)
FRAMES: list[pygame.Surface] = [_add_outline(_build_frame(a)) for a in _WING_ANGLES]


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


# ── Fried-chicken variant (KFC powerup) ──────────────────────────────────────

_CRISPY_GOLD  = (188, 105,  18)   # main batter — rich dark amber-brown
_CRISPY_DARK  = ( 95,  40,   4)   # deep crack shadows
_CRISPY_LIGHT = (248, 192,  62)   # golden highlight peak
_CRISPY_SPOT  = ( 60,  24,   2)   # very dark burnt patches
_CRISPY_RIM   = (225, 148,  38)   # outer crust / raised batter ridge
_CRISPY_BELLY = (215, 158,  45)   # lower belly warmth


def _crackle(surf, lines):
    """Draw raised-batter crackle: dark crack valley + gold ridge alongside it."""
    for x1, y1, x2, y2 in lines:
        pygame.draw.line(surf, _CRISPY_DARK,  (x1,   y1  ), (x2,   y2  ), 1)
        pygame.draw.line(surf, _CRISPY_LIGHT, (x1-1, y1-1), (x2-1, y2-1), 1)


def _build_fried_wing(angle_deg):
    """Stubby fried wing — dark amber batter, heavy crackle, dark spots."""
    w = pygame.Surface((44, 44), pygame.SRCALPHA)
    pygame.draw.polygon(w, (0, 0, 0, 110),
                        [(22, 22), (38, 13), (42, 26), (30, 38), (16, 34)])
    pts = [(22, 20), (36, 12), (40, 25), (28, 36), (16, 32)]
    pygame.draw.polygon(w, _CRISPY_GOLD, pts)
    # Underside darker
    pygame.draw.polygon(w, _CRISPY_DARK, [(22, 20), (28, 36), (16, 32)])
    # Bright ridge highlight down the spine
    pygame.draw.line(w, _CRISPY_LIGHT, (23, 20), (37, 13), 1)
    # Crackle texture
    _crackle(w, [(24, 22, 38, 17), (26, 28, 40, 24), (30, 17, 36, 26)])
    # Dark burnt patches — denser than before
    for px, py, pr in ((32, 17, 2), (38, 23, 2), (25, 30, 2),
                       (35, 28, 1), (29, 20, 1), (41, 20, 1)):
        pygame.draw.circle(w, _CRISPY_SPOT, (px, py), pr)
    return pygame.transform.rotate(w, angle_deg)


def _build_fried_frame(wing_angle_deg):
    """Whole fried Thanksgiving chicken — crispy dark batter, plump body, drumstick legs."""
    surf = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)

    # ── Rear / tail bump ─────────────────────────────────────────────────────
    _aaellipse(surf, _CRISPY_DARK,  ( 8, 36), 10,  9)
    _aaellipse(surf, _CRISPY_GOLD,  ( 7, 34),  9,  8)
    _aaellipse(surf, _CRISPY_RIM,   ( 5, 31),  4,  3)   # raised crust rim
    for px, py, pr in ((5, 32, 2), (9, 29, 1), (4, 36, 1)):
        pygame.draw.circle(surf, _CRISPY_SPOT, (px, py), pr)

    # ── Main body ─────────────────────────────────────────────────────────────
    _aaellipse(surf, ( 80,  32,  2),  (33, 35), 25, 18)  # deep drop shadow
    _aaellipse(surf, _CRISPY_DARK,    (33, 34), 23, 17)  # dark base layer
    _aaellipse(surf, _CRISPY_GOLD,    (32, 32), 22, 16)  # main batter coat
    _aaellipse(surf, _CRISPY_RIM,     (32, 30), 20, 13)  # outer crust rim
    _aaellipse(surf, _CRISPY_LIGHT,   (29, 25), 14,  9)  # bright breast peak
    _aaellipse(surf, _CRISPY_BELLY,   (26, 38), 13,  7)  # lower belly warmth
    _aaellipse(surf, _CRISPY_DARK,    (32, 44), 19,  5)  # bottom shadow

    # Lots of dark crispy spots — uneven sizing for realism
    for px, py, pr in (
        (16, 27, 3), (35, 24, 3), (43, 31, 3), (22, 37, 3), (39, 38, 3),
        (27, 42, 2), (30, 23, 2), (46, 25, 2), (13, 34, 2), (36, 42, 2),
        (20, 32, 2), (42, 36, 1), (25, 27, 2), (33, 38, 1), (18, 41, 1),
    ):
        pygame.draw.circle(surf, _CRISPY_SPOT, (px, py), pr)

    # Dense raised-batter crackle — dark valley + gold ridge
    _crackle(surf, [
        (13, 30, 22, 25), (37, 25, 46, 29), (15, 38, 24, 43),
        (40, 37, 49, 33), (20, 33, 29, 28), (35, 32, 42, 38),
        (23, 41, 32, 36), (26, 28, 33, 33), (44, 29, 50, 35),
        (17, 43, 25, 39),
    ])

    # Golden grease sheen at breast peak
    sheen = pygame.Surface((28, 7), pygame.SRCALPHA)
    pygame.draw.ellipse(sheen, (255, 220, 120, 130), sheen.get_rect())
    surf.blit(sheen, (17, 19))

    # ── Drumstick legs ────────────────────────────────────────────────────────
    for (rx, ry, ex, ey) in ((19, 46, 7, 57), (45, 46, 57, 57)):
        pygame.draw.line(surf, _CRISPY_DARK,  (rx,   ry  ), (ex,   ey  ), 6)
        pygame.draw.line(surf, _CRISPY_GOLD,  (rx-1, ry-1), (ex-1, ey-1), 4)
        pygame.draw.line(surf, _CRISPY_RIM,   (rx-2, ry-2), (ex-2, ey-2), 2)
        pygame.draw.line(surf, _CRISPY_LIGHT, (rx-3, ry-2), (ex-3, ey-2), 1)
        ball = (ex, ey)
        pygame.draw.circle(surf, _CRISPY_DARK,  ball, 6)
        pygame.draw.circle(surf, _CRISPY_GOLD,  ball, 5)
        pygame.draw.circle(surf, _CRISPY_SPOT,  (ball[0]-1, ball[1]-2), 2)
        pygame.draw.circle(surf, WHITE,         ball, 2)   # bone tip
    # Crispy spot on each drumstick shaft
    pygame.draw.circle(surf, _CRISPY_SPOT, (13, 51), 2)
    pygame.draw.circle(surf, _CRISPY_SPOT, (51, 51), 2)

    # ── Wing (stubby, animated) ───────────────────────────────────────────────
    wing = _build_fried_wing(wing_angle_deg)
    surf.blit(wing, wing.get_rect(center=(34, 25)).topleft)

    # ── Head ─────────────────────────────────────────────────────────────────
    _aaellipse(surf, ( 80, 32,  2),  (50, 18), 11, 10)   # deep shadow
    _aaellipse(surf, _CRISPY_DARK,   (50, 17), 10,  9)
    _aaellipse(surf, _CRISPY_GOLD,   (49, 15), 10,  9)
    _aaellipse(surf, _CRISPY_RIM,    (47, 13),  7,  5)
    _aaellipse(surf, _CRISPY_LIGHT,  (45, 11),  5,  3)
    for px, py, pr in ((52, 14, 2), (47, 18, 1), (53, 19, 1)):
        pygame.draw.circle(surf, _CRISPY_SPOT, (px, py), pr)

    # Red chicken comb (it's a chicken now)
    for cx, cy, cr in ((47, 8, 3), (50, 6, 3), (53, 8, 2)):
        pygame.draw.circle(surf, (210, 30, 30), (cx, cy), cr)
        pygame.draw.circle(surf, (255, 70, 70), (cx-1, cy-1), cr-1)

    # Eye
    pygame.draw.circle(surf, WHITE,        (52, 16), 3)
    pygame.draw.circle(surf, (15, 15, 25), (53, 16), 2)
    pygame.draw.circle(surf, WHITE,        (54, 14), 1)

    # Beak
    beak_pts = [(55, 17), (61, 20), (58, 24), (52, 22)]
    pygame.draw.polygon(surf, BIRD_BEAK,   beak_pts)
    pygame.draw.polygon(surf, BIRD_BEAK_D, beak_pts, 1)
    pygame.draw.line(surf, (255, 230, 150), (55, 18), (59, 20), 1)

    return surf


KFC_FRAMES: list[pygame.Surface] = [_add_outline(_build_fried_frame(a)) for a in _WING_ANGLES]

_kfc_rot_cache: dict = {}


def get_fried_parrot(frame_idx: int, tilt_deg: float) -> pygame.Surface:
    """Return rotated fried-chicken parrot, cached by (frame, rounded-angle)."""
    frame_idx = frame_idx % len(KFC_FRAMES)
    key = (frame_idx, int(round(tilt_deg / 3.0)) * 3)
    s = _kfc_rot_cache.get(key)
    if s is None:
        s = pygame.transform.rotozoom(KFC_FRAMES[frame_idx], key[1], 1.0)
        _kfc_rot_cache[key] = s
    return s
