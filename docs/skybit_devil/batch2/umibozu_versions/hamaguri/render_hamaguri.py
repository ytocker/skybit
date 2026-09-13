"""Look-dev sheet for the Skybit BOSS — "HAMAGURI-SHINKIROU" (Umibozu-versions #4).

Hamaguri-shinkirou — the mirage clam: a serene old bivalve that hums a whole
drowned ghost-city out of its mouth. Cuted into the Umibozu epic lineage as the
ONLY HORIZONTAL-grin silhouette of the brood — two sea-rust shell halves hinged
at a WIDE horizontal split, the city exhaled as a pale pearl-green mirage rising
out of the gap between the lips.

House style this obeys (the elevated epic grammar):
  - CHIBI proportions — one big oversized clam, no torso/limbs. The mirage tower
    it breathes is the body/trail that becomes the pillar.
  - FLAT saturated fills + a hard 1-2px ink keyline (28,26,24). No within-shape
    gradients, no soft/feathered edges, no bevels.
  - Form via the TRIAD: dark-core ring -> flat fill -> top-left rim sheen.
  - Scary-CUTE not grim: heavy-lidded calm hinge-eyes + a serene exhaling mouth;
    the dread is the silent drowned city, not a snarl.
  - Silhouette POP via a 1px ink keyline grown from the alpha mask.
  - EPIC pass: render BIG at SS=5 then smoothscale for a crisp downscale.

Palette read (pinned in brief): brown-WARM sea-rust shell — NEVER teal. The lone
cool accent is the ghost PEARL-GREEN mirage glow (the PALER/greyer green, pinned
APART from Tehom's deeper sourer green). The warm-shell-vs-pale-mirage value +
hue split is the accessibility tell.

RE-SPEC pins:
  - Shell relief = bold RADIATING fan-ribs (distinct from Tehom's spiral whorl).
  - Body stays the ONLY HORIZONTAL-grin silhouette — the wide horizontal split is
    the whole distinctness; the shell halves must NOT round up into a vertical blob.

Prop -> pillar mirror: the exhaled mirage TOWER is the pillar. A translucent
pagoda shaft stacks one drowned-city tier per repeat (tileable PILLAR BODY); a
single mirage-pagoda roof finial (~shaft+30%) = the detachable GAP-EDGE CAP
glowing pearl-green into the gap. Naturally vertical + symmetric — clean mirror.

    SDL_VIDEODRIVER=dummy PYTHONPATH=/home/user/skybit python docs/skybit_devil/batch2/umibozu_versions/hamaguri/render_hamaguri.py
"""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from game.draw import _shade_c, lerp_color, make_glow_surface
from game.config import PIPE_W


pygame.init()

# ── PINNED PALETTE (hamaguri-shinkirou) ──────────────────────────────────────
# Sea-rust shell — warm brown, the value-anchored mass. The ONLY cool note is
# the pale pearl-green mirage; the warm-shell-vs-cool-mirage split is the tell.
SHELL       = (178, 142, 96)    # sea-rust shell fill (warm brown)
SHELL_DK    = (120, 86, 52)     # umber-shell shade (dark-core ring / hollows)
SHELL_DEEP  = (86, 60, 38)      # deepest umber (rib valleys / hinge socket)
PEARL       = (236, 224, 196)   # pearl-cream sheen (top-left lit rim, lip nacre)

# Ghost pearl-GREEN mirage — the PALER / greyer green (pinned apart from Tehom's
# deeper sourer crack-green). The single cool focal: the exhaled city + glow.
MIRAGE      = (170, 222, 186)   # ghost pearl-green mirage body
MIRAGE_LT   = (214, 242, 222)   # lifted mirage core (brightest pip)
MIRAGE_DK   = (108, 158, 132)   # mirage dark structure (souls / roof shade)

EYE         = (60, 72, 74)      # slate hinge-eye (cool-grey, calm heavy lid)
INK         = (28, 26, 24)      # the house keyline (warm near-black)
SHELL_INK   = (44, 32, 26)      # rib / facial ink drawn warm, not pure black

INK_NIGHT   = (228, 216, 184)   # warm pearl keyline for night — a lifted-value rim
                                # so the warm shell edge survives on the midnight
                                # sky (dark ink would vanish there), grown 2px so
                                # the silhouette reads on shape, not on glow alone.


def _add_outline(src, outline_color=(*INK, 235), width=1):
    """Grow a keyline from the alpha mask so the silhouette POPS on any sky (the
    parrot `_add_outline` recipe). On night the keyline is a lifted warm pearl
    tone, grown thicker, so the shell edge survives on dark sky by SHAPE — not on
    the mirage glow alone. Returns a padded surface."""
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


