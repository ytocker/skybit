"""portrait-plate — store_card_v3_tl concept, round 1 headless render.

A calm, premium "portrait framed under glass" card. A large cabochon hero sits
in the upper 60% of the body; a gem crest anchors the top-LEFT corner while the
price rides a dark-glass pill top-RIGHT; the item name lands on a slim frosted
footer strip along the bottom. No tier-word banner — rarity is carried entirely
by the gutter halo + the in-disc tint veil. The dome is pushed to be genuinely
juicy: an extra upper-left crescent caustic is painted INSIDE the glass on top of
the standard cabochon sheen, with a tight bright-gold bevel rim.

Headless (SDL dummy) → a 3-up RARE/EPIC/LEGENDARY review sheet at SS
(324×200, no downscale) + a real-scale 1x strip (162×100). Not wired into the
live store; writes docs/store_card_v3_tl/portrait-plate/round_1.png.
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

# The portrait disc: R=24 logical leaves a generous indigo gutter for the tier
# halo AND clears the bottom footer name-strip. Centred high (upper 60%) so the
# frosted footer never crowds the glass.
R = 24


def _disc_tint(surf, cx, cy, r, color, deep, peak=55, base=22):
    """A tier colour veil INSIDE the disc, clipped to the glass. It warms the
    cool CABO_LO→CABO_HI dome away from the indigo body, and — carrying a
    meaningful centre alpha — pulls a bright skin highlight toward the tier hue
    so it stops blowing out. The gentle exponent lets the hue carry inward
    instead of collapsing at the centre; the veil stays rim-biased (peak > base)
    so the portrait's face reads through while the surround takes the tier hue."""
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


def _gutter_aura(surf, cx, cy, disc_r, glow_r, color, peak=85, layers=18):
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


