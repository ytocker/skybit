"""Final-tweak pass on the LOCKED WINNER ("Fused Lead") of the tabbed
leaderboard.

This reuses the round-3 lead chassis verbatim (segmented gold/navy pill tabs,
era coins, aged-navy legends tint, wax FINAL seal, full medal pills) and changes
only two things:

  * CHANGE 1 — Crown placement now matches the shipping ``HUD._render_leaderboard``
    EXACTLY: the rank-1 crown is centred on the LEFT rank-badge circle and seated
    ``7*S`` above its centre (``row_cy - 7*S - c_h``), using the same
    ``_get_crown_sprite_hd(S)`` sprite. The round-3 lead anchored the crown to the
    pill top (``ry - c_h - 1*S``); that is replaced here.

  * CHANGE 2 — Version-free copy. No "v4" / "v5" anywhere:
      - Tab labels are "CURRENT" (bright domed live-gold coin) and "LEGACY"
        (flat tarnished bronze coin). Selected/deselected styling is unchanged.
      - The CURRENT board subline reads "LIVE" (centred, gold).
      - The LEGACY board ribbon reads "FROZEN  ·  HALL OF FAME" (same aged-navy
        frost-tinted one-line ribbon, hard crystal ticks only). The drip-edged
        wax FINAL seal stays in the dead-zone below row 10.

Output: ``docs/leaderboard/lead_revised.png`` — the revised lead at TRUE 360px
(S=3 supersample smoothscaled to native 360x640, never upscaled beyond native),
both states side by side with "CURRENT" / "LEGACY" captions, mirroring the
existing ``round_3_lead_360.png`` layout.

Pipeline + palette + draw helpers are imported from ``game.hud`` so the
exploration reads as the real game; no new raster assets ship.
"""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

pygame.init()
pygame.display.set_mode((1, 1))  # font/surface init for the dummy driver

from game.config import W, H
from game.draw import WHITE, NEAR_BLACK
from game.hud import (
    _GOLD_BRIGHT, _GOLD_DEEP, _GOLD_PALE, _GOLD_MUTED,
    _PANEL_DARK, _PANEL_LIGHTER,
    _MEDAL_GRADIENTS,
    _medal_row_pill, _get_crown_sprite_hd,
    _outlined_text, _font,
)

S = 3                     # in-game supersample factor for the leaderboard
Ws, Hs = W * S, H * S

