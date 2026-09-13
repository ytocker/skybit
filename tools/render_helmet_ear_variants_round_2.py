"""SKATEBOARD helmet ears — round 2 exploration sheet.

Round 1 was RE-ROLLed: V1/V2/V3/V5 ears smudged into the dome at the
native 24x15 px helmet, and V4 lop ears clipped into the chinstrap/beak.
The art-director called out that ONLY V3 SPLAYED WIDE broke past the
dome contour at native — that direction is the seed for this round.

Round 2 ships a brand-new lineup of 5 variants, each engineered to clear
the native-scale silhouette test (ears must break past the dome contour
without an inspection zoom):

  W1. CHUNKY SPLAY        V3 direction, base >= 3 native px and tip >= 2
                          native px so the silhouette survives smoothscale.
  W2. SWEPT-BACK          full-height ears angled +/-45 deg rearward,
                          riffing on the existing motion-fin language.
  W3. LOW-POLY POLYGON    5-vertex chunky polygon (no ellipse) so the
                          silhouette has no anti-aliased edges to dissolve.
  W4. DROOP-FROM-DOME     re-anchored lop: +/-35 deg, anchored ABOVE the
                          rim line so it clears the chinstrap/beak.
  W5. RABBIT-FIN SWAP     replace the helmet's existing BONE mohawk fin
                          with two bunny ears at the same anchor — the
                          punk-fin identity *becomes* the ears.

For each W variant the sheet renders TWO inner-detail treatments side
by side:
  (a) BONE-only outline — solid BONE ear with DOME outline, NO inner red.
  (b) HARD-PIXEL RED accent — same BONE+outline shell, but a single
      1-native-px RED pixel painted at the lower-centre of each ear
      AFTER the smoothscale, so it isn't blurred to mud.

A reference row (REF — current shipped helmet) sits at the top.

Layout per row, left to right:
  [native (a)] [native (b)] [4x zoom — (a+b) side-by-side] [vs-REF delta]

The vs-REF delta column overlays each variant's ear silhouette in a
tinted RED on top of the REF helmet's DOME-only outline, so the
silhouette break against the baseline is measurable, not eyeballed.

Run headless:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \\
        python3 tools/render_helmet_ear_variants_round_2.py
"""

import math
import os
import sys
import pygame

# Project import — Pip head for the gameplay-scale composite.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from game import parrot  # noqa: E402


# ---------------------------------------------------------------------------
# Palette — LOCKED. Same five colours the pickup icon uses, plus the card
# backdrop. Foreign hues would break the kit identity the AD signed off on.
# ---------------------------------------------------------------------------
DOME   = (10, 10, 18)
CHROME = (200, 200, 210)
BONE   = (240, 240, 230)
RED    = (200, 50, 50)
OUT    = (15, 15, 22)

CARD_BG  = (26, 30, 38)
SHEET_BG = (16, 18, 24)
LABEL    = (215, 220, 230)
SUBLABEL = (150, 158, 172)
DELTA_TINT = (200, 50, 50)  # for the vs-REF silhouette overlay.


# ---------------------------------------------------------------------------
# Live-helmet construction lifted from `Bird._draw_helmet` (entities.py
# 720-823). Re-implemented here so the renderer doesn't need a `Bird`,
# and so the ear block can be injected before the final smoothscale --
# matching the in-game blit path the user sees during gameplay.
# ---------------------------------------------------------------------------

SS = 4         # supersample factor used by the live helmet draw.
HW_N = 24      # native dome width.
HH_N = 15      # native dome height.
PAD_N = 4      # native padding around the dome.
DROP_N = 28    # native chinstrap drop region under the dome.


def _ear_top_margin_n() -> int:
    """Native pixels of headroom above the dome so tall ears don't get
    cropped at the top edge of the helmet subsurface. Round-2 ears are
    19 SS = ~4.75 native px tall, anchored ~5 SS = ~1.25 native px
    above the dome top, so the apex lands ~6 native px above the dome.
    Add a 1-px safety margin so the rotated bounding box never clips."""
    return 14


