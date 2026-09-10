"""
Round-2 concept renderer for TAKE-TSUCHIGUMO — the grove spider-yokai whose
legs are jointed bamboo culm-segments  (bamboo v2 REALISTIC set, concept #7).
Headless Pygame; ELEVATED pipeline (supersample SS=6 -> smoothscale) so the
node-ring leg-joints stay crisp at downscale.

WHY round 2 is a SILHOUETTE / LEGIBILITY RE-POSE, not a redesign: round 1's
hero was strong, but the legs launched as two bilateral SIDE-FANS (all angles
in one upper-left arc, then mirrored) with a bare front gap, so the 32px chip
down-sampled to a crab/beetle LOZENGE instead of a radial spider STAR. The
fix is purely in the LEG LAYOUT + value separation; hero shading, palette, the
amber eye-focal, and the culm-node leg construction are unchanged.

WHAT CHANGED vs round 1 (the AD punch list):
1. TRUE RADIAL SPLAY: legs now ring the body all the way around the clock —
   a front pair reaching FORWARD/DOWN (killing the bare front gap), mid pairs
   straight OUT, a rear pair swept BACK — so the blacked-out chip radiates from
   a central hub like an asterisk, not a solid lozenge.
2. FRONT PAIRS LARGEST (pulled hard): the front 2 leg-pairs are now ~1.4-1.5x
   body width and clearly the boldest/longest radiating spokes; rear pairs
   taper and recede. A few long dominant legs read "spider" at 32px.
3. LEGS SEPARATED FROM BODY ON NIGHT: the brighter muddy-tan node band now
   lands on the OUTER leg segments (outer-segment node knuckles are pushed one
   value step brighter), so leg edges catch light against the dark body.
4. WHOLE-FORM VALUE LIFTED ~15-20% vs night: the carapace lit band is pushed
   up and the rose collars / tan nodes form a mid-value scaffold so the body
   silhouette holds against the night sky.
5. GAP-CAP HEAD scaled up ~35% with bolder amber eye-glints + a clear fang
   triangle so it reads as a fanged spider-head; the lower-mirror curled claw +
   web-wisp is drawn as a clearer hooked shape.

WHY this is the RADIAL MULTI-LEG SPIDER of the set (and the ONLY one): the
roster green lanes are all upright stalks/creatures, so Tsuchigumo is the sole
many-limbed star. Each leg is a real bamboo culm whose NODE-RINGS segment the
leg-joints (the node IS the leg-knuckle), a dusty-rose sheath-collar at each.

WHY amber is the readability anchor: deep grove-green-black (58,90,62)/(34,54,38)
risks merging with NIGHT skies AND with its own legs at small scale, so the
venom-amber eye-glints + fang-tips (232,176,72) are pushed to the BRIGHTEST
values on the figure. The whole figure leans HARD into the WARM amber/dusty-rose
ambush-predator temperature — the gap-widener against #3's COOL snow-white mound.

WHY the single culm-LEG is the pillar: a jointed leg IS a natural bamboo culm —
node-segment leg = the repeat band; the fanged head-carapace with eye-glints =
the detachable gap-edge cap; a curled leg-tip claw + a wisp of web = the lower
mirror. Slim, on-axis, bottom-rooted.

WHY a standalone script under docs/: review art must never enter the shipped
bundle, so it imports nothing from game.* — only colour math + the stepped-band
helpers, the alpha-grown outline, and the radial_glow cloned from the lineage.
"""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame

pygame.init()

# ── PINNED PALETTE (locked brief, lane #7) — UNCHANGED from round 1 ───────────
GROVE      = ( 58,  90,  62)   # deep grove-green culm base (the dominant fill)
GROVE_D    = ( 34,  54,  38)   # near-black bark shade
GROVE_DD   = ( 22,  38,  28)   # deepest culm hollow / inter-leg shadow
NODE_TAN   = (150, 120,  72)   # muddy-tan leg-node knuckle band
AMBER      = (232, 176,  72)   # venom-amber eye-cluster + fang-tip (focal/anchor)
AMBER_HOT  = (255, 224, 150)   # hottest amber glint core
AMBER_RUST = (176, 116,  44)   # rust shade beneath the amber
ROSE       = (178, 108,  98)   # dusty-rose sheath-collar
ROSE_HI    = (214, 156, 142)   # rose collar lit edge
INK        = ( 28,  22,  30)   # hard ink keyline

# derived stepped bands inside the pinned families (no new hues) — discrete
# VALUE steps, never blended. Round 2 lifts the lit culm band a touch so the
# body silhouette holds ~15-20% brighter against the night sky.
GROVE_HI   = (104, 146, 100)   # lit culm facet (top-left band) — lifted vs r1
GROVE_HHI  = (146, 184, 132)   # hottest culm rim band (a thin top edge only)
NODE_HI    = (198, 166, 108)   # lit node-knuckle band — lifted vs r1
NODE_D     = (104,  80,  46)   # shaded node band

