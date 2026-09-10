"""ribbon-wrap — store_card_v4_r2 concept, round 2 (final) headless render.

A WRAPPED REWARD. The disc-led indigo card gains a real silhouette change: a
tier-tinted SILK RIBBON crosses the lower card horizontally, tucks BEHIND the
hero disc mid-run, and is CLOSED at its right end by a warm WAX CARTOUCHE that
carries the price. Gift/reward grammar without touching the locked shell or
hero stack.

Round 2 answers the art-director notes:

  * PRICE LEGIBILITY — the round wax wafer (r~5px at 1x, too small to hold a
    5-char price like "3,500") is REPLACED by a horizontal wax CARTOUCHE — a
    warm pill wider than tall — so the price renders as distinct cream glyphs
    at 8pt even at the live 1x size.
  * DISC TUCK — the disc is lowered so its dome bisects the FULL ribbon band
    (both upper leaf AND lower leaf), so the ribbon genuinely disappears behind
    the disc and re-emerges as visible silk on both sides where the fold-shadows
    land.
  * NAME OFF THE CREASE — the cream name is centred on the UPPER LEAF (crease -
    m(5)), not on the seam, so the dark crease no longer bisects the letters.
    The leaf is proportioned (upper > lower) to hold the name clear of both the
    top edge and the crease.
  * LONG NAMES — the disc is trimmed (R=30) and the left run widened so the
    longest names (e.g. GENTLEMAN, 9 chars) fit at >= 7pt; auto-shrink covers
    the rest.
  * SEAL vs GEM MATERIAL — the wax cartouche is unmistakably NOT the faceted
    crystal crest: a warm sealing-wax hue (leaned only faintly to the tier), a
    soft matte dome with a broad low sheen (no hot pip, no facet lines), a
    pressed-emblem rim, and a rounded pill silhouette.

Headless (SDL dummy) -> a 3-up RARE/EPIC/LEGENDARY review sheet at SS
(324x200 panels, no downscale) + a real-scale 1x strip so the name/price caps
are checked at the live 162x100 size. Not wired into the live store; writes
docs/store_card_v4_r2/ribbon-wrap/round_2.png.
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

from game.draw import lerp_color, NEAR_BLACK, WHITE
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

# Hero disc: R=30 — trimmed from the portrait-vignette dome so the ribbon's left
# run stays wide enough to print a long name (GENTLEMAN, 9 chars) at >= 7pt
# without the disc eating the run.
R = 30

# Cream shared by the name AND the cartouche numerals — one warm type value so
# nothing on the card has to carry legibility on gold; only the gem/wax keep hue.
CREAM_LABEL = (236, 230, 208)

# Warm sealing-wax base for the price cartouche. Kept a terracotta amber for
# EVERY tier (leaned only faintly toward the tier) so the wax reads as a
# different MATERIAL from the cool faceted crystal crest, not just a re-tint.
WAX_BASE = (172, 96, 52)


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


def _ribbon(surf, rect, ribbon_cy, th, disc_cx, disc_cy, disc_r, pal):
    """A THICK folded silk ribbon crossing the lower card, forked at both edges,
    tucking behind the hero disc. Built from TWO vgrad_stops strips reading as a
    fold — a TALL lit upper leaf over a SHORTER shaded lower leaf meeting at a
    crease — then swallowtail-masked at the ends. The upper leaf is the taller
    of the two so it can carry the printed name clear of BOTH its top edge and
    the crease. Returns (crease_y, left_x, right_x): the seam line (so the name
    can sit above it) and the x where the disc rim meets the band centre-line (so
    the fold-shadows land on the tuck)."""
    x0 = rect.x + m(1)
    x1 = rect.right - m(1)
    w = x1 - x0
    y0 = ribbon_cy - th // 2
    notch = m(11)                                   # swallowtail depth at each end
    # UPPER leaf larger than the lower so the name clears the crease: the fold is
    # seen slightly from above, which reads as a natural silk drape anyway.
    upper_h = int(th * 0.68)
    lower_h = th - upper_h
    crease_y = y0 + upper_h

    hi = lerp_color(pal["gem"], WHITE, 0.34)        # lit silk crown
    mid = pal["gem"]
    glow = pal["glow"]
    deep = pal["deep"]
    sh = lerp_color(pal["deep"], NEAR_BLACK, 0.18)  # deep fold underside

    band = pygame.Surface((w, th), pygame.SRCALPHA)
    # upper leaf: bright crown easing to mid at the crease (the sheen the cream
    # name reads against).
    band.blit(vgrad_stops(w, upper_h, 0,
                          [(0.0, hi), (0.55, glow), (1.0, mid)], 255, gamma=1.05),
              (0, 0))
    # lower leaf: mid rolling to deep — the shaded fold that catches under the crown.
    band.blit(vgrad_stops(w, lower_h, 0,
                          [(0.0, lerp_color(mid, deep, 0.25)), (0.6, deep),
                           (1.0, sh)], 255, gamma=1.05),
              (0, upper_h))
    # crease: a thin dark seam with a bright kiss just above = the fold ridge.
    pygame.draw.line(band, (*NEAR_BLACK, 150), (0, upper_h), (w, upper_h), max(1, m(0.8)))
    pygame.draw.line(band, (255, 250, 236, 90), (0, upper_h - m(1)),
                     (w, upper_h - m(1)), max(1, m(0.6)))

    # swallowtail: notch a V into each end so the ribbon forks at the card edges.
    poly = [(0, 0), (w, 0), (w - notch, th // 2), (w, th),
            (0, th), (notch, th // 2)]
    pmask = pygame.Surface((w, th), pygame.SRCALPHA)
    pygame.draw.polygon(pmask, (255, 255, 255, 255), poly)
    band.blit(pmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

    # soft cast shadow under the whole band so it lifts off the card body.
    sh_surf = pygame.Surface((w, th), pygame.SRCALPHA)
    pygame.draw.polygon(sh_surf, (0, 0, 0, 120), poly)
    surf.blit(sh_surf, (x0, y0 + m(2)))
    surf.blit(band, (x0, y0))

    # fold-shadows: where the ribbon dives under the disc it should darken. The
    # disc rim meets the band centre-line at +/- halfw of the disc centre; the
    # disc now sits low enough that its dome covers the FULL band height at the
    # centre, so each fold-shadow re-emerges onto visible silk (both leaves) on
    # its side, densest right at the rim and fading outward along the silk.
    dy = ribbon_cy - disc_cy
    halfw = int(math.sqrt(max(0.0, disc_r * disc_r - dy * dy)))
    left_x = disc_cx - halfw
    right_x = disc_cx + halfw
    tuck_w = m(13)
    for side in ("L", "R"):
        tuck = pygame.Surface((tuck_w, th), pygame.SRCALPHA)
        for i in range(tuck_w):
            d = (tuck_w - 1 - i) if side == "L" else i   # px from the disc rim
            a = int(125 * (1 - d / tuck_w) ** 1.4)
            pygame.draw.line(tuck, (0, 0, 0, a), (i, 0), (i, th))
        bx = (left_x - tuck_w) if side == "L" else right_x
        surf.blit(tuck, (bx, y0))

    # thin dark silk-printed edge round the whole fork so the caps read crisp.
    abspoly = [(x0 + px, y0 + py) for px, py in poly]
    pygame.draw.polygon(surf, (6, 6, 16), abspoly, width=max(1, m(1.2)))
    return crease_y, left_x, right_x


def _name_on_ribbon(surf, name, cx, cy, max_w, max_h):
    """Cream item name printed on the ribbon's UPPER LEAF, tight dark keyline,
    auto-shrunk from 8.5pt in 0.5 steps so it fits the visible left run in BOTH
    width (max_w) and the leaf height (max_h) — the longest names land near 7pt,
    which stays legible at the live 1x size."""
    sz = 8.5
    f = font(sz)
    while sz > 6.5:
        g = _glyph_base(name, f, 0)
        if g.get_width() <= max_w and g.get_height() <= max_h:
            break
        sz -= 0.5
        f = font(sz)
    plain_text(surf, name, f, (cx, cy), CREAM_LABEL, shadow_a=140,
               weight=m(0.9), keyline=(8, 6, 16), kw=m(0.9))


def _wax_cartouche(surf, cx, cy, digits, pal):
    """A horizontal WAX CARTOUCHE closing the ribbon's right end and carrying the
    price. A warm sealing-wax pill (wider than tall) with a soft MATTE dome, a
    broad low sheen (no hot pip), a pressed rim, and the price in distinct cream
    glyphs. Deliberately NOT the faceted crystal crest: warm hue, rounded
    silhouette, no sharp facet lines — a different material read entirely."""
    # size to the digits at 8pt (drops to 7pt only for very long prices) so the
    # numerals are legible at 1x; the pill widens to hold them + warm padding.
    sz = 8.0
    f = font(sz)
    max_inner = m(46)
    while sz > 7.0 and _glyph_base(digits, f, 0).get_width() > max_inner:
        sz -= 0.5
        f = font(sz)
    num_w = _glyph_base(digits, f, 0).get_width()
    h = m(13)
    w = num_w + m(18)
    rad = h // 2
    r = pygame.Rect(cx - w // 2, cy - h // 2, w, h)

    # warm bloom so the wax seats into the collar (warmer than the tier glow).
    soft_glow(surf, cx, cy, w // 2 + m(2),
              lerp_color(pal["glow"], (214, 132, 78), 0.5), 18, layers=7)
    # cast shadow onto the silk beneath so the seal reads pressed ONTO the ribbon.
    csh = pygame.Surface((w + m(4), h + m(4)), pygame.SRCALPHA)
    pygame.draw.rect(csh, (0, 0, 0, 120), csh.get_rect(), border_radius=rad + m(2))
    surf.blit(csh, (r.x - m(2), r.y - m(2) + m(2)))

    # matte wax dome: warm hue leaned only faintly to the tier, a gentle
    # crown->underside gradient (soft gamma = a rounded, un-crystalline dome).
    wax = lerp_color(WAX_BASE, pal["gem"], 0.22)
    crown = lerp_color(wax, WHITE, 0.20)
    shade = lerp_color(wax, NEAR_BLACK, 0.36)
    body = vgrad_stops(w, h, rad, [(0.0, crown), (0.42, wax), (1.0, shade)],
                       255, gamma=1.18)
    surf.blit(body, r.topleft)

    # broad MATTE sheen across the upper band — low alpha, wide falloff, no hot
    # pip — the diffuse highlight of soft wax, unlike the gem's sharp specular.
    sheen = pygame.Surface((w, h), pygame.SRCALPHA)
    sh_h = int(h * 0.55)
    for y in range(sh_h):
        a = int(58 * (1 - y / sh_h) ** 1.5)
        pygame.draw.line(sheen, (255, 242, 224, a), (0, y), (w, y))
    smask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(smask, (255, 255, 255, 255), smask.get_rect(),
                     border_radius=rad)
    sheen.blit(smask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(sheen, r.topleft, special_flags=pygame.BLEND_ADD)

    # pressed rim: a dark warm contact keyline UNDER a fine warm-gold bevel — a
    # stamped-into-wax edge, no facet lines.
    warm_rim = lerp_color(WAX_BASE, (255, 214, 156), 0.55)
    pygame.draw.rect(surf, (44, 18, 8), r, width=max(1, m(1.2)), border_radius=rad)
    pygame.draw.rect(surf, (*warm_rim, 150), r.inflate(-m(1), -m(1)),
                     width=max(1, m(0.7)), border_radius=max(1, rad - m(1)))

    # the payload: price in distinct cream glyphs with a warm-dark keyline so it
    # reads pressed into the wax and stays legible on the warm dome.
    plain_text(surf, digits, f, (cx, cy), CREAM_LABEL, shadow_a=0,
               weight=m(0.9), keyline=(58, 24, 12), kw=m(0.7))


def render_card(sid):
    """Draw ONE ribbon-wrap card onto a fresh SS panel (324x200) and return it
    (drawn directly at SS, no smoothscale)."""
    pal = RARITY.get(_rarity(sid), MYSTERY)
    name = store_catalog.name(sid)
    price = f"{store_catalog.cost(sid):,}" if store_catalog.exists(sid) else "0"

    big = pygame.Surface((CARD_W * SS, CARD_H * SS), pygame.SRCALPHA)
    rect = pygame.Rect(m(_INSET), m(_INSET),
                       CARD_W * SS - 2 * m(_INSET), CARD_H * SS - 2 * m(_INSET))
    rad = m(CARD_RAD)
    # Disc lowered (cy = rect.y + m(41)) so its dome bisects the FULL ribbon band
    # rather than resting on the upper leaf; ribbon rides just below at m(64).
    cx, cy = rect.centerx, rect.y + m(41)
    disc_r = m(R)
    ribbon_cy = rect.y + m(64)
    ribbon_th = m(16)

    # ── SHELL (locked order) ──
    drop_shadow(big, rect, rad, blur=m(8), alpha=160, dy=m(4))
    big.blit(vgrad(rect.w, rect.h, rad, CARD_T, CARD_B, 252, gamma=1.15),
             rect.topleft)
    top_sheen(big, rect, rad, m(30), peak=62)
    contact_shadow(big, rect, rad, m(9), alpha=120)
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 235),
              w=max(1, m(2.0)))

    # ── RIBBON (before the disc so the dome occludes its mid-run) ──
    crease_y, left_x, right_x = _ribbon(big, rect, ribbon_cy, ribbon_th,
                                        cx, cy, disc_r, pal)

    # ── HERO DISC (locked stack) ──
    soft_glow(big, cx, cy, m(R + 3), pal["glow"], 34, layers=9)
    cabochon(big, cx, cy, disc_r, CABO_LO, CABO_HI, ring=pal["gem"], ring_a=55)
    blit_thumb(big, sid, cx, cy, disc_r * 0.66)
    cabochon_glass(big, cx, cy, disc_r, tint=pal["gem"])
    _hero_specular(big, cx, cy, disc_r)

    # ── NAME on the UPPER LEAF of the visible left run (above the crease) ──
    run_l = rect.x + m(6)
    run_r = left_x - m(3)
    name_max_h = (crease_y - (ribbon_cy - ribbon_th // 2)) - m(3)  # leaf minus margin
    _name_on_ribbon(big, name.upper(), (run_l + run_r) // 2, crease_y - m(5),
                    max(m(20), run_r - run_l), name_max_h)

    # ── WAX CARTOUCHE — closes the ribbon's RIGHT end, carrying the price. Sits
    #    on the visible right run, clear of the disc tuck and well below the gem. ──
    _wax_cartouche(big, rect.right - m(21), ribbon_cy - m(2), price, pal)

    # ── GEM CREST (locked call) ──
    facet_gem(big, rect.right - m(19), rect.y + m(19), m(GEM_R + 3),
              pal["gem"], pal["deep"])

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
htxt = hfont.render("store_card_v4_r2 — ribbon-wrap — round 2", True,
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
# the name/price caps are verified at the size the player actually sees.
strip_label_y = panel_y + PANEL_H + FOOTER_H
ltxt = sfont.render("real scale (1x, 162x100)", True, (200, 204, 220))
sheet.blit(ltxt, (MARGIN, strip_label_y + (STRIP_LABEL_H - ltxt.get_height()) // 2))
strip_y = strip_label_y + STRIP_LABEL_H
for i, panel in enumerate(panels):
    px = MARGIN + i * (PANEL_W + GUTTER)
    left = px + (PANEL_W - CARD_W) // 2
    small = pygame.transform.smoothscale(panel, (CARD_W, CARD_H))
    sheet.blit(small, (left, strip_y))

out = "/home/user/skybit/docs/store_card_v4_r2/ribbon-wrap/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())

# ── L* probes (no image display) so ribbon-face + price legibility are checked
#    numerically, per the notes, without ever viewing the PNG. ──
if "--probe" in sys.argv:
    def _lstar(rgb):
        def lin(c):
            c /= 255.0
            return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
        r, g, b = (lin(v) for v in rgb[:3])
        y = 0.2126 * r + 0.7152 * g + 0.0722 * b
        return 903.3 * y if y <= 0.008856 else 116 * y ** (1 / 3) - 16

    r = pygame.Rect(m(_INSET), m(_INSET),
                    CARD_W * SS - 2 * m(_INSET), CARD_H * SS - 2 * m(_INSET))
    dcx, dcy = r.centerx, r.y + m(41)
    ribbon_cy = r.y + m(64)
    for tier, sid in VARIANTS:
        pal = RARITY[_rarity(sid)]
        panel = render_card(sid)
        # ribbon upper-leaf face: sample the lit silk on the left run, off the caps.
        face = panel.get_at((r.x + m(15), ribbon_cy - m(5)))
        # cartouche dome: sample the warm wax crown, off the digits.
        cart = panel.get_at((r.right - m(21) - m(11), ribbon_cy - m(2) - m(3)))
        # price legibility: count high-value (cream) pixels across the cartouche
        # digit band — a nonzero, well-separated count means distinct glyphs.
        band_y = ribbon_cy - m(2)
        cream_px = 0
        for xx in range(r.right - m(21) - m(18), r.right - m(21) + m(18)):
            if _lstar(panel.get_at((xx, band_y))) > 62:
                cream_px += 1
        print(f"  {tier:10s} ribbon_face L*={_lstar(face):5.1f}  "
              f"wax_dome L*={_lstar(cart):5.1f}  cream_run_px={cream_px}")