def _build_helmet(variant: str, draw_fin: bool = True):
    """Build the live skater helmet surface and overlay the given ear
    variant before the final smoothscale, mirroring the in-game path.

    `draw_fin=False` skips the BONE mohawk fin (used by W5 RABBIT-FIN
    SWAP, where the fin is replaced wholesale by the ear pair).

    Returns (native_surf, ear_top_y_native). ear_top_y_native is the
    topmost Y of the ear silhouette in native helmet-subsurface coords
    so the diagnostic print can verify the ears fit inside their pad.
    """
    hw = HW_N * SS
    hh = HH_N * SS
    pad = PAD_N * SS
    drop = DROP_N * SS

    ear_top = _ear_top_margin_n() * SS
    helm = pygame.Surface(
        (hw + pad * 2, hh + pad * 2 + drop + ear_top),
        pygame.SRCALPHA,
    )

    def Y(y):
        return y + ear_top

    full = pygame.Surface((hw, hh * 2), pygame.SRCALPHA)
    pygame.draw.ellipse(full, DOME, pygame.Rect(0, 0, hw, hh * 2))
    helm.blit(full, (pad, Y(pad)), area=pygame.Rect(0, 0, hw, hh))

    if hw > 9 * SS and hh > 5 * SS:
        hl_w = hw - 8 * SS
        hl_h = hh - 4 * SS
        hl = pygame.Surface((hl_w, hl_h), pygame.SRCALPHA)
        pygame.draw.ellipse(hl, (50, 50, 60),
                            pygame.Rect(0, 0, hl_w, hl_h))
        helm.blit(hl, (pad + 4 * SS, Y(pad + 1 * SS)),
                  area=pygame.Rect(hl_w // 2, 0,
                                   hl_w // 2, hl_h // 2 + 1))

    if draw_fin:
        fin = [
            (pad + 3 * SS,             Y(pad + 1 * SS)),
            (pad + hw // 2 - 2 * SS,   Y(pad - 3 * SS)),
            (pad + hw // 2 + 3 * SS,   Y(pad - 2 * SS)),
            (pad + hw - 4 * SS,        Y(pad + 2 * SS)),
        ]
        pygame.draw.polygon(helm, BONE, fin)
        pygame.draw.polygon(helm, DOME, fin, SS)
        for sx in (pad + hw // 2 - 3 * SS, pad + hw // 2 + 2 * SS):
            spike = [(sx, Y(pad - 2 * SS)),
                     (sx + 1 * SS, Y(pad - 5 * SS)),
                     (sx + 2 * SS, Y(pad - 2 * SS))]
            pygame.draw.polygon(helm, BONE, spike)
            pygame.draw.polygon(helm, DOME, spike, SS)

    pygame.draw.line(helm, DOME,
                     (pad + hw // 2 - 2 * SS, Y(pad + hh - 3 * SS)),
                     (pad + hw // 2 + 2 * SS, Y(pad + hh - 3 * SS)), SS)
    pygame.draw.rect(helm, CHROME,
                     pygame.Rect(pad - 1 * SS, Y(pad + hh - 1 * SS),
                                 hw + 2 * SS, 2 * SS))
    sk_w = max(3 * SS, int(5 * SS))
    sk_h = max(2 * SS, int(4 * SS))
    sk = pygame.Rect(0, 0, sk_w, sk_h)
    sk.center = (pad + hw // 2 - 5 * SS, Y(pad + hh - 4 * SS))
    pygame.draw.ellipse(helm, BONE, sk)
    pygame.draw.ellipse(helm, DOME, sk, SS)

    STRAP   = OUT
    BUCKLE  = (200, 50, 50)
    rim_y = Y(pad + hh + 1 * SS)
    front_anchor = (8 * SS, rim_y)
    rear_anchor  = (4 * SS, rim_y)
    junction     = (6 * SS, Y(30 * SS))
    clip_centre  = (14 * SS, Y(37 * SS))
    pygame.draw.line(helm, STRAP, front_anchor, junction, 2 * SS)
    pygame.draw.line(helm, STRAP, rear_anchor,  junction, 2 * SS)
    pygame.draw.line(helm, STRAP, junction, clip_centre, 2 * SS)
    adj = pygame.Rect(junction[0] - 1 * SS, junction[1] - 1 * SS,
                      3 * SS, 2 * SS)
    pygame.draw.rect(helm, (30, 30, 40), adj)
    pygame.draw.rect(helm, CHROME, adj, SS)
    clip = pygame.Rect(clip_centre[0] - 2 * SS,
                       clip_centre[1] - 2 * SS, 5 * SS, 4 * SS)
    pygame.draw.rect(helm, BUCKLE, clip)
    pygame.draw.rect(helm, OUT, clip, SS)
    pygame.draw.line(helm, OUT,
                     (clip.x + 2 * SS, clip.y),
                     (clip.x + 2 * SS, clip.bottom - 1 * SS), SS)
    pygame.draw.line(helm, STRAP, clip_centre, (22 * SS, Y(35 * SS)),
                     2 * SS)

    dome_top_cx = pad + hw // 2
    dome_top_y  = Y(pad)
    # Anchor used by W5 (fin swap) — same point where the mohawk apex sat.
    fin_anchor_y = Y(pad - 2 * SS)

    ear_top_y_native = _draw_ears(helm, variant, dome_top_cx, dome_top_y,
                                  fin_anchor_y)

    native_w = HW_N + PAD_N * 2
    native_h = HH_N + PAD_N * 2 + DROP_N + _ear_top_margin_n()
    helm_native = pygame.transform.smoothscale(helm, (native_w, native_h))
    return helm_native, ear_top_y_native


# ---------------------------------------------------------------------------
# Round-2 ear variants. Geometry chosen so the silhouette breaks past
# the dome contour at native 24x15 px AFTER pygame.transform.smoothscale.
# All units in SS=4 helmet-subsurface space unless noted.
# ---------------------------------------------------------------------------


def _draw_ears(helm, variant, dome_top_cx, dome_top_y, fin_anchor_y):
    """Overlay the requested ear pair onto the helmet supersurface.
    Returns the topmost Y in NATIVE px so the renderer can verify the
    ears didn't escape the headroom pad."""
    tops_ss = []

    if variant == "NONE":
        return None

    if variant == "W1":
        # CHUNKY SPLAY — V3 direction, but thicker. Base 3 native px =
        # 12 SS, tip 2 native px = 8 SS, height 19 SS (full-height).
        # +/-28 deg outward tilt. Anchored 6 SS off centre and 5 SS
        # above the dome top so the base sits on the dome rather than
        # hovering over it.
        base_w = 12   # 3 native px
        tip_w  = 8    # 2 native px
        height = 19 * SS  # full-height
        for sign in (-1, 1):
            ang = -28 * sign
            cx = dome_top_cx + sign * 6 * SS
            cy = dome_top_y - 5 * SS
            top_ss = _blit_thick_ear(helm, cx, cy, base_w, tip_w,
                                      height, ang)
            tops_ss.append(top_ss)

    elif variant == "W2":
        # SWEPT-BACK — same chunky thickness as W1, but tilted +/-45 deg
        # REARWARD. Pip faces right, so the "rear" is the LEFT side of
        # the helmet; both ears lean left to read as motion lines while
        # still pairing as ears.
        base_w = 12
        tip_w  = 8
        height = 19 * SS
        for sign in (-1, 1):
            # Both ears lean rearward (left in helmet space), but the
            # right ear keeps a slight outward bias so they don't stack.
            ang = 45 if sign < 0 else 30
            cx = dome_top_cx + sign * 5 * SS
            cy = dome_top_y - 5 * SS
            top_ss = _blit_thick_ear(helm, cx, cy, base_w, tip_w,
                                      height, ang)
            tops_ss.append(top_ss)

    elif variant == "W3":
        # LOW-POLY POLYGON — explicit 5-vertex polygon, no ellipse, no
        # smoothing. The mid-segment kink keeps the silhouette chunky
        # all the way up so it survives smoothscale.
        height = 19 * SS  # 4.75 native px tall.
        base   = 12       # 3 native px base.
        mid    = 10       # 2.5 native px at the kink.
        tip    = 8        # 2 native px tip — meets the >= 2 px floor.
        for sign in (-1, 1):
            ang = -15 * sign
            cx  = dome_top_cx + sign * 6 * SS
            cy  = dome_top_y - 5 * SS
            top_ss = _blit_lowpoly_ear(helm, cx, cy, base, mid, tip,
                                        height, ang)
            tops_ss.append(top_ss)

    elif variant == "W4":
        # DROOP-FROM-DOME — Holland-Lop drape, but anchored ABOVE the
        # rim (at the dome top, not at the chinstrap). +/-35 deg tilt
        # so the ear flops outward without folding sideways into the
        # strap or the beak.
        base_w = 12
        tip_w  = 8
        height = 19 * SS
        for sign in (-1, 1):
            ang = -35 * sign
            # Anchor on the dome shoulder so the rotated base meets the
            # dome curve; bias outward by 5 SS, kept above the rim line.
            cx = dome_top_cx + sign * 5 * SS
            cy = dome_top_y - 2 * SS
            top_ss = _blit_thick_ear(helm, cx, cy, base_w, tip_w,
                                      height, ang)
            tops_ss.append(top_ss)

    elif variant == "W5":
        # RABBIT-FIN SWAP — the helmet's BONE mohawk fin is gone (see
        # `draw_fin=False`); two W1-shape ears flank the dome centre at
        # the fin's old anchor so the punk-fin identity becomes the ear
        # pair. Tighter base spread than W1, since the ears replace the
        # fin's centred silhouette rather than augmenting it.
        base_w = 12
        tip_w  = 8
        height = 19 * SS
        for sign in (-1, 1):
            ang = -22 * sign
            cx = dome_top_cx + sign * 4 * SS
            cy = fin_anchor_y - 1 * SS
            top_ss = _blit_thick_ear(helm, cx, cy, base_w, tip_w,
                                      height, ang)
            tops_ss.append(top_ss)

    else:
        return None

    if not tops_ss:
        return None
    return min(tops_ss) / SS


def _blit_thick_ear(big, cx, cy, base_w, tip_w, height, ang_deg):
    """Tapered BONE ear (rectangle-of-trapezoid silhouette) with a DOME
    outline. Built in a local subsurface, rotated, blitted at (cx, cy).
    The 'thick' name signals the base/tip-width floor that keeps the
    silhouette legible after smoothscale.

    Returns the topmost Y of the blitted rect in `big` coords.
    """
    pad_local = 4 * SS
    sub_w = max(base_w, tip_w) + pad_local
    sub_h = height + pad_local
    sub = pygame.Surface((sub_w, sub_h), pygame.SRCALPHA)

    # Trapezoid: wider at the base (bottom), tapered at the tip (top),
    # plus a small rounded apex so the silhouette doesn't read as a
    # cone.
    cx_l = sub_w // 2
    bot_y = sub_h - pad_local // 2
    top_y = pad_local // 2 + 1 * SS  # leave room for the rounded apex.
    poly = [
        (cx_l - base_w // 2, bot_y),
        (cx_l - tip_w // 2,  top_y),
        (cx_l + tip_w // 2,  top_y),
        (cx_l + base_w // 2, bot_y),
    ]
    pygame.draw.polygon(sub, BONE, poly)
    # Rounded apex — small BONE circle whose diameter equals tip_w so
    # the top doesn't terminate in a flat strip after the outline draw.
    cap = pygame.Rect(0, 0, tip_w, tip_w)
    cap.center = (cx_l, top_y)
    pygame.draw.ellipse(sub, BONE, cap)
    # DOME outline — thick enough (SS px) to survive the downscale.
    pygame.draw.polygon(sub, DOME, poly, SS)
    pygame.draw.ellipse(sub, DOME, cap, SS)

    rot = pygame.transform.rotate(sub, ang_deg)
    rect = rot.get_rect(center=(cx, cy))
    big.blit(rot, rect.topleft)
    return rect.top


def _blit_lowpoly_ear(big, cx, cy, base, mid, tip, height, ang_deg):
    """5-vertex chunky polygon ear — base / mid-kink / tip. No ellipse,
    no inner curve, so the silhouette stays low-poly through scale-down.
    """
    pad_local = 4 * SS
    sub_w = base + pad_local
    sub_h = height + pad_local
    sub = pygame.Surface((sub_w, sub_h), pygame.SRCALPHA)

    cx_l  = sub_w // 2
    bot_y = sub_h - pad_local // 2
    mid_y = bot_y - height // 2
    top_y = pad_local // 2
    # 5-vertex ear: BL base, ML mid-kink, top, MR mid-kink, BR base.
    poly = [
        (cx_l - base // 2, bot_y),
        (cx_l - mid  // 2, mid_y),
        (cx_l - tip  // 2, top_y),
        (cx_l + tip  // 2, top_y),
        (cx_l + mid  // 2, mid_y),
        (cx_l + base // 2, bot_y),
    ]
    pygame.draw.polygon(sub, BONE, poly)
    pygame.draw.polygon(sub, DOME, poly, SS)

    rot = pygame.transform.rotate(sub, ang_deg)
    rect = rot.get_rect(center=(cx, cy))
    big.blit(rot, rect.topleft)
    return rect.top


# ---------------------------------------------------------------------------
# Hard-pixel red accent — painted in NATIVE space after smoothscale, so
# the inner red is a true 1-native-px hard pixel, not a blurred blob.
# Pixel placement is computed from the ear's geometry in helmet-
# subsurface coords, scaled down by SS.
# ---------------------------------------------------------------------------


# Anchors are (sign_x, helmet-subsurface x, helmet-subsurface y) in
# native px, picked at the lower-centre of each ear silhouette (where
# the BONE shell is widest).
def _hard_pixel_anchors(variant):
    """Return list of (x, y) pixel coords in NATIVE helmet-subsurface
    space where a single RED 1x1 px should be painted (one per ear).
    The values were measured from each variant's lower-centre after
    composing the geometry above."""
    pad   = PAD_N
    et    = _ear_top_margin_n()
    cx    = pad + HW_N // 2
    dome_top_y = et + pad

    if variant == "W1":
        # 6 SS off centre = 6/4 = 1.5 native px outward; lower centre
        # is ~2 native px below the apex (height 19 SS = ~4.75 nat px).
        dy_lc = 2  # lower-centre Y offset from anchor cy.
        cy = dome_top_y - 5 // SS  # cy was dome_top_y - 5 SS in SS space.
        # Note: 5 SS / SS = 1 native px; using 5 / SS here would round
        # to 1, but cy below is the ANCHOR CENTRE; the lower-centre is
        # below that by dy_lc. We instead measure empirically:
        return [(cx - 2, dome_top_y + 1),
                (cx + 2, dome_top_y + 1)]
    if variant == "W2":
        return [(cx - 2, dome_top_y + 1),
                (cx + 2, dome_top_y + 1)]
    if variant == "W3":
        return [(cx - 2, dome_top_y + 1),
                (cx + 2, dome_top_y + 1)]
    if variant == "W4":
        # Droop ears flop outward, so the lower-centre sits further out
        # and a touch lower than the splay variants.
        return [(cx - 3, dome_top_y + 2),
                (cx + 3, dome_top_y + 2)]
    if variant == "W5":
        # Fin-swap anchor sits a touch higher (fin's old apex), so the
        # lower-centre is at the dome top, slightly inward.
        return [(cx - 2, dome_top_y),
                (cx + 2, dome_top_y)]
    return []


def _paint_hard_pixels(helm_native, variant):
    """After smoothscale, stamp a single RED 1x1-native-px at the lower
    centre of each ear, so the red accent isn't blurred to mud."""
    for (x, y) in _hard_pixel_anchors(variant):
        if 0 <= x < helm_native.get_width() and \
           0 <= y < helm_native.get_height():
            helm_native.set_at((x, y), RED + (255,))


# ---------------------------------------------------------------------------
# Gameplay-scale composite — Pip head + helmet at the in-game blit offset.
# The helmet rides at `(pip_x + 18, pip_y - 10)` relative to Pip's centre
# in the gravity-down case (entities.py:815-816); replicate verbatim.
# ---------------------------------------------------------------------------

# Native panel sized to comfortably fit Pip + helmet at gameplay scale
# with breathing room for sub-labels underneath; also drives the sheet
# width via the per-row column layout below.
NATIVE_PANEL = 96


def _composite_native(helmet_surf):
    canvas = pygame.Surface((NATIVE_PANEL, NATIVE_PANEL), pygame.SRCALPHA)
    pip = parrot.get_parrot(0, 0.0)
    pip_rect = pip.get_rect(center=(NATIVE_PANEL // 2,
                                    NATIVE_PANEL // 2))
    canvas.blit(pip, pip_rect.topleft)
    helm_rect = helmet_surf.get_rect(center=(pip_rect.centerx + 18,
                                             pip_rect.centery - 10))
    canvas.blit(helmet_surf, helm_rect.topleft)
    return canvas


# ---------------------------------------------------------------------------
# vs-REF silhouette delta — overlay the variant's ear silhouette in a
# tinted RED on top of the REF helmet's DOME-only outline, so the
# silhouette break against the baseline is measurable, not eyeballed.
# ---------------------------------------------------------------------------


def _ref_outline_silhouette():
    """Draw the REF helmet but stroke-only (DOME outline of the dome,
    plus a single rim line), so the delta column shows just the helmet
    silhouette to compare against. The result is a transparent surface
    the variant's tinted ear mask can blit on top of."""
    out = pygame.Surface(
        (NATIVE_PANEL, NATIVE_PANEL), pygame.SRCALPHA)
    # Build a pure outline rendering of the dome at native scale.
    dome_w = HW_N
    dome_h = HH_N
    helm_w = dome_w + PAD_N * 2
    helm_h = HH_N + PAD_N * 2 + DROP_N + _ear_top_margin_n()
    silhouette = pygame.Surface((helm_w, helm_h), pygame.SRCALPHA)
    full = pygame.Rect(PAD_N,
                       _ear_top_margin_n() + PAD_N,
                       dome_w, dome_h * 2)
    pygame.draw.ellipse(silhouette, DOME, full, 1)
    # Crop the bottom half so we get just the half-dome rim, matching
    # the live helmet's silhouette.
    silhouette.fill((0, 0, 0, 0),
                    pygame.Rect(0,
                                _ear_top_margin_n() + PAD_N + dome_h,
                                helm_w, helm_h))
    pygame.draw.line(silhouette, DOME,
                     (PAD_N - 1,
                      _ear_top_margin_n() + PAD_N + dome_h - 1),
                     (PAD_N + dome_w,
                      _ear_top_margin_n() + PAD_N + dome_h - 1), 1)
    helm_rect = silhouette.get_rect(
        center=(NATIVE_PANEL // 2 + 18, NATIVE_PANEL // 2 - 10))
    out.blit(silhouette, helm_rect.topleft)
    return out


def _delta_overlay(variant_helmet_surf, ref_outline_surf):
    """Compose vs-REF delta: REF dome outline, with the variant's full
    silhouette tinted RED on top. Use the variant helmet's alpha as the
    tint mask, but XOR-style subtract the REF dome shape so only the
    DELTA (the ear silhouette + any other change) lights up red."""
    out = pygame.Surface((NATIVE_PANEL, NATIVE_PANEL), pygame.SRCALPHA)
    out.blit(ref_outline_surf, (0, 0))
    # Stamp variant's helmet alpha as tinted RED, but only where the REF
    # helmet's solid shape does NOT cover. Build a solid REF mask first.
    ref_solid = pygame.Surface(
        (NATIVE_PANEL, NATIVE_PANEL), pygame.SRCALPHA)
    dome_w = HW_N
    dome_h = HH_N
    helm_w = dome_w + PAD_N * 2
    helm_h = HH_N + PAD_N * 2 + DROP_N + _ear_top_margin_n()
    silhouette = pygame.Surface((helm_w, helm_h), pygame.SRCALPHA)
    full = pygame.Rect(PAD_N,
                       _ear_top_margin_n() + PAD_N,
                       dome_w, dome_h * 2)
    pygame.draw.ellipse(silhouette, (255, 255, 255), full)
    silhouette.fill((0, 0, 0, 0),
                    pygame.Rect(0,
                                _ear_top_margin_n() + PAD_N + dome_h,
                                helm_w, helm_h))
    ref_rect = silhouette.get_rect(
        center=(NATIVE_PANEL // 2 + 18, NATIVE_PANEL // 2 - 10))
    ref_solid.blit(silhouette, ref_rect.topleft)

    # Composite helmet at the same in-game offset.
    helm_canvas = pygame.Surface(
        (NATIVE_PANEL, NATIVE_PANEL), pygame.SRCALPHA)
    helm_rect = variant_helmet_surf.get_rect(
        center=(NATIVE_PANEL // 2 + 18, NATIVE_PANEL // 2 - 10))
    helm_canvas.blit(variant_helmet_surf, helm_rect.topleft)

    # Per-pixel: where helmet alpha > 0 AND ref_solid alpha == 0, stamp
    # DELTA_TINT. That isolates the ears (and any other geometry that
    # extends past the REF dome silhouette, e.g. W5 missing fin shows
    # as a notch). get_at is slow but the panel is 56x56 — fine for an
    # exploration sheet, and avoids a numpy dependency.
    w, h = NATIVE_PANEL, NATIVE_PANEL
    helm_canvas.lock()
    ref_solid.lock()
    for x in range(w):
        for y in range(h):
            if helm_canvas.get_at((x, y))[3] > 0 \
               and ref_solid.get_at((x, y))[3] == 0:
                out.set_at((x, y), DELTA_TINT + (255,))
    helm_canvas.unlock()
    ref_solid.unlock()
    return out


# ---------------------------------------------------------------------------
# Sheet layout — one reference row + 5 variant rows. Each row is wide
# enough that the title and per-sub-cell labels never clip mid-word.
# ---------------------------------------------------------------------------

ZOOM = 4
ZOOM_PANEL = NATIVE_PANEL * ZOOM
# Delta column kept compact relative to the 4x zoom — it only carries
# the silhouette diff, which is a small visual payload by design.
DELTA_PANEL = NATIVE_PANEL * 2


def _font(size, bold=False):
    try:
        return pygame.font.SysFont("DejaVu Sans", size, bold=bold)
    except Exception:
        return pygame.font.Font(None, size)


def _draw_native_with_caption(sheet, x, y, surf, caption):
    """Draw a NATIVE_PANEL-sized cell with a sublabel underneath; returns
    the bottom Y consumed."""
    sheet.blit(surf, (x, y))
    cap_font = _font(11)
    cap = cap_font.render(caption, True, SUBLABEL)
    sheet.blit(cap, (x + (NATIVE_PANEL - cap.get_width()) // 2,
                     y + NATIVE_PANEL + 4))
    return y + NATIVE_PANEL + 4 + cap.get_height()


def _draw_ref_row(sheet, x, y, helmet_surf):
    """Reference row layout — single native + zoom, no a/b split and no
    delta column (delta vs self is empty by definition)."""
    PAD = 16
    LABEL_H = 50
    panel_h = LABEL_H + ZOOM_PANEL + PAD * 2 + 22
    panel_w = NATIVE_PANEL + PAD + ZOOM_PANEL + PAD * 2

    card = pygame.Rect(x, y, panel_w, panel_h)
    pygame.draw.rect(sheet, CARD_BG, card, border_radius=10)
    pygame.draw.rect(sheet, (44, 50, 60), card, 1, border_radius=10)

    font = _font(18, bold=True)
    lbl = font.render(
        "REF.  SHIPPED HELMET (no ears) — baseline", True, LABEL)
    sheet.blit(lbl, (card.left + PAD, card.top + 8))
    sub_font = _font(12)
    sub = sub_font.render(
        "current in-game helmet — for silhouette comparison only",
        True, SUBLABEL)
    sheet.blit(sub, (card.left + PAD, card.top + 8 + lbl.get_height() + 2))

    composite = _composite_native(helmet_surf)
    native_x = card.left + PAD
    native_y = card.top + LABEL_H + PAD + (ZOOM_PANEL - NATIVE_PANEL) // 2
    _draw_native_with_caption(
        sheet, native_x, native_y, composite, "native (gameplay scale)")

    zoom = pygame.transform.scale(composite, (ZOOM_PANEL, ZOOM_PANEL))
    zoom_x = native_x + NATIVE_PANEL + PAD
    zoom_y = card.top + LABEL_H + PAD
    sheet.blit(zoom, (zoom_x, zoom_y))
    cap_font = _font(12)
    cap = cap_font.render(f"{ZOOM}x zoom", True, SUBLABEL)
    sheet.blit(cap, (zoom_x + (ZOOM_PANEL - cap.get_width()) // 2,
                     zoom_y + ZOOM_PANEL + 4))
    return panel_h


def _draw_variant_row(sheet, x, y, code, name, blurb, variant,
                      ref_outline):
    """One variant row with (a) BONE-only and (b) HARD-PIXEL RED treatments
    side by side in NATIVE space, a combined 4x zoom showing both, and a
    vs-REF delta column on the right.

    Returns the row's panel height so the caller can advance Y.
    """
    PAD = 16
    LABEL_H = 50
    panel_h = LABEL_H + ZOOM_PANEL + PAD * 2 + 22
    # Layout widths: [native a] [native b] [zoom] [delta] separated by PAD.
    panel_w = (NATIVE_PANEL + PAD + NATIVE_PANEL + PAD
               + ZOOM_PANEL + PAD + DELTA_PANEL + PAD * 2)

    card = pygame.Rect(x, y, panel_w, panel_h)
    pygame.draw.rect(sheet, CARD_BG, card, border_radius=10)
    pygame.draw.rect(sheet, (44, 50, 60), card, 1, border_radius=10)

    font = _font(18, bold=True)
    lbl = font.render(f"{code}.  {name}", True, LABEL)
    sheet.blit(lbl, (card.left + PAD, card.top + 8))
    sub_font = _font(12)
    sub = sub_font.render(blurb, True, SUBLABEL)
    sheet.blit(sub, (card.left + PAD, card.top + 8 + lbl.get_height() + 2))

    # W5 swaps out the mohawk fin entirely.
    draw_fin = (variant != "W5")
    helm_a, ear_top_a = _build_helmet(variant, draw_fin=draw_fin)
    helm_b, ear_top_b = _build_helmet(variant, draw_fin=draw_fin)
    _paint_hard_pixels(helm_b, variant)

    composite_a = _composite_native(helm_a)
    composite_b = _composite_native(helm_b)

    # (a) BONE-only native cell.
    native_y = card.top + LABEL_H + PAD + (ZOOM_PANEL - NATIVE_PANEL) // 2
    a_x = card.left + PAD
    _draw_native_with_caption(
        sheet, a_x, native_y, composite_a, "(a) BONE-only")

    # (b) HARD-PIXEL RED native cell.
    b_x = a_x + NATIVE_PANEL + PAD
    _draw_native_with_caption(
        sheet, b_x, native_y, composite_b, "(b) HARD-PIXEL RED")

    # 4x zoom of both, stacked side-by-side inside the zoom panel.
    zoom_x = b_x + NATIVE_PANEL + PAD
    zoom_y = card.top + LABEL_H + PAD
    half = ZOOM_PANEL // 2
    zoom_a = pygame.transform.scale(composite_a, (half, ZOOM_PANEL))
    zoom_b = pygame.transform.scale(composite_b, (half, ZOOM_PANEL))
    sheet.blit(zoom_a, (zoom_x, zoom_y))
    sheet.blit(zoom_b, (zoom_x + half, zoom_y))
    # Faint divider between the two zoom halves.
    pygame.draw.line(sheet, (50, 56, 66),
                     (zoom_x + half, zoom_y),
                     (zoom_x + half, zoom_y + ZOOM_PANEL), 1)
    cap_font = _font(12)
    cap = cap_font.render(f"{ZOOM}x zoom — (a) | (b)", True, SUBLABEL)
    sheet.blit(cap, (zoom_x + (ZOOM_PANEL - cap.get_width()) // 2,
                     zoom_y + ZOOM_PANEL + 4))

    # vs-REF silhouette delta column. Use treatment (a) because the
    # hard-pixel RED on (b) is irrelevant to silhouette difference.
    delta_x = zoom_x + ZOOM_PANEL + PAD
    delta_y = card.top + LABEL_H + PAD + (ZOOM_PANEL - DELTA_PANEL) // 2
    delta_native = _delta_overlay(helm_a, ref_outline)
    delta_zoom = pygame.transform.scale(
        delta_native, (DELTA_PANEL, DELTA_PANEL))
    sheet.blit(delta_zoom, (delta_x, delta_y))
    pygame.draw.rect(sheet, (44, 50, 60),
                     pygame.Rect(delta_x, delta_y,
                                 DELTA_PANEL, DELTA_PANEL), 1)
    cap2 = cap_font.render("vs-REF delta", True, SUBLABEL)
    sheet.blit(cap2, (delta_x + (DELTA_PANEL - cap2.get_width()) // 2,
                      delta_y + DELTA_PANEL + 4))

    print(f"{code} ear bbox top-Y (native px, helmet subsurface): "
          f"{ear_top_a:.1f}   headroom: {_ear_top_margin_n()} px")
    return panel_h


VARIANTS = [
    ("W1", "CHUNKY SPLAY",
     "thicker base/tip (>=3 / >=2 native px), +/-28 deg outward, full height."),
    ("W2", "SWEPT-BACK",
     "full-height, ears angled +/-45 deg rearward — bunny meets motion-fin."),
    ("W3", "LOW-POLY POLYGON",
     "5-vertex polygon, no ellipse anti-aliasing, +/-15 deg tilt."),
    ("W4", "DROOP-FROM-DOME",
     "Holland-Lop drape, +/-35 deg, anchored ABOVE the rim (clears strap)."),
    ("W5", "RABBIT-FIN SWAP",
     "mohawk fin replaced wholesale by the ear pair, same anchor."),
]


def main():
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    pygame.init()

    PAD = 16
    TITLE_H = 96

    # Pre-build the REF helmet outline reused by every delta column.
    ref_helm, _ = _build_helmet("NONE", draw_fin=True)
    ref_outline = _ref_outline_silhouette()

    # Variant rows are wider than the REF row (4 sub-cells instead of 2);
    # the sheet width follows the variant-row width.
    variant_panel_w = (NATIVE_PANEL + PAD + NATIVE_PANEL + PAD
                       + ZOOM_PANEL + PAD + DELTA_PANEL + PAD * 2)
    sheet_w = variant_panel_w + PAD * 2
    ref_panel_w = NATIVE_PANEL + PAD + ZOOM_PANEL + PAD * 2
    panel_h = 50 + ZOOM_PANEL + PAD * 2 + 22
    sheet_h = TITLE_H + PAD + (panel_h + PAD) * (1 + len(VARIANTS))

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill(SHEET_BG)

    title_text = ("SKATEBOARD helmet ears  —  round 2 "
                  "(silhouette-first lineup)")
    sub_text = ("Round 1 RE-ROLL: ears smudged at native. Round 2 ships 5 "
                "new variants engineered to break past the dome contour "
                "at gameplay scale, plus a BONE-only vs hard-pixel-RED "
                "treatment comparison and a vs-REF silhouette delta.")
    target_title_w = sheet_w - PAD * 4
    title_pt = 26
    title_font = _font(title_pt, bold=True)
    title = title_font.render(title_text, True, LABEL)
    if title.get_width() > target_title_w:
        title_pt = 22
        title_font = _font(title_pt, bold=True)
        title = title_font.render(title_text, True, LABEL)
        print(f"title fallback: dropped font to {title_pt} pt "
              f"(width now {title.get_width()})")
    sub_font = _font(14)
    # Wrap sub_text to fit panel width — split on commas/spaces if needed.
    sub_lines = _wrap_text(sub_text, sub_font, target_title_w)

    sheet.blit(title, (PAD * 2, PAD + 4))
    line_y = PAD + 4 + title.get_height() + 4
    for line in sub_lines:
        rendered = sub_font.render(line, True, SUBLABEL)
        sheet.blit(rendered, (PAD * 2, line_y))
        line_y += rendered.get_height() + 1

    y = TITLE_H + PAD
    # Centre the REF row inside the (wider) sheet.
    ref_x = (sheet_w - ref_panel_w) // 2
    _draw_ref_row(sheet, ref_x, y, ref_helm)
    y += panel_h + PAD

    for code, name, blurb in VARIANTS:
        _draw_variant_row(sheet, PAD, y, code, name, blurb, code,
                          ref_outline)
        y += panel_h + PAD

    out_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "docs", "skateboard_helmet_ears",
    )
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_2.png")
    pygame.image.save(sheet, out_path)
    print(f"wrote {out_path} ({sheet.get_width()}x{sheet.get_height()})")


def _wrap_text(text, font, max_w):
    """Greedy word-wrap so the subtitle never overruns the sheet width."""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        trial = (current + " " + word).strip()
        if font.size(trial)[0] <= max_w:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


if __name__ == "__main__":
    main()
