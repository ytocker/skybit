"""
Round-1 concept renderer for HAEDUNG — the fire-eating guardian-LION totem-post
(Jangseung-versions set, concept #1). A carved-WOOD spin-off off the shipped
Jangseung: where Jangseung is a smooth official-face post, Haedung is the
Korean Haetae/Haechi — the lion that EATS FIRE — carved as a squat scaled cedar
column. Headless Pygame; supersample at SS=6 then smoothscale to match the
elevated house grammar (chibi, flat saturated fills, hard 1-2px ink keyline,
dark-core -> flat-fill -> top-left rim-sheen triad, 1px alpha-grown outline).

WHY haedung stays a true creature=prop=pillar mirror: the Haetae is a guardian
totem-beast, so the carved cedar COLUMN itself is the body. Fish-scale courses
are the tileable repeat band (more column = more of the same scaled wood); the
gap-edge cap is a SMALLER mirrored lion-mask whose ember mouth is lit, so the
on-axis top<->bottom mirror is folklore-true rather than forced.

WHY MATTE honey-cedar, not a glazed kiln-wood (anti-Zhenmushou re-spec): this is
carved temple wood, not ceramic — flat triad fills, zero crackle/sheen-glaze.
The three set teals are policed by PLACEMENT: Haedung's jade is a SCALE-BAND +
mane-tip accent ONLY (blue-leaning), never a body fill, so it can never grow
into a second mass against Muljang's prow-foam band or Hyeoljang's eye-ring.
The one warm focal is the EMBER mouth glow — the fire it eats; eye glow stays a
quieter warm amber. Character soul = the fire-EATER gag: a tiny carved
flame-curl licking from ONE mouth corner, sized to survive the 1x read.

WHY a standalone script: review art must never enter the shipped bundle, so it
lives under docs/ and reuses only colour math, not runtime sprite modules.
"""
import os
import math
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
pygame.init()

# ── PINNED PALETTE (locked brief) ─────────────────────────────────────────────
# Honey CEDAR — warm carved temple wood, MATTE (no glaze, no crackle).
WOOD      = (198, 150,  84)   # honey-cedar base
WOOD_D    = (150, 104,  52)   # cedar shade (dark core)
WOOD_T    = (224, 188, 132)   # sun-warmed cedar rim-sheen helper
WOOD_GRV  = (110,  74,  40)   # carved bevel-groove shadow

# JADE — scale-band + mane-tip ACCENT only (blue-leaning). NEVER a body fill.
JADE      = ( 72, 150, 118)
JADE_D    = ( 44, 104,  84)   # deep jade shade
JADE_T    = (120, 188, 156)   # jade rim-sheen

# EMBER — the warm focal: the fire the guardian eats, glowing in the mouth.
EMBER     = (238, 128,  64)
EMBER_D   = (188,  86,  44)   # deep ember shade
EMBER_T   = (252, 196, 120)   # ember hot core / rim
FLAME_TIP = (255, 232, 150)   # cream-yellow hot flame TONGUE-TIP (out-values maw)

# Gold bell is HARDWARE, not a second light source: toned down in value +
# saturation from the brief gold so the EMBER MAW stays the sole warm focal.
# AD r2 ship-gate: the bell's LIT area is dropped a further ~12% (hue held) so
# at hero scale it can never match the maw key and re-fuse into one bright
# lower-face mass — gold catching warm light, not emitting it.
GOLD      = (162, 132,  70)   # gold neck-bell (muted hardware, value-dropped)
GOLD_D    = (116,  92,  44)   # bell shade
GOLD_T    = (188, 162, 104)   # bell rim-sheen (small, no glow halo)

EYEGLOW   = (246, 206, 132)   # warm-amber eye glow (quieter than ember)
EYEGLOW_D = (208, 158,  92)   # eye-glow shade ring
TOOTH     = (240, 230, 206)   # bone-cream fangs

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
    """Flat fill + optional dark-core + top-left rim-sheen + ink keyline.
    Deliberately MATTE: the rim-sheen is a soft tint toward white, not a glossy
    specular hotspot — carved temple wood, never glazed ceramic."""
    if outline:
        pygame.draw.polygon(surf, INK, pts)
    pygame.draw.polygon(surf, color, pts)
    if core_pts:
        pygame.draw.polygon(surf, lerp(color, INK, 0.42), core_pts)
    if sheen_pts:
        pygame.draw.polygon(surf, lerp(color, (255, 255, 255), 0.26), sheen_pts)
    if outline:
        pygame.draw.polygon(surf, INK, pts, ow)


