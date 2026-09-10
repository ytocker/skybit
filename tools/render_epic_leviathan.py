"""Scratch renderer for the `deep-leviathan` epic-boss concept (round 2).

A bloated abyssal whale-GOD dragging itself out of a drowned world: the only
bulbous/organic-blob mass in the boss set, made epic by rounded BULK and
bioluminescence rather than spikes. Headless-safe (SDL_VIDEODRIVER=dummy).

Palette is the locked three-tone brief: abyss blue-black body, jade-green
bioluminescence as the day+night focal (light against dark, so it holds on
either sky without leaning on hue), and pale-flesh barnacle for the bone-crust
mass that catches rim light.

ROUND 2 — the whole battle is surviving the DOWNSCALE. Round 1's hero passed
but at 1× it collapsed into a cute round blob, so every change below is a
silhouette-first fix aimed at phone scale:

  * The belly smile-glow is GONE — the lit throat is now a downward-pointing
    JAGGED jade maw that reinforces fangs, never a curved grin.
  * The blackout is no longer egg + fins: the lower JAW juts forward and down
    past the body outline so the silhouette reads SNAPPING JAW.
  * Dorsal flukes are raked hard back and uneven — predatory, not rabbit-ears.
  * The jade hierarchy is collapsed to ONE dominant esca-lure + the slit eye,
    with flank nodes demoted ~50% so only ~4 lit points survive at 1×.
  * The pillar spine is an OPAQUE barnacled bone column; bulbs sit ON it as
    CAGED, pale-rimmed nodes that read 'solid wall', not collectible coins.

PROP DECISION: the signature prop is a CHAIN-OF-LURE-STALKS, not a single
harpoon. A barbed TIP can't mirror into a symmetric top/bottom column. A
barnacled bone-spine studded with caged jade nodes flips top-to-bottom into a
clean mirrored pair, every node fanning toward the open gap.
"""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

# ── locked brief palette ─────────────────────────────────────────────────────
ABYSS      = (18, 30, 52)      # abyss blue-black — the body's deep mass
ABYSS_DK   = (10, 18, 34)      # darkest occlusion / under-belly
ABYSS_DKR  = (6, 11, 22)       # deepest core shadow, the maw + belly hollow
ABYSS_HI   = (38, 58, 92)      # lifted top of the dome where ambient catches
ABYSS_RIM  = (58, 86, 128)     # cool wet rim along the crown
JADE       = (72, 236, 176)    # bioluminescent jade — THE focal (light v dark)
JADE_DIM   = (40, 150, 116)    # jade in shadow / stalk cores
JADE_PALE  = (190, 255, 230)   # hottest lure centre, near-white bloom
FLESH      = (200, 196, 184)   # pale-flesh barnacle crust
FLESH_DK   = (132, 128, 118)   # barnacle shade
FLESH_DKR  = (88, 86, 80)      # deepest barnacle occlusion
FLESH_HI   = (238, 236, 228)   # barnacle rim light

DAY_BG  = ((96, 168, 214), (158, 210, 234))   # bright sky → the jade still pops
NIGHT_BG = ((9, 13, 32), (24, 34, 66))         # dark sky → flesh reads, jade glows


def _lerp(a, b, t):
    t = max(0.0, min(1.0, t))
    return (int(a[0] + (b[0] - a[0]) * t),
            int(a[1] + (b[1] - a[1]) * t),
            int(a[2] + (b[2] - a[2]) * t))


def _vgrad(surf, rect, top, bot):
    x, y, w, h = rect
    for i in range(h):
        pygame.draw.line(surf, _lerp(top, bot, i / max(1, h - 1)),
                         (x, y + i), (x + w - 1, y + i))


def _glow(surf, cx, cy, r, color, alpha=150, falloff=2.4):
    """Additive radial bloom — jade lures read as LIGHT, not paint. Rings are
    drawn onto a scratch surface so the centre can't saturate to a solid disc;
    only the final composite blits ADD, so a big halo stays a soft falloff."""
    if r < 1:
        return
    g = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
    for rr in range(r, 0, -1):
        t = (rr / r) ** falloff
        a = int(alpha * (1 - t))
        pygame.draw.circle(g, (*color, max(0, a)), (r + 1, r + 1), rr)
    surf.blit(g, (cx - r - 1, cy - r - 1), special_flags=pygame.BLEND_ADD)


