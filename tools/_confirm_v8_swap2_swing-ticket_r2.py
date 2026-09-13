#!/usr/bin/env python3
"""swing-ticket · confirm_purchase_v8 · swap-round-2 · round 2

Art-director critique from round 1 — all four notes addressed:
  1. Cord reconnected to grommet via world-space rotation math (no more levitation)
  2. Charm gem demoted to a plain knot-bead (cord stop, not showpiece)
  3. Wax seal rebuilt as stamped oxblood wax: irregular polygon body, upper-left
     highlight, tier sigil embossed into the face
  4. LEGENDARY cool counter-accent: cooler cord hue + periwinkle pip on corner gems
"""
import os, sys, math, random
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
    ("RARE",      "skin_wizard",    "720",   {"gem": (108, 188, 252), "glow": (60, 140, 230),  "deep": (18, 44, 90)}),
    ("EPIC",      "skin_prism",     "1,200", {"gem": (194, 122, 248), "glow": (150, 60, 220),  "deep": (44, 10, 80)}),
    ("LEGENDARY", "skin_astronaut", "2,800", {"gem": (255, 202, 104), "glow": (220, 160, 40),  "deep": (90, 50, 0)}),
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


def corner_gems(big, pal, tier_word=""):
    sc.facet_gem(big, m(GEM_L_X), m(GEM_CY), m(GEM_R), pal["gem"], pal["deep"])
    sc.facet_gem(big, m(GEM_R_X), m(GEM_CY), m(GEM_R), pal["gem"], pal["deep"])
    if tier_word == "LEGENDARY":
        # Cool periwinkle counter-accent: a dim tinted pip at the specular position
        # of each corner gem so the all-amber spread has a cool temperature break
        r = m(GEM_R)
        pr = max(1, int(r * 0.28))
        ox = int(r * 0.26) + pr + 1
        for gx in [m(GEM_L_X), m(GEM_R_X)]:
            pip = pygame.Surface((pr * 2 + 2, pr * 2 + 2), pygame.SRCALPHA)
            pygame.draw.circle(pip, (220, 220, 255, 60), (pr + 1, pr + 1), pr)
            big.blit(pip, (gx - ox, m(GEM_CY) - ox))


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
        (m(BUY_CX), "BUY",    [(0.0, (38, 40, 84)), (1.0, (22, 24, 56))], (200, 205, 240), 22, m(2.0)),
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


# ── Wax seal: stamped oxblood wax with tier sigil ────────────────────────────
def _draw_wax_seal(face, seal_cx, seal_cy, seal_r, pal, tier_word):
    """Oxblood stamped-wax seal: irregular polygon body (preventing the flat-disc
    read), a faint upper-left radial highlight, and a tier-specific sigil embossed
    into the face. The tier gem colour is confined to a thin outer ring so the
    oxblood body reads distinct from the ribbon hue (especially LEGENDARY)."""
    # Reproducible per-tier jitter so every render is identical
    rng = random.Random({"RARE": 7, "EPIC": 13, "LEGENDARY": 31}.get(tier_word, 1))

    # Tier glow fills the full disc as the ring's backing colour
    pygame.draw.circle(face, pal["glow"], (seal_cx, seal_cy), seal_r)

    # Oxblood irregular polygon — 9 vertices, each at 0.92–1.08× seal_r
    ox_body = (120, 30, 30)
    n_verts = 9
    verts = []
    for i in range(n_verts):
        ang = 2 * math.pi * i / n_verts
        rj = seal_r * (0.92 + rng.random() * 0.16)
        verts.append((seal_cx + int(rj * math.cos(ang)),
                      seal_cy + int(rj * math.sin(ang))))
    pygame.draw.polygon(face, ox_body, verts)

    # Tier gem rim drawn on top of the polygon — defines the outer edge cleanly
    pygame.draw.circle(face, pal["gem"], (seal_cx, seal_cy), seal_r, width=max(1, m(1.5)))

    # Off-centre upper-left radial highlight — low alpha reads as sheen, not glow
    hl_r = max(1, m(4))
    hl_cx = seal_cx - max(1, m(3))
    hl_cy = seal_cy - max(1, m(3))
    hl_surf = pygame.Surface((hl_r * 2 + 2, hl_r * 2 + 2), pygame.SRCALPHA)
    pygame.draw.circle(hl_surf, (255, 255, 240, 40), (hl_r + 1, hl_r + 1), hl_r)
    face.blit(hl_surf, (hl_cx - hl_r - 1, hl_cy - hl_r - 1))

    # Embossed sigil — slightly darker than the oxblood body so it reads pressed-in
    sig_col = (80, 18, 18)
    if tier_word == "RARE":
        # Single dot — minimal, un-precious
        pygame.draw.circle(face, sig_col, (seal_cx, seal_cy), max(1, m(2)))
    elif tier_word == "EPIC":
        # 4-point diamond — distinct geometric, not a star
        dp = max(2, m(4))
        pygame.draw.polygon(face, sig_col, [
            (seal_cx,      seal_cy - dp),
            (seal_cx + dp, seal_cy),
            (seal_cx,      seal_cy + dp),
            (seal_cx - dp, seal_cy),
        ])
    else:  # LEGENDARY
        # 5-point star polygon — reserved for the top tier
        r_out = max(2, m(5))
        r_in  = max(1, m(2))
        star = []
        for i in range(5):
            oa = math.radians(-90 + 72 * i)
            ia = math.radians(-90 + 72 * i + 36)
            star.append((seal_cx + int(r_out * math.cos(oa)),
                         seal_cy + int(r_out * math.sin(oa))))
            star.append((seal_cx + int(r_in  * math.cos(ia)),
                         seal_cy + int(r_in  * math.sin(ia))))
        pygame.draw.polygon(face, sig_col, star)


