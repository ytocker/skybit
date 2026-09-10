"""Look-dev sheet for the Skybit BOSS — "UMIBOZU" (Leyak-epic set, concept #3).

The umi-bozu: a giant serene "sea-monk" that rises from the deep. Cuted down to
the Leyak lineage — a bodiless floating HEAD whose downward trailing stream IS
the pillar. Here the head is a smooth abyss-teal jelly-dome wearing the calm,
heavy-lidded face of a meditating monk; the body it drags is a glowing tentacle
curtain that becomes the obstacle shaft, capped at the gap by a modest bell-jelly.

House style this obeys (the elevated "epic" Leyak grammar):
  - CHIBI proportions — one oversized rounded jelly-dome head, NO torso/limbs;
    the tentacle curtain is the body/trail.
  - FLAT saturated fills + a hard 1-2px ink keyline (28,22,30). No within-shape
    gradients, no soft/feathered edges, no bevels.
  - Form via the TRIAD: dark-core ring -> flat fill -> top-left rim sheen lobe.
  - Scary-CUTE not grim: calm closed/heavy eyes + a tiny serene mouth on a vast
    smooth dome — placid, looming, never a snarl.
  - Silhouette POP via a 1px ink keyline grown from the alpha mask.
  - EPIC pass: render BIG at SS=6, then smoothscale down for crisp downscale —
    more tentacles, richer triad, stronger glow than the source Leyak.

Palette read (pinned in brief): abyss teal-black body (COOL — clear of
Tzitzimitl's indigo); warm-amber biolum confined to SMALL DOTS only, never a
body wash. The dome-vs-curtain value split + the dotted-curtain shape carry the
read independent of hue.

Prop -> pillar mirror: the tentacle CURTAIN is the pillar. A tileable band of 6
straight tentacles (sucker-dot + biolum-dot cadence) = the repeatable PILLAR
BODY; a modest bell-jelly (~shaft+30%) = the detachable GAP-EDGE CAP glowing at
the gap. Naturally vertical + symmetric — clean mirror, no top-heavy cap.

    SDL_VIDEODRIVER=dummy PYTHONPATH=/home/user/skybit python docs/skybit_devil/batch2/leyak_epic/umibozu/render_umibozu.py
"""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from game.draw import _shade_c, lerp_color, make_glow_surface
from game.config import PIPE_W


pygame.init()

# ── PINNED PALETTE (umibozu) ─────────────────────────────────────────────────
# Abyss teal-black dome — cool, deep, distinct from any indigo/violet boss. The
# body is the VALUE-LOW cool mass; the warm amber biolum sits ONLY inside small
# discrete dots, so the contained warm/cool split is the accessibility tell.
BODY        = (28, 78, 84)      # abyss teal fill (deep cool blue-green)
BODY_DK     = (14, 44, 52)      # darker abyss shade (dark-core ring / hollows)
BODY_SHEEN  = (96, 168, 168)    # cool sea-foam rim sheen (top-left lit lobe)
BODY_DEEP   = (10, 30, 38)      # near-black abyss base (lowest value)

# Translucency band — a slightly lifted teal so the jelly-dome reads see-through
# without a gradient (a flat lighter inner band, not a soft wash).
JELLY       = (44, 110, 112)
JELLY_LT    = (72, 150, 148)

AMBER       = (255, 196, 96)    # warm-amber biolum — DOTS ONLY
AMBER_CORE  = (255, 238, 196)   # hot twinkle core inside the biggest dots
AMBER_DK    = (196, 132, 56)    # amber dot dark-core ring

INK         = (28, 22, 30)      # the house keyline
FACE_INK    = (18, 38, 44)      # eyes/mouth drawn in deep teal-ink, not pure ink


def _triad_circle(surf, cx, cy, r, col, *, sheen=True, sheen_d=30, sheen_col=None):
    """House form triad on a circle: dark-core ring -> flat fill -> top-left rim
    sheen. Sculpted volume while staying flat-shaded. `sheen_col` overrides the
    sheen so a cool sea-foam highlight can be used instead of a tinted fill."""
    pygame.draw.circle(surf, _shade_c(col, -28), (int(cx), int(cy)), int(r))
    pygame.draw.circle(surf, col, (int(cx), int(cy)),
                       max(1, int(r - max(1, r * 0.055))))
    if sheen:
        sc = sheen_col if sheen_col is not None else _shade_c(col, sheen_d)
        pygame.draw.circle(surf, sc,
                           (int(cx - r * 0.32), int(cy - r * 0.34)),
                           max(2, int(r * 0.30)))


INK_NIGHT   = (188, 226, 224)   # cool sea-foam keyline for night — a lifted-value
                                # rim so the teal-black dome edge survives on the
                                # midnight-blue sky (dark ink would vanish there).
                                # R3 lifts it ~25% brighter and grows it 2px so the
                                # silhouette reads on shape, not on amber alone.


