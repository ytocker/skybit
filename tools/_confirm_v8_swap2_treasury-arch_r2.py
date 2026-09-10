#!/usr/bin/env python3
"""treasury-arch · confirm_purchase_v8 · swap-round-2 · round 2

Addresses all art-director notes from round 1:
  - Arch body is dark bronze (tier-neutral), so LEGENDARY keystone + ribbon
    carry the hue while the arch stays a contrasting dark metal.
  - LEGENDARY keystone shifts to platinum so Zone A reads a different hue
    family than the gold Zone B ribbon.
  - Arch scaled down (outer_r=42, inner_r=30) and spring-line lowered to y=248
    so the crown frames the price below rather than colliding with the hero disc.
  - Piers gain material presence via a dark backdrop strip, a warmer lighter
    body gradient (lum delta ≥40 vs card body), a lit inward face, and a
    crisp dark outer keyline.
  - Soffit glow origin moved to the inner arch crown underside and aimed
    downward so the price reads lit from above.
  - Dark fill behind the price band ensures clean type regardless of overflow."""

import os, sys, math
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.path.insert(0, "/home/user/skybit")
import pygame; pygame.init(); pygame.display.set_mode((1, 1))
import game.store_cards as sc
from game.store_cards import (vgrad_stops, plain_text, m, SS, font,
                               CABO_LO, CABO_HI, CARD_T, CARD_B,
                               CARD_RING_BRIGHT, CARD_RING_DEEP)
from game.draw import lerp_color, NEAR_BLACK, WHITE
from PIL import Image, ImageDraw

# Mandatory gloss_sweep BLEND_ADD fix — the shipped helper produces a near-white
# slab under smoothscale on dark bodies; this variant writes (a,a,a,255) so the
# additive amount tracks the curve instead of blowing the dark field.
def _gloss_sweep_fixed(surf, rect, radius, peak=120):
    sweep = pygame.Surface(rect.size, pygame.SRCALPHA)
    h = max(1, rect.h)
    for y in range(h):
        v = int(peak * (1 - y / h) ** 2.4)
        if v <= 0:
            continue
        pygame.draw.line(sweep, (v, v, v, 255), (0, y), (rect.w, y))
    sm = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(sm, (255, 255, 255, 255), sm.get_rect(), border_radius=radius)
    sweep.blit(sm, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(sweep, rect.topleft, special_flags=pygame.BLEND_ADD)
sc.gloss_sweep = _gloss_sweep_fixed

TIERS = [
    ("RARE",      "skin_wizard",    "720",   {"gem": (108, 188, 252), "glow": (60,  140, 230), "deep": (18,  44,  90)}),
    ("EPIC",      "skin_prism",     "1,400", {"gem": (194, 122, 248), "glow": (150,  60, 220), "deep": (44,  10,  80)}),
    ("LEGENDARY", "skin_astronaut", "2,600", {"gem": (255, 202, 104), "glow": (220, 160,  40), "deep": (90,  50,   0)}),
]
NAMES = {"RARE": "WIZARD", "EPIC": "PRISM", "LEGENDARY": "ASTRONAUT"}
POP_W, POP_H = 260, 442
CX = 130
CARD_X, CARD_TOP_Y, CARD_W, CARD_H, CARD_RAD = 10, 127, 240, 299, 23
DISC_CY, DISC_R = 135, 53
GEM_L_X, GEM_R_X, GEM_CY, GEM_R = 43, 217, 152, 14
BOT_GEM_CY = 402
SHELF_X, SHELF_Y, SHELF_W, SHELF_H = 17, 335, 226, 91
BTN_W, BTN_H, BTN_RAD, BTN_CY, BTN_GAP = 99, 31, 12, 360, 10
BUY_CX = CX - (BTN_W + BTN_GAP) // 2
CAN_CX = CX + (BTN_W + BTN_GAP) // 2


def card_body(big):
    rect = pygame.Rect(m(CARD_X), m(CARD_TOP_Y), m(CARD_W), m(CARD_H))
    rad = m(CARD_RAD)
    sc.drop_shadow(big, rect, rad, blur=m(8), alpha=165, dy=m(4))
    big.blit(vgrad_stops(rect.w, rect.h, rad,
                         [(0.0, CARD_T), (1.0, CARD_B)], 255, gamma=1.15),
             rect.topleft)
    sc.top_sheen(big, rect, rad, m(30), peak=56)
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    sc.bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 230), w=max(1, m(1.9)))
    tray = rect.inflate(-m(8), -m(8))
    pygame.draw.rect(big, (*CARD_RING_BRIGHT, 55), tray,
                     width=max(1, m(1)), border_radius=rad - m(3))


