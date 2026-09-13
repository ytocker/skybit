"""Look-dev sheet for the Skybit BOSS — "TEHOM-NO-TAMAGO" (Umibozu-versions #5).

The cosmic outlier of the abyssal brood: a vertical SPIRAL EGG. Not a creature
with a face stuck on a body — the egg IS the body. The shell is a deep
teal-indigo backdrop held intentionally LOW in value so it never twins the
teal-black source Umibozu; the read is carried by a single continuous bone-cream
WHORL ridge spiralling up the shell (the eye lands on the spiral) and a sour
embryo-GREEN crack that fractures across it. One curious baby slit-eye blinks
out through the crack — impossibly cute, and what's coiled inside is the end of
the world.

House style this obeys (the elevated "epic" Umibozu-versions grammar):
  - CHIBI proportions — one oversized rounded egg, no torso/limbs. The egg is
    everything; the birth-cord tether is the dragged body / pillar.
  - FLAT saturated fills + a hard 1-2px ink keyline (20,28,36). No within-shape
    gradients, no soft/feathered edges, no bevels.
  - Form via the TRIAD: dark-core ring -> flat fill -> top-left rim sheen lobe.
  - Scary-CUTE not grim: one round, glossy, curious baby slit-eye peering through
    the crack — wide and innocent on a vast cosmic shell.
  - Silhouette POP via a 1px ink keyline grown from the alpha mask.
  - EPIC pass: render BIG at SS=6, then smoothscale down for a crisp downscale —
    a richer whorl, a hotter crack, a stronger glow than a flat egg would carry.

RE-SPEC obeyed: shell relief = a SINGLE CONTINUOUS LOGARITHMIC SPIRAL whorl
(equiangular, r = a*e^(b*theta) — each turn grows by a fixed factor), explicitly
distinct from Hamaguri's bold RADIATING fan-ribs. The dark shell value is held
LOW so the bone whorl + green crack carry the read and the egg never twins the
teal-black source Umibozu's smooth jelly-dome.

Palette pins: deeper/sourer embryo-GREEN crack (150,206,140) sits apart from
Hamaguri's PALER/greyer mirage pearl-green (170,222,186). The shell teal-indigo
is backdrop only; bone-cream is the brightest structural read.

Prop -> pillar mirror: the BIRTH-CORD / kelp-tether is the pillar — a knotted
cord shaft with a barnacle-cluster per repeat (the repeatable PILLAR BODY); a
small cracked shell-shard EGG-STONE (~shaft+30%) caps the gap edge, leaking one
green glow line into the gap.

    SDL_VIDEODRIVER=dummy PYTHONPATH=/home/user/skybit python docs/skybit_devil/batch2/umibozu_versions/tehom/render_tehom.py
"""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from game.draw import _shade_c, lerp_color, make_glow_surface
from game.config import PIPE_W


pygame.init()

# ── PINNED PALETTE (tehom) ────────────────────────────────────────────────────
# Deep teal-indigo shell — held BACK as a low-value BACKDROP so it cannot twin
# the teal-black source Umibozu. It is the cool mass the bright structure reads
# against, never the focal itself. R1 read too PALE, so the flat fill is dropped
# to the near-black shade and the old (46,66,84) is demoted to a thin rim-only
# accent — the body is now genuinely dark and the bone whorl + green crack are
# the sole bright masses (AD directive 4).
SHELL       = (32, 48, 64)      # deep teal-indigo shell fill (dark backdrop)
SHELL_DK    = (22, 34, 47)      # near-black shade (dark-core ring / hollows)
SHELL_DEEP  = (14, 24, 36)      # lowest abyss value (crack seams, deep recesses)
SHELL_RIM   = (52, 74, 94)      # the only lifted teal — a thin top-left rim sliver

# Bone-cream WHORL ridge — THE bright structural read. The eye lands on the
# single continuous spiral; this is the lightest value on the egg.
BONE        = (214, 206, 182)   # bone-cream whorl ridge (brightest structural)
BONE_DK     = (150, 146, 128)   # whorl dark-core / shaded underside of the ridge
BONE_LT     = (238, 232, 214)   # hot lit crest of the whorl (top-left rim sheen)

# Abyss embryo-GREEN crack glow — the DEEPER / SOURER green, pinned apart from
# Hamaguri's paler greyer mirage pearl-green. The sole emissive focal.
GREEN       = (150, 206, 140)   # embryo-green crack glow
GREEN_HOT   = (206, 244, 188)   # hot white-green core inside the crack / iris
GREEN_DK    = (78, 130, 84)     # sour-green dark seat (crack lip, eye rim)

# Barnacle bone-grey — the cord's encrusting clusters (cooler/greyer than the
# whorl bone so the two never read as the same material).
BARN        = (170, 172, 164)   # barnacle bone-grey
BARN_DK     = (108, 112, 108)   # barnacle dark-core

INK         = (20, 28, 36)      # the house keyline (deep teal-ink)

# Night keyline: a lifted cool bone tone so the low-value teal-indigo shell edge
# survives on the midnight-blue sky (dark ink would vanish there), grown 2px so
# the silhouette reads on shape, not on the green crack alone.
INK_NIGHT   = (198, 210, 214)


