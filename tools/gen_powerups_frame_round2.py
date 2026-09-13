"""Round-2 exploration sheet for the power-ups card FRAME (`_dark_panel`).

LEAD = direction C ("Raised Metal") only — 5 micro-variants tuning rim
weight / bevel strength / body gradient, plus the CURRENT shipped frame.
Renders the real in-context card (TRIPLE icon + name + blurb on the live
gradient+star background) so the frame is judged exactly as it ships.

Standalone — does NOT modify game/powerup_help.py. Run headless:
    SDL_VIDEODRIVER=dummy python tools/gen_powerups_frame_round2.py
"""
from __future__ import annotations

import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from game.config import W, H
from game.draw import lerp_color, UI_CREAM
from game.hud import (
    _font, _draw_overlay_stars,
    _GOLD_BRIGHT, _GOLD_PALE, _GOLD_DEEP,
    _PANEL_DARK, _PANEL_LIGHTER,
)
from game.powerup_help import (
    _powerup_icon, _wrap, _seeded_stars, _gradient_bg, _PANEL_OS,
)

CARD_W, CARD_H = 162, 124
RADIUS = 14
ALPHA = 215


# ── frame variants ───────────────────────────────────────────────────────────
#
# All variants composite at _PANEL_OS× then smoothscale to native, matching
# the shipped pipeline. Pre-scale thicknesses are chosen so they land at the
# intended native weight after the 4× downscale (smoothscale averages, so a
# 1px native line needs ~3-4px of pre-scale ink to survive as a clean line
# rather than a faint gray smear).

def _frame_current(rect, alpha):
    """CURRENT shipped _dark_panel — flat panel + single 2px gold rim."""
    os_ = _PANEL_OS
    ow, oh = rect.width * os_, rect.height * os_
    orad = RADIUS * os_
    pnl = pygame.Surface((ow, oh), pygame.SRCALPHA)
    pygame.draw.rect(pnl, (*_PANEL_DARK, alpha), (0, 0, ow, oh),
                     border_radius=orad)
    pygame.draw.rect(pnl, (*_GOLD_BRIGHT, 130), (0, 0, ow, oh),
                     width=2 * os_, border_radius=orad)
    return pygame.transform.smoothscale(pnl, rect.size)


def _body_gradient(pnl, ow, oh, orad, alpha, delta_pct):
    """Vertical _PANEL_LIGHTER(top) → _PANEL_DARK(bottom) fill, but with the
    value delta clamped to `delta_pct` of the full LIGHTER→DARK span so it
    reads as 'lit' without banding at downscale or fighting the icon glow.
    Painted into a rounded mask so corners stay clean."""
    grad = pygame.Surface((ow, oh), pygame.SRCALPHA)
    # Center the small swing on the panel's mean tone so the interior never
    # dips below CURRENT's flat _PANEL_DARK brightness under the blurb.
    base = _PANEL_DARK
    top = lerp_color(base, _PANEL_LIGHTER, delta_pct)
    bot = base
    for y in range(oh):
        t = y / max(1, oh - 1)
        c = lerp_color(top, bot, t)
        pygame.draw.line(grad, (*c, alpha), (0, y), (ow - 1, y))
    mask = pygame.Surface((ow, oh), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, ow, oh),
                     border_radius=orad)
    grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    pnl.blit(grad, (0, 0))


def _two_tone_rim(pnl, ow, oh, orad, rim_native_px):
    """Two-tone metallic rim landing at ~`rim_native_px` total at native size —
    deliberately NOT heavier than CURRENT's 2px, or six cards become a wall of
    gold. The outer ~1px is _GOLD_DEEP (the milled under-ply / shadow side of
    the metal) and the inner ~1px is _GOLD_BRIGHT (the lit top ply). Alphas are
    held below opaque so the combined rim reads at roughly CURRENT's weight
    rather than blaring."""
    os_ = _PANEL_OS
    # Total rim = rim_native_px. Split it: outer half deep, inner half bright.
    total = rim_native_px * os_
    deep_w = total                       # deep fills the whole rim band first…
    bright_w = max(os_, (rim_native_px - 1) * os_)  # …bright overlays inner ply
    pygame.draw.rect(pnl, (*_GOLD_DEEP, 200), (0, 0, ow, oh),
                     width=deep_w, border_radius=orad)
    inset = os_  # bright ply pulled in by 1 native px so a deep edge shows
    pygame.draw.rect(pnl, (*_GOLD_BRIGHT, 175),
                     (inset, inset, ow - 2 * inset, oh - 2 * inset),
                     width=bright_w, border_radius=max(1, orad - inset))


