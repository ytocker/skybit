"""Look-dev sheet for the Skybit BOSS — "WANDJINA", a white-clay spin-off
off the shipped Mokoi (same flat-graphic lineage, inverted value structure).

Wandjina is the Kimberley rain-ancestor: a calm MOUTHLESS face inside a
radiating halo (the rays read as rain / lightning streaming off a sky-being).
Where Mokoi is a charcoal-DOMINANT plank-mask, Wandjina is its mirror: the
pipeclay-WHITE is the dominant ground (it INVERTS the source's dark plank),
the charcoal becomes a heavy keyline-MASS that draws the face, brick-red-ochre
rays make the halo starburst, and a soft yellow-ochre dot-field is the only
filler pattern. This is the cleanest, anchor survivor of the brood and the
ONLY white-dominant one — so its hue-blind tell flips too: a LIGHT body with a
dark face-mass, not a dark body with light dots.

House style this obeys (the leyak-epic flat-graphic grammar):
  - CHIBI proportions — one oversized floating haloed face-disk, big calm
    dark eyes, NO MOUTH (the character beat: the weather-god that never speaks).
  - FLAT saturated fills. NO within-shape gradients, NO bevels, NO soft edges.
    Detail is carried by PATTERN DENSITY (dot-field, ray-hatch), not shading.
  - Hard ink keyline (28,22,30) + a 1px grown outline so the disk POPS on any
    sky (the parrot `_add_outline` recipe). On a bright day sky the white body
    leans on this outline + the charcoal face-mass to stay readable.
  - The HALO is a crisp graphic STARBURST: alternating long/short red-ochre
    ray-tips radiating straight from the disk rim. It is NEVER a soft glow ring
    nor a circle of discrete drum-objects (the Raijin trap) — it is hard
    radial linework, so it reads as rain-streaks, not a corona.
  - Ember is WARM and CAP-RIM ONLY (the lone glow); the shaft + hero stay
    pigment-flat.
  - SUPERSAMPLE at SS=5-6 then smoothscale down — crisp geometry at downscale.

Accessibility tell (the inverted Wandjina read): a LIGHT pipeclay body with a
heavy CHARCOAL face-mass + radial ray linework. It survives grayscale on the
value flip alone (bright disk, dark eyes, dark rays) — no hue needed.

Prop -> pillar mirror: the rain-streak board IS the pillar. One pipeclay
rain-DOT column band + one red-ochre ray-HATCH band per repeat = the tiling
shaft; a small haloed face-DISK (~strip+30%) = the gap-edge cap, ember confined
to the cap RIM. Naturally vertical + symmetric — clean top<->bottom mirror.

Imports the real game colour/shape kit only; nothing under game/ is touched.
Headless + deterministic.

    SDL_VIDEODRIVER=dummy PYTHONPATH=/home/user/skybit python docs/skybit_devil/batch2/mokoi_versions/wandjina/render_wandjina.py
"""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from game.draw import lerp_color, make_glow_surface
from game.config import PIPE_W


pygame.init()

# ── PINNED PALETTE (wandjina) — hex-exact from the locked brief ──────────────
# Pipeclay-WHITE is the DOMINANT mass here (it INVERTS Mokoi's dark plank). The
# charcoal is a heavy keyline-MASS that draws the face (eyes / rim / nose), not
# a ground. Brick-red-ochre is the halo ray pigment. Soft yellow-ochre is the
# only dot-field filler. Ember is the lone warm glow, cap-RIM only. No triad.
PIPECLAY    = (232, 226, 212)   # pipeclay-WHITE — the DOMINANT light ground
PIPECLAY_HI = (244, 240, 230)   # a flat brighter clay for graphic separation
PIPECLAY_DK = (200, 194, 180)   # quiet clay shade for inner-disk seams

CHAR        = (44, 40, 46)      # charcoal keyline-MASS (eyes, rim, face lines)
CHAR_DK     = (28, 25, 32)      # deeper charcoal for pupils / deepest wells

RED_OCHRE   = (176, 84, 60)     # brick-red-ochre — the halo rays
RED_OCHRE_D = (138, 62, 44)     # deep red-ochre for ray keylines / shadow tips

YEL_OCHRE   = (214, 168, 96)    # soft yellow-ochre — the dot-field filler
YEL_OCHRE_D = (176, 132, 70)    # deep yellow-ochre dot keyline

EMBER       = (236, 138, 58)    # cap-RIM ember glow core
EMBER_HOT   = (255, 206, 132)   # ember twinkle centre

INK         = (28, 22, 30)      # the house keyline


