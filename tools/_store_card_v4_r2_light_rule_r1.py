"""light-rule — store_card_v4_r2 concept, round 1 headless render.

The airy counterpoint to the four heavier slab siblings: there is NO plate
anywhere below the disc. The "band" is a single luminous BASELINE RULE — one
thin bright emissive line low on the card — and the name floats on the OPEN
indigo body directly above it, carried by its own keyline (no frosted plate,
no carved trough behind it).

  * LUMINOUS RULE: a crisp bright core line (CARD_RING_BRIGHT with a hotter
    cream centre) spanning most of the width, wrapped in a soft additive bloom
    so it reads as EMISSIVE light rather than a drawn border.
  * NAME: cream (CREAM_LABEL) floating on bare indigo above the rule. With no
    plate behind it, legibility rests entirely on a firm dark keyline
    (6,6,16) — kept crisp so the letters hold against the body.
  * PRICE: a minimal glow-CAPSULE straddling the rule's RIGHT END (below the
    top-right gem) — just a feathered additive pill of light behind the coin
    glyph + cream digits, NOT a frosted or carved plate. The bloom is the only
    thing behind the numerals.

The bottom half stays genuinely open indigo (negative space), so the card
cannot converge with the plate/arc-marquee grammar of its siblings.

Headless (SDL dummy) -> a 3-up RARE/EPIC/LEGENDARY review sheet at SS
(324x200, no downscale) plus a real-scale 1x strip so the keyline-only name
and the glow capsule are checked at the live size. Not wired into the live
store; writes docs/store_card_v4_r2/light-rule/round_1.png.
"""
import os

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import math
import sys

sys.path.insert(0, "/home/user/skybit")

import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from game import store_catalog
from game.hud import _font
from game.store_cards import (
    vgrad, vgrad_stops, drop_shadow, bevel_rim, top_sheen, contact_shadow,
    cabochon, cabochon_glass, blit_thumb, facet_gem, plain_text, soft_glow,
    coin_glyph, _glyph_base, _rarity, font, m, SS,
    CABO_LO, CABO_HI, CARD_T, CARD_B, CARD_RING_DEEP, CARD_RING_BRIGHT,
    GEM_R, RARITY, MYSTERY,
)

# LOCKED card constants (from store_cards).
CARD_W, CARD_H = 162, 100
CARD_RAD = 17
_INSET = 6

# Hero disc radius (logical). The disc dominates the top; the open indigo body
# below it is left bare so the name can genuinely float on it.
R = 34

# Cream shared by the name AND the price numerals — one type value so gold never
# has to carry legibility (only the coin glyph is gold).
CREAM_LABEL = (236, 230, 208)


def _hero_specular(surf, cx, cy, r):
    """A guaranteed high-value glass specular on the upper-left rim, drawn OVER
    the cabochon glass so EVERY skin keeps a lit crescent — dark heroes (e.g.
    skin_tophat) no longer read as a flat low-value blob under the dome."""
    ec = r + m(3)
    edge = pygame.Surface((ec * 2 + m(2), ec * 2 + m(2)), pygame.SRCALPHA)
    steps = max(2, m(4))
    for k in range(steps):
        a = int(210 * (1 - k / steps))
        rk = r - m(1) - k
        if rk <= 0:
            break
        pygame.draw.arc(edge, (255, 250, 234, a),
                        (ec - rk, ec - rk, rk * 2, rk * 2),
                        math.radians(110), math.radians(198), max(1, m(1)))
    surf.blit(edge, (cx - ec, cy - ec), special_flags=pygame.BLEND_ADD)
    # a single hot pip upper-left so there is always a crisp catch-light.
    pr = max(1, int(r * 0.17))
    pip = pygame.Surface((pr * 2 + m(2), pr * 2 + m(2)), pygame.SRCALPHA)
    pygame.draw.circle(pip, (255, 255, 255, 235), (pr + m(1), pr + m(1)), pr)
    off = int(r * 0.66)
    surf.blit(pip, (cx - pr - off, cy - pr - off),
              special_flags=pygame.BLEND_ADD)


def _luminous_rule(surf, x0, x1, y, bright):
    """The baseline itself: a crisp bright core line wrapped in a soft ADDITIVE
    bloom so it reads as emissive light, not a drawn border. The bloom is stacked
    wide translucent strokes (widest+faintest first) plus rounded glow caps at
    the ends, then a hot cream centre so the core stays a hard bright thread."""
    bloom = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    for w, a in [(m(9), 16), (m(6), 28), (m(3.5), 52), (m(2), 92)]:
        pygame.draw.line(bloom, (*bright, a), (x0, y), (x1, y), max(1, int(w)))
    surf.blit(bloom, (0, 0), special_flags=pygame.BLEND_ADD)
    # soft round caps so the emission fades out rather than ending on a hard edge.
    soft_glow(surf, x0, y, m(5), bright, 26, layers=7)
    soft_glow(surf, x1, y, m(5), bright, 26, layers=7)
    # crisp core: bright ring gold thread with a hotter cream filament on top.
    pygame.draw.line(surf, bright, (x0, y), (x1, y), max(1, m(1.4)))
    pygame.draw.line(surf, (250, 244, 224), (x0, y), (x1, y), max(1, m(0.7)))


