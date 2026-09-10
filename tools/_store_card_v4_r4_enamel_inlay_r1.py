"""enamel-inlay — store_card_v4_r4 concept, round 1 headless render.

Visual thesis: the card floor is a cloisonné / hard-enamel inlay channel.
A jewel-toned, glossy, tier-reactive enamel fill sits inside a thin raised
metal cell wall (the cloisonné border), reading as vitreous wet enamel poured
into a minted metal channel.  The price is not a floating chip — it is its own
tiny cloisonné cell minted into the card body corner: a raised enamel pill
with the same metal wall + gloss construction as the band, so it reads as
built-in by the same process rather than pasted on top.

Headless (SDL dummy) -> a 3-up RARE/EPIC/LEGENDARY review sheet at SS
(324x200 panels, no downscale).  Not wired into the live store; writes
docs/store_card_v4_r4/enamel-inlay/round_1.png.
"""
import os

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import sys

sys.path.insert(0, "/home/user/skybit")

import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from game import store_catalog
from game.hud import _font
from game.store_cards import (
    cabochon, cabochon_glass, blit_thumb, facet_gem,
    vgrad, vgrad_stops, drop_shadow, bevel_rim, top_sheen, contact_shadow,
    plain_text, font, m, SS, soft_glow, coin_glyph, _glyph_base,
    CARD_T, CARD_B, CARD_RING_BRIGHT, CARD_RING_DEEP,
    CABO_LO, CABO_HI, GEM_R, RARITY, MYSTERY, _rarity,
    lerp_color, WHITE, NEAR_BLACK,
)

# LOCKED card constants (from store_cards).
CARD_W, CARD_H = 162, 100
CARD_RAD = 17
_INSET = 6

# Hero disc: R=36, left-leaning.
R = 36


def _enamel_stops(pal):
    """Tier-reactive glossy enamel ramp: gem hue dark-shifted toward near-black
    so the channel reads as deep vitreous colour with body, not a flat panel."""
    return [
        (0.0, lerp_color(pal["gem"], (2, 2, 6), 0.55)),
        (1.0, lerp_color(pal["gem"], (2, 2, 6), 0.72)),
    ]


