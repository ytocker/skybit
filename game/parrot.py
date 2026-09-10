"""
Stylish scarlet-macaw with aviator sunglasses — 4 pre-rendered wing frames.
Everything is drawn procedurally once at import with smooth alpha surfaces
(no pixel art). `get_parrot(frame_idx, tilt_deg)` returns a rotated surface,
cached by (frame, rounded-angle).
"""
import math
import pygame

from game.config import GROW_SCALE
from game.draw import (
    BIRD_RED, BIRD_RED_D, BIRD_WING, BIRD_WING_D, BIRD_TIP,
    BIRD_BELLY, BIRD_BEAK, BIRD_BEAK_D, WHITE, BLACK, NEAR_BLACK,
    lerp_color as _lerp_color,
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


def _draw_eye(surf, cx, cy):
    """Plain macaw eye — the bare-faced look that sits under the default
    aviators. A pale bare-skin facial patch (the scarlet macaw's signature)
    carrying a dark, glinting eye. It is the base the SHADES cosmetics paint
    over, and the look the store's NO-SHADES option leaves showing."""
    _aaellipse(surf, (250, 243, 236), (cx, cy), 6, 5)
    # Faint feather-lines streak the bare patch the way a real macaw's does.
    pygame.draw.line(surf, (236, 210, 205), (cx - 5, cy - 2), (cx + 5, cy - 2), 1)
    pygame.draw.line(surf, (236, 210, 205), (cx - 5, cy + 2), (cx + 5, cy + 2), 1)
    pygame.draw.circle(surf, (40, 26, 30), (cx + 1, cy), 3)
    pygame.draw.circle(surf, (15, 10, 12), (cx + 1, cy), 3, 1)
    pygame.draw.circle(surf, (255, 255, 255), (cx, cy - 1), 1)


def _build_frame(wing_angle_deg, *, eyewear=True):
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

    # Aviator sunglasses (replaces the plain eye). The SHADES cosmetics start
    # from the bare-eyed build (eyewear=False) and paint their own lenses over
    # this anchor; NO SHADES leaves the plain eye showing.
    if eyewear:
        _draw_sunglasses(surf, 50, 20)
    else:
        _draw_eye(surf, 50, 20)

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

# Lazy: building all four outlined frames cost ~100-300 ms on the WASM
# cold path. Deferring lets the splash paint first; the work runs the
# first time anything actually reads a frame (intro, menu, gameplay).
# Module `__getattr__` keeps `parrot.FRAMES` working for external code.
_FRAMES: "list[pygame.Surface] | None" = None

def _get_frames() -> "list[pygame.Surface]":
    global _FRAMES
    if _FRAMES is None:
        _FRAMES = [_add_outline(_build_frame(a)) for a in _WING_ANGLES]
    return _FRAMES


# ── Hi-res GROW-mode frames ──────────────────────────────────────────────────
# Round-9 picker (commit 0073175) chose v3: build the bird at 4.5× the
# base coordinates, then smoothscale DOWN to grow display size. Ports the
# same draw recipe as `_build_wing` / `_build_frame` / `_add_outline`,
# with every literal coordinate, line width, and ellipse radius
# multiplied by `s`. This produces a crisp grow-mode bird without
# upscaling the small 68×64 base sprite (the prior path's blur source).

_GROW_SS = 3.0 * GROW_SCALE                          # 3× supersample of GROW_SCALE
_GROW_W  = int((SPRITE_W + 4) * GROW_SCALE)
_GROW_H  = int((SPRITE_H + 4) * GROW_SCALE)


def _Sg(v, s): return int(round(v * s))
def _Pg(p, s): return (_Sg(p[0], s), _Sg(p[1], s))
def _Lg(pts, s): return [_Pg(p, s) for p in pts]


def _aaellipse_scaled(surf, color, center, rx, ry, s):
    cx, cy = center
    rect = pygame.Rect(_Sg(cx - rx, s), _Sg(cy - ry, s),
                       _Sg(rx * 2, s),  _Sg(ry * 2, s))
    pygame.draw.ellipse(surf, color, rect)


def _build_wing_scaled(angle_deg, s):
    box = _Sg(50, s)
    w = pygame.Surface((box, box), pygame.SRCALPHA)
    pygame.draw.polygon(w, (0, 0, 0, 110), _Lg(
        [(24, 26), (46, 14), (50, 30), (34, 44), (18, 40)], s))
    pygame.draw.polygon(w, BIRD_WING, _Lg(
        [(24, 24), (44, 13), (48, 28), (32, 42), (18, 36)], s))
    pygame.draw.polygon(w, BIRD_WING_D, _Lg(
        [(24, 24), (32, 42), (18, 36)], s))
    pygame.draw.polygon(w, BIRD_TIP, _Lg(
        [(44, 13), (50, 18), (48, 28)], s))
    pygame.draw.polygon(w, (255, 200, 60), _Lg(
        [(42, 18), (48, 22), (46, 28), (40, 24)], s))
    div_w = max(1, _Sg(2, s))
    pygame.draw.line(w, BIRD_WING_D, _Pg((26, 25), s), _Pg((42, 18), s), div_w)
    pygame.draw.line(w, BIRD_WING_D, _Pg((28, 30), s), _Pg((44, 25), s), div_w)
    pygame.draw.line(w, BIRD_WING_D, _Pg((30, 34), s), _Pg((46, 32), s), div_w)
    pygame.draw.line(w, (170, 210, 255),
                     _Pg((25, 25), s), _Pg((41, 15), s), max(1, _Sg(1, s)))
    return pygame.transform.rotate(w, angle_deg)


def _draw_sunglasses_scaled(surf, cx, cy, s):
    r_outer = 6
    left  = (cx - 4, cy)
    right = (cx + 6, cy - 1)
    pygame.draw.circle(surf, SHADE_FRAME, _Pg(left, s),  _Sg(r_outer + 1, s))
    pygame.draw.circle(surf, SHADE_FRAME, _Pg(right, s), _Sg(r_outer + 1, s))
    pygame.draw.circle(surf, SHADE_BLACK, _Pg(left, s),  _Sg(r_outer, s))
    pygame.draw.circle(surf, SHADE_BLACK, _Pg(right, s), _Sg(r_outer, s))
    tw = _Sg(r_outer * 2, s); th = _Sg(r_outer, s)
    tint = pygame.Surface((tw, th), pygame.SRCALPHA)
    pygame.draw.ellipse(tint, (*SHADE_TINT, 130), tint.get_rect())
    surf.blit(tint, (_Sg(left[0]  - r_outer, s), _Sg(left[1]  - r_outer + 1, s)))
    surf.blit(tint, (_Sg(right[0] - r_outer, s), _Sg(right[1] - r_outer + 1, s)))
    pygame.draw.circle(surf, SHADE_GLINT, _Pg((left[0]  - 2, left[1]  - 2), s), _Sg(2, s))
    pygame.draw.circle(surf, SHADE_GLINT, _Pg((right[0] - 2, right[1] - 3), s), _Sg(2, s))
    pygame.draw.circle(surf, (255, 255, 255, 200),
                       _Pg((left[0]  + 2, left[1]  + 2), s), max(1, _Sg(1, s)))
    pygame.draw.circle(surf, (255, 255, 255, 200),
                       _Pg((right[0] + 2, right[1] + 1), s), max(1, _Sg(1, s)))
    pygame.draw.line(surf, SHADE_FRAME,
                     _Pg((left[0]  + r_outer, left[1]),  s),
                     _Pg((right[0] - r_outer, right[1]), s), max(1, _Sg(2, s)))
    pygame.draw.line(surf, SHADE_FRAME,
                     _Pg((left[0]  - r_outer + 1, left[1]  - r_outer + 2), s),
                     _Pg((right[0] + r_outer - 1, right[1] - r_outer + 2), s),
                     max(1, _Sg(1, s)))


def _build_frame_scaled(wing_angle_deg, s):
    surf = pygame.Surface((_Sg(SPRITE_W, s), _Sg(SPRITE_H, s)), pygame.SRCALPHA)
    tail_colors = [
        (200,  30,  40),
        (240,  95,  40),
        (255, 160,  55),
        (255, 220,  80),
    ]
    for i, c in enumerate(tail_colors):
        pts = [
            (2 + i * 3, 26 + i * 2),
            (14 + i,     24 + i),
            (20 + i,     30 + i * 2),
            (6 + i * 3,  36 + i * 2),
        ]
        pygame.draw.polygon(surf, c, _Lg(pts, s))
    div_w = max(1, _Sg(1, s))
    pygame.draw.line(surf, BIRD_RED_D, _Pg((4, 27), s), _Pg((18, 31), s), div_w)
    pygame.draw.line(surf, BIRD_RED_D, _Pg((6, 33), s), _Pg((20, 35), s), div_w)

    _aaellipse_scaled(surf, (120, 20, 25),  (34, 35), 19, 14, s)
    _aaellipse_scaled(surf, BIRD_RED,       (32, 32), 19, 14, s)
    _aaellipse_scaled(surf, (255, 100, 100),(30, 29), 13,  8, s)
    _aaellipse_scaled(surf, BIRD_BELLY,     (28, 38), 12,  6, s)

    sw, sh = _Sg(28, s), _Sg(6, s)
    sheen = pygame.Surface((sw, sh), pygame.SRCALPHA)
    pygame.draw.ellipse(sheen, (255, 230, 230, 160), sheen.get_rect())
    surf.blit(sheen, (_Sg(22, s), _Sg(21, s)))

    wing = _build_wing_scaled(wing_angle_deg, s)
    surf.blit(wing, wing.get_rect(center=_Pg((34, 28), s)).topleft)

    _aaellipse_scaled(surf, (150, 15, 20),  (48, 23), 12, 11, s)
    _aaellipse_scaled(surf, BIRD_RED,       (47, 21), 12, 11, s)
    _aaellipse_scaled(surf, (255, 130, 130),(44, 24),  4,  3, s)
    _aaellipse_scaled(surf, (255, 170, 170),(46, 16),  7,  3, s)

    _draw_sunglasses_scaled(surf, 50, 20, s)

    beak_pts = [(55, 21), (61, 24), (58, 28), (52, 26)]
    pygame.draw.polygon(surf, BIRD_BEAK,   _Lg(beak_pts, s))
    pygame.draw.polygon(surf, BIRD_BEAK_D, _Lg(beak_pts, s), max(1, _Sg(1, s)))
    pygame.draw.line(surf, (255, 230, 150),
                     _Pg((55, 22), s), _Pg((59, 24), s), max(1, _Sg(1, s)))
    pygame.draw.line(surf, BIRD_BEAK_D,
                     _Pg((52, 24), s), _Pg((58, 25), s), max(1, _Sg(1, s)))

    foot_w = max(1, _Sg(2, s))
    pygame.draw.line(surf, BIRD_BEAK_D, _Pg((28, 45), s), _Pg((26, 49), s), foot_w)
    pygame.draw.line(surf, BIRD_BEAK_D, _Pg((34, 45), s), _Pg((36, 49), s), foot_w)

    return surf


def _add_outline_scaled(src, scale, outline_color=(20, 12, 18, 220)):
    """Outline thickness scales with `scale` so that after smoothscale-down
    to the 102×96 display target the outline reads as ~1 px."""
    w, h = src.get_size()
    r = max(1, int(round(scale)))
    pad = r + 1
    out = pygame.Surface((w + pad * 2, h + pad * 2), pygame.SRCALPHA)
    mask = pygame.mask.from_surface(src, threshold=8)
    silhouette = mask.to_surface(setcolor=outline_color, unsetcolor=(0, 0, 0, 0))
    for dx in range(-r, r + 1):
        for dy in range(-r, r + 1):
            if dx == 0 and dy == 0:
                continue
            if max(abs(dx), abs(dy)) > r:
                continue
            out.blit(silhouette, (pad + dx, pad + dy))
    out.blit(src, (pad, pad))
    return out


def _build_grow_frame(angle_deg):
    """One grow-mode bird frame: 4.5× supersampled body + outline,
    smoothscaled DOWN to grow display size (102×96)."""
    src = _build_frame_scaled(angle_deg, _GROW_SS)
    outlined = _add_outline_scaled(src, _GROW_SS)
    return pygame.transform.smoothscale(outlined, (_GROW_W, _GROW_H))


GROW_FRAMES: "list[pygame.Surface] | None" = None

_grow_rot_cache: dict = {}


def _get_grow_frames() -> "list[pygame.Surface]":
    """Lazy-build the 4 grow-mode parrot frames. At 4.5× supersample
    each frame is expensive (~tens of ms on native, multiples of that
    on WASM) and players who never pick up the GROW power-up never
    need them — building them at import time was adding noticeable
    latency to the splash-to-menu transition. Built once on first
    call and cached for the rest of the session."""
    global GROW_FRAMES
    if GROW_FRAMES is None:
        GROW_FRAMES = [_build_grow_frame(a) for a in _WING_ANGLES]
    return GROW_FRAMES


def get_grow_parrot(frame_idx: int, tilt_deg: float) -> pygame.Surface:
    """Hi-res grow-mode parrot. Pre-built at full grow display size — the
    caller MUST NOT smoothscale-up further."""
    frames = _get_grow_frames()
    frame_idx = frame_idx % len(frames)
    key = (frame_idx, int(round(tilt_deg / 3.0)) * 3)
    s = _grow_rot_cache.get(key)
    if s is None:
        s = pygame.transform.rotozoom(frames[frame_idx], key[1], 1.0)
        _grow_rot_cache[key] = s
    return s


# ── X-Ray Sparks (cartoon electrocution flash) ───────────────────────────────
# Classic Looney-Tunes / Tom-and-Jerry visual idiom: when Pip is struck by
# the storm-jolt lightning the body silhouette goes solid dark and the
# skeleton bones glow white inside, with crackling cyan sparks around the
# silhouette edge. Bird.draw alternates between this sprite and the normal
# parrot at ~10 Hz across 0.5s while `skeleton_flash_t > 0`. Body-part
# anchors mirror `_build_frame` so the silhouette matches Pip's normal pose
# exactly — only the palette + the bones-overlay change.

SKEL_DARK  = ( 26,  22,  36)     # silhouette / "flesh" colour
SKEL_BONE  = (255, 255, 255)     # bone highlights
SKEL_SOCK  = ( 14,  10,  18)     # eye sockets (slightly darker than dark)
SKEL_SPARK = (175, 230, 255)     # cyan crackle ticks


def _build_skeleton_wing(angle_deg):
    """Solid-dark wing polygon (matches `_build_wing`'s silhouette
    exactly, just one flat colour + a white bone tracing inside)."""
    w = pygame.Surface((50, 50), pygame.SRCALPHA)
    # Filled silhouette in dark
    silhouette_pts = [
        (24, 26), (46, 14), (50, 30), (34, 44), (18, 40),
    ]
    pygame.draw.polygon(w, SKEL_DARK, silhouette_pts)
    pygame.draw.polygon(w, SKEL_BONE, silhouette_pts, 1)
    # Bone tracing inside the wing — humerus (shoulder→elbow),
    # radius/ulna (elbow→wrist), and 3 finger phalanges (wrist→tips)
    pygame.draw.line(w, SKEL_BONE, (24, 26), (38, 22), 1)   # humerus
    pygame.draw.line(w, SKEL_BONE, (38, 22), (46, 30), 1)   # radius/ulna
    pygame.draw.line(w, SKEL_BONE, (46, 30), (50, 30), 1)   # phalanx 1
    pygame.draw.line(w, SKEL_BONE, (46, 30), (42, 40), 1)   # phalanx 2
    pygame.draw.line(w, SKEL_BONE, (46, 30), (34, 42), 1)   # phalanx 3
    # Joint dots so the bones read as articulated rather than scribbled
    pygame.draw.circle(w, SKEL_BONE, (24, 26), 1)
    pygame.draw.circle(w, SKEL_BONE, (38, 22), 1)
    pygame.draw.circle(w, SKEL_BONE, (46, 30), 1)
    rotated = pygame.transform.rotate(w, angle_deg)
    return rotated


def _build_skeleton_frame(wing_angle_deg):
    """One X-Ray Sparks frame at base 64×60. Solid dark silhouette of
    the parrot + white skeleton bones (skull, beak outline, spine,
    ribcage, wing bones, leg bones) + a handful of cyan crackle ticks
    baked around the silhouette edge."""
    surf = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)

    # ── Silhouette (matches _build_frame's body-part geometry) ──
    # Tail (one solid fan instead of the layered red→yellow gradient)
    tail_silhouette_pts = [
        (2, 26), (17, 24), (23, 36), (12, 42),
    ]
    pygame.draw.polygon(surf, SKEL_DARK, tail_silhouette_pts)
    # Body silhouette (single ellipse — no shadow / chest texture)
    _aaellipse(surf, SKEL_DARK, (32, 32), 19, 14)
    # Wing (dark + bone tracing). Drawn behind head, after body.
    wing = _build_skeleton_wing(wing_angle_deg)
    wr = wing.get_rect(center=(34, 28))
    surf.blit(wing, wr.topleft)
    # Head silhouette
    _aaellipse(surf, SKEL_DARK, (47, 21), 12, 11)
    # Beak silhouette (still hooked, just dark)
    beak_pts = [(55, 21), (61, 24), (58, 28), (52, 26)]
    pygame.draw.polygon(surf, SKEL_DARK, beak_pts)

    # ── Skeleton overlay (white-on-dark) ──
    # Skull: bright oval inside the head, with two dark eye sockets.
    # Slightly smaller than the head silhouette so the dark "flesh"
    # halo reads around the bone.
    _aaellipse(surf, SKEL_BONE, (47, 21), 9, 8)
    # Eye sockets — dark dots inside the white skull
    pygame.draw.circle(surf, SKEL_SOCK, (50, 19), 2)
    pygame.draw.circle(surf, SKEL_SOCK, (44, 20), 2)
    # Tiny bright glints to keep the sockets feeling like sockets,
    # not just dark holes (matches the eye position of the sunglasses
    # in the canonical frame)
    pygame.draw.circle(surf, SKEL_BONE, (51, 18), 1)
    # Beak outline in white over the dark beak silhouette
    pygame.draw.polygon(surf, SKEL_BONE, beak_pts, 1)
    # Lower-beak split line
    pygame.draw.line(surf, SKEL_BONE, (52, 25), (58, 25), 1)
    # Spine — vertical 2-px line from base of skull down to tail
    pygame.draw.line(surf, SKEL_BONE, (38, 26), (22, 36), 2)
    # Ribcage — 4 curved arc lines across the body silhouette
    for off_x in (-6, -2, 2, 6):
        pygame.draw.arc(surf, SKEL_BONE,
                        (24 + off_x, 24, 14, 16),
                        math.radians(200), math.radians(340), 1)
    # Tail bones — radiating fan lines mirroring the silhouette
    pygame.draw.line(surf, SKEL_BONE, (22, 36), (4, 28), 1)
    pygame.draw.line(surf, SKEL_BONE, (22, 36), (6, 34), 1)
    pygame.draw.line(surf, SKEL_BONE, (22, 36), (8, 40), 1)
    # Leg bones — 2 thin lines on each tucked leg (femur + tibia)
    pygame.draw.line(surf, SKEL_BONE, (28, 45), (27, 49), 1)
    pygame.draw.line(surf, SKEL_BONE, (34, 45), (35, 49), 1)
    # Tiny "foot bones" at the tip of each leg
    pygame.draw.circle(surf, SKEL_BONE, (27, 49), 1)
    pygame.draw.circle(surf, SKEL_BONE, (35, 49), 1)

    # ── Crackle ticks baked around the silhouette edge ──
    # Short 2-3 px cyan jagged sparks so the sprite reads as "being
    # shocked" even before the per-frame ephemeral sparks layered on
    # in Bird.draw. Positions are deterministic per-frame so each of
    # the 4 wing-flap frames looks slightly different.
    crackle_seeds = (
        (8, 22), (54, 14), (62, 30), (12, 44), (50, 46), (24, 18),
    )
    for cx, cy in crackle_seeds:
        # Small zig-zag: 3 points, 2 segments
        pygame.draw.line(surf, SKEL_SPARK, (cx, cy), (cx + 2, cy - 2), 1)
        pygame.draw.line(surf, SKEL_SPARK, (cx + 2, cy - 2),
                          (cx + 1, cy - 4), 1)
        # Brighter centre dot
        pygame.draw.circle(surf, SKEL_BONE, (cx + 1, cy - 2), 1)

    return surf


