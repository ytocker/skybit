"""Candidate visual designs for the store, selected by config.STORE_DESIGN.

Three designs (see docs/confirm_purchase_v8/premium-v1/colorways/
before_vs_chosen_v4.png, columns left to right):

  "classic" — the original store look; the only change applied game-side
              is the rarity-banner draw order fix from FINAL_SPEC.md
              (drawn above the shelf instead of buried under it).
  "antique" — aged-gold metalwork (exploration lineage: checkpoint 7 /
              figure K v11 "BASE"): antique-gold palette, D1 double-bevel
              perimeter on popup/buttons/cards, gold constellation-web
              behind the upper card, bullion price bar, I5 inner-keyline
              BUY accent, tucked corner gems, smooth halo.
  "gilded"  — polished rim-shine gold (the locked candidate): same
              skeleton as antique, with the perimeter swapped for the
              rim-shine gold stack at x1.4 thickness (popup, buttons,
              cards) and the I1 swash-underline on a mat-free BUY.

Everything here is a self-contained port of the reference renderers under
tools/ (the _confirm_v8_premv1_hybrid2_* family); store.py and
store_cards.py branch on DESIGN at their draw sites.
"""
import math

import pygame

from . import store_cards as sc
from .store_cards import (m, font, vgrad_stops, bevel_rim, top_sheen,
                          drop_shadow, plain_text, contact_shadow,
                          coin_glyph, _glyph_base, _stamp_bold, facet_gem)
from .config import STORE_DESIGN

# ── palettes ──────────────────────────────────────────────────────────────────
GOLD = dict(deep=(96, 66, 14), mid=(214, 156, 48), bright=(255, 210, 92),
            gem=(240, 178, 54), gem_deep=(120, 76, 12),
            glint=(240, 182, 62), ring=(250, 200, 80))
# G8 rim-shine: sampled from the popup hero rim's layered build
G8 = dict(deep=(96, 74, 30), mid=(236, 202, 116), bright=(246, 220, 140),
          gem=(236, 202, 116), gem_deep=(96, 74, 30),
          glint=(246, 220, 140), ring=(250, 200, 80))

# bullion price bar (PANEL_GOLD): stops, numeral colour, rim dark, rim bright
BAR_STOPS = [(0.0, (244, 214, 128)), (0.35, (224, 186, 98)),
             (0.7, (196, 160, 78)), (1.0, (146, 114, 50))]
BAR_NUM, BAR_RIM_D, BAR_RIM_B = (52, 28, 4), (78, 50, 14), (250, 226, 160)
# button faces (two-metals silver "can") + BUY text
CAN_STOPS = [(0.0, (24, 28, 44)), (1.0, (12, 14, 26))]
BUY_TEXT = (255, 248, 220)

CX = 130
BAR_H = 34
NAME_ZONE_C = 237          # zone-centred name block centre
CHIP_CY = 300              # bullion bar centre (may push down, see chip_cy)
CARD_S = 154.0 / 240.0     # card-frame scale relative to the popup
LOCKED_T = 1.4             # gilded perimeter thickness


# ── perimeter frames ──────────────────────────────────────────────────────────
def frame_double_bevel(big, rect, rad):
    """D1: filled mid-band + bevel rim + twin inner keylines (antique gold)."""
    deep, mid, bright = GOLD["deep"], GOLD["mid"], GOLD["bright"]
    band = rect.inflate(-m(3), -m(3))
    pygame.draw.rect(big, (*mid, 150), band, width=max(3, m(5)),
                     border_radius=rad - m(1))
    bevel_rim(big, rect, rad, deep, (*bright, 245), w=max(2, m(4)))
    inner = rect.inflate(-m(11), -m(11))
    pygame.draw.rect(big, (*bright, 170), inner, width=max(1, m(1.2)),
                     border_radius=rad - m(5))
    pygame.draw.rect(big, (*deep, 210), rect.inflate(-m(8), -m(8)),
                     width=max(1, m(1)), border_radius=rad - m(4))


