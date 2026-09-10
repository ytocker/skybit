"""Render 5 ALADDIN-LAMP variants at higher resolution + heavy
decoration. All five share the same squat brass S-spout lamp
silhouette so they read as the same artefact family; what varies
is the decorative treatment, palette, and ornament style.

Variants:
  1. Royal Sapphire — sapphire enamel body, gold filigree
     scrollwork, royal cartouche medallion with crown + ruby on
     the belly, crown-spike finial along the spout, ruby in the
     handle, pearled foot ring.
  2. Arabesque Imperial — imperial purple body, intricate gold
     arabesque pattern with diamond motifs + vertical pinstripes,
     centre emerald gem with burst rays, twin gold tassels
     hanging from the handle, jeweled emerald finial on spout.
  3. Apothecary Antique — aged brass with verdigris patches,
     parchment label tied around the belly with calligraphy +
     red wax seal stamped "G", brass chain dangling from handle.
  4. Faceted Crystal — pale-cyan crystal enamel body with large
     outlined diamond facets across the body + spout, multi-gem
     finial cluster, gold rim collar, heavy sparkle ring.
  5. Celestial Nebula — deep cosmic navy body, bright golden
     core star on the belly with halo + cross, constellation
     lines etched on the surface, comet finial on the spout,
     silver + gold layered handle and foot.

Run from repo root:
    SDL_VIDEODRIVER=dummy python -m tools.render_a1_lamp_variants [tag]
"""
import os, sys, math, random
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame
pygame.init()
pygame.display.set_mode((1, 1))

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                       "docs", "screenshots", "genie_designs")
os.makedirs(OUT_DIR, exist_ok=True)

# Higher resolution: SS=8 (was 6 in r3). Wider than tall — the
# lamp shape has a long horizontal silhouette.
W, H, SS = 112, 104, 8
PW, PH = W * SS, H * SS
SKY = (110, 175, 220)
NEAR_BLK = (16, 12, 8)

DISPLAY_BIG   = 4
DISPLAY_SMALL = 1


def s(v):
    return int(v * SS)


def aa_circle(surf, color, cx, cy, r):
    pygame.draw.circle(surf, color, (int(cx), int(cy)), int(r))


def ell(surf, color, cx, cy, w, h):
    pygame.draw.ellipse(surf, color,
                        (int(cx - w / 2), int(cy - h / 2),
                         int(w), int(h)))


def filled_poly(surf, color, pts):
    pygame.draw.polygon(surf, color, [(int(x), int(y)) for x, y in pts])


def gem_diamond(surf, cx, cy, r, color, hi_color):
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