def _add_outline(src, outline_color=(*INK, 235)):
    """Grow a 1px dark keyline from the alpha mask so the silhouette POPS on any
    sky (the parrot `_add_outline` recipe). Matters doubly here: the body is
    pipeclay-WHITE, so on a pale day sky only this outline keeps the disk edge
    from dissolving. Returns a padded surface."""
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


# ── flat-graphic primitives (NO triad — fills + ink keylines only) ───────────

def _dot_row(surf, cx, y, span_hw, n, r, col, *, key_col=None, ss=3):
    """A single evenly-spaced row of dots. Flat filled circles with an optional
    keyline so a row reads as crisp clean geometry and survives the downscale."""
    if n <= 1:
        xs = [cx]
    else:
        xs = [cx - span_hw + 2 * span_hw * (i / (n - 1)) for i in range(n)]
    for x in xs:
        pygame.draw.circle(surf, col, (int(x), int(y)), int(r))
        if key_col is not None:
            pygame.draw.circle(surf, key_col, (int(x), int(y)), int(r),
                               max(1, int(ss * 0.6)))


def _starburst_halo(surf, cx, cy, r_in, r_long, r_short, ss, *, n_long=12,
                    skip_bottom=0.0, skip_dir=1):
    """The signature HALO: a crisp graphic STARBURST of red-ochre rays radiating
    straight from the disk rim. Rays ALTERNATE long / short tips around the
    circle (the rain-streak / lightning read). This is hard radial linework —
    deliberately NOT a soft glow ring and NOT a circle of discrete objects (the
    Raijin drum-ring trap). Each ray is a tapered triangle (fat at the rim,
    pointed at the tip) so the burst reads as spokes of rain, not a gear.

    A BOLDER, LOWER-count burst reads more graphic at 32px than a dense fan: the
    long tips are clearly longer + wider-based so they own the silhouette, and
    the short tips are clearly stubbier so the long/short alternation stays
    legible after the downscale instead of mushing into a fuzzy spiky blob."""
    # Draw the long + short rays interleaved. Long rays carry the silhouette;
    # short rays read as the in-between stubs — the clear long/short rhythm is
    # what keeps the burst crisp small rather than a uniform spiky ring.
    for i in range(n_long):
        a0 = 2 * math.pi * (i / n_long) - math.pi / 2.0
        # one long ray on the spoke, one short ray in the gap after it
        for kind in ("long", "short"):
            a_test = a0 if kind == "long" else a0 + math.pi / n_long
            # Suppress rays that fire toward the board junction so no ray-tip
            # clips the neck where the disk meets the rain-board. `skip_dir` is
            # +1 when the board exits DOWN (hero, bottom-pillar cap) and -1 when
            # it exits UP (top-pillar cap) — keeps the seam clean either way.
            if skip_bottom > 0.0:
                target = skip_dir * math.pi / 2.0          # +y down / -y up
                off = abs(((a_test - target + math.pi) % (2 * math.pi)) - math.pi)
                if off < skip_bottom:
                    continue
            if kind == "long":
                a = a0
                r_tip = r_long
                # wider base so the long tips read BOLD, not thread-thin, at 32px
                half = 0.050 * 2 * math.pi
                col = RED_OCHRE
                col_key = RED_OCHRE_D
            else:
                a = a0 + math.pi / n_long
                # clearly stubbier short tip — exaggerated long/short contrast
                r_tip = r_in + (r_short - r_in) * 0.62
                half = 0.022 * 2 * math.pi
                col = RED_OCHRE_D
                col_key = None
            # tapered triangle: two base points on the rim, one tip out at r_tip
            bx0 = cx + math.cos(a - half) * r_in
            by0 = cy + math.sin(a - half) * r_in
            bx1 = cx + math.cos(a + half) * r_in
            by1 = cy + math.sin(a + half) * r_in
            tx = cx + math.cos(a) * r_tip
            ty = cy + math.sin(a) * r_tip
            pts = [(int(bx0), int(by0)), (int(bx1), int(by1)), (int(tx), int(ty))]
            pygame.draw.polygon(surf, col, pts)
            if col_key is not None:
                pygame.draw.polygon(surf, col_key, pts, max(1, int(1.2 * ss)))


def _ray_hatch_band(surf, cx, y0, y1, span_hw, ss, *, n=7):
    """A red-ochre RAY-hatch band: a fan of short radial-feeling streaks for the
    shaft. Echoes the halo's starburst as a flat repeating motif (slanted ray
    pairs, alternating long/short) so the pillar carries the rain-streak tell."""
    h = y1 - y0
    step = (2 * span_hw) / (n - 1)
    lw = max(1, int(1.8 * ss))
    for i in range(n):
        x = cx - span_hw + i * step
        long = (i % 2 == 0)
        drop = h * (0.95 if long else 0.55)
        col = RED_OCHRE if long else RED_OCHRE_D
        # a slim V — two streaks fanning down from a shared top point
        pygame.draw.line(surf, col, (int(x), int(y0)),
                         (int(x - h * 0.28), int(y0 + drop)), lw)
        pygame.draw.line(surf, col, (int(x), int(y0)),
                         (int(x + h * 0.28), int(y0 + drop)), lw)


