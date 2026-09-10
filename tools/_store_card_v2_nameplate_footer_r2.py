"""nameplate-footer store-card concept — round 2 review render (headless).

A compact hero disc over a full-width tier footer that fuses ribbon and
nameplate into one lit shelf: the footer stripe carries the rarity read (tier
gradient) AND the item name, with a dark-vignetted canonical gold price pill in
its lower zone. No separate ribbon. This is an exploration harness, not shipped
runtime — it writes a review sheet under docs/, never into the game bundle.

Round 2 folds the art-director's ITERATE notes:
  1. CREAM name text + dark keyline so it clears 3:1 on blue/purple/gold tiers
     (R1's dark engrave died on EPIC purple).
  2. redundant non-colour tier cue — 1/2/3 pips left of the price chip so the
     RARE-blue vs EPIC-purple deutan/protan confuser is still distinguishable.
  3. 2px more air between the disc's dark lower arc and the footer's gold rim.
  4. widened name<->chip lane so they don't crowd at 1x.
  5. saturated 2-stop footer gradient (gem->glow) so the tier hue stays vivid
     around the chip instead of darkening to near-navy.
"""
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
import sys
sys.path.insert(0, "/home/user/skybit")
import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from game.store_cards import (
    vgrad, vgrad_stops, drop_shadow, bevel_rim, top_sheen, contact_shadow,
    plain_text, price_chip, facet_gem, cabochon, cabochon_glass, blit_thumb,
    soft_glow, font, m, SS, CABO_LO, CABO_HI, CARD_T, CARD_B, CARD_RING_DEEP,
    CARD_RING_BRIGHT, CREAM, GEM_R, CARD_RAD, _name,
)
from game.hud import _font

# ── LOCKED card metrics ───────────────────────────────────────────────────────
CARD_W, CARD_H = 162, 100
INSET = 6
BODY_W = 150                      # visible body: 150x88 at logical (6,6)


def _tier_pips(big, n, right_edge, cy, r, gap):
    """Redundant non-colour tier cue: a left-growing row of `n` filled dots so
    RARE/EPIC/LEGENDARY are separable by COUNT, not just by the blue/purple/gold
    hue a colourblind player can't split. Drawn on a temp SRCALPHA tile so the
    semi-transparent fill blends OVER the footer instead of punching holes."""
    step = r * 2 + gap
    width = n * step
    tile = pygame.Surface((width + m(2), r * 2 + m(2)), pygame.SRCALPHA)
    ty = r + m(1)
    for i in range(n):
        # lay dots right-to-left so the row ends flush against `right_edge`
        cxp = width - m(1) - r - i * step
        pygame.draw.circle(tile, (255, 255, 220, 200), (cxp, ty), r)
    big.blit(tile, (right_edge - width, cy - ty))


def draw_nameplate_card(big, sid, rect, pal, price, pips):
    """Render one nameplate-footer card into `rect` (device px) on `big`."""
    rad = m(CARD_RAD)
    body_x, body_y = rect.x, rect.y
    cx_ss = rect.centerx
    # disc nudged 2px higher than R1 (33->31) so its dark lower arc keeps 2-3px
    # of air above the footer's gold top rim instead of kissing it.
    cy_ss = rect.y + m(31)
    R = 28                        # hero disc radius (logical)

    # 1) soft multi-layer drop shadow (top-left light => offset down)
    drop_shadow(big, rect, rad, blur=m(8), alpha=160, dy=m(4))
    # 2) body gradient
    big.blit(vgrad(rect.w, rect.h, rad, CARD_T, CARD_B, 252, gamma=1.15),
             rect.topleft)
    # 3) glossy top sheen
    top_sheen(big, rect, rad, m(30), peak=62)
    # 4) bottom-right contact AO
    contact_shadow(big, rect, rad, m(9), alpha=120)
    # 5) inner tray (dark border + faint gold keyline)
    tray = rect.inflate(-m(7), -m(7))
    trad = rad - m(4)
    pygame.draw.rect(big, (10, 10, 24, 200), tray.inflate(m(2), m(2)),
                     width=max(1, m(1)), border_radius=trad + m(1))
    pygame.draw.rect(big, (*CARD_RING_BRIGHT, 90), tray, width=max(1, m(1)),
                     border_radius=trad)

    # 6) soft tier aura behind the hero disc — rarity is carried by the footer,
    #    so the glow stays at the standard peak.
    soft_glow(big, cx_ss, cy_ss, m(R + 3), pal["glow"], 30, layers=8)
    # 7) cabochon well -> rim-lit hero skin -> glass dome overlay
    cabochon(big, cx_ss, cy_ss, m(R), CABO_LO, CABO_HI, ring=pal["gem"],
             ring_a=50)
    blit_thumb(big, sid, cx_ss, cy_ss, m(R) * 1.5)
    cabochon_glass(big, cx_ss, cy_ss, m(R), tint=pal["gem"])

    # 8) full-width tier-gradient footer, clipped to the body rounded rect so its
    #    bottom corners follow the card. This IS the rarity + name shelf. A
    #    2-stop gem->glow ramp (was gem->glow->deep): the saturated tier hue now
    #    stays vivid all the way down to the chip zone instead of sinking to navy.
    fw, fh = m(BODY_W), m(22)
    footer = vgrad_stops(fw, fh, m(CARD_RAD - 4),
                         [(0.0, pal["gem"]), (1.0, pal["glow"])], 255, gamma=1.0)
    body_mask = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    pygame.draw.rect(body_mask, (255, 255, 255, 255), (0, 0, rect.w, rect.h),
                     border_radius=rad)
    corner_clip = body_mask.subsurface((0, m(62), fw, fh)).copy()
    footer.blit(corner_clip, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(footer, (body_x, body_y + m(62)))

    # 9) item name — CREAM fill + a tight dark keyline so it reads as engraved
    #    AND clears 3:1 contrast on EVERY tier (R1's dark-brown engrave failed on
    #    EPIC purple). Lifted to y=66 to widen the lane above the chip.
    plain_text(big, _name(sid), font(13.5), (cx_ss, body_y + m(66)),
               (250, 240, 220), shadow_a=180, weight=m(0.8),
               keyline=(8, 6, 16), kw=m(1.0))

    # 10) canonical GOLD RAMP-A price pill in the footer's lower zone, dropped to
    #     y=79 for a 4-5px gap under the name at 1x. A dark backing vignette sits
    #     behind it so canonical gold never muddies against the tier hue.
    chip_cy = body_y + m(79)
    pygame.draw.rect(big, (4, 4, 14, 160),
                     (cx_ss - m(42), chip_cy - m(11), m(84), m(22)),
                     border_radius=m(10))
    chip_rect = price_chip(big, cx_ss, chip_cy, f"{price:,}", m(20),
                           affordable=True)

    # 11) tier pips — 1/2/3 dots left of the chip, a colour-independent count cue.
    _tier_pips(big, pips, chip_rect.left - m(6), chip_cy, m(3), m(2))

    # 12) crest gem, top-right corner
    facet_gem(big, rect.right - m(19), rect.y + m(19), m(GEM_R + 3),
              pal["gem"], pal["deep"])

    # 13) bevel rim + dark keyline LAST so the card edge stays crisp on top
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 235),
              w=max(1, m(2.0)))


