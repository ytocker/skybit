"""Look-dev sheet for the Skybit DEVIL boss, Group A take A2 — "BRIMSTONE".

A devilish-death hybrid: a faceted, angular cooling-LAVA boulder-SKULL — death
made of HELLFIRE STONE. The cranium is a low-poly chunk of charcoal basalt cut
from 5-6 hard angular planes (NOT Big Reapy's smooth dome); glowing magma seams
crack through the facets, the sockets + a square-tooth grin keep it reading
SKULL not just rock. It sits like a hot coal (no legs) on a squat ember-cloaked
body. Its signature prop is the most literally pillar-like in the whole set: a
hexagonal BASALT COLUMN with a magma seam running its length, capped by a
flaming brazier-bowl.

House style this obeys (the warren-clown / Big-Reapy grammar):
  - CHIBI proportions — big head dominant, short wide weight-shifted body.
  - FLAT saturated fills + hard 1-2px ink keylines (20,16,22). No within-shape
    soft gradients, no bevels, no realistic shading.
  - Form via the triad: dark-core -> flat fill -> top-left rim sheen, applied
    per FACET so the skull reads faceted-but-flat.
  - Magma seams = FLAT bright shapes (orange seam + yellow hot core) + an OUTSIDE
    BLEND_ADD glow — never a soft within-shape gradient.
  - Silhouette POP via a 1px ink keyline grown from the alpha mask; the jagged
    cranial crags break the outline so it reads stony.
  - SUPERSAMPLE then smoothscale.

Prop -> pillar mirror: the basalt column shaft is the tileable PILLAR BODY (its
hexagonal column-segments are the banding, the magma seam runs the whole length);
the flaming brazier-bowl is the detachable TOP CAP that rides the gap-edge only,
so a top/bottom mirror reads as a clean vertical basalt column with fire welling
INTO the gap. The most "literally a pillar" prop in the set.

Imports the real game colour/shape kit only; nothing under game/ is touched.
Headless + deterministic.

    SDL_VIDEODRIVER=dummy PYTHONPATH=/home/user/skybit python tools/render_skybit_devil_brimstone.py
"""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from game.draw import _shade_c, lerp_color, make_glow_surface
from game.config import PIPE_W


pygame.init()

# ── "charcoal basalt & magma" palette (take A2) ──────────────────────────────
# Charcoal-basalt DOMINANT as the cool value anchor that holds the silhouette on
# a warm day sky; magma-orange seams + a hot-yellow core are the single glow
# family, kept as the ONLY warm so the rock never muddies. The dark seam/socket
# SHAPE must read in grayscale too, so the magma is never the only face cue.
BASALT      = (46, 40, 48)      # charcoal-basalt facet fill (the rock body)
BASALT_DK   = (28, 24, 34)      # dark-core ring / facet seat
ROCK        = (78, 70, 82)      # cool-rock lighter facet (lit planes)
ROCK_SHEEN  = (150, 142, 150)   # ash-grey top-left rim sheen

MAGMA       = (255, 96, 30)     # magma-orange seam
MAGMA_CORE  = (255, 206, 72)    # hot-yellow molten core
MAGMA_DEEP  = (200, 52, 20)     # seam shadow where the crack deepens
EMBER_SOOT  = (96, 88, 96)      # soot-puff grey

INK         = (20, 16, 22)      # the house keyline


def _add_outline(src, outline_color=(*INK, 235)):
    """Grow a 1px dark keyline from the alpha mask so the silhouette POPS on any
    sky (the parrot/Big-Reapy `_add_outline` recipe). Returns a padded surface."""
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


def _facet(surf, pts, col, ss, *, sheen_edge=None):
    """One flat triad-lit basalt plane: a dark-core seat polygon, the flat facet
    fill inset on top, and an optional top-left rim-sheen line down one edge. This
    is the per-facet equivalent of Big-Reapy's `_triad_circle` — it gives the
    low-poly skull sculpted volume while every plane stays dead flat."""
    ipts = [(int(x), int(y)) for x, y in pts]
    # Dark-core seat behind the facet so adjacent planes read as separate cuts.
    pygame.draw.polygon(surf, _shade_c(col, -22), ipts)
    # Flat fill inset slightly toward the centroid so the dark seat shows as a
    # hairline crack between facets (the low-poly rock look).
    cx = sum(p[0] for p in pts) / len(pts)
    cy = sum(p[1] for p in pts) / len(pts)
    k = 1.6 * ss
    inset = []
    for x, y in pts:
        dx, dy = cx - x, cy - y
        d = math.hypot(dx, dy) or 1.0
        inset.append((x + dx / d * k, y + dy / d * k))
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in inset])
    if sheen_edge is not None:
        a, b = sheen_edge
        pygame.draw.line(surf, ROCK_SHEEN, (int(a[0]), int(a[1])),
                         (int(b[0]), int(b[1])), max(1, int(1.6 * ss)))


