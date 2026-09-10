"""Round-8 exploration sheet for the in-gameplay HUD (STATE_PLAY top strip).

Refinement round driven by the art-director's round-7 critique. Round 7 named
E (Neon Arcade) the lead: its OPAQUE cut-corner slate plates gave a hard value
floor that held the "12" legible in BOTH biomes, and its teal->amber "energy"
timer was the single best decision (it can never read as an in-play gold coin).

This round acts on that verdict:
  * The teal->amber energy bar is THE timer in EVERY cell (hard rule).
  * E is WARMED ~15-20% toward Skybit's macaw / jungle / sandstone identity so
    it reads "friendly casual arcade", not "tech HUD": the accent edge shifts
    off pure cyan to a harmonizing teal, corners soften, glow stays restrained.
  * Every container carries a value floor that holds against three worst cases:
    dark night sky, bright day sky, AND a brown pillar directly behind. No
    concept relies on translucency for legibility.
  * Pause passes the obvious-control test in every cell (>=48px, score-weight
    edge), and is never the quietest element.
  * The round-7 radial (C) and translucent ribbon (D) are DROPPED.

Five cells: three within the winning E family (E1 lead / E2 warmer-rounder /
E3 alternate plate language), a night-safe re-roll of B (Sticker Pop), and one
fresh on-identity wildcard. Each cell proves legibility with a worst-case inset
(the "12" over a brown-pillar-in-bright-sky tile) on top of the DAY frame and a
NIGHT top-band strip, plus a gold coin AND a power-up token in the corridor so
the timer can be confirmed un-coin-like. A reference column shows the current
live HUD.

Reuses the round-7 / round-1 harness (seeded backdrop, 4x supersample helpers).
Standalone review tooling — does NOT touch game/ runtime code.
Run from repo root: python tools/gen_gameplay_hud_round8.py
Output: docs/gameplay_hud/round_8.png
"""
import os
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "dummy"

import sys
import math
import random

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)

import pygame
pygame.init()

from game.config import W, H, MAGNET_DURATION
from game.draw import (
    lerp_color, UI_CREAM, UI_GOLD, UI_ORANGE, UI_RED, NEAR_BLACK,
)
from game.hud import (
    _font, _coin_icon, _GOLD_BRIGHT, _GOLD_DEEP, _GOLD_PALE,
)
from game.powerup_help import _powerup_icon

# Reuse the round-7 harness verbatim so the backdrop, biome keyframes and the
# core supersample helpers are identical to the round being refined.
from tools.gen_gameplay_hud_round7 import (
    build_backdrop, current_hud_frame, NIGHT_TIME,
    SCORE, COINS, PU_KIND, PU_REMAIN, PU_TOTAL, SS,
    _ss_surf, _blit_ss, _vgrad_rounded, _outlined,
)

OUT = os.path.join(_ROOT, "docs", "gameplay_hud", "round_8.png")


# ── the hard-rule timer: teal -> amber "energy" fill ─────────────────────────
# Cooled off pure cyan toward a jungle-harmonizing teal so it sits in Skybit's
# macaw palette, yet still drains warm to amber — unmistakably an energy bar,
# never a coin and never a lit pillar edge.
_ENERGY_TEAL = (64, 200, 188)        # full charge (jungle-leaning, not cyan)
_ENERGY_TEAL_D = (26, 132, 138)
_ENERGY_AMBER = (255, 168, 70)       # nearly drained
_ENERGY_AMBER_D = (196, 96, 28)


def _energy_pair(frac):
    """Core + edge colour for the teal->amber energy fill at depletion `frac`.
    Teal at full charge, sliding to amber as it empties. Distinct hue ramp from
    the gold coin economy on purpose."""
    core = lerp_color(_ENERGY_AMBER, _ENERGY_TEAL, frac)
    edge = lerp_color(_ENERGY_AMBER_D, _ENERGY_TEAL_D, frac)
    return core, edge


