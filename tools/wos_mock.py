"""SCRATCH mock — Wall of Shame two-tab achievements screen.

Renders ONE design mock for art-director review. Nothing here is imported by
the game; it prototypes the tarnished anti-trophy palette + crack/drip recipe
and the FAME|SHAME segmented tab bar so they can be baked into the real
_build later. Outputs:
  docs/wall_of_shame/round_1.png     full Shame tab (360x640)
  docs/wall_of_shame/tarnish_strip.png  gold vs tarnished badge at ~64px

The tarnished badge reuses the real medallion construction primitives
(_draw_laurel/_draw_rim/_draw_step/_draw_face/_stamp_glyph) so the silhouette
stays identical to the gold "Courier's Commendation" — only the palette is
swapped to pewter and a crack polyline + dripping-bronze accent are overlaid.
"""
from __future__ import annotations

import math
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from game.draw import lerp_color, blit_glow
from game.hud import (
    _font, _outlined_text,
    _GOLD_BRIGHT, _GOLD_PALE, _GOLD_DEEP,
    _PANEL_DARK, _PANEL_LIGHTER, _NIGHT_DEEP,
)
from game import achievement_icons as AI

W, H = 360, 640

# ── Tarnished anti-trophy palette ─────────────────────────────────────────────
# The gold medal corroded: a cool pewter rim (no warm cast — read as dead
# metal, not sleeping gold), a grimy slate enamel well, and a single oxidised
# BRONZE accent that the crack + drip wear so the badge reads "verdigris ruin"
# rather than the neutral dormant-pewter lock. Bronze is the only saturated
# tone, mirroring how gold is the only saturated tone on the Fame side.
_T_RIM_HI   = (158, 162, 170)   # specular crest of the corroded rim
_T_RIM_MID  = (118, 120, 128)   # body pewter
_T_RIM_LO   = ( 64,  66,  74)   # shadowed underside of the bevel
_T_SPEC     = (196, 200, 208)   # weak upper-left specular (metal gone matte)
_T_FACE_TOP = ( 46,  48,  60)   # grimy slate enamel, lit top
_T_FACE_BOT = ( 22,  23,  32)   # enamel shadowed base
_T_RECESS   = ( 12,  12,  20)
_T_STEP_HI  = (150, 152, 160)
_T_STEP_LO  = ( 70,  72,  80)
_T_GLY      = (176, 178, 188)   # engraved glyph highlight (cold)
_T_GLY_SH   = ( 18,  18,  26)
_T_GLY_SHEEN = (206, 208, 216)
_T_LAUREL_L = (132, 134, 142)
_T_LAUREL_D = ( 66,  68,  76)

# Oxidised bronze — the corrosion accent for crack lips + the drip.
_BRONZE_HI  = (176, 112,  54)   # lit bronze edge
_BRONZE_MID = (132,  78,  36)   # drip body
_BRONZE_LO  = ( 82,  46,  20)   # drip shadow / crack depth
_VERDIGRIS  = ( 96, 132, 110)   # faint blue-green oxide bloom in the crack

_SS = AI._SS


