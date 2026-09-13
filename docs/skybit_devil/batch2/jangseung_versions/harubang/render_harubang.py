"""
Round-1 concept renderer for HARUBANG — the bellied grandfather TOTEM-POST,
re-laned into the carved-WOOD set as the spin-off SET LEAD off the shipped
Jangseung. Headless Pygame; supersample at SS=6 then smoothscale to match the
elevated house grammar (chibi, flat triad dark-core -> flat-fill -> top-left
rim-sheen, hard 1-2px ink keyline, 1px alpha-grown outline; pushed EPIC).

WHY harubang is the best mirror in the set: a real dol hareubang is a fat,
bottom-heavy barrel of a grandfather — widest at the belly, tapering only at the
shoulders, capped by a modest domed mushroom hat. The barrel body literally IS
the post, so the shaft is "more of the same carved belly" (belt-bands +
grain-swirl repeat) and the gap-edge cap is a SMALLER mirrored grandpa-head with
its eyes lit. Fattest + bottom-heavy = a clean on-axis top<->bottom mirror with
zero top-heavy risk (the gap-cap head is deliberately under barrel width).

WHY blackened BOG-OAK as the set's DARK value anchor: the cross-set fix
separates the wood bosses by VALUE. Harubang owns the darkest near-black oak mass
so the TURMERIC-GOLD cap+belt reads as a warm GOLD mass that pops off the dark
oak, the lichen patches stay a desaturated GREY-green (kept greyer than any
Kitsune mint so they never read as a cool accent), and the warm-cream eye glow is
the one bright focal — the pupil-less owl-STARE.

WHY a standalone script: review art must never enter the shipped bundle, so it
lives under docs/ and reuses only colour math, not runtime sprite modules.
"""
import os
import math
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
pygame.init()

# ── PINNED PALETTE (locked brief) ─────────────────────────────────────────────
# Blackened bog-oak — the SET's dark value anchor; near-black so gold pops.
OAK       = ( 96,  80,  68)   # blackened bog-oak base
OAK_D     = ( 60,  48,  42)   # deep bog-oak shade (dark core)
OAK_T     = (138, 120, 104)   # bleached oak rim-sheen helper
OAK_GRV   = ( 44,  36,  32)   # carved bevel-groove shadow (near-ink)

GOLD      = (224, 168,  60)   # turmeric-gold cap + belt-bands (warm GOLD mass)
GOLD_D    = (168, 120,  38)   # deep turmeric shade
GOLD_T    = (248, 214, 132)   # turmeric rim-sheen

# Lichen pushed a hair WARMER/GREYER than r1 so it never drifts toward a cool
# Kitsune-mint reading on the green day sky (AD note: zero mint risk).
LICHEN    = (172, 174, 148)   # pale lichen-grey patch (GREYER + warmer than mint)
LICHEN_D  = (122, 126, 102)   # deep lichen-grey
LICHEN_T  = (208, 208, 184)   # lichen rim-sheen

# PALE OAK-SHEEN wood for the clasped belly-hands — a separate VALUE from the
# near-black belly AND from the gold band, so the hands pop as a third body blob
# at 32px (AD ruling: hands must own their own value, never gold, never the belly).
HAND      = (172, 150, 124)   # pale oak-sheen wood (clasped hands)
HAND_D    = (118,  98,  80)   # hand shade (carved finger grooves)
HAND_T    = (224, 206, 176)   # bright hand rim-sheen (top-left pop)

EYEGLOW   = (246, 224, 168)   # warm-cream eye glow (THE STARE focal)
EYEGLOW_D = (208, 168,  96)   # eye-glow shade ring

INK       = ( 28,  22,  30)   # hard ink keyline (locked set ink)

BG        = ( 96, 100, 104)   # neutral grey review backdrop
PANEL     = ( 72,  76,  82)
DAY_SKY_T = (140, 206, 232)   # day biome sky (top)
DAY_SKY_B = (206, 232, 240)   # day biome sky (low)
NIGHT_T   = ( 22,  28,  52)   # night biome sky (top)
NIGHT_B   = ( 46,  44,  78)   # night biome sky (low)
LABEL     = (238, 240, 242)
LABEL_DIM = (188, 196, 204)


def lerp(a, b, t):
    t = max(0.0, min(1.0, t))
    return (int(a[0] + (b[0]-a[0])*t),
            int(a[1] + (b[1]-a[1])*t),
            int(a[2] + (b[2]-a[2])*t))


# ── outline grown from the alpha mask (the house keyline) ────────────────────
def grow_outline(surf, color, px):
    mask = pygame.mask.from_surface(surf)
    outline_pts = mask.outline()
    if len(outline_pts) < 2:
        return surf
    base = surf.copy()
    ring = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    for (ox, oy) in outline_pts:
        pygame.draw.circle(ring, color, (ox, oy), px)
    ring.blit(base, (0, 0))
    return ring


