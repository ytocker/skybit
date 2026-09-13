"""Look-dev sheet for the Skybit BOSS batch-2 LEYAK-EPIC take — "TZITZIMITL".

An Aztec eclipse-omen cuted down: a pocket eclipse-star-skull blazing a too-big
GOLD CORONA, dropping a fall of doom-banners that form the pillar. Bodiless
star-head over a banner-fall trail — same Leyak DNA (no torso, no limbs; the
downward trail IS the pillar), but the silhouette KIND is a wide RADIAL
star-corona instead of the dangling-viscera ribbon.

House style this obeys (the elevated Leyak-EPIC grammar):
  - CHIBI proportions — one small bone skull-head wreathed in an oversized gold
    star-corona; NO torso, NO limbs. The banner-fall is the body.
  - FLAT saturated fills + hard 1-2px ink keylines (28,22,30). No within-shape
    gradients, no soft/feathered edges, no bevels.
  - Form via the TRIAD: dark-core ring -> flat fill -> top-left rim sheen.
  - EPIC dial: bigger render scale, SS=6, more geometry (8 alternating
    long/short rays), richer triad, stronger make_glow_surface corona glow.
  - The GOLD corona is the single brightest WARM focal mass; the body stays
    midnight-INDIGO (blue-leaning, NOT violet — clear of Necrarch). Scary-CUTE.
  - Silhouette POP via a 1px ink keyline grown from the alpha mask.
  - SUPERSAMPLE then smoothscale.

Accessibility tell: the wide radial star-corona silhouette + the high
value-contrast between the bright gold corona and the dark indigo body/banners
carry the read independent of hue.

Prop -> pillar mirror: the banner-FALL is the pillar. Stacked indigo doom-banner
panels with gold glyph trim = the repeatable PILLAR BODY (2-3 panels per
repeat); a creature-derived STAR-DISK medallion (~shaft+30%, not top-heavy) =
the detachable GAP-EDGE CAP radiating at the gap. On-axis + symmetric — clean
mirror.

Imports the real game colour/shape kit only; nothing under game/ is touched.
Headless + deterministic.

    SDL_VIDEODRIVER=dummy PYTHONPATH=/home/user/skybit python docs/skybit_devil/batch2/leyak_epic/tzitzimitl/render_tzitzimitl.py
"""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from game.draw import _shade_c, lerp_color, make_glow_surface
from game.config import PIPE_W


pygame.init()

# ── PINNED PALETTE (Leyak-EPIC / Tzitzimitl) — hex from the locked brief ──────
# Dominant family: midnight-INDIGO night-cloth body (blue-leaning, kept clear of
# the violet Necrarch) + a single BRIGHT GOLD corona as the sole warm focal. The
# bone face is a small high-value mark wreathed by the gold. Value split:
# bright-gold corona vs deep-indigo body = the hue-blind tell.
INDIGO      = (52, 56, 120)     # midnight night-cloth fill (blue-leaning)
INDIGO_DK   = (28, 30, 74)      # deep-indigo shade (dark-core / seams)
# Rim sheen pinned BLUE-WHITE (not lilac): blue channel leads but green tracks
# it closely so a violet drift can't pull the body toward Necrarch's lane.
INDIGO_SHEEN = (150, 172, 222)  # blue-white rim sheen (no lilac cast)
NIGHTCLOTH  = (48, 52, 116)     # banner cloth fill — ONE indigo value, no cream

GOLD        = (255, 214, 110)   # the corona — single brightest warm focal
GOLD_DK     = (198, 150, 52)    # gold shade (dark-core / ray roots)
GOLD_SHEEN  = (255, 244, 196)   # hot gold rim sheen / glyph highlight
GOLD_GLYPH  = (240, 196, 84)    # banner glyph stitching

BONE        = (236, 230, 214)   # skull bone fill
BONE_DK     = (176, 168, 152)   # bone shade (sockets / cracks)
BONE_SHEEN  = (255, 252, 242)   # bone top-left sheen

STAR_TEAL   = (120, 150, 220)   # cool star-spark inside the corona eye-stars

INK         = (28, 22, 30)      # the house keyline
SHEEN       = (255, 244, 196)


def _triad_circle(surf, cx, cy, r, col, *, sheen=True, sheen_d=30, ss=1):
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


# ── the gold star-corona (the dominant warm focal, the radial-KIND silhouette) ─

