"""Procedural umbrella graphics — the in-world PICKUP icon (C4: cream
badge ring + teal/white scalloped canopy + J-hook) and the in-play
OVERLAY canopy that floats above Pip's head while the umbrella power-up
is active (W2b: V4-direction canopy at +50% width, upright, no handle).

Same idiom as the rest of the procedural icon family (lottery, knight,
poison): build at SS× supersample, smoothscale down. Surfaces are
cached at module level so the per-frame cost is one alpha blit.
"""

from __future__ import annotations

import math

import pygame

from game.config import POWERUP_R


# ── Palette (matches the round-2 icon C4 swatches) ────────────────────────────
INK            = ( 22,  18,  34)
CANOPY_CREAM   = (250, 244, 222)
CANOPY_TEAL    = ( 60, 176, 188)
CANOPY_TEAL_HI = (120, 214, 222)
FERRULE        = (246, 222, 120)
RING_CREAM     = (250, 238, 206)

# In-play overlay uses a touch-brighter teal so the canopy separates from
# the dark night thunderstorm sky (lifted ~12% off the icon palette — see
# tools/render_umbrella_ingame_options.py round 2 polish).
OVERLAY_TEAL    = ( 84, 185, 196)
OVERLAY_TEAL_HI = (136, 219, 226)


# Pip-sprite geometry. The head ellipse centre sits at sprite (47, 21) in
# a 64×60 sprite (centre 32, 30) → offset (+15, −9). The CROWN is ~9 px
# above the ellipse centre, so the head-crown offset from Pip's (x, y) is
# roughly (+15, −18). The umbrella hem floats `_OVERLAY_FLOAT_GAP` px
# above that.
_HEAD_DX = 15
_HEAD_DY = -18
_OVERLAY_FLOAT_GAP = 7


SS = 7  # supersample factor — matches the icon tool


# ── Low-level canopy + handle drawing ────────────────────────────────────────


