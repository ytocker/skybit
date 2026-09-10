import os, sys
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import math
import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)
import game.store_cards as sc
from game.hud import _font as hud_font


# ── the recessed-coin-well price chip ─────────────────────────────────────────
def recessed_coin_well_chip(surf, cx, cy, text, h, affordable=True):
    """Layered relief inside ONE pill: only the coin socket is debossed while the
    pill body reads flat-dark at mid level (not as sunken as a full obsidian
    slot). A dark arc across the coin's upper edge + a bright catch-light arc
    under it reads as a coin DROPPED into a socket — the whole depth story sits
    in that one concave cell, so the rest of the pill stays a calm raised chip."""
    coin_d = int(h * 0.66)
    pad = sc.m(13)
    gapc = sc.m(8)                                    # clear gap: socket -> digits
    f = sc.font(h * 0.50 / sc.SS)
    nw = sc._glyph_base(text, f, 0).get_width() + sc.m(2)  # account for faux-bold
    w = pad + coin_d + gapc + nw + pad
    r = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
    radius = h // 2

    # Raised pill body: mid-dark, low gloss so it never reads as sunken. The
    # depth cue is reserved entirely for the coin socket below.
    sc.drop_shadow(surf, r, radius, blur=sc.m(4), alpha=110, dy=sc.m(2))
    surf.blit(sc.vgrad_stops(r.w, r.h, radius,
                             [(0.0, (34, 36, 58)), (1.0, (26, 28, 46))], 255,
                             gamma=1.05), r.topleft)
    sc.gloss_sweep(surf, r, radius, peak=25)
    sc.contact_shadow(surf, r, radius, sc.m(3), alpha=80)
    # standard double rim: dark keyline under a faint top-left bevel
    pygame.draw.rect(surf, (4, 5, 16), r, width=max(1, sc.m(1.6)),
                     border_radius=radius)
    sc.bevel_rim(surf, r, radius, (4, 5, 16), (*sc.CARD_RING_BRIGHT, 80),
                 w=max(1, sc.m(1)))

    # THE STAR MOVE — a concave socket ringing the coin. Shadow arc hugs the
    # coin's upper edge, a thin warm catch-light arc hugs the lower edge; drawn
    # BEFORE the coin so the coin overlays the arc line and reads dropped-in.
    coin_r = coin_d // 2
    coin_cx = r.x + pad + coin_r
    coin_cy = cy
    coin_rect = pygame.Rect(coin_cx - coin_r - sc.m(1), coin_cy - coin_r - sc.m(1),
                            (coin_r + sc.m(1)) * 2, (coin_r + sc.m(1)) * 2)
    shadow_surf = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.arc(shadow_surf, (0, 0, 0, 140), coin_rect,
                    math.radians(20), math.radians(160), max(2, sc.m(2)))
    surf.blit(shadow_surf, (0, 0))
    catch_a = 120 if affordable else 40
    catch_surf = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.arc(catch_surf, (255, 240, 180, catch_a), coin_rect,
                    math.radians(200), math.radians(340), max(1, sc.m(1)))
    surf.blit(catch_surf, (0, 0))

    coin_rim = sc.GOLD_A_COIN_RIM if affordable else (80, 86, 104)
    sc.coin_glyph(surf, coin_cx, coin_cy, coin_r, rim=coin_rim)

    # matte numerals — warm gold when affordable, cool grey when not — no shadow
    num_col = (228, 196, 120) if affordable else (150, 158, 178)
    x = r.x + pad + coin_d + gapc
    sc.plain_text(surf, text, f, (x + nw // 2, cy), num_col, shadow_a=0,
                  weight=sc.m(1.0))
    return r


# ── the card, drawn with the new chip swapped in for state_chip ───────────────
def draw_card_with_chip(surf, sid, rect, equipped, secret, affordable=True):
    """Body-for-body copy of sc.draw_card() with the state_chip() call replaced by
    the recessed-coin-well chip so the concept reads in its true context."""
    pal = sc.MYSTERY if secret else sc.RARITY[sc._rarity(sid)]
    rad = sc.m(sc.CARD_RAD)
    sc.drop_shadow(surf, rect, rad, blur=sc.m(8), alpha=160, dy=sc.m(4))
    surf.blit(sc.vgrad(rect.w, rect.h, rad, sc.CARD_T, sc.CARD_B, 252, gamma=1.15),
              rect.topleft)
    sc.top_sheen(surf, rect, rad, sc.m(30), peak=62)
    sc.contact_shadow(surf, rect, rad, sc.m(9), alpha=120)
    pygame.draw.rect(surf, (4, 5, 16), rect, width=max(1, sc.m(2)), border_radius=rad)
    sc.bevel_rim(surf, rect, rad, sc.CARD_RING_DEEP, (*sc.CARD_RING_BRIGHT, 235),
                 w=max(1, sc.m(2.0)))
    tray = rect.inflate(-sc.m(7), -sc.m(7))
    trad = rad - sc.m(4)
    pygame.draw.rect(surf, (10, 10, 24, 200), tray.inflate(sc.m(2), sc.m(2)),
                     width=max(1, sc.m(1)), border_radius=trad + sc.m(1))
    pygame.draw.rect(surf, (*sc.CARD_RING_BRIGHT, 90), tray, width=max(1, sc.m(1)),
                     border_radius=trad)

    cx, cy = rect.centerx, rect.y + sc.m(sc.CY_DISC) + sc._DOME_DY
    sc.soft_glow(surf, cx, cy, sc._DOME_R + sc.m(3), pal["glow"], 30, layers=8)
    sc.cabochon(surf, cx, cy, sc._DOME_R, sc.CABO_LO, sc.CABO_HI, ring=pal["gem"],
                ring_a=50)
    if secret:
        sc._draw_qmark(surf, cx, cy, sc._DOME_R + sc.m(6), sc.CREAM, sc.NEAR_BLACK,
                       thick=sc.m(2))
        name = "???"
    else:
        name = sc._name(sid)
    sc.cabochon_glass(surf, cx, cy, sc._DOME_R, tint=pal["gem"])
    if not secret:
        sc.blit_thumb(surf, sid, cx, cy - sc._ITEM_DY, sc._BOX_PX)

    sc.facet_gem(surf, rect.right - sc.m(19), rect.y + sc.m(19), sc.m(sc.GEM_R + 3),
                 pal["gem"], pal["deep"], mystery=secret)

    tier_word = "MYSTERY" if secret else sc._rarity(sid).upper()
    sc._ribbon_lozenge(surf, tier_word, cx, rect.y + sc.m(55) - sc._RIBN_DY,
                       rect.w - sc.m(34), pal)
    sc._name_on(surf, name, cx, rect.y + sc.m(70), rect.w - sc.m(26))
    price = sc._cost(sid)
    recessed_coin_well_chip(surf, cx, rect.y + sc.m(88) - sc._CHIP_DY,
                            f"{price:,}", sc.m(20), affordable=affordable)


# ── review-sheet render ───────────────────────────────────────────────────────
def _render_full_card(sid, affordable=True):
    big = pygame.Surface((sc.CARD_W * sc.SS, sc.CARD_H * sc.SS), pygame.SRCALPHA)
    rect = pygame.Rect(sc.m(sc._INSET), sc.m(sc._INSET),
                       sc.CARD_W * sc.SS - 2 * sc.m(sc._INSET),
                       sc.CARD_H * sc.SS - 2 * sc.m(sc._INSET))
    draw_card_with_chip(big, sid, rect, equipped=False, secret=False,
                        affordable=affordable)
    return big


def _render_chip_crop(text, affordable):
    """Draw the chip on a generous transparent field, then crop tight to its
    rect (inflated a little so shadow + rim survive) for a zoomed detail view."""
    field = pygame.Surface((sc.m(160), sc.m(70)), pygame.SRCALPHA)
    r = recessed_coin_well_chip(field, sc.m(80), sc.m(35), text, sc.m(20),
                                affordable=affordable)
    pad = sc.m(6)
    crop = r.inflate(pad * 2, pad * 2).clip(field.get_rect())
    return field.subsurface(crop).copy()


def build_sheet():
    bg = (8, 8, 20)
    margin = 20
    header = 44
    footer = 36
    zoom = 4

    card = _render_full_card("skin_mummy", affordable=True)
    cw, ch = card.get_size()

    aff = _render_chip_crop("1,100", True)
    aff = pygame.transform.scale(aff, (aff.get_width() * zoom // 2,
                                       aff.get_height() * zoom // 2))
    naf = _render_chip_crop("1,100", False)
    naf = pygame.transform.scale(naf, (naf.get_width() * zoom // 2,
                                       naf.get_height() * zoom // 2))

    strip_gap = 48
    strip_w = aff.get_width() + strip_gap + naf.get_width()
    content_w = max(cw, strip_w)
    W = content_w + margin * 2

    label_h = 26
    gap_card_strip = 34
    strip_h = max(aff.get_height(), naf.get_height())
    H = header + ch + gap_card_strip + label_h + strip_h + label_h + footer

    surf = pygame.Surface((W, H))
    surf.fill(bg)

    title = hud_font(22, True)
    sub = hud_font(14, False)
    lbl = hud_font(16, True)

    def _text(s, txt, font_obj, center, col):
        img = font_obj.render(txt, True, col)
        s.blit(img, img.get_rect(center=center))

    _text(surf, "PRICE CHIP  ·  recessed-coin-well  ·  round 1", title,
          (W // 2, 20), (238, 232, 214))
    _text(surf, "dropped-coin-into-slot — only the coin socket is debossed",
          sub, (W // 2, 38), (150, 156, 178))

    # full card
    cy = header
    surf.blit(card, ((W - cw) // 2, cy))

    # zoomed chip strip
    ly = cy + ch + gap_card_strip
    _text(surf, "AFFORDABLE", lbl, ((W - strip_w) // 2 + aff.get_width() // 2,
                                    ly + label_h // 2), (210, 190, 130))
    _text(surf, "CAN'T AFFORD", lbl,
          ((W - strip_w) // 2 + aff.get_width() + strip_gap + naf.get_width() // 2,
           ly + label_h // 2), (150, 158, 178))
    sy = ly + label_h
    sx = (W - strip_w) // 2
    surf.blit(aff, (sx, sy + (strip_h - aff.get_height()) // 2))
    surf.blit(naf, (sx + aff.get_width() + strip_gap,
                    sy + (strip_h - naf.get_height()) // 2))

    _text(surf, "shadow arc above + warm catch-light below = coin dropped INTO a socket",
          sub, (W // 2, sy + strip_h + footer // 2 + 4), (150, 156, 178))
    return surf


if __name__ == "__main__":
    out = "/home/user/skybit/docs/store_card_v5_price_chip/recessed-coin-well/round_1.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    sheet = build_sheet()
    pygame.image.save(sheet, out)
    print("saved", out, sheet.get_size())