def _ray(surf, cx, cy, ang, inner_r, outer_r, half_w, col, ss):
    """One corona RAY as a flat triad SPEAR: a clean isosceles triangle from a
    flat base on the corona ring (inner_r) to a SHARP point at outer_r. No belly
    bulge — a crisp triangular tip so the starburst stays snappy even at 32px.
    Dark-core spear behind, gold fill in front, a thin top-left sheen sliver on
    the lit flank."""
    ca, sa = math.cos(ang), math.sin(ang)
    pa = ang + math.pi / 2                      # perpendicular for the width
    pca, psa = math.cos(pa), math.sin(pa)

    def _spear(o_r, hw, i_r):
        bx, by = cx + ca * i_r, cy + sa * i_r           # base centre on the ring
        tx, ty = cx + ca * o_r, cy + sa * o_r           # SHARP spear tip
        return [
            (bx + pca * hw, by + psa * hw),             # base, lit flank
            (tx, ty),                                   # crisp triangular point
            (bx - pca * hw, by - psa * hw),             # base, shadow flank
        ]

    pygame.draw.polygon(surf, GOLD_DK,
                        [(int(x), int(y)) for x, y in _spear(outer_r, half_w, inner_r)])
    pygame.draw.polygon(surf, col,
                        [(int(x), int(y)) for x, y in
                         _spear(outer_r - 1.4 * ss, half_w * 0.70, inner_r + 0.8 * ss)])
    # Top-left lit flank sheen: a thin sliver hugging the ray's upper edge.
    sl = _spear(outer_r - 2.4 * ss, half_w * 0.26, inner_r + 1.2 * ss)
    pygame.draw.polygon(surf, GOLD_SHEEN,
                        [(int(x + pca * half_w * 0.34), int(y + psa * half_w * 0.34))
                         for x, y in sl])


def _corona(surf, cx, cy, ring_r, ss, *, night=False):
    """The 8-ray gold star-corona wreathing the skull — the dominant warm mass.
    8 rays MAX, long/short alternating (the brief's clean readable starburst);
    a fat gold glow halo behind, and a gold ring band the rays spring from. The
    longest rays point up/down/sides so the radial silhouette reads instantly."""
    # Glow halo behind the whole corona — the eclipse blaze (stronger on night).
    # Tighter falloff so the ADD-blend stays a warm corona bloom and does NOT
    # flat-wash the indigo banner panel below it to a false cream value.
    gr = int(ring_r * (2.7 if night else 2.2))
    gl = make_glow_surface(gr, GOLD, alpha_center=140 if night else 92, falloff=3.4)
    surf.blit(gl, (int(cx - gr), int(cy - gr)), special_flags=pygame.BLEND_ADD)

    n = 8
    long_r = ring_r * 2.55
    short_r = ring_r * 1.58              # decisively ~62% of long → crisp 8-point
    for i in range(n):
        ang = -math.pi / 2 + (2 * math.pi) * (i / n)     # first ray straight UP
        long_ray = (i % 2 == 0)
        outer = long_r if long_ray else short_r
        hw = ring_r * (0.30 if long_ray else 0.22)
        _ray(surf, cx, cy, ang, ring_r * 0.92, outer, hw, GOLD, ss)

    # The gold ring band the rays grow out of — a triad torus framing the bone.
    pygame.draw.circle(surf, GOLD_DK, (int(cx), int(cy)), int(ring_r * 1.02))
    pygame.draw.circle(surf, GOLD, (int(cx), int(cy)), int(ring_r * 0.92))
    pygame.draw.circle(surf, _shade_c(GOLD, 28),
                       (int(cx - ring_r * 0.26), int(cy - ring_r * 0.28)),
                       int(ring_r * 0.30))
    # Punch the centre out to indigo so the bone skull seats inside the ring.
    pygame.draw.circle(surf, INDIGO_DK, (int(cx), int(cy)), int(ring_r * 0.74))

    # Tiny cool eye-stars studding the gold ring between rays — the night-sky
    # tell (Tzitzimitl = the star-demon). Kept small so gold stays dominant.
    for i in range(n):
        ang = -math.pi / 2 + (2 * math.pi) * ((i + 0.5) / n)
        sx = cx + math.cos(ang) * ring_r * 0.96
        sy = cy + math.sin(ang) * ring_r * 0.96
        pygame.draw.circle(surf, STAR_TEAL, (int(sx), int(sy)), max(1, int(ring_r * 0.07)))
        pygame.draw.circle(surf, GOLD_SHEEN, (int(sx), int(sy)), max(1, int(ring_r * 0.035)))


# ── the bone star-skull face (small high-value mark inside the corona) ────────

