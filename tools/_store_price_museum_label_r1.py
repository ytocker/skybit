"""Round-1 render sheet for the MUSEUM-LABEL store-card price redesign.

Monkey-patches store_cards.price_chip with a pure-typography treatment: the
price stops being a physical pill and becomes an editorial caption at the card
foot — a subtle full-width dark wash under a fine hairline rule, with large
coin-metal numerals floating on it like an auction-catalog price line. No
container, no border, no pill metaphor: the band IS the ground and the type IS
the object. Renders 4 in-context cards (EPIC + LEGENDARY, affordable + locked)
plus 4x zoom crops of the band so the numeral treatment reads clearly.

Review-only tooling — never imported by the game.
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, "/home/user/skybit")

import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

import game.store_cards as sc
from game.draw import NEAR_BLACK
from game.hud import _font as hud_font


SID_PRIMARY   = "skin_mummy"    # EPIC
SID_SECONDARY = "skin_kitsune"  # LEGENDARY

# The band lives at the FOOT of the fixed card body — derive it from the same
# inset the live card uses so the treatment tracks the real geometry.
BODY = pygame.Rect(sc.m(sc._INSET), sc.m(sc._INSET),
                   sc.CARD_W * sc.SS - 2 * sc.m(sc._INSET),
                   sc.CARD_H * sc.SS - 2 * sc.m(sc._INSET))
BAND_H = 22


def _lerp_rgba(stops, t):
    """Per-stop RGBA lerp — the band fades BOTH colour and alpha (transparent at
    the top, a dark wash at the foot), which the RGB-only vgrad_stops can't do."""
    t = max(0.0, min(1.0, t))
    (t0, c0), (t1, c1) = stops[0], stops[1]
    f = 0.0 if t1 == t0 else (t - t0) / (t1 - t0)
    return tuple(int(round(a + (b - a) * f)) for a, b in zip(c0, c1))


