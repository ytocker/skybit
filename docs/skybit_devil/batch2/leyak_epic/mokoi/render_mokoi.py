"""Look-dev sheet for the Skybit BOSS leyak-epic take — "MOKOI".

Aboriginal-mimi / mokoi sorcerer-spirit reframed as a FLAT painted plank-mask:
a charcoal-ground board face blinking big concentric target-eyes, sliding down a
strip of glowing bark-art that IS the pillar. Where the shipped Leyak sculpted
volume with a warm triad, Mokoi is intentionally the FLAT-GRAPHIC concept of
this set — all read comes from saturated flat fills + dense geometric pattern
(pipeclay dot-rows, ochre cross-hatch), NOT from 3D shading.

House style this obeys (the leyak-epic grammar, flat-graphic dialect):
  - CHIBI proportions — one oversized floating plank-mask, huge ring-eyes, a
    small bared grin. No torso, no limbs; the bark-ribbon is the body.
  - FLAT saturated fills. NO within-shape gradients, NO bevels, NO soft edges.
    Detail is carried by PATTERN DENSITY (dot-rows, hatch-lines), not shading.
  - Hard 1-2px ink keyline (28,22,30) inside + a 1px grown outline on the
    silhouette so the board POPS on any sky (the parrot `_add_outline` recipe).
  - Charcoal is the DOMINANT mass; twin-ochre are the warm accents; the
    pipeclay-white dot-pattern is the protected hue-blind tell (it survives a
    grayscale check on its own). Ember glow is CONFINED to the gap-edge cap.
  - SUPERSAMPLE at SS=5-6 then smoothscale down — crisp geometry at downscale.

Accessibility tell (pinned in brief): the pipeclay-white dot-pattern + the
high charcoal/pipeclay value contrast carry the read independent of hue. No
warm hue anywhere except the contained cap ember, so a hue-blind player still
reads the dotted board + dotted ribbon.

Prop -> pillar mirror: the bark-art STRIP itself is the pillar. One pipeclay
dot-band + one ochre hatch-band per repeat = the tiling shaft; a creature-
derived totem-plaque (a small plank-mask sibling) = the gap-edge cap, with the
ember glow confined to that cap. Naturally vertical + symmetric — clean mirror,
no top-heavy cap.

Imports the real game colour/shape kit only; nothing under game/ is touched.
Headless + deterministic.

    SDL_VIDEODRIVER=dummy PYTHONPATH=/home/user/skybit python docs/skybit_devil/batch2/leyak_epic/mokoi/render_mokoi.py
"""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from game.draw import _shade_c, lerp_color, make_glow_surface
from game.config import PIPE_W


pygame.init()

# ── PINNED PALETTE (leyak-epic mokoi) — hex-exact from the locked brief ──────
# Charcoal is the DOMINANT mass (the board ground + the ribbon ground). Twin
# ochre are the only chromatic accents. Pipeclay-white is the protected tell —
# it carries the read in grayscale. Ember is the lone warm glow, confined to
# the cap. There is deliberately no triad sheen tint: the look is FLAT.
CHAR        = (46, 42, 48)      # charcoal ground (dominant)
CHAR_DK     = (30, 27, 34)      # deeper charcoal for inset wells / seams
CHAR_HI     = (66, 60, 68)      # a flat lighter charcoal for graphic separation

# Pushed REDDER/earthier (burnt-sienna red-ochre) so Mokoi's warm reads
# distinct from Mariachi sombrero-ochre (214,168,84) and Karakasa ochre-bamboo
# (204,168,96) — both yellow-ochres. This lands as a red-ochre, not a yellow.
OCHRE_L     = (192, 118, 56)    # bright red-ochre accent
OCHRE_D     = (150, 86, 40)     # deep red-ochre accent

PIPECLAY    = (238, 232, 220)   # pipeclay-white — the protected dot tell
PIPECLAY_DK = (196, 190, 178)   # a quiet shade for dot keylines (still light)

EMBER       = (236, 138, 58)    # cap-only ember glow core
EMBER_HOT   = (255, 206, 132)   # ember twinkle centre

INK         = (28, 22, 30)      # the house keyline


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


# ── flat-graphic primitives (NO triad — fills + ink keylines only) ───────────

