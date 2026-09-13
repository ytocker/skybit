"""SKATEBOARD helmet ears — round 5 (seated + bent-tip mix).

Round 4 shipped ICON-MATCH red-tipped ears at +/-12 deg tilt but introduced
two regressions plus left one open question:

  1. The helmet visibly dropped onto Pip's face. Round 3->4 added 14 native
     px of top headroom to the helmet subsurface so tall ears wouldn't
     clip, but didn't shift the blit anchor down to compensate — so the
     subsurface's geometric centre moved DOWN by 7 px and the dome bottom
     buried Pip's eye/beak.

  2. User wanted bent / flopped ear tips (Holland-lop droop) mixed in with
     the straight icon-port — not all variants, just some.

  3. User wanted chunkier / wider ears alongside round 4's 6x18.

Round 5 addresses all three:

  * ANCHOR FIX. When ear_top > 0 the helmet blit centre is shifted UP by
    ear_top / 2 native px. REF (ear_top=0) lands at the live game's
    centery - 10; G1..G5 (ear_top=18) land at centery - 10 - 9 = -19, so
    the dome bottom sits at the SAME on-Pip y as REF +/-1 px. Live helmet
    seating is preserved while the taller subsurface holds the bent tips.

  * BENT-TIP HELPER. _draw_ear_bent_tip composes the ear from two pieces:
    a lower BONE+DOME+RED ellipse (~65% of the ear height), plus an upper
    BONE+DOME tip ellipse rotated outward at the fold angle. The lower
    half stays upright; only the upper segment flops. Then the WHOLE ear
    is tilted +/-12 deg as round 4 did, so the fold reads on top of the
    base tilt — exactly the Holland-lop silhouette the user asked for.

  * WIDTH MIX. G2 widens to 8x18 (straight). G4 widens to 8x20 (bent).
    G1 keeps round-4's 6x18 control. G3/G5 keep 6x18 + fold for direct
    side-by-side with G4's wider fold.

Lineup, all ICON palette, all +/-12 deg tilt:

  G1. STRAIGHT CHUNKY  — control, identical body to round-4 F3 (6x18),
                          re-seated.
  G2. STRAIGHT WIDE    — width-only experiment, 8x18, no fold.
  G3. BENT-TIP MID     — 6x18 with top 35% folded outward at 55 deg.
  G4. BENT-TIP WIDE    — 8x20 with top 35% folded outward at 60 deg.
  G5. BENT-TIP + BOW   — G3 (6x18 bent) + RED bandana bow at LEFT ear base.

REF row at top: shipped helmet (no ears), also re-seated via the anchor
fix (ear_top=0 so the shift is a no-op — confirms REF still matches
the live game's centery - 10 anchor exactly).

Run headless:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \\
        python3 tools/render_helmet_ear_variants_round_5.py
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
# SS stays at 8 (DOUBLE the live SS=4) so the inner RED ellipse survives
# smoothscale to the native destination at every ear width.
# ---------------------------------------------------------------------------

SS = 8         # 2x the live helmet SS, so RED inner ellipse survives downscale.
HW_N = 24      # native dome width.
HH_N = 15      # native dome height.
PAD_N = 4      # native padding around the dome.
DROP_N = 28    # native chinstrap drop region under the dome.

# Round 5: headroom above the dome. 18 native px holds the tallest G4
# (8x20) ear at fold + +/-12 deg tilt with margin. Tracked separately so
# the anchor-fix shift is exact.
EAR_TOP_N = 18


def _ear_top_margin_n() -> int:
    return EAR_TOP_N


# ---------------------------------------------------------------------------
# Ear sizing table for round 5. Bent-tip variants get a fold angle in
# degrees; straight variants get fold=0. Footprint == lower-ellipse
# native bounding-rect before tilt.
# ---------------------------------------------------------------------------

EAR_SPECS = {
    # (ear_w_n, ear_h_n, anchor_dx_n, anchor_dy_n, fold_deg, has_bow)
    "G1": (6, 18, 5, -3,  0, False),  # STRAIGHT CHUNKY
    "G2": (8, 18, 5, -3,  0, False),  # STRAIGHT WIDE
    "G3": (6, 18, 5, -3, 55, False),  # BENT-TIP MID
    "G4": (8, 20, 5, -4, 60, False),  # BENT-TIP WIDE
    "G5": (6, 18, 5, -3, 55, True),   # BENT-TIP MID + BOW
}


def _build_helmet(variant: str, draw_fin: bool = True):
    """Build the live skater helmet surface and overlay the requested ear
    variant before the final smoothscale, mirroring the in-game path.

    Returns (native_surf, diagnostics). `diagnostics` exposes ear_bbox,
    red_pixel_count, ear_base_width_n, and the dome bottom y in NATIVE
    coords (for the anchor-fix audit).
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
    dome_bottom_y_ss = Y(pad + hh - 1)
    ear_bbox_ss = None
    if variant != "NONE":
        ear_bbox_ss = _draw_ears(helm, variant, dome_top_cx, dome_top_y)

    # Final smoothscale to the native helmet-subsurface size. Source is
    # 2x larger than the live helmet thanks to SS=8 so the RED inner
    # ellipse survives downscale at every ear width.
    native_w = HW_N + PAD_N * 2
    native_h = HH_N + PAD_N * 2 + DROP_N + _ear_top_margin_n()
    helm_native = pygame.transform.smoothscale(helm, (native_w, native_h))

    diagnostics = _analyse_native(helm_native, variant)
    diagnostics["dome_bottom_y_native"] = dome_bottom_y_ss / SS
    if ear_bbox_ss is not None:
        x0, y0, x1, y1 = ear_bbox_ss
        diagnostics["ear_bbox"] = (
            x0 / SS, y0 / SS, x1 / SS, y1 / SS,
        )
    else:
        diagnostics["ear_bbox"] = None
    return helm_native, diagnostics


