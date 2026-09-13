"""Dead-Pip v2 Round 1.

The Round-3 winner ("Classic X-Eyes") was rejected by the user as
"basically the same X in different colours" — not cutting-edge enough.
This v2 round splits the exploration along TWO axes the user named:

  - end colour (where Pip's body locks once the poison transition
    completes) — three options: liquid green, vapor yellow-green,
    painterly two-tone (vapor body + liquid-green shadows).
  - X-glyph style (the cutting-edge eye mark) — four options:
    surgical sutures, beveled/faceted, neon glow, mini bone-cross.

Each variant paints the real in-game parrot sprite — supersampled 5x,
per-pixel lerped toward the end colour, eyes over-painted with the
chosen X glyph, smoothscaled back down. The sheet also shows a
5-frame transition demo (t = 0/25/50/75/100%) so reviewers can read
the time-locked colour shift, and a 4-eye detail row so each X glyph
is legible without zooming.

Pure pygame: no numpy, no surfarray. Drop shadow carried over from
Round 3 anchors every body as a "fallen weight."
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

# End-colour palette options the user named verbatim.
LIQUID_GREEN  = (120, 200,  90)
VAPOR_YGREEN  = (200, 224,  96)

# Drop-shadow ink — carried over from Round 3 (universal "fallen weight").
SHADOW_INK    = (15, 18, 28)
SHADOW_ALPHA  = 120

# Eye glyph constants — every X over-paints a small pale disc so it
# survives over both warm body feathers and the dark socket below.
EYE_DISC      = (244, 240, 228)
EYE_DISC_RIM  = (24, 22, 28)

# Lens centres in sprite-pixel coordinates (mirror `_draw_sunglasses`).
LEFT_LENS  = (50 - 4, 20)
RIGHT_LENS = (50 + 6, 20 - 1)

SPRITE_W, SPRITE_H = parrot.SPRITE_W, parrot.SPRITE_H

# Supersample factor — heavy enough that bone knobs, suture knots and
# bevel edges all survive a smoothscale-down to 96 px native.
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


def _lerp_rgb(a, b, t):
    return (int(_lerp(a[0], b[0], t)),
            int(_lerp(a[1], b[1], t)),
            int(_lerp(a[2], b[2], t)))


# ── per-pixel body recolour (no numpy) ───────────────────────────────────────

def _tint_body_toward(big: pygame.Surface, end_color: tuple[int, int, int],
                      t: float, scale: float, offset: tuple[int, int],
                      *, shadow_color: tuple[int, int, int] | None = None,
                      luma_pivot: float = 110.0) -> None:
    """Lerp each body-region pixel from its base RGB toward `end_color`
    by factor `t` (0 = unchanged, 1 = locked at end_color). When
    `shadow_color` is supplied, dark/shadow pixels (below `luma_pivot`)
    lerp toward `shadow_color` instead — painterly two-tone variant.

    Body region = head ellipse + body ellipse from `parrot._build_frame`.
    Wing pixels (blue-dominant) and tail pixels (lower-left orange-yellow
    region) are skipped so silhouette identity carries through.
    """
    body_cx_s, body_cy_s = _sprite_to_canvas((32, 32), offset, scale)
    head_cx_s, head_cy_s = _sprite_to_canvas((47, 21), offset, scale)
    body_rx, body_ry = 19 * scale, 14 * scale
    head_rx, head_ry = 12 * scale, 11 * scale

    # Also lerp tail toward the end colour at the SAME rate — the user
    # wants the WHOLE bird's body locking, not just head+belly.
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
                # Skip wing — wing is blue-dominant and reads as Pip's
                # signature flash; tinting it dilutes the silhouette.
                if b > r + 10 and b > g - 10:
                    continue
                # Skip near-black outline strokes — they should stay dark.
                if r + g + b < 60:
                    continue
                # Two-tone branch — shadow pixels lerp toward the deeper
                # liquid-green so the painterly read sells "vapor lit body,
                # liquid shadow." Branch on perceived luma.
                luma = 0.299 * r + 0.587 * g + 0.114 * b
                if shadow_color is not None and luma < luma_pivot:
                    target = shadow_color
                else:
                    target = end_color
                nr = int(_lerp(r, target[0], t))
                ng = int(_lerp(g, target[1], t))
                nb = int(_lerp(b, target[2], t))
                big.set_at((x, y), (nr, ng, nb, a))
    finally:
        big.unlock()


# ── eye disc + X glyph styles ────────────────────────────────────────────────

def _draw_eye_disc(surf: pygame.Surface, center: tuple[float, float],
                   scale: float, radius_native: float = 5.5) -> None:
    """Pale eye disc + dark socket rim. Sits under every X glyph so the
    glyph reads on a contrasting cavity regardless of body colour."""
    cx, cy = center
    r = radius_native * scale
    rim = max(1.0, 1.0 * scale)
    pygame.draw.circle(surf, EYE_DISC_RIM, (int(cx), int(cy)), int(r + rim))
    pygame.draw.circle(surf, EYE_DISC, (int(cx), int(cy)), int(r))


# ── X1: SURGICAL SUTURES ─────────────────────────────────────────────────────

def _glyph_surgical_sutures(surf: pygame.Surface, center: tuple[float, float],
                            scale: float) -> None:
    """X built from two crossed surgical sutures. Each leg is a thin dark
    diagonal "wound line" with 4 short perpendicular stitch beads
    crossing it, plus a small dark knot disc at each of the four end
    points. Reads as medical / poisoned because the perpendicular beads
    cleanly subdivide the diagonal into stitches without scrambling it.
    """
    cx, cy = center
    leg_len = 4.7 * scale
    stitch_thick = max(1.0, 1.4 * scale)
    wound_thick = max(1.0, 1.1 * scale)
    knot_r = max(1.0, 1.15 * scale)
    knot_inner_r = max(0.5, 0.5 * scale)
    thread_dark = (24, 20, 28)
    thread_hi = (245, 245, 240)
    knot_dark = (16, 14, 22)

    # Slight overall tilt away from a perfect +/-45 so the X reads hand-stitched
    base_tilt = 6.0

    for ang_deg in (45 + base_tilt, -45 + base_tilt):
        a = math.radians(ang_deg)
        ux, uy = math.cos(a), math.sin(a)
        # Perpendicular for the cross-stitch beads.
        px, py = -uy, ux
        p_end_a = (cx - ux * leg_len, cy - uy * leg_len)
        p_end_b = (cx + ux * leg_len, cy + uy * leg_len)

        # Dark wound line down the spine of the leg — the cut the
        # stitch closes; thinner than the beads so beads dominate.
        pygame.draw.line(surf, thread_dark, p_end_a, p_end_b,
                         max(1, int(wound_thick)))

        # Cross-stitch beads: 4 short perpendicular segments stepped
        # uniformly along the leg. Each bead is a cream-cored dark stroke
        # — the classic "+" pattern stitched diagonally across the wound.
        n_stitches = 4
        step = (2 * leg_len) / (n_stitches + 1)
        bead_half_native = 1.5
        bead_half = bead_half_native * scale
        for i in range(1, n_stitches + 1):
            t = -leg_len + step * i
            mx = cx + ux * t
            my = cy + uy * t
            s_a = (mx + px * bead_half, my + py * bead_half)
            s_b = (mx - px * bead_half, my - py * bead_half)
            # Dark casing under the bead so it reads on cream/light bodies.
            pygame.draw.line(surf, thread_dark, s_a, s_b,
                             max(1, int(stitch_thick)))
            # Cream inner thread highlight.
            ih_a = (s_a[0] - ux * 0.18 * scale, s_a[1] - uy * 0.18 * scale)
            ih_b = (s_b[0] - ux * 0.18 * scale, s_b[1] - uy * 0.18 * scale)
            pygame.draw.line(surf, thread_hi, ih_a, ih_b,
                             max(1, int(stitch_thick * 0.45)))

        # Knot discs at each end — dark filled disc with a tiny cream
        # highlight, reads as "tied off thread end."
        for end in (p_end_a, p_end_b):
            pygame.draw.circle(surf, knot_dark,
                               (int(end[0]), int(end[1])), int(knot_r))
            pygame.draw.circle(surf, thread_hi,
                               (int(end[0] - 0.45 * scale),
                                int(end[1] - 0.45 * scale)),
                               int(knot_inner_r))


# ── X2: BEVELED / FACETED ────────────────────────────────────────────────────

def _glyph_beveled(surf: pygame.Surface, center: tuple[float, float],
                   scale: float) -> None:
    """X with 3D bevel facets — warm white edge top-left, deep purple-black
    shadow edge bottom-right. Like a gem-cut enamel pin. Each leg is a
    quad with a centre highlight stripe and a darker bottom-right edge.
    """
    cx, cy = center
    leg_len = 4.6 * scale
    half_w = 1.55 * scale
    base_tilt = 6.0

    bevel_hi   = (255, 252, 240)
    bevel_mid  = (200, 198, 210)
    bevel_lo   = (44, 38, 58)
    bevel_core = (110, 108, 130)

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

        # Lighter centre stripe — the bevel ridge.
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

        # Top-left highlight edge (thin warm-white stripe along the +p side).
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

        # Mid-grey transition stripe between hi and core for the gem facet.
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


# ── X3: NEON GLOW ────────────────────────────────────────────────────────────

def _glyph_neon(surf: pygame.Surface, center: tuple[float, float],
                scale: float) -> None:
    """X with a bright white inner core and a luminous warning-red halo.
    Drawn by stacking translucent X strokes from wide+soft to narrow+hot.
    """
    cx, cy = center
    leg_len = 4.7 * scale
    base_tilt = 6.0
    halo_color = (255, 80, 60)
    core_color = (255, 255, 255)
    hot_mid = (255, 180, 150)

    # Halo passes — three increasingly tighter wide strokes with alpha.
    halo_steps = [
        (4.8, 60),
        (3.2, 110),
        (2.2, 180),
    ]
    # Use a temporary RGBA surface for additive-ish glow stacking so
    # the halo composites cleanly over body recolour.
    pad = int(leg_len * 2 + 6)
    glow = pygame.Surface((pad * 2, pad * 2), pygame.SRCALPHA)
    gx, gy = pad, pad

    for thick_native, alpha in halo_steps:
        thick = max(1, int(thick_native * scale))
        col = (*halo_color, alpha)
        for ang_deg in (45 + base_tilt, -45 + base_tilt):
            a = math.radians(ang_deg)
            ux, uy = math.cos(a), math.sin(a)
            p1 = (gx - ux * leg_len, gy - uy * leg_len)
            p2 = (gx + ux * leg_len, gy + uy * leg_len)
            pygame.draw.line(glow, col, p1, p2, thick)

    # Hot orange-pink mid layer.
    for ang_deg in (45 + base_tilt, -45 + base_tilt):
        a = math.radians(ang_deg)
        ux, uy = math.cos(a), math.sin(a)
        p1 = (gx - ux * leg_len, gy - uy * leg_len)
        p2 = (gx + ux * leg_len, gy + uy * leg_len)
        pygame.draw.line(glow, (*hot_mid, 235),
                         p1, p2, max(1, int(1.6 * scale)))

    # Bright white inner core — the lit filament.
    for ang_deg in (45 + base_tilt, -45 + base_tilt):
        a = math.radians(ang_deg)
        ux, uy = math.cos(a), math.sin(a)
        p1 = (gx - ux * leg_len, gy - uy * leg_len)
        p2 = (gx + ux * leg_len, gy + uy * leg_len)
        pygame.draw.line(glow, (*core_color, 255),
                         p1, p2, max(1, int(0.9 * scale)))

    # Small bright bloom at the centre — "lit warning lamp".
    pygame.draw.circle(glow, (*core_color, 240),
                       (gx, gy), max(1, int(0.9 * scale)))

    surf.blit(glow, (int(cx - pad), int(cy - pad)),
              special_flags=pygame.BLEND_PREMULTIPLIED)


# ── X4: MINI BONE-CROSS ──────────────────────────────────────────────────────

def _glyph_bone_cross(surf: pygame.Surface, center: tuple[float, float],
                      scale: float) -> None:
    """Tiny crossed femurs with knobbed (rounded) epiphyses at the four
    leg ends. Bone cream with a thin shadow line. Mirrors the poison
    vial's crossed-bones label.
    """
    cx, cy = center
    leg_len = 4.6 * scale
    shaft_half = 0.95 * scale
    knob_r = 1.55 * scale
    base_tilt = 6.0

    bone_cream = (244, 240, 220)
    bone_shadow = (180, 170, 145)
    bone_dark = (24, 22, 28)

    for ang_deg in (45 + base_tilt, -45 + base_tilt):
        a = math.radians(ang_deg)
        ux, uy = math.cos(a), math.sin(a)
        px, py = -uy, ux

        # Shaft endpoints (slightly inset so knobs straddle the ends).
        end_a = (cx - ux * (leg_len - 0.4 * scale),
                 cy - uy * (leg_len - 0.4 * scale))
        end_b = (cx + ux * (leg_len - 0.4 * scale),
                 cy + uy * (leg_len - 0.4 * scale))

        # Dark shaft outline (wider) — gives the bone a defined edge.
        outline_half = shaft_half + max(0.5, 0.55 * scale)
        o1 = (end_a[0] + px * outline_half, end_a[1] + py * outline_half)
        o2 = (end_b[0] + px * outline_half, end_b[1] + py * outline_half)
        o3 = (end_b[0] - px * outline_half, end_b[1] - py * outline_half)
        o4 = (end_a[0] - px * outline_half, end_a[1] - py * outline_half)
        pygame.draw.polygon(surf, bone_dark, [o1, o2, o3, o4])

        # Cream shaft.
        s1 = (end_a[0] + px * shaft_half, end_a[1] + py * shaft_half)
        s2 = (end_b[0] + px * shaft_half, end_b[1] + py * shaft_half)
        s3 = (end_b[0] - px * shaft_half, end_b[1] - py * shaft_half)
        s4 = (end_a[0] - px * shaft_half, end_a[1] - py * shaft_half)
        pygame.draw.polygon(surf, bone_cream, [s1, s2, s3, s4])

        # Shadow strip along the bottom-right side of the shaft.
        sh_w = shaft_half * 0.55
        sh1 = (end_a[0] - px * (shaft_half - sh_w),
               end_a[1] - py * (shaft_half - sh_w))
        sh2 = (end_b[0] - px * (shaft_half - sh_w),
               end_b[1] - py * (shaft_half - sh_w))
        sh3 = (end_b[0] - px * shaft_half, end_b[1] - py * shaft_half)
        sh4 = (end_a[0] - px * shaft_half, end_a[1] - py * shaft_half)
        pygame.draw.polygon(surf, bone_shadow, [sh1, sh2, sh3, sh4])

        # Two knobbed epiphyses per leg (rounded twin knobs at each end).
        for end in (end_a, end_b):
            for side in (-1.0, 1.0):
                kx = end[0] + px * side * knob_r * 0.65
                ky = end[1] + py * side * knob_r * 0.65
                # Outline knob (dark) then cream + small shadow inside.
                pygame.draw.circle(surf, bone_dark,
                                   (int(kx), int(ky)),
                                   int(knob_r + max(0.5, 0.5 * scale)))
                pygame.draw.circle(surf, bone_cream,
                                   (int(kx), int(ky)), int(knob_r))
                pygame.draw.circle(surf, bone_shadow,
                                   (int(kx + 0.35 * scale),
                                    int(ky + 0.35 * scale)),
                                   max(1, int(knob_r * 0.55)))


# ── glyph dispatch ───────────────────────────────────────────────────────────

GLYPHS = {
    "surgical": _glyph_surgical_sutures,
    "beveled":  _glyph_beveled,
    "neon":     _glyph_neon,
    "bone":     _glyph_bone_cross,
}

GLYPH_LABELS = {
    "surgical": "SURGICAL SUTURES",
    "beveled":  "BEVELED / FACETED",
    "neon":     "NEON GLOW",
    "bone":     "MINI BONE-CROSS",
}


def _stamp_x_glyph(big: pygame.Surface, glyph_key: str, scale: float,
                   offset: tuple[int, int]) -> None:
    """Paint the eye disc at each lens centre, then over-paint with the
    chosen X glyph style. Both eyes get the same glyph for unified read."""
    fn = GLYPHS[glyph_key]
    for centre in (LEFT_LENS, RIGHT_LENS):
        c = _sprite_to_canvas(centre, offset, scale)
        _draw_eye_disc(big, c, scale)
        fn(big, c, scale)


# ── transitions ──────────────────────────────────────────────────────────────

END_COLORS = {
    "liquid":  {"body": LIQUID_GREEN, "shadow": None},
    "vapor":   {"body": VAPOR_YGREEN, "shadow": None},
    "twotone": {"body": VAPOR_YGREEN, "shadow": LIQUID_GREEN},
}

END_LABELS = {
    "liquid":  "LIQUID GREEN  (120, 200, 90)",
    "vapor":   "VAPOR YELLOW-GREEN  (200, 224, 96)",
    "twotone": "TWO-TONE  (vapor body / liquid shadows)",
}


def _build_dead_sprite(end_key: str, glyph_key: str,
                       t: float = 1.0,
                       frame_idx: int = 1) -> pygame.Surface:
    """Assemble a single dead-Pip variant supersampled at SS.

    `t` is the transition factor (0 = unchanged Pip, 1 = locked at the
    end colour). Frame 1 is a near-neutral wing pose (mid-up) so the
    silhouette is recognisable and uncluttered for review.
    """
    base = parrot.FRAMES[frame_idx].copy()
    w, h = base.get_size()
    big = pygame.transform.smoothscale(base, (w * SS, h * SS))

    spec = END_COLORS[end_key]
    _tint_body_toward(big, spec["body"], t, SS, (0, 0),
                      shadow_color=spec["shadow"])

    # X glyph fades in over the second half of the transition so early
    # frames show the colour shift without the glyph dominating.
    # At t=0 the bird still has aviators; at t>=0.5 the X is fully drawn.
    if t >= 0.5:
        _stamp_x_glyph(big, glyph_key, SS, (0, 0))

    return _composite_with_shadow(big, SS)


def _composite_with_shadow(sprite_big: pygame.Surface,
                           scale: float) -> pygame.Surface:
    """Universal 1 px native dark drop shadow under the body, offset
    2 px native down/right. Carried over from Round 3 — anchors Pip as
    a fallen weight at all sizes.
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
    given pixel size — used for the bottom detail row.
    """
    canvas = pygame.Surface((target_size, target_size), pygame.SRCALPHA)
    canvas.blit(_swatch_disc(target_size, BG_TEAL), (0, 0))

    # Draw glyph at SS=12 then smoothscale to ~70% of target size so it
    # reads BIG without bleeding off the swatch.
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
    """Top section — 5 frames of SURGICAL + VAPOR end colour at
    t = 0, 25, 50, 75, 100% showing the gradient lock.
    """
    cell_d = 130
    cell_gap = 18
    label_h = 30
    head_h = 60
    pad = 24
    n = 5
    inner_w = pad * 2 + cell_d * n + cell_gap * (n - 1)
    total_w = max(width, inner_w)
    total_h = head_h + pad + cell_d + 8 + label_h + pad

    sect = pygame.Surface((total_w, total_h), pygame.SRCALPHA)
    pygame.draw.rect(sect, SECTION_BG, sect.get_rect(), border_radius=14)
    pygame.draw.rect(sect, SECTION_EDGE, sect.get_rect(), width=2,
                     border_radius=14)

    head = _section_header(total_w - 24, head_h, "SECTION 1",
                           "GRADIENT TRANSITION",
                           "Body colour locks at the end colour and stays. "
                           "Example: SURGICAL X + VAPOR YELLOW-GREEN. "
                           "X fades in over the second half.")
    sect.blit(head, (12, 8))

    # Row of 5 cells.
    x = (total_w - inner_w) // 2 + pad
    y = head_h + pad
    ts = [0.0, 0.25, 0.5, 0.75, 1.0]
    for t in ts:
        cell = pygame.Surface((cell_d, cell_d + label_h + 6), pygame.SRCALPHA)
        swatch = _swatch_disc(cell_d, BG_TEAL)
        cell.blit(swatch, (0, 0))
        sprite = _render_at("vapor", "surgical", t, NATIVE_H)
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
    """4-col x 3-row exploration matrix — glyph style x end colour."""
    glyph_keys = ["surgical", "beveled", "neon", "bone"]
    end_keys = ["liquid", "vapor", "twotone"]

    cell_d = 130
    cell_gap = 22
    row_label_w = 184
    col_label_h = 34
    row_label_pad = 12
    head_h = 60
    pad = 22

    inner_w = row_label_w + cell_gap + (cell_d + cell_gap) * len(glyph_keys)
    inner_h = head_h + col_label_h + (cell_d + cell_gap) * len(end_keys)
    total_w = max(width, inner_w + pad * 2)
    total_h = inner_h + pad * 2

    sect = pygame.Surface((total_w, total_h), pygame.SRCALPHA)
    pygame.draw.rect(sect, SECTION_BG, sect.get_rect(), border_radius=14)
    pygame.draw.rect(sect, SECTION_EDGE, sect.get_rect(), width=2,
                     border_radius=14)

    head = _section_header(total_w - 24, head_h, "SECTION 2",
                           "EXPLORATION MATRIX",
                           "Rows = end-colour options.  "
                           "Cols = X-glyph styles.  All shown locked at t = 100%.")
    sect.blit(head, (12, 8))

    grid_x0 = (total_w - inner_w) // 2
    grid_y0 = head_h + pad

    # Column headers — slightly smaller font so the longest label
    # ("BEVELED / FACETED") clears its column without bleeding into
    # its neighbours.
    for ci, g in enumerate(glyph_keys):
        cx = grid_x0 + row_label_w + cell_gap + ci * (cell_d + cell_gap)
        lab = _font(13, bold=True).render(GLYPH_LABELS[g], True, LABEL_HEAD)
        sect.blit(lab, (cx + (cell_d - lab.get_width()) // 2,
                        grid_y0 + (col_label_h - lab.get_height()) // 2))

    # Rows.
    for ri, e in enumerate(end_keys):
        ry = grid_y0 + col_label_h + ri * (cell_d + cell_gap)
        # Row label box.
        row_rect = pygame.Rect(grid_x0, ry, row_label_w, cell_d)
        pygame.draw.rect(sect, PANEL_BG, row_rect, border_radius=10)
        pygame.draw.rect(sect, PANEL_EDGE, row_rect, width=1,
                         border_radius=10)
        # Multi-line row label.
        name_lab = _font(15, bold=True)
        if e == "liquid":
            head_str = "LIQUID GREEN"
            sub_str = "(120, 200, 90)"
            chip = LIQUID_GREEN
            chip_b = None
        elif e == "vapor":
            head_str = "VAPOR YELLOW-GREEN"
            sub_str = "(200, 224, 96)"
            chip = VAPOR_YGREEN
            chip_b = None
        else:
            head_str = "TWO-TONE"
            sub_str = "vapor body / liquid shadows"
            chip = VAPOR_YGREEN
            chip_b = LIQUID_GREEN

        head_surf = name_lab.render(head_str, True, LABEL_HI)
        sub_surf = _font(12).render(sub_str, True, LABEL_DIM)
        sect.blit(head_surf, (row_rect.x + 12, row_rect.y + 14))
        sect.blit(sub_surf, (row_rect.x + 12,
                             row_rect.y + 14 + head_surf.get_height() + 2))

        # Colour chip(s).
        chip_y = row_rect.y + 14 + head_surf.get_height() + sub_surf.get_height() + 12
        chip_w = 44
        chip_h = 22
        pygame.draw.rect(sect, chip, (row_rect.x + 12, chip_y, chip_w, chip_h),
                         border_radius=6)
        pygame.draw.rect(sect, (220, 220, 230),
                         (row_rect.x + 12, chip_y, chip_w, chip_h),
                         width=1, border_radius=6)
        if chip_b is not None:
            pygame.draw.rect(sect, chip_b,
                             (row_rect.x + 12 + chip_w + 6, chip_y,
                              chip_w, chip_h), border_radius=6)
            pygame.draw.rect(sect, (220, 220, 230),
                             (row_rect.x + 12 + chip_w + 6, chip_y,
                              chip_w, chip_h),
                             width=1, border_radius=6)

        for ci, g in enumerate(glyph_keys):
            cx = grid_x0 + row_label_w + cell_gap + ci * (cell_d + cell_gap)
            swatch = _swatch_disc(cell_d, BG_TEAL)
            sect.blit(swatch, (cx, ry))
            sprite = _render_at(e, g, 1.0, NATIVE_H)
            sx = cx + (cell_d - sprite.get_width()) // 2
            sy = ry + (cell_d - sprite.get_height()) // 2
            sect.blit(sprite, (sx, sy))

    return sect


def build_section_3_eye_details(width: int) -> pygame.Surface:
    """Bottom section — 4x big eye-glyph crops so each X style is
    legible without zooming into the matrix.
    """
    n = 4
    crop_size = 200
    crop_gap = 28
    label_h = 30
    head_h = 60
    pad = 22

    inner_w = pad * 2 + n * crop_size + (n - 1) * crop_gap
    total_w = max(width, inner_w)
    total_h = head_h + pad + crop_size + 6 + label_h + pad

    sect = pygame.Surface((total_w, total_h), pygame.SRCALPHA)
    pygame.draw.rect(sect, SECTION_BG, sect.get_rect(), border_radius=14)
    pygame.draw.rect(sect, SECTION_EDGE, sect.get_rect(), width=2,
                     border_radius=14)

    head = _section_header(total_w - 24, head_h, "SECTION 3",
                           "X-GLYPH DETAIL",
                           "Cropped to single eye region at ~200 px so each "
                           "X style reads on its own merits.")
    sect.blit(head, (12, 8))

    x = (total_w - inner_w) // 2 + pad
    y = head_h + pad
    for g in ("surgical", "beveled", "neon", "bone"):
        crop = _eye_crop_zoom(g, crop_size)
        sect.blit(crop, (x, y))
        lab = _font(15, bold=True).render(GLYPH_LABELS[g], True, LABEL_HEAD)
        sect.blit(lab, (x + (crop_size - lab.get_width()) // 2,
                        y + crop_size + 6))
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
    sec3 = build_section_3_eye_details(section_w)

    sheet_h = (title_h + sec1.get_height() + sec2.get_height()
               + sec3.get_height() + gutter * 4 + 20)
    sheet = pygame.Surface((sheet_w, sheet_h))

    # Background — soft vertical gradient from BG_TEAL into something
    # marginally darker so the section cards lift off the page.
    for y in range(sheet_h):
        tt = y / max(1, sheet_h - 1)
        col = (
            int(BG_TEAL[0] * (1 - tt * 0.30)),
            int(BG_TEAL[1] * (1 - tt * 0.25)),
            int(BG_TEAL[2] * (1 - tt * 0.18)),
        )
        pygame.draw.line(sheet, col, (0, y), (sheet_w, y))

    title_font = _font(36, bold=True)
    title = title_font.render(
        "DEAD PIP v2  —  Round 1  (cutting-edge X + gradient transition)",
        True, LABEL_HI)
    sheet.blit(title, ((sheet_w - title.get_width()) // 2, 24))
    sub_font = _font(16)
    sub = sub_font.render(
        "Two axes:  END COLOUR (3 options)  x  X-GLYPH STYLE (4 options). "
        "Gradient locks at the end colour and stays.",
        True, LABEL_DIM)
    sheet.blit(sub, ((sheet_w - sub.get_width()) // 2,
                     24 + title.get_height() + 6))

    y = title_h + gutter
    sheet.blit(sec1, ((sheet_w - sec1.get_width()) // 2, y))
    y += sec1.get_height() + gutter
    sheet.blit(sec2, ((sheet_w - sec2.get_width()) // 2, y))
    y += sec2.get_height() + gutter
    sheet.blit(sec3, ((sheet_w - sec3.get_width()) // 2, y))

    return sheet


if __name__ == "__main__":
    out_path = "/home/user/skybit/docs/dead_pip_v2/round_1.png"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    sheet = build_sheet()
    pygame.image.save(sheet, out_path)
    print(f"Saved {out_path} ({sheet.get_width()}x{sheet.get_height()})")
