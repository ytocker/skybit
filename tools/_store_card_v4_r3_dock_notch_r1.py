"""dock-notch store-card concept — round 1 review render (headless).

A money-native variant of the CONSTELLATION card built around an in-cut
occlusion: a solid full-width PLINTH at the foot of the card with a
semicircular NOTCH carved out of its top edge, concentric with the hero disc.
The disc is drawn FIRST; the plinth is then composited with the notch punched
to alpha 0, so the disc's lower arc shows THROUGH the gap and the plinth
material appears to wrap the disc like a socket. A dark inner-shadow arc on the
near (lower) notch wall and a thin warm lit lip on the far (upper) wall sell the
depth. The item name sits full-width across the lit plinth face below the notch;
the price is a right-biased overlapping coin-stack cluster floating above the
band — a money-native price read distinct from chip/escutcheon/etch/hang-tag.

This is an exploration harness, not shipped runtime — it writes a review sheet
under docs/, never into the game bundle.
"""
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
import sys
import math
sys.path.insert(0, "/home/user/skybit")
import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from game.hud import _font
from game import store_catalog
from game.store_cards import (
    cabochon, cabochon_glass, blit_thumb, facet_gem,
    vgrad, vgrad_stops, drop_shadow, bevel_rim, top_sheen, contact_shadow,
    plain_text, font, m, SS, soft_glow, coin_glyph,
    CARD_T, CARD_B, CARD_RING_BRIGHT, CARD_RING_DEEP,
    CABO_LO, CABO_HI, GEM_R, RARITY, CREAM, _rarity,
)

# ── LOCKED card metrics ───────────────────────────────────────────────────────
CARD_W, CARD_H = 162, 100
INSET = 6
CARD_RAD = 17
R = 34                             # hero disc radius (logical) — the notch fits it
CREAM_NUM = (250, 244, 226)
NAME_DARK = (26, 22, 34)           # dark-on-lit plinth name (~7:1 on the lit face)

# The lit plinth face — a warm/cool stone gradient kept clearly LIGHTER than the
# card body (CARD_T/CARD_B navy) so dark type reads on it at high contrast.
PLINTH_STOPS = [
    (0.00, (120, 108, 120)),
    (0.48, (92, 82, 106)),
    (1.00, (56, 52, 80)),
]


def _coin_stack(big, cx, cy, price):
    """Money-native price: 2-3 overlapping in-game gold coins staggered into a
    small stack, each ringed with the card's canonical gold so it ties to the
    frame, with the price numerals stamped across the FRONT coin in cream. The
    cluster floats above the plinth band, right-biased into the empty space the
    left-leaning disc leaves open."""
    coin_r = m(12)
    # back-to-front, each nudged down-right so the front coin reads on top and
    # the stack climbs up-left behind it.
    offs = [(-m(6), -m(7)), (-m(3), -m(3)), (0, 0)]
    for dx, dy in offs:
        coin_glyph(big, cx + dx, cy + dy, coin_r)
        pygame.draw.circle(big, (*CARD_RING_BRIGHT, 210), (cx + dx, cy + dy),
                           coin_r, max(1, m(0.9)))
    # price numerals across the front coin — cream with a tight dark keyline so
    # they stay legible over the yellow coin face.
    f = font(9.5)
    plain_text(big, f"{price:,}", f, (cx, cy), CREAM_NUM, shadow_a=0,
               weight=m(0.9), keyline=(18, 12, 8), kw=m(0.9))