# ── the haloed mouthless face-disk ───────────────────────────────────────────

def _wandjina_eye(surf, cx, cy, r, ss):
    """A big CALM dark eye: a heavy charcoal-mass oval ringed thin pipeclay, with
    a soft yellow-ochre iris-ring and an ink pupil. Flat fills only. The eyes
    are the dominant dark mass on the white face — wide and serene, the watching
    stare.

    The CATCH-LIGHT is the load-bearing detail: at true 32px the charcoal mass
    collapses to a solid dark oval and the eye otherwise reads as an empty skull
    socket. A BOLD pipeclay catch-ring around the iris plus a pipeclay glint pip
    keep a bright spot inside the dark mass after the downscale, so the eye still
    reads as a watching EYE rather than a hole — the whole scary-CUTE beat."""
    # charcoal eye-mass (the dominant dark on the white disk)
    pygame.draw.ellipse(surf, CHAR,
                        pygame.Rect(int(cx - r), int(cy - r * 1.18),
                                    int(2 * r), int(2 * r * 1.18)))
    pygame.draw.ellipse(surf, INK,
                        pygame.Rect(int(cx - r), int(cy - r * 1.18),
                                    int(2 * r), int(2 * r * 1.18)),
                        max(1, int(1.4 * ss)))
    # BOLD pipeclay catch-ring: a bright clay annulus just inside the charcoal
    # rim. This is the bright pixel that must survive to 32px so the eye is not a
    # hollow socket — drawn fat (filled clay disk, then re-cut by the iris) so it
    # keeps width after smoothscale.
    pygame.draw.circle(surf, PIPECLAY_HI, (int(cx), int(cy)), int(r * 0.78))
    # yellow-ochre iris ring inside the catch-ring
    pygame.draw.circle(surf, YEL_OCHRE, (int(cx), int(cy)), int(r * 0.56))
    pygame.draw.circle(surf, YEL_OCHRE_D, (int(cx), int(cy)), int(r * 0.56),
                       max(1, int(1.0 * ss)))
    # ink pupil
    pygame.draw.circle(surf, CHAR_DK, (int(cx), int(cy)), int(r * 0.32))
    # bright pipeclay glint pip riding the catch-ring (the lone 'alive' spark)
    pygame.draw.circle(surf, PIPECLAY_HI,
                       (int(cx - r * 0.20), int(cy - r * 0.34)),
                       max(1, int(r * 0.16)))


