"""Round-1 exploration sheet for the tabbed V5 / V4-LEGENDS leaderboard.

Five distinct full-screen 360x640 portrait candidates rendered headless at
3x supersample (mirroring the in-game leaderboard pipeline in
``HUD._render_leaderboard``), then smoothscaled to native and composited into
one labelled 5-up review grid at ``docs/leaderboard/round_1.png``.

Why headless + real helpers: the explorations must read as the actual game,
so we import the canonical palette + draw helpers from ``game.hud`` rather
than re-deriving the look. No new raster assets are produced; only the review
PNG (kept out of the shipped bundle by the CI staging step).
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
# tabs read as genuinely different difficulties; distinct playful name pools.
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

# ── Aged-bronze / sepia palette for the legends era ──────────────────────────
SEPIA_BG_TOP = (38, 26, 16)
SEPIA_BG_BOT = (18, 12, 7)
BRONZE_BRIGHT = (196, 142, 74)
BRONZE_DEEP = (96, 62, 28)
BRONZE_PALE = (224, 192, 140)
STONE_TOP = (74, 58, 40)
STONE_BOT = (44, 33, 22)
WAX_RED = (150, 28, 26)
WAX_RED_HI = (196, 60, 52)


# ── Shared background ────────────────────────────────────────────────────────
def _night_bg(sepia=False):
    """Vertical night-sky (or sepia) gradient + a deterministic star field, so
    every candidate sits on the same canvas the real overlay dims onto."""
    bg = pygame.Surface((Ws, Hs))
    top = SEPIA_BG_TOP if sepia else (10, 6, 30)
    bot = SEPIA_BG_BOT if sepia else (4, 2, 16)
    for yy in range(Hs):
        t = yy / (Hs - 1)
        c = tuple(int(top[i] * (1 - t) + bot[i] * t) for i in range(3))
        pygame.draw.line(bg, c, (0, yy), (Ws, yy))
    # Stars — fixed pseudo-random pattern (hashed positions) for repeatability.
    star_col = (200, 168, 120) if sepia else (255, 255, 255)
    for k in range(70):
        x = (k * 73 + 31) % Ws
        y = (k * 149 + 17) % (Hs * 3 // 5)
        r = (1 + (k % 3)) * S
        a = 40 + (k * 37) % 150
        st = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(st, (*star_col, a), (r + 1, r + 1), r // 2 + 1)
        bg.blit(st, (x, y))
    return bg


def _base(sepia=False):
    """Background + the standard dark overlay tint used by the live board."""
    surf = pygame.Surface((Ws, Hs), pygame.SRCALPHA)
    surf.blit(_night_bg(sepia), (0, 0))
    dim = pygame.Surface((Ws, Hs), pygame.SRCALPHA)
    dim.fill((26, 12, 0, 150) if sepia else (0, 0, 20, 175))
    surf.blit(dim, (0, 0))
    return surf


def _lerp(a, b, t):
    return tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(3))


# ── Theme-parameterised row helper ───────────────────────────────────────────
def _draw_rows(surf, scores, card_x, card_y, card_w, row_h, theme,
               crowned=True):
    """One shared row renderer driven by a ``theme`` dict so every candidate's
    rows share structure (badge + crown on #1, name, score) but can re-skin
    medals / plain rows / engraving for the live vs frozen eras.

    theme keys:
      medals      -> use gold/silver/bronze gradient pills for top 3
      plain_top   -> top colour of a plain-row gradient
      plain_bot   -> bottom colour of a plain-row gradient
      border      -> (rgb, alpha) row border
      name_col    -> name text colour on plain rows
      score_col   -> score text colour on plain rows
      badge_col   -> ring colour for ranks 4-10
      badge_num   -> numeral colour for ranks 4-10
      engrave     -> draw a pale top + dark bottom inner bevel (stone look)
    """
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
        is_medal = theme.get("medals") and rank in _MEDAL_GRADIENTS
        row_radius = row_h // 2

        pnl = pygame.Surface((card_w, row_h), pygame.SRCALPHA)
        if is_medal:
            pnl = _medal_row_pill(card_w, row_h, row_radius, rank)
            name_col = NEAR_BLACK
            score_col = NEAR_BLACK
        else:
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
            if theme.get("engrave"):
                # Engraved-stone bevel: pale top edge, dark bottom edge.
                pygame.draw.line(pnl, (*BRONZE_PALE, 90),
                                 (row_radius, 2 * S),
                                 (card_w - row_radius, 2 * S), 1 * S)
                pygame.draw.line(pnl, (0, 0, 0, 120),
                                 (row_radius, row_h - 3 * S),
                                 (card_w - row_radius, row_h - 3 * S), 1 * S)
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

        if rank == 1 and crowned:
            c_w, c_h = hd_crown.get_size()
            surf.blit(hd_crown, (badge_cx - c_w // 2, row_cy - 7 * S - c_h))

        # Name.
        nm = entry["name"][:10]
        nm_img = f_name.render(nm, True, NEAR_BLACK if is_medal else name_col)
        surf.blit(nm_img, (card_x + 44 * S,
                           row_cy - nm_img.get_height() // 2))

        # Score (right-aligned).
        sc_img = f_score.render(str(entry["score"]), True,
                                NEAR_BLACK if is_medal else score_col)
        surf.blit(sc_img,
                  (card_x + card_w - 16 * S - sc_img.get_width(),
                   row_cy - sc_img.get_height() // 2))

        ry += row_h + row_gap
    return ry


# Live (v5) plain-row theme — deep navy panels, gold accents.
LIVE_THEME = {
    "medals": True,
    "plain_top": _PANEL_LIGHTER,
    "plain_bot": _PANEL_DARK,
    "border": (_GOLD_BRIGHT, 110),
    "name_col": WHITE,
    "score_col": _GOLD_BRIGHT,
    "badge_col": _GOLD_BRIGHT,
    "badge_num": _GOLD_BRIGHT,
}
# Frozen (v4) engraved-stone theme — warm sepia, bronze accents.
FROZEN_THEME = {
    "medals": True,
    "plain_top": STONE_TOP,
    "plain_bot": STONE_BOT,
    "border": (BRONZE_BRIGHT, 150),
    "name_col": BRONZE_PALE,
    "score_col": BRONZE_BRIGHT,
    "badge_col": BRONZE_BRIGHT,
    "badge_num": BRONZE_PALE,
    "engrave": True,
}


# ── Small shared chrome bits ─────────────────────────────────────────────────
def _grad_round(surf, rect, top_c, bot_c, radius, alpha=255, border=None,
                border_w=2):
    pnl = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
    for yy in range(rect[3]):
        u = yy / max(1, rect[3] - 1)
        pygame.draw.line(pnl, (*_lerp(top_c, bot_c, u), alpha),
                         (0, yy), (rect[2], yy))
    mask = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255),
                     (0, 0, rect[2], rect[3]), border_radius=radius)
    pnl.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    if border:
        pygame.draw.rect(pnl, border, (0, 0, rect[2], rect[3]),
                         width=border_w, border_radius=radius)
    surf.blit(pnl, (rect[0], rect[1]))


def _subtitle(surf, txt, cy, col):
    f = _font(11 * S, True)
    img = f.render(txt, True, col)
    r = img.get_rect(center=(Ws // 2, cy))
    sh = f.render(txt, True, NEAR_BLACK)
    sh.set_alpha(150)
    surf.blit(sh, (r.x + 1 * S, r.y + 1 * S))
    surf.blit(img, r)


def _laurel(surf, cx, cy, scale, col):
    """A simple symmetric laurel pair around a centre — drawn as a fan of
    tapering leaf ellipses on each side."""
    for side in (-1, 1):
        for k in range(6):
            ang = math.radians(35 + k * 22)
            lx = cx + side * (14 * S + k * 6 * S) * math.cos(0)
            r = (18 + k * 8) * scale
            leaf = pygame.Surface((10 * S, 5 * S), pygame.SRCALPHA)
            pygame.draw.ellipse(leaf, (*col, 230), (0, 0, 10 * S, 5 * S))
            leaf = pygame.transform.rotate(leaf, side * (90 - 30 - k * 9))
            px = cx + side * int((16 + k * 8.5) * S)
            py = cy - int(28 * S) + k * 9 * S
            surf.blit(leaf, leaf.get_rect(center=(px, py)))


# ── Candidate 1: Segmented Twins (V5 active) ─────────────────────────────────
def render_segmented_twins():
    surf = _base()
    _outlined_text(surf, "TOP 10", (Ws // 2, 36 * S), size=26 * S,
                   px=2 * S, shadow_offset=(2 * S, 3 * S))

    # Segmented control: V5 | V4 LEGENDS.
    seg_y = 62 * S
    seg_h = 26 * S
    seg_x = 18 * S
    seg_w = (W - 36) * S
    half = seg_w // 2
    # Track.
    _grad_round(surf, (seg_x, seg_y, seg_w, seg_h), (16, 11, 44), (8, 5, 26),
                radius=seg_h // 2, alpha=235,
                border=(*_GOLD_BRIGHT, 120), border_w=1 * S)
    # Selected (V5) — filled gold.
    _grad_round(surf, (seg_x + 2 * S, seg_y + 2 * S, half - 3 * S,
                       seg_h - 4 * S),
                _GOLD_PALE, _GOLD_DEEP, radius=(seg_h - 4 * S) // 2, alpha=255,
                border=(*NEAR_BLACK, 200), border_w=1 * S)
    f = _font(14 * S, True)
    a = f.render("V5", True, NEAR_BLACK)
    surf.blit(a, a.get_rect(center=(seg_x + half // 2, seg_y + seg_h // 2)))
    # Unselected (V4 LEGENDS) — hollow navy.
    b = f.render("V4 LEGENDS", True, _GOLD_MUTED)
    surf.blit(b, b.get_rect(center=(seg_x + half + half // 2,
                                    seg_y + seg_h // 2)))

    _subtitle(surf, "LIVE  ·  CURRENT SEASON", 100 * S, _GOLD_PALE)

    _draw_rows(surf, V5_SCORES, 14 * S, 116 * S, (W - 28) * S, 36 * S,
               LIVE_THEME)
    _tap(surf, _GOLD_MUTED)
    return surf


# ── Candidate 2: Era Monument (V4 LEGENDS active) ────────────────────────────
def render_era_monument():
    surf = _base(sepia=True)
    # Laurel + engraved title.
    _laurel(surf, Ws // 2, 44 * S, 1.0, BRONZE_BRIGHT)
    _outlined_text(surf, "HALL OF FAME", (Ws // 2, 40 * S), size=22 * S,
                   fill=BRONZE_PALE, outline=BRONZE_DEEP,
                   px=2 * S, shadow_offset=(2 * S, 3 * S))

    # Segmented control, legends side selected, bronze theme.
    seg_y = 66 * S
    seg_h = 24 * S
    seg_x = 18 * S
    seg_w = (W - 36) * S
    half = seg_w // 2
    _grad_round(surf, (seg_x, seg_y, seg_w, seg_h), (54, 38, 22), (30, 20, 11),
                radius=seg_h // 2, alpha=235,
                border=(*BRONZE_BRIGHT, 150), border_w=1 * S)
    f = _font(13 * S, True)
    a = f.render("V5", True, (150, 120, 86))
    surf.blit(a, a.get_rect(center=(seg_x + half // 2, seg_y + seg_h // 2)))
    _grad_round(surf, (seg_x + half + 2 * S, seg_y + 2 * S, half - 4 * S,
                       seg_h - 4 * S),
                BRONZE_PALE, BRONZE_DEEP, radius=(seg_h - 4 * S) // 2,
                alpha=255, border=(*NEAR_BLACK, 200), border_w=1 * S)
    b = f.render("V4 LEGENDS", True, NEAR_BLACK)
    surf.blit(b, b.get_rect(center=(seg_x + half + half // 2,
                                    seg_y + seg_h // 2)))

    _subtitle(surf, "HALL OF FAME  ·  v4 ERA (EASIER)", 100 * S, BRONZE_PALE)

    _draw_rows(surf, V4_SCORES, 14 * S, 116 * S, (W - 28) * S, 36 * S,
               FROZEN_THEME)

    # Rotated wax "FINAL" stamp over the lower-right rows.
    stamp = pygame.Surface((92 * S, 56 * S), pygame.SRCALPHA)
    pygame.draw.circle(stamp, (*WAX_RED, 220), (46 * S, 28 * S), 26 * S)
    pygame.draw.circle(stamp, (*WAX_RED_HI, 210), (46 * S, 28 * S),
                       26 * S, 2 * S)
    pygame.draw.circle(stamp, (*WAX_RED_HI, 180), (46 * S, 28 * S),
                       20 * S, 1 * S)
    sf = _font(15 * S, True)
    si = sf.render("FINAL", True, (245, 220, 210))
    stamp.blit(si, si.get_rect(center=(46 * S, 28 * S)))
    stamp = pygame.transform.rotate(stamp, 14)
    surf.blit(stamp, stamp.get_rect(center=(Ws - 70 * S, Hs - 120 * S)))

    _tap(surf, BRONZE_BRIGHT)
    return surf


# ── Candidate 3: Banner Ribbon (V5 active) ───────────────────────────────────
def render_banner_ribbon():
    surf = _base()
    _outlined_text(surf, "TOP 10", (Ws // 2, 34 * S), size=24 * S,
                   px=2 * S, shadow_offset=(2 * S, 3 * S))

    band_y = 58 * S
    band_h = 34 * S
    # Dog-eared back tab (V4 LEGENDS) tucked to the right, behind the ribbon.
    back_x = Ws - 134 * S
    back_pts = [
        (back_x, band_y + 4 * S),
        (Ws - 16 * S, band_y + 4 * S),
        (Ws - 16 * S, band_y + band_h),
        (back_x - 10 * S, band_y + band_h),
    ]
    pygame.draw.polygon(surf, (30, 20, 11), back_pts)
    pygame.draw.polygon(surf, BRONZE_BRIGHT, back_pts, 1 * S)
    # Dog-ear fold highlight.
    pygame.draw.polygon(surf, (62, 44, 26),
                        [(Ws - 30 * S, band_y + 4 * S),
                         (Ws - 16 * S, band_y + 4 * S),
                         (Ws - 16 * S, band_y + 16 * S)])
    bf = _font(11 * S, True)
    bi = bf.render("V4 LEGENDS", True, BRONZE_PALE)
    surf.blit(bi, bi.get_rect(center=((back_x + Ws - 16 * S) // 2,
                                      band_y + band_h - 11 * S)))

    # Forward gold ribbon banner (V5) — notched ends, sits proud in front.
    rb_x = 14 * S
    rb_w = 200 * S
    rb_pts = [
        (rb_x, band_y),
        (rb_x + rb_w, band_y),
        (rb_x + rb_w + 14 * S, band_y + band_h // 2),
        (rb_x + rb_w, band_y + band_h),
        (rb_x, band_y + band_h),
        (rb_x + 14 * S, band_y + band_h // 2),
    ]
    # Shadow.
    sh = [(x + 2 * S, y + 4 * S) for x, y in rb_pts]
    pygame.draw.polygon(surf, (0, 0, 0, 120), sh)
    # Gold gradient fill via clipped strips.
    rb_surf = pygame.Surface((rb_w + 16 * S, band_h), pygame.SRCALPHA)
    for yy in range(band_h):
        u = yy / max(1, band_h - 1)
        pygame.draw.line(rb_surf, (*_lerp(_GOLD_PALE, _GOLD_DEEP, u), 255),
                         (0, yy), (rb_w + 16 * S, yy))
    mask = pygame.Surface((rb_w + 16 * S, band_h), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255),
                        [(p[0] - rb_x, p[1] - band_y) for p in rb_pts])
    rb_surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(rb_surf, (rb_x, band_y))
    pygame.draw.polygon(surf, NEAR_BLACK, rb_pts, 2 * S)
    # Fold-under wings at each notch for a real ribbon feel.
    for fx, fdir in ((rb_x, 1), (rb_x + rb_w + 14 * S, -1)):
        pygame.draw.polygon(surf, BRONZE_DEEP,
                            [(fx, band_y + band_h),
                             (fx, band_y + band_h + 8 * S),
                             (fx + fdir * 12 * S, band_y + band_h)])
    rf = _font(15 * S, True)
    ri = rf.render("V5", True, NEAR_BLACK)
    surf.blit(ri, ri.get_rect(center=(rb_x + 24 * S + rb_w // 2 - 60 * S,
                                      band_y + band_h // 2)))
    ri2 = _font(11 * S, True).render("CURRENT", True, (60, 40, 8))
    surf.blit(ri2, ri2.get_rect(midleft=(rb_x + 70 * S,
                                         band_y + band_h // 2)))

    _subtitle(surf, "LIVE  ·  CURRENT SEASON", 110 * S, _GOLD_PALE)

    _draw_rows(surf, V5_SCORES, 14 * S, 126 * S, (W - 28) * S, 35 * S,
               LIVE_THEME)
    _tap(surf, _GOLD_MUTED)
    return surf


# ── Candidate 4: Side Shoulder Tabs (V5 active) ──────────────────────────────
def render_side_shoulder():
    surf = _base()
    # Main panel inset from the left to leave room for vertical shoulder tabs.
    panel_x = 40 * S
    panel_w = (W - 40 - 12) * S
    panel_y = 70 * S
    panel_h = (H - 70 - 40) * S
    _grad_round(surf, (panel_x, panel_y, panel_w, panel_h),
                _PANEL_LIGHTER, _PANEL_DARK, radius=14 * S, alpha=230,
                border=(*_GOLD_BRIGHT, 130), border_w=1 * S)

    _outlined_text(surf, "TOP 10", (panel_x + panel_w // 2, 38 * S),
                   size=22 * S, px=2 * S, shadow_offset=(2 * S, 3 * S))

    # Vertical rotated shoulder tabs on the left edge.
    def vtab(cy, label, active, aged=False):
        tw, th = 96 * S, 30 * S
        tab = pygame.Surface((tw, th), pygame.SRCALPHA)
        if active:
            top_c, bot_c = _GOLD_PALE, _GOLD_DEEP
            txt_c = NEAR_BLACK
            border = (*NEAR_BLACK, 200)
        elif aged:
            top_c, bot_c = STONE_TOP, STONE_BOT
            txt_c = BRONZE_PALE
            border = (*BRONZE_BRIGHT, 150)
        else:
            top_c, bot_c = (20, 13, 52), (10, 6, 30)
            txt_c = _GOLD_MUTED
            border = (*_GOLD_BRIGHT, 110)
        for xx in range(tw):
            u = xx / max(1, tw - 1)
            pygame.draw.line(tab, (*_lerp(top_c, bot_c, u), 245),
                             (xx, 0), (xx, th))
        mask = pygame.Surface((tw, th), pygame.SRCALPHA)
        # Round only the outer (left) corners after rotation — keep it simple
        # with a full round; active tab bleeds into the panel edge.
        pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, tw, th),
                         border_radius=10 * S)
        tab.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        pygame.draw.rect(tab, border, (0, 0, tw, th), width=1 * S,
                         border_radius=10 * S)
        tf = _font(13 * S, True)
        ti = tf.render(label, True, txt_c)
        tab.blit(ti, ti.get_rect(center=(tw // 2, th // 2)))
        if aged and not active:
            # Cracks / weathering: a couple of dark hairlines.
            for cx0 in (28 * S, 64 * S):
                pygame.draw.line(tab, (0, 0, 0, 90),
                                 (cx0, 4 * S), (cx0 + 5 * S, th - 4 * S), 1 * S)
        rot = pygame.transform.rotate(tab, 90)
        rx = panel_x - rot.get_width() + 6 * S  # bleed into panel edge
        surf.blit(rot, (rx, cy - rot.get_height() // 2))

    vtab(panel_y + 78 * S, "V5", True)
    vtab(panel_y + 180 * S, "V4 LEGENDS", False, aged=True)

    _subtitle(surf, "LIVE · CURRENT SEASON",
              panel_y - 8 * S + 0, _GOLD_PALE)

    # Full-width rows inside the panel.
    _draw_rows(surf, V5_SCORES, panel_x + 8 * S, panel_y + 18 * S,
               panel_w - 16 * S, 35 * S, LIVE_THEME)
    _tap(surf, _GOLD_MUTED)
    return surf


# ── Candidate 5: Split Coin Toggle (V4 LEGENDS active) ───────────────────────
def _coin_medallion(surf, cx, cy, r, top_c, bot_c, label, big, crowned):
    """A round medallion toggle: live gold or tarnished bronze, with a beaded
    rim, embossed label, and an optional crown when it is the active board."""
    disc = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
    cc = r + 2
    for yy in range(r * 2):
        u = yy / max(1, r * 2 - 1)
        col = _lerp(top_c, bot_c, u)
        half = int(math.sqrt(max(0, r * r - (yy - r) ** 2)))
        pygame.draw.line(disc, (*col, 255), (cc - half, yy + 2), (cc + half,
                                                                   yy + 2))
    pygame.draw.circle(disc, NEAR_BLACK, (cc, cc), r, 2 * S)
    # Beaded rim.
    for k in range(24):
        ang = k / 24 * math.tau
        bx = cc + int((r - 3 * S) * math.cos(ang))
        by = cc + int((r - 3 * S) * math.sin(ang))
        pygame.draw.circle(disc, (*bot_c, 200), (bx, by), 1 * S)
    lf = _font((13 if big else 11) * S, True)
    li = lf.render(label, True, NEAR_BLACK)
    disc.blit(li, li.get_rect(center=(cc, cc)))
    surf.blit(disc, (cx - cc, cy - cc))
    if crowned:
        cr = _get_crown_sprite_hd(S)
        surf.blit(cr, (cx - cr.get_width() // 2, cy - r - cr.get_height() + 4 * S))


def render_split_coin():
    surf = _base(sepia=True)
    _outlined_text(surf, "HALL OF FAME", (Ws // 2, 36 * S), size=20 * S,
                   fill=BRONZE_PALE, outline=BRONZE_DEEP,
                   px=2 * S, shadow_offset=(2 * S, 3 * S))

    # Two medallion toggles. Live = gold coin (small, dimmed), legend =
    # tarnished bronze (enlarged + crowned, the active board).
    cy = 84 * S
    _coin_medallion(surf, Ws // 2 - 66 * S, cy + 4 * S, 22 * S,
                    (150, 120, 60), (96, 74, 30), "V5", big=False,
                    crowned=False)
    _coin_medallion(surf, Ws // 2 + 58 * S, cy, 30 * S,
                    BRONZE_PALE, BRONZE_DEEP, "V4", big=True, crowned=True)
    # "vs" between them.
    _text_small = _font(12 * S, True)
    vs = _text_small.render("vs", True, BRONZE_PALE)
    surf.blit(vs, vs.get_rect(center=(Ws // 2 - 4 * S, cy + 2 * S)))

    _subtitle(surf, "HALL OF FAME · v4 ERA (EASIER)", 126 * S, BRONZE_PALE)

    _draw_rows(surf, V4_SCORES, 14 * S, 142 * S, (W - 28) * S, 35 * S,
               FROZEN_THEME)
    _tap(surf, BRONZE_BRIGHT)
    return surf


def _tap(surf, col):
    f = _font(14 * S, True)
    img = f.render("TAP  TO  MENU", True, col)
    img.set_alpha(210)
    surf.blit(img, img.get_rect(center=(Ws // 2, Hs - 26 * S)))


# ── Compose the 5-up review grid ─────────────────────────────────────────────
def main():
    candidates = [
        ("1 · Segmented Twins", render_segmented_twins),
        ("2 · Era Monument", render_era_monument),
        ("3 · Banner Ribbon", render_banner_ribbon),
        ("4 · Side Shoulder Tabs", render_side_shoulder),
        ("5 · Split Coin Toggle", render_split_coin),
    ]

    tiles = []
    for label, fn in candidates:
        hd = fn()
        scaled = pygame.transform.smoothscale(hd, (W, H))
        tiles.append((label, scaled))

    # Grid: 5 tiles in one row, each W x H, with a caption strip + padding.
    pad = 16
    cap_h = 30
    tile_w, tile_h = W, H + cap_h
    cols = 5
    grid_w = pad + cols * (tile_w + pad)
    grid_h = pad + tile_h + pad + 40  # +40 for the sheet title

    grid = pygame.Surface((grid_w, grid_h))
    grid.fill((18, 14, 26))

    lab_font = pygame.font.Font(None, 22)
    title_font = pygame.font.Font(None, 30)
    title = title_font.render(
        "Skybit · Tabbed Leaderboard (V5 / V4 LEGENDS) · Round 1",
        True, (245, 220, 150))
    grid.blit(title, (pad, 12))

    y0 = 48
    for i, (label, tile) in enumerate(tiles):
        x = pad + i * (tile_w + pad)
        pygame.draw.rect(grid, (40, 32, 50),
                         (x - 2, y0 - 2, tile_w + 4, tile_h + 4),
                         border_radius=6)
        grid.blit(tile, (x, y0))
        cap = lab_font.render(label, True, (235, 235, 245))
        grid.blit(cap, (x + 6, y0 + H + 6))

    out_dir = os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), "docs", "leaderboard")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_1.png")
    pygame.image.save(grid, out_path)
    print("wrote", out_path, grid.get_size())


if __name__ == "__main__":
    main()
