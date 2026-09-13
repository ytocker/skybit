import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
import sys
sys.path.insert(0, "/home/user/skybit")
import pygame
import math
pygame.init()
pygame.display.set_mode((1, 1))

from game.draw import lerp_color
from game import store_cards as sc
from game.store_cards import (
    m, font, vgrad, gold_a_fill, contact_shadow, drop_shadow,
    bevel_rim, soft_glow, cabochon, cabochon_glass, blit_thumb, _ribbon,
    price_chip, plain_text, coin_glyph, _glyph_base,
    RARITY, CARD_RING_DEEP, CARD_RING_BRIGHT, GOLD_A_RIM_DARK, GOLD_A_RIM_BRIGHT,
    GOLD_A_NUM, CABO_LO, CABO_HI,
)

# This SDL build's BLEND_ADD adds full source RGB regardless of source alpha, so
# the module's gloss_sweep (white lines carrying the sheen in their alpha) blows
# every gold fill to a flat white slab. Re-express the sheen as PREMULTIPLIED
# intensity in the RGB channels so the canonical price_chip + our BUY stay gold
# end-to-end. Kept as the module's RECT signature (surf, rect, radius, peak) so
# price_chip -> chip_body_stops resolves it unchanged.
def _gloss_sweep_fixed(surf, rect, radius, peak=95):
    sweep = pygame.Surface(rect.size, pygame.SRCALPHA)
    h = max(1, rect.h)
    for y in range(h):
        v = int(peak * (1 - y / h) ** 2.4)
        pygame.draw.line(sweep, (v, v, v, 255), (0, y), (rect.w, y))
    sm = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(sm, (255, 255, 255, 255), sm.get_rect(), border_radius=radius)
    sweep.blit(sm, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(sweep, rect.topleft, special_flags=pygame.BLEND_ADD)


sc.gloss_sweep = _gloss_sweep_fixed          # price_chip resolves it module-level
gloss_sweep = _gloss_sweep_fixed

SID = "skin_lorikeet"
PAL = RARITY["legendary"]          # brief pins this item to the legendary tier
NAME_L1 = "RAINBOW"
NAME_L2 = "LORIKEET"
PRICE = "4,200"
BALANCE = "12,340"

W, H = 360, 640
big = pygame.Surface((m(W), m(H)), pygame.SRCALPHA)
big.fill((8, 6, 16, 255))                    # deep obsidian ground


def name_line(surf, txt, cx, cy, size, max_w):
    """Cream item name with the card's dark keyline (the _name_on look), split to
    two lines and auto-shrunk so even the widest legendary name stays inside the
    right pane instead of clipping the inner bezel."""
    f = font(size)
    while _glyph_base(txt, f, 0).get_width() > max_w and size > 10:
        size -= 0.5
        f = font(size)
    plain_text(surf, txt, f, (cx, cy), (250, 248, 240), shadow_a=160,
               weight=m(0.9), keyline=(6, 6, 16), kw=m(1.0))


def caption(surf, txt, cx, cy, size, col):
    f = font(size)
    plain_text(surf, txt, f, (cx, cy), col, shadow_a=120, weight=m(0.4),
               tracking=m(2))


def gold_button(surf, rect, radius, label, size):
    drop_shadow(surf, rect, radius, blur=m(4), alpha=130, dy=m(2))
    surf.blit(gold_a_fill(rect.w, rect.h, radius), rect.topleft)
    # Peak capped low so the premultiplied sheen only lifts the crown; the body
    # samples R>G>B gold everywhere, never a white slab.
    gloss_sweep(surf, rect, radius, peak=94)
    contact_shadow(surf, rect, radius, m(3), alpha=80)
    pygame.draw.rect(surf, GOLD_A_RIM_DARK, rect, width=max(1, m(1.6)),
                     border_radius=radius)
    bevel_rim(surf, rect, radius, GOLD_A_RIM_DARK, (*GOLD_A_RIM_BRIGHT, 235),
              w=max(1, m(1.6)))
    plain_text(surf, label, font(size), rect.center, GOLD_A_NUM, shadow_a=0,
               weight=m(1.3), tracking=m(3))


def ghost_button(surf, rect, radius, label, size):
    """A subtle keyline pill — 'ghost' means low-fill, NOT invisible: it keeps a
    translucent body, a defined dark+gold double keyline and legible cream type
    so the safe-out is always readable and comfortably tappable."""
    fill = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(fill, (44, 42, 66, 96), fill.get_rect(), border_radius=radius)
    surf.blit(fill, rect.topleft)
    pygame.draw.rect(surf, (8, 9, 20), rect, width=max(1, m(1.5)),
                     border_radius=radius)
    inner = rect.inflate(-m(1.4), -m(1.4))
    pygame.draw.rect(surf, (*CARD_RING_BRIGHT, 185), inner, width=max(1, m(1.2)),
                     border_radius=max(1, radius - m(1)))
    plain_text(surf, label, font(size), rect.center, (234, 228, 208),
               shadow_a=130, weight=m(0.8), tracking=m(2))


def divider(surf, x, y0, y1, w):
    """Bright gold gradient seam between panes — hottest at the vertical centre,
    but with a raised alpha + colour floor so the line still reads GOLD (not a
    dark brown vanish) at the very top and bottom, top-to-bottom."""
    h = y1 - y0
    d = pygame.Surface((w, h), pygame.SRCALPHA)
    for yy in range(h):
        t = yy / max(1, h - 1)
        edge = 1.0 - abs(t - 0.5) * 2.0        # 0 at ends, 1 at centre
        a = int(255 * (0.44 + 0.56 * edge ** 1.1))
        c = lerp_color((150, 96, 24), (255, 242, 196), 0.28 + 0.72 * edge ** 0.7)
        pygame.draw.line(d, (*c, a), (0, yy), (w - 1, yy))
    surf.blit(d, (x - w // 2, y0))


# ── header ─────────────────────────────────────────────────────────────────────
plain_text(big, "CONFIRM PURCHASE", font(16), (m(180), m(92)),
           (246, 214, 138), shadow_a=170, weight=m(1.0), tracking=m(3))
caption(big, "REVIEW YOUR TRADE", m(180), m(116), 9, (128, 124, 150))

# ── card geometry — a wide split trade card centred on the screen ───────────────
cardx, cardy = m(15), m(160)
cw, ch = m(330), m(280)
rad = m(22)
card_rect = pygame.Rect(cardx, cardy, cw, ch)
leftw = int(cw * 0.45)
rightw = cw - leftw

# Build the two-tone body on its own surface, round its corners, then seat it.
body = pygame.Surface((cw, ch), pygame.SRCALPHA)
body.blit(vgrad(leftw, ch, 0, (17, 15, 32), (6, 6, 17), gamma=1.1), (0, 0))
body.blit(vgrad(rightw, ch, 0, (33, 31, 56), (15, 15, 34), gamma=1.12), (leftw, 0))
mask = pygame.Surface((cw, ch), pygame.SRCALPHA)
pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=rad)
body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

drop_shadow(big, card_rect, rad, blur=m(8), alpha=170, dy=m(4))
big.blit(body, card_rect.topleft)

# gold DOUBLE bezel — dark contact keyline, bright struck bevel, inner gold hairline
pygame.draw.rect(big, (4, 5, 16), card_rect, width=max(1, m(2)), border_radius=rad)
bevel_rim(big, card_rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 235),
          w=max(1, m(2)))
inner_inset = m(8)
inner_bez = card_rect.inflate(-inner_inset * 2, -inner_inset * 2)
pygame.draw.rect(big, (*CARD_RING_BRIGHT, 120), inner_bez, width=max(1, m(1)),
                 border_radius=rad - m(6))

# ── shared right-pane axis ──────────────────────────────────────────────────────
# rcx is the true midpoint between the divider and the RIGHT inner bezel, so every
# right-pane element (name / price / CANCEL / BUY) is optically centred with equal
# padding on both sides instead of drifting toward the outer bezel.
div_x = cardx + leftw
bez_r = cardx + cw - inner_inset
rcx = (div_x + bez_r) // 2
pad = m(15)
pill_w = (bez_r - pad) - (div_x + pad)
name_max_w = pill_w - m(6)

# ── LEFT PANE — the vitrine (what you get) ──────────────────────────────────────
cabx = cardx + leftw // 2
caby = cardy + m(130)          # nudged down to optically centre in the vitrine
r_disc = m(56)
caption(big, "YOU UNLOCK", cabx, cardy + m(26), 9, (188, 152, 92))
soft_glow(big, cabx, caby, r_disc + m(6), PAL["glow"], 44, layers=9)
cabochon(big, cabx, caby, r_disc, CABO_LO, CABO_HI, ring=PAL["gem"], ring_a=55)
blit_thumb(big, SID, cabx, caby, r_disc * 1.5)
cabochon_glass(big, cabx, caby, r_disc, tint=PAL["gem"])
_ribbon(big, "LEGENDARY", cabx, cardy + m(232), leftw - m(20), PAL)

# ── DIVIDER ─────────────────────────────────────────────────────────────────────
divider(big, div_x, cardy + m(14), cardy + ch - m(14), max(2, m(2)))

# ── RIGHT PANE — the offer (what you pay + the decision) ─────────────────────────
name_line(big, NAME_L1, rcx, cardy + m(40), 14, name_max_w)
name_line(big, NAME_L2, rcx, cardy + m(58), 14, name_max_w)

caption(big, "PRICE", rcx, cardy + m(86), 8, (150, 146, 172))
price_chip(big, rcx, cardy + m(106), PRICE, m(24), affordable=True)

cancel = pygame.Rect(rcx - pill_w // 2, cardy + m(138), pill_w, m(48))
ghost_button(big, cancel, cancel.h // 2, "CANCEL", 12)
buy = pygame.Rect(rcx - pill_w // 2, cardy + m(208), pill_w, m(58))
gold_button(big, buy, buy.h // 2, "BUY", 21)

# ── FOOTER — wallet balance so the trade has context ────────────────────────────
caption(big, "YOUR BALANCE", m(180), m(505), 9, (132, 128, 154))
bf = font(15)
bw = _glyph_base(BALANCE, bf, 0).get_width()
coin_r = m(9)
gap = m(8)
group_w = coin_r * 2 + gap + bw
gx = m(180) - group_w // 2
coin_glyph(big, gx + coin_r, m(530), coin_r)
plain_text(big, BALANCE, bf, (gx + coin_r * 2 + gap + bw // 2, m(530)),
           (246, 226, 158), shadow_a=140, weight=m(0.9))

# ── downscale once for crisp AA, save ───────────────────────────────────────────
out = pygame.transform.smoothscale(big, (W, H))
outdir = "/home/user/skybit/docs/confirm_purchase/split-deal-card"
os.makedirs(outdir, exist_ok=True)
path = os.path.join(outdir, "round_2.png")
pygame.image.save(out, path)
print("saved", path, os.path.getsize(path))

# ── verification: right-pane symmetry + BUY centre-column colour ─────────────────
sf = W / m(W)
print("div_x(1x)=%.1f  rcx(1x)=%.1f  bez_r(1x)=%.1f" % (div_x*sf, rcx*sf, bez_r*sf))
print("cancel L/R gap to div/bez (1x): %.1f / %.1f" % (
    (cancel.left - div_x) * sf, (bez_r - cancel.right) * sf))
buy_cx = int((rcx) * sf)
buy_cy = int((buy.centery) * sf)
r, g, b, _ = out.get_at((buy_cx, buy_cy))
print("BUY centre px RGB:", (r, g, b), "R>G>B" if r > g > b else "FAIL R>G>B")
# divider top/bottom sample
dtx = int(div_x * sf)
for lbl, yy in (("top", cardy + m(20)), ("bot", cardy + ch - m(20))):
    px = out.get_at((dtx, int(yy * sf)))
    print("divider", lbl, "px:", tuple(px[:3]))
