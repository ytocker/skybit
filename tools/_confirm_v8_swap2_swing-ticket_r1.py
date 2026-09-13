#!/usr/bin/env python3
"""swing-ticket · confirm_purchase_v8 · swap-round-2

Zone A is a hero-scale landscape cream sumi hang-tag (~150×82 logical, -4°)
hung from a cord that rises toward the item name. Coin + price in heavy sumi
ink on the cream face; a tier wax-seal in the lower-right corner. This reuses
the _draw_hang_tag / _tag_draw_price RECIPE but rebuilds the geometry as a
LANDSCAPE face — the store's own tag chip is portrait 81×94 and must not be
called here. Zone B stays the store_cards notched-hex _ribbon.
"""
import os, sys, math
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.path.insert(0, "/home/user/skybit")
import pygame; pygame.init(); pygame.display.set_mode((1, 1))
import game.store_cards as sc
from game.store_cards import vgrad_stops, plain_text, m, SS, font, CABO_LO, CABO_HI, CARD_T, CARD_B, CARD_RING_BRIGHT, CARD_RING_DEEP
from game.draw import lerp_color, NEAR_BLACK, WHITE
from PIL import Image, ImageDraw

# mandatory gloss_sweep patch — BLEND_ADD-safe so dark bodies don't blow to white
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

# Representative prices per tier (ink-on-cream, so tier gold never fights them)
TIERS = [
    ("RARE", "skin_wizard", "720", {"gem": (108, 188, 252), "glow": (60, 140, 230), "deep": (18, 44, 90)}),
    ("EPIC", "skin_prism", "1,200", {"gem": (194, 122, 248), "glow": (150, 60, 220), "deep": (44, 10, 80)}),
    ("LEGENDARY", "skin_astronaut", "2,800", {"gem": (255, 202, 104), "glow": (220, 160, 40), "deep": (90, 50, 0)}),
]
NAMES = {"RARE": "WIZARD", "EPIC": "PRISM", "LEGENDARY": "ASTRONAUT"}
POP_W, POP_H = 260, 442; CX = 130
CARD_X, CARD_TOP_Y, CARD_W, CARD_H, CARD_RAD = 10, 127, 240, 299, 23
DISC_CY, DISC_R = 135, 53
GEM_L_X, GEM_R_X, GEM_CY, GEM_R = 43, 217, 152, 14
CHIP_CY = 247; Y_BANNER = 402; BOT_GEM_CY = 402
SHELF_X, SHELF_Y, SHELF_W, SHELF_H = 17, 335, 226, 91
BTN_W, BTN_H, BTN_RAD, BTN_CY, BTN_GAP = 99, 31, 12, 360, 10
BUY_CX = CX - (BTN_W + BTN_GAP) // 2; CAN_CX = CX + (BTN_W + BTN_GAP) // 2

def card_body(big):
    rect = pygame.Rect(m(CARD_X), m(CARD_TOP_Y), m(CARD_W), m(CARD_H)); rad = m(CARD_RAD)
    sc.drop_shadow(big, rect, rad, blur=m(8), alpha=165, dy=m(4))
    big.blit(vgrad_stops(rect.w, rect.h, rad, [(0.0, CARD_T), (1.0, CARD_B)], 255, gamma=1.15), rect.topleft)
    sc.top_sheen(big, rect, rad, m(30), peak=56)
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    sc.bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 230), w=max(1, m(1.9)))
    tray = rect.inflate(-m(8), -m(8))
    pygame.draw.rect(big, (*CARD_RING_BRIGHT, 55), tray, width=max(1, m(1)), border_radius=rad - m(3))

def corner_gems(big, pal):
    sc.facet_gem(big, m(GEM_L_X), m(GEM_CY), m(GEM_R), pal["gem"], pal["deep"])
    sc.facet_gem(big, m(GEM_R_X), m(GEM_CY), m(GEM_R), pal["gem"], pal["deep"])

def name_text(big, name):
    nfs = 45; nfnt = font(nfs); mw = m(CARD_W - 20)
    while sc._glyph_base(name, nfnt, 0).get_width() > mw and nfs > 24:
        nfs -= 1; nfnt = font(nfs)
    plain_text(big, name, nfnt, (m(CX), m(213)), (250, 248, 240), shadow_a=160, weight=m(0.9), keyline=(6, 6, 16), kw=m(1.0))

