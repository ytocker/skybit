"""Look-dev sheet for the Skybit BOSS batch-2 take — "LEYAK".

Bali's Leyak / SE-Asian penanggalan cuted down: a grinning detached HEAD flying
with a trailing comet of dangling viscera. Body-horror reframed as a goofy
floating jack-o-head (devil-skeleton hybrid: skull-grin head, no body) over a
long wavy viscera-RIBBON that streams straight down beneath it. The trailing
ribbon doubles as the pillar — heart-pendant lantern caps the gap.

House style this obeys (the warren-clown / Big-Reapy / Pyrecrown grammar):
  - CHIBI proportions — one oversized floating head, huge bug-eyes, wide
    tongue-lolling tusk-grin; NO torso, NO limbs. The ribbon-trail is the body.
  - FLAT saturated fills + hard 1-2px ink keylines (30,22,28). No within-shape
    gradients, no soft/feathered edges, no bevels.
  - Form via the TRIAD: dark-core ring -> flat fill -> top-left rim sheen.
  - Viscera lobes are HARD flat triad shapes (heart / ribbon / bead-drips),
    NOT gore-realistic — scary-CUTE, never grim.
  - Silhouette POP via a 1px ink keyline grown from the alpha mask.
  - SUPERSAMPLE then smoothscale.

Accessibility tell (pinned in brief): the trailing-RIBBON shape + the high
face/trail value contrast carry the read independent of hue.

Prop -> pillar mirror: the viscera-RIBBON itself is the pillar. The rib-bead
ribbon = the repeatable PILLAR BODY (rib-bead banding that tiles); a glowing
heart-pendant LANTERN = the detachable GAP-EDGE CAP radiating at the gap.
Naturally vertical + symmetric — clean mirror, no top-heavy risk.

Imports the real game colour/shape kit only; nothing under game/ is touched.
Headless + deterministic.

    SDL_VIDEODRIVER=dummy PYTHONPATH=/home/user/skybit python docs/skybit_devil/batch2/leyak/render_leyak.py
"""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from game.draw import _shade_c, lerp_color, make_glow_surface
from game.config import PIPE_W


pygame.init()

# ── PINNED PALETTE (batch-2 Leyak) — copied hex-exact from the locked brief ──
# Dominant family: ash-white face + hot-pink trail — the sole bodiless-head
# silhouette. Ash face is the VALUE-HIGH mass; the hot-pink/deep-rose viscera
# ribbon is the VALUE-LOW warm trail — that face/trail value split is the
# accessibility tell.
FACE        = (232, 224, 214)   # ash-white face fill
FACE_DK     = (168, 160, 160)   # cool-grey shade (dark-core ring / hollows)
FACE_SHEEN  = (255, 238, 232)   # top-left rim sheen

TRAIL       = (228, 84, 128)    # hot-pink trail accent (ribbon body fill)
TRAIL_DK    = (168, 44, 84)     # deep-rose shade (dark-core / seams)
BRUISE      = (120, 82, 140)    # violet bruise-rim (cool counter-accent)

AMBER       = (244, 196, 72)    # amber eye iris / lantern glow

INK         = (30, 22, 28)      # the house keyline
SHEEN       = (255, 238, 232)   # shared sheen tint

# Tooth/tusk reuse the ash family so the grin reads bone, not pink.
TUSK        = (244, 238, 230)
TUSK_DK     = (176, 168, 162)


def _triad_circle(surf, cx, cy, r, col, *, sheen=True, sheen_d=30):
    """House form triad on a circle: dark-core ring -> flat fill -> top-left rim
    sheen. Sculpted volume while staying flat-shaded."""
    pygame.draw.circle(surf, _shade_c(col, -46), (int(cx), int(cy)), int(r))
    pygame.draw.circle(surf, col, (int(cx), int(cy)),
                       max(1, int(r - max(1, r * 0.06))))
    if sheen:
        pygame.draw.circle(surf, _shade_c(col, sheen_d),
                           (int(cx - r * 0.32), int(cy - r * 0.34)),
                           max(2, int(r * 0.34)))


def _add_outline(src, outline_color=(*INK, 235)):
    """Grow a 1px dark keyline from the alpha mask so the silhouette POPS on any
    sky (the parrot `_add_outline` recipe). Returns a padded surface."""
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


# ── one viscera lobe (a flat triad teardrop/heart shape) ─────────────────────

