"""Look-dev sheet for the Skybit BOSS mokoi-spin-off — "QUINKAN-IMJIM".

Quinkan Imjim reframed as a FLAT painted-spirit knob-on-a-stalk: a squat,
goofy bulb-head bobbing on a too-thin neck, lurking by the trail to thump you.
Where the parent Mokoi is a floating plank-MASK, the Imjim is the brood's only
KNOB-TOP / low-lurking read — a lollipop. The whole creature, and its pillar,
is the knob-tipped club / digging-stick the imp ambushes with.

House style this obeys (mokoi flat-graphic dialect):
  - CHIBI proportions — a FAT knob-head on a THIN neck-stalk so the lollipop
    silhouette is unmistakable at true 32px. The fat-knob / thin-stalk ratio is
    the hard rule: body detail must never compete with the knob for the eye.
  - FLAT saturated fills. NO within-shape gradients, NO bevels, NO soft edges.
    Detail is PATTERN DENSITY — the pipeclay-white concentric KNOB-BANDS are the
    tell (a target carved into the bulb), red-ochre dot-columns + handprint
    stamps band the shaft. NOT 3D triad shading.
  - Hard 1-2px ink keyline (28,22,30) inside + a 1px grown outline on the
    silhouette so the club POPS on any sky (the parrot `_add_outline` recipe).
  - Charcoal is the DOMINANT mass with a RED-ochre lean; brick-red-ochre is the
    dot/stamp accent; the pipeclay-white concentric knob-bands are the protected
    hue-blind tell; a thin yellow-ochre rim edges the knob. Ember CAP-only.
  - SUPERSAMPLE at SS=5-6 then smoothscale down — crisp geometry at downscale.

Accessibility tell: the pipeclay-white concentric knob-bands + the high
charcoal/pipeclay value contrast carry the read independent of hue. No warm hue
anywhere except the contained cap ember.

Prop -> pillar mirror: the knob-tipped CLUB itself is the pillar. One
red-ochre DOT-COLUMN band + one red-ochre HANDPRINT-STAMP band per repeat tile
the shaft; a round KNOB-HEAD finial (~strip+30%) = the gap-edge cap, ember
confined to that cap. On-axis, clean vertical mirror.

    SDL_VIDEODRIVER=dummy PYTHONPATH=/home/user/skybit python docs/skybit_devil/batch2/mokoi_versions/quinkan_imjim/render_quinkan_imjim.py
"""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from game.draw import lerp_color, make_glow_surface
from game.config import PIPE_W


pygame.init()

# ── PINNED PALETTE (quinkan-imjim) — hex-exact from the locked brief ─────────
# Charcoal is the DOMINANT mass with a RED-ochre lean (warmer than Baiame's
# neutral charcoal). Brick-red-ochre is the dot/stamp accent. Pipeclay-white is
# the protected tell — the concentric knob-bands carry the read in grayscale. A
# thin yellow-ochre rim edges the knob. Ember is the lone warm glow, cap-only.
CHAR        = (48, 42, 46)      # charcoal body, red-ochre lean (dominant)
CHAR_DK     = (32, 28, 33)      # deeper charcoal for wells / seams
CHAR_HI     = (66, 56, 60)      # flat lighter charcoal for graphic separation

BRICK       = (180, 84, 58)     # brick-red-ochre dot / handprint stamp
BRICK_DK    = (132, 58, 40)     # deep brick for stamp keylines / shadow-edge

PIPECLAY    = (232, 226, 212)   # pipeclay-white — the protected band tell
PIPECLAY_DK = (190, 184, 170)   # quiet shade for band keylines (still light)

YELLOW_RIM  = (206, 150, 72)    # thin yellow-ochre rim (knob edge only)

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

def _dot_column(surf, cx, y0, y1, r, col, *, key_col=None, ss=3, n=None):
    """A vertical COLUMN of evenly-spaced brick-red dots down the shaft centre —
    the protected motif on the club body. Flat filled circles with an optional
    keyline so the column stays a COUNTABLE row of stamps, not a smear."""
    if n is None:
        n = max(2, int((y1 - y0) / (r * 3.2)))
    if n == 1:
        ys = [(y0 + y1) * 0.5]
    else:
        ys = [y0 + (y1 - y0) * (i / (n - 1)) for i in range(n)]
    for y in ys:
        pygame.draw.circle(surf, col, (int(cx), int(y)), int(r))
        if key_col is not None:
            pygame.draw.circle(surf, key_col, (int(cx), int(y)), int(r),
                               max(1, int(ss * 0.6)))


