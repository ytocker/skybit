"""
Tlaloc-Tiki — the rain-fanged jade idol devil (BATCH 2 / Section 1 Devilish /
GREEN-BAND #2: GREY SLATE-JADE + CORAL FOCAL).

Round-1 concept render. Procedural Pygame, house style: chibi proportions,
flat fills, hard ink keylines, dark-core -> flat-fill -> top-left rim-sheen
triad, 1px alpha-grown outline, supersample -> smoothscale.

WHY a carved-relief idol: the goggle eye-RINGS + carved-seam geometry give a
shape read that survives the green hue collapsing on a green day-sky, and the
CORAL mouth is rendered as the single brightest/warmest mass so the eye lands
on the mouth first and the stone reads as a near-neutral grey-jade backdrop —
that warm-focal-on-neutral split is what separates this green from the pine
(Cernun) and the yellow-green (Kappa).
"""
import os
import math

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame

pygame.init()

# ── PINNED PALETTE (exact hexes from the locked brief) ───────────────────────
# Pushed to the greyer end of the pinned range so the stone stays near-neutral
# against a green day-sky, per the AD must-fix.
STONE      = (96, 128, 124)    # greyer slate-jade base (pinned fallback)
STONE_SHD  = (50,  92,  90)    # deep slate-jade shade  -> dark-core
TURQ       = (120, 210, 196)   # turquoise inlay accent
GOLD       = (226, 186,  80)   # gold goggle-ring
GOLD_SHD   = (164, 130,  44)
CORAL      = (224,  90,  74)   # CORAL-red mouth FOCAL — hero, brightest mass
CORAL_SHD  = (158,  52,  44)
CORAL_LIT  = (248, 138, 110)   # coral inner sheen
INK        = (22,  32,  30)    # keyline ink
SHEEN      = (150, 206, 196)   # top-left rim sheen
TOOTH      = (236, 230, 214)   # fang ivory

# triad shade/sheen for the stone body
def _shade(c, k=0.62):
    return (int(c[0]*k), int(c[1]*k), int(c[2]*k))

# ── tiny vector/scale helpers (mirror parrot.py's _Pg/_Sg grammar) ───────────
def P(pt, s):
    return (int(round(pt[0]*s)), int(round(pt[1]*s)))

def G(v, s):
    return max(1, int(round(v*s)))

def poly(surf, color, pts, s, width=0):
    pygame.draw.polygon(surf, color, [P(p, s) for p in pts], G(width, s) if width else 0)

def line(surf, color, a, b, s, w=1):
    pygame.draw.line(surf, color, P(a, s), P(b, s), G(w, s))

def circ(surf, color, c, r, s, width=0):
    pygame.draw.circle(surf, color, P(c, s), G(r, s), G(width, s) if width else 0)


# ── alpha-grown 1px outline (ported from parrot._add_outline_scaled) ─────────
def add_outline(src, scale, outline_color=INK):
    w, h = src.get_size()
    r = max(1, int(round(scale)))
    pad = r + 1
    out = pygame.Surface((w + pad*2, h + pad*2), pygame.SRCALPHA)
    mask = pygame.mask.from_surface(src, threshold=8)
    sil = mask.to_surface(setcolor=(*outline_color, 235), unsetcolor=(0, 0, 0, 0))
    for dx in range(-r, r+1):
        for dy in range(-r, r+1):
            if dx == 0 and dy == 0:
                continue
            if max(abs(dx), abs(dy)) > r:
                continue
            out.blit(sil, (pad+dx, pad+dy))
    out.blit(src, (pad, pad))
    return out


# Design canvas is 64 units wide; everything below is drawn at `s` supersample.
CW, CH = 64, 72


