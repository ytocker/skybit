#!/usr/bin/env python3
"""obsidian-forge · confirm_purchase_v8 · premium-v1 · round_1

Brutalist machined luxury — premium by restraint. The shipping confirm popup's
STRUCTURE and POSITIONS are untouched; this only upgrades the materials/finishes:
a bright bullion-bar price chip with countersunk bolt dots, a forge-iron brushed
card body, one crisp machined chamfer ring on the hero, a single dead-zone score
line, and a dark gunmetal LEGENDARY banner that contrasts the bright gold Zone A
(bright gold vs dark gunmetal = two different metal families).
"""
import os, sys, math
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame
pygame.init()
pygame.display.set_mode((1, 1))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import game.store_cards as sc


# The bullion price chip is a BRIGHT body, so the standard additive gloss is
# safe here — but the mandated patch keeps the BLEND_ADD amount on-curve so no
# body it touches is ever blown to white.
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

from game.store_cards import (
    m, SS, font, vgrad_stops, plain_text, coin_glyph, cabochon, cabochon_glass,
    facet_gem, _alpha_aura, _ribbon_lozenge, chip_body_stops, drop_shadow,
    top_sheen, bevel_rim, blit_thumb, _glyph_base, _stamp_bold,
    CARD_T, CARD_B, CABO_LO, CABO_HI, CARD_RING_BRIGHT, CARD_RING_DEEP,
    GOLD_A_STOPS, GOLD_A_RIM_DARK, GOLD_A_RIM_BRIGHT, GOLD_A_NUM)
from PIL import Image, ImageDraw


# ── locked layout (logical px; everything flows through m()) ───────────────────
POP_W, POP_H = 260, 442
CX = 130
CARD_X, CARD_TOP, CARD_W, CARD_H, CARD_RAD = 10, 127, 240, 299, 23
R_HERO, DISC_CY = 53, 135
GEM_R, GEM_CY, GEM_L_X, GEM_R_X = 14, 152, 43, 217
NAME_FS, Y_NAME = 45, 213
CHIP_CY = 247
SHELF_X, SHELF_Y, SHELF_W, SHELF_H = 17, 335, 226, 91
BTN_W, BTN_H, BTN_RAD, BTN_CY, BTN_GAP = 99, 31, 12, 360, 10
Y_BANNER, BOT_GEM_CY = 402, 402
BUY_CX = CX - (BTN_W + BTN_GAP) // 2
CAN_CX = CX + (BTN_W + BTN_GAP) // 2

PALETTES = {
    "RARE":      {"gem": (108, 188, 252), "deep": (28, 60, 120), "glow": (160, 210, 255)},
    "EPIC":      {"gem": (194, 122, 248), "deep": (72, 28, 120), "glow": (230, 160, 255)},
    "LEGENDARY": {"gem": (255, 202, 104), "deep": (120, 72, 12), "glow": (255, 230, 140)},
}
# Dark forged-iron banner for LEGENDARY: pushes Zone B into the gunmetal/steel
# family so it never collapses into the bright bullion gold Zone A already owns.
LEGENDARY_BANNER = {"gem": (96, 110, 128), "deep": (30, 36, 48), "glow": (140, 158, 180)}

HERO = {"RARE": ("skin_wizard", "WIZARD"),
        "EPIC": ("skin_prism", "PRISM"),
        "LEGENDARY": ("skin_astronaut", "ASTRONAUT")}
PRICE = {"RARE": 720, "EPIC": 1400, "LEGENDARY": 2600}


# ── card body + forge-iron brushing ────────────────────────────────────────────
def card_body(big):
    rect = pygame.Rect(m(CARD_X), m(CARD_TOP), m(CARD_W), m(CARD_H))
    rad = m(CARD_RAD)
    drop_shadow(big, rect, rad, blur=m(8), alpha=165, dy=m(4))
    big.blit(vgrad_stops(rect.w, rect.h, rad,
                         [(0.0, CARD_T), (1.0, CARD_B)], 255, gamma=1.15),
             rect.topleft)
    _forge_grain(big, rect, rad)
    top_sheen(big, rect, rad, m(30), peak=56)
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 230),
              w=max(1, m(1.9)))
    tray = rect.inflate(-m(8), -m(8))
    pygame.draw.rect(big, (*CARD_RING_BRIGHT, 55), tray,
                     width=max(1, m(1)), border_radius=rad - m(3))


