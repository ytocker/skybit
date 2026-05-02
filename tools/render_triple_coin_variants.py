"""Five `$ in the middle of the coin` variants for 3X-mode coins.

When 3X mode is active, the in-world coins should display the dollar sign
in the middle (replacing the embossed parrot) — same gold rim, gradient
body, rope rim, and sparkles as the standard coin. Each variant only
differs in HOW the `$` is stamped on the centre.

Each builder returns a 120×120 face surface, drop-in compatible with
`game.entities._COIN_FACE_CACHE`. Imported by
`tools/render_triple_coin_gameplay.py`. Does NOT modify any game module.
"""
import math
import os
import pathlib
import sys

import pygame


# ── Palette (mirrors entities._get_coin_face + dollar_coin_glyphs) ─────────
GOLD_HI         = (255, 232, 130)
GOLD_MID        = (240, 195,  55)
GOLD_LO         = (190, 130,  20)
OUTLINE_DK      = ( 95,  50,   0)
OUTLINE_LT      = (150,  90,  10)
DARK_AMBER      = ( 75,  35,   0)
LITE_AMBER      = (210, 165,  50)

BILL_GREEN_LITE = (130, 220, 150)
BILL_GREEN      = ( 75, 165, 105)
BILL_GREEN_DK   = ( 35, 100,  65)
BILL_GREEN_DEEP = ( 12,  50,   0)
NEON_HALO       = (110, 240, 160)


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