# ── the carved idol head: triad-lit relief, used by both creature & totem ────
def draw_mask_face(surf, s, cx, cy, scale=1.0, mouth_focal=True):
    """A single Tlaloc temple-mask: squarish stone face, two concentric gold
    goggle eye-rings, downturned coral mouth with two curled serpent-fangs."""
    def x(v): return cx + v*scale
    def y(v): return cy + v*scale

    # squarish stone mask block — dark-core under-shape first (drop the fill
    # down+right so the top-left edge keeps the sheen).
    head = [(-15, -13), (15, -13), (16, 9), (12, 14), (-12, 14), (-16, 9)]
    poly(surf, STONE_SHD, [(x(px+0.8), y(py+1.0)) for px, py in head], s)
    poly(surf, STONE, [(x(px), y(py)) for px, py in head], s)
    # top-left rim sheen: a thin lit lip along the upper-left contour
    line(surf, SHEEN, (x(-15), y(-12.5)), (x(14), y(-12.5)), s, 1.4)
    line(surf, SHEEN, (x(-15.5), y(-12)), (x(-15.5), y(7)), s, 1.4)

    # carved-relief brow band (triad-lit groove) — shape tell independent of hue
    poly(surf, STONE_SHD, [(x(-14), y(-9)), (x(14), y(-9)), (x(13), y(-6)), (x(-13), y(-6))], s)
    line(surf, SHEEN, (x(-13.5), y(-9)), (x(13.5), y(-9)), s, 1.0)
    # turquoise inlay chips in the brow band
    for tx in (-9, -3, 3, 9):
        poly(surf, TURQ, [(x(tx-1.4), y(-8.2)), (x(tx+1.4), y(-8.2)),
                          (x(tx+1.4), y(-6.6)), (x(tx-1.4), y(-6.6))], s)

    # ── goggle eye-RINGS (Tlaloc signature) — two big concentric gold rings ──
    for ex in (-7.5, 7.5):
        # carved socket recess (dark-core)
        circ(surf, STONE_SHD, (x(ex), y(-1)), 6.6*scale, s)
        # outer gold ring
        circ(surf, GOLD_SHD, (x(ex), y(-0.6)), 6.2*scale, s)
        circ(surf, GOLD, (x(ex), y(-1)), 6.2*scale, s)
        # inner stone reveal
        circ(surf, STONE, (x(ex), y(-1)), 4.0*scale, s)
        # inner gold ring
        circ(surf, GOLD, (x(ex), y(-1)), 4.0*scale, s, width=1.4)
        # pupil — dark with a turquoise iris ring + ink dot
        circ(surf, TURQ, (x(ex), y(-1)), 2.6*scale, s)
        circ(surf, INK, (x(ex), y(-1)), 1.5*scale, s)
        # sheen catch top-left of each ring
        circ(surf, SHEEN, (x(ex-3.4), y(-3.6)), 1.0*scale, s)

    # ── CORAL MOUTH FOCAL: wide downturned fanged maw — brightest warm mass ──
    mouth = [(-11, 5), (11, 5), (10, 11.5), (5, 14), (-5, 14), (-10, 11.5)]
    poly(surf, CORAL_SHD, [(x(px+0.6), y(py+0.8)) for px, py in mouth], s)
    poly(surf, CORAL, [(x(px), y(py)) for px, py in mouth], s)
    # coral inner sheen lip (top-left) keeps it reading as the lit/hero mass
    line(surf, CORAL_LIT, (x(-10), y(5.6)), (x(10), y(5.6)), s, 1.4)
    # dark throat under-bite
    poly(surf, INK, [(x(-7), y(9)), (x(7), y(9)), (x(5), y(13)), (x(-5), y(13))], s)

    # upper tooth row inside the maw
    for tx in (-5, -1.6, 1.6, 5):
        poly(surf, TOOTH, [(x(tx-1.1), y(9)), (x(tx+1.1), y(9)),
                           (x(tx+0.7), y(11)), (x(tx-0.7), y(11))], s)

    # two curled serpent-fangs sweeping up out of the mouth corners
    for sgn in (-1, 1):
        bx = 8.5*sgn
        fang = [(bx, 5), (bx+1.6*sgn, 1.5), (bx+0.4*sgn, -1.5),
                (bx-1.2*sgn, 0.5), (bx-1.6*sgn, 4)]
        poly(surf, TOOTH, [(x(px), y(py)) for px, py in fang], s)
        line(surf, GOLD_SHD, (x(bx-1.4*sgn), y(4)), (x(bx+0.2*sgn), y(-1)), s, 0.8)


