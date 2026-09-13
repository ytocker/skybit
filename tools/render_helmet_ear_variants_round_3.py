"""SKATEBOARD helmet ears — round 3 FINAL exploration sheet.

Round 2 verdict was ITERATE. W3 LOW-POLY POLYGON was the lead because its
ear pair read as a vertical MASS rather than a line; W1 CHUNKY SPLAY was
the runner-up DNA. W2 SWEPT-BACK and W5 RABBIT-FIN SWAP were dropped.
W4 DROOP-FROM-DOME failed structurally (droop stayed vertical, eaten by
the dome) and gets re-rolled as a TRUE LOP that bends OUTWARD past the
dome's widest contour with tips at/below the helmet equator.

Round-3 lineup, all BONE-only (single-pixel RED accent dropped per AD —
it read as kill-marker noise at native scale):

  X1. W1 CHUNKY SPLAY +1 BASE  — runner-up, bases widened +1 native px
                                  each side. Tilt stays +/-28 deg.
  X2. W3 FATTENED (lead)        — round-2 W3 lead, bases widened +1
                                  native px each side. Primary AD call.
  X3. W3 EXTRA-WIDE             — bases widened +2 native px each side.
                                  Tests how far chunky can be pushed.
  X4. W3 CARTILAGE              — X2 metrics, plus a 1-native-px DOME
                                  highlight stripe down each ear centre.
  X5. TRUE LOP                  — W4 re-rolled. Ears bend 70-80 deg from
                                  vertical at the base, body lies
                                  near-horizontal, tips at/below the
                                  helmet equator. Crossy-Road bunny DNA.

Layout per row:
  [native (BONE-only)] [4x zoom] [vs-REF delta]

The vs-REF delta column overlays the variant's ear silhouette in tinted
RED on top of the REF helmet's DOME-only outline, so the silhouette
break against the baseline is measurable, not eyeballed.

Run headless:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \\
        python3 tools/render_helmet_ear_variants_round_3.py
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
# 720-823). Re-implemented here so the renderer doesn't need a `Bird`, and
# so the ear block can be injected before the final smoothscale — matching
# the in-game blit path the user sees during gameplay.
# ---------------------------------------------------------------------------

SS = 4         # supersample factor used by the live helmet draw.
HW_N = 24      # native dome width.
HH_N = 15      # native dome height.
PAD_N = 4      # native padding around the dome.
DROP_N = 28    # native chinstrap drop region under the dome.


def _ear_top_margin_n() -> int:
    """Native pixels of headroom above the dome so tall ears don't get
    cropped at the top edge of the helmet subsurface. Round-3 ears still
    fit inside ~6 native px above the dome top; reuse round-2's 14 px
    headroom so apex never clips even with the +/-28 deg splay rotation."""
    return 14


def _build_helmet(variant: str, draw_fin: bool = True):
    """Build the live skater helmet surface and overlay the given ear
    variant before the final smoothscale, mirroring the in-game path.

    `draw_fin=False` is unused in round 3 (we keep the mohawk fin under
    every ear variant since W5 was dropped) but stays here so the helper
    keeps parity with the round-2 renderer signature.

    Returns (native_surf, ear_bbox_native) where ear_bbox_native is
    (min_x, min_y, max_x, max_y) of the ear silhouette in NATIVE
    helmet-subsurface coords. Used by the diagnostic print so the
    orchestrator can verify horizontal break on X5 and vertical mass on
    X1-X4.
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
    # Helmet equator = vertical midpoint of the dome (rim line is at
    # Y(pad + hh)). For TRUE LOP we want tips at or below this line.
    helmet_equator_y = Y(pad + hh // 2)
    # Dome widest contour x-extents at native: pad..pad+hw on the SS
    # canvas. Native equivalents shift down to PAD_N..PAD_N+HW_N.
    dome_left_ss  = pad
    dome_right_ss = pad + hw

    ear_bbox_ss = _draw_ears(helm, variant, dome_top_cx, dome_top_y,
                             helmet_equator_y, dome_left_ss, dome_right_ss)

    native_w = HW_N + PAD_N * 2
    native_h = HH_N + PAD_N * 2 + DROP_N + _ear_top_margin_n()
    helm_native = pygame.transform.smoothscale(helm, (native_w, native_h))

    # Convert ear bbox from SS space to native px.
    if ear_bbox_ss is None:
        ear_bbox = None
    else:
        x0, y0, x1, y1 = ear_bbox_ss
        ear_bbox = (x0 / SS, y0 / SS, x1 / SS, y1 / SS)
    return helm_native, ear_bbox


# ---------------------------------------------------------------------------
# Round-3 ear variants. All BONE-only; bases widened so the silhouette
# survives smoothscale at the gameplay-scale 24x15 native helmet.
# All units in SS=4 helmet-subsurface space unless noted.
# ---------------------------------------------------------------------------


def _draw_ears(helm, variant, dome_top_cx, dome_top_y, helmet_equator_y,
               dome_left_ss, dome_right_ss):
    """Overlay the requested ear pair onto the helmet supersurface.
    Returns the bounding box (min_x, min_y, max_x, max_y) of the ear
    pixels in SS-canvas coords so the renderer can verify silhouette
    extents (horizontal break for X5, vertical mass for X1-X4)."""
    rects = []

    if variant == "NONE":
        return None

    if variant == "X1":
        # CHUNKY SPLAY +1 BASE. Round-2 W1 base was 12 SS = 3 native px;
        # round 3 widens to 16 SS = 4 native px so the base reads as
        # mass at native. Tip stays at 8 SS = 2 native px to keep a
        # bunny-ear taper rather than a slab. Tilt unchanged at +/-28.
        base_w = 16   # 4 native px
        tip_w  = 8    # 2 native px
        height = 19 * SS
        for sign in (-1, 1):
            ang = -28 * sign
            cx = dome_top_cx + sign * 6 * SS
            cy = dome_top_y - 5 * SS
            rect = _blit_thick_ear(helm, cx, cy, base_w, tip_w,
                                   height, ang)
            rects.append(rect)

    elif variant == "X2":
        # W3 FATTENED — the AD's lead candidate. Round-2 W3 used base 12,
        # mid 10, tip 8 (3 / 2.5 / 2 native px). Round 3 widens to base
        # 16, mid 12, tip 8 (4 / 3 / 2 native px). Tilt unchanged at
        # +/-15 deg, 5-vertex low-poly silhouette preserved.
        height = 19 * SS
        base = 16   # 4 native px
        mid  = 12   # 3 native px
        tip  = 8    # 2 native px
        for sign in (-1, 1):
            ang = -15 * sign
            cx  = dome_top_cx + sign * 6 * SS
            cy  = dome_top_y - 5 * SS
            rect = _blit_lowpoly_ear(helm, cx, cy, base, mid, tip,
                                     height, ang)
            rects.append(rect)

    elif variant == "X3":
        # W3 EXTRA-WIDE — push base another native px to 20 SS = 5 native
        # px. Tests whether the chunky direction stays bunny-coded or
        # starts to read as horns/bear ears. Mid widens proportionally;
        # tip kept at 8 SS so the apex doesn't blunt into a slab.
        height = 19 * SS
        base = 20   # 5 native px
        mid  = 14   # 3.5 native px
        tip  = 8    # 2 native px
        for sign in (-1, 1):
            ang = -15 * sign
            cx  = dome_top_cx + sign * 7 * SS
            cy  = dome_top_y - 5 * SS
            rect = _blit_lowpoly_ear(helm, cx, cy, base, mid, tip,
                                     height, ang)
            rects.append(rect)

    elif variant == "X4":
        # W3 CARTILAGE — X2 silhouette with a single 1-native-px DOME
        # highlight stripe down each ear centre. The stripe is drawn at
        # SS thickness in helmet-subsurface space; after smoothscale it
        # reads as roughly 1 native px. Sole interior detail so we test
        # whether minimal cartilage cue survives downscale.
        height = 19 * SS
        base = 16
        mid  = 12
        tip  = 8
        for sign in (-1, 1):
            ang = -15 * sign
            cx  = dome_top_cx + sign * 6 * SS
            cy  = dome_top_y - 5 * SS
            rect = _blit_lowpoly_ear(
                helm, cx, cy, base, mid, tip, height, ang,
                cartilage_stripe=True,
            )
            rects.append(rect)

    elif variant == "X5":
        # TRUE LOP — re-rolled W4. Ear body lies near-horizontal past the
        # dome's widest contour with the tip AT or BELOW the helmet
        # equator. Built as a chunky low-poly polygon like W3 fattened
        # (no ellipse anti-aliasing), then rotated 75 deg from vertical
        # so the polygon arc bends outward. Anchored on the dome shoulder
        # so the rotated base meets the dome surface, then the body
        # extends OUTWARD over the dome's widest point.
        height = 22 * SS  # slightly longer than the splay variants
        base = 16
        mid  = 12
        tip  = 8
        # Rotation: 75 deg from vertical = the apex points sideways. Sign
        # flips between left and right ear so they fan symmetrically.
        for sign in (-1, 1):
            ang = -75 * sign
            # Anchor on the dome shoulder where the dome curve is widest
            # in the upper hemisphere. cx is biased outward so the
            # rotated base meets the dome rather than crossing through
            # the dome's centre, and cy is on the dome equator line so
            # the lop's body lies right across the helmet's widest belt.
            cx = dome_top_cx + sign * 5 * SS
            cy = dome_top_y + 4 * SS
            rect = _blit_lowpoly_ear(helm, cx, cy, base, mid, tip,
                                     height, ang)
            rects.append(rect)

    else:
        return None

    if not rects:
        return None
    x0 = min(r.left  for r in rects)
    y0 = min(r.top   for r in rects)
    x1 = max(r.right for r in rects)
    y1 = max(r.bottom for r in rects)
    return (x0, y0, x1, y1)


def _blit_thick_ear(big, cx, cy, base_w, tip_w, height, ang_deg):
    """Tapered BONE ear (trapezoid with a rounded apex) with a DOME
    outline. Built in a local subsurface, rotated, blitted at (cx, cy).
    Returns the blitted rect in `big` coords."""
    pad_local = 4 * SS
    sub_w = max(base_w, tip_w) + pad_local
    sub_h = height + pad_local
    sub = pygame.Surface((sub_w, sub_h), pygame.SRCALPHA)

    cx_l = sub_w // 2
    bot_y = sub_h - pad_local // 2
    top_y = pad_local // 2 + 1 * SS
    poly = [
        (cx_l - base_w // 2, bot_y),
        (cx_l - tip_w // 2,  top_y),
        (cx_l + tip_w // 2,  top_y),
        (cx_l + base_w // 2, bot_y),
    ]
    pygame.draw.polygon(sub, BONE, poly)
    cap = pygame.Rect(0, 0, tip_w, tip_w)
    cap.center = (cx_l, top_y)
    pygame.draw.ellipse(sub, BONE, cap)
    pygame.draw.polygon(sub, DOME, poly, SS)
    pygame.draw.ellipse(sub, DOME, cap, SS)

    rot = pygame.transform.rotate(sub, ang_deg)
    rect = rot.get_rect(center=(cx, cy))
    big.blit(rot, rect.topleft)
    return rect


def _blit_lowpoly_ear(big, cx, cy, base, mid, tip, height, ang_deg,
                      cartilage_stripe=False):
    """5-vertex chunky polygon ear — base / mid-kink / tip. No ellipse,
    no inner curve, so the silhouette stays low-poly through scale-down.
    `cartilage_stripe=True` adds a single SS-thick DOME stripe down the
    ear centre (X4 only) as a minimal cartilage cue.
    """
    pad_local = 4 * SS
    sub_w = max(base, mid, tip) + pad_local
    sub_h = height + pad_local
    sub = pygame.Surface((sub_w, sub_h), pygame.SRCALPHA)

    cx_l  = sub_w // 2
    bot_y = sub_h - pad_local // 2
    mid_y = bot_y - height // 2
    top_y = pad_local // 2
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
    if cartilage_stripe:
        # Centre stripe runs from just above the base inward to just
        # below the tip; SS thick so it survives downscale to ~1 nat px.
        # Inset from base/tip so it doesn't merge with the DOME outline.
        stripe_top = top_y + 2 * SS
        stripe_bot = bot_y - 2 * SS
        pygame.draw.line(sub, DOME,
                         (cx_l, stripe_top), (cx_l, stripe_bot), SS)

    rot = pygame.transform.rotate(sub, ang_deg)
    rect = rot.get_rect(center=(cx, cy))
    big.blit(rot, rect.topleft)
    return rect


# ---------------------------------------------------------------------------
# Gameplay-scale composite — Pip head + helmet at the in-game blit offset.
# The helmet rides at `(pip_x + 18, pip_y - 10)` relative to Pip's centre
# in the gravity-down case (entities.py:815-816); replicate verbatim.
# ---------------------------------------------------------------------------

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
# vs-REF silhouette delta — round-2's most useful chrome addition. The
# delta column tints any pixel that lies OUTSIDE the REF helmet's solid
# dome mask, so the ear silhouette stands out against the baseline.
# ---------------------------------------------------------------------------


def _ref_outline_silhouette():
    """REF helmet dome OUTLINE only — used as the backdrop of the delta
    column. The variant's silhouette is tinted on top."""
    out = pygame.Surface(
        (NATIVE_PANEL, NATIVE_PANEL), pygame.SRCALPHA)
    dome_w = HW_N
    dome_h = HH_N
    helm_w = dome_w + PAD_N * 2
    helm_h = HH_N + PAD_N * 2 + DROP_N + _ear_top_margin_n()
    silhouette = pygame.Surface((helm_w, helm_h), pygame.SRCALPHA)
    full = pygame.Rect(PAD_N,
                       _ear_top_margin_n() + PAD_N,
                       dome_w, dome_h * 2)
    pygame.draw.ellipse(silhouette, DOME, full, 1)
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
    """Compose vs-REF delta. REF dome outline + variant pixels tinted RED
    where they fall OUTSIDE the REF dome mask (= true silhouette delta)."""
    out = pygame.Surface((NATIVE_PANEL, NATIVE_PANEL), pygame.SRCALPHA)
    out.blit(ref_outline_surf, (0, 0))
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

    helm_canvas = pygame.Surface(
        (NATIVE_PANEL, NATIVE_PANEL), pygame.SRCALPHA)
    helm_rect = variant_helmet_surf.get_rect(
        center=(NATIVE_PANEL // 2 + 18, NATIVE_PANEL // 2 - 10))
    helm_canvas.blit(variant_helmet_surf, helm_rect.topleft)

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
# Sheet layout — one REF row + 5 variant rows. Round 3 drops the (a)/(b)
# split column from round 2 since every variant ships BONE-only this
# round, leaving more room for the 4x zoom and vs-REF delta.
# ---------------------------------------------------------------------------

ZOOM = 4
ZOOM_PANEL = NATIVE_PANEL * ZOOM
DELTA_PANEL = NATIVE_PANEL * 2


def _font(size, bold=False):
    try:
        return pygame.font.SysFont("DejaVu Sans", size, bold=bold)
    except Exception:
        return pygame.font.Font(None, size)


def _draw_native_with_caption(sheet, x, y, surf, caption):
    sheet.blit(surf, (x, y))
    cap_font = _font(11)
    cap = cap_font.render(caption, True, SUBLABEL)
    sheet.blit(cap, (x + (NATIVE_PANEL - cap.get_width()) // 2,
                     y + NATIVE_PANEL + 4))
    return y + NATIVE_PANEL + 4 + cap.get_height()


def _draw_ref_row(sheet, x, y, helmet_surf):
    """Reference row: single native + 4x zoom, no delta (delta vs self
    is empty by definition)."""
    PAD = 16
    LABEL_H = 50
    panel_h = LABEL_H + ZOOM_PANEL + PAD * 2 + 22
    panel_w = NATIVE_PANEL + PAD + ZOOM_PANEL + PAD * 2

    card = pygame.Rect(x, y, panel_w, panel_h)
    pygame.draw.rect(sheet, CARD_BG, card, border_radius=10)
    pygame.draw.rect(sheet, (44, 50, 60), card, 1, border_radius=10)

    font = _font(18, bold=True)
    lbl = font.render(
        "REF.  SHIPPED HELMET (no ears) — baseline only",
        True, LABEL)
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
    cap = cap_font.render(
        f"{ZOOM}x zoom  (no ears — baseline only)", True, SUBLABEL)
    sheet.blit(cap, (zoom_x + (ZOOM_PANEL - cap.get_width()) // 2,
                     zoom_y + ZOOM_PANEL + 4))
    return panel_h


def _draw_variant_row(sheet, x, y, code, name, blurb, variant,
                      ref_outline):
    """One variant row: native | 4x zoom | vs-REF delta. All BONE-only
    this round (per AD)."""
    PAD = 16
    LABEL_H = 50
    panel_h = LABEL_H + ZOOM_PANEL + PAD * 2 + 22
    panel_w = (NATIVE_PANEL + PAD + ZOOM_PANEL + PAD
               + DELTA_PANEL + PAD * 2)

    card = pygame.Rect(x, y, panel_w, panel_h)
    pygame.draw.rect(sheet, CARD_BG, card, border_radius=10)
    pygame.draw.rect(sheet, (44, 50, 60), card, 1, border_radius=10)

    font = _font(18, bold=True)
    lbl = font.render(f"{code}.  {name}", True, LABEL)
    sheet.blit(lbl, (card.left + PAD, card.top + 8))
    sub_font = _font(12)
    sub = sub_font.render(blurb, True, SUBLABEL)
    sheet.blit(sub, (card.left + PAD, card.top + 8 + lbl.get_height() + 2))

    helm, ear_bbox = _build_helmet(variant, draw_fin=True)
    composite = _composite_native(helm)

    native_y = card.top + LABEL_H + PAD + (ZOOM_PANEL - NATIVE_PANEL) // 2
    native_x = card.left + PAD
    _draw_native_with_caption(
        sheet, native_x, native_y, composite, "native (BONE-only)")

    zoom_x = native_x + NATIVE_PANEL + PAD
    zoom_y = card.top + LABEL_H + PAD
    zoom = pygame.transform.scale(composite, (ZOOM_PANEL, ZOOM_PANEL))
    sheet.blit(zoom, (zoom_x, zoom_y))
    cap_font = _font(12)
    cap = cap_font.render(f"{ZOOM}x zoom", True, SUBLABEL)
    sheet.blit(cap, (zoom_x + (ZOOM_PANEL - cap.get_width()) // 2,
                     zoom_y + ZOOM_PANEL + 4))

    delta_x = zoom_x + ZOOM_PANEL + PAD
    delta_y = card.top + LABEL_H + PAD + (ZOOM_PANEL - DELTA_PANEL) // 2
    delta_native = _delta_overlay(helm, ref_outline)
    delta_zoom = pygame.transform.scale(
        delta_native, (DELTA_PANEL, DELTA_PANEL))
    sheet.blit(delta_zoom, (delta_x, delta_y))
    pygame.draw.rect(sheet, (44, 50, 60),
                     pygame.Rect(delta_x, delta_y,
                                 DELTA_PANEL, DELTA_PANEL), 1)
    cap2 = cap_font.render("vs-REF delta", True, SUBLABEL)
    sheet.blit(cap2, (delta_x + (DELTA_PANEL - cap2.get_width()) // 2,
                      delta_y + DELTA_PANEL + 4))

    if ear_bbox is not None:
        x0, y0, x1, y1 = ear_bbox
        # Dome's widest contour is x in [PAD_N, PAD_N + HW_N] at native.
        # For X5 we want max_x > PAD_N + HW_N (right ear) and min_x <
        # PAD_N (left ear).
        dome_left  = PAD_N
        dome_right = PAD_N + HW_N
        helmet_equator_n = _ear_top_margin_n() + PAD_N + HH_N // 2
        print(
            f"{code} ear bbox (native px, helmet subsurface): "
            f"x [{x0:.1f}, {x1:.1f}]  "
            f"y [{y0:.1f}, {y1:.1f}]  "
            f"| dome x-extent [{dome_left}, {dome_right}]  "
            f"helmet-equator y={helmet_equator_n}  "
            f"horizontal-break? "
            f"left={'yes' if x0 < dome_left else 'no'} "
            f"right={'yes' if x1 > dome_right else 'no'}  "
            f"tips-at-or-below-equator? "
            f"{'yes' if y1 >= helmet_equator_n else 'no'}"
        )
    return panel_h


VARIANTS = [
    ("X1", "W1 CHUNKY SPLAY +1 BASE",
     "runner-up: trapezoid splay, base +1 nat px (>=4), tip >=2, +/-28 deg."),
    ("X2", "W3 FATTENED  (lead candidate)",
     "AD lead: 5-vertex polygon, base +1 nat px (>=4), tip >=2, +/-15 deg."),
    ("X3", "W3 EXTRA-WIDE",
     "polygon w/ base +2 nat px (>=5) — tests how chunky we can push."),
    ("X4", "W3 CARTILAGE",
     "X2 silhouette + single 1-nat-px DOME stripe down each ear centre."),
    ("X5", "TRUE LOP",
     "re-rolled W4: ears bend 75 deg from vertical, tips at/below equator."),
]


def main():
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    pygame.init()

    PAD = 16
    TITLE_H = 96

    ref_helm, _ = _build_helmet("NONE", draw_fin=True)
    ref_outline = _ref_outline_silhouette()

    # Variant rows: native | 4x zoom | vs-REF delta. Sheet width follows
    # the brief's 880 px requirement, with the variant panel sized to fit.
    variant_panel_w = (NATIVE_PANEL + PAD + ZOOM_PANEL + PAD
                       + DELTA_PANEL + PAD * 2)
    sheet_w = max(880, variant_panel_w + PAD * 2)
    ref_panel_w = NATIVE_PANEL + PAD + ZOOM_PANEL + PAD * 2
    panel_h = 50 + ZOOM_PANEL + PAD * 2 + 22
    sheet_h = TITLE_H + PAD + (panel_h + PAD) * (1 + len(VARIANTS))

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill(SHEET_BG)

    title_text = ("SKATEBOARD helmet ears  —  round 3 FINAL "
                  "(chunky lineup)")
    sub_text = ("Round 2 lead = W3 (low-poly polygon, BONE-only). "
                "Round 3 widens the bases and explores true-lop. "
                "Sheet ships to user after this round.")
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
    sub_lines = _wrap_text(sub_text, sub_font, target_title_w)

    sheet.blit(title, (PAD * 2, PAD + 4))
    line_y = PAD + 4 + title.get_height() + 4
    for line in sub_lines:
        rendered = sub_font.render(line, True, SUBLABEL)
        sheet.blit(rendered, (PAD * 2, line_y))
        line_y += rendered.get_height() + 1

    y = TITLE_H + PAD
    ref_x = (sheet_w - ref_panel_w) // 2
    _draw_ref_row(sheet, ref_x, y, ref_helm)
    y += panel_h + PAD

    var_x = (sheet_w - variant_panel_w) // 2
    for code, name, blurb in VARIANTS:
        _draw_variant_row(sheet, var_x, y, code, name, blurb, code,
                          ref_outline)
        y += panel_h + PAD

    out_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "docs", "skateboard_helmet_ears",
    )
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_3.png")
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
