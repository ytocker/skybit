"""ACHIEVEMENT EARNED! — the end-of-run unlock screen (commendation card stack).

Shown once on death when a run unlocked one or more achievements, *before* the
run summary. A fixed gold-outlined "ACHIEVEMENT EARNED!" headline crowns a
vertical stack of gilt commendation cards — one per newly-unlocked achievement,
each carrying the real `draw_badge` medallion + name + requirement. When more
cards are earned than fit the viewport the stack scrolls (wheel + drag), with a
scrollbar; a near-stationary tap hands off to the run summary. The card art is
the gold-on-navy "Courier's Commendation" family the menus already use, so the
screen reads as part of the game.

The card list is rendered once into a tall content surface (rebuilt only if the
unlock set changes) and the visible slice is blitted 1:1 between a fixed header
and footer — the same cache discipline as the achievements list.
"""
from __future__ import annotations

import math
import pygame

from game.config import W, H
from game.draw import blit_glow, rounded_rect_grad, lerp_color
from game.achievement_icons import draw_badge
from game.hud import (
    _font, _outlined_text, _pill_btn, _draw_overlay_stars,
    _GOLD_BRIGHT, _GOLD_PALE, _GOLD_DEEP, _PANEL_DARK, _PANEL_LIGHTER, _NIGHT_DEEP,
)
from game import achievements as ach

# Card value palette — a genuine navy range so each plate has minted depth
# rather than flat-web uniformity (ported from the chosen design study).
_PLATE_TOP   = (30, 22, 70)
_PLATE_BOT   = (13, 8, 40)
_WELL_TOP    = (18, 12, 50)
_WELL_BOT    = (8, 4, 28)
_RULE_BRIGHT = (255, 224, 150)
_RULE_DEEP   = (150, 104, 26)
_BEVEL_HI    = (70, 54, 130)
_BEVEL_LO    = (6, 3, 22)

# Layout (logical px).
_HEADER_H = 84          # headline + count-chip crest live here, fixed
_FOOTER_H = 70          # TAP-to-continue pill, fixed
_CARD_W   = 330
_BIG_H    = 116         # the lifted top (newest) card
_CARD_H   = 104         # settled cards below it
_GAP      = 14
_TOP_PAD  = 4


