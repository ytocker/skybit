#!/usr/bin/env python3
"""cartouche-sacred · confirm_purchase_v8 · card-frame-v1 · round 2

Egyptian royal cartouche silhouette: the card body keeps its straight sides and
rounded bottom (r=23), but the TOP grows a DEEP semicircular cap — a half-ellipse
dome (CAP_RY=47) springing from the two top corners up to a high crown, so the
whole frame reads as a sealed royal name-ring, not a rounded rect. A knotted
tie-bar band binds the cap base (the cue that separates a cartouche from a plain
oval). A Ra sun-disc cabochon crowns the cap under a warm solar corona +
radiating gold spokes; coin+price, tier-rank pips and the rarity ribbon all live
in the full-width straight midsection below. Deep-lapis body + hand-rolled
two-tone gold cartouche border built as a clean filled+inset mask ring.
"""
import os, sys, math
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.path.insert(0, "/home/user/skybit")
import pygame; pygame.init(); pygame.display.set_mode((1, 1))
import game.store_cards as sc

# mandatory gloss_sweep patch — the shipped helper leaves a hard slab under
# smoothscale; this BLEND_ADD masked variant is what the v8 sheet was tuned on.
def _gloss_sweep_fixed(surf, rect, radius, peak=120):
    sweep = pygame.Surface(rect.size, pygame.SRCALPHA)
    h = max(1, rect.h)
    for y in range(h):
        v = int(peak * (1 - y / h) ** 2.4)
        if v <= 0: continue
        pygame.draw.line(sweep, (v, v, v, 255), (0, y), (rect.w, y))
    sm = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(sm, (255, 255, 255, 255), sm.get_rect(), border_radius=radius)
    sweep.blit(sm, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(sweep, rect.topleft, special_flags=pygame.BLEND_ADD)
sc.gloss_sweep = _gloss_sweep_fixed

from game.store_cards import (m, SS, font, vgrad_stops, plain_text, coin_glyph,
                              facet_gem, cabochon, cabochon_glass, blit_thumb,
                              CABO_LO, CABO_HI, PRICE_STOPS, GOLD_A_STOPS,
                              CARD_RING_BRIGHT)
from PIL import Image, ImageDraw

# ── palette / geometry ────────────────────────────────────────────────────────
TIERS = [
    ("RARE",      {"gem": (108, 188, 252), "glow": (60, 140, 220), "deep": (20, 60, 130)}),
    ("EPIC",      {"gem": (194, 122, 248), "glow": (140, 60, 220),  "deep": (70, 20, 160)}),
    ("LEGENDARY", {"gem": (255, 202, 104), "glow": (220, 150, 40),  "deep": (140, 80, 10)}),
]
SIDS   = {"RARE": "skin_wizard", "EPIC": "skin_mummy", "LEGENDARY": "skin_astronaut"}
NAMES  = {"RARE": "SCARAB", "EPIC": "FALCON", "LEGENDARY": "PHARAOH"}
PRICES = {"RARE": "720", "EPIC": "1,400", "LEGENDARY": "2,600"}
PIPS   = {"RARE": 1, "EPIC": 2, "LEGENDARY": 3}

# Egyptian faience/turquoise — the LEGENDARY Zone-B override. A wholly different
# hue from RARE's blue and EPIC's purple, so the top tier reads unmistakably
# ancient-Egyptian and never as "the same blue as RARE".
LEG_TURQ_GEM  = (64, 196, 180)
LEG_TURQ_GLOW = (30, 150, 140)
LEG_TURQ_DEEP = (15, 80, 75)

POP_W, POP_H = 260, 442
CX = 130
CARD_X, CARD_TOP, CARD_W, CARD_H, CARD_RAD = 10, 127, 240, 299, 23
CARD_R, CARD_BOT = CARD_X + CARD_W, CARD_TOP + CARD_H      # 250, 426
# Deep royal cap: crown peaks a full 47 px above the springline (CAP_RY=47) so the
# silhouette reads as a domed name-ring, not a barely-bulged rounded rect.
CAP_RX, CAP_CY, CAP_RY = 120, CARD_TOP, 47                 # half-ellipse cap
CAP_PEAK_Y = CAP_CY - CAP_RY                               # 80
CAP_CROWN_Y = CAP_PEAK_Y                                   # top of cap fill band
DISC_CY, DISC_R = 135, 53
ZA_CY = 247
PIP_CY, PIP_R, PIP_GAP = 285, 9, 20
BTN_W, BTN_H, BTN_RAD, BTN_CY, BTN_GAP = 99, 31, 12, 360, 10
BUY_CX = CX - (BTN_W + BTN_GAP) // 2                       # 76
CAN_CX = CX + (BTN_W + BTN_GAP) // 2                       # 184
ZB_CY, GEM_L_X, GEM_R_X = 402, 43, 217

# Deep-lapis sacred body; crown lit a touch so the cap reads domed.
LAPIS_STOPS = [(0.0, (18, 22, 58)), (0.5, (35, 28, 52)), (1.0, (14, 16, 44))]
CAP_STOPS   = [(0.0, (28, 32, 72)), (1.0, (18, 22, 58))]
# Cartouche gold border tones (this frame's own bevel, not the shared card ring).
BORDER_DEEP   = (91, 70, 19)
BORDER_BRIGHT = (236, 202, 116)


def _cap_arch_pts():
    """Half-ellipse cap points, right springline -> crown -> left springline, in
    LOGICAL px. cos(0)=+1 lands the first point on the RIGHT top corner."""
    n = 72
    pts = []
    for i in range(n + 1):
        t = math.pi * i / n
        pts.append((CX + CAP_RX * math.cos(t), CAP_CY - CAP_RY * math.sin(t)))
    return pts


def _outline_pts():
    """Full cartouche outline as one continuous logical-px point ring: cap arch,
    left side, bottom-left corner, bottom, bottom-right corner, right side. The
    cap is an arc, the sides are straight, the bottom corners are r=23 arcs —
    generated parametrically so the mask ring is one clean unbroken bevel."""
    pts = list(_cap_arch_pts())                # right corner -> crown -> left corner
    pts.append((CARD_X, CARD_BOT - CARD_RAD))  # left side down
    # bottom-left corner (screen convention: y+ down), from left (180) to bottom (90)
    for k in range(1, 13):
        a = math.radians(180 - 90 * k / 12)
        pts.append((CARD_X + CARD_RAD + CARD_RAD * math.cos(a),
                    CARD_BOT - CARD_RAD + CARD_RAD * math.sin(a)))
    pts.append((CARD_R - CARD_RAD, CARD_BOT))  # bottom edge
    # bottom-right corner, from bottom (90) to right (0)
    for k in range(1, 13):
        a = math.radians(90 - 90 * k / 12)
        pts.append((CARD_R - CARD_RAD + CARD_RAD * math.cos(a),
                    CARD_BOT - CARD_RAD + CARD_RAD * math.sin(a)))
    pts.append((CARD_R, CARD_TOP))             # right side up, closes to cap start
    return pts


def _inset_poly(pts, d):
    """Parallel-inset a convex polygon inward by ~d px. Each vertex is pushed
    along the bisector of its two edge in-normals (normals chosen to point at the
    centroid), so the offset is a true even inset — no faceted/notched joins like
    thick polylines produce at seam transitions."""
    n = len(pts)
    gx = sum(p[0] for p in pts) / n
    gy = sum(p[1] for p in pts) / n

    def innorm(ax, ay, bx, by):
        ex, ey = bx - ax, by - ay
        L = math.hypot(ex, ey) or 1.0
        nx, ny = -ey / L, ex / L
        mx, my = (ax + bx) / 2, (ay + by) / 2
        if nx * (gx - mx) + ny * (gy - my) < 0:
            nx, ny = -nx, -ny
        return nx, ny

    out = []
    for i in range(n):
        x0, y0 = pts[(i - 1) % n]
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % n]
        n1x, n1y = innorm(x0, y0, x1, y1)
        n2x, n2y = innorm(x1, y1, x2, y2)
        bx, by = n1x + n2x, n1y + n2y
        L = math.hypot(bx, by) or 1.0
        bx, by = bx / L, by / L
        cosv = bx * n1x + by * n1y
        scale = d / (cosv if abs(cosv) > 1e-3 else 1.0)
        out.append((x1 + bx * scale, y1 + by * scale))
    return out


