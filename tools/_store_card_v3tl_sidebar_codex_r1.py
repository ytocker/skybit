"""sidebar-codex — store_card_v3_tl concept, round 1 headless render.

A "codex spine" card: the hero skin sits in the left ~60% display-case half; a
narrow vertical sidebar rail along the right ~40% carries the item name rotated
90° (bottom-to-top), single-line small-caps with tight tracking. The split reads
like the spine of a boxed collectible or museum specimen card. Gem crest sits
top-LEFT; the price is bare gem-coloured digits top-RIGHT (no pill body). A 1px
vertical rule divides the two halves, and the tier halo concentrates in the left
gutter behind the hero. No tier-word banner.

Shares the bezel-hero disc build (cabochon → thumb → tier tint → glass → bezel)
and the gutter-only tier halo with the other v3 concepts; _disc_tint and
_gutter_aura are copied verbatim from arc-veil-pill r2.

Headless (SDL dummy) → a 3-up RARE/EPIC/LEGENDARY review sheet at SS (324×200,
no downscale) + a real-scale 1x strip (162×100). Not wired into the live store;
writes docs/store_card_v3_tl/sidebar-codex/round_1.png.
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

# The hero medallion: a smaller R=21 leaves the left half a compact display case
# while freeing the right ~40% for the spine rail — the split geometry is the
# concept, so the disc is left-biased (cx at 42% of the body width) rather than
# centred.
R = 21

# The rail begins at 60% of the body width; everything right of the dividing rule
# is the codex spine that carries the rotated name.
SPLIT_X = 0.60


def _disc_tint(surf, cx, cy, r, color, deep, peak=92, base=78):
    """A tier colour veil INSIDE the disc, clipped to the glass. It warms the
    cool CABO_LO→CABO_HI dome away from the indigo body, and — carrying a
    meaningful centre alpha — pulls the LEGENDARY hero's near-white specular
    toward the tier hue so it stops blowing out. The gentler exponent (1.3, down
    from r1's 1.6) lets the hue carry further inward instead of collapsing to
    nothing at the centre; the veil stays rim-biased because peak > base.

    base sits well above the ~34 first estimate because cabochon_glass paints its
    crescent sheen over the SAME centre AFTER this tint, re-lighting it — so the
    centre pixel (whose alpha equals base) needs ~78 before LEGENDARY's specular
    drops under the 245/channel ceiling, while RARE/EPIC (mid-tone, not near
    white) only shed a few points and stay legible."""
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


def render_sidebar_codex(sid, pal, price, name, tier):
    """Draw ONE sidebar-codex card onto a fresh SS panel (324×200) and return it.
    Drawn directly at SS (no smoothscale) so the review sheet inspects the
    geometry at author resolution."""
    big = pygame.Surface((CARD_W * SS, CARD_H * SS), pygame.SRCALPHA)
    rect = pygame.Rect(m(_INSET), m(_INSET),
                       CARD_W * SS - 2 * m(_INSET), CARD_H * SS - 2 * m(_INSET))
    rad = m(CARD_RAD)

    # Disc left-biased at 42% of the body width so the display case owns the left
    # half and the spine rail owns the right — the split is the concept.
    cx = rect.x + int(rect.w * 0.42)
    cy = rect.y + m(38)

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
    #    display case.
    tray = rect.inflate(-m(7), -m(7))
    trad = rad - m(4)
    pygame.draw.rect(big, (10, 10, 24, 200), tray.inflate(m(2), m(2)),
                     width=max(1, m(1)), border_radius=trad + m(1))
    pygame.draw.rect(big, (*CARD_RING_BRIGHT, 90), tray, width=max(1, m(1)),
                     border_radius=trad)

    # 6. SIDEBAR RAIL — a subtle dark fill over the region right of the split
    #    line, so the spine reads as a distinct panel that carries the rotated
    #    name. Drawn under the divider rule + name.
    split_px = rect.x + int(rect.w * SPLIT_X)
    rail_rect = pygame.Rect(split_px + m(1), rect.y + m(2),
                            rect.right - (split_px + m(1)) - m(2),
                            rect.h - m(4))
    rail_surf = pygame.Surface((rail_rect.w, rail_rect.h), pygame.SRCALPHA)
    rail_surf.fill((20, 22, 50, 130))
    big.blit(rail_surf, rail_rect.topleft)

    # 7. the domed glass well → hero skin (compact, left-biased display case).
    cabochon(big, cx, cy, m(R), CABO_LO, CABO_HI, ring=pal["gem"], ring_a=60)
    blit_thumb(big, sid, cx, cy, m(R) * 1.5)
    # 8. tier tint INSIDE the disc — warms the glass + pulls any near-white
    #    highlight toward the tier hue.
    _disc_tint(big, cx, cy, m(R), pal["glow"], pal["deep"], peak=55, base=22)
    # 9. glass dome overlay (crescent sheen + gold bezel) on top of the tint.
    cabochon_glass(big, cx, cy, m(R), tint=pal["gem"])
    # 10. ONE tier-coloured bezel ring at R+2.
    pygame.draw.circle(big, (*pal["gem"], 100), (cx, cy), m(R) + m(2), width=m(2))

    # 11. gutter halo — concentrated in the LEFT gutter behind the hero so the
    #     tier read lives in the display-case half, not the spine.
    _gutter_aura(big, cx, cy, m(R), m(R + 28), pal["glow"], peak=90, layers=18)

    # 12. VERTICAL DIVIDING RULE between the display case and the spine rail.
    pygame.draw.line(big, (*CARD_RING_BRIGHT, 80),
                     (split_px, rect.y + m(4)),
                     (split_px, rect.bottom - m(4)), max(1, m(0.7)))

    # 13. ROTATED NAME — rendered at SS, then rotated 90° CCW so it reads
    #     bottom-to-top up the spine rail. A dark keyline shadow is composited
    #     under the cream glyphs so the name lifts off the rail fill.
    nf = font(9.5)
    name_surf = nf.render(name, True, (236, 230, 208))
    shadow = nf.render(name, True, (4, 5, 16))
    name_with_shadow = pygame.Surface(
        (name_surf.get_width() + m(2), name_surf.get_height() + m(2)),
        pygame.SRCALPHA)
    name_with_shadow.blit(shadow, (m(1), m(1)))
    name_with_shadow.blit(name_surf, (0, 0))
    rotated = pygame.transform.rotate(name_with_shadow, 90)
    # Centre horizontally in the rail; the bottom of the rotated block sits m(6)
    # above the card bottom so the name starts at the bottom of the spine.
    rx = rail_rect.centerx - rotated.get_width() // 2
    ry = rect.bottom - m(6) - rotated.get_height()
    big.blit(rotated, (rx, ry))

    # 14. crest gem — faceted tier badge, top-LEFT corner of the display case.
    facet_gem(big, rect.x + m(19), rect.y + m(19), m(GEM_R + 2),
              pal["gem"], pal["deep"])

    # 15. PRICE — bare gem-coloured digits top-RIGHT, no pill body. A dark
    #     keyline + soft shadow lift the digits off the rail.
    pf = font(9.5)
    price_str = f"{price:,}"
    plain_text(big, price_str, pf, (rect.right - m(18), rect.y + m(10)),
               pal["gem"], shadow_a=200, weight=m(0.8), keyline=(4, 5, 16),
               kw=m(1.2))

    # 16. bevel rim + dark keyline LAST so the card frame stays crisp over the
    #     halo + rail that reach the body edge.
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
htxt = hfont.render("store_card_v3_tl — sidebar-codex — round 1", True,
                    (236, 232, 214))
sheet.blit(htxt, (MARGIN, MARGIN + (HEADER_H - htxt.get_height()) // 2))

panel_y = MARGIN + HEADER_H
panels = []
centers = []
for i, (tier, sid, pal, price, name) in enumerate(VARIANTS):
    px = MARGIN + i * (PANEL_W + GUTTER)
    panel, ctr = render_sidebar_codex(sid, pal, price, name, tier)
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

out = "/home/user/skybit/docs/store_card_v3_tl/sidebar-codex/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())

# sanity: the rail fill must be a distinct dark panel (measured OFF the rotated
# name); the left gutter 15px past the disc must be clearly tier-tinted; the disc
# centre must not blow to white (LEGENDARY ≤ 240 on every channel).
for (tier, sid, pal, price, name), panel, (cx, cy) in zip(VARIANTS, panels, centers):
    split_px = m(_INSET) + int((PANEL_W - 2 * m(_INSET)) * SPLIT_X)
    rail_x = split_px + m(6)
    rail_px = panel.get_at((rail_x, cy))[:3]
    gx = cx - m(R) - m(15)                          # LEFT gutter probe
    gutter_px = panel.get_at((max(0, gx), cy))[:3]
    center_px = panel.get_at((cx, cy))[:3]
    print(f"{tier:9s} rail(off-text) {rail_px}  L-gutter+15 {gutter_px}  "
          f"centre {center_px}  maxch {max(center_px)}")
    if tier == "LEGENDARY" and max(center_px) > 240:
        print(f"  !! FLAG: LEGENDARY disc centre {center_px} exceeds 240 — "
              f"still blowing toward white")
