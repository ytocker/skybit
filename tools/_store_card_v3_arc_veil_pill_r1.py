"""arc-veil-pill — store_card_v3 concept, round 1 headless render.

A large medallion hero (R=35) on a visible indigo body — same "maximum skin,
minimum chrome" DNA as v2 bezel-hero — but the label now lands as a physical
FROSTED STRADDLE-BAND mounted across the glass dome's 6-o'clock: the band
bridges the bezel (top half over the dome exterior, bottom half on the card
body) so the name reads as an engraved plate, not floating type. Price drops to
a tier-coloured dark-glass PILL below the band (no gold chip, no coin glyph) so
the whole lower stack carries the tier hue.

Reuses v2's gutter aura + disc tint verbatim; only render_card()'s lower layout
is new. Headless (SDL dummy) → a 3-up RARE/EPIC/LEGENDARY review sheet at SS
(324×200, no downscale) + a real-scale 1x strip (162×100). Not wired into the
live store; writes docs/store_card_v3/arc-veil-pill/round_1.png.
"""
import os

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import sys

sys.path.insert(0, "/home/user/skybit")

import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from game.draw import lerp_color
from game.hud import _font
from game.store_cards import (
    vgrad, drop_shadow, bevel_rim, top_sheen, contact_shadow,
    cabochon, cabochon_glass, blit_thumb, facet_gem, plain_text,
    font, m, SS, CABO_LO, CABO_HI, CARD_T, CARD_B,
    CARD_RING_DEEP, CARD_RING_BRIGHT, GEM_R,
)

# LOCKED card constants (from store_cards).
CARD_W, CARD_H = 162, 100
CARD_RAD = 17
_INSET = 6

# The hero medallion: R=35 logical leaves a ~40px indigo gutter left/right — the
# whole point of the concept, and the room the tier halo needs to be visible.
R = 35

# Disc centre a touch higher than v2's 40 so the disc's 6-o'clock leaves a hair
# of body below for the straddle-band + pill to sit on.
CY = 38