def _mirage_glow(surf, cx, cy, r, *, night=False, mult=1.0):
    """A contained pearl-green mirage halo — the single cool focal. Kept additive
    + tightish so it lanterns the gap/mouth without blooming into a corona."""
    gr = int(r * (2.8 if night else 2.0) * mult)
    gl = make_glow_surface(max(1, gr), MIRAGE, alpha_center=170 if night else 104,
                           falloff=2.1)
    surf.blit(gl, (int(cx - gr), int(cy - gr)), special_flags=pygame.BLEND_ADD)


# ── the exhaled drowned-city tier (creature mirage + pillar repeat) ───────────

def _city_tier(surf, cx, base_y, w, h, ss, *, night=False, glow=True, souls=True):
    """One translucent pagoda-city TIER: a flat pale pearl-green slab roofed with
    a wide pagoda eave, studded with a row of tiny drowned-soul windows (dark
    mirage dots that read as little lit huts). This is the mirage unit the clam
    hums out AND the band that TILES for the pillar shaft. Hard flat triad, no
    gradient — the see-through read comes from low layer alpha + the value step."""
    body = MIRAGE if not night else _shade_c(MIRAGE, 10)
    roof = MIRAGE_DK
    # Faint contained halo behind the tier so the stack glimmers as a mirage.
    if glow:
        _mirage_glow(surf, cx, base_y - h * 0.5, max(2, w * 0.42),
                     night=night, mult=0.7)

    # Tier wall — a translucent slab. Drawn onto its own alpha layer so the whole
    # city reads see-through (low alpha) without any within-shape gradient.
    layer = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    wall = pygame.Rect(0, 0, int(w), int(h * 0.74))
    wall.midbottom = (int(cx), int(base_y))
    pygame.draw.rect(layer, (*_shade_c(body, -26), 255), wall)
    pygame.draw.rect(layer, (*body, 255), wall.inflate(-int(w * 0.10), -int(h * 0.14)))
    # Top-left lit edge of the slab (rim sheen).
    pygame.draw.line(layer, (*MIRAGE_LT, 255),
                     (wall.left + int(w * 0.06), wall.top + int(h * 0.08)),
                     (wall.left + int(w * 0.06), wall.bottom - int(h * 0.10)),
                     max(1, int(1.4 * ss)))

    # Pagoda eave — a wide flared roof capping the tier (the city silhouette read).
    roof_y = wall.top
    eave_w = w * 1.18
    rh = h * 0.30
    eave = [
        (cx - eave_w * 0.5, roof_y),
        (cx - w * 0.30, roof_y - rh),
        (cx + w * 0.30, roof_y - rh),
        (cx + eave_w * 0.5, roof_y),
    ]
    pygame.draw.polygon(layer, (*roof, 255), [(int(x), int(y)) for x, y in eave])
    # Ridge sheen line along the roof crest.
    pygame.draw.line(layer, (*MIRAGE_LT, 255),
                     (int(cx - w * 0.30), int(roof_y - rh)),
                     (int(cx + w * 0.30), int(roof_y - rh)), max(1, int(1.2 * ss)))

    # Drowned-soul windows — a row of tiny dark hut-lights. They read as a sunken
    # populated town: the quiet dread inside the pretty mirage.
    if souls:
        nwin = 3
        wy = wall.centery + int(h * 0.04)
        for k in range(nwin):
            t = (k + 0.5) / nwin
            wx = wall.left + int(w * 0.14) + int(t * (w * 0.72))
            wr = max(1, int(w * 0.05))
            pygame.draw.rect(layer, (*MIRAGE_DK, 255),
                             (wx - wr, wy - wr, wr * 2, int(wr * 2.4)))
            pygame.draw.rect(layer, (*MIRAGE_LT, 255),
                             (wx - max(1, wr // 2), wy - max(1, wr // 2),
                              max(1, wr), max(1, wr)))

    # Whole tier at translucent alpha so the city is a glassy mirage, not solid.
    layer.set_alpha(150 if night else 124)
    surf.blit(layer, (0, 0))


def _finial(surf, cx, tip_y, w, h, ss, *, night=False, point_up=True):
    """A single mirage-pagoda roof FINIAL — the gap-cap unit. A compact stacked
    double-eave roof topped by a jewel knob, glowing pearl-green into the gap.
    `point_up` orients the roof so the eaves flare toward the gap edge."""
    d = -1 if point_up else 1
    _mirage_glow(surf, cx, tip_y + d * h * 0.2, max(2, w * 0.6), night=night, mult=0.95)
    layer = pygame.Surface(surf.get_size(), pygame.SRCALPHA)

    # Lower wide eave.
    base = tip_y + d * h * 0.62
    e1w = w
    e1h = h * 0.34
    eave1 = [
        (cx - e1w * 0.5, base),
        (cx - e1w * 0.18, base - d * e1h),
        (cx + e1w * 0.18, base - d * e1h),
        (cx + e1w * 0.5, base),
    ]
    pygame.draw.polygon(layer, (*MIRAGE_DK, 255), [(int(x), int(y)) for x, y in eave1])
    # Upper narrow eave.
    base2 = base - d * e1h * 1.05
    e2w = w * 0.6
    e2h = h * 0.30
    eave2 = [
        (cx - e2w * 0.5, base2),
        (cx - e2w * 0.16, base2 - d * e2h),
        (cx + e2w * 0.16, base2 - d * e2h),
        (cx + e2w * 0.5, base2),
    ]
    pygame.draw.polygon(layer, (*MIRAGE, 255), [(int(x), int(y)) for x, y in eave2])
    # Ridge sheen on both eaves.
    for ev in (eave1, eave2):
        pygame.draw.line(layer, (*MIRAGE_LT, 255),
                         (int(ev[1][0]), int(ev[1][1])),
                         (int(ev[2][0]), int(ev[2][1])), max(1, int(1.3 * ss)))
    # Jewel knob at the very tip.
    knob_y = base2 - d * e2h * 1.1
    pygame.draw.circle(layer, (*MIRAGE, 255), (int(cx), int(knob_y)), max(2, int(w * 0.10)))
    pygame.draw.circle(layer, (*MIRAGE_LT, 255), (int(cx), int(knob_y)), max(1, int(w * 0.055)))

    layer.set_alpha(178 if night else 152)
    surf.blit(layer, (0, 0))
    # The hot knob core sits at full alpha as the brightest focal pip of the cap —
    # carrying the same raised plume value the body's mirage now uses, so the
    # gap-cap glows as brightly as the creature's exhaled plume.
    hot = (230, 250, 236) if night else MIRAGE_LT
    pygame.draw.circle(surf, hot, (int(cx), int(knob_y)), max(2, int(w * 0.075)))


def _plume_pip(surf, cx, base_y, w, h, ss, *, night=False):
    """A SINGLE bright pearl-green mirage PLUME pip rising from the parted lips —
    the compact/32px mirage. Not a tower: one narrow tapering flame of light with
    a tiny pagoda hint at its tip, floating ABOVE the split with air around it so
    it never plugs the hinge or de-silhouettes the grin. It is the SOLE bright
    focal pip — lifted well above shell value so it reads as LIGHT, not mass."""
    # A broad bright halo first so the pip reads as LIGHT — distinctly brighter
    # than the warm shell on day haze AND night indigo. This carries the "glow"
    # read even after the 32px downscale softens the flame body.
    _mirage_glow(surf, cx, base_y - h * 0.5, max(3, w * 1.0),
                 night=night, mult=1.5)

    core = (236, 252, 240) if night else (224, 248, 230)
    edge = MIRAGE
    # A narrow upward teardrop flame: wide-ish at the lips, tapering to a point.
    # Drawn mostly in the LIFTED core value so the silhouette itself reads bright
    # (not a grey-green mass); a thin MIRAGE edge keeps it from being pure white.
    flame = [
        (cx - w * 0.5, base_y),
        (cx - w * 0.20, base_y - h * 0.55),
        (cx, base_y - h),
        (cx + w * 0.20, base_y - h * 0.55),
        (cx + w * 0.5, base_y),
    ]
    pygame.draw.polygon(surf, edge, [(int(x), int(y)) for x, y in flame])
    # Bright inner core flame filling most of the body so the plume is the
    # brightest value on the whole sheet — the sole focal pip.
    inner = [
        (cx - w * 0.34, base_y - h * 0.04),
        (cx, base_y - h * 0.96),
        (cx + w * 0.34, base_y - h * 0.04),
    ]
    pygame.draw.polygon(surf, core, [(int(x), int(y)) for x, y in inner])
    # A tiny pagoda-eave hint near the tip — the drowned-city read at hero scale,
    # small enough to vanish gracefully at 32px (leaving just the bright plume).
    ry = base_y - h * 0.60
    rw = w * 0.70
    pygame.draw.polygon(surf, core, [
        (int(cx - rw * 0.5), int(ry)),
        (int(cx), int(ry - h * 0.18)),
        (int(cx + rw * 0.5), int(ry)),
    ])
    # Hot knob at the apex — one crisp bright dot crowning the plume.
    pygame.draw.circle(surf, core, (int(cx), int(base_y - h)), max(2, int(w * 0.20)))


# ── the mirage tower (creature exhalation + pillar body) ──────────────────────

def _mirage_tower(surf, cx, top_y, base_y, w, ss, *, night=False, n_tiers=4,
                  finial=True):
    """The exhaled mirage TOWER: a stack of translucent pagoda city-tiers rising
    out of the clam's mouth, narrowing slightly as it climbs (a spire). One tier
    per repeat is the pillar's tileable unit; an optional pagoda roof FINIAL caps
    the very top. Vertical + symmetric so the prop->pillar mirror stays clean."""
    span = base_y - top_y
    tier_h = span / (n_tiers + (0.6 if finial else 0.0))
    for i in range(n_tiers):
        by = base_y - i * tier_h
        # Spire narrows as it rises so the hummed city tapers to a thread.
        tw = w * (1.0 - 0.12 * i)
        _city_tier(surf, cx, by, tw, tier_h, ss, night=night,
                   glow=(i % 2 == 0), souls=True)
    if finial:
        ty = base_y - n_tiers * tier_h
        _finial(surf, cx, ty, w * 0.62, tier_h * 0.9, ss, night=night)


# ── one shell half (a flat triad fan-ribbed valve) ───────────────────────────

def _shell_half(surf, cx, lip_y, hw, vh, ss, *, upper, night=False):
    """ONE clam valve drawn as a hard flat triad fan: a wide shallow shell that
    flares from the hinge line outward. `upper` mirrors it above the lip; the
    lower valve sits below. The valve is deliberately WIDE and SHALLOW so the two
    halves meet at a long HORIZONTAL split — never rounding into a vertical ball.
    Relief = a few BOLD value-stepped fan WEDGES (chunky rays) that survive the
    32px downscale as fan-DIRECTION, distinct from any spiral whorl."""
    d = -1 if upper else 1                       # vertical direction of the bulge
    body = _shade_c(SHELL, 12) if night else SHELL
    sheen = _shade_c(PEARL, 14) if night else PEARL

    # Valve silhouette: a wide low arc — a flattened half-ellipse so the shell is
    # MUCH wider than tall (the horizontal-grin pin). The lip edge runs flat across
    # the hinge line; the back fans up/down into a shallow bulge.
    steps = 48
    edge = []          # the curved outer rim (back of the valve)
    for i in range(steps + 1):
        t = i / steps
        ang = math.pi * t                        # 0..pi across the width
        x = cx - hw + 2 * hw * t
        y = lip_y + d * (math.sin(ang) ** 0.78) * vh
        edge.append((x, y))
    lip = [(cx + hw, lip_y), (cx - hw, lip_y)]
    shape = edge + lip

    pygame.draw.polygon(surf, _shade_c(body, -30),
                        [(int(x), int(y)) for x, y in shape])
    # Inset fill leaving a dark-core rim.
    inset = [(x, y + d * max(1, vh * 0.06)) for x, y in edge]
    inset_lip = [(cx + hw - hw * 0.04, lip_y), (cx - hw + hw * 0.04, lip_y)]
    pygame.draw.polygon(surf, body,
                        [(int(x), int(y)) for x, y in (inset + inset_lip)])

    # — Bold value-stepped fan WEDGES: a few chunky pie-slices radiating from the
    #   hinge apex, alternating ridge-light / valley-dark. Drawn as filled wedges
    #   (not hairline ribs) so the radiating fan-DIRECTION reads as a few fat rays
    #   even when the image is crushed to 32px — the "fan vs spiral" distinctness.
    apex = (cx, lip_y - d * vh * 0.02)           # wedges radiate from near the hinge
    n_wedge = 7
    valley = _shade_c(body, -30)
    ridge = _shade_c(body, 26)

    def _rim(t):
        ang = math.pi * (0.03 + 0.94 * t)
        rx = cx - hw * 0.97 + (2 * hw * 0.97) * t
        ry = lip_y + d * (math.sin(ang) ** 0.78) * vh * 0.98
        return rx, ry

    for k in range(n_wedge):
        t0 = k / n_wedge
        t1 = (k + 1) / n_wedge
        r0 = _rim(t0)
        r1 = _rim(t1)
        col = ridge if k % 2 == 0 else valley
        pygame.draw.polygon(surf, col, [(int(apex[0]), int(apex[1])),
                                        (int(r0[0]), int(r0[1])),
                                        (int(r1[0]), int(r1[1]))])
    # Hard dark valley-lines along the wedge seams so the rays stay separated at
    # small size even if neighbouring fills blur together.
    for k in range(n_wedge + 1):
        t = k / n_wedge
        rx, ry = _rim(t)
        pygame.draw.line(surf, _shade_c(body, -40), (int(apex[0]), int(apex[1])),
                         (int(rx), int(ry)), max(1, int(0.9 * ss)))

    # — Concentric growth-band arcs near the rim crossing the fan, the bivalve
    #   tell (a couple of darker bands following the shell edge).
    for gb in (0.62, 0.84):
        band = []
        for i in range(steps + 1):
            t = i / steps
            ang = math.pi * t
            x = cx - hw * 0.94 + 2 * hw * 0.94 * t
            y = lip_y + d * (math.sin(ang) ** 0.78) * vh * gb
            band.append((int(x), int(y)))
        pygame.draw.lines(surf, _shade_c(body, -22), False, band, max(1, int(1.1 * ss)))

    # — ONE hard pearl rim-sheen lobe on the top-left of the bulge (the lit crest).
    #   Stronger on the rounder LOWER valve so the asymmetric weight reads lit.
    sx, sy = cx - hw * 0.36, lip_y + d * vh * 0.62
    pygame.draw.circle(surf, sheen, (int(sx), int(sy)), max(2, int(hw * 0.15)))
    pygame.draw.circle(surf, body,
                       (int(sx + hw * 0.10), int(sy - d * vh * 0.16)),
                       max(2, int(hw * 0.12)))

    # — Pearl-nacre lip welt running the full horizontal split (the bright grin
    #   line). A bright flat band hugging the hinge edge so the wide split reads.
    welt_d = d * max(1, vh * 0.05)
    pygame.draw.line(surf, _shade_c(PEARL, -10 if not night else 8),
                     (int(cx - hw * 0.96), int(lip_y + welt_d)),
                     (int(cx + hw * 0.96), int(lip_y + welt_d)), max(2, int(2.0 * ss)))


def _hinge_eye(surf, ex, ey, r, ss, *, night=False):
    """A calm slate hinge-EYE seated at the shell wing — a heavy half-lidded slate
    lens with a tiny pearl catch-light. Two of these (one per wing) read as the
    serene old clam's eyes without breaking the warm shell with a cool body."""
    pygame.draw.circle(surf, SHELL_DEEP, (int(ex), int(ey)), max(2, int(r * 1.15)))
    pygame.draw.circle(surf, EYE, (int(ex), int(ey)), max(2, int(r)))
    # Heavy upper lid — a thick warm-ink arc dropping over the top of the lens so
    # the eye reads sleepy/serene, never a round bug-eye stare.
    lid = pygame.Rect(int(ex - r * 1.2), int(ey - r * 1.4), int(r * 2.4), int(r * 1.7))
    pygame.draw.arc(surf, SHELL_INK, lid, math.radians(8), math.radians(172),
                    max(2, int(2.0 * ss)))
    pygame.draw.circle(surf, PEARL,
                       (int(ex - r * 0.34), int(ey + r * 0.18)), max(1, int(r * 0.24)))


# ── the whole creature: clam + exhaled mirage tower ───────────────────────────

def build_hamaguri(scale=1.0, ss=5, *, night=False, compact=False):
    """The full creature on a transparent surface: the wide horizontal clam down
    low, the translucent mirage city-tower humming UP out of its parted lips. EPIC
    pass renders BIG at SS then smoothscales. `compact` is the gameplay/32px
    variant — clam grown to dominate the budget, tower shortened, face boldened."""
    # The clam is WIDE: half-width >> valve height, the horizontal-grin pin. The
    # shell MASS must read wider than tall (~1.4:1 W:H) at 32px so the grin wins.
    shell_hw = int(62 * scale) * ss
    # Asymmetric valve weight (kills the UFO/saucer twinning): the LOWER valve is
    # the heavier, rounder, bottom-rooted shell; the UPPER valve is flatter/thinner
    # so the pair reads as a clam opening UPWARD — a mouth, not a lens between domes.
    valve_lo = int(32 * scale) * ss              # heavier rounded lower valve
    valve_hi = int(22 * scale) * ss              # flatter, thinner upper valve
    tower_h = int(shell_hw * 3.0)

    side_pad = int(14 * scale) * ss
    top_pad = int(14 * scale) * ss
    bot_pad = int(14 * scale) * ss

    if compact:
        # Compact/32px budget: the CLAM dominates and the mirage is a single bright
        # plume pip floating above the split — short, with air around it, so it
        # never competes with the clam as a vertical mass (no UFO-antenna read).
        plume_h = int(shell_hw * 0.46)
        plume_w = int(shell_hw * 0.30)
        W = int((shell_hw + side_pad) * 2)
        H = int(top_pad + plume_h + valve_hi + valve_lo + bot_pad)
        surf = pygame.Surface((W, H), pygame.SRCALPHA)
        cx = W // 2
        mouth_w = shell_hw * 0.34
        lip_y = top_pad + plume_h + valve_hi
        # Plume pip rises with AIR above the parted lips, brightest focal value.
        open_gap = mouth_w * 1.15
        plume_base = lip_y - open_gap - valve_hi * 0.1
        _plume_pip(surf, cx, plume_base, plume_w, plume_h * 0.92, ss, night=night)
    else:
        # Hero budget: the full exhaled mirage city-tower hums up out of the mouth.
        tower_w = int(shell_hw * 0.5)
        W = int((shell_hw + side_pad) * 2)
        H = int(top_pad + tower_h + valve_hi + valve_lo + bot_pad)
        surf = pygame.Surface((W, H), pygame.SRCALPHA)
        cx = W // 2
        mouth_w = shell_hw * 0.30
        lip_y = top_pad + tower_h + valve_hi
        _mirage_tower(surf, cx, top_pad, lip_y - valve_hi * 0.1, tower_w, ss,
                      night=night, n_tiers=4, finial=True)
        open_gap = mouth_w * 0.9

    # The hummed-out mouth glow at the lip gap — the city's source.
    _mirage_glow(surf, cx, lip_y - open_gap * 0.5, max(3, mouth_w * 0.9),
                 night=night, mult=0.95)

    # Lower (heavy) valve first, then the lifted thin upper valve so the parted
    # mouth reads as a clean WIDE horizontal split with the mirage rising between.
    _shell_half(surf, cx, lip_y, shell_hw, valve_lo, ss, upper=False, night=night)
    _shell_half(surf, cx, lip_y - open_gap, shell_hw, valve_hi, ss, upper=True,
                night=night)

    # — Deep dark split-line keyline between the valves: a bold warm-ink band along
    #   the parting so the "parted-lips grin" is the FIRST thing the eye lands on
    #   at 32px (the whole distinctness pin). Drawn across the full hinge span.
    split_th = max(2, int(2.4 * ss))
    for yy, alpha in (((lip_y + lip_y - open_gap) / 2, 255),):
        pygame.draw.line(surf, SHELL_INK,
                         (int(cx - shell_hw * 0.99), int(yy)),
                         (int(cx + shell_hw * 0.99), int(yy)), split_th)
    # Dark inner-mouth shadow filling the gap between the lips so the split reads
    # as a deep dark slot, not just two touching edges.
    inner = [
        (cx - shell_hw * 0.86, lip_y),
        (cx + shell_hw * 0.86, lip_y),
        (cx + shell_hw * 0.70, lip_y - open_gap),
        (cx - shell_hw * 0.70, lip_y - open_gap),
    ]
    gap_layer = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(gap_layer, (*SHELL_DEEP, 255),
                        [(int(x), int(y)) for x, y in inner])
    gap_layer.set_alpha(150)
    surf.blit(gap_layer, (0, 0))

    # Hinge-eyes on the two wings of the UPPER valve (serene old clam). Larger so
    # they carry charm at 32px: the serene face above the wide grin.
    eye_r = shell_hw * (0.13 if compact else 0.10)
    eye_y = lip_y - open_gap - valve_hi * 0.42
    for s in (-1, 1):
        _hinge_eye(surf, cx + s * shell_hw * 0.60, eye_y, eye_r, ss, night=night)

    out_w = int(surf.get_width() / ss)
    out_h = int(surf.get_height() / ss)
    smallv = pygame.transform.smoothscale(surf, (out_w, out_h))
    oc = (*INK_NIGHT, 245) if night else (*INK, 235)
    return _add_outline(smallv, outline_color=oc, width=2 if night else 1)


# ── pillar pair (prop -> pillar mirror proof) ────────────────────────────────

OVERHANG = 12


def _tower_column(surf, cx, top_y, bot_y, w, ss, *, night=False):
    """The repeatable PILLAR BODY: the mirage city-tower as a straight tiling
    shaft — equal-height pagoda tiers filling the post with a steady tier +
    drowned-soul cadence. Tiers stack vertically so the band tiles top<->bottom."""
    length = bot_y - top_y
    tier_h = w * 1.15
    n = max(2, int(length / tier_h))
    th = length / n
    for i in range(n):
        by = bot_y - i * th
        _city_tier(surf, cx, by, w, th, ss, night=night,
                   glow=(i % 2 == 0), souls=True)


def _tower_pillar_obstacle(height, ss, *, flip, night=False):
    """One mirage-tower PILLAR obstacle: the city-tier shaft fills the post and a
    single pagoda roof FINIAL (~shaft+30%) caps the GAP-facing edge, glowing pearl-
    green INTO the gap. `flip=True` is the TOP pillar (finial at the bottom/gap
    edge, roof pointing DOWN); `flip=False` is the BOTTOM pillar (finial at the
    top/gap edge, roof pointing UP). Both mirror the same shaft — clean mirror."""
    bw = (PIPE_W + 2 * OVERHANG) * ss
    bh = max(1, int(height)) * ss
    surf = pygame.Surface((bw, bh), pygame.SRCALPHA)
    cx = bw // 2
    w = (PIPE_W - 14) * ss
    cap_band = int(48 * ss)
    if flip:
        _tower_column(surf, cx, 0, bh - cap_band, w, ss, night=night)
        _finial(surf, cx, bh - cap_band, w * 1.0, cap_band * 0.92, ss,
                night=night, point_up=False)
    else:
        _tower_column(surf, cx, cap_band, bh, w, ss, night=night)
        _finial(surf, cx, cap_band, w * 1.0, cap_band * 0.92, ss,
                night=night, point_up=True)
    out = pygame.transform.smoothscale(surf, (PIPE_W + 2 * OVERHANG, max(1, int(height))))
    oc = (*INK_NIGHT, 245) if night else (*INK, 235)
    return _add_outline(out, outline_color=oc, width=2 if night else 1)


# ── sheet composition ────────────────────────────────────────────────────────

def _label(surf, font, text, x, y, color=(238, 238, 232)):
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
    sheet.fill((54, 50, 46))          # warm neutral grey bg
    _label(sheet, font,
            "HAMAGURI-SHINKIROU  —  Umibozu-versions #4  —  mirage clam, mouth of a drowned city  —  round 2", 18, 12)
    _label(sheet, small,
            "Horizontal clam-mouth (the ONLY horizontal-grin of the brood) humming a translucent pearl-green pagoda-city out of its parted lips. Warm sea-rust shell w/ bold RADIATING fan-ribs; never teal.",
            18, 32, (214, 206, 188))

    # — Cell A: BIG hero, on a warm hazy mirage-sky.
    panel = pygame.Rect(18, 56, 320, 660)
    bgA = _sky(panel.w, panel.h, (40, 64, 78), (78, 104, 104), (150, 162, 138))
    sheet.blit(bgA, panel.topleft)
    pygame.draw.rect(sheet, (150, 130, 96), panel, 2, border_radius=8)
    hero = build_hamaguri(scale=1.6, ss=5)
    sheet.blit(hero, (panel.centerx - hero.get_width() // 2, panel.y + 44))
    _label(sheet, font, "(a) HERO  big scale (SS=5)", panel.x + 8, panel.y + 8)
    _label(sheet, small, "wide horizontal split + fan-ribbed valves + exhaled mirage tower",
           panel.x + 8, panel.y + 28, (224, 232, 214))

    # — Cell B: mirage-tower PILLAR pair at TRUE obstacle scale (night), plus a
    #   2x zoom on the gap proving the mirrored pagoda finials cap the gap.
    panelB = pygame.Rect(352, 56, 330, 660)
    bg = _sky(panelB.w, panelB.h, (10, 16, 28), (16, 28, 40), (26, 44, 46), stars=True)
    sheet.blit(bg, panelB.topleft)
    pygame.draw.rect(sheet, (150, 130, 96), panelB, 2, border_radius=8)
    _label(sheet, font, "(b) PILLAR  @ TRUE scale  (NIGHT)", panelB.x + 8, panelB.y + 8)
    _label(sheet, small, "city-tier tower tiles + pagoda finial cap (~shaft+30%), MIRRORED",
           panelB.x + 8, panelB.y + 28, (210, 232, 214))

    pw = PIPE_W + 2 * OVERHANG
    slice_h = 540
    slice_x = panelB.x + 22
    slice_y = panelB.y + 50
    gap_top = 178
    gap_h = 132
    top_h = gap_top
    bot_h = slice_h - gap_top - gap_h
    top_pillar = _tower_pillar_obstacle(top_h, 4, flip=True, night=True)
    bot_pillar = _tower_pillar_obstacle(bot_h, 4, flip=False, night=True)
    sheet.blit(top_pillar, (slice_x - 2, slice_y - 2))
    sheet.blit(bot_pillar, (slice_x - 2, slice_y + gap_top + gap_h - 2))
    pygame.draw.rect(sheet, (200, 210, 190), (slice_x - 4, slice_y - 4, pw + 8, slice_h + 8), 1)
    # Centre axis guide so the mirror is visible.
    axis_x = slice_x - 2 + (top_pillar.get_width() // 2)
    for yy in range(slice_y, slice_y + slice_h, 10):
        pygame.draw.line(sheet, (120, 150, 130), (axis_x, yy), (axis_x, yy + 4), 1)
    _label(sheet, small, "1x native (82px): city-tower", slice_x - 2, slice_y + slice_h + 6, (210, 230, 214))
    _label(sheet, small, "tiles; finials mirror @ gap", slice_x - 2, slice_y + slice_h + 22, (180, 230, 196))

    # 2x zoom of the gap band (the mirrored finials facing each other).
    cap_band = 48
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
    zbg = _sky(zw * 2, zh * 2, (10, 16, 28), (16, 26, 38), (24, 40, 44))
    sheet.blit(zbg, (zx, zy))
    pygame.draw.rect(sheet, (200, 210, 190), (zx - 1, zy - 1, zw * 2 + 2, zh * 2 + 2), 1)
    sheet.blit(zoom, (zx, zy))
    # Mirror line through the gap centre.
    mzy = zy + zh
    pygame.draw.line(sheet, (150, 200, 168), (zx, mzy), (zx + zw * 2, mzy), 1)
    _label(sheet, small, "2x zoom: pagoda finials", zx - 2, zy - 16, (255, 255, 255))
    _label(sheet, small, "mirror across gap (line)", zx - 2, zy + zh * 2 + 6, (180, 230, 196))

    # — Cell C: TRUE 32px gameplay chip on day + night, plus a 4x audit + grayscale.
    panelC = pygame.Rect(696, 56, 326, 660)
    pygame.draw.rect(sheet, (44, 40, 36), panelC, border_radius=8)
    pygame.draw.rect(sheet, (150, 130, 96), panelC, 2, border_radius=8)
    _label(sheet, font, "(c) TRUE 32px gameplay chip", panelC.x + 8, panelC.y + 8)
    _label(sheet, small, "clam-dominant compact / day + night sky", panelC.x + 8, panelC.y + 28,
           (210, 230, 214))

    # Compact gameplay creature, day + night, shown at a readable mid scale.
    boss_day = build_hamaguri(scale=0.6, ss=5, compact=True)
    boss_night = build_hamaguri(scale=0.6, ss=5, night=True, compact=True)
    day = _sky(150, 300, (96, 150, 200), (150, 180, 200), (200, 206, 176))
    night = _sky(150, 300, (10, 16, 28), (16, 28, 40), (28, 46, 48), stars=True)
    dy = panelC.y + 50
    sheet.blit(day, (panelC.x + 12, dy))
    sheet.blit(night, (panelC.x + 170, dy))
    sheet.blit(boss_day, (panelC.x + 12 + 75 - boss_day.get_width() // 2, dy + 8))
    sheet.blit(boss_night, (panelC.x + 170 + 75 - boss_night.get_width() // 2, dy + 8))
    _label(sheet, small, "DAY", panelC.x + 18, dy + 6, (24, 28, 24))
    _label(sheet, small, "NIGHT", panelC.x + 176, dy + 6, (180, 230, 196))

    # TRUE 32px chips on day + night skies, then a 4x nearest-neighbour blow-up +
    # grayscale value audit.
    gy = dy + 318
    _label(sheet, small, "TRUE 32px chip on day + night sky:", panelC.x + 12, gy - 2,
           (210, 230, 214))
    icon_src = build_hamaguri(scale=1.0, ss=5, compact=True)
    sc32 = 32 / icon_src.get_height()
    icon32 = pygame.transform.smoothscale(
        icon_src, (max(1, int(icon_src.get_width() * sc32)), 32))

    chips = [
        (_sky(86, 86, (96, 150, 200), (150, 180, 200), (200, 206, 176)), "day"),
        (_sky(86, 86, (10, 16, 28), (16, 28, 40), (28, 46, 48), stars=True), "night"),
    ]
    sx = panelC.x + 12
    for bg_chip, lab in chips:
        chip = pygame.Rect(sx, gy + 16, 86, 86)
        sheet.blit(bg_chip, chip.topleft)
        pygame.draw.rect(sheet, (160, 150, 120), chip, 1, border_radius=4)
        sheet.blit(icon32, (chip.centerx - icon32.get_width() // 2,
                            chip.centery - icon32.get_height() // 2))
        _label(sheet, small, lab, chip.x + 4, chip.y + 2, (240, 240, 232))
        sx += 96

    # 4x blow-up + grayscale of the true-32 chip.
    blow = pygame.transform.scale(icon32, (icon32.get_width() * 4, icon32.get_height() * 4))
    bx = panelC.x + 12
    byy = gy + 118
    pygame.draw.rect(sheet, (64, 58, 52), (bx - 2, byy - 2, blow.get_width() + 4, blow.get_height() + 4),
                     border_radius=4)
    sheet.blit(blow, (bx, byy))
    _label(sheet, small, "4x blow-up of the 32px chip", bx, byy + blow.get_height() + 4,
           (210, 230, 214))

    gray = _to_gray(blow)
    gx = bx + blow.get_width() + 24
    pygame.draw.rect(sheet, (112, 108, 102), (gx - 2, byy - 2, gray.get_width() + 4, gray.get_height() + 4),
                     border_radius=4)
    sheet.blit(gray, (gx, byy))
    _label(sheet, small, "grayscale value check", gx, byy + gray.get_height() + 4, (24, 24, 24))

    # — Footer captions.
    _label(sheet, small,
           "STYLE: flat saturated fills, hard 1-2px warm ink keyline (28,26,24), dark-core -> flat-fill -> pearl rim-sheen triad, 1px grown outline, chibi, scary-CUTE.",
           18, SH - 40, (214, 206, 188))
    _label(sheet, small,
           "PILLAR: the exhaled mirage CITY-TOWER is the shaft (translucent pagoda tiers tile w/ drowned-soul cadence); a single pagoda-roof FINIAL (~shaft+30%) caps + pearl-green-rims the gap. On-axis mirror.",
           18, SH - 22, (214, 206, 188))

    out_dir = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(out_dir, "round_2.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path)


if __name__ == "__main__":
    main()