def _lobe(surf, cx, cy, w, h, ss, col, *, tilt=0.0, heart=False):
    """A single dangling viscera lobe as a HARD flat triad shape (dark-core ->
    fill -> top-left sheen). `heart` draws a fat two-lobe heart (the signature
    pendant); otherwise a rounded teardrop-bead hanging point-DOWN. `tilt` leans
    the shape so the trail can wave instead of falling stiff. NOT gore-realistic
    — these are cute candy-bead organs."""
    def _shape(scale, c, dx=0.0, dy=0.0):
        pts = []
        n = 22
        for i in range(n + 1):
            a = math.pi * (i / n)              # 0..pi sweeps one side top->bottom
            if heart:
                # Two top humps necking to a point at the bottom (a valentine).
                hump = math.sin(a) * (1.0 + 0.55 * math.cos(2 * a))
                ww = (w * 0.5) * scale * max(0.12, hump)
                yy = -h * 0.5 * scale * math.cos(a)
            else:
                # Bead/teardrop: wide round top, tapering to a hanging point.
                t = i / n
                ww = (w * 0.5) * scale * math.sin(t * math.pi) * (1.0 - 0.45 * t) \
                    + (w * 0.5) * scale * 0.12 * (1 - t)
                yy = -h * 0.5 * scale + h * scale * t
            xx = ww
            lean = tilt * (yy)                 # straight lean, keeps it a flat shape
            pts.append((cx + dx + xx + lean, cy + dy + yy))
        for i in range(n, -1, -1):
            a = math.pi * (i / n)
            if heart:
                hump = math.sin(a) * (1.0 + 0.55 * math.cos(2 * a))
                ww = (w * 0.5) * scale * max(0.12, hump)
                yy = -h * 0.5 * scale * math.cos(a)
            else:
                t = i / n
                ww = (w * 0.5) * scale * math.sin(t * math.pi) * (1.0 - 0.45 * t) \
                    + (w * 0.5) * scale * 0.12 * (1 - t)
                yy = -h * 0.5 * scale + h * scale * t
            lean = tilt * yy
            pts.append((cx + dx - ww + lean, cy + dy + yy))
        pygame.draw.polygon(surf, c, [(int(px), int(py)) for px, py in pts])

    _shape(1.00, _shade_c(col, -46))           # dark-core ring
    _shape(0.86, col, dy=ss * 0.4)             # flat fill
    # Top-left rim sheen tucked high on the lit shoulder.
    _shape(0.34, _shade_c(col, 34), dx=-w * 0.16, dy=-h * 0.18)


# ── the trailing viscera ribbon (creature trail + the pillar body) ───────────

def _ribbon(surf, top_x, top_y, length, hw, ss, *, n_beads, wave=0.0, phase=0.0,
            heart_tip=False, night=False):
    """The hot-pink viscera RIBBON streaming straight DOWN: a soft S-waving
    central stalk strung with rib-bead lobes at a steady cadence (the band that
    TILES top<->bottom for the pillar), tapering as it falls. `heart_tip` hangs a
    glowing heart-pendant LANTERN at the bottom (the gap-edge cap business end).
    The bead cadence + the value-dark warm ribbon vs the value-light face are the
    accessibility read."""
    # Central S-wave stalk: a fat triad cord so the ribbon reads as one connected
    # streamer (not loose beads). Drawn as a tapering quad strip following a sine.
    def _x_at(t):
        return top_x + wave * hw * math.sin(t * math.pi * 2.4 + phase) * (0.35 + 0.65 * t)

    def _hw_at(t):
        return hw * (1.0 - 0.55 * t)           # ribbon necks down as it falls

    left, right = [], []
    steps = 40
    for i in range(steps + 1):
        t = i / steps
        x = _x_at(t)
        y = top_y + length * t
        w = _hw_at(t)
        left.append((x - w, y))
        right.append((x + w, y))
    stalk = left + right[::-1]
    pygame.draw.polygon(surf, TRAIL_DK, [(int(x), int(y)) for x, y in stalk])
    inner_l = [(x + ss, y) for x, y in left]
    inner_r = [(x - ss, y) for x, y in right]
    pygame.draw.polygon(surf, TRAIL,
                        [(int(x), int(y)) for x, y in (inner_l + inner_r[::-1])])
    # Top-left sheen stripe down the lit edge of the stalk.
    sheen_pts = [(int(x + ss * 1.2), int(y)) for x, y in left[::2]]
    if len(sheen_pts) >= 2:
        pygame.draw.lines(surf, _shade_c(TRAIL, 30), False, sheen_pts,
                          max(1, int(1.4 * ss)))
    # Violet bruise-rim seams crossing the stalk (the rib-bead banding) — a quiet
    # cool accent that also marks the tile cadence.
    for i in range(1, n_beads + 1):
        t = i / (n_beads + 0.5)
        x = _x_at(t)
        y = top_y + length * t
        w = _hw_at(t)
        pygame.draw.line(surf, BRUISE, (int(x - w), int(y)), (int(x + w), int(y)),
                         max(1, int(1.6 * ss)))

    # Rib-bead lobes alternating side to side off the stalk — the dangling organs.
    for i in range(n_beads):
        t = (i + 0.5) / n_beads
        x = _x_at(t)
        y = top_y + length * t
        scale = 1.0 - 0.50 * t                 # beads shrink down the trail
        bw = hw * 1.7 * scale
        bh = hw * 2.0 * scale
        side = 1 if i % 2 == 0 else -1
        # Beads hang slightly outboard + are tilted to follow the wave.
        bx = x + side * hw * 0.30
        col = TRAIL if i % 2 == 0 else _shade_c(TRAIL, -12)
        _lobe(surf, bx, y, bw, bh, ss, col, tilt=0.10 * side)

    # Heart-pendant lantern at the very tip (creature) — a fat glowing heart.
    if heart_tip:
        ht_y = top_y + length
        hw2 = hw * 2.2
        hh2 = hw * 2.4
        # AD r1: keep amber for the EYES (face is the hero). The pendant glows in
        # the warm HOT-PINK/ROSE family so two amber focals don't split attention
        # at small scale — only a tiny warm core twinkles inside the rose heart.
        gr = int(hw2 * (1.5 if night else 1.15))
        gl = make_glow_surface(gr, TRAIL, alpha_center=200 if night else 130,
                               falloff=2.2)
        surf.blit(gl, (int(top_x - gr), int(ht_y - gr)),
                  special_flags=pygame.BLEND_ADD)
        _lobe(surf, top_x, ht_y, hw2, hh2, ss, TRAIL, heart=True)
        # Small warm core — the will-o'-the-wisp twinkle, kept tiny so the eye
        # reads face -> trail -> cap, not cap-vs-eyes.
        pygame.draw.circle(surf, AMBER, (int(top_x), int(ht_y)),
                           max(1, int(hw2 * 0.13)))
        pygame.draw.circle(surf, (255, 244, 210), (int(top_x), int(ht_y)),
                           max(1, int(hw2 * 0.06)))