def _enamel_band(big, rect, plinth_top, rad, pal):
    """Draw the cloisonné enamel channel across the card floor.

    Order sells the glass: deep jewel fill -> broad gloss ramp over the top
    third -> a tight specular hotspot -> the raised metal cell wall that
    contains the poured enamel, with a 1px dark inner shadow so the wall reads
    as standing proud of the enamel surface."""
    bx, by = rect.left, plinth_top
    bw = rect.w
    bh = rect.bottom - plinth_top

    # Rounded-bottom mask matching the card's lower corners so the poured
    # enamel — and its bright metal wall — seat flush into the shell rather than
    # nubbing square corners past the card's radius.  The full card rect is
    # shifted up so its rounded bottom aligns with the band's bottom row.
    moff = rect.y - plinth_top
    body_mask = pygame.Surface((bw, bh), pygame.SRCALPHA)
    pygame.draw.rect(body_mask, (255, 255, 255, 255),
                     (0, moff, bw, rect.h), border_radius=rad)

    # Deep vitreous jewel fill.
    fill = vgrad_stops(bw, bh, 0, _enamel_stops(pal), 255, gamma=1.05)
    fill.blit(body_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(fill, (bx, by))

    # Broad gloss highlight over the top third — a white-tinted vertical ramp
    # (peak alpha 45) blitted additively for the wet-enamel sheen of poured glass.
    gh = int(bh * 0.36)
    gloss = pygame.Surface((bw, gh), pygame.SRCALPHA)
    for y in range(gh):
        a = int(45 * (1 - y / max(1, gh - 1)) ** 1.4)
        pygame.draw.line(gloss, (255, 255, 255, a), (0, y), (bw - 1, y))
    gloss.blit(body_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(gloss, (bx, by), special_flags=pygame.BLEND_ADD)

    # Specular hotspot — a small oval of near-white glow so the surface reads
    # as glass catching a point light rather than matte paint.
    spec = pygame.Surface((bw, bh), pygame.SRCALPHA)
    soft_glow(spec, int(bw * 0.30), int(bh * 0.30), m(15),
              (250, 250, 255), 36, layers=6)
    # Squash to an oval — wider than tall — by scaling the glow vertically.
    spec = pygame.transform.smoothscale(spec, (bw, int(bh * 0.72)))
    smask = pygame.Surface(spec.get_size(), pygame.SRCALPHA)
    pygame.draw.rect(smask, (255, 255, 255, 255),
                     (0, moff, bw, rect.h), border_radius=rad)
    spec.blit(smask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(spec, (bx, by), special_flags=pygame.BLEND_ADD)

    # Raised cloisonné metal wall — the cell border that contains the channel.
    # Drawn square (border_radius=0) for a minted-channel edge, then clipped to
    # the rounded-bottom mask so it doesn't nub past the card's corners.
    wall = pygame.Surface((bw, bh), pygame.SRCALPHA)
    ww = max(1, m(1.5))
    pygame.draw.rect(wall, (*CARD_RING_BRIGHT, 200), (0, 0, bw, bh),
                     width=ww, border_radius=0)
    # Dark inner shadow one px inside the wall — the wall stands proud of enamel.
    pygame.draw.rect(wall, (4, 5, 14, 170), (ww, ww, bw - 2 * ww, bh - 2 * ww),
                     width=max(1, m(1)), border_radius=0)
    wall.blit(body_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(wall, (bx, by))


def _price_cell(big, cx, cy, price, pal):
    """A tiny cloisonné numeral cell minted into the card body: darkened enamel
    fill, raised metal wall border, gloss strip across the top, price numeral
    engraved in near-white.  Same construction as the band so it reads as part
    of the mint, not a floating chip."""
    f = font(7.5)
    txt = f"{price}"                                 # no comma — compact at 162px
    nw = _glyph_base(txt, f, 0).get_width()
    padx = m(6)
    pady = m(4)
    w = nw + padx * 2
    h = _glyph_base(txt, f, 0).get_height() + pady * 2
    x0, y0 = cx - w // 2, cy - h // 2
    rad = m(3)

    # Drop shadow so the raised pill sits above the card body.
    sh = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 150), (0, 0, w, h), border_radius=rad)
    big.blit(sh, (x0, y0 + m(2)))

    # Deep enamel fill (same tier-reactive logic as the band).
    fill = vgrad_stops(w, h, rad, _enamel_stops(pal), 255, gamma=1.05)
    big.blit(fill, (x0, y0))

    # Gloss strip across the top for the wet-enamel read.
    gh = int(h * 0.42)
    gloss = pygame.Surface((w, gh), pygame.SRCALPHA)
    for y in range(gh):
        a = int(50 * (1 - y / max(1, gh - 1)) ** 1.3)
        pygame.draw.line(gloss, (255, 255, 255, a), (0, y), (w - 1, y))
    gmask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(gmask, (255, 255, 255, 255), (0, 0, w, h), border_radius=rad)
    gloss.blit(gmask.subsurface((0, 0, w, gh)), (0, 0),
               special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(gloss, (x0, y0), special_flags=pygame.BLEND_ADD)

    # Raised metal wall border — the cloisonné cell edge.
    pygame.draw.rect(big, (*CARD_RING_BRIGHT, 220), (x0, y0, w, h),
                     width=max(1, m(1)), border_radius=rad)

    # Engraved near-white numeral.
    plain_text(big, txt, f, (cx, cy),
               lerp_color(WHITE, (240, 240, 255), 0.2), shadow_a=0,
               weight=m(0.8), keyline=(6, 6, 16), kw=m(0.8))


def _name_on_band(big, name, cx, cy, max_w):
    """Near-white name engraved into the enamel surface, auto-shrunk to fit and
    given a hard dark keyline so it stays legible over the glossy jewel fill."""
    sz = 12.0
    f = font(sz)
    while _glyph_base(name, f, 0).get_width() > max_w and sz > 7.0:
        sz -= 0.5
        f = font(sz)
    plain_text(big, name, f, (cx, cy), (230, 225, 240), shadow_a=150,
               weight=m(0.95), keyline=(4, 4, 12), kw=m(1.0))


def render_card(sid):
    """Draw ONE enamel-inlay card onto a fresh SS panel (324x200) and return it."""
    pal = RARITY.get(_rarity(sid), MYSTERY)
    name = store_catalog.name(sid)
    price = store_catalog.cost(sid)

    big = pygame.Surface((CARD_W * SS, CARD_H * SS), pygame.SRCALPHA)
    rect = pygame.Rect(m(_INSET), m(_INSET),
                       CARD_W * SS - 2 * m(_INSET), CARD_H * SS - 2 * m(_INSET))
    rad = m(CARD_RAD)

    # ── SHELL (locked order) ──
    drop_shadow(big, rect, rad, blur=m(8), alpha=160, dy=m(4))
    big.blit(vgrad(rect.w, rect.h, rad, CARD_T, CARD_B, 252, gamma=1.15),
             rect.topleft)
    top_sheen(big, rect, rad, m(30), peak=62)
    contact_shadow(big, rect, rad, m(9), alpha=120)
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 235),
              w=max(1, m(2.0)))

    # ── LOCKED positional skeleton ──
    cx = rect.left + m(40)
    cy = rect.y + m(38)
    plinth_top = rect.y + m(72)

    # ── ENAMEL BAND — cloisonné inlay channel across the card floor. ──
    _enamel_band(big, rect, plinth_top, rad, pal)

    # ── HERO DISC (R=36, left-leaning; base seats into the enamel channel) ──
    soft_glow(big, cx, cy, m(R + 4), pal["glow"], 30, layers=8)
    cabochon(big, cx, cy, m(R), CABO_LO, CABO_HI, ring=pal["gem"], ring_a=50)
    blit_thumb(big, sid, cx, cy, int(m(R) * 1.5))
    cabochon_glass(big, cx, cy, m(R), tint=pal["gem"])

    # ── GEM CREST (locked call) ──
    facet_gem(big, rect.right - m(19), rect.y + m(19), m(GEM_R + 3),
              pal["gem"], pal["deep"])

    # ── PRICE — raised enamel numeral cell minted into the upper-right body. ──
    _price_cell(big, rect.right - m(23), rect.y + m(48), price, pal)

    # ── NAME — near-white, engraved into the enamel band. ──
    _name_on_band(big, name.upper(), rect.centerx, rect.y + m(81),
                  rect.w - m(22))

    return big


# ── review sheet ──────────────────────────────────────────────────────────────
VARIANTS = [
    ("RARE",      "skin_tophat"),
    ("EPIC",      "skin_prism"),
    ("LEGENDARY", "skin_kitsune"),
]

PANEL_W, PANEL_H = CARD_W * SS, CARD_H * SS
MARGIN = 10
GUTTER = 8
HEADER_H = 26
FOOTER_H = 22

sheet_w = MARGIN * 2 + PANEL_W * 3 + GUTTER * 2
sheet_h = MARGIN + HEADER_H + PANEL_H + FOOTER_H + MARGIN
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((8, 8, 20))

hfont = _font(20, True)
ffont = _font(18, True)
htxt = hfont.render("store_card_v4_r4 — enamel-inlay — round 1", True,
                    (236, 232, 214))
sheet.blit(htxt, (MARGIN, MARGIN + (HEADER_H - htxt.get_height()) // 2))

panel_y = MARGIN + HEADER_H
for i, (tier, sid) in enumerate(VARIANTS):
    px = MARGIN + i * (PANEL_W + GUTTER)
    panel = render_card(sid)
    sheet.blit(panel, (px, panel_y))
    ftxt = ffont.render(tier, True, (218, 214, 200))
    sheet.blit(ftxt, (px + (PANEL_W - ftxt.get_width()) // 2,
                      panel_y + PANEL_H + (FOOTER_H - ftxt.get_height()) // 2))

out = "/home/user/skybit/docs/store_card_v4_r4/enamel-inlay/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())
