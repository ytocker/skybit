#!/usr/bin/env python3
"""cartouche-sacred · confirm_purchase_v8 · card-frame-v1

Egyptian royal cartouche silhouette: the card body keeps its straight sides and
rounded bottom (r=23), but the TOP grows a semicircular cap — a half-ellipse
dome springing from the two top corners up to a crown, so the whole frame reads
as a sealed royal name-ring. A Ra sun-disc cabochon crowns the cap; coin+price,
tier-rank pips and the rarity ribbon all live in the full-width straight
midsection below. Deep-lapis body + hand-rolled two-tone gold cartouche border.
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

POP_W, POP_H = 260, 442
CX = 130
CARD_X, CARD_TOP, CARD_W, CARD_H, CARD_RAD = 10, 127, 240, 299, 23
CARD_R, CARD_BOT = CARD_X + CARD_W, CARD_TOP + CARD_H      # 250, 426
CAP_RX, CAP_CROWN_Y = 120, 95                              # half-ellipse cap
CAP_RY = CARD_TOP - CAP_CROWN_Y                            # 32
DISC_CY, DISC_R, HALO_R = 135, 53, 57
ZA_CY = 247
PIP_CY, PIP_R, PIP_GAP = 285, 7, 20
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
        pts.append((CX + CAP_RX * math.cos(t), CARD_TOP - CAP_RY * math.sin(t)))
    return pts


def _outline_pts():
    """Full cartouche outline as one continuous logical-px point ring: cap arch,
    left side, bottom-left corner, bottom, bottom-right corner, right side. The
    cap is an arc, the sides are straight, the bottom corners are r=23 arcs —
    generated parametrically so the stroke is one clean unbroken bevel."""
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

    # hand-rolled two-tone gold border: dark base stroke, then bright bevel
    # offset up-left so the frame reads embossed under the top-left light.
    ring = [(m(x), m(y)) for x, y in _outline_pts()]
    off = m(1)
    pygame.draw.lines(big, BORDER_DEEP, True, ring, m(5))
    hi = [(x - off, y - off) for x, y in ring]
    pygame.draw.lines(big, BORDER_BRIGHT, True, hi, m(5))


def name_text(big, name):
    nfs = 20; nfnt = font(nfs); mw = m(CARD_W - 44)
    while sc._glyph_base(name, nfnt, 0).get_width() > mw and nfs > 12:
        nfs -= 1; nfnt = font(nfs)
    plain_text(big, name, nfnt, (m(CX), m(213)), (250, 244, 224), shadow_a=160,
               weight=m(0.9), keyline=(84, 62, 18), kw=m(1.0))


def zone_a(big, price_str):
    """Coin + gold price numeral inline on a dark lapis lozenge."""
    chip = pygame.Rect(0, 0, m(160), m(28)); chip.center = (m(CX), m(ZA_CY))
    sc._dark_chip_body(big, chip, m(11),
                       [(0.0, (30, 34, 74)), (1.0, (16, 18, 46))],
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
        facet_gem(big, int(m(x)), m(PIP_CY), m(PIP_R), pal["gem"], pal["deep"])


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
    # LEGENDARY: pull the ribbon firmly into the sapphire family so it never
    # reads as the same gold as the price chip and pips.
    if tier_word == "LEGENDARY":
        rpal = dict(pal)
        rpal["gem"] = (80, 130, 240); rpal["glow"] = (40, 80, 200)
        rpal["deep"] = (24, 42, 112)
    else:
        rpal = pal
    sc._ribbon_lozenge(big, tier_word, m(CX), m(ZB_CY), m(112), rpal)
    for gx in (GEM_L_X, GEM_R_X):
        sc._alpha_aura(big, m(gx), m(ZB_CY), m(16), pal["glow"], peak=60, layers=14)
        facet_gem(big, m(gx), m(ZB_CY), m(14), pal["gem"], pal["deep"])


def hero_disc(big, sid, pal):
    """Ra sun-disc cabochon crowning the cap: normal-alpha aura behind the dome,
    the glass cabochon + skin, a gold halo ring, then the glass overlay (the ONLY
    BLEND_ADD source at this centre)."""
    cx, cy, r = m(CX), m(DISC_CY), m(DISC_R)
    sc._alpha_aura(big, cx, cy, r + m(30), pal["glow"], peak=35, layers=15)
    cabochon(big, cx, cy, r, CABO_LO, CABO_HI, ring=pal["gem"], ring_a=50)
    try:
        blit_thumb(big, sid, cx, cy, int(r * 1.5))
    except Exception:
        pygame.draw.circle(big, pal["gem"], (cx, cy), int(r * 0.7))
    pygame.draw.circle(big, CARD_RING_BRIGHT, (cx, cy), m(HALO_R), max(1, m(2)))
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
idr.text((MARGIN, 18), "cartouche-sacred · card-frame-v1 · round 1", fill=(232, 226, 208))
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
OUT = OUTDIR + "/round_1.png"
out.save(OUT)
print(f"saved {out.size[0]}x{out.size[1]}  ->  {OUT}")
