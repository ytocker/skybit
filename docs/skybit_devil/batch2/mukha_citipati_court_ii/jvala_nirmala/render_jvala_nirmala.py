"""
Round-1 concept renderer for JVALA-NIRMALA — sister #3 of the SECOND bone-deity
brood (mukha_citipati_court_ii), the charnel-ascetic / mountain-cave register.
She is the COOL WISDOM-FLAME DANCER: a Citipati cocked-hip dancing skeleton fused
with the Mukha six-arm radial fan + six palm-skulls, sheathed in a FULL-BODY
cobalt wisdom-flame MANTLE. Headless Pygame; ELEVATED pipeline (SS=8 supersample
-> smoothscale) so the dense draped flame stays crisp at downscale. House
grammar: flat saturated fills, hard ink keyline (28,22,26), dark-core -> flat-fill
-> top-left rim-sheen triad, 1px alpha-grown outline, chibi scary-cute;
procedural-only (no gradients/PNGs).

WHY she must NOT read as "a blue vajra_rakta": three taken sisters already own
the FLAME-as-HEAD-RING / closed-HALO grammar (vajra_rakta's flame-ring,
ratna_padmini's flame-halo, the Citipati reference's own ember-ring). The whole
job here is distinctness in PLACEMENT + SHAPE, not hue. So the cobalt flame is a
FULL-BODY DRAPED MANTLE — a sheeting SHAWL of overlapping tongues wrapping the
shoulders, both arm-fans, and the kicked-out knee — a filled blue dancing-flame
MASS, never a thin radiating spike-ring behind the head. There is deliberately
NO head-ring and NO closed halo. The mantle tongues route BEHIND the six arms so
all six palm-skulls stay legible.

WHY the crown is value-laddered against the mantle: the triple cobalt flame-crest
sits BEHIND the skull arc and is the SAME cold family as the mantle, so the
5-skull arc is forced OPAQUE PALE-BONE reading clearly IN FRONT of the crest
(value gap), and the Mukha tiara-BAND crosses the brow under it. The white-blue
third-eye is the single brightest pixel and OUT-GLOWS the crown-centre skull by a
wide value gap so the two near-white points never tie.

WHY a standalone script under docs/: review art must never enter the shipped
bundle, so it reuses only colour math + the triad/outline helpers, not runtime
sprite modules.
"""
import math
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

# ── PINNED PALETTE (locked brief) ─────────────────────────────────────────────
# Pale-BONE is the figure mass; deep saturated COBALT is a FILLED flame field
# (not a thin glow rim); ice-white is the focal/highlight. NO warm note anywhere.
BONE      = (232, 234, 224)   # pale-bone (the figure mass — cool-neutral, no warmth)
BONE_D    = (168, 174, 172)   # bone dark-core / shade
BONE_DD   = (104, 112, 118)   # deepest bone hollow (sockets, rib gaps)
BONE_SH   = (215, 218, 222)   # bone top-left rim-sheen — PEAK DROPPED so the cranium
                              # hot-spots never out-brighten the third-eye core at 32px
                              # (the eye must be the single brightest pixel on both chips)
# the cobalt mantle is a filled MASS with a clear value ladder so sheeting tongues
# overlap legibly: deep field -> mid cobalt -> bright ice-edge tips.
COBALT_DD = ( 14,  28,  92)   # deepest cobalt (drapery under-fold shadow / overlaps)
COBALT_D  = ( 30,  62, 172)   # deep saturated cobalt field (the dominant mantle mass)
COBALT    = ( 54, 108, 222)   # mid cobalt flame body
COBALT_BR = ( 98, 162, 240)   # bright cobalt fold-crest (NO bloom — a value step only)
ICE       = (168, 206, 246)   # cool edge keyline on a leading fold (muted, never a glow)
INK       = ( 28,  22,  26)   # hard ink keyline
# the third-eye is the single brightest element — a near-white ICE that must
# OUT-glow EVERYTHING by a wide margin. Held DELIBERATELY brighter than any
# cobalt fold-crest and than the crown-centre skull (which gets NO near-white).
EYE_GLOW  = (206, 230, 250)   # third-eye tight glow halo (the ONLY halo on the sheet)
EYE_CORE  = (246, 250, 255)   # third-eye brightest pixel — the lone near-white ice,
                              # nudged toward white so it stays the single brightest
                              # point even after the 32px smoothscale softens it
EYE_RING  = ( 66, 132, 232)   # third-eye cobalt iris (frames the ice core)

BG        = ( 90,  94, 104)   # neutral grey review backdrop
PANEL     = ( 70,  74,  86)
DAY_SKY_T = (120, 196, 236)   # day biome sky (top)
DAY_SKY_B = (196, 232, 244)
NIGHT_T   = ( 22,  26,  54)   # night biome sky (top)
NIGHT_B   = ( 48,  44,  82)
LABEL     = (240, 240, 244)
LABEL_DIM = (192, 198, 210)


def lerp(a, b, t):
    t = max(0.0, min(1.0, t))
    return (int(a[0] + (b[0]-a[0])*t),
            int(a[1] + (b[1]-a[1])*t),
            int(a[2] + (b[2]-a[2])*t))


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


def _sheen_of(color):
    # WHY cap the bone sheen instead of lerping to pure white: a near-white sheen
    # on the pale-bone cranium out-brightens the third-eye core at 32px (the
    # identity-breaking value tie). For bone-family fills the sheen is clamped to
    # the dimmed cool BONE_SH peak so the eye stays the single brightest pixel;
    # the saturated cobalt mantle keeps its ordinary bright fold-crest sheen.
    if color[0] > 180 and color[1] > 180:
        return BONE_SH
    return lerp(color, (255, 255, 255), 0.4)


def triad_blob(surf, color, pts, sheen_pts=None, core_pts=None, outline=True, ow=2):
    """Flat fill + optional dark-core + top-left rim-sheen + ink keyline."""
    if outline:
        pygame.draw.polygon(surf, INK, pts)
    pygame.draw.polygon(surf, color, pts)
    if core_pts:
        pygame.draw.polygon(surf, lerp(color, INK, 0.42), core_pts)
    if sheen_pts:
        pygame.draw.polygon(surf, _sheen_of(color), sheen_pts)
    if outline:
        pygame.draw.polygon(surf, INK, pts, ow)


