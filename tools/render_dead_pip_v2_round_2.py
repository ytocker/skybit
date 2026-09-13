"""Dead-Pip v2 Round 2 — focused redesign.

Round 1 (`docs/dead_pip_v2/round_1.png`) got VERDICT: ITERATE. The
critique narrowed the field hard:

  - Drop NEON, BONE-CROSS, TWO-TONE — they fail at 96 px native.
  - Keep BEVELED (lead) and SURGICAL (simplified).
  - Lead end colour LIQUID GREEN; revised sicklier VAPOR as comparison.

This Round 2 sheet is a focused 2x2 matrix (Beveled / Surgical x Liquid
/ Vapor), a fixed gradient-transition demo (aviator cross-fade 0.2..0.6,
X cross-fade 0.85..1.0), and a TRUE 1x legibility strip alongside the 4x
craft detail so the legibility gate is unambiguous.

Pure pygame: no numpy, no surfarray. Drop shadow carried over.
"""

import math
import os
import sys

# Headless — pygbag isn't involved, we just need to save a PNG.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

sys.path.insert(0, "/home/user/skybit")

import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((1, 1))

from game import parrot  # noqa: E402


# ── palette ──────────────────────────────────────────────────────────────────
BG_TEAL       = (38, 44, 66)
SUB_TEAL      = (48, 56, 78)
PANEL_BG      = (24, 28, 42)
PANEL_EDGE    = (58, 70, 100)
LABEL_HI      = (245, 235, 210)
LABEL_DIM     = (170, 180, 210)
LABEL_HEAD    = (255, 220, 130)
TAG_BG        = (58, 38, 50)
TAG_HI        = (255, 210, 90)
SECTION_BG    = (30, 36, 54)
SECTION_EDGE  = (74, 88, 122)

# End-colour palette. LIQUID is the lead; VAPOR was revised to a more
# saturated, lower-green chartreuse so it reads "sick" rather than
# "healthy parakeet" — Round 1 had VAPOR at (200, 224, 96).
LIQUID_GREEN  = (120, 200,  90)
VAPOR_YGREEN  = (200, 215,  60)

# Drop-shadow ink — universal "fallen weight".
SHADOW_INK    = (15, 18, 28)
SHADOW_ALPHA  = 120

# Eye disc — pale base under every X glyph for contrast.
EYE_DISC      = (244, 240, 228)
EYE_DISC_RIM  = (24, 22, 28)

# Lens centres in sprite-pixel coordinates (mirror `_draw_sunglasses`).
LEFT_LENS  = (50 - 4, 20)
RIGHT_LENS = (50 + 6, 20 - 1)

SPRITE_W, SPRITE_H = parrot.SPRITE_W, parrot.SPRITE_H

# Supersample factor — heavy enough that bevel facets and stitch beads
# survive a smoothscale-down to 96 px native.
SS = 5

NATIVE_H = 96


# ── helpers ──────────────────────────────────────────────────────────────────

def _font(size: int, bold: bool = False) -> pygame.font.Font:
    return pygame.font.SysFont("dejavusans", size, bold=bold)


def _sprite_to_canvas(p: tuple[float, float],
                      offset: tuple[int, int],
                      scale: float,
                      outline_pad: int = 2) -> tuple[float, float]:
    """Map sprite-pixel coordinate (un-padded 64x60 frame) onto the
    supersampled canvas. `parrot._add_outline` pads by 2 px per side."""
    return ((p[0] + outline_pad + offset[0]) * scale,
            (p[1] + outline_pad + offset[1]) * scale)


def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def _smoothstep(edge0: float, edge1: float, x: float) -> float:
    """Standard smoothstep — used for soft alpha cross-fades."""
    if edge1 <= edge0:
        return 0.0 if x < edge1 else 1.0
    t = max(0.0, min(1.0, (x - edge0) / (edge1 - edge0)))
    return t * t * (3.0 - 2.0 * t)


# ── per-pixel body recolour (no numpy) ───────────────────────────────────────