def _plank_outline(surf, cx, cy, hw, hh, ss, col, *, key=True):
    """A flat plank-board panel: a rounded-corner rectangle drawn as a hard flat
    fill with a 1-2px ink keyline. The slightly bowed top + bottom + tapered
    base read it as a carved board, not a screen rectangle. NO bevel/sheen — the
    board is graphic-flat; volume is faked only by the keyline."""
    r = int(hw * 0.22)
    rect = pygame.Rect(int(cx - hw), int(cy - hh), int(2 * hw), int(2 * hh))
    pygame.draw.rect(surf, col, rect, border_radius=r)
    if key:
        pygame.draw.rect(surf, INK, rect, max(1, int(1.6 * ss)), border_radius=r)


def _dot_row(surf, cx, y, span_hw, n, r, col, *, key_col=None, ss=3):
    """A single evenly-spaced row of pipeclay dots — the protected tell motif.
    Dots are flat filled circles with an optional 1px lighter keyline so a row
    reads as crisp clean geometry at high res and survives the downscale."""
    if n <= 1:
        xs = [cx]
    else:
        xs = [cx - span_hw + 2 * span_hw * (i / (n - 1)) for i in range(n)]
    for x in xs:
        pygame.draw.circle(surf, col, (int(x), int(y)), int(r))
        if key_col is not None:
            pygame.draw.circle(surf, key_col, (int(x), int(y)), int(r),
                               max(1, int(ss * 0.6)))


def _hatch_band(surf, cx, y0, y1, span_hw, col, ss, *, n=9, cross=True):
    """An ochre cross-hatch band: a set of evenly spaced diagonal lines (and a
    mirrored set for the cross) confined to a horizontal band. Pure linework —
    the second flat motif that alternates with the dot-rows. Graphic density,
    not shading."""
    h = y1 - y0
    step = (2 * span_hw) / (n - 1)
    lw = max(1, int(1.6 * ss))
    for i in range(n):
        x = cx - span_hw + i * step
        pygame.draw.line(surf, col, (int(x), int(y0)), (int(x + h * 0.5), int(y1)), lw)
        if cross:
            pygame.draw.line(surf, col, (int(x), int(y0)), (int(x - h * 0.5), int(y1)), lw)


# ── the floating plank-mask head ─────────────────────────────────────────────

def _ring_eye(surf, cx, cy, r, ss, *, blink=False):
    """A big CONCENTRIC ring-eye — the signature target motif. Alternating flat
    charcoal / pipeclay / ochre rings around an ink pupil. All rings are flat
    fills (no shading); the concentric banding is the graphic detail. `blink`
    swaps the wide eye for a single bowed pipeclay lid-bar (the cute beat)."""
    if blink:
        # A fat upward-bowed pipeclay lid-bar — a sleepy half-closed eye.
        top, bot = [], []
        n = 12
        for i in range(n + 1):
            xr = -1.0 + 2.0 * (i / n)
            x = cx + xr * r
            lift = r * 0.5 * (xr * xr)
            top.append((x, cy - r * 0.16 + lift))
            bot.append((x, cy + r * 0.16 + lift))
        pygame.draw.polygon(surf, PIPECLAY, [(int(x), int(y)) for x, y in (top + bot[::-1])])
        pygame.draw.polygon(surf, INK, [(int(x), int(y)) for x, y in (top + bot[::-1])],
                            max(1, int(1.4 * ss)))
        return
    # Concentric rings from outside in. Ochre is reserved for the OUTER ring
    # only; the inner bands alternate strictly pipeclay<->ink so the target keeps
    # crisp value-contrast all the way down to 32px (ochre-on-ochre inner bands
    # turned to mud below ~64px). Flat fills, hard edges.
    bands = [
        (1.00, CHAR_DK),
        (0.84, OCHRE_D),
        (0.66, PIPECLAY),
        (0.50, INK),
        (0.34, PIPECLAY),
        (0.20, INK),
    ]
    for frac, col in bands:
        pygame.draw.circle(surf, col, (int(cx), int(cy)), max(1, int(r * frac)))
    # Crisp ink keyline on the outer ring so the target POPS off the board.
    pygame.draw.circle(surf, INK, (int(cx), int(cy)), int(r), max(1, int(1.4 * ss)))
    # A tiny pipeclay catch-dot — the only "glint", kept flat (a stamped dot).
    pygame.draw.circle(surf, PIPECLAY, (int(cx + r * 0.10), int(cy - r * 0.10)),
                       max(1, int(r * 0.07)))