def _skull(surf, cx, cy, r, ss, *, night=False, compact=False, chip=False):
    """The small bone skull seated inside the gold ring: round-ish cranium,
    big dark eye-sockets with a cool star-spark, a tiny triangle nose, and a
    little stitched grin. Scary-CUTE — wide friendly sockets, not a rictus.

    `night` lifts the bone value so it stays a light pop on dark sky. `chip` is
    the true-32px build: the face collapses to the absolute-minimum legible mark
    — two OVERSIZED dark socket dots + one dark grin slot, ink keyline thickened,
    and the bone pushed brighter than the indigo disk so the FACE survives as a
    distinct value island instead of one light blob."""
    # Bone pushed brighter for night AND for the chip — at 32px the face must be
    # a clear value island ~15-20% above the indigo disk it sits on.
    lift_v = 12 if night else 0
    if chip:
        lift_v += 14
    bone = _shade_c(BONE, lift_v)
    bone_sheen = _shade_c(BONE_SHEEN, 6) if night else BONE_SHEEN

    # Cranium dome.
    _triad_circle(surf, cx, cy, r, bone, ss=ss)
    # A slightly wider lower jaw bulge so it's a skull, not a ball.
    jaw = pygame.Rect(0, 0, int(r * 1.62), int(r * 1.34))
    jaw.center = (int(cx), int(cy + r * 0.34))
    pygame.draw.ellipse(surf, _shade_c(bone, -46), jaw)
    inner = jaw.inflate(-int(r * 0.16), -int(r * 0.16))
    pygame.draw.ellipse(surf, bone, inner)
    _triad_circle(surf, cx, cy, r, bone, ss=ss)
    if not chip:
        pygame.draw.circle(surf, bone_sheen,
                           (int(cx - r * 0.30), int(cy - r * 0.40)),
                           max(2, int(r * 0.26)))

    # Subtle bone cracks (elevated detail) — thin hairline seams off the crown.
    if not compact and not chip:
        for (a0, ln) in ((-1.15, 0.55), (-0.35, 0.42)):
            x0 = cx + math.cos(a0) * r * 0.5
            y0 = cy + math.sin(a0) * r * 0.5 - r * 0.2
            x1 = x0 + math.cos(a0 + 0.5) * r * ln
            y1 = y0 + math.sin(a0 + 0.5) * r * ln
            pygame.draw.line(surf, BONE_DK, (int(x0), int(y0)), (int(x1), int(y1)),
                             max(1, int(1.2 * ss)))

    if chip:
        # MINIMUM legible face: two oversized solid-ink socket dots + a bold ink
        # grin slot. No star-spark / nose / teeth — they vanish at 32px and just
        # muddy the value. Outline thickened so the marks survive the downscale.
        eye_dx = r * 0.46
        eye_dy = -r * 0.06
        eye_r = r * 0.44
        for s in (-1, 1):
            ex = cx + s * eye_dx
            pygame.draw.circle(surf, INK, (int(ex), int(cy + eye_dy)), int(eye_r))
            # one tiny bright catch so the eye still twinkles, not dead black
            pygame.draw.circle(surf, GOLD_SHEEN,
                               (int(ex - eye_r * 0.18), int(cy + eye_dy - eye_r * 0.20)),
                               max(1, int(eye_r * 0.34)))
        # Bold grin slot: a single thick ink bar, gentle smile curve.
        grin_y = cy + r * 0.66
        grin_hw = r * 0.56
        grin_h = r * 0.30
        top, bot = [], []
        n = 10
        for i in range(n + 1):
            xr = -1.0 + 2.0 * (i / n)
            x = cx + xr * grin_hw
            lift = grin_h * 0.5 * (xr * xr)
            top.append((x, grin_y - grin_h * 0.5 + lift))
            bot.append((x, grin_y + grin_h * 0.5 + lift))
        pygame.draw.polygon(surf, INK, [(int(x), int(y)) for x, y in (top + bot[::-1])])
        return

    # — Eye sockets: big round dark hollows, the dominant face read. A cool
    #   star-spark sits in each so the eyes twinkle (the star-demon tell).
    eye_dx = r * 0.42
    eye_dy = -r * 0.04
    eye_r = r * 0.36
    for s in (-1, 1):
        ex, ey = cx + s * eye_dx, cy + eye_dy
        pygame.draw.circle(surf, _shade_c(bone, -54), (int(ex), int(ey)), int(eye_r * 1.08))
        pygame.draw.circle(surf, INK, (int(ex), int(ey)), int(eye_r))
        # 4-point cool star-spark inside the socket.
        for k in range(4):
            a = k * math.pi / 2 - math.pi / 4
            tx = ex + math.cos(a) * eye_r * 0.62
            ty = ey + math.sin(a) * eye_r * 0.62
            pygame.draw.line(surf, STAR_TEAL, (int(ex), int(ey)), (int(tx), int(ty)),
                             max(1, int(1.4 * ss)))
        pygame.draw.circle(surf, GOLD_SHEEN, (int(ex), int(ey)), max(1, int(eye_r * 0.30)))
        # cute top-left glint
        pygame.draw.circle(surf, (255, 255, 255),
                           (int(ex - eye_r * 0.22), int(ey - eye_r * 0.26)),
                           max(1, int(eye_r * 0.12)))

    # — Nose: tiny upturned dark triangle hole between + below the eyes.
    nose_y = cy + r * 0.30
    nose = [(cx, nose_y - r * 0.05), (cx - r * 0.085, nose_y + r * 0.10),
            (cx + r * 0.085, nose_y + r * 0.10)]
    pygame.draw.polygon(surf, INK, [(int(x), int(y)) for x, y in nose])

    # — Grin: a small stitched skull-grin — a dark band with little vertical
    #   stitch teeth. Friendly + tidy, not a wide menacing rictus.
    grin_y = cy + r * 0.60
    grin_hw = r * 0.54
    grin_h = r * 0.20
    top, bot = [], []
    n = 12
    for i in range(n + 1):
        xr = -1.0 + 2.0 * (i / n)
        x = cx + xr * grin_hw
        lift = grin_h * 0.4 * (xr * xr)
        top.append((x, grin_y - grin_h * 0.5 + lift))
        bot.append((x, grin_y + grin_h * 0.5 + lift))
    pygame.draw.polygon(surf, INK, [(int(x), int(y)) for x, y in (top + bot[::-1])])
    if not compact:
        teeth = 6
        for i in range(1, teeth):
            xr = -1.0 + 2.0 * (i / teeth)
            x = cx + xr * grin_hw
            lift = grin_h * 0.4 * (xr * xr)
            pygame.draw.line(surf, bone, (int(x), int(grin_y - grin_h * 0.5 + lift)),
                             (int(x), int(grin_y + grin_h * 0.5 + lift)), max(1, int(ss)))