# ── one fish-scale course (the tileable scaled-wood repeat band) ──────────────
def scale_course(surf, cx, y, half_w, s, row_idx, jade=False):
    """A single horizontal course of carved overlapping fish-scales spanning the
    column width. WHY scales are THE repeat unit: the Haetae is dragon-scaled, so
    stacking courses down the shaft is literally 'more of the same carved body'.
    Alternate courses brick-offset like real scale armour. When `jade` is set the
    course is the BLUE-LEANING jade accent BAND — a single course, never the body
    fill — which is how the set's teal stays a placement accent."""
    sw = int(20 * s)                 # scale cell width
    sh = int(16 * s)                 # scale visible height
    base = WOOD if not jade else JADE
    shade = WOOD_D if not jade else JADE_D
    sheen = WOOD_T if not jade else JADE_T
    x = cx - half_w + (sw // 2 if row_idx % 2 else 0)
    while x - sw // 2 < cx + half_w:
        # clamp each scale into the column so the band never bleeds past the edge
        left = max(cx - half_w, x - sw // 2)
        right = min(cx + half_w, x + sw // 2)
        if right - left > int(3 * s):
            cxx = (left + right) // 2
            rr = (right - left) // 2
            # carved scale = a flat rounded fan: ink seat, fill, dark seam, sheen
            pygame.draw.circle(surf, INK, (cxx, y), rr + max(1, int(1.5 * s)),
                               draw_top_left=False, draw_top_right=False)
            pygame.draw.circle(surf, base, (cxx, y), rr,
                               draw_top_left=False, draw_top_right=False)
            pygame.draw.circle(surf, shade, (cxx, y + int(rr * 0.32)),
                               int(rr * 0.62),
                               draw_top_left=False, draw_top_right=False)
            pygame.draw.circle(surf, sheen, (cxx - int(rr * 0.34), y),
                               max(1, int(rr * 0.34)),
                               draw_top_left=False, draw_top_right=False)
        x += sw
    return sh


# ── carved-wood column band (the repeatable shaft unit) ───────────────────────
def carved_shaft(surf, cx, top, bot, half_w, s):
    """One stretch of the totem POST: a honey-cedar column clad in courses of
    carved fish-SCALES, with a single jade accent course per stretch and a couple
    of carved banding seams. This is what tiles — the creature IS this column."""
    w = half_w * 2
    x0 = cx - half_w

    # main cedar mass — flat fill + warm dark core on the right + sun sheen left.
    body = [(x0, top), (x0 + w, top), (x0 + w, bot), (x0, bot)]
    triad_blob(
        surf, WOOD, body,
        core_pts=[(cx + int(half_w*0.22), top), (x0 + w, top),
                  (x0 + w, bot), (cx + int(half_w*0.22), bot)],
        sheen_pts=[(x0, top), (x0 + int(half_w*0.30), top),
                   (x0 + int(half_w*0.30), bot), (x0, bot)],
        ow=max(2, int(2*s)),
    )

    # stacked fish-scale courses tiling the whole stretch. WHY one jade course
    # mid-stretch: it pins the blue-leaning accent BAND into the scale rhythm
    # without ever becoming the body fill — the cross-set teal placement rule.
    course_pitch = int(15 * s)
    jade_at = top + (bot - top) // 2          # one jade band per stretch
    y = top + int(10 * s)
    row = 0
    while y < bot - int(4 * s):
        is_jade = abs(y - jade_at) < course_pitch // 2
        scale_course(surf, cx, y, half_w, s, row, jade=is_jade)
        y += course_pitch
        row += 1

    # a couple of carved horizontal BANDING SEAMS — full-width triad-lit channels
    # that read as stacked carved courses (temple-post joinery, not a smooth bar).
    for frac in (0.0, 1.0):
        sy = int(top + (bot - top) * frac)
        if frac == 1.0:
            sy = bot - int(2 * s)
        pygame.draw.line(surf, WOOD_GRV, (x0 + int(3*s), sy),
                         (x0 + w - int(3*s), sy), max(2, int(3*s)))
        pygame.draw.line(surf, WOOD_T, (x0 + int(3*s), sy - max(1, int(2*s))),
                         (x0 + w - int(3*s), sy - max(1, int(2*s))),
                         max(1, int(1*s)))


# ── a tiny carved flame-curl — THE fire-eater gag, the character's soul ───────
def flame_curl(surf, x, y, s, lit=True):
    """ONE bold flame licking UP out of ONE mouth corner — the fire the Haetae is
    mid-devouring, and the character's SOUL. WHY this rebuild (AD round-1 ruling):
    at 1x the old curl fused into the same-ember maw and died. So now it is built
    as a SEPARATE shape from the maw, three ways at once:
      • a HARD INK-GAP collar is laid down FIRST and oversized, so a dark keyline
        ring always sits between the maw rim and the flame — they read as two
        shapes, never one blob;
      • the lobe is a CHUNKY single comma ~40% taller than before, hooked, and
        lifted clear of the lip so its tip bites UP into the negative space above
        the mouth corner (the silhouette break is what sells 'flame');
      • a 2-VALUE tip — ember body + a cream-yellow hot TONGUE-TIP — so the flame
        out-values the maw and becomes the eye's second stop after the eyes.
    Anchored to ONE corner only (asymmetry = 'caught mid-bite'); warm glow when
    lit so it pops at night."""
    fw = int(18 * s)
    fh = int(36 * s)               # ~40% taller — breaks the mouth's top silhouette
    # lift the whole curl clear of the lip line so it bites into the space ABOVE
    # the corner rather than sitting flush against the ember interior.
    bx, by = x - int(2*s), y - int(7*s)
    if lit:
        glow_r = int(fh * 0.85)
        glow = pygame.Surface((glow_r*4, glow_r*4), pygame.SRCALPHA)
        for r in range(glow_r, 0, -1):
            a = int(135 * (1 - r/glow_r))
            pygame.draw.circle(glow, (*EMBER, a), (glow_r*2, glow_r*2), r)
        surf.blit(glow, (bx - glow_r*2, by - fh - glow_r + int(fh*0.45)),
                  special_flags=pygame.BLEND_ADD)
    # ONE chunky comma-lobe flame: a fat base swelling up to a single hooked tip.
    flame = [
        (bx - int(fw*0.30), by),
        (bx - int(fw*0.66), by - int(fh*0.34)),
        (bx - int(fw*0.40), by - int(fh*0.62)),
        (bx + int(fw*0.06), by - int(fh*0.78)),
        (bx + int(fw*0.62), by - int(fh*1.00)),   # the lifted hooked TIP
        (bx + int(fw*0.30), by - int(fh*0.66)),
        (bx + int(fw*0.74), by - int(fh*0.40)),
        (bx + int(fw*0.70), by - int(fh*0.06)),
    ]
    # HARD INK-GAP collar drawn FIRST and oversized — guarantees a dark keyline
    # ring between maw rim and flame at every scale, so the two never fuse.
    pygame.draw.polygon(surf, INK, [
        (bx - int(fw*0.46), by + int(fh*0.06)),
        (bx - int(fw*0.84), by - int(fh*0.34)),
        (bx - int(fw*0.56), by - int(fh*0.66)),
        (bx + int(fw*0.04), by - int(fh*0.86)),
        (bx + int(fw*0.78), by - int(fh*1.10)),
        (bx + int(fw*0.40), by - int(fh*0.64)),
        (bx + int(fw*0.92), by - int(fh*0.40)),
        (bx + int(fw*0.88), by + int(fh*0.02)),
    ])
    pygame.draw.polygon(surf, EMBER, flame)
    # deep-ember base shade (anchors the lobe to dark before the hot values)
    pygame.draw.polygon(surf, EMBER_D, [
        (bx - int(fw*0.30), by),
        (bx - int(fw*0.50), by - int(fh*0.26)),
        (bx - int(fw*0.10), by - int(fh*0.40)),
        (bx + int(fw*0.34), by - int(fh*0.30)),
        (bx + int(fw*0.55), by - int(fh*0.06)),
    ])
    pygame.draw.polygon(surf, INK, flame, max(2, int(1.8*s)))
    # 2-VALUE hot TIP: ember-core mid, then a cream-yellow tongue at the very tip,
    # so the flame out-values the maw interior and reads as the brightest licking
    # point — the eye's second stop after the eyes.
    core = [
        (bx - int(fw*0.04), by - int(fh*0.20)),
        (bx - int(fw*0.18), by - int(fh*0.50)),
        (bx + int(fw*0.18), by - int(fh*0.70)),
        (bx + int(fw*0.50), by - int(fh*0.88)),
        (bx + int(fw*0.26), by - int(fh*0.58)),
        (bx + int(fw*0.40), by - int(fh*0.34)),
    ]
    pygame.draw.polygon(surf, EMBER_T, core)
    tip = [
        (bx + int(fw*0.04), by - int(fh*0.58)),
        (bx + int(fw*0.50), by - int(fh*0.90)),
        (bx + int(fw*0.30), by - int(fh*0.62)),
    ]
    pygame.draw.polygon(surf, FLAME_TIP, tip)


# ── the lion-mask: the carved guardian-lion face ──────────────────────────────
def lion_mask(surf, cx, cy, s, lit=False, hero=True):
    """The carved guardian-LION mask: round bug-EYES (single carved ring each),
    ONE stubby centre brow-HORN, a fat snout, a fanged maw with the EMBER glow
    inside, a sparse RING of ~6 hard curl-lobes for the mane (jade-tipped), and
    the fire-eater flame-curl licking from ONE corner. `lit` lights the maw +
    flame for the gap-edge cap. `hero` draws the full mane ring + bell; the cap
    uses a tighter mane so the SMALLER mirrored mask doesn't overweight the gap.
    Big-and-few features = one clean face read at 1x. No limbs — the mask IS the
    creature, the column IS its body."""

    # mane RING first (behind the face). WHY a sparse ring of ~6 hard curl-lobes:
    # the brief caps the mane so it never becomes a fuzzy halo — six chunky
    # comma-curls survive 1x, and each lobe gets a JADE tip (the accent placed,
    # not massed). The cap uses fewer/tighter lobes to stay visually smaller.
    # Exactly 6 BOLD lobes with a clear gap between each — the AD round-1 note:
    # cull from a packed "noise ring" to six distinct silhouette bumps. Chunkier
    # radius + a tighter arc spread (so each lobe stands apart, not bead-packed).
    n_lobes = 6
    ring_r = int(56 * s) if hero else int(48 * s)
    lobe_r = int(23 * s) if hero else int(18 * s)
    for i in range(n_lobes):
        # spread the six over a top-biased arc with real spacing between lobes
        ang = -math.pi/2 + (i / (n_lobes - 1) - 0.5) * math.radians(206)
        lx = cx + int(math.cos(ang) * ring_r)
        ly = cy + int(math.sin(ang) * ring_r) - int(6 * s)
        # hard comma-curl: ink seat, cedar lobe, dark core, JADE tip fleck, sheen
        pygame.draw.circle(surf, INK, (lx, ly), lobe_r + max(1, int(2*s)))
        pygame.draw.circle(surf, WOOD, (lx, ly), lobe_r)
        pygame.draw.circle(surf, WOOD_D, (lx + int(lobe_r*0.3), ly + int(lobe_r*0.3)),
                           int(lobe_r*0.58))
        pygame.draw.circle(surf, INK, (lx, ly), lobe_r, max(1, int(1.5*s)))
        # JADE mane-TIP fleck — the accent placed on the outer edge of each curl
        tx = cx + int(math.cos(ang) * (ring_r + lobe_r*0.55))
        ty = cy + int(math.sin(ang) * (ring_r + lobe_r*0.55)) - int(6*s)
        pygame.draw.circle(surf, INK, (tx, ty), max(2, int(lobe_r*0.42)) + max(1, int(1*s)))
        pygame.draw.circle(surf, JADE, (tx, ty), max(2, int(lobe_r*0.42)))
        pygame.draw.circle(surf, JADE_T, (tx - int(lobe_r*0.16), ty - int(lobe_r*0.16)),
                           max(1, int(lobe_r*0.18)))

    # face block — a broad rounded cedar lion-mask
    fw, fh = int(96*s), int(96*s)
    fx0, fy0 = cx - fw // 2, cy - fh // 2
    face = [(fx0 + int(14*s), fy0 + int(4*s)),
            (fx0 + fw - int(14*s), fy0 + int(4*s)),
            (fx0 + fw - int(2*s), fy0 + int(22*s)),
            (fx0 + fw, fy0 + fh - int(26*s)),
            (fx0 + fw - int(16*s), fy0 + fh - int(4*s)),
            (cx, fy0 + fh),
            (fx0 + int(16*s), fy0 + fh - int(4*s)),
            (fx0, fy0 + fh - int(26*s)),
            (fx0 + int(2*s), fy0 + int(22*s))]
    triad_blob(
        surf, WOOD, face,
        core_pts=[(cx + int(6*s), fy0 + int(8*s)), (fx0 + fw - int(2*s), fy0 + int(22*s)),
                  (fx0 + fw, fy0 + fh - int(26*s)),
                  (fx0 + fw - int(16*s), fy0 + fh - int(4*s)), (cx + int(6*s), fy0 + fh)],
        sheen_pts=[(fx0 + int(10*s), fy0 + int(8*s)), (cx - int(4*s), fy0 + int(8*s)),
                   (cx - int(4*s), fy0 + fh - int(20*s)),
                   (fx0 + int(8*s), fy0 + fh - int(22*s))],
        ow=max(2, int(2*s)),
    )

    # ONE stubby centre brow-HORN (the Haetae unicorn-horn tell; single, no pair).
    # A short fat carved nub rising from the brow centre, cedar with a sheen.
    # Carved nub IN THE ROUND, not a flat plug: full triad (dark-core on the
    # right → cedar flat-fill → top-left rim-sheen) plus a stronger taper so the
    # silhouette narrows toward a rounded tip.
    horn_base_y = fy0 + int(8*s)
    horn = [(cx - int(10*s), horn_base_y + int(4*s)),
            (cx + int(10*s), horn_base_y + int(4*s)),
            (cx + int(6*s), horn_base_y - int(13*s)),
            (cx + int(3*s), horn_base_y - int(22*s)),
            (cx - int(3*s), horn_base_y - int(22*s)),
            (cx - int(6*s), horn_base_y - int(13*s))]
    triad_blob(surf, WOOD, horn,
               core_pts=[(cx + int(1*s), horn_base_y + int(3*s)),
                         (cx + int(10*s), horn_base_y + int(4*s)),
                         (cx + int(6*s), horn_base_y - int(13*s)),
                         (cx + int(2*s), horn_base_y - int(21*s)),
                         (cx + int(1*s), horn_base_y - int(20*s))],
               sheen_pts=[(cx - int(8*s), horn_base_y + int(2*s)),
                          (cx - int(2*s), horn_base_y + int(2*s)),
                          (cx - int(2*s), horn_base_y - int(19*s)),
                          (cx - int(5*s), horn_base_y - int(12*s))],
               ow=max(1, int(1.5*s)))
    # carved ring groove around the horn base (the single-ring carved language)
    pygame.draw.arc(surf, WOOD_GRV,
                    (cx - int(11*s), horn_base_y - int(2*s), int(22*s), int(12*s)),
                    math.pi, 2*math.pi, max(1, int(2*s)))

    # heavy carved BROW ridge — one bold furrow framing the eyes (fierce-cute)
    brow_y = fy0 + int(30*s)
    brow = [(fx0 + int(12*s), brow_y), (cx - int(4*s), brow_y - int(7*s)),
            (cx + int(4*s), brow_y - int(7*s)), (fx0 + fw - int(12*s), brow_y),
            (fx0 + fw - int(12*s), brow_y + int(8*s)),
            (cx, brow_y + int(2*s)),
            (fx0 + int(12*s), brow_y + int(8*s))]
    triad_blob(surf, WOOD_D, brow,
               sheen_pts=[(fx0 + int(14*s), brow_y - int(2*s)),
                          (cx - int(8*s), brow_y - int(6*s)),
                          (cx - int(8*s), brow_y + int(1*s)),
                          (fx0 + int(14*s), brow_y + int(3*s))],
               ow=max(1, int(1.5*s)))

    # round bug-EYES — simple domes with a SINGLE carved ring each (anti-goggle).
    # warm-amber glow (quieter than the ember maw so the maw stays the focal).
    eye_dx = int(23*s)
    eye_y = fy0 + int(48*s)
    er = int(16*s)
    glow_a = 120 if lit else 80
    glow_r = int(er * (1.9 if lit else 1.5))
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
        # ONE carved socket ring (single, not concentric goggles)
        pygame.draw.circle(surf, INK, (ex, eye_y), er + max(1, int(2*s)))
        pygame.draw.circle(surf, WOOD_D, (ex, eye_y), er)
        pygame.draw.circle(surf, INK, (ex, eye_y), er, max(1, int(2*s)))
        # the warm-amber glowing eyeball
        eb = int(er * (0.72 if lit else 0.66))
        pygame.draw.circle(surf, EYEGLOW_D, (ex, eye_y), eb + max(1, int(1*s)))
        pygame.draw.circle(surf, EYEGLOW, (ex, eye_y), eb)
        # ink pupil + tiny hot highlight
        pygame.draw.circle(surf, INK, (ex + int(1*s), eye_y + int(1*s)),
                           int(eb*0.46))
        # catchlight knocked off pure white toward warm cream so the EMBER MAW
        # (+ flame cream-tip) remains the single brightest point in the face.
        pygame.draw.circle(surf, (242, 226, 196),
                           (ex - int(eb*0.32), eye_y - int(eb*0.32)),
                           max(1, int(eb*0.20)))

    # fat carved SNOUT — one rounded muzzle mass dead-centre (the lion anchor)
    ny = fy0 + int(66*s)
    nr = int(15*s)
    pygame.draw.circle(surf, INK, (cx, ny), nr + max(1, int(2*s)))
    pygame.draw.circle(surf, WOOD, (cx, ny), nr)
    pygame.draw.circle(surf, WOOD_D, (cx + int(nr*0.3), ny + int(nr*0.35)),
                       int(nr*0.6))
    pygame.draw.circle(surf, WOOD_T, (cx - int(nr*0.35), ny - int(nr*0.4)),
                       int(nr*0.40))
    pygame.draw.circle(surf, INK, (cx, ny), nr, max(1, int(2*s)))
    # broad flat nose pad + nostril dots
    pygame.draw.line(surf, INK, (cx - int(nr*0.5), ny - int(nr*0.15)),
                     (cx + int(nr*0.5), ny - int(nr*0.15)), max(1, int(2*s)))
    for sgn in (-1, 1):
        pygame.draw.circle(surf, INK, (cx + sgn*int(nr*0.4), ny + int(nr*0.42)),
                           max(1, int(2.5*s)))

    # fanged MAW — a wide mouth with the EMBER fire-glow lit from inside (focal)
    my = fy0 + int(86*s)
    mw = int(32*s)
    mh = int(18*s) if lit else int(15*s)
    if lit or hero:
        # The maw always glows a little (it's eating fire), brighter when lit —
        # but the glow radius + alpha are pulled in (AD r2): the old wide/strong
        # additive halo lifted the chin and bell to maw key and smeared the warm
        # focal down onto the chest. A tighter, dimmer glow keeps the warm pool
        # contained to the cavity so the dark chin band below can read.
        gr = int(mw * (1.05 if lit else 0.85))
        mglow = pygame.Surface((gr*4, gr*4), pygame.SRCALPHA)
        for r in range(gr, 0, -1):
            a = int((100 if lit else 62) * (1 - r/gr))
            pygame.draw.circle(mglow, (*EMBER, a), (gr*2, gr*2), r)
        # Vertically SQUASH the halo so the warm pool spreads across the maw but
        # its downward falloff dies at the dark chin band instead of washing over
        # it onto the bell + top scale courses — the gap under the chin must read
        # dark at hero scale. Centre it inside the cavity, above the lower lip.
        mglow = pygame.transform.smoothscale(mglow, (gr*4, int(gr*4*0.62)))
        gh = mglow.get_height()
        # Alpha-blend (NOT additive): BLEND_ADD ignored the per-pixel alpha and
        # summed full EMBER onto the already-bright cedar, clamping the maw +
        # surrounding snout to near-white and fusing with the bell into one bright
        # lower-face mass (the r2/r3 ship-gate). A normal alpha blit keeps the glow
        # a contained warm TINT over cedar, so the cavity never out-values the
        # eye-rings and the dark chin band below reads.
        surf.blit(mglow, (cx - gr*2, my - int(mh*0.1) - gh//2))
    mouth = [(cx - mw, my - int(3*s)), (cx + mw, my - int(3*s)),
             (cx + int(mw*0.7), my + mh), (cx - int(mw*0.7), my + mh)]
    pygame.draw.polygon(surf, INK, mouth)
    # Ember-lit interior, value-DROPPED (AD r2 ship-gate): at hero scale the old
    # near-cream EMBER_T core blew the maw out and fused it with the gold bell
    # into one bright lower-face mass. So the maw now glows but never blows: the
    # interior reads EMBER_D base -> EMBER mid as its TOP fill (the spec ember
    # mid is the brightest the cavity gets), and EMBER_T is demoted from a broad
    # core to ONLY a thin top rim-LICK just inside the upper lip. The brightest
    # cream value (FLAME_TIP) is reserved for the flame-curl tip alone, so the
    # read order stays EYES > flame-curl + ember maw > everything else.
    pygame.draw.polygon(surf, EMBER_D,
                        [(cx - mw + int(3*s), my - int(1*s)),
                         (cx + mw - int(3*s), my - int(1*s)),
                         (cx + int(mw*0.6), my + mh - int(2*s)),
                         (cx - int(mw*0.6), my + mh - int(2*s))])
    pygame.draw.polygon(surf, EMBER,
                        [(cx - int(mw*0.62), my + int(1*s)),
                         (cx + int(mw*0.62), my + int(1*s)),
                         (cx + int(mw*0.40), my + mh - int(3*s)),
                         (cx - int(mw*0.40), my + mh - int(3*s))])
    # thin hot rim-lick hugging the upper lip ONLY — a glint, not a filled core,
    # so the cavity never matches the flame tip or the bell in value.
    pygame.draw.polygon(surf, EMBER_T,
                        [(cx - int(mw*0.30), my + int(2*s)),
                         (cx + int(mw*0.30), my + int(2*s)),
                         (cx + int(mw*0.24), my + int(5*s)),
                         (cx - int(mw*0.24), my + int(5*s))])
    # cedar lip lines bracketing the fang-row into a grin (carved, not painted)
    lip_w = max(2, int(3*s))
    pygame.draw.line(surf, WOOD_D, (cx - mw, my - int(3*s)),
                     (cx + mw, my - int(3*s)), lip_w)
    pygame.draw.line(surf, WOOD_T, (cx - mw, my - int(4*s)),
                     (cx, my - int(4*s)), max(1, int(1*s)))
    pygame.draw.line(surf, WOOD_D, (cx - int(mw*0.7), my + mh),
                     (cx + int(mw*0.7), my + mh), lip_w)
    # BIG snaggle fangs — top row down, two bottom up, few & chunky
    for fx in (-int(mw*0.62), -int(mw*0.16), int(mw*0.34)):
        tri = [(cx + fx, my - int(2*s)),
               (cx + fx + int(7*s), my - int(2*s)),
               (cx + fx + int(3*s), my + int(8*s))]
        pygame.draw.polygon(surf, TOOTH, tri)
        pygame.draw.polygon(surf, INK, tri, max(1, int(1*s)))
    for fx in (-int(mw*0.42), int(mw*0.18)):
        tri = [(cx + fx, my + mh - int(1*s)),
               (cx + fx + int(7*s), my + mh - int(1*s)),
               (cx + fx + int(3*s), my + mh - int(9*s))]
        pygame.draw.polygon(surf, TOOTH, tri)
        pygame.draw.polygon(surf, INK, tri, max(1, int(1*s)))

    # dark CHIN BAND beneath the maw (AD r2 ship-gate): a carved jaw shelf in
    # ink + deep cedar shade that re-couples the lower lip to the face mass and
    # de-couples the lit maw from the gold bell hung below. Without this the lit
    # cavity and the warm-metal bell fused into one bright lower-face block at
    # hero scale; the band is the dark gap that makes them two shapes again.
    # band sits between the lower lip and the face's chin point so it stays
    # WITHIN the face silhouette (the maw is near the face bottom); it is the
    # carved shadow of the jaw, not a shape floating off below the head.
    chin_top = my + mh
    chin_bot = min(chin_top + int(10*s), fy0 + fh - int(1*s))
    chin = [(cx - int(mw*0.78), chin_top - int(1*s)),
            (cx + int(mw*0.78), chin_top - int(1*s)),
            (cx + int(mw*0.52), chin_bot),
            (cx - int(mw*0.52), chin_bot)]
    pygame.draw.polygon(surf, INK, chin)
    pygame.draw.polygon(surf, WOOD_GRV,
                        [(cx - int(mw*0.66), chin_top + int(1*s)),
                         (cx + int(mw*0.66), chin_top + int(1*s)),
                         (cx + int(mw*0.46), chin_bot - int(2*s)),
                         (cx - int(mw*0.46), chin_bot - int(2*s))])
    # a single sun-side sheen sliver so the band reads as carved cedar in shadow,
    # not a flat black bar — matte triad even in the dark gap.
    pygame.draw.line(surf, WOOD_D,
                     (cx - int(mw*0.58), chin_top + int(2*s)),
                     (cx - int(mw*0.08), chin_top + int(2*s)), max(1, int(2*s)))

    # THE fire-eater flame-curl — licking up from ONE (left) mouth corner.
    flame_curl(surf, cx - mw + int(3*s), my - int(2*s), s, lit=(lit or hero))


# ── gold neck-bell — hung below the mask on the column (a Haetae temple tell) ──
def neck_bell(surf, cx, y, s):
    """A small gold temple-bell on a strap, hung where the mask meets the column.
    WHY gold + small: it's a single warm-metal accent that reads as 'guardian
    beast' regalia without competing with the ember focal; kept tiny so it stays
    a detail, not a second mass."""
    # strap
    pygame.draw.line(surf, WOOD_D, (cx, y - int(10*s)), (cx, y), max(2, int(3*s)))
    br = int(9*s)   # kept small — a detail, not a second mass under the maw
    # bell body — a rounded trapezoid bell
    bell = [(cx - int(br*0.5), y),
            (cx + int(br*0.5), y),
            (cx + br, y + int(br*1.3)),
            (cx - br, y + int(br*1.3))]
    pygame.draw.polygon(surf, INK, bell)
    pygame.draw.polygon(surf, GOLD, bell)
    pygame.draw.polygon(surf, GOLD_D,
                        [(cx + int(br*0.1), y + int(br*0.2)),
                         (cx + int(br*0.5), y),
                         (cx + br, y + int(br*1.3)),
                         (cx + int(br*0.2), y + int(br*1.3))])
    # narrow left-edge rim-sheen only — a carved hardware highlight, NOT a lit
    # face, so the bell never competes with the ember maw for the warm focal.
    pygame.draw.polygon(surf, GOLD_T,
                        [(cx - int(br*0.42), y + int(br*0.20)),
                         (cx - int(br*0.20), y + int(br*0.20)),
                         (cx - int(br*0.52), y + int(br*0.92)),
                         (cx - int(br*0.74), y + int(br*0.92))])
    pygame.draw.polygon(surf, INK, bell, max(1, int(1.5*s)))
    # bell mouth rim + clapper dot
    pygame.draw.line(surf, GOLD_D, (cx - br, y + int(br*1.3)),
                     (cx + br, y + int(br*1.3)), max(2, int(2.5*s)))
    pygame.draw.circle(surf, GOLD_D, (cx, y + int(br*1.42)), max(2, int(3*s)))
    pygame.draw.circle(surf, INK, (cx, y + int(br*1.42)), max(2, int(3*s)), max(1, int(1*s)))


# ── the full hero creature: lion-mask-topped scaled cedar post ────────────────
def draw_haedung(surf, cx, cy, s):
    """The whole guardian-lion: the carved lion-mask crowning a TALL scaled cedar
    POST (the body = the pillar shaft). The column is kept visibly tall so the
    wide mask + mane do not overweight the top. No limbs. `s` is a unit scale
    around a ~250-unit figure."""
    half_w = int(40*s)
    # WHY a long shaft below the mask: the wide mask/mane is heavy, so the column
    # runs well down to keep the silhouette bottom-rooted, not top-heavy.
    post_top = cy - int(36*s)
    post_bot = cy + int(168*s)
    carved_shaft(surf, cx, post_top, post_bot, half_w, s)
    # wider plinth foot grounds the post
    foot = [(cx - half_w - int(8*s), post_bot - int(4*s)),
            (cx + half_w + int(8*s), post_bot - int(4*s)),
            (cx + half_w + int(4*s), post_bot + int(14*s)),
            (cx - half_w - int(4*s), post_bot + int(14*s))]
    triad_blob(surf, WOOD_D, foot,
               sheen_pts=[(cx - half_w - int(6*s), post_bot - int(2*s)),
                          (cx - int(4*s), post_bot - int(2*s)),
                          (cx - int(4*s), post_bot + int(10*s)),
                          (cx - half_w - int(4*s), post_bot + int(10*s))],
               ow=max(2, int(2*s)))
    # gold neck-bell at the mask/column join
    neck_bell(surf, cx, post_top + int(6*s), s)
    # the carved lion-mask crowning the post
    lion_mask(surf, cx, cy - int(92*s), s, lit=False, hero=True)


# ── the pillar: same carved post, mirrored, with a SMALLER lion-mask gap-cap ──
def draw_pillar_segment(surf, cx, top, bot, half_w, s, cap="bottom"):
    """A shaft stretch of the totem POST that meets the gap with a SMALLER
    mirrored lion-MASK cap (ember maw + flame LIT at the gap). The shaft is the
    same scaled cedar column as the creature body, so creature == pillar. `cap`
    end faces the gap. WHY the cap mask is smaller: the brief wants the wide mask
    NOT to overweight the gap, so the cap mask is drawn at ~0.8x and the shaft
    stays visibly tall."""
    cap_scale = 0.80
    face_room = int(108*s*cap_scale) + int(20*s)
    if cap == "bottom":
        shaft_top, shaft_bot = top, bot - face_room
        face_cy = bot - face_room + int(54*s*cap_scale)
        face_dir = 1
    else:
        shaft_top, shaft_bot = top + face_room, bot
        face_cy = top + face_room - int(54*s*cap_scale)
        face_dir = -1
    carved_shaft(surf, cx, shaft_top, shaft_bot, half_w, s)

    # the SMALLER lion-mask cap, drawn into a scratch surface so it can be FLIPPED
    # for the top cap (proving the true top<->bottom mirror).
    fsz = int(170*s)
    fbuf = pygame.Surface((fsz, fsz), pygame.SRCALPHA)
    lion_mask(fbuf, fsz//2, fsz//2, s*cap_scale, lit=True, hero=False)
    if face_dir < 0:
        fbuf = pygame.transform.flip(fbuf, False, True)
    surf.blit(fbuf, (cx - fsz//2, int(face_cy) - fsz//2))


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
    sheet.blit(font_big.render("HAEDUNG", True, LABEL), (22, 12))
    sheet.blit(font_sm.render(
        "fire-eating guardian-lion totem-post  ·  matte honey-cedar + jade scale-band + ember maw + muted gold bell  ·  round 3  ·  creature IS the pillar",
        True, LABEL_DIM), (200, 26))

    # (a) BIG hero sprite ------------------------------------------------------
    hb_w, hb_h = 300, 470
    big = pygame.Surface((hb_w*SS, hb_h*SS), pygame.SRCALPHA)
    draw_haedung(big, hb_w*SS//2, int(hb_h*SS*0.44), 1.30*SS)
    hero = pygame.transform.smoothscale(big, (hb_w, hb_h))
    hero = grow_outline(hero, INK + (255,), 1)
    sheet.blit(hero, (10, 72))
    sheet.blit(font.render("(a) Hero — lion-mask on scaled cedar post", True, LABEL), (16, 548))
    sheet.blit(font_sm.render("bug-eyes (single ring) + 1 brow-horn + ember maw; fish-scale", True, LABEL_DIM), (16, 572))
    sheet.blit(font_sm.render("courses tile the body; jade scale-band + mane-tips; gold bell; flame-curl", True, LABEL_DIM), (16, 588))

    # (b) pillar assembled — top segment + gap + bottom segment, MIRRORED ------
    pcx = 460
    seg_half = int(34)
    seg_h = 250
    seg_top_y = 72
    gap_px = 96
    # top segment (cap faces DOWN toward the gap = flipped mirrored mask)
    topbuf = pygame.Surface((170*SS, seg_h*SS), pygame.SRCALPHA)
    draw_pillar_segment(topbuf, 85*SS, 4*SS, (seg_h-4)*SS, seg_half*SS, 1.0*SS, cap="top")
    topimg = pygame.transform.smoothscale(topbuf, (170, seg_h))
    topimg = grow_outline(topimg, INK + (255,), 1)
    sheet.blit(topimg, (pcx - 85, seg_top_y))
    # bottom segment (cap faces UP toward the gap = upright mirrored mask)
    botbuf = pygame.Surface((170*SS, seg_h*SS), pygame.SRCALPHA)
    draw_pillar_segment(botbuf, 85*SS, 4*SS, (seg_h-4)*SS, seg_half*SS, 1.0*SS, cap="bottom")
    botimg = pygame.transform.smoothscale(botbuf, (170, seg_h))
    botimg = grow_outline(botimg, INK + (255,), 1)
    sheet.blit(botimg, (pcx - 85, seg_top_y + seg_h + gap_px))

    # gap guide lines
    gap_y0, gap_y1 = seg_top_y + seg_h, seg_top_y + seg_h + gap_px
    for gy in (gap_y0, gap_y1):
        pygame.draw.line(sheet, (150, 154, 160), (pcx - 92, gy), (pcx + 92, gy), 1)
    sheet.blit(font_sm.render("← gap →", True, LABEL_DIM), (pcx - 24, (gap_y0+gap_y1)//2 - 7))
    by = seg_top_y + 2*seg_h + gap_px + 10
    sheet.blit(font.render("(b) Pillar — MIRRORED", True, LABEL), (pcx - 92, by))
    sheet.blit(font_sm.render("tileable scaled shaft + jade band; SMALLER", True, LABEL_DIM), (pcx - 92, by + 24))
    sheet.blit(font_sm.render("mirrored mask cap, maw/flame lit at gap", True, LABEL_DIM), (pcx - 92, by + 40))

    # (c) TRUE 32px gameplay-scale chips — day sky + night sky -----------------
    panel_x = 660
    pw = W - panel_x - 14
    pygame.draw.rect(sheet, PANEL, (panel_x, 72, pw, 372))
    sheet.blit(font.render("(c) True 32px gameplay chip", True, LABEL), (panel_x + 14, 82))
    sheet.blit(font_sm.render("flame-curl (ink-gapped, cream tip) bites above the maw corner", True, LABEL_DIM), (panel_x + 14, 104))

    # render at a true ~32px FACE read — the gameplay collision shows the
    # mask-topped cap end, so the chip frames the MASK (not the long shaft).
    def chip32():
        cs = 44  # chip canvas (px) — mask + a sliver of post under it
        buf = pygame.Surface((cs*SS, cs*SS), pygame.SRCALPHA)
        draw_haedung(buf, cs*SS//2, int(cs*SS*1.10), (32/96.0)*SS)
        img = pygame.transform.smoothscale(buf, (cs, cs))
        return grow_outline(img, INK + (255,), 1)

    chip = chip32()
    cs = chip.get_width()
    chip4 = pygame.transform.scale(chip, (cs*4, cs*4))  # zoom to inspect read

    def chip_row(sky_top, sky_bot, sy, lbl, lbl_col):
        sw, sh = 130, 132
        sx = panel_x + 22
        sky(sheet, (sx, sy, sw, sh), sky_top, sky_bot)
        pygame.draw.rect(sheet, INK, (sx, sy, sw, sh), 1)
        sheet.blit(chip, (sx + sw//2 - cs//2, sy + sh//2 - cs//2))
        sheet.blit(font_sm.render(lbl, True, lbl_col), (sx + 4, sy + sh - 16))
        zx = sx + sw + 18
        zw = cs*4
        if zx + zw > panel_x + pw - 10:
            zw = panel_x + pw - 10 - zx
            chip_z = pygame.transform.scale(chip, (cs*4, cs*4)).subsurface((0, 0, zw, min(cs*4, sh+24)))
            sheet.blit(chip_z, (zx, sy))
        else:
            sheet.blit(chip4, (zx, sy - 6))
        return sx, zx

    cy0 = 132
    chip_row(DAY_SKY_T, DAY_SKY_B, cy0, "day sky", INK)
    sheet.blit(font_sm.render("4× zoom →", True, LABEL_DIM), (panel_x + 22 + 130 + 18, cy0 - 18))
    cy1 = cy0 + 168
    chip_row(NIGHT_T, NIGHT_B, cy1, "night sky", LABEL)
    sheet.blit(font_sm.render("ember maw stays the warm focal at night",
                              True, LABEL_DIM), (panel_x + 22, cy1 + 138))

    # palette swatch row -------------------------------------------------------
    pal_y = 458
    pygame.draw.rect(sheet, PANEL, (panel_x, pal_y, pw, 196))
    sheet.blit(font.render("Pinned palette", True, LABEL), (panel_x + 14, pal_y + 10))
    swatches = [
        (WOOD, "honey-cedar"), (WOOD_D, "cedar shade"),
        (WOOD_T, "cedar sheen"), (WOOD_GRV, "bevel groove"),
        (JADE, "jade band"), (JADE_D, "deep jade"),
        (EMBER, "ember maw"), (FLAME_TIP, "flame tip"),
        (GOLD, "gold bell (muted)"), (EYEGLOW, "eye-glow amber"),
        (TOOTH, "fang bone"), (INK, "ink keyline"),
    ]
    sx, sy = panel_x + 14, pal_y + 40
    for i, (c, name) in enumerate(swatches):
        col = i % 2
        row = i // 2
        rx = sx + col*150
        ry = sy + row*26
        pygame.draw.rect(sheet, INK, (rx-1, ry-1, 22, 22))
        pygame.draw.rect(sheet, c, (rx, ry, 20, 20))
        sheet.blit(font_sm.render(name, True, LABEL), (rx+27, ry+4))

    # construction note panel — full-width strip across the bottom ------------
    note_y = 668
    pygame.draw.rect(sheet, PANEL, (10, note_y, W - 20, 222))
    sheet.blit(font.render("Construction notes", True, LABEL), (26, note_y + 10))
    notes_l = [
        "• MATTE honey-cedar — flat triad, NO glaze/crackle/kiln",
        "  sheen (anti-Zhenmushou re-spec).",
        "• Jade is a single SCALE-BAND course + mane-TIP flecks —",
        "  blue-leaning ACCENT, never a body fill (cross-set teal rule).",
        "• Ember MAW glow is the SOLE warm focal; interior value-DROPPED",
        "  to ember-mid + a thin rim-lick so it glows, not blows (r3).",
        "• Dark CHIN BAND + value-dropped gold bell DE-COUPLE the lit maw",
        "  from the bell — two shapes, not one bright lower-face mass (r3).",
    ]
    notes_r = [
        "• Eyes = round bug-eyes, SINGLE carved ring each (anti-goggle);",
        "  ONE stubby brow-horn now triad-shaded + tapered (r2).",
        "• Mane culled to 6 BOLD spaced curl-lobes, jade-tipped (r2).",
        "• Fire-EATER gag (r2): chunky comma-lobe lifted clear of the",
        "  lip with a HARD INK GAP + cream tip — reads as flame at 1x.",
        "• Creature IS the pillar: fish-scale courses tile the body;",
    ]
    for i, line in enumerate(notes_l):
        sheet.blit(font_sm.render(line, True, LABEL_DIM), (26, note_y + 40 + i*19))
    for i, line in enumerate(notes_r):
        sheet.blit(font_sm.render(line, True, LABEL_DIM), (540, note_y + 40 + i*19))
    sheet.blit(font_sm.render("  cap = SMALLER mirrored lion-mask so the wide mask never overweights the gap.",
                              True, LABEL_DIM), (540, note_y + 40 + 6*19))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_4.png")
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
