"""nameplate-footer store-card concept — round 1 review render (headless).

A compact hero disc over a full-width tier footer that fuses ribbon and
nameplate into one lit shelf: the footer stripe carries the rarity read (tier
gradient) AND the item name, with a dark-vignetted canonical gold price pill in
its lower zone. No separate ribbon. This is an exploration harness, not shipped
runtime — it writes a review sheet under docs/, never into the game bundle.
"""
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
import sys
sys.path.insert(0, "/home/user/skybit")
import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from game.store_cards import (
    vgrad, vgrad_stops, drop_shadow, bevel_rim, top_sheen, contact_shadow,
    plain_text, price_chip, facet_gem, cabochon, cabochon_glass, blit_thumb,
    soft_glow, font, m, SS, CABO_LO, CABO_HI, CARD_T, CARD_B, CARD_RING_DEEP,
    CARD_RING_BRIGHT, CREAM, GEM_R, CARD_RAD, _name,
)
from game.hud import _font

# ── LOCKED card metrics ───────────────────────────────────────────────────────
CARD_W, CARD_H = 162, 100
INSET = 6
BODY_W = 150                      # visible body: 150x88 at logical (6,6)


def draw_nameplate_card(big, sid, rect, pal, price):
    """Render one nameplate-footer card into `rect` (device px) on `big`."""
    rad = m(CARD_RAD)
    body_x, body_y = rect.x, rect.y
    cx_ss = rect.centerx
    cy_ss = rect.y + m(33)        # hero disc centre, body-relative y=33
    R = 28                        # hero disc radius (logical)

    # 1) soft multi-layer drop shadow (top-left light => offset down)
    drop_shadow(big, rect, rad, blur=m(8), alpha=160, dy=m(4))
    # 2) body gradient
    big.blit(vgrad(rect.w, rect.h, rad, CARD_T, CARD_B, 252, gamma=1.15),
             rect.topleft)
    # 3) glossy top sheen
    top_sheen(big, rect, rad, m(30), peak=62)
    # 4) bottom-right contact AO
    contact_shadow(big, rect, rad, m(9), alpha=120)
    # 5) inner tray (dark border + faint gold keyline)
    tray = rect.inflate(-m(7), -m(7))
    trad = rad - m(4)
    pygame.draw.rect(big, (10, 10, 24, 200), tray.inflate(m(2), m(2)),
                     width=max(1, m(1)), border_radius=trad + m(1))
    pygame.draw.rect(big, (*CARD_RING_BRIGHT, 90), tray, width=max(1, m(1)),
                     border_radius=trad)

    # 6) soft tier aura behind the hero disc — rarity is carried by the footer,
    #    so the glow stays at the standard peak.
    soft_glow(big, cx_ss, cy_ss, m(R + 3), pal["glow"], 30, layers=8)
    # 7) cabochon well -> rim-lit hero skin -> glass dome overlay
    cabochon(big, cx_ss, cy_ss, m(R), CABO_LO, CABO_HI, ring=pal["gem"],
             ring_a=50)
    blit_thumb(big, sid, cx_ss, cy_ss, m(R) * 1.5)
    cabochon_glass(big, cx_ss, cy_ss, m(R), tint=pal["gem"])

    # 8) full-width tier-gradient footer, clipped to the body rounded rect so its
    #    bottom corners follow the card. This IS the rarity + name shelf.
    fw, fh = m(BODY_W), m(22)
    footer = vgrad_stops(fw, fh, m(CARD_RAD - 4),
                         [(0.0, pal["gem"]), (0.5, pal["glow"]),
                          (1.0, pal["deep"])], 255, gamma=1.0)
    body_mask = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    pygame.draw.rect(body_mask, (255, 255, 255, 255), (0, 0, rect.w, rect.h),
                     border_radius=rad)
    corner_clip = body_mask.subsurface((0, m(62), fw, fh)).copy()
    footer.blit(corner_clip, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(footer, (body_x, body_y + m(62)))

    # 9) item name on the footer's upper zone
    plain_text(big, _name(sid), font(13.5), (cx_ss, body_y + m(68)), CREAM,
               shadow_a=160, weight=m(0.8), keyline=(6, 6, 16), kw=m(0.8))
    # 10) dark chip-backing vignette so canonical gold never reads on tier colour
    pygame.draw.rect(big, (4, 4, 14, 160),
                     (cx_ss - m(42), body_y + m(68), m(84), m(22)),
                     border_radius=m(10))
    # 11) canonical GOLD RAMP-A price pill in the footer's lower zone
    price_chip(big, cx_ss, body_y + m(78), f"{price:,}", m(20), affordable=True)

    # 12) crest gem, top-right corner
    facet_gem(big, rect.right - m(19), rect.y + m(19), m(GEM_R + 3),
              pal["gem"], pal["deep"])

    # 13) bevel rim + dark keyline LAST so the card edge stays crisp on top
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 235),
              w=max(1, m(2.0)))


def render_panel(sid, pal, price):
    big = pygame.Surface((CARD_W * SS, CARD_H * SS), pygame.SRCALPHA)
    rect = pygame.Rect(m(INSET), m(INSET),
                       CARD_W * SS - 2 * m(INSET), CARD_H * SS - 2 * m(INSET))
    draw_nameplate_card(big, sid, rect, pal, price)
    return big


VARIANTS = [
    ("RARE", "skin_lorikeet",
     {"gem": (108, 188, 252), "glow": (60, 140, 230), "deep": (18, 44, 90)}, 600),
    ("EPIC", "skin_prism",
     {"gem": (194, 122, 248), "glow": (150, 60, 220), "deep": (44, 10, 80)}, 1400),
    ("LEGENDARY", "skin_kitsune",
     {"gem": (255, 202, 104), "glow": (220, 160, 40), "deep": (90, 50, 0)}, 3500),
]

# ── review sheet ──────────────────────────────────────────────────────────────
MARGIN, GUTTER, HEADER_H = 20, 16, 30
LABEL_H = 24
PW, PH = CARD_W * SS, CARD_H * SS

sheet_w = MARGIN * 2 + PW * 3 + GUTTER * 2
sheet_h = MARGIN + HEADER_H + 10 + PH + 8 + LABEL_H + MARGIN
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((20, 22, 40))

hfont = _font(20, True)
htxt = hfont.render("store_card_v2 — nameplate-footer — round 1", True,
                    (240, 236, 224))
sheet.blit(htxt, (MARGIN, MARGIN + (HEADER_H - htxt.get_height()) // 2))

lfont = _font(16, True)
py = MARGIN + HEADER_H + 10
for i, (label, sid, pal, price) in enumerate(VARIANTS):
    px = MARGIN + i * (PW + GUTTER)
    sheet.blit(render_panel(sid, pal, price), (px, py))
    lt = lfont.render(label, True, (232, 228, 216))
    sheet.blit(lt, (px + (PW - lt.get_width()) // 2, py + PH + 8))

out = "/home/user/skybit/docs/store_card_v2/nameplate-footer/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())
