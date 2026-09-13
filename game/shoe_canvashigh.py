"""CANVAS HIGH — black canvas basketball HIGH-TOP homage.

Drawn entirely from pygame primitives so it survives the full size range:
the SAME function is the ~104×62 product shot AND a ~15×10 sprite on the
bird's feet. Geometry is expressed as fractions of the (x, y, w, h) box so it
scales cleanly; stroke widths clamp to >=1px so detail never vanishes tiny.

It is a HOMAGE in the spirit of the game's KFC parody theme — the classic
black-canvas hi-top colorway and silhouette with stylized cues (white rubber
toe cap, white foxing stripe, cream outsole, a plain generic star on the
ankle), never an exact trademarked mark. The ankle mark is deliberately a
bare flat star — NO ringed roundel, no concentric border — so it can't read
as a real brand medallion. No text, no logo.

The READ is the silhouette: the high-top collar deliberately rises ABOVE the
box top (v < 0), so callers / previews must leave vertical headroom.
"""
import pygame


# Black canvas upper with a near-black shadow tint (not pure black, so the 1px
# edges read against a dark navy field). The body is pushed DARKER so the
# three-part read — collar / white toe / cream sole — is unmistakable on the
# dark navy Store field. White rubber + cream outsole are the contrast.
_CANVAS    = (20, 20, 24)
_CANVAS_S  = (10, 10, 14)      # canvas shadow / seam
# Toe cap + foxing pushed near-white; the foxing band is one value brighter
# than the cream outsole so it still separates from the sole after downscale.
_RUBBER    = (252, 252, 250)   # white toe cap + foxing stripe (near-white)
_RUBBER_S  = (214, 214, 210)   # 1px rubber edge
_SOLE      = (228, 222, 206)   # cream vulcanized outsole face (below rubber)
_SOLE_EDGE = (190, 184, 168)   # 1px sole edge
# Bare flat star (no ring, no disc) — an unmistakably generic mark.
_STAR      = (150, 60, 60)     # muted red ankle star
_LACE      = (228, 228, 222)
_EYELET    = (150, 150, 156)

# Below this device width the only cues are silhouette + white toe + sole;
# laces and the ankle star are dropped so they don't smear into mush.
_DETAIL_MIN_W = 24


def _u(u, v, x, y, w, h, facing):
    """Map unit-box (u, v) to device pixels, mirroring about u=0.5 when facing
    left so one core serves both feet / both store orientations. v may be < 0:
    the hi-top collar lives above the box top."""
    if facing < 0:
        u = 1.0 - u
    return (int(round(x + u * w)), int(round(y + v * h)))


def _poly(surf, color, pts, x, y, w, h, facing):
    pygame.draw.polygon(surf, color, [_u(u, v, x, y, w, h, facing)
                                      for u, v in pts])


def _line(surf, color, a, b, x, y, w, h, facing, width):
    pygame.draw.line(surf, color, _u(*a, x, y, w, h, facing),
                     _u(*b, x, y, w, h, facing), max(1, int(round(width))))


def _star(surf, color, cu, cv, ru, rv, x, y, w, h, facing):
    """A bare generic 5-point star (NOT a trademark — no ring, no surrounding
    disc) of radius (ru, rv) about (cu, cv). Points up; alternates radii."""
    import math
    inner = 0.42  # inner-to-outer radius ratio of a classic 5-point star
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = 1.0 if i % 2 == 0 else inner
        pts.append((cu + math.cos(ang) * ru * rr,
                    cv + math.sin(ang) * rv * rr))
    # Mirror handling is done per-point by _u, so build in unit space directly.
    dev = [_u(pu, pv, x, y, w, h, facing) for pu, pv in pts]
    pygame.draw.polygon(surf, color, dev)


