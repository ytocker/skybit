"""
Round-1 concept renderer for VETALA — the inverted bat-hung charnel revenant
(Jiangshi-epic set, concept #5). Headless Pygame; supersample at SS=6 then
smoothscale, matching the elevated house grammar (chibi, flat saturated fills,
hard 1-2px ink keyline, dark-core -> flat-fill -> top-left rim-sheen triad,
1px alpha-grown outline). Epic = bigger render scale + more geometry + richer
triad + stronger glow than the shipped Jiangshi source.

WHY upside-down is the whole point: this is the single UPENDED silhouette across
both boss batches — clawed grip-feet hooked at the TOP, a wrapped tapering body
hanging DOWN, the fanged chibi head at the BOTTOM. The head is drawn so the eyes
read right-way-up even though the body is inverted (the gravity gag: tongue
lolls UP toward the body, not down). The mass is bottom-weighted like a real
pendulum so it never reads top-heavy.

WHY the cross-set palette discipline: Citipati, Xinniang and Vetala all sit in
the red->amber arc, so they are separated by VALUE/SATURATION, not hue. Vetala
is pale dusty bone-wrap dominant; its only red is a DARK, DESATURATED ox-blood
maroon membrane accent (deliberately duller than Xinniang's saturated
vermilion) plus a hot-amber eye/gap glow. The red never grows into a second
saturated mass.

WHY a standalone script: review art must never enter the shipped bundle, so it
lives under docs/ and reuses only colour math, not runtime sprite modules.
"""
import math
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
pygame.init()

# ── PINNED PALETTE ───────────────────────────────────────────────────────────
# dusty bone-wrap dominant; ox-blood maroon a DARK desaturated accent (kept
# clearly duller/cooler in saturation than Xinniang's vermilion); hot-amber the
# only warm focal; slate branch is a prop-only neutral.
WRAP      = (214, 200, 168)   # dusty bone-wrap base (the dominant mass)
WRAP_D    = (150, 136, 110)   # bone-wrap shade (dark core)
WRAP_DD   = (104,  92,  74)   # deepest wrap groove between bands
WRAP_T    = (238, 228, 200)   # bone-wrap rim-sheen helper (top-left)
FLESH     = (176, 150, 132)   # exposed grey-tan charnel flesh under the wraps
FLESH_D   = (120,  98,  88)

# the face owns its OWN brighter ivory value (not the dull body flesh) so the
# head pops off BOTH the dark-blue night sky and the maroon wings at true 32px —
# the brief's lever is VALUE/GEOMETRY, never a maroon brighten.
FACE      = (236, 224, 196)   # bright bone-ivory face ball (the 1x value anchor)
FACE_D    = (176, 158, 128)   # face shade core
FACE_T    = (252, 246, 226)   # face rim-sheen

MAROON    = (108,  40,  46)   # DARK desaturated ox-blood membrane (NOT vermilion)
MAROON_D  = ( 70,  26,  32)   # deep ox-blood shade
MAROON_T  = (140,  62,  68)   # muted maroon rim-sheen (still desaturated)
# a thin COOL-BONE edge sheen on the wing membranes so their silhouette survives
# against the ~20,30,55 night sky WITHOUT brightening the maroon hue itself.
MEMB_RIM  = (172, 166, 158)   # cool greyed-bone wing-edge rim (value, not hue)

AMBER     = (244, 176,  60)   # hot-amber eye / gap focal
AMBER_BR  = (255, 214, 120)   # brightest amber core (night anchor)
AMBER_D   = (188, 120,  36)

SLATE     = ( 96, 100, 108)   # slate charnel-branch (prop only)
SLATE_D   = ( 62,  66,  74)
SLATE_T   = (132, 138, 148)

FANG      = (242, 236, 220)   # bone-white fangs
INK       = ( 28,  22,  30)   # hard ink keyline (brief-specified)
NAIL      = ( 40,  34,  40)   # claw horn

BG        = (108, 110, 114)   # neutral grey review backdrop
PANEL     = ( 84,  86,  92)
DAY_SKY   = (126, 190, 222)   # bright day sky for the gameplay chip
NIGHT_SKY = ( 26,  30,  52)   # dark night sky for the gameplay chip
LABEL     = (240, 240, 242)
LABEL_DIM = (196, 198, 204)


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
    ring = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    for (ox, oy) in outline_pts:
        pygame.draw.circle(ring, color, (ox, oy), px)
    ring.blit(surf.copy(), (0, 0))
    return ring


