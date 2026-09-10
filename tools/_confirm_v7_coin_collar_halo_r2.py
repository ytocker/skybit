#!/usr/bin/env python3
"""
coin-collar-halo  ·  confirm_purchase_v7  ·  round 2

Couture jewellery as UI: a jewelled collar clasps a large centrepiece coin
below the hero disc. The collar is rebuilt as a continuous band — every stud
has a dedicated dark bezel seat so none dissolves into the card or the coin's
bevel; stud sizes taper from the bottom apex (largest) to the opening ends
(smallest) so the arc reads as one sweeping piece. The coin (r=44) dominates
the lower zone; deliberate 6px dark gap between disc body and coin top shows
pendant spacing. The BUY pill brightens to warm gold so the CTA pops clearly
against the dark card body.
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
from PIL import Image


# ── gloss_sweep patch ─────────────────────────────────────────────────────────
# BLEND_ADD reads RGB directly (source alpha ignored) so the sheen lives in the
# RGB channels, not alpha — otherwise a near-black enamel body blows to white.
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


# ── tier palette ──────────────────────────────────────────────────────────────
TIERS = [
    ("RARE",      "skin_wizard",    "720",
     {"gem": (108, 188, 252), "glow": (60, 140, 230), "deep": (18, 44, 90)}),
    ("EPIC",      "skin_prism",     "1,400",
     {"gem": (194, 122, 248), "glow": (150, 60, 220), "deep": (44, 10, 80)}),
    ("LEGENDARY", "skin_astronaut", "2,600",
     {"gem": (255, 202, 104), "glow": (220, 160, 40), "deep": (90, 50, 0)}),
]
NAMES = {"RARE": "WIZARD", "EPIC": "PRISM", "LEGENDARY": "ASTRONAUT"}


# ── popup metrics (logical px; flow through m()) ──────────────────────────────
POP_W, POP_H = 260, 442
CX = 130

CARD_L, CARD_T_Y = 10, 127
CARD_R, CARD_B_Y = 250, 436
CARD_RAD = 23

DISC_CY, DISC_R = 135, 53

# Enlarged coin: cy=238 puts the coin top at 194, disc bottom is 188 → 6px gap.
COIN_CY, COIN_R = 238, 44
COLLAR_R = 50        # stud centres at 50 → 6px proud of coin edge (r=44): clasps it
BAND_R   = 49        # gold band sits just inside the stud centres


Y_LOZ = 302
Y_NAME = 330
Y_BTN  = 392


# ── card body ─────────────────────────────────────────────────────────────────
def card_body(big):
    rect = pygame.Rect(m(CARD_L), m(CARD_T_Y),
                       m(CARD_R - CARD_L), m(CARD_B_Y - CARD_T_Y))
    rad = m(CARD_RAD)
    sc.drop_shadow(big, rect, rad, blur=m(8), alpha=165, dy=m(4))
    big.blit(vgrad_stops(rect.w, rect.h, rad, [(0.0, CARD_T), (1.0, CARD_B)],
                         255, gamma=1.15), rect.topleft)
    sc.top_sheen(big, rect, rad, m(30), peak=56)
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    sc.bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 230),
                 w=max(1, m(1.9)))


# ── hero disc ─────────────────────────────────────────────────────────────────
def hero_disc(big, sid, pal):
    cx, cy, r = m(CX), m(DISC_CY), m(DISC_R)
    sc._alpha_aura(big, cx, cy, r + m(18), pal["glow"], peak=52, layers=15)
    sc.cabochon(big, cx, cy, r, CABO_LO, CABO_HI, ring=pal["gem"], ring_a=50)
    sc.blit_thumb(big, sid, cx, cy, int(r * 1.5))
    sc.cabochon_glass(big, cx, cy, r, tint=pal["gem"])
    ring_w = max(3, m(3.0))
    pygame.draw.circle(big, pal["gem"], (cx, cy), r + ring_w // 2 + m(1), ring_w)


# ── facet gem with capped highlight ──────────────────────────────────────────
def _facet_gem_capped(surf, cx, cy, r, base, deep):
    """8-facet brilliant with top-left highlight capped at 25% white so studs
    that share brighter tier hues don't blow out against the card or coin bevel.
    The internal seat dark-circle + external bezel cup together guarantee contrast
    on any underlying surface."""
    body    = base
    t_table = lerp_color(body, WHITE, 0.34)
    t_hi    = lerp_color(body, WHITE, 0.25)   # was 0.55 — capped to prevent blow-out
    t_sh    = lerp_color(body, deep, 0.5)
    t_dk    = lerp_color(deep, NEAR_BLACK, 0.32)
    t_key   = lerp_color(deep, NEAR_BLACK, 0.5)

    # dark seat well so the gem reads on any ground; 'seat_c' replaces the
    # original 'sc' local to avoid shadowing the module alias.
    seat_c = r + m(5)
    seat = pygame.Surface((r * 2 + m(10), r * 2 + m(10)), pygame.SRCALPHA)
    pygame.draw.circle(seat, (0, 0, 0, 175), (seat_c, seat_c), r + m(4))
    pygame.draw.circle(seat, (*sc.GOLD_DEEP, 115), (seat_c, seat_c),
                       r + m(4), max(1, m(0.8)))
    surf.blit(seat, (cx - seat_c, cy - seat_c))

    n = 8
    rot = -math.pi / 2 - math.pi / n
    girdle = [(cx + r * math.cos(rot + 2 * math.pi * i / n),
               cy + r * math.sin(rot + 2 * math.pi * i / n)) for i in range(n)]
    tr = r * 0.46
    table = [(cx + tr * math.cos(rot + 2 * math.pi * i / n),
              cy + tr * math.sin(rot + 2 * math.pi * i / n)) for i in range(n)]
    lx, ly = -0.7071, -0.7071
    for i in range(n):
        a  = girdle[i]
        b  = girdle[(i + 1) % n]
        ta = table[i]
        tb = table[(i + 1) % n]
        mx = (a[0] + b[0]) / 2 - cx
        my = (a[1] + b[1]) / 2 - cy
        ml = math.hypot(mx, my) or 1
        d  = (mx / ml) * lx + (my / ml) * ly
        f  = (d + 1) / 2
        col = lerp_color(lerp_color(t_dk, t_sh, min(1.0, f * 2)),
                         t_hi, max(0.0, (f - 0.5) * 2))
        pygame.draw.polygon(surf, col, [a, b, tb, ta])
    pygame.draw.polygon(surf, t_table, table)
    pygame.draw.polygon(surf, t_key, girdle, width=max(1, m(0.6)))
    for i in range(n):
        pygame.draw.line(surf, (*t_key, 190), girdle[i], table[i], max(1, m(0.4)))
    pr = max(1, int(r * 0.24))
    pip = pygame.Surface((pr * 2 + m(2), pr * 2 + m(2)), pygame.SRCALPHA)
    pygame.draw.circle(pip, (255, 255, 255, 250), (pr + m(1), pr + m(1)), pr)
    surf.blit(pip, (cx - pr - int(r * 0.26), cy - pr - int(r * 0.26)),
              special_flags=pygame.BLEND_ADD)


# ── centrepiece coin ──────────────────────────────────────────────────────────
def centrepiece_coin(big, price, pal):
    cx, cy = m(CX), m(COIN_CY)

    # Aura peak=40 (vs disc's 52) keeps the coin's bloom from merging with the
    # disc aura; the 6px dark gap between the two bodies remains visible.
    sc._alpha_aura(big, cx, cy, m(COIN_R + 16), pal["glow"], peak=40, layers=16)

    # Three-ring bevel gives the enlarged coin a grandiose, weighty feel:
    # dark outer contact → warm gold → pale inner glint.
    pygame.draw.circle(big, (0, 0, 0, 190),            (cx, cy), m(46), m(3))
    pygame.draw.circle(big, (*CARD_RING_BRIGHT, 230),   (cx, cy), m(45), m(2))
    pygame.draw.circle(big, (246, 220, 140, 130),       (cx, cy), m(43), m(1))

    sc.coin_glyph(big, cx, cy, m(43))

    # Top-left specular pip — freshly-minted coin catching the light.
    pr = m(4)
    pip = pygame.Surface((pr * 2 + 2, pr * 2 + 2), pygame.SRCALPHA)
    pygame.draw.circle(pip, (255, 255, 255, 255), (pr + 1, pr + 1), pr)
    big.blit(pip, (m(118) - pr - 1, m(226) - pr - 1),
             special_flags=pygame.BLEND_ADD)

    # Deep-brown ink reads as debossed across all three tier palettes; a bright
    # or saturated numeral would bleed into the coin face on LEGENDARY gold.
    plain_text(big, price, font(13), (cx, m(COIN_CY + 4)),
               (52, 35, 12), shadow_a=150, weight=m(1.0),
               keyline=(70, 52, 8), kw=m(0.9))


# ── collar: 240° continuous jewelled band (open at top) ──────────────────────
def collar(big, pal):
    cx, cy = m(CX), m(COIN_CY)
    # -30° to 210° wraps UNDER the coin through the bottom; top gap keeps the
    # disc visible above the collar opening.
    a0, a1 = -30.0, 210.0

    # Thin gold band the studs sit on — composited on a temp surface so its
    # alpha blends over the card face instead of punching through it.
    band = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pts = []
    steps = 96
    for k in range(steps + 1):
        a = math.radians(a0 + (a1 - a0) * k / steps)
        pts.append((cx + m(BAND_R) * math.cos(a), cy + m(BAND_R) * math.sin(a)))
    pygame.draw.lines(band, (*CARD_RING_BRIGHT, 180), False, pts, max(1, m(2)))
    big.blit(band, (0, 0))

    # 11 studs (10 intervals) so one stud lands exactly at the 90° bottom apex.
    # Size tapers from apex (r=6) → shoulder (r=5) → opening ends (r=4) so the
    # eye reads the arc as one continuous sweeping band, not uniform dots.
    for i in range(11):
        a_deg = a0 + (a1 - a0) * i / 10
        dist  = abs(a_deg - 90.0)            # angular distance from bottom apex
        if dist < 12:
            gem_r = m(6)     # single bottom apex stud — the clasp centre
        elif dist < 80:
            gem_r = m(5)     # shoulder studs
        else:
            gem_r = m(4)     # opening-end studs

        a  = math.radians(a_deg)
        sx = int(cx + m(COLLAR_R) * math.cos(a))
        sy = int(cy + m(COLLAR_R) * math.sin(a))

        # Dark bezel cup drawn before the gem so every stud has a defined
        # contrast seat and doesn't dissolve into the card or the coin's bevel.
        cup_r = gem_r + 2
        cup = pygame.Surface((cup_r * 2 + 2, cup_r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(cup, (0, 0, 0, 160), (cup_r + 1, cup_r + 1), cup_r)
        big.blit(cup, (sx - cup_r - 1, sy - cup_r - 1))

        _facet_gem_capped(big, sx, sy, gem_r, pal["gem"], pal["deep"])


# ── rarity lozenge ────────────────────────────────────────────────────────────
def rarity_lozenge(big, tier_word, pal):
    cx, cy = m(CX), m(Y_LOZ)
    w, h   = m(116), m(26)
    notch  = m(6)
    x0, y0 = cx - w // 2, cy - h // 2
    stops = [(0.0, pal["gem"]), (0.5, pal["glow"]), (1.0, pal["deep"])]
    body  = vgrad_stops(w, h, 0, stops, 255, gamma=1.08)
    poly  = [(notch, 0), (w - notch, 0), (w, h // 2), (w - notch, h),
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
    inpoly  = [(x0 + px + (1 if px < w / 2 else -1) * m(1.6),
                y0 + py + (1 if py < h / 2 else -1) * m(1.2)) for px, py in poly]
    pygame.draw.polygon(big, (*edge_br, 150), inpoly, width=max(1, m(1)))
    fsz = 12
    f   = font(fsz)
    while sc._glyph_base(tier_word, f, m(1.6)).get_width() > w - notch * 2 - m(8) \
            and fsz > 6:
        fsz -= 0.5
        f = font(fsz)
    plain_text(big, tier_word, f, (cx, cy), (250, 248, 240),
               shadow_a=150, tracking=m(1.6), weight=m(1.0),
               keyline=(10, 10, 22), kw=m(0.8))


# ── pill buttons ──────────────────────────────────────────────────────────────
def pill_button(big, cx, label, stops, bevel_bright, label_c, gloss,
                h_lp=46, sheen_peak=0):
    w, h = m(106), m(h_lp)
    rad  = m(12)
    rect = pygame.Rect(m(cx) - w // 2, m(Y_BTN) - h // 2, w, h)
    body = vgrad_stops(w, h, rad, stops, 255, gamma=1.1)
    sh   = pygame.Surface((w, h + m(3)), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 120), (0, m(3), w, h), border_radius=rad)
    big.blit(sh, (rect.x, rect.y))
    big.blit(body, rect.topleft)
    sc.gloss_sweep(big, rect, rad, peak=gloss)
    if sheen_peak:
        # top_sheen uses normal alpha compositing (not BLEND_ADD) so it
        # lightens the warm gold crown without blowing out the gradient.
        sc.top_sheen(big, rect, rad, m(30), peak=sheen_peak)
    sc.bevel_rim(big, rect, rad, CARD_RING_DEEP, bevel_bright, w=max(1, m(1.6)))
    plain_text(big, label, font(14), rect.center, label_c,
               shadow_a=170, tracking=m(1.2), weight=m(1.0),
               keyline=(6, 6, 16), kw=m(0.9))


# ── popup ─────────────────────────────────────────────────────────────────────
def render_popup(tier_word, sid, price, pal):
    big = pygame.Surface((POP_W * SS, POP_H * SS), pygame.SRCALPHA)
    card_body(big)
    centrepiece_coin(big, price, pal)
    collar(big, pal)
    rarity_lozenge(big, tier_word, pal)
    plain_text(big, NAMES[tier_word], font(15), (m(CX), m(Y_NAME)),
               (250, 248, 240), shadow_a=160, weight=m(0.9),
               keyline=(6, 6, 16), kw=m(1.0))
    # BUY: warm gold pill so the CTA contrasts the dark card body; taller (h=50)
    # and crowned with top_sheen so it reads as the primary action at a glance.
    pill_button(big, 70, "BUY",
                [(0.0, (155, 115, 32)), (0.5, (95, 68, 16)), (1.0, (55, 38, 8))],
                (*CARD_RING_BRIGHT, 230), (255, 244, 210), gloss=42,
                h_lp=50, sheen_peak=55)
    # CANCEL: unchanged dark enamel — recessive against the BUY gold.
    pill_button(big, 190, "CANCEL",
                [(0.0, (30, 26, 40)), (1.0, (18, 16, 28))],
                (*CARD_RING_BRIGHT, 160), (226, 222, 234), gloss=16)
    # Disc drawn last so its overhanging aura crowns the card without clipping.
    hero_disc(big, sid, pal)
    return pygame.transform.smoothscale(big, (POP_W, POP_H))


# ── surface → PIL ─────────────────────────────────────────────────────────────
def surf_to_pil(surf):
    w, h = surf.get_size()
    raw  = pygame.image.tostring(surf, "RGBA")
    return Image.frombytes("RGBA", (w, h), raw)


def panel_2x(tier_word, sid, price, pal):
    popup_1x = render_popup(tier_word, sid, price, pal)
    pil = surf_to_pil(popup_1x)
    return pil.resize((POP_W * 2, POP_H * 2), Image.LANCZOS)


# ── three-tier review sheet ───────────────────────────────────────────────────
PW, PH   = POP_W * 2, POP_H * 2
GAP      = 24
MARGIN   = 40
HEAD     = 116
LABEL_H  = 64
CANVAS_W = MARGIN * 2 + PW * 3 + GAP * 2
CANVAS_H = HEAD + PH + LABEL_H

canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), (8, 8, 20))

title = _font(34, True).render(
    "confirm_purchase_v7  ·  coin-collar-halo  ·  round 2", True, (232, 226, 208))
sub = _font(21, True).render(
    "continuous jewelled collar · coin r=44 cy=238 · warm-gold BUY · deep-brown numeral",
    True, (150, 156, 178))
canvas.paste(surf_to_pil(title), (MARGIN, 30), surf_to_pil(title))
canvas.paste(surf_to_pil(sub),   (MARGIN, 76), surf_to_pil(sub))

lab = _font(26, True)
for i, (word, sid, price, pal) in enumerate(TIERS):
    panel = panel_2x(word, sid, price, pal)
    px    = MARGIN + i * (PW + GAP)
    py    = HEAD
    canvas.paste(panel, (px, py), panel)
    tcol  = lerp_color(pal["gem"], WHITE, 0.25)
    tsurf = lab.render(word, True, tcol)
    tpil  = surf_to_pil(tsurf)
    tx    = px + PW // 2 - tsurf.get_width() // 2
    canvas.paste(tpil, (tx, py + PH + 14), tpil)

OUT = "/home/user/skybit/docs/confirm_purchase_v7/coin-collar-halo/round_2.png"
os.makedirs(os.path.dirname(OUT), exist_ok=True)
canvas.save(OUT)
print("saved", OUT, canvas.size)