def _add_outline(src, outline_color=(*INK, 235), width=1):
    """Grow a keyline from the alpha mask so the silhouette POPS on any sky (the
    parrot `_add_outline` recipe). On night the keyline is a lifted cool sea-foam
    tone, not dark ink, AND grown thicker (width=2) so the dome edge survives on
    the dark sky by shape. Returns a padded surface."""
    w, h = src.get_size()
    pad = width + 1
    out = pygame.Surface((w + pad * 2, h + pad * 2), pygame.SRCALPHA)
    mask = pygame.mask.from_surface(src, threshold=8)
    sil = mask.to_surface(setcolor=outline_color, unsetcolor=(0, 0, 0, 0))
    offs = [(dx, dy) for dx in range(-width, width + 1)
            for dy in range(-width, width + 1) if (dx, dy) != (0, 0)]
    for dx, dy in offs:
        out.blit(sil, (pad + dx, pad + dy))
    out.blit(src, (pad, pad))
    return out


def _biolum_dot(surf, cx, cy, r, ss, *, glow=True, night=False, core=True,
                glow_mult=1.0):
    """A single warm-amber biolum DOT — the ONLY place warm hue is allowed. A
    contained glow halo + a flat amber disc with a dark-core ring + (optionally) a
    hot twinkle core. Kept small + discrete so the warm never washes the cool body.
    `core=False` gives a flat amber point-glow (no bright ring-with-pupil read) —
    used for the brow constellation so the dots don't read as open eyes.
    `glow_mult` tightens the halo radius (the cap rim uses <1 so the dots stay
    discrete point-glows and never bloom into a Tzitzimitl-style corona)."""
    if glow:
        gr = int(r * (3.4 if night else 2.4) * glow_mult)
        gl = make_glow_surface(max(1, gr), AMBER, alpha_center=190 if night else 120,
                               falloff=2.0)
        surf.blit(gl, (int(cx - gr), int(cy - gr)), special_flags=pygame.BLEND_ADD)
    pygame.draw.circle(surf, AMBER_DK, (int(cx), int(cy)), max(1, int(r)))
    pygame.draw.circle(surf, AMBER, (int(cx), int(cy)), max(1, int(r * 0.78)))
    if core:
        pygame.draw.circle(surf, AMBER_CORE, (int(cx), int(cy)), max(1, int(r * 0.36)))


# ── one tentacle (a flat triad tapering ribbon) ──────────────────────────────

def _tentacle(surf, top_x, top_y, length, hw, ss, *, wave=0.0, phase=0.0,
              col=BODY, sucker_side=1, biolum=False, night=False, n_band=4):
    """A single dangling tentacle: a tapering cord that necks to a point, drawn as
    a hard flat triad shape (dark-core -> fill -> top-left sheen stripe). Sucker
    dots run down one inner edge; a couple of biolum dots twinkle if `biolum`.
    `wave` lets the creature's tentacles drift; the pillar passes wave=0 so the
    shaft tiles straight."""
    def _x_at(t):
        return top_x + wave * hw * math.sin(t * math.pi * 2.2 + phase) * (0.3 + 0.7 * t)

    def _hw_at(t):
        return hw * (1.0 - 0.78 * t)            # necks to a fine tip

    steps = 36
    left, right = [], []
    for i in range(steps + 1):
        t = i / steps
        x = _x_at(t)
        y = top_y + length * t
        w = _hw_at(t)
        left.append((x - w, y))
        right.append((x + w, y))
    shape = left + right[::-1]
    pygame.draw.polygon(surf, _shade_c(col, -28), [(int(x), int(y)) for x, y in shape])
    inner_l = [(x + ss, y) for x, y in left]
    inner_r = [(x - ss, y) for x, y in right]
    pygame.draw.polygon(surf, col,
                        [(int(x), int(y)) for x, y in (inner_l + inner_r[::-1])])
    # Top-left sheen stripe down the lit edge — the cool sea-foam rim.
    sheen_pts = [(int(x + ss * 1.3), int(y)) for x, y in left[::2]]
    if len(sheen_pts) >= 2:
        pygame.draw.lines(surf, BODY_SHEEN, False, sheen_pts, max(1, int(1.2 * ss)))

    # Sucker dots: small dark hollows marching down one inner edge — the tentacle
    # tell, drawn cool (no warm here).
    for i in range(n_band):
        t = (i + 0.6) / (n_band + 0.6)
        x = _x_at(t) + sucker_side * _hw_at(t) * 0.34
        y = top_y + length * t
        rr = max(1, _hw_at(t) * 0.30)
        pygame.draw.circle(surf, BODY_DEEP, (int(x), int(y)), int(rr))
        pygame.draw.circle(surf, _shade_c(col, 18),
                           (int(x - rr * 0.3), int(y - rr * 0.3)), max(1, int(rr * 0.42)))

    # Biolum dots — sparse, only on some tentacles, near the upper third where the
    # tentacle is fat enough to host a dot without becoming a wash.
    if biolum:
        for t in (0.30, 0.62):
            x = _x_at(t)
            y = top_y + length * t
            _biolum_dot(surf, x, y, max(2, _hw_at(t) * 0.42), ss, night=night)