def _handprint(surf, cx, cy, w, ss, col, key=None):
    """A flat red-ochre HANDPRINT stamp — a palm disc with five short stub
    fingers fanning UP. A folk rock-art motif, drawn as hard flat fills (the
    second shaft band, alternating with the dot-column). Graphic, not shaded."""
    palm_r = w * 0.34
    pygame.draw.circle(surf, col, (int(cx), int(cy)), int(palm_r))
    # Five stub fingers fanning up from the palm top.
    for i, a in enumerate((-0.95, -0.5, 0.0, 0.5, 0.95)):
        # Middle finger longest, thumbs shortest — a recognizable hand.
        fl = palm_r * (1.5 if i == 2 else (1.25 if i in (1, 3) else 0.95))
        fr = palm_r * 0.30
        fx = cx + math.sin(a) * palm_r * 0.78
        fy = cy - math.cos(a) * palm_r * 0.55
        tx = cx + math.sin(a) * (palm_r * 0.5 + fl)
        ty = cy - math.cos(a) * (palm_r * 0.5 + fl)
        pygame.draw.line(surf, col, (int(fx), int(fy)), (int(tx), int(ty)),
                         max(2, int(fr)))
        pygame.draw.circle(surf, col, (int(tx), int(ty)), int(fr * 0.5))
    if key is not None:
        pygame.draw.circle(surf, key, (int(cx), int(cy)), int(palm_r),
                           max(1, int(ss * 0.7)))


# ── the FAT knob-head (the hero read) ────────────────────────────────────────

def _knob_base(surf, cx, cy, r, ss):
    """The fat bulb GROUND for the imp's face — a charcoal disc edged by a thin
    yellow-ochre rim and a single PARTIAL pipeclay brow-arc. Deliberately NOT a
    set of concentric rings: the bands are demoted to one open top-of-skull arc
    (a painted brow stripe) + one short brick chin-mark, so the bulb never reads
    as a bullseye. The big asymmetric eyes + mouth (drawn after) are the
    dominant marks; this is just the field they sit on.

    The asymmetry is the whole point — a concentric target survives downscale as
    rings, but an off-centre brow + chin breaks that symmetry so at 32px the eye
    reads a FACE on a bulb, not a dartboard on a stick."""
    # Thin yellow-ochre rim, then the charcoal bulb field it edges.
    pygame.draw.circle(surf, YELLOW_RIM, (int(cx), int(cy)), int(r))
    pygame.draw.circle(surf, CHAR, (int(cx), int(cy)), int(r * 0.90))
    # ONE partial pipeclay brow-band hugging the top of the skull — an open arc,
    # not a closed ring, so it can't ring as a target. It also frames the eyes.
    brow = pygame.Rect(int(cx - r * 0.72), int(cy - r * 0.80),
                       int(r * 1.44), int(r * 1.10))
    pygame.draw.arc(surf, PIPECLAY, brow, math.radians(28), math.radians(152),
                    max(2, int(r * 0.16)))
    pygame.draw.arc(surf, INK, brow, math.radians(28), math.radians(152),
                    max(1, int(0.8 * ss)))
    # ONE short brick chin-mark low + off the centre line — warm tell, asymmetric.
    chin = pygame.Rect(int(cx - r * 0.40), int(cy + r * 0.52),
                       int(r * 0.74), int(r * 0.34))
    pygame.draw.arc(surf, BRICK, chin, math.radians(200), math.radians(340),
                    max(2, int(r * 0.13)))
    # Crisp ink keyline on the bulb edge so the knob POPS.
    pygame.draw.circle(surf, INK, (int(cx), int(cy)), int(r), max(1, int(1.6 * ss)))


