"""Look-dev mockup: Skybit endgame boss — "THE HOLLOW" (Death take #8).

WHY: the seed reaper shipped off-style (desaturated void-violet, soft shading,
feathered smoke, no keyline, grim-realist). This take re-cuts the canonical
hooded-cloak FACELESS Death into Skybit's CHIBI HOUSE STYLE: big hood, short
wide round-shouldered body, FLAT saturated fills, hard ~(28,22,30) ink keylines,
the dark-core -> fill -> top-left sheen triad on the cloak, a HARD scalloped hem
(crisp lobes, zero feathering), and a 1px post-pass silhouette outline.

The deliberate divergence from the seed: where the seed dissolved into a soft
smoke blur and a soft-gradient void, THE HOLLOW ends in a hard chibi scalloped
hem and the hood interior is a FLAT-BLACK field with crisp STAR PIXELS plus two
faint cyan pinprick "almost-eyes" — eerie, not a transparency dropout. The
palette is bold saturated cosmic (midnight-indigo + electric-cyan + soul-pink),
NOT a desaturated grim blur, so it pops scary-cute on a dark night sky.

Signature prop = the SNUFFER-CANDLE POLE: a tall banded pole capped by a
bell-shaped candle-snuffer cone with a tiny soul-flame peeking under its rim.
The pole is the pillar body (top cap + repeatable mid band); the snuffer-bell +
flame ride the GAP-EDGE as a flourish, proving the prop->pillar mirror.

Nothing under game/ is touched; we import the real colour kit only. Headless +
deterministic.  Output: docs/skybit_reaper/the_hollow/round_2.png

    SDL_VIDEODRIVER=dummy python tools/render_skybit_reaper_the_hollow.py
"""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from game.draw import _shade_c, lerp_color, blit_glow  # real game helpers

pygame.init()


# ── THE HOLLOW palette ("midnight & starfire") ───────────────────────────────
# Saturated cosmic, NOT the seed's desaturated void-violet. The shroud is a deep
# midnight-indigo with REAL chroma; the rim sheen is a clearly violet rim (not
# grey); stars are electric-cyan + white; the soul-flame is soul-pink. Bone trim
# + brass collar keep warm punctuation so the figure never goes monochrome.
INK         = (28, 22, 30)        # the house keyline / silhouette outline
# WHY: r1 lost the lower bell to the night-sky gradient (which climbs toward
# (35,55,115)) — the fill sat only a hair above it. The shroud is lifted ~18% in
# value AND pushed cooler/more saturated so the midnight mass clears dark sky on
# its own, with the triad now stepping in three clearly separated values.
SHROUD      = (58, 49, 100)       # robe fill — the dominant midnight-indigo mass
SHROUD_DK   = (28, 23, 56)        # dark-core ring / fold valley (triad floor)
SHROUD_HI   = (110, 96, 170)      # top-left rim sheen (the bright violet, triad top)
# A thin cooler-violet halo rim traced JUST inside the silhouette so the lower
# bell separates from the night gradient without leaning on the 1px ink outline.
SHROUD_RIM  = (132, 120, 205)     # interior cool-violet separation rim
VOID        = (10, 8, 20)         # the FLAT-black hood cavity (not a gradient)
VOID_RIM    = (74, 62, 124)       # a thin violet cloth rim shaping the cowl mouth
STAR_CYAN   = (127, 232, 255)     # electric-cyan star pixels + the pinprick eyes
STAR_WHITE  = (255, 255, 255)     # the brightest hard star pixels
BONE        = (240, 230, 206)     # hem trim + snuffer-pole highlight
BONE_DK     = (176, 162, 132)     # bone underside / pole shade
BRASS       = (200, 144, 46)      # collar clasp / ferrule banding
BRASS_HI    = (255, 224, 150)
FLAME_PINK  = (255, 79, 168)      # soul-flame core (the soul-pink glow)
FLAME_HOT   = (255, 196, 230)     # flame hot centre


