"""Round-2 (final pass) render for the `chrome-ring` price-chip concept
(Lever P — rim/border).

The identity is the FRAME, not the fill: a genuinely dark near-black obsidian
pill whose only shine lives in a cool-white metallic DOUBLE-BAND ring. That cool
hue family is alien to every gold concept, so the frame alone identifies the
chip. Warm-gold numerals + the real in-game coin ride the dark body; can't-afford
drains the metal to dead pewter and greys the coin so the chip goes dull rather
than changing character.

WHY a local body finish: sc.chip_body_stops() routes through gloss_sweep(),
which BLEND_ADDs (255,255,255,a) source pixels. Pygame's BLEND_ADD ignores the
source alpha and adds the full 255 per channel, so ANY gloss value blows a dark
obsidian body to solid white. The premultiplied _gloss_corrected() below draws
(a,a,a,255) so the additive amount actually respects the gloss curve, keeping
the body near-black. And the NO-BEVEL variant suppresses chip_body's built-in
neutral bevel so the chrome bands are the ONLY rim the eye reads — no muddy
triple-stack of concentric neutral strokes competing with the frame.
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

SID = "skin_mummy"


# ── corrected chip body (BLEND_ADD-safe gloss) ────────────────────────────────
def _gloss_corrected(surf, rect, radius, peak):
    """Premultiplied gloss: draws (a,a,a,255) so BLEND_ADD adds correct amount."""
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
    """Like dark_chip_body but WITHOUT the final bevel_rim — the chrome-ring draws
    its own frame, so the chip must NOT carry chip_body's built-in neutral bevel
    (that stacked a third concentric stroke that muddied the double-band read)."""
    sc.drop_shadow(surf, r, radius, blur=sc.m(4), alpha=110, dy=sc.m(2))
    surf.blit(sc.vgrad_stops(r.w, r.h, radius, stops, 255, gamma=gamma), r.topleft)
    _gloss_corrected(surf, r, radius, peak=gloss)
    sc.contact_shadow(surf, r, radius, sc.m(3), alpha=80)
    pygame.draw.rect(surf, rim_dark, r, width=max(1, sc.m(1.6)), border_radius=radius)
    # NO bevel_rim here — chrome-ring draws its own frame


def _bottom_frame_stroke(surf, rect, radius, color, alpha, w):
    """A cool bottom-lit stroke hugging the lower arc of the pill: bevel_rim only
    ever brightens the top-left, so on its own the ring reads as a top emboss.
    This masks a rounded-rect outline to the bottom half + blits it at reduced
    alpha, so the frame wraps the bottom arc and reads as a full closed ring."""
    s = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(s, (*color, 255), s.get_rect(), width=w, border_radius=radius)
    mask = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255),
                        [(0, rect.h // 2), (rect.w, rect.h // 2),
                         (rect.w, rect.h), (0, rect.h)])
    s.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    s.set_alpha(alpha)
    surf.blit(s, rect.topleft)


# ── the concept: dark obsidian body framed by a cool-white chrome double-ring ──
def _chip_geometry(text, h):
    """The deterministic layout the chip + the pixel-verify both read from."""
    coin_d = int(h * 0.66)
    pad = sc.m(13)
    gapc = sc.m(8)                                    # clear gap: coin cell -> digits
    f = sc.font(h * 0.50 / sc.SS)
    nw = sc._glyph_base(text, f, 0).get_width() + sc.m(2)
    w = pad + coin_d + gapc + nw + pad
    return coin_d, pad, gapc, f, nw, w


def price_chip_chrome_ring(surf, cx, cy, text, h, affordable=True):
    coin_d, pad, gapc, f, nw, w = _chip_geometry(text, h)
    rad = h // 2                                       # full pill silhouette
    r = pygame.Rect(cx - w // 2, cy - h // 2, w, h)

    if affordable:
        stops = [(0.0, (12, 13, 22)), (1.0, (34, 37, 56))]
    else:
        stops = [(0.0, (10, 11, 20)), (1.0, (26, 28, 44))]
    # gloss stays very low so the body stays dark; the chrome frame carries shine.
    dark_chip_body_no_bevel(surf, r, rad, stops, (8, 10, 20), gloss=12, gamma=1.04)

    if affordable:
        # DOUBLE chrome ring — thickened to 2px at SS=2 and separated so the two
        # bands survive the 1x downscale instead of fusing into one strip.
        sc.bevel_rim(surf, r, rad, (30, 34, 50, 220), (235, 240, 255, 255),
                     w=sc.m(1))
        outer_r = r.inflate(4, 4)                      # 2px out each side: no fuse
        sc.bevel_rim(surf, outer_r, rad + 2, (70, 78, 100, 200),
                     (200, 215, 240, 200), w=sc.m(1))
        # full-frame wrap: a cool mid-tone stroke on the bottom arc so the ring
        # reads as a closed frame, not just a top-left emboss.
        _bottom_frame_stroke(surf, outer_r, rad + 2, (150, 165, 200), 150,
                             max(1, sc.m(1)))
        num_gold = True
        coin_tint = None
    else:
        # metal drained to DEAD pewter — clearly not a live cool chrome anymore.
        sc.bevel_rim(surf, r, rad, (30, 34, 50, 160), (110, 115, 130, 140),
                     w=sc.m(1))
        outer_r = r.inflate(4, 4)
        sc.bevel_rim(surf, outer_r, rad + 2, (50, 56, 70, 150),
                     (100, 104, 116, 130), w=sc.m(1))
        _bottom_frame_stroke(surf, outer_r, rad + 2, (78, 84, 100), 110,
                             max(1, sc.m(1)))
        num_gold = False
        coin_tint = (70, 74, 84, 180)                  # clean neutral-grey overlay

    x = r.x + pad
    ccx = x + coin_d // 2
    sc.coin_glyph(surf, ccx, cy, coin_d // 2, rim=(180, 150, 60))
    if coin_tint is not None:
        # coin_glyph() ignores `rim`; a neutral-grey high-alpha tint reads the
        # locked coin unmistakably dead, not merely dim gold.
        cr = coin_d // 2
        tint = pygame.Surface((coin_d, coin_d), pygame.SRCALPHA)
        pygame.draw.circle(tint, coin_tint, (cr, cr), cr)
        surf.blit(tint, (ccx - cr, cy - cr))

    nx = r.x + pad + coin_d + gapc + nw // 2
    if num_gold:
        # glyph-mask pipeline: a bold white mask multiplied by a warm-gold ramp
        # (pale crown -> amber foot) so the numerals read as struck metal without
        # any additive light spilling onto the dark body.
        mask = sc._stamp_bold(sc._glyph_base(text, f, 0), sc.m(1.0))
        grad = sc.vgrad_stops(mask.get_width(), mask.get_height(), 0,
                              [(0.0, (255, 238, 170)), (0.5, (240, 196, 90)),
                               (1.0, (200, 152, 50))], 255, 1.0)
        img = mask.copy()
        img.blit(grad, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        surf.blit(img, img.get_rect(center=(nx, cy)))
    else:
        # value drained: flat slate numerals carry the primary locked-state cue.
        sc.plain_text(surf, text, f, (nx, cy), color=(120, 124, 140),
                      shadow_a=0, weight=sc.m(1.0))
    return r


def draw_card_with_chip(surf, sid, rect, equipped=False, secret=False,
                        affordable=True):
    """draw_card() verbatim, with state_chip() swapped for the chrome-ring chip."""
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
        price_chip_chrome_ring(surf, cx, rect.y + m(88) - sc._CHIP_DY, price,
                               m(20), affordable=affordable)


def chip_native(text, affordable):
    """Draw one chip at native SS onto a tight cropped surface."""
    h = sc.m(20)
    pad = sc.m(6)                                      # room for the outer band
    tmp = pygame.Surface((sc.m(400), h + pad * 2), pygame.SRCALPHA)
    r = price_chip_chrome_ring(tmp, sc.m(200), h // 2 + pad, text, h,
                               affordable=affordable)
    crop = pygame.Rect(r.x - pad, 0, r.w + pad * 2, h + pad * 2)
    return tmp.subsurface(crop).copy()


def zoom_chip(text, affordable, zoom=4):
    sub = chip_native(text, affordable)
    return pygame.transform.smoothscale(
        sub, (sub.get_width() * zoom, sub.get_height() * zoom))


def true1x_chip(text, affordable):
    """The chip at actual gameplay logical size (SS downscaled to 1x)."""
    sub = chip_native(text, affordable)
    w = max(1, round(sub.get_width() / sc.SS))
    h = max(1, round(sub.get_height() / sc.SS))
    return pygame.transform.smoothscale(sub, (w, h))


def verify(text):
    """Pixel-audit an AFFORDABLE chip: the body must stay near-black even with the
    chrome frame composited on top."""
    h = sc.m(20)
    coin_d, pad, gapc, f, nw, w = _chip_geometry(text, h)
    surf = pygame.Surface((w + sc.m(40), h + sc.m(40)), pygame.SRCALPHA)
    cx, cy = surf.get_width() // 2, surf.get_height() // 2
    r = price_chip_chrome_ring(surf, cx, cy, text, h, affordable=True)

    # body sample: the pure-body gap between the coin cell and the numerals
    bx = r.x + pad + coin_d + gapc // 2
    body = surf.get_at((bx, cy))
    print(f"  body gap center: {tuple(body[:3])}")
    assert body[0] < 60 and body[1] < 60 and body[2] < 90, \
        f"Body blown! {tuple(body[:3])}"
    print("  body verified dark: OK")


def main():
    print("verify AFFORDABLE chip:")
    verify("1,100")

    label_lg = hud_font(22, True)
    label_md = hud_font(16, True)
    label_sm = hud_font(13, True)

    cw, ch = sc.CARD_W * sc.SS, sc.CARD_H * sc.SS

    def hero(affordable):
        card = pygame.Surface((cw, ch + 16), pygame.SRCALPHA)
        rect = pygame.Rect(sc.m(sc._INSET), sc.m(sc._INSET),
                           cw - 2 * sc.m(sc._INSET), ch - 2 * sc.m(sc._INSET))
        draw_card_with_chip(card, SID, rect, equipped=False, secret=False,
                            affordable=affordable)
        return card

    card_yes = hero(True)
    card_no = hero(False)

    chip_yes = zoom_chip("1,100", True, zoom=4)
    chip_no = zoom_chip("1,100", False, zoom=4)

    t1_yes = true1x_chip("1,100", True)
    t1_no = true1x_chip("1,100", False)

    MARGIN = 20
    HDR_H = 44
    footer = 34
    col_gap = 30
    card_row_w = cw + col_gap + cw
    W = card_row_w + MARGIN * 2

    def text(surf, s, font_obj, center, col=(232, 236, 248)):
        img = font_obj.render(s, True, col)
        surf.blit(img, img.get_rect(center=center))

    y_cards = HDR_H
    y_striplbl = y_cards + ch + 42
    y_strip = y_striplbl + 20
    strip_h = max(chip_yes.get_height(), chip_no.get_height())
    y_1xlbl = y_strip + strip_h + 24
    y_1x = y_1xlbl + 20
    t1_h = max(t1_yes.get_height(), t1_no.get_height())
    H = y_1x + t1_h + footer

    canvas = pygame.Surface((W, H))
    canvas.fill((8, 8, 20))

    text(canvas, f"v5 price-chip r3 — chrome-ring r2 — {SID} EPIC — P(rim)",
         label_lg, (W // 2, HDR_H // 2))

    cx_yes = MARGIN
    cx_no = MARGIN + cw + col_gap
    canvas.blit(card_yes, (cx_yes, y_cards))
    canvas.blit(card_no, (cx_no, y_cards))
    text(canvas, "AFFORDABLE", label_sm, (cx_yes + cw // 2, y_cards + ch + 12),
         (150, 214, 150))
    text(canvas, "CAN'T AFFORD", label_sm, (cx_no + cw // 2, y_cards + ch + 12),
         (214, 158, 158))

    # 4x detail strip on a card-body gradient patch so the chip is judged on the
    # same dark ground it ships on (not a flat swatch)
    text(canvas, "4× DETAIL (on card-body gradient)", label_md,
         (W // 2, y_striplbl), (150, 156, 178))
    strip_w = chip_yes.get_width() + col_gap + chip_no.get_width()
    sx = (W - strip_w) // 2
    patch_pad = 18
    patch = pygame.Rect(sx - patch_pad, y_strip - patch_pad // 2,
                        strip_w + patch_pad * 2, strip_h + patch_pad)
    canvas.blit(sc.vgrad(patch.w, patch.h, sc.m(sc.CARD_RAD), sc.CARD_T,
                         sc.CARD_B, 255, gamma=1.15), patch.topleft)
    pygame.draw.rect(canvas, (*sc.CARD_RING_BRIGHT, 90), patch,
                     width=1, border_radius=sc.m(sc.CARD_RAD))
    canvas.blit(chip_yes, (sx, y_strip))
    canvas.blit(chip_no, (sx + chip_yes.get_width() + col_gap, y_strip))

    text(canvas, "TRUE 1× (gameplay scale)", label_md, (W // 2, y_1xlbl),
         (150, 156, 178))
    t1_gap = 40
    t1_w = t1_yes.get_width() + t1_gap + t1_no.get_width()
    tx = (W - t1_w) // 2
    canvas.blit(t1_yes, (tx, y_1x + (t1_h - t1_yes.get_height()) // 2))
    canvas.blit(t1_no, (tx + t1_yes.get_width() + t1_gap,
                        y_1x + (t1_h - t1_no.get_height()) // 2))

    text(canvas,
         "dark obsidian · warm-gold numerals · cool-white chrome double-band "
         "frame · locked = pewter · body verified dark",
         label_sm, (W // 2, H - footer // 2), (150, 156, 178))

    out = os.path.join(os.path.dirname(__file__), "..",
                       "docs", "store_card_v5_price_chip_r3",
                       "chrome-ring", "round_2.png")
    out = os.path.abspath(out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(canvas, out)
    print("wrote", out, canvas.get_size())


if __name__ == "__main__":
    main()