# ── a single doom-banner panel (creature trail + the pillar body unit) ────────

def _banner_panel(surf, cx, top_y, w, h, ss, *, glyph=True, lit=True):
    """One hanging indigo doom-banner panel: a flat triad cloth rectangle necking
    to a notched (swallow-tail) bottom edge, with gold glyph stitching down the
    middle. This is the repeatable PILLAR BODY unit — 2-3 stack per repeat. Flat
    shapes, hard edges, no gradient.

    Every panel is ONE indigo cloth value (`lit` no longer flips the fill) so the
    fall reads as a single repeating cloth — only the dark-core seam, the flat
    fill and the top-left blue-white sheen separate panels. A strobing
    light/dark alternation would read as a second material as the pillar tiles."""
    hw = w * 0.5
    notch = h * 0.16
    # Cloth body: dark-core silhouette then flat fill, with a swallow-tail hem.
    def _cloth(scale, col, dx=0.0):
        pts = [
            (cx - hw * scale + dx, top_y),
            (cx + hw * scale + dx, top_y),
            (cx + hw * scale + dx, top_y + h - notch),
            (cx + hw * scale * 0.5 + dx, top_y + h),
            (cx + dx, top_y + h - notch * 0.7),
            (cx - hw * scale * 0.5 + dx, top_y + h),
            (cx - hw * scale + dx, top_y + h - notch),
        ]
        pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in pts])

    _cloth(1.00, INDIGO_DK)
    _cloth(0.88, NIGHTCLOTH)
    # Top-left rim sheen stripe down the lit edge of the cloth.
    pygame.draw.line(surf, INDIGO_SHEEN,
                     (int(cx - hw * 0.80), int(top_y + h * 0.06)),
                     (int(cx - hw * 0.80), int(top_y + h * 0.78)), max(1, int(1.6 * ss)))
    # A gold top-rail trim where the banner hangs from the cord.
    pygame.draw.rect(surf, GOLD_DK,
                     (int(cx - hw), int(top_y - 1.2 * ss), int(w), int(2.6 * ss)))
    pygame.draw.rect(surf, GOLD,
                     (int(cx - hw + ss), int(top_y - 0.6 * ss), int(w - 2 * ss), int(1.6 * ss)))
    # Gold glyph stitching down the centre — a stacked diamond+bar eclipse glyph.
    if glyph:
        gy = top_y + h * 0.30
        for k in range(2):
            yy = gy + k * h * 0.34
            d = w * 0.16
            pygame.draw.polygon(surf, GOLD_GLYPH, [
                (int(cx), int(yy - d)), (int(cx + d), int(yy)),
                (int(cx), int(yy + d)), (int(cx - d), int(yy))])
            pygame.draw.line(surf, GOLD_SHEEN, (int(cx - d * 0.5), int(yy)),
                             (int(cx + d * 0.5), int(yy)), max(1, int(ss)))