def corner_gems(big, pal):
    sc.facet_gem(big, m(GEM_L_X), m(GEM_CY), m(GEM_R), pal["gem"], pal["deep"])
    sc.facet_gem(big, m(GEM_R_X), m(GEM_CY), m(GEM_R), pal["gem"], pal["deep"])


def name_text(big, name):
    nfs = 45
    nfnt = font(nfs)
    mw = m(CARD_W - 20)
    while sc._glyph_base(name, nfnt, 0).get_width() > mw and nfs > 24:
        nfs -= 1
        nfnt = font(nfs)
    plain_text(big, name, nfnt, (m(CX), m(213)), (250, 248, 240),
               shadow_a=160, weight=m(0.9), keyline=(6, 6, 16), kw=m(1.0))


def shelf_and_buttons(big):
    shelf_rect = pygame.Rect(m(SHELF_X), m(SHELF_Y), m(SHELF_W), m(SHELF_H))
    sr = m(CARD_RAD)
    shelf = vgrad_stops(shelf_rect.w, shelf_rect.h, 0,
                        [(0.0, (34, 36, 72)), (0.5, (22, 24, 54)), (1.0, (12, 14, 36))], 255).copy()
    smask = pygame.Surface(shelf_rect.size, pygame.SRCALPHA)
    pygame.draw.rect(smask, (255, 255, 255, 255), smask.get_rect(),
                     border_bottom_left_radius=sr, border_bottom_right_radius=sr)
    shelf.blit(smask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    sc.top_sheen(shelf, shelf.get_rect(), 0, m(20), peak=35)
    pygame.draw.line(shelf, (115, 106, 140), (0, 0), (shelf_rect.w - 1, 0), max(1, m(1)))
    seat = pygame.Surface((shelf_rect.w, m(6)), pygame.SRCALPHA)
    for yy in range(m(6)):
        pygame.draw.line(seat, (0, 0, 0, int(120 * (1 - yy / m(6)))),
                         (0, yy), (shelf_rect.w - 1, yy))
    big.blit(seat, (shelf_rect.x, shelf_rect.y - m(6)))
    big.blit(shelf, shelf_rect.topleft)
    br = m(BTN_RAD)
    for cx_b, lbl, stops, lab_c, pk, rw in [
        (m(BUY_CX),  "BUY",    [(0.0, (38, 40, 84)), (1.0, (22, 24, 56))], (200, 205, 240), 22, m(2.0)),
        (m(CAN_CX), "CANCEL", [(0.0, (26, 28, 64)), (1.0, (14, 16, 44))], (150, 155, 200), 14, m(2.2)),
    ]:
        r = pygame.Rect(0, 0, m(BTN_W), m(BTN_H))
        r.center = (cx_b, m(BTN_CY))
        sc.drop_shadow(big, r, br, blur=m(3), alpha=100, dy=m(2))
        big.blit(vgrad_stops(r.w, r.h, br, stops, 255), r.topleft)
        sc.top_sheen(big, r, br, m(12), peak=pk)
        sc.bevel_rim(big, r, br, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 230), w=max(1, rw))
        plain_text(big, lbl, font(14 if lbl == "BUY" else 13), r.center,
                   lab_c, shadow_a=110, weight=m(0.8), keyline=(8, 6, 20), kw=m(0.9))


def bottom_gems(big, pal):
    for gx in [m(GEM_L_X), m(GEM_R_X)]:
        sc._alpha_aura(big, gx, m(BOT_GEM_CY), m(16), pal["glow"], peak=60, layers=14)
        sc.facet_gem(big, gx, m(BOT_GEM_CY), m(GEM_R), pal["gem"], pal["deep"])


def hero_disc(big, sid, pal):
    cx, cy, r = m(CX), m(DISC_CY), m(DISC_R)
    sc._alpha_aura(big, cx, cy, r + m(55), pal["glow"], peak=95, layers=24)
    sc._alpha_aura(big, cx, cy, r + m(20), pal["glow"], peak=70, layers=12)
    sc.cabochon(big, cx, cy, r, CABO_LO, CABO_HI, ring=pal["gem"], ring_a=50)
    try:
        sc.blit_thumb(big, sid, cx, cy, int(r * 1.5))
    except Exception:
        pygame.draw.circle(big, pal["gem"], (cx, cy), int(r * 0.7))
    sc.cabochon_glass(big, cx, cy, r, tint=pal["gem"])


