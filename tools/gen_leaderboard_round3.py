"""Round-3 final-polish sheet for the tabbed V5 / V4-LEGENDS leaderboard.

Round-2 locked candidate #1 "Fused Lead" as the winner. Round 3 ships the
final build of that lead (candidate 1) plus four polished, viable
alternatives — five options for the user to choose from. Every candidate
carries the SAME round-2 critique fixes:

  * Deselected tab reads "tappable", never "disabled": gold label raised to
    ~83% brightness + a 1px brighter top hairline on the hollow segment.
  * Era coins in BOTH segments, colorblind-safe by value + shape: V5 = bright
    domed live-gold coin, V4 = flat tarnished BRONZE coin (aged bronze, not
    grey). The V5 coin stays BRIGHT even on the frozen board so users know the
    live board is there to return to.
  * Legends = aged NAVY (cool-bronze patina tint on chrome), NOT sepia — keeps
    the night-blue DNA.
  * Frozen double-signal: a worded ONE-LINE frost-tinted ribbon
    (``FROZEN · v4 ERA · EASIER``) that does NOT eat row height, plus a
    drip-edged wax FINAL seal in the dead-zone below row 10 / above TAP TO MENU.
  * NO feathery procedural frost flourishes — frost is expressed as a flat
    tint + 2-3 HARD crystal ticks only.
  * Crown seated ABOVE the rank-1 pill (no clip); full medal-pill gradient
    richness on the top 3.

Two PNGs are produced:
  * ``docs/leaderboard/round_3.png`` — labelled comparison grid of all 5
    candidates, each shown as a V5-LIVE + V4-LEGENDS pair.
  * ``docs/leaderboard/round_3_lead_360.png`` — the LEAD candidate (1) at
    TRUE 360px width (tile not upscaled beyond native), both states side by
    side, so deselected-tab contrast and bronze-vs-grey coin read can be
    judged at honest gameplay scale.

Pipeline mirrors ``HUD._render_leaderboard``: each full screen is built at
3x supersample then smoothscaled to native 360x640. Real palette + draw
helpers are imported from ``game.hud`` so explorations read as the actual
game. No new raster assets ship; only the review PNGs (kept out of the
bundle by the CI staging step).
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
# Legends must stay the SAME night-navy screen, just frozen — a desaturated
# cool-bronze navy, NOT sepia. Backgrounds keep night-sky blue; only the chrome
# cools toward patina-bronze.
AGED_BG_TOP = (14, 13, 34)        # cool desaturated navy (vs live 10,6,30)
AGED_BG_BOT = (5, 5, 18)
AGED_PANEL_TOP = (24, 24, 50)     # navy panel, slightly cooler + greyer
AGED_PANEL_BOT = (11, 11, 30)
PATINA_BRIGHT = (150, 176, 150)   # verdigris-bronze accent (cool, not warm sepia)
PATINA_DEEP = (70, 92, 80)
PATINA_PALE = (198, 214, 190)     # frosty pale-bronze for legend text

# ── Coin glyphs ──────────────────────────────────────────────────────────────
# V5 live gold — bright, warm.
LIVE_COIN_TOP = _GOLD_PALE
LIVE_COIN_BOT = _GOLD_DEEP
# V4 tarnished BRONZE — warmed deliberately so it reads as AGED BRONZE, not a
# grey "disabled" disc. A real copper/bronze hue (more red than green) keeps it
# legible as "old money" even next to the cool patina chrome.
BRONZE_COIN_TOP = (198, 138, 84)   # warm coppery bronze highlight
BRONZE_COIN_BOT = (120, 70, 34)    # deep aged-bronze shadow

# Wax seal.
WAX_RED = (150, 28, 26)
WAX_RED_HI = (196, 60, 52)

# Frost ribbon — icy navy-blue tint (cool, never warm sepia).
FROST_TOP = (176, 204, 226)
FROST_BOT = (108, 142, 176)
FROST_INK = (22, 38, 60)           # dark navy ink for ribbon text
CRYSTAL = (224, 240, 252)          # hard ice-tick highlight


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
    # Stars — fixed hashed positions for repeatability. Legends cool them a
    # touch so the era reads "frozen" without going warm.
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
    """Small medallion read by VALUE + SHAPE before colour: a bright domed
    live-gold coin (smooth, glinting, star pip) vs a flatter AGED-BRONZE coin
    (worn notched rim, dull centre, no glint) — so the era reads even in
    greyscale. The bronze stays a warm copper hue so it never reads as a grey
    'disabled' disc."""
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
        for ang in range(0, 360, 90):
            ex = cc + int((r // 2) * math.cos(math.radians(ang)))
            ey = cc + int((r // 2) * math.sin(math.radians(ang)))
            pygame.draw.line(disc, (255, 250, 230), (cc, cc), (ex, ey),
                             max(1, S // 2))
    else:
        # Worn notched rim + dull warm-bronze centre — reads "old, tarnished"
        # in grey too, but the warm copper hue keeps it from looking disabled.
        pygame.draw.circle(disc, (*_lerp(bot_c, (40, 22, 10), 0.3), 210),
                           (cc, cc), inner, 1 * S)
        for k in range(8):
            ang = k / 8 * math.tau
            nx = cc + int((r - 1 * S) * math.cos(ang))
            ny = cc + int((r - 1 * S) * math.sin(ang))
            pygame.draw.circle(disc, (*bot_c, 230), (nx, ny), max(1, S // 2))
    return disc


# ── Theme-parameterised row helper ───────────────────────────────────────────
def _draw_rows(surf, scores, card_x, card_y, card_w, row_h, theme):
    """Shared row renderer. Top-3 always use the FULL medal gradient pill
    (never flatten); plain rows re-skin per era. The #1 crown is seated ABOVE
    the pill so it cannot clip the pill's top rim. Returns the y just below
    the last row (for placing seals in the dead-zone)."""
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


# ── Frozen ribbon (worded, ONE LINE TALL) ────────────────────────────────────
def _frozen_ribbon(surf, cx, cy, w, h, text=" FROZEN  ·  v4 ERA  ·  EASIER "):
    """A flat frost-TINTED ribbon, one line tall — the explicit worded frozen
    signal that does NOT eat row height. Frost is a flat icy gradient + 2-3
    HARD crystal ticks only (no feathery procedural flourishes). Returns rect."""
    x = cx - w // 2
    y = cy - h // 2
    _grad_round(surf, (x, y, w, h), FROST_TOP, FROST_BOT, radius=h // 2,
                alpha=235, border=(*PATINA_PALE, 210), border_w=1 * S)
    # Inner top sheen so the ribbon reads frosted, not flat plastic.
    sheen = pygame.Surface((w - 6 * S, h - 4 * S), pygame.SRCALPHA)
    pygame.draw.line(sheen, (255, 255, 255, 70),
                     (6 * S, 2 * S), (w - 12 * S, 2 * S), 2 * S)
    surf.blit(sheen, (x + 3 * S, y + 2 * S))
    # 2-3 HARD crystal ticks (tiny 4-point asterisks), placed at the ends and
    # one near a third — deliberately geometric, never feathery.
    for tx in (x + 12 * S, x + w - 12 * S, cx):
        _crystal_tick(surf, tx, cy, 4 * S)
    f = _font(11 * S, True)
    ti = f.render(text.strip(), True, FROST_INK)
    surf.blit(ti, ti.get_rect(center=(cx, cy)))
    return pygame.Rect(x, y, w, h)


def _crystal_tick(surf, cx, cy, r):
    """A single hard ice crystal: a 4-point asterisk with a bright core. Flat,
    geometric — the only frost flourish allowed (no feathery laurels)."""
    for ang in (0, 45, 90, 135):
        dx = int(r * math.cos(math.radians(ang)))
        dy = int(r * math.sin(math.radians(ang)))
        pygame.draw.line(surf, CRYSTAL, (cx - dx, cy - dy),
                         (cx + dx, cy + dy), max(1, S // 2))
    pygame.draw.circle(surf, (255, 255, 255), (cx, cy), max(1, S // 2 + 1))


# ── Wax FINAL seal ───────────────────────────────────────────────────────────
def _wax_seal(surf, cx, cy, r):
    """Small rotated wax 'FINAL' seal — anchored where no name/score sits, so
    the frozen board double-signals (worded ribbon + ceremonial seal)."""
    pad = r + 8 * S
    stamp = pygame.Surface((pad * 2, pad * 2), pygame.SRCALPHA)
    sc = pad
    # Drip-edged wax blob: jittered outer ring for a melted look.
    pts = []
    for k in range(20):
        ang = k / 20 * math.tau
        rr = r + (3 * S if k % 2 == 0 else 0)
        pts.append((sc + rr * math.cos(ang), sc + rr * math.sin(ang)))
    pygame.draw.polygon(stamp, (*WAX_RED, 235), pts)
    pygame.draw.circle(stamp, (*WAX_RED_HI, 220), (sc, sc), r - 2 * S, 2 * S)
    pygame.draw.circle(stamp, (*WAX_RED_HI, 150), (sc, sc), r - 7 * S, 1 * S)
    sf = _font(13 * S, True)
    si = sf.render("FINAL", True, (245, 222, 212))
    stamp.blit(si, si.get_rect(center=(sc, sc)))
    stamp = pygame.transform.rotate(stamp, -12)
    surf.blit(stamp, stamp.get_rect(center=(cx, cy)))


# ── Title ────────────────────────────────────────────────────────────────────
def _title(surf, cy, aged, size=24 * S):
    if aged:
        _outlined_text(surf, "TOP 10", (Ws // 2, cy), size=size,
                       fill=PATINA_PALE, outline=PATINA_DEEP, px=2 * S,
                       shadow_offset=(2 * S, 3 * S))
    else:
        _outlined_text(surf, "TOP 10", (Ws // 2, cy), size=size,
                       px=2 * S, shadow_offset=(2 * S, 3 * S))


# ── Segmented control: pill track + two halves, each carrying a coin glyph ───
def _segmented_control(surf, seg_x, seg_y, seg_w, seg_h, v5_active, aged,
                       coin_inside=False, lgnd_label="LEGENDS"):
    """The locked round-1 #1 chassis fused with the #5 coin-state. One pill
    track, two equal halves; each half carries its era coin (live gold /
    tarnished bronze) so the era reads by value + shape before text.

    Selected   = filled gold gradient capsule + dark text + inner top glow.
    Deselected = hollow navy + gold hairline + a 1px BRIGHTER top hairline +
                 gold label at ~83% brightness — so it reads tappable, not
                 disabled.

    The V5 coin stays BRIGHT live-gold even on the frozen board so users know
    the live board is there to return to. ``coin_inside`` left-anchors a
    larger coin at the segment's leading edge (candidate 3) instead of beside
    the centred label."""
    half = seg_w // 2
    radius = seg_h // 2
    # Track body — navy, cooled when legends are active.
    track_top = (20, 18, 46) if aged else (16, 11, 44)
    track_bot = (9, 9, 26) if aged else (8, 5, 26)
    trim = (*PATINA_BRIGHT, 140) if aged else (*_GOLD_BRIGHT, 130)
    _grad_round(surf, (seg_x, seg_y, seg_w, seg_h), track_top, track_bot,
                radius=radius, alpha=240, border=trim, border_w=1 * S)

    coin_r = (seg_h - 14 * S) // 2
    big_coin_r = (seg_h - 8 * S) // 2
    f = _font(13 * S, True)
    # ~83% gold for deselected labels — clearly a tappable control, not greyed.
    DESEL_GOLD = _lerp((0, 0, 0), _GOLD_BRIGHT, 0.85)
    DESEL_PATINA = _lerp((0, 0, 0), PATINA_PALE, 0.84)

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
            pygame.draw.line(glow, (255, 255, 255, 95),
                             (8 * S, 3 * S), (half - 12 * S, 3 * S), 2 * S)
            surf.blit(glow, (hx + 2 * S, seg_y + 2 * S))
            txt_col = NEAR_BLACK
        else:
            # Hollow segment — add a 1px BRIGHTER top hairline so the deselected
            # half still reads as a raised, tappable control.
            hair = pygame.Surface((half - 6 * S, 2 * S), pygame.SRCALPHA)
            hcol = (*PATINA_PALE, 150) if aged else (*_GOLD_PALE, 150)
            pygame.draw.line(hair, hcol, (4 * S, 0), (half - 10 * S, 0),
                             1 * S)
            surf.blit(hair, (hx + 3 * S, seg_y + 3 * S))
            txt_col = DESEL_PATINA if aged else DESEL_GOLD

        # The V5 coin is ALWAYS bright live-gold; the V4 coin is always bronze.
        ctop, cbot = (LIVE_COIN_TOP, LIVE_COIN_BOT) if live else \
            (BRONZE_COIN_TOP, BRONZE_COIN_BOT)
        if coin_inside:
            # Coin left-anchored at the leading edge — never overlaps the
            # label (the round-2 #2 failure mode).
            glyph = _coin_glyph(big_coin_r, ctop, cbot, live)
            gx = hx + 6 * S
            surf.blit(glyph, (gx, cy - glyph.get_height() // 2))
            lbl = f.render(label, True, txt_col)
            lx = gx + glyph.get_width() + 4 * S
            # Centre the label in the space remaining to the half's right edge.
            avail = (hx + half) - lx
            surf.blit(lbl, (lx + (avail - lbl.get_width()) // 2,
                            cy - lbl.get_height() // 2))
        else:
            glyph = _coin_glyph(coin_r, ctop, cbot, live)
            gw = glyph.get_width()
            lbl = f.render(label, True, txt_col)
            group_w = gw + 4 * S + lbl.get_width()
            gx = cx - group_w // 2
            surf.blit(glyph, (gx, cy - glyph.get_height() // 2))
            surf.blit(lbl, (gx + gw + 4 * S, cy - lbl.get_height() // 2))

    _half(seg_x, "V5", v5_active, live=True)
    _half(seg_x + half, lgnd_label, not v5_active, live=False)


# ── Candidate 1 — Fused Lead (LOCKED WINNER) ─────────────────────────────────
def render_fused(v5_active):
    """The locked lead: segmented pill-track + era coins, worded frozen ribbon
    on the legends board (one line tall, replacing the subline), plus the wax
    FINAL seal in the dead-zone. Live board keeps the LIVE subline."""
    aged = not v5_active
    surf = _base(aged=aged)
    _title(surf, 34 * S, aged)

    seg_y, seg_h = 58 * S, 28 * S
    seg_x, seg_w = 18 * S, (W - 36) * S
    _segmented_control(surf, seg_x, seg_y, seg_w, seg_h, v5_active, aged)

    if v5_active:
        _subtitle(surf, "LIVE  ·  CURRENT SEASON", 100 * S, _GOLD_PALE)
        _draw_rows(surf, V5_SCORES, 14 * S, 114 * S, (W - 28) * S, 35 * S,
                   LIVE_THEME)
        _tap(surf, _GOLD_MUTED)
    else:
        # The frozen ribbon REPLACES the subline (same vertical slot) so it
        # never eats a row's height.
        _frozen_ribbon(surf, Ws // 2, 100 * S, (W - 70) * S, 18 * S)
        bottom = _draw_rows(surf, V4_SCORES, 14 * S, 114 * S, (W - 28) * S,
                            35 * S, AGED_THEME)
        _wax_seal(surf, Ws // 2, (bottom + Hs - 24 * S) // 2, 24 * S)
        _tap(surf, PATINA_BRIGHT)
    return surf


# ── Candidate 2 — Header Frost Band ──────────────────────────────────────────
def render_header_band(v5_active):
    """Same chassis as the lead, but the frozen signal is a full-width frost
    BAND tucked between the title and the tabs on the legends board (the
    round-2 #4 idea, cleaned up to flat tint + crystal ticks). Wax seal in the
    dead-zone keeps the double-signal. Title nudged up to make room."""
    aged = not v5_active
    surf = _base(aged=aged)
    _title(surf, 28 * S, aged, size=22 * S)

    if aged:
        # Header frost band sits ABOVE the tabs, between title and control.
        _frozen_ribbon(surf, Ws // 2, 52 * S, (W - 44) * S, 18 * S,
                       text="FROZEN  ·  v4 ERA  ·  EASIER")
        seg_y, seg_h = 74 * S, 26 * S
    else:
        seg_y, seg_h = 56 * S, 28 * S
    seg_x, seg_w = 18 * S, (W - 36) * S
    _segmented_control(surf, seg_x, seg_y, seg_w, seg_h, v5_active, aged)

    if v5_active:
        _subtitle(surf, "LIVE  ·  CURRENT SEASON", 98 * S, _GOLD_PALE)
        _draw_rows(surf, V5_SCORES, 14 * S, 112 * S, (W - 28) * S, 35 * S,
                   LIVE_THEME)
        _tap(surf, _GOLD_MUTED)
    else:
        bottom = _draw_rows(surf, V4_SCORES, 14 * S, 112 * S, (W - 28) * S,
                            35 * S, AGED_THEME)
        _wax_seal(surf, Ws // 2, (bottom + Hs - 24 * S) // 2, 24 * S)
        _tap(surf, PATINA_BRIGHT)
    return surf


# ── Candidate 3 — Inset Coins ────────────────────────────────────────────────
def render_inset_coins(v5_active):
    """Larger era coins seated neatly INSIDE each segment at the leading edge
    (learning from round-2 #2: coins never overlap the label). Worded frozen
    ribbon as the subline + wax seal in the dead-zone, same as the lead."""
    aged = not v5_active
    surf = _base(aged=aged)
    _title(surf, 34 * S, aged)

    seg_y, seg_h = 56 * S, 32 * S
    seg_x, seg_w = 16 * S, (W - 32) * S
    _segmented_control(surf, seg_x, seg_y, seg_w, seg_h, v5_active, aged,
                       coin_inside=True)

    if v5_active:
        _subtitle(surf, "LIVE  ·  CURRENT SEASON", 102 * S, _GOLD_PALE)
        _draw_rows(surf, V5_SCORES, 14 * S, 116 * S, (W - 28) * S, 35 * S,
                   LIVE_THEME)
        _tap(surf, _GOLD_MUTED)
    else:
        _frozen_ribbon(surf, Ws // 2, 102 * S, (W - 70) * S, 18 * S)
        bottom = _draw_rows(surf, V4_SCORES, 14 * S, 116 * S, (W - 28) * S,
                            35 * S, AGED_THEME)
        _wax_seal(surf, Ws // 2, (bottom + Hs - 24 * S) // 2, 24 * S)
        _tap(surf, PATINA_BRIGHT)
    return surf


# ── Candidate 4 — Stacked Tabs + Corner Medallion ────────────────────────────
def render_stacked_medallion(v5_active):
    """Two-line-stacked tab labels (coin over a small ERA caption) for a chunky,
    confident control, plus a small 'FINAL' corner medallion that is anchored
    to the BOTTOM-RIGHT of the tab track — deliberately clear of the centred
    TOP 10 header (fixes the round-2 #3 collision). Worded ribbon as subline."""
    aged = not v5_active
    surf = _base(aged=aged)
    _title(surf, 30 * S, aged, size=22 * S)

    seg_y, seg_h = 50 * S, 40 * S
    seg_x, seg_w = 18 * S, (W - 36) * S
    _stacked_control(surf, seg_x, seg_y, seg_w, seg_h, v5_active, aged)

    if aged:
        # Small corner FINAL medallion, anchored to the tab track's lower-right
        # — far below the centred title, so there is no header collision.
        _final_medallion(surf, seg_x + seg_w - 4 * S, seg_y + seg_h - 2 * S,
                         13 * S)

    if v5_active:
        _subtitle(surf, "LIVE  ·  CURRENT SEASON", 106 * S, _GOLD_PALE)
        _draw_rows(surf, V5_SCORES, 14 * S, 120 * S, (W - 28) * S, 34 * S,
                   LIVE_THEME)
        _tap(surf, _GOLD_MUTED)
    else:
        _frozen_ribbon(surf, Ws // 2, 106 * S, (W - 70) * S, 18 * S)
        _draw_rows(surf, V4_SCORES, 14 * S, 120 * S, (W - 28) * S, 34 * S,
                   AGED_THEME)
        _tap(surf, PATINA_BRIGHT)
    return surf


def _stacked_control(surf, seg_x, seg_y, seg_w, seg_h, v5_active, aged):
    """A taller segmented control whose halves stack a coin over a 2-line label
    (V5 / LIVE, LGND / v4). Same selected/deselected affordances as the lead."""
    half = seg_w // 2
    radius = 14 * S
    track_top = (20, 18, 46) if aged else (16, 11, 44)
    track_bot = (9, 9, 26) if aged else (8, 5, 26)
    trim = (*PATINA_BRIGHT, 140) if aged else (*_GOLD_BRIGHT, 130)
    _grad_round(surf, (seg_x, seg_y, seg_w, seg_h), track_top, track_bot,
                radius=radius, alpha=240, border=trim, border_w=1 * S)
    big = _font(14 * S, True)
    small = _font(9 * S, True)
    coin_r = 9 * S
    DESEL_GOLD = _lerp((0, 0, 0), _GOLD_BRIGHT, 0.85)
    DESEL_PATINA = _lerp((0, 0, 0), PATINA_PALE, 0.84)

    def _half(hx, top_lbl, sub_lbl, selected, live):
        cx = hx + half // 2
        if selected:
            top_c = LIVE_COIN_TOP if live else (180, 196, 178)
            bot_c = LIVE_COIN_BOT if live else PATINA_DEEP
            _grad_round(surf, (hx + 3 * S, seg_y + 3 * S, half - 6 * S,
                               seg_h - 6 * S),
                        top_c, bot_c, radius=11 * S, alpha=255,
                        border=(*NEAR_BLACK, 200), border_w=1 * S)
            glow = pygame.Surface((half - 6 * S, seg_h - 6 * S),
                                  pygame.SRCALPHA)
            pygame.draw.line(glow, (255, 255, 255, 95),
                             (8 * S, 3 * S), (half - 16 * S, 3 * S), 2 * S)
            surf.blit(glow, (hx + 3 * S, seg_y + 3 * S))
            tcol = NEAR_BLACK
            scol = NEAR_BLACK
        else:
            hair = pygame.Surface((half - 8 * S, 2 * S), pygame.SRCALPHA)
            hcol = (*PATINA_PALE, 150) if aged else (*_GOLD_PALE, 150)
            pygame.draw.line(hair, hcol, (4 * S, 0), (half - 12 * S, 0), 1 * S)
            surf.blit(hair, (hx + 4 * S, seg_y + 4 * S))
            tcol = DESEL_PATINA if aged else DESEL_GOLD
            scol = tcol
        ctop, cbot = (LIVE_COIN_TOP, LIVE_COIN_BOT) if live else \
            (BRONZE_COIN_TOP, BRONZE_COIN_BOT)
        glyph = _coin_glyph(coin_r, ctop, cbot, live)
        # Coin to the left, two-line label to the right of it.
        ti = big.render(top_lbl, True, tcol)
        si = small.render(sub_lbl, True, scol)
        grp_w = glyph.get_width() + 4 * S + max(ti.get_width(), si.get_width())
        gx = cx - grp_w // 2
        cy = seg_y + seg_h // 2
        surf.blit(glyph, (gx, cy - glyph.get_height() // 2))
        tx = gx + glyph.get_width() + 4 * S
        surf.blit(ti, (tx, cy - ti.get_height() + 1 * S))
        surf.blit(si, (tx, cy + 2 * S))

    _half(seg_x, "V5", "LIVE", v5_active, live=True)
    _half(seg_x + half, "LGND", "v4 ERA", not v5_active, live=False)


def _final_medallion(surf, right_x, bottom_y, r):
    """Small round 'FINAL' medallion — a deep-gold disc with FINAL engraved,
    anchored by its bottom-right corner so it tucks under the tab track and
    well clear of the centred header."""
    cx = right_x - r
    cy = bottom_y - r
    disc = pygame.Surface((r * 2 + 2 * S, r * 2 + 2 * S), pygame.SRCALPHA)
    cc = r + 1 * S
    for yy in range(-r, r + 1):
        half = int(math.sqrt(max(0, r * r - yy * yy)))
        if half <= 0:
            continue
        u = (yy + r) / max(1, 2 * r)
        pygame.draw.line(disc, (*_lerp(WAX_RED_HI, WAX_RED, u), 245),
                         (cc - half, cc + yy), (cc + half, cc + yy))
    pygame.draw.circle(disc, (*PATINA_PALE, 220), (cc, cc), r - 1 * S, 1 * S)
    fi = _font(8 * S, True).render("FINAL", True, (245, 222, 212))
    disc.blit(fi, fi.get_rect(center=(cc, cc)))
    surf.blit(disc, disc.get_rect(center=(cx, cy)))


# ── Candidate 5 — Designer's Choice: Trophy Frame ────────────────────────────
def render_trophy_frame(v5_active):
    """Designer's choice: the lead chassis, but the era cue is amplified by a
    procedural TROPHY flanking the title (gold, live / patina, frozen). On the
    frozen board the trophy is patina-tinted and the worded ribbon + wax seal
    carry the frozen story; the live board's trophy reads gold + current.
    A confident 'hall of fame' framing that still keeps every fix."""
    aged = not v5_active
    surf = _base(aged=aged)
    # Trophy flanks the title — small, ceremonial, and tinted per era.
    _flanked_title(surf, 34 * S, aged)

    seg_y, seg_h = 60 * S, 28 * S
    seg_x, seg_w = 18 * S, (W - 36) * S
    _segmented_control(surf, seg_x, seg_y, seg_w, seg_h, v5_active, aged)

    if v5_active:
        _subtitle(surf, "LIVE  ·  CURRENT SEASON", 102 * S, _GOLD_PALE)
        _draw_rows(surf, V5_SCORES, 14 * S, 116 * S, (W - 28) * S, 35 * S,
                   LIVE_THEME)
        _tap(surf, _GOLD_MUTED)
    else:
        _frozen_ribbon(surf, Ws // 2, 102 * S, (W - 70) * S, 18 * S)
        bottom = _draw_rows(surf, V4_SCORES, 14 * S, 116 * S, (W - 28) * S,
                            35 * S, AGED_THEME)
        _wax_seal(surf, Ws // 2, (bottom + Hs - 24 * S) // 2, 24 * S)
        _tap(surf, PATINA_BRIGHT)
    return surf


def _flanked_title(surf, cy, aged):
    """TOP 10 title with a small procedural trophy on each side. The trophy is
    drawn on a temp surface so it can be patina-tinted for the frozen era
    without sepia warmth."""
    _title(surf, cy, aged)
    # Approximate the title half-width so trophies sit just outside it.
    f = _font(24 * S, True)
    tw = f.render("TOP 10", True, WHITE).get_width()
    tro = 12 * S
    for side in (-1, 1):
        tx = Ws // 2 + side * (tw // 2 + tro + 6 * S)
        if aged:
            # Draw the gold trophy on a temp surface and cool it to patina.
            tmp = pygame.Surface((tro * 4, tro * 4), pygame.SRCALPHA)
            _draw_trophy(tmp, tro * 2, tro * 2, tro)
            tint = pygame.Surface(tmp.get_size(), pygame.SRCALPHA)
            tint.fill((*PATINA_BRIGHT, 130))
            tmp.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            surf.blit(tmp, tmp.get_rect(center=(tx, cy)))
        else:
            _draw_trophy(surf, tx, cy, tro)


# ── Compose the 5-candidate review grid (each shown in BOTH eras) ────────────
def _candidates():
    return [
        ("1 - Fused Lead (LOCKED WINNER): segmented track + era coins, "
         "worded frozen ribbon + wax seal",
         [("V5 LIVE", lambda: render_fused(True)),
          ("V4 LEGENDS", lambda: render_fused(False))]),
        ("2 - Header Frost Band: frozen signal as a cleaned-up header band "
         "above the tabs",
         [("V5 LIVE", lambda: render_header_band(True)),
          ("V4 LEGENDS", lambda: render_header_band(False))]),
        ("3 - Inset Coins: larger coins seated inside each segment's leading "
         "edge (no label overlap)",
         [("V5 LIVE", lambda: render_inset_coins(True)),
          ("V4 LEGENDS", lambda: render_inset_coins(False))]),
        ("4 - Stacked + Medallion: two-line tabs + corner FINAL medallion "
         "clear of the header",
         [("V5 LIVE", lambda: render_stacked_medallion(True)),
          ("V4 LEGENDS", lambda: render_stacked_medallion(False))]),
        ("5 - Trophy Frame (designer's choice): lead chassis + flanking "
         "era-tinted trophies",
         [("V5 LIVE", lambda: render_trophy_frame(True)),
          ("V4 LEGENDS", lambda: render_trophy_frame(False))]),
    ]


def _grid():
    candidates = _candidates()
    pad = 16
    cap_h = 30
    state_cap_h = 20
    tile_w, tile_h = W, H
    cell_w = 2 * tile_w + pad        # one candidate occupies two side tiles
    title_h = 44
    cell_h = state_cap_h + tile_h + cap_h
    cols = 2
    rows = (len(candidates) + cols - 1) // cols
    grid_w = pad + cols * (cell_w + pad)
    grid_h = title_h + pad + rows * (cell_h + pad)

    grid = pygame.Surface((grid_w, grid_h))
    grid.fill((18, 14, 26))

    lab_font = pygame.font.Font(None, 22)
    state_font = pygame.font.Font(None, 20)
    title_font = pygame.font.Font(None, 30)
    title = title_font.render(
        "Skybit - Tabbed Leaderboard (V5 / V4 LEGENDS) - Round 3 (final 5)",
        True, (245, 220, 150))
    grid.blit(title, (pad, 14))

    for idx, (label, states) in enumerate(candidates):
        col = idx % cols
        row = idx // cols
        cx0 = pad + col * (cell_w + pad)
        cy0 = title_h + pad + row * (cell_h + pad)
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
        # Two-line wrap for the long candidate captions.
        line1, line2 = label, ""
        if len(label) > 56:
            mid = label.rfind(" ", 0, 56)
            line1, line2 = label[:mid], label[mid + 1:]
        cap1 = lab_font.render(line1, True, (235, 235, 245))
        grid.blit(cap1, (cx0 + 4, cy0 + state_cap_h + tile_h + 4))
        if line2:
            cap2 = lab_font.render(line2, True, (235, 235, 245))
            grid.blit(cap2, (cx0 + 4, cy0 + state_cap_h + tile_h + 4 + 20))
    return grid


def _lead_360():
    """The LEAD candidate at TRUE 360px width (tile not upscaled beyond native),
    both states side by side, for honest deselected-tab + bronze coin read."""
    pad = 14
    cap_h = 22
    title_h = 36
    grid_w = pad + 2 * (W + pad)
    grid_h = title_h + cap_h + H + pad
    g = pygame.Surface((grid_w, grid_h))
    g.fill((18, 14, 26))
    tf = pygame.font.Font(None, 26)
    g.blit(tf.render("Round 3 LEAD (cand. 1) - true 360px - V5 LIVE | "
                     "V4 LEGENDS", True, (245, 220, 150)), (pad, 10))
    cf = pygame.font.Font(None, 22)
    for si, (lbl, fn) in enumerate((("V5 LIVE", lambda: render_fused(True)),
                                    ("V4 LEGENDS",
                                     lambda: render_fused(False)))):
        hd = fn()
        tile = pygame.transform.smoothscale(hd, (W, H))  # 1080 -> 360 native
        tx = pad + si * (W + pad)
        ty = title_h + cap_h
        pygame.draw.rect(g, (40, 32, 50), (tx - 2, ty - 2, W + 4, H + 4),
                         border_radius=6)
        g.blit(tile, (tx, ty))
        g.blit(cf.render(lbl, True, (200, 210, 235)), (tx + 4, title_h))
    return g


def main():
    out_dir = os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), "docs", "leaderboard")
    os.makedirs(out_dir, exist_ok=True)

    grid = _grid()
    grid_path = os.path.join(out_dir, "round_3.png")
    pygame.image.save(grid, grid_path)
    print("wrote", grid_path, grid.get_size())

    lead = _lead_360()
    lead_path = os.path.join(out_dir, "round_3_lead_360.png")
    pygame.image.save(lead, lead_path)
    print("wrote", lead_path, lead.get_size())


if __name__ == "__main__":
    main()
