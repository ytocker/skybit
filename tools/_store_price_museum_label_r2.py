"""Round-2 render sheet for the MUSEUM-LABEL store-card price redesign.

Round 1 proved the editorial-caption idea: a wash at the card foot, large
numerals, a hairline footer rule. Round 2 resolves the coin contradiction and
strengthens the affordability read. The price keeps the real in-game coin — a
COMPACT r=8 disc that anchors the numerals as a COST, not a score — so this is
now a "minimal typographic price", not a no-glyph line. Affordable is warm,
bright and visually HEAVIER (large gold numerals + bright coin + a bright warm
rule + a faint additive shimmer along the numeral midline); locked drops cooler,
darker and SMALLER, with a tiny cool-pewter LOCKED micro-cap above a steel rule,
so "more active" reads instantly by weight and temperature. The foot wash is
softened to a gentle warm darken (max alpha 130, warm floor) so it never stamps
a black band. Renders 4 in-context cards plus 4x foot-zoom crops.

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

# The footer lives at the FOOT of the fixed card body — derive it from the same
# inset the live card uses so the treatment tracks the real geometry (2x buffer:
# body x 12..312, bottom 188, bottom corners radius m(CARD_RAD)=34).
BODY = pygame.Rect(sc.m(sc._INSET), sc.m(sc._INSET),
                   sc.CARD_W * sc.SS - 2 * sc.m(sc._INSET),
                   sc.CARD_H * sc.SS - 2 * sc.m(sc._INSET))

# Vertical stack (device px in the 2x buffer). Numeral MIDLINE is shared across
# both states so the price sits at the same optical foot in the grid; locked
# simply adds a micro-cap above the rule. The wash is tall enough to breathe up
# past the rule but fades to transparent well before it, so it darkens gently.
NUM_Y    = 176               # numeral midline — the price optical centre
RULE_Y   = 158               # full-width footer rule, just above the numerals
MICRO_Y  = 148               # locked "LOCKED" micro-cap, above the rule
WASH_TOP = 142
WASH_H   = BODY.bottom - WASH_TOP

# Warmer, brighter coin-metal ramp than round 1 — the brightest stop is pushed
# to a hot gold so the affordable numerals feel LIT, not merely coloured.
_R2_NUM_STOPS = [
    (0.0,  (255, 220, 120)),
    (0.35, (246, 198, 104)),
    (0.70, (214, 150,  54)),
    (1.0,  (168, 112,  34)),
]

# Softened foot wash: a warm floor tint at a capped alpha so it reads as gentle
# atmosphere, never a punched-out black band (round 1's near-black floor).
WASH_FLOOR = (30, 24, 44)
WASH_MAX_A = 130

# Full-width footer rule ends (2x buffer): edge-to-edge from the body inset.
RULE_X0 = BODY.x + sc.m(3)   # x=12+6=18 -> full-card footer read, not a stub
RULE_X1 = BODY.right - sc.m(3)


def _lerp_rgba(c0, c1, f):
    f = max(0.0, min(1.0, f))
    return tuple(int(round(a + (b - a) * f)) for a, b in zip(c0, c1))


def _wash_surface():
    """A soft warm darken at the card foot: transparent at the top, easing to a
    warm floor tint at a CAPPED alpha, clipped to the body's rounded bottom
    corners so it never bleeds past the silhouette."""
    wash = pygame.Surface((BODY.w, WASH_H), pygame.SRCALPHA)
    for y in range(WASH_H):
        # ease-in so the darken accelerates toward the foot instead of a linear
        # ramp that would read as a hard-edged band.
        f = (y / max(1, WASH_H - 1)) ** 1.6
        a = int(WASH_MAX_A * f)
        pygame.draw.line(wash, (*WASH_FLOOR, a), (0, y), (BODY.w - 1, y))
    rad = sc.m(sc.CARD_RAD)
    mask = pygame.Surface((BODY.w, BODY.h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=rad)
    slice_ = mask.subsurface((0, BODY.h - WASH_H, BODY.w, WASH_H)).copy()
    wash.blit(slice_, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return wash


def _rule(surf, y, color):
    """A 1px footer hairline drawn edge-to-edge on an SRCALPHA strip so its low
    alpha COMPOSITES onto the card instead of punching a translucent slot."""
    lw = max(1, sc.m(0.5))
    rule = pygame.Surface((RULE_X1 - RULE_X0, lw), pygame.SRCALPHA)
    rule.fill(color)
    surf.blit(rule, (RULE_X0, y))


def my_price_chip(surf, cx, cy, text, h, variant=1, affordable=True):
    """MUSEUM-LABEL price line: a soft foot wash + a full-width hairline rule,
    with the price set as the sole element. Affordable = LARGE warm gold numerals
    + a compact bright coin + a lit shimmer; locked = SMALLER cool-pewter numerals
    under a tiny LOCKED micro-cap, so 'more active' reads by weight + temperature."""
    cx = BODY.centerx    # centre on the real card, not the chip's passed centre

    # 1 — the softened wash is the whole ground for the price
    surf.blit(_wash_surface(), (BODY.x, WASH_TOP))

    # 2 — the footer rule: bright warm gold (affordable) / cool steel (locked)
    if affordable:
        _rule(surf, RULE_Y, (246, 214, 132, 185))
    else:
        _rule(surf, RULE_Y, (120, 126, 146, 150))
        # 3 — locked-only micro-cap: a quiet cool-pewter caption above the rule
        sc.plain_text(surf, "LOCKED", sc.font(7), (cx, MICRO_Y),
                      color=(150, 156, 178), shadow_a=90,
                      tracking=sc.m(1.4), weight=sc.m(0.5))

    # 4 — the price line: a COMPACT coin left of the numerals so the number reads
    # unambiguously as a cost. Locked numerals shrink (font 11 vs 13) so the
    # affordable line is visually the heavier, more active one.
    coin_r = sc.m(4)                      # r=8 device px — compact
    coin_d = coin_r * 2
    f = sc.font(13) if affordable else sc.font(11)

    mask = sc._stamp_bold(sc._glyph_base(text, f, 0), sc.m(1.0))
    num_w = mask.get_width()
    gap = sc.m(4)
    total = coin_d + gap + num_w
    gx = cx - total // 2
    ccx = gx + coin_r
    nx = gx + coin_d + gap + num_w // 2

    if affordable:
        sc.coin_glyph(surf, ccx, NUM_Y, coin_r)
        # a soft dark drop so the metal numerals hold on the subtle wash
        sh = mask.copy()
        sh.fill((*NEAR_BLACK, 255), special_flags=pygame.BLEND_RGBA_MULT)
        sh.set_alpha(150)
        surf.blit(sh, sh.get_rect(center=(nx, NUM_Y + sc.m(1.4))))
        grad = sc.vgrad_stops(mask.get_width(), mask.get_height(), 0,
                              _R2_NUM_STOPS, 255, 1.0)
        img = mask.copy()
        img.blit(grad, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        surf.blit(img, img.get_rect(center=(nx, NUM_Y)))
        # 5 — a thin lit shimmer along the numeral midline so the gold feels lit,
        # not static: a faint warm additive strip, just a few px tall.
        shim_h = sc.m(4)
        shimmer = pygame.Surface((num_w + sc.m(6), shim_h), pygame.SRCALPHA)
        shimmer.fill((255, 240, 180, 20))
        surf.blit(shimmer, shimmer.get_rect(center=(nx, NUM_Y)),
                  special_flags=pygame.BLEND_ADD)
    else:
        # cool locked coin: same struck disc, pewter-tinted so the whole line goes
        # quiet and cooler than the warm affordable line.
        sc.coin_glyph(surf, ccx, NUM_Y, coin_r, rim=(120, 108, 78))
        tint = pygame.Surface((coin_d, coin_d), pygame.SRCALPHA)
        pygame.draw.circle(tint, (72, 76, 92, 150), (coin_r, coin_r), coin_r)
        surf.blit(tint, (ccx - coin_r, NUM_Y - coin_r))
        # darker AND cooler numerals than the affordable gold
        sc.plain_text(surf, text, f, (nx, NUM_Y), color=(110, 114, 136),
                      shadow_a=140, weight=sc.m(1.0))

    return pygame.Rect(BODY.x, WASH_TOP, BODY.w, WASH_H)


sc.price_chip = my_price_chip   # patch BEFORE any draw_card call


# ── render helpers ─────────────────────────────────────────────────────────────
def render_card(sid, affordable):
    """One full v5 card at SS. Affordability is driven by the REAL wallet gate,
    so we pin store_data.balance to force each state."""
    sc.store_data.balance = (lambda: 10 ** 9) if affordable else (lambda: 0)
    big = pygame.Surface((sc.CARD_W * sc.SS, sc.CARD_H * sc.SS), pygame.SRCALPHA)
    sc.draw_card(big, sid, BODY.copy(), equipped=False, secret=False)
    return big


def down(surf, w, h):
    return pygame.transform.smoothscale(surf, (w, h))


# ── pixel verification ─────────────────────────────────────────────────────────
def _luma(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def verify(big_afford, big_locked):
    """Probe the rendered 2x buffers to confirm the round-2 intent held."""
    # wash alpha ceiling — check the standalone wash surface at its darkest row
    wash = _wash_surface()
    max_a = max(wash.get_at((wash.get_width() // 2, y))[3]
                for y in range(wash.get_height()))
    assert max_a <= 135, f"wash alpha {max_a} exceeds 135"

    # affordable numerals: warm gold present, well right of centre-left coin
    warm = False
    for y in range(NUM_Y - 8, NUM_Y + 9):
        for x in range(BODY.centerx - 20, BODY.centerx + 60):
            r, g, b, _ = big_afford.get_at((x, y))
            if r > 200 and g > 160 and b < 130 and r > b + 50:
                warm = True
                break
        if warm:
            break
    assert warm, "no warm gold numeral pixel found on affordable card"

    # locked numerals: cool pewter (b>r) and clearly lower luma than affordable
    cool_luma = []
    warm_luma = []
    for y in range(NUM_Y - 8, NUM_Y + 9):
        for x in range(BODY.centerx - 10, BODY.centerx + 60):
            cl = big_locked.get_at((x, y))
            ca = big_afford.get_at((x, y))
            if cl[3] > 200 and cl[2] > cl[0] and _luma(cl) > 40:
                cool_luma.append(_luma(cl))
            if ca[3] > 200 and ca[0] > ca[2] + 30:
                warm_luma.append(_luma(ca))
    assert cool_luma, "no cool pewter locked numeral pixel found"
    assert (sum(cool_luma) / len(cool_luma)) < (sum(warm_luma) / len(warm_luma)), \
        "locked numerals not clearly darker than affordable"

    # LOCKED micro-cap present: cool pixels centred in the locked card at the
    # expected footer band (numerals + micro-cap both land cool here).
    micro_cool = 0
    for y in range(170, 179):
        for x in range(BODY.centerx - 40, BODY.centerx + 40):
            c = big_locked.get_at((x, y))
            if c[3] > 120 and c[2] > c[0] and _luma(c) > 60:
                micro_cool += 1
    assert micro_cool > 8, f"locked footer cool pixels sparse ({micro_cool})"

    # and the micro-cap glyph itself, above the rule
    micro_label = 0
    for y in range(MICRO_Y - 8, MICRO_Y + 9):
        for x in range(BODY.centerx - 40, BODY.centerx + 40):
            c = big_locked.get_at((x, y))
            if c[3] > 120 and c[2] >= c[0] and _luma(c) > 70:
                micro_label += 1
    assert micro_label > 6, f"LOCKED micro-cap glyph not found ({micro_label})"
    print(f"verify OK — wash_a<=135 ({max_a}), warm gold + cool pewter split, "
          f"micro-cap px {micro_label}")


def main():
    out_dir = "/home/user/skybit/docs/store_price_redesign/museum-label"
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "round_2.png")

    specs = [
        ("skin_mummy EPIC — buy",      SID_PRIMARY,   True),
        ("skin_mummy EPIC — locked",   SID_PRIMARY,   False),
        ("skin_kitsune LEG — buy",     SID_SECONDARY, True),
        ("skin_kitsune LEG — locked",  SID_SECONDARY, False),
    ]

    big_cards = [render_card(sid, aff) for _, sid, aff in specs]

    # verify on the EPIC pair (index 0 afford, 1 locked)
    verify(big_cards[0], big_cards[1])

    pad = 20
    gap = 12
    header_h = 40
    label_h = 20
    cw, chh = 162, 100

    cards = [down(b, cw, chh) for b in big_cards]

    # 4x foot-zoom crops: 1x card foot y=76..100 full width -> device y 152..200,
    # x 0..324, then scale 2x for 4x effective magnification.
    crop_dev = pygame.Rect(0, 152, sc.CARD_W * sc.SS, sc.CARD_H * sc.SS - 152)
    zoom = 2
    zw, zh = crop_dev.w * zoom, crop_dev.h * zoom
    crops = [(specs[i][0], down(big_cards[i].subsurface(crop_dev).copy(), zw, zh))
             for i in range(4)]

    row1_w = cw * 4 + gap * 3
    row1_y = header_h + pad

    canvas_w = pad * 2 + max(row1_w, zw)
    zoom_y = row1_y + chh + label_h + gap
    canvas_h = zoom_y + (zh + label_h) * 4 + gap * 3 + pad

    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill((8, 8, 20))

    hf = hud_font(28, True)
    lf = hud_font(16)
    sf = hud_font(15)

    canvas.blit(hf.render("store price redesign  —  museum-label  r2",
                          True, (236, 232, 250)), (pad, pad // 2 + 4))

    # Row 1 — the four cards in context
    x = pad + (max(row1_w, zw) - row1_w) // 2
    for (label, _, _), card in zip(specs, cards):
        canvas.blit(card, (x, row1_y))
        lbl = lf.render(label, True, (206, 202, 224))
        canvas.blit(lbl, (x + (cw - lbl.get_width()) // 2, row1_y + chh + 4))
        x += cw + gap

    # Foot zoom crops stacked — the price footer at 4x so the type + rule + coin
    # + micro-cap read clearly.
    zx = pad + (max(row1_w, zw) - zw) // 2
    y = zoom_y
    canvas.blit(sf.render("price footer  —  4x zoom", True, (150, 156, 178)),
                (zx, y - label_h + 2))
    for label, crop in crops:
        canvas.blit(crop, (zx, y))
        canvas.blit(sf.render(label, True, (206, 202, 224)), (zx + 6, y + zh + 2))
        y += zh + label_h + gap

    pygame.image.save(canvas, out)
    print(f"saved {canvas.get_width()}x{canvas.get_height()} -> {out}")


if __name__ == "__main__":
    main()