def _imp_face(surf, cx, cy, r, ss, *, blink=False):
    """The goofy CROSS-EYED imp face — the dominant marks on the bulb, authored
    to survive at TRUE 32px. Two BIG high-contrast asymmetric eyes (pipeclay
    whites, hard charcoal pupils that converge cross-eyed) and one decisive
    charcoal mouth-bar with fang-notches. Sized so the eyes+mouth, not the
    bands, win the focal at native res — read the 1x chip and it's a face.

    Asymmetry is deliberate: the eyes sit at slightly different heights/sizes and
    the pupils cross inward, so the knob can never collapse into concentric
    symmetry the way a tidy two-eye target would."""
    # Big eyes, set wide and high, intentionally unequal — goofy, never tidy.
    eye_dx = r * 0.40
    # Left eye a touch larger + lower; right smaller + higher — broken symmetry.
    specs = (
        (-1, eye_dx * 1.02, cy - r * 0.10, r * 0.34),
        (+1, eye_dx * 0.96, cy - r * 0.18, r * 0.30),
    )
    if blink:
        for s, dx, ey, er in specs:
            ex = cx + s * dx
            pygame.draw.line(surf, INK, (int(ex - er), int(ey)),
                             (int(ex + er), int(ey)), max(2, int(0.5 * er)))
    else:
        for s, dx, ey, er in specs:
            ex = cx + s * dx
            # Big pipeclay sclera with a hard ink keyline — high value contrast
            # so the eye punches through at 32px as a clear light blob + dark dot.
            pygame.draw.circle(surf, PIPECLAY, (int(ex), int(ey)), int(er))
            pygame.draw.circle(surf, INK, (int(ex), int(ey)), int(er),
                               max(1, int(1.4 * ss)))
            # Fat charcoal pupil pulled INWARD (cross-eyed toward the nose) — the
            # goofy ambush-imp read, and it forces left/right asymmetry.
            pup_r = er * 0.62
            px = ex - s * er * 0.34
            pygame.draw.circle(surf, INK, (int(px), int(ey + er * 0.06)), int(pup_r))
            # Tiny catch-light so the pupil reads as an eye, not a hole.
            pygame.draw.circle(surf, PIPECLAY,
                               (int(px - s * pup_r * 0.3), int(ey - pup_r * 0.3)),
                               max(1, int(pup_r * 0.30)))
    # One decisive charcoal mouth-BAR low on the bulb — a wide flat well that
    # survives downscale as a single dark horizontal mark (matches the Mokoi
    # parent's bar-mouth read), with two pipeclay fang-notches biting up.
    grin_y = cy + r * 0.40
    grin_hw = r * 0.42
    grin_h = r * 0.15
    mouth = pygame.Rect(int(cx - grin_hw), int(grin_y - grin_h),
                        int(2 * grin_hw), int(2 * grin_h))
    pygame.draw.rect(surf, CHAR_DK, mouth, border_radius=int(grin_h * 0.6))
    pygame.draw.rect(surf, INK, mouth, max(1, int(1.4 * ss)),
                     border_radius=int(grin_h * 0.6))
    # Two stubby pipeclay fangs poking UP from the lower lip — goofy-menacing.
    for s in (-1, 1):
        fx = cx + s * grin_hw * 0.45
        pts = [(fx - grin_hw * 0.18, grin_y + grin_h * 0.55),
               (fx + grin_hw * 0.18, grin_y + grin_h * 0.55),
               (fx, grin_y - grin_h * 0.4)]
        pygame.draw.polygon(surf, PIPECLAY, [(int(x), int(y)) for x, y in pts])


# ── the THIN neck-stalk + squat foot (the club shaft as the body) ────────────

def _shaft_repeat(surf, cx, y0, band_h, half_w, ss):
    """ONE repeat of the club shaft: a brick-red DOT-COLUMN segment stacked over
    a brick-red HANDPRINT-STAMP on the charcoal ground — the unit that TILES
    top<->bottom for the pillar. Exactly one dot band + one handprint band per
    repeat. Pure flat motifs; the alternation is the read."""
    pygame.draw.rect(surf, CHAR, (int(cx - half_w), int(y0),
                                  int(2 * half_w), int(band_h)))
    # Top half: a short brick-red dot-column.
    _dot_column(surf, cx, y0 + band_h * 0.10, y0 + band_h * 0.44,
                half_w * 0.30, BRICK, key_col=BRICK_DK, ss=ss, n=3)
    # A thin charcoal-dark seam between the two motifs (graphic divider).
    seam_y = y0 + band_h * 0.52
    pygame.draw.line(surf, CHAR_DK, (int(cx - half_w), int(seam_y)),
                     (int(cx + half_w), int(seam_y)), max(2, int(2.2 * ss)))
    # Bottom half: a single brick-red handprint stamp.
    _handprint(surf, cx, y0 + band_h * 0.74, half_w * 1.05, ss, BRICK, key=BRICK_DK)
    # Twin pipeclay rail-lines down both edges so the shaft reads as one club.
    for s in (-1, 1):
        pygame.draw.line(surf, PIPECLAY_DK, (int(cx + s * half_w * 0.92), int(y0)),
                         (int(cx + s * half_w * 0.92), int(y0 + band_h)),
                         max(1, int(1.4 * ss)))


