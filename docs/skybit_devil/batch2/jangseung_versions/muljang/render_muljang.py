"""
Round-1 concept renderer for MULJANG — the prow-rider SHIP-FIGUREHEAD spirit
(carved-WOOD jangseung spin-off set, concept #3). Headless Pygame; supersample
at SS=6 then smoothscale to match the elevated house grammar (chibi, flat
saturated fills, hard 1-2px ink keyline, dark-core -> flat-fill -> top-left
rim-sheen triad, 1px alpha-grown outline).

WHY muljang is the only MOTION read of its set: a ship figurehead is carved to
lean INTO the wind off the prow, so its whole identity is dynamism — a forward
~15-degree lean and a swept-back blade-lock hair fan that no other (rooted,
symmetric) sibling post has. The carved wave-SCROLL column IS the pillar: real
prow trailboards are stacks of foam-curl scrolls, so the shaft is literally
"more of the same carved foam-scroll" and the gap-cap is a SMALLER mirrored
figurehead-head — a clean on-axis top<->bottom mirror that is folklore-true.

WHY a HEAVY scroll base under a leaning head: a lean alone would make the
gap-cap top-heavy. The re-spec balances the ~15-degree lean with a broad, dense
stack of scroll-commas low on the post so the MASS stays at the base while only
the head tips toward the gap — bottom-rooted dynamism, not a toppling cap.

WHY teak a hair COOLER/greyer than honey-cedar: muljang and the cedar lion-post
Haedung are the closest wood pair in the set, so the cross-set pin keeps this
teak slightly greyer and its accent on the COOL side — sea-teal foam (deeper,
cooler than Haedung's jade) lives in a single PROW-FOAM band, never a body
fill, and the one warm focal is the coral lip/medallion plus the warm eye glow.

WHY a standalone script: review art must never enter the shipped bundle, so it
lives under docs/ and reuses only colour math, not runtime sprite modules.
"""
import os
import math
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
pygame.init()

# ── PINNED PALETTE (locked brief) ─────────────────────────────────────────────
# Golden-tan TEAK — kept a hair cooler/greyer than Haedung's honey-cedar so the
# closest wood pair in the set still reads apart at thumbnail.
TEAK      = (204, 158,  98)   # golden-tan teak base
TEAK_D    = (154, 108,  56)   # deep teak shade (dark core)
# WHY a distinctly greyer rim than a pure cream: a salt-bleached teak catches a
# cool-pale highlight, not a warm honey one — this is the cooler-than-cedar tell.
TEAK_T    = (224, 190, 138)   # sun-warmed teak rim-sheen helper
GRV       = ( 96,  66,  40)   # carved scroll-groove shadow

SALT      = (212, 200, 170)   # pale salt-bleach on wind-edges (cool pale)
SALT_T    = (236, 230, 210)   # brightest salt fleck
# WHY a capped warm light-teak (not the cream salt): the lit cap face must read
# as the SAME carved teak as the body, so its rim-sheen tops out near L~176 — a
# warm light-teak within ~25 L of the body fill, never the L~204 cream that
# made the cap look like a separate pale stone mask. Salt is now an EDGE-only
# sliver; this is the cap's interior lift.
RIM_TEAK  = (224, 184, 132)   # restrained warm light-teak cap rim-sheen (~L176)

# SEA-TEAL — PROW-FOAM band + eye-paint ONLY (deeper/cooler than jade); never a
# body fill, so it stays a single placed band, not a second mass.
TEAL      = ( 58, 138, 140)   # sea-teal foam / eye-paint
TEAL_D    = ( 34,  92,  96)   # deep sea-teal shade
TEAL_T    = (118, 186, 184)   # foam rim-sheen

# CORAL-RED — small warm focal: lip + brow medallion only.
CORAL     = (216,  96,  76)   # coral-red lip + medallion
CORAL_D   = (158,  62,  50)   # deep coral shade
CORAL_T   = (240, 148, 128)   # coral rim-sheen

EYEGLOW   = (250, 226, 170)   # warm eye glow (the one warm light)
EYEGLOW_D = (216, 168,  98)   # eye-glow shade ring

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


def triad_blob(surf, color, pts, sheen_pts=None, core_pts=None, outline=True,
               ow=2, sheen_amt=0.30):
    """Flat fill + optional dark-core + top-left rim-sheen + ink keyline.
    WHY a tunable sheen amount: the lit cap face must NOT flood to a pale cream
    plate (it broke the "creature IS the wood" read), so the face passes a
    restrained sheen that lifts the teak only a little — teak stays dominant."""
    if outline:
        pygame.draw.polygon(surf, INK, pts)
    pygame.draw.polygon(surf, color, pts)
    if core_pts:
        pygame.draw.polygon(surf, lerp(color, INK, 0.45), core_pts)
    if sheen_pts:
        pygame.draw.polygon(surf, lerp(color, (255, 255, 255), sheen_amt), sheen_pts)
    if outline:
        pygame.draw.polygon(surf, INK, pts, ow)


