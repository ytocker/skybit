import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
import math, sys
sys.path.insert(0, "/home/user/skybit")
import pygame
pygame.init()
pygame.display.set_mode((1, 1))
from game import store_catalog
from game.hud import _font
from game.store_cards import (
    cabochon, cabochon_glass, blit_thumb, facet_gem,
    vgrad, vgrad_stops, drop_shadow, bevel_rim, top_sheen, contact_shadow,
    plain_text, font, m, SS, soft_glow, _glyph_base, _stamp_bold,
    CARD_T, CARD_B, CARD_RING_BRIGHT, CARD_RING_DEEP,
    CABO_LO, CABO_HI, GEM_R, RARITY, MYSTERY, _rarity,
    lerp_color, WHITE, NEAR_BLACK,
)

CARD_W, CARD_H = 162, 100
CARD_RAD = 17
_INSET = 6
R = 36


def _neutral_band(big, rect, plinth_top, rad):
    ph = rect.bottom - plinth_top
    band = vgrad_stops(rect.w, ph, 0,
                       [(0.0, (28, 24, 44)), (1.0, (14, 12, 26))], 255)
    mask = pygame.Surface((rect.w, ph), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255),
                     (0, plinth_top - rect.bottom, rect.w, rect.h),
                     border_radius=rad)
    band.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(band, (rect.left, plinth_top))
    seam = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.line(seam, (*CARD_RING_BRIGHT, 80),
                     (rect.left, plinth_top - max(1, m(1))),
                     (rect.right - 1, plinth_top - max(1, m(1))), max(1, m(1)))
    big.blit(seam, (0, 0))
    pygame.draw.line(big, (6, 5, 12), (rect.left, plinth_top),
                     (rect.right - 1, plinth_top), max(1, m(1)))


def _simple_price(big, cx, cy, price, pal):
    f = font(9.0)
    txt = f"{price}"
    nw = _glyph_base(txt, f, 0).get_width()
    ar = nw // 2 + m(6)
    rimbox = pygame.Rect(cx - ar, cy - ar, ar * 2, ar * 2)
    arc = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.arc(arc, (*CARD_RING_BRIGHT, 140), rimbox,
                    math.radians(60), math.radians(210), max(1, m(1)))
    big.blit(arc, (0, 0))
    plain_text(big, txt, f, (cx, cy),
               lerp_color(pal["gem"], WHITE, 0.25), shadow_a=0, weight=m(0.9))


def _tier_bed(w, h, inner, outer, alpha=230):
    """The luminous card body that reads THROUGH the punched voids. A NORMAL-alpha
    radial (bright tier centre -> deep tier edge) — NOT additive — so it never
    stacks toward white and every tier keeps its own chroma in the letter holes.
    The full rect is floored to `outer` first so edge letters over the plate
    corners still reveal tier colour, never bare card body."""
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    surf.fill((*outer, alpha))
    cx, cy = w // 2, h // 2
    maxr = max(1, int(math.hypot(cx, cy)))
    for i in range(maxr, 0, -1):
        t = i / maxr                               # 1 at rim .. 0 at centre
        col = lerp_color(inner, outer, t)
        pygame.draw.circle(surf, (*col, alpha), (cx, cy), i)
    return surf