# ── Sample data ──────────────────────────────────────────────────────────────
# Low live (CURRENT) scores (the hard era) vs much higher LEGACY scores so the
# two tabs read as genuinely different difficulties; playful names, all <= 10
# chars.
CURRENT_SCORES = [
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
LEGACY_SCORES = [
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
# Legacy stays the SAME night-navy screen, just frozen — a desaturated
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
# CURRENT live gold — bright, warm.
LIVE_COIN_TOP = _GOLD_PALE
LIVE_COIN_BOT = _GOLD_DEEP
# LEGACY tarnished BRONZE — warmed deliberately so it reads as AGED BRONZE, not
# a grey "disabled" disc. A real copper/bronze hue (more red than green) keeps
# it legible as "old money" even next to the cool patina chrome.
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
    """Vertical night-sky gradient + a deterministic star field. Legacy keeps
    the night-blue DNA (only cooled/desaturated), never sepia."""
    bg = pygame.Surface((Ws, Hs))
    top = AGED_BG_TOP if aged else (10, 6, 30)
    bot = AGED_BG_BOT if aged else (4, 2, 16)
    for yy in range(Hs):
        t = yy / (Hs - 1)
        pygame.draw.line(bg, _lerp(top, bot, t), (0, yy), (Ws, yy))
    # Stars — fixed hashed positions for repeatability. Legacy cools them a
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
    Legacy uses a cool navy tint, not a warm one — keep the same screen."""
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
    (never flatten); plain rows re-skin per era. The #1 crown is placed
    EXACTLY as the shipping ``HUD._render_leaderboard``: centred on the LEFT
    rank-badge circle and seated ``7*S`` above its centre. Returns the y just
    below the last row (for placing seals in the dead-zone)."""
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

        # #1 crown — placed EXACTLY like the shipping leaderboard: centred on
        # the LEFT badge circle, seated 7*S above the badge centre.
        if rank == 1:
            c_w, c_h = hd_crown.get_size()
            surf.blit(hd_crown,
                      (badge_cx - c_w // 2,
                       row_cy - 7 * S - c_h))

        nm = entry["name"][:10]
        nm_img = f_name.render(nm, True, name_col)
        surf.blit(nm_img, (card_x + 44 * S, row_cy - nm_img.get_height() // 2))

        sc_img = f_score.render(str(entry["score"]), True, score_col)
        surf.blit(sc_img,
                  (card_x + card_w - 16 * S - sc_img.get_width(),
                   row_cy - sc_img.get_height() // 2))

        ry += row_h + row_gap
    return ry


# Live (CURRENT) plain-row theme — deep navy panels, gold accents.
LIVE_THEME = {
    "plain_top": _PANEL_LIGHTER,
    "plain_bot": _PANEL_DARK,
    "border": (_GOLD_BRIGHT, 110),
    "name_col": WHITE,
    "score_col": _GOLD_BRIGHT,
    "badge_col": _GOLD_BRIGHT,
    "badge_num": _GOLD_BRIGHT,
}
# Frozen (LEGACY) AGED-NAVY theme — same navy panels cooled toward patina bronze.
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
def _frozen_ribbon(surf, cx, cy, w, h, text="FROZEN  ·  HALL OF FAME"):
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
    # one near the centre — deliberately geometric, never feathery.
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
def _segmented_control(surf, seg_x, seg_y, seg_w, seg_h, current_active, aged):
    """The locked round-1 #1 chassis fused with the #5 coin-state. One pill
    track, two equal halves; each half carries its era coin (live gold /
    tarnished bronze) so the era reads by value + shape before text.

    Selected   = filled gold gradient capsule + dark text + inner top glow.
    Deselected = hollow navy + gold hairline + a 1px BRIGHTER top hairline +
                 gold label at ~85% brightness — so it reads tappable, not
                 disabled.

    The CURRENT coin stays BRIGHT live-gold even on the frozen board so users
    know the live board is there to return to."""
    half = seg_w // 2
    radius = seg_h // 2
    # Track body — navy, cooled when legacy is active.
    track_top = (20, 18, 46) if aged else (16, 11, 44)
    track_bot = (9, 9, 26) if aged else (8, 5, 26)
    trim = (*PATINA_BRIGHT, 140) if aged else (*_GOLD_BRIGHT, 130)
    _grad_round(surf, (seg_x, seg_y, seg_w, seg_h), track_top, track_bot,
                radius=radius, alpha=240, border=trim, border_w=1 * S)

    coin_r = (seg_h - 14 * S) // 2
    f = _font(13 * S, True)
    # ~85% gold for deselected labels — clearly a tappable control, not greyed.
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

        # The CURRENT coin is ALWAYS bright live-gold; LEGACY is always bronze.
        ctop, cbot = (LIVE_COIN_TOP, LIVE_COIN_BOT) if live else \
            (BRONZE_COIN_TOP, BRONZE_COIN_BOT)
        glyph = _coin_glyph(coin_r, ctop, cbot, live)
        gw = glyph.get_width()
        lbl = f.render(label, True, txt_col)
        group_w = gw + 4 * S + lbl.get_width()
        gx = cx - group_w // 2
        surf.blit(glyph, (gx, cy - glyph.get_height() // 2))
        surf.blit(lbl, (gx + gw + 4 * S, cy - lbl.get_height() // 2))

    _half(seg_x, "CURRENT", current_active, live=True)
    _half(seg_x + half, "LEGACY", not current_active, live=False)


# ── Fused Lead (LOCKED WINNER) — revised ─────────────────────────────────────
def render_fused(current_active):
    """The locked lead: segmented pill-track + era coins, version-free frozen
    ribbon on the legacy board (one line tall, replacing the subline), plus the
    wax FINAL seal in the dead-zone. The current board keeps a short LIVE
    subline. Rank-1 crown is seated like the shipping board."""
    aged = not current_active
    surf = _base(aged=aged)
    _title(surf, 34 * S, aged)

    seg_y, seg_h = 58 * S, 28 * S
    seg_x, seg_w = 18 * S, (W - 36) * S
    _segmented_control(surf, seg_x, seg_y, seg_w, seg_h, current_active, aged)

    if current_active:
        _subtitle(surf, "LIVE", 100 * S, _GOLD_PALE)
        _draw_rows(surf, CURRENT_SCORES, 14 * S, 114 * S, (W - 28) * S, 35 * S,
                   LIVE_THEME)
        _tap(surf, _GOLD_MUTED)
    else:
        # The frozen ribbon REPLACES the subline (same vertical slot) so it
        # never eats a row's height.
        _frozen_ribbon(surf, Ws // 2, 100 * S, (W - 70) * S, 18 * S)
        bottom = _draw_rows(surf, LEGACY_SCORES, 14 * S, 114 * S, (W - 28) * S,
                            35 * S, AGED_THEME)
        _wax_seal(surf, Ws // 2, (bottom + Hs - 24 * S) // 2, 24 * S)
        _tap(surf, PATINA_BRIGHT)
    return surf


# ── Compose the revised-lead sheet at TRUE 360px, both states side by side ────
def _lead_revised():
    """The revised LEAD at TRUE 360px width (tile not upscaled beyond native),
    both states side by side with CURRENT / LEGACY captions."""
    pad = 14
    cap_h = 22
    title_h = 36
    grid_w = pad + 2 * (W + pad)
    grid_h = title_h + cap_h + H + pad
    g = pygame.Surface((grid_w, grid_h))
    g.fill((18, 14, 26))
    tf = pygame.font.Font(None, 26)
    g.blit(tf.render("Fused Lead (revised) - true 360px - CURRENT | LEGACY",
                     True, (245, 220, 150)), (pad, 10))
    cf = pygame.font.Font(None, 22)
    for si, (lbl, fn) in enumerate((("CURRENT", lambda: render_fused(True)),
                                    ("LEGACY",
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

    lead = _lead_revised()
    lead_path = os.path.join(out_dir, "lead_revised.png")
    pygame.image.save(lead, lead_path)
    print("wrote", lead_path, lead.get_size())


if __name__ == "__main__":
    main()