def _mask_head(surf, cx, cy, hw, hh, ss, *, blink=False):
    """The oversized floating plank-MASK: a charcoal board face carrying two big
    concentric ring-eyes, a pipeclay-dot brow + cheek-rows (the protected tell),
    a slim ochre nose-bar, and a small bared grin. Everything is flat-graphic;
    the charcoal board is the dominant mass, ochre is minor, pipeclay dots carry
    the value read. No ember on the creature — ember is cap-only."""
    # The board ground (dominant charcoal mass).
    _plank_outline(surf, cx, cy, hw, hh, ss, CHAR)
    # A flat inner charcoal-light panel for graphic separation (NOT a bevel —
    # it's a second flat board inset, marked by its own keyline).
    _plank_outline(surf, cx, cy, hw * 0.88, hh * 0.90, ss, CHAR_HI, key=False)
    pygame.draw.rect(
        surf, INK,
        pygame.Rect(int(cx - hw * 0.88), int(cy - hh * 0.90),
                    int(2 * hw * 0.88), int(2 * hh * 0.90)),
        max(1, int(1.2 * ss)), border_radius=int(hw * 0.20))

    # Brow band: a dense pipeclay dot-row across the top (the tell, up high).
    brow_y = cy - hh * 0.60
    _dot_row(surf, cx, brow_y, hw * 0.66, 9, hw * 0.052, PIPECLAY,
             key_col=PIPECLAY_DK, ss=ss)

    # Twin ochre forehead chevrons flanking the centre (minor warm accent).
    for s in (-1, 1):
        chev = [
            (cx + s * hw * 0.14, cy - hh * 0.44),
            (cx + s * hw * 0.40, cy - hh * 0.30),
            (cx + s * hw * 0.14, cy - hh * 0.30),
        ]
        pygame.draw.polygon(surf, OCHRE_L, [(int(x), int(y)) for x, y in chev])

    # The two big concentric ring-eyes — the dominant face read.
    eye_dx = hw * 0.42
    eye_y = cy - hh * 0.06
    eye_r = hw * 0.34
    for s in (-1, 1):
        _ring_eye(surf, cx + s * eye_dx, eye_y, eye_r, ss, blink=blink)

    # Slim ochre nose-bar down the centreline between/below the eyes.
    nose_top = eye_y + eye_r * 0.4
    nose_bot = cy + hh * 0.40
    pygame.draw.line(surf, OCHRE_D, (int(cx), int(nose_top)), (int(cx), int(nose_bot)),
                     max(2, int(3.0 * ss)))
    pygame.draw.line(surf, OCHRE_L, (int(cx), int(nose_top)), (int(cx), int(nose_bot)),
                     max(1, int(1.4 * ss)))
    # Pipeclay nostril dots at the base of the nose-bar.
    _dot_row(surf, cx, nose_bot, hw * 0.10, 2, hw * 0.045, PIPECLAY, ss=ss)

    # Cheek dot-rows flanking the nose — more of the protected tell.
    for s in (-1, 1):
        for k, ry in enumerate((0.10, 0.24)):
            _dot_row(surf, cx + s * hw * 0.50, cy + hh * (ry + 0.02), hw * 0.18, 3,
                     hw * 0.045, PIPECLAY, key_col=PIPECLAY_DK, ss=ss)

    # A small bared grin: a charcoal-dark mouth well with a single pipeclay
    # tooth-row (flat geometric teeth, the scary-CUTE beat — small, not a maw).
    grin_y = cy + hh * 0.62
    grin_hw = hw * 0.48
    grin_h = hh * 0.16
    mouth = pygame.Rect(int(cx - grin_hw), int(grin_y - grin_h),
                        int(2 * grin_hw), int(2 * grin_h))
    pygame.draw.rect(surf, CHAR_DK, mouth, border_radius=int(grin_h * 0.7))
    pygame.draw.rect(surf, INK, mouth, max(1, int(1.4 * ss)),
                     border_radius=int(grin_h * 0.7))
    teeth = 6
    tw = (2 * grin_hw * 0.86) / teeth
    for i in range(teeth):
        tx = cx - grin_hw * 0.86 + i * tw
        rect = pygame.Rect(int(tx + tw * 0.16), int(grin_y - grin_h * 0.7),
                           int(tw * 0.68), int(grin_h * 1.4))
        pygame.draw.rect(surf, PIPECLAY, rect, border_radius=max(1, int(ss)))

    # Chin dot-row — the lowest tell row, tying the board to the ribbon below.
    _dot_row(surf, cx, cy + hh * 0.84, hw * 0.46, 7, hw * 0.046, PIPECLAY,
             key_col=PIPECLAY_DK, ss=ss)


