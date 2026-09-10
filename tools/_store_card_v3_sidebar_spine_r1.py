"""sidebar-spine — store_card_v3 concept, round 1 headless render.

Reworked from the original rotated-spine idea into a HORIZONTAL BRIDGE PLATE:
a bold indigo nameplate bar physically crosses from the card body INTO the disc
glass, overlapping the bezel at the disc's lower third. The bar is drawn AFTER
the glass dome so it composites ON TOP of it, and it casts a soft drop shadow
onto the glass below + the body above — the plate reads as a real object passing
in front of the dome, giving the flat card a 3D depth cue. Price is bare gold
digits below the disc; no pill, no chip — ultra-minimal.

Shares the bezel-hero disc build (cabochon → thumb → tier tint → glass → bezel)
and the gutter-only tier halo so the tier read still floods the side gutters.

Headless (SDL dummy) → a 3-up RARE/EPIC/LEGENDARY review sheet at SS (324×200,
no downscale) + a real-scale 1x strip (162×100). Not wired into the live store;
writes docs/store_card_v3/sidebar-spine/round_1.png.
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
    cabochon, cabochon_glass, blit_thumb, facet_gem,
    plain_text, font, m, SS, CABO_LO, CABO_HI, CARD_T, CARD_B,
    CARD_RING_DEEP, CARD_RING_BRIGHT, GEM_R,
)

# LOCKED card constants (from store_cards).
CARD_W, CARD_H = 162, 100
CARD_RAD = 17
_INSET = 6

# The hero medallion: R=35 logical leaves a ~40px indigo gutter left/right — the
# room the tier halo needs AND the span the bridge plate crosses.
R = 35


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


def _alpha_text(surf, txt, font_obj, center, color, alpha, shadow_a=120):
    """plain_text carried at a uniform surface alpha. store_cards.plain_text
    fills type at full opacity; the bare price wants a muted ~170-alpha glow, so
    we stamp onto a scratch layer and scale every pixel's alpha down before
    compositing — keeps the tier hue but pulls the digits back to a whisper."""
    scratch = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    r = plain_text(scratch, txt, font_obj, center, color, shadow_a=shadow_a)
    scratch.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(scratch, (0, 0))
    return r


def render_sidebar_spine(sid, pal, price, name):
    """Draw ONE sidebar-spine (bridge-plate) card onto a fresh SS panel
    (324×200) and return it. Drawn directly at SS (no smoothscale) so the review
    sheet inspects the geometry at author resolution."""
    big = pygame.Surface((CARD_W * SS, CARD_H * SS), pygame.SRCALPHA)
    rect = pygame.Rect(m(_INSET), m(_INSET),
                       CARD_W * SS - 2 * m(_INSET), CARD_H * SS - 2 * m(_INSET))
    rad = m(CARD_RAD)
    body_y = m(_INSET)
    cx, cy = rect.centerx, body_y + m(38)

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
    #    disc.
    tray = rect.inflate(-m(7), -m(7))
    trad = rad - m(4)
    pygame.draw.rect(big, (10, 10, 24, 200), tray.inflate(m(2), m(2)),
                     width=max(1, m(1)), border_radius=trad + m(1))
    pygame.draw.rect(big, (*CARD_RING_BRIGHT, 90), tray, width=max(1, m(1)),
                     border_radius=trad)

    # 6. the domed glass well → hero skin.
    cabochon(big, cx, cy, m(R), CABO_LO, CABO_HI, ring=pal["gem"], ring_a=60)
    blit_thumb(big, sid, cx, cy, m(R) * 1.5)

    # 7. tier tint INSIDE the disc.
    _disc_tint(big, cx, cy, m(R), pal["glow"], pal["deep"])

    # 8. glass dome overlay (crescent sheen + gold bezel) on top of the tint.
    cabochon_glass(big, cx, cy, m(R), tint=pal["gem"])

    # 9. ONE tier-coloured bezel ring at R+2.
    pygame.draw.circle(big, (*pal["gem"], 100), (cx, cy), m(R) + m(2), width=m(2))

    # 10. gutter-only feathered halo — the tier read floods the side gutters.
    _gutter_aura(big, cx, cy, m(R), m(R + 28), pal["glow"], peak=90, layers=18)

    # 11. THE BRIDGE PLATE. A bold horizontal nameplate spanning the full body
    #     width, seated at the disc's lower third (cy + R*0.3). Drawn AFTER the
    #     glass + halo so it passes clearly IN FRONT of the dome — the concept's
    #     whole depth cue. Same indigo material as the body but LIFTED in value
    #     so it reads as a raised physical plate, not a recolour.
    bar_h = m(16)
    bar_cy = cy + m(R * 0.3)
    bar = pygame.Rect(rect.x, bar_cy - bar_h // 2, rect.w, bar_h)
    bar_rad = m(4)
    # cast the plate's shadow onto the glass below + body above BEFORE the plate
    # lands (small blur + downward offset = a plate floating just off the face).
    drop_shadow(big, bar, bar_rad, blur=m(4), alpha=150, dy=m(3))
    big.blit(vgrad(bar.w, bar.h, bar_rad, (38, 40, 82), (22, 24, 54), 255,
                   gamma=1.05), bar.topleft)
    # gold edging + a slim top sheen so the plate feels premium and raised.
    bevel_rim(big, bar, bar_rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 200),
              w=max(1, m(1.5)))
    top_sheen(big, bar, bar_rad, m(3), peak=45)
    # skin NAME on the plate — cream, centred in the plate, left-padded so it
    # sits clear of the crest side. Auto-shrink 10.5 → 8 to fit the width.
    pad_l = m(24)
    avail = bar.right - (bar.x + pad_l) - m(6)
    size = 10.5
    while size > 8:
        if font(size).size(name)[0] <= avail:
            break
        size -= 0.5
    tcx = (bar.x + pad_l + bar.right) // 2
    plain_text(big, name, font(size), (tcx, bar.centery), (246, 240, 216),
               shadow_a=150)

    # 12. price — BARE gold digits below the disc, no pill, no keyline. A muted
    #     tier-glow whisper (~170 alpha) so the price never competes with the
    #     hero or the plate.
    _alpha_text(big, f"{price:,}", font(9), (cx, body_y + m(82)),
                pal["glow"], 170)

    # 13. crest gem — faceted tier badge, top-right corner.
    facet_gem(big, rect.right - m(19), rect.y + m(19), m(GEM_R + 3),
              pal["gem"], pal["deep"])

    # 14. bevel rim + dark keyline LAST so the card frame stays crisp over the
    #     halo + plate that reach the body edge.
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 235),
              w=max(1, m(2.0)))
    return big, (cx, cy)


# ── review sheet ──────────────────────────────────────────────────────────────
VARIANTS = [
    ("RARE", "skin_lorikeet",
     {"gem": (108, 188, 252), "glow": (60, 140, 230), "deep": (18, 44, 90)},
     600, "Lorikeet"),
    ("EPIC", "skin_prism",
     {"gem": (194, 122, 248), "glow": (140, 40, 230), "deep": (44, 10, 80)},
     1400, "Prism"),
    ("LEGENDARY", "skin_kitsune",
     {"gem": (255, 202, 104), "glow": (220, 160, 40), "deep": (90, 50, 0)},
     3500, "Kitsune"),
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
htxt = hfont.render("store_card_v3 — sidebar-spine — round 1", True,
                    (236, 232, 214))
sheet.blit(htxt, (MARGIN, MARGIN + (HEADER_H - htxt.get_height()) // 2))

panel_y = MARGIN + HEADER_H
panels = []
centers = []
for i, (tier, sid, pal, price, name) in enumerate(VARIANTS):
    px = MARGIN + i * (PANEL_W + GUTTER)
    panel, ctr = render_sidebar_spine(sid, pal, price, name)
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

out = "/home/user/skybit/docs/store_card_v3/sidebar-spine/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())

# sanity: plate row must be a lifted indigo (brighter than the CARD_B body), the
# gutter 15px past the disc must be clearly tier-tinted, and the disc centre must
# not blow to pure white.
for (tier, sid, pal, price, name), panel, (cx, cy) in zip(VARIANTS, panels, centers):
    plate_px = panel.get_at((cx, cy + m(R * 0.3)))[:3]
    gx = cx + m(R) + m(15)
    gutter_px = panel.get_at((gx, cy))[:3]
    center_px = panel.get_at((cx, cy))[:3]
    print(f"{tier:9s} plate {plate_px}  gutter+15 {gutter_px}  centre {center_px}")