def _triad_poly(surf, pts, col, ss, *, sheen_inset=0.34, rim=True):
    """A FLAT-fill polygon dressed with the house triad: a dark-core keyline ring
    (no soft edge), the flat colour fill, then a top-left rim-sheen drawn as a
    WIDE lighter band along the upper-left edges. No within-shape gradient — the
    form reads from three hard value steps, never a blur. `rim` traces a thin
    cool-violet separation halo just inside the WHOLE silhouette so the mass clears
    the night-sky gradient without leaning on the 1px ink outline."""
    ipts = [(int(p[0]), int(p[1])) for p in pts]
    pygame.draw.polygon(surf, _shade_c(col, -55), ipts)
    pygame.draw.polygon(surf, col, ipts)
    # Interior cool-violet separation rim — drawn FIRST so the heavier ink keyline
    # and the sheen overprint it; on dark sky this thin bright edge is what lifts
    # the bell off the gradient even where the outline is hairline-thin.
    if rim:
        pygame.draw.polygon(surf, SHROUD_RIM, ipts, max(1, int(2 * ss)))
    pygame.draw.polygon(surf, INK, ipts, max(1, int(2 * ss)))
    # Top-left sheen: a WIDE lighter band a few px in along the upper-left edges,
    # so the cloak catches a clearly readable third value from the canonical
    # top-left light without any within-shape gradient.
    n = len(pts)
    inset = []
    cxg = sum(p[0] for p in pts) / n
    cyg = sum(p[1] for p in pts) / n
    for p in pts:
        dx, dy = cxg - p[0], cyg - p[1]
        d = math.hypot(dx, dy) or 1.0
        # only pull the upper-left arc inward; lower-right edges stay on the keyline
        if (p[0] <= cxg) or (p[1] <= cyg):
            inset.append((p[0] + dx / d * sheen_inset * 8 * ss,
                          p[1] + dy / d * sheen_inset * 8 * ss))
        else:
            inset.append(p)
    upper_left = [pp for pp, src in zip(inset, pts)
                  if src[0] <= cxg or src[1] <= cyg]
    if len(upper_left) >= 2:
        # A fat sheen band (the third triad step) — was a thin hairline in r1.
        pygame.draw.lines(surf, SHROUD_HI, False,
                          [(int(p[0]), int(p[1])) for p in upper_left],
                          max(2, int(4 * ss)))


def _scallop_hem(surf, cx, hem_y, half_w, ss, col, *, lobes=7):
    """A HARD chibi scalloped hem: a row of crisp downward lobes (semicircles)
    along the robe base, each ink-keyed, with a bone trim band riding the top of
    the scallops. Zero feathering — flat lobes, the deliberate divergence from
    the seed's smoke dissolve. Returns the lowest hem y so the figure footprint
    is known."""
    span = half_w * 2
    lobe_w = span / lobes
    r = int(lobe_w * 0.5)
    lowest = hem_y
    for i in range(lobes):
        lx = int(cx - half_w + lobe_w * (i + 0.5))
        ly = int(hem_y)
        # dark-core ring then flat fill then top-left sheen pip — the triad, hard.
        pygame.draw.circle(surf, _shade_c(col, -55), (lx, ly), r)
        pygame.draw.circle(surf, col, (lx, ly), max(2, r - int(ss)))
        pygame.draw.circle(surf, SHROUD_HI,
                           (int(lx - r * 0.34), int(ly - r * 0.34)),
                           max(1, int(r * 0.34)))
        # A thin cool-violet rim on each lobe so the bottom edge of the bell
        # separates from the night gradient even where the ink outline is thin.
        pygame.draw.circle(surf, SHROUD_RIM, (lx, ly), r, max(1, int(1.4 * ss)))
        pygame.draw.circle(surf, INK, (lx, ly), r, max(2, int(2 * ss)))
        lowest = max(lowest, ly + r)
    # A bone trim band sitting along the scallop tops so the hem reads finished.
    pygame.draw.line(surf, BONE_DK, (int(cx - half_w), int(hem_y - r * 0.2)),
                     (int(cx + half_w), int(hem_y - r * 0.2)), max(2, int(2.4 * ss)))
    pygame.draw.line(surf, BONE, (int(cx - half_w), int(hem_y - r * 0.55)),
                     (int(cx + half_w), int(hem_y - r * 0.55)), max(1, int(1.6 * ss)))
    return lowest