def _backdrop():
    """Deep-night field with a soft vertical gradient + a scatter of twinkles —
    the same gold-on-navy night the menus live in."""
    surf = pygame.Surface((W, H))
    top, mid, bot = (16, 10, 44), (10, 5, 30), (5, 2, 18)
    for y in range(H):
        t = y / (H - 1)
        c = lerp_color(top, mid, t / 0.5) if t < 0.5 else lerp_color(mid, bot, (t - 0.5) / 0.5)
        pygame.draw.line(surf, c, (0, y), (W - 1, y))
    stars = []
    rng = 1234567
    for _ in range(46):
        rng = (rng * 1103515245 + 12345) & 0x7FFFFFFF
        x = rng % W
        rng = (rng * 1103515245 + 12345) & 0x7FFFFFFF
        y = rng % (H * 7 // 10)
        rng = (rng * 1103515245 + 12345) & 0x7FFFFFFF
        r = 1 + (rng % 2)
        rng = (rng * 1103515245 + 12345) & 0x7FFFFFFF
        ph = (rng % 628) / 100.0
        stars.append((x, y, r, ph))
    _draw_overlay_stars(surf, stars, 0.6)
    return surf


def _corner_ribbon(surf, rect, bright):
    """A small gilt corner-ribbon tab inside the card's top-right, so the plate
    reads as an awarded commendation rather than a generic card."""
    w, h = 18, 26
    x = rect.right - w - 14
    y = rect.top + 1
    hi = _GOLD_PALE if bright else _GOLD_BRIGHT
    lo = _GOLD_DEEP
    body = [(x, y), (x + w, y), (x + w, y + h), (x + w // 2, y + h - 7), (x, y + h)]
    pygame.draw.polygon(surf, lo, body)
    face = [(x, y), (x + w * 2 // 3, y), (x + w * 2 // 3, y + h - 5),
            (x + w // 2, y + h - 9), (x, y + h - 2)]
    pygame.draw.polygon(surf, hi, face)
    pygame.draw.polygon(surf, _RULE_DEEP, body, 1)
    pygame.draw.circle(surf, lo, (x + w // 2, y + 10), 2)


def _draw_card(surf, rect, item, newest=False):
    """One flat 2-D gilt commendation plate: drop-shadow gap, soft halo (newest
    only), navy plate gradient, gilt DOUBLE-rule frame, inner bevel, recessed
    well, then the medallion socket + name + requirement + corner ribbon."""
    icon_key, name, desc, hidden, tone = item

    # Drop-shadow gap so each plate reads as a separate inset on the stack.
    sh_off = 12 if newest else 5
    sh_a = 170 if newest else 90
    sh = pygame.Surface((rect.w + 12, rect.h + 12), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, sh_a), (6, 6, rect.w, rect.h), border_radius=16)
    sh = pygame.transform.smoothscale(
        pygame.transform.smoothscale(sh, ((rect.w + 12) // 2, (rect.h + 12) // 2)),
        (rect.w + 12, rect.h + 12))
    surf.blit(sh, (rect.x - 6, rect.y - 6 + sh_off))

    if newest:
        # Warm "it just landed" heat pooling at the base of the freshest plate.
        blit_glow(surf, rect.centerx, rect.bottom + 6,
                  int(rect.w * 0.26), (255, 190, 92), 34)

    radius = 16
    plate_top = lerp_color(_PLATE_TOP, _GOLD_DEEP, 0.05) if newest else _PLATE_TOP
    rounded_rect_grad(surf, rect, radius, plate_top, _PLATE_BOT)

    # Gilt DOUBLE-rule frame: bright outer hairline + deep inner hairline.
    out_w = 2 if newest else 1
    pygame.draw.rect(surf, _RULE_BRIGHT if newest else _GOLD_BRIGHT,
                     rect, width=out_w, border_radius=radius)
    inner = rect.inflate(-6, -6)
    pygame.draw.rect(surf, _RULE_DEEP, inner, width=1, border_radius=max(4, radius - 4))

    # Inner bevel — upper-left catch-light arc + lower-right shadow arc.
    bev = rect.inflate(-3, -3)
    pygame.draw.arc(surf, _BEVEL_HI, bev, math.radians(40), math.radians(210), 2)
    pygame.draw.arc(surf, _BEVEL_LO, bev, math.radians(210), math.radians(400), 2)

    # Recessed inner WELL the badge + text sit inside.
    well = pygame.Rect(rect.x + 10, rect.y + 10, rect.w - 20, rect.h - 20)
    rounded_rect_grad(surf, well, 11, _WELL_TOP, _WELL_BOT)
    pygame.draw.rect(surf, _BEVEL_LO, well, width=1, border_radius=11)
    pygame.draw.line(surf, _BEVEL_HI, (well.x + 6, well.y + 1), (well.right - 6, well.y + 1), 1)

    # Left medallion SOCKET — a circular gold-ringed seat the badge drops into.
    sock_d = rect.h - 26
    sock_cx = rect.x + 18 + sock_d // 2
    sock_cy = rect.centery
    pygame.draw.circle(surf, _WELL_BOT, (sock_cx, sock_cy), sock_d // 2 + 3)
    pygame.draw.circle(surf, (4, 2, 16), (sock_cx, sock_cy), sock_d // 2 + 3, 2)
    pygame.draw.circle(surf, _GOLD_BRIGHT, (sock_cx, sock_cy), sock_d // 2 + 2, 2)
    pygame.draw.circle(surf, _GOLD_DEEP, (sock_cx, sock_cy), sock_d // 2 + 5, 1)
    brect = pygame.Rect(0, 0, sock_d, sock_d)
    brect.center = (sock_cx, sock_cy)
    draw_badge(surf, icon_key, brect, True, hidden, tone)

    # NAME (gold bold) over DESCRIPTION (pale), right of the socket.
    text_x = sock_cx + sock_d // 2 + 14
    nf = _font(19 if newest else 18, True)
    nsh = nf.render(name, True, _PANEL_DARK)
    nimg = nf.render(name, True, _GOLD_PALE if newest else _GOLD_BRIGHT)
    name_y = rect.centery - 13
    surf.blit(nsh, (text_x + 1, name_y + 1))
    surf.blit(nimg, (text_x, name_y))
    rule_w = nimg.get_width() + 6
    ry = name_y + nimg.get_height() + 3
    pygame.draw.line(surf, _GOLD_DEEP, (text_x, ry), (text_x + rule_w, ry), 1)
    df = _font(12, True)
    # Roasts can be long; the full text wraps on the Wall screen, so truncate to
    # the card width here rather than overflow the plate edge.
    avail = rect.right - 14 - text_x
    d = desc
    if df.size(d)[0] > avail:
        while d and df.size(d + "…")[0] > avail:
            d = d[:-1]
        d = d.rstrip() + "…"
    surf.blit(df.render(d, True, (198, 188, 220)), (text_x, ry + 5))

    _corner_ribbon(surf, rect, newest)


def _headline(surf, n):
    """Centred gold-outlined "ACHIEVEMENT EARNED!" + a thin gold rule. When more
    than one unlocked, the rule splits around a gilt "xN" count chip so the
    player instantly reads how many landed at once."""
    cy = 40
    _outlined_text(surf, "ACHIEVEMENT EARNED!", (W // 2, cy), 19, shadow_offset=(2, 3))
    ry = cy + 18

    if n > 1:
        chip_f = _font(13, True)
        cimg = chip_f.render("x%d" % n, True, _NIGHT_DEEP)
        cw, ch = cimg.get_width() + 14, cimg.get_height() + 5
        chip = pygame.Rect(0, 0, cw, ch)
        chip.center = (W // 2, ry)
        gap = cw // 2 + 7
    else:
        chip = None
        gap = 6

    rule_half = 92
    for sgn in (-1, 1):
        x0 = W // 2 + sgn * gap
        x1 = W // 2 + sgn * rule_half
        pygame.draw.line(surf, _GOLD_DEEP, (x0, ry), (x1, ry), 2)
        pygame.draw.line(surf, _GOLD_PALE, (x0, ry - 1), (x1, ry - 1), 1)
        pygame.draw.polygon(surf, _GOLD_BRIGHT,
                            [(x1, ry - 3), (x1 + sgn * 4, ry), (x1, ry + 3), (x1 - sgn * 4, ry)])

    if chip is not None:
        rounded_rect_grad(surf, chip, chip.h // 2, _GOLD_PALE, _GOLD_BRIGHT)
        pygame.draw.rect(surf, _GOLD_DEEP, chip, width=1, border_radius=chip.h // 2)
        surf.blit(cimg, cimg.get_rect(center=chip.center))


class AchievementEarnedScene:
    WHEEL_STEP = 56
    _TAP_SLOP = 8

    def __init__(self, ids):
        self.ids = list(ids)
        # Shame unlocks ride the same end-of-run card but in the tarnished tone
        # — "ACHIEVEMENT EARNED!" over a roast is the joke.
        self.items = [(a.id, a.title, a.desc, a.hidden,
                       "tarnished" if ach.is_shame(a.id) else "gold")
                      for a in (ach.BY_ID[i] for i in self.ids) if a is not None]
        self._t = 0.0
        self.scroll_offset = 0.0
        self.max_scroll = 0.0
        self._drag_active = False
        self._drag_last = 0
        self._drag_moved = 0
        self._bg = None
        self._content = None
        self._content_h = 0
        self._build_content()

    # ── content build ─────────────────────────────────────────────────────
    def _viewport(self):
        return _HEADER_H, H - _FOOTER_H

    def _build_content(self):
        h = _TOP_PAD
        for k in range(len(self.items)):
            h += (_BIG_H if k == 0 else _CARD_H) + _GAP
        h += 8                              # bottom pad for the last shadow
        self._content_h = h

        surf = pygame.Surface((W, h), pygame.SRCALPHA)
        y = _TOP_PAD
        for k, item in enumerate(self.items):
            ch = _BIG_H if k == 0 else _CARD_H
            rect = pygame.Rect((W - _CARD_W) // 2, y, _CARD_W, ch)
            _draw_card(surf, rect, item, newest=(k == 0))
            y += ch + _GAP
        self._content = surf

        top, bot = self._viewport()
        self.max_scroll = max(0.0, h - (bot - top))
        self.scroll_offset = min(self.scroll_offset, self.max_scroll)

    # ── input ─────────────────────────────────────────────────────────────
    def scroll_by(self, dpx):
        self.scroll_offset = max(0.0, min(self.max_scroll, self.scroll_offset + dpx))

    def pointer_down(self, y):
        self._drag_active = True
        self._drag_last = y
        self._drag_moved = 0

    def pointer_move(self, y):
        if not self._drag_active:
            return
        dy = y - self._drag_last
        self.scroll_by(-dy)
        self._drag_moved += abs(dy)
        self._drag_last = y

    def pointer_up(self) -> bool:
        """Return True when the gesture was a tap (continue), False for a drag."""
        if not self._drag_active:
            return False
        self._drag_active = False
        return self._drag_moved < self._TAP_SLOP

    def update(self, dt):
        self._t += dt

    # ── render ────────────────────────────────────────────────────────────
    def render(self, surf, dt):
        self._t += dt
        if self._bg is None:
            self._bg = _backdrop()
        surf.blit(self._bg, (0, 0))

        top, bot = self._viewport()
        view_h = bot - top
        src_y = int(self.scroll_offset)
        src_h = min(view_h, self._content_h - src_y)
        if src_h > 0:
            surf.blit(self._content, (0, top), pygame.Rect(0, src_y, W, src_h))

        # Scrollbar (only when the stack overflows the viewport).
        if self.max_scroll > 0:
            track_x = W - 5
            pygame.draw.rect(surf, (255, 255, 255, 30), (track_x, top, 3, view_h), border_radius=2)
            thumb_h = max(24, int(view_h * view_h / self._content_h))
            travel = view_h - thumb_h
            thumb_y = top + int((self.scroll_offset / self.max_scroll) * travel)
            pygame.draw.rect(surf, _GOLD_BRIGHT, (track_x, thumb_y, 3, thumb_h), border_radius=2)

        # Fixed header crest (re-blit the bg strip so cards scroll cleanly under it).
        surf.blit(self._bg, (0, 0), pygame.Rect(0, 0, W, _HEADER_H))
        _headline(surf, len(self.items))

        # Fixed footer + TAP pill (with a scroll hint while there's more below).
        surf.blit(self._bg, (0, H - _FOOTER_H), pygame.Rect(0, H - _FOOTER_H, W, _FOOTER_H))
        if self.max_scroll > 0 and self.scroll_offset < self.max_scroll - 1:
            hint = _font(11, True).render("DRAG TO SEE MORE", True, _GOLD_PALE)
            hint.set_alpha(int(150 + 80 * math.sin(self._t * 4.0)))
            surf.blit(hint, hint.get_rect(center=(W // 2, H - _FOOTER_H + 12)))
        alpha = int(228 + 27 * math.sin(self._t * 3.0))
        _pill_btn(surf, (W // 2, H - 34), "TAP TO CONTINUE", size=17,
                  alpha=alpha, primary=True, wide=True)