# ── the goofy floating jack-o-head ───────────────────────────────────────────

def _bat_ear(surf, cx, cy, r, ss, side):
    """A little bat-ear flap pinned at the side of the head — a small flat
    triad-lit leaf so the head reads devil-impish, not just a skull. AD r1: the
    flaps read as horns at mid scale, so they are ROUNDED + shortened (the tip
    pulled in and down ~15%) — the goofy beats the pointy-menacing."""
    s = side
    base = (cx + s * r * 0.84, cy - r * 0.06)
    tip = (cx + s * r * 1.20, cy - r * 0.48)     # shorter + less swept than r1
    bend = (cx + s * r * 1.16, cy - r * 0.20)    # a rounding mid-point on the back
    bot = (cx + s * r * 0.80, cy + r * 0.28)
    pygame.draw.polygon(surf, _shade_c(FACE, -46),
                        [base, tip, bend, bot])
    inner = [(base[0] - s * ss, base[1] + ss), (tip[0] - s * ss, tip[1] + ss),
             (bend[0] - s * ss, bend[1]), (bot[0] - s * ss, bot[1] - ss)]
    pygame.draw.polygon(surf, FACE, [(int(x), int(y)) for x, y in inner])
    # Inner-ear pink so the bat-flap reads warm + tied to the trail palette.
    inner2 = [(cx + s * r * 0.90, cy - r * 0.02),
              (cx + s * r * 1.06, cy - r * 0.30),
              (cx + s * r * 0.88, cy + r * 0.14)]
    pygame.draw.polygon(surf, _shade_c(TRAIL, -6),
                        [(int(x), int(y)) for x, y in inner2])


