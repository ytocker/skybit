"""Five CHEERFUL outer-RING concepts for the Hall of Shame medallions.

The brief: the live tarnished cracked-pewter ring reads too grim. These five
reinvent ONLY the frame (rim / laurel-substitute / step / face backing /
palette / festive trim) so the medal lands as a tongue-in-cheek booby prize —
clearly NOT the gold Fame medal, but fun rather than bleak. The center emblem
is untouched: every concept stamps the real engraved glyph via the live
``_stamp_glyph`` so the joke shape still carries.

Each ``ring_<name>(surf, cx, cy, R, glyph_key)`` draws a COMPLETE medallion at
supersample scale (caller smoothscales down), reusing the live module's
``_draw_step`` / ``_draw_face`` / ``_stamp_glyph`` / ``lerp_color`` /
``blit_glow`` low-level helpers but giving each ring its own bottom-up
construction + palette so the five are distinct in KIND, not finish. No
diagonal crack on any of them (the gloom cue is gone by design).

WRITE-ONLY scratch — never bundled. Imports ``game`` read-only.
"""
from __future__ import annotations

import math
import pygame

import game.achievement_icons as ai
from game.draw import lerp_color, blit_glow

_LIGHT = ai._LIGHT  # share the family's one upper-left light source


# ── shared low-level helpers (a bevel / a glyph stamp are fine to share; the
#    FRAME silhouette of each concept is bespoke below) ─────────────────────────

def _radial_face(surf, cx, cy, fr, top, bot, recess):
    """Recessed disc backing, reusing the live face routine so the center sits
    in a real struck well rather than on a flat fill."""
    ai._draw_face(surf, cx, cy, fr, top, bot, recess)


def _center(surf, glyph_key, cx, cy, R, gly, gly_sh, sheen=None):
    gr = int(R * 0.56)
    ai._stamp_glyph(surf, glyph_key, cx, cy, gr, gly, gly_sh, sheen)