def _cartouche_border(big):
    """Two-tone gold cartouche ring built by MASKING, not thick polylines: a
    filled outline polygon with the interior knocked transparent leaves a clean
    even-width ring (no join artifacts). A second bright ring nudged up-left over
    the dark base gives a real embossed bevel — lit top-left, shaded bottom-right.
    Drawn on its own surface so the knock-out preserves the gradient body below."""
    size = big.get_size()
    ring = [(m(x), m(y)) for x, y in _outline_pts()]
    inner = _inset_poly(ring, m(4))
    # dark base ring
    base = pygame.Surface(size, pygame.SRCALPHA)
    pygame.draw.polygon(base, BORDER_DEEP, ring)
    pygame.draw.polygon(base, (0, 0, 0, 0), inner)     # knock interior transparent
    big.blit(base, (0, 0))
    # bright bevel: same ring shifted up-left so only the lit top-left face shows
    # bright while the bottom-right keeps the dark base — an embossed edge.
    off = m(1)
    bev = pygame.Surface(size, pygame.SRCALPHA)
    hi_out = [(x - off, y - off) for x, y in ring]
    hi_in = [(x - off, y - off) for x, y in inner]
    pygame.draw.polygon(bev, BORDER_BRIGHT, hi_out)
    pygame.draw.polygon(bev, (0, 0, 0, 0), hi_in)
    big.blit(bev, (0, 0))


