"""Wardrobe screen — the player's owned-items case, one tab of the shared
PROFILE parent (see game/profile_screen.py). Ported from the foamcase
design-exploration mockup into a real interactive scene: same look, real
data (game/store_data.py, game/store_catalog.py) instead of a hand-authored
mock save, real tap-to-equip instead of static demo frames.

Scope simplifications vs. the design exploration (kept intentionally small
for this first real pass — see round-20 plan notes):
  - No "new/unseen" badges and no first-open coaching hint — neither has a
    persisted flag anywhere in store_data.py yet; inventing one as a side
    effect of a navigation task was out of scope.
  - Tapping an unowned (void) tile is a no-op — "Wardrobe is what is
    owned"; no deep-link into the coin store from here.
  - No sticky/pinned category header while scrolling (the real
    achievements screen doesn't bother with this either — its category
    headers just scroll with the list, which is the same simpler
    behavior used here).
  - No equip-confirmation burst/celebration animation, no "released"
    latch flourish on the item that got swapped out — the persistent
    checkmark chip on the equipped tile already carries that state.
  - Pip renders on a single static frame (no idle animation cycle).

Geometry (CASE/lid/cutout/rail) is unchanged from the round-17/19 wardrobe
mockup, which already assumes 72px of shared chrome above it (PROFILE
title + WARDROBE/ACHIEVEMENTS pill, drawn by ProfileScene) — this scene
only ever renders itself starting at that fixed y.
"""
from __future__ import annotations

import math
import random

import pygame

from game.config import W, H
from game.draw import lerp_color
from game.hud import (
    _font, _GOLD_BRIGHT, _GOLD_PALE, _NIGHT_DEEP,
    _draw_overlay_stars, _draw_mountain_silhouette,
)
from game import parrot, store_catalog, store_cards, store_data
from game.store_hub import GOLD_A_STOPS

# Content starts right after ProfileScene's shared header (40px) + view-pill
# tab bar (32px) — this scene never draws either of those itself.
CONTENT_TOP = 72

S = 2  # supersample factor for the case artwork only (chrome text stays 1x)

# Seeded twinkle field so this screen sits in the same night world as the
# menu/achievements wall (same technique as achievements_screen.py's own).
_STARS = []


def _star_field():
    if not _STARS:
        rng = random.Random(42)
        for _ in range(46):
            _STARS.append((rng.randint(6, W - 6), rng.randint(8, H - 150),
                           rng.choice((1, 1, 1, 2)), rng.uniform(0, 6.28)))
    return _STARS


def p(v):
    return int(round(v * S))


def R(x, y, w, h):
    return pygame.Rect(p(x), p(y), p(w), p(h))


def font(sz):
    return _font(max(6, p(sz)), True)


def gold_at(t):
    t = max(0.0, min(1.0, t))
    for i in range(len(GOLD_A_STOPS) - 1):
        t0, c0 = GOLD_A_STOPS[i]
        t1, c1 = GOLD_A_STOPS[i + 1]
        if t <= t1:
            return lerp_color(c0, c1, (t - t0) / max(1e-6, t1 - t0))
    return GOLD_A_STOPS[-1][1]


# ── palette (ported unchanged from the design exploration) ──────────────────
SHELL_HI = (35, 33, 68)
SHELL_LO = (18, 12, 34)
FOAM_HI = (35, 32, 56)
FOAM = (28, 24, 45)
FOAM_LO = (20, 15, 31)
CHANNEL = (9, 7, 17)
POCKET_HI = (24, 19, 39)
POCKET_LO = (14, 9, 24)
POCKET_EQ_HI = (78, 68, 86)
POCKET_EQ_LO = (63, 52, 68)
CAVITY_HI = (22, 17, 36)
CAVITY_LO = (5, 2, 9)
POCKET_EQ_RIM = (255, 198, 118)


