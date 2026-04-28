"""Five ghost-parrot treatments for the ghost power-up.

Each `build_<name>_frame(src)` takes the normal already-outlined parrot
frame and returns a same-size surface with one ghost transformation
applied. Frame size is unchanged, so no canvas resizing or `Bird.draw`
offset adjustments are needed.

`build_ghost_variant_frames(build_fn)` returns 4 frames (one per wing
angle) ready to drop into the rotation cache.

Preview-only — nothing in the game imports this yet. The chosen variant
gets wired into `parrot.get_ghost_parrot` in a follow-up.
"""
import random
import pygame

from game.parrot import FRAMES as _NORMAL_FRAMES, _WING_ANGLES
from game.draw import blit_glow, lerp_color, WHITE, NEAR_BLACK


# Eye-area anchor (matches the original aviator-sunglasses centres in
# game/parrot.py: `_draw_sunglasses(surf, 50, 20)`). With the +2 px outline
# padding from `_add_outline`, the eyes sit at (52, 22) on the 68×64 frame.
EYE_L = (50, 22)
EYE_R = (56, 21)


def _silhouette(src: pygame.Surface) -> pygame.mask.Mask:
    return pygame.mask.from_surface(src, threshold=8)


def _filled_silhouette(src: pygame.Surface, color):
    """Solid-coloured copy of the parrot silhouette."""
    mask = _silhouette(src)
    return mask.to_surface(setcolor=color, unsetcolor=(0, 0, 0, 0))


# ── V1 — Bedsheet ghost ──────────────────────────────────────────────────────

