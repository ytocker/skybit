"""
Achievements screen — a scrollable, category-grouped list of every unlockable.

The full list (taller than the 360×640 canvas) is rendered ONCE into a tall
supersampled surface and only rebuilt when the set of unlocked ids changes
(same cache discipline as the leaderboard). Each frame blits the visible slice
into a viewport between a fixed header and a pulsing footer prompt, plus a live
scrollbar. Scrolling is mouse-wheel + pointer-drag; a drag that barely moves is
treated as a tap to dismiss (the App decides on `pointer_up()`).
"""
from __future__ import annotations

import math
import pygame

from game.config import W, H
from game.draw import lerp_color
from game.hud import (
    _font, _outlined_text, _outline_pill_btn,
    _draw_overlay_stars, _draw_mountain_silhouette,
    _GOLD_BRIGHT, _GOLD_PALE, _GOLD_DEEP, _GOLD_MUTED,
    _PANEL_DARK, _PANEL_LIGHTER, _NIGHT_DEEP,
)
from game import achievements as ach
from game.achievement_icons import draw_badge

_WHITE = (245, 246, 255)
_DIM   = (150, 150, 172)
# A faint amethyst tint for masked Mystery rows so their "???" echoes the rarer
# amethyst badge without ever competing with gold.
_MYST_DIM = (176, 154, 200)
# Bronze-tinted dim for masked Wall-of-Shame rows, echoing the tarnished badge.
_SHAME_DIM = (180, 150, 120)
_BRONZE      = (198, 132, 66)     # Shame accent (mirrors gold on Fame)
_BRONZE_PALE = (228, 182, 130)
_BRONZE_DEEP = (110, 64, 28)

# Layout (logical px).
_HEADER_H = 56          # taller: title + a global progress bar live here
_TAB_H    = 32          # FAME | SHAME segmented toggle, below the header
_FOOTER_H = 54          # a grounded band for the real MENU button
_CAT_H    = 30
_ROW_H    = 56          # tightened ~10% for better scan density
_ROW_GAP  = 7
_PAD_X    = 12
_BADGE    = 44

# The gold underline beneath the ACHIEVEMENTS title — the category hairlines
# reuse this weight + horizontal inset so the whole screen reads as one system.
_RULE_INSET = 40

_S = 2  # supersample — 2× is indistinguishable from 3× at 360 px wide and halves build cost

_DECAY_K  = 5.0     # s⁻¹ exponential friction — tune lower for floatier feel
_STOP_VEL = 5.0     # px/s  below this the fling is considered stopped
_MAX_VEL  = 4000.0  # px/s  cap so an accidental huge swipe stays sane


# Seeded twinkle field so the wall lives in the same night world as the menu.
_STARS = []
def _star_field():
    if not _STARS:
        import random as _r
        rng = _r.Random(42)
        for _ in range(46):
            _STARS.append((rng.randint(6, W - 6), rng.randint(8, H - 150),
                           rng.choice((1, 1, 1, 2)), rng.uniform(0, 6.28)))
    return _STARS


