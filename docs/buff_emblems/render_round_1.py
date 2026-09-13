"""Round-1 exploration sheet for the active-buff HUD emblem family.

Throwaway render harness — NOT shipped. Draws all 10 redesigned emblems on
the real slate plate (display size) plus a 6x zoom, with a top strip of the
CURRENT production emblems for before/after. Saves docs/buff_emblems/round_1.png.

Shared visual language for the new set:
  - rendered on a 6x supersampled scratch surface, smoothscaled down (crisp);
  - one key light from the top-left, one specular pinprick top-left;
  - a uniform dark outline weight + a faint warm contact-shadow ellipse so
    every object "sits" on the plate at the same visual weight/footprint;
  - silhouettes sized to fill ~22-24px of the 24px draw area, so no emblem
    looks tiny next to another.
"""
import math
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from game.hud import (
    _na_plate, _draw_buff_icon, _font, _NA_PAD,
    lerp_color,
)
from game.draw import (
    COIN_GOLD, COIN_DARK, MUSH_CAP, MUSH_CAP2, MUSH_SPOT, MUSH_STEM, WHITE,
)

KINDS = ["triple", "magnet", "megamagnet", "slowmo", "kfc",
         "ghost", "shrink", "grow", "reverse", "rail"]

# ── New emblem family ────────────────────────────────────────────────────────
# Every emblem renders at SS x its display size onto a square scratch surface,
# then smoothscales down. Drawing happens in a NATIVE-resolution coordinate
# system N x N (so geometry reads the same regardless of SS) by working in
# big-pixel units = native * SS.

SS = 6           # supersample factor for the emblems
N = 26           # native draw canvas (slightly larger than the 24px slot so
                 # the soft contact shadow has bleed room)
KEY = (-0.55, -0.6)   # top-left key-light direction, shared by all emblems


def _scratch():
    return pygame.Surface((N * SS, N * SS), pygame.SRCALPHA)


def _down(big, target):
    return pygame.transform.smoothscale(big, (target, target))


def _radial(surf, cx, cy, r, inner, outer, steps=None):
    """Soft radial gradient disc (inner->outer) drawn big for smooth banding."""
    steps = steps or r
    for i in range(steps, 0, -1):
        t = i / steps
        col = lerp_color(inner, outer, t)
        pygame.draw.circle(surf, col, (cx, cy), int(r * t))


def _vgrad_poly(big, pts, top, bot):
    """Vertical gradient clipped to a polygon (in big-pixel coords)."""
    ys = [p[1] for p in pts]
    y0, y1 = min(ys), max(ys)
    band = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    for y in range(y0, y1 + 1):
        t = (y - y0) / max(1, y1 - y0)
        pygame.draw.line(band, lerp_color(top, bot, t), (0, y),
                         (big.get_width(), y))
    mask = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), pts)
    band.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    big.blit(band, (0, 0))


def _contact_shadow(big, cx, cy, rx, ry):
    """Faint dark ellipse under an object so it 'sits' on the plate.
    Shared grounding treatment across the whole family."""
    sh = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (0, 0, 0, 95),
                        pygame.Rect(cx - rx, cy - ry, rx * 2, ry * 2))
    big.blit(sh, (0, 0))


def _spec(big, cx, cy, r, alpha=210):
    """Shared top-left specular pinprick."""
    s = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.circle(s, (255, 255, 255, alpha), (cx, cy), r)
    big.blit(s, (0, 0))


def _outline_poly(big, pts, color, w):
    pygame.draw.polygon(big, color, pts, width=w)


# Each builder draws into a fresh scratch in big-pixel units and returns it.

def emblem_triple():
    big = _scratch()
    cx = cy = N * SS // 2
    r = int(10.5 * SS)
    _contact_shadow(big, cx, cy + int(8.5 * SS), int(8.5 * SS), int(2.4 * SS))
    # Coin body: dark rim, gold radial fill warm at the top-left key light.
    pygame.draw.circle(big, (120, 78, 0), (cx, cy), r + int(0.8 * SS))
    # Radial gold biased toward the key light.
    kx = cx + int(KEY[0] * r * 0.45)
    ky = cy + int(KEY[1] * r * 0.45)
    _radial(big, kx, ky, r, (255, 240, 150), COIN_DARK, steps=r)
    # Re-stamp a clean rim ring so the off-centre radial doesn't bleed edges.
    pygame.draw.circle(big, (150, 96, 8), (cx, cy), r, int(1.4 * SS))
    pygame.draw.circle(big, (255, 236, 120), (cx, cy), r - int(2.4 * SS),
                       int(1.0 * SS))
    # Embossed "$": dark shadow offset down-right, gold-cream face on top.
    f = pygame.font.Font(os.path.join(
        os.path.dirname(__file__), "..", "..", "game", "assets",
        "LiberationSans-Bold.ttf"), int(15 * SS))
    sh = f.render("$", True, (110, 70, 0))
    fg = f.render("$", True, (255, 248, 205))
    rct = fg.get_rect(center=(cx, cy))
    big.blit(sh, (rct.x + int(0.9 * SS), rct.y + int(0.9 * SS)))
    big.blit(fg, rct.topleft)
    _spec(big, cx - int(3.6 * SS), cy - int(4.2 * SS), int(1.7 * SS))
    return big