def _tint_body_toward(big: pygame.Surface, end_color: tuple[int, int, int],
                      t: float, scale: float,
                      offset: tuple[int, int]) -> None:
    """Lerp each body-region pixel from its base RGB toward `end_color`
    by factor `t` (0 = unchanged, 1 = locked at end_color).

    Body region = head + body + tail ellipses from `parrot._build_frame`.
    Wing pixels (blue-dominant) are skipped so the silhouette identity
    carries through.
    """
    body_cx_s, body_cy_s = _sprite_to_canvas((32, 32), offset, scale)
    head_cx_s, head_cy_s = _sprite_to_canvas((47, 21), offset, scale)
    body_rx, body_ry = 19 * scale, 14 * scale
    head_rx, head_ry = 12 * scale, 11 * scale

    tail_cx_s, tail_cy_s = _sprite_to_canvas((16, 30), offset, scale)
    tail_rx, tail_ry = 18 * scale, 16 * scale

    big.lock()
    try:
        w, h = big.get_size()
        x0 = int(max(0, min(body_cx_s - body_rx, head_cx_s - head_rx,
                            tail_cx_s - tail_rx)))
        x1 = int(min(w, max(body_cx_s + body_rx, head_cx_s + head_rx,
                            tail_cx_s + tail_rx)) + 1)
        y0 = int(max(0, min(body_cy_s - body_ry, head_cy_s - head_ry,
                            tail_cy_s - tail_ry)))
        y1 = int(min(h, max(body_cy_s + body_ry, head_cy_s + head_ry,
                            tail_cy_s + tail_ry)) + 1)
        for y in range(y0, y1):
            for x in range(x0, x1):
                in_body = ((x - body_cx_s) ** 2) / (body_rx ** 2) + \
                          ((y - body_cy_s) ** 2) / (body_ry ** 2) <= 1.0
                in_head = ((x - head_cx_s) ** 2) / (head_rx ** 2) + \
                          ((y - head_cy_s) ** 2) / (head_ry ** 2) <= 1.0
                in_tail = ((x - tail_cx_s) ** 2) / (tail_rx ** 2) + \
                          ((y - tail_cy_s) ** 2) / (tail_ry ** 2) <= 1.0
                if not (in_body or in_head or in_tail):
                    continue
                r, g, b, a = big.get_at((x, y))
                if a < 24:
                    continue
                # Wing stays blue — Pip's signature flash.
                if b > r + 10 and b > g - 10:
                    continue
                # Outline strokes stay dark.
                if r + g + b < 60:
                    continue
                nr = int(_lerp(r, end_color[0], t))
                ng = int(_lerp(g, end_color[1], t))
                nb = int(_lerp(b, end_color[2], t))
                big.set_at((x, y), (nr, ng, nb, a))
    finally:
        big.unlock()


# ── eye disc ─────────────────────────────────────────────────────────────────

def _draw_eye_disc(surf: pygame.Surface, center: tuple[float, float],
                   scale: float, radius_native: float = 5.5,
                   alpha: int = 255) -> None:
    """Pale eye disc + dark socket rim. Sits under every X glyph so the
    glyph reads on a contrasting cavity regardless of body colour.

    `alpha` lets the eye disc fade in alongside the X during the
    aviator-to-X cross-fade — at low alpha the disc emerges through the
    fading aviator hole.
    """
    cx, cy = center
    r = radius_native * scale
    rim = max(1.0, 1.0 * scale)
    if alpha >= 255:
        pygame.draw.circle(surf, EYE_DISC_RIM,
                           (int(cx), int(cy)), int(r + rim))
        pygame.draw.circle(surf, EYE_DISC, (int(cx), int(cy)), int(r))
    else:
        # Composite via a scratch surface so alpha pre-multiplies cleanly.
        pad = int(r + rim + 2)
        tmp = pygame.Surface((pad * 2, pad * 2), pygame.SRCALPHA)
        pygame.draw.circle(tmp, EYE_DISC_RIM, (pad, pad), int(r + rim))
        pygame.draw.circle(tmp, EYE_DISC, (pad, pad), int(r))
        tmp.set_alpha(alpha)
        surf.blit(tmp, (int(cx) - pad, int(cy) - pad))


# ── X1: SURGICAL SUTURES (simplified per critique) ───────────────────────────

def _glyph_surgical_sutures(surf: pygame.Surface, center: tuple[float, float],
                            scale: float, alpha: int = 255) -> None:
    """Stitched-wound X — simplified for native legibility.

    Round 1 had 4 stitch beads x 2 legs + 4 knot discs = 12 sub-elements
    crammed into a ~12 px disc, which read as a black rosette at 96 px.
    Round 2:
      - 2 stitch beads per leg (not 4).
      - Knot discs reduced to a single dark pixel — barely there.
      - Wound line thickened so the diagonal cut is the dominant read.
      - Stitch beads are small bright accents on the wound line.

    Goal at 96 px native: reads "stitched wound", not "black blob with
    sparkles."
    """
    cx, cy = center
    leg_len = 4.7 * scale
    # Wound line is the dominant stroke now — was 1.1*scale in R1.
    wound_thick = max(1.0, 1.85 * scale)
    # Stitch beads are smaller bright accents, not equal partners.
    stitch_thick = max(1.0, 1.05 * scale)
    knot_r = max(0.6, 0.55 * scale)
    thread_dark = (24, 20, 28)
    thread_hi = (250, 240, 220)
    knot_dark = (16, 14, 22)

    base_tilt = 6.0

    # Draw onto a temp surface so alpha cross-fade composites cleanly.
    if alpha < 255:
        pad = int(leg_len * 1.6 + 6)
        tmp = pygame.Surface((pad * 2, pad * 2), pygame.SRCALPHA)
        local = (pad, pad)
        _glyph_surgical_sutures(tmp, local, scale, alpha=255)
        tmp.set_alpha(alpha)
        surf.blit(tmp, (int(cx) - pad, int(cy) - pad))
        return

    for ang_deg in (45 + base_tilt, -45 + base_tilt):
        a = math.radians(ang_deg)
        ux, uy = math.cos(a), math.sin(a)
        px, py = -uy, ux
        p_end_a = (cx - ux * leg_len, cy - uy * leg_len)
        p_end_b = (cx + ux * leg_len, cy + uy * leg_len)

        # Dark wound line — the dominant stroke now.
        pygame.draw.line(surf, thread_dark, p_end_a, p_end_b,
                         max(2, int(wound_thick)))

        # 2 cross-stitch beads per leg, spaced 1/3 and 2/3 along.
        n_stitches = 2
        step = (2 * leg_len) / (n_stitches + 1)
        bead_half_native = 1.7
        bead_half = bead_half_native * scale
        for i in range(1, n_stitches + 1):
            t = -leg_len + step * i
            mx = cx + ux * t
            my = cy + uy * t
            s_a = (mx + px * bead_half, my + py * bead_half)
            s_b = (mx - px * bead_half, my - py * bead_half)
            # Small bright accent — cream highlight on a thin dark casing.
            pygame.draw.line(surf, thread_dark, s_a, s_b,
                             max(1, int(stitch_thick)))
            ih_a = (s_a[0] - ux * 0.18 * scale,
                    s_a[1] - uy * 0.18 * scale)
            ih_b = (s_b[0] - ux * 0.18 * scale,
                    s_b[1] - uy * 0.18 * scale)
            pygame.draw.line(surf, thread_hi, ih_a, ih_b,
                             max(1, int(stitch_thick * 0.5)))

        # Knot discs reduced to single dark pixels at each end — minimal
        # punctuation so they don't compete with the wound line.
        for end in (p_end_a, p_end_b):
            pygame.draw.circle(surf, knot_dark,
                               (int(end[0]), int(end[1])), int(knot_r))


