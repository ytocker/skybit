"""SCRATCH mock — polished WALL OF FAME / WALL OF SHAME achievements screen.

Nothing here is imported by the game. It prototypes the high-fidelity restyle
of the two-tab achievements screen for art-director review, so the recipe can
be baked into game/achievements_screen.py later. The whole 360x640 frame is
drawn at 3x and smoothscaled down so text, borders, badges and gradients land
razor sharp at 1x.

Outputs:
  docs/wall_polish/shame_tab.png   polished Shame tab (360x640)
  docs/wall_polish/fame_tab.png    polished Fame tab  (360x640)

Treatments prototyped here (all reuse the real game helpers so the mock looks
like the shipped menus):
  - rows as MINTED CARDS: _volume_panel emboss (gradient body, 2px gold border,
    top sheen line, multi-step drop shadow) + earned gold stripe & star.
  - recessed METALLIC SCROLLBAR: a sunken channel + a brighter rounded thumb.
  - a real bottom MENU button via hud._outline_pill_btn (navy + gold rim).
  - menu-matching BACKGROUND: night gradient + seeded twinkle starfield
    (_draw_overlay_stars) + a dim mountain silhouette low down.
"""
from __future__ import annotations

import math
import os
import random
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from game.draw import lerp_color
from game.hud import (
    _font, _outlined_text, _outline_pill_btn,
    _draw_overlay_stars, _draw_mountain_silhouette,
    _GOLD_BRIGHT, _GOLD_PALE, _GOLD_DEEP, _GOLD_MUTED,
    _PANEL_DARK, _PANEL_LIGHTER, _NIGHT_DEEP, _RED_OUTLINE,
)
from game import achievements as ach
from game.achievement_icons import draw_badge

W, H = 360, 640
S = 3  # whole-frame supersample for crisp 1x output

# Shame accents mirror Fame's gold with a bronze family.
_BRONZE      = (198, 132, 66)
_BRONZE_HI   = (228, 168, 104)
_BRONZE_DEEP = (110, 64, 28)

_WHITE   = (245, 246, 255)
_DIM     = (150, 150, 172)
_SHAME_DIM = (180, 150, 120)

_HEADER_H = 56
_TAB_H    = 32
_FOOTER_H = 56          # taller: holds a real pill + a micro-cue above it
_CAT_H    = 30
_ROW_H    = 60          # a touch taller so the card emboss + sheen can breathe
_ROW_GAP  = 7
_PAD_X    = 12
_BADGE    = 44


