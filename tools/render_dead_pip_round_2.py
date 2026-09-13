"""Round 2 of the dead-Pip design loop.

Round 1's verdict was ITERATE: every X glyph collapsed at 96 px because
the strokes were too thin, too dark against the dark head feathers, and
there was no eye-disc cavity underneath for the X to "cross out". This
round overhauls the X glyph — matte grey eye disc + 1 px dark outline +
pale-cream 2 px native X strokes — and threads that fix through every
remaining panel, drops Spiral, and adds two new panels: HEAVY-LID + X
(the universal "passed out" shorthand) and CONVERGENCE (the candidate
fusing cause + state + condition + pose).

All concepts paint on top of the real in-game parrot sprite, supersampled
~5x and smoothscaled down so strokes anti-alias cleanly at 96 px native
AND at the 4x zoom column. Pure-pygame — no numpy.
"""

import math
import os
import sys

# Headless run — pygbag isn't involved; we just want to save a PNG.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

sys.path.insert(0, "/home/user/skybit")

import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((1, 1))

from game import parrot  # noqa: E402

# ── palette ──────────────────────────────────────────────────────────────────
BG_TEAL     = (38, 44, 66)
PANEL_BG    = (24, 28, 42)
PANEL_EDGE  = (58, 70, 100)
LABEL_HI    = (245, 235, 210)
LABEL_DIM   = (170, 180, 210)
TAG_BG      = (58, 38, 50)
TAG_HI      = (255, 210, 90)

# New round-2 dead-eye palette per the critique.
EYE_DISC      = (70, 70, 75)        # matte grey, no white, no glint
EYE_OUTLINE   = (15, 15, 22)        # crisp dark socket rim
X_CREAM       = (245, 235, 215)     # pale cream X — survives over dark head feathers
LID_INK       = (30, 30, 35)        # heavy-lid eyelid stroke

# Tongue — desaturated soft flesh per directive C.
TONGUE_BASE = (195, 130, 140)
TONGUE_DARK = (110,  55,  70)

# Vapor — kept the round-1 hue, but now outlined for legibility over orange tail.
VAPOR_GREEN     = (200, 224,  96)
VAPOR_DEEP      = (140, 180,  50)
VAPOR_OUTLINE   = ( 40,  60,  20)

# Lens centres in sprite-pixel coordinates (see game/parrot.py:71-104).
LEFT_LENS  = (50 - 4, 20)
RIGHT_LENS = (50 + 6, 20 - 1)

SPRITE_W, SPRITE_H = parrot.SPRITE_W, parrot.SPRITE_H

# Supersample factor for the dead-overlay layer.
SS = 5

# Display dimensions for the previews (native + 4x zoom side by side).
NATIVE_H = 96
ZOOM_FACTOR = 4
ZOOM_H = NATIVE_H * ZOOM_FACTOR


# ── helpers ──────────────────────────────────────────────────────────────────

def _font(size: int, bold: bool = False) -> pygame.font.Font:
    return pygame.font.SysFont("dejavusans", size, bold=bold)


