"""portrait-plate — store_card_v3_tl concept, round 2 headless render.

A calm, premium "portrait framed under glass" card. A large cabochon hero sits
in the upper 60% of the body; a gem crest anchors the top-LEFT corner while the
price rides a dark-glass pill top-RIGHT; the item name lands on a slim frosted
footer plate along the bottom. Rarity is now carried primarily by the disc tint
+ a tier-sized crest (readable in grayscale), with the gutter halo demoted to a
clean symmetric dim glow.

Round-2 revisions off the art-director notes:
  1. Footer reads as a frosted PLATE, not a seam — cool desaturated fill lifted
     well above the body, a 1px inner top-shadow so the name sits ON the plate,
     and a thicker brighter gold keyline.
  2. The dome mid-interior floor is lifted with a feathered additive frosted
     surface so it stops reading as a hollow socket, while the caustic + top
     specular stay the brightest peaks.
  3. EPIC/LEGENDARY get a compensating white crescent so every dome's specular
     equalises across tiers (the muted-glass EPIC no longer under-reads).
  4. The gutter halo is a clean symmetric dim glow — disc tint + crest carry
     rarity — eliminating the old asymmetric top-smear.
  5. Crest specular capped below pure white; crest size steps per tier
     (RARE/EPIC/LEGENDARY = GEM_R+1/+2/+3) so rarity reads in grayscale too.

Headless (SDL dummy) → a 3-up RARE/EPIC/LEGENDARY review sheet at SS
(324×200, no downscale) + a real-scale 1x strip (162×100). Not wired into the
live store; writes docs/store_card_v3_tl/portrait-plate/round_2.png.
"""
import math
import os

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import sys

sys.path.insert(0, "/home/user/skybit")

import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from game.draw import lerp_color, NEAR_BLACK, WHITE
from game.hud import _font
from game.store_cards import (
    vgrad, drop_shadow, bevel_rim, top_sheen, contact_shadow,
    cabochon, cabochon_glass, blit_thumb, plain_text,
    font, m, SS, CABO_LO, CABO_HI, CARD_T, CARD_B,
    CARD_RING_DEEP, CARD_RING_BRIGHT, GEM_R, GOLD_DEEP,
)

# LOCKED card constants (from store_cards).
CARD_W, CARD_H = 162, 100
CARD_RAD = 17
_INSET = 6

# The portrait disc: R=24 logical leaves a generous indigo gutter for the tier
# glow AND clears the bottom footer name-plate. Centred high (upper 60%) so the
# frosted footer never crowds the glass.
R = 24


def _crest_gem(surf, cx, cy, r, base, deep):
    """Local copy of store_cards.facet_gem with the single specular pip pulled
    OFF pure white (→230) so the corner crest never out-glares the hero dome.
    Everything else is the locked 8-facet brilliant."""
    body = base
    t_table = lerp_color(body, WHITE, 0.34)
    t_hi = lerp_color(body, WHITE, 0.55)
    t_sh = lerp_color(body, deep, 0.5)
    t_dk = lerp_color(deep, NEAR_BLACK, 0.32)
    t_key = lerp_color(deep, NEAR_BLACK, 0.5)

    seat = pygame.Surface((r * 2 + m(10), r * 2 + m(10)), pygame.SRCALPHA)
    sc = r + m(5)
    pygame.draw.circle(seat, (0, 0, 0, 175), (sc, sc), r + m(4))
    pygame.draw.circle(seat, (*GOLD_DEEP, 115), (sc, sc), r + m(4), max(1, m(0.8)))
    surf.blit(seat, (cx - sc, cy - sc))

    n = 8
    rot = -math.pi / 2 - math.pi / n
    girdle = [(cx + r * math.cos(rot + 2 * math.pi * i / n),
               cy + r * math.sin(rot + 2 * math.pi * i / n)) for i in range(n)]
    tr = r * 0.46
    table = [(cx + tr * math.cos(rot + 2 * math.pi * i / n),
              cy + tr * math.sin(rot + 2 * math.pi * i / n)) for i in range(n)]
    lx, ly = -0.7071, -0.7071
    for i in range(n):
        a = girdle[i]
        b = girdle[(i + 1) % n]
        ta = table[i]
        tb = table[(i + 1) % n]
        mx = (a[0] + b[0]) / 2 - cx
        my = (a[1] + b[1]) / 2 - cy
        ml = math.hypot(mx, my) or 1
        d = (mx / ml) * lx + (my / ml) * ly
        f = (d + 1) / 2
        col = lerp_color(lerp_color(t_dk, t_sh, min(1.0, f * 2)),
                         t_hi, max(0.0, (f - 0.5) * 2))
        pygame.draw.polygon(surf, col, [a, b, tb, ta])
    pygame.draw.polygon(surf, t_table, table)
    pygame.draw.polygon(surf, t_key, girdle, width=max(1, m(0.6)))
    for i in range(n):
        pygame.draw.line(surf, (*t_key, 190), girdle[i], table[i], max(1, m(0.4)))
    # capped specular pip: 230 not 255, so the crest can't blow past the dome.
    pr = max(1, int(r * 0.24))
    pip = pygame.Surface((pr * 2 + m(2), pr * 2 + m(2)), pygame.SRCALPHA)
    pygame.draw.circle(pip, (230, 230, 230, 250), (pr + m(1), pr + m(1)), pr)
    surf.blit(pip, (cx - pr - int(r * 0.26), cy - pr - int(r * 0.26)),
              special_flags=pygame.BLEND_ADD)