BG         = ( 42,  52,  44)   # deep-grove review backdrop
PANEL      = ( 30,  40,  34)
DAY_SKY_T  = (120, 196, 236)   # day biome sky (top)
DAY_SKY_B  = (196, 232, 244)
NIGHT_T    = ( 22,  26,  54)   # night biome sky (top)
NIGHT_B    = ( 48,  44,  82)
LABEL      = (236, 240, 230)
LABEL_DIM  = (186, 200, 184)


def lerp(a, b, t):
    t = max(0.0, min(1.0, t))
    return (int(a[0] + (b[0] - a[0]) * t),
            int(a[1] + (b[1] - a[1]) * t),
            int(a[2] + (b[2] - a[2]) * t))


# ── outline grown from the alpha mask (the house keyline) ────────────────────
def grow_outline(surf, color, px):
    mask = pygame.mask.from_surface(surf)
    pts = mask.outline()
    if len(pts) < 2:
        return surf
    base = surf.copy()
    ring = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    for (ox, oy) in pts:
        pygame.draw.circle(ring, color, (ox, oy), px)
    ring.blit(base, (0, 0))
    return ring


def radial_glow(radius, color, alpha_center=200, falloff=2.0):
    """Soft additive radial halo — ACCENTS ONLY (the venom-amber eyes/fangs).
    Cloned from the necrarch lineage. The body shading never uses this; it is
    strictly the warm focal bloom so the amber wins the first glance."""
    size = radius * 2 + 2
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    c = radius + 1
    for r in range(radius, 0, -1):
        t = (r / radius) ** falloff
        a = int(alpha_center * (1 - t))
        pygame.draw.circle(s, (*color, max(0, min(255, a))), (c, c), r)
    return s


# ── HARD STEPPED-BAND shading (the bamboo-v2 sculpt — NO gradients) ──────────
def stepped_blob(surf, pts, bands, ow=2):
    """Fill a polygon as 4-6 HARD value bands instead of a smooth gradient: an
    ink keyline, then each (color, inset_t) drawn as a concentrically scaled-in
    copy of the silhouette so the form reads as discrete sculpted facets. WHY
    inset-scaling and not a separate hand-poly per band: it guarantees the bands
    nest cleanly and never gap, and it survives the 32px downscale as steps, not
    mush. `bands` is ordered darkest/outermost -> brightest/innermost; the first
    band IS the base fill (inset 1.0)."""
    pygame.draw.polygon(surf, INK, pts)
    gx = sum(p[0] for p in pts) / len(pts)
    gy = sum(p[1] for p in pts) / len(pts)
    for color, t in bands:
        if t >= 0.999:
            pygame.draw.polygon(surf, color, pts)
        else:
            poly = [(gx + (px - gx) * t, gy + (py - gy) * t) for (px, py) in pts]
            pygame.draw.polygon(surf, color, poly)
    pygame.draw.polygon(surf, INK, pts, ow)


def offset_band(surf, pts, color, dx, dy, frac=0.62):
    """A directional HARD value band: a copy of the silhouette shifted by
    (dx,dy) and clipped to the original by intersection-via-scale. Used for the
    top-left lit facet on the round carapace so the light has a DIRECTION, still
    as a hard step (no blend)."""
    gx = sum(p[0] for p in pts) / len(pts)
    gy = sum(p[1] for p in pts) / len(pts)
    poly = [(gx + (px - gx) * frac + dx, gy + (py - gy) * frac + dy)
            for (px, py) in pts]
    pygame.draw.polygon(surf, color, poly)


