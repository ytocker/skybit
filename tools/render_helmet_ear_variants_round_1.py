"""SKATEBOARD helmet ears — round 1 exploration sheet.

The just-picked pickup icon (A. PUNK STUDDED SKULL-BUNNY) wears tall
red-tipped bunny ears. This sheet explores 5 attachment styles for the
LIVE helmet during gameplay so the user can pick the silhouette that
reads best at 24x15 native px.

Five rows below a reference row that shows the shipped earless helmet:

  V1. ICON-MATCH      ear shape + tilt scaled from the pickup-icon recipe
                      (SS=6 metrics -> SS=4 helmet metrics).
  V2. SHORT NUBS      ~60% height, 0 degree tilt, anchored closer in.
  V3. SPLAYED WIDE    full height, +/-28 degree tilt, wider anchor.
  V4. LOP / DROOPY    rotated +/-70 degrees so the ears drape sideways
                      from the dome rim (Holland-Lop bunny).
  V5. POINTY DEMON    triangular ears via pygame.draw.polygon; sharper
                      silhouette than the ellipse family.

Palette is LOCKED to the pickup-icon's five colours plus the card
backdrop -- BONE shell, DOME outline, RED tip insert. Nothing foreign.

Run headless:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \\
        python3 tools/render_helmet_ear_variants_round_1.py
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
CREAM  = (245, 240, 230)
RED    = (200, 50, 50)

CARD_BG  = (26, 30, 38)
SHEET_BG = (16, 18, 24)
LABEL    = (215, 220, 230)
SUBLABEL = (150, 158, 172)


# ---------------------------------------------------------------------------
# Live-helmet construction lifted from `Bird._draw_helmet`
# (game/entities.py:720-823). Re-implemented here as a free function so
# the renderer doesn't need a `Bird` instance, and so the ear block can
# be injected before the final smoothscale. The dome/fin/strap geometry
# is byte-identical to the shipped helmet; only the subsurface height is
# expanded upward so tall ears don't clip when blitted before scale-down.
# ---------------------------------------------------------------------------

SS = 4         # supersample factor used by the live helmet draw.
HW_N = 24      # native dome width.
HH_N = 15      # native dome height.
PAD_N = 4      # native padding around the dome.
DROP_N = 28    # native chinstrap drop region under the dome.


def _ear_top_margin_n() -> int:
    """Extra padding above the dome in NATIVE units so the tallest
    bunny ear fits inside the helmet subsurface. The icon ear is ~28
    SS=6 units tall i.e. ~19 SS=4 units; once anchored ~7 SS above the
    dome top, its tip lands ~26 SS = 6.5 native units up. Round to 8."""
    return 8


def _build_helmet_with_ears(variant: str):
    """Build the live skater helmet surface and overlay the given ear
    variant before the final smoothscale, mirroring the in-game path.

    Returns (native_surf, ear_top_y_native, ear_label).
    `ear_top_y_native` is the top-most Y of the ear silhouette in
    native helmet-subsurface coordinates -- used by the diagnostic
    print so the orchestrator can verify nothing clipped.
    """
    hw = HW_N * SS
    hh = HH_N * SS
    pad = PAD_N * SS
    drop = DROP_N * SS

    # Extra headroom above the dome so the bunny ears live inside the
    # subsurface rather than getting cropped at the top edge.
    ear_top = _ear_top_margin_n() * SS

    helm = pygame.Surface(
        (hw + pad * 2, hh + pad * 2 + drop + ear_top),
        pygame.SRCALPHA,
    )

    # All dome/fin/strap coordinates from `_draw_helmet` are offset by
    # `ear_top` so the dome's logical (pad, pad) origin lives below the
    # ear headroom.
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

    OUT     = (15, 15, 22)
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

    # -----------------------------------------------------------------
    # EARS: draw onto the SS=4 helmet surface BEFORE the smoothscale so
    # the inner red insert and outline antialias to the same crispness
    # as the rest of the helmet. Anchored from the dome top, NOT from
    # the helmet's subsurface top (which now includes ear_top headroom).
    # -----------------------------------------------------------------
    dome_top_cx = pad + hw // 2
    dome_top_y  = Y(pad)
    rim_y_local = Y(pad + hh)  # rim line — V4 drapes from here.

    ear_top_y_native = _draw_ears(helm, variant, dome_top_cx, dome_top_y,
                                  rim_y_local)

    # Smoothscale to native gameplay size (with ear headroom included).
    native_w = HW_N + PAD_N * 2
    native_h = HH_N + PAD_N * 2 + DROP_N + _ear_top_margin_n()
    helm_native = pygame.transform.smoothscale(helm, (native_w, native_h))
    return helm_native, ear_top_y_native


def _draw_ears(helm, variant, dome_top_cx, dome_top_y, rim_y_local):
    """Overlay the requested ear pair onto the helmet supersurface.

    Returns the topmost Y (helmet-subsurface coords, SS=4 units NOT
    native) of any ear pixel so the renderer can sanity-check clip-free
    placement. Coordinates are returned in NATIVE pixels (SS=4 -> /SS)
    for the diagnostic line.
    """
    tops_ss = []

    if variant == "V1":
        # ICON-MATCH: pickup-icon ear scaled SS=6 -> SS=4. Ellipse
        # 7*SS=6 wide x 28*SS=6 tall becomes ~5*SS=4 wide x ~19*SS=4
        # tall; +/-12 degree tilt; RED inner insert via inflate by the
        # same 4/6 ratio. Anchor 5 SS off centre and 7 SS above the
        # dome top -- "sprouting from the dome" silhouette.
        for sign in (-1, 1):
            ear_w = int(7 * 4 / 6 * SS)   # ~5 SS
            ear_h = int(28 * 4 / 6 * SS)  # ~19 SS
            ang   = -12 * sign
            cx    = dome_top_cx + sign * int(5 * SS)
            cy    = dome_top_y - int(7 * SS)
            top_ss = _blit_ellipse_ear(helm, cx, cy, ear_w, ear_h, ang,
                                       inflate=(int(-2.5 * 4 / 6 * SS),
                                                int(-8 * 4 / 6 * SS)))
            tops_ss.append(top_ss)

    elif variant == "V2":
        # SHORT NUBS: same ear shape, ~60% height, straight up.
        for sign in (-1, 1):
            ear_w = int(7 * 4 / 6 * SS)
            ear_h = int(28 * 4 / 6 * 0.60 * SS)
            ang   = 0
            cx    = dome_top_cx + sign * int(4 * SS)
            cy    = dome_top_y - int(4 * SS)
            top_ss = _blit_ellipse_ear(helm, cx, cy, ear_w, ear_h, ang,
                                       inflate=(int(-2.5 * 4 / 6 * SS),
                                                int(-5 * 4 / 6 * SS)))
            tops_ss.append(top_ss)

    elif variant == "V3":
        # SPLAYED WIDE: V1 silhouette tilted out +/-28 degrees, anchor
        # widened by 2 SS so they read as alert / listening.
        for sign in (-1, 1):
            ear_w = int(7 * 4 / 6 * SS)
            ear_h = int(28 * 4 / 6 * SS)
            ang   = -28 * sign
            cx    = dome_top_cx + sign * int(7 * SS)
            cy    = dome_top_y - int(6 * SS)
            top_ss = _blit_ellipse_ear(helm, cx, cy, ear_w, ear_h, ang,
                                       inflate=(int(-2.5 * 4 / 6 * SS),
                                                int(-8 * 4 / 6 * SS)))
            tops_ss.append(top_ss)

    elif variant == "V4":
        # LOP / DROOPY: full-length ears rotated +/-70 degrees so they
        # flop almost horizontal off the rim. Anchored AT the rim line
        # so the ears drape across the dome shoulder.
        for sign in (-1, 1):
            ear_w = int(7 * 4 / 6 * SS)
            ear_h = int(28 * 4 / 6 * SS)
            ang   = -70 * sign
            # After a 70 degree rotation the ear roughly lays sideways;
            # anchor near the rim, offset out so the bases meet the
            # dome shoulder rather than poking into the strap region.
            cx    = dome_top_cx + sign * int(4 * SS)
            cy    = rim_y_local - int(4 * SS)
            top_ss = _blit_ellipse_ear(helm, cx, cy, ear_w, ear_h, ang,
                                       inflate=(int(-2.5 * 4 / 6 * SS),
                                                int(-8 * 4 / 6 * SS)))
            tops_ss.append(top_ss)

    elif variant == "V5":
        # POINTY DEMON: triangular ears via pygame.draw.polygon, with
        # an inner RED triangle insert. Base ~4 SS wide, height ~19 SS
        # tall. Same BONE-shell / DOME-outline palette discipline.
        base_w = int(4 * SS)
        height = int(19 * SS)
        for sign in (-1, 1):
            ang   = -12 * sign
            cx    = dome_top_cx + sign * int(5 * SS)
            cy    = dome_top_y - int(7 * SS)
            top_ss = _blit_triangle_ear(helm, cx, cy, base_w, height, ang)
            tops_ss.append(top_ss)

    else:
        return None

    # Convert SS-units to native px for the diagnostic; smallest top-Y
    # (highest on screen) wins.
    if not tops_ss:
        return None
    return min(tops_ss) / SS


def _blit_ellipse_ear(big, cx, cy, ear_w, ear_h, ang_deg, inflate):
    """Draw a single icon-style ear (BONE ellipse + DOME outline + RED
    inner insert) onto `big`, rotated and centred at (cx, cy).

    Returns the topmost Y of the blitted ear rect in `big` coords.
    """
    pad_local = 4 * SS
    sub = pygame.Surface(
        (ear_w + pad_local, ear_h + pad_local),
        pygame.SRCALPHA,
    )
    local = pygame.Rect(0, 0, ear_w, ear_h)
    local.center = (sub.get_width() // 2, sub.get_height() // 2)
    pygame.draw.ellipse(sub, BONE, local)
    pygame.draw.ellipse(sub, DOME, local, max(1, int(1.2 * SS * 4 / 6)))
    inner = local.inflate(*inflate)
    if inner.width > 0 and inner.height > 0:
        pygame.draw.ellipse(sub, RED, inner)
    rot = pygame.transform.rotate(sub, ang_deg)
    rect = rot.get_rect(center=(cx, cy))
    big.blit(rot, rect.topleft)
    return rect.top


def _blit_triangle_ear(big, cx, cy, base_w, height, ang_deg):
    """Pointy isoceles-triangle ear (BONE shell + DOME outline + RED
    inner triangle tip). Built in a local subsurface, then rotated."""
    pad_local = 4 * SS
    sub_w = base_w + pad_local
    sub_h = height + pad_local
    sub = pygame.Surface((sub_w, sub_h), pygame.SRCALPHA)

    # Triangle apex at top centre, base at bottom across `base_w`.
    apex = (sub_w // 2, pad_local // 2)
    bl   = (sub_w // 2 - base_w // 2, sub_h - pad_local // 2)
    br   = (sub_w // 2 + base_w // 2, sub_h - pad_local // 2)
    pygame.draw.polygon(sub, BONE, [apex, bl, br])
    pygame.draw.polygon(sub, DOME, [apex, bl, br],
                        max(1, int(1.2 * SS * 4 / 6)))

    # Inner RED tip — same apex, half the height, narrower base.
    inner_h = height * 2 // 3
    inner_w = max(SS, base_w // 2)
    apex_i = (sub_w // 2, pad_local // 2 + height // 8)
    bl_i = (sub_w // 2 - inner_w // 2,
            pad_local // 2 + height // 8 + inner_h)
    br_i = (sub_w // 2 + inner_w // 2,
            pad_local // 2 + height // 8 + inner_h)
    pygame.draw.polygon(sub, RED, [apex_i, bl_i, br_i])

    rot = pygame.transform.rotate(sub, ang_deg)
    rect = rot.get_rect(center=(cx, cy))
    big.blit(rot, rect.topleft)
    return rect.top


def _build_helmet_no_ears():
    """Reference helmet — shipped earless silhouette, same draw path as
    the live game but with no ear overlay."""
    helm_native, _ = _build_helmet_with_ears(variant="NONE")
    return helm_native


# ---------------------------------------------------------------------------
# Gameplay-scale composite — Pip head + helmet at the in-game blit offset.
# The helmet rides at `(pip_x + 18, pip_y - 10)` relative to Pip's centre
# in the gravity-down case (entities.py:815-816); replicate verbatim so
# the user sees true in-game positioning.
# ---------------------------------------------------------------------------

NATIVE_PANEL = 56   # canvas px around Pip's centre for the native cell.


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
# Sheet layout — one reference row + 5 variant rows, each with a native
# composite and a 4x zoom, matching the gallery convention used in
# `tools/render_skateboard_redesign_round_3.py`.
# ---------------------------------------------------------------------------

ZOOM = 4
ZOOM_PANEL = NATIVE_PANEL * ZOOM


def _font(size, bold=False):
    try:
        return pygame.font.SysFont("DejaVu Sans", size, bold=bold)
    except Exception:
        return pygame.font.Font(None, size)


def _draw_row(sheet, x, y, label_text, sub_text, helmet_surf):
    PAD = 16
    LABEL_H = 50  # title line + sub tag.
    panel_h = LABEL_H + ZOOM_PANEL + PAD * 2 + 22
    panel_w = ZOOM_PANEL + NATIVE_PANEL + PAD * 3

    card = pygame.Rect(x, y, panel_w, panel_h)
    pygame.draw.rect(sheet, CARD_BG, card, border_radius=10)
    pygame.draw.rect(sheet, (44, 50, 60), card, 1, border_radius=10)

    font = _font(18, bold=True)
    lbl = font.render(label_text, True, LABEL)
    sheet.blit(lbl, (card.left + PAD, card.top + 8))

    sub_font = _font(12)
    sub = sub_font.render(sub_text, True, SUBLABEL)
    sheet.blit(sub, (card.left + PAD, card.top + 8 + lbl.get_height() + 2))

    composite = _composite_native(helmet_surf)

    native_x = card.left + PAD
    native_y = card.top + LABEL_H + PAD + (ZOOM_PANEL - NATIVE_PANEL) // 2
    sheet.blit(composite, (native_x, native_y))
    cap_font = _font(12)
    cap = cap_font.render("native (gameplay scale)", True, SUBLABEL)
    sheet.blit(cap, (native_x + (NATIVE_PANEL - cap.get_width()) // 2,
                     native_y + NATIVE_PANEL + 4))

    zoom = pygame.transform.scale(composite, (ZOOM_PANEL, ZOOM_PANEL))
    zoom_x = native_x + NATIVE_PANEL + PAD
    zoom_y = card.top + LABEL_H + PAD
    sheet.blit(zoom, (zoom_x, zoom_y))
    cap2 = cap_font.render(f"{ZOOM}x zoom", True, SUBLABEL)
    sheet.blit(cap2, (zoom_x + (ZOOM_PANEL - cap2.get_width()) // 2,
                      zoom_y + ZOOM_PANEL + 4))

    return panel_h


VARIANTS = [
    ("V1", "ICON-MATCH",
     "exact pickup-icon recipe, SS=6 metrics rescaled to SS=4."),
    ("V2", "SHORT NUBS",
     "~60% height, 0 degree tilt, anchored closer to centre."),
    ("V3", "SPLAYED WIDE",
     "full-height ears tilted +/-28 degrees outward, wider anchor."),
    ("V4", "LOP / DROOPY",
     "+/-70 degrees rotation, anchored at the rim — Holland-Lop bunny."),
    ("V5", "POINTY DEMON",
     "isoceles triangle silhouette with RED inner-triangle tip."),
]


def main():
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    pygame.init()

    PAD = 16
    TITLE_H = 86

    rows = []
    # Reference row first so the user sees the baseline silhouette.
    rows.append(("REF.  SHIPPED HELMET (no ears) — baseline",
                 "current in-game helmet — for comparison only",
                 _build_helmet_no_ears(),
                 None))
    for code, name, blurb in VARIANTS:
        helm, ear_top_native = _build_helmet_with_ears(code)
        rows.append((f"{code}.  {name}", blurb, helm, ear_top_native))

    panel_w = ZOOM_PANEL + NATIVE_PANEL + PAD * 3
    panel_h = 50 + ZOOM_PANEL + PAD * 2 + 22

    sheet_w = panel_w + PAD * 2
    sheet_h = TITLE_H + PAD + (panel_h + PAD) * len(rows)

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill(SHEET_BG)

    title_text = "SKATEBOARD helmet ears  —  round 1 (5 attachment variants)"
    sub_text = ("Picked icon = A. PUNK STUDDED SKULL-BUNNY. "
                "These 5 variants try the matching bunny ears on the "
                "LIVE helmet during gameplay.")
    target_title_w = 720
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
    sub = sub_font.render(sub_text, True, SUBLABEL)

    max_title_w = sheet_w - PAD * 4
    if title.get_width() > max_title_w:
        print(f"WARNING title pixel width {title.get_width()} > "
              f"sheet max {max_title_w}; consider shortening.")
    sheet.blit(title, (PAD * 2, PAD + 4))
    sheet.blit(sub, (PAD * 2, PAD + 4 + title.get_height() + 4))

    y = TITLE_H + PAD
    for label_text, blurb, helm, ear_top_native in rows:
        _draw_row(sheet, PAD, y, label_text, blurb, helm)
        if ear_top_native is not None:
            print(f"{label_text.split('.')[0]} ear bbox top-Y in helmet "
                  f"subsurface (native px) = {ear_top_native:.1f}  "
                  f"(headroom available: {_ear_top_margin_n()} px)")
        y += panel_h + PAD

    out_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "docs", "skateboard_helmet_ears",
    )
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_1.png")
    pygame.image.save(sheet, out_path)
    print(f"wrote {out_path} ({sheet.get_width()}x{sheet.get_height()})")


if __name__ == "__main__":
    main()