# ── the tentacle curtain (creature trail + pillar body) ──────────────────────

def _tentacle_curtain(surf, cx, top_y, length, span, ss, *, wave=0.0, night=False,
                      n=6):
    """The hanging tentacle CURTAIN beneath the dome — up to 6 tentacles fanned
    across `span`, of alternating length so the hem reads organic, a few carrying
    biolum dots. This is both the creature's dragged body and the band that TILES
    for the pillar (passed wave=0, equal lengths there)."""
    for i in range(n):
        fx = (i + 0.5) / n - 0.5                # -0.5..0.5 across the span
        tx = cx + fx * span
        # Outer tentacles a touch shorter so the curtain hem is gently rounded.
        edge = abs(fx) * 2.0
        ln = length * (1.0 - 0.16 * edge)
        hw = span / n * 0.46
        # Stagger which tentacles glow so biolum stays SPARSE dots, not a row.
        biolum = i in (1, 4)
        col = BODY if i % 2 == 0 else _shade_c(BODY, -10)
        _tentacle(surf, tx, top_y, ln, hw, ss, wave=wave,
                  phase=i * 1.3, col=col, sucker_side=1 if i % 2 == 0 else -1,
                  biolum=biolum, night=night, n_band=5 if wave == 0 else 4)


# ── the serene sea-monk jelly-dome head ──────────────────────────────────────

