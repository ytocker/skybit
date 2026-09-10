"""Five FRESH paired outer-RING concepts where the ring dramatizes a
Fame -> Shame TRADE-OFF on the achievement medallion.

Each concept is a MATCHED PAIR sharing ONE prestige material + form:

  * ``fame_<name>``  — the object at its most premium: struck, lit, glinting,
    triumphant.
  * ``shame_<name>`` — the SAME object GONE BAD: the identical material and
    construction visibly ruined, so it always reads as "this exact honour,
    ruined", never an unrelated badge.

The five are distinct in MATERIAL, FORM and FAILURE mode (no laurel wreath, no
twig crown — those were retired):

  1) SEAL     wax + cord   minted royal wax seal  -> melted, broken, frayed
  2) GEM      cut crystal  brilliant-cut stones   -> clouded, cracked, sockets
  3) FLAME    fire/light   eternal-flame corona   -> extinguished to cold smoke
  4) COIN     struck metal reeded guilloché proof -> corroded verdigris + clip
  5) ENAMEL   vitreous     cloisonné colour ring  -> chipped, crazed, ashen

The CENTER emblem is never redesigned — every composer stamps the live engraved
glyph through ``ai._stamp_glyph`` (``pillar_100`` in Fame, ``goose_egg`` in
Shame), so only the ring/frame carries the trade-off. NO diagonal crack cue on
any Shame ring.

WRITE-ONLY scratch under ``tools/`` — never bundled; imports ``game`` read-only.
"""
from __future__ import annotations

import math
import pygame

import game.achievement_icons as ai
from game.draw import lerp_color, blit_glow

_LIGHT = ai._LIGHT  # share the family's one upper-left light source


# ── shared low-level helpers ────────────────────────────────────────────────

def _center(surf, glyph_key, cx, cy, R, gly, gly_sh, sheen=None):
    ai._stamp_glyph(surf, glyph_key, cx, cy, int(R * 0.56), gly, gly_sh, sheen)


def _metal_band(surf, cx, cy, R, inner, hi, lo, spec=None,
                spec_span=0.55, light=_LIGHT, edge=None):
    """The shared struck-metal rim bevel from ``R`` inward to ``inner`` under the
    one upper-left light. Each concept feeds its own palette so the MATERIAL
    (bright gold vs. dead pewter) differs while the strike geometry matches the
    live family."""
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
    if edge is not None:
        pygame.draw.circle(surf, edge, (cx, cy), R, max(1, R // 36))


def _oxide_mottle(surf, cx, cy, r0, r1, cols, seed, n=26):
    """Deterministic corrosion mottle — irregular oxide blots so a degraded frame
    reads as corroded material, not a flat recolour. Fixed pseudo-random from
    ``seed`` so a badge is stable across renders."""
    s = seed
    for i in range(n):
        s = (s * 1103515245 + 12345) & 0x7fffffff
        a = (s / 0x7fffffff) * math.tau
        s = (s * 1103515245 + 12345) & 0x7fffffff
        rad = r0 + (r1 - r0) * (s / 0x7fffffff)
        px = cx + int(math.cos(a) * rad)
        py = cy + int(math.sin(a) * rad)
        col = cols[i % len(cols)]
        sz = max(2, int((r1 - r0) * (0.18 + 0.22 * ((i * 7) % 3) / 2)))
        pygame.draw.circle(surf, col, (px, py), sz)


def _wedge(surf, cx, cy, a0, a1, rin, rout, col, steps=8):
    pts = []
    for k in range(steps + 1):
        a = a0 + (a1 - a0) * k / steps
        pts.append((cx + math.cos(a) * rout, cy + math.sin(a) * rout))
    for k in range(steps + 1):
        a = a1 - (a1 - a0) * k / steps
        pts.append((cx + math.cos(a) * rin, cy + math.sin(a) * rin))
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in pts])


# ═══════════════════════════════════════════════════════════════════════════
# 1) SEAL — a minted royal WAX SEAL hung on gilt cords.
#    Fame: a deep-vermilion wax seal with a scalloped rosette border and an
#    embossed bead ring, glossy with a waxy sheen, suspended on two twisted gold
#    cords ending in tassels. Shame: the SAME seal MELTED & BROKEN — the wax
#    dulled to dried maroon, lobes sagging into drips off the lower rim, a whole
#    arc of the border cracked away into a gap, the cords snapped and frayed.
# ═══════════════════════════════════════════════════════════════════════════
_SE_RIM_HI = (255, 232, 160)
_SE_RIM_MID = (232, 184, 72)
_SE_RIM_LO = (150, 102, 20)
_SE_EDGE = (70, 44, 8)
_SE_SPEC = (255, 250, 222)
_SE_CORD_HI = (250, 214, 120)
_SE_CORD_LO = (150, 104, 30)
_SE_WAX_HI = (232, 104, 88)       # lit crimson wax
_SE_WAX_MID = (196, 56, 46)       # wax body
_SE_WAX_LO = (120, 26, 22)        # wax shadow / deep press
_SE_WAX_SHEEN = (255, 196, 178)   # waxy specular gloss
_SE_FACE_TOP = (44, 32, 92)
_SE_FACE_BOT = (16, 10, 44)
_SE_RECESS = (10, 6, 28)
_SE_GLY = (255, 236, 184)
_SE_GLY_SH = (32, 18, 44)

_SD_RIM_HI = (150, 148, 152)
_SD_RIM_MID = (96, 94, 98)
_SD_RIM_LO = (52, 50, 54)
_SD_EDGE = (24, 22, 24)
_SD_CORD_HI = (140, 138, 144)
_SD_CORD_LO = (78, 76, 82)
_SD_WAX_HI = (128, 82, 76)        # dried, dulled maroon wax
_SD_WAX_MID = (96, 54, 50)
_SD_WAX_LO = (58, 30, 28)
_SD_FACE_TOP = (48, 46, 52)
_SD_FACE_BOT = (24, 22, 28)
_SD_RECESS = (14, 12, 18)
_SD_GLY = (172, 168, 158)
_SD_GLY_SH = (16, 14, 16)


