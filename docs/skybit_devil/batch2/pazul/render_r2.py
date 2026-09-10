"""
Pazul — the scorpion-tailed plague-wind demon (Batch 2, Section 1 Devilish).
ROUND 2 renderer.

Pazuzu cuted to a pocket gremlin: lion-dog snarl head, DOUBLE-DECK wings
(turquoise membranes pinned PROMINENT — the two LARGEST non-body masses,
framing the ochre body left & right), and a fat scorpion sting arcing UP
over the head.

Why this round changes the wings so drastically: the AD critique flagged the
single hardest pin on the brief as failing — turquoise wings read as ragged
low-mass slivers BEHIND the torso. So here each wing is rebuilt as ONE bold
faceted flat panel with a single clean keyline and a small number of internal
vanes (no feathered fringe), the four panels brought FORWARD of the shoulder
line and enlarged so together they rival/exceed the torso area, with a clear
upper(large)/lower(small) deck step so the double-deck read survives at 32px.

House style obeyed: chibi proportions, FLAT saturated fills with hard ink
keylines, form via dark-core -> flat-fill -> top-left rim-sheen TRIAD,
silhouette POP via a 1px outline grown from the alpha mask, supersample ->
smoothscale. Standalone (no game imports) so it renders headless without
touching live draw paths.
"""
import math
import pygame

# --- PINNED PALETTE (exact hexes from the locked Pazul brief) ---------------
OCHRE      = (206, 158, 84)    # desert-ochre hide base
TAN_D      = (150, 104, 52)    # burnt-tan shade (dark-core of the triad)
TURQUOISE  = (64, 176, 168)    # wing-membrane PROMINENT accent (cool counter)
TURQ_D     = (32, 104, 104)    # derived darker turquoise for membrane cores
TURQ_SHEEN = (150, 224, 214)   # cool sheen for the wing leading edge
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
# WING  — one bold faceted turquoise panel. The make-or-break mass.
# ============================================================================
def draw_wing(s, cx, anchor_x, anchor_y, span, height, deck, side):
    """One wing membrane as a SINGLE bold faceted flat panel.

    deck 0 = upper (large), deck 1 = lower (small). `side` is +1 right / -1
    left. The panel is a broad bat-membrane bracket: a long leading edge up &
    out from the shoulder, a wide membrane body, and exactly three blunt
    scallops on the trailing edge (no feathered fringe). Internal vanes are
    limited to 2 hard struts so the turquoise never breaks into noise at 1x.
    """
    d = side
    ax, ay = anchor_x, anchor_y
    # tip of the leading edge, thrust up & outward
    tip_x = ax + d * span
    tip_y = ay - height * 0.55
    # three blunt trailing scallops, sized to read as one bold edge at 1x.
    # The trailing edge bows OUTWARD (away from the body) so the membrane mass
    # sits beside the torso, not tucked behind it — this is what makes the
    # turquoise the dominant flanking mass per the pin.
    sc = height
    membrane = [
        (ax, ay - sc * 0.12),                       # shoulder root (top)
        (tip_x, tip_y),                             # leading tip (up & out)
        (ax + d * span * 1.04, ay + sc * 0.24),     # outer shoulder of edge
        (ax + d * span * 0.90, ay + sc * 0.38),     # scallop 1 notch
        (ax + d * span * 1.02, ay + sc * 0.56),     # scallop 1 lobe (bows out)
        (ax + d * span * 0.84, ay + sc * 0.70),     # scallop 2 notch
        (ax + d * span * 0.96, ay + sc * 0.90),     # scallop 2 lobe (bows out)
        (ax + d * span * 0.74, ay + sc * 1.00),     # scallop 3 notch
        (ax + d * span * 0.84, ay + sc * 1.20),     # scallop 3 lobe (bows out)
        (ax + d * span * 0.40, ay + sc * 1.10),     # inner trailing
        (ax + d * span * 0.06, ay + sc * 0.52),     # root (bottom)
    ]
    base = TURQUOISE if deck == 0 else lerp(TURQUOISE, TURQ_D, 0.18)
    # 1) flat fill
    pygame.draw.polygon(s, base, membrane)
    # 2) dark-core wash — a small shrunk copy so most of the membrane stays the
    # bright (64,176,168) flat fill (the cool note the eye must catch first).
    mcx = sum(p[0] for p in membrane) / len(membrane)
    mcy = sum(p[1] for p in membrane) / len(membrane)
    core = [(mcx + (p[0] - mcx) * 0.58, mcy + (p[1] - mcy) * 0.58)
            for p in membrane]
    pygame.draw.polygon(s, shade(base, 0.66), core)
    pygame.draw.polygon(s, base, [
        (mcx + (p[0] - mcx) * 0.4, mcy + (p[1] - mcy) * 0.4) for p in membrane])
    # 3) top-left COOL sheen wedge riding the leading edge (the triad sheen)
    pygame.draw.polygon(s, TURQ_SHEEN, [
        (ax, ay - sc * 0.12),
        (tip_x, tip_y),
        (ax + d * span * 0.82, ay - sc * 0.04),
        (ax + d * span * 0.34, ay + sc * 0.06),
    ])
    # 4) exactly TWO internal vane struts — hard flats, never feathered
    pygame.draw.line(s, TURQ_D, (ax + d * span * 0.06, ay + sc * 0.10),
                     (ax + d * span * 1.0, ay + sc * 0.46), 3 * SS)
    pygame.draw.line(s, TURQ_D, (ax + d * span * 0.06, ay + sc * 0.26),
                     (ax + d * span * 0.88, ay + sc * 0.84), 3 * SS)
    # 5) a single ochre finger-spar along the leading edge ties wing to body
    pygame.draw.line(s, TAN_D, (ax, ay - sc * 0.06), (tip_x, tip_y), 4 * SS)
    return membrane