def _hood_void(surf, cx, cav_cy, cav_w, cav_h, ss, *, eye_dx, blink=False):
    """The hood interior: a FLAT-black cavity (no gradient) carrying crisp white +
    cyan STAR PIXELS and two faint cyan pinprick "almost-eyes". These eyes are
    load-bearing per the cull guardrail — without them the void is a dead hole, so
    they get a tiny additive glow to read at 1x while the star field keeps it
    cosmic rather than a face. `eye_dx` shifts the gaze; `blink` halves the eyes."""
    cav = pygame.Rect(0, 0, int(cav_w), int(cav_h))
    cav.center = (int(cx), int(cav_cy))
    # FLAT-black field — a single ellipse fill, deliberately NO radial gradient.
    pygame.draw.ellipse(surf, VOID, cav)
    pygame.draw.ellipse(surf, INK, cav, max(1, int(2 * ss)))
    # A thin violet cloth rim along the upper brow shapes the cowl mouth without
    # lighting the void (matches the seed's intent, kept HARD not feathered).
    pygame.draw.arc(surf, VOID_RIM, cav.inflate(int(3 * ss), int(3 * ss)),
                    math.radians(28), math.radians(152), max(1, int(1.8 * ss)))
    # Hard star PIXELS scattered in the void — a deterministic layout so the eerie
    # starlight reads as crisp dots, not noise. A couple are cyan, the rest white.
    stars = ((-0.34, -0.18, 1, STAR_WHITE), (0.30, -0.30, 1, STAR_CYAN),
             (0.10, 0.34, 1, STAR_WHITE), (-0.22, 0.40, 1, STAR_CYAN),
             (0.40, 0.10, 1, STAR_WHITE), (-0.05, -0.42, 2, STAR_WHITE))
    for fx, fy, sz, col in stars:
        sx = int(cx + fx * cav_w * 0.5)
        sy = int(cav_cy + fy * cav_h * 0.5)
        pygame.draw.circle(surf, col, (sx, sy), max(1, int(sz * ss)))
    # Two faint cyan pinprick "almost-eyes" deep in the field — a soft additive
    # glow so they read at 1x, then a hard crisp core pixel on top.
    er = max(1, int(1.6 * ss))
    eh = 0.5 if blink else 1.0
    for s in (-1, 1):
        ex = int(cx + s * cav_w * 0.20 + eye_dx)
        ey = int(cav_cy + cav_h * 0.06)
        blit_glow(surf, ex, ey, max(2, int(4 * ss)), STAR_CYAN, alpha=150)
        pygame.draw.circle(surf, STAR_CYAN, (ex, int(ey)),
                           max(1, int(er * eh)))
        pygame.draw.circle(surf, STAR_WHITE, (ex, int(ey)),
                           max(1, int(er * 0.5 * eh)))