# ── the whole creature: star-skull + banner-fall, on one surface ──────────────

def build_tzitzimitl(scale=1.0, ss=6, *, night=False, compact=False, chip=False):
    """The full creature on its own transparent surface: the bone star-skull
    wreathed in the gold corona up top, a fall of indigo doom-banners streaming
    straight down beneath it. Returns an outlined surface.

    `compact` is the GAMEPLAY / 32px-icon variant: the head+corona is grown to
    dominate the vertical budget and the banner-fall is cut to ~1 short panel,
    so the icon reads 'star-skull with a gold burst' — never a thin banner
    squiggle with a speck."""
    ring_r = int(30 * scale) * ss
    skull_r = int(ring_r * 0.62)
    corona_reach = ring_r * 2.55           # longest ray reach for padding

    banner_w = int(ring_r * 0.92)
    panel_h = int(ring_r * 0.66)
    n_panels = 2 if compact else 5
    band_gap = int(panel_h * 0.10)

    side_pad = int(corona_reach - ring_r) + 6 * ss
    top_pad = int(corona_reach - ring_r) + 6 * ss
    bot_pad = int(14 * scale) * ss

    head_cx = side_pad + ring_r
    head_cy = top_pad + ring_r

    # The banner-fall hangs from BELOW the corona's downward long ray so the
    # ray reads as the corona's bottom point and never paints over (cream-washes)
    # the top banner cloth. The cord bridges the short gap from ring to fall.
    ray_reach_down = ring_r * (2.55 if compact else 2.55)
    fall_top = head_cy + ray_reach_down + ring_r * 0.10
    fall_h = n_panels * (panel_h + band_gap)
    feet_y = fall_top + fall_h

    W = int(head_cx * 2)
    H = int(feet_y + bot_pad)
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    cx = W // 2

    # A thin cord the banners hang from (springs from inside the ring base).
    pygame.draw.line(surf, GOLD_DK, (int(cx), int(head_cy + ring_r * 0.5)),
                     (int(cx), int(feet_y)), max(1, int(1.6 * ss)))

    # The banner-fall trail (the body / the pillar source). Panels narrow as the
    # fall descends so it reads as a tapering streamer, not a stiff stack.
    y = fall_top
    for i in range(n_panels):
        t = i / max(1, n_panels - 1)
        sc = 1.0 - 0.36 * t
        _banner_panel(surf, cx, y, banner_w * sc, panel_h * sc, ss,
                      glyph=(panel_h * sc > 14), lit=(i % 2 == 0))
        y += panel_h * sc + band_gap

    # The corona + skull over the banner roots. Corona drawn first (behind), then
    # the bone skull seated inside the ring. On the chip the skull is grown so
    # the minimal face survives the 32px downscale.
    _corona(surf, cx, head_cy, ring_r, ss, night=night)
    sr = skull_r * 1.14 if chip else skull_r
    _skull(surf, cx, head_cy, sr, ss, night=night, compact=compact, chip=chip)

    out_w = int(surf.get_width() / ss)
    out_h = int(surf.get_height() / ss)
    smallv = pygame.transform.smoothscale(surf, (out_w, out_h))
    return _add_outline(smallv)


# ── pillar pair (prop -> pillar mirror proof) ────────────────────────────────

OVERHANG = 12


def _banner_column(surf, cx, top_y, bot_y, ss):
    """The repeatable PILLAR BODY: the banner-fall as a straight tiling shaft —
    stacked indigo doom-banner panels (uniform, on-axis, no taper) with gold
    glyph trim, hung off a central cord. 2-3 panels per visible repeat so the
    cadence tiles top<->bottom for the pillar."""
    length = bot_y - top_y
    bw = (PIPE_W) * ss * 0.92               # banner spans most of the post width
    panel_h = bw * 0.92
    band_gap = panel_h * 0.10
    unit = panel_h + band_gap
    n = max(2, int(round(length / unit)))
    unit = length / n
    panel_h = unit - band_gap
    # Central cord behind the banners.
    pygame.draw.line(surf, GOLD_DK, (int(cx), int(top_y)), (int(cx), int(bot_y)),
                     max(1, int(1.8 * ss)))
    y = top_y
    for i in range(n):
        _banner_panel(surf, cx, y, bw, panel_h, ss, glyph=True, lit=(i % 2 == 0))
        y += unit


