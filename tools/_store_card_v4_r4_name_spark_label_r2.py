"""spark-label — store_card_v4_r4_name concept, round 2 headless render.

Ports Skybit's in-game "+N" float-text vocabulary onto the store card NAME so the
card reads as the same visual family as the in-game coin/power-up feedback.  The
name treatment is the focus; the rest of the card is the shared v4_r4 base kept
deliberately neutral so the name reads:

  * Band  — flat dark indigo vgrad (no material story competing with the name).
  * Price — a simple struck numeral with a thin mint arc.
  * Name  — tier-gradient fill through the glyph + deep blocky outline + a few
            tier-glow sparkle dots, mirroring FloatText._draw_powerup
            (gradient / outline / sparkle) in game/entities.py.

Round 2 addresses the art-director notes: sparkles are seeded only into the empty
band flanking the word (never on the glyphs, never off-card), the tier gradient
carries real top-to-bottom value travel on every tier (LEGENDARY included), and
the word is sized down so it sits in the band with breathing room above and below.
"""
import os

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import math
import random
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
    """Flat dark-indigo plinth — intentionally featureless so the spark-label
    name is the only thing competing for attention on the lower band."""
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
    """Plain struck numeral with a thin mint arc — kept minimal so the name owns
    the float-text vocabulary."""
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


def _name_spark_label(big, name, cx, max_w, pal, sid, rect, plinth_top):
    """The focus: FloatText '+N' recipe applied to the item name — tier-gradient
    fill, deep blocky outline, and a handful of tier-glow sparkle dots.  Sizing
    lands the word inside the plinth band with breathing room, and the sparkles
    are seeded only into the empty flanks so they read as twinkle, never as dirt
    on the letterforms."""
    # True band center so the word sits centred between seam and card foot.
    cy = plinth_top + (rect.bottom - plinth_top) // 2

    # Start smaller than r1 so glyphs clear the band edges with ~m(2) top/bottom.
    sz = 11.5
    f = font(sz)
    tracking = m(0.3)
    while _glyph_base(name, f, tracking).get_width() > max_w and sz > 9.5:
        sz -= 0.5
        f = font(sz)
    base = _glyph_base(name, f, tracking)
    bw, bh = base.get_size()

    # Drop shadow seats the label above the band.
    sh = base.copy()
    sh.fill((4, 4, 12, 255), special_flags=pygame.BLEND_RGBA_MULT)
    sh.set_alpha(150)
    big.blit(sh, base.get_rect(center=(cx, cy + m(2))))

    # Blocky deep outline — tier deep colour stamped at the 8 surrounding offsets.
    # Offset trimmed to m(1.25) (from m(1.5)) because the smaller glyphs would
    # otherwise clog the E/A/N/R counters once the card downsamples to 1x; the
    # 8-direction stamp still carries the float-text vocabulary.
    off = int(m(1.25))
    outline = base.copy()
    outline.fill((*pal["deep"], 255), special_flags=pygame.BLEND_RGBA_MULT)
    for dx in (-off, 0, off):
        for dy in (-off, 0, off):
            if dx == 0 and dy == 0:
                continue
            big.blit(outline, base.get_rect(center=(cx + dx, cy + dy)))

    # Vertical tier gradient masked to the glyph.  Stops carry real value travel
    # (>=40 lum top-to-bottom on every tier, LEGENDARY included) so the fill reads
    # as lit metal rather than flat colour.
    grad = vgrad_stops(bw, bh, 0,
                       [(0.0, lerp_color(pal["gem"], WHITE, 0.58)),
                        (1.0, lerp_color(pal["gem"], pal["deep"], 0.28))], 255)
    grad.blit(base, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    big.blit(grad, grad.get_rect(center=(cx, cy)))

    # Sparkles: seed only in the empty band flanking the word.  The glyph bbox is
    # excluded outright and every dot Y is clamped between the seam and the card
    # foot, so no dot can land on a letterform or spill off the card.
    glyph_rect = pygame.Rect(cx - bw // 2, cy - bh // 2, bw, bh).inflate(
        int(m(2)) * 2, int(m(2)) * 2)
    y_lo = plinth_top + m(2)
    y_hi = rect.bottom - m(2)
    x_lo = rect.left + m(2)
    x_hi = rect.right - m(2)

    rng = random.Random(hash((name, sid)) & 0xffffffff)
    placed = []
    attempts = 0
    want = 6 if (glyph_rect.left - x_lo) >= m(6) and (x_hi - glyph_rect.right) >= m(6) else 4
    while len(placed) < want and attempts < 400:
        attempts += 1
        sx = rng.randint(x_lo, x_hi)
        sy = rng.randint(y_lo, y_hi)
        if glyph_rect.collidepoint(sx, sy):
            continue
        # Keep dots from clustering on top of one another.
        if any((sx - px) ** 2 + (sy - py) ** 2 < (m(4)) ** 2 for px, py in placed):
            continue
        placed.append((sx, sy))

    for sx, sy in placed:
        pygame.draw.circle(big, (*pal["glow"], 255), (sx, sy), max(1, m(1)))
        pygame.draw.circle(big, (255, 255, 255, 255), (sx, sy), max(1, m(0.5)))


def render_card(sid):
    pal = RARITY.get(_rarity(sid), MYSTERY)
    name = store_catalog.name(sid)
    price = store_catalog.cost(sid)

    big = pygame.Surface((CARD_W * SS, CARD_H * SS), pygame.SRCALPHA)
    rect = pygame.Rect(m(_INSET), m(_INSET),
                       CARD_W * SS - 2 * m(_INSET), CARD_H * SS - 2 * m(_INSET))
    rad = m(CARD_RAD)

    drop_shadow(big, rect, rad, blur=m(8), alpha=160, dy=m(4))
    big.blit(vgrad(rect.w, rect.h, rad, CARD_T, CARD_B, 252, gamma=1.15),
             rect.topleft)
    top_sheen(big, rect, rad, m(30), peak=62)
    contact_shadow(big, rect, rad, m(9), alpha=120)
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 235),
              w=max(1, m(2.0)))

    cx = rect.left + m(40)
    cy = rect.y + m(38)
    plinth_top = rect.y + m(72)

    _neutral_band(big, rect, plinth_top, rad)

    soft_glow(big, cx, cy, m(R + 4), pal["glow"], 30, layers=8)
    cabochon(big, cx, cy, m(R), CABO_LO, CABO_HI, ring=pal["gem"], ring_a=50)
    blit_thumb(big, sid, cx, cy, int(m(R) * 1.5))
    cabochon_glass(big, cx, cy, m(R), tint=pal["gem"])

    facet_gem(big, rect.right - m(19), rect.y + m(19), m(GEM_R + 3),
              pal["gem"], pal["deep"])
    _simple_price(big, rect.right - m(23), rect.y + m(48), price, pal)
    _name_spark_label(big, name.upper(), rect.centerx,
                      rect.w - m(22), pal, sid, rect, plinth_top)

    return big