# ---------------------------------------------------------------------------
# Ear constructors.
#
# _draw_ear_straight: round 4's single-ellipse port (BONE + DOME + RED).
# Used for G1 / G2.
#
# _draw_ear_bent_tip: composes two ellipses. Lower segment ~ 65% of the ear
# height carries the BONE + DOME + RED — this is what reads as "skater
# ear". Upper segment is a smaller BONE + DOME ellipse rotated outward at
# the fold angle, blitted with its midbottom attached at the lower
# segment's top. Whole composite is then tilted +/-12 deg outward to match
# the icon's base posture.
# ---------------------------------------------------------------------------


def _draw_ear_straight(big, sign, cx, cy, ear_w_ss, ear_h_ss):
    """Round-4 single-ellipse ear, returned as a screen rect for bbox.
    `sign` mirrors left/right; `cx`,`cy` are the helmet-canvas anchor."""
    ear_sub = pygame.Surface(
        (ear_w_ss + 4 * SS, ear_h_ss + 4 * SS), pygame.SRCALPHA)
    local = pygame.Rect(0, 0, ear_w_ss, ear_h_ss)
    local.center = (ear_sub.get_width() // 2,
                    ear_sub.get_height() // 2)
    pygame.draw.ellipse(ear_sub, BONE, local)
    pygame.draw.ellipse(ear_sub, DOME, local, max(1, int(1.2 * SS)))
    inner = local.inflate(-int(2.5 * SS), -int(8 * SS))
    pygame.draw.ellipse(ear_sub, RED, inner)

    ang = -12 * sign
    rot = pygame.transform.rotate(ear_sub, ang)
    rect = rot.get_rect(center=(cx, cy))
    big.blit(rot, rect.topleft)
    return rect


def _draw_ear_bent_tip(big, sign, cx, cy, ear_w_ss, ear_h_ss, fold_deg):
    """Two-segment Holland-lop ear: upright lower BONE+DOME+RED ellipse +
    smaller upper BONE+DOME tip rotated outward at `fold_deg` AROUND THE
    TIP'S BASE (not its centre, so the tip stays attached). The whole
    composite then gets the +/-12 deg base tilt the icon uses, and the
    lower-ear BOTTOM lands at the same on-helmet y a straight ear would —
    so the seating fix carries cleanly across variants.

    (cx, cy) is the anchor that would hold the CENTRE of a straight ear.
    """
    lower_h_ss = int(ear_h_ss * 0.65)
    tip_h_ss = (ear_h_ss - lower_h_ss) + int(2 * SS)   # 2 SS seam overlap
    tip_w_ss = max(2 * SS, int(ear_w_ss * 0.75))

    # Composite canvas — generous margin so both rotations have room.
    margin = ear_h_ss + 4 * SS
    comp_w = ear_w_ss + 2 * margin
    comp_h = ear_h_ss + 2 * margin
    comp = pygame.Surface((comp_w, comp_h), pygame.SRCALPHA)

    # Lower ellipse — placed so its bottom lands at the SAME y as where a
    # straight ear ellipse bottom would land after the base tilt is applied
    # to the composite. Since the composite centre will be placed at
    # (cx, cy) and a straight ear of height ear_h_ss spans cy +/- ear_h_ss/2,
    # set lower.bottom = comp_h/2 + ear_h_ss/2.
    lower_cx = comp_w // 2
    lower_bottom = comp_h // 2 + ear_h_ss // 2
    lower_top = lower_bottom - lower_h_ss
    lower_rect = pygame.Rect(0, 0, ear_w_ss, lower_h_ss)
    lower_rect.center = (lower_cx, lower_top + lower_h_ss // 2)
    pygame.draw.ellipse(comp, BONE, lower_rect)
    pygame.draw.ellipse(comp, DOME, lower_rect, max(1, int(1.2 * SS)))
    inner = lower_rect.inflate(-int(2.5 * SS), -int(6 * SS))
    pygame.draw.ellipse(comp, RED, inner)

    # Tip surface — draw the tip ellipse with its MIDBOTTOM at the tip_sub
    # geometric centre, so `pygame.transform.rotate` (which pivots around
    # the surface centre) pivots around the tip's BASE point. After
    # rotation the tip stays "hinged" at the base instead of swinging out
    # by an offset.
    tip_pad = 4 * SS
    tip_sub_w = tip_w_ss + 2 * tip_pad
    tip_sub_h = tip_h_ss * 2 + 2 * tip_pad  # double so midbottom is at centre
    tip_sub = pygame.Surface((tip_sub_w, tip_sub_h), pygame.SRCALPHA)
    tip_rect = pygame.Rect(0, 0, tip_w_ss, tip_h_ss)
    tip_rect.midbottom = (tip_sub_w // 2, tip_sub_h // 2)
    pygame.draw.ellipse(tip_sub, BONE, tip_rect)
    pygame.draw.ellipse(tip_sub, DOME, tip_rect, max(1, int(1.2 * SS)))

    # Rotate the tip; pivot is the surface centre, which is the tip's BASE.
    tip_rot = pygame.transform.rotate(tip_sub, -fold_deg * sign)
    # Blit so the rotated surface CENTRE lands at the lower ellipse's top —
    # i.e. the tip's BASE attaches to the lower's top exactly.
    tip_rotrect = tip_rot.get_rect(center=(lower_cx, lower_top))
    comp.blit(tip_rot, tip_rotrect)

    # Base tilt for the whole ear — same as the straight-ear path.
    ang = -12 * sign
    rot = pygame.transform.rotate(comp, ang)
    rect = rot.get_rect(center=(cx, cy))
    big.blit(rot, rect.topleft)
    return rect


def _draw_ears(helm, variant, dome_top_cx, dome_top_y):
    """Overlay the requested ear pair onto the helmet supersurface.
    Returns the SS-canvas bounding box of all ear pixels for diagnostics.
    """
    ear_w_n, ear_h_n, dx_n, dy_n, fold_deg, has_bow = EAR_SPECS[variant]
    ear_w = ear_w_n * SS
    ear_h = ear_h_n * SS

    rects = []
    ear_centres = {}
    for sign in (-1, 1):
        cx = dome_top_cx + sign * dx_n * SS
        cy = dome_top_y + dy_n * SS

        if fold_deg == 0:
            rect = _draw_ear_straight(helm, sign, cx, cy, ear_w, ear_h)
        else:
            rect = _draw_ear_bent_tip(
                helm, sign, cx, cy, ear_w, ear_h, fold_deg)
        rects.append(rect)
        ear_centres[sign] = (cx, cy)

    # Bandana bow at LEFT ear base — port of game/entities.py:2362-2381.
    # The bow lives at the ear BASE and does NOT bend with the tip, so it
    # reads independently of the fold. Round 4's F5 used 7*SS / 2*SS for
    # the y/x offsets at SS=8; we keep that here (the SS=4 icon recipe's
    # 11*SS / 3*SS scaled to SS=8 lands a bit low, so the 7/2 round-4
    # tweak is the version that visually attaches at the base seam).
    if has_bow:
        knot_cx, knot_cy = ear_centres[-1]
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
                if r >= 130 and g <= 110 and b <= 110 and r - max(g, b) >= 30:
                    red_count += 1
        diag["red_pixel_count"] = red_count

        ear_top_n = _ear_top_margin_n()
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
# (entities.py:815-816), PLUS the round-5 anchor fix: shift center y up by
# ear_top / 2 so the larger headroom doesn't push the dome onto Pip's face.
# ---------------------------------------------------------------------------

NATIVE_PANEL = 96


def _composite_native(helmet_surf, ear_top_n):
    canvas = pygame.Surface((NATIVE_PANEL, NATIVE_PANEL), pygame.SRCALPHA)
    pip = parrot.get_parrot(0, 0.0)
    pip_rect = pip.get_rect(center=(NATIVE_PANEL // 2,
                                    NATIVE_PANEL // 2))
    canvas.blit(pip, pip_rect.topleft)
    # ANCHOR FIX: live helmet sits at centery - 10. When the helmet
    # subsurface has ear_top px of extra headroom on top, the subsurface's
    # geometric centre shifts DOWN by ear_top / 2, so we compensate by
    # shifting the blit centre UP by the same amount. For REF (ear_top=0)
    # this is a no-op and matches the live game exactly.
    center_y = pip_rect.centery - 10 - (ear_top_n / 2.0)
    helm_rect = helmet_surf.get_rect(
        center=(pip_rect.centerx + 18, center_y))
    canvas.blit(helmet_surf, helm_rect.topleft)
    # Returned anchor y is logged per-row as the seating audit.
    return canvas, helm_rect


# ---------------------------------------------------------------------------
# vs-REF silhouette delta — pixels of the variant that fall OUTSIDE the
# REF helmet's solid dome silhouette get tinted RED. Uses the same anchor
# fix so the REF silhouette and the variant land at matching dome-bottom
# coordinates.
# ---------------------------------------------------------------------------


def _ref_outline_silhouette(ear_top_n):
    out = pygame.Surface(
        (NATIVE_PANEL, NATIVE_PANEL), pygame.SRCALPHA)
    dome_w = HW_N
    dome_h = HH_N
    helm_w = dome_w + PAD_N * 2
    helm_h = HH_N + PAD_N * 2 + DROP_N + ear_top_n
    silhouette = pygame.Surface((helm_w, helm_h), pygame.SRCALPHA)
    full = pygame.Rect(PAD_N,
                       ear_top_n + PAD_N,
                       dome_w, dome_h * 2)
    pygame.draw.ellipse(silhouette, DOME, full, 1)
    silhouette.fill((0, 0, 0, 0),
                    pygame.Rect(0,
                                ear_top_n + PAD_N + dome_h,
                                helm_w, helm_h))
    pygame.draw.line(silhouette, DOME,
                     (PAD_N - 1,
                      ear_top_n + PAD_N + dome_h - 1),
                     (PAD_N + dome_w,
                      ear_top_n + PAD_N + dome_h - 1), 1)
    center_y = NATIVE_PANEL // 2 - 10 - (ear_top_n / 2.0)
    helm_rect = silhouette.get_rect(
        center=(NATIVE_PANEL // 2 + 18, center_y))
    out.blit(silhouette, helm_rect.topleft)
    return out


def _delta_overlay(variant_helmet_surf, ref_outline_surf, ear_top_n):
    out = pygame.Surface((NATIVE_PANEL, NATIVE_PANEL), pygame.SRCALPHA)
    out.blit(ref_outline_surf, (0, 0))
    ref_solid = pygame.Surface(
        (NATIVE_PANEL, NATIVE_PANEL), pygame.SRCALPHA)
    dome_w = HW_N
    dome_h = HH_N
    helm_w = dome_w + PAD_N * 2
    helm_h = HH_N + PAD_N * 2 + DROP_N + ear_top_n
    silhouette = pygame.Surface((helm_w, helm_h), pygame.SRCALPHA)
    full = pygame.Rect(PAD_N,
                       ear_top_n + PAD_N,
                       dome_w, dome_h * 2)
    pygame.draw.ellipse(silhouette, (255, 255, 255), full)
    silhouette.fill((0, 0, 0, 0),
                    pygame.Rect(0,
                                ear_top_n + PAD_N + dome_h,
                                helm_w, helm_h))
    center_y = NATIVE_PANEL // 2 - 10 - (ear_top_n / 2.0)
    ref_rect = silhouette.get_rect(
        center=(NATIVE_PANEL // 2 + 18, center_y))
    ref_solid.blit(silhouette, ref_rect.topleft)

    helm_canvas = pygame.Surface(
        (NATIVE_PANEL, NATIVE_PANEL), pygame.SRCALPHA)
    helm_rect = variant_helmet_surf.get_rect(
        center=(NATIVE_PANEL // 2 + 18, center_y))
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
# Sheet layout — REF row at the top + 5 round-5 variants.
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


def _draw_ref_row(sheet, x, y, helmet_surf, ear_top_n):
    PAD = 16
    LABEL_H = 50
    panel_h = LABEL_H + ZOOM_PANEL + PAD * 2 + 22
    panel_w = NATIVE_PANEL + PAD + ZOOM_PANEL + PAD * 2

    card = pygame.Rect(x, y, panel_w, panel_h)
    pygame.draw.rect(sheet, CARD_BG, card, border_radius=10)
    pygame.draw.rect(sheet, (44, 50, 60), card, 1, border_radius=10)

    font = _font(18, bold=True)
    lbl = font.render(
        "REF.  SHIPPED HELMET (no ears) — re-seated baseline",
        True, LABEL)
    sheet.blit(lbl, (card.left + PAD, card.top + 8))
    sub_font = _font(12)
    sub = sub_font.render(
        "ear_top=0 -> blit anchor matches live game's centery - 10 exactly",
        True, SUBLABEL)
    sheet.blit(sub, (card.left + PAD, card.top + 8 + lbl.get_height() + 2))

    # REF is rendered with ear_top=0 so the anchor-fix shift is a no-op.
    composite, helm_rect = _composite_native(helmet_surf, ear_top_n=0)
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
    print(
        f"REF  anchor y (post-fix): {helm_rect.centery}  | "
        f"dome bottom on Pip y ~ {helm_rect.centery + 9} native px"
    )
    return panel_h


def _draw_variant_row(sheet, x, y, code, name, blurb, variant,
                      ref_outline, ear_top_n):
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
    composite, helm_rect = _composite_native(helm, ear_top_n=ear_top_n)

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
    delta_native = _delta_overlay(helm, ref_outline, ear_top_n)
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
    bbox = diag["ear_bbox"]
    bbox_w = (bbox[2] - bbox[0]) if bbox else 0
    print(
        f"{code}  anchor y (post-fix): {helm_rect.centery}  | "
        f"dome bottom on Pip y ~ {helm_rect.centery + 9 - ear_top_n // 2 + ear_top_n // 2} "
        f"| RED px: {red:3d}  | base w: {base_w}n  | "
        f"ear bbox: {bbox}  | bbox width: {bbox_w:.1f}n"
    )
    return panel_h


VARIANTS = [
    ("G1", "STRAIGHT CHUNKY",
     "control — 6x18 straight ellipse, +/-12 deg tilt (round-4 F3 re-seated)."),
    ("G2", "STRAIGHT WIDE",
     "width experiment — 8x18 straight ellipse, +/-12 deg tilt."),
    ("G3", "BENT-TIP MID",
     "6x18 ear, top 35% folds outward at 55 deg — Holland-lop droop."),
    ("G4", "BENT-TIP WIDE",
     "8x20 ear, top 35% folds outward at 60 deg — chunkier flop."),
    ("G5", "BENT-TIP + BANDANA BOW",
     "G3 bent-tip + RED bandana bow at LEFT ear base (bow stays at base)."),
]


def main():
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    pygame.init()

    PAD = 16
    TITLE_H = 96

    ref_helm, _ = _build_helmet("NONE", draw_fin=True)
    ref_outline = _ref_outline_silhouette(EAR_TOP_N)

    variant_panel_w = (NATIVE_PANEL + PAD + ZOOM_PANEL + PAD
                       + DELTA_PANEL + PAD * 2)
    sheet_w = max(880, variant_panel_w + PAD * 2)
    ref_panel_w = NATIVE_PANEL + PAD + ZOOM_PANEL + PAD * 2
    panel_h = 50 + ZOOM_PANEL + PAD * 2 + 22
    sheet_h = TITLE_H + PAD + (panel_h + PAD) * (1 + len(VARIANTS))

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill(SHEET_BG)

    title_text = ("SKATEBOARD helmet ears  —  round 5 "
                  "(seated + bent-tip mix)")
    sub_text = ("Round 5: helmet sits naturally on Pip again; "
                "5 variants explore width x bent-tip mix.")
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
    _draw_ref_row(sheet, ref_x, y, ref_helm, ear_top_n=0)
    y += panel_h + PAD

    var_x = (sheet_w - variant_panel_w) // 2
    for code, name, blurb in VARIANTS:
        _draw_variant_row(sheet, var_x, y, code, name, blurb, code,
                          ref_outline, ear_top_n=EAR_TOP_N)
        y += panel_h + PAD

    out_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "docs", "skateboard_helmet_ears",
    )
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_5.png")
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