def draw_creature(s):
    """Full Tlaloc-Tiki imp: carved mask head over a blocky stepped-stone
    body with stubby blocky limbs and carved-relief seams."""
    surf = pygame.Surface((int(CW*s), int(CH*s)), pygame.SRCALPHA)
    cx = 32

    # ── stepped-pyramid stone body (3 receding steps, triad-lit) ────────────
    steps = [
        ((-16, 47), (16, 47), (14, 58), (-14, 58)),   # base step (widest)
        ((-13, 38), (13, 38), (16, 47), (-16, 47)),   # mid step
        ((-10, 30), (10, 30), (13, 38), (-13, 38)),   # neck step (narrowest)
    ]
    for st in steps:
        poly(surf, STONE_SHD, [(cx+px+0.8, py+1.0) for px, py in st], s)
        poly(surf, STONE, [(cx+px, py) for px, py in st], s)
        # carved seam groove between steps (shape tell)
        top = st[0:2]
        line(surf, STONE_SHD, (cx+top[0][0], top[0][1]), (cx+top[1][0], top[1][1]), s, 1.2)
        line(surf, SHEEN, (cx+top[0][0]+1, top[0][1]-0.6), (cx+top[1][0]-1, top[1][1]-0.6), s, 0.8)
    # turquoise inlay band across the chest (mid step)
    for tx in (-8, -2.7, 2.7, 8):
        poly(surf, TURQ, [(cx+tx-1.6, 41), (cx+tx+1.6, 41), (cx+tx+1.6, 43.4), (cx+tx-1.6, 43.4)], s)
    # gold sash line on base step
    line(surf, GOLD, (cx-13, 52), (cx+13, 52), s, 1.4)

    # ── stubby blocky limbs ─────────────────────────────────────────────────
    for sgn in (-1, 1):
        # arms
        ax = sgn*16
        arm = [(ax, 39), (ax+sgn*6, 40), (ax+sgn*6, 47), (ax, 46)]
        poly(surf, STONE_SHD, [(cx+px+0.6, py+0.8) for px, py in arm], s)
        poly(surf, STONE, [(cx+px, py) for px, py in arm], s)
        # blocky three-claw hand
        hx = ax+sgn*6
        poly(surf, STONE, [(cx+hx, 45), (cx+hx+sgn*3.4, 45.5), (cx+hx+sgn*3.4, 49), (cx+hx, 49.5)], s)
        for f in range(3):
            fy = 45.6 + f*1.3
            line(surf, STONE_SHD, (cx+hx+sgn*3.4, fy), (cx+hx+sgn*4.6, fy+0.4), s, 1.0)
        # stubby feet at the base
        fx = sgn*9
        poly(surf, STONE_SHD, [(cx+fx-4, 58), (cx+fx+4, 58), (cx+fx+5, 62), (cx+fx-5, 62)], s)
        poly(surf, STONE, [(cx+fx-4, 57.4), (cx+fx+4, 57.4), (cx+fx+4.4, 61), (cx+fx-4.4, 61)], s)

    # ── carved mask head on top ─────────────────────────────────────────────
    draw_mask_face(surf, s, cx, 16, scale=1.0)

    return surf


def draw_totem(s):
    """Prop -> pillar: carved TOTEM / stela column. Stacked mini-mask bands =
    repeatable shaft body; feathered-serpent head finial = gap-edge cap.
    Symmetric carved column — clean mirror."""
    TW, TH = 52, 116
    surf = pygame.Surface((int(TW*s), int(TH*s)), pygame.SRCALPHA)
    cx = TW/2

    # column shaft (slightly tapered, two side rails so the mirror reads clean)
    shaft = [(-19, 24), (19, 24), (17, 110), (-17, 110)]
    poly(surf, STONE_SHD, [(cx+px+0.8, py+1.0) for px, py in shaft], s)
    poly(surf, STONE, [(cx+px, py) for px, py in shaft], s)
    line(surf, SHEEN, (cx-18, 25), (cx-18, 108), s, 1.2)

    # ── feathered-serpent head FINIAL (gap-edge cap) ────────────────────────
    # plumed crest of turquoise feather-fans fanning up off the top
    for fx, fh in ((-13, 14), (-6.5, 19), (0, 22), (6.5, 19), (13, 14)):
        feather = [(cx+fx, 24), (cx+fx-2.2, 24-fh), (cx+fx+2.2, 24-fh)]
        poly(surf, _shade(TURQ), [(p[0]+0.6, p[1]+0.8) for p in feather], s)
        poly(surf, TURQ, feather, s)
        line(surf, SHEEN, (cx+fx-2, 24-fh+2), (cx+fx, 24-fh), s, 0.8)
    # serpent snout jutting forward under the crest
    snout = [(cx-18, 16), (cx+18, 16), (cx+16, 26), (cx-16, 26)]
    poly(surf, STONE_SHD, [(p[0]+0.6, p[1]+0.8) for p in snout], s)
    poly(surf, STONE, snout, s)
    line(surf, SHEEN, (cx-17, 16.6), (cx+17, 16.6), s, 1.0)
    # serpent goggle-eyes (echo the creature's gold rings, smaller)
    for ex in (-9, 9):
        circ(surf, GOLD, (cx+ex, 21), 3.2, s)
        circ(surf, TURQ, (cx+ex, 21), 1.7, s)
        circ(surf, INK, (cx+ex, 21), 0.9, s)
    # coral fanged maw on the finial — the cap's warm focal, biting at the gap
    maw = [(cx-12, 23), (cx+12, 23), (cx+9, 30), (cx-9, 30)]
    poly(surf, CORAL_SHD, [(p[0]+0.5, p[1]+0.7) for p in maw], s)
    poly(surf, CORAL, maw, s)
    line(surf, CORAL_LIT, (cx-11, 23.6), (cx+11, 23.6), s, 1.2)
    for tx in (-7, -2.5, 2.5, 7):
        poly(surf, TOOTH, [(cx+tx-1.3, 23.5), (cx+tx+1.3, 23.5),
                           (cx+tx+0.9, 26.5), (cx+tx-0.9, 26.5)], s)

    # ── repeatable shaft BODY: 3 stacked mini-mask bands ────────────────────
    band_ys = (40, 64, 88)
    for by in band_ys:
        # band divider seams (carved relief)
        line(surf, STONE_SHD, (cx-18, by-9), (cx+18, by-9), s, 1.2)
        line(surf, SHEEN, (cx-17, by-9.6), (cx+17, by-9.6), s, 0.7)
        # a compact stacked mini-mask centered in the band
        draw_mini_mask(surf, s, cx, by)
    line(surf, STONE_SHD, (cx-17, 110), (cx+17, 110), s, 1.2)

    return surf


