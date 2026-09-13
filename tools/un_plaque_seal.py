"""plaque-seal — the unlock pressed INTO the hero score plaque like a wax seal.

A freshly-struck commendation medallion is pressed into the plaque's bottom-right
corner the way a wax seal / cornerstone stamp lands on a certificate: a poured
gold-wax wafer (irregular drip edge + a debossed shine), the real Courier's
Commendation badge struck into its centre, and a tiny engraved "NEW COMMENDATION"
microcaption riding a ribbon under the cluster. Zero new surface area — the
plaque the player is already proud of hosts the reward.

The 3-unlock case is the design driver: three wafers fan in the corner, each
nested behind the last, kept clear of the centred FINAL SCORE numeral and the
"BEST 47  -11" readout. Scratch tooling only; game/ is untouched.
"""
import os
import math
import pygame

from tools.unlock_notice_common import render_backdrop, demo_ids
from game import achievements as ach
from game.achievement_icons import draw_badge
from game.draw import lerp_color, blit_glow
from game.hud import (_font, _GOLD_BRIGHT, _GOLD_PALE, _GOLD_DEEP,
                      _PANEL_DARK, _NIGHT_DEEP)

# Wax-wafer palette — a poured gold wax that belongs to the gold-on-navy family
# but reads as a soft pressed medium, not the plaque's hard minted frame.
_WAX_HI   = (210, 158,  44)
_WAX_MID  = (168, 118,  26)
_WAX_LO   = (104,  70,  12)
_WAX_EDGE = ( 58,  36,   6)