def _inner_bevel(pnl, ow, oh, orad, rim_native_px,
                 pale_alpha, dark_alpha, bevel_native_px):
    """The hero detail. A pale highlight on the top+left inner edge and a dark
    accent on the bottom+right inner edge, sitting just inboard of the rim so
    the tile reads as physically raised (light from top-left). Drawn as two
    rounded-rect strokes clipped to half the rect via additive/normal blits —
    cheaper and crisper at corners than per-segment arcs because it follows the
    same border_radius the rim uses."""
    os_ = _PANEL_OS
    # Bevel ring sits one native px inside the bright ply.
    inset = (rim_native_px + 1) * os_
    # `bevel_native_px` here is the PRE-scale stroke width (2-3px) chosen so it
    # lands as a clean ~1px line after the 4x downscale rather than a 2px smear;
    # smoothscale averaging means a literal 1-native-px target would vanish.
    bw = max(2, bevel_native_px)
    bx, by = inset, inset
    brw, brh = ow - 2 * inset, oh - 2 * inset
    brad = max(1, orad - inset)

    # Highlight (top + left): draw a full rounded stroke on its own layer,
    # then keep only the top-left half via a diagonal alpha mask so the
    # gradient of light wraps the two corners that catch the light.
    def _half_ring(color, alpha, keep_top_left):
        layer = pygame.Surface((ow, oh), pygame.SRCALPHA)
        pygame.draw.rect(layer, (*color, alpha), (bx, by, brw, brh),
                         width=bw, border_radius=brad)
        mask = pygame.Surface((ow, oh), pygame.SRCALPHA)
        # Diagonal split: top-left triangle vs bottom-right triangle. A soft
        # 1-native-px feather at the diagonal avoids a hard seam where the two
        # halves meet at the off-light corners.
        if keep_top_left:
            pygame.draw.polygon(mask, (255, 255, 255, 255),
                                [(0, 0), (ow, 0), (0, oh)])
        else:
            pygame.draw.polygon(mask, (255, 255, 255, 255),
                                [(ow, 0), (ow, oh), (0, oh)])
        layer.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        pnl.blit(layer, (0, 0))

    # The shadow side must read DARKER than the panel floor. NEAR_BLACK
    # (15,15,30) is actually a touch lighter than _PANEL_DARK (12,8,38), so it
    # vanishes; pure black is the only value that subtracts below the interior
    # and makes the bottom-right edge recede — the half of the bevel that sells
    # the raise.
    _half_ring(_GOLD_PALE, pale_alpha, keep_top_left=True)
    _half_ring((0, 0, 0), dark_alpha, keep_top_left=False)


def _frame_C(rect, alpha, *, rim_px, pale_a, dark_a,
             grad_pct, bevel_px=3):
    """Direction C — Raised Metal. Two-tone rim + small body gradient +
    1px inner bevel. Composited at _PANEL_OS× then smoothscaled."""
    os_ = _PANEL_OS
    ow, oh = rect.width * os_, rect.height * os_
    orad = RADIUS * os_
    pnl = pygame.Surface((ow, oh), pygame.SRCALPHA)

    _body_gradient(pnl, ow, oh, orad, alpha, grad_pct)
    _two_tone_rim(pnl, ow, oh, orad, rim_px)
    _inner_bevel(pnl, ow, oh, orad, rim_px, pale_a, dark_a, bevel_px)

    return pygame.transform.smoothscale(pnl, rect.size)


