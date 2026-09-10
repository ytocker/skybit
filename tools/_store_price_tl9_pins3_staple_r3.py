"""Round-3 render for tl9 pins3: staple (⊓-shape bridge + crimped tips)"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import sys
sys.path.insert(0, "/home/user/skybit")
import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)
import game.store_cards as sc
import game.store_data as sd
from game.hud import _font as hud_font
sd.load()

FACE_W, FACE_H = 76, 88
TILT = -7

def _full(text):
    digits = ''.join(c for c in text if c.isdigit())
    return str(int(digits)) if digits else text

def _price_glyph(text):
    for fs in (15, 14, 13, 12, 11, 10, 9, 8):
        raw = sc._stamp_bold(sc._glyph_base(text, sc.font(fs), 0), sc.m(1.0))
        crushed = pygame.transform.smoothscale(raw, (max(1, int(raw.get_width() * 0.86)), raw.get_height()))
        if crushed.get_width() <= 66:
            return crushed
    return crushed

def _draw_price(face, text, affordable):
    ink = (40, 30, 26) if affordable else (40, 40, 52)
    rule_col = (56, 42, 30) if affordable else (40, 40, 52)
    amt_mask = _price_glyph(text)
    cy_amount = int(FACE_H * 0.52)
    amt_r = amt_mask.get_rect(center=(FACE_W // 2, cy_amount))
    amt_fill = amt_mask.copy()
    amt_fill.fill((*ink, 255), special_flags=pygame.BLEND_RGBA_MULT)
    face.blit(amt_fill, amt_r)
    rule_y = cy_amount + amt_mask.get_height() // 2 + sc.m(2)
    rule_w = min(amt_mask.get_width() + sc.m(4), FACE_W - sc.m(8))
    rule_x = FACE_W // 2 - rule_w // 2
    peak_h = max(3, sc.m(3))
    min_h = max(1, sc.m(1))
    pygame.draw.polygon(face, rule_col, [
        (rule_x, rule_y), (rule_x + rule_w, rule_y + (peak_h - min_h) // 2),
        (rule_x + rule_w, rule_y + (peak_h + min_h) // 2), (rule_x, rule_y + peak_h),
    ])

def _attachment(card, affordable):
    if affordable:
        shadow = (108, 124, 134)
        mid    = (168, 189, 198)
        hi     = (214, 226, 230)
    else:
        shadow = (76,  78,  86)    # pushed darker for clearer state contrast
        mid    = (118, 120, 128)
        hi     = (164, 166, 174)
    kl = (24, 26, 34)

    # crown — draw order: kl base → shadow underside → mid face → hi TOP LAST
    pygame.draw.line(card, kl,     (6,  6), (22,  6), 4)   # kl (trim from 5 to 4)
    pygame.draw.line(card, shadow, (6,  9), (22,  9), 1)   # underside shadow
    pygame.draw.line(card, mid,    (6,  7), (22,  7), 2)   # mid face (y7 only — not y6)
    pygame.draw.line(card, hi,     (6,  6), (22,  6), 1)   # highlight ON TOP at y6 ← LAST

    # left leg — outer face hi at top, mid main, inner shadow
    pygame.draw.line(card, kl,    (7,  8), (7,  21), 4)
    pygame.draw.line(card, mid,   (7,  8), (7,  21), 2)
    pygame.draw.line(card, shadow,(8,  9), (8,  20), 1)    # inner face shadow
    pygame.draw.line(card, hi,    (6,  8), (6,  11), 1)    # outer-top specular tick

    # right leg
    pygame.draw.line(card, kl,    (21,  8), (21, 21), 4)
    pygame.draw.line(card, mid,   (21,  8), (21, 21), 2)
    pygame.draw.line(card, shadow,(20,  9), (20, 20), 1)   # inner face shadow
    pygame.draw.line(card, hi,    (22,  8), (22, 11), 1)   # outer-top specular tick

    # crimped tips bent inward
    pygame.draw.line(card, kl,  (7,  21), (12, 23), 3)
    pygame.draw.line(card, mid, (7,  21), (12, 23), 2)
    pygame.draw.line(card, kl,  (21, 21), (16, 23), 3)
    pygame.draw.line(card, mid, (21, 21), (16, 23), 2)

def my_price_chip(surf, cx, cy, text, h, variant=sc.PRICE_VARIANT, **kw):
    affordable = (variant != "locked")
    text = _full(text)
    rad = sc.m(3)
    face = pygame.Surface((FACE_W, FACE_H), pygame.SRCALPHA)
    brect = pygame.Rect(0, 0, FACE_W, FACE_H)
    if affordable:
        body = sc.vgrad_stops(FACE_W, FACE_H, rad, [(0.0, (248, 238, 210)), (1.0, (224, 204, 166))], 255, gamma=1.04)
        face.blit(body, (0, 0))
        sc.bevel_rim(face, brect, rad, (80, 52, 12, 200), (255, 240, 190, 200), w=max(1, sc.m(1.2)))
    else:
        body = sc.vgrad_stops(FACE_W, FACE_H, rad, [(0.0, (156, 160, 176)), (1.0, (88, 92, 112))], 255, gamma=1.02)
        face.blit(body, (0, 0))
        sc.bevel_rim(face, brect, rad, (54, 58, 74, 200), (214, 218, 232, 200), w=max(1, sc.m(1.2)))
    _draw_price(face, text, affordable)
    rot = pygame.transform.rotate(face, TILT)
    surf.blit(rot, rot.get_rect(center=(44, 60)))

sc.price_chip = my_price_chip

def render_card_1x(sid, affordable=True):
    variant = sc.PRICE_VARIANT if affordable else "locked"
    big = pygame.Surface((sc.CARD_W * sc.SS, sc.CARD_H * sc.SS), pygame.SRCALPHA)
    inset = sc.m(sc._INSET)
    rect = pygame.Rect(inset, inset, sc.CARD_W * sc.SS - 2 * inset, sc.CARD_H * sc.SS - 2 * inset)
    sc.draw_card(big, sid, rect, equipped=False, secret=False, variant=variant)
    card = pygame.transform.smoothscale(big, (sc.CARD_W, sc.CARD_H))
    _attachment(card, affordable)
    return card

SLUG = "staple"
skins = [("skin_mummy", True), ("skin_mummy", False), ("skin_kitsune", True), ("skin_kitsune", False)]
cards = [render_card_1x(sid, aff) for sid, aff in skins]
labels = ["mummy aff", "mummy lock", "kitsune aff", "kitsune lock"]

PAD, GAP, HEADER_H, LABEL_H = 20, 12, 40, 20
CW, CH = sc.CARD_W, sc.CARD_H
sheet_w = PAD + len(cards) * CW + (len(cards) - 1) * GAP + PAD
sheet_h = PAD + HEADER_H + CH + GAP + LABEL_H + 100 * 2 + GAP + PAD
BG = (8, 8, 20)
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)

fh = hud_font(18)
fl = hud_font(12)
title = fh.render(f"tl9 pins3: {SLUG} — round 3", True, (240, 224, 180))
sheet.blit(title, (PAD, PAD // 2))

y = PAD + HEADER_H
x = PAD
for i, card in enumerate(cards):
    sheet.blit(card, (x, y))
    lbl = fl.render(labels[i], True, (190, 196, 210))
    sheet.blit(lbl, (x, y + CH + 4))
    x += CW + GAP

y += CH + GAP + LABEL_H
for i in range(2):
    cx = PAD + i * (80 * 2 + GAP)
    crop = cards[i].subsurface(pygame.Rect(0, 0, 80, 100))
    zoomed = pygame.transform.smoothscale(crop, (80 * 2, 100 * 2))
    sheet.blit(zoomed, (cx, y))

aff_card = cards[0]
lock_card = cards[1]
found_dark = False
for px in range(14, 42):
    for py in range(22, 44):
        r, g, b, *_ = aff_card.get_at((px, py))
        if r < 100 and g < 100 and b < 100:
            print(f"dark numeral at ({px},{py}) = ({r},{g},{b})")
            found_dark = True
            break
    if found_dark:
        break
assert found_dark, "no dark numeral pixel found in aff card tag zone"

aff_px = aff_card.get_at((20, 35))[:3]
lock_px = lock_card.get_at((20, 35))[:3]
print(f"aff:{aff_px} lock:{lock_px} PASS")
assert aff_px != lock_px, "aff/lock cards look identical"

out = f"docs/store_price_tl9_pins3/{SLUG}/round_3.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print(f"saved {sheet_w}x{sheet_h} -> {out}")