def _tie_bar(big):
    """The cartouche's definitive cue: a knotted tie-bar band binding the cap
    base — a double gold rule at the springline. This horizontal binding is what
    reads as a sealed name-ring rather than a plain oval; the sun-disc crowns
    above it and the two rule ends emerge from behind the disc as the knot cords."""
    x0, x1 = m(40), m(220)
    y = m(127)
    wd, gap = m(3), m(3)
    # dark seat so the twin gold rules read as raised binding, not painted lines
    pygame.draw.rect(big, BORDER_DEEP, (x0, y - m(1), x1 - x0, wd * 2 + gap + m(2)))
    pygame.draw.rect(big, BORDER_BRIGHT, (x0, y, x1 - x0, wd))
    pygame.draw.rect(big, BORDER_BRIGHT, (x0, y + wd + gap, x1 - x0, wd))


def card_body(big):
    body_rect = pygame.Rect(m(CARD_X), m(CARD_TOP), m(CARD_W), m(CARD_H))
    # silhouette drop shadow (body dominates; the shallow cap adds little).
    sc.drop_shadow(big, body_rect, m(CARD_RAD), blur=m(8), alpha=165, dy=m(4))

    # body fill: straight (square) top corners so the sides run clean up to the
    # cap springline; only the BOTTOM corners round.
    bw, bh = body_rect.size
    body = vgrad_stops(bw, bh, 0, LAPIS_STOPS, 255, gamma=1.12).copy()
    bmask = pygame.Surface((bw, bh), pygame.SRCALPHA)
    pygame.draw.rect(bmask, (255, 255, 255, 255), bmask.get_rect(),
                     border_bottom_left_radius=m(CARD_RAD),
                     border_bottom_right_radius=m(CARD_RAD))
    body.blit(bmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(body, body_rect.topleft)

    # cap fill: lapis gradient masked to the half-ellipse dome above the body.
    cap_pts = [(m(x), m(y)) for x, y in _cap_arch_pts()]
    bx, byt = m(CARD_X), m(CAP_CROWN_Y)
    cw, ch = m(CARD_W), m(CARD_TOP) - m(CAP_CROWN_Y)
    cap = vgrad_stops(cw, ch, 0, CAP_STOPS, 255).copy()
    cmask = pygame.Surface((cw, ch), pygame.SRCALPHA)
    pygame.draw.polygon(cmask, (255, 255, 255, 255),
                        [(px - bx, py - byt) for px, py in cap_pts])
    cap.blit(cmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(cap, (bx, byt))
    # gentle sheen on the cap crown so the gilded dome catches light.
    sheen = pygame.Surface((cw, ch), pygame.SRCALPHA)
    for yy in range(ch):
        a = int(46 * (1 - yy / ch) ** 1.4)
        pygame.draw.line(sheen, (255, 255, 255, a), (0, yy), (cw - 1, yy))
    sheen.blit(cmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(sheen, (bx, byt))

    # faint inner tray keyline echoing the cartouche (bottom-rounded, square top).
    tray = body_rect.inflate(-m(8), -m(8))
    tmask_surf = pygame.Surface(tray.size, pygame.SRCALPHA)
    pygame.draw.rect(tmask_surf, (*CARD_RING_BRIGHT, 48), tmask_surf.get_rect(),
                     width=max(1, m(1)), border_bottom_left_radius=m(CARD_RAD - 3),
                     border_bottom_right_radius=m(CARD_RAD - 3))
    big.blit(tmask_surf, tray.topleft)

    # clean masked two-tone gold cartouche ring, then the knotted tie-bar binding.
    _cartouche_border(big)
    _tie_bar(big)


def name_text(big, name):
    nfs = 20; nfnt = font(nfs); mw = m(CARD_W - 44)
    while sc._glyph_base(name, nfnt, 0).get_width() > mw and nfs > 12:
        nfs -= 1; nfnt = font(nfs)
    plain_text(big, name, nfnt, (m(CX), m(213)), (250, 244, 224), shadow_a=160,
               weight=m(0.9), keyline=(84, 62, 18), kw=m(1.0))


def zone_a(big, price_str):
    """Coin + gold price numeral inline on a near-black enamel well, deep enough
    that the gold reads against true darkness — not the same-hue lapis body."""
    chip = pygame.Rect(0, 0, m(160), m(28)); chip.center = (m(CX), m(ZA_CY))
    sc._dark_chip_body(big, chip, m(11),
                       [(0.0, (10, 12, 30)), (1.0, (4, 5, 18))],
                       (70, 56, 20), (236, 202, 116), gloss=14, gamma=1.04)
    coin_glyph(big, m(CX - 46), m(ZA_CY), m(12))
    nf = font(20)
    base = sc._stamp_bold(sc._glyph_base(price_str, nf, 0), m(0.9))
    bw, bh = base.get_size()
    r = base.get_rect(center=(m(CX + 14), m(ZA_CY)))
    kl = base.copy(); kl.fill((10, 8, 20, 255), special_flags=pygame.BLEND_RGBA_MULT)
    for ang in range(0, 360, 45):
        dx = int(round(m(1) * math.cos(math.radians(ang))))
        dy = int(round(m(1) * math.sin(math.radians(ang))))
        big.blit(kl, (r.x + dx, r.y + dy))
    fill = vgrad_stops(bw, bh, 0, PRICE_STOPS, 255)
    gold = base.copy(); gold.blit(fill, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    big.blit(gold, r)


def tier_pips(big, tier_word, pal):
    n = PIPS.get(tier_word, 1)
    for i in range(n):
        x = CX + (i - (n - 1) / 2) * PIP_GAP
        pc = (int(m(x)), m(PIP_CY))
        # dark seat well behind each pip so the 8-facet gem reads as INSET and its
        # facets catch light against true black, not the lapis midsection.
        pygame.draw.circle(big, (6, 7, 18), pc, m(12))
        facet_gem(big, pc[0], pc[1], m(PIP_R), pal["gem"], pal["deep"])


def buttons(big):
    br = m(BTN_RAD)
    for cx_b, lbl, stops, lab_c, pk, kl, sha in [
        (m(BUY_CX), "BUY", GOLD_A_STOPS, (44, 28, 6), 40, None, 90),
        (m(CAN_CX), "CANCEL", [(0.0, (26, 28, 64)), (1.0, (14, 16, 44))],
         (206, 210, 238), 16, (8, 6, 20), 110),
    ]:
        r = pygame.Rect(0, 0, m(BTN_W), m(BTN_H)); r.center = (cx_b, m(BTN_CY))
        sc.drop_shadow(big, r, br, blur=m(3), alpha=110, dy=m(2))
        big.blit(vgrad_stops(r.w, r.h, br, stops, 255,
                             gamma=1.06 if lbl == "BUY" else 1.0), r.topleft)
        sc.top_sheen(big, r, br, m(12), peak=pk)
        sc.bevel_rim(big, r, br, (78, 60, 20) if lbl == "BUY" else (20, 18, 40),
                     (*CARD_RING_BRIGHT, 230), w=max(1, m(2.2)))
        plain_text(big, lbl, font(14 if lbl == "BUY" else 13), r.center, lab_c,
                   shadow_a=sha, weight=m(0.8), keyline=kl, kw=m(0.9))


def zone_b(big, tier_word, pal):
    # LEGENDARY owns Egyptian turquoise here — a hue nowhere else on the card, so
    # top tier reads special. Both the ribbon AND the flanking gems take it, and
    # against the gold Zone-A chip that turquoise-vs-gold split IS the signature.
    if tier_word == "LEGENDARY":
        rpal = dict(pal)
        rpal["gem"] = LEG_TURQ_GEM
        rpal["glow"] = LEG_TURQ_GLOW
        rpal["deep"] = LEG_TURQ_DEEP
    else:
        rpal = pal
    sc._ribbon_lozenge(big, tier_word, m(CX), m(ZB_CY), m(112), rpal)
    for gx in (GEM_L_X, GEM_R_X):
        sc._alpha_aura(big, m(gx), m(ZB_CY), m(16), rpal["glow"], peak=60, layers=14)
        facet_gem(big, m(gx), m(ZB_CY), m(14), rpal["gem"], rpal["deep"])


def hero_disc(big, sid, pal):
    """Ra sun-disc cabochon crowning the cap: a warm amber solar CORONA clearly
    larger than the disc, 12 radiating gold spoke-rays, then the glass cabochon +
    skin and the glass overlay. No close-hugging ring — the sun radiates."""
    cx, cy, r = m(CX), m(DISC_CY), m(DISC_R)
    # warm solar corona (normal-alpha so it survives the transparent headroom).
    sc._alpha_aura(big, m(130), m(135), m(65), (255, 200, 100), peak=40, layers=15)
    # 12 radiating gold spokes fanning out beyond the disc rim = a sun, not a bezel
    for i in range(12):
        angle = i * math.pi / 6
        x0 = m(130) + int(m(57) * math.cos(angle))
        y0 = m(135) + int(m(57) * math.sin(angle))
        x1 = m(130) + int(m(68) * math.cos(angle))
        y1 = m(135) + int(m(68) * math.sin(angle))
        pygame.draw.line(big, CARD_RING_BRIGHT, (x0, y0), (x1, y1), m(2))
    cabochon(big, cx, cy, r, CABO_LO, CABO_HI, ring=pal["gem"], ring_a=50)
    try:
        blit_thumb(big, sid, cx, cy, int(r * 1.5))
    except Exception:
        pygame.draw.circle(big, pal["gem"], (cx, cy), int(r * 0.7))
    cabochon_glass(big, cx, cy, r, tint=pal["gem"])


def draw_popup(tier_word, pal):
    big = pygame.Surface((POP_W * SS, POP_H * SS), pygame.SRCALPHA)
    card_body(big)
    name_text(big, NAMES[tier_word])
    zone_a(big, PRICES[tier_word])
    tier_pips(big, tier_word, pal)
    buttons(big)
    zone_b(big, tier_word, pal)
    hero_disc(big, SIDS[tier_word], pal)      # last so the disc overhangs the cap
    return pygame.transform.smoothscale(big, (POP_W, POP_H))


# ── strip ─────────────────────────────────────────────────────────────────────
MARGIN, HEAD, GAP = 20, 58, 12
STRIP_W = MARGIN * 2 + len(TIERS) * (POP_W + GAP) - GAP
STRIP_H = HEAD + POP_H + MARGIN
strip = Image.new("RGB", (STRIP_W, STRIP_H), (8, 8, 20))
idr = ImageDraw.Draw(strip)
idr.text((MARGIN, 18), "cartouche-sacred · card-frame-v1 · round 2", fill=(232, 226, 208))
for i, (tw, pal) in enumerate(TIERS):
    pop = draw_popup(tw, pal)
    pil = Image.frombytes("RGB", (POP_W, POP_H), pygame.image.tostring(pop, "RGB"))
    x = MARGIN + i * (POP_W + GAP)
    strip.paste(pil, (x, HEAD))
    idr.text((x + POP_W // 2, HEAD + POP_H + 6), tw, fill=(180, 176, 210), anchor="mt")
out = strip.resize((STRIP_W * 2, STRIP_H * 2), Image.LANCZOS)
import pathlib
OUTDIR = "/home/user/skybit/docs/confirm_purchase_v8/card-frame-v1/cartouche-sacred"
pathlib.Path(OUTDIR).mkdir(parents=True, exist_ok=True)
OUT = OUTDIR + "/round_2.png"
out.save(OUT)
print(f"saved {out.size[0]}x{out.size[1]}  ->  {OUT}")
