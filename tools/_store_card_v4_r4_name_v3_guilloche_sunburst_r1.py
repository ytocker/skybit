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

# Fixed, tier-agnostic palette. This treatment reads premium from GEOMETRY (an
# engine-turned radial fan), never from colour, so it stays identical across
# every rarity and can never leak a tier tell into the name band.
WARM_WHITE = (255, 255, 252)
CHAMP_HI = (218, 208, 182)
CHAMP_LO = (200, 190, 160)
INK = (6, 6, 16)
PEWTER = (160, 155, 140)


def _name_guilloche_sunburst(big, name, cx, cy, max_w, rect):
    """Guilloche-sunburst nameplate: the caps ride a fine engine-turned fan —
    the banknote / watch-dial shimmer that signals value with pure geometry and
    no colour. A near-black->pewter band grounds thin champagne spokes that
    converge just under the baseline; overlaps accumulate into a soft continuous
    glow, and each spoke feathers out before the band edge so nothing reads as a
    hard ray. Colour stays fixed on every tier so the shimmer, not a hue, is the
    premium tell."""
    plinth_top = rect.y + m(72)
    band_top = plinth_top
    band_bot = rect.bottom
    bh = band_bot - band_top
    rad = m(CARD_RAD)

    # Near-black -> pewter vertical ground: dark at the seam so the fan ignites,
    # lifting toward a cool metal grey at the foot for a brushed-dial base.
    panel = pygame.Surface((rect.w, bh), pygame.SRCALPHA)
    panel.blit(vgrad_stops(rect.w, bh, 0, [(0.0, INK), (1.0, PEWTER)], 255), (0, 0))

    # Virtual origin sits just BELOW the baseline centre and a hair past the
    # foot, so the spokes rake steeply up through the whole band and read as one
    # fan rather than a starburst pinned inside the name.
    ox = cx - rect.left
    oy = (band_bot + m(4)) - band_top
    spokes = 22
    half_span = math.radians(74.0)
    reach = bh * 2.4          # overshoot the top edge; the mask trims the rays
    steps = 26
    for i in range(spokes):
        frac = (i / (spokes - 1)) * 2.0 - 1.0
        ang = frac * half_span
        dx = math.sin(ang)
        dy = -math.cos(ang)
        # A single accumulation surface per spoke so its many faded segments do
        # not self-blend, but neighbouring spokes DO composite over one another
        # when blitted — that cross-build is what makes the shimmer continuous.
        sp = pygame.Surface((rect.w, bh), pygame.SRCALPHA)
        base_a = 44 + int(26 * (1.0 - abs(frac)))   # centre spokes a touch hotter
        for s in range(steps):
            t0 = s / steps
            t1 = (s + 1) / steps
            # Feather the outer third to nothing so no spoke ends on a hard tip.
            fade = 1.0 if t1 < 0.62 else max(0.0, 1.0 - (t1 - 0.62) / 0.38)
            a = int(base_a * fade)
            if a <= 0:
                continue
            col = lerp_color(CHAMP_HI, CHAMP_LO, t1)
            x0 = ox + dx * reach * t0
            y0 = oy + dy * reach * t0
            x1 = ox + dx * reach * t1
            y1 = oy + dy * reach * t1
            pygame.draw.line(sp, (*col, a), (x0, y0), (x1, y1), 1)
        panel.blit(sp, (0, 0))

    # One-two faint concentric guilloche arcs share the fan's origin, banding the
    # radial rays with a whisper of a curve for the woven engine-turned read.
    for rr, aa in ((bh * 0.9, 26), (bh * 1.55, 18)):
        arc = pygame.Surface((rect.w, bh), pygame.SRCALPHA)
        box = pygame.Rect(ox - rr, oy - rr, rr * 2, rr * 2)
        pygame.draw.arc(arc, (*CHAMP_HI, aa), box,
                        math.pi / 2 - half_span, math.pi / 2 + half_span, 1)
        panel.blit(arc, (0, 0))

    # Clip the whole plate to the band's rounded silhouette (square top seam,
    # rounded foot) exactly like the neutral band it overlays.
    mask = pygame.Surface((rect.w, bh), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255),
                     (0, plinth_top - rect.bottom, rect.w, rect.h), border_radius=rad)
    panel.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(panel, (rect.left, band_top))

    # Caps: tracking-first then shrink, so short names breathe and long names
    # still clear the price rail.
    size = 12.5
    f = font(size)
    tracking = m(1.0)
    while tracking > 0 and _glyph_base(name, f, tracking).get_width() > max_w:
        tracking -= 1
    tracking = max(m(0.4), tracking)
    while size > 9.0 and _glyph_base(name, f, tracking).get_width() > max_w:
        size -= 0.5
        f = font(size)
    # Warm-white type with a crisp ink keyline + drop shadow so the caps punch
    # clear of the shimmer without any coloured halo.
    plain_text(big, name, f, (cx, cy), WARM_WHITE, shadow_a=150, tracking=tracking,
               weight=m(0.9), keyline=INK, kw=m(0.9))

    # The lone colour accent allowed: a single CARD_RING_BRIGHT hairline tracing
    # the band's lower edge (bottom run + the two foot corners), nothing more.
    edge = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    col = (*CARD_RING_BRIGHT, 205)
    w = max(1, m(1))
    yb = rect.bottom - 1
    pygame.draw.line(edge, col, (rect.left + rad, yb), (rect.right - 1 - rad, yb), w)
    pygame.draw.arc(edge, col, (rect.left, rect.bottom - 2 * rad, 2 * rad, 2 * rad),
                    math.pi, math.pi * 1.5, w)
    pygame.draw.arc(edge, col, (rect.right - 1 - 2 * rad, rect.bottom - 2 * rad, 2 * rad, 2 * rad),
                    math.pi * 1.5, math.pi * 2, w)
    big.blit(edge, (0, 0))


