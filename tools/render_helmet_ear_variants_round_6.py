"""SKATEBOARD helmet — round 6 (skull-bunny face on the dome).

Round 5 picked G1 STRAIGHT CHUNKY ears as the locked treatment. Round 6
shifts the conversation FROM the ear silhouette TO the dome face: the
icon's punk skull-bunny face — bone skull body, dome eye sockets, dome
nose triangle, Jolly Roger mouth (3 tooth lines + 2 sine-arc dips), and
the signature RED bandage cross over the left eye — needs to land on the
helmet dome at gameplay scale WITHOUT pulling in the crossed skateboard
decks behind it (the helmet IS the skater wearing the kit, not the icon).

Donor: tools/render_helmet_ear_variants_round_5.py. Re-uses the helmet
body draw at SS=8, the anchor-fix (shift centre y up by ear_top / 2 when
the subsurface gains headroom), the G1 ear draw, and the sheet layout.

CHANGES vs round 5:

  * Removed the small placeholder skull decal at the chrome strip
    (round 5 _build_helmet lines 185-190). The dome face owns that
    real estate now.

  * New `_draw_face(helm, variant)` helper. Draws face elements in
    SS-space so they anti-alias the same way the dome does at the
    final smoothscale.

  * REF row is now G1 + NO FACE — so each H_ variant's vs-REF delta
    isolates the face pixels against the locked-ears baseline.

  * All H1..H5 use G1 ears verbatim from round 5. Ears are LOCKED.

Lineup:

  H1. FULL FACE         — skull body + 2 eyes + nose + mouth + bandage.
  H2. NO BANDAGE        — H1 minus the RED cross.
  H3. MASK STYLE        — eyes + nose + mouth, no skull body
                          (the dome substitutes for the skull silhouette).
  H4. EYE-PATCH PUNK    — H1 face, but the RED cross is positioned fully
                          OVER the left eye (covers it). Right eye + nose
                          + mouth visible; left eye omitted.
  H5. BIG FACE FILL     — H1 face stretched to fill the dome bbox more
                          aggressively (skull 22x13 native, squashed).

Run headless:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \\
        python3 tools/render_helmet_ear_variants_round_6.py
"""

import math
import os
import sys
import pygame

# Pip head for the gameplay-scale composite — same dependency as round 5.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from game import parrot  # noqa: E402


# ---------------------------------------------------------------------------
# Palette — LOCKED. Same five colours the pickup icon + helmet kit use.
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
# Helmet construction constants — straight port from round 5 so REF still
# lines up pixel-for-pixel with the G1 cell the user picked.
# ---------------------------------------------------------------------------
SS = 8
HW_N = 24
HH_N = 15
PAD_N = 4
DROP_N = 28
EAR_TOP_N = 18


def _ear_top_margin_n() -> int:
    return EAR_TOP_N


# Locked ear spec: only G1 from round 5. Face variants reuse this same
# ear pair across the board.
G1_EAR = (6, 18, 5, -3, 0, False)  # (ear_w, ear_h, dx, dy, fold, has_bow)


# ---------------------------------------------------------------------------
# Face spec — face element recipes ported from
# game/entities.py:_draw_skateboard_icon. Scaled down with FACE_NATIVE_SCALE
# so the icon's 44x38-native skull fits inside the helmet dome bbox.
# ---------------------------------------------------------------------------

# Icon skull native dims (SK_W, SK_H in entities.py). Round 6 shrinks them
# to fit the helmet dome — see FACE_NATIVE_SCALE.
ICON_SK_W = 44
ICON_SK_H = 38

# Default scale: shrink icon's 44x38 skull to ~17x15 native (fits dome).
FACE_NATIVE_SCALE = 0.395

# Dome-relative face anchor (subsurface coords, native px). Dome native
# bbox is (left=4, top=22, right=28, bottom=37) after the anchor fix; the
# face sits in the middle visible area, clear of the chrome strip.
DOME_CX_N = 16          # subsurface centre x.
DOME_CY_N = 30          # mid-dome y (slightly above chrome strip at 37).