# ── Zone A — treasury-arch ────────────────────────────────────────────────────

def zone_a_arch(big, price_str, pal, tier_word):
    """Dark-bronze vault gateway: obsidian piers with material presence flanking
    a FILLED arch (annulus sector) in tier-neutral dark metal — the KEYSTONE and
    RIBBON carry the tier hue so Zone A and Zone B never land in the same family.
    LEGENDARY keystone shifts to platinum so it reads against the gold ribbon
    below. Soffit glow spills downward from the inner crown, pricing reads lit
    from above."""

    arch_base_y  = m(248)   # springline; price sits just below this
    arch_outer_r = m(42)    # crown at y=248-42=206, below disc bottom at ~188
    arch_inner_r = m(30)    # inner crown at y=248-30=218; ring width 12 logical px
    arch_cx      = m(CX)    # horizontally centred on the popup

    pier_w = m(12)
    pier_h = m(62)          # piers sit below the springline, forming the vault sides
    pier_top = arch_base_y  # springline is the pier top — arch rests on pier caps

    # ── Piers ─────────────────────────────────────────────────────────────────
    for px in (m(50), m(200)):
        pier = pygame.Rect(px, pier_top, pier_w, pier_h)

        # Dark backdrop behind each pier so the warm pier body reads clearly
        # against the deep card field — lum≈8 vs pier lum≈70, delta ≈62.
        pygame.draw.rect(big, (8, 6, 14),
                         pier.inflate(m(2), m(2)))

        sc.drop_shadow(big, pier, m(3), blur=m(3), alpha=90, dy=m(2))

        # Warm obsidian pier body — lighter than the card body (lum≈23) by ≥40.
        big.blit(vgrad_stops(pier_w, pier_h, m(3),
                             [(0.0, (90, 80, 60)), (1.0, (70, 62, 46))], 255,
                             gamma=1.05),
                 pier.topleft)

        # Crisp dark outer keyline anchors the pier edge against the card.
        sc.bevel_rim(big, pier, m(3), (8, 6, 16),
                     (*CARD_RING_BRIGHT, 220), w=max(1, m(1.5)))

        # Lit inward face — soffit light catching the pier edge facing the vault.
        inward_x = (pier.right - m(2)) if px == m(50) else pier.left
        for yy in range(pier_h):
            t = yy / max(1, pier_h - 1)
            col = lerp_color((140, 120, 80), (80, 65, 42), t)
            pygame.draw.line(big, col,
                             (inward_x, pier.top + yy),
                             (inward_x + m(2) - 1, pier.top + yy))

    # ── Arch fill (annulus sector) ─────────────────────────────────────────────
    # Build as a filled polygon (outer arc forward + inner arc reversed) so the
    # ring is solid and AA-clean at SS=2 — pygame.draw.arc stays 1 px thin.
    n_steps = 48
    outer_pts, inner_pts = [], []
    for i in range(n_steps + 1):
        ang = math.pi - (math.pi * i / n_steps)   # left→crown→right
        outer_pts.append((int(arch_cx + arch_outer_r * math.cos(ang)),
                          int(arch_base_y - arch_outer_r * math.sin(ang))))
        inner_pts.append((int(arch_cx + arch_inner_r * math.cos(ang)),
                          int(arch_base_y - arch_inner_r * math.sin(ang))))
    arch_poly = outer_pts + list(reversed(inner_pts))

    # Dark bronze gradient — hue-neutral so any tier keystone/ribbon pops against
    # this metal rather than blending into it.
    bx  = min(p[0] for p in arch_poly)
    byt = min(p[1] for p in arch_poly)
    bw  = max(p[0] for p in arch_poly) - bx + 1
    bh  = arch_base_y - byt + 1
    grad = vgrad_stops(bw, bh, 0,
                       [(0.0, (80, 68, 52)), (0.45, (100, 84, 62)), (1.0, (60, 50, 38))],
                       255)
    ring_mask = pygame.Surface((bw, bh), pygame.SRCALPHA)
    pygame.draw.polygon(ring_mask, (255, 255, 255, 255),
                        [(px - bx, py - byt) for px, py in arch_poly])
    grad.blit(ring_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(grad, (bx, byt))

    # Dark outer keyline + bright inner soffit line = machined-bevel read.
    pygame.draw.polygon(big, (6, 4, 16), arch_poly, width=max(1, m(1.4)))
    pygame.draw.lines(big, (*lerp_color(CARD_RING_BRIGHT, WHITE, 0.4), 210),
                      False, inner_pts, max(1, m(1.0)))

    # ── Keystone ──────────────────────────────────────────────────────────────
    apex_x = arch_cx
    apex_y = arch_base_y - arch_outer_r

    # LEGENDARY: dark bronze arch + gold ribbon already pair; platinum keystone
    # gives Zone A a third hue (cool-silver) distinct from both arch and ribbon.
    if tier_word == "LEGENDARY":
        ks_gem  = (220, 220, 230)
        ks_deep = (100, 100, 115)
    else:
        ks_gem  = pal["gem"]
        ks_deep = pal["deep"]

    sc._alpha_aura(big, apex_x, apex_y, m(16), pal["glow"], peak=80, layers=10)
    sc.facet_gem(big, apex_x, apex_y, m(10), ks_gem, ks_deep)

    # ── Soffit glow ───────────────────────────────────────────────────────────
    # Origin at the underside of the inner arch crown so the glow spills downward
    # through the vault opening onto the price — reads as the vault casting light.
    soffit_cy = arch_base_y - arch_inner_r + m(4)   # just below inner crown
    sc.soft_glow(big, arch_cx, soffit_cy, m(32), pal["glow"], peak_alpha=35, layers=12)
    sc._alpha_aura(big, arch_cx, soffit_cy, m(22), pal["gem"], peak=20, layers=8)

    # ── Price band ────────────────────────────────────────────────────────────
    price_y = m(258)

    # Clean dark fill behind coin+price so any arch foot bleed is covered and
    # the text always reads on a known dark ground (contrast ≥7:1).
    band_h = m(34)
    band = pygame.Surface((m(160), band_h), pygame.SRCALPHA)
    band.fill((12, 11, 28, 210))
    big.blit(band, (m(CX) - m(80), price_y - band_h // 2))

    sc.coin_glyph(big, m(CX - 30), price_y, m(14))
    plain_text(big, price_str, font(22), (m(CX + 20), price_y), (250, 245, 235),
               shadow_a=180, weight=m(1.2), keyline=(6, 6, 16), kw=m(1.0))


# ── render loop ───────────────────────────────────────────────────────────────

def render_popup(tier_word, sid, price_str, pal):
    big = pygame.Surface((POP_W * SS, POP_H * SS), pygame.SRCALPHA)
    card_body(big)
    corner_gems(big, pal)
    # Draw arch before hero disc and name so both render on top of the gateway,
    # keeping disc glass + name keyline cleanly legible.
    zone_a_arch(big, price_str, pal, tier_word)
    hero_disc(big, sid, pal)
    name_text(big, NAMES[tier_word])
    shelf_and_buttons(big)
    sc._ribbon_lozenge(big, tier_word, m(CX), m(BOT_GEM_CY), m(146), pal)
    bottom_gems(big, pal)
    return pygame.transform.smoothscale(big, (POP_W, POP_H))


MARGIN, HEAD, GAP = 20, 58, 12
STRIP_W = MARGIN * 2 + len(TIERS) * (POP_W + GAP) - GAP
STRIP_H = HEAD + POP_H + MARGIN
strip = Image.new("RGB", (STRIP_W, STRIP_H), (8, 8, 20))
idr = ImageDraw.Draw(strip)
idr.text((MARGIN, 18), "treasury-arch · swap-round-2 · round 2", fill=(232, 226, 208))
for i, (tw, sid, ps, pal) in enumerate(TIERS):
    pop = render_popup(tw, sid, ps, pal)
    pil = Image.frombytes("RGB", (POP_W, POP_H), pygame.image.tostring(pop, "RGB"))
    x = MARGIN + i * (POP_W + GAP)
    strip.paste(pil, (x, HEAD))
    idr.text((x + POP_W // 2, HEAD + POP_H + 6), tw, fill=(180, 176, 210), anchor="mt")

out = strip.resize((STRIP_W * 2, STRIP_H * 2), Image.LANCZOS)

import pathlib
OUTDIR = "/home/user/skybit/docs/confirm_purchase_v8/swap-round-2/treasury-arch"
pathlib.Path(OUTDIR).mkdir(parents=True, exist_ok=True)
OUT = f"{OUTDIR}/round_2.png"
out.save(OUT)
print(f"saved {out.size[0]}x{out.size[1]}  ->  {OUT}")