def _add_outline(src, outline_color=(*INK, 235), width=1):
    """Grow a keyline from the alpha mask so the silhouette POPS on any sky (the
    parrot `_add_outline` recipe). On night the keyline is a lifted cool bone
    tone, not dark ink, AND grown thicker so the low-value shell edge survives on
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


def _green_glow(surf, cx, cy, r, *, night=False, alpha=None, mult=1.0):
    """A contained embryo-green glow halo — the ONLY emissive in the design. Kept
    tight (falloff 2.0) so it lanterns the crack/eye without blooming into a
    star-corona that would crown the egg. Night pushes the alpha + radius so the
    green still reads on the midnight sky."""
    gr = max(2, int(r * (3.0 if night else 2.1) * mult))
    a = alpha if alpha is not None else (190 if night else 120)
    gl = make_glow_surface(gr, GREEN, alpha_center=a, falloff=2.0)
    surf.blit(gl, (int(cx - gr), int(cy - gr)), special_flags=pygame.BLEND_ADD)


# ── the bone-cream spiral whorl ───────────────────────────────────────────────

def _spiral_whorl(surf, cx, cy, r, ss, *, night=False, turns=3.0, core=None):
    """The single continuous LOGARITHMIC (equiangular) whorl — the bright
    structural read and the design's distinctness pin. ONE unbroken bone-cream
    ribbon winding from the outer shell INWARD to a tight cosmic core:
    r = a*e^(b*theta), a real nautilus growth law — explicitly NOT Hamaguri's
    straight radiating fan-ribs. R1 read as separate crescents because the
    dark-core ribbon was offset far down-right and drawn full-width, fracturing
    the line; here the ribbon is rendered as ONE continuous chain of overlapping
    discs (so there are no gaps to read as crescent ends), the dark-core sits
    DIRECTLY UNDER the bone as a single hair-fatter shadow ribbon, and the crest
    is one continuous polyline — the coil is one stroke, end to end.

    Ribbon half-width tapers from fat at the open outer mouth to fine at the
    core, so the eye is dragged INWARD along the single line to the centre where
    the crack splits and the egg-tooth eye peers out."""
    bone    = _shade_c(BONE, 8) if night else BONE
    bone_dk = _shade_c(BONE_DK, 6) if night else BONE_DK
    bone_lt = _shade_c(BONE_LT, 6) if night else BONE_LT

    # Equiangular spiral, swept from the tight core OUT to the open mouth. Growth
    # factor ~6 across the whole sweep keeps each turn visibly larger than the
    # last (the read that says "spiral", not "concentric rings").
    theta_max = turns * 2 * math.pi
    b = math.log(6.0) / theta_max
    # The coil's tight inner end stops at the eye core (passed in) so the eye is
    # the centre the spiral winds DOWN to; it never overdraws the iris.
    a0 = core if core is not None else r * 0.060
    # Spiral centre IS the eye; squashed to the egg oval, never a fat circle.
    sx, sy = cx, cy

    steps = 220
    pts = []
    for i in range(steps + 1):
        th = theta_max * (i / steps)
        rad = a0 * math.exp(b * th)
        px = sx + math.cos(th + math.pi * 0.5) * rad * 0.82
        py = sy - math.sin(th + math.pi * 0.5) * rad * 1.02
        frac = i / steps                    # 0 at core, 1 at outer mouth
        hw = (r * 0.014 + r * 0.072 * frac)
        pts.append((px, py, hw))

    def _ribbon(col, dx, dy, wmul):
        # One continuous chain of overlapping discs — no segment ever ends with a
        # hard crescent cap; consecutive discs overlap so the stroke reads unbroken.
        for x, y, w in pts:
            pygame.draw.circle(surf, col, (int(x + dx), int(y + dy)),
                               max(1, int(w * wmul)))

    # Dark-core shadow ribbon, a hair fatter and DIRECTLY under the bone (tiny
    # down-right nudge only) — gives the ridge depth without splitting the line.
    _ribbon(bone_dk, ss * 0.35, ss * 0.5, 1.12)
    # Flat bone fill — the unbroken body of the ridge.
    _ribbon(bone, 0, 0, 0.92)
    # Top-left-lit crest — ONE continuous polyline riding the lit edge of the coil.
    crest = [(int(x - w * 0.30), int(y - w * 0.40)) for x, y, w in pts]
    if len(crest) >= 2:
        pygame.draw.lines(surf, bone_lt, False, crest, max(1, int(1.2 * ss)))


# ── the cosmic spiral egg (the whole creature) ────────────────────────────────

def _egg(surf, cx, cy, rx, ry, ss, *, night=False, tell=False):
    """The oversized cosmic spiral EGG: a tall teal-indigo oval shell (held LOW in
    value as a backdrop), a single bone-cream logarithmic whorl spiralling up it
    (the bright structural read), a sour embryo-green crack fracturing down from
    the core, and one curious round baby slit-eye blinking out through the crack —
    glossy and innocent on a vast cosmic shell. `tell` bakes a bolder low-res
    crack+eye mark for the 32px read."""
    shell    = _shade_c(SHELL, 10) if night else SHELL
    shell_dk = _shade_c(SHELL_DK, 6) if night else SHELL_DK
    rim      = _shade_c(SHELL_RIM, 8) if night else SHELL_RIM

    # — Shell oval triad: dark-core ring -> flat low-value fill. The egg is a tall
    #   pointed-top oval (the leviathan-egg silhouette), broad at the base.
    egg = pygame.Rect(0, 0, int(rx * 2), int(ry * 2))
    egg.center = (int(cx), int(cy))
    pygame.draw.ellipse(surf, shell_dk, egg)
    pygame.draw.ellipse(surf, shell, egg.inflate(-int(rx * 0.11), -int(ry * 0.11)))
    # Taper the crown so it reads egg (pointed top) not ball: a shell-coloured
    # wedge narrowing the upper third.
    crown = [
        (int(cx - rx * 0.62), int(cy - ry * 0.30)),
        (int(cx), int(cy - ry * 1.16)),
        (int(cx + rx * 0.62), int(cy - ry * 0.30)),
    ]
    pygame.draw.polygon(surf, shell, crown)
    pygame.draw.polygon(surf, shell_dk, [
        (int(cx - rx * 0.62), int(cy - ry * 0.30)),
        (int(cx - rx * 0.40), int(cy - ry * 0.66)),
        (int(cx), int(cy - ry * 1.16)),
    ])

    # The slit-eye sits at the spiral's TIGHT CORE — the coil winds inward to it,
    # so the eye reads as the cosmic centre the whorl spirals down to (not a
    # separate fried-egg disc bolted on). Compute its anchor first.
    eye_x = cx + rx * 0.04
    eye_y = cy + ry * 0.20
    eye_r = ry * 0.19

    # — The bone-cream spiral whorl: THE structural focal. Centred ON the eye so
    #   the single continuous coil visibly winds from the outer shell INWARD to
    #   the eye core — the distinctness gate vs Hamaguri's radiating fan-ribs.
    _spiral_whorl(surf, eye_x, eye_y, min(rx, ry) * 1.58, ss, night=night,
                  core=eye_r * 0.92)

    # — The embryo-green crack: a sour-green jagged fissure splitting DOWN the
    #   shell from near the whorl core, where the egg-tooth eye peers out. Drawn as
    #   a dark seam, a green glow inside, then a hot lightning-thin filament.
    # The crack ORIGINATES at the eye (the split where the egg-tooth eye peers
    # out) and leaks DOWN the shell as the main green fissure; a faint hairline
    # continues UP through the crown. The downward run is the dominant green leak.
    crack_pts = [
        (cx + rx * 0.05, cy - ry * 0.22),   # faint upper hairline (crown)
        (eye_x, eye_y),                      # the split AT the eye (origin)
        (cx + rx * 0.14, cy + ry * 0.46),
        (cx - rx * 0.04, cy + ry * 0.66),
        (cx + rx * 0.10, cy + ry * 0.84),
        (cx + rx * 0.0,  cy + ry * 0.98),
    ]
    # Glow first (under the seam) so the crack reads as LIGHT LEAKING out of the
    # fracture — strongest at the split by the eye, swelling on the downward leak,
    # so it reads as a leak rather than an even-lit slot.
    # Additive green glows stacked along the leak summed to near-WHITE (each
    # BLEND_ADD blit piling GREEN's channels past clamp) — recreating one zone
    # south the very halo r3 killed at the iris. Pulled per-point alpha + radius
    # down hard so the leak lanterns a contained SOUR-GREEN fissure that never
    # out-values the bone whorl.
    for gi, (gx, gy) in enumerate(crack_pts[2:]):
        falloff = 1.0 - 0.40 * (gi / max(1, len(crack_pts) - 3))
        _green_glow(surf, gx, gy, rx * (0.15 * falloff), night=night,
                    alpha=int((84 if night else 46) * falloff), mult=0.6)
    # Dark crack seam (the gap in the shell) — full run.
    seam = [(int(x), int(y)) for x, y in crack_pts]
    pygame.draw.lines(surf, SHELL_DEEP, False, seam, max(3, int(4.6 * ss)))
    # The DOWNWARD leak below the eye is the bright green fissure (the co-focal).
    lower = seam[1:]
    pygame.draw.lines(surf, GREEN, False, lower, max(2, int(2.8 * ss)))
    # Hot white-green filament kept ONLY to the short run nearest the eye-origin,
    # not the full downward leak — so the leak body stays sour-green instead of a
    # near-white lightning line down the belly.
    pygame.draw.lines(surf, GREEN_HOT, False, lower[:2], max(1, int(1.1 * ss)))
    # The upper crown crack stays a thin sour hairline (doesn't compete).
    pygame.draw.lines(surf, GREEN_DK, False, seam[:2], max(1, int(1.4 * ss)))
    # A couple of hairline branch cracks off the DOWNWARD seam (shell stress).
    for (bx, by), (ex, ey) in (
        (crack_pts[2], (cx - rx * 0.44, cy + ry * 0.36)),
        (crack_pts[3], (cx + rx * 0.42, cy + ry * 0.56)),
        (crack_pts[4], (cx - rx * 0.34, cy + ry * 0.78)),
    ):
        pygame.draw.line(surf, SHELL_DEEP, (int(bx), int(by)), (int(ex), int(ey)),
                         max(2, int(2.2 * ss)))
        pygame.draw.line(surf, GREEN_DK, (int(bx), int(by)), (int(ex), int(ey)),
                         max(1, int(1.0 * ss)))

    # — The curious baby slit-eye: ONE round glossy eye peering out through the
    #   widest point of the crack. Big innocent iris, a vertical cat-slit pupil
    #   (the leviathan-within tell), a bright catch-light. Scary-CUTE: the wide
    #   curious read with a slit that says something ancient is awake.
    bone    = _shade_c(BONE, 8) if night else BONE
    bone_lt = _shade_c(BONE_LT, 6) if night else BONE_LT
    # A HAIR-THIN bone lid ring framing the iris — only the rim, never a filled
    # bone disc. R2 flooded a near-white halo across the whole eye-zone (the
    # brightest mass on the egg); the AD's sole remaining blocker. Fix: the dark
    # shell re-owns the socket, the lid is a THIN cool bone-cream RING (a step
    # below white) that hugs the iris, and the biolum eye-glow is pulled tight +
    # cooled to the sour-green seat so it lanterns the slit without blooming.
    # The slit reads on CONTRAST (dark slit on bone-lit iris), not on a hot socket.
    pygame.draw.circle(surf, SHELL_DEEP, (int(eye_x), int(eye_y)),
                       max(2, int(eye_r * 1.18)))
    # Thin bone lid: drawn as a ring (dark fill re-stamped inside) so the bone is
    # a rim only — the dark shell value wins the area immediately around the lid.
    pygame.draw.circle(surf, BONE_DK, (int(eye_x), int(eye_y)), max(2, int(eye_r * 1.10)))
    pygame.draw.circle(surf, bone, (int(eye_x), int(eye_y)), max(2, int(eye_r * 1.04)))
    pygame.draw.circle(surf, SHELL_DEEP, (int(eye_x), int(eye_y)), max(2, int(eye_r * 0.96)))
    # Green-lit eyeball glow — biolum from within, but TIGHT (radius to the iris
    # footprint, cooled toward the sour-green seat) so it never blooms past the
    # lid onto the whorl/shell as a white halo.
    _green_glow(surf, eye_x, eye_y, eye_r * 0.66, night=night,
                alpha=110 if night else 72, mult=0.85)
    # The iris: a sour-green disc with a dark rim.
    pygame.draw.circle(surf, GREEN_DK, (int(eye_x), int(eye_y)), max(2, int(eye_r)))
    pygame.draw.circle(surf, GREEN, (int(eye_x), int(eye_y)), max(2, int(eye_r * 0.84)))
    # Hot core kept SMALL + tight to the slit so the iris reads sour-GREEN (not a
    # pale white-green wash). The pale GREEN_HOT is a sharp pip, not the eye body.
    pygame.draw.circle(surf, GREEN_HOT, (int(eye_x), int(eye_y)), max(1, int(eye_r * 0.26)))
    # Vertical cat-slit pupil — the leviathan-within tell. Pure ink, fat enough to
    # read as the dark sclera-slit at 32px against the bright green iris.
    slit_w = max(2, int(eye_r * 0.30))
    pygame.draw.ellipse(surf, INK,
                        (int(eye_x - slit_w * 0.5), int(eye_y - eye_r * 0.78),
                         slit_w, int(eye_r * 1.56)))
    # Glossy catch-light, top-left (the baby-cute beat) — a tiny crisp pip only.
    pygame.draw.circle(surf, GREEN_HOT,
                       (int(eye_x - eye_r * 0.34), int(eye_y - eye_r * 0.40)),
                       max(1, int(eye_r * 0.20)))

    # — One thin top-left rim SLIVER on the shell crown: the only lifted teal on
    #   the body. R1 used a big bright disc-crescent that lightened the whole egg;
    #   now it's a hair-thin lit edge so the shell stays a dark backdrop and the
    #   bone whorl + green crack remain the sole bright masses (AD directive 4).
    rim_pts = [
        (int(cx - rx * 0.52), int(cy - ry * 0.18)),
        (int(cx - rx * 0.30), int(cy - ry * 0.74)),
        (int(cx + rx * 0.04), int(cy - ry * 1.04)),
    ]
    pygame.draw.lines(surf, rim, False, rim_pts, max(2, int(2.4 * ss)))

    if tell:
        # Baked low-res tell for the 32px read: bolder DOWNWARD green leak + a
        # fatter green iris, then the dark slit RE-STAMPED on top so the curious
        # slit-eye charm focal survives the downscale (AD directive 5) instead of
        # washing to a green dot.
        pygame.draw.lines(surf, GREEN, False, lower, max(2, int(3.2 * ss)))
        pygame.draw.circle(surf, GREEN, (int(eye_x), int(eye_y)),
                           max(2, int(eye_r * 0.66)))
        pygame.draw.ellipse(surf, INK,
                            (int(eye_x - slit_w * 0.6), int(eye_y - eye_r * 0.74),
                             int(slit_w * 1.2), int(eye_r * 1.48)))


def build_tehom(scale=1.0, ss=5, *, night=False, compact=False):
    """The full cosmic spiral EGG on a transparent surface. EPIC pass renders BIG
    at SS then smoothscales down. `compact` is the gameplay/32px variant — the egg
    grown to dominate the budget with a baked low-res crack+eye tell."""
    rx = int(40 * scale) * ss
    ry = int(rx * 1.34)                     # tall egg
    side_pad = int(14 * scale) * ss
    top_pad = int(rx * 0.42)
    bot_pad = int(14 * scale) * ss

    W = int(rx * 2 + side_pad * 2)
    H = int(ry * 2 + top_pad + bot_pad)
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    cx = W // 2
    cy = top_pad + ry

    _egg(surf, cx, cy, rx, ry, ss, night=night, tell=compact)

    out_w = int(surf.get_width() / ss)
    out_h = int(surf.get_height() / ss)
    smallv = pygame.transform.smoothscale(surf, (out_w, out_h))
    oc = (*INK_NIGHT, 245) if night else (*INK, 235)
    return _add_outline(smallv, outline_color=oc, width=2 if night else 1)


# ── pillar pair (prop -> pillar mirror proof) ────────────────────────────────

OVERHANG = 12


def _barnacle(surf, cx, cy, r, ss, *, night=False, glow=False):
    """A single barnacle: a bone-grey volcano-cone with a dark aperture. The cord's
    encrusting tell. A few in the gap-facing cluster carry a green-lit aperture so
    the cord feels alive without becoming a wash."""
    barn    = _shade_c(BARN, 10) if night else BARN
    barn_dk = _shade_c(BARN_DK, 6) if night else BARN_DK
    pygame.draw.circle(surf, barn_dk, (int(cx), int(cy)), max(2, int(r)))
    pygame.draw.circle(surf, barn, (int(cx), int(cy)), max(1, int(r * 0.82)))
    # Top-left lit fleck.
    pygame.draw.circle(surf, _shade_c(barn, 24),
                       (int(cx - r * 0.30), int(cy - r * 0.30)), max(1, int(r * 0.30)))
    # Dark aperture (the open mouth at the cone tip).
    ar = max(1, int(r * 0.34))
    if glow:
        _green_glow(surf, cx, cy, r * 0.7, night=night, alpha=130 if night else 80,
                    mult=0.7)
        pygame.draw.circle(surf, GREEN_DK, (int(cx), int(cy)), ar)
        pygame.draw.circle(surf, GREEN, (int(cx), int(cy)), max(1, int(ar * 0.6)))
    else:
        pygame.draw.circle(surf, SHELL_DEEP, (int(cx), int(cy)), ar)


def _cord_column(surf, cx, top_y, bot_y, span, ss, *, night=False):
    """The repeatable PILLAR BODY: the birth-cord / kelp-tether as a straight
    tiling shaft — a knotted twin-strand cord with a barnacle-cluster per repeat.
    Drawn vertical so the band tiles cleanly top<->bottom. The two strands cross
    at each knot node, and a barnacle cluster encrusts each knot — the per-repeat
    cadence."""
    length = bot_y - top_y
    hw = span * 0.30                        # cord half-width (twin strands inside)
    # Knot cadence: one knot+cluster per ~1.8 spans so it reads as a regular repeat.
    period = max(span * 1.6, 1)
    n_knot = max(2, int(length / period))
    seg = length / n_knot

    barn    = _shade_c(BARN, 10) if night else BARN

    # Twin strands weaving down the shaft — two sinusoids in antiphase so they
    # cross at each knot node (the braided birth-cord read).
    for strand in (0, 1):
        ph = strand * math.pi
        pts_dk, pts = [], []
        steps = 120
        for i in range(steps + 1):
            t = i / steps
            y = top_y + length * t
            x = cx + math.sin(t * n_knot * 2 * math.pi + ph) * hw * 0.62
            pts.append((x, y))
        sw = max(2, int(hw * 0.42))
        # Dark-core strand offset, then the lit strand.
        pygame.draw.lines(surf, SHELL_DK, False,
                          [(int(x + ss), int(y)) for x, y in pts], sw)
        pygame.draw.lines(surf, SHELL, False,
                          [(int(x), int(y)) for x, y in pts], sw)
        # Thin bone-grey sheen filament down the lit edge of each strand.
        pygame.draw.lines(surf, _shade_c(barn, 6), False,
                          [(int(x - sw * 0.4), int(y)) for x, y in pts],
                          max(1, int(1.0 * ss)))

    # Barnacle cluster + a tighter cord-binding at each knot node.
    for k in range(n_knot + 1):
        ky = top_y + seg * k
        # Cord binding: a short dark wrap band cinching the two strands.
        bind = pygame.Rect(0, 0, int(hw * 1.5), int(seg * 0.14))
        bind.center = (int(cx), int(ky))
        pygame.draw.ellipse(surf, SHELL_DK, bind)
        pygame.draw.ellipse(surf, SHELL, bind.inflate(-int(hw * 0.3), -int(seg * 0.04)))
        # Barnacle cluster encrusting the knot — a few cones of mixed size, one lit.
        cl = [(-0.5, -0.18, 0.42), (0.42, 0.0, 0.52), (-0.18, 0.30, 0.34),
              (0.16, -0.32, 0.30)]
        for ci, (ox, oy, sz) in enumerate(cl):
            _barnacle(surf, cx + ox * hw * 1.4, ky + oy * seg,
                      hw * sz, ss, night=night, glow=(ci == 1))


def _egg_stone_cap(surf, cx, cap_base_y, span, ss, *, point_up, night=False):
    """The detachable GAP-EDGE CAP: a small CRACKED SHELL-SHARD egg-stone
    (~shaft span +30%) sitting at the cord's gap end. R1 was a smooth pale ovoid
    with a straight green stick poking up — the AD's worst offender. This is now
    an ANGULAR faceted broken-egg silhouette (hard concave notches in the
    outline + a visible jagged split seam) whose green reads as a CRACK LEAKING
    light DOWNWARD into the gap (a short irregular tapering wedge, not an
    antenna). `point_up` orients the cracked face toward the gap. Kept compact so
    the cap is never top-heavy vs the cord shaft."""
    d = -1 if point_up else 1               # +1 bottom-pillar (gap above), -1 top
    stone_w = span * 1.30                   # ~shaft +30%
    stone_h = stone_w * 1.10
    sy = cap_base_y + d * stone_h * 0.52

    shell    = _shade_c(SHELL, 10) if night else SHELL
    shell_dk = _shade_c(SHELL_DK, 6) if night else SHELL_DK
    rim      = _shade_c(SHELL_RIM, 8) if night else SHELL_RIM
    hw = stone_w * 0.5
    hh = stone_h * 0.5

    # ANGULAR cracked-shard silhouette: a faceted polygon, broad at the anchored
    # (shaft) end, narrowing to a JAGGED broken lip at the gap-facing end. Two
    # hard concave notches bite the outline so it reads "broken shell", not pebble.
    # Local coords: gy-axis runs from anchored end (-d) to gap end (+d).
    def P(fx, fy):
        return (int(cx + fx * hw), int(sy + d * fy * hh))
    # fy: -1 anchored crown -> +1 gap-facing jagged lip.
    shard = [
        P(-0.62, -0.86),   # anchored shoulder L
        P(-0.92, -0.10),   # wide L
        P(-0.40,  0.18),   # concave NOTCH bite (in)
        P(-0.78,  0.52),   # jagged out
        P(-0.30,  0.70),   # broken lip step
        P(-0.46,  1.02),   # gap-facing fang L
        P( 0.06,  0.78),   # split valley (where the crack opens)
        P( 0.40,  1.06),   # gap-facing fang R
        P( 0.30,  0.64),   # broken lip step
        P( 0.86,  0.46),   # jagged out R
        P( 0.34,  0.16),   # concave NOTCH bite R (in)
        P( 0.90, -0.16),   # wide R
        P( 0.58, -0.84),   # anchored shoulder R
        P( 0.0,  -1.02),   # crown point (egg apex)
    ]
    pygame.draw.polygon(surf, shell_dk, shard)
    # Inner flat-fill facet, pulled in from the keyline edge.
    inner = [(int(cx + (px - cx) * 0.80), int(sy + (py - sy) * 0.82)) for px, py in shard]
    pygame.draw.polygon(surf, shell, inner)

    # The JAGGED SPLIT SEAM through the shard, opening at the gap-facing lip — a
    # dark zig-zag fissure (not a clean line). It runs from inside the shard out
    # to the broken lip, where it widens into the gap.
    split = [
        P(-0.04, -0.40),
        P( 0.14, -0.05),
        P(-0.06,  0.28),
        P( 0.12,  0.55),
        P(-0.02,  0.80),
    ]
    pygame.draw.lines(surf, SHELL_DEEP, False, split, max(2, int(2.6 * ss)))

    # A short bone-whorl HINT on the shard face (NOT a full spiral — the AD ruled
    # the cap should carry the crack + shard shape, the hero carries the spiral):
    # one small bone tick echoing the coil so the family reads.
    tick_cx, tick_cy = P(-0.18, -0.30)
    pygame.draw.arc(surf, BONE,
                    (int(tick_cx - hw * 0.34), int(tick_cy - hh * 0.30),
                     int(hw * 0.68), int(hh * 0.60)),
                    math.radians(150), math.radians(20), max(1, int(1.8 * ss)))

    # Green LEAK: a tapering irregular WEDGE of light bleeding DOWN out of the
    # split's open lip into the gap — wide at the fracture, narrowing as it falls.
    # No straight stick: the wedge is a tight column of glow discs that shrink as
    # they descend toward the gap edge, with a couple of off-axis jitter steps so
    # it reads as leaking, not beaming.
    lip_x, lip_y = P(0.04, 0.92)            # the open mouth of the split
    n_leak = 6
    jit = [0.0, 0.10, -0.06, 0.08, -0.04, 0.0]
    for i in range(n_leak):
        f = i / (n_leak - 1)                # 0 at lip -> 1 at gap edge
        gx = lip_x + jit[i] * stone_w
        gy = lip_y + d * f * stone_h * 0.78
        gr = stone_w * (0.28 - 0.20 * f)    # tapers narrower into the gap
        # Knocked back from R2 so the cap leak lanterns the gap without blooming
        # into a halo — the same value discipline applied to the hero eye-zone.
        _green_glow(surf, gx, gy, gr, night=night,
                    alpha=int((140 if night else 96) * (1.0 - 0.45 * f)))
    # The bright crack filament inside the leak — short, jagged, fading down.
    leak_seam = [(int(lip_x + jit[i] * stone_w * 0.6),
                  int(lip_y + d * (i / (n_leak - 1)) * stone_h * 0.72))
                 for i in range(n_leak)]
    pygame.draw.lines(surf, SHELL_DEEP, False, leak_seam, max(2, int(2.4 * ss)))
    pygame.draw.lines(surf, GREEN, False, leak_seam, max(1, int(1.6 * ss)))
    pygame.draw.lines(surf, GREEN_HOT, False, leak_seam[:3], max(1, int(0.8 * ss)))

    # Thin top-left rim sliver on the shard's anchored crown (only lifted teal).
    pygame.draw.line(surf, rim, P(-0.55, -0.70), P(-0.04, -1.0), max(2, int(2.0 * ss)))


def _cord_pillar_obstacle(height, ss, *, flip, night=False):
    """One birth-cord PILLAR obstacle: the knotted cord fills the post and a small
    cracked egg-stone CAP sits at the GAP-facing edge, leaking one green line INTO
    the gap. `flip=True` is the TOP pillar (cap at the bottom/gap edge); `flip=
    False` is the BOTTOM pillar (cap at the top/gap edge). Both mirror the same
    cord body — clean vertical, no top-heavy cap."""
    bw = (PIPE_W + 2 * OVERHANG) * ss
    bh = max(1, int(height)) * ss
    surf = pygame.Surface((bw, bh), pygame.SRCALPHA)
    cx = bw // 2
    span = (PIPE_W - 10) * ss
    cap_band = int(54 * ss)
    if flip:
        _cord_column(surf, cx, 0, bh - cap_band, span, ss, night=night)
        _egg_stone_cap(surf, cx, bh - cap_band, span, ss, point_up=False, night=night)
    else:
        _cord_column(surf, cx, cap_band, bh, span, ss, night=night)
        _egg_stone_cap(surf, cx, cap_band, span, ss, point_up=True, night=night)
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
        rng = _r.Random(77)
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
    sheet.fill((44, 50, 56))
    _label(sheet, font,
            "TEHOM-NO-TAMAGO  —  Umibozu-versions #5  —  abyssal leviathan-egg (vertical spiral egg)  —  round 3", 18, 12)
    _label(sheet, small,
            "R3 fix: eye-zone HALO knocked back — thin cool bone lid RING (not a hot bone disc), tight cooled biolum glow, smaller hot iris pip; dark shell re-owns the socket. Iris slit + bone whorl stay the bright masses. Cap leak trimmed.",
            18, 32, (196, 210, 206))

    # — Cell A: BIG hero on an abyssal teal-indigo sky.
    panel = pygame.Rect(18, 56, 320, 660)
    bgA = _sky(panel.w, panel.h, (12, 22, 40), (20, 40, 60), (34, 70, 88))
    sheet.blit(bgA, panel.topleft)
    pygame.draw.rect(sheet, (110, 130, 150), panel, 2, border_radius=8)
    hero = build_tehom(scale=1.7, ss=6)
    sheet.blit(hero, (panel.centerx - hero.get_width() // 2, panel.y + 60))
    _label(sheet, font, "(a) HERO  big scale (SS=6)", panel.x + 8, panel.y + 8)
    # Hero pulled up a touch — the crown is tall; centring leaves headroom.
    _label(sheet, small, "bone spiral whorl + sour-green crack + curious slit-eye",
           panel.x + 8, panel.y + 28, (200, 224, 218))

    # — Cell B: birth-cord PILLAR pair at TRUE obstacle scale (night), mirror
    #   visible, plus a 2x zoom on the cap band proving the egg-stone leaks a green
    #   line into the gap.
    panelB = pygame.Rect(352, 56, 330, 660)
    bg = _sky(panelB.w, panelB.h, (6, 12, 26), (10, 22, 40), (16, 42, 56), stars=True)
    sheet.blit(bg, panelB.topleft)
    pygame.draw.rect(sheet, (110, 130, 150), panelB, 2, border_radius=8)
    _label(sheet, font, "(b) PILLAR @ TRUE scale (NIGHT)", panelB.x + 8, panelB.y + 8)
    _label(sheet, small, "knotted birth-cord tiles + egg-stone cap (~shaft+30%)",
           panelB.x + 8, panelB.y + 28, (200, 224, 218))

    pw = PIPE_W + 2 * OVERHANG
    slice_h = 540
    slice_x = panelB.x + 22
    slice_y = panelB.y + 50
    gap_top = 178
    gap_h = 132
    top_h = gap_top
    bot_h = slice_h - gap_top - gap_h
    top_pillar = _cord_pillar_obstacle(top_h, 4, flip=True, night=True)
    bot_pillar = _cord_pillar_obstacle(bot_h, 4, flip=False, night=True)
    sheet.blit(top_pillar, (slice_x - 2, slice_y - 2))
    sheet.blit(bot_pillar, (slice_x - 2, slice_y + gap_top + gap_h - 2))
    pygame.draw.rect(sheet, (170, 200, 210), (slice_x - 4, slice_y - 4, pw + 8, slice_h + 8), 1)
    # Mirror axis line, made visible per the brief.
    pygame.draw.line(sheet, (150, 210, 150),
                     (slice_x + pw // 2, slice_y - 4),
                     (slice_x + pw // 2, slice_y + slice_h + 4), 1)
    _label(sheet, small, "1x native (82px): cord", slice_x - 2, slice_y + slice_h + 6, (200, 224, 218))
    _label(sheet, small, "tiles; egg-stone leaks gap", slice_x - 2, slice_y + slice_h + 22, (180, 230, 170))

    # 2x zoom of the cap band (mirror visible across the gap).
    cap_band = 54
    zw, zh = pw, 180
    zoom_src = pygame.Surface((zw, zh), pygame.SRCALPHA)
    top_anchor = 18
    zoom_src.blit(top_pillar, (-2, -(top_h - cap_band - top_anchor) - 2))
    zoom_gap = zh - 2 * cap_band - 2 * top_anchor
    bot_anchor = top_anchor + cap_band + zoom_gap
    zoom_src.blit(bot_pillar, (-2, bot_anchor - 2))
    zoom = pygame.transform.scale(zoom_src, (zw * 2, zh * 2))
    zx = panelB.x + 168
    zy = panelB.y + 110
    zbg = _sky(zw * 2, zh * 2, (6, 12, 26), (10, 20, 38), (14, 36, 50))
    sheet.blit(zbg, (zx, zy))
    pygame.draw.rect(sheet, (170, 200, 210), (zx - 1, zy - 1, zw * 2 + 2, zh * 2 + 2), 1)
    sheet.blit(zoom, (zx, zy))
    pygame.draw.line(sheet, (150, 210, 150), (zx + zw, zy), (zx + zw, zy + zh * 2), 1)
    _label(sheet, small, "2x zoom: egg-stone caps", zx - 2, zy - 16, (255, 255, 255))
    _label(sheet, small, "(mirror axis green) leak gap", zx - 2, zy + zh * 2 + 6, (180, 230, 170))

    # — Cell C: TRUE 32px gameplay chip on day + night, plus a mid-scale compact +
    #   a 4x audit + grayscale.
    panelC = pygame.Rect(696, 56, 326, 660)
    pygame.draw.rect(sheet, (38, 44, 50), panelC, border_radius=8)
    pygame.draw.rect(sheet, (110, 130, 150), panelC, 2, border_radius=8)
    _label(sheet, font, "(c) TRUE 32px gameplay chip", panelC.x + 8, panelC.y + 8)
    _label(sheet, small, "egg-dominant compact / day + night sky", panelC.x + 8, panelC.y + 28,
           (200, 224, 218))

    boss_day = build_tehom(scale=0.6, ss=6, compact=True)
    boss_night = build_tehom(scale=0.6, ss=6, night=True, compact=True)
    day = _sky(150, 300, (60, 140, 215), (110, 185, 235), (180, 222, 246))
    night = _sky(150, 300, (6, 12, 26), (10, 24, 44), (18, 50, 64), stars=True)
    dy = panelC.y + 50
    sheet.blit(day, (panelC.x + 12, dy))
    sheet.blit(night, (panelC.x + 170, dy))
    sheet.blit(boss_day, (panelC.x + 12 + 75 - boss_day.get_width() // 2, dy + 8))
    sheet.blit(boss_night, (panelC.x + 170 + 75 - boss_night.get_width() // 2, dy + 8))
    _label(sheet, small, "DAY", panelC.x + 18, dy + 6, (16, 28, 40))
    _label(sheet, small, "NIGHT", panelC.x + 176, dy + 6, (180, 230, 170))

    # TRUE 32px chips on day + night skies, then a 4x nearest-neighbour blow-up +
    # grayscale audit.
    gy = dy + 318
    _label(sheet, small, "TRUE 32px chip on day + night sky:", panelC.x + 12, gy - 2,
           (200, 224, 218))
    icon_day = build_tehom(scale=1.0, ss=6, compact=True)
    icon_night = build_tehom(scale=1.0, ss=6, night=True, compact=True)
    sc32 = 32 / icon_day.get_height()
    icon32_day = pygame.transform.smoothscale(
        icon_day, (max(1, int(icon_day.get_width() * sc32)), 32))
    icon32_night = pygame.transform.smoothscale(
        icon_night, (max(1, int(icon_night.get_width() * sc32)), 32))

    chips = [
        (_sky(86, 86, (60, 140, 215), (110, 185, 235), (180, 222, 246)), "day", icon32_day),
        (_sky(86, 86, (6, 12, 26), (10, 24, 44), (18, 50, 64), stars=True), "night", icon32_night),
    ]
    sx = panelC.x + 12
    for bg_chip, lab, icon in chips:
        chip = pygame.Rect(sx, gy + 16, 86, 86)
        sheet.blit(bg_chip, chip.topleft)
        pygame.draw.rect(sheet, (140, 165, 170), chip, 1, border_radius=4)
        sheet.blit(icon, (chip.centerx - icon.get_width() // 2,
                          chip.centery - icon.get_height() // 2))
        _label(sheet, small, lab, chip.x + 4, chip.y + 2, (240, 244, 244))
        sx += 96

    # 4x blow-up + grayscale of the true-32 DAY chip.
    blow = pygame.transform.scale(icon32_day, (icon32_day.get_width() * 4, icon32_day.get_height() * 4))
    bx = panelC.x + 12
    byy = gy + 118
    pygame.draw.rect(sheet, (58, 62, 66), (bx - 2, byy - 2, blow.get_width() + 4, blow.get_height() + 4),
                     border_radius=4)
    sheet.blit(blow, (bx, byy))
    _label(sheet, small, "4x blow-up of the 32px chip", bx, byy + blow.get_height() + 4,
           (200, 224, 218))

    gray = _to_gray(blow)
    gx = bx + blow.get_width() + 24
    pygame.draw.rect(sheet, (108, 112, 110), (gx - 2, byy - 2, gray.get_width() + 4, gray.get_height() + 4),
                     border_radius=4)
    sheet.blit(gray, (gx, byy))
    _label(sheet, small, "grayscale value check", gx, byy + gray.get_height() + 4, (24, 24, 24))

    # — Footer captions.
    _label(sheet, small,
           "STYLE: flat fills, hard 1-2px ink keyline (20,28,36), dark-core -> flat-fill -> top-left rim-sheen triad, 1px grown outline, chibi, scary-CUTE.",
           18, SH - 40, (196, 210, 206))
    _label(sheet, small,
           "PILLAR: the knotted BIRTH-CORD IS the shaft (twin braided strands + a barnacle-cluster per knot repeat); a small cracked EGG-STONE (~shaft+30%) caps + leaks one green line into the gap. On-axis mirror.",
           18, SH - 22, (196, 210, 206))

    out_dir = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(out_dir, "round_4.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path)


if __name__ == "__main__":
    main()
