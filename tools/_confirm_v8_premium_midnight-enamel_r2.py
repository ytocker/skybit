#!/usr/bin/env python3
"""midnight-enamel · confirm_purchase_v8 · premium-v1 · round_2

Haute-horlogerie watch-dial finish laid over the SHIPPED confirm-purchase
popup — every position is the production layout; only the materials change.
Zone A is a gold-on-black engine-turned (guilloché) subdial price chip; Zone B
is a cloisonné-enamel rarity banner that, for LEGENDARY, diverges to peacock
teal so the rarity band never collapses into the gold-on-black subdial lane.
"""
import os, sys, math
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame
pygame.init()
pygame.display.set_mode((1, 1))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import game.store_cards as sc


# mandatory gloss_sweep patch — a near-black enamel body must not be blown white
# by a flat BLEND_ADD sweep, so the highlight follows a falloff curve.
def _safe_gloss(surf, rect, radius, peak=46):
    w, h = rect[2], rect[3]
    gsurf = pygame.Surface((w, h), pygame.SRCALPHA)
    gsurf.fill((0, 0, 0, 0))
    steps = 10
    for i in range(steps):
        t = i / (steps - 1)
        alpha = int(peak * (1 - t))
        bar_h = max(1, int(h * 0.45 * (1 - t)))
        pygame.draw.ellipse(gsurf, (255, 255, 255, alpha),
            (int(w * 0.1), int(h * 0.04 + i * 1.5), int(w * 0.8), bar_h))
    surf.blit(gsurf, (rect[0], rect[1]))
sc.gloss_sweep = _safe_gloss


from game.store_cards import (m, SS, font, vgrad_stops, plain_text, coin_glyph,
                              CABO_LO, CABO_HI, CARD_T, CARD_B,
                              CARD_RING_BRIGHT, CARD_RING_DEEP, GOLD_A_RIM_DARK)
from PIL import Image, ImageDraw
import pathlib


# ── geometry (production confirm popup — do not move) ─────────────────────────
POP_W, POP_H = 260, 442
CX = POP_W // 2
CARD_X, CARD_TOP, CARD_W, CARD_H, CARD_RAD = 10, 127, 240, 299, 23
R_HERO, DISC_CY = 53, 135
GEM_R, GEM_CY, GEM_L_X, GEM_R_X = 14, 152, 43, 217
Y_NAME, NAME_FS = 213, 45
CHIP_CY = 247
SHELF_X, SHELF_Y, SHELF_W, SHELF_H = 17, 335, 226, 91
BTN_W, BTN_H, BTN_RAD, BTN_CY, BTN_GAP = 99, 31, 12, 360, 10
BUY_CX = CX - (BTN_W + BTN_GAP) // 2
CAN_CX = CX + (BTN_W + BTN_GAP) // 2
Y_BANNER, BOT_GEM_CY = 402, 402

CHIP_W, CHIP_H, CHIP_RAD = 88, 26, 8

# Deep-cut incised groove colour — the dark wall of an engraved channel.
GUILLOCHE = (86, 50, 8)
# Visible-enamel guilloché arcs need a substantially warmer, lighter gold so
# the concentric rose-engine rings lift above the warm near-black field.
GUILLOCHE_VIS = (150, 110, 40)

# Gold outer keyline colour for the BUY button rim — same family as the chip
# bezel so the primary tap target ties visually to the coin payment concept.
BUY_GOLD = (200, 162, 62)

# LEGENDARY diverges the whole cloisonné Zone B to peacock/teal so the rarity
# band reads as a distinct enamel cloison, never as the gold-on-black subdial.
PEACOCK = {"gem": (46, 150, 150), "deep": (10, 54, 60), "glow": (96, 206, 196)}

PALETTES = {
    "RARE":      {"gem": (108, 188, 252), "deep": (28, 60, 120), "glow": (160, 210, 255)},
    "EPIC":      {"gem": (194, 122, 248), "deep": (72, 28, 120), "glow": (230, 160, 255)},
    "LEGENDARY": {"gem": (255, 202, 104), "deep": (120, 72, 12), "glow": (255, 230, 140)},
}
TIERS = [("RARE", "skin_wizard", "720"),
         ("EPIC", "skin_prism", "1,400"),
         ("LEGENDARY", "skin_astronaut", "2,600")]
NAMES = {"RARE": "WIZARD", "EPIC": "PRISM", "LEGENDARY": "ASTRONAUT"}