def _head(surf, cx, cy, r, ss, *, night=False, tell=False):
    """The oversized serene jelly-dome head: a tall smooth abyss-teal dome, a
    flat lighter inner translucency band (jelly see-through, no gradient), a hard
    cool rim-sheen lobe on the pate, calm heavy-lidded closed eyes, a tiny placid
    mouth, and a sparse few biolum dots dotting the brow. Looming + calm — the
    scary-CUTE beat is the meditative stillness on a vast face. `tell` bakes a
    bolder low-res face mark for the 32px read."""
    body = _shade_c(BODY, 14) if night else BODY
    # Night lifts the sea-foam sheen so the rim-lit dome edge holds value on the
    # midnight-blue sky (teal-black-on-dark would otherwise lose the shape). R3
    # pushes the lift further (+64 vs R2's +40) — with the grown cool keyline this
    # carries the dome SILHOUETTE on shape, not on amber alone (the accessibility
    # requirement: the night chip must read with the amber mentally subtracted).
    sheen = _shade_c(BODY_SHEEN, 64) if night else BODY_SHEEN

    # Dome: a tall rounded jelly head — circle crown with an elongated lower jaw
    # so it reads as a heavy looming monk-pate, not a perfect ball.
    # Lower jaw bulge first (occluded by the crown dome).
    jaw = pygame.Rect(0, 0, int(r * 1.74), int(r * 1.62))
    jaw.center = (int(cx), int(cy + r * 0.42))
    pygame.draw.ellipse(surf, _shade_c(body, -28), jaw)
    pygame.draw.ellipse(surf, body, jaw.inflate(-int(r * 0.12), -int(r * 0.12)))

    # Crown dome triad — dark-core ring + flat fill ONLY. The pate sheen is a
    # single dedicated crescent (below), so the triad's own sheen disc is
    # suppressed to avoid a second softer crescent reading as a dent/blob.
    _triad_circle(surf, cx, cy, r, body, sheen=False)

    # Inner translucency band — a flat lighter teal arc band low on the dome so
    # the jelly reads see-through (hard-edged, NOT a soft gradient).
    jelly = _shade_c(JELLY, 10) if night else JELLY
    band = pygame.Rect(0, 0, int(r * 1.18), int(r * 0.92))
    band.center = (int(cx), int(cy + r * 0.50))
    pygame.draw.ellipse(surf, jelly, band)
    pygame.draw.ellipse(surf, _shade_c(jelly, 22),
                        band.inflate(-int(r * 0.34), -int(r * 0.44)))

    # ONE hard rim-sheen lobe on the pate: a single crisp sea-foam crescent hugging
    # the top-left of the dome arc. Built as a lit disc minus a body-colored bite so
    # it reads as one clean crescent — NO second body circle that dents the dome.
    # The bite is carved with the dome's OWN fill so the silhouette stays unbroken.
    sheen_cx, sheen_cy, sheen_r = cx - r * 0.30, cy - r * 0.42, r * 0.30
    pygame.draw.circle(surf, _shade_c(sheen, 12),
                       (int(sheen_cx), int(sheen_cy)), max(2, int(sheen_r)))
    # Carve the crescent: re-fill the inner side with body so a thin lit rim remains.
    pygame.draw.circle(surf, body,
                       (int(sheen_cx + sheen_r * 0.52), int(sheen_cy + sheen_r * 0.46)),
                       max(2, int(sheen_r * 0.86)))

    # — Eyes: calm CLOSED / heavy-lidded — two long downward-bowed lash arcs, NOT
    #   round bug-eyes. Serene meditation, the scary-cute placid beat.
    eye_dx = r * 0.42
    eye_y = cy + r * 0.04
    eye_hw = r * 0.34
    lw = max(2, int(2.0 * ss))
    for s in (-1, 1):
        ex = cx + s * eye_dx
        # A gentle closed-lid arc: a shallow downward curve (a calm ^ flipped).
        pts = []
        steps = 14
        for i in range(steps + 1):
            t = i / steps
            ax = ex - eye_hw + 2 * eye_hw * t
            # Lid dips in the middle -> a soft closed-eye droop.
            ay = eye_y - math.sin(t * math.pi) * r * 0.10
            pts.append((int(ax), int(ay)))
        # Soft lid shadow above the lash.
        pygame.draw.lines(surf, _shade_c(body, -20), False,
                          [(x, y - lw) for x, y in pts], max(1, int(1.4 * ss)))
        pygame.draw.lines(surf, FACE_INK, False, pts, lw)
        # A tiny calm lash tick at the outer corner.
        oc = pts[0] if s < 0 else pts[-1]
        pygame.draw.line(surf, FACE_INK, oc,
                         (oc[0] + s * int(r * 0.06), oc[1] + int(r * 0.05)),
                         max(1, int(1.4 * ss)))

    # — Brow: two faint calm brow arcs above the eyes (the monk serenity).
    for s in (-1, 1):
        bx = cx + s * eye_dx
        pygame.draw.arc(surf, _shade_c(body, -22),
                        (int(bx - eye_hw), int(eye_y - r * 0.34),
                         int(eye_hw * 2), int(r * 0.30)),
                        math.radians(20), math.radians(160), max(1, int(1.4 * ss)))

    # — Mouth: a tiny serene closed mouth — a short gentle line, slightly down at
    #   the corners (placid, contemplative; never a grin/snarl).
    mw = r * 0.26
    my = cy + r * 0.52
    mpts = []
    for i in range(11):
        t = i / 10
        ax = cx - mw + 2 * mw * t
        ay = my + math.sin(t * math.pi) * r * 0.05   # tiny downward bow
        mpts.append((int(ax), int(ay)))
    pygame.draw.lines(surf, FACE_INK, False, mpts, max(2, int(1.8 * ss)))

    # — Brow biolum constellation (DOTS only, the warm focal). TWO TINY flat amber
    # points sitting ON the brow ridge — emphatically NOT a second eye-pair. R3
    # makes these genuinely subordinate: shrunk hard, NO dark seat (that read as a
    # pupil), NO glow bloom (that swelled them to eye size), just a small flat amber
    # disc. They register as a faint biolum freckle pair, never an open-eye read;
    # the serene closed lids stay the dominant facial beat. Seated low on the brow
    # arc and in off the sheen foam so amber never vibrates on the cool highlight.
    brow_dots = [
        (cx - r * 0.15, cy - r * 0.22, r * 0.045),
        (cx + r * 0.17, cy - r * 0.22, r * 0.045),
    ]
    for bx, by, br in brow_dots:
        _biolum_dot(surf, bx, by, max(2, br), ss, glow=False, night=night,
                    core=False)

    if tell:
        # Baked low-res face tell so the 32px icon keeps a creature read: two bold
        # dark closed-lid bars + a bright biolum brow-dot.
        for s in (-1, 1):
            ex = cx + s * eye_dx
            pygame.draw.line(surf, FACE_INK, (int(ex - eye_hw), int(eye_y)),
                             (int(ex + eye_hw), int(eye_y)), max(2, int(2.4 * ss)))
        _biolum_dot(surf, cx, cy - r * 0.30, max(2, r * 0.09), ss,
                    glow=False, night=night, core=False)


# ── the whole creature: dome + tentacle curtain ──────────────────────────────

