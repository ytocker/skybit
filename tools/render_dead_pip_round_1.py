"""Round 1 of the dead-Pip design loop.

Renders 5 candidate dead-Pip treatments on top of the real in-game parrot
sprite (`game.parrot.FRAMES[2]`, mid-flap level wings) so reviews are judged
against the actual silhouette the player sees. Each concept paints its
own dead-eye / pose / tint / overlay ON TOP of the base bird and replaces
the aviator sunglasses at the original lens centres
(sprite-pixel `(cx-4, cy)` / `(cx+6, cy-1)` where head ref = `(50, 20)`).

Supersamples the dead overlays at ~5x and smoothscales down so the X
strokes, spirals, tongues, and toxic vapour all read crisply at 96 px
native display height (the in-game Pip size) AND at the 4x zoom column.
"""

import math
import os
import sys

# Headless run — pygbag isn't involved; we just want to save a PNG.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

sys.path.insert(0, "/home/user/skybit")

import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((1, 1))

from game import parrot  # noqa: E402

# ── palette ──────────────────────────────────────────────────────────────────
BG_TEAL     = (38, 44, 66)        # dawn-sky teal, per brief
SWATCH_DEEP = (28, 33, 50)        # darker disc behind native preview
PANEL_BG    = (24, 28, 42)
PANEL_EDGE  = (58, 70, 100)
LABEL_HI    = (245, 235, 210)
LABEL_DIM   = (170, 180, 210)
TAG_BG      = (58, 38, 50)
TAG_HI      = (255, 210, 90)

X_BLACK     = (15, 15, 25)        # body of the X — matches the original lens fill
X_OUTLINE   = (255, 255, 255)     # thin white halo behind the X for legibility on red head
EYEWHITE    = (245, 240, 230)
SPIRAL_INK  = (15, 15, 25)
TONGUE_HI   = (255, 145, 165)
TONGUE_BASE = (210,  60,  85)
TONGUE_DARK = (130,  20,  45)
VAPOR_GREEN = (200, 224,  96)     # same hue as the poison-vial vapor
VAPOR_DEEP  = (140, 180,  50)

# Lens centres in sprite-pixel coordinates (see game/parrot.py:71-104).
LEFT_LENS  = (50 - 4, 20)
RIGHT_LENS = (50 + 6, 20 - 1)

# Sprite size (also the size of the rotated base frame for level wings).
SPRITE_W, SPRITE_H = parrot.SPRITE_W, parrot.SPRITE_H

# Supersample factor for the dead-overlay layer. We paint the overlay on
# a transparent surface at this scale on top of an upscaled base, then
# smoothscale the composite down to native 96-px display height so the
# X strokes / spirals / tongues anti-alias cleanly.
SS = 5

# Display dimensions for the previews (native + 4x zoom side by side).
NATIVE_H = 96
ZOOM_FACTOR = 4
ZOOM_H = NATIVE_H * ZOOM_FACTOR


# ── helpers ──────────────────────────────────────────────────────────────────

def _font(size: int, bold: bool = False) -> pygame.font.Font:
    f = pygame.font.SysFont("dejavusans", size, bold=bold)
    return f


def _draw_x(surf: pygame.Surface, center: tuple[int, int], leg: float, thick: float,
            color=X_BLACK, halo_color=X_OUTLINE) -> None:
    """Two diagonal strokes forming a cartoon-dead X. `leg` is half the
    length of each stroke; `thick` is the stroke thickness. Renders the
    halo first so the body of the X stays crisp."""
    cx, cy = center
    # Two slightly-rotated strokes (12 deg) so the X feels hand-drawn rather
    # than perfectly orthogonal, which matches the rest of the bird's
    # warmer cartoon vocabulary.
    for ang_deg in (45 + 12, -45 + 12):
        a = math.radians(ang_deg)
        dx = math.cos(a) * leg
        dy = math.sin(a) * leg
        p1 = (cx - dx, cy - dy)
        p2 = (cx + dx, cy + dy)
        # Halo
        pygame.draw.line(surf, halo_color, p1, p2, max(1, int(thick + 2)))
    for ang_deg in (45 + 12, -45 + 12):
        a = math.radians(ang_deg)
        dx = math.cos(a) * leg
        dy = math.sin(a) * leg
        p1 = (cx - dx, cy - dy)
        p2 = (cx + dx, cy + dy)
        pygame.draw.line(surf, color, p1, p2, max(1, int(thick)))


