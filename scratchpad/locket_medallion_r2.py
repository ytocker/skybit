import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
import sys
sys.path.insert(0, "/home/user/skybit")
import pygame, math
pygame.init()
pygame.display.set_mode((1, 1))

from game import store_cards as sc
from game.draw import lerp_color

# Author at 2x, downscale once for crisp anti-aliased edges. Coordinates below
# are logical 360x640 px scaled by SC into the 720x1280 authoring canvas so the
# AD layout numbers map directly.
SC = 2
W, H = 360 * SC, 640 * SC


def px(v):
    return int(round(v * SC))


LEG = sc.RARITY["legendary"]          # gem / glow / deep amber tier
PALE = (255, 236, 176)
DEEP_GOLD = (120, 74, 14)
BASE_GOLD = (216, 160, 60)

surf = pygame.Surface((W, H), pygame.SRCALPHA)
surf.fill((8, 6, 16))

CX, CY = px(180), px(270)

# faint legendary aura so the hero jewel sits in its own pool of tier light
sc.soft_glow(surf, CX, CY, px(180), LEG["glow"], 46, layers=10)


def beveled_ring(surf, cx, cy, r_out, r_in, base, pale, deep):
    """A thin gold locket rim lit from top-left: a rounded cross-section bevel
    (dark contact edges, bright mid) crossed with one angular light so the ring
    reads as turned metal, not a flat stamped coin edge."""
    ring_w = r_out - r_in
    lx, ly = -0.7071, -0.7071                       # top-left light
    steps = int(2 * math.pi * r_out) + 8            # dense enough: no seams
    for i in range(steps):
        a = 2 * math.pi * i / steps
        ca, sa = math.cos(a), math.sin(a)
        af = (ca * lx + sa * ly + 1) * 0.5          # 1 top-left .. 0 bottom-right
        for rr in range(r_in, r_out + 1):
            t = (rr - r_in) / max(1, ring_w)        # 0 inner .. 1 outer
            bev = max(0.0, 1.0 - abs(t - 0.6) * 1.9)
            lit = 0.18 + 0.55 * af + 0.30 * bev * af
            col = lerp_color(base, pale, max(0.0, min(1.0, lit)))
            if t < 0.10 or t > 0.92:                # dark contact keylines
                col = lerp_color(deep, base, 0.25 + 0.35 * af)
            surf.set_at((int(cx + rr * ca), int(cy + rr * sa)), col)
    # crisp dark keylines seat the rim against the obsidian + the inner well
    pygame.draw.circle(surf, (26, 16, 6), (cx, cy), r_out, px(1.5))
    pygame.draw.circle(surf, (30, 18, 6), (cx, cy), r_in, px(1.4))
    # a restrained warm glint hugging only the upper-left crown (one light) —
    # kept low-alpha so it never blows the gold to white
    mid = (r_out + r_in) // 2
    glint = pygame.Surface((r_out * 2 + 8, r_out * 2 + 8), pygame.SRCALPHA)
    gc = r_out + 4
    pygame.draw.arc(glint, (250, 224, 156, 90),
                    (gc - mid, gc - mid, mid * 2, mid * 2),
                    math.radians(108), math.radians(168), px(2.2))
    surf.blit(glint, (cx - gc, cy - gc), special_flags=pygame.BLEND_ADD)


R_OUT = px(158)
R_IN = px(138)

# dark jewel well filling the whole locket interior — a soft domed obsidian so
# the hero cabochon and tier facets have depth to sit in.
for i in range(R_IN, 0, -1):
    f = (i / R_IN) ** 1.4
    col = lerp_color((16, 15, 30), (5, 5, 12), f)
    pygame.draw.circle(surf, col, (CX, CY), i)
sc.soft_glow(surf, CX, CY, px(96), LEG["glow"], 30, layers=8)

beveled_ring(surf, CX, CY, R_OUT, R_IN, BASE_GOLD, PALE, DEEP_GOLD)

# six tier facets ringing the well just inside the rim, each seated in its own
# dark notch on the obsidian so the amber pops instead of dissolving into gold
# and the thin gold rim stays continuous.
gem_r = px(110)
for k in range(6):
    a = math.radians(-90 + k * 60)
    gx = int(CX + gem_r * math.cos(a))
    gy = int(CY + gem_r * math.sin(a))
    pygame.draw.circle(surf, (4, 4, 10), (gx, gy), px(13))
    pygame.draw.circle(surf, (*LEG["deep"], 120), (gx, gy), px(13), px(1))
    sc.facet_gem(surf, gx, gy, px(9.5), (255, 190, 84), LEG["deep"])

# hero cabochon: dark well -> real skin under glass. ONE jewel, no mini-discs.
R_CABO = px(65)
sc.cabochon(surf, CX, CY, R_CABO, sc.CABO_LO, sc.CABO_HI)
sc.blit_thumb(surf, "skin_lorikeet", CX, CY, R_CABO * 1.5)
sc.cabochon_glass(surf, CX, CY, R_CABO, tint=LEG["gem"])


