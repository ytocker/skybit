"""tidal-shelf — store_card_v4_r3 concept, round 2 headless render.

Addresses all five art-director notes from round 1:

1. Strata rebalanced: name lane thinned to m(12) below the waterline
   (~17.5 px display). The three cool indigo bands below each claim ~8 px —
   enough to read as distinct sediment at 162×100.

2. Etch price floor: a ~40 % cream base layer drawn before the shadow and
   glint stamps lifts the entire numeral silhouette above the near-black card
   body; the carved core stamp is reduced to 40 % opacity so the floor shows
   through. No chip, no pill — still bodiless.

3. Waterline crest rim cooled 40 % toward aqua-white (200, 220, 235) so the
   water line reads as a different material than the price glint and tier-gem
   ring, ending three competing warms in the upper-right quadrant.

4. Disc cx nudged +3 logical px (m(40) → m(43)) so the soft glow clears the
   left bevel.

5. Post-render: downsamples the RARE panel to true 162×100 via smoothscale and
   prints L* strata measurements + name contrast ratio.

What is kept from round 1: burial concept (disc drawn first, strata over lower
arc), waterline amplitude and periodicity (WAVE_AMP=3.5, WAVE_CRESTS=2.5),
disc radius R=36, standard locked shell + gem badge, name contrast protection.
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

from game.draw import lerp_color
from game.hud import _font
from game import store_catalog
from game.store_cards import (
    cabochon, cabochon_glass, blit_thumb, facet_gem,
    vgrad, vgrad_stops, drop_shadow, bevel_rim, top_sheen, contact_shadow,
    plain_text, font, m, SS, soft_glow, coin_glyph, _glyph_base, _stamp_bold,
    _cost,
    CARD_T, CARD_B, CARD_RING_BRIGHT, CARD_RING_DEEP,
    CABO_LO, CABO_HI, GEM_R, RARITY, MYSTERY, _rarity,
)

# LOCKED card shell constants (mirrors store_cards.render_card).
CARD_W, CARD_H = 162, 100
CARD_RAD = 17
_INSET = 6
R = 36                          # hero disc radius; lower ~third is buried
CREAM = (248, 246, 236)

# Waterline geometry preserved from round 1.
WAVE_AMP = 3.5
WAVE_CRESTS = 2.5

# Aqua-white target: lerp the crest rim this far from warm-gold so the water
# line separates visually from the price glint and tier-gem ring.
_RIM_AQUA = (200, 220, 235)


def _name_on_shelf(surf, name, cx, cy, max_w):
    """Cream item name auto-shrunk to the warm lane; keylined for legibility
    on the tier-tinted band."""
    sz = 13.5
    f = font(sz)
    while _glyph_base(name, f, 0).get_width() > max_w and sz > 9:
        sz -= 0.5
        f = font(sz)
    plain_text(surf, name, f, (cx, cy), CREAM, shadow_a=170,
               weight=m(0.9), keyline=(6, 6, 16), kw=m(1.0))


def _etch_number(surf, text, right_x, cy, size):
    """Bodiless tide-mark engrave: the numeral is pressed into the card face.
    A faint cream floor is drawn first so the full glyph silhouette carries a
    readable value above the near-black ground; the dark shadow and warm glint
    then modulate the intaglio walls on top of it. The carved-core stamp is
    held at 40 % opacity so the floor shows through at centre — no chip, no
    pill, just an engraved groove."""
    f = font(size)
    base = _stamp_bold(_glyph_base(text, f, 0), m(0.6))
    w, h = base.get_size()
    x = right_x - w
    y = cy - h // 2
    e = max(1, m(0.8))

    def tint(col, alpha=255):
        img = base.copy()
        img.fill((*col, 255), special_flags=pygame.BLEND_RGBA_MULT)
        if alpha < 255:
            img.set_alpha(alpha)
        return img

    # warm halo sells the etch as catching stray ambient light
    soft_glow(surf, x + w // 2, cy, int(m(size * 0.42)), (255, 214, 150), 9,
              layers=6)
    # recessed floor: pale cream at ~40 % lifts the whole glyph outline above
    # the near-black card body — the groove now reads as a sunken shape, not
    # just a one-sided gold rim
    surf.blit(tint((248, 244, 224), alpha=100), (x, y))
    surf.blit(tint((2, 3, 10)), (x - e, y - e))           # dark upper-left wall
    surf.blit(tint((255, 226, 158)), (x + e, y + e))      # warm lower-right glint
    # reduced-opacity core so the cream floor remains visible at centre
    surf.blit(tint((9, 10, 26), alpha=100), (x, y))
    return pygame.Rect(x, y, w, h)


def _coin_ring(surf, cx, cy, r):
    """Faint denomination coin mark beside the etched price."""
    pad = m(2)
    tmp = pygame.Surface((r * 2 + pad * 2, r * 2 + pad * 2), pygame.SRCALPHA)
    coin_glyph(tmp, r + pad, r + pad, r)
    tmp.fill((255, 255, 255, 96), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(tmp, (cx - r - pad, cy - r - pad))
    pygame.draw.circle(surf, (*CARD_RING_BRIGHT, 130), (cx, cy), r, max(1, m(1)))


def _wave_y(x, x0, span, base):
    """Waterline height at column x: a shallow sine of WAVE_CRESTS periods."""
    return base + m(WAVE_AMP) * math.sin(
        2 * math.pi * WAVE_CRESTS * (x - x0) / span)


def _shelf(surf, rect, rad, base, pal):
    """Build the tide shelf on a SRCALPHA layer and composite it over the disc.

    Name lane thinned to m(12) below the waterline (~17.5 px display) so the
    three cool indigo strata below each occupy ~8 px — legibly distinct at the
    displayed 162×100. The waterline crest rim is lerped 40 % toward aqua-white
    so it reads as a different material from the price glint and gem ring above."""
    x0 = rect.left
    span = rect.w
    layer = pygame.Surface(surf.get_size(), pygame.SRCALPHA)

    # warm name band: tier-dark so cream name clears ~7:1, yet distinct from
    # the cool strata below
    name_band = lerp_color(lerp_color(CARD_T, pal["deep"], 0.45),
                           (96, 74, 42), 0.16)

    # thinned lane: s1 at +m(12) gives ~17.5 px display; the 50 device-px
    # remainder is split into three cool bands of ~8 display px each — enough
    # to see layered strata at true 162×100
    s1 = base + m(12)
    bottom = rect.bottom
    seg = (bottom - s1) / 3.0
    strata = [
        (base - m(WAVE_AMP) - m(2), s1, name_band),
        (s1, s1 + seg, (24, 26, 60)),
        (s1 + seg, s1 + 2 * seg, (18, 19, 48)),
        (s1 + 2 * seg, bottom, CARD_B),
    ]
    for top, bot, col in strata:
        pygame.draw.rect(layer, col,
                         (0, int(round(top)), surf.get_width(),
                          int(round(bot - top)) + 1))
    # thin sediment keylines between the cool strata
    for yb in (s1, s1 + seg, s1 + 2 * seg):
        pygame.draw.line(layer, (6, 7, 20), (0, int(round(yb))),
                         (surf.get_width(), int(round(yb))), max(1, m(0.7)))

    # carve wavy top edge: keep only what sits below the waterline
    pts = [(x, _wave_y(x, x0, span, base))
           for x in range(0, surf.get_width() + 1, m(1))]
    below = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    poly = pts + [(surf.get_width(), bottom + m(4)), (0, bottom + m(4))]
    pygame.draw.polygon(below, (255, 255, 255, 255), poly)
    layer.blit(below, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

    # crest rim cooled 40 % toward aqua-white — water-line ≠ price glint ≠ gem ring
    crest_col = (*lerp_color((255, 228, 172), _RIM_AQUA, 0.40), 200)
    pygame.draw.lines(layer, crest_col, False, pts, max(1, m(1.2)))

    # honour the card's rounded bottom corners
    mask = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), rect, border_radius=rad)
    layer.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(layer, (0, 0))


def render_card(sid):
    """Draw ONE tidal-shelf card onto a fresh SS panel (324×200) and return it."""
    pal = RARITY.get(_rarity(sid), MYSTERY)
    big = pygame.Surface((CARD_W * SS, CARD_H * SS), pygame.SRCALPHA)
    rect = pygame.Rect(m(_INSET), m(_INSET),
                       CARD_W * SS - 2 * m(_INSET), CARD_H * SS - 2 * m(_INSET))
    rad = m(CARD_RAD)

    # ── card shell (locked order) ──
    drop_shadow(big, rect, rad, blur=m(8), alpha=160, dy=m(4))
    big.blit(vgrad(rect.w, rect.h, rad, CARD_T, CARD_B, 252, gamma=1.15),
             rect.topleft)
    top_sheen(big, rect, rad, m(30), peak=62)
    contact_shadow(big, rect, rad, m(9), alpha=120)
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 235),
              w=max(1, m(2.0)))

    # ── hero disc: cx nudged +3 logical px so the soft glow clears the left bevel ──
    cx = rect.left + m(43)
    cy = rect.centery - m(6)
    soft_glow(big, cx, cy, m(R + 4), pal["glow"], 30, layers=8)
    cabochon(big, cx, cy, m(R), CABO_LO, CABO_HI, ring=pal["gem"], ring_a=50)
    blit_thumb(big, sid, cx, cy, int(m(R) * 1.5))
    cabochon_glass(big, cx, cy, m(R), tint=pal["gem"])

    # ── tide shelf composited over the disc ──
    wl_base = cy + m(13)
    _shelf(big, rect, rad, wl_base, pal)

    # ── name centred in thinned warm lane (m(6) = midpoint of ~12 px below-wave band) ──
    _name_on_shelf(big, store_catalog.name(sid), rect.centerx, wl_base + m(6),
                   rect.w - m(26))

    # ── bodiless tide-mark price, upper-right ──
    right_x = rect.right - m(12)
    py = rect.y + m(40)
    num = _etch_number(big, f"{_cost(sid):,}", right_x, py, 12.5)
    _coin_ring(big, num.left - m(9), py, m(6))

    # ── corner tier gem ──
    facet_gem(big, rect.right - m(19), rect.y + m(19), m(GEM_R + 3),
              pal["gem"], pal["deep"])
    return big


# ── review strip ───────────────────────────────────────────────────────────────
PANELS = [
    ("skin_tophat", "RARE"),
    ("skin_prism", "EPIC"),
    ("skin_kitsune", "LEGENDARY"),
]

PANEL_W, PANEL_H = CARD_W * SS, CARD_H * SS
MARGIN = 10
GAP = 8
HEADER_H = 26
LABEL_H = 22

sheet_w = MARGIN * 2 + PANEL_W * 3 + GAP * 2
sheet_h = MARGIN + HEADER_H + PANEL_H + LABEL_H + MARGIN
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((8, 8, 20))

hfont = _font(20, True)
lfont = _font(18, True)
htxt = hfont.render("store_card_v4_r3  —  tidal-shelf  —  round 2",
                    True, (236, 232, 214))
sheet.blit(htxt, (MARGIN, MARGIN + (HEADER_H - htxt.get_height()) // 2))

panel_y = MARGIN + HEADER_H
for i, (sid, tier) in enumerate(PANELS):
    px = MARGIN + i * (PANEL_W + GAP)
    sheet.blit(render_card(sid), (px, panel_y))
    ltxt = lfont.render(tier, True, (214, 210, 196))
    sheet.blit(ltxt, (px + (PANEL_W - ltxt.get_width()) // 2,
                      panel_y + PANEL_H + (LABEL_H - ltxt.get_height()) // 2))

out = "/home/user/skybit/docs/store_card_v4_r3/tidal-shelf/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())


# ── L* strata verification at true 162×100 ────────────────────────────────────
# Renders the RARE card, downsamples to display size with smoothscale, and
# samples key pixel positions to confirm strata distinctness + name contrast.
# Geometry at display size: inset=6, rect h=88, disc cy=44, wl_base=57,
# name centre=63, s1=69, strata midpoints at ~73 / 81 / 90.

def _srgb_lin(c):
    c /= 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _lstar(r, g, b):
    Y = 0.2126 * _srgb_lin(r) + 0.7152 * _srgb_lin(g) + 0.0722 * _srgb_lin(b)
    f = Y ** (1 / 3) if Y > 0.008856 else 7.787 * Y + 16 / 116
    return 116 * f - 16


def _contrast(La, Lb):
    def _y(L): return ((L + 16) / 116) ** 3
    hi, lo = sorted([_y(La), _y(Lb)], reverse=True)
    return (hi + 0.05) / (lo + 0.05)


card_ss = render_card("skin_tophat")
card_disp = pygame.transform.smoothscale(card_ss, (CARD_W, CARD_H))

# probe positions (x, y) in display pixels
probes = [
    ("card body above shelf",  (81, 30)),   # pure card gradient, above waterline
    ("name band bg (right)",   (140, 65)),  # warm lane away from text
    ("cool stratum 1",         (81, 73)),   # centre of first cool band (~69–77)
    ("cool stratum 2",         (81, 81)),   # centre of second cool band (~77–86)
    ("cool stratum 3",         (81, 90)),   # centre of third cool band (~86–94)
]

print("\nL* strata check at 162×100 (RARE — skin_tophat):")
Ls = {}
for label, (px2, py2) in probes:
    col = card_disp.get_at((px2, py2))
    L = _lstar(col.r, col.g, col.b)
    Ls[label] = L
    print(f"  {label:26s} ({px2:3d},{py2:2d})  "
          f"rgb({col.r:3d},{col.g:3d},{col.b:3d})  L*={L:.1f}")

# scan the full name band (y=57–69 display) for the brightest pixel so the
# contrast measurement finds actual glyph pixels rather than letter gaps
best_lum, best_col, best_xy = 0.0, None, (0, 0)
for sy in range(55, 70):
    for sx in range(8, 155):
        c = card_disp.get_at((sx, sy))
        lum = 0.2126 * _srgb_lin(c.r) + 0.7152 * _srgb_lin(c.g) + 0.0722 * _srgb_lin(c.b)
        if lum > best_lum:
            best_lum, best_col, best_xy = lum, c, (sx, sy)

L_text = _lstar(best_col.r, best_col.g, best_col.b) if best_col else 0
L_bg   = Ls.get("name band bg (right)", 0)
print(f"  name text (brightest px)   {str(best_xy):10s}  "
      f"rgb({best_col.r:3d},{best_col.g:3d},{best_col.b:3d})  "
      f"L*={L_text:.1f}")
Ls["name text (brightest px)"] = L_text

# strata distinctness: each pair should differ by >=5 L* units at display
pairs = [
    ("name band → stratum 1", "name band bg (right)", "cool stratum 1"),
    ("stratum 1 → stratum 2", "cool stratum 1",        "cool stratum 2"),
    ("stratum 2 → stratum 3", "cool stratum 2",        "cool stratum 3"),
]
print(f"\n  name contrast: {_contrast(L_text, L_bg):.1f}:1  "
      f"(text L*={L_text:.1f}, bg L*={L_bg:.1f})")
print()
for label, k1, k2 in pairs:
    diff = abs(Ls.get(k1, 0) - Ls.get(k2, 0))
    flag = "" if diff >= 3 else "  << LOW"
    print(f"  ΔL* {label:28s}: {diff:.1f}{flag}")
print()