# ── X2: BEVELED / FACETED (polished per critique) ────────────────────────────

def _glyph_beveled(surf: pygame.Surface, center: tuple[float, float],
                   scale: float, alpha: int = 255) -> None:
    """X with 3D bevel facets — warm-white edge, warm mid-band, dark
    shadow edge. Like a gem-cut enamel pin.

    Round 2 polish:
      - Mid-stripe shifted warm to (180, 170, 165) (was cool lavender
        which read as chromatic fringing).
      - Single 1-px hot-yellow specular dot at the centre — pushes from
        "enamel" to "shiny enamel pin."
      - Dark bevel-shadow edge kept as-is.
    """
    cx, cy = center
    leg_len = 4.6 * scale
    half_w = 1.55 * scale
    base_tilt = 6.0

    if alpha < 255:
        pad = int(leg_len * 1.6 + 6)
        tmp = pygame.Surface((pad * 2, pad * 2), pygame.SRCALPHA)
        local = (pad, pad)
        _glyph_beveled(tmp, local, scale, alpha=255)
        tmp.set_alpha(alpha)
        surf.blit(tmp, (int(cx) - pad, int(cy) - pad))
        return

    bevel_hi   = (255, 252, 240)
    # Warm grey mid-band — was (200, 198, 210) lavender in R1, which
    # read as cool chromatic fringing against the green body.
    bevel_mid  = (180, 170, 165)
    bevel_lo   = (44, 38, 58)
    bevel_core = (120, 110, 122)
    # Centre specular — hot yellow, pushes the read to "shiny pin".
    specular   = (255, 240, 120)

    for ang_deg in (45 + base_tilt, -45 + base_tilt):
        a = math.radians(ang_deg)
        ux, uy = math.cos(a), math.sin(a)
        px, py = -uy, ux

        # Quad endpoints (a long rectangle along the leg axis).
        p1 = (cx - ux * leg_len + px * half_w,
              cy - uy * leg_len + py * half_w)
        p2 = (cx + ux * leg_len + px * half_w,
              cy + uy * leg_len + py * half_w)
        p3 = (cx + ux * leg_len - px * half_w,
              cy + uy * leg_len - py * half_w)
        p4 = (cx - ux * leg_len - px * half_w,
              cy - uy * leg_len - py * half_w)

        # Dark base quad — bottom-right facet shadow.
        pygame.draw.polygon(surf, bevel_lo, [p1, p2, p3, p4])

        # Centre stripe — the bevel ridge core (slightly warmer than R1).
        inset = 0.55 * scale
        c1 = (cx - ux * leg_len + px * (half_w - inset),
              cy - uy * leg_len + py * (half_w - inset))
        c2 = (cx + ux * leg_len + px * (half_w - inset),
              cy + uy * leg_len + py * (half_w - inset))
        c3 = (cx + ux * leg_len - px * (half_w - inset),
              cy + uy * leg_len - py * (half_w - inset))
        c4 = (cx - ux * leg_len - px * (half_w - inset),
              cy - uy * leg_len - py * (half_w - inset))
        pygame.draw.polygon(surf, bevel_core, [c1, c2, c3, c4])

        # Top-left highlight edge (warm-white stripe along the +p side).
        hi_w = 0.55 * scale
        h1 = (cx - ux * leg_len + px * half_w,
              cy - uy * leg_len + py * half_w)
        h2 = (cx + ux * leg_len + px * half_w,
              cy + uy * leg_len + py * half_w)
        h3 = (cx + ux * leg_len + px * (half_w - hi_w),
              cy + uy * leg_len + py * (half_w - hi_w))
        h4 = (cx - ux * leg_len + px * (half_w - hi_w),
              cy - uy * leg_len + py * (half_w - hi_w))
        pygame.draw.polygon(surf, bevel_hi, [h1, h2, h3, h4])

        # Warm mid-band between highlight and core — was cool lavender
        # in R1; now (180, 170, 165) reads as warm bevel transition.
        mid_w = 0.45 * scale
        m1 = (cx - ux * leg_len + px * (half_w - hi_w),
              cy - uy * leg_len + py * (half_w - hi_w))
        m2 = (cx + ux * leg_len + px * (half_w - hi_w),
              cy + uy * leg_len + py * (half_w - hi_w))
        m3 = (cx + ux * leg_len + px * (half_w - hi_w - mid_w),
              cy + uy * leg_len + py * (half_w - hi_w - mid_w))
        m4 = (cx - ux * leg_len + px * (half_w - hi_w - mid_w),
              cy - uy * leg_len + py * (half_w - hi_w - mid_w))
        pygame.draw.polygon(surf, bevel_mid, [m1, m2, m3, m4])

    # Single hot-yellow specular dot at the X intersection — "shiny pin"
    # signal. Sized to 1 px native (~1 px * SS = SS px at native).
    spec_r = max(1.0, 0.85 * scale)
    pygame.draw.circle(surf, specular, (int(cx), int(cy)), int(spec_r))
    # Tiny white core inside the specular for extra catchlight.
    pygame.draw.circle(surf, (255, 255, 255),
                       (int(cx - 0.15 * scale), int(cy - 0.2 * scale)),
                       max(1, int(spec_r * 0.45)))


