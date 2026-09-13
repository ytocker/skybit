"""
Pazul — the scorpion-tailed plague-wind demon (Batch 2, Section 1 Devilish).
Pazuzu cuted to a pocket gremlin: lion-dog snarl head, double-deck stubby
wings (turquoise membranes pinned PROMINENT as the cool counterweight to the
ochre hide), and a fat scorpion sting arcing UP over the head.

House style this renderer obeys: chibi proportions, FLAT saturated fills with
hard ink keylines, form via the dark-core -> flat-fill -> top-left rim-sheen
TRIAD, silhouette POP via a 1px outline grown from the alpha mask, and a
supersample -> smoothscale pipeline. Standalone (no game imports) so the
review sheet renders headless without touching live draw paths.
"""
import math
import pygame

# --- PINNED PALETTE (exact hexes from the locked Pazul brief) ---------------
OCHRE      = (206, 158, 84)    # desert-ochre hide base
TAN_D      = (150, 104, 52)    # burnt-tan shade (dark-core of the triad)
TURQUOISE  = (64, 176, 168)    # wing-membrane PROMINENT accent (cool counter)
TURQ_D     = (38, 118, 116)    # derived darker turquoise for membrane cores
VENOM      = (176, 224, 72)    # venom-lime sting-glow
EYE        = (244, 196, 64)    # amber slit-eye
INK        = (30, 22, 20)      # hard keyline
SHEEN      = (244, 214, 150)   # top-left rim sheen

# day / night biome sky stops (matches the game's interp feel)
SKY_DAY    = ((150, 205, 235), (208, 236, 246))
SKY_NIGHT  = ((20, 26, 58), (44, 40, 86))

SS = 4  # supersample factor


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def shade(col, k):
    """Darken/lighten toward ink or white; k<1 darkens, k>1 lightens."""
    if k < 1:
        return lerp(col, INK, 1 - k)
    return lerp(col, (255, 255, 255), min(1.0, k - 1))


# --- alpha-mask outline grow (the house silhouette-POP step) ----------------
def grow_outline(surf, color=INK, px=1):
    """Grow a 1px keyline from the alpha mask so the silhouette reads clean."""
    mask = pygame.mask.from_surface(surf)
    outline = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pts = mask.outline()
    if len(pts) > 2:
        pygame.draw.polygon(outline, color, pts, max(1, px * 2))
    base = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    base.blit(outline, (0, 0))
    base.blit(surf, (0, 0))
    return base


def make_glow(radius, color, alpha_center=150, falloff=1.9):
    size = radius * 2 + 2
    g = pygame.Surface((size, size), pygame.SRCALPHA)
    cx = cy = size // 2
    for r in range(radius, 0, -1):
        t = r / radius
        a = int(alpha_center * (1 - t) ** falloff)
        pygame.draw.circle(g, (*color, a), (cx, cy), r)
    return g


# --- triad-lit primitive: dark-core wash, flat fill, top-left sheen ----------
def triad_poly(surf, pts, base, core_k=0.62, sheen_k=1.0, sheen_pts=None):
    """Flat-fill a polygon, then lay a dark-core wash and a top-left sheen so
    the form reads with no soft gradient — just the three stacked flats."""
    pygame.draw.polygon(surf, base, pts)
    # dark-core: a shrunk copy pulled toward the lower-right, darker
    cx = sum(p[0] for p in pts) / len(pts)
    cy = sum(p[1] for p in pts) / len(pts)
    core = [(cx + (p[0] - cx) * 0.78 + 2 * SS, cy + (p[1] - cy) * 0.78 + 2 * SS)
            for p in pts]
    pygame.draw.polygon(surf, shade(base, core_k), core)
    pygame.draw.polygon(surf, base, [
        (cx + (p[0] - cx) * 0.62, cy + (p[1] - cy) * 0.62) for p in pts])
    if sheen_pts:
        pygame.draw.polygon(surf, shade(base, sheen_k), sheen_pts)


