"""
Review renderer for RAIJIN — the thunder-drum ring demon
(Section 3 Japanese, GREY RECEDES; GOLD+CRIMSON FOCAL).

House style: chibi, flat saturated fills, hard ink keylines, the
dark-core -> flat-fill -> top-left rim-sheen TRIAD, a 1px outline grown from
the alpha mask, and supersample -> smoothscale. The creature is drawn once at
a high supersample factor onto a transparent surface, outlined from its own
alpha mask, then downscaled for the crisp large + 32px review tiles.

The key brief constraint: the storm-grey-blue BODY is low-contrast and is
designed to RECEDE into a dark-blue night sky; the GOLD lightning-zags and
CRIMSON drum-rims are the brightest, highest-contrast masses so they read
FIRST. The wholly-unique read is the drum-ring HALO — a crown of taiko drums
arcing OVER the head with open sky between skull and ring — so the circle
silhouette is legible at 32px; the accessibility tell is that drum-ring CIRCLE
plus zag SHAPE, carrying the read where the grey body can't.

Round 2 (AD critique): the halo is re-staged as a true overhead ARC of 4
LARGE drums cresting clear above the head (sky visible between), gold is
committed to lightning-zags radiating from the ring (mallets demoted to clear
diagonal sticks held low), the pillar cap is pulled tight onto the shaft and
shrunk with its zag dropping into the gap, shaft banding is calmed to two wood
bands, and spiky storm-hair frames the head.

Standalone headless script: writes round_2.png next to itself. No game imports
so the review sheet stays reproducible in isolation.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import math
import pygame

# ── PINNED PALETTE (exact hexes from the locked Raijin brief) ───────────────
BODY      = (108, 124, 144)   # storm-grey-blue body — RECEDES, low chroma/mid value
BODY_D    = (66, 80, 100)     # deep-slate shade (dark core)
SHEEN     = (168, 184, 204)   # top-left rim sheen
GOLD      = (248, 212, 96)    # thunder-gold lightning FOCAL
GOLD_D    = (196, 156, 52)    # gold dark core (derived, same family)
GOLD_RIM  = (255, 240, 168)   # gold sheen (derived)
CRIMSON   = (206, 62, 52)     # drum-crimson rim FOCAL
CRIMSON_D = (150, 34, 30)     # crimson dark core (derived)
CRIMSON_R = (236, 116, 96)    # crimson sheen (derived)
CLOUD     = (232, 236, 240)   # cloud-white
CLOUD_D   = (188, 196, 210)   # cloud shade (derived)
TOMOE_INK = (34, 30, 38)      # tomoe comma-swirl ink on drum heads
INK       = (24, 28, 34)      # keyline ink
DRUM_SKIN = (224, 206, 176)   # taiko drum head (vellum) — neutral, sits under focal
DRUM_SK_D = (180, 158, 124)
DRUM_BODY = (120, 78, 52)     # drum wood barrel body (warm brown, low key)
DRUM_BD_D = (84, 52, 34)
DRUM_BD_R = (160, 112, 78)
TIGER     = (216, 178, 96)    # tiger-print wrap base (muted ochre, NOT a focal)
TIGER_D   = (150, 116, 56)

SS = 4   # supersample factor for the large render


def _poly(surf, color, pts):
    pygame.draw.polygon(surf, color, [(int(x), int(y)) for x, y in pts])


def _ellipse(surf, color, cx, cy, rx, ry):
    pygame.draw.ellipse(surf, color, (int(cx - rx), int(cy - ry), int(rx * 2), int(ry * 2)))


def grow_outline(src, ink, px):
    """1px (scaled) ink keyline grown from the sprite's own alpha mask, so the
    silhouette POPs against any biome. We dilate by stamping the alpha mask in
    a ring of offsets behind the art."""
    mask = pygame.mask.from_surface(src)
    out = pygame.Surface(src.get_size(), pygame.SRCALPHA)
    stamp = mask.to_surface(setcolor=(*ink, 255), unsetcolor=(0, 0, 0, 0))
    r = px
    for dx in range(-r, r + 1):
        for dy in range(-r, r + 1):
            if dx * dx + dy * dy <= r * r:
                out.blit(stamp, (dx, dy))
    out.blit(src, (0, 0))
    return out


def _zag(surf, pts, w):
    """A jagged lightning bolt through `pts` — the gold FOCAL. Drawn as a
    dark-core stroke, a flat-fill stroke, then a thin top-left rim sheen, so it
    carries the same triad as the solid masses but stays the brightest."""
    ip = [(int(a), int(b)) for a, b in pts]
    pygame.draw.lines(surf, GOLD_D, False, ip, int(w * 2.0))
    pygame.draw.lines(surf, GOLD, False, ip, int(w))
    pygame.draw.lines(surf, GOLD_RIM, False,
                      [(a - int(w * 0.4), b - int(w * 0.4)) for a, b in ip], max(1, int(w * 0.4)))


def _radial_zag(surf, x0, y0, x1, y1, w):
    """A short 3-kink lightning fork between two points — used to radiate gold
    OUT of the drum-ring so the gold language is unambiguously zags, not
    mallet shafts."""
    pts = [(x0, y0)]
    dx, dy = (x1 - x0), (y1 - y0)
    ln = max(1.0, math.hypot(dx, dy))
    px, py = -dy / ln, dx / ln
    for i in (1, 2):
        t = i / 3
        mx, my = x0 + dx * t, y0 + dy * t
        off = (w * 1.5) * (1 if i % 2 else -1)
        pts.append((mx + px * off, my + py * off))
    pts.append((x1, y1))
    _zag(surf, pts, w)


def _taiko_drum(surf, cx, cy, r, ang, s):
    """One taiko drum on the halo ring. CRIMSON laced rim is the focal; vellum
    head carries a TOMOE comma-swirl. `ang` rolls the tomoe so the ring of
    heads reads as a crown facing outward."""
    # wood barrel body peeking behind the head (low-key brown, recedes)
    bw, bh = r * 1.05, r * 1.18
    _ellipse(surf, DRUM_BD_D, cx + 1.5 * s, cy + 1.5 * s, bw, bh)
    _ellipse(surf, DRUM_BODY, cx, cy, bw - 1.0 * s, bh - 1.0 * s)
    _ellipse(surf, DRUM_BD_R, cx - bw * 0.32, cy - bh * 0.34, bw * 0.30, bh * 0.30)

    # CRIMSON rim ring — the focal. A fat crimson disc with the vellum head
    # inset, leaving the crimson as a bold ring.
    _ellipse(surf, CRIMSON_D, cx + 0.8 * s, cy + 0.8 * s, r + 0.5 * s, r + 0.5 * s)
    _ellipse(surf, CRIMSON, cx, cy, r, r)
    _ellipse(surf, CRIMSON_R, cx - r * 0.42, cy - r * 0.42, r * 0.34, r * 0.34)
    # vellum head inset
    hr = r * 0.66
    _ellipse(surf, DRUM_SK_D, cx + 0.5 * s, cy + 0.5 * s, hr + 0.4 * s, hr + 0.4 * s)
    _ellipse(surf, DRUM_SKIN, cx, cy, hr, hr)
    _ellipse(surf, (240, 226, 200), cx - hr * 0.4, cy - hr * 0.4, hr * 0.30, hr * 0.30)

    # tomoe comma-swirl ink on the head (two-comma mitsudomoe-lite)
    for k in range(2):
        a = ang + k * math.pi
        tx = cx + math.cos(a) * hr * 0.28
        ty = cy + math.sin(a) * hr * 0.28
        _ellipse(surf, TOMOE_INK, tx, ty, hr * 0.30, hr * 0.30)
        tpts = []
        for j in range(5):
            tt = j / 4
            aa = a + tt * 2.1
            tpts.append((tx + math.cos(aa) * (hr * 0.42 * tt),
                         ty + math.sin(aa) * (hr * 0.42 * tt)))
        if len(tpts) > 1:
            pygame.draw.lines(surf, TOMOE_INK, False,
                              [(int(a2), int(b2)) for a2, b2 in tpts], max(1, int(s * 1.4)))

    # crimson lacing ticks around the rim
    for a in range(0, 360, 72):
        ar = math.radians(a)
        x0 = cx + math.cos(ar) * r * 0.86
        y0 = cy + math.sin(ar) * r * 0.86
        x1 = cx + math.cos(ar) * (r + 1.6 * s)
        y1 = cy + math.sin(ar) * (r + 1.6 * s)
        pygame.draw.line(surf, CRIMSON_D, (int(x0), int(y0)), (int(x1), int(y1)), max(1, int(s)))


def draw_raijin(surf, ox, oy, s):
    """Draw the chibi storm-god centred near (ox, oy). `s` is unit scale.
    Drum-ring halo CRESTS overhead with sky between head and ring; the grey
    body sits low-contrast below; gold zags + crimson rims are the focal."""

    def P(x, y):  # local unit coords -> surface px
        return (ox + x * s, oy + y * s)

    # ---- cloud-puff perch (drawn first, behind feet) ----
    cl_y = 32
    for cdx, cw, ch in [(-12, 13, 7), (12, 13, 7), (0, 16, 8), (-6, 11, 6), (7, 11, 6)]:
        _ellipse(surf, CLOUD_D, ox + (cdx) * s, oy + (cl_y + 1) * s, cw * s, ch * s)
        _ellipse(surf, CLOUD, ox + (cdx) * s, oy + cl_y * s, (cw - 1) * s, (ch - 1) * s)

    # ---- drum-ring HALO cresting OVERHEAD (the unique read) ----
    # The whole gate item: 4 LARGE drums on a high arc whose lowest points clear
    # the TOP of the head, leaving open sky between skull and ring so the CIRCLE
    # silhouette reads. The ring centre sits well above the head; the angular
    # sweep is kept near the top of the circle (a crown, not a full wreath).
    ring_cx, ring_cy = 0, -23
    ring_r = 23
    drum_r = 9.0
    # symmetric sweep across the crown of the circle (screen coords, y down)
    sweep = [206, 246, 294, 334]
    for deg in sweep:
        a = math.radians(deg)
        dx = ring_cx + math.cos(a) * ring_r
        dy = ring_cy + math.sin(a) * ring_r
        # gold lightning-zags radiating OUTWARD from each drum along the ring
        # radius — commits the gold language to zags, the pinned focal.
        zx = ring_cx + math.cos(a) * (ring_r + drum_r + 6)
        zy = ring_cy + math.sin(a) * (ring_r + drum_r + 6)
        _radial_zag(surf, ox + dx * s, oy + dy * s, ox + zx * s, oy + zy * s, 2.0 * s)
    for deg in sweep:
        a = math.radians(deg)
        dx = ring_cx + math.cos(a) * ring_r
        dy = ring_cy + math.sin(a) * ring_r
        _taiko_drum(surf, ox + dx * s, oy + dy * s, drum_r * s, a + math.pi / 2, s)

    # ---- wild spiky flame-hair framing the head (grey-blue, recedes) ----
    # Sits in the open sky BELOW the ring and to the sides of the skull, so the
    # head silhouette has wild-god energy without filling the halo gap.
    spikes = [(-11, -8, -17, -18), (-6, -11, -8, -22),
              (6, -11, 8, -22), (11, -8, 17, -18),
              (-14, -2, -23, -6), (14, -2, 23, -6)]
    for bx, by, tx, ty in spikes:
        pts = [P(bx - 2.6, by), P(tx, ty), P(bx + 2.6, by)]
        _poly(surf, BODY_D, [(x + 1.5, y + 1.5) for x, y in pts])
        _poly(surf, BODY, pts)

    # ---- muscular storm-grey torso (chibi, short + wide, weight-shifted) ----
    tx, ty = 0, 12
    _ellipse(surf, BODY_D, *P(tx, ty + 1), 16 * s, 17 * s)            # dark core
    _ellipse(surf, BODY, ox + (tx + 1) * s, oy + (ty + 1) * s, 14.5 * s, 15.5 * s)  # fill
    _ellipse(surf, SHEEN, ox + (tx - 6) * s, oy + (ty - 6) * s, 6 * s, 5 * s)       # TL rim sheen

    # pectoral / muscle seams (triad-lit grooves, very low contrast — recede)
    pygame.draw.line(surf, BODY_D, P(-7, 6), P(-2, 9), max(1, int(s)))
    pygame.draw.line(surf, BODY_D, P(7, 6), P(2, 9), max(1, int(s)))
    pygame.draw.line(surf, BODY_D, P(0, 9), P(0, 18), max(1, int(s)))

    # ---- tiger-print loincloth wrap (muted ochre, NOT a focal) ----
    wrap = [(-12, 18), (12, 18), (10, 28), (-10, 28)]
    _poly(surf, TIGER_D, [P(x + 1, y + 1) for x, y in wrap])
    _poly(surf, TIGER, [P(x, y) for x, y in wrap])
    # tiger stripes (dark slashes) + short ink dashes so it doesn't read as a
    # plain ochre belt at 32px
    for sx in (-7, -1, 5):
        pygame.draw.line(surf, TIGER_D, P(sx, 19), P(sx - 2, 27), max(1, int(s * 1.2)))
    for dxp in (-9, 3):
        pygame.draw.line(surf, INK, P(dxp, 21), P(dxp - 1.4, 25), max(1, int(s)))
    pygame.draw.rect(surf, BODY_D, (int(P(-12, 17)[0]), int(P(-12, 17)[1]), int(24 * s), int(2.2 * s)))

    # ---- legs perched squat on the cloud ----
    for lx, sign in [(-7, -1), (7, 1)]:
        leg = [(lx - 3, 27), (lx + 3, 27), (lx + 5, 33),
               (lx + sign * 2, 35), (lx - 3, 33)]
        _poly(surf, BODY_D, [P(x + 1, y + 1) for x, y in leg])
        _poly(surf, BODY, [P(x, y) for x, y in leg])

    # ---- arms raised gripping mallets (bachi), demoted to clear grey-wood
    # diagonal sticks so gold belongs to the zags alone ----
    def arm_and_mallet(shoulder, elbow, hand, tip):
        sx, sy = shoulder
        ex, ey = elbow
        hx, hy = hand
        pygame.draw.line(surf, BODY_D, P(sx, sy + 0.5), P(ex, ey + 0.5), max(2, int(4.2 * s)))
        pygame.draw.line(surf, BODY, P(sx, sy), P(ex, ey), max(2, int(3.4 * s)))
        pygame.draw.line(surf, BODY_D, P(ex, ey + 0.5), P(hx, hy + 0.5), max(2, int(3.8 * s)))
        pygame.draw.line(surf, BODY, P(ex, ey), P(hx, hy), max(2, int(3.0 * s)))
        # fist
        _ellipse(surf, BODY_D, *P(hx, hy + 0.4), 3 * s, 3 * s)
        _ellipse(surf, BODY, ox + hx * s, oy + hy * s, 2.6 * s, 2.6 * s)
        # mallet shaft (plain wood, low key) + knob — reads as a stick, no gold
        pygame.draw.line(surf, DRUM_BD_D, P(hx, hy + 0.4), (tip[0] + 0.6, tip[1] + 0.6), max(2, int(2.6 * s)))
        pygame.draw.line(surf, DRUM_BODY, P(hx, hy), tip, max(2, int(2.0 * s)))
        _ellipse(surf, DRUM_BD_D, tip[0] + 0.8 * s, tip[1] + 0.8 * s, 3.0 * s, 3.0 * s)
        _ellipse(surf, DRUM_BODY, *tip, 2.6 * s, 2.6 * s)
        _ellipse(surf, DRUM_BD_R, tip[0] - 1.0 * s, tip[1] - 1.0 * s, 1.0 * s, 1.0 * s)

    # hands held just outside the body at chest height, mallet tips angled up
    # toward (not into) the ring — they support the pose without competing.
    arm_and_mallet((-12, 6), (-18, 0), (-21, -4), P(-23, -12))
    arm_and_mallet((12, 6), (18, 0), (21, -4), P(23, -12))

    # ---- head: chibi, big, fierce ----
    hx, hy, hr = 0, -11, 13
    _ellipse(surf, BODY_D, *P(hx, hy), hr * s, (hr - 0.5) * s)
    _ellipse(surf, BODY, ox + (hx + 1) * s, oy + (hy + 1) * s, (hr - 1.5) * s, (hr - 2) * s)
    _ellipse(surf, SHEEN, ox + (hx - 5) * s, oy + (hy - 5) * s, 5 * s, 4.5 * s)
    # jaw flare / wide shout
    _ellipse(surf, BODY, ox + hx * s, oy + (hy + 5) * s, (hr - 2) * s, 9 * s)

    # ---- fierce round eyes (whites with gold-amber glow ring) ----
    for ex in (-6, 6):
        _ellipse(surf, CLOUD, *P(hx + ex, hy - 1), 4.2 * s, 4.6 * s)
        _ellipse(surf, GOLD, ox + (hx + ex) * s, oy + (hy - 0.5) * s, 2.6 * s, 2.8 * s)
        _ellipse(surf, INK, ox + (hx + ex + ex * 0.08) * s, oy + (hy) * s, 1.5 * s, 1.7 * s)
        _ellipse(surf, CLOUD, ox + (hx + ex - 1.1) * s, oy + (hy - 1.6) * s, 0.9 * s, 0.9 * s)
    # furious angled brows (dark, low-contrast)
    pygame.draw.line(surf, BODY_D, P(hx - 10, hy - 5), P(hx - 2, hy - 2), max(2, int(2 * s)))
    pygame.draw.line(surf, BODY_D, P(hx + 10, hy - 5), P(hx + 2, hy - 2), max(2, int(2 * s)))

    # ---- wide open shout mouth (dark hollow + tiny fangs) — a second crimson
    # note low on the body that ties the rims to the face ----
    mpts = [(-5, 5), (5, 5), (4, 10), (0, 12), (-4, 10)]
    _poly(surf, INK, [P(x, y) for x, y in mpts])
    _poly(surf, CRIMSON_D, [P(x * 0.7, y * 0.7 + 4.4) for x, y in mpts])
    _poly(surf, CLOUD, [P(-4, 5), P(-2.5, 5), P(-3.2, 7.5)])
    _poly(surf, CLOUD, [P(4, 5), P(2.5, 5), P(3.2, 7.5)])


def draw_mallet_drum_pillar(surf, cx, top, bottom, w, s, cap=True):
    """Prop -> PILLAR mirror: a banded drum-MALLET (bachi) shaft is the
    repeatable body; a single modest FRONT-ON taiko drum with a lightning-zag
    cracking it is the detachable gap-edge cap.

    TOP-HEAVY FIX (per AD): the cap drum is rendered front-on and MODEST
    (~shaft-width +30%, NOT the full creature drum-ring), seated TIGHT on the
    haft (it overlaps the shaft top rather than floating on a stem), with the
    CRIMSON rim + a short GOLD zag dropping DOWN INTO the gap so the visual mass
    falls toward the gap line — balanced like Big Reapy's bone-bident. Shaft
    banding is calmed to two wood bands so it does not strobe while scrolling."""
    half = w // 2
    # ---- mallet-shaft body (banded wood) ----
    pygame.draw.rect(surf, DRUM_BD_D, (cx - half - int(2 * s), top, w + int(4 * s), bottom - top))
    pygame.draw.rect(surf, DRUM_BODY, (cx - half, top, w, bottom - top))
    pygame.draw.rect(surf, DRUM_BD_R, (cx - half + int(2 * s), top, max(2, w // 5), bottom - top))
    # two calm rope-grip wood bands (no crimson — let the cap carry the focal)
    span = bottom - top
    for frac in (0.40, 0.74):
        y = int(top + span * frac)
        pygame.draw.rect(surf, DRUM_BD_D, (cx - half - int(3 * s), y - int(2 * s),
                                           w + int(6 * s), int(4 * s)))

    if cap:
        # ---- gap-edge cap: modest front-on taiko drum cracked by a zag ----
        # Drum diameter ~ shaft +30%; seated so its lower edge OVERLAPS the
        # shaft top (mass pulled down onto the haft, not ballooning above it).
        dr = (w * 1.30) / 2
        dcx = cx
        dcy = top - dr * 0.55
        _ellipse(surf, DRUM_BD_D, dcx + 1.5 * s, dcy + 1.5 * s, dr * 1.05, dr * 1.16)
        _ellipse(surf, DRUM_BODY, dcx, dcy, dr * 0.98, dr * 1.08)
        # CRIMSON rim ring (focal)
        _ellipse(surf, CRIMSON_D, dcx + 0.8 * s, dcy + 0.8 * s, dr + 0.6 * s, dr + 0.6 * s)
        _ellipse(surf, CRIMSON, dcx, dcy, dr, dr)
        _ellipse(surf, CRIMSON_R, dcx - dr * 0.42, dcy - dr * 0.42, dr * 0.32, dr * 0.32)
        # vellum head
        hr = dr * 0.68
        _ellipse(surf, DRUM_SK_D, dcx + 0.5 * s, dcy + 0.5 * s, hr + 0.4 * s, hr + 0.4 * s)
        _ellipse(surf, DRUM_SKIN, dcx, dcy, hr, hr)
        # tomoe swirl
        for k in range(2):
            a = (k * math.pi) - 0.6
            tx = dcx + math.cos(a) * hr * 0.28
            tyy = dcy + math.sin(a) * hr * 0.28
            _ellipse(surf, TOMOE_INK, tx, tyy, hr * 0.30, hr * 0.30)
            tpts = []
            for j in range(5):
                tt = j / 4
                aa = a + tt * 2.1
                tpts.append((tx + math.cos(aa) * (hr * 0.42 * tt),
                             tyy + math.sin(aa) * (hr * 0.42 * tt)))
            pygame.draw.lines(surf, TOMOE_INK, False,
                              [(int(a2), int(b2)) for a2, b2 in tpts], max(1, int(s * 1.4)))
        # crimson lacing ticks
        for a in range(0, 360, 72):
            ar = math.radians(a)
            x0 = dcx + math.cos(ar) * dr * 0.86
            y0 = dcy + math.sin(ar) * dr * 0.86
            x1 = dcx + math.cos(ar) * (dr + 1.6 * s)
            y1 = dcy + math.sin(ar) * (dr + 1.6 * s)
            pygame.draw.line(surf, CRIMSON_D, (int(x0), int(y0)), (int(x1), int(y1)), max(1, int(s)))
        # short GOLD zag cracking the drum head and DROPPING DOWN INTO the gap —
        # a clean 3-kink fork (not a swirl), pulling visual mass to the gap line.
        zpts = [(dcx + dr * 0.16, dcy - dr * 0.30),
                (dcx - dr * 0.20, dcy + dr * 0.12),
                (dcx + dr * 0.12, dcy + dr * 0.46),
                (dcx - w * 0.12, top + int(4 * s))]
        _zag(surf, zpts, 2.0 * s)


def build_raijin_sprite(unit_px):
    """Render raijin at unit_px supersampled, outline from its alpha mask,
    return the high-res surface (caller smoothscales)."""
    W = int(64 * unit_px)
    H = int(86 * unit_px)
    big = pygame.Surface((W * SS, H * SS), pygame.SRCALPHA)
    draw_raijin(big, big.get_width() // 2, int(H * SS * 0.62), unit_px * SS)
    big = grow_outline(big, INK, SS)
    return big, (W, H)


def build_pillar_sprite(unit_px):
    W = int(34 * unit_px)
    H = int(98 * unit_px)
    big = pygame.Surface((W * SS, H * SS), pygame.SRCALPHA)
    draw_mallet_drum_pillar(big, big.get_width() // 2,
                            int(24 * unit_px * SS), big.get_height(),
                            int(12 * unit_px * SS), unit_px * SS, cap=True)
    big = grow_outline(big, INK, SS)
    return big, (W, H)


def main():
    pygame.init()

    SHEET_W, SHEET_H = 880, 780
    sheet = pygame.Surface((SHEET_W, SHEET_H))
    sky_a, sky_b = (150, 176, 210), (110, 142, 184)
    for y in range(SHEET_H):
        t = y / SHEET_H
        c = tuple(int(sky_a[i] + (sky_b[i] - sky_a[i]) * t) for i in range(3))
        pygame.draw.line(sheet, c, (0, y), (SHEET_W, y))

    font = pygame.font.SysFont("dejavusans", 18, bold=True)
    small = pygame.font.SysFont("dejavusans", 13)
    title = pygame.font.SysFont("dejavusans", 22, bold=True)

    def label(text, x, y, col=(20, 24, 30)):
        sheet.blit(font.render(text, True, (250, 252, 248)), (x + 1, y + 1))
        sheet.blit(font.render(text, True, col), (x, y))

    def slabel(text, x, y, col=(24, 28, 34), light=(250, 252, 248)):
        sheet.blit(small.render(text, True, light), (x + 1, y + 1))
        sheet.blit(small.render(text, True, col), (x, y))

    sheet.blit(title.render("RAIJIN — thunder-drum ring demon  (round 2)", True, (250, 252, 248)), (19, 13))
    sheet.blit(title.render("RAIJIN — thunder-drum ring demon  (round 2)", True, (24, 30, 38)), (18, 12))
    sheet.blit(small.render("GREY RECEDES; GOLD+CRIMSON FOCAL  ·  drum-ring HALO crests overhead (sky between head + ring)  ·  chibi storm-god",
                            True, (24, 30, 40)), (18, 38))

    # ---- large creature ----
    big_c, _ = build_raijin_sprite(4.3)
    large_c = pygame.transform.smoothscale(big_c, (big_c.get_width() // SS, big_c.get_height() // SS))
    sheet.blit(large_c, (16, 60))
    label("creature", 110, 62 + large_c.get_height())
    slabel("4 large drums crest ABOVE the head · gold zags radiate from ring · crimson rims read first", 24, 84 + large_c.get_height())

    # ---- large pillar mirror ----
    big_p, _ = build_pillar_sprite(4.2)
    large_p = pygame.transform.smoothscale(big_p, (big_p.get_width() // SS, big_p.get_height() // SS))
    sheet.blit(large_p, (374, 60))
    label("mallet + drum pillar", 346, 62 + large_p.get_height())
    slabel("MODEST front-on cap seated TIGHT on the haft;", 346, 84 + large_p.get_height())
    slabel("crimson rim + gold zag drop INTO gap · 2 calm bands", 346, 100 + large_p.get_height())

    def to_h(big, target_h):
        w, h = big.get_size()
        scale = (target_h * SS) / h
        return pygame.transform.smoothscale(big, (max(1, int(w * scale / SS)), target_h))

    panel_x = 568
    pw = 296
    # DAY panel
    pygame.draw.rect(sheet, (192, 210, 234), (panel_x, 60, pw, 236), border_radius=8)
    pygame.draw.rect(sheet, (44, 56, 72), (panel_x, 60, pw, 236), 2, border_radius=8)
    slabel("on DAY sky — large + 32px", panel_x + 12, 66)
    sheet.blit(to_h(big_c, 110), (panel_x + 12, 92))
    sheet.blit(to_h(big_p, 160), (panel_x + 168, 86))
    slabel("32px", panel_x + 34, 256)
    slabel("32px", panel_x + 210, 256)
    sheet.blit(to_h(big_c, 32), (panel_x + 28, 218))
    sheet.blit(to_h(big_c, 24), (panel_x + 78, 226))
    sheet.blit(to_h(big_p, 56), (panel_x + 204, 214))
    sheet.blit(to_h(big_p, 40), (panel_x + 244, 226))

    # NIGHT panel — dark-blue night biome swatch; grey RECEDES + focal pops
    ny = 312
    nh = 252
    pygame.draw.rect(sheet, (18, 24, 46), (panel_x, ny, pw, nh), border_radius=8)
    pygame.draw.rect(sheet, (60, 78, 120), (panel_x, ny, pw, nh), 2, border_radius=8)
    import random as _r
    rng = _r.Random(99)
    for _ in range(58):
        sx = rng.randint(panel_x + 6, panel_x + pw - 6)
        sy = rng.randint(ny + 26, ny + nh - 6)
        pygame.draw.circle(sheet, (210, 220, 240), (sx, sy), rng.choice((1, 1, 2)))
    slabel("DARK-BLUE NIGHT — grey recedes, gold+crimson pop",
           panel_x + 10, ny + 6, col=(200, 214, 240), light=(8, 12, 28))
    sheet.blit(to_h(big_c, 112), (panel_x + 12, ny + 28))
    sheet.blit(to_h(big_p, 162), (panel_x + 170, ny + 24))
    sheet.blit(to_h(big_c, 32), (panel_x + 168, ny + 196))
    sheet.blit(to_h(big_c, 24), (panel_x + 218, ny + 204))
    slabel("32 / 24px", panel_x + 168, ny + 230, col=(200, 214, 240), light=(8, 12, 28))

    # ---- 32px row on a flat dark-blue strip below the large creature/pillar ----
    strip_y = 60 + max(large_c.get_height(), large_p.get_height()) + 56
    pygame.draw.rect(sheet, (20, 26, 48), (16, strip_y, 528, 100), border_radius=8)
    pygame.draw.rect(sheet, (60, 78, 120), (16, strip_y, 528, 100), 2, border_radius=8)
    slabel("32px read on night biome — drum-ring CIRCLE + zag SHAPE carry the read where grey can't",
           24, strip_y + 6, col=(200, 214, 240), light=(8, 12, 28))
    sheet.blit(to_h(big_c, 38), (44, strip_y + 30))
    sheet.blit(to_h(big_c, 32), (120, strip_y + 36))
    sheet.blit(to_h(big_p, 74), (210, strip_y + 20))
    sheet.blit(to_h(big_p, 50), (280, strip_y + 34))
    sheet.blit(to_h(big_c, 32), (370, strip_y + 36))
    sheet.blit(to_h(big_p, 56), (440, strip_y + 30))

    # ---- palette swatches (bottom strip) ----
    swatches = [("body recedes", BODY), ("shade", BODY_D), ("GOLD focal", GOLD),
                ("CRIMSON focal", CRIMSON), ("cloud", CLOUD), ("drum wood", DRUM_BODY),
                ("sheen", SHEEN)]
    sx = 24
    sy = strip_y + 124
    slabel("pinned palette:", sx, sy - 18)
    for name, col in swatches:
        pygame.draw.rect(sheet, col, (sx, sy, 26, 26), border_radius=4)
        pygame.draw.rect(sheet, (18, 22, 28), (sx, sy, 26, 26), 1, border_radius=4)
        sheet.blit(small.render(name, True, (250, 252, 248)), (sx + 1, sy + 28))
        sheet.blit(small.render(name, True, (22, 26, 32)), (sx, sy + 27))
        sx += small.size(name)[0] + 22

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_2.png")
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