# ── one carved FOAM-CURL scroll comma (the repeatable shaft unit) ─────────────
def foam_scroll(surf, cx, cy, r, s, facing=1, teal_band=False):
    """ONE hard triad foam-curl comma: a fat carved spiral that tapers to a
    hooked tip — the trailboard scroll a prow stacks. WHY a chunky spiral disc
    rather than a thin line spiral: at 32px a thin spiral fuzzes to a smudge, so
    the comma is built from two flat discs (a fat head + a tapering tail arc)
    with one carved inner groove and a single salt-bleach rim fleck — big & few
    survives the downscale. `teal_band` swaps the inner groove for a sea-teal
    foam highlight so the foam band reads only where placed, never as body fill.
    `facing` mirrors the hook L/R so a stacked column alternates like real foam."""
    fr = facing
    # outer comma silhouette: a fat round head with a sweeping tail hook
    head = (cx, cy)
    pts = []
    # head arc (big circle) approximated as a polygon so the keyline is crisp
    for a in range(0, 360, 24):
        rad = math.radians(a)
        pts.append((cx + math.cos(rad) * r, cy + math.sin(rad) * r))
    # tail hook sweeping out from the head and curling back
    tail = [
        (cx + fr * r * 0.2, cy - r),
        (cx + fr * r * 1.7, cy - r * 0.85),
        (cx + fr * r * 2.05, cy - r * 0.05),
        (cx + fr * r * 1.5, cy + r * 0.45),
        (cx + fr * r * 1.0, cy + r * 0.2),
    ]
    comma = pts + tail
    triad_blob(
        surf, TEAK, comma,
        core_pts=[(cx + fr * int(r * 0.2), cy - int(r * 0.1)),
                  (cx + fr * r * 1.7, cy - r * 0.6),
                  (cx + fr * r * 1.4, cy + r * 0.3),
                  (cx + fr * int(r * 0.15), cy + int(r * 0.7))],
        sheen_pts=[(cx - int(r * 0.8), cy - int(r * 0.6)),
                   (cx + int(r * 0.1), cy - int(r * 0.85)),
                   (cx - int(r * 0.1), cy - int(r * 0.1)),
                   (cx - int(r * 0.7), cy + int(r * 0.1))],
        ow=max(2, int(2 * s)),
    )
    # the carved inner-spiral groove — one bold ring so the curl reads as a SCROLL
    inner_r = int(r * 0.5)
    if teal_band:
        # sea-teal foam highlight rides the curl crest (the prow-foam band). WHY
        # the foam leads with the DEEPER TEAL_D and only a small TEAL crest: the
        # mid-body foam must read COOLER/deeper than the eye-paint rings so the
        # two teal uses stay separated by value and the foam never grows into a
        # second teal mass rivalling the eye cluster.
        pygame.draw.circle(surf, INK, (cx, cy), inner_r + max(1, int(2 * s)))
        pygame.draw.circle(surf, TEAL_D, (cx, cy), inner_r)
        pygame.draw.circle(surf, TEAL, (cx - int(inner_r * 0.25),
                           cy - int(inner_r * 0.25)), int(inner_r * 0.55))
        pygame.draw.circle(surf, TEAL_T, (cx - int(inner_r * 0.35),
                           cy - int(inner_r * 0.4)), max(1, int(inner_r * 0.24)))
        # a tiny coral pearl at the foam-eye is forbidden (coral is lip/medallion
        # only) — instead a salt-white spume fleck rides the crest tip
        pygame.draw.circle(surf, SALT_T, (cx - int(inner_r * 0.2),
                           cy - int(inner_r * 0.2)), max(1, int(inner_r * 0.2)))
    else:
        pygame.draw.circle(surf, INK, (cx, cy), inner_r + max(1, int(1 * s)))
        pygame.draw.circle(surf, GRV, (cx, cy), inner_r)
        pygame.draw.circle(surf, TEAK_D, (cx + int(inner_r * 0.25),
                           cy + int(inner_r * 0.25)), int(inner_r * 0.55))
        pygame.draw.circle(surf, TEAK_T, (cx - int(inner_r * 0.4),
                           cy - int(inner_r * 0.4)), max(1, int(inner_r * 0.25)))
    # salt-bleach wind-edge fleck on the tail hook (wind-blown spray)
    pygame.draw.line(surf, SALT, (cx + fr * int(r * 1.55), cy - int(r * 0.7)),
                     (cx + fr * int(r * 1.9), cy - int(r * 0.1)),
                     max(1, int(1.5 * s)))