def _forge_grain(big, rect, rad):
    """Directional brushed forge-iron: a few dozen horizontal passes in CARD_T
    ±6 tone at low alpha, authored ≥8 px apart (SS=2) so the grain reads as a
    machined finish, not noise. Clipped to the card's rounded interior."""
    grain = pygame.Surface(rect.size, pygame.SRCALPHA)
    hi = (CARD_T[0] + 6, CARD_T[1] + 6, CARD_T[2] + 6)
    lo = (max(0, CARD_T[0] - 6), max(0, CARD_T[1] - 6), max(0, CARD_T[2] - 6))
    pitch = m(4)  # 8 device px between lines
    for i, y in enumerate(range(m(2), rect.h - m(2), pitch)):
        col = hi if i % 2 == 0 else lo
        pygame.draw.line(grain, (*col, 22), (m(3), y), (rect.w - m(3), y), max(1, m(0.5)))
    mask = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=rad)
    grain.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(grain, rect.topleft)


# ── name plate ─────────────────────────────────────────────────────────────────
def name_text(big, name):
    fs, nf = NAME_FS, font(NAME_FS)
    mw = m(CARD_W - 20)
    while _glyph_base(name, nf, 0).get_width() > mw and fs > 24:
        fs -= 1
        nf = font(fs)
    plain_text(big, name, nf, (m(CX), m(Y_NAME)), (250, 248, 240),
               shadow_a=160, weight=m(0.9), keyline=(6, 6, 16), kw=m(1.0))