class AchievementsScene:
    WHEEL_STEP = 56
    _TAP_SLOP = 8

    def __init__(self):
        self.scroll_offset = 0.0
        self.max_scroll = 0.0
        self._t = 0.0
        self._drag_active = False
        self._drag_last = 0
        self._drag_moved = 0
        self._scroll_vel = 0.0   # px/s — updated each frame during drag, used for fling
        self._drag_y_now  = 0    # latest y from pointer_move (read by update)
        self._drag_y_prev = 0    # y at the start of the last update tick
        self._content: "pygame.Surface | None" = None
        self._content_h = 0          # logical content height
        self._cache_key = None
        # Two walls on one screen: "fame" (gold) | "shame" (tarnished). The two
        # share the flat unlocked map; the active tab picks the roster + tone.
        self._tab = "fame"
        self.tab_fame_rect: "pygame.Rect | None" = None
        self.tab_shame_rect: "pygame.Rect | None" = None
        self.menu_btn_rect: "pygame.Rect | None" = None
        # Oddities one-shot guards: scrolling the Fame list to its foot and
        # visiting the Shame wall each unlock a hidden badge, once per session.
        self._saw_bottom = False
        self._saw_shame = False

    def _roster(self):
        """(category order, by-cat map, total, badge tone) for the active tab."""
        if self._tab == "shame":
            return (ach.SHAME_CATEGORY_ORDER, ach.BY_CAT_SHAME,
                    len(ach.SHAME_ACHIEVEMENTS), "tarnished")
        return (ach.CATEGORY_ORDER, ach.BY_CAT, len(ach.ACHIEVEMENTS), "gold")

    def set_tab(self, name: str) -> None:
        if name not in ("fame", "shame") or name == self._tab:
            return
        self._tab = name
        self.scroll_offset = 0.0
        self._scroll_vel = 0.0
        self._cache_key = None       # force a rebuild for the new roster
        if name == "shame" and not self._saw_shame:
            self._saw_shame = True
            ach.unlock("morbid_curiosity")

    # ── input ────────────────────────────────────────────────────────────
    def scroll_by(self, dpx: float) -> None:
        self.scroll_offset = max(0.0, min(self.max_scroll, self.scroll_offset + dpx))
        # Read the Fine Print: reaching the very bottom of the Fame list.
        if (self._tab == "fame" and not self._saw_bottom
                and self.max_scroll > 0 and self.scroll_offset >= self.max_scroll):
            self._saw_bottom = True
            ach.unlock("read_fine_print")

    def pointer_down(self, y: int) -> None:
        self._scroll_vel = 0.0
        self._drag_y_now = y
        self._drag_y_prev = y
        self._drag_active = True
        self._drag_last = y
        self._drag_moved = 0

    def pointer_move(self, y: int) -> None:
        if not self._drag_active:
            return
        self._drag_y_now = y
        dy = y - self._drag_last
        self.scroll_by(-dy)
        self._drag_moved += abs(dy)
        self._drag_last = y

    def pointer_up(self) -> bool:
        """Return True when the gesture was a tap (dismiss), False for a drag."""
        if not self._drag_active:
            return False
        self._drag_active = False
        # _scroll_vel was kept up-to-date each frame in update(); fling continues.
        return self._drag_moved < self._TAP_SLOP

    def update(self, dt: float) -> None:
        self._t += dt
        if self._drag_active:
            # Measure velocity once per game-clock tick — immune to sparse or
            # same-timestamp FINGERMOTION events that plagued the get_ticks() approach.
            if dt > 0:
                dy = self._drag_y_now - self._drag_y_prev
                instant = -(dy / dt)
                # EMA: weight 0.8 on fresh sample so fast direction changes register.
                self._scroll_vel = 0.8 * instant + 0.2 * self._scroll_vel
                self._scroll_vel = max(-_MAX_VEL, min(_MAX_VEL, self._scroll_vel))
            self._drag_y_prev = self._drag_y_now
            return
        # Fling coast — apply velocity then exponentially decay it.
        if abs(self._scroll_vel) <= _STOP_VEL:
            self._scroll_vel = 0.0
            return
        if (self._scroll_vel < 0 and self.scroll_offset <= 0) or \
                (self._scroll_vel > 0 and self.scroll_offset >= self.max_scroll):
            self._scroll_vel = 0.0
            return
        self.scroll_by(self._scroll_vel * dt)
        self._scroll_vel *= math.exp(-_DECAY_K * dt)

    # ── content build (cached) ───────────────────────────────────────────
    def _viewport(self) -> "tuple[int, int]":
        top = _HEADER_H + _TAB_H
        bot = H - _FOOTER_H
        return top, bot

    def _ensure_content(self, store: dict) -> None:
        order, by_cat, _total, tone = self._roster()
        key = (self._tab, ach.unlocked_signature(store))
        if self._content is not None and key == self._cache_key:
            return
        self._cache_key = key

        # Measure logical height first.
        h = 4
        for cat in order:
            h += _CAT_H
            h += len(by_cat[cat]) * (_ROW_H + _ROW_GAP)
        h += 6
        self._content_h = h

        S = _S
        surf = pygame.Surface((W * S, h * S), pygame.SRCALPHA)
        y = 4
        for cat in order:
            self._draw_cat_header(surf, cat, y, store, S)
            y += _CAT_H
            for a in by_cat[cat]:
                self._draw_row(surf, a, y, store, S, tone)
                y += _ROW_H + _ROW_GAP
        # Pre-scale to display resolution once so render can blit the visible
        # slice directly instead of calling smoothscale every frame.
        self._content = pygame.transform.smoothscale(surf, (W, h))

        top, bot = self._viewport()
        self.max_scroll = max(0.0, self._content_h - (bot - top))
        self.scroll_offset = min(self.scroll_offset, self.max_scroll)

    def _draw_cat_header(self, surf, cat, y, store, S):
        got, total = ach.category_progress(store, cat)
        complete = got >= total and total > 0
        head_col = _GOLD_PALE if complete else _GOLD_BRIGHT

        # A small gold diamond pip leads the section title — a struck-metal
        # bullet that echoes the badge rim and sets the title off the rail.
        py = int((y + _CAT_H * 0.5) * S)
        d = int(4 * S)
        pip = [(_PAD_X * S, py), (_PAD_X * S + d, py - d),
               (_PAD_X * S + 2 * d, py), (_PAD_X * S + d, py + d)]
        pygame.draw.polygon(surf, head_col, pip)
        pygame.draw.polygon(surf, _GOLD_DEEP, pip, max(1, S))

        label = self._scaled_text(cat.upper(), 15 * S, head_col)
        lx = _PAD_X * S + 3 * d
        surf.blit(label, (lx, int((y + 5) * S)))

        cnt = self._scaled_text(f"{got}/{total}", 13 * S, _GOLD_DEEP)
        cnt_x = int((W - _PAD_X) * S - cnt.get_width())
        surf.blit(cnt, (cnt_x, int((y + 6) * S)))

        # Engraved rule between the title and the count — same weight + fade as
        # the gold underline under the ACHIEVEMENTS title, so the category bands
        # and the header read as one system rather than two unrelated rules.
        ry = int((y + _CAT_H - 6) * S)
        rail_l = lx + label.get_width() + 6 * S
        rail_r = cnt_x - 6 * S
        if rail_r > rail_l:
            rail = pygame.Surface((rail_r - rail_l, max(2, 2 * S)), pygame.SRCALPHA)
            for xx in range(rail.get_width()):
                fade = 1.0 - xx / max(1, rail.get_width())
                rail.fill((*_GOLD_BRIGHT, int(160 * fade)),
                          (xx, 0, 1, max(2, 2 * S)))
            surf.blit(rail, (rail_l, ry))

    def _scaled_text(self, txt, size, color):
        return _font(int(size), True).render(txt, True, color)

    def _draw_row(self, surf, a: "ach.Achievement", y, store, S, tone="gold"):
        unlocked = ach.is_unlocked(store, a.id)
        shame = (tone == "tarnished")
        acc, acc_pale, acc_deep = ((_BRONZE, _BRONZE_PALE, _BRONZE_DEEP) if shame
                                   else (_GOLD_BRIGHT, _GOLD_PALE, _GOLD_DEEP))
        rx = _PAD_X * S
        rw = (W - _PAD_X * 2) * S
        ry = y * S
        rh = _ROW_H * S
        rad = 12 * S

        # Soft drop shadow so each card sits proud of the night field.
        sh = pygame.Surface((rw, rh), pygame.SRCALPHA)
        pygame.draw.rect(sh, (0, 0, 0, 120 if unlocked else 70),
                         (0, 0, rw, rh), border_radius=rad)
        surf.blit(sh, (rx, ry + 4 * S))

        # Minted card body — a gradient plate. Earned rows sit a clear tier above
        # the masked ones (which drop ~28% in value and lose the accent border),
        # so "earned" is carried by the body + star, not a loud ring of gold.
        if unlocked:
            body_top, body_bot = _PANEL_LIGHTER, _PANEL_DARK
        else:
            body_top, body_bot = (12, 9, 30), (7, 4, 18)
        panel = pygame.Surface((rw, rh), pygame.SRCALPHA)
        for yy in range(rh):
            t = yy / max(1, rh - 1)
            panel.fill(lerp_color(body_top, body_bot, t), (0, yy, rw, 1))
        mask = pygame.Surface((rw, rh), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, rw, rh), border_radius=rad)
        panel.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

        if unlocked:
            # Top sheen + bottom inner shadow = the menu's minted emboss.
            pygame.draw.line(panel, (*acc_pale, 110), (10 * S, 3 * S),
                             (rw - 10 * S, 3 * S), max(1, S))
            pygame.draw.line(panel, (4, 2, 14), (12 * S, rh - 3 * S),
                             (rw - 12 * S, rh - 3 * S), max(1, S))
            # A thin, low-chroma accent border (not a bright ring) + a left stripe.
            pygame.draw.rect(panel, (*acc_deep, 210), (0, 0, rw, rh),
                             width=max(1, S), border_radius=rad)
            stripe = pygame.Surface((max(3, 4 * S), rh - 8 * S), pygame.SRCALPHA)
            for yy in range(stripe.get_height()):
                t = yy / max(1, stripe.get_height() - 1)
                stripe.fill(lerp_color(acc_pale, acc_deep, t), (0, yy, stripe.get_width(), 1))
            stm = pygame.Surface(stripe.get_size(), pygame.SRCALPHA)
            pygame.draw.rect(stm, (255, 255, 255, 255), stm.get_rect(), border_radius=max(1, 2 * S))
            stripe.blit(stm, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            panel.blit(stripe, (3 * S, 4 * S))
        else:
            # Masked rows read as empty slots — a faint cool hairline, no accent.
            pygame.draw.rect(panel, (66, 62, 92, 90), (0, 0, rw, rh),
                             width=max(1, S), border_radius=rad)
        surf.blit(panel, (rx, ry))

        # Badge.
        badge_rect = pygame.Rect(int(rx + 8 * S), int(ry + (rh - _BADGE * S) // 2),
                                 _BADGE * S, _BADGE * S)
        draw_badge(surf, a.id, badge_rect, unlocked, a.hidden, tone)

        # Text block. EVERY locked achievement is masked — title, description and
        # any progress are hidden so the player discovers it in play rather than
        # reading it off a checklist. Mystery (amethyst) and Shame (bronze) rows
        # get a faintly tinted hint to echo their badge.
        tx = int(rx + (8 + _BADGE + 10) * S)
        if unlocked:
            title, desc = a.title, a.desc
            tcol, dcol = _GOLD_PALE, _WHITE
        elif shame:
            title, desc = "???", "Disgrace yourself in play to reveal."
            tcol = dcol = _SHAME_DIM
        elif a.hidden:
            title, desc = "???", "A rare secret — find it in play."
            tcol = dcol = _MYST_DIM
        else:
            title, desc = "???", "Hidden — discover it in play."
            tcol = dcol = _DIM

        ts = self._scaled_text(title, 17 * S, tcol)
        surf.blit(ts, (tx, int(ry + 9 * S)))

        # Description (wrapped to one or two short lines).
        self._blit_wrapped(surf, desc, tx, int(ry + 30 * S),
                           int((W - _PAD_X) * S - tx - 8 * S), 12 * S, dcol)

        # Earned star only — locked rows show no progress (it would betray the
        # hidden goal). The star carries "earned", recoloured per wall.
        if unlocked:
            star_cx = int((W - _PAD_X) * S - 12 * S)
            star_cy = int(ry + 16 * S)
            self._draw_star(surf, star_cx, star_cy, 8 * S, acc, acc_deep)

    def _gilded_count(self, txt, size, hi=_GOLD_PALE, lo=_GOLD_DEEP):
        """The header counter rendered with a vertical gradient fill (pale crest
        → deep base) so it matches the gilded title rather than sitting as a flat
        orphaned label. ``hi``/``lo`` recolour it per active wall."""
        base = _font(size, True).render(txt, True, hi)
        w, h = base.get_size()
        grad = pygame.Surface((w, h), pygame.SRCALPHA)
        for yy in range(h):
            t = yy / max(1, h - 1)
            grad.fill(lerp_color(hi, lo, t), (0, yy, w, 1))
        grad.blit(base, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        out = pygame.Surface((w + 2, h + 2), pygame.SRCALPHA)
        sh = _font(size, True).render(txt, True, (20, 12, 4))
        out.blit(sh, (1, 1))
        out.blit(grad, (0, 0))
        return out

    def _draw_star(self, surf, cx, cy, rad, fill=_GOLD_BRIGHT, edge=_GOLD_DEEP):
        """Procedural five-point "earned" star — the bundled bold font has no
        U+2605 glyph, so the badge family's star is drawn instead of typeset."""
        pts = []
        for i in range(10):
            ang = -math.pi / 2 + i * math.pi / 5
            rr = rad if i % 2 == 0 else rad * 0.42
            pts.append((cx + math.cos(ang) * rr, cy + math.sin(ang) * rr))
        pygame.draw.polygon(surf, fill, [(int(x), int(y)) for x, y in pts])
        pygame.draw.polygon(surf, edge, [(int(x), int(y)) for x, y in pts], max(1, _S))

    def _blit_wrapped(self, surf, text, x, y, maxw, size, color):
        f = _font(int(size), True)
        words = text.split(" ")
        lines, cur = [], ""
        for w in words:
            trial = (cur + " " + w).strip()
            if f.size(trial)[0] <= maxw or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        for i, ln in enumerate(lines[:2]):
            img = f.render(ln, True, color)
            surf.blit(img, (x, y + i * int(size * 1.15)))

    # ── tab bar ──────────────────────────────────────────────────────────
    def _draw_tab_bar(self, surf) -> None:
        y = _HEADER_H
        band = pygame.Surface((W, _TAB_H), pygame.SRCALPHA)
        band.fill((*_NIGHT_DEEP, 235))
        surf.blit(band, (0, y))
        pad, gap = 10, 6
        seg_w = (W - pad * 2 - gap) // 2
        self.tab_fame_rect = pygame.Rect(pad, y + 4, seg_w, _TAB_H - 8)
        self.tab_shame_rect = pygame.Rect(pad + seg_w + gap, y + 4, seg_w, _TAB_H - 8)
        self._draw_tab(surf, self.tab_fame_rect, "HALL OF FAME",
                       self._tab == "fame", _GOLD_BRIGHT, _GOLD_DEEP)
        self._draw_tab(surf, self.tab_shame_rect, "HALL OF SHAME",
                       self._tab == "shame", _BRONZE, _BRONZE_DEEP)
        pygame.draw.line(surf, (*_GOLD_BRIGHT, 110),
                         (0, y + _TAB_H - 1), (W, y + _TAB_H - 1), 1)

    def _draw_tab(self, surf, rect, label, active, accent, accent_lo) -> None:
        """One segment. Active = filled accent→deep pill with near-black text;
        inactive = hollow navy with a dimmed accent label, so the toggle reads
        from value alone (not hue) for colourblind/low-vision safety."""
        rad = rect.h // 2
        if active:
            grad = pygame.Surface(rect.size, pygame.SRCALPHA)
            for yy in range(rect.h):
                t = yy / max(1, rect.h - 1)
                grad.fill((*lerp_color(accent, accent_lo, t), 255), (0, yy, rect.w, 1))
            m = pygame.Surface(rect.size, pygame.SRCALPHA)
            pygame.draw.rect(m, (255, 255, 255, 255), (0, 0, rect.w, rect.h), border_radius=rad)
            grad.blit(m, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            surf.blit(grad, rect.topleft)
            pygame.draw.rect(surf, accent, rect, width=2, border_radius=rad)
            txt = _font(13, True).render(label, True, _NIGHT_DEEP)
            surf.blit(txt, txt.get_rect(center=rect.center))
        else:
            pygame.draw.rect(surf, (*_PANEL_DARK, 235), rect, border_radius=rad)
            pygame.draw.rect(surf, (*accent, 140), rect, width=1, border_radius=rad)
            txt = _font(13, True).render(label, True, accent)
            txt.set_alpha(150)
            surf.blit(txt, txt.get_rect(center=rect.center))

    # ── per-frame render ─────────────────────────────────────────────────
    def render(self, surf, dt: float, store: dict) -> None:
        self._t += dt
        self._ensure_content(store)

        # Background — the menu's night world: deep gradient + twinkle starfield
        # + a dim mountain silhouette low down, so the wall sits in the same place.
        for yy in range(H):
            t = yy / (H - 1)
            pygame.draw.line(surf, lerp_color(_NIGHT_DEEP, (14, 8, 36), t), (0, yy), (W, yy))
        _draw_overlay_stars(surf, _star_field(), self._t)
        _draw_mountain_silhouette(surf, alpha=130)

        top, bot = self._viewport()
        view_h = bot - top

        # Blit the pre-scaled 1x content surface — no per-frame scaling.
        src_y = int(self.scroll_offset)
        src_h = min(view_h, self._content.get_height() - src_y)
        if src_h > 0:
            surf.blit(self._content, (0, top), (0, src_y, W, src_h))

        # Recessed metallic scrollbar — a sunken channel + a brighter rounded
        # thumb with a gold rim, the energy-bar language. Self-documents the
        # drag, so no "drag to scroll" caption is needed.
        if self.max_scroll > 0:
            is_shame = self._tab == "shame"
            acc = _BRONZE if is_shame else _GOLD_BRIGHT
            acc_lo = _BRONZE_DEEP if is_shame else _GOLD_DEEP
            tw = 6
            tx = W - tw - 3
            pygame.draw.rect(surf, (4, 2, 14), (tx, top, tw, view_h), border_radius=tw // 2)
            pygame.draw.line(surf, (2, 1, 8), (tx + 1, top + 1), (tx + 1, bot - 1), 1)
            thumb_h = max(30, int(view_h * view_h / self._content_h))
            travel = view_h - thumb_h
            thumb_y = top + int((self.scroll_offset / self.max_scroll) * travel)
            thumb = pygame.Surface((tw, thumb_h), pygame.SRCALPHA)
            for yy in range(thumb_h):
                t = yy / max(1, thumb_h - 1)
                thumb.fill((*lerp_color(acc, acc_lo, t), 255), (0, yy, tw, 1))
            tm = pygame.Surface((tw, thumb_h), pygame.SRCALPHA)
            pygame.draw.rect(tm, (255, 255, 255, 255), (0, 0, tw, thumb_h), border_radius=tw // 2)
            thumb.blit(tm, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            surf.blit(thumb, (tx, thumb_y))
            pygame.draw.line(surf, _GOLD_PALE, (tx + 2, thumb_y + 4),
                             (tx + 2, thumb_y + thumb_h // 3), 1)

        # Header bar (over the scrolling content) — title = the ACTIVE wall, with
        # its counter + progress bar recoloured (gold for Fame, bronze for Shame).
        order, by_cat, total, _tone = self._roster()
        got = sum(1 for cat in order for a in by_cat[cat]
                  if ach.is_unlocked(store, a.id))
        is_shame = self._tab == "shame"
        accent = _BRONZE if is_shame else _GOLD_BRIGHT
        accent_lo = _BRONZE_DEEP if is_shame else _GOLD_DEEP
        accent_hi = (228, 182, 130) if is_shame else _GOLD_PALE

        hdr = pygame.Surface((W, _HEADER_H), pygame.SRCALPHA)
        hdr.fill((*_NIGHT_DEEP, 235))
        surf.blit(hdr, (0, 0))
        _outlined_text(surf, "HALL OF SHAME" if is_shame else "HALL OF FAME",
                       (W // 2, 16), size=22, px=2, shadow_offset=(2, 3))
        uw = 152
        ux = W // 2 - uw // 2
        pygame.draw.line(surf, accent, (ux, 30), (ux + uw, 30), 2)

        cnt = self._gilded_count(f"{got} / {total}", 14, accent_hi, accent_lo)
        surf.blit(cnt, (W - cnt.get_width() - 8, 6))

        # Global progress bar for the active wall.
        gbh = 6
        gbx = _RULE_INSET
        gbw = W - _RULE_INSET * 2
        gby = _HEADER_H - 11
        frac = (got / total) if total else 0.0
        pygame.draw.rect(surf, (8, 5, 24), (gbx, gby, gbw, gbh), border_radius=gbh // 2)
        pygame.draw.line(surf, (4, 2, 14), (gbx + 1, gby + 1), (gbx + gbw - 2, gby + 1), 1)
        fw = int(gbw * max(0.0, min(1.0, frac)))
        if fw > 0:
            bar = pygame.Surface((fw, gbh), pygame.SRCALPHA)
            for xx in range(fw):
                t = xx / max(1, fw - 1)
                bar.fill(lerp_color(accent_lo, accent, t), (xx, 0, 1, gbh))
            surf.blit(bar, (gbx, gby))
        pygame.draw.rect(surf, (*accent, 110), (gbx, gby, gbw, gbh),
                         width=1, border_radius=gbh // 2)

        # FAME | SHAME segmented toggle, just below the header.
        self._draw_tab_bar(surf)

        # Footer — a grounded band carrying the real MENU button (a secondary
        # navy+gold pill, matching the run-summary MAIN MENU). A full-width gold
        # hairline divides the list from the footer so the button sits in its
        # own band; the recessed scrollbar already signals "drag to scroll".
        fy = H - _FOOTER_H
        ftr = pygame.Surface((W, _FOOTER_H), pygame.SRCALPHA)
        ftr.fill((*_NIGHT_DEEP, 236))
        surf.blit(ftr, (0, fy))
        pygame.draw.line(surf, (*_GOLD_BRIGHT, 120), (0, fy), (W, fy), 1)
        self.menu_btn_rect = _outline_pill_btn(
            surf, (W // 2, fy + _FOOTER_H // 2), "MENU",
            size=15, min_width=150)
