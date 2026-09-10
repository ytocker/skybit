"""
Round-1 concept renderer for ROSE-GOLD PRINCE — the boy-prince, the CUTE pole
of the KING SKULL royal brood (Batch 2 / skull_kings, concept #6). Headless
Pygame; ELEVATED pipeline (supersample SS=6 -> smoothscale) so the dainty
coronet + tiny accents stay crisp at downscale. Keeps the shipped house grammar
cloned from jiangshi_epic/citipati: flat saturated fills, hard 1-2px ink keyline
(28,22,30), dark-core -> flat-fill -> top-left rim-sheen triad, 1px alpha-grown
outline, chibi proportions, scary-CUTE; procedural-only (no gradients/PNGs).

WHY this concept is the cute pole: the brood's other five kings are TALL or WIDE
or RADIAL masses. The prince is the ONLY small/round silhouette — a compact
"egg-on-legs" heir, the gentlest of the six. He is the sole pink king (palest
bone + rose-gold + soft pink), staying clear of KFC red entirely.

WHY the crown + posture are policed hard: a tiny round king risks reading as a
COIN / power-up PICKUP at 32px (the AD's stated worry). The defence is a
SILHOUETTE that a coin can never own — a dainty OPEN trefoil coronet that adds
clear vertical HEIGHT above a round head, a flared royal CAPE-COLLAR that breaks
the circle into shoulders, and a tiny orb-sceptre held to one side. Round + tall
crown + side-staff = unmistakably a tiny KING, never a symmetric disc.

WHY a standalone script under docs/: review art must never enter the shipped
bundle, so it reuses only colour math + the triad/outline helpers, not runtime
sprite modules.
"""
import math
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
pygame.init()

# -- PINNED PALETTE (locked brief sec.6) --------------------------------------
# Palest bone is the dominant MASS; rose-gold is a thin metal edge/coronet
# accent; soft pink is the gem + cape lining sliver. NO KFC red anywhere.
BONE      = (250, 244, 236)   # palest bone — the dominant fill (egg body + head)
BONE_D    = (214, 202, 196)   # bone dark-core / cheek + body shade
BONE_DD   = (168, 154, 150)   # deepest bone hollow (sockets, seams)
BONE_SH   = (255, 252, 248)   # bone top-left rim-sheen (near-white)
ROSE      = (214, 150, 122)   # rose-gold — the coronet metal + collar trim
ROSE_BR   = (240, 192, 168)   # rose-gold highlight
ROSE_D    = (168, 110,  86)   # rose-gold shade / keyline-warm
PINK      = (244, 168, 192)   # soft pink — cape lining + cheek blush sliver
PINK_BR   = (255, 214, 228)   # soft pink highlight
PINK_D    = (206, 120, 152)   # soft pink shade
TOURM     = (236, 104, 156)   # pink tourmaline gem — the single bright focal
TOURM_BR  = (255, 188, 218)   # tourmaline hot core (the single brightest pixel)
TOURM_D   = (176,  62, 110)
INK       = ( 28,  22,  30)   # hard ink keyline
SOCKET    = (122,  92, 110)   # warm-mauve socket glow (scary-cute, not black)
SOCKET_BR = (196, 150, 178)

BG        = ( 96, 100, 108)   # neutral grey review backdrop
PANEL     = ( 74,  78,  88)
DAY_SKY_T = (120, 196, 236)   # day biome sky (top)
DAY_SKY_B = (196, 232, 244)
NIGHT_T   = ( 22,  26,  54)   # night biome sky (top)
NIGHT_B   = ( 48,  44,  82)
BLACKOUT  = ( 18,  18,  22)   # silhouette-proof backdrop
LABEL     = (238, 240, 244)
LABEL_DIM = (188, 196, 208)


def lerp(a, b, t):
    t = max(0.0, min(1.0, t))
    return (int(a[0] + (b[0]-a[0])*t),
            int(a[1] + (b[1]-a[1])*t),
            int(a[2] + (b[2]-a[2])*t))


# -- outline grown from the alpha mask (the house keyline) --------------------
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


def triad_blob(surf, color, pts, sheen_pts=None, core_pts=None, outline=True, ow=2):
    """Flat fill + optional dark-core + top-left rim-sheen + ink keyline."""
    if outline:
        pygame.draw.polygon(surf, INK, pts)
    pygame.draw.polygon(surf, color, pts)
    if core_pts:
        pygame.draw.polygon(surf, lerp(color, INK, 0.34), core_pts)
    if sheen_pts:
        pygame.draw.polygon(surf, lerp(color, (255, 255, 255), 0.5), sheen_pts)
    if outline:
        pygame.draw.polygon(surf, INK, pts, ow)