def _magma_seam(surf, pts, ss, *, width=4.0, glow=True):
    """A magma crack: a FLAT bright shape (deep-orange edge -> orange seam ->
    hot-yellow core) plus a TIGHT outside additive glow — light leaking from a
    crack in cool rock, NOT rock on fire. `pts` is the seam polyline; it stays
    bright enough to survive the 1x downscale while the charcoal stays dominant."""
    if len(pts) < 2:
        return
    if glow:
        # A TIGHT rim glow stamped ONCE along the seam (sparse samples, halved
        # radius, low alpha) so the bloom hugs the crack edge instead of
        # compounding into a solid orange wash over the whole figure.
        gr = int(width * 1.1 * ss)
        if gr >= 1:
            g = make_glow_surface(gr, MAGMA, alpha_center=82, falloff=2.6)
            step = max(1, len(pts) // 3)
            for px, py in pts[::step]:
                surf.blit(g, (int(px - gr - 1), int(py - gr - 1)),
                          special_flags=pygame.BLEND_ADD)

    def _stroke(col, w):
        w = max(1, int(w))
        for i in range(len(pts) - 1):
            a, b = pts[i], pts[i + 1]
            pygame.draw.line(surf, col, (int(a[0]), int(a[1])),
                             (int(b[0]), int(b[1])), w)
        for px, py in pts:
            pygame.draw.circle(surf, col, (int(px), int(py)), max(1, w // 2))

    _stroke(MAGMA_DEEP, width * 1.5 * ss)
    _stroke(MAGMA, width * 1.0 * ss)
    _stroke(MAGMA_CORE, width * 0.42 * ss)


# ── the faceted boulder-skull face ───────────────────────────────────────────

def _skull_face(surf, cx, cy, r, ss, *, night=False):
    """The faceted hellfire-stone boulder-skull: a low-poly charcoal cranium built
    from hard angular planes (NOT a circle), with magma seams cracking between
    facets, two deep sockets pooling molten light, a chipped square-tooth grin and
    a tiny upturned nose hole — so it reads SKULL (sockets + jaw) AND infernal
    (crags + glowing seams). `night` pushes the seam/socket glow so the magma
    stays lit on a dark sky instead of going to dead charcoal."""
    # — The cranium as an angular boulder. A ring of jagged vertices (crags) gives
    #   the silhouette its stony broken-outline read; planes are cut from it.
    crags = []
    n = 11
    # Per-vertex radius wobble so the boulder is irregular, not a clean polygon.
    jag = [1.02, 0.86, 1.06, 0.80, 1.04, 0.90, 1.05, 0.82, 1.08, 0.88, 1.00]
    for i in range(n):
        ang = -math.pi / 2 + (i / n) * 2 * math.pi
        rr = r * jag[i % len(jag)]
        # Slightly wider than tall + a flat-ish brow up top so it reads as a skull
        # boulder, not a ball.
        crags.append((cx + math.cos(ang) * rr * 1.04,
                      cy + math.sin(ang) * rr * 0.98))

    # Dark-core boulder seat behind everything.
    pygame.draw.polygon(surf, BASALT_DK, [(int(x), int(y)) for x, y in crags])

    # Cut the boulder into 6 hard angular facets fanning from an off-centre point
    # (up-left, so the lit planes cluster top-left per the triad). Alternate the
    # facet value (lit ROCK vs shadow BASALT) so the low-poly cut reads.
    fp = (cx - r * 0.16, cy - r * 0.20)         # facet fan origin (light side)
    for i in range(n):
        a = crags[i]
        b = crags[(i + 1) % n]
        # Lit when the facet's outward normal points up-left; shaded otherwise.
        mid_ang = math.atan2((a[1] + b[1]) * 0.5 - cy, (a[0] + b[0]) * 0.5 - cx)
        lit = math.cos(mid_ang - math.radians(215)) > 0.15
        col = ROCK if lit else BASALT
        sheen = (a, b) if lit else None
        _facet(surf, (fp, a, b), col, ss, sheen_edge=sheen)

    # — Magma seams threading the cranial cracks: a few bold zigzags between facets
    #   radiating from the brow. Kept to THREE bold seams (not many fine cracks) so
    #   they survive 1x as molten lines, not noise.
    seam_specs = [
        [(cx - r * 0.10, cy - r * 0.92), (cx - r * 0.02, cy - r * 0.50),
         (cx - r * 0.20, cy - r * 0.20), (cx - r * 0.04, cy + r * 0.10)],
        [(cx + r * 0.30, cy - r * 0.78), (cx + r * 0.46, cy - r * 0.40),
         (cx + r * 0.30, cy - r * 0.08)],
        [(cx - r * 0.62, cy - r * 0.30), (cx - r * 0.44, cy - r * 0.02),
         (cx - r * 0.60, cy + r * 0.26)],
    ]
    sw = 3.0 if not night else 3.6
    for seam in seam_specs:
        _magma_seam(surf, seam, ss, width=sw)

    # — Eye sockets: deep angular EMPTY ink cavities with only a small molten pool
    #   pooled LOW inside — "empty skull socket with embers at the bottom", NOT a
    #   glowing iris. Mostly ink so the bone (not the magma) draws the face.
    eye_dx = r * 0.40
    eye_dy = -r * 0.04
    sock_r = r * 0.30
    for s in (-1, 1):
        ex, ey = cx + s * eye_dx, cy + eye_dy
        # Angular ink socket (a cut hexagonal hollow, not a round eye) — the
        # grayscale-legible shape that survives without the magma colour. The dark
        # cavity is the dominant value; the magma only sits in its floor.
        hexr = sock_r
        sock = []
        for k in range(6):
            aa = math.radians(30 + k * 60)
            sock.append((ex + math.cos(aa) * hexr * 1.0,
                         ey + math.sin(aa) * hexr * 0.92))
        pygame.draw.polygon(surf, INK, [(int(x), int(y)) for x, y in sock])
        pygame.draw.polygon(surf, _shade_c(ROCK, -10),
                            [(int(x), int(y)) for x, y in sock], max(1, int(2 * ss)))
        # Only a SMALL ember pool resting low in the cavity floor (a flat sliver,
        # not a centred iris) + a tight contained underglow so the cool basalt
        # keeps owning the face. The pool + glow are sized as a fixed FRACTION of the
        # socket but kept genuinely small so the read holds at BOTH boss + 1x scale:
        # the round-disc-iris / horizontal-lid look at showcase scale came from a
        # glow that ballooned with sock_r — so the bloom is tied tightly to the small
        # pool, not the whole cavity. Night only lifts alpha, never the pool size.
        pool_y = ey + sock_r * 0.50
        pool_hw = sock_r * 0.34
        glow_a = 132 if night else 88
        glow_r = int(pool_hw * 1.05)
        if glow_r >= 1:
            g = make_glow_surface(glow_r, MAGMA, alpha_center=glow_a, falloff=2.8)
            surf.blit(g, (int(ex - glow_r - 1), int(pool_y - glow_r - 1)),
                      special_flags=pygame.BLEND_ADD)
        # A small flat trapezoid sliver pooled LOW — a puddle on the cavity floor,
        # not a disc filling the socket; NO horizontal core line (that read as a lid).
        pool = [(ex - pool_hw, pool_y - sock_r * 0.06),
                (ex + pool_hw, pool_y - sock_r * 0.06),
                (ex + pool_hw * 0.66, pool_y + sock_r * 0.18),
                (ex - pool_hw * 0.66, pool_y + sock_r * 0.18)]
        pygame.draw.polygon(surf, MAGMA, [(int(x), int(y)) for x, y in pool])
        # A tiny hot dot at the very bottom of the puddle so the ember reads molten
        # without a lid-like horizontal bar bisecting the socket.
        pygame.draw.circle(surf, MAGMA_CORE, (int(ex), int(pool_y + sock_r * 0.06)),
                           max(1, int(pool_hw * 0.34)))
        # A heavy angular basalt brow-ridge sitting OVER each socket, only gently
        # lifted at the outer corner with a SOFTENED (less peaked) wedge so the
        # read is eager/curious, not an aggressive glare.
        brow = [(ex - sock_r * 1.10, ey - sock_r * 0.62),
                (ex + sock_r * 1.05, ey - sock_r * 0.88),
                (ex + sock_r * 0.95, ey - sock_r * 0.58)]
        if s < 0:
            brow = [(2 * ex - x, y) for x, y in brow]
        pygame.draw.polygon(surf, _shade_c(BASALT, -8),
                            [(int(x), int(y)) for x, y in brow])

    # — Nose: a small upturned triangular hole between + below the sockets.
    nose_y = cy + r * 0.34
    nose = [(cx, nose_y - r * 0.10), (cx - r * 0.10, nose_y + r * 0.12),
            (cx + r * 0.10, nose_y + r * 0.12)]
    pygame.draw.polygon(surf, INK, [(int(x), int(y)) for x, y in nose])

    # — The magma grin: a wide deep mouth-seat that GLOWS (the "blushing" pulse),
    #   with chunky square basalt teeth biting down over it. Even teeth + a bowed-UP
    #   band = a happy jack-grin, not a horror rictus; one chipped tooth for cheek.
    grin_y = cy + r * 0.66
    grin_hw = r * 0.58
    grin_h = r * 0.32
    bow_amp = grin_h * 0.58

    def _bow(x_rel):
        return bow_amp * (x_rel * x_rel)

    # Deep molten mouth-cavity: a wide curved band filled with magma so the grin
    # glows from within (the scary-cute blush). Drawn first; teeth bite over it.
    seat_top, seat_bot = [], []
    m = 16
    for i in range(m + 1):
        xr = -1.0 + 2.0 * (i / m)
        x = cx + xr * grin_hw
        yt = grin_y - _bow(xr)
        seat_top.append((x, yt))
        seat_bot.append((x, yt + grin_h))
    seat = seat_top + seat_bot[::-1]
    # A TIGHT additive glow hugging just the mouth-band so the grin reads as molten
    # light leaking between the teeth — not a warm cheek-disc washing the lower
    # face. Halved radius + low alpha so the basalt cheekbone stays cool basalt;
    # alpha pulled down a touch so the grin reads as a quiet blush behind the teeth,
    # not a lightbar, and the two scales agree.
    gr = int(grin_hw * 0.62)
    gm = make_glow_surface(gr, MAGMA,
                           alpha_center=104 if night else 64, falloff=2.8)
    surf.blit(gm, (int(cx - gr - 1), int(grin_y + grin_h * 0.45 - gr - 1)),
              special_flags=pygame.BLEND_ADD)
    pygame.draw.polygon(surf, MAGMA_DEEP, [(int(x), int(y)) for x, y in seat])
    inner_seat = ([(x, y + ss) for x, y in seat_top]
                  + [(x, y - ss) for x, y in seat_bot][::-1])
    pygame.draw.polygon(surf, MAGMA, [(int(x), int(y)) for x, y in inner_seat])
    # The hot-yellow core band is cooled ~15-20%: a deeper-orange MAGMA core instead
    # of MAGMA_CORE yellow, and a thinner band — so the teeth-as-basalt-blocks stay
    # the hero and the glow is a blush, not a yellow-cored lightbar at showcase scale.
    core_seat = ([(x, y + grin_h * 0.42) for x, y in seat_top]
                 + [(x, y + grin_h * 0.60) for x, y in seat_top][::-1])
    pygame.draw.polygon(surf, _shade_c(MAGMA, 6),
                        [(int(x), int(y)) for x, y in core_seat])

    # Chunky square basalt teeth biting DOWN from the upper edge over the magma,
    # so the molten gaps glow between them. One chipped (shorter) for cheek.
    teeth = 5
    gap = grin_hw * 0.12
    tw = (grin_hw * 2.0 - gap * (teeth - 1)) / teeth
    for i in range(teeth):
        tx = -grin_hw + i * (tw + gap)
        xr = (tx + tw * 0.5) / grin_hw
        ty = grin_y - _bow(xr) - ss
        th = grin_h * (0.46 if i == 3 else 0.74)        # tooth #3 chipped short
        rect = pygame.Rect(int(cx + tx + ss), int(ty), int(tw - ss), int(th))
        pygame.draw.rect(surf, BASALT_DK, rect, border_radius=max(1, int(1.4 * ss)))
        pygame.draw.rect(surf, ROCK, rect.inflate(-int(2 * ss), -int(2 * ss)),
                         border_radius=max(1, int(1.4 * ss)))
        pygame.draw.line(surf, ROCK_SHEEN, (rect.left + ss, rect.top + ss),
                         (rect.left + ss, rect.top + int(th * 0.55)), max(1, int(ss)))

    # — A tiny puff of soot wisping from one socket (the scary-cute beat). A couple
    #   of soft grey lobes drifting up + out from the right socket.
    sx0 = cx + eye_dx + sock_r * 0.4
    sy0 = cy + eye_dy - sock_r * 1.1
    for i, (ox, oy, rr) in enumerate(((0, 0, 0.30), (0.5, -0.7, 0.24),
                                      (1.1, -1.4, 0.18))):
        pc = make_glow_surface(int(sock_r * rr * 2.0), EMBER_SOOT,
                               alpha_center=120 - i * 28, falloff=2.0)
        pr = int(sock_r * rr * 2.0)
        surf.blit(pc, (int(sx0 + sock_r * ox - pr), int(sy0 + sock_r * oy - pr)),
                  special_flags=pygame.BLEND_ALPHA_SDL2)


def _coal_body(surf, cx, neck_y, w, h, ss):
    """The squat ember-cloaked body the skull sits on like a hot coal — NO legs.
    A wide low charcoal mound with magma seams cracking through it and a soot-dark
    cloak hem, so the whole figure reads bottom-rounded + sitting, head dominant."""
    hem_y = neck_y + h
    # Wide rounded coal-mound silhouette — broadest at the base so it 'sits'.
    body = [
        (cx - w * 0.34, neck_y),
        (cx - w * 0.62, neck_y + h * 0.50),
        (cx - w * 0.78, hem_y),
        (cx + w * 0.78, hem_y),
        (cx + w * 0.62, neck_y + h * 0.50),
        (cx + w * 0.34, neck_y),
    ]
    pygame.draw.polygon(surf, BASALT_DK, [(int(x), int(y)) for x, y in body])
    inner = [(cx - w * 0.30, neck_y + ss), (cx - w * 0.56, neck_y + h * 0.50),
             (cx - w * 0.70, hem_y - ss), (cx + w * 0.70, hem_y - ss),
             (cx + w * 0.56, neck_y + h * 0.50), (cx + w * 0.30, neck_y + ss)]
    pygame.draw.polygon(surf, BASALT, [(int(x), int(y)) for x, y in inner])
    # Top-left lit facet on the body so it shares the head's triad lighting.
    litf = [(cx - w * 0.30, neck_y + ss), (cx - w * 0.06, neck_y + h * 0.18),
            (cx - w * 0.30, neck_y + h * 0.56), (cx - w * 0.58, neck_y + h * 0.48)]
    pygame.draw.polygon(surf, ROCK, [(int(x), int(y)) for x, y in litf])
    pygame.draw.line(surf, ROCK_SHEEN, (int(cx - w * 0.34), int(neck_y + h * 0.12)),
                     (int(cx - w * 0.62), int(neck_y + h * 0.46)), max(2, int(2 * ss)))

    # ONE bold magma seam cracking down the coal-mound — a confident zigzag with
    # real width, not several thin snakes that shimmer to noise at 1x. It STARTS at
    # the neckline (so it reads as a single crack running from under the chin down
    # the body, not a stray floating ember dot) and stays mostly cool charcoal so
    # the figure reads "cracked rock", not "on fire".
    _magma_seam(surf, [(cx - w * 0.02, neck_y - h * 0.02),
                       (cx - w * 0.06, neck_y + h * 0.16),
                       (cx + w * 0.10, neck_y + h * 0.46),
                       (cx - w * 0.04, hem_y - h * 0.06)], ss, width=3.0)

    # Two stub basalt mitts poking from the mound — one will brace the column prop
    # (drawn by the caller), the other rests. Tiny + blocky = cute, no legs needed.
    for s in (-1, 1):
        ax = cx + s * w * 0.56
        ay = neck_y + h * 0.40
        mr = w * 0.13
        mitt = []
        for k in range(6):
            aa = math.radians(k * 60)
            mitt.append((ax + math.cos(aa) * mr, ay + math.sin(aa) * mr))
        pygame.draw.polygon(surf, BASALT_DK, [(int(x), int(y)) for x, y in mitt])
        pygame.draw.polygon(surf, ROCK, [(int(x - ss), int(y - ss)) for x, y in mitt])


# ── the basalt-column prop (and its pillar-tile components) ──────────────────

def _basalt_column(surf, cx, top_y, bot_y, hw, ss, *, seam_phase=0.0):
    """The basalt COLUMN shaft = the tileable PILLAR BODY: a literal hexagonal
    volcanic column built from stacked column-SEGMENTS (Giant's-Causeway banding),
    a faceted top-left lit edge + a shadowed right edge so it reads as a prism, and
    a single magma SEAM running the whole length (welling brighter where segments
    meet). The most 'literally a pillar' prop in the set — no fork, no flourish;
    the brazier fire is the detachable top cap. Chunky banding sized so only a few
    segments stack across a gameplay-height pillar, so the read survives the 1x
    downscale instead of washing to a flat charcoal bar."""
    length = bot_y - top_y
    # Hexagonal-prism cross-section read: a lit left face, a mid front face, a
    # shadowed right face. Drawn as three vertical bands.
    left_x = cx - hw
    right_x = cx + hw
    facet_l = cx - hw * 0.34
    facet_r = cx + hw * 0.30
    # Dark-core full-width seat.
    pygame.draw.rect(surf, BASALT_DK,
                     (int(left_x), int(top_y), int(2 * hw), int(length)))
    # Shadowed right face.
    pygame.draw.polygon(surf, BASALT, [(int(facet_r), int(top_y)),
                                       (int(right_x), int(top_y)),
                                       (int(right_x), int(bot_y)),
                                       (int(facet_r), int(bot_y))])
    # Mid front face.
    pygame.draw.polygon(surf, _shade_c(BASALT, 10),
                        [(int(facet_l), int(top_y)), (int(facet_r), int(top_y)),
                         (int(facet_r), int(bot_y)), (int(facet_l), int(bot_y))])
    # Lit left face (top-left light per the triad).
    pygame.draw.polygon(surf, ROCK, [(int(left_x), int(top_y)),
                                     (int(facet_l), int(top_y)),
                                     (int(facet_l), int(bot_y)),
                                     (int(left_x), int(bot_y))])
    pygame.draw.line(surf, ROCK_SHEEN, (int(left_x + ss), int(top_y)),
                     (int(left_x + ss), int(bot_y)), max(1, int(1.6 * ss)))
    # Prism edge keylines between the faces.
    for ex in (facet_l, facet_r):
        pygame.draw.line(surf, BASALT_DK, (int(ex), int(top_y)),
                         (int(ex), int(bot_y)), max(1, int(1.4 * ss)))

    # Horizontal column-SEGMENT joints (the Giant's-Causeway banding). Chunky so a
    # few stack across a gameplay post; a dark groove + a thin sheen lip per joint.
    seg_h = max(int(26 * ss), int(hw * 2.4))
    nseg = max(2, round(length / seg_h))
    seg_h = length / nseg
    for i in range(1, nseg):
        jy = top_y + i * seg_h
        pygame.draw.line(surf, BASALT_DK, (int(left_x), int(jy)),
                         (int(right_x), int(jy)), max(2, int(2.4 * ss)))
        pygame.draw.line(surf, ROCK_SHEEN, (int(left_x), int(jy + ss)),
                         (int(facet_l), int(jy + ss)), max(1, int(ss)))

    # The magma seam runs the FULL length of the column as a near-STRAIGHT crack
    # that only kinks at the segment joints — so the Giant's-Causeway banding stays
    # the dominant read and the seam is a secondary, decisive crack (not a sine
    # wobble competing with the joints). It wells BRIGHTER where segments meet.
    seam = [(cx, top_y)]
    for i in range(1, nseg):
        jy = top_y + i * seg_h
        # A small lateral jog at each joint = a real basalt fracture stepping
        # between columns, kept tight so the line reads straight at 1x.
        jog = hw * 0.16 * (1 if i % 2 else -1)
        seam.append((cx + jog, jy))
    seam.append((cx, bot_y))
    _magma_seam(surf, seam, ss, width=2.8)
    # Brighter molten welling exactly at each joint where the crack opens.
    for i in range(1, nseg):
        jy = top_y + i * seg_h
        jog = hw * 0.16 * (1 if i % 2 else -1)
        pygame.draw.circle(surf, MAGMA_CORE, (int(cx + jog), int(jy)),
                           max(1, int(1.4 * ss)))


def _brazier_cap(surf, cx, base_y, hw, ss, *, point_up=True):
    """The flaming brazier-bowl = the detachable PILLAR TOP CAP that rides the
    gap-edge ONLY. A wide basalt bowl crowning the column, brimful of welling magma
    with flame tongues licking up (or down, when it caps the bottom pillar) INTO
    the gap. Bold + bright so it survives the 1x downscale; it's the prop's
    signature flourish, mirroring the soul-catcher's role on Big Reapy.
    `point_up` orients the flame away from the shaft (toward the gap)."""
    d = -1 if point_up else 1
    bowl_w = hw * 2.4
    bowl_h = hw * 1.5
    # The basalt bowl: a trapezoid rim cup sitting on the column end.
    rim_y = base_y
    cup = [(cx - bowl_w, rim_y),
           (cx + bowl_w, rim_y),
           (cx + bowl_w * 0.62, rim_y + d * bowl_h),
           (cx - bowl_w * 0.62, rim_y + d * bowl_h)]
    pygame.draw.polygon(surf, BASALT_DK, [(int(x), int(y)) for x, y in cup])
    cup_in = [(cx - bowl_w + ss, rim_y + d * ss),
              (cx + bowl_w - ss, rim_y + d * ss),
              (cx + bowl_w * 0.60, rim_y + d * (bowl_h - ss)),
              (cx - bowl_w * 0.60, rim_y + d * (bowl_h - ss))]
    pygame.draw.polygon(surf, BASALT, [(int(x), int(y)) for x, y in cup_in])
    pygame.draw.line(surf, ROCK_SHEEN, (int(cx - bowl_w + ss), int(rim_y)),
                     (int(cx - bowl_w * 0.60), int(rim_y + d * (bowl_h - ss))),
                     max(1, int(1.6 * ss)))

    # Welling magma pool sitting in the bowl rim, with a contained additive glow —
    # this is the prop's signature flame flourish so it stays bright, but the bloom
    # is tightened so it doesn't wash the basalt shaft/skull below it into orange.
    pool_y = rim_y - d * bowl_h * 0.12
    gp = make_glow_surface(int(bowl_w * 1.1), MAGMA, alpha_center=175, falloff=2.4)
    gpr = int(bowl_w * 1.1)
    surf.blit(gp, (int(cx - gpr - 1), int(pool_y - d * bowl_w * 0.6 - gpr - 1)),
              special_flags=pygame.BLEND_ADD)

    # Flame tongues licking out of the bowl, AWAY from the shaft (into the gap).
    flame_h = bowl_w * 1.7
    for fx, fscale in ((-0.55, 0.7), (0.0, 1.0), (0.55, 0.72)):
        bx = cx + fx * bowl_w
        tip_y = pool_y - d * flame_h * fscale
        base_w = bowl_w * 0.42 * fscale
        # Outer orange flame.
        flame = [(bx - base_w, pool_y),
                 (bx - base_w * 0.25, pool_y - d * flame_h * fscale * 0.5),
                 (bx, tip_y),
                 (bx + base_w * 0.30, pool_y - d * flame_h * fscale * 0.5),
                 (bx + base_w, pool_y)]
        pygame.draw.polygon(surf, MAGMA, [(int(x), int(y)) for x, y in flame])
        # Inner hot-yellow core flame.
        core = [(bx - base_w * 0.5, pool_y),
                (bx, pool_y - d * flame_h * fscale * 0.82),
                (bx + base_w * 0.5, pool_y)]
        pygame.draw.polygon(surf, MAGMA_CORE, [(int(x), int(y)) for x, y in core])
    # Bright welling-pool lip across the rim so the magma reads brim-full.
    pygame.draw.line(surf, MAGMA_CORE,
                     (int(cx - bowl_w * 0.8), int(pool_y)),
                     (int(cx + bowl_w * 0.8), int(pool_y)), max(2, int(3 * ss)))


def build_brimstone(scale=1.0, ss=3, *, night=False):
    """The full boss figure on its own transparent surface. Head ~58% of total
    height (chibi head-dominant, sitting like a coal). Returns an outlined surface
    and its baseline (seat) y for placement. `night` pushes the magma glow so the
    seams + sockets stay lit on a dark sky."""
    H = int(252 * scale)
    W = int(150 * scale)
    pad = int(78 * scale)
    surf = pygame.Surface(((W + pad * 2) * ss, (H + pad) * ss), pygame.SRCALPHA)
    cx = (W // 2 + pad) * ss

    head_band = int(H * 0.58) * ss
    skull_r = head_band * 0.42
    skull_cy = int(pad * 0.32) * ss + skull_r
    skull_cx = cx

    neck_y = skull_cy + skull_r * 1.02
    body_w = W * 0.66 * ss
    body_h = int(H * 0.32) * ss

    # Basalt column held upright at the figure's right, braced by a stub mitt. The
    # shaft runs past the seat; the brazier fire rises above the skull (the
    # signature flourish overhead, mirroring Big Reapy's soul-catcher).
    bx = cx + W * 0.50 * ss
    bhw = 9 * ss
    cap_base = skull_cy - skull_r * 0.55
    seat_y = neck_y + body_h + W * 0.04 * ss
    _basalt_column(surf, bx, cap_base, seat_y + 8 * ss, bhw, ss)
    _brazier_cap(surf, bx, cap_base, bhw, ss, point_up=True)

    _coal_body(surf, skull_cx, neck_y, body_w, body_h, ss)
    _skull_face(surf, skull_cx, skull_cy, skull_r, ss, night=night)

    out_w = int(surf.get_width() / ss)
    out_h = int(surf.get_height() / ss)
    small = pygame.transform.smoothscale(surf, (out_w, out_h))
    return _add_outline(small), seat_y / ss


# ── pillar pair (prop -> pillar mirror proof) ────────────────────────────────

OVERHANG = 12


def _column_pillar_obstacle(height, ss, *, flip):
    """One basalt-column PILLAR obstacle: the hexagonal column fills the post, the
    flaming brazier cap sits at the gap end. `flip` makes the top pillar's flame
    point DOWN into the gap; the bottom pillar's flame points UP — proving the prop
    mirrors top<->bottom into a clean vertical basalt column with fire welling into
    the gap. The most literal prop->pillar mirror in the set."""
    bw = (PIPE_W + 2 * OVERHANG) * ss
    bh = max(1, int(height)) * ss
    surf = pygame.Surface((bw, bh), pygame.SRCALPHA)
    cx = bw // 2
    hw = 11 * ss
    cap_band = int(56 * ss)
    _basalt_column(surf, cx, 0, bh - cap_band, hw, ss)
    _brazier_cap(surf, cx, bh - cap_band, hw, ss, point_up=False)
    out = pygame.transform.smoothscale(surf, (PIPE_W + 2 * OVERHANG, max(1, int(height))))
    out = _add_outline(out)
    if flip:
        out = pygame.transform.flip(out, False, True)
    return out


# ── sheet composition ────────────────────────────────────────────────────────

def _label(surf, font, text, x, y, color=(245, 240, 230)):
    surf.blit(font.render(text, True, (0, 0, 0)), (x + 1, y + 1))
    surf.blit(font.render(text, True, color), (x, y))


def _sky(w, h, top, mid, bot):
    s = pygame.Surface((w, h))
    for i in range(h):
        t = i / max(1, h - 1)
        if t < 0.5:
            c = lerp_color(top, mid, t / 0.5)
        else:
            c = lerp_color(mid, bot, (t - 0.5) / 0.5)
        pygame.draw.line(s, c, (0, i), (w, i))
    return s


def main():
    pygame.font.init()
    font = pygame.font.SysFont("dejavusans", 15, bold=True)
    small = pygame.font.SysFont("dejavusans", 12)

    SW, SH = 1180, 760
    sheet = pygame.Surface((SW, SH))
    sheet.fill((30, 26, 32))
    _label(sheet, font, "BRIMSTONE  —  Group A take A2  —  charcoal-basalt & magma  —  round 3", 18, 12)
    _label(sheet, small, "the cracked-magma boulder-skull: a faceted hellfire-STONE skull (sockets+grin) sitting like a coal, carrying a basalt-column brazier",
            18, 32, (200, 196, 210))

    # — Cell A: boss at showcase scale, on a neutral panel.
    panel = pygame.Rect(18, 56, 360, 560)
    pygame.draw.rect(sheet, (48, 44, 54), panel, border_radius=8)
    pygame.draw.rect(sheet, (96, 88, 100), panel, 2, border_radius=8)
    boss, _ = build_brimstone(scale=1.7, ss=3)
    sheet.blit(boss, (panel.centerx - boss.get_width() // 2,
                      panel.bottom - boss.get_height() - 20))
    _label(sheet, font, "(a) BOSS  showcase scale", panel.x + 8, panel.y + 8)

    # — Cell B: the basalt column as a tileable PILLAR pair at TRUE obstacle scale.
    #   LEFT = a real 360x640 virtual-canvas slice at native 1x (exactly what
    #   scrolls in-game). RIGHT = a 2x zoom of the gap so the brazier cap + column
    #   banding + magma seam that must survive the 1x downscale are legible.
    panelB = pygame.Rect(394, 56, 360, 560)
    bg = _sky(panelB.w, panelB.h, (40, 110, 200), (90, 170, 230), (170, 220, 245))
    sheet.blit(bg, panelB.topleft)
    pygame.draw.rect(sheet, (96, 88, 100), panelB, 2, border_radius=8)
    _label(sheet, font, "(b) PROP -> PILLAR  @ TRUE obstacle scale", panelB.x + 8, panelB.y + 8)

    pw = PIPE_W + 2 * OVERHANG
    slice_h = 470
    slice_x = panelB.x + 26
    slice_y = panelB.y + 46
    gap_top = 168
    gap_h = 120
    top_h = gap_top
    bot_h = slice_h - gap_top - gap_h
    top_pillar = _column_pillar_obstacle(top_h, 3, flip=True)
    bot_pillar = _column_pillar_obstacle(bot_h, 3, flip=False)
    sheet.blit(top_pillar, (slice_x - 2, slice_y - 2))
    sheet.blit(bot_pillar, (slice_x - 2, slice_y + gap_top + gap_h - 2))
    pygame.draw.rect(sheet, (255, 255, 255), (slice_x - 4, slice_y - 4, pw + 8, slice_h + 8), 1)
    _label(sheet, small, "1x native (82px wide, as", slice_x - 2, slice_y + slice_h + 6, (20, 20, 30))
    _label(sheet, small, "it scrolls): hex column +", slice_x - 2, slice_y + slice_h + 22, (20, 20, 30))
    _label(sheet, small, "magma seam, brazier cap", slice_x - 2, slice_y + slice_h + 38, (20, 20, 30))

    zw, zh = pw, 150
    zoom_src = pygame.Surface((zw, zh), pygame.SRCALPHA)
    zoom_src.blit(top_pillar, (-2, -(gap_top - 70) - 2))
    zoom_src.blit(bot_pillar, (-2, gap_h + 70 - 2))
    zoom = pygame.transform.scale(zoom_src, (zw * 2, zh * 2))
    zx = panelB.x + 184
    zy = panelB.y + 70
    sheet.blit(zoom, (zx, zy))
    _label(sheet, small, "2x zoom of the gap:", zx - 4, zy - 16, (255, 255, 255))
    _label(sheet, small, "brazier fire wells", zx - 4, zy + zh * 2 + 6, (20, 20, 30))
    _label(sheet, small, "INTO the gap;", zx - 4, zy + zh * 2 + 22, (20, 20, 30))
    _label(sheet, small, "top<->bottom mirror", zx - 4, zy + zh * 2 + 38, (20, 20, 30))

    # — Cell C: 1x in-game-scale INSET on BOTH day and night skies.
    panelC = pygame.Rect(770, 56, 392, 560)
    pygame.draw.rect(sheet, (48, 44, 54), panelC, border_radius=8)
    pygame.draw.rect(sheet, (96, 88, 100), panelC, 2, border_radius=8)
    _label(sheet, font, "(c) 1x in-game scale  —  day / night legibility", panelC.x + 8, panelC.y + 8)

    boss1x, _ = build_brimstone(scale=0.66, ss=3)
    boss1x_n, _ = build_brimstone(scale=0.66, ss=3, night=True)
    day = _sky(180, 250, (40, 110, 200), (90, 170, 230), (170, 220, 245))
    night = _sky(180, 250, (5, 8, 30), (15, 25, 70), (35, 55, 115))
    for sx, sy in ((24, 40), (150, 26), (96, 70), (40, 120), (160, 150), (70, 200)):
        pygame.draw.circle(night, (220, 230, 255), (sx, sy), 1)

    dy = panelC.y + 40
    sheet.blit(day, (panelC.x + 14, dy))
    sheet.blit(night, (panelC.x + 200, dy))
    sheet.blit(boss1x, (panelC.x + 14 + 90 - boss1x.get_width() // 2,
                        dy + 250 - boss1x.get_height() - 6))
    sheet.blit(boss1x_n, (panelC.x + 200 + 90 - boss1x_n.get_width() // 2,
                          dy + 250 - boss1x_n.get_height() - 6))
    _label(sheet, small, "DAY", panelC.x + 14 + 6, dy + 6, (20, 20, 30))
    _label(sheet, small, "NIGHT", panelC.x + 200 + 6, dy + 6, (210, 220, 255))

    # — Grayscale silhouette check (face must read without the magma colour).
    gy = dy + 270
    gray = pygame.Surface((boss1x.get_width(), boss1x.get_height()), pygame.SRCALPHA)
    gray.blit(boss1x, (0, 0))
    arr = pygame.surfarray.pixels3d(gray)
    lum = (arr[:, :, 0] * 0.3 + arr[:, :, 1] * 0.59 + arr[:, :, 2] * 0.11).astype("uint8")
    arr[:, :, 0] = lum
    arr[:, :, 1] = lum
    arr[:, :, 2] = lum
    del arr
    gpanel = pygame.Rect(panelC.x + 14, gy, 360, 230)
    pygame.draw.rect(sheet, (120, 120, 128), gpanel, border_radius=6)
    sheet.blit(gray, (gpanel.centerx - gray.get_width() // 2,
                      gpanel.bottom - gray.get_height() - 8))
    _label(sheet, small, "grayscale: faceted crags + dark sockets + grin carry the skull (no magma reliance)",
            gpanel.x + 6, gpanel.y + 6, (30, 30, 30))

    # — Footer caption: the scary-cute thesis.
    _label(sheet, small,
           "scary-cute: charcoal basalt DOMINATES; sockets are empty ink cavities with embers pooled LOW; the magma grin glows like a quiet blush, not a glare.",
           18, SH - 124, (210, 206, 220))
    _label(sheet, small,
           "house style: FLAT triad facets, hard ink keyline from the alpha mask, magma seams = flat bright shape + OUTSIDE additive glow, ss=3.",
           18, SH - 104, (210, 206, 220))
    _label(sheet, small,
           "prop->pillar: the hexagonal BASALT COLUMN is the most literal pillar in the set — magma seam runs the full length, brazier fire is the cap.",
           18, SH - 84, (210, 206, 220))

    out_dir = os.path.join(os.path.dirname(__file__), "..", "docs",
                           "skybit_devil", "reapy_devil", "brimstone")
    out_dir = os.path.abspath(out_dir)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_3.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path)


if __name__ == "__main__":
    main()
