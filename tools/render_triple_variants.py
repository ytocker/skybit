"""Five `$` variants in the bold-stamp ↔ neon-glow space.

User feedback: "something between 2 (bold stamp) and 5 (neon glow) can
work, kick up the resolution." All variants use the bundled
LiberationSans-Bold font (game/assets) and 3× super-sampling, then
smoothscale down — same approach the in-game coin uses for crisp
edges.

Each variant is a draw function with the existing signature:

    fn(surf, cx, cy, pulse=0.0)

No coin disc — the glyph stands on its own. Imported by
`tools/render_triple_gameplay.py`. Does NOT modify any game module.
"""
import math
import pathlib
import pygame


# ── Palette ─────────────────────────────────────────────────────────────────
BILL_GREEN_LITE = (130, 220, 150)
BILL_GREEN      = ( 75, 165, 105)
BILL_GREEN_MID  = ( 55, 135,  85)
BILL_GREEN_DK   = ( 25,  85,  55)
BILL_GREEN_DEEP = ( 12,  50,  30)
NEON_HALO       = (110, 240, 160)
NEAR_BLACK      = ( 12,  16,  22)
WHITE           = (255, 255, 255)


_FONT_BOLD = str(
    pathlib.Path(__file__).resolve().parent.parent
    / "game" / "assets" / "LiberationSans-Bold.ttf"
)
_font_cache: dict = {}


def _bold_font(size):
    f = _font_cache.get(size)
    if f is None:
        f = pygame.font.Font(_FONT_BOLD, size)
        _font_cache[size] = f
    return f


# ── Crisp-glyph helpers ─────────────────────────────────────────────────────
GLYPH_SIZE = 30                # final on-screen height
SS         = 3                 # super-sample factor for crisp edges