def _draw_eye_white_disc(surf: pygame.Surface, center: tuple[int, int],
                         radius: float) -> None:
    """Pale eye-white disc behind a spiral, to give the spiral a clean
    contrast field on the red head. Soft thin rim sells the cartoon read."""
    cx, cy = center
    r = int(radius)
    pygame.draw.circle(surf, (220, 215, 200), (int(cx), int(cy)), r + 1)
    pygame.draw.circle(surf, EYEWHITE, (int(cx), int(cy)), r)


def _draw_spiral(surf: pygame.Surface, center: tuple[int, int],
                 r_outer: float, turns: float, thick: float) -> None:
    """Concussed-cartoon spiral. Starts from the centre, sweeps outwards
    over `turns` revolutions, sampled densely enough that smoothscale-down
    yields a clean continuous curve."""
    cx, cy = center
    steps = max(40, int(turns * 60))
    pts: list[tuple[float, float]] = []
    for i in range(steps + 1):
        t = i / steps
        ang = turns * 2 * math.pi * t
        rad = r_outer * t
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    if len(pts) >= 2:
        pygame.draw.lines(surf, SPIRAL_INK, False, pts, max(1, int(thick)))


def _draw_tongue(surf: pygame.Surface, anchor: tuple[float, float],
                 length: float, width: float) -> None:
    """Pink/red tongue hanging straight down from the beak slot. Tear-
    drop silhouette with a soft mid-tone highlight so it reads as soft
    flesh rather than a flat polygon."""
    ax, ay = anchor
    # Outer (dark) silhouette
    pts_outer = [
        (ax - width * 0.55, ay),
        (ax + width * 0.55, ay),
        (ax + width * 0.40, ay + length * 0.85),
        (ax,                 ay + length),
        (ax - width * 0.40, ay + length * 0.85),
    ]
    pygame.draw.polygon(surf, TONGUE_DARK, pts_outer)
    # Inner fill — slightly narrower so dark silhouette reads as outline
    pts_in = [
        (ax - width * 0.40, ay + 1.5),
        (ax + width * 0.40, ay + 1.5),
        (ax + width * 0.28, ay + length * 0.82),
        (ax,                 ay + length - 1.0),
        (ax - width * 0.28, ay + length * 0.82),
    ]
    pygame.draw.polygon(surf, TONGUE_BASE, pts_in)
    # Soft sheen down the centre
    pygame.draw.line(surf, TONGUE_HI,
                     (ax - 0.5, ay + 2.0),
                     (ax - 0.5, ay + length * 0.75),
                     max(1, int(width * 0.25)))
    # Tip glint
    pygame.draw.circle(surf, TONGUE_HI, (int(ax), int(ay + length * 0.45)),
                       max(1, int(width * 0.18)))


def _draw_vapor_curl(surf: pygame.Surface, base: tuple[float, float],
                     height: float) -> None:
    """Sickly yellow-green vapor curl rising from the beak. Stack of soft
    discs with alpha falloff plus a gentle horizontal drift, so it reads
    as smoke rather than a paint splat — the same vocabulary the live
    poison-vial uses for its vapor."""
    bx, by = base
    layers = 7
    for i in range(layers):
        t = i / (layers - 1)
        # Drift sideways slightly in a sine so the curl looks alive.
        dx = math.sin(t * math.pi * 1.4) * height * 0.18
        cx = bx + dx
        cy = by - t * height
        r = (1.0 - 0.45 * t) * height * 0.22
        alpha = int(220 * (1.0 - t * 0.8))
        col = (
            int(VAPOR_GREEN[0] * (1 - t) + VAPOR_DEEP[0] * t),
            int(VAPOR_GREEN[1] * (1 - t) + VAPOR_DEEP[1] * t),
            int(VAPOR_GREEN[2] * (1 - t) + VAPOR_DEEP[2] * t),
            alpha,
        )
        disc = pygame.Surface((int(r * 2 + 4), int(r * 2 + 4)), pygame.SRCALPHA)
        pygame.draw.circle(disc, col, (int(r + 2), int(r + 2)), int(r))
        surf.blit(disc, (cx - r - 2, cy - r - 2))