def _rounded_mask(w, h, rad):
    mk = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(mk, (255, 255, 255, 255), mk.get_rect(), border_radius=rad)
    return mk


# ── card body: enamel plate + satin soleil + regalia border ───────────────────
def card_body(big):
    rect = pygame.Rect(m(CARD_X), m(CARD_TOP), m(CARD_W), m(CARD_H))
    rad = m(CARD_RAD)
    sc.drop_shadow(big, rect, rad, blur=m(8), alpha=165, dy=m(4))
    big.blit(vgrad_stops(rect.w, rect.h, rad,
                         [(0.0, CARD_T), (1.0, CARD_B)], 255, gamma=1.15),
             rect.topleft)
    sc.top_sheen(big, rect, rad, m(30), peak=56)

    # radial wash centred on the hero disc so the satin spokes read as angled
    # light catching a brushed-metal plate rather than a flat scrim — the
    # gradient makes the fan visible by giving it a luminance context to sit in.
    hcx, hcy = m(CX), m(DISC_CY)
    wash = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    max_r = m(260)
    step_px = max(1, m(10))
    for step in range(0, max_r, step_px):
        t = step / max_r
        a = int(10 * (1 - t * t))
        if a > 0:
            pygame.draw.circle(wash, (210, 205, 220, a), (hcx, hcy), max_r - step)
    big.blit(wash, (0, 0))

    # satin soleil at alpha 42 — raised from 18 so the fan reads clearly as a
    # brushed-metal subdial under the dial glass.
    spokes = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    length = m(320)
    for ang in range(12, 169, 11):
        rad_a = math.radians(ang)
        ex = hcx + length * math.cos(rad_a)
        ey = hcy + length * math.sin(rad_a)
        pygame.draw.line(spokes, (*CARD_RING_DEEP, 42), (hcx, hcy),
                         (int(ex), int(ey)), max(1, m(1)))
    spokes.blit(_rounded_mask(rect.w, rect.h, rad), rect.topleft,
                special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(spokes, (0, 0))

    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(1.4)), border_radius=rad)
    sc._draw_regalia_frame(big, rect, rad)


# ── dead zone: gold-incised watchcase groove (double-line engraving) ──────────
def dead_zone_engraving(big):
    band = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    ccy = m(430)
    for rr in (m(150), m(158)):
        # dark groove wall — the cut face of the channel as a rose-lathe would leave it
        rect_dark = pygame.Rect(m(CX) - rr, ccy - rr, rr * 2, rr * 2)
        pygame.draw.arc(band, (30, 24, 10, 65), rect_dark,
                        math.radians(34), math.radians(146), max(1, m(1)))
        # bright highlight 1 px below — the lit lower lip of the incised cut,
        # the same engraving trick used on a polished watchcase chamfer.
        rect_lite = pygame.Rect(m(CX) - rr, ccy - rr + m(1), rr * 2, rr * 2)
        pygame.draw.arc(band, (180, 150, 80, 90), rect_lite,
                        math.radians(34), math.radians(146), max(1, m(1)))
    big.blit(band, (0, 0))