def triad_blob(surf, color, pts, sheen_pts=None, core_pts=None, outline=True, ow=2):
    """Flat fill + optional dark-core + top-left rim-sheen + ink keyline."""
    if outline:
        pygame.draw.polygon(surf, INK, pts)
    pygame.draw.polygon(surf, color, pts)
    if core_pts:
        pygame.draw.polygon(surf, lerp(color, INK, 0.45), core_pts)
    if sheen_pts:
        pygame.draw.polygon(surf, lerp(color, (255, 255, 255), 0.35), sheen_pts)
    if outline:
        pygame.draw.polygon(surf, INK, pts, ow)


def triad_disc(surf, color, cx, cy, r, ow=2):
    """Round flat-triad lobe: ink ring + flat fill + dark-core lower-right +
    rim-sheen upper-left. The barrel/belly/hands are all built from these so the
    chibi roundness survives the 1x downscale."""
    pygame.draw.circle(surf, INK, (cx, cy), r + ow)
    pygame.draw.circle(surf, color, (cx, cy), r)
    pygame.draw.circle(surf, lerp(color, INK, 0.42),
                       (cx + int(r*0.30), cy + int(r*0.32)), int(r*0.60))
    pygame.draw.circle(surf, lerp(color, (255, 255, 255), 0.30),
                       (cx - int(r*0.34), cy - int(r*0.38)), int(r*0.34))
    pygame.draw.circle(surf, INK, (cx, cy), r, ow)


# ── deterministic SPARSE weather-pitting (procedural, no PRNG state leak) ─────
def weather_pits(surf, cx, cy, rad, s, seed, n=3):
    """A few BIG, FEW dark pits — the re-spec demands SPARSE stipple (no
    face-fuzz at 1x). WHY hash-jittered discs anchored inside a small radius:
    they read as carved weather-pocks on volcanic-look oak, yet stay sparse
    enough that smoothscale never fuzzes them into a grey field."""
    for i in range(n):
        ha = ((seed * 73 + i * 137) % 360) * math.pi / 180.0
        hd = ((seed * 51 + i *  29) % 100) / 100.0
        hr = ((seed * 97 + i *  17) % 100) / 100.0
        lx = cx + int(math.cos(ha) * hd * rad)
        ly = cy + int(math.sin(ha) * hd * rad)
        pr = max(int(2*s), int((0.10 + 0.08*hr) * rad))
        pygame.draw.circle(surf, OAK_GRV, (lx, ly), pr)
        pygame.draw.circle(surf, OAK_T, (lx - int(pr*0.4), ly - int(pr*0.4)),
                           max(1, int(pr*0.34)))


# ── one lichen-grey patch cluster (the aged-stone tell, kept GREY) ────────────
def lichen_patch(surf, cx, cy, rad, s, seed):
    """One COMPACT lichen-grey cluster. A few BIG flat lobes survive 1x
    downscale where stipple fuzzes to grey; kept desaturated GREY-green so it
    never grows into a Kitsune-mint cool accent."""
    n = 4
    for i in range(n):
        ha = ((seed * 67 + i * 131) % 360) * math.pi / 180.0
        hd = ((seed * 47 + i *  31) % 100) / 100.0
        hr = ((seed * 89 + i *  19) % 100) / 100.0
        lx = cx + int(math.cos(ha) * hd * rad * 0.55)
        ly = cy + int(math.sin(ha) * hd * rad * 0.55)
        lr = int((0.34 + 0.30 * hr) * rad)
        pygame.draw.circle(surf, INK, (lx, ly), lr + max(1, int(1*s)))
        pygame.draw.circle(surf, LICHEN, (lx, ly), lr)
        pygame.draw.circle(surf, LICHEN_D, (lx + int(lr*0.3), ly + int(lr*0.3)),
                           int(lr*0.55))
        pygame.draw.circle(surf, LICHEN_T, (lx - int(lr*0.35), ly - int(lr*0.35)),
                           max(1, int(lr*0.28)))