def draw_mini_mask(surf, s, cx, cy):
    """A compact carved face for the totem shaft bands — goggle-ring read +
    coral mouth focal preserved at small size."""
    def x(v): return cx+v
    def y(v): return cy+v
    # goggle eyes
    for ex in (-8, 8):
        circ(surf, STONE_SHD, (x(ex), y(-3)), 4.6, s)
        circ(surf, GOLD, (x(ex), y(-3)), 4.0, s)
        circ(surf, STONE, (x(ex), y(-3)), 2.3, s)
        circ(surf, TURQ, (x(ex), y(-3)), 1.5, s)
        circ(surf, INK, (x(ex), y(-3)), 0.8, s)
    # turquoise inlay nose chip
    poly(surf, TURQ, [(x(-1.4), y(0)), (x(1.4), y(0)), (x(1), y(3)), (x(-1), y(3))], s)
    # coral mouth focal
    maw = [(x(-9), y(4)), (x(9), y(4)), (x(7), y(8)), (x(-7), y(8))]
    poly(surf, CORAL_SHD, [(p[0]+0.4, p[1]+0.6) for p in maw], s)
    poly(surf, CORAL, maw, s)
    line(surf, CORAL_LIT, (x(-8), y(4.5)), (x(8), y(4.5)), s, 1.0)
    for tx in (-5, -1.7, 1.7, 5):
        poly(surf, TOOTH, [(x(tx-1), y(4.2)), (x(tx+1), y(4.2)),
                           (x(tx+0.6), y(6.6)), (x(tx-0.6), y(6.6))], s)


# ── build + supersample-down ──────────────────────────────────────────────
def baked(build_fn, scale, target_w):
    SS = 4.0
    src = build_fn(SS)
    outlined = add_outline(src, SS)
    w, h = outlined.get_size()
    th = int(round(target_w * h / w))
    return pygame.transform.smoothscale(outlined, (target_w, th))


def render_at_px(build_fn, px_w):
    """Render directly to a small pixel target (for the 32px scale views) with
    a thinner outline scale so the keyline stays ~1px after downscale."""
    SS = 4.0
    src = build_fn(SS)
    outlined = add_outline(src, SS)
    w, h = outlined.get_size()
    ph = int(round(px_w * h / w))
    return pygame.transform.smoothscale(outlined, (px_w, ph))


