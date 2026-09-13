#!/usr/bin/env python3
"""
coin-mint-well  ·  confirm_purchase_v7  ·  round 2

The recessed intaglio concept: the hero coin is struck INTO a sunken well cut
into the card face. Round 2 addresses the art-director critique:
  - coin shrunk to r=30 so the 14-px wall ring has room to breathe
  - well wall carries a real inverted depth gradient (dark rim → warm inner edge)
  - inner-shadow lip drawn on the exposed wall with a complementary warm catch
  - rim-overhang crescent shadow cast onto the coin face (the definitive intaglio tell)
  - price numeral debossed dark on gold (struck/engraved read)
  - BUY button brightened with 3-stop gradient + top sheen
"""
import os
import math

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import sys
sys.path.insert(0, "/home/user/skybit")

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

import game.store_cards as sc
from game.store_cards import (
    vgrad_stops, plain_text, m, SS, font,
    CABO_LO, CABO_HI, CARD_T, CARD_B, CARD_RING_BRIGHT, CARD_RING_DEEP,
)
from game.hud import _font
from game.draw import lerp_color, NEAR_BLACK, WHITE


# ── mandatory gloss_sweep patch (verbatim from r1) ────────────────────────────
# BLEND_ADD reads RGB directly so sheen lives in the RGB channels, not alpha.
def _gloss_sweep_fixed(surf, rect, radius, peak=120):
    sweep = pygame.Surface(rect.size, pygame.SRCALPHA)
    h = max(1, rect.h)
    for y in range(h):
        v = int(peak * (1 - y / h) ** 2.4)
        if v <= 0:
            continue
        pygame.draw.line(sweep, (v, v, v, 255), (0, y), (rect.w, y))
    sm = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(sm, (255, 255, 255, 255), sm.get_rect(), border_radius=radius)
    sweep.blit(sm, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(sweep, rect.topleft, special_flags=pygame.BLEND_ADD)


sc.gloss_sweep = _gloss_sweep_fixed


# ── tier palette ─────────────────────────────────────────────────────────────
TIERS = [
    ("RARE",      "skin_wizard",    "720",
     {"gem": (108, 188, 252), "glow": (60, 140, 230), "deep": (18, 44, 90)}),
    ("EPIC",      "skin_prism",     "1,400",
     {"gem": (194, 122, 248), "glow": (150, 60, 220), "deep": (44, 10, 80)}),
    ("LEGENDARY", "skin_astronaut", "2,600",
     {"gem": (255, 202, 104), "glow": (220, 160, 40), "deep": (90, 50, 0)}),
]
NAMES = {"RARE": "WIZARD", "EPIC": "PRISM", "LEGENDARY": "ASTRONAUT"}


# ── popup metrics ─────────────────────────────────────────────────────────────
POP_W, POP_H = 260, 442
CX = 130

CARD_L, CARD_T_Y = 10, 127
CARD_R, CARD_B_Y = 250, 436
CARD_RAD = 23

DISC_CY, DISC_R = 135, 53

WELL_CY, WELL_R = 225, 44
# Coin shrunk r=38→r=30: creates a 14-px annular wall the depth gradient can
# actually render on, letting the well exist as a concept rather than a thin
# frame.
COIN_R = 30

Y_LOZ = 298
Y_NAME = 326
Y_BTN = 392


# ── card body ─────────────────────────────────────────────────────────────────
def card_body(big):
    rect = pygame.Rect(m(CARD_L), m(CARD_T_Y), m(CARD_R - CARD_L), m(CARD_B_Y - CARD_T_Y))
    rad = m(CARD_RAD)
    sc.drop_shadow(big, rect, rad, blur=m(8), alpha=165, dy=m(4))
    big.blit(vgrad_stops(rect.w, rect.h, rad, [(0.0, CARD_T), (1.0, CARD_B)],
                         255, gamma=1.15), rect.topleft)
    sc.top_sheen(big, rect, rad, m(30), peak=56)
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    sc.bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 230),
                 w=max(1, m(1.9)))