def shelf_and_buttons(big):
    shelf_rect = pygame.Rect(m(SHELF_X), m(SHELF_Y), m(SHELF_W), m(SHELF_H)); sr = m(CARD_RAD)
    shelf = vgrad_stops(shelf_rect.w, shelf_rect.h, 0, [(0.0, (34, 36, 72)), (0.5, (22, 24, 54)), (1.0, (12, 14, 36))], 255).copy()
    smask = pygame.Surface(shelf_rect.size, pygame.SRCALPHA)
    pygame.draw.rect(smask, (255, 255, 255, 255), smask.get_rect(), border_bottom_left_radius=sr, border_bottom_right_radius=sr)
    shelf.blit(smask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    sc.top_sheen(shelf, shelf.get_rect(), 0, m(20), peak=35)
    pygame.draw.line(shelf, (115, 106, 140), (0, 0), (shelf_rect.w - 1, 0), max(1, m(1)))
    seat = pygame.Surface((shelf_rect.w, m(6)), pygame.SRCALPHA)
    for yy in range(m(6)):
        pygame.draw.line(seat, (0, 0, 0, int(120 * (1 - yy / m(6)))), (0, yy), (shelf_rect.w - 1, yy))
    big.blit(seat, (shelf_rect.x, shelf_rect.y - m(6))); big.blit(shelf, shelf_rect.topleft)
    br = m(BTN_RAD)
    for cx_b, lbl, stops, lab_c, pk, rw in [
        (m(BUY_CX), "BUY", [(0.0, (38, 40, 84)), (1.0, (22, 24, 56))], (200, 205, 240), 22, m(2.0)),
        (m(CAN_CX), "CANCEL", [(0.0, (26, 28, 64)), (1.0, (14, 16, 44))], (150, 155, 200), 14, m(2.2)),
    ]:
        r = pygame.Rect(0, 0, m(BTN_W), m(BTN_H)); r.center = (cx_b, m(BTN_CY))
        sc.drop_shadow(big, r, br, blur=m(3), alpha=100, dy=m(2))
        big.blit(vgrad_stops(r.w, r.h, br, stops, 255), r.topleft)
        sc.top_sheen(big, r, br, m(12), peak=pk)
        sc.bevel_rim(big, r, br, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 230), w=max(1, rw))
        plain_text(big, lbl, font(14 if lbl == "BUY" else 13), r.center, lab_c, shadow_a=110, weight=m(0.8), keyline=(8, 6, 20), kw=m(0.9))

def bottom_gems(big, pal):
    for gx in [m(GEM_L_X), m(GEM_R_X)]:
        sc._alpha_aura(big, gx, m(BOT_GEM_CY), m(16), pal["glow"], peak=60, layers=14)
        sc.facet_gem(big, gx, m(BOT_GEM_CY), m(GEM_R), pal["gem"], pal["deep"])

def hero_disc(big, sid, pal):
    cx, cy, r = m(CX), m(DISC_CY), m(DISC_R)
    sc._alpha_aura(big, cx, cy, r + m(55), pal["glow"], peak=95, layers=24)
    sc._alpha_aura(big, cx, cy, r + m(20), pal["glow"], peak=70, layers=12)
    sc.cabochon(big, cx, cy, r, CABO_LO, CABO_HI, ring=pal["gem"], ring_a=50)
    try: sc.blit_thumb(big, sid, cx, cy, int(r * 1.5))
    except Exception: pygame.draw.circle(big, pal["gem"], (cx, cy), int(r * 0.7))
    sc.cabochon_glass(big, cx, cy, r, tint=pal["gem"])