def triad_blob(surf, color, pts, sheen_pts=None, core_pts=None, outline=True, ow=2):
    """Flat fill + optional dark-core + top-left rim-sheen + ink keyline — the
    house triad. Core darkens toward INK; sheen lifts toward white."""
    if outline:
        pygame.draw.polygon(surf, INK, pts)
    pygame.draw.polygon(surf, color, pts)
    if core_pts:
        pygame.draw.polygon(surf, lerp(color, INK, 0.42), core_pts)
    if sheen_pts:
        pygame.draw.polygon(surf, lerp(color, (255, 255, 255), 0.36), sheen_pts)
    if outline:
        pygame.draw.polygon(surf, INK, pts, ow)


def amber_glow(surf, cx, cy, r, intensity=120):
    """Additive hot-amber halo — the single warm focal, pushed stronger than the
    source so it anchors on a dark night sky."""
    glow = pygame.Surface((r*4, r*4), pygame.SRCALPHA)
    for rr in range(r*2, 0, -1):
        a = int(intensity * (1 - rr/(r*2)) ** 1.5)
        pygame.draw.circle(glow, (*AMBER, a), (r*2, r*2), rr)
    surf.blit(glow, (cx-r*2, cy-r*2), special_flags=pygame.BLEND_ADD)


# ── shared body parts ─────────────────────────────────────────────────────────
def grip_claw_foot(surf, fx, fy, sgn, s):
    """One clawed grip-foot HOOKED over the branch at the TOP — the anchor the
    whole pendulum hangs from. `sgn` -1/+1 splays the toes left/right. Drawn as
    a stubby flesh ankle + three down-curling horn claws gripping over."""
    # short flesh ankle stub rising into the branch
    ankle = [(fx - int(7*s), fy),
             (fx + int(7*s), fy),
             (fx + int(5*s), fy + int(13*s)),
             (fx - int(5*s), fy + int(13*s))]
    triad_blob(surf, FLESH, ankle,
               core_pts=[(fx + int(1*s), fy + int(2*s)),
                         (fx + int(7*s), fy),
                         (fx + int(5*s), fy + int(13*s)),
                         (fx + int(1*s), fy + int(13*s))],
               sheen_pts=[(fx - int(6*s), fy + int(1*s)),
                          (fx - int(1*s), fy + int(1*s)),
                          (fx - int(2*s), fy + int(8*s)),
                          (fx - int(6*s), fy + int(8*s))],
               ow=max(2, int(2*s)))
    # three horn claws curling UP-and-OVER the branch (the hook grip)
    for i in (-1, 0, 1):
        bx = fx + i * int(6*s)
        claw = [(bx - int(3*s), fy),
                (bx + int(3*s), fy),
                (bx + int(4*s) + sgn*int(2*s), fy - int(11*s)),
                (bx + sgn*int(5*s), fy - int(17*s)),
                (bx - int(2*s) + sgn*int(4*s), fy - int(12*s))]
        triad_blob(surf, NAIL, claw,
                   sheen_pts=[(bx - int(2*s), fy - int(2*s)),
                              (bx + int(1*s), fy - int(2*s)),
                              (bx + int(2*s), fy - int(9*s)),
                              (bx - int(1*s), fy - int(9*s))],
                   ow=max(1, int(1.5*s)))


def furled_wing_arm(surf, sx, sy, sgn, s):
    """One arm folded UP alongside the hanging body as a furled bat-wing
    membrane — the dark ox-blood maroon accent. Reaches from a shoulder near the
    head (low) up toward the feet (high), hugging the body so the silhouette
    stays a tight pendulum. Rib-struts segment the membrane (elevated detail)."""
    # membrane sweeps from the shoulder (sy, near the head/bottom) UP the body
    top = sy - int(96*s)              # toward the feet/top
    wing = [
        (sx,                      sy),
        (sx + sgn*int(22*s),      sy - int(18*s)),
        (sx + sgn*int(30*s),      sy - int(48*s)),
        (sx + sgn*int(24*s),      top + int(14*s)),
        (sx + sgn*int(9*s),       top),
        (sx + sgn*int(2*s),       top + int(22*s)),
        (sx - sgn*int(2*s),       sy - int(40*s)),
    ]
    triad_blob(
        surf, MAROON, wing,
        core_pts=[(sx + sgn*int(2*s),  sy - int(38*s)),
                  (sx + sgn*int(22*s), sy - int(46*s)),
                  (sx + sgn*int(18*s), top + int(16*s)),
                  (sx + sgn*int(6*s),  top + int(20*s))],
        sheen_pts=[(sx + sgn*int(3*s),  sy - int(6*s)),
                   (sx + sgn*int(16*s), sy - int(16*s)),
                   (sx + sgn*int(20*s), sy - int(40*s)),
                   (sx + sgn*int(6*s),  sy - int(36*s))],
        ow=max(2, int(2*s)),
    )
    # thin cool-bone rim along the OUTER membrane edge so the maroon wing keeps a
    # readable silhouette against the dark-blue night sky (value, not a hue lift).
    outer_edge = [
        (sx + sgn*int(22*s), sy - int(18*s)),
        (sx + sgn*int(30*s), sy - int(48*s)),
        (sx + sgn*int(24*s), top + int(14*s)),
        (sx + sgn*int(9*s),  top),
    ]
    pygame.draw.lines(surf, MEMB_RIM, False, outer_edge, max(1, int(1.4*s)))
    # rib-struts — three slate finger-bones fanning through the membrane
    for k in range(3):
        t = 0.2 + k*0.3
        rx = sx + sgn*int((10 + k*7)*s)
        r0 = (sx + sgn*int(2*s), int(sy - 36*s + (top + 18*s - (sy - 36*s))*0.0))
        r1 = (rx, int(sy - (24 + k*22)*s))
        pygame.draw.line(surf, SLATE_D, r0, r1, max(2, int(2.6*s)))
        pygame.draw.line(surf, SLATE_T, r0, r1, max(1, int(1*s)))
        pygame.draw.circle(surf, SLATE, r1, max(2, int(2.4*s)))
        pygame.draw.circle(surf, INK, r1, max(2, int(2.4*s)), max(1, int(1*s)))


