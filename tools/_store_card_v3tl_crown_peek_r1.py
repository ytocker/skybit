"""crown-peek — store_card_v3_tl concept, round 1 headless render.

A high-domed "crowned" card: the hero disc sits very high (centre at logical
y≈16 within the inset body) so the top third of the glass dome overruns the
inner tray boundary and crests over it — collectible-toy energy from breaking
the frame silhouette. The overrun clips naturally at the card SURFACE edge, so
nothing escapes the gold bevel. The gem crest tucks top-LEFT (shifted down to
clear the dome), the price rides a small faceted tier-badge shield top-RIGHT,
and the item name lands on a frosted gold-rimmed nameplate plaque in the lower
half. Rarity is carried by the gutter halo + in-disc tint veil — no tier-word
banner.

Headless (SDL dummy) → a 3-up RARE/EPIC/LEGENDARY review sheet at SS
(324×200, no downscale) + a real-scale 1x strip (162×100). Not wired into the
live store; writes docs/store_card_v3_tl/crown-peek/round_1.png.
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

# The crowned hero disc: R=26 logical is large enough to feel like a domed
# collectible medallion, yet its top crests just over the inner tray without
# eating so much body that the lower nameplate is crowded. The centre rides
# HIGH (below) so the crown overrun is the whole point of the layout.
R = 26


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


def _gutter_aura(surf, cx, cy, disc_r, glow_r, color, peak=88, layers=18):
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


ITEM_NAMES = {"skin_lorikeet": "Lorikeet", "skin_prism": "Prism",
              "skin_kitsune": "Kitsune"}


def render_crown_peek(sid, pal, price):
    """Draw ONE crown-peek card onto a fresh SS panel (324×200) and return it
    (drawn directly at SS, no smoothscale) plus the disc centre."""
    big = pygame.Surface((CARD_W * SS, CARD_H * SS), pygame.SRCALPHA)
    rect = pygame.Rect(m(_INSET), m(_INSET),
                       CARD_W * SS - 2 * m(_INSET), CARD_H * SS - 2 * m(_INSET))
    rad = m(CARD_RAD)

    # Disc centre rides VERY high in surface coords: cy = m(_INSET)+m(14) puts
    # the disc top at cy - m(R) = m(20) - m(26) = -m(6), so the crown crests
    # over the tray top and clips off cleanly at the card surface edge — the
    # frame is redrawn LAST, keeping the gold bevel over everything.
    cx, cy = rect.centerx, m(_INSET) + m(14)

    # 1. depth: soft multi-layer drop shadow (top-left light → offset down).
    drop_shadow(big, rect, rad, blur=m(8), alpha=160, dy=m(4))
    # 2. body gradient (indigo CARD_T → CARD_B).
    big.blit(vgrad(rect.w, rect.h, rad, CARD_T, CARD_B, 252, gamma=1.15),
             rect.topleft)
    # 3. glossy top sheen.
    top_sheen(big, rect, rad, m(16), peak=45)
    # 4. bottom-right contact AO.
    contact_shadow(big, rect, rad, m(9), alpha=100)

    # 5. subtle inner tray outline — a faint dark border the crown overruns, so
    #    the "peek over the frame" reads against a real boundary.
    tray = rect.inflate(-m(7), -m(7))
    trad = rad - m(4)
    pygame.draw.rect(big, (10, 10, 24, 180), tray.inflate(m(2), m(2)),
                     width=max(1, m(1)), border_radius=trad + m(1))

    # ── crowned hero disc + its gutter halo, on a MASKED layer ──
    # The disc rides so high its dome + halo overrun both the tray AND the outer
    # rect top. We draw the whole stack onto its own transparent layer, then clip
    # that layer to the OUTER rounded rect via BLEND_RGBA_MIN — so the crest
    # crests over the inner tray yet is cut cleanly at the gold bevel and never
    # leaks into the drop-shadow margin above the card. Masking a SEPARATE layer
    # (not `big`) keeps the min-blend off the body, which is already composited.
    layer = pygame.Surface((CARD_W * SS, CARD_H * SS), pygame.SRCALPHA)
    _gutter_aura(layer, cx, cy, m(R), m(R + 26), pal["glow"], peak=88, layers=18)
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

    # 7. NAMEPLATE PLAQUE — a frosted gold-rimmed pill in the lower body, its
    #    name centred. Sits below the disc so the crown + plaque bracket the card.
    name = ITEM_NAMES.get(sid, (sid or "").replace("skin_", "").title())
    plaque_cy = rect.bottom - m(22)
    plaque_w, plaque_h = m(80), m(16)
    plaque = pygame.Surface((plaque_w, plaque_h), pygame.SRCALPHA)
    pygame.draw.rect(plaque, (22, 24, 55, 200), (0, 0, plaque_w, plaque_h),
                     border_radius=plaque_h // 2)
    pygame.draw.rect(plaque, (*CARD_RING_BRIGHT, 120), (0, 0, plaque_w, plaque_h),
                     width=max(1, m(1)), border_radius=plaque_h // 2)
    big.blit(plaque, (cx - plaque_w // 2, plaque_cy - plaque_h // 2))
    plain_text(big, name, font(8.5), (cx, plaque_cy), (236, 230, 208),
               shadow_a=150, weight=m(0.7))

    # 8. PRICE TIER-BADGE — a small faceted shield chip top-RIGHT: a tier-deep
    #    rounded body with a lighter faceted top edge, price in the gem hue.
    price_str = f"{price:,}"
    pf = font(8.5)
    ptw = pf.render(price_str, True, (255, 255, 255)).get_width()
    pw, ph = ptw + m(12), m(15)
    pcx = rect.right - m(8) - pw // 2
    pcy = rect.y + m(12)
    badge = pygame.Surface((pw, ph), pygame.SRCALPHA)
    pygame.draw.rect(badge, (*pal["deep"], 215), (0, 0, pw, ph), border_radius=m(4))
    # lighter faceted rim catches the top-left light like a cut gem.
    pygame.draw.rect(badge, (*[min(255, c + 50) for c in pal["gem"]], 90),
                     (0, 0, pw, ph), width=max(1, m(1)), border_radius=m(4))
    big.blit(badge, (pcx - pw // 2, pcy - ph // 2))
    plain_text(big, price_str, pf, (pcx, pcy), pal["gem"], shadow_a=0,
               weight=m(0.7))

    # 9. GEM CREST — faceted tier badge, top-LEFT, shifted DOWN (y=m(28)) so it
    #    tucks under the crown crest instead of colliding with the dome.
    facet_gem(big, rect.x + m(19), m(_INSET) + m(28), m(GEM_R + 2),
              pal["gem"], pal["deep"])

    # 10. bevel rim + dark keyline LAST so the gold frame stays crisp OVER the
    #     crown overrun — this is what clips the dome to the card silhouette.
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 235),
              w=max(1, m(2.0)))
    return big, (cx, cy)


# ── review sheet ──────────────────────────────────────────────────────────────
VARIANTS = [
    ("RARE",      "skin_lorikeet", {"gem": (108, 188, 252), "glow": (60, 140, 230), "deep": (18, 44, 90)},  600),
    ("EPIC",      "skin_prism",    {"gem": (194, 122, 248), "glow": (140, 40, 230), "deep": (44, 10, 80)},  1400),
    ("LEGENDARY", "skin_kitsune",  {"gem": (255, 202, 104), "glow": (220, 160, 40), "deep": (90, 50, 0)},   3500),
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
htxt = hfont.render("store_card_v3_tl — crown-peek — round 1", True,
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

out = "/home/user/skybit/docs/store_card_v3_tl/crown-peek/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())
