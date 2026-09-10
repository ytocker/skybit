"""SKATEBOARD helmet ears — round 4 ICON-MATCH exploration sheet.

Round 3 shipped X2 (W3 FATTENED, BONE-only, no RED) as the AD's pick.
User's reaction killed that direction outright: they want the SAME bunny
ears the pickup icon uses — BONE outer ellipse + DOME outline + RED inner
ellipse tip + +/-12 deg tilt. The 8-second skateboard power-up is a
punk-themed short fun event; visual loudness is the brief.

Round-1 V1 already attempted an ICON-MATCH port and failed because the
helmet's SS=4 supersample blurred the 3-native-px RED inner ellipse into
a smudge through smoothscale. Round 4's fix:

  * Render the helmet at SS=8 (DOUBLE the live SS=4). The big-surface is
    2x larger so the RED inner ellipse has 2x the source resolution to
    survive smoothscale to the same native 32x51 destination.
  * Physically enlarge the ear footprint across 5 sizes so the inner RED
    ellipse spans >=3 native px in every dimension after smoothscale.

Lineup, all ICON-PALETTE (BONE/DOME/RED), all +/-12 deg tilt, all using
the icon's `local.inflate(-2.5*SS, -8*SS)` inner-RED recipe scaled to
each variant's ear size:

  F1. ICON-PROPORTIONS — exact icon ratios scaled to helmet. Native ear
                          ~ 4x16 px, inner RED ~ 2x12 px. Literal port.
  F2. ICON-PLUS         — modestly chunkier. Native ear ~ 5x17 px,
                          inner RED ~ 3x12 px.
  F3. ICON-CHUNKY       — punk-weight. Native ear ~ 6x18 px, inner RED
                          ~ 3x11 px. The "not too narrow" feedback target.
  F4. ICON-XL           — maximum punk impact. Native ear ~ 7x21 px,
                          inner RED ~ 4x13 px (icon's literal 7x28 ratio).
  F5. ICON-CHUNKY + BOW — F3's chunky ears + RED bandana bow at the
                          LEFT-ear base, mirroring the icon's full styling.

Layout per row: [native composite] [4x zoom] [vs-REF silhouette delta].
REF row at top: shipped helmet with NO ears as baseline.

Run headless:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \\
        python3 tools/render_helmet_ear_variants_round_4.py
"""

import os
import sys
import pygame

# Project import — Pip head for the gameplay-scale composite.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from game import parrot  # noqa: E402


# ---------------------------------------------------------------------------
# Palette — LOCKED. Same five colours the pickup icon uses, plus the card
# backdrop. Foreign hues would break the kit identity the user signed off
# on by name ("the SAME bunny ears that are in the icon").
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
DELTA_TINT = (200, 50, 50)


# ---------------------------------------------------------------------------
# Live-helmet construction — re-implemented from Bird._draw_helmet so the
# renderer doesn't need a Bird, and so the ear block can be injected before
# the final smoothscale, matching the in-game blit path.
#
# Round 4's KEY tweak: SS is bumped to 8 (live helmet uses SS=4). Every
# SS-relative metric in the helmet body scales naturally because each is
# already expressed in SS units. The native destination size stays the
# same (32x51 helmet subsurface), but the source big-surface is 2x larger,
# so the RED inner ellipse — which was 3 native px and AA-smudged at SS=4
# — now resolves cleanly through smoothscale.
# ---------------------------------------------------------------------------

SS = 8         # 2x the live helmet SS, so RED inner ellipse survives downscale.
HW_N = 24      # native dome width.
HH_N = 15      # native dome height.
PAD_N = 4      # native padding around the dome.
DROP_N = 28    # native chinstrap drop region under the dome.


def _ear_top_margin_n() -> int:
    """Native pixels of headroom above the dome so tall ears don't get
    cropped at the top edge of the helmet subsurface. Round 4 keeps the
    same 14-px headroom that round 3 used; the ICON-XL apex (taller than
    round-3 ears) still clears it after the +/-12 deg tilt."""
    return 14


# ---------------------------------------------------------------------------
# Ear sizing table. Native pixels per variant; the supersample build then
# multiplies by SS. The icon's inner-RED inset (-2.5 SS x, -8 SS y) is
# applied in the variant's OWN supersample space so the proportional shape
# of the red tip is preserved across sizes.
#
# Footprint == the icon ellipse's NATIVE bounding-rect (er.width x er.height
# in native px) before tilt. Slight clipping at corners after rotation is
# expected; smoothscale and the BONE/DOME outline absorb it.
# ---------------------------------------------------------------------------