def build_umibozu(scale=1.0, ss=5, *, night=False, compact=False):
    """The full creature on a transparent surface: the serene jelly-dome up top,
    a tentacle curtain hanging straight beneath it. EPIC pass renders BIG at SS,
    then smoothscales down. `compact` is the gameplay/32px variant — head grown to
    dominate the budget, curtain shortened, a baked low-res face tell."""
    head_r = int(48 * scale) * ss
    curtain_mult = 1.05 if compact else 2.4
    curtain_len = int(head_r * curtain_mult)
    span = head_r * (1.5 if compact else 1.7)
    n = 6
    side_pad = int(16 * scale) * ss
    top_pad = int(16 * scale) * ss
    bot_pad = int(18 * scale) * ss

    head_cx_off = side_pad + int(span / 2) + head_r
    head_cy = top_pad + head_r * 1.02

    curtain_top_y = head_cy + head_r * 0.78
    feet_y = curtain_top_y + curtain_len

    W = int(head_cx_off * 2)
    H = int(feet_y + bot_pad)
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    cx = W // 2

    # Curtain first so the dome jaw occludes the tentacle roots (one body).
    _tentacle_curtain(surf, cx, curtain_top_y, curtain_len, span, ss,
                      wave=0.7 if compact else 1.0, night=night, n=n)
    _head(surf, cx, head_cy, head_r, ss, night=night, tell=compact)

    out_w = int(surf.get_width() / ss)
    out_h = int(surf.get_height() / ss)
    smallv = pygame.transform.smoothscale(surf, (out_w, out_h))
    oc = (*INK_NIGHT, 245) if night else (*INK, 235)
    return _add_outline(smallv, outline_color=oc, width=2 if night else 1)


# ── pillar pair (prop -> pillar mirror proof) ────────────────────────────────

OVERHANG = 12


def _curtain_column(surf, cx, top_y, bot_y, span, ss, *, night=False):
    """The repeatable PILLAR BODY: the tentacle curtain as a straight tiling shaft
    — 6 equal-length tentacles filling the post with a steady sucker-dot + biolum
    cadence. Drawn vertical (wave=0) so the band tiles cleanly top<->bottom."""
    length = bot_y - top_y
    n = 6
    hw = span / n * 0.46
    for i in range(n):
        fx = (i + 0.5) / n - 0.5
        tx = cx + fx * span
        col = BODY if i % 2 == 0 else _shade_c(BODY, -10)
        biolum = i in (1, 4)
        # Band count scales with length so dots keep a constant cadence as the
        # shaft tiles to any height.
        n_band = max(3, int(length / (hw * 3.0)))
        _tentacle(surf, tx, top_y, length, hw, ss, wave=0.0, col=col,
                  sucker_side=1 if i % 2 == 0 else -1, biolum=False,
                  night=night, n_band=n_band)
    # Biolum dots laid on a regular cadence down two columns so they tile and stay
    # sparse discrete dots, not a wash.
    cadence = max(2, int(length / (span * 0.55)))
    for col_i in (1, 4):
        fx = (col_i + 0.5) / n - 0.5
        tx = cx + fx * span
        for k in range(cadence):
            t = (k + 0.5) / cadence
            _biolum_dot(surf, tx, top_y + length * t, max(2, hw * 0.42), ss,
                        night=night)


def _bell_cap(surf, cx, cap_base_y, span, ss, *, point_up, night=False):
    """The detachable GAP-EDGE CAP: a MODEST bell-jelly (~shaft span +30%) sitting
    at the curtain's gap end, radiating amber biolum INTO the gap. `point_up`
    orients the bell so its dome faces the gap. Kept compact so the cap is never
    top-heavy vs the shaft."""
    d = -1 if point_up else 1
    bell_w = span * 1.28               # ~shaft +28% — modest, not a big lantern
    bell_h = bell_w * 0.56             # flatter dome so the cap isn't top-heavy
    by = cap_base_y + d * bell_h * 0.62

    body = _shade_c(BODY, 14) if night else BODY
    sheen = _shade_c(BODY_SHEEN, 40) if night else BODY_SHEEN

    # The bell dome — a flat triad half-ellipse with the dome facing the gap. A
    # short fringe of stubby tentacles trails out the back (away from the gap).
    dome = pygame.Rect(0, 0, int(bell_w), int(bell_h * 1.7))
    dome.center = (int(cx), int(by))
    pygame.draw.ellipse(surf, _shade_c(body, -28), dome)
    pygame.draw.ellipse(surf, body, dome.inflate(-int(bell_w * 0.10), -int(bell_h * 0.10)))
    # Cool inner translucency band low on the bell.
    jelly = _shade_c(JELLY, 10) if night else JELLY
    jb = pygame.Rect(0, 0, int(bell_w * 0.72), int(bell_h * 0.7))
    jb.center = (int(cx), int(by - d * bell_h * 0.18))
    pygame.draw.ellipse(surf, jelly, jb)
    # Hard rim sheen lobe on the gap-facing pate.
    pygame.draw.circle(surf, sheen,
                       (int(cx - bell_w * 0.16), int(by - d * bell_h * 0.34)),
                       max(2, int(bell_w * 0.16)))

    # Stubby trailing fringe out the BACK of the bell (away from the gap).
    fringe_y = by - d * bell_h * 0.62
    for s in (-2, -1, 0, 1, 2):
        fx = cx + s * bell_w * 0.16
        _tentacle(surf, fx, fringe_y, -d * bell_h * 1.1, bell_w * 0.05, ss,
                  wave=0.0, col=_shade_c(body, -6), biolum=False, night=night,
                  n_band=2)

    # Amber biolum DOTS at the gap-facing rim of the bell — the warm focal that
    # lanterns the gap, kept as a FEW discrete dots, NOT a full bright crown ring.
    # Thinned to 3 small de-cored point-glows hugging the rim (vs the dense R2 ring
    # that out-weighed the gap line and re-read top-heavy). Pulled INBOARD (0.26)
    # and shrunk so the amber never widens/crowns the modest bell silhouette.
    for ang_deg in (54, 90, 126):
        a = math.radians(ang_deg)
        rx = math.cos(a) * bell_w * 0.26
        ry = -d * (math.sin(a) * bell_h * 0.40 + bell_h * 0.06)
        _biolum_dot(surf, cx + rx, by + ry, max(2, bell_w * 0.036), ss,
                    night=night, core=False, glow_mult=0.55)