def _smooth_band(surf, cx, cy, R, inner, hi, lo, spec=None,
                 spec_span=0.55, light=_LIGHT):
    """A generic lit metal/material band from R inward to ``inner`` under the
    one upper-left light — shared bevel math, each concept feeds its own
    palette so the band MATERIAL differs (plastic, wood, fabric, wax)."""
    for i in range(R, inner, -1):
        t = (R - i) / max(1, R - inner)
        pygame.draw.circle(surf, lerp_color(hi, lo, t * 0.6 + 0.2), (cx, cy), i)
    steps = 56
    band = (R - inner)
    for seg in range(steps):
        a0 = seg / steps * math.tau
        a1 = (seg + 1) / steps * math.tau
        d = (math.cos(a0 - light) + 1) * 0.5
        col = lerp_color(lo, hi, d ** 1.4)
        rect = pygame.Rect(cx - R + band // 3, cy - R + band // 3,
                           (R - band // 3) * 2, (R - band // 3) * 2)
        pygame.draw.arc(surf, col, rect, -a1, -a0, max(2, band - band // 3))
    if spec is not None:
        mid_r = (R + inner) // 2
        hot = pygame.Rect(cx - mid_r, cy - mid_r, mid_r * 2, mid_r * 2)
        pygame.draw.arc(surf, spec, hot, light - spec_span, light + spec_span,
                        max(2, band // 2))


# ═══════════════════════════════════════════════════════════════════════════
# 1) ROSETTE — "Participation Award" pleated ribbon rosette.
#    A soft fabric medal: a fan of cream pleats radiating under a sky-blue
#    button disc, with two wavy ribbon tails dangling below. Everyone's-a-winner
#    booby prize. Palette: sky blue + cream + soft gold button.
# ═══════════════════════════════════════════════════════════════════════════
_ROS_PLEAT_HI = (236, 244, 252)   # cream pleat crest
_ROS_PLEAT_LO = (150, 184, 220)   # pleat valley (blue shadow)
_ROS_DISC_HI  = (150, 206, 244)   # sky-blue button crest
_ROS_DISC_LO  = ( 70, 132, 196)   # button shadow
_ROS_DISC_EDGE = ( 40,  86, 150)
_ROS_RIBBON_HI = (132, 196, 240)
_ROS_RIBBON_LO = ( 60, 120, 188)
_ROS_FACE_TOP = (224, 238, 250)   # bright fabric well — cheerful, not navy
_ROS_FACE_BOT = (158, 192, 226)
_ROS_RECESS   = (108, 150, 196)
_ROS_GLY      = ( 44,  88, 148)   # engraved glyph reads as stitched thread
_ROS_GLY_SH   = (200, 224, 244)


def _ribbon_tail(surf, x, top, length, w, hi, lo, sgn):
    """A wavy ribbon tail with a notched fishtail end."""
    pts_l, pts_r = [], []
    for i in range(8):
        f = i / 7
        yy = top + int(length * f)
        # splay outward (a participation-ribbon V) + a gentle wave for cloth feel
        splay = int(f * length * 0.34 * sgn)
        wave = int(math.sin(f * math.pi * 1.4) * w * 0.30 * sgn)
        off = splay + wave
        pts_l.append((x - w // 2 + off, yy))
        pts_r.append((x + w // 2 + off, yy))
    poly = pts_l + pts_r[::-1]
    pygame.draw.polygon(surf, lerp_color(hi, lo, 0.35),
                        [(int(a), int(b)) for a, b in poly])
    # lit edge down the left of the tail (one upper-left light)
    pygame.draw.lines(surf, hi, False, [(int(a), int(b)) for a, b in pts_l],
                      max(2, w // 6))
    # fishtail notch at the bottom
    bx, by = pts_l[-1][0], pts_l[-1][1]
    ex = pts_r[-1][0]
    pygame.draw.polygon(surf, lo, [
        (int(bx), int(by)), (int(ex), int(by)),
        (int((bx + ex) // 2), int(by - w * 0.55))])


def ring_rosette(surf, cx, cy, R, glyph_key):
    # Two ribbon tails first, behind everything, fanning OUT below the rosette so
    # their fishtail ends clear the pleats — the dangling-streamer read of a
    # participation ribbon. They start near the bottom of the disc and splay.
    tail_w = int(R * 0.42)
    for sgn in (-1, 1):
        sx = cx + sgn * int(R * 0.22)
        _ribbon_tail(surf, sx, cy + int(R * 0.74),
                     int(R * 1.30), tail_w, _ROS_RIBBON_HI, _ROS_RIBBON_LO, sgn)

    # Pleated fabric fan — wedges of cream radiating from the centre, each lit
    # by its facing to the upper-left light. This IS the rosette frame.
    pleats = 24
    outer = int(R * 1.16)
    inner = int(R * 0.70)
    for i in range(pleats):
        a0 = i / pleats * math.tau
        a1 = (i + 1) / pleats * math.tau
        am = (a0 + a1) / 2
        d = (math.cos(am - _LIGHT) + 1) * 0.5
        # alternate crest/valley so the fabric reads as folded pleats — the
        # fold contrast is flattened ~15% (compressed toward its midpoint) so the
        # pleats stay a soft frame and don't fight the centre emblem at 44px.
        fold = 0.79 if i % 2 == 0 else 0.38
        col = lerp_color(_ROS_PLEAT_LO, _ROS_PLEAT_HI, (d ** 1.2) * fold + 0.14)
        p = [
            (cx + math.cos(a0) * inner, cy + math.sin(a0) * inner),
            (cx + math.cos(a0) * outer, cy + math.sin(a0) * outer),
            (cx + math.cos(a1) * outer, cy + math.sin(a1) * outer),
            (cx + math.cos(a1) * inner, cy + math.sin(a1) * inner),
        ]
        pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in p])
    # scalloped outer hem so the pleats end in soft fabric bumps, not a hard ring
    for i in range(pleats // 2):
        a = (i + 0.5) / (pleats // 2) * math.tau
        hx = cx + int(math.cos(a) * outer)
        hy = cy + int(math.sin(a) * outer)
        d = (math.cos(a - _LIGHT) + 1) * 0.5
        pygame.draw.circle(surf, lerp_color(_ROS_PLEAT_LO, _ROS_PLEAT_HI, d),
                           (hx, hy), max(3, R // 12))

    # Sky-blue button disc — the rosette's centre boss the well sits in.
    disc_R = int(R * 0.82)
    _smooth_band(surf, cx, cy, disc_R, int(disc_R * 0.62),
                 _ROS_DISC_HI, _ROS_DISC_LO, spec=(220, 244, 255))
    pygame.draw.circle(surf, _ROS_DISC_EDGE, (cx, cy), disc_R, max(2, R // 26))

    fr = int(R * 0.56)
    ai._draw_step(surf, cx, cy, fr + max(2, R // 16), _ROS_DISC_HI, _ROS_DISC_LO)
    _radial_face(surf, cx, cy, fr, _ROS_FACE_TOP, _ROS_FACE_BOT, _ROS_RECESS)
    # cross-stitch dots around the well so it reads as sewn-on fabric
    for i in range(10):
        a = i / 10 * math.tau - 0.2
        sx = cx + int(math.cos(a) * fr * 0.92)
        sy = cy + int(math.sin(a) * fr * 0.92)
        pygame.draw.circle(surf, _ROS_GLY, (sx, sy), max(1, R // 30))
    _center(surf, glyph_key, cx, cy, R, _ROS_GLY, _ROS_GLY_SH)


# ═══════════════════════════════════════════════════════════════════════════
# 2) SPOON — "Wooden Spoon" booby prize.
#    A warm oak rim with a wood-grain sheen, and a big wooden cooking spoon
#    crossing behind the disc — paddle up-left, handle down-right — the classic
#    last-place award. Palette: honey/oak browns + cream highlight.
# ═══════════════════════════════════════════════════════════════════════════
# Lifted off muddy oak toward a cheerful honey/blonde maple: brighter, warmer,
# higher value so the medal feels playful rather than earthbound.
_SPN_RIM_HI  = (252, 222, 160)    # lit blonde crest
_SPN_RIM_MID = (224, 176, 110)    # honey body
_SPN_RIM_LO  = (170, 118,  62)    # warm shadow (not muddy brown)
_SPN_RIM_EDGE = (120,  78,  36)
_SPN_SPEC    = (255, 240, 204)
_SPN_WOOD_HI = (248, 210, 146)    # spoon lit face — bright blonde
_SPN_WOOD_LO = (188, 132,  74)    # spoon warm shadow
_SPN_FACE_TOP = (255, 244, 220)   # creamy well
_SPN_FACE_BOT = (224, 192, 148)
_SPN_RECESS   = (176, 138,  96)
_SPN_GLY      = (150,  98,  48)   # toasty branding read on pale wood
_SPN_GLY_SH   = (255, 240, 214)


def _wood_spoon(surf, cx, cy, R, hi, lo):
    # The spoon stands UP behind the medal: a fat bowl poking clearly ABOVE the
    # top of the rim (the unmistakable spoon read) with the tapered handle
    # running down through the disc to the lower-right. Tilted slightly so it
    # feels jaunty, not stiff. The bowl-above-rim is the whole legibility fix.
    ang = math.radians(-118)             # bowl up (+slightly right), handle down
    ca, sa = math.cos(ang), math.sin(ang)

    def rot(px, py):
        # +x runs base->bowl (up), +y across the spoon's width.
        return (cx + px * ca - py * sa, cy + px * sa + py * ca)

    # handle — a long tapered quad from below the disc up toward the bowl
    h0 = rot(-R * 1.30, -R * 0.11)
    h1 = rot(-R * 1.30, R * 0.11)
    h2 = rot(R * 0.74, R * 0.05)
    h3 = rot(R * 0.74, -R * 0.05)
    pygame.draw.polygon(surf, lerp_color(hi, lo, 0.38),
                        [(int(x), int(y)) for x, y in (h0, h1, h2, h3)])
    pygame.draw.polygon(surf, _SPN_RIM_EDGE,
                        [(int(x), int(y)) for x, y in (h0, h1, h2, h3)],
                        max(2, R // 30))
    pygame.draw.line(surf, hi, (int(h0[0]), int(h0[1])),
                     (int(h3[0]), int(h3[1])), max(2, R // 24))
    # rounded handle end-knob at the bottom
    kx, ky = rot(-R * 1.30, 0)
    pygame.draw.circle(surf, lerp_color(hi, lo, 0.42),
                       (int(kx), int(ky)), max(3, R // 13))
    pygame.draw.circle(surf, _SPN_RIM_EDGE, (int(kx), int(ky)),
                       max(3, R // 13), max(1, R // 34))

    # bowl — a fat oval whose centre sits ABOVE the top of the rim so a clear
    # spoon-head reads, drawn as a rotated ellipse via a polygon ring.
    pcx, pcy = rot(R * 1.18, 0)
    pw, ph = R * 0.86, R * 0.62        # long axis along the handle (+x)
    pts = []
    for i in range(28):
        t = i / 28 * math.tau
        ex = pw * math.cos(t)
        ey = ph * math.sin(t)
        pts.append((pcx + ex * ca - ey * sa, pcy + ex * sa + ey * ca))
    pygame.draw.polygon(surf, lerp_color(hi, lo, 0.34),
                        [(int(x), int(y)) for x, y in pts])
    pygame.draw.polygon(surf, _SPN_RIM_EDGE,
                        [(int(x), int(y)) for x, y in pts], max(2, R // 26))
    # concave scoop — a smaller inset oval in a darker tone + a lit crescent so
    # the bowl reads as the hollow of a spoon, not a flat paddle.
    icx, icy = rot(R * 1.22, 0)
    ipts = []
    for i in range(24):
        t = i / 24 * math.tau
        ex = pw * 0.60 * math.cos(t)
        ey = ph * 0.60 * math.sin(t)
        ipts.append((icx + ex * ca - ey * sa, icy + ex * sa + ey * ca))
    pygame.draw.polygon(surf, lerp_color(hi, lo, 0.62),
                        [(int(x), int(y)) for x, y in ipts])
    pygame.draw.lines(surf, hi, True,
                      [(int(x), int(y)) for x, y in pts[7:16]], max(2, R // 22))


def ring_spoon(surf, cx, cy, R, glyph_key):
    _wood_spoon(surf, cx, cy, R, _SPN_WOOD_HI, _SPN_WOOD_LO)

    # Oak rim band with a faint wood-grain — concentric arcs + a few grain
    # streaks so it reads as turned wood, not metal.
    _smooth_band(surf, cx, cy, R, int(R * 0.72),
                 _SPN_RIM_HI, _SPN_RIM_LO, spec=_SPN_SPEC, spec_span=0.6)
    for k in range(5):
        ga = _LIGHT + math.radians(-40 + k * 20)
        rr0 = int(R * 0.74)
        rr1 = int(R * 0.99)
        gx0 = cx + int(math.cos(ga) * rr0)
        gy0 = cy + int(math.sin(ga) * rr0)
        gx1 = cx + int(math.cos(ga) * rr1)
        gy1 = cy + int(math.sin(ga) * rr1)
        pygame.draw.line(surf, _SPN_RIM_LO, (gx0, gy0), (gx1, gy1), max(1, R // 40))
    pygame.draw.circle(surf, _SPN_RIM_MID, (cx, cy), R, max(2, R // 22))
    pygame.draw.circle(surf, _SPN_RIM_EDGE, (cx, cy), R, max(1, R // 36))

    fr = int(R * 0.70)
    ai._draw_step(surf, cx, cy, fr + max(2, R // 16), _SPN_RIM_HI, _SPN_RIM_LO)
    _radial_face(surf, cx, cy, fr, _SPN_FACE_TOP, _SPN_FACE_BOT, _SPN_RECESS)
    _center(surf, glyph_key, cx, cy, R, _SPN_GLY, _SPN_GLY_SH)


# ═══════════════════════════════════════════════════════════════════════════
# 3) CONFETTI — party-popper ring.
#    A rounded bubble-gum-pink rim ringed with scattered confetti dots, squiggle
#    streamers and a couple of pop-burst star-flecks. A birthday-party booby
#    prize. Palette: candy multicolour (cyan / magenta / yellow / lime) on a
#    warm bubblegum rim.
# ═══════════════════════════════════════════════════════════════════════════
_CNF_RIM_HI  = (255, 196, 224)    # bubblegum crest
_CNF_RIM_MID = (236, 130, 184)    # pink body
_CNF_RIM_LO  = (170,  64, 124)    # shadow
_CNF_RIM_EDGE = (110,  34,  84)
_CNF_SPEC    = (255, 232, 244)
_CNF_FACE_TOP = ( 96,  60, 116)   # plum well — lets the candy confetti pop
_CNF_FACE_BOT = ( 52,  30,  72)
_CNF_RECESS   = ( 34,  18,  50)
_CNF_GLY      = (255, 238, 250)   # bright icing glyph
_CNF_GLY_SH   = ( 60,  28,  72)
_CNF_CONFETTI = [(86, 214, 236), (255, 224, 92), (140, 226, 120),
                 (255, 150, 96), (180, 150, 255)]


def ring_confetti(surf, cx, cy, R, glyph_key):
    # bubblegum rim
    _smooth_band(surf, cx, cy, R, int(R * 0.74),
                 _CNF_RIM_HI, _CNF_RIM_LO, spec=_CNF_SPEC, spec_span=0.6)
    pygame.draw.circle(surf, _CNF_RIM_MID, (cx, cy), R, max(2, R // 24))
    pygame.draw.circle(surf, _CNF_RIM_EDGE, (cx, cy), R, max(1, R // 38))

    # Confetti scatter HUGGING the rim — deterministic from a fixed angle table
    # so the badge is stable (no RNG between renders). Count cut ~40% (22→13) and
    # pulled tight to the rim band so it reads as a crisp festive trim, not a
    # noisy halo that crowds the centre emblem at 44px.
    n = 13
    for i in range(n):
        a = i / n * math.tau + (i % 3) * 0.18
        rad = R * (1.00 + 0.05 * ((i * 7) % 3) / 2)     # tight to the rim
        px = cx + int(math.cos(a) * rad)
        py = cy + int(math.sin(a) * rad)
        col = _CNF_CONFETTI[i % len(_CNF_CONFETTI)]
        kind = i % 3
        sz = max(3, R // 10)
        if kind == 0:                                   # round dot
            pygame.draw.circle(surf, col, (px, py), sz)
            pygame.draw.circle(surf, _CNF_RIM_EDGE, (px, py), sz, max(1, R // 44))
        elif kind == 1:                                 # tilted rectangle fleck
            rot = (i * 37) % 180
            rs = pygame.Surface((sz * 2, sz * 3), pygame.SRCALPHA)
            rs.fill(col)
            rs = pygame.transform.rotate(rs, rot)
            surf.blit(rs, rs.get_rect(center=(px, py)))
        else:                                           # streamer arc squiggle
            rr = pygame.Rect(px - sz, py - sz, sz * 2, sz * 2)
            pygame.draw.arc(surf, col, rr, 0.2, math.pi * 1.3, max(2, R // 26))

    # a few four-point pop-flecks for the party-popper sparkle, also kept tight
    for i in range(4):
        a = i / 4 * math.tau + 0.6
        rad = R * 1.08
        px = cx + int(math.cos(a) * rad)
        py = cy + int(math.sin(a) * rad)
        col = _CNF_CONFETTI[(i + 2) % len(_CNF_CONFETTI)]
        s = max(3, R // 11)
        pygame.draw.line(surf, col, (px - s, py), (px + s, py), max(2, R // 30))
        pygame.draw.line(surf, col, (px, py - s), (px, py + s), max(2, R // 30))

    fr = int(R * 0.70)
    ai._draw_step(surf, cx, cy, fr + max(2, R // 16), _CNF_RIM_HI, _CNF_RIM_LO)
    _radial_face(surf, cx, cy, fr, _CNF_FACE_TOP, _CNF_FACE_BOT, _CNF_RECESS)
    _center(surf, glyph_key, cx, cy, R, _CNF_GLY, _CNF_GLY_SH)


# ═══════════════════════════════════════════════════════════════════════════
# 4) STARBURST — comic sticker-burst seal ("PRIZE!" sticker).
#    A spiky zig-zag star-seal rim with a bold cartoon keyline, like a stuck-on
#    reward sticker. Angular shape language — the opposite of the round others.
#    Palette: tangerine + cream pop-art with a thick ink outline.
# ═══════════════════════════════════════════════════════════════════════════
# Pushed off amber toward a punchy CORAL/orange (more red, less yellow) so the
# 44px chip reads as a comic sticker, never a gold sunburst Fame medal.
_STR_BURST_HI = (255, 142,  96)   # coral crest
_STR_BURST_LO = (224,  78,  52)   # red-orange shadow
_STR_INK      = ( 92,  28,  20)   # bold warm-brown cartoon keyline
_STR_FACE_TOP = (255, 240, 224)   # warm cream sticker well
_STR_FACE_BOT = (250, 206, 184)
_STR_RECESS   = (214, 140, 116)
_STR_RING     = (255, 228, 210)   # inner cream ring of the seal
_STR_GLY      = (226,  96,  62)   # printed-coral glyph on cream
_STR_GLY_SH   = (255, 246, 236)


def ring_starburst(surf, cx, cy, R, glyph_key):
    # The spiky star-seal: a 16-point burst (alternating long/short radii) with a
    # bold ink outline, the classic comic "BURST" sticker silhouette.
    pts_n = 32
    outer = int(R * 1.18)
    inner = int(R * 0.92)
    burst = []
    for i in range(pts_n):
        a = i / pts_n * math.tau - math.pi / 2
        rad = outer if i % 2 == 0 else inner
        burst.append((cx + math.cos(a) * rad, cy + math.sin(a) * rad))
    bpts = [(int(x), int(y)) for x, y in burst]
    # ink drop-shadow offset so the sticker reads as stuck-on with lift
    sh = [(x + max(2, R // 16), y + max(2, R // 16)) for x, y in bpts]
    pygame.draw.polygon(surf, (40, 22, 6), sh)
    # the tangerine burst body, then a soft lower-right shade so the seal reads
    # as a lit object under the family's upper-left light (not a flat print).
    pygame.draw.polygon(surf, _STR_BURST_HI, bpts)
    shade = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    lo_dir = _LIGHT + math.pi              # opposite the light = the shadow side
    shpts = []
    for i in range(pts_n):
        a = i / pts_n * math.tau - math.pi / 2
        rad = outer if i % 2 == 0 else inner
        d = (math.cos(a - lo_dir) + 1) * 0.5          # 1 on the shadow side
        alpha = int(170 * d ** 1.6)
        shpts.append(((cx + math.cos(a) * rad, cy + math.sin(a) * rad), alpha))
    # paint each spike-wedge from centre with its own shadow alpha
    for i in range(pts_n):
        (x0, y0), al0 = shpts[i]
        (x1, y1), al1 = shpts[(i + 1) % pts_n]
        al = (al0 + al1) // 2
        if al <= 4:
            continue
        pygame.draw.polygon(shade, (*_STR_BURST_LO, al),
                            [(cx, cy), (int(x0), int(y0)), (int(x1), int(y1))])
    surf.blit(shade, (0, 0))
    pygame.draw.polygon(surf, _STR_INK, bpts, max(3, R // 16))

    # inner cream ring band of the seal (a flat printed ring inside the spikes)
    pygame.draw.circle(surf, _STR_RING, (cx, cy), int(R * 0.84))
    pygame.draw.circle(surf, _STR_INK, (cx, cy), int(R * 0.84), max(2, R // 22))
    # tiny printed dots running the cream ring — sticker "ticket" perforation
    for i in range(20):
        a = i / 20 * math.tau
        dx = cx + int(math.cos(a) * R * 0.78)
        dy = cy + int(math.sin(a) * R * 0.78)
        pygame.draw.circle(surf, _STR_BURST_LO, (dx, dy), max(1, R // 30))

    fr = int(R * 0.66)
    ai._draw_step(surf, cx, cy, fr + max(2, R // 16), _STR_BURST_HI, _STR_BURST_LO)
    _radial_face(surf, cx, cy, fr, _STR_FACE_TOP, _STR_FACE_BOT, _STR_RECESS)
    pygame.draw.circle(surf, _STR_INK, (cx, cy), fr, max(2, R // 24))
    _center(surf, glyph_key, cx, cy, R, _STR_GLY, _STR_GLY_SH)


# ═══════════════════════════════════════════════════════════════════════════
# 5) DROOPY — melted gag-medal.
#    A glossy rubber-toy medal that has half-melted: the rim sags and drips into
#    soft wax blobs along the lower edge. Round-but-runny shape language; a
#    high-gloss bubble highlight. Palette: minty teal + soft lilac, candy gloss.
# ═══════════════════════════════════════════════════════════════════════════
_DRP_RIM_HI  = (170, 240, 224)    # mint crest
_DRP_RIM_MID = ( 86, 196, 184)    # teal body
_DRP_RIM_LO  = ( 36, 130, 132)    # teal shadow
_DRP_RIM_EDGE = ( 18,  78,  84)
_DRP_SPEC    = (236, 255, 250)
_DRP_FACE_TOP = (212, 198, 244)   # soft lilac well
_DRP_FACE_BOT = (150, 128, 204)
_DRP_RECESS   = (104,  84, 160)
_DRP_GLY      = ( 64,  44, 120)   # grape glyph on lilac
_DRP_GLY_SH   = (224, 214, 248)


def _melt_blob(surf, x, top, length, w, hi, mid, lo):
    # A sagging wax drip: a wide neck (still part of the rim) that necks IN then
    # swells into a fat rounded bead at the bottom — the classic dripping-candle
    # teardrop, lit on the upper-left so it reads as glossy rubber.
    pts_l, pts_r = [], []
    for i in range(9):
        f = i / 8
        yy = top + int(length * f)
        # wide at the rim, pinch in the middle, bulge at the bead
        ww = int(w * (1.15 - 0.85 * f + 1.05 * (f ** 2)))
        pts_l.append((x - ww, yy))
        pts_r.append((x + ww, yy))
    poly = pts_l + pts_r[::-1]
    pygame.draw.polygon(surf, mid, [(int(a), int(b)) for a, b in poly])
    by = top + length
    br = int(w * 1.35)
    pygame.draw.circle(surf, mid, (x, by), br)
    pygame.draw.circle(surf, lo, (x, by), br, max(1, br // 4))
    # gloss bubble on the bead — the wet-rubber sheen
    pygame.draw.circle(surf, hi, (x - br // 3, by - br // 3), max(2, br // 2))


def ring_droopy(surf, cx, cy, R, glyph_key):
    # melt drips hang off the lower rim first (behind the body). Three fat,
    # well-separated wax beads of differing length so the rim looks genuinely
    # half-melted — the whole joke lives here, so they hang well below the disc.
    for ddx, dtop, dlen, dw in ((-0.50, 0.70, 0.84, 0.24),
                                (0.02, 0.86, 1.06, 0.29),
                                (0.52, 0.66, 0.70, 0.21)):
        _melt_blob(surf, cx + int(R * ddx), cy + int(R * dtop),
                   int(R * dlen), int(R * dw),
                   _DRP_RIM_HI, _DRP_RIM_MID, _DRP_RIM_LO)

    # The rim is a near-circle that SAGS: bottom pushed down + slightly fatter,
    # drawn as a smooth polygon so the silhouette droops rather than reads as a
    # clean coin. Lit per-vertex by the upper-left light.
    pts_n = 48
    poly = []
    for i in range(pts_n):
        a = i / pts_n * math.tau - math.pi / 2
        sag = 1.0 + 0.26 * max(0.0, math.sin(a)) ** 1.3   # bottom bulges down
        squash = 1.0 + 0.09 * max(0.0, math.sin(a))
        poly.append((a, R * sag * squash))
    # fill from outer polygon inward as shaded bands
    for layer, scale in enumerate((1.0, 0.93, 0.86)):
        ring = []
        for a, rad in poly:
            ring.append((cx + math.cos(a) * rad * scale,
                         cy + math.sin(a) * rad * scale))
        d_mix = (0.0, 0.28, 0.6)[layer]
        pygame.draw.polygon(surf, lerp_color(_DRP_RIM_HI, _DRP_RIM_LO, d_mix),
                            [(int(x), int(y)) for x, y in ring])
    # directional sheen + edge keyline along the droopy outline
    out_ring = [(cx + math.cos(a) * rad, cy + math.sin(a) * rad)
                for a, rad in poly]
    for i in range(pts_n):
        a, rad = poly[i]
        d = (math.cos(a - _LIGHT) + 1) * 0.5
        x0, y0 = out_ring[i]
        x1, y1 = out_ring[(i + 1) % pts_n]
        pygame.draw.line(surf, lerp_color(_DRP_RIM_LO, _DRP_RIM_HI, d ** 1.3),
                         (int(x0), int(y0)), (int(x1), int(y1)), max(2, R // 12))
    pygame.draw.polygon(surf, _DRP_RIM_EDGE,
                        [(int(x), int(y)) for x, y in out_ring], max(2, R // 30))

    # big glossy highlight bubble on the upper-left — the rubber-toy sheen
    blit_glow(surf, cx - int(R * 0.34), cy - int(R * 0.34), int(R * 0.30),
              (210, 255, 248), 120)

    fr = int(R * 0.66)
    ai._draw_step(surf, cx, cy, fr + max(2, R // 16), _DRP_RIM_HI, _DRP_RIM_LO)
    _radial_face(surf, cx, cy, fr, _DRP_FACE_TOP, _DRP_FACE_BOT, _DRP_RECESS)
    _center(surf, glyph_key, cx, cy, R, _DRP_GLY, _DRP_GLY_SH)


CONCEPTS = [
    ("rosette", ring_rosette),
    ("spoon", ring_spoon),
    ("confetti", ring_confetti),
    ("starburst", ring_starburst),
    ("droopy", ring_droopy),
]