def _draw_dead_eye_glyph(surf: pygame.Surface, center: tuple[float, float],
                         scale: float, *, lid: bool = False) -> None:
    """Round-2 eye glyph: matte grey eye disc + 1 px dark outline + pale
    cream X. Disc radius 5 px native, X strokes 2 px native, bounding box
    ~10x10 px native so each leg of the X extends ~2 px past the disc.

    If `lid=True`, draws a thick dark eyelid chord across the TOP THIRD
    of the disc and vertically biases the X downward so it sits in the
    visible lower 2/3 of the disc (Panel B "Heavy-lid + X").
    """
    cx, cy = center
    disc_r_native = 5.0
    outline_thick_native = 1.0
    x_leg_native = 5.0           # half the ~10x10 bounding box
    x_thick_native = 2.0
    lid_chord_w_native = 5.0     # ~ disc diameter
    lid_thick_native = 1.6
    lid_y_offset_native = -2.5   # chord sits across the top third of the disc

    disc_r = disc_r_native * scale
    out_thick = max(1.0, outline_thick_native * scale)
    x_leg = x_leg_native * scale
    x_thick = x_thick_native * scale

    # 1) Dark socket outline ring (a slightly larger filled disc) — gives
    #    the eye disc a defined cavity edge that survives the downscale.
    pygame.draw.circle(surf, EYE_OUTLINE, (int(cx), int(cy)),
                       int(disc_r + out_thick))
    # 2) Matte grey eye disc — flat, no glint, no white.
    pygame.draw.circle(surf, EYE_DISC, (int(cx), int(cy)), int(disc_r))

    # 3) Optional heavy lid (Panel B) — chord across the top portion of
    #    the disc, drawn AFTER the disc and BEFORE the X so the X reads
    #    on top of it.
    if lid:
        lid_y = cy + lid_y_offset_native * scale
        half_w = (lid_chord_w_native * 0.5) * scale
        pygame.draw.line(surf, LID_INK,
                         (cx - half_w, lid_y),
                         (cx + half_w, lid_y),
                         max(1, int(lid_thick_native * scale)))
        # Slight droop curve below the chord to sell the closed-lid arc.
        droop_y = lid_y + 0.9 * scale
        pygame.draw.line(surf, LID_INK,
                         (cx - half_w * 0.7, droop_y),
                         (cx + half_w * 0.7, droop_y),
                         max(1, int(0.8 * scale)))

    # 4) Cream X — two diagonal strokes. When lid is on, bias the X
    #    downward so it sits in the visible lower 2/3 of the disc.
    x_cy = cy + (1.4 * scale if lid else 0.0)
    for ang_deg in (45 + 8, -45 + 8):
        a = math.radians(ang_deg)
        dx = math.cos(a) * x_leg
        dy = math.sin(a) * (x_leg if not lid else x_leg * 0.78)
        p1 = (cx - dx, x_cy - dy)
        p2 = (cx + dx, x_cy + dy)
        pygame.draw.line(surf, X_CREAM, p1, p2, max(1, int(x_thick)))


def _draw_dead_eyes(surf: pygame.Surface, scale: float,
                    offset: tuple[int, int], *, lid: bool = False) -> None:
    """Stamp the round-2 dead-eye glyph at both lens centres."""
    for centre in (LEFT_LENS, RIGHT_LENS):
        c = _sprite_to_canvas(centre, offset, scale)
        _draw_dead_eye_glyph(surf, c, scale, lid=lid)


def _draw_tongue(surf: pygame.Surface, anchor: tuple[float, float],
                 length_native: float, width_native: float,
                 scale: float) -> None:
    """Desaturated-pink limp tongue per directive C. Soft flesh, NOT hot
    pink. 2 px native wide / ~8 px native long, hanging straight down
    from the beak slot with a small darker outline so it clears the
    beak silhouette."""
    ax, ay = anchor
    length = length_native * scale
    width = width_native * scale

    # Outer dark silhouette (the "outline so it clears the beak").
    pts_outer = [
        (ax - width * 0.65, ay - 0.6 * scale),
        (ax + width * 0.65, ay - 0.6 * scale),
        (ax + width * 0.55, ay + length * 0.88),
        (ax,                 ay + length),
        (ax - width * 0.55, ay + length * 0.88),
    ]
    pygame.draw.polygon(surf, TONGUE_DARK, pts_outer)
    # Inner fill — slightly narrower so dark silhouette reads as outline
    pts_in = [
        (ax - width * 0.45, ay),
        (ax + width * 0.45, ay),
        (ax + width * 0.38, ay + length * 0.82),
        (ax,                 ay + length - 0.8 * scale),
        (ax - width * 0.38, ay + length * 0.82),
    ]
    pygame.draw.polygon(surf, TONGUE_BASE, pts_in)


