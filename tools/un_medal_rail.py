"""medal-rail unlock-notice mock — an earned commendation badge cluster pinned
in the top-left open margin of the run-summary screen, with a thin decorative
ribbon spine descending the dead left edge below it.

The legible reward lives UP TOP, left of the centred "RUN SUMMARY" title and
above the hero plaque (y<104): a clearly-struck circular medallion hung from a
real grosgrain sash with knots, capped by a horizontal "EARNED ×N" plate. Only
a slim ribbon spine continues down the x0..18 gutter past the protected layout,
so the rail reads as a hanging commendation, not a scrollbar / frame edge.

Scratch tooling only; nothing under game/ is touched.
"""
import os
import pygame

from tools.unlock_notice_common import render_backdrop, demo_ids
from game import achievements as ach
from game.achievement_icons import draw_badge
from game.draw import blit_glow, lerp_color
from game.hud import (_font, _GOLD_BRIGHT, _GOLD_PALE, _GOLD_DEEP,
                      _PANEL_DARK, _NIGHT_DEEP)

W, H = 360, 640

# Geometry — the readable cluster lives in the top-left open area (left of the
# centred title, above the plaque at y104). The ribbon is pulled in off the
# absolute screen edge so it never merges with the frame, and given real width
# so it reads as a hanging sash. The descending spine that runs past the plaque
# stays inside x0..18 (the only dead gutter beside protected content).
# The genuinely dead top-left area is x0..46 (left of the title, whose glyphs
# start at x48) from y~6 down to y~66, plus a short full-width strip y66..102
# above the plaque (border at x34, y104). The cluster fits ONE legible Ø44
# medallion into that left wedge, clear of both the title and the plaque.
SPINE_X = 13                # ribbon centre line — OFF the absolute edge (x0)
RIBBON_W = 10               # sash width — broad enough to read as grosgrain
BADGE_D = 38                # medallion diameter — legible struck medal + rim,
BADGE_CX = 21               # tucked into the x0..44 wedge; glow stays clear of
BADGE_CY = 52               # the title (glyphs at x48) and the plaque (y104)
CAP_TOP = 4                 # horizontal "EARNED ×N" plate top


def _sash(surf, cx, top, bottom, w):
    """A satin gold grosgrain sash: a vertical gradient stripe with a lit
    centre crease + shadowed right fold and a fine warp seam, so it reads as a
    hanging ribbon (a medal sash), not a flat bar or a scrollbar track."""
    x0 = cx - w // 2
    strip = pygame.Surface((w, bottom - top), pygame.SRCALPHA)
    for xx in range(w):
        t = xx / max(1, w - 1)
        if t < 0.5:
            col = lerp_color(_GOLD_DEEP, _GOLD_PALE, t * 2.0)
        else:
            col = lerp_color(_GOLD_PALE, (120, 80, 14), (t - 0.5) * 2.0)
        pygame.draw.line(strip, col, (xx, 0), (xx, bottom - top))
    # bright warp seam down the lit crease + a darker selvedge on the right edge
    pygame.draw.line(strip, (*_GOLD_PALE, 200), (int(w * 0.40), 0),
                     (int(w * 0.40), bottom - top))
    pygame.draw.line(strip, (70, 44, 8), (w - 1, 0), (w - 1, bottom - top))
    surf.blit(strip, (x0, top))


def _knot(surf, cx, cy, scale=1.0):
    """A gold ribbon-knot where a hanger pinches the sash — the cue the medal
    HANGS from the ribbon. Two lit lobes + a bright pip, sized by ``scale``."""
    lob = max(2, int(3 * scale))
    for sgn in (-1, 1):
        pygame.draw.circle(surf, _GOLD_DEEP, (cx + sgn * lob, cy), lob)
        pygame.draw.circle(surf, _GOLD_PALE, (cx + sgn * lob, cy), lob, 1)
    pygame.draw.circle(surf, _GOLD_BRIGHT, (cx, cy), max(1, int(lob * 0.6)))


