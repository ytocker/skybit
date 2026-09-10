"""lacquer-panel — store_card_v4_r4 concept, round 1 headless render.

Visual thesis: the bottom band abandons the speckled-metal plinth for deep wet
urushi lacquer — a near-black tier-tinted base sealed under a single diagonal
specular sweep, so the foot reads as a hand-polished lacquer plate rather than a
lit socket.  The price is recast as a vermilion hanko seal: a hand-carved
cinnabar stamp with the numeral reversed out in a paper-toned light value, so
its legibility comes from value contrast on the red field rather than from glow.

Why lacquer + hanko: it moves the card's identity toward a crafted, tactile
material story (wet lacquer, carved seal, inlaid gilt name) instead of the
neon/metal vocabulary of the sibling concepts — a distinct answer to "what the
foot is made of."

Headless (SDL dummy) -> a 3-up RARE/EPIC/LEGENDARY review sheet at SS
(324x200 panels, no downscale). Not wired into the live store; writes
docs/store_card_v4_r4/lacquer-panel/round_1.png.
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
    plain_text, font, m, SS, soft_glow, coin_glyph, _glyph_base,
    CARD_T, CARD_B, CARD_RING_BRIGHT, CARD_RING_DEEP,
    CABO_LO, CABO_HI, GEM_R, RARITY, MYSTERY, _rarity,
    lerp_color, WHITE, NEAR_BLACK,
)

# LOCKED card constants (from store_cards).
CARD_W, CARD_H = 162, 100
CARD_RAD = 17
_INSET = 6

R = 36

# Warm gilt-adjacent lettering colours: inlaid gold reading on wet lacquer.
NAME_GILT = (210, 195, 145)
SEAL_CINNABAR = (185, 40, 38)
SEAL_PAPER = (240, 230, 200)


def _lacquer_band(big, rect, plinth_top, rad, pal):
    """Fill the foot with wet urushi lacquer: a near-black tier-tinted base, one
    diagonal specular sweep to sell glossy depth, and a thin polished edge
    highlight around the perimeter.  No flecks or speckle — the material reads
    from the single moving highlight, the way real lacquer does."""
    ph = rect.bottom - plinth_top
    band_top = lerp_color(pal["deep"], (4, 4, 12), 0.5)
    band = vgrad_stops(rect.w, ph, 0,
                       [(0.0, band_top), (1.0, (3, 3, 9))], 255)

    # Clip the lacquer to the card's rounded bottom corners so it seats flush.
    body_mask = pygame.Surface((rect.w, ph), pygame.SRCALPHA)
    pygame.draw.rect(body_mask, (255, 255, 255, 255),
                     (0, plinth_top - rect.bottom, rect.w, rect.h),
                     border_radius=rad)
    band.blit(body_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

    # Diagonal specular sweep: a soft 45deg light band across the lacquer.  Peak
    # is offset toward the left so it runs under the hero disc, where wet lacquer
    # would catch the top-left key light most strongly.
    # The additive blit adds stored RGB regardless of per-pixel alpha, so the
    # sweep intensity is baked into the RGB channels (warm-white, scaled by the
    # gaussian) rather than into alpha — otherwise every set pixel blows to white.
    sweep = pygame.Surface((rect.w, ph), pygame.SRCALPHA)
    peak_u = rect.w * 0.34          # centre of the highlight along the diagonal
    sigma = rect.w * 0.16           # soft falloff width
    peak_a = 52
    for y in range(ph):
        for x in range(rect.w):
            u = x - y                # 45deg diagonal coordinate (top-left light)
            a = peak_a * math.exp(-((u - peak_u) ** 2) / (2 * sigma * sigma))
            if a >= 1.0:
                f = a / 255.0
                sweep.set_at((x, y),
                             (int(255 * f), int(250 * f), int(242 * f), 255))
    sweep.blit(body_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    band.blit(sweep, (0, 0), special_flags=pygame.BLEND_ADD)

    big.blit(band, (rect.left, plinth_top))

    # Polished edge highlight: a 1px lit keyline tracing the band perimeter, so
    # the lacquer plate reads as a discrete inlaid panel.
    edge = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.rect(edge, (*CARD_RING_BRIGHT, 80), rect,
                     width=max(1, m(1)), border_radius=rad)
    clip = pygame.Rect(rect.left, plinth_top, rect.w, ph)
    big.blit(edge, clip, area=clip)

    # Top seam: lit micro-bevel over a dark keyline so the foot reads as raised.
    bevel_y = plinth_top - max(1, m(1))
    seam = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.line(seam, (*CARD_RING_BRIGHT, 90),
                     (rect.left, bevel_y), (rect.right - 1, bevel_y),
                     max(1, m(1)))
    big.blit(seam, (0, 0))
    pygame.draw.line(big, (3, 4, 12), (rect.left, plinth_top),
                     (rect.right - 1, plinth_top), max(1, m(1)))


def _hanko_seal(big, cx, cy, price, sid):
    """A vermilion hanko: a hand-carved cinnabar stamp with the price reversed
    out in a light paper value.  Edge irregularity (per-angle radius jitter) and
    a faint ink-bleed ring outside sell a physical stamped impression; contrast
    comes from the light numeral on the dark-red field, never from glow."""
    rng = random.Random(hash(sid) & 0xffffffff)
    R_seal = m(13)
    steps = 72

    def _jitter_poly(base_r, jit):
        pts = []
        for i in range(steps):
            th = 2 * math.pi * i / steps
            rr = base_r + rng.uniform(-jit, jit)
            pts.append((cx + rr * math.cos(th), cy + rr * math.sin(th)))
        return pts

    # Ink bleed: a slightly larger, softer, darker-red impression under the seal.
    bleed = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(bleed, (150, 30, 28, 70),
                        _jitter_poly(R_seal + m(1.6), m(2)))
    big.blit(bleed, (0, 0))

    # Seal body: cinnabar fill with a hand-carved jittered rim.
    rng2 = random.Random((hash(sid) & 0xffffffff) ^ 0x5a5a)
    body_pts = []
    for i in range(steps):
        th = 2 * math.pi * i / steps
        rr = R_seal + rng2.uniform(-1.5, 1.5) * SS * 0.5
        body_pts.append((cx + rr * math.cos(th), cy + rr * math.sin(th)))
    pygame.draw.polygon(big, SEAL_CINNABAR, body_pts)
    # Darker carved rim reinforces the impressed edge without any glow.
    pygame.draw.polygon(big, (150, 28, 26), body_pts, width=max(1, m(1)))

    # Numeral reversed out in paper tone; shrink to seat inside the seal.
    txt = f"{price}"
    sz = 8.0
    f = font(sz)
    while _glyph_base(txt, f, 0).get_width() > R_seal * 1.5 and sz > 5.0:
        sz -= 0.5
        f = font(sz)
    plain_text(big, txt, f, (cx, cy), SEAL_PAPER, shadow_a=0,
               weight=m(0.7), keyline=(120, 20, 18), kw=m(0.6))


def _name_on_lacquer(big, name, cx, cy, max_w):
    """Warm gilt name centred on the lacquer, auto-shrunk to fit — reads as
    inlaid gold lettering against the wet dark ground."""
    sz = 12.0
    f = font(sz)
    while _glyph_base(name, f, 0).get_width() > max_w and sz > 7.0:
        sz -= 0.5
        f = font(sz)
    plain_text(big, name, f, (cx, cy), NAME_GILT, shadow_a=150,
               weight=m(0.9), keyline=(4, 4, 12), kw=m(1.0))


def render_card(sid):
    """Draw ONE lacquer-panel card onto a fresh SS panel (324x200) and return it."""
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
    price_cx = rect.right - m(23)
    price_cy = rect.y + m(48)

    # ── LACQUER BAND — wet urushi foot with a single diagonal specular sweep. ──
    _lacquer_band(big, rect, plinth_top, rad, pal)

    # ── HERO DISC (R=36, left-leaning; seats on the lacquer). ──
    soft_glow(big, cx, cy, m(R + 4), pal["glow"], 30, layers=8)
    cabochon(big, cx, cy, m(R), CABO_LO, CABO_HI, ring=pal["gem"], ring_a=50)
    blit_thumb(big, sid, cx, cy, int(m(R) * 1.5))
    cabochon_glass(big, cx, cy, m(R), tint=pal["gem"])

    # ── GEM CREST (locked call) ──
    facet_gem(big, rect.right - m(19), rect.y + m(19), m(GEM_R + 3),
              pal["gem"], pal["deep"])

    # ── PRICE — vermilion hanko seal, upper-right, clear of disc + gem crest. ──
    _hanko_seal(big, price_cx, price_cy, price, sid)

    # ── NAME — warm gilt, centred across the lacquer below the disc. ──
    _name_on_lacquer(big, name.upper(), rect.centerx, rect.y + m(81),
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
htxt = hfont.render("store_card_v4_r4 — lacquer-panel — round 1", True,
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

out = "/home/user/skybit/docs/store_card_v4_r4/lacquer-panel/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())

# ── L* probes — verify the reversed-out numeral + gilt name clear legibility. ──
def _lstar(rgb):
    def lin(c):
        c /= 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(v) for v in rgb[:3])
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return 903.3 * y if y <= 0.008856 else 116 * y ** (1 / 3) - 16


def _contrast(a, b):
    la, lb = _lstar(a) / 100.0, _lstar(b) / 100.0
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


r2 = pygame.Rect(m(_INSET), m(_INSET),
                 CARD_W * SS - 2 * m(_INSET), CARD_H * SS - 2 * m(_INSET))
for tier, sid in VARIANTS:
    print(f"  {tier:10s} "
          f"paper/cinnabar contrast={_contrast(SEAL_PAPER, SEAL_CINNABAR):4.1f}:1  "
          f"gilt/lacquer contrast={_contrast(NAME_GILT, (3, 3, 9)):4.1f}:1")
