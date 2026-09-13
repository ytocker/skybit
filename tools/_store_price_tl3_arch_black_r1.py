"""arch-black tl3 hang-tag concept — round 1 render (obsidian arch-top boutique tag).

Standalone review harness: monkey-patches store_cards.price_chip with the
arch-black tag, renders mummy/kitsune cards in affordable + locked states, and
tiles them into docs/store_price_tl3/arch_black/round_1.png. Not wired into the
live store — exploration only.
"""
import os, sys, math
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, "/home/user/skybit")
import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)
import game.store_cards as sc
import game.store_data as sd
from game.draw import lerp_color, WHITE, NEAR_BLACK
from game.hud import _font as hud_font
sd.load()


def _abbr(text):
    digits = ''.join(c for c in text if c.isdigit())
    if not digits:
        return text
    v = int(digits)
    if v >= 1000:
        frac = (v % 1000) // 100
        return f"{v//1000}.{frac}k" if frac else f"{v//1000}k"
    return str(v)


def coin_ring(surf, cx, cy):
    r = sc.m(5)
    s = pygame.Surface((r*2+2, r*2+2), pygame.SRCALPHA)
    cc = (r+1, r+1)
    pygame.draw.circle(s, (156, 116, 58), cc, r)
    pygame.draw.circle(s, (48, 28, 10), cc, r, 1)
    pygame.draw.circle(s, (0, 0, 0, 0), cc, sc.m(3)+1)
    surf.blit(s, (cx-r-1, cy-r-1))