# ── compose the review sheet ────────────────────────────────────────────────
def main():
    creature_big = baked(draw_creature, 4.0, 260)
    totem_big = baked(draw_totem, 4.0, 210)
    creature_32 = render_at_px(draw_creature, 32)
    totem_32w = int(round(32 * (52/64)))  # keep relative footprint
    totem_32 = render_at_px(draw_totem, 28)

    W, H = 860, 620
    sheet = pygame.Surface((W, H))

    # backdrop split: left = neutral grey card to judge stone neutrality,
    # right = a green day-sky strip to prove the stone does NOT melt into it.
    sheet.fill((46, 50, 58))
    green_sky = pygame.Surface((W, H))
    for yy in range(H):
        t = yy / H
        c = (int(70 + 60*t), int(150 + 50*t), int(70 + 40*t))
        pygame.draw.line(green_sky, c, (0, yy), (W, yy))
    sheet.blit(green_sky, (W//2, 0), pygame.Rect(W//2, 0, W//2, H))
    pygame.draw.line(sheet, (20, 22, 28), (W//2, 0), (W//2, H), 2)

    f_big = pygame.font.SysFont("dejavusans", 20, bold=True)
    f_sm = pygame.font.SysFont("dejavusans", 14)
    f_xs = pygame.font.SysFont("dejavusans", 12)

    def label(txt, x, y, font=f_sm, col=(236, 238, 240)):
        sh = font.render(txt, True, (0, 0, 0))
        sheet.blit(sh, (x+1, y+1))
        sheet.blit(font.render(txt, True, col), (x, y))

    label("TLALOC-TIKI — rain-fanged jade idol devil   |   GREEN-BAND #2: GREY SLATE-JADE + CORAL FOCAL",
          16, 12, f_big)
    label("round 1   ·   left: neutral card (stone neutrality)   ·   right: green day-sky (must NOT melt into it)",
          16, 40, f_xs, (200, 206, 214))

    # creature — large, on the neutral side
    cr = creature_big.get_rect()
    cr.topleft = (40, 80)
    sheet.blit(creature_big, cr)
    label("creature — carved temple-mask + stepped-stone body", 30, cr.bottom + 6, f_sm)
    label("goggle eye-RINGS + carved seams = shape tell", 30, cr.bottom + 24, f_xs, (190, 196, 204))

    # totem — large, straddling onto the green side to prove separation
    tr = totem_big.get_rect()
    tr.topleft = (400, 70)
    sheet.blit(totem_big, tr)
    label("prop -> pillar: carved totem / stela", tr.left - 10, tr.bottom + 6, f_sm)
    label("feathered-serpent head = gap-cap · stacked", tr.left - 10, tr.bottom + 24, f_xs, (235, 238, 242))
    label("mini-mask bands = repeatable shaft", tr.left - 10, tr.bottom + 38, f_xs, (235, 238, 242))

    # 32px scale row — both on green-sky tiles to prove the read holds
    sx = 640
    sy = 360
    for i, (spr, name) in enumerate(((creature_32, "32px"), (totem_32, "28px"))):
        tile = pygame.Surface((54, 60))
        for yy in range(60):
            t = yy/60
            tile.fill((int(80+50*t), int(160+40*t), int(80+30*t)))
            pygame.draw.line(tile, (int(80+50*t), int(160+40*t), int(80+30*t)), (0, yy), (54, yy))
        tx = sx + i*88
        sheet.blit(tile, (tx, sy))
        pygame.draw.rect(sheet, (20, 22, 28), (tx, sy, 54, 60), 1)
        r = spr.get_rect(center=(tx+27, sy+30))
        sheet.blit(spr, r)
        label(name, tx+6, sy+62, f_xs, (28, 30, 34))

    label("32px game scale — read survives the downscale", sx, sy - 22, f_xs, (28, 32, 24))

    # palette swatch strip
    py = 470
    label("PINNED PALETTE", sx, py - 20, f_xs, (236, 238, 240))
    swatches = [("stone", STONE), ("shade", STONE_SHD), ("turq", TURQ),
                ("gold", GOLD), ("CORAL focal", CORAL), ("sheen", SHEEN), ("ink", INK)]
    for i, (nm, col) in enumerate(swatches):
        ry = py + i*20
        pygame.draw.rect(sheet, col, (sx, ry, 18, 16))
        pygame.draw.rect(sheet, (10, 10, 14), (sx, ry, 18, 16), 1)
        label(nm, sx + 24, ry + 1, f_xs, (230, 232, 236))

    pygame.image.save(sheet, "/home/user/skybit/docs/skybit_devil/batch2/tlaloc_tiki/round_1.png")
    print("saved round_1.png")


if __name__ == "__main__":
    main()