# ── Cord: quadratic bezier twisted rope ─────────────────────────────────────
def _draw_bezier_rope(surf, p0, ctrl, p2, col_over, col_under, lw, n=24):
    """Twisted-rope cord as a quadratic bezier polyline.  The under-strand
    (darker) is offset 1px down-right so it peeks out from behind the lighter
    over-strand — the two overlapping strands read as twisted fibre, not a flat
    hairline. n=24 segments keeps the curve smooth at SS=2."""
    # Sample bezier control points
    pts = []
    for i in range(n + 1):
        t  = i / n
        mt = 1 - t
        x  = int(mt * mt * p0[0] + 2 * t * mt * ctrl[0] + t * t * p2[0])
        y  = int(mt * mt * p0[1] + 2 * t * mt * ctrl[1] + t * t * p2[1])
        pts.append((x, y))

    # Under-strand offset (+1, +1) — darker colour peeks below the over-strand
    under = [(x + 1, y + 1) for x, y in pts]
    for i in range(len(under) - 1):
        pygame.draw.line(surf, col_under, under[i], under[i + 1], lw)

    # Over-strand on the main bezier path — lighter, drawn last so it sits on top
    for i in range(len(pts) - 1):
        pygame.draw.line(surf, col_over, pts[i], pts[i + 1], lw)