# ── the bark-art STRIP (creature trail + the pillar body) ────────────────────

def _bark_band_repeat(surf, cx, y0, band_h, half_w, ss):
    """ONE repeat of the bark-art ribbon: a pipeclay DOT-band stacked over an
    ochre HATCH-band on the charcoal ground. This is the unit that TILES
    top<->bottom — exactly one dot-band + one hatch-band per repeat. Pure flat
    motifs; the alternation is the read."""
    # Charcoal ground for this repeat (the dominant mass of the ribbon).
    pygame.draw.rect(surf, CHAR, (int(cx - half_w), int(y0), int(2 * half_w), int(band_h)))

    # Top half: a pipeclay dot-band — ONE clean row of larger, well-spaced dots.
    # (Two tight rows merged into grain at true obstacle scale; the protected
    # tell must stay a COUNTABLE motif, not a dense field — fewer/bigger dots.)
    dot_y = y0 + band_h * 0.28
    _dot_row(surf, cx, dot_y, half_w * 0.62, 4, half_w * 0.215, PIPECLAY,
             key_col=PIPECLAY_DK, ss=ss)

    # A thin charcoal-dark seam between the two bands (graphic divider).
    seam_y = y0 + band_h * 0.52
    pygame.draw.line(surf, CHAR_DK, (int(cx - half_w), int(seam_y)),
                     (int(cx + half_w), int(seam_y)), max(2, int(2.4 * ss)))

    # Bottom half: an ochre cross-hatch band.
    hatch_y0 = y0 + band_h * 0.60
    hatch_y1 = y0 + band_h * 0.92
    _hatch_band(surf, cx, hatch_y0, hatch_y1, half_w * 0.72, OCHRE_D, ss, n=7)
    _hatch_band(surf, cx, hatch_y0, hatch_y1, half_w * 0.72, OCHRE_L, ss, n=7,
                cross=False)

    # Twin ochre rail-lines down both edges so the ribbon reads as one strip.
    for s in (-1, 1):
        pygame.draw.line(surf, OCHRE_D, (int(cx + s * half_w * 0.92), int(y0)),
                         (int(cx + s * half_w * 0.92), int(y0 + band_h)),
                         max(1, int(1.8 * ss)))


def _bark_strip(surf, cx, top_y, length, half_w, ss, *, n_repeats):
    """The bark-art STRIP streaming straight DOWN: charcoal ground with stacked
    dot-band + hatch-band repeats — the band that TILES for the pillar. NO ember
    here (ember is cap-only). The dot cadence + the charcoal/pipeclay value
    contrast are the accessibility read."""
    band_h = length / n_repeats
    for i in range(n_repeats):
        _bark_band_repeat(surf, cx, top_y + i * band_h, band_h, half_w, ss)
    # A continuous ink keyline up both long edges so the strip POPS as one ribbon.
    for s in (-1, 1):
        pygame.draw.line(surf, INK, (int(cx + s * half_w), int(top_y)),
                         (int(cx + s * half_w), int(top_y + length)),
                         max(1, int(1.6 * ss)))


# ── the whole creature: plank-mask + trailing bark strip, on one surface ──────

def _face_tell(surf, cx, cy, hw, hh, ss):
    """A baked LOW-RES face tell: two fat pipeclay ring-dots (light) ringing two
    ink pupils + a single pipeclay grin-bar, sized so smoothscale to true 32px
    PRESERVES a recognizable two-eyed dotted mask instead of mushing to noise.
    At showcase scale it hides under the real rings; at icon scale it is what
    survives, carrying the 'dotted plank-mask, not a striped rope' read."""
    eye_dx = hw * 0.42
    eye_y = cy - hh * 0.04
    eye_r = hw * 0.30
    for s in (-1, 1):
        ex = cx + s * eye_dx
        pygame.draw.circle(surf, OCHRE_D, (int(ex), int(eye_y)), int(eye_r * 1.06))
        pygame.draw.circle(surf, PIPECLAY, (int(ex), int(eye_y)), int(eye_r))
        pygame.draw.circle(surf, INK, (int(ex), int(eye_y)), int(eye_r * 0.48))
    # A single wide pipeclay grin-bar that survives downscale.
    gw = hw * 0.50
    gy = cy + hh * 0.60
    gh = hh * 0.12
    pygame.draw.rect(surf, PIPECLAY,
                     pygame.Rect(int(cx - gw), int(gy - gh), int(2 * gw), int(2 * gh)),
                     border_radius=int(gh))