def _draw_vapor_ribbon(surf: pygame.Surface, base: tuple[float, float],
                       scale: float, *, x_drift_native: float,
                       phase: float, height_native: float) -> None:
    """A single chubby ribbon curl rising from `base`, with a 1 px dark
    outline so it survives over the orange tail AND the dawn-teal sky.
    Stack of soft discs with alpha falloff plus a horizontal sine drift.

    `phase` shifts the sine wave start so multiple curls don't trace the
    same path. `height_native` is the total ribbon height in native px.
    """
    bx, by = base
    layers = 9
    for i in range(layers):
        t = i / (layers - 1)
        # Sine drift with phase offset.
        dx = math.sin((t + phase) * math.pi * 1.6) * x_drift_native * scale
        cx = bx + dx
        cy = by - t * height_native * scale
        # Slight bulge in the middle, taper at the top.
        r_native = (1.0 - 0.55 * t) * 2.2
        r = r_native * scale
        col_core = (
            int(VAPOR_GREEN[0] * (1 - t) + VAPOR_DEEP[0] * t),
            int(VAPOR_GREEN[1] * (1 - t) + VAPOR_DEEP[1] * t),
            int(VAPOR_GREEN[2] * (1 - t) + VAPOR_DEEP[2] * t),
            int(245 * (1.0 - t * 0.55)),
        )
        outline_alpha = int(220 * (1.0 - t * 0.5))
        disc = pygame.Surface((int(r * 2 + 6), int(r * 2 + 6)), pygame.SRCALPHA)
        cc = (int(r + 3), int(r + 3))
        # 1 px native outline ring.
        pygame.draw.circle(disc, (*VAPOR_OUTLINE, outline_alpha), cc,
                           int(r + max(1.0, 1.0 * scale)))
        pygame.draw.circle(disc, col_core, cc, int(r))
        surf.blit(disc, (cx - r - 3, cy - r - 3))


def _draw_triple_vapor(surf: pygame.Surface, scale: float,
                       offset: tuple[int, int]) -> None:
    """3 distinct ribbon curls rising from the beak tip, ~12 px tall
    native overall, per directive D. Phase offsets fan them out so each
    reads as its own curl rather than blurring into a single wisp."""
    base = _sprite_to_canvas((60.5, 22.0), offset, scale)
    bx, by = base
    # Three curl emitters fanned slightly across the beak tip.
    for i, (ox, phase, h, drift) in enumerate((
            (-1.6, 0.0,  11.5, 2.0),
            ( 0.0, 0.4,  13.0, 2.4),
            ( 1.6, 0.8,  10.5, 1.7),
    )):
        _draw_vapor_ribbon(
            surf,
            (bx + ox * scale, by),
            scale,
            x_drift_native=drift,
            phase=phase,
            height_native=h,
        )


# ── body-region recolour utilities (no numpy) ────────────────────────────────

def _body_pixel_mask(sprite: pygame.Surface) -> set[tuple[int, int]]:
    """Return the set of (x, y) sprite-pixel coords whose colour reads as
    a "body green/red" pixel — i.e. the warm-red body / head feathers,
    excluding the cool-blue wing AND the orange-yellow tail. Used by
    directives D + F so the chartreuse tint hits only the body, not the
    tail/wing identity colours."""
    w, h = sprite.get_size()
    keep: set[tuple[int, int]] = set()
    sprite.lock()
    try:
        for y in range(h):
            for x in range(w):
                r, g, b, a = sprite.get_at((x, y))
                if a == 0:
                    continue
                # Warm reddish-pink head/body pixels: red dominant,
                # not the orange-yellow tail (which has high green AND
                # is in the lower-left tail region), and not blue wing.
                if r > b + 20 and r > g + 5 and not (g > 140 and b < 90 and x < 24 and y > 24):
                    keep.add((x, y))
        # Hard-mask out the tail region (sprite x<22, y>=24) to keep tail
        # untinted regardless of colour heuristic.
        keep = {(x, y) for (x, y) in keep if not (x < 24 and y >= 24)}
        # Hard-mask out the wing region (sprite x in 10..50, y in 8..28)
        # where the cool-blue wing sits in FRAMES[2/3].
        keep = {(x, y) for (x, y) in keep if not (10 <= x <= 50 and 8 <= y <= 28 and (
            # Blue-dominant wing pixel test
            sprite.get_at((x, y))[2] > sprite.get_at((x, y))[0] + 10
        ))}
    finally:
        sprite.unlock()
    return keep


def _body_pixel_mask_canvas(big: pygame.Surface, scale: float,
                            offset: tuple[int, int]) -> None:
    """Unused helper placeholder — kept inline-tinting path lives in
    `_tint_body_region` which operates directly on the SS canvas."""
    raise NotImplementedError