# ── Zone A — swing-ticket (hero landscape hang-tag) ───────────────────────────
def zone_a_swing_ticket(big, price_str, pal):
    """Hero landscape sumi hang-tag: cream face, coin + heavy-ink price inline,
    wedge-taper rule, tier wax-seal lower-right, hung from a cord + charm gem
    that rises toward the name. Custom 150×82 landscape geometry — NOT the
    store's portrait price_chip."""
    TAG_W, TAG_H = m(150), m(82)
    face = pygame.Surface((TAG_W, TAG_H), pygame.SRCALPHA)
    face_rect = pygame.Rect(0, 0, TAG_W, TAG_H)
    rad = m(5)

    # Cream body — same aged-paper recipe as _draw_hang_tag
    body = sc.vgrad_stops(TAG_W, TAG_H, rad,
        [(0.0, (248, 238, 210)), (0.6, (236, 224, 188)), (1.0, (220, 200, 160))], 255, gamma=1.04)
    face.blit(body, (0, 0))
    sc.bevel_rim(face, face_rect, rad, (80, 52, 12, 200), (255, 240, 190, 200), w=max(1, m(1.2)))

    # Grommet hole (top-left) the cord threads through
    grommet_cx, grommet_cy = m(22), m(16)
    pygame.draw.circle(face, (0, 0, 0, 0), (grommet_cx, grommet_cy), m(5))
    pygame.draw.circle(face, (110, 80, 30), (grommet_cx, grommet_cy), m(5) + 1, width=max(1, m(1)))

    # Coin + price sit on one baseline, near-black warm ink on cream
    face_coin_cx = m(38)
    face_cy = TAG_H // 2 + m(4)
    sc.coin_glyph(face, face_coin_cx, face_cy, m(16))

    price_col = (40, 28, 18)
    price_font = sc.font(20)
    price_w = sc._glyph_base(price_str, price_font, 0).get_width()
    price_x = face_coin_cx + m(22)
    plain_text(face, price_str, price_font, (price_x + price_w // 2, face_cy),
               price_col, shadow_a=0, weight=m(1.4))

    # Wedge-taper finishing rule under the numeral (echoes _tag_draw_price)
    rule_y = face_cy + m(12)
    rule_x0 = price_x
    rule_x1 = price_x + price_w
    for i, thickness in enumerate([m(2.5), m(1.5), m(0.8)]):
        pygame.draw.line(face, (*price_col, 200 - i * 60),
                         (rule_x0 + i * 2, rule_y + i), (rule_x1 - i, rule_y + i), max(1, int(thickness)))

    # Tier wax-seal, lower-right — physically clear of the ink price (no gold-on-gold)
    seal_cx, seal_cy = TAG_W - m(22), TAG_H - m(18)
    pygame.draw.circle(face, pal["glow"], (seal_cx, seal_cy), m(9))
    pygame.draw.circle(face, pal["gem"], (seal_cx, seal_cy), m(9), width=max(1, m(1.5)))

    # Rotate -4° (positive arg = CCW) and land just below cy=247 so the tilted
    # visual centre reads at the zone centre.
    rot = pygame.transform.rotate(face, 4)
    tag_center = (m(CX), m(252))
    big.blit(rot, rot.get_rect(center=tag_center))

    # Cord rising from grommet toward the name, with a charm gem threaded on it
    cord = (190, 165, 115)
    knot = (m(CX) - m(78), m(222))
    grommet_pos = (m(CX) - m(62), m(228))
    pygame.draw.line(big, cord, grommet_pos, (knot[0] - 1, knot[1] - 1), max(1, m(1.5)))
    pygame.draw.line(big, cord, grommet_pos, (knot[0] + 2, knot[1] + 2), max(1, m(1.5)))
    pygame.draw.circle(big, cord, knot, max(1, m(1.5)))

    charm_pos = ((grommet_pos[0] + knot[0]) // 2, (grommet_pos[1] + knot[1]) // 2)
    sc.facet_gem(big, charm_pos[0], charm_pos[1], m(6), pal["gem"], pal["deep"])

# ── Zone B — notched-hex _ribbon ──────────────────────────────────────────────
def zone_b_ribbon(big, tier_word, pal):
    sc._ribbon(big, tier_word, m(CX), m(Y_BANNER), m(146), pal)

# ── render loop ───────────────────────────────────────────────────────────────
def render_popup(tier_word, sid, price_str, pal):
    big = pygame.Surface((POP_W * SS, POP_H * SS), pygame.SRCALPHA)
    card_body(big); corner_gems(big, pal); name_text(big, NAMES[tier_word])
    zone_a_swing_ticket(big, price_str, pal)
    shelf_and_buttons(big)
    zone_b_ribbon(big, tier_word, pal)
    bottom_gems(big, pal); hero_disc(big, sid, pal)
    return pygame.transform.smoothscale(big, (POP_W, POP_H))

MARGIN, HEAD, GAP = 20, 58, 12
STRIP_W = MARGIN * 2 + len(TIERS) * (POP_W + GAP) - GAP; STRIP_H = HEAD + POP_H + MARGIN
strip = Image.new("RGB", (STRIP_W, STRIP_H), (8, 8, 20))
idr = ImageDraw.Draw(strip)
idr.text((MARGIN, 18), "swing-ticket · swap-round-2 · round 1", fill=(232, 226, 208))
for i, (tw, sid, ps, pal) in enumerate(TIERS):
    pop = render_popup(tw, sid, ps, pal)
    pil = Image.frombytes("RGB", (POP_W, POP_H), pygame.image.tostring(pop, "RGB"))
    x = MARGIN + i * (POP_W + GAP); strip.paste(pil, (x, HEAD))
    idr.text((x + POP_W // 2, HEAD + POP_H + 6), tw, fill=(180, 176, 210), anchor="mt")
out = strip.resize((STRIP_W * 2, STRIP_H * 2), Image.LANCZOS)
import pathlib
OUTDIR = "/home/user/skybit/docs/confirm_purchase_v8/swap-round-2/swing-ticket"
pathlib.Path(OUTDIR).mkdir(parents=True, exist_ok=True)
OUT = OUTDIR + "/round_1.png"
out.save(OUT); print(f"saved {out.size[0]}×{out.size[1]}  →  {OUT}")