def build_mokoi(scale=1.0, ss=5, *, blink=False, compact=False):
    """The full creature on its own transparent surface: the oversized plank-mask
    up top, a bark-art strip streaming straight down beneath it. Returns an
    outlined surface. The elevated pipeline renders LARGE at SS=5-6 then
    smoothscales down so the dense geometry stays crisp.

    `compact` is the GAMEPLAY / 32px-icon variant: the MASK is grown to dominate
    the vertical budget and the strip is cut to ~1.2x the mask height with 1
    repeat, so the icon reads 'dotted plank-mask on a short striped strip' — not
    a striped squiggle with a speck. Compact bakes a low-res face tell."""
    mask_hw = int(40 * scale) * ss
    mask_hh = int(48 * scale) * ss
    # Privilege the mask in the icon budget. Showcase keeps a long 3-repeat
    # strip; compact cuts it to a single SHORT stub so the MASK owns ~72% of the
    # vertical budget at true 32px — the read is "dotted plank-mask with a stub
    # of strip," head unmistakably the hero (not a striped bar with a blob).
    strip_mult = 0.38 if compact else 1.9
    strip_len = int(mask_hh * 2 * strip_mult)
    n_repeats = 1 if compact else 3
    half_w = int(mask_hw * 0.46)
    side_pad = int(10 * scale) * ss
    top_pad = int(12 * scale) * ss
    bot_pad = int(14 * scale) * ss

    W = int((mask_hw + side_pad) * 2)
    cx = W // 2
    mask_cy = top_pad + mask_hh
    strip_top_y = mask_cy + mask_hh * 0.96
    feet_y = strip_top_y + strip_len
    H = int(feet_y + bot_pad)

    surf = pygame.Surface((W, H), pygame.SRCALPHA)

    # The bark strip first so the mask board occludes its top edge.
    _bark_strip(surf, cx, strip_top_y, strip_len, half_w, ss, n_repeats=n_repeats)
    # A short charcoal collar-board behind the mask base so the strip springs
    # from under the board (the carved-totem join).
    pygame.draw.rect(surf, CHAR, (int(cx - mask_hw * 0.5),
                                  int(mask_cy + mask_hh * 0.6),
                                  int(mask_hw), int(mask_hh * 0.5)))

    _mask_head(surf, cx, mask_cy, mask_hw, mask_hh, ss, blink=blink)
    if compact:
        _face_tell(surf, cx, mask_cy, mask_hw, mask_hh, ss)

    out_w = int(surf.get_width() / ss)
    out_h = int(surf.get_height() / ss)
    smallv = pygame.transform.smoothscale(surf, (out_w, out_h))
    return _add_outline(smallv)


# ── pillar pair (prop -> pillar mirror proof) ────────────────────────────────

OVERHANG = 12


def _strip_column(surf, cx, top_y, bot_y, half_w, ss):
    """The repeatable PILLAR BODY: the bark-art strip as a straight tiling shaft
    — exactly one pipeclay dot-band + one ochre hatch-band per repeat on the
    charcoal ground (the band that mirrors top<->bottom). Drawn vertical so it
    tiles cleanly along the post. NO ember here — ember is cap-only."""
    length = bot_y - top_y
    band = half_w * 2.6
    n = max(1, int(round(length / band)))
    band = length / n
    for i in range(n):
        _bark_band_repeat(surf, cx, top_y + i * band, band, half_w, ss)
    for s in (-1, 1):
        pygame.draw.line(surf, INK, (int(cx + s * half_w), int(top_y)),
                         (int(cx + s * half_w), int(bot_y)), max(1, int(1.6 * ss)))