def draw_hollow(surf, cx, feet_y, scale=1.0, ss=1, *, eye_dx=0.0, blink=False):
    """THE HOLLOW chibi void-shroud, built on its own geometry, all keyed off `H`.

    Chibi build: a BIG hood arch sitting LOW, round shoulders sloping into a
    SHORT, WIDER-THAN-TALL bell robe, a hard scalloped lobe hem, two stub
    sleeve-arms gripping the snuffer-pole. A clear weight-shift (the whole bell
    + hood lean toward the prop, one shoulder dropped) gives the playful
    presenting stance; the void inside the hood is flat-black with star pixels +
    pinprick eyes (scary-cute)."""
    # WHY r2: r1 read "tall generic reaper" (H=190/W=150). Drop H and fatten W so
    # the silhouette is an unmistakable WIDER-THAN-TALL chibi bell with a low
    # centre of gravity, distinct from the other roster takes.
    H = int(160 * scale * ss)
    W = int(184 * scale * ss)
    top_y = feet_y - H

    # — Short wide bell robe: a squat chibi trapezoid flaring to a hem WIDER than
    #   the figure is tall, narrow at the round shoulders. The big-hood mass starts
    #   low so the whole centre of gravity sits in the bottom third.
    shoulder_y = top_y + int(H * 0.46)        # shoulders dropped low -> big hood
    hem_y = feet_y - int(H * 0.13)
    sh_half = int(W * 0.30)         # narrow round shoulders
    hem_half = int(W * 0.52)        # very wide bell hem (low centre of gravity)
    # A real weight-shift: the bell leans toward the held prop so it presents,
    # rather than standing as a stiff symmetric T.
    lean = int(W * 0.06)
    # Asymmetric hem — the prop-side skirt kicks out wider so the pose reads as a
    # cocked-hip lean, not a mirror trapezoid.
    body = [
        (cx - sh_half + lean, shoulder_y),
        (cx - hem_half + int(lean * 0.4), hem_y),
        (cx + hem_half + int(lean * 1.5), hem_y),
        (cx + sh_half + lean, shoulder_y),
    ]
    _triad_poly(surf, body, SHROUD, ss)

    # Round shoulders: two dark cloth lobes pulled up to the hood so the chibi
    # silhouette reads round-shouldered and broad, not a flat cone. The figure's
    # left (s<0) shoulder drops noticeably for the presenting weight-shift.
    for s in (-1, 1):
        drop = int(H * 0.06) if s < 0 else 0      # dropped shoulder = the lean
        sh = [
            (cx + lean, shoulder_y - int(H * 0.05) + drop),
            (cx + s * int(W * 0.40) + lean, shoulder_y + int(H * 0.04) + drop),
            (cx + s * int(W * 0.32) + lean, shoulder_y + int(H * 0.18)),
            (cx + lean, shoulder_y + int(H * 0.08)),
        ]
        _triad_poly(surf, sh, SHROUD, ss, sheen_inset=0.5)

    # Two long vertical drape folds — hard dark grooves (no gradient), so the bell
    # reads as cloth without lifting value.
    for fx in (-0.42, 0.20):
        x0 = cx + int(fx * hem_half) + lean
        x1 = cx + int(fx * hem_half * 1.25) + lean
        pygame.draw.line(surf, SHROUD_DK, (x0, shoulder_y + int(H * 0.10)),
                         (x1, hem_y - int(2 * ss)), max(1, int(2 * ss)))

    # — Brass collar clasp where the hood meets the shoulders (warm punctuation).
    clasp_y = shoulder_y - int(H * 0.01)
    pygame.draw.line(surf, _shade_c(BRASS, -50),
                     (cx - sh_half * 0.7 + lean, clasp_y),
                     (cx + sh_half * 0.7 + lean, clasp_y), max(3, int(4 * ss)))
    pygame.draw.line(surf, BRASS,
                     (cx - sh_half * 0.7 + lean, clasp_y - int(ss)),
                     (cx + sh_half * 0.7 + lean, clasp_y - int(ss)), max(1, int(2 * ss)))
    pygame.draw.circle(surf, BRASS, (int(cx + lean), int(clasp_y)), max(2, int(3.4 * ss)))
    pygame.draw.circle(surf, BRASS_HI,
                       (int(cx + lean - ss), int(clasp_y - ss)), max(1, int(1.4 * ss)))

    # — The BIG HOOD: a broad teardrop cowl leaning clearly toward the held pole,
    #   the archetypal Death silhouette done chibi-round and OVERSIZED so it caps
    #   the squat body. Built as a flat triad mass with a deep cavity for the void.
    hood_peak_y = top_y - int(H * 0.02)
    hlean = int(W * 0.10)            # exaggerated cowl lean toward the prop side
    hood = [
        (cx - int(W * 0.34), shoulder_y - int(H * 0.02)),     # left jaw, broad
        (cx - int(W * 0.33), top_y + int(H * 0.16)),
        (cx - int(W * 0.12) + hlean, hood_peak_y),            # rounded peak
        (cx + int(W * 0.14) + hlean, hood_peak_y + int(H * 0.01)),
        (cx + int(W * 0.35) + hlean, top_y + int(H * 0.16)),
        (cx + int(W * 0.37) + hlean, shoulder_y - int(H * 0.02)),  # right jaw
        (cx + int(W * 0.20) + hlean, shoulder_y + int(H * 0.03)),  # chin scoop
        (cx - int(W * 0.20), shoulder_y + int(H * 0.03)),
    ]
    _triad_poly(surf, hood, SHROUD, ss)

    # The faceless void cavity, set under the cowl brow with star pixels + eyes.
    cav_cx = cx + hlean
    cav_cy = top_y + int(H * 0.22)
    _hood_void(surf, cav_cx, cav_cy, int(W * 0.34), int(H * 0.28), ss,
               eye_dx=eye_dx * ss, blink=blink)

    # — The hard scalloped hem along the robe base (the signature divergence).
    _scallop_hem(surf, cx + lean, hem_y, hem_half, ss, SHROUD, lobes=7)

    # — Two stub sleeve-arms reaching to grip the snuffer-pole on the figure's
    #   right. Chibi stubs (rounded capsules), not anatomical arms.
    pole_x = cx + int(W * 0.46) + lean
    grip_hi = shoulder_y + int(H * 0.04)
    grip_lo = shoulder_y + int(H * 0.30)
    for (sx, sy, ex, ey) in (
        (cx + int(W * 0.20) + lean, shoulder_y + int(H * 0.12), pole_x, grip_hi),
        (cx + int(W * 0.22) + lean, shoulder_y + int(H * 0.24), pole_x, grip_lo),
    ):
        pygame.draw.line(surf, SHROUD_DK, (sx, sy), (ex, ey), max(4, int(10 * ss)))
        pygame.draw.line(surf, SHROUD, (sx, sy), (ex, ey), max(3, int(7 * ss)))
        pygame.draw.line(surf, SHROUD_HI, (sx - int(ss), sy - int(ss)),
                         (int((sx + ex) / 2), int((sy + ey) / 2)), max(2, int(3 * ss)))

    # — The SNUFFER-CANDLE POLE held upright: a tall FAT banded pole capped by a
    #   bell-shaped candle-snuffer cone with a soul-flame peeking under the rim.
    #   WHY r2: r1's pole was a hairline lost on night sky — thickened substantially.
    pole_top = top_y - int(H * 0.20)
    pole_bot = feet_y - int(H * 0.04)
    _snuffer_pole(surf, pole_x, pole_top, pole_bot, max(4, int(9 * ss)), ss,
                  bell=True)

    # — Stub mitts over the pole so the grip reads (drawn last to sit on top).
    for gy in (grip_hi, grip_lo):
        pygame.draw.circle(surf, INK, (int(pole_x), int(gy)), max(4, int(8 * ss)))
        pygame.draw.circle(surf, SHROUD, (int(pole_x), int(gy)), max(3, int(7 * ss)))
        pygame.draw.circle(surf, SHROUD_HI,
                           (int(pole_x - ss), int(gy - ss)), max(2, int(2.6 * ss)))