def draw_vetala(surf, cx, cy, s):
    """The inverted bat-hung revenant. `cy` is roughly the vertical centre of the
    ~150-unit figure; feet hook at the TOP, head hangs at the BOTTOM. `s` is the
    unit scale. Drawn back-to-front: branch grip -> body -> wings -> head."""

    top_y    = cy - int(74*s)        # where the feet hook over the branch
    head_cy  = cy + int(70*s)        # the chibi head, hanging low (bottom-weighted)
    body_top = top_y + int(14*s)     # body starts just under the feet
    body_bot = head_cy - int(22*s)   # body tapers down into the head

    # --- the branch the feet grip (drawn first, sits behind the feet) ---
    br_y = top_y + int(2*s)
    pygame.draw.rect(surf, INK, (cx - int(34*s), br_y - int(9*s), int(68*s), int(18*s)))
    pygame.draw.rect(surf, SLATE, (cx - int(33*s), br_y - int(8*s), int(66*s), int(16*s)))
    pygame.draw.rect(surf, SLATE_D, (cx - int(33*s), br_y + int(1*s), int(66*s), int(7*s)))
    pygame.draw.rect(surf, SLATE_T, (cx - int(33*s), br_y - int(8*s), int(66*s), int(3*s)))

    # --- two clawed grip-feet hooked over the branch at the TOP ---
    grip_claw_foot(surf, cx - int(15*s), br_y + int(6*s), -1, s)
    grip_claw_foot(surf, cx + int(15*s), br_y + int(6*s), +1, s)

    # --- wrapped tapering body HANGING DOWN (the bone-wrap dominant mass) ---
    # widest at the top (hips, near the feet), tapering toward the neck/head so
    # the form reads as a hanging, swaddled cocoon — a pendulum bob.
    half_top = int(26*s)
    half_bot = int(20*s)
    body = [
        (cx - half_top, body_top),
        (cx + half_top, body_top),
        (cx + int(23*s), body_top + int(40*s)),
        (cx + half_bot,  body_bot),
        (cx + int(14*s), body_bot + int(10*s)),
        (cx - int(14*s), body_bot + int(10*s)),
        (cx - half_bot,  body_bot),
        (cx - int(23*s), body_top + int(40*s)),
    ]
    triad_blob(
        surf, WRAP, body,
        core_pts=[(cx + int(2*s),  body_top + int(4*s)),
                  (cx + half_top,  body_top + int(2*s)),
                  (cx + int(23*s), body_top + int(40*s)),
                  (cx + half_bot,  body_bot),
                  (cx + int(2*s),  body_bot)],
        sheen_pts=[(cx - half_top + int(3*s), body_top + int(3*s)),
                   (cx - int(2*s),            body_top + int(3*s)),
                   (cx - int(4*s),            body_bot - int(6*s)),
                   (cx - half_top + int(7*s), body_bot - int(20*s))],
        ow=max(2, int(2.2*s)),
    )

    # wrap-banding — hard diagonal binding wraps with deep grooves between (the
    # signature charnel-wrap texture; alternating bands tilt opposite ways).
    n_bands = 6
    span = body_bot + int(8*s) - body_top
    for i in range(n_bands):
        t = i / (n_bands - 1)
        by = int(body_top + t * span)
        hw = int((half_top + (half_bot - half_top) * t))
        tilt = int(5*s) * (1 if i % 2 == 0 else -1)
        # deep groove (dark) just above each band
        pygame.draw.line(surf, WRAP_DD,
                         (cx - hw, by - int(4*s) - tilt),
                         (cx + hw, by - int(4*s) + tilt), max(2, int(2.4*s)))
        # the raised band itself
        pygame.draw.line(surf, WRAP_D,
                         (cx - hw, by - tilt),
                         (cx + hw, by + tilt), max(3, int(4*s)))
        pygame.draw.line(surf, WRAP_T,
                         (cx - hw, by - int(2*s) - tilt),
                         (cx + hw, by - int(2*s) + tilt), max(1, int(1.2*s)))

    # a sliver of exposed charnel flesh peeking between two wraps mid-body
    fl_y = body_top + int(int(span*0.5))
    pygame.draw.polygon(surf, FLESH,
                        [(cx - int(8*s), fl_y - int(3*s)),
                         (cx + int(9*s), fl_y - int(1*s)),
                         (cx + int(7*s), fl_y + int(6*s)),
                         (cx - int(7*s), fl_y + int(4*s))])
    pygame.draw.polygon(surf, FLESH_D,
                        [(cx + int(1*s), fl_y - int(1*s)),
                         (cx + int(9*s), fl_y - int(1*s)),
                         (cx + int(7*s), fl_y + int(6*s)),
                         (cx + int(1*s), fl_y + int(5*s))])

    # --- both arms folded UP as furled bat-wing membranes (ox-blood accent) ---
    # shoulders sit LOW near the head; the membranes sweep UP toward the feet,
    # hugging the body so the pendulum silhouette stays tight.
    sh_y = body_bot - int(4*s)
    furled_wing_arm(surf, cx - half_bot + int(4*s), sh_y, -1, s)
    furled_wing_arm(surf, cx + half_bot - int(4*s), sh_y, +1, s)

    # --- the fanged chibi head at the BOTTOM (eyes read right-way-up) ---
    # head enlarged ~18% over round 1 and dropped slightly lower so the FACE owns
    # more pixels at true 32px — the brief's #1 gate (face FIRST, day AND night).
    hr = int(36*s)
    hc = (cx, head_cy + int(4*s))
    # neck wrap joining body to head
    pygame.draw.polygon(surf, WRAP_D,
                        [(cx - int(13*s), body_bot + int(2*s)),
                         (cx + int(13*s), body_bot + int(2*s)),
                         (cx + int(11*s), hc[1] - int(hr*0.74)),
                         (cx - int(11*s), hc[1] - int(hr*0.74))])
    pygame.draw.polygon(surf, INK,
                        [(cx - int(13*s), body_bot + int(2*s)),
                         (cx + int(13*s), body_bot + int(2*s)),
                         (cx + int(11*s), hc[1] - int(hr*0.74)),
                         (cx - int(11*s), hc[1] - int(hr*0.74))], max(1, int(2*s)))

    # head ball — BRIGHT bone-ivory (its own value, not the dull body flesh) with
    # a heavy ink keyline so it pops off both the maroon wings and the night sky.
    pygame.draw.circle(surf, INK, hc, hr + int(4*s))
    pygame.draw.circle(surf, FACE, hc, hr)
    pygame.draw.circle(surf, FACE_D, (hc[0] + int(9*s), hc[1] + int(9*s)), int(hr*0.74))
    pygame.draw.circle(surf, FACE, hc, int(hr*0.86))
    pygame.draw.circle(surf, FACE_T,
                       (hc[0] - int(13*s), hc[1] - int(13*s)), int(9*s))
    pygame.draw.circle(surf, INK, hc, hr, max(3, int(3*s)))

    # two big hot-amber eyes with HARD dark socket rims so they survive as TWO
    # distinct dots (not one smear) at 1x. Placed in the upper half of the head
    # so the inverted face still reads eyes-over-mouth = a FACE.
    eye_r = int(8*s)
    for ex in (hc[0] - int(15*s), hc[0] + int(15*s)):
        ey = hc[1] - int(8*s)
        amber_glow(surf, ex, ey, int(10*s), intensity=140)
        # hard dark socket rim keeps each eye an isolated dot when downscaled
        pygame.draw.circle(surf, INK, (ex, ey), eye_r + int(2*s))
        pygame.draw.circle(surf, AMBER_D, (ex, ey), eye_r + int(1*s))
        pygame.draw.circle(surf, AMBER, (ex, ey), eye_r)
        pygame.draw.circle(surf, AMBER_BR, (ex - int(1*s), ey - int(2*s)), int(4*s))
        pygame.draw.circle(surf, (255, 250, 230), (ex - int(2*s), ey - int(2*s)), max(1, int(1.6*s)))
        # heavy ridge-brow above each eye (toward the body) for the menace read
        pygame.draw.line(surf, INK, (ex - int(10*s), ey - int(11*s)),
                         (ex + int(9*s), ey - int(8*s)), max(2, int(3*s)))

    # tiny down-turned nose hollow between the eyes
    pygame.draw.polygon(surf, FACE_D,
                        [(hc[0] - int(3*s), hc[1] + int(3*s)),
                         (hc[0] + int(3*s), hc[1] + int(3*s)),
                         (hc[0], hc[1] + int(9*s))])

    # fanged grin LOW on the head ball. At true 32px a row of small teeth reads
    # as a flat band, so this is THREE big triangular fangs over a dark mouth-gap
    # — the grin survives the downscale the way Karakasa's / Citipati's do.
    my = hc[1] + int(17*s)
    mouth_w = int(17*s)
    # the dark mouth-gap behind the fangs (with a faint amber gap-glow inside)
    amber_glow(surf, hc[0], my + int(3*s), int(8*s), intensity=70)
    mouth_box = [(hc[0] - mouth_w, my),
                 (hc[0] + mouth_w, my),
                 (hc[0] + int(mouth_w*0.7), my + int(12*s)),
                 (hc[0] - int(mouth_w*0.7), my + int(12*s))]
    pygame.draw.polygon(surf, INK, mouth_box)
    pygame.draw.polygon(surf, MAROON_D,
                        [(hc[0] - mouth_w + int(2*s), my + int(1*s)),
                         (hc[0] + mouth_w - int(2*s), my + int(1*s)),
                         (hc[0] + int(mouth_w*0.6), my + int(10*s)),
                         (hc[0] - int(mouth_w*0.6), my + int(10*s))])
    # THREE big fangs pointing UP (inverted) — the wide outer pair carry the read
    fang_xs = (hc[0] - int(11*s), hc[0], hc[0] + int(11*s))
    fang_w  = (int(5*s), int(4*s), int(5*s))
    for fx, fw in zip(fang_xs, fang_w):
        fang = [(fx - fw, my + int(11*s)),
                (fx + fw, my + int(11*s)),
                (fx, my - int(2*s))]
        pygame.draw.polygon(surf, FANG, fang)
        pygame.draw.polygon(surf, INK, fang, max(1, int(1.4*s)))
    # tongue reduced to a small amber-pink nub only — sacrificed first at 1x so
    # the fangs + eyes carry the face; just a hint of the inverted gravity gag.
    nub = [(hc[0] - int(3*s), my + int(3*s)),
           (hc[0] + int(3*s), my + int(3*s)),
           (hc[0], my - int(3*s))]
    pygame.draw.polygon(surf, MAROON_T, nub)
    pygame.draw.polygon(surf, INK, nub, max(1, int(1*s)))