# ── glyph dispatch ───────────────────────────────────────────────────────────

GLYPHS = {
    "surgical": _glyph_surgical_sutures,
    "beveled":  _glyph_beveled,
}

GLYPH_LABELS = {
    "surgical": "SURGICAL SUTURES",
    "beveled":  "BEVELED / FACETED",
}


def _stamp_x_glyph(big: pygame.Surface, glyph_key: str, scale: float,
                   offset: tuple[int, int], alpha: int = 255) -> None:
    """Paint the eye disc at each lens centre, then over-paint with the
    chosen X glyph style. Both eyes get the same glyph for unified read.
    """
    fn = GLYPHS[glyph_key]
    for centre in (LEFT_LENS, RIGHT_LENS):
        c = _sprite_to_canvas(centre, offset, scale)
        _draw_eye_disc(big, c, scale, alpha=alpha)
        fn(big, c, scale, alpha=alpha)


# ── aviator stripping (cross-fade) ───────────────────────────────────────────

def _strip_aviators(big: pygame.Surface, scale: float,
                    offset: tuple[int, int], strip_alpha: int) -> None:
    """Fade the in-place aviator sunglasses to reveal a bare eye socket.

    `strip_alpha` is how much of the aviator pixels to ERASE (0 = keep
    fully, 255 = fully removed). We approximate by overlaying a body-
    coloured fill disc at each lens centre with the given alpha — the
    aviator artwork stays visible beneath at (1 - alpha/255). The lens
    centre is then ready for the eye disc to cross-fade in on top.
    """
    if strip_alpha <= 0:
        return
    # Cover slightly wider than the gold rim radius (r_outer + 1 = 7 px).
    cover_r = 7.4 * scale
    for centre in (LEFT_LENS, RIGHT_LENS):
        c = _sprite_to_canvas(centre, offset, scale)
        # Pull body fill colour from a head pixel near the lens. We
        # sample a tan/feather pixel a few px below the lens so the
        # mask blends; if it's dark/outline we fall back to a neutral
        # warm tan that matches the head feather palette.
        sample_x = int(c[0])
        sample_y = int(c[1] + 4 * scale)
        sw, sh = big.get_size()
        if 0 <= sample_x < sw and 0 <= sample_y < sh:
            sr, sg, sb, sa = big.get_at((sample_x, sample_y))
        else:
            sr, sg, sb, sa = 0, 0, 0, 0
        if sa < 200 or (sr + sg + sb) < 80:
            sr, sg, sb = 230, 100, 80
        # Composite a translucent fill disc to fade the aviators out.
        pad = int(cover_r + 2)
        tmp = pygame.Surface((pad * 2, pad * 2), pygame.SRCALPHA)
        pygame.draw.circle(tmp, (sr, sg, sb, strip_alpha),
                           (pad, pad), int(cover_r))
        big.blit(tmp, (int(c[0]) - pad, int(c[1]) - pad))


# ── transitions ──────────────────────────────────────────────────────────────

END_COLORS = {
    "liquid":  LIQUID_GREEN,
    "vapor":   VAPOR_YGREEN,
}