def _snuffer_pole(surf, cx, top_y, bot_y, hw, ss, *, bell=True):
    """The pole body + (optionally) the snuffer-bell cap + soul-flame. Dark-cored
    bone pole with brass band rings; the bell-cone caps the top and a soul-pink
    flame peeks under its rim with an additive glow. The pole alone (bell=False)
    is the repeatable PILLAR mid; bell=True is the gap-edge cap flourish."""
    # Pole: dark-core mass, bone rail, bright bone highlight, hard keyline — reads
    # round, fat, and holds value on dark sky (the bone rail is the bright cue).
    pygame.draw.line(surf, INK, (int(cx), int(top_y)), (int(cx), int(bot_y)),
                     hw + max(3, int(5 * ss)))
    pygame.draw.line(surf, BONE_DK, (int(cx), int(top_y)), (int(cx), int(bot_y)), hw)
    # Brighter bone rail down the lit side so the round post pops off night sky.
    pygame.draw.line(surf, BONE, (int(cx - hw * 0.28), int(top_y)),
                     (int(cx - hw * 0.28), int(bot_y)), max(2, int(hw * 0.42)))
    pygame.draw.line(surf, BRASS_HI, (int(cx - hw * 0.32), int(top_y)),
                     (int(cx - hw * 0.32), int(bot_y)), max(1, int(2 * ss)))
    # Brass band rings — pillar banding when tiled.
    span = bot_y - top_y
    for t in (0.30, 0.62, 0.90):
        ry = int(top_y + span * t)
        pygame.draw.rect(surf, _shade_c(BRASS, -50),
                         (int(cx - hw - 2 * ss), ry, int((hw + 2 * ss) * 2),
                          max(2, int(4 * ss))))
        pygame.draw.line(surf, BRASS_HI, (int(cx - hw - 2 * ss), ry + int(ss)),
                         (int(cx + hw + 2 * ss), ry + int(ss)), max(1, int(1.4 * ss)))
    if not bell:
        return
    # The candle-snuffer BELL cone: a flat cone (triad) flaring at the rim, with a
    # finial knob on top — the unmistakable snuffer silhouette. WHY r2: r1's cap
    # barely registered at 1x, so the bell + rim + flame are all enlarged and the
    # cone gets its own bright rim so it clears night sky like the body.
    bw = int(hw * 2.2)
    bh = int(hw * 3.4)
    by = top_y                       # bell rim sits at the pole top
    cone = [(cx, by - bh), (cx - bw, by), (cx + bw, by)]
    icone = [(int(p[0]), int(p[1])) for p in cone]
    pygame.draw.polygon(surf, _shade_c(SHROUD, -40), icone)
    pygame.draw.polygon(surf, SHROUD,
                        [(int(p[0] + ss), int(p[1])) for p in
                         ((cx, by - bh + ss), (cx - bw + ss, by - ss),
                          (cx + bw - ss, by - ss))])
    pygame.draw.line(surf, SHROUD_HI, (int(cx), int(by - bh)),
                     (int(cx - bw + ss), int(by - ss)), max(2, int(3 * ss)))
    pygame.draw.polygon(surf, SHROUD_RIM, icone, max(1, int(1.6 * ss)))
    pygame.draw.polygon(surf, INK, icone, max(2, int(2.4 * ss)))
    # Brass rim band + finial knob — thicker so the snuffer mouth reads.
    pygame.draw.line(surf, _shade_c(BRASS, -50), (int(cx - bw), int(by)),
                     (int(cx + bw), int(by)), max(3, int(5 * ss)))
    pygame.draw.line(surf, BRASS, (int(cx - bw), int(by - ss)),
                     (int(cx + bw), int(by - ss)), max(2, int(3 * ss)))
    pygame.draw.circle(surf, BRASS, (int(cx), int(by - bh)), max(3, int(4 * ss)))
    pygame.draw.circle(surf, BRASS_HI, (int(cx - ss), int(by - bh - ss)),
                       max(1, int(2 * ss)))
    # The soul-flame peeking under the bell rim — a bigger soul-pink teardrop with
    # a wider additive glow (the prop's signature accent; void eyes share the cyan).
    fy = by + int(hw * 1.2)
    blit_glow(surf, int(cx), int(fy), max(5, int(12 * ss)), FLAME_PINK, alpha=190)
    flame = [(cx, fy - int(hw * 2.2)), (cx - int(hw * 1.0), fy),
             (cx, fy + int(hw * 0.7)), (cx + int(hw * 1.0), fy)]
    pygame.draw.polygon(surf, FLAME_PINK, [(int(p[0]), int(p[1])) for p in flame])
    pygame.draw.polygon(surf, FLAME_HOT,
                        [(cx, int(fy - hw * 1.3)), (int(cx - hw * 0.5), int(fy)),
                         (cx, int(fy + hw * 0.3)), (int(cx + hw * 0.5), int(fy))])
    pygame.draw.circle(surf, STAR_WHITE, (int(cx), int(fy - hw * 0.5)),
                       max(1, int(hw * 0.35)))