def build_quinkan(scale=1.0, ss=5, *, blink=False, compact=False):
    """The full Imjim on its own transparent surface: a FAT knob-head up top, a
    THIN neck-stalk dropping to a squat foot-club beneath it. Returns an
    outlined surface. Renders LARGE at SS=5-6 then smoothscales for crisp
    geometry.

    The lollipop ratio is the hard rule: `knob_r` is large and `neck_half` is
    small. `compact` is the GAMEPLAY / 32px-icon variant — the knob is grown to
    dominate the vertical budget and the stalk cut to a short stub so the read
    is unmistakably 'fat bulb on a thin stick,' never a striped bar with a blob."""
    knob_r = int(46 * scale) * ss
    neck_half = int(8 * scale) * ss     # THIN stalk — kept narrow on purpose
    # Privilege the knob in the icon budget. Showcase keeps a longer club shaft;
    # compact cuts it to a short stub so the KNOB owns most of the vertical
    # budget at true 32px — the read is "fat bulb on a thin stalk."
    shaft_mult = 0.85 if compact else 2.4
    shaft_len = int(knob_r * shaft_mult)
    side_pad = int(10 * scale) * ss
    top_pad = int(10 * scale) * ss
    bot_pad = int(12 * scale) * ss

    W = int((knob_r + side_pad) * 2)
    cx = W // 2
    knob_cy = top_pad + knob_r
    neck_top = knob_cy + knob_r * 0.86
    shaft_top = neck_top + knob_r * 0.55
    foot_y = shaft_top + shaft_len
    H = int(foot_y + knob_r * 0.6 + bot_pad)

    surf = pygame.Surface((W, H), pygame.SRCALPHA)

    # The thin neck-stalk first (a charcoal column under the knob). Kept narrow
    # so the lollipop silhouette is unmistakable.
    pygame.draw.rect(surf, CHAR, (int(cx - neck_half), int(neck_top),
                                  int(2 * neck_half), int(shaft_top - neck_top + 4)))
    pygame.draw.line(surf, CHAR_DK, (int(cx), int(neck_top)),
                     (int(cx), int(shaft_top)), max(1, int(1.2 * ss)))

    # The squat foot-club shaft (the body / digging-stick) under the neck.
    shaft_half = int(neck_half * 1.7)
    n_repeats = 1 if compact else 2
    band_h = shaft_len / n_repeats
    for i in range(n_repeats):
        _shaft_repeat(surf, cx, shaft_top + i * band_h, band_h, shaft_half, ss)
    for s in (-1, 1):
        pygame.draw.line(surf, INK, (int(cx + s * shaft_half), int(shaft_top)),
                         (int(cx + s * shaft_half), int(shaft_top + shaft_len)),
                         max(1, int(1.5 * ss)))
    # A small charcoal BOOKEND-KNOB closes the club on-axis — a flat hard-edged
    # bulb echoing the head, no wider than the shaft so the lollipop silhouette
    # and the mirror stay clean (NO flared tripod / stand). One brick dot stamps
    # its centre as the last handprint-family mark; a hard ink cap, no fuzz.
    foot_r = int(shaft_half * 1.05)
    foot_cy = int(foot_y + foot_r * 0.55)
    pygame.draw.circle(surf, CHAR, (int(cx), foot_cy), foot_r)
    pygame.draw.circle(surf, INK, (int(cx), foot_cy), foot_r, max(1, int(1.5 * ss)))
    pygame.draw.circle(surf, BRICK, (int(cx), foot_cy), max(2, int(foot_r * 0.34)))
    pygame.draw.circle(surf, BRICK_DK, (int(cx), foot_cy),
                       max(2, int(foot_r * 0.34)), max(1, int(0.6 * ss)))

    # The FAT knob-head last so it occludes the stalk top — the dominant read.
    _knob_base(surf, cx, knob_cy, knob_r, ss)
    _imp_face(surf, cx, knob_cy, knob_r, ss, blink=blink)

    out_w = int(surf.get_width() / ss)
    out_h = int(surf.get_height() / ss)
    smallv = pygame.transform.smoothscale(surf, (out_w, out_h))
    return _add_outline(smallv)