def render_card(sid, pal, price, name):
    """Draw ONE portrait-plate card onto a fresh SS panel (324×200) and return
    it (drawn directly at SS, no smoothscale) plus the disc centre."""
    big = pygame.Surface((CARD_W * SS, CARD_H * SS), pygame.SRCALPHA)
    rect = pygame.Rect(m(_INSET), m(_INSET),
                       CARD_W * SS - 2 * m(_INSET), CARD_H * SS - 2 * m(_INSET))
    rad = m(CARD_RAD)
    cx, cy = rect.centerx, rect.y + m(36)

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
    #    portrait even at "minimum chrome".
    tray = rect.inflate(-m(7), -m(7))
    trad = rad - m(4)
    pygame.draw.rect(big, (10, 10, 24, 200), tray.inflate(m(2), m(2)),
                     width=max(1, m(1)), border_radius=trad + m(1))
    pygame.draw.rect(big, (*CARD_RING_BRIGHT, 90), tray, width=max(1, m(1)),
                     border_radius=trad)

    # ── hero portrait disc ──
    # 6. the domed glass well.
    cabochon(big, cx, cy, m(R), CABO_LO, CABO_HI, ring=pal["gem"], ring_a=60)
    # 7. the skin portrait, framed under glass.
    if sid is not None:
        blit_thumb(big, sid, cx, cy, m(R) * 1.5)
    # 8. tier tint INSIDE the disc — warms the glass per tier.
    _disc_tint(big, cx, cy, m(R), pal["glow"], pal["deep"], peak=55, base=22)
    # 9. glass dome overlay (standard crescent sheen + gold bezel).
    cabochon_glass(big, cx, cy, m(R), tint=pal["gem"])

    # 10. EXTRA JUICE — a second, narrow crescent caustic INSIDE the glass, swept
    #     across the upper-left, on TOP of the standard sheen. Painted on a
    #     temp SRCALPHA surface then masked to the disc so it can't spill past
    #     the rim. This is the "genuinely juicy" upper-left highlight.
    d = m(R) * 2
    cres = pygame.Surface((d, d), pygame.SRCALPHA)
    # a tall, off-centre ellipse biased to the upper-left quadrant.
    ell = pygame.Rect(0, 0, int(m(R) * 0.9), int(m(R) * 1.5))
    ell.center = (int(m(R) * 0.62), int(m(R) * 0.58))
    pygame.draw.ellipse(cres, (255, 255, 255, 45), ell)
    # subtract a shifted copy of itself to leave only a crescent sliver.
    sub = pygame.Surface((d, d), pygame.SRCALPHA)
    ell2 = ell.copy()
    ell2.move_ip(m(3), m(2))
    pygame.draw.ellipse(sub, (255, 255, 255, 255), ell2)
    cres.blit(sub, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
    # mask the whole crescent to the disc interior.
    cmask = pygame.Surface((d, d), pygame.SRCALPHA)
    pygame.draw.circle(cmask, (255, 255, 255, 255), (m(R), m(R)), m(R) - m(1))
    cres.blit(cmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(cres, (cx - m(R), cy - m(R)))

    # 11. faint darker pool at the lower rim for depth (weight sits low in the
    #     glass), masked to the disc so it hugs the 6-o'clock bevel.
    pool = pygame.Surface((d, d), pygame.SRCALPHA)
    pell = pygame.Rect(0, 0, int(m(R) * 1.5), int(m(R) * 0.85))
    pell.center = (m(R), int(m(R) * 1.35))
    pygame.draw.ellipse(pool, (*pal["deep"], 70), pell)
    pmask = pygame.Surface((d, d), pygame.SRCALPHA)
    pygame.draw.circle(pmask, (255, 255, 255, 255), (m(R), m(R)), m(R) - m(1))
    pool.blit(pmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(pool, (cx - m(R), cy - m(R)))

    # 12. tight bright-gold bevel rim right on the glass edge.
    pygame.draw.circle(big, (*CARD_RING_BRIGHT, 180), (cx, cy),
                       m(R) + m(1), width=m(1))

    # 13. tier read: a gutter-only feathered halo that floods the side gutters.
    _gutter_aura(big, cx, cy, m(R), m(R + 26), pal["glow"], peak=85, layers=18)

    # 14. FOOTER NAME STRIP — a slim frosted plate across the bottom of the body
    #     interior: brightened body colour, a thin gold keyline at its top edge,
    #     cream small-caps name centred.
    strip_rect = pygame.Rect(rect.x, rect.bottom - m(22), rect.w, m(22))
    strip = pygame.Surface((strip_rect.w, strip_rect.h), pygame.SRCALPHA)
    strip.fill((40, 42, 85, 210))
    pygame.draw.line(strip, (*CARD_RING_BRIGHT, 160),
                     (0, 0), (strip_rect.w, 0), max(1, m(1)))
    big.blit(strip, strip_rect.topleft)
    plain_text(big, name.upper(), font(9.0), strip_rect.center,
               (236, 230, 208), shadow_a=160, tracking=m(1.0), weight=m(0.7))

    # 15. PRICE PILL — small dark-glass rounded pill, top-RIGHT.
    ph, pw_min = m(14), m(40)
    price_str = f"{price:,}"
    pf = font(8.0)
    ptw = pf.render(price_str, True, (255, 255, 255)).get_width()
    pw = max(pw_min, ptw + m(12))
    pcx = rect.right - m(6) - pw // 2
    pcy = rect.y + m(10)
    pill = pygame.Surface((pw, ph), pygame.SRCALPHA)
    pygame.draw.rect(pill, (*pal["deep"], 210), (0, 0, pw, ph),
                     border_radius=ph // 2)
    pygame.draw.rect(pill, (*pal["gem"], 70), (0, 0, pw, ph),
                     width=max(1, m(1)), border_radius=ph // 2)
    big.blit(pill, (pcx - pw // 2, pcy - ph // 2))
    plain_text(big, price_str, pf, (pcx, pcy), pal["gem"],
               shadow_a=0, weight=m(0.7))

    # 16. GEM CREST — faceted tier badge, top-LEFT corner.
    facet_gem(big, rect.x + m(19), rect.y + m(19), m(GEM_R + 2),
              pal["gem"], pal["deep"])

    # 17. bevel rim + dark keyline LAST so the card frame stays crisp over the
    #     halo + footer that bleed to the body edge.
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
htxt = hfont.render("store_card_v3_tl — portrait-plate — round 1", True,
                    (236, 232, 214))
sheet.blit(htxt, (MARGIN, MARGIN + (HEADER_H - htxt.get_height()) // 2))

panel_y = MARGIN + HEADER_H
panels = []
for i, (tier, sid, pal, price, name) in enumerate(VARIANTS):
    px = MARGIN + i * (PANEL_W + GUTTER)
    panel, _ = render_card(sid, pal, price, name)
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

out = "/home/user/skybit/docs/store_card_v3_tl/portrait-plate/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())