# ── a single CULM LEG SEGMENT — a real bamboo internode with a node-knuckle ──
def culm_segment(surf, a, b, w_root, w_tip, s, collar=True, sulcus=True,
                 outer=False):
    """One internode of a culm leg: a near-parallel tapering tube from `a` to
    `b`, shaded in HARD stepped bands (dark bark trailing edge -> grove fill ->
    lit rim band along the leading edge), with the Phyllostachys SULCUS groove
    as a single dark line down the lit face. A muddy-tan NODE-KNUCKLE ring + a
    dusty-rose SHEATH-COLLAR cap the `b` end (the leg-joint = the botanical node:
    botany and anatomy fuse). WHY hard bands not a tube-gradient: stepped facets
    keep the segment reading as a faceted culm at 32px instead of a smudged
    noodle, and the node-rings + rose collar are the bamboo tell.

    `outer=True` flags the OUTER leg segments (mid/tip joints away from the
    body): their node knuckles use the brighter lit tan band so the leg EDGES
    catch light and separate from the dark body mass on a night sky."""
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    nx, ny = -uy, ux                 # perpendicular = width axis
    hr, ht = w_root * 0.5, w_tip * 0.5
    quad = [
        (ax + nx * hr, ay + ny * hr),
        (bx + nx * ht, by + ny * ht),
        (bx - nx * ht, by - ny * ht),
        (ax - nx * hr, ay - ny * hr),
    ]
    # 4 hard bands: bark shade base -> grove fill -> lit facet -> hot rim sliver.
    pygame.draw.polygon(surf, INK, quad)
    pygame.draw.polygon(surf, GROVE_D, quad)
    # grove fill = the leading 70% of the width (a hard band, not a blend)
    fill = [
        (ax + nx * hr, ay + ny * hr),
        (bx + nx * ht, by + ny * ht),
        (bx + nx * ht - nx * w_tip * 0.62, by + ny * ht - ny * w_tip * 0.62),
        (ax + nx * hr - nx * w_root * 0.62, ay + ny * hr - ny * w_root * 0.62),
    ]
    pygame.draw.polygon(surf, GROVE, fill)
    # lit facet band along the leading edge (top-left of the tube)
    lit = [
        (ax + nx * hr, ay + ny * hr),
        (bx + nx * ht, by + ny * ht),
        (bx + nx * ht - nx * w_tip * 0.30, by + ny * ht - ny * w_tip * 0.30),
        (ax + nx * hr - nx * w_root * 0.30, ay + ny * hr - ny * w_root * 0.30),
    ]
    pygame.draw.polygon(surf, GROVE_HI, lit)
    # a hot rim sliver — a thin top edge only (the brightest culm band)
    pygame.draw.line(surf, GROVE_HHI,
                     (ax + nx * hr * 0.92, ay + ny * hr * 0.92),
                     (bx + nx * ht * 0.92, by + ny * ht * 0.92),
                     max(1, int(w_tip * 0.14)))
    if sulcus:
        # Phyllostachys sulcus groove — one confident dark line down the face
        pygame.draw.line(surf, GROVE_DD,
                         (ax - nx * hr * 0.18, ay - ny * hr * 0.18),
                         (bx - nx * ht * 0.18, by - ny * ht * 0.18),
                         max(1, int(w_tip * 0.16)))
    pygame.draw.polygon(surf, INK, quad, max(1, int(w_tip * 0.12)))

    if collar:
        # NODE-KNUCKLE: the two-ring bamboo node (muddy-tan), swelling slightly
        # proud of the tube — the leg-joint. Then the dusty-rose SHEATH-COLLAR
        # flaring back below it (papery sheath scar).
        cw = max(ht * 1.55, ht + 1.4 * s)
        node = [
            (bx + nx * cw, by + ny * cw),
            (bx + nx * cw - ux * w_tip * 0.55, by + ny * cw - uy * w_tip * 0.55),
            (bx - nx * cw - ux * w_tip * 0.55, by - ny * cw - uy * w_tip * 0.55),
            (bx - nx * cw, by - ny * cw),
            (bx - nx * cw + ux * w_tip * 0.55, by - ny * cw + uy * w_tip * 0.55),
            (bx + nx * cw + ux * w_tip * 0.55, by + ny * cw + uy * w_tip * 0.55),
        ]
        # OUTER leg-segment knuckles ride one value step BRIGHTER so the leg
        # edges separate from the dark body on a night sky (AD note 3).
        if outer:
            node_bands = [(NODE_TAN, 1.0), (NODE_HI, 0.78), (AMBER_HOT, 0.4)]
        else:
            node_bands = [(NODE_D, 1.0), (NODE_TAN, 0.82), (NODE_HI, 0.5)]
        stepped_blob(surf, node, node_bands, ow=max(1, int(w_tip * 0.12)))
        # the two close node rings (sheath-ring + stem-ring) as hard dark ticks
        for kk in (-0.30, 0.30):
            pygame.draw.line(surf, GROVE_DD,
                             (bx + nx * cw + ux * w_tip * 0.55 * kk,
                              by + ny * cw + uy * w_tip * 0.55 * kk),
                             (bx - nx * cw + ux * w_tip * 0.55 * kk,
                              by - ny * cw + uy * w_tip * 0.55 * kk),
                             max(1, int(w_tip * 0.10)))
        # dusty-rose sheath-collar flaring back below the node (papery scar) —
        # a mid-value scaffold that keeps the leg readable against the night
        back = (bx - ux * w_tip * 0.55, by - uy * w_tip * 0.55)
        collar_poly = [
            (back[0] + nx * cw * 1.18, back[1] + ny * cw * 1.18),
            (back[0] - ux * w_tip * 0.6 + nx * cw * 0.5,
             back[1] - uy * w_tip * 0.6 + ny * cw * 0.5),
            (back[0] - ux * w_tip * 0.6 - nx * cw * 0.5,
             back[1] - uy * w_tip * 0.6 - ny * cw * 0.5),
            (back[0] - nx * cw * 1.18, back[1] - ny * cw * 1.18),
        ]
        pygame.draw.polygon(surf, INK, collar_poly)
        pygame.draw.polygon(surf, ROSE, collar_poly)
        pygame.draw.line(surf, ROSE_HI,
                         (back[0] + nx * cw * 1.1, back[1] + ny * cw * 1.1),
                         (back[0] - ux * w_tip * 0.55 + nx * cw * 0.45,
                          back[1] - uy * w_tip * 0.55 + ny * cw * 0.45),
                         max(1, int(w_tip * 0.12)))