def _totem_cap(surf, cx, cap_base_y, half_w, ss, *, point_up, night=False):
    """The creature-derived GAP-EDGE CAP: a small totem-PLAQUE — a sibling
    plank-mask sized ~strip+30% — sitting at the strip end facing the gap, with
    the EMBER glow CONFINED to this cap (the only warm light anywhere). A modest
    plaque, never a top-heavy slab. `point_up` faces the plaque toward the gap."""
    d = -1 if point_up else 1
    plaque_hw = half_w * 1.20          # cap ~ strip + 20%, no top-heavy slab
    plaque_hh = plaque_hw * 1.15
    cy = cap_base_y + d * (plaque_hh + half_w * 0.4)

    # Ember glow CONFINED to the cap — radiates INTO the gap. This is the lone
    # warm light in the whole pillar; the shaft stays charcoal+pipeclay+ochre.
    # Night alpha + radius pulled DOWN so the halo stays a contained cap glow and
    # does not bloom into the gap/shaft and crown-heavy the silhouette.
    gr = int(plaque_hw * (1.35 if night else 1.2))
    gy = cap_base_y + d * half_w * 0.4
    gl = make_glow_surface(gr, EMBER, alpha_center=160 if night else 125, falloff=2.4)
    surf.blit(gl, (int(cx - gr), int(gy - gr)), special_flags=pygame.BLEND_ADD)

    # The plaque board (charcoal ground, flat).
    _plank_outline(surf, cx, cy, plaque_hw, plaque_hh, ss, CHAR)
    # A pipeclay dot-ring framing the plaque (the tell, on the cap too). Fewer
    # dots so the cap doesn't read heavier than the shaft at the gap line.
    ring_n = 8
    for i in range(ring_n):
        a = 2 * math.pi * (i / ring_n)
        rx = cx + math.cos(a) * plaque_hw * 0.74
        ry = cy + math.sin(a) * plaque_hh * 0.74
        pygame.draw.circle(surf, PIPECLAY, (int(rx), int(ry)), max(1, int(plaque_hw * 0.10)))
    # A single concentric ring-eye centre — the totem stares back from the cap.
    _ring_eye(surf, cx, cy, plaque_hw * 0.42, ss)
    # The ember twinkle core sits in the pupil so the warm light reads as the
    # plaque's lit eye, not a free-floating spark.
    pygame.draw.circle(surf, EMBER, (int(cx), int(cy)), max(1, int(plaque_hw * 0.14)))
    pygame.draw.circle(surf, EMBER_HOT, (int(cx), int(cy)), max(1, int(plaque_hw * 0.07)))