def _build_coin_base(coin_r):
    """Build the 120×120 coin face at SS=8 — outline + body gradient + rope
    rim + specular highlight, **without** the parrot. Returns the SS-sized
    surface, the body_mask (for downstream masking), and final_d.

    Mirrors the build steps in entities._get_coin_face exactly except the
    parrot section is omitted. The caller (each variant) stamps `$` on
    the center then smoothscales to final_d × final_d."""
    SS = 8
    DISPLAY_D = coin_r * 2 + 4
    CACHE_MUL = 4
    final_d = DISPLAY_D * CACHE_MUL
    size = final_d * SS

    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx = cy = size // 2
    r_outer = size // 2 - SS
    r_outline = max(SS * 2, r_outer // 6)
    r_body = r_outer - r_outline

    # 1) Double-band outline.
    pygame.draw.circle(surf, OUTLINE_DK, (cx, cy), r_outer)
    pygame.draw.circle(surf, OUTLINE_LT, (cx, cy), r_outer - SS)

    # 2) Vertical gradient body.
    body_surf = pygame.Surface((size, size), pygame.SRCALPHA)
    y0, y1 = cy - r_body, cy + r_body
    for yy in range(y0, y1 + 1):
        t = (yy - y0) / max(1, (y1 - y0))
        if t < 0.4:
            u = t / 0.4
            col = (
                int(GOLD_HI[0]  + (GOLD_MID[0] - GOLD_HI[0])  * u),
                int(GOLD_HI[1]  + (GOLD_MID[1] - GOLD_HI[1])  * u),
                int(GOLD_HI[2]  + (GOLD_MID[2] - GOLD_HI[2])  * u),
            )
        else:
            u = (t - 0.4) / 0.6
            col = (
                int(GOLD_MID[0] + (GOLD_LO[0]  - GOLD_MID[0]) * u),
                int(GOLD_MID[1] + (GOLD_LO[1]  - GOLD_MID[1]) * u),
                int(GOLD_MID[2] + (GOLD_LO[2]  - GOLD_MID[2]) * u),
            )
        pygame.draw.line(body_surf, col, (0, yy), (size, yy))
    body_mask = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(body_mask, (255, 255, 255, 255), (cx, cy), r_body)
    body_surf.blit(body_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(body_surf, (0, 0))

    # 3) Twisted-rope rim.
    n_segs = 22
    ring_r = r_outer - r_outline // 2
    seg_w = max(SS * 3, r_outline + SS)
    for i in range(n_segs):
        ang = i * (math.tau / n_segs)
        ang_next = (i + 1) * (math.tau / n_segs)
        mid = (ang + ang_next) / 2
        sx = cx + math.cos(mid) * ring_r
        sy = cy + math.sin(mid) * ring_r
        seg_len = int((math.tau / n_segs) * ring_r * 0.95)
        seg = pygame.Surface((seg_len, seg_w), pygame.SRCALPHA)
        col       = DARK_AMBER if i % 2 == 0 else LITE_AMBER
        highlight = LITE_AMBER if i % 2 == 0 else GOLD_HI
        pygame.draw.ellipse(seg, col, seg.get_rect())
        pygame.draw.ellipse(seg, highlight, seg.get_rect().inflate(-SS, -SS))
        rotated = pygame.transform.rotate(seg, -math.degrees(mid))
        r_rect = rotated.get_rect(center=(int(sx), int(sy)))
        surf.blit(rotated, r_rect.topleft)

    # 4) [Parrot omitted — variant-specific `$` stamped after smoothscale.]

    # 5) Specular highlight crescent.
    hl = pygame.Surface((size, size), pygame.SRCALPHA)
    hl_rect = pygame.Rect(cx - r_body + r_body // 5,
                          cy - r_body + r_body // 6,
                          int(r_body * 1.1), int(r_body * 0.5))
    pygame.draw.ellipse(hl, (255, 255, 235, 110), hl_rect)
    hl.blit(body_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(hl, (0, 0))

    return pygame.transform.smoothscale(surf, (final_d, final_d))


# ── `$` stamp helpers (operate at 120×120 cache resolution) ─────────────────
SS_GLYPH = 3   # super-sample for the `$` stamp


def _crisp_dollar(font_size, color):
    """Render `$` at 3× SS then smoothscale, for crisp glyph edges."""
    big = _bold_font(font_size * SS_GLYPH).render("$", True, color)
    bw, bh = big.get_size()
    return pygame.transform.smoothscale(big, (bw // SS_GLYPH, bh // SS_GLYPH))


def _gradient_dollar(font_size):
    """Build a `$` filled with the green vertical gradient — same colours
    as the in-game pickup icon (light top → mid → deep bottom)."""
    mask = _crisp_dollar(font_size, (255, 255, 255))
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
    return grad


def _stamp_dollar(face, cx, cy, font_size, with_outline=True,
                   with_halo=False, fill_override=None):
    """Stamp the `$` onto the face surface at (cx, cy). Outline (1 px) is
    drawn behind the fill for legibility against the gold body. Halo is
    a soft outer glow stamped 8 directions × 3 radii."""
    if with_halo:
        halo_glyph = _crisp_dollar(font_size, NEON_HALO)
        layers = ((4, 30), (3, 60), (2, 90))
        gw, gh = halo_glyph.get_size()
        pad = max(layer[0] for layer in layers) + 2
        halo = pygame.Surface((gw + pad * 2, gh + pad * 2), pygame.SRCALPHA)
        hcx, hcy = halo.get_width() // 2, halo.get_height() // 2
        for radius, alpha in layers:
            layer = halo_glyph.copy()
            layer.set_alpha(alpha)
            for ang in range(0, 360, 45):
                ox = int(math.cos(math.radians(ang)) * radius)
                oy = int(math.sin(math.radians(ang)) * radius)
                r = layer.get_rect(center=(hcx + ox, hcy + oy))
                halo.blit(layer, r.topleft)
        face.blit(halo, halo.get_rect(center=(cx, cy)).topleft)

    if fill_override is not None:
        body = _crisp_dollar(font_size, fill_override)
    else:
        body = _gradient_dollar(font_size)

    body_rect = body.get_rect(center=(cx, cy))
    if with_outline:
        out = _crisp_dollar(font_size, BILL_GREEN_DEEP)
        for ox, oy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            face.blit(out, (body_rect.x + ox, body_rect.y + oy))
    face.blit(body, body_rect.topleft)


# ── Variant face builders ───────────────────────────────────────────────────
def build_v1_small(coin_r):
    face = _build_coin_base(coin_r)
    cx = cy = face.get_width() // 2
    _stamp_dollar(face, cx, cy + 1, font_size=44)
    return face


def build_v2_medium(coin_r):
    face = _build_coin_base(coin_r)
    cx = cy = face.get_width() // 2
    _stamp_dollar(face, cx, cy + 1, font_size=58)
    return face


def build_v3_large(coin_r):
    face = _build_coin_base(coin_r)
    cx = cy = face.get_width() // 2
    _stamp_dollar(face, cx, cy + 1, font_size=72)
    return face


def build_v4_medium_halo(coin_r):
    face = _build_coin_base(coin_r)
    cx = cy = face.get_width() // 2
    _stamp_dollar(face, cx, cy + 1, font_size=58, with_halo=True)
    return face


def build_v5_dark_contrast(coin_r):
    face = _build_coin_base(coin_r)
    cx = cy = face.get_width() // 2
    _stamp_dollar(face, cx, cy + 1, font_size=58,
                  fill_override=BILL_GREEN_DEEP, with_outline=False)
    return face


VARIANTS = {
    1: ("1 — small $",       build_v1_small),
    2: ("2 — medium $",      build_v2_medium),
    3: ("3 — large $",       build_v3_large),
    4: ("4 — medium + halo", build_v4_medium_halo),
    5: ("5 — dark contrast", build_v5_dark_contrast),
}