def draw_dock_notch_card(big, sid, rect, pal, price):
    """Render one dock-notch card into `rect` (device px) on `big`."""
    rad = m(CARD_RAD)
    cx = rect.left + m(44)          # slightly more centered so the notch aligns
    cy = rect.centery - m(4)
    notch_r = m(R) + m(2)           # a 2px socket gap so the shadow ring has room
    plinth_top = cy - m(8)          # top edge ABOVE disc centre => a far wall too
    plinth_h = rect.bottom - plinth_top
    # half-width of the notch opening where the plinth's straight top edge meets
    # the arc — used to break the gold lip line around the cut.
    open_hw = int(math.sqrt(max(0, notch_r ** 2 - (cy - plinth_top) ** 2)))

    # ── LOCKED shell: shadow, body, sheen, contact AO ───────────────────────
    drop_shadow(big, rect, rad, blur=m(8), alpha=160, dy=m(4))
    big.blit(vgrad(rect.w, rect.h, rad, CARD_T, CARD_B, 252, gamma=1.15),
             rect.topleft)
    top_sheen(big, rect, rad, m(30), peak=62)
    contact_shadow(big, rect, rad, m(9), alpha=120)

    # ── HERO DISC (drawn FIRST so the notch reveals its lower arc) ───────────
    soft_glow(big, cx, cy, m(R + 4), pal["glow"], 30, layers=8)
    cabochon(big, cx, cy, m(R), CABO_LO, CABO_HI, ring=pal["gem"], ring_a=50)
    blit_thumb(big, sid, cx, cy, int(m(R) * 1.5))
    cabochon_glass(big, cx, cy, m(R), tint=pal["gem"])

    # ── SOCKET SHADOW: a dark ring in the disc<->wall gap, LOWER half only, so
    #    the near (bottom) notch wall reads as the shaded contact under the disc.
    #    Drawn before the plinth; the plinth punch keeps only its inner portion.
    ring = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.circle(ring, (0, 0, 0, 165), (cx, cy), notch_r, m(3))
    low = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    low.fill((255, 255, 255, 255))
    pygame.draw.rect(low, (0, 0, 0, 0), (0, 0, big.get_width(), cy))
    ring.blit(low, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(ring, (0, 0))

    # ── PLINTH: lit stone band, bottom corners clipped to the card body, with
    #    the notch semicircle punched to alpha 0 so the disc shows through.
    plinth = vgrad_stops(rect.w, plinth_h, 0, PLINTH_STOPS, 255, gamma=1.05)
    body_mask = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(body_mask, (255, 255, 255, 255), (0, 0, rect.w, rect.h),
                     border_radius=rad)
    corner_clip = body_mask.subsurface(
        (0, plinth_top - rect.y, rect.w, plinth_h)).copy()
    plinth.blit(corner_clip, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    punch = pygame.Surface((rect.w, plinth_h), pygame.SRCALPHA)
    punch.fill((255, 255, 255, 255))
    pygame.draw.circle(punch, (0, 0, 0, 0),
                       (cx - rect.x, cy - plinth_top), notch_r)
    plinth.blit(punch, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(plinth, (rect.x, plinth_top))

    # ── DEPTH SELLERS ───────────────────────────────────────────────────────
    # far (upper) notch wall catches the top-left light: a thin warm lit lip.
    lip = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.circle(lip, (*CARD_RING_BRIGHT, 205), (cx, cy), notch_r,
                       max(1, m(1.4)))
    up = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    up.fill((255, 255, 255, 255))
    pygame.draw.rect(up, (0, 0, 0, 0), (0, cy, big.get_width(),
                                        big.get_height() - cy))
    lip.blit(up, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(lip, (0, 0))
    # gold lip along the plinth's straight top edge, broken around the notch.
    lipw = max(1, m(1.4))
    pygame.draw.line(big, CARD_RING_BRIGHT, (rect.left, plinth_top),
                     (cx - open_hw, plinth_top), lipw)
    pygame.draw.line(big, CARD_RING_BRIGHT, (cx + open_hw, plinth_top),
                     (rect.right, plinth_top), lipw)

    # ── NAME: full-width across the lit plinth face, BELOW the notch, dark-on
    #    -lit for legibility.
    name = store_catalog.name(sid)
    name_cy = (cy + notch_r + rect.bottom) // 2
    f = font(11.5)
    while f.size(name)[0] > rect.w - m(18) and f.get_height() > m(9):
        f = font(f.get_height() / SS - 0.5)
    plain_text(big, name, f, (rect.centerx, name_cy), NAME_DARK, shadow_a=0,
               weight=m(0.9), keyline=(214, 206, 220), kw=m(0.8))

    # ── PRICE coin-stack, floating above the band, right-biased.
    _coin_stack(big, rect.right - m(40), plinth_top - m(3), price)

    # ── GEM badge, top-right corner.
    facet_gem(big, rect.right - m(19), rect.y + m(19), m(GEM_R + 3),
              pal["gem"], pal["deep"])

    # ── crisp dark keyline + gold bevel rim LAST so the card edge stays sharp.
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 235),
              w=max(1, m(2.0)))


def render_panel(sid):
    big = pygame.Surface((CARD_W * SS, CARD_H * SS), pygame.SRCALPHA)
    rect = pygame.Rect(m(INSET), m(INSET),
                       CARD_W * SS - 2 * m(INSET), CARD_H * SS - 2 * m(INSET))
    pal = RARITY[_rarity(sid)]
    price = store_catalog.cost(sid)
    draw_dock_notch_card(big, sid, rect, pal, price)
    return big


# ── review strip ──────────────────────────────────────────────────────────────
VARIANTS = [
    ("RARE", "skin_tophat"),
    ("EPIC", "skin_prism"),
    ("LEGENDARY", "skin_kitsune"),
]

MARGIN, GAP, HEADER_H, LABEL_H = 10, 8, 26, 22
PW, PH = CARD_W * SS, CARD_H * SS

sheet_w = MARGIN * 2 + PW * 3 + GAP * 2
sheet_h = MARGIN + HEADER_H + PH + LABEL_H + MARGIN
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((8, 8, 20))

hfont = _font(18, True)
htxt = hfont.render("store_card_v4_r3 — dock-notch — round 1", True,
                    (240, 236, 224))
sheet.blit(htxt, (MARGIN, MARGIN + (HEADER_H - htxt.get_height()) // 2))

lfont = _font(15, True)
py = MARGIN + HEADER_H
for i, (label, sid) in enumerate(VARIANTS):
    px = MARGIN + i * (PW + GAP)
    sheet.blit(render_panel(sid), (px, py))
    lt = lfont.render(label, True, (222, 218, 208))
    sheet.blit(lt, (px + (PW - lt.get_width()) // 2,
                    py + PH + (LABEL_H - lt.get_height()) // 2))

out = "/home/user/skybit/docs/store_card_v4_r3/dock-notch/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())