def _neutral_band(big, rect, plinth_top, rad):
    ph = rect.bottom - plinth_top
    band = vgrad_stops(rect.w, ph, 0, [(0.0, (28, 24, 44)), (1.0, (14, 12, 26))], 255)
    mask = pygame.Surface((rect.w, ph), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255,255,255,255), (0, plinth_top - rect.bottom, rect.w, rect.h), border_radius=rad)
    band.blit(mask, (0,0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(band, (rect.left, plinth_top))
    seam = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.line(seam, (*CARD_RING_BRIGHT, 80), (rect.left, plinth_top - max(1,m(1))), (rect.right-1, plinth_top - max(1,m(1))), max(1,m(1)))
    big.blit(seam, (0,0))
    pygame.draw.line(big, (6,5,12), (rect.left, plinth_top), (rect.right-1, plinth_top), max(1,m(1)))


def _simple_price(big, cx, cy, price, pal):
    f = font(9.0)
    txt = f"{price}"
    nw = _glyph_base(txt, f, 0).get_width()
    ar = nw // 2 + m(6)
    rimbox = pygame.Rect(cx-ar, cy-ar, ar*2, ar*2)
    arc = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.arc(arc, (*CARD_RING_BRIGHT, 140), rimbox, math.radians(60), math.radians(210), max(1,m(1)))
    big.blit(arc, (0,0))
    plain_text(big, txt, f, (cx,cy), lerp_color(pal["gem"], WHITE, 0.25), shadow_a=0, weight=m(0.9))


def render_card(sid):
    pal = RARITY.get(_rarity(sid), MYSTERY)
    name = store_catalog.name(sid)
    price = store_catalog.cost(sid)
    big = pygame.Surface((CARD_W*SS, CARD_H*SS), pygame.SRCALPHA)
    rect = pygame.Rect(m(_INSET), m(_INSET), CARD_W*SS - 2*m(_INSET), CARD_H*SS - 2*m(_INSET))
    rad = m(CARD_RAD)
    drop_shadow(big, rect, rad, blur=m(8), alpha=160, dy=m(4))
    big.blit(vgrad(rect.w, rect.h, rad, CARD_T, CARD_B, 252, gamma=1.15), rect.topleft)
    top_sheen(big, rect, rad, m(30), peak=62)
    contact_shadow(big, rect, rad, m(9), alpha=120)
    pygame.draw.rect(big, (4,5,16), rect, width=max(1,m(2)), border_radius=rad)
    bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 235), w=max(1,m(2.0)))
    cx = rect.left + m(40)
    cy = rect.y + m(38)
    plinth_top = rect.y + m(72)
    _neutral_band(big, rect, plinth_top, rad)
    soft_glow(big, cx, cy, m(R+4), pal["glow"], 30, layers=8)
    cabochon(big, cx, cy, m(R), CABO_LO, CABO_HI, ring=pal["gem"], ring_a=50)
    blit_thumb(big, sid, cx, cy, int(m(R)*1.5))
    cabochon_glass(big, cx, cy, m(R), tint=pal["gem"])
    facet_gem(big, rect.right - m(19), rect.y + m(19), m(GEM_R+3), pal["gem"], pal["deep"])
    _simple_price(big, rect.right - m(23), rect.y + m(48), price, pal)
    _name_guilloche_sunburst(big, name.upper(), rect.centerx, rect.y + m(81), rect.w - m(26), rect)
    return big


VARIANTS = [("RARE","skin_tophat"),("EPIC","skin_prism"),("LEGENDARY","skin_kitsune")]
PANEL_W, PANEL_H = CARD_W*SS, CARD_H*SS
MARGIN, GUTTER, HEADER_H, FOOTER_H = 10, 8, 26, 22
sheet_w = MARGIN*2 + PANEL_W*3 + GUTTER*2
sheet_h = MARGIN + HEADER_H + PANEL_H + FOOTER_H + MARGIN
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((8,8,20))
hfont = _font(20,True); ffont = _font(18,True)
htxt = hfont.render("store_card_v4_r4_name_v3 — guilloche-sunburst — round 1", True, (236,232,214))
sheet.blit(htxt, (MARGIN, MARGIN + (HEADER_H - htxt.get_height())//2))
panel_y = MARGIN + HEADER_H
for i,(tier,sid) in enumerate(VARIANTS):
    px = MARGIN + i*(PANEL_W+GUTTER)
    sheet.blit(render_card(sid), (px, panel_y))
    ftxt = ffont.render(tier, True, (218,214,200))
    sheet.blit(ftxt, (px+(PANEL_W-ftxt.get_width())//2, panel_y+PANEL_H+(FOOTER_H-ftxt.get_height())//2))
out = "/home/user/skybit/docs/store_card_v4_r4_name_v3/guilloche-sunburst/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())