# ── Minted card row (the _volume_panel emboss applied to a list row) ──────────
def _draw_row(surf, y, icon_key, title, desc, unlocked, hidden, tone):
    """One row drawn as a minted stat card: gradient body, 2px accent border,
    a top sheen highlight line, an inner bottom shadow line, and a soft 3-step
    drop shadow — the premium emboss of the menu's _volume_panel. Earned rows
    keep the bright accent left-stripe + star; locked rows are masked '???'."""
    shame = (tone == "tarnished")
    accent      = _BRONZE if shame else _GOLD_BRIGHT
    accent_pale = _BRONZE_HI if shame else _GOLD_PALE
    accent_deep = _BRONZE_DEEP if shame else _GOLD_DEEP

    rx, rw, rh = _PAD_X * S, (W - _PAD_X * 2) * S, _ROW_H * S
    ry = y * S
    rad = 13 * S

    # Multi-step drop shadow — softer + more diffuse than a flat shade, so the
    # card sits with real volume against the night background.
    sh = pygame.Surface((rw + 8 * S, rh + 8 * S), pygame.SRCALPHA)
    for k in range(4):
        a = 86 - k * 18
        pygame.draw.rect(sh, (0, 0, 0, a),
                         (k * S, k * 2 * S, rw + 8 * S - k * 2 * S,
                          rh + 8 * S - k * 2 * S), border_radius=rad)
    surf.blit(sh, (rx - 4 * S, ry + 2 * S))

    # Gradient body — lighter crest, dark base. Locked rows are dimmer + cooler.
    body_top = _PANEL_LIGHTER if unlocked else (18, 14, 40)
    body_bot = _PANEL_DARK if unlocked else (10, 7, 26)
    panel = pygame.Surface((rw, rh), pygame.SRCALPHA)
    for yy in range(rh):
        t = yy / max(1, rh - 1)
        pygame.draw.line(panel, lerp_color(body_top, body_bot, t), (0, yy), (rw, yy))
    mask = pygame.Surface((rw, rh), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, rw, rh), border_radius=rad)
    panel.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

    # 2px accent border (earned) / dim navy hairline (locked).
    border = (*accent, 200) if unlocked else (90, 86, 120, 150)
    bw = max(2, 2 * S) if unlocked else max(1, S)
    pygame.draw.rect(panel, border, (0, 0, rw, rh), width=bw, border_radius=rad)

    # Inner top sheen + inner bottom shadow — the _volume_panel emboss that
    # turns a flat ramp into a struck-metal plate.
    sheen = accent_pale if unlocked else (200, 200, 220)
    pygame.draw.line(panel, (*sheen, 150 if unlocked else 60),
                     (12 * S, 3 * S), (rw - 12 * S, 3 * S), max(1, S))
    pygame.draw.line(panel, (0, 0, 0, 90),
                     (12 * S, rh - 4 * S), (rw - 12 * S, rh - 4 * S), max(1, S))

    # Earned accent stripe down the left edge — the quick "this one's yours" read.
    if unlocked:
        sw, shh = max(3, 4 * S), rh - 10 * S
        stripe = pygame.Surface((sw, shh), pygame.SRCALPHA)
        for yy in range(shh):
            t = yy / max(1, shh - 1)
            stripe.fill(lerp_color(accent_pale, accent_deep, t), (0, yy, sw, 1))
        sm = pygame.Surface((sw, shh), pygame.SRCALPHA)
        pygame.draw.rect(sm, (255, 255, 255, 255), sm.get_rect(),
                         border_radius=max(1, 2 * S))
        stripe.blit(sm, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        panel.blit(stripe, (4 * S, 5 * S))
    surf.blit(panel, (rx, ry))

    # Badge — gold on Fame, tarnished on Shame; masked when locked.
    badge_rect = pygame.Rect(int(rx + 9 * S), int(ry + (rh - _BADGE * S) // 2),
                             _BADGE * S, _BADGE * S)
    draw_badge(surf, icon_key, badge_rect, unlocked, hidden, tone)

    # Text block.
    tx = int(rx + (9 + _BADGE + 11) * S)
    if unlocked:
        tcol, dcol = accent_pale, _WHITE
    elif shame:
        title, desc = "???", "Disgrace yourself in play to reveal."
        tcol = dcol = _SHAME_DIM
    elif hidden:
        title, desc = "???", "A rare secret — find it in play."
        tcol = dcol = (176, 154, 200)
    else:
        title, desc = "???", "Hidden — discover it in play."
        tcol = dcol = _DIM

    ts = _font(17 * S, True).render(title, True, tcol)
    surf.blit(ts, (tx, int(ry + 10 * S)))
    _blit_wrapped(surf, desc, tx, int(ry + 32 * S),
                  int((W - _PAD_X) * S - tx - 10 * S), 12 * S, dcol)

    # Earned star, top-right.
    if unlocked:
        _draw_star(surf, int((W - _PAD_X) * S - 13 * S), int(ry + 17 * S),
                   8 * S, accent, accent_deep)


def _blit_wrapped(surf, text, x, y, maxw, size, color):
    f = _font(int(size), True)
    words, lines, cur = text.split(" "), [], ""
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
        surf.blit(f.render(ln, True, color), (x, y + i * int(size * 1.18)))


def _draw_star(surf, cx, cy, rad, fill, deep):
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = rad if i % 2 == 0 else rad * 0.42
        pts.append((cx + math.cos(ang) * rr, cy + math.sin(ang) * rr))
    pygame.draw.polygon(surf, fill, [(int(x), int(y)) for x, y in pts])
    pygame.draw.polygon(surf, deep, [(int(x), int(y)) for x, y in pts], max(1, S))


# ── Category header ──────────────────────────────────────────────────────────
def _draw_cat_header(surf, y, label, got, total):
    complete = got >= total and total > 0
    head_col = _GOLD_PALE if complete else _GOLD_BRIGHT
    py = int((y + _CAT_H * 0.5) * S)
    d = int(4 * S)
    pip = [(_PAD_X * S, py), (_PAD_X * S + d, py - d),
           (_PAD_X * S + 2 * d, py), (_PAD_X * S + d, py + d)]
    pygame.draw.polygon(surf, head_col, pip)
    pygame.draw.polygon(surf, _GOLD_DEEP, pip, max(1, S))

    lbl = _font(15 * S, True).render(label.upper(), True, head_col)
    lx = _PAD_X * S + 3 * d
    surf.blit(lbl, (lx, int((y + 5) * S)))

    cnt = _font(13 * S, True).render(f"{got}/{total}", True, _GOLD_DEEP)
    cnt_x = int((W - _PAD_X) * S - cnt.get_width())
    surf.blit(cnt, (cnt_x, int((y + 6) * S)))

    ry = int((y + _CAT_H - 6) * S)
    rail_l = lx + lbl.get_width() + 6 * S
    rail_r = cnt_x - 6 * S
    if rail_r > rail_l:
        rail = pygame.Surface((rail_r - rail_l, max(2, 2 * S)), pygame.SRCALPHA)
        for xx in range(rail.get_width()):
            fade = 1.0 - xx / max(1, rail.get_width())
            rail.fill((*_GOLD_BRIGHT, int(160 * fade)), (xx, 0, 1, max(2, 2 * S)))
        surf.blit(rail, (rail_l, ry))


# ── Tab bar (segmented FAME | SHAME toggle) ──────────────────────────────────
def _draw_tab_bar(surf, active):
    y = _HEADER_H * S
    band = pygame.Surface((W * S, _TAB_H * S), pygame.SRCALPHA)
    band.fill((*_NIGHT_DEEP, 235))
    surf.blit(band, (0, y))
    pad, gap = 10 * S, 6 * S
    seg_w = (W * S - pad * 2 - gap) // 2
    fame = pygame.Rect(pad, y + 4 * S, seg_w, _TAB_H * S - 8 * S)
    shame = pygame.Rect(pad + seg_w + gap, y + 4 * S, seg_w, _TAB_H * S - 8 * S)
    _draw_tab(surf, fame, "WALL OF FAME", active == "fame", _GOLD_BRIGHT, _GOLD_DEEP)
    _draw_tab(surf, shame, "WALL OF SHAME", active == "shame", _BRONZE, _BRONZE_DEEP)
    pygame.draw.line(surf, (*_GOLD_BRIGHT, 110),
                     (0, y + _TAB_H * S - S), (W * S, y + _TAB_H * S - S), max(1, S))


def _draw_tab(surf, rect, label, active, accent, accent_lo):
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
        # Crisp rim + a top inner sheen line so the active pill reads as struck.
        pygame.draw.rect(surf, accent, rect, width=max(2, 2 * S), border_radius=rad)
        pygame.draw.line(surf, (255, 245, 220, 150),
                         (rect.x + rad, rect.y + 3 * S),
                         (rect.right - rad, rect.y + 3 * S), max(1, S))
        txt = _font(13 * S, True).render(label, True, _NIGHT_DEEP)
        surf.blit(txt, txt.get_rect(center=rect.center))
    else:
        pygame.draw.rect(surf, (*_PANEL_DARK, 235), rect, border_radius=rad)
        pygame.draw.rect(surf, (*accent, 140), rect, width=max(1, S), border_radius=rad)
        txt = _font(13 * S, True).render(label, True, accent)
        txt.set_alpha(150)
        surf.blit(txt, txt.get_rect(center=rect.center))


# ── Recessed metallic scrollbar ──────────────────────────────────────────────
def _draw_scrollbar(surf, top, view_h, content_h, frac, accent, accent_lo):
    """A sunken channel + a brighter rounded thumb — energy-bar language, not a
    hairline. The channel is darker than the background with a faint inner top
    shadow (recessed), and the thumb is a vertical accent gradient with a bright
    sheen pip near its crest so it reads as a polished slider."""
    bw = 7 * S
    track_x = W * S - bw - 3 * S
    ty, th = top * S, view_h * S
    # Sunken channel.
    pygame.draw.rect(surf, (4, 2, 14), (track_x, ty, bw, th), border_radius=bw // 2)
    pygame.draw.line(surf, (0, 0, 0, 120), (track_x + S, ty + S),
                     (track_x + bw - S, ty + S), max(1, S))
    pygame.draw.rect(surf, (*accent, 70), (track_x, ty, bw, th),
                     width=max(1, S), border_radius=bw // 2)

    thumb_h = max(34 * S, int(th * th / (content_h * S)))
    travel = th - thumb_h
    thumb_y = ty + int(frac * travel)
    thumb = pygame.Surface((bw, thumb_h), pygame.SRCALPHA)
    for yy in range(thumb_h):
        t = yy / max(1, thumb_h - 1)
        thumb.fill(lerp_color(accent, accent_lo, t), (0, yy, bw, 1))
    tm = pygame.Surface((bw, thumb_h), pygame.SRCALPHA)
    pygame.draw.rect(tm, (255, 255, 255, 255), tm.get_rect(), border_radius=bw // 2)
    thumb.blit(tm, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(thumb, (track_x, thumb_y))
    # Bright sheen pip near the crest.
    pygame.draw.line(thumb if False else surf, (255, 245, 220, 180),
                     (track_x + 2 * S, thumb_y + 5 * S),
                     (track_x + bw - 2 * S, thumb_y + 5 * S), max(1, S))


# ── Full-frame render ────────────────────────────────────────────────────────
def render_tab(tab):
    is_shame = (tab == "shame")
    tone = "tarnished" if is_shame else "gold"
    accent     = _BRONZE if is_shame else _GOLD_BRIGHT
    accent_lo  = _BRONZE_DEEP if is_shame else _GOLD_DEEP
    accent_hi  = (228, 182, 130) if is_shame else _GOLD_PALE

    if is_shame:
        order, by_cat, total = ach.SHAME_CATEGORY_ORDER, ach.BY_CAT_SHAME, len(ach.SHAME_ACHIEVEMENTS)
        title = "WALL OF SHAME"
    else:
        order, by_cat, total = ach.CATEGORY_ORDER, ach.BY_CAT, len(ach.ACHIEVEMENTS)
        title = "WALL OF FAME"

    # A demo store: mark the first ~3 of the displayed category as earned so the
    # mock shows both revealed cards and masked rows.
    store = {"unlocked": {}}

    big = pygame.Surface((W * S, H * S))

    # ── Background — night gradient + starfield + dim mountains (menu world) ──
    for yy in range(H * S):
        t = yy / (H * S - 1)
        pygame.draw.line(big, lerp_color(_NIGHT_DEEP, (14, 8, 36), t),
                         (0, yy), (W * S, yy))
    rng = random.Random(42)
    stars = [(rng.randint(8, W - 8) * S, rng.randint(8, H - 180) * S,
              rng.choice((1, 1, 1, 2)) * S, rng.uniform(0, 6.28)) for _ in range(46)]
    _draw_overlay_stars(big, stars, 1.7)
    mtn = pygame.Surface((W * S, H * S), pygame.SRCALPHA)
    _mtn_silhouette(mtn)
    big.blit(mtn, (0, 0))

    # ── Scrolling content region (cards) ──
    top = _HEADER_H + _TAB_H
    bot = H - _FOOTER_H
    view_h = bot - top

    # Choose a representative category + build rows: 3-4 revealed + 2 masked.
    cat = order[0]
    cat_rows = list(by_cat[cat])
    revealed_n = min(4, len(cat_rows))
    y = top + 4
    _draw_cat_header(big, y, cat, revealed_n, len(cat_rows))
    y += _CAT_H
    shown = 0
    for i, a in enumerate(cat_rows):
        unlocked = i < revealed_n
        _draw_row(big, y, a.icon_key, a.title, a.desc, unlocked, a.hidden, tone)
        y += _ROW_H + _ROW_GAP
        shown += 1
        if shown >= revealed_n + 2:
            break

    # A long-list scroll position so the scrollbar thumb sits mid-track.
    content_h = (_CAT_H + len(cat_rows) * (_ROW_H + _ROW_GAP)) * 2
    _draw_scrollbar(big, top, view_h, content_h, 0.32, accent, accent_lo)

    # ── Header bar (over the content) ──
    hdr = pygame.Surface((W * S, _HEADER_H * S), pygame.SRCALPHA)
    hdr.fill((*_NIGHT_DEEP, 235))
    big.blit(hdr, (0, 0))
    _outlined_text(big, title, (W // 2 * S, 16 * S), size=22 * S, px=2 * S,
                   shadow_offset=(2 * S, 3 * S))
    uw = 152 * S
    ux = W // 2 * S - uw // 2
    pygame.draw.line(big, accent, (ux, 30 * S), (ux + uw, 30 * S), max(2, 2 * S))

    cnt = _gilded_count(f"{revealed_n} / {total}", 14 * S, accent_hi, accent_lo)
    big.blit(cnt, (W * S - cnt.get_width() - 8 * S, 6 * S))

    # Global progress bar for the active wall — same recessed/energy language.
    gbh = 6 * S
    gbx = 40 * S
    gbw = W * S - 40 * S * 2
    gby = _HEADER_H * S - 11 * S
    frac = revealed_n / total if total else 0.0
    pygame.draw.rect(big, (8, 5, 24), (gbx, gby, gbw, gbh), border_radius=gbh // 2)
    pygame.draw.line(big, (4, 2, 14), (gbx + S, gby + S), (gbx + gbw - 2 * S, gby + S), max(1, S))
    fw = int(gbw * max(0.0, min(1.0, frac)))
    if fw > 0:
        bar = pygame.Surface((fw, gbh), pygame.SRCALPHA)
        for xx in range(fw):
            t = xx / max(1, fw - 1)
            bar.fill(lerp_color(accent_lo, accent, t), (xx, 0, 1, gbh))
        big.blit(bar, (gbx, gby))
    pygame.draw.rect(big, (*accent, 110), (gbx, gby, gbw, gbh),
                     width=max(1, S), border_radius=gbh // 2)

    # ── Tab bar ──
    _draw_tab_bar(big, tab)

    # ── Footer — a real MENU pill + a quiet DRAG TO SCROLL micro-cue above ──
    ftr = pygame.Surface((W * S, _FOOTER_H * S), pygame.SRCALPHA)
    ftr.fill((*_NIGHT_DEEP, 235))
    pygame.draw.line(ftr, (*_GOLD_BRIGHT, 100), (0, 0), (W * S, 0), max(1, S))
    big.blit(ftr, (0, (H - _FOOTER_H) * S))

    cue = _font(11 * S, True).render("DRAG TO SCROLL", True, _GOLD_MUTED)
    cue.set_alpha(150)
    big.blit(cue, cue.get_rect(center=(W // 2 * S, (H - _FOOTER_H + 13) * S)))

    _outline_pill_btn(big, (W // 2 * S, (H - 20) * S), "MENU",
                      size=15 * S, min_width=132 * S, pad_x=26 * S, pad_y=13 * S)

    return pygame.transform.smoothscale(big, (W, H))


def _mtn_silhouette(mtn):
    """Dim mountain silhouettes low down — the menu's shapes, supersampled."""
    far = [(0, H), (0, 490), (60, 420), (120, 450), (200, 375), (280, 430),
           (360, 360), (W, 400), (W, H)]
    near = [(0, H), (0, 530), (80, 505), (160, 520), (240, 490), (320, 510),
            (W, 495), (W, H)]
    pygame.draw.polygon(mtn, (14, 26, 12, 150),
                        [(x * S, y * S) for x, y in far])
    pygame.draw.polygon(mtn, (10, 18, 8, 175),
                        [(x * S, y * S) for x, y in near])


def _gilded_count(txt, size, hi, lo):
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


def main():
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "docs", "wall_polish")
    os.makedirs(out_dir, exist_ok=True)
    for tab, name in (("shame", "shame_tab.png"), ("fame", "fame_tab.png")):
        path = os.path.join(out_dir, name)
        pygame.image.save(render_tab(tab), path)
        print("wrote", path)


if __name__ == "__main__":
    main()