# ── carved foam-scroll column band (the repeatable shaft unit) ────────────────
def scroll_shaft(surf, cx, top, bot, half_w, s, foam_at=None):
    """One stretch of the prow POST: a teak spine with a STACK of foam-curl
    scroll-commas climbing it, on-axis. This is what tiles — the creature shaft
    IS this. WHY a central spine plank behind the scrolls: it gives the stacked
    commas a continuous carved backbone so the column never reads as detached
    discs, and it carries the salt-bleach wind-edge down the leading side.
    `foam_at` (a set of indices) lights those scroll crests with the sea-teal
    PROW-FOAM band so the teal reads as a placed band, not every curl."""
    w = half_w * 2
    x0 = cx - half_w

    # central teak spine plank (the backbone the scrolls are carved onto)
    spine_hw = int(half_w * 0.46)
    spine = [(cx - spine_hw, top), (cx + spine_hw, top),
             (cx + spine_hw, bot), (cx - spine_hw, bot)]
    triad_blob(
        surf, TEAK, spine,
        core_pts=[(cx + int(spine_hw * 0.2), top), (cx + spine_hw, top),
                  (cx + spine_hw, bot), (cx + int(spine_hw * 0.2), bot)],
        sheen_pts=[(cx - spine_hw, top), (cx - int(spine_hw * 0.4), top),
                   (cx - int(spine_hw * 0.4), bot), (cx - spine_hw, bot)],
        ow=max(2, int(2 * s)),
    )
    # leading-edge salt-bleach wind line down the spine (the wind tell on shaft)
    pygame.draw.line(surf, SALT, (cx - spine_hw + max(1, int(2 * s)), top + int(4 * s)),
                     (cx - spine_hw + max(1, int(2 * s)), bot - int(4 * s)),
                     max(1, int(2 * s)))

    # the STACK of foam-curl scrolls, alternating facing so it reads as foam.
    # spacing chosen so a few BIG scrolls fill the column (survives 1x).
    r = int(half_w * 0.92)
    pitch = int(r * 1.5)
    i = 0
    cy = top + r + int(4 * s)
    while cy < bot - r:
        facing = 1 if (i % 2 == 0) else -1
        is_foam = (foam_at is not None and i in foam_at)
        foam_scroll(surf, cx, cy, r, s, facing=facing, teal_band=is_foam)
        cy += pitch
        i += 1