# ── the prop -> pillar mirror (charnel-branch / bat-wing-fan cap) ─────────────
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """Wrapped charnel-branch shaft (same hard wrap-banding + hooked claw-marks
    as the creature) with a bat-wings-unfurled scalloped-fan gap-cap. `cap` end
    faces the gap; a hot-amber focal sits at the gap so the eye lands there."""
    shaft_w = int(34*s)
    # the slate branch core
    pygame.draw.rect(surf, INK, (cx - shaft_w//2 - 1, top, shaft_w + 2, bot - top))
    pygame.draw.rect(surf, SLATE, (cx - shaft_w//2, top, shaft_w, bot - top))
    pygame.draw.rect(surf, SLATE_D, (cx + shaft_w//2 - int(10*s), top, int(10*s), bot - top))
    pygame.draw.rect(surf, SLATE_T, (cx - shaft_w//2, top, int(7*s), bot - top))

    # bone-wrap binding the branch — repeating diagonal bands with deep grooves
    # and a hooked claw-mark scored into every other band (tileable on-axis).
    band = top + int(14*s)
    flip = 0
    while band < bot - int(14*s):
        tilt = int(7*s) * (1 if flip % 2 == 0 else -1)
        bw = shaft_w + int(6*s)
        bx = cx - bw // 2
        # the wrap band
        wrap = [(bx, band - tilt),
                (bx + bw, band + tilt),
                (bx + bw, band + tilt + int(13*s)),
                (bx, band - tilt + int(13*s))]
        triad_blob(surf, WRAP, wrap,
                   core_pts=[(cx, band + int(5*s)),
                             (bx + bw, band + tilt + int(2*s)),
                             (bx + bw, band + tilt + int(13*s)),
                             (cx, band + int(13*s))],
                   sheen_pts=[(bx + int(2*s), band - tilt + int(1*s)),
                              (cx, band + int(1*s)),
                              (cx, band + int(4*s)),
                              (bx + int(2*s), band - tilt + int(4*s))],
                   ow=max(1, int(1.6*s)))
        # deep groove above the band
        pygame.draw.line(surf, WRAP_DD,
                         (bx, band - tilt - int(3*s)),
                         (bx + bw, band + tilt - int(3*s)), max(2, int(2.4*s)))
        # hooked claw-marks gouged into every other band
        if flip % 2 == 0:
            for i in (-1, 1):
                gx = cx + i * int(9*s)
                pygame.draw.line(surf, WRAP_DD,
                                 (gx, band + int(2*s)),
                                 (gx + i*int(5*s), band + int(11*s)), max(2, int(2*s)))
        band += int(26*s)
        flip += 1

    # --- the bat-wing-fan gap-cap ---
    cap_y = (bot - int(6*s)) if cap == "bottom" else (top + int(6*s))
    fan_dir = 1 if cap == "bottom" else -1   # the fan opens AWAY from the gap

    # strong hot-amber focal sitting AT the gap edge
    amber_glow(surf, cx, cap_y, int(26*s), intensity=150)

    # bat-wings unfurled into a hard scalloped fan — a row of membrane lobes
    # arcing out symmetrically about the axis. Each lobe is a maroon scallop on
    # slate strut bones; the fan is the unmistakable creature-derived cap.
    n_lobes = 5
    spread = int(78*s)
    reach  = int(46*s)
    base_y = cap_y
    pts_outer = []
    for i in range(n_lobes + 1):
        ang = math.pi * (i / n_lobes)            # 0..pi across the fan
        lx = cx - spread + int(2 * spread * (i / n_lobes))
        ly = base_y + fan_dir * int(reach * math.sin(ang) * 0.55)
        pts_outer.append((lx, ly))
    # solid membrane behind the scallops (maroon mass, triad-lit)
    membrane = [(cx - spread, base_y)] + pts_outer + [(cx + spread, base_y)]
    # build the scalloped outer edge: dip between each lobe tip
    scallop = [(cx - spread, base_y)]
    for i in range(n_lobes):
        lx0 = cx - spread + int(2 * spread * (i / n_lobes))
        lx1 = cx - spread + int(2 * spread * ((i + 1) / n_lobes))
        tipx = (lx0 + lx1) // 2
        tipy = base_y + fan_dir * reach
        scallop.append((tipx, tipy))
        scallop.append((lx1, base_y + fan_dir * int(reach * 0.25)))
    scallop.append((cx + spread, base_y))
    triad_blob(
        surf, MAROON, scallop,
        core_pts=[(cx - int(spread*0.4), base_y + fan_dir*int(6*s)),
                  (cx + int(spread*0.4), base_y + fan_dir*int(6*s)),
                  (cx + int(spread*0.3), base_y + fan_dir*int(reach*0.7)),
                  (cx - int(spread*0.3), base_y + fan_dir*int(reach*0.7))],
        sheen_pts=[(cx - spread + int(6*s), base_y),
                   (cx - int(spread*0.2), base_y),
                   (cx - int(spread*0.25), base_y + fan_dir*int(reach*0.5)),
                   (cx - spread + int(10*s), base_y + fan_dir*int(reach*0.3))],
        ow=max(2, int(2.2*s)),
    )
    # slate strut bones radiating to each scallop tip (the wing fingers)
    for i in range(n_lobes):
        lx0 = cx - spread + int(2 * spread * (i / n_lobes))
        lx1 = cx - spread + int(2 * spread * ((i + 1) / n_lobes))
        tipx = (lx0 + lx1) // 2
        tipy = base_y + fan_dir * reach
        pygame.draw.line(surf, SLATE_D, (cx, base_y), (tipx, tipy), max(2, int(2.6*s)))
        pygame.draw.line(surf, SLATE_T, (cx, base_y), (tipx, tipy), max(1, int(1*s)))
        # tiny claw hook at each fan tip (bat-wing thumb)
        pygame.draw.line(surf, NAIL, (tipx, tipy),
                         (tipx + int(3*s), tipy + fan_dir*int(5*s)), max(2, int(2*s)))

    # central amber focal eye at the very gap edge — where the player looks
    pygame.draw.circle(surf, INK, (cx, base_y), int(9*s))
    pygame.draw.circle(surf, AMBER, (cx, base_y), int(7*s))
    pygame.draw.circle(surf, AMBER_BR, (cx, base_y - int(1*s)), int(3*s))


# ── compose the review sheet ─────────────────────────────────────────────────
SS = 6


def render_creature_box(boxw, boxh, draw_cx, draw_cy, scale):
    big = pygame.Surface((boxw*SS, boxh*SS), pygame.SRCALPHA)
    draw_vetala(big, draw_cx*SS, draw_cy*SS, scale*SS)
    small = pygame.transform.smoothscale(big, (boxw, boxh))
    return grow_outline(small, INK + (255,), 1)


def render_pillar_box(boxw, boxh, top, bot, scale, cap):
    big = pygame.Surface((boxw*SS, boxh*SS), pygame.SRCALPHA)
    draw_pillar(big, (boxw//2)*SS, top*SS, bot*SS, scale*SS, cap=cap)
    small = pygame.transform.smoothscale(big, (boxw, boxh))
    return grow_outline(small, INK + (255,), 1)


def main():
    # widened to 1280 so the palette panel, the night 32px chip, and the
    # face-read aid no longer clip off the right edge (round-1 FIX #1).
    W, H = 1280, 880
    font_big = pygame.font.SysFont("DejaVu Sans", 30, bold=True)
    font = pygame.font.SysFont("DejaVu Sans", 17, bold=True)
    font_sm = pygame.font.SysFont("DejaVu Sans", 12)

    sheet = pygame.Surface((W, H))
    sheet.fill(BG)

    pygame.draw.rect(sheet, PANEL, (0, 0, W, 56))
    sheet.blit(font_big.render("VETALA", True, LABEL), (24, 13))
    sheet.blit(font_sm.render(
        "inverted bat-hung charnel revenant  ·  dusty bone-wrap + DARK ox-blood maroon + hot-amber  ·  round 2  ·  SS=6 epic",
        True, LABEL_DIM), (180, 24))

    # --- (a) BIG HERO sprite (inverted: feet hook top, head hangs bottom) ---
    hero = render_creature_box(300, 470, 150, 235, 1.55)
    sheet.blit(hero, (16, 78))
    sheet.blit(font.render("(a) Hero — inverted bat-hung", True, LABEL), (40, 560))
    sheet.blit(font_sm.render("clawed grip-feet hook the branch at TOP; wrapped body hangs DOWN;", True, LABEL_DIM), (16, 582))
    sheet.blit(font_sm.render("fanged chibi head at BOTTOM (eyes right-way-up); arms furled as bat-wings;", True, LABEL_DIM), (16, 598))
    sheet.blit(font_sm.render("tongue lolls UP — bottom-weighted pendulum, never top-heavy", True, LABEL_DIM), (16, 614))

    # --- (b) the pillar assembled: top seg + GAP + bottom seg, MIRRORED ---
    # top segment caps DOWN into the gap; bottom segment caps UP into the gap.
    gap_h = 132
    seg_h = 250
    px0 = 340
    pcx = 100
    top_seg = render_pillar_box(200, seg_h, 0, seg_h, 1.0, cap="bottom")
    bot_seg = render_pillar_box(200, seg_h, 0, seg_h, 1.0, cap="top")
    sheet.blit(top_seg, (px0, 78))
    sheet.blit(bot_seg, (px0, 78 + seg_h + gap_h))
    # gap label + the bottom-weighted pendulum hint
    gy = 78 + seg_h
    sheet.blit(font_sm.render("← GAP →", True, AMBER_BR), (px0 + 78, gy + gap_h//2 - 8))
    sheet.blit(font.render("(b) Pillar — mirrored, tileable", True, LABEL), (px0 - 4, 78 + 2*seg_h + gap_h + 8))
    sheet.blit(font_sm.render("wrapped charnel-branch + wrap-banding + hooked claw-marks;", True, LABEL_DIM), (px0 - 8, 78 + 2*seg_h + gap_h + 32))
    sheet.blit(font_sm.render("bat-wings-unfurled scalloped fan caps each gap edge, amber focal at gap", True, LABEL_DIM), (px0 - 8, 78 + 2*seg_h + gap_h + 48))

    # --- (c) TRUE 32px gameplay chips on day + night sky ---
    # right column fully inside the widened canvas: panel spans to W-16 with both
    # day + night chips and their 4x zooms laid out so nothing clips (FIX #1).
    panel_x = 600
    pw = W - panel_x - 16
    pygame.draw.rect(sheet, PANEL, (panel_x, 78, pw, 388))
    sheet.blit(font.render("(c) TRUE 32px gameplay chip", True, LABEL), (panel_x + 16, 90))
    sheet.blit(font_sm.render("the inverted face must read as a FACE first — day AND night", True, LABEL_DIM), (panel_x + 16, 114))

    # build a 32px-tall creature chip (figure ~150 units -> scale 32/150)
    def chip_32():
        big = pygame.Surface((64*SS, 64*SS), pygame.SRCALPHA)
        draw_vetala(big, 32*SS, 32*SS, (32.0/150.0)*SS)
        small = pygame.transform.smoothscale(big, (64, 64))
        return grow_outline(small, INK + (255,), 1)

    chip = chip_32()
    # show at 32px native and a 4x zoom so the reviewer can read both
    zoom = pygame.transform.scale(chip, (256, 256))

    # day column
    dx, dyy = panel_x + 24, 144
    pygame.draw.rect(sheet, DAY_SKY, (dx, dyy, 64, 64))
    sheet.blit(chip, (dx, dyy))
    pygame.draw.rect(sheet, INK, (dx, dyy, 64, 64), 1)
    sheet.blit(font_sm.render("32px · day", True, LABEL), (dx, dyy + 70))
    pygame.draw.rect(sheet, DAY_SKY, (dx, dyy + 96, 256, 256))
    sheet.blit(zoom, (dx, dyy + 96))
    pygame.draw.rect(sheet, INK, (dx, dyy + 96, 256, 256), 1)
    sheet.blit(font_sm.render("4× zoom of the 32px day chip", True, LABEL_DIM), (dx, dyy + 356))

    # night column — fully inside the panel (was clipped in round 1)
    nx2 = dx + 296
    pygame.draw.rect(sheet, NIGHT_SKY, (nx2, dyy, 64, 64))
    sheet.blit(chip, (nx2, dyy))
    pygame.draw.rect(sheet, INK, (nx2, dyy, 64, 64), 1)
    sheet.blit(font_sm.render("32px · night", True, LABEL), (nx2, dyy + 70))
    pygame.draw.rect(sheet, NIGHT_SKY, (nx2, dyy + 96, 256, 256))
    sheet.blit(zoom, (nx2, dyy + 96))
    pygame.draw.rect(sheet, INK, (nx2, dyy + 96, 256, 256), 1)
    sheet.blit(font_sm.render("4× zoom · bright face + 2 socketed eyes anchor on dark", True, LABEL_DIM), (nx2, dyy + 356))

    # --- palette swatch row ---
    pygame.draw.rect(sheet, PANEL, (panel_x, 480, pw, 196))
    sheet.blit(font.render("Pinned palette", True, LABEL), (panel_x + 16, 490))
    swatches = [
        (WRAP, "bone-wrap"), (WRAP_D, "wrap-shade"),
        (FACE, "face ivory (1x anchor)"), (FLESH, "charnel flesh"),
        (MAROON, "ox-blood (dark/desat)"), (MAROON_D, "ox-blood shade"),
        (MEMB_RIM, "wing rim (night sep)"), (SLATE, "slate branch"),
        (AMBER, "hot-amber"), (AMBER_BR, "amber (night)"),
        (AMBER_D, "amber socket"), (INK, "ink keyline"),
    ]
    sx, sy = panel_x + 16, 520
    for i, (c, name) in enumerate(swatches):
        col = i % 2
        row = i // 2
        rx = sx + col*322
        ry = sy + row*26
        pygame.draw.rect(sheet, INK, (rx-1, ry-1, 24, 24))
        pygame.draw.rect(sheet, c, (rx, ry, 22, 22))
        sheet.blit(font_sm.render("%s  %d,%d,%d" % (name, *c), True, LABEL), (rx+30, ry+5))

    # --- face-read aid: the head alone, day + night, proving eyes-over-mouth ---
    pygame.draw.rect(sheet, PANEL, (panel_x, 690, pw, 174))
    sheet.blit(font.render("Face-read aid — head alone (eyes-over-mouth)", True, LABEL), (panel_x + 16, 700))
    sheet.blit(font_sm.render("bright ivory ball + 2 socketed amber eyes + 3 big fangs over a dark mouth-gap", True, LABEL_DIM), (panel_x + 16, 724))

    def head_crop():
        # frame the enlarged head; figure head_cy ~= cy+70, so centre the box there
        big = pygame.Surface((96*SS, 96*SS), pygame.SRCALPHA)
        draw_vetala(big, 48*SS, (48 - 74)*SS, 1.0*SS)  # shift body up so head sits in frame
        small = pygame.transform.smoothscale(big, (132, 132))
        return grow_outline(small, INK + (255,), 1)

    hcrop = head_crop()
    hy = 742
    pygame.draw.rect(sheet, DAY_SKY, (panel_x + 24, hy, 132, 116))
    sheet.blit(hcrop, (panel_x + 24, hy - 12))
    pygame.draw.rect(sheet, INK, (panel_x + 24, hy, 132, 116), 1)
    sheet.blit(font_sm.render("day", True, LABEL_DIM), (panel_x + 24, hy + 118))
    nhx = panel_x + 24 + 160
    pygame.draw.rect(sheet, NIGHT_SKY, (nhx, hy, 132, 116))
    sheet.blit(hcrop, (nhx, hy - 12))
    pygame.draw.rect(sheet, INK, (nhx, hy, 132, 116), 1)
    sheet.blit(font_sm.render("night", True, LABEL_DIM), (nhx, hy + 118))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_2.png")
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