def _tint_body_region(big: pygame.Surface, factors: tuple[float, float, float],
                      desat: float, scale: float,
                      offset: tuple[int, int]) -> None:
    """Apply per-channel multiplication AND desaturation to body-region
    pixels of the supersampled canvas, leaving tail + wing alone.

    Body region is approximated as the union of head circle + body
    ellipse from `parrot._build_frame`:
      - body ellipse  centred at sprite (32, 32), radii (19, 14)
      - head ellipse  centred at sprite (47, 21), radii (12, 11)
    Both mapped to canvas coords. Pure-pygame pixel walk on just the
    masked region (cheap enough for the 64x60 * SS=5 sprite).
    """
    body_cx_s, body_cy_s = _sprite_to_canvas((32, 32), offset, scale)
    head_cx_s, head_cy_s = _sprite_to_canvas((47, 21), offset, scale)
    body_rx, body_ry = 19 * scale, 14 * scale
    head_rx, head_ry = 12 * scale, 11 * scale

    fr, fg, fb = factors
    big.lock()
    try:
        w, h = big.get_size()
        # Iterate only the bounding box that contains either ellipse.
        x0 = int(max(0, min(body_cx_s - body_rx, head_cx_s - head_rx)))
        x1 = int(min(w, max(body_cx_s + body_rx, head_cx_s + head_rx)) + 1)
        y0 = int(max(0, min(body_cy_s - body_ry, head_cy_s - head_ry)))
        y1 = int(min(h, max(body_cy_s + body_ry, head_cy_s + head_ry)) + 1)
        for y in range(y0, y1):
            for x in range(x0, x1):
                # Point-in-ellipse for body or head.
                in_body = ((x - body_cx_s) ** 2) / (body_rx ** 2) + \
                          ((y - body_cy_s) ** 2) / (body_ry ** 2) <= 1.0
                in_head = ((x - head_cx_s) ** 2) / (head_rx ** 2) + \
                          ((y - head_cy_s) ** 2) / (head_ry ** 2) <= 1.0
                if not (in_body or in_head):
                    continue
                r, g, b, a = big.get_at((x, y))
                if a == 0:
                    continue
                # Skip pixels that are clearly the cool-blue wing — the wing
                # sits on top of the body ellipse and we don't want to
                # tint it. Wing pixels have blue > red.
                if b > r + 10:
                    continue
                nr = min(255, max(0, int(r * fr)))
                ng = min(255, max(0, int(g * fg)))
                nb = min(255, max(0, int(b * fb)))
                if desat > 0.0:
                    lum = 0.299 * nr + 0.587 * ng + 0.114 * nb
                    k = 1.0 - desat
                    nr = int(nr * k + lum * desat)
                    ng = int(ng * k + lum * desat)
                    nb = int(nb * k + lum * desat)
                big.set_at((x, y), (nr, ng, nb, a))
    finally:
        big.unlock()


def _desaturate_body_only(big: pygame.Surface, amount: float, scale: float,
                          offset: tuple[int, int]) -> None:
    """Directive E: desaturate ONLY the green body, leave wing + tail
    at full saturation. We piggy-back on `_tint_body_region` with
    identity factors and the requested desat amount."""
    _tint_body_region(big, (1.0, 1.0, 1.0), amount, scale, offset)


# ── base sprite assembly ─────────────────────────────────────────────────────

def _base_frame(frame_idx: int = 2) -> pygame.Surface:
    """Pull the real in-game parrot frame so concepts are judged against
    the actual silhouette."""
    return parrot.FRAMES[frame_idx].copy()


def _supersample_canvas(base: pygame.Surface) -> tuple[pygame.Surface, float, tuple[int, int]]:
    """Upscale the base sprite by SS so we have plenty of room to paint
    smooth dead-overlay details on top."""
    w, h = base.get_size()
    big = pygame.transform.smoothscale(base, (w * SS, h * SS))
    return big, SS, (0, 0)


