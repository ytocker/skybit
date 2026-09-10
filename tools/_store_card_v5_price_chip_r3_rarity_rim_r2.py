"""Round-2 (final pass) render for the `rarity-rim` price-chip concept
(Lever C+P — a rarity-tinted keyline around a dark chip, gold numerals).

The identity is the RIM HUE: every price chip is the same near-black obsidian
pill with the same warm-gold numerals, but the dominant keyline takes the item's
rarity colour — vivid purple for EPIC, hot amber-orange for LEGENDARY. The rim
is the only thing that changes across tiers, so a player learns "purple edge =
epic, amber edge = legendary" at a glance while the price itself stays a single
consistent gold everywhere.

WHY a local body finish: sc.chip_body_stops() routes through gloss_sweep(),
which BLEND_ADDs source pixels (255,255,255,a). Pygame's BLEND_ADD ignores the
source alpha and adds the full 255 per channel, so ANY gloss value blows a dark
obsidian body to solid white. The premultiplied _gloss_corrected() below draws
(a,a,a,255) so the additive amount actually respects the gloss curve. The body
also SUPPRESSES the built-in neutral bevel so the rarity keyline drawn on top is
the single dominant rim — nothing neutral competes with the tier hue.
"""
import os, sys
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)
import game.store_cards as sc
from game.hud import _font as hud_font