def _head(surf, cx, cy, r, ss, *, night=False, tongue=True):
    """The oversized floating jack-o-head: round ash skull-ish face, huge bug-eyes
    with amber irises, a wide tongue-lolling tusk-grin, little bat-ear flaps. The
    goofy GRIN + bug-eyes are the scary-cute beat — body-horror reframed as a
    friendly floating gourd-head. `tongue=False` drops the lolling tongue (AD r1:
    it blurs into the first trail-lobe at 32px). `night` lifts the ash value ~12%
    so the head stays a clean LIGHT blob against dark-blue night biomes."""
    # AD r1: keep the ash face a high-value pop on night skies — lift the fill +
    # sheen so the upper face never sinks into the dark-blue sky.
    face = _shade_c(FACE, 16) if night else FACE
    face_sheen = _shade_c(FACE_SHEEN, 8) if night else FACE_SHEEN

    # Bat-ear flaps behind the face so the dome occludes their roots.
    _bat_ear(surf, cx, cy, r, ss, -1)
    _bat_ear(surf, cx, cy, r, ss, 1)

    # Cranium dome (ash-white) — slightly squashed wide for a gourd/jack read.
    _triad_circle(surf, cx, cy, r, face)
    # A subtle wider lower-cheek bulge so it's a head, not a perfect ball.
    cheek = pygame.Rect(0, 0, int(r * 1.86), int(r * 1.5))
    cheek.center = (int(cx), int(cy + r * 0.30))
    pygame.draw.ellipse(surf, _shade_c(face, -46), cheek)
    inner = cheek.inflate(-int(r * 0.14), -int(r * 0.14))
    pygame.draw.ellipse(surf, face, inner)
    _triad_circle(surf, cx, cy, r, face)       # re-seat the dome over the cheek
    # A bright cranium-top sheen cap so the head crown catches light on night.
    pygame.draw.circle(surf, face_sheen,
                       (int(cx - r * 0.30), int(cy - r * 0.42)),
                       max(2, int(r * 0.30)))

    # — Eyes: HUGE round bug-eyes (the dominant face read). White sclera, big amber
    #   iris, fat ink pupil with a sheen catch — wide and goofy, not menacing.
    eye_dx = r * 0.44
    eye_dy = -r * 0.10
    eye_r = r * 0.42
    for s in (-1, 1):
        ex, ey = cx + s * eye_dx, cy + eye_dy
        # Violet bruise socket-ring (the cool accent + a faint penanggalan rot).
        pygame.draw.circle(surf, BRUISE, (int(ex), int(ey)), int(eye_r * 1.12))
        # White sclera.
        pygame.draw.circle(surf, (250, 248, 244), (int(ex), int(ey)), int(eye_r))
        pygame.draw.circle(surf, FACE_DK, (int(ex), int(ey)), int(eye_r), max(1, int(ss)))
        # Amber iris, slightly inward + down (cross-eyed goofy).
        ix, iy = ex + s * eye_r * 0.10, ey + eye_r * 0.16
        pygame.draw.circle(surf, _shade_c(AMBER, -30), (int(ix), int(iy)),
                           int(eye_r * 0.62))
        pygame.draw.circle(surf, AMBER, (int(ix), int(iy)), int(eye_r * 0.52))
        # Fat ink pupil + a bright top-left sheen catch (the cute glint).
        pygame.draw.circle(surf, INK, (int(ix), int(iy)), int(eye_r * 0.30))
        pygame.draw.circle(surf, (255, 255, 255),
                           (int(ix - eye_r * 0.16), int(iy - eye_r * 0.20)),
                           max(1, int(eye_r * 0.14)))

    # — Nose: tiny upturned heart/triangle hole between + below the eyes.
    nose_y = cy + r * 0.30
    nose = [(cx, nose_y - r * 0.06), (cx - r * 0.09, nose_y + r * 0.10),
            (cx + r * 0.09, nose_y + r * 0.10)]
    pygame.draw.polygon(surf, INK, [(int(x), int(y)) for x, y in nose])

    # — Mouth: a WIDE tusk-grin with a lolling tongue — the goofy jack-o-grin. A
    #   dark mouth seat, two big up-curling TUSKS at the corners, a row of little
    #   teeth, and a fat pink tongue flopping out the bottom-centre.
    grin_y = cy + r * 0.62
    grin_hw = r * 0.78
    grin_h = r * 0.40
    # Mouth seat — a wide upward-bowed dark band (a happy curve).
    seat_top, seat_bot = [], []
    n = 16
    for i in range(n + 1):
        xr = -1.0 + 2.0 * (i / n)
        x = cx + xr * grin_hw
        lift = grin_h * 0.55 * (xr * xr)        # corners ride up -> a grin
        seat_top.append((x, grin_y - grin_h * 0.5 + lift))
        seat_bot.append((x, grin_y + grin_h * 0.5 + lift * 0.4))
    seat = seat_top + seat_bot[::-1]
    pygame.draw.polygon(surf, INK, [(int(x), int(y)) for x, y in seat])

    # Lolling tongue first (behind the teeth band, flops out the bottom). AD r1:
    # TUCKED shorter so it no longer blurs into the first trail-lobe; dropped
    # entirely on the compact 32px icon (`tongue=False`).
    if tongue:
        tongue_y = grin_y + grin_h * 0.34
        tip = [
            (cx - grin_hw * 0.28, tongue_y),
            (cx + grin_hw * 0.28, tongue_y),
            (cx + grin_hw * 0.30, tongue_y + grin_h * 0.70),
            (cx, tongue_y + grin_h * 0.92),
            (cx - grin_hw * 0.30, tongue_y + grin_h * 0.70),
        ]
        pygame.draw.polygon(surf, TRAIL_DK, [(int(x), int(y)) for x, y in tip])
        inner_t = [(cx - grin_hw * 0.22, tongue_y + ss), (cx + grin_hw * 0.22, tongue_y + ss),
                   (cx + grin_hw * 0.24, tongue_y + grin_h * 0.64),
                   (cx, tongue_y + grin_h * 0.84),
                   (cx - grin_hw * 0.24, tongue_y + grin_h * 0.64)]
        pygame.draw.polygon(surf, TRAIL, [(int(x), int(y)) for x, y in inner_t])
        # Centre tongue groove.
        pygame.draw.line(surf, TRAIL_DK, (int(cx), int(tongue_y + grin_h * 0.16)),
                         (int(cx), int(tongue_y + grin_h * 0.80)), max(1, int(1.4 * ss)))

    # Little even teeth across the top of the grin.
    teeth = 7
    gap = grin_hw * 0.10
    tw = (grin_hw * 1.7 - gap * (teeth - 1)) / teeth
    th = grin_h * 0.42
    for i in range(teeth):
        tx = -grin_hw * 0.85 + i * (tw + gap)
        xr = (tx + tw * 0.5) / grin_hw
        ty = grin_y - grin_h * 0.5 + grin_h * 0.55 * (xr * xr) + ss
        rect = pygame.Rect(int(cx + tx + ss * 0.5), int(ty),
                           int(tw - ss * 0.5), int(th))
        pygame.draw.rect(surf, TUSK, rect, border_radius=max(1, int(1.2 * ss)))
        pygame.draw.rect(surf, TUSK_DK, rect, max(1, int(ss)),
                         border_radius=max(1, int(1.2 * ss)))

    # Two big up-curling TUSKS at the mouth corners (the devil tell).
    for s in (-1, 1):
        bx = cx + s * grin_hw * 0.86
        by = grin_y + grin_h * 0.10
        tusk = [
            (bx, by),
            (bx + s * grin_hw * 0.16, by - grin_h * 0.95),
            (bx + s * grin_hw * 0.34, by - grin_h * 0.70),
            (bx + s * grin_hw * 0.20, by + grin_h * 0.35),
        ]
        pygame.draw.polygon(surf, TUSK_DK, [(int(x), int(y)) for x, y in tusk])
        inner_k = [(bx + s * ss, by - ss), (bx + s * grin_hw * 0.14, by - grin_h * 0.85),
                   (bx + s * grin_hw * 0.28, by - grin_h * 0.62),
                   (bx + s * grin_hw * 0.18, by + grin_h * 0.22)]
        pygame.draw.polygon(surf, TUSK, [(int(x), int(y)) for x, y in inner_k])


# ── the whole creature: head + trailing ribbon, on one surface ───────────────

