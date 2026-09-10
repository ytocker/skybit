"""Round 3 (final) of the dead-Pip design loop.

Round 2's verdict was ITERATE with sharp final directives. The X glyph
worked but overshot the socket ring; the heavy-lid concept fought the
glyph; the tongue dominated at 96 px; the 20 deg tilt read "thrown,"
not limp; the chartreuse tint competed with the X for attention. This
round collapses to 4 finalists, tightens the X, adds a 1 px dark drop
shadow under every body so Pip reads as a fallen weight, and presents
a clean trio (glyph-only / pose-only-plus-glyph / full-pose-plus-glyph)
alongside the convergence option.

Pure-pygame, no numpy. Same 5x supersample + smoothscale-down pipeline
so every stroke anti-aliases cleanly at 96 px native AND 4x zoom.
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

# Dead-eye palette carried over from Round 2 (only X stroke length changes).
EYE_DISC      = (70, 70, 75)        # matte grey, no white, no glint
EYE_OUTLINE   = (15, 15, 22)        # crisp dark socket rim
X_CREAM       = (245, 235, 215)     # pale cream X — survives over dark feathers

# Vapor (F only) — kept the Round 2 hue + outline approach.
VAPOR_GREEN     = (200, 224,  96)
VAPOR_DEEP      = (140, 180,  50)
VAPOR_OUTLINE   = ( 40,  60,  20)

# Drop-shadow ink — universal "fallen weight" anchor under every panel.
SHADOW_INK      = (15, 18, 28)
SHADOW_ALPHA    = 120

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
                         scale: float) -> None:
    """TIGHTENED Round-3 eye glyph: matte grey disc + 1 px dark outline +
    pale cream X. Stroke length shortened by 1 px native so each leg of
    the X sits JUST INSIDE the socket ring rather than overshooting.
    Bounding box ~8x8 px native (was ~10x10) — the X no longer reads
    pasted on.
    """
    cx, cy = center
    disc_r_native = 5.0
    outline_thick_native = 1.0
    # Round-2 was 5.0 — Round-3 directive: 1 px shorter so legs sit
    # inside the outlined disc rim instead of overshooting it.
    x_leg_native = 4.0
    x_thick_native = 2.0

    disc_r = disc_r_native * scale
    out_thick = max(1.0, outline_thick_native * scale)
    x_leg = x_leg_native * scale
    x_thick = x_thick_native * scale

    # Dark socket outline ring (a slightly larger filled disc) — defined
    # cavity edge that survives the downscale.
    pygame.draw.circle(surf, EYE_OUTLINE, (int(cx), int(cy)),
                       int(disc_r + out_thick))
    pygame.draw.circle(surf, EYE_DISC, (int(cx), int(cy)), int(disc_r))

    # Cream X — two diagonal strokes. Slight 8 deg tilt carried from
    # Round 2 keeps the X from reading as a perfect "+ rotated 45".
    for ang_deg in (45 + 8, -45 + 8):
        a = math.radians(ang_deg)
        dx = math.cos(a) * x_leg
        dy = math.sin(a) * x_leg
        p1 = (cx - dx, cy - dy)
        p2 = (cx + dx, cy + dy)
        pygame.draw.line(surf, X_CREAM, p1, p2, max(1, int(x_thick)))


def _draw_dead_eyes(surf: pygame.Surface, scale: float,
                    offset: tuple[int, int]) -> None:
    """Stamp the tightened dead-eye glyph at both lens centres."""
    for centre in (LEFT_LENS, RIGHT_LENS):
        c = _sprite_to_canvas(centre, offset, scale)
        _draw_dead_eye_glyph(surf, c, scale)


def _draw_vapor_ribbon(surf: pygame.Surface, base: tuple[float, float],
                       scale: float, *, x_drift_native: float,
                       phase: float, height_native: float) -> None:
    """One ribbon curl, stack of soft outlined discs with alpha falloff."""
    bx, by = base
    layers = 9
    for i in range(layers):
        t = i / (layers - 1)
        dx = math.sin((t + phase) * math.pi * 1.6) * x_drift_native * scale
        cx = bx + dx
        cy = by - t * height_native * scale
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
        pygame.draw.circle(disc, (*VAPOR_OUTLINE, outline_alpha), cc,
                           int(r + max(1.0, 1.0 * scale)))
        pygame.draw.circle(disc, col_core, cc, int(r))
        surf.blit(disc, (cx - r - 3, cy - r - 3))


def _draw_double_vapor(surf: pygame.Surface, scale: float,
                       offset: tuple[int, int]) -> None:
    """2 curls (was 3 in Round 2) — directive: vapor must not compete
    with the X for attention in the convergence panel."""
    base = _sprite_to_canvas((60.5, 22.0), offset, scale)
    bx, by = base
    for ox, phase, h, drift in (
            (-1.4, 0.0,  12.0, 2.2),
            ( 1.4, 0.5,  11.0, 1.9),
    ):
        _draw_vapor_ribbon(
            surf,
            (bx + ox * scale, by),
            scale,
            x_drift_native=drift,
            phase=phase,
            height_native=h,
        )


# ── body-region recolour utilities (no numpy) ────────────────────────────────

def _tint_body_region(big: pygame.Surface, factors: tuple[float, float, float],
                      desat: float, scale: float,
                      offset: tuple[int, int]) -> None:
    """Per-channel multiplication + desat on body-region pixels of the
    supersampled canvas (tail + wing untouched). Body region approximated
    as the union of head circle + body ellipse from `parrot._build_frame`.
    """
    body_cx_s, body_cy_s = _sprite_to_canvas((32, 32), offset, scale)
    head_cx_s, head_cy_s = _sprite_to_canvas((47, 21), offset, scale)
    body_rx, body_ry = 19 * scale, 14 * scale
    head_rx, head_ry = 12 * scale, 11 * scale

    fr, fg, fb = factors
    big.lock()
    try:
        w, h = big.get_size()
        x0 = int(max(0, min(body_cx_s - body_rx, head_cx_s - head_rx)))
        x1 = int(min(w, max(body_cx_s + body_rx, head_cx_s + head_rx)) + 1)
        y0 = int(max(0, min(body_cy_s - body_ry, head_cy_s - head_ry)))
        y1 = int(min(h, max(body_cy_s + body_ry, head_cy_s + head_ry)) + 1)
        for y in range(y0, y1):
            for x in range(x0, x1):
                in_body = ((x - body_cx_s) ** 2) / (body_rx ** 2) + \
                          ((y - body_cy_s) ** 2) / (body_ry ** 2) <= 1.0
                in_head = ((x - head_cx_s) ** 2) / (head_rx ** 2) + \
                          ((y - head_cy_s) ** 2) / (head_ry ** 2) <= 1.0
                if not (in_body or in_head):
                    continue
                r, g, b, a = big.get_at((x, y))
                if a == 0:
                    continue
                # Skip the cool-blue wing — wing has blue dominant.
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
    """E: desat body, leave wing + tail at full saturation."""
    _tint_body_region(big, (1.0, 1.0, 1.0), amount, scale, offset)


# ── base sprite assembly ─────────────────────────────────────────────────────

def _base_frame(frame_idx: int) -> pygame.Surface:
    """Pull the real in-game parrot frame so concepts are judged against
    the actual silhouette."""
    return parrot.FRAMES[frame_idx].copy()


def _supersample_canvas(base: pygame.Surface) -> tuple[pygame.Surface, float, tuple[int, int]]:
    w, h = base.get_size()
    big = pygame.transform.smoothscale(base, (w * SS, h * SS))
    return big, SS, (0, 0)


def _sprite_to_canvas(p: tuple[float, float],
                      offset: tuple[int, int],
                      scale: float,
                      outline_pad: int = 2) -> tuple[float, float]:
    return ((p[0] + outline_pad + offset[0]) * scale,
            (p[1] + outline_pad + offset[1]) * scale)


# ── concept overlays ─────────────────────────────────────────────────────────

def concept_a_classic_x(big: pygame.Surface, scale: float,
                        offset: tuple[int, int]) -> pygame.Surface:
    """A. Classic X-eyes (tightened). FRAMES[2], no pose change."""
    _draw_dead_eyes(big, scale, offset)
    return big


def concept_b_soft(scale: float,
                   offset: tuple[int, int]) -> pygame.Surface:
    """B' SOFT. Pose-only-plus-glyph: 8 deg back-tilt, FRAMES[3] droop
    wings, no tint, no tongue, no vapor. Just the tightened X."""
    base = parrot.FRAMES[3].copy()
    big, _, _ = _supersample_canvas(base)
    _draw_dead_eyes(big, scale, offset)
    big = pygame.transform.rotozoom(big, 8.0, 1.0)
    return big


def concept_e_full_dead(scale: float,
                        offset: tuple[int, int]) -> pygame.Surface:
    """E. Full dead-pose (cleanup). Drooping wings (FRAMES[3]), body-only
    desaturation, 14 deg back-tilt (was 20 — too "thrown"), tightened X.
    Tongue dropped — dominated the silhouette at 96 px.
    """
    base = parrot.FRAMES[3].copy()
    big, _, _ = _supersample_canvas(base)
    _desaturate_body_only(big, amount=0.45, scale=scale, offset=offset)
    _draw_dead_eyes(big, scale, offset)
    big = pygame.transform.rotozoom(big, 14.0, 1.0)
    return big


def concept_f_convergence(scale: float,
                          offset: tuple[int, int]) -> pygame.Surface:
    """F. CONVERGENCE (restrained). Chartreuse body-only tint with EXTRA
    25% luma-pull desat so it doesn't compete with the X. 2 curls (was
    3). Droop wings, restrained 10 deg tilt, tightened X. Tongue dropped.
    """
    base = parrot.FRAMES[3].copy()
    big, _, _ = _supersample_canvas(base)
    # Tint multiply first…
    _tint_body_region(big, (0.85, 1.0, 0.50), desat=0.0,
                      scale=scale, offset=offset)
    # …then a second pass pulling 25% toward luma (per directive: desat
    # AFTER the multiply so the chartreuse hue is locked in first).
    _desaturate_body_only(big, amount=0.25, scale=scale, offset=offset)
    _draw_dead_eyes(big, scale, offset)
    _draw_double_vapor(big, scale, offset)
    big = pygame.transform.rotozoom(big, 10.0, 1.0)
    return big


# ── shadow compositing ───────────────────────────────────────────────────────

def _composite_with_shadow(sprite_big: pygame.Surface,
                           scale: float) -> pygame.Surface:
    """1 px native dark drop shadow under the body, 2 px native offset
    down/right. Anchors Pip as a "fallen weight." Drawn at SS scale so
    it survives the smoothscale-down at both 96 px native and 4x zoom.

    The shadow is the sprite's own alpha silhouette filled solid
    SHADOW_INK at SHADOW_ALPHA, offset by `2 * SS` px on each axis.
    """
    sw, sh = sprite_big.get_size()
    # Canvas extends down + right to hold the shadow offset without
    # clipping it off the bottom edge.
    pad = int(2 * scale + 6)
    canvas = pygame.Surface((sw + pad, sh + pad), pygame.SRCALPHA)

    # Build the shadow silhouette by masking the alpha channel.
    shadow = pygame.Surface((sw, sh), pygame.SRCALPHA)
    shadow.fill((SHADOW_INK[0], SHADOW_INK[1], SHADOW_INK[2], 0))
    # Walk the sprite alpha — anywhere opaque, write a SHADOW_ALPHA pixel.
    # Bbox-limited so we don't re-walk every transparent pixel.
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


# ── panel renderer ───────────────────────────────────────────────────────────

def _build_concept_surface(concept_fn) -> pygame.Surface:
    """Run a concept builder and return the supersampled RGBA surface
    with the universal drop shadow composited underneath. Smoothscale to
    presentation size happens in the native/zoom helpers below."""
    if concept_fn is concept_a_classic_x:
        base = _base_frame(2)
        big, _, _ = _supersample_canvas(base)
        concept_a_classic_x(big, SS, (0, 0))
    elif concept_fn is concept_b_soft:
        big = concept_b_soft(SS, (0, 0))
    elif concept_fn is concept_e_full_dead:
        big = concept_e_full_dead(SS, (0, 0))
    elif concept_fn is concept_f_convergence:
        big = concept_f_convergence(SS, (0, 0))
    else:
        raise ValueError(concept_fn)
    return _composite_with_shadow(big, SS)


def _render_concept_native(concept_fn) -> pygame.Surface:
    big = _build_concept_surface(concept_fn)
    bw, bh = big.get_size()
    target_w = int(bw * (NATIVE_H / bh))
    return pygame.transform.smoothscale(big, (target_w, NATIVE_H))


def _render_concept_zoom(concept_fn) -> pygame.Surface:
    big = _build_concept_surface(concept_fn)
    bw, bh = big.get_size()
    target_w = int(bw * (ZOOM_H / bh))
    return pygame.transform.smoothscale(big, (target_w, ZOOM_H))


def _swatch_disc(diameter: int, color, ring_color=(70, 90, 130)) -> pygame.Surface:
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
    """Vertical stack of 4 final panels with a title bar at the top."""
    panel_w = 920
    panel_h = 470
    gutter = 22
    title_h = 100
    sheet_w = panel_w + 60
    sheet_h = title_h + 4 * panel_h + 5 * gutter + 30

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
    title = title_font.render("DEAD PIP  —  Round 3 (final)", True, LABEL_HI)
    sheet.blit(title, ((sheet_w - title.get_width()) // 2, 24))
    sub_font = _font(16)
    sub = sub_font.render(
        "Tightened X (8x8 px bbox) + universal 1 px drop shadow under every body. "
        "4 finalists: glyph-only | pose-only+glyph | full-pose | restrained convergence.",
        True, LABEL_DIM,
    )
    sheet.blit(sub, ((sheet_w - sub.get_width()) // 2, 24 + title.get_height() + 6))

    concepts = [
        ("A.", "CLASSIC X-EYES",
         "Tightened X (4 px leg, ~8x8 px bbox) — strokes sit inside the socket ring. Pose unchanged.",
         concept_a_classic_x),
        ("B'.", "SOFT",
         "Pose-only+glyph: 8 deg back-tilt + FRAMES[3] droop wings. No tint, no tongue, no vapor.",
         concept_b_soft),
        ("E.", "FULL DEAD-POSE",
         "Droop wings + body-only desat + 14 deg back-tilt (was 20). Tongue dropped.",
         concept_e_full_dead),
        ("F.", "CONVERGENCE",
         "Restrained: chartreuse tint -25% extra desat, 2 curls (was 3), 10 deg tilt. Tongue dropped.",
         concept_f_convergence),
    ]

    y = title_h + 16
    for tag, head, note, fn in concepts:
        p = _panel(tag, head, note, fn, (panel_w, panel_h))
        sheet.blit(p, ((sheet_w - panel_w) // 2, y))
        y += panel_h + gutter

    return sheet


if __name__ == "__main__":
    out_path = "/home/user/skybit/docs/dead_pip/round_3.png"
    sheet = build_sheet()
    pygame.image.save(sheet, out_path)
    print(f"Saved {out_path} ({sheet.get_width()}x{sheet.get_height()})")