# ── Zone A: bright bullion-bar price chip ──────────────────────────────────────
def zone_a(big, price):
    """A bright bullion bar carrying the coin + numeral inline, flanked by two
    countersunk bolt dots that read as machined holes (not specks) — the one
    ornament restraint allows here."""
    txt = f"{price:,}"
    r = pygame.Rect(0, 0, m(168), m(28))
    r.center = (m(CX), m(CHIP_CY))
    chip_body_stops(big, r, m(11), GOLD_A_STOPS, GOLD_A_RIM_DARK,
                    GOLD_A_RIM_BRIGHT, gloss=120)

    num_font = font(18)
    base = _stamp_bold(_glyph_base(txt, num_font, 0), m(0.7))
    bw, bh = base.get_size()
    coin_d, gap = m(22), m(5)
    group_w = coin_d + gap + bw
    left = m(CX) - group_w // 2
    coin_cx = left + coin_d // 2
    num_left = left + coin_d + gap
    coin_glyph(big, coin_cx, m(CHIP_CY), m(11))
    plain_text(big, txt, num_font, (num_left + bw // 2, m(CHIP_CY)), GOLD_A_NUM,
               shadow_a=0, weight=m(0.7))

    for bx in (r.left + m(13), r.right - m(13)):
        _bolt_dot(big, bx, m(CHIP_CY))


def _bolt_dot(big, bx, by):
    """Countersunk machined hole: a dark sunk disc (≥4 px at SS=2) inside a
    thin warm ring so it reads as a bolted hole in the bar, not a stray speck."""
    pygame.draw.circle(big, (60, 42, 12), (bx, by), m(2))
    ring = pygame.Surface((m(6), m(6)), pygame.SRCALPHA)
    pygame.draw.circle(ring, (180, 140, 60, 120), (m(3), m(3)), m(2), max(1, m(0.6)))
    big.blit(ring, (bx - m(3), by - m(3)))


# ── dead-zone score line ───────────────────────────────────────────────────────
def dead_zone_score(big):
    """One faint machined score line centred in the ~76 px void between the price
    chip and the shelf. Restraint is the thesis — a single hairline, nothing more.
    (22,24,56) is the brief-specified deep score ink for this brutalist body.)"""
    band_cy = (259 + 335) // 2
    line = pygame.Surface((POP_W * SS, POP_H * SS), pygame.SRCALPHA)
    pygame.draw.line(line, (22, 24, 56, 24), (m(30), m(band_cy)),
                     (m(230), m(band_cy)), max(1, m(0.5)))
    big.blit(line, (0, 0))


# ── shelf ──────────────────────────────────────────────────────────────────────
def shelf(big):
    rect = pygame.Rect(m(SHELF_X), m(SHELF_Y), m(SHELF_W), m(SHELF_H))
    rad = m(CARD_RAD)
    stops = [(0.0, (34, 36, 72)), (0.5, (22, 24, 54)), (1.0, (12, 14, 36))]
    face = vgrad_stops(rect.w, rect.h, 0, stops, 255).copy()
    smask = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(smask, (255, 255, 255, 255), smask.get_rect(),
                     border_bottom_left_radius=rad, border_bottom_right_radius=rad)
    face.blit(smask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    top_sheen(face, face.get_rect(), 0, m(20), peak=35)
    pygame.draw.line(face, (115, 106, 140), (0, 0), (rect.w - 1, 0), max(1, m(1)))
    seat = pygame.Surface((rect.w, m(6)), pygame.SRCALPHA)
    for yy in range(m(6)):
        a = int(120 * (1 - yy / m(6)))
        pygame.draw.line(seat, (0, 0, 0, a), (0, yy), (rect.w - 1, yy))
    big.blit(seat, (rect.x, rect.y - m(6)))
    big.blit(face, rect.topleft)
    # recessed side walls between the card edge and the shelf lip
    wall_h = m(CARD_TOP + CARD_H - CARD_RAD - SHELF_Y)
    if wall_h > 0:
        wall_w = m(SHELF_X - CARD_X)
        for col_fn, bx in [
            (lambda xx: (130, 120, 165, int(50 * xx / max(1, wall_w - 1))), m(CARD_X)),
            (lambda xx: (0, 0, 0, int(50 * (1 - xx / max(1, wall_w - 1)))), m(SHELF_X + SHELF_W)),
        ]:
            wall = pygame.Surface((wall_w, wall_h), pygame.SRCALPHA)
            for xx in range(wall_w):
                pygame.draw.line(wall, col_fn(xx), (xx, 0), (xx, wall_h - 1))
            big.blit(wall, (bx, m(SHELF_Y)))


# ── buttons ────────────────────────────────────────────────────────────────────
def buttons(big):
    br = m(BTN_RAD)
    for cx_b, lbl, stops, lab_c, sheen, is_cancel in [
        (m(BUY_CX), "BUY", [(0.0, (38, 40, 84)), (1.0, (22, 24, 56))], (200, 205, 240), 22, False),
        (m(CAN_CX), "CANCEL", [(0.0, (26, 28, 64)), (1.0, (14, 16, 44))], (150, 155, 200), 14, True),
    ]:
        r = pygame.Rect(0, 0, m(BTN_W), m(BTN_H))
        r.center = (cx_b, m(BTN_CY))
        drop_shadow(big, r, br, blur=m(3), alpha=100, dy=m(2))
        big.blit(vgrad_stops(r.w, r.h, br, stops, 255), r.topleft)
        top_sheen(big, r, br, m(12), peak=sheen)
        rim_w = m(2.2) if is_cancel else m(2.0)
        bevel_rim(big, r, br, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 230), w=max(1, rim_w))
        plain_text(big, lbl, font(13 if is_cancel else 14), r.center, lab_c,
                   shadow_a=110, weight=m(0.8), keyline=(8, 6, 20), kw=m(0.9))


# ── gems + Zone B banner ───────────────────────────────────────────────────────
def top_gems(big, pal):
    facet_gem(big, m(GEM_L_X), m(GEM_CY), m(GEM_R), pal["gem"], pal["deep"])
    facet_gem(big, m(GEM_R_X), m(GEM_CY), m(GEM_R), pal["gem"], pal["deep"])


def zone_b(big, tier_word, pal):
    for gx in (m(GEM_L_X), m(GEM_R_X)):
        _alpha_aura(big, gx, m(BOT_GEM_CY), m(16), pal["glow"], peak=60, layers=14)
        facet_gem(big, gx, m(BOT_GEM_CY), m(GEM_R), pal["gem"], pal["deep"])
    banner_pal = LEGENDARY_BANNER if tier_word == "LEGENDARY" else pal
    _ribbon_lozenge(big, tier_word, m(CX), m(Y_BANNER), m(146), banner_pal)


# ── hero ───────────────────────────────────────────────────────────────────────
def hero(big, sid, pal):
    """Restraint hero: dome + skin under glass, then ONE crisp machined chamfer
    ring at the rim. Nothing else is stacked here — no spotlight halo."""
    cx, cy, r = m(CX), m(DISC_CY), m(R_HERO)
    cabochon(big, cx, cy, r, CABO_LO, CABO_HI, ring=pal["gem"], ring_a=50)
    try:
        blit_thumb(big, sid, cx, cy, int(r * 1.5))
    except Exception:
        pygame.draw.circle(big, pal["gem"], (cx, cy), int(r * 0.7))
    cabochon_glass(big, cx, cy, r, tint=pal["gem"])
    ring = pygame.Surface((r * 2 + m(4), r * 2 + m(4)), pygame.SRCALPHA)
    c = r + m(2)
    pygame.draw.circle(ring, (*pal["gem"], 150), (c, c), r, max(1, m(1)))
    big.blit(ring, (cx - c, cy - c))


# ── render one popup ───────────────────────────────────────────────────────────
def render_popup(tier_word):
    pal = PALETTES[tier_word]
    sid, name = HERO[tier_word]
    big = pygame.Surface((POP_W * SS, POP_H * SS), pygame.SRCALPHA)
    card_body(big)
    top_gems(big, pal)
    name_text(big, name)
    zone_a(big, PRICE[tier_word])
    dead_zone_score(big)
    shelf(big)
    buttons(big)
    zone_b(big, tier_word, pal)
    hero(big, sid, pal)
    return pygame.transform.smoothscale(big, (POP_W, POP_H))


# ── strip ──────────────────────────────────────────────────────────────────────
MARGIN, HEAD, GAP = 20, 58, 12
TIERS = ["RARE", "EPIC", "LEGENDARY"]
canvas_w = MARGIN * 2 + POP_W * 3 + GAP * 2
canvas_h = HEAD + POP_H + MARGIN
strip = Image.new("RGB", (canvas_w, canvas_h), (8, 8, 20))
idr = ImageDraw.Draw(strip)
idr.text((MARGIN, 18), "obsidian-forge  ·  confirm_purchase_v8  ·  premium-v1  ·  round_1",
         fill=(232, 226, 208))
for i, tw in enumerate(TIERS):
    pop = render_popup(tw)
    pil = Image.frombytes("RGB", (POP_W, POP_H), pygame.image.tostring(pop, "RGB"))
    x = MARGIN + i * (POP_W + GAP)
    idr.text((x + POP_W // 2, 40), tw, fill=(180, 176, 210), anchor="mm")
    strip.paste(pil, (x, HEAD))
out = strip.resize((canvas_w * 2, canvas_h * 2), Image.LANCZOS)

import pathlib
OUTDIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                      "docs/confirm_purchase_v8/premium-v1/obsidian-forge")
pathlib.Path(OUTDIR).mkdir(parents=True, exist_ok=True)
OUT = os.path.join(OUTDIR, "round_1.png")
out.save(OUT)
print(f"saved {out.size[0]}x{out.size[1]}  ->  {OUT}")