def _crisp_glyph(text, size, color):
    """Render `text` at 3× resolution then smoothscale to `size`. Final
    glyph is anti-aliased and noticeably sharper than rendering at `size`
    directly, because the SDL hinter has more sub-pixel grid to work with."""
    big = _bold_font(size * SS).render(text, True, color)
    bw, bh = big.get_size()
    return pygame.transform.smoothscale(big, (bw // SS, bh // SS))


def _crisp_glyph_mask(size):
    """Same as _crisp_glyph but returns an opaque-white glyph used as a
    multiply mask for gradient/halo fills."""
    return _crisp_glyph("$", size, (255, 255, 255))


def _blit_centered(surf, glyph, center, dx=0, dy=0):
    r = glyph.get_rect(center=(center[0] + dx, center[1] + dy))
    surf.blit(glyph, r.topleft)


def _make_halo(color, size, layers=((6, 28), (4, 60), (2, 110))):
    """Build a per-glyph halo surface: stamp the `$` glyph multiple times
    in 8 directions at decreasing radii / increasing alpha. Result is a
    soft outer glow that mostly stays OUTSIDE the glyph silhouette
    because the centre overlaps and saturates first."""
    glyph = _crisp_glyph("$", size, color)
    gw, gh = glyph.get_size()
    pad = max(layer[0] for layer in layers) + 2
    halo = pygame.Surface((gw + pad * 2, gh + pad * 2), pygame.SRCALPHA)
    cx, cy = halo.get_width() // 2, halo.get_height() // 2
    for radius, alpha in layers:
        layer = glyph.copy()
        layer.set_alpha(alpha)
        for ang in range(0, 360, 45):
            ox = int(math.cos(math.radians(ang)) * radius)
            oy = int(math.sin(math.radians(ang)) * radius)
            r = layer.get_rect(center=(cx + ox, cy + oy))
            halo.blit(layer, r.topleft)
    return halo


# ── V1 — bold stamp + faint halo ────────────────────────────────────────────
def draw_v1_faint_halo(surf, cx, cy, pulse=0.0):
    """V2 (bold stamp) with the softest possible outer halo. Reads as a
    weighty stamp that's just slightly luminous."""
    halo = _make_halo(NEON_HALO, GLYPH_SIZE,
                      layers=((4, 18), (2, 35)))
    _blit_centered(surf, halo, (cx, cy + 1))

    out  = _crisp_glyph("$", GLYPH_SIZE, BILL_GREEN_DEEP)
    fill = _crisp_glyph("$", GLYPH_SIZE, BILL_GREEN_LITE)
    for ox, oy in ((-1, 0), (1, 0), (0, -1), (0, 1),
                   (-1, -1), (1, -1), (-1, 1), (1, 1)):
        _blit_centered(surf, out, (cx, cy + 1), dx=ox, dy=oy)
    _blit_centered(surf, fill, (cx, cy + 1))


# ── V2 — bold stamp + medium halo ───────────────────────────────────────────
def draw_v2_medium_halo(surf, cx, cy, pulse=0.0):
    """Bolder halo — definitely glowing, but the stamp body still reads as
    an inked banknote stamp, not an arcade neon."""
    breathe = 0.7 + 0.3 * (0.5 + 0.5 * math.sin(pulse * 1.5))
    halo = _make_halo(NEON_HALO, GLYPH_SIZE,
                      layers=((6, int(28 * breathe)),
                              (4, int(60 * breathe)),
                              (2, int(95 * breathe))))
    _blit_centered(surf, halo, (cx, cy + 1))

    out  = _crisp_glyph("$", GLYPH_SIZE, BILL_GREEN_DEEP)
    fill = _crisp_glyph("$", GLYPH_SIZE, BILL_GREEN_LITE)
    for ox, oy in ((-1, 0), (1, 0), (0, -1), (0, 1),
                   (-1, -1), (1, -1), (-1, 1), (1, 1)):
        _blit_centered(surf, out, (cx, cy + 1), dx=ox, dy=oy)
    _blit_centered(surf, fill, (cx, cy + 1))


# ── V3 — gradient body + halo ───────────────────────────────────────────────
def draw_v3_gradient_halo(surf, cx, cy, pulse=0.0):
    """Vertical green gradient (light top → deep bottom) inside a 1-px
    dark outline, with a medium halo. Adds dimensionality without going
    full embossed."""
    halo = _make_halo(NEON_HALO, GLYPH_SIZE,
                      layers=((6, 24), (4, 50), (2, 80)))
    _blit_centered(surf, halo, (cx, cy + 1))

    # Gradient body — render mask, multiply against per-row gradient.
    mask = _crisp_glyph_mask(GLYPH_SIZE)
    mw, mh = mask.get_size()
    grad = pygame.Surface((mw, mh), pygame.SRCALPHA)
    for yy in range(mh):
        t = yy / max(1, mh - 1)
        if t < 0.5:
            u = t / 0.5
            col = (
                int(BILL_GREEN_LITE[0] + (BILL_GREEN[0]    - BILL_GREEN_LITE[0]) * u),
                int(BILL_GREEN_LITE[1] + (BILL_GREEN[1]    - BILL_GREEN_LITE[1]) * u),
                int(BILL_GREEN_LITE[2] + (BILL_GREEN[2]    - BILL_GREEN_LITE[2]) * u),
                255,
            )
        else:
            u = (t - 0.5) / 0.5
            col = (
                int(BILL_GREEN[0]      + (BILL_GREEN_DK[0] - BILL_GREEN[0])      * u),
                int(BILL_GREEN[1]      + (BILL_GREEN_DK[1] - BILL_GREEN[1])      * u),
                int(BILL_GREEN[2]      + (BILL_GREEN_DK[2] - BILL_GREEN[2])      * u),
                255,
            )
        pygame.draw.line(grad, col, (0, yy), (mw, yy))
    grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    # Outline behind the gradient
    out_glyph = _crisp_glyph("$", GLYPH_SIZE, BILL_GREEN_DEEP)
    for ox, oy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        _blit_centered(surf, out_glyph, (cx, cy + 1), dx=ox, dy=oy)
    _blit_centered(surf, grad, (cx, cy + 1))


# ── V4 — stamp + inner shine (no halo, lit from inside) ────────────────────
def draw_v4_inner_shine(surf, cx, cy, pulse=0.0):
    """Bold stamp with a bright inner highlight only — no outer halo. Reads
    as a stamp catching light, more grounded than the haloed variants."""
    out  = _crisp_glyph("$", GLYPH_SIZE, BILL_GREEN_DEEP)
    body = _crisp_glyph("$", GLYPH_SIZE, BILL_GREEN)
    shine_top = _crisp_glyph("$", GLYPH_SIZE, BILL_GREEN_LITE)
    sheen = _crisp_glyph("$", GLYPH_SIZE, WHITE)
    sheen.set_alpha(120)

    # Outline
    for ox, oy in ((-1, 0), (1, 0), (0, -1), (0, 1),
                   (-1, -1), (1, -1), (-1, 1), (1, 1)):
        _blit_centered(surf, out, (cx, cy + 1), dx=ox, dy=oy)
    # Body
    _blit_centered(surf, body, (cx, cy + 1))
    # Highlight offset up-left for "lit from upper-left" feel
    _blit_centered(surf, shine_top, (cx, cy + 1), dx=-1, dy=-1)
    # Tiny white sheen blended on top
    _blit_centered(surf, sheen, (cx, cy + 1), dx=-1, dy=-2)


# ── V5 — embossed + halo ───────────────────────────────────────────────────
def draw_v5_embossed_halo(surf, cx, cy, pulse=0.0):
    """Three-layer embossed green (dark shadow, body, bright highlight)
    plus a medium halo. Most dimensional of the five — depth + glow."""
    halo = _make_halo(NEON_HALO, GLYPH_SIZE,
                      layers=((5, 22), (3, 50), (2, 80)))
    _blit_centered(surf, halo, (cx, cy + 1))

    shadow = _crisp_glyph("$", GLYPH_SIZE, BILL_GREEN_DEEP)
    body   = _crisp_glyph("$", GLYPH_SIZE, BILL_GREEN)
    hi     = _crisp_glyph("$", GLYPH_SIZE, BILL_GREEN_LITE)
    sheen  = _crisp_glyph("$", GLYPH_SIZE, WHITE)
    sheen.set_alpha(140)

    _blit_centered(surf, shadow, (cx, cy + 1), dx=2,  dy=2)
    _blit_centered(surf, body,   (cx, cy + 1))
    _blit_centered(surf, hi,     (cx, cy + 1), dx=-1, dy=-1)
    _blit_centered(surf, sheen,  (cx, cy + 1), dx=-1, dy=-2)


VARIANTS = {
    1: ("1 — faint halo",      draw_v1_faint_halo),
    2: ("2 — medium halo",     draw_v2_medium_halo),
    3: ("3 — gradient + halo", draw_v3_gradient_halo),
    4: ("4 — inner shine",     draw_v4_inner_shine),
    5: ("5 — embossed + halo", draw_v5_embossed_halo),
}
