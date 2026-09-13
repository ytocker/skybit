"""Render 5 visual variants of the in-game HUD (score, BEST, coins, pause).

Each variant paints the four HUD elements at their live layout coordinates
on top of an authentic dusk-biome backdrop (sky + clouds + mountains +
ground + one pillar silhouette mid-frame) so the user can judge legibility
and theme fit against real gameplay context.

Output:
  docs/screenshots/hud_variants/v1_royal.png    full 360 × 640 frames
  docs/screenshots/hud_variants/v2_scarlet.png
  docs/screenshots/hud_variants/v3_glass.png
  docs/screenshots/hud_variants/v4_hex.png
  docs/screenshots/hud_variants/v5_ribbon.png
  docs/screenshots/hud_variants/compare.png    labelled horizontal strip

Run from the repo root:

    PYTHONPATH=. python tools/render_hud_variants.py
"""
import math
import os
import random
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame


# ── Shared dusk backdrop ─────────────────────────────────────────────────────

def draw_bg(surf, scroll=0.0, phase=0.62):
    """Sky + cloud + mountain + ground backdrop matching the live game look.
    Lifted from tools/render_pillar_gameplay.py::draw_bg."""
    from game.config import W, H, GROUND_Y
    from game import biome as _biome
    from game.draw import (
        get_sky_surface_biome, draw_mountains, draw_cloud, draw_ground,
    )
    buckets = _biome.PHASE_BUCKETS
    bf = (phase % 1.0) * buckets
    a = int(bf) % buckets
    b = (a + 1) % buckets
    t = bf - int(bf)
    pal_a = _biome.palette_for_phase(a / buckets)
    pal_b = _biome.palette_for_phase(b / buckets)
    sky_a = get_sky_surface_biome(W, H, GROUND_Y, pal_a, a)
    sky_b = get_sky_surface_biome(W, H, GROUND_Y, pal_b, b)
    sky_a.set_alpha(None); surf.blit(sky_a, (0, 0))
    if t > 0:
        sky_b.set_alpha(int(t * 255)); surf.blit(sky_b, (0, 0))
        sky_b.set_alpha(None)
    for i, (bx, by, sc, var) in enumerate(
            ((20, 90, 0.9, 0), (180, 140, 1.1, 2), (60, 220, 0.8, 3),
             (230, 60, 0.7, 1), (320, 180, 0.9, 4))):
        ox = ((bx - scroll * (0.04 + 0.02 * i)) % (W + 160)) - 80
        draw_cloud(surf, ox, by + math.sin(1.2 + i) * 3, sc, variant=var)
    pal = pal_a
    draw_mountains(surf, scroll, GROUND_Y, W, pal['mtn_far'], pal['mtn_near'])
    draw_ground(surf, GROUND_Y, W, H, scroll,
                pal['ground_top'], pal['ground_mid'], (60, 40, 25))
    return pal


def draw_pillar_context(surf, palette):
    """One pillar mid-frame to give the HUD realistic visual competition."""
    from game.config import GAP_START
    from game.entities import Pipe
    p = Pipe(180.0, 360.0, float(GAP_START))
    p.seed = 13  # lantern variant for warm dusk tones
    p.draw(surf, palette)


# ── Variant 1: Royal ─────────────────────────────────────────────────────────
# Ornate, gold-dominant. Score uses the menu's gold-on-red outlined-text
# treatment (same one that rims the SKYBIT title) for a hero feel. Side
# pills get a deeper border, a heavier trophy, and a gold rivet detail.