def triad_circle(surf, color, c, r, ow=2, sheen=True, core=True):
    """Round equivalent of triad_blob — dark core bottom-right, sheen top-left."""
    pygame.draw.circle(surf, INK, c, r + max(1, ow // 2))
    pygame.draw.circle(surf, color, c, r)
    if core:
        pygame.draw.circle(surf, lerp(color, INK, 0.4),
                           (c[0] + int(r * 0.28), c[1] + int(r * 0.30)),
                           int(r * 0.74))
        pygame.draw.circle(surf, color, c, int(r * 0.82))
    if sheen:
        pygame.draw.circle(surf, _sheen_of(color),
                           (c[0] - int(r * 0.38), c[1] - int(r * 0.40)),
                           max(1, int(r * 0.26)))
    pygame.draw.circle(surf, INK, c, r, ow)


def bone_limb(surf, p0, p1, p2, thick, s, joint=True):
    """Two-segment pale-bone limb with ink keyline + bulbous joint (Citipati)."""
    for (a, b) in ((p0, p1), (p1, p2)):
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = max(1.0, math.hypot(dx, dy))
        nx, ny = -dy / L * thick / 2, dx / L * thick / 2
        quad = [(a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny),
                (b[0] - nx, b[1] - ny), (a[0] - nx, a[1] - ny)]
        triad_blob(surf, BONE, quad,
                   sheen_pts=[(a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny),
                              (b[0] + nx * 0.3, b[1] + ny * 0.3),
                              (a[0] + nx * 0.3, a[1] + ny * 0.3)],
                   ow=max(1, int(thick * 0.18)))
    if joint:
        triad_circle(surf, BONE, p1, int(thick * 0.62), ow=max(1, int(1.2 * s)),
                     core=False)


# ── ONE curled flame-LICK — the cloth-of-flame drapery unit (NOT a spike) ─────
def flame_lick(surf, bx, by, ang, length, width, s, lit=0.0, curl=0.9, fill=None):
    """A single CURLED flame-lick: a candle-flame lobe whose tip CURLS BACK over
    itself in an S-curve, so the silhouette UNDULATES (a fold of drapery) instead
    of bristling outward like a spike. WHY built from a curved spine, not a
    triangle: the whole collision gate is shape — the taken fire sisters own the
    straight radiating triangular tongue. Here the spine bows (curl) and the lobe
    is wide-bellied near the base and hooks at the cusp, reading as a tongue of
    cloth-flame folding, never a needle pointing away.

    `ang` = mean direction the lick reaches; `curl` bends the spine sideways
    (sign = curl handedness). `lit` 0..1 picks the cobalt value band. The lobe is
    drawn as one filled polygon: left rib up the curved spine, hook the cusp,
    right rib back down — with an inner darker under-fold so stacked licks read as
    overlapping folds, and a thin cooler keyline on the LEADING rib only."""
    body = fill if fill is not None else lerp(COBALT_D, COBALT, lit)
    under = lerp(COBALT_DD, COBALT_D, lit)
    crest = lerp(COBALT, COBALT_BR, lit)
    perp = ang + math.pi / 2
    # sample the curved spine: it leans `curl` off-axis and eases to a hooked cusp
    spine = []
    for i in range(7):
        t = i / 6.0
        # spine length eases; lateral bow grows then the cusp hooks further over
        r = length * t
        bow = curl * width * (1.4 * t * t)          # accelerating sideways curl
        sx = bx + math.cos(ang) * r + math.cos(perp) * bow
        sy = by + math.sin(ang) * r + math.sin(perp) * bow
        # belly width: fat near base, easing to a ROUNDED (not needle) cusp — the
        # tip keeps a small radius so the hem undulates as scalloped folds, never
        # bristles into points (the collision-gate distinctness)
        w = width * (0.30 + 0.70 * (1.0 - t) ** 0.85) * (0.62 + 0.38 * math.sin(t * math.pi))
        spine.append((sx, sy, w))
    # build the closed lobe: up the left rib, around the cusp, back down the right
    left, right = [], []
    for (sx, sy, w) in spine:
        left.append((sx + math.cos(perp) * w, sy + math.sin(perp) * w))
        right.append((sx - math.cos(perp) * w, sy - math.sin(perp) * w))
    lobe = left + right[::-1]
    pygame.draw.polygon(surf, INK, lobe)
    pygame.draw.polygon(surf, body, lobe)
    # under-fold: the trailing (curl-side) half sits in shadow so folds stack
    shadow = right[::-1] + [(spine[i][0], spine[i][1]) for i in range(len(spine))]
    pygame.draw.polygon(surf, under, shadow)
    # leading-rib crest value + a thin cool keyline ON THE LEADING EDGE ONLY
    crest_band = left + [(spine[i][0], spine[i][1]) for i in range(len(spine) - 1, -1, -1)]
    pygame.draw.polygon(surf, crest, crest_band)
    if len(left) >= 2:
        pygame.draw.lines(surf, ICE, False, left, max(1, int(1.3 * s)))
    pygame.draw.polygon(surf, INK, lobe, max(1, int(1.1 * s)))
    return spine[-1][:2]   # the cusp point (for chaining)


def mantle_sheet(surf, anchor, ang, length, width, s, n=4, lit=0.0,
                 curl=0.9, spread=0.85, fan=1.15):
    """One PANEL of the cloth-of-flame mantle: a row of CURLED licks that OVERLAP
    and fold back over each other so the outer hem UNDULATES (cusp-valley-cusp)
    rather than bristling. WHY rows of curled licks, not a fan of spikes: drapery
    reads as overlapping sheeting cloth — each lick partly covers its neighbour, and
    the alternating curl handedness makes a scalloped, woven hem (a shawl), the
    anti-thesis of a radiating spike-ring. Internal overlap lines are implicit in
    each lick's under-fold. Licks are laid base-to-tip across the anchor so the
    panel hangs as a continuous sheet, all curls leaning the SAME way (toward the
    body centre) so it folds like worn cloth."""
    licks = []
    for i in range(n):
        f = (i - (n - 1) / 2.0) / max(1, (n - 1))   # -0.5..0.5 across the panel
        a = ang + f * spread
        L = length * (0.82 + 0.26 * (1 - abs(f)))    # centre licks reach furthest
        # seat the lick bases along an arc across the anchor so they sheet, overlap
        bx = anchor[0] + math.cos(ang + math.pi / 2) * width * f * fan
        by = anchor[1] + math.sin(ang + math.pi / 2) * width * f * fan
        # curl handedness leans toward panel centre so neighbours fold over inward
        c = curl * (-1.0 if f > 0 else 1.0) * (0.55 + abs(f))
        licks.append((abs(f), bx, by, a, L, c))
    # draw outer licks first; inner licks then OVERLAP them (drapery layering)
    licks.sort(key=lambda t: -t[0])
    for (af, bx, by, a, L, c) in licks:
        flame_lick(surf, bx, by, a, L, width * (0.62 - 0.10 * af), s,
                   lit=lit + (1 - af) * 0.22, curl=c)


# ── a single ornamental crown-skull (reused for the arc + the pillar cap) ─────
def crown_skull(surf, cx, cy, r, s, lit=False, idx=0):
    """Tiny pale-bone skull — the arc skulls are OPAQUE bone so they read clearly
    IN FRONT of the cobalt crest behind them (value separation). `lit` swaps the
    centre skull's eye-pins to a cool ice pin — but kept BELOW the third-eye so the
    value gap holds. `idx` (0..4 across the arc) gives the arc the SAME construction
    VARIETY as the palm relics — a different cranium SILHOUETTE per slot (round /
    narrow-tall / faceted-angular, width/height varied ~15-20%) so the arc is not
    one dome ×5 either.

    This is the DIMMEST frost tier and MUST stay clean at 32px: a single hairline
    ink seam (or a flat cobalt fleck on one slot only) — NO crack network, NO frost
    cap, NO glow. All flat fills under the value of the third-eye."""
    lw = max(1, int(1.6 * s))
    fine = max(1, int(1.0 * s))
    # cranium silhouette varies per arc slot, mirroring the palm relics' variety
    shape = idx % 5
    if shape in (1, 3):
        # narrow-tall egg vault — pushed taller/slimmer so the arc isn't a uniform
        # comb of identical bumps at 32px (this slot reads as a clear tall peak)
        ell = pygame.Rect(0, 0, int(r * 1.48), int(r * 2.36))
        ell.center = (cx, cy - int(r * 0.16))
        pygame.draw.ellipse(surf, INK, ell.inflate(lw, lw))
        pygame.draw.ellipse(surf, BONE, ell)
    elif shape == 2:
        # faceted angular vault — flat-planed crown with an ASYMMETRIC top edge
        # (the left plane sheared lower than the right) so the centre slot reads as
        # its own crisp silhouette at chip scale, not a mirror-symmetric dome
        cap = [(cx - int(r * 0.92), cy - int(r * 0.04)),
               (cx - int(r * 0.30), cy - int(r * 0.66)),
               (cx + int(r * 0.44), cy - int(r * 0.98)),
               (cx + int(r * 0.92), cy - int(r * 0.16)),
               (cx + int(r * 0.62), cy + int(r * 0.44)),
               (cx - int(r * 0.62), cy + int(r * 0.44))]
        triad_blob(surf, BONE, cap, ow=lw)
    else:
        # shape 0 / 4: round vault baseline
        triad_circle(surf, BONE, (cx, cy), r, ow=lw, core=False)
    jaw = [(cx - int(r * 0.52), cy + int(r * 0.52)),
           (cx + int(r * 0.52), cy + int(r * 0.52)),
           (cx + int(r * 0.34), cy + int(r * 1.0)),
           (cx - int(r * 0.34), cy + int(r * 1.0))]
    triad_blob(surf, BONE, jaw, ow=max(1, int(1.2 * s)))
    eye_c = COBALT_BR if lit else INK
    for ex in (cx - int(r * 0.38), cx + int(r * 0.38)):
        pygame.draw.circle(surf, INK, (ex, cy + int(r * 0.04)), max(1, int(r * 0.24)))
        if lit:
            pygame.draw.circle(surf, eye_c, (ex, cy + int(r * 0.04)), max(1, int(r * 0.13)))
    pygame.draw.circle(surf, INK, (cx, cy + int(r * 0.42)), max(1, int(r * 0.13)))
    pygame.draw.line(surf, INK,
                     (cx - int(r * 0.34), cy + int(r * 0.70)),
                     (cx + int(r * 0.34), cy + int(r * 0.70)),
                     max(1, int(1.2 * s)))
    # frost echo (DIMMEST): a single short hairline ink seam (drawn-flat). The two
    # narrow-tall slots carry a hairline crown seam; the faceted centre carries one
    # INK seam only; the round slots stay essentially clean — none gets a crack
    # network or frost cap, so the arc stays crisp at 32px with NO glow.
    # WHY the faceted centre's fleck is now INK, not cobalt: the third-eye must be
    # the ONLY saturated-blue point in the crown silhouette at 32px — a 2nd blue
    # fleck right beside it read as a rival blue point on the night chip.
    if shape in (1, 3):
        pygame.draw.line(surf, INK, (cx + int(r * 0.08), cy - int(r * 0.86)),
                         (cx - int(r * 0.10), cy - int(r * 0.34)), fine)
    elif shape == 2:
        pygame.draw.line(surf, INK, (cx + int(r * 0.22), cy - int(r * 0.50)),
                         (cx + int(r * 0.34), cy - int(r * 0.30)), fine)


# ── a tiny cradled palm-skull (the core Mukha motif) ──────────────────────────
def palm_skull(surf, cx, cy, r, s, idx=0):
    """A tiny charnel relic cradled in an open palm — six ride the fan-tips and
    MUST stay legible (mantle routes behind them). The SIX are genuinely DISTINCT
    CONSTRUCTIONS, not one dome re-cracked: each gets its own CRANIUM SILHOUETTE
    (width/height varied ~15-20% across the set so the difference survives 32px)
    AND its own silhouette-altering FROST archetype:

        idx 0 (left)  — round vault + FORKED ice-fracture NETWORK (branching Y).
        idx 1 (right) — narrow-tall vault under a thick flat RIME-FROST CAP, no
                        crack; carries cobalt socket #1.
        idx 2 (left)  — CALVED TALL VAULT: tall/narrow with a CHUNK SHEARED off the
                        upper-left crown (flat-faceted break that alters the outline)
                        + an L-shaped calving crack.
        idx 3 (right) — round vault, one FROZEN-OVER socket filled flat with pale
                        ICE/BONE (NOT cobalt) so cobalt stays scarce; hairline only.
        idx 4 (left)  — broad-low vault + ICICLE-TOOTHED jaw (downward ice fangs).
        idx 5 (right) — CLEAN ANGULAR RELIC: faceted hexagonal-leaning cranium,
                        minimal damage; carries cobalt socket #2.

    Cobalt lands on EXACTLY two flat sockets (idx 1 & 5, the right palm skulls);
    the frozen-over socket (idx 3) is pale ICE, never cobalt, so the cobalt count
    holds at two and the value ladder is preserved.

    CRITICAL: every accent — including the two drawn-FLAT cobalt sockets — is a
    FLAT fill with the INK keyline. NO additive/glow surface, NO bloom anywhere.
    jvala's cobalt third-eye stays the single brightest pixel AND the only glow on
    the whole sheet; these relics sit a clear value step below it.

    WHY idx is the primary seed (position hash kept as a light secondary jitter):
    the orchestrator passes the hand index so the six can be cleanly individuated
    and gem-assigned, while a tiny position wobble keeps each placement organic."""
    # secondary seed: a faint position jitter on tilt only, so identical idx in
    # different layouts still feel hand-placed (renders stay deterministic).
    h = (cx * 73 + cy * 131) & 0xFFFF
    tilt = (((idx - 2.5) * 0.04) + ((h % 5) - 2) * 0.012)
    ct, st = math.cos(tilt), math.sin(tilt)

    def rot(dx, dy):
        # rotate an offset by the per-skull tilt, return absolute pixel point
        return (cx + int(dx * ct - dy * st), cy + int(dx * st + dy * ct))

    lw = max(1, int(1.2 * s))
    fine = max(1, int(1.0 * s))
    rime = lerp(BONE, ICE, 0.5)            # pale ice-bone for drawn-flat frost dabs

    # per-idx jaw gape + which sockets carry the (exactly two) cobalt fills. The
    # frozen socket (idx 3) is ICE, NOT cobalt, so cobalt stays scarce at two.
    jaw_open = (0.10, 0.06, 0.12, 0.08, 0.22, 0.10)[idx % 6]
    cobalt_socket = idx in (1, 5)

    # ── CRANIUM SILHOUETTE — a genuinely DIFFERENT shape per idx ─────────────────
    # WHY the radius/proportion varies ~15-20% across the set: a uniform dome
    # radius is exactly what reads as "one skull re-tilted." Two are narrow-tall
    # (1,2), two are round (0,3), one is broad-low (4), one is faceted-angular (5).
    if idx == 0:
        # round mid vault — the baseline ROUND construction (frost is the network)
        triad_circle(surf, BONE, (cx, cy), r, ow=lw, core=False)
    elif idx == 1:
        # NARROW-TALL egg vault (rime-cap archetype): taller, slimmer than round.
        # WHY pushed even taller/narrower: at 32px the crown was reading as a
        # uniform comb of identical bumps — exaggerating this slot's tall-slim
        # proportion makes it the clear PEAK of the row against its neighbours.
        ell = pygame.Rect(0, 0, int(r * 1.42), int(r * 2.34))
        ell.center = rot(0, -r * 0.20)
        pygame.draw.ellipse(surf, INK, ell.inflate(lw * 2, lw * 2))
        pygame.draw.ellipse(surf, BONE, ell)
    elif idx == 2:
        # CALVED TALL VAULT: a tall narrow dome with a CHUNK SHEARED off the
        # upper-LEFT crown — a flat-faceted break that genuinely alters the OUTLINE
        # (drawn as a clipped polygon dome so the missing corner is part of the
        # silhouette, not an overlay). Reads as calved glacier-ice bone.
        # WHY the shear is now more AGGRESSIVE + asymmetric (a deeper bite taken
        # out of the upper-left, the right crown pushed taller): at 32px a gentle
        # bevel reads as just another dome bump in a uniform comb — a hard
        # asymmetric top edge gives this slot a silhouette that survives downscale.
        vault = [rot(-r * 0.70, r * 0.30), rot(-r * 0.76, -r * 0.22),
                 rot(-r * 0.16, -r * 0.52),                 # deep sheared flat facet ↑
                 rot(r * 0.10, -r * 1.16), rot(r * 0.62, -r * 0.82),
                 rot(r * 0.90, -r * 0.10), rot(r * 0.80, r * 0.36)]
        triad_blob(surf, BONE, vault, ow=lw)
        # dark inner shelf along the sheared facet so the break reads as depth
        pygame.draw.polygon(surf, BONE_DD, [rot(-r * 0.76, -r * 0.22),
                            rot(-r * 0.16, -r * 0.52), rot(-r * 0.20, -r * 0.10)])
    elif idx == 5:
        # CLEAN ANGULAR RELIC: a faceted, hexagonal-leaning cranium (six flat
        # planes) — minimal damage. The angular outline is the differentiator.
        cap = [rot(-r * 0.88, -r * 0.12), rot(-r * 0.46, -r * 0.92),
               rot(r * 0.46, -r * 0.92), rot(r * 0.88, -r * 0.12),
               rot(r * 0.60, r * 0.44), rot(-r * 0.60, r * 0.44)]
        triad_blob(surf, BONE, cap, ow=lw)
    elif idx == 4:
        # BROAD-LOW brachycephalic vault — squat + wide (the icicle-jaw skull).
        # WHY pushed broader + lower: it must stay a distinct BROAD-LOW dome at
        # 32px, never a twin of the clean-angular relic (idx5) whose outline is
        # tall-faceted; widening + flattening this one keeps the pair separable.
        ell = pygame.Rect(0, 0, int(r * 2.42), int(r * 1.52))
        ell.center = rot(0, r * 0.02)
        pygame.draw.ellipse(surf, INK, ell.inflate(lw * 2, lw * 2))
        pygame.draw.ellipse(surf, BONE, ell)
    else:
        # idx 3: round vault (frozen-socket archetype rides a clean round dome)
        triad_circle(surf, BONE, (cx, cy), r, ow=lw, core=False)

    # cheek/jaw bone block tucked under the dome so the head reads as a skull,
    # not a ball — kept inside r so the silhouette footprint is unchanged
    jp = [rot(-r * 0.46, r * 0.18), rot(-r * 0.30, r * 0.66),
          rot(r * 0.30, r * 0.66), rot(r * 0.46, r * 0.18)]
    pygame.draw.polygon(surf, BONE, jp)
    pygame.draw.polygon(surf, INK, jp, fine)

    # cranial suture — a faint forked seam over the crown (BONE_D, drawn not glow).
    # Skipped on the rime-cap skull (idx 1) — the frost cap covers the crown.
    if idx != 1:
        sb = rot(0, -r * 0.10)
        pygame.draw.line(surf, BONE_D, rot(0, -r * 0.78), sb, fine)
        pygame.draw.line(surf, BONE_D, sb, rot(-r * 0.30, r * 0.04), fine)
        pygame.draw.line(surf, BONE_D, sb, rot(r * 0.30, r * 0.04), fine)

    # brow ridge — a shaded bone bar above the sockets gives the skull a glower
    pygame.draw.line(surf, BONE_D, rot(-r * 0.52, -r * 0.18),
                     rot(r * 0.52, -r * 0.18), max(1, int(1.6 * s)))

    # temple / cheek hollows — soft bone shade scooped beside the sockets
    for sgn in (-1, 1):
        pygame.draw.circle(surf, BONE_D, rot(sgn * r * 0.62, r * 0.06),
                           max(1, int(r * 0.18)))

    # ── two sockets — idx 3 has one FROZEN-OVER (ICE); idx 1 & 5 carry cobalt ────
    for k, sgn in enumerate((-1, 1)):
        ec = rot(sgn * r * 0.40, -r * 0.02)
        pygame.draw.circle(surf, BONE_DD, ec, max(1, int(r * 0.34)))
        if idx == 3 and sgn == -1:
            # frozen-over socket: a flat ICE/BONE plate caps the cavity (rime ring
            # + pale-ice fill) — a socket glazed shut with frost. NO cobalt (keeps
            # cobalt scarce at two), NO glow; the rim keyline is ink, not cobalt.
            pygame.draw.circle(surf, INK, ec, max(1, int(r * 0.30)))
            pygame.draw.circle(surf, rime, ec, max(1, int(r * 0.24)))
            pygame.draw.circle(surf, lerp(ICE, (255, 255, 255), 0.5), ec,
                               max(1, int(r * 0.12)))
            pygame.draw.circle(surf, INK, ec, max(1, int(r * 0.24)), max(1, fine))
        elif cobalt_socket:
            # DRAWN-FLAT cobalt-filled socket: flat cobalt disc set in the ink
            # pit, dimmer than the third-eye, no additive blending whatsoever.
            # WHY pulled ~one half-step darker/desaturated (toward COBALT_D): the
            # two sockets read clearly cobalt in the hero, but at 32px they must
            # stay SUBORDINATE to the third-eye and not flash as rival blue points
            # beside it. Still flat-fill, no glow, count held at exactly two.
            pygame.draw.circle(surf, INK, ec, max(1, int(r * 0.30)))
            pygame.draw.circle(surf, COBALT_D, ec, max(1, int(r * 0.26)))
            pygame.draw.circle(surf, lerp(COBALT, COBALT_D, 0.5), ec, max(1, int(r * 0.15)))
        else:
            pygame.draw.circle(surf, INK, ec, max(1, int(r * 0.27)))

    # heart-shaped nasal cavity (two ink dabs that meet) under the brow
    pygame.draw.circle(surf, INK, rot(-r * 0.10, r * 0.30), max(1, int(r * 0.12)))
    pygame.draw.circle(surf, INK, rot(r * 0.10, r * 0.30), max(1, int(r * 0.12)))

    # ── jaw — idx 4 is ICICLE-TOOTHED (frost fangs hang from the mouth) ──────────
    my = r * (0.56 + jaw_open)
    ml, mr = rot(-r * 0.40, my), rot(r * 0.40, my)
    if idx == 4:
        # NO flat tooth-bar: 4 drawn-flat pale-ice triangles taper DOWN off the
        # jaw line (frozen fangs), each with an ink keyline. This replaces the bar.
        for t in (-0.30, -0.12, 0.06, 0.24):
            tx, ty = rot(t * r, my)
            tri = [(tx - int(r * 0.08), ty), (tx + int(r * 0.08), ty),
                   (tx + int((t * 0.4) * r * 0.1), ty + int(r * 0.34))]
            pygame.draw.polygon(surf, INK, tri)
            pygame.draw.polygon(surf, rime,
                                [(tx - int(r * 0.055), ty), (tx + int(r * 0.055), ty),
                                 (tx + int((t * 0.4) * r * 0.1), ty + int(r * 0.27))])
    else:
        pygame.draw.line(surf, INK, ml, mr, lw)
        for t in (-0.24, -0.08, 0.08, 0.24):
            tx, ty = rot(t * r, my)
            pygame.draw.line(surf, INK, (tx, ty - int(r * 0.16)), (tx, ty), fine)

    # top-left bone sheen so the dome catches the same key as the rest of the sheet
    pygame.draw.circle(surf, BONE_SH, rot(-r * 0.34, -r * 0.40), max(1, int(r * 0.16)))

    # ── per-idx FROST CONSTRUCTION (all DRAWN-FLAT, no glow) ─────────────────────
    if idx == 0:
        # FORKED ice-fracture NETWORK: a branching Y-crack (a trunk that splits
        # into two limbs, each forking again) — NOT a single vertical line. Ink
        # hairlines with a few pale-rime glints at the nodes.
        trunk_top = rot(r * 0.06, -r * 0.20)
        fork = rot(-r * 0.02, -r * 0.62)
        pygame.draw.line(surf, INK, trunk_top, fork, fine)
        for end in (rot(-r * 0.44, -r * 0.84), rot(r * 0.40, -r * 0.92)):
            pygame.draw.line(surf, INK, fork, end, fine)
            pygame.draw.circle(surf, rime, end, max(1, fine))
        # a secondary branch forking off the left limb so the network reads as a tree
        midL = rot(-r * 0.22, -r * 0.73)
        pygame.draw.line(surf, INK, midL, rot(-r * 0.50, -r * 0.46), fine)
        pygame.draw.circle(surf, rime, fork, max(1, fine))
    elif idx == 1:
        # RIME-FROST CAP: a thick FLAT pale-ice cap sitting on the crown of the
        # narrow-tall vault (a rounded frost plate, NOT a crack). Drawn-flat rime
        # with an ink underline + a couple of softer ice highlights ON the cap.
        cap = [rot(-r * 0.62, -r * 0.52), rot(-r * 0.40, -r * 0.96),
               rot(r * 0.36, -r * 1.0), rot(r * 0.60, -r * 0.50),
               rot(r * 0.30, -r * 0.62), rot(0, -r * 0.54),
               rot(-r * 0.32, -r * 0.64)]
        pygame.draw.polygon(surf, INK, cap)
        pygame.draw.polygon(surf, rime, [rot(-r * 0.56, -r * 0.54),
                            rot(-r * 0.36, -r * 0.90), rot(r * 0.32, -r * 0.94),
                            rot(r * 0.54, -r * 0.52), rot(r * 0.26, -r * 0.62),
                            rot(0, -r * 0.56), rot(-r * 0.28, -r * 0.64)])
        # a soft brighter ice ridge along the cap's left lip (drawn-flat, no glow)
        pygame.draw.line(surf, lerp(ICE, (255, 255, 255), 0.35),
                         rot(-r * 0.40, -r * 0.84), rot(r * 0.20, -r * 0.90),
                         max(1, fine))
    elif idx == 2:
        # CALVED break — an L-SHAPED calving crack tracing down from the sheared
        # facet then jogging sideways (the fracture that let the corner shear off).
        a = rot(-r * 0.30, -r * 0.46)
        b = rot(-r * 0.10, r * 0.06)
        c = rot(r * 0.34, r * 0.10)
        pygame.draw.lines(surf, INK, False, [a, b, c], fine)
        pygame.draw.line(surf, rime, rot(-r * 0.26, -r * 0.40),
                         rot(-r * 0.12, r * 0.0), max(1, fine))
    elif idx == 5:
        # CLEAN angular relic: minimal damage — only a single short hairline ink
        # seam along one facet edge + a tiny rime glint. No fracture network.
        pygame.draw.line(surf, INK, rot(r * 0.30, -r * 0.72),
                         rot(r * 0.12, -r * 0.30), fine)
        pygame.draw.circle(surf, rime, rot(r * 0.22, -r * 0.52), max(1, fine))
    # idx 3 frost is its frozen ICE socket (above) + a faint hairline crown seam
    if idx == 3:
        pygame.draw.line(surf, INK, rot(r * 0.10, -r * 0.82),
                         rot(-r * 0.02, -r * 0.30), fine)


def open_palm(surf, hx, hy, ang, r, s):
    """An open bone palm cradling a skull — a small cup of finger ticks fanning up
    around the cradled palm-skull. Drawn so the skull nests in the cup."""
    # palm pad
    triad_circle(surf, BONE, (hx, hy), int(r * 0.7), ow=max(1, int(1.2 * s)), core=False)
    # finger ticks fanning outward (the cradle)
    for k in range(-2, 3):
        fa = ang + k * 0.34
        ex = hx + math.cos(fa) * r * 1.25
        ey = hy + math.sin(fa) * r * 1.25
        pygame.draw.line(surf, INK, (hx, hy), (ex, ey), max(1, int(2.0 * s)))
        pygame.draw.line(surf, BONE, (hx, hy), (ex, ey), max(1, int(1.2 * s)))


# ── the six-arm radial fan (Mukha KIND, grafted onto the Citipati torso) ──────
def draw_arm_fan(surf, sh_cx, sh_cy, s, hr):
    """Six fat bone arms splay in a wide symmetric STARBURST from a LOW shoulder
    origin (Mukha radial fan). No arm aims straight up — the crown sky stays open.
    Spread ~[100,64,28] deg off vertical, three per side. Returns the six hand
    centres + their outward angles for palm + cradled-skull placement."""
    arm_len = int(hr * 1.95)
    arm_th = int(12 * s)
    spread = [100, 64, 28]
    order = []
    for sgn in (-1, 1):
        for d in spread:
            a = math.radians(-90 + sgn * d)
            order.append((sgn, d, a))
    order.sort(key=lambda o: -o[1])   # lowest arms first so upper splay overlaps
    hands = []
    for sgn, d, a in order:
        sh = (sh_cx + sgn * int(hr * 0.55), sh_cy)
        elbow = (sh[0] + math.cos(a) * arm_len * 0.52,
                 sh[1] + math.sin(a) * arm_len * 0.52)
        hand = (sh[0] + math.cos(a) * arm_len,
                sh[1] + math.sin(a) * arm_len)
        for (p, q) in ((sh, elbow), (elbow, hand)):
            dx, dy = q[0] - p[0], q[1] - p[1]
            L = max(1.0, math.hypot(dx, dy))
            nx, ny = -dy / L * arm_th / 2, dx / L * arm_th / 2
            quad = [(p[0] + nx, p[1] + ny), (q[0] + nx, q[1] + ny),
                    (q[0] - nx, q[1] - ny), (p[0] - nx, p[1] - ny)]
            triad_blob(surf, BONE, quad,
                       sheen_pts=[(p[0] + nx, p[1] + ny), (q[0] + nx, q[1] + ny),
                                  (q[0] + nx * 0.3, q[1] + ny * 0.3),
                                  (p[0] + nx * 0.3, p[1] + ny * 0.3)],
                       ow=max(1, int(arm_th * 0.16)))
        triad_circle(surf, BONE, (int(elbow[0]), int(elbow[1])), int(arm_th * 0.55),
                     ow=max(1, int(1.2 * s)), core=False)
        hands.append((int(hand[0]), int(hand[1]), a))
    return hands


# ── the cool wisdom-flame dancer ──────────────────────────────────────────────
def draw_jvala(surf, cx, cy, s):
    """Citipati cocked-hip dancing skeleton (tall rib-barrel torso, one knee
    kicked out) wearing the Mukha six-arm fan + six cradled palm-skulls, all
    sheathed in a FULL-BODY cobalt wisdom-flame MANTLE (sheeting shawl). Fused
    crown: triple cobalt flame-crest behind an opaque 5-skull arc + Mukha
    tiara-band across the brow. White-blue third-eye out-glows the crown centre.
    `s` = unit scale around a ~140-unit figure."""

    head_c = (cx, cy - int(30 * s))
    hr = int(23 * s)
    hip_y = cy + int(24 * s)
    hip_cx = cx + int(7 * s)
    rc_cx, rc_cy = cx, cy - int(2 * s)
    rc_w, rc_h = int(34 * s), int(40 * s)
    sh_line_y = rc_cy - rc_h // 2 + int(6 * s)

    # === (1) BACK MANTLE PANELS (drawn FIRST → the shawl behind the whole body) =
    # WHY a full-body field, not a head-ring: a broad cobalt mantle MASS spreads
    # behind shoulders, down both flanks, and out under the kicked-out knee — the
    # silhouette-carrying blue dancing-flame figure. Tongues sheet densely so no
    # sky shows through onto the body. This is the anti-halo placement.
    # broad rear sheet filling behind the torso (the shawl back — a soft dome of
    # short up-curling licks, NOT a starburst). Curls lean inward so it pools.
    mantle_sheet(surf, (cx, rc_cy + int(10 * s)), math.radians(-90),
                 int(40 * s), int(46 * s), s, n=7, lit=0.0, curl=0.7, spread=1.4, fan=1.05)
    # the DRAPED SKIRT-MASS — two big sheeting panels hanging DOWN the flanks and
    # pooling under the hips/knee. WHY mostly downward (>90deg) with strong curl:
    # this is the undulating skirt-mass that must carry the silhouette as a ROBE,
    # the hem scalloping cusp-valley-cusp instead of bristling outward.
    mantle_sheet(surf, (hip_cx - int(12 * s), hip_y - int(2 * s)), math.radians(118),
                 int(62 * s), int(40 * s), s, n=6, lit=0.0, curl=1.0, spread=0.95, fan=1.25)
    mantle_sheet(surf, (hip_cx + int(14 * s), hip_y - int(4 * s)), math.radians(62),
                 int(64 * s), int(42 * s), s, n=6, lit=0.0, curl=1.0, spread=0.95, fan=1.25)
    # a central front apron of licks folding down over the lap (fills the gap so no
    # sky shows through the skirt — keeps the mass dense/opaque)
    mantle_sheet(surf, (hip_cx, hip_y + int(4 * s)), math.radians(90),
                 int(52 * s), int(30 * s), s, n=5, lit=0.06, curl=0.8, spread=0.7, fan=1.0)
    # two shoulder-shawl panels sweeping OUT-and-DOWN behind the arms (curling back
    # over, not radiating up) so the cloth wraps the shoulders like a worn shawl
    mantle_sheet(surf, (rc_cx - int(18 * s), sh_line_y + int(2 * s)), math.radians(208),
                 int(44 * s), int(34 * s), s, n=5, lit=0.08, curl=0.95, spread=0.8, fan=1.2)
    mantle_sheet(surf, (rc_cx + int(18 * s), sh_line_y + int(2 * s)), math.radians(-28),
                 int(44 * s), int(34 * s), s, n=5, lit=0.08, curl=0.95, spread=0.8, fan=1.2)

    # === (2) SIX-ARM RADIAL FAN (bone arms over the back mantle) ===============
    hands = draw_arm_fan(surf, head_c[0], head_c[1] + int(hr * 0.92), s, hr)

    # === (3) LEGS — cocked-hip dance, one knee kicked OUT (Citipati) ===========
    leg_th = int(14 * s)
    hipL = (hip_cx - int(13 * s), hip_y)
    kneeL = (hip_cx - int(20 * s), hip_y + int(26 * s))
    footL = (hip_cx - int(22 * s), hip_y + int(52 * s))
    bone_limb(surf, hipL, kneeL, footL, leg_th, s)
    hipR = (hip_cx + int(11 * s), hip_y)
    kneeR = (hip_cx + int(30 * s), hip_y + int(8 * s))
    footR = (hip_cx + int(20 * s), hip_y + int(34 * s))
    bone_limb(surf, hipR, kneeR, footR, leg_th, s)
    for (fx, fy), sgn in ((footL, -1), (footR, +1)):
        foot = [(fx - int(4 * s), fy - int(2 * s)), (fx + sgn * int(16 * s), fy + int(2 * s)),
                (fx + sgn * int(15 * s), fy + int(10 * s)), (fx - int(5 * s), fy + int(8 * s))]
        triad_blob(surf, BONE, foot, ow=max(1, int(1.4 * s)))

    # === (3b) KNEE MANTLE WRAP — sheeting tongues over the kicked-out knee =====
    # WHY explicitly on the knee: the brief wants the mantle wrapping shoulders/
    # arms/KNEE; a cobalt drape licking up over the thrust knee proves it is a
    # garment on the body, not a backdrop ring.
    mantle_sheet(surf, (kneeR[0] + int(4 * s), kneeR[1]), math.radians(8),
                 int(26 * s), int(20 * s), s, n=4, lit=0.28, curl=1.1, spread=0.7, fan=1.0)

    # === (4) PELVIS + RIBCAGE torso (Citipati rib bands → pillar motif) ========
    pelvis = [(hip_cx - int(17 * s), hip_y - int(4 * s)),
              (hip_cx + int(17 * s), hip_y - int(6 * s)),
              (hip_cx + int(14 * s), hip_y + int(10 * s)),
              (hip_cx, hip_y + int(13 * s)),
              (hip_cx - int(15 * s), hip_y + int(9 * s))]
    triad_blob(surf, BONE, pelvis,
               core_pts=[(hip_cx - int(6 * s), hip_y + int(2 * s)),
                         (hip_cx + int(14 * s), hip_y - int(2 * s)),
                         (hip_cx + int(13 * s), hip_y + int(9 * s)),
                         (hip_cx, hip_y + int(12 * s))],
               ow=max(1, int(1.6 * s)))
    pygame.draw.circle(surf, BONE_DD, (hip_cx, hip_y + int(2 * s)), int(4 * s))

    spine_top_y = cy - int(14 * s)
    spine = [(hip_cx, hip_y - int(2 * s)),
             (cx + int(2 * s), cy + int(6 * s)),
             (cx - int(1 * s), spine_top_y)]
    pygame.draw.lines(surf, INK, False, spine, int(8 * s))
    pygame.draw.lines(surf, BONE, False, spine, int(5 * s))

    cage = [(rc_cx - rc_w // 2, rc_cy - rc_h // 2 + int(2 * s)),
            (rc_cx + rc_w // 2, rc_cy - rc_h // 2),
            (rc_cx + int(rc_w * 0.40), rc_cy + rc_h // 2),
            (rc_cx - int(rc_w * 0.40), rc_cy + rc_h // 2)]
    triad_blob(surf, BONE, cage,
               core_pts=[(rc_cx + int(2 * s), rc_cy - rc_h // 2 + int(3 * s)),
                         (rc_cx + rc_w // 2, rc_cy - rc_h // 2 + int(2 * s)),
                         (rc_cx + int(rc_w * 0.40), rc_cy + rc_h // 2),
                         (rc_cx + int(2 * s), rc_cy + rc_h // 2)],
               sheen_pts=[(rc_cx - rc_w // 2 + int(2 * s), rc_cy - rc_h // 2 + int(3 * s)),
                          (rc_cx - int(4 * s), rc_cy - rc_h // 2 + int(2 * s)),
                          (rc_cx - int(6 * s), rc_cy + int(6 * s)),
                          (rc_cx - rc_w // 2 + int(2 * s), rc_cy + int(4 * s))],
               ow=max(1, int(1.8 * s)))
    for i in range(4):
        ry = rc_cy - rc_h // 2 + int(8 * s) + i * int(8 * s)
        bw = int(rc_w * (0.46 - i * 0.05))
        pygame.draw.arc(surf, BONE_DD,
                        (rc_cx - bw, ry - int(7 * s), bw * 2, int(16 * s)),
                        math.radians(205), math.radians(335), max(2, int(2.4 * s)))
    pygame.draw.line(surf, BONE_DD, (rc_cx, rc_cy - rc_h // 2 + int(6 * s)),
                     (rc_cx, rc_cy + int(6 * s)), max(1, int(2 * s)))

    # === (4b) FRONT MANTLE COLLAR — sheeting tongues draped over the shoulders ==
    # WHY a FRONT drape too: a shawl wraps over the shoulders, not only behind. A
    # band of dense cobalt tongues laps over the collarbones and down the chest
    # sides so the cobalt clearly OVERLAYS the body (a worn garment), and the
    # density means the torso never reads naked. WHY aimed DOWNWARD (>90deg, into
    # the chest) and anchored a touch lower: the collar must NEVER lick up onto the
    # brow and bury the third-eye — it pools down over the sternum.
    mantle_sheet(surf, (rc_cx - int(15 * s), sh_line_y + int(9 * s)), math.radians(130),
                 int(28 * s), int(22 * s), s, n=5, lit=0.42, curl=0.95, spread=0.7, fan=1.05)
    mantle_sheet(surf, (rc_cx + int(15 * s), sh_line_y + int(9 * s)), math.radians(50),
                 int(28 * s), int(22 * s), s, n=5, lit=0.42, curl=0.95, spread=0.7, fan=1.05)
    # a short cobalt cowl row pooling down the upper chest (the collar fold), the
    # brightest licks on the body so the leading edge of the cloth reads
    mantle_sheet(surf, (rc_cx, sh_line_y + int(11 * s)), math.radians(90),
                 int(22 * s), int(28 * s), s, n=6, lit=0.52, curl=0.6, spread=0.6, fan=0.95)

    # === (5) SIX OPEN PALMS each cradling a TINY SKULL =========================
    # WHY drawn AFTER the front mantle, over the bone arms: the palm-skulls are the
    # core motif and must stay frontmost & legible; the mantle was routed behind
    # the arms so nothing occludes the six skulls.
    palm_r = int(8 * s)
    for i, (hx, hy, a) in enumerate(hands):
        open_palm(surf, hx, hy, a, palm_r, s)
        # the cradled skull sits just outward of the palm, in the finger cup; idx
        # individuates each as a distinct frost-cracked relic + gem assignment
        skx = hx + int(math.cos(a) * palm_r * 0.7)
        sky = hy + int(math.sin(a) * palm_r * 0.7)
        palm_skull(surf, skx, sky, int(palm_r * 0.78), s, idx=i)

    # === (6) SKULL HEAD — chibi scary-cute, white-blue third eye ===============
    triad_circle(surf, BONE, head_c, hr, ow=max(2, int(2 * s)))
    for sgn in (-1, 1):
        pygame.draw.circle(surf, BONE_D,
                           (head_c[0] + sgn * int(hr * 0.66), head_c[1] + int(hr * 0.28)),
                           int(hr * 0.26))
    # two big sockets — cool deep cobalt pins, kept DIM so the third-eye out-glows
    for sgn in (-1, 1):
        ex = head_c[0] + sgn * int(hr * 0.44)
        ey = head_c[1] + int(hr * 0.04)
        pygame.draw.circle(surf, BONE_DD, (ex, ey), int(hr * 0.34))
        pygame.draw.circle(surf, INK, (ex, ey), int(hr * 0.28))
        pygame.draw.circle(surf, COBALT_D, (ex + sgn * int(1 * s), ey + int(1 * s)),
                           int(hr * 0.13))
    # nose triangle
    pygame.draw.polygon(surf, BONE_DD,
                        [(head_c[0] - int(hr * 0.14), head_c[1] + int(hr * 0.26)),
                         (head_c[0] + int(hr * 0.14), head_c[1] + int(hr * 0.26)),
                         (head_c[0], head_c[1] + int(hr * 0.52))])
    my = head_c[1] + int(hr * 0.68)
    pygame.draw.line(surf, INK, (head_c[0] - int(hr * 0.5), my),
                     (head_c[0] + int(hr * 0.5), my), max(1, int(2 * s)))
    for k in range(-3, 4):
        pygame.draw.line(surf, INK, (head_c[0] + int(k * hr * 0.16), my - int(hr * 0.1)),
                         (head_c[0] + int(k * hr * 0.16), my + int(hr * 0.14)), max(1, int(1 * s)))

    # === (7) FUSED CROWN — triple cobalt flame-crest BEHIND, opaque 5-skull arc =
    #         + Mukha tiara-BAND across the brow, all IN FRONT of the crest =======
    # WHY small + contained + drawn FIRST: three short curling cobalt flame-licks
    # peek up from BEHIND the head and will sit between/above the bone skulls; the
    # opaque arc + band drawn afterward must clearly read in FRONT (the un-fuse
    # rule). Each crest lick CURLS so it matches the mantle cloth, not a spike.
    crest_cy = head_c[1] - int(hr * 0.62)
    for cx_off, lift, hand in ((-int(hr * 0.70), 0.80, 1),
                               (0.0, 1.0, 1),
                               (int(hr * 0.70), 0.80, -1)):
        anchor = (head_c[0] + cx_off, crest_cy)
        flame_lick(surf, anchor[0], anchor[1], math.radians(-90),
                   int(hr * 1.05 * lift), int(hr * 0.46), s,
                   lit=0.18, curl=0.85 * hand)

    # Mukha tiara BAND across the brow — an OPAQUE warm-bone strip drawn over the
    # crest. WHY a fat opaque band (not a thin line) and warm-lighter than cobalt:
    # the same-cool crest would otherwise swallow it; a bone-warm value-separated
    # strip reads clearly in FRONT of the flame.
    band_r = int(hr * 1.06)
    band_pts = []
    for i in range(13):
        a = math.radians(214 + i * (112 / 12))
        band_pts.append((head_c[0] + math.cos(a) * band_r,
                         head_c[1] + math.sin(a) * band_r))
    pygame.draw.lines(surf, INK, False, band_pts, int(9 * s))
    pygame.draw.lines(surf, BONE, False, band_pts, int(5 * s))
    pygame.draw.lines(surf, BONE_SH, False, band_pts[:7], max(1, int(2.0 * s)))

    # FIVE opaque pale-bone crown skulls fanned across the top arc, IN FRONT of
    # the cobalt crest. WHY the centre is NOT lit: the value ladder demands a clear
    # step DOWN from the third-eye — no skull gets a near-white inlay, so the
    # third-eye stays the lone brightest point by a wide margin.
    skull_cr = hr * 1.54
    skull_r = int(hr * 0.40)
    for i in range(5):
        a = math.radians(216 + i * (108 / 4))
        sx = head_c[0] + math.cos(a) * skull_cr
        sy = head_c[1] + math.sin(a) * skull_cr
        crown_skull(surf, int(sx), int(sy), skull_r, s, lit=False, idx=i)

    # === (8) THIRD EYE — drawn LAST so NOTHING (mantle/crest/band) can occlude ==
    # the single BRIGHTEST element. WHY glow-ring -> cobalt iris -> pure-white core,
    # and bigger than the crown-centre skull's eye-pins: it must win the value
    # ladder by a WIDE gap (the two near-white-blue points never tie), seated on
    # the brow between the band apex and the sockets.
    tex, tey = head_c[0], head_c[1] - int(hr * 0.40)
    pygame.draw.circle(surf, INK, (tex, tey), max(2, int(hr * 0.40)))
    pygame.draw.circle(surf, EYE_RING, (tex, tey), max(2, int(hr * 0.36)))
    pygame.draw.circle(surf, EYE_GLOW, (tex, tey), max(2, int(hr * 0.25)))
    pygame.draw.circle(surf, EYE_CORE, (tex, tey), max(1, int(hr * 0.14)))


# ── the spine-staff → pillar mirror, built from HER own forms ─────────────────
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """The dancer's spine-staff IS the pillar: stacked vertebra beads (her torso
    rib-band motif) = the tileable shaft, each bead flanked by small CURLING
    cloth-of-flame licks (her mantle grammar) so the column reads as her own; the
    gap-edge cap is a single opaque crown-skull seated in front of a triple curled
    cobalt flame-crest (her crown in miniature). On-axis, symmetric, not top-heavy.

    `cap` names the END that faces the GAP."""
    shaft_w = int(14 * s)
    pygame.draw.rect(surf, INK, (cx - int(3 * s), top, int(6 * s), bot - top))

    bead_pitch = int(22 * s)
    cap_room = int(34 * s)
    if cap == "bottom":
        b0, b1 = top + int(8 * s), bot - cap_room
    else:
        b0, b1 = top + cap_room, bot - int(8 * s)
    y = b0
    idx = 0
    while y <= b1:
        # curling cloth-flame licks flanking each bead (drawn first → behind it),
        # curling DOWN-and-back so the shaft edge undulates like her skirt-hem
        for sgn in (-1, 1):
            mantle_sheet(surf, (cx + sgn * int(shaft_w * 0.8), y + int(2 * s)),
                         math.radians(20 if sgn > 0 else 160),
                         int(20 * s), int(13 * s), s, n=3, lit=0.1,
                         curl=0.9 * sgn, spread=0.7, fan=1.0)
        bw = shaft_w
        bead = [(cx - bw, y + int(2 * s)),
                (cx - int(bw * 0.5), y - int(7 * s)),
                (cx + int(bw * 0.5), y - int(7 * s)),
                (cx + bw, y + int(2 * s)),
                (cx + int(bw * 0.5), y + int(11 * s)),
                (cx - int(bw * 0.5), y + int(11 * s))]
        triad_blob(surf, BONE, bead,
                   core_pts=[(cx, y - int(1 * s)), (cx + bw, y + int(2 * s)),
                             (cx + int(bw * 0.5), y + int(11 * s)), (cx, y + int(9 * s))],
                   sheen_pts=[(cx - bw, y + int(2 * s)), (cx - int(bw * 0.5), y - int(6 * s)),
                              (cx - int(bw * 0.2), y - int(4 * s)), (cx - int(bw * 0.7), y + int(5 * s))],
                   ow=max(1, int(1.4 * s)))
        pygame.draw.circle(surf, BONE_DD, (cx, y + int(2 * s)), int(4 * s))
        pygame.draw.circle(surf, INK, (cx, y + int(2 * s)), int(4 * s), max(1, int(1 * s)))
        pygame.draw.line(surf, BONE_DD, (cx - int(bw * 0.5), y - int(5 * s)),
                         (cx + int(bw * 0.5), y - int(5 * s)), max(1, int(1.2 * s)))
        idx += 1
        y += bead_pitch

    # gap-edge cap: triple curled cobalt flame-lick behind a single opaque skull
    cap_y = (bot - int(20 * s)) if cap == "bottom" else (top + int(20 * s))
    grow = +1 if cap == "bottom" else -1
    crest_dir = math.radians(90) if grow > 0 else math.radians(-90)
    for off, hand in ((-int(12 * s), 1), (0, 1), (int(12 * s), -1)):
        sc = 0.8 if off else 1.0
        flame_lick(surf, cx + off, cap_y, crest_dir,
                   int(28 * s * sc), int(12 * s * sc), s, lit=0.15, curl=0.8 * hand)
    crown_skull(surf, cx, cap_y, int(13 * s), s, lit=False, idx=2)


# ── compose the review sheet ─────────────────────────────────────────────────
SS = 8


def render_creature_chip(boxw, boxh, draw_cx, draw_cy, scale, ss=SS, night=False):
    # WHY a half-step lighter cobalt at NIGHT: on the dark night sky the deep
    # field can collapse toward black at 32px; nudging the whole cobalt band up
    # keeps the mass legible AS BLUE (a cool flame robe), not a black blob.
    global COBALT_DD, COBALT_D, COBALT, COBALT_BR
    saved = (COBALT_DD, COBALT_D, COBALT, COBALT_BR)
    if night:
        COBALT_DD = lerp(COBALT_DD, ICE, 0.16)
        COBALT_D = lerp(COBALT_D, ICE, 0.14)
        COBALT = lerp(COBALT, ICE, 0.10)
        COBALT_BR = lerp(COBALT_BR, ICE, 0.08)
    big = pygame.Surface((boxw * ss, boxh * ss), pygame.SRCALPHA)
    draw_jvala(big, draw_cx * ss, draw_cy * ss, scale * ss)
    small = pygame.transform.smoothscale(big, (boxw, boxh))
    out = grow_outline(small, INK + (255,), 1)
    COBALT_DD, COBALT_D, COBALT, COBALT_BR = saved
    return out


def vgrad(surf, rect, top_col, bot_col):
    x, y, w, h = rect
    for j in range(h):
        pygame.draw.line(surf, lerp(top_col, bot_col, j / max(1, h - 1)),
                         (x, y + j), (x + w, y + j))


def render_hero_hires():
    """Standalone hi-res hero ≈1024px tall on a dark cool panel."""
    HW, HH = 820, 1024
    surf = pygame.Surface((HW, HH))
    vgrad(surf, (0, 0, HW, HH), (24, 28, 52), (40, 38, 70))
    hero = render_creature_chip(HW, HH, HW // 2 // 1, 540, 4.0)
    surf.blit(hero, (0, 0))
    font_sm = pygame.font.SysFont("DejaVu Sans", 18)
    surf.blit(font_sm.render(
        "JVALA-NIRMALA  ·  cool wisdom-flame dancer  ·  hi-res hero (SS=8)",
        True, LABEL), (24, 24))
    return surf


def blackout(surf):
    """Silhouette proof — fill every non-transparent pixel solid black."""
    out = surf.copy()
    arr = pygame.surfarray.pixels_alpha(out)
    rgb = pygame.surfarray.pixels3d(out)
    mask = arr > 24
    rgb[mask] = (12, 12, 14)
    del arr, rgb
    return out


def main():
    here = os.path.dirname(os.path.abspath(__file__))

    # ── hi-res standalone hero ────────────────────────────────────────────────
    hero_hi = render_hero_hires()
    hero_path = os.path.join(here, "round_8_hero.png")
    pygame.image.save(hero_hi, hero_path)

    # ── the standard review sheet ─────────────────────────────────────────────
    W, H = 1040, 860
    font_big = pygame.font.SysFont("DejaVu Sans", 30, bold=True)
    font = pygame.font.SysFont("DejaVu Sans", 17, bold=True)
    font_sm = pygame.font.SysFont("DejaVu Sans", 12)

    sheet = pygame.Surface((W, H))
    sheet.fill(BG)

    pygame.draw.rect(sheet, PANEL, (0, 0, W, 56))
    sheet.blit(font_big.render("#5 — JVALA-NIRMALA", True, LABEL), (24, 13))
    sheet.blit(font_sm.render(
        "cool wisdom-flame dancer  ·  CITIPATI body + Mukha 6-arm fan · FULL-BODY cobalt cloth-of-flame ROBE (curled sheeting, NOT a ring) · 6 DISTINCTLY-CONSTRUCTED frost palm-skulls · round 8",
        True, LABEL_DIM), (300, 26))

    # === (a) BIG HERO =========================================================
    hero = render_creature_chip(370, 500, 185, 268, 1.95)
    sheet.blit(hero, (14, 86))
    sheet.blit(font.render("Creature — hero", True, LABEL), (120, 596))
    sheet.blit(font_sm.render("CURLED, OVERLAPPING cloth-of-flame licks drape down the flanks/knee as a", True, LABEL_DIM), (14, 620))
    sheet.blit(font_sm.render("ROBE with an UNDULATING hem (NOT radiating spikes). 6 DISTINCTLY-built frost relics in FRONT.", True, LABEL_DIM), (14, 636))
    sheet.blit(font_sm.render("Crown: small curled flame-crest BEHIND; opaque warm-bone 5-skull arc + band", True, LABEL_DIM), (14, 652))
    sheet.blit(font_sm.render("IN FRONT. Third-eye = lone near-white ice, the only glow, by a wide margin.", True, LABEL_DIM), (14, 668))

    # === (b) PILLAR assembled — mirrored, from HER own forms ==================
    pcx = 408
    top_big = pygame.Surface((150 * SS, 250 * SS), pygame.SRCALPHA)
    draw_pillar(top_big, 75 * SS, 4 * SS, 246 * SS, 1.0 * SS, cap="bottom")
    top_seg = grow_outline(pygame.transform.smoothscale(top_big, (150, 250)), INK + (255,), 1)
    sheet.blit(top_seg, (pcx, 86))
    bot_big = pygame.Surface((150 * SS, 250 * SS), pygame.SRCALPHA)
    draw_pillar(bot_big, 75 * SS, 4 * SS, 246 * SS, 1.0 * SS, cap="top")
    bot_seg = grow_outline(pygame.transform.smoothscale(bot_big, (150, 250)), INK + (255,), 1)
    sheet.blit(bot_seg, (pcx, 86 + 250 + 96))
    pygame.draw.rect(sheet, (58, 62, 74), (pcx + 8, 86 + 250, 134, 96))
    sheet.blit(font_sm.render("GAP", True, LABEL_DIM), (pcx + 56, 86 + 250 + 40))
    sheet.blit(font.render("Pillar — spine-staff", True, LABEL), (pcx - 4, 690))
    sheet.blit(font_sm.render("vertebra beads + cobalt-flame drapes = shaft;", True, LABEL_DIM), (pcx - 4, 714))
    sheet.blit(font_sm.render("crown-skull + flame-crest caps each gap edge", True, LABEL_DIM), (pcx - 4, 730))
    sheet.blit(font_sm.render("(mirrored top<->bottom, on-axis, her own forms)", True, LABEL_DIM), (pcx - 4, 746))

    # === (c) blackout / silhouette proof ======================================
    sil_box = render_creature_chip(150, 250, 75, 132, 0.95)
    sil = blackout(sil_box)
    sbx = 568
    pygame.draw.rect(sheet, (150, 156, 168), (sbx - 4, 86 - 4, 158, 258))
    sheet.blit(sil, (sbx, 86))
    sheet.blit(font.render("Silhouette", True, LABEL), (sbx, 350))
    sheet.blit(font_sm.render("a DRAPED figure with an", True, LABEL_DIM), (sbx, 374))
    sheet.blit(font_sm.render("undulating skirt-mass —", True, LABEL_DIM), (sbx, 390))
    sheet.blit(font_sm.render("not a ring/halo blackout.", True, LABEL_DIM), (sbx, 406))

    # === (d) TRUE 32px gameplay chips on day + night sky ======================
    panel_x = 736
    pygame.draw.rect(sheet, PANEL, (panel_x, 86, W - panel_x - 14, 600))
    sheet.blit(font.render("True 32px chip", True, LABEL), (panel_x + 16, 96))

    def chip32(night=False):
        # render at ~4x then smoothscale to a TRUE 32px tile for the on-sky read
        big = render_creature_chip(32, 34, 16, 18, (32 / 150.0), night=night)
        return pygame.transform.scale(big, (120, int(34 / 32 * 120)))

    day_chip = chip32(night=False)
    night_chip = chip32(night=True)
    day_y = 128
    vgrad(sheet, (panel_x + 20, day_y, 130, 130), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, day_y, 130, 130), 1)
    sheet.blit(day_chip, (panel_x + 20 + 5, day_y + 5))
    sheet.blit(font_sm.render("32px DAY", True, LABEL), (panel_x + 20, day_y + 134))

    night_y = day_y + 168
    vgrad(sheet, (panel_x + 20, night_y, 130, 130), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, night_y, 130, 130), 1)
    sheet.blit(night_chip, (panel_x + 20 + 5, night_y + 5))
    sheet.blit(font_sm.render("32px NIGHT (cobalt +half-step)", True, LABEL_DIM), (panel_x + 20, night_y + 134))

    def pillar_chip32():
        big = pygame.Surface((44 * SS, 130 * SS), pygame.SRCALPHA)
        draw_pillar(big, 22 * SS, 2 * SS, 128 * SS, 0.32 * SS, cap="bottom")
        small = pygame.transform.smoothscale(big, (44, 130))
        return grow_outline(small, INK + (255,), 1)

    pc = pillar_chip32()
    px2 = panel_x + 162
    vgrad(sheet, (px2, day_y, 56, 130), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (px2, day_y, 56, 130), 1)
    sheet.blit(pc, (px2 + 6, day_y + 2))
    vgrad(sheet, (px2, night_y, 56, 130), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (px2, night_y, 56, 130), 1)
    sheet.blit(pc, (px2 + 6, night_y + 2))
    sheet.blit(font_sm.render("pillar", True, LABEL_DIM), (px2 + 6, day_y - 16))

    # palette strip
    sheet.blit(font.render("Pinned palette", True, LABEL), (panel_x + 16, 480))
    swatches = [
        (BONE, "pale-bone"), (BONE_DD, "bone hollow"),
        (COBALT_D, "deep cobalt"), (COBALT, "cobalt body"),
        (COBALT_BR, "fold-crest"), (ICE, "fold keyline"),
        (EYE_CORE, "third-eye core"), (INK, "ink keyline"),
    ]
    sxp, syp = panel_x + 16, 508
    for i, (c, name) in enumerate(swatches):
        col, row = i % 2, i // 2
        rx = sxp + col * 142
        ry = syp + row * 26
        pygame.draw.rect(sheet, INK, (rx - 1, ry - 1, 20, 20))
        pygame.draw.rect(sheet, c, (rx, ry, 18, 18))
        sheet.blit(font_sm.render(name, True, LABEL), (rx + 24, ry + 3))

    pygame.draw.rect(sheet, PANEL, (14, 700, W - 28, 44))
    sheet.blit(font_sm.render(
        "DISTINCTNESS: cobalt flame = a CLOTH-OF-FLAME ROBE of CURLED, OVERLAPPING licks folding back over each other (undulating hem), NOT radiating spikes — vs", True, LABEL_DIM), (26, 708))
    sheet.blit(font_sm.render(
        "vajra_rakta ring / ratna_padmini spike-halo / Citipati ember-ring.  STAY: flat fills · ink keyline (28,22,26) · triad · 1px grown outline · chibi scary-cute · procedural.",
        True, LABEL_DIM), (26, 724))

    pygame.draw.rect(sheet, PANEL, (14, 756, W - 28, 28))
    sheet.blit(font_sm.render(
        "ELEVATED pipeline: SS=8 supersample -> smoothscale.  Standalone hi-res hero exported separately: round_8_hero.png (~1024px).",
        True, LABEL_DIM), (26, 762))

    out = os.path.join(here, "round_8.png")
    pygame.image.save(sheet, out)
    print("wrote", out)
    print("wrote", hero_path)


if __name__ == "__main__":
    main()