def _glow_capsule(surf, rect, color, peak=46):
    """A minimal emissive pill of light behind the price — a feathered additive
    rounded bloom (widest+faintest first, narrowing to a bright core), NOT a
    frosted or carved plate. Only this soft pad sits behind the coin + digits."""
    for grow, frac in [(m(6), 0.20), (m(4), 0.36), (m(2), 0.60), (0, 1.0)]:
        r = rect.inflate(grow * 2, grow * 2)
        pad = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
        pygame.draw.rect(pad, (*color, int(peak * frac)), (0, 0, r.w, r.h),
                         border_radius=r.h // 2)
        surf.blit(pad, r.topleft, special_flags=pygame.BLEND_ADD)


def _name_floating(surf, name, cx, cy, max_w):
    """Cream item name floating on bare indigo — auto-shrunk from 9.5pt until it
    fits `max_w`. With no plate behind it, the firm dark keyline is the ONLY
    thing separating the letters from the body, so it is kept crisp + heavy."""
    sz = 9.5
    f = font(sz)
    while _glyph_base(name, f, 0).get_width() > max_w and sz > 6.0:
        sz -= 0.5
        f = font(sz)
    plain_text(surf, name, f, (cx, cy), CREAM_LABEL, shadow_a=170,
               weight=m(1.0), keyline=(6, 6, 16), kw=m(1.0))


def render_card(sid):
    """Draw ONE light-rule card onto a fresh SS panel (324x200) and return it
    (drawn directly at SS, no smoothscale)."""
    pal = RARITY.get(_rarity(sid), MYSTERY)
    name = store_catalog.name(sid)

    big = pygame.Surface((CARD_W * SS, CARD_H * SS), pygame.SRCALPHA)
    rect = pygame.Rect(m(_INSET), m(_INSET),
                       CARD_W * SS - 2 * m(_INSET), CARD_H * SS - 2 * m(_INSET))
    rad = m(CARD_RAD)
    cx, cy = rect.centerx, rect.y + m(31)          # disc high; open body below it

    # ── SHELL (locked order) ──
    drop_shadow(big, rect, rad, blur=m(8), alpha=160, dy=m(4))
    big.blit(vgrad(rect.w, rect.h, rad, CARD_T, CARD_B, 252, gamma=1.15),
             rect.topleft)
    top_sheen(big, rect, rad, m(30), peak=62)
    contact_shadow(big, rect, rad, m(9), alpha=120)
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 235),
              w=max(1, m(2.0)))

    # ── HERO DISC ──
    soft_glow(big, cx, cy, m(R + 3), pal["glow"], 34, layers=9)
    cabochon(big, cx, cy, m(R), CABO_LO, CABO_HI, ring=pal["gem"], ring_a=55)
    blit_thumb(big, sid, cx, cy, m(R) * 0.66)
    cabochon_glass(big, cx, cy, m(R), tint=pal["gem"])
    _hero_specular(big, cx, cy, m(R))              # luminance-independent catch-light

    # ── GEM CREST (locked call) ──
    facet_gem(big, rect.right - m(19), rect.y + m(19), m(GEM_R + 3),
              pal["gem"], pal["deep"])

    # ── PRICE (glow-capsule straddling the rule's RIGHT END, below the gem) ──
    # Sized first so the name knows how much of the rule to clear on the right.
    rule_y = rect.bottom - m(7)
    rule_x0 = rect.x + m(10)
    rule_x1 = rect.right - m(10)
    price_str = "480"
    pf = font(8.0)
    num_w = _glyph_base(price_str, pf, 0).get_width()
    coin_r = m(4.5)
    pad = m(5)
    gapc = m(3.5)
    cap_w = pad + coin_r * 2 + gapc + num_w + pad
    cap_h = m(13)
    cap = pygame.Rect(rule_x1 - cap_w, rule_y - cap_h // 2, cap_w, cap_h)
    _glow_capsule(big, cap, pal["glow"])
    coin_cx = cap.x + pad + coin_r
    coin_glyph(big, coin_cx, cap.centery, coin_r)
    plain_text(big, price_str, pf,
               (coin_cx + coin_r + gapc + num_w // 2, cap.centery),
               CREAM_LABEL, shadow_a=0, weight=m(0.9), keyline=(6, 6, 16),
               kw=m(0.8))

    # ── LUMINOUS BASELINE RULE (drawn under the capsule's right end) ──
    _luminous_rule(big, rule_x0, rule_x1, rule_y, CARD_RING_BRIGHT)

    # ── NAME floating on the open indigo body, centred over the rule left of the
    #    price cell (so it reads slightly left) and carried by its keyline. ──
    name_left = rule_x0
    name_right = cap.left - m(6)
    name_cx = (name_left + name_right) // 2
    name_cy = rect.bottom - m(16)
    _name_floating(big, name.upper(), name_cx, name_cy, name_right - name_left)

    return big


# ── review sheet ──────────────────────────────────────────────────────────────
VARIANTS = [
    ("RARE",      "skin_tophat"),
    ("EPIC",      "skin_prism"),
    ("LEGENDARY", "skin_kitsune"),
]

PANEL_W, PANEL_H = CARD_W * SS, CARD_H * SS   # 324 x 200 (SS panels, no downscale)
MARGIN = 10
GUTTER = 8
HEADER_H = 30
FOOTER_H = 22
STRIP_LABEL_H = 20
STRIP_H = CARD_H                              # real-scale 1x cards (162x100)

sheet_w = MARGIN * 2 + PANEL_W * 3 + GUTTER * 2
sheet_h = (MARGIN + HEADER_H + PANEL_H + FOOTER_H + STRIP_LABEL_H + STRIP_H
           + MARGIN)
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((8, 8, 20))

hfont = _font(22, True)
ffont = _font(18, True)
sfont = _font(15, True)
htxt = hfont.render("store_card_v4_r2 — light-rule — round 1", True,
                    (236, 232, 214))
sheet.blit(htxt, (MARGIN, MARGIN + (HEADER_H - htxt.get_height()) // 2))

panel_y = MARGIN + HEADER_H
panels = []
for i, (tier, sid) in enumerate(VARIANTS):
    px = MARGIN + i * (PANEL_W + GUTTER)
    panel = render_card(sid)
    panels.append(panel)
    sheet.blit(panel, (px, panel_y))
    ftxt = ffont.render(tier, True, (218, 214, 200))
    sheet.blit(ftxt, (px + (PANEL_W - ftxt.get_width()) // 2,
                      panel_y + PANEL_H + (FOOTER_H - ftxt.get_height()) // 2))

# 1x real-scale strip: smoothscale each SS panel down to the live 162x100 card so
# the keyline-only name + glow capsule survival is visible in the same sheet.
strip_label_y = panel_y + PANEL_H + FOOTER_H
ltxt = sfont.render("real scale (1x, 162x100)", True, (200, 204, 220))
sheet.blit(ltxt, (MARGIN, strip_label_y + (STRIP_LABEL_H - ltxt.get_height()) // 2))
strip_y = strip_label_y + STRIP_LABEL_H
for i, panel in enumerate(panels):
    px = MARGIN + i * (PANEL_W + GUTTER)
    left = px + (PANEL_W - CARD_W) // 2
    small = pygame.transform.smoothscale(panel, (CARD_W, CARD_H))
    sheet.blit(small, (left, strip_y))

out = "/home/user/skybit/docs/store_card_v4_r2/light-rule/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())


# ── L* probes (no image display): confirm the floating name + price capsule both
#    read well clear of the dark indigo body they sit on, at authored SS. ──
def _lstar(rgb):
    def lin(c):
        c /= 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(v) for v in rgb[:3])
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return 903.3 * y if y <= 0.008856 else 116 * y ** (1 / 3) - 16


epic = render_card("skin_prism")
rect = pygame.Rect(m(_INSET), m(_INSET),
                   CARD_W * SS - 2 * m(_INSET), CARD_H * SS - 2 * m(_INSET))
# body reference: bare indigo just below the disc, left of the name.
body = epic.get_at((rect.x + m(14), rect.bottom - m(16)))
# brightest name-glyph pixel across its floating band (the lit cream face).
name_peak = 0.0
for yy in range(rect.bottom - m(22), rect.bottom - m(10)):
    for xx in range(rect.x + m(10), rect.centerx + m(20)):
        name_peak = max(name_peak, _lstar(epic.get_at((xx, yy))))
# brightest price-digit pixel in the right capsule.
price_peak = 0.0
for yy in range(rect.bottom - m(13), rect.bottom - m(1)):
    for xx in range(rect.right - m(46), rect.right - m(8)):
        price_peak = max(price_peak, _lstar(epic.get_at((xx, yy))))
print(f"  body(indigo)      rgb={tuple(body)[:3]}  L*={_lstar(body):5.1f}")
print(f"  floating name     peak L*={name_peak:5.1f}")
print(f"  price capsule     peak L*={price_peak:5.1f}")