# H1..H5 face spec. Each entry tells _draw_face which elements to draw and
# what skull dims to use. `bandage_mode` = "off" | "on_eye" | "covers_eye".
# `omit_left_eye` is True when the bandage fully covers the left socket so
# the underlying eye circle should be skipped.
FACE_SPECS = {
    "H1": {
        "skull_body": True,
        "skull_w_native": int(ICON_SK_W * FACE_NATIVE_SCALE),
        "skull_h_native": int(ICON_SK_H * FACE_NATIVE_SCALE),
        "draw_eyes": True,
        "draw_nose": True,
        "draw_mouth": True,
        "bandage_mode": "on_eye",
        "omit_left_eye": False,
    },
    "H2": {
        "skull_body": True,
        "skull_w_native": int(ICON_SK_W * FACE_NATIVE_SCALE),
        "skull_h_native": int(ICON_SK_H * FACE_NATIVE_SCALE),
        "draw_eyes": True,
        "draw_nose": True,
        "draw_mouth": True,
        "bandage_mode": "off",
        "omit_left_eye": False,
    },
    "H3": {
        "skull_body": False,
        "skull_w_native": int(ICON_SK_W * FACE_NATIVE_SCALE),
        "skull_h_native": int(ICON_SK_H * FACE_NATIVE_SCALE),
        "draw_eyes": True,
        "draw_nose": True,
        "draw_mouth": True,
        "bandage_mode": "off",
        "omit_left_eye": False,
    },
    "H4": {
        "skull_body": True,
        "skull_w_native": int(ICON_SK_W * FACE_NATIVE_SCALE),
        "skull_h_native": int(ICON_SK_H * FACE_NATIVE_SCALE),
        "draw_eyes": True,
        "draw_nose": True,
        "draw_mouth": True,
        "bandage_mode": "covers_eye",
        "omit_left_eye": True,
    },
    "H5": {
        # Stretched face fills the dome bbox horizontally.
        "skull_body": True,
        "skull_w_native": 22,
        "skull_h_native": 13,
        "draw_eyes": True,
        "draw_nose": True,
        "draw_mouth": True,
        "bandage_mode": "on_eye",
        "omit_left_eye": False,
    },
}


# ---------------------------------------------------------------------------
# Helmet body — straight copy from round 5, MINUS the placeholder skull
# decal (the dome face owns that real estate). _draw_face is the new
# helper; it runs after the body draws but before the ear block so the
# face never overdraws the ear silhouette.
# ---------------------------------------------------------------------------