_SKELETON_FRAMES: "list[pygame.Surface] | None" = None
_skeleton_rot_cache: dict = {}


def _get_skeleton_frames() -> "list[pygame.Surface]":
    global _SKELETON_FRAMES
    if _SKELETON_FRAMES is None:
        _SKELETON_FRAMES = [_build_skeleton_frame(a) for a in _WING_ANGLES]
    return _SKELETON_FRAMES


def get_skeleton_parrot(frame_idx: int, tilt_deg: float) -> pygame.Surface:
    """X-Ray Sparks parrot — dark silhouette with white skeleton bones
    + baked cyan crackle ticks. Used by Bird.draw as a strobe overlay
    during the storm-jolt impact. Caches like get_parrot."""
    frames = _get_skeleton_frames()
    frame_idx = frame_idx % len(frames)
    key = (frame_idx, int(round(tilt_deg / 3.0)) * 3)
    cached = _skeleton_rot_cache.get(key)
    if cached is None:
        cached = pygame.transform.rotozoom(frames[frame_idx], key[1], 1.0)
        _skeleton_rot_cache[key] = cached
    return cached


# ── parcel sprite (Pip's permanent companion in gameplay) ────────────────────
# Pip carries the parcel through every run. Each visual mode (KFC, ghost,
# triple-buff hat, normal) uses a hand-tuned palette so the parcel reads as
# part of Pip's silhouette in that mode rather than as a colour-tinted overlay.

PARCEL_SIZE = 22

_PARCEL_PALETTES = {
    "normal": dict(
        BOX_BASE=(180, 130,  80), BOX_SHADE=(110,  75,  40), BOX_HI=(220, 175, 120),
        RIBBON  =(200,  50,  60), RIBBON_HI=(255, 110, 100),
        BOW_FILL=(200,  50,  60), BOW_HI   =(255, 130, 120),
        OUTLINE =( 26,  10,  12),
    ),
    "kfc": dict(  # warm fried-chicken amber to match KFC_FRAMES
        BOX_BASE=(210, 138,  42), BOX_SHADE=(148,  82,  18), BOX_HI=(238, 178,  72),
        RIBBON  =(110,  46,  22), RIBBON_HI=(180, 100,  52),
        BOW_FILL=(110,  46,  22), BOW_HI   =(180, 100,  52),
        OUTLINE =( 60,  32,  16),
    ),
    "ghost": dict(  # cool spectral cyan; alpha breath applied at draw-time
        BOX_BASE=(140, 200, 230), BOX_SHADE=( 88, 150, 190), BOX_HI=(200, 235, 250),
        RIBBON  =(110, 170, 210), RIBBON_HI=(180, 225, 250),
        BOW_FILL=(110, 170, 210), BOW_HI   =(180, 225, 250),
        OUTLINE =( 40,  90, 140),
    ),
    "triple": dict(  # kraft box, gold ribbon to harmonise with the stovepipe hat
        BOX_BASE=(180, 130,  80), BOX_SHADE=(110,  75,  40), BOX_HI=(220, 175, 120),
        RIBBON  =(210, 170,  60), RIBBON_HI=(255, 225, 140),
        BOW_FILL=(210, 170,  60), BOW_HI   =(255, 225, 140),
        OUTLINE =( 50,  32,  12),
    ),
}