def _seal_cord(surf, cx, cy, R, sgn, hi, lo, drop=0.22, frayed=False):
    """A twisted gilt suspension cord hanging off the seal's lower flank down to a
    tassel — the cue that this medal is a hung charter seal. ``frayed`` snaps it
    short with loose threads instead of a tassel."""
    # anchored on the lower flank and kept SHORT so the tassel stays fully inside
    # the badge square (core geometry: total reach must clear ~1.28*R)
    aa = math.radians(126 if sgn < 0 else 54)
    x0 = cx + math.cos(aa) * R * 1.0
    y0 = cy + math.sin(aa) * R * 1.0
    length = R * (drop if not frayed else drop * 0.55)
    steps = 12
    prev = (x0, y0)
    for k in range(1, steps + 1):
        f = k / steps
        yy = y0 + length * f
        xx = x0 + sgn * math.sin(f * math.pi * 2.2) * R * 0.045 + sgn * f * R * 0.10
        c = hi if (int(f * 10) % 2 == 0) else lo   # twisted two-tone strand
        pygame.draw.line(surf, c, (int(prev[0]), int(prev[1])),
                         (int(xx), int(yy)), max(3, R // 16))
        prev = (xx, yy)
    ex, ey = prev
    if frayed:
        for k in range(4):
            fx = ex + sgn * R * (0.02 + 0.04 * k)
            pygame.draw.line(surf, lo, (int(ex), int(ey)),
                             (int(fx), int(ey + R * (0.06 + 0.03 * k))),
                             max(2, R // 26))
    else:
        # a tidy tassel: a rounded cap + a short fan of gold fringe
        pygame.draw.circle(surf, hi, (int(ex), int(ey)), max(4, R // 12))
        pygame.draw.circle(surf, lo, (int(ex), int(ey)), max(4, R // 12), max(1, R // 44))
        for k in range(5):
            fx = ex + (k - 2) * R * 0.04
            pygame.draw.line(surf, lo, (int(ex), int(ey + R * 0.05)),
                             (int(fx), int(ey + R * 0.15)), max(2, R // 28))


def _wax_border(surf, cx, cy, R, hi, mid, lo, sheen=None, base_r=1.02,
                lobe_r=0.15, n=15, melt=False, broken_gap=None, seed=7):
    """A hand-pressed WAX rosette pooled around the medal: irregular convex
    droplets (varied size + press radius, each with a glossy specular highlight)
    on a continuous wax annulus — molten wax squeezed under a seal, NOT uniform
    beads. ``melt`` sags the lower droplets into hanging drips; ``broken_gap`` is
    an (a0, a1) arc where the wax has cracked clean away."""
    br = R * base_r
    # the continuous wax pool the droplets sit on (slightly inboard so the lobes
    # bulge past its edge, giving the irregular hand-pressed rim)
    pygame.draw.circle(surf, mid, (cx, cy), int(br * 0.94))
    s = seed
    for i in range(n):
        a = i / n * math.tau - math.pi / 2
        if broken_gap and broken_gap[0] <= (a % math.tau) <= broken_gap[1]:
            continue
        s = (s * 1103515245 + 12345) & 0x7fffffff
        jr = 0.78 + 0.55 * (s / 0x7fffffff)        # irregular droplet size
        s = (s * 1103515245 + 12345) & 0x7fffffff
        jb = 0.95 + 0.12 * (s / 0x7fffffff)        # irregular press radius
        lr = max(2, int(R * lobe_r * jr))
        lx = cx + math.cos(a) * br * jb
        ly = cy + math.sin(a) * br * jb
        d = (math.cos(a - _LIGHT) + 1) * 0.5
        col = lerp_color(lo, hi, d ** 1.05)
        if melt and math.sin(a) > 0.15:            # lower half sags into a drip
            # kept short so the longest drip still clears the badge square (~1.28R)
            sag = R * (0.08 + 0.17 * math.sin(a))
            pygame.draw.line(surf, mid, (int(lx), int(ly)),
                             (int(lx), int(ly + sag)), max(3, lr))
            pygame.draw.circle(surf, col, (int(lx), int(ly + sag * 0.35)), lr)
            pygame.draw.circle(surf, lerp_color(lo, mid, 0.5),
                               (int(lx), int(ly + sag)), int(lr * 0.82))
        else:
            pygame.draw.circle(surf, lo, (int(lx), int(ly)), lr)         # shade base
            pygame.draw.circle(surf, col, (int(lx - lr * 0.08), int(ly - lr * 0.08)),
                               int(lr * 0.92))
            if sheen is not None:                                        # glossy dab
                pygame.draw.circle(surf, sheen,
                                   (int(lx - lr * 0.34), int(ly - lr * 0.34)),
                                   max(1, int(lr * 0.34)))


def fame_seal(surf, cx, cy, R, glyph_key):
    for sgn in (-1, 1):
        _seal_cord(surf, cx, cy, R, sgn, _SE_CORD_HI, _SE_CORD_LO)
    # hand-pressed glossy wax pool, then punch its centre with the gold rim band
    _wax_border(surf, cx, cy, R, _SE_WAX_HI, _SE_WAX_MID, _SE_WAX_LO,
                sheen=_SE_WAX_SHEEN, n=15)
    # a broad waxy upper-left gloss sweep so the whole pool reads wet/convex
    pygame.draw.arc(surf, _SE_WAX_SHEEN,
                    (cx - int(R * 1.0), cy - int(R * 1.0),
                     int(R * 2.0), int(R * 2.0)),
                    _LIGHT - 0.6, _LIGHT + 0.6, max(2, R // 14))
    _metal_band(surf, cx, cy, R, int(R * 0.74), _SE_RIM_HI, _SE_RIM_LO,
                spec=_SE_SPEC, edge=_SE_EDGE)
    pygame.draw.circle(surf, _SE_RIM_MID, (cx, cy), R, max(2, R // 24))
    fr = int(R * 0.70)
    ai._draw_step(surf, cx, cy, fr + max(2, R // 16), _SE_RIM_HI, _SE_RIM_LO)
    ai._draw_face(surf, cx, cy, fr, _SE_FACE_TOP, _SE_FACE_BOT, _SE_RECESS)
    _center(surf, glyph_key, cx, cy, R, _SE_GLY, _SE_GLY_SH, ai._GLYPH_SHEEN)


def shame_seal(surf, cx, cy, R, glyph_key):
    # one cord snapped short and frayed, one hanging slack
    _seal_cord(surf, cx, cy, R, -1, _SD_CORD_HI, _SD_CORD_LO, frayed=True)
    _seal_cord(surf, cx, cy, R, 1, _SD_CORD_HI, _SD_CORD_LO, drop=0.34)
    # melted, broken wax: a big cracked-away gap on the upper-right border
    _wax_border(surf, cx, cy, R, _SD_WAX_HI, _SD_WAX_MID, _SD_WAX_LO, n=15,
                melt=True, broken_gap=(math.radians(300), math.radians(352)))
    # crazing cracks webbing the surviving wax
    for a0, a1 in ((math.radians(200), math.radians(250)),
                   (math.radians(120), math.radians(150))):
        p0 = (cx + math.cos(a0) * R * 0.92, cy + math.sin(a0) * R * 0.92)
        p1 = (cx + math.cos(a1) * R * 1.02, cy + math.sin(a1) * R * 1.02)
        pygame.draw.line(surf, _SD_WAX_LO, (int(p0[0]), int(p0[1])),
                         (int(p1[0]), int(p1[1])), max(1, R // 40))
    _metal_band(surf, cx, cy, R, int(R * 0.74), _SD_RIM_HI, _SD_RIM_LO,
                spec=None, edge=_SD_EDGE)
    _oxide_mottle(surf, cx, cy, int(R * 0.80), int(R * 1.00),
                  (_SD_WAX_LO, _SD_RIM_LO), seed=17, n=18)
    pygame.draw.circle(surf, _SD_RIM_MID, (cx, cy), R, max(2, R // 24))
    fr = int(R * 0.70)
    ai._draw_step(surf, cx, cy, fr + max(2, R // 16), _SD_RIM_HI, _SD_RIM_LO)
    ai._draw_face(surf, cx, cy, fr, _SD_FACE_TOP, _SD_FACE_BOT, _SD_RECESS)
    _center(surf, glyph_key, cx, cy, R, _SD_GLY, _SD_GLY_SH)


# ═══════════════════════════════════════════════════════════════════════════
# 2) GEM — a bezel of brilliant-cut stones in gold prong settings.
#    Fame: a ring of ice-bright round brilliants, each faceted with a table +
#    kite facets and an upper-left glint, gripped by crisp gold claws. Shame:
#    the SAME stones CLOUDED to milky grey and CRACKED, glints dead, two stones
#    shattered out of their bent claws leaving empty dark sockets.
# ═══════════════════════════════════════════════════════════════════════════
_GM_RIM_HI = (255, 230, 158)
_GM_RIM_MID = (232, 184, 74)
_GM_RIM_LO = (150, 102, 22)
_GM_EDGE = (70, 44, 8)
_GM_SPEC = (255, 250, 222)
_GM_PRONG = (255, 236, 176)
_GM_TABLE = (224, 240, 255)       # ice-white brilliant table
_GM_MID = (150, 196, 244)
_GM_DK = (78, 128, 190)
_GM_GLINT = (255, 255, 255)
_GM_FACE_TOP = (40, 32, 90)
_GM_FACE_BOT = (16, 10, 44)
_GM_RECESS = (10, 6, 28)
_GM_GLY = (255, 236, 184)
_GM_GLY_SH = (32, 18, 44)

_GD_RIM_HI = (148, 146, 150)
_GD_RIM_MID = (96, 94, 98)
_GD_RIM_LO = (52, 50, 54)
_GD_EDGE = (24, 22, 24)
_GD_PRONG = (120, 118, 122)
_GD_TABLE = (156, 158, 164)       # clouded milky stone
_GD_MID = (112, 114, 122)
_GD_DK = (72, 74, 82)
_GD_SOCKET = (18, 18, 24)         # empty setting rim
_GD_FACE_TOP = (48, 46, 52)
_GD_FACE_BOT = (24, 22, 28)
_GD_RECESS = (14, 12, 18)
_GD_GLY = (170, 164, 152)
_GD_GLY_SH = (16, 14, 16)


def _brilliant(surf, cx, cy, gr, table, mid, dk, glint=None, cracked=False):
    """One round brilliant seen top-down: an octagon girdle, kite facets around a
    central table, a corner glint. ``cracked`` webs the facets with fractures."""
    verts = [(cx + math.cos(i / 8 * math.tau - math.pi / 8) * gr,
              cy + math.sin(i / 8 * math.tau - math.pi / 8) * gr) for i in range(8)]
    pygame.draw.polygon(surf, mid, [(int(x), int(y)) for x, y in verts])
    tv = [(cx + (x - cx) * 0.46, cy + (y - cy) * 0.46) for x, y in verts]
    # kite facets: alternate light/dark girdle-to-table wedges for sparkle
    for i in range(8):
        j = (i + 1) % 8
        shade = table if i % 2 == 0 else dk
        pygame.draw.polygon(surf, shade, [
            (int(verts[i][0]), int(verts[i][1])),
            (int(verts[j][0]), int(verts[j][1])),
            (int(tv[j][0]), int(tv[j][1])),
            (int(tv[i][0]), int(tv[i][1]))])
    pygame.draw.polygon(surf, table, [(int(x), int(y)) for x, y in tv])
    pygame.draw.polygon(surf, dk, [(int(x), int(y)) for x, y in tv], max(1, gr // 10))
    if cracked:
        for i in (1, 4, 6):
            pygame.draw.line(surf, dk, (cx, cy),
                             (int(verts[i][0]), int(verts[i][1])), max(1, gr // 8))
            pygame.draw.line(surf, table,
                             (int(tv[i][0]), int(tv[i][1])),
                             (int(verts[(i + 3) % 8][0]), int(verts[(i + 3) % 8][1])),
                             max(1, gr // 12))
    if glint is not None:
        pygame.draw.circle(surf, glint,
                           (int(cx - gr * 0.30), int(cy - gr * 0.30)), max(1, gr // 4))


def _prongs(surf, cx, cy, gr, col, edge, bent=False):
    for k in range(4):
        a = k * math.pi / 2 - math.pi / 4 + (0.25 if bent else 0.0)
        px = cx + math.cos(a) * gr * (1.18 if not bent else 1.34)
        py = cy + math.sin(a) * gr * (1.18 if not bent else 1.34)
        h = gr * 0.32
        n = (-math.sin(a), math.cos(a))
        pygame.draw.polygon(surf, col, [
            (int(px), int(py)),
            (int(cx + math.cos(a) * gr * 0.9 + n[0] * h), int(cy + math.sin(a) * gr * 0.9 + n[1] * h)),
            (int(cx + math.cos(a) * gr * 0.9 - n[0] * h), int(cy + math.sin(a) * gr * 0.9 - n[1] * h))])


def _gem_ring(surf, cx, cy, R, palette, n=10, wrecked=False):
    table, mid, dk, prong, edge = palette
    ring_r = R * 1.04
    gr = int(R * 0.15)
    missing = {2, 7} if wrecked else set()
    cracked_set = {0, 4, 8} if wrecked else set()
    for i in range(n):
        a = i / n * math.tau - math.pi / 2
        gx = cx + math.cos(a) * ring_r
        gy = cy + math.sin(a) * ring_r
        if i in missing:
            # a DEEP empty claw setting: a dark cupped socket (darker toward the
            # centre) with a lit lower lip, ringed by a few bent prong-claws left
            # standing — so the loss reads as "the gem fell out", not a grey bump
            pygame.draw.circle(surf, _GD_SOCKET, (int(gx), int(gy)), int(gr * 0.98))
            pygame.draw.circle(surf, (8, 8, 12), (int(gx), int(gy)), int(gr * 0.60))
            pygame.draw.arc(surf, prong,
                            (int(gx - gr * 0.8), int(gy - gr * 0.8),
                             int(gr * 1.6), int(gr * 1.6)),
                            math.radians(200), math.radians(340), max(1, R // 46))
            for k in range(4):                      # empty claws still gripping air
                ca = k * math.pi / 2 - math.pi / 4
                cx2 = gx + math.cos(ca) * gr * 1.02
                cy2 = gy + math.sin(ca) * gr * 1.02
                nrm = (-math.sin(ca), math.cos(ca))
                hclaw = gr * 0.34
                pygame.draw.polygon(surf, prong, [
                    (int(cx2 + math.cos(ca) * gr * 0.28), int(cy2 + math.sin(ca) * gr * 0.28)),
                    (int(gx + math.cos(ca) * gr * 0.5 + nrm[0] * hclaw),
                     int(gy + math.sin(ca) * gr * 0.5 + nrm[1] * hclaw)),
                    (int(gx + math.cos(ca) * gr * 0.5 - nrm[0] * hclaw),
                     int(gy + math.sin(ca) * gr * 0.5 - nrm[1] * hclaw))])
            continue
        _prongs(surf, int(gx), int(gy), gr, prong, edge, bent=wrecked)
        _brilliant(surf, int(gx), int(gy), gr, table, mid, dk,
                   glint=None if wrecked else _GM_GLINT, cracked=i in cracked_set)


def fame_gem(surf, cx, cy, R, glyph_key):
    _metal_band(surf, cx, cy, R, int(R * 0.74), _GM_RIM_HI, _GM_RIM_LO,
                spec=_GM_SPEC, edge=_GM_EDGE)
    _gem_ring(surf, cx, cy, R, (_GM_TABLE, _GM_MID, _GM_DK, _GM_PRONG, _GM_EDGE))
    pygame.draw.circle(surf, _GM_RIM_MID, (cx, cy), R, max(2, R // 24))
    fr = int(R * 0.70)
    ai._draw_step(surf, cx, cy, fr + max(2, R // 16), _GM_RIM_HI, _GM_RIM_LO)
    ai._draw_face(surf, cx, cy, fr, _GM_FACE_TOP, _GM_FACE_BOT, _GM_RECESS)
    _center(surf, glyph_key, cx, cy, R, _GM_GLY, _GM_GLY_SH, ai._GLYPH_SHEEN)


def shame_gem(surf, cx, cy, R, glyph_key):
    _metal_band(surf, cx, cy, R, int(R * 0.74), _GD_RIM_HI, _GD_RIM_LO,
                spec=None, edge=_GD_EDGE)
    _oxide_mottle(surf, cx, cy, int(R * 0.78), int(R * 0.98),
                  (_GD_RIM_LO, _GD_EDGE), seed=29)
    _gem_ring(surf, cx, cy, R, (_GD_TABLE, _GD_MID, _GD_DK, _GD_PRONG, _GD_EDGE),
              wrecked=True)
    pygame.draw.circle(surf, _GD_RIM_MID, (cx, cy), R, max(2, R // 24))
    fr = int(R * 0.70)
    ai._draw_step(surf, cx, cy, fr + max(2, R // 16), _GD_RIM_HI, _GD_RIM_LO)
    ai._draw_face(surf, cx, cy, fr, _GD_FACE_TOP, _GD_FACE_BOT, _GD_RECESS)
    _center(surf, glyph_key, cx, cy, R, _GD_GLY, _GD_GLY_SH)


# ═══════════════════════════════════════════════════════════════════════════
# 3) FLAME — an eternal-flame corona licking around the rim.
#    Fame: a crown of layered gold flame tongues (amber -> yellow -> white core)
#    curling clockwise over a warm glow. Shame: the SAME corona EXTINGUISHED —
#    every flame reduced to a charred black wick stub trailing a cold grey smoke
#    curl, one last dying ember, the glow gone.
# ═══════════════════════════════════════════════════════════════════════════
_FL_RIM_HI = (255, 226, 150)
_FL_RIM_MID = (236, 184, 72)
_FL_RIM_LO = (150, 102, 22)
_FL_EDGE = (78, 48, 10)
_FL_SPEC = (255, 250, 222)
_FL_AMBER = (250, 138, 40)
_FL_ORANGE = (255, 186, 66)
_FL_YEL = (255, 228, 130)
_FL_WHITE = (255, 250, 224)
_FL_FACE_TOP = (44, 32, 92)
_FL_FACE_BOT = (16, 10, 44)
_FL_RECESS = (10, 6, 28)
_FL_GLY = (255, 236, 184)
_FL_GLY_SH = (32, 18, 44)

_FD_RIM_HI = (146, 144, 148)
_FD_RIM_MID = (94, 92, 96)
_FD_RIM_LO = (50, 48, 52)
_FD_EDGE = (22, 20, 22)
_FD_SOOT = (28, 26, 28)           # charred wick stub
_FD_SMOKE = (150, 150, 158)       # cold smoke
_FD_EMBER = (150, 74, 34)         # one dying ember
_FD_FACE_TOP = (48, 46, 52)
_FD_FACE_BOT = (24, 22, 28)
_FD_RECESS = (14, 12, 18)
_FD_GLY = (170, 164, 152)
_FD_GLY_SH = (16, 14, 16)


def _flame_shape(cx, cy, a, base_r, L, lean, hw, n=11):
    """A smooth flame-tongue outline: wide at the rooted base, bulging low, then
    tapering to a sharp tip that curls tangentially (a real fire lick, not a
    spike). Returns a closed point list."""
    left, right = [], []
    for k in range(n + 1):
        t = k / n
        rr = base_r + L * t
        ca = a + lean * (t ** 1.7)                  # the tip flicks to one side
        w = hw * (1 - t) * (1.0 + 0.55 * math.sin(math.pi * t))
        left.append((cx + math.cos(ca - w) * rr, cy + math.sin(ca - w) * rr))
        right.append((cx + math.cos(ca + w) * rr, cy + math.sin(ca + w) * rr))
    return left + right[::-1]


def _flame_lick(surf, cx, cy, a, base_r, length, lean, half, cols):
    """A layered flame tongue rooted on the rim: outer->core teardrops sharing a
    curling tip so the flame reads amber-edged with a white-hot heart."""
    for col, scale in cols:
        pts = _flame_shape(cx, cy, a, base_r, length * scale, lean,
                           half * (0.5 + 0.5 * scale))
        pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in pts])


def _smoke_curl(surf, cx, cy, a, base_r, length, cols):
    n = 7
    for k in range(n):
        f = k / (n - 1)
        rr = base_r + length * f
        off = math.sin(f * math.pi * 1.7) * length * 0.34
        px = cx + math.cos(a) * rr - math.sin(a) * off
        py = cy + math.sin(a) * rr + math.cos(a) * off
        sz = max(2, int((1.0 - 0.55 * f) * length * 0.42))
        alpha = int(190 * (1.0 - 0.7 * f))
        blob = pygame.Surface((sz * 2 + 2, sz * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(blob, (*cols, alpha), (sz + 1, sz + 1), sz)
        surf.blit(blob, (int(px - sz - 1), int(py - sz - 1)))


def fame_flame(surf, cx, cy, R, glyph_key):
    blit_glow(surf, cx, cy, int(R * 1.45), (255, 168, 70), 80)
    cols = [(_FL_AMBER, 1.0), (_FL_ORANGE, 0.72), (_FL_YEL, 0.46), (_FL_WHITE, 0.24)]
    n = 12
    for i in range(n):
        a = i / n * math.tau - math.pi / 2
        L = R * (0.32 if i % 2 == 0 else 0.21)
        _flame_lick(surf, cx, cy, a, R * 0.97, L, math.radians(13),
                    math.radians(360 / n * 0.5), cols)
    _metal_band(surf, cx, cy, R, int(R * 0.74), _FL_RIM_HI, _FL_RIM_LO,
                spec=_FL_SPEC, edge=_FL_EDGE)
    pygame.draw.circle(surf, _FL_RIM_MID, (cx, cy), R, max(2, R // 24))
    fr = int(R * 0.70)
    ai._draw_step(surf, cx, cy, fr + max(2, R // 16), _FL_RIM_HI, _FL_RIM_LO)
    ai._draw_face(surf, cx, cy, fr, _FL_FACE_TOP, _FL_FACE_BOT, _FL_RECESS)
    _center(surf, glyph_key, cx, cy, R, _FL_GLY, _FL_GLY_SH, ai._GLYPH_SHEEN)


def shame_flame(surf, cx, cy, R, glyph_key):
    n = 12
    # cold smoke rising off half the dead wicks — thick pale curls so the
    # "extinguished" read survives the shrink to 44px
    for i in range(n):
        if i % 2 != 0:
            continue
        a = i / n * math.tau - math.pi / 2
        _smoke_curl(surf, cx, cy, a, R * 1.02, R * 0.40, _FD_SMOKE)
    # charred wick stubs all round the rim — each is a burnt-out flame: the same
    # tongue silhouette, cropped short and sooted black with a faint grey lip
    ember_tips = {6, 1}
    for i in range(n):
        a = i / n * math.tau - math.pi / 2
        L = R * (0.18 if i % 2 == 0 else 0.13)
        pts = _flame_shape(cx, cy, a, R * 0.97, L, math.radians(6),
                           math.radians(360 / n * 0.5))
        pygame.draw.polygon(surf, _FD_SOOT, [(int(x), int(y)) for x, y in pts])
        pygame.draw.lines(surf, _FD_RIM_LO, False,
                          [(int(x), int(y)) for x, y in pts[:len(pts) // 2]],
                          max(1, R // 40))
    _metal_band(surf, cx, cy, R, int(R * 0.74), _FD_RIM_HI, _FD_RIM_LO,
                spec=None, edge=_FD_EDGE)
    _oxide_mottle(surf, cx, cy, int(R * 0.80), int(R * 0.98),
                  (_FD_SOOT, _FD_RIM_LO), seed=41)
    pygame.draw.circle(surf, _FD_RIM_MID, (cx, cy), R, max(2, R // 24))
    # a couple of wick tips still glow as dying coals — the cue that this WAS
    # fire, painted last so the warm ember reads over the cold soot at 44px
    for i in ember_tips:
        a = i / n * math.tau - math.pi / 2
        L = R * (0.18 if i % 2 == 0 else 0.13)
        tx = cx + math.cos(a) * (R * 0.97 + L * 0.55)
        ty = cy + math.sin(a) * (R * 0.97 + L * 0.55)
        blit_glow(surf, int(tx), int(ty), int(R * 0.22), (232, 118, 38), 110)
        pygame.draw.circle(surf, _FD_EMBER, (int(tx), int(ty)), max(3, R // 15))
        pygame.draw.circle(surf, (255, 176, 82),
                           (int(tx - R * 0.02), int(ty - R * 0.02)), max(2, R // 24))
    fr = int(R * 0.70)
    ai._draw_step(surf, cx, cy, fr + max(2, R // 16), _FD_RIM_HI, _FD_RIM_LO)
    ai._draw_face(surf, cx, cy, fr, _FD_FACE_TOP, _FD_FACE_BOT, _FD_RECESS)
    _center(surf, glyph_key, cx, cy, R, _FD_GLY, _FD_GLY_SH)


# ═══════════════════════════════════════════════════════════════════════════
# 4) COIN — a struck proof coin: reeded (milled) edge + engine-turned guilloché.
#    Fame: a mirror-bright gold coin, a ring of fine reeded ticks at the edge and
#    a woven guilloché band engraved into the field, with a strong specular
#    sweep. Shame: the SAME coin CORRODED — green-black verdigris eating the
#    metal, the milling worn smooth on one flank, a flat CLIP shaved off the
#    lower-right edge (raw gouged metal), the guilloché eroded to broken arcs.
# ═══════════════════════════════════════════════════════════════════════════
_CN_RIM_HI = (255, 228, 156)
_CN_RIM_MID = (232, 186, 78)
_CN_RIM_LO = (150, 104, 24)
_CN_EDGE = (78, 50, 12)
_CN_SPEC = (255, 250, 224)
_CN_ENGR = (168, 120, 34)         # engraved guilloché line
_CN_ENGR_HI = (255, 236, 168)
_CN_FACE_TOP = (44, 32, 92)
_CN_FACE_BOT = (16, 10, 44)
_CN_RECESS = (10, 6, 28)
_CN_GLY = (255, 236, 184)
_CN_GLY_SH = (32, 18, 44)

_CD_RIM_HI = (150, 138, 108)      # dulled brassy
_CD_RIM_MID = (110, 96, 66)
_CD_RIM_LO = (66, 56, 38)
_CD_EDGE = (30, 24, 16)
_CD_VERD = (78, 128, 96)          # verdigris green
_CD_VERD_DK = (40, 74, 56)
_CD_GOUGE = (36, 30, 22)          # raw shaved clip metal
_CD_GOUGE_HI = (96, 82, 60)
_CD_FACE_TOP = (46, 44, 40)
_CD_FACE_BOT = (24, 22, 20)
_CD_RECESS = (14, 12, 10)
_CD_GLY = (166, 156, 132)
_CD_GLY_SH = (18, 14, 12)


def _reeding(surf, cx, cy, R, hi, lo, n=60, worn=None):
    """Fine milled edge ticks around the rim. ``worn`` (a0, a1) smooths the ticks
    away over an arc so a corroded coin reads as edge-worn."""
    r0, r1 = R * 0.955, R * 1.028
    for i in range(n):
        a = i / n * math.tau
        if worn and worn[0] <= (a % math.tau) <= worn[1]:
            continue
        col = hi if i % 2 == 0 else lo
        p0 = (cx + math.cos(a) * r0, cy + math.sin(a) * r0)
        p1 = (cx + math.cos(a) * r1, cy + math.sin(a) * r1)
        pygame.draw.line(surf, col, (int(p0[0]), int(p0[1])),
                         (int(p1[0]), int(p1[1])), max(1, R // 40))


def _guilloche(surf, cx, cy, R, engr, engr_hi, rings=5, lobes=14, amp=0.5,
               eroded=False):
    """Engine-turned guilloché in the rim field: concentric circles whose radius
    is sine-modulated, drawn as short arc segments so they weave. ``eroded``
    drops random segments so the pattern reads worn."""
    r_in, r_out = R * 0.76, R * 0.94
    seg = 72
    for ri in range(rings):
        base = r_in + (r_out - r_in) * ri / max(1, rings - 1)
        phase = ri * 0.6
        pts = []
        for k in range(seg + 1):
            a = k / seg * math.tau
            if eroded and (int(a * 3 + ri) % 3 == 0):
                if pts:
                    pygame.draw.lines(surf, engr, False,
                                      [(int(x), int(y)) for x, y in pts], max(1, R // 60))
                    pts = []
                continue
            rr = base + math.sin(a * lobes + phase) * (R * 0.012 * amp)
            pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
        if len(pts) > 1:
            col = engr if eroded else (engr_hi if ri % 2 == 0 else engr)
            pygame.draw.lines(surf, col, False,
                              [(int(x), int(y)) for x, y in pts], max(1, R // 60))


def fame_coin(surf, cx, cy, R, glyph_key):
    _reeding(surf, cx, cy, R, _CN_RIM_HI, _CN_RIM_LO)
    _metal_band(surf, cx, cy, R, int(R * 0.70), _CN_RIM_HI, _CN_RIM_LO,
                spec=_CN_SPEC, edge=_CN_EDGE)
    _guilloche(surf, cx, cy, R, _CN_ENGR, _CN_ENGR_HI)
    pygame.draw.circle(surf, _CN_RIM_MID, (cx, cy), R, max(2, R // 26))
    fr = int(R * 0.66)
    ai._draw_step(surf, cx, cy, fr + max(2, R // 16), _CN_RIM_HI, _CN_RIM_LO)
    ai._draw_face(surf, cx, cy, fr, _CN_FACE_TOP, _CN_FACE_BOT, _CN_RECESS)
    _center(surf, glyph_key, cx, cy, R, _CN_GLY, _CN_GLY_SH, ai._GLYPH_SHEEN)


def _verdigris_creep(surf, cx, cy, R):
    """Corrosion that CREEPS rather than measles: thin crusty patina following the
    reeded milling grooves at the rim, plus a couple of larger bloom patches, so
    it reads as oxide eating into the coin."""
    # crusty streaks tracking the milling grooves (radial, uneven length)
    s = 0x5321
    for i in range(46):
        s = (s * 1103515245 + 12345) & 0x7fffffff
        a = (i / 46) * math.tau
        s = (s * 1103515245 + 12345) & 0x7fffffff
        if (s / 0x7fffffff) < 0.42:                 # patchy, not every groove
            continue
        s = (s * 1103515245 + 12345) & 0x7fffffff
        r0 = R * (0.90 + 0.02 * (s / 0x7fffffff))
        r1 = R * (0.99 + 0.06 * (s / 0x7fffffff))
        col = _CD_VERD if i % 2 else _CD_VERD_DK
        pygame.draw.line(surf, col,
                         (int(cx + math.cos(a) * r0), int(cy + math.sin(a) * r0)),
                         (int(cx + math.cos(a) * r1), int(cy + math.sin(a) * r1)),
                         max(1, R // 34))
    # a couple of larger corrosion blooms creeping across the field
    for ba, br, bs in ((math.radians(205), 0.82, 0.30),
                       (math.radians(300), 0.70, 0.24),
                       (math.radians(150), 0.92, 0.20)):
        bx = cx + math.cos(ba) * R * br
        by = cy + math.sin(ba) * R * br
        for dx, dy, sc in ((0, 0, 1.0), (0.5, 0.2, 0.7), (-0.4, 0.4, 0.6),
                           (0.2, -0.5, 0.55)):
            pygame.draw.circle(surf, _CD_VERD_DK,
                               (int(bx + dx * R * bs), int(by + dy * R * bs)),
                               max(2, int(R * bs * sc * 0.5)))
        pygame.draw.circle(surf, _CD_VERD, (int(bx), int(by)),
                           max(2, int(R * bs * 0.42)))


def shame_coin(surf, cx, cy, R, glyph_key):
    _reeding(surf, cx, cy, R, _CD_RIM_HI, _CD_RIM_LO,
             worn=(math.radians(20), math.radians(140)))
    _metal_band(surf, cx, cy, R, int(R * 0.70), _CD_RIM_HI, _CD_RIM_LO,
                spec=None, edge=_CD_EDGE)
    _guilloche(surf, cx, cy, R, _CD_RIM_LO, _CD_RIM_MID, eroded=True)
    _verdigris_creep(surf, cx, cy, R)
    pygame.draw.circle(surf, _CD_RIM_MID, (cx, cy), R, max(2, R // 26))
    # a flat CLIP shaved off the lower-right edge: the rounded rim replaced by a
    # straight filed chord. The raw circular segment stays entirely INSIDE R (no
    # spill past the badge square), reading as metal shaved off the coin's edge.
    ca = math.radians(38)
    ha = math.radians(34)
    seg = [(cx + math.cos(ca - ha + (2 * ha) * k / 10) * R * 0.995,
            cy + math.sin(ca - ha + (2 * ha) * k / 10) * R * 0.995)
           for k in range(11)]
    pygame.draw.polygon(surf, _CD_GOUGE, [(int(x), int(y)) for x, y in seg])
    # the new flat filed edge, lit along the chord so the shave reads as a facet
    pygame.draw.line(surf, _CD_GOUGE_HI,
                     (int(seg[0][0]), int(seg[0][1])),
                     (int(seg[-1][0]), int(seg[-1][1])), max(2, R // 22))
    fr = int(R * 0.66)
    ai._draw_step(surf, cx, cy, fr + max(2, R // 16), _CD_RIM_HI, _CD_RIM_LO)
    ai._draw_face(surf, cx, cy, fr, _CD_FACE_TOP, _CD_FACE_BOT, _CD_RECESS)
    _center(surf, glyph_key, cx, cy, R, _CD_GLY, _CD_GLY_SH)


# ═══════════════════════════════════════════════════════════════════════════
# 5) ENAMEL — a cloisonné colour ring: jewel enamel cells between gold cloisons.
#    Fame: a band of alternating sapphire / ruby / emerald / amber vitreous cells
#    divided by bright gold wire partitions, each cell glossed with a top glaze.
#    Shame: the SAME enamel CHIPPED & CRAZED — colours burnt to ash, crazing
#    webbing every cell, whole cells chipped out to raw dark metal, the gold
#    cloisons tarnished and lifting.
# ═══════════════════════════════════════════════════════════════════════════
_EN_RIM_HI = (255, 230, 158)
_EN_RIM_MID = (232, 184, 74)
_EN_RIM_LO = (150, 102, 22)
_EN_EDGE = (70, 44, 8)
_EN_SPEC = (255, 250, 222)
_EN_WIRE = (255, 232, 160)
_EN_WIRE_LO = (150, 104, 30)
# Jewel enamel as (deep, bright) pairs so each cell can be domed dark->bright
# for a glassy vitreous read rather than a flat primary.
_EN_CELLS = [
    ((24, 58, 150), (74, 132, 236)),    # sapphire
    ((150, 26, 54), (224, 62, 94)),     # ruby
    ((16, 112, 76), (54, 192, 132)),    # emerald
    ((176, 118, 22), (250, 202, 84)),   # amber
]
_EN_GLAZE = (244, 250, 255)
_EN_FACE_TOP = (40, 32, 90)
_EN_FACE_BOT = (16, 10, 44)
_EN_RECESS = (10, 6, 28)
_EN_GLY = (255, 236, 184)
_EN_GLY_SH = (32, 18, 44)

_ED_RIM_HI = (148, 146, 150)
_ED_RIM_MID = (96, 94, 98)
_ED_RIM_LO = (52, 50, 54)
_ED_EDGE = (24, 22, 24)
_ED_WIRE = (120, 116, 110)        # tarnished cloison
_ED_WIRE_LO = (70, 66, 62)
_ED_METAL = (34, 30, 34)          # raw base metal under a chipped cell
_ED_METAL_HI = (86, 82, 86)
_ED_FACE_TOP = (48, 46, 52)
_ED_FACE_BOT = (24, 22, 28)
_ED_RECESS = (14, 12, 18)
_ED_GLY = (170, 164, 152)
_ED_GLY_SH = (16, 14, 16)


def _ash(col, t=0.66):
    return lerp_color(col, (92, 86, 80), t)


def _enamel_ring(surf, cx, cy, R, wire, wire_lo, cells, n=12, wrecked=False):
    rin, rout = R * 0.80, R * 1.02
    chipped = {1, 5, 8, 10} if wrecked else set()
    band = rout - rin
    for i in range(n):
        a0 = i / n * math.tau
        a1 = (i + 1) / n * math.tau
        deep, bright = cells[i % len(cells)]
        if i in chipped:
            # enamel chipped away to raw pitted metal, with a lit broken lip
            _wedge(surf, cx, cy, a0 + 0.02, a1 - 0.02, rin, rout, _ED_METAL)
            _oxide_mottle(surf, cx, cy, int(rin), int(rout),
                          (_ED_METAL, (24, 22, 26)), seed=90 + i, n=6)
            mid_a = (a0 + a1) / 2
            lip = (cx + math.cos(mid_a) * (rin + band * 0.5),
                   cy + math.sin(mid_a) * (rin + band * 0.5))
            pygame.draw.circle(surf, _ED_METAL_HI, (int(lip[0]), int(lip[1])),
                               max(2, R // 26))
            continue
        if wrecked:
            _wedge(surf, cx, cy, a0 + 0.015, a1 - 0.015, rin, rout, _ash(bright))
            # crazing: a web of fine dark cracks across the burnt cell
            for j in range(3):
                aa = a0 + (a1 - a0) * (0.25 + 0.25 * j)
                p0 = (cx + math.cos(aa) * rin, cy + math.sin(aa) * rin)
                p1 = (cx + math.cos(aa + 0.06) * rout, cy + math.sin(aa + 0.06) * rout)
                pygame.draw.line(surf, (30, 28, 30), (int(p0[0]), int(p0[1])),
                                 (int(p1[0]), int(p1[1])), max(1, R // 64))
            pygame.draw.arc(surf, (30, 28, 30),
                            (cx - int(rout * 0.94), cy - int(rout * 0.94),
                             int(rout * 1.88), int(rout * 1.88)),
                            a0, a1, max(1, R // 60))
        else:
            # domed vitreous cell: deep at the walls -> bright core -> a glassy
            # near-white specular streak on the upper edge (premium enamel gloss)
            _wedge(surf, cx, cy, a0 + 0.015, a1 - 0.015, rin, rout, deep)
            _wedge(surf, cx, cy, a0 + 0.055, a1 - 0.055,
                   rin + band * 0.16, rout - band * 0.12, bright)
            _wedge(surf, cx, cy, a0 + 0.075, (a0 + a1) / 2,
                   rin + band * 0.44, rout - band * 0.18,
                   lerp_color(bright, _EN_GLAZE, 0.7))
    # gold cloison wires: a dark keyline base + a bright raised crest so the cell
    # walls read as crisp raised wire between the colours
    for i in range(n):
        a = i / n * math.tau
        p0 = (cx + math.cos(a) * (rin - band * 0.04), cy + math.sin(a) * (rin - band * 0.04))
        p1 = (cx + math.cos(a) * rout, cy + math.sin(a) * rout)
        pygame.draw.line(surf, wire_lo, (int(p0[0]), int(p0[1])),
                         (int(p1[0]), int(p1[1])), max(3, R // 26))
        if not (wrecked and i % 2 == 0):
            pygame.draw.line(surf, wire, (int(p0[0]), int(p0[1])),
                             (int(p1[0]), int(p1[1])), max(2, R // 42))
    for rr, wc in ((rout, wire), (rin, wire_lo)):
        pygame.draw.circle(surf, wire_lo, (cx, cy), int(rr), max(3, R // 30))
        pygame.draw.circle(surf, wc, (cx, cy), int(rr), max(2, R // 48))


def fame_enamel(surf, cx, cy, R, glyph_key):
    _metal_band(surf, cx, cy, R, int(R * 0.74), _EN_RIM_HI, _EN_RIM_LO,
                spec=_EN_SPEC, edge=_EN_EDGE)
    _enamel_ring(surf, cx, cy, R, _EN_WIRE, _EN_WIRE_LO, _EN_CELLS)
    fr = int(R * 0.70)
    ai._draw_step(surf, cx, cy, fr + max(2, R // 16), _EN_RIM_HI, _EN_RIM_LO)
    ai._draw_face(surf, cx, cy, fr, _EN_FACE_TOP, _EN_FACE_BOT, _EN_RECESS)
    _center(surf, glyph_key, cx, cy, R, _EN_GLY, _EN_GLY_SH, ai._GLYPH_SHEEN)


def shame_enamel(surf, cx, cy, R, glyph_key):
    _metal_band(surf, cx, cy, R, int(R * 0.74), _ED_RIM_HI, _ED_RIM_LO,
                spec=None, edge=_ED_EDGE)
    _enamel_ring(surf, cx, cy, R, _ED_WIRE, _ED_WIRE_LO, _EN_CELLS, wrecked=True)
    _oxide_mottle(surf, cx, cy, int(R * 0.98), int(R * 1.04),
                  (_ED_RIM_LO, _ED_EDGE), seed=61, n=14)
    fr = int(R * 0.70)
    ai._draw_step(surf, cx, cy, fr + max(2, R // 16), _ED_RIM_HI, _ED_RIM_LO)
    ai._draw_face(surf, cx, cy, fr, _ED_FACE_TOP, _ED_FACE_BOT, _ED_RECESS)
    _center(surf, glyph_key, cx, cy, R, _ED_GLY, _ED_GLY_SH)


# Each concept pairs a Fame composer with its degraded Shame twin, plus the
# core-radius fraction that keeps its ornament inside the real badge square.
CONCEPTS = [
    ("seal", fame_seal, shame_seal, 0.38),
    ("gem", fame_gem, shame_gem, 0.39),
    ("flame", fame_flame, shame_flame, 0.37),
    ("coin", fame_coin, shame_coin, 0.44),
    ("enamel", fame_enamel, shame_enamel, 0.42),
]