def gem_round(surf, cx, cy, r, color, hi_color):
    pygame.draw.circle(surf, NEAR_BLK, (cx, cy), int(r + s(1) // 2))
    pygame.draw.circle(surf, color, (cx, cy), int(r))
    pygame.draw.circle(surf, hi_color,
                       (int(cx - r * 0.32), int(cy - r * 0.32)),
                       max(1, int(r * 0.55)))
    pygame.draw.circle(surf, (255, 255, 255),
                       (int(cx - r * 0.45), int(cy - r * 0.45)),
                       max(1, int(r * 0.22)))


def smoke_ribbon(surf, ox, oy, palette, n_puffs=14, height_n=42,
                 curl=2.0, taper=True, start_radius=4):
    for i in range(n_puffs):
        k = i / max(1, n_puffs - 1)
        sway = math.sin(0.6 + i * 0.55) * s(curl) * (0.3 + k)
        x = ox + sway
        y = oy - int(s(height_n) * k)
        if taper:
            rad = max(s(1), int(s(start_radius) * (1 - k * 0.65)))
        else:
            rad = max(s(1), int(s(start_radius * 0.7)))
        alpha = int(235 * (1 - k * 0.78))
        col = palette[min(int(k * len(palette)), len(palette) - 1)]
        puff = pygame.Surface((rad * 2 + 4, rad * 2 + 4),
                              pygame.SRCALPHA)
        pygame.draw.circle(puff, (*col, alpha),
                           (rad + 2, rad + 2), rad)
        surf.blit(puff, (int(x - rad - 2), int(y - rad - 2)))


def sparkles_around(surf, cx, cy, n=6, radius_n=40,
                    color=(255, 240, 180), rng_seed=11,
                    ang_lo=-math.pi, ang_hi=math.pi):
    rng = random.Random(rng_seed)
    R = s(radius_n)
    for _ in range(n):
        ang = rng.uniform(ang_lo, ang_hi)
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
        aa_circle(surf, (255, 255, 255), sx, sy, max(1, sr))


# ─────────────────────────────────────────────────────────────────────
# Shared lamp silhouette. Builds the body polygon, spout polygon,
# and returns key anchor points so each variant can decorate from
# a consistent starting point. Smooth: 48-vertex body + 14-pt spout.
# ─────────────────────────────────────────────────────────────────────

def lamp_silhouette(cx, cy):
    body_cy = cy + s(6)
    bw = s(54)
    bh = s(24)
    # Body — parametric oval with flatter bottom (so the foot can
    # sit on it). 48 vertices for buttery curve.
    n_vert = 48
    body_pts = []
    for k in range(n_vert):
        t = (k / n_vert) * math.tau - math.pi / 2
        cos_t = math.cos(t)
        sin_t = math.sin(t)
        # Asymmetric squash: top fuller, bottom flatter for the foot
        yk = sin_t * 0.86 if sin_t > 0 else sin_t * 1.0
        x = cx + cos_t * (bw / 2)
        y = body_cy + yk * (bh / 2)
        body_pts.append((x, y))

    # Spout — swan-neck S-curve polygon. Base buried INSIDE the
    # body's right shoulder so the silhouette flows out smoothly.
    spa_x = cx + bw // 2 - s(8)
    spa_y = body_cy - s(1)
    outer_pts = [
        (spa_x - s(4),  spa_y + s(7)),    # buried lower base
        (spa_x + s(4),  spa_y + s(3)),    # body shoulder exit
        (spa_x + s(11), spa_y - s(3)),    # lower curve
        (spa_x + s(17), spa_y - s(11)),   # mid sweep
        (spa_x + s(21), spa_y - s(19)),   # upper sweep
        (spa_x + s(22), spa_y - s(26)),   # near tip outer
        (spa_x + s(19), spa_y - s(31)),   # mouth outer rim
    ]
    inner_pts = [
        (spa_x + s(13), spa_y - s(31)),   # mouth inner rim
        (spa_x + s(15), spa_y - s(26)),   # upper inner
        (spa_x + s(16), spa_y - s(19)),   # mid inner (back)
        (spa_x + s(13), spa_y - s(11)),   # mid inner
        (spa_x + s(7),  spa_y - s(3)),    # lower inner
        (spa_x + s(1),  spa_y + s(2)),    # shoulder return
        (spa_x - s(4),  spa_y + s(5)),    # buried return
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
        # Handle anchor (left side)
        "h_cx": cx - bw // 2 - s(4),
        "h_cy": body_cy - s(2),
        "h_w": s(14),
        "h_h": s(24),
        # Foot anchors
        "stem_y": body_cy + bh // 2 - s(2),
        "stem_w": s(20),
        "stem_h": s(3),
        "base_w": s(32),
        "base_h": s(5),
    }


def paint_lamp_body(big, anc, palette,
                    draw_outline=True,
                    body_inset_ratio=0.86):
    """Paint body + spout (no handle, no foot — those are drawn
    by helpers below since their decoration varies per variant)."""
    DK    = palette["dk"]
    BASE  = palette["base"]
    HI    = palette["hi"]
    SHEEN = palette.get("sheen", (255, 255, 255))

    cx = anc["cx"]
    body_cy = anc["body_cy"]
    bw, bh = anc["bw"], anc["bh"]

    # Body — drop shadow + dark base + inset mid + bright crescent
    if draw_outline:
        shadow_pts = [(x + s(1), y + s(1)) for x, y in anc["body_pts"]]
        filled_poly(big, NEAR_BLK, shadow_pts)
    filled_poly(big, DK, anc["body_pts"])
    inner = []
    for x, y in anc["body_pts"]:
        dx = (x - cx) * body_inset_ratio
        dy = (y - body_cy) * body_inset_ratio
        inner.append((cx + dx, body_cy + dy))
    filled_poly(big, BASE, inner)

    # Highlight crescent — thin tapered arc along upper curve
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
    # Tiny pinpoint glint
    aa_circle(big, SHEEN, cx - s(10), body_cy - s(8), max(2, s(1)))

    # Spout — drop shadow + dark base + inset mid + highlight stripe
    if draw_outline:
        sh_pts = [(x + s(1), y + s(1)) for x, y in anc["spout_pts"]]
        filled_poly(big, NEAR_BLK, sh_pts)
    filled_poly(big, DK, anc["spout_pts"])
    # Inset fill (offset toward inner edge)
    in_fill = [(x - s(1), y + s(1)) for x, y in anc["outer_pts"]] + \
              [(x + s(2), y) for x, y in anc["inner_pts"]]
    filled_poly(big, BASE, in_fill)
    # Highlight stripe along outer (right) curve
    spa_x = anc["spa_x"]
    spa_y = anc["spa_y"]
    pygame.draw.lines(big, HI, False,
                      [(spa_x + s(7),  spa_y - s(3)),
                       (spa_x + s(13), spa_y - s(11)),
                       (spa_x + s(18), spa_y - s(20))],
                      max(2, s(1)))
    pygame.draw.lines(big, SHEEN, False,
                      [(spa_x + s(9),  spa_y - s(5)),
                       (spa_x + s(14), spa_y - s(13))],
                      max(1, s(1) // 2 + 1))
    # Mouth rim crescent + opening
    pygame.draw.lines(big, NEAR_BLK, False,
                      [(spa_x + s(13), spa_y - s(30)),
                       (spa_x + s(16), spa_y - s(29)),
                       (spa_x + s(19), spa_y - s(30))],
                      max(2, s(1)))
    ell(big, NEAR_BLK, anc["mouth_x"], anc["mouth_y"], s(6), s(2))


def paint_torus_handle(big, anc, palette,
                       inner_gem=None, ornaments=None):
    """Paint the lamp's handle as a torus on the left side. Optionally
    embed a centre gem in the hole, and add small ornament dots
    around the ring."""
    DK    = palette["dk"]
    BASE  = palette["base"]
    HI    = palette["hi"]
    h_cx, h_cy = anc["h_cx"], anc["h_cy"]
    h_w, h_h = anc["h_w"], anc["h_h"]
    HOLE_COLOR = palette.get("hole", (60, 95, 130))
    # Outer dark ring
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
    # Inner hole
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
    # Top + bottom catch-lights
    pygame.draw.line(big, HI,
                     (h_cx - s(1), h_cy - h_h // 2 + s(1)),
                     (h_cx + s(3), h_cy - h_h // 2 + s(1)),
                     max(2, s(1)))
    pygame.draw.line(big, HI,
                     (h_cx + h_w // 2 - s(2), h_cy + s(2)),
                     (h_cx + h_w // 2 - s(2), h_cy + s(5)),
                     max(2, s(1)))
    # Optional centre gem (embedded in the upper part of the ring)
    if inner_gem is not None:
        gtype, gcx_off, gcy_off, gr, gcol, ghi = inner_gem
        gcx = h_cx + gcx_off
        gcy = h_cy + gcy_off
        if gtype == "diamond":
            gem_diamond(big, gcx, gcy, gr, gcol, ghi)
        else:
            gem_round(big, gcx, gcy, gr, gcol, ghi)
    # Optional ornament dots around the ring
    if ornaments is not None:
        for (ang_deg, col) in ornaments:
            ang = math.radians(ang_deg)
            ox = h_cx + math.cos(ang) * (h_w / 2 + s(1))
            oy = h_cy + math.sin(ang) * (h_h / 2 + s(1))
            aa_circle(big, NEAR_BLK, ox + s(1) // 2,
                      oy + s(1) // 2, max(1, s(1)))
            aa_circle(big, col, ox, oy, max(1, s(1) // 2 + 1))


def paint_foot(big, anc, palette,
               band_colors=None, with_pearls=False,
               extra_layer=None):
    """Paint stem + flared foot base. band_colors lets variants
    swap brass→gold→silver layers."""
    DK    = palette["dk"]
    BASE  = palette["base"]
    HI    = palette["hi"]
    cx = anc["cx"]
    body_cy = anc["body_cy"]
    bh = anc["bh"]
    stem_y = anc["stem_y"]
    stem_w, stem_h = anc["stem_w"], anc["stem_h"]
    base_w, base_h = anc["base_w"], anc["base_h"]
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
    # Base
    base_y = stem_y + stem_h
    pygame.draw.rect(big, NEAR_BLK,
                     (cx - base_w // 2 - s(1) // 2, base_y,
                      base_w + s(1), base_h + s(1)),
                     border_radius=s(1))
    if band_colors is None:
        pygame.draw.rect(big, DK,
                         (cx - base_w // 2, base_y, base_w, base_h),
                         border_radius=s(1))
        pygame.draw.rect(big, BASE,
                         (cx - base_w // 2 + s(1) // 2, base_y,
                          base_w - s(1), max(1, base_h - s(1))),
                         border_radius=s(1))
        pygame.draw.line(big, HI,
                         (cx - base_w // 2 + s(3), base_y + s(1)),
                         (cx + base_w // 2 - s(3), base_y + s(1)),
                         max(1, s(1) // 2))
    else:
        # band_colors is a list of (color, height_fraction) tuples
        cur_y = base_y
        total_h = base_h
        for col, frac in band_colors:
            h_band = int(total_h * frac)
            pygame.draw.rect(big, col,
                             (cx - base_w // 2, cur_y, base_w, h_band),
                             border_radius=s(1))
            cur_y += h_band
    if with_pearls:
        # Pearled dots on the base
        for dx in range(-base_w // 2 + s(3), base_w // 2,
                        max(1, s(3))):
            aa_circle(big, (245, 240, 230),
                      cx + dx, base_y + s(2), max(1, s(1) // 2 + 1))
    if extra_layer is not None:
        # E.g., star dots, gold lip, etc.
        extra_layer(big, cx, base_y, base_w, base_h)


def clip_to_body(surf, body_pts):
    mask = pygame.Surface((PW, PH), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255),
                        [(int(x), int(y)) for x, y in body_pts])
    surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)


# ─────────────────────────────────────────────────────────────────────
# Variant 1 — Royal Sapphire. Sapphire enamel body, gold filigree
# scrollwork at the upper body corners, royal cartouche medallion
# on the belly (gold shield + crown silhouette + ruby), crown-spike
# finial along the spout top edge, ruby in the handle, ornate gold
# foot ring with pearled rivets.
# ─────────────────────────────────────────────────────────────────────

def draw_lamp_1_royal_sapphire(big, cx, cy):
    pal = {
        "dk":    ( 18,  30,  90),
        "base":  ( 45,  75, 175),
        "hi":    (140, 175, 235),
        "sheen": (235, 245, 255),
        "hole":  ( 55,  35, 100),
    }
    GOLD     = (255, 220, 110)
    GOLD_HI  = (255, 245, 175)
    GOLD_DK  = (180, 130,  40)
    RUBY     = (220,  55,  75)
    RUBY_HI  = (255, 175, 195)
    SMOKE    = [(245, 230, 255), (180, 200, 245), (110, 140, 220),
                ( 70,  95, 185)]

    anc = lamp_silhouette(cx, cy)
    paint_lamp_body(big, anc, pal)

    bw, bh = anc["bw"], anc["bh"]
    body_cy = anc["body_cy"]

    # Gold filigree scrollwork — 2 S-curves on the upper body
    def scroll(start_xy, end_xy, n_pts=14):
        pts = []
        sx, sy = start_xy
        ex, ey = end_xy
        for k in range(n_pts):
            t = k / (n_pts - 1)
            x = sx + (ex - sx) * t
            y = sy + (ey - sy) * t
            # Add S-curve perturbation
            curl = math.sin(t * math.pi) * s(3)
            x += curl
            pts.append((x, y))
        # Shadow
        pygame.draw.lines(big, NEAR_BLK, False,
                          [(p[0] + s(1) // 3, p[1] + s(1) // 3)
                           for p in pts], max(4, s(1) + 1))
        pygame.draw.lines(big, GOLD_DK, False, pts, max(3, s(1)))
        pygame.draw.lines(big, GOLD, False, pts, max(2, s(1) - 1))
        # Curl balls at the endpoints
        for ep in (pts[0], pts[-1]):
            aa_circle(big, GOLD_DK, ep[0], ep[1], max(2, s(1) + 1))
            aa_circle(big, GOLD, ep[0], ep[1], max(2, s(1)))
            aa_circle(big, GOLD_HI, ep[0] - s(1) // 2,
                      ep[1] - s(1) // 2, max(1, s(1) // 2 + 1))

    # Upper-left filigree
    scroll((cx - bw // 2 + s(6), body_cy - bh // 2 + s(4)),
           (cx - s(8), body_cy + s(3)))
    # Upper-right filigree
    scroll((cx + bw // 2 - s(14), body_cy - bh // 2 + s(4)),
           (cx + s(4), body_cy + s(3)))

    # Royal cartouche medallion on the belly
    med_cx, med_cy = cx + s(2), body_cy + s(2)
    med_w, med_h = s(16), s(10)
    pygame.draw.ellipse(big, NEAR_BLK,
                        (med_cx - med_w // 2 - s(1) // 2,
                         med_cy - med_h // 2 - s(1) // 2,
                         med_w + s(1), med_h + s(1)))
    pygame.draw.ellipse(big, GOLD_DK,
                        (med_cx - med_w // 2, med_cy - med_h // 2,
                         med_w, med_h))
    pygame.draw.ellipse(big, GOLD,
                        (med_cx - med_w // 2 + s(1) // 2,
                         med_cy - med_h // 2 + s(1) // 2,
                         med_w - s(1), med_h - s(1)))
    pygame.draw.ellipse(big, GOLD_DK,
                        (med_cx - med_w // 2 + s(2),
                         med_cy - med_h // 2 + s(2),
                         med_w - s(4), med_h - s(4)))
    # Crown silhouette ABOVE the medallion
    cr_y = med_cy - med_h // 2 - s(1)
    crown_pts = [(med_cx - s(6), cr_y),
                 (med_cx - s(4), cr_y - s(3)),
                 (med_cx - s(2), cr_y - s(1)),
                 (med_cx,        cr_y - s(4)),
                 (med_cx + s(2), cr_y - s(1)),
                 (med_cx + s(4), cr_y - s(3)),
                 (med_cx + s(6), cr_y)]
    pygame.draw.polygon(big, GOLD, crown_pts)
    pygame.draw.polygon(big, NEAR_BLK, crown_pts, max(1, s(1) // 2))
    aa_circle(big, RUBY, med_cx, cr_y - s(3) - s(1) // 2,
              max(1, s(1) // 2 + 1))
    # Ruby diamond in the medallion centre
    gem_diamond(big, med_cx, med_cy + s(1), s(2) + s(1) // 2,
                RUBY, RUBY_HI)
    # Tiny gold dots flanking the ruby
    aa_circle(big, GOLD_HI, med_cx - s(5), med_cy + s(1),
              max(1, s(1) // 2))
    aa_circle(big, GOLD_HI, med_cx + s(5), med_cy + s(1),
              max(1, s(1) // 2))

    # Gold neck ring where the spout joins the body
    spa_x, spa_y = anc["spa_x"], anc["spa_y"]
    pygame.draw.rect(big, NEAR_BLK,
                     (spa_x - s(2), spa_y - s(2),
                      s(8), s(5)))
    pygame.draw.rect(big, GOLD_DK,
                     (spa_x - s(1), spa_y - s(2),
                      s(7), s(5)))
    pygame.draw.rect(big, GOLD,
                     (spa_x - s(1), spa_y - s(1),
                      s(7), s(3)))
    pygame.draw.line(big, GOLD_HI,
                     (spa_x, spa_y - s(1) + s(1) // 2),
                     (spa_x + s(5), spa_y - s(1) + s(1) // 2),
                     max(1, s(1) // 2))

    # Crown-spike finial along the spout's top edge — 3 mini spikes
    # rising from the upper outer curve
    for i, frac in enumerate((0.35, 0.55, 0.75)):
        # Sample point along the outer spout curve
        outer = anc["outer_pts"]
        idx = max(0, min(len(outer) - 2, int(frac * (len(outer) - 1))))
        a = outer[idx]
        b = outer[idx + 1]
        # Direction tangent (approx)
        tx, ty = a[0] + (b[0] - a[0]) * 0.5, a[1] + (b[1] - a[1]) * 0.5
        # Normal pointing outward (rotate tangent by 90°)
        ang = math.atan2(b[1] - a[1], b[0] - a[0]) - math.pi / 2
        sp_h = s(3 + (i % 2))
        spike_tip = (tx + math.cos(ang) * sp_h,
                     ty + math.sin(ang) * sp_h)
        base_w = s(2)
        base_perp = ang + math.pi / 2
        bl = (tx + math.cos(base_perp) * base_w / 2,
              ty + math.sin(base_perp) * base_w / 2)
        br = (tx - math.cos(base_perp) * base_w / 2,
              ty - math.sin(base_perp) * base_w / 2)
        pygame.draw.polygon(big, GOLD, [bl, spike_tip, br])
        pygame.draw.polygon(big, NEAR_BLK,
                            [bl, spike_tip, br], max(1, s(1) // 2))

    # Ruby gem at the spout tip (just inside the mouth opening)
    aa_circle(big, NEAR_BLK, anc["mouth_x"] + s(1) // 2,
              anc["mouth_y"] - s(2) + s(1) // 2, max(2, s(1)))
    aa_circle(big, RUBY, anc["mouth_x"], anc["mouth_y"] - s(2),
              max(2, s(1)))
    aa_circle(big, RUBY_HI, anc["mouth_x"] - s(1) // 2,
              anc["mouth_y"] - s(2) - s(1) // 2, max(1, s(1) // 2 + 1))

    # Handle — gold torus with embedded ruby in the hole
    handle_pal = {
        "dk":    GOLD_DK,
        "base":  GOLD,
        "hi":    GOLD_HI,
        "hole":  ( 90,  20,  35),
    }
    paint_torus_handle(big, anc, handle_pal,
                       inner_gem=("diamond", 0, 0,
                                  s(3), RUBY, RUBY_HI))

    # Foot — gold ring with pearled rivets
    paint_foot(big, anc, pal,
               band_colors=[(NEAR_BLK, 0.0),
                            (GOLD_DK,  0.25),
                            (GOLD,     0.55),
                            (GOLD_HI,  0.20)],
               with_pearls=True)

    # Smoke + sparkles
    smoke_ribbon(big, anc["mouth_x"], anc["mouth_y"], SMOKE,
                 n_puffs=14, height_n=40, curl=1.8, start_radius=4)
    sparkles_around(big, cx, cy - s(4), n=6, radius_n=42,
                    color=(220, 230, 255), rng_seed=21)
    sparkles_around(big, anc["mouth_x"], anc["mouth_y"] - s(4),
                    n=4, radius_n=14, color=(255, 245, 200),
                    rng_seed=22)


# ─────────────────────────────────────────────────────────────────────
# Variant 2 — Arabesque Imperial. Imperial purple body, intricate
# gold arabesque pattern (diamond motifs + sine connectors + vert
# pinstripes), centre emerald gem with burst rays, twin gold tassels
# hanging from the handle, jeweled emerald finial on the spout.
# ─────────────────────────────────────────────────────────────────────

def draw_lamp_2_arabesque(big, cx, cy):
    pal = {
        "dk":    ( 50,  18,  90),
        "base":  (100,  50, 170),
        "hi":    (175, 135, 220),
        "sheen": (245, 230, 255),
        "hole":  ( 75,  25, 115),
    }
    GOLD     = (255, 220, 110)
    GOLD_HI  = (255, 245, 175)
    GOLD_DK  = (180, 130,  40)
    EMERALD  = ( 70, 175, 110)
    EMERALD_HI = (180, 240, 200)
    SMOKE    = [(245, 225, 255), (200, 165, 240), (135,  85, 200),
                ( 80,  45, 165)]

    anc = lamp_silhouette(cx, cy)
    paint_lamp_body(big, anc, pal)

    bw, bh = anc["bw"], anc["bh"]
    body_cy = anc["body_cy"]

    # Arabesque pattern — single row of diamond motifs with sine
    # connectors across the upper body, plus a row of dots along the
    # lower body. (The lamp is squat, so only one main row fits.)
    def diamond_motif(x, y, dr):
        # Shadow + base + highlight diamond outline
        pygame.draw.polygon(big, GOLD_DK,
                            [(x, y - dr - s(1) // 2),
                             (x + dr + s(1) // 2, y),
                             (x, y + dr + s(1) // 2),
                             (x - dr - s(1) // 2, y)])
        pygame.draw.polygon(big, GOLD,
                            [(x, y - dr), (x + dr, y),
                             (x, y + dr), (x - dr, y)])
        aa_circle(big, GOLD_HI, x, y, max(1, s(1) // 2 + 1))

    band_y = body_cy - s(5)
    n_motifs = 5
    span = bw - s(20)
    for j in range(n_motifs):
        t = (j + 0.5) / n_motifs
        x = cx - bw // 2 + s(10) + span * t
        diamond_motif(x, band_y, s(2) + s(1) // 2)
        # connector to next motif
        if j < n_motifs - 1:
            t2 = (j + 1.5) / n_motifs
            x2 = cx - bw // 2 + s(10) + span * t2
            cn = 8
            curve_pts = []
            for ck in range(cn + 1):
                ct = ck / cn
                cxp = x + (x2 - x) * ct
                cyp = band_y + math.sin(ct * math.pi) * s(2)
                curve_pts.append((cxp, cyp))
            pygame.draw.lines(big, GOLD_DK, False, curve_pts,
                              max(2, s(1)))
            pygame.draw.lines(big, GOLD, False, curve_pts,
                              max(1, s(1) // 2 + 1))

    # Lower row of dots along the lower belly
    lower_y = body_cy + s(6)
    for j in range(8):
        t = (j + 0.5) / 8
        x = cx - bw // 2 + s(8) + (bw - s(16)) * t
        aa_circle(big, NEAR_BLK, x + s(1) // 3, lower_y + s(1) // 3,
                  max(1, s(1) // 2 + 1))
        aa_circle(big, GOLD, x, lower_y, max(1, s(1) // 2 + 1))
        aa_circle(big, GOLD_HI, x - s(1) // 2, lower_y - s(1) // 2,
                  max(1, s(1) // 2))

    # Vertical gold pinstripes — left + right edges of the dome,
    # connecting the upper motif row and the lower dot row.
    for sign in (-1, 1):
        sx = cx + sign * (bw // 2 - s(6))
        pygame.draw.line(big, GOLD_DK,
                         (sx + s(1) // 3, band_y - s(3) + s(1) // 3),
                         (sx + s(1) // 3, lower_y + s(2) + s(1) // 3),
                         max(2, s(1)))
        pygame.draw.line(big, GOLD,
                         (sx, band_y - s(3)),
                         (sx, lower_y + s(2)),
                         max(1, s(1) // 2 + 1))

    # Centre emerald gem with gold burst rays
    em_cx, em_cy = cx + s(1), body_cy + s(1)
    gem_round(big, em_cx, em_cy, s(3) + s(1) // 2,
              EMERALD, EMERALD_HI)
    for ang_deg in (45, 135, 225, 315):
        ang = math.radians(ang_deg)
        x1 = em_cx + math.cos(ang) * s(5)
        y1 = em_cy + math.sin(ang) * s(5)
        x2 = em_cx + math.cos(ang) * s(7)
        y2 = em_cy + math.sin(ang) * s(7)
        pygame.draw.line(big, NEAR_BLK,
                         (x1 + s(1) // 3, y1 + s(1) // 3),
                         (x2 + s(1) // 3, y2 + s(1) // 3),
                         max(3, s(1) + 1))
        pygame.draw.line(big, GOLD,
                         (x1, y1), (x2, y2),
                         max(2, s(1)))

    # Gold neck ring at spout base
    spa_x, spa_y = anc["spa_x"], anc["spa_y"]
    pygame.draw.rect(big, NEAR_BLK,
                     (spa_x - s(2), spa_y - s(2),
                      s(8), s(5)))
    pygame.draw.rect(big, GOLD_DK,
                     (spa_x - s(1), spa_y - s(2),
                      s(7), s(5)))
    pygame.draw.rect(big, GOLD,
                     (spa_x - s(1), spa_y - s(1),
                      s(7), s(3)))

    # Jeweled emerald finial on the spout — at the mouth opening
    aa_circle(big, NEAR_BLK, anc["mouth_x"] + s(1) // 2,
              anc["mouth_y"] - s(2) + s(1) // 2,
              max(3, s(1) + 1))
    gem_diamond(big, anc["mouth_x"], anc["mouth_y"] - s(3),
                s(3), EMERALD, EMERALD_HI)

    # Handle — gold torus
    handle_pal = {
        "dk":    GOLD_DK,
        "base":  GOLD,
        "hi":    GOLD_HI,
        "hole":  ( 65,  30,  95),
    }
    paint_torus_handle(big, anc, handle_pal,
                       ornaments=[(0, GOLD_HI), (180, GOLD_HI)])

    # Twin gold tassels hanging from the handle's bottom
    h_cx, h_cy, h_h = anc["h_cx"], anc["h_cy"], anc["h_h"]
    for sign in (-1, 1):
        rope_top = (h_cx + sign * s(3), h_cy + h_h // 2 + s(1))
        bell_top = (h_cx + sign * s(5) - s(1) * sign,
                    h_cy + h_h // 2 + s(8))
        # Rope curve
        rope_pts = []
        for k in range(8):
            t = k / 7.0
            xp = rope_top[0] + (bell_top[0] - rope_top[0]) * t
            yp = rope_top[1] + (bell_top[1] - rope_top[1]) * t
            rope_pts.append((xp, yp))
        pygame.draw.lines(big, NEAR_BLK, False,
                          [(p[0] + s(1) // 3, p[1] + s(1) // 3)
                           for p in rope_pts], max(4, s(1) + 1))
        pygame.draw.lines(big, GOLD_DK, False, rope_pts,
                          max(3, s(1)))
        pygame.draw.lines(big, GOLD, False, rope_pts,
                          max(2, s(1) - 1))
        # Tassel bell
        bw_t = s(4)
        bh_t = s(5)
        pygame.draw.polygon(big, NEAR_BLK,
                            [(bell_top[0] - bw_t // 2 + s(1) // 3,
                              bell_top[1] + s(1) // 3),
                             (bell_top[0] + bw_t // 2 + s(1) // 3,
                              bell_top[1] + s(1) // 3),
                             (bell_top[0] + bw_t // 2 - s(1) + s(1) // 3,
                              bell_top[1] + bh_t + s(1) // 3),
                             (bell_top[0] - bw_t // 2 + s(1) + s(1) // 3,
                              bell_top[1] + bh_t + s(1) // 3)])
        pygame.draw.polygon(big, GOLD,
                            [(bell_top[0] - bw_t // 2, bell_top[1]),
                             (bell_top[0] + bw_t // 2, bell_top[1]),
                             (bell_top[0] + bw_t // 2 - s(1),
                              bell_top[1] + bh_t),
                             (bell_top[0] - bw_t // 2 + s(1),
                              bell_top[1] + bh_t)])
        # Threads
        for tdx in range(-bw_t // 2 + s(1), bw_t // 2, max(1, s(1))):
            pygame.draw.line(big, GOLD,
                             (bell_top[0] + tdx, bell_top[1] + bh_t),
                             (bell_top[0] + tdx, bell_top[1] + bh_t + s(5)),
                             max(1, s(1) // 2))

    # Foot — gold ring with pearled rivets
    paint_foot(big, anc, pal,
               band_colors=[(NEAR_BLK, 0.0),
                            (GOLD_DK,  0.25),
                            (GOLD,     0.55),
                            (GOLD_HI,  0.20)],
               with_pearls=True)

    # Smoke + sparkles
    smoke_ribbon(big, anc["mouth_x"], anc["mouth_y"], SMOKE,
                 n_puffs=14, height_n=40, curl=1.9, start_radius=4)
    sparkles_around(big, cx, cy - s(2), n=6, radius_n=42,
                    color=GOLD_HI, rng_seed=27)
    sparkles_around(big, anc["mouth_x"], anc["mouth_y"] - s(4),
                    n=4, radius_n=14, color=(255, 245, 200),
                    rng_seed=28)


# ─────────────────────────────────────────────────────────────────────
# Variant 3 — Apothecary Antique. Aged brass body with verdigris
# patches, parchment label tied around the belly with calligraphy
# script + red wax seal stamped "G", brass chain dangling from the
# handle, weathered spout with patina drip.
# ─────────────────────────────────────────────────────────────────────

def draw_lamp_3_apothecary(big, cx, cy):
    pal = {
        "dk":    ( 80,  60,  25),
        "base":  (160, 120,  55),
        "hi":    (220, 180, 110),
        "sheen": (250, 230, 165),
        "hole":  ( 65,  50,  20),
    }
    BRASS    = pal["base"]
    BRASS_HI = pal["hi"]
    BRASS_DK = pal["dk"]
    PATINA   = ( 75, 150, 130)
    PATINA_HI = (130, 200, 180)
    PARCH    = (235, 215, 165)
    PARCH_HI = (255, 240, 200)
    PARCH_DK = (170, 150, 100)
    INK      = ( 80,  45,  20)
    WAX      = (175,  35,  35)
    WAX_HI   = (220,  90,  90)
    SMOKE    = [(220, 235, 220), (175, 215, 180), (110, 175, 130),
                ( 60, 130,  90)]

    anc = lamp_silhouette(cx, cy)
    paint_lamp_body(big, anc, pal)

    bw, bh = anc["bw"], anc["bh"]
    body_cy = anc["body_cy"]

    # Verdigris patches on the dome (greenish patina splotches)
    rng = random.Random(7)
    patina_clip = pygame.Surface((PW, PH), pygame.SRCALPHA)
    for _ in range(7):
        px = cx + rng.randint(-bw // 2 + s(4), bw // 2 - s(4))
        py = body_cy + rng.randint(-bh // 2 + s(2), bh // 2 - s(4))
        pr = rng.randint(s(2), s(4))
        col = rng.choice([PATINA, PATINA_HI])
        sub = pygame.Surface((pr * 2 + 4, pr * 2 + 4),
                             pygame.SRCALPHA)
        pygame.draw.circle(sub, (*col, 140),
                           (pr + 2, pr + 2), pr)
        patina_clip.blit(sub, (px - pr - 2, py - pr - 2))
    clip_to_body(patina_clip, anc["body_pts"])
    big.blit(patina_clip, (0, 0))

    # Parchment label tied around the belly. Curved-edge rectangle
    # with torn edges + 2 ink script lines + red wax seal at bottom.
    lbl_top_y = body_cy - s(4)
    lbl_bot_y = body_cy + s(8)
    lbl_left = cx - s(20)
    lbl_right = cx + s(18)
    label_pts = [
        (lbl_left + s(1), lbl_top_y),
        (lbl_left, lbl_top_y + s(2)),
        (lbl_left + s(1), lbl_top_y + s(5)),
        (lbl_left - s(1), lbl_top_y + s(7)),
        (lbl_left + s(1), lbl_top_y + s(9)),
        (lbl_left, lbl_bot_y - s(1)),
        (lbl_left + s(2), lbl_bot_y),
        (lbl_right - s(2), lbl_bot_y),
        (lbl_right + s(1), lbl_bot_y - s(1)),
        (lbl_right, lbl_top_y + s(9)),
        (lbl_right - s(1), lbl_top_y + s(7)),
        (lbl_right + s(1), lbl_top_y + s(5)),
        (lbl_right, lbl_top_y + s(2)),
        (lbl_right - s(1), lbl_top_y),
    ]
    filled_poly(big, NEAR_BLK,
                [(x + s(1), y + s(1)) for x, y in label_pts])
    filled_poly(big, PARCH_DK, label_pts)
    inner = []
    for x, y in label_pts:
        dx = (x - cx) * 0.92
        dy = (y - body_cy) * 0.92
        inner.append((cx + dx, body_cy + dy))
    filled_poly(big, PARCH, inner)
    # Top edge crease highlight
    pygame.draw.line(big, PARCH_HI,
                     (lbl_left + s(3), lbl_top_y + s(2)),
                     (lbl_right - s(3), lbl_top_y + s(2)),
                     max(1, s(1) // 2))

    # Calligraphy script — 2 wavy ink lines
    for line_y_off in (-s(2), s(2)):
        line_y = body_cy + s(1) + line_y_off
        pts = []
        for k in range(12):
            t = k / 11.0
            xp = lbl_left + s(3) + (lbl_right - lbl_left - s(6)) * t
            yp = line_y + math.sin(t * math.tau * 1.5) * s(1) // 2
            pts.append((xp, yp))
        pygame.draw.lines(big, INK, False, pts, max(2, s(1) // 2 + 1))

    # Brass cord ties on each side of the label (loops that show
    # the label is bound around the lamp)
    for sign in (-1, 1):
        cord_x = cx + sign * (s(20) + s(2))
        cord_y = body_cy + s(2)
        pygame.draw.ellipse(big, NEAR_BLK,
                            (cord_x - s(2) + s(1) // 3,
                             cord_y - s(2) + s(1) // 3,
                             s(4) + s(1), s(4) + s(1)))
        pygame.draw.ellipse(big, BRASS_DK,
                            (cord_x - s(2), cord_y - s(2),
                             s(4), s(4)))
        pygame.draw.ellipse(big, BRASS,
                            (cord_x - s(2) + s(1) // 2,
                             cord_y - s(2) + s(1) // 2,
                             s(3), s(3)))

    # Red wax seal at the bottom-centre of the label
    seal_cx = cx
    seal_cy = lbl_bot_y - s(2)
    seal_r = s(4)
    # outer rim drips
    for ang_deg in range(0, 360, 30):
        ang = math.radians(ang_deg + 12)
        x = seal_cx + math.cos(ang) * seal_r
        y = seal_cy + math.sin(ang) * seal_r
        aa_circle(big, WAX, x, y, max(2, s(1)))
    aa_circle(big, NEAR_BLK, seal_cx + s(1) // 2, seal_cy + s(1) // 2,
              seal_r + s(1))
    aa_circle(big, WAX, seal_cx, seal_cy, seal_r)
    aa_circle(big, WAX_HI, seal_cx - s(1), seal_cy - s(1),
              max(1, seal_r * 3 // 4))
    # "G" stamp
    font_g = pygame.font.SysFont("Times New Roman", s(5), bold=True)
    g_dark = font_g.render("G", True, (90, 15, 15))
    g_w = g_dark.get_width()
    g_h = g_dark.get_height()
    big.blit(g_dark, (seal_cx - g_w // 2, seal_cy - g_h // 2))

    # Brass chain dangling from the handle's bottom
    h_cx, h_cy, h_h = anc["h_cx"], anc["h_cy"], anc["h_h"]
    chain_x = h_cx + s(1)
    chain_y = h_cy + h_h // 2 + s(2)
    for k in range(7):
        lx = chain_x - math.sin(k * 0.85) * s(2)
        ly = chain_y + k * s(2)
        pygame.draw.ellipse(big, NEAR_BLK,
                            (lx - s(2) - s(1) // 3,
                             ly - s(1) - s(1) // 3,
                             s(4) + s(1), s(2) + s(1)))
        pygame.draw.ellipse(big, BRASS_DK,
                            (lx - s(2), ly - s(1), s(4), s(2)))
        pygame.draw.ellipse(big, BRASS,
                            (lx - s(2) + s(1) // 2, ly - s(1),
                             s(3), max(1, s(1))))
    # Charm at end of chain
    last_x = chain_x - math.sin(7 * 0.85) * s(2)
    last_y = chain_y + 7 * s(2)
    aa_circle(big, NEAR_BLK, last_x + s(1) // 2,
              last_y + s(1) // 2, max(2, s(1) + 1))
    aa_circle(big, BRASS, last_x, last_y, max(2, s(1) + 1))
    aa_circle(big, BRASS_HI, last_x - s(1) // 2, last_y - s(1) // 2,
              max(1, s(1) // 2 + 1))

    # Handle — aged brass torus
    handle_pal = {
        "dk":    BRASS_DK,
        "base":  BRASS,
        "hi":    BRASS_HI,
        "hole":  ( 50,  35,  15),
    }
    paint_torus_handle(big, anc, handle_pal)

    # Patina drip on the spout — a vertical greenish drip down
    # the outer curve of the spout
    spa_x, spa_y = anc["spa_x"], anc["spa_y"]
    drip_pts = [
        (spa_x + s(19), spa_y - s(15)),
        (spa_x + s(20), spa_y - s(10)),
        (spa_x + s(19), spa_y - s(5)),
        (spa_x + s(20), spa_y),
        (spa_x + s(20) - s(1), spa_y + s(2)),
        (spa_x + s(19), spa_y),
        (spa_x + s(18), spa_y - s(5)),
        (spa_x + s(17), spa_y - s(10)),
        (spa_x + s(18), spa_y - s(15)),
    ]
    pygame.draw.polygon(big, PATINA, drip_pts)
    # Tiny patina highlight
    pygame.draw.line(big, PATINA_HI,
                     (spa_x + s(19), spa_y - s(14)),
                     (spa_x + s(19), spa_y),
                     max(1, s(1) // 2))

    # Foot — aged brass with verdigris streaks
    paint_foot(big, anc, pal)
    # Verdigris streaks on the base
    base_y = anc["stem_y"] + anc["stem_h"]
    for offset in (-anc["base_w"] // 4, anc["base_w"] // 5):
        pygame.draw.line(big, PATINA,
                         (cx + offset, base_y),
                         (cx + offset + s(1), base_y + anc["base_h"] - s(1)),
                         max(2, s(1)))

    # Smoke + soft sparkles
    smoke_ribbon(big, anc["mouth_x"], anc["mouth_y"], SMOKE,
                 n_puffs=13, height_n=38, curl=1.6, start_radius=4)
    sparkles_around(big, anc["mouth_x"], anc["mouth_y"] - s(4),
                    n=3, radius_n=12, color=(255, 245, 200),
                    rng_seed=23)
    sparkles_around(big, cx, cy - s(6), n=3, radius_n=44,
                    color=PARCH_HI, rng_seed=24)


# ─────────────────────────────────────────────────────────────────────
# Variant 4 — Faceted Crystal. Pale-cyan crystal enamel body with
# large outlined diamond facets across the body + spout, multi-gem
# finial cluster at the spout tip, gold rim collar, heavy sparkle
# ring around the lamp.
# ─────────────────────────────────────────────────────────────────────

def draw_lamp_4_faceted(big, cx, cy):
    GOLD     = (255, 220, 110)
    GOLD_HI  = (255, 245, 175)
    GOLD_DK  = (180, 130,  40)
    RUBY     = (220,  55,  75)
    RUBY_HI  = (255, 175, 195)
    EMERALD  = ( 70, 175, 110)
    EMERALD_HI = (180, 240, 200)
    SAPPHIRE = ( 70, 100, 220)
    SAPPHIRE_HI = (175, 200, 255)
    # Cyan-family handle gem so the centre disc + gem read as one
    # monochrome element of the lamp body. Core sits darker than
    # body_pal["base"] so the gem still reads as a gem; highlight is
    # brighter than body_pal["hi"] so it pops at small footprint.
    CYAN_GEM    = ( 40, 100, 160)
    CYAN_GEM_HI = (170, 220, 245)
    WHITE    = (250, 250, 250)
    _render_faceted_lamp(
        big, cx, cy,
        body_pal={
            "dk":    ( 60, 130, 170),
            "base":  (130, 195, 220),
            "hi":    (220, 245, 255),
            "sheen": (255, 255, 255),
            "hole":  ( 55, 110, 145),
        },
        metal={"dk": GOLD_DK, "base": GOLD, "hi": GOLD_HI},
        gems={
            "handle_centre": ("round", CYAN_GEM, CYAN_GEM_HI, s(3)),
            "foot_dot":     (EMERALD, EMERALD_HI),
            "stopper_left": ("round", EMERALD, EMERALD_HI, s(2)),
            "stopper_centre": ("diamond", RUBY, RUBY_HI,
                                s(2) + s(1) // 2),
            "stopper_right":("round", SAPPHIRE, SAPPHIRE_HI, s(2)),
        },
        smoke=[WHITE, (195, 235, 255), (130, 195, 235),
               ( 75, 145, 200)],
    )


def _render_faceted_lamp(big, cx, cy, body_pal, metal, gems, smoke):
    """Shared render for the Faceted Crystal design. Each call uses
    a different body palette + metal + gem set so the silhouette +
    facet pattern + ornaments are identical; only the colour scheme
    changes."""
    # Convenience aliases so the body code reads naturally
    M_DK    = metal["dk"]
    M       = metal["base"]
    M_HI    = metal["hi"]
    pal     = body_pal
    GOLD_DK = M_DK
    GOLD    = M
    GOLD_HI = M_HI
    SMOKE   = smoke
    WHITE   = (250, 250, 250)
    # Unpack gem set
    h_gem_type, h_gem_col, h_gem_hi, h_gem_r = gems["handle_centre"]
    foot_dot_col, foot_dot_hi = gems["foot_dot"]
    EMERALD, EMERALD_HI = foot_dot_col, foot_dot_hi
    sl_type, sl_col, sl_hi, sl_r = gems["stopper_left"]
    sc_type, sc_col, sc_hi, sc_r = gems["stopper_centre"]
    sr_type, sr_col, sr_hi, sr_r = gems["stopper_right"]

    anc = lamp_silhouette(cx, cy)

    # ─── Outline glow (subtle dark-navy halo) ────────────────────
    # The crystal palette is close to the bright DAY-biome sky tones.
    # A soft dark halo hugging the silhouette gives the lamp a
    # consistent silhouette separation against ANY sky colour: it
    # darkens the area behind bright skies (day) and disappears
    # against dark skies (night) where it's not needed.
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

    paint_lamp_body(big, anc, pal)

    bw, bh = anc["bw"], anc["bh"]
    body_cy = anc["body_cy"]

    # Cut-crystal facets — large outlined diamonds across the body.
    # Sparse arrangement so the silhouette stays readable.
    facet_clip = pygame.Surface((PW, PH), pygame.SRCALPHA)

    def draw_facet(fcx, fcy, fw, fh):
        # Skip facets too close to the body edge
        if abs(fcx - cx) + fw // 2 > bw // 2 - s(3):
            return
        if abs(fcy - body_cy) + fh // 2 > bh // 2 - s(2):
            return
        pts = [(fcx, fcy - fh // 2),
               (fcx + fw // 2, fcy),
               (fcx, fcy + fh // 2),
               (fcx - fw // 2, fcy)]
        # Inner shadow half (lower-right triangle)
        shadow_tri = [pts[0], pts[1], pts[2]]
        pygame.draw.polygon(facet_clip, (*pal["dk"], 110),
                            shadow_tri)
        # Full outline — sheen white
        pygame.draw.polygon(facet_clip, (*pal["sheen"], 250),
                            pts, max(3, s(1) + 1))
        # Light edge (upper-left)
        pygame.draw.line(facet_clip, (*pal["sheen"], 255),
                         pts[3], pts[0], max(2, s(1)))
        # Catch-light dot
        pygame.draw.circle(facet_clip, (255, 255, 255, 255),
                           (int(fcx - fw // 5),
                            int(fcy - fh // 5)),
                           max(2, s(1)))

    # Row of 5 facets across the body
    for j in range(5):
        t = (j + 0.5) / 5
        fx = cx - bw // 2 + s(6) + (bw - s(12)) * t
        # Alternate vertical position for visual interest
        fy_off = s(2) if j % 2 == 1 else -s(2)
        draw_facet(fx, body_cy + fy_off, s(10), s(11))
    # Center large facet
    draw_facet(cx, body_cy, s(13), s(14))
    clip_to_body(facet_clip, anc["body_pts"])
    big.blit(facet_clip, (0, 0))

    # Facet treatment on the spout — a few small diamonds along the
    # outer curve
    spa_x, spa_y = anc["spa_x"], anc["spa_y"]
    for t_frac in (0.3, 0.55, 0.78):
        outer = anc["outer_pts"]
        idx = max(0, min(len(outer) - 2, int(t_frac * (len(outer) - 1))))
        a = outer[idx]
        b = outer[idx + 1]
        mx, my = (a[0] + b[0]) // 2, (a[1] + b[1]) // 2
        # Shift inward slightly so facet stays on the spout
        ang = math.atan2(b[1] - a[1], b[0] - a[0])
        nx = math.cos(ang + math.pi / 2)
        ny = math.sin(ang + math.pi / 2)
        fcx = mx + nx * s(2)
        fcy = my + ny * s(2)
        pts = [(fcx, fcy - s(2)),
               (fcx + s(2), fcy),
               (fcx, fcy + s(2)),
               (fcx - s(2), fcy)]
        pygame.draw.polygon(big, pal["sheen"], pts, max(2, s(1)))
        aa_circle(big, (255, 255, 255),
                  fcx - s(1) // 2, fcy - s(1) // 2, max(1, s(1) // 2 + 1))

    # Gold rim collar where the spout joins the body
    pygame.draw.rect(big, NEAR_BLK,
                     (spa_x - s(2), spa_y - s(3),
                      s(9), s(7)))
    pygame.draw.rect(big, GOLD_DK,
                     (spa_x - s(1), spa_y - s(3),
                      s(8), s(7)))
    pygame.draw.rect(big, GOLD,
                     (spa_x - s(1), spa_y - s(2),
                      s(8), s(5)))
    pygame.draw.line(big, GOLD_HI,
                     (spa_x, spa_y - s(1)),
                     (spa_x + s(6), spa_y - s(1)),
                     max(1, s(1) // 2))

    # Multi-gem cluster finial at the spout tip
    fx = anc["mouth_x"]
    fy = anc["mouth_y"] - s(3)
    # Gold base disk
    pygame.draw.ellipse(big, NEAR_BLK,
                        (fx - s(5) - s(1) // 2,
                         fy + s(1) - s(1) // 2,
                         s(10) + s(1), s(4) + s(1)))
    pygame.draw.ellipse(big, GOLD_DK,
                        (fx - s(5), fy + s(1), s(10), s(4)))
    pygame.draw.ellipse(big, GOLD,
                        (fx - s(5) + s(1) // 2, fy + s(1) + s(1) // 2,
                         s(10) - s(1), s(3) - s(1)))
    # 3 gems clustered above — types + colours per the gem set
    def _stopper_gem(gtype, x, y, r, c, hi):
        if gtype == "diamond":
            gem_diamond(big, x, y, r, c, hi)
        else:
            gem_round(big, x, y, r, c, hi)
    _stopper_gem(sl_type, fx - s(3), fy, sl_r, sl_col, sl_hi)
    _stopper_gem(sc_type, fx, fy - s(2), sc_r, sc_col, sc_hi)
    _stopper_gem(sr_type, fx + s(3), fy, sr_r, sr_col, sr_hi)

    # Handle — metal torus with the chosen handle-centre gem
    handle_pal = {
        "dk":    GOLD_DK,
        "base":  GOLD,
        "hi":    GOLD_HI,
        # Hole reads as "lamp body showing through the handle ring",
        # so colour-match it to the body's base tone instead of a
        # hardcoded slate blue.
        "hole":  body_pal["base"],
    }
    paint_torus_handle(big, anc, handle_pal,
                       inner_gem=(h_gem_type, 0, 0,
                                  h_gem_r, h_gem_col, h_gem_hi))

    # Foot — metal ring with gem dots (using foot_dot palette)
    def foot_gems(big, cx_in, by, bw_in, bh_in):
        for gem_off in (-bw_in // 3, 0, bw_in // 3):
            aa_circle(big, NEAR_BLK,
                      cx_in + gem_off + s(1) // 2,
                      by + s(2) + s(1) // 2, max(2, s(1)))
            aa_circle(big, foot_dot_col, cx_in + gem_off, by + s(2),
                      max(1, s(1) + 1))
            aa_circle(big, foot_dot_hi,
                      cx_in + gem_off - s(1) // 2,
                      by + s(2) - s(1) // 2, max(1, s(1) // 2))
    paint_foot(big, anc, pal,
               band_colors=[(NEAR_BLK, 0.0),
                            (GOLD_DK,  0.20),
                            (GOLD,     0.55),
                            (GOLD_HI,  0.25)],
               extra_layer=foot_gems)

    # Smoke + heavy sparkle ring
    smoke_ribbon(big, anc["mouth_x"], anc["mouth_y"], SMOKE,
                 n_puffs=14, height_n=42, curl=1.7, start_radius=4)
    sparkles_around(big, cx, cy, n=14, radius_n=48,
                    color=WHITE, rng_seed=14)
    sparkles_around(big, cx, cy, n=6, radius_n=38,
                    color=(255, 245, 200), rng_seed=15)
    sparkles_around(big, fx, fy, n=6, radius_n=12,
                    color=WHITE, rng_seed=17)


# ─────────────────────────────────────────────────────────────────────
# Variant 5 — Celestial Nebula. Deep cosmic navy body, bright golden
# core star on the belly with halo + cross, constellation lines etched
# on the surface, comet-streak finial on the spout, silver + gold
# layered handle and foot.
# ─────────────────────────────────────────────────────────────────────

def draw_lamp_5_celestial(big, cx, cy):
    pal = {
        "dk":    (  8,  10,  40),
        "base":  ( 24,  22,  82),
        "hi":    ( 95,  78, 170),
        "sheen": (220, 215, 250),
        "hole":  ( 18,  15,  55),
    }
    GOLD     = (255, 220, 110)
    GOLD_HI  = (255, 245, 195)
    GOLD_DK  = (180, 130,  40)
    SILVER   = (215, 220, 240)
    SILVER_HI = (250, 250, 255)
    NEBULA_HINT = (130,  60, 200)
    CYAN     = (175, 230, 255)
    WHITE    = (250, 250, 250)
    SMOKE    = [(255, 250, 230), (220, 200, 255), (130, 110, 220),
                ( 80,  60, 180)]

    anc = lamp_silhouette(cx, cy)
    paint_lamp_body(big, anc, pal)

    bw, bh = anc["bw"], anc["bh"]
    body_cy = anc["body_cy"]

    # Subtle nebula clouds INSIDE the body silhouette (only barely
    # visible since the body is dark enamel — gives an "internal
    # cosmos hint" without breaking the metal feel)
    nebula_clip = pygame.Surface((PW, PH), pygame.SRCALPHA)
    rng = random.Random(9)
    for _ in range(6):
        nx = cx + rng.randint(-bw // 2 + s(5), bw // 2 - s(5))
        ny = body_cy + rng.randint(-bh // 2 + s(2), bh // 2 - s(3))
        nr = rng.randint(s(3), s(5))
        sub = pygame.Surface((nr * 2 + 4, nr * 2 + 4),
                             pygame.SRCALPHA)
        pygame.draw.circle(sub, (*NEBULA_HINT, 80),
                           (nr + 2, nr + 2), nr)
        nebula_clip.blit(sub, (nx - nr - 2, ny - nr - 2))
    clip_to_body(nebula_clip, anc["body_pts"])
    big.blit(nebula_clip, (0, 0))

    # Constellation lines etched on the body — 3 small constellations
    # arranged across the body
    constellations = [
        # (anchor_dx, anchor_dy, list_of_relative_pts)
        (-s(15), -s(4), [(0, 0), (s(4), -s(3)), (s(7), -s(1)),
                          (s(5), s(3))]),
        ( s(13), -s(5), [(0, 0), (-s(3), s(3)), (s(2), s(5))]),
        ( s(10), s(5),  [(0, 0), (s(3), s(3)), (s(6), s(1)),
                          (s(8), s(4))]),
    ]
    for ax, ay, rel_pts in constellations:
        abs_pts = [(cx + ax + p[0], body_cy + ay + p[1])
                   for p in rel_pts]
        # Connecting lines first
        pygame.draw.lines(big, SILVER, False, abs_pts,
                          max(2, s(1) // 2 + 1))
        # Star dots on top
        for px, py in abs_pts:
            aa_circle(big, NEAR_BLK, px + s(1) // 3,
                      py + s(1) // 3, max(2, s(1)))
            aa_circle(big, SILVER_HI, px, py, max(2, s(1)))
            aa_circle(big, WHITE, px - s(1) // 2, py - s(1) // 2,
                      max(1, s(1) // 2))

    # Bright golden core star at the centre of the belly
    core_x = cx + s(1)
    core_y = body_cy + s(1)
    # Halo
    for r_n, a in ((s(11), 60), (s(7), 130), (s(4), 220)):
        sub = pygame.Surface((r_n * 2 + 4, r_n * 2 + 4),
                             pygame.SRCALPHA)
        pygame.draw.circle(sub, (255, 240, 180, a),
                           (r_n + 2, r_n + 2), r_n)
        big.blit(sub, (core_x - r_n - 2, core_y - r_n - 2))
    # 4-point cross (long arms)
    for dx_, dy_ in ((s(11), 0), (-s(11), 0), (0, s(8)), (0, -s(8))):
        pygame.draw.line(big, (255, 240, 180),
                         (core_x, core_y),
                         (core_x + dx_, core_y + dy_),
                         max(2, s(1)))
    # 4-point star polygon (the central jewel)
    star_r = s(4)
    star_pts = []
    for j in range(8):
        ang = j * math.pi / 4 - math.pi / 2
        r = star_r if j % 2 == 0 else star_r // 2
        star_pts.append((core_x + math.cos(ang) * r,
                         core_y + math.sin(ang) * r))
    filled_poly(big, NEAR_BLK,
                [(x + s(1) // 3, y + s(1) // 3) for x, y in star_pts])
    filled_poly(big, GOLD, star_pts)
    aa_circle(big, GOLD_HI, core_x, core_y, max(2, s(1) + 1))
    aa_circle(big, WHITE, core_x - s(1) // 2, core_y - s(1) // 2,
              max(1, s(1)))

    # Silver + gold layered neck ring at spout base
    spa_x, spa_y = anc["spa_x"], anc["spa_y"]
    pygame.draw.rect(big, NEAR_BLK,
                     (spa_x - s(2), spa_y - s(3),
                      s(9), s(7)))
    pygame.draw.rect(big, GOLD_DK,
                     (spa_x - s(1), spa_y - s(3),
                      s(8), s(7)))
    pygame.draw.rect(big, GOLD,
                     (spa_x - s(1), spa_y - s(2),
                      s(8), s(3)))
    pygame.draw.rect(big, SILVER,
                     (spa_x - s(1), spa_y + s(1),
                      s(8), s(2)))

    # Comet finial on the spout — a silver streak running along the
    # upper outer curve of the spout, ending in a gold 4-point star
    # at the mouth.
    streak_start = (spa_x + s(8), spa_y - s(5))
    streak_end = (anc["mouth_x"], anc["mouth_y"] - s(1))
    # Tapered silver streak
    streak_pts = []
    n_streak = 12
    for k in range(n_streak):
        t = k / (n_streak - 1)
        # Follow the curve from start to end (via mid point)
        mid_x = (streak_start[0] + streak_end[0]) // 2 + s(4)
        mid_y = (streak_start[1] + streak_end[1]) // 2 - s(2)
        # Quadratic bezier-ish
        sx = (1 - t) ** 2 * streak_start[0] + 2 * (1 - t) * t * mid_x + \
             t ** 2 * streak_end[0]
        sy = (1 - t) ** 2 * streak_start[1] + 2 * (1 - t) * t * mid_y + \
             t ** 2 * streak_end[1]
        streak_pts.append((sx, sy))
    # Draw with tapered width (wider near the head)
    for k in range(len(streak_pts) - 1):
        t = k / (len(streak_pts) - 1)
        w = max(2, int(s(1) + t * s(2)))
        a = int(80 + t * 175)
        surf_l = pygame.Surface((PW, PH), pygame.SRCALPHA)
        pygame.draw.line(surf_l, (*SILVER, a),
                         streak_pts[k], streak_pts[k + 1], w)
        big.blit(surf_l, (0, 0))
    # Comet head — gold 4-point star at the mouth
    head_x, head_y = streak_end
    head_x -= s(1)
    head_y -= s(1)
    star_r = s(5)
    head_pts = []
    for j in range(8):
        ang = j * math.pi / 4 - math.pi / 2
        r = star_r if j % 2 == 0 else star_r // 2
        head_pts.append((head_x + math.cos(ang) * r,
                         head_y + math.sin(ang) * r))
    filled_poly(big, NEAR_BLK,
                [(x + s(1) // 3, y + s(1) // 3)
                 for x, y in head_pts])
    filled_poly(big, GOLD, head_pts)
    aa_circle(big, GOLD_HI, head_x, head_y, max(2, s(1) + 1))
    aa_circle(big, WHITE, head_x - s(1) // 2, head_y - s(1) // 2,
              max(1, s(1)))

    # Handle — silver + gold layered torus
    handle_pal = {
        "dk":    GOLD_DK,
        "base":  GOLD,
        "hi":    GOLD_HI,
        "hole":  ( 25,  20,  65),
    }
    paint_torus_handle(big, anc, handle_pal)
    # Silver inset accent on the handle (outer rim secondary ring)
    h_cx, h_cy = anc["h_cx"], anc["h_cy"]
    h_w, h_h = anc["h_w"], anc["h_h"]
    pygame.draw.ellipse(big, SILVER,
                        (h_cx - h_w // 2 + s(1),
                         h_cy - h_h // 2 + s(1),
                         h_w - s(2), h_h - s(2)), max(1, s(1) // 2))
    # Star dots on top + bottom of the ring
    for off in (-h_h // 2, h_h // 2 - s(1)):
        aa_circle(big, SILVER_HI, h_cx, h_cy + off, max(1, s(1) // 2 + 1))

    # Foot — silver + gold layered with star dots
    def foot_stars(big, cx_in, by, bw_in, bh_in):
        for dx in range(-bw_in // 2 + s(3), bw_in // 2, max(1, s(4))):
            aa_circle(big, SILVER_HI, cx_in + dx, by + s(2),
                      max(1, s(1) // 2 + 1))
    paint_foot(big, anc, pal,
               band_colors=[(NEAR_BLK, 0.0),
                            (GOLD_DK,  0.20),
                            (GOLD,     0.40),
                            (SILVER,   0.40)],
               extra_layer=foot_stars)

    # Smoke + cosmic sparkles
    smoke_ribbon(big, anc["mouth_x"] - s(2), anc["mouth_y"], SMOKE,
                 n_puffs=15, height_n=44, curl=2.2, start_radius=4)
    sparkles_around(big, cx, cy - s(2), n=10, radius_n=46,
                    color=WHITE, rng_seed=14)
    sparkles_around(big, cx, cy - s(2), n=5, radius_n=38,
                    color=CYAN, rng_seed=17)
    sparkles_around(big, head_x, head_y, n=5, radius_n=10,
                    color=(255, 245, 200), rng_seed=33)


# ─────────────────────────────────────────────────────────────────────
# Five colour variations of the Faceted Crystal design. Each shares
# the same silhouette, facet pattern, gold accents, ornaments and
# outline glow — only the body palette + gem set changes, so the
# lamp pops against the bright DAY-biome cyan sky in different ways.
# ─────────────────────────────────────────────────────────────────────

# Shared metal accent palette (warm gold)
_GOLD    = (255, 220, 110)
_GOLD_HI = (255, 245, 175)
_GOLD_DK = (180, 130,  40)
# Shared metal accent palette (cool silver) — used by colder variants
_SILVER    = (215, 220, 240)
_SILVER_HI = (250, 250, 255)
_SILVER_DK = (130, 145, 175)
# Gem swatches
_RUBY,    _RUBY_HI    = (220,  55,  75), (255, 175, 195)
_EMERALD, _EMERALD_HI = ( 70, 175, 110), (180, 240, 200)
_SAPPHIRE,_SAPPHIRE_HI= ( 70, 100, 220), (175, 200, 255)
_AMETHYST,_AMETHYST_HI= (155,  85, 220), (220, 180, 245)
_AMBER,   _AMBER_HI   = (240, 165,  50), (255, 220, 140)
_ROSE,    _ROSE_HI    = (235, 110, 160), (255, 195, 220)


def draw_color_1_teal(big, cx, cy):
    _render_faceted_lamp(
        big, cx, cy,
        body_pal={
            "dk":    ( 12,  72,  80),
            "base":  ( 45, 150, 145),
            "hi":    (140, 220, 215),
            "sheen": (235, 250, 245),
            "hole":  ( 25,  65,  70),
        },
        metal={"dk": _GOLD_DK, "base": _GOLD, "hi": _GOLD_HI},
        gems={
            "handle_centre": ("round", _RUBY, _RUBY_HI, s(3)),
            "foot_dot":     (_AMBER, _AMBER_HI),
            "stopper_left": ("round", _AMETHYST, _AMETHYST_HI, s(2)),
            "stopper_centre": ("diamond", _RUBY, _RUBY_HI,
                                s(2) + s(1) // 2),
            "stopper_right":("round", _AMBER, _AMBER_HI, s(2)),
        },
        smoke=[(250, 250, 250), (190, 235, 220), (110, 200, 175),
               ( 50, 145, 130)],
    )


def draw_color_2_emerald(big, cx, cy):
    _render_faceted_lamp(
        big, cx, cy,
        body_pal={
            "dk":    ( 14,  75,  40),
            "base":  ( 50, 160,  90),
            "hi":    (150, 230, 170),
            "sheen": (235, 255, 230),
            "hole":  ( 25,  70,  35),
        },
        metal={"dk": _GOLD_DK, "base": _GOLD, "hi": _GOLD_HI},
        gems={
            "handle_centre": ("round", _RUBY, _RUBY_HI, s(3)),
            "foot_dot":     (_SAPPHIRE, _SAPPHIRE_HI),
            "stopper_left": ("round", _SAPPHIRE, _SAPPHIRE_HI, s(2)),
            "stopper_centre": ("diamond", _RUBY, _RUBY_HI,
                                s(2) + s(1) // 2),
            "stopper_right":("round", _AMBER, _AMBER_HI, s(2)),
        },
        smoke=[(255, 250, 245), (200, 235, 205), (115, 200, 145),
               ( 55, 140,  85)],
    )


def draw_color_3_amber(big, cx, cy):
    _render_faceted_lamp(
        big, cx, cy,
        body_pal={
            "dk":    (115,  60,  10),
            "base":  (225, 145,  45),
            "hi":    (255, 215, 130),
            "sheen": (255, 245, 195),
            "hole":  ( 95,  50,  10),
        },
        metal={"dk": _GOLD_DK, "base": _GOLD, "hi": _GOLD_HI},
        gems={
            "handle_centre": ("round", _SAPPHIRE, _SAPPHIRE_HI, s(3)),
            "foot_dot":     (_EMERALD, _EMERALD_HI),
            "stopper_left": ("round", _EMERALD, _EMERALD_HI, s(2)),
            "stopper_centre": ("diamond", _SAPPHIRE, _SAPPHIRE_HI,
                                s(2) + s(1) // 2),
            "stopper_right":("round", _RUBY, _RUBY_HI, s(2)),
        },
        smoke=[(255, 250, 230), (250, 215, 165), (220, 145, 95),
               (150,  75,  35)],
    )


def draw_color_4_rose(big, cx, cy):
    _render_faceted_lamp(
        big, cx, cy,
        body_pal={
            "dk":    (110,  40,  70),
            "base":  (225, 115, 155),
            "hi":    (250, 195, 220),
            "sheen": (255, 235, 245),
            "hole":  ( 90,  35,  60),
        },
        metal={"dk": _GOLD_DK, "base": _GOLD, "hi": _GOLD_HI},
        gems={
            "handle_centre": ("round", _EMERALD, _EMERALD_HI, s(3)),
            "foot_dot":     (_AMETHYST, _AMETHYST_HI),
            "stopper_left": ("round", _EMERALD, _EMERALD_HI, s(2)),
            "stopper_centre": ("diamond", _AMETHYST, _AMETHYST_HI,
                                s(2) + s(1) // 2),
            "stopper_right":("round", _AMBER, _AMBER_HI, s(2)),
        },
        smoke=[(255, 250, 250), (250, 215, 230), (230, 155, 195),
               (160,  75, 120)],
    )


def draw_color_5_amethyst(big, cx, cy):
    _render_faceted_lamp(
        big, cx, cy,
        body_pal={
            "dk":    ( 55,  20, 105),
            "base":  (135,  75, 210),
            "hi":    (210, 170, 240),
            "sheen": (240, 230, 250),
            "hole":  ( 40,  18,  85),
        },
        metal={"dk": _GOLD_DK, "base": _GOLD, "hi": _GOLD_HI},
        gems={
            "handle_centre": ("round", _AMBER, _AMBER_HI, s(3)),
            "foot_dot":     (_EMERALD, _EMERALD_HI),
            "stopper_left": ("round", _EMERALD, _EMERALD_HI, s(2)),
            "stopper_centre": ("diamond", _AMBER, _AMBER_HI,
                                s(2) + s(1) // 2),
            "stopper_right":("round", _ROSE, _ROSE_HI, s(2)),
        },
        smoke=[(255, 250, 255), (220, 195, 245), (160, 110, 215),
               ( 90,  50, 170)],
    )


LAMPS = [
    ("1: Teal Crystal",     draw_color_1_teal),
    ("2: Emerald Crystal",  draw_color_2_emerald),
    ("3: Amber Crystal",    draw_color_3_amber),
    ("4: Rose Crystal",     draw_color_4_rose),
    ("5: Amethyst Crystal", draw_color_5_amethyst),
]


def render_one(fn, display_scale):
    big = pygame.Surface((PW, PH), pygame.SRCALPHA)
    big.fill(SKY)
    cx = PW // 2
    cy = PH // 2
    fn(big, cx, cy)
    out_w = W * display_scale
    out_h = H * display_scale
    return pygame.transform.smoothscale(big, (out_w, out_h))


def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else "v1"
    DW = W * DISPLAY_BIG
    DH = H * DISPLAY_BIG
    SW = W * DISPLAY_SMALL
    SH = H * DISPLAY_SMALL
    cols, rows = 3, 2
    margin = 18
    label_h = 28
    small_band_h = SH + 8
    cell_h = DH + label_h + small_band_h + 8
    sheet_w = DW * cols + margin * (cols + 1)
    sheet_h = cell_h * rows + margin * (rows + 1)
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((22, 24, 32))
    font_big = pygame.font.SysFont("Arial", 20, bold=True)
    font_small = pygame.font.SysFont("Arial", 11)
    small_caption = font_small.render("in-game scale", True,
                                       (170, 180, 200))
    for i in range(cols * rows):
        col, row = i % cols, i // cols
        x = margin + col * (DW + margin)
        y = margin + row * (cell_h + margin)
        if i >= len(LAMPS):
            pygame.draw.rect(sheet, (30, 32, 42),
                             (x - 2, y - 2, DW + 4, DH + 4))
            continue
        label, fn = LAMPS[i]
        portrait = render_one(fn, DISPLAY_BIG)
        small = render_one(fn, DISPLAY_SMALL)
        pygame.draw.rect(sheet, (60, 65, 80),
                         (x - 2, y - 2, DW + 4, DH + 4), 2)
        sheet.blit(portrait, (x, y))
        text = font_big.render(label, True, (240, 240, 240))
        sheet.blit(text, (x + (DW - text.get_width()) // 2,
                          y + DH + 2))
        sb_y = y + DH + label_h + 6
        for k in range(3):
            sx = x + 10 + k * (SW + 12) + ((DW - 3 * SW - 24) // 2)
            sheet.blit(small, (sx, sb_y))
            pygame.draw.rect(sheet, (50, 55, 70),
                             (sx - 1, sb_y - 1, SW + 2, SH + 2), 1)
        sheet.blit(small_caption,
                   (x + DW - small_caption.get_width() - 8,
                    sb_y + SH - 2))
        ind_path = os.path.join(OUT_DIR, f"colorlamp_{i + 1}_{tag}.png")
        pygame.image.save(portrait, ind_path)
    out = os.path.join(OUT_DIR, f"colorlamp_sheet_{tag}.png")
    pygame.image.save(sheet, out)
    print(f"saved {out}  ({sheet_w}x{sheet_h})")


if __name__ == "__main__":
    main()