def _tarnished_egg_glyph(surf, cx, cy, r, col):
    """A cracked egg — the GOOSE-EGG (zero) glyph: an upright ovoid split by a
    jagged seam, the lower-left shell tipped open. Lives only in the mock; if
    baked it would join achievement_icons._GLYPHS as 'egg'."""
    # Egg body: an ellipse taller than wide, fat at the base.
    ew, eh = int(r * 0.86), int(r * 1.18)
    rect = pygame.Rect(cx - ew // 2, cy - int(eh * 0.46), ew, eh)
    pygame.draw.ellipse(surf, col, rect)
    # Jagged shell crack across the middle — a zig-zag seam in the shadow tone.
    seam = []
    for i, (fx, fy) in enumerate([(-0.46, 0.04), (-0.22, -0.10), (0.0, 0.06),
                                  (0.22, -0.08), (0.46, 0.06)]):
        seam.append((cx + fx * ew, cy + fy * eh))
    pygame.draw.lines(surf, AI._GLYPH_SH, False,
                      [(int(x), int(y)) for x, y in seam], max(2, r // 9))


def _build_tarnished(icon_key, size, locked=False):
    """Prototype the tarnished badge by re-running the real medallion build with
    a pewter palette, then overlaying the crack polyline + bronze drip.

    locked=True yields the dormant '?' anti-trophy (still corroded, masked).
    """
    S = _SS
    px = size * S
    surf = pygame.Surface((px, px), pygame.SRCALPHA)
    cx = cy = px // 2
    R = int(px * 0.46)

    # A weak cold halo (vs gold's warm glow) so a revealed shame row still
    # pops off the panel without ever looking earned.
    if not locked:
        blit_glow(surf, cx, cy, int(R * 1.06), (120, 124, 140), 55)
    else:
        blit_glow(surf, cx, cy, int(R * 1.02), (90, 94, 108), 40)

    AI._draw_laurel(surf, cx, cy, R, _T_LAUREL_L, _T_LAUREL_D)
    AI._draw_rim(surf, cx, cy, R, _T_RIM_HI, _T_RIM_MID, _T_RIM_LO, _T_SPEC)
    fr = int(R * 0.70)
    AI._draw_step(surf, cx, cy, fr + max(2, R // 16), _T_STEP_HI, _T_STEP_LO)
    AI._draw_face(surf, cx, cy, fr, _T_FACE_TOP, _T_FACE_BOT, _T_RECESS)

    # Glyph (or masked '?').
    gr = int(R * 0.56)
    if locked:
        f = AI._glyph_font(int(R * 1.05))
        off = max(1, R // 18)
        for dx, dy, c in ((off, off, _T_GLY_SH), (0, 0, _T_GLY)):
            q = f.render("?", True, c)
            surf.blit(q, q.get_rect(center=(cx + dx, cy + dy)))
    elif icon_key == "egg":
        # Engrave the bespoke egg with the same dark-then-light emboss pass.
        off = max(1, gr // 18)
        _tarnished_egg_glyph(surf, cx + off, cy + off, gr, _T_GLY_SH)
        _tarnished_egg_glyph(surf, cx, cy, gr, _T_GLY)
    else:
        AI._stamp_glyph(surf, icon_key, cx, cy, gr, _T_GLY, _T_GLY_SH, _T_GLY_SHEEN)

    # ── Crack polyline across the disc ────────────────────────────────────────
    # A jagged fracture running upper-left to lower-right across the whole
    # medallion. Drawn three-pass: a wide dark depth stroke (the gouge), a
    # thin bronze-oxide lip catching the upper-left light, and a few verdigris
    # flecks where the oxide blooms. Fixed seed-free zig-zag so it always lands
    # the same — a baked version would store these fractions verbatim.
    crack = [
        (-0.74, -0.42), (-0.40, -0.18), (-0.30, -0.30), (-0.06, 0.02),
        (0.04, -0.12), (0.30, 0.22), (0.42, 0.10), (0.72, 0.46),
    ]
    cpts = [(int(cx + fx * R), int(cy + fy * R)) for fx, fy in crack]
    # gouge depth, then a cold pewter shoulder, then the lit bronze lip — three
    # passes give the fracture real relief instead of a flat scribble.
    pygame.draw.lines(surf, (8, 8, 14), False, cpts, max(4, R // 9))     # deep gouge
    pygame.draw.lines(surf, _BRONZE_LO, False, cpts, max(3, R // 13))    # oxide depth
    pygame.draw.lines(surf, _BRONZE_HI, False, cpts, max(1, R // 24))    # lit lip
    for (fx, fy) in (crack[2], crack[4], crack[6]):
        pygame.draw.circle(surf, _VERDIGRIS,
                           (int(cx + fx * R), int(cy + fy * R)), max(1, R // 20))

    # ── Dripping-bronze accent ────────────────────────────────────────────────
    # A teardrop of corrosion oozing off the rim near the crack's exit, lower
    # right — the "this trophy is leaking" cue. A tapered stem + a swollen
    # bead, lit upper-left so it reads as wet metal.
    dx = cx + int(R * 0.62)
    dy_top = cy + int(R * 0.42)
    bead_y = cy + int(R * 0.92)
    bead_r = max(3, int(R * 0.13))
    pygame.draw.line(surf, _BRONZE_MID, (dx, dy_top), (dx, bead_y),
                     max(3, R // 12))
    pygame.draw.line(surf, _BRONZE_LO, (dx + max(1, R // 28), dy_top),
                     (dx + max(1, R // 28), bead_y), max(1, R // 26))
    pygame.draw.circle(surf, _BRONZE_MID, (dx, bead_y), bead_r)
    pygame.draw.circle(surf, _BRONZE_LO, (dx, bead_y), bead_r, max(1, R // 30))
    pygame.draw.circle(surf, _BRONZE_HI,
                       (dx - bead_r // 3, bead_y - bead_r // 3), max(1, bead_r // 3))

    return pygame.transform.smoothscale(surf, (size, size))


# ── Tab bar (FAME | SHAME), modelled on hud._draw_lb_tabs ─────────────────────
def draw_tab_bar(surf, rect, active_idx):
    """Segmented two-tab control. Active half = filled gold gradient with dark
    text; inactive half = hollow navy with gold text. Each half carries an era
    coin: FAME a bright-gold disc, SHAME a cracked pewter-bronze disc — so the
    tabs read apart by value + the crack motif, not colour alone."""
    x, y, w, h = rect
    rad = h // 2
    track = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(track, (*_PANEL_DARK, 235), (0, 0, w, h), border_radius=rad)
    surf.blit(track, (x, y))

    half = w // 2
    f = _font(15, True)
    coin_r = 7
    tabs = (("WALL OF FAME", _GOLD_BRIGHT, False),
            ("WALL OF SHAME", _T_RIM_MID, True))
    for idx, (label, coin_col, cracked) in enumerate(tabs):
        hx = x + (0 if idx == 0 else half)
        hw = half if idx == 0 else (w - half)
        selected = (idx == active_idx)
        if selected:
            fill = pygame.Surface((hw, h), pygame.SRCALPHA)
            for yy in range(h):
                fc = lerp_color(_GOLD_BRIGHT, _GOLD_DEEP, yy / max(1, h - 1))
                pygame.draw.line(fill, fc, (0, yy), (hw, yy))
            mask = pygame.Surface((hw, h), pygame.SRCALPHA)
            if idx == 0:
                pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, hw, h),
                                 border_top_left_radius=rad,
                                 border_bottom_left_radius=rad)
            else:
                pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, hw, h),
                                 border_top_right_radius=rad,
                                 border_bottom_right_radius=rad)
            fill.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            surf.blit(fill, (hx, y))
            txt_col = (16, 10, 30)
        else:
            txt_col = _GOLD_BRIGHT

        img = f.render(label, True, txt_col)
        if not selected:
            img.set_alpha(216)
        group_w = coin_r * 2 + 5 + img.get_width()
        gx = hx + (hw - group_w) // 2
        ccx, ccy = gx + coin_r, y + h // 2
        if cracked:
            # Tarnished era coin: pewter disc, bronze crack, one drip nub.
            pygame.draw.circle(surf, _T_RIM_MID, (ccx, ccy), coin_r)
            pygame.draw.circle(surf, (16, 10, 30), (ccx, ccy), coin_r, 1)
            pygame.draw.lines(surf, _BRONZE_HI, False,
                              [(ccx - coin_r + 2, ccy - 2), (ccx - 1, ccy + 1),
                               (ccx + 2, ccy - 2), (ccx + coin_r - 2, ccy + 3)], 1)
            pygame.draw.circle(surf, _BRONZE_MID, (ccx + coin_r - 2, ccy + coin_r - 1), 2)
        else:
            pygame.draw.circle(surf, coin_col, (ccx, ccy), coin_r)
            pygame.draw.circle(surf, (16, 10, 30), (ccx, ccy), coin_r, 1)
            pygame.draw.circle(surf, (255, 255, 255, 150),
                               (ccx - coin_r // 3, ccy - coin_r // 3), max(1, coin_r // 3))
        surf.blit(img, (gx + coin_r * 2 + 5, ccy - img.get_height() // 2))

    pygame.draw.rect(surf, _GOLD_BRIGHT, (x, y, w, h), width=2, border_radius=rad)
    pygame.draw.line(surf, (*_GOLD_BRIGHT, 120),
                     (x + half, y + 4), (x + half, y + h - 4), 1)


# ── Shame row (mirrors achievements_screen._draw_row at 1x) ───────────────────
_WHITE = (245, 246, 255)
_DIM   = (150, 150, 172)
_ROW_H = 56
_PAD_X = 12
_BADGE = 44


def draw_shame_row(surf, y, icon_key, title, desc, revealed):
    rx = _PAD_X
    rw = W - _PAD_X * 2
    rh = _ROW_H
    rad = 12
    body_top = _PANEL_LIGHTER if revealed else (18, 14, 40)
    body_bot = _PANEL_DARK if revealed else (10, 7, 26)
    panel = pygame.Surface((rw, rh), pygame.SRCALPHA)
    for yy in range(rh):
        t = yy / max(1, rh - 1)
        pygame.draw.line(panel, lerp_color(body_top, body_bot, t), (0, yy), (rw, yy))
    mask = pygame.Surface((rw, rh), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, rw, rh), border_radius=rad)
    panel.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    # Revealed shame rows wear a BRONZE hairline + left stripe (vs Fame's gold),
    # so a "yours" read survives without ever looking like a gold win.
    border = (*_BRONZE_HI, 190) if revealed else (90, 86, 120, 140)
    pygame.draw.rect(panel, border, (0, 0, rw, rh), width=1, border_radius=rad)
    if revealed:
        stripe = pygame.Surface((4, rh - 8), pygame.SRCALPHA)
        for yy in range(stripe.get_height()):
            t = yy / max(1, stripe.get_height() - 1)
            stripe.fill(lerp_color(_BRONZE_HI, _BRONZE_LO, t), (0, yy, 4, 1))
        panel.blit(stripe, (3, 4))
    surf.blit(panel, (rx, y))

    badge_rect = pygame.Rect(rx + 8, y + (rh - _BADGE) // 2, _BADGE, _BADGE)
    badge = _build_tarnished(icon_key, _BADGE, locked=not revealed)
    surf.blit(badge, badge.get_rect(center=badge_rect.center))

    tx = rx + 8 + _BADGE + 10
    if revealed:
        tcol, dcol = (210, 196, 176), _WHITE   # tarnished-cream title
    else:
        title, desc = "???", "Hidden — disgrace yourself to reveal."
        tcol = dcol = _DIM

    ts = _font(17, True).render(title, True, tcol)
    surf.blit(ts, (tx, y + 9))
    # description wrap to two lines
    f = _font(12, True)
    words = desc.split(" ")
    lines, cur = [], ""
    maxw = (W - _PAD_X) - tx - 8
    for wd in words:
        trial = (cur + " " + wd).strip()
        if f.size(trial)[0] <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    for i, ln in enumerate(lines[:2]):
        surf.blit(f.render(ln, True, dcol), (tx, y + 30 + i * 14))

    # Revealed shame rows carry a small cracked-skull "demerit" mark instead of
    # the Fame gold star — bronze, top-right.
    if revealed:
        scx, scy = W - _PAD_X - 12, y + 16
        pygame.draw.circle(surf, _BRONZE_MID, (scx, scy - 1), 5)
        pygame.draw.rect(surf, _BRONZE_MID, (scx - 3, scy + 2, 6, 3), border_radius=1)
        for ddx in (-2, 2):
            pygame.draw.circle(surf, (16, 10, 30), (scx + ddx, scy - 1), 1)


def render_shame_tab():
    surf = pygame.Surface((W, H))
    for yy in range(H):
        t = yy / (H - 1)
        pygame.draw.line(surf, lerp_color(_NIGHT_DEEP, (14, 8, 36), t), (0, yy), (W, yy))

    # Title.
    _outlined_text(surf, "ACHIEVEMENTS", (W // 2, 14), size=22, px=2,
                   shadow_offset=(2, 3))

    # Tab bar just under the title.
    tab_rect = (24, 32, W - 48, 26)
    draw_tab_bar(surf, tab_rect, active_idx=1)

    # Category header band.
    cy0 = 70
    head_col = _GOLD_BRIGHT
    py = cy0 + 13
    d = 4
    pip = [(_PAD_X, py), (_PAD_X + d, py - d), (_PAD_X + 2 * d, py), (_PAD_X + d, py + d)]
    pygame.draw.polygon(surf, head_col, pip)
    pygame.draw.polygon(surf, _GOLD_DEEP, pip, 1)
    lbl = _font(15, True).render("BLOOPER REEL", True, head_col)
    lx = _PAD_X + 3 * d
    surf.blit(lbl, (lx, cy0 + 5))
    cnt = _font(13, True).render("3/9", True, _GOLD_DEEP)
    cnt_x = (W - _PAD_X) - cnt.get_width()
    surf.blit(cnt, (cnt_x, cy0 + 6))
    rail_l = lx + lbl.get_width() + 6
    rail_r = cnt_x - 6
    if rail_r > rail_l:
        rail = pygame.Surface((rail_r - rail_l, 2), pygame.SRCALPHA)
        for xx in range(rail.get_width()):
            fade = 1.0 - xx / max(1, rail.get_width())
            rail.fill((*_GOLD_BRIGHT, int(160 * fade)), (xx, 0, 1, 2))
        surf.blit(rail, (rail_l, cy0 + 24))

    rows = [
        ("egg", "THE GOOSE EGG",
         "Zero points, zero coins. A flawless record of nothing.", True),
        ("kfc", "THE KFC INCIDENT",
         "Died as a flying fry. Finger lickin' fatal.", True),
        ("wing", "THE ICARUS AWARD",
         "Flew too close to the sun. It was 4 seconds away.", True),
        ("", "???", "", False),
        ("", "???", "", False),
    ]
    y = cy0 + _CAT_H
    for icon, title, desc, revealed in rows:
        draw_shame_row(surf, y, icon, title, desc, revealed)
        y += _ROW_H + 5

    # Scrollbar (content taller than viewport).
    top = 100
    view_h = H - 30 - top
    track_x = W - 5
    pygame.draw.rect(surf, (255, 255, 255, 30), (track_x, top, 3, view_h), border_radius=2)
    thumb_h = 90
    pygame.draw.rect(surf, _BRONZE_HI, (track_x, top + 10, 3, thumb_h), border_radius=2)

    # Footer prompt.
    ftr = pygame.Surface((W, 30), pygame.SRCALPHA)
    ftr.fill((*_NIGHT_DEEP, 230))
    pygame.draw.line(ftr, (*_GOLD_BRIGHT, 100), (0, 0), (W, 0), 1)
    surf.blit(ftr, (0, H - 30))
    tip = _font(13, True).render("TAP TO RETURN  ·  DRAG TO SCROLL", True, _GOLD_PALE)
    surf.blit(tip, tip.get_rect(center=(W // 2, H - 15)))
    return surf


_CAT_H = 30


def render_tarnish_strip():
    """Gold badge vs tarnished variant side by side at ~64px so the crack/drip
    recipe is legible for baking."""
    sz = 64
    cell = 150          # wide enough that the labels never collide
    pad = 18
    labh = 24
    panel = pygame.Surface((cell * 2, sz + pad * 2 + labh))
    for yy in range(panel.get_height()):
        t = yy / max(1, panel.get_height() - 1)
        pygame.draw.line(panel, lerp_color(_NIGHT_DEEP, (14, 8, 36), t),
                         (0, yy), (panel.get_width(), yy))

    gold = AI.get_badge("score", sz, unlocked=True)
    tarn = _build_tarnished("score", sz, locked=False)
    panel.blit(gold, (cell // 2 - sz // 2, pad + labh))
    panel.blit(tarn, (cell + cell // 2 - sz // 2, pad + labh))

    f = _font(13, True)
    g = f.render("GOLD - Fame", True, _GOLD_PALE)
    panel.blit(g, (cell // 2 - g.get_width() // 2, pad // 2))
    t2 = f.render("TARNISHED - Shame", True, (200, 188, 170))
    panel.blit(t2, (cell + cell // 2 - t2.get_width() // 2, pad // 2))

    # thin gold divider between the two cells so the comparison reads as a pair
    pygame.draw.line(panel, (*_GOLD_DEEP, 120), (cell, pad // 2),
                     (cell, panel.get_height() - pad // 2), 1)
    return panel


def main():
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "docs", "wall_of_shame")
    os.makedirs(out_dir, exist_ok=True)
    pygame.image.save(render_shame_tab(), os.path.join(out_dir, "round_1.png"))
    pygame.image.save(render_tarnish_strip(), os.path.join(out_dir, "tarnish_strip.png"))
    print("wrote", os.path.join(out_dir, "round_1.png"))
    print("wrote", os.path.join(out_dir, "tarnish_strip.png"))


if __name__ == "__main__":
    main()