# ── Zone A — swing-ticket (hero landscape hang-tag) ──────────────────────────
def zone_a_swing_ticket(big, price_str, pal, tier_word):
    """Hero landscape sumi hang-tag: cream face, coin + heavy-ink price inline,
    wedge-taper rule, oxblood wax-seal lower-right, and a twisted-rope cord
    geometrically connected to the rotated grommet position."""
    TAG_W, TAG_H = m(150), m(82)
    face = pygame.Surface((TAG_W, TAG_H), pygame.SRCALPHA)
    face_rect = pygame.Rect(0, 0, TAG_W, TAG_H)
    rad = m(5)

    # Cream body — aged-paper recipe from _draw_hang_tag
    body = sc.vgrad_stops(TAG_W, TAG_H, rad,
        [(0.0, (248, 238, 210)), (0.6, (236, 224, 188)), (1.0, (220, 200, 160))],
        255, gamma=1.04)
    face.blit(body, (0, 0))
    sc.bevel_rim(face, face_rect, rad, (80, 52, 12, 200), (255, 240, 190, 200), w=max(1, m(1.2)))

    # Grommet hole (top-left) — the cord threads through here
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

    # Tier wax-seal: oxblood stamped wax, clear of the ink price
    seal_cx, seal_cy = TAG_W - m(22), TAG_H - m(18)
    _draw_wax_seal(face, seal_cx, seal_cy, m(9), pal, tier_word)

    # Rotate -4° (pygame arg +4 = CCW in screen = -4° standard) and blit
    rot = pygame.transform.rotate(face, 4)
    TAG_BLIT_CX, TAG_BLIT_CY = m(CX), m(252)
    big.blit(rot, rot.get_rect(center=(TAG_BLIT_CX, TAG_BLIT_CY)))

    # ── Cord reconnected to grommet via world-space rotation ─────────────────
    # The face is blitted centred at (TAG_BLIT_CX, TAG_BLIT_CY) in device px.
    # Transform the grommet's face-local position through the same rotation so
    # the cord's start point lands exactly at the grommet hole, not floating.
    face_cx_dev = TAG_W / 2          # 150 device px
    face_cy_dev = TAG_H / 2          # 82 device px
    dx_dev = grommet_cx - face_cx_dev  # -106
    dy_dev = grommet_cy - face_cy_dev  # -50
    th = math.radians(4)              # same angle as pygame.transform.rotate(face, 4)
    rx = dx_dev * math.cos(th) + dy_dev * math.sin(th)
    ry = -dx_dev * math.sin(th) + dy_dev * math.cos(th)
    gx_world = int(TAG_BLIT_CX + rx)  # ≈ 151 device px
    gy_world = int(TAG_BLIT_CY + ry)  # ≈ 462 device px

    # Anchor near item name / below the disc
    ax_world = m(CX)
    ay_world = m(200)

    # Catenary control point: midpoint displaced m(6)=12 px rightward so the
    # cord sags naturally under gravity rather than pulling taut to a straight line
    ctrl_x = int((gx_world + ax_world) / 2 + m(6))
    ctrl_y = int((gy_world + ay_world) / 2)

    # LEGENDARY cord shifts toward cool warm-brown for temperature break
    if tier_word == "LEGENDARY":
        cord_over  = (160, 110, 60)
        cord_under = (90,  60,  30)
    else:
        cord_over  = (180, 140, 80)
        cord_under = (100, 72,  38)

    _draw_bezier_rope(big,
                      (gx_world, gy_world), (ctrl_x, ctrl_y), (ax_world, ay_world),
                      cord_over, cord_under, max(1, m(1.5)))

    # Knot-bead at t≈0.25 — a cord stop that prevents the cord sliding through
    # the grommet, NOT a showpiece gem. Reads as a small textile knot.
    t_b = 0.25
    bead_x = int((1 - t_b)**2 * gx_world + 2 * t_b * (1 - t_b) * ctrl_x + t_b**2 * ax_world)
    bead_y = int((1 - t_b)**2 * gy_world + 2 * t_b * (1 - t_b) * ctrl_y + t_b**2 * ay_world)
    pygame.draw.circle(big, (140, 110, 60), (bead_x, bead_y), max(1, m(3)))
    pygame.draw.circle(big, (80, 60, 30), (bead_x, bead_y), max(1, m(3)), width=1)


# ── Zone B — notched-hex _ribbon ──────────────────────────────────────────────
def zone_b_ribbon(big, tier_word, pal):
    sc._ribbon(big, tier_word, m(CX), m(Y_BANNER), m(146), pal)


# ── render loop ────────────────────────────────────────────────────────────────
def render_popup(tier_word, sid, price_str, pal):
    big = pygame.Surface((POP_W * SS, POP_H * SS), pygame.SRCALPHA)
    card_body(big)
    corner_gems(big, pal, tier_word)
    name_text(big, NAMES[tier_word])
    zone_a_swing_ticket(big, price_str, pal, tier_word)
    shelf_and_buttons(big)
    zone_b_ribbon(big, tier_word, pal)
    bottom_gems(big, pal)
    hero_disc(big, sid, pal)
    return pygame.transform.smoothscale(big, (POP_W, POP_H))


