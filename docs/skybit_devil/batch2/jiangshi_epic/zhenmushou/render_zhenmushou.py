"""
Round-1 concept renderer for ZHENMUSHOU — the antlered sancai tomb-guardian
BEAST (Jiangshi-epic set, concept #2). Headless Pygame; supersample (SS=6) →
smoothscale, the elevated "epic" pipeline of this set (bigger render, more
geometry, richer triad, stronger glow than the Jiangshi source).

House grammar held from the lineage: chibi + scary-CUTE, flat saturated fills,
hard 1-2px ink keyline (28,22,30), dark-core -> flat-fill -> top-left rim-sheen
triad, 1px alpha-grown outline. Procedural only — no gradients/PNGs.

WHY a squat seated quadruped block: this is the ONLY beast in the lineage, so
the read must be bottom-heavy seated mass on straight forelegs — never the
upright humanoid box the rest of the set uses. The wide lion-mask face, two
upswept oxidized-red horns, and a back-fan of EXACTLY 5 triangular spine-plates
(bottom-rooted) carry the silhouette. Sancai owns a lane nobody else has:
cream-glaze base + an earned amber-glaze mid-band + a brown-OLIVE ceramic accent
(deliberately NOT leaf green, to stay clear of pine/yellow-green neighbours),
with a kiln-amber mouth glow. The pillar is the spine-spike stela: the same
triad-lit spike-plates stacked edge-on with sparse crackle-glaze banding, capped
at the gap by a smaller MIRRORED beast-mask with a glowing amber kiln-mouth —
bottom-rooted, on-axis, no top-heavy cap.

WHY standalone: review art must never enter the shipped bundle, so it lives
under docs/ and reuses only colour math, not runtime sprite modules.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
pygame.init()

# ── PINNED SANCAI PALETTE ─────────────────────────────────────────────────────
# The earned three-glaze lane: cream / amber / brown-olive. Each colour carries
# its own dark-core + rim-sheen helper so the flat triad reads on every mass.
CREAM     = (236, 220, 168)   # cream-glaze base (the dominant body mass)
CREAM_D   = (176, 154, 104)   # cream dark-core
CREAM_T   = (250, 240, 206)   # cream rim-sheen helper
AMBER     = (206, 142,  48)   # amber-glaze mid-band (earned extra band)
AMBER_D   = (150,  96,  30)   # amber dark-core
AMBER_T   = (240, 188,  92)   # amber rim-sheen helper / mouth-glow anchor
OLIVE     = ( 96,  96,  44)   # brown-OLIVE ceramic accent (NOT leaf green)
OLIVE_D   = ( 60,  62,  28)   # olive dark-core
OLIVE_T   = (140, 138,  78)   # olive rim-sheen helper
HORN      = (170,  56,  38)   # oxidized-red horn (thin LINEAR accent, never mass)
HORN_D    = (112,  34,  24)   # horn dark-core
HORN_T    = (208,  96,  66)   # horn rim-sheen
KILN      = (255, 176,  70)   # kiln-amber mouth glow (hot focal)
KILN_HOT  = (255, 226, 150)   # mouth glow hottest core
TOOTH     = (244, 236, 210)   # ivory fang / tusk
INK       = ( 28,  22,  30)   # hard ink keyline (locked)
EYE_GLOW  = (255, 198, 120)   # warm eye pinpoint

BG        = (104, 104, 104)   # neutral grey review backdrop
PANEL     = ( 84,  84,  84)
DAY_SKY   = (126, 196, 226)   # gameplay day sky
NIGHT_SKY = ( 28,  34,  62)   # gameplay night sky
LABEL     = (240, 240, 240)
LABEL_DIM = (196, 196, 196)


def face_cy_of(body_cy, s):
    # WHY a shared accessor: the back-fan must key off the same face centre the
    # head uses so the five plate-apexes always land relative to the head top.
    return body_cy - int(58*s)


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
        pygame.draw.polygon(surf, lerp(color, INK, 0.42), core_pts)
    if sheen_pts:
        pygame.draw.polygon(surf, lerp(color, (255, 255, 255), 0.35), sheen_pts)
    if outline:
        pygame.draw.polygon(surf, INK, pts, ow)


def kiln_glow(surf, cx, cy, r, s, strength=120):
    """Additive kiln-amber bloom — the hot focal that anchors the warm read on
    both day and night sky. WHY additive: keeps the glaze fills flat (no
    gradient) while still throwing real light at the mouth."""
    glow = pygame.Surface((r*4, r*4), pygame.SRCALPHA)
    for rr in range(r*2, 0, -1):
        a = int(strength * (1 - rr/(r*2)) ** 1.6)
        pygame.draw.circle(glow, (*KILN, a), (r*2, r*2), rr)
    surf.blit(glow, (cx-r*2, cy-r*2), special_flags=pygame.BLEND_ADD)


def spine_plate(surf, apex, bl, br, s, rake=0):
    """One DISCRETE triangular back-fan spine-plate — a tall narrow SPIKE, not a
    bump. Triad-lit independently so the plate count survives downscale: olive
    dark-core down the right flank, amber fill, cream rim-sheen up the left edge.
    The left edge is SERRATED with two shallow saw-notches so each plate reads as
    a ceramic spine-plate (and still telegraphs the silhouette at true 32px),
    distinct from the smooth round mane-curls. `rake` shifts the apex outward so
    the fan splays (centre upright, outer plates raked out). A thick ink-keyline
    gives every plate its own hard edge and keeps the notch between neighbours as
    visible negative space."""
    apex = (apex[0] + rake, apex[1])
    ax, ay = apex
    blx, bly = bl
    # serrate the LEFT (light) edge with two tucks so the spike reads as toothed
    h = bly - ay
    midL = (int(ax + (blx-ax)*0.5),  int(ay + h*0.5))
    s1   = (int(ax + (blx-ax)*0.33) + int(4*s), int(ay + h*0.33))
    s2   = (int(ax + (blx-ax)*0.66) + int(4*s), int(ay + h*0.66))
    left_edge = [apex, s1, midL, s2, bl]
    pts = left_edge + [br]
    # heavy keyline first so adjacent plates never visually fuse into a lump
    pygame.draw.polygon(surf, INK, pts)
    pygame.draw.polygon(surf, AMBER, pts)
    # olive dark-core down the right flank (away from the top-left light)
    pygame.draw.polygon(surf, OLIVE_D,
                        [apex, br, ((ax+br[0])//2, (ay+br[1])//2)])
    pygame.draw.polygon(surf, AMBER_D,
                        [apex, ((ax+br[0])//2, (ay+br[1])//2), br,
                         (br[0]-int(3*s), br[1])])
    # cream rim-sheen catch up the serrated left edge — the per-plate top-left
    # light, traced along the saw-notches so the teeth pick up the highlight
    pygame.draw.polygon(surf, CREAM_T,
                        [apex, s1, midL, s2, bl,
                         (blx+int(5*s), bly),
                         (midL[0]+int(5*s), midL[1]),
                         (ax+int(4*s), ay+int(8*s))])
    pygame.draw.polygon(surf, INK, pts, max(3, int(3*s)))


def crackle(surf, x0, y0, x1, y1, s):
    """A sparse hard hairline crackle-glaze seam — drawn as a thin ink triad
    groove. Kept sparse per brief so seams never fuzz the form at 1x."""
    pygame.draw.line(surf, OLIVE_D, (x0, y0), (x1, y1), max(1, int(1.5*s)))


# ── the creature ─────────────────────────────────────────────────────────────
def draw_zhenmushou(surf, cx, cy, s):
    """Squat SEATED antlered sancai beast on straight forelegs. Bottom-heavy:
    the haunch + foreleg block is the widest, lowest mass; the wide lion-mask
    face sits on top with two upswept red horns; a bottom-rooted back-fan of
    EXACTLY 5 triangular spine-plates rises behind. `s` is a unit scale around a
    ~150-unit-tall figure."""

    # ── geometry anchors (defined up front so layers can key off them) ────────
    body_w  = int(96*s)
    body_h  = int(60*s)
    body_cx = cx
    body_cy = cy + int(22*s)               # seated mass sits LOW
    haunch_y = body_cy + int(8*s)
    ground_y = body_cy + int(46*s)         # where the forelegs plant

    # ── (1) back-fan of EXACTLY 5 spine-plates (drawn FIRST → behind head) ────
    # THE signature epic read, and the whole job of this pass. Round 1+2 let this
    # collapse into a lump/row-of-curls hiding behind the skull. It is now a CROWN
    # of five DISCRETE hard-edged triangular plates that clearly OUT-RISE the head:
    # every apex clears the top of the skull, the centre plate is tallest + dead
    # upright, the inner pair steps down + rakes out, the outer pair shorter still
    # + raked further out — a true splayed fan, not sideways wings. Each plate is
    # tall + narrow (a spike, distinct from the round mane-curls) and carries its
    # own thick ink-keyline so the NOTCH between neighbours stays as visible
    # negative space — the test is being able to count 5 top-edges at 32px.
    # WHY drawn first: the plates root behind the shoulders/skull; the head + mane
    # then occlude only their lower thirds, leaving the five spike-tips proud.
    head_top   = face_cy_of(body_cy, s) - int(32*s)
    # A tight high spine line behind the skull: the five bases sit close together
    # so the fan reads as ONE crown (not sideways wings), while the apexes splay
    # into an even arc. Keeping the rake modest is what stops the outer plates
    # colliding with the horns and reading as random extra spikes.
    fan_base_y = head_top + int(8*s)                  # bases tuck behind the skull
    half_w     = int(11*s)                            # narrow base → spike, not bump
    # (centre offset of base, apex height ABOVE head_top, outward apex-rake).
    # Apex rises form a symmetric arc — centre tallest, stepping down to the
    # sides — and even the SHORTEST (outer) plate clears the horn tips so the fan
    # towers over the head as its own clean system rather than interleaving with
    # the two red horns below it. Small rakes splay the tips just enough to count
    # five edges without throwing the outer plates out sideways like wings.
    fan = [
        (-int(33*s), int(54*s), -int(14*s)),   # outer-left  (clears the horn tip)
        (-int(17*s), int(74*s), -int(7*s)),    # inner-left  (tall)
        (   0,       int(92*s),   0),          # centre      (tallest, upright)
        ( int(17*s), int(74*s),  int(7*s)),    # inner-right (tall)
        ( int(33*s), int(54*s),  int(14*s)),   # outer-right (clears the horn tip)
    ]
    for dx, apex_rise, rake in fan:
        bx = body_cx + dx
        spine_plate(surf, (bx, head_top - apex_rise),
                    (bx - half_w, fan_base_y), (bx + half_w, fan_base_y),
                    s, rake=rake)

    # ── (2) haunches + straight forelegs (the bottom-heavy base block) ────────
    # Hind haunch — a rounded cream mound either side, low and wide.
    for sgn in (-1, 1):
        hx = body_cx + sgn*int(34*s)
        haunch = [
            (hx - sgn*int(6*s), haunch_y - int(20*s)),
            (hx + sgn*int(22*s), haunch_y - int(10*s)),
            (hx + sgn*int(24*s), ground_y),
            (hx - sgn*int(14*s), ground_y),
        ]
        triad_blob(
            surf, CREAM, haunch,
            core_pts=[(hx + sgn*int(8*s), haunch_y - int(2*s)),
                      (hx + sgn*int(22*s), haunch_y - int(6*s)),
                      (hx + sgn*int(24*s), ground_y),
                      (hx + sgn*int(6*s), ground_y)],
            sheen_pts=[(hx - sgn*int(4*s), haunch_y - int(17*s)),
                       (hx + sgn*int(6*s), haunch_y - int(13*s)),
                       (hx + sgn*int(6*s), haunch_y + int(4*s)),
                       (hx - sgn*int(8*s), haunch_y + int(2*s))],
            ow=max(2, int(2.4*s)),
        )

    # straight forelegs planted at front — WIDENED into solid pillars and the
    # paws rooted with a clear ground line so the bottom-heavy mass is
    # unambiguous (the "seated on straight forelegs" tell).
    for sgn in (-1, 1):
        lx = body_cx + sgn*int(28*s)
        leg = [
            (lx - int(13*s), haunch_y + int(2*s)),
            (lx + int(13*s), haunch_y + int(2*s)),
            (lx + int(15*s), ground_y + int(22*s)),
            (lx - int(15*s), ground_y + int(22*s)),
        ]
        triad_blob(
            surf, CREAM, leg,
            core_pts=[(lx + int(3*s), haunch_y + int(2*s)),
                      (lx + int(13*s), haunch_y + int(2*s)),
                      (lx + int(15*s), ground_y + int(22*s)),
                      (lx + int(3*s), ground_y + int(22*s))],
            sheen_pts=[(lx - int(11*s), haunch_y + int(4*s)),
                       (lx - int(3*s), haunch_y + int(4*s)),
                       (lx - int(3*s), ground_y + int(18*s)),
                       (lx - int(11*s), ground_y + int(18*s))],
            ow=max(2, int(2.4*s)),
        )
        # broad clawed paw block rooted on the ground — amber-banded, wider base
        paw = [(lx - int(17*s), ground_y + int(16*s)),
               (lx + int(17*s), ground_y + int(16*s)),
               (lx + int(18*s), ground_y + int(28*s)),
               (lx - int(18*s), ground_y + int(28*s))]
        triad_blob(surf, AMBER, paw, ow=max(2, int(2.2*s)))
        # a dark ground-contact shadow line under the paw roots the mass
        pygame.draw.line(surf, INK,
                         (lx - int(18*s), ground_y + int(28*s)),
                         (lx + int(18*s), ground_y + int(28*s)), max(2, int(2.6*s)))
        # three claw splits
        for i in (-1, 0, 1):
            ncx = lx + i*int(9*s)
            pygame.draw.line(surf, INK, (ncx, ground_y + int(17*s)),
                             (ncx, ground_y + int(28*s)), max(1, int(1.8*s)))

    # ── (3) body / chest block — cream base with an EARNED amber mid-band ─────
    body = [
        (body_cx - body_w//2, body_cy - body_h//2 + int(6*s)),
        (body_cx + body_w//2, body_cy - body_h//2 + int(6*s)),
        (body_cx + body_w//2 + int(2*s), body_cy + body_h//2),
        (body_cx - body_w//2 - int(2*s), body_cy + body_h//2),
    ]
    triad_blob(
        surf, CREAM, body,
        core_pts=[(body_cx, body_cy - int(6*s)),
                  (body_cx + body_w//2, body_cy - int(10*s)),
                  (body_cx + body_w//2, body_cy + body_h//2),
                  (body_cx, body_cy + body_h//2)],
        sheen_pts=[(body_cx - body_w//2 + int(4*s), body_cy - body_h//2 + int(8*s)),
                   (body_cx - int(6*s), body_cy - body_h//2 + int(8*s)),
                   (body_cx - int(6*s), body_cy + int(2*s)),
                   (body_cx - body_w//2 + int(4*s), body_cy - int(2*s))],
        ow=max(2, int(2.6*s)),
    )
    # the earned amber-glaze mid-band across the chest (sancai's middle colour)
    band_y = body_cy - int(2*s)
    band_h = int(16*s)
    bx0 = body_cx - body_w//2 + int(3*s)
    bw  = body_w - int(6*s)
    pygame.draw.rect(surf, AMBER, (bx0, band_y, bw, band_h))
    pygame.draw.rect(surf, AMBER_D, (bx0, band_y + band_h - int(4*s), bw, int(4*s)))
    pygame.draw.rect(surf, AMBER_T, (bx0, band_y, bw, int(3*s)))
    pygame.draw.rect(surf, INK, (bx0, band_y, bw, band_h), max(1, int(1.6*s)))
    # sparse crackle-glaze seams on the chest (kept few)
    crackle(surf, body_cx - int(20*s), body_cy - int(18*s),
            body_cx - int(14*s), band_y, s)
    crackle(surf, body_cx + int(16*s), body_cy - int(20*s),
            body_cx + int(22*s), band_y, s)

    # ── (4) the WIDE lion-mask face (the dominant top read) ───────────────────
    face_cx = body_cx
    face_cy = face_cy_of(body_cy, s)
    face_w  = int(86*s)
    face_h  = int(64*s)
    face = [
        (face_cx - face_w//2, face_cy - int(10*s)),
        (face_cx - face_w//2 + int(8*s), face_cy - face_h//2),
        (face_cx + face_w//2 - int(8*s), face_cy - face_h//2),
        (face_cx + face_w//2, face_cy - int(10*s)),
        (face_cx + face_w//2 - int(6*s), face_cy + face_h//2),
        (face_cx + int(16*s), face_cy + face_h//2 + int(6*s)),
        (face_cx - int(16*s), face_cy + face_h//2 + int(6*s)),
        (face_cx - face_w//2 + int(6*s), face_cy + face_h//2),
    ]
    triad_blob(
        surf, CREAM, face,
        core_pts=[(face_cx, face_cy - int(6*s)),
                  (face_cx + face_w//2, face_cy - int(6*s)),
                  (face_cx + face_w//2 - int(6*s), face_cy + face_h//2),
                  (face_cx, face_cy + face_h//2 + int(4*s))],
        sheen_pts=[(face_cx - face_w//2 + int(6*s), face_cy - int(6*s)),
                   (face_cx - int(4*s), face_cy - face_h//2 + int(4*s)),
                   (face_cx - int(4*s), face_cy + int(6*s)),
                   (face_cx - face_w//2 + int(8*s), face_cy + int(10*s))],
        ow=max(2, int(2.8*s)),
    )

    # olive mane-curls: a tidy SYMMETRIC scallop frame hugging the face cheeks —
    # the elevated "mane curls" detail. This owns the soft round job so the
    # back-fan owns the spiky one (one spiky system, not two competing ones).
    # A column of three small round olive lobes down each cheek, mirrored L/R.
    for sgn in (-1, 1):
        mx = face_cx + sgn*int(44*s)
        for i, cy_off in enumerate((-int(14*s), int(6*s), int(24*s))):
            r = int((11 - i*1.5)*s)
            cyl = face_cy + cy_off
            pygame.draw.circle(surf, INK, (mx, cyl), r + max(2, int(2*s)))
            pygame.draw.circle(surf, OLIVE, (mx, cyl), r)
            pygame.draw.circle(surf, OLIVE_D, (mx + sgn*int(3*s), cyl + int(2*s)),
                               max(2, int(r*0.55)))
            pygame.draw.circle(surf, OLIVE_T,
                               (mx - sgn*int(3*s), cyl - int(3*s)),
                               max(1, int(r*0.4)))

    # heavy ink brow ridge (fierce-cute) over big sunken sockets
    pygame.draw.line(surf, INK,
                     (face_cx - int(30*s), face_cy - int(18*s)),
                     (face_cx - int(4*s), face_cy - int(10*s)), max(2, int(4*s)))
    pygame.draw.line(surf, INK,
                     (face_cx + int(30*s), face_cy - int(18*s)),
                     (face_cx + int(4*s), face_cy - int(10*s)), max(2, int(4*s)))

    # big round eyes — amber iris, warm pinpoint, scary-CUTE (large + bright)
    for sgn in (-1, 1):
        ex = face_cx + sgn*int(20*s)
        ey = face_cy - int(2*s)
        pygame.draw.circle(surf, INK, (ex, ey), int(13*s))
        pygame.draw.circle(surf, CREAM_T, (ex, ey), int(11*s))
        pygame.draw.circle(surf, AMBER, (ex, ey), int(9*s))
        pygame.draw.circle(surf, INK, (ex, ey), int(5*s))
        pygame.draw.circle(surf, EYE_GLOW, (ex - int(2*s), ey - int(2*s)), int(3*s))
        pygame.draw.circle(surf, (255, 255, 255),
                           (ex - int(3*s), ey - int(3*s)), max(1, int(1.4*s)))

    # broad flat snout / nose pad
    snout = [(face_cx - int(12*s), face_cy + int(10*s)),
             (face_cx + int(12*s), face_cy + int(10*s)),
             (face_cx + int(10*s), face_cy + int(22*s)),
             (face_cx - int(10*s), face_cy + int(22*s))]
    triad_blob(surf, AMBER, snout,
               core_pts=[(face_cx, face_cy + int(10*s)),
                         (face_cx + int(12*s), face_cy + int(10*s)),
                         (face_cx + int(10*s), face_cy + int(22*s)),
                         (face_cx, face_cy + int(22*s))],
               ow=max(2, int(2*s)))
    for sgn in (-1, 1):
        pygame.draw.circle(surf, INK,
                           (face_cx + sgn*int(5*s), face_cy + int(17*s)), int(3*s))

    # ── (5) the kiln-amber MOUTH GLOW (hot focal) — drawn over the lower face ─
    mouth_cy = face_cy + int(34*s)
    kiln_glow(surf, face_cx, mouth_cy, int(20*s), s, strength=150)
    mouth = [(face_cx - int(22*s), mouth_cy - int(6*s)),
             (face_cx + int(22*s), mouth_cy - int(6*s)),
             (face_cx + int(16*s), mouth_cy + int(12*s)),
             (face_cx - int(16*s), mouth_cy + int(12*s))]
    pygame.draw.polygon(surf, INK, mouth)
    pygame.draw.polygon(surf, KILN, mouth)
    pygame.draw.polygon(surf, KILN_HOT,
                        [(face_cx - int(14*s), mouth_cy - int(2*s)),
                         (face_cx + int(14*s), mouth_cy - int(2*s)),
                         (face_cx + int(9*s), mouth_cy + int(7*s)),
                         (face_cx - int(9*s), mouth_cy + int(7*s))])
    pygame.draw.polygon(surf, INK, mouth, max(2, int(2*s)))
    # ivory fangs over the glow (top + bottom rows, scary-cute)
    for i in (-1, 1):
        fx = face_cx + i*int(13*s)
        pygame.draw.polygon(surf, TOOTH,
                            [(fx - int(4*s), mouth_cy - int(6*s)),
                             (fx + int(4*s), mouth_cy - int(6*s)),
                             (fx, mouth_cy + int(4*s))])
        pygame.draw.polygon(surf, INK,
                            [(fx - int(4*s), mouth_cy - int(6*s)),
                             (fx + int(4*s), mouth_cy - int(6*s)),
                             (fx, mouth_cy + int(4*s))], max(1, int(1.4*s)))
    # tusks curling up at the corners
    for sgn in (-1, 1):
        tx = face_cx + sgn*int(20*s)
        pygame.draw.polygon(surf, TOOTH,
                            [(tx, mouth_cy - int(4*s)),
                             (tx + sgn*int(6*s), mouth_cy - int(14*s)),
                             (tx + sgn*int(2*s), mouth_cy - int(2*s))])
        pygame.draw.polygon(surf, INK,
                            [(tx, mouth_cy - int(4*s)),
                             (tx + sgn*int(6*s), mouth_cy - int(14*s)),
                             (tx + sgn*int(2*s), mouth_cy - int(2*s))], max(1, int(1.4*s)))

    # ── (6) two upswept oxidized-red HORNS — THICK at the base (~50% wider than
    # round 1) so they survive 32px, still a thin LINEAR cinnabar accent (width,
    # not extra saturated area). Two firm tapered prongs with a single ridge
    # groove + a top-left rim-sheen so they read even against the night sky. ──
    for sgn in (-1, 1):
        rx = face_cx + sgn*int(22*s)
        ry = face_cy - int(28*s)
        # widened base (root ~16 units across) tapering to a still-pointed tip
        horn = [
            (rx - sgn*int(8*s), ry + int(8*s)),     # outer base corner
            (rx + sgn*int(8*s), ry + int(4*s)),     # inner base corner
            (rx + sgn*int(20*s), ry - int(26*s)),   # inner mid
            (rx + sgn*int(30*s), ry - int(54*s)),   # tip
            (rx + sgn*int(20*s), ry - int(52*s)),   # tip back
            (rx + sgn*int(10*s), ry - int(24*s)),   # outer mid
            (rx - sgn*int(8*s), ry - int(2*s)),     # outer base
        ]
        triad_blob(
            surf, HORN, horn,
            core_pts=[(rx + sgn*int(6*s), ry + int(2*s)),
                      (rx + sgn*int(20*s), ry - int(26*s)),
                      (rx + sgn*int(30*s), ry - int(54*s)),
                      (rx + sgn*int(24*s), ry - int(52*s)),
                      (rx + sgn*int(14*s), ry - int(24*s))],
            ow=max(2, int(2.6*s)),
        )
        # single ridge groove up the spine of the horn (the "horn ridges" detail)
        pygame.draw.line(surf, HORN_D,
                         (rx + sgn*int(4*s), ry),
                         (rx + sgn*int(24*s), ry - int(48*s)), max(2, int(2.4*s)))
        # bright top-left rim-sheen on the front edge — rescues the horn at night
        pygame.draw.line(surf, HORN_T,
                         (rx - sgn*int(4*s), ry + int(2*s)),
                         (rx + sgn*int(18*s), ry - int(46*s)), max(2, int(2.6*s)))


# ── the spine-spike stela pillar (creature-derived; clean tileable shaft) ─────
def draw_pillar_segment(surf, cx, top, bot, s, cap_at=None):
    """Spine-spike stela — BOTTOM-ROOTED. The shaft is a column of the hero's
    back-fan spike-plates stacked edge-on, every plate UPSWEPT (apex pointing
    UP/away from the rooted end) and the WIDEST plates clustered at the rooted
    base, tapering as they climb — so the eye reads upward growth and grounded
    mass, never the descending-arrow pile the round-1 column made. Sparse
    hairline crackle-glaze seams band the shaft (2-3 per plate, hard 1px). The
    `cap_at` end carries the smaller mirrored beast-mask at the gap; the OTHER
    end is the root, where the mass is widest.

    `cap_at == "bottom"`  → mask at the bottom edge (this segment hangs from the
                            ceiling: root is at the TOP, plates upswept toward it).
    `cap_at == "top"`     → mask at the top edge (this segment grows from the
                            floor: root is at the BOTTOM, plates upswept away)."""
    # Root end is widest so the stela reads bottom-rooted in MASS, not just in
    # plate direction (round-2 note #2): the shaft is a slight trapezoid, wide at
    # the root, tapering toward the capped gap end.
    root_at_top_shaft = (cap_at == "bottom")
    wide = int(40*s)                                  # shaft width at the root
    narrow = int(28*s)                                # shaft width at the gap
    if root_at_top_shaft:
        wtop, wbot = wide, narrow
    else:
        wtop, wbot = narrow, wide
    shaft_w = max(wtop, wbot)
    shaft = [(cx - wtop//2, top), (cx + wtop//2, top),
             (cx + wbot//2, bot), (cx - wbot//2, bot)]
    # core cream shaft with an olive shade flank + cream rim-sheen flank (triad)
    pygame.draw.polygon(surf, INK, shaft)
    pygame.draw.polygon(surf, CREAM, shaft)
    pygame.draw.polygon(surf, OLIVE_D,
                        [(cx + wtop//2 - int(8*s), top), (cx + wtop//2, top),
                         (cx + wbot//2, bot), (cx + wbot//2 - int(8*s), bot)])
    pygame.draw.polygon(surf, CREAM_T,
                        [(cx - wtop//2, top), (cx - wtop//2 + int(6*s), top),
                         (cx - wbot//2 + int(6*s), bot), (cx - wbot//2, bot)])

    # Which end is the ROOT (widest, grounded) vs the GAP (capped, tapered)?
    # Plates always sweep UP-AND-OUT away from the root: apex toward the root,
    # base toward the gap — so following the shaft from gap to root, mass grows.
    root_at_top = (cap_at == "bottom")          # cap at bottom → root at top
    span = bot - top
    pitch = int(28*s)
    n = max(1, (span - int(20*s)) // pitch)
    band_toggle = 0
    for i in range(n):
        # frac: 0 at the ROOT end, 1 at the GAP end — plates widen toward root
        frac = i / max(1, n - 1)                 # 0 at the root end, 1 at the gap
        if root_at_top:
            band_y = top + int(12*s) + i*pitch
            up = +1                              # apex points UP toward the ceiling root
        else:
            band_y = bot - int(12*s) - i*pitch
            up = +1                              # apex points UP toward the floor root
        # widest plate at the root, tapering toward the gap
        half = int((22 - 9*frac) * s)
        height = int((24 - 8*frac) * s)
        base_y = band_y
        apex = (cx, base_y - up*height)
        a = (cx - half, base_y)
        b = (cx + half, base_y)
        pts = [apex, b, a]
        col   = AMBER if band_toggle % 2 == 0 else CREAM
        col_d = AMBER_D if band_toggle % 2 == 0 else CREAM_D
        col_t = AMBER_T if band_toggle % 2 == 0 else CREAM_T
        pygame.draw.polygon(surf, INK, pts)
        pygame.draw.polygon(surf, col, pts)
        # dark-core right flank
        pygame.draw.polygon(surf, col_d, [apex, b, ((apex[0]+b[0])//2, (apex[1]+b[1])//2)])
        # olive ridge groove up the spine of the plate
        pygame.draw.line(surf, OLIVE_D, apex, (cx, base_y), max(1, int(1.8*s)))
        # cream rim-sheen left edge
        pygame.draw.polygon(surf, col_t,
                            [apex, a, (a[0]+int(5*s), a[1]),
                             (apex[0]-int(3*s), apex[1]+up*int(5*s))])
        pygame.draw.polygon(surf, INK, pts, max(2, int(2.4*s)))
        # sparse hairline crackle-glaze seams — 2-3 per plate, irregular, hard 1px
        crackle(surf, cx - int(11*s), base_y - up*int(3*s),
                cx - int(5*s), base_y - up*int(11*s), s)
        if band_toggle % 2 == 0:
            crackle(surf, cx + int(9*s), base_y - up*int(2*s),
                    cx + int(4*s), base_y - up*int(9*s), s)
        band_toggle += 1

    # ── the mirrored beast-mask gap-cap (smaller; glowing amber kiln-mouth) ───
    if cap_at:
        my = bot - int(26*s) if cap_at == "bottom" else top + int(26*s)
        flip = 1 if cap_at == "bottom" else -1   # mirror about the mask centre
        mw, mh = int(56*s), int(40*s)
        mask = [
            (cx - mw//2, my - flip*int(8*s)),
            (cx - mw//2 + int(6*s), my - flip*mh//2),
            (cx + mw//2 - int(6*s), my - flip*mh//2),
            (cx + mw//2, my - flip*int(8*s)),
            (cx + mw//2 - int(4*s), my + flip*mh//2),
            (cx, my + flip*(mh//2 + int(4*s))),
            (cx - mw//2 + int(4*s), my + flip*mh//2),
        ]
        triad_blob(
            surf, CREAM, mask,
            core_pts=[(cx, my), (cx + mw//2, my - flip*int(4*s)),
                      (cx + mw//2 - int(4*s), my + flip*mh//2),
                      (cx, my + flip*(mh//2 + int(2*s)))],
            ow=max(2, int(2.4*s)),
        )
        # two thick upswept red horns on the cap (echo the thickened hero horns)
        for sgn in (-1, 1):
            hx = cx + sgn*int(15*s)
            hy = my - flip*int(15*s)
            chorn = [(hx - sgn*int(6*s), hy),
                     (hx + sgn*int(6*s), hy - flip*int(2*s)),
                     (hx + sgn*int(16*s), hy - flip*int(24*s)),
                     (hx + sgn*int(9*s), hy - flip*int(23*s)),
                     (hx - sgn*int(4*s), hy - flip*int(2*s))]
            pygame.draw.polygon(surf, INK, chorn)
            pygame.draw.polygon(surf, HORN, chorn)
            pygame.draw.line(surf, HORN_T, (hx - sgn*int(2*s), hy),
                             (hx + sgn*int(13*s), hy - flip*int(20*s)),
                             max(1, int(2*s)))
        # two eyes
        for sgn in (-1, 1):
            ex = cx + sgn*int(13*s)
            ey = my - flip*int(2*s)
            pygame.draw.circle(surf, INK, (ex, ey), int(7*s))
            pygame.draw.circle(surf, AMBER, (ex, ey), int(5*s))
            pygame.draw.circle(surf, EYE_GLOW, (ex - int(1*s), ey - int(1*s)), int(2*s))
        # the glowing amber kiln-mouth at the gap edge
        gy = my + flip*int(16*s)
        kiln_glow(surf, cx, gy, int(15*s), s, strength=150)
        mo = [(cx - int(15*s), gy - flip*int(4*s)),
              (cx + int(15*s), gy - flip*int(4*s)),
              (cx + int(10*s), gy + flip*int(9*s)),
              (cx - int(10*s), gy + flip*int(9*s))]
        pygame.draw.polygon(surf, INK, mo)
        pygame.draw.polygon(surf, KILN, mo)
        pygame.draw.polygon(surf, KILN_HOT,
                            [(cx - int(9*s), gy - flip*int(1*s)),
                             (cx + int(9*s), gy - flip*int(1*s)),
                             (cx, gy + flip*int(6*s))])
        pygame.draw.polygon(surf, INK, mo, max(1, int(1.6*s)))
        for i in (-1, 1):
            fx = cx + i*int(8*s)
            pygame.draw.polygon(surf, TOOTH,
                                [(fx - int(3*s), gy - flip*int(4*s)),
                                 (fx + int(3*s), gy - flip*int(4*s)),
                                 (fx, gy + flip*int(3*s))])


# ── compose the review sheet ─────────────────────────────────────────────────
SS = 6


def render_creature(boxw, boxh, draw_cx, draw_cy, scale):
    big = pygame.Surface((boxw*SS, boxh*SS), pygame.SRCALPHA)
    draw_zhenmushou(big, draw_cx*SS, draw_cy*SS, scale*SS)
    small = pygame.transform.smoothscale(big, (boxw, boxh))
    return grow_outline(small, INK + (255,), 1)


def render_pillar(boxw, boxh, top, bot, scale, cap_at):
    big = pygame.Surface((boxw*SS, boxh*SS), pygame.SRCALPHA)
    draw_pillar_segment(big, (boxw//2)*SS, top*SS, bot*SS, scale*SS, cap_at=cap_at)
    small = pygame.transform.smoothscale(big, (boxw, boxh))
    return grow_outline(small, INK + (255,), 1)


def main():
    W, H = 1000, 860
    font_big = pygame.font.SysFont("DejaVu Sans", 30, bold=True)
    font = pygame.font.SysFont("DejaVu Sans", 17, bold=True)
    font_sm = pygame.font.SysFont("DejaVu Sans", 12)

    sheet = pygame.Surface((W, H))
    sheet.fill(BG)

    pygame.draw.rect(sheet, PANEL, (0, 0, W, 56))
    sheet.blit(font_big.render("ZHENMUSHOU", True, LABEL), (24, 12))
    sheet.blit(font_sm.render(
        "antlered sancai tomb-guardian beast  ·  cream + amber + brown-olive + oxidized-red horns + kiln-amber mouth  ·  round 3",
        True, LABEL_DIM), (250, 24))

    # ── (a) BIG hero sprite ───────────────────────────────────────────────────
    hero = render_creature(360, 470, 180, 215, 1.55)
    sheet.blit(hero, (12, 78))
    sheet.blit(font.render("Hero — seated antlered beast", True, LABEL), (60, 548))
    sheet.blit(font_sm.render("bottom-heavy seated mass on straight forelegs; wide lion-mask;", True, LABEL_DIM), (16, 572))
    sheet.blit(font_sm.render("2 upswept red horns; back-fan of EXACTLY 5 spine-plates", True, LABEL_DIM), (16, 588))

    # ── (b) pillar assembled — top + gap + bottom, MIRRORED ───────────────────
    px = 392
    pygame.draw.rect(sheet, PANEL, (px, 78, 196, 700))
    sheet.blit(font.render("Pillar — mirrored", True, LABEL), (px+14, 86))
    pcx = px + 98
    # top segment: cap faces DOWN into the gap (so its mouth glows at the gap)
    top_seg = render_pillar(160, 250, 4, 246, 1.0, cap_at="bottom")
    sheet.blit(top_seg, (pcx - 80, 114))
    # gap
    gap_top = 114 + 250
    gap_h = 96
    # bottom segment: MIRRORED — cap faces UP into the gap
    bot_seg = render_pillar(160, 300, 4, 296, 1.0, cap_at="top")
    sheet.blit(bot_seg, (pcx - 80, gap_top + gap_h))
    sheet.blit(font_sm.render("stacked spike-plate shaft +", True, LABEL_DIM), (px+10, 760))
    sheet.blit(font_sm.render("mirrored beast-mask gap-caps", True, LABEL_DIM), (px+10, 776))

    # ── (c) TRUE 32px gameplay chips on day + night sky ───────────────────────
    rx = 612
    pygame.draw.rect(sheet, PANEL, (rx, 78, 376, 360))
    sheet.blit(font.render("32px gameplay chip", True, LABEL), (rx+16, 86))
    sheet.blit(font_sm.render("true gameplay scale — does the seated beast read?", True, LABEL_DIM), (rx+16, 110))

    # day
    chip_day = render_creature(64, 84, 32, 40, (32/170.0))
    pygame.draw.rect(sheet, DAY_SKY, (rx+40, 140, 160, 200))
    sheet.blit(chip_day, (rx+40 + 48, 196))
    # show a 32px pillar gap-cap chip beside it on day
    pchip_day = render_pillar(40, 130, 2, 128, (32/100.0), cap_at="bottom")
    sheet.blit(pchip_day, (rx+40 + 110, 170))
    sheet.blit(font_sm.render("DAY", True, LABEL), (rx+40 + 70, 344))

    # night
    chip_night = render_creature(64, 84, 32, 40, (32/170.0))
    pygame.draw.rect(sheet, NIGHT_SKY, (rx+220, 140, 140, 200))
    sheet.blit(chip_night, (rx+220 + 40, 196))
    pchip_night = render_pillar(40, 130, 2, 128, (32/100.0), cap_at="bottom")
    sheet.blit(pchip_night, (rx+220 + 96, 170))
    sheet.blit(font_sm.render("NIGHT", True, LABEL), (rx+220 + 56, 344))

    # ── palette swatch row ────────────────────────────────────────────────────
    pygame.draw.rect(sheet, PANEL, (rx, 452, 376, 326))
    sheet.blit(font.render("Pinned sancai palette", True, LABEL), (rx+16, 460))
    swatches = [
        (CREAM, "cream-glaze base"), (CREAM_D, "cream dark-core"),
        (AMBER, "amber mid-band"), (AMBER_D, "amber dark-core"),
        (OLIVE, "brown-olive accent"), (OLIVE_D, "olive dark-core"),
        (HORN, "oxidized-red horn"), (HORN_T, "horn rim-sheen"),
        (KILN, "kiln-amber glow"), (KILN_HOT, "kiln hot-core"),
        (TOOTH, "ivory fang"), (INK, "ink keyline"),
    ]
    sx, sy = rx+16, 494
    for i, (c, name) in enumerate(swatches):
        col = i % 2
        row = i // 2
        bx = sx + col*180
        by = sy + row*44
        pygame.draw.rect(sheet, INK, (bx-1, by-1, 26, 26))
        pygame.draw.rect(sheet, c, (bx, by, 24, 24))
        sheet.blit(font_sm.render(name, True, LABEL), (bx+32, by+1))
        sheet.blit(font_sm.render("%d,%d,%d" % c, True, LABEL_DIM), (bx+32, by+14))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_3.png")
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