def _strip_pillar_obstacle(height, ss, *, flip, night=False):
    """One bark-art STRIP pillar obstacle: the dot/hatch strip fills the post and
    a totem-plaque CAP sits at the GAP-facing edge, its ember glow radiating INTO
    the gap. `flip=True` is the TOP pillar — cap at the bottom (gap) edge;
    `flip=False` is the BOTTOM pillar — cap at the top (gap) edge. Both mirror
    the same dot+hatch body into a clean vertical strip-pillar."""
    bw = (PIPE_W + 2 * OVERHANG) * ss
    bh = max(1, int(height)) * ss
    surf = pygame.Surface((bw, bh), pygame.SRCALPHA)
    cx = bw // 2
    half_w = int((PIPE_W * 0.42)) * ss
    cap_band = int(54 * ss)
    if flip:
        _strip_column(surf, cx, 0, bh - cap_band, half_w, ss)
        _totem_cap(surf, cx, bh - cap_band, half_w, ss, point_up=False, night=night)
    else:
        _strip_column(surf, cx, cap_band, bh, half_w, ss)
        _totem_cap(surf, cx, cap_band, half_w, ss, point_up=True, night=night)
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

    SW, SH = 1080, 770
    sheet = pygame.Surface((SW, SH))
    sheet.fill((120, 120, 124))            # neutral grey bg
    _label(sheet, font,
           "MOKOI  —  leyak-epic  —  flat plank-mask + bark-art strip  —  round 2",
           18, 12, (24, 24, 28))
    _label(sheet, small,
           "FLAT-GRAPHIC: charcoal-dominant ground, twin-ochre accents, pipeclay-white dot-pattern as the protected tell; ember CONFINED to the cap. SS=6 hero, no gradients/3D shading.",
           18, 32, (40, 40, 46))

    # — Cell A: the BIG hero plank-mask on a neutral panel (elevated SS=6).
    panel = pygame.Rect(18, 56, 320, 600)
    pygame.draw.rect(sheet, (96, 96, 100), panel, border_radius=8)
    pygame.draw.rect(sheet, (60, 60, 64), panel, 2, border_radius=8)
    _label(sheet, font, "(a) HERO  big scale  SS=6", panel.x + 8, panel.y + 8, (245, 240, 230))
    hero = build_mokoi(scale=1.7, ss=6)
    sheet.blit(hero, (panel.centerx - hero.get_width() // 2, panel.y + 44))
    _label(sheet, small, "plank-mask + 3-repeat dot/hatch bark strip", panel.x + 8, panel.y + 28,
           (235, 230, 220))

    # — Cell B: strip as a tileable PILLAR pair at TRUE obstacle scale, on NIGHT,
    #   plus a 2x zoom of the CAP band proving the contained ember + the mirror.
    panelB = pygame.Rect(348, 56, 320, 600)
    bg = _sky(panelB.w, panelB.h, (8, 8, 30), (20, 18, 52), (40, 30, 70), stars=True)
    sheet.blit(bg, panelB.topleft)
    pygame.draw.rect(sheet, (60, 60, 64), panelB, 2, border_radius=8)
    _label(sheet, font, "(b) PROP -> PILLAR  @ TRUE  (NIGHT)", panelB.x + 8, panelB.y + 8)

    pw = PIPE_W + 2 * OVERHANG
    slice_h = 500
    slice_x = panelB.x + 22
    slice_y = panelB.y + 44
    gap_top = 158
    gap_h = 124
    top_h = gap_top
    bot_h = slice_h - gap_top - gap_h
    top_pillar = _strip_pillar_obstacle(top_h, 4, flip=True, night=True)
    bot_pillar = _strip_pillar_obstacle(bot_h, 4, flip=False, night=True)
    sheet.blit(top_pillar, (slice_x - 2, slice_y - 2))
    sheet.blit(bot_pillar, (slice_x - 2, slice_y + gap_top + gap_h - 2))
    pygame.draw.rect(sheet, (210, 200, 180), (slice_x - 4, slice_y - 4, pw + 8, slice_h + 8), 1)
    _label(sheet, small, "1x native (82px): dot-band +", slice_x - 2, slice_y + slice_h + 6,
           (235, 225, 210))
    _label(sheet, small, "hatch-band per repeat tiles; ember on CAP only",
           slice_x - 2, slice_y + slice_h + 22, (255, 210, 150))

    cap_band = 54
    zw, zh = pw, 150
    zoom_src = pygame.Surface((zw, zh), pygame.SRCALPHA)
    top_anchor = 14
    zoom_src.blit(top_pillar, (-2, -(top_h - cap_band - top_anchor) - 2))
    zoom_gap = zh - 2 * cap_band - 2 * top_anchor
    bot_anchor = top_anchor + cap_band + zoom_gap
    zoom_src.blit(bot_pillar, (-2, bot_anchor - 2))
    zoom = pygame.transform.scale(zoom_src, (zw * 2, zh * 2))
    zx = panelB.x + 170
    zy = panelB.y + 110
    zbg = _sky(zw * 2, zh * 2, (8, 8, 30), (16, 14, 44), (28, 20, 58))
    sheet.blit(zbg, (zx, zy))
    pygame.draw.rect(sheet, (210, 200, 180), (zx - 1, zy - 1, zw * 2 + 2, zh * 2 + 2), 1)
    sheet.blit(zoom, (zx, zy))
    _label(sheet, small, "2x zoom CAP band:", zx - 2, zy - 16, (255, 255, 255))
    _label(sheet, small, "totem-plaque cap;", zx - 2, zy + zh * 2 + 6, (255, 210, 150))
    _label(sheet, small, "ember radiates INTO gap", zx - 2, zy + zh * 2 + 22, (255, 210, 150))

    # — Cell C: TRUE 32px gameplay chip on a DAY sky AND a NIGHT sky, plus a 4x
    #   audit + grayscale tell-check.
    panelC = pygame.Rect(678, 56, 384, 600)
    pygame.draw.rect(sheet, (96, 96, 100), panelC, border_radius=8)
    pygame.draw.rect(sheet, (60, 60, 64), panelC, 2, border_radius=8)
    _label(sheet, font, "(c) TRUE 32px gameplay chip", panelC.x + 8, panelC.y + 8, (245, 240, 230))
    _label(sheet, small, "head-dominant compact; day + night skies", panelC.x + 8, panelC.y + 28,
           (235, 230, 220))

    # The compact gameplay creature blown up for a clear day/night read.
    boss = build_mokoi(scale=0.62, ss=5, compact=True)
    day = _sky(140, 280, (40, 110, 200), (90, 170, 230), (170, 220, 245))
    night = _sky(140, 280, (8, 8, 30), (20, 18, 52), (40, 30, 70), stars=True)
    dy = panelC.y + 48
    sheet.blit(day, (panelC.x + 16, dy))
    sheet.blit(night, (panelC.x + 168, dy))
    sheet.blit(boss, (panelC.x + 16 + 70 - boss.get_width() // 2, dy + 8))
    sheet.blit(boss, (panelC.x + 168 + 70 - boss.get_width() // 2, dy + 8))
    _label(sheet, small, "DAY", panelC.x + 16 + 6, dy + 6, (18, 28, 24))
    _label(sheet, small, "NIGHT", panelC.x + 168 + 6, dy + 6, (255, 220, 200))

    # The TRUE-32 icon: shown at 1x on day/night/dusk chips, then 4x audit + gray.
    icon_src = build_mokoi(scale=1.0, ss=5, compact=True)
    sc32 = 32 / icon_src.get_height()
    icon32 = pygame.transform.smoothscale(
        icon_src, (max(1, int(icon_src.get_width() * sc32)), 32))
    sc64 = 64 / icon_src.get_height()
    icon64 = pygame.transform.smoothscale(
        icon_src, (max(1, int(icon_src.get_width() * sc64)), 64))

    gy = dy + 296
    _label(sheet, small, "TRUE 32px at 1x (no blow-up):", panelC.x + 16, gy - 2,
           (235, 225, 215))
    swatches = [
        ((40, 110, 200), "day"),
        ((40, 30, 70), "night"),
        ((96, 96, 100), "neutral"),
    ]
    sx = panelC.x + 16
    sw = 92
    for col, lab in swatches:
        chip = pygame.Rect(sx, gy + 16, sw, 76)
        pygame.draw.rect(sheet, col, chip, border_radius=4)
        sheet.blit(icon32, (chip.centerx - icon32.get_width() // 2,
                            chip.centery - icon32.get_height() // 2))
        _label(sheet, small, lab, chip.x + 4, chip.y + 2, (240, 240, 240))
        sx += sw + 8

    # 4x nearest-neighbour blow-up of the true-32 icon so the tell is auditable,
    # plus the grayscale value check (the protected dot tell must survive).
    chip = pygame.Rect(panelC.x + 16, gy + 104, 86, 100)
    pygame.draw.rect(sheet, (78, 78, 82), chip, border_radius=4)
    blow = pygame.transform.scale(icon32, (icon32.get_width() * 3, icon32.get_height() * 3))
    sheet.blit(blow, (chip.x + 6, chip.centery - blow.get_height() // 2))
    sheet.blit(icon64, (chip.right + 10, chip.centery - icon64.get_height() // 2))
    _label(sheet, small, "3x / 64px audit", chip.x + 4, chip.y + 2, (240, 240, 240))

    gray = _to_gray(icon64)
    gchip = pygame.Rect(panelC.x + 250, gy + 104, 100, 100)
    pygame.draw.rect(sheet, (124, 128, 124), gchip, border_radius=4)
    sheet.blit(gray, (gchip.centerx - gray.get_width() // 2,
                      gchip.centery - gray.get_height() // 2))
    _label(sheet, small, "grayscale tell", gchip.x + 4, gchip.y + 2, (24, 24, 24))

    # — Footer: style notes.
    _label(sheet, small,
           "FLAT only: detail via PATTERN DENSITY (dot-rows + cross-hatch), never 3D shading; charcoal dominant; twin-ochre minor; pipeclay dots are the protected hue-blind tell.",
           18, SH - 64, (40, 40, 46))
    _label(sheet, small,
           "prop->pillar: bark strip = 1 pipeclay dot-band + 1 ochre hatch-band per repeat (tiles); gap-edge cap = a creature-derived totem-plaque w/ ember CONFINED to the cap. Clean mirror.",
           18, SH - 44, (40, 40, 46))

    out_dir = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(out_dir, "round_2.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path)


if __name__ == "__main__":
    main()