def _sprite_to_canvas(p: tuple[float, float],
                      offset: tuple[int, int],
                      scale: float,
                      outline_pad: int = 2) -> tuple[float, float]:
    """Map sprite-pixel coordinate (un-padded 64x60 frame) onto the
    supersampled canvas. `parrot._add_outline` pads by 2 px every side."""
    return ((p[0] + outline_pad + offset[0]) * scale,
            (p[1] + outline_pad + offset[1]) * scale)


# ── concept overlays ─────────────────────────────────────────────────────────

def concept_a_classic_x(big: pygame.Surface, scale: float,
                        offset: tuple[int, int]) -> pygame.Surface:
    """A. Classic X-eyes (round-2 overhaul). Eye disc + outline + cream X."""
    _draw_dead_eyes(big, scale, offset, lid=False)
    return big


def concept_b_heavy_lid(big: pygame.Surface, scale: float,
                        offset: tuple[int, int]) -> pygame.Surface:
    """B. Heavy-lid + X (NEW, replaces Spiral). Universal cartoon
    passed-out / dead shorthand: half-closed dead lid + X on the
    visible lower 2/3 of the eye disc."""
    _draw_dead_eyes(big, scale, offset, lid=True)
    return big


def concept_c_x_plus_tongue(big: pygame.Surface, scale: float,
                            offset: tuple[int, int]) -> pygame.Surface:
    """C. X-eyes plus desaturated limp tongue."""
    _draw_dead_eyes(big, scale, offset, lid=False)
    anchor = _sprite_to_canvas((55.5, 26.0), offset, scale)
    _draw_tongue(big, anchor, length_native=8.0, width_native=2.0, scale=scale)
    return big


def concept_d_poisoned(big: pygame.Surface, scale: float,
                       offset: tuple[int, int]) -> pygame.Surface:
    """D. X-eyes + chartreuse body-only tint + 3-curl outlined vapor."""
    # Body tint shifted toward yellow-green (chartreuse), with mild
    # desaturation so the bird reads "sick" not "vivid green Ghost cyan."
    _tint_body_region(big, (0.85, 1.0, 0.50), desat=0.20,
                      scale=scale, offset=offset)
    _draw_dead_eyes(big, scale, offset, lid=False)
    _draw_triple_vapor(big, scale, offset)
    return big


def concept_e_full_dead(scale: float,
                        offset: tuple[int, int]) -> pygame.Surface:
    """E. Full dead-pose. Drooping wings (FRAMES[3]), body-only
    desaturation, ~20 deg back-tilt, X-eyes, limp tongue."""
    base = parrot.FRAMES[3].copy()
    big, _, _ = _supersample_canvas(base)
    # Body-region desaturate only — wing + tail keep full saturation.
    _desaturate_body_only(big, amount=0.45, scale=scale, offset=offset)
    _draw_dead_eyes(big, scale, offset, lid=False)
    anchor = _sprite_to_canvas((55.5, 26.0), offset, scale)
    _draw_tongue(big, anchor, length_native=8.0, width_native=2.0, scale=scale)
    big = pygame.transform.rotozoom(big, 20.0, 1.0)
    return big


def concept_f_convergence(scale: float,
                          offset: tuple[int, int]) -> pygame.Surface:
    """F. CONVERGENCE (NEW). D's chartreuse body tint + 3-curl vapor,
    E's wing-droop + a more restrained ~10 deg head tilt back, A-style
    X-eye glyph, C's limp tongue. Cause + state + condition + pose."""
    base = parrot.FRAMES[3].copy()
    big, _, _ = _supersample_canvas(base)
    # D's chartreuse body-only tint with desat.
    _tint_body_region(big, (0.85, 1.0, 0.50), desat=0.20,
                      scale=scale, offset=offset)
    # A's dead-eye glyph.
    _draw_dead_eyes(big, scale, offset, lid=False)
    # C's tongue.
    anchor = _sprite_to_canvas((55.5, 26.0), offset, scale)
    _draw_tongue(big, anchor, length_native=8.0, width_native=2.0, scale=scale)
    # D's triple vapor curl.
    _draw_triple_vapor(big, scale, offset)
    # Restrained back-tilt — half of E's so Pip stays recognisable.
    big = pygame.transform.rotozoom(big, 10.0, 1.0)
    return big