def draw_shoe(surf, x, y, w, h, facing=1):
    """Draw a single side-profile CANVAS HIGH sneaker into box (x, y, w, h).

    Toe points RIGHT when facing=1 (mirrored for -1). High-top: the ankle
    collar rises above y; the cream vulcanized outsole is the bottom ~22% of h
    with a white foxing stripe along its top. No outer outline — the caller
    adds the house outline.
    """
    # ── cream vulcanized outsole (bottom ~22%) ────────────────────────────
    # A flat-bottomed vulcanized cupsole with a softly upturned toe — the
    # basketball-hi-top read, not a chunky runner. Edge first, cream face on top.
    sole = [(0.05, 0.80), (0.92, 0.80), (0.99, 0.86), (0.97, 0.99),
            (0.06, 0.99), (0.02, 0.90)]
    _poly(surf, _SOLE_EDGE, sole, x, y, w, h, facing)
    sole_face = [(0.06, 0.82), (0.92, 0.82), (0.97, 0.88), (0.95, 0.97),
                 (0.07, 0.97), (0.04, 0.90)]
    _poly(surf, _SOLE, sole_face, x, y, w, h, facing)

    # ── CUE · white foxing stripe along the top of the sole ───────────────
    # The rubber bumper band that wraps the whole shoe just above the outsole.
    # Drawn as a CONTINUOUS thick band one value brighter than the cream sole
    # so it survives downscale without merging into it; clamps to >=2px so the
    # white band is never lost on the foot-sprite.
    _line(surf, _RUBBER_S, (0.03, 0.795), (0.97, 0.805), x, y, w, h, facing,
          max(3, h * 0.13))
    _line(surf, _RUBBER, (0.04, 0.78), (0.95, 0.79), x, y, w, h, facing,
          max(2, h * 0.10))

    # ── black canvas upper — HIGH-TOP, collar rises above the box ─────────
    # Heel at left, ankle cuff sweeping up and out of the box (v down to ~-0.30),
    # vamp dropping to the toe. The tall back collar IS the silhouette read.
    upper = [(0.07, 0.80), (0.05, 0.30), (0.06, -0.18), (0.10, -0.28),
             (0.26, -0.30), (0.34, -0.22), (0.34, 0.06), (0.46, 0.16),
             (0.70, 0.24), (0.88, 0.40), (0.93, 0.62), (0.92, 0.80)]
    _poly(surf, _CANVAS_S, upper, x, y, w, h, facing)
    upper_face = [(0.09, 0.79), (0.075, 0.30), (0.085, -0.16), (0.115, -0.255),
                  (0.255, -0.275), (0.315, -0.205), (0.315, 0.07),
                  (0.46, 0.18), (0.695, 0.255), (0.865, 0.41), (0.915, 0.62),
                  (0.905, 0.79)]
    _poly(surf, _CANVAS, upper_face, x, y, w, h, facing)

    # Collar opening notch — the ankle cuff's inner curve, a tonal shadow that
    # gives the hi-top its open-cuff depth.
    _poly(surf, _CANVAS_S, [(0.135, -0.20), (0.30, -0.22), (0.315, 0.02),
                            (0.26, 0.08), (0.18, 0.00)], x, y, w, h, facing)

    # ── CUE · white rounded rubber toe cap ────────────────────────────────
    # Hard-snapped to ~30% of shoe width as a SOLID white block so it survives
    # the foot-sprite as a clean bright mass (not a thin pale wedge). The cap
    # spans u≈0.67→0.97 and bites high up the vamp; rounded leading edge.
    toe = [(0.67, 0.80), (0.685, 0.34), (0.80, 0.35), (0.93, 0.55),
           (0.97, 0.73), (0.93, 0.81)]
    _poly(surf, _RUBBER_S, toe, x, y, w, h, facing)
    toe_face = [(0.69, 0.79), (0.705, 0.37), (0.795, 0.38), (0.905, 0.56),
                (0.945, 0.73), (0.91, 0.80)]
    _poly(surf, _RUBBER, toe_face, x, y, w, h, facing)
    # Rounded toe tip so the cap never reads as a hard corner, even tiny.
    tip = _u(0.885, 0.62, x, y, w, h, facing)
    pygame.draw.circle(surf, _RUBBER, tip, max(2, int(round(w * 0.075))))
    # Toe-cap stitch seam where the rubber meets canvas — only at larger sizes
    # so the cap stays a clean solid block when small.
    if w >= _DETAIL_MIN_W:
        _line(surf, _RUBBER_S, (0.685, 0.36), (0.675, 0.79), x, y, w, h,
              facing, max(1, w * 0.012))

    # ── lace throat — a couple of bold lace bars up the high tongue ───────
    # Detail-only: below _DETAIL_MIN_W the laces would smear to gray mush, so
    # the small sizes rely on silhouette + white toe + sole alone. At size we
    # draw just TWO thick lace marks (three turned to mush) with dot eyelets.
    if w >= _DETAIL_MIN_W:
        bar_w = max(2, h * 0.07)
        for lv in (0.08, -0.08):
            _line(surf, _LACE, (0.36, lv), (0.50, lv - 0.05), x, y, w, h,
                  facing, bar_w)
        erad = max(1, int(round(w * 0.016)))
        for ev in (0.10, -0.06):
            pygame.draw.circle(surf, _EYELET,
                               _u(0.345, ev, x, y, w, h, facing), erad)

    # ── CUE · bare generic star on the ankle ──────────────────────────────
    # DELIBERATELY NOT a ringed roundel/medallion (which would read as a real
    # brand mark) — just a single flat star floating on the canvas, no disc,
    # no border ring. Detail-only: dropped below _DETAIL_MIN_W so small sizes
    # rely on silhouette + white toe + sole.
    if w >= _DETAIL_MIN_W:
        pcu, pcv = 0.21, 0.04
        sr_dev = w * 0.075
        # ru/rv are unit-box fractions; equalise device radius (ru*w == rv*h)
        # so the star stays visually round regardless of box aspect.
        _star(surf, _STAR, pcu, pcv, sr_dev / w, sr_dev / h,
              x, y, w, h, facing)