# ── corrected chip body (BLEND_ADD-safe gloss, no competing bevel) ────────────
def _gloss_corrected(surf, rect, radius, peak):
    """Premultiplied gloss: (a,a,a,255) so BLEND_ADD adds correct small amount."""
    sweep = pygame.Surface(rect.size, pygame.SRCALPHA)
    h = max(1, rect.h)
    for y in range(h):
        a = int(peak * (1 - y / h) ** 2.4)
        pygame.draw.line(sweep, (a, a, a, 255), (0, y), (rect.w, y))
    sm = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(sm, (255, 255, 255, 255), sm.get_rect(), border_radius=radius)
    sweep.blit(sm, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(sweep, rect.topleft, special_flags=pygame.BLEND_ADD)


def dark_chip_body_no_bevel(surf, r, radius, stops, rim_dark, gloss=12, gamma=1.04):
    """Body draw WITHOUT final bevel_rim — rarity-rim draws its own dominant
    keyline on top, so any neutral bevel here would only dilute the tier hue."""
    sc.drop_shadow(surf, r, radius, blur=sc.m(4), alpha=110, dy=sc.m(2))
    surf.blit(sc.vgrad_stops(r.w, r.h, radius, stops, 255, gamma=gamma), r.topleft)
    _gloss_corrected(surf, r, radius, peak=gloss)
    sc.contact_shadow(surf, r, radius, sc.m(3), alpha=80)
    pygame.draw.rect(surf, rim_dark, r, width=max(1, sc.m(1.6)), border_radius=radius)


# ── the concept: gold numerals on a dark pill, rim tinted by rarity ───────────
# The ONE gold ramp for numerals, identical across every tier — the tier signal
# lives entirely in the rim hue, never in the price colour.
NUM_STOPS = [(0.0, (255, 244, 196)), (0.48, (250, 228, 148)),
             (0.52, (224, 164, 62)), (1.0, (210, 150, 60))]

# (rarity, affordable) -> (deep, bright) for the dominant rarity keyline.
# Affordable rims run hot + saturated; locked rims keep the SAME hue but drop the
# bright alpha to ~100 so the tier still reads while the chip clearly looks dead.
# Legendary is pushed to amber-orange (255,140,40) so it never collides with the
# coin/numeral gold — it reads distinctly hotter and more saturated than either.
_RIM = {
    ("epic", True):       ((60, 30, 100, 220), (170, 120, 245, 240)),
    ("legendary", True):  ((100, 60, 10, 220), (255, 140, 40, 240)),
    ("epic", False):      ((40, 20, 70, 180),  (130, 90, 200, 100)),
    ("legendary", False): ((80, 50, 10, 180),  (200, 110, 30, 100)),
}


def _chip_geometry(text, h):
    """The deterministic layout the chip + the pixel-verify both read from."""
    coin_d = int(h * 0.66)
    pad = sc.m(13)
    gapc = sc.m(8)
    f = sc.font(h * 0.50 / sc.SS)
    nw = sc._glyph_base(text, f, 0).get_width() + sc.m(2)
    w = pad + coin_d + gapc + nw + pad
    return coin_d, pad, gapc, f, nw, w


def price_chip_rarity_rim(surf, cx, cy, text, h, rarity="epic", affordable=True):
    coin_d, pad, gapc, f, nw, w = _chip_geometry(text, h)
    rad = h // 2                                        # full pill silhouette
    r = pygame.Rect(cx - w // 2, cy - h // 2, w, h)

    if affordable:
        stops = [(0.0, (12, 13, 22)), (1.0, (34, 37, 56))]
    else:
        stops = [(0.0, (10, 11, 20)), (1.0, (26, 28, 44))]
    dark_chip_body_no_bevel(surf, r, rad, stops, (8, 10, 20), gloss=12, gamma=1.04)

    # the ONE dominant rim: thick (m(2) = 4 device px, survives the 2x downscale)
    # rarity keyline, drawn AFTER the body so nothing neutral competes with hue.
    deep, bright = _RIM[(rarity, affordable)]
    sc.bevel_rim(surf, r, rad, deep, bright, w=sc.m(2))

    x = r.x + pad
    ccx = x + coin_d // 2
    sc.coin_glyph(surf, ccx, cy, coin_d // 2, rim=(180, 150, 60))
    if not affordable:
        # coin_glyph() ignores `rim`; drain the locked coin with a neutral-grey
        # high-alpha tint so it reads unmistakably dead, not merely dim gold.
        cr = coin_d // 2
        tint = pygame.Surface((coin_d, coin_d), pygame.SRCALPHA)
        pygame.draw.circle(tint, (70, 74, 84, 180), (cr, cr), cr)
        surf.blit(tint, (ccx - cr, cy - cr))

    nx = r.x + pad + coin_d + gapc + nw // 2
    if affordable:
        # glyph-mask pipeline: a bold white mask multiplied by the ONE warm-gold
        # ramp so numerals read as struck metal top-lit, identical across tiers.
        mask = sc._stamp_bold(sc._glyph_base(text, f, 0), sc.m(1.0))
        grad = sc.vgrad_stops(mask.get_width(), mask.get_height(), 0,
                              NUM_STOPS, 255, 1.0)
        img = mask.copy()
        img.blit(grad, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        surf.blit(img, img.get_rect(center=(nx, cy)))
    else:
        sc.plain_text(surf, text, f, (nx, cy), color=(150, 140, 110), shadow_a=0,
                      weight=sc.m(1.0))
    return r


def draw_card_with_chip(surf, sid, rect, equipped=False, secret=False,
                        affordable=True):
    """draw_card() verbatim, with state_chip() swapped for the rarity-rim chip."""
    m = sc.m
    pal = sc.MYSTERY if secret else sc.RARITY[sc._rarity(sid)]
    rad = m(sc.CARD_RAD)
    sc.drop_shadow(surf, rect, rad, blur=m(8), alpha=160, dy=m(4))
    surf.blit(sc.vgrad(rect.w, rect.h, rad, sc.CARD_T, sc.CARD_B, 252, gamma=1.15),
              rect.topleft)
    sc.top_sheen(surf, rect, rad, m(30), peak=62)
    sc.contact_shadow(surf, rect, rad, m(9), alpha=120)
    pygame.draw.rect(surf, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    sc.bevel_rim(surf, rect, rad, sc.CARD_RING_DEEP, (*sc.CARD_RING_BRIGHT, 235),
                 w=max(1, m(2.0)))
    tray = rect.inflate(-m(7), -m(7))
    trad = rad - m(4)
    pygame.draw.rect(surf, (10, 10, 24, 200), tray.inflate(m(2), m(2)),
                     width=max(1, m(1)), border_radius=trad + m(1))
    pygame.draw.rect(surf, (*sc.CARD_RING_BRIGHT, 90), tray, width=max(1, m(1)),
                     border_radius=trad)
    cx, cy = rect.centerx, rect.y + m(sc.CY_DISC) + sc._DOME_DY
    sc.soft_glow(surf, cx, cy, sc._DOME_R + m(3), pal["glow"], 30, layers=8)
    sc.cabochon(surf, cx, cy, sc._DOME_R, sc.CABO_LO, sc.CABO_HI,
                ring=pal["gem"], ring_a=50)
    if secret:
        sc._draw_qmark(surf, cx, cy, sc._DOME_R + m(6), sc.CREAM, sc.NEAR_BLACK,
                       thick=m(2))
        name = "???"
    else:
        name = sc._name(sid)
    sc.cabochon_glass(surf, cx, cy, sc._DOME_R, tint=pal["gem"])
    if not secret:
        sc.blit_thumb(surf, sid, cx, cy - sc._ITEM_DY, sc._BOX_PX)
    sc.facet_gem(surf, rect.right - m(19), rect.y + m(19), m(sc.GEM_R + 3),
                 pal["gem"], pal["deep"], mystery=secret)
    tier_word = "MYSTERY" if secret else sc._rarity(sid).upper()
    sc._ribbon_lozenge(surf, tier_word, cx, rect.y + m(55) - sc._RIBN_DY,
                       rect.w - m(34), pal)
    sc._name_on(surf, name, cx, rect.y + m(70), rect.w - m(26))
    if equipped:
        sc.status_chip(surf, cx, rect.y + m(88) - sc._CHIP_DY, "EQUIPPED", m(20),
                       kind="equipped")
    else:
        price = f"{sc._cost(sid):,}"
        price_chip_rarity_rim(surf, cx, rect.y + m(88) - sc._CHIP_DY,
                              price, m(20), rarity=sc._rarity(sid),
                              affordable=affordable)


# ── chip strips (4x detail + true 1x) ─────────────────────────────────────────
def chip_native(text, rarity, affordable):
    """Draw one chip at native SS onto a tight cropped surface."""
    h = sc.m(20)
    pad = sc.m(6)
    tmp = pygame.Surface((sc.m(400), h + pad * 2), pygame.SRCALPHA)
    r = price_chip_rarity_rim(tmp, sc.m(200), h // 2 + pad, text, h,
                              rarity=rarity, affordable=affordable)
    crop = pygame.Rect(r.x - pad, 0, r.w + pad * 2, h + pad * 2)
    return tmp.subsurface(crop).copy()


def zoom_chip(text, rarity, affordable, zoom=4):
    sub = chip_native(text, rarity, affordable)
    return pygame.transform.smoothscale(
        sub, (sub.get_width() * zoom, sub.get_height() * zoom))


def true1x_chip(text, rarity, affordable):
    """The chip at actual gameplay logical size (SS downscaled to 1x)."""
    sub = chip_native(text, rarity, affordable)
    w = max(1, round(sub.get_width() / sc.SS))
    h = max(1, round(sub.get_height() / sc.SS))
    return pygame.transform.smoothscale(sub, (w, h))


def verify(text, rarity):
    """Pixel-audit an AFFORDABLE chip: the body must stay near-black."""
    h = sc.m(20)
    coin_d, pad, gapc, f, nw, w = _chip_geometry(text, h)
    surf = pygame.Surface((w + sc.m(40), h + sc.m(40)), pygame.SRCALPHA)
    cx, cy = surf.get_width() // 2, surf.get_height() // 2
    r = price_chip_rarity_rim(surf, cx, cy, text, h, rarity=rarity, affordable=True)
    # pure-body sample: the gap between the coin cell and the numerals
    bx = r.x + pad + coin_d + gapc // 2
    px = surf.get_at((bx, cy))
    assert px[0] < 60 and px[1] < 60 and px[2] < 90, f"Body blown! {tuple(px[:3])}"
    print(f"  {rarity} body center: {tuple(px[:3])}  (near-black OK)")


# ── SIDs under test ───────────────────────────────────────────────────────────
EPIC_SID = "skin_mummy"       # cost 1,100
LEGEND_SID = "skin_kitsune"   # cost 3,500

# The 4-column matrix: (sid, rarity, affordable, label)
COLS = [
    (EPIC_SID,   "epic",      True,  "EPIC / AFFORDABLE"),
    (EPIC_SID,   "epic",      False, "EPIC / LOCKED"),
    (LEGEND_SID, "legendary", True,  "LEGEND / AFFORDABLE"),
    (LEGEND_SID, "legendary", False, "LEGEND / LOCKED"),
]


def main():
    print("verify AFFORDABLE bodies stay dark:")
    verify("1,100", "epic")
    verify("3,500", "legendary")

    label_lg = hud_font(18, True)
    label_md = hud_font(16, True)
    label_sm = hud_font(13, True)

    cw, ch = sc.CARD_W * sc.SS, sc.CARD_H * sc.SS

    def hero(sid, affordable):
        card = pygame.Surface((cw, ch + 16), pygame.SRCALPHA)
        rect = pygame.Rect(sc.m(sc._INSET), sc.m(sc._INSET),
                           cw - 2 * sc.m(sc._INSET), ch - 2 * sc.m(sc._INSET))
        draw_card_with_chip(card, sid, rect, equipped=False, secret=False,
                            affordable=affordable)
        return card

    cards = [hero(sid, aff) for sid, rar, aff, lbl in COLS]

    def price_of(sid):
        return f"{sc._cost(sid):,}"

    chips4 = [zoom_chip(price_of(sid), rar, aff, zoom=4)
              for sid, rar, aff, lbl in COLS]
    chips1 = [true1x_chip(price_of(sid), rar, aff)
              for sid, rar, aff, lbl in COLS]

    MARGIN = 20
    GAP = 16
    HDR_H = 44
    footer = 34

    card_row_w = cw * 4 + GAP * 3
    W = card_row_w + MARGIN * 2

    def text(surf, s, font_obj, center, col=(232, 236, 248)):
        img = font_obj.render(s, True, col)
        surf.blit(img, img.get_rect(center=center))

    y_cards = HDR_H
    y_striplbl = y_cards + ch + 46
    y_strip = y_striplbl + 20
    strip_h = max(c.get_height() for c in chips4)
    y_1xlbl = y_strip + strip_h + 26
    y_1x = y_1xlbl + 20
    t1_h = max(c.get_height() for c in chips1)
    H = y_1x + t1_h + footer

    canvas = pygame.Surface((W, H))
    canvas.fill((8, 8, 20))

    text(canvas,
         "v5 price-chip r3 — rarity-rim r2 — EPIC vs LEGENDARY — C+P(rim-hue)",
         label_lg, (W // 2, HDR_H // 2))

    # card row
    lbl_cols = [(150, 214, 150), (214, 158, 158),
                (150, 214, 150), (214, 158, 158)]
    for i, (sid, rar, aff, lbl) in enumerate(COLS):
        cx0 = MARGIN + i * (cw + GAP)
        canvas.blit(cards[i], (cx0, y_cards))
        text(canvas, lbl, label_sm, (cx0 + cw // 2, y_cards + ch + 13),
             lbl_cols[i])

    # 4x detail strip on a card-body gradient patch (judged on the shipping ground)
    text(canvas, "4× DETAIL (on card-body gradient)", label_md,
         (W // 2, y_striplbl), (150, 156, 178))
    s_gap = 26
    strip_w = sum(c.get_width() for c in chips4) + s_gap * 3
    sx = (W - strip_w) // 2
    patch_pad = 18
    patch = pygame.Rect(sx - patch_pad, y_strip - patch_pad // 2,
                        strip_w + patch_pad * 2, strip_h + patch_pad)
    canvas.blit(sc.vgrad(patch.w, patch.h, sc.m(sc.CARD_RAD), sc.CARD_T,
                         sc.CARD_B, 255, gamma=1.15), patch.topleft)
    pygame.draw.rect(canvas, (*sc.CARD_RING_BRIGHT, 90), patch,
                     width=1, border_radius=sc.m(sc.CARD_RAD))
    xcur = sx
    for c in chips4:
        canvas.blit(c, (xcur, y_strip + (strip_h - c.get_height()) // 2))
        xcur += c.get_width() + s_gap

    # true 1x strip
    text(canvas, "TRUE 1× (gameplay scale)", label_md, (W // 2, y_1xlbl),
         (150, 156, 178))
    t1_gap = 34
    t1_w = sum(c.get_width() for c in chips1) + t1_gap * 3
    tx = (W - t1_w) // 2
    for c in chips1:
        canvas.blit(c, (tx, y_1x + (t1_h - c.get_height()) // 2))
        tx += c.get_width() + t1_gap

    text(canvas,
         "dark body · gold numerals everywhere · thick rarity keyline "
         "purple=EPIC / amber=LEGENDARY · body verified dark",
         label_sm, (W // 2, H - footer // 2), (150, 156, 178))

    out = os.path.join(os.path.dirname(__file__), "..",
                       "docs", "store_card_v5_price_chip_r3",
                       "rarity-rim", "round_2.png")
    out = os.path.abspath(out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(canvas, out)
    print("wrote", out, canvas.get_size())


if __name__ == "__main__":
    main()