def _face_tell(surf, cx, cy, r, ss):
    """A baked LOW-RES face tell (AD r1 gate): two fat dark eye-dots + a single
    dark grin-bar stamped on the ash field, sized so smoothscale to true 32px
    PRESERVES a recognizable grinning-skull face instead of mushing to a speck.
    Drawn over the detailed face — at showcase scale it hides under the real eyes
    and grin; at icon scale it is the only thing that survives, so it carries the
    'this is a creature, not a rope' read on its own."""
    # Two bold dark eye-dots — wide-set, the dominant low-res mark.
    eye_dx = r * 0.46
    eye_dy = -r * 0.06
    eye_rr = r * 0.26
    for s in (-1, 1):
        ex, ey = cx + s * eye_dx, cy + eye_dy
        pygame.draw.circle(surf, INK, (int(ex), int(ey)), int(eye_rr))
        # An amber rim-pip so the EYE stays the sole warm focal (face is hero).
        pygame.draw.circle(surf, AMBER, (int(ex), int(ey)), int(eye_rr * 0.42))
    # A single wide dark grin-BAR — a fat upward-bowed curve, the one mouth mark
    # that survives downscale. Drawn as a thick arc-polygon.
    gw = r * 0.92
    gy = cy + r * 0.52
    gh = r * 0.20
    top, bot = [], []
    n = 12
    for i in range(n + 1):
        xr = -1.0 + 2.0 * (i / n)
        x = cx + xr * gw
        lift = gh * 1.30 * (xr * xr)             # corners ride up -> a grin curve
        top.append((x, gy - gh * 0.5 + lift))
        bot.append((x, gy + gh * 0.5 + lift))
    pygame.draw.polygon(surf, INK, [(int(x), int(y)) for x, y in (top + bot[::-1])])


def build_leyak(scale=1.0, ss=3, *, night=False, compact=False):
    """The full creature on its own transparent surface: the oversized jack-o-head
    up top, a viscera-ribbon streaming straight down beneath it tipped with a
    glowing heart-pendant. Returns an outlined surface. `night` lifts the head
    value + pendant glow so both read on a dark sky.

    `compact` is the GAMEPLAY / 32px-icon variant (AD r1 gate): the HEAD is grown
    to dominate ~55-60% of the vertical budget and the trail is cut to 3 short
    lobes, so the icon reads 'grinning skull on a short ribbon' — never inverts to
    a pink squiggle with a speck. The showcase variant keeps the longer 6-lobe
    streamer. Compact also bakes a low-res face tell + drops the tongue."""
    head_r = int(46 * scale) * ss
    # AD r1: privilege the head in the icon budget. Showcase keeps a long
    # streamer (~3.3x head); compact shortens the trail to ~1.1x the head radius
    # so the head wins the vertical budget at gameplay scale.
    trail_mult = 1.15 if compact else 2.85
    trail_len = int(head_r * trail_mult)
    n_beads = 3 if compact else 6
    side_pad = int(26 * scale) * ss        # room for ears + wave + bead lobes
    top_pad = int(18 * scale) * ss
    bot_pad = int(20 * scale) * ss         # room for the pendant glow halo

    head_cx_off = side_pad + head_r + int(8 * scale) * ss
    head_cy = top_pad + head_r * 1.06

    # Neck stub seat: the ribbon springs from just under the jaw.
    trail_top_y = head_cy + head_r * 1.18
    feet_y = trail_top_y + trail_len

    W = int(head_cx_off * 2)
    H = int(feet_y + bot_pad)
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    cx = W // 2

    # A short ragged neck-stump so the head reads severed (the detached-head tell),
    # drawn before the ribbon so the ribbon springs from inside it.
    stump_top = head_cy + head_r * 0.74
    stump = [
        (cx - head_r * 0.40, stump_top),
        (cx + head_r * 0.40, stump_top),
        (cx + head_r * 0.30, trail_top_y),
        (cx - head_r * 0.30, trail_top_y),
    ]
    pygame.draw.polygon(surf, TRAIL_DK, [(int(x), int(y)) for x, y in stump])
    inner = [(cx - head_r * 0.32, stump_top + ss), (cx + head_r * 0.32, stump_top + ss),
             (cx + head_r * 0.24, trail_top_y), (cx - head_r * 0.24, trail_top_y)]
    pygame.draw.polygon(surf, TRAIL, [(int(x), int(y)) for x, y in inner])

    # The trailing viscera ribbon. Compact uses a tighter wave so the few lobes
    # still read as a deliberate wavy ribbon, not noise, at 1x.
    hw = head_r * 0.34
    _ribbon(surf, cx, trail_top_y, trail_len, hw, ss,
            n_beads=n_beads, wave=0.7 if compact else 1.0,
            phase=0.6, heart_tip=True, night=night)

    # Head over the stump top. Tongue dropped in the compact icon so it never
    # blurs into the first trail-lobe.
    _head(surf, cx, head_cy, head_r, ss, night=night, tongue=not compact)
    if compact:
        _face_tell(surf, cx, head_cy, head_r, ss)

    out_w = int(surf.get_width() / ss)
    out_h = int(surf.get_height() / ss)
    smallv = pygame.transform.smoothscale(surf, (out_w, out_h))
    return _add_outline(smallv)


# ── pillar pair (prop -> pillar mirror proof) ────────────────────────────────

OVERHANG = 12


