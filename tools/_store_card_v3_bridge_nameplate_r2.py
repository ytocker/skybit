"""bridge-nameplate — store_card_v3 concept, round 2 headless render.

A jeweler's nameplate plaque straddles the disc's bottom rim (6 o'clock): half
over the glass exterior, half on the card body — an engraved trophy plate
riveted onto a display medallion. Below it sits a dark-on-dark indigo price
chip whose ONLY silhouette cue is a 1px tier-coloured keyline, so the number
reads as etched into the card rather than stamped on a bright pill.

Round-2 fixes (art-director):
  - The tier bezel ring is masked so it never crosses the plaque: rendered on
    its own surface, the plaque silhouette (inflated m(2)) is punched out with
    BLEND_RGBA_MIN, and two gold rivet tabs are dropped where the ring meets
    the plate shoulders — the mount now reads as clamping the plate.
  - m(4) breathing gap opened between plaque and price chip.
  - Whole disc + plaque group nudged up m(3) so the chip lifts off the panel
    floor and top/bottom margins even out.
  - Price chip's unresolvable inner CARD_RING_DEEP rim dropped; the single tier
    keyline carries the silhouette.
  - Disc-centre tint richened (base 32, softer alpha falloff) to keep the hero
    off pure white without blowing the LEGENDARY centre.

Headless (SDL dummy) → a 3-up RARE/EPIC/LEGENDARY review sheet at SS
(324×200, no downscale) + a real-scale 1x strip (162×100). Not wired into the
live store; writes docs/store_card_v3/bridge-nameplate/round_2.png.
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
    plain_text, cabochon, cabochon_glass, blit_thumb, facet_gem,
    font, m, SS, CABO_LO, CABO_HI, CARD_T, CARD_B,
    CARD_RING_DEEP, CARD_RING_BRIGHT, GEM_R,
)

# LOCKED card constants (from store_cards).
CARD_W, CARD_H = 162, 100
CARD_RAD = 17
_INSET = 6

# The hero medallion: R=35 logical leaves a ~40px indigo gutter left/right for
# the tier halo, same as bezel-hero. CY lowered by m(3) vs r1 (38→35) so the
# straddling plaque + price chip both lift off the body bottom — the chip clears
# the panel floor and the top/bottom margins read even.
R = 35
CY = 35


def _disc_tint(surf, cx, cy, r, color, deep, peak=52, base=32):
    """A tier colour veil INSIDE the disc, clipped to the glass. It warms the
    cool CABO_LO→CABO_HI dome away from the indigo body, and — carrying a modest
    centre alpha — pulls any near-white skin highlight toward the tier hue so the
    hero never reads pure (255,255,255). A richer centre alpha (base 32) with a
    softer falloff keeps the hero off white without over-darkening; still
    rim-biased so it reads as a coloured dome, not a flat cast."""
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


def _fit_name_font(name, max_w):
    """Nameplate type wants to sit large in the plate, but the longest skin
    names must not touch the bevel. Try 10.5 down to 8; take the first that
    fits the engraved field."""
    for size in (10.5, 9.5, 8.5, 8):
        f = font(size)
        if f.size(name)[0] <= max_w:
            return f
    return font(8)


def _bridge_plaque(surf, cx, cy, name):
    """The engraved nameplate straddling the disc's 6-o'clock rim: a deep-indigo
    rounded plate lifted a touch above the card body, dropped-shadowed onto BOTH
    the glass and the body, gold-mounted, top-sheened, and engraved with the
    skin name in cream. Its width (90 > the 70px disc) makes it read as a plate
    bridging FROM the medallion ONTO the card, not a label inside the disc.
    Returns (prect, prad) so the bezel ring can be masked to its silhouette."""
    plaque_w, plaque_h = m(90), m(18)
    prad = m(5)
    prect = pygame.Rect(cx - plaque_w // 2, cy + m(R) - plaque_h // 2,
                        plaque_w, plaque_h)

    # shadow first (onto glass + body), then the plate on top → it floats proud.
    drop_shadow(surf, prect, prad, blur=m(5), alpha=140, dy=m(2))
    surf.blit(vgrad(prect.w, prect.h, prad, (36, 38, 80), (20, 22, 52), 255),
              prect.topleft)
    bevel_rim(surf, prect, prad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 220),
              w=max(1, m(1.4)))
    top_sheen(surf, prect, prad, m(8), peak=50)

    nfont = _fit_name_font(name, plaque_w - m(14))
    plain_text(surf, name, nfont, prect.center, (246, 240, 216),
               shadow_a=130, keyline=(4, 4, 14), kw=m(1))
    return prect, prad


def _clipped_bezel_ring(surf, cx, cy, prect, prad, pal):
    """The disc's tier bezel ring at R+2 — but masked so it NEVER paints across
    the plaque (in r1 it drew a coloured line straight through the name). The
    ring is rendered on its own surface, the plaque silhouette (inflated m(2)) is
    punched out with BLEND_RGBA_MIN, and the masked ring is composited back.
    Two gold rivet tabs land where the ring enters the plate boundary so the
    mount reads as clamping the plate down onto the medallion."""
    ring = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.circle(ring, (*pal["gem"], 100), (cx, cy), m(R) + m(2), width=m(2))

    # Punch the plaque out of the ring: MIN with an opaque field that carries
    # alpha-0 inside the (inflated) plate silhouette erases the ring there.
    punch = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    punch.fill((255, 255, 255, 255))
    hole = prect.inflate(m(2), m(2))
    pygame.draw.rect(punch, (0, 0, 0, 0), hole, border_radius=prad + m(2))
    ring.blit(punch, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(ring, (0, 0))

    # Rivet tabs at the two shoulders where the ring circle crosses the plate's
    # top edge — the visible mount clamps that hold the plate onto the disc.
    rr = m(R) + m(2)
    dy = prect.top - cy
    if abs(dy) < rr:
        dx = (rr * rr - dy * dy) ** 0.5
        for sx in (cx - dx, cx + dx):
            tab = pygame.Rect(0, 0, m(5), m(5))
            tab.center = (int(round(sx)), prect.top)
            pygame.draw.rect(surf, (*CARD_RING_BRIGHT, 200), tab,
                             border_radius=m(2))


def _price_chip(surf, cx, cy, price, pal):
    """Dark-on-dark indigo price chip. The body is the SAME tone as the card
    bottom (CARD_B), so the number would vanish — the read comes entirely from
    a crisp 1px OUTER keyline in the tier glow colour that traces the chip
    silhouette. Etched, not stamped. The inner gold rim from r1 is gone (it did
    not resolve at 1× and only warmed the chip); the single tier keyline carries
    the silhouette on its own. Returns the chip rect for pixel sampling."""
    pfont = font(8.5)
    ptxt = f"{price:,}"
    tw = pfont.size(ptxt)[0]
    chip_w = tw + m(18)
    chip_h = m(14)
    chip_rad = chip_h // 2
    chip = pygame.Rect(0, 0, chip_w, chip_h)
    chip.center = (cx, cy)

    pygame.draw.rect(surf, (*CARD_B, 230), chip, border_radius=chip_rad)
    # THE silhouette cue: a 1px tier-coloured keyline sitting just OUTSIDE the
    # body, so the otherwise-invisible dark chip registers as an object.
    outer = chip.inflate(m(2), m(2))
    pygame.draw.rect(surf, (*pal["glow"], 180), outer, width=max(1, m(1)),
                     border_radius=chip_rad + m(1))
    plain_text(surf, ptxt, pfont, chip.center, (180, 184, 210),
               shadow_a=110, keyline=None)
    return chip


def render_bridge_nameplate(sid, pal, price, name):
    """Draw ONE bridge-nameplate card onto a fresh SS panel (324×200) and return
    (surface, disc_center, geom). Drawn directly at SS (no smoothscale) so the
    review sheet inspects the geometry at author resolution."""
    big = pygame.Surface((CARD_W * SS, CARD_H * SS), pygame.SRCALPHA)
    rect = pygame.Rect(m(_INSET), m(_INSET),
                       CARD_W * SS - 2 * m(_INSET), CARD_H * SS - 2 * m(_INSET))
    rad = m(CARD_RAD)
    cx, cy = rect.centerx, m(CY)

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
    #    disc + plaque.
    tray = rect.inflate(-m(7), -m(7))
    trad = rad - m(4)
    pygame.draw.rect(big, (10, 10, 24, 200), tray.inflate(m(2), m(2)),
                     width=max(1, m(1)), border_radius=trad + m(1))
    pygame.draw.rect(big, (*CARD_RING_BRIGHT, 90), tray, width=max(1, m(1)),
                     border_radius=trad)

    # 6. domed glass well → hero skin.
    cabochon(big, cx, cy, m(R), CABO_LO, CABO_HI, ring=pal["gem"], ring_a=60)
    blit_thumb(big, sid, cx, cy, m(R) * 1.5)

    # 7. glass dome overlay (crescent sheen + gold bezel).
    cabochon_glass(big, cx, cy, m(R), tint=pal["gem"])

    # 8. tier tint INSIDE the disc — warms the glass per tier.
    _disc_tint(big, cx, cy, m(R), pal["glow"], pal["deep"])

    # 9. THE concept: the engraved nameplate bridging the disc rim onto the body.
    #    After the glass (sits on the sheen), before the bezel ring (the disc's
    #    gold mount then reads as clamping the plate down).
    prect, prad = _bridge_plaque(big, cx, cy, name)

    # 10. tier bezel ring at R+2 — masked off the plaque, with rivet tabs.
    _clipped_bezel_ring(big, cx, cy, prect, prad, pal)

    # 11. gutter-only feathered halo flooding the ~40px side gutters.
    _gutter_aura(big, cx, cy, m(R), m(R + 28), pal["glow"], peak=90, layers=18)

    # 12. dark-on-dark price chip below the plaque, tier-keyline silhouette.
    #     m(20) below the disc rim (vs m(16) in r1) opens an m(4) gap under the
    #     plaque so its bottom keyline and the chip top no longer touch.
    chip = _price_chip(big, cx, cy + m(R) + m(20), price, pal)

    # 13. crest gem — faceted tier badge, top-right corner.
    facet_gem(big, rect.right - m(19), rect.y + m(19), m(GEM_R + 3),
              pal["gem"], pal["deep"])

    # 14. bevel rim + dark keyline LAST so the card frame stays crisp over the
    #     halo that bleeds to the body edge.
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 235),
              w=max(1, m(2.0)))
    return big, (cx, cy), {"rect": rect, "prect": prect, "chip": chip}


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
htxt = hfont.render("store_card_v3 — bridge-nameplate — round 2", True,
                    (236, 232, 214))
sheet.blit(htxt, (MARGIN, MARGIN + (HEADER_H - htxt.get_height()) // 2))

panel_y = MARGIN + HEADER_H
panels = []


def _px(panel, x, y):
    """Clamped pixel read as an (r,g,b,a) tuple for the sample printout."""
    x = max(0, min(panel.get_width() - 1, int(round(x))))
    y = max(0, min(panel.get_height() - 1, int(round(y))))
    return tuple(panel.get_at((x, y)))


print("pixel samples (device px, RGBA) — SS panels 324×200")
for i, (tier, sid, pal, price, name) in enumerate(VARIANTS):
    px = MARGIN + i * (PANEL_W + GUTTER)
    panel, (cx, cy), geo = render_bridge_nameplate(sid, pal, price, name)
    panels.append(panel)
    sheet.blit(panel, (px, panel_y))
    ftxt = ffont.render(tier, True, (218, 214, 200))
    sheet.blit(ftxt, (px + (PANEL_W - ftxt.get_width()) // 2,
                      panel_y + PANEL_H + (FOOTER_H - ftxt.get_height()) // 2))

    rect, prect, chip = geo["rect"], geo["prect"], geo["chip"]
    gutter_x = cx - m(R) - 15                         # 15px into the left gutter aura
    plaque_off_x = cx + m(30)                        # plaque body, clear of text
    print(f"  {tier:<10} "
          f"gutter+15={_px(panel, gutter_x, cy)}  "
          f"disc_centre={_px(panel, cx, cy)}  "
          f"plaque_offtext={_px(panel, plaque_off_x, prect.centery)}  "
          f"chip_text={_px(panel, chip.centerx, chip.centery)}")

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

out = "/home/user/skybit/docs/store_card_v3/bridge-nameplate/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())