def _tint_body(sprite: pygame.Surface,
               factors: tuple[float, float, float]) -> pygame.Surface:
    """Multiply the per-channel colour of a sprite by the given factors,
    preserving alpha. Pure-pygame implementation (no numpy)."""
    fr, fg, fb = factors
    w, h = sprite.get_size()
    out = pygame.Surface((w, h), pygame.SRCALPHA)
    src_lock = sprite.lock()
    out_lock = out.lock()
    try:
        for y in range(h):
            for x in range(w):
                r, g, b, a = sprite.get_at((x, y))
                if a == 0:
                    continue
                out.set_at((x, y), (
                    min(255, max(0, int(r * fr))),
                    min(255, max(0, int(g * fg))),
                    min(255, max(0, int(b * fb))),
                    a,
                ))
    finally:
        out.unlock()
        sprite.unlock()
    return out


def _desaturate(sprite: pygame.Surface, amount: float = 0.4) -> pygame.Surface:
    """Pull a sprite toward Rec.601 luma by `amount` (0=identity,
    1=full grey). Preserves alpha. Pure-pygame."""
    w, h = sprite.get_size()
    out = pygame.Surface((w, h), pygame.SRCALPHA)
    k = 1.0 - amount
    for y in range(h):
        for x in range(w):
            r, g, b, a = sprite.get_at((x, y))
            if a == 0:
                continue
            lum = 0.299 * r + 0.587 * g + 0.114 * b
            out.set_at((x, y), (
                int(r * k + lum * amount),
                int(g * k + lum * amount),
                int(b * k + lum * amount),
                a,
            ))
    return out


# ── base sprite assembly (with the bob baked in) ─────────────────────────────

def _base_frame(frame_idx: int = 2) -> pygame.Surface:
    """Pull the real in-game parrot frame so concepts are judged against
    the actual silhouette. parrot.FRAMES already includes the outline."""
    return parrot.FRAMES[frame_idx].copy()


def _supersample_canvas(base: pygame.Surface) -> tuple[pygame.Surface, float, tuple[int, int]]:
    """Upscale the base sprite by SS so we have plenty of room to paint
    smooth dead-overlay details on top. Returns the upscaled base, the
    SS factor used, and the (offset) where the sprite sits inside the
    canvas (this matches the outline padding `parrot._add_outline` adds —
    we just scale uniformly)."""
    w, h = base.get_size()
    big = pygame.transform.smoothscale(base, (w * SS, h * SS))
    return big, SS, (0, 0)


def _sprite_to_canvas(p: tuple[float, float],
                      offset: tuple[int, int],
                      scale: float,
                      outline_pad: int = 2) -> tuple[float, float]:
    """Map a sprite-pixel coordinate (in the un-padded 64x60 frame's
    coordinate system) onto the supersampled canvas. The real `FRAMES`
    surface is padded by 2 px on every side by `_add_outline`, so we
    bake that offset into the mapping."""
    return ((p[0] + outline_pad + offset[0]) * scale,
            (p[1] + outline_pad + offset[1]) * scale)


# ── concept overlays — each receives the supersampled base and paints on it ──

def concept_a_classic_x(big: pygame.Surface, scale: float,
                        offset: tuple[int, int]) -> pygame.Surface:
    """A. Classic X-eyes. Two black X strokes at each lens centre,
    replacing the sunglasses entirely. Stroke thickness ~3 px at
    native = 3*SS at supersampled."""
    leg = 4.2 * scale     # ~4.2 px at native → ~6 px diagonal leg
    thick = 2.6 * scale   # ~2.6 px at native, looks like a 3 px stroke after AA
    for centre in (LEFT_LENS, RIGHT_LENS):
        c = _sprite_to_canvas(centre, offset, scale)
        _draw_x(big, c, leg, thick)
    return big