# ── panel renderer ───────────────────────────────────────────────────────────

def _render_concept_native(concept_fn) -> pygame.Surface:
    """Run a concept builder and smoothscale to NATIVE_H height. This is
    the preview that MUST be judged — every X overhaul lives or dies here."""
    if concept_fn in (concept_e_full_dead, concept_f_convergence):
        big = concept_fn(SS, (0, 0))
    else:
        base = _base_frame(2)
        big, _, _ = _supersample_canvas(base)
        concept_fn(big, SS, (0, 0))
    bw, bh = big.get_size()
    target_w = int(bw * (NATIVE_H / bh))
    return pygame.transform.smoothscale(big, (target_w, NATIVE_H))


def _render_concept_zoom(concept_fn) -> pygame.Surface:
    """Same concept, scaled to 4x zoom target."""
    if concept_fn in (concept_e_full_dead, concept_f_convergence):
        big = concept_fn(SS, (0, 0))
    else:
        base = _base_frame(2)
        big, _, _ = _supersample_canvas(base)
        concept_fn(big, SS, (0, 0))
    bw, bh = big.get_size()
    target_w = int(bw * (ZOOM_H / bh))
    return pygame.transform.smoothscale(big, (target_w, ZOOM_H))


def _swatch_disc(diameter: int, color, ring_color=(70, 90, 130)) -> pygame.Surface:
    """Soft round swatch background — sells the dawn-teal sky color
    behind each native preview without dominating the panel."""
    surf = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
    r = diameter // 2
    pygame.draw.circle(surf, ring_color, (r, r), r)
    for i in range(r - 2, 0, -1):
        t = 1.0 - (i / (r - 2))
        col = (
            int(color[0] * (0.78 + 0.22 * (1 - t))),
            int(color[1] * (0.78 + 0.22 * (1 - t))),
            int(color[2] * (0.78 + 0.22 * (1 - t))),
        )
        pygame.draw.circle(surf, col, (r, r), i)
    return surf