def _star_disk_cap(surf, cx, cap_base_y, disk_r, ss, *, point_up, night=False):
    """The detachable GAP-EDGE CAP: a creature-derived STAR-DISK medallion — a
    gold-ringed disk with a bone star-skull motif + short corona spikes, radiating
    gold INTO the gap. Sized ~shaft+30% (modest, NOT top-heavy). `point_up` faces
    the medallion's spikes toward the gap."""
    d = -1 if point_up else 1
    cy = cap_base_y + d * (disk_r * 0.92)

    # Gold glow biased INTO the gap (offset toward the gap edge, tighter reach +
    # lower alpha) so the ADD-blend lights the gap, NOT the indigo banner behind
    # it. A fat glow over the shaft washed the adjacent cloth panel to cream.
    gr = int(disk_r * (1.5 if night else 1.2))
    gl = make_glow_surface(gr, GOLD, alpha_center=150 if night else 96, falloff=2.8)
    glow_cy = cy + d * disk_r * 0.55           # push the bloom toward the gap
    surf.blit(gl, (int(cx - gr), int(glow_cy - gr)), special_flags=pygame.BLEND_ADD)

    # Short corona spikes around the disk (8, alternating). Kept SHORT so the
    # disk+rays envelope holds to ~shaft+30% and the cap never reads top-heavy.
    n = 8
    for i in range(n):
        ang = (2 * math.pi) * (i / n) - math.pi / 2
        long_ray = (i % 2 == 0)
        outer = disk_r * (1.34 if long_ray else 1.16)
        hw = disk_r * (0.17 if long_ray else 0.13)
        _ray(surf, cx, cy, ang, disk_r * 0.94, outer, hw, GOLD, ss)

    # Gold ring band.
    pygame.draw.circle(surf, GOLD_DK, (int(cx), int(cy)), int(disk_r * 1.02))
    pygame.draw.circle(surf, GOLD, (int(cx), int(cy)), int(disk_r * 0.92))
    pygame.draw.circle(surf, _shade_c(GOLD, 28),
                       (int(cx - disk_r * 0.26), int(cy - disk_r * 0.28)),
                       int(disk_r * 0.28))
    pygame.draw.circle(surf, INDIGO_DK, (int(cx), int(cy)), int(disk_r * 0.70))

    # A compact bone star-skull motif in the disk centre (the creature tie-back).
    _skull(surf, cx, cy, disk_r * 0.52, ss, night=night, compact=True)