def _curtain_pillar_obstacle(height, ss, *, flip, night=False):
    """One tentacle-curtain PILLAR obstacle: the 6-tentacle curtain fills the post
    and a modest bell-jelly CAP sits at the GAP-facing edge, radiating amber INTO
    the gap. `flip=True` is the TOP pillar (cap at the bottom/gap edge, bell facing
    DOWN); `flip=False` is the BOTTOM pillar (cap at the top/gap edge, bell facing
    UP). Both mirror the same curtain body — clean vertical, no top-heavy cap."""
    bw = (PIPE_W + 2 * OVERHANG) * ss
    bh = max(1, int(height)) * ss
    surf = pygame.Surface((bw, bh), pygame.SRCALPHA)
    cx = bw // 2
    span = (PIPE_W - 6) * ss
    cap_band = int(46 * ss)
    if flip:
        _curtain_column(surf, cx, 0, bh - cap_band, span, ss, night=night)
        _bell_cap(surf, cx, bh - cap_band, span, ss, point_up=False, night=night)
    else:
        _curtain_column(surf, cx, cap_band, bh, span, ss, night=night)
        _bell_cap(surf, cx, cap_band, span, ss, point_up=True, night=night)
    out = pygame.transform.smoothscale(surf, (PIPE_W + 2 * OVERHANG, max(1, int(height))))
    oc = (*INK_NIGHT, 245) if night else (*INK, 235)
    return _add_outline(out, outline_color=oc, width=2 if night else 1)


# ── sheet composition ────────────────────────────────────────────────────────

def _label(surf, font, text, x, y, color=(238, 244, 244)):
    surf.blit(font.render(text, True, (0, 0, 0)), (x + 1, y + 1))
    surf.blit(font.render(text, True, color), (x, y))


def _sky(w, h, top, mid, bot, *, stars=False):
    s = pygame.Surface((w, h))
    for i in range(h):
        t = i / max(1, h - 1)
        if t < 0.5:
            c = lerp_color(top, mid, t / 0.5)
        else:
            c = lerp_color(mid, bot, (t - 0.5) / 0.5)
        pygame.draw.line(s, c, (0, i), (w, i))
    if stars:
        import random as _r
        rng = _r.Random(99)
        for _ in range(26):
            sx = rng.randint(0, w - 1)
            sy = rng.randint(0, int(h * 0.7))
            pygame.draw.circle(s, (220, 230, 255), (sx, sy), rng.choice((1, 1, 2)))
    return s


def _to_gray(src):
    g = pygame.Surface(src.get_size(), pygame.SRCALPHA)
    g.blit(src, (0, 0))
    arr = pygame.surfarray.pixels3d(g)
    lum = (arr[:, :, 0] * 0.3 + arr[:, :, 1] * 0.59 + arr[:, :, 2] * 0.11).astype("uint8")
    arr[:, :, 0] = lum
    arr[:, :, 1] = lum
    arr[:, :, 2] = lum
    del arr
    return g