# Variant table — label carries the exact tuning parameters.
VARIANTS = [
    ("CURRENT", "rim 2px  no bevel  flat body",
     lambda r: _frame_current(r, ALPHA)),
    ("V1 baseline-C", "rim 2px  bevel pale120/dark80  grad 10%",
     lambda r: _frame_C(r, ALPHA, rim_px=2, pale_a=120, dark_a=80,
                        grad_pct=0.10)),
    ("V2 strong bevel", "rim 2px  bevel pale130/dark95  grad 10%",
     lambda r: _frame_C(r, ALPHA, rim_px=2, pale_a=130, dark_a=95,
                        grad_pct=0.10)),
    ("V3 subtle", "rim 2px  bevel pale90/dark60  grad 8%",
     lambda r: _frame_C(r, ALPHA, rim_px=2, pale_a=90, dark_a=60,
                        grad_pct=0.08)),
    ("V4 stronger grad", "rim 2px  bevel pale120/dark80  grad 12%",
     lambda r: _frame_C(r, ALPHA, rim_px=2, pale_a=120, dark_a=80,
                        grad_pct=0.12)),
    ("V5 premium", "rim 2px  bevel pale115/dark85  grad 11%",
     lambda r: _frame_C(r, ALPHA, rim_px=2, pale_a=115, dark_a=85,
                        grad_pct=0.11)),
]


# ── in-context card render ────────────────────────────────────────────────────
def _draw_card_content(surf, card):
    """Mirror powerup_help's interior layout: TRIPLE icon, gold name, blurb."""
    _powerup_icon(surf, "triple", card.centerx, card.y + 32, 48)
    nimg = _font(14, True).render("TRIPLE", True, _GOLD_BRIGHT)
    surf.blit(nimg, nimg.get_rect(center=(card.centerx, card.y + 66)))
    f = _font(12, True)
    for li, line in enumerate(_wrap(f, "Coins are worth 3x", CARD_W - 16)[:3]):
        img = f.render(line, True, UI_CREAM)
        surf.blit(img, img.get_rect(center=(card.centerx,
                                            card.y + 84 + li * 14)))


def _make_bg(w, h, stars, t):
    """The exact help-screen backdrop (purple→navy gradient + twinkle stars),
    cropped to the requested tile size."""
    full = pygame.Surface((W, H))
    _gradient_bg(full)
    _draw_overlay_stars(full, stars, t)
    return pygame.transform.scale(full.subsurface((0, 0, min(w, W),
                                                   min(h, H))).copy(), (w, h)) \
        if (w, h) != (W, H) else full


def _render_card_on_bg(frame_fn, bg_patch):
    """Composite a single card (frame + content) onto a backdrop patch sized to
    the card with a small margin so the surrounding stars show."""
    surf = bg_patch.copy()
    margin = (surf.get_width() - CARD_W) // 2
    card = pygame.Rect(margin, (surf.get_height() - CARD_H) // 2,
                       CARD_W, CARD_H)
    surf.blit(frame_fn(card), card.topleft)
    _draw_card_content(surf, card)
    return surf, card


def _to_grayscale(img):
    """Numpy-free luminance conversion (Rec.601). PixelArray lets us rewrite
    each pixel in place so the value-only readout works without numpy, which
    the WASM/native runtime never relies on anyway."""
    gray = img.copy()
    pa = pygame.PixelArray(gray)
    w, h = gray.get_size()
    for x in range(w):
        for y in range(h):
            r, g, b, _a = gray.unmap_rgb(pa[x, y])
            lum = int(r * 0.299 + g * 0.587 + b * 0.114)
            pa[x, y] = (lum, lum, lum)
    pa.close()
    return gray


