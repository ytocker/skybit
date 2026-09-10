"""product-line-bar — store_card_v3 concept, round 2 headless render.

Round-2 revision of the retail-SKU read. The medallion hero now rides with more
AIR (R=32, disc centre at rect.y+34 so the disc top clears the inner-tray frame
and the disc bottom only just overhangs the shelf bar), and the full-width tier
FOOTER BAR is INSET to the gold inner tray (tray.x / tray.w, seated flush to the
tray bottom with the tray's own bottom-corner radius) so it lives inside the
frame like the disc does.

The bar's tier ramp is INVERTED versus r1: deep at the TOP, glow through the
mid, and gem only as a 1-2px bright lip at the very base. That seats the NAME +
PRICE glyphs on the darkest, most consistent slice of the bar. Text ink is
TIER-ADAPTIVE: the actual bar background under the glyphs is sampled and, when
its luminance clears ~90 (warm bars like LEGENDARY), the glyphs flip to dark ink
so cream-on-gold never smears; cool/dark bars keep cream. The gutter halo is
pulled back (glow_r=R+16, peak=65) now that the bar carries the rarity read, and
the disc-centre tint is strengthened (base 30, exp 1.3) to tame near-white skins.

Copied scaffold from _store_card_v3_product_line_bar_r1 (_disc_tint,
_gutter_aura, VARIANTS list, review-sheet stitch); only the numbers the
art-director called out changed.

Headless (SDL dummy) -> a 3-up RARE/EPIC/LEGENDARY review sheet at SS (324x200,
no downscale) + a real-scale 1x strip (162x100). Not wired into the live store;
writes docs/store_card_v3/product-line-bar/round_2.png.
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
    vgrad, vgrad_stops, drop_shadow, bevel_rim, top_sheen, contact_shadow,
    cabochon, cabochon_glass, blit_thumb, facet_gem, plain_text,
    font, m, SS, CABO_LO, CABO_HI, CARD_T, CARD_B,
    CARD_RING_DEEP, CARD_RING_BRIGHT, GEM_R,
)

# LOCKED card constants (from store_cards).
CARD_W, CARD_H = 162, 100
CARD_RAD = 17
_INSET = 6

# Hero medallion radius: dropped to R=32 to give the hero more breathing room in
# the gutter and above/below, so the disc no longer crowds the tray frame or the
# shelf bar.
R = 32
# Disc centre measured from the body top (rect.y + 34): the disc top now clears
# the inner-tray frame by a couple logical px and the disc bottom only just kisses
# the top lip of the shelf bar instead of burying into it.
CY = 34

# Cream vs dark ink for the shelf label. Cream is the default over cool/dark
# bars; dark ink lands on warm/bright bars (LEGENDARY) where cream would smear.
INK_CREAM = (246, 240, 216)
INK_DARK = (40, 26, 6)
INK_LUM_THRESHOLD = 90        # background luminance above which cream fails


def _luma(c):
    """Rec601 perceived luminance — the store's existing convention for
    background-vs-ink decisions."""
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def _disc_tint(surf, cx, cy, r, color, deep, peak=52, base=30):
    """A tier colour veil INSIDE the disc, clipped to the glass. It warms the
    cool CABO_LO->CABO_HI dome away from the indigo body, and — carrying a
    STRONGER centre alpha (base 30) with a gentler falloff (exp 1.3) — pulls any
    near-white skin highlight harder toward the tier hue so the hero never reads
    pure (255,255,255). Rim-biased (deeper toward the edge) reads as a coloured
    dome, not a flat cast."""
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


def _gutter_aura(surf, cx, cy, disc_r, glow_r, color, peak=65, layers=18):
    """A feathered tier halo that lives ONLY beyond the disc rim (radius >
    disc_r), so it floods the side gutters with tier colour without touching —
    or blowing out — the hero inside the glass. Normal alpha-carry blits (NOT
    additive) so the colour survives compositing and reads as a tint, not a hot
    white bloom. Brightest at the rim, feathering out into the gutter. Pulled
    back (tighter radius, softer peak) now that the shelf bar carries the read."""
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


def _top_edge_shadow(surf, bar, depth, alpha):
    """A soft AO band hugging the bar's TOP edge only, so the bar reads as
    resting UNDER the disc that overhangs it. contact_shadow hugs bottom+right,
    which is the wrong edge here — this feathers a dark band downward from the
    bar's top lip instead."""
    band = pygame.Surface((bar.w, depth), pygame.SRCALPHA)
    for y in range(depth):
        a = int(alpha * (1 - y / depth) ** 1.4)
        pygame.draw.line(band, (0, 0, 0, a), (0, y), (bar.w - 1, y))
    surf.blit(band, (bar.x, bar.y))