def build_sheet_frame(src: pygame.Surface) -> pygame.Surface:
    """Classic Halloween bedsheet ghost: pure white parrot silhouette with
    two dark eye holes and a soft cyan halo."""
    w, h = src.get_size()
    out = pygame.Surface((w, h), pygame.SRCALPHA)

    # Soft cyan glow halo behind the silhouette
    blit_glow(out, w // 2, h // 2, max(w, h) // 2, (140, 220, 255), alpha=120)

    # White silhouette
    sheet = _filled_silhouette(src, (245, 250, 255, 235))
    out.blit(sheet, (0, 0))

    # Two dark eye holes
    pygame.draw.ellipse(out, (15, 15, 25), (EYE_L[0] - 3, EYE_L[1] - 2, 6, 5))
    pygame.draw.ellipse(out, (15, 15, 25), (EYE_R[0] - 3, EYE_R[1] - 2, 6, 5))
    # Tiny inner glints so the eyes don't read as flat black holes
    pygame.draw.circle(out, (255, 255, 255), (EYE_L[0] - 1, EYE_L[1] - 1), 1)
    pygame.draw.circle(out, (255, 255, 255), (EYE_R[0] - 1, EYE_R[1] - 1), 1)
    return out


# ── V2 — Translucent spirit ──────────────────────────────────────────────────

def build_spirit_frame(src: pygame.Surface) -> pygame.Surface:
    """Cyan spirit with a wide outer halo. Silhouette stays clearly blue
    rather than washing out to white."""
    w, h = src.get_size()
    out = pygame.Surface((w, h), pygame.SRCALPHA)

    # One wide soft halo behind the silhouette
    cx, cy = w // 2, h // 2
    blit_glow(out, cx, cy, max(w, h) // 2 + 6, (60, 180, 255), alpha=170)

    # Cyan silhouette body — solid enough to read as a coloured spirit
    sil = _filled_silhouette(src, (110, 200, 255, 240))
    out.blit(sil, (0, 0))

    # Subtle inner highlight near the upper body (drawn as a smaller
    # silhouette tinted lighter at lower alpha) so the spirit isn't flat
    hi = _silhouette(src).to_surface(
        setcolor=(220, 245, 255, 110), unsetcolor=(0, 0, 0, 0))
    out.blit(hi, (-1, -1))

    # Two bright eye dots so the silhouette has a face
    pygame.draw.circle(out, (255, 255, 255), EYE_L, 2)
    pygame.draw.circle(out, (255, 255, 255), EYE_R, 2)
    return out


# ── V3 — Pac-Man ghost ───────────────────────────────────────────────────────

def build_pacman_frame(src: pygame.Surface) -> pygame.Surface:
    """Cartoon Pac-Man-style ghost: solid cyan parrot silhouette with big
    white eyes and dark blue pupils."""
    w, h = src.get_size()
    out = pygame.Surface((w, h), pygame.SRCALPHA)

    # Solid cyan silhouette
    body = _filled_silhouette(src, (60, 200, 255, 255))
    out.blit(body, (0, 0))

    # Big white eyes with dark blue pupils — Pac-Man signature
    for ex, ey in (EYE_L, EYE_R):
        pygame.draw.ellipse(out, (245, 250, 255), (ex - 4, ey - 3, 8, 7))
        pygame.draw.ellipse(out, ( 25,  35,  90), (ex - 2, ey - 2, 4, 4))
    return out


# ── V4 — Green ectoplasm ─────────────────────────────────────────────────────

def build_ectoplasm_frame(src: pygame.Surface) -> pygame.Surface:
    """Ghostbusters-style green slime spirit. Vertical gradient fill,
    wispy edges, bright green BLEND_ADD halo."""
    w, h = src.get_size()
    out = pygame.Surface((w, h), pygame.SRCALPHA)

    # Bright green halo (drawn first, behind everything)
    blit_glow(out, w // 2, h // 2, max(w, h) // 2 + 2, (120, 255, 130), alpha=140)

    mask = _silhouette(src)
    sil_surf = mask.to_surface(setcolor=(255, 255, 255, 255), unsetcolor=(0, 0, 0, 0))

    # Vertical green gradient on a separate canvas, then masked by silhouette
    grad = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(h):
        t = y / max(1, h - 1)
        c = lerp_color((200, 255, 210), (40, 160,  90), t)
        pygame.draw.line(grad, (*c, 255), (0, y), (w - 1, y))
    grad.blit(sil_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    # Wispy edges: blit the silhouette twice at jittered offsets with low alpha
    rng = random.Random(7)
    for _ in range(2):
        wisp = mask.to_surface(setcolor=(180, 255, 200, 70),
                               unsetcolor=(0, 0, 0, 0))
        out.blit(wisp, (rng.randint(-1, 1), rng.randint(-1, 1)))

    out.blit(grad, (0, 0))

    # Bright yellow eye dots
    pygame.draw.circle(out, (255, 250, 180), EYE_L, 2)
    pygame.draw.circle(out, (255, 250, 180), EYE_R, 2)
    return out


# ── V5 — Dark wraith ─────────────────────────────────────────────────────────

def build_wraith_frame(src: pygame.Surface) -> pygame.Surface:
    """Dark silhouette with bright cyan rim-light and glowing white eyes."""
    w, h = src.get_size()
    out = pygame.Surface((w, h), pygame.SRCALPHA)

    # Faint outer cyan halo so the wraith reads against bright skies too
    blit_glow(out, w // 2, h // 2, max(w, h) // 2, (60, 180, 255), alpha=80)

    # Build a stamped-rim effect: blit the silhouette in cyan at the 4
    # cardinal offsets via BLEND_ADD so the edges glow.
    mask = _silhouette(src)
    rim = mask.to_surface(setcolor=(80, 220, 255, 200),
                          unsetcolor=(0, 0, 0, 0))
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        out.blit(rim, (dx, dy), special_flags=pygame.BLEND_ADD)

    # Dark filled silhouette in the centre (covers the rim except at edges)
    body = mask.to_surface(setcolor=(20, 25, 40, 250),
                           unsetcolor=(0, 0, 0, 0))
    out.blit(body, (0, 0))

    # Glowing white eyes (with a tiny additive halo behind each)
    for ex, ey in (EYE_L, EYE_R):
        blit_glow(out, ex, ey, 4, (200, 240, 255), alpha=200)
        pygame.draw.circle(out, (240, 250, 255), (ex, ey), 2)
        pygame.draw.circle(out, (255, 255, 255), (ex - 1, ey - 1), 1)
    return out


# ── Frame builder ────────────────────────────────────────────────────────────

def build_ghost_variant_frames(build_fn) -> list:
    """Return 4 ghost frames (one per wing angle) for the given variant."""
    return [build_fn(f) for f in _NORMAL_FRAMES]


# ── Registry ─────────────────────────────────────────────────────────────────

VARIANTS = [
    ("SHEET",      build_sheet_frame),
    ("SPIRIT",     build_spirit_frame),
    ("PACMAN",     build_pacman_frame),
    ("ECTOPLASM",  build_ectoplasm_frame),
    ("WRAITH",     build_wraith_frame),
]
