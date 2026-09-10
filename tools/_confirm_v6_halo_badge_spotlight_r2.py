#!/usr/bin/env python3
"""
halo-badge × spotlight-marquee-halo hybrid — confirm_purchase_v6 round 2.

Round 2 layout notes over r1:
  - the single centre tier GEM badge is replaced by a symmetric PAIR of tier
    gems, one tucked in each top corner of the card body (just inside the bevel
    rim) so the rarity read frames the overhanging disc instead of sitting under
    it;
  - a notched-hex RARITY BANNER (store_cards' `_ribbon` construction, re-voiced
    with a white tier word on the raw 3-stop tier gradient) sits just above the
    item name so the tier is legible as a word, not only a hue;
  - to make room for the banner the NAME / PRICE CHIP / CONFIRM button all slide
    down ~28 px and the card body + popup grow to match so nothing clips.

Everything else is r1 verbatim: the overhanging cabochon disc + the transplanted
spotlight two-pass hero aura (raw tier glow, no white-lerp), the gold bevel rim,
the caption plate, the price chip and the CONFIRM pill. The halo is untouched.
"""
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
import sys
sys.path.insert(0, "/home/user/skybit")

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

import game.store_cards as sc
from game.store_cards import (
    vgrad_stops, drop_shadow, bevel_rim, top_sheen,
    plain_text, price_chip, chip_body, facet_gem, _glyph_base,
    cabochon, cabochon_glass, blit_thumb, font, m, SS,
    CABO_LO, CABO_HI, CARD_T, CARD_B, CARD_RING_DEEP, CARD_RING_BRIGHT,
)
from game.hud import _font
from game.draw import lerp_color, NEAR_BLACK, WHITE


# BLEND_ADD alpha rule: keep the sweep in RGB magnitude so the additive path
# never blows the price-chip gold to white (BLEND_ADD ignores source alpha).
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


# ── brief palette ─────────────────────────────────────────────────────────────
TIERS = [
    ("RARE",      "skin_lorikeet",  600,
     {"gem": (108, 188, 252), "glow": (60, 140, 230),  "deep": (18, 44, 90)}),
    ("EPIC",      "skin_prism",    1400,
     {"gem": (194, 122, 248), "glow": (150, 60, 220),  "deep": (44, 10, 80)}),
    ("LEGENDARY", "skin_kitsune",  3500,
     {"gem": (255, 202, 104), "glow": (220, 160, 40),  "deep": (90, 50, 0)}),
]


# ── popup metrics (logical px, scaled from the v5 halo-badge pixel read) ───────
# The card + popup grow by 28 px vs r1 so the NAME/CHIP/BUTTON can slide down to
# make room for the rarity banner above the name without anything clipping.
POP_W, POP_H = 200, 340
CX = POP_W // 2                                  # 100

CARD_X   = 8
CARD_W   = POP_W - CARD_X * 2                    # 184
CARD_TOP = 98
CARD_H   = 230
CARD_BOT = CARD_TOP + CARD_H                     # 328
CARD_RAD = 18

# Overhanging cabochon disc: ~44% overhangs; centre ~6 px below card top.
R_HERO   = 41
DISC_CY  = CARD_TOP + 6                           # 104
DISC_BOT = DISC_CY + R_HERO                       # 145

# Tier gem PAIR — pulled inward from card corners.
GEM_R    = 11
GEM_CY   = CARD_TOP + GEM_R + 8                   # 117
GEM_L_X  = CARD_X + GEM_R + 14                    # 33
GEM_R_X  = POP_W - CARD_X - GEM_R - 14            # 167

# Caption plate — large name high up, banner below it, chip+button lower/larger.
NAME_FS  = 30
Y_NAME   = DISC_BOT + 10                          # 155 — tight under disc
Y_BANNER = Y_NAME + 20                            # 175
Y_CHIP   = Y_BANNER + 54                          # 229 — pushed lower
Y_BTN    = Y_CHIP   + 44                          # 273 — pushed lower
BANNER_W = 120
BANNER_H = 22
CHIP_H   = 28                                     # larger price chip
BTN_H    = 30                                     # larger confirm button
BTN_W    = 136                                    # wider confirm button


# ── spotlight-marquee halo (transplanted verbatim) ────────────────────────────