def _disc_tint(surf, cx, cy, r, color, deep, peak=52, base=16):
    """A tier colour veil INSIDE the disc, clipped to the glass. It warms the
    cool CABO_LO→CABO_HI dome away from the indigo body, and — carrying a modest
    centre alpha — pulls any near-white skin highlight toward the tier hue so the
    hero never reads pure (255,255,255). Rim-biased (deeper toward the edge)
    reads as a coloured dome, not a flat cast."""
    pad = 2
    tint = pygame.Surface((r * 2 + pad * 2, r * 2 + pad * 2), pygame.SRCALPHA)
    c = r + pad
    for i in range(r, 0, -1):
        f = i / r                                   # 1 at rim, 0 at centre
        col = lerp_color(color, deep, f ** 1.3)
        a = int(base + (peak - base) * f ** 1.6)    # base at centre, peak at rim
        pygame.draw.circle(tint, (*col, a), (c, c), i, width=2)
    tmask = pygame.Surface(tint.get_size(), pygame.SRCALPHA)
    pygame.draw.circle(tmask, (255, 255, 255, 255), (c, c), r - m(1))
    tint.blit(tmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(tint, (cx - c, cy - c))


def _gutter_aura(surf, cx, cy, disc_r, glow_r, color, peak=90, layers=18):
    """A feathered tier halo that lives ONLY beyond the disc rim (radius >
    disc_r), so it floods the side gutters with tier colour without touching —
    or blowing out — the hero inside the glass. Normal alpha-carry blits (NOT
    additive) so the colour survives compositing and reads as a tint, not a hot
    white bloom. Brightest at the rim, feathering out into the gutter."""
    for i in range(1, layers + 1):
        r = int(disc_r + (glow_r - disc_r) * i / layers)
        if r <= disc_r:
            continue
        a = int(peak * (1 - (i - 1) / layers) ** 1.6)
        if a <= 0:
            continue
        w = max(2, int((glow_r - disc_r) / layers) + m(1.5))
        g = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(g, (*color, a), (r + 1, r + 1), r, width=w)
        surf.blit(g, (cx - r - 1, cy - r - 1))


def _fit_font(txt, max_w, base_size, min_size=6):
    """Largest logical font size whose rendered width fits max_w (device px), so
    a long skin name auto-shrinks inside the fixed straddle-band."""
    s = base_size
    while s > min_size:
        f = font(s)
        if f.size(txt)[0] <= max_w:
            return f
        s -= 1
    return font(min_size)


def render_card(sid, pal, price, name):
    """Draw ONE arc-veil-pill card onto a fresh SS panel (324×200) and return it.
    Drawn directly at SS (no smoothscale) so the review sheet inspects the
    geometry at author resolution."""
    big = pygame.Surface((CARD_W * SS, CARD_H * SS), pygame.SRCALPHA)
    rect = pygame.Rect(m(_INSET), m(_INSET),
                       CARD_W * SS - 2 * m(_INSET), CARD_H * SS - 2 * m(_INSET))
    rad = m(CARD_RAD)
    body_y = m(_INSET)
    cx, cy = rect.centerx, rect.y + m(CY)

    # 1. depth: soft multi-layer drop shadow (top-left light → offset down).
    drop_shadow(big, rect, rad, blur=m(8), alpha=160, dy=m(4))
    # 2. body gradient (indigo CARD_T → CARD_B).
    big.blit(vgrad(rect.w, rect.h, rad, CARD_T, CARD_B, 252, gamma=1.15),
             rect.topleft)
    # 3. glossy top sheen.
    top_sheen(big, rect, rad, m(30), peak=62)
    # 4. bottom-right contact AO.
    contact_shadow(big, rect, rad, m(9), alpha=120)
    # 5. inner tray dark border + faint gold lane so the body edge frames the
    #    disc even at "minimum chrome".
    tray = rect.inflate(-m(7), -m(7))
    trad = rad - m(4)
    pygame.draw.rect(big, (10, 10, 24, 200), tray.inflate(m(2), m(2)),
                     width=max(1, m(1)), border_radius=trad + m(1))
    pygame.draw.rect(big, (*CARD_RING_BRIGHT, 90), tray, width=max(1, m(1)),
                     border_radius=trad)

    # 6. the domed glass well → hero skin.
    cabochon(big, cx, cy, m(R), CABO_LO, CABO_HI, ring=pal["gem"], ring_a=60)
    blit_thumb(big, sid, cx, cy, m(R) * 1.5)

    # 7. tier tint INSIDE the disc — warms the glass per tier and pulls any
    #    near-white skin highlight toward the tier hue.
    _disc_tint(big, cx, cy, m(R), pal["glow"], pal["deep"])

    # 8. glass dome overlay (crescent sheen + gold bezel) on top of the tint.
    cabochon_glass(big, cx, cy, m(R), tint=pal["gem"])

    # 9. ONE tier-coloured bezel ring at R+2 (the whole edge treatment).
    pygame.draw.circle(big, (*pal["gem"], 100), (cx, cy), m(R) + m(2), width=m(2))

    # 10. tier read: a gutter-only feathered halo that floods the side gutters.
    _gutter_aura(big, cx, cy, m(R), m(R + 28), pal["glow"], peak=90, layers=18)

    # 11. NAME — a frosted straddle-band mounted ACROSS the dome's 6-o'clock:
    #     top half over the glass exterior, bottom half on the body, so the name
    #     reads as a physical plate bolted to the medallion. Drawn AFTER the
    #     glass so it sits ON the dome, not under it.
    band_w, band_h = m(100), m(14)
    band_cx, band_cy = cx, cy + m(R)             # centred on the disc bottom edge
    band_rect = pygame.Rect(band_cx - band_w // 2, band_cy - band_h // 2,
                            band_w, band_h)
    band_rad = m(6)
    # frosted cool-indigo plate (translucent so the dome reads faintly through).
    big.blit(vgrad(band_w, band_h, band_rad, (44, 46, 90), (28, 30, 68), 210),
             band_rect.topleft)
    # 1px bright top glint → the plate catches the top-left light like a bevel.
    pygame.draw.line(big, (180, 190, 220),
                     (band_rect.x + band_rad, band_rect.y + max(1, m(0.5))),
                     (band_rect.right - band_rad, band_rect.y + max(1, m(0.5))),
                     max(1, m(0.6)))
    # cream engraved name, auto-shrunk to the plate width.
    nfont = _fit_font(name, band_w - m(14), 11)
    plain_text(big, name, nfont, (band_cx, band_cy + m(0.5)), (246, 240, 216),
               shadow_a=120, keyline=(12, 12, 30), kw=max(1, m(0.7)))

    # 12. PRICE — a tier-coloured dark-glass pill below the band (no gold chip,
    #     no coin glyph): the lower stack carries the tier hue end to end.
    price_txt = f"{price:,}"
    pfont = font(11)
    pill_h = m(15)
    pill_w = pfont.size(price_txt)[0] + m(18)
    pill_cx, pill_cy = cx, body_y + m(80)
    pill_rect = pygame.Rect(pill_cx - pill_w // 2, pill_cy - pill_h // 2,
                           pill_w, pill_h)
    pill_rad = pill_h // 2
    pill = pygame.Surface((pill_w, pill_h), pygame.SRCALPHA)
    pygame.draw.rect(pill, (*pal["deep"], 215), pill.get_rect(),
                     border_radius=pill_rad)
    pygame.draw.rect(pill, (*pal["gem"], 80), pill.get_rect(),
                     width=max(1, m(0.7)), border_radius=pill_rad)
    big.blit(pill, pill_rect.topleft)
    plain_text(big, price_txt, pfont, (pill_cx, pill_cy), pal["gem"],
               shadow_a=130, keyline=(8, 8, 20), kw=max(1, m(0.6)))

    # 13. crest gem — faceted tier badge, top-right corner.
    facet_gem(big, rect.right - m(19), rect.y + m(19), m(GEM_R + 3),
              pal["gem"], pal["deep"])

    # 14. bevel rim + dark keyline LAST so the card frame stays crisp over the
    #     halo that bleeds to the body edge.
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 235),
              w=max(1, m(2.0)))
    return big, (cx, cy)