def render_v1_royal(surf, score, best, coins):
    from game.config import W
    from game.draw import rounded_rect, NEAR_BLACK, WHITE
    from game.hud import (
        _PANEL_DARK, _GOLD_BRIGHT, _GOLD_MUTED, _GOLD_DEEP, _GOLD_PALE,
        _RED_OUTLINE, _ORANGE_BORDER, _draw_trophy, _coin_icon, _font,
    )

    # ── Score: outlined gold-on-red, sat on a dark panel with double trim
    score_txt = str(score)
    f = _font(48, True)
    img = f.render(score_txt, True, _GOLD_BRIGHT)
    out = f.render(score_txt, True, _RED_OUTLINE)
    sh  = f.render(score_txt, True, NEAR_BLACK)
    r = img.get_rect(center=(W // 2, 72))
    back_w = max(r.width + 64, 96)
    back_h = r.height + 18
    back = pygame.Surface((back_w, back_h), pygame.SRCALPHA)
    pygame.draw.rect(back, (*_PANEL_DARK, 200), (0, 0, back_w, back_h),
                     border_radius=back_h // 2)
    # Double rim: outer gold + inner deep gold accent for a "framed plaque"
    pygame.draw.rect(back, (*_GOLD_BRIGHT, 220), (0, 0, back_w, back_h),
                     border_radius=back_h // 2, width=2)
    pygame.draw.rect(back, (*_GOLD_DEEP, 140), (3, 3, back_w - 6, back_h - 6),
                     border_radius=(back_h - 6) // 2, width=1)
    surf.blit(back, (W // 2 - back_w // 2, r.y - 9))
    # Pixel outline (3px) + soft shadow + gold face
    for ox, oy in ((-3, 0), (3, 0), (0, -3), (0, 3),
                   (-3, -3), (3, -3), (-3, 3), (3, 3)):
        surf.blit(out, (r.x + ox, r.y + oy))
    sh.set_alpha(150)
    surf.blit(sh, (r.x + 2, r.y + 4))
    surf.blit(img, r.topleft)

    # ── BEST: dark shield with trophy + gold-on-dark label + bright value
    bp = pygame.Surface((100, 38), pygame.SRCALPHA)
    pygame.draw.rect(bp, (*_PANEL_DARK, 230), (0, 0, 100, 38), border_radius=11)
    pygame.draw.rect(bp, (*_GOLD_BRIGHT, 220), (0, 0, 100, 38),
                     border_radius=11, width=2)
    # Gold rivet at each corner
    for cx, cy in ((6, 6), (94, 6), (6, 32), (94, 32)):
        pygame.draw.circle(bp, _GOLD_PALE, (cx, cy), 1)
    _draw_trophy(bp, 18, 19, 9)
    lf = _font(11, True).render("BEST", True, _GOLD_MUTED)
    bp.blit(lf, lf.get_rect(center=(64, 11)))
    vf = _font(16, True).render(str(best), True, _GOLD_BRIGHT)
    bp.blit(vf, vf.get_rect(center=(64, 26)))
    surf.blit(bp, (10, 14))

    # ── Coins: matching dark pill with coin face and bright gold count
    cp = pygame.Surface((94, 38), pygame.SRCALPHA)
    pygame.draw.rect(cp, (*_PANEL_DARK, 230), (0, 0, 94, 38), border_radius=11)
    pygame.draw.rect(cp, (*_GOLD_BRIGHT, 220), (0, 0, 94, 38),
                     border_radius=11, width=2)
    for cx, cy in ((6, 6), (88, 6), (6, 32), (88, 32)):
        pygame.draw.circle(cp, _GOLD_PALE, (cx, cy), 1)
    _coin_icon(cp, 18, 19, 11)
    cv = _font(18, True).render(f"x{coins}", True, _GOLD_BRIGHT)
    cp.blit(cv, cv.get_rect(center=(58, 19)))
    surf.blit(cp, (W - 162, 14))

    # ── Pause: round medallion (dark + gold ring + gold bars)
    px, py = W - 56, 12
    cx, cy = px + 22, py + 22
    pygame.draw.circle(surf, _PANEL_DARK, (cx, cy), 22)
    pygame.draw.circle(surf, _GOLD_BRIGHT, (cx, cy), 22, 2)
    pygame.draw.circle(surf, _GOLD_DEEP, (cx, cy), 18, 1)
    pygame.draw.rect(surf, _GOLD_BRIGHT, (cx - 8, cy - 9, 5, 18), border_radius=2)
    pygame.draw.rect(surf, _GOLD_BRIGHT, (cx + 3, cy - 9, 5, 18), border_radius=2)


# ── Variant 2: Scarlet ───────────────────────────────────────────────────────
# Bold arcade red. The score sits on a true scarlet gradient pill (same
# look as the menu's PLAY button); the side pills echo it at smaller scale;
# the pause button is a square scarlet plate with white bars.

def render_v2_scarlet(surf, score, best, coins):
    from game.config import W
    from game.draw import lerp_color, WHITE, NEAR_BLACK
    from game.hud import (
        _SCARLET_TOP, _SCARLET_BOT, _SCARLET_SHADOW, _GOLD_BRIGHT, _GOLD_PALE,
        _coin_icon, _font,
    )

    def scarlet_pill(w, h, alpha=255):
        pill = pygame.Surface((w, h), pygame.SRCALPHA)
        for yy in range(h):
            c = lerp_color(_SCARLET_TOP, _SCARLET_BOT, yy / max(1, h - 1))
            pygame.draw.line(pill, c, (0, yy), (w - 1, yy))
        # cream frost on the top half
        frost = pygame.Surface((w, h), pygame.SRCALPHA)
        for yy in range(h // 2):
            a = int(50 * (1 - yy / (h / 2)))
            pygame.draw.line(frost, (255, 245, 220, a), (0, yy), (w, yy))
        pill.blit(frost, (0, 0))
        # darkening on the bottom half
        bsh = pygame.Surface((w, h), pygame.SRCALPHA)
        for yy in range(h // 2, h):
            a = int(55 * (yy - h // 2) / (h / 2))
            pygame.draw.line(bsh, (0, 0, 0, a), (0, yy), (w, yy))
        pill.blit(bsh, (0, 0))
        # rounded mask
        mask = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, w, h),
                         border_radius=h // 2)
        pill.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        # gold border + thin accent line
        pygame.draw.rect(pill, _GOLD_BRIGHT, (0, 0, w, h),
                         width=2, border_radius=h // 2)
        pygame.draw.line(pill, (*_GOLD_BRIGHT, 110),
                         (h // 2, 3), (w - h // 2, 3), 1)
        pill.set_alpha(alpha)
        return pill

    # ── Score: hero scarlet pill, cream-embossed numerals
    score_txt = str(score)
    f = _font(40, True)
    img = f.render(score_txt, True, (255, 245, 220))
    ph = img.get_height() + 18
    pw = max(img.get_width() + 56, 100)
    pill = scarlet_pill(pw, ph)
    surf.blit(pill, (W // 2 - pw // 2, 72 - ph // 2))
    sh_img = f.render(score_txt, True, _SCARLET_SHADOW)
    sh_img.set_alpha(220)
    tr = img.get_rect(center=(W // 2, 72))
    surf.blit(sh_img, (tr.x + 1, tr.y + 1))
    surf.blit(img, tr)

    # ── BEST: smaller scarlet pill with gold "BEST" label + bright value
    bw, bh = 100, 36
    surf.blit(scarlet_pill(bw, bh), (10, 14))
    bf = _font(10, True).render("BEST", True, _GOLD_PALE)
    surf.blit(bf, bf.get_rect(center=(10 + 32, 14 + 11)))
    vf = _font(16, True).render(str(best), True, (255, 245, 220))
    sh = _font(16, True).render(str(best), True, _SCARLET_SHADOW)
    sh.set_alpha(200)
    vc = (10 + 64, 14 + 22)
    surf.blit(sh, sh.get_rect(center=(vc[0] + 1, vc[1] + 1)))
    surf.blit(vf, vf.get_rect(center=vc))
    # tiny gold trophy bullet on the left
    pygame.draw.circle(surf, _GOLD_BRIGHT, (10 + 14, 14 + 18), 4)
    pygame.draw.rect(surf, _GOLD_BRIGHT, (10 + 12, 14 + 22, 5, 4))

    # ── Coins: scarlet pill with coin pinned right
    cw, ch = 94, 36
    cx0 = W - 162
    surf.blit(scarlet_pill(cw, ch), (cx0, 14))
    cv = _font(18, True).render(f"x{coins}", True, (255, 245, 220))
    sh = _font(18, True).render(f"x{coins}", True, _SCARLET_SHADOW)
    sh.set_alpha(200)
    cvc = (cx0 + 38, 14 + 18)
    surf.blit(sh, sh.get_rect(center=(cvc[0] + 1, cvc[1] + 1)))
    surf.blit(cv, cv.get_rect(center=cvc))
    _coin_icon(surf, cx0 + 76, 14 + 18, 10)

    # ── Pause: square scarlet plate with white pause bars
    pr = pygame.Rect(W - 56, 12, 44, 44)
    pill = scarlet_pill(pr.width, pr.height)
    # squarer corners — overlay a less-rounded mask
    mask = pygame.Surface((pr.width, pr.height), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255),
                     (0, 0, pr.width, pr.height), border_radius=10)
    pill.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    pygame.draw.rect(pill, _GOLD_BRIGHT, (0, 0, pr.width, pr.height),
                     width=2, border_radius=10)
    surf.blit(pill, pr.topleft)
    cx, cy = pr.center
    pygame.draw.rect(surf, WHITE, (cx - 8, cy - 9, 5, 18), border_radius=2)
    pygame.draw.rect(surf, WHITE, (cx + 3, cy - 9, 5, 18), border_radius=2)


# ── Variant 3: Glass ─────────────────────────────────────────────────────────
# Minimal, translucent. Pills are low-alpha dark slabs with a single 1px
# gold hairline; text is white with a thin shadow. The pause button is a
# glass disc. Quietest variant — meant to get out of the way during play.

def render_v3_glass(surf, score, best, coins):
    from game.config import W
    from game.draw import WHITE, NEAR_BLACK
    from game.hud import _PANEL_DARK, _GOLD_BRIGHT, _GOLD_PALE, _coin_icon, _font

    # ── Score: thin glass pill, white numerals, gold hairline
    score_txt = str(score)
    f = _font(46, True)
    img = f.render(score_txt, True, WHITE)
    sh  = f.render(score_txt, True, NEAR_BLACK)
    r = img.get_rect(center=(W // 2, 72))
    back_w = max(r.width + 48, 90)
    back_h = r.height + 12
    back = pygame.Surface((back_w, back_h), pygame.SRCALPHA)
    pygame.draw.rect(back, (*_PANEL_DARK, 110), (0, 0, back_w, back_h),
                     border_radius=back_h // 2)
    pygame.draw.rect(back, (*_GOLD_BRIGHT, 150), (0, 0, back_w, back_h),
                     border_radius=back_h // 2, width=1)
    surf.blit(back, (W // 2 - back_w // 2, r.y - 6))
    sh.set_alpha(140)
    surf.blit(sh, (r.x + 2, r.y + 3))
    surf.blit(img, r.topleft)

    # ── BEST: low-alpha slab, gold value
    bp = pygame.Surface((92, 32), pygame.SRCALPHA)
    pygame.draw.rect(bp, (*_PANEL_DARK, 140), (0, 0, 92, 32), border_radius=8)
    pygame.draw.rect(bp, (*_GOLD_BRIGHT, 110), (0, 0, 92, 32),
                     border_radius=8, width=1)
    # Subtle star/spark glyph
    pts = [(11, 8), (13, 13), (18, 13), (14, 16), (16, 21),
           (11, 18), (6, 21), (8, 16), (4, 13), (9, 13)]
    pygame.draw.polygon(bp, (*_GOLD_BRIGHT, 220), pts)
    lf = _font(10, True).render("BEST", True, (235, 230, 215))
    bp.blit(lf, lf.get_rect(center=(56, 9)))
    vf = _font(15, True).render(str(best), True, _GOLD_BRIGHT)
    bp.blit(vf, vf.get_rect(center=(56, 21)))
    surf.blit(bp, (10, 14))

    # ── Coins: matching slab
    cp = pygame.Surface((86, 32), pygame.SRCALPHA)
    pygame.draw.rect(cp, (*_PANEL_DARK, 140), (0, 0, 86, 32), border_radius=8)
    pygame.draw.rect(cp, (*_GOLD_BRIGHT, 110), (0, 0, 86, 32),
                     border_radius=8, width=1)
    _coin_icon(cp, 14, 16, 9)
    cv = _font(16, True).render(f"x{coins}", True, _GOLD_BRIGHT)
    cp.blit(cv, cv.get_rect(center=(52, 16)))
    surf.blit(cp, (W - 154, 14))

    # ── Pause: round glass disc
    px, py = W - 56, 12
    cx, cy = px + 22, py + 22
    disc = pygame.Surface((44, 44), pygame.SRCALPHA)
    pygame.draw.circle(disc, (*_PANEL_DARK, 130), (22, 22), 22)
    pygame.draw.circle(disc, (*_GOLD_BRIGHT, 150), (22, 22), 22, 1)
    # subtle inner highlight
    pygame.draw.arc(disc, (*_GOLD_PALE, 90),
                    (3, 3, 38, 38), math.pi * 1.1, math.pi * 1.9, 1)
    surf.blit(disc, (px, py))
    pygame.draw.rect(surf, WHITE, (cx - 7, cy - 8, 4, 16), border_radius=2)
    pygame.draw.rect(surf, WHITE, (cx + 3, cy - 8, 4, 16), border_radius=2)


# ── Variant 4: Hex ───────────────────────────────────────────────────────────
# Geometric badge / achievement-plate feel. Every element is a hexagon
# (pointy-top), filled with a scarlet→dark gradient, gold trim, gold rivets
# at the three top vertices. Score is a tall hexagon; side pills are
# horizontal hexagons.

def render_v4_hex(surf, score, best, coins):
    from game.config import W
    from game.draw import lerp_color, WHITE, NEAR_BLACK
    from game.hud import (
        _PANEL_DARK, _PANEL_LIGHTER, _SCARLET_TOP, _SCARLET_BOT,
        _GOLD_BRIGHT, _GOLD_DEEP, _GOLD_PALE, _RED_OUTLINE, _draw_trophy,
        _coin_icon, _font,
    )

    def hex_pts(cx, cy, w, h, pointy_top=False):
        # Flat-top hex by default; pointy-top rotates 90°.
        if pointy_top:
            return [
                (cx, cy - h // 2),
                (cx + w // 2, cy - h // 4),
                (cx + w // 2, cy + h // 4),
                (cx, cy + h // 2),
                (cx - w // 2, cy + h // 4),
                (cx - w // 2, cy - h // 4),
            ]
        return [
            (cx - w // 2, cy),
            (cx - w // 4, cy - h // 2),
            (cx + w // 4, cy - h // 2),
            (cx + w // 2, cy),
            (cx + w // 4, cy + h // 2),
            (cx - w // 4, cy + h // 2),
        ]

    def hex_plate(surf, cx, cy, w, h, scarlet=True):
        pts = hex_pts(cx, cy, w, h)
        # Solid fill — gradient effect via two stacked polygons (top
        # lighter, bottom darker) split horizontally through the centre.
        top_col = _SCARLET_TOP if scarlet else _PANEL_LIGHTER
        bot_col = _SCARLET_BOT if scarlet else _PANEL_DARK
        # full polygon as the base (bot colour)
        pygame.draw.polygon(surf, bot_col, pts)
        # clip a top-half lighter polygon by drawing on a temp surface
        tmp = pygame.Surface((w + 2, h + 2), pygame.SRCALPHA)
        local_pts = [(p[0] - cx + w // 2 + 1, p[1] - cy + h // 2 + 1) for p in pts]
        pygame.draw.polygon(tmp, top_col, local_pts)
        # mask only the top half
        mask = pygame.Surface((w + 2, h + 2), pygame.SRCALPHA)
        mask.fill((255, 255, 255, 255), pygame.Rect(0, 0, w + 2, h // 2 + 1))
        tmp.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        surf.blit(tmp, (cx - w // 2 - 1, cy - h // 2 - 1))
        # gold trim
        pygame.draw.polygon(surf, _GOLD_BRIGHT, pts, 2)
        # rivets at the three top vertices
        for i in (0, 1, 2, 3, 4, 5):
            px, py = pts[i]
            pygame.draw.circle(surf, _GOLD_PALE, (px, py), 2)
            pygame.draw.circle(surf, _GOLD_DEEP, (px, py), 2, 1)

    # ── Score: large flat-top hex, gold-on-red outlined numerals
    score_txt = str(score)
    f = _font(40, True)
    img = f.render(score_txt, True, _GOLD_BRIGHT)
    out = f.render(score_txt, True, _RED_OUTLINE)
    sh  = f.render(score_txt, True, NEAR_BLACK)
    hex_plate(surf, W // 2, 72, 130, 72, scarlet=True)
    r = img.get_rect(center=(W // 2, 72))
    for ox, oy in ((-2, 0), (2, 0), (0, -2), (0, 2),
                   (-2, -2), (2, -2), (-2, 2), (2, 2)):
        surf.blit(out, (r.x + ox, r.y + oy))
    sh.set_alpha(150)
    surf.blit(sh, (r.x + 2, r.y + 3))
    surf.blit(img, r.topleft)

    # ── BEST: smaller flat-top hex with trophy + value
    hex_plate(surf, 56, 32, 96, 44, scarlet=False)
    _draw_trophy(surf, 28, 32, 8)
    lf = _font(10, True).render("BEST", True, _GOLD_PALE)
    surf.blit(lf, lf.get_rect(center=(68, 24)))
    vf = _font(15, True).render(str(best), True, _GOLD_BRIGHT)
    surf.blit(vf, vf.get_rect(center=(68, 38)))

    # ── Coins: matching hex
    hex_plate(surf, W - 110, 32, 92, 44, scarlet=False)
    _coin_icon(surf, W - 138, 32, 10)
    cv = _font(17, True).render(f"x{coins}", True, _GOLD_BRIGHT)
    surf.blit(cv, cv.get_rect(center=(W - 96, 32)))

    # ── Pause: small flat-top hex with pause bars
    hex_plate(surf, W - 34, 32, 44, 44, scarlet=True)
    cx, cy = W - 34, 32
    pygame.draw.rect(surf, WHITE, (cx - 7, cy - 8, 4, 16), border_radius=2)
    pygame.draw.rect(surf, WHITE, (cx + 3, cy - 8, 4, 16), border_radius=2)


# ── Variant 5: Ribbon ────────────────────────────────────────────────────────
# Scroll-and-seal. Score is a horizontal banner with V-cut tails; side
# pills are smaller banners; pause is a wax-seal style circular medallion
# with a scalloped (sun-burst) outer edge. Most decorative variant.

def render_v5_ribbon(surf, score, best, coins):
    from game.config import W
    from game.draw import WHITE, NEAR_BLACK
    from game.hud import (
        _PANEL_DARK, _SCARLET_TOP, _SCARLET_BOT, _SCARLET_SHADOW,
        _GOLD_BRIGHT, _GOLD_DEEP, _GOLD_PALE, _RED_OUTLINE,
        _coin_icon, _font,
    )

    def banner(surf, cx, cy, w, h, scarlet=True):
        # Horizontal banner with notched (V-cut) ends. Two stacked
        # polygons — outer (gold/dark trim) and inner (scarlet/dark body).
        notch = max(h // 2 - 2, 6)
        x = cx - w // 2
        y = cy - h // 2
        outer = [
            (x + notch, y),
            (x + w - notch, y),
            (x + w, y + h // 2),
            (x + w - notch, y + h),
            (x + notch, y + h),
            (x, y + h // 2),
        ]
        # Fold accents on the back of each tail
        fold_l = [(x, y + h // 2),
                  (x + notch, y + h),
                  (x + notch, y + h + 4),
                  (x - 4, y + h // 2 + 4)]
        fold_r = [(x + w, y + h // 2),
                  (x + w - notch, y + h),
                  (x + w - notch, y + h + 4),
                  (x + w + 4, y + h // 2 + 4)]
        pygame.draw.polygon(surf, _SCARLET_SHADOW if scarlet else (0, 0, 0), fold_l)
        pygame.draw.polygon(surf, _SCARLET_SHADOW if scarlet else (0, 0, 0), fold_r)
        # Body fill (scarlet uses real two-tone gradient via two polys)
        if scarlet:
            pygame.draw.polygon(surf, _SCARLET_BOT, outer)
            top_half = pygame.Surface((w + 4, h + 4), pygame.SRCALPHA)
            local = [(p[0] - x + 2, p[1] - y + 2) for p in outer]
            pygame.draw.polygon(top_half, _SCARLET_TOP, local)
            mask = pygame.Surface((w + 4, h + 4), pygame.SRCALPHA)
            mask.fill((255, 255, 255, 255), pygame.Rect(0, 0, w + 4, h // 2 + 2))
            top_half.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            surf.blit(top_half, (x - 2, y - 2))
        else:
            pygame.draw.polygon(surf, _PANEL_DARK, outer)
        # Gold trim
        pygame.draw.polygon(surf, _GOLD_BRIGHT, outer, 2)
        # Inner highlight line along the top fold
        pygame.draw.line(surf, (*_GOLD_PALE, 180),
                         (x + notch + 2, y + 2),
                         (x + w - notch - 2, y + 2), 1)

    # ── Score: big scarlet banner with gold-outlined numerals
    score_txt = str(score)
    f = _font(40, True)
    img = f.render(score_txt, True, _GOLD_BRIGHT)
    out = f.render(score_txt, True, _RED_OUTLINE)
    sh  = f.render(score_txt, True, NEAR_BLACK)
    banner(surf, W // 2, 72, 170, 56, scarlet=True)
    r = img.get_rect(center=(W // 2, 72))
    for ox, oy in ((-2, 0), (2, 0), (0, -2), (0, 2),
                   (-2, -2), (2, -2), (-2, 2), (2, 2)):
        surf.blit(out, (r.x + ox, r.y + oy))
    sh.set_alpha(150)
    surf.blit(sh, (r.x + 2, r.y + 3))
    surf.blit(img, r.topleft)

    # ── BEST: small navy banner with gold trim, trophy bullet, gold value
    banner(surf, 58, 30, 104, 30, scarlet=False)
    # Tiny trophy bullet
    pygame.draw.circle(surf, _GOLD_BRIGHT, (24, 30), 5)
    pygame.draw.rect(surf, _GOLD_BRIGHT, (21, 32, 7, 4))
    lf = _font(10, True).render("BEST", True, _GOLD_PALE)
    surf.blit(lf, lf.get_rect(center=(50, 23)))
    vf = _font(15, True).render(str(best), True, _GOLD_BRIGHT)
    surf.blit(vf, vf.get_rect(center=(72, 35)))

    # ── Coins: small scarlet banner with coin pinned right
    banner(surf, W - 110, 30, 94, 30, scarlet=True)
    cv = _font(17, True).render(f"x{coins}", True, _GOLD_PALE)
    sh = _font(17, True).render(f"x{coins}", True, _SCARLET_SHADOW)
    sh.set_alpha(220)
    cc = (W - 130, 30)
    surf.blit(sh, sh.get_rect(center=(cc[0] + 1, cc[1] + 1)))
    surf.blit(cv, cv.get_rect(center=cc))
    _coin_icon(surf, W - 86, 30, 9)

    # ── Pause: wax-seal medallion with scalloped edge
    px, py = W - 56, 12
    cx, cy = px + 22, py + 22
    # Scalloped sun-burst — 12 small gold circles around the rim
    for k in range(12):
        ang = k * math.pi / 6
        sx = cx + int(math.cos(ang) * 22)
        sy = cy + int(math.sin(ang) * 22)
        pygame.draw.circle(surf, _GOLD_BRIGHT, (sx, sy), 3)
        pygame.draw.circle(surf, _GOLD_DEEP, (sx, sy), 3, 1)
    # Inner dark disc
    pygame.draw.circle(surf, _PANEL_DARK, (cx, cy), 17)
    pygame.draw.circle(surf, _GOLD_BRIGHT, (cx, cy), 17, 2)
    # Embossed P (engraved style — outlined gold)
    pf = _font(20, True)
    pi = pf.render("P", True, _GOLD_BRIGHT)
    po = pf.render("P", True, _RED_OUTLINE)
    pr = pi.get_rect(center=(cx, cy))
    for ox, oy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        surf.blit(po, (pr.x + ox, pr.y + oy))
    surf.blit(pi, pr)


# ── Main ─────────────────────────────────────────────────────────────────────

VARIANTS = [
    ("v1_royal",   "Royal",   render_v1_royal),
    ("v2_scarlet", "Scarlet", render_v2_scarlet),
    ("v3_glass",   "Glass",   render_v3_glass),
    ("v4_hex",     "Hex",     render_v4_hex),
    ("v5_ribbon",  "Ribbon",  render_v5_ribbon),
]

SCORE = 127
BEST  = 842
COINS = 23


def main():
    random.seed(42)
    pygame.init()
    pygame.font.init()

    from game.config import W, H
    pygame.display.set_mode((W, H))

    out_dir = os.path.join("docs", "screenshots", "hud_variants")
    os.makedirs(out_dir, exist_ok=True)

    frames: "list[tuple[str, str, pygame.Surface]]" = []

    for slug, label, render in VARIANTS:
        surf = pygame.Surface((W, H))
        palette = draw_bg(surf, scroll=120.0, phase=0.62)
        draw_pillar_context(surf, palette)
        render(surf, SCORE, BEST, COINS)

        out_path = os.path.join(out_dir, f"{slug}.png")
        pygame.image.save(surf, out_path)
        print(f"saved {out_path}")
        frames.append((slug, label, surf))

    # ── Compare strip: 5 frames tiled horizontally, labelled
    GAP = 12
    LABEL_H = 28
    PAD = 16
    cell_w, cell_h = W, H
    n = len(frames)
    canvas_w = cell_w * n + GAP * (n - 1) + PAD * 2
    canvas_h = cell_h + LABEL_H + PAD * 2
    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill((22, 18, 32))
    font = pygame.font.SysFont(None, 24, bold=True)
    for i, (_slug, label, fr) in enumerate(frames):
        x = PAD + i * (cell_w + GAP)
        y = PAD
        pygame.draw.rect(canvas, (200, 170, 90),
                         pygame.Rect(x - 2, y - 2, cell_w + 4, cell_h + 4),
                         width=2)
        canvas.blit(fr, (x, y))
        lbl = font.render(label, True, (240, 210, 130))
        canvas.blit(lbl, (x + (cell_w - lbl.get_width()) // 2, y + cell_h + 6))

    cmp_path = os.path.join(out_dir, "compare.png")
    pygame.image.save(canvas, cmp_path)
    print(f"saved {cmp_path}  ({canvas_w}x{canvas_h})")


if __name__ == "__main__":
    sys.exit(main() or 0)
