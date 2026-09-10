"""
Review renderer for KARAKASA — the one-eyed hopping umbrella ghost
(Section 3 Japanese, sole object-spirit / tsukumogami).

House style: chibi, flat saturated fills, hard ink keylines, the
dark-core -> flat-fill -> top-left rim-sheen TRIAD, a 1px outline grown from
the alpha mask, and supersample -> smoothscale. The karakasa is the cleanest
single-object mirror in either batch: the creature IS the prop IS the pillar,
so the same ribbed-canopy + bamboo-shaft language drives both the creature and
its pillar tile.

Round 2 reprofiles the canopy from a low circus-tent dome into a TALL conical
wagasa parasol (taller-than-wide, top finial spike, slightly out-flared
rib-tipped hem, alternating oxblood/cream panels), drops the two splayed
stick-arms to vestigial twig-stubs so the SINGLE central leg+geta carries the
"umbrella-on-one-leg" read, and blows up the lone central eye to the canopy's
dominant focal — so it reads "umbrella ghost," never "tent / mushroom," at 32px.

Standalone headless script: writes round_2.png next to itself. No game imports
so the review sheet stays reproducible in isolation.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import math
import pygame

# ── PINNED PALETTE (exact hexes from the locked Karakasa brief) ─────────────
CANOPY    = (168, 66, 52)     # oxblood-paper canopy base
CANOPY_D  = (110, 40, 34)     # deep-maroon shade (dark core)
SHEEN     = (220, 128, 108)   # top-left rim sheen
SHEEN_HOT = (244, 158, 132)   # hotter sheen so the edge survives on night-blue
RIB       = (204, 168, 96)    # ochre-bamboo ribs accent
RIB_D     = (150, 120, 60)    # rib dark core (derived, same bamboo family)
RIB_RIM   = (228, 200, 140)   # rib sheen (derived)
CREAM     = (232, 216, 182)   # cream oilpaper panel
CREAM_D   = (188, 170, 132)   # cream panel shade (derived)
EYE_WHITE = (244, 240, 230)   # big-eye white (derived warm white)
IRIS      = (244, 196, 72)    # amber iris
IRIS_D    = (188, 142, 40)    # amber iris shade (derived)
TONGUE    = (224, 108, 128)   # tongue-pink
TONGUE_D  = (176, 70, 92)     # tongue dark (derived)
TONGUE_RIM= (244, 158, 174)   # tongue sheen (derived)
INK       = (30, 22, 22)      # keyline ink
GETA      = (150, 108, 64)    # wooden geta clog (bamboo-ochre family)
GETA_D    = (104, 74, 40)
GETA_RIM  = (196, 154, 100)

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


# ── shared canopy primitive: a TALL conical wagasa, not a tent dome ─────────

def _wagasa_outline(half_w, top_y, rim_y):
    """Half-profile control points (right side) of a tall onion-conical wagasa:
    a sharp apex near the finial, a gentle convex onion shoulder, then a slight
    OUTWARD flare at the hem so the rim bells past the shoulder — the classic
    paper-parasol silhouette. Mirrored to build the full closed polygon. The
    profile is taller than wide on purpose so it never reads as a tent dome."""
    h = rim_y - top_y
    # (x as fraction of half_w, y as fraction of canopy height from apex)
    prof = [
        (0.08, 0.00),   # just off the finial apex — narrow, tall start
        (0.28, 0.12),
        (0.54, 0.30),
        (0.78, 0.50),
        (0.92, 0.70),
        (0.99, 0.88),
        (1.00, 0.97),   # widest point near the hem
        (0.97, 1.00),   # slight outward flare lip at the very rim
    ]
    right = [(x * half_w, top_y + y * h) for x, y in prof]
    left = [(-x, y) for x, y in reversed(right)]
    return left + [(0, top_y)] + right


def draw_canopy(surf, P, top_y, half_w, depth, n_ribs=8, accent_panel=True,
                hot_sheen=False):
    """A TALL conical paper-parasol canopy: alternating oxblood/cream wagasa
    panels split by radiating ochre-bamboo ribs, triad-lit, topped by a finial
    spike. `P` maps unit coords to surface px. Apex sits at (0, top_y); it
    bells to `half_w` and the hem drops `depth` below the apex. `depth` is
    larger than `half_w` here so the canopy is taller than wide — the SAME
    shape both the creature canopy and the pillar cap reuse so the mirror reads
    as one object. Returns the hem y."""
    rim_y = top_y + depth
    h = rim_y - top_y

    poly = _wagasa_outline(half_w, top_y, rim_y)

    # dark-core silhouette
    _poly(surf, CANOPY_D, [P(x, y) for x, y in poly])

    # flat OXBLOOD fill is the dominant canopy field (pulled in lower-right so a
    # dark-core rim survives) — oxblood is the hero, cream is only an accent.
    fill = _wagasa_outline(half_w * 0.93, top_y + h * 0.06, top_y + h * 0.985)
    # nudge the fill down-right so the dark core reads on the right + bottom edge
    _poly(surf, CANOPY, [(P(x, y)[0] + 1, P(x, y)[1] + 1) for x, y in fill])

    def rib_x(a):  # x along the cone for a in [-1, 1]
        return a * half_w * 0.97

    def cone_top_y(a):  # where a rib/panel meets near the apex collar
        return top_y + h * 0.10

    # cream wagasa panels on a FEW alternating OUTER wedges only — they give the
    # two-tone candy-stripe + value structure without swamping the oxblood field
    # that the giant eye reads against. Central wedges stay oxblood for the eye.
    for i in range(n_ribs):
        a0 = -1.0 + 2.0 * (i / n_ribs)
        a1 = -1.0 + 2.0 * ((i + 1) / n_ribs)
        mid = (a0 + a1) * 0.5
        if abs(mid) < 0.30:        # keep the central field oxblood for the eye
            continue
        if i % 2 == 1:             # alternate -> candy stripe
            continue
        wedge = [P(0, cone_top_y(mid)),
                 P(rib_x(a0) * 0.94, rim_y - h * 0.04),
                 P(rib_x(a1) * 0.94, rim_y - h * 0.04)]
        _poly(surf, CREAM_D, wedge)
        wedge2 = [P(0, cone_top_y(mid) + h * 0.03),
                  P(rib_x(a0) * 0.88, rim_y - h * 0.07),
                  P(rib_x(a1) * 0.88, rim_y - h * 0.07)]
        _poly(surf, CREAM, wedge2)

    # top-left rim sheen — a bright crescent down the canopy's upper-left cone
    sh = SHEEN_HOT if hot_sheen else SHEEN
    sheen = [P(-half_w * 0.06, top_y + h * 0.08),
             P(-half_w * 0.26, top_y + h * 0.30),
             P(-half_w * 0.52, top_y + h * 0.66),
             P(-half_w * 0.66, top_y + h * 0.92),
             P(-half_w * 0.44, top_y + h * 0.92),
             P(-half_w * 0.32, top_y + h * 0.60),
             P(-half_w * 0.16, top_y + h * 0.30)]
    _poly(surf, sh, sheen)

    # radiating bamboo ribs — thin hairlines from the apex collar to each hem
    # tip (a clear paper-parasol fan, not heavy bars overpowering the panels).
    px_per_unit = P(1, 0)[0] - P(0, 0)[0]
    rib_w = max(1, int(0.8 * px_per_unit))
    for i in range(n_ribs + 1):
        a = -1.0 + 2.0 * (i / n_ribs)
        rx = rib_x(a)
        ry = rim_y - h * 0.03
        ax, ay = P(0, top_y + h * 0.08)
        tx, ty = P(rx, ry)
        pygame.draw.line(surf, RIB_D, (ax, ay), (tx, ty), rib_w)

    # scalloped hem: rib-tip beads on the slightly flared rim (paper fringe)
    for i in range(n_ribs + 1):
        a = -1.0 + 2.0 * (i / n_ribs)
        rx = rib_x(a)
        ry = rim_y - h * 0.03
        _ellipse(surf, RIB_D, *P(rx, ry + 0.6), 1.8 * px_per_unit, 1.3 * px_per_unit)
        _ellipse(surf, RIB, *P(rx, ry + 0.3), 1.3 * px_per_unit, 1.0 * px_per_unit)
        _ellipse(surf, RIB_RIM, *P(rx - 0.4, ry - 0.2), 0.6 * px_per_unit, 0.5 * px_per_unit)

    # ---- top FINIAL spike (ishizuki ferrule) — the wagasa point ----
    fy = top_y
    _poly(surf, RIB_D, [P(-1.7, fy + 0.5), P(0, fy - 7.5), P(1.7, fy + 0.5)])
    _poly(surf, RIB, [P(-1.0, fy + 0.2), P(0, fy - 6.8), P(1.0, fy + 0.2)])
    pygame.draw.line(surf, RIB_RIM, P(-0.5, fy - 0.5), P(-0.2, fy - 5.8),
                     max(1, int(0.9 * (P(1, 0)[0] - P(0, 0)[0]))))
    # collar nub where ribs gather under the finial
    _ellipse(surf, RIB_D, *P(0, fy + 1.0), 2.8 * px_per_unit, 1.8 * px_per_unit)
    _ellipse(surf, RIB, *P(0, fy + 0.6), 2.0 * px_per_unit, 1.3 * px_per_unit)
    return rim_y


def draw_karakasa(surf, ox, oy, s):
    """Draw the one-eyed hopping umbrella ghost centred near (ox, oy). `s` is
    unit scale. Tall vertical wagasa up top, one GIANT eye on the oxblood
    central field, a long lolling+curling tongue below the hem, ONE bare
    central leg + geta clog, and only vestigial twig-stubs where arms used to
    be. The creature IS the prop."""

    def P(x, y):  # local unit coords -> surface px
        return (ox + x * s, oy + y * s)

    def E(color, cx, cy, rx, ry):  # ellipse whose radii are in UNITS, scaled by s
        _ellipse(surf, color, *P(cx, cy), rx * s, ry * s)

    # ---- the single central leg + bamboo shaft down to the geta ----
    # (drawn first so the hem + tongue overlap its top). One spar on-axis is
    # the signature; no tripod of limbs.
    leg_x = 0
    pygame.draw.line(surf, RIB_D, P(leg_x, 7), P(leg_x, 30), max(4, int(4.0 * s)))
    pygame.draw.line(surf, RIB, P(leg_x, 7), P(leg_x, 30), max(2, int(2.4 * s)))
    pygame.draw.line(surf, RIB_RIM, P(leg_x - 0.9, 8), P(leg_x - 0.9, 27), max(1, int(s)))
    # bamboo node bands (matches the pillar banding)
    for ny in (13, 22):
        E(RIB_D, leg_x, ny, 2.8, 1.4)
        pygame.draw.line(surf, RIB_RIM, P(leg_x - 1.4, ny - 0.4), P(leg_x + 1.0, ny - 0.4), max(1, int(s)))

    # ---- geta clog (wooden sandal) at the foot, mid-hop tilt ----
    gx, gy = leg_x, 32
    sole = [(-8, -1), (9, -3), (10, 2), (-7, 3.5)]      # tilted plank
    _poly(surf, GETA_D, [P(gx + x, gy + y + 0.8) for x, y in sole])
    sole2 = [(-7, -1), (8, -3), (8.6, 1.4), (-6, 2.6)]
    _poly(surf, GETA, [P(gx + x, gy + y) for x, y in sole2])
    pygame.draw.line(surf, GETA_RIM, P(gx - 6.5, gy - 1.2), P(gx + 7.5, gy - 2.8), max(1, int(s)))
    # two teeth (ha) under the plank
    for tx in (-4, 5):
        _poly(surf, GETA_D, [P(gx + tx - 1.5, gy + 3), P(gx + tx + 1.5, gy + 2.6),
                             P(gx + tx + 1.6, gy + 6.5), P(gx + tx - 1.4, gy + 6.9)])
    # toe-thong V
    pygame.draw.line(surf, INK, P(gx + 0.5, gy - 2.4), P(gx - 4, gy + 0.6), max(1, int(s)))
    pygame.draw.line(surf, INK, P(gx + 0.5, gy - 2.4), P(gx + 5, gy - 0.4), max(1, int(s)))

    # ---- vestigial twig-arm STUBS (no longer splayed limbs) ----
    # Tiny paper-rib stubs poking from just under the hem — they add a flick of
    # life but never compete with the single-leg silhouette.
    for side in (-1, 1):
        sx0 = P(side * 9, 7)
        sx1 = P(side * 13.5, 8.5 if side < 0 else 5.5)
        pygame.draw.line(surf, CANOPY_D, sx0, sx1, max(2, int(1.8 * s)))
        pygame.draw.line(surf, RIB, sx0, sx1, max(1, int(s)))
        # two short finger-twigs at the tip
        for fa in (-0.4, 0.4):
            fx = sx1[0] + math.cos(-1.0 + fa) * 3.0 * s * side
            fy = sx1[1] + math.sin(-1.0 + fa) * 3.0 * s
            pygame.draw.line(surf, CANOPY_D, sx1, (fx, fy), max(1, int(s)))

    # ---- the TALL conical wagasa canopy (the body) ----
    # depth >> half_w so it is clearly taller than wide.
    rim_y = draw_canopy(surf, P, top_y=-34, half_w=18, depth=34, n_ribs=8)

    # ---- mouth + long lolling, curling tongue below the hem ----
    mcx, mcy = 0, rim_y - 1.0
    E(INK, mcx, mcy + 1.6, 7.5, 3.6)
    E(CANOPY_D, mcx, mcy + 0.6, 7.0, 3.0)
    for txx in range(-5, 6, 3):
        _poly(surf, CREAM, [P(mcx + txx - 1, mcy - 0.4), P(mcx + txx + 1, mcy - 0.4),
                            P(mcx + txx, mcy + 1.6)])
    # tapering ribbon tongue that narrows downward and curls/flaps at the tip —
    # not a rectangular bib. Wide at the mouth, pinches, then a hooked flick.
    tongue = [(-4.2, 0), (-3.4, 8), (-2.2, 16), (-3.6, 22),
              (-1.0, 25.5), (2.2, 23.5), (2.0, 16), (2.6, 8), (4.2, 0)]
    _poly(surf, TONGUE_D, [P(mcx + x, mcy + 2.4 + y + 0.6) for x, y in tongue])
    tongue2 = [(-3.2, 0.4), (-2.6, 8), (-1.6, 15.5), (-2.6, 21),
               (-0.6, 23.8), (1.6, 22), (1.4, 15.5), (1.9, 8), (3.2, 0.6)]
    _poly(surf, TONGUE, [P(mcx + x, mcy + 2.4 + y) for x, y in tongue2])
    # curling flick lobe at the tip
    E(TONGUE, mcx + 1.6, mcy + 25.0, 2.4, 2.0)
    E(TONGUE_RIM, mcx + 0.8, mcy + 24.2, 1.0, 0.9)
    # centre crease + sheen
    pygame.draw.line(surf, TONGUE_D, P(mcx - 0.4, mcy + 4), P(mcx - 0.8, mcy + 22), max(1, int(s)))
    pygame.draw.line(surf, TONGUE_RIM, P(mcx - 2.4, mcy + 4), P(mcx - 2.0, mcy + 17), max(1, int(s)))

    # ---- one GIANT central EYE on the oxblood field (drawn last = focal) ----
    # ~40% of canopy face width, the creature's whole personality. Sits on the
    # central oxblood wedge so the amber pops against the deep red.
    ecx, ecy = 0, -8.5
    er = 6.8
    E(INK, ecx, ecy + 0.3, er + 1.1, er + 1.1)    # ink ring
    E(EYE_WHITE, ecx, ecy, er, er)                # huge sclera
    E(IRIS_D, ecx + 0.4, ecy + 0.9, er * 0.68, er * 0.68)
    E(IRIS, ecx, ecy + 0.5, er * 0.62, er * 0.62)
    E(INK, ecx + 0.4, ecy + 0.8, er * 0.30, er * 0.30)  # pupil
    # light hooded upper-lid crescent — only SKIMS the very top edge so the big
    # round amber read fully survives (round 1's lid buried the whole eye).
    lid = [(-er - 0.6, -er - 0.4), (er + 0.6, -er - 0.4), (er * 0.96, -er * 0.74),
           (0, -er * 0.9), (-er * 0.96, -er * 0.76)]
    _poly(surf, CANOPY_D, [P(ecx + x, ecy + y) for x, y in lid])
    # twin catchlights (top-left, holds the triad light direction)
    E(EYE_WHITE, ecx - 2.2, ecy - 1.8, 1.7, 1.7)
    E(EYE_WHITE, ecx + 2.0, ecy + 2.0, 0.8, 0.8)
    # a couple of oxblood bloodshot flicks for paper-spirit menace
    for va in (2.4, 3.0):
        pygame.draw.line(surf, CANOPY, P(ecx + math.cos(va) * er * 0.6, ecy + math.sin(va) * er * 0.6),
                         P(ecx + math.cos(va) * er * 0.92, ecy + math.sin(va) * er * 0.92), max(1, int(s)))
    # lower lash flicks
    pygame.draw.line(surf, INK, P(ecx - er * 0.86, ecy + er * 0.66), P(ecx - er * 0.36, ecy + er * 0.96), max(1, int(s)))
    pygame.draw.line(surf, INK, P(ecx + er * 0.86, ecy + er * 0.66), P(ecx + er * 0.36, ecy + er * 0.96), max(1, int(s)))


def draw_canopy_pillar(surf, cx, top, bottom, w, cap=True):
    """Prop -> PILLAR mirror: the karakasa's own parasol. The long bamboo
    umbrella-HANDLE is the repeatable rib-banded shaft body; the open TALL
    conical CANOPY blooms at the gap as the detachable gap-edge cap with its
    finial dropping INTO the gap. Creature = prop = pillar — the cleanest
    single-object mirror; canopy is round/symmetric on-axis."""
    half = w // 2
    u = w / 24.0                     # unit so the banding scales with width
    # ---- bamboo handle shaft body ----
    pygame.draw.rect(surf, RIB_D, (cx - half - 2, top, w + 4, bottom - top))
    pygame.draw.rect(surf, RIB, (cx - half, top, w, bottom - top))
    pygame.draw.rect(surf, RIB_RIM, (cx - half + 2, top, max(2, w // 5), bottom - top))
    # node bands (repeatable banding — same language as the leg-shaft)
    seg_h = w * 1.7
    y = top + seg_h
    while y < bottom:
        pygame.draw.rect(surf, RIB_D, (cx - half - 3, int(y) - 3, w + 6, 6))
        pygame.draw.line(surf, RIB_RIM, (cx - half + 2, int(y) - 3), (cx - half + 2, int(y) + 3), 2)
        y += seg_h

    if cap:
        # gap-edge cap: the open TALL conical parasol blooming at the gap.
        # Reuse the creature's canopy primitive so the mirror is literal; the
        # finial spike points up into the gap as the bloom detail.
        def P(x, yy):
            return (cx + x * u, top + yy * u)
        draw_canopy(surf, P, top_y=-40, half_w=half / u + 6, depth=40, n_ribs=10)


def build_karakasa_sprite(unit_px):
    """Render the karakasa at unit_px supersampled, outline from its alpha
    mask, return the high-res surface (caller smoothscales)."""
    W = int(50 * unit_px)
    H = int(86 * unit_px)
    big = pygame.Surface((W * SS, H * SS), pygame.SRCALPHA)
    # centre: canopy near top, tongue + leg + geta trailing below
    draw_karakasa(big, big.get_width() // 2, int(H * SS * 0.50), unit_px * SS)
    big = grow_outline(big, INK, SS)   # 1px @ final scale
    return big, (W, H)


def build_pillar_sprite(unit_px):
    W = int(46 * unit_px)
    H = int(104 * unit_px)
    big = pygame.Surface((W * SS, H * SS), pygame.SRCALPHA)
    draw_canopy_pillar(big, big.get_width() // 2,
                       int(42 * unit_px * SS), big.get_height(),
                       int(13 * unit_px * SS), cap=True)
    big = grow_outline(big, INK, SS)
    return big, (W, H)


def main():
    pygame.init()

    SHEET_W, SHEET_H = 780, 580
    sheet = pygame.Surface((SHEET_W, SHEET_H))
    sky_a, sky_b = (190, 168, 158), (150, 120, 116)   # warm dusk so oxblood reads honest
    for y in range(SHEET_H):
        t = y / SHEET_H
        c = tuple(int(sky_a[i] + (sky_b[i] - sky_a[i]) * t) for i in range(3))
        pygame.draw.line(sheet, c, (0, y), (SHEET_W, y))

    font = pygame.font.SysFont("dejavusans", 18, bold=True)
    small = pygame.font.SysFont("dejavusans", 13)

    def label(text, x, y, col=(28, 20, 20)):
        sheet.blit(font.render(text, True, (250, 246, 240)), (x + 1, y + 1))
        sheet.blit(font.render(text, True, col), (x, y))

    def slabel(text, x, y):
        sheet.blit(small.render(text, True, (250, 246, 240)), (x + 1, y + 1))
        sheet.blit(small.render(text, True, (30, 22, 22)), (x, y))

    title = pygame.font.SysFont("dejavusans", 22, bold=True)
    sheet.blit(title.render("KARAKASA — one-eyed hopping umbrella ghost  · round 2", True, (250, 246, 240)), (19, 13))
    sheet.blit(title.render("KARAKASA — one-eyed hopping umbrella ghost  · round 2", True, (40, 24, 22)), (18, 12))
    sheet.blit(small.render("tall conical wagasa · ONE central leg+geta · giant single eye · alternating oxblood/cream panels",
                            True, (40, 26, 24)), (18, 38))

    # ---- large creature ----
    big_c, _ = build_karakasa_sprite(5.0)
    large_c = pygame.transform.smoothscale(big_c, (big_c.get_width() // SS, big_c.get_height() // SS))
    sheet.blit(large_c, (20, 64))
    label("creature", 70, 60 + large_c.get_height())

    # ---- large pillar mirror ----
    big_p, _ = build_pillar_sprite(4.4)
    large_p = pygame.transform.smoothscale(big_p, (big_p.get_width() // SS, big_p.get_height() // SS))
    sheet.blit(large_p, (300, 58))
    label("parasol pillar", 286, 60 + large_p.get_height())
    slabel("tall canopy-cap blooms into gap (finial points in) · rib-banded handle repeats", 270, 80 + large_p.get_height())

    # ---- scale strip: creature + pillar on light & dark panels ----
    def to_h(big, target_h):
        w, h = big.get_size()
        scale = (target_h * SS) / h
        return pygame.transform.smoothscale(big, (max(1, int(w * scale / SS)), target_h))

    panel_x = 560
    pygame.draw.rect(sheet, (240, 232, 222), (panel_x, 64, 204, 224), border_radius=8)
    pygame.draw.rect(sheet, (60, 40, 38), (panel_x, 64, 204, 224), 2, border_radius=8)
    pygame.draw.rect(sheet, (26, 30, 50), (panel_x, 304, 204, 214), border_radius=8)
    pygame.draw.rect(sheet, (90, 96, 124), (panel_x, 304, 204, 214), 2, border_radius=8)

    slabel("32px on dusk sky", panel_x + 10, 70)
    sheet.blit(to_h(big_c, 36), (panel_x + 22, 100))
    sheet.blit(to_h(big_p, 76), (panel_x + 120, 96))
    slabel("48px detail", panel_x + 10, 202)
    c48 = pygame.transform.smoothscale(big_c, (int(big_c.get_width() / SS * 0.58),
                                               int(big_c.get_height() / SS * 0.58)))
    sheet.blit(c48, (panel_x + 14, 150))

    slabel("32px on night sky", panel_x + 10, 310)
    sheet.blit(to_h(big_c, 36), (panel_x + 22, 340))
    sheet.blit(to_h(big_p, 76), (panel_x + 120, 336))
    slabel("24px silhouette", panel_x + 10, 442)
    sheet.blit(to_h(big_c, 24), (panel_x + 34, 466))
    sheet.blit(to_h(big_p, 52), (panel_x + 132, 460))

    # palette swatches
    swatches = [("canopy", CANOPY), ("shade", CANOPY_D), ("rib", RIB),
                ("cream", CREAM), ("amber", IRIS), ("tongue", TONGUE), ("sheen", SHEEN)]
    sx = 24
    sy = 526
    slabel("pinned palette:", sx, sy - 18)
    for name, col in swatches:
        pygame.draw.rect(sheet, col, (sx, sy, 30, 30), border_radius=4)
        pygame.draw.rect(sheet, (28, 20, 20), (sx, sy, 30, 30), 1, border_radius=4)
        sheet.blit(small.render(name, True, (250, 246, 240)), (sx + 1, sy + 31))
        sheet.blit(small.render(name, True, (30, 22, 22)), (sx, sy + 30))
        sx += 68

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_2.png")
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