def _ribbon_column(surf, cx, top_y, bot_y, hw, ss):
    """The repeatable PILLAR BODY: the viscera-ribbon as a straight tiling shaft —
    a fat triad cord with rib-bead lobes at a steady cadence + violet bruise-rim
    rib seams (the band that mirrors top<->bottom). Drawn vertical (no wave) so it
    tiles cleanly along the post."""
    length = bot_y - top_y
    # Central cord.
    pygame.draw.rect(surf, TRAIL_DK, (int(cx - hw), int(top_y), int(2 * hw), int(length)))
    pygame.draw.rect(surf, TRAIL, (int(cx - hw + ss), int(top_y),
                                   int(2 * hw - 2 * ss), int(length)))
    pygame.draw.line(surf, _shade_c(TRAIL, 30), (int(cx - hw + 1.6 * ss), int(top_y)),
                     (int(cx - hw + 1.6 * ss), int(bot_y)), max(1, int(1.8 * ss)))
    # Rib-bead banding: a rib seam + a pair of side beads at a regular cadence so
    # the body tiles — the rib-bead band is what repeats top<->bottom.
    band = hw * 2.4
    n = max(2, int(length / band))
    band = length / n
    for i in range(n):
        by = top_y + (i + 0.5) * band
        # Violet rib seam across the cord.
        pygame.draw.line(surf, BRUISE, (int(cx - hw), int(by)), (int(cx + hw), int(by)),
                         max(1, int(1.8 * ss)))
        # A bead lobe bulging off each side.
        for s in (-1, 1):
            _lobe(surf, cx + s * hw * 0.7, by, hw * 1.5, hw * 1.7, ss,
                  TRAIL if s < 0 else _shade_c(TRAIL, -12), tilt=0.0)