def main():
    pygame.font.init()
    font = pygame.font.SysFont("dejavusans", 15, bold=True)
    small = pygame.font.SysFont("dejavusans", 12)

    SW, SH = 1040, 770
    sheet = pygame.Surface((SW, SH))
    sheet.fill((52, 56, 58))          # neutral grey bg
    _label(sheet, font,
            "UMIBOZU  —  Leyak-epic set #3  —  abyss sea-monk jelly-dome + tentacle curtain  —  round 3", 18, 12)
    _label(sheet, small,
            "R3 (subtractive): brow dots DE-EYED (shrunk ~40%, no bright cores, seated on the brow ridge); cap crown THINNED (3 small de-cored dots); night dome lifted (brighter foam sheen + 2px grown cool keyline) so the silhouette reads without amber.",
            18, 32, (190, 214, 212))

    # — Cell A: BIG hero, on an abyssal teal-black sky.
    panel = pygame.Rect(18, 56, 320, 660)
    bgA = _sky(panel.w, panel.h, (10, 30, 46), (16, 54, 70), (30, 92, 100))
    sheet.blit(bgA, panel.topleft)
    pygame.draw.rect(sheet, (90, 140, 140), panel, 2, border_radius=8)
    hero = build_umibozu(scale=1.7, ss=5)
    sheet.blit(hero, (panel.centerx - hero.get_width() // 2, panel.y + 56))
    _label(sheet, font, "(a) HERO  big scale (SS=5)", panel.x + 8, panel.y + 8)
    _label(sheet, small, "serene dome + heavy closed eyes + 6-tentacle curtain (amber DOTS)",
           panel.x + 8, panel.y + 28, (190, 230, 226))

    # — Cell B: curtain as a tileable PILLAR pair at TRUE obstacle scale (night),
    #   plus a 2x zoom on the cap band proving the bell-jelly lanterns the gap.
    panelB = pygame.Rect(352, 56, 330, 660)
    bg = _sky(panelB.w, panelB.h, (6, 12, 26), (10, 24, 44), (16, 46, 60), stars=True)
    sheet.blit(bg, panelB.topleft)
    pygame.draw.rect(sheet, (90, 140, 140), panelB, 2, border_radius=8)
    _label(sheet, font, "(b) PILLAR  @ TRUE scale  (NIGHT)", panelB.x + 8, panelB.y + 8)
    _label(sheet, small, "6-tentacle curtain tiles + bell-jelly cap (~shaft+30%)",
           panelB.x + 8, panelB.y + 28, (190, 230, 226))

    pw = PIPE_W + 2 * OVERHANG
    slice_h = 540
    slice_x = panelB.x + 22
    slice_y = panelB.y + 50
    gap_top = 178
    gap_h = 132
    top_h = gap_top
    bot_h = slice_h - gap_top - gap_h
    top_pillar = _curtain_pillar_obstacle(top_h, 4, flip=True, night=True)
    bot_pillar = _curtain_pillar_obstacle(bot_h, 4, flip=False, night=True)
    sheet.blit(top_pillar, (slice_x - 2, slice_y - 2))
    sheet.blit(bot_pillar, (slice_x - 2, slice_y + gap_top + gap_h - 2))
    pygame.draw.rect(sheet, (170, 210, 206), (slice_x - 4, slice_y - 4, pw + 8, slice_h + 8), 1)
    _label(sheet, small, "1x native (82px): curtain", slice_x - 2, slice_y + slice_h + 6, (200, 230, 226))
    _label(sheet, small, "tiles; bell lanterns gap", slice_x - 2, slice_y + slice_h + 22, (255, 220, 180))

    # 2x zoom of the cap band.
    cap_band = 46
    zw, zh = pw, 170
    zoom_src = pygame.Surface((zw, zh), pygame.SRCALPHA)
    top_anchor = 16
    zoom_src.blit(top_pillar, (-2, -(top_h - cap_band - top_anchor) - 2))
    zoom_gap = zh - 2 * cap_band - 2 * top_anchor
    bot_anchor = top_anchor + cap_band + zoom_gap
    zoom_src.blit(bot_pillar, (-2, bot_anchor - 2))
    zoom = pygame.transform.scale(zoom_src, (zw * 2, zh * 2))
    zx = panelB.x + 168
    zy = panelB.y + 116
    zbg = _sky(zw * 2, zh * 2, (6, 12, 26), (10, 22, 40), (14, 38, 54))
    sheet.blit(zbg, (zx, zy))
    pygame.draw.rect(sheet, (170, 210, 206), (zx - 1, zy - 1, zw * 2 + 2, zh * 2 + 2), 1)
    sheet.blit(zoom, (zx, zy))
    _label(sheet, small, "2x zoom: bell-jelly", zx - 2, zy - 16, (255, 255, 255))
    _label(sheet, small, "biolum-rims the gap", zx - 2, zy + zh * 2 + 6, (255, 220, 180))

    # — Cell C: TRUE 32px gameplay chip on day + night, plus a 4x audit + grayscale.
    panelC = pygame.Rect(696, 56, 326, 660)
    pygame.draw.rect(sheet, (40, 46, 48), panelC, border_radius=8)
    pygame.draw.rect(sheet, (90, 140, 140), panelC, 2, border_radius=8)
    _label(sheet, font, "(c) TRUE 32px gameplay chip", panelC.x + 8, panelC.y + 8)
    _label(sheet, small, "head-dominant compact / day + night sky", panelC.x + 8, panelC.y + 28,
           (190, 230, 226))

    # Compact gameplay creature, day + night, shown at a readable mid scale.
    boss_day = build_umibozu(scale=0.6, ss=5, compact=True)
    boss_night = build_umibozu(scale=0.6, ss=5, night=True, compact=True)
    day = _sky(150, 300, (60, 140, 215), (110, 185, 235), (180, 222, 246))
    night = _sky(150, 300, (6, 12, 26), (10, 24, 44), (18, 50, 64), stars=True)
    dy = panelC.y + 50
    sheet.blit(day, (panelC.x + 12, dy))
    sheet.blit(night, (panelC.x + 170, dy))
    sheet.blit(boss_day, (panelC.x + 12 + 75 - boss_day.get_width() // 2, dy + 8))
    sheet.blit(boss_night, (panelC.x + 170 + 75 - boss_night.get_width() // 2, dy + 8))
    _label(sheet, small, "DAY", panelC.x + 18, dy + 6, (16, 28, 40))
    _label(sheet, small, "NIGHT", panelC.x + 176, dy + 6, (255, 220, 180))

    # TRUE 32px chips on day + night skies (the gameplay-scale read), then a 4x
    # nearest-neighbour blow-up + grayscale audit.
    gy = dy + 318
    _label(sheet, small, "TRUE 32px chip on day + night sky:", panelC.x + 12, gy - 2,
           (200, 226, 222))
    icon_src = build_umibozu(scale=1.0, ss=5, compact=True)
    sc32 = 32 / icon_src.get_height()
    icon32 = pygame.transform.smoothscale(
        icon_src, (max(1, int(icon_src.get_width() * sc32)), 32))

    chips = [
        (_sky(86, 86, (60, 140, 215), (110, 185, 235), (180, 222, 246)), "day"),
        (_sky(86, 86, (6, 12, 26), (10, 24, 44), (18, 50, 64), stars=True), "night"),
    ]
    sx = panelC.x + 12
    for bg_chip, lab in chips:
        chip = pygame.Rect(sx, gy + 16, 86, 86)
        sheet.blit(bg_chip, chip.topleft)
        pygame.draw.rect(sheet, (140, 170, 168), chip, 1, border_radius=4)
        sheet.blit(icon32, (chip.centerx - icon32.get_width() // 2,
                            chip.centery - icon32.get_height() // 2))
        _label(sheet, small, lab, chip.x + 4, chip.y + 2, (240, 244, 244))
        sx += 96

    # 4x blow-up + grayscale of the true-32 chip.
    blow = pygame.transform.scale(icon32, (icon32.get_width() * 4, icon32.get_height() * 4))
    bx = panelC.x + 12
    byy = gy + 118
    pygame.draw.rect(sheet, (60, 64, 66), (bx - 2, byy - 2, blow.get_width() + 4, blow.get_height() + 4),
                     border_radius=4)
    sheet.blit(blow, (bx, byy))
    _label(sheet, small, "4x blow-up of the 32px chip", bx, byy + blow.get_height() + 4,
           (200, 226, 222))

    gray = _to_gray(blow)
    gx = bx + blow.get_width() + 24
    pygame.draw.rect(sheet, (110, 114, 112), (gx - 2, byy - 2, gray.get_width() + 4, gray.get_height() + 4),
                     border_radius=4)
    sheet.blit(gray, (gx, byy))
    _label(sheet, small, "grayscale value check", gx, byy + gray.get_height() + 4, (24, 24, 24))

    # — Footer captions.
    _label(sheet, small,
           "STYLE: flat saturated fills, hard 1-2px ink keyline (28,22,30), dark-core -> flat-fill -> cool sea-foam rim-sheen triad, 1px grown outline, chibi, scary-CUTE.",
           18, SH - 40, (190, 214, 212))
    _label(sheet, small,
           "PILLAR: the 6-tentacle curtain IS the shaft (tiles top<->bottom w/ sucker + biolum-dot cadence); a modest bell-jelly (~shaft+30%) caps + biolum-rims the gap. On-axis mirror, no top-heavy cap.",
           18, SH - 22, (190, 214, 212))

    out_dir = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(out_dir, "round_3.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path)


if __name__ == "__main__":
    main()
