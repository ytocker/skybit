"""Round-1 render for the `double-tag` store-card price tag (tier-3 line).

A layered dual-card swing tag: a large dark bronze FRONT card carries the
price and a brass grommet, while a small warm-cream BACK accent card — bearing
only a coin ring — peeks out from behind the front card's top-right corner,
tilted a few degrees off-axis. A hard (unblurred) 40%-alpha cast shadow drops
the front card off the back one so the pair reads as stacked depth rather than
clutter. A twisted two-strand cord dives into the shared grommet and runs off
the top of the clear zone.

Review sheet only — nothing here is wired into the live store draw path.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import sys
sys.path.insert(0, "/home/user/skybit")

import math
import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

import game.store_cards as sc
import game.store_data as sd
from game.draw import lerp_color, WHITE, NEAR_BLACK
from game.hud import _font as hud_font

sd.load()


# ── geometry (device px in the 2x card buffer) ────────────────────────────────
FACE_W, FACE_H = 66, 74
FRONT_RAD = sc.m(5)                       # 10dp rounded front card
BACK_W, BACK_H = 34, 34
BACK_RAD = sc.m(4)                        # 8dp rounded back accent card
FRONT_X, FRONT_Y = 14, 16                 # front card topleft in the buffer
GROMMET = (33, 14)                        # face-local grommet centre (shared)


def _abbr(text):
    """Prices climb into the thousands; a swing-tag face is narrow, so collapse
    long numbers to a compact `1.2k` style that still stays readable at 1x."""
    digits = ''.join(c for c in text if c.isdigit())
    if not digits:
        return text
    v = int(digits)
    if v >= 1000:
        frac = (v % 1000) // 100
        return f"{v//1000}.{frac}k" if frac else f"{v//1000}k"
    return str(v)


def coin_ring(surf, cx, cy):
    """The shared, byte-identical coin-ring accent that unifies this tag family:
    a small brass ring with a punched-through centre so the card body shows
    inside it."""
    r = sc.m(5)
    s = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
    cc = (r + 1, r + 1)
    pygame.draw.circle(s, (156, 116, 58), cc, r)
    pygame.draw.circle(s, (48, 28, 10), cc, r, 1)
    pygame.draw.circle(s, (0, 0, 0, 0), cc, sc.m(3) + 1)
    surf.blit(s, (cx - r - 1, cy - r - 1))


def _price_glyph(text):
    """Faux-bold numeral master at the largest size whose width still clears the
    ~60dp internal face; the price is the focal element so it starts big and
    only shrinks when a wide value forces it."""
    for fs in (14, 13, 12, 11, 10):
        mask = sc._stamp_bold(sc._glyph_base(text, sc.font(fs), 0), sc.m(1.0))
        if mask.get_width() <= 60:
            return mask
    return mask


def _draw_price(face, text, center, fill_col, key_col):
    """Solid champagne numerals wrapped in a 1px device keyline so the price
    reads crisp against the dark bronze face."""
    mask = _price_glyph(text)
    r = mask.get_rect(center=center)
    kl = mask.copy()
    kl.fill((*key_col, 255), special_flags=pygame.BLEND_RGBA_MULT)
    p = sc.m(1)
    for ang in range(0, 360, 45):
        dx = int(round(p * math.cos(math.radians(ang))))
        dy = int(round(p * math.sin(math.radians(ang))))
        face.blit(kl, (r.x + dx, r.y + dy))
    img = mask.copy()
    img.fill((*fill_col, 255), special_flags=pygame.BLEND_RGBA_MULT)
    face.blit(img, r)


def _grommet(face):
    """Brass eyelet on the front face: a brass disc with a lit upper-left arc +
    shaded lower-right arc bevel, a dark bore, and a punched transparent void so
    the cord reads as diving through the card."""
    gx, gy = GROMMET
    outer_r = sc.m(4) + 1                                   # 9dp
    pygame.draw.circle(face, (184, 146, 74), (gx, gy), outer_r)
    ar = outer_r - 1
    box = (gx - ar, gy - ar, ar * 2, ar * 2)
    pygame.draw.arc(face, (240, 210, 100), box,
                    math.radians(108), math.radians(192), max(1, sc.m(1)))
    pygame.draw.arc(face, (80, 50, 10), box,
                    math.radians(288), math.radians(372), max(1, sc.m(1)))
    pygame.draw.circle(face, (40, 30, 18), (gx, gy), sc.m(3))   # bore
    pygame.draw.circle(face, (0, 0, 0, 0), (gx, gy), sc.m(2))   # void


def _build_front(text, fill_top, fill_bot, price_col):
    """The large foreground card: bronze gradient body, a fine golden inner
    keyline, the price glyph, then the shared brass grommet."""
    face = pygame.Surface((FACE_W, FACE_H), pygame.SRCALPHA)
    body = sc.vgrad_stops(FACE_W, FACE_H, FRONT_RAD,
                          [(0.0, fill_top), (1.0, fill_bot)], 255, gamma=1.04)
    face.blit(body, (0, 0))
    inset = sc.m(1)
    pygame.draw.rect(face, (196, 158, 96),
                     (inset, inset, FACE_W - 2 * inset, FACE_H - 2 * inset),
                     width=1, border_radius=FRONT_RAD - inset)
    _draw_price(face, text, (33, 45), price_col, (20, 12, 6))
    _grommet(face)
    return face


def _build_back(cream_top, cream_bot):
    """The small background accent card: warm cream body, a fine golden inner
    border, and ONLY the shared coin ring at its centre."""
    back = pygame.Surface((BACK_W, BACK_H), pygame.SRCALPHA)
    body = sc.vgrad_stops(BACK_W, BACK_H, BACK_RAD,
                          [(0.0, cream_top), (1.0, cream_bot)], 255, gamma=1.03)
    back.blit(body, (0, 0))
    inset = sc.m(1)
    pygame.draw.rect(back, (180, 154, 96),
                     (inset, inset, BACK_W - 2 * inset, BACK_H - 2 * inset),
                     width=1, border_radius=BACK_RAD - inset)
    coin_ring(back, 17, 17)
    return back


def my_price_chip(surf, cx, cy, text, h, variant=sc.PRICE_VARIANT, **kw):
    """Draw the layered double-tag at a fixed anchor in the 2x card buffer.
    Affordability is read from the variant (the store passes "locked" for
    gated/too-expensive cards); the wallet-derived `affordable` kwarg is
    absorbed and ignored so the exploration sheet forces both states
    deterministically."""
    affordable = (variant != "locked")
    text = _abbr(text)

    if affordable:
        fill_top, fill_bot = (58, 40, 24), (40, 26, 14)
        price_col = (242, 224, 178)
        cream_top, cream_bot = (246, 236, 216), (228, 212, 182)
        cord = (80, 60, 30)
        shadow_a = 102
    else:
        fill_top, fill_bot = (52, 46, 42), (38, 34, 32)
        price_col = (150, 146, 140)
        cream_top, cream_bot = (226, 222, 214), (206, 202, 194)
        cord = (100, 90, 80)
        shadow_a = 70

    # 1-2. BACK accent card (coin ring baked in), tilted, peeking top-right of
    # the front card. Blit centred so the small tilt never drifts its anchor.
    back = _build_back(cream_top, cream_bot)
    back_rot = pygame.transform.rotozoom(back, -4, 1.0)
    back_cx = FRONT_X + FACE_W - 22 + BACK_W // 2      # unrotated topleft + half
    back_cy = FRONT_Y - 8 + BACK_H // 2
    surf.blit(back_rot, back_rot.get_rect(center=(back_cx, back_cy)))

    # 3. FRONT card hard cast shadow (no blur) dropped lower-right onto the back.
    shadow = pygame.Surface((FACE_W, FACE_H), pygame.SRCALPHA)
    pygame.draw.rect(shadow, (0, 0, 0, shadow_a), shadow.get_rect(),
                     border_radius=FRONT_RAD)
    surf.blit(shadow, (FRONT_X + sc.m(3), FRONT_Y + sc.m(3)))

    # 4-7. FRONT card (body + inner stripe + price + grommet).
    front = _build_front(text, fill_top, fill_bot, price_col)
    surf.blit(front, (FRONT_X, FRONT_Y))

    # 8. Twisted two-strand cord diving into the shared grommet and off the top.
    gx, gy = FRONT_X + GROMMET[0], FRONT_Y + GROMMET[1]
    lw = max(1, sc.m(0.6))
    pygame.draw.line(surf, cord, (FRONT_X + 32, FRONT_Y + 14),
                     (FRONT_X + 16, FRONT_Y - 26), lw)
    pygame.draw.line(surf, cord, (FRONT_X + 34, FRONT_Y + 14),
                     (FRONT_X + 50, FRONT_Y - 26), lw)


sc.price_chip = my_price_chip


# ── pixel verification (run BEFORE saving the sheet) ──────────────────────────
def render_card_1x(sid, variant):
    big = pygame.Surface((sc.CARD_W * sc.SS, sc.CARD_H * sc.SS), pygame.SRCALPHA)
    inset = sc.m(sc._INSET)
    rect = pygame.Rect(inset, inset,
                       sc.CARD_W * sc.SS - 2 * inset,
                       sc.CARD_H * sc.SS - 2 * inset)
    sc.draw_card(big, sid, rect, equipped=False, secret=False, variant=variant)
    return pygame.transform.smoothscale(big, (sc.CARD_W, sc.CARD_H))


def zoom_left(card_1x):
    crop = card_1x.subsurface((0, 0, 80, 100))
    return pygame.transform.scale(crop, (160, 200))


_va = render_card_1x("skin_mummy", sc.PRICE_VARIANT)
_vl = render_card_1x("skin_mummy", "locked")
pa, pl = _va.get_at((30, 22))[:3], _vl.get_at((30, 22))[:3]
assert pa != pl, f"states identical near price face: {pa}"
print(f"aff:{pa} lock:{pl} PASS")

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
total_w = PAD + 4 * CW + 3 * GAP + PAD
total_h = HDR_H + LABEL_H + row1_h + GAP + row2_h + PAD
canvas = pygame.Surface((total_w, total_h))
canvas.fill(BG)

hf = hud_font(9, True)
ht = hf.render("double-tag · tl3 hang-tag · round 1", True, (255, 220, 80))
canvas.blit(ht, (total_w // 2 - ht.get_width() // 2, (HDR_H - ht.get_height()) // 2))

lf = hud_font(7)
card_list = [cards["mummy_aff"], cards["mummy_lck"], cards["kitsune_aff"], cards["kitsune_lck"]]
labels = ["mummy aff", "mummy lck", "kitsune aff", "kitsune lck"]
y1 = HDR_H + LABEL_H
for i, (card, label) in enumerate(zip(card_list, labels)):
    x = PAD + i * (CW + GAP)
    lbl = lf.render(label, True, (160, 156, 180))
    canvas.blit(lbl, (x, HDR_H + (LABEL_H - lbl.get_height()) // 2))
    canvas.blit(card, (x, y1))

y2 = y1 + row1_h + GAP
for i, (key, label) in enumerate([("mummy_aff", "mummy aff (2×crop)"), ("mummy_lck", "mummy lck (2×crop)")]):
    x = PAD + i * (160 + GAP)
    lbl = lf.render(label, True, (140, 136, 160))
    canvas.blit(lbl, (x, y2 - lf.get_height() - 2))
    canvas.blit(zoom_left(cards[key]), (x, y2))

out = "docs/store_price_tl3/double_tag/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(canvas, out)
print(f"saved {canvas.get_width()}x{canvas.get_height()} -> {out}")