def _build_parcel_variant(palette: dict, icon_size: int = 0) -> pygame.Surface:
    """Render a 22×22 parcel sprite using the supplied palette. Geometry
    ported from `game.intro._build_parcel` so the silhouette matches the
    intro exactly. Render at 2× detail then smoothscale-down once for crisp
    outlines + tiny pixel reads."""
    BOX_BASE = palette["BOX_BASE"]
    BOX_SHADE = palette["BOX_SHADE"]
    BOX_HI = palette["BOX_HI"]
    RIBBON = palette["RIBBON"]
    RIBBON_HI = palette["RIBBON_HI"]
    BOW_FILL = palette["BOW_FILL"]
    BOW_HI = palette["BOW_HI"]
    OUTLINE = palette["OUTLINE"]

    SIZE = 56
    surf = pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)
    BOX_W, BOX_H = 40, 34
    cx, cy = SIZE // 2, SIZE // 2 + 2
    rect = pygame.Rect(cx - BOX_W // 2, cy - BOX_H // 2 + 2, BOX_W, BOX_H)

    # Drop shadow
    sh = pygame.Surface((BOX_W + 8, 10), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (8, 4, 22, 130), sh.get_rect())
    surf.blit(sh, (cx - (BOX_W + 8) // 2, rect.bottom - 4))

    # Box body — outline frame + vertical-gradient fill + top sheen line
    pygame.draw.rect(surf, OUTLINE, rect.inflate(4, 4), border_radius=8)
    body = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    for y in range(rect.h):
        t = y / max(1, rect.h - 1)
        col = _lerp_color(BOX_BASE, BOX_SHADE, t) + (255,)
        body.fill(col, pygame.Rect(0, y, rect.w, 1))
    mask = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(),
                     border_radius=6)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(body, rect.topleft)
    pygame.draw.line(surf, BOX_HI,
                     (rect.x + 4, rect.y + 3),
                     (rect.right - 5, rect.y + 3), 2)

    # Vertical ribbon
    rv_w = 6
    rvx = rect.centerx - rv_w // 2
    pygame.draw.rect(surf, RIBBON, (rvx, rect.y, rv_w, rect.h))
    pygame.draw.line(surf, RIBBON_HI,
                     (rvx + 1, rect.y), (rvx + 1, rect.bottom - 1), 1)

    # Horizontal ribbon
    rh_w = 6
    rhy = rect.y + rect.h // 2 - rh_w // 2
    pygame.draw.rect(surf, RIBBON, (rect.x, rhy, rect.w, rh_w))
    pygame.draw.line(surf, RIBBON_HI, (rect.x, rhy + 1),
                     (rect.right - 1, rhy + 1), 1)

    # Bow on top — two puffy loops + knot + trailing tails
    bx, by = cx, rect.y - 6
    pygame.draw.ellipse(surf, OUTLINE,
                        pygame.Rect(bx - 13, by - 6, 13, 12))
    pygame.draw.ellipse(surf, BOW_FILL,
                        pygame.Rect(bx - 12, by - 5, 11, 10))
    pygame.draw.ellipse(surf, OUTLINE,
                        pygame.Rect(bx,       by - 6, 13, 12))
    pygame.draw.ellipse(surf, BOW_FILL,
                        pygame.Rect(bx + 1,   by - 5, 11, 10))
    pygame.draw.ellipse(surf, BOW_HI, pygame.Rect(bx - 10, by - 4, 4, 3))
    pygame.draw.ellipse(surf, BOW_HI, pygame.Rect(bx + 6,  by - 4, 4, 3))
    pygame.draw.rect(surf, OUTLINE, pygame.Rect(bx - 4, by - 6, 9, 12),
                     border_radius=2)
    pygame.draw.rect(surf, BOW_FILL,  pygame.Rect(bx - 3, by - 5, 7, 10),
                     border_radius=2)
    pygame.draw.line(surf, BOW_HI, (bx - 1, by - 4), (bx - 1, by + 3), 1)
    pygame.draw.line(surf, OUTLINE, (bx - 2, by + 4), (bx - 7, by + 11), 4)
    pygame.draw.line(surf, OUTLINE, (bx + 2, by + 4), (bx + 7, by + 11), 4)
    pygame.draw.line(surf, BOW_FILL, (bx - 2, by + 4), (bx - 6, by + 10), 2)
    pygame.draw.line(surf, BOW_FILL, (bx + 2, by + 4), (bx + 6, by + 10), 2)

    size = icon_size if icon_size else PARCEL_SIZE
    return pygame.transform.smoothscale(surf, (size, size))


def get_parcel_icon(icon_size: int = 88) -> pygame.Surface:
    """High-res parcel-base icon for store cards (clean downscale into thumb())."""
    return _build_parcel_variant(_PARCEL_PALETTES["normal"], icon_size=icon_size)


# Lazy: building all four parcel variants up front costs ~40-80 ms on
# the WASM cold path. Built on first get_parcel() call instead.
_PARCELS: "dict[str, pygame.Surface] | None" = None


def get_parcel(mode: str = "normal",
               parcel_id: "str | None" = None) -> pygame.Surface:
    """Return the parcel sprite. A custom equipped ``parcel_id`` routes to its
    cosmetic builder (mode-agnostic — it keeps its own look across power-ups);
    the default / None / ``parcel_base`` path uses the legacy per-mode palette
    box. Falls back to 'normal' on any miss so the parcel never disappears."""
    if parcel_id and parcel_id != "parcel_base":
        fn = _store_parcel_builders().get(parcel_id)
        if fn is not None:
            try:
                return fn(mode)
            except Exception:
                pass
    global _PARCELS
    if _PARCELS is None:
        _PARCELS = {name: _build_parcel_variant(pal)
                    for name, pal in _PARCEL_PALETTES.items()}
    return _PARCELS.get(mode, _PARCELS["normal"])


_rot_cache: dict = {}


def get_parrot(frame_idx: int, tilt_deg: float) -> pygame.Surface:
    """Return rotated parrot surface, cached by (frame, rounded-angle)."""
    frames = _get_frames()
    frame_idx = frame_idx % len(frames)
    key = (frame_idx, int(round(tilt_deg / 3.0)) * 3)
    s = _rot_cache.get(key)
    if s is None:
        s = pygame.transform.rotozoom(frames[frame_idx], key[1], 1.0)
        _rot_cache[key] = s
    return s


# ── Hurt parrot variant (last-life skin — ace headwrap) ──────────────────────

_H_SHADE_BLACK  = (15, 15, 25)
_H_SHADE_GLINT  = (255, 255, 255)
_H_SHADE_TINT   = (35, 55, 90)
_H_SHADE_FRAME  = (220, 175, 40)
_H_STITCH       = (180, 170, 160)
_H_GAUZE        = (198, 190, 172)
_H_HEM          = (120, 108,  95)
_H_CROSS        = (190,  20,  35)
_H_SCRATCH_D    = (100,  10,  10)
_H_SCRATCH_HL   = (245, 165, 150)
_H_SCRATCH_PALE = (180,  90,  80)
_H_CRACK        = (150, 175, 205)

_H_HURT_ANGLES = (10, -5, -20, -35)

_H_CHEST_PAD = [(20, 23), (30, 21), (31, 34), (21, 36)]
_H_CHEST_H   = ((23, 28), (27, 28))
_H_CHEST_V   = ((25, 25), (25, 31))
_H_UPPER_CUT = ((20, 33), (37, 43))
_H_LOWER_CUT = ((22, 40), (32, 45))
_H_BANDAID_L = (12, 40, 24, 46)
_H_BANDAID_R = (33, 37, 44, 43)
_H_BANDAID_3 = (38, 33, 47, 38)


def _h_stamp_clipped(surf: pygame.Surface, layer: pygame.Surface) -> None:
    # C-level mask replaces the Python 64×60 pixel loop — critical for WASM speed.
    surf_mask = pygame.mask.from_surface(surf, threshold=8)
    stamp = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    surf_mask.to_surface(stamp, setsurface=layer, unsetcolor=(0, 0, 0, 0))
    surf.blit(stamp, (0, 0))


def _h_lerp_pt(a, b, t):
    return (int(a[0] + (b[0] - a[0]) * t), int(a[1] + (b[1] - a[1]) * t))


def _h_draw_ragged_cuts(surf: pygame.Surface) -> None:
    core_layer = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    lip_layer  = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    d = pygame.draw
    pts = []
    for (ax, ay), (bx, by) in (_H_UPPER_CUT, _H_LOWER_CUT):
        lip_a = _h_lerp_pt((ax - 1, ay - 2), (bx - 1, by - 2), 0.20)
        d.line(lip_layer,  _H_SCRATCH_HL, lip_a, (bx - 1, by - 2), 1)
        d.line(core_layer, _H_SCRATCH_D,  (ax, ay), (bx, by), 1)
        pts.extend([(ax, ay), (bx, by), lip_a, (bx - 1, by - 2)])
    # Restrict pixel scan to the bounding box of the scratch lines — ~15×20 px
    # instead of 64×60, cutting 3840-iteration loops down to ~300.
    w, h = surf.get_size()
    x0 = max(0, min(p[0] for p in pts) - 1)
    x1 = min(w, max(p[0] for p in pts) + 2)
    y0 = max(0, min(p[1] for p in pts) - 1)
    y1 = min(h, max(p[1] for p in pts) + 2)
    dark: set = set()
    for x in range(x0, x1):
        for y in range(y0, y1):
            r, g, b, a = surf.get_at((x, y))
            if a > 8 and (0.299 * r + 0.587 * g + 0.114 * b) < 80:
                dark.add((x, y))
    for x in range(x0, x1):
        for y in range(y0, y1):
            base_a = surf.get_at((x, y))[3]
            if base_a <= 8:
                continue
            on_dark = (x, y) in dark
            if core_layer.get_at((x, y))[3] > 8:
                c = _H_SCRATCH_PALE if on_dark else _H_SCRATCH_D
                surf.set_at((x, y), (*c, base_a))
            elif lip_layer.get_at((x, y))[3] > 8 and not on_dark:
                surf.set_at((x, y), (*_H_SCRATCH_HL, base_a))


def _h_draw_bandaid(surf: pygame.Surface, x0, y0, x1, y1, tab_left: bool = True) -> None:
    layer = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    d = pygame.draw
    if tab_left:
        d.line(layer, _H_STITCH, (x0 - 3, y0 + 1), (x0, y0 + 1), 1)
        d.line(layer, _H_STITCH, (x0 - 3, y1 - 1), (x0, y1 - 1), 1)
    else:
        d.line(layer, _H_STITCH, (x1, y0 + 1), (x1 + 3, y0 + 1), 1)
        d.line(layer, _H_STITCH, (x1, y1 - 1), (x1 + 3, y1 - 1), 1)
    d.rect(layer, _H_GAUZE, (x0, y0, x1 - x0, y1 - y0))
    d.rect(layer, _H_HEM,   (x0, y0, x1 - x0, y1 - y0), 1)
    _h_stamp_clipped(surf, layer)


def _h_draw_bandaids(surf: pygame.Surface) -> None:
    x0, y0, x1, y1 = _H_BANDAID_L
    _h_draw_bandaid(surf, x0, y0, x1, y1, tab_left=True)
    x0, y0, x1, y1 = _H_BANDAID_R
    _h_draw_bandaid(surf, x0, y0, x1, y1, tab_left=False)
    x0, y0, x1, y1 = _H_BANDAID_3
    _h_draw_bandaid(surf, x0, y0, x1, y1, tab_left=False)


def _h_draw_chest_dressing(surf: pygame.Surface) -> None:
    import math as _math
    layer = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    d = pygame.draw
    cx = sum(p[0] for p in _H_CHEST_PAD) / len(_H_CHEST_PAD)
    cy = sum(p[1] for p in _H_CHEST_PAD) / len(_H_CHEST_PAD)
    grown = []
    for px, py in _H_CHEST_PAD:
        vx, vy = px - cx, py - cy
        L = max(1e-3, _math.hypot(vx, vy))
        grown.append((px + vx / L * 1.6, py + vy / L * 1.6))
    d.polygon(layer, _H_HEM,   grown)
    d.polygon(layer, _H_GAUZE, _H_CHEST_PAD)
    d.line(layer, _H_CROSS, _H_CHEST_H[0], _H_CHEST_H[1], 2)
    d.line(layer, _H_CROSS, _H_CHEST_V[0], _H_CHEST_V[1], 2)
    d.line(layer, _H_STITCH, (18, 26), (21, 26), 1)
    d.line(layer, _H_STITCH, (18, 32), (21, 32), 1)
    d.line(layer, _H_STITCH, (29, 23), (32, 23), 1)
    d.line(layer, _H_STITCH, (29, 31), (32, 31), 1)
    _h_stamp_clipped(surf, layer)


def _h_draw_headwrap(surf: pygame.Surface) -> None:
    layer = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    d = pygame.draw
    cap_pts = [(36, 21), (37, 16), (40, 12), (45, 10),
               (51, 11), (56, 14), (59, 18), (59, 21)]
    d.polygon(layer, _H_GAUZE, cap_pts)
    d.lines(layer, _H_HEM, False, cap_pts[:-1], 1)
    d.line(layer, _H_HEM, (38, 19), (57, 19), 1)
    d.line(layer, _H_HEM, (40, 17), (56, 17), 1)
    d.line(layer, _H_HEM, (40, 13), (54, 13), 1)
    d.line(layer, _H_HEM, (39, 15), (56, 15), 1)
    knot_pts = [(36, 16), (38, 14), (41, 15), (40, 18), (37, 19)]
    d.polygon(layer, _H_GAUZE, knot_pts)
    d.polygon(layer, _H_HEM,   knot_pts, 1)
    _h_stamp_clipped(surf, layer)
    d.line(surf, _H_GAUZE, (36, 17), (33, 20), 2)
    d.line(surf, _H_HEM,   (36, 17), (33, 20), 1)
    d.line(surf, _H_GAUZE, (37, 19), (35, 23), 2)
    d.line(surf, _H_HEM,   (37, 19), (35, 23), 1)
    surf.set_at((41, 19), _H_SCRATCH_PALE)
    surf.set_at((42, 19), _H_SCRATCH_PALE)
    surf.set_at((41, 20), (*_H_SCRATCH_PALE[:2], _H_SCRATCH_PALE[2] - 20))


def _h_draw_sunglasses(surf: pygame.Surface, cx: int, cy: int) -> None:
    r_outer = 6
    left  = (cx - 4, cy + 2)
    right = (cx + 6, cy - 1)
    pygame.draw.circle(surf, _H_SHADE_FRAME, left,  r_outer + 1)
    pygame.draw.circle(surf, _H_SHADE_FRAME, right, r_outer + 1)
    pygame.draw.circle(surf, _H_SHADE_BLACK, left,  r_outer)
    pygame.draw.circle(surf, _H_SHADE_BLACK, right, r_outer)
    tint = pygame.Surface((r_outer * 2, r_outer), pygame.SRCALPHA)
    pygame.draw.ellipse(tint, (*_H_SHADE_TINT, 130), tint.get_rect())
    surf.blit(tint, (left[0]  - r_outer, left[1]  - r_outer + 1))
    surf.blit(tint, (right[0] - r_outer, right[1] - r_outer + 1))
    pygame.draw.circle(surf, _H_SHADE_GLINT,       (right[0] - 2, right[1] - 3), 2)
    pygame.draw.circle(surf, (255, 255, 255, 200),  (right[0] + 2, right[1] + 1), 1)
    pygame.draw.line(surf, _H_SHADE_FRAME, (left[0] + 6, 21), (right[0] - 6, 19), 2)
    pygame.draw.line(surf, _H_SHADE_FRAME,
                     (left[0]  - r_outer + 1, left[1]  - r_outer + 2),
                     (right[0] + r_outer - 1, right[1] - r_outer + 2), 1)


def _h_draw_cracked_lens(surf: pygame.Surface) -> None:
    for end in ((41, 17), (50, 18), (47, 26)):
        pygame.draw.line(surf, _H_CRACK, (45, 21), end, 1)
    pygame.draw.line(surf, _H_CRACK, (43, 19), (47, 23), 1)


def _h_tail_feather(pts, damaged: bool = False):
    if not damaged:
        return pts
    import math as _math
    root = ((pts[1][0] + pts[2][0]) / 2.0, (pts[1][1] + pts[2][1]) / 2.0)
    a = _math.radians(18)
    ca, sa = _math.cos(a), _math.sin(a)
    out = []
    for i, (x, y) in enumerate(pts):
        if i in (0, 3):
            dx, dy = root[0] - x, root[1] - y
            L = max(1e-3, _math.hypot(dx, dy))
            x, y = x + dx / L * 8.0, y + dy / L * 8.0
        vx, vy = x - root[0], y - root[1]
        out.append((root[0] + vx * ca - vy * sa, root[1] + vx * sa + vy * ca))
    return out


def _h_draw_tail(surf: pygame.Surface) -> None:
    d = pygame.draw
    BODY_SH = (130, 12, 12)
    for i, c in enumerate(((174, 38, 48), (190, 70, 30),
                            (210, 130, 40), (230, 195, 65))):
        pts = [
            (2 + i * 3, 26 + i * 2), (14 + i, 24 + i),
            (20 + i, 30 + i * 2),    (6 + i * 3, 36 + i * 2),
        ]
        d.polygon(surf, c, _h_tail_feather(pts, damaged=(i == 1)))
    d.line(surf, BODY_SH, (4, 27), (18, 31), 1)
    d.line(surf, BODY_SH, (6, 33), (20, 35), 1)


def _h_build_wing(angle_deg: float) -> pygame.Surface:
    WING   = (30,  70, 180)
    WING_D = (18,  42, 125)
    TIP    = (50, 200,  95)
    STRIPE = (210, 175,  50)
    HL     = (130, 175, 240)
    w = pygame.Surface((50, 50), pygame.SRCALPHA)
    d = pygame.draw
    d.polygon(w, (0, 0, 0, 100), [(24, 26), (46, 14), (50, 30), (34, 44), (18, 40)])
    d.polygon(w, WING,           [(24, 24), (44, 13), (48, 28), (32, 42), (18, 36)])
    d.polygon(w, WING_D,         [(24, 24), (32, 42), (18, 36)])
    d.polygon(w, TIP,            [(44, 13), (50, 18), (48, 28)])
    d.polygon(w, STRIPE,         [(42, 18), (48, 22), (46, 28), (40, 24)])
    d.line(w, WING_D, (26, 25), (42, 18), 2)
    d.line(w, WING_D, (28, 30), (44, 25), 2)
    d.line(w, WING_D, (30, 34), (46, 32), 2)
    d.line(w, HL,     (25, 25), (41, 15), 1)
    d.polygon(w, (0, 0, 0, 0), [(41, 11), (53, 17), (47, 25), (43, 16)])
    return pygame.transform.rotate(w, angle_deg)


def _h_build_hurt_frame(wing_angle_deg: float) -> pygame.Surface:
    surf = pygame.Surface((64, 60), pygame.SRCALPHA)
    d = pygame.draw

    BODY    = (205,  28,  28)
    BODY_SH = (130,  12,  12)
    CHEST   = (235,  80,  80)
    BELLY   = (215, 140,  45)
    BEAK    = (235, 168,   0)
    BEAK_LO = (205, 138,   0)
    BEAK_D  = (140,  92,   0)

    _h_draw_tail(surf)

    _aaellipse(surf, BODY_SH, (34, 35), 19, 14)
    _aaellipse(surf, BODY,    (32, 32), 19, 14)
    _aaellipse(surf, CHEST,   (30, 29), 13,  8)
    _aaellipse(surf, BELLY,   (28, 38), 12,  6)

    sheen = pygame.Surface((28, 6), pygame.SRCALPHA)
    d.ellipse(sheen, (205, 150, 150, 120), sheen.get_rect())
    surf.blit(sheen, (22, 21))

    wing = _h_build_wing(wing_angle_deg)
    surf.blit(wing, wing.get_rect(center=(34, 28)).topleft)

    _h_draw_ragged_cuts(surf)
    _h_draw_bandaids(surf)

    _aaellipse(surf, (155, 15, 20),   (48, 24), 12, 11)
    _aaellipse(surf, BODY,            (47, 22), 12, 11)
    _aaellipse(surf, (200, 90, 90),   (44, 24),  4,  3)
    _aaellipse(surf, (230, 140, 140), (46, 17),  7,  3)

    _h_draw_headwrap(surf)
    _h_draw_sunglasses(surf, 50, 20)
    _h_draw_cracked_lens(surf)
    _h_draw_chest_dressing(surf)

    upper = [(55, 21), (61, 24), (58, 26), (52, 25)]
    lower = [(52, 26), (58, 27), (59, 30), (54, 31)]
    d.polygon(surf, BEAK,    upper)
    d.polygon(surf, BEAK_D,  upper, 1)
    d.polygon(surf, BEAK_LO, lower)
    d.polygon(surf, BEAK_D,  lower, 1)
    d.line(surf, (255, 220, 100), (55, 22), (59, 24), 1)

    d.line(surf, BEAK_D, (28, 45), (26, 49), 2)
    d.line(surf, BEAK_D, (34, 45), (36, 49), 2)

    return surf


_hurt_frames: list | None = None
_hurt_rot_cache: dict = {}


def _get_hurt_frames() -> list:
    global _hurt_frames
    if _hurt_frames is None:
        _hurt_frames = [_add_outline(_h_build_hurt_frame(a)) for a in _H_HURT_ANGLES]
    return _hurt_frames


def get_hurt_parrot(frame_idx: int, tilt_deg: float) -> pygame.Surface:
    """Return hurt-parrot (ace-headwrap last-life skin), cached by (frame, rounded-angle)."""
    frames = _get_hurt_frames()
    key = (frame_idx % 4, int(round(tilt_deg / 3.0)) * 3)
    s = _hurt_rot_cache.get(key)
    if s is None:
        s = pygame.transform.rotozoom(frames[key[0]], key[1], 1.0)
        _hurt_rot_cache[key] = s
    return s


# ── First-hit parrot (lives_remaining == 1) ──────────────────────────────────

def _fh_draw_single_crack(surf: pygame.Surface) -> None:
    """One hairline crack on the left lens — centre to lower-right rim only."""
    pygame.draw.line(surf, _H_CRACK, (45, 21), (47, 26), 1)


def _fh_build_hurt_frame(wing_angle_deg: float) -> pygame.Surface:
    """First-hit variant: bandaids + single lens crack, nothing else."""
    surf = pygame.Surface((64, 60), pygame.SRCALPHA)
    d = pygame.draw

    BODY    = (205,  28,  28)
    BODY_SH = (130,  12,  12)
    CHEST   = (235,  80,  80)
    BELLY   = (215, 140,  45)
    BEAK    = (235, 168,   0)
    BEAK_LO = (205, 138,   0)
    BEAK_D  = (140,  92,   0)

    _h_draw_tail(surf)

    _aaellipse(surf, BODY_SH, (34, 35), 19, 14)
    _aaellipse(surf, BODY,    (32, 32), 19, 14)
    _aaellipse(surf, CHEST,   (30, 29), 13,  8)
    _aaellipse(surf, BELLY,   (28, 38), 12,  6)

    sheen = pygame.Surface((28, 6), pygame.SRCALPHA)
    d.ellipse(sheen, (205, 150, 150, 120), sheen.get_rect())
    surf.blit(sheen, (22, 21))

    wing = _h_build_wing(wing_angle_deg)
    surf.blit(wing, wing.get_rect(center=(34, 28)).topleft)

    _h_draw_bandaids(surf)

    _aaellipse(surf, (155, 15, 20),   (48, 24), 12, 11)
    _aaellipse(surf, BODY,            (47, 22), 12, 11)
    _aaellipse(surf, (200, 90, 90),   (44, 24),  4,  3)
    _aaellipse(surf, (230, 140, 140), (46, 17),  7,  3)

    _h_draw_sunglasses(surf, 50, 20)
    _fh_draw_single_crack(surf)

    upper = [(55, 21), (61, 24), (58, 26), (52, 25)]
    lower = [(52, 26), (58, 27), (59, 30), (54, 31)]
    d.polygon(surf, BEAK,    upper)
    d.polygon(surf, BEAK_D,  upper, 1)
    d.polygon(surf, BEAK_LO, lower)
    d.polygon(surf, BEAK_D,  lower, 1)
    d.line(surf, (255, 220, 100), (55, 22), (59, 24), 1)

    d.line(surf, BEAK_D, (28, 45), (26, 49), 2)
    d.line(surf, BEAK_D, (34, 45), (36, 49), 2)

    return surf


_fh_frames: list | None = None
_fh_rot_cache: dict = {}


def _get_fh_frames() -> list:
    global _fh_frames
    if _fh_frames is None:
        _fh_frames = [_add_outline(_fh_build_hurt_frame(a)) for a in _H_HURT_ANGLES]
    return _fh_frames


def get_first_hit_parrot(frame_idx: int, tilt_deg: float) -> pygame.Surface:
    """Return first-hit parrot (bandaids + single crack), cached by (frame, rounded-angle)."""
    frames = _get_fh_frames()
    key = (frame_idx % 4, int(round(tilt_deg / 3.0)) * 3)
    s = _fh_rot_cache.get(key)
    if s is None:
        s = pygame.transform.rotozoom(frames[key[0]], key[1], 1.0)
        _fh_rot_cache[key] = s
    return s


# ── Ghost + last-life ─────────────────────────────────────────────────────────

def _build_ghost_hurt_frame(angle_deg: float) -> pygame.Surface:
    from game.dollar_parrot_ghost import _build_parrot_with_palette, P_SPECTRAL, _draw_lenses
    base = _build_parrot_with_palette(angle_deg, P_SPECTRAL, draw_lenses=False)
    _h_draw_bandaids(base)
    _h_draw_headwrap(base)
    _draw_lenses(base, 50, 20, P_SPECTRAL)
    _h_draw_chest_dressing(base)
    _h_draw_ragged_cuts(base)
    _h_draw_cracked_lens(base)
    return base


_ghost_hurt_frames: list | None = None
_ghost_hurt_cache: dict = {}


def _get_ghost_hurt_frames() -> list:
    global _ghost_hurt_frames
    if _ghost_hurt_frames is None:
        _ghost_hurt_frames = [_add_outline(_build_ghost_hurt_frame(a)) for a in _H_HURT_ANGLES]
    return _ghost_hurt_frames


def get_ghost_hurt_parrot(frame_idx: int, tilt_deg: float) -> pygame.Surface:
    frames = _get_ghost_hurt_frames()
    key = (frame_idx % 4, int(round(tilt_deg / 3.0)) * 3)
    s = _ghost_hurt_cache.get(key)
    if s is None:
        s = pygame.transform.rotozoom(frames[key[0]], key[1], 1.0)
        _ghost_hurt_cache[key] = s
    return s


# ── Ghost + first-hit ─────────────────────────────────────────────────────────

def _build_ghost_fh_frame(angle_deg: float) -> pygame.Surface:
    from game.dollar_parrot_ghost import _build_parrot_with_palette, P_SPECTRAL
    base = _build_parrot_with_palette(angle_deg, P_SPECTRAL)
    _h_draw_bandaids(base)
    _fh_draw_single_crack(base)
    return base


_ghost_fh_frames: list | None = None
_ghost_fh_cache: dict = {}


def _get_ghost_fh_frames() -> list:
    global _ghost_fh_frames
    if _ghost_fh_frames is None:
        _ghost_fh_frames = [_add_outline(_build_ghost_fh_frame(a)) for a in _H_HURT_ANGLES]
    return _ghost_fh_frames


def get_ghost_first_hit_parrot(frame_idx: int, tilt_deg: float) -> pygame.Surface:
    frames = _get_ghost_fh_frames()
    key = (frame_idx % 4, int(round(tilt_deg / 3.0)) * 3)
    s = _ghost_fh_cache.get(key)
    if s is None:
        s = pygame.transform.rotozoom(frames[key[0]], key[1], 1.0)
        _ghost_fh_cache[key] = s
    return s


# ── Grow + last-life ──────────────────────────────────────────────────────────

def _build_grow_hurt_frame(angle_deg: float) -> pygame.Surface:
    return pygame.transform.smoothscale(
        _add_outline(_h_build_hurt_frame(angle_deg)), (_GROW_W, _GROW_H))


_grow_hurt_frames: list | None = None
_grow_hurt_cache: dict = {}


def _get_grow_hurt_frames() -> list:
    global _grow_hurt_frames
    if _grow_hurt_frames is None:
        _grow_hurt_frames = [_build_grow_hurt_frame(a) for a in _H_HURT_ANGLES]
    return _grow_hurt_frames


def get_grow_hurt_parrot(frame_idx: int, tilt_deg: float) -> pygame.Surface:
    frames = _get_grow_hurt_frames()
    key = (frame_idx % 4, int(round(tilt_deg / 3.0)) * 3)
    s = _grow_hurt_cache.get(key)
    if s is None:
        s = pygame.transform.rotozoom(frames[key[0]], key[1], 1.0)
        _grow_hurt_cache[key] = s
    return s


# ── Grow + first-hit ──────────────────────────────────────────────────────────

def _build_grow_fh_frame(angle_deg: float) -> pygame.Surface:
    return pygame.transform.smoothscale(
        _add_outline(_fh_build_hurt_frame(angle_deg)), (_GROW_W, _GROW_H))


_grow_fh_frames: list | None = None
_grow_fh_cache: dict = {}


def _get_grow_fh_frames() -> list:
    global _grow_fh_frames
    if _grow_fh_frames is None:
        _grow_fh_frames = [_build_grow_fh_frame(a) for a in _H_HURT_ANGLES]
    return _grow_fh_frames


def get_grow_first_hit_parrot(frame_idx: int, tilt_deg: float) -> pygame.Surface:
    frames = _get_grow_fh_frames()
    key = (frame_idx % 4, int(round(tilt_deg / 3.0)) * 3)
    s = _grow_fh_cache.get(key)
    if s is None:
        s = pygame.transform.rotozoom(frames[key[0]], key[1], 1.0)
        _grow_fh_cache[key] = s
    return s


def __getattr__(name: str):
    """Lazy module attribute: external code reading `parrot.FRAMES`
    triggers the build on first access. Keeps the previous public API
    working without forcing every caller to switch to `_get_frames()`."""
    if name == "FRAMES":
        return _get_frames()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


# ── Fried-chicken variant (KFC powerup) ──────────────────────────────────────

_CRISPY_GOLD  = (210, 138,  42)
_CRISPY_DARK  = (148,  82,  18)
_CRISPY_LIGHT = (238, 178,  72)
_CRISPY_SPOT  = (125,  68,  12)


def _build_fried_wing(angle_deg):
    w = pygame.Surface((62, 62), pygame.SRCALPHA)
    # Drop shadow
    pygame.draw.polygon(w, (0, 0, 0, 120),
                        [(22, 28), (52, 10), (58, 32), (40, 50), (16, 44)])
    # Dark crust outline layer
    pygame.draw.polygon(w, _CRISPY_DARK,
                        [(22, 26), (50,  9), (56, 30), (38, 48), (16, 42)])
    # Main batter
    pygame.draw.polygon(w, _CRISPY_GOLD,
                        [(22, 24), (48,  8), (54, 28), (36, 46), (16, 40)])
    # Underside shadow
    pygame.draw.polygon(w, _CRISPY_DARK, [(22, 24), (36, 46), (16, 40)])
    # Bright ridge highlight
    _aaellipse(w, _CRISPY_LIGHT, (38, 22), 12, 6)
    # Dense crispy spots on wing
    for px, py, pr in ((40, 14, 3), (50, 20, 3), (44, 28, 3),
                       (30, 18, 2), (54, 28, 2), (34, 36, 2), (46, 34, 2)):
        pygame.draw.circle(w, _CRISPY_SPOT, (px, py), pr)
    # Crackle lines
    pygame.draw.line(w, _CRISPY_DARK,  (25, 27), (47, 15), 2)
    pygame.draw.line(w, _CRISPY_DARK,  (28, 34), (50, 24), 2)
    pygame.draw.line(w, _CRISPY_DARK,  (30, 40), (52, 32), 1)
    pygame.draw.line(w, _CRISPY_LIGHT, (24, 25), (46, 13), 1)
    pygame.draw.line(w, _CRISPY_LIGHT, (27, 32), (49, 22), 1)
    return pygame.transform.rotate(w, angle_deg)


def _build_fried_frame(wing_angle_deg):
    surf = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)

    # Tail — golden-brown crispy wedges
    for i, c in enumerate([(148, 82, 18), (178, 108, 28), (208, 138, 42), (228, 162, 58)]):
        pts = [(2 + i*3, 26 + i*2), (14 + i, 24 + i),
               (20 + i, 30 + i*2), (6 + i*3, 36 + i*2)]
        pygame.draw.polygon(surf, c, pts)
    pygame.draw.line(surf, _CRISPY_DARK, (4, 27), (18, 31), 1)
    pygame.draw.line(surf, _CRISPY_DARK, (6, 33), (20, 35), 1)

    # Body — plumper, more layered
    _aaellipse(surf, ( 85,  44,  5),   (34, 36), 23, 17)  # deep drop shadow
    _aaellipse(surf, _CRISPY_DARK,     (33, 35), 22, 16)  # dark base crust
    _aaellipse(surf, _CRISPY_GOLD,     (32, 33), 21, 15)  # main batter coat
    _aaellipse(surf, _CRISPY_LIGHT,    (29, 28), 15, 10)  # bright breast peak
    _aaellipse(surf, (242, 190, 80),   (27, 39), 14,  8)  # belly warmth
    _aaellipse(surf, _CRISPY_DARK,     (32, 45), 18,  5)  # bottom shadow

    # Dense crispy spots — varied sizes
    for px, py, pr in ((20, 30, 3), (37, 27, 3), (43, 35, 3),
                       (24, 39, 2), (38, 39, 2), (28, 34, 2),
                       (32, 26, 2), (44, 30, 2), (16, 37, 2),
                       (34, 42, 2), (40, 24, 1), (22, 43, 1)):
        pygame.draw.circle(surf, _CRISPY_SPOT, (px, py), pr)

    # Crackle lines — dark valley + gold ridge = raised batter texture
    for x1, y1, x2, y2 in [(14, 30, 23, 25), (37, 25, 47, 30),
                            (15, 39, 25, 44), (40, 38, 50, 33),
                            (22, 34, 31, 29), (34, 39, 43, 36)]:
        pygame.draw.line(surf, _CRISPY_DARK,  (x1,   y1  ), (x2,   y2  ), 1)
        pygame.draw.line(surf, _CRISPY_LIGHT, (x1-1, y1-1), (x2-1, y2-1), 1)

    # Golden grease sheen
    sheen = pygame.Surface((30, 7), pygame.SRCALPHA)
    pygame.draw.ellipse(sheen, (255, 225, 145, 130), sheen.get_rect())
    surf.blit(sheen, (17, 20))

    # Wing — larger, anchored higher so it fans out prominently
    wing = _build_fried_wing(wing_angle_deg)
    surf.blit(wing, wing.get_rect(center=(32, 24)).topleft)

    # Head — slightly bigger
    _aaellipse(surf, ( 95,  50,  6),   (49, 23), 13, 12)
    _aaellipse(surf, _CRISPY_GOLD,     (48, 21), 13, 12)
    _aaellipse(surf, _CRISPY_LIGHT,    (45, 24),  5,  4)
    _aaellipse(surf, (232, 172, 68),   (47, 15),  8,  4)
    for px, py, pr in ((52, 18, 2), (45, 22, 2), (51, 25, 1)):
        pygame.draw.circle(surf, _CRISPY_SPOT, (px, py), pr)

    # Eyes
    pygame.draw.circle(surf, WHITE,        (51, 20), 4)
    pygame.draw.circle(surf, (15, 15, 25), (52, 20), 2)
    pygame.draw.circle(surf, WHITE,        (53, 18), 1)

    # Beak
    beak_pts = [(55, 21), (61, 24), (58, 28), (52, 26)]
    pygame.draw.polygon(surf, BIRD_BEAK,   beak_pts)
    pygame.draw.polygon(surf, BIRD_BEAK_D, beak_pts, 1)
    pygame.draw.line(surf, (255, 230, 150), (55, 22), (59, 24), 1)
    pygame.draw.line(surf, BIRD_BEAK_D,    (52, 24), (58, 25), 1)

    # Simple tucked legs (original style)
    for lx, ly, ex, ey in ((28, 44, 24, 51), (34, 44, 38, 51)):
        pygame.draw.line(surf, _CRISPY_DARK, (lx, ly), (ex, ey), 3)
        pygame.draw.circle(surf, _CRISPY_GOLD, (ex, ey), 3)
        pygame.draw.circle(surf, _CRISPY_DARK, (ex, ey), 3, 1)

    return surf


KFC_FRAMES: "list[pygame.Surface] | None" = None

_kfc_rot_cache: dict = {}


def _get_kfc_frames() -> "list[pygame.Surface]":
    """Lazy-build the 4 KFC-mode parrot frames (same reasoning as
    _get_grow_frames — players who never pick up the KFC power-up
    never need them, so we don't pay the cost at boot)."""
    global KFC_FRAMES
    if KFC_FRAMES is None:
        KFC_FRAMES = [_add_outline(_build_fried_frame(a)) for a in _WING_ANGLES]
    return KFC_FRAMES


def get_fried_parrot(frame_idx: int, tilt_deg: float) -> pygame.Surface:
    """Return rotated fried-chicken parrot, cached by (frame, rounded-angle)."""
    frames = _get_kfc_frames()
    frame_idx = frame_idx % len(frames)
    key = (frame_idx, int(round(tilt_deg / 3.0)) * 3)
    s = _kfc_rot_cache.get(key)
    if s is None:
        s = pygame.transform.rotozoom(frames[frame_idx], key[1], 1.0)
        _kfc_rot_cache[key] = s
    return s


# ── Ghost variant ─────────────────────────────────────────────────────────────
#
# The ghost-parrot frames are built procedurally in
# `game.dollar_parrot_ghost.build_spectral_frame` — a full hand-drawn parrot
# in cool cyan tones with a soft halo. Lazy-init avoids the circular import
# (dollar_parrot_ghost imports FRAMES / _add_outline from this module).

_ghost_frames: "list[pygame.Surface] | None" = None
_ghost_cache: dict = {}


def _ensure_ghost_frames():
    global _ghost_frames
    if _ghost_frames is None:
        from game.dollar_parrot_ghost import (
            build_ghost_variant_frames, build_spectral_frame,
        )
        _ghost_frames = build_ghost_variant_frames(build_spectral_frame)
    return _ghost_frames


def get_ghost_parrot(frame_idx: int, tilt_deg: float) -> pygame.Surface:
    """Return rotated ghost parrot, cached by (frame, rounded-angle)."""
    frames = _ensure_ghost_frames()
    frame_idx = frame_idx % len(frames)
    key = (frame_idx, int(round(tilt_deg / 3.0)) * 3)
    s = _ghost_cache.get(key)
    if s is None:
        s = pygame.transform.rotozoom(frames[frame_idx], key[1], 1.0)
        _ghost_cache[key] = s
    return s


# ── Dead-Pip cross-fade variant ──────────────────────────────────────────────
# Drawn on top of the alive sprite at alpha = fade_t during the 0.4 s
# death cross-fade. E's aura scales with fade_t so early frames don't
# read "haunted while still alive" — buckets at 10% so frame counts
# stay bounded across the fade.
_dead_frames_by_key: dict = {}
_dead_rotation_cache: dict = {}


def _dead_aura_bucket(scale: float) -> int:
    s = max(0.0, min(1.0, scale))
    return int(round(s * 10)) * 10


def _ensure_dead_frames(palette_key: str, aura_bucket: int):
    key = (palette_key, aura_bucket)
    frames = _dead_frames_by_key.get(key)
    if frames is None:
        from game.dollar_parrot_dead import build_dead_variant_frames
        frames = build_dead_variant_frames(palette_key, aura_scale=aura_bucket / 100.0)
        _dead_frames_by_key[key] = frames
    return frames


def get_dead_parrot(frame_idx: int, tilt_deg: float,
                    palette_key: str = "E", aura_scale: float = 1.0):
    """Rotated dead-Pip sprite, cached by (palette, aura, frame, rounded-angle)."""
    bucket = _dead_aura_bucket(aura_scale)
    frames = _ensure_dead_frames(palette_key, bucket)
    frame_idx = frame_idx % len(frames)
    angle = int(round(tilt_deg / 3.0)) * 3
    rot_key = (palette_key, bucket, frame_idx, angle)
    s = _dead_rotation_cache.get(rot_key)
    if s is None:
        s = pygame.transform.rotozoom(frames[frame_idx], angle, 1.0)
        _dead_rotation_cache[rot_key] = s
    return s


# ── Triple-buff hat variant ───────────────────────────────────────────────────
# Lazily built on first use to avoid a circular import (dollar_parrot_hat
# imports from parrot for the body sprite).
_hat_frames: "list | None" = None
_hat_cache: dict = {}


def _ensure_hat_frames():
    global _hat_frames
    if _hat_frames is None:
        from game.dollar_parrot_hat import build_hat_frames, draw_stovepipe
        _hat_frames = build_hat_frames(draw_stovepipe)
    return _hat_frames


def get_hat_parrot(frame_idx: int, tilt_deg: float) -> pygame.Surface:
    """Return rotated stovepipe-hatted parrot, cached by (frame, rounded-angle)."""
    frames = _ensure_hat_frames()
    frame_idx = frame_idx % len(frames)
    key = (frame_idx, int(round(tilt_deg / 3.0)) * 3)
    s = _hat_cache.get(key)
    if s is None:
        s = pygame.transform.rotozoom(frames[frame_idx], key[1], 1.0)
        _hat_cache[key] = s
    return s


# ── Stacked-powerup combo helpers ────────────────────────────────────────────
# When kfc, ghost, and triple flags can all be true simultaneously, the
# default cascade in Bird.draw silently dropped all but the top-priority
# mode. These accessors give Bird.draw a dedicated sprite for every
# reachable combo. Themed hats live in dollar_parrot_hat; the cyan tint
# helper sits here (parrot.py) since both hatted and bare-fried-ghost
# combos use it.

def _cyan_tint_in_place(sprite, tint=(170, 230, 255), strength=0.55):
    """Shift a sprite's RGB toward cool cyan while preserving its alpha
    silhouette. Cheap derivation that turns a fried-chicken sprite into a
    spectral-fried hybrid without rebuilding a full palette pixel-by-
    pixel.

    `strength` is the alpha of the cyan overlay (0 = no effect, 1 = full
    cyan replacement). Implementation: build a solid cyan layer, mask it
    to the sprite silhouette so cyan doesn't leak into transparent
    regions, then alpha-blend onto the sprite."""
    sw, sh = sprite.get_size()
    overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
    overlay.fill((*tint, int(255 * strength)))
    overlay.blit(sprite, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    sprite.blit(overlay, (0, 0))


def tint_copy(sprite, tint, strength):
    """Return a COPY of `sprite` tinted toward `tint` (mask-clamped to the
    silhouette), leaving the source untouched — used to poison-tint whichever
    cached skin frame the draw cascade picked without mutating the cache."""
    out = sprite.copy()
    _cyan_tint_in_place(out, tint=tint, strength=strength)
    return out


def _ghostify_in_place(sprite: "pygame.Surface") -> None:
    """Replace the sprite's colour plate with the SPECTRAL ghost palette.

    Desaturates to luminance-correct grayscale, then gradient-maps:
      black  → SPECTRAL shadow  (40,  80, 140)
      white  → SPECTRAL highlight (220, 240, 250)
    The original skin's light/dark contrast is preserved as variation within
    the blue range. Alpha is carried through unchanged.
    """
    gray = pygame.transform.grayscale(sprite)
    # MULT scales [0,255] → [0,(180,160,110)]; ADD then lifts base to (40,80,140).
    # Result: black→(40,80,140), white→(220,240,250) — the SPECTRAL palette range.
    gray.fill((180, 160, 110, 255), special_flags=pygame.BLEND_MULT)
    gray.fill(( 40,  80, 140,   0), special_flags=pygame.BLEND_ADD)
    sprite.fill((0, 0, 0, 0))
    sprite.blit(gray, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)


# Crispy-parcel KFC cache — keyed by parcel_id; built once on first KFC pickup,
# never invalidated (parcel art is deterministic so the same id always produces
# the same surface).
_PARCEL_KFC_CACHE: "dict[str, pygame.Surface]" = {}


def _build_crispy_parcel(parcel_id: str, surf: pygame.Surface) -> pygame.Surface:
    """Return an 'extra crispy' KFC version of a 22×22 parcel surface.

    Samples the parcel's own dominant color and derives three crust tones from
    it — a mid amber coat, a dark spot/crack shade, and a light grease sheen —
    so every parcel gets a unique fried palette that harmonises with its own hue
    rather than a uniform amber wash.
    """
    w, h = surf.get_size()
    out = surf.copy()

    # Sample opaque interior pixels (skip 3px outer ring to avoid outline bias).
    margin = 3
    samples: list = []
    for px in range(margin, w - margin, 2):
        for py in range(margin, h - margin, 2):
            col = out.get_at((px, py))
            if col[3] > 160:
                samples.append(col[:3])
    avg = (tuple(sum(c[i] for c in samples) // len(samples) for i in range(3))
           if samples else _CRISPY_GOLD)

    def _blend(a, b, t):
        return tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(3))

    # Three crust tones: mid coat, dark spots/cracks, light sheen.
    coat  = _blend(avg, _CRISPY_GOLD,  0.50)
    dark  = _blend(avg, _CRISPY_DARK,  0.65)
    light = _blend(avg, _CRISPY_LIGHT, 0.50)

    # Amber base coat.
    _cyan_tint_in_place(out, tint=coat, strength=0.48)

    # Crispy spots — fixed relative positions so the pattern is consistent.
    hw, hh = w // 2, h // 2
    for sx, sy, sr in ((hw - 5, hh - 4, 2), (hw + 4, hh - 3, 1),
                       (hw - 4, hh + 4, 1), (hw + 5, hh + 3, 2),
                       (4,      hh,     1), (w - 5,  hh,     1)):
        if 0 <= sx < w and 0 <= sy < h:
            pygame.draw.circle(out, dark, (sx, sy), sr)

    # Crackle lines — dark valley then light ridge.
    for (x1, y1, x2, y2) in ((3, 5, 7, 3), (w - 4, h - 6, w - 8, h - 4)):
        pygame.draw.line(out, dark,  (x1,     y1    ), (x2,     y2    ), 1)
        pygame.draw.line(out, light, (x1 - 1, y1 - 1), (x2 - 1, y2 - 1), 1)

    # Grease sheen ellipse — upper-centre.
    sheen = pygame.Surface((10, 4), pygame.SRCALPHA)
    pygame.draw.ellipse(sheen, (*light, 110), sheen.get_rect())
    out.blit(sheen, (hw - 5, hh - 5))

    return out


def get_crispy_parcel(parcel_id: str, base_surf: pygame.Surface) -> pygame.Surface:
    """Return a cached crispy-KFC parcel surface, building it on first call."""
    s = _PARCEL_KFC_CACHE.get(parcel_id)
    if s is None:
        s = _build_crispy_parcel(parcel_id, base_surf)
        _PARCEL_KFC_CACHE[parcel_id] = s
    return s


_PARCEL_GHOST_CACHE: "dict[str, pygame.Surface]" = {}


def get_ghost_parcel(parcel_id: str) -> pygame.Surface:
    """Return a SPECTRAL-blue ghost version of a custom parcel.

    Built from the normal-mode surface so the cache is stable regardless of
    whether KFC was active — ghost dominates KFC, matching bird behaviour.
    """
    s = _PARCEL_GHOST_CACHE.get(parcel_id)
    if s is None:
        src = get_parcel("normal", parcel_id)
        s = src.copy()
        _ghostify_in_place(s)
        _PARCEL_GHOST_CACHE[parcel_id] = s
    return s


# Skin-power-up composite cache.
# Baked at run-start (Bird.rebuild_skin_combos) for the one equipped custom
# skin.  Seven flag combos x 4 wing angles stored at tilt=0; tilt rotation is
# applied at lookup time so the rotated result fits the standard rounded-angle
# cache already used by all other parrot getters.
_SKIN_COMBOS: "dict[str, dict[tuple, list]]" = {}
_SKIN_COMBO_ROT_CACHE: "dict[tuple, pygame.Surface]" = {}


def build_skin_powerup_composites(skin_id: str) -> None:
    """Pre-bake the 7 non-knight power-up combos x 4 frames for one skin.

    No-ops for skin_base and any id absent from the store skin registry; those
    fall through to the original bespoke cascade which already handles the base
    macaw correctly.
    """
    global _SKIN_COMBOS, _SKIN_COMBO_ROT_CACHE
    if _store_skin_builders().get(skin_id) is None:
        _SKIN_COMBOS.pop(skin_id, None)
        _SKIN_COMBO_ROT_CACHE = {}
        return
    from game.dollar_parrot_hat import (
        draw_stovepipe, draw_stovepipe_kfc, draw_stovepipe_ghost,
    )


    combos: "dict[tuple, list]" = {}
    for kfc_f in (False, True):
        for ghost_f in (False, True):
            for triple_f in (False, True):
                if not (kfc_f or ghost_f or triple_f):
                    continue
                frames = []
                for fi in range(4):
                    img = get_skin_frame(skin_id, fi, 0.0).copy()
                    iw, ih = img.get_size()
                    # Standard 68×104 skin: ax=0, ay=20 (= PARROT_DY).
                    # Zombie 100×96 (16 px aura on every side): ax=ay=16.
                    # The same formula aligns both KFC overlay and hat anchor
                    # without any per-skin branching.
                    ax = (iw - 68) // 2  # used by triple hat anchor
                    ay = (ih - 64) // 2
                    if kfc_f:
                        # KFC shows only the fried body — erase skin so nothing bleeds through.
                        img.fill((0, 0, 0, 0))
                        kfc_frame = _get_kfc_frames()[fi].copy()
                        img.blit(kfc_frame, (ax, ay))
                    if triple_f:
                        # $ stovepipe hat: brim always at (ax+50, ay+12) in canvas coords.
                        # In KFC+triple, the fried head is anchored at ay+11 regardless of scale.
                        hat_fn = (draw_stovepipe_kfc   if kfc_f
                                  else draw_stovepipe_ghost if ghost_f
                                  else draw_stovepipe)
                        if kfc_f:
                            hat_fn(img, ax + 50, ay + 12)
                        else:
                            hat_fn(img, 49 + ax, 12 + ay)
                    if ghost_f:
                        # Full SPECTRAL palette replacement: kills original hues,
                        # gradient-maps luminance to the ghost blue range (40,80,140)→(220,240,250).
                        _ghostify_in_place(img)
                    frames.append(img)
                combos[(kfc_f, ghost_f, triple_f)] = frames
    _SKIN_COMBOS[skin_id] = combos
    _SKIN_COMBO_ROT_CACHE = {}


def get_skin_combo_frame(
    skin_id: str, kfc: bool, ghost: bool, triple: bool,
    frame_idx: int, tilt_deg: float,
) -> "pygame.Surface | None":
    """Return the pre-baked composite for the given flags, or None to fall back."""
    combos = _SKIN_COMBOS.get(skin_id)
    if combos is None:
        return None
    frames = combos.get((kfc, ghost, triple))
    if frames is None:
        return None
    fi = frame_idx % 4
    rounded = int(round(tilt_deg / 3.0)) * 3
    key = (skin_id, kfc, ghost, triple, fi, rounded)
    s = _SKIN_COMBO_ROT_CACHE.get(key)
    if s is None:
        s = pygame.transform.rotozoom(frames[fi], rounded, 1.0)
        _SKIN_COMBO_ROT_CACHE[key] = s
    return s




# kfc + triple — fried bird + crispy KFC hat
_kfc_hat_frames: "list | None" = None
_kfc_hat_cache: dict = {}


def _ensure_kfc_hat_frames():
    global _kfc_hat_frames
    if _kfc_hat_frames is None:
        from game.dollar_parrot_hat import build_kfc_hat_frames
        _kfc_hat_frames = build_kfc_hat_frames()
    return _kfc_hat_frames


def get_kfc_hat_parrot(frame_idx: int, tilt_deg: float) -> pygame.Surface:
    frames = _ensure_kfc_hat_frames()
    frame_idx = frame_idx % len(frames)
    key = (frame_idx, int(round(tilt_deg / 3.0)) * 3)
    s = _kfc_hat_cache.get(key)
    if s is None:
        s = pygame.transform.rotozoom(frames[frame_idx], key[1], 1.0)
        _kfc_hat_cache[key] = s
    return s


# ghost + triple — spectral bird + spectral hat
_ghost_hat_frames: "list | None" = None
_ghost_hat_cache: dict = {}


def _ensure_ghost_hat_frames():
    global _ghost_hat_frames
    if _ghost_hat_frames is None:
        from game.dollar_parrot_hat import build_ghost_hat_frames
        _ghost_hat_frames = build_ghost_hat_frames()
    return _ghost_hat_frames


def get_ghost_hat_parrot(frame_idx: int, tilt_deg: float) -> pygame.Surface:
    frames = _ensure_ghost_hat_frames()
    frame_idx = frame_idx % len(frames)
    key = (frame_idx, int(round(tilt_deg / 3.0)) * 3)
    s = _ghost_hat_cache.get(key)
    if s is None:
        s = pygame.transform.rotozoom(frames[frame_idx], key[1], 1.0)
        _ghost_hat_cache[key] = s
    return s


# triple + last-life — stovepipe hat + ace-headwrap dressings
_hat_hurt_frames: "list | None" = None
_hat_hurt_cache: dict = {}


def _ensure_hat_hurt_frames():
    global _hat_hurt_frames
    if _hat_hurt_frames is None:
        from game.dollar_parrot_hat import build_hat_hurt_frames
        _hat_hurt_frames = build_hat_hurt_frames()
    return _hat_hurt_frames


def get_hat_hurt_parrot(frame_idx: int, tilt_deg: float) -> pygame.Surface:
    frames = _ensure_hat_hurt_frames()
    key = (frame_idx % len(frames), int(round(tilt_deg / 3.0)) * 3)
    s = _hat_hurt_cache.get(key)
    if s is None:
        s = pygame.transform.rotozoom(frames[key[0]], key[1], 1.0)
        _hat_hurt_cache[key] = s
    return s


# triple + first-hit — stovepipe hat + bandaids + single crack
_hat_fh_frames: "list | None" = None
_hat_fh_cache: dict = {}


def _ensure_hat_fh_frames():
    global _hat_fh_frames
    if _hat_fh_frames is None:
        from game.dollar_parrot_hat import build_hat_first_hit_frames
        _hat_fh_frames = build_hat_first_hit_frames()
    return _hat_fh_frames


def get_hat_first_hit_parrot(frame_idx: int, tilt_deg: float) -> pygame.Surface:
    frames = _ensure_hat_fh_frames()
    key = (frame_idx % len(frames), int(round(tilt_deg / 3.0)) * 3)
    s = _hat_fh_cache.get(key)
    if s is None:
        s = pygame.transform.rotozoom(frames[key[0]], key[1], 1.0)
        _hat_fh_cache[key] = s
    return s


# ghost + triple + last-life — ghost stovepipe + spectral parrot + dressings
_ghost_hat_hurt_frames: "list | None" = None
_ghost_hat_hurt_cache: dict = {}


def _ensure_ghost_hat_hurt_frames():
    global _ghost_hat_hurt_frames
    if _ghost_hat_hurt_frames is None:
        from game.dollar_parrot_hat import build_ghost_hat_hurt_frames
        _ghost_hat_hurt_frames = build_ghost_hat_hurt_frames()
    return _ghost_hat_hurt_frames


def get_ghost_hat_hurt_parrot(frame_idx: int, tilt_deg: float) -> pygame.Surface:
    frames = _ensure_ghost_hat_hurt_frames()
    key = (frame_idx % len(frames), int(round(tilt_deg / 3.0)) * 3)
    s = _ghost_hat_hurt_cache.get(key)
    if s is None:
        s = pygame.transform.rotozoom(frames[key[0]], key[1], 1.0)
        _ghost_hat_hurt_cache[key] = s
    return s


# ghost + triple + first-hit — ghost stovepipe + spectral parrot + first-hit dressings
_ghost_hat_fh_frames: "list | None" = None
_ghost_hat_fh_cache: dict = {}


def _ensure_ghost_hat_fh_frames():
    global _ghost_hat_fh_frames
    if _ghost_hat_fh_frames is None:
        from game.dollar_parrot_hat import build_ghost_hat_first_hit_frames
        _ghost_hat_fh_frames = build_ghost_hat_first_hit_frames()
    return _ghost_hat_fh_frames


def get_ghost_hat_first_hit_parrot(frame_idx: int, tilt_deg: float) -> pygame.Surface:
    frames = _ensure_ghost_hat_fh_frames()
    key = (frame_idx % len(frames), int(round(tilt_deg / 3.0)) * 3)
    s = _ghost_hat_fh_cache.get(key)
    if s is None:
        s = pygame.transform.rotozoom(frames[key[0]], key[1], 1.0)
        _ghost_hat_fh_cache[key] = s
    return s


# kfc + ghost — fried body cyan-tinted to read as spectral fried (no hat)
_kfc_ghost_frames: "list | None" = None
_kfc_ghost_cache: dict = {}


def _ensure_kfc_ghost_frames():
    global _kfc_ghost_frames
    if _kfc_ghost_frames is None:
        frames = []
        for a in _WING_ANGLES:
            f = _build_fried_frame(a).copy()
            _cyan_tint_in_place(f)
            frames.append(_add_outline(f))
        _kfc_ghost_frames = frames
    return _kfc_ghost_frames


def get_kfc_ghost_parrot(frame_idx: int, tilt_deg: float) -> pygame.Surface:
    frames = _ensure_kfc_ghost_frames()
    frame_idx = frame_idx % len(frames)
    key = (frame_idx, int(round(tilt_deg / 3.0)) * 3)
    s = _kfc_ghost_cache.get(key)
    if s is None:
        s = pygame.transform.rotozoom(frames[frame_idx], key[1], 1.0)
        _kfc_ghost_cache[key] = s
    return s


# kfc + ghost + triple — full stack: fried + KFC hat composite, all cyan-tinted
_kfc_ghost_hat_frames: "list | None" = None
_kfc_ghost_hat_cache: dict = {}


def _ensure_kfc_ghost_hat_frames():
    global _kfc_ghost_hat_frames
    if _kfc_ghost_hat_frames is None:
        from game.dollar_parrot_hat import build_kfc_ghost_hat_frames
        _kfc_ghost_hat_frames = build_kfc_ghost_hat_frames()
    return _kfc_ghost_hat_frames


def get_kfc_ghost_hat_parrot(frame_idx: int, tilt_deg: float) -> pygame.Surface:
    frames = _ensure_kfc_ghost_hat_frames()
    frame_idx = frame_idx % len(frames)
    key = (frame_idx, int(round(tilt_deg / 3.0)) * 3)
    s = _kfc_ghost_hat_cache.get(key)
    if s is None:
        s = pygame.transform.rotozoom(frames[frame_idx], key[1], 1.0)
        _kfc_ghost_hat_cache[key] = s
    return s


# ── Knight skin (survive-one-hit buff) ───────────────────────────────────────
#
# Frames are built in game/knight_skin.py (imported lazily to avoid a circular
# import at module load) so the armoured costume flaps with Pip's own wing
# per frame.
_knight_frames: "list[pygame.Surface] | None" = None
_knight_rot_cache: dict = {}


def _get_knight_frames() -> "list[pygame.Surface]":
    global _knight_frames
    if _knight_frames is None:
        from game import knight_skin
        _knight_frames = knight_skin.build_knight_frames()
    return _knight_frames


def get_knight_parrot(frame_idx: int, tilt_deg: float) -> pygame.Surface:
    """Return rotated knight-mode parrot, cached by (frame, rounded-angle)."""
    frames = _get_knight_frames()
    frame_idx = frame_idx % len(frames)
    key = (frame_idx, int(round(tilt_deg / 3.0)) * 3)
    s = _knight_rot_cache.get(key)
    if s is None:
        s = pygame.transform.rotozoom(frames[frame_idx], key[1], 1.0)
        _knight_rot_cache[key] = s
    return s


# knight + triple — armoured Pip wearing the royal metallic crown
_knight_hat_frames: "list | None" = None
_knight_hat_rot_cache: dict = {}


def _get_knight_hat_frames() -> "list[pygame.Surface]":
    global _knight_hat_frames
    if _knight_hat_frames is None:
        from game import knight_crown
        _knight_hat_frames = knight_crown.build_knight_hat_frames()
    return _knight_hat_frames


def get_knight_hat_parrot(frame_idx: int, tilt_deg: float) -> pygame.Surface:
    """Knight skin + royal crown (knight+3x), rotated, cached by (frame, angle)."""
    frames = _get_knight_hat_frames()
    frame_idx = frame_idx % len(frames)
    key = (frame_idx, int(round(tilt_deg / 3.0)) * 3)
    s = _knight_hat_rot_cache.get(key)
    if s is None:
        s = pygame.transform.rotozoom(frames[frame_idx], key[1], 1.0)
        _knight_hat_rot_cache[key] = s
    return s


# Remaining bespoke knight combos: knight x {kfc, ghost, kfc+ghost} and their
# +3x crowned stacks. Same lazy flat-build + per-(frame, angle) rotation-cache
# shape as get_knight_parrot, produced via a factory so each is one line rather
# than four boilerplate defs. Builders import lazily so a player who never
# reaches a combo never pays its build cost.
def _knight_combo_getter(build):
    state = {"frames": None, "cache": {}}

    def getter(frame_idx, tilt_deg):
        if state["frames"] is None:
            state["frames"] = build()
        frames = state["frames"]
        frame_idx %= len(frames)
        key = (frame_idx, int(round(tilt_deg / 3.0)) * 3)
        s = state["cache"].get(key)
        if s is None:
            s = pygame.transform.rotozoom(frames[frame_idx], key[1], 1.0)
            state["cache"][key] = s
        return s
    return getter


def _b_knight_kfc():
    from game import knight_skin
    return knight_skin.build_knight_kfc_frames()


def _b_knight_ghost():
    from game import knight_skin
    return knight_skin.build_knight_ghost_frames()


def _b_knight_kfc_ghost():
    from game import knight_skin
    return knight_skin.build_knight_kfc_ghost_frames()


def _b_knight_kfc_hat():
    from game import knight_crown
    return knight_crown.build_knight_kfc_hat_frames()


def _b_knight_ghost_hat():
    from game import knight_crown
    return knight_crown.build_knight_ghost_hat_frames()


def _b_knight_kfc_ghost_hat():
    from game import knight_crown
    return knight_crown.build_knight_kfc_ghost_hat_frames()


get_knight_kfc_parrot = _knight_combo_getter(_b_knight_kfc)
get_knight_ghost_parrot = _knight_combo_getter(_b_knight_ghost)
get_knight_kfc_ghost_parrot = _knight_combo_getter(_b_knight_kfc_ghost)
get_knight_kfc_hat_parrot = _knight_combo_getter(_b_knight_kfc_hat)
get_knight_ghost_hat_parrot = _knight_combo_getter(_b_knight_ghost_hat)
get_knight_kfc_ghost_hat_parrot = _knight_combo_getter(_b_knight_kfc_ghost_hat)


# ── Poisoned (dead-Pip B) accessor ──────────────────────────────────────────
#
# Used by Bird.draw while poison_active to cross-fade between the healthy
# sprite and the fully-poisoned t = 1.0 endpoint. Same frame the existing
# death-fade overlay paints with, so the visual lands continuous when the
# terminal poison kill kicks off the standard death pipeline.
_poisoned_frames: "list[pygame.Surface] | None" = None
_poisoned_rot_cache: dict = {}


def _get_poisoned_frames() -> "list[pygame.Surface]":
    global _poisoned_frames
    if _poisoned_frames is None:
        from game import dollar_parrot_dead
        _poisoned_frames = [
            _add_outline(dollar_parrot_dead.build_chartreuse_dead(a))
            for a in _WING_ANGLES
        ]
    return _poisoned_frames


def get_poisoned_parrot(frame_idx: int, tilt_deg: float) -> pygame.Surface:
    frames = _get_poisoned_frames()
    frame_idx = frame_idx % len(frames)
    key = (frame_idx, int(round(tilt_deg / 3.0)) * 3)
    s = _poisoned_rot_cache.get(key)
    if s is None:
        s = pygame.transform.rotozoom(frames[frame_idx], key[1], 1.0)
        _poisoned_rot_cache[key] = s
    return s


# ── Coin-store cosmetic-skin dispatch ─────────────────────────────────────────
# The store's cosmetic roster (costumes, parrot recolors, animals, shoes, hats,
# shades, parcels) lives in game/*_skins.py; those modules are imported lazily
# (after this module is fully loaded) so they can import `parrot` back without a
# circular-import hazard. Each exposes a BUILDERS dict (skin id -> (frame,tilt)
# builder) and optionally an ICONS dict (skin id -> product-shot surface).
_STORE_SKINS: "dict | None" = None
_SKIN_ICONS: "dict | None" = None
_STORE_PARCELS: "dict | None" = None


def _build_frame_bare(wing_angle_deg):
    """The base macaw with a plain eye instead of the baked aviators — the
    `base_fn` every SHADES skin builds on (glasses_skins.py)."""
    return _build_frame(wing_angle_deg, eyewear=False)


def _store_skin_builders() -> dict:
    global _STORE_SKINS
    if _STORE_SKINS is None:
        merged: dict = {}
        for modname in ("store_skins", "skeleton_skin", "animal_skins",
                        "shoe_skins", "hat_skins", "glasses_skins",
                        "skin_basketball"):
            try:
                mod = __import__("game." + modname, fromlist=["BUILDERS"])
                merged.update(mod.BUILDERS)
            except Exception:
                pass
        _STORE_SKINS = merged
    return _STORE_SKINS


def _skin_icons() -> dict:
    """Prebuilt product-shot surfaces for skins that want a store icon distinct
    from their in-game look (shoes show the sneaker itself). Lazily merged.
    Parcel icons are excluded — handled per-item lazily in get_skin_icon()."""
    global _SKIN_ICONS
    if _SKIN_ICONS is None:
        merged: dict = {}
        for modname in ("shoe_skins", "hat_skins", "glasses_skins"):
            try:
                mod = __import__("game." + modname, fromlist=["ICONS"])
                merged.update(getattr(mod, "ICONS", {}))
            except Exception:
                pass
        _SKIN_ICONS = merged
    return _SKIN_ICONS


def _store_parcel_builders() -> dict:
    """Lazily merge ``parcel_skins.BUILDERS`` — the swappable parcel cosmetics
    sold in the PARCELS store tab. An absent/broken module degrades to the
    legacy palette box."""
    global _STORE_PARCELS
    if _STORE_PARCELS is None:
        merged: dict = {}
        try:
            mod = __import__("game.parcel_skins", fromlist=["BUILDERS"])
            merged.update(mod.BUILDERS)
        except Exception:
            pass
        _STORE_PARCELS = merged
    return _STORE_PARCELS


def get_skin_frame(skin_id: str, frame_idx: int, tilt_deg: float) -> pygame.Surface:
    """Render the equipped cosmetic's frame. Unknown ids fall back to the base
    parrot so a stale save (skin removed in a later build) degrades to the
    default look rather than crashing the draw."""
    fn = _store_skin_builders().get(skin_id) or get_parrot
    return fn(frame_idx, tilt_deg)


_STORE_SKIN_HURT: "dict | None" = None


def _store_skin_hurt_getters() -> dict:
    global _STORE_SKIN_HURT
    if _STORE_SKIN_HURT is None:
        try:
            mod = __import__("game.store_skin_hurt", fromlist=["SKIN_HURT_GETTERS"])
            _STORE_SKIN_HURT = mod.SKIN_HURT_GETTERS
        except Exception:
            _STORE_SKIN_HURT = {}
    return _STORE_SKIN_HURT


def get_skin_hurt_frame(skin_id: str, frame_idx: int, tilt_deg: float) -> pygame.Surface:
    """Last-life frame for the equipped store skin. Falls back to the base
    macaw hurt skin when skin_id is unrecognised."""
    pair = _store_skin_hurt_getters().get(skin_id)
    if pair is None:
        return get_hurt_parrot(frame_idx, tilt_deg)
    ll_getter, _ = pair
    return ll_getter(frame_idx, tilt_deg)


def get_skin_first_hit_frame(skin_id: str, frame_idx: int, tilt_deg: float) -> pygame.Surface:
    """First-hit frame for the equipped store skin. Falls back to the base
    macaw first-hit skin when skin_id is unrecognised."""
    pair = _store_skin_hurt_getters().get(skin_id)
    if pair is None:
        return get_first_hit_parrot(frame_idx, tilt_deg)
    _, fh_getter = pair
    return fh_getter(frame_idx, tilt_deg)


def get_skin_frame_hi(skin_id: str) -> pygame.Surface:
    """High-res skin frame for store thumbnails. Renders the base macaw at 3×
    (192×180) so thumb() gets a clean downscale; all registered skins fall back
    to standard get_skin_frame (already a clean downscale at 64×60)."""
    if skin_id in _store_skin_builders():
        return get_skin_frame(skin_id, 1, 0.0)
    raw = _build_frame_scaled(_WING_ANGLES[1], 3.0)
    return _add_outline_scaled(raw, 3.0)


def get_skin_icon(skin_id: str) -> "pygame.Surface | None":
    """The store product-shot for a skin, or None to fall back to the in-game
    look (so shoe cards show the sneaker itself, not Pip wearing it)."""
    if skin_id.startswith("parcel"):
        try:
            mod = __import__("game.parcel_skins", fromlist=["get_icon"])
            return mod.get_icon(skin_id)
        except Exception:
            return None
    return _skin_icons().get(skin_id)


def skin_builder_ids() -> set:
    """All renderable cosmetic skin ids (the store roster). Used by tests to
    assert every catalog skin resolves to a builder. ``skin_base`` is the
    implicit default — it renders as the base parrot via the get_parrot
    fallback, so it counts as drawable."""
    return {"skin_base"} | set(_store_skin_builders())


# ── Skin-aware powerup frame helpers ─────────────────────────────────────────
# Ghost, hat (triple), ghost+hat, and grow all route through these getters so
# the equipped store skin's own body/accessories appear under each powerup.

def _spectral_colorize(surf: pygame.Surface) -> pygame.Surface:
    """Return a new spectral-blue copy of surf; alpha channel unchanged."""
    out = surf.copy()
    _ghostify_in_place(out)
    return out


# ── Ghost + skin ──────────────────────────────────────────────────────────────

_skin_ghost_cache: dict = {}
_skin_ghost_fh_cache: dict = {}
_skin_ghost_hurt_cache: dict = {}


def get_skin_ghost_frame(skin_id: str, frame_idx: int, tilt_deg: float) -> pygame.Surface:
    """Ghost-colorized clean frame for the equipped skin."""
    key = (skin_id, frame_idx % 4, int(round(tilt_deg / 3.0)) * 3)
    s = _skin_ghost_cache.get(key)
    if s is None:
        base = get_skin_frame(skin_id, key[1], 0.0)
        colored = _spectral_colorize(base)
        s = pygame.transform.rotozoom(colored, key[2], 1.0)
        _skin_ghost_cache[key] = s
    return s


def get_skin_ghost_first_hit_frame(skin_id: str, frame_idx: int, tilt_deg: float) -> pygame.Surface:
    """Ghost-colorized first-hit frame for the equipped skin."""
    key = (skin_id, frame_idx % 4, int(round(tilt_deg / 3.0)) * 3)
    s = _skin_ghost_fh_cache.get(key)
    if s is None:
        base = get_skin_first_hit_frame(skin_id, key[1], 0.0)
        colored = _spectral_colorize(base)
        s = pygame.transform.rotozoom(colored, key[2], 1.0)
        _skin_ghost_fh_cache[key] = s
    return s


def get_skin_ghost_hurt_frame(skin_id: str, frame_idx: int, tilt_deg: float) -> pygame.Surface:
    """Ghost-colorized last-life frame for the equipped skin."""
    key = (skin_id, frame_idx % 4, int(round(tilt_deg / 3.0)) * 3)
    s = _skin_ghost_hurt_cache.get(key)
    if s is None:
        base = get_skin_hurt_frame(skin_id, key[1], 0.0)
        colored = _spectral_colorize(base)
        s = pygame.transform.rotozoom(colored, key[2], 1.0)
        _skin_ghost_hurt_cache[key] = s
    return s


# ── Hat (triple) + skin ───────────────────────────────────────────────────────

_STORE_SKIN_HAT: "dict | None" = None


def _store_skin_hat_getters() -> dict:
    global _STORE_SKIN_HAT
    if _STORE_SKIN_HAT is None:
        try:
            mod = __import__("game.store_skin_hat", fromlist=["SKIN_HAT_GETTERS"])
            _STORE_SKIN_HAT = mod.SKIN_HAT_GETTERS
        except Exception:
            _STORE_SKIN_HAT = {}
    return _STORE_SKIN_HAT


def get_skin_hat_frame(skin_id: str, frame_idx: int, tilt_deg: float) -> pygame.Surface:
    """Hatted clean frame for the equipped skin; falls back to base macaw hat."""
    triple = _store_skin_hat_getters().get(skin_id)
    if triple is None:
        return get_hat_parrot(frame_idx, tilt_deg)
    return triple[0](frame_idx, tilt_deg)


def get_skin_hat_first_hit_frame(skin_id: str, frame_idx: int, tilt_deg: float) -> pygame.Surface:
    """Hatted first-hit frame for the equipped skin."""
    triple = _store_skin_hat_getters().get(skin_id)
    if triple is None:
        return get_hat_first_hit_parrot(frame_idx, tilt_deg)
    return triple[1](frame_idx, tilt_deg)


def get_skin_hat_hurt_frame(skin_id: str, frame_idx: int, tilt_deg: float) -> pygame.Surface:
    """Hatted last-life frame for the equipped skin."""
    triple = _store_skin_hat_getters().get(skin_id)
    if triple is None:
        return get_hat_hurt_parrot(frame_idx, tilt_deg)
    return triple[2](frame_idx, tilt_deg)


# ── Ghost+hat + skin ──────────────────────────────────────────────────────────

_skin_ghost_hat_cache: dict = {}
_skin_ghost_hat_fh_cache: dict = {}
_skin_ghost_hat_hurt_cache: dict = {}


def get_skin_ghost_hat_frame(skin_id: str, frame_idx: int, tilt_deg: float) -> pygame.Surface:
    """Ghost-colorized hatted clean frame for the equipped skin."""
    key = (skin_id, frame_idx % 4, int(round(tilt_deg / 3.0)) * 3)
    s = _skin_ghost_hat_cache.get(key)
    if s is None:
        base = get_skin_hat_frame(skin_id, key[1], 0.0)
        colored = _spectral_colorize(base)
        s = pygame.transform.rotozoom(colored, key[2], 1.0)
        _skin_ghost_hat_cache[key] = s
    return s


def get_skin_ghost_hat_first_hit_frame(skin_id: str, frame_idx: int, tilt_deg: float) -> pygame.Surface:
    """Ghost-colorized hatted first-hit frame for the equipped skin."""
    key = (skin_id, frame_idx % 4, int(round(tilt_deg / 3.0)) * 3)
    s = _skin_ghost_hat_fh_cache.get(key)
    if s is None:
        base = get_skin_hat_first_hit_frame(skin_id, key[1], 0.0)
        colored = _spectral_colorize(base)
        s = pygame.transform.rotozoom(colored, key[2], 1.0)
        _skin_ghost_hat_fh_cache[key] = s
    return s


def get_skin_ghost_hat_hurt_frame(skin_id: str, frame_idx: int, tilt_deg: float) -> pygame.Surface:
    """Ghost-colorized hatted last-life frame for the equipped skin."""
    key = (skin_id, frame_idx % 4, int(round(tilt_deg / 3.0)) * 3)
    s = _skin_ghost_hat_hurt_cache.get(key)
    if s is None:
        base = get_skin_hat_hurt_frame(skin_id, key[1], 0.0)
        colored = _spectral_colorize(base)
        s = pygame.transform.rotozoom(colored, key[2], 1.0)
        _skin_ghost_hat_hurt_cache[key] = s
    return s


# ── Grow + skin ───────────────────────────────────────────────────────────────

_skin_grow_cache: dict = {}
_skin_grow_fh_cache: dict = {}
_skin_grow_hurt_cache: dict = {}


def get_skin_grow_frame(skin_id: str, frame_idx: int, tilt_deg: float) -> pygame.Surface:
    """Grow-scaled clean frame for the equipped skin."""
    key = (skin_id, frame_idx % 4, int(round(tilt_deg / 3.0)) * 3)
    s = _skin_grow_cache.get(key)
    if s is None:
        base = get_skin_frame(skin_id, key[1], 0.0)
        scaled = pygame.transform.smoothscale(base, (_GROW_W, _GROW_H))
        s = pygame.transform.rotozoom(scaled, key[2], 1.0)
        _skin_grow_cache[key] = s
    return s


def get_skin_grow_first_hit_frame(skin_id: str, frame_idx: int, tilt_deg: float) -> pygame.Surface:
    """Grow-scaled first-hit frame for the equipped skin."""
    key = (skin_id, frame_idx % 4, int(round(tilt_deg / 3.0)) * 3)
    s = _skin_grow_fh_cache.get(key)
    if s is None:
        base = get_skin_first_hit_frame(skin_id, key[1], 0.0)
        scaled = pygame.transform.smoothscale(base, (_GROW_W, _GROW_H))
        s = pygame.transform.rotozoom(scaled, key[2], 1.0)
        _skin_grow_fh_cache[key] = s
    return s


def get_skin_grow_hurt_frame(skin_id: str, frame_idx: int, tilt_deg: float) -> pygame.Surface:
    """Grow-scaled last-life frame for the equipped skin."""
    key = (skin_id, frame_idx % 4, int(round(tilt_deg / 3.0)) * 3)
    s = _skin_grow_hurt_cache.get(key)
    if s is None:
        base = get_skin_hurt_frame(skin_id, key[1], 0.0)
        scaled = pygame.transform.smoothscale(base, (_GROW_W, _GROW_H))
        s = pygame.transform.rotozoom(scaled, key[2], 1.0)
        _skin_grow_hurt_cache[key] = s
    return s