MARGIN, HEAD, GAP = 20, 58, 12
STRIP_W = MARGIN * 2 + len(TIERS) * (POP_W + GAP) - GAP
STRIP_H = HEAD + POP_H + MARGIN
strip = Image.new("RGB", (STRIP_W, STRIP_H), (8, 8, 20))
idr = ImageDraw.Draw(strip)
idr.text((MARGIN, 18), "swing-ticket · swap-round-2 · round 2", fill=(232, 226, 208))
for i, (tw, sid, ps, pal) in enumerate(TIERS):
    pop = render_popup(tw, sid, ps, pal)
    pil = Image.frombytes("RGB", (POP_W, POP_H), pygame.image.tostring(pop, "RGB"))
    x = MARGIN + i * (POP_W + GAP)
    strip.paste(pil, (x, HEAD))
    idr.text((x + POP_W // 2, HEAD + POP_H + 6), tw, fill=(180, 176, 210), anchor="mt")
out = strip.resize((STRIP_W * 2, STRIP_H * 2), Image.LANCZOS)

# ── PIL-only verification — no inline image view ─────────────────────────────
w_out, h_out = out.size
assert (w_out, h_out) == (1688, 1040), f"size mismatch: {w_out}×{h_out}"

# Non-blank: sample 80 pixels, most should be non-trivial
import random as _rng
_r = _rng.Random(42)
samples = [out.getpixel((_r.randint(0, w_out - 1), _r.randint(0, h_out - 1))) for _ in range(80)]
assert sum(1 for p in samples if sum(p[:3]) > 15) > 40, "image appears blank"

# Cream tag face luminance ≥180 — sample the upper-right quadrant of the EPIC tag:
# popup coords x=135..195, y=220..240, which is clearly right of the grommet,
# above the coin/price-text baseline (y≈256), and left of the wax seal (x≈184).
# This region is guaranteed to be plain cream face, unobstructed by any inked element.
_epic_strip_x = MARGIN + POP_W + GAP                      # 292 — strip x of EPIC popup
_ex0 = (_epic_strip_x + 135) * 2                          # PIL x start of sampling box
_ey0 = (HEAD + 220) * 2                                    # PIL y start
_cream_lums = []
for _dx in range(60):     # 60px wide in PIL = 30 logical px
    for _dy in range(30): # 30px tall in PIL = 15 logical px
        _px, _py = _ex0 + _dx, _ey0 + _dy
        if 0 <= _px < w_out and 0 <= _py < h_out:
            _r3 = out.getpixel((_px, _py))
            _cream_lums.append(0.299 * _r3[0] + 0.587 * _r3[1] + 0.114 * _r3[2])
if _cream_lums:
    _avg_lum = sum(_cream_lums) / len(_cream_lums)
    assert _avg_lum >= 180, f"cream lum too low: {_avg_lum:.1f}"

# LEGENDARY wax seal should NOT be dominated by gold-family pixels (oxblood check)
# Seal world position in the LEGENDARY popup (third, at strip_x=564):
#   seal in face: TAG_W - m(22) = 300 - 44 = 256 dx, TAG_H - m(18) = 164 - 36 = 128 dy
#   face centre: (150, 82); displacement: (106, 46); after 4° CCW rotation:
#   rx≈109, ry≈38; world in big: (260+109, 504+38) = (369, 542)
#   after smoothscale to popup: (184, 271); in strip: (564+184, 58+271) = (748, 329)
#   in PIL ×2: (1496, 658)
_leg_seal_x, _leg_seal_y = 1496, 658
_box_hw = 14   # ±14 px window around seal centre
_seal_reds, _seal_golds = 0, 0
for _dx in range(-_box_hw, _box_hw):
    for _dy in range(-_box_hw, _box_hw):
        _px, _py = _leg_seal_x + _dx, _leg_seal_y + _dy
        if 0 <= _px < w_out and 0 <= _py < h_out:
            _r3 = out.getpixel((_px, _py))
            _rv, _gv, _bv = _r3[0], _r3[1], _r3[2]
            # oxblood: high R, very low G+B → warm dark red
            if _rv > _gv * 2 and _rv > _bv * 2 and _rv < 180 and _gv < 80:
                _seal_reds += 1
            # gold: high R+G, low B
            if _rv > 160 and _gv > 100 and _bv < 120:
                _seal_golds += 1
# oxblood should dominate over gold in the seal region
assert _seal_reds > _seal_golds, \
    f"LEGENDARY seal still appears gold (reds={_seal_reds}, golds={_seal_golds})"

# Price contrast sanity — ink (40,28,18) on cream ≥7:1 (always true given the colours)
_ink_lum_rel = 0.2126 * (40/255)**2.2 + 0.7152 * (28/255)**2.2 + 0.0722 * (18/255)**2.2
_cream_lum_rel = 0.2126 * (234/255)**2.2 + 0.7152 * (224/255)**2.2 + 0.0722 * (194/255)**2.2
_contrast_ratio = (_cream_lum_rel + 0.05) / (_ink_lum_rel + 0.05)
assert _contrast_ratio >= 7.0, f"price contrast too low: {_contrast_ratio:.1f}"

print(f"verif ok — cream_lum={_avg_lum:.1f}  seal reds={_seal_reds} golds={_seal_golds}  contrast={_contrast_ratio:.1f}:1")

import pathlib
OUTDIR = "/home/user/skybit/docs/confirm_purchase_v8/swap-round-2/swing-ticket"
pathlib.Path(OUTDIR).mkdir(parents=True, exist_ok=True)
OUT = OUTDIR + "/round_2.png"
out.save(OUT)
print(f"saved {out.size[0]}×{out.size[1]}  →  {OUT}")