# ── a whole jointed CULM LEG — 3 internodes radiating then drooping, claw tip ─
def culm_leg(surf, root, ang0, reach, w0, s, droop=0.55, tip_claw=True):
    """A spider leg built from THREE culm internodes, each shorter and thinner
    than the last, the leg ARCING progressively along `droop` per joint so it
    reads as a long jointed limb, not a straight radial spoke. Node-knuckles +
    rose collars segment every joint; the OUTER (2nd, 3rd) joints get the
    brighter lit-tan knuckle so the leg edge catches light against the body.
    Ends in a small curled culm-tip CLAW (a sharp dark hook). WHY front-largest
    construction lives in the caller: the radial star must read at 32px, so the
    caller renders the FRONT pairs with bigger `reach`/`w0`."""
    segs = ((0.46, 1.00), (0.34, 0.74), (0.20, 0.56))   # (len-frac, width-frac)
    a = ang0
    p = root
    w = w0
    for i, (lf, wf) in enumerate(segs):
        seg_len = reach * lf
        nxp = (p[0] + math.cos(a) * seg_len, p[1] + math.sin(a) * seg_len)
        wt = w0 * (wf * 0.78 if i < len(segs) - 1 else wf * 0.5)
        culm_segment(surf, p, nxp, w, wt, s,
                     collar=(i < len(segs) - 1), sulcus=True,
                     outer=(i >= 1))             # 2nd+ joints = OUTER (lit knuckle)
        p = nxp
        w = wt
        a += droop                               # each joint angles further along
    if tip_claw:
        # a small curled culm-tip claw — a sharp dark hook, brightest amber rim
        cl = reach * 0.12
        tip = (p[0] + math.cos(a + 0.5) * cl, p[1] + math.sin(a + 0.5) * cl)
        claw = [
            (p[0] + math.cos(a - 1.4) * w, p[1] + math.sin(a - 1.4) * w),
            tip,
            (p[0] + math.cos(a + 1.6) * w, p[1] + math.sin(a + 1.6) * w),
        ]
        pygame.draw.polygon(surf, INK, claw)
        pygame.draw.polygon(surf, GROVE_D, claw)
    return p, a