def _earned_cap(surf, cx, top, n):
    """A horizontal 'EARNED ×N' plate at the head of the rail — a navy lozenge
    with a gold keyline, set in upright readable type (never rotated). This is
    the self-label that turns the rail from chrome into a commendation."""
    f = _font(12, True)
    txt = f.render(f"EARNED ×{n}", True, _GOLD_PALE)
    pad_x, pad_y = 8, 4
    pw = txt.get_width() + pad_x * 2
    ph = txt.get_height() + pad_y * 2
    plate = pygame.Surface((pw, ph), pygame.SRCALPHA)
    pygame.draw.rect(plate, (*_PANEL_DARK, 240), (0, 0, pw, ph), border_radius=ph // 2)
    pygame.draw.rect(plate, _GOLD_BRIGHT, (0, 0, pw, ph), 2, border_radius=ph // 2)
    pygame.draw.line(plate, (*_GOLD_PALE, 130), (ph // 2, 1), (pw - ph // 2, 1))
    plate.blit(txt, (pad_x, pad_y))
    rect = plate.get_rect(midtop=(cx, top))
    # keep the plate inside the canvas so the left rounded end stays on-screen
    if rect.left < 1:
        rect.left = 1
    surf.blit(plate, rect)
    return rect.bottom


def _hang_badge(surf, icon_key, cx, cy, d):
    """Hang one struck medallion: a hanger link up to a ribbon knot on the sash,
    a soft cast shadow so the medal lifts off the panel, then the full badge at a
    legible diameter ``d`` — clearly a gold medallion, never a scrollbar nub."""
    r = d // 2
    knot_y = cy - r - 7
    pygame.draw.line(surf, _GOLD_DEEP, (cx, knot_y + 2), (cx, cy - r + 2), 3)
    _knot(surf, cx, knot_y, scale=1.3)
    sh = pygame.Surface((d, d), pygame.SRCALPHA)
    pygame.draw.circle(sh, (0, 0, 0, 130), (r, r), r - 1)
    surf.blit(sh, (cx - r + 3, cy - r + 4))
    rect = pygame.Rect(cx - r, cy - r, d, d)
    draw_badge(surf, icon_key, rect, True, False)


def _more_pill(surf, cx, cy, d, n):
    """A '+N' navy disc on the sash — the graceful-scaling overflow cue when a
    single run unlocks more than the cluster's shown slots."""
    r = d // 2
    knot_y = cy - r - 6
    pygame.draw.line(surf, _GOLD_DEEP, (cx, knot_y + 2), (cx, cy - r + 2), 3)
    _knot(surf, cx, knot_y, scale=1.1)
    pygame.draw.circle(surf, _GOLD_BRIGHT, (cx, cy), r + 1)
    pygame.draw.circle(surf, _PANEL_DARK, (cx, cy), r)
    pygame.draw.circle(surf, _GOLD_DEEP, (cx, cy), r, 2)
    f = _font(15, True)
    g = f.render(f"+{n}", True, _GOLD_PALE)
    surf.blit(g, g.get_rect(center=(cx, cy)))


def _build_rail(surf, ids, overflow=0):
    """Compose the rail onto ``surf``: cap → sash → medallion(s) → ribbon spine.

    Layout budget (all readable content y<104, left of the centred title and
    above the plaque): cap at the very top, then up to two Ø56 medallions hung
    on a broad sash. Below the plaque only a slim decorative spine descends the
    x0..18 gutter, so nothing protected is occluded."""
    # Cap at the very top of the wedge; the sash drops from under it to the
    # single legible medallion seated low in the wedge (BADGE_CY).
    cap_bottom = _earned_cap(surf, BADGE_CX, CAP_TOP, len(ids) + overflow)

    sash_bottom = BADGE_CY + BADGE_D // 2 + 6
    _sash(surf, BADGE_CX, cap_bottom + 2, sash_bottom, RIBBON_W)
    # forked tail closing the readable sash like a real ribbon end
    by = sash_bottom
    pygame.draw.polygon(surf, _GOLD_DEEP, [
        (BADGE_CX - RIBBON_W // 2, by - 2),
        (BADGE_CX + RIBBON_W // 2, by - 2),
        (BADGE_CX, by + 9),
    ])

    # One clearly-readable medallion is the reward; any further unlocks roll
    # into the EARNED ×N cap above, keeping the shown medal large.
    _hang_badge(surf, ach.BY_ID[ids[0]].icon_key, BADGE_CX, BADGE_CY, BADGE_D)
    return ids[:1]


def _spine(surf, top, bottom):
    """A slim decorative ribbon spine descending the dead x0..18 gutter past the
    plaque/tiles — purely ornamental continuation of the sash, kept thin and
    well inside x18 so it overhangs nothing protected."""
    sx = 6
    w = 4
    strip = pygame.Surface((w, bottom - top), pygame.SRCALPHA)
    for xx in range(w):
        t = xx / max(1, w - 1)
        col = lerp_color(_GOLD_DEEP, _GOLD_PALE, 0.5 + (0.5 - abs(t - 0.5)))
        col = (*col, 150)
        pygame.draw.line(strip, col, (xx, 0), (xx, bottom - top))
    surf.blit(strip, (sx - w // 2, top))
    pygame.draw.polygon(surf, (*_GOLD_DEEP, 150), [
        (sx - w // 2, bottom - 2), (sx + w // 2, bottom - 2), (sx, bottom + 6)])


def build():
    surf = render_backdrop()
    ids = demo_ids(2)

    shown = _build_rail(surf, ids)
    # the secondary unlock is represented as a '+1' so the legible top medal
    # stays large; both unlocks are still accounted for in the EARNED ×2 cap.
    extra = [i for i in ids if i not in shown]
    # the slim ornamental spine continues down the dead gutter, well clear of
    # the plaque (x18+) — it lives at x<=8.
    _spine(surf, 116, 626)

    OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "docs", "achievements", "unlock_notice", "medal-rail")
    os.makedirs(OUT, exist_ok=True)
    out_path = os.path.join(OUT, "round_2.png")
    pygame.image.save(surf, out_path)
    return out_path, surf, ids


def build_scale_study(primary_path):
    """A comparison board: how the rail reads at 1, 2, and 3+ unlocks (the third
    uses a '+N' cap to imply many), each on a real backdrop crop."""
    ids3 = demo_ids(2)
    pad = 12
    panel_w = 120
    board = pygame.Surface((panel_w * 3 + pad * 4, H + 40), pygame.SRCALPHA)
    board.fill((10, 6, 26, 255))

    f = _font(13, True)
    title = f.render("medal-rail · scales 1 / 2 / 3+", True, _GOLD_BRIGHT)
    board.blit(title, (pad, 8))

    cases = [
        ("1 unlocked", 1, 0),
        ("2 unlocked", 2, 0),
        ("3+ (with +N cap)", 2, 4),
    ]
    for ci, (label, nshown, overflow) in enumerate(cases):
        bd = render_backdrop()
        _build_rail(bd, ids3[:max(1, nshown)], overflow=overflow)
        _spine(bd, 116, 626)
        col = bd.subsurface(pygame.Rect(0, 0, panel_w, H)).copy()
        board.blit(col, (pad + ci * (panel_w + pad), 30))
        cf = _font(11, True)
        lab = cf.render(label, True, _GOLD_PALE)
        board.blit(lab, (pad + ci * (panel_w + pad), 30 + H + 2))

    OUT = os.path.dirname(primary_path)
    pygame.image.save(board, os.path.join(OUT, "scale_study.png"))


if __name__ == "__main__":
    path, _surf, _ids = build()
    build_scale_study(path)
    print("wrote", path)