# ── standard hero disc ────────────────────────────────────────────────────────
def hero_disc(big, sid, pal):
    cx, cy, r = m(CX), m(DISC_CY), m(DISC_R)
    sc._alpha_aura(big, cx, cy, r + m(18), pal["glow"], peak=52, layers=15)
    sc.cabochon(big, cx, cy, r, CABO_LO, CABO_HI, ring=pal["gem"], ring_a=50)
    sc.blit_thumb(big, sid, cx, cy, int(r * 1.5))
    sc.cabochon_glass(big, cx, cy, r, tint=pal["gem"])
    ring_w = max(3, m(3.0))
    pygame.draw.circle(big, pal["gem"], (cx, cy), r + ring_w // 2 + m(1), ring_w)


# ── recessed coin-mint well ───────────────────────────────────────────────────
def coin_well(big, price, pal):
    cx, cy = m(CX), m(WELL_CY)

    # 1) soft ambient glow leaking upward out of the mouth — slightly dimmer
    #    than the disc aura because the well is partially enclosed.
    sc._alpha_aura(big, cx, cy, m(WELL_R + 20), pal["glow"], peak=40, layers=15)

    # 2) Inverted depth gradient on the exposed 14-px wall ring (r=44 down to
    #    r=31): near-black at the outer rim brightening toward the inner edge,
    #    with a warm brown-gold bounce at the very inner edge where reflected
    #    gold from the coin inside would scatter back up the wall.
    #    Draw concentric filled circles largest-first; each smaller circle paints
    #    over the centre leaving only its annular band visible in the final result.
    wall_stops = [
        (44, (4,  5,  16)),   # rim — near-black, opening is in deep shadow
        (40, (10, 12, 30)),   # upper wall — begins to lighten going inward
        (36, (15, 18, 42)),   # mid wall
        (33, (22, 26, 55)),   # inner wall just outside coin — noticeably lighter
        (31, (28, 22, 12)),   # warm brown-gold bounce: reflected coin light
    ]
    for ri, col in wall_stops:
        pygame.draw.circle(big, col, (cx, cy), m(ri))

    # 3) Inner-shadow lip — the intaglio TELL drawn on the now-visible wall.
    #    A recess casts a shadow crescent on its own upper-left inner wall
    #    (108°–192°) exactly where a raised boss would catch direct light.
    #    The complementary warm catch at lower-right (285°–355°) is the
    #    reflected fill light that prevents the wall reading as a flat disc.
    lip = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    r_lip = 40
    lrect = pygame.Rect(cx - m(r_lip), cy - m(r_lip), m(r_lip * 2), m(r_lip * 2))
    pygame.draw.arc(lip, (0, 0, 0, 180), lrect,
                    math.radians(108), math.radians(192), m(8))
    pygame.draw.arc(lip, (80, 60, 20, 100), lrect,
                    math.radians(285), math.radians(355), m(5))
    big.blit(lip, (0, 0))

    # 4) Gold-rimmed opening — the cut rim of the well mouth.
    rim = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.circle(rim, (4, 5, 16, 255),           (cx, cy), m(45), m(3))
    pygame.draw.circle(rim, (*CARD_RING_BRIGHT, 235),   (cx, cy), m(44), m(2))
    pygame.draw.circle(rim, (246, 220, 140, 120),       (cx, cy), m(42), m(1))
    big.blit(rim, (0, 0))

    # 5) Raised coin inside the well — proud of the floor.
    sc.coin_glyph(big, cx, cy, m(COIN_R))

    # 6) Rim overhang shadow cast ONTO the coin face — the definitive intaglio
    #    tell. The well rim physically occludes top-left light, casting a dark
    #    crescent shadow on the coin's upper-left quadrant. Nothing else reads
    #    "the coin is below the surface" as unambiguously as this.
    #    Technique: draw the shadow disc on an SRCALPHA surface, then blit a
    #    punch-mask (opaque everywhere except the lower-right shifted hole) with
    #    BLEND_RGBA_MIN — the zero-alpha hole zeros out the overhang there, leaving
    #    only the upper-left crescent.
    cr = m(COIN_R)
    pad = m(10)
    overhang = pygame.Surface((cr * 2 + pad * 2, cr * 2 + pad * 2), pygame.SRCALPHA)
    oc = cr + pad
    # shadow fills the full coin disc at (0,0,0,120)
    pygame.draw.circle(overhang, (0, 0, 0, 120), (oc, oc), cr)
    # punch_mask is (255,255,255,255) everywhere; the shifted circle is drawn
    # with alpha=0 on an SRCALPHA surface so BLEND_RGBA_MIN zeroes out those pixels.
    shift = m(9)
    punch_mask = pygame.Surface(overhang.get_size(), pygame.SRCALPHA)
    punch_mask.fill((255, 255, 255, 255))
    pygame.draw.circle(punch_mask, (0, 0, 0, 0), (oc + shift, oc + shift), cr)
    overhang.blit(punch_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(overhang, (cx - oc, cy - oc))

    # 7) Top-left specular crescent on the coin's raised upper-left edge —
    #    the raised lip of the coin itself does catch light even inside the well.
    spec = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    srect = pygame.Rect(cx - m(COIN_R), cy - m(COIN_R), m(COIN_R * 2), m(COIN_R * 2))
    pygame.draw.arc(spec, (255, 255, 255, 130), srect,
                    math.radians(120), math.radians(210), m(3))
    big.blit(spec, (0, 0), special_flags=pygame.BLEND_ADD)

    # 8) Debossed price numeral — dark ink on the gold coin face reads as
    #    struck/engraved (intaglio), not floating on top. The dark (48,32,10)
    #    fill against the gold disc is the engraved-numeral convention.
    plain_text(big, price, font(14), (cx, m(231)), (48, 32, 10),
               shadow_a=0, weight=m(1.0), keyline=(20, 12, 4), kw=m(0.9))

    # 9) Tiny hot specular pip at the coin's upper-left — the single
    #    brightest-kiss highlight confirming the coin is a convex disc.
    pip = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.circle(pip, (255, 255, 255, 200),
                       (cx - m(17), cy - m(17)), m(3))
    big.blit(pip, (0, 0), special_flags=pygame.BLEND_ADD)


# ── rarity lozenge ────────────────────────────────────────────────────────────
def rarity_lozenge(big, tier_word, pal):
    cx, cy = m(CX), m(Y_LOZ)
    w_log, h_log = 116, 26
    w, h = m(w_log), m(h_log)
    notch = m(6)
    x0, y0 = cx - w // 2, cy - h // 2
    stops = [(0.0, pal["gem"]), (0.5, pal["glow"]), (1.0, pal["deep"])]
    body = vgrad_stops(w, h, 0, stops, 255, gamma=1.08)
    poly = [(notch, 0), (w - notch, 0), (w, h // 2), (w - notch, h),
            (notch, h), (0, h // 2)]
    pmask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(pmask, (255, 255, 255, 255), poly)
    body.blit(pmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    sh = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(sh, (0, 0, 0, 130), poly)
    big.blit(sh, (x0, y0 + m(2)))
    big.blit(body, (x0, y0))
    abspoly = [(x0 + px, y0 + py) for px, py in poly]
    pygame.draw.polygon(big, (6, 6, 16), abspoly, width=max(1, m(1.6)))
    edge_br = lerp_color(pal["gem"], WHITE, 0.5)
    inpoly = [(x0 + px + (1 if px < w / 2 else -1) * m(1.6),
               y0 + py + (1 if py < h / 2 else -1) * m(1.2)) for px, py in poly]
    pygame.draw.polygon(big, (*edge_br, 150), inpoly, width=max(1, m(1)))
    fsz = 12
    f = font(fsz)
    while sc._glyph_base(tier_word, f, m(1.6)).get_width() > w - notch * 2 - m(8) and fsz > 6:
        fsz -= 0.5
        f = font(fsz)
    plain_text(big, tier_word, f, (cx, cy), (250, 248, 240),
               shadow_a=150, tracking=m(1.6), weight=m(1.0),
               keyline=(10, 10, 22), kw=m(0.8))


# ── buttons ───────────────────────────────────────────────────────────────────
def slab_button(big, cx, label, gradient_stops, label_c, sheen_peak=54):
    """Rectangular slab button — gradient_stops lets BUY carry a 3-stop ramp
    while CANCEL stays a plain 2-stop."""
    w, h = m(106), m(46)
    rad = m(8)
    rect = pygame.Rect(m(cx) - w // 2, m(Y_BTN) - h // 2, w, h)
    body = vgrad_stops(w, h, rad, gradient_stops, 255, gamma=1.1)
    sh = pygame.Surface((w, h + m(3)), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 120), (0, m(3), w, h), border_radius=rad)
    big.blit(sh, (rect.x, rect.y))
    big.blit(body, rect.topleft)
    # top sheen on BUY (sheen_peak=55) gives the gold slab a crisp lit brow;
    # CANCEL keeps peak=54 so it reads flat/neutral by contrast.
    sc.top_sheen(big, rect, rad, m(18), peak=sheen_peak)
    sc.gloss_sweep(big, rect, rad, peak=54)
    sc.bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 230),
                 w=max(1, m(1.6)))
    plain_text(big, label, font(14), rect.center, label_c,
               shadow_a=170, tracking=m(1.2), weight=m(1.0),
               keyline=(6, 6, 16), kw=m(0.9))


# ── popup ─────────────────────────────────────────────────────────────────────
def render_popup(tier_word, sid, price, pal):
    big = pygame.Surface((POP_W * SS, POP_H * SS), pygame.SRCALPHA)
    card_body(big)
    coin_well(big, price, pal)
    rarity_lozenge(big, tier_word, pal)
    plain_text(big, NAMES[tier_word], font(15), (m(CX), m(Y_NAME)),
               (250, 248, 240), shadow_a=160, weight=m(0.9),
               keyline=(6, 6, 16), kw=m(1.0))

    # BUY: brightened 3-stop gold ramp + top sheen so it reads as the primary CTA.
    # CANCEL: unchanged neutral-dark.
    slab_button(big, 70, "BUY",
                [(0.0, (150, 110, 30)), (0.5, (90, 64, 14)), (1.0, (52, 36, 8))],
                (255, 244, 210), sheen_peak=55)
    slab_button(big, 190, "CANCEL",
                [(0.0, (28, 24, 36)), (1.0, (20, 16, 28))],
                (226, 222, 234), sheen_peak=54)

    # disc drawn last so its overhanging aura crowns the card unclipped
    hero_disc(big, sid, pal)
    return pygame.transform.smoothscale(big, (POP_W, POP_H))


# ── three-tier review sheet ───────────────────────────────────────────────────
GAP    = 12
MARGIN = 20
HEAD   = 68
CANVAS_W = MARGIN * 2 + POP_W * 3 + GAP * 2
CANVAS_H = HEAD + POP_H + 40

canvas = pygame.Surface((CANVAS_W, CANVAS_H))
canvas.fill((8, 8, 20))

title = _font(19, True).render(
    "confirm_purchase_v7  ·  coin-mint-well  ·  round 2", True, (232, 226, 208))
canvas.blit(title, (MARGIN, 12))
sub1 = _font(11, True).render(
    "coin r=30, 14-px wall ring with inverted depth gradient · rim overhang shadow on coin face",
    True, (150, 156, 178))
canvas.blit(sub1, (MARGIN, 34))
sub2 = _font(11, True).render(
    "inner-shadow lip + warm catch on wall · debossed price numeral · brightened BUY · 260x442",
    True, (120, 126, 148))
canvas.blit(sub2, (MARGIN, 50))

lab = _font(13, True)
for i, (word, sid, price, pal) in enumerate(TIERS):
    pop = render_popup(word, sid, price, pal)
    px = MARGIN + i * (POP_W + GAP)
    py = HEAD
    canvas.blit(pop, (px, py))
    t = lab.render(word, True, lerp_color(pal["gem"], WHITE, 0.25))
    canvas.blit(t, t.get_rect(midtop=(px + POP_W // 2, py + POP_H + 6)))

OUT = "/home/user/skybit/docs/confirm_purchase_v7/coin-mint-well/round_2.png"
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(canvas, OUT)
print("saved", OUT, canvas.get_size())