def card_frame_d1(surf, rect, rad):
    """D1 scaled to card proportions (s = 154/240)."""
    s = CARD_S
    deep, mid, bright = GOLD["deep"], GOLD["mid"], GOLD["bright"]
    band = rect.inflate(-m(3 * s), -m(3 * s))
    pygame.draw.rect(surf, (*mid, 150), band, width=max(2, m(5 * s)),
                     border_radius=rad - m(1 * s))
    bevel_rim(surf, rect, rad, deep, (*bright, 245), w=max(1, m(4 * s)))
    inner = rect.inflate(-m(11 * s), -m(11 * s))
    pygame.draw.rect(surf, (*bright, 170), inner, width=max(1, m(1.2 * s)),
                     border_radius=rad - m(5 * s))
    pygame.draw.rect(surf, (*deep, 210), rect.inflate(-m(8 * s), -m(8 * s)),
                     width=max(1, m(1 * s)), border_radius=rad - m(4 * s))


def make_rim_shine_frame(s=1.0, t=LOCKED_T):
    """The hero rim's stroke stack on the rounded-rect perimeter: dark
    contact keyline, warm-gold rim, pale inner glint, a polished top-to-
    bottom brightness grade, and an additive warm specular kiss fading
    from the top. t scales every stroke width and inset."""
    s = s * t

    def frame(surf, rect, rad):
        layer = pygame.Surface(rect.size, pygame.SRCALPHA)
        lrect = layer.get_rect()
        pygame.draw.rect(layer, (5, 5, 12), lrect,
                         width=max(1, m(1.4 * s)), border_radius=rad)
        r1 = lrect.inflate(-2 * m(0.9 * s), -2 * m(0.9 * s))
        pygame.draw.rect(layer, (232, 196, 108), r1,
                         width=max(1, m(1.6 * s)),
                         border_radius=max(2, rad - m(0.9 * s)))
        r3 = lrect.inflate(-2 * m(2.0 * s), -2 * m(2.0 * s))
        pygame.draw.rect(layer, (246, 220, 140), r3,
                         width=max(1, m(0.8 * s)),
                         border_radius=max(2, rad - m(2.0 * s)))
        grade = pygame.Surface(rect.size, pygame.SRCALPHA)
        for yy in range(rect.h):
            g = 255 - int(90 * yy / max(1, rect.h - 1))
            pygame.draw.line(grade, (g, g, g, 255), (0, yy),
                             (rect.w - 1, yy))
        layer.blit(grade, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
        surf.blit(layer, rect.topleft)
        # specular kiss, premultiplied into RGB (BLEND_RGB_ADD ignores alpha)
        kiss = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(kiss, (85, 72, 48),
                         kiss.get_rect().inflate(-2 * m(0.9 * s),
                                                 -2 * m(0.9 * s)),
                         width=max(1, m(1.6 * s)),
                         border_radius=max(2, rad - m(0.9 * s)))
        fade_h = int(rect.h * 0.4)
        fade = pygame.Surface(rect.size, pygame.SRCALPHA)
        for yy in range(rect.h):
            a = max(0, 255 - yy * 255 // max(1, fade_h))
            pygame.draw.line(fade, (a, a, a, 255), (0, yy),
                             (rect.w - 1, yy))
        kiss.blit(fade, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
        surf.blit(kiss, rect.topleft, special_flags=pygame.BLEND_RGB_ADD)
    return frame


# ── background ornament: B5 constellation-web ─────────────────────────────────
_Q_DEEP = (22, 24, 56)
_CX_L, _CY_L = 130, 235
_CLIP_Y = 337


def _web_apply(big, layer):
    mask = pygame.Surface(layer.get_size(), pygame.SRCALPHA)
    mask.fill((0, 0, 0, 0))
    pygame.draw.rect(mask, (255, 255, 255, 255),
                     pygame.Rect(m(14), m(131), m(232), m(_CLIP_Y - 131)),
                     border_radius=m(18))
    layer.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(layer, (0, 0))


def make_constellation(glint, deep_a=155, glint_a=138):
    """Star sigil: 4-point star nodes + connecting web + sparkles + ring."""
    def _star(layer, x, y, r, col):
        pts = [(x, y - r), (x + r * 0.3, y - r * 0.3), (x + r, y),
               (x + r * 0.3, y + r * 0.3), (x, y + r),
               (x - r * 0.3, y + r * 0.3), (x - r, y),
               (x - r * 0.3, y - r * 0.3)]
        pygame.draw.polygon(layer, col, pts)

    def hook(big):
        layer = pygame.Surface(big.get_size(), pygame.SRCALPHA)
        cx, cy = m(_CX_L), m(_CY_L)
        nodes = [(cx, cy - m(84)), (cx + m(74), cy - m(34)),
                 (cx + m(52), cy + m(58)), (cx - m(52), cy + m(58)),
                 (cx - m(74), cy - m(34)), (cx + m(30), cy - m(6)),
                 (cx - m(30), cy - m(6)), (cx, cy + m(30)),
                 (cx + m(88), cy + m(26)), (cx - m(88), cy + m(26))]
        web = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0),
               (0, 5), (0, 6), (1, 5), (4, 6), (5, 7), (6, 7), (2, 7),
               (3, 7), (5, 6), (1, 8), (2, 8), (4, 9), (3, 9)]
        pygame.draw.circle(layer, (*_Q_DEEP, deep_a - 10), (cx, cy - m(6)),
                           m(92), max(2, m(2)))
        for i, j in web:
            pygame.draw.line(layer, (*_Q_DEEP, deep_a), nodes[i], nodes[j],
                             max(2, m(1.8)))
            pygame.draw.line(layer, (*glint, glint_a - 30),
                             (nodes[i][0] + m(1), nodes[i][1] + m(1)),
                             (nodes[j][0] + m(1), nodes[j][1] + m(1)),
                             max(1, m(0.8)))
        for x, y in nodes:
            _star(layer, x, y, m(5), (*glint, glint_a))
            pygame.draw.circle(layer, (*_Q_DEEP, min(255, deep_a + 40)),
                               (x, y), m(1.4))
        for sx, sy in [(cx + m(48), cy - m(64)), (cx - m(48), cy - m(64)),
                       (cx + m(70), cy + m(16)), (cx - m(70), cy + m(16)),
                       (cx, cy + m(74))]:
            pygame.draw.line(layer, (*glint, glint_a - 20),
                             (sx - m(3), sy), (sx + m(3), sy), max(1, m(1)))
            pygame.draw.line(layer, (*glint, glint_a - 20),
                             (sx, sy - m(3)), (sx, sy + m(3)), max(1, m(1)))
        _web_apply(big, layer)
    return hook


# ── smooth hero halo (ring-free replacement for _alpha_aura) ─────────────────
_aura_cache: dict = {}


def _build_aura(radius, color, peak, layers):
    side = radius * 2 + 2
    try:
        import numpy as np
    except ImportError:
        # numpy is absent on the pygbag/web runtime (and bare CI). The
        # halo's alpha depends only on distance, so evaluate the same
        # cumulative profile per integer radius (1D, cheap) and paint it
        # as 1px-stepped rings — smooth, unlike the stock 24-ring stack.
        step = radius / layers
        ris = []
        for i in range(layers, 0, -1):
            r_i = int(radius * i / layers)
            a_i = int(peak * (1 - (i - 1) / layers) ** 1.6)
            if r_i > 0 and a_i > 0:
                ris.append((r_i, math.log1p(-a_i / 255.0)))
        g = pygame.Surface((side, side), pygame.SRCALPHA)
        c = (radius + 1, radius + 1)
        for d in range(radius, -1, -1):
            log_keep = 0.0
            for r_i, la in ris:
                w = min(1.0, max(0.0, (r_i - d) / step + 0.5))
                log_keep += w * la
            a = int(round(255.0 * (1.0 - math.exp(log_keep))))
            if a <= 0:
                continue
            if d == 0:
                pygame.draw.circle(g, (*color, a), c, 1)
            else:
                # width=2 so adjacent rings overlap pixel-complete; drawn
                # outside-in, the inner (stronger) ring wins the overlap
                pygame.draw.circle(g, (*color, a), c, d, 2)
        return g
    yy, xx = np.mgrid[0:side, 0:side]
    d = np.hypot(xx - (radius + 1), yy - (radius + 1))
    step = radius / layers
    log_keep = np.zeros((side, side), dtype=np.float64)
    for i in range(layers, 0, -1):
        r_i = int(radius * i / layers)
        a_i = int(peak * (1 - (i - 1) / layers) ** 1.6)
        if r_i <= 0 or a_i <= 0:
            continue
        w = np.clip((r_i - d) / step + 0.5, 0.0, 1.0)
        log_keep += w * np.log1p(-a_i / 255.0)
    alpha = np.rint(255.0 * (1.0 - np.exp(log_keep))).astype(np.uint8)
    g = pygame.Surface((side, side), pygame.SRCALPHA)
    rgb = pygame.surfarray.pixels3d(g)
    rgb[..., 0], rgb[..., 1], rgb[..., 2] = color[0], color[1], color[2]
    del rgb
    pygame.surfarray.pixels_alpha(g)[:, :] = alpha.T
    return g


def smooth_aura(surf, cx, cy, radius, color, peak=27, layers=15):
    """Built once per (radius, colour, strength) and cached — the confirm
    popup redraws every frame, so the halo must not be recomputed live."""
    key = (radius, color, peak, layers)
    g = _aura_cache.get(key)
    if g is None:
        g = _build_aura(radius, color, peak, layers)
        _aura_cache[key] = g
    surf.blit(g, (cx - radius - 1, cy - radius - 1))


def hero_circle(big, cx, cy, r, ring, cw=1.4, ca=180):
    side = r * 2 + 4
    layer = pygame.Surface((side, side), pygame.SRCALPHA)
    pygame.draw.circle(layer, (*ring, ca), (side // 2, side // 2), r,
                       max(2, m(cw)))
    big.blit(layer, (cx - side // 2, cy - side // 2))


# ── bullion price bar ─────────────────────────────────────────────────────────
def _bolt_dot(ov, bx, by):
    pygame.draw.circle(ov, (60, 42, 12), (bx, by), m(2))
    ring = pygame.Surface((m(6), m(6)), pygame.SRCALPHA)
    pygame.draw.circle(ring, (180, 140, 60, 120), (m(3), m(3)), m(2),
                       max(1, m(0.6)))
    ov.blit(ring, (bx - m(3), by - m(3)))
    arc_s = pygame.Surface((m(6), m(6)), pygame.SRCALPHA)
    pygame.draw.arc(arc_s, (200, 170, 100, 180),
                    pygame.Rect(0, 0, m(6) - 1, m(6) - 1),
                    3 * math.pi / 2, 2 * math.pi, 1)
    ov.blit(arc_s, (bx - m(3), by - m(3)))


def draw_bullion_chip(ov, price, cy=CHIP_CY):
    """The gold bullion price bar — identical in both affordability states
    (the can't-afford signal lives on the BUY button alone)."""
    txt = f"{price:,}"
    r = pygame.Rect(0, 0, m(168), m(BAR_H))
    r.center = (m(CX), m(cy))
    # chip_body_stops minus its gloss_sweep call: the S2-clean finish wants
    # NO gloss ellipse, and stock gloss_sweep's BLEND_ADD pass whites the
    # body out even at peak=0 (it adds the sweep's RGB regardless of alpha)
    rad = m(11)
    drop_shadow(ov, r, rad, blur=m(4), alpha=110, dy=m(2))
    ov.blit(vgrad_stops(r.w, r.h, rad, BAR_STOPS, 255, gamma=1.05), r.topleft)
    contact_shadow(ov, r, rad, m(3), alpha=80)
    pygame.draw.rect(ov, BAR_RIM_D, r, width=max(1, m(1.6)), border_radius=rad)
    bevel_rim(ov, r, rad, BAR_RIM_D, (*BAR_RIM_B, 235), w=max(1, m(1.5)))
    top_sheen(ov, r, m(11), m(12), peak=64)
    num_font = font(18)
    base = _stamp_bold(_glyph_base(txt, num_font, 0), m(0.7))
    bw = base.get_width()
    coin_d, gap = m(22), m(5)
    left = m(CX) - (coin_d + gap + bw) // 2
    coin_glyph(ov, left + coin_d // 2, m(cy), m(11))
    plain_text(ov, txt, num_font,
               (left + coin_d + gap + bw // 2, m(cy)), BAR_NUM,
               shadow_a=0, weight=m(0.7))
    for bx in (r.left + m(13), r.right - m(13)):
        _bolt_dot(ov, bx, m(cy))


def chip_cy(name):
    """Push-down mirroring the zone-centred 2-line name block."""
    fs = 45
    f = font(fs)
    mw = m(240 - 20)
    while _glyph_base(name, f, 0).get_width() > mw and fs > 24:
        fs -= 1
        f = font(fs)
    if _glyph_base(name, f, 0).get_width() <= mw:
        return CHIP_CY
    fh = f.get_height()
    gap = int(fh * 1.15)
    cy2 = m(NAME_ZONE_C) + gap // 2
    return max(CHIP_CY, (cy2 + fh // 2) // sc.SS + 10 + 17)


# ── BUY engraving (I1 swash + I5 keyline) ─────────────────────────────────────
# gilded-design engraving metal (the rim-shine golds)
_ENG_GLINT, _ENG_BRIGHT = (236, 202, 116), (246, 220, 140)
_ENG_SHADOW = (26, 17, 4)
_ENG_GEM, _ENG_GEM_DEEP = (236, 202, 116), (96, 74, 30)


def _engraved(ov, pts, w=1.7, body_a=235, hi_a=160):
    """Three-pass engraved stroke: shadow under, gold body, bright crest."""
    if len(pts) < 2:
        return
    sh = [(x + m(0.8), y + m(0.8)) for x, y in pts]
    hi = [(x - m(0.5), y - m(0.5)) for x, y in pts]
    pygame.draw.lines(ov, (*_ENG_SHADOW, 210), False, sh, max(2, m(w)))
    pygame.draw.lines(ov, (*_ENG_GLINT, body_a), False, pts, max(2, m(w)))
    pygame.draw.lines(ov, (*_ENG_BRIGHT, hi_a), False, hi, max(1, m(w - 0.7)))


def _spiral(cx, cy, r0, turns=1.9, phase=0.0, mirror=1, n=26, shrink=0.78):
    pts = []
    for k in range(n + 1):
        t = k / n
        th = phase + mirror * t * turns * 2 * math.pi
        rad = r0 * (1 - shrink * t)
        pts.append((cx + rad * math.cos(th), cy + rad * math.sin(th)))
    return pts


def _tapered(ov, pts, w0, w1, body_a=200, hi_a=115):
    thirds = max(1, len(pts) // 3)
    for i in range(3):
        seg = pts[i * thirds:(i + 1) * thirds + 1]
        if len(seg) < 2:
            continue
        t = i / 2
        w = w0 + (w1 - w0) * t
        _engraved(ov, seg, w=w, body_a=int(body_a * (1 - 0.18 * t)),
                  hi_a=int(hi_a * (1 - 0.25 * t)))


def _micro_gem(ov, x, y, r=2.2):
    pygame.draw.circle(ov, (*_ENG_SHADOW, 220),
                       (int(x + m(0.6)), int(y + m(0.6))), m(r + 0.8))
    facet_gem(ov, int(x), int(y), m(r), _ENG_GEM, _ENG_GEM_DEEP)


def _swash_underline(ov, r, half_tw):
    """I1: one calligraphic divider under the BUY label, curled ends,
    micro gem at centre."""
    y0 = r.centery + m(13)
    for side in (-1, 1):
        run = [(r.centerx + side * m(1.5), y0),
               (r.centerx + side * m(10), y0 + m(0.5)),
               (r.centerx + side * m(20), y0 - m(0.5))]
        curl = _spiral(r.centerx + side * m(26), y0 - m(2.2), m(2.8),
                       turns=1.15, phase=math.pi / 2, mirror=-side, n=20)
        _tapered(ov, run + curl, 1.5, 0.9, body_a=205, hi_a=120)
    _micro_gem(ov, r.centerx, y0, r=1.4)


def _inner_keyline(ov, r):
    """I5: hairline jeweller's mat inside the BUY border (base design)."""
    glint, bright, shadow = GOLD["glint"], GOLD["bright"], (26, 17, 4)
    kr = r.inflate(-m(13), -m(13))
    rad = m(7)
    pygame.draw.rect(ov, (*shadow, 175), kr.move(m(0.7), m(0.7)),
                     max(1, m(0.9)), border_radius=rad)
    pygame.draw.rect(ov, (*glint, 185), kr, max(1, m(0.9)),
                     border_radius=rad)
    pygame.draw.rect(ov, (*bright, 85), kr.move(-m(0.5), -m(0.5)),
                     max(1, m(0.5)), border_radius=rad)


# ── buttons ───────────────────────────────────────────────────────────────────
# locked (can't-afford) BUY: stock's greyed language on the design build
LOCKED_STOPS = [(0.0, (58, 60, 74)), (1.0, (40, 42, 54))]
LOCKED_LABEL = (150, 152, 162)


def _padlock(surf, cx, cy, h, color):
    bw, bh = int(h * 0.92), int(h * 0.60)
    body = pygame.Rect(0, 0, bw, bh)
    body.center = (cx, cy + int(h * 0.20))
    pygame.draw.rect(surf, color, body, border_radius=max(1, int(h * 0.14)))
    sr = int(h * 0.30)
    arc = pygame.Rect(cx - sr, body.top - sr, sr * 2, sr * 2)
    pygame.draw.arc(surf, color, arc, math.radians(15), math.radians(165),
                    max(1, int(h * 0.17)))
    kh = pygame.Rect(0, 0, max(1, int(h * 0.16)), max(1, int(h * 0.22)))
    kh.center = (cx, body.centery + int(h * 0.02))
    pygame.draw.rect(surf, (10, 14, 26), kh, border_radius=1)


def _locked_label(ov, r, lbl):
    lab_font = font(15)
    lw = lab_font.size(lbl)[0]
    lock_h = m(11)
    lock_w = int(lock_h * 0.92)
    inner = m(4)
    grp = lock_w + inner + lw
    gx = r.centerx - grp // 2
    _padlock(ov, gx + lock_w // 2, r.centery, lock_h, LOCKED_LABEL)
    plain_text(ov, lbl, lab_font, (gx + lock_w + inner + lw // 2, r.centery),
               LOCKED_LABEL, shadow_a=0, weight=m(0.6))


def draw_buttons_antique(ov, affordable=True):
    """Antique design: silver-can faces, antique-gold bevel rims (w=4),
    I5 inner keyline on BUY. An unaffordable BUY keeps the same frame
    construction dimmed to pewter: locked face, full-width grey rim,
    padlock label, ornament omitted."""
    rad = m(12)
    for cx, lbl in ((76, "BUY"), (184, "CANCEL")):
        locked = lbl == "BUY" and not affordable
        r = pygame.Rect(0, 0, m(99), m(42))
        r.center = (m(cx), m(360))
        drop_shadow(ov, r, rad, blur=m(3), alpha=100, dy=m(2))
        ov.blit(vgrad_stops(r.w, r.h, rad,
                            LOCKED_STOPS if locked else CAN_STOPS, 255),
                r.topleft)
        top_sheen(ov, r, rad, m(12), peak=10 if locked else 14)
        if locked:
            bevel_rim(ov, r, rad, (44, 44, 54), (156, 152, 164, 235),
                      w=max(1, m(4.0)))
            _locked_label(ov, r, lbl)
            continue
        bevel_rim(ov, r, rad, GOLD["deep"], (*GOLD["bright"], 235),
                  w=max(1, m(4.0)))
        if lbl == "BUY":
            _inner_keyline(ov, r)
        plain_text(ov, lbl, font(15), r.center, BUY_TEXT,
                   shadow_a=110, weight=m(0.8), keyline=(8, 6, 20), kw=m(0.9))


_rim_shine_btn = make_rim_shine_frame(CARD_S)


def _pewter_rim(ov, r, rad):
    """Desaturated rim-shine stack for the locked BUY: same construction,
    grey metal, no specular kiss."""
    s = CARD_S * LOCKED_T
    pygame.draw.rect(ov, (5, 5, 12), r, width=max(1, m(1.4 * s)),
                     border_radius=rad)
    r1 = r.inflate(-2 * m(0.9 * s), -2 * m(0.9 * s))
    pygame.draw.rect(ov, (150, 146, 138), r1, width=max(1, m(1.6 * s)),
                     border_radius=max(2, rad - m(0.9 * s)))
    r3 = r.inflate(-2 * m(2.0 * s), -2 * m(2.0 * s))
    pygame.draw.rect(ov, (176, 172, 164), r3, width=max(1, m(0.8 * s)),
                     border_radius=max(2, rad - m(2.0 * s)))


def draw_buttons_gilded(ov, affordable=True):
    """Gilded design: rim-shine rims, I1 swash on a mat-free BUY. An
    unaffordable BUY greys out like stock: locked face, pewter rim,
    padlock label, swash omitted."""
    rad = m(12)
    for cx, lbl in ((76, "BUY"), (184, "CANCEL")):
        locked = lbl == "BUY" and not affordable
        r = pygame.Rect(0, 0, m(99), m(42))
        r.center = (m(cx), m(360))
        drop_shadow(ov, r, rad, blur=m(3), alpha=100, dy=m(2))
        ov.blit(vgrad_stops(r.w, r.h, rad,
                            LOCKED_STOPS if locked else CAN_STOPS, 255),
                r.topleft)
        top_sheen(ov, r, rad, m(12), peak=10 if locked else 14)
        if locked:
            _pewter_rim(ov, r, rad)
            _locked_label(ov, r, lbl)
            continue
        _rim_shine_btn(ov, r, rad)
        if lbl == "BUY":
            half_tw = _glyph_base("BUY", font(15), 0).get_width() // 2
            _swash_underline(ov, r, half_tw + m(4))
        plain_text(ov, lbl, font(15), r.center, BUY_TEXT,
                   shadow_a=110, weight=m(0.8), keyline=(8, 6, 20), kw=m(0.9))


# ── design registry ───────────────────────────────────────────────────────────
def _resolve():
    if STORE_DESIGN == "antique":
        return dict(ring=GOLD["ring"],
                    bg_hook=make_constellation(GOLD["glint"]),
                    frame_hook=frame_double_bevel,
                    card_frame=card_frame_d1,
                    buttons=draw_buttons_antique)
    if STORE_DESIGN == "gilded":
        return dict(ring=G8["ring"],
                    bg_hook=make_constellation(G8["glint"]),
                    frame_hook=make_rim_shine_frame(1.0),
                    card_frame=make_rim_shine_frame(CARD_S),
                    buttons=draw_buttons_gilded)
    return None


DESIGN = _resolve()