def _add_outline(src, outline_color=(28, 22, 30, 230)):
    """Grow a 1px dark silhouette outline (the parrot `_add_outline` recipe) so the
    figure POPS on any sky — the house silhouette-pop discipline."""
    w, h = src.get_size()
    pad = 2
    out = pygame.Surface((w + pad * 2, h + pad * 2), pygame.SRCALPHA)
    mask = pygame.mask.from_surface(src, threshold=8)
    sil = mask.to_surface(setcolor=outline_color, unsetcolor=(0, 0, 0, 0))
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1),
                   (-1, -1), (1, -1), (-1, 1), (1, 1)):
        out.blit(sil, (pad + dx, pad + dy))
    out.blit(src, (pad, pad))
    return out


# ── pillar mirror ─────────────────────────────────────────────────────────────

def draw_pole_pillar(surf, cx, top, bot, hw, ss, *, cap):
    """Prove the prop->pillar mirror: the snuffer-POLE is the vertical post that
    runs the full obstacle height; the snuffer-BELL + soul-flame ride the GAP-EDGE
    as the cap flourish. `cap` toggles the bell cap (the gap end) vs a plain post.
    The brass band rings give the repeatable mid its banding."""
    if cap:
        # The pole runs from the gap up; the bell caps the GAP end (here the top).
        _snuffer_pole(surf, cx, top, bot, hw, ss, bell=True)
    else:
        _snuffer_pole(surf, cx, top, bot, hw, ss, bell=False)


# ── sky panels (real biome keyframes) ─────────────────────────────────────────