END_LABELS = {
    "liquid":  "LIQUID GREEN  (120, 200, 90)",
    "vapor":   "VAPOR YELLOW-GREEN  (200, 215, 60)",
}


def _build_dead_sprite(end_key: str, glyph_key: str,
                       t: float = 1.0,
                       frame_idx: int = 1) -> pygame.Surface:
    """Assemble a single dead-Pip variant supersampled at SS.

    `t` is the transition factor (0 = unchanged Pip, 1 = locked at the
    end colour). Round 2 timing:
      - body colour lerps 0..1 over the full t range.
      - aviator strip-out cross-fades over t = 0.2 .. 0.6.
      - X glyph (and eye disc) cross-fades in over t = 0.85 .. 1.0.
    """
    base = parrot.FRAMES[frame_idx].copy()
    w, h = base.get_size()
    big = pygame.transform.smoothscale(base, (w * SS, h * SS))

    end_color = END_COLORS[end_key]
    _tint_body_toward(big, end_color, t, SS, (0, 0))

    # Aviator strip cross-fade — they melt away through t = 0.2..0.6.
    av_strip = int(255 * _smoothstep(0.2, 0.6, t))
    _strip_aviators(big, SS, (0, 0), av_strip)

    # X glyph + eye disc fade in over the LAST 15% of the transition.
    # The body lock + aviator removal carry frames 0..80%, the X is the
    # final punctuation mark at the very end.
    x_alpha = int(255 * _smoothstep(0.85, 1.0, t))
    if x_alpha > 0:
        _stamp_x_glyph(big, glyph_key, SS, (0, 0), alpha=x_alpha)

    return _composite_with_shadow(big, SS)


def _composite_with_shadow(sprite_big: pygame.Surface,
                           scale: float) -> pygame.Surface:
    """Universal 1 px native dark drop shadow under the body, offset
    2 px native down/right. Anchors Pip as a fallen weight.
    """
    sw, sh = sprite_big.get_size()
    pad = int(2 * scale + 6)
    canvas = pygame.Surface((sw + pad, sh + pad), pygame.SRCALPHA)

    shadow = pygame.Surface((sw, sh), pygame.SRCALPHA)
    bbox = sprite_big.get_bounding_rect()
    sprite_big.lock()
    shadow.lock()
    try:
        for y in range(bbox.y, bbox.y + bbox.h):
            for x in range(bbox.x, bbox.x + bbox.w):
                a = sprite_big.get_at((x, y))[3]
                if a > 24:
                    shadow.set_at((x, y), (SHADOW_INK[0], SHADOW_INK[1],
                                           SHADOW_INK[2], SHADOW_ALPHA))
    finally:
        sprite_big.unlock()
        shadow.unlock()

    off = int(2 * scale)
    canvas.blit(shadow, (off, off))
    canvas.blit(sprite_big, (0, 0))
    return canvas


# ── render helpers ───────────────────────────────────────────────────────────

def _render_at(end_key: str, glyph_key: str, t: float,
               target_h: int) -> pygame.Surface:
    big = _build_dead_sprite(end_key, glyph_key, t=t)
    bw, bh = big.get_size()
    target_w = int(bw * (target_h / bh))
    return pygame.transform.smoothscale(big, (target_w, target_h))


def _swatch_disc(diameter: int, color, ring_color=(74, 92, 132)) -> pygame.Surface:
    surf = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
    r = diameter // 2
    pygame.draw.circle(surf, ring_color, (r, r), r)
    for i in range(r - 2, 0, -1):
        tt = 1.0 - (i / (r - 2))
        col = (
            int(color[0] * (0.80 + 0.20 * (1 - tt))),
            int(color[1] * (0.80 + 0.20 * (1 - tt))),
            int(color[2] * (0.80 + 0.20 * (1 - tt))),
        )
        pygame.draw.circle(surf, col, (r, r), i)
    return surf