VARIANTS = [
    ("RARE",      "skin_tophat"),
    ("EPIC",      "skin_prism"),
    ("LEGENDARY", "skin_kitsune"),
]

PANEL_W, PANEL_H = CARD_W * SS, CARD_H * SS
MARGIN, GUTTER, HEADER_H, FOOTER_H = 10, 8, 26, 22

sheet_w = MARGIN * 2 + PANEL_W * 3 + GUTTER * 2
sheet_h = MARGIN + HEADER_H + PANEL_H + FOOTER_H + MARGIN
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((8, 8, 20))

hfont = _font(20, True)
ffont = _font(18, True)
htxt = hfont.render("store_card_v4_r4_name — spark-label — round 2", True,
                    (236, 232, 214))
sheet.blit(htxt, (MARGIN, MARGIN + (HEADER_H - htxt.get_height()) // 2))

panel_y = MARGIN + HEADER_H
for i, (tier, sid) in enumerate(VARIANTS):
    px = MARGIN + i * (PANEL_W + GUTTER)
    sheet.blit(render_card(sid), (px, panel_y))
    ftxt = ffont.render(tier, True, (218, 214, 200))
    sheet.blit(ftxt, (px + (PANEL_W - ftxt.get_width()) // 2,
                      panel_y + PANEL_H + (FOOTER_H - ftxt.get_height()) // 2))

out = "/home/user/skybit/docs/store_card_v4_r4_name/spark-label/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())