# ============================================================================
# CREATURE  — drawn at SS scale into a big surface, outlined, then downscaled.
# ============================================================================
def build_creature():
    W, H = 260 * SS, 200 * SS
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    cx = W // 2

    def P(*pairs):
        return [(int(x * SS), int(y * SS)) for x, y in pairs]

    # ---- DOUBLE-DECK WINGS — drawn FIRST so they sit BEHIND only the torso
    # edge, but pushed FORWARD/outward so they are the two largest masses and
    # FRAME the body. Upper deck large, lower deck smaller & stepped down.
    # Shoulder anchors sit close to the body so the wings read as attached.
    # Anchor the wing roots OUTSIDE the torso edge (torso spans cx +/-24) so
    # each membrane fans out beyond the body silhouette instead of hiding
    # behind it. Big upper deck + smaller lower deck = the double-deck read.
    shoulder_x = 26
    # upper (large) deck — anchored high on the back, fans up & out wide
    draw_wing(s, cx, cx + shoulder_x * SS, 102 * SS,
              span=72 * SS, height=110 * SS, deck=0, side=+1)
    draw_wing(s, cx, cx - shoulder_x * SS, 102 * SS,
              span=72 * SS, height=110 * SS, deck=0, side=-1)
    # lower (small) deck — stepped down & out, clear overlap step under the big
    draw_wing(s, cx, cx + (shoulder_x + 2) * SS, 138 * SS,
              span=52 * SS, height=72 * SS, deck=1, side=+1)
    draw_wing(s, cx, cx - (shoulder_x + 2) * SS, 138 * SS,
              span=52 * SS, height=72 * SS, deck=1, side=-1)

    # ---- SCORPION STING arcing UP & forward, CLEARING the skull crown -------
    # venom outer glow behind the bulb so the lime read survives at small size
    glow = make_glow(34 * SS, VENOM, alpha_center=150, falloff=1.6)
    # bulb sits HIGH and to the left, clearing the head crown (head center ~80)
    bulb_x, bulb_y = cx / SS - 32, 26
    s.blit(glow, (int(bulb_x * SS) - glow.get_width() // 2,
                  bulb_y * SS - glow.get_height() // 2),
           special_flags=pygame.BLEND_RGBA_ADD)

    # the tail: a fat chitin TUBE from the right hip, up the right side, then
    # hooking LEFT & forward over the head so the bulb-sting clears the crown.
    arc = [
        (cx / SS + 22, 150), (cx / SS + 40, 122), (cx / SS + 44, 90),
        (cx / SS + 34, 58), (cx / SS + 14, 36), (cx / SS - 14, 24),
        (bulb_x, bulb_y),
    ]
    apx = [(x * SS, y * SS) for x, y in arc]
    # under-stroke (dark core; the grown outline will hug this)
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

    # fat venom bulb sting tip — the ONE dominant round mass up top
    tcx, tcy = int(bulb_x * SS), int(bulb_y * SS)
    pygame.draw.circle(s, lerp(OCHRE, TAN_D, 0.18), (tcx, tcy), 17 * SS)
    pygame.draw.circle(s, shade(OCHRE, 0.6), (tcx + 3 * SS, tcy + 4 * SS), 12 * SS)
    pygame.draw.circle(s, OCHRE, (tcx, tcy), 10 * SS)
    pygame.draw.circle(s, SHEEN, (tcx - 6 * SS, tcy - 6 * SS), 5 * SS)
    # venom-lime glow node ON the creature's own sting (echoes the pillar cap)
    pygame.draw.circle(s, VENOM, (tcx + 2 * SS, tcy + 2 * SS), 6 * SS)
    pygame.draw.circle(s, lerp(VENOM, SHEEN, 0.45), (tcx, tcy), 3 * SS)
    # the venom barb point aiming down-forward toward the snarl
    pygame.draw.polygon(s, OCHRE, P((bulb_x - 4, bulb_y + 14),
                                    (bulb_x - 14, bulb_y + 30),
                                    (bulb_x + 6, bulb_y + 18)))
    pygame.draw.polygon(s, VENOM, P((bulb_x - 8, bulb_y + 24),
                                    (bulb_x - 16, bulb_y + 34),
                                    (bulb_x - 2, bulb_y + 26)))
    pygame.draw.circle(s, VENOM, (int((bulb_x - 16) * SS), (bulb_y + 36) * SS), 4 * SS)

    # ---- STUMPY RIB-TORSO ---------------------------------------------------
    triad_poly(s, P((cx / SS - 24, 116), (cx / SS + 24, 116),
                    (cx / SS + 20, 166), (cx / SS - 20, 166)),
               OCHRE,
               sheen_pts=P((cx / SS - 22, 118), (cx / SS - 6, 118),
                           (cx / SS - 10, 158), (cx / SS - 22, 154)))
    for ry in (124, 134, 144):
        pygame.draw.line(s, TAN_D, ((cx / SS - 16) * SS, ry * SS),
                         ((cx / SS + 16) * SS, ry * SS), 2 * SS)

    # ---- FOUR LITTLE BIRD-CLAW LIMBS ---------------------------------------
    def claw(x, y, d):
        triad_poly(s, P((x, y), (x + d * 8, y + 2),
                        (x + d * 6, y + 16), (x - d * 1, y + 14)), OCHRE)
        for t in (-3, 0, 3):
            pygame.draw.line(s, TAN_D, ((x + d * 4) * SS, (y + 14) * SS),
                             ((x + d * 4 + t) * SS, (y + 22) * SS), 2 * SS)
    claw(cx / SS - 16, 158, -1)
    claw(cx / SS + 16, 158, +1)
    claw(cx / SS - 24, 116, -1)
    claw(cx / SS + 24, 116, +1)

    # ---- BLOCKY CANINE-LION HEAD with square open snarl --------------------
    hy = 80  # head center y
    triad_poly(s, P((cx / SS - 26, hy - 22), (cx / SS + 26, hy - 22),
                    (cx / SS + 28, hy + 10), (cx / SS + 16, hy + 24),
                    (cx / SS - 16, hy + 24), (cx / SS - 28, hy + 10)),
               OCHRE,
               sheen_pts=P((cx / SS - 24, hy - 20), (cx / SS - 4, hy - 20),
                           (cx / SS - 10, hy + 8), (cx / SS - 24, hy + 4)))
    triad_poly(s, P((cx / SS - 14, hy + 6), (cx / SS + 14, hy + 6),
                    (cx / SS + 12, hy + 28), (cx / SS - 12, hy + 28)), OCHRE)
    pygame.draw.polygon(s, shade(TAN_D, 0.5), P(
        (cx / SS - 9, hy + 14), (cx / SS + 9, hy + 14),
        (cx / SS + 8, hy + 26), (cx / SS - 8, hy + 26)))
    for fx in (-7, -3, 3, 7):
        pygame.draw.polygon(s, SHEEN, P(
            (cx / SS + fx - 1.5, hy + 26), (cx / SS + fx + 1.5, hy + 26),
            (cx / SS + fx, hy + 19)))
    pygame.draw.line(s, TAN_D, ((cx / SS - 12) * SS, (hy + 8) * SS),
                     ((cx / SS - 4) * SS, (hy + 4) * SS), 2 * SS)
    pygame.draw.line(s, TAN_D, ((cx / SS + 12) * SS, (hy + 8) * SS),
                     ((cx / SS + 4) * SS, (hy + 4) * SS), 2 * SS)
    # small canine ears swept back
    triad_poly(s, P((cx / SS - 26, hy - 20), (cx / SS - 34, hy - 30),
                    (cx / SS - 20, hy - 24)), TAN_D)
    triad_poly(s, P((cx / SS + 26, hy - 20), (cx / SS + 34, hy - 30),
                    (cx / SS + 20, hy - 24)), TAN_D)

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
        pygame.draw.line(s, INK, (ecx, ecy - 1 * SS), (ecx, ecy + 6 * SS), 2 * SS)
        pygame.draw.circle(s, SHEEN, (int(ecx - 2 * SS), int(ecy)), 1 * SS)
    pygame.draw.line(s, TAN_D, ((cx / SS - 16) * SS, (hy - 12) * SS),
                     ((cx / SS + 16) * SS, (hy - 12) * SS), 2 * SS)

    out = grow_outline(s, INK, px=1 * SS)
    return out


# ============================================================================
# PROP -> PILLAR  : scorpion STING-SPEAR (segmented chitin shaft + venom cap)
# ============================================================================
def build_pillar_segment(width_px, height_px):
    W, H = width_px * SS, height_px * SS
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    cx = W // 2
    half = int(W * 0.36)
    pygame.draw.rect(s, OCHRE, (cx - half, 0, half * 2, H))
    pygame.draw.rect(s, shade(OCHRE, 0.6), (cx, 0, half, H))
    pygame.draw.rect(s, OCHRE, (cx - half, 0, half, H))
    pygame.draw.rect(s, SHEEN, (cx - half, 0, int(half * 0.4), H))
    seg_h = 18 * SS
    y = 0
    while y < H:
        pygame.draw.line(s, TAN_D, (cx - half, y), (cx + half, y), 3 * SS)
        pygame.draw.line(s, shade(OCHRE, 0.5), (cx - half, y + 3 * SS),
                         (cx + half, y + 3 * SS), 1 * SS)
        y += seg_h
    return grow_outline(s, INK, px=1 * SS)


def build_pillar_cap(width_px, height_px):
    W, H = width_px * SS, height_px * SS
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    cx = W // 2
    half = int(W * 0.36)

    def P(*pairs):
        return [(int(x), int(y)) for x, y in pairs]

    glow = make_glow(int(W * 0.5), VENOM, alpha_center=130, falloff=1.7)
    s.blit(glow, (cx - glow.get_width() // 2,
                  int(H * 0.5) - glow.get_height() // 2),
           special_flags=pygame.BLEND_RGBA_ADD)
    pygame.draw.rect(s, OCHRE, (cx - half, 0, half * 2, int(H * 0.28)))
    pygame.draw.rect(s, shade(OCHRE, 0.6), (cx, 0, half, int(H * 0.28)))
    pygame.draw.rect(s, SHEEN, (cx - half, 0, int(half * 0.4), int(H * 0.28)))
    by = int(H * 0.46)
    br = int(W * 0.34)
    pygame.draw.circle(s, lerp(OCHRE, TAN_D, 0.2), (cx, by), br)
    pygame.draw.circle(s, shade(OCHRE, 0.6), (cx + 3 * SS, by + 3 * SS), int(br * 0.72))
    pygame.draw.circle(s, OCHRE, (cx, by), int(br * 0.6))
    pygame.draw.circle(s, SHEEN, (cx - int(br * 0.4), by - int(br * 0.4)), int(br * 0.28))
    pygame.draw.polygon(s, OCHRE, P(
        (cx - br * 0.5, by + br * 0.6), (cx + br * 0.5, by + br * 0.6),
        (cx + 2 * SS, H - 6 * SS)))
    pygame.draw.polygon(s, TAN_D, P(
        (cx, by + br * 0.6), (cx + br * 0.5, by + br * 0.6), (cx + 2 * SS, H - 6 * SS)))
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

    label("PAZUL  —  scorpion-tailed plague-wind demon  —  round 2", 16, 12, font_big)
    label("R2: turquoise wings rebuilt as the TWO LARGEST masses — bold faceted panels brought FORWARD, framing the ochre body; sting raised to clear the crown",
          16, 36, font_sm, (200, 200, 210))

    creature = build_creature()

    # ---- Panel A: BOSS showcase ----
    pax, pay, paw, pah = 12, 56, 380, 690
    pygame.draw.rect(sheet, (28, 28, 34), (pax, pay, paw, pah), border_radius=8)
    label("(a) BOSS  showcase scale", pax + 12, pay + 8, font)
    big = down(creature, 2.85)
    sheet.blit(big, (pax + paw // 2 - big.get_width() // 2,
                     pay + (pah - big.get_height()) // 2 + 10))

    # ---- Panel B: PROP -> PILLAR at obstacle scale ----
    pbx = pax + paw + 12
    pbw = 380
    pygame.draw.rect(sheet, (110, 175, 225), (pbx, pay, pbw, pah), border_radius=8)
    label("(b) PROP -> PILLAR  @ obstacle scale", pbx + 12, pay + 8, font, (20, 30, 50))
    seg = build_pillar_segment(60, 200)
    cap = build_pillar_cap(60, 90)
    seg_d = down(seg, 1.0)
    cap_d = down(cap, 1.0)
    px = pbx + 110
    gap_top = pay + 250
    sheet.blit(seg_d, (px, pay + 50))
    sheet.blit(seg_d, (px, pay + 50 + seg_d.get_height() - 4))
    sheet.blit(cap_d, (px, gap_top))
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

    small = down(creature, 1.35)
    tiny = down(creature, 0.30)

    tw = (pcw - 36) // 2
    th = 200
    tx, ty = pcx + 12, pay + 40
    day = vgrad(tw, th, *SKY_DAY)
    day.blit(small, (tw // 2 - small.get_width() // 2, th - small.get_height() - 6))
    sheet.blit(day, (tx, ty))
    label("DAY", tx + 6, ty + 4, font_sm, (20, 30, 50))
    nx = tx + tw + 12
    night = vgrad(tw, th, *SKY_NIGHT)
    night.blit(small, (tw // 2 - small.get_width() // 2, th - small.get_height() - 6))
    sheet.blit(night, (nx, ty))
    label("NIGHT", nx + 6, ty + 4, font_sm, (235, 235, 240))

    sy = ty + th + 20
    label("32px read  (creature 1x / 2x zoom / sting-cap)", pcx + 12, sy, font_sm, (215, 215, 225))
    strip = pygame.Surface((pcw - 24, 84))
    strip.fill((60, 60, 70))
    strip.blit(tiny, (16, 42 - tiny.get_height() // 2))
    tiny2 = pygame.transform.scale(tiny, (tiny.get_width() * 2, tiny.get_height() * 2))
    strip.blit(tiny2, (16 + tiny.get_width() + 26, 42 - tiny2.get_height() // 2))
    cap_tiny = down(cap, 0.30)
    strip.blit(cap_tiny, (strip.get_width() - cap_tiny.get_width() - 24,
                          42 - cap_tiny.get_height() // 2))
    sheet.blit(strip, (pcx + 12, sy + 18))

    gy = sy + 124
    label("grayscale  —  silhouette / value tell  (warm body vs cool wings)",
          pcx + 12, gy, font_sm, (215, 215, 225))
    gpanel = pygame.Surface((pcw - 24, 210))
    gpanel.fill((150, 150, 155))
    gray = down(creature, 1.1)
    gs = gray.copy()
    arr = pygame.surfarray.pixels3d(gray.copy())
    px3 = pygame.surfarray.pixels3d(gs)
    lum = (0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 2]).astype('uint8')
    px3[:, :, 0] = lum
    px3[:, :, 1] = lum
    px3[:, :, 2] = lum
    del px3, arr
    gpanel.blit(gs, (gpanel.get_width() // 2 - gs.get_width() // 2, 4))
    sheet.blit(gpanel, (pcx + 12, gy + 18))

    out_path = "/home/user/skybit/docs/skybit_devil/batch2/pazul/round_2.png"
    pygame.image.save(sheet, out_path)
    print("saved", out_path)


if __name__ == "__main__":
    import os
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    os.environ["SDL_AUDIODRIVER"] = "dummy"
    main()
