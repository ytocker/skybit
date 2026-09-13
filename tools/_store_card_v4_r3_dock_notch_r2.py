"""dock-notch store-card concept — round 2 review render (headless).

Round 2 addresses the full art-director note set from round 1:

1. Coin price: no thousands comma; numerals auto-sized to ≤65% of front-coin
   diameter so the gold face shows around the numeral.  Front coin enlarged
   (r=16 logical) vs. back coin (r=11 logical) so the stamped face reads clearly.
2. Coin cluster moved left (rect.right − m(56)) to keep ≥6 logical-px clearance
   from the gem face (≥10px) / seat (≥6px); top-right corner reserved for gem.
3. Two-coin stack with a bold 8-logical-px per-axis offset so both disc rims
   read as distinct stamped coins rather than an ambiguous blob.
4. Plinth raised (plinth_top = cy − m(14), was cy − m(8)) and gradient lower
   stop lifted so the name-row background lands at ≈(96, 87, 111) — dark text
   on lit stone reads at high contrast.  Disc radius trimmed 34→31 to give the
   taller name band room.
5. Far-wall (upper) notch arc thickened to m(2.5) + a warm inner highlight
   line so both socket walls (dark near / lit far) read at 1× display scale.
6. Lower disc rim suppressed: a dark overdraw ring clipped to the bottom ~30%
   of the disc circumference so the socket-shadow contact reads as a clean
   seating plane instead of a warm glow fighting the near-wall shadow.

What is kept from round 1:
- Near-wall socket shadow (lower half, at notch_r) — the depth-cue anchor.
- Plinth-lit vs. body contrast on disc flanks.
- In-cut occlusion: disc drawn first, plinth SRCALPHA with punched notch on top.
- Broken horizontal gold top-edge lip of the plinth around the notch opening.
- Standard locked shell (drop shadow / body / sheen / contact AO) + gem badge.

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

# ── card metrics ──────────────────────────────────────────────────────────────
CARD_W, CARD_H = 162, 100
INSET = 6
CARD_RAD = 17
R = 31                              # shrunk 34→31 to give the name band more height
CREAM_NUM = (250, 244, 226)
NAME_DARK = (26, 22, 34)            # dark-on-lit (~7:1 on the raised plinth face)

# Plinth gradient: lower stop lifted to ~(92,84,108) so the name-row background
# lands ≈(96,87,111) — enough for dark type to read at high contrast.
PLINTH_STOPS = [
    (0.00, (130, 118, 132)),
    (0.42, (110, 100, 122)),
    (1.00, (92,  84, 108)),
]


def _coin_stack(big, cx, cy, price):
    """2-coin stamped-medallion price cluster: a larger front coin carrying the
    numeral and a smaller receding back coin offset 8 logical px up-left so both
    rims read as distinct discs at 1x.  No thousands comma so shorter text fits
    more comfortably; numerals auto-sized to ≤65% of the front-coin diameter so
    the gold face is visible around them."""
    front_r = m(16)     # enlarged stamped face — clearly larger than back coin
    back_r  = m(11)     # smaller back coin — depth cue, clearly behind
    off     = m(8)      # bold 8-logical-px per-axis offset (≈11 logical diagonal)

    # back coin (partly occluded by front — crescent visible upper-left)
    coin_glyph(big, cx - off, cy - off, back_r)
    pygame.draw.circle(big, (*CARD_RING_BRIGHT, 195), (cx - off, cy - off),
                       back_r, max(1, m(0.8)))

    # front coin — larger, last drawn = clearly on top
    coin_glyph(big, cx, cy, front_r)
    pygame.draw.circle(big, (*CARD_RING_BRIGHT, 220), (cx, cy),
                       front_r, max(1, m(1.0)))

    # price numeral across the front coin: no comma, auto-shrink to ≤65% of
    # front-coin diameter so visible gold face wraps around the numeral
    label = str(price)
    front_diam = front_r * 2
    sz = 9.5
    f = font(sz)
    while sz > 3.0:
        if f is not None and f.size(label)[0] + 6 <= int(front_diam * 0.65):
            break
        sz -= 0.5
        f = font(sz)
    if f is None:
        f = font(5.0)
    plain_text(big, label, f, (cx, cy), CREAM_NUM, shadow_a=0,
               weight=m(0.9), keyline=(18, 12, 8), kw=m(0.9))


def draw_dock_notch_card(big, sid, rect, pal, price):
    """Render one dock-notch card into `rect` (device px) on `big`."""
    rad      = m(CARD_RAD)
    cx       = rect.left + m(44)
    cy       = rect.centery - m(4)
    notch_r  = m(R) + m(2)          # 2-px socket gap around the disc rim
    plinth_top = cy - m(14)         # raised 6 logical px vs r1: taller name band
    plinth_h   = rect.bottom - plinth_top
    # half-width of the notch opening at the plinth top edge — splits the gold lip
    open_hw = int(math.sqrt(max(0, notch_r ** 2 - (cy - plinth_top) ** 2)))

    # ── LOCKED shell ─────────────────────────────────────────────────────────
    drop_shadow(big, rect, rad, blur=m(8), alpha=160, dy=m(4))
    big.blit(vgrad(rect.w, rect.h, rad, CARD_T, CARD_B, 252, gamma=1.15),
             rect.topleft)
    top_sheen(big, rect, rad, m(30), peak=62)
    contact_shadow(big, rect, rad, m(9), alpha=120)

    # ── HERO DISC (drawn FIRST so the plinth punch reveals its lower arc) ────
    soft_glow(big, cx, cy, m(R + 4), pal["glow"], 30, layers=8)
    cabochon(big, cx, cy, m(R), CABO_LO, CABO_HI)
    blit_thumb(big, sid, cx, cy, int(m(R) * 1.5))
    cabochon_glass(big, cx, cy, m(R), tint=pal["gem"])

    # ── SUPPRESS lower disc rim — overdraw the gold bezel ring in the bottom
    #    ~30% of disc circumference so the socket-shadow contact reads as a
    #    clean dark seating plane instead of a warm lip fighting the near-wall
    disc_r_dev = m(R)
    suppress = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.circle(suppress, (6, 8, 20, 215), (cx, cy), disc_r_dev,
                       max(3, m(2.5)))          # wide enough to cover all three bezel rings
    supp_mask = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    supp_mask.fill((0, 0, 0, 0))
    # bottom 30% of circumference starts at y > cy + disc_r × cos(54°) ≈ cy + r×0.59
    bottom_thresh = cy + int(disc_r_dev * 0.59)
    pygame.draw.rect(supp_mask, (255, 255, 255, 255),
                     (0, bottom_thresh, big.get_width(), big.get_height()))
    suppress.blit(supp_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(suppress, (0, 0))

    # ── SOCKET SHADOW: dark ring in the disc↔wall gap, LOWER half only.
    #    Near (bottom) notch wall reads as the shaded contact under the disc.
    ring = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.circle(ring, (0, 0, 0, 165), (cx, cy), notch_r, m(3))
    low = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    low.fill((255, 255, 255, 255))
    pygame.draw.rect(low, (0, 0, 0, 0), (0, 0, big.get_width(), cy))
    ring.blit(low, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(ring, (0, 0))

    # ── PLINTH: raised lit stone band, corners clipped to the card body, with
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

    # ── DEPTH SELLERS ────────────────────────────────────────────────────────
    # Far (upper) notch wall: thickened gold arc + warm inner highlight both
    # clipped to the upper half — two lit lines make the socket-wall read at 1×
    lip = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.circle(lip, (*CARD_RING_BRIGHT, 235), (cx, cy), notch_r,
                       max(2, m(2.5)))
    pygame.draw.circle(lip, (255, 248, 210, 130), (cx, cy),
                       notch_r - max(2, m(2)), max(1, m(1.2)))
    up = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    up.fill((255, 255, 255, 255))
    pygame.draw.rect(up, (0, 0, 0, 0), (0, cy, big.get_width(),
                                        big.get_height() - cy))
    lip.blit(up, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(lip, (0, 0))

    # Gold lip along the plinth straight top edge, broken around the notch opening
    lipw = max(1, m(1.4))
    pygame.draw.line(big, CARD_RING_BRIGHT, (rect.left, plinth_top),
                     (cx - open_hw, plinth_top), lipw)
    pygame.draw.line(big, CARD_RING_BRIGHT, (cx + open_hw, plinth_top),
                     (rect.right, plinth_top), lipw)

    # ── NAME: full-width across the lit plinth face, dark-on-lit ────────────
    name   = store_catalog.name(sid)
    name_cy = (cy + notch_r + rect.bottom) // 2
    f = font(11.5)
    while f.size(name)[0] > rect.w - m(18) and f.get_height() > m(9):
        f = font(f.get_height() / SS - 0.5)
    plain_text(big, name, f, (rect.centerx, name_cy), NAME_DARK, shadow_a=0,
               weight=m(0.9), keyline=(214, 206, 220), kw=m(0.8))

    # ── COIN STACK: right-biased but with ≥6 logical-px clearance from gem ──
    # Pulling left to rect.right − m(56) puts the front coin right edge 6 logical
    # px clear of the gem badge seat so the top-right corner belongs to the gem.
    _coin_stack(big, rect.right - m(56), plinth_top - m(4), price)

    # ── GEM badge, top-right corner (reserved, coin stack does not encroach) ─
    facet_gem(big, rect.right - m(19), rect.y + m(19), m(GEM_R + 3),
              pal["gem"], pal["deep"])

    # ── Crisp dark keyline + gold bevel rim LAST so the card edge stays sharp ─
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 235),
              w=max(1, m(2.0)))


def render_panel(sid):
    big  = pygame.Surface((CARD_W * SS, CARD_H * SS), pygame.SRCALPHA)
    rect = pygame.Rect(m(INSET), m(INSET),
                       CARD_W * SS - 2 * m(INSET), CARD_H * SS - 2 * m(INSET))
    pal   = RARITY[_rarity(sid)]
    price = store_catalog.cost(sid)
    draw_dock_notch_card(big, sid, rect, pal, price)
    return big


# ── review strip ──────────────────────────────────────────────────────────────
VARIANTS = [
    ("RARE",      "skin_tophat"),
    ("EPIC",      "skin_prism"),
    ("LEGENDARY", "skin_kitsune"),
]

MARGIN, GAP, HEADER_H, LABEL_H = 10, 8, 26, 22
PW, PH = CARD_W * SS, CARD_H * SS

sheet_w = MARGIN * 2 + PW * 3 + GAP * 2
sheet_h = MARGIN + HEADER_H + PH + LABEL_H + MARGIN
sheet   = pygame.Surface((sheet_w, sheet_h))
sheet.fill((8, 8, 20))

hfont = _font(18, True)
htxt  = hfont.render("store_card_v4_r3 — dock-notch — round 2", True,
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

out = "/home/user/skybit/docs/store_card_v4_r3/dock-notch/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())
