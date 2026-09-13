"""Round-1 cloud-renderer explorations for the shan-shui sky.

The shipped `game.draw.draw_cloud` paints a stack of white circles with
fixed RGB and no biome coupling — that reads as Eurocentric cumulus puffs
and breaks the East-Asian ink-wash contract that V14 backdrop + pagoda
pillars already enforce. Each variant here brings a distinct calligraphic
silhouette family (wash / scroll / bank / streak / curl) and tints itself
from the live biome palette so dawn warm, dusk cool, and night ghostly
read consistently with the rest of the scene.

Drop-in: every variant matches `draw_cloud_<name>(surf, x, y, palette,
scale=1.0)`. The harness adapts the existing `draw_cloud` signature
(x, y, scale, variant) by injecting `palette` from the phase being
rendered, so live-game integration only swaps the call wrapper, never
the call sites.
"""
from __future__ import annotations

import math
import pygame


# ── shared palette / colour helpers ──────────────────────────────────────────
#
# All variants ask the biome for a sky-aware cloud tint instead of the
# hard-coded white the legacy renderer uses. The cloud body lerps between
# horizon (warm at sunset, cool at dawn) and sky_bot (cooler base) so the
# cloud sits ON the sky band it's drawn over rather than punching a hole
# through it. Night phases lean toward sky_bot + a touch of horizon so the
# cloud reads as a luminous-pale shape, never a daylight blob.


def _cloud_body_color(palette: dict) -> tuple[int, int, int]:
    horizon = palette['horizon']
    sky_bot = palette['sky_bot']
    sky_top = palette['sky_top']
    # At night the horizon channel is still warm-ish (residual dusk), so a
    # 70/30 horizon-led mix paints clouds as pale-WARM blobs after dark —
    # wrong: night cumulus should read pale-cool, lit by moon or scattered
    # sky. When sky_top luminance drops below 90 we re-weight 50/50 against
    # sky_top so the body cools off; daytime keeps the warmer horizon-led
    # mix that ties clouds to the dawn/dusk rim light.
    top_lum = (sky_top[0] * 299 + sky_top[1] * 587 + sky_top[2] * 114) / 1000
    if top_lum < 90:
        r = int(horizon[0] * 0.50 + sky_top[0] * 0.50)
        g = int(horizon[1] * 0.50 + sky_top[1] * 0.50)
        b = int(horizon[2] * 0.50 + sky_top[2] * 0.50)
    else:
        r = int(horizon[0] * 0.70 + sky_bot[0] * 0.30)
        g = int(horizon[1] * 0.70 + sky_bot[1] * 0.30)
        b = int(horizon[2] * 0.70 + sky_bot[2] * 0.30)
    r, g, b = min(255, r + 25), min(255, g + 25), min(255, b + 25)
    # Bright-blue DAY (sky_top luminance 150–200) still washes the body
    # out against the cyan dome — Ruyi-round-2 AD measured ~25% value
    # contrast and called it. Pull the mixed body 30% toward warm paper-
    # white only on that luminance band so night-cool (lum < 90) and
    # sunset-warm (lum 90–150) branches are preserved verbatim.
    if 150 < top_lum < 200:
        r = int(r * 0.70 + 252 * 0.30)
        g = int(g * 0.70 + 252 * 0.30)
        b = int(b * 0.70 + 245 * 0.30)
    return (r, g, b)


def _ink_shadow_color(palette: dict) -> tuple[int, int, int]:
    # The "wet ink" edge of a calligraphic wash — pulls from the deepest
    # palette key around (mtn_far → sky_top) so it stays in-key.
    far = palette['mtn_far']
    top = palette['sky_top']
    return (
        max(0, int(far[0] * 0.55 + top[0] * 0.45) - 10),
        max(0, int(far[1] * 0.55 + top[1] * 0.45) - 10),
        max(0, int(far[2] * 0.55 + top[2] * 0.45) - 10),
    )


