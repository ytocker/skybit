"""Round-2 exploration sheet for the tabbed V5 / V4-LEGENDS leaderboard.

Round 1 verdict was ITERATE toward the segmented-control chassis with a
coin-state era cue. Round 2 ships ONE fused lead plus three genuinely
distinct executions of the SAME goals (instant tab affordance, a
colorblind-safe coin/era cue read by value+shape, a difficulty subline,
a FINAL/frozen signal that never overlaps data, and aged-NAVY — not sepia
— legends). Each candidate is rendered in BOTH eras where useful so the
two states can be judged side by side.

Pipeline mirrors ``HUD._render_leaderboard``: build each full-screen
360x640 portrait at 3x supersample, smoothscale to native, then composite
into one labelled review grid at ``docs/leaderboard/round_2.png``. Real
palette + draw helpers are imported from ``game.hud`` so the explorations
read as the actual game. No new raster assets are produced; only the
review PNG (kept out of the shipped bundle by the CI staging step).
"""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

pygame.init()
pygame.display.set_mode((1, 1))  # font/surface init for the dummy driver

from game.config import W, H
from game.draw import WHITE, NEAR_BLACK, UI_CREAM
from game.hud import (
    _GOLD_BRIGHT, _GOLD_DEEP, _GOLD_PALE, _GOLD_MUTED,
    _PANEL_DARK, _PANEL_LIGHTER,
    _SCARLET_TOP, _SCARLET_BOT,
    _MEDAL_GRADIENTS,
    _medal_row_pill, _draw_trophy, _get_crown_sprite_hd,
    _outlined_text, _font,
)

S = 3                     # in-game supersample factor for the leaderboard
Ws, Hs = W * S, H * S

# ── Sample data ──────────────────────────────────────────────────────────────
# Low live-v5 scores (the hard era) vs much higher v4-legend scores so the two
# tabs read as genuinely different difficulties; distinct playful name pools,
# all <= 10 chars.
V5_SCORES = [
    {"name": "Pip", "score": 58},
    {"name": "SkyDuck", "score": 47},
    {"name": "Nova", "score": 41},
    {"name": "BeakBoss", "score": 33},
    {"name": "Zippy", "score": 28},
    {"name": "Mango", "score": 22},
    {"name": "Wisp", "score": 17},
    {"name": "Coco", "score": 13},
    {"name": "Fizz", "score": 9},
    {"name": "Tato", "score": 7},
]
V4_SCORES = [
    {"name": "OG_FLAP", "score": 410},
    {"name": "GrandPaw", "score": 366},
    {"name": "DodoKing", "score": 318},
    {"name": "AceWings", "score": 275},
    {"name": "RubyBeak", "score": 240},
    {"name": "OldGuard", "score": 205},
    {"name": "Comet", "score": 178},
    {"name": "Vinyl", "score": 152},
    {"name": "Bramble", "score": 134},
    {"name": "Marble", "score": 120},
]

# ── Aged-NAVY legends palette ────────────────────────────────────────────────
# Critique: legends must stay obviously the SAME navy screen, just frozen — a
# desaturated cool-bronze navy, NOT a sepia full-reskin. Backgrounds keep the
# night-sky blue; only the chrome cools toward patina-bronze.
AGED_BG_TOP = (14, 13, 34)        # cool desaturated navy (vs live 10,6,30)
AGED_BG_BOT = (5, 5, 18)
AGED_PANEL_TOP = (24, 24, 50)     # navy panel, slightly cooler + greyer
AGED_PANEL_BOT = (11, 11, 30)
PATINA_BRIGHT = (150, 176, 150)   # verdigris-bronze accent (cool, not warm sepia)
PATINA_DEEP = (70, 92, 80)
PATINA_PALE = (198, 214, 190)     # frosty pale-bronze for legend text
# Coin glyphs.
LIVE_COIN_TOP = _GOLD_PALE        # bright live gold
LIVE_COIN_BOT = _GOLD_DEEP
TARNISH_TOP = (150, 138, 96)      # tarnished/patinated bronze coin
TARNISH_BOT = (78, 70, 44)
# Wax seal.
WAX_RED = (150, 28, 26)
WAX_RED_HI = (196, 60, 52)
# Frost band.
FROST_TOP = (188, 210, 230)
FROST_BOT = (120, 150, 180)


def _lerp(a, b, t):
    return tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(3))


