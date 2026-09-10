"""Round-1 review render for the FULL-BLEED store-card size concept.

The character breaks containment: instead of sitting inside a glass cabochon
disc, the hero clips edge-to-edge to the card's own rounded-rect at _BOX_PX=118,
filling the frame like a poster. The glass dome demotes to a radial tier glow
plus a 180 degree top-arc gold rim — a SUGGESTED aperture, not an enclosure.
Ribbon + name compress into a scrimmed lower band; the crest gem stays.

Review-only: this does NOT edit game/store_cards.py. It reuses that module's
locked primitives through a local draw_card_fullbleed() so the exploration reads
exactly like the shipped card art, minus the swapped BAND A treatment.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import math
import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from game import store_cards as sc
from game.store_cards import m

# Full-bleed hero box in device px (was 84 in the shipped card).
_FB_BOX = 118
# Suggested-aperture arc radius (device px) for the 180deg top rim.
_FB_ARC_R = 66

# A deep night-sky body so the concept reads against the NIGHT biome.
_NIGHT_T = (14, 16, 44)
_NIGHT_B = (5, 6, 22)


def _rounded_mask(size, radius):
    mask = pygame.Surface(size, pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, size[0], size[1]),
                     border_radius=radius)
    return mask


def draw_card_fullbleed(surf, sid, rect, equipped, secret, night=False):
    """draw_card, but BAND A is the full-bleed hero: the thumbnail clips to the
    body rounded-rect edge-to-edge, backed by the tier glow, fronted by a
    top-arc gold rim. Ribbon/name/chip compress into a scrimmed lower band."""
    pal = sc.MYSTERY if secret else sc.RARITY[sc._rarity(sid)]
    rad = m(sc.CARD_RAD)

    # BODY STACK — identical to the shipped card so the frame reads the same.
    sc.drop_shadow(surf, rect, rad, blur=m(8), alpha=160, dy=m(4))
    top, bot = (_NIGHT_T, _NIGHT_B) if night else (sc.CARD_T, sc.CARD_B)
    surf.blit(sc.vgrad(rect.w, rect.h, rad, top, bot, 252, gamma=1.15),
              rect.topleft)
    sc.top_sheen(surf, rect, rad, m(30), peak=62)
    sc.contact_shadow(surf, rect, rad, m(9), alpha=120)
    pygame.draw.rect(surf, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    sc.bevel_rim(surf, rect, rad, sc.CARD_RING_DEEP, (*sc.CARD_RING_BRIGHT, 235),
                 w=max(1, m(2.0)))

    # HERO — the whole card face. Compose glow + oversized thumb on a temp
    # layer, then mask it to the body rounded-rect so it bleeds to the bevel.
    cx, cy = rect.centerx, rect.y + m(sc.CY_DISC) + sc._DOME_DY
    hero = pygame.Surface(rect.size, pygame.SRCALPHA)
    lx, ly = cx - rect.x, cy - rect.y
    # tier aura behind the hero — the radial glow the demoted dome leaves behind.
    sc.soft_glow(hero, lx, ly, _FB_ARC_R + m(10), pal["glow"], 46, layers=10)
    if secret:
        sc._draw_qmark(hero, lx, ly, m(28), sc.CREAM, sc.NEAR_BLACK, thick=m(2))
        name = "???"
    else:
        sc.blit_thumb(hero, sid, lx, ly - sc._ITEM_DY, _FB_BOX)
        name = sc._name(sid)
    hero.blit(_rounded_mask(rect.size, rad), (0, 0),
              special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(hero, rect.topleft)

    # SUGGESTED APERTURE — a 180deg top-arc gold rim (0..pi), a couple of passes
    # for a soft rim. Not an enclosure — the lower half stays open.
    arc_box = pygame.Rect(cx - _FB_ARC_R, cy - _FB_ARC_R, _FB_ARC_R * 2, _FB_ARC_R * 2)
    for k, a in ((0, 235), (m(1), 120)):
        b = arc_box.inflate(-2 * k, -2 * k)
        pygame.draw.arc(surf, (*sc.CARD_RING_BRIGHT, a), b, 0.0, math.pi,
                        max(1, m(1.6)))

    # inner tray keylines, drawn OVER the hero so the frame stays crisp.
    tray = rect.inflate(-m(7), -m(7))
    trad = rad - m(4)
    pygame.draw.rect(surf, (*sc.CARD_RING_BRIGHT, 90), tray, width=max(1, m(1)),
                     border_radius=trad)

    # CREST GEM — kept top-right; the enlarged hero can crowd it, so nudge it a
    # touch further into the corner than the shipped card.
    sc.facet_gem(surf, rect.right - m(18), rect.y + m(18), m(sc.GEM_R + 3),
                 pal["gem"], pal["deep"], mystery=secret)

    # LOWER BAND — a bottom scrim keeps the compressed ribbon/name/chip legible
    # over the full-bleed hero, then the three lanes tucked tight to the foot.
    band_h = m(46)
    scrim = pygame.Surface((rect.w, band_h), pygame.SRCALPHA)
    for y in range(band_h):
        a = int(210 * (y / max(1, band_h - 1)) ** 1.3)
        pygame.draw.line(scrim, (5, 6, 20, a), (0, y), (rect.w, y))
    scrim.blit(_rounded_mask((rect.w, band_h), rad), (0, -m(20)),
               special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(scrim, (rect.x, rect.bottom - band_h))

    tier_word = "MYSTERY" if secret else sc._rarity(sid).upper()
    sc._ribbon_lozenge(surf, tier_word, cx, rect.y + m(56), rect.w - m(34), pal)
    sc._name_on(surf, name, cx, rect.y + m(72), rect.w - m(26))
    sc.state_chip(surf, sid, cx, rect.y + m(88) - sc._CHIP_DY, equipped, secret,
                  m(20))


def _big_surface(draw_fn):
    """Author a full device-res 324x200 card via a draw callback, matching
    render_card's inset body rect so shadow + halo land on-surface."""
    big = pygame.Surface((sc.CARD_W * sc.SS, sc.CARD_H * sc.SS), pygame.SRCALPHA)
    rect = pygame.Rect(m(sc._INSET), m(sc._INSET),
                       sc.CARD_W * sc.SS - 2 * m(sc._INSET),
                       sc.CARD_H * sc.SS - 2 * m(sc._INSET))
    draw_fn(big, rect)
    return big


