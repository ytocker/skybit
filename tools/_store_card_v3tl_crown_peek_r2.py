"""crown-peek — store_card_v3_tl concept, round 2 headless render.

A high-domed "crowned" card whose hero disc BURSTS out of the top frame:
the dome crown is hard-clipped by the outer gold bounding rect (top at
≈ -m(20) in surface coords), so the glass looks like it is escaping a box
rather than sitting contained in it. A crisp inner tray rect gives the
dome a real boundary to overrun, with a contact-shadow strip where the
glass punches through the tray line. The gem crest tucks top-LEFT, a warm
metallic price badge counterweights it top-RIGHT, and the item name lands
on an engraved gold-rimmed plaque low in the body. Rarity rides the gutter
halo (steel-blue / violet / warm-gold) + in-disc tint veil.

Headless (SDL dummy) → a 3-up RARE/EPIC/LEGENDARY review sheet at SS
(324×200, no downscale) + a real-scale 1x strip (162×100). Not wired into
the live store; writes docs/store_card_v3_tl/crown-peek/round_2.png.
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

# The crowned hero disc: R=28 logical, riding HIGH enough that the dome top
# clears the whole surface and is HARD-CLIPPED by the outer gold frame — the
# dome bursts out of the box instead of sitting contained inside it.
R = 28


def _disc_tint(surf, cx, cy, r, color, deep, peak=55, base=22):
    """A tier colour veil INSIDE the disc, clipped to the glass. It warms the
    cool CABO_LO→CABO_HI dome away from the indigo body, and — carrying a
    meaningful centre alpha — pulls a bright skin highlight toward the tier hue
    so it stops blowing out. The gentle exponent lets the hue carry inward
    instead of collapsing at the centre; the veil stays rim-biased (peak > base)
    so the hero reads through while the surround takes the tier hue."""
    pad = 2
    tint = pygame.Surface((r * 2 + pad * 2, r * 2 + pad * 2), pygame.SRCALPHA)
    c = r + pad
    for i in range(r, 0, -1):
        f = i / r                                   # 1 at rim, 0 at centre
        col = lerp_color(color, deep, f ** 1.3)
        a = int(base + (peak - base) * f ** 1.3)    # base at centre, peak at rim
        pygame.draw.circle(tint, (*col, a), (c, c), i, width=2)
    tmask = pygame.Surface(tint.get_size(), pygame.SRCALPHA)
    pygame.draw.circle(tmask, (255, 255, 255, 255), (c, c), r - m(1))
    tint.blit(tmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(tint, (cx - c, cy - c))


def _gutter_aura(surf, cx, cy, disc_r, glow_r, color, peak=110, layers=18):
    """A feathered tier halo that lives ONLY beyond the disc rim (radius >
    disc_r), so it floods the side gutters with tier colour without touching —
    or blowing out — the hero inside the glass. Normal alpha-carry blits (NOT
    additive) so the colour survives compositing and reads as a measurable
    colored ring in the gutters, not a hot white bloom. Brightest at the rim,
    feathering out into the gutter."""
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


ITEM_NAMES = {"skin_lorikeet": "Lorikeet", "skin_prism": "Prism",
              "skin_kitsune": "Kitsune"}


def render_crown_peek(sid, pal, price):
    """Draw ONE crown-peek card onto a fresh SS panel (324×200) and return it
    (drawn directly at SS, no smoothscale) plus the disc centre."""
    big = pygame.Surface((CARD_W * SS, CARD_H * SS), pygame.SRCALPHA)
    rect = pygame.Rect(m(_INSET), m(_INSET),
                       CARD_W * SS - 2 * m(_INSET), CARD_H * SS - 2 * m(_INSET))
    rad = m(CARD_RAD)

    # Disc centre rides so high the dome top (cy - m(R) = m(8) - m(28) = -m(20))
    # is well above the surface and HARD-CLIPS against the outer card top edge —
    # the crown bursts out of the frame rather than nestling under the tray.
    cx, cy = rect.centerx, m(_INSET) + m(8)

    # 1. depth: soft multi-layer drop shadow (top-left light → offset down).
    drop_shadow(big, rect, rad, blur=m(8), alpha=160, dy=m(4))
    # 2. body gradient (indigo CARD_T → CARD_B).
    big.blit(vgrad(rect.w, rect.h, rad, CARD_T, CARD_B, 252, gamma=1.15),
             rect.topleft)
    # 3. glossy top sheen.
    top_sheen(big, rect, rad, m(16), peak=45)
    # 4. bottom-right contact AO.
    contact_shadow(big, rect, rad, m(9), alpha=100)

    # 5. INNER TRAY boundary — a crisp recessed rect the dome bursts UP over. Its
    #    bright top keyline is the physical edge the glass overruns; without a
    #    real line the "peek" reads as containment, not escape.
    tray = rect.inflate(-m(10), -m(10))
    trad = rad - m(5)
    pygame.draw.rect(big, (*CARD_RING_BRIGHT, 180), tray,
                     width=max(1, m(2)), border_radius=trad)

    # ── crowned hero disc + its gutter halo, on a MASKED layer ──
    # The dome + halo overrun the tray AND the outer rect top. We draw the whole
    # stack onto its own transparent layer, then clip that layer to the OUTER
    # rounded rect via BLEND_RGBA_MIN — so the crest bursts over the inner tray
    # yet is cut cleanly at the gold bevel and never leaks into the drop-shadow
    # margin above the card. Masking a SEPARATE layer (not `big`) keeps the
    # min-blend off the already-composited body.
    layer = pygame.Surface((CARD_W * SS, CARD_H * SS), pygame.SRCALPHA)
    _gutter_aura(layer, cx, cy, m(R), m(R + 30), pal["glow"], peak=110, layers=18)
    cabochon(layer, cx, cy, m(R), CABO_LO, CABO_HI, ring=pal["gem"], ring_a=70)
    if sid is not None:
        blit_thumb(layer, sid, cx, cy, m(R) * 1.5)
    _disc_tint(layer, cx, cy, m(R), pal["glow"], pal["deep"], peak=55, base=22)
    cabochon_glass(layer, cx, cy, m(R), tint=pal["gem"])
    # tier-gem bezel ring at R+2.
    pygame.draw.circle(layer, (*pal["gem"], 110), (cx, cy), m(R) + m(2), width=m(2))
    clip_mask = pygame.Surface((CARD_W * SS, CARD_H * SS), pygame.SRCALPHA)
    pygame.draw.rect(clip_mask, (255, 255, 255, 255), rect, border_radius=rad)
    layer.blit(clip_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(layer, (0, 0))

    # 5b. CONTACT SHADOW where the dome punches through the tray top line — a
    #     thin dark strip just inside the tray edge sells the glass overrunning
    #     a real recessed lip rather than floating in front of it.
    pygame.draw.line(big, (0, 0, 0, 100), (tray.x, tray.y + m(2)),
                     (tray.right, tray.y + m(2)), max(1, m(1)))

    # 7. NAMEPLATE PLAQUE — an ENGRAVED gold-rimmed pill low in the body: fill
    #    lifted ~18 luma over the tray, a bright top rim + dark bottom inner
    #    shadow to cut it INTO the card. Pulled up so the crown + plaque bracket
    #    the card and it keeps 4px breathing room off the bottom frame.
    name = ITEM_NAMES.get(sid, (sid or "").replace("skin_", "").title())
    plaque_cy = rect.bottom - m(18)
    plaque_w, plaque_h = m(80), m(16)
    plaque_x = cx - plaque_w // 2
    plaque_top = plaque_cy - plaque_h // 2
    plaque_bottom = plaque_cy + plaque_h // 2
    plaque = pygame.Surface((plaque_w, plaque_h), pygame.SRCALPHA)
    pygame.draw.rect(plaque, (52, 55, 100, 215), (0, 0, plaque_w, plaque_h),
                     border_radius=plaque_h // 2)
    pygame.draw.rect(plaque, (*CARD_RING_BRIGHT, 120), (0, 0, plaque_w, plaque_h),
                     width=max(1, m(1)), border_radius=plaque_h // 2)
    big.blit(plaque, (plaque_x, plaque_top))
    # engrave: bright top rim catches the light, dark bottom inner shadow recesses.
    pygame.draw.line(big, (*CARD_RING_BRIGHT, 180), (plaque_x, plaque_top),
                     (plaque_x + plaque_w, plaque_top), max(1, m(1)))
    pygame.draw.line(big, (0, 0, 0, 90), (plaque_x + m(2), plaque_bottom - m(2)),
                     (plaque_x + plaque_w - m(2), plaque_bottom - m(2)), max(1, m(1)))
    plain_text(big, name, font(8.5), (cx, plaque_cy), (236, 230, 208),
               shadow_a=150, weight=m(0.7))

    # 8. PRICE BADGE — a warm METALLIC chip top-RIGHT, a gold/silver counterweight
    #    to the gem crest on the left. Gold-gradient body + hairline rim, the
    #    denomination in the gem hue on the light-gold ground so it reads at 1×.
    price_str = f"{price:,}"
    pf = font(9.0)
    ptw = pf.render(price_str, True, (255, 255, 255)).get_width()
    pw, ph = ptw + m(12), m(15)
    pcx = rect.right - m(8) - pw // 2
    pcy = rect.y + m(12)
    badge = vgrad(pw, ph, m(4), (180, 160, 100), (100, 85, 50), 220)
    pygame.draw.rect(badge, (240, 210, 140, 180), (0, 0, pw, ph),
                     width=max(1, m(1)), border_radius=m(4))
    big.blit(badge, (pcx - pw // 2, pcy - ph // 2))
    plain_text(big, price_str, pf, (pcx, pcy), pal["gem"], shadow_a=0,
               weight=m(0.7))

    # 9. GEM CREST — faceted tier badge, top-LEFT, shifted DOWN (y=m(32)) so it
    #    clears the now-larger dome crest instead of colliding with the glass.
    facet_gem(big, rect.x + m(19), m(_INSET) + m(32), m(GEM_R + 2),
              pal["gem"], pal["deep"])

    # 10. bevel rim + dark keyline LAST so the gold frame stays crisp OVER the
    #     crown overrun — this is what clips the dome to the card silhouette.
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 235),
              w=max(1, m(2.0)))
    return big, (cx, cy)


# ── review sheet ──────────────────────────────────────────────────────────────
# Halo hue is tier-separated: RARE steel-blue, EPIC violet, LEGENDARY warm gold.
VARIANTS = [
    ("RARE",      "skin_lorikeet", {"gem": (108, 188, 252), "glow": (74, 132, 210), "deep": (18, 44, 90)},  600),
    ("EPIC",      "skin_prism",    {"gem": (194, 122, 248), "glow": (150, 60, 232), "deep": (44, 10, 80)},  1400),
    ("LEGENDARY", "skin_kitsune",  {"gem": (255, 202, 104), "glow": (226, 168, 54), "deep": (90, 50, 0)},   3500),
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
htxt = hfont.render("store_card_v3_tl — crown-peek — round 2", True,
                    (236, 232, 214))
sheet.blit(htxt, (MARGIN, MARGIN + (HEADER_H - htxt.get_height()) // 2))

panel_y = MARGIN + HEADER_H
panels = []
for i, (tier, sid, pal, price) in enumerate(VARIANTS):
    px = MARGIN + i * (PANEL_W + GUTTER)
    panel, _ = render_crown_peek(sid, pal, price)
    panels.append(panel)
    sheet.blit(panel, (px, panel_y))
    ftxt = ffont.render(tier, True, (218, 214, 200))
    sheet.blit(ftxt, (px + (PANEL_W - ftxt.get_width()) // 2,
                      panel_y + PANEL_H + (FOOTER_H - ftxt.get_height()) // 2))

# 1x real-scale strip: smoothscale each SS panel down to the live 162×100 card.
strip_label_y = panel_y + PANEL_H + FOOTER_H
ltxt = sfont.render("real scale (1×, 162×100)", True, (200, 204, 220))
sheet.blit(ltxt, (MARGIN, strip_label_y + (STRIP_LABEL_H - ltxt.get_height()) // 2))
strip_y = strip_label_y + STRIP_LABEL_H
for i, panel in enumerate(panels):
    px = MARGIN + i * (PANEL_W + GUTTER)
    left = px + (PANEL_W - CARD_W) // 2
    small = pygame.transform.smoothscale(panel, (CARD_W, CARD_H))
    sheet.blit(small, (left, strip_y))

out = "/home/user/skybit/docs/store_card_v3_tl/crown-peek/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())