def _disc_tint(surf, cx, cy, r, color, deep, peak=55, base=22):
    """A tier colour veil INSIDE the disc, clipped to the glass. It warms the
    cool CABO_LO→CABO_HI dome away from the indigo body and pulls a bright skin
    highlight toward the tier hue so it stops blowing out. Rim-biased (peak >
    base) so the portrait's face reads through while the surround takes the hue."""
    pad = 2
    tint = pygame.Surface((r * 2 + pad * 2, r * 2 + pad * 2), pygame.SRCALPHA)
    c = r + pad
    for i in range(r, 0, -1):
        f = i / r
        col = lerp_color(color, deep, f ** 1.3)
        a = int(base + (peak - base) * f ** 1.3)
        pygame.draw.circle(tint, (*col, a), (c, c), i, width=2)
    tmask = pygame.Surface(tint.get_size(), pygame.SRCALPHA)
    pygame.draw.circle(tmask, (255, 255, 255, 255), (c, c), r - m(1))
    tint.blit(tmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(tint, (cx - c, cy - c))


def _interior_floor(surf, cx, cy, r, warm_off):
    """Lift the dome's mid-interior floor so the band above the caustic stops
    reading as a hollow socket. A feathered cool-frosted disc (~0.55×R) added
    into the glass raises the floor toward ~45-55 lum while the crescent caustic
    and top specular, painted after, stay the brightest peaks. warm_off nudges
    the red channel per tier so the floor keeps a hint of the tier hue."""
    fr = int(r * 0.55)
    d = fr * 2 + 2
    floor = pygame.Surface((d, d), pygame.SRCALPHA)
    for i in range(fr, 0, -1):
        f = i / fr                                  # 1 rim .. 0 centre
        # brightest at centre, feathering to nothing at the edge so there is no
        # hard disc lip inside the glass.
        a = int(150 * (1 - f) ** 0.7)
        pygame.draw.circle(floor, (40 + warm_off, 42, 75, a), (fr + 1, fr + 1),
                           i, width=2)
    surf.blit(floor, (cx - fr - 1, cy - fr - 1),
              special_flags=pygame.BLEND_RGBA_ADD)


def _crescent(surf, cx, cy, r, color, alpha):
    """A THIN upper-left crescent caustic INSIDE the glass, masked to the disc.
    A tall off-centre ellipse minus a shifted copy leaves only the sliver hugging
    the upper-left rim. Reused for the base caustic (all tiers) and the EPIC/
    LEGENDARY compensating specular so every dome equalises."""
    d = r * 2
    cres = pygame.Surface((d, d), pygame.SRCALPHA)
    ell = pygame.Rect(0, 0, int(r * 0.9), int(r * 1.5))
    ell.center = (int(r * 0.62), int(r * 0.58))
    pygame.draw.ellipse(cres, (*color, alpha), ell)
    sub = pygame.Surface((d, d), pygame.SRCALPHA)
    ell2 = ell.copy()
    ell2.move_ip(m(3), m(2))
    pygame.draw.ellipse(sub, (255, 255, 255, 255), ell2)
    cres.blit(sub, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
    cmask = pygame.Surface((d, d), pygame.SRCALPHA)
    pygame.draw.circle(cmask, (255, 255, 255, 255), (r, r), r - m(1))
    cres.blit(cmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(cres, (cx - r, cy - r))


def _gutter_aura(surf, cx, cy, disc_r, glow_r, color, peak=45, layers=18):
    """A clean, SYMMETRIC dim tier glow living only beyond the disc rim. Demoted
    from a rarity carrier (that leaves to the disc tint + crest) to a quiet halo:
    low peak so the gutters take a faint even tint with no hot top-smear. Normal
    alpha-carry blits so the colour reads as a tint, not a white bloom."""
    for i in range(1, layers + 1):
        r = int(disc_r + (glow_r - disc_r) * i / layers)
        if r <= disc_r:
            continue
        a = int(peak * (1 - (i - 1) / layers) ** 1.6)
        if a <= 0:
            continue
        w = max(2, int((glow_r - disc_r) / layers) + m(1.5))
        g = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(g, (*color, a), (r + 1, r + 1), r, width=w)
        surf.blit(g, (cx - r - 1, cy - r - 1))


def render_card(sid, pal, price, name, gem_r_off, spec_boost, floor_off):
    """Draw ONE portrait-plate card onto a fresh SS panel (324×200) and return
    it (drawn directly at SS, no smoothscale) plus the disc centre."""
    big = pygame.Surface((CARD_W * SS, CARD_H * SS), pygame.SRCALPHA)
    rect = pygame.Rect(m(_INSET), m(_INSET),
                       CARD_W * SS - 2 * m(_INSET), CARD_H * SS - 2 * m(_INSET))
    rad = m(CARD_RAD)
    cx, cy = rect.centerx, rect.y + m(36)

    # 1. depth: soft multi-layer drop shadow (top-left light → offset down).
    drop_shadow(big, rect, rad, blur=m(8), alpha=160, dy=m(4))
    # 2. body gradient (indigo CARD_T → CARD_B).
    big.blit(vgrad(rect.w, rect.h, rad, CARD_T, CARD_B, 252, gamma=1.15),
             rect.topleft)
    # 3. glossy top sheen.
    top_sheen(big, rect, rad, m(30), peak=62)
    # 4. bottom-right contact AO.
    contact_shadow(big, rect, rad, m(9), alpha=120)
    # 5. inner tray dark border + faint gold lane so the body edge frames the
    #    portrait even at "minimum chrome".
    tray = rect.inflate(-m(7), -m(7))
    trad = rad - m(4)
    pygame.draw.rect(big, (10, 10, 24, 200), tray.inflate(m(2), m(2)),
                     width=max(1, m(1)), border_radius=trad + m(1))
    pygame.draw.rect(big, (*CARD_RING_BRIGHT, 90), tray, width=max(1, m(1)),
                     border_radius=trad)

    # ── hero portrait disc ──
    # 6. the domed glass well.
    cabochon(big, cx, cy, m(R), CABO_LO, CABO_HI, ring=pal["gem"], ring_a=60)
    # 7. the skin portrait, framed under glass.
    if sid is not None:
        blit_thumb(big, sid, cx, cy, m(R) * 1.5)
    # 8. tier tint INSIDE the disc — warms the glass per tier.
    _disc_tint(big, cx, cy, m(R), pal["glow"], pal["deep"], peak=55, base=22)
    # 9. glass dome overlay (standard crescent sheen + gold bezel).
    cabochon_glass(big, cx, cy, m(R), tint=pal["gem"])

    # 10. lift the mid-interior floor so the socket-dark band above the caustic
    #     reads as frosted glass, not a hole. Painted BEFORE the caustics so they
    #     remain the brightest peaks.
    _interior_floor(big, cx, cy, m(R), floor_off)

    # 11. base crescent caustic (all tiers), on TOP of the standard sheen — the
    #     genuinely juicy upper-left highlight.
    _crescent(big, cx, cy, m(R), (255, 255, 255), 45)
    # 12. EPIC/LEGENDARY compensating specular: their glass reads muted through
    #     the darker tier veil, so an extra white crescent equalises the dome's
    #     specular back up to the RARE reference.
    if spec_boost > 0:
        _crescent(big, cx, cy, m(R), (255, 255, 255), spec_boost)

    # 13. faint darker pool at the lower rim for depth (weight sits low in the
    #     glass), masked to the disc so it hugs the 6-o'clock bevel.
    d = m(R) * 2
    pool = pygame.Surface((d, d), pygame.SRCALPHA)
    pell = pygame.Rect(0, 0, int(m(R) * 1.5), int(m(R) * 0.85))
    pell.center = (m(R), int(m(R) * 1.35))
    pygame.draw.ellipse(pool, (*pal["deep"], 70), pell)
    pmask = pygame.Surface((d, d), pygame.SRCALPHA)
    pygame.draw.circle(pmask, (255, 255, 255, 255), (m(R), m(R)), m(R) - m(1))
    pool.blit(pmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(pool, (cx - m(R), cy - m(R)))

    # 14. tight bright-gold bevel rim right on the glass edge.
    pygame.draw.circle(big, (*CARD_RING_BRIGHT, 180), (cx, cy),
                       m(R) + m(1), width=m(1))

    # 15. tier read (supporting): a clean symmetric dim gutter glow. The disc
    #     tint + tier-sized crest are the primary rarity carriers.
    _gutter_aura(big, cx, cy, m(R), m(R + 26), pal["glow"], peak=45, layers=18)

    # 16. FOOTER NAME PLATE — a frosted plate across the bottom of the body
    #     interior: a cool desaturated fill lifted well above the body reads as a
    #     surface the name sits ON, not a seam. A 1px inner top-shadow deepens
    #     the plate lip; a thick bright-gold keyline caps its top edge.
    strip_rect = pygame.Rect(rect.x, rect.bottom - m(22), rect.w, m(22))
    strip = pygame.Surface((strip_rect.w, strip_rect.h), pygame.SRCALPHA)
    strip.fill((60, 65, 86, 244))
    # inner top-shadow just under the keyline so the name reads as raised on the
    # plate rather than floating on the body.
    pygame.draw.line(strip, (10, 11, 26, 80),
                     (0, m(1.5)), (strip_rect.w, m(1.5)), max(1, m(1)))
    big.blit(strip, strip_rect.topleft)
    # thicker, brighter gold keyline capping the plate's top edge.
    pygame.draw.line(big, (*CARD_RING_BRIGHT, 235),
                     (strip_rect.x, strip_rect.y),
                     (strip_rect.right, strip_rect.y), max(1, m(1.5)))
    plain_text(big, name.upper(), font(9.0), strip_rect.center,
               (236, 230, 208), shadow_a=170, tracking=m(1.0), weight=m(0.7))

    # 17. PRICE PILL — small dark-glass rounded pill, top-RIGHT.
    ph, pw_min = m(14), m(40)
    price_str = f"{price:,}"
    pf = font(8.0)
    ptw = pf.render(price_str, True, (255, 255, 255)).get_width()
    pw = max(pw_min, ptw + m(12))
    pcx = rect.right - m(6) - pw // 2
    pcy = rect.y + m(10)
    pill = pygame.Surface((pw, ph), pygame.SRCALPHA)
    pygame.draw.rect(pill, (*pal["deep"], 210), (0, 0, pw, ph),
                     border_radius=ph // 2)
    pygame.draw.rect(pill, (*pal["gem"], 70), (0, 0, pw, ph),
                     width=max(1, m(1)), border_radius=ph // 2)
    big.blit(pill, (pcx - pw // 2, pcy - ph // 2))
    plain_text(big, price_str, pf, (pcx, pcy), pal["gem"],
               shadow_a=0, weight=m(0.7))

    # 18. GEM CREST — faceted tier badge, top-LEFT corner. Its RADIUS steps per
    #     tier (+1/+2/+3) so rarity reads even in grayscale, alongside hue.
    _crest_gem(big, rect.x + m(19), rect.y + m(19), m(GEM_R + gem_r_off),
               pal["gem"], pal["deep"])

    # 19. bevel rim + dark keyline LAST so the card frame stays crisp over the
    #     halo + footer that bleed to the body edge.
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 235),
              w=max(1, m(2.0)))
    return big, (cx, cy)


# ── review sheet ──────────────────────────────────────────────────────────────
# Per-tier: gem_r_off (crest size step), spec_boost (compensating crescent
# alpha; 0 = none), floor_off (interior-floor warm nudge).
VARIANTS = [
    ("RARE",      "skin_lorikeet", {"gem": (108, 188, 252), "glow": (60, 140, 230), "deep": (18, 44, 90)},  600,  "Lorikeet", 1, 0,  0),
    ("EPIC",      "skin_prism",    {"gem": (194, 122, 248), "glow": (140, 40, 230), "deep": (44, 10, 80)},  1400, "Prism",    2, 42, 8),
    ("LEGENDARY", "skin_kitsune",  {"gem": (255, 202, 104), "glow": (220, 160, 40), "deep": (90, 50, 0)},   3500, "Kitsune",  3, 40, 16),
]

PANEL_W, PANEL_H = CARD_W * SS, CARD_H * SS   # 324 × 200 (SS panels, no downscale)
MARGIN = 20
GUTTER = 16
HEADER_H = 30
FOOTER_H = 24
STRIP_LABEL_H = 20
STRIP_H = CARD_H                              # real-scale 1x cards (162×100)

sheet_w = MARGIN * 2 + PANEL_W * 3 + GUTTER * 2
sheet_h = (MARGIN + HEADER_H + PANEL_H + FOOTER_H + STRIP_LABEL_H + STRIP_H
           + MARGIN)
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((16, 17, 30))

hfont = _font(22, True)
ffont = _font(20, True)
sfont = _font(16, True)
htxt = hfont.render("store_card_v3_tl — portrait-plate — round 2", True,
                    (236, 232, 214))
sheet.blit(htxt, (MARGIN, MARGIN + (HEADER_H - htxt.get_height()) // 2))

panel_y = MARGIN + HEADER_H
panels = []
for i, (tier, sid, pal, price, name, gro, sb, fo) in enumerate(VARIANTS):
    px = MARGIN + i * (PANEL_W + GUTTER)
    panel, _ = render_card(sid, pal, price, name, gro, sb, fo)
    panels.append(panel)
    sheet.blit(panel, (px, panel_y))
    ftxt = ffont.render(tier, True, (218, 214, 200))
    sheet.blit(ftxt, (px + (PANEL_W - ftxt.get_width()) // 2,
                      panel_y + PANEL_H + (FOOTER_H - ftxt.get_height()) // 2))

# 1x real-scale strip: smoothscale each SS panel down to the live 162×100 card.
strip_label_y = panel_y + PANEL_H + FOOTER_H
ltxt = sfont.render("real scale (1×, 162×100)", True, (200, 204, 220))
sheet.blit(ltxt, (MARGIN, strip_label_y + (STRIP_LABEL_H - ltxt.get_height()) // 2))
strip_y = strip_label_y + STRIP_LABEL_H
for i, panel in enumerate(panels):
    px = MARGIN + i * (PANEL_W + GUTTER)
    left = px + (PANEL_W - CARD_W) // 2
    small = pygame.transform.smoothscale(panel, (CARD_W, CARD_H))
    sheet.blit(small, (left, strip_y))

out = "/home/user/skybit/docs/store_card_v3_tl/portrait-plate/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())


# ── measurement (verify director targets; not part of the review sheet) ──────
def _lum(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


for (tier, sid, pal, price, name, gro, sb, fo), panel in zip(VARIANTS, panels):
    cx, cy = panel.get_width() // 2, m(_INSET) + m(36)
    rr = m(R)
    # caustic peak: scan the upper-left arc band of the dome for max luminance.
    caustic = 0.0
    for ang_deg in range(100, 200, 2):
        a = math.radians(ang_deg)
        for rad_f in (0.72, 0.8, 0.86, 0.92):
            x = int(cx + rr * rad_f * math.cos(a))
            y = int(cy + rr * rad_f * math.sin(a))
            caustic = max(caustic, _lum(panel.get_at((x, y))))
    # interior floor: median of mid-interior probes (avoid the skin's own bright
    # pixels dominating).
    fs = sorted(_lum(panel.get_at((cx + int(rr * dx), cy + int(rr * dy))))
                for dx, dy in ((0, -0.1), (-0.12, 0), (0.12, 0), (0, 0.1), (0, 0)))
    floor = fs[len(fs) // 2]
    # footer plate vs body just above it, sampled LEFT of the centred name.
    rect_l = m(_INSET)
    rect_b = m(_INSET) + CARD_H * SS - 2 * m(_INSET)
    px = rect_l + m(9)
    plate = _lum(panel.get_at((px, rect_b - m(11))))
    body = _lum(panel.get_at((px, rect_b - m(26))))
    print(f"{tier:10s} caustic={caustic:5.1f} floor={floor:5.1f} "
          f"plate={plate:5.1f} body={body:5.1f} plate-body={plate - body:+5.1f}")