def _panel(tag: str, headline: str, note: str,
           concept_fn, panel_size: tuple[int, int],
           bob_offset_px: int = 2) -> pygame.Surface:
    pw, ph = panel_size
    surf = pygame.Surface((pw, ph), pygame.SRCALPHA)
    pygame.draw.rect(surf, PANEL_BG, surf.get_rect(), border_radius=14)
    pygame.draw.rect(surf, PANEL_EDGE, surf.get_rect(), width=2, border_radius=14)

    tag_h = 36
    tag_rect = pygame.Rect(12, 10, pw - 24, tag_h)
    pygame.draw.rect(surf, TAG_BG, tag_rect, border_radius=10)
    tag_surf = _font(20, bold=True).render(tag, True, TAG_HI)
    head_surf = _font(18, bold=False).render(headline, True, LABEL_HI)
    surf.blit(tag_surf, (tag_rect.x + 12, tag_rect.y + (tag_h - tag_surf.get_height()) // 2))
    surf.blit(head_surf, (tag_rect.x + 12 + tag_surf.get_width() + 14,
                          tag_rect.y + (tag_h - head_surf.get_height()) // 2 + 1))

    # Native preview on the left, on a swatch disc
    swatch_d = 140
    swatch = _swatch_disc(swatch_d, BG_TEAL)
    swatch_x = 18
    swatch_y = tag_rect.bottom + 14
    surf.blit(swatch, (swatch_x, swatch_y))
    native = _render_concept_native(concept_fn)
    nx = swatch_x + (swatch_d - native.get_width()) // 2
    ny = swatch_y + (swatch_d - native.get_height()) // 2 + bob_offset_px
    surf.blit(native, (nx, ny))
    size_lab = _font(13).render("96 px native", True, LABEL_DIM)
    surf.blit(size_lab, (swatch_x + (swatch_d - size_lab.get_width()) // 2,
                         swatch_y + swatch_d + 6))

    # 4x zoom preview on the right, on the teal background directly
    zoom_x = swatch_x + swatch_d + 24
    zoom_y = swatch_y - 10
    zoom_rect = pygame.Rect(zoom_x, zoom_y, ZOOM_H + 16, ZOOM_H + 16)
    pygame.draw.rect(surf, BG_TEAL, zoom_rect, border_radius=10)
    pygame.draw.rect(surf, PANEL_EDGE, zoom_rect, width=1, border_radius=10)
    zoom = _render_concept_zoom(concept_fn)
    zx = zoom_x + (zoom_rect.w - zoom.get_width()) // 2
    zy = zoom_y + (zoom_rect.h - zoom.get_height()) // 2 + bob_offset_px * ZOOM_FACTOR
    surf.blit(zoom, (zx, zy))
    zoom_lab = _font(13).render("4x zoom (384 px)", True, LABEL_DIM)
    surf.blit(zoom_lab, (zoom_x + (zoom_rect.w - zoom_lab.get_width()) // 2,
                         zoom_rect.bottom + 6))

    note_y = max(swatch_y + swatch_d + 26, zoom_rect.bottom + 26)
    note_surf = _font(15).render(note, True, LABEL_DIM)
    surf.blit(note_surf, (18, note_y))
    return surf


def build_sheet() -> pygame.Surface:
    """Vertical stack of 6 panels with a title bar at the top."""
    panel_w = 920
    panel_h = 470
    gutter = 22
    title_h = 92
    sheet_w = panel_w + 60
    sheet_h = title_h + 6 * panel_h + 7 * gutter + 30

    sheet = pygame.Surface((sheet_w, sheet_h))
    for y in range(sheet_h):
        t = y / max(1, sheet_h - 1)
        col = (
            int(BG_TEAL[0] * (1 - t * 0.25)),
            int(BG_TEAL[1] * (1 - t * 0.20)),
            int(BG_TEAL[2] * (1 - t * 0.15)),
        )
        pygame.draw.line(sheet, col, (0, y), (sheet_w, y))

    title_font = _font(36, bold=True)
    title = title_font.render("DEAD PIP  —  Round 2  (after critique)", True, LABEL_HI)
    sheet.blit(title, ((sheet_w - title.get_width()) // 2, 24))
    sub_font = _font(16)
    sub = sub_font.render(
        "Overhauled X glyph (matte grey eye disc + 1 px dark outline + 2 px cream X). "
        "Spiral dropped. New: Heavy-Lid (B) + Convergence (F).",
        True, LABEL_DIM,
    )
    sheet.blit(sub, ((sheet_w - sub.get_width()) // 2, 24 + title.get_height() + 6))

    concepts = [
        ("A.", "CLASSIC X-EYES",
         "Matte grey eye disc (r=5 px) + 1 px dark outline + 2 px cream X. Pose + body unchanged.",
         concept_a_classic_x),
        ("B.", "HEAVY-LID + X",
         "Universal passed-out shorthand: dark eyelid chord across top of disc, X biased into the lower 2/3.",
         concept_b_heavy_lid),
        ("C.", "X + LIMP TONGUE",
         "Round-2 X-glyph + 2 px desaturated-pink tongue (NOT hot pink), ~8 px long, with dark outline.",
         concept_c_x_plus_tongue),
        ("D.", "POISONED",
         "Chartreuse body-only tint (tail untouched) + 3 outlined vapor curls ~12 px tall over the beak.",
         concept_d_poisoned),
        ("E.", "FULL DEAD-POSE",
         "Drooping wings + body-only desaturation (wing+tail full saturation) + 20 deg head-back tilt.",
         concept_e_full_dead),
        ("F.", "CONVERGENCE",
         "D-tint + 3-curl vapor + droop + restrained 10 deg tilt + X-eyes + tongue. Cause+state+condition+pose.",
         concept_f_convergence),
    ]

    y = title_h + 16
    for tag, head, note, fn in concepts:
        p = _panel(tag, head, note, fn, (panel_w, panel_h))
        sheet.blit(p, ((sheet_w - panel_w) // 2, y))
        y += panel_h + gutter

    return sheet


if __name__ == "__main__":
    out_path = "/home/user/skybit/docs/dead_pip/round_2.png"
    sheet = build_sheet()
    pygame.image.save(sheet, out_path)
    print(f"Saved {out_path} ({sheet.get_width()}x{sheet.get_height()})")