# ── Zone A: engine-turned subdial price chip ──────────────────────────────────
def zone_a(big, price):
    chip = pygame.Rect(0, 0, m(CHIP_W), m(CHIP_H))
    chip.center = (m(CX), m(CHIP_CY))
    crad = m(CHIP_RAD)
    # warm near-black enamel field — blue-black actively swallowed warm guilloché
    # arcs at round_1; removing the blue cast doubles perceived contrast for free.
    sc._dark_chip_body(big, chip, crad,
                       [(0.0, (20, 18, 22)), (1.0, (12, 10, 14))],
                       (70, 52, 14), (236, 206, 140))

    # guilloché in the VISIBLE enamel flanks only — concentric arcs anchored to
    # the chip left and right edges curl into the two exposed enamel strips that
    # bracket the coin+numeral group. At alpha 88 each ring lifts the surface by
    # ~40 lum pts, reading unmistakably as a rose-engine–turned subdial face.
    eng = pygame.Surface(chip.size, pygame.SRCALPHA)
    ecy = chip.h // 2
    # tighter pitch: 5 rings at 3-px intervals (1x) pack 4-5 arcs into the
    # ~22-32 px exposed flank at every tier's price width.
    for ring_r in (m(4), m(7), m(10), m(13), m(16)):
        pygame.draw.circle(eng, (*GUILLOCHE_VIS, 88), (0, ecy), ring_r, max(1, m(1)))
        pygame.draw.circle(eng, (*GUILLOCHE_VIS, 88), (chip.w, ecy), ring_r, max(1, m(1)))
    eng.blit(_rounded_mask(chip.w, chip.h, crad), (0, 0),
             special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(eng, chip.topleft)

    # coin + numeral, side-by-side inline, centred as one group on CX. Cool ink
    # numeral so it reads as a printed dial figure over the black enamel.
    txt = f"{price}"
    num_font = font(18)
    coin_r, gap = m(11), m(4)
    num_w = num_font.size(txt)[0]
    total = coin_r * 2 + gap + num_w
    left = m(CX) - total // 2
    coin_cx = left + coin_r
    num_cx = left + coin_r * 2 + gap + num_w // 2
    coin_glyph(big, coin_cx, m(CHIP_CY), coin_r)
    plain_text(big, txt, num_font, (num_cx, m(CHIP_CY) + m(1)), (220, 224, 218),
               shadow_a=0, weight=m(0.7))


# ── name plate (standard) ─────────────────────────────────────────────────────
def name_text(big, name):
    fs = NAME_FS
    nf = font(fs)
    mw = m(CARD_W - 20)
    while sc._glyph_base(name, nf, 0).get_width() > mw and fs > 24:
        fs -= 1
        nf = font(fs)
    plain_text(big, name, nf, (m(CX), m(Y_NAME)), (250, 248, 240),
               shadow_a=160, weight=m(0.9), keyline=(6, 6, 16), kw=m(1.0))


# ── shelf gradient (standard) ─────────────────────────────────────────────────
def shelf(big):
    shelf_rect = pygame.Rect(m(SHELF_X), m(SHELF_Y), m(SHELF_W), m(SHELF_H))
    shelf_rad = m(CARD_RAD)
    surf = vgrad_stops(shelf_rect.w, shelf_rect.h, 0,
                       [(0.0, (34, 36, 72)), (0.5, (22, 24, 54)), (1.0, (12, 14, 36))],
                       255).copy()
    smask = pygame.Surface(shelf_rect.size, pygame.SRCALPHA)
    pygame.draw.rect(smask, (255, 255, 255, 255), smask.get_rect(),
                     border_bottom_left_radius=shelf_rad,
                     border_bottom_right_radius=shelf_rad)
    surf.blit(smask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    sc.top_sheen(surf, surf.get_rect(), 0, m(20), peak=35)
    pygame.draw.line(surf, (115, 106, 140), (0, 0), (shelf_rect.w - 1, 0), max(1, m(1)))
    seat = pygame.Surface((shelf_rect.w, m(6)), pygame.SRCALPHA)
    for yy in range(m(6)):
        a = int(120 * (1 - yy / m(6)))
        pygame.draw.line(seat, (0, 0, 0, a), (0, yy), (shelf_rect.w - 1, yy))
    big.blit(seat, (shelf_rect.x, shelf_rect.y - m(6)))
    big.blit(surf, shelf_rect.topleft)


# ── buttons — BUY carries a gold keyline to be unmistakably the hero target ───
def buttons(big):
    br = m(BTN_RAD)
    for cx_b, lbl, stops, lab_c, kl_c, pk, rw in [
        # BUY: warm gold label + gold bevel so it reads as the coin-payment action
        (m(BUY_CX), "BUY",
         [(0.0, (38, 40, 84)), (1.0, (22, 24, 56))], (248, 220, 142), (40, 28, 6), 28, m(2.0)),
        (m(CAN_CX), "CANCEL",
         [(0.0, (26, 28, 64)), (1.0, (14, 16, 44))], (150, 155, 200), (8, 6, 20), 14, m(2.2)),
    ]:
        r = pygame.Rect(0, 0, m(BTN_W), m(BTN_H))
        r.center = (cx_b, m(BTN_CY))
        sc.drop_shadow(big, r, br, blur=m(3), alpha=100, dy=m(2))
        big.blit(vgrad_stops(r.w, r.h, br, stops, 255), r.topleft)
        sc.top_sheen(big, r, br, m(12), peak=pk)
        if lbl == "BUY":
            # gold bevel rim ties the tap target visually to the chip/coin palette
            sc.bevel_rim(big, r, br, (60, 44, 10), (220, 185, 90, 230), w=max(1, rw))
            # thin outer gold keyline — the final clear ring around the primary action
            gold_ring = pygame.Surface(big.get_size(), pygame.SRCALPHA)
            pygame.draw.rect(gold_ring, (*BUY_GOLD, 195), r,
                             width=max(1, m(1)), border_radius=br)
            big.blit(gold_ring, (0, 0))
        else:
            sc.bevel_rim(big, r, br, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 230), w=max(1, rw))
        plain_text(big, lbl, font(14 if lbl == "BUY" else 13), r.center, lab_c,
                   shadow_a=130, weight=m(0.8), keyline=kl_c, kw=m(0.9))


# ── Zone B: cloisonné rarity banner + its bottom gem pair ─────────────────────
def zone_b(big, tier_word, zb_pal):
    for gx in [m(GEM_L_X), m(GEM_R_X)]:
        sc._alpha_aura(big, gx, m(BOT_GEM_CY), m(16), zb_pal["glow"], peak=60, layers=14)
        sc.facet_gem(big, gx, m(BOT_GEM_CY), m(GEM_R), zb_pal["gem"], zb_pal["deep"])
    sc._ribbon_lozenge(big, tier_word, m(CX), m(Y_BANNER), m(146), zb_pal)


# ── upper tier gems (standard, real pal) ──────────────────────────────────────
def upper_gems(big, pal):
    sc.facet_gem(big, m(GEM_L_X), m(GEM_CY), m(GEM_R), pal["gem"], pal["deep"])
    sc.facet_gem(big, m(GEM_R_X), m(GEM_CY), m(GEM_R), pal["gem"], pal["deep"])


# ── hero cabochon + chapter ring ──────────────────────────────────────────────
def hero(big, sid, pal):
    cx, cy, r = m(CX), m(DISC_CY), m(R_HERO)
    sc._alpha_aura(big, cx, cy, r + m(55), pal["glow"], peak=95, layers=24)
    sc._alpha_aura(big, cx, cy, r + m(20), pal["glow"], peak=70, layers=12)
    sc.cabochon(big, cx, cy, r, CABO_LO, CABO_HI, ring=pal["gem"], ring_a=50)
    try:
        sc.blit_thumb(big, sid, cx, cy, int(r * 1.5))
    except Exception:
        pygame.draw.circle(big, pal["gem"], (cx, cy), int(r * 0.7))
    sc.cabochon_glass(big, cx, cy, r, tint=pal["gem"])
    # ONE chapter-ring in the tier glow — the dial's minute track, nothing more.
    ring = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.circle(ring, (*pal["glow"], 140), (cx, cy), r, max(1, m(1)))
    big.blit(ring, (0, 0))


def render_popup(tier_word, sid, price):
    pal = PALETTES[tier_word]
    zb_pal = PEACOCK if tier_word == "LEGENDARY" else pal
    big = pygame.Surface((POP_W * SS, POP_H * SS), pygame.SRCALPHA)
    card_body(big)
    upper_gems(big, pal)
    name_text(big, NAMES[tier_word])
    dead_zone_engraving(big)
    zone_a(big, price)
    shelf(big)
    buttons(big)
    zone_b(big, tier_word, zb_pal)
    hero(big, sid, pal)
    return pygame.transform.smoothscale(big, (POP_W, POP_H))


# ── strip ─────────────────────────────────────────────────────────────────────
MARGIN, HEAD, GAP = 20, 58, 12
canvas_w = MARGIN * 2 + POP_W * 3 + GAP * 2
canvas_h = HEAD + POP_H + MARGIN
strip = Image.new("RGB", (canvas_w, canvas_h), (8, 8, 20))
idr = ImageDraw.Draw(strip)
idr.text((MARGIN, 20),
         "midnight-enamel  ·  confirm_purchase_v8  ·  premium-v1  ·  round_2",
         fill=(232, 226, 208))
for i, (tw, sid, ps) in enumerate(TIERS):
    pop = render_popup(tw, sid, ps)
    pil = Image.frombytes("RGB", (POP_W, POP_H), pygame.image.tostring(pop, "RGB"))
    x = MARGIN + i * (POP_W + GAP)
    strip.paste(pil, (x, HEAD))
    idr.text((x + POP_W // 2, HEAD + POP_H + 4), tw, fill=(180, 176, 210), anchor="mt")
out = strip.resize((canvas_w * 2, canvas_h * 2), Image.LANCZOS)

OUTDIR = "/home/user/skybit/docs/confirm_purchase_v8/premium-v1/midnight-enamel"
pathlib.Path(OUTDIR).mkdir(parents=True, exist_ok=True)
OUT = OUTDIR + "/round_2.png"
out.save(OUT)
print(f"saved {out.size[0]}x{out.size[1]}  ->  {OUT}")
