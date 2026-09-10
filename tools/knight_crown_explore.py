"""Round-2 exploration sheet: the LEAD HYBRID crown (CORONET silhouette ×
CIRCLET metal) for the knight+3x combo, plus two tight tunings of that one
idea — NOT five new types.

The art-director picked #1 CORONET refined toward a CORONET×CIRCLET hybrid:
three fat triangular points on a thick, rounder-bevelled warm-gold band with a
single centred ruby, seated low/back so the crimson plume rises behind it.
This round shows that hybrid in slot 1 and varies only point height and the
gem socket (ruby vs. a tiny green-$).

Each crown is drawn procedurally and composited onto the REAL knight frame
(parrot.get_knight_parrot) so we judge it at gameplay scale. Headless/dummy
SDL so it runs in CI and on any target. Output: docs/knight_crown/round_2.png.
"""
import math
import os
import pathlib

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from game import parrot
from game.knight_skin import BRASS, BRASS_HI

# ── crown palette — a half-step warmer/brighter than the helm brass ──────────
# The helm trim is BRASS (208,174,98) / BRASS_HI (255,232,168). The crown is
# the same gold-on-steel family but pushed a notch richer/royal so it reads as
# a CROWN, not just more trim. The band uses a full 5-step ramp so its bevel
# reads as a ROUNDED armour ring (a gradient top→bottom), never a flat painted
# strip: seat-shadow → bevel-dark → warm mid core → warm light → specular pip.
G_SEAT = (88, 60, 22)            # contact shadow where the band meets the dome
G_DK = (150, 110, 42)            # lower bevel (curving away from the light)
G_MID = (222, 180, 92)           # warm royal gold core (> BRASS 208,174,98)
G_LT = (244, 212, 132)           # upper-mid lit gold (between core and rim)
G_HI = (255, 238, 174)           # rim light (> BRASS_HI 255,232,168)
G_GLINT = (255, 252, 228)        # hottest specular pip
# Ruby: dark bezel, a 2-value faceted body (lower-right deeper, upper-left
# brighter) and one white spark — a single warm gem does the work.
RUBY = (196, 38, 54); RUBY_DK = (118, 16, 30)
RUBY_LT = (236, 92, 96); RUBY_HI = (255, 168, 174)
# The $-socket option: green tied to the 3x/wealth read (kept OUT of slot 1 so
# the colourblind-safe ruby stays the lead).
DOL = (70, 192, 112); DOL_DK = (22, 92, 54); DOL_HI = (192, 252, 214)