def _banner_pillar_obstacle(height, ss, *, flip, night=False):
    """One banner-fall PILLAR obstacle: stacked doom-banners fill the post and a
    star-disk medallion CAP sits at the GAP-facing edge, radiating INTO the gap.
    `flip=True` is the TOP pillar — cap at the bottom (gap) edge; `flip=False`
    is the BOTTOM pillar — cap at the TOP (gap) edge. Both mirror the same banner
    body into a clean vertical pillar capped at the gap."""
    bw = (PIPE_W + 2 * OVERHANG) * ss
    bh = max(1, int(height)) * ss
    surf = pygame.Surface((bw, bh), pygame.SRCALPHA)
    cx = bw // 2
    # Size the disk so the disk+RAYS envelope (rays reach disk_r*1.34) holds to
    # ~shaft+30%, not the disk alone — keeps the cap from creeping top-heavy.
    cap_reach = (PIPE_W * 0.5) * 1.30 * ss       # half the shaft+30% envelope
    disk_r = int(cap_reach / 1.34)
    cap_band = int(cap_reach * 2.4)
    if flip:
        _banner_column(surf, cx, 0, bh - cap_band, ss)
        _star_disk_cap(surf, cx, bh - cap_band, disk_r, ss, point_up=False, night=night)
    else:
        _banner_column(surf, cx, cap_band, bh, ss)
        _star_disk_cap(surf, cx, cap_band, disk_r, ss, point_up=True, night=night)
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
        rng = _r.Random(7)
        for _ in range(30):
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

    SW, SH = 1000, 760
    sheet = pygame.Surface((SW, SH))
    sheet.fill((70, 72, 78))          # neutral grey bg
    _label(sheet, font,
            "TZITZIMITL  —  LEYAK-EPIC  —  eclipse star-skull + gold corona + indigo doom-banners  —  round 2", 16, 12)
    _label(sheet, small,
            "epic dial: SS=6, 8 alternating long/short corona rays (dominant warm focal), midnight-INDIGO body (blue-leaning), bone star-skull. banner-fall IS the pillar.",
            16, 32, (210, 214, 230))

    # — Cell A: BIG hero sprite on a dusk/eclipse sky.
    panel = pygame.Rect(14, 56, 320, 612)
    bgA = _sky(panel.w, panel.h, (24, 22, 56), (70, 60, 110), (160, 130, 150))
    sheet.blit(bgA, panel.topleft)
    pygame.draw.rect(sheet, (120, 120, 132), panel, 2, border_radius=8)
    hero = build_tzitzimitl(scale=1.7, ss=6)
    sheet.blit(hero, (panel.centerx - hero.get_width() // 2, panel.y + 44))
    _label(sheet, font, "(a) HERO  big scale  (SS=6)", panel.x + 8, panel.y + 8)
    _label(sheet, small, "gold corona = brightest focal; bone skull seated in the ring",
           panel.x + 8, panel.y + 26, (255, 230, 180))

    # — Cell B: banner-fall as a tileable PILLAR pair at TRUE obstacle scale on
    #   NIGHT, plus a 2x zoom on the CAP band proving the star-disk medallion.
    panelB = pygame.Rect(346, 56, 320, 612)
    bg = _sky(panelB.w, panelB.h, (8, 10, 34), (18, 20, 60), (40, 38, 86), stars=True)
    sheet.blit(bg, panelB.topleft)
    pygame.draw.rect(sheet, (120, 120, 132), panelB, 2, border_radius=8)
    _label(sheet, font, "(b) PROP -> PILLAR  @ TRUE scale  (NIGHT)", panelB.x + 8, panelB.y + 8)

    pw = PIPE_W + 2 * OVERHANG
    slice_h = 500
    slice_x = panelB.x + 22
    slice_y = panelB.y + 42
    gap_top = 162
    gap_h = 132
    top_h = gap_top
    bot_h = slice_h - gap_top - gap_h
    top_pillar = _banner_pillar_obstacle(top_h, 3, flip=True, night=True)
    bot_pillar = _banner_pillar_obstacle(bot_h, 3, flip=False, night=True)
    sheet.blit(top_pillar, (slice_x - 2, slice_y - 2))
    sheet.blit(bot_pillar, (slice_x - 2, slice_y + gap_top + gap_h - 2))
    pygame.draw.rect(sheet, (200, 200, 210), (slice_x - 4, slice_y - 4, pw + 8, slice_h + 8), 1)
    _label(sheet, small, "1x native (82px): doom-banner", slice_x - 2, slice_y + slice_h + 6, (215, 215, 225))
    _label(sheet, small, "panels tile; star-disk caps gap", slice_x - 2, slice_y + slice_h + 22, (255, 225, 170))

    # 2x zoom re-aimed at the CAP band. The zoom surface is padded WIDER than the
    # pillar (zpad each side) and the pillar centred inside it, so no corona ray /
    # outline can clip at the frame edge — the cap audit must show all 8 rays.
    cap_band = 64
    zpad = 6
    zw, zh = pw + 2 * zpad, 180
    px = zpad - 2                           # pillar surface is outlined (pad=2)
    zoom_src = pygame.Surface((zw, zh), pygame.SRCALPHA)
    top_anchor = 14
    zoom_src.blit(top_pillar, (px, -(top_h - cap_band - top_anchor) - 2))
    zoom_gap = zh - 2 * cap_band - 2 * top_anchor
    bot_anchor = top_anchor + cap_band + zoom_gap
    zoom_src.blit(bot_pillar, (px, bot_anchor - 2))
    zoom = pygame.transform.scale(zoom_src, (zw * 2, zh * 2))
    zx = panelB.right - zw * 2 - 14
    zy = panelB.y + 92
    zbg = _sky(zw * 2, zh * 2, (8, 10, 34), (16, 16, 50), (28, 26, 66))
    sheet.blit(zbg, (zx, zy))
    pygame.draw.rect(sheet, (200, 200, 210), (zx - 1, zy - 1, zw * 2 + 2, zh * 2 + 2), 1)
    sheet.blit(zoom, (zx, zy))
    _label(sheet, small, "2x zoom of the CAP band:", zx - 2, zy - 16, (255, 255, 255))
    _label(sheet, small, "star-disk medallion (~shaft+30%)", zx - 2, zy + zh * 2 + 6, (255, 225, 170))
    _label(sheet, small, "radiates gold INTO the gap", zx - 2, zy + zh * 2 + 22, (255, 225, 170))

    # — Cell C: TRUE 32px gameplay chip on day + night, plus a 4x audit.
    panelC = pygame.Rect(678, 56, 308, 612)
    pygame.draw.rect(sheet, (54, 56, 62), panelC, border_radius=8)
    pygame.draw.rect(sheet, (120, 120, 132), panelC, 2, border_radius=8)
    _label(sheet, font, "(c) TRUE 32px gameplay chip", panelC.x + 8, panelC.y + 8)
    _label(sheet, small, "head-dominant compact; day + night sky", panelC.x + 8, panelC.y + 26,
           (255, 230, 180))

    icon_src = build_tzitzimitl(scale=1.0, ss=6, compact=True, chip=True)
    icon_src_n = build_tzitzimitl(scale=1.0, ss=6, night=True, compact=True, chip=True)
    sc = 32 / icon_src.get_height()
    icon32 = pygame.transform.smoothscale(
        icon_src, (max(1, int(icon_src.get_width() * sc)), 32))
    icon32_n = pygame.transform.smoothscale(
        icon_src_n, (max(1, int(icon_src_n.get_width() * sc)), 32))

    # True-32 chips on day + night.
    day = _sky(132, 150, (40, 110, 200), (90, 170, 230), (170, 220, 245))
    night = _sky(132, 150, (8, 10, 34), (18, 20, 60), (40, 38, 86), stars=True)
    dy = panelC.y + 50
    sheet.blit(day, (panelC.x + 16, dy))
    sheet.blit(night, (panelC.x + 160, dy))
    sheet.blit(icon32, (panelC.x + 16 + 66 - icon32.get_width() // 2, dy + 75 - 16))
    sheet.blit(icon32_n, (panelC.x + 160 + 66 - icon32_n.get_width() // 2, dy + 75 - 16))
    _label(sheet, small, "DAY 32px", panelC.x + 16 + 4, dy + 4, (20, 30, 26))
    _label(sheet, small, "NIGHT 32px", panelC.x + 160 + 4, dy + 4, (255, 225, 170))

    # 4x nearest-neighbour blow-up so the corona + skull read at 32 is auditable.
    gy = dy + 168
    _label(sheet, small, "4x blow-up (audit corona + skull read at 32px):",
           panelC.x + 16, gy - 2, (235, 220, 200))
    blow = pygame.transform.scale(icon32, (icon32.get_width() * 4, icon32.get_height() * 4))
    blow_n = pygame.transform.scale(icon32_n, (icon32_n.get_width() * 4, icon32_n.get_height() * 4))
    chip = pygame.Rect(panelC.x + 16, gy + 14, blow.get_width() + 8, blow.get_height() + 8)
    pygame.draw.rect(sheet, (40, 110, 200), chip, border_radius=4)
    sheet.blit(blow, (chip.x + 4, chip.y + 4))
    chipn = pygame.Rect(panelC.x + 160, gy + 14, blow_n.get_width() + 8, blow_n.get_height() + 8)
    pygame.draw.rect(sheet, (40, 38, 86), chipn, border_radius=4)
    sheet.blit(blow_n, (chipn.x + 4, chipn.y + 4))

    # Grayscale value check.
    gy2 = gy + 14 + blow.get_height() + 26
    _label(sheet, small, "grayscale value (corona/body split):", panelC.x + 16, gy2 - 2, (235, 235, 235))
    gray = _to_gray(blow)
    chipg = pygame.Rect(panelC.x + 16, gy2 + 14, blow.get_width() + 8, blow.get_height() + 8)
    pygame.draw.rect(sheet, (120, 124, 120), chipg, border_radius=4)
    sheet.blit(gray, (chipg.x + 4, chipg.y + 4))

    # — Footer captions.
    _label(sheet, small,
           "STAY: flat saturated fills, 1-2px ink keyline (28,22,30), dark-core->fill->top-left rim-sheen triad, 1px grown outline, chibi, scary-CUTE, procedural-only (NO gradients/PNGs).",
           16, SH - 64, (210, 214, 230))
    _label(sheet, small,
           "prop->pillar: indigo doom-banner panels (gold glyph trim) tile as the shaft 2-3/repeat; a star-disk medallion (~shaft+30%, not top-heavy) caps + lights the gap. On-axis, clean mirror.",
           16, SH - 44, (210, 214, 230))

    out_dir = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(out_dir, "round_2.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path)


if __name__ == "__main__":
    main()