def _horseshoe(big, cx, cy, scale, mega=False):
    """Shared horseshoe geometry for magnet + megamagnet. Crimson U with
    steel poles, top-left key light, dark outline. Returns pole tip x's."""
    R = int(9.5 * SS * scale)        # outer radius of the arc
    INNER = int(4.6 * SS * scale)
    arch_cy = cy - int(1.5 * SS)
    leg_bot = cy + int(9.0 * SS)
    OUT = (70, 8, 12)
    # Outline silhouette: arc circle + leg slab.
    pygame.draw.circle(big, OUT, (cx, arch_cy), R + int(1.3 * SS))
    pygame.draw.rect(big, OUT, (cx - R - int(1.3 * SS), arch_cy,
                                (R + int(1.3 * SS)) * 2,
                                leg_bot - arch_cy + int(1.3 * SS)))
    # Crimson body via vertical gradient masked to arc+legs.
    body_mask = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.circle(body_mask, (255, 255, 255), (cx, arch_cy), R)
    pygame.draw.rect(body_mask, (255, 255, 255),
                     (cx - R, arch_cy, R * 2, leg_bot - arch_cy))
    band = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    top, bot = (250, 92, 80), (150, 14, 24)
    y0, y1 = arch_cy - R, leg_bot
    for y in range(y0, y1 + 1):
        t = (y - y0) / max(1, y1 - y0)
        pygame.draw.line(band, lerp_color(top, bot, t), (0, y),
                         (big.get_width(), y))
    band.blit(body_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(band, (0, 0))
    # Carve the U cavity (transparent overdraw).
    pygame.draw.circle(big, (0, 0, 0, 0), (cx, arch_cy), INNER)
    pygame.draw.rect(big, (0, 0, 0, 0),
                     (cx - INNER, arch_cy, INNER * 2,
                      leg_bot - arch_cy + int(2 * SS)))
    # Glossy sheen arc on the upper-left of the body.
    sheen = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.circle(sheen, (255, 200, 190, 150), (cx, arch_cy),
                       R - int(1.2 * SS), int(1.4 * SS))
    sm = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(sm, (255, 255, 255), [
        (cx - R, arch_cy - R), (cx, arch_cy - R), (cx - R, arch_cy)])
    sheen.blit(sm, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(sheen, (0, 0))
    # Steel pole tips at the base of each leg.
    arm_w = R - INNER
    lx = cx - INNER - arm_w // 2
    rx = cx + INNER + arm_w // 2
    for px in (lx, rx):
        pygame.draw.rect(big, OUT, (px - arm_w // 2 - int(0.8 * SS),
                                    leg_bot - int(1 * SS),
                                    arm_w + int(1.6 * SS), int(5.5 * SS)),
                         border_radius=int(1.5 * SS))
        pygame.draw.rect(big, (188, 200, 224),
                         (px - arm_w // 2, leg_bot - int(0.4 * SS),
                          arm_w, int(4.4 * SS)),
                         border_radius=int(1.2 * SS))
        pygame.draw.rect(big, (240, 248, 255),
                         (px - arm_w // 2 + int(0.6 * SS),
                          leg_bot, arm_w - int(1.2 * SS), int(1.5 * SS)),
                         border_radius=int(0.8 * SS))
    return lx, rx, leg_bot


def emblem_magnet():
    big = _scratch()
    cx = cy = N * SS // 2
    _contact_shadow(big, cx, cy + int(10 * SS), int(8 * SS), int(2.0 * SS))
    lx, rx, leg_bot = _horseshoe(big, cx, cy, 1.0)
    # Two small warm field-spark chevrons radiating from the pole tips.
    for sign, px in ((-1, lx), (1, rx)):
        pygame.draw.lines(big, (255, 225, 120), False, [
            (px, leg_bot + int(5.5 * SS)),
            (px + sign * int(2.0 * SS), leg_bot + int(7.0 * SS)),
            (px, leg_bot + int(8.5 * SS)),
        ], int(1.4 * SS))
    _spec(big, cx - int(5 * SS), cy - int(7 * SS), int(1.6 * SS))
    return big


def emblem_megamagnet():
    big = _scratch()
    cx = cy = N * SS // 2
    _contact_shadow(big, cx, cy + int(10 * SS), int(8.6 * SS), int(2.1 * SS))
    lx, rx, leg_bot = _horseshoe(big, cx, cy, 1.08, mega=True)
    # Copper coil hint on each leg — distinguishes from plain magnet.
    for px in (lx, rx):
        for i in range(2):
            wy = cy + int((1.5 + i * 2.6) * SS)
            pygame.draw.line(big, (210, 120, 50),
                             (px - int(2.6 * SS), wy),
                             (px + int(2.6 * SS), wy), int(1.3 * SS))
            pygame.draw.line(big, (255, 220, 160),
                             (px - int(2.0 * SS), wy - int(0.5 * SS)),
                             (px + int(1.0 * SS), wy - int(0.5 * SS)),
                             int(0.7 * SS))
    # Cyan discharge balls + bright "++" upgrade badge bottom-right.
    for px in (lx, rx):
        by = leg_bot + int(6.5 * SS)
        gl = pygame.Surface(big.get_size(), pygame.SRCALPHA)
        for r in range(int(4 * SS), 0, -1):
            a = int(150 * (1 - r / (4 * SS) * 0.8))
            pygame.draw.circle(gl, (130, 210, 255, a), (px, by), r)
        big.blit(gl, (0, 0))
        pygame.draw.circle(big, (255, 240, 150), (px, by), int(1.8 * SS))
        pygame.draw.circle(big, (255, 255, 245), (px, by), int(0.9 * SS))
    f = pygame.font.Font(os.path.join(
        os.path.dirname(__file__), "..", "..", "game", "assets",
        "LiberationSans-Bold.ttf"), int(9 * SS))
    sh = f.render("++", True, (60, 30, 8))
    plus = f.render("++", True, (255, 222, 80))
    bx = N * SS - plus.get_width() - int(1 * SS)
    by = int(0.5 * SS)
    big.blit(sh, (bx + int(0.8 * SS), by + int(0.8 * SS)))
    big.blit(plus, (bx, by))
    _spec(big, cx - int(5 * SS), cy - int(7.5 * SS), int(1.6 * SS))
    return big


def emblem_slowmo():
    big = _scratch()
    cx = cy = N * SS // 2
    R = int(10.5 * SS)
    _contact_shadow(big, cx, cy + int(9 * SS), int(8.5 * SS), int(2.2 * SS))
    # Purple metallic bezel: dark ring -> bright bevel -> deep face.
    pygame.draw.circle(big, (28, 6, 50), (cx, cy), R + int(1.2 * SS))
    pygame.draw.circle(big, (200, 150, 255), (cx, cy), R)
    pygame.draw.circle(big, (120, 64, 190), (cx, cy), R - int(1.6 * SS))
    # Face radial, brighter top-left.
    kx, ky = cx - int(2.4 * SS), cy - int(2.8 * SS)
    _radial(big, kx, ky, R - int(2.6 * SS), (88, 36, 132), (40, 10, 70),
            steps=R)
    pygame.draw.circle(big, (52, 16, 86), (cx, cy), R - int(2.6 * SS),
                       int(1.0 * SS))
    # Tick marks: 4 major + minors.
    for i in range(12):
        ang = math.pi * 2 * i / 12 - math.pi / 2
        major = (i % 3 == 0)
        ro = R - int(2.8 * SS)
        ri = ro - int((3.0 if major else 1.8) * SS)
        col = (235, 205, 255) if major else (160, 120, 205)
        pygame.draw.line(big, col,
                         (cx + math.cos(ang) * ro, cy + math.sin(ang) * ro),
                         (cx + math.cos(ang) * ri, cy + math.sin(ang) * ri),
                         int((1.6 if major else 1.0) * SS))
    # Hour hand to ~10 o'clock, minute to 12 — frozen "slow" pose.
    ha = math.radians(-120)
    pygame.draw.line(big, (250, 230, 255), (cx, cy),
                     (cx + math.cos(ha) * int(4 * SS),
                      cy + math.sin(ha) * int(4 * SS)), int(2.2 * SS))
    pygame.draw.line(big, (210, 170, 255), (cx, cy),
                     (cx, cy - int(6 * SS)), int(1.6 * SS))
    # Amber sweep hand for drama.
    sa = math.radians(35)
    pygame.draw.line(big, (255, 190, 70), (cx, cy),
                     (cx + math.cos(sa) * int(5.5 * SS),
                      cy + math.sin(sa) * int(5.5 * SS)), int(1.0 * SS))
    pygame.draw.circle(big, (255, 240, 255), (cx, cy), int(1.6 * SS))
    _spec(big, cx - int(4.2 * SS), cy - int(4.6 * SS), int(2.0 * SS))
    return big


def emblem_kfc():
    """KFC bucket: white-and-red striped tub matching the in-world bucket
    metaphor, with the in-world logo's red brand colour. (The vendored JPG
    logo doesn't read at 24px, so we elevate to a clean striped bucket.)"""
    big = _scratch()
    cx = cy = N * SS // 2
    RED = (208, 22, 24)
    RED_D = (150, 10, 14)
    top_w = int(10.5 * SS)
    bot_w = int(7.5 * SS)
    top_y = cy - int(8.0 * SS)
    bot_y = cy + int(9.5 * SS)
    _contact_shadow(big, cx, bot_y + int(1.5 * SS), bot_w + int(1.5 * SS),
                    int(2.0 * SS))
    body = [(cx - top_w, top_y), (cx + top_w, top_y),
            (cx + bot_w, bot_y), (cx - bot_w, bot_y)]
    out = [(cx - top_w - int(1.2 * SS), top_y - int(0.6 * SS)),
           (cx + top_w + int(1.2 * SS), top_y - int(0.6 * SS)),
           (cx + bot_w + int(1.0 * SS), bot_y + int(1.0 * SS)),
           (cx - bot_w - int(1.0 * SS), bot_y + int(1.0 * SS))]
    pygame.draw.polygon(big, (70, 6, 8), out)
    _vgrad_poly(big, body, (236, 60, 56), RED_D)
    # Vertical white bucket stripes (classic KFC tub), clipped to the body.
    stripes = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    n = 4
    for i in range(n):
        sx = cx - top_w + int((i + 0.5) * (2 * top_w / n))
        pygame.draw.line(stripes, (250, 245, 240, 235),
                         (sx, top_y + int(1.5 * SS)),
                         (int(cx + (sx - cx) * (bot_w / top_w)),
                          bot_y - int(0.5 * SS)), int(2.6 * SS))
    smask = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(smask, (255, 255, 255), body)
    stripes.blit(smask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(stripes, (0, 0))
    # Red rim band at the top (the lid lip).
    pygame.draw.rect(big, RED, (cx - top_w - int(1.5 * SS),
                                top_y - int(2.8 * SS),
                                (top_w + int(1.5 * SS)) * 2, int(3.2 * SS)),
                     border_radius=int(1.2 * SS))
    pygame.draw.rect(big, (245, 110, 95),
                     (cx - top_w, top_y - int(2.4 * SS),
                      top_w * 2, int(1.0 * SS)),
                     border_radius=int(0.6 * SS))
    # Three drumstick-tops poking out of the tub.
    for dxp, dyp, rr in ((-int(5*SS), -int(4.0*SS), int(3.0*SS)),
                         (int(5*SS), -int(3.6*SS), int(3.0*SS)),
                         (0, -int(5.6*SS), int(3.2*SS))):
        pygame.draw.circle(big, (172, 112, 56), (cx + dxp, top_y + dyp), rr)
        pygame.draw.circle(big, (214, 158, 96),
                           (cx + dxp - int(0.8*SS), top_y + dyp - int(0.8*SS)),
                           int(rr * 0.55))
        pygame.draw.circle(big, (245, 240, 235),
                           (cx + dxp, top_y + dyp + rr - int(0.4*SS)),
                           int(1.0 * SS))  # bone tip
    _spec(big, cx - int(5 * SS), top_y + int(2 * SS), int(1.6 * SS))
    return big


def emblem_ghost():
    big = _scratch()
    cx = N * SS // 2
    hr = int(9.0 * SS)
    gcy = N * SS // 2 - int(2.5 * SS)
    body_y2 = gcy + int(7.0 * SS)
    _contact_shadow(big, cx, body_y2 + int(6 * SS), int(7 * SS),
                    int(1.6 * SS))
    # Single perimeter: head arc -> sides -> scalloped skirt.
    perim = []
    for i in range(33):
        th = math.pi - i * math.pi / 32
        perim.append((cx + hr * math.cos(th), gcy - hr * math.sin(th)))
    perim.append((cx + hr, body_y2))
    bump_y = body_y2 + int(4.5 * SS)
    ind_y = body_y2 + int(1.2 * SS)
    xl, xr = cx - hr, cx + hr
    span = xr - xl
    scal = [(xl + i * span / 6,
             body_y2 if i in (0, 6) else (bump_y if i % 2 == 1 else ind_y))
            for i in range(7)]
    perim.extend(reversed(scal))
    perim.append((cx - hr, gcy))
    # Dark hairline outline then holographic gradient fill.
    pygame.draw.polygon(big, (20, 24, 60), perim)
    mask = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255), perim)
    # diagonal pearl gradient
    stops = [(240, 215, 255), (255, 220, 240), (210, 240, 255),
             (215, 255, 235), (245, 245, 220)]
    grad = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    W = big.get_width()
    diag = W * 2
    for y in range(big.get_height()):
        for seg in range(1):
            pass
    # cheap diagonal: per-row blit of a strip
    strip = pygame.Surface((diag, 1), pygame.SRCALPHA)
    for xx in range(diag):
        t = xx / (diag - 1) * (len(stops) - 1)
        i = min(int(t), len(stops) - 2)
        u = t - i
        c = lerp_color(stops[i], stops[i + 1], u)
        strip.set_at((xx, 0), (*c, 255))
    for y in range(big.get_height()):
        grad.blit(strip, (0, y), area=pygame.Rect(y, 0, W, 1))
    # shrink fill 1px inside outline
    inner_mask = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(inner_mask, (255, 255, 255),
                        [(cx + (p[0] - cx) * 0.93, gcy + (p[1] - gcy) * 0.93)
                         for p in perim])
    grad.blit(inner_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(grad, (0, 0))
    # Upper sheen.
    sh = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (255, 255, 255, 70),
                        pygame.Rect(cx - int(6 * SS), gcy - int(7 * SS),
                                    int(8 * SS), int(7 * SS)))
    big.blit(sh, (0, 0))
    # Eyes.
    for ex in (cx - int(3.4 * SS), cx + int(3.4 * SS)):
        pygame.draw.circle(big, (252, 254, 255), (ex, gcy - int(0.5 * SS)),
                           int(2.6 * SS))
        pygame.draw.circle(big, (48, 70, 150),
                           (ex + int(0.7 * SS), gcy), int(1.6 * SS))
        pygame.draw.circle(big, (255, 255, 255),
                           (ex - int(0.5 * SS), gcy - int(1.2 * SS)),
                           int(0.7 * SS))
    return big


def _mush_velvet(big, cx, cap_cy, cap_w, cap_h, wide):
    """Shared velvet-mushroom rendering (cap + spots) for grow/shrink.
    `wide` flattens the parasol for the shrink silhouette."""
    OUT = (60, 15, 25)
    if wide:
        outer = pygame.Rect(cx - cap_w, cap_cy - cap_h, cap_w * 2, cap_h * 2)
        pygame.draw.ellipse(big, OUT, outer)
        inn = outer.inflate(-int(2 * SS), -int(2 * SS))
        _vgrad_poly_ellipse(big, inn, MUSH_CAP2, MUSH_CAP)
    else:
        pts_out = [(cx, cap_cy - cap_h),
                   (cx + cap_w, cap_cy + cap_h - int(2 * SS)),
                   (cx + int(cap_w * 1.1), cap_cy + cap_h),
                   (cx - int(cap_w * 1.1), cap_cy + cap_h),
                   (cx - cap_w, cap_cy + cap_h - int(2 * SS))]
        pygame.draw.polygon(big, OUT, pts_out)
        pts_in = [(cx, cap_cy - cap_h + int(1.5 * SS)),
                  (cx + cap_w - int(1.5 * SS), cap_cy + cap_h - int(3 * SS)),
                  (cx + int(cap_w * 1.0), cap_cy + cap_h - int(1.5 * SS)),
                  (cx - int(cap_w * 1.0), cap_cy + cap_h - int(1.5 * SS)),
                  (cx - cap_w + int(1.5 * SS), cap_cy + cap_h - int(3 * SS))]
        _vgrad_poly(big, pts_in, MUSH_CAP2, MUSH_CAP)


def _vgrad_poly_ellipse(big, rect, top, bot):
    band = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    for y in range(rect.top, rect.bottom):
        t = (y - rect.top) / max(1, rect.height)
        pygame.draw.line(band, lerp_color(top, bot, t), (0, y),
                         (big.get_width(), y))
    m = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.ellipse(m, (255, 255, 255), rect)
    band.blit(m, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(band, (0, 0))


def emblem_grow():
    """Tall velvet witch-hat cone + ivory stem (matches in-world grow)."""
    big = _scratch()
    cx = N * SS // 2
    peak_y = int(2.0 * SS)
    base_y = int(15.5 * SS)
    half_w = int(8.5 * SS)
    _contact_shadow(big, cx, int(23.5 * SS), int(7 * SS), int(1.8 * SS))
    OUT = (60, 15, 25)
    cone_out = [(cx, peak_y - int(1 * SS)),
                (cx + half_w + int(1 * SS), base_y),
                (cx - half_w - int(1 * SS), base_y)]
    pygame.draw.polygon(big, OUT, cone_out)
    cone_in = [(cx, peak_y + int(0.5 * SS)),
               (cx + half_w - int(1 * SS), base_y - int(1 * SS)),
               (cx - half_w + int(1 * SS), base_y - int(1 * SS))]
    _vgrad_poly(big, cone_in, MUSH_CAP2, MUSH_CAP)
    # Left-side pink highlight sliver (key light).
    pygame.draw.polygon(big, (205, 95, 110), [
        (cx - int(0.5 * SS), peak_y + int(2 * SS)),
        (cx - int(3.5 * SS), base_y - int(2 * SS)),
        (cx - int(1.0 * SS), base_y - int(2 * SS))])
    # Scalloped rim curls.
    n = 5
    for i in range(n):
        rcx = cx - half_w + int((i + 0.5) * (2 * half_w / n))
        rr = int(half_w / n)
        pygame.draw.circle(big, MUSH_CAP, (rcx, base_y), rr)
        pygame.draw.circle(big, OUT, (rcx, base_y), rr, int(1.0 * SS))
        pygame.draw.circle(big, (220, 120, 130),
                           (rcx - rr // 3, base_y - rr // 3), max(1, rr // 3))
    # Ivory bulbed stem.
    stem = [(cx - int(2.4 * SS), base_y),
            (cx + int(2.4 * SS), base_y),
            (cx + int(3.0 * SS), int(21 * SS)),
            (cx, int(23 * SS)),
            (cx - int(3.0 * SS), int(21 * SS))]
    pygame.draw.polygon(big, MUSH_STEM, stem)
    pygame.draw.polygon(big, (150, 120, 90), stem, int(1.0 * SS))
    pygame.draw.line(big, (255, 250, 230),
                     (cx - int(1 * SS), base_y + int(1 * SS)),
                     (cx - int(1 * SS), int(20.5 * SS)), int(1.2 * SS))
    # Cream spots.
    for fx, fy in ((0.0, 6), (2.2, 9.5), (-1.6, 11.5)):
        sx = cx + int(fx * SS)
        sy = peak_y + int(fy * SS)
        pygame.draw.circle(big, (195, 165, 110), (sx, sy), int(1.7 * SS))
        pygame.draw.circle(big, MUSH_SPOT, (sx, sy), int(1.3 * SS))
        pygame.draw.circle(big, (255, 250, 220),
                           (sx - int(0.5 * SS), sy - int(0.5 * SS)),
                           int(0.6 * SS))
    return big


def emblem_shrink():
    """Squat red-velvet mushroom: WIDE flat parasol + short flared stem.
    Same fungal palette as grow, opposite silhouette (low + wide)."""
    big = _scratch()
    cx = N * SS // 2
    cap_cy = int(10 * SS)
    cap_w = int(11 * SS)
    cap_h = int(5.0 * SS)
    _contact_shadow(big, cx, int(22 * SS), int(7.5 * SS), int(1.8 * SS))
    OUT = (60, 15, 25)
    # Flared stem.
    stem = [(cx - int(3.0 * SS), cap_cy + int(2 * SS)),
            (cx + int(3.0 * SS), cap_cy + int(2 * SS)),
            (cx + int(4.6 * SS), int(20.5 * SS)),
            (cx - int(4.6 * SS), int(20.5 * SS))]
    pygame.draw.polygon(big, MUSH_STEM, stem)
    pygame.draw.polygon(big, (150, 120, 90), stem, int(1.0 * SS))
    pygame.draw.line(big, (255, 250, 230),
                     (cx - int(1.5 * SS), cap_cy + int(3 * SS)),
                     (cx - int(2.2 * SS), int(20 * SS)), int(1.2 * SS))
    # Wide flat parasol disc.
    outer = pygame.Rect(cx - cap_w, cap_cy - cap_h, cap_w * 2, cap_h * 2)
    pygame.draw.ellipse(big, OUT, outer)
    inn = outer.inflate(-int(2 * SS), -int(2 * SS))
    _vgrad_poly_ellipse(big, inn, MUSH_CAP2, MUSH_CAP)
    # Under-cap shadow band.
    pygame.draw.ellipse(big, (90, 18, 30),
                        pygame.Rect(cx - cap_w + int(1.5 * SS),
                                    cap_cy + int(0.5 * SS),
                                    (cap_w - int(1.5 * SS)) * 2,
                                    int(3.5 * SS)))
    # Cream spots across the disc.
    for fx, fy in ((-4.5, -2.0), (0.0, -3.0), (4.0, -1.8), (2.0, 0.5)):
        sx = cx + int(fx * SS)
        sy = cap_cy + int(fy * SS)
        pygame.draw.circle(big, (195, 165, 110), (sx, sy), int(1.6 * SS))
        pygame.draw.circle(big, MUSH_SPOT, (sx, sy), int(1.2 * SS))
        pygame.draw.circle(big, (255, 250, 220),
                           (sx - int(0.5 * SS), sy - int(0.5 * SS)),
                           int(0.6 * SS))
    # Tiny down-arrows flanking it to reinforce "shrink".
    for sign in (-1, 1):
        ax = cx + sign * int(12 * SS)
        ay = cap_cy
        pygame.draw.polygon(big, (120, 170, 235), [
            (ax - int(1.6 * SS), ay - int(1.5 * SS)),
            (ax + int(1.6 * SS), ay - int(1.5 * SS)),
            (ax, ay + int(2.0 * SS))])
    _spec(big, cx - int(4 * SS), cap_cy - int(2.5 * SS), int(1.5 * SS))
    return big


def emblem_reverse():
    """Holographic squircle panel + up/down purple chevrons (matches the
    in-world reverse pickup palette)."""
    big = _scratch()
    n = N * SS
    rad = int(7 * SS)
    panel = pygame.Rect(int(2.5 * SS), int(2.5 * SS), n - int(5 * SS),
                        n - int(5 * SS))
    _contact_shadow(big, n // 2, panel.bottom + int(1.5 * SS),
                    int(9 * SS), int(1.8 * SS))
    pygame.draw.rect(big, (20, 12, 55), panel, border_radius=rad)
    pygame.draw.rect(big, (195, 175, 240), panel.inflate(-int(2*SS), -int(2*SS)),
                     border_radius=rad - int(1 * SS))
    inner = panel.inflate(-int(5 * SS), -int(5 * SS))
    # Holographic diagonal fill.
    grad = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    hs = [(240, 220, 240), (210, 220, 245), (215, 240, 240)]
    for y in range(inner.top, inner.bottom):
        for_band = y
    strip = pygame.Surface((inner.width + inner.height, 1), pygame.SRCALPHA)
    L = inner.width + inner.height
    for xx in range(L):
        t = xx / (L - 1) * 2
        if t < 1:
            c = lerp_color(hs[0], hs[1], t)
        else:
            c = lerp_color(hs[1], hs[2], t - 1)
        strip.set_at((xx, 0), (*c, 255))
    gm = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.rect(gm, (255, 255, 255), inner, border_radius=rad - int(2*SS))
    for y in range(inner.top, inner.bottom):
        grad.blit(strip, (inner.left, y),
                  area=pygame.Rect(y - inner.top, 0, inner.width, 1))
    grad.blit(gm, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(grad, (0, 0))
    # Two chevrons: up (left) + down (right).
    cy = n // 2
    A_TOP, A_MID, A_BOT, A_OUT = (175,100,230), (130,55,200), (75,25,145), (35,10,70)
    def chevron(colx, up):
        sw = int(2.4 * SS)
        hw = int(5.6 * SS)
        top = inner.top + int(1.5 * SS)
        bot = inner.bottom - int(1.5 * SS)
        head_h = (bot - top) * 42 // 100
        if up:
            pts = [(colx, top),
                   (colx + hw, top + head_h), (colx + sw, top + head_h),
                   (colx + sw, bot), (colx - sw, bot),
                   (colx - sw, top + head_h), (colx - hw, top + head_h)]
        else:
            pts = [(colx, bot),
                   (colx - hw, bot - head_h), (colx - sw, bot - head_h),
                   (colx - sw, top), (colx + sw, top),
                   (colx + sw, bot - head_h), (colx + hw, bot - head_h)]
        pygame.draw.polygon(big, A_OUT,
                            [(p[0] + (1 if i else 0), p[1]) for i, p in enumerate(pts)])
        pygame.draw.polygon(big, A_OUT, pts)
        _vgrad_poly(big, pts, A_TOP, A_BOT)
    chevron(inner.left + inner.width // 4, up=True)
    chevron(inner.right - inner.width // 4, up=False)
    # Top frame highlight.
    pygame.draw.line(big, (255, 255, 255),
                     (panel.left + rad, panel.top + int(1.2 * SS)),
                     (panel.right - rad, panel.top + int(1.2 * SS)),
                     int(1.0 * SS))
    return big


def emblem_rail():
    """Minecart on a rail: dark iron wagon with ore load + two wheels on a
    short rail line. Higher-fidelity than the flat production cart."""
    big = _scratch()
    cx = N * SS // 2
    cy = N * SS // 2
    _contact_shadow(big, cx, cy + int(9.5 * SS), int(9 * SS), int(1.6 * SS))
    # Rail line + ties.
    rail_y = cy + int(8.5 * SS)
    for ty in range(-int(8 * SS), int(8 * SS), int(3.2 * SS)):
        pygame.draw.line(big, (90, 70, 55),
                         (cx + ty, rail_y - int(0.5 * SS)),
                         (cx + ty, rail_y + int(2.0 * SS)), int(1.6 * SS))
    pygame.draw.line(big, (190, 178, 160), (cx - int(10 * SS), rail_y),
                     (cx + int(10 * SS), rail_y), int(1.6 * SS))
    # Cart body — trapezoid tub, dark iron with warm rim.
    top_y = cy - int(3.5 * SS)
    bot_y = cy + int(4.5 * SS)
    tw = int(8.5 * SS)
    bw = int(6.5 * SS)
    body = [(cx - tw, top_y), (cx + tw, top_y),
            (cx + bw, bot_y), (cx - bw, bot_y)]
    pygame.draw.polygon(big, (28, 24, 22),
                        [(cx - tw - int(1*SS), top_y - int(0.6*SS)),
                         (cx + tw + int(1*SS), top_y - int(0.6*SS)),
                         (cx + bw + int(0.8*SS), bot_y + int(0.8*SS)),
                         (cx - bw - int(0.8*SS), bot_y + int(0.8*SS))])
    _vgrad_poly(big, body, (96, 66, 44), (44, 30, 22))
    # Iron band + rivets.
    pygame.draw.line(big, (24, 20, 18),
                     (cx - tw + int(1*SS), top_y + int(3*SS)),
                     (cx + tw - int(1*SS), top_y + int(3*SS)), int(1.4 * SS))
    for rx in (-tw + int(1.5*SS), tw - int(2.5*SS)):
        pygame.draw.circle(big, (150, 130, 110),
                           (cx + rx, top_y + int(3 * SS)), int(0.8 * SS))
    # Amber ore/gold load mounded at the top.
    for dxp, rr in ((-int(3.5*SS), int(2.6*SS)), (int(3.5*SS), int(2.4*SS)),
                    (0, int(3.0*SS))):
        pygame.draw.circle(big, (255, 200, 60),
                           (cx + dxp, top_y - int(0.5 * SS)), rr)
        pygame.draw.circle(big, (255, 235, 150),
                           (cx + dxp - int(0.8*SS), top_y - int(1.3*SS)),
                           int(rr * 0.5))
    # Wheels.
    for wx in (cx - int(4.5 * SS), cx + int(4.5 * SS)):
        pygame.draw.circle(big, (20, 18, 16), (wx, bot_y + int(2.2 * SS)),
                           int(2.8 * SS))
        pygame.draw.circle(big, (120, 110, 100), (wx, bot_y + int(2.2 * SS)),
                           int(2.8 * SS), int(1.0 * SS))
        pygame.draw.circle(big, (180, 170, 158), (wx, bot_y + int(2.2 * SS)),
                           int(1.0 * SS))
    _spec(big, cx - int(5 * SS), top_y + int(4 * SS), int(1.4 * SS))
    return big


BUILDERS = {
    "triple": emblem_triple, "magnet": emblem_magnet,
    "megamagnet": emblem_megamagnet, "slowmo": emblem_slowmo,
    "kfc": emblem_kfc, "ghost": emblem_ghost, "shrink": emblem_shrink,
    "grow": emblem_grow, "reverse": emblem_reverse, "rail": emblem_rail,
}


def new_emblem(kind, target):
    big = BUILDERS[kind]()
    return _down(big, target)


# ── Sheet composition ────────────────────────────────────────────────────────

PLATE = 32          # real plate size
ICON_DRAW = 24      # inflate(-8,-8) inner area (production)
ZOOM = ICON_DRAW * 6


def plate_with(icon_surf):
    """Render the real 32x32 slate plate and blit an icon centred in its
    inflate(-8,-8) inner area, returning a surface that includes the glow pad."""
    full = pygame.Surface((PLATE + _NA_PAD * 2, PLATE + _NA_PAD * 2),
                          pygame.SRCALPHA)
    rect = pygame.Rect(_NA_PAD, _NA_PAD, PLATE, PLATE)
    from game.hud import _ENERGY_FULL
    _na_plate(full, rect, cut=7, round_r=7, accent=_ENERGY_FULL, glow=False)
    inner = rect.inflate(-8, -8)
    full.blit(icon_surf, icon_surf.get_rect(center=inner.center))
    return full


def main():
    pygame.font.init()
    label_f = pygame.font.Font(os.path.join(
        os.path.dirname(__file__), "..", "..", "game", "assets",
        "LiberationSans-Bold.ttf"), 20)
    small_f = pygame.font.Font(os.path.join(
        os.path.dirname(__file__), "..", "..", "game", "assets",
        "LiberationSans-Bold.ttf"), 16)
    title_f = pygame.font.Font(os.path.join(
        os.path.dirname(__file__), "..", "..", "game", "assets",
        "LiberationSans-Bold.ttf"), 30)

    BG = (24, 26, 30)
    cols = 2
    rows = len(KINDS)
    col_w = 470
    row_h = 168
    pad = 28
    top_strip_h = 150
    sheet_w = cols * col_w + pad * 3
    sheet_h = top_strip_h + rows * row_h + pad * 3 + 60
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill(BG)

    # Title.
    t = title_f.render("Buff Emblem Family — Round 1", True, (245, 220, 150))
    sheet.blit(t, (pad, 16))
    sub = small_f.render(
        "Shared language: 6x supersample, top-left key light + single "
        "specular, uniform outline + contact shadow.",
        True, (170, 175, 185))
    sheet.blit(sub, (pad, 52))

    # Top strip: CURRENT production emblems on the real plate.
    strip_y = 84
    cur_lbl = small_f.render("CURRENT (production)", True, (230, 130, 120))
    sheet.blit(cur_lbl, (pad, strip_y))
    gx = pad
    gy = strip_y + 26
    for kind in KINDS:
        full = pygame.Surface((PLATE + _NA_PAD * 2, PLATE + _NA_PAD * 2),
                              pygame.SRCALPHA)
        rect = pygame.Rect(_NA_PAD, _NA_PAD, PLATE, PLATE)
        from game.hud import _ENERGY_FULL
        _na_plate(full, rect, cut=7, round_r=7, accent=_ENERGY_FULL, glow=False)
        _draw_buff_icon(full, rect.inflate(-8, -8), kind)
        sheet.blit(full, (gx, gy))
        lab = pygame.font.Font(os.path.join(
            os.path.dirname(__file__), "..", "..", "game", "assets",
            "LiberationSans-Bold.ttf"), 12).render(kind, True, (160, 165, 175))
        sheet.blit(lab, (gx + (PLATE + _NA_PAD * 2 - lab.get_width()) // 2,
                         gy + PLATE + _NA_PAD * 2 + 2))
        gx += PLATE + _NA_PAD * 2 + 8

    # Divider.
    div_y = strip_y + top_strip_h
    pygame.draw.line(sheet, (60, 64, 70), (pad, div_y),
                     (sheet_w - pad, div_y), 2)
    new_lbl = label_f.render("NEW (display size  +  6x zoom)", True,
                             (150, 220, 160))
    sheet.blit(new_lbl, (pad, div_y + 10))

    grid_top = div_y + 44
    for i, kind in enumerate(KINDS):
        col = i % cols
        row = i // cols
        # two columns each hold half the list
    # Lay out as a single column pair: left col first 5, right col next 5.
    half = (rows + 1) // 2
    for i, kind in enumerate(KINDS):
        col = 0 if i < half else 1
        row = i % half
        cell_x = pad + col * (col_w + pad)
        cell_y = grid_top + row * row_h
        # Cell background.
        pygame.draw.rect(sheet, (32, 35, 40),
                         (cell_x, cell_y, col_w, row_h - 14), border_radius=10)
        # Display-size on plate (left of cell).
        full = plate_with(new_emblem(kind, ICON_DRAW))
        plate_x = cell_x + 18
        plate_y = cell_y + (row_h - 14 - full.get_height()) // 2
        sheet.blit(full, (plate_x, plate_y))
        ds_lbl = small_f.render("32px", True, (150, 155, 165))
        sheet.blit(ds_lbl, (plate_x + (full.get_width() - ds_lbl.get_width()) // 2,
                            plate_y + full.get_height() + 2))
        # Zoom (right of cell).
        zoom = new_emblem(kind, ZOOM)
        zx = cell_x + col_w - ZOOM - 24
        zy = cell_y + (row_h - 14 - ZOOM) // 2
        pygame.draw.rect(sheet, (18, 20, 24),
                         (zx - 6, zy - 6, ZOOM + 12, ZOOM + 12),
                         border_radius=8)
        sheet.blit(zoom, (zx, zy))
        # Kind name.
        nm = label_f.render(kind, True, (240, 235, 220))
        sheet.blit(nm, (cell_x + 110, cell_y + 16))

    out = os.path.join(os.path.dirname(__file__), "round_1.png")
    pygame.image.save(sheet, out)
    print("saved", out, sheet.get_size())


if __name__ == "__main__":
    main()