def _ruby_gem(surf, cx, cy, r):
    """Faceted ruby set into the band face. Light from the upper-left to match
    the helm: dark bezel ring, a saturated body split into a deeper lower-right
    and a brighter upper-left facet, then one white spark. Two body values are
    what make a 4-5px stone read as cut rather than a flat dot."""
    # bezel ring (one px proud of the body all round)
    pygame.draw.circle(surf, RUBY_DK, (cx, cy), r + 1)
    # deeper body fills the whole stone, then the lit facet is laid upper-left
    pygame.draw.circle(surf, RUBY, (cx, cy), r)
    pygame.draw.circle(surf, RUBY_LT, (cx - 1, cy - 1), max(1, r - 1))
    # tiny bright facet + a single white spark, both upper-left
    pygame.draw.circle(surf, RUBY_HI, (cx - 1, cy - 1), max(1, r // 2))
    surf.set_at((cx - 1, cy - 1), (255, 255, 255))


def _dollar_gem(surf, cx, cy, r):
    """Same socket as the ruby but a tiny green '$' coin: green disc, dark
    bezel, a crisp light-green stroke. The alternate 'wealth' read."""
    pygame.draw.circle(surf, DOL_DK, (cx, cy), r + 1)
    pygame.draw.circle(surf, DOL, (cx, cy), r)
    # vertical bar + two short serif tails reads as '$' even at 2-3px radius
    pygame.draw.line(surf, DOL_HI, (cx, cy - r), (cx, cy + r), 1)
    surf.set_at((cx - 1, cy - r + 1), DOL_HI)
    surf.set_at((cx + 1, cy + r - 1), DOL_HI)
    surf.set_at((cx, cy), DOL_HI)


def _band(surf, x0, x1, y, h):
    """Thick coronet band with CIRCLET-grade ROUNDED bevel. Rather than one
    flat strip + outline, the band is a top→bottom value ramp — bevel-dark
    along the bottom, warm core through the middle, a bright lit row near the
    top and a thin specular rim hugging the upper-left — so it reads as a
    curved armour ring catching upper-left light. ~1.3x the round-1 band (h=7).
    """
    w = x1 - x0
    # contact shadow where gold meets the steel dome
    pygame.draw.rect(surf, G_SEAT, (x0, y + h, w, 1))
    # full-height bevel-dark base; successive insets from the BOTTOM build the
    # rounded ramp so the lower edge stays dark and the light climbs the face
    pygame.draw.rect(surf, G_DK, (x0, y, w, h))
    pygame.draw.rect(surf, G_MID, (x0 + 1, y + 1, w - 2, h - 2))
    # upper-mid lit row + bright rim row sit in the top of the band only
    pygame.draw.rect(surf, G_LT, (x0 + 1, y + 1, w - 2, 2))
    pygame.draw.rect(surf, G_HI, (x0 + 2, y + 1, w - 4, 1))
    # the brightest specular climbs toward the upper-LEFT corner of the band
    surf.set_at((x0 + 3, y + 1), G_GLINT)
    surf.set_at((x0 + 2, y + 2), G_GLINT)


def _fat_point(surf, cx, base_y, top_y, half):
    """A fat, clearly triangular gold point (base width = 2*half, kept >=3px).
    Same rounded-metal read as the band: a dark bevel triangle, a warm core
    inset off the right/under edges, a lit upper-left face climbing to the tip,
    and a glint pip. No thin spikes."""
    # dark full triangle (bevel/shadow)
    pygame.draw.polygon(surf, G_DK, [(cx - half, base_y), (cx + half, base_y), (cx, top_y)])
    # warm core, inset on the right/underside so the dark shows as edge bevel
    pygame.draw.polygon(surf, G_MID, [(cx - half + 1, base_y), (cx + half - 1, base_y), (cx, top_y + 2)])
    # lit upper-left face: a filled sliver hugging the left edge up to the tip
    pygame.draw.polygon(surf, G_LT, [(cx - half + 1, base_y), (cx - half + 2, base_y), (cx, top_y + 2), (cx, top_y + 3)])
    pygame.draw.line(surf, G_HI, (cx - half + 2, base_y - 1), (cx, top_y + 1), 1)
    surf.set_at((cx, top_y + 1), G_GLINT)


def _coronet(surf, cx, cy, point_dh=0, gem="ruby"):
    """LEAD HYBRID: thick warm-gold band + three fat triangular points (centre
    tallest), one centred gem in the band face. `point_dh` nudges point height
    (-1/0/+1 native px); `gem` is 'ruby' or 'dollar'."""
    half = 11
    h = 7                       # ~1.3x the round-1 band (was 5, mostly 4)
    by = cy
    # points sit UNDER the band draw so the band's lit top edge crosses cleanly
    # in front of each point base — the points read as rising FROM the ring.
    ch = 9 + point_dh           # centre point height above the band top
    sh = 6 + point_dh           # side point height
    for dx, ph, hw in ((-8, sh, 3), (0, ch, 3), (8, sh, 3)):
        _fat_point(surf, cx + dx, by + 2, by - ph, hw)
    _band(surf, cx - half, cx + half, by, h)
    # gem seated in the band face, centred over the brow
    if gem == "ruby":
        _ruby_gem(surf, cx, by + h // 2 + 1, 2)
    else:
        _dollar_gem(surf, cx, by + h // 2 + 1, 2)


# ── the three round-2 tunings (one idea, tight variations) ───────────────────
def draw_a(surf, cx, cy):
    """A — LEAD HYBRID, baseline: centre point 9px, ruby socket."""
    _coronet(surf, cx, cy, point_dh=0, gem="ruby")


def draw_b(surf, cx, cy):
    """B — points +1px taller (more regal silhouette), ruby socket."""
    _coronet(surf, cx, cy, point_dh=1, gem="ruby")


def draw_c(surf, cx, cy):
    """C — baseline points, green-$ socket instead of the ruby (wealth read)."""
    _coronet(surf, cx, cy, point_dh=0, gem="dollar")


CANDIDATES = [
    ("A  HYBRID · ruby",        draw_a),
    ("B  +1px points · ruby",   draw_b),
    ("C  $-socket",             draw_c),
]


# ── helm-crown anchor on the real knight frame ───────────────────────────────
# Knight char surface is (SPRITE_W+2*PAD, SPRITE_H+2*PAD). The armet helm is
# blitted at _P(nom,0.73,0.17) at size (nom.w*0.5, nom.h*0.54). Round 1 seated
# the band at HELM_TOP+5; the director asked to drop ~2px LOWER and slightly
# BACK onto the dome so the plume clears behind the crown.
PAD = 16
NOM_X = PAD; NOM_Y = PAD
HELM_CX = NOM_X + 0.73 * parrot.SPRITE_W
HELM_TOP = NOM_Y + 0.17 * parrot.SPRITE_H - 0.54 * parrot.SPRITE_H * 0.5
CROWN_CX = int(HELM_CX) - 1        # ~1px back toward the dome crest
CROWN_CY = int(HELM_TOP + 7)       # ~2px lower than round 1 (was +5)


def _knight_with_crown(crown_fn):
    """Real knight frame 0 (flat tilt) with the candidate crown drawn on the
    helm dome. Returns the full char surface."""
    base = parrot.get_knight_parrot(0, 0.0)
    surf = base.copy()
    crown_fn(surf, CROWN_CX, CROWN_CY)
    return surf


def main():
    pygame.font.init()
    label_font = pygame.font.SysFont("dejavusans", 14, bold=True)
    sub_font = pygame.font.SysFont("dejavusans", 10)

    BG = (38, 44, 58)
    PANEL = (28, 33, 44)
    INK = (232, 238, 250)
    DIM = (150, 160, 180)

    cols = 3
    cell_w = 270
    cell_h = 500
    head_h = 60
    sheet = pygame.Surface((cols * cell_w, head_h + cell_h), pygame.SRCALPHA)
    sheet.fill(BG)

    title = pygame.font.SysFont("dejavusans", 18, bold=True).render(
        "Knight + 3x  —  METALLIC CROWN  ·  round 2  (CORONET x CIRCLET hybrid)", True, INK)
    sheet.blit(title, (16, 13))
    subtitle = sub_font.render(
        "lead hybrid + tight tunings  ·  real knight armet helm  ·  top = ~2x play scale  ·  bottom = 5x detail",
        True, DIM)
    sheet.blit(subtitle, (18, 40))

    for i, (name, fn) in enumerate(CANDIDATES):
        x0 = i * cell_w
        panel = pygame.Rect(x0 + 8, head_h + 6, cell_w - 16, cell_h - 12)
        pygame.draw.rect(sheet, PANEL, panel, border_radius=8)
        pygame.draw.rect(sheet, (60, 70, 90), panel, width=1, border_radius=8)

        lab = label_font.render(name, True, (255, 226, 150))
        sheet.blit(lab, (panel.x + 12, panel.y + 8))

        composed = _knight_with_crown(fn)

        # ~2x play-scale tile (no smoothing — show the real native read)
        s2 = pygame.transform.scale(
            composed, (composed.get_width() * 2, composed.get_height() * 2))
        sheet.blit(s2, (panel.centerx - s2.get_width() // 2, panel.y + 32))

        cap = sub_font.render("~2x play scale", True, DIM)
        sheet.blit(cap, (panel.centerx - s2.get_width() // 2, panel.y + 32 + s2.get_height() + 2))

        # 5x detail crop — zoom the head/helm region only
        crop = pygame.Rect(int(CROWN_CX - 28), int(CROWN_CY - 17), 56, 56)
        crop = crop.clamp(composed.get_rect())
        head = composed.subsurface(crop).copy()
        s5 = pygame.transform.scale(head, (head.get_width() * 5, head.get_height() * 5))
        sub_x = panel.centerx - s5.get_width() // 2
        sub_y = panel.y + 32 + s2.get_height() + 24
        pygame.draw.rect(sheet, (20, 24, 32), (sub_x - 2, sub_y - 2, s5.get_width() + 4, s5.get_height() + 4))
        sheet.blit(s5, (sub_x, sub_y))
        cap2 = sub_font.render("5x detail", True, DIM)
        sheet.blit(cap2, (sub_x, sub_y + s5.get_height() + 2))

    out_dir = pathlib.Path("/home/user/skybit/docs/knight_crown")
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "round_2.png"
    pygame.image.save(sheet, str(out))
    print("WROTE", out, sheet.get_size())


if __name__ == "__main__":
    main()
