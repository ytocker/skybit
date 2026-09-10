"""
Five `$` glyph treatments on the same gold-coin body.

The user picked the COIN concept from `game/dollar_variants.py` but flagged
that the central `$` glyph isn't crystal clear at icon scale. This module
keeps the disc identical across all five and varies only the `$` so the
choice is purely about glyph legibility.

Each function: draw_coin_<style>(surf, cx, cy, pulse=0.0).

Preview-only — nothing in the game imports this yet. The chosen treatment
gets folded into entities.PowerUp in a follow-up.
"""
import math
import os
import pathlib
import pygame

from game.config import POWERUP_R
from game.draw import COIN_GOLD, COIN_DARK, WHITE, NEAR_BLACK
from game.dollar_variants import BILL_GREEN, BILL_GREEN_DK

# Extra palette for the V3 (gradient + halo) treatment used by
# draw_coin_font_bold below.
BILL_GREEN_LITE = (130, 220, 150)
BILL_GREEN_DEEP = ( 12,  50,  30)
NEON_HALO       = (110, 240, 160)


# ── shared coin body ────────────────────────────────────────────────────────

def _draw_coin_disc(surf, cx, cy):
    """Identical disc for every variant: dark rim → gold fill → warm inner
    ring → specular pinprick. Only the `$` overlay differs."""
    r = POWERUP_R
    pygame.draw.circle(surf, COIN_DARK, (cx, cy), r + 1)
    pygame.draw.circle(surf, COIN_GOLD, (cx, cy), r)
    pygame.draw.circle(surf, (255, 235, 110), (cx, cy), r - 3, 1)
    pygame.draw.circle(surf, WHITE, (cx - r // 2, cy - r // 2), 2)


# ── font cache (shared between font-rendered styles) ────────────────────────

_font_cache: dict = {}
_FONT_BOLD = str(
    pathlib.Path(__file__).parent / "assets" / "LiberationSans-Bold.ttf"
)


def _bold_font(size):
    f = _font_cache.get(size)
    if f is None:
        f = pygame.font.Font(_FONT_BOLD, size)
        _font_cache[size] = f
    return f


def _blit_outlined_text(surf, text, font, center, fill, outline,
                        outline_w=1):
    """Render `text` with a solid outline by stamping the silhouette in 8
    neighbour offsets, then the fill on top. Produces a clean readable glyph."""
    body = font.render(text, True, fill)
    edge = font.render(text, True, outline)
    rect = body.get_rect(center=center)
    for dx, dy in ((-outline_w, 0), (outline_w, 0),
                   (0, -outline_w), (0, outline_w),
                   (-outline_w, -outline_w), (outline_w, -outline_w),
                   (-outline_w, outline_w), (outline_w, outline_w)):
        surf.blit(edge, (rect.x + dx, rect.y + dy))
    surf.blit(body, rect.topleft)


# ── helpers shared by hand-drawn glyphs ─────────────────────────────────────

def _arc_glyph(surf, cx, cy, height, color, weight, outline=None,
               outline_w=1):
    """Two-arc + center-bar `$` glyph. Used by heavy_stroke."""
    import math
    h = max(8, int(height))
    w = max(6, int(h * 0.62))
    bar_top = (cx, cy - h // 2 - 1)
    bar_bot = (cx, cy + h // 2 + 1)
    half = h // 2
    top_rect = pygame.Rect(cx - w // 2, cy - half, w, half)
    bot_rect = pygame.Rect(cx - w // 2, cy, w, half)
    if outline is not None:
        pygame.draw.line(surf, outline, bar_top, bar_bot, weight + outline_w * 2)
        pygame.draw.arc(surf, outline, top_rect.inflate(2, 2),
                        math.radians(20), math.radians(220),
                        weight + outline_w * 2)
        pygame.draw.arc(surf, outline, bot_rect.inflate(2, 2),
                        math.radians(200), math.radians(400),
                        weight + outline_w * 2)
    pygame.draw.line(surf, color, bar_top, bar_bot, weight)
    pygame.draw.arc(surf, color, top_rect, math.radians(20),
                    math.radians(220), weight)
    pygame.draw.arc(surf, color, bot_rect, math.radians(200),
                    math.radians(400), weight)


def _block_glyph(surf, cx, cy, height, color, outline=None):
    """Block-letter `$`: three horizontal bars + two side connectors + the
    center vertical bar. Pure rectangles, reads bold at any size."""
    h = max(10, int(height))
    w = max(8, int(h * 0.62))
    t = max(2, h // 7)               # bar thickness
    half_w = w // 2
    half_h = h // 2

    # Layout the three horizontal bars
    rects = [
        # top bar
        pygame.Rect(cx - half_w, cy - half_h, w, t),
        # middle bar
        pygame.Rect(cx - half_w, cy - t // 2, w, t),
        # bottom bar
        pygame.Rect(cx - half_w, cy + half_h - t, w, t),
        # upper-left connector (top-bar bottom → middle-bar top, on the left)
        pygame.Rect(cx - half_w, cy - half_h + t, t, half_h - t),
        # lower-right connector (middle-bar bottom → bottom-bar top, on the right)
        pygame.Rect(cx + half_w - t, cy + t // 2, t, half_h - t),
        # center vertical bar (the through-stroke)
        pygame.Rect(cx - t // 2 + 1, cy - half_h - 2, t - 1, h + 4),
    ]
    if outline is not None:
        for r in rects:
            pygame.draw.rect(surf, outline, r.inflate(2, 2))
    for r in rects:
        pygame.draw.rect(surf, color, r)


# ── V1 — gradient $ + soft halo (no coin disc) ──────────────────────────────
# User picked this treatment after rejecting the gold-coin background and
# four rounds of double-bar cifrão attempts. Single-bar $, sized like the
# original. Crisp 3× super-sample, vertical green gradient body, soft
# outer halo, dark outline behind for readability on any background.
#
# Helpers + cache live below this function; cached per-call so a static
# pulse value (which is the typical case) reuses the same surface.

_GLYPH_SIZE = 30
_GLYPH_SS = 3
_glyph_cache: dict = {}


def _crisp_glyph(text, size, color):
    """Render at 3× SS then smoothscale — sharper than rendering at `size`
    directly because the SDL hinter has more sub-pixel grid to work with."""
    key = (text, size, color)
    cached = _glyph_cache.get(key)
    if cached is not None:
        return cached
    big = _bold_font(size * _GLYPH_SS).render(text, True, color)
    bw, bh = big.get_size()
    out = pygame.transform.smoothscale(big, (bw // _GLYPH_SS, bh // _GLYPH_SS))
    _glyph_cache[key] = out
    return out


_halo_cache: "pygame.Surface | None" = None


def _make_dollar_halo():
    """Build the green halo once: stamp the `$` glyph in 8 directions at
    decreasing radii / increasing alpha. Returns a soft outer glow layer."""
    global _halo_cache
    if _halo_cache is not None:
        return _halo_cache
    glyph = _crisp_glyph("$", _GLYPH_SIZE, NEON_HALO)
    gw, gh = glyph.get_size()
    layers = ((6, 24), (4, 50), (2, 80))
    pad = max(layer[0] for layer in layers) + 2
    halo = pygame.Surface((gw + pad * 2, gh + pad * 2), pygame.SRCALPHA)
    hcx, hcy = halo.get_width() // 2, halo.get_height() // 2
    for radius, alpha in layers:
        layer = glyph.copy()
        layer.set_alpha(alpha)
        for ang in range(0, 360, 45):
            ox = int(math.cos(math.radians(ang)) * radius)
            oy = int(math.sin(math.radians(ang)) * radius)
            r = layer.get_rect(center=(hcx + ox, hcy + oy))
            halo.blit(layer, r.topleft)
    _halo_cache = halo
    return halo


_grad_body_cache: "pygame.Surface | None" = None


def _make_dollar_gradient_body():
    """Vertical green gradient inside the `$` silhouette — light-top to
    deep-bottom. Built once; the result is RGBA-masked to the glyph."""
    global _grad_body_cache
    if _grad_body_cache is not None:
        return _grad_body_cache
    mask = _crisp_glyph("$", _GLYPH_SIZE, (255, 255, 255))
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
    _grad_body_cache = grad
    return grad


def draw_coin_font_bold(surf, cx, cy, pulse=0.0):
    halo = _make_dollar_halo()
    surf.blit(halo, halo.get_rect(center=(cx, cy + 1)).topleft)

    out_glyph = _crisp_glyph("$", _GLYPH_SIZE, BILL_GREEN_DEEP)
    body = _make_dollar_gradient_body()
    body_rect = body.get_rect(center=(cx, cy + 1))
    for ox, oy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        surf.blit(out_glyph, (body_rect.x + ox, body_rect.y + oy))
    surf.blit(body, body_rect.topleft)


# ── V2 — heavy stroke arcs ──────────────────────────────────────────────────

def draw_coin_heavy_stroke(surf, cx, cy, pulse=0.0):
    _draw_coin_disc(surf, cx, cy)
    h = int(POWERUP_R * 1.5)
    _arc_glyph(surf, cx, cy, height=h, color=BILL_GREEN_DK, weight=5)
    _arc_glyph(surf, cx, cy, height=h, color=BILL_GREEN,    weight=3)


# ── V3 — block letter ───────────────────────────────────────────────────────

def draw_coin_block_letter(surf, cx, cy, pulse=0.0):
    _draw_coin_disc(surf, cx, cy)
    h = int(POWERUP_R * 1.55)
    _block_glyph(surf, cx, cy, height=h, color=BILL_GREEN,
                 outline=BILL_GREEN_DK)


# ── V4 — high-contrast monochrome ───────────────────────────────────────────

def draw_coin_mono_contrast(surf, cx, cy, pulse=0.0):
    _draw_coin_disc(surf, cx, cy)
    f = _bold_font(28)
    # Black body for max contrast on gold
    _blit_outlined_text(surf, "$", f, (cx, cy + 1),
                        fill=NEAR_BLACK, outline=NEAR_BLACK, outline_w=1)
    # Crisp white highlight stamp offset to the upper-left so the glyph
    # reads as struck/embossed.
    body = f.render("$", True, WHITE)
    rect = body.get_rect(center=(cx - 1, cy))
    body.set_alpha(170)
    surf.blit(body, rect.topleft)
    # Re-stamp the black on top with a tiny mask so the highlight only
    # bleeds at the upper-left edge — gives a stamped-coin feel.
    body2 = f.render("$", True, NEAR_BLACK)
    surf.blit(body2, body2.get_rect(center=(cx, cy + 1)).topleft)


# ── V5 — embossed 3D ────────────────────────────────────────────────────────

def draw_coin_embossed_3d(surf, cx, cy, pulse=0.0):
    _draw_coin_disc(surf, cx, cy)
    f = _bold_font(28)
    # Bottom-right shadow layer
    sh = f.render("$", True, BILL_GREEN_DK)
    surf.blit(sh, sh.get_rect(center=(cx + 1, cy + 2)).topleft)
    # Top-left highlight layer
    hi = f.render("$", True, (255, 245, 200))
    surf.blit(hi, hi.get_rect(center=(cx - 1, cy)).topleft)
    # Mid-tone body on top
    body = f.render("$", True, BILL_GREEN)
    surf.blit(body, body.get_rect(center=(cx, cy + 1)).topleft)


# ── registry ────────────────────────────────────────────────────────────────

VARIANTS = (
    ("FONT BOLD",    draw_coin_font_bold),
    ("HEAVY STROKE", draw_coin_heavy_stroke),
    ("BLOCK",        draw_coin_block_letter),
    ("MONO",         draw_coin_mono_contrast),
    ("EMBOSSED",     draw_coin_embossed_3d),
)