# ── review sheet ──────────────────────────────────────────────────────────────
VARIANTS = [
    ("RARE",      "skin_lorikeet", {"gem": (108, 188, 252), "glow": (60, 140, 230), "deep": (18, 44, 90)},  600,  "Lorikeet"),
    ("EPIC",      "skin_prism",    {"gem": (194, 122, 248), "glow": (140, 40, 230), "deep": (44, 10, 80)},  1400, "Prism"),
    ("LEGENDARY", "skin_kitsune",  {"gem": (255, 202, 104), "glow": (220, 160, 40), "deep": (90, 50, 0)},   3500, "Kitsune"),
]

PANEL_W, PANEL_H = CARD_W * SS, CARD_H * SS   # 324 × 200 (SS panels, no downscale)
MARGIN = 20
GUTTER = 16
HEADER_H = 30
FOOTER_H = 24
STRIP_LABEL_H = 20
STRIP_H = CARD_H                              # real-scale 1x cards (162×100)

sheet_w = MARGIN * 2 + PANEL_W * 3 + GUTTER * 2
sheet_h = (MARGIN + HEADER_H + PANEL_H + FOOTER_H + STRIP_LABEL_H + STRIP_H
           + MARGIN)
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((16, 17, 30))

hfont = _font(22, True)
ffont = _font(20, True)
sfont = _font(16, True)
htxt = hfont.render("store_card_v3 — arc-veil-pill — round 1", True, (236, 232, 214))
sheet.blit(htxt, (MARGIN, MARGIN + (HEADER_H - htxt.get_height()) // 2))

panel_y = MARGIN + HEADER_H
panels = []
centers = []
for i, (tier, sid, pal, price, name) in enumerate(VARIANTS):
    px = MARGIN + i * (PANEL_W + GUTTER)
    panel, ctr = render_card(sid, pal, price, name)
    panels.append(panel)
    centers.append(ctr)
    sheet.blit(panel, (px, panel_y))
    ftxt = ffont.render(tier, True, (218, 214, 200))
    sheet.blit(ftxt, (px + (PANEL_W - ftxt.get_width()) // 2,
                      panel_y + PANEL_H + (FOOTER_H - ftxt.get_height()) // 2))

# 1x real-scale strip: smoothscale each SS panel down to the live 162×100 card
# so the sheet also shows how the card reads at true size.
strip_label_y = panel_y + PANEL_H + FOOTER_H
ltxt = sfont.render("real scale (1×, 162×100):", True, (200, 204, 220))
sheet.blit(ltxt, (MARGIN, strip_label_y + (STRIP_LABEL_H - ltxt.get_height()) // 2))
strip_y = strip_label_y + STRIP_LABEL_H
for i, panel in enumerate(panels):
    px = MARGIN + i * (PANEL_W + GUTTER)
    small = pygame.transform.smoothscale(panel, (CARD_W, CARD_H))
    sheet.blit(small, (px + (PANEL_W - CARD_W) // 2, strip_y))

out = "/home/user/skybit/docs/store_card_v3/arc-veil-pill/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())

# sanity: gutter tier tint (15px past the disc edge), disc centre (not blown to
# white), the frosted band plate, and the tier pill body.
for (tier, sid, pal, price, name), panel, (cx, cy) in zip(VARIANTS, panels, centers):
    gx = cx + m(R) + m(15)
    gutter_px = panel.get_at((gx, cy))[:3]
    center_px = panel.get_at((cx, cy))[:3]
    band_px = panel.get_at((cx, cy + m(R)))[:3]
    pill_px = panel.get_at((cx, m(_INSET) + m(80)))[:3]
    print(f"{tier:9s} gutter+15 {gutter_px}  centre {center_px}  "
          f"band {band_px}  pill {pill_px}")