def _lit_edge_color(palette: dict) -> tuple[int, int, int]:
    # The single bright sliver on the cloud's sunlit side — picked from
    # horizon and pushed brighter so it pops even in dusk/night phases.
    h = palette['horizon']
    return (
        min(255, h[0] + 30),
        min(255, h[1] + 30),
        min(255, h[2] + 30),
    )


def _lerp(a, b, t):
    return a + (b - a) * t


def _lerp_color(a, b, t):
    return (
        int(_lerp(a[0], b[0], t)),
        int(_lerp(a[1], b[1], t)),
        int(_lerp(a[2], b[2], t)),
    )


def _alpha_surf(w, h) -> pygame.Surface:
    return pygame.Surface((max(2, int(w)), max(2, int(h))), pygame.SRCALPHA)


# ─────────────────────────────────────────────────────────────────────────────
# Variant 1 — Sumi-e Ink-Wash Wisp
# Research:
#   https://www.asianbrushpainter.com/blogs/kb/the-use-of-ink
#   https://www.shimizuart.org/post/sumi-e-the-art-of-ink-wash-painting
#
# Single calligraphic stroke: loaded-brush "head" with wet pooled ink,
# tapering into a dry-brush "flying-white" (kasure) tail of broken ink
# specks. Direction is near-horizontal with a subtle downward swoop so
# the body weight reads on the leading edge, exactly how a sumi-e cloud
# is laid down in one motion.
# ─────────────────────────────────────────────────────────────────────────────