def vgrad(size, top, bot, radius=0, gamma=1.0):
    w, h = size
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(h):
        t = (y / max(1, h - 1)) ** gamma
        s.fill((*lerp_color(top, bot, t), 255), (0, y, w, 1))
    if radius > 0:
        m = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(m, (255, 255, 255, 255), (0, 0, w, h), border_radius=radius)
        s.blit(m, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return s


def speckle(surf, rect, n, seed, lo=8, hi=20):
    rnd = random.Random(seed)
    n = max(1, int(n * S * S / 9))
    grain = pygame.Surface(rect.size, pygame.SRCALPHA)
    for _ in range(n):
        x = rnd.randrange(rect.w)
        y = rnd.randrange(rect.h)
        r = rnd.randint(max(1, p(0.5)), max(2, p(1.4)))
        a = rnd.randint(lo, hi)
        c = (170, 182, 214, a) if rnd.random() < 0.55 else (0, 0, 0, a + 10)
        pygame.draw.circle(grain, c, (x, y), r)
    surf.blit(grain, rect.topleft)


def gold_rect(surf, rect, radius, width, t0=0.0, t1=1.0):
    strip = pygame.Surface(rect.size, pygame.SRCALPHA)
    for y in range(rect.h):
        c = gold_at(t0 + (t1 - t0) * y / max(1, rect.h - 1))
        strip.fill((*c, 255), (0, y, rect.w, 1))
    m = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(m, (255, 255, 255, 255), (0, 0, rect.w, rect.h),
                     width=width, border_radius=radius)
    strip.blit(m, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(strip, rect.topleft)


def inner_shadow(surf, rect, radius, depth, alpha=150):
    sh = pygame.Surface(rect.size, pygame.SRCALPHA)
    for i in range(depth):
        a = int(alpha * (1 - i / depth) ** 1.5)
        pygame.draw.rect(sh, (0, 0, 0, a), (i, i, rect.w - i * 2, rect.h - i * 2),
                         width=1, border_radius=max(1, radius - i))
    surf.blit(sh, rect.topleft)


def drop(surf, rect, radius, blur, alpha, dy):
    sh = pygame.Surface((rect.w + blur * 2, rect.h + blur * 2), pygame.SRCALPHA)
    for i in range(blur, 0, -1):
        a = int(alpha * (1 - (i - 1) / blur) ** 1.7)
        pygame.draw.rect(sh, (0, 0, 0, a),
                         (blur - i, blur - i, rect.w + i * 2, rect.h + i * 2),
                         border_radius=radius + i)
    surf.blit(sh, (rect.x - blur, rect.y - blur + dy))


# ── die-cut void (unowned tile silhouette) ───────────────────────────────────
def silhouette(img):
    sil = img.copy()
    sil.fill((255, 255, 255, 255), special_flags=pygame.BLEND_RGB_MAX)
    for _ in range(3):
        sil.blit(sil.copy(), (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    return sil


def dilate(sil, d):
    w, h = sil.get_size()
    out = pygame.Surface((w + d * 2, h + d * 2), pygame.SRCALPHA)
    for dx in range(-d, d + 1):
        for dy in range(-d, d + 1):
            if dx * dx + dy * dy <= d * d:
                out.blit(sil, (d + dx, d + dy), special_flags=pygame.BLEND_RGBA_MAX)
    return out


def masked(mask, fill_surf):
    out = fill_surf.copy()
    out.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return out


def die_cut(dst, sid, cx, cy, box):
    sil = silhouette(store_cards.thumb(sid, box))
    wall_w = max(2, p(2.6))
    hole = dilate(sil, max(1, p(1.6)))
    wall = dilate(sil, max(1, p(1.6)) + int(wall_w))
    ww, wh = wall.get_size()
    hw, hh = hole.get_size()

    ao = dilate(wall, max(1, p(2)))
    ao_s = masked(ao, pygame.Surface(ao.get_size(), pygame.SRCALPHA))
    ao_s.fill((0, 0, 0, 90), special_flags=pygame.BLEND_RGBA_MAX)
    ao_s.blit(ao, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    dst.blit(ao_s, (cx - ao.get_width() // 2, cy - ao.get_height() // 2 + p(1)))

    chamfer = masked(wall, vgrad((ww, wh), (96, 108, 148), (7, 8, 16), gamma=0.72))
    dst.blit(chamfer, (cx - ww // 2, cy - wh // 2))

    cav = masked(hole, vgrad((hw, hh), CAVITY_HI, CAVITY_LO, gamma=1.5))
    dst.blit(cav, (cx - hw // 2, cy - hh // 2))

    rim = hole.copy()
    down = pygame.Surface((hw, hh), pygame.SRCALPHA)
    down.blit(hole, (0, max(1, p(1.6))))
    rim.blit(down, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
    rim_s = pygame.Surface((hw, hh), pygame.SRCALPHA)
    rim_s.fill((150, 164, 200, 120))
    rim_s.blit(rim, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    dst.blit(rim_s, (cx - hw // 2, cy - hh // 2))


def dim_thumb(img, mult=0.60):
    """An un-equipped owned thumb reads dimmer than the equipped one — a
    flat multiply (no numpy dependency; the game ships no numpy import
    anywhere else) rather than the design exploration's true per-pixel
    desaturation. Good enough to separate the two states at a glance."""
    out = img.copy()
    tint = pygame.Surface(img.get_size(), pygame.SRCALPHA)
    v = max(0, min(255, int(255 * mult)))
    tint.fill((v, v, v, 255))
    out.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return out


# ── tiles ─────────────────────────────────────────────────────────────────────
def pocket(surf, rect, equipped=False, brighten=0):
    rad = p(9)
    top = POCKET_EQ_HI if equipped else POCKET_HI
    bot = POCKET_EQ_LO if equipped else POCKET_LO
    if brighten:
        top = tuple(min(255, c + brighten) for c in top)
        bot = tuple(min(255, c + brighten) for c in bot)
    body = vgrad(rect.size, top, bot, radius=rad, gamma=1.2)
    surf.blit(body, rect.topleft)
    inner_shadow(surf, rect, rad, max(2, p(2.5)), 130 if not equipped else 90)
    ao = pygame.Surface(rect.size, pygame.SRCALPHA)
    for i in range(max(2, p(5))):
        a = int(56 * (1 - i / max(2, p(5))) ** 1.6)
        pygame.draw.rect(ao, (0, 0, 0, a),
                         (i, i, rect.w - i * 2, rect.h - i * 2),
                         width=1, border_radius=max(1, rad - i))
    surf.blit(ao, rect.topleft)
    if equipped:
        pygame.draw.rect(surf, (*POCKET_EQ_RIM, 200), rect, width=max(1, p(1.4)),
                         border_radius=rad)
    else:
        pygame.draw.rect(surf, (52, 60, 90, 130), rect, width=max(1, p(0.7)),
                         border_radius=rad)


def latch_chip(surf, x, y, flip_x, flip_y):
    """Gold corner latch: the fastener holding the equipped item in its pocket."""
    s = p(11)
    ch = pygame.Surface((s, s), pygame.SRCALPHA)
    pts = [(0, 0), (s, 0), (s, p(3.4)), (p(3.4), p(3.4)), (p(3.4), s), (0, s)]
    grad = vgrad((s, s), gold_at(0.02), gold_at(0.85))
    m = pygame.Surface((s, s), pygame.SRCALPHA)
    pygame.draw.polygon(m, (255, 255, 255, 255), pts)
    grad.blit(m, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    ch.blit(grad, (0, 0))
    pygame.draw.line(ch, (*_GOLD_PALE, 200), (p(1), p(1)),
                     (s - p(1), p(1)), max(1, p(0.7)))
    sc = (p(1.9), p(1.9))
    pygame.draw.circle(ch, (58, 40, 8), sc, max(1, p(1.2)))
    pygame.draw.circle(ch, (232, 200, 132), sc, max(1, p(0.8)))
    pygame.draw.line(ch, (58, 40, 8), (sc[0] - p(0.7), sc[1]), (sc[0] + p(0.7), sc[1]),
                     max(1, p(0.4)))
    if flip_x or flip_y:
        ch = pygame.transform.flip(ch, flip_x, flip_y)
    surf.blit(ch, (x, y))


def check_chip(surf, cx, cy, r):
    """Persistent equipped confirmation — a glance away and back still finds it."""
    pygame.draw.circle(surf, (22, 14, 2), (cx, cy + max(1, p(0.6))), r + max(1, p(0.8)))
    disc = vgrad((r * 2, r * 2), gold_at(0.0), gold_at(0.7))
    mk = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
    pygame.draw.circle(mk, (255, 255, 255, 255), (r, r), r)
    disc.blit(mk, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(disc, (cx - r, cy - r))
    pygame.draw.circle(surf, (255, 246, 216, 200), (cx, cy), r, max(1, p(0.5)))
    pygame.draw.lines(surf, (34, 20, 2), False,
                      [(cx - r * 0.46, cy + r * 0.02),
                       (cx - r * 0.10, cy + r * 0.40),
                       (cx + r * 0.52, cy - r * 0.42)], max(2, p(1.5)))


def name_strip(surf, rect, txt, equipped):
    hstrip = p(14)
    r = pygame.Rect(rect.x + p(4), rect.bottom - hstrip - p(3),
                    rect.w - p(8), hstrip)
    if equipped:
        g = vgrad(r.size, gold_at(0.05), gold_at(0.72), radius=max(1, p(2)))
        surf.blit(g, r.topleft)
        t = font(10).render(txt, True, (22, 14, 2))
    else:
        pygame.draw.rect(surf, (10, 12, 24), r, border_radius=max(1, p(2)))
        t = font(10).render(txt, True, (214, 220, 236))
    surf.blit(t, (r.centerx - t.get_width() // 2, r.centery - t.get_height() // 2))


def tile_owned(surf, rect, sid, label, equipped, box_px=34):
    pocket(surf, rect, equipped)
    box = p(box_px)
    cx, cy = rect.centerx, rect.centery - p(5)
    th = store_cards.thumb(sid, box)
    if equipped:
        gl = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
        for i in range(6):
            a = int(30 * (1 - i / 6))
            pygame.draw.rect(gl, (*_GOLD_BRIGHT, a),
                             (i, i, rect.w - i * 2, rect.h - i * 2),
                             width=1, border_radius=p(9) - i)
        surf.blit(gl, rect.topleft)
    else:
        th = dim_thumb(th)
    csh = pygame.Surface((p(46), p(12)), pygame.SRCALPHA)
    for i in range(8):
        a = int(64 * (1 - i / 8))
        pygame.draw.ellipse(csh, (0, 0, 0, a),
                            (i * p(2), i * p(0.6), p(46) - i * p(4), p(12) - i * p(1.2)))
    surf.blit(csh, (cx - p(23), cy + p(13)))
    surf.blit(th, th.get_rect(center=(cx, cy)))
    name_strip(surf, rect, label, equipped)
    if equipped:
        gold_rect(surf, rect, p(9), max(1, p(1)), 0.0, 0.9)
        latch_chip(surf, rect.x + p(2), rect.y + p(2), False, False)
        latch_chip(surf, rect.right - p(13), rect.bottom - p(13), True, True)
        check_chip(surf, rect.right - p(9), rect.y + p(9), max(3, p(6)))


def tile_void(surf, rect, sid, stub, box_px=34):
    die_cut(surf, sid, rect.centerx, rect.centery - p(6), p(box_px))
    st = font(10).render("?", True, (206, 214, 232))
    surf.blit(st, (rect.centerx - st.get_width() // 2, rect.bottom - p(16)))


# ── catalogue truth ───────────────────────────────────────────────────────────
# Open stalls only — matching the store's own OPEN_GROUPS convention (more
# categories arrive later; scale-back is a follow-up, not a v1 requirement).
CATS = (("COSTUME", "costume"), ("PARROT", "parrot"), ("PARCELS", "parcels"))
G_COLS = 4
G_TILE_W, G_TILE_H = 76, 62
G_PITCH_X = 82
HEADER_ROW, PAD_BOTTOM, GAP = 14, 4, 5


def _slot_for(group: str) -> str:
    return "parcel" if group == "parcels" else "skin"


def _owned_ids_for(group: str) -> set:
    owned = store_data.owned_ids()
    return {sid for sid in store_catalog.ids_of_group(group) if sid in owned}


def _equipped_sid_for(group: str) -> "str | None":
    return store_data.equipped(_slot_for(group))


def _total_count(group: str) -> int:
    ids = store_catalog.ids_of_group(group)
    return len(ids) + (1 if group in ("parrot", "parcels") else 0)


def _owned_count(group: str) -> int:
    return len(_owned_ids_for(group))


GRAND_TOTAL = sum(_total_count(g) for _, g in CATS)


def _rail_icon_sid(group: str) -> "str | None":
    """The item shown on the category rail button: the equipped item if it
    belongs to this group, else the first owned item, else the first
    catalog item (so a never-opened category still shows something)."""
    ids = store_catalog.ids_of_group(group)
    if not ids:
        return None
    eq = _equipped_sid_for(group)
    if eq in ids:
        return eq
    owned = store_data.owned_ids()
    for sid in ids:
        if sid in owned:
            return sid
    return ids[0]


def category_rows(group: str, label: str):
    """The tray's row-blocks for ONE category, from the real catalog and
    real save data."""
    ids = store_catalog.ids_of_group(group)
    owned_ids = _owned_ids_for(group)
    equipped_sid = _equipped_sid_for(group)
    total = _total_count(group)
    got = len(owned_ids)
    rows = []
    for start in range(0, len(ids), G_COLS):
        chunk = ids[start:start + G_COLS]
        tiles = []
        for i, sid in enumerate(chunk):
            idx = start + i
            if sid in owned_ids:
                nm = store_catalog.name(sid).upper()[:8]
                tiles.append({"kind": "own", "sid": sid, "label": nm,
                             "equipped": sid == equipped_sid})
            else:
                tiles.append({"kind": "void", "sid": sid,
                             "label": f"{label[0]}-{idx + 1:02d}"})
        rows.append({"tiles": tiles})
    if rows:
        rows[0].update(title=label, got=got, total=total, is_first=True)
    for r in rows[1:]:
        r["is_first"] = False
    return rows


def draw_rail_column(surf, col, sel_idx):
    """Buttons are milled tool blanks with real depth — a selected blank
    sits PROUD of the foam (bevel + gold face + cast shadow); unselected
    ones are pressed flush."""
    pitch = p(32)
    row_h = p(26)
    for i, (label, group) in enumerate(CATS):
        r = pygame.Rect(col.x, col.y + i * pitch, col.w, row_h)
        selected = (i == sel_idx)
        rad = max(1, p(4))
        icon_sid = _rail_icon_sid(group)
        if selected:
            drop(surf, r, rad, max(2, p(3)), 140, p(3))
            face = pygame.Rect(r.x, r.y - p(2), r.w, r.h)
            surf.blit(vgrad(face.size, gold_at(0.08), gold_at(0.7), radius=rad), face.topleft)
            pygame.draw.line(surf, (*_GOLD_PALE, 160), (face.x + p(3), face.y + p(1.6)),
                             (face.right - p(3), face.y + p(1.6)), max(1, p(1)))
            pygame.draw.rect(surf, gold_at(0.92), face, width=max(1, p(1.2)), border_radius=rad)
            txt_col = (24, 16, 2)
            icon_cx, icon_cy = face.x + p(14), face.centery
            if icon_sid:
                store_cards.blit_thumb(surf, icon_sid, icon_cx, icon_cy, p(15))
            lbl = font(8).render(label, True, txt_col)
            surf.blit(lbl, (face.x + p(26), face.centery - lbl.get_height() // 2))
        else:
            surf.blit(vgrad(r.size, CAVITY_HI, CAVITY_LO, radius=rad), r.topleft)
            inner_shadow(surf, r, rad, max(2, p(3)), 150)
            pygame.draw.rect(surf, (52, 60, 90, 110), r, width=max(1, p(0.7)), border_radius=rad)
            txt_col = (140, 148, 172)
            icon_cx, icon_cy = r.x + p(13), r.centery
            if icon_sid:
                die_cut(surf, icon_sid, icon_cx, icon_cy, p(11))
            lbl = font(8).render(label, True, txt_col)
            surf.blit(lbl, (r.x + p(24), r.centery - lbl.get_height() // 2))


# Locked geometry (round 17/19) — CASE/lid start 72px down (ProfileScene's
# shared header + view-pill), same bottom edge as the original design.
CASE = R(9, 80, 342, 498)
LID = R(15, 84, 330, 110)
_COL_W = 96
_GAP = 6
_CUTOUT_W = 318 - _COL_W - _GAP
CUTOUT = R(21, 90, _CUTOUT_W, 96)
_INNER = CASE.inflate(-p(6), -p(6))
_HINGE = pygame.Rect(_INNER.x + p(4), LID.bottom + p(1), _INNER.w - p(8), p(9))
_TRAY = pygame.Rect(_INNER.x, _HINGE.bottom, _INNER.w, _INNER.bottom - _HINGE.bottom)
TRAY_TOP_LOGICAL = 208.0  # logical-px y (unscaled) the tray content starts at


class WardrobeScene:
    _TAP_SLOP = 8
    WHEEL_STEP = 56
    _DECAY_K = 5.0
    _STOP_VEL = 5.0
    _MAX_VEL = 4000.0

    def __init__(self):
        self.sel_group = CATS[0][1]
        self.scroll_offset = 0.0
        self.max_scroll = 0.0
        self._t = 0.0
        self._drag_active = False
        self._drag_last = 0
        self._drag_moved = 0
        self._scroll_vel = 0.0
        self._drag_y_now = 0
        self._drag_y_prev = 0

        self._chrome: "pygame.Surface | None" = None
        self._chrome_key = None
        self._tray_content: "pygame.Surface | None" = None
        self._tray_content_h = 0
        self._tray_key = None
        self._tile_layout: list = []  # (content_rect, tile) in tray-content space

        self.rail_rects: list = []  # (Rect, group) in screen space
        self._flash_text = ""
        self._flash_t = 0.0

        # Logical viewport of the scrollable tray, in screen space.
        view_y = int(TRAY_TOP_LOGICAL) - 1
        self.view = pygame.Rect(_TRAY.x // S, view_y, _TRAY.w // S,
                                (_TRAY.bottom // S) - view_y)

    # ── real-data signature helpers (cache keys) ─────────────────────────
    def _owned_signature(self, group):
        return tuple(sorted(_owned_ids_for(group)))

    def _rail_signature(self):
        return tuple(_rail_icon_sid(g) for _, g in CATS)

    # ── pointer / scroll (mirrors AchievementsScene's vertical drag+fling) ──
    def pointer_down(self, y: int) -> None:
        self._drag_active = True
        self._drag_last = y
        self._drag_moved = 0
        self._scroll_vel = 0.0
        self._drag_y_now = y
        self._drag_y_prev = y

    def pointer_move(self, y: int) -> None:
        if not self._drag_active:
            return
        dy = y - self._drag_last
        self._drag_moved += abs(dy)
        self.scroll_by(-dy)
        self._drag_last = y
        self._drag_y_now = y

    def pointer_up(self) -> bool:
        was_drag = self._drag_active
        self._drag_active = False
        return (not was_drag) or self._drag_moved < self._TAP_SLOP

    def scroll_by(self, dpx: float) -> None:
        self.scroll_offset = max(0.0, min(self.max_scroll, self.scroll_offset + dpx))

    def update(self, dt: float) -> None:
        self._t += dt
        if self._flash_t > 0:
            self._flash_t = max(0.0, self._flash_t - dt)
        if self._drag_active:
            dy = self._drag_y_now - self._drag_y_prev
            if dt > 0:
                self._scroll_vel = max(-self._MAX_VEL, min(self._MAX_VEL, -dy / dt))
            self._drag_y_prev = self._drag_y_now
            return
        if abs(self._scroll_vel) < self._STOP_VEL:
            self._scroll_vel = 0.0
            return
        self.scroll_by(self._scroll_vel * dt)
        decay = math.exp(-self._DECAY_K * dt)
        self._scroll_vel *= decay

    # ── taps ───────────────────────────────────────────────────────────
    def handle_tap(self, pos) -> None:
        for rect, group in self.rail_rects:
            if rect.collidepoint(pos):
                if group != self.sel_group:
                    self.sel_group = group
                    self.scroll_offset = 0.0
                return
        if not self.view.collidepoint(pos):
            return
        rel_y = pos[1] - self.view.y + int(self.scroll_offset)
        rel_x = pos[0] - self.view.x
        # _tile_layout rects are in tray-content space (relative to the top
        # of the unscrolled tall content, x relative to view.x) — see
        # _ensure_tray — so hit-test directly against (rel_x, rel_y).
        for rect, tile in self._tile_layout:
            if rect.collidepoint(rel_x, rel_y):
                self._tap_tile(tile)
                return

    def _tap_tile(self, tile: dict) -> None:
        if tile["kind"] != "own":
            return
        sid = tile["sid"]
        slot = store_data.slot_of(sid)
        if store_data.equipped(slot) == sid:
            return
        if store_data.equip(sid):
            self._flash_text = store_catalog.name(sid).upper() + " EQUIPPED"
            self._flash_t = 1.4

    # ── caches ───────────────────────────────────────────────────────────
    def _ensure_chrome(self) -> None:
        key = (self.sel_group, self._rail_signature(), _equipped_sid_for("costume"),
              _equipped_sid_for("parcels"))
        if self._chrome is not None and key == self._chrome_key:
            return
        self._chrome_key = key

        surf = pygame.Surface((CASE.w + p(20), CASE.h + p(20)), pygame.SRCALPHA)
        origin = (CASE.x - p(10), CASE.y - p(10))

        def off(rect):
            return pygame.Rect(rect.x - origin[0], rect.y - origin[1], rect.w, rect.h)

        case_r = off(CASE)
        drop(surf, case_r, p(7), max(3, p(9)), 120, p(4))
        surf.blit(vgrad(case_r.size, SHELL_HI, SHELL_LO, radius=p(7)), case_r.topleft)
        speckle(surf, case_r, 2600, 7, 4, 10)
        gold_rect(surf, case_r, p(7), max(1, p(1.1)), 0.5, 1.0)
        inner_r = case_r.inflate(-p(6), -p(6))
        pygame.draw.rect(surf, CHANNEL, inner_r, border_radius=p(4))
        gold_rect(surf, inner_r.inflate(p(2), p(2)), p(5), max(1, p(0.7)), 0.55, 0.95)

        lid_r = off(LID)
        LID_HI, LID_LO = (36, 31, 65), (21, 16, 41)
        lid_panel = vgrad(lid_r.size, LID_HI, LID_LO, radius=p(5), gamma=0.9)
        sheen = pygame.Surface(lid_r.size, pygame.SRCALPHA)
        for x in range(lid_r.w):
            t = x / lid_r.w
            a = int(46 * math.exp(-((t - 0.34) ** 2) / 0.045))
            if a:
                pygame.draw.line(sheen, (176, 198, 245, a), (x, 0), (x - lid_r.h // 3, lid_r.h))
        lid_panel.blit(sheen, (0, 0))
        mask = pygame.Surface(lid_r.size, pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, lid_r.w, lid_r.h), border_radius=p(5))
        lid_panel.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        surf.blit(lid_panel, lid_r.topleft)
        inner_shadow(surf, lid_r, p(5), max(2, p(4)), 150)
        gold_rect(surf, lid_r, p(5), max(1, p(0.8)), 0.5, 0.85)

        def bracket(x, y, fx, fy):
            s = p(26)
            b = pygame.Surface((s, s), pygame.SRCALPHA)
            pts = [(0, 0), (s, 0), (s, p(7)), (p(7), p(7)), (p(7), s), (0, s)]
            g = vgrad((s, s), (64, 61, 104), (27, 21, 48))
            mk = pygame.Surface((s, s), pygame.SRCALPHA)
            pygame.draw.polygon(mk, (255, 255, 255, 255), pts)
            g.blit(mk, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            b.blit(g, (0, 0))
            pygame.draw.lines(b, (140, 156, 200, 150), False,
                              [(p(1), s), (p(1), p(1)), (s, p(1))], max(1, p(0.7)))
            for rx, ry in ((p(3.6), p(3.6)), (p(3.6), p(15)), (p(15), p(3.6))):
                pygame.draw.circle(b, (10, 12, 24), (int(rx), int(ry)), max(2, p(2.1)))
                pygame.draw.circle(b, (96, 108, 148), (int(rx), int(ry)), max(1, p(1.6)))
                pygame.draw.circle(b, (168, 184, 224), (int(rx - p(0.5)), int(ry - p(0.5))),
                                   max(1, p(0.8)))
            if fx or fy:
                b = pygame.transform.flip(b, fx, fy)
            surf.blit(b, (x, y))

        bracket(lid_r.x + p(2), lid_r.y + p(2), False, False)
        bracket(lid_r.right - p(28), lid_r.y + p(2), True, False)
        bracket(lid_r.x + p(2), lid_r.bottom - p(28), False, True)
        bracket(lid_r.right - p(28), lid_r.bottom - p(28), True, True)

        cutout_r = off(CUTOUT)
        cav = vgrad(cutout_r.size, CAVITY_HI, CAVITY_LO, radius=p(10), gamma=1.4)
        surf.blit(cav, cutout_r.topleft)
        inner_shadow(surf, cutout_r, p(10), max(2, p(4)), 150)
        pygame.draw.rect(surf, (150, 164, 200, 110), cutout_r, width=max(1, p(1)),
                         border_radius=p(10))

        equipped_skin = store_data.equipped("skin")
        pip_src = parrot.get_skin_frame(equipped_skin, 1, 0.0)
        pip_src = pip_src.subsurface(pip_src.get_bounding_rect()).copy()
        pw, ph = pip_src.get_size()
        pip_k = 3.4 / 3.0 * S
        pip = pygame.transform.scale(pip_src, (int(pw * pip_k), int(ph * pip_k)))
        pip_c = (cutout_r.centerx, cutout_r.centery + p(1))
        pr0 = pip.get_rect(center=pip_c)

        old_clip = surf.get_clip()
        surf.set_clip(cutout_r)
        halo_r = p(78)
        halo = pygame.Surface((halo_r * 2, halo_r * 2), pygame.SRCALPHA)
        for i in range(22):
            t = i / 21
            rr = int(halo_r * (1 - t * 0.72))
            pygame.draw.circle(halo, (70, 78, 122, 9), (halo_r, halo_r), rr)
        surf.blit(halo, (pip_c[0] - halo_r, pip_c[1] - halo_r))
        ring_r = p(72)
        for k in range(48):
            a0 = k * math.tau / 48
            a1 = a0 + math.tau / 72
            pygame.draw.line(surf, (146, 158, 196, 46),
                             (pip_c[0] + ring_r * math.cos(a0), pip_c[1] + ring_r * math.sin(a0)),
                             (pip_c[0] + ring_r * math.cos(a1), pip_c[1] + ring_r * math.sin(a1)),
                             max(1, p(0.7)))
        sh = pygame.Surface((p(96), p(26)), pygame.SRCALPHA)
        for i in range(10):
            a = int(78 * (1 - i / 10))
            pygame.draw.ellipse(sh, (0, 0, 0, a),
                                (i * p(4), i * p(1.1), p(96) - i * p(8), p(26) - i * p(2.2)))
        surf.blit(sh, (pip_c[0] - p(48), pr0.bottom - p(14)))
        surf.blit(pip, pr0)
        surf.set_clip(old_clip)

        if pr0.right > cutout_r.right:
            slice_w = min(pr0.right - cutout_r.right, pr0.w)
            slice_img = pip.subsurface((pr0.w - slice_w, 0, slice_w, pr0.h)).copy()
            ssh = pygame.Surface((slice_w + p(6), p(10)), pygame.SRCALPHA)
            pygame.draw.ellipse(ssh, (0, 0, 0, 90), ssh.get_rect())
            surf.blit(ssh, (cutout_r.right - p(3), pr0.centery - p(2)))
            surf.blit(slice_img, (cutout_r.right, pr0.y))

        sel_idx = next((i for i, (_, g) in enumerate(CATS) if g == self.sel_group), 0)
        col_x = cutout_r.right + p(_GAP)
        column = pygame.Rect(col_x, cutout_r.y, p(_COL_W), cutout_r.h)
        draw_rail_column(surf, column, sel_idx)
        self.rail_rects = [
            (pygame.Rect((column.x + origin[0]) // S, (column.y + i * p(32) + origin[1]) // S,
                        column.w // S, p(26) // S), g)
            for i, (_, g) in enumerate(CATS)
        ]

        hinge_r = off(_HINGE)
        surf.blit(vgrad(hinge_r.size, (50, 45, 76), (19, 12, 34)), hinge_r.topleft)
        kn = p(13)
        for i in range(hinge_r.w // kn + 1):
            kx = hinge_r.x + i * kn
            kw = min(kn - p(1.6), hinge_r.right - kx)
            if kw <= 0:
                break
            top = (i % 2 == 0)
            kr = pygame.Rect(kx, hinge_r.y + (0 if top else p(3)), int(kw), hinge_r.h - p(3))
            surf.blit(vgrad(kr.size, (84, 82, 130) if top else (58, 55, 96),
                            (25, 19, 44), radius=max(1, p(2))), kr.topleft)
            pygame.draw.rect(surf, (8, 10, 20), kr, width=max(1, p(0.5)), border_radius=max(1, p(2)))
        pygame.draw.line(surf, (150, 166, 208, 160), (hinge_r.x, hinge_r.centery),
                         (hinge_r.right, hinge_r.centery), max(1, p(0.6)))
        pygame.draw.line(surf, (4, 5, 12), (hinge_r.x, hinge_r.bottom),
                         (hinge_r.right, hinge_r.bottom), max(1, p(0.8)))

        tray_r = off(_TRAY)
        surf.blit(vgrad(tray_r.size, FOAM_LO, (15, 9, 22)), tray_r.topleft)

        # Transparent everywhere except the case — the sky background is
        # drawn fresh each frame in render() (so its starfield can twinkle),
        # not baked into this cache.
        out = pygame.Surface((W, H), pygame.SRCALPHA)
        down = pygame.transform.smoothscale(
            surf, (surf.get_width() // S, surf.get_height() // S))
        out.blit(down, (origin[0] // S, origin[1] // S))
        self._chrome = out

    def _ensure_tray(self) -> None:
        key = (self.sel_group, self._owned_signature(self.sel_group),
              _equipped_sid_for(self.sel_group))
        if self._tray_content is not None and key == self._tray_key:
            return
        self._tray_key = key

        label = next(lbl for lbl, g in CATS if g == self.sel_group)
        rows = category_rows(self.sel_group, label)

        h = 4
        for r in rows:
            bh = (HEADER_ROW if r.get("is_first") else 0) + G_TILE_H + PAD_BOTTOM
            h += bh + GAP
        h = max(h, self.view.h)
        self._tray_content_h = h

        surf = pygame.Surface((self.view.w * S, h * S), pygame.SRCALPHA)
        grid_x0 = p(6)
        by = 4
        layout = []
        for gi, g in enumerate(rows):
            is_first = g.get("is_first", False)
            bh = (HEADER_ROW if is_first else 0) + G_TILE_H + PAD_BOTTOM
            blk = pygame.Rect(grid_x0 - p(5), p(by), self.view.w * S - p(2), p(bh))
            pygame.draw.rect(surf, CHANNEL, blk.inflate(p(3), p(3)), border_radius=p(5))
            face = vgrad(blk.size, FOAM_HI, FOAM, radius=p(4), gamma=1.1)
            surf.blit(face, blk.topleft)
            speckle(surf, blk, 900, 100 + gi)
            pygame.draw.line(surf, (18, 20, 34, 190), (blk.x + p(4), blk.y + p(0.6)),
                             (blk.right - p(4), blk.y + p(0.6)), max(1, p(0.7)))
            pygame.draw.rect(surf, (5, 6, 13, 200), blk, width=max(1, p(0.7)), border_radius=p(4))

            if is_first:
                title_t = font(11).render(f"{g['title']} · {g['got']}/{g['total']}",
                                          True, _GOLD_PALE)
                surf.blit(title_t, (blk.x + p(6), blk.y + p(2)))

            ty = blk.y + (p(HEADER_ROW) if is_first else 0)
            for ti, t in enumerate(g["tiles"]):
                tr = pygame.Rect(grid_x0 + ti * p(G_PITCH_X), ty, p(G_TILE_W), p(G_TILE_H))
                if t["kind"] == "own":
                    tile_owned(surf, tr, t["sid"], t["label"], t["equipped"])
                else:
                    tile_void(surf, tr, t["sid"], t["label"])
                # Store the tile's hit rect in tray-content LOGICAL (1x)
                # space (relative to the top of the unscrolled tall content).
                layout.append((pygame.Rect(tr.x // S, tr.y // S,
                                          tr.w // S, tr.h // S), t))
            by += bh + GAP

        self._tile_layout = layout
        self._tray_content = pygame.transform.smoothscale(surf, (self.view.w, h))
        self.max_scroll = max(0.0, self._tray_content_h - self.view.h)
        self.scroll_offset = min(self.scroll_offset, self.max_scroll)

    # ── render ───────────────────────────────────────────────────────────
    def render(self, surf: pygame.Surface) -> None:
        self._ensure_chrome()
        self._ensure_tray()

        # Night-sky background, same as the menu/achievements world — drawn
        # fresh each frame (not cached) so the starfield can twinkle.
        for yy in range(H):
            t = yy / (H - 1)
            pygame.draw.line(surf, lerp_color(_NIGHT_DEEP, (14, 8, 36), t), (0, yy), (W, yy))
        _draw_overlay_stars(surf, _star_field(), self._t)
        _draw_mountain_silhouette(surf, alpha=130)

        surf.blit(self._chrome, (0, 0))

        src_y = int(self.scroll_offset)
        src_h = min(self.view.h, self._tray_content.get_height() - src_y)
        if src_h > 0:
            surf.blit(self._tray_content, (self.view.x, self.view.y), (0, src_y, self.view.w, src_h))

        if self.max_scroll > 0:
            tw = 3
            tx = self.view.right - tw - 2
            pygame.draw.rect(surf, (0, 0, 0, 150), (tx, self.view.y, tw, self.view.h),
                             border_radius=tw // 2)
            frac = min(1.0, self.view.h / self._tray_content_h)
            th_h = max(14, int(self.view.h * frac))
            travel = self.view.h - th_h
            ty = self.view.y + int((self.scroll_offset / self.max_scroll) * travel)
            pygame.draw.rect(surf, (*_GOLD_BRIGHT, 190), (tx, ty, tw, th_h),
                             border_radius=tw // 2)

        if self._flash_t > 0:
            a = min(255, int(255 * min(1.0, self._flash_t / 0.3)))
            txt = _font(13, True).render(self._flash_text, True, _GOLD_PALE)
            txt.set_alpha(a)
            surf.blit(txt, txt.get_rect(center=(W // 2, self.view.y - 10)))