def concept_b_spiral(big: pygame.Surface, scale: float,
                     offset: tuple[int, int]) -> pygame.Surface:
    """B. Spiral / swirly eyes — 1.5–2 turn black spiral on a pale
    eye-white disc at each lens centre."""
    r_disc = 6.0 * scale
    r_spiral = 4.4 * scale
    for centre in (LEFT_LENS, RIGHT_LENS):
        c = _sprite_to_canvas(centre, offset, scale)
        _draw_eye_white_disc(big, c, r_disc)
        _draw_spiral(big, c, r_spiral, turns=1.8, thick=1.6 * scale)
    return big


def concept_c_x_plus_tongue(big: pygame.Surface, scale: float,
                            offset: tuple[int, int]) -> pygame.Surface:
    """C. X-eyes plus a limp tongue hanging from the beak slot."""
    concept_a_classic_x(big, scale, offset)
    # Beak slot — the lower-beak split line in parrot.py sits at sprite
    # y=24-25 and x=52-58; we drop the tongue just below the mouth
    # opening so it reads as hanging from inside the beak.
    anchor = _sprite_to_canvas((55.5, 26.0), offset, scale)
    _draw_tongue(big, anchor, length=7.0 * scale, width=3.4 * scale)
    return big


def concept_d_poisoned(big: pygame.Surface, scale: float,
                       offset: tuple[int, int]) -> pygame.Surface:
    """D. X-eyes plus sickly green tint plus a toxic vapor curl rising
    from the beak. The tint is applied before the X so the X stays a
    crisp black on top of the sickly bird."""
    # Pre-tint the body underneath. Multiplying the RGB channels by
    # (0.7, 1.0, 0.5) drops red, holds green, slashes blue — bringing
    # the bird's vibrant scarlet down into a queasy olive-green range.
    tinted = _tint_body(big, (0.7, 1.0, 0.5))
    big.fill((0, 0, 0, 0))
    big.blit(tinted, (0, 0))
    concept_a_classic_x(big, scale, offset)
    # Vapor curl rising from the beak tip (sprite ~ (61, 24)).
    base = _sprite_to_canvas((60.0, 22.0), offset, scale)
    _draw_vapor_curl(big, base, height=14.0 * scale)
    return big


def concept_e_full_dead(scale: float,
                        offset: tuple[int, int]) -> pygame.Surface:
    """E. Full dead-pose. Built on the down-most wing frame FRAMES[3]
    (wing angle -40 deg) for drooping wings, with body desaturation +
    full-sprite back-tilt + X-eyes + limp tongue.

    Builds its own supersampled canvas because the base frame is
    different from A-D."""
    base = parrot.FRAMES[3].copy()
    # Desaturate the body so the bird reads as slack.
    base = _desaturate(base, amount=0.32)
    big, _, _ = _supersample_canvas(base)
    concept_a_classic_x(big, scale, offset)
    # Limp tongue from the beak slot
    anchor = _sprite_to_canvas((55.5, 26.0), offset, scale)
    _draw_tongue(big, anchor, length=8.0 * scale, width=3.6 * scale)
    # Tilt the entire sprite back ~20 deg (counter-clockwise from Pip's
    # facing direction — head goes back, tail goes down).
    big = pygame.transform.rotozoom(big, 20.0, 1.0)
    return big


# ── panel renderer ───────────────────────────────────────────────────────────

def _render_concept_native(concept_fn) -> pygame.Surface:
    """Run a concept builder against a fresh supersampled canvas and
    smoothscale down to NATIVE_H height with a tiny downward bob so
    the preview matches the falling motion."""
    if concept_fn is concept_e_full_dead:
        big = concept_fn(SS, (0, 0))
    else:
        base = _base_frame(2)
        big, _, _ = _supersample_canvas(base)
        concept_fn(big, SS, (0, 0))
    # Scale down to a target height of NATIVE_H while keeping aspect.
    bw, bh = big.get_size()
    target_w = int(bw * (NATIVE_H / bh))
    return pygame.transform.smoothscale(big, (target_w, NATIVE_H))