def _sky_panel(w, h, night):
    surf = pygame.Surface((w, h))
    if night:
        top, bot = (5, 8, 30), (35, 55, 115)          # biome NIGHT keyframe
    else:
        top, bot = (40, 110, 200), (170, 220, 245)    # biome DAY keyframe
    for y in range(h):
        pygame.draw.line(surf, lerp_color(top, bot, y / h), (0, y), (w, y))
    if night:
        # A few backdrop stars so the dark sky reads as night, not flat blue —
        # mirrors get_sky_surface_biome's star sprinkle.
        import random
        rng = random.Random(w * 7919)
        for _ in range(40):
            sx, sy = rng.randint(0, w - 1), rng.randint(0, int(h * 0.7))
            pygame.draw.circle(surf, (255, 255, 255), (sx, sy),
                               rng.choice((1, 1, 2)))
    return surf


def _boss_bitmap(disp_w, disp_h, ss, **kw):
    """Render the boss supersampled then smoothscale down (house AA discipline),
    with the 1px outline grown on the downscaled sprite. WHY r2: the squatter,
    wider build + its held snuffer-pole (which rises ABOVE the head) need more
    headroom and right-margin than r1 — figure is shifted left and the feet
    dropped so the whole prop-and-bell reads inside the cell without clipping."""
    big = pygame.Surface((disp_w * ss, disp_h * ss), pygame.SRCALPHA)
    # Scale off the smaller axis so the wide hem + the tall held pole both fit.
    scale = min(disp_w / 270.0, disp_h / 250.0)
    draw_hollow(big, int(disp_w * 0.42 * ss), int((disp_h - 6) * ss),
                scale=scale, ss=ss, **kw)
    small = pygame.transform.smoothscale(big, (disp_w, disp_h))
    return _add_outline(small)