def my_price_chip(surf, cx, cy, text, h, variant=sc.PRICE_VARIANT, **kw):
    # affordability is driven by variant here so the review sheet can force a
    # locked take regardless of the (zero) fixture wallet.
    affordable = (variant != "locked")
    text = _abbr(text)

    FACE_W = 74
    FACE_H = 78
    ARCH_R = 37  # semicircle radius = FACE_W // 2

    if affordable:
        grad_top, grad_bot = (38, 36, 42), (22, 20, 26)
        hair = (210, 190, 150, 170)          # champagne edge hairline
        price_col = (242, 224, 178)
        steel, steel_ul, steel_lr = (150, 158, 166), (190, 198, 204), (60, 68, 76)
        base_shadow = (200, 180, 130, 80)
    else:
        grad_top, grad_bot = (34, 34, 38), (24, 24, 28)
        hair = (90, 90, 96, 120)
        price_col = (140, 140, 146)
        # steel kept, brightness dropped ~20 so the locked tag reads inert.
        steel, steel_ul, steel_lr = (130, 138, 146), (170, 178, 184), (40, 48, 56)
        base_shadow = (200, 180, 130, 60)

    face = pygame.Surface((FACE_W, FACE_H), pygame.SRCALPHA)

    # ── near-black arch fill: 2-stop vertical gradient masked to the tombstone
    # silhouette (semicircle crown atop a flat-bottom rect). The faint 2-stop
    # cast reads as depth on an otherwise matte obsidian slab.
    grad = pygame.Surface((FACE_W, FACE_H), pygame.SRCALPHA)
    for y in range(FACE_H):
        t = y / (FACE_H - 1)
        grad.fill(lerp_color(grad_top, grad_bot, t), (0, y, FACE_W, 1))
    mask = pygame.Surface((FACE_W, FACE_H), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), (ARCH_R, ARCH_R), ARCH_R)
    pygame.draw.rect(mask, (255, 255, 255, 255),
                     (0, ARCH_R, FACE_W, FACE_H - ARCH_R),
                     border_bottom_left_radius=sc.m(4),
                     border_bottom_right_radius=sc.m(4))
    grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    face.blit(grad, (0, 0))

    # ── inner debossed border at 4dp inset, barely lighter than the body so it
    # reads as a pressed lip rather than a drawn line.
    deb = (50, 48, 56)
    inset = sc.m(2)  # 4dp
    pygame.draw.arc(face, deb, (inset, inset, FACE_W-2*inset, FACE_W-2*inset),
                    0, math.pi, 1)
    pygame.draw.line(face, deb, (inset, ARCH_R), (inset, FACE_H-1-inset), 1)
    pygame.draw.line(face, deb, (FACE_W-1-inset, ARCH_R),
                     (FACE_W-1-inset, FACE_H-1-inset), 1)
    pygame.draw.line(face, deb, (inset, FACE_H-1-inset),
                     (FACE_W-1-inset, FACE_H-1-inset), 1)

    # ── FLOURISH A: champagne edge hairline hugging the arch silhouette. Drawn
    # on an alpha overlay so the translucent stroke blends onto the face rather
    # than punching holes (pygame.draw replaces, it does not blend).
    hl = pygame.Surface((FACE_W, FACE_H), pygame.SRCALPHA)
    pygame.draw.arc(hl, hair, (0, 0, FACE_W, FACE_W), 0, math.pi, 1)
    pygame.draw.line(hl, hair, (0, ARCH_R), (0, FACE_H-1), 1)
    pygame.draw.line(hl, hair, (FACE_W-1, ARCH_R), (FACE_W-1, FACE_H-1), 1)
    pygame.draw.line(hl, hair, (0, FACE_H-2), (FACE_W-1, FACE_H-2), 1)
    face.blit(hl, (0, 0))

    # ── grommet (steel) centred in the arch crown; the void is a real punched
    # hole so the boutique tag reads as physically hung.
    gx, gy = ARCH_R, 14
    outer_r = sc.m(4)+1
    pygame.draw.circle(face, steel, (gx, gy), outer_r)
    aw = max(1, sc.m(1))
    pygame.draw.arc(face, steel_ul, (gx-outer_r, gy-outer_r, outer_r*2, outer_r*2),
                    math.pi/2, math.pi, aw)
    pygame.draw.arc(face, steel_lr, (gx-outer_r, gy-outer_r, outer_r*2, outer_r*2),
                    3*math.pi/2, 2*math.pi, aw)
    pygame.draw.circle(face, (40, 30, 18), (gx, gy), sc.m(3))
    pygame.draw.circle(face, (0, 0, 0, 0), (gx, gy), sc.m(2))

    # ── FLOURISH B: bronze coin ring in the lower crown, byte-identical family
    # unifier. Sits below the grommet, above the price band — no overlap.
    coin_ring(face, ARCH_R, 33)

    # ── price: champagne numeral centred in the rect body with a near-black
    # keyline that bakes to a crisp dark border on the obsidian ground.
    size = 12.0
    f = sc.font(size)
    while (sc._glyph_base(text, f, 0).get_width() > 60 or f.get_height() > 18) \
            and size > 6:
        size -= 0.5
        f = sc.font(size)
    r = sc.plain_text(face, text, f, (ARCH_R, 54), price_col,
                      shadow_a=0, weight=sc.m(1.0), keyline=(12, 10, 14), kw=1)

    # champagne baseline shadow so the numerals sit ON a surface, not float.
    bl = pygame.Surface((FACE_W, FACE_H), pygame.SRCALPHA)
    pygame.draw.line(bl, base_shadow, (r.left, r.bottom+1), (r.right, r.bottom+1), 1)
    face.blit(bl, (0, 0))

    # ── boutique tag hangs in the top-left clear zone of the 2x buffer.
    surf.blit(face, (48 - FACE_W // 2, 50 - FACE_H // 2))
    return pygame.Rect(48 - FACE_W // 2, 50 - FACE_H // 2, FACE_W, FACE_H)


sc.price_chip = my_price_chip


def render_card_1x(sid, variant):
    big = pygame.Surface((sc.CARD_W * sc.SS, sc.CARD_H * sc.SS), pygame.SRCALPHA)
    inset = sc.m(sc._INSET)
    rect = pygame.Rect(inset, inset,
                       sc.CARD_W * sc.SS - 2*inset,
                       sc.CARD_H * sc.SS - 2*inset)
    sc.draw_card(big, sid, rect, equipped=False, secret=False, variant=variant)
    return pygame.transform.smoothscale(big, (sc.CARD_W, sc.CARD_H))


def zoom_left(card_1x):
    crop = card_1x.subsurface((0, 0, 80, 100))
    return pygame.transform.scale(crop, (160, 200))


BG = (8, 8, 20)
PAD = 20
GAP = 12
HDR_H = 40
LABEL_H = 20
CW, CH = sc.CARD_W, sc.CARD_H

cards = {
    "mummy_aff":   render_card_1x("skin_mummy",   sc.PRICE_VARIANT),
    "mummy_lck":   render_card_1x("skin_mummy",   "locked"),
    "kitsune_aff": render_card_1x("skin_kitsune", sc.PRICE_VARIANT),
    "kitsune_lck": render_card_1x("skin_kitsune", "locked"),
}

row1_h = CH
row2_h = 200
total_w = PAD + 4*CW + 3*GAP + PAD
total_h = HDR_H + LABEL_H + row1_h + GAP + row2_h + PAD
canvas = pygame.Surface((total_w, total_h))
canvas.fill(BG)

hf = hud_font(9, True)
ht = hf.render("arch-black · tl3 hang-tag · round 1", True, (255, 220, 80))
canvas.blit(ht, (total_w//2 - ht.get_width()//2, (HDR_H-ht.get_height())//2))

lf = hud_font(7)
card_list = [cards["mummy_aff"], cards["mummy_lck"], cards["kitsune_aff"], cards["kitsune_lck"]]
labels = ["mummy aff", "mummy lck", "kitsune aff", "kitsune lck"]
y1 = HDR_H + LABEL_H
for i, (card, label) in enumerate(zip(card_list, labels)):
    x = PAD + i*(CW+GAP)
    lbl = lf.render(label, True, (160, 156, 180))
    canvas.blit(lbl, (x, HDR_H + (LABEL_H-lbl.get_height())//2))
    canvas.blit(card, (x, y1))

y2 = y1 + row1_h + GAP
for i, (key, label) in enumerate([("mummy_aff", "mummy aff (2×crop)"), ("mummy_lck", "mummy lck (2×crop)")]):
    x = PAD + i*(160+GAP)
    lbl = lf.render(label, True, (140, 136, 160))
    canvas.blit(lbl, (x, y2 - lf.get_height() - 2))
    canvas.blit(zoom_left(cards[key]), (x, y2))

out = "docs/store_price_tl3/arch_black/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(canvas, out)
print(f"saved {canvas.get_width()}x{canvas.get_height()} -> {out}")