def pill(surf, rect, radius, top, bot, rim_d, rim_b, gloss_a):
    """Rounded body with a single top-biased gloss band and a dark-under-bright
    beveled rim — the shared button/nameplate finish, top-left lit."""
    body = sc.vgrad_stops(rect.w, rect.h, radius, [(0.0, top), (1.0, bot)],
                          255, gamma=1.05)
    surf.blit(body, rect.topleft)
    if gloss_a:
        band_h = max(1, rect.h // 3)
        sweep = pygame.Surface((rect.w, band_h), pygame.SRCALPHA)
        for y in range(band_h):
            a = int(gloss_a * (1 - y / band_h) ** 1.8)
            pygame.draw.line(sweep, (255, 255, 255, a), (0, y), (rect.w, y))
        sm = pygame.Surface((rect.w, band_h), pygame.SRCALPHA)
        pygame.draw.rect(sm, (255, 255, 255, 255), sm.get_rect(),
                         border_top_left_radius=radius,
                         border_top_right_radius=radius)
        sweep.blit(sm, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        surf.blit(sweep, rect.topleft)
    pygame.draw.rect(surf, rim_d, rect, width=px(1.6), border_radius=radius)
    sc.bevel_rim(surf, rect, radius, rim_d, (*rim_b, 230), w=px(1.4))


# ── floating tier ribbon ABOVE the locket ─────────────────────────────────────
def tier_ribbon(surf, word, cx, cy):
    f = sc.font(13)
    tw = sc._glyph_base(word, f, px(2)).get_width()
    pad = px(20)
    w = tw + pad * 2
    h = px(30)
    notch = px(11)
    x0, y0 = cx - w // 2, cy - h // 2
    top = lerp_color(LEG["gem"], (255, 255, 255), 0.10)
    bot = lerp_color(LEG["deep"], (15, 15, 30), 0.05)
    body = sc.vgrad_stops(w, h, 0,
                          [(0.0, top), (0.5, LEG["glow"]), (1.0, bot)], 255, 1.08)
    poly = [(notch, 0), (w - notch, 0), (w, h // 2), (w - notch, h),
            (notch, h), (0, h // 2)]
    pmask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(pmask, (255, 255, 255, 255), poly)
    body.blit(pmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    sh = pygame.Surface((w, h + px(3)), pygame.SRCALPHA)
    pygame.draw.polygon(sh, (0, 0, 0, 130), [(x, y + px(3)) for x, y in poly])
    surf.blit(sh, (x0, y0))
    surf.blit(body, (x0, y0))
    ab = [(x0 + x, y0 + y) for x, y in poly]
    pygame.draw.polygon(surf, (24, 14, 6), ab, width=px(1.6))
    sc.plain_text(surf, word, f, (cx, cy), (26, 14, 4), shadow_a=0,
                  tracking=px(2), weight=px(1.0))


tier_ribbon(surf, "LEGENDARY", CX, px(110))

# ── item name banner across the bottom of the locket ──────────────────────────
name = "RAINBOW LORIKEET"
nf = sc.font(15)
nw = sc._glyph_base(name, nf, px(1)).get_width()
bw, bh = nw + px(44), px(40)
nb = pygame.Rect(CX - bw // 2, px(372) - bh // 2, bw, bh)
sc.drop_shadow(surf, nb, bh // 2, blur=px(4), alpha=120, dy=px(2))
pill(surf, nb, bh // 2, (26, 22, 40), (12, 10, 22), (36, 22, 8),
     sc.CARD_RING_BRIGHT, gloss_a=0)
sc.plain_text(surf, name, nf, nb.center, (248, 208, 112), shadow_a=150,
              weight=px(1.0), keyline=(6, 5, 14), kw=px(1))

# ── price chip below the locket ───────────────────────────────────────────────
sc.price_chip(surf, CX, px(460), "3,600", px(46), affordable=True)

# ── CANCEL (ghost) + BUY (gold hero) side by side ─────────────────────────────
by = px(540)
# CANCEL — ghost pill, gold outline
cw, ch = px(112), px(50)
cr = pygame.Rect(px(90) - cw // 2, by - ch // 2, cw, ch)
sc.drop_shadow(surf, cr, ch // 2, blur=px(4), alpha=90, dy=px(2))
pill(surf, cr, ch // 2, (34, 30, 48), (18, 16, 30), (10, 9, 20),
     (198, 168, 96), gloss_a=36)
sc.plain_text(surf, "CANCEL", sc.font(14), cr.center, (222, 216, 232),
              shadow_a=140, weight=px(0.9))

# BUY — the gold hero pill (R>G>B, capped top gloss)
bw2, bh2 = px(162), px(58)
br = pygame.Rect(px(246) - bw2 // 2, by - bh2 // 2, bw2, bh2)
sc.drop_shadow(surf, br, bh2 // 2, blur=px(5), alpha=120, dy=px(2))
sc.soft_glow(surf, br.centerx, br.centery, px(46), LEG["glow"], 40, layers=8)
pill(surf, br, bh2 // 2,
     (246, 200, 96), (196, 130, 40), sc.GOLD_A_RIM_DARK, sc.GOLD_A_RIM_BRIGHT,
     gloss_a=72)
sc.plain_text(surf, "BUY", sc.font(19), br.center, (58, 32, 6),
              shadow_a=0, weight=px(1.2), keyline=(255, 236, 176), kw=px(1))

# downscale once -> crisp final
out = pygame.transform.smoothscale(surf, (360, 640))
dest = "/home/user/skybit/docs/confirm_purchase/locket-medallion/round_2.png"
os.makedirs(os.path.dirname(dest), exist_ok=True)
pygame.image.save(out, dest)
print("saved", dest, out.get_size())

# pixel-sample the gold hero centre so BUY is verified gold, not white
c = out.get_at((246, 540))
print("BUY center px", c[:3])