def main():
    ss = 3
    label_f = pygame.font.SysFont("dejavusans", 19, bold=True)
    title_f = pygame.font.SysFont("dejavusans", 30, bold=True)
    note_f = pygame.font.SysFont("dejavusans", 14)

    GAP = 26
    SHOW_W, SHOW_H = 360, 560      # (a) showcase boss
    PILL_W, PILL_H = 300, 560      # (b) pillar pair
    INS_W, INS_H = 150, 320        # (c) 1x in-game insets (stacked day/night)

    SHEET_W = GAP * 5 + SHOW_W + PILL_W + INS_W
    SHEET_H = 110 + max(SHOW_H, PILL_H, INS_H * 2 + 30) + 70

    sheet = pygame.Surface((SHEET_W, SHEET_H))
    sheet.fill((24, 22, 32))
    sheet.blit(title_f.render("SKYBIT ENDGAME BOSS  —  THE HOLLOW  —  round 2",
                              True, (236, 236, 240)), (28, 22))
    sheet.blit(note_f.render(
        "Faceless cosmic void-shroud, chibi-flat. Big hood + flat-black star-void + "
        "cyan pinprick eyes + HARD scalloped hem. Midnight-indigo / electric-cyan / "
        "soul-pink.", True, (170, 170, 184)), (28, 58))
    sheet.blit(note_f.render(
        "Snuffer-candle pole = prop->pillar mirror.  FLAT fills + ink keylines, "
        "triad form, no feathering.", True, (170, 170, 184)), (28, 78))

    top_y = 104

    # (a) Showcase boss over a day/night split panel so the cosmic palette is read
    # against both the bright day sky and (critically) the dark night sky.
    sx = GAP
    show = pygame.Surface((SHOW_W, SHOW_H))
    half = SHOW_W // 2
    show.blit(_sky_panel(half, SHOW_H, False), (0, 0))
    show.blit(_sky_panel(SHOW_W - half, SHOW_H, True), (half, 0))
    boss = _boss_bitmap(int(SHOW_W * 0.7), int(SHOW_H * 0.86), ss, eye_dx=-1.0)
    show.blit(boss, ((SHOW_W - boss.get_width()) // 2,
                     (SHOW_H - boss.get_height()) // 2))
    pygame.draw.line(show, (70, 64, 80), (half, 0), (half, SHOW_H), 1)
    sheet.blit(show, (sx, top_y))
    pygame.draw.rect(sheet, (70, 64, 80), (sx, top_y, SHOW_W, SHOW_H), 1)
    lab = label_f.render("BOSS  (day | night)", True, (236, 236, 240))
    sheet.blit(lab, (sx + (SHOW_W - lab.get_width()) // 2, top_y + SHOW_H + 8))
    sheet.blit(note_f.render("scary-cute: pinprick eyes + chibi shoulders under big hood",
                             True, (170, 170, 184)), (sx + 4, top_y + SHOW_H + 32))

    # (b) Pillar pair: the snuffer-pole mirrored top<->bottom, proving cap (bell at
    # the gap edge) + repeatable mid (banded pole). Night sky to stress legibility.
    px = sx + SHOW_W + GAP
    pill = _sky_panel(PILL_W, PILL_H, True)
    gap_top = int(PILL_H * 0.40)
    gap_bot = int(PILL_H * 0.60)
    col_x = PILL_W // 2
    # WHY r2: r1's post was a near-invisible hairline on night sky — fattened to a
    # real obstacle so the pillar reads as a tileable pole at gameplay scale.
    post_w = max(6, int(11 * ss))
    big_t = pygame.Surface((PILL_W * ss, PILL_H * ss), pygame.SRCALPHA)
    # Bottom pier: post rises from the floor, bell caps UP into the gap.
    draw_pole_pillar(big_t, col_x * ss, gap_bot * ss, (PILL_H - 8) * ss,
                     post_w, ss, cap=True)
    # Top pier: mirror — build the same pillar then flip the whole scratch so the
    # bell caps DOWN into the gap and the banded pole runs to the ceiling.
    top_scr = pygame.Surface((PILL_W * ss, PILL_H * ss), pygame.SRCALPHA)
    draw_pole_pillar(top_scr, col_x * ss, (PILL_H - gap_top) * ss,
                     (PILL_H - 8) * ss, post_w, ss, cap=True)
    top_scr = pygame.transform.flip(top_scr, False, True)
    big_t.blit(top_scr, (0, 0))
    small_t = pygame.transform.smoothscale(big_t, (PILL_W, PILL_H))
    pill.blit(_add_outline(small_t), (-2, -2))
    pygame.draw.line(pill, (110, 200, 150), (8, gap_top), (PILL_W - 8, gap_top), 1)
    pygame.draw.line(pill, (110, 200, 150), (8, gap_bot), (PILL_W - 8, gap_bot), 1)
    pill.blit(note_f.render("flap gap", True, (150, 230, 180)), (10, gap_top + 4))
    sheet.blit(pill, (px, top_y))
    pygame.draw.rect(sheet, (70, 64, 80), (px, top_y, PILL_W, PILL_H), 1)
    lab = label_f.render("PILLAR  (pole=post, bell=gap cap)", True, (236, 236, 240))
    sheet.blit(lab, (px + (PILL_W - lab.get_width()) // 2, top_y + PILL_H + 8))
    sheet.blit(note_f.render("brass bands = repeatable mid banding", True,
                             (170, 170, 184)), (px + 4, top_y + PILL_H + 32))

    # (c) 1x in-game-scale INSETS on day AND night — must especially prove the
    # void-shroud POPS on a dark night sky at true gameplay footprint.
    ix = px + PILL_W + GAP
    for j, night in enumerate((False, True)):
        sky_i = _sky_panel(INS_W, INS_H, night)
        # ~true 1x boss footprint within the 360x640 virtual canvas.
        boss_i = _boss_bitmap(int(INS_W * 0.72), int(INS_H * 0.82), ss,
                              eye_dx=-1.0, blink=(j == 1))
        sky_i.blit(boss_i, ((INS_W - boss_i.get_width()) // 2,
                            INS_H - boss_i.get_height() - 6))
        frame = pygame.Surface((INS_W + 12, INS_H + 26), pygame.SRCALPHA)
        frame.fill((20, 18, 26, 235))
        frame.blit(sky_i, (6, 22))
        frame.blit(note_f.render("1x  " + ("NIGHT" if night else "DAY"), True,
                                 (220, 222, 230)), (8, 3))
        pygame.draw.rect(frame, (90, 84, 104), (6, 22, INS_W, INS_H), 1)
        sheet.blit(frame, (ix, top_y + j * (INS_H + 30)))

    out = "/home/user/skybit/docs/skybit_reaper/the_hollow/round_2.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