def _alpha_aura(surf, cx, cy, radius, color, peak=27, layers=15):
    """Feathered halo via normal alpha-carry blits — survives compositing in
    transparent headroom above the card top where BLEND_ADD would leave alpha=0."""
    for i in range(layers, 0, -1):
        r = int(radius * i / layers)
        if r <= 0:
            continue
        a = int(peak * (1 - (i - 1) / layers) ** 1.6)
        if a <= 0:
            continue
        g = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(g, (*color, a), (r + 1, r + 1), r)
        surf.blit(g, (cx - r - 1, cy - r - 1))


def _hero_aura(big, cx, cy, r, glow):
    """Pure tier-hued radial bloom — two concentric passes, no white lerp.
    The broad outer pass (r+55) reaches 40-60 px above the card top; the tighter
    inner ring (r+20) concentrates the hue at the disc edge. Raw glow colour so
    sky-blue / vivid-purple / warm-gold reads unmistakably."""
    _alpha_aura(big, cx, cy, r + m(55), glow, peak=95, layers=24)
    _alpha_aura(big, cx, cy, r + m(20), glow, peak=70, layers=12)


# ── rarity banner (store_cards notched-hex ribbon, re-voiced) ─────────────────

def _tier_banner(big, cx, cy, w_log, h_log, tier_word, pal):
    """Notched-hex rarity banner using store_cards' `_ribbon` construction, but
    re-voiced for the confirm popup: a WHITE/cream bold tier word over the raw
    3-stop tier gradient (gem -> glow -> deep) with a dark keyline on the hex
    outline. Louder than the store grid's dark-text ribbon so the tier reads as a
    word at a glance, one clear lane above the item name."""
    w, h = m(w_log), m(h_log)
    notch = m(6)
    x0, y0 = m(cx) - w // 2, m(cy) - h // 2
    stops = [(0.0, pal["gem"]), (0.5, pal["glow"]), (1.0, pal["deep"])]
    body = vgrad_stops(w, h, 0, stops, 255, gamma=1.08)
    poly = [(notch, 0), (w - notch, 0), (w, h // 2), (w - notch, h),
            (notch, h), (0, h // 2)]
    pmask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(pmask, (255, 255, 255, 255), poly)
    body.blit(pmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    # soft cast shadow so the banner floats above the plate
    sh = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(sh, (0, 0, 0, 130), poly)
    big.blit(sh, (x0, y0 + m(2)))
    big.blit(body, (x0, y0))
    abspoly = [(x0 + px, y0 + py) for px, py in poly]
    pygame.draw.polygon(big, (6, 6, 16), abspoly, width=max(1, m(1.6)))
    # white tier word, auto-shrunk so even LEGENDARY sits inside the notches
    fsz = h_log * 0.52
    f = font(fsz)
    avail = w - notch * 2 - m(8)
    while _glyph_base(tier_word, f, m(1.6)).get_width() > avail and fsz > 6:
        fsz -= 0.5
        f = font(fsz)
    plain_text(big, tier_word, f, (m(cx), m(cy)), (250, 248, 240),
               shadow_a=150, tracking=m(1.6), weight=m(1.0),
               keyline=(10, 10, 22), kw=m(0.8))


# ── card pieces ───────────────────────────────────────────────────────────────

def _card_body(big):
    rect = pygame.Rect(m(CARD_X), m(CARD_TOP), m(CARD_W), m(CARD_H))
    rad = m(CARD_RAD)
    drop_shadow(big, rect, rad, blur=m(8), alpha=165, dy=m(4))
    big.blit(vgrad_stops(rect.w, rect.h, rad, [(0.0, CARD_T), (1.0, CARD_B)],
                         255, gamma=1.15), rect.topleft)
    top_sheen(big, rect, rad, m(30), peak=56)
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 230),
              w=max(1, m(1.9)))
    tray = rect.inflate(-m(8), -m(8))
    pygame.draw.rect(big, (*CARD_RING_BRIGHT, 55), tray, width=max(1, m(1)),
                     border_radius=rad - m(3))


def _confirm_button(big, pal):
    """Tier-coloured confirm pill — vibrant gradient using the tier gem/glow so
    it feels like the action belongs to the item being purchased."""
    h = m(BTN_H)
    w = m(BTN_W)
    r = pygame.Rect(m(CX) - w // 2, m(Y_BTN) - h // 2, w, h)
    top_c = lerp_color(pal["gem"], WHITE, 0.18)
    bot_c = lerp_color(pal["deep"], (4, 4, 12), 0.4)
    rim_c = lerp_color(pal["gem"], WHITE, 0.45)
    chip_body(big, r, h // 2, top_c, bot_c, (4, 4, 12), rim_c, gloss=72)
    plain_text(big, "CONFIRM", font(13), r.center, (255, 255, 255),
               shadow_a=180, tracking=m(1.4), weight=m(1.0),
               keyline=lerp_color(pal["deep"], (0, 0, 0), 0.5), kw=m(1.0))


def _hero_disc(big, sid, pal):
    """Overhanging cabochon medallion drawn last so it crowns the plate. The
    v6 spotlight aura reaches into the transparent headroom above the card,
    unclipped; the disc itself keeps the v5 badge's gold bezel + faint tier
    tint (tier hue is carried by the halo + the gem badges, not a disc ring)."""
    cx, cy, r = m(CX), m(DISC_CY), m(R_HERO)
    _hero_aura(big, cx, cy, r, pal["glow"])
    cabochon(big, cx, cy, r, CABO_LO, CABO_HI, ring=pal["gem"], ring_a=50)
    blit_thumb(big, sid, cx, cy, int(r * 1.5))
    cabochon_glass(big, cx, cy, r, tint=pal["gem"])


def render_popup(tier_word, sid, price, pal):
    big = pygame.Surface((POP_W * SS, POP_H * SS), pygame.SRCALPHA)
    _card_body(big)
    # caption plate first, then the disc (with its aura) crowns it last.
    # symmetric tier gems frame the top corners of the card body.
    facet_gem(big, m(GEM_L_X), m(GEM_CY), m(GEM_R), pal["gem"], pal["deep"])
    facet_gem(big, m(GEM_R_X), m(GEM_CY), m(GEM_R), pal["gem"], pal["deep"])
    name = sc._name(sid)
    plain_text(big, name, font(NAME_FS), (m(CX), m(Y_NAME)), (250, 248, 240),
               shadow_a=160, weight=m(0.9), keyline=(6, 6, 16), kw=m(1.0))
    _tier_banner(big, CX, Y_BANNER, BANNER_W, BANNER_H, tier_word, pal)
    price_chip(big, m(CX), m(Y_CHIP), f"{price:,}", m(CHIP_H), affordable=True)
    _confirm_button(big, pal)
    _hero_disc(big, sid, pal)
    return pygame.transform.smoothscale(big, (POP_W, POP_H))


# =============================================================================
# Review sheet — three tiers side by side over a modal-style scrim
# =============================================================================
GUT    = 24
MARGIN = 24
HEAD   = 60
CANVAS_W = MARGIN * 2 + POP_W * 3 + GUT * 2
CANVAS_H = HEAD + POP_H + 30

canvas = pygame.Surface((CANVAS_W, CANVAS_H))
for y in range(CANVAS_H):
    pygame.draw.line(canvas, lerp_color((10, 11, 26), (5, 5, 14), y / CANVAS_H),
                     (0, y), (CANVAS_W, y))

title = _font(19, True).render(
    "confirm_purchase_v6 — halo-badge x spotlight halo  (round 2)", True,
    (232, 226, 208))
canvas.blit(title, (MARGIN, 15))
sub = _font(11, True).render(
    "r1 kept intact  ·  centre gem -> PAIR of top-corner tier gems  ·  notched-hex "
    "rarity BANNER above the name (name/chip/button slid down to fit)",
    True, (150, 156, 178))
canvas.blit(sub, (MARGIN, 38))

lab = _font(13, True)
for i, (tier_word, sid, price, pal) in enumerate(TIERS):
    pop = render_popup(tier_word, sid, price, pal)
    px = MARGIN + i * (POP_W + GUT)
    py = HEAD
    canvas.blit(pop, (px, py))
    t = lab.render(tier_word, True, lerp_color(pal["gem"], WHITE, 0.25))
    canvas.blit(t, t.get_rect(center=(px + POP_W // 2, py - 6)))

out = "/home/user/skybit/docs/confirm_purchase_v6/halo-badge-spotlight/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(canvas, out)
print("saved", out, canvas.get_size())
