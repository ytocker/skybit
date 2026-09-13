#!/usr/bin/env python3
"""gilt-codex · confirm_purchase_v8 · card-frame-v1 · round_1

An illuminated-manuscript codex page: warm parchment body inside the ornate
gold double-bevel regalia frame, a gothic-arch niche framing the hero portrait,
an engraved nameplate, a warm-gold price ledger (Zone A), and a wax-seal ribbon
footer (Zone B). LEGENDARY forces Zone B to oxblood enamel so the tier never
reads gold-on-gold across both zones.
"""
import os, sys, math
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.path.insert(0, "/home/user/skybit")
import pygame; pygame.init(); pygame.display.set_mode((1, 1))
import game.store_cards as sc
from game.store_cards import (m, SS, font, vgrad_stops, bevel_rim, top_sheen,
                              coin_glyph, facet_gem, _alpha_aura, plain_text,
                              CABO_LO, CABO_HI, CARD_RING_BRIGHT, CARD_RING_DEEP)
from PIL import Image, ImageDraw

# mandatory gloss_sweep patch — BLEND_ADD amount must follow the curve so a
# body isn't blown white.
def _gloss_sweep_fixed(surf, rect, radius, peak=120):
    sweep = pygame.Surface(rect.size, pygame.SRCALPHA)
    h = max(1, rect.h)
    for y in range(h):
        v = int(peak * (1 - y / h) ** 2.4)
        if v <= 0: continue
        pygame.draw.line(sweep, (v, v, v, 255), (0, y), (rect.w, y))
    sm = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(sm, (255, 255, 255, 255), sm.get_rect(), border_radius=radius)
    sweep.blit(sm, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(sweep, rect.topleft, special_flags=pygame.BLEND_ADD)
sc.gloss_sweep = _gloss_sweep_fixed

# The strip carries only (tier_word, palette); the hero/name/price are keyed off
# tier so the sheet reads as three real store items, not placeholder swatches.
TIERS = [
    ("RARE",      {"gem": (108, 188, 252), "glow": (60, 140, 220), "deep": (20, 60, 130)}),
    ("EPIC",      {"gem": (194, 122, 248), "glow": (140, 60, 220), "deep": (70, 20, 160)}),
    ("LEGENDARY", {"gem": (255, 202, 104), "glow": (220, 150, 40), "deep": (140, 80, 10)}),
]
HERO = {"RARE": ("skin_wizard", "WIZARD"),
        "EPIC": ("skin_prism", "PRISM"),
        "LEGENDARY": ("skin_astronaut", "ASTRONAUT")}
PRICE = "720"

POP_W, POP_H = 260, 442; CX = 130
CARD_X, CARD_TOP_Y, CARD_W, CARD_H, CARD_RAD = 10, 127, 240, 299, 23
DISC_CY, DISC_R = 135, 53
ZA_CY = 247; ZB_CY = 402
BOT_GEM_L_X, BOT_GEM_R_X, GEM_R = 43, 217, 14
BTN_W, BTN_H, BTN_RAD, BTN_CY, BTN_GAP = 99, 31, 12, 360, 10
BUY_CX = CX - (BTN_W + BTN_GAP) // 2
CAN_CX = CX + (BTN_W + BTN_GAP) // 2

# Parchment vellum stops — three warm-cream steps down the leaf.
PARCHMENT = [(0.0, (238, 222, 182)), (0.5, (224, 206, 162)), (1.0, (214, 196, 150))]
INK = (60, 40, 20)            # illuminated-manuscript nameplate ink
LEDGER_STOPS = [(0.0, (180, 140, 40)), (0.5, (200, 160, 60)), (1.0, (160, 120, 30))]
LEDGER_RIM_D, LEDGER_RIM_B = (120, 90, 20), (240, 210, 120)
# Zone B on LEGENDARY: oxblood wax-seal enamel so the crimson footer sits clearly
# apart from the gold price ledger above — never gold in both zones.
OXBLOOD = {"gem": (160, 30, 30), "glow": (120, 20, 20), "deep": (80, 14, 14)}


def codex_body(big):
    rect = pygame.Rect(m(CARD_X), m(CARD_TOP_Y), m(CARD_W), m(CARD_H)); rad = m(CARD_RAD)
    sc.drop_shadow(big, rect, rad, blur=m(8), alpha=165, dy=m(4))
    big.blit(vgrad_stops(rect.w, rect.h, rad, PARCHMENT, 255, gamma=1.05), rect.topleft)
    top_sheen(big, rect, rad, m(28), peak=30)
    sc._draw_regalia_frame(big, rect, rad)
    return rect


def gothic_arch(big):
    """Beveled gold arch behind the portrait: dark seat arc, bright gold, pale
    inner glint, plus short jamb feet at the springline. The disc bezel completes
    the crown, so what reads is a gothic niche shouldering up around the hero."""
    seat = pygame.Rect(m(29), m(139), m(202), m(122))
    bright = pygame.Rect(m(30), m(140), m(200), m(120))
    glint = pygame.Rect(m(32), m(142), m(196), m(116))
    pygame.draw.arc(big, CARD_RING_DEEP, seat, 0, math.pi, max(2, m(4)))
    pygame.draw.arc(big, CARD_RING_BRIGHT, bright, 0, math.pi, max(2, m(3)))
    pygame.draw.arc(big, (255, 240, 190), glint, 0, math.pi, max(1, m(1)))
    for jx in (m(30), m(230)):
        pygame.draw.line(big, CARD_RING_DEEP, (jx, m(200)), (jx, m(207)), max(2, m(4)))
        pygame.draw.line(big, CARD_RING_BRIGHT, (jx, m(200)), (jx, m(206)), max(2, m(3)))


def hero(big, sid, pal):
    cx, cy, r = m(CX), m(DISC_CY), m(DISC_R)
    _alpha_aura(big, m(CX), m(155), m(30), pal["glow"], peak=25, layers=10)
    sc.cabochon(big, cx, cy, r, CABO_LO, CABO_HI, ring=pal["gem"], ring_a=50)
    try: sc.blit_thumb(big, sid, cx, cy, int(r * 1.5))
    except Exception: pygame.draw.circle(big, pal["gem"], (cx, cy), int(r * 0.7))
    sc.cabochon_glass(big, cx, cy, r, tint=pal["gem"])
    # Keystone gem caps the niche at the crown of the portrait bezel — the true
    # arch apex sits under the disc, so the visible crown is where it belongs.
    facet_gem(big, m(CX), m(80), m(8), pal["gem"], pal["deep"])


def nameplate(big, name):
    plain_text(big, name, font(18), (m(CX), m(213)), INK, shadow_a=70, weight=m(0.8))


def price_ledger(big):
    r = pygame.Rect(0, 0, m(160), m(26)); r.center = (m(CX), m(ZA_CY))
    sc.chip_body_stops(big, r, m(10), LEDGER_STOPS, LEDGER_RIM_D, LEDGER_RIM_B, gloss=90)
    coin_glyph(big, m(CX - 44), m(ZA_CY), m(11))
    plain_text(big, PRICE, font(19), (m(CX + 22), m(ZA_CY)), (40, 25, 10),
               shadow_a=0, weight=m(0.7))


def buttons(big):
    buy = pygame.Rect(0, 0, m(BTN_W), m(BTN_H)); buy.center = (m(BUY_CX), m(BTN_CY))
    sc.chip_body_stops(big, buy, m(BTN_RAD),
                       [(0.0, (232, 190, 90)), (0.5, (206, 160, 64)), (1.0, (150, 104, 28))],
                       (100, 66, 14), (255, 236, 170), gloss=120)
    plain_text(big, "BUY", font(14), buy.center, (58, 36, 12), shadow_a=0, weight=m(0.9))
    can = pygame.Rect(0, 0, m(BTN_W), m(BTN_H)); can.center = (m(CAN_CX), m(BTN_CY))
    sc.chip_body_stops(big, can, m(BTN_RAD),
                       [(0.0, (210, 196, 166)), (1.0, (176, 160, 128))],
                       (120, 104, 72), (238, 226, 196), gloss=60)
    plain_text(big, "CANCEL", font(13), can.center, (86, 66, 40), shadow_a=0, weight=m(0.8))


def wax_seal_footer(big, tier_word, pal):
    zb = OXBLOOD if tier_word == "LEGENDARY" else pal
    for gx in (m(BOT_GEM_L_X), m(BOT_GEM_R_X)):
        _alpha_aura(big, gx, m(ZB_CY), m(16), zb["glow"], peak=60, layers=14)
    sc._ribbon_lozenge(big, tier_word, m(CX), m(ZB_CY), m(146), zb)
    for gx in (m(BOT_GEM_L_X), m(BOT_GEM_R_X)):
        facet_gem(big, gx, m(ZB_CY), m(GEM_R), zb["gem"], zb["deep"])


def render_popup(tier_word, pal):
    sid, name = HERO[tier_word]
    big = pygame.Surface((POP_W * SS, POP_H * SS), pygame.SRCALPHA)
    codex_body(big)
    gothic_arch(big)
    hero(big, sid, pal)
    nameplate(big, name)
    price_ledger(big)
    buttons(big)
    wax_seal_footer(big, tier_word, pal)
    return pygame.transform.smoothscale(big, (POP_W, POP_H))


MARGIN, HEAD, GAP = 20, 58, 12
STRIP_W = MARGIN * 2 + len(TIERS) * (POP_W + GAP) - GAP
STRIP_H = HEAD + POP_H + MARGIN
strip = Image.new("RGB", (STRIP_W, STRIP_H), (26, 22, 16))
idr = ImageDraw.Draw(strip)
idr.text((MARGIN, 18), "gilt-codex · card-frame-v1 · round_1", fill=(236, 220, 176))
for i, (tw, pal) in enumerate(TIERS):
    pop = render_popup(tw, pal)
    pil = Image.frombytes("RGB", (POP_W, POP_H), pygame.image.tostring(pop, "RGB"))
    x = MARGIN + i * (POP_W + GAP); strip.paste(pil, (x, HEAD))
    idr.text((x + POP_W // 2, HEAD + POP_H + 6), tw, fill=(206, 190, 150), anchor="mt")
out = strip.resize((STRIP_W * 2, STRIP_H * 2), Image.LANCZOS)
import pathlib
OUTDIR = "/home/user/skybit/docs/confirm_purchase_v8/card-frame-v1/gilt-codex"
pathlib.Path(OUTDIR).mkdir(parents=True, exist_ok=True)
OUT = OUTDIR + "/round_1.png"
out.save(OUT); print(f"saved {out.size[0]}x{out.size[1]}  ->  {OUT}")