# ── the figurehead HEAD (hero head + the smaller mirrored gap-cap head) ───────
def figurehead_head(surf, cx, cy, s, lean_deg=0.0, lit=False, hair_fan=True):
    """The carved prow figurehead head: a forward-leaning chibi face with a
    medallion-marked brow, sea-teal painted eye-rings with a warm eye glow, a
    coral lip, and a swept-back fan of ~5 hard blade-lock hair scrolls. The head
    is drawn upright into a scratch buffer by the caller and rotated by
    `lean_deg` there, so this routine only lays out features around (cx, cy).
    `lit` brightens the eye glow + coral lip for the GAP-CAP partner-head. Big &
    few features = one clean face read at 1x. WHY ~5 blade-locks max and no
    streaming fringe: a fine fringe turns to noise at 1x; a few hard swept
    blades read as wind-blown hair AND echo the foam scrolls below."""

    fw, fh = int(94 * s), int(108 * s)
    fx0, fy0 = cx - fw // 2, cy - fh // 2

    # swept-back HAIR FAN first (behind the face) — ~5 hard blade-locks sweeping
    # up-and-back, echoing the foam scrolls. Drawn before the face so the face
    # plate overlaps their roots cleanly.
    if hair_fan:
        # WHY exactly 5 CHUNKY locks with visible teak gaps and a SPARSE salt
        # tell: round-1 fanned more locks and salt-edged every one, so at 32px
        # night they collapsed into a single dark fringe with no internal read.
        # Wider root spacing + fatter blades + teak gaps keep the fan reading as
        # distinct swept HAIR (the motion hook), not noise.
        n = 5
        for k in range(n):
            t = k / (n - 1)            # 0..1 top->bottom along the back of head
            root_x = fx0 + int(fw * 0.18)
            root_y = fy0 + int(fh * (0.10 + 0.66 * t))
            # blades sweep BACK (negative x) and the upper ones reach highest
            reach = (1.0 - 0.42 * t)
            tip_x = root_x - int(fw * (0.66 * reach))
            tip_y = root_y - int(fh * (0.32 * reach)) + int(fh * 0.10 * t)
            mid_x = root_x - int(fw * 0.36 * reach)
            mid_y = root_y - int(fh * 0.04)
            # fatter root + tapered tip so each lock survives downscale as a slab
            blade = [(root_x, root_y - int(10 * s)),
                     (root_x, root_y + int(9 * s)),
                     (mid_x, mid_y + int(8 * s)),
                     (tip_x, tip_y + int(4 * s)),
                     (tip_x - int(4 * s), tip_y - int(3 * s)),
                     (mid_x, mid_y - int(8 * s))]
            triad_blob(surf, TEAK_D, blade,
                       sheen_pts=[(root_x, root_y - int(7 * s)),
                                  (mid_x, mid_y - int(5 * s)),
                                  (tip_x, tip_y - int(1 * s)),
                                  (mid_x, mid_y - int(2 * s))],
                       ow=max(2, int(2 * s)))
            # salt-bleach wind-edge ONLY on the top two locks (sparse wind tell);
            # the lower locks keep clean teak gaps between them.
            if k <= 1:
                pygame.draw.line(surf, SALT, (mid_x, mid_y - int(7 * s)),
                                 (tip_x, tip_y - int(2 * s)), max(1, int(1.5 * s)))

    # face plate — a forward-jutting prow-bust block (jaw leads, brow set back)
    face = [(fx0 + int(20 * s), fy0),                       # brow top-left
            (fx0 + fw - int(4 * s), fy0 + int(8 * s)),      # brow top-right (leads)
            (fx0 + fw, fy0 + int(40 * s)),                  # cheek out front
            (fx0 + fw - int(6 * s), fy0 + fh - int(20 * s)),# jaw front
            (fx0 + fw - int(24 * s), fy0 + fh),             # chin
            (fx0 + int(12 * s), fy0 + fh - int(10 * s)),    # under-jaw back
            (fx0, fy0 + int(54 * s)),                       # back of head
            (fx0 + int(6 * s), fy0 + int(20 * s))]          # back-brow
    # WHY the cheek core stays TEAK and only a thin top-left edge lifts: the
    # round-1 sheen flooded the whole cheek mass to a near-cream L~204 plate;
    # the cap then read as a separate pale stone mask on a wood post. The sheen
    # polygon is now a NARROW top-left rim sliver at a capped warm light-teak
    # (RIM_TEAK ~L176, within ~25 L of the body), so teak is the dominant value
    # across the entire face — exactly as on the hero body.
    triad_blob(
        surf, TEAK, face,
        core_pts=[(cx + int(6 * s), fy0 + int(6 * s)),
                  (fx0 + fw - int(4 * s), fy0 + int(8 * s)),
                  (fx0 + fw, fy0 + int(40 * s)),
                  (fx0 + fw - int(6 * s), fy0 + fh - int(20 * s)),
                  (fx0 + fw - int(24 * s), fy0 + fh),
                  (cx + int(6 * s), fy0 + fh - int(6 * s))],
        ow=max(2, int(2 * s)),
    )
    # restrained warm light-teak rim-sheen — a thin top-left wind-facing sliver
    # only (back-brow down the back of the head), NOT a full-cheek wash.
    rim = [(fx0 + int(20 * s), fy0 + int(2 * s)),
           (fx0 + int(30 * s), fy0 + int(2 * s)),
           (fx0 + int(16 * s), fy0 + int(28 * s)),
           (fx0 + int(10 * s), fy0 + int(50 * s)),
           (fx0 + int(12 * s), fy0 + fh - int(28 * s)),
           (fx0 + int(4 * s), fy0 + int(52 * s)),
           (fx0 + int(6 * s), fy0 + int(22 * s))]
    pygame.draw.polygon(surf, RIM_TEAK, rim)
    # salt-bleach is now an EDGE-only fleck on the very wind-facing back edge —
    # a thin cool-pale line, the third-tier accent it's specced to be.
    pygame.draw.line(surf, SALT,
                     (fx0 + int(7 * s), fy0 + int(22 * s)),
                     (fx0 + int(11 * s), fy0 + fh - int(30 * s)),
                     max(1, int(1.5 * s)))

    # carved brow ridge + coral MEDALLION at brow centre (the small warm focal)
    brow_y = fy0 + int(30 * s)
    brow = [(fx0 + int(14 * s), brow_y), (cx + int(6 * s), brow_y - int(7 * s)),
            (fx0 + fw - int(8 * s), brow_y - int(2 * s)),
            (fx0 + fw - int(8 * s), brow_y + int(8 * s)),
            (cx, brow_y + int(2 * s)),
            (fx0 + int(14 * s), brow_y + int(8 * s))]
    triad_blob(surf, TEAK_D, brow,
               sheen_pts=[(fx0 + int(16 * s), brow_y - int(1 * s)),
                          (cx, brow_y - int(6 * s)),
                          (cx, brow_y + int(1 * s)),
                          (fx0 + int(16 * s), brow_y + int(3 * s))],
               ow=max(1, int(1.5 * s)))
    # WHY a bigger medallion: at true 32px the round-1 dot nearly vanished, so
    # it's enlarged to read as a deliberate single coral focal dot on downscale.
    med_r = int(11 * s)
    med_y = fy0 + int(15 * s)
    pygame.draw.circle(surf, INK, (cx + int(4 * s), med_y), med_r + max(1, int(2 * s)))
    pygame.draw.circle(surf, CORAL, (cx + int(4 * s), med_y), med_r)
    pygame.draw.circle(surf, CORAL_D, (cx + int(4 * s) + int(med_r * 0.3),
                       med_y + int(med_r * 0.3)), int(med_r * 0.55))
    pygame.draw.circle(surf, CORAL_T, (cx + int(4 * s) - int(med_r * 0.35),
                       med_y - int(med_r * 0.35)), max(1, int(med_r * 0.32)))

    # EYES — warm glow with a SEA-TEAL painted ring (the eye-paint band use)
    eye_dx = int(20 * s)
    eye_y = fy0 + int(50 * s)
    er = int(15 * s)
    # WHY the lit eyes carry more glow now: with the cap bleach pulled back to a
    # thin rim, the WARM eye glow does the "lift the cap so it reads at night"
    # job (per the ruling) instead of a pale face wash.
    glow_a = 185 if lit else 95
    glow_r = int(er * (2.35 if lit else 1.5))
    glow = pygame.Surface((glow_r * 4, glow_r * 4), pygame.SRCALPHA)
    for rr in range(glow_r, 0, -1):
        a = int(glow_a * (1 - rr / glow_r))
        pygame.draw.circle(glow, (*EYEGLOW, a), (glow_r * 2, glow_r * 2), rr)
    for sgn in (-1, 1):
        ex = cx + int(6 * s) + sgn * eye_dx
        surf.blit(glow, (ex - glow_r * 2, eye_y - glow_r * 2),
                  special_flags=pygame.BLEND_ADD)
    for sgn in (-1, 1):
        ex = cx + int(6 * s) + sgn * eye_dx
        # sea-teal painted socket ring (carved + painted)
        pygame.draw.circle(surf, INK, (ex, eye_y), er + max(1, int(2 * s)))
        pygame.draw.circle(surf, TEAL, (ex, eye_y), er)
        pygame.draw.circle(surf, TEAL_D, (ex + int(er * 0.3), eye_y + int(er * 0.3)),
                           int(er * 0.55))
        pygame.draw.circle(surf, INK, (ex, eye_y), er, max(1, int(2 * s)))
        # warm glowing eyeball inside the teal ring (warm focal vs cool paint)
        eb = int(er * (0.62 if lit else 0.56))
        pygame.draw.circle(surf, EYEGLOW_D, (ex, eye_y), eb + max(1, int(1 * s)))
        pygame.draw.circle(surf, EYEGLOW, (ex, eye_y), eb)
        pygame.draw.circle(surf, INK, (ex + int(2 * s), eye_y),
                           int(eb * 0.42))
        pygame.draw.circle(surf, (255, 250, 238),
                           (ex - int(eb * 0.3), eye_y - int(eb * 0.3)),
                           max(1, int(eb * 0.22)))

    # short carved NOSE down the lean-front (a small wedge, not a bulb)
    ny0 = eye_y + int(6 * s)
    nose = [(cx + int(6 * s), ny0),
            (cx + int(16 * s), ny0 + int(18 * s)),
            (cx + int(4 * s), ny0 + int(22 * s))]
    pygame.draw.polygon(surf, TEAK_D, nose)
    pygame.draw.polygon(surf, INK, nose, max(1, int(1.5 * s)))
    pygame.draw.line(surf, TEAK_T, (cx + int(6 * s), ny0),
                     (cx + int(5 * s), ny0 + int(20 * s)), max(1, int(1 * s)))

    # CORAL lip — a determined set mouth (the second small warm focal). WHY
    # thicker: the round-1 lip line went sub-pixel at true 32px; a fatter bar
    # keeps the coral lip present on downscale.
    my = fy0 + int(88 * s)
    mw = int(26 * s)
    mh = int(12 * s) if lit else int(10 * s)
    if lit:
        mglow = pygame.Surface((mw * 4, mh * 6), pygame.SRCALPHA)
        for rr in range(int(mw * 1.2), 0, -1):
            a = int(110 * (1 - rr / (mw * 1.2)))
            pygame.draw.circle(mglow, (*EYEGLOW, a), (mw * 2, mh * 3), rr)
        surf.blit(mglow, (cx - mw * 2 + int(6 * s), my - mh * 3 + int(4 * s)),
                  special_flags=pygame.BLEND_ADD)
    mouth = [(cx - int(mw * 0.7) + int(6 * s), my),
             (cx + mw + int(6 * s), my - int(2 * s)),
             (cx + mw + int(6 * s), my + mh),
             (cx - int(mw * 0.7) + int(6 * s), my + mh + int(2 * s))]
    pygame.draw.polygon(surf, INK, mouth)
    pygame.draw.polygon(surf, CORAL, mouth)
    pygame.draw.polygon(surf, CORAL_D,
                        [(cx - int(mw * 0.7) + int(6 * s), my + int(mh * 0.5)),
                         (cx + mw + int(6 * s), my + int(mh * 0.4)),
                         (cx + mw + int(6 * s), my + mh),
                         (cx - int(mw * 0.7) + int(6 * s), my + mh + int(2 * s))])
    pygame.draw.line(surf, CORAL_T,
                     (cx - int(mw * 0.6) + int(6 * s), my),
                     (cx + int(mw * 0.4) + int(6 * s), my - int(1 * s)),
                     max(1, int(1 * s)))


