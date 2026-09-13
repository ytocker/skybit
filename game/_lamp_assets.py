"""Procedural Faceted-Crystal lamp asset for the Genie powerup pickup
icon. Cyan body + cyan handle gem variant — the design picked from
the multi-colour exploration sheet in
`docs/screenshots/genie_designs/`.

Consolidates the relevant drawing helpers from
`tools/render_a1_lamp_variants.py:draw_lamp_4_faceted` so the runtime
never imports from `tools/` (which is stripped from the pygbag deploy
bundle and also runs `pygame.display.set_mode` at import time).

Public API:
    get_lamp_sprite(target_height: int = 52) -> pygame.Surface
        Returns a cached, smoothscaled cyan Faceted-Crystal lamp
        sprite ready to blit. The sprite aspect ratio is preserved
        (target_w ≈ target_height * W / H ≈ 56 for the default).
"""
from __future__ import annotations

import math
import random

import pygame


# ── canvas + supersample ────────────────────────────────────────────
SS = 8
W, H = 112, 104
PW, PH = W * SS, H * SS
NEAR_BLK = (16, 12, 8)
SKY_HOLE = (60, 95, 130)


def s(v):
    return int(v * SS)


def _aa_circle(surf, color, cx, cy, r):
    pygame.draw.circle(surf, color, (int(cx), int(cy)), int(r))


def _ell(surf, color, cx, cy, w, h):
    pygame.draw.ellipse(surf, color,
                        (int(cx - w / 2), int(cy - h / 2),
                         int(w), int(h)))


def _filled_poly(surf, color, pts):
    pygame.draw.polygon(surf, color, [(int(x), int(y)) for x, y in pts])