def _name_negative_cutout(big, name, cx, plinth_top, rect_bottom, max_plate_w, pal):
    # Floor sz at 10.5 so counters stay >=4 device px, and let the BAND HEIGHT
    # (not just width) drive the shrink so the plate never overhangs the 26px
    # slot between the disc plinth and the card's bottom margin.
    slot_bot = rect_bottom - m(3)                  # keep a real bottom margin
    slot_h = slot_bot - plinth_top
    padx, pady = m(6), m(2.5)
    sz = 13.5
    while True:
        f = font(sz)
        raw = _glyph_base(name, f, m(0.6))
        # ~1 device-px even faux-bold growth: the shared helper scales its input
        # by ~0.42 and caps at 1px, so m(1.5) is the smallest nominal weight that
        # actually thickens the strokes (and thus widens the voids) at SS=2.
        stamped = _stamp_bold(raw, m(1.5))
        bb = stamped.get_bounding_rect()           # hug the caps, not the line box
        base = stamped.subsurface(bb).copy() if bb.width and bb.height else stamped
        bw, bh = base.get_size()
        pw, ph = bw + padx * 2, bh + pady * 2
        if (pw <= max_plate_w and ph <= slot_h) or sz <= 10.5:
            break
        sz -= 0.5

    # Tier-coloured opaque plate — the material the letters are punched out of.
    plate = vgrad_stops(pw, ph, m(3),
                        [(0.0, lerp_color(pal["gem"], WHITE, 0.20)),
                         (1.0, pal["deep"])], 255, gamma=1.1)
    gx, gy = padx, pady

    # Deboss: a dark copy pushed toward the top-left shadow and a bright copy
    # toward the bottom-right highlight, offset a visible ~1.5 device px so the
    # void reads as pressed INTO the plate rather than a flat sticker hole. The
    # bevel deltas run to true shadow / a hot tier-white so the emboss survives
    # the downscale.
    off = m(1.5)
    dark_g = base.copy()
    dark_g.fill((10, 8, 18, 255), special_flags=pygame.BLEND_RGBA_MULT)
    bright_g = base.copy()
    bright_g.fill((*lerp_color(pal["gem"], WHITE, 0.6), 255),
                  special_flags=pygame.BLEND_RGBA_MULT)
    plate.blit(dark_g,   (gx - off, gy - off))
    plate.blit(bright_g, (gx + off, gy + off))

    # BLEND_RGBA_SUB drops plate alpha to 0 wherever the glyph is opaque,
    # cutting true letter-shaped holes rather than painting dark ink.
    plate.blit(base, (gx, gy), special_flags=pygame.BLEND_RGBA_SUB)

    # Anchor to the bottom margin so the plate clears as much of the disc as the
    # thin band allows while guaranteeing >=m(3) below.
    plate_rect = pygame.Rect(cx - pw // 2, slot_bot - ph, pw, ph)

    # A capped additive halo (never clips white) blooms the tier colour onto the
    # band around the plate; the chromatic bed then carries the glow through the
    # voids themselves.
    soft_glow(big, plate_rect.centerx, plate_rect.centery, m(20),
              pal["glow"], 20, layers=3)
    bed = _tier_bed(pw, ph, lerp_color(pal["gem"], WHITE, 0.15), pal["deep"], 230)
    big.blit(bed, plate_rect.topleft)

    big.blit(plate, plate_rect.topleft)
    # Bevel rim ON TOP of the plate = its own separation from the band; no
    # neutralising contact-shadow rect over the void field.
    bevel_rim(big, plate_rect, m(3), CARD_RING_DEEP,
              (*CARD_RING_BRIGHT, 150), w=max(1, m(1)))

    # Report a void sample point (mid-height, inside a stroke) for verification.
    mid = base.get_height() // 2
    for frac in (0.5, 0.28, 0.72):
        c0 = int(base.get_width() * frac)
        for dx in range(0, m(8)):
            for xx in (c0 + dx, c0 - dx):
                if 0 <= xx < base.get_width() and base.get_at((xx, mid))[3] > 220:
                    return plate_rect, (plate_rect.left + gx + xx,
                                        plate_rect.top + gy + mid)
    return plate_rect, plate_rect.center


def render_card(sid):
    pal = RARITY.get(_rarity(sid), MYSTERY)
    name = store_catalog.name(sid)
    price = store_catalog.cost(sid)
    big = pygame.Surface((CARD_W * SS, CARD_H * SS), pygame.SRCALPHA)
    rect = pygame.Rect(m(_INSET), m(_INSET),
                       CARD_W * SS - 2 * m(_INSET), CARD_H * SS - 2 * m(_INSET))
    rad = m(CARD_RAD)
    drop_shadow(big, rect, rad, blur=m(8), alpha=160, dy=m(4))
    big.blit(vgrad(rect.w, rect.h, rad, CARD_T, CARD_B, 252, gamma=1.15), rect.topleft)
    top_sheen(big, rect, rad, m(30), peak=62)
    contact_shadow(big, rect, rad, m(9), alpha=120)
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 235), w=max(1, m(2.0)))
    cx = rect.left + m(40)
    cy = rect.y + m(38)
    plinth_top = rect.y + m(72)
    _neutral_band(big, rect, plinth_top, rad)
    soft_glow(big, cx, cy, m(R + 4), pal["glow"], 30, layers=8)
    cabochon(big, cx, cy, m(R), CABO_LO, CABO_HI, ring=pal["gem"], ring_a=50)
    blit_thumb(big, sid, cx, cy, int(m(R) * 1.5))
    cabochon_glass(big, cx, cy, m(R), tint=pal["gem"])
    facet_gem(big, rect.right - m(19), rect.y + m(19), m(GEM_R + 3), pal["gem"], pal["deep"])
    _simple_price(big, rect.right - m(23), rect.y + m(48), price, pal)
    plate_rect, void_pt = _name_negative_cutout(
        big, name.upper(), rect.centerx, plinth_top, rect.bottom,
        rect.w - m(16), pal)
    return big, rect, plinth_top, plate_rect, void_pt


VARIANTS = [("RARE", "skin_tophat"), ("EPIC", "skin_prism"), ("LEGENDARY", "skin_kitsune")]
PANEL_W, PANEL_H = CARD_W * SS, CARD_H * SS
MARGIN, GUTTER, HEADER_H, FOOTER_H = 10, 8, 26, 22
sheet_w = MARGIN * 2 + PANEL_W * 3 + GUTTER * 2
sheet_h = MARGIN + HEADER_H + PANEL_H + FOOTER_H + MARGIN
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((8, 8, 20))
hfont = _font(20, True); ffont = _font(18, True)
htxt = hfont.render("store_card_v4_r4_name — negative-cutout — round 2", True, (236, 232, 214))
sheet.blit(htxt, (MARGIN, MARGIN + (HEADER_H - htxt.get_height()) // 2))
panel_y = MARGIN + HEADER_H
report = []
for i, (tier, sid) in enumerate(VARIANTS):
    px = MARGIN + i * (PANEL_W + GUTTER)
    big, rect, plinth_top, plate_rect, void_pt = render_card(sid)
    sheet.blit(big, (px, panel_y))
    voidc = big.get_at(void_pt)
    spread = max(voidc[0], voidc[1], voidc[2]) - min(voidc[0], voidc[1], voidc[2])
    report.append((tier, plate_rect, rect.bottom, plinth_top, tuple(voidc), spread))
    ftxt = ffont.render(tier, True, (218, 214, 200))
    sheet.blit(ftxt, (px + (PANEL_W - ftxt.get_width()) // 2,
                      panel_y + PANEL_H + (FOOTER_H - ftxt.get_height()) // 2))
out = "/home/user/skybit/docs/store_card_v4_r4_name/negative-cutout/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())
print("--- verification ---")
for tier, pr, rb, pt, vc, spread in report:
    print(f"{tier:10s} plate.top={pr.top:4d} plinth_top={pt:4d} "
          f"plate.bottom={pr.bottom:4d} rect.bottom={rb:4d} "
          f"inside={pr.top >= pt and pr.bottom <= rb} "
          f"void_rgb={vc[:3]} chroma_spread={spread}")