def _heart_cap(surf, cx, cap_base_y, hw, ss, *, point_up, night=False):
    """The detachable GAP-EDGE CAP: a glowing heart-pendant LANTERN hanging off the
    ribbon end, radiating amber INTO the gap. `point_up` hangs the heart toward the
    gap (up for a bottom pillar). This is the ribbon-pillar 'business end' — it
    LANTERNS the gap (a will-o'-the-wisp twinkle, not a snuffer)."""
    d = -1 if point_up else 1
    # A short connective neck of two stacked beads from the shaft to the pendant.
    for k in (0.4, 1.1):
        ny = cap_base_y + d * hw * (0.6 + k * 1.4)
        _lobe(surf, cx, ny, hw * 1.3, hw * 1.5, ss, _shade_c(TRAIL, -10))
    # The big heart pendant lantern at the gap edge.
    hy = cap_base_y + d * hw * 3.8
    hw2 = hw * 2.4
    hh2 = hw * 2.6
    # Rose-family glow (mirrors the creature pendant) so the cap reads as the same
    # hot-pink heart-lantern, not a competing amber focal.
    gr = int(hw2 * (1.7 if night else 1.3))
    gl = make_glow_surface(gr, TRAIL, alpha_center=220 if night else 150, falloff=2.2)
    surf.blit(gl, (int(cx - gr), int(hy - gr)), special_flags=pygame.BLEND_ADD)
    # Heart oriented point toward the gap (point down for a top pillar reading up).
    if point_up:
        _lobe(surf, cx, hy, hw2, hh2, ss, TRAIL, heart=True)
    else:
        tmp = pygame.Surface((int(hw2 * 2.4), int(hh2 * 2.4)), pygame.SRCALPHA)
        _lobe(tmp, tmp.get_width() // 2, tmp.get_height() // 2, hw2, hh2, ss,
              TRAIL, heart=True)
        tmp = pygame.transform.flip(tmp, False, True)
        surf.blit(tmp, (int(cx - tmp.get_width() // 2), int(hy - tmp.get_height() // 2)),
                  special_flags=pygame.BLEND_RGBA_MAX)
    # Small warm twinkle core so the pendant reads as a lantern without becoming a
    # second amber focal that competes with the creature's eyes.
    pygame.draw.circle(surf, AMBER, (int(cx), int(hy)), max(1, int(hw2 * 0.14)))
    pygame.draw.circle(surf, (255, 244, 210), (int(cx), int(hy)), max(1, int(hw2 * 0.07)))


def _ribbon_pillar_obstacle(height, ss, *, flip, night=False):
    """One viscera-ribbon PILLAR obstacle: the rib-bead ribbon fills the post and a
    glowing heart-pendant lantern CAP sits at the GAP-facing edge, radiating INTO
    the gap. `flip=True` is the TOP pillar — cap at the bottom (gap) edge, heart
    pointing DOWN into the gap; `flip=False` is the BOTTOM pillar — cap at the TOP
    (gap) edge, heart pointing UP into the gap. Both mirror the same rib-bead body
    into a clean vertical ribbon-pillar lanterned at the gap."""
    bw = (PIPE_W + 2 * OVERHANG) * ss
    bh = max(1, int(height)) * ss
    surf = pygame.Surface((bw, bh), pygame.SRCALPHA)
    cx = bw // 2
    hw = 12 * ss
    cap_band = int(64 * ss)
    if flip:
        _ribbon_column(surf, cx, 0, bh - cap_band, hw, ss)
        _heart_cap(surf, cx, bh - cap_band, hw, ss, point_up=False, night=night)
    else:
        _ribbon_column(surf, cx, cap_band, bh, hw, ss)
        _heart_cap(surf, cx, cap_band, hw, ss, point_up=True, night=night)
    out = pygame.transform.smoothscale(surf, (PIPE_W + 2 * OVERHANG, max(1, int(height))))
    return _add_outline(out)


# ── sheet composition ────────────────────────────────────────────────────────

def _label(surf, font, text, x, y, color=(245, 240, 230)):
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

    SW, SH = 1180, 760
    sheet = pygame.Surface((SW, SH))
    sheet.fill((34, 28, 36))          # plum-charcoal so the warm trail reads warm
    _label(sheet, font,
            "LEYAK  —  batch2 DEVILISH  —  ash-white face + hot-pink viscera-trail  —  round 2", 18, 12)
    _label(sheet, small,
            "r2 gate FIX: the 32px icon is now HEAD-DOMINANT (~55-60% head / short 3-lobe ribbon) with a baked low-res face tell — reads 'grinning skull on a streamer' at 1x, never a pink squiggle + speck.",
            18, 32, (210, 180, 196))

    # — Cell A: creature at showcase scale, on a dusk sky (the long-streamer
    #   showcase variant — the compact gameplay icon lives in cell C).
    panel = pygame.Rect(18, 56, 360, 580)
    bgA = _sky(panel.w, panel.h, (60, 30, 70), (120, 60, 110), (210, 130, 150))
    sheet.blit(bgA, panel.topleft)
    pygame.draw.rect(sheet, (150, 90, 120), panel, 2, border_radius=8)
    boss = build_leyak(scale=1.85, ss=3)
    sheet.blit(boss, (panel.centerx - boss.get_width() // 2,
                      panel.y + 52))
    _label(sheet, font, "(a) CREATURE  showcase scale", panel.x + 8, panel.y + 8)
    _label(sheet, small, "head + 6-lobe trailing ribbon + rose heart pendant (amber EYES only)",
           panel.x + 8, panel.y + 28, (255, 220, 232))

    # — Cell B: ribbon as a tileable PILLAR pair at TRUE obstacle scale, on NIGHT,
    #   plus a 2x zoom re-aimed at the CAP band so the heart-lantern lighting the
    #   gap is proven.
    panelB = pygame.Rect(394, 56, 360, 580)
    bg = _sky(panelB.w, panelB.h, (8, 8, 32), (20, 18, 58), (44, 32, 78), stars=True)
    sheet.blit(bg, panelB.topleft)
    pygame.draw.rect(sheet, (150, 90, 120), panelB, 2, border_radius=8)
    _label(sheet, font, "(b) PROP -> PILLAR  @ TRUE scale  (NIGHT)", panelB.x + 8, panelB.y + 8)

    pw = PIPE_W + 2 * OVERHANG
    slice_h = 470
    slice_x = panelB.x + 24
    slice_y = panelB.y + 44
    gap_top = 150
    gap_h = 128
    top_h = gap_top
    bot_h = slice_h - gap_top - gap_h
    top_pillar = _ribbon_pillar_obstacle(top_h, 3, flip=True, night=True)
    bot_pillar = _ribbon_pillar_obstacle(bot_h, 3, flip=False, night=True)
    sheet.blit(top_pillar, (slice_x - 2, slice_y - 2))
    sheet.blit(bot_pillar, (slice_x - 2, slice_y + gap_top + gap_h - 2))
    pygame.draw.rect(sheet, (220, 180, 200), (slice_x - 4, slice_y - 4, pw + 8, slice_h + 8), 1)
    _label(sheet, small, "1x native (82px): rib-bead banding", slice_x - 2, slice_y + slice_h + 6, (235, 200, 215))
    _label(sheet, small, "tiles; heart-lanterns LIGHT the gap", slice_x - 2, slice_y + slice_h + 22, (255, 225, 200))

    cap_band = 64
    zw, zh = pw, 170
    zoom_src = pygame.Surface((zw, zh), pygame.SRCALPHA)
    top_anchor = 12
    zoom_src.blit(top_pillar, (-2, -(top_h - cap_band - top_anchor) - 2))
    zoom_gap = zh - 2 * cap_band - 2 * top_anchor
    bot_anchor = top_anchor + cap_band + zoom_gap
    zoom_src.blit(bot_pillar, (-2, bot_anchor - 2))
    zoom = pygame.transform.scale(zoom_src, (zw * 2, zh * 2))
    zx = panelB.x + 178
    zy = panelB.y + 96
    zbg = _sky(zw * 2, zh * 2, (8, 8, 32), (16, 14, 48), (30, 22, 64))
    sheet.blit(zbg, (zx, zy))
    pygame.draw.rect(sheet, (220, 180, 200), (zx - 1, zy - 1, zw * 2 + 2, zh * 2 + 2), 1)
    sheet.blit(zoom, (zx, zy))
    _label(sheet, small, "2x zoom of the CAP band:", zx - 2, zy - 16, (255, 255, 255))
    _label(sheet, small, "heart-pendant lantern", zx - 2, zy + zh * 2 + 6, (255, 225, 200))
    _label(sheet, small, "radiates INTO the gap", zx - 2, zy + zh * 2 + 22, (255, 225, 200))

    # — Cell C: the GAMEPLAY icon (compact, head-dominant) — leads with the true-32
    #   read on day/night, then the 4x audit + grayscale. This cell carries the
    #   round-2 gate: the head must dominate and read as a grinning skull at 1x.
    panelC = pygame.Rect(770, 56, 392, 580)
    pygame.draw.rect(sheet, (44, 38, 48), panelC, border_radius=8)
    pygame.draw.rect(sheet, (150, 90, 120), panelC, 2, border_radius=8)
    _label(sheet, font, "(c) GAMEPLAY ICON  —  HEAD-DOMINANT compact", panelC.x + 8, panelC.y + 8)
    _label(sheet, small, "head ~55-60% of the icon / short 3-lobe ribbon", panelC.x + 8, panelC.y + 28,
           (255, 220, 232))

    # The compact gameplay creature at in-game scale, day + night.
    boss1x = build_leyak(scale=0.62, ss=3, compact=True)
    boss1x_n = build_leyak(scale=0.62, ss=3, night=True, compact=True)
    day = _sky(180, 300, (40, 110, 200), (90, 170, 230), (170, 220, 245))
    night = _sky(180, 300, (8, 8, 32), (20, 18, 58), (44, 32, 78), stars=True)

    dy = panelC.y + 46
    sheet.blit(day, (panelC.x + 14, dy))
    sheet.blit(night, (panelC.x + 200, dy))
    sheet.blit(boss1x, (panelC.x + 14 + 90 - boss1x.get_width() // 2, dy + 8))
    sheet.blit(boss1x_n, (panelC.x + 200 + 90 - boss1x_n.get_width() // 2, dy + 8))
    _label(sheet, small, "DAY", panelC.x + 14 + 6, dy + 6, (20, 30, 26))
    _label(sheet, small, "NIGHT", panelC.x + 200 + 6, dy + 6, (255, 225, 200))

    # 32px silhouette row, the round-2 GATE: a true-32 head-dominant icon shown at
    # 1x FIRST (must read as a grinning skull on a short ribbon WITHOUT the
    # blow-up), then the 4x audit + grayscale. Built from the compact creature so
    # the head wins the budget instead of inverting to a speck.
    gy = dy + 312
    _label(sheet, small, "32px GATE: reads as a grinning skull on a short ribbon AT 1x:",
           panelC.x + 14, gy - 2, (235, 210, 220))
    icon_src = build_leyak(scale=1.0, ss=3, compact=True)
    target_h = 64
    sc = target_h / icon_src.get_height()
    icon = pygame.transform.smoothscale(
        icon_src, (max(1, int(icon_src.get_width() * sc)), target_h))
    icon32 = pygame.transform.smoothscale(
        icon_src, (max(1, int(icon_src.get_width() * (32 / icon_src.get_height()))), 32))
    swatches = [
        ((40, 110, 200), "day 1x"),
        ((44, 32, 78), "night 1x"),
        ((120, 60, 110), "dusk 1x"),
    ]
    sx = panelC.x + 14
    sw = 86
    for col, lab in swatches:
        chip = pygame.Rect(sx, gy + 16, sw, 84)
        pygame.draw.rect(sheet, col, chip, border_radius=4)
        # Show the true-32 icon at 1x (NOT scaled up) so the at-scale read is honest.
        sheet.blit(icon32, (chip.centerx - icon32.get_width() // 2,
                            chip.centery - icon32.get_height() // 2))
        _label(sheet, small, lab, chip.x + 4, chip.y + 2, (240, 240, 240))
        sx += sw + 10
    # True 32px on neutral + a 4x nearest-neighbour blow-up so the face tell is
    # auditable, plus the 64px in between for a mid read.
    chip = pygame.Rect(panelC.x + 14, gy + 112, 86, 84)
    pygame.draw.rect(sheet, (90, 90, 96), chip, border_radius=4)
    sheet.blit(icon32, (chip.centerx - icon32.get_width() // 2,
                        chip.centery - icon32.get_height() // 2))
    sheet.blit(icon, (chip.centerx + 22, chip.centery - icon.get_height() // 2))
    _label(sheet, small, "32 / 64px", chip.x + 4, chip.y + 2, (240, 240, 240))
    blow = pygame.transform.scale(icon32, (icon32.get_width() * 4, icon32.get_height() * 4))
    sheet.blit(blow, (panelC.x + 116, gy + 8))
    _label(sheet, small, "4x blow-up of the 32px icon (face tell baked)",
           panelC.x + 116, gy + 8 + blow.get_height() + 2, (235, 210, 220))
    # Grayscale value check beside the blow-up.
    gray = _to_gray(icon)
    chip = pygame.Rect(panelC.x + 290, gy + 112, 86, 84)
    pygame.draw.rect(sheet, (120, 124, 120), chip, border_radius=4)
    sheet.blit(gray, (chip.centerx - gray.get_width() // 2,
                      chip.centery - gray.get_height() // 2))
    _label(sheet, small, "grayscale", chip.x + 4, chip.y + 2, (24, 24, 24))

    # — Footer captions: r2 fixes + style + mirror.
    _label(sheet, small,
           "r2 fixes: head:trail rebalanced to ~55-60% head in the icon + 3-lobe trail; baked low-res face tell (eye-dots + grin-bar); night ash value lifted +12% w/ cranium sheen.",
           18, SH - 84, (210, 180, 196))
    _label(sheet, small,
           "amber kept for the EYES only (face is hero); pendant glows ROSE/hot-pink w/ a tiny warm core; tongue tucked shorter + dropped from the icon; bat-ears rounded + shortened ~15%.",
           18, SH - 64, (210, 180, 196))
    _label(sheet, small,
           "prop->pillar (kept ~as-is per AD): the rib-bead viscera-ribbon tiles as the shaft; a glowing heart-pendant lantern caps + LIGHTS the gap. Naturally vertical + symmetric — clean mirror.",
           18, SH - 44, (210, 180, 196))

    out_dir = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(out_dir, "round_2.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path)


if __name__ == "__main__":
    main()