def _face_disk(surf, cx, cy, r, ss, *, halo=True, r_long=None, r_short=None,
               skip_bottom=0.0, skip_dir=1):
    """The oversized haloed MOUTHLESS face-disk. White pipeclay ground (DOMINANT
    mass), a heavy charcoal rim keyline, two big calm dark eyes, a slim charcoal
    nose-bar, a yellow-ochre dot-field across the brow + cheeks — and NO MOUTH
    (the character beat). The red-ochre starburst halo radiates from the rim.
    Everything flat-graphic; the value flip (light disk / dark face-mass) is the
    hue-blind read."""
    if halo:
        rl = r_long if r_long is not None else r * 2.05
        rs = r_short if r_short is not None else r * 1.55
        _starburst_halo(surf, cx, cy, r * 0.98, rl, rs, ss, n_long=12,
                        skip_bottom=skip_bottom, skip_dir=skip_dir)

    # white disk ground (the DOMINANT light mass)
    pygame.draw.circle(surf, PIPECLAY, (int(cx), int(cy)), int(r))
    # a flat brighter inner disk for graphic separation (NOT a bevel — a second
    # flat clay field marked by its own charcoal seam)
    pygame.draw.circle(surf, PIPECLAY_HI, (int(cx), int(cy)), int(r * 0.86))
    pygame.draw.circle(surf, CHAR, (int(cx), int(cy)), int(r * 0.86),
                       max(1, int(1.4 * ss)))
    # the heavy charcoal RIM keyline — the dark mass that frames the white face
    pygame.draw.circle(surf, CHAR, (int(cx), int(cy)), int(r), max(2, int(2.6 * ss)))
    pygame.draw.circle(surf, INK, (int(cx), int(cy)), int(r), max(1, int(1.2 * ss)))

    # yellow-ochre dot-field across the brow (the only filler pattern, up high).
    # Nudged one value/size step up so a hint of the dot-row survives to 64px.
    brow_y = cy - r * 0.50
    _dot_row(surf, cx, brow_y, r * 0.56, 6, r * 0.078, YEL_OCHRE,
             key_col=YEL_OCHRE_D, ss=ss)

    # two big CALM dark eyes — the dominant dark mass on the white face. Slightly
    # SMALLER + WIDER-set than round 1: recovers the "face" read over the
    # "skull" read and leaves room inside the dark oval for the catch-ring.
    eye_dx = r * 0.45
    eye_y = cy + r * 0.02
    eye_r = r * 0.235
    for s in (-1, 1):
        _wandjina_eye(surf, cx + s * eye_dx, eye_y, eye_r, ss)

    # slim charcoal nose-bar down the centreline, ending in a small splayed
    # base (the canonical Wandjina long straight nose). NO MOUTH below it.
    nose_top = eye_y - eye_r * 0.4
    nose_bot = cy + r * 0.56
    pygame.draw.line(surf, CHAR, (int(cx), int(nose_top)), (int(cx), int(nose_bot)),
                     max(2, int(2.8 * ss)))
    pygame.draw.line(surf, INK, (int(cx), int(nose_top)), (int(cx), int(nose_bot)),
                     max(1, int(1.0 * ss)))
    # splayed nostril base — two short charcoal feet (no mouth, deliberately)
    for s in (-1, 1):
        pygame.draw.line(surf, CHAR, (int(cx), int(nose_bot)),
                         (int(cx + s * r * 0.12), int(nose_bot + r * 0.10)),
                         max(2, int(2.4 * ss)))

    # yellow-ochre cheek dots flanking the nose — more dot-field, framing the
    # empty (mouthless) lower face so the absence reads as intentional calm
    for s in (-1, 1):
        _dot_row(surf, cx + s * r * 0.52, cy + r * 0.30, r * 0.12, 2,
                 r * 0.060, YEL_OCHRE, key_col=YEL_OCHRE_D, ss=ss)
    # a low brow-line of dots under the eyes, reinforcing the serene mask
    _dot_row(surf, cx, cy + r * 0.62, r * 0.30, 5, r * 0.052, YEL_OCHRE,
             key_col=YEL_OCHRE_D, ss=ss)


# ── the rain-streak board (creature trail + the pillar body) ─────────────────

def _rain_band_repeat(surf, cx, y0, band_h, half_w, ss):
    """ONE repeat of the rain-streak board: a pipeclay rain-DOT column band
    stacked over a red-ochre RAY-hatch band, on the WHITE clay ground (inverted
    from Mokoi's charcoal ground). This is the unit that TILES top<->bottom —
    exactly one rain-dot band + one ray-hatch band per repeat."""
    # WHITE clay ground for this repeat (the DOMINANT mass of the board)
    pygame.draw.rect(surf, PIPECLAY,
                     (int(cx - half_w), int(y0), int(2 * half_w), int(band_h)))

    # Top half: pipeclay rain-DOT columns — strings of dots reading as falling
    # rain. Charcoal-keyed so they pop on the light clay ground. A slight
    # diagonal LEAN + a per-column phase offset loosen the grid into a "falling
    # rain" cadence rather than a regular dot matrix.
    n_cols = 3
    for c in range(n_cols):
        colx = cx - half_w * 0.5 + half_w * (c / (n_cols - 1))
        phase = (c % 2) * 0.065        # stagger alternating columns
        for k in range(3):
            dy = y0 + band_h * (0.11 + phase + 0.13 * k)
            dx = colx + half_w * 0.10 * (k - 1)   # diagonal rain lean
            pygame.draw.circle(surf, PIPECLAY_DK, (int(dx), int(dy)),
                               max(1, int(half_w * 0.13)))
            pygame.draw.circle(surf, CHAR, (int(dx), int(dy)),
                               max(1, int(half_w * 0.13)), max(1, int(ss * 0.7)))

    # A thin charcoal seam between the two bands (graphic divider).
    seam_y = y0 + band_h * 0.50
    pygame.draw.line(surf, CHAR, (int(cx - half_w), int(seam_y)),
                     (int(cx + half_w), int(seam_y)), max(2, int(2.2 * ss)))

    # Bottom half: a red-ochre RAY-hatch band (the halo motif as a strip).
    _ray_hatch_band(surf, cx, y0 + band_h * 0.58, y0 + band_h * 0.94,
                    half_w * 0.70, ss, n=5)

    # Twin charcoal rail-lines down both edges so the board reads as one strip.
    for s in (-1, 1):
        pygame.draw.line(surf, CHAR, (int(cx + s * half_w * 0.92), int(y0)),
                         (int(cx + s * half_w * 0.92), int(y0 + band_h)),
                         max(1, int(1.8 * ss)))