# ── shaded blob primitive: the wet rounded bulk ──────────────────────────────

def _wet_dome(surf, cx, cy, rw, rh):
    """A bottom-heavy water-logged dome rendered as nested ellipses so the mass
    reads as ROUND wet bulk, not a flat cut-out. The KEEP note: this is the only
    rounded blob in the boss set. Dark occluded belly, mid body, a lifted ambient
    crown and a thin cool rim down the top edge — the value ramp sells 'epic
    rounded GOD'. The rim arc is intentionally shallow (top quarter only) so it
    can never read as a curved smile lower down."""
    pygame.draw.ellipse(surf, ABYSS_DKR,
                        (cx - rw, cy - rh + int(rh * 0.12), rw * 2, rh * 2))
    pygame.draw.ellipse(surf, ABYSS_DK,
                        (cx - rw + 3, cy - rh, rw * 2 - 6, rh * 2 - 4))
    pygame.draw.ellipse(surf, ABYSS,
                        (cx - rw + 8, cy - rh - 2, rw * 2 - 16, int(rh * 1.7)))
    crown = pygame.Surface((rw * 2, rh * 2), pygame.SRCALPHA)
    pygame.draw.ellipse(crown, (*ABYSS_HI, 200),
                        (10, -int(rh * 0.10), rw * 2 - 20, int(rh * 0.92)))
    pygame.draw.ellipse(crown, (*ABYSS_RIM, 150),
                        (16, -int(rh * 0.14), rw * 2 - 32, int(rh * 0.46)))
    surf.blit(crown, (cx - rw, cy - rh))
    rim = pygame.Surface((rw * 2, rh), pygame.SRCALPHA)
    pygame.draw.arc(rim, (*ABYSS_RIM, 220),
                    (4, 2, rw * 2 - 8, rh * 2 - 4), 0.7, math.pi - 0.5, 2)
    surf.blit(rim, (cx - rw, cy - rh))


# ── barnacle crust primitive (shared by body back + lure column) ─────────────