# ── Shared background ────────────────────────────────────────────────────────
def _night_bg(aged=False):
    """Vertical night-sky gradient + a deterministic star field. Legends keep
    the night-blue DNA (only cooled/desaturated), never sepia."""
    bg = pygame.Surface((Ws, Hs))
    top = AGED_BG_TOP if aged else (10, 6, 30)
    bot = AGED_BG_BOT if aged else (4, 2, 16)
    for yy in range(Hs):
        t = yy / (Hs - 1)
        pygame.draw.line(bg, _lerp(top, bot, t), (0, yy), (Ws, yy))
    # Stars — fixed hashed positions for repeatability. Legends dim them a
    # touch toward cool grey so the era reads "frozen" without going warm.
    star_col = (188, 202, 210) if aged else (255, 255, 255)
    for k in range(70):
        x = (k * 73 + 31) % Ws
        y = (k * 149 + 17) % (Hs * 3 // 5)
        r = (1 + (k % 3)) * S
        a = (30 + (k * 37) % 110) if aged else (40 + (k * 37) % 150)
        st = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(st, (*star_col, a), (r + 1, r + 1), r // 2 + 1)
        bg.blit(st, (x, y))
    return bg


def _base(aged=False):
    """Background + the standard dark overlay tint used by the live board.
    Legends use a cool navy tint, not a warm one — keep the same screen."""
    surf = pygame.Surface((Ws, Hs), pygame.SRCALPHA)
    surf.blit(_night_bg(aged), (0, 0))
    dim = pygame.Surface((Ws, Hs), pygame.SRCALPHA)
    dim.fill((6, 8, 26, 165) if aged else (0, 0, 20, 175))
    surf.blit(dim, (0, 0))
    return surf


# ── Generic rounded-gradient chrome helper ───────────────────────────────────
def _grad_round(surf, rect, top_c, bot_c, radius, alpha=255, border=None,
                border_w=2):
    x, y, w, h = rect
    pnl = pygame.Surface((w, h), pygame.SRCALPHA)
    for yy in range(h):
        u = yy / max(1, h - 1)
        pygame.draw.line(pnl, (*_lerp(top_c, bot_c, u), alpha),
                         (0, yy), (w, yy))
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, w, h),
                     border_radius=radius)
    pnl.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    if border:
        pygame.draw.rect(pnl, border, (0, 0, w, h), width=border_w,
                         border_radius=radius)
    surf.blit(pnl, (x, y))