# ── turmeric-gold belt-band (the repeating warm-gold mass on the barrel) ──────
def belt_band(surf, cx, by, half_w, s, h=None):
    """One full-width carved TURMERIC-GOLD belt-band wrapped around the barrel.
    WHY a chunky banded ring (not a thin line): gold is a warm MASS that must pop
    off the dark oak at 32px — a few bold bands give the body its rhythm and read
    as the carved belt the dol hareubang wears low. Top-left rim-sheen + a deep
    lower edge make it sit as a raised carved ring, not a painted stripe."""
    bh = h if h is not None else int(13*s)
    w = half_w * 2
    x0 = cx - half_w
    band = [(x0, by), (x0 + w, by), (x0 + w, by + bh), (x0, by + bh)]
    triad_blob(
        surf, GOLD, band,
        core_pts=[(x0, by + int(bh*0.55)), (x0 + w, by + int(bh*0.55)),
                  (x0 + w, by + bh), (x0, by + bh)],
        sheen_pts=[(x0 + int(3*s), by + int(2*s)), (x0 + w - int(3*s), by + int(2*s)),
                   (x0 + w - int(3*s), by + int(bh*0.42)),
                   (x0 + int(3*s), by + int(bh*0.42))],
        ow=max(1, int(1.5*s)),
    )
    # a couple of carved notch-studs along the band (few & big — the belt tell)
    for fx in (-0.5, 0.0, 0.5):
        sx = cx + int(fx * w * 0.5)
        pygame.draw.circle(surf, GOLD_D, (sx, by + bh//2), max(2, int(2.4*s)))
        pygame.draw.circle(surf, GOLD_T, (sx - int(1*s), by + bh//2 - int(1*s)),
                           max(1, int(1.4*s)))


# ── carved-barrel shaft band (the repeatable POST unit = the belly) ───────────
def barrel_shaft(surf, cx, top, bot, half_w, s, swell=1.0):
    """One stretch of the barrel POST: a near-black bog-oak column that BULGES
    out (the belly is the body is the pillar). Carved belt-bands + a belly
    grain-SWIRL repeat down it; sparse weather-pitting + 2 lichen clusters age
    it. `swell` lets the hero body fatten at the belly while the pillar tiles a
    gentler swell so segments stack cleanly. This is what tiles — the creature
    IS this barrel."""
    h = bot - top
    # a subtly bulged barrel silhouette (widest at mid) built as a polygon so the
    # whole post reads FAT/bottom-heavy rather than a straight bar.
    bulge = int(half_w * 0.16 * swell)
    midy = (top + bot) // 2
    left = [
        (cx - half_w + bulge, top),
        (cx - half_w - bulge, midy),
        (cx - half_w + int(bulge*0.4), bot),
    ]
    right = [
        (cx + half_w - int(bulge*0.4), bot),
        (cx + half_w + bulge, midy),
        (cx + half_w - bulge, top),
    ]
    body = left + right
    # main barrel mass — flat fill + dark core on the right + bleached sheen left
    triad_blob(
        surf, OAK, body,
        core_pts=[(cx + int(half_w*0.18), top), (cx + half_w + bulge, midy),
                  (cx + half_w - int(bulge*0.4), bot), (cx + int(half_w*0.18), bot)],
        sheen_pts=[(cx - half_w + bulge, top),
                   (cx - half_w - bulge, midy),
                   (cx - half_w + int(bulge*0.4), bot),
                   (cx - int(half_w*0.30), bot),
                   (cx - int(half_w*0.30), top)],
        ow=max(2, int(2*s)),
    )

    # belly grain-SWIRL — a few BIG concentric carved arcs centred low on the
    # barrel (where the belly bulges). WHY big arcs not a hatch field: they read
    # as the carved belly grain at 32px and survive downscale; piling thin grain
    # would fuzz to mud. Few & bold per the big-and-few identity rule.
    # grain-swirl pushed to the UPPER belly (above where the clasped hands sit)
    # so it reads as carved belly grain and never tangles with the hand mass.
    swirl_cy = top + int(h * 0.40)
    for ri, rr in enumerate((0.70, 0.50, 0.30)):
        rad = int(half_w * rr)
        rect = pygame.Rect(cx - rad, swirl_cy - int(rad*0.78),
                           rad*2, int(rad*1.56))
        pygame.draw.arc(surf, OAK_GRV, rect, math.radians(202), math.radians(338),
                        max(2, int(3*s)))
        pygame.draw.arc(surf, OAK_T, rect.move(0, -max(1, int(2*s))),
                        math.radians(212), math.radians(328), max(1, int(1.5*s)))

    # carved TURMERIC-GOLD belt-bands wrapping the barrel (the repeat rhythm).
    pitch = int(108 * s)
    by = top + int(40 * s)
    while by < bot - int(28*s):
        # band half-width follows the bulge so it hugs the barrel
        frac = (by - top) / max(1, h)
        bw = half_w + int(bulge * math.sin(math.pi * frac)) - int(2*s)
        belt_band(surf, cx, by, bw, s)
        by += pitch

    # SPARSE weather-pitting + 2 lichen clusters anchored inside the silhouette.
    # Thinned ~30% from r1 and pushed to the EDGES/upper-shoulder so the pits
    # never compete with the (now enlarged) clasped-hands mass on the mid-belly.
    weather_pits(surf, cx - int(half_w*0.55), top + int(h*0.22),
                 int(half_w*0.42), s, seed=int(top) % 71 + 3, n=2)
    weather_pits(surf, cx + int(half_w*0.58), bot - int(h*0.18),
                 int(half_w*0.34), s, seed=int(bot) % 67 + 5, n=1)
    lr = max(int(5*s), int(half_w * 0.28))
    lichen_patch(surf, cx - int(half_w*0.66), top + int(h*0.32), lr, s,
                 seed=int(top) % 97 + 3)
    lichen_patch(surf, cx + int(half_w*0.62), bot - int(h*0.14), lr, s,
                 seed=int(bot) % 89 + 7)


# ── the two little clasped hands low on the belly (identity feature) ──────────
def belly_hands(surf, cx, cy, half_w, s):
    """Two fat hands clasped on the MID-belly — the load-bearing identity beat
    that makes him a grandfather, not just a big-eyed post (AD ruling).

    WHY this redraw (the decisive r1->r2 fix): at 32px the r1 hands merged into
    the gold belt-band and read as a lumpy stripe. So now —
      • the hands are ENLARGED into one wide clasped mass spanning most of the
        belly, sitting on the MID-belly well CLEAR of the lower belt-band;
      • a hard dark BOG-OAK-shade gap (carved bevel-groove value) is laid UNDER
        the hands so they never touch the band and never merge at 1x;
      • they are painted in PALE OAK-SHEEN WOOD (not gold, not belly-oak) with a
        bright top-left rim-sheen, so the body reads as THREE blobs at 32px:
        gold cap-eyes mass / dark belly / pale clasped-hands mass;
      • BIG AND FEW: two fat mitten-blobs with just 3 fat sausage-finger lobes
        crossing the seam — no thin-finger noise that fuzzes at downscale."""
    hr = int(half_w * 0.62)                 # ENLARGED — was 0.40
    span = int(hr * 0.72)                   # how far each mitt sits off-centre
    ly_off = int(hr * 0.10)                 # the slight clasp asymmetry

    # 1) HARD DARK GAP first: a near-black bog-oak shadow shelf carved UNDER the
    #    hand mass so the pale hands float clear of the belly/belt and never merge.
    shelf = [
        (cx - hr - span + int(hr*0.2), cy + int(hr*0.62)),
        (cx + hr + span - int(hr*0.2), cy + int(hr*0.62)),
        (cx + hr + span - int(hr*0.5), cy + int(hr*1.18)),
        (cx - hr - span + int(hr*0.5), cy + int(hr*1.18)),
    ]
    pygame.draw.polygon(surf, OAK_GRV, shelf)

    # 2) the two fat mitten-blobs in PALE OAK-SHEEN wood (the third body blob)
    lx = cx - span
    rx = cx + span
    for (hx, hy) in ((lx, cy + ly_off), (rx, cy - ly_off)):
        triad_disc(surf, HAND, hx, hy, hr, ow=max(2, int(2.2*s)))

    # 3) ONE deep ink clasp-seam down the centre where the two mitts overlap
    pygame.draw.line(surf, INK, (cx, cy - int(hr*0.78)),
                     (cx, cy + int(hr*0.74)), max(2, int(3.2*s)))

    # 4) just 3 FAT sausage-finger lobes crossing the seam (big & few). Each is a
    #    pale disc with a carved shade groove below + bright sheen above — they
    #    read as plump grandfather fingers, never thin hatch lines.
    fr = int(hr * 0.30)
    for fy_f in (-0.34, 0.0, 0.34):
        fy = cy + int(hr * fy_f)
        for sgn in (-1, 1):
            fx = cx + sgn * int(hr * 0.42)
            pygame.draw.circle(surf, HAND_D, (fx, fy + max(1, int(2*s))),
                               fr + max(1, int(1*s)))
            pygame.draw.circle(surf, HAND, (fx, fy), fr)
            pygame.draw.circle(surf, HAND_T,
                               (fx - int(fr*0.34), fy - int(fr*0.40)),
                               max(1, int(fr*0.40)))
            pygame.draw.circle(surf, INK, (fx, fy), fr, max(1, int(1.4*s)))


# ── the grandpa head: pupil-less owl-eyes STARE under a domed mushroom-cap ────
def grandpa_head(surf, cx, cy, s, head_r, lit=False):
    """The grandfather head: a rounded oak block dominated by two pupil-less
    bulging owl-EYES (warm-cream glow + bright rim-sheen = THE STARE), a fat
    bulb-nose, a calm carved grin, all under a MODEST domed mushroom-cap with a
    turmeric-gold band. `lit` brightens the eye-glow so the same head works as
    the GAP-EDGE cap (the partner-head, lit at the gap). `head_r` scales the
    whole head so the gap-cap head can be drawn CLEARLY SMALLER than the barrel
    (no top-heavy risk). Eyes + nose + cap = the whole face identity, big & few."""
    # head block — a broad rounded oak plaque, a touch narrower than the barrel
    triad_disc(surf, OAK, cx, cy, head_r, ow=max(2, int(2*s)))
    # carved brow ridge — one calm furrow framing the owl-eyes (grandfatherly)
    brow_y = cy - int(head_r*0.30)
    pygame.draw.arc(surf, OAK_GRV,
                    pygame.Rect(cx - int(head_r*0.78), brow_y - int(head_r*0.30),
                                int(head_r*1.56), int(head_r*0.7)),
                    math.radians(202), math.radians(338), max(2, int(3*s)))

    # ── the owl-eyes: pupil-LESS bulging domes with a bright rim-sheen STARE ──
    eye_dx = int(head_r * 0.46)
    eye_y = cy - int(head_r*0.10)
    er = int(head_r * 0.40)
    glow_a = 165 if lit else 95
    glow_r = int(er * (2.4 if lit else 1.7))
    glow = pygame.Surface((glow_r*4, glow_r*4), pygame.SRCALPHA)
    for r in range(glow_r, 0, -1):
        a = int(glow_a * (1 - r/glow_r))
        pygame.draw.circle(glow, (*EYEGLOW, a), (glow_r*2, glow_r*2), r)
    for sgn in (-1, 1):
        ex = cx + sgn * eye_dx
        surf.blit(glow, (ex - glow_r*2, eye_y - glow_r*2),
                  special_flags=pygame.BLEND_ADD)
    for sgn in (-1, 1):
        ex = cx + sgn * eye_dx
        # bulging carved socket rim (the owl-eye dome)
        pygame.draw.circle(surf, INK, (ex, eye_y), er + max(1, int(2*s)))
        pygame.draw.circle(surf, OAK_D, (ex, eye_y), er)
        pygame.draw.circle(surf, OAK_T, (ex - int(er*0.4), eye_y - int(er*0.4)),
                           int(er*0.5))
        pygame.draw.circle(surf, INK, (ex, eye_y), er, max(1, int(2*s)))
        # the warm-cream glowing eyeball — PUPIL-LESS (no ink dot): the blank
        # owl STARE. A bright top-left rim-sheen crescent reads as THE STARE.
        eb = int(er * (0.78 if lit else 0.70))
        pygame.draw.circle(surf, EYEGLOW_D, (ex, eye_y), eb + max(1, int(1*s)))
        pygame.draw.circle(surf, EYEGLOW, (ex, eye_y), eb)
        # bright rim-sheen crescent (upper-left) = the wet bulging-eye stare
        pygame.draw.circle(surf, (255, 250, 232),
                           (ex - int(eb*0.30), eye_y - int(eb*0.34)),
                           max(1, int(eb*0.40)))

    # fat BULB-NOSE — one big rounded mass dead-centre (the grandfather anchor)
    ny = cy + int(head_r*0.34)
    nr = int(head_r * 0.26)
    triad_disc(surf, OAK, cx, ny, nr, ow=max(1, int(2*s)))
    for sgn in (-1, 1):
        pygame.draw.circle(surf, INK, (cx + sgn*int(nr*0.42), ny + int(nr*0.40)),
                           max(1, int(2.4*s)))

    # calm carved GRIN — a single soft upturned groove (grandfatherly, not fanged)
    my = cy + int(head_r*0.66)
    mw = int(head_r*0.46)
    pygame.draw.arc(surf, INK,
                    pygame.Rect(cx - mw, my - int(mw*0.6), mw*2, int(mw*1.2)),
                    math.radians(200), math.radians(340), max(2, int(3*s)))
    pygame.draw.arc(surf, OAK_T,
                    pygame.Rect(cx - mw, my - int(mw*0.6) - max(1, int(1*s)),
                                mw*2, int(mw*1.2)),
                    math.radians(206), math.radians(334), max(1, int(1*s)))

    # ── the MODEST domed mushroom-cap (brim <= belly width, no top-heavy) ──
    cap_w = int(head_r * 1.52)          # brim kept under barrel width by caller
    cap_cy = cy - int(head_r * 0.92)
    cap_h = int(head_r * 0.78)
    # the dome — a half-ellipse turmeric-gold cap
    dome_rect = pygame.Rect(cx - cap_w//2, cap_cy - cap_h, cap_w, cap_h*2)
    pygame.draw.circle(surf, INK, (cx, cap_cy), 1)  # anchor (cheap no-op guard)
    # ink under-ring then gold dome (upper half only)
    dome_pts = []
    for a in range(180, 361, 12):
        rad = math.radians(a)
        dome_pts.append((cx + int(math.cos(rad)*cap_w*0.5),
                         cap_cy + int(math.sin(rad)*cap_h)))
    dome_pts += [(cx + cap_w//2, cap_cy), (cx - cap_w//2, cap_cy)]
    triad_blob(
        surf, GOLD, dome_pts,
        core_pts=[(cx, cap_cy - int(cap_h*0.2)),
                  (cx + int(cap_w*0.34), cap_cy),
                  (cx + cap_w//2, cap_cy), (cx, cap_cy)],
        sheen_pts=[(cx - int(cap_w*0.42), cap_cy - int(cap_h*0.1)),
                   (cx - int(cap_w*0.06), cap_cy - int(cap_h*0.78)),
                   (cx - int(cap_w*0.02), cap_cy - int(cap_h*0.30)),
                   (cx - int(cap_w*0.34), cap_cy)],
        ow=max(2, int(2*s)),
    )
    # the cap BRIM — a DOMED gold ledge whose LOWER edge curves like the crown
    # so the whole cap reads unmistakably as a soft MUSHROOM (AD fix: no flat
    # brim). Built as a thin gold lens: an arc top edge + a deeper arc bottom edge.
    brim_y = cap_cy
    brim_hw = cap_w//2 + int(3*s)
    brim_th = int(10*s)                     # brim thickness at centre
    top_pts, bot_pts = [], []
    steps = 22
    for i in range(steps + 1):
        t = i / steps
        bx = cx - brim_hw + int(2*brim_hw * t)
        # gentle dome curve on both edges (lower edge bows DOWN at centre)
        dome = math.sin(math.pi * t)
        top_pts.append((bx, brim_y - int(brim_th*0.25*dome)))
        bot_pts.append((bx, brim_y + int(brim_th*0.45) + int(brim_th*0.55*dome)))
    brim = top_pts + bot_pts[::-1]
    pygame.draw.polygon(surf, INK, brim)
    pygame.draw.polygon(surf, GOLD, brim)
    # top-left sheen lip + deeper lower lip read the brim as a raised carved lens
    pygame.draw.lines(surf, GOLD_T, False, top_pts, max(1, int(2*s)))
    pygame.draw.lines(surf, GOLD_D, False, bot_pts, max(1, int(2*s)))
    pygame.draw.polygon(surf, INK, brim, max(1, int(1.5*s)))


# ── the full hero creature: domed-cap grandpa atop the fat barrel post ────────
def draw_harubang(surf, cx, cy, s):
    """The whole bellied grandfather: a SMALL domed grandpa-head crowning a FAT
    bottom-heavy barrel post (the belly = the body = the pillar), two little
    hands clasped low on the belly. No legs — a hareubang is a post. `s` is a
    unit scale around a ~250-unit-tall figure."""
    half_w = int(46*s)            # FAT barrel — widest in the set
    post_top = cy - int(36*s)
    post_bot = cy + int(168*s)
    # the carved-barrel body shaft (continues the same column the pillar tiles)
    barrel_shaft(surf, cx, post_top, post_bot, half_w, s, swell=1.4)
    # a wide plinth foot grounds the barrel (bottom-rooted, never top-heavy)
    pf_w = half_w + int(14*s)
    foot = [(cx - pf_w, post_bot - int(6*s)), (cx + pf_w, post_bot - int(6*s)),
            (cx + pf_w - int(4*s), post_bot + int(18*s)),
            (cx - pf_w + int(4*s), post_bot + int(18*s))]
    triad_blob(surf, OAK_D, foot,
               sheen_pts=[(cx - pf_w + int(2*s), post_bot - int(4*s)),
                          (cx - int(4*s), post_bot - int(4*s)),
                          (cx - int(4*s), post_bot + int(12*s)),
                          (cx - pf_w + int(4*s), post_bot + int(12*s))],
               ow=max(2, int(2*s)))
    # the two fat clasped hands on the MID-belly (identity anchor #2) — lifted
    # well clear of the lower belt-band so the dark gap reads at 32px.
    belly_hands(surf, cx, cy + int(58*s), half_w, s)
    # the grandpa head crowning the barrel — head clearly NARROWER than belly.
    # lit=True so the warm-cream owl-stare carries the SAME glow weight as the
    # gap-cap partner-head, anchoring the night read consistently (AD FIX 8).
    head_r = int(half_w * 0.82)
    grandpa_head(surf, cx, post_top - int(head_r*0.66), s, head_r, lit=True)


# ── the pillar: same carved barrel, mirrored, with a partner-head gap-cap ─────
def draw_pillar_segment(surf, cx, top, bot, half_w, s, cap="bottom"):
    """A stretch of the barrel POST that meets the gap with a SMALLER mirrored
    PARTNER-HEAD cap (owl-eyes LIT at the gap). The shaft is the same carved
    barrel as the creature body, so creature == pillar. `cap` end faces the gap.
    The gap-cap head is drawn deliberately SMALLER than the barrel half-width so
    the stacked mirror is bottom-heavy and NEVER top-heavy."""
    head_r = int(half_w * 0.74)         # gap-cap head < barrel half-width
    head_room = int(head_r * 2.5)
    if cap == "bottom":
        shaft_top, shaft_bot = top, bot - head_room
        head_cy = bot - head_room // 2 + int(head_r*0.30)
        flip = False
    else:
        shaft_top, shaft_bot = top + head_room, bot
        head_cy = top + head_room // 2 - int(head_r*0.30)
        flip = True
    barrel_shaft(surf, cx, shaft_top, shaft_bot, half_w, s, swell=0.8)

    # the partner-head — same grandpa head, drawn into a scratch surface so it
    # can be FLIPPED for the top cap (proving the true top<->bottom mirror)
    hsz = int(head_r * 4)
    hbuf = pygame.Surface((hsz, hsz), pygame.SRCALPHA)
    grandpa_head(hbuf, hsz//2, hsz//2, s, head_r, lit=True)
    if flip:
        hbuf = pygame.transform.flip(hbuf, False, True)
    surf.blit(hbuf, (cx - hsz//2, int(head_cy) - hsz//2))


# ── sky helpers (procedural vertical gradient via per-row fills) ─────────────
def sky(surf, rect, top_col, bot_col):
    x, y, w, h = rect
    for j in range(h):
        surf.fill(lerp(top_col, bot_col, j / max(1, h-1)), (x, y+j, w, 1))


# ── compose the review sheet ─────────────────────────────────────────────────
SS = 6


def main():
    W, H = 1040, 900
    font_big = pygame.font.SysFont("DejaVu Sans", 30, bold=True)
    font = pygame.font.SysFont("DejaVu Sans", 17, bold=True)
    font_sm = pygame.font.SysFont("DejaVu Sans", 12)

    sheet = pygame.Surface((W, H))
    sheet.fill(BG)

    pygame.draw.rect(sheet, PANEL, (0, 0, W, 56))
    sheet.blit(font_big.render("HARUBANG", True, LABEL), (22, 12))
    sheet.blit(font_sm.render(
        "bellied grandfather totem-post  ·  bog-oak + turmeric-gold belt/cap + pale-wood clasped hands + warm-cream owl-eyes  ·  round 2  ·  SET LEAD  ·  barrel IS the pillar",
        True, LABEL_DIM), (215, 26))

    # (a) BIG hero sprite ------------------------------------------------------
    hb_w, hb_h = 300, 470
    big = pygame.Surface((hb_w*SS, hb_h*SS), pygame.SRCALPHA)
    draw_harubang(big, hb_w*SS//2, int(hb_h*SS*0.44), 1.30*SS)
    hero = pygame.transform.smoothscale(big, (hb_w, hb_h))
    hero = grow_outline(hero, INK + (255,), 1)
    sheet.blit(hero, (10, 72))
    sheet.blit(font.render("(a) Hero — domed-cap grandpa on a fat barrel", True, LABEL), (16, 548))
    sheet.blit(font_sm.render("owl-eye STARE + FAT pale-wood clasped hands (lifted off the belt,", True, LABEL_DIM), (16, 572))
    sheet.blit(font_sm.render("dark gap under them) + domed mushroom-cap = identity; bottom-heavy", True, LABEL_DIM), (16, 588))

    # (b) pillar assembled — top segment + gap + bottom segment, MIRRORED ------
    pcx = 460
    seg_half = int(40)
    seg_h = 250
    seg_top_y = 72
    gap_px = 96
    # top segment (cap faces DOWN toward the gap = flipped partner-head)
    topbuf = pygame.Surface((160*SS, seg_h*SS), pygame.SRCALPHA)
    draw_pillar_segment(topbuf, 80*SS, 4*SS, (seg_h-4)*SS, seg_half*SS, 1.0*SS, cap="top")
    topimg = pygame.transform.smoothscale(topbuf, (160, seg_h))
    topimg = grow_outline(topimg, INK + (255,), 1)
    sheet.blit(topimg, (pcx - 80, seg_top_y))
    # bottom segment (cap faces UP toward the gap = upright partner-head)
    botbuf = pygame.Surface((160*SS, seg_h*SS), pygame.SRCALPHA)
    draw_pillar_segment(botbuf, 80*SS, 4*SS, (seg_h-4)*SS, seg_half*SS, 1.0*SS, cap="bottom")
    botimg = pygame.transform.smoothscale(botbuf, (160, seg_h))
    botimg = grow_outline(botimg, INK + (255,), 1)
    sheet.blit(botimg, (pcx - 80, seg_top_y + seg_h + gap_px))

    # gap guide lines
    gap_y0, gap_y1 = seg_top_y + seg_h, seg_top_y + seg_h + gap_px
    for gy in (gap_y0, gap_y1):
        pygame.draw.line(sheet, (150, 154, 160), (pcx - 92, gy), (pcx + 92, gy), 1)
    sheet.blit(font_sm.render("← gap →", True, LABEL_DIM), (pcx - 24, (gap_y0+gap_y1)//2 - 7))
    by = seg_top_y + 2*seg_h + gap_px + 10
    sheet.blit(font.render("(b) Pillar — MIRRORED", True, LABEL), (pcx - 92, by))
    sheet.blit(font_sm.render("tileable carved barrel (gold belts +", True, LABEL_DIM), (pcx - 92, by + 24))
    sheet.blit(font_sm.render("belly grain); SMALLER mirrored grandpa-", True, LABEL_DIM), (pcx - 92, by + 40))
    sheet.blit(font_sm.render("head cap, owl-eyes lit at gap (no top-heavy)", True, LABEL_DIM), (pcx - 92, by + 56))

    # (c) TRUE 32px gameplay-scale chips — day sky + night sky -----------------
    panel_x = 660
    pw = W - panel_x - 14
    pygame.draw.rect(sheet, PANEL, (panel_x, 72, pw, 372))
    sheet.blit(font.render("(c) True 32px gameplay chip", True, LABEL), (panel_x + 14, 82))
    sheet.blit(font_sm.render("owl-eye stare + belly + cap silhouette read", True, LABEL_DIM), (panel_x + 14, 104))

    # render at a true ~32px-TALL read — the full bellied figure scaled so its
    # height spans ~32px, the gameplay collision scale.
    def chip32():
        cw, ch = 30, 32          # chip canvas (px): true 32px-TALL figure
        buf = pygame.Surface((cw*SS, ch*SS*1.0), pygame.SRCALPHA)
        # the hero ~250 units tall packs into ~32px height -> s such that
        # 250*s ~= 32  (the draw_harubang figure spans ~204 units top->foot)
        draw_harubang(buf, cw*SS//2, int(ch*SS*0.46), (32/250.0)*SS)
        img = pygame.transform.smoothscale(buf, (cw, ch))
        return grow_outline(img, INK + (255,), 1)

    chip = chip32()
    cw, ch = chip.get_size()
    chip4 = pygame.transform.scale(chip, (cw*4, ch*4))  # zoom to inspect read

    def chip_row(sky_top, sky_bot, sy, lbl, lbl_col):
        sw, shh = 130, 132
        sx = panel_x + 22
        sky(sheet, (sx, sy, sw, shh), sky_top, sky_bot)
        pygame.draw.rect(sheet, INK, (sx, sy, sw, shh), 1)
        # true-size chip centred in the sky tile
        sheet.blit(chip, (sx + sw//2 - cw//2, sy + shh//2 - ch//2))
        sheet.blit(font_sm.render(lbl, True, lbl_col), (sx + 4, sy + shh - 16))
        # 4x zoom to the right, clamped inside the panel
        zx = sx + sw + 18
        zw = cw*4
        if zx + zw > panel_x + pw - 10:
            zw = panel_x + pw - 10 - zx
            chip_z = chip4.subsurface((0, 0, max(1, zw), min(ch*4, shh+24)))
            sheet.blit(chip_z, (zx, sy))
        else:
            sheet.blit(chip4, (zx, sy - 6))
        return sx, zx

    cy0 = 132
    chip_row(DAY_SKY_T, DAY_SKY_B, cy0, "day sky", INK)
    sheet.blit(font_sm.render("4× zoom →", True, LABEL_DIM), (panel_x + 22 + 130 + 18, cy0 - 18))
    cy1 = cy0 + 168
    chip_row(NIGHT_T, NIGHT_B, cy1, "night sky", LABEL)
    sheet.blit(font_sm.render("warm-cream owl-eyes anchor the night read",
                              True, LABEL_DIM), (panel_x + 22, cy1 + 138))

    # palette swatch row -------------------------------------------------------
    pal_y = 458
    pygame.draw.rect(sheet, PANEL, (panel_x, pal_y, pw, 196))
    sheet.blit(font.render("Pinned palette", True, LABEL), (panel_x + 14, pal_y + 10))
    swatches = [
        (OAK, "bog-oak"), (OAK_D, "deep oak (core)"),
        (OAK_T, "oak sheen"), (OAK_GRV, "bevel groove"),
        (GOLD, "turmeric gold"), (GOLD_D, "deep gold"),
        (HAND, "pale-wood hand"), (HAND_T, "hand sheen"),
        (LICHEN, "lichen-grey"), (LICHEN_D, "deep lichen"),
        (EYEGLOW, "eye-glow cream"), (EYEGLOW_D, "glow shade"),
        (INK, "ink keyline"),
    ]
    sx, sy = panel_x + 14, pal_y + 40
    for i, (c, name) in enumerate(swatches):
        col = i % 2
        row = i // 2
        rx = sx + col*150
        ry = sy + row*28
        pygame.draw.rect(sheet, INK, (rx-1, ry-1, 22, 22))
        pygame.draw.rect(sheet, c, (rx, ry, 20, 20))
        sheet.blit(font_sm.render(name, True, LABEL), (rx+27, ry+4))

    # construction note panel — full-width strip across the bottom ------------
    note_y = 668
    pygame.draw.rect(sheet, PANEL, (10, note_y, W - 20, 222))
    sheet.blit(font.render("Construction notes", True, LABEL), (26, note_y + 10))
    notes_l = [
        "• Blackened BOG-OAK = the set's DARK value anchor; near-black",
        "  so the turmeric-gold reads as a warm GOLD MASS that pops.",
        "• Turmeric-gold = cap dome + brim + carved BELT-BANDS (the",
        "  repeat rhythm wrapping the barrel) — a warm mass, not a line.",
        "• Lichen-grey kept GREYER than any mint (clustered lobes,",
        "  not noise) so it never reads as a cool Kitsune-mint accent.",
    ]
    notes_r = [
        "• HANDS FIX (r2): enlarged, lifted to MID-belly off the belt-band",
        "  w/ a hard dark bog-oak gap under them; PALE-WOOD (not gold) +",
        "  rim-sheen so the body reads as 3 blobs at 32px — gold cap-eyes /",
        "  dark belly / pale clasped-hands. Two mitts, 3 fat fingers. Big&few.",
        "• Fattest, BOTTOM-HEAVY barrel; gap-cap grandpa-head CLEARLY",
        "  smaller than belly — best mirror, no top-heavy; eyes glow-matched.",
    ]
    for i, line in enumerate(notes_l):
        sheet.blit(font_sm.render(line, True, LABEL_DIM), (26, note_y + 40 + i*19))
    for i, line in enumerate(notes_r):
        sheet.blit(font_sm.render(line, True, LABEL_DIM), (540, note_y + 40 + i*19))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_2.png")
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