def _band_surface():
    """A 300x22 wash, transparent->dark top to bottom, clipped to the body's
    rounded bottom corners so it never bleeds past the card silhouette."""
    band = pygame.Surface((BODY.w, BAND_H), pygame.SRCALPHA)
    stops = [(0.0, (16, 16, 34, 0)), (1.0, (8, 8, 20, 150))]
    for y in range(BAND_H):
        pygame.draw.line(band, _lerp_rgba(stops, y / max(1, BAND_H - 1)),
                         (0, y), (BODY.w - 1, y))
    # Clip to the card's rounded bottom: build the full body mask, keep its
    # bottom slice, and MIN it into the band's alpha.
    rad = sc.m(sc.CARD_RAD)
    mask = pygame.Surface((BODY.w, BODY.h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=rad)
    slice_ = mask.subsurface((0, BODY.h - BAND_H, BODY.w, BAND_H)).copy()
    band.blit(slice_, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return band


def my_price_chip(surf, cx, cy, text, h, variant=1, affordable=True):
    """MUSEUM-LABEL price line: no pill, no rim. A dark editorial wash + a fine
    hairline rule, with the price set LARGE as the sole design element — warm
    coin-metal numerals when affordable, cool pewter when locked."""
    band_x, band_y = BODY.x, BODY.bottom - BAND_H

    # 1 — the wash band is the whole background for the price
    surf.blit(_band_surface(), (band_x, band_y))

    # 2 — a single fine hairline rule capping the band (warm gold / cool steel);
    # drawn on an SRCALPHA strip so its low alpha COMPOSITES instead of punching
    # a translucent slot into the opaque card body.
    x0, x1 = BODY.x + sc.m(9), BODY.right - sc.m(9)
    lw = max(1, sc.m(0.5))
    hair = (236, 202, 116, 150) if affordable else (110, 116, 132, 140)
    rule = pygame.Surface((x1 - x0, lw), pygame.SRCALPHA)
    rule.fill(hair)
    surf.blit(rule, (x0, band_y))

    # 3 — the price, set large, centred on the band as the sole element
    gy = band_y + BAND_H // 2
    f = sc.font(13)                      # ~13pt at 1x — larger than any chip glyph
    coin_r = sc.m(4.5)                   # r=9 device px
    coin_d = coin_r * 2

    mask = sc._stamp_bold(sc._glyph_base(text, f, 0), sc.m(1.0))
    num_w = mask.get_width()
    gap = sc.m(5)
    total = coin_d + gap + num_w
    gx = cx - total // 2
    ccx = gx + coin_r
    nx = gx + coin_d + gap + num_w // 2

    if affordable:
        sc.coin_glyph(surf, ccx, gy, coin_r)
        # a soft dark drop so the metal numerals hold on the subtle wash
        sh = mask.copy()
        sh.fill((*NEAR_BLACK, 255), special_flags=pygame.BLEND_RGBA_MULT)
        sh.set_alpha(150)
        surf.blit(sh, sh.get_rect(center=(nx, gy + sc.m(1.4))))
        grad = sc.vgrad_stops(mask.get_width(), mask.get_height(), 0,
                              sc._SOVEREIGN_NUM_STOPS, 255, 1.0)
        img = mask.copy()
        img.blit(grad, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        surf.blit(img, img.get_rect(center=(nx, gy)))
    else:
        # cool locked coin: same struck disc, pewter-tinted so the whole line
        # goes quiet and the warm gradient is skipped entirely.
        sc.coin_glyph(surf, ccx, gy, coin_r, rim=(120, 108, 78))
        tint = pygame.Surface((coin_d, coin_d), pygame.SRCALPHA)
        pygame.draw.circle(tint, (72, 76, 92, 150), (coin_r, coin_r), coin_r)
        surf.blit(tint, (ccx - coin_r, gy - coin_r))
        sc.plain_text(surf, text, f, (nx, gy), color=(150, 156, 172),
                      shadow_a=150, weight=sc.m(1.0))

    return pygame.Rect(band_x, band_y, BODY.w, BAND_H)


sc.price_chip = my_price_chip   # patch BEFORE any draw_card call


# ── render helpers ─────────────────────────────────────────────────────────────
def render_card(sid, affordable):
    """One full v5 card at SS. Affordability is driven by the REAL wallet gate,
    so we pin store_data.balance to force each state (no card cache in this path)."""
    sc.store_data.balance = (lambda: 10 ** 9) if affordable else (lambda: 0)
    big = pygame.Surface((sc.CARD_W * sc.SS, sc.CARD_H * sc.SS), pygame.SRCALPHA)
    sc.draw_card(big, sid, BODY.copy(), equipped=False, secret=False)
    return big


def down(surf, w, h):
    return pygame.transform.smoothscale(surf, (w, h))


def main():
    out_dir = "/home/user/skybit/docs/store_price_redesign/museum-label"
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "round_1.png")

    specs = [
        ("skin_mummy EPIC — buy",      SID_PRIMARY,   True),
        ("skin_mummy EPIC — locked",   SID_PRIMARY,   False),
        ("skin_kitsune LEG — buy",     SID_SECONDARY, True),
        ("skin_kitsune LEG — locked",  SID_SECONDARY, False),
    ]

    pad = 28
    gap = 22
    header_h = 42
    label_h = 22
    cw, chh = 162, 100

    big_cards = [render_card(sid, aff) for _, sid, aff in specs]
    cards = [down(b, cw, chh) for b in big_cards]

    # 4x zoom crops of the band foot (buffer is 2x -> crop x2 = 4x effective).
    crop_dev = pygame.Rect(BODY.x, BODY.bottom - 40, BODY.w, 40)
    zoom = 2
    zw, zh = crop_dev.w * zoom, crop_dev.h * zoom
    crops = [(specs[i][0], down(big_cards[i].subsurface(crop_dev).copy(), zw, zh))
             for i in (2, 3)]   # LEGENDARY affordable + locked show the band best

    row1_w = cw * 4 + gap * 3
    row1_y = header_h + pad

    zoom_y = row1_y + chh + label_h + gap * 2
    row2_w = zw

    canvas_w = pad * 2 + max(row1_w, row2_w)
    canvas_h = zoom_y + (zh + label_h) * 2 + gap + pad

    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill((8, 8, 20))

    hf = hud_font(30, True)
    lf = hud_font(17)
    sf = hud_font(15)

    canvas.blit(hf.render("store price redesign  —  museum-label  r1",
                          True, (236, 232, 250)), (pad, pad // 2 + 4))

    # Row 1 — the four cards in context
    x = pad + (max(row1_w, row2_w) - row1_w) // 2
    for (label, _, _), card in zip(specs, cards):
        canvas.blit(card, (x, row1_y))
        lbl = lf.render(label, True, (206, 202, 224))
        canvas.blit(lbl, (x + (cw - lbl.get_width()) // 2, row1_y + chh + 5))
        x += cw + gap

    # Zoom crops — the price band at 4x so the type treatment is legible
    zx = pad + (max(row1_w, row2_w) - row2_w) // 2
    y = zoom_y
    canvas.blit(sf.render("price band  —  4x zoom", True, (150, 156, 178)),
                (zx, y - label_h + 2))
    for label, crop in crops:
        canvas.blit(crop, (zx, y))
        canvas.blit(sf.render(label, True, (206, 202, 224)),
                    (zx + 6, y + zh + 3))
        y += zh + label_h + gap

    pygame.image.save(canvas, out)
    print("saved", out, canvas.get_size())


if __name__ == "__main__":
    main()