def _subtitle(surf, txt, cy, col, size=11):
    f = _font(size * S, True)
    img = f.render(txt, True, col)
    r = img.get_rect(center=(Ws // 2, cy))
    sh = f.render(txt, True, NEAR_BLACK)
    sh.set_alpha(150)
    surf.blit(sh, (r.x + 1 * S, r.y + 1 * S))
    surf.blit(img, r)


# ── Coin medallion glyph (colorblind-safe era cue: value + shape) ────────────
def _coin_glyph(r, top_c, bot_c, live):
    """Small medallion read by VALUE + SHAPE before text: a bright domed
    live-gold coin (smooth, glinting, star pip) vs a flatter tarnished bronze
    coin (notched/worn rim, no glint) — so the era reads even in greyscale."""
    size = r * 2 + 4 * S
    cc = size // 2
    disc = pygame.Surface((size, size), pygame.SRCALPHA)
    # Dome shading.
    for yy in range(-r, r + 1):
        half = int(math.sqrt(max(0, r * r - yy * yy)))
        if half <= 0:
            continue
        u = (yy + r) / max(1, 2 * r)
        pygame.draw.line(disc, (*_lerp(top_c, bot_c, u), 255),
                         (cc - half, cc + yy), (cc + half, cc + yy))
    pygame.draw.circle(disc, NEAR_BLACK, (cc, cc), r, max(1, 1 * S))
    inner = max(1 * S, r - 3 * S)
    if live:
        # Bright inner ring + specular glint + star pip — reads "live, shiny".
        pygame.draw.circle(disc, (*_GOLD_PALE, 220), (cc, cc), inner, 1 * S)
        glint = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(glint, (255, 255, 255, 150),
                           (cc - r // 3, cc - r // 3), max(1, r // 4))
        disc.blit(glint, (0, 0))
        # Tiny 4-point star pip at centre.
        for ang in range(0, 360, 90):
            ex = cc + int((r // 2) * math.cos(math.radians(ang)))
            ey = cc + int((r // 2) * math.sin(math.radians(ang)))
            pygame.draw.line(disc, (255, 250, 230), (cc, cc), (ex, ey),
                             max(1, S // 2))
    else:
        # Worn notched rim + dull center — reads "old, tarnished" in grey too.
        pygame.draw.circle(disc, (*PATINA_DEEP, 200), (cc, cc), inner, 1 * S)
        for k in range(8):
            ang = k / 8 * math.tau
            nx = cc + int((r - 1 * S) * math.cos(ang))
            ny = cc + int((r - 1 * S) * math.sin(ang))
            pygame.draw.circle(disc, (*bot_c, 220), (nx, ny), max(1, S // 2))
    return disc


# ── Theme-parameterised row helper ───────────────────────────────────────────
def _draw_rows(surf, scores, card_x, card_y, card_w, row_h, theme):
    """Shared row renderer. Top-3 always use the FULL medal gradient pill
    (critique: never flatten); plain rows re-skin per era. The #1 crown is
    seated ABOVE the pill so it cannot clip the pill's top rim."""
    row_gap = 4 * S
    SILVER = (185, 195, 205)
    BRONZE = (185, 125, 55)
    f_badge = _font(13 * S, True)
    f_name = _font(16 * S, True)
    f_score = _font(17 * S, True)
    hd_crown = _get_crown_sprite_hd(S)

    ry = card_y
    for i, entry in enumerate(scores):
        rank = i + 1
        row_cy = ry + row_h // 2
        is_medal = rank in _MEDAL_GRADIENTS
        row_radius = row_h // 2

        if is_medal:
            pnl = _medal_row_pill(card_w, row_h, row_radius, rank)
            name_col = NEAR_BLACK
            score_col = NEAR_BLACK
        else:
            pnl = pygame.Surface((card_w, row_h), pygame.SRCALPHA)
            top_c = theme["plain_top"]
            bot_c = theme["plain_bot"]
            for yy in range(row_h):
                u = yy / max(1, row_h - 1)
                pygame.draw.line(pnl, (*_lerp(top_c, bot_c, u), 230),
                                 (0, yy), (card_w, yy))
            mask = pygame.Surface((card_w, row_h), pygame.SRCALPHA)
            pygame.draw.rect(mask, (255, 255, 255, 255),
                             (0, 0, card_w, row_h), border_radius=row_radius)
            pnl.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            bcol, balpha = theme["border"]
            pygame.draw.rect(pnl, (*bcol, balpha), (0, 0, card_w, row_h),
                             width=1 * S, border_radius=row_radius)
            name_col = theme["name_col"]
            score_col = theme["score_col"]
        surf.blit(pnl, (card_x, ry))

        # Rank badge.
        badge_cx = card_x + 24 * S
        badge_r = 13 * S
        if rank == 1:
            bcol = _GOLD_BRIGHT
        elif rank == 2:
            bcol = SILVER
        elif rank == 3:
            bcol = BRONZE
        else:
            bcol = theme["badge_col"]
        if rank <= 3:
            pygame.draw.circle(surf, bcol, (badge_cx, row_cy), badge_r)
            pygame.draw.circle(surf, NEAR_BLACK, (badge_cx, row_cy),
                               badge_r, 1 * S)
            num_col = NEAR_BLACK
        else:
            pygame.draw.circle(surf, bcol, (badge_cx, row_cy), badge_r, 2 * S)
            num_col = theme["badge_num"]
        num_img = f_badge.render(str(rank), True, num_col)
        surf.blit(num_img, num_img.get_rect(center=(badge_cx, row_cy)))

        # #1 crown seated ABOVE the pill rim — a clear gap so it never clips.
        if rank == 1:
            c_w, c_h = hd_crown.get_size()
            surf.blit(hd_crown, (badge_cx - c_w // 2, ry - c_h - 1 * S))

        nm = entry["name"][:10]
        nm_img = f_name.render(nm, True, name_col)
        surf.blit(nm_img, (card_x + 44 * S, row_cy - nm_img.get_height() // 2))

        sc_img = f_score.render(str(entry["score"]), True, score_col)
        surf.blit(sc_img,
                  (card_x + card_w - 16 * S - sc_img.get_width(),
                   row_cy - sc_img.get_height() // 2))

        ry += row_h + row_gap
    return ry


# Live (v5) plain-row theme — deep navy panels, gold accents.
LIVE_THEME = {
    "plain_top": _PANEL_LIGHTER,
    "plain_bot": _PANEL_DARK,
    "border": (_GOLD_BRIGHT, 110),
    "name_col": WHITE,
    "score_col": _GOLD_BRIGHT,
    "badge_col": _GOLD_BRIGHT,
    "badge_num": _GOLD_BRIGHT,
}
# Frozen (v4) AGED-NAVY theme — same navy panels cooled toward patina bronze.
AGED_THEME = {
    "plain_top": AGED_PANEL_TOP,
    "plain_bot": AGED_PANEL_BOT,
    "border": (PATINA_BRIGHT, 130),
    "name_col": PATINA_PALE,
    "score_col": PATINA_BRIGHT,
    "badge_col": PATINA_BRIGHT,
    "badge_num": PATINA_PALE,
}


def _tap(surf, col):
    f = _font(14 * S, True)
    img = f.render("TAP  TO  MENU", True, col)
    img.set_alpha(210)
    surf.blit(img, img.get_rect(center=(Ws // 2, Hs - 24 * S)))


# ── Segmented control: pill track + two halves, each carrying a coin glyph ───
def _segmented_control(surf, seg_x, seg_y, seg_w, seg_h, v5_active, aged):
    """Round-1 #1 chassis fused with #5 coin-state. One pill track, two equal
    halves; each half carries its era coin (live gold / tarnished bronze) so
    the era reads by value+shape before text. Selected = filled gold gradient
    + dark text + faint inner glow; deselected = hollow navy + gold hairline +
    ~70% gold text (tappable, never greyed-disabled)."""
    half = seg_w // 2
    radius = seg_h // 2
    # Track body — navy, cooled when legends are active.
    track_top = (20, 18, 46) if aged else (16, 11, 44)
    track_bot = (9, 9, 26) if aged else (8, 5, 26)
    trim = (*PATINA_BRIGHT, 140) if aged else (*_GOLD_BRIGHT, 130)
    _grad_round(surf, (seg_x, seg_y, seg_w, seg_h), track_top, track_bot,
                radius=radius, alpha=240, border=trim, border_w=1 * S)

    coin_r = (seg_h - 14 * S) // 2
    f = _font(13 * S, True)

    def _half(hx, label, selected, live):
        cx = hx + half // 2
        cy = seg_y + seg_h // 2
        if selected:
            top_c = LIVE_COIN_TOP if live else (180, 196, 178)
            bot_c = LIVE_COIN_BOT if live else PATINA_DEEP
            _grad_round(surf, (hx + 2 * S, seg_y + 2 * S, half - 4 * S,
                               seg_h - 4 * S),
                        top_c, bot_c, radius=(seg_h - 4 * S) // 2, alpha=255,
                        border=(*NEAR_BLACK, 200), border_w=1 * S)
            # Faint inner top glow on the filled tab.
            glow = pygame.Surface((half - 4 * S, seg_h - 4 * S),
                                  pygame.SRCALPHA)
            pygame.draw.line(glow, (255, 255, 255, 90),
                             (8 * S, 3 * S), (half - 12 * S, 3 * S), 2 * S)
            surf.blit(glow, (hx + 2 * S, seg_y + 2 * S))
            txt_col = NEAR_BLACK
        else:
            txt_col = ((*PATINA_PALE,) if aged else _GOLD_MUTED)
        # Coin glyph to the left of the label.
        ctop, cbot = (LIVE_COIN_TOP, LIVE_COIN_BOT) if live else \
            (TARNISH_TOP, TARNISH_BOT)
        glyph = _coin_glyph(coin_r, ctop, cbot, live)
        gw = glyph.get_width()
        lbl = f.render(label, True, txt_col)
        group_w = gw + 4 * S + lbl.get_width()
        gx = cx - group_w // 2
        surf.blit(glyph, (gx, cy - glyph.get_height() // 2))
        surf.blit(lbl, (gx + gw + 4 * S, cy - lbl.get_height() // 2))

    _half(seg_x, "V5", v5_active, live=True)
    _half(seg_x + half, "LEGENDS", not v5_active, live=False)


# ── Candidate 1 — Fused Lead: segmented control + coin state ─────────────────
def render_fused(v5_active):
    aged = not v5_active
    surf = _base(aged=aged)
    title_fill = PATINA_PALE if aged else _GOLD_BRIGHT
    if aged:
        _outlined_text(surf, "TOP 10", (Ws // 2, 34 * S), size=24 * S,
                       fill=title_fill, outline=PATINA_DEEP, px=2 * S,
                       shadow_offset=(2 * S, 3 * S))
    else:
        _outlined_text(surf, "TOP 10", (Ws // 2, 34 * S), size=24 * S,
                       px=2 * S, shadow_offset=(2 * S, 3 * S))

    seg_y, seg_h = 58 * S, 28 * S
    seg_x, seg_w = 18 * S, (W - 36) * S
    _segmented_control(surf, seg_x, seg_y, seg_w, seg_h, v5_active, aged)

    if v5_active:
        _subtitle(surf, "LIVE  ·  CURRENT SEASON", 100 * S, _GOLD_PALE)
        _draw_rows(surf, V5_SCORES, 14 * S, 114 * S, (W - 28) * S, 35 * S,
                   LIVE_THEME)
        _tap(surf, _GOLD_MUTED)
    else:
        _subtitle(surf, "v4 ERA  ·  EASIER", 100 * S, PATINA_BRIGHT)
        bottom = _draw_rows(surf, V4_SCORES, 14 * S, 114 * S, (W - 28) * S,
                            35 * S, AGED_THEME)
        # FINAL wax seal in the dead-zone BELOW row 10 / ABOVE "TAP TO MENU".
        _wax_seal(surf, Ws // 2, (bottom + Hs - 24 * S) // 2, 26 * S)
        _tap(surf, PATINA_BRIGHT)
    return surf


def _wax_seal(surf, cx, cy, r):
    """Small rotated wax 'FINAL' seal — anchored where no name/score sits."""
    pad = r + 6 * S
    stamp = pygame.Surface((pad * 2, pad * 2), pygame.SRCALPHA)
    sc = pad
    # Drip-edged wax blob: jittered outer ring for a melted look.
    pts = []
    for k in range(20):
        ang = k / 20 * math.tau
        rr = r + (3 * S if k % 2 == 0 else 0)
        pts.append((sc + rr * math.cos(ang), sc + rr * math.sin(ang)))
    pygame.draw.polygon(stamp, (*WAX_RED, 230), pts)
    pygame.draw.circle(stamp, (*WAX_RED_HI, 220), (sc, sc), r - 2 * S, 2 * S)
    pygame.draw.circle(stamp, (*WAX_RED_HI, 150), (sc, sc), r - 7 * S, 1 * S)
    sf = _font(14 * S, True)
    si = sf.render("FINAL", True, (245, 222, 212))
    stamp.blit(si, si.get_rect(center=(sc, sc)))
    stamp = pygame.transform.rotate(stamp, -12)
    surf.blit(stamp, stamp.get_rect(center=(cx, cy)))


# ── Candidate 2 — Big Coins ON the track as the active indicator ─────────────
def render_big_coins(v5_active):
    """Variant: the coin medallions are LARGER and sit ON the segment track as
    the active indicator — the selected era's coin pops forward (bright, raised
    with a halo), the deselected era's coin sits flat/dim. Same affordance,
    different emphasis on the coin as the control's 'thumb'."""
    aged = not v5_active
    surf = _base(aged=aged)
    if aged:
        _outlined_text(surf, "TOP 10", (Ws // 2, 34 * S), size=24 * S,
                       fill=PATINA_PALE, outline=PATINA_DEEP, px=2 * S,
                       shadow_offset=(2 * S, 3 * S))
    else:
        _outlined_text(surf, "TOP 10", (Ws // 2, 34 * S), size=24 * S,
                       px=2 * S, shadow_offset=(2 * S, 3 * S))

    seg_y, seg_h = 56 * S, 34 * S
    seg_x, seg_w = 22 * S, (W - 44) * S
    half = seg_w // 2
    radius = seg_h // 2
    track_top = (20, 18, 46) if aged else (16, 11, 44)
    track_bot = (9, 9, 26) if aged else (8, 5, 26)
    trim = (*PATINA_BRIGHT, 140) if aged else (*_GOLD_BRIGHT, 130)
    _grad_round(surf, (seg_x, seg_y, seg_w, seg_h), track_top, track_bot,
                radius=radius, alpha=240, border=trim, border_w=1 * S)
    # Selected-half fill behind the big coin so the tab still reads as a tab.
    f = _font(13 * S, True)

    def _half(hx, label, selected, live):
        cx = hx + half // 2
        cy = seg_y + seg_h // 2
        if selected:
            top_c = LIVE_COIN_TOP if live else (180, 196, 178)
            bot_c = LIVE_COIN_BOT if live else PATINA_DEEP
            _grad_round(surf, (hx + 2 * S, seg_y + 2 * S, half - 4 * S,
                               seg_h - 4 * S),
                        top_c, bot_c, radius=(seg_h - 4 * S) // 2, alpha=255,
                        border=(*NEAR_BLACK, 200), border_w=1 * S)
            txt_col = NEAR_BLACK
        else:
            txt_col = PATINA_PALE if aged else _GOLD_MUTED
        # Big coin raised on the track. Selected coin gets a halo + sits high.
        big_r = (seg_h // 2) + 6 * S if selected else (seg_h // 2) - 2 * S
        coin_cy = cy - (3 * S if selected else 0)
        coin_cx = cx - 26 * S
        if selected and live:
            halo = pygame.Surface((big_r * 4, big_r * 4), pygame.SRCALPHA)
            for rr in range(big_r + 8 * S, big_r, -2 * S):
                a = int(70 * (big_r + 8 * S - rr) / (8 * S))
                pygame.draw.circle(halo, (*_GOLD_BRIGHT, a),
                                   (big_r * 2, big_r * 2), rr)
            surf.blit(halo, (coin_cx - big_r * 2, coin_cy - big_r * 2))
        ctop, cbot = (LIVE_COIN_TOP, LIVE_COIN_BOT) if live else \
            (TARNISH_TOP, TARNISH_BOT)
        glyph = _coin_glyph(big_r, ctop, cbot, live)
        if not selected:
            glyph.set_alpha(170)
        surf.blit(glyph, glyph.get_rect(center=(coin_cx, coin_cy)))
        lbl = f.render(label, True, txt_col)
        surf.blit(lbl, lbl.get_rect(midleft=(coin_cx + big_r + 4 * S, cy)))

    _half(seg_x, "V5", v5_active, live=True)
    _half(seg_x + half, "LGND", not v5_active, live=False)

    if v5_active:
        _subtitle(surf, "LIVE  ·  CURRENT SEASON", 102 * S, _GOLD_PALE)
        _draw_rows(surf, V5_SCORES, 14 * S, 116 * S, (W - 28) * S, 35 * S,
                   LIVE_THEME)
        _tap(surf, _GOLD_MUTED)
    else:
        _subtitle(surf, "v4 ERA  ·  EASIER", 102 * S, PATINA_BRIGHT)
        bottom = _draw_rows(surf, V4_SCORES, 14 * S, 116 * S, (W - 28) * S,
                            35 * S, AGED_THEME)
        _wax_seal(surf, Ws // 2, (bottom + Hs - 24 * S) // 2, 26 * S)
        _tap(surf, PATINA_BRIGHT)
    return surf


# ── Candidate 3 — Inkbar: underline-style tabs + corner seal ─────────────────
def render_inkbar(v5_active):
    """Variant: an underline/inkbar segmented control — both labels share one
    flat bar, the active tab is marked by a thick gold (or patina) underline +
    its coin glyph. The FINAL signal moves to a small CORNER seal in the header
    dead-zone rather than below the rows."""
    aged = not v5_active
    surf = _base(aged=aged)
    if aged:
        _outlined_text(surf, "TOP 10", (Ws // 2, 32 * S), size=22 * S,
                       fill=PATINA_PALE, outline=PATINA_DEEP, px=2 * S,
                       shadow_offset=(2 * S, 3 * S))
    else:
        _outlined_text(surf, "TOP 10", (Ws // 2, 32 * S), size=22 * S,
                       px=2 * S, shadow_offset=(2 * S, 3 * S))

    bar_y = 56 * S
    bar_h = 30 * S
    bar_x = 24 * S
    bar_w = (W - 48) * S
    half = bar_w // 2
    # Thin shared baseline under both labels.
    base_col = (*PATINA_DEEP, 160) if aged else (*_GOLD_DEEP, 160)
    pygame.draw.line(surf, base_col, (bar_x, bar_y + bar_h),
                     (bar_x + bar_w, bar_y + bar_h), 1 * S)
    f = _font(14 * S, True)
    coin_r = 8 * S

    def _tab(hx, label, selected, live):
        cx = hx + half // 2
        cy = bar_y + bar_h // 2
        ctop, cbot = (LIVE_COIN_TOP, LIVE_COIN_BOT) if live else \
            (TARNISH_TOP, TARNISH_BOT)
        glyph = _coin_glyph(coin_r, ctop, cbot, live)
        gw = glyph.get_width()
        if selected:
            txt_col = PATINA_PALE if aged else _GOLD_BRIGHT
        else:
            txt_col = (140, 158, 140) if aged else _GOLD_MUTED
        lbl = f.render(label, True, txt_col)
        group_w = gw + 4 * S + lbl.get_width()
        gx = cx - group_w // 2
        surf.blit(glyph, (gx, cy - glyph.get_height() // 2))
        surf.blit(lbl, (gx + gw + 4 * S, cy - lbl.get_height() // 2))
        if selected:
            ink = PATINA_BRIGHT if aged else _GOLD_BRIGHT
            uw = group_w + 10 * S
            pygame.draw.line(surf, ink,
                             (cx - uw // 2, bar_y + bar_h),
                             (cx + uw // 2, bar_y + bar_h), 4 * S)

    _tab(bar_x, "V5", v5_active, live=True)
    _tab(bar_x + half, "LEGENDS", not v5_active, live=False)

    # Corner FINAL seal in the header dead-zone (only on the frozen board).
    if aged:
        _wax_seal(surf, Ws - 40 * S, 36 * S, 20 * S)
        _subtitle(surf, "v4 ERA  ·  EASIER", 102 * S, PATINA_BRIGHT)
        _draw_rows(surf, V4_SCORES, 14 * S, 116 * S, (W - 28) * S, 35 * S,
                   AGED_THEME)
        _tap(surf, PATINA_BRIGHT)
    else:
        _subtitle(surf, "LIVE  ·  CURRENT SEASON", 102 * S, _GOLD_PALE)
        _draw_rows(surf, V5_SCORES, 14 * S, 116 * S, (W - 28) * S, 35 * S,
                   LIVE_THEME)
        _tap(surf, _GOLD_MUTED)
    return surf


# ── Candidate 4 — Frost Band: frozen treatment as a header band, not wax ─────
def render_frost_band(v5_active):
    """Variant: same segmented-control chassis, but the FROZEN treatment is a
    laurel/frost header BAND across the top of the legends board (an icy ribbon
    reading 'FROZEN · v4 ERA') instead of a wax seal — keeping aged-navy. The
    live board shows the same chassis cleanly with no band."""
    aged = not v5_active
    surf = _base(aged=aged)
    if aged:
        _outlined_text(surf, "TOP 10", (Ws // 2, 34 * S), size=22 * S,
                       fill=PATINA_PALE, outline=PATINA_DEEP, px=2 * S,
                       shadow_offset=(2 * S, 3 * S))
    else:
        _outlined_text(surf, "TOP 10", (Ws // 2, 34 * S), size=22 * S,
                       px=2 * S, shadow_offset=(2 * S, 3 * S))

    seg_y, seg_h = 58 * S, 28 * S
    seg_x, seg_w = 18 * S, (W - 36) * S
    _segmented_control(surf, seg_x, seg_y, seg_w, seg_h, v5_active, aged)

    if aged:
        # Frost band: an icy ribbon + laurel pair flanking a FROZEN tag.
        band_y = 96 * S
        band_h = 22 * S
        _grad_round(surf, (40 * S, band_y, (W - 80) * S, band_h),
                    FROST_TOP, FROST_BOT, radius=band_h // 2, alpha=230,
                    border=(*PATINA_PALE, 200), border_w=1 * S)
        _frost_laurel(surf, 52 * S, band_y + band_h // 2, -1)
        _frost_laurel(surf, Ws - 52 * S, band_y + band_h // 2, 1)
        bf = _font(11 * S, True)
        bi = bf.render("FROZEN  ·  v4 ERA  ·  EASIER", True, (24, 40, 60))
        surf.blit(bi, bi.get_rect(center=(Ws // 2, band_y + band_h // 2)))
        _draw_rows(surf, V4_SCORES, 14 * S, 128 * S, (W - 28) * S, 33 * S,
                   AGED_THEME)
        _tap(surf, PATINA_BRIGHT)
    else:
        _subtitle(surf, "LIVE  ·  CURRENT SEASON", 102 * S, _GOLD_PALE)
        _draw_rows(surf, V5_SCORES, 14 * S, 116 * S, (W - 28) * S, 35 * S,
                   LIVE_THEME)
        _tap(surf, _GOLD_MUTED)
    return surf


def _frost_laurel(surf, cx, cy, side):
    """A small frosty laurel sprig — a fan of pale leaves curling inward, so
    the frozen band reads ceremonial without going sepia."""
    for k in range(4):
        leaf = pygame.Surface((9 * S, 5 * S), pygame.SRCALPHA)
        pygame.draw.ellipse(leaf, (*FROST_TOP, 235), (0, 0, 9 * S, 5 * S))
        pygame.draw.ellipse(leaf, (*PATINA_PALE, 180), (0, 0, 9 * S, 5 * S),
                            1 * S)
        leaf = pygame.transform.rotate(leaf, side * (40 - k * 22))
        px = cx + side * (k * 3 * S)
        py = cy - 8 * S + k * 5 * S
        surf.blit(leaf, leaf.get_rect(center=(px, py)))


# ── Compose the review grid (each candidate shown in BOTH eras) ──────────────
def main():
    # Each candidate is a (label, [state tiles]) pair so the sheet shows both
    # eras for every execution. The fused lead leads; three distinct tab-bar
    # executions follow.
    candidates = [
        ("1 - Fused Lead (segmented + coin)",
         [("V5 LIVE", lambda: render_fused(True)),
          ("V4 LEGENDS", lambda: render_fused(False))]),
        ("2 - Big Coins on Track",
         [("V5 LIVE", lambda: render_big_coins(True)),
          ("V4 LEGENDS", lambda: render_big_coins(False))]),
        ("3 - Inkbar + Corner Seal",
         [("V5 LIVE", lambda: render_inkbar(True)),
          ("V4 LEGENDS", lambda: render_inkbar(False))]),
        ("4 - Frost Band Header",
         [("V5 LIVE", lambda: render_frost_band(True)),
          ("V4 LEGENDS", lambda: render_frost_band(False))]),
    ]

    pad = 16
    cap_h = 26
    state_cap_h = 20
    tile_w, tile_h = W, H
    # Two state-columns per candidate, candidates laid out in a 2x2 block.
    cell_w = 2 * tile_w + pad        # one candidate occupies two side tiles
    cols = 2                          # two candidates per row
    rows = 2
    title_h = 44

    block_w = cell_w + state_cap_h * 0  # state caps live above tiles
    grid_w = pad + cols * (cell_w + pad)
    cell_h = state_cap_h + tile_h + cap_h
    grid_h = title_h + pad + rows * (cell_h + pad)

    grid = pygame.Surface((grid_w, grid_h))
    grid.fill((18, 14, 26))

    lab_font = pygame.font.Font(None, 24)
    state_font = pygame.font.Font(None, 20)
    title_font = pygame.font.Font(None, 30)
    title = title_font.render(
        "Skybit - Tabbed Leaderboard (V5 / V4 LEGENDS) - Round 2",
        True, (245, 220, 150))
    grid.blit(title, (pad, 14))

    for idx, (label, states) in enumerate(candidates):
        col = idx % cols
        row = idx // cols
        cx0 = pad + col * (cell_w + pad)
        cy0 = title_h + pad + row * (cell_h + pad)
        # Two state tiles side by side.
        for si, (state_label, fn) in enumerate(states):
            hd = fn()
            tile = pygame.transform.smoothscale(hd, (tile_w, tile_h))
            tx = cx0 + si * (tile_w + pad)
            ty = cy0 + state_cap_h
            pygame.draw.rect(grid, (40, 32, 50),
                             (tx - 2, ty - 2, tile_w + 4, tile_h + 4),
                             border_radius=6)
            grid.blit(tile, (tx, ty))
            scap = state_font.render(state_label, True, (200, 210, 235))
            grid.blit(scap, (tx + 4, cy0))
        cap = lab_font.render(label, True, (235, 235, 245))
        grid.blit(cap, (cx0 + 4, cy0 + state_cap_h + tile_h + 4))

    out_dir = os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), "docs", "leaderboard")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_2.png")
    pygame.image.save(grid, out_path)
    print("wrote", out_path, grid.get_size())


if __name__ == "__main__":
    main()