def _build_helmet(variant: str, draw_fin: bool = True):
    """Build the helmet surface for round 6. `variant` selects the face
    spec ("H1".."H5"); ears are always G1 (or absent for REF).
    `variant` == "REF" means G1 ears + no face.
    `variant` == "NONE" means no ears + no face (legacy hook, unused).
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

    # Dome body.
    full = pygame.Surface((hw, hh * 2), pygame.SRCALPHA)
    pygame.draw.ellipse(full, DOME, pygame.Rect(0, 0, hw, hh * 2))
    helm.blit(full, (pad, Y(pad)), area=pygame.Rect(0, 0, hw, hh))

    # Highlight ellipse — kept so the helmet still reads as glossy plastic
    # under the new face decals.
    if hw > 9 * SS and hh > 5 * SS:
        hl_w = hw - 8 * SS
        hl_h = hh - 4 * SS
        hl = pygame.Surface((hl_w, hl_h), pygame.SRCALPHA)
        pygame.draw.ellipse(hl, (50, 50, 60),
                            pygame.Rect(0, 0, hl_w, hl_h))
        helm.blit(hl, (pad + 4 * SS, Y(pad + 1 * SS)),
                  area=pygame.Rect(hl_w // 2, 0,
                                   hl_w // 2, hl_h // 2 + 1))

    # Mohawk fin.
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

    # Rim line + chrome strip. Round 5's small placeholder skull decal is
    # intentionally GONE — the big dome face replaces it.
    pygame.draw.line(helm, DOME,
                     (pad + hw // 2 - 2 * SS, Y(pad + hh - 3 * SS)),
                     (pad + hw // 2 + 2 * SS, Y(pad + hh - 3 * SS)), SS)
    pygame.draw.rect(helm, CHROME,
                     pygame.Rect(pad - 1 * SS, Y(pad + hh - 1 * SS),
                                 hw + 2 * SS, 2 * SS))

    # Face block — sits between rim line and chrome strip, on the dome
    # itself. Run BEFORE the chinstrap so the strap never overdraws the
    # face features at the lower rim. Skip for REF + NONE.
    face_diag = {
        "skull": False, "eyes": False, "nose": False, "mouth": False,
        "bandage": False, "face_pixels": 0, "bandage_red_pixels": 0,
    }
    if variant in FACE_SPECS:
        face_diag = _draw_face(helm, variant, pad, Y, hw, hh)

    # Chinstrap + buckle — final, on top of the face so the strap reads
    # as the outermost layer (same as the live game).
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

    # Ear block — REF + H_ all get G1 ears. NONE skips ears.
    dome_top_cx = pad + hw // 2
    dome_top_y  = Y(pad)
    dome_bottom_y_ss = Y(pad + hh - 1)
    ear_bbox_ss = None
    if variant != "NONE":
        ear_bbox_ss = _draw_ears_g1(helm, dome_top_cx, dome_top_y)

    native_w = HW_N + PAD_N * 2
    native_h = HH_N + PAD_N * 2 + DROP_N + _ear_top_margin_n()
    helm_native = pygame.transform.smoothscale(helm, (native_w, native_h))

    diagnostics = _analyse_native(helm_native, variant)
    diagnostics["dome_bottom_y_native"] = dome_bottom_y_ss / SS
    diagnostics.update(face_diag)
    if ear_bbox_ss is not None:
        x0, y0, x1, y1 = ear_bbox_ss
        diagnostics["ear_bbox"] = (
            x0 / SS, y0 / SS, x1 / SS, y1 / SS,
        )
    else:
        diagnostics["ear_bbox"] = None
    return helm_native, diagnostics


# ---------------------------------------------------------------------------
# Face drawing — port of game/entities.py:_draw_skateboard_icon's skull +
# eyes + nose + mouth + bandage block, MINUS the crossed-deck X behind it.
# Coordinates are in the helmet supersurface (SS=8) space; the icon's
# original SS was 6, so we scale by FACE_NATIVE_SCALE relative to icon
# native then multiply by SS for supersurface coords.
# ---------------------------------------------------------------------------


def _draw_face(helm, variant, pad, Y, hw, hh):
    """Draw the chosen face elements on the dome. Returns diagnostics
    (which elements rendered + a pixel count for the face footprint)."""
    spec = FACE_SPECS[variant]
    diag = {
        "skull": False, "eyes": False, "nose": False, "mouth": False,
        "bandage": False, "face_pixels": 0, "bandage_red_pixels": 0,
    }

    # Face centre in supersurface coords. Use the dome native bbox
    # midpoint (16, 30) and scale by SS. Y(pad) is the dome top, so the
    # centre is (pad + hw//2, Y(pad + hh//2 - ~1)) — equivalent to
    # (16, 30) native after the anchor fix.
    face_cx = pad + hw // 2
    # Slightly above the chrome strip so the face's mouth doesn't hit
    # the chrome line.
    face_cy = Y(pad + int(hh * 0.5))

    sk_w_ss = spec["skull_w_native"] * SS
    sk_h_ss = spec["skull_h_native"] * SS
    sk = pygame.Rect(0, 0, sk_w_ss, sk_h_ss)
    sk.center = (face_cx, face_cy)

    # 1. Skull body (BONE ellipse + DOME outline).
    if spec["skull_body"]:
        pygame.draw.ellipse(helm, BONE, sk)
        # Outline thickness scales with SS — icon uses 1.4*SS at SS=6;
        # at SS=8 with FACE_NATIVE_SCALE the proportion is preserved by
        # using ~1 SS stroke (any thicker swamps the face at native).
        pygame.draw.ellipse(helm, DOME, sk, max(1, int(1.0 * SS)))
        diag["skull"] = True

    # Eye geometry — icon's relative offsets are kept so the face still
    # reads as the same skull-bunny.
    eye_r = max(1, int(sk_w_ss * 0.13))
    eye_x_off = int(sk_w_ss * 0.20)
    eye_y = sk.top + int(sk_h_ss * 0.38)

    # 2. Eyes (DOME-coloured sockets).
    if spec["draw_eyes"]:
        eyes_drawn = 0
        for sign in (-1, 1):
            if sign == -1 and spec["omit_left_eye"]:
                continue
            ex = sk.centerx + sign * eye_x_off
            pygame.draw.circle(helm, DOME, (ex, eye_y), eye_r)
            eyes_drawn += 1
        if eyes_drawn:
            diag["eyes"] = True

    # 3. Nose (DOME triangle).
    if spec["draw_nose"]:
        nose_top_y = sk.top + int(sk_h_ss * 0.55)
        nose_bot_y = nose_top_y + int(0.55 * SS)
        # Triangle wing width scales with skull width so H5's stretched
        # skull gets a proportional nose.
        wing = max(1, int(sk_w_ss * 0.07))
        pygame.draw.polygon(helm, DOME, [
            (sk.centerx - wing, nose_top_y),
            (sk.centerx + wing, nose_top_y),
            (sk.centerx,        nose_bot_y),
        ])
        diag["nose"] = True

    # 4. Jolly Roger mouth — 3 tooth lines + 2 sine-arc dips connecting
    # adjacent pairs. Port verbatim from icon, scaled to round-6 skull.
    if spec["draw_mouth"]:
        # mouth_scale: icon's recipe was authored against SK_W=23; here
        # we feed it the round-6 skull width so the tooth spacing tracks.
        mouth_scale = spec["skull_w_native"] / 23.0
        # Stroke must clear smoothscale — clamp to at least 1 SS.
        mouth_stroke = max(1, int(1.0 * SS * mouth_scale))
        teeth_top = sk.bottom - int(5 * SS * mouth_scale)
        teeth_bot = sk.bottom - int(2.5 * SS * mouth_scale)
        if teeth_bot <= teeth_top:
            teeth_bot = teeth_top + max(2, SS // 2)
        divider_dx = max(2, int(2.5 * SS * mouth_scale))
        divider_offsets = (-divider_dx, 0, divider_dx)
        outer_shorten = max(1, int(0.6 * SS * mouth_scale))
        tooth_bottoms = []
        for idx, dx in enumerate(divider_offsets):
            top_y = teeth_top + (outer_shorten if idx != 1 else 0)
            pygame.draw.line(helm, DOME,
                             (sk.centerx + dx, top_y),
                             (sk.centerx + dx, teeth_bot),
                             mouth_stroke)
            tooth_bottoms.append((sk.centerx + dx, teeth_bot))
        dip = max(2, int(1.0 * SS * mouth_scale))
        for (x0, y0), (x1, y1) in zip(tooth_bottoms, tooth_bottoms[1:]):
            pts = []
            for i in range(7):
                t = i / 6.0
                x = x0 + (x1 - x0) * t
                y_base = y0 + (y1 - y0) * t
                y = y_base + dip * math.sin(math.pi * t)
                pts.append((x, y))
            pygame.draw.lines(helm, DOME, False, pts, mouth_stroke)
        diag["mouth"] = True

    # 5. Bandage cross. Two modes:
    #   on_eye:   cross sits over the LEFT eye socket (H1/H5 — icon
    #             default). Both eyes still drawn underneath.
    #   covers_eye: cross is positioned slightly tighter on the left eye
    #               centre and the left eye is omitted (H4 punk eye-patch
    #               read). Right eye + nose + mouth still visible.
    if spec["bandage_mode"] != "off":
        cross_cx = sk.centerx - eye_x_off
        cross_cy = eye_y
        bar_l = max(3, int(5.0 * SS * (spec["skull_w_native"] / 23.0)))
        bar_t = max(1, int(1.6 * SS * (spec["skull_w_native"] / 23.0)))
        horiz = pygame.Rect(0, 0, bar_l, bar_t)
        horiz.center = (cross_cx, cross_cy)
        vert = pygame.Rect(0, 0, bar_t, bar_l)
        vert.center = (cross_cx, cross_cy)
        pygame.draw.rect(helm, RED, horiz, border_radius=max(1, SS // 3))
        pygame.draw.rect(helm, RED, vert, border_radius=max(1, SS // 3))
        pygame.draw.rect(helm, DOME, horiz, max(1, SS // 4),
                         border_radius=max(1, SS // 3))
        pygame.draw.rect(helm, DOME, vert, max(1, SS // 4),
                         border_radius=max(1, SS // 3))
        diag["bandage"] = True

    return diag


# ---------------------------------------------------------------------------
# Ear constructor — G1 straight ear from round 5, locked.
# ---------------------------------------------------------------------------


def _draw_ear_straight(big, sign, cx, cy, ear_w_ss, ear_h_ss):
    """Round-5 G1 ear: BONE outer ellipse + DOME 1.2-SS outline + RED
    inner ellipse (inflate -2.5*SS, -8*SS), tilted +/-12 deg."""
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


def _draw_ears_g1(helm, dome_top_cx, dome_top_y):
    """Overlay the locked G1 ear pair onto the helmet supersurface."""
    ear_w_n, ear_h_n, dx_n, dy_n, _fold, _bow = G1_EAR
    ear_w = ear_w_n * SS
    ear_h = ear_h_n * SS

    rects = []
    for sign in (-1, 1):
        cx = dome_top_cx + sign * dx_n * SS
        cy = dome_top_y + dy_n * SS
        rect = _draw_ear_straight(helm, sign, cx, cy, ear_w, ear_h)
        rects.append(rect)

    if not rects:
        return None
    x0 = min(r.left  for r in rects)
    y0 = min(r.top   for r in rects)
    x1 = max(r.right for r in rects)
    y1 = max(r.bottom for r in rects)
    return (x0, y0, x1, y1)


# ---------------------------------------------------------------------------
# Diagnostics — count RED pixels (bandage) + face footprint on the dome.
# ---------------------------------------------------------------------------


def _analyse_native(helm_native, variant):
    diag = {"red_pixel_count": 0, "ear_base_width_n": 0,
            "face_pixels": 0, "bandage_red_pixels": 0}
    if variant == "NONE":
        return diag
    w, h = helm_native.get_size()
    helm_native.lock()
    try:
        # Dome bbox in native subsurface coords (after anchor fix the dome
        # spans approx y in [22, 37], x in [4, 28]).
        dome_x0 = PAD_N
        dome_x1 = PAD_N + HW_N
        dome_y0 = EAR_TOP_N + PAD_N
        dome_y1 = EAR_TOP_N + PAD_N + HH_N

        red_count = 0
        bandage_red = 0
        face_pixels = 0
        for x in range(w):
            for y in range(h):
                r, g, b, a = helm_native.get_at((x, y))
                if a < 80:
                    continue
                is_red = (r >= 130 and g <= 110 and b <= 110
                          and r - max(g, b) >= 30)
                in_dome = (dome_x0 <= x < dome_x1
                           and dome_y0 <= y < dome_y1)
                if is_red:
                    red_count += 1
                    if in_dome:
                        bandage_red += 1
                # Face pixel = anything inside the dome bbox that ISN'T
                # the dome-base navy (the body) and isn't pure CHROME.
                # i.e. BONE / RED / DOME-stroke decals.
                if in_dome:
                    # BONE-ish (high luminance, low saturation toward red).
                    is_bone = (r >= 200 and g >= 200 and b >= 200)
                    if is_bone or is_red:
                        face_pixels += 1
        diag["red_pixel_count"] = red_count
        diag["bandage_red_pixels"] = bandage_red
        diag["face_pixels"] = face_pixels

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
# Gameplay-scale composite — same anchor fix as round 5.
# ---------------------------------------------------------------------------

NATIVE_PANEL = 96


def _composite_native(helmet_surf, ear_top_n):
    canvas = pygame.Surface((NATIVE_PANEL, NATIVE_PANEL), pygame.SRCALPHA)
    pip = parrot.get_parrot(0, 0.0)
    pip_rect = pip.get_rect(center=(NATIVE_PANEL // 2,
                                    NATIVE_PANEL // 2))
    canvas.blit(pip, pip_rect.topleft)
    center_y = pip_rect.centery - 10 - (ear_top_n / 2.0)
    helm_rect = helmet_surf.get_rect(
        center=(pip_rect.centerx + 18, center_y))
    canvas.blit(helmet_surf, helm_rect.topleft)
    return canvas, helm_rect


# ---------------------------------------------------------------------------
# vs-REF delta — round 6's REF is G1 (ears + bare dome). Variant pixels
# that fall OUTSIDE the REF's solid dome silhouette get tinted RED. Since
# all H_ variants share G1's ear pixels, the delta isolates the FACE
# elements drawn on the dome's interior.
# ---------------------------------------------------------------------------


def _ref_outline_silhouette(ear_top_n, ref_helm_native):
    """REF outline = G1 helmet's full silhouette outline (the silhouette
    of the BARE-DOME G1 baseline). The delta tints variant-only pixels
    on top of this outline."""
    out = pygame.Surface(
        (NATIVE_PANEL, NATIVE_PANEL), pygame.SRCALPHA)
    # Build the outline as a 1-px DOME stroke around the REF helmet's
    # alpha mask. We expand the REF alpha by 1 px and subtract — that
    # gives a crisp outline that follows the actual ear silhouette.
    src = ref_helm_native
    w, h = src.get_size()
    mask = pygame.mask.from_surface(src, threshold=80)
    outline_pts = mask.outline()

    # Render the outline onto a helmet-subsurface-sized canvas, then
    # composite onto the panel using the same anchor as the composite.
    silhouette = pygame.Surface((w, h), pygame.SRCALPHA)
    if len(outline_pts) >= 2:
        pygame.draw.lines(silhouette, DOME, True, outline_pts, 1)

    center_y = NATIVE_PANEL // 2 - 10 - (ear_top_n / 2.0)
    helm_rect = silhouette.get_rect(
        center=(NATIVE_PANEL // 2 + 18, center_y))
    out.blit(silhouette, helm_rect.topleft)
    return out


def _delta_overlay(variant_helmet_surf, ref_outline_surf, ref_helm_native,
                   ear_top_n):
    """Show REF outline + RED tint where variant has pixels REF does not.
    Since the ears are locked across REF + variants, the delta isolates
    the face decals on the dome."""
    out = pygame.Surface((NATIVE_PANEL, NATIVE_PANEL), pygame.SRCALPHA)
    out.blit(ref_outline_surf, (0, 0))

    # Build a REF-solid mask in panel coordinates so we can detect
    # variant-only pixels by simple alpha comparison.
    ref_solid = pygame.Surface(
        (NATIVE_PANEL, NATIVE_PANEL), pygame.SRCALPHA)
    center_y = NATIVE_PANEL // 2 - 10 - (ear_top_n / 2.0)
    ref_rect = ref_helm_native.get_rect(
        center=(NATIVE_PANEL // 2 + 18, center_y))
    ref_solid.blit(ref_helm_native, ref_rect.topleft)

    var_canvas = pygame.Surface(
        (NATIVE_PANEL, NATIVE_PANEL), pygame.SRCALPHA)
    var_rect = variant_helmet_surf.get_rect(
        center=(NATIVE_PANEL // 2 + 18, center_y))
    var_canvas.blit(variant_helmet_surf, var_rect.topleft)

    w, h = NATIVE_PANEL, NATIVE_PANEL
    var_canvas.lock()
    ref_solid.lock()
    for x in range(w):
        for y in range(h):
            var_a = var_canvas.get_at((x, y))[3]
            ref_a = ref_solid.get_at((x, y))[3]
            if var_a > 0:
                # Tint pixels that:
                #   * fall OUTSIDE the REF silhouette (none expected since
                #     ears + dome are locked), OR
                #   * differ in colour from the REF pixel at the same
                #     coord by more than a small threshold (the face
                #     decals on the dome).
                if ref_a == 0:
                    out.set_at((x, y), DELTA_TINT + (255,))
                else:
                    r1, g1, b1, _ = var_canvas.get_at((x, y))
                    r0, g0, b0, _ = ref_solid.get_at((x, y))
                    if (abs(r1 - r0) + abs(g1 - g0) + abs(b1 - b0)) > 60:
                        out.set_at((x, y), DELTA_TINT + (255,))
    var_canvas.unlock()
    ref_solid.unlock()
    return out


# ---------------------------------------------------------------------------
# Sheet layout — REF (G1, no face) + 5 face variants.
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
        "REF.  G1 ears + NO FACE — round-5 winner baseline",
        True, LABEL)
    sheet.blit(lbl, (card.left + PAD, card.top + 8))
    sub_font = _font(12)
    sub = sub_font.render(
        "G1 from round 5 — picked ear treatment, no face yet",
        True, SUBLABEL)
    sheet.blit(sub, (card.left + PAD, card.top + 8 + lbl.get_height() + 2))

    composite, helm_rect = _composite_native(helmet_surf, ear_top_n=ear_top_n)
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
        f"{ZOOM}x zoom  (locked-ears baseline)", True, SUBLABEL)
    sheet.blit(cap, (zoom_x + (ZOOM_PANEL - cap.get_width()) // 2,
                     zoom_y + ZOOM_PANEL + 4))
    print(
        f"REF  anchor y (post-fix): {helm_rect.centery}  | "
        f"dome bottom on Pip y ~ {helm_rect.centery + 9} native px"
    )
    return panel_h


def _draw_variant_row(sheet, x, y, code, name, blurb, variant,
                      ref_outline, ref_helm_native, ear_top_n):
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
        sheet, native_x, native_y, composite, "native (gameplay scale)")

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
    delta_native = _delta_overlay(
        helm, ref_outline, ref_helm_native, ear_top_n)
    delta_zoom = pygame.transform.scale(
        delta_native, (DELTA_PANEL, DELTA_PANEL))
    sheet.blit(delta_zoom, (delta_x, delta_y))
    pygame.draw.rect(sheet, (44, 50, 60),
                     pygame.Rect(delta_x, delta_y,
                                 DELTA_PANEL, DELTA_PANEL), 1)
    cap2 = cap_font.render("vs-REF delta (face only)", True, SUBLABEL)
    sheet.blit(cap2, (delta_x + (DELTA_PANEL - cap2.get_width()) // 2,
                      delta_y + DELTA_PANEL + 4))

    parts = []
    parts.append(f"skull={'Y' if diag['skull'] else 'N'}")
    parts.append(f"eyes={'Y' if diag['eyes'] else 'N'}")
    parts.append(f"nose={'Y' if diag['nose'] else 'N'}")
    parts.append(f"mouth={'Y' if diag['mouth'] else 'N'}")
    parts.append(f"bandage={'Y' if diag['bandage'] else 'N'}")
    bandage_px = diag.get("bandage_red_pixels", 0)
    face_px = diag.get("face_pixels", 0)
    print(
        f"{code}  face px: {face_px:4d}  | "
        f"bandage red px: {bandage_px:3d}  | "
        f"elements: " + " ".join(parts)
    )
    return panel_h


VARIANTS = [
    ("H1", "FULL FACE",
     "skull + eyes + nose + Jolly Roger mouth + RED bandage over LEFT eye."),
    ("H2", "NO BANDAGE",
     "H1 minus the RED cross — skull + eyes + nose + mouth only."),
    ("H3", "MASK STYLE",
     "no skull body; the dome IS the skull. Only eyes + nose + mouth."),
    ("H4", "EYE-PATCH PUNK",
     "H1 face but the RED cross fully COVERS the LEFT eye (eye omitted)."),
    ("H5", "BIG FACE FILL",
     "H1 stretched to 22x13 native — face fills more of the dome bbox."),
]


def main():
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    pygame.init()

    PAD = 16
    TITLE_H = 96

    # REF = G1 ears + NO face. We pass a non-FACE_SPECS sentinel so
    # _build_helmet skips the face block.
    ref_helm, _ = _build_helmet("REF", draw_fin=True)
    ref_outline = _ref_outline_silhouette(EAR_TOP_N, ref_helm)

    variant_panel_w = (NATIVE_PANEL + PAD + ZOOM_PANEL + PAD
                       + DELTA_PANEL + PAD * 2)
    sheet_w = max(880, variant_panel_w + PAD * 2)
    ref_panel_w = NATIVE_PANEL + PAD + ZOOM_PANEL + PAD * 2
    panel_h = 50 + ZOOM_PANEL + PAD * 2 + 22
    sheet_h = TITLE_H + PAD + (panel_h + PAD) * (1 + len(VARIANTS))

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill(SHEET_BG)

    title_text = ("SKATEBOARD helmet  —  round 6 "
                  "(skull-bunny face on the dome)")
    sub_text = ("G1 ears locked. 5 variants explore how much of the "
                "icon's skull-bunny face sits on the dome. No crossed boards.")
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
    _draw_ref_row(sheet, ref_x, y, ref_helm, ear_top_n=EAR_TOP_N)
    y += panel_h + PAD

    var_x = (sheet_w - variant_panel_w) // 2
    for code, name, blurb in VARIANTS:
        _draw_variant_row(sheet, var_x, y, code, name, blurb, code,
                          ref_outline, ref_helm, ear_top_n=EAR_TOP_N)
        y += panel_h + PAD

    out_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "docs", "skateboard_helmet_ears",
    )
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_6.png")
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