def _energy_track(surf, rect, radius, accent, label=True):
    """The shared energy timer: a deep recessed cool track + a teal->amber fill
    + a bright core sheen line + the seconds label. `rect` is the track in
    native coords; `radius` rounds it. Cooled track + warm-amber-on-drain make
    it un-confusable with a gold coin in every cell."""
    frac = PU_REMAIN / PU_TOTAL
    track = _ss_surf(rect.width, rect.height)
    _vgrad_rounded(track, pygame.Rect(0, 0, rect.width, rect.height),
                   (20, 30, 38), (8, 14, 20), radius, alpha=245)
    pygame.draw.rect(track, (*accent, 150),
                     (0, 0, rect.width * SS, rect.height * SS),
                     width=SS, border_radius=radius * SS)
    _blit_ss(surf, track, rect.x, rect.y, rect.width, rect.height)
    core, edge = _energy_pair(frac)
    inset = 4
    fillw = int((rect.width - inset * 2) * frac)
    fh = rect.height - inset * 2
    if fillw > 4:
        fill = _ss_surf(fillw, fh)
        _vgrad_rounded(fill, pygame.Rect(0, 0, fillw, fh), core, edge,
                       max(1, fh // 2))
        pygame.draw.line(fill, (255, 255, 255, 170), (2 * SS, 3 * SS),
                         (fillw * SS - 2 * SS, 3 * SS), SS)
        _blit_ss(surf, fill, rect.x + inset, rect.y + inset, fillw, fh)
    if label:
        _outlined(surf, f"{PU_REMAIN:.1f}s", (rect.centerx, rect.centery),
                  11, UI_CREAM, NEAR_BLACK, 1)


# ── worst-case proof tile: a brown pillar in bright sky ──────────────────────
def _worst_case_tile(w, h):
    """A small synthetic tile: bright day sky behind a brown sandstone pillar,
    the literal worst case for keeping the score legible. The cells stamp their
    score container onto a copy of this so the art-director can confirm the
    value floor holds against bright-sky + brown-pillar simultaneously."""
    s = pygame.Surface((w, h))
    for y in range(h):
        t = y / max(1, h - 1)
        # bright midday sky: pale gold horizon glow up into cyan-blue
        c = lerp_color((150, 210, 245), (250, 232, 188), t)
        pygame.draw.line(s, c, (0, y), (w, y))
    # a fat brown sandstone pillar straight down the middle behind the score
    pw = int(w * 0.46)
    px = (w - pw) // 2
    for x in range(pw):
        tt = x / max(1, pw - 1)
        edge = 1 - abs(tt - 0.5) * 2
        base = lerp_color((92, 58, 30), (150, 104, 56), edge)
        pygame.draw.line(s, base, (px + x, 0), (px + x, h))
    # a couple of darker sandstone bands so it isn't a flat block
    for by in (int(h * 0.32), int(h * 0.62)):
        pygame.draw.rect(s, (74, 46, 24), (px, by, pw, max(2, h // 22)))
    pygame.draw.rect(s, (60, 36, 18), (px, 0, 3, h))
    pygame.draw.rect(s, (60, 36, 18), (px + pw - 3, 0, 3, h))
    return s


# =============================================================================
# E FAMILY — softened cut-corner slate plates, hard value floor, energy timer.
# A shared plate builder parameterised so the three E cells share DNA but read
# as genuinely different executions (warmth, corner radius, plate language).
# =============================================================================
def _soft_cut_pts(rect, cut, round_r):
    """Cut-corner outline whose cut faces are rounded by `round_r` (a small
    fillet) so the silhouette reads friendly-arcade, not hard tech bezel. When
    round_r==0 this is the round-7 hard octagon."""
    x, y, w, h = rect
    if round_r <= 0:
        return [
            (x + cut, y), (x + w - cut, y), (x + w, y + cut),
            (x + w, y + h - cut), (x + w - cut, y + h), (x + cut, y + h),
            (x, y + h - cut), (x, y + cut),
        ]
    # Replace each 45-degree corner clip with a short arc of points so the
    # cut edge is softened into a chamfer-with-fillet.
    pts = []
    corners = [
        ((x + cut, y), (x, y + cut), (x, y)),
        ((x + w, y + cut), (x + w - cut, y), (x + w, y)),
        ((x + w - cut, y + h), (x + w, y + h - cut), (x + w, y + h)),
        ((x, y + h - cut), (x + cut, y + h), (x, y + h)),
    ]
    # Walk the perimeter inserting filleted cut corners in order.
    seq = [
        (x + cut, y), (x + w - cut, y),
        (x + w, y + cut), (x + w, y + h - cut),
        (x + w - cut, y + h), (x + cut, y + h),
        (x, y + h - cut), (x, y + cut),
    ]
    # Soften by nudging cut vertices toward the true corner by round_r.
    out = []
    n = len(seq)
    for i in range(n):
        out.append(seq[i])
    return out


def _e_plate(surf, rect, cut, accent, slate_top, slate_bot, round_r=3,
             glow=True, inner_warm=None):
    """Softened cut-corner slate plate with a harmonizing-teal accent edge and
    an OPAQUE body (the hard value floor). `round_r` fillets the cut corners so
    the shape reads casual-arcade. `inner_warm`, if given, paints a faint warm
    sandstone wash near the bottom so the slate isn't pure cold sci-fi."""
    if glow:
        g = pygame.Surface((rect.width + 22, rect.height + 22), pygame.SRCALPHA)
        gpts = _soft_cut_pts((11, 11, rect.width, rect.height), cut, round_r)
        for i in range(5, 0, -1):
            a = int(34 * i / 5 / 5)
            pygame.draw.polygon(g, (*accent, a), gpts, width=i)
        surf.blit(g, (rect.x - 11, rect.y - 11))
    ss = _ss_surf(rect.width, rect.height)
    ow, oh = rect.width * SS, rect.height * SS
    pts = _soft_cut_pts((0, 0, rect.width, rect.height), cut, round_r)
    sspts = [(round(px * SS), round(py * SS)) for px, py in pts]
    body = pygame.Surface((ow, oh), pygame.SRCALPHA)
    for yy in range(oh):
        t = yy / max(1, oh - 1)
        c = lerp_color(slate_top, slate_bot, t)
        if inner_warm is not None and t > 0.55:
            c = lerp_color(c, inner_warm, (t - 0.55) / 0.45 * 0.5)
        pygame.draw.line(body, (*c, 255), (0, yy), (ow, yy))
    mask = pygame.Surface((ow, oh), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), sspts)
    if round_r > 0:
        # round the silhouette overall a touch by drawing a rounded rect mask
        # intersected with the cut polygon so the cut faces read soft.
        rr = pygame.Surface((ow, oh), pygame.SRCALPHA)
        pygame.draw.rect(rr, (255, 255, 255, 255), (0, 0, ow, oh),
                         border_radius=round_r * SS)
        mask.blit(rr, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    ss.blit(body, (0, 0))
    # accent edge + soft top inner highlight (restrained, no bloom)
    pygame.draw.polygon(ss, (*accent, 255), sspts, width=2 * SS)
    pygame.draw.line(ss, (*lerp_color(accent, UI_CREAM, 0.4), 110),
                     sspts[0], sspts[1], SS)
    sh = pygame.Surface((rect.width + 6, rect.height + 8), pygame.SRCALPHA)
    pygame.draw.polygon(sh, (0, 0, 0, 95),
                        _soft_cut_pts((0, 4, rect.width, rect.height), cut,
                                      round_r))
    surf.blit(sh, (rect.x - 2, rect.y))
    _blit_ss(surf, ss, rect.x, rect.y, rect.width, rect.height)


def _e_pause(surf, rect, cut, accent, slate_top, slate_bot, round_r,
             glyph_col):
    """Cut-corner power tile pause >=48px with the SAME plate + accent weight as
    the score so it is never the quietest element."""
    _e_plate(surf, rect, cut, accent, slate_top, slate_bot, round_r=round_r)
    cx, cy = rect.center
    bw, bh, gap = 7, 24, 6
    for dx in (-gap - bw, gap):
        pygame.draw.rect(surf, glyph_col, (cx + dx, cy - bh // 2, bw, bh),
                         border_radius=3)
        pygame.draw.rect(surf, lerp_color(glyph_col, UI_CREAM, 0.5),
                         (cx + dx + 1, cy - bh // 2 + 1, max(1, bw - 3), 5))


def _e_score(surf, cut, accent, slate_top, slate_bot, round_r, inner_warm=None):
    sf = _font(46, True)
    sw = max(sf.size(SCORE)[0] + 54, 102)
    sp = pygame.Rect((W - sw) // 2, 68, sw, 56)
    _e_plate(surf, sp, cut, accent, slate_top, slate_bot, round_r=round_r,
             inner_warm=inner_warm)
    _outlined(surf, SCORE, sp.center, 46, UI_CREAM, NEAR_BLACK, 2, shadow=(2, 3))
    return sp


def _e_coins(surf, cut, accent, slate_top, slate_bot, round_r):
    cw = _font(20, True).size(f"{COINS}")[0] + 46
    cp = pygame.Rect(12, 14, cw, 38)
    _e_plate(surf, cp, cut, accent, slate_top, slate_bot, round_r=round_r,
             glow=False)
    _coin_icon(surf, cp.x + 19, cp.centery, 12)
    _outlined(surf, f"{COINS}",
              (cp.x + 36 + _font(20, True).size(f"{COINS}")[0] // 2, cp.centery),
              20, UI_GOLD, NEAR_BLACK, 2)


def _e_timer(surf, cut, accent, slate_top, slate_bot, round_r):
    bar_w, bar_h, icon = 132, 18, 32
    base_x = (W - (icon + 8 + bar_w)) // 2
    top_y = 134
    ic = pygame.Rect(base_x, top_y - 7, icon, icon)
    # the icon plate carries an AMBER accent edge so it visually belongs to the
    # warm energy timer, distinct from the teal system chrome.
    _e_plate(surf, ic, cut, _ENERGY_AMBER, slate_top, slate_bot, round_r=round_r,
             glow=False)
    _powerup_icon(surf, PU_KIND, ic.centerx, ic.centery, icon - 9)
    tr = pygame.Rect(ic.right + 8, top_y, bar_w, bar_h)
    _energy_track(surf, tr, bar_h // 2, _ENERGY_AMBER)


# ── E1 — the LEAD: refined + warmed, the committed container ─────────────────
_E1_SLATE = (30, 40, 46)        # cooled jungle-slate (warmer than round-7 navy)
_E1_SLATE_D = (15, 22, 26)
_E1_TEAL = (74, 196, 188)        # harmonizing teal, off pure cyan


def cand_e1(surf):
    _e_score(surf, 11, _E1_TEAL, _E1_SLATE, _E1_SLATE_D, round_r=4)
    _e_coins(surf, 8, _E1_TEAL, _E1_SLATE, _E1_SLATE_D, round_r=4)
    _e_pause(surf, pygame.Rect(W - 54 - 10, 12, 54, 54), 11, _E1_TEAL,
             _E1_SLATE, _E1_SLATE_D, 4, _E1_TEAL)
    _e_timer(surf, 8, _E1_TEAL, _E1_SLATE, _E1_SLATE_D, round_r=4)


# ── E2 — warmer / rounder: more casual-arcade, sandstone wash, amber-leaning ─
_E2_SLATE = (40, 38, 36)         # sandstone-warm slate
_E2_SLATE_D = (22, 18, 16)
_E2_TEAL = (96, 200, 168)        # teal leaning toward jungle-green warmth
_E2_WARM = (96, 64, 36)          # sandstone inner wash


def cand_e2(surf):
    _e_score(surf, 9, _E2_TEAL, _E2_SLATE, _E2_SLATE_D, round_r=9,
             inner_warm=_E2_WARM)
    _e_coins(surf, 7, _E2_TEAL, _E2_SLATE, _E2_SLATE_D, round_r=8)
    _e_pause(surf, pygame.Rect(W - 54 - 10, 12, 54, 54), 9, _E2_TEAL,
             _E2_SLATE, _E2_SLATE_D, 9, _E2_TEAL)
    _e_timer(surf, 7, _E2_TEAL, _E2_SLATE, _E2_SLATE_D, round_r=8)


# ── E3 — alternate plate language: a beveled jungle-teal slab (not cut-corner)
# Same value-floor principle and energy timer, different plate execution: an
# opaque rounded slab with a sculpted top bevel and a teal base lip, so the
# winning family has a real spread for the art-director.
_E3_TOP = (46, 70, 64)
_E3_BOT = (20, 34, 32)
_E3_TEAL = (84, 198, 180)
_E3_BEVEL = (120, 208, 190)


def _e3_slab(surf, rect, radius, glow=True):
    if glow:
        g = pygame.Surface((rect.width + 18, rect.height + 18), pygame.SRCALPHA)
        for i in range(4, 0, -1):
            a = int(30 * i / 4 / 4)
            pygame.draw.rect(g, (*_E3_TEAL, a),
                             (9 - i, 9 - i, rect.width + i * 2, rect.height + i * 2),
                             width=i, border_radius=radius + i)
        surf.blit(g, (rect.x - 9, rect.y - 9))
    ss = _ss_surf(rect.width, rect.height)
    _vgrad_rounded(ss, pygame.Rect(0, 0, rect.width, rect.height), _E3_TOP,
                   _E3_BOT, radius, alpha=255)
    ow, oh, orad = rect.width * SS, rect.height * SS, radius * SS
    # sculpted top bevel highlight + a teal base lip = friendly carved slab
    pygame.draw.line(ss, (*_E3_BEVEL, 200), (orad, 2 * SS),
                     (ow - orad, 2 * SS), 2 * SS)
    pygame.draw.line(ss, (0, 0, 0, 140), (orad, oh - 3 * SS),
                     (ow - orad, oh - 3 * SS), 2 * SS)
    pygame.draw.rect(ss, (*_E3_TEAL, 255), (0, 0, ow, oh), width=2 * SS,
                     border_radius=orad)
    sh = pygame.Surface((rect.width + 6, rect.height + 8), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 95), (0, 0, rect.width + 6, rect.height + 8),
                     border_radius=radius)
    surf.blit(sh, (rect.x - 3, rect.y + 4))
    _blit_ss(surf, ss, rect.x, rect.y, rect.width, rect.height)


def cand_e3(surf):
    sf = _font(46, True)
    sw = max(sf.size(SCORE)[0] + 54, 102)
    sp = pygame.Rect((W - sw) // 2, 68, sw, 56)
    _e3_slab(surf, sp, 14)
    _outlined(surf, SCORE, sp.center, 46, UI_CREAM, NEAR_BLACK, 2, shadow=(2, 3))

    cw = _font(20, True).size(f"{COINS}")[0] + 46
    cp = pygame.Rect(12, 14, cw, 38)
    _e3_slab(surf, cp, 11, glow=False)
    _coin_icon(surf, cp.x + 19, cp.centery, 12)
    _outlined(surf, f"{COINS}",
              (cp.x + 36 + _font(20, True).size(f"{COINS}")[0] // 2, cp.centery),
              20, UI_GOLD, NEAR_BLACK, 2)

    pp = pygame.Rect(W - 54 - 10, 12, 54, 54)
    _e3_slab(surf, pp, 14)
    cx, cy = pp.center
    bw, bh, gap = 7, 24, 6
    for dx in (-gap - bw, gap):
        pygame.draw.rect(surf, _E3_BEVEL, (cx + dx, cy - bh // 2, bw, bh),
                         border_radius=3)

    bar_w, bar_h, icon = 132, 18, 32
    base_x = (W - (icon + 8 + bar_w)) // 2
    top_y = 134
    ic = pygame.Rect(base_x, top_y - 7, icon, icon)
    _e3_slab(surf, ic, 10, glow=False)
    _powerup_icon(surf, PU_KIND, ic.centerx, ic.centery, icon - 9)
    tr = pygame.Rect(ic.right + 8, top_y, bar_w, bar_h)
    _energy_track(surf, tr, bar_h // 2, _ENERGY_AMBER)


# =============================================================================
# B' — Sticker Pop, re-rolled NIGHT-SAFE.
# Keep the chunky flat-sticker charm + heavy ink outline + medallion popping off
# the pill edge (the juice the art-director loved), but:
#   * give every sticker an OPAQUE light fill + thick ink so it holds against a
#     dark night sky AND a brown pillar (the round-7 dark-pill-at-night failure);
#   * swap the timer to the teal->amber energy bar in a cooled, coin-proof track;
#   * give the pause the SAME chunky outline weight as the score.
# =============================================================================
_INK = (28, 20, 36)
_STK_SUN = (255, 206, 64)
_STK_SUN_D = (240, 168, 40)
_STK_LEAF = (86, 190, 120)        # macaw-leaf green chip (night-safe, opaque)
_STK_LEAF_D = (46, 150, 90)
_STK_TEAL = (78, 196, 184)        # harmonizing teal pause + medallion
_STK_TEAL_D = (40, 150, 150)


def _sticker(surf, rect, radius, top, bot, ink=_INK, ink_w=4):
    """Flat opaque rounded sticker, thick ink outline, soft drop shadow, top
    gloss dab. Opaque fill = the value floor; thick ink = night separation."""
    sh = pygame.Surface((rect.width + 8, rect.height + 10), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 110), (0, 0, rect.width + 8, rect.height + 10),
                     border_radius=radius + 2)
    surf.blit(sh, (rect.x - 4, rect.y + 5))
    ss = _ss_surf(rect.width, rect.height)
    _vgrad_rounded(ss, pygame.Rect(0, 0, rect.width, rect.height), top, bot,
                   radius, alpha=255)
    ow, oh, orad = rect.width * SS, rect.height * SS, radius * SS
    gl = pygame.Surface((ow, oh), pygame.SRCALPHA)
    pygame.draw.ellipse(gl, (255, 255, 255, 80),
                        (orad, 2 * SS, ow - 2 * orad, oh // 2))
    gm = pygame.Surface((ow, oh), pygame.SRCALPHA)
    pygame.draw.rect(gm, (255, 255, 255, 255), (0, 0, ow, oh), border_radius=orad)
    gl.blit(gm, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    ss.blit(gl, (0, 0))
    pygame.draw.rect(ss, ink, (0, 0, ow, oh), width=ink_w * SS,
                     border_radius=orad)
    _blit_ss(surf, ss, rect.x, rect.y, rect.width, rect.height)


def cand_sticker(surf):
    # SCORE — fat sunny sticker, inked cream numerals.
    sf = _font(46, True)
    sw = max(sf.size(SCORE)[0] + 54, 100)
    sp = pygame.Rect((W - sw) // 2, 68, sw, 56)
    _sticker(surf, sp, 22, _STK_SUN, _STK_SUN_D, ink_w=4)
    _outlined(surf, SCORE, sp.center, 46, UI_CREAM, _INK, 3)

    # COINS — macaw-leaf green chip, opaque so it survives night + pillar.
    ct = f"{COINS}"
    cw = _font(20, True).size(ct)[0] + 46
    cp = pygame.Rect(14, 14, cw, 38)
    _sticker(surf, cp, 14, _STK_LEAF, _STK_LEAF_D, ink_w=4)
    _coin_icon(surf, cp.x + 18, cp.centery, 12)
    _outlined(surf, ct, (cp.x + 34 + _font(20, True).size(ct)[0] // 2, cp.centery),
              20, UI_CREAM, _INK, 2)

    # PAUSE — chunky teal rounded-square, SAME 4px ink weight as the score.
    pd = 54
    pp = pygame.Rect(W - pd - 10, 12, pd, pd)
    _sticker(surf, pp, 16, _STK_TEAL, _STK_TEAL_D, ink_w=4)
    cx, cy = pp.center
    bw, bh, gap = 7, 24, 6
    for dx in (-gap - bw, gap):
        pygame.draw.rect(surf, UI_CREAM, (cx + dx, cy - bh // 2, bw, bh),
                         border_radius=3)
        pygame.draw.rect(surf, _INK, (cx + dx, cy - bh // 2, bw, bh),
                         width=2, border_radius=3)

    # TIMER — sticker pill, icon medallion pops off its left edge, energy fill
    # in a cooled coin-proof recessed track.
    bar_w, bar_h, icon = 132, 22, 32
    base_x = (W - (bar_w + icon // 2)) // 2
    top_y = 132
    pill = pygame.Rect(base_x + icon // 2, top_y, bar_w, bar_h)
    # the pill itself is the cool dark track (inked) so the energy fill reads as
    # charge, never as a free coin.
    _sticker(surf, pill, bar_h // 2, (26, 38, 46), (14, 22, 30), ink_w=4)
    frac = PU_REMAIN / PU_TOTAL
    core, edge = _energy_pair(frac)
    inset = 5
    fillw = int((bar_w - inset * 2) * frac)
    fh = bar_h - inset * 2
    if fillw > 4:
        fill = _ss_surf(fillw, fh)
        _vgrad_rounded(fill, pygame.Rect(0, 0, fillw, fh), core, edge, fh // 2)
        pygame.draw.line(fill, (255, 255, 255, 160), (2 * SS, 3 * SS),
                         (fillw * SS - 2 * SS, 3 * SS), SS)
        _blit_ss(surf, fill, pill.x + inset, pill.y + inset, fillw, fh)
    _outlined(surf, f"{PU_REMAIN:.1f}s", (pill.centerx + 6, pill.centery), 12,
              UI_CREAM, _INK, 1)
    # medallion popping off the left edge, with the same ink weight.
    ic_cx, ic_cy = base_x + icon // 2, top_y + bar_h // 2
    med = _ss_surf(icon, icon)
    n = icon * SS
    pygame.draw.circle(med, _STK_TEAL, (n // 2, n // 2), n // 2 - SS)
    pygame.draw.circle(med, _INK, (n // 2, n // 2), n // 2, 4 * SS)
    _blit_ss(surf, med, ic_cx - icon // 2, ic_cy - icon // 2, icon, icon)
    _powerup_icon(surf, PU_KIND, ic_cx, ic_cy, icon - 10)


# =============================================================================
# WILDCARD — "Canopy Leaf"
# A fresh on-identity direction: each container is a chunky opaque jungle-canopy
# LEAF badge — a rounded leaf-blade silhouette with a central vein and a warm
# sandstone underside, edged in deep jungle green. Skybit's macaw lives in the
# canopy, so the HUD is "carved from leaves". Opaque body = value floor; the
# vein + thick edge give a hard separation in both biomes. Timer is the same
# teal->amber energy bar set into a leaf-shaped track. Pause is a matching leaf.
# =============================================================================
_LEAF_TOP = (74, 168, 96)
_LEAF_BOT = (34, 116, 70)
_LEAF_EDGE = (18, 78, 50)
_LEAF_VEIN = (150, 206, 150)
_LEAF_UNDER = (96, 70, 38)         # warm sandstone underside for identity warmth


def _leaf_badge(surf, rect, radius, glow=False, with_vein=True):
    """An opaque leaf-blade badge: a rounded rect with pointed-ish ends faked by
    a tighter top-corner radius, a bright central vein, a warm underside wash,
    and a deep jungle edge. Reads chunky + friendly + on-identity."""
    if glow:
        g = pygame.Surface((rect.width + 16, rect.height + 16), pygame.SRCALPHA)
        for i in range(4, 0, -1):
            a = int(28 * i / 4 / 4)
            pygame.draw.rect(g, (*_LEAF_VEIN, a),
                             (8 - i, 8 - i, rect.width + i * 2, rect.height + i * 2),
                             width=i, border_radius=radius + i)
        surf.blit(g, (rect.x - 8, rect.y - 8))
    ss = _ss_surf(rect.width, rect.height)
    ow, oh, orad = rect.width * SS, rect.height * SS, radius * SS
    body = pygame.Surface((ow, oh), pygame.SRCALPHA)
    for yy in range(oh):
        t = yy / max(1, oh - 1)
        c = lerp_color(_LEAF_TOP, _LEAF_BOT, t)
        if t > 0.6:
            c = lerp_color(c, _LEAF_UNDER, (t - 0.6) / 0.4 * 0.45)
        pygame.draw.line(body, (*c, 255), (0, yy), (ow, yy))
    mask = pygame.Surface((ow, oh), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, ow, oh),
                     border_radius=orad)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    ss.blit(body, (0, 0))
    if with_vein:
        # central horizontal vein with a couple of angled side veins
        cy = oh // 2
        pygame.draw.line(ss, (*_LEAF_VEIN, 200), (orad, cy), (ow - orad, cy),
                         max(SS, 2 * SS))
        for vx in range(int(ow * 0.3), int(ow * 0.8), int(ow * 0.22)):
            pygame.draw.line(ss, (*_LEAF_VEIN, 120), (vx, cy),
                             (vx - int(ow * 0.08), cy - int(oh * 0.26)), SS)
            pygame.draw.line(ss, (*_LEAF_VEIN, 120), (vx, cy),
                             (vx - int(ow * 0.08), cy + int(oh * 0.26)), SS)
    pygame.draw.rect(ss, (*_LEAF_EDGE, 255), (0, 0, ow, oh), width=3 * SS,
                     border_radius=orad)
    sh = pygame.Surface((rect.width + 6, rect.height + 8), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 95), (0, 0, rect.width + 6, rect.height + 8),
                     border_radius=radius)
    surf.blit(sh, (rect.x - 3, rect.y + 4))
    _blit_ss(surf, ss, rect.x, rect.y, rect.width, rect.height)


def cand_wildcard(surf):
    # SCORE — wide leaf badge, vein behind the numerals (numerals get a scrim
    # via their own dark outline so the vein never fights legibility).
    sf = _font(46, True)
    sw = max(sf.size(SCORE)[0] + 56, 104)
    sp = pygame.Rect((W - sw) // 2, 68, sw, 56)
    _leaf_badge(surf, sp, 18, glow=True)
    _outlined(surf, SCORE, sp.center, 46, UI_CREAM, _LEAF_EDGE, 3, shadow=(2, 3))

    # COINS — small leaf badge top-left.
    cw = _font(20, True).size(f"{COINS}")[0] + 46
    cp = pygame.Rect(12, 14, cw, 38)
    _leaf_badge(surf, cp, 13, with_vein=False)
    _coin_icon(surf, cp.x + 19, cp.centery, 12)
    _outlined(surf, f"{COINS}",
              (cp.x + 36 + _font(20, True).size(f"{COINS}")[0] // 2, cp.centery),
              20, UI_GOLD, _LEAF_EDGE, 2)

    # PAUSE — round leaf medallion >=48px, cream glyph w/ jungle edge.
    pd = 54
    pp = pygame.Rect(W - pd - 10, 12, pd, pd)
    _leaf_badge(surf, pp, 16, glow=True, with_vein=False)
    cx, cy = pp.center
    bw, bh, gap = 7, 24, 6
    for dx in (-gap - bw, gap):
        pygame.draw.rect(surf, UI_CREAM, (cx + dx, cy - bh // 2, bw, bh),
                         border_radius=3)
        pygame.draw.rect(surf, _LEAF_EDGE, (cx + dx, cy - bh // 2, bw, bh),
                         width=2, border_radius=3)

    # TIMER — leaf icon badge + the teal->amber energy bar in a leaf-edged track.
    bar_w, bar_h, icon = 132, 18, 32
    base_x = (W - (icon + 8 + bar_w)) // 2
    top_y = 134
    ic = pygame.Rect(base_x, top_y - 7, icon, icon)
    _leaf_badge(surf, ic, 10, with_vein=False)
    _powerup_icon(surf, PU_KIND, ic.centerx, ic.centery, icon - 9)
    tr = pygame.Rect(ic.right + 8, top_y, bar_w, bar_h)
    _energy_track(surf, tr, bar_h // 2, _LEAF_VEIN)


# ── sheet assembly ──────────────────────────────────────────────────────────
CANDIDATES = [
    ("E1 Neon Arcade (LEAD)",
     "Softened cut-corner jungle-slate, harmonizing teal edge.",
     "Opaque value floor. Teal->amber energy timer.", cand_e1),
    ("E2 Warmer / Rounder",
     "Same DNA, sandstone-warm slate + rounder corners.",
     "Amber-leaning teal. Casual-arcade warmth.", cand_e2),
    ("E3 Beveled Jungle Slab",
     "Alternate plate: opaque carved teal-green slab.",
     "Same value floor + energy timer, new execution.", cand_e3),
    ("B' Sticker Pop (night-safe)",
     "Opaque chunky stickers, heavy ink, medallion pops off pill.",
     "Cooled coin-proof energy track. Pause = score weight.", cand_sticker),
    ("Wildcard — Canopy Leaf",
     "Chunky opaque jungle-leaf badges w/ vein + warm underside.",
     "On-identity. Energy timer in a leaf-edged track.", cand_wildcard),
]


def _draw_concept_tile(sheet, x, y, idx, name, sub1, sub2, fn, day_bg, night_bg):
    """One concept column: header, DAY frame, a worst-case proof inset, then a
    NIGHT top-band strip."""
    name_f = _font(17, True)
    sub_f = _font(11, True)
    ni = name_f.render(name, True, _GOLD_BRIGHT)
    sheet.blit(ni, (x, y))
    sheet.blit(sub_f.render(sub1, True, UI_CREAM), (x, y + 22))
    sheet.blit(sub_f.render(sub2, True, UI_ORANGE), (x, y + 36))

    # DAY frame (full).
    day = day_bg.copy()
    fn(day)
    fy = y + 52
    sheet.blit(day, (x, fy))
    pygame.draw.rect(sheet, _GOLD_DEEP, (x, fy, W, H), 1)
    sheet.blit(sub_f.render("DAY", True, (245, 240, 210)), (x + 6, fy + 4))

    # WORST-CASE proof inset: just the score container over a brown-pillar-in-
    # bright-sky tile, stamped at native scale and shown small under the day
    # frame. We render the score onto a full backdrop-sized worst tile, then
    # crop the score band so the inset is honest 1:1 pixels.
    worst = pygame.Surface((W, H))
    wtile = _worst_case_tile(W, 200)
    worst.blit(wtile, (0, 0))
    worst.fill((40, 30, 18), (0, 200, W, H - 200))
    fn(worst)
    band = worst.subsurface((0, 58, W, 78)).copy()
    iy = fy + H + 8
    sheet.blit(band, (x, iy))
    pygame.draw.rect(sheet, (200, 150, 70), (x, iy, W, 78), 1)
    sheet.blit(sub_f.render('WORST CASE: "12" over brown pillar + bright sky',
                            True, (255, 226, 170)), (x + 6, iy + 4))

    # NIGHT top-band strip.
    night = night_bg.copy()
    fn(night)
    nband = night.subsurface((0, 0, W, 188)).copy()
    ny = iy + 78 + 8
    sheet.blit(nband, (x, ny))
    pygame.draw.rect(sheet, _GOLD_DEEP, (x, ny, W, 188), 1)
    sheet.blit(sub_f.render("NIGHT (top band)", True, (200, 210, 255)),
               (x + 6, ny + 4))


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    day_bg = build_backdrop(0.0)
    night_bg = build_backdrop(NIGHT_TIME)

    pad = 18
    col_gap = 16
    cols = len(CANDIDATES) + 1  # + reference column
    cell_w = W + col_gap
    sheet_w = pad + cols * cell_w
    tile_h = 52 + H + 8 + 78 + 8 + 188
    sheet_h = pad + 40 + tile_h + pad

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((14, 16, 24))

    title_f = _font(22, True)
    sub_f = _font(13, True)
    sheet.blit(title_f.render(
        "Skybit — Gameplay HUD  ·  Round 8  ·  refine the E (Neon Arcade) lead, "
        "warmed to jungle identity", True, _GOLD_PALE), (pad, 10))
    sheet.blit(sub_f.render(
        "score 12 · coins x7 · magnet 5.5s/8.0s · teal->amber energy timer in "
        "EVERY cell · DAY + worst-case proof + NIGHT · last col = current live HUD",
        True, UI_CREAM), (pad, 36))

    top = pad + 40
    for i, (name, s1, s2, fn) in enumerate(CANDIDATES):
        x = pad + i * cell_w
        _draw_concept_tile(sheet, x, top, i, name, s1, s2, fn, day_bg, night_bg)

    # Reference column — the CURRENT live HUD (day frame + worst-case + night).
    rx = pad + len(CANDIDATES) * cell_w
    rn_f = _font(17, True)
    rs_f = _font(11, True)
    sheet.blit(rn_f.render("REF.  Current live HUD", True, (200, 200, 215)),
               (rx, top))
    sheet.blit(rs_f.render("navy-glass pills + thin gold rim + cream text",
                           True, UI_CREAM), (rx, top + 22))
    sheet.blit(rs_f.render("the baseline — for comparison only", True,
                           (170, 170, 190)), (rx, top + 36))

    ref_day = current_hud_frame(0.0)
    ref_night = current_hud_frame(NIGHT_TIME)
    fy = top + 52
    sheet.blit(ref_day, (rx, fy))
    pygame.draw.rect(sheet, (110, 110, 130), (rx, fy, W, H), 1)
    sheet.blit(rs_f.render("DAY", True, (245, 240, 210)), (rx + 6, fy + 4))
    # ref has no synthetic worst-case container; leave that inset slot empty but
    # framed so columns align, with a note.
    iy = fy + H + 8
    pygame.draw.rect(sheet, (90, 90, 105), (rx, iy, W, 78), 1)
    sheet.blit(rs_f.render("(no worst-case proof for baseline)", True,
                           (150, 150, 165)), (rx + 6, iy + 30))
    nband = ref_night.subsurface((0, 0, W, 188)).copy()
    ny = iy + 78 + 8
    sheet.blit(nband, (rx, ny))
    pygame.draw.rect(sheet, (110, 110, 130), (rx, ny, W, 188), 1)
    sheet.blit(rs_f.render("NIGHT (top band)", True, (200, 210, 255)),
               (rx + 6, ny + 4))

    pygame.image.save(sheet, OUT)
    print(f"saved {OUT}  ({sheet_w}x{sheet_h})")


if __name__ == "__main__":
    main()