def _fit_font(txt, max_w, hi=10.5, lo=8.0):
    """Auto-shrink the label font from hi->lo (0.5 steps) until it fits max_w, so
    long skin names never spill past the bar's left cell."""
    size = hi
    while size > lo:
        f = font(size)
        if f.size(txt)[0] <= max_w:
            return f
        size -= 0.5
    return font(lo)


def render_card(sid, pal, price, name):
    """Draw ONE product-line-bar card onto a fresh SS panel (324x200) and return
    it plus a probe dict for pixel sampling. Drawn directly at SS (no
    smoothscale) so the review sheet inspects the geometry at author
    resolution."""
    big = pygame.Surface((CARD_W * SS, CARD_H * SS), pygame.SRCALPHA)
    rect = pygame.Rect(m(_INSET), m(_INSET),
                       CARD_W * SS - 2 * m(_INSET), CARD_H * SS - 2 * m(_INSET))
    rad = m(CARD_RAD)
    cx, cy = rect.centerx, rect.y + m(CY)

    # 1. depth: soft multi-layer drop shadow (top-left light -> offset down).
    drop_shadow(big, rect, rad, blur=m(8), alpha=160, dy=m(4))
    # 2. body gradient (indigo CARD_T -> CARD_B).
    big.blit(vgrad(rect.w, rect.h, rad, CARD_T, CARD_B, 252, gamma=1.15),
             rect.topleft)
    # 3. glossy top sheen.
    top_sheen(big, rect, rad, m(30), peak=62)
    # 4. bottom-right contact AO.
    contact_shadow(big, rect, rad, m(9), alpha=120)
    # 5. inner tray dark border + faint gold lane framing the disc.
    tray = rect.inflate(-m(7), -m(7))
    trad = rad - m(4)
    pygame.draw.rect(big, (10, 10, 24, 200), tray.inflate(m(2), m(2)),
                     width=max(1, m(1)), border_radius=trad + m(1))
    pygame.draw.rect(big, (*CARD_RING_BRIGHT, 90), tray, width=max(1, m(1)),
                     border_radius=trad)

    # 11. FOOTER BAR — inset to the gold inner tray (tray.x / tray.w), seated
    #     flush to the tray bottom with the tray's own bottom-corner radius, so
    #     it lives inside the frame like the disc. Drawn BEFORE the disc so the
    #     disc's slight overhang + top-edge AO read as the disc resting on it.
    bar = pygame.Rect(tray.x, 0, tray.w, m(20))
    bar.bottom = tray.bottom
    #     INVERTED 3-stop tier ramp: deep at the TOP (the flattest, darkest,
    #     most consistent ground for the glyphs), glow through the mid, gem only
    #     as a bright lip at the very base. gamma>1 biases the whole bar toward
    #     the deep end, flattening value behind the text further.
    fill = vgrad_stops(bar.w, bar.h, 0,
                       [(0.0, pal["deep"]), (0.80, pal["glow"]), (1.0, pal["gem"])],
                       255, gamma=1.5)
    #     round ONLY the bottom corners (to the tray radius); the top stays flat
    #     under the overhanging disc.
    cmask = pygame.Surface((bar.w, bar.h), pygame.SRCALPHA)
    pygame.draw.rect(cmask, (255, 255, 255, 255), (0, 0, bar.w, bar.h),
                     border_bottom_left_radius=trad, border_bottom_right_radius=trad)
    fill.blit(cmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(fill, bar.topleft)

    # 6. domed glass well -> hero skin (no under-disc additive glow).
    cabochon(big, cx, cy, m(R), CABO_LO, CABO_HI, ring=pal["gem"], ring_a=60)
    blit_thumb(big, sid, cx, cy, m(R) * 1.5)

    # 7. tier tint INSIDE the disc — warms the glass, tames near-white skins.
    _disc_tint(big, cx, cy, m(R), pal["glow"], pal["deep"])

    # 8. glass dome overlay (crescent sheen + gold bezel) on top of the tint.
    cabochon_glass(big, cx, cy, m(R), tint=pal["gem"])

    # 9. ONE tier-coloured bezel ring at R+2.
    pygame.draw.circle(big, (*pal["gem"], 100), (cx, cy), m(R) + m(2), width=m(2))

    # 10. gutter halo — pulled back (R+16, softer peak) since the shelf bar now
    #     carries the rarity read and the halo shouldn't compete with it. Clipped
    #     to above the bar so its lower arcs stay in the side gutters and never
    #     streak across the shelf the disc overhangs.
    prev_clip = big.get_clip()
    big.set_clip(pygame.Rect(0, 0, big.get_width(), bar.top))
    _gutter_aura(big, cx, cy, m(R), m(R + 16), pal["glow"], peak=65, layers=18)
    big.set_clip(prev_clip)

    #     top-edge AO so the bar reads as resting below the overhanging disc.
    _top_edge_shadow(big, bar, depth=m(4), alpha=100)
    #     1px bevel to define the bar edges against body + gutter halo.
    bevel_rim(big, bar, 0, CARD_RING_DEEP, CARD_RING_BRIGHT, w=max(1, m(1)))

    # 12/13. TIER-ADAPTIVE INK — sample the ACTUAL bar background under the
    #     glyphs (bar centre) and flip to dark ink when it clears the luminance
    #     threshold, so warm bars read dark type and cool bars keep cream. Gating
    #     on the rendered pixel (not a fixed per-tier choice) keeps it
    #     future-proof for any new palette.
    bg = big.get_at((bar.centerx, bar.centery))[:3]
    ink = INK_DARK if _luma(bg) > INK_LUM_THRESHOLD else INK_CREAM
    pad = m(8)
    price_txt = f"$ {price:,}"
    pfont = font(10.5)
    price_w = pfont.size(price_txt)[0]
    name_max = bar.w - price_w - pad * 3
    nfont = _fit_font(name, name_max)
    nsurf = nfont.render(name, True, ink)
    # NAME (left cell) — left-aligned, m(8) pad, vertically centred.
    plain_text(big, name, nfont,
               (bar.x + pad + nsurf.get_width() // 2, bar.centery),
               ink, shadow_a=170, keyline=(20, 14, 4), kw=m(0.8))
    # PRICE (right cell) — right-aligned, m(8) pad.
    prect = plain_text(big, price_txt, pfont,
                       (bar.right - pad - price_w // 2, bar.centery),
                       ink, shadow_a=170, keyline=(20, 14, 4), kw=m(0.8))

    # 14. crest gem — faceted tier badge, top-right corner.
    facet_gem(big, rect.right - m(19), rect.y + m(19), m(GEM_R + 3),
              pal["gem"], pal["deep"])

    # 15. bevel rim + dark keyline LAST so the card frame stays crisp.
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 235),
              w=max(1, m(2.0)))
    probe = {
        "cx": cx, "cy": cy, "bar": bar, "prect": prect,
        "bg": bg, "ink": ink, "lum": _luma(bg),
    }
    return big, probe


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

PANEL_W, PANEL_H = CARD_W * SS, CARD_H * SS   # 324 x 200 (SS panels, no downscale)
MARGIN = 20
GUTTER = 16
HEADER_H = 30
FOOTER_H = 24
STRIP_LABEL_H = 20
STRIP_H = CARD_H                              # real-scale 1x cards (162x100)

sheet_w = MARGIN * 2 + PANEL_W * 3 + GUTTER * 2
sheet_h = (MARGIN + HEADER_H + PANEL_H + FOOTER_H + STRIP_LABEL_H + STRIP_H
           + MARGIN)
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((16, 17, 30))

hfont = _font(22, True)
ffont = _font(20, True)
sfont = _font(16, True)
htxt = hfont.render("store_card_v3 — product-line-bar — round 2", True,
                    (236, 232, 214))
sheet.blit(htxt, (MARGIN, MARGIN + (HEADER_H - htxt.get_height()) // 2))

panel_y = MARGIN + HEADER_H
panels = []
probes = []
for i, (tier, sid, pal, price, name) in enumerate(VARIANTS):
    px = MARGIN + i * (PANEL_W + GUTTER)
    panel, probe = render_card(sid, pal, price, name)
    panels.append(panel)
    probes.append(probe)
    sheet.blit(panel, (px, panel_y))
    ftxt = ffont.render(tier, True, (218, 214, 200))
    sheet.blit(ftxt, (px + (PANEL_W - ftxt.get_width()) // 2,
                      panel_y + PANEL_H + (FOOTER_H - ftxt.get_height()) // 2))

# 1x real-scale strip: smoothscale each SS panel down to the live 162x100 card
# so the sheet also shows how the card reads at true size.
strip_label_y = panel_y + PANEL_H + FOOTER_H
ltxt = sfont.render("real scale (1×, 162×100):", True, (200, 204, 220))
sheet.blit(ltxt, (MARGIN, strip_label_y + (STRIP_LABEL_H - ltxt.get_height()) // 2))
strip_y = strip_label_y + STRIP_LABEL_H
for i, panel in enumerate(panels):
    px = MARGIN + i * (PANEL_W + GUTTER)
    small = pygame.transform.smoothscale(panel, (CARD_W, CARD_H))
    sheet.blit(small, (px + (PANEL_W - CARD_W) // 2, strip_y))

out = "/home/user/skybit/docs/store_card_v3/product-line-bar/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())


def _find_ink_pixel(panel, prect, ink):
    """Scan the price glyph rect for the pixel nearest the chosen ink — a real
    rendered text pixel to verify the adaptive-ink decision landed."""
    best, bestd = None, 1e9
    for y in range(prect.top, prect.bottom):
        for x in range(prect.left, prect.right):
            c = panel.get_at((x, y))[:3]
            d = sum((a - b) ** 2 for a, b in zip(c, ink))
            if d < bestd:
                bestd, best = d, c
    return best


# Per-tier pixel samples the art-director asked for.
for (tier, sid, pal, price, name), panel, pr in zip(VARIANTS, panels, probes):
    cx, cy, bar = pr["cx"], pr["cy"], pr["bar"]
    gutter_px = panel.get_at((cx + m(R) + m(15), cy))[:3]     # rim + 15px logical
    disc_px = panel.get_at((cx, cy))[:3]
    bar_hue = panel.get_at((bar.centerx, bar.centery))[:3]
    text_px = _find_ink_pixel(panel, pr["prect"], pr["ink"])
    ink_name = "dark" if pr["ink"] == INK_DARK else "cream"
    print(f"{tier:9s} gutter+15 {gutter_px}  disc-centre {disc_px}  "
          f"bar-hue {bar_hue}  bg-lum {pr['lum']:5.1f}->{ink_name:5s}  "
          f"text-px {text_px}")