def draw_cloud_sumie(surf, x, y, palette, scale=1.0):
    """Calligraphic single-stroke wisp — wet head, flying-white tail."""
    body = _cloud_body_color(palette)
    edge = _ink_shadow_color(palette)
    lit = _lit_edge_color(palette)

    # Stroke length and head radius scale together. Length pulled in
    # from 80 → 60 so the wisp reads as one confident calligraphic
    # stroke instead of a comet trail across the sky.
    length = int(60 * scale)
    head_r = int(14 * scale)
    pad = head_r + 6
    surf_w = length + pad * 2
    surf_h = head_r * 3 + 8
    s = _alpha_surf(surf_w, surf_h)

    cy = surf_h // 2

    # Wet head — overlapping discs with varied radii. The 3rd disc is
    # deliberately tighter and offset UP, breaking the previous near-
    # identical "stamped" lozenge into a calligraphic asymmetric head.
    for i, (dx, ry, rad, a) in enumerate((
            (0, 0, head_r, 235),
            (head_r // 2, -2, head_r - 2, 220),
            (head_r, -3, head_r - 7, 210),
            (-2, 4, head_r - 5, 200),
    )):
        pygame.draw.ellipse(
            s, (*body, a),
            pygame.Rect(pad + dx - rad, cy + ry - rad,
                        rad * 2, int(rad * 1.6)))

    # Tapered body — line of ellipses shrinking toward the tail. Amplitude
    # bumped + phase shifted so head sits higher than tail; a flat spine
    # was visually competing with the horizontal mist-veil row.
    n_body = 9
    for i in range(n_body):
        t = i / (n_body - 1)
        bx = pad + head_r + int(t * (length - head_r))
        # Swoop amplitude halved (4 → 2) so the spine reads as a single
        # confident stroke rather than a comet arc; the head-vs-tail
        # height delta still breaks the flat horizontal silhouette.
        by = cy + int(math.sin(t * math.pi * 0.6 - 0.1) * 2 * scale)
        rad = max(2, int((head_r - 3) * (1 - t * 0.85)))
        a = int(_lerp(210, 120, t))
        pygame.draw.ellipse(
            s, (*body, a),
            pygame.Rect(bx - rad, by - rad // 2,
                        rad * 2, max(3, int(rad * 1.1))))

    # Flying-white kasure tail. Base alpha lifted so 1-px specks survive
    # against dark NIGHT sky_top, and speck radius scaled up: at 1× the
    # tail used to disappear past the body's last ellipse.
    rng_seed = (int(x) * 73856093) ^ (int(y) * 19349663)
    for k in range(14):
        t = 0.55 + (k / 14) * 0.55
        if t > 1.0:
            break
        tx = pad + head_r + int(t * (length - head_r))
        jitter = ((rng_seed >> (k % 16)) & 0x7) - 3
        # Tail amplitude matches the body's tamed swoop (4 → 2) so the
        # specks track the spine instead of drifting above/below it.
        ty = cy + int(math.sin(t * math.pi * 0.7 - 0.1) * 2 * scale) + jitter
        rad = max(1, int(3.5 * scale * (1 - t * 0.6)))
        a = int(_lerp(190, 30, t))
        if a <= 0:
            continue
        pygame.draw.circle(s, (*body, a), (tx, ty), rad)

    # Ink-shadow underline. Pulled from `mtn_far` direct (not pre-mixed
    # toward sky_top) so warm-on-warm sunset / golden still shows the
    # pooled edge; the mixed colour collapsed into the horizon band.
    # Width pulled in (head_r*3 → head_r*2) and alpha softened
    # (110 → 70) so the underline supports the head rather than
    # outlining it like a label.
    pygame.draw.ellipse(
        s, (*palette['mtn_far'], 70),
        pygame.Rect(pad - 2, cy + head_r // 2 - 1,
                    head_r * 2, max(3, int(head_r * 0.6))))

    # Sunlit highlight kiss on the top-left of the head.
    pygame.draw.ellipse(
        s, (*lit, 140),
        pygame.Rect(pad - 4, cy - head_r + 2,
                    head_r + 4, max(3, head_r // 2)))

    surf.blit(s, (int(x - pad), int(y - cy)))


# ─────────────────────────────────────────────────────────────────────────────
# Variant 2 — Ruyi Auspicious Scroll (祥云)
# Research:
#   https://en.wikipedia.org/wiki/Xiangyun_(Auspicious_clouds)
#   https://www.chinese-showcase.com/blogs/chinese-symbols/auspicious-clouds-pattern-xiangyun-meaning-symbolism-spiritual-significance
#
# Vector-clean 4-lobe scroll silhouette descended from the Beijing 2008
# torch "Cloud of Promise" and the Tang/Ming porcelain motif. Distinct
# coiled spirals on each lobe + a wide base ribbon. Outlined in a soft
# darker keyline so it reads as a heraldic / decorative shape, not a
# puff of vapour.
# ─────────────────────────────────────────────────────────────────────────────

def draw_cloud_ruyi(surf, x, y, palette, scale=1.0):
    """Tang/Ming auspicious-cloud scroll — 3 lobes + inner-arc swoops."""
    body = _cloud_body_color(palette)
    edge = _ink_shadow_color(palette)
    lit = _lit_edge_color(palette)

    # Dropped from 96 px / 4 lobes to 72 px / 3 lobes: the prior fan of
    # 4 lobes on a strict diagonal read as a vector decal / heraldic
    # crest, which competed with the KFC pillar logo. 3-lobe Tang
    # arrangement with broken alignment lands as a sky motif.
    w = int(72 * scale)
    h = int(46 * scale)
    pad = 6
    s = _alpha_surf(w + pad * 2, h + pad * 2)
    cx = pad + w // 2
    cy = pad + h // 2

    # Seeded RNG so the y jitter is deterministic per spawn position
    # (cloud doesn't reshuffle each frame).
    rng_seed = (int(x) * 0x9E3779B1) ^ (int(y) * 0x7F4A7C15)

    def _jit(idx, amp):
        # Cheap LCG step keyed off seed+idx, returns [-amp, +amp].
        v = ((rng_seed + idx * 2654435761) & 0xFFFF) / 0xFFFF
        return int((v - 0.5) * 2 * amp)

    # 3-lobe layout — break the strict diagonal by jittering y per lobe
    # ±0.06h. Dominant lobe still on the leading (right) side.
    base_lobes = (
        (int(w * 0.25), cy - int(h * 0.05), int(h * 0.36)),
        (int(w * 0.55), cy - int(h * 0.18), int(h * 0.42)),
        (int(w * 0.82), cy - int(h * 0.08), int(h * 0.38)),
    )
    lobes = tuple(
        (lx, ly + _jit(i, int(h * 0.06)), lr)
        for i, (lx, ly, lr) in enumerate(base_lobes)
    )

    # 1. Soft ink-shadow halo offset down-right. Alpha pulled 70 → 45
    # and offset +2,+3 → +1,+2 so the halo reads as drop-shadow whisper
    # instead of bordering the lobes like a stencil.
    for (lx, ly, lr) in lobes:
        pygame.draw.circle(
            s, (*edge, 45), (lx + pad + 1, ly + 2), lr + 1)
    # Base ribbon — halved vertical extent (was h*0.28, now ~h*0.18) so
    # the ribbon supports the lobes rather than overwhelming them.
    base_pts = [
        (pad + int(w * 0.10), cy + int(h * 0.05)),
        (pad + int(w * 0.30), cy + int(h * 0.12)),
        (pad + int(w * 0.55), cy + int(h * 0.13)),
        (pad + int(w * 0.78), cy + int(h * 0.09)),
        (pad + int(w * 0.90), cy + int(h * 0.04)),
        (pad + int(w * 0.78), cy + int(h * 0.14)),
        (pad + int(w * 0.55), cy + int(h * 0.18)),
        (pad + int(w * 0.30), cy + int(h * 0.17)),
        (pad + int(w * 0.12), cy + int(h * 0.12)),
    ]
    pygame.draw.polygon(s, (*edge, 60),
                        [(px + 2, py + 3) for px, py in base_pts])
    pygame.draw.polygon(s, (*body, 240), base_pts)

    # 2. Lobe fills.
    for (lx, ly, lr) in lobes:
        pygame.draw.circle(s, (*body, 245), (lx + pad, ly), lr)

    # 3. Arc-segment keylines instead of full circumference rings — the
    # full ring read as a logo/badge; a 200°–340° arc on the lower-left
    # quadrant only reads as a calligraphic ruyi curl on each lobe.
    for (lx, ly, lr) in lobes:
        cx_l = lx + pad
        pygame.draw.arc(
            s, (*edge, 160),
            pygame.Rect(cx_l - lr, ly - lr, lr * 2, lr * 2),
            math.radians(200), math.radians(340), 2)
        # Inner swoop — the actual ruyi flourish. No centre pinpoint:
        # at 1× the dot read as a pixel defect.
        inner = max(3, lr - 5)
        rect = pygame.Rect(cx_l - inner, ly - inner, inner * 2, inner * 2)
        pygame.draw.arc(s, (*edge, 180), rect,
                        math.radians(20), math.radians(200), 2)

    # 4. Base-ribbon keyline.
    pygame.draw.lines(s, (*edge, 170), False, base_pts[:5], 2)
    pygame.draw.lines(s, (*edge, 130), False, base_pts[4:], 1)

    # 5. Sunlit crescent — restricted to the dominant (middle) lobe only.
    # Three crescents lit the silhouette like a vector decal; one
    # crescent on the apex lobe reads as a single directional sun-kiss.
    lx, ly, lr = lobes[1]
    cx_l = lx + pad
    pygame.draw.arc(s, (*lit, 200),
                    pygame.Rect(cx_l - lr + 2, ly - lr + 2,
                                lr * 2 - 4, lr * 2 - 4),
                    math.radians(110), math.radians(220), 2)

    surf.blit(s, (int(x - cx), int(y - cy)))


# ─────────────────────────────────────────────────────────────────────────────
# Variant 3 — Yúnhǎi Cloud-Sea Bank (雲海)
# Research:
#   https://learnjapanese123.com/unkai-japans-top-sea-of-clouds-spots/
#   https://www.1000museums.com/shop/art/hiroshi-yoshida-sea-of-clouds-unkai-ho-o-san/
#
# Horizontal banded cloud-sea like Hiroshi Yoshida's "Unkai" or the
# distant cloud bands in Tang-era shan-shui. Long elliptical strata
# stacked in 3 tiers, gradient fade top-to-bottom so the bottom edge
# dissolves into the sky. Reads as a far-off ridge of cloud, not a
# discrete puff — anchors the horizon line in shan-shui style.
# ─────────────────────────────────────────────────────────────────────────────

def draw_cloud_yunhai(surf, x, y, palette, scale=1.0):
    """Horizontal cloud-sea bank — stacked strata reading as distance."""
    body = _cloud_body_color(palette)
    edge = _ink_shadow_color(palette)
    lit = _lit_edge_color(palette)

    w = int(110 * scale)
    h = int(42 * scale)
    pad = 6
    s = _alpha_surf(w + pad * 2, h + pad * 2)

    # 3 stacked strata, each a flattened ellipse with a small horizontal
    # offset per band — purely vertical alignment read as flat-stencil.
    # Top tilts right, bottom tilts left so the bank reads as parallax-
    # offset strata at different "distances".
    # At NIGHT the bank covered the star field too aggressively; soften
    # the alphas (210/235/175 → 180/210/150) so stars peek through the
    # bank just like in Yoshida's "Unkai" nightside woodblock.
    sky_top_strata = palette['sky_top']
    top_lum_strata = (
        sky_top_strata[0] * 299
        + sky_top_strata[1] * 587
        + sky_top_strata[2] * 114
    ) / 1000
    if top_lum_strata < 90:
        strata = (
            (0.22, 0.78, 5, 180, +0.05),
            (0.50, 1.00, 7, 210,  0.00),
            (0.78, 0.88, 6, 150, -0.05),
        )
    else:
        strata = (
            (0.22, 0.78, 5, 210, +0.05),
            (0.50, 1.00, 7, 235,  0.00),
            (0.78, 0.88, 6, 175, -0.05),
        )

    cy = pad + h // 2
    cx = pad + w // 2

    # Seeded RNG so 3-ellipse silhouette breakdown is stable per spawn.
    rng_seed = (int(x) * 0x85EBCA77) ^ (int(y) * 0xC2B2AE3D)

    def _r01(idx):
        v = ((rng_seed + idx * 0x27D4EB2F) & 0xFFFF) / 0xFFFF
        return v

    # Shadow halo under the densest stratum first.
    pygame.draw.ellipse(
        s, (*edge, 50),
        pygame.Rect(pad + 4, cy + 2, w - 8, int(h * 0.55)))

    for sidx, (yfrac, wfrac, hh, a, xoff) in enumerate(strata):
        band_y = pad + int(h * yfrac)
        half_w = int(w * 0.5 * wfrac)
        band_cx = cx + int(w * xoff)
        # 3 ellipses with randomized widths per instance (0.7–1.0 ×
        # half_w) so the silhouette isn't a perfect 3-bump mirror.
        for k, ox in enumerate((-half_w * 2 // 3, 0, half_w * 2 // 3)):
            wf = 0.7 + _r01(sidx * 3 + k) * 0.3
            ow = int(half_w * wf)
            rect = pygame.Rect(band_cx + ox - ow // 2, band_y - hh,
                               ow, hh * 2)
            pygame.draw.ellipse(s, (*body, a), rect)

    # Sunlit-ridge highlight on the TOP stratum's upper edge — a thin
    # warm rim so the bank picks up sunset/golden light. Previously the
    # body was already horizon-dominated so warm-on-warm vanished.
    top_y = pad + int(h * 0.22) - 4
    top_cx = cx + int(w * 0.05)
    pygame.draw.arc(s, (*lit, 200),
                    pygame.Rect(top_cx - int(w * 0.36), top_y,
                                int(w * 0.72), 10),
                    math.radians(190), math.radians(350), 2)
    pygame.draw.arc(s, (*lit, 80),
                    pygame.Rect(top_cx - int(w * 0.36), top_y - 1,
                                int(w * 0.72), 10),
                    math.radians(200), math.radians(340), 1)

    # Dashed ink underline beneath the mid bank — replaces the previous
    # twin solid lines which read as a hard horizon ruler at 1×. Three
    # short low-alpha dashes (30%/20%/30% of band width) sell the
    # painted-ink horizon without ruling a straightedge across it.
    line_y = pad + int(h * 0.66)
    seg_specs = ((-0.45, 0.30), (-0.10, 0.20), (0.15, 0.30))
    for (sx_frac, sw_frac) in seg_specs:
        x0 = cx + int(w * sx_frac)
        x1 = x0 + int(w * sw_frac)
        pygame.draw.line(s, (*edge, 60), (x0, line_y), (x1, line_y), 1)

    surf.blit(s, (int(x - cx), int(y - cy)))


# ─────────────────────────────────────────────────────────────────────────────
# Variant 4 — Trailing Mist Veil
# Research:
#   https://www.traveliszen.com/stories/2018/huangshan-mountain-china-ghost-pines-in-the-mist
#   https://www.terrastories.com/bearings/misty_mountain
#
# Huangshan's "Sea of Clouds" sits as a horizontal blanket of low fog
# clinging to the lower ridges — not a discrete brush stroke. This veil
# is a thin horizontal alpha-gradient strip that PEAKS in the middle
# and tapers to zero at both ends, intended to be spawned ONLY in the
# lower sky band (y > 0.55 * H) so it reads as ridge-fog passing IN
# FRONT of the V14 silhouette, distinct from the Yunhai bank which
# sits behind the ridges. Replaces the round-1 cirrus streak which
# read as invisible at DAY.
# ─────────────────────────────────────────────────────────────────────────────

def draw_cloud_mistveil(surf, x, y, palette, scale=1.0):
    """Horizontal low-altitude fog ribbon clinging to a ridge."""
    body = _cloud_body_color(palette)
    lit = _lit_edge_color(palette)

    # Width 60-90 px, height 4-8 px scaled. Veil is thin by design — the
    # mass is in horizontal coverage, not vertical bulk.
    length = int(80 * scale)
    thickness = max(4, int(7 * scale))
    pad = 4
    s = _alpha_surf(length + pad * 2, thickness * 3 + pad * 2)
    cy = s.get_height() // 2

    # Phase-aware rim tint: warm at golden/sunset (horizon), pale-cool
    # at night (mix of stone_light + sky_top), neutral pale at day.
    sky_top = palette['sky_top']
    top_lum = (sky_top[0] * 299 + sky_top[1] * 587 + sky_top[2] * 114) / 1000
    if top_lum < 90:
        stone_light = palette.get('stone_light', palette['horizon'])
        rim = _lerp_color(stone_light, sky_top, 0.6)
    else:
        rim = palette['horizon']

    # Round-3 re-roll: the previous 28-stripe slice stack produced
    # visible vertical scanline bars — read like a corrupt JPEG, not
    # Huangshan fog. Replace with a small set of overlapping long thin
    # ellipses, alpha-stacked, so the silhouette has soft elliptical
    # falloff at both ends and zero per-column banding.
    #
    # Each tier is one continuous ellipse painted onto its own
    # SRCALPHA scratch and blitted with reduced alpha — the natural
    # horizontal alpha bell comes from drawing 3 progressively shorter
    # overlapping ellipses, which gives a wide soft centre and tapered
    # edges without any per-pixel mask work.
    tiers = (
        # (color, length_frac, height_frac, alpha)
        (_lerp_color(body, lit, 0.25), 0.62, 0.45, 230),  # bright top tier
        (body,                          0.92, 0.95, 215),  # main body
        (_lerp_color(body, rim, 0.45), 0.78, 0.55, 170),  # cool bottom tier
    )
    tier_y_off = (
        -max(1, thickness // 3),
         0,
         max(1, thickness // 3),
    )

    for (col, lfrac, hfrac, alpha), yo in zip(tiers, tier_y_off):
        ell_w = max(8, int(length * lfrac))
        ell_h = max(2, int(thickness * 2.2 * hfrac))
        rect = pygame.Rect(
            pad + (length - ell_w) // 2,
            cy + yo - ell_h // 2,
            ell_w, ell_h,
        )
        # Drawing the ellipse with the alpha embedded keeps it a single
        # continuous shape — no segmented surface fills, so there are
        # no column-aligned seams that could read as scanlines.
        pygame.draw.ellipse(s, (*col, alpha), rect)

    # One continuous thin lit line along the top arc — replaces the
    # previous row of 1-px specks (AD: read as a pixel row of specks).
    # Drawn as a flat ellipse a hair above the main body, with a
    # shallow height so it presents as a curved highlight line.
    top_line_w = max(8, int(length * 0.55))
    top_line_h = max(2, thickness // 2)
    top_rect = pygame.Rect(
        pad + (length - top_line_w) // 2,
        cy - thickness - top_line_h // 2,
        top_line_w, top_line_h,
    )
    pygame.draw.ellipse(s, (*lit, 110), top_rect)

    surf.blit(s, (int(x - pad - length // 2), int(y - cy)))


# ─────────────────────────────────────────────────────────────────────────────
# Variant 5 — Korean Minhwa Cloud Scroll
# Research:
#   https://en.wikipedia.org/wiki/Minhwa
#   https://koreanfolkart.org/blogs/resources/clouds-and-dragon
#
# Korean folk-painting (minhwa) cloud panels in the National Museum of
# Korea collection show flat-fill cloud silhouettes with bold dark
# outlines and one internal swirl line reading as auspicious wind.
# Different from the Hokusai curl this replaces: silhouette is a
# rounded "cloud bun" with 2-3 scallops on the top edge, no spiral, no
# curl — a single inner C-curve flourish near the top. Body fill is a
# 2-stop vertical gradient.
# ─────────────────────────────────────────────────────────────────────────────

def draw_cloud_minhwa(surf, x, y, palette, scale=1.0):
    """Korean folk cloud-bun — flat fill, bold outline, inner C-curve."""
    body = _cloud_body_color(palette)
    lit = _lit_edge_color(palette)
    stone_dark = palette.get('stone_dark', palette['mtn_far'])
    horizon = palette['horizon']

    # Bold outline — warmer at sunset (more horizon weight) and cooler
    # at night (more stone_dark) via the palette interpolation.
    outline = (
        max(0, int(stone_dark[0] * 0.70 + horizon[0] * 0.30) - 20),
        max(0, int(stone_dark[1] * 0.70 + horizon[1] * 0.30) - 20),
        max(0, int(stone_dark[2] * 0.70 + horizon[2] * 0.30) - 20),
    )
    # 2-stop body gradient: lit top, mid-shadow bottom.
    body_top = _lerp_color(body, lit, 0.30)
    body_bot = _lerp_color(body, stone_dark, 0.20)

    w = int(80 * scale)
    h = int(36 * scale)
    pad = 4
    s = _alpha_surf(w + pad * 2, h + pad * 2)

    # Silhouette: rounded-corner pillow with 3 scallops on the top edge.
    # The scallops are circle arcs; the bottom is a flat-bottom rounded
    # rect. Build as a polygon approximation (segmented) so we can fill
    # with the gradient via horizontal strips.
    cx = pad + w // 2
    body_top_y = pad + int(h * 0.30)
    body_bot_y = pad + h - 4

    # Three scallop bump centres along the top.
    scallop_centres = (
        (pad + int(w * 0.22), body_top_y, int(h * 0.30)),
        (pad + int(w * 0.50), body_top_y - int(h * 0.05), int(h * 0.34)),
        (pad + int(w * 0.78), body_top_y, int(h * 0.30)),
    )

    # 2-stop fill done by drawing two stacked rounded rects and two
    # ellipses per scallop, all flat. The gradient is faked by drawing
    # the top half in body_top and bottom half in body_bot.
    # Bottom slab (rounded rect, lower-shadow tone).
    pygame.draw.rect(
        s, (*body_bot, 240),
        pygame.Rect(pad + 4, body_top_y, w - 8, body_bot_y - body_top_y),
        border_radius=8)
    # Top slab (lit tone), capped so the gradient transition sits at
    # the cloud's vertical midline.
    mid_y = (body_top_y + body_bot_y) // 2
    pygame.draw.rect(
        s, (*body_top, 240),
        pygame.Rect(pad + 4, body_top_y, w - 8, mid_y - body_top_y),
        border_radius=8)

    # Top scallops — filled with the lit tone so they read as "bun bumps".
    for (scx, scy, scr) in scallop_centres:
        pygame.draw.circle(s, (*body_top, 245), (scx, scy), scr)

    # Bold outline (2 px) — traced as a polyline of the silhouette top
    # (3 arcs), then sides + bottom. Use arcs for the scallop outline.
    # Day-phase outline alpha is pulled 220 → 180 so the scallop edges
    # stop reading as "comic-book inked" against bright DAY sky; the
    # bolder 220 is retained for low-luminance phases where the outline
    # is what keeps the silhouette legible.
    sky_top_minhwa = palette['sky_top']
    minhwa_top_lum = (
        sky_top_minhwa[0] * 299
        + sky_top_minhwa[1] * 587
        + sky_top_minhwa[2] * 114
    ) / 1000
    outline_top_a = 180 if minhwa_top_lum > 150 else 220
    for (scx, scy, scr) in scallop_centres:
        pygame.draw.arc(
            s, (*outline, outline_top_a),
            pygame.Rect(scx - scr, scy - scr, scr * 2, scr * 2),
            math.radians(20), math.radians(160), 2)
    # Sides + bottom outline as a single rounded-rect stroke beneath
    # the slab; covers anywhere the scallop arcs don't.
    pygame.draw.rect(
        s, (*outline, 200),
        pygame.Rect(pad + 4, body_top_y, w - 8, body_bot_y - body_top_y),
        width=2, border_radius=8)

    # Inner C-curve flourish near the top — single calligraphic wind
    # line, no spiral. Sits inside the central scallop, slight inward
    # curl.
    fcx = pad + int(w * 0.50)
    fcy = body_top_y - int(h * 0.02)
    fr = int(h * 0.22)
    pygame.draw.arc(
        s, (*outline, 200),
        pygame.Rect(fcx - fr, fcy - fr // 2, fr * 2, fr),
        math.radians(200), math.radians(340), 2)

    # A tiny lit crescent along the top of the middle scallop catches
    # rim light — minhwa panels often show a single highlight stroke.
    mid_scx, mid_scy, mid_scr = scallop_centres[1]
    pygame.draw.arc(
        s, (*lit, 220),
        pygame.Rect(mid_scx - mid_scr + 3, mid_scy - mid_scr + 3,
                    (mid_scr - 3) * 2, (mid_scr - 3) * 2),
        math.radians(110), math.radians(220), 2)

    surf.blit(s, (int(x - cx), int(y - pad - h // 2)))


# ── registries ───────────────────────────────────────────────────────────────

VARIANTS = {
    1: draw_cloud_sumie,
    2: draw_cloud_ruyi,
    3: draw_cloud_yunhai,
    4: draw_cloud_mistveil,
    5: draw_cloud_minhwa,
}

VARIANT_NAMES = {
    1: "Sumi-e Ink-Wash Wisp",
    2: "Ruyi Auspicious Scroll",
    3: "Yunhai Cloud-Sea Bank",
    4: "Trailing Mist Veil",
    5: "Korean Minhwa Cloud Scroll",
}

VARIANT_SOURCES = {
    1: "asianbrushpainter.com/blogs/kb/the-use-of-ink",
    2: "en.wikipedia.org/wiki/Xiangyun_(Auspicious_clouds)",
    3: "1000museums.com Yoshida 'Sea of Clouds (Unkai)'",
    4: "traveliszen.com Huangshan ghost pines in the mist",
    5: "koreanfolkart.org clouds-and-dragon (minhwa)",
}