def _barnacle(surf, cx, cy, r):
    """A pale conical barnacle: a stacked volcano-ring of calcified bone-crust
    with a dark open maw, rim-lit top-left so the flesh tone catches light on a
    dark sky. Reads as a fused shell cluster, not a flat dot."""
    pygame.draw.ellipse(surf, FLESH_DKR, (cx - r, cy - r + r // 3, r * 2, r * 2 - r // 2))
    pygame.draw.circle(surf, FLESH_DK, (cx, cy), r)
    pygame.draw.circle(surf, FLESH, (cx, cy), max(1, r - 1))
    pygame.draw.arc(surf, FLESH_HI,
                    (cx - r + 1, cy - r + 1, r * 2 - 2, r * 2 - 2),
                    0.5, 2.3, max(1, r // 3))
    pygame.draw.circle(surf, ABYSS_DKR, (cx, cy), max(1, r - 2))  # open maw


def _lure(surf, cx, cy, r, pulse=1.0, hero=False, dim=False):
    """A single bioluminescent lure-bulb: jade core + layered additive halo.
    `pulse` scales the outer bloom so a column reads as a living, breathing
    chain. The jade hierarchy is collapsed for 1×: `hero` is the ONE dominant
    focal and `dim` is a demoted flank pinprick (no hot core, weak halo) so only
    the esca + eye command the eye at phone scale.

    Round-2 correction: the esca's halo is the DOMINANT focal by INTENSITY (a
    hot near-white core), NOT by sprawling area. At 1× an oversized bloom became
    a glowing 'headlight' that swallowed the whole jaw/eye silhouette, so the
    halo radius is capped — a tight bright point that draws the eye without
    washing out the dark menace shape behind it."""
    if dim:
        _glow(surf, cx, cy, int(r * 2.6 * pulse), JADE, alpha=30)
        pygame.draw.circle(surf, JADE_DIM, (cx, cy), r + 1)
        pygame.draw.circle(surf, JADE, (cx, cy), max(1, r))
        return
    if hero:
        # capped tight halo: dominant by heat, never an area-wash at 1×
        halo_r = min(int(r * 3.4 * pulse), r + 14)
        _glow(surf, cx, cy, halo_r, JADE, alpha=120)
        _glow(surf, cx, cy, int(r * 1.9), JADE_PALE, alpha=150)
    else:
        _glow(surf, cx, cy, int(r * 3.2 * pulse), JADE, alpha=60)
        _glow(surf, cx, cy, int(r * 2.0), JADE_PALE, alpha=90)
    pygame.draw.circle(surf, JADE_DIM, (cx, cy), r + 1)
    pygame.draw.circle(surf, JADE, (cx, cy), r)
    pygame.draw.circle(surf, JADE_PALE, (cx - max(1, r // 3), cy - max(1, r // 3)),
                       max(1, r // 2))


# ── THE CREATURE ─────────────────────────────────────────────────────────────

def _jagged_maw_glow(surf, cx, cy, w, h, color, alpha, teeth):
    """A DOWNWARD-pointing sawtooth jade glow filling the open maw. Round 1's
    soft belly crescent read as a SMILE at 1× and made the whole thing cute;
    this is a jagged ramp whose spikes point DOWN so the lit throat reinforces
    the interlocking fangs instead of a friendly grin. The top edge is FLAT (no
    upward curve) — a curved upper edge is what would re-introduce a grin."""
    pts = [(cx - w, cy - h)]
    n = max(3, teeth)
    for i in range(n + 1):
        tx = cx - w + (2 * w) * i / n
        # alternate the lower edge into hard down-pointing spikes
        ty = cy + (h if i % 2 else h * 0.18)
        pts.append((int(tx), int(ty)))
    pts.append((cx + w, cy - h))
    g = pygame.Surface((int(w * 2 + 4), int(h * 2 + 4)), pygame.SRCALPHA)
    off = (-(cx - w) + 2, -(cy - h) + 2)
    pygame.draw.polygon(g, (*color, alpha),
                        [(p[0] + off[0], p[1] + off[1]) for p in pts])
    surf.blit(g, (cx - w - 2, cy - h - 2), special_flags=pygame.BLEND_ADD)


def draw_leviathan(surf, cx, base_y, scale=1.0, t=0.0):
    """The abyssal whale-GOD, facing left, hauling itself onto the ground line at
    `base_y`. Built bottom-heavy: a vast wet rounded dome of abyss-mass slung
    low, with a lower JAW that juts forward and down PAST the body outline so the
    blackout silhouette reads 'snapping jaw' (not egg) at phone scale; raked,
    uneven dorsal flukes (never upright 'ears'); a sunken dead-jade slit eye; and
    ONE dominant esca-lure as the focal. Bulk + bioluminescence, never cute."""
    s = scale

    # — drowned-world drip: stranded under-belly tendrils trailing to the ground
    #   (drawn FIRST so the body mass overlaps and roots them). —
    for i in range(7):
        dx = cx - int(70 * s) + int(i * 24 * s)
        dy0 = base_y - int(2 * s)
        wob = int(math.sin(i * 1.3 + t) * 5 * s)
        pygame.draw.line(surf, ABYSS_DKR,
                         (dx, base_y - int(58 * s)), (dx + wob, dy0),
                         max(1, int(3 * s)))
        pygame.draw.circle(surf, ABYSS_DK, (dx + wob, dy0), max(1, int(2 * s)))

    # — looming wet dome of body-mass (the only blob in the set) —
    body_rw = int(96 * s)
    body_rh = int(70 * s)
    bx = cx + int(16 * s)
    by = base_y - int(52 * s)
    _wet_dome(surf, bx, by, body_rw, body_rh)

    # — RAKED, asymmetric dorsal flukes (note 3). Round 1's near-symmetric upright
    #   pair read as cute rabbit-"ears". These now sweep hard BACK toward the tail
    #   (positive x, away from the left-facing head) and are deliberately uneven:
    #   a tall hooked rear fluke and a shorter mid one, both leaning the same way
    #   so the crown silhouette rakes like a shark's, never two perky ears. —
    for base_ox, root_w, lean, tip_h in (
            (40, 22, 64, 70),    # rear fluke: tall, raked far back
            (8, 16, 40, 44)):    # mid fluke: shorter, same back-lean
        fx = bx + int(base_ox * s)
        fy = by - int(46 * s)
        pygame.draw.polygon(surf, ABYSS_DKR, [
            (fx, fy + int(8 * s)),                               # front root
            (fx + int(root_w * s), fy + int(10 * s)),            # rear root
            (fx + int(lean * s), fy - int(tip_h * s)),           # raked-back tip
        ])
        # concave trailing edge: a thin shade slice gives the hook its curl
        pygame.draw.polygon(surf, ABYSS, [
            (fx + int(root_w * 0.55 * s), fy + int(8 * s)),
            (fx + int(lean * s), fy - int(tip_h * s)),
            (fx + int((lean - 10) * s), fy - int(tip_h * 0.45 * s)),
        ])

    # — barnacle reef riding the back, like crust on a drowned hull —
    for (ox, oy, r) in (
            (-58, -56, 7), (-30, -70, 9), (2, -76, 8),
            (34, -70, 7), (58, -52, 6), (-14, -50, 5), (22, -54, 5)):
        _barnacle(surf, bx + int(ox * s), by + int(oy * s), max(2, int(r * s)))

    # — HEAD / underbite jaw (faces LEFT). This is where 'mean' lives. The head is
    #   built large + thrust forward so it commands the silhouette at 1×. —
    hx = bx - int(78 * s)
    hy = by + int(26 * s)

    # Upper snout (recessed, blunt) — the RECESS is what makes the under-jaw mean.
    snout = [
        (hx + int(52 * s), hy - int(26 * s)),
        (hx - int(30 * s), hy - int(18 * s)),
        (hx - int(20 * s), hy + int(2 * s)),
        (hx + int(50 * s), hy + int(4 * s)),
    ]
    pygame.draw.polygon(surf, ABYSS_DK, snout)
    pygame.draw.polygon(surf, ABYSS,
                        [(p[0] + 2, p[1] + 1) for p in snout[:3]] + [snout[3]])

    # Black gaping maw between the jaws — the cavernous throat.
    pygame.draw.polygon(surf, ABYSS_DKR, [
        (hx + int(44 * s), hy - int(6 * s)),
        (hx - int(40 * s), hy - int(6 * s)),
        (hx - int(58 * s), hy + int(26 * s)),
        (hx + int(40 * s), hy + int(22 * s)),
    ])

    # Lower JAW (note 2 — the 1× menace). A massive bone slab that juts forward
    # AND DOWN, breaking ~20% of body width PAST the body outline to the left and
    # well below it, so the BLACKOUT silhouette reads 'snapping jaw', never an
    # egg. The tip is a hard angular point, not a rounded chin.
    jut = int(body_rw * 0.20)
    jaw = [
        (hx + int(48 * s), hy + int(16 * s)),                  # hinge under body
        (hx + int(44 * s), hy + int(48 * s)),                  # dropped down
        (hx - int(30 * s), hy + int(62 * s)),                  # low jaw floor
        (hx - int(64 * s) - jut, hy + int(46 * s)),            # forward+down jut tip
        (hx - int(52 * s) - jut // 2, hy + int(16 * s)),       # gum line forward
        (hx - int(24 * s), hy + int(20 * s)),
    ]
    pygame.draw.polygon(surf, ABYSS_DK, jaw)
    pygame.draw.polygon(surf, ABYSS,
                        [(p[0], p[1] + 2) for p in jaw])
    # A chin highlight ridge so the slab reads as forward, heavy bone in blackout.
    pygame.draw.line(surf, ABYSS_RIM,
                     (hx - int(64 * s) - jut, hy + int(46 * s)),
                     (hx - int(10 * s), hy + int(42 * s)), max(1, int(2 * s)))

    # — JAGGED jade maw-glow inside the open throat (note 1): a down-pointing
    #   sawtooth, NOT a curved grin. Kept low-saturation so it backlights the
    #   fangs without competing with the single esca focal. —
    mw = int(46 * s)
    mcx = hx - int(8 * s)
    mcy = hy + int(6 * s)
    _jagged_maw_glow(surf, mcx, mcy, mw, int(22 * s), JADE,
                     int(58 + 16 * math.sin(t * 2.2)), teeth=7)

    # — interlocking barnacle FANGS ringing the maw: the underbite's teeth. The
    #   lower row juts UP from the heavy forward jaw; the upper row drops from the
    #   snout, and they interlock like a deep-sea gulper's trap. —
    n_low = 9
    for i in range(n_low):
        tt = i / (n_low - 1)
        lx = hx + int((42 - 104 * tt) * s)
        ly = hy + int((16 + 16 * tt) * s)
        th = int((14 + 5 * math.sin(tt * math.pi)) * s)
        pygame.draw.polygon(surf, FLESH_DK, [
            (lx - int(4 * s), ly + int(2 * s)), (lx + int(4 * s), ly + int(2 * s)),
            (lx, ly - th)])
        pygame.draw.polygon(surf, FLESH, [
            (lx - int(3 * s), ly + int(1 * s)), (lx + int(2 * s), ly + int(1 * s)),
            (lx, ly - th + int(1 * s))])
        pygame.draw.line(surf, FLESH_HI, (lx - int(1 * s), ly),
                         (lx, ly - th + int(2 * s)), max(1, int(s)))
    n_up = 6
    for i in range(n_up):
        tt = i / (n_up - 1)
        ux = hx + int((34 - 66 * tt) * s)
        uy = hy - int((6 + 1 * tt) * s)
        th = int((10 + 3 * math.sin(tt * math.pi)) * s)
        pygame.draw.polygon(surf, FLESH_DK, [
            (ux - int(3 * s), uy - int(1 * s)), (ux + int(3 * s), uy - int(1 * s)),
            (ux, uy + th)])
        pygame.draw.polygon(surf, FLESH, [
            (ux - int(2 * s), uy - int(1 * s)), (ux + int(2 * s), uy - int(1 * s)),
            (ux, uy + th - int(1 * s))])

    # — sunken dead-jade eye with a vertical predator slit, set DEEP in a socket
    #   under a heavy bony brow ridge. The SECOND focal — sized + lit below the
    #   esca so the lure stays dominant. Small + cold, never a friendly disc. —
    ex, ey = hx + int(20 * s), hy - int(34 * s)
    pygame.draw.ellipse(surf, ABYSS_DKR,
                        (ex - int(16 * s), ey - int(12 * s), int(32 * s), int(24 * s)))
    _glow(surf, ex, ey, int(9 * s), JADE, alpha=52)
    pygame.draw.circle(surf, JADE_DIM, (ex, ey), int(7 * s))
    pygame.draw.circle(surf, JADE, (ex, ey), int(5 * s))
    pygame.draw.ellipse(surf, ABYSS_DKR,
                        (ex - int(2 * s), ey - int(6 * s), max(2, int(3 * s)), int(12 * s)))
    pygame.draw.circle(surf, JADE_PALE,
                       (ex - int(2 * s), ey - int(2 * s)), max(1, int(2 * s)))
    # Heavy hooded brow ridge angled DOWN toward the snout — a permanent glower.
    pygame.draw.polygon(surf, ABYSS_DKR, [
        (ex - int(20 * s), ey - int(6 * s)),
        (ex + int(22 * s), ey - int(14 * s)),
        (ex + int(24 * s), ey - int(6 * s)),
        (ex - int(18 * s), ey + int(2 * s)),
    ])
    pygame.draw.line(surf, ABYSS_RIM,
                     (ex - int(18 * s), ey - int(6 * s)),
                     (ex + int(22 * s), ey - int(13 * s)), max(1, int(2 * s)))

    # — the ESCA: the SINGLE DOMINANT focal (note 4). A long forehead lure-stalk
    #   rooting between the brows and arcing FORWARD over the snout so its big
    #   bright bulb dangles out in front of the maw — the brightest + largest jade
    #   in the whole piece, so the eye lands here first at 1×. —
    sx, sy = ex + int(20 * s), ey - int(20 * s)
    stalk = []
    for k in range(16):
        kt = k / 15
        wob = math.sin(kt * 2.4 + t * 2.0) * 5 * kt
        px = sx - int((104 * kt + wob) * s)
        py = sy - int(math.sin(kt * math.pi * 0.45) * 30 * s) + int(76 * kt * kt * s)
        stalk.append((px, py))
    pygame.draw.lines(surf, JADE_DIM, False, stalk, max(1, int(3 * s)))
    pygame.draw.lines(surf, JADE, False, stalk, max(1, int(s)))
    tip = stalk[-1]
    _lure(surf, tip[0], tip[1], max(4, int(8 * s)),
          pulse=0.95 + 0.35 * math.sin(t * 2.5), hero=True)

    # — flank lures DEMOTED to ~50% size/brightness (note 4): faint pinpricks
    #   subordinate to the esca + eye, never a field of equal "measles" at 1×.
    #   Two only, low on the dark under-mass. —
    for i, (ox, oy, r) in enumerate(((-46, 24, 2), (18, 34, 2))):
        _lure(surf, bx + int(ox * s), by + int(oy * s), max(1, int(r * s)),
              pulse=0.55 + 0.2 * math.sin(t * 1.7 + i), dim=True)


# ── PROP → PILLAR: chain-of-lure-stalks ──────────────────────────────────────

def draw_lure_column(surf, x, y_top, y_bot, t=0.0):
    """A vertical OPAQUE barnacled bone-spine studded with a RHYTHMIC stack of
    caged jade nodes. This is the signature prop AND the obstacle pillar.

    Round-3 final fix — WALL FIRST, nodes second (AD blackout test). Round 2's
    spine was too narrow + too dark, so at 1× only the bright round jade discs
    popped and read as a string of collectible coins floating in the gap. Now:
      * the column is the WIDEST, PALEST, MOST-PRESENT mass on screen — a
        full-bleed pale-flesh bone wall with hard rim edges that survives the
        blackout test as a SOLID BAR (not a dotted line) on either sky;
      * each jade node is RECESSED deep into the bone behind a hard pale rib-cage
        BRACKET — visible vertical bars cross the glow, and the node itself is
        dimmer + desaturated below the esca, so it reads 'caged fixture embedded
        in a wall', never a floating pickup;
      * the node is read by SHAPE as much as value: a bracketed/barred socket,
        angular-framed — so a colorblind player still sees 'structure, not loot'
        where coins/esca are clean glowing circles.
    The straight central spine + symmetric placement is what mirrors cleanly:
    flip top-to-bottom and the caged nodes still face the gap."""
    h = y_bot - y_top
    seg = max(40, h // 5)
    half = 22   # WIDE: the column must read as the brightest solid mass at 1×

    # Opaque bone wall: a hard-edged column with a value ramp across its width
    # (dark left occlusion → mid shade → broad PALE body → rim-lit right edge) so
    # it reads as a rounded, fully solid WALL. The pale body is the dominant mass
    # — brighter than any node — so the blackout silhouette is a solid bar.
    pygame.draw.rect(surf, ABYSS_DKR, (x - half - 2, y_top, half * 2 + 4, h))
    pygame.draw.rect(surf, FLESH_DKR, (x - half, y_top, half * 2, h))
    pygame.draw.rect(surf, FLESH_DK, (x - half + 3, y_top, half * 2 - 7, h))
    pygame.draw.rect(surf, FLESH, (x - half + 6, y_top, int(half * 1.3), h))
    pygame.draw.rect(surf, FLESH_HI, (x - half + 6, y_top, 4, h))  # hard rim edge
    pygame.draw.line(surf, FLESH_DKR, (x + half - half // 3, y_top),
                     (x + half - half // 3, y_bot), 3)   # right-face core shade
    pygame.draw.line(surf, ABYSS_DKR, (x + half - 1, y_top),
                     (x + half - 1, y_bot), 2)            # hard occluded edge

    # Calcified vertebra joints banding the FULL width at a tight rhythm — the
    # wall reads as fused, segmented bone, never a smooth pipe or a thin stalk.
    yy = y_top
    while yy < y_bot:
        pygame.draw.line(surf, FLESH_DKR, (x - half, yy), (x + half, yy), 3)
        pygame.draw.line(surf, FLESH_HI, (x - half + 4, yy - 2),
                         (x + half - 4, yy - 2), 1)
        yy += seg // 2

    # Caged jade nodes at a fixed rhythm. Each node is RECESSED into a square
    # bone socket and shut behind hard pale BARS — bracket above/below + two
    # vertical jail bars across the glow — so it reads as a barred fixture set
    # INTO the wall. The jade is dim + desaturated (JADE_DIM core, no hot pale
    # centre) so pillar-jade can never be mistaken for coin/esca-jade.
    node = 0
    yy = y_top + seg // 2
    while yy < y_bot - 10:
        # deep square recess cut into the bone — angular, never a round coin well
        pygame.draw.rect(surf, FLESH_DK, (x - 11, yy - 11, 22, 22))
        pygame.draw.rect(surf, ABYSS_DKR, (x - 9, yy - 9, 18, 18))
        # contained, low glow — dimmer than the esca, kept inside the socket
        pulse = 0.7 + 0.2 * math.sin(t * 2 + node)
        _glow(surf, x, yy, int(9 * pulse), JADE_DIM, alpha=46)
        pygame.draw.rect(surf, JADE_DIM, (x - 6, yy - 6, 12, 12))
        pygame.draw.rect(surf, _lerp(JADE_DIM, JADE, 0.5), (x - 4, yy - 4, 8, 8))
        # CAGE: a hard pale bone frame + bracket lip top & bottom + two vertical
        # jail BARS crossing the glow → unmistakably 'barred socket', not a bulb.
        pygame.draw.rect(surf, FLESH_HI, (x - 11, yy - 11, 22, 22), 2)
        pygame.draw.line(surf, FLESH, (x - 11, yy - 9), (x + 11, yy - 9), 2)
        pygame.draw.line(surf, FLESH, (x - 11, yy + 9), (x + 11, yy + 9), 2)
        pygame.draw.line(surf, FLESH_HI, (x - 4, yy - 11), (x - 4, yy + 11), 2)
        pygame.draw.line(surf, FLESH_HI, (x + 4, yy - 11), (x + 4, yy + 11), 2)
        node += 1
        yy += seg


def render_pillar_pair(w, gap_top, gap_bot, total_h, t=0.0):
    """Build a top + bottom obstacle pillar from ONE column builder, proving the
    prop mirrors. The bottom pillar is drawn head-up; the top is the SAME
    surface flipped vertically — the abyss convention. Caged nodes always face
    the gap because the spine is symmetric."""
    col_w = w
    bot = pygame.Surface((col_w, total_h - gap_bot), pygame.SRCALPHA)
    draw_lure_column(bot, col_w // 2, 0, bot.get_height(), t=t)
    top_src = pygame.Surface((col_w, gap_top), pygame.SRCALPHA)
    draw_lure_column(top_src, col_w // 2, 0, top_src.get_height(), t=t)
    top = pygame.transform.flip(top_src, False, True)
    return top, bot


# ── compose review sheet ──────────────────────────────────────────────────────

def main():
    pygame.init()
    big = pygame.font.SysFont("dejavusans", 19, bold=True)
    med = pygame.font.SysFont("dejavusans", 15, bold=True)
    small = pygame.font.SysFont("dejavusans", 13)
    tiny = pygame.font.SysFont("dejavusans", 11)

    # ── TOP: day/night full-scale hero panels (unchanged layout) ──────────────
    W = 820
    H = 560
    panel_w = W // 2
    ground_y = 460
    body = pygame.Surface((W, H))
    for i, (bg, label) in enumerate(((DAY_BG, "DAY SKY"), (NIGHT_BG, "NIGHT SKY"))):
        px = i * panel_w
        panel = pygame.Surface((panel_w, H))
        _vgrad(panel, (0, 0, panel_w, H), bg[0], bg[1])
        _vgrad(panel, (0, ground_y, panel_w, H - ground_y), ABYSS_DK, (5, 8, 16))
        pygame.draw.line(panel, JADE_DIM, (0, ground_y), (panel_w, ground_y), 2)
        draw_leviathan(panel, panel_w // 2 - 6, ground_y, scale=1.35, t=0.7)
        body.blit(panel, (px, 0))
        body.blit(big.render(label, True, JADE), (px + 16, 12))
    pygame.draw.line(body, (6, 8, 16), (panel_w, 0), (panel_w, H), 2)

    # ── MIDDLE: the MANDATORY 1× insets — the only test that matters now ──────
    #   The creature drawn at scale=1.0 on BOTH skies + the pillar at 1× against
    #   a scrolling sky, each on its own swatch with a 'shrunk to phone' caption.
    mid_h = 300
    mid = pygame.Surface((W, mid_h))
    _vgrad(mid, (0, 0, W, mid_h), (14, 18, 30), (24, 30, 46))
    mid.blit(med.render("1× AT-SCALE — the downscale test "
                        "(does it stay MEAN, does the pillar read WALL?)",
                        True, FLESH_HI), (16, 10))

    # three 1× swatches across the strip
    sw_w, sw_h = 250, 230
    sw_y = 46
    cap_y = sw_y + sw_h + 4
    swatches = [
        ("creature · DAY", DAY_BG, "creature"),
        ("creature · NIGHT", NIGHT_BG, "creature"),
        ("pillar · scrolling sky", NIGHT_BG, "pillar"),
    ]
    for j, (cap, bg, kind) in enumerate(swatches):
        sx = 16 + j * (sw_w + 14)
        sw = pygame.Surface((sw_w, sw_h))
        _vgrad(sw, (0, 0, sw_w, sw_h), bg[0], bg[1])
        if kind == "creature":
            g_y = sw_h - 30
            _vgrad(sw, (0, g_y, sw_w, sw_h - g_y), ABYSS_DK, (5, 8, 16))
            pygame.draw.line(sw, JADE_DIM, (0, g_y), (sw_w, g_y), 1)
            # scale 1.0 → exactly phone size; centred so the silhouette is judged
            draw_leviathan(sw, sw_w // 2 + 30, g_y, scale=1.0, t=0.7)
        else:
            # faint ambient sky bands to stand in for a scroll, then a 1× pillar
            for band in range(0, sw_w, 26):
                pygame.draw.line(sw, _lerp(bg[0], bg[1], 0.5),
                                 (band, 0), (band - 18, sw_h), 1)
            top, bot = render_pillar_pair(64, 70, 118, sw_h, t=0.4)
            ptx = sw_w // 2 - 32
            sw.blit(top, (ptx, 0))
            sw.blit(bot, (ptx, 118))
            sw.blit(tiny.render("GAP", True, JADE), (ptx + 8, 90))
        mid.blit(sw, (sx, sw_y))
        pygame.draw.rect(mid, (8, 10, 18), (sx, sw_y, sw_w, sw_h), 1)
        mid.blit(small.render(cap, True, JADE), (sx, cap_y))

    # ── BOTTOM: pillar-fit mirror proof + prop rationale ──────────────────────
    strip_h = 210
    th = pygame.Surface((W, strip_h))
    _vgrad(th, (0, 0, W, strip_h), (12, 16, 28), (22, 28, 44))
    col_w = 96
    gap_top, gap_bot = 78, 132
    top, bot = render_pillar_pair(col_w, gap_top, gap_bot, strip_h, t=0.4)
    tx = 70
    th.blit(top, (tx, 0))
    th.blit(bot, (tx, gap_bot))
    for gy in (gap_top, gap_bot):
        pygame.draw.line(th, JADE, (tx - 12, gy), (tx + col_w + 12, gy), 1)
    th.blit(small.render("GAP", True, JADE), (tx + col_w // 2 - 14,
                                              (gap_top + gap_bot) // 2 - 8))
    cx = tx + col_w + 50
    th.blit(big.render("PILLAR-FIT", True, FLESH_HI), (cx, 16))
    lines = [
        "WIDE OPAQUE pale bone WALL first — brightest solid mass, hard",
        "rim edges, full-bleed; passes the blackout SOLID-BAR test.",
        "Jade nodes RECESSED behind a square bone bracket + jail BARS,",
        "dim + desaturated → barred fixture by SHAPE, never a coin.",
        "",
        "TOP pillar = the SAME surface flipped vertically",
        "(top = flip(bottom)); caged nodes face the GAP because the",
        "spine is symmetric. A barbed harpoon TIP could not mirror.",
    ]
    for k, ln in enumerate(lines):
        col = JADE if ln.startswith("TOP") else FLESH
        th.blit(small.render(ln, True, col), (cx, 46 + k * 19))

    # ── title band + assemble ─────────────────────────────────────────────────
    band_h = 48
    final = pygame.Surface((W, band_h + H + mid_h + strip_h))
    band = pygame.Surface((W, band_h))
    band.fill((8, 10, 18))
    band.blit(big.render("deep-leviathan  —  round 3  —  abyssal whale-GOD",
                         True, (235, 240, 245)), (12, 6))
    band.blit(small.render("creature LOCKED  ·  PILLAR-ONLY pass: wide pale bone "
                           "WALL first, jade nodes recessed behind barred sockets "
                           "(no coin-read)",
                           True, JADE), (12, 29))
    final.blit(band, (0, 0))
    final.blit(body, (0, band_h))
    final.blit(mid, (0, band_h + H))
    final.blit(th, (0, band_h + H + mid_h))

    dst = os.path.join(os.path.dirname(__file__), "..",
                       "docs", "epic_boss", "deep-leviathan", "round_3.png")
    dst = os.path.abspath(dst)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    pygame.image.save(final, dst)
    print("saved", dst)


if __name__ == "__main__":
    main()