def render_panel(sid, pal, price, pips):
    big = pygame.Surface((CARD_W * SS, CARD_H * SS), pygame.SRCALPHA)
    rect = pygame.Rect(m(INSET), m(INSET),
                       CARD_W * SS - 2 * m(INSET), CARD_H * SS - 2 * m(INSET))
    draw_nameplate_card(big, sid, rect, pal, price, pips)
    return big


VARIANTS = [
    ("RARE", "skin_lorikeet",
     {"gem": (108, 188, 252), "glow": (60, 140, 230), "deep": (18, 44, 90)},
     600, 1),
    ("EPIC", "skin_prism",
     {"gem": (194, 122, 248), "glow": (150, 60, 220), "deep": (44, 10, 80)},
     1400, 2),
    ("LEGENDARY", "skin_kitsune",
     {"gem": (255, 202, 104), "glow": (220, 160, 40), "deep": (90, 50, 0)},
     3500, 3),
]

# ── review sheet ──────────────────────────────────────────────────────────────
MARGIN, GUTTER, HEADER_H = 20, 16, 30
LABEL_H = 24
PW, PH = CARD_W * SS, CARD_H * SS          # 324x200 SS panels, no downscale
ONE_W, ONE_H = CARD_W, CARD_H              # 1x strip so tier + name read at game size

sheet_w = MARGIN * 2 + PW * 3 + GUTTER * 2
sheet_h = (MARGIN + HEADER_H + 10 + PH + 8 + LABEL_H + 14
           + ONE_H + 8 + LABEL_H + MARGIN)
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((20, 22, 40))

hfont = _font(20, True)
htxt = hfont.render("store_card_v2 — nameplate-footer — round 2", True,
                    (240, 236, 224))
sheet.blit(htxt, (MARGIN, MARGIN + (HEADER_H - htxt.get_height()) // 2))

lfont = _font(16, True)
sfont = _font(13, True)

# SS panels row
py = MARGIN + HEADER_H + 10
panels = []
for i, (label, sid, pal, price, pips) in enumerate(VARIANTS):
    px = MARGIN + i * (PW + GUTTER)
    panel = render_panel(sid, pal, price, pips)
    panels.append(panel)
    sheet.blit(panel, (px, py))
    lt = lfont.render(label, True, (232, 228, 216))
    sheet.blit(lt, (px + (PW - lt.get_width()) // 2, py + PH + 8))

# 1x strip: smoothscale each 324x200 panel down to the live 162x100 game size so
# tier separation, name legibility and pip visibility can be judged as shipped.
oy = py + PH + 8 + LABEL_H + 14
one_lbl = sfont.render("1x (game size 162x100)", True, (200, 198, 214))
sheet.blit(one_lbl, (MARGIN, oy - one_lbl.get_height() - 2))
for i, panel in enumerate(panels):
    ox = MARGIN + i * (ONE_W + GUTTER)
    one = pygame.transform.smoothscale(panel, (ONE_W, ONE_H))
    sheet.blit(one, (ox, oy))
    label = VARIANTS[i][0]
    lt = sfont.render(label, True, (200, 198, 214))
    sheet.blit(lt, (ox + (ONE_W - lt.get_width()) // 2, oy + ONE_H + 6))

out = "/home/user/skybit/docs/store_card_v2/nameplate-footer/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())
