"""Five double-bar (cifrão-style) `$` variants for the 3× powerup.

User picked V3 (gradient + halo) but wants the dollar sign rendered with
two vertical bars through the S — the cifrão / classic-cartoon-money
look. Liberation Sans renders a single-bar `$`, so we composite at 3×
super-sample: render `S`, draw two vertical bars over it, then
smoothscale down. Anti-aliasing falls out of the smoothscale step.

All five variants share V3's base treatment (vertical green gradient
body + medium green halo + 1-px dark outline) — only the bar geometry
varies. Each is the same draw signature as the existing
`game.dollar_coin_glyphs.draw_coin_font_bold`:

    fn(surf, cx, cy, pulse=0.0)

Imported by `tools/render_triple_gameplay.py`. Does NOT modify any game
module.
"""
import math
import pathlib
import pygame


# ── Palette (same as the V3 picker that the user approved) ──────────────────
BILL_GREEN_LITE = (130, 220, 150)
BILL_GREEN      = ( 75, 165, 105)
BILL_GREEN_DK   = ( 25,  85,  55)
BILL_GREEN_DEEP = ( 12,  50,  30)
NEON_HALO       = (110, 240, 160)
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


GLYPH_SIZE = 30                # final on-screen S height
SS         = 3                 # super-sample factor for crisp edges


def _double_bar_dollar(size, color,
                        bar_w_frac=0.07,
                        bar_extend_frac=0.10,
                        bar_centre_gap_frac=0.08,
                        bar_top_highlight=False):
    """Render an `S` glyph at 3× SS, then composite two vertical bars
    near the CENTRE of the S to make a cifrão-style double-bar dollar
    sign. Smoothscale to final resolution.

    Geometry follows real cifrão references: the two bars sit where the
    single bar of a regular `$` would be — straddling the S centre line
    by ±(bar_centre_gap_frac/2) of S width. They do NOT split the S into
    thirds. They DO extend a small distance above and below the S
    (matching the single-bar `$` overshoot in Liberation Sans).

    bar_w_frac          — bar thickness as fraction of S width
    bar_extend_frac     — how far bars extend above/below the S
    bar_centre_gap_frac — distance between bar CENTRES, as fraction of S width
    bar_top_highlight   — if True, paint a bright cap at the top of each bar
    """
    big_s = _bold_font(size * SS).render("S", True, color)
    sw, sh = big_s.get_size()

    bar_w  = max(2, int(sw * bar_w_frac))
    extend = int(sh * bar_extend_frac)
    full_h = sh + extend * 2

    out = pygame.Surface((sw, full_h), pygame.SRCALPHA)

    half_gap = (sw * bar_centre_gap_frac) / 2.0
    bar1_cx = int(sw / 2 - half_gap)
    bar2_cx = int(sw / 2 + half_gap)

    # Bars first — S blits on top so the strokes look like they pass
    # through the bars naturally (where S has ink, S wins).
    for cx_b in (bar1_cx, bar2_cx):
        pygame.draw.rect(out, color,
                         pygame.Rect(cx_b - bar_w // 2, 0, bar_w, full_h))

    out.blit(big_s, (0, extend))

    if bar_top_highlight:
        cap_h = max(2, int(extend * 0.35))
        cap_color = (
            min(255, color[0] + 60),
            min(255, color[1] + 60),
            min(255, color[2] + 60),
            255,
        )
        for cx_b in (bar1_cx, bar2_cx):
            pygame.draw.rect(out, cap_color,
                             pygame.Rect(cx_b - bar_w // 2, 0, bar_w, cap_h))

    return pygame.transform.smoothscale(out, (sw // SS, full_h // SS))


def _make_halo_from_glyph(glyph, layers):
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


def _blit_centered(surf, glyph, center, dx=0, dy=0):
    r = glyph.get_rect(center=(center[0] + dx, center[1] + dy))
    surf.blit(glyph, r.topleft)


def _draw_v3_treatment(surf, cx, cy, *,
                       bar_w_frac, bar_extend_frac=0.08,
                       bar_centre_gap_frac=0.10,
                       bar_top_highlight=False):
    """Apply V3's gradient + halo + outline to a double-bar `$` whose
    geometry is parameterised. Variants below all call this with
    different bar params."""
    body_kwargs = dict(
        bar_w_frac=bar_w_frac,
        bar_extend_frac=bar_extend_frac,
        bar_centre_gap_frac=bar_centre_gap_frac,
        bar_top_highlight=bar_top_highlight,
    )

    # Halo
    halo_glyph = _double_bar_dollar(GLYPH_SIZE, NEON_HALO, **body_kwargs)
    halo = _make_halo_from_glyph(halo_glyph,
                                 layers=((6, 24), (4, 50), (2, 80)))
    _blit_centered(surf, halo, (cx, cy + 1))

    # Mask for gradient body
    mask = _double_bar_dollar(GLYPH_SIZE, (255, 255, 255), **body_kwargs)
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

    # Outline behind the gradient fill
    out_glyph = _double_bar_dollar(GLYPH_SIZE, BILL_GREEN_DEEP, **body_kwargs)
    for ox, oy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        _blit_centered(surf, out_glyph, (cx, cy + 1), dx=ox, dy=oy)
    _blit_centered(surf, grad, (cx, cy + 1))


# ── V1 — touching: bars almost merged at centre ─────────────────────────────
def draw_v1_touching(surf, cx, cy, pulse=0.0):
    _draw_v3_treatment(surf, cx, cy,
                       bar_w_frac=0.06,
                       bar_extend_frac=0.08,
                       bar_centre_gap_frac=0.07)


# ── V2 — narrow gap (classic cifrão weight) ────────────────────────────────
def draw_v2_narrow(surf, cx, cy, pulse=0.0):
    _draw_v3_treatment(surf, cx, cy,
                       bar_w_frac=0.06,
                       bar_extend_frac=0.08,
                       bar_centre_gap_frac=0.10)


# ── V3 — clear gap (bit more breathing room) ───────────────────────────────
def draw_v3_clear(surf, cx, cy, pulse=0.0):
    _draw_v3_treatment(surf, cx, cy,
                       bar_w_frac=0.06,
                       bar_extend_frac=0.08,
                       bar_centre_gap_frac=0.13)


# ── V4 — bold narrow (cartoon-money weight) ────────────────────────────────
def draw_v4_bold(surf, cx, cy, pulse=0.0):
    _draw_v3_treatment(surf, cx, cy,
                       bar_w_frac=0.09,
                       bar_extend_frac=0.08,
                       bar_centre_gap_frac=0.10)


# ── V5 — bold + bright top caps (3D feel) ──────────────────────────────────
def draw_v5_capped(surf, cx, cy, pulse=0.0):
    _draw_v3_treatment(surf, cx, cy,
                       bar_w_frac=0.09,
                       bar_extend_frac=0.08,
                       bar_centre_gap_frac=0.10,
                       bar_top_highlight=True)


VARIANTS = {
    1: ("1 — touching",   draw_v1_touching),
    2: ("2 — narrow gap", draw_v2_narrow),
    3: ("3 — clear gap",  draw_v3_clear),
    4: ("4 — bold narrow", draw_v4_bold),
    5: ("5 — bold + caps", draw_v5_capped),
}
