"""Five distinctive 3× powerup-icon variants — preview only.

Each variant is a draw function with the same signature as the existing
`game.dollar_coin_glyphs.draw_coin_font_bold` so it can drop in via a
monkey-patch on the import alias used in `game.entities`:

    fn(surf, cx, cy, pulse=0.0)

Centred on (cx, cy) with the in-game POWERUP_R footprint (≈14 px). All
five concepts use techniques the codebase already trusts: super-sampled
caches for curves, per-row gradient lines, polygon/circle/ellipse
primitives. Palette borrowed from game.draw where appropriate.

These functions are imported by `tools/render_triple_gameplay.py`. They
do NOT modify any game module.
"""
import math
import pygame


# ── Palette (same values as game.draw / dollar_variants) ────────────────────
COIN_GOLD_DEEP  = (200, 140,   0)   # = COIN_DARK in game.draw — outline tone
COIN_GOLD_BODY  = (255, 210,  20)   # = COIN_GOLD
COIN_GOLD_HI    = (255, 232, 130)   # warm highlight
COIN_GOLD_LO    = (190, 130,  20)   # gradient bottom
NEAR_BLACK      = ( 18,  20,  28)
WHITE           = (255, 255, 255)
UI_RED          = (230,  40,  40)
UI_RED_DK       = (150,  20,  20)
BILL_GREEN      = ( 75, 165, 105)
BILL_GREEN_DK   = ( 40, 110,  70)

POWERUP_R = 14


# ── Shared helpers ──────────────────────────────────────────────────────────
def _gold_disc(surf, cx, cy, r, with_rim=True, with_specular=True):
    """Standard gold coin disc — used by stack / trinity / banner concepts."""
    SS = 4
    d = (r + 2) * 2 * SS
    big = pygame.Surface((d, d), pygame.SRCALPHA)
    bx = by = d // 2
    R = r * SS

    # Dark rim
    if with_rim:
        pygame.draw.circle(big, COIN_GOLD_DEEP, (bx, by), R + SS)
    # Vertical gold gradient body
    grad = pygame.Surface((d, d), pygame.SRCALPHA)
    y0, y1 = by - R, by + R
    for yy in range(y0, y1 + 1):
        t = (yy - y0) / max(1, (y1 - y0))
        if t < 0.45:
            u = t / 0.45
            col = (
                int(COIN_GOLD_HI[0]   + (COIN_GOLD_BODY[0] - COIN_GOLD_HI[0])   * u),
                int(COIN_GOLD_HI[1]   + (COIN_GOLD_BODY[1] - COIN_GOLD_HI[1])   * u),
                int(COIN_GOLD_HI[2]   + (COIN_GOLD_BODY[2] - COIN_GOLD_HI[2])   * u),
            )
        else:
            u = (t - 0.45) / 0.55
            col = (
                int(COIN_GOLD_BODY[0] + (COIN_GOLD_LO[0]   - COIN_GOLD_BODY[0]) * u),
                int(COIN_GOLD_BODY[1] + (COIN_GOLD_LO[1]   - COIN_GOLD_BODY[1]) * u),
                int(COIN_GOLD_BODY[2] + (COIN_GOLD_LO[2]   - COIN_GOLD_BODY[2]) * u),
            )
        pygame.draw.line(grad, col, (0, yy), (d, yy))
    mask = pygame.Surface((d, d), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), (bx, by), R)
    grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    big.blit(grad, (0, 0))

    if with_specular:
        # Soft upper-left crescent highlight
        sp = pygame.Surface((d, d), pygame.SRCALPHA)
        pygame.draw.ellipse(sp, (255, 255, 220, 130),
                            (bx - R + R // 5, by - R + R // 6,
                             int(R * 1.0), int(R * 0.45)))
        sp.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        big.blit(sp, (0, 0))

    target = pygame.transform.smoothscale(big, ((r + 2) * 2, (r + 2) * 2))
    surf.blit(target, (cx - (r + 2), cy - (r + 2)))


def _bold_text(text, size, color, bold=True):
    f = pygame.font.SysFont(None, size, bold=bold)
    return f.render(text, True, color)


def _outlined_text(surf, text, size, center, fill, outline, outline_w=1):
    f = pygame.font.SysFont(None, size, bold=True)
    img_fill = f.render(text, True, fill)
    img_out  = f.render(text, True, outline)
    cx, cy = center
    r = img_fill.get_rect(center=(cx, cy))
    for ox in range(-outline_w, outline_w + 1):
        for oy in range(-outline_w, outline_w + 1):
            if ox == 0 and oy == 0:
                continue
            surf.blit(img_out, (r.x + ox, r.y + oy))
    surf.blit(img_fill, r.topleft)