# ── pillar pair (prop -> pillar mirror proof) ────────────────────────────────

OVERHANG = 12


def _club_column(surf, cx, top_y, bot_y, half_w, ss):
    """The repeatable PILLAR BODY: the club shaft as a straight tiling post —
    exactly one brick-red dot-column band + one brick-red handprint-stamp band
    per repeat on the charcoal ground. Drawn vertical so it tiles cleanly. NO
    ember here — ember is cap-only."""
    length = bot_y - top_y
    band = half_w * 3.2
    n = max(1, int(round(length / band)))
    band = length / n
    for i in range(n):
        _shaft_repeat(surf, cx, top_y + i * band, band, half_w, ss)
    for s in (-1, 1):
        pygame.draw.line(surf, INK, (int(cx + s * half_w), int(top_y)),
                         (int(cx + s * half_w), int(bot_y)), max(1, int(1.5 * ss)))


def _knob_cap(surf, cx, cap_base_y, half_w, ss, *, point_up, night=False):
    """The creature-derived GAP-EDGE CAP: the round KNOB-HEAD finial (~shaft
    +30%) sitting at the club end facing the gap, with the EMBER glow CONFINED to
    this cap. A modest knob finial, never a top-heavy slab. `point_up` faces the
    knob toward the gap."""
    d = -1 if point_up else 1
    knob_r = half_w * 1.30           # cap ~ shaft + 30%, on-axis
    cy = cap_base_y + d * (knob_r + half_w * 0.5)

    # Ember glow CONFINED to the cap — radiates INTO the gap. The lone warm light
    # in the whole pillar; the shaft stays charcoal+brick+pipeclay.
    gr = int(knob_r * (1.35 if night else 1.15))
    gy = cap_base_y + d * half_w * 0.5
    gl = make_glow_surface(gr, EMBER, alpha_center=160 if night else 120, falloff=2.4)
    surf.blit(gl, (int(cx - gr), int(gy - gr)), special_flags=pygame.BLEND_ADD)

    # A short charcoal neck-stub joining the knob to the shaft so the finial
    # reads as the club's knob, not a free disc.
    pygame.draw.rect(surf, CHAR,
                     (int(cx - half_w * 0.5),
                      int(min(cap_base_y, cy)),
                      int(half_w), int(abs(cy - cap_base_y))))

    # The knob finial carries the SAME face the hero does — so a scrolling column
    # of caps reads as a row of lurking imp-HEADS, never stacked dartboards. The
    # face-dominant authoring (eyes + mouth beat the bands) is what de-targets it.
    _knob_base(surf, cx, cy, knob_r, ss)
    _imp_face(surf, cx, cy, knob_r, ss)
    # A warm ember twinkle low in the mouth so the cap's lone warm light reads as
    # the imp's lit grin, not a free spark — still strictly cap-confined.
    em_y = cy + knob_r * 0.40
    pygame.draw.circle(surf, EMBER, (int(cx), int(em_y)), max(1, int(knob_r * 0.13)))
    pygame.draw.circle(surf, EMBER_HOT, (int(cx), int(em_y)), max(1, int(knob_r * 0.06)))