# ============================================================================
# CREATURE  — drawn at SS scale into a big surface, outlined, then downscaled.
# ============================================================================
def build_creature():
    W, H = 180 * SS, 196 * SS
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    cx = W // 2

    def P(*pairs):
        return [(int(x * SS), int(y * SS)) for x, y in pairs]

    # ---- DOUBLE-DECK WINGS (turquoise membranes — the two LARGEST masses) --
    # Drawn FIRST (deepest layer) and fanning wide so the cool turquoise reads
    # as the dominant non-body mass against the warm ochre hide, per the pin.
    def wing(side, top_y, span, drop, deck):
        d = side  # +1 right, -1 left
        ax, ay = cx + d * 24 * SS, top_y  # shoulder anchor
        base = TURQUOISE if deck == 0 else lerp(TURQUOISE, TURQ_D, 0.22)
        # outer membrane lobe (the big sweeping mass, scalloped trailing edge)
        outer = [
            (ax, ay - 4 * SS),
            (ax + d * span, ay - 14 * SS),
            (ax + d * (span * 1.02), ay + drop * 0.34),
            (ax + d * (span * 0.74), ay + drop * 0.62),
            (ax + d * (span * 0.82), ay + drop * 0.86),
            (ax + d * (span * 0.5), ay + drop),
            (ax + d * (span * 0.56), ay + drop * 1.18),
            (ax + d * 22 * SS, ay + drop * 0.9),
        ]
        pygame.draw.polygon(s, base, outer)
        # dark-core wash toward the membrane interior
        core = [
            (ax + d * 16 * SS, ay + 2 * SS),
            (ax + d * (span * 0.84), ay - 4 * SS),
            (ax + d * (span * 0.74), ay + drop * 0.5),
            (ax + d * (span * 0.42), ay + drop * 0.86),
            (ax + d * 22 * SS, ay + drop * 0.7),
        ]
        pygame.draw.polygon(s, TURQ_D, core)
        # faceted membrane ribs (hard flat splits, not gradient)
        for f in (0.34, 0.6, 0.84):
            rx = ax + d * span * f
            ry = ay - 10 * SS + drop * (0.9 + f * 0.25)
            pygame.draw.line(s, TURQ_D, (ax + d * 14 * SS, ay - 1 * SS),
                             (rx, ry), 3 * SS)
        # top-left rim sheen along the leading edge (the triad sheen)
        pygame.draw.polygon(s, lerp(TURQUOISE, SHEEN, 0.5), [
            (ax, ay - 4 * SS),
            (ax + d * span, ay - 14 * SS),
            (ax + d * (span * 0.9), ay - 7 * SS),
            (ax + d * 14 * SS, ay - 1 * SS),
        ])
        # bone finger spars at lobe tips (ochre claws define the deck)
        for f, fy in ((1.02, 0.34), (0.82, 0.86), (0.56, 1.18)):
            pygame.draw.line(s, TAN_D, (ax, ay - 2 * SS),
                             (ax + d * span * f, ay - 14 * SS + drop * fy + 14 * SS),
                             3 * SS)

    # upper deck (largest), then lower deck spread below it — both prominent
    wing(+1, 84 * SS, 60 * SS, 46 * SS, deck=0)
    wing(-1, 84 * SS, 60 * SS, 46 * SS, deck=0)
    wing(+1, 112 * SS, 46 * SS, 36 * SS, deck=1)
    wing(-1, 112 * SS, 46 * SS, 36 * SS, deck=1)

    # ---- SCORPION STING arcing UP & forward over the head (the signature) --
    # venom outer glow behind the bulb so the lime read survives at small size
    glow = make_glow(30 * SS, VENOM, alpha_center=140, falloff=1.6)
    s.blit(glow, (cx + 2 * SS - glow.get_width() // 2,
                  34 * SS - glow.get_height() // 2),
           special_flags=pygame.BLEND_RGBA_ADD)

    # the tail is a thick chitin TUBE following an arc: from the hip up the
    # right side, then hooking left over the head. Drawn as a fat stroked
    # polyline (dark-core under-stroke, ochre fill, sheen over-stroke) so it
    # reads as one bold continuous blob, then segment rings stamped on top.
    arc = [
        (118, 150), (132, 126), (137, 98), (130, 70),
        (112, 50), (88, 40), (66, 42),
    ]
    apx = [(x * SS, y * SS) for x, y in arc]
    # under-stroke (dark core + the grown outline will hug this)
    pygame.draw.lines(s, shade(OCHRE, 0.55), False, apx, 24 * SS)
    for (x, y) in apx:
        pygame.draw.circle(s, shade(OCHRE, 0.55), (x, y), 12 * SS)
    # mid fill
    pygame.draw.lines(s, OCHRE, False, apx, 18 * SS)
    for (x, y) in apx:
        pygame.draw.circle(s, OCHRE, (x, y), 9 * SS)
    # top-left sheen stripe riding the upper edge of the tube
    sheen_pts = [(x - 3 * SS, y - 4 * SS) for x, y in apx]
    pygame.draw.lines(s, SHEEN, False, sheen_pts, 4 * SS)
    # segment drum rings across the tube
    for i in range(len(apx) - 1):
        mx = (apx[i][0] + apx[i + 1][0]) // 2
        my = (apx[i][1] + apx[i + 1][1]) // 2
        pygame.draw.circle(s, TAN_D, (mx, my), 10 * SS, 3 * SS)

    # fat venom bulb sting tip hooking over the head
    tip = (62, 44)
    tcx, tcy = tip[0] * SS, tip[1] * SS
    pygame.draw.circle(s, lerp(OCHRE, TAN_D, 0.18), (tcx, tcy), 15 * SS)
    pygame.draw.circle(s, shade(OCHRE, 0.6), (tcx + 3 * SS, tcy + 3 * SS), 10 * SS)
    pygame.draw.circle(s, OCHRE, (tcx, tcy), 9 * SS)
    pygame.draw.circle(s, SHEEN, (tcx - 5 * SS, tcy - 5 * SS), 4 * SS)
    # the venom barb point + lime drip aiming down-forward toward the snarl
    pygame.draw.polygon(s, VENOM, P((58, 56), (50, 70), (66, 60)))
    pygame.draw.circle(s, VENOM, (50 * SS, 72 * SS), 4 * SS)
    pygame.draw.circle(s, lerp(VENOM, SHEEN, 0.4), (48 * SS, 70 * SS), 2 * SS)

    # ---- STUMPY RIB-TORSO ---------------------------------------------------
    triad_poly(s, P((cx / SS - 24, 116), (cx / SS + 24, 116),
                    (cx / SS + 20, 162), (cx / SS - 20, 162)),
               OCHRE,
               sheen_pts=P((cx / SS - 22, 118), (cx / SS - 6, 118),
                           (cx / SS - 10, 154), (cx / SS - 22, 150)))
    # rib bands (triad-lit grooves)
    for ry in (108, 118, 128):
        pygame.draw.line(s, TAN_D, ((cx / SS - 16) * SS, ry * SS),
                         ((cx / SS + 16) * SS, ry * SS), 2 * SS)

    # ---- FOUR LITTLE BIRD-CLAW LIMBS ---------------------------------------
    def claw(x, y, d):
        triad_poly(s, P((x, y), (x + d * 8, y + 2), (x + d * 6, y + 16), (x - d * 1, y + 14)),
                   OCHRE)
        for t in (-3, 0, 3):
            pygame.draw.line(s, TAN_D, ((x + d * 4) * SS, (y + 14) * SS),
                             ((x + d * 4 + t) * SS, (y + 22) * SS), 2 * SS)
    claw(cx / SS - 16, 132, -1)
    claw(cx / SS + 16, 132, +1)
    # tiny upper arm-claws gripping forward
    claw(cx / SS - 24, 104, -1)
    claw(cx / SS + 24, 104, +1)

    # ---- BLOCKY CANINE-LION HEAD with square open snarl --------------------
    hy = 70  # head center y
    triad_poly(s, P((cx / SS - 26, hy - 22), (cx / SS + 26, hy - 22),
                    (cx / SS + 28, hy + 10), (cx / SS + 16, hy + 24),
                    (cx / SS - 16, hy + 24), (cx / SS - 28, hy + 10)),
               OCHRE,
               sheen_pts=P((cx / SS - 24, hy - 20), (cx / SS - 4, hy - 20),
                           (cx / SS - 10, hy + 8), (cx / SS - 24, hy + 4)))
    # square muzzle pushed forward-down
    triad_poly(s, P((cx / SS - 14, hy + 6), (cx / SS + 14, hy + 6),
                    (cx / SS + 12, hy + 28), (cx / SS - 12, hy + 28)),
               OCHRE)
    # open square snarl (dark cavity)
    pygame.draw.polygon(s, shade(TAN_D, 0.5), P(
        (cx / SS - 9, hy + 14), (cx / SS + 9, hy + 14),
        (cx / SS + 8, hy + 26), (cx / SS - 8, hy + 26)))
    # tiny up-fangs
    for fx in (-7, -3, 3, 7):
        pygame.draw.polygon(s, SHEEN, P(
            (cx / SS + fx - 1.5, hy + 26), (cx / SS + fx + 1.5, hy + 26),
            (cx / SS + fx, hy + 19)))
    # snarl wrinkle ridges
    pygame.draw.line(s, TAN_D, ((cx / SS - 12) * SS, (hy + 8) * SS),
                     ((cx / SS - 4) * SS, (hy + 4) * SS), 2 * SS)
    pygame.draw.line(s, TAN_D, ((cx / SS + 12) * SS, (hy + 8) * SS),
                     ((cx / SS + 4) * SS, (hy + 4) * SS), 2 * SS)
    # snout-frill ears (small canine ears swept back)
    triad_poly(s, P((cx / SS - 26, hy - 20), (cx / SS - 34, hy - 30), (cx / SS - 20, hy - 24)), TAN_D)
    triad_poly(s, P((cx / SS + 26, hy - 20), (cx / SS + 34, hy - 30), (cx / SS + 20, hy - 24)), TAN_D)

    # ---- AMBER SLIT-EYES with venom glint ----------------------------------
    for ex in (-11, 11):
        ecx = (cx / SS + ex) * SS
        ecy = (hy - 6) * SS
        pygame.draw.polygon(s, INK, [
            (ecx - 7 * SS, ecy + 4 * SS), (ecx + 7 * SS, ecy - 1 * SS),
            (ecx + 6 * SS, ecy + 4 * SS), (ecx - 6 * SS, ecy + 7 * SS)])
        pygame.draw.polygon(s, EYE, [
            (ecx - 5 * SS, ecy + 4 * SS), (ecx + 5 * SS, ecy + 0 * SS),
            (ecx + 4 * SS, ecy + 3 * SS), (ecx - 4 * SS, ecy + 6 * SS)])
        # vertical reptile slit
        pygame.draw.line(s, INK, (ecx, ecy - 1 * SS), (ecx, ecy + 6 * SS), 2 * SS)
        pygame.draw.circle(s, SHEEN, (int(ecx - 2 * SS), int(ecy)), 1 * SS)
    # brow ridge
    pygame.draw.line(s, TAN_D, ((cx / SS - 16) * SS, (hy - 12) * SS),
                     ((cx / SS + 16) * SS, (hy - 12) * SS), 2 * SS)

    out = grow_outline(s, INK, px=1 * SS)
    return out


# ============================================================================
# PROP -> PILLAR  : scorpion STING-SPEAR (segmented chitin shaft + venom cap)
# ============================================================================
def build_pillar_segment(width_px, height_px):
    """A repeatable segmented-chitin shaft tile at SS scale."""
    W, H = width_px * SS, height_px * SS
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    cx = W // 2
    half = int(W * 0.36)
    # shaft body
    pygame.draw.rect(s, OCHRE, (cx - half, 0, half * 2, H))
    pygame.draw.rect(s, shade(OCHRE, 0.6), (cx, 0, half, H))
    pygame.draw.rect(s, OCHRE, (cx - half, 0, half, H))
    # top-left sheen stripe
    pygame.draw.rect(s, SHEEN, (cx - half, 0, int(half * 0.4), H))
    # segment banding (chitin drum rings)
    seg_h = 18 * SS
    y = 0
    while y < H:
        pygame.draw.line(s, TAN_D, (cx - half, y), (cx + half, y), 3 * SS)
        pygame.draw.line(s, shade(OCHRE, 0.5), (cx - half, y + 3 * SS),
                         (cx + half, y + 3 * SS), 1 * SS)
        y += seg_h
    return grow_outline(s, INK, px=1 * SS)


def build_pillar_cap(width_px, height_px):
    """Hooked venom-bulb sting cap dripping a green venom bead (gap-edge)."""
    W, H = width_px * SS, height_px * SS
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    cx = W // 2
    half = int(W * 0.36)

    def P(*pairs):
        return [(int(x), int(y)) for x, y in pairs]

    # venom glow under the bulb (additive)
    glow = make_glow(int(W * 0.5), VENOM, alpha_center=130, falloff=1.7)
    s.blit(glow, (cx - glow.get_width() // 2, int(H * 0.5) - glow.get_height() // 2),
           special_flags=pygame.BLEND_RGBA_ADD)

    # shaft stub at top
    pygame.draw.rect(s, OCHRE, (cx - half, 0, half * 2, int(H * 0.28)))
    pygame.draw.rect(s, shade(OCHRE, 0.6), (cx, 0, half, int(H * 0.28)))
    pygame.draw.rect(s, SHEEN, (cx - half, 0, int(half * 0.4), int(H * 0.28)))

    # fat venom bulb
    by = int(H * 0.46)
    br = int(W * 0.34)
    pygame.draw.circle(s, lerp(OCHRE, TAN_D, 0.2), (cx, by), br)
    pygame.draw.circle(s, shade(OCHRE, 0.6), (cx + 3 * SS, by + 3 * SS), int(br * 0.72))
    pygame.draw.circle(s, OCHRE, (cx, by), int(br * 0.6))
    pygame.draw.circle(s, SHEEN, (cx - int(br * 0.4), by - int(br * 0.4)), int(br * 0.28))

    # hooked barb point down into the gap
    pygame.draw.polygon(s, OCHRE, P(
        (cx - br * 0.5, by + br * 0.6), (cx + br * 0.5, by + br * 0.6),
        (cx + 2 * SS, H - 6 * SS)))
    pygame.draw.polygon(s, TAN_D, P(
        (cx, by + br * 0.6), (cx + br * 0.5, by + br * 0.6), (cx + 2 * SS, H - 6 * SS)))
    # venom drip bead at the very tip (into the gap)
    pygame.draw.circle(s, VENOM, (cx + 2 * SS, H - 5 * SS), 4 * SS)
    pygame.draw.circle(s, lerp(VENOM, SHEEN, 0.4), (cx, H - 7 * SS), 2 * SS)
    return grow_outline(s, INK, px=1 * SS)


# ============================================================================
# SHEET ASSEMBLY
# ============================================================================
def down(surf, scale):
    w = int(surf.get_width() / SS * scale)
    h = int(surf.get_height() / SS * scale)
    return pygame.transform.smoothscale(surf, (w, h))


def vgrad(w, h, top, bot):
    g = pygame.Surface((w, h))
    for y in range(h):
        pygame.draw.line(g, lerp(top, bot, y / h), (0, y), (w, y))
    return g


def main():
    pygame.init()
    font_big = pygame.font.SysFont("dejavusans", 19, bold=True)
    font = pygame.font.SysFont("dejavusans", 13)
    font_sm = pygame.font.SysFont("dejavusans", 11)

    SW, SH = 1180, 760
    sheet = pygame.Surface((SW, SH))
    sheet.fill((40, 40, 48))

    def label(txt, x, y, f=font, col=(235, 235, 240)):
        sheet.blit(f.render(txt, True, col), (x, y))

    label("PAZUL  —  scorpion-tailed plague-wind demon  —  round 1", 16, 12, font_big)
    label("TURQUOISE wings PROMINENT (two largest masses) as the cool counterweight to desert-ochre; over-the-head scorpion sting = the signature blob",
          16, 36, font_sm, (200, 200, 210))

    creature = build_creature()

    # ---- Panel A: BOSS showcase ----
    pax, pay, paw, pah = 12, 56, 380, 690
    pygame.draw.rect(sheet, (28, 28, 34), (pax, pay, paw, pah), border_radius=8)
    label("(a) BOSS  showcase scale", pax + 12, pay + 8, font)
    big = down(creature, 4.2)
    sheet.blit(big, (pax + paw // 2 - big.get_width() // 2, pay + 60))

    # ---- Panel B: PROP -> PILLAR at obstacle scale ----
    pbx = pax + paw + 12
    pbw = 380
    pygame.draw.rect(sheet, (110, 175, 225), (pbx, pay, pbw, pah), border_radius=8)
    label("(b) PROP -> PILLAR  @ obstacle scale", pbx + 12, pay + 8, font, (20, 30, 50))
    # build a real pillar: top cap (mirrored down) + shaft + bottom cap mirrored
    seg = build_pillar_segment(60, 200)
    cap = build_pillar_cap(60, 90)
    pscale = 1.0
    seg_d = down(seg, pscale)
    cap_d = down(cap, pscale)
    px = pbx + 110
    # top pillar: shaft from top, cap pointing DOWN into gap
    gap_top = pay + 250
    sheet.blit(seg_d, (px, pay + 50))
    # tile a second shaft segment to show repeatability
    sheet.blit(seg_d, (px, pay + 50 + seg_d.get_height() - 4))
    sheet.blit(cap_d, (px, gap_top))
    # bottom pillar: mirrored cap pointing UP, shaft below
    cap_up = pygame.transform.flip(cap_d, False, True)
    gap_bot = gap_top + cap_d.get_height() + 120
    sheet.blit(cap_up, (px, gap_bot))
    sheet.blit(seg_d, (px, gap_bot + cap_up.get_height() - 4))
    label("segmented chitin shaft = repeatable body", pbx + 12, pay + 470, font_sm, (20, 30, 50))
    label("hooked venom-bulb = gap-edge cap;", pbx + 12, pay + 488, font_sm, (20, 30, 50))
    label("lime venom bead drips INTO the gap.", pbx + 12, pay + 506, font_sm, (20, 30, 50))
    label("slim symmetric column -> clean top<->bottom mirror.", pbx + 12, pay + 524, font_sm, (20, 30, 50))

    # ---- Panel C: 1x in-game scale day/night + grayscale ----
    pcx = pbx + pbw + 12
    pcw = SW - pcx - 12
    pygame.draw.rect(sheet, (28, 28, 34), (pcx, pay, pcw, pah), border_radius=8)
    label("(c) in-game scale  —  day / night + 32px + grayscale", pcx + 12, pay + 8, font)

    small = down(creature, 1.45)   # ~ in-game obstacle scale
    tiny = down(creature, 0.30)    # 32px-class read

    # day tile
    tw = (pcw - 36) // 2
    th = 200
    tx, ty = pcx + 12, pay + 40
    day = vgrad(tw, th, *SKY_DAY)
    day.blit(small, (tw // 2 - small.get_width() // 2, th - small.get_height() - 6))
    sheet.blit(day, (tx, ty))
    label("DAY", tx + 6, ty + 4, font_sm, (20, 30, 50))
    # night tile
    nx = tx + tw + 12
    night = vgrad(tw, th, *SKY_NIGHT)
    night.blit(small, (tw // 2 - small.get_width() // 2, th - small.get_height() - 6))
    sheet.blit(night, (nx, ty))
    label("NIGHT", nx + 6, ty + 4, font_sm, (235, 235, 240))

    # 32px strip
    sy = ty + th + 20
    label("32px read  (creature / sting-cap)", pcx + 12, sy, font_sm, (215, 215, 225))
    strip = pygame.Surface((pcw - 24, 70))
    strip.fill((60, 60, 70))
    strip.blit(tiny, (16, 35 - tiny.get_height() // 2))
    cap_tiny = down(cap, 0.30)
    strip.blit(cap_tiny, (16 + tiny.get_width() + 30, 35 - cap_tiny.get_height() // 2))
    # 2x zoom of the 32px so reviewers can judge the read
    tiny2 = pygame.transform.scale(tiny, (tiny.get_width() * 2, tiny.get_height() * 2))
    strip.blit(tiny2, (strip.get_width() - tiny2.get_width() - 16, 35 - tiny2.get_height() // 2))
    sheet.blit(strip, (pcx + 12, sy + 18))

    # grayscale shape-tell check
    gy = sy + 110
    label("grayscale  —  silhouette / value tell", pcx + 12, gy, font_sm, (215, 215, 225))
    gpanel = pygame.Surface((pcw - 24, 220))
    gpanel.fill((150, 150, 155))
    gray = down(creature, 1.15)
    arr = pygame.surfarray.pixels3d(gray.copy())
    gs = gray.copy()
    px3 = pygame.surfarray.pixels3d(gs)
    al = pygame.surfarray.pixels_alpha(gs)
    lum = (0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 2]).astype('uint8')
    px3[:, :, 0] = lum
    px3[:, :, 1] = lum
    px3[:, :, 2] = lum
    del px3, al, arr
    gpanel.blit(gs, (gpanel.get_width() // 2 - gs.get_width() // 2, 6))
    sheet.blit(gpanel, (pcx + 12, gy + 18))

    pygame.image.save(sheet, "/home/user/skybit/docs/skybit_devil/batch2/pazul/round_1.png")
    print("saved round_1.png")


if __name__ == "__main__":
    import os
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    os.environ["SDL_AUDIODRIVER"] = "dummy"
    main()