# ── the venom-amber EYE-CLUSTER + FANGS (the focal, brightest values) ────────
def eye_cluster(surf, cx, cy, r, s, glow=True):
    """The spider face: a cluster of eight tiny venom-amber eye-glints in two
    rows (the tsuchigumo's many eyes) + two amber fang-tips below. These are the
    BRIGHTEST values on the figure and the small-scale readability anchor, so
    each glint carries a soft amber radial halo + a hot core; the fangs glow at
    the tips. WHY amber-not-green: the deep grove body would otherwise vanish on
    a night sky and merge with its own legs — the amber is the lock-on."""
    # the principal pair (largest, front) + flanking smaller eyes
    eyes = [
        (-0.55, -0.18, 1.10), (0.55, -0.18, 1.10),   # principal front pair (big)
        (-0.95, -0.40, 0.62), (0.95, -0.40, 0.62),   # outer upper
        (-0.22, -0.52, 0.55), (0.22, -0.52, 0.55),   # inner upper
        (-0.40, 0.14, 0.50), (0.40, 0.14, 0.50),     # lower row
    ]
    for ex, ey, ef in eyes:
        px = int(cx + ex * r)
        py = int(cy + ey * r)
        er = max(2, int(r * 0.20 * ef))
        if glow:
            g = radial_glow(int(er * 2.4), AMBER, alpha_center=150, falloff=2.4)
            surf.blit(g, (px - g.get_width() // 2, py - g.get_height() // 2),
                      special_flags=pygame.BLEND_ADD)
        pygame.draw.circle(surf, INK, (px, py), er + max(1, int(0.6 * s)))
        pygame.draw.circle(surf, AMBER_RUST, (px, py), er)
        pygame.draw.circle(surf, AMBER, (px, py), max(1, int(er * 0.72)))
        pygame.draw.circle(surf, AMBER_HOT,
                           (px - max(1, er // 3), py - max(1, er // 3)),
                           max(1, int(er * 0.34)))
    # two fangs (chelicerae) hooking DOWN below the cluster, amber-tipped
    for sgn in (-1, 1):
        fx = cx + sgn * int(r * 0.34)
        fang = [
            (fx - sgn * int(r * 0.18), cy + int(r * 0.42)),
            (fx + sgn * int(r * 0.16), cy + int(r * 0.46)),
            (cx + sgn * int(r * 0.10), cy + int(r * 1.02)),   # hooked tip toward centre
        ]
        stepped_blob(surf, fang, [
            (GROVE_DD, 1.0), (NODE_D, 0.74), (NODE_TAN, 0.42),
        ], ow=max(1, int(0.9 * s)))
        # amber-glowing fang TIP (brightest, the venom)
        tip = (cx + sgn * int(r * 0.10), cy + int(r * 1.02))
        if glow:
            g = radial_glow(max(2, int(r * 0.22)), AMBER, alpha_center=170,
                            falloff=2.2)
            surf.blit(g, (tip[0] - g.get_width() // 2,
                          tip[1] - g.get_height() // 2),
                      special_flags=pygame.BLEND_ADD)
        pygame.draw.circle(surf, AMBER, tip, max(1, int(r * 0.09)))
        pygame.draw.circle(surf, AMBER_HOT, tip, max(1, int(r * 0.045)))


# ── the bristled CARAPACE body (compact, split-culm plating) ─────────────────
def carapace(surf, cx, cy, rw, rh, s):
    """The compact bristled spider body: a rounded carapace (cephalothorax) over
    a fatter abdomen, plated like SPLIT CULM (hard stepped facets + node-ring
    arcs), fine leaf-hair bristles around the rim, paired branch-stub spinnerets
    below the abdomen. Drawn as the radial hub the legs root into. HARD bands
    only — top-left lit facet stepped, never blended. Round 2 lifts the body's
    lit band (GROVE_HI) up so the silhouette holds ~15-20% brighter against the
    night sky."""
    # ABDOMEN (lower, fatter) — drawn first, behind the cephalothorax
    ab_cy = cy + int(rh * 0.86)
    ab = []
    for k in range(20):
        th = math.tau * k / 20
        ax = cx + math.cos(th) * rw * 1.06
        ay = ab_cy + math.sin(th) * rh * 1.16
        ab.append((ax, ay))
    stepped_blob(surf, ab, [
        (GROVE_D, 1.0), (GROVE, 0.80), (GROVE_HI, 0.46),
    ], ow=max(1, int(1.4 * s)))
    offset_band(surf, ab, GROVE_HHI, -rw * 0.18, -rh * 0.20, frac=0.30)
    # split-culm node-ring arcs banding the abdomen (the bamboo tell on the body)
    for i in range(3):
        ry = ab_cy - int(rh * 0.5) + i * int(rh * 0.62)
        rww = int(rw * (1.02 - i * 0.12))
        pygame.draw.arc(surf, GROVE_DD,
                        (cx - rww, ry - int(rh * 0.3), rww * 2, int(rh * 0.6)),
                        math.radians(202), math.radians(338), max(1, int(1.6 * s)))
        pygame.draw.arc(surf, NODE_TAN,
                        (cx - rww, ry - int(rh * 0.3) - int(1.4 * s),
                         rww * 2, int(rh * 0.6)),
                        math.radians(206), math.radians(334), max(1, int(1.2 * s)))
    # paired branch-stub spinnerets at the abdomen base
    for sgn in (-1, 1):
        sp = (cx + sgn * int(rw * 0.22), ab_cy + int(rh * 1.06))
        spine = [
            (sp[0] - sgn * int(rw * 0.12), sp[1] - int(rh * 0.14)),
            (sp[0] + sgn * int(rw * 0.12), sp[1] - int(rh * 0.10)),
            (sp[0] + sgn * int(rw * 0.30), sp[1] + int(rh * 0.30)),
        ]
        stepped_blob(surf, spine, [(GROVE_DD, 1.0), (NODE_D, 0.6)],
                     ow=max(1, int(0.8 * s)))

    # CEPHALOTHORAX (upper, the head-carapace the eyes/fangs sit on)
    ceph = []
    for k in range(20):
        th = math.tau * k / 20
        ax = cx + math.cos(th) * rw
        ay = cy + math.sin(th) * rh
        ceph.append((ax, ay))
    # fine leaf-hair bristles around the rim FIRST (behind the plate)
    import random
    rnd = random.Random(7)
    for k in range(28):
        th = math.tau * k / 28
        bx = cx + math.cos(th) * rw
        by = cy + math.sin(th) * rh
        bl = (3.0 + rnd.random() * 3.0) * s
        bt = (bx + math.cos(th) * bl, by + math.sin(th) * bl)
        pygame.draw.line(surf, GROVE_DD, (bx, by), bt, max(1, int(0.7 * s)))
    stepped_blob(surf, ceph, [
        (GROVE_D, 1.0), (GROVE, 0.82), (GROVE_HI, 0.5),
    ], ow=max(1, int(1.6 * s)))
    offset_band(surf, ceph, GROVE_HHI, -rw * 0.20, -rh * 0.22, frac=0.34)
    # central split-culm sulcus down the carapace + a paired branch-whorl scar
    pygame.draw.line(surf, GROVE_DD, (cx, cy - int(rh * 0.7)),
                     (cx, cy + int(rh * 0.7)), max(1, int(1.4 * s)))
    # a dusty-rose collar arc hugging the carapace front rim — a mid-value
    # scaffold so the body keeps a readable bright edge on the night sky
    pygame.draw.arc(surf, ROSE,
                    (cx - rw, cy - int(rh * 0.2), rw * 2, int(rh * 1.4)),
                    math.radians(206), math.radians(334), max(1, int(1.6 * s)))


# ── the RADIAL spider hero ────────────────────────────────────────────────────
def draw_tsuchigumo(surf, cx, cy, s, leg_glow=True):
    """The grove spider-yokai in a TRUE radial STAR: a compact bristled carapace
    hub with EIGHT jointed culm-legs RINGING the body all the way around — a
    front pair reaching FORWARD/DOWN (no bare front gap), mid pairs straight
    OUT, a rear pair swept BACK — so the silhouette radiates from a central hub
    like an asterisk. The FRONT pairs are the longest/boldest spokes so the star
    reads at 32px; rear pairs taper and recede. Venom-amber eye-cluster + fangs
    as the bright focal. `s` ~ unit scale around a ~120-unit figure. Legs drawn
    first/behind so the carapace overlaps the roots (legs anchored INTO body)."""
    rw = int(20 * s)
    rh = int(17 * s)
    root = (cx, cy + int(2 * s))

    # TRUE RADIAL SPLAY. Angles from +x (right), +y DOWN (screen coords), so
    # 90deg = straight down, 0deg = right, 180deg = left, 270deg = straight up.
    # Defined for the LEFT side then MIRRORED across the vertical axis, ringing
    # the clock from a forward-down reach through straight-out to swept-back.
    # FRONT pairs are clearly LARGEST (reach ~1.4-1.5x body width = 28*s..30*s)
    # so they project well past the body mass and hold the star's points at 32px.
    # (launch_angle_deg, reach_units, root_width_units, droop, root_anchor_t)
    # root_anchor_t in [-1..1] places the leg root around the carapace rim
    # (-1 = front/top of hub, +1 = rear/bottom) so the splay fans from the edge.
    leg_specs = [
        ( 60, 60, 9.0, 0.34, -0.85),   # FRONT — forward & DOWN, LARGEST/boldest
        ( 25, 58, 8.5, 0.30, -0.45),   # front-out — forward-out, also dominant
        (-10, 50, 7.0, 0.28,  0.05),   # mid — straight OUT (slightly up)
        (-42, 40, 5.5, 0.30,  0.55),   # REAR — swept BACK & up, smallest/recede
    ]
    # paint order: rear legs first (behind), front legs last so they overlap and
    # the longest forward spokes sit on top — but keep BOTH front pairs frontmost
    # so the star's dominant points are never buried.
    order = sorted(range(4), key=lambda i: leg_specs[i][1])  # shortest first
    for i in order:
        base_deg, reach, w0, droop, anchor_t = leg_specs[i]
        for sgn in (-1, 1):
            ang = math.radians(base_deg)        # left-side launch
            if sgn > 0:
                ang = math.radians(180) - ang   # mirror to the right side
            # root offset around the carapace rim so legs fan from the hub EDGE
            rx = root[0] + sgn * int(rw * 0.72)
            ry = root[1] + int(rh * 0.55 * anchor_t)
            culm_leg(surf, (rx, ry), ang, reach * s, w0 * s, s,
                     droop=droop, tip_claw=True)

    # the carapace hub over the leg-roots
    carapace(surf, cx, cy, rw, rh, s)

    # the venom-amber eye-cluster + fangs last — the brightest focal owns centre
    eye_cluster(surf, cx, cy - int(rh * 0.18), int(rw * 0.92), s, glow=leg_glow)


# ── the single culm-LEG -> pillar mirror ──────────────────────────────────────
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """The single culm-LEG IS the pillar: a jointed culm shaft (node-segment =
    the repeat band, each node a leg-knuckle with a rose sheath-collar) tiles as
    the body; a single fanged HEAD-CARAPACE with amber eye-glints is the gap-edge
    cap; the lower mirror is a curled leg-tip CLAW + a wisp of web. Slim, on-axis,
    bottom-rooted. `cap` names the END that faces the GAP. Round 2 scales the
    gap-cap head up ~35% and pushes a clearer fang triangle so it reads as a
    fanged spider-head at 32px; the lower-mirror claw is a clearer hook."""
    w_root = int(13 * s)
    w_tip = int(11 * s)
    cap_room = int(58 * s)            # was 46*s — bigger room for the larger head
    if cap == "bottom":
        seg_top, seg_bot = top + int(4 * s), bot - cap_room
        node_dir = 1                      # nodes face down toward the gap
    else:
        seg_top, seg_bot = top + cap_room, bot - int(4 * s)
        node_dir = 1

    # === jointed culm shaft: stacked internodes with node-knuckle leg-joints ===
    seg_pitch = int(30 * s)
    y = seg_top
    while y < seg_bot:
        ny = min(y + seg_pitch, seg_bot)
        culm_segment(surf, (cx, y), (cx, ny), w_root, w_tip, s,
                     collar=(ny < seg_bot - 1), sulcus=True)
        y = ny

    # === gap-edge cap: fanged head-carapace with amber eye-glints =============
    if cap == "bottom":
        cap_cy = bot - int(30 * s)            # head sits higher to fit larger size
        hw, hh = int(20 * s), int(17 * s)     # ~35% bigger carapace than r1
        # a small jointed sub-leg curling off the carapace (the spider tell on
        # the prop) + the eye-cluster facing the gap
        carapace(surf, cx, cap_cy, hw, hh, s)
        culm_leg(surf, (cx - int(13 * s), cap_cy), math.radians(150),
                 30 * s, 6.5 * s, s, droop=0.5)
        culm_leg(surf, (cx + int(13 * s), cap_cy), math.radians(30),
                 30 * s, 6.5 * s, s, droop=0.5)
        eye_cluster(surf, cx, cap_cy - int(2 * s), int(18 * s), s, glow=True)
    else:
        # lower mirror: a clearer curled leg-tip CLAW + a wisp of web, mirrored
        tmp = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        ty = surf.get_height() - (top + int(24 * s))
        # a curled culm-tip claw hooking toward the gap (bigger reach + droop
        # so the hook reads as a clear curled shape)
        p, a = culm_leg(tmp, (cx, ty - int(22 * s)), math.radians(90),
                        40 * s, 9.5 * s, s, droop=0.52)
        # a wisp of web — three faint dragline threads fanning from the claw tip
        for dth in (-0.6, 0.0, 0.6):
            wx = p[0] + math.cos(a + dth) * 34 * s
            wy = p[1] + math.sin(a + dth) * 34 * s
            pygame.draw.line(tmp, ROSE_HI, p, (wx, wy), max(1, int(0.9 * s)))
        flipped = pygame.transform.flip(tmp, False, True)
        surf.blit(flipped, (0, 0))


# ── compose the review sheet ─────────────────────────────────────────────────
SS = 6


def vgrad(surf, rect, top_col, bot_col):
    x, y, w, h = rect
    for j in range(h):
        pygame.draw.line(surf, lerp(top_col, bot_col, j / max(1, h - 1)),
                         (x, y + j), (x + w, y + j))


def main():
    W, H = 1010, 900
    font_big = pygame.font.SysFont("DejaVu Sans", 30, bold=True)
    font = pygame.font.SysFont("DejaVu Sans", 17, bold=True)
    font_sm = pygame.font.SysFont("DejaVu Sans", 12)

    sheet = pygame.Surface((W, H))
    sheet.fill(BG)

    pygame.draw.rect(sheet, PANEL, (0, 0, W, 56))
    sheet.blit(font_big.render("TAKE-TSUCHIGUMO", True, LABEL), (24, 13))
    sheet.blit(font_sm.render(
        "grove spider-yokai · TRUE RADIAL splay · front pairs LARGEST · culm-segment legs (node = leg-knuckle) · venom-amber focal · round 2",
        True, LABEL_DIM), (320, 26))

    # === (a) BIG HERO =========================================================
    def render_hero():
        big = pygame.Surface((360 * SS, 470 * SS), pygame.SRCALPHA)
        draw_tsuchigumo(big, 178 * SS, 220 * SS, 2.05 * SS)
        small = pygame.transform.smoothscale(big, (360, 470))
        return grow_outline(small, INK + (255,), 1)

    sheet.blit(render_hero(), (14, 92))
    sheet.blit(font.render("Creature — hero", True, LABEL), (110, 566))
    sheet.blit(font_sm.render("TRUE RADIAL spider: legs ring the hub — front pair forward/DOWN, mid pairs OUT, rear pair BACK.", True, LABEL_DIM), (14, 590))
    sheet.blit(font_sm.render("FRONT pairs longest/boldest (~1.4-1.5x body) = the dominant star points; rear pairs taper/recede.", True, LABEL_DIM), (14, 606))
    sheet.blit(font_sm.render("Outer leg-knuckles ride a brighter tan band so legs separate from body on night. HARD stepped bands, no gradients.", True, LABEL_DIM), (14, 622))

    # === (b) PILLAR assembled — mirrored, clean tileable shaft ================
    pcx = 470
    top_big = pygame.Surface((150 * SS, 250 * SS), pygame.SRCALPHA)
    draw_pillar(top_big, 75 * SS, 4 * SS, 246 * SS, 1.0 * SS, cap="bottom")
    top_seg = grow_outline(pygame.transform.smoothscale(top_big, (150, 250)), INK + (255,), 1)
    sheet.blit(top_seg, (pcx, 86))
    bot_big = pygame.Surface((150 * SS, 250 * SS), pygame.SRCALPHA)
    draw_pillar(bot_big, 75 * SS, 4 * SS, 246 * SS, 1.0 * SS, cap="top")
    bot_seg = grow_outline(pygame.transform.smoothscale(bot_big, (150, 250)), INK + (255,), 1)
    sheet.blit(bot_seg, (pcx, 86 + 250 + 96))
    pygame.draw.rect(sheet, (40, 50, 42), (pcx + 8, 86 + 250, 134, 96))
    sheet.blit(font_sm.render("GAP", True, LABEL_DIM), (pcx + 56, 86 + 250 + 40))
    sheet.blit(font.render("Pillar — culm-LEG", True, LABEL), (pcx - 4, 690))
    sheet.blit(font_sm.render("node-segment LEG = repeat band (each node a", True, LABEL_DIM), (pcx - 4, 714))
    sheet.blit(font_sm.render("leg-knuckle); BIGGER fanged head-carapace w/", True, LABEL_DIM), (pcx - 4, 730))
    sheet.blit(font_sm.render("eye-glints = gap cap; curled claw + web = mirror.", True, LABEL_DIM), (pcx - 4, 746))

    # === (c) TRUE 32px gameplay chips on day + night sky ======================
    panel_x = 660
    pygame.draw.rect(sheet, PANEL, (panel_x, 86, W - panel_x - 14, 720))
    sheet.blit(font.render("True 32px gameplay-scale chip", True, LABEL), (panel_x + 16, 96))

    def chip32():
        big = pygame.Surface((96 * SS, 96 * SS), pygame.SRCALPHA)
        draw_tsuchigumo(big, 48 * SS, 48 * SS, (32 / 122.0) * SS)
        small = pygame.transform.smoothscale(big, (96, 96))
        return grow_outline(small, INK + (255,), 1)

    chip = chip32()

    day_y = 128
    vgrad(sheet, (panel_x + 20, day_y, 150, 150), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, day_y, 150, 150), 1)
    sheet.blit(chip, (panel_x + 20 + 27, day_y + 27))
    sheet.blit(font_sm.render("32px on day sky", True, LABEL), (panel_x + 20, day_y + 156))

    night_y = day_y + 184
    vgrad(sheet, (panel_x + 20, night_y, 150, 150), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, night_y, 150, 150), 1)
    sheet.blit(chip, (panel_x + 20 + 27, night_y + 27))
    sheet.blit(font_sm.render("32px on night sky", True, LABEL_DIM), (panel_x + 20, night_y + 156))

    # blacked-out 32px silhouette — must read as a radial STAR (a spider), not
    # a blob: the front-largest radial splay has to hold its points.
    def silhouette32():
        big = pygame.Surface((96 * SS, 96 * SS), pygame.SRCALPHA)
        draw_tsuchigumo(big, 48 * SS, 48 * SS, (32 / 122.0) * SS, leg_glow=False)
        small = pygame.transform.smoothscale(big, (96, 96))
        small = grow_outline(small, INK + (255,), 1)
        mask = pygame.mask.from_surface(small, 24)
        sil = mask.to_surface(setcolor=INK + (255,), unsetcolor=(0, 0, 0, 0))
        return sil

    sil_y = night_y + 188
    sx = panel_x + 20
    pygame.draw.rect(sheet, (212, 214, 200), (sx, sil_y, 96, 96))
    pygame.draw.rect(sheet, INK, (sx, sil_y, 96, 96), 1)
    sheet.blit(silhouette32(), (sx, sil_y))
    sheet.blit(font_sm.render("32px BLACKED-OUT silhouette —", True, LABEL), (sx + 104, sil_y + 30))
    sheet.blit(font_sm.render("must read RADIAL SPIDER STAR", True, LABEL_DIM), (sx + 104, sil_y + 48))

    def pillar_chip32():
        big = pygame.Surface((44 * SS, 130 * SS), pygame.SRCALPHA)
        draw_pillar(big, 22 * SS, 2 * SS, 128 * SS, 0.34 * SS, cap="bottom")
        small = pygame.transform.smoothscale(big, (44, 130))
        return grow_outline(small, INK + (255,), 1)

    pc = pillar_chip32()
    px2 = panel_x + 192
    vgrad(sheet, (px2, day_y, 56, 150), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (px2, day_y, 56, 150), 1)
    sheet.blit(pc, (px2 + 6, day_y + 10))
    vgrad(sheet, (px2, night_y, 56, 150), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (px2, night_y, 56, 150), 1)
    sheet.blit(pc, (px2 + 6, night_y + 10))
    sheet.blit(font_sm.render("pillar", True, LABEL_DIM), (px2 + 4, day_y - 16))
    sheet.blit(font_sm.render("gap-cap", True, LABEL_DIM), (px2 - 2, night_y - 16))

    sheet.blit(font.render("Pinned palette", True, LABEL), (panel_x + 16, 636))
    swatches = [
        (GROVE, "grove-green"), (GROVE_D, "bark shade"),
        (AMBER, "venom-amber"), (AMBER_HOT, "amber core"),
        (ROSE, "dusty-rose collar"), (NODE_TAN, "node-tan"),
        (GROVE_DD, "deep hollow"), (INK, "ink keyline"),
    ]
    sxp, syp = panel_x + 16, 664
    for i, (c, name) in enumerate(swatches):
        col, row = i % 2, i // 2
        rx = sxp + col * 158
        ry = syp + row * 26
        pygame.draw.rect(sheet, INK, (rx - 1, ry - 1, 20, 20))
        pygame.draw.rect(sheet, c, (rx, ry, 18, 18))
        sheet.blit(font_sm.render(name, True, LABEL), (rx + 26, ry + 3))

    pygame.draw.rect(sheet, PANEL, (14, 850, W - 28, 40))
    sheet.blit(font_sm.render(
        "BAMBOO v2 REALISTIC: SS=6 supersample -> smoothscale.  4-6 HARD STEPPED value bands per form (NO gradients) · radial glow ACCENTS only · "
        "hard ink keyline (28,22,30) + 1px grown outline · TRUE radial splay, front pairs largest · WARM ambush temperature.",
        True, LABEL_DIM), (26, 863))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_2.png")
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