def _rain_board(surf, cx, top_y, length, half_w, ss, *, n_repeats):
    """The rain-streak board streaming straight DOWN: white clay ground with
    stacked rain-dot + ray-hatch repeats — the band that TILES for the pillar.
    NO ember here (ember is cap-RIM only)."""
    band_h = length / n_repeats
    for i in range(n_repeats):
        _rain_band_repeat(surf, cx, top_y + i * band_h, band_h, half_w, ss)
    # A continuous ink keyline up both long edges so the board POPS as one strip.
    for s in (-1, 1):
        pygame.draw.line(surf, INK, (int(cx + s * half_w), int(top_y)),
                         (int(cx + s * half_w), int(top_y + length)),
                         max(1, int(1.6 * ss)))


# ── the whole creature: haloed face-disk + trailing rain board ───────────────

def _face_tell(surf, cx, cy, r, ss):
    """A baked LOW-RES face tell, sized so smoothscale to true 32px PRESERVES a
    recognizable haloed two-eyed mouthless mask instead of mushing to noise. At
    showcase scale it hides under the real disk; at icon scale it is what
    survives, carrying the 'haloed dark-eyed white disk, not a striped rope'
    read. The value flip (bright disk / dark eyes) is the tell."""
    eye_dx = r * 0.45
    eye_y = cy + r * 0.02
    eye_r = r * 0.235
    for s in (-1, 1):
        ex = cx + s * eye_dx
        # charcoal eye-mass
        pygame.draw.circle(surf, CHAR, (int(ex), int(eye_y)), int(eye_r * 1.16))
        # BOLD pipeclay catch-ring baked into the tell so the eye keeps a bright
        # spot at 32px instead of collapsing to a solid black socket
        pygame.draw.circle(surf, PIPECLAY_HI, (int(ex), int(eye_y)), int(eye_r * 0.84))
        pygame.draw.circle(surf, CHAR_DK, (int(ex), int(eye_y)), int(eye_r * 0.46))
        # the glint pip — the single bright pixel that must survive the downscale
        pygame.draw.circle(surf, PIPECLAY_HI,
                           (int(ex - eye_r * 0.22), int(eye_y - eye_r * 0.38)),
                           max(1, int(eye_r * 0.30)))
    # the long nose-bar that survives downscale
    pygame.draw.line(surf, CHAR, (int(cx), int(eye_y)), (int(cx), int(cy + r * 0.56)),
                     max(2, int(2.6 * ss)))


def build_wandjina(scale=1.0, ss=5, *, compact=False):
    """The full creature on its own transparent surface: the oversized haloed
    face-disk up top, a rain-streak board streaming straight down beneath it.
    Returns an outlined surface. Renders LARGE at SS=5-6 then smoothscales down.

    `compact` is the GAMEPLAY / 32px-icon variant: the DISK is grown to dominate
    the vertical budget and the board is cut to a short stub with 1 repeat, so
    the icon reads 'haloed mouthless disk on a short rain-board' — not a striped
    squiggle with a speck. Compact bakes a low-res face tell."""
    disk_r = int(40 * scale) * ss
    # The halo extends beyond the disk; budget for the long rays in the canvas.
    r_long = int(disk_r * 1.92)
    r_short = int(disk_r * 1.46)

    # Privilege the disk in the icon budget. Showcase keeps a long 3-repeat
    # board; compact cuts it to a single SHORT stub so the DISK+halo own the
    # vertical budget at true 32px.
    strip_mult = 0.34 if compact else 1.35
    half_w = int(disk_r * 0.40)
    strip_len = int(disk_r * 2 * strip_mult)
    n_repeats = 1 if compact else 3

    side_pad = int(8 * scale) * ss
    top_pad = int(8 * scale) * ss
    bot_pad = int(12 * scale) * ss

    # canvas wide enough for the full halo starburst
    W = int((r_long + side_pad) * 2)
    cx = W // 2
    disk_cy = top_pad + r_long
    board_top_y = disk_cy + disk_r * 0.92
    feet_y = board_top_y + strip_len
    H = int(feet_y + bot_pad)

    surf = pygame.Surface((W, H), pygame.SRCALPHA)

    # the rain board first so the disk occludes its top edge
    _rain_board(surf, cx, board_top_y, strip_len, half_w, ss, n_repeats=n_repeats)
    # a short white collar behind the disk base so the board springs from under it
    pygame.draw.rect(surf, PIPECLAY, (int(cx - disk_r * 0.42),
                                      int(disk_cy + disk_r * 0.55),
                                      int(disk_r * 0.84), int(disk_r * 0.5)))

    # Skip the rays firing straight DOWN so none clip the neck where the disk
    # springs from the rain-board collar (a clean disk<->board seam).
    _face_disk(surf, cx, disk_cy, disk_r, ss, halo=True,
               r_long=r_long, r_short=r_short, skip_bottom=0.42)
    if compact:
        _face_tell(surf, cx, disk_cy, disk_r, ss)

    out_w = int(surf.get_width() / ss)
    out_h = int(surf.get_height() / ss)
    smallv = pygame.transform.smoothscale(surf, (out_w, out_h))
    return _add_outline(smallv)