# ── V1 — coin stack (3 stacked, slight perspective) ────────────────────────
def draw_v1_stack(surf, cx, cy, pulse=0.0):
    """Three gold coins stacked vertically, top one tilted forward, bold "3"
    glyph on the front face. Reads as a growing pile of loot."""
    # Coins drawn back-to-front so the top one sits on top.
    # Slight breathing pulse → vertical offset of ~1 px max.
    bob = int(math.sin(pulse * 1.5) * 1)
    coin_r = POWERUP_R - 2          # 12 — leave room for stack height
    # Bottom coin
    _gold_disc(surf, cx, cy + 6 + bob, coin_r, with_specular=False)
    # Middle coin (slightly offset right for "leaning" depth)
    _gold_disc(surf, cx + 1, cy + 1 + bob, coin_r, with_specular=False)
    # Top coin — full disc + specular + bold "3" glyph
    _gold_disc(surf, cx, cy - 4 + bob, coin_r + 1, with_specular=True)

    _outlined_text(surf, "3", 22, (cx, cy - 4 + bob),
                   fill=UI_RED, outline=NEAR_BLACK, outline_w=1)


# ── V2 — trinity coins (triangular cluster) ─────────────────────────────────
def draw_v2_trinity(surf, cx, cy, pulse=0.0):
    """Three small coins arranged as an equilateral triangle, all face-on so
    the multi-coin read is unambiguous at 28 px. A subtle pulse breathes
    them in unison; a tiny gold sparkle in the triangle's centre adds the
    "magic" cue. Mario-style multi-coin cluster."""
    coin_r = 6
    spread = 8
    breathe = 1.0 + 0.04 * math.sin(pulse * 1.6)   # subtle scale pulse
    rr = max(4, int(coin_r * breathe))
    positions = [
        (cx,           cy - spread),                 # top
        (cx - spread,  cy + spread // 2 + 2),        # bottom-left
        (cx + spread,  cy + spread // 2 + 2),        # bottom-right
    ]
    # Each coin gets a tiny embossed "$" so it reads as currency, not just
    # gold blob. Glyph is small but readable.
    for (px, py) in positions:
        _gold_disc(surf, px, py, rr, with_specular=True)
        _outlined_text(surf, "$", 11, (px, py),
                       fill=BILL_GREEN, outline=BILL_GREEN_DK, outline_w=1)

    # Centre sparkle — pulses on/off out of sync with the coin breathe.
    twink = 0.5 + 0.5 * math.sin(pulse * 2.5)
    a = int(200 * twink)
    if a > 30:
        spark = pygame.Surface((9, 9), pygame.SRCALPHA)
        pygame.draw.line(spark, (255, 255, 220, a), (4, 0), (4, 8), 1)
        pygame.draw.line(spark, (255, 255, 220, a), (0, 4), (8, 4), 1)
        pygame.draw.circle(spark, (255, 255, 255, a), (4, 4), 1)
        surf.blit(spark, (cx - 4, cy + 1))


# ── V3 — jackpot star burst ─────────────────────────────────────────────────
def draw_v3_jackpot(surf, cx, cy, pulse=0.0):
    """6-point gold star with bold "3×" inside, short ray pricks radiating,
    faint amber halo. Slot-machine jackpot read."""
    SS = 4
    R = (POWERUP_R + 4) * SS
    d = R * 2 + 4 * SS
    big = pygame.Surface((d, d), pygame.SRCALPHA)
    bx = by = d // 2

    # Halo
    halo = pygame.Surface((d, d), pygame.SRCALPHA)
    halo_r = int((POWERUP_R + 4) * SS * 1.0)
    halo_pulse = 0.7 + 0.3 * (0.5 + 0.5 * math.sin(pulse * 1.8))
    for ring_i in range(4):
        a = int(48 * halo_pulse * (4 - ring_i) / 4)
        pygame.draw.circle(halo, (255, 200, 80, a), (bx, by),
                           halo_r + ring_i * 2 * SS)
    big.blit(halo, (0, 0))

    # Ray pricks — 12 short rays
    n_rays = 12
    inner_r = int((POWERUP_R + 5) * SS)
    outer_r = int((POWERUP_R + 8) * SS)
    for i in range(n_rays):
        a = (i * math.tau / n_rays) + math.sin(pulse * 0.8) * 0.05
        x1, y1 = bx + math.cos(a) * inner_r, by + math.sin(a) * inner_r
        x2, y2 = bx + math.cos(a) * outer_r, by + math.sin(a) * outer_r
        pygame.draw.line(big, (255, 215, 100, 220),
                         (int(x1), int(y1)), (int(x2), int(y2)),
                         max(2, SS // 2))

    # 6-point star polygon (alternating outer/inner radii)
    n_pts = 6
    star_outer = int((POWERUP_R + 2) * SS)
    star_inner = int(star_outer * 0.50)
    star_pts = []
    for i in range(n_pts * 2):
        rr = star_outer if i % 2 == 0 else star_inner
        a = -math.pi / 2 + i * math.pi / n_pts
        star_pts.append((bx + math.cos(a) * rr, by + math.sin(a) * rr))

    # Dark outline + gold fill
    dark_pts = [(x, y + 2 * SS) for (x, y) in star_pts]   # drop shadow
    pygame.draw.polygon(big, (50, 30, 0, 110), dark_pts)

    # Star body — gradient via per-row mask
    star_surf = pygame.Surface((d, d), pygame.SRCALPHA)
    for yy in range(d):
        t = max(0.0, min(1.0, (yy - (by - star_outer)) / max(1, star_outer * 2)))
        col = (
            int(COIN_GOLD_HI[0]   + (COIN_GOLD_LO[0]   - COIN_GOLD_HI[0])   * t),
            int(COIN_GOLD_HI[1]   + (COIN_GOLD_LO[1]   - COIN_GOLD_HI[1])   * t),
            int(COIN_GOLD_HI[2]   + (COIN_GOLD_LO[2]   - COIN_GOLD_HI[2])   * t),
        )
        pygame.draw.line(star_surf, col, (0, yy), (d, yy))
    star_mask = pygame.Surface((d, d), pygame.SRCALPHA)
    pygame.draw.polygon(star_mask, (255, 255, 255, 255), star_pts)
    star_surf.blit(star_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    big.blit(star_surf, (0, 0))

    # Star outline
    pygame.draw.polygon(big, COIN_GOLD_DEEP, star_pts, max(2, SS // 2))

    # Smoothscale to display
    final = pygame.transform.smoothscale(big, (d // SS, d // SS))
    surf.blit(final, (cx - (d // SS) // 2, cy - (d // SS) // 2))

    # "3×" text drawn AT display resolution so it stays crisp.
    # Use a tight pixel layout, bold red on white edge.
    _outlined_text(surf, "3X", 16, (cx, cy + 1),
                   fill=UI_RED, outline=WHITE, outline_w=1)


# ── V4 — holographic 3X sticker (rounded rectangle, foil) ──────────────────
def draw_v4_foil_sticker(surf, cx, cy, pulse=0.0):
    """Rounded-rect foil sticker with saturated diagonal holographic
    gradient (hot pink → cyan → mint → gold) and bold black '3X' text.
    Premium-loot collectible feel — distinctly NOT a coin."""
    SS = 4
    W_SHOW, H_SHOW = (POWERUP_R + 3) * 2, (POWERUP_R + 1) * 2
    sw, sh = W_SHOW * SS, H_SHOW * SS
    big = pygame.Surface((sw, sh), pygame.SRCALPHA)

    radius = int(6 * SS)
    rect = pygame.Rect(0, 0, sw, sh)

    # Saturated holographic stops — strong colour shift so the foil reads
    # as foil, not pale grey. Hot pink → magenta → cyan → mint → gold.
    stops = [
        (255, 110, 200),   # hot pink
        (200, 100, 255),   # magenta-violet
        ( 90, 200, 255),   # cyan
        (130, 245, 180),   # mint
        (255, 215,  90),   # gold
    ]
    diag_len = sw + sh
    shift = int((math.sin(pulse * 0.6) * 0.5 + 0.5) * diag_len * 0.20)
    grad = pygame.Surface((sw, sh), pygame.SRCALPHA)
    # Build a 1-D gradient strip of length diag_len, then per row blit a
    # sw-wide slice starting at offset (yy + shift). Same approach as the
    # ghost icon — fast and gives a clean continuous diagonal.
    strip = pygame.Surface((diag_len, 1), pygame.SRCALPHA)
    for xx in range(diag_len):
        t = xx / max(1, diag_len - 1)
        seg = t * (len(stops) - 1)
        i0 = int(seg)
        i1 = min(len(stops) - 1, i0 + 1)
        u = seg - i0
        a, b = stops[i0], stops[i1]
        col = (
            int(a[0] + (b[0] - a[0]) * u),
            int(a[1] + (b[1] - a[1]) * u),
            int(a[2] + (b[2] - a[2]) * u),
            255,
        )
        strip.set_at((xx, 0), col)
    for yy in range(sh):
        offset = (yy + shift) % diag_len
        # Take a sw-wide slice starting at `offset`. Wrap-around is rare
        # at this scale; for simplicity slice with clamping.
        if offset + sw <= diag_len:
            grad.blit(strip, (0, yy), area=pygame.Rect(offset, 0, sw, 1))
        else:
            first = diag_len - offset
            grad.blit(strip, (0, yy), area=pygame.Rect(offset, 0, first, 1))
            grad.blit(strip, (first, yy),
                      area=pygame.Rect(0, 0, sw - first, 1))

    # Mask to rounded rect
    mask = pygame.Surface((sw, sh), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), rect, border_radius=radius)
    grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    big.blit(grad, (0, 0))

    # Soft top-half white sheen for foil shimmer
    sheen = pygame.Surface((sw, sh), pygame.SRCALPHA)
    for yy in range(sh // 2):
        a = int(120 * (1.0 - yy / max(1, sh // 2)) ** 1.5)
        if a > 0:
            pygame.draw.line(sheen, (255, 255, 255, a), (0, yy), (sw, yy))
    sheen.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    big.blit(sheen, (0, 0))

    # Outer black border
    pygame.draw.rect(big, (15, 15, 25, 255), rect,
                     width=max(2, SS // 2), border_radius=radius)

    final = pygame.transform.smoothscale(big, (W_SHOW, H_SHOW))
    surf.blit(final, (cx - W_SHOW // 2, cy - H_SHOW // 2))

    # Bold black "3X" — drawn at display resolution for crispness.
    _outlined_text(surf, "3X", 18, (cx, cy + 1),
                   fill=(15, 15, 25), outline=(255, 255, 255), outline_w=1)


# ── V5 — banner-wrapped coin ────────────────────────────────────────────────
def draw_v5_banner(surf, cx, cy, pulse=0.0):
    """Single oversized gold coin with a red diagonal banner sash and bold
    white 'X3' text. Premium-chest-reward read while keeping the gold-coin
    silhouette familiar."""
    bob = int(math.sin(pulse * 1.2) * 1)
    cy = cy + bob

    # Bigger coin than the default since the banner overlays it
    _gold_disc(surf, cx, cy, POWERUP_R + 1, with_specular=True)

    # Banner — a horizontal-leaning trapezoid across the lower 2/3 of the
    # coin. Width chosen so the banner stays just inside the coin diameter
    # at its inner edges and just slightly past at its end-rivets, NOT
    # extending into the surrounding sky.
    banner_h = 9
    banner_y = cy + 1
    bw = POWERUP_R - 2
    pts = [
        (cx - bw,     banner_y - banner_h // 2 - 1),   # top-left  notch up
        (cx + bw,     banner_y - banner_h // 2 + 1),
        (cx + bw,     banner_y + banner_h // 2 + 1),
        (cx - bw,     banner_y + banner_h // 2 - 1),
    ]
    # Drop shadow
    shadow_pts = [(x + 1, y + 2) for (x, y) in pts]
    pygame.draw.polygon(surf, (40, 10, 10, 130), shadow_pts)
    # Body
    pygame.draw.polygon(surf, UI_RED, pts)
    # Top highlight stripe
    hi_pts = [
        (cx - bw + 1, banner_y - banner_h // 2),
        (cx + bw - 1, banner_y - banner_h // 2 + 1),
        (cx + bw - 1, banner_y - banner_h // 2 + 2),
        (cx - bw + 1, banner_y - banner_h // 2 + 1),
    ]
    pygame.draw.polygon(surf, (255, 110, 110, 200), hi_pts)
    # Outline
    pygame.draw.polygon(surf, UI_RED_DK, pts, 1)

    # Banner-end rivets — small gold dots at each banner tip
    pygame.draw.circle(surf, COIN_GOLD_HI, (cx - bw, banner_y), 2)
    pygame.draw.circle(surf, COIN_GOLD_DEEP, (cx - bw, banner_y), 2, 1)
    pygame.draw.circle(surf, COIN_GOLD_HI, (cx + bw, banner_y), 2)
    pygame.draw.circle(surf, COIN_GOLD_DEEP, (cx + bw, banner_y), 2, 1)

    # "X3" text
    _outlined_text(surf, "X3", 14, (cx, banner_y + 1),
                   fill=WHITE, outline=NEAR_BLACK, outline_w=1)


VARIANTS = {
    1: ("1 — coin stack",     draw_v1_stack),
    2: ("2 — trinity coins",  draw_v2_trinity),
    3: ("3 — jackpot star",   draw_v3_jackpot),
    4: ("4 — holographic 3X", draw_v4_foil_sticker),
    5: ("5 — banner coin",    draw_v5_banner),
}