# ── the full hero creature: leaning figurehead atop a heavy scroll base ───────
def draw_muljang(surf, cx, cy, s):
    """The whole prow-rider: a forward-LEANING figurehead head riding the top of
    a tall carved foam-scroll POST whose MASS sits low (a heavy stacked scroll
    base) so the lean never makes it top-heavy. The shaft is the same scroll
    column the pillar tiles. `s` is a unit scale around a ~250-unit figure."""
    half_w = int(38 * s)
    post_top = cy - int(34 * s)
    post_bot = cy + int(168 * s)

    # the carved foam-scroll body shaft — light ONE mid crest with the foam band
    # so the mid-body teal stays a small clustered accent, not a second mass.
    scroll_shaft(surf, cx, post_top, post_bot, half_w, s, foam_at={2})

    # HEAVY scroll base — a broad pair of big foam-curls + a wide plinth so the
    # mass clearly sits low and balances the leaning head above (re-spec HARD).
    base_y = post_bot - int(8 * s)
    big_r = int(half_w * 1.35)
    foam_scroll(surf, cx - int(half_w * 0.7), base_y, big_r, s, facing=-1, teal_band=True)
    foam_scroll(surf, cx + int(half_w * 0.7), base_y, big_r, s, facing=1, teal_band=False)
    plinth = [(cx - half_w - int(20 * s), post_bot + int(14 * s)),
              (cx + half_w + int(20 * s), post_bot + int(14 * s)),
              (cx + half_w + int(12 * s), post_bot + int(34 * s)),
              (cx - half_w - int(12 * s), post_bot + int(34 * s))]
    triad_blob(surf, TEAK_D, plinth,
               sheen_pts=[(cx - half_w - int(18 * s), post_bot + int(16 * s)),
                          (cx - int(4 * s), post_bot + int(16 * s)),
                          (cx - int(4 * s), post_bot + int(30 * s)),
                          (cx - half_w - int(12 * s), post_bot + int(30 * s))],
               ow=max(2, int(2 * s)))

    # the figurehead head — drawn upright into a buffer, leaned ~15deg toward the
    # gap (forward = the lean direction), pivoting near the neck so the head tips
    # but the mass below stays put.
    hsz = int(150 * s)
    hbuf = pygame.Surface((hsz, hsz), pygame.SRCALPHA)
    figurehead_head(hbuf, hsz // 2, hsz // 2, s, lit=False)
    hbuf = pygame.transform.rotate(hbuf, -15)  # ~15deg lean (forward = right)
    hw, hh = hbuf.get_size()
    surf.blit(hbuf, (cx - hw // 2 + int(6 * s), post_top - int(70 * s) - hh // 2 + hsz // 2))


# ── the pillar: same scroll post, mirrored, SMALLER partner-head gap-cap ──────
def draw_pillar_segment(surf, cx, top, bot, half_w, s, cap="bottom"):
    """A shaft stretch of the prow POST that meets the gap with a SMALLER twin
    mirrored partner-HEAD cap (eyes + lip LIT at the gap). The shaft is the same
    foam-scroll column as the creature body, so creature == pillar. The cap head
    is rendered at ~78% of the hero head and tucked to the axis so the gap-cap
    stays bottom-light (re-spec). `cap` end faces the gap."""
    face_room = int(108 * s)
    cap_scale = 0.78                       # SMALLER mirrored head (re-spec)
    if cap == "bottom":
        shaft_top, shaft_bot = top, bot - face_room
        head_cy = bot - int(face_room * 0.42)
        flip = False
    else:
        shaft_top, shaft_bot = top + face_room, bot
        head_cy = top + int(face_room * 0.42)
        flip = True
    # foam band placed on the crests nearest the gap (band reads at the cap edge)
    scroll_shaft(surf, cx, shaft_top, shaft_bot, half_w, s, foam_at={0, 2})

    # smaller partner-head, leaned toward the gap, rendered to a scratch buffer
    # so it can be FLIPPED for the opposite cap (proves the true mirror).
    hsz = int(150 * s)
    hbuf = pygame.Surface((hsz, hsz), pygame.SRCALPHA)
    figurehead_head(hbuf, hsz // 2, hsz // 2, s * cap_scale, lit=True)
    hbuf = pygame.transform.rotate(hbuf, -15)
    if flip:
        hbuf = pygame.transform.flip(hbuf, False, True)
    hw, hh = hbuf.get_size()
    surf.blit(hbuf, (cx - hw // 2 + int(5 * s), int(head_cy) - hh // 2))


# ── sky helpers (procedural vertical gradient via per-row fills) ─────────────
def sky(surf, rect, top_col, bot_col):
    x, y, w, h = rect
    for j in range(h):
        surf.fill(lerp(top_col, bot_col, j / max(1, h - 1)), (x, y + j, w, 1))


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
    sheet.blit(font_big.render("MULJANG", True, LABEL), (22, 12))
    sheet.blit(font_sm.render(
        "prow-rider ship-figurehead spirit  ·  cooler-teak + sea-teal foam band + coral lip/medallion + warm eye glow  ·  round 2  ·  teak-dominant cap, warm-glow night lift",
        True, LABEL_DIM), (200, 26))

    # (a) BIG hero sprite ------------------------------------------------------
    hb_w, hb_h = 300, 470
    big = pygame.Surface((hb_w * SS, hb_h * SS), pygame.SRCALPHA)
    draw_muljang(big, hb_w * SS // 2, int(hb_h * SS * 0.48), 1.28 * SS)
    hero = pygame.transform.smoothscale(big, (hb_w, hb_h))
    hero = grow_outline(hero, INK + (255,), 1)
    sheet.blit(hero, (10, 72))
    sheet.blit(font.render("(a) Hero — leaning figurehead on heavy scroll base", True, LABEL), (16, 548))
    sheet.blit(font_sm.render("~15deg lean + 5 chunky blade-locks; teak-dominant cap face;", True, LABEL_DIM), (16, 572))
    sheet.blit(font_sm.render("salt-bleach now a thin rim only; warm eye glow lifts the cap", True, LABEL_DIM), (16, 588))

    # (b) pillar assembled — top segment + gap + bottom segment, MIRRORED ------
    pcx = 460
    seg_half = int(32)
    seg_h = 250
    seg_top_y = 72
    gap_px = 96
    # top segment (cap faces DOWN toward the gap = flipped partner-head)
    topbuf = pygame.Surface((150 * SS, seg_h * SS), pygame.SRCALPHA)
    draw_pillar_segment(topbuf, 75 * SS, 4 * SS, (seg_h - 4) * SS, seg_half * SS, 1.0 * SS, cap="top")
    topimg = pygame.transform.smoothscale(topbuf, (150, seg_h))
    topimg = grow_outline(topimg, INK + (255,), 1)
    sheet.blit(topimg, (pcx - 75, seg_top_y))
    # bottom segment (cap faces UP toward the gap = upright partner-head)
    botbuf = pygame.Surface((150 * SS, seg_h * SS), pygame.SRCALPHA)
    draw_pillar_segment(botbuf, 75 * SS, 4 * SS, (seg_h - 4) * SS, seg_half * SS, 1.0 * SS, cap="bottom")
    botimg = pygame.transform.smoothscale(botbuf, (150, seg_h))
    botimg = grow_outline(botimg, INK + (255,), 1)
    sheet.blit(botimg, (pcx - 75, seg_top_y + seg_h + gap_px))

    # gap guide lines
    gap_y0, gap_y1 = seg_top_y + seg_h, seg_top_y + seg_h + gap_px
    for gy in (gap_y0, gap_y1):
        pygame.draw.line(sheet, (150, 154, 160), (pcx - 92, gy), (pcx + 92, gy), 1)
    sheet.blit(font_sm.render("<- gap ->", True, LABEL_DIM), (pcx - 24, (gap_y0 + gap_y1) // 2 - 7))
    by = seg_top_y + 2 * seg_h + gap_px + 10
    sheet.blit(font.render("(b) Pillar — MIRRORED", True, LABEL), (pcx - 92, by))
    sheet.blit(font_sm.render("tileable foam-scroll shaft; SMALLER (78%)", True, LABEL_DIM), (pcx - 92, by + 24))
    sheet.blit(font_sm.render("mirrored partner-head cap, eyes/lip lit", True, LABEL_DIM), (pcx - 92, by + 40))

    # (c) TRUE 32px gameplay-scale chips — day sky + night sky -----------------
    panel_x = 660
    pw = W - panel_x - 14
    pygame.draw.rect(sheet, PANEL, (panel_x, 72, pw, 372))
    sheet.blit(font.render("(c) True 32px gameplay chip", True, LABEL), (panel_x + 14, 82))
    sheet.blit(font_sm.render("leaning head + scroll base read", True, LABEL_DIM), (panel_x + 14, 104))

    # render at a true ~32px tall read for the gameplay collision footprint.
    def chip32():
        cs = 44
        buf = pygame.Surface((cs * SS, cs * SS), pygame.SRCALPHA)
        draw_muljang(buf, cs * SS // 2, int(cs * SS * 0.52), (32 / 250.0) * SS)
        img = pygame.transform.smoothscale(buf, (cs, cs))
        return grow_outline(img, INK + (255,), 1)

    chip = chip32()
    cs = chip.get_width()
    chip4 = pygame.transform.scale(chip, (cs * 4, cs * 4))

    def chip_row(sky_top, sky_bot, sy, lbl, lbl_col):
        sw, sh = 130, 132
        sx = panel_x + 22
        sky(sheet, (sx, sy, sw, sh), sky_top, sky_bot)
        pygame.draw.rect(sheet, INK, (sx, sy, sw, sh), 1)
        sheet.blit(chip, (sx + sw // 2 - cs // 2, sy + sh // 2 - cs // 2))
        sheet.blit(font_sm.render(lbl, True, lbl_col), (sx + 4, sy + sh - 16))
        zx = sx + sw + 18
        zw = cs * 4
        if zx + zw > panel_x + pw - 10:
            zw = panel_x + pw - 10 - zx
            chip_z = pygame.transform.scale(chip, (cs * 4, cs * 4)).subsurface((0, 0, zw, min(cs * 4, sh + 24)))
            sheet.blit(chip_z, (zx, sy))
        else:
            sheet.blit(chip4, (zx, sy - 6))
        return sx, zx

    cy0 = 132
    chip_row(DAY_SKY_T, DAY_SKY_B, cy0, "day sky", INK)
    sheet.blit(font_sm.render("4x zoom ->", True, LABEL_DIM), (panel_x + 22 + 130 + 18, cy0 - 18))
    cy1 = cy0 + 168
    chip_row(NIGHT_T, NIGHT_B, cy1, "night sky", LABEL)
    sheet.blit(font_sm.render("warm eyes/coral lip anchor the night read",
                              True, LABEL_DIM), (panel_x + 22, cy1 + 138))

    # palette swatch row -------------------------------------------------------
    pal_y = 458
    pygame.draw.rect(sheet, PANEL, (panel_x, pal_y, pw, 196))
    sheet.blit(font.render("Pinned palette", True, LABEL), (panel_x + 14, pal_y + 10))
    swatches = [
        (TEAK, "teak (cooler)"), (TEAK_D, "deep teak"),
        (TEAK_T, "teak sheen"), (GRV, "scroll groove"),
        (TEAL, "sea-teal foam"), (TEAL_D, "deep sea-teal"),
        (CORAL, "coral lip/med."), (CORAL_D, "deep coral"),
        (SALT, "salt-bleach"), (EYEGLOW, "warm eye glow"),
        (INK, "ink keyline"),
    ]
    sx, sy = panel_x + 14, pal_y + 40
    for i, (c, name) in enumerate(swatches):
        col = i % 2
        row = i // 2
        rx = sx + col * 150
        ry = sy + row * 28
        pygame.draw.rect(sheet, INK, (rx - 1, ry - 1, 22, 22))
        pygame.draw.rect(sheet, c, (rx, ry, 20, 20))
        sheet.blit(font_sm.render(name, True, LABEL), (rx + 27, ry + 4))

    # construction note panel — full-width strip across the bottom ------------
    note_y = 668
    pygame.draw.rect(sheet, PANEL, (10, note_y, W - 20, 222))
    sheet.blit(font.render("Construction notes", True, LABEL), (26, note_y + 10))
    notes_l = [
        "• R2 FIX: salt-bleach restrained to a thin top-left rim sliver;",
        "  cap face stays TEAK-dominant (warm light-teak rim ~L176, not",
        "  the L204 cream) — within ~25 L of the body, same carved wood.",
        "• R2: warm EYE GLOW now carries the cap's night lift (brighter",
        "  lit glow), not a pale face wash.",
        "• Only MOTION read: ~15deg lean + 5 CHUNKY blade-locks w/ teak",
        "  gaps + sparse salt tell (no solid fringe at 32px).",
    ]
    notes_r = [
        "• Re-spec: lean balanced by a HEAVY low scroll base — mass low,",
        "  head tips to the gap; gap-cap NOT top-heavy.",
        "• Teak kept a hair COOLER/greyer than Haedung's honey-cedar.",
        "• Sea-teal split by VALUE: foam = DEEPER TEAL_D crest (one mid",
        "  crest, clustered), eye-paint = brighter ring; never a body fill.",
        "• R2: coral medallion enlarged + lip thickened so the single",
        "  coral focal survives true-32px downscale.",
    ]
    for i, line in enumerate(notes_l):
        sheet.blit(font_sm.render(line, True, LABEL_DIM), (26, note_y + 40 + i * 19))
    for i, line in enumerate(notes_r):
        sheet.blit(font_sm.render(line, True, LABEL_DIM), (540, note_y + 40 + i * 19))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_2.png")
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