def _gem_diamond(surf, cx, cy, r, color, hi_color):
    pygame.draw.polygon(surf, NEAR_BLK,
                        [(cx, cy - r - s(1) // 2),
                         (cx + r + s(1) // 2, cy),
                         (cx, cy + r + s(1) // 2),
                         (cx - r - s(1) // 2, cy)])
    pygame.draw.polygon(surf, color,
                        [(cx, cy - r), (cx + r, cy),
                         (cx, cy + r), (cx - r, cy)])
    pygame.draw.polygon(surf, hi_color,
                        [(cx, cy - r),
                         (cx - int(r * 0.55), cy),
                         (cx - int(r * 0.25),
                          cy - int(r * 0.35))])
    pygame.draw.circle(surf, (255, 255, 255),
                       (int(cx - r * 0.3), int(cy - r * 0.5)),
                       max(1, int(r * 0.22)))


def _gem_round(surf, cx, cy, r, color, hi_color):
    pygame.draw.circle(surf, NEAR_BLK, (cx, cy), int(r + s(1) // 2))
    pygame.draw.circle(surf, color, (cx, cy), int(r))
    pygame.draw.circle(surf, hi_color,
                       (int(cx - r * 0.32), int(cy - r * 0.32)),
                       max(1, int(r * 0.55)))
    pygame.draw.circle(surf, (255, 255, 255),
                       (int(cx - r * 0.45), int(cy - r * 0.45)),
                       max(1, int(r * 0.22)))


def _smoke_ribbon(surf, ox, oy, palette, n_puffs=14, height_n=42,
                  curl=2.0, start_radius=4):
    for i in range(n_puffs):
        k = i / max(1, n_puffs - 1)
        sway = math.sin(0.6 + i * 0.55) * s(curl) * (0.3 + k)
        x = ox + sway
        y = oy - int(s(height_n) * k)
        rad = max(s(1), int(s(start_radius) * (1 - k * 0.65)))
        alpha = int(235 * (1 - k * 0.78))
        col = palette[min(int(k * len(palette)), len(palette) - 1)]
        puff = pygame.Surface((rad * 2 + 4, rad * 2 + 4),
                              pygame.SRCALPHA)
        pygame.draw.circle(puff, (*col, alpha),
                           (rad + 2, rad + 2), rad)
        surf.blit(puff, (int(x - rad - 2), int(y - rad - 2)))


def _sparkles_around(surf, cx, cy, n=6, radius_n=40,
                     color=(255, 240, 180), rng_seed=11):
    rng = random.Random(rng_seed)
    R = s(radius_n)
    for _ in range(n):
        ang = rng.uniform(-math.pi, math.pi)
        r = rng.uniform(R * 0.7, R)
        sx = cx + math.cos(ang) * r
        sy = cy + math.sin(ang) * r * 0.85
        sr = max(1, rng.randint(s(1) // 2, s(1)))
        cw = max(1, s(1) // 2)
        pygame.draw.line(surf, color,
                         (int(sx - sr * 2), int(sy)),
                         (int(sx + sr * 2), int(sy)), cw)
        pygame.draw.line(surf, color,
                         (int(sx), int(sy - sr * 2)),
                         (int(sx), int(sy + sr * 2)), cw)
        _aa_circle(surf, (255, 255, 255), sx, sy, max(1, sr))


def _lamp_silhouette(cx, cy):
    body_cy = cy + s(6)
    bw = s(54)
    bh = s(24)
    n_vert = 48
    body_pts = []
    for k in range(n_vert):
        t = (k / n_vert) * math.tau - math.pi / 2
        cos_t = math.cos(t)
        sin_t = math.sin(t)
        yk = sin_t * 0.86 if sin_t > 0 else sin_t * 1.0
        x = cx + cos_t * (bw / 2)
        y = body_cy + yk * (bh / 2)
        body_pts.append((x, y))
    spa_x = cx + bw // 2 - s(8)
    spa_y = body_cy - s(1)
    outer_pts = [
        (spa_x - s(4),  spa_y + s(7)),
        (spa_x + s(4),  spa_y + s(3)),
        (spa_x + s(11), spa_y - s(3)),
        (spa_x + s(17), spa_y - s(11)),
        (spa_x + s(21), spa_y - s(19)),
        (spa_x + s(22), spa_y - s(26)),
        (spa_x + s(19), spa_y - s(31)),
    ]
    inner_pts = [
        (spa_x + s(13), spa_y - s(31)),
        (spa_x + s(15), spa_y - s(26)),
        (spa_x + s(16), spa_y - s(19)),
        (spa_x + s(13), spa_y - s(11)),
        (spa_x + s(7),  spa_y - s(3)),
        (spa_x + s(1),  spa_y + s(2)),
        (spa_x - s(4),  spa_y + s(5)),
    ]
    spout_pts = outer_pts + inner_pts
    mouth_x = spa_x + s(16)
    mouth_y = spa_y - s(31)
    return {
        "cx": cx, "cy": cy,
        "body_cy": body_cy,
        "bw": bw, "bh": bh,
        "body_pts": body_pts,
        "spout_pts": spout_pts,
        "outer_pts": outer_pts,
        "inner_pts": inner_pts,
        "spa_x": spa_x, "spa_y": spa_y,
        "mouth_x": mouth_x, "mouth_y": mouth_y,
        "h_cx": cx - bw // 2 - s(4),
        "h_cy": body_cy - s(2),
        "h_w": s(14),
        "h_h": s(24),
        "stem_y": body_cy + bh // 2 - s(2),
        "stem_w": s(20),
        "stem_h": s(3),
        "base_w": s(32),
        "base_h": s(5),
    }


def _paint_lamp_body(big, anc, palette):
    DK, BASE, HI = palette["dk"], palette["base"], palette["hi"]
    SHEEN = palette.get("sheen", (255, 255, 255))
    cx = anc["cx"]
    body_cy = anc["body_cy"]
    bw, bh = anc["bw"], anc["bh"]
    # Body
    shadow_pts = [(x + s(1), y + s(1)) for x, y in anc["body_pts"]]
    _filled_poly(big, NEAR_BLK, shadow_pts)
    _filled_poly(big, DK, anc["body_pts"])
    inner = []
    for x, y in anc["body_pts"]:
        dx = (x - cx) * 0.86
        dy = (y - body_cy) * 0.86
        inner.append((cx + dx, body_cy + dy))
    _filled_poly(big, BASE, inner)
    # Highlight crescent
    pad = s(4)
    arc_rect = (cx - bw // 2 + pad,
                body_cy - bh // 2 + pad,
                bw - 2 * pad, bh - 2 * pad)
    pygame.draw.arc(big, HI, arc_rect,
                    math.radians(195), math.radians(330),
                    max(3, s(1) + 1))
    pygame.draw.arc(big, SHEEN,
                    (arc_rect[0] + s(1), arc_rect[1] + s(1),
                     arc_rect[2] - s(2), arc_rect[3] - s(2)),
                    math.radians(210), math.radians(285),
                    max(2, s(1) - 1))
    _aa_circle(big, SHEEN, cx - s(10), body_cy - s(8), max(2, s(1)))
    # Spout
    sh_pts = [(x + s(1), y + s(1)) for x, y in anc["spout_pts"]]
    _filled_poly(big, NEAR_BLK, sh_pts)
    _filled_poly(big, DK, anc["spout_pts"])
    in_fill = [(x - s(1), y + s(1)) for x, y in anc["outer_pts"]] + \
              [(x + s(2), y) for x, y in anc["inner_pts"]]
    _filled_poly(big, BASE, in_fill)
    spa_x, spa_y = anc["spa_x"], anc["spa_y"]
    pygame.draw.lines(big, HI, False,
                      [(spa_x + s(7),  spa_y - s(3)),
                       (spa_x + s(13), spa_y - s(11)),
                       (spa_x + s(18), spa_y - s(20))],
                      max(2, s(1)))
    pygame.draw.lines(big, SHEEN, False,
                      [(spa_x + s(9),  spa_y - s(5)),
                       (spa_x + s(14), spa_y - s(13))],
                      max(1, s(1) // 2 + 1))
    pygame.draw.lines(big, NEAR_BLK, False,
                      [(spa_x + s(13), spa_y - s(30)),
                       (spa_x + s(16), spa_y - s(29)),
                       (spa_x + s(19), spa_y - s(30))],
                      max(2, s(1)))
    _ell(big, NEAR_BLK, anc["mouth_x"], anc["mouth_y"], s(6), s(2))


def _paint_torus_handle(big, anc, palette, inner_gem=None):
    DK, BASE, HI = palette["dk"], palette["base"], palette["hi"]
    h_cx, h_cy = anc["h_cx"], anc["h_cy"]
    h_w, h_h = anc["h_w"], anc["h_h"]
    HOLE_COLOR = palette.get("hole", SKY_HOLE)
    pygame.draw.ellipse(big, NEAR_BLK,
                        (h_cx - h_w // 2 - s(1),
                         h_cy - h_h // 2 - s(1),
                         h_w + s(2), h_h + s(2)))
    pygame.draw.ellipse(big, DK,
                        (h_cx - h_w // 2, h_cy - h_h // 2, h_w, h_h))
    pygame.draw.ellipse(big, BASE,
                        (h_cx - h_w // 2 + s(1) // 2,
                         h_cy - h_h // 2 + s(1) // 2,
                         h_w - s(1), h_h - s(1)))
    pygame.draw.ellipse(big, HOLE_COLOR,
                        (h_cx - h_w // 2 + s(3),
                         h_cy - h_h // 2 + s(4),
                         h_w - s(6), h_h - s(8)))
    pygame.draw.arc(big, NEAR_BLK,
                    (h_cx - h_w // 2 + s(3),
                     h_cy - h_h // 2 + s(4),
                     h_w - s(6), h_h - s(8)),
                    math.radians(260), math.radians(80),
                    max(3, s(1) + 1))
    pygame.draw.line(big, HI,
                     (h_cx - s(1), h_cy - h_h // 2 + s(1)),
                     (h_cx + s(3), h_cy - h_h // 2 + s(1)),
                     max(2, s(1)))
    pygame.draw.line(big, HI,
                     (h_cx + h_w // 2 - s(2), h_cy + s(2)),
                     (h_cx + h_w // 2 - s(2), h_cy + s(5)),
                     max(2, s(1)))
    if inner_gem is not None:
        gtype, gcx_off, gcy_off, gr, gcol, ghi = inner_gem
        gcx = h_cx + gcx_off
        gcy = h_cy + gcy_off
        if gtype == "diamond":
            _gem_diamond(big, gcx, gcy, gr, gcol, ghi)
        else:
            _gem_round(big, gcx, gcy, gr, gcol, ghi)


def _paint_foot(big, anc, palette, band_colors, extra_layer=None):
    cx = anc["cx"]
    stem_y = anc["stem_y"]
    stem_w, stem_h = anc["stem_w"], anc["stem_h"]
    base_w, base_h = anc["base_w"], anc["base_h"]
    DK = palette["dk"]
    BASE = palette["base"]
    HI = palette["hi"]
    # Stem
    pygame.draw.rect(big, NEAR_BLK,
                     (cx - stem_w // 2 - s(1) // 2, stem_y,
                      stem_w + s(1), stem_h + s(1)),
                     border_radius=s(1))
    pygame.draw.rect(big, DK,
                     (cx - stem_w // 2, stem_y, stem_w, stem_h),
                     border_radius=s(1))
    pygame.draw.rect(big, BASE,
                     (cx - stem_w // 2 + s(1) // 2, stem_y,
                      stem_w - s(1), max(1, stem_h - s(1))),
                     border_radius=s(1))
    base_y = stem_y + stem_h
    pygame.draw.rect(big, NEAR_BLK,
                     (cx - base_w // 2 - s(1) // 2, base_y,
                      base_w + s(1), base_h + s(1)),
                     border_radius=s(1))
    cur_y = base_y
    total_h = base_h
    for col, frac in band_colors:
        h_band = int(total_h * frac)
        pygame.draw.rect(big, col,
                         (cx - base_w // 2, cur_y, base_w, h_band),
                         border_radius=s(1))
        cur_y += h_band
    if extra_layer is not None:
        extra_layer(big, cx, base_y, base_w, base_h)


def _clip_to_body(surf, body_pts):
    mask = pygame.Surface((PW, PH), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255),
                        [(int(x), int(y)) for x, y in body_pts])
    surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)


# ── Cyan Faceted-Crystal palette + render ──────────────────────────
# Picked design from docs/screenshots/genie_designs/. Pale-cyan crystal
# body + cyan-family handle gem + inner-disc so the handle reads as one
# monochrome cyan element rather than swapping to a sapphire contrast
# spot. Stopper finial keeps EMERALD + RUBY-diamond + SAPPHIRE so the
# jewel trio still pops against the cool body.

_CYAN_PAL = {
    "dk":    ( 60, 130, 170),
    "base":  (130, 195, 220),
    "hi":    (220, 245, 255),
    "sheen": (255, 255, 255),
    "hole":  ( 55, 110, 145),
}
_GOLD    = (255, 220, 110)
_GOLD_HI = (255, 245, 175)
_GOLD_DK = (180, 130,  40)
_RUBY,    _RUBY_HI    = (220,  55,  75), (255, 175, 195)
_EMERALD, _EMERALD_HI = ( 70, 175, 110), (180, 240, 200)
_SAPPHIRE,_SAPPHIRE_HI= ( 70, 100, 220), (175, 200, 255)
_CYAN_GEM, _CYAN_GEM_HI = ( 40, 100, 160), (170, 220, 245)
_SMOKE   = [(250, 250, 250), (195, 235, 255), (130, 195, 235),
            ( 75, 145, 200)]


def _render_faceted_cyan(big, cx, cy):
    anc = _lamp_silhouette(cx, cy)

    # Outline glow — subtle dark-navy halo for sky-colour separation
    HALO_COLOR = (28, 40, 70)
    halo_cx = anc["cx"]
    halo_cy = anc["body_cy"]
    sp_cx = anc["spa_x"] + s(8)
    sp_cy = anc["spa_y"] - s(15)
    for scale, alpha in ((1.20, 35), (1.12, 70), (1.05, 115)):
        sub = pygame.Surface((PW, PH), pygame.SRCALPHA)
        body_scaled = [(halo_cx + (x - halo_cx) * scale,
                        halo_cy + (y - halo_cy) * scale)
                       for x, y in anc["body_pts"]]
        spout_scaled = [(sp_cx + (x - sp_cx) * scale,
                         sp_cy + (y - sp_cy) * scale)
                        for x, y in anc["spout_pts"]]
        pygame.draw.polygon(sub, (*HALO_COLOR, alpha),
                            [(int(x), int(y)) for x, y in body_scaled])
        pygame.draw.polygon(sub, (*HALO_COLOR, alpha),
                            [(int(x), int(y)) for x, y in spout_scaled])
        big.blit(sub, (0, 0))

    _paint_lamp_body(big, anc, _CYAN_PAL)

    bw, bh = anc["bw"], anc["bh"]
    body_cy = anc["body_cy"]

    # Cut-crystal facets
    facet_clip = pygame.Surface((PW, PH), pygame.SRCALPHA)

    def draw_facet(fcx, fcy, fw, fh):
        if abs(fcx - cx) + fw // 2 > bw // 2 - s(3):
            return
        if abs(fcy - body_cy) + fh // 2 > bh // 2 - s(2):
            return
        pts = [(fcx, fcy - fh // 2),
               (fcx + fw // 2, fcy),
               (fcx, fcy + fh // 2),
               (fcx - fw // 2, fcy)]
        shadow_tri = [pts[0], pts[1], pts[2]]
        pygame.draw.polygon(facet_clip, (*_CYAN_PAL["dk"], 110),
                            shadow_tri)
        pygame.draw.polygon(facet_clip, (*_CYAN_PAL["sheen"], 250),
                            pts, max(3, s(1) + 1))
        pygame.draw.line(facet_clip, (*_CYAN_PAL["sheen"], 255),
                         pts[3], pts[0], max(2, s(1)))
        pygame.draw.circle(facet_clip, (255, 255, 255, 255),
                           (int(fcx - fw // 5),
                            int(fcy - fh // 5)),
                           max(2, s(1)))

    for j in range(5):
        t = (j + 0.5) / 5
        fx_f = cx - bw // 2 + s(6) + (bw - s(12)) * t
        fy_off = s(2) if j % 2 == 1 else -s(2)
        draw_facet(fx_f, body_cy + fy_off, s(10), s(11))
    draw_facet(cx, body_cy, s(13), s(14))
    _clip_to_body(facet_clip, anc["body_pts"])
    big.blit(facet_clip, (0, 0))

    # Facet treatment on the spout
    spa_x, spa_y = anc["spa_x"], anc["spa_y"]
    for t_frac in (0.3, 0.55, 0.78):
        outer = anc["outer_pts"]
        idx = max(0, min(len(outer) - 2, int(t_frac * (len(outer) - 1))))
        a = outer[idx]
        b = outer[idx + 1]
        mx, my = (a[0] + b[0]) // 2, (a[1] + b[1]) // 2
        ang = math.atan2(b[1] - a[1], b[0] - a[0])
        nx = math.cos(ang + math.pi / 2)
        ny = math.sin(ang + math.pi / 2)
        fcx = mx + nx * s(2)
        fcy = my + ny * s(2)
        pts = [(fcx, fcy - s(2)),
               (fcx + s(2), fcy),
               (fcx, fcy + s(2)),
               (fcx - s(2), fcy)]
        pygame.draw.polygon(big, _CYAN_PAL["sheen"], pts, max(2, s(1)))
        _aa_circle(big, (255, 255, 255),
                   fcx - s(1) // 2, fcy - s(1) // 2,
                   max(1, s(1) // 2 + 1))

    # Gold rim collar at spout base
    pygame.draw.rect(big, NEAR_BLK,
                     (spa_x - s(2), spa_y - s(3), s(9), s(7)))
    pygame.draw.rect(big, _GOLD_DK,
                     (spa_x - s(1), spa_y - s(3), s(8), s(7)))
    pygame.draw.rect(big, _GOLD,
                     (spa_x - s(1), spa_y - s(2), s(8), s(5)))
    pygame.draw.line(big, _GOLD_HI,
                     (spa_x, spa_y - s(1)),
                     (spa_x + s(6), spa_y - s(1)),
                     max(1, s(1) // 2))

    # Multi-gem cluster finial at the spout tip
    fx = anc["mouth_x"]
    fy = anc["mouth_y"] - s(3)
    pygame.draw.ellipse(big, NEAR_BLK,
                        (fx - s(5) - s(1) // 2,
                         fy + s(1) - s(1) // 2,
                         s(10) + s(1), s(4) + s(1)))
    pygame.draw.ellipse(big, _GOLD_DK,
                        (fx - s(5), fy + s(1), s(10), s(4)))
    pygame.draw.ellipse(big, _GOLD,
                        (fx - s(5) + s(1) // 2, fy + s(1) + s(1) // 2,
                         s(10) - s(1), s(3) - s(1)))
    # Stopper gem cluster — emerald + ruby-diamond + sapphire. Cyan
    # variant centres the RUBY diamond instead of the amber's sapphire
    # so the trio pops against the cool body.
    _gem_round(big, fx - s(3), fy, s(2), _EMERALD, _EMERALD_HI)
    _gem_diamond(big, fx, fy - s(2), s(2) + s(1) // 2,
                 _RUBY, _RUBY_HI)
    _gem_round(big, fx + s(3), fy, s(2), _SAPPHIRE, _SAPPHIRE_HI)

    # Handle — gold torus with a CYAN inner gem (matches the cyan body
    # palette so the handle reads as one cool jewel rather than a
    # warm contrast spot). Hole tone colour-matches the body base so
    # the ring reads as "lamp body showing through the handle".
    handle_pal = {
        "dk":    _GOLD_DK,
        "base":  _GOLD,
        "hi":    _GOLD_HI,
        "hole":  _CYAN_PAL["base"],
    }
    _paint_torus_handle(big, anc, handle_pal,
                        inner_gem=("round", 0, 0, s(3),
                                   _CYAN_GEM, _CYAN_GEM_HI))

    # Foot — gold ring with emerald gem dots
    def foot_gems(big, cx_in, by, bw_in, bh_in):
        for gem_off in (-bw_in // 3, 0, bw_in // 3):
            _aa_circle(big, NEAR_BLK,
                       cx_in + gem_off + s(1) // 2,
                       by + s(2) + s(1) // 2, max(2, s(1)))
            _aa_circle(big, _EMERALD, cx_in + gem_off, by + s(2),
                       max(1, s(1) + 1))
            _aa_circle(big, _EMERALD_HI,
                       cx_in + gem_off - s(1) // 2,
                       by + s(2) - s(1) // 2, max(1, s(1) // 2))
    _paint_foot(big, anc, _CYAN_PAL,
                band_colors=[(NEAR_BLK, 0.0),
                             (_GOLD_DK,  0.20),
                             (_GOLD,     0.55),
                             (_GOLD_HI,  0.25)],
                extra_layer=foot_gems)

    # Smoke + sparkles
    _smoke_ribbon(big, anc["mouth_x"], anc["mouth_y"], _SMOKE,
                  n_puffs=14, height_n=42, curl=1.7, start_radius=4)
    _sparkles_around(big, cx, cy, n=14, radius_n=48,
                     color=(250, 250, 250), rng_seed=14)
    _sparkles_around(big, cx, cy, n=6, radius_n=38,
                     color=(255, 245, 200), rng_seed=15)
    _sparkles_around(big, fx, fy, n=6, radius_n=12,
                     color=(250, 250, 250), rng_seed=17)


# Module-level cache so the heavy render only happens once.
_cached_sprite: pygame.Surface | None = None
_cached_target_h: int | None = None


def get_lamp_sprite(target_height: int = 52) -> pygame.Surface:
    """Return a smoothscaled cyan Faceted-Crystal lamp sprite. First
    call pays the render cost; subsequent calls return the cached
    surface."""
    global _cached_sprite, _cached_target_h
    if _cached_sprite is not None and _cached_target_h == target_height:
        return _cached_sprite
    big = pygame.Surface((PW, PH), pygame.SRCALPHA)
    _render_faceted_cyan(big, PW // 2, PH // 2)
    target_w = int(target_height * (W / H))
    sprite = pygame.transform.smoothscale(big, (target_w, target_height))
    _cached_sprite = sprite
    _cached_target_h = target_height
    return sprite