def _baseline_big(sid):
    return _big_surface(lambda s, r: sc.draw_card(s, sid, r, False, False))


def _concept_big(sid, night=False):
    return _big_surface(
        lambda s, r: draw_card_fullbleed(s, sid, r, False, False, night=night))


def main():
    label_f = pygame.font.SysFont("dejavusans", 15, bold=True)
    small_f = pygame.font.SysFont("dejavusans", 12)

    BW, BH = sc.CARD_W * sc.SS, sc.CARD_H * sc.SS      # 324 x 200 device panel
    ONE_W, ONE_H = sc.CARD_W, sc.CARD_H                # 162 x 100 downscaled

    pad = 22
    lab_h = 26
    row1 = [
        ("BASELINE  mummy / day", _baseline_big("skin_mummy")),
        ("FULL-BLEED  mummy / day", _concept_big("skin_mummy")),
        ("FULL-BLEED  mummy / NIGHT", _concept_big("skin_mummy", night=True)),
        ("FULL-BLEED  astronaut (legendary)", _concept_big("skin_astronaut")),
    ]
    row2 = [
        ("baseline mummy", pygame.transform.smoothscale(_baseline_big("skin_mummy"), (ONE_W, ONE_H))),
        ("concept mummy", pygame.transform.smoothscale(_concept_big("skin_mummy"), (ONE_W, ONE_H))),
        ("concept ninja (rare)", pygame.transform.smoothscale(_concept_big("skin_ninja"), (ONE_W, ONE_H))),
        ("concept astronaut (leg.)", pygame.transform.smoothscale(_concept_big("skin_astronaut"), (ONE_W, ONE_H))),
    ]

    cols = 4
    row1_w = cols * BW + (cols + 1) * pad
    sheet_w = row1_w
    r1_y = pad + lab_h
    r2_y = r1_y + lab_h + BH + pad * 2
    sheet_h = r2_y + lab_h + ONE_H + pad

    sheet = pygame.Surface((sheet_w, sheet_h), pygame.SRCALPHA)
    sheet.fill((8, 8, 20))

    title = label_f.render(
        "Store card size — FULL-BLEED concept — round 1", True, (236, 224, 190))
    sheet.blit(title, (pad, 4))

    # Row 1 — device-res 324x200 panels.
    for i, (lab, surfimg) in enumerate(row1):
        x = pad + i * (BW + pad)
        sheet.blit(small_f.render(lab, True, (210, 214, 230)), (x, r1_y))
        sheet.blit(surfimg, (x, r1_y + lab_h))

    # Row 2 — 1x downscaled cards, on a night patch under the concept ones.
    for i, (lab, surfimg) in enumerate(row2):
        x = pad + i * (BW + pad) + (BW - ONE_W) // 2
        sheet.blit(small_f.render(lab, True, (200, 204, 222)), (x, r2_y))
        sheet.blit(surfimg, (x, r2_y + lab_h))

    out = "docs/store_card_size/full_bleed/round_1.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print(f"saved {sheet.get_width()}x{sheet.get_height()} -> {out}")


if __name__ == "__main__":
    main()