def _wax_wafer(surf, cx, cy, R, seed):
    """A poured-wax disc with an irregular molten rim and an upper-left sheen,
    so the badge looks pressed INTO wax rather than floating on a flat coin."""
    rng = pygame.math
    # Build the lobed silhouette: small per-vertex radius jitter for a poured
    # drip edge that still reads round at a glance.
    pts = []
    n = 40
    for i in range(n):
        a = i / n * math.tau
        # deterministic wobble keyed on seed so each wafer differs slightly
        w = (math.sin(a * 3 + seed * 1.7) * 0.05
             + math.sin(a * 5 + seed * 0.9) * 0.03
             + math.sin(a * 2 + seed) * 0.04)
        rr = R * (1.0 + w)
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    ipts = [(int(x), int(y)) for x, y in pts]

    # Contact shadow under the wafer — a darker, slightly enlarged silhouette
    # offset down-right, softened by a round-trip downscale. Sells "a thick wax
    # blob pressed onto the certificate surface", not a flat coin laid on top.
    sh = pygame.Surface((R * 3, R * 3), pygame.SRCALPHA)
    soff = max(3, R // 5)
    spts = [(int((x - cx) * 1.08 + R * 1.5 + soff),
             int((y - cy) * 1.08 + R * 1.5 + soff)) for x, y in pts]
    pygame.draw.polygon(sh, (0, 0, 0, 150), spts)
    sh = pygame.transform.smoothscale(
        pygame.transform.smoothscale(sh, (R, R)), (R * 3, R * 3))
    surf.blit(sh, (cx - int(R * 1.5), cy - int(R * 1.5)))

    # Wax body — radial-ish fill via concentric shrinking polygons, lit upper-left.
    layers = 14
    for li in range(layers):
        t = li / (layers - 1)
        f = 1.0 - t * 0.9
        # bias the lit centre up-left
        ox = -R * 0.16 * t
        oy = -R * 0.16 * t
        col = lerp_color(_WAX_LO, _WAX_HI, t)
        lp = [(int(cx + (x - cx) * f + ox), int(cy + (y - cy) * f + oy))
              for x, y in pts]
        pygame.draw.polygon(surf, col, lp)
    # Molten dark keyline around the rim.
    pygame.draw.polygon(surf, _WAX_EDGE, ipts, max(2, R // 12))
    # Specular crescent on the upper-left lip of the wax.
    sheen = pygame.Surface((R * 2, R * 2), pygame.SRCALPHA)
    pygame.draw.arc(sheen, (*_GOLD_PALE, 150),
                    (int(R * 0.18), int(R * 0.14), int(R * 1.5), int(R * 1.5)),
                    math.radians(120), math.radians(220), max(2, R // 9))
    surf.blit(sheen, (cx - R, cy - R))


def _ribbon_tail(surf, cx, cy, R, seed):
    """A short twin-tail ribbon slipping out from under the wax, the way a wax
    seal pins a ribbon to a document. Drawn before the wafer so the wax overlaps
    its top."""
    drop = int(R * 1.5)
    spread = int(R * 0.62)
    for sgn in (-1, 1):
        tip_x = cx + sgn * spread
        tip_y = cy + drop
        ribbon = [
            (cx + sgn * int(R * 0.22), cy + int(R * 0.2)),
            (cx + sgn * int(R * 0.62), cy + int(R * 0.2)),
            (tip_x + sgn * int(R * 0.10), tip_y),
            (tip_x - sgn * int(R * 0.16), tip_y),
            (cx - sgn * int(R * 0.04), cy + int(R * 0.42)),
        ]
        col = lerp_color(_GOLD_DEEP, _WAX_MID, 0.3)
        pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in ribbon])
        pygame.draw.polygon(surf, _WAX_EDGE,
                            [(int(x), int(y)) for x, y in ribbon], 1)
        # swallowtail notch shading
        pygame.draw.line(surf, _WAX_LO,
                         (tip_x - sgn * int(R * 0.03), tip_y),
                         (cx, cy + int(R * 0.5)), 1)


def _stamp_seal(surf, ids, corner_cx, corner_cy):
    """Press a fanned cluster of wax seals into the corner. The cluster is built
    back-to-front so the freshest (last) seal sits on top, fully crisp."""
    n = len(ids)
    R = 20                       # wafer radius — sized so a 3-fan stays in corner
    # Fan offsets: each later seal steps up-LEFT a touch and UP, overlapping the
    # one before, so the stack reads as a deliberately pressed cluster that climbs
    # into the corner — kept tight so the whole fan clears the centred numeral
    # (right edge x229) and the "BEST 47  -11" line (right edge x223).
    step_x = -12
    step_y = -15
    badge_frac = 0.78            # struck badge fills most of the wafer

    centers = []
    for k in range(n):
        cx = corner_cx + step_x * (n - 1 - k)
        cy = corner_cy + step_y * (n - 1 - k)
        centers.append((cx, cy))

    # A soft warm press-glow behind the whole cluster — the "freshly struck" heat.
    gx = sum(c[0] for c in centers) // n
    gy = sum(c[1] for c in centers) // n
    blit_glow(surf, gx, gy, int(R * 1.7), (255, 196, 96), 60)

    for k, (cx, cy) in enumerate(centers):
        _wax_wafer(surf, cx, cy, R, seed=k)
        br = int(R * badge_frac * 2)
        brect = pygame.Rect(0, 0, br, br)
        brect.center = (cx, cy)
        draw_badge(surf, ach.BY_ID[ids[k]].icon_key, brect, True, False)

    return centers


def _micro_caption(surf, centers, plaque):
    """A tiny engraved microcaption on a debossed plate, tucked into the plaque's
    bottom-RIGHT corner under the cluster — right-aligned to the plaque edge so it
    can never reach the centred 'BEST 47  -11' readout (whose right edge is x223),
    and small enough that it never reads as a competing banner."""
    label = "NEW COMMENDATION"
    f = _font(8, True)
    txt = f.render(label, True, _GOLD_PALE)
    plate_w = txt.get_width() + 12
    plate_h = txt.get_height() + 5
    # Sit just below the lowest wafer, hugging the plaque's bottom-right inner
    # corner; right-aligned so the left edge stays well right of the BEST line.
    plate = pygame.Rect(0, 0, plate_w, plate_h)
    plate.right = plaque.right - 12
    plate.bottom = plaque.bottom - 11
    # Debossed dark plate with a thin gold keyline + top sheen.
    chip = pygame.Surface(plate.size, pygame.SRCALPHA)
    pygame.draw.rect(chip, (*_NIGHT_DEEP, 240), (0, 0, plate_w, plate_h),
                     border_radius=4)
    pygame.draw.rect(chip, (*_GOLD_DEEP, 235), (0, 0, plate_w, plate_h),
                     width=1, border_radius=4)
    pygame.draw.line(chip, (*_GOLD_PALE, 70), (3, 1), (plate_w - 3, 1))
    surf.blit(chip, plate.topleft)
    # Engrave: dark inset + gold face.
    sh = f.render(label, True, _PANEL_DARK)
    surf.blit(sh, sh.get_rect(center=(plate.centerx + 1, plate.centery + 1)))
    surf.blit(txt, txt.get_rect(center=plate.center))
    return plate


def _compose(ids, out_name):
    surf = render_backdrop()
    # The roomy layout's plaque (matches game/hud.py draw_stats roomy branch).
    plaque = pygame.Rect(18, 104, 360 - 36, 156)
    # Anchor for the FRONTMOST seal: tucked into the lower-right quadrant so the
    # fan climbs up-left from here, staying right of the numeral (right edge x229)
    # and above the BEST line / the corner microcaption plate.
    corner_cx = plaque.right - 33
    corner_cy = plaque.bottom - 50
    centers = _stamp_seal(surf, ids, corner_cx, corner_cy)
    _micro_caption(surf, centers, plaque)

    OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "docs", "achievements", "unlock_notice", "plaque-seal")
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, out_name)
    pygame.image.save(surf, path)
    return path


if __name__ == "__main__":
    p2 = _compose(demo_ids(2), "round_1.png")
    p3 = _compose(demo_ids(3), "round_1_three.png")
    print(p2)
    print(p3)