def _render_concept_zoom(concept_fn) -> pygame.Surface:
    """Same concept, scaled to the 4x zoom target. Builds at SS, scales
    once to the larger display size so pixels stay smooth."""
    if concept_fn is concept_e_full_dead:
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
    # Outer ring
    pygame.draw.circle(surf, ring_color, (r, r), r)
    # Inner disc with a gentle radial shading: deeper bottom, lighter top.
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
    """A single concept panel — tag bar at top, native preview on a
    teal swatch on the left, 4x zoom preview on the right, footnote
    underneath. `bob_offset_px` bakes a small downward bob into the
    preview Y position so the preview matches the falling motion."""
    pw, ph = panel_size
    surf = pygame.Surface((pw, ph), pygame.SRCALPHA)
    # Panel background — rounded panel with a thin lens-flare edge.
    pygame.draw.rect(surf, PANEL_BG, surf.get_rect(), border_radius=14)
    pygame.draw.rect(surf, PANEL_EDGE, surf.get_rect(), width=2, border_radius=14)

    # Top tag bar
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
    # Tiny native-size label
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

    # Bottom note
    note_y = max(swatch_y + swatch_d + 26, zoom_rect.bottom + 26)
    note_surf = _font(15).render(note, True, LABEL_DIM)
    surf.blit(note_surf, (18, note_y))
    return surf


def build_sheet() -> pygame.Surface:
    """Vertical stack of 5 panels with a title bar at the top."""
    # Panel height needs to fit the 4x zoom preview (384 px) plus padding.
    panel_w = 920
    panel_h = 470
    gutter = 22
    title_h = 78
    sheet_w = panel_w + 60
    sheet_h = title_h + 5 * panel_h + 6 * gutter + 30

    sheet = pygame.Surface((sheet_w, sheet_h))
    # Dawn-teal gradient background
    for y in range(sheet_h):
        t = y / max(1, sheet_h - 1)
        col = (
            int(BG_TEAL[0] * (1 - t * 0.25)),
            int(BG_TEAL[1] * (1 - t * 0.20)),
            int(BG_TEAL[2] * (1 - t * 0.15)),
        )
        pygame.draw.line(sheet, col, (0, y), (sheet_w, y))

    # Title bar
    title_font = _font(36, bold=True)
    title = title_font.render("DEAD PIP  —  Round 1  (poison-only death sprite)", True, LABEL_HI)
    sheet.blit(title, ((sheet_w - title.get_width()) // 2, 24))
    sub_font = _font(16)
    sub = sub_font.render(
        "5 concepts painted on the real in-game parrot. Native 96 px (left) + 4x zoom (right). "
        "Dawn-teal sky swatch + 2 px downward bob baked in.",
        True, LABEL_DIM,
    )
    sheet.blit(sub, ((sheet_w - sub.get_width()) // 2, 24 + title.get_height() + 4))

    concepts = [
        ("A.", "CLASSIC X-EYES",
         "Replaces the aviators with two black diagonal X strokes (~3 px native). Pose + body unchanged.",
         concept_a_classic_x),
        ("B.", "SPIRAL EYES",
         "Concussed-cartoon spiral on a pale eye-white disc at each lens. Dazed/dizzy read.",
         concept_b_spiral),
        ("C.", "X + LIMP TONGUE",
         "Classic X plus a small pink tongue hanging straight down from the beak. Max cartoon-dead.",
         concept_c_x_plus_tongue),
        ("D.", "POISONED",
         "X + sickly-green palette shift + toxic yellow-green vapor curl from the beak (ties to vial vapor).",
         concept_d_poisoned),
        ("E.", "FULL DEAD-POSE",
         "Drooping wings (FRAMES[3]) + body desaturation + 20 deg head-back tilt + X-eyes + limp tongue.",
         concept_e_full_dead),
    ]

    y = title_h + 16
    for tag, head, note, fn in concepts:
        p = _panel(tag, head, note, fn, (panel_w, panel_h))
        sheet.blit(p, ((sheet_w - panel_w) // 2, y))
        y += panel_h + gutter

    return sheet


if __name__ == "__main__":
    out_path = "/home/user/skybit/docs/dead_pip/round_1.png"
    sheet = build_sheet()
    pygame.image.save(sheet, out_path)
    print(f"Saved {out_path} ({sheet.get_width()}x{sheet.get_height()})")