def _eye_crop_zoom(glyph_key: str, target_size: int) -> pygame.Surface:
    """Render a single eye glyph centred on a dawn-teal swatch at the
    given pixel size — for the 4x detail row.
    """
    canvas = pygame.Surface((target_size, target_size), pygame.SRCALPHA)
    canvas.blit(_swatch_disc(target_size, BG_TEAL), (0, 0))

    scale = 12.0
    pad = int(8 * scale)
    glyph_canvas = pygame.Surface((pad * 2, pad * 2), pygame.SRCALPHA)
    centre = (pad, pad)
    _draw_eye_disc(glyph_canvas, centre, scale, radius_native=5.5)
    GLYPHS[glyph_key](glyph_canvas, centre, scale)
    target = int(target_size * 0.72)
    scaled = pygame.transform.smoothscale(glyph_canvas, (target, target))
    canvas.blit(scaled, ((target_size - target) // 2,
                         (target_size - target) // 2))
    return canvas


def _eye_native_strip(glyph_key: str, swatch_size: int) -> pygame.Surface:
    """Render a single eye glyph at TRUE native disc size (~11-13 px
    radius) on the dawn-teal swatch — no zoom. This is the legibility
    gate: what you actually see on Pip in-game.
    """
    canvas = pygame.Surface((swatch_size, swatch_size), pygame.SRCALPHA)
    canvas.blit(_swatch_disc(swatch_size, BG_TEAL), (0, 0))

    # Supersample the glyph at SS=5, then smoothscale down to native.
    # native disc radius matches the in-game eye disc: 5.5 px native.
    # Total glyph footprint extends a few px beyond the disc (knots,
    # bevel ends) so we pad the canvas to 16 px native.
    native_d = 18
    big_scale = 6.0
    pad = int(native_d / 2 * big_scale)
    tmp = pygame.Surface((pad * 2, pad * 2), pygame.SRCALPHA)
    centre = (pad, pad)
    _draw_eye_disc(tmp, centre, big_scale, radius_native=5.5)
    GLYPHS[glyph_key](tmp, centre, big_scale)
    native = pygame.transform.smoothscale(tmp, (native_d, native_d))
    # Centre the native glyph on the swatch.
    canvas.blit(native, ((swatch_size - native_d) // 2,
                         (swatch_size - native_d) // 2))
    return canvas


# ── section builders ─────────────────────────────────────────────────────────

def _section_header(width: int, height: int, tag: str, head: str,
                    sub: str) -> pygame.Surface:
    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.rect(surf, SECTION_BG, surf.get_rect(), border_radius=14)
    pygame.draw.rect(surf, SECTION_EDGE, surf.get_rect(), width=2,
                     border_radius=14)
    tag_surf = _font(18, bold=True).render(tag, True, TAG_HI)
    head_surf = _font(22, bold=True).render(head, True, LABEL_HI)
    sub_surf = _font(14).render(sub, True, LABEL_DIM)
    surf.blit(tag_surf, (16, 10))
    surf.blit(head_surf, (16 + tag_surf.get_width() + 14, 8))
    surf.blit(sub_surf, (16, 12 + head_surf.get_height()))
    return surf


def build_section_1_transition(width: int) -> pygame.Surface:
    """Top section — 5 frames of BEVELED + LIQUID GREEN at
    t = 0/25/50/75/100% showing the fixed transition timing.

    Critique fixes:
      - X cross-fades 0.85..1.0 instead of pop-in at t = 0.5.
      - Aviator strip cross-fades 0.2..0.6 instead of hard cut.
      - Demo now uses the recommended pairing (Beveled + Liquid Green).
    """
    cell_d = 142
    cell_gap = 20
    label_h = 30
    head_h = 64
    pad = 24
    n = 5
    inner_w = pad * 2 + cell_d * n + cell_gap * (n - 1)
    total_w = max(width, inner_w)
    total_h = head_h + pad + cell_d + 8 + label_h + pad

    sect = pygame.Surface((total_w, total_h), pygame.SRCALPHA)
    pygame.draw.rect(sect, SECTION_BG, sect.get_rect(), border_radius=14)
    pygame.draw.rect(sect, SECTION_EDGE, sect.get_rect(), width=2,
                     border_radius=14)

    head = _section_header(
        total_w - 24, head_h, "SECTION 1",
        "GRADIENT TRANSITION  (lead pairing)",
        "BEVELED X + LIQUID GREEN.  Aviator cross-fades over t = 0.2..0.6.  "
        "X glyph cross-fades over t = 0.85..1.0 — final punctuation.")
    sect.blit(head, (12, 8))

    x = (total_w - inner_w) // 2 + pad
    y = head_h + pad
    ts = [0.0, 0.25, 0.5, 0.75, 1.0]
    for t in ts:
        cell = pygame.Surface((cell_d, cell_d + label_h + 6), pygame.SRCALPHA)
        swatch = _swatch_disc(cell_d, BG_TEAL)
        cell.blit(swatch, (0, 0))
        sprite = _render_at("liquid", "beveled", t, NATIVE_H)
        sx = (cell_d - sprite.get_width()) // 2
        sy = (cell_d - sprite.get_height()) // 2
        cell.blit(sprite, (sx, sy))
        lab = _font(16, bold=True).render(f"t = {int(t * 100):>3d}%",
                                          True, LABEL_HEAD)
        cell.blit(lab, ((cell_d - lab.get_width()) // 2,
                        cell_d + 4))
        sect.blit(cell, (x, y))
        x += cell_d + cell_gap

    return sect


def build_section_2_matrix(width: int) -> pygame.Surface:
    """Focused 2x2 matrix — BEVELED / SURGICAL x LIQUID / VAPOR.
    All cells at 96 px native, t = 1.0 (fully poisoned)."""
    glyph_keys = ["beveled", "surgical"]
    end_keys = ["liquid", "vapor"]

    cell_d = 168
    cell_gap = 28
    row_label_w = 210
    col_label_h = 38
    head_h = 64
    pad = 24

    inner_w = row_label_w + cell_gap + (cell_d + cell_gap) * len(glyph_keys)
    inner_h = head_h + col_label_h + (cell_d + cell_gap) * len(end_keys)
    total_w = max(width, inner_w + pad * 2)
    total_h = inner_h + pad * 2

    sect = pygame.Surface((total_w, total_h), pygame.SRCALPHA)
    pygame.draw.rect(sect, SECTION_BG, sect.get_rect(), border_radius=14)
    pygame.draw.rect(sect, SECTION_EDGE, sect.get_rect(), width=2,
                     border_radius=14)

    head = _section_header(
        total_w - 24, head_h, "SECTION 2",
        "FOCUSED 2 x 2 MATRIX",
        "Rows = end-colour finalists.  Cols = X-glyph finalists.  "
        "All at 96 px native, t = 1.0 (fully poisoned).")
    sect.blit(head, (12, 8))

    grid_x0 = (total_w - inner_w) // 2
    grid_y0 = head_h + pad

    # Column headers.
    for ci, g in enumerate(glyph_keys):
        cx = grid_x0 + row_label_w + cell_gap + ci * (cell_d + cell_gap)
        lab = _font(15, bold=True).render(GLYPH_LABELS[g], True, LABEL_HEAD)
        sect.blit(lab, (cx + (cell_d - lab.get_width()) // 2,
                        grid_y0 + (col_label_h - lab.get_height()) // 2))
        # Mark the lead glyph.
        if g == "beveled":
            badge = _font(11, bold=True).render("LEAD", True, TAG_HI)
            sect.blit(badge,
                      (cx + (cell_d - badge.get_width()) // 2,
                       grid_y0 + col_label_h - 4))

    # Rows.
    for ri, e in enumerate(end_keys):
        ry = grid_y0 + col_label_h + ri * (cell_d + cell_gap)
        row_rect = pygame.Rect(grid_x0, ry, row_label_w, cell_d)
        pygame.draw.rect(sect, PANEL_BG, row_rect, border_radius=10)
        pygame.draw.rect(sect, PANEL_EDGE, row_rect, width=1,
                         border_radius=10)
        name_lab = _font(16, bold=True)
        if e == "liquid":
            head_str = "LIQUID GREEN"
            sub_str = "(120, 200, 90)"
            chip = LIQUID_GREEN
            tag_str = "LEAD"
        else:
            head_str = "VAPOR (revised)"
            sub_str = "(200, 215, 60)"
            chip = VAPOR_YGREEN
            tag_str = "compare"

        head_surf = name_lab.render(head_str, True, LABEL_HI)
        sub_surf = _font(13).render(sub_str, True, LABEL_DIM)
        sect.blit(head_surf, (row_rect.x + 14, row_rect.y + 16))
        sect.blit(sub_surf,
                  (row_rect.x + 14,
                   row_rect.y + 16 + head_surf.get_height() + 2))

        # Colour chip.
        chip_y = row_rect.y + 16 + head_surf.get_height() + \
                 sub_surf.get_height() + 14
        chip_w = 56
        chip_h = 26
        pygame.draw.rect(sect, chip,
                         (row_rect.x + 14, chip_y, chip_w, chip_h),
                         border_radius=6)
        pygame.draw.rect(sect, (220, 220, 230),
                         (row_rect.x + 14, chip_y, chip_w, chip_h),
                         width=1, border_radius=6)

        # Role tag.
        tag_surf = _font(12, bold=True).render(
            tag_str, True,
            TAG_HI if tag_str == "LEAD" else LABEL_DIM)
        sect.blit(tag_surf,
                  (row_rect.x + 14 + chip_w + 10, chip_y + 6))

        for ci, g in enumerate(glyph_keys):
            cx = grid_x0 + row_label_w + cell_gap + ci * (cell_d + cell_gap)
            swatch = _swatch_disc(cell_d, BG_TEAL)
            sect.blit(swatch, (cx, ry))
            sprite = _render_at(e, g, 1.0, NATIVE_H)
            sx = cx + (cell_d - sprite.get_width()) // 2
            sy = ry + (cell_d - sprite.get_height()) // 2
            sect.blit(sprite, (sx, sy))

    return sect


def build_section_3_legibility(width: int) -> pygame.Surface:
    """Bottom section — TRUE 1x legibility strip beside 4x craft detail.

    Sub-row A: 4x zoom of BEVELED + SURGICAL eye glyphs.
    Sub-row B: SAME glyphs at TRUE in-game disc size (no zoom).

    The point is to make the gap between "looks beautiful zoomed" and
    "actually reads on the bird" unmissable — this is the legibility
    gate that decides what ships.
    """
    crop_size = 220
    native_swatch = 96
    crop_gap = 40
    label_h = 28
    row_gap = 24
    head_h = 64
    pad = 28
    # Two columns: each column shows 4x detail above + 1x native below.
    col_w = max(crop_size, native_swatch)

    inner_w = pad * 2 + 2 * col_w + crop_gap
    total_w = max(width, inner_w)
    total_h = (head_h + pad + crop_size + label_h + row_gap +
               native_swatch + label_h + pad + 14)

    sect = pygame.Surface((total_w, total_h), pygame.SRCALPHA)
    pygame.draw.rect(sect, SECTION_BG, sect.get_rect(), border_radius=14)
    pygame.draw.rect(sect, SECTION_EDGE, sect.get_rect(), width=2,
                     border_radius=14)

    head = _section_header(
        total_w - 24, head_h, "SECTION 3",
        "LEGIBILITY GATE",
        "4x detail = craft.  1x native = what ships on Pip.  "
        "If a glyph reads beautifully at 4x but vanishes at 1x, it loses.")
    sect.blit(head, (12, 8))

    # Sub-row tag labels.
    tag_a = _font(13, bold=True).render(
        "SUB-ROW A: 4x detail (craft) — does the concept hold?",
        True, LABEL_HEAD)
    tag_b = _font(13, bold=True).render(
        "SUB-ROW B: 1x actual in-game disc size (~18 px) — does it READ?",
        True, LABEL_HEAD)

    sect.blit(tag_a, (pad, head_h + 6))
    row_y_a = head_h + 6 + tag_a.get_height() + 6

    # Sub-row A — 4x detail crops side-by-side.
    x = (total_w - (2 * crop_size + crop_gap)) // 2
    for g in ("beveled", "surgical"):
        crop = _eye_crop_zoom(g, crop_size)
        sect.blit(crop, (x, row_y_a))
        lab = _font(15, bold=True).render(GLYPH_LABELS[g], True, LABEL_HEAD)
        sect.blit(lab, (x + (crop_size - lab.get_width()) // 2,
                        row_y_a + crop_size + 6))
        x += crop_size + crop_gap

    row_y_b_tag = row_y_a + crop_size + label_h + row_gap
    sect.blit(tag_b, (pad, row_y_b_tag))
    row_y_b = row_y_b_tag + tag_b.get_height() + 6

    # Sub-row B — TRUE native size on swatches.
    # Lay them at the same x positions for visual alignment, so the
    # reviewer can scan top -> bottom in each column.
    x = (total_w - (2 * crop_size + crop_gap)) // 2
    for g in ("beveled", "surgical"):
        native_strip = _eye_native_strip(g, native_swatch)
        # Centre the small native swatch inside the column width.
        nx = x + (crop_size - native_swatch) // 2
        sect.blit(native_strip, (nx, row_y_b))
        lab = _font(14, bold=True).render(GLYPH_LABELS[g], True, LABEL_HEAD)
        sect.blit(lab, (x + (crop_size - lab.get_width()) // 2,
                        row_y_b + native_swatch + 4))
        x += crop_size + crop_gap

    return sect


# ── final sheet ──────────────────────────────────────────────────────────────

def build_sheet() -> pygame.Surface:
    title_h = 100
    sheet_w = 1240
    pad_x = 30
    gutter = 22

    section_w = sheet_w - pad_x * 2

    sec1 = build_section_1_transition(section_w)
    sec2 = build_section_2_matrix(section_w)
    sec3 = build_section_3_legibility(section_w)

    sheet_h = (title_h + sec1.get_height() + sec2.get_height()
               + sec3.get_height() + gutter * 4 + 20)
    sheet = pygame.Surface((sheet_w, sheet_h))

    # Soft vertical gradient backdrop — section cards lift off slightly.
    for y in range(sheet_h):
        tt = y / max(1, sheet_h - 1)
        col = (
            int(BG_TEAL[0] * (1 - tt * 0.30)),
            int(BG_TEAL[1] * (1 - tt * 0.25)),
            int(BG_TEAL[2] * (1 - tt * 0.18)),
        )
        pygame.draw.line(sheet, col, (0, y), (sheet_w, y))

    title_font = _font(34, bold=True)
    title = title_font.render(
        "DEAD PIP v2  —  Round 2  "
        "(focused: Beveled + Surgical  x  Liquid + Vapor)",
        True, LABEL_HI)
    sheet.blit(title, ((sheet_w - title.get_width()) // 2, 22))
    sub_font = _font(16)
    sub = sub_font.render(
        "ITERATE -> focus.  Dropped Neon / Bone-Cross / Two-Tone.  "
        "Polished bevel + simplified sutures + fixed transition + true-size legibility.",
        True, LABEL_DIM)
    sheet.blit(sub, ((sheet_w - sub.get_width()) // 2,
                     22 + title.get_height() + 6))

    y = title_h + gutter
    sheet.blit(sec1, ((sheet_w - sec1.get_width()) // 2, y))
    y += sec1.get_height() + gutter
    sheet.blit(sec2, ((sheet_w - sec2.get_width()) // 2, y))
    y += sec2.get_height() + gutter
    sheet.blit(sec3, ((sheet_w - sec3.get_width()) // 2, y))

    return sheet


if __name__ == "__main__":
    out_path = "/home/user/skybit/docs/dead_pip_v2/round_2.png"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    sheet = build_sheet()
    pygame.image.save(sheet, out_path)
    print(f"Saved {out_path} ({sheet.get_width()}x{sheet.get_height()})")