def _club_pillar_obstacle(height, ss, *, flip, night=False):
    """One knob-tipped CLUB pillar obstacle: the dot/handprint shaft fills the
    post and a round KNOB finial CAP sits at the GAP-facing edge, its ember glow
    radiating INTO the gap. `flip=True` is the TOP pillar — cap at the bottom
    (gap) edge; `flip=False` is the BOTTOM pillar. Both mirror the same
    dot+handprint body into a clean vertical club-pillar."""
    bw = (PIPE_W + 2 * OVERHANG) * ss
    bh = max(1, int(height)) * ss
    surf = pygame.Surface((bw, bh), pygame.SRCALPHA)
    cx = bw // 2
    half_w = int((PIPE_W * 0.34)) * ss
    cap_band = int(58 * ss)
    if flip:
        _club_column(surf, cx, 0, bh - cap_band, half_w, ss)
        _knob_cap(surf, cx, bh - cap_band, half_w, ss, point_up=False, night=night)
    else:
        _club_column(surf, cx, cap_band, bh, half_w, ss)
        _knob_cap(surf, cx, cap_band, half_w, ss, point_up=True, night=night)
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

    SW, SH = 1320, 770
    sheet = pygame.Surface((SW, SH))
    sheet.fill((120, 120, 124))
    _label(sheet, font,
           "QUINKAN-IMJIM  —  mokoi spin-off  —  knob-lollipop ambush-imp  —  round 2",
           18, 12, (24, 24, 28))
    _label(sheet, small,
           "FLAT-GRAPHIC: charcoal body (red-ochre lean), brick-red dot/handprint stamps, pipeclay concentric knob-bands as the tell, thin yellow-ochre rim; ember CAP-only. FAT knob + THIN stalk.",
           18, 32, (40, 40, 46))

    # — Cell A: the BIG hero lollipop on a neutral panel (elevated SS=6).
    panel = pygame.Rect(18, 56, 320, 600)
    pygame.draw.rect(sheet, (96, 96, 100), panel, border_radius=8)
    pygame.draw.rect(sheet, (60, 60, 64), panel, 2, border_radius=8)
    _label(sheet, font, "(a) HERO  big scale  SS=6", panel.x + 8, panel.y + 8, (245, 240, 230))
    hero = build_quinkan(scale=1.7, ss=6)
    sheet.blit(hero, (panel.centerx - hero.get_width() // 2, panel.y + 48))
    _label(sheet, small, "fat knob-head + thin neck + dot/handprint club", panel.x + 8, panel.y + 28,
           (235, 230, 220))

    # — Cell B: club as a tileable PILLAR pair at TRUE obstacle scale, on NIGHT,
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
    gap_h = 130
    top_h = gap_top
    bot_h = slice_h - gap_top - gap_h
    top_pillar = _club_pillar_obstacle(top_h, 4, flip=True, night=True)
    bot_pillar = _club_pillar_obstacle(bot_h, 4, flip=False, night=True)
    sheet.blit(top_pillar, (slice_x - 2, slice_y - 2))
    sheet.blit(bot_pillar, (slice_x - 2, slice_y + gap_top + gap_h - 2))
    pygame.draw.rect(sheet, (210, 200, 180), (slice_x - 4, slice_y - 4, pw + 8, slice_h + 8), 1)
    _label(sheet, small, "1x native: dot-column +", slice_x - 2, slice_y + slice_h + 6,
           (235, 225, 210))
    _label(sheet, small, "handprint per repeat tiles; ember on CAP knob only",
           slice_x - 2, slice_y + slice_h + 22, (255, 210, 150))

    cap_band = 58
    zw, zh = pw, 160
    zoom_src = pygame.Surface((zw, zh), pygame.SRCALPHA)
    top_anchor = 16
    zoom_src.blit(top_pillar, (-2, -(top_h - cap_band - top_anchor) - 2))
    zoom_gap = zh - 2 * cap_band - 2 * top_anchor
    bot_anchor = top_anchor + cap_band + zoom_gap
    zoom_src.blit(bot_pillar, (-2, bot_anchor - 2))
    zoom = pygame.transform.scale(zoom_src, (zw * 2, zh * 2))
    zx = panelB.x + 168
    zy = panelB.y + 100
    zbg = _sky(zw * 2, zh * 2, (8, 8, 30), (16, 14, 44), (28, 20, 58))
    sheet.blit(zbg, (zx, zy))
    pygame.draw.rect(sheet, (210, 200, 180), (zx - 1, zy - 1, zw * 2 + 2, zh * 2 + 2), 1)
    sheet.blit(zoom, (zx, zy))
    _label(sheet, small, "2x zoom CAP band:", zx - 2, zy - 16, (255, 255, 255))
    _label(sheet, small, "knob-head finial;", zx - 2, zy + zh * 2 + 6, (255, 210, 150))
    _label(sheet, small, "mirror + ember INTO gap", zx - 2, zy + zh * 2 + 22, (255, 210, 150))

    # — Cell C: TRUE 32px gameplay chip on a DAY sky AND a NIGHT sky, plus a 3x
    #   audit + grayscale tell-check.
    panelC = pygame.Rect(678, 56, 384, 600)
    pygame.draw.rect(sheet, (96, 96, 100), panelC, border_radius=8)
    pygame.draw.rect(sheet, (60, 60, 64), panelC, 2, border_radius=8)
    _label(sheet, font, "(c) TRUE 32px gameplay chip", panelC.x + 8, panelC.y + 8, (245, 240, 230))
    _label(sheet, small, "knob-dominant compact; day + night skies", panelC.x + 8, panelC.y + 28,
           (235, 230, 220))

    # The compact gameplay creature blown up for a clear day/night read.
    boss = build_quinkan(scale=0.62, ss=5, compact=True)
    day = _sky(140, 280, (40, 110, 200), (90, 170, 230), (170, 220, 245))
    night = _sky(140, 280, (8, 8, 30), (20, 18, 52), (40, 30, 70), stars=True)
    dy = panelC.y + 48
    sheet.blit(day, (panelC.x + 16, dy))
    sheet.blit(night, (panelC.x + 168, dy))
    sheet.blit(boss, (panelC.x + 16 + 70 - boss.get_width() // 2, dy + 8))
    sheet.blit(boss, (panelC.x + 168 + 70 - boss.get_width() // 2, dy + 8))
    _label(sheet, small, "DAY", panelC.x + 16 + 6, dy + 6, (18, 28, 24))
    _label(sheet, small, "NIGHT", panelC.x + 168 + 6, dy + 6, (255, 220, 200))

    # The TRUE-32 icon: shown at 1x on day/night/neutral chips, then 3x audit + gray.
    icon_src = build_quinkan(scale=1.0, ss=5, compact=True)
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

    # — Cell D: a SCROLLING COLUMN of 3-4 repeating pillars at 1x, day + night,
    #   to confirm the caps read as a row of imp-HEADS, not stacked dartboards.
    panelD = pygame.Rect(1074, 56, 230, 600)
    pygame.draw.rect(sheet, (96, 96, 100), panelD, border_radius=8)
    pygame.draw.rect(sheet, (60, 60, 64), panelD, 2, border_radius=8)
    _label(sheet, font, "(d) SCROLL @ 1x", panelD.x + 8, panelD.y + 8, (245, 240, 230))
    _label(sheet, small, "caps = imp-HEADS, not", panelD.x + 8, panelD.y + 28, (235, 230, 220))
    _label(sheet, small, "stacked targets", panelD.x + 8, panelD.y + 42, (235, 230, 220))

    pw = PIPE_W + 2 * OVERHANG
    for col_i, (sky_cols, lab, night) in enumerate((
            (((40, 110, 200), (90, 170, 230), (170, 220, 245)), "day", False),
            (((8, 8, 30), (20, 18, 52), (40, 30, 70)), "night", True))):
        col_x = panelD.x + 14 + col_i * (pw + 26)
        col_y = panelD.y + 64
        col_h = 510
        cbg = _sky(pw, col_h, *sky_cols, stars=night)
        sheet.blit(cbg, (col_x, col_y))
        pygame.draw.rect(sheet, (60, 60, 64), (col_x, col_y, pw, col_h), 1)
        # Three repeating top pillars marching down the column with gaps, so the
        # gap-edge caps stack into the player's view the way they scroll in-game.
        for k in range(3):
            ph = 96
            py = col_y + 6 + k * (ph + 64)
            pil = _club_pillar_obstacle(ph, 4, flip=True, night=night)
            sheet.blit(pil, (col_x - 2, py - 2))
        _label(sheet, small, lab, col_x + 4, col_y + 4,
               (18, 28, 24) if not night else (255, 220, 200))

    _label(sheet, small,
           "FLAT only: detail via PATTERN DENSITY (face-dominant knob + dot-column + handprint), never 3D shading; charcoal dominant (red lean); pipeclay marks are the protected tell.",
           18, SH - 64, (40, 40, 46))
    _label(sheet, small,
           "ROUND 2: face de-targeted (big cross-eyes + bar-mouth beat the bands; brow is a PARTIAL arc, not concentric rings); foot = small charcoal bookend-knob (no tripod); caps read as heads.",
           18, SH - 44, (40, 40, 46))

    out_dir = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(out_dir, "round_2.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path)


if __name__ == "__main__":
    main()
