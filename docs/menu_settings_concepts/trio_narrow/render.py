"""Round-1 mockups: five narrower treatments of the Concept-3 bottom trio
(AWARDS / TOP 10 / SETTINGS) on the main menu.

These are review-only mockups — nothing here is wired into the live game.
The module is deliberately re-importable so revision rounds can tweak the
five ``trio_*`` routines without re-deriving the Concept-3 base every time.

The base is the real menu: we render everything above the trio exactly as
Concept 3 (title, subtitle, divider, Pip + post-house, night sky + mountains)
by monkeypatching ``draw_menu`` down to a background-only pass, then paint a
recentered + enlarged START pill and one of the five candidate trios on top.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import math
import pygame

from game.config import W, H
from game.scenes import App, STATE_MENU
from game.hud import (
    _pill_btn, _volume_panel, _draw_trophy, _draw_award_star, _font,
    _GOLD_PALE, _draw_overlay_stars, _draw_mountain_silhouette,
    _outlined_text, _ORANGE_BORDER, _GOLD_BRIGHT, _PANEL_LIGHTER, _PANEL_DARK,
)

# Trio baseline shared by every option so they sit in the same band.
TRIO_CY = H - 86          # 554
TILE_H = 48

_GOLD = (240, 192, 64)
_GOLD_HI = (255, 230, 150)
_RIM = (140, 90, 8)
_RIMD = (110, 72, 8)
_NAVY = (12, 8, 38)


# ── Gear glyph — sibling of _draw_trophy / _draw_award_star ──────────────────
# A struck-metal cog so SETTINGS reads in the same gold-on-navy family as the
# star and trophy. Supersampled then smoothscaled so the teeth + centre hole
# stay crisp at the ~18 px tile size.
def _draw_gear(surf, cx, cy, R, teeth=None):
    # At tile-icon scale (R ≤ 10) an 8-tooth cog with a wide navy centre hole
    # reads as a busy ring beside the solid star/trophy; a 6-tooth cog + a
    # tighter hole gives it the same disc-with-teeth weight, which is the key
    # cohesion fix. Larger renders keep the finer 8-tooth silhouette.
    if teeth is None:
        teeth = 6 if R <= 10 else 8
    hole = 0.24 if R <= 10 else 0.30
    SS = 4
    box = int(R * 2 + 6)
    B = box * SS
    c = B / 2
    g = pygame.Surface((B, B), pygame.SRCALPHA)
    Ro = R * SS              # tooth-tip radius
    Rb = R * SS * 0.74       # gear-body radius
    hw = math.radians(360.0 / teeth * 0.34)   # tooth half-angle at the base

    # Teeth first (trapezoids) so the body disc laps over their inner edge.
    for i in range(teeth):
        a = 2 * math.pi * i / teeth
        pts = [
            (c + Rb * math.cos(a - hw), c + Rb * math.sin(a - hw)),
            (c + Ro * math.cos(a - hw * 0.62), c + Ro * math.sin(a - hw * 0.62)),
            (c + Ro * math.cos(a + hw * 0.62), c + Ro * math.sin(a + hw * 0.62)),
            (c + Rb * math.cos(a + hw), c + Rb * math.sin(a + hw)),
        ]
        pygame.draw.polygon(g, _RIM, pts)                 # dark keyline
        inset = [(px - (px - c) * 0.10, py - (py - c) * 0.10) for px, py in pts]
        pygame.draw.polygon(g, _GOLD, inset)

    # Body disc + dark rim.
    pygame.draw.circle(g, _GOLD, (c, c), Rb)
    pygame.draw.circle(g, _RIM, (c, c), Rb, max(1, int(0.9 * SS)))
    # Upper-left sheen so the disc reads as raised metal.
    pygame.draw.circle(g, _GOLD_HI, (c - Rb * 0.24, c - Rb * 0.24),
                       Rb * 0.30)
    pygame.draw.circle(g, _GOLD, (c, c), Rb * 0.70)
    # Centre hole in the navy panel family.
    pygame.draw.circle(g, _NAVY, (c, c), R * SS * hole)
    pygame.draw.circle(g, _RIMD, (c, c), R * SS * hole, max(1, int(0.9 * SS)))

    small = pygame.transform.smoothscale(g, (box, box))
    surf.blit(small, (int(round(cx - box / 2)), int(round(cy - box / 2))))


def _soft_panel(surf, rect, radius=16, border_alpha=140):
    """Segmented-bar panel: same embossed body as ``_volume_panel`` but with a
    single thin, reduced-alpha gold rim. The full-width bar's continuous gold
    loop otherwise competes with the scarlet START pill; a quieter rim keeps
    the whole control clearly secondary to it."""
    sh = pygame.Surface((rect.width + 8, rect.height + 8), pygame.SRCALPHA)
    for k in range(4):
        a = 80 - k * 16
        pygame.draw.rect(sh, (0, 0, 0, a),
                         (k, k * 2, rect.width + 8 - k * 2,
                          rect.height + 8 - k * 2), border_radius=radius)
    surf.blit(sh, (rect.x - 4, rect.y + 2))

    pnl = pygame.Surface(rect.size, pygame.SRCALPHA)
    for yy in range(rect.height):
        t = yy / max(1, rect.height - 1)
        r = int(_PANEL_LIGHTER[0] * (1 - t) + _PANEL_DARK[0] * t)
        g = int(_PANEL_LIGHTER[1] * (1 - t) + _PANEL_DARK[1] * t)
        b = int(_PANEL_LIGHTER[2] * (1 - t) + _PANEL_DARK[2] * t)
        pygame.draw.line(pnl, (r, g, b, 235), (0, yy), (rect.width - 1, yy))
    mask = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255),
                     (0, 0, rect.width, rect.height), border_radius=radius)
    pnl.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    pygame.draw.rect(pnl, (*_GOLD_BRIGHT, border_alpha),
                     (0, 0, rect.width, rect.height), width=1, border_radius=radius)
    pygame.draw.line(pnl, (*_GOLD_PALE, 90), (10, 3), (rect.width - 10, 3), 1)
    surf.blit(pnl, rect.topleft)


def _tracked_label(surf, text, center, size, color=_GOLD_PALE, track=0,
                   alpha=230):
    """Render a label with optional per-letter tracking so tight tiles can
    pull the caption in without the wide ``A W A R D S`` spacing."""
    f = _font(size, True)
    if track == 0:
        img = f.render(text, True, color)
        img.set_alpha(alpha)
        surf.blit(img, img.get_rect(center=center))
        return
    glyphs = [f.render(ch, True, color) for ch in text]
    total = sum(gg.get_width() for gg in glyphs) + track * (len(glyphs) - 1)
    x = center[0] - total // 2
    for gg in glyphs:
        gg.set_alpha(alpha)
        surf.blit(gg, (x, center[1] - gg.get_height() // 2))
        x += gg.get_width() + track


# ── Icon dispatch so every routine draws the three glyphs at a shared size ───
def _glyph(surf, kind, cx, cy, r):
    if kind == "star":
        _draw_award_star(surf, cx, cy, r)
    elif kind == "trophy":
        _draw_trophy(surf, cx, cy, int(r * 0.9))
    else:
        _draw_gear(surf, cx, cy, r)


_TRIO = (("AWARDS", "star"), ("TOP 10", "trophy"), ("SETTINGS", "gear"))


# ── 1 · Inset equal tiles ────────────────────────────────────────────────────
# Three equal rounded tiles, generous outer margins, compact label over glyph —
# the matched-trio read of Concept 3 but pulled well clear of the screen edges.
def trio_inset_equal(surf, cy=TRIO_CY):
    margin, gap = 36, 10
    tile_w = (W - margin * 2 - gap * 2) // 3      # ≈ 89
    rects = []
    x = margin
    for label, kind in _TRIO:
        r = pygame.Rect(x, cy - TILE_H // 2, tile_w, TILE_H)
        _volume_panel(surf, r, radius=13)
        _tracked_label(surf, label, (r.centerx, cy - 13), 12, track=1)
        _glyph(surf, kind, r.centerx, cy + 10, 11)
        rects.append(r)
        x += tile_w + gap
    return rects


# ── 2 · Icon + short-caption chips ───────────────────────────────────────────
# Smaller chips clustered toward centre; the glyph carries the tile and the
# caption drops to a quiet footnote beneath it.
def trio_icon_chips(surf, cy=TRIO_CY):
    tile_w, gap, h = 84, 8, 54
    total = tile_w * 3 + gap * 2
    x = (W - total) // 2
    rects = []
    for label, kind in _TRIO:
        r = pygame.Rect(x, cy - h // 2, tile_w, h)
        _volume_panel(surf, r, radius=13)
        _glyph(surf, kind, r.centerx, cy - 5, 12)
        _tracked_label(surf, label, (r.centerx, cy + 15), 10,
                       color=_GOLD_HI, track=1, alpha=210)
        rects.append(r)
        x += tile_w + gap
    return rects


# ── 3 · Icon-only rounded tiles ──────────────────────────────────────────────
# No captions — just the three glyphs in small near-circular tiles, the tightest
# and most inset cluster of the set.
def trio_icon_only(surf, cy=TRIO_CY):
    tile, gap = 64, 10
    total = tile * 3 + gap * 2
    x = (W - total) // 2
    rects = []
    for _label, kind in _TRIO:
        r = pygame.Rect(x, cy - tile // 2, tile, tile)
        _volume_panel(surf, r, radius=tile // 2)
        # With no captions, star (AWARDS) and trophy (TOP 10) both read as
        # "achievement". A small "10" numeral under the cup pins the trophy
        # unmistakably to the leaderboard so the two glyphs can't be confused.
        if kind == "trophy":
            _draw_trophy(surf, r.centerx, r.centery - 6, int(13 * 0.9))
            _tracked_label(surf, "10", (r.centerx, r.centery + 15), 13,
                           color=_GOLD_HI, track=1)
        else:
            _glyph(surf, kind, r.centerx, r.centery, 13)
        rects.append(r)
        x += tile + gap
    return rects


# ── 4 · Segmented bar ────────────────────────────────────────────────────────
# One inset rounded panel split into three cells by thin gold dividers, each an
# icon over a tiny label — reads as a single unified control, clearly narrower.
def trio_segmented(surf, cy=TRIO_CY):
    # The AD asked for 256, but START's pill renders 240 px wide, so 256 would
    # invert the hierarchy the fix targets. 224 keeps the single-control read
    # while sitting a clear 8 px inside START's footprint on each side.
    bar_w, h = 224, 56
    x = (W - bar_w) // 2                     # → margin 68, inside START's 240
    bar = pygame.Rect(x, cy - h // 2, bar_w, h)
    _soft_panel(surf, bar, radius=16)
    cell_w = bar_w / 3
    rects = []
    for i, (label, kind) in enumerate(_TRIO):
        ccx = int(x + cell_w * (i + 0.5))
        if i > 0:
            dx = int(x + cell_w * i)
            pygame.draw.line(surf, (*_GOLD, 70),
                             (dx, cy - h // 2 + 10), (dx, cy + h // 2 - 10), 1)
            pygame.draw.line(surf, (*_NAVY, 140),
                             (dx + 1, cy - h // 2 + 10),
                             (dx + 1, cy + h // 2 - 10), 1)
        _glyph(surf, kind, ccx, cy - 7, 11)
        _tracked_label(surf, label, (ccx, cy + 16), 10, color=_GOLD_HI, track=0)
        rects.append(pygame.Rect(int(x + cell_w * i), bar.y, int(cell_w), h))
    return rects


# ── 5 · Stacked label-over-icon (portrait) ───────────────────────────────────
# Three narrow taller-than-wide cards, a small label capping a large glyph —
# a distinctly vertical silhouette that narrows the row by standing it up.
def trio_stacked(surf, cy=TRIO_CY):
    tile_w, gap, h = 86, 8, 70
    total = tile_w * 3 + gap * 2
    x = (W - total) // 2
    rects = []
    for label, kind in _TRIO:
        r = pygame.Rect(x, cy - h // 2, tile_w, h)
        _volume_panel(surf, r, radius=14)
        _tracked_label(surf, label, (r.centerx, r.y + 17), 11, track=1)
        _glyph(surf, kind, r.centerx, r.y + 48, 13)
        rects.append(r)
        x += tile_w + gap
    return rects


OPTIONS = [
    ("1 · INSET EQUAL TILES", "3 equal tiles, wide margins, label over glyph",
     trio_inset_equal),
    ("2 · ICON CHIPS", "Icon-forward chips, quiet caption, centre cluster",
     trio_icon_chips),
    ("3 · ICON-ONLY PILLS", "Bare glyphs in mini round tiles — most minimal",
     trio_icon_only),
    ("4 · SEGMENTED BAR", "One inset panel, three cells, single-control read",
     trio_segmented),
    ("5 · STACKED CARDS", "Portrait tiles: small label capping a big glyph",
     trio_stacked),
]


# ── Concept-3 base ───────────────────────────────────────────────────────────
def _menu_bg_only(hud, surf, dt, best):
    """Concept-3 menu minus the START pill + bottom trio: the exact night
    sky, mountains, floating title, subtitle and divider from ``draw_menu``,
    stopping short of the three pills + twin panels."""
    hud.title_t += dt
    dim = pygame.Surface((W, H), pygame.SRCALPHA)
    dim.fill((6, 1, 21, 110))
    surf.blit(dim, (0, 0))
    _draw_overlay_stars(surf, hud._stars, hud.title_t)
    _draw_mountain_silhouette(surf, alpha=180)
    pulse = 1.0 + math.sin(hud.title_t * 2.4) * 0.04
    float_y = int(7 * math.sin(hud.title_t * 1.8))
    _outlined_text(surf, "SKYBIT", (W // 2, 126 + float_y),
                   size=int(72 * pulse), px=3)
    _outlined_text(surf, "POCKET  SKY  FLYER", (W // 2, 184),
                   size=22, px=2, shadow_offset=(2, 3))
    pygame.draw.line(surf, (*_ORANGE_BORDER, 120),
                     (W // 2 - 70, 208), (W // 2 + 70, 208), 1)


def base_frame():
    """Render the Concept-3 base once and hand back a fresh copy."""
    app = App()
    app.state = STATE_MENU
    for _ in range(3):
        app.world.update(1 / 60)
    orig = type(app.hud).draw_menu
    type(app.hud).draw_menu = lambda self, s, dt, b: _menu_bg_only(self, s, dt, b)
    try:
        app._render()
        frame = app.screen.copy()
    finally:
        type(app.hud).draw_menu = orig
    return frame


def render_option(idx):
    """Full 360×640 menu frame for OPTIONS[idx]: base + enlarged START + trio."""
    frame = base_frame()
    # START recentered + enlarged (primary pill), matching Concept 3.
    _pill_btn(frame, (W // 2, 430), "START", size=24, alpha=255,
              min_width=240, primary=True, dim=True, shadow=False)
    OPTIONS[idx][2](frame)
    return frame


def compose():
    """Tile all five full frames into one labeled review board."""
    n = len(OPTIONS)
    pad, top, cap = 22, 92, 74
    cols = n
    board_w = pad + cols * (W + pad)
    board_h = top + H + cap + pad
    board = pygame.Surface((board_w, board_h))
    board.fill((22, 18, 34))
    # Header band.
    band = pygame.Surface((board_w, top), pygame.SRCALPHA)
    band.fill((15, 11, 26, 255))
    board.blit(band, (0, 0))
    tf = _font(30, True)
    t = tf.render("SKYBIT  —  CONCEPT-3 TRIO,  FIVE NARROWER TREATMENTS",
                  True, _GOLD)
    board.blit(t, t.get_rect(center=(board_w // 2, 34)))
    sf = _font(17, True)
    s = sf.render("Round 2 · same START + Pip above; only the AWARDS / TOP 10 / "
                  "SETTINGS row varies — all inset from the 360px edges",
                  True, (210, 200, 230))
    board.blit(s, s.get_rect(center=(board_w // 2, 64)))

    lf = _font(19, True)
    cf = _font(14, True)
    for i, (title, caption, _fn) in enumerate(OPTIONS):
        x = pad + i * (W + pad)
        frame = render_option(i)
        pygame.draw.rect(board, (60, 50, 84),
                         (x - 2, top - 2, W + 4, H + 4), border_radius=6)
        board.blit(frame, (x, top))
        lt = lf.render(title, True, _GOLD_HI)
        board.blit(lt, lt.get_rect(center=(x + W // 2, top + H + 18)))
        # Wrap the caption to the frame width.
        words = caption.split()
        lines, cur = [], ""
        for wd in words:
            test = (cur + " " + wd).strip()
            if cf.size(test)[0] > W - 10:
                lines.append(cur)
                cur = wd
            else:
                cur = test
        lines.append(cur)
        for j, ln in enumerate(lines):
            ct = cf.render(ln, True, (198, 190, 214))
            board.blit(ct, ct.get_rect(
                center=(x + W // 2, top + H + 40 + j * 17)))
    return board


if __name__ == "__main__":
    pygame.init()
    pygame.display.set_mode((W, H))
    out = os.path.join(os.path.dirname(__file__), "round_2.png")
    board = compose()
    pygame.image.save(board, out)
    print("wrote", out, board.get_size())
