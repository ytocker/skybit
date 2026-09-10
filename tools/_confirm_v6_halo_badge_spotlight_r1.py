#!/usr/bin/env python3
"""
halo-badge × spotlight-marquee-halo hybrid — confirm_purchase_v6 round 1.

Structure is the v5 HALO-BADGE card, reverse-engineered from
docs/confirm_purchase_v5/halo-badge/round_2.png by pixel sampling:
  - overhanging cabochon disc crowning the card top (~44% of the disc
    overhangs; centre sits ~6 px below the card edge), standard gold bezel
    + faint tier tint (no crisp tier ring — tier is carried by the halo);
  - a small faceted tier GEM badge peeking just below the disc (the "badge");
  - caption plate: cream item NAME, gold PRICE CHIP, dark CONFIRM button
    with light lavender text;
  - rounded-rect indigo body, gold bevel rim + dark keyline, inner tray line.

The ONLY thing swapped in from spotlight-marquee is the disc BLOOM: the v5
badge's original soft additive glow is replaced by spotlight's two-pass
_alpha_aura hero aura — raw tier `glow` colour, NO white-lerp, NO near-white
smear (outer r+55/peak95/24 layers, inner r+20/peak70/12 layers). Because the
passes are normal alpha-carry blits they survive compositing in the transparent
headroom above the card top, so the tier hue reads unmistakably before any text.
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
    plain_text, price_chip, chip_body, facet_gem,
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
POP_W, POP_H = 200, 296
CX = POP_W // 2                                  # 100

CARD_X   = 8
CARD_W   = POP_W - CARD_X * 2                    # 184
CARD_TOP = 98
CARD_H   = 186
CARD_BOT = CARD_TOP + CARD_H                     # 284
CARD_RAD = 18

# Overhanging cabochon disc: ~44% overhangs; centre ~6 px below card top.
R_HERO   = 41
DISC_CY  = CARD_TOP + 6                           # 104
DISC_BOT = DISC_CY + R_HERO                       # 145

# Caption plate — card-top-relative offsets straight off the reference read.
GEM_CY   = CARD_TOP + 50                          # 148  (tier gem badge)
GEM_R    = 11
Y_NAME   = CARD_TOP + 96                          # 194
Y_CHIP   = CARD_TOP + 137                         # 235
Y_BTN    = CARD_TOP + 166                         # 264


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
    """Dark indigo-lavender action pill with light 'CONFIRM' text — the v5
    badge's caption-plate button (light glyphs on a dark ground, subtle rim)."""
    h = m(22)
    w = m(96)
    r = pygame.Rect(m(CX) - w // 2, m(Y_BTN) - h // 2, w, h)
    chip_body(big, r, h // 2, (72, 76, 112), (36, 38, 68),
              (10, 12, 26), (150, 156, 192), gloss=54)
    plain_text(big, "CONFIRM", font(11), r.center, (214, 216, 236),
               shadow_a=150, tracking=m(1.2), weight=m(0.9),
               keyline=(10, 12, 26), kw=m(0.9))


def _hero_disc(big, sid, pal):
    """Overhanging cabochon medallion drawn last so it crowns the plate. The
    v6 spotlight aura reaches into the transparent headroom above the card,
    unclipped; the disc itself keeps the v5 badge's gold bezel + faint tier
    tint (tier hue is carried by the halo + the gem badge, not a disc ring)."""
    cx, cy, r = m(CX), m(DISC_CY), m(R_HERO)
    _hero_aura(big, cx, cy, r, pal["glow"])
    cabochon(big, cx, cy, r, CABO_LO, CABO_HI, ring=pal["gem"], ring_a=50)
    blit_thumb(big, sid, cx, cy, int(r * 1.5))
    cabochon_glass(big, cx, cy, r, tint=pal["gem"])


def render_popup(tier_word, sid, price, pal):
    big = pygame.Surface((POP_W * SS, POP_H * SS), pygame.SRCALPHA)
    _card_body(big)
    # caption plate first, then the disc (with its aura) crowns it last.
    facet_gem(big, m(CX), m(GEM_CY), m(GEM_R), pal["gem"], pal["deep"])
    name = sc._name(sid)
    plain_text(big, name, font(14), (m(CX), m(Y_NAME)), (250, 248, 240),
               shadow_a=160, weight=m(0.9), keyline=(6, 6, 16), kw=m(1.0))
    price_chip(big, m(CX), m(Y_CHIP), f"{price:,}", m(22), affordable=True)
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
    "confirm_purchase_v6 — halo-badge x spotlight halo  (round 1)", True,
    (232, 226, 208))
canvas.blit(title, (MARGIN, 15))
sub = _font(11, True).render(
    "v5 halo-badge structure kept intact  ·  disc bloom swapped for spotlight's "
    "two-pass tier aura (raw glow, no white-lerp, no near-white smear)",
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

out = "/home/user/skybit/docs/confirm_purchase_v6/halo-badge-spotlight/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(canvas, out)
print("saved", out, canvas.get_size())