def _canopy(surf, cx, cy, span, rise, panels, ink_w,
            teal, teal_hi, *, ferrule=True):
    """Draw a scalloped open canopy centred at (cx, cy) on `surf`. `span`
    is the half-width (rim-to-centre); `rise` is the dome height; panels
    alternate teal / cream; the rim is re-inked as one continuous line so
    the outline survives the smoothscale at small footprints."""
    hem_y = cy
    cols = (teal, CANOPY_CREAM)
    # Panels (alternating colours under a dome arc).
    for i in range(panels):
        t0 = i / panels
        t1 = (i + 1) / panels
        # Each panel is the slice between two ribs, bounded by the dome
        # arc at the top and the hem line at the bottom.
        poly = [(cx - span + 2 * span * t0, hem_y),
                (cx - span + 2 * span * t1, hem_y)]
        steps = 6
        for k in range(steps + 1):
            t = t1 - (t1 - t0) * (k / steps)
            ax = cx - span + 2 * span * t
            # cos-falloff across the span — same curve as the icon's _canopy.
            n = (t * 2) - 1
            ay = hem_y - rise * max(0.0, math.cos(n * math.pi / 2))
            poly.append((ax, ay))
        col = cols[i % 2]
        pygame.draw.polygon(surf, col, poly)
        pygame.draw.polygon(surf, INK, poly, ink_w)
    # Sheen highlight: a thin teal-hi arc along the upper-left of the dome.
    sheen_pts = []
    for k in range(16):
        t = -0.7 + (k / 15) * 0.6                # left third of the dome
        ax = cx + span * t
        ay = hem_y - rise * max(0.0, math.cos(t * math.pi / 2)) + ink_w
        sheen_pts.append((ax, ay))
    pygame.draw.lines(surf, teal_hi, False, sheen_pts, max(1, ink_w // 2))
    # Re-ink dome arc + hem so the outline reads as a continuous bold rim.
    rim_pts = []
    steps = 48
    for k in range(steps + 1):
        t = (k / steps) * 2 - 1
        ax = cx - span + 2 * span * (k / steps)
        ay = hem_y - rise * max(0.0, math.cos(t * math.pi / 2))
        rim_pts.append((ax, ay))
    pygame.draw.lines(surf, INK, False, rim_pts, ink_w)
    pygame.draw.line(surf, INK, (cx - span, hem_y), (cx + span, hem_y), ink_w)
    pygame.draw.line(surf, INK, (cx - span, hem_y),
                     (cx - span, hem_y - rise * 0.04), ink_w)
    pygame.draw.line(surf, INK, (cx + span, hem_y),
                     (cx + span, hem_y - rise * 0.04), ink_w)
    if ferrule:
        # Knob centred on the apex.
        tip_top = cy - rise - max(2, ink_w)
        pygame.draw.line(surf, INK, (cx, cy - rise + 2), (cx, tip_top),
                         max(2, ink_w))
        pygame.draw.circle(surf, FERRULE, (int(cx), int(tip_top)),
                           max(2, int(ink_w * 0.9)))
        pygame.draw.circle(surf, INK, (int(cx), int(tip_top)),
                           max(2, int(ink_w * 0.9)), max(1, ink_w // 2))


def _j_handle(surf, cx, top_y, length, span, ink_w):
    """Vertical shaft + J-hook crook hanging below the hem at (cx, top_y),
    drawn UPRIGHT — never rotates with the parrot's body tilt."""
    bot_y = top_y + length
    hook_r = max(int(span * 0.20), ink_w * 2)
    pygame.draw.line(surf, INK, (cx, top_y), (cx, bot_y), ink_w)
    rect = pygame.Rect(cx - hook_r * 2, bot_y - hook_r, hook_r * 2, hook_r * 2)
    pygame.draw.arc(surf, INK, rect, math.radians(-95), math.radians(180),
                    ink_w)


# ── Public draw entry points ─────────────────────────────────────────────────


_ICON_CACHE: dict[int, pygame.Surface] = {}


def _build_pickup_icon(footprint_px: int) -> pygame.Surface:
    """Build the C4 pickup icon at `footprint_px` square: cream badge
    ring + gold edge + enlarged teal/white scalloped canopy + J-hook
    handle dropping just inside the rim. Supersampled then smoothscaled
    so the scallops + ring rim stay crisp."""
    px = footprint_px * SS
    big = pygame.Surface((px, px), pygame.SRCALPHA)
    c = px // 2
    ink = max(2, int(SS * 0.9))
    # Cream badge ring with gold edge — framed-charm read.
    ring_r = int(px * 0.46)
    pygame.draw.circle(big, RING_CREAM, (c, c), ring_r)
    pygame.draw.circle(big, FERRULE, (c, c), ring_r, max(2, int(SS * 0.7)))
    pygame.draw.circle(big, INK, (c, c), ring_r, ink)
    pygame.draw.circle(big, INK, (c, c), int(ring_r * 0.86),
                       max(1, int(SS * 0.4)))
    # Enlarged canopy filling the upper ring.
    span = int(px * 0.34)
    rise = int(px * 0.26)
    uy = c - int(px * 0.02)
    _j_handle(big, c, uy, int(px * 0.30), span, ink)
    _canopy(big, c, uy, span, rise, panels=6, ink_w=ink,
            teal=CANOPY_TEAL, teal_hi=CANOPY_TEAL_HI, ferrule=True)
    return pygame.transform.smoothscale(big,
                                        (footprint_px, footprint_px))


def draw_pickup_icon(surf: pygame.Surface, cx: int, cy: int, pulse: float):
    """Blit the C4 pickup icon centred at (cx, cy) with a gentle sine bob
    on `pulse` (same idiom as the other in-world power-up icons)."""
    # Footprint matches the visual size of other 14-radius pickups — the
    # other procedural icons (lottery, knight) render at ~3× POWERUP_R.
    fp = POWERUP_R * 3
    icon = _ICON_CACHE.get(fp)
    if icon is None:
        icon = _build_pickup_icon(fp)
        _ICON_CACHE[fp] = icon
    bob = int(round(math.sin(pulse * 1.0) * 2))
    r = icon.get_rect(center=(int(cx), int(cy) + bob))
    surf.blit(icon, r.topleft)


# ── In-play overlay (umbrella floating above Pip's head) ─────────────────────


_OVERLAY_CACHE: pygame.Surface | None = None
_OVERLAY_HEM: tuple[int, int] | None = None


def _build_overlay() -> tuple[pygame.Surface, tuple[int, int]]:
    """Build the W2b umbrella overlay: V4-direction canopy at +50% width
    (head_span 20 × 1.50 = 30), upright, no handle, with the brightened
    overlay teal so it pops against the night thunderstorm sky. Returns
    the surface + the (x, y) of the hem-centre in surface coords."""
    head_span = 30                          # 20 base × 1.50 (W2b)
    span = head_span * SS
    rise = int(span * 0.62)
    ink = max(3, int(SS * 1.5))
    margin = int(span * 0.6)
    w = span * 2 + margin * 2
    h = rise + int(span * 0.5) + margin * 2
    big = pygame.Surface((w, h), pygame.SRCALPHA)
    cx = w // 2
    hem_y = margin + rise + int(span * 0.30)
    _canopy(big, cx, hem_y, span, rise, panels=5, ink_w=ink,
            teal=OVERLAY_TEAL, teal_hi=OVERLAY_TEAL_HI, ferrule=True)
    # Smoothscale 1/SS.
    final_w = w // SS
    final_h = h // SS
    small = pygame.transform.smoothscale(big, (final_w, final_h))
    return small, (cx // SS, hem_y // SS)


def head_crown_position(bird_x: float, bird_y: float,
                        tilt_deg: float) -> tuple[float, float]:
    """Where Pip's head crown lands on screen for the given body tilt.
    The head sprite sits offset from Pip's body centre (+15 right, −18
    up); when the body rotates the head moves through 2D, so the offset
    vector must rotate with `tilt_deg` for the umbrella to stay above
    the actual head — not behind it when Pip dives forward.

    pygame.transform.rotozoom uses CCW-for-positive degrees in screen
    coords (y-down)."""
    a = math.radians(tilt_deg)
    cosA, sinA = math.cos(a), math.sin(a)
    dx = _HEAD_DX * cosA + _HEAD_DY * sinA
    dy = -_HEAD_DX * sinA + _HEAD_DY * cosA
    return bird_x + dx, bird_y + dy


def draw_overlay(surf: pygame.Surface, bird_x: float, bird_y: float,
                 tilt_deg: float):
    """Render the umbrella above Pip's head at (bird_x, bird_y) for the
    given body `tilt_deg`. The overlay is drawn UPRIGHT — it never
    inherits Pip's tilt — but its position tracks his head crown so it
    stays seated as he flaps and dives.

    Purely visual: the umbrella is NOT part of the bird's collision
    hitbox; pillars must hit Pip's actual circle to count as a death."""
    global _OVERLAY_CACHE, _OVERLAY_HEM
    if _OVERLAY_CACHE is None:
        _OVERLAY_CACHE, _OVERLAY_HEM = _build_overlay()
    crown_x, crown_y = head_crown_position(bird_x, bird_y, tilt_deg)
    hem_x, hem_y = _OVERLAY_HEM
    target_x = crown_x
    target_y = crown_y - _OVERLAY_FLOAT_GAP
    blit_x = int(target_x - hem_x)
    blit_y = int(target_y - hem_y)
    surf.blit(_OVERLAY_CACHE, (blit_x, blit_y))