def triad_circle(surf, color, c, r, ow=2, sheen=True, core=True):
    """Round equivalent of triad_blob — dark core bottom-right, sheen top-left."""
    pygame.draw.circle(surf, INK, c, r + max(1, ow // 2))
    pygame.draw.circle(surf, color, c, r)
    if core:
        pygame.draw.circle(surf, lerp(color, INK, 0.28),
                           (c[0] + int(r * 0.28), c[1] + int(r * 0.30)),
                           int(r * 0.74))
        pygame.draw.circle(surf, color, c, int(r * 0.80))
    if sheen:
        # WHY softer than pure white: the pink gem must be the brightest thing at
        # 32px, so the big bone masses keep a pearly (not near-white) sheen and
        # cede the top of the value range to the tourmaline's hot core.
        pygame.draw.circle(surf, lerp(color, (255, 255, 255), 0.30),
                           (c[0] - int(r * 0.38), c[1] - int(r * 0.40)),
                           max(1, int(r * 0.26)))
    pygame.draw.circle(surf, INK, c, r, ow)


def faceted_gem(surf, cx, cy, r, base, brt, dk, s, hot=False):
    """A small kite/round-cut tourmaline — the single brightest accent. Faceted
    so it reads as a JEWEL (royal), not a flat dot that could be a coin pip.

    WHY `hot`: at 32px the EYE must land on the pink gem, not the bone face — so
    the hero/cap stone gets a punchy near-white table facet + a 1px hot specular
    core that survives the downscale as the single brightest pixel on the sheet."""
    kite = [(cx, cy - r), (cx + int(r * 0.78), cy),
            (cx, cy + int(r * 1.05)), (cx - int(r * 0.78), cy)]
    pygame.draw.polygon(surf, INK, kite)
    pygame.draw.polygon(surf, base, kite)
    # table facet (upper-left) catches the light — punched brighter when hot
    table_col = lerp(brt, (255, 255, 255), 0.35) if hot else brt
    pygame.draw.polygon(surf, table_col, [(cx, cy - r),
                                    (cx + int(r * 0.40), cy - int(r * 0.10)),
                                    (cx, cy + int(r * 0.10)),
                                    (cx - int(r * 0.40), cy - int(r * 0.10))])
    # lower pavilion facet shaded
    pygame.draw.polygon(surf, dk, [(cx, cy + int(r * 0.10)),
                                   (cx + int(r * 0.40), cy),
                                   (cx, cy + int(r * 1.05)),
                                   (cx - int(r * 0.40), cy)])
    # specular core — a 1px-native hot dot so the gem wins the 32px attention test
    spec_r = max(1, int(r * (0.30 if hot else 0.16)))
    pygame.draw.circle(surf, (255, 250, 252), (cx - int(r * 0.16), cy - int(r * 0.26)),
                       spec_r)
    if hot:
        pygame.draw.circle(surf, (255, 255, 255), (cx - int(r * 0.16), cy - int(r * 0.26)),
                           max(1, int(r * 0.13)))
    pygame.draw.polygon(surf, INK, kite, max(1, int(1.2 * s)))


# -- the dainty OPEN trefoil coronet (the top tell) ---------------------------
def trefoil_coronet(surf, cx, cy, w, s, gem=True, rim=False):
    """A delicate open coronet: a slim rose-gold circlet band carrying a tall
    CENTRAL fleur SPIKE flanked by two short open loops, the spike set with a
    pink tourmaline. Returns the gem-apex (gx, gy) so the caller can rim-light
    the crown's top edge on night sky.

    WHY a tall central SPIKE (the anti-coin GATE): a trefoil of three EQUAL
    bumps blacks-out as a soft bow/cluster — still a "round pickup". A single
    pointed centre that out-tops the flanks by ~2x makes the blackout SPIKE out
    of the round head: unmistakably a tiny KING, never a disc. Total coronet
    height is now ~18-22% of body height (was ~10-12%).

    WHY OPEN flanks: negative sky shows THROUGH the side loops so the crown
    breaks the head's outline into a spiky-dainty silhouette no coin can mimic."""
    band_h = int(7 * s)
    # circlet band — a slim rose-gold ring across the brow
    band = [(cx - w, cy), (cx + w, cy),
            (cx + int(w * 0.92), cy + band_h), (cx - int(w * 0.92), cy + band_h)]
    triad_blob(surf, ROSE, band,
               sheen_pts=[(cx - w, cy + int(1 * s)), (cx + int(w * 0.2), cy + int(1 * s)),
                          (cx + int(w * 0.2), cy + int(band_h * 0.5)),
                          (cx - w, cy + int(band_h * 0.5))],
               ow=max(1, int(1.4 * s)))
    # tiny rose-gold studs along the band (jewel-setting detail)
    for k in (-1, 0, 1):
        sx = cx + int(k * w * 0.55)
        pygame.draw.circle(surf, ROSE_D, (sx, cy + band_h // 2), max(1, int(1.6 * s)))

    def arch(ax, ar, lift):
        """One OPEN trefoil loop: an ink-keyed rose-gold ANNULUS with sky inside.
        WHY a stroked ring (not fill-then-carve): on an SRCALPHA surface drawing
        a (0,0,0,0) fill BLENDS to nothing and would NOT punch a hole, leaving a
        solid disc that reads as a coin. Stroking a thick ring leaves genuine
        transparent sky inside the loop — the whole anti-coin point of an OPEN
        coronet."""
        ay = cy - lift
        ring_w = max(2, int(3.4 * s))
        # ink keyline ring (slightly fatter), then the rose-gold ring inside it
        pygame.draw.circle(surf, INK, (ax, ay), ar, ring_w + max(1, int(1.2 * s)))
        pygame.draw.circle(surf, ROSE, (ax, ay), ar, ring_w)
        # warm sheen on the upper-left of the ring
        pygame.draw.arc(surf, ROSE_BR,
                        (ax - ar, ay - ar, ar * 2, ar * 2),
                        math.radians(95), math.radians(190), max(1, int(1.6 * s)))

    side_r = int(w * 0.26)
    # flanking open loops — kept SHORT so the centre spike clearly out-tops them
    arch(cx - int(w * 0.66), side_r, int(band_h * 0.3))
    arch(cx + int(w * 0.66), side_r, int(band_h * 0.3))
    # tiny ball finials on the flank loops (royal punctuation)
    for sgn in (-1, 1):
        fx = cx + sgn * int(w * 0.66)
        fy = cy - int(band_h * 0.3) - side_r
        triad_circle(surf, ROSE, (fx, fy), max(2, int(2.6 * s)),
                     ow=max(1, int(1.0 * s)), core=False)

    # === the tall CENTRAL SPIKE — a pointed fleur the height that says KING ====
    # a slim rose-gold triangular spike rising well above the flanks
    spike_h = int(w * 1.30)              # tall: dominates the coronet height
    spike_half = max(2, int(w * 0.24))
    apex_y = cy - spike_h
    spike = [(cx, apex_y),
             (cx + spike_half, cy + int(band_h * 0.2)),
             (cx - spike_half, cy + int(band_h * 0.2))]
    triad_blob(surf, ROSE, spike,
               sheen_pts=[(cx, apex_y + int(spike_h * 0.06)),
                          (cx + int(spike_half * 0.45), cy - int(spike_h * 0.20)),
                          (cx - int(spike_half * 0.45), cy - int(spike_h * 0.20))],
               ow=max(1, int(1.4 * s)))
    # a small pointed finial barb just below the apex (fleur tip, royal not coin)
    gx = cx
    gy = apex_y + int(w * 0.30)
    if gem:
        # the tourmaline rides the spike near its top — sized large enough that
        # its hot specular survives the 32px downscale as the single brightest dot
        faceted_gem(surf, gx, gy, int(w * 0.52),
                    TOURM, TOURM_BR, TOURM_D, s, hot=True)
    if rim:
        # cool/rose-gold rim-light along the SPIKE's top-left edges so the crown
        # separates from a dark night sky (the Obsidian/Koschei night-rim lesson)
        rim_col = (255, 226, 232)
        rw = max(1, int(1.6 * s))
        pygame.draw.line(surf, rim_col, (cx, apex_y),
                         (cx - spike_half, cy + int(band_h * 0.2)), rw)
        pygame.draw.line(surf, rim_col, (cx, apex_y),
                         (cx + int(spike_half * 0.5), cy - int(spike_h * 0.4)), rw)
        # nick the flank loop tops too, so the whole coronet top edge glows
        for sgn in (-1, 1):
            fx = cx + sgn * int(w * 0.66)
            fcy = cy - int(band_h * 0.3)
            pygame.draw.arc(surf, rim_col,
                            (fx - side_r, fcy - side_r, side_r * 2, side_r * 2),
                            math.radians(100), math.radians(180), rw)
    return (gx, apex_y)


# -- a single tiny skull (lineage tell — perched on the band as a held toy) ---
def tiny_skull(surf, cx, cy, r, s):
    """A tiny bone skull charm — domed cranium, two mauve socket dots, stub jaw.
    The brood's lineage tell, kept charm-sized so the prince stays gentle."""
    triad_circle(surf, BONE, (cx, cy), r, ow=max(1, int(1.2 * s)), core=False)
    jaw = [(cx - int(r * 0.5), cy + int(r * 0.5)),
           (cx + int(r * 0.5), cy + int(r * 0.5)),
           (cx + int(r * 0.32), cy + int(r * 0.98)),
           (cx - int(r * 0.32), cy + int(r * 0.98))]
    triad_blob(surf, BONE, jaw, ow=max(1, int(1.0 * s)))
    for ex in (cx - int(r * 0.38), cx + int(r * 0.38)):
        pygame.draw.circle(surf, SOCKET, (ex, cy + int(r * 0.02)), max(1, int(r * 0.22)))
    pygame.draw.circle(surf, INK, (cx, cy + int(r * 0.40)), max(1, int(r * 0.12)))


# -- the boy-prince: compact egg-on-legs --------------------------------------
def draw_prince(surf, cx, cy, s, rim=False):
    """Short round chibi heir. A plump ovoid BODY (the egg) sits on two stubby
    bone legs; a big round skull HEAD sits on top with NO neck (chibi). A flared
    royal CAPE-COLLAR breaks the egg into shoulders; a tiny orb-sceptre is held
    to one side. The dainty open trefoil coronet crowns the head.
    `s` = unit scale around a ~120-unit-tall figure."""

    # vertical anchors — chibi: head ~= body, stubby legs, low centre of mass
    body_cx = cx
    body_cy = cy + int(18 * s)
    body_w = int(34 * s)
    body_h = int(40 * s)
    head_c = (cx, cy - int(26 * s))
    hr = int(25 * s)

    # === CAPE behind the body (drawn first) — a soft royal flare ==============
    # WHY a cape: it widens the bottom silhouette into a regal trapezoid skirt,
    # the single strongest cue that this round thing is a robed monarch, not a
    # coin. Pink lining sliver shows at the parted front hem.
    # WHY wider at the hips: the lower silhouette must read "robed figure", never
    # "disc" — so the cape flares well past the body and is pulled ASYMMETRIC
    # (left hem swung wider) to echo the off-centre orb-sceptre on that side.
    cape = [(body_cx - int(body_w * 0.74), body_cy - int(body_h * 0.30)),
            (body_cx - int(body_w * 1.58), body_cy + int(body_h * 0.78)),
            (body_cx - int(body_w * 0.34), body_cy + int(body_h * 0.90)),
            (body_cx + int(body_w * 0.34), body_cy + int(body_h * 0.90)),
            (body_cx + int(body_w * 1.40), body_cy + int(body_h * 0.74)),
            (body_cx + int(body_w * 0.72), body_cy - int(body_h * 0.30))]
    triad_blob(surf, PINK_D, cape,
               core_pts=[(body_cx - int(body_w * 0.4), body_cy),
                         (body_cx - int(body_w * 1.3), body_cy + int(body_h * 0.74)),
                         (body_cx, body_cy + int(body_h * 0.86)),
                         (body_cx, body_cy)],
               ow=max(1, int(1.6 * s)))
    # rose-gold cape hem trim (thin metal accent along the flared edge)
    hem = [(body_cx - int(body_w * 1.58), body_cy + int(body_h * 0.78)),
           (body_cx - int(body_w * 0.34), body_cy + int(body_h * 0.90)),
           (body_cx + int(body_w * 0.34), body_cy + int(body_h * 0.90)),
           (body_cx + int(body_w * 1.40), body_cy + int(body_h * 0.74))]
    pygame.draw.lines(surf, ROSE, False, hem, max(2, int(3 * s)))
    pygame.draw.lines(surf, ROSE_BR, False, hem[:2], max(1, int(1.4 * s)))

    # === STUBBY LEGS — short little bone legs poking from the egg =============
    leg_th = int(11 * s)
    foot_y = body_cy + int(body_h * 0.86)
    for sgn in (-1, 1):
        lx = body_cx + sgn * int(11 * s)
        hip = (lx, body_cy + int(body_h * 0.34))
        foot = (lx + sgn * int(2 * s), foot_y)
        dx, dy = foot[0] - hip[0], foot[1] - hip[1]
        L = max(1.0, math.hypot(dx, dy))
        nx, ny = -dy / L * leg_th / 2, dx / L * leg_th / 2
        quad = [(hip[0] + nx, hip[1] + ny), (foot[0] + nx, foot[1] + ny),
                (foot[0] - nx, foot[1] - ny), (hip[0] - nx, hip[1] - ny)]
        triad_blob(surf, BONE, quad, ow=max(1, int(1.2 * s)))
        # little bone foot-block
        ft = [(foot[0] - int(7 * s), foot[1] - int(2 * s)),
              (foot[0] + int(9 * s), foot[1] - int(2 * s)),
              (foot[0] + int(8 * s), foot[1] + int(7 * s)),
              (foot[0] - int(7 * s), foot[1] + int(7 * s))]
        triad_blob(surf, BONE, ft, ow=max(1, int(1.2 * s)))

    # === EGG BODY — the plump round torso (the dominant bone mass) ============
    body = [(body_cx - int(body_w * 0.5), body_cy - int(body_h * 0.5)),
            (body_cx + int(body_w * 0.5), body_cy - int(body_h * 0.5)),
            (body_cx + int(body_w * 0.62), body_cy + int(body_h * 0.20)),
            (body_cx + int(body_w * 0.42), body_cy + int(body_h * 0.56)),
            (body_cx - int(body_w * 0.42), body_cy + int(body_h * 0.56)),
            (body_cx - int(body_w * 0.62), body_cy + int(body_h * 0.20))]
    triad_blob(surf, BONE, body,
               core_pts=[(body_cx + int(body_w * 0.05), body_cy - int(body_h * 0.4)),
                         (body_cx + int(body_w * 0.62), body_cy + int(body_h * 0.18)),
                         (body_cx + int(body_w * 0.40), body_cy + int(body_h * 0.54)),
                         (body_cx + int(body_w * 0.05), body_cy + int(body_h * 0.54))],
               sheen_pts=[(body_cx - int(body_w * 0.46), body_cy - int(body_h * 0.42)),
                          (body_cx - int(body_w * 0.06), body_cy - int(body_h * 0.42)),
                          (body_cx - int(body_w * 0.12), body_cy + int(body_h * 0.2)),
                          (body_cx - int(body_w * 0.5), body_cy + int(body_h * 0.1))],
               ow=max(1, int(1.8 * s)))
    # a couple of soft rib seams (keeps the bone read; not a hard ribcage)
    for i in range(2):
        ry = body_cy - int(body_h * 0.18) + i * int(11 * s)
        pygame.draw.arc(surf, BONE_DD,
                        (body_cx - int(body_w * 0.34), ry - int(6 * s),
                         int(body_w * 0.68), int(14 * s)),
                        math.radians(210), math.radians(330), max(1, int(2 * s)))

    # === ROYAL CAPE-COLLAR — a flared rose-gold collar at the shoulders =======
    # WHY the collar: it caps the egg with two raised wings, giving the round
    # body clear SHOULDERS. Round body + winged collar = a robed figure read.
    for sgn in (-1, 1):
        coll = [(body_cx + sgn * int(2 * s), body_cy - int(body_h * 0.52)),
                (body_cx + sgn * int(body_w * 0.74), body_cy - int(body_h * 0.64)),
                (body_cx + sgn * int(body_w * 0.66), body_cy - int(body_h * 0.30)),
                (body_cx + sgn * int(body_w * 0.10), body_cy - int(body_h * 0.34))]
        triad_blob(surf, ROSE, coll,
                   sheen_pts=[(body_cx + sgn * int(4 * s), body_cy - int(body_h * 0.5)),
                              (body_cx + sgn * int(body_w * 0.5), body_cy - int(body_h * 0.58)),
                              (body_cx + sgn * int(body_w * 0.46), body_cy - int(body_h * 0.42)),
                              (body_cx + sgn * int(6 * s), body_cy - int(body_h * 0.4))],
                   ow=max(1, int(1.4 * s)))
        # pink lining sliver inside the collar wing
        pygame.draw.line(surf, PINK,
                         (body_cx + sgn * int(body_w * 0.14), body_cy - int(body_h * 0.36)),
                         (body_cx + sgn * int(body_w * 0.64), body_cy - int(body_h * 0.32)),
                         max(1, int(1.6 * s)))
    # a single tourmaline brooch clasp at the collar throat (small focal echo)
    faceted_gem(surf, body_cx, body_cy - int(body_h * 0.40), int(4.4 * s),
                TOURM, TOURM_BR, TOURM_D, s)

    # === LEFT ARM — clutching a tiny ORB-SCEPTRE to the side ==================
    # WHY off to one side: the held staff is a hard non-coin cue and adds an
    # asymmetric vertical the silhouette test can latch onto at 32px.
    arm_th = int(8 * s)
    sh = (body_cx - int(body_w * 0.46), body_cy - int(body_h * 0.20))
    hand = (body_cx - int(body_w * 0.66), body_cy + int(body_h * 0.10))
    dx, dy = hand[0] - sh[0], hand[1] - sh[1]
    L = max(1.0, math.hypot(dx, dy))
    nx, ny = -dy / L * arm_th / 2, dx / L * arm_th / 2
    armq = [(sh[0] + nx, sh[1] + ny), (hand[0] + nx, hand[1] + ny),
            (hand[0] - nx, hand[1] - ny), (sh[0] - nx, sh[1] - ny)]
    triad_blob(surf, BONE, armq, ow=max(1, int(1.0 * s)))
    triad_circle(surf, BONE, hand, int(5 * s), ow=max(1, int(1.0 * s)), core=False)
    # the sceptre shaft (rose-gold rod) rising from the hand
    sc_top = (hand[0] - int(2 * s), hand[1] - int(body_h * 0.78))
    pygame.draw.line(surf, INK, hand, sc_top, max(2, int(4.4 * s)))
    pygame.draw.line(surf, ROSE, hand, sc_top, max(1, int(2.6 * s)))
    pygame.draw.line(surf, ROSE_BR, (hand[0] - int(1 * s), hand[1] - int(6 * s)),
                     (sc_top[0] - int(1 * s), sc_top[1] + int(6 * s)), max(1, int(1.0 * s)))
    # the ORB finial — a small pink globe with a rose-gold band + cross stud
    orb_c = (sc_top[0], sc_top[1] - int(6 * s))
    orb_r = int(7 * s)
    triad_circle(surf, PINK, orb_c, orb_r, ow=max(1, int(1.2 * s)))
    pygame.draw.line(surf, ROSE, (orb_c[0] - orb_r, orb_c[1]),
                     (orb_c[0] + orb_r, orb_c[1]), max(1, int(1.6 * s)))
    pygame.draw.line(surf, ROSE_BR, (orb_c[0], orb_c[1] - orb_r - int(4 * s)),
                     (orb_c[0], orb_c[1] - orb_r), max(1, int(1.8 * s)))  # cross finial

    # === RIGHT ARM — a tiny hand resting on the belly (gentle, relaxed) =======
    sh2 = (body_cx + int(body_w * 0.46), body_cy - int(body_h * 0.18))
    hand2 = (body_cx + int(body_w * 0.22), body_cy + int(body_h * 0.14))
    dx, dy = hand2[0] - sh2[0], hand2[1] - sh2[1]
    L = max(1.0, math.hypot(dx, dy))
    nx, ny = -dy / L * arm_th / 2, dx / L * arm_th / 2
    armq2 = [(sh2[0] + nx, sh2[1] + ny), (hand2[0] + nx, hand2[1] + ny),
             (hand2[0] - nx, hand2[1] - ny), (sh2[0] - nx, sh2[1] - ny)]
    triad_blob(surf, BONE, armq2, ow=max(1, int(1.0 * s)))
    triad_circle(surf, BONE, hand2, int(5 * s), ow=max(1, int(1.0 * s)), core=False)

    # === SKULL HEAD — big round chibi skull, soft scary-cute =================
    triad_circle(surf, BONE, head_c, hr, ow=max(2, int(2 * s)))
    # rosy cheek blush (the cute tell) — soft pink, kept a faint sliver
    for sgn in (-1, 1):
        pygame.draw.circle(surf, PINK,
                           (head_c[0] + sgn * int(hr * 0.62), head_c[1] + int(hr * 0.30)),
                           max(2, int(hr * 0.20)))
        pygame.draw.circle(surf, PINK_BR,
                           (head_c[0] + sgn * int(hr * 0.62), head_c[1] + int(hr * 0.26)),
                           max(1, int(hr * 0.09)))
    # BIG round sockets (chibi-cute = oversized eyes), warm-mauve glow not black
    for sgn in (-1, 1):
        ex = head_c[0] + sgn * int(hr * 0.42)
        ey = head_c[1] - int(hr * 0.04)
        pygame.draw.circle(surf, INK, (ex, ey), int(hr * 0.34))
        pygame.draw.circle(surf, SOCKET, (ex, ey), int(hr * 0.27))
        pygame.draw.circle(surf, SOCKET_BR, (ex - int(2 * s), ey - int(2 * s)),
                           max(1, int(hr * 0.12)))
        # cool catch-light kept BELOW pure white so the gem stays the brightest
        pygame.draw.circle(surf, (228, 218, 232),
                           (ex - int(3 * s), ey - int(3 * s)), max(1, int(hr * 0.06)))
    # tiny heart-ish nose tick
    pygame.draw.polygon(surf, BONE_DD,
                        [(head_c[0] - int(hr * 0.10), head_c[1] + int(hr * 0.26)),
                         (head_c[0] + int(hr * 0.10), head_c[1] + int(hr * 0.26)),
                         (head_c[0], head_c[1] + int(hr * 0.46))])
    # small gentle grin — a short stitch row, not a fierce maw
    my = head_c[1] + int(hr * 0.62)
    pygame.draw.line(surf, INK, (head_c[0] - int(hr * 0.32), my),
                     (head_c[0] + int(hr * 0.32), my), max(1, int(1.8 * s)))
    for k in range(-2, 3):
        pygame.draw.line(surf, INK, (head_c[0] + int(k * hr * 0.14), my - int(hr * 0.05)),
                         (head_c[0] + int(k * hr * 0.14), my + int(hr * 0.08)),
                         max(1, int(1 * s)))

    # === the OPEN TREFOIL CORONET with tall central spike (the top tell) ======
    crown_w = int(hr * 0.84)
    trefoil_coronet(surf, head_c[0], head_c[1] - int(hr * 0.86), crown_w, s, rim=rim)

    # === a single tiny skull held as a TOY in the right hand (lineage tell) ===
    tiny_skull(surf, hand2[0] + int(2 * s), hand2[1] + int(5 * s), int(5 * s), s)


# -- the prince's forms -> pillar mirror --------------------------------------
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """The prince's regalia IS the pillar: a stacked column of plump rose-gold
    ORB beads (the orb-sceptre globe repeated) threaded on a slim rod = the
    tileable shaft; a single dainty trefoil-coronet ring + pink gem at the gap =
    the creature-derived gap-edge cap. On-axis, symmetric, never top-heavy.

    `cap` names the END that faces the GAP."""
    # central ink rod the beads thread onto
    pygame.draw.rect(surf, INK, (cx - int(3 * s), top, int(6 * s), bot - top))

    bead_pitch = int(22 * s)
    cap_room = int(32 * s)
    if cap == "bottom":
        b0, b1 = top + int(8 * s), bot - cap_room
    else:
        b0, b1 = top + cap_room, bot - int(8 * s)
    y = b0
    while y <= b1:
        # each orb bead: a plump pink globe with a rose-gold equator band
        orb_r = int(14 * s)
        triad_circle(surf, BONE, (cx, y), orb_r, ow=max(1, int(1.4 * s)))
        # rose-gold band across the orb (the regalia metal echo)
        pygame.draw.line(surf, INK, (cx - orb_r, y), (cx + orb_r, y), max(2, int(5 * s)))
        pygame.draw.line(surf, ROSE, (cx - int(orb_r * 0.92), y),
                         (cx + int(orb_r * 0.92), y), max(1, int(3 * s)))
        pygame.draw.line(surf, ROSE_BR, (cx - int(orb_r * 0.7), y - int(1 * s)),
                         (cx - int(orb_r * 0.1), y - int(1 * s)), max(1, int(1.2 * s)))
        # a tiny pink gem at the band centre (focal echo, kept small)
        faceted_gem(surf, cx, y + int(1 * s), int(3.2 * s), TOURM, TOURM_BR, TOURM_D, s)
        y += bead_pitch

    # === gap-edge cap: a trefoil-coronet ring + pink tourmaline ==============
    cap_y = (bot - int(20 * s)) if cap == "bottom" else (top + int(20 * s))
    # a small rose-gold collar ferrule where the cap meets the shaft
    coll_y = (cap_y - int(20 * s)) if cap == "bottom" else (cap_y + int(20 * s))
    pygame.draw.rect(surf, INK, (cx - int(13 * s), coll_y - int(3 * s), int(26 * s), int(8 * s)))
    pygame.draw.rect(surf, ROSE, (cx - int(12 * s), coll_y - int(2 * s), int(24 * s), int(6 * s)))
    pygame.draw.rect(surf, ROSE_BR, (cx - int(12 * s), coll_y - int(2 * s), int(24 * s), int(2 * s)))
    # the trefoil coronet faces the gap (flip vertically for the top cap)
    if cap == "bottom":
        trefoil_coronet(surf, cx, cap_y - int(2 * s), int(16 * s), s)
    else:
        # mirror: render onto a small bounded surface and flip so the crown points DOWN
        # (drawing into a local box avoids subsurfacing the main surface out of bounds)
        w, h = int(80 * s), int(80 * s)
        lcx, lcy = int(40 * s), int(60 * s)
        temp = pygame.Surface((w, h), pygame.SRCALPHA)
        trefoil_coronet(temp, lcx, lcy, int(16 * s), s)
        flipped = pygame.transform.flip(temp, False, True)
        surf.blit(flipped, (cx - int(40 * s), cap_y - int(20 * s)))


# -- compose the review sheet -------------------------------------------------
SS = 6


def grow(small):
    return grow_outline(small, INK + (255,), 1)


def vgrad(surf, rect, top_col, bot_col):
    x, y, w, h = rect
    for j in range(h):
        pygame.draw.line(surf, lerp(top_col, bot_col, j / max(1, h - 1)),
                         (x, y + j), (x + w, y + j))


def hero_chip(boxw, boxh, dcx, dcy, scale):
    big = pygame.Surface((boxw * SS, boxh * SS), pygame.SRCALPHA)
    draw_prince(big, dcx * SS, dcy * SS, scale * SS)
    return grow(pygame.transform.smoothscale(big, (boxw, boxh)))


def chip32(black=False, rim=False):
    """A genuine ~32px-tall figure, downscaled from the SS render."""
    big = pygame.Surface((96 * SS, 96 * SS), pygame.SRCALPHA)
    draw_prince(big, 48 * SS, 52 * SS, (32 / 120.0) * SS, rim=rim)
    small = pygame.transform.smoothscale(big, (96, 96))
    out = grow(small)
    if black:
        # blackout silhouette: stamp the alpha mask solid black
        mask = pygame.mask.from_surface(out)
        sil = mask.to_surface(setcolor=(8, 8, 10, 255), unsetcolor=(0, 0, 0, 0))
        return sil
    return out


def load_font(size, bold=True):
    here = os.path.dirname(os.path.abspath(__file__))
    # FONT path FIVE levels up: rosegold_prince -> skull_kings -> batch2 ->
    # skybit_devil -> docs -> repo root -> game/assets
    fp = os.path.normpath(os.path.join(here, "..", "..", "..", "..", "..",
                                       "game", "assets", "LiberationSans-Bold.ttf"))
    if os.path.exists(fp):
        return pygame.font.Font(fp, size)
    return pygame.font.SysFont("DejaVu Sans", size, bold=bold)


def main():
    W, H = 1010, 820
    font_big = load_font(30)
    font = load_font(17)
    font_sm = load_font(12)

    sheet = pygame.Surface((W, H))
    sheet.fill(BG)

    pygame.draw.rect(sheet, PANEL, (0, 0, W, 56))
    sheet.blit(font_big.render("ROSE-GOLD PRINCE", True, LABEL), (24, 13))
    sheet.blit(font_sm.render(
        "the boy-prince  ·  cute pole · egg-on-legs · spiked trefoil coronet + hot pink tourmaline · round 2",
        True, LABEL_DIM), (330, 26))

    # === (a) BIG HERO =========================================================
    hero = hero_chip(360, 470, 180, 232, 2.0)
    sheet.blit(hero, (14, 92))
    sheet.blit(font.render("Creature — hero", True, LABEL), (110, 566))
    sheet.blit(font_sm.render("compact EGG-ON-LEGS heir (the only small/round king). Tall CENTRAL", True, LABEL_DIM), (14, 590))
    sheet.blit(font_sm.render("spike spikes the coronet out of the round head; wider asymmetric cape +", True, LABEL_DIM), (14, 606))
    sheet.blit(font_sm.render("off-side orb-sceptre. Hot pink tourmaline = brightest pixel. Palest bone.", True, LABEL_DIM), (14, 622))

    # === (b) PILLAR assembled — mirrored, clean tileable shaft ================
    pcx = 470
    top_big = pygame.Surface((150 * SS, 250 * SS), pygame.SRCALPHA)
    draw_pillar(top_big, 75 * SS, 4 * SS, 246 * SS, 1.0 * SS, cap="bottom")
    sheet.blit(grow(pygame.transform.smoothscale(top_big, (150, 250))), (pcx, 86))
    bot_big = pygame.Surface((150 * SS, 250 * SS), pygame.SRCALPHA)
    draw_pillar(bot_big, 75 * SS, 4 * SS, 246 * SS, 1.0 * SS, cap="top")
    sheet.blit(grow(pygame.transform.smoothscale(bot_big, (150, 250))), (pcx, 86 + 250 + 96))
    pygame.draw.rect(sheet, (60, 64, 72), (pcx + 8, 86 + 250, 134, 96))
    sheet.blit(font_sm.render("GAP", True, LABEL_DIM), (pcx + 56, 86 + 250 + 40))
    sheet.blit(font.render("Pillar — orb-regalia", True, LABEL), (pcx - 4, 690))
    sheet.blit(font_sm.render("stacked rose-gold orb beads = tileable shaft;", True, LABEL_DIM), (pcx - 4, 714))
    sheet.blit(font_sm.render("trefoil-coronet + pink gem caps each gap edge", True, LABEL_DIM), (pcx - 4, 730))
    sheet.blit(font_sm.render("(mirrored top<->bottom, on-axis, not top-heavy)", True, LABEL_DIM), (pcx - 4, 746))

    # === (c) TRUE 32px chips on day + night + blackout proof ==================
    panel_x = 660
    pygame.draw.rect(sheet, PANEL, (panel_x, 86, W - panel_x - 14, 560))
    sheet.blit(font.render("True 32px gameplay-scale", True, LABEL), (panel_x + 16, 96))

    chip = chip32()
    chip_night = chip32(rim=True)  # crown rim-light carries the coronet on dark sky

    day_y = 128
    vgrad(sheet, (panel_x + 20, day_y, 150, 150), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, day_y, 150, 150), 1)
    sheet.blit(chip, (panel_x + 20 + 27, day_y + 27))
    sheet.blit(font_sm.render("32px on day sky", True, LABEL), (panel_x + 20, day_y + 156))

    night_y = day_y + 184
    vgrad(sheet, (panel_x + 20, night_y, 150, 150), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, night_y, 150, 150), 1)
    sheet.blit(chip_night, (panel_x + 20 + 27, night_y + 27))
    sheet.blit(font_sm.render("32px night (crown rim-lit)", True, LABEL_DIM), (panel_x + 20, night_y + 156))

    # blackout silhouette proof (the anti-coin test) beside the chips
    px2 = panel_x + 192
    pygame.draw.rect(sheet, BLACKOUT, (px2, day_y, 132, 150))
    pygame.draw.rect(sheet, INK, (px2, day_y, 132, 150), 1)
    # white silhouette stamp so the crown's open trefoil reads as shape
    mask = pygame.mask.from_surface(chip)
    wsil = mask.to_surface(setcolor=(236, 232, 226, 255), unsetcolor=(0, 0, 0, 0))
    sheet.blit(wsil, (px2 + 18, day_y + 27))
    sheet.blit(font_sm.render("silhouette proof", True, LABEL), (px2 + 4, day_y + 156))
    sheet.blit(font_sm.render("(spike SPIKES out of", True, LABEL_DIM), (px2 + 2, day_y + 172))
    sheet.blit(font_sm.render(" the round body)", True, LABEL_DIM), (px2 + 2, day_y + 186))

    # 32px pillar gap-cap chip on both skies
    def pillar_chip32():
        big = pygame.Surface((44 * SS, 130 * SS), pygame.SRCALPHA)
        draw_pillar(big, 22 * SS, 2 * SS, 128 * SS, 0.34 * SS, cap="bottom")
        return grow(pygame.transform.smoothscale(big, (44, 130)))
    pc = pillar_chip32()
    vgrad(sheet, (px2, night_y, 60, 150), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (px2, night_y, 60, 150), 1)
    sheet.blit(pc, (px2 + 8, night_y + 10))
    vgrad(sheet, (px2 + 70, night_y, 60, 150), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (px2 + 70, night_y, 60, 150), 1)
    sheet.blit(pc, (px2 + 78, night_y + 10))
    sheet.blit(font_sm.render("pillar cap (day/night)", True, LABEL_DIM), (px2, night_y + 156))

    # palette swatches
    sheet.blit(font.render("Pinned palette", True, LABEL), (panel_x + 16, 512))
    swatches = [
        (BONE, "palest bone"), (BONE_D, "bone shade"),
        (ROSE, "rose-gold"), (ROSE_BR, "rose-gold hi"),
        (PINK, "soft pink"), (TOURM, "tourmaline"),
        (SOCKET, "socket glow"), (INK, "ink keyline"),
    ]
    sxp, syp = panel_x + 16, 540
    for i, (c, name) in enumerate(swatches):
        col, row = i % 2, i // 2
        rx = sxp + col * 160
        ry = syp + row * 26
        pygame.draw.rect(sheet, INK, (rx - 1, ry - 1, 20, 20))
        pygame.draw.rect(sheet, c, (rx, ry, 18, 18))
        sheet.blit(font_sm.render(name, True, LABEL), (rx + 26, ry + 3))

    # bottom note strip
    pygame.draw.rect(sheet, PANEL, (14, 770, W - 28, 40))
    sheet.blit(font_sm.render(
        "ELEVATED pipeline: SS=6 supersample -> smoothscale.  STAY: flat fills · ink keyline (28,22,30) · "
        "dark-core->fill->top-left sheen triad · 1px grown outline · chibi scary-CUTE · procedural-only · NO KFC red.",
        True, LABEL_DIM), (26, 783))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_2.png")
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