EAR_SPECS = {
    # (ear_w_n, ear_h_n, anchor_dx_n, anchor_dy_n)
    # anchor offsets are from the dome's top-centre, native px.
    "F1": (4, 16,  4, -3),
    "F2": (5, 17,  4, -3),
    "F3": (6, 18,  5, -3),
    "F4": (7, 21,  5, -4),
    "F5": (6, 18,  5, -3),   # same body as F3 + bow on left ear.
}


def _build_helmet(variant: str, draw_fin: bool = True):
    """Build the live skater helmet surface and overlay the requested ear
    variant before the final smoothscale, mirroring the in-game path.

    Returns (native_surf, diagnostics). `diagnostics` is a dict with
    `ear_bbox` (in native helmet-subsurface coords), `red_pixel_count`
    (RED pixels surviving in the FINAL native surf), and
    `ear_base_width_n` (sample width across the ear base in native px,
    measured by scanning a horizontal line near the ear base on the
    native surf and counting BONE-coloured pixels).
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

    # Dome body — single ellipse, top half only (cap shape).
    full = pygame.Surface((hw, hh * 2), pygame.SRCALPHA)
    pygame.draw.ellipse(full, DOME, pygame.Rect(0, 0, hw, hh * 2))
    helm.blit(full, (pad, Y(pad)), area=pygame.Rect(0, 0, hw, hh))

    # Highlight ellipse in the right-front quadrant of the dome.
    if hw > 9 * SS and hh > 5 * SS:
        hl_w = hw - 8 * SS
        hl_h = hh - 4 * SS
        hl = pygame.Surface((hl_w, hl_h), pygame.SRCALPHA)
        pygame.draw.ellipse(hl, (50, 50, 60),
                            pygame.Rect(0, 0, hl_w, hl_h))
        helm.blit(hl, (pad + 4 * SS, Y(pad + 1 * SS)),
                  area=pygame.Rect(hl_w // 2, 0,
                                   hl_w // 2, hl_h // 2 + 1))

    # Mohawk fin — sits between the ears, kept under every variant so the
    # punk silhouette stays consistent with the shipped helmet.
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

    # Rim line + chrome strip + skull decal.
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

    # Chinstrap + buckle. Sub-millimetre details but they anchor the
    # whole composition; dropping them makes the helmet look unfinished.
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

    # Ear block.
    dome_top_cx = pad + hw // 2
    dome_top_y  = Y(pad)
    ear_bbox_ss = None
    if variant != "NONE":
        ear_bbox_ss = _draw_ears(helm, variant, dome_top_cx, dome_top_y)

    # Final smoothscale to the native helmet-subsurface size. The
    # destination is identical to the live in-game helmet (so the
    # composite reads at the same scale as gameplay); the source is
    # 2x larger thanks to SS=8 so the RED tip survives downscale.
    native_w = HW_N + PAD_N * 2
    native_h = HH_N + PAD_N * 2 + DROP_N + _ear_top_margin_n()
    helm_native = pygame.transform.smoothscale(helm, (native_w, native_h))

    # Diagnostics — count surviving RED pixels and sample the ear base.
    diagnostics = _analyse_native(helm_native, variant)
    if ear_bbox_ss is not None:
        x0, y0, x1, y1 = ear_bbox_ss
        diagnostics["ear_bbox"] = (
            x0 / SS, y0 / SS, x1 / SS, y1 / SS,
        )
    else:
        diagnostics["ear_bbox"] = None
    return helm_native, diagnostics


# ---------------------------------------------------------------------------
# Ear draw — direct port of the pickup icon's ear recipe (entities.py
# 2276-2294) at the helmet's SS=8 supersample. Both ears are built in a
# local subsurface, then rotated +/-12 deg, then blitted at the dome top.
# F5 additionally draws a RED bandana bow at the left ear's base.
# ---------------------------------------------------------------------------


def _draw_ears(helm, variant, dome_top_cx, dome_top_y):
    """Overlay the requested ear pair onto the helmet supersurface.
    Returns the SS-canvas bounding box of all ear pixels for diagnostics.
    """
    ear_w_n, ear_h_n, dx_n, dy_n = EAR_SPECS[variant]
    ear_w = ear_w_n * SS
    ear_h = ear_h_n * SS

    rects = []
    ear_centres = {}
    for sign in (-1, 1):
        cx = dome_top_cx + sign * dx_n * SS
        cy = dome_top_y + dy_n * SS

        ear_sub = pygame.Surface(
            (ear_w + 4 * SS, ear_h + 4 * SS), pygame.SRCALPHA)
        local = pygame.Rect(0, 0, ear_w, ear_h)
        local.center = (ear_sub.get_width() // 2,
                        ear_sub.get_height() // 2)
        # BONE outer ellipse + DOME outline — exact icon recipe.
        pygame.draw.ellipse(ear_sub, BONE, local)
        pygame.draw.ellipse(ear_sub, DOME, local,
                            max(1, int(1.2 * SS)))
        # RED inner ellipse — icon's `local.inflate(-2.5*SS, -8*SS)`. The
        # inflate inputs are in the variant's OWN supersample space, so
        # the inner ellipse stays proportional across F1..F5.
        inner = local.inflate(-int(2.5 * SS), -int(8 * SS))
        pygame.draw.ellipse(ear_sub, RED, inner)

        ang = -12 * sign  # icon-exact tilt; signs mirror left/right.
        rot = pygame.transform.rotate(ear_sub, ang)
        rect = rot.get_rect(center=(cx, cy))
        helm.blit(rot, rect.topleft)
        rects.append(rect)
        ear_centres[sign] = (cx, cy)

    # F5: bandana bow at the LEFT ear's base. Direct port of the icon's
    # bow recipe (entities.py 2362-2381). The icon uses SS=6; we use SS=8
    # here, so the helper constants (bow_w, bow_h, knot_r, the 0.5/3/5/11
    # offsets) stay in SS units and the bow naturally scales up.
    if variant == "F5":
        knot_cx, knot_cy = ear_centres[-1]
        # Ear-base offset matches the icon recipe (knot under the ear,
        # slightly inward toward the helmet centre). The 11 SS y-shift
        # ports the icon constant; in helmet space this lands the bow at
        # the BONE-RED-BONE base seam of the left ear.
        knot_cy = knot_cy + int(7 * SS)
        knot_cx = knot_cx + int(2 * SS)
        bow_w = int(5 * SS)
        bow_h = int(3 * SS)
        bow_left = [
            (knot_cx - bow_w, knot_cy - bow_h),
            (knot_cx - int(0.5 * SS), knot_cy),
            (knot_cx - bow_w, knot_cy + bow_h),
        ]
        bow_right = [
            (knot_cx + bow_w, knot_cy - bow_h),
            (knot_cx + int(0.5 * SS), knot_cy),
            (knot_cx + bow_w, knot_cy + bow_h),
        ]
        pygame.draw.polygon(helm, RED, bow_left)
        pygame.draw.polygon(helm, RED, bow_right)
        pygame.draw.circle(helm, RED, (knot_cx, knot_cy), int(1.5 * SS))
        pygame.draw.polygon(helm, DOME, bow_left, max(1, SS // 3))
        pygame.draw.polygon(helm, DOME, bow_right, max(1, SS // 3))
        # Bow lies outside the ear-rect bbox; widen the returned bbox
        # so the diagnostic prints reflect the actual silhouette mass.
        bow_rect = pygame.Rect(
            knot_cx - bow_w, knot_cy - bow_h,
            bow_w * 2, bow_h * 2,
        )
        rects.append(bow_rect)

    if not rects:
        return None
    x0 = min(r.left  for r in rects)
    y0 = min(r.top   for r in rects)
    x1 = max(r.right for r in rects)
    y1 = max(r.bottom for r in rects)
    return (x0, y0, x1, y1)


# ---------------------------------------------------------------------------
# Diagnostics — scan the FINAL native surface to confirm the RED inner
# ellipse survives smoothscale and to sample the ear base width.
# ---------------------------------------------------------------------------


def _analyse_native(helm_native, variant):
    """Count RED-tinted pixels and sample ear-base widths on the native
    helmet surface. The RED check accepts any pixel close to the RED
    palette colour after AA blending; smoothscale typically dims/desats
    the inner ellipse so we use a generous tolerance."""
    diag = {"red_pixel_count": 0, "ear_base_width_n": 0}
    if variant == "NONE":
        return diag
    w, h = helm_native.get_size()
    helm_native.lock()
    try:
        red_count = 0
        for x in range(w):
            for y in range(h):
                r, g, b, a = helm_native.get_at((x, y))
                if a < 80:
                    continue
                # RED palette is (200, 50, 50). After AA blending the
                # exact tuple is rare, so the test is "channel ratios
                # roughly RED-dominant" with R high and G/B both low.
                if r >= 130 and g <= 110 and b <= 110 and r - max(g, b) >= 30:
                    red_count += 1
        diag["red_pixel_count"] = red_count

        # Ear-base width sample: scan a horizontal line through the
        # ear-base region (just above the dome top) and count the longest
        # contiguous run of opaque pixels on the LEFT half (= left ear).
        ear_top_n = _ear_top_margin_n()
        # Sample 2 native rows below the topmost pixel of the ear bbox so
        # we're solidly inside the ear shape, not the AA fringe.
        # Walk down rows from y=0 to ear_top_n + PAD_N looking for the
        # widest opaque run on the left half of the helmet width.
        best_left = 0
        for y in range(0, ear_top_n + PAD_N + 4):
            run = 0
            best_in_row = 0
            for x in range(0, w // 2):
                _, _, _, a = helm_native.get_at((x, y))
                if a > 40:
                    run += 1
                    if run > best_in_row:
                        best_in_row = run
                else:
                    run = 0
            if best_in_row > best_left:
                best_left = best_in_row
        diag["ear_base_width_n"] = best_left
    finally:
        helm_native.unlock()
    return diag


# ---------------------------------------------------------------------------
# Gameplay-scale composite — Pip head + helmet at the in-game blit offset
# (entities.py:815-816). Helmet rides at (pip_x + 18, pip_y - 10).
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
# vs-REF silhouette delta — pixels of the variant that fall OUTSIDE the
# REF helmet's solid dome silhouette get tinted RED.
# ---------------------------------------------------------------------------


def _ref_outline_silhouette():
    """REF helmet dome OUTLINE only — backdrop for the delta column."""
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
# Sheet layout — REF row at the top + 5 ICON-MATCH variants.
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
    """REF row: single native + 4x zoom, no delta (delta vs self is
    empty by definition)."""
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
    """One variant row: native | 4x zoom | vs-REF delta."""
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

    helm, diag = _build_helmet(variant, draw_fin=True)
    composite = _composite_native(helm)

    native_y = card.top + LABEL_H + PAD + (ZOOM_PANEL - NATIVE_PANEL) // 2
    native_x = card.left + PAD
    _draw_native_with_caption(
        sheet, native_x, native_y, composite, "native (icon-style)")

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

    red = diag["red_pixel_count"]
    base_w = diag["ear_base_width_n"]
    print(
        f"{code}  RED pixels (native): {red:3d}  | "
        f"left-ear base width sample: {base_w} native px  | "
        f"bbox: {diag['ear_bbox']}"
    )
    return panel_h


VARIANTS = [
    ("F1", "ICON-PROPORTIONS",
     "exact icon ratios. ear ~ 4x16 nat px, RED inner ~ 2x12 nat px."),
    ("F2", "ICON-PLUS",
     "modestly chunkier. ear ~ 5x17 nat px, RED inner ~ 3x12 nat px."),
    ("F3", "ICON-CHUNKY",
     "punk-weight: ear ~ 6x18 nat px, RED inner ~ 3x11 nat px."),
    ("F4", "ICON-XL",
     "max punk impact. ear ~ 7x21 nat px, RED inner ~ 4x13 nat px."),
    ("F5", "ICON-CHUNKY + BANDANA BOW",
     "F3 ears + RED bandana bow at LEFT ear base — full icon styling."),
]


def main():
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    pygame.init()

    PAD = 16
    TITLE_H = 96

    ref_helm, _ = _build_helmet("NONE", draw_fin=True)
    ref_outline = _ref_outline_silhouette()

    variant_panel_w = (NATIVE_PANEL + PAD + ZOOM_PANEL + PAD
                       + DELTA_PANEL + PAD * 2)
    sheet_w = max(880, variant_panel_w + PAD * 2)
    ref_panel_w = NATIVE_PANEL + PAD + ZOOM_PANEL + PAD * 2
    panel_h = 50 + ZOOM_PANEL + PAD * 2 + 22
    sheet_h = TITLE_H + PAD + (panel_h + PAD) * (1 + len(VARIANTS))

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill(SHEET_BG)

    title_text = ("SKATEBOARD helmet ears  —  round 4 "
                  "(ICON-MATCH, red-tipped)")
    sub_text = ("Punk-themed power-up: bringing back the icon's full "
                "BONE + DOME + RED ear styling. 5 sizes, pick the "
                "chunkiest read.")
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
    out_path = os.path.join(out_dir, "round_4.png")
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
