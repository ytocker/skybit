"""engraved-slab — store_card_v4_r2 concept, round 2 (final) headless render.

The whole card reads as ONE carved block: the name and price are CUT INTO the
surface as incised troughs sharing one carved grammar, and the crest gem is
INTAGLIO'D into a shallow socket so a proud jewel no longer clashes with the
recesses beneath it. Round 2 answers the round-1 art-direction:

  * FLOOR now reads as a warm LIT cream ledge, not an invisible blue-violet box.
    R1 laid a faint cream wash (alpha 50) straight over the indigo body, netting
    a floor at L*~14-17 @1x — effectively black. R2 lays an OPAQUE warm base
    first, then a cream glaze, so the floor nets warm cream around L*30-40 @1x
    and the recess reads as a carved ledge catching the key.
  * BEVEL is re-biased for 1x: ONE strong dark top-inner shadow band + a warm
    bright bottom lip. At 1x this clearly reads "open at the top, lit at the
    bottom" = pressed in, instead of the R1 bottom lip merging into the keyline.
  * TYPE is inverted for the lit floor: incised letters are now a DARK pressed
    body with a warm light lower-right rim (the far cut-wall catching the key).
    Dark-on-cream keeps legibility where R1's cream-on-cream would vanish.
  * PRICE digits grow to font(9.0) with letter-tracking (each digit reads
    distinctly) and the coin glyph shrinks ~1px to make room.
  * CREST GEM sits in a carved socket ring (set-INTO the surface) AND the price
    trough drops clear of it, so the raised-gem / carved-trough clash is gone and
    each element owns its breathing room.

Headless (SDL dummy) -> a 3-up RARE/EPIC/LEGENDARY review sheet at SS (324x200,
no downscale) plus a real-scale 1x strip. Not wired into the live store; writes
docs/store_card_v4_r2/engraved-slab/round_2.png and asserts the floor L* @1x.
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
    coin_glyph, _glyph_base, _stamp_bold, _rarity, font, m, SS,
    CABO_LO, CABO_HI, CARD_T, CARD_B, CARD_RING_DEEP, CARD_RING_BRIGHT,
    GEM_R, RARITY, MYSTERY,
)

# LOCKED card constants (from store_cards).
CARD_W, CARD_H = 162, 100
CARD_RAD = 17
_INSET = 6

# Hero disc radius (logical). Fills most of the block; the carved name band
# reads in front of its lower rim like a ledge cut into the same stone.
R = 34

# ── Carved-floor recipe ───────────────────────────────────────────────────────
# The floor is an OPAQUE warm base + a cream glaze (NOT a wash over the indigo
# body). Tuned so the composited mid-floor nets a warm lit cream around L*30-40
# at 1x — comfortably clear of the body (L*~13) so the recess reads as a lit
# carved ledge rather than a dark hole, per the round-1 gate.
FLOOR_BASE_TOP = (98, 86, 60)
FLOOR_BASE_BOT = (70, 61, 43)
FLOOR_GLAZE_TOP = (204, 190, 160)
FLOOR_GLAZE_BOT = (134, 118, 88)
FLOOR_GLAZE_A = 52


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


def _carved_trough(surf, rect, radius):
    """Cut a recess INTO the carved surface so it reads as pressed-in stone:

      * an OPAQUE warm base + cream glaze floor (a genuinely LIT cream ledge, not
        a faint wash over the indigo body that crushes to blue-black at 1x),
      * ONE strong DARK top-inner shadow band hugging the top edge (the near lip
        the top-left key presses past can't reach),
      * a WARM BRIGHT bottom lip (~2px) where the far interior wall catches the
        key — together these read "open at the top, lit at the bottom" = pressed
        in, and survive the 1x downscale where a fine per-edge bevel would not,
      * a crisp dark keyline round the mouth so the cut edge is defined.
    """
    w, h = rect.w, rect.h
    rmask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(rmask, (255, 255, 255, 255), (0, 0, w, h),
                     border_radius=radius)

    # OPAQUE warm base — the removed material's lit floor colour.
    base = vgrad_stops(w, h, radius, [(0.0, FLOOR_BASE_TOP), (1.0, FLOOR_BASE_BOT)],
                       alpha=255)
    surf.blit(base, rect.topleft)
    # cream glaze lifts the floor toward warm cream where the key reaches.
    glaze = vgrad_stops(w, h, radius,
                        [(0.0, FLOOR_GLAZE_TOP), (1.0, FLOOR_GLAZE_BOT)],
                        alpha=FLOOR_GLAZE_A)
    surf.blit(glaze, rect.topleft)

    # ONE strong dark top-inner shadow band (3-4px tall), fading downward.
    band = max(2, m(4))
    top_sh = pygame.Surface((w, h), pygame.SRCALPHA)
    for yy in range(band):
        a = int(205 * (1 - yy / band) ** 1.15)
        pygame.draw.line(top_sh, (5, 5, 14, a), (0, yy), (w, yy))
    top_sh.blit(rmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(top_sh, rect.topleft)

    # warm bright bottom lip (~2px) — the lit far wall of the cut.
    lip = max(2, m(2))
    bot_lip = pygame.Surface((w, h), pygame.SRCALPHA)
    for yy in range(lip):
        a = int(200 * (1 - yy / lip))
        y = h - 1 - yy
        pygame.draw.line(bot_lip, (226, 196, 138, a), (0, y), (w, y))
    bot_lip.blit(rmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(bot_lip, rect.topleft)

    # crisp dark mouth keyline defining the cut edge in the surface.
    pygame.draw.rect(surf, (4, 4, 12), rect, width=max(1, m(1)),
                     border_radius=radius)


def _engraved_text(surf, txt, f, center, tracking=0, weight=None):
    """Incised type on the LIT cream floor: a DARK pressed letter body with a
    warm LIGHT lower-right rim (the far wall of the cut catching the top-left
    key). Dark-on-cream keeps hard contrast on the lit floor where round 1's
    cream-on-cream letters would have vanished."""
    if weight is None:
        weight = m(0.9)
    base = _glyph_base(txt, f, tracking)
    base = _stamp_bold(base, weight)
    r = base.get_rect(center=center)
    off = max(1, m(0.8))
    # warm lit lower-right rim of the incision.
    lip = base.copy()
    lip.fill((248, 234, 202, 255), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(lip, (r.x + off, r.y + off))
    # dark pressed letter body on top.
    body = base.copy()
    body.fill((42, 31, 20, 255), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(body, r.topleft)
    return r


def _name_in_trough(surf, name, cx, cy, max_w):
    """Carved item name, auto-shrunk from 9.5pt until it fits `max_w`, drawn with
    the incised dark-body / warm-lip grammar."""
    sz = 9.5
    f = font(sz)
    while _glyph_base(name, f, 0).get_width() > max_w and sz > 6.0:
        sz -= 0.5
        f = font(sz)
    _engraved_text(surf, name, f, (cx, cy), weight=m(0.9))


def _gem_socket(surf, cx, cy, r):
    """A shallow carved socket ring around the crest gem so a PROUD faceted jewel
    reads as SET INTO the slab (intaglio'd crest), sharing the pressed-in grammar
    of the troughs below instead of clashing with them: a dark inner shadow on
    the top-left ring wall, a warm lit lip on the bottom-right far wall, and a
    crisp dark cut-edge circle at the mouth."""
    sr = r + m(6)
    pad = m(3)
    ring = pygame.Surface((sr * 2 + pad * 2, sr * 2 + pad * 2), pygame.SRCALPHA)
    c = sr + pad
    # dark inner shadow on the top-left (near) wall.
    for k in range(max(2, m(2))):
        a = int(160 * (1 - k / max(2, m(2))))
        pygame.draw.arc(ring, (4, 4, 12, a),
                        (c - sr + k, c - sr + k, (sr - k) * 2, (sr - k) * 2),
                        math.radians(96), math.radians(214), max(1, m(1.2)))
    # warm lit lip on the bottom-right (far) wall catching the key.
    for k in range(max(2, m(1.5))):
        a = int(120 * (1 - k / max(2, m(1.5))))
        pygame.draw.arc(ring, (176, 148, 96, a),
                        (c - sr + k, c - sr + k, (sr - k) * 2, (sr - k) * 2),
                        math.radians(280), math.radians(392), max(1, m(1)))
    # crisp dark cut-edge circle round the socket mouth.
    pygame.draw.circle(ring, (4, 4, 12, 210), (c, c), sr, max(1, m(1)))
    surf.blit(ring, (cx - c, cy - c))


def render_card(sid):
    """Draw ONE engraved-slab card onto a fresh SS panel (324x200) and return it
    (drawn directly at SS, no smoothscale)."""
    pal = RARITY.get(_rarity(sid), MYSTERY)
    name = store_catalog.name(sid)

    big = pygame.Surface((CARD_W * SS, CARD_H * SS), pygame.SRCALPHA)
    rect = pygame.Rect(m(_INSET), m(_INSET),
                       CARD_W * SS - 2 * m(_INSET), CARD_H * SS - 2 * m(_INSET))
    rad = m(CARD_RAD)
    cx, cy = rect.centerx, rect.y + m(36)          # disc high; band cuts the foot

    # ── SHELL (locked order) — the carved block itself ──
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

    # ── GEM CREST — intaglio'd: a carved socket ring so the proud faceted gem
    #    reads as SET INTO the slab, not clashing with the carved troughs. ──
    gem_cx, gem_cy = rect.right - m(19), rect.y + m(19)
    _gem_socket(big, gem_cx, gem_cy, m(GEM_R + 3))
    facet_gem(big, gem_cx, gem_cy, m(GEM_R + 3), pal["gem"], pal["deep"])

    # ── PRICE (debossed into a small trough in the right collar, dropped clear of
    #    the gem socket so each element owns its breathing room) ──
    price_str = "480"
    pf = font(9.0)                                 # bigger digits: 480 no longer a mush blob
    ptrk = m(1.0)                                  # tracking: each digit reads distinctly
    num_w = _glyph_base(price_str, pf, ptrk).get_width()
    coin_r = m(3.5)                                # shrunk ~1px to make room for the digits
    pad = m(6)
    gapc = m(4)
    pt_w = pad + coin_r * 2 + gapc + num_w + pad
    pt_h = m(17)
    pcy = rect.y + m(50)                           # clear of the gem socket above
    pt = pygame.Rect(rect.right - m(7) - pt_w, pcy - pt_h // 2, pt_w, pt_h)
    _carved_trough(big, pt, m(6))
    coin_cx = pt.x + pad + coin_r
    coin_glyph(big, coin_cx, pt.centery, coin_r)
    _engraved_text(big, price_str, pf,
                   (coin_cx + coin_r + gapc + num_w // 2, pt.centery),
                   tracking=ptrk, weight=m(0.8))

    # ── NAME BAND (carved recess at the foot) ──
    band_h = m(19)
    band = pygame.Rect(rect.x + m(5), rect.bottom - m(4) - band_h,
                       rect.w - m(10), band_h)
    _carved_trough(big, band, m(7))
    _name_in_trough(big, name.upper(), band.centerx, band.centery,
                    band.w - m(16))

    return big, band, pt


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
htxt = hfont.render("store_card_v4_r2 — engraved-slab — round 2", True,
                    (236, 232, 214))
sheet.blit(htxt, (MARGIN, MARGIN + (HEADER_H - htxt.get_height()) // 2))

panel_y = MARGIN + HEADER_H
panels = []
bands = []
troughs = []
for i, (tier, sid) in enumerate(VARIANTS):
    px = MARGIN + i * (PANEL_W + GUTTER)
    panel, band, pt = render_card(sid)
    panels.append(panel)
    bands.append(band)
    troughs.append(pt)
    sheet.blit(panel, (px, panel_y))
    ftxt = ffont.render(tier, True, (218, 214, 200))
    sheet.blit(ftxt, (px + (PANEL_W - ftxt.get_width()) // 2,
                      panel_y + PANEL_H + (FOOTER_H - ftxt.get_height()) // 2))

# 1x real-scale strip: smoothscale each SS panel down to the live 162x100 card so
# the carved-type-at-1x survival is visible in the same sheet.
strip_label_y = panel_y + PANEL_H + FOOTER_H
ltxt = sfont.render("real scale (1x, 162x100)", True, (200, 204, 220))
sheet.blit(ltxt, (MARGIN, strip_label_y + (STRIP_LABEL_H - ltxt.get_height()) // 2))
strip_y = strip_label_y + STRIP_LABEL_H
smalls = []
for i, panel in enumerate(panels):
    px = MARGIN + i * (PANEL_W + GUTTER)
    left = px + (PANEL_W - CARD_W) // 2
    small = pygame.transform.smoothscale(panel, (CARD_W, CARD_H))
    smalls.append(small)
    sheet.blit(small, (left, strip_y))

out = "/home/user/skybit/docs/store_card_v4_r2/engraved-slab/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())


# ── L* probe (no image display): confirm the trough floor now reads as a warm
#    LIT cream ledge at 1x — the primary round-1 gate. ──
def _lstar(rgb):
    def lin(c):
        c /= 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(v) for v in rgb[:3])
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return 903.3 * y if y <= 0.008856 else 116 * y ** (1 / 3) - 16


def _window_L(surf, cx, cy, rad):
    """Mean L* over a small window — the composited floor value, robust to the
    single-pixel jitter the 1x smoothscale introduces."""
    ls, n = 0.0, 0
    for yy in range(cy - rad, cy + rad + 1):
        for xx in range(cx - rad, cx + rad + 1):
            if 0 <= xx < surf.get_width() and 0 <= yy < surf.get_height():
                ls += _lstar(surf.get_at((xx, yy)))
                n += 1
    return ls / max(1, n)


# EPIC panel; sample the NAME-BAND floor in its guaranteed-clear left margin (the
# name is centred within band.w - m(16), leaving m(8) of pure floor each side).
epic_ss = panels[1]
epic_1x = smalls[1]
band = bands[1]
# body reference (upper-left, away from any recess).
body_ss = epic_ss.get_at((int(CARD_W * SS * 0.16), int(CARD_H * SS * 0.30)))
floor_x_ss = band.x + m(5)
floor_y_ss = band.centery
floor_ss = _window_L(epic_ss, floor_x_ss, floor_y_ss, m(1))
floor_1x = _window_L(epic_1x, floor_x_ss // SS, floor_y_ss // SS, 1)
print(f"  body           rgb={tuple(body_ss)[:3]}  L*={_lstar(body_ss):5.1f}")
print(f"  floor  @SS  L*={floor_ss:5.1f}")
print(f"  floor  @1x  L*={floor_1x:5.1f}   (gate: >= 28)")
assert floor_1x >= 28, f"trough floor too dark at 1x: L*={floor_1x:.1f} < 28"
print("  OK — trough floor reads as a lit warm ledge at 1x")