# ── sheet assembly ────────────────────────────────────────────────────────────
def main():
    stars = _seeded_stars()
    t = 1.4

    # A representative slice of the real backdrop, reused for every tile so the
    # cards sit on the same star pattern the player sees.
    bg_full = pygame.Surface((W, H))
    _gradient_bg(bg_full)
    _draw_overlay_stars(bg_full, stars, t)

    pad = 24
    zoom = 2.7
    tile_card_w = CARD_W + 28   # backdrop margin around each card
    tile_card_h = CARD_H + 28
    tw = int(tile_card_w * zoom)
    th = int(tile_card_h * zoom)
    label_h = 40
    cols = 3
    rows = 2

    sheet_w = pad * 2 + cols * tw + (cols - 1) * pad
    # extra space at bottom for the 1× native strips (color row + label,
    # grayscale header + grayscale row + label, plus breathing room)
    strip_h = 380
    sheet_w = max(sheet_w, 1180)
    sheet_h = pad + 70 + rows * (th + label_h + pad) + strip_h

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((18, 14, 26))

    title = _font(26, True).render(
        "POWER-UPS CARD FRAME — RAISED METAL (round 2)", True, _GOLD_BRIGHT)
    sheet.blit(title, (pad, 18))
    sub = _font(13, False).render(
        "Direction C micro-variants in context @2.7x  +  1x native strips "
        "(color & grayscale) below", True, UI_CREAM)
    sheet.blit(sub, (pad, 50))

    grid_top = pad + 70

    # source backdrop patch for one tile (centered slice of the real bg)
    def bg_patch():
        sx = (W - tile_card_w) // 2
        sy = (H - tile_card_h) // 2
        return bg_full.subsurface((sx, sy, tile_card_w, tile_card_h)).copy()

    for idx, (name, params, fn) in enumerate(VARIANTS):
        col = idx % cols
        row = idx // cols
        x = pad + col * (tw + pad)
        y = grid_top + row * (th + label_h + pad)

        card_img, _ = _render_card_on_bg(fn, bg_patch())
        big = pygame.transform.scale(card_img, (tw, th))
        sheet.blit(big, (x, y))
        # thin frame around the tile
        pygame.draw.rect(sheet, (60, 50, 80), (x, y, tw, th), 1)

        nlab = _font(15, True).render(name, True, _GOLD_PALE)
        sheet.blit(nlab, (x, y + th + 4))
        plab = _font(11, False).render(params, True, UI_CREAM)
        sheet.blit(plab, (x, y + th + 22))

    # ── 1× native strips ──────────────────────────────────────────────────────
    strip_y = grid_top + rows * (th + label_h + pad) + 6
    pygame.draw.line(sheet, (70, 60, 90), (pad, strip_y),
                     (sheet_w - pad, strip_y), 1)

    head = _font(14, True).render(
        "AT TRUE 1x NATIVE SIZE (162x124) — color row + grayscale row "
        "(confirm the raised read is VALUE, not hue)", True, _GOLD_BRIGHT)
    sheet.blit(head, (pad, strip_y + 8))

    # Build each card at native size on the real backdrop.
    native_cards = []
    for name, params, fn in VARIANTS:
        card_img, _ = _render_card_on_bg(fn, bg_patch())
        # crop to just the card (strip the surrounding margin)
        m = (card_img.get_width() - CARD_W) // 2
        my = (card_img.get_height() - CARD_H) // 2
        native_cards.append(
            (name, card_img.subsurface((m, my, CARD_W, CARD_H)).copy()))

    nx = pad
    ny = strip_y + 34
    gap = 14
    for name, img in native_cards:
        sheet.blit(img, (nx, ny))
        lab = _font(10, True).render(name, True, _GOLD_PALE)
        sheet.blit(lab, (nx, ny + CARD_H + 2))
        nx += CARD_W + gap

    # grayscale row of the same native cards, to verify value separation.
    gy = ny + CARD_H + 22
    ghead = _font(12, True).render("GRAYSCALE (value check):", True, UI_CREAM)
    sheet.blit(ghead, (pad, gy - 2))
    gx = pad
    gy2 = gy + 16
    for name, img in native_cards:
        sheet.blit(_to_grayscale(img), (gx, gy2))
        gx += CARD_W + gap

    out = "/home/user/skybit/docs/powerups_frame_polish/round_2.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("wrote", out, sheet.get_size())


if __name__ == "__main__":
    main()