# ── pillar pair (prop -> pillar mirror proof) ────────────────────────────────

OVERHANG = 12


def _board_column(surf, cx, top_y, bot_y, half_w, ss):
    """The repeatable PILLAR BODY: the rain-streak board as a straight tiling
    shaft — exactly one pipeclay rain-dot band + one red-ochre ray-hatch band
    per repeat on the white clay ground (the band that mirrors top<->bottom).
    NO ember here — ember is cap-RIM only."""
    length = bot_y - top_y
    band = half_w * 2.6
    n = max(1, int(round(length / band)))
    band = length / n
    for i in range(n):
        _rain_band_repeat(surf, cx, top_y + i * band, band, half_w, ss)
    for s in (-1, 1):
        pygame.draw.line(surf, INK, (int(cx + s * half_w), int(top_y)),
                         (int(cx + s * half_w), int(bot_y)), max(1, int(1.6 * ss)))


def _disk_cap(surf, cx, cap_base_y, half_w, ss, *, point_up, night=False):
    """The creature-derived GAP-EDGE CAP: a small haloed face-DISK sized
    ~strip+30%, sitting at the board end facing the gap, with the EMBER glow
    CONFINED to the cap RIM (the only warm light anywhere). A modest disk, never
    a top-heavy slab. `point_up` orients the cap toward the gap."""
    d = -1 if point_up else 1
    disk_r = int(half_w * 1.30)        # cap ~ strip + 30%
    cy = cap_base_y + d * (disk_r + half_w * 0.3)

    # Ember glow CONFINED to the cap RIM — radiates INTO the gap. The lone warm
    # light in the whole pillar; the shaft stays white+charcoal+red+yellow.
    gr = int(disk_r * (1.5 if night else 1.32))
    gy = cy
    gl = make_glow_surface(gr, EMBER, alpha_center=150 if night else 110, falloff=2.5)
    surf.blit(gl, (int(cx - gr), int(gy - gr)), special_flags=pygame.BLEND_ADD)

    # the haloed face-disk cap (smaller halo than the hero so it stays compact).
    # The board exits on the NON-gap side, so skip the rays that fire that way
    # to keep the disk<->board seam clean. point_up -> board exits down (+1);
    # point_down -> board exits up (-1).
    _face_disk(surf, cx, cy, disk_r, ss, halo=True,
               r_long=int(disk_r * 1.62), r_short=int(disk_r * 1.28),
               skip_bottom=0.42, skip_dir=(1 if point_up else -1))

    # ember twinkle at the disk RIM facing the gap (cap-rim ember, per brief)
    rim_y = cy + (-d) * disk_r * 0.98
    pygame.draw.circle(surf, EMBER, (int(cx), int(rim_y)), max(1, int(disk_r * 0.18)))
    pygame.draw.circle(surf, EMBER_HOT, (int(cx), int(rim_y)), max(1, int(disk_r * 0.09)))


def _board_pillar_obstacle(height, ss, *, flip, night=False):
    """One rain-streak BOARD pillar obstacle: the rain/ray board fills the post
    and a haloed face-disk CAP sits at the GAP-facing edge, its ember glow
    radiating INTO the gap. `flip=True` is the TOP pillar — cap at the bottom
    (gap) edge; `flip=False` is the BOTTOM pillar — cap at the top (gap) edge."""
    bw = (PIPE_W + 2 * OVERHANG) * ss
    bh = max(1, int(height)) * ss
    surf = pygame.Surface((bw, bh), pygame.SRCALPHA)
    cx = bw // 2
    half_w = int((PIPE_W * 0.42)) * ss
    cap_band = int(58 * ss)
    if flip:
        _board_column(surf, cx, 0, bh - cap_band, half_w, ss)
        _disk_cap(surf, cx, bh - cap_band, half_w, ss, point_up=False, night=night)
    else:
        _board_column(surf, cx, cap_band, bh, half_w, ss)
        _disk_cap(surf, cx, cap_band, half_w, ss, point_up=True, night=night)
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

    SW, SH = 1120, 800
    sheet = pygame.Surface((SW, SH))
    sheet.fill((118, 120, 126))            # neutral grey bg
    _label(sheet, font,
           "WANDJINA  —  mokoi spin-off  —  white-clay radial rain-ancestor  —  round 2",
           18, 12, (24, 24, 28))
    _label(sheet, small,
           "FLAT-GRAPHIC, INVERTED VALUE: pipeclay-WHITE dominant ground, charcoal keyline-MASS face, brick-red ray-STARBURST halo, soft yellow-ochre dot-field; MOUTHLESS; ember cap-rim only.",
           18, 32, (40, 40, 46))

    # — Cell A: the BIG hero haloed face-disk on a neutral panel (SS=6).
    panel = pygame.Rect(18, 56, 372, 690)
    pygame.draw.rect(sheet, (96, 96, 100), panel, border_radius=8)
    pygame.draw.rect(sheet, (60, 60, 64), panel, 2, border_radius=8)
    _label(sheet, font, "(a) HERO  big scale  SS=6", panel.x + 8, panel.y + 8, (245, 240, 230))
    _label(sheet, small, "haloed mouthless disk + 3-repeat rain/ray board",
           panel.x + 8, panel.y + 28, (235, 230, 220))
    hero = build_wandjina(scale=1.55, ss=6)
    hx = panel.centerx - hero.get_width() // 2
    hy = panel.y + 50
    if hx < panel.x + 4:
        hero = pygame.transform.smoothscale(
            hero, (panel.w - 16, int(hero.get_height() * (panel.w - 16) / hero.get_width())))
        hx = panel.x + 8
    sheet.blit(hero, (hx, hy))

    # — Cell B: board as a tileable PILLAR pair at TRUE obstacle scale, on NIGHT,
    #   plus a 2x zoom of the CAP band proving the contained ember + the mirror.
    panelB = pygame.Rect(402, 56, 320, 690)
    bg = _sky(panelB.w, panelB.h, (8, 8, 30), (20, 18, 52), (40, 30, 70), stars=True)
    sheet.blit(bg, panelB.topleft)
    pygame.draw.rect(sheet, (60, 60, 64), panelB, 2, border_radius=8)
    _label(sheet, font, "(b) PROP -> PILLAR  @ TRUE  (NIGHT)", panelB.x + 8, panelB.y + 8)

    pw = PIPE_W + 2 * OVERHANG
    slice_h = 560
    slice_x = panelB.x + 24
    slice_y = panelB.y + 44
    gap_top = 176
    gap_h = 130
    top_h = gap_top
    bot_h = slice_h - gap_top - gap_h
    top_pillar = _board_pillar_obstacle(top_h, 4, flip=True, night=True)
    bot_pillar = _board_pillar_obstacle(bot_h, 4, flip=False, night=True)
    sheet.blit(top_pillar, (slice_x - 2, slice_y - 2))
    sheet.blit(bot_pillar, (slice_x - 2, slice_y + gap_top + gap_h - 2))
    pygame.draw.rect(sheet, (210, 200, 180), (slice_x - 4, slice_y - 4, pw + 8, slice_h + 8), 1)
    _label(sheet, small, "1x native: rain-dot band +", slice_x - 2, slice_y + slice_h + 6,
           (235, 225, 210))
    _label(sheet, small, "ray-hatch band per repeat; disk cap; ember on RIM",
           slice_x - 2, slice_y + slice_h + 22, (255, 210, 150))

    cap_band = 58
    zw, zh = pw, 150
    zoom_src = pygame.Surface((zw, zh), pygame.SRCALPHA)
    top_anchor = 12
    zoom_src.blit(top_pillar, (-2, -(top_h - cap_band - top_anchor) - 2))
    zoom_gap = zh - 2 * cap_band - 2 * top_anchor
    bot_anchor = top_anchor + cap_band + zoom_gap
    zoom_src.blit(bot_pillar, (-2, bot_anchor - 2))
    zoom = pygame.transform.scale(zoom_src, (zw * 2, zh * 2))
    zx = panelB.x + 168
    zy = panelB.y + 120
    zbg = _sky(zw * 2, zh * 2, (8, 8, 30), (16, 14, 44), (28, 20, 58))
    sheet.blit(zbg, (zx, zy))
    pygame.draw.rect(sheet, (210, 200, 180), (zx - 1, zy - 1, zw * 2 + 2, zh * 2 + 2), 1)
    sheet.blit(zoom, (zx, zy))
    _label(sheet, small, "2x zoom CAP band:", zx - 2, zy - 16, (255, 255, 255))
    _label(sheet, small, "haloed disk cap;", zx - 2, zy + zh * 2 + 6, (255, 210, 150))
    _label(sheet, small, "top<->bottom mirror; ember rim", zx - 2, zy + zh * 2 + 22, (255, 210, 150))

    # — Cell C: TRUE 32px gameplay chip on a DAY sky AND a NIGHT sky, plus a 4x
    #   audit + grayscale tell-check.
    panelC = pygame.Rect(734, 56, 368, 690)
    pygame.draw.rect(sheet, (96, 96, 100), panelC, border_radius=8)
    pygame.draw.rect(sheet, (60, 60, 64), panelC, 2, border_radius=8)
    _label(sheet, font, "(c) TRUE 32px gameplay chip", panelC.x + 8, panelC.y + 8, (245, 240, 230))
    _label(sheet, small, "disk-dominant compact; day + night skies", panelC.x + 8, panelC.y + 28,
           (235, 230, 220))

    # The compact gameplay creature blown up for a clear day/night read.
    boss = build_wandjina(scale=0.62, ss=5, compact=True)
    day = _sky(160, 300, (40, 110, 200), (90, 170, 230), (170, 220, 245))
    night = _sky(160, 300, (8, 8, 30), (20, 18, 52), (40, 30, 70), stars=True)
    dy = panelC.y + 48
    sheet.blit(day, (panelC.x + 16, dy))
    sheet.blit(night, (panelC.x + 184, dy))
    sheet.blit(boss, (panelC.x + 16 + 80 - boss.get_width() // 2, dy + 8))
    sheet.blit(boss, (panelC.x + 184 + 80 - boss.get_width() // 2, dy + 8))
    _label(sheet, small, "DAY", panelC.x + 16 + 6, dy + 6, (18, 28, 24))
    _label(sheet, small, "NIGHT", panelC.x + 184 + 6, dy + 6, (255, 220, 200))

    # The TRUE-32 icon: shown at 1x on day/night/neutral chips, then 3x + 64 + gray.
    icon_src = build_wandjina(scale=1.0, ss=5, compact=True)
    sc32 = 32 / icon_src.get_height()
    icon32 = pygame.transform.smoothscale(
        icon_src, (max(1, int(icon_src.get_width() * sc32)), 32))
    sc64 = 64 / icon_src.get_height()
    icon64 = pygame.transform.smoothscale(
        icon_src, (max(1, int(icon_src.get_width() * sc64)), 64))

    gy = dy + 316
    _label(sheet, small, "TRUE 32px at 1x (no blow-up):", panelC.x + 16, gy - 2,
           (235, 225, 215))
    swatches = [
        ((40, 110, 200), "day"),
        ((40, 30, 70), "night"),
        ((96, 96, 100), "neutral"),
    ]
    sx = panelC.x + 16
    sw = 100
    for col, lab in swatches:
        chip = pygame.Rect(sx, gy + 16, sw, 80)
        pygame.draw.rect(sheet, col, chip, border_radius=4)
        sheet.blit(icon32, (chip.centerx - icon32.get_width() // 2,
                            chip.centery - icon32.get_height() // 2))
        _label(sheet, small, lab, chip.x + 4, chip.y + 2, (240, 240, 240))
        sx += sw + 8

    # 3x nearest-neighbour blow-up of the true-32 icon so the tell is auditable,
    # plus the grayscale value check (the inverted light/dark tell must survive).
    chip = pygame.Rect(panelC.x + 16, gy + 110, 96, 110)
    pygame.draw.rect(sheet, (78, 78, 82), chip, border_radius=4)
    blow = pygame.transform.scale(icon32, (icon32.get_width() * 3, icon32.get_height() * 3))
    sheet.blit(blow, (chip.x + 6, chip.centery - blow.get_height() // 2))
    sheet.blit(icon64, (chip.right + 12, chip.centery - icon64.get_height() // 2))
    _label(sheet, small, "3x / 64px audit", chip.x + 4, chip.y + 2, (240, 240, 240))

    gray = _to_gray(icon64)
    gchip = pygame.Rect(panelC.x + 244, gy + 110, 104, 110)
    pygame.draw.rect(sheet, (124, 128, 124), gchip, border_radius=4)
    sheet.blit(gray, (gchip.centerx - gray.get_width() // 2,
                      gchip.centery - gray.get_height() // 2))
    _label(sheet, small, "grayscale tell", gchip.x + 4, gchip.y + 2, (24, 24, 24))

    # — Footer: style notes.
    _label(sheet, small,
           "FLAT only: detail via PATTERN DENSITY (rain-dot columns + ray-hatch + starburst halo), never 3D shading; pipeclay-WHITE dominant; charcoal face-MASS; red-ochre rays; yellow dot-field.",
           18, SH - 64, (40, 40, 46))
    _label(sheet, small,
           "prop->pillar: rain board = 1 pipeclay rain-dot band + 1 red-ochre ray-hatch band per repeat (tiles); gap-edge cap = a haloed mouthless face-disk (~+30%), ember CONFINED to cap rim. Clean mirror.",
           18, SH - 44, (40, 40, 46))

    out_dir = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(out_dir, "round_2.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path)


if __name__ == "__main__":
    main()
